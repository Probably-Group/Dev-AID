# RAG Implementation for Dev-AID

> **Status (2026-04-08):** Historical design doc. The lightweight-RAG decision
> below was taken in December 2025. Since then Dev-AID ships its own embedded
> local semantic search module at `.dev-aid/local-search/` (FAISS +
> EmbeddingGemma + tree-sitter chunker over 8 languages). For current setup
> and usage, see `.dev-aid/RAG-SETUP.md`.

## Decision: Lightweight RAG vs Full LlamaIndex

**Status:** Approved — shipped as `.dev-aid/local-search/`
**Date:** 2025-12-03
**Decision:** Implement lightweight RAG for codebase context retrieval, WITHOUT full LlamaIndex orchestration

### Rationale

From our analysis in `LLAMAINDEX-ANALYSIS.md`:

**✅ What we DO want from LlamaIndex:**
- Semantic search across large codebases
- Smart context retrieval for memory banks
- Finding relevant code without hardcoded file paths

**❌ What we DON'T need from LlamaIndex:**
- Heavy orchestration framework (200MB)
- Complex state management
- Production-grade workflow engine
- Multi-tenant capabilities

**Solution:** Use lightweight RAG tools that integrate with our existing slash command architecture.

---

## The Problem We're Solving

### Current Limitation

```toml
# In Gemini CLI commands
prompt = """
Context: !{cat .dev-aid/memory-bank/security.md}
"""
```

**Problems:**
- Must know exact file path
- Can't search semantically ("find all auth-related code")
- Doesn't scale to large codebases (100s of files)
- No ranking by relevance

### Desired Capability

```bash
/dev-aid-router-challenger "Implement OAuth2 authentication"

# Behind the scenes:
# 1. RAG searches: "OAuth2, authentication, security"
# 2. Finds relevant context:
#    - .dev-aid/memory-bank/security.md
#    - src/auth/jwt.py (similar implementation)
#    - docs/security-guidelines.md
#    - .dev-aid/skills/expert/auth-expert/references/*
# 3. Routes to Claude with top 5 most relevant contexts
# 4. Gemini reviews with same context
```

---

## Implementation Options

### Option 1: Claude Context MCP ⭐ **RECOMMENDED**

**What it is:** MCP server specifically built for code search with Claude Code

**GitHub:** https://github.com/zilliztech/claude-context

**Why it's perfect for Dev-AID:**
- ✅ Built specifically for Claude Code integration
- ✅ MCP protocol (both Claude Code and Gemini CLI support MCP!)
- ✅ 40% token reduction under equivalent retrieval quality
- ✅ Supports multiple embedding providers (OpenAI, Voyage, Ollama, Gemini)
- ✅ Multiple vector databases (Milvus, Zilliz Cloud, ChromaDB)
- ✅ AST-based code splitting (understands code structure)
- ✅ Local-first (can run entirely on your machine)

**Setup:**
```bash
# Install MCP server
npm install -g @zilliz/claude-context

# Configure in Claude Code
# Add to .claude/mcp.json:
{
  "mcpServers": {
    "claude-context": {
      "command": "claude-context",
      "args": [
        "--embedding-provider", "openai",
        "--vector-db", "chromadb",
        "--index-path", ".dev-aid/rag-index"
      ]
    }
  }
}

# Index your codebase
claude-context index ./dev-aid

# Now available in slash commands!
```

**Integration with Router:**
```toml
# .gemini/commands/router/dev-aid-router-challenger.toml
description = "Challenger mode with semantic context retrieval"

prompt = """
User request: {{args}}

# MCP automatically provides relevant context!
# Just ask for it:
@claude-context search "{{args}}"

Now with this context:
1. Claude generates implementation
2. Gemini reviews for security issues
"""
```

**Pros:**
- Native MCP integration (no custom code)
- Works with both Claude Code and Gemini CLI
- Production-ready
- Multiple embedding provider options
- 40% token reduction = significant cost savings

**Cons:**
- Requires MCP server setup (10-15 min)
- Node.js dependency
- Embedding API costs (though Ollama is free local option)

**Cost:**
- OpenAI embeddings: ~$0.13 per 1M tokens
- Voyage AI: ~$0.10 per 1M tokens
- Ollama (local): $0 (free!)

---

### Option 2: Sturdy Dev Semantic Code Search

**What it is:** Lightweight CLI tool for local semantic code search

**GitHub:** https://github.com/sturdy-dev/semantic-code-search

**Why it's interesting:**
- ✅ Fully local (no API calls, no data leaves computer)
- ✅ Simple CLI interface
- ✅ Zero configuration
- ✅ Fast indexing

**Setup:**
```bash
# Install
cargo install semantic-code-search

# Index codebase
scs index ./dev-aid

# Search
scs search "authentication implementation"
```

**Integration with Router:**
```toml
# .gemini/commands/router/dev-aid-router-challenger.toml
prompt = """
User request: {{args}}

# Get relevant code via CLI
Relevant context:
!{scs search "{{args}}" --top-k 5}

Now implement with this context...
"""
```

**Pros:**
- 100% local, no API costs
- Privacy-preserving (no data leaves machine)
- Simple Rust binary (fast)
- Works offline

**Cons:**
- No MCP integration (need shell command wrapper)
- Limited to code search (no document search)
- Less sophisticated than Claude Context MCP

**Cost:** $0 (completely free)

---

### Option 3: ChromaDB + Custom Integration

**What it is:** Lightweight vector database with custom indexing scripts

**Why it's flexible:**
- ✅ Most lightweight option (pure Python)
- ✅ Complete control over indexing
- ✅ Can index code, docs, memory banks, git history
- ✅ Local-first
- ✅ Scales to 200k vectors easily

**Setup:**
```bash
pip install chromadb sentence-transformers
```

**Custom Indexing Script:**
```python
# .dev-aid/scripts/index_codebase.py
import chromadb
from sentence_transformers import SentenceTransformer

# Initialize
client = chromadb.PersistentClient(path=".dev-aid/rag-index")
collection = client.get_or_create_collection("dev-aid-code")

# Use code-specific embedding model
model = SentenceTransformer('jinaai/jina-embeddings-v2-base-code')

# Index everything
def index_directory(path):
    for file in glob(f"{path}/**/*.py", recursive=True):
        content = open(file).read()
        embedding = model.encode(content)
        collection.add(
            ids=[file],
            embeddings=[embedding.tolist()],
            documents=[content],
            metadatas=[{"type": "code", "path": file}]
        )

# Index different content types
index_directory("dev-aid/")
index_directory(".dev-aid/memory-bank/")
index_directory(".dev-aid/skills/expert/")
```

**Search Script:**
```python
# .dev-aid/scripts/search_context.py
import sys
import chromadb
from sentence_transformers import SentenceTransformer

query = sys.argv[1]
top_k = int(sys.argv[2]) if len(sys.argv) > 2 else 5

client = chromadb.PersistentClient(path=".dev-aid/rag-index")
collection = client.get_collection("dev-aid-code")

model = SentenceTransformer('jinaai/jina-embeddings-v2-base-code')
query_embedding = model.encode(query)

results = collection.query(
    query_embeddings=[query_embedding.tolist()],
    n_results=top_k
)

for doc, metadata in zip(results['documents'][0], results['metadatas'][0]):
    print(f"# {metadata['path']}")
    print(doc)
    print("---")
```

**Integration with Router:**
```toml
# .gemini/commands/router/dev-aid-router-challenger.toml
prompt = """
User request: {{args}}

Relevant context:
!{python3 .dev-aid/scripts/search_context.py "{{args}}" 5}

Now implement with this context...
"""
```

**Pros:**
- Maximum flexibility
- Can customize for Dev-AID's specific needs
- Lightweight (just ChromaDB + sentence-transformers)
- Index anything (code, docs, git history, issues)

**Cons:**
- Need to write custom scripts
- Manual maintenance
- No MCP integration out-of-box

**Cost:**
- Embedding model: Free (Sentence Transformers local)
- Storage: ~1-5MB per 1000 files

---

### Option 4: R2R (Retrieval to Response)

**What it is:** Lightweight RAG framework focused on simplicity

**Why it's interesting:**
- ✅ Designed to be "sleek and lightweight"
- ✅ Optimizes entire RAG pipeline
- ✅ Multi-step retrieval
- ✅ Production-ready

**Setup:**
```bash
pip install r2r

# Configure
r2r init --project dev-aid-rag

# Index
r2r index ./dev-aid

# Query
r2r search "authentication implementation"
```

**Pros:**
- Lightweight RAG-focused framework
- Good documentation
- Active development

**Cons:**
- Still requires Python runtime
- Less mature than LlamaIndex
- No native MCP integration

**Cost:**
- Framework: Free (open source)
- Embeddings: Depends on provider

---

## Comparison Matrix

| Feature | Claude Context MCP | Sturdy Dev | ChromaDB Custom | R2R |
|---------|-------------------|------------|-----------------|-----|
| **Setup Time** | 15 min | 5 min | 30-60 min | 20 min |
| **MCP Integration** | ✅ Native | ❌ Manual | ❌ Manual | ❌ Manual |
| **Cost** | $0-0.13/M tokens | $0 | $0 | $0-0.13/M |
| **Local-First** | ✅ (Ollama) | ✅ | ✅ | ✅ |
| **Code-Specific** | ✅ AST parsing | ✅ | ⚠️ DIY | ⚠️ Generic |
| **Customization** | ⚠️ Limited | ❌ Limited | ✅ Full | ⚠️ Moderate |
| **Scalability** | ✅ Excellent | ✅ Good | ⚠️ Manual | ✅ Good |
| **Maintenance** | Low | Low | Medium | Low |
| **CLI Integration** | ✅ Excellent | ✅ Good | ⚠️ DIY | ⚠️ DIY |

---

## Recommendation

### Phase 1: Start with Claude Context MCP ⭐

**Why:**
1. **Native integration** - Built specifically for Claude Code + MCP
2. **Works with both Claude Code and Gemini CLI** (both support MCP)
3. **Production-ready** - Used by companies, actively maintained
4. **40% token reduction** - Immediate cost savings
5. **Multiple embedding options** - Start with Ollama (free), upgrade to OpenAI if needed
6. **Code-aware** - AST parsing understands code structure

**Implementation Path:**

```bash
# Week 1: Basic Setup
1. Install Claude Context MCP server
2. Configure with Ollama (free local embeddings)
3. Index dev-aid/ directory
4. Test with basic queries

# Week 2: Router Integration
1. Update slash commands to use @claude-context
2. Test challenger mode with automatic context
3. Measure token reduction

# Week 3: Expand Scope
1. Index memory banks
2. Index expert skills
3. Add git history (optional)

# Week 4: Optimize
1. Switch to better embeddings if needed (Voyage, OpenAI)
2. Tune retrieval parameters
3. Add caching
```

### Phase 2: Add Sturdy Dev for Privacy-Critical Projects

For projects with strict privacy requirements:

```bash
# Use Sturdy Dev instead
scs index ./
scs search "query"

# 100% local, no network calls
```

### Phase 3: Consider Custom ChromaDB (Optional)

Only if you need:
- Custom indexing logic (e.g., git commit messages, issues)
- Specific embedding models
- Non-code document types
- Advanced filtering

---

## Integration with Existing Router

### Updated Slash Command Architecture

```
User: /dev-aid-router-challenger "Implement OAuth2"
        ↓
   [MCP: @claude-context search "OAuth2 authentication security"]
        ↓
   Returns top 5 relevant contexts:
   - .dev-aid/memory-bank/security.md
   - .dev-aid/skills/expert/auth-expert/references/oauth2.md
   - src/auth/jwt.py (similar implementation)
        ↓
   [Router: Send to Claude with context]
        ↓
   Claude generates implementation
        ↓
   [Router: Send to Gemini with same context]
        ↓
   Gemini reviews for security issues
```

### Updated File Structure

```
dev-aid/.dev-aid/
├── config/
│   ├── routing.json
│   ├── models.json
│   └── mcp.json              ← NEW: MCP server config
├── providers/
│   ├── claude/.claude/commands/router/
│   └── gemini/.gemini/commands/router/
├── rag-index/                ← NEW: Vector database
│   └── chromadb/
├── scripts/                  ← NEW: Helper scripts
│   ├── index_codebase.py
│   └── search_context.py
└── logs/
    ├── routing.log
    ├── costs.json
    └── rag-queries.log        ← NEW: RAG query logs
```

---

## Expected Benefits

### 1. Better Context for Code Generation

**Before:**
```bash
/dev-aid-router-challenger "Implement password reset"
# Claude has no context, generates generic implementation
```

**After:**
```bash
/dev-aid-router-challenger "Implement password reset"
# RAG finds:
# - Existing auth patterns from src/auth/
# - Security guidelines from memory bank
# - Similar implementation in password-change.py
# Claude generates implementation matching your codebase style
```

### 2. Massive Context Analysis

**Before:**
```bash
# Gemini: "Analyze entire codebase for auth issues"
# Can't actually provide entire codebase (millions of tokens)
```

**After:**
```bash
# Gemini: "Analyze entire codebase for auth issues"
# RAG finds all auth-related files
# Provides summarized context (5-10k tokens)
# Gemini analyzes with full relevant context
```

### 3. Cost Savings

**Token Reduction Examples:**

| Task | Without RAG | With RAG | Savings |
|------|-------------|----------|---------|
| "Implement OAuth2" | 150k tokens (entire codebase) | 50k tokens (relevant context) | 67% ↓ |
| "Review auth code" | 200k tokens | 60k tokens | 70% ↓ |
| "Find security issues" | 300k tokens | 90k tokens | 70% ↓ |

**At scale:**
- 100 requests/month without RAG: ~$45 (15M tokens × $3/M)
- 100 requests/month with RAG: ~$13.50 (4.5M tokens × $3/M)
- **Savings: $31.50/month = 70% cost reduction**

### 4. Smarter Routing

```python
# Enhanced ensemble routing with RAG
def route_with_rag(request: str):
    # 1. Get semantic context
    context = rag.search(request, top_k=5)

    # 2. Analyze context size
    if sum(len(c) for c in context) > 100_000:
        # Large context → Gemini (2M context window)
        return "gemini-flash"

    # 3. Analyze context type
    if any("security" in c.metadata.tags for c in context):
        return "claude-sonnet"  # Security expert

    return "claude-sonnet"  # Default
```

---

## Migration Path from Current Implementation

### Step 1: No Changes to Existing Commands

Keep current slash commands working:

```toml
# .gemini/commands/router/dev-aid-router-challenger.toml
# Keep this working exactly as before
```

### Step 2: Add RAG-Enhanced Versions

Create new commands with RAG:

```toml
# .gemini/commands/router/dev-aid-router-challenger-rag.toml
description = "Challenger mode with semantic context retrieval"

prompt = """
User request: {{args}}

# Use MCP to get context
@claude-context search "{{args}}"

# Rest is same as original command
...
"""
```

### Step 3: Test and Compare

Run both versions side-by-side:

```bash
# Original (no RAG)
/dev-aid-router-challenger "Implement OAuth2"

# RAG-enhanced
/dev-aid-router-challenger-rag "Implement OAuth2"

# Compare quality, cost, speed
```

### Step 4: Gradual Migration

Once validated:
1. Update existing commands to use RAG
2. Deprecate `-rag` suffix
3. RAG becomes standard

---

## Metrics to Track

### Performance Metrics

```json
{
  "rag_metrics": {
    "query_latency_ms": 150,
    "retrieval_accuracy": 0.89,
    "context_relevance_score": 0.92,
    "token_reduction_pct": 68
  }
}
```

### Cost Metrics

```json
{
  "cost_comparison": {
    "without_rag": {
      "avg_input_tokens": 145000,
      "cost_per_request": 0.435
    },
    "with_rag": {
      "avg_input_tokens": 48000,
      "cost_per_request": 0.144,
      "embedding_cost": 0.006
    },
    "total_savings_pct": 66
  }
}
```

### Quality Metrics

```json
{
  "quality_metrics": {
    "code_quality_score": 4.2,
    "security_issues_found": 8,
    "false_positives": 2,
    "developer_satisfaction": 4.5
  }
}
```

---

## Next Steps

### Immediate (This Week)

1. **Set up Claude Context MCP** (15 min)
   ```bash
   npm install -g @zilliz/claude-context
   # Configure with Ollama (free)
   ```

2. **Index Dev-AID codebase** (5 min)
   ```bash
   claude-context index ./dev-aid
   ```

3. **Create test command** (10 min)
   ```bash
   # .gemini/commands/router/dev-aid-router-test-rag.toml
   ```

4. **Validate retrieval quality** (30 min)
   ```bash
   # Test queries, measure relevance
   ```

### Short Term (Next 2 Weeks)

1. **Integrate with existing router commands**
2. **Measure token reduction and cost savings**
3. **Expand index to include memory banks and skills**
4. **Update documentation**

### Long Term (Next Month)

1. **Optimize embedding model selection**
2. **Add caching for frequently accessed contexts**
3. **Implement hybrid search (keyword + semantic)**
4. **Add feedback loop for relevance tuning**

---

## Risks and Mitigations

### Risk 1: MCP Setup Complexity

**Risk:** Team members struggle with MCP setup

**Mitigation:**
- Provide detailed setup guide
- Create setup script: `./dev-aid/scripts/setup-rag.sh`
- Fallback: Use Sturdy Dev (simpler CLI)

### Risk 2: Embedding API Costs

**Risk:** Embedding costs become significant

**Mitigation:**
- Start with Ollama (free local embeddings)
- Only upgrade to paid if quality issues
- Set up cost monitoring

### Risk 3: Index Maintenance

**Risk:** Index becomes stale as codebase changes

**Mitigation:**
- Set up git hook to re-index on commit
- Weekly automated re-indexing
- Incremental indexing (only changed files)

### Risk 4: Retrieval Quality

**Risk:** RAG returns irrelevant context

**Mitigation:**
- Manual validation of top 20 queries
- Tune top_k parameter
- Add metadata filtering
- Collect feedback from developers

---

## References

**Claude Context MCP:**
- [GitHub Repository](https://github.com/zilliztech/claude-context)
- [Code Search MCP Documentation](https://github.com/zilliztech/claude-context)

**Lightweight RAG Frameworks:**
- [15 Best Open-Source RAG Frameworks 2025](https://www.firecrawl.dev/blog/best-open-source-rag-frameworks)
- [R2R Framework](https://www.designveloper.com/blog/best-open-source-rag-framework/)
- [RAGatouille](https://www.signitysolutions.com/blog/best-open-source-rag-frameworks)

**Vector Databases:**
- [ChromaDB vs FAISS Comparison](https://aloa.co/ai/comparisons/vector-database-comparison/faiss-vs-chroma)
- [Vector Database Guide](https://mohamedbakrey094.medium.com/chromadb-vs-faiss-a-comprehensive-guide-for-vector-search-and-ai-applications-39762ed1326f)
- [FAISS & ChromaDB in VS Code](https://medium.com/@gitaramkanawade/exploring-faiss-chroma-embeddings-inside-vs-code-af23ac68c488)

**Semantic Code Search:**
- [Sturdy Dev Semantic Code Search](https://github.com/sturdy-dev/semantic-code-search)
- [Vector Embeddings for Codebases](https://dzone.com/articles/vector-embeddings-codebase-guide)
- [ZeroEntropy Semantic Code Search](https://www.zeroentropy.dev/articles/semantic-code-search)
- [Jina Code Embeddings](https://jina.ai/news/elevate-your-code-search-with-new-jina-code-embeddings/)
- [Qdrant Code Search](https://qdrant.tech/documentation/advanced-tutorials/code-search/)

---

**Last Updated:** 2025-12-03
**Status:** Ready for implementation
**Recommended Approach:** Claude Context MCP with Ollama embeddings
