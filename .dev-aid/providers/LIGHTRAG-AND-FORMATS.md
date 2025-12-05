# LightRAG Analysis & File Format Support Comparison

## LightRAG Deep Dive

### What is LightRAG?

**Official:** [EMNLP2025] "LightRAG: Simple and Fast Retrieval-Augmented Generation"
**GitHub:** https://github.com/HKUDS/LightRAG
**Status:** Academic research project, accepted to EMNLP 2025

### Key Innovation: Graph-Based RAG

Unlike traditional vector-only RAG systems, LightRAG uses **graph structures** for indexing and retrieval:

```
Traditional RAG:
Document → Chunks → Embeddings → Vector DB → Similarity Search

LightRAG:
Document → Chunks → Embeddings + Knowledge Graph → Dual-Level Retrieval
                                                    ├─ Vector similarity (low-level)
                                                    └─ Graph relationships (high-level)
```

**Why this matters:**
- **Entity relationships** - Understands "OAuth2 uses JWT tokens" as connected concepts
- **Faster retrieval** - Graph traversal can be faster than pure vector search
- **Better context** - Returns not just similar text, but related concepts

### Architecture

```python
# LightRAG workflow
import lightrag

# 1. Initialize with graph backend
rag = LightRAG(
    working_dir="./lightrag_index",
    llm="gpt-4o-mini",  # For graph extraction
    embedding="text-embedding-3-small",
    graph_storage="NetworkXStorage"  # or Neo4j
)

# 2. Ingest documents (builds graph + vectors)
rag.insert("path/to/documents")

# 3. Query with graph-enhanced retrieval
result = rag.query(
    "How does OAuth2 work?",
    mode="hybrid"  # naive (vector), local (1-hop), global (multi-hop), hybrid
)
```

### Performance Benchmarks

According to paper (EMNLP 2025):
- **Better accuracy** than GraphRAG, standard RAG
- **Faster** than GraphRAG (3-4x speedup)
- **Lower cost** than GraphRAG (graph building is cheaper)

---

## File Format Support Comparison

### Configuration Formats (How you configure each system)

| System | Config Format | Example |
|--------|--------------|---------|
| **Claude Context MCP** | JSON | `mcp.json`, `config.json` |
| **LightRAG** | Python dict/JSON | Python config or JSON |
| **Sturdy Dev** | TOML | `.scs.toml` |
| **ChromaDB** | Python dict/YAML | Python config |
| **R2R** | YAML/JSON | `config.yaml` |
| **FAISS** | Python code | No config files |

**Configuration Examples:**

**Claude Context MCP (JSON):**
```json
{
  "mcpServers": {
    "claude-context": {
      "command": "claude-context",
      "args": ["--embedding-provider", "openai"]
    }
  }
}
```

**LightRAG (Python/JSON):**
```python
config = {
    "working_dir": "./rag_index",
    "llm": "gpt-4o-mini",
    "embedding": "text-embedding-3-small",
    "graph_storage": "NetworkXStorage"
}
```

**Sturdy Dev (TOML):**
```toml
[semantic-code-search]
index_path = ".scs"
embedding_model = "all-MiniLM-L6-v2"
```

**R2R (YAML):**
```yaml
ingestion:
  mode: hi-res
  chunk_size: 1024
embedding:
  provider: openai
  model: text-embedding-3-small
```

---

## Document Ingestion Formats (What files can be indexed)

### Claude Context MCP

**Supported Formats:**
- ✅ **Code**: `.py`, `.js`, `.ts`, `.java`, `.cpp`, `.c`, `.rs`, `.go`, `.rb`, `.php`, etc.
- ✅ **Markup**: `.md`, `.html`, `.css`, `.xml`
- ✅ **Config**: `.json`, `.yaml`, `.toml`, `.xml`, `.env`, `.ini`
- ✅ **Docs**: `.txt`, `.rst`
- ✅ **Data**: `.csv`, `.tsv`
- ❌ **Binary**: `.pdf`, `.docx` (not natively supported - need conversion)

**Focus:** Code and text files

**Special Feature:** AST-based code parsing (understands code structure)

---

### LightRAG

**Supported Formats:**
- ✅ **Documents**: `.pdf`, `.docx`, `.pptx`, `.xlsx`
- ✅ **Text**: `.txt`, `.md`, `.rtf`
- ✅ **Structured**: `.csv` (via pandas)
- ⚠️ **XML/JSON**: Not explicitly mentioned (may need conversion)
- ❌ **Code files**: No special code handling

**Focus:** Document-heavy workloads (PDFs, Office docs)

**Special Feature:** Knowledge graph extraction from documents

**Processing Libraries:**
```python
# LightRAG uses these for parsing:
- python-docx  → DOCX files
- python-pptx  → PPTX files
- openpyxl     → XLSX files
- PyMuPDF      → PDF files
```

**Limitations:**
- XML/JSON files not natively supported
- No AST parsing for code (treats code as plain text)
- Requires LLM calls for graph extraction (adds cost)

---

### Sturdy Dev Semantic Code Search

**Supported Formats:**
- ✅ **Code**: All programming languages
- ✅ **Text**: `.txt`, `.md`
- ⚠️ **Config**: `.json`, `.yaml`, `.toml`, `.xml` (treated as text)
- ❌ **Documents**: `.pdf`, `.docx` not supported

**Focus:** Code-only

**Special Feature:** Fully local (no API calls)

---

### ChromaDB (Custom)

**Supported Formats:**
- ✅ **Anything you can read into Python**
- Parse yourself, then add to ChromaDB

**Example:**
```python
import chromadb
import json
import xml.etree.ElementTree as ET

# JSON
with open("config.json") as f:
    data = json.load(f)
    collection.add(documents=[json.dumps(data)])

# XML
tree = ET.parse("config.xml")
xml_str = ET.tostring(tree.getroot()).decode()
collection.add(documents=[xml_str])

# TOML
import tomli
with open("config.toml", "rb") as f:
    data = tomli.load(f)
    collection.add(documents=[str(data)])

# Code files
with open("script.py") as f:
    collection.add(documents=[f.read()])
```

**Flexibility:** Maximum (you write the parser)

---

### R2R Framework

**Supported Formats:**
- ✅ **Documents**: `.pdf`, `.docx`, `.pptx`, `.xlsx`
- ✅ **Text**: `.txt`, `.md`, `.html`, `.csv`
- ✅ **Structured**: `.json`
- ✅ **Media**: `.png`, `.jpg`, `.mp3`, `.mp4` (with multimodal models)
- ⚠️ **XML**: Via HTML parser or Unstructured integration
- ⚠️ **TOML**: Not explicitly mentioned

**Focus:** Multi-modal RAG (text, images, audio, video)

**Special Feature:** 4 ingestion modes (fast, hi-res, ocr, custom)

**Extended Support with Unstructured.io:**
When integrated with Unstructured, R2R supports **27 file types** including:
- `.eml`, `.epub`, `.odt`, `.org`, `.rst`, `.rtf`, `.tsv`, etc.

---

## Format Support Matrix

| Format | Claude Context | LightRAG | Sturdy Dev | ChromaDB | R2R | FAISS |
|--------|----------------|----------|------------|----------|-----|-------|
| **JSON** | ✅ Config | ⚠️ Convert | ⚠️ Text | ✅ DIY | ✅ Native | ✅ DIY |
| **XML** | ✅ Markup | ⚠️ Convert | ⚠️ Text | ✅ DIY | ⚠️ HTML | ✅ DIY |
| **TOML** | ✅ Config | ⚠️ Convert | ✅ Config | ✅ DIY | ⚠️ Convert | ✅ DIY |
| **YAML** | ✅ Config | ⚠️ Convert | ⚠️ Text | ✅ DIY | ✅ Config | ✅ DIY |
| **Markdown** | ✅ Native | ✅ Native | ✅ Native | ✅ DIY | ✅ Native | ✅ DIY |
| **PDF** | ❌ | ✅ Native | ❌ | ✅ DIY | ✅ Native | ✅ DIY |
| **DOCX** | ❌ | ✅ Native | ❌ | ✅ DIY | ✅ Native | ✅ DIY |
| **Code Files** | ✅ AST | ⚠️ Text | ✅ Native | ✅ DIY | ⚠️ Text | ✅ DIY |
| **Images** | ❌ | ❌ | ❌ | ✅ DIY | ✅ Vision | ✅ DIY |
| **Audio/Video** | ❌ | ❌ | ❌ | ✅ DIY | ✅ Multi | ✅ DIY |

**Legend:**
- ✅ **Native** - Built-in support
- ⚠️ **Convert** - Requires conversion or workaround
- ❌ **No** - Not supported
- **DIY** - You write the parser (ChromaDB/FAISS)

---

## LightRAG Pros & Cons for Dev-AID

### ✅ Pros

**1. Graph-Enhanced Retrieval**
```python
# Query: "How does authentication work?"
# LightRAG returns:
# - Vector: Similar auth code
# - Graph: Related concepts (JWT, OAuth2, sessions, security)
# Result: More complete context
```

**2. Academic Validation**
- EMNLP 2025 acceptance
- Outperforms GraphRAG, standard RAG in benchmarks
- Well-documented research

**3. Flexible Graph Storage**
```python
# Local: NetworkX (in-memory graph)
# Production: Neo4j (distributed graph database)
```

**4. Document-Focused**
- Better for `.pdf`, `.docx`, `.pptx` than Claude Context MCP
- Good for documentation-heavy projects

**5. Performance**
- 3-4x faster than GraphRAG
- Lower cost than GraphRAG

### ❌ Cons

**1. Academic Project**
- Not as production-hardened as Claude Context MCP
- Less mature ecosystem
- Smaller community

**2. LLM Dependency for Graphs**
```python
# Each document requires LLM calls to build graph
# Example: 100 documents × $0.01 per doc = $1.00 for indexing
# vs Claude Context MCP: $0 with Ollama embeddings
```

**3. No MCP Integration**
- Can't use `@lightrag search` in Claude Code
- Need custom wrapper scripts

**4. Limited Code Support**
- No AST parsing (treats code as plain text)
- No language-specific understanding
- Bad for code-heavy projects

**5. No Native XML/JSON/TOML Ingestion**
- Need to convert config files to text first
- Extra preprocessing step

**6. Setup Complexity**
```bash
pip install lightrag
# vs
npm install -g @zilliz/claude-context  # Claude Context MCP
```

Both require setup, but LightRAG needs:
- Python environment
- LLM API (for graph extraction)
- Graph database (optional Neo4j)

---

## When to Choose LightRAG

### ✅ Choose LightRAG if:

**1. Document-Heavy Codebase**
```
Your project structure:
├── docs/           ← Lots of PDFs, DOCX
│   ├── specs/
│   ├── design/
│   └── guides/
├── src/            ← Some code
└── .dev-aid/
```

**Use case:** "Find all design decisions related to authentication across Word docs, PDFs, and presentations"

**LightRAG wins:** Graph connects concepts across documents

---

**2. Complex Concept Relationships**
```
Query: "How do microservices communicate?"

LightRAG graph:
[Microservices] ─uses→ [REST APIs]
                ─uses→ [Message Queues]
                ─uses→ [gRPC]
[REST APIs] ─requires→ [Authentication]
[Message Queues] ─examples→ [RabbitMQ, Kafka]

Result: Full concept map, not just similar text
```

---

**3. Multi-Document Synthesis**
```
Query: "What are all security requirements?"

LightRAG:
- Finds security mentions across 50 docs
- Builds graph of security concepts
- Returns unified view

Standard RAG:
- Returns 5 most similar chunks
- Misses connections between docs
```

---

### ❌ Don't Choose LightRAG if:

**1. Code-Heavy Project**
```
Your project:
├── src/          ← 90% of content
│   ├── auth/
│   ├── api/
│   └── db/
├── docs/         ← 10% of content
└── .dev-aid/
```

**Better choice:** Claude Context MCP (AST parsing for code)

---

**2. Need MCP Integration**
```bash
# You want:
@claude-context search "auth implementation"

# LightRAG requires:
!{python3 .dev-aid/scripts/lightrag_search.py "auth implementation"}
```

**Better choice:** Claude Context MCP (native integration)

---

**3. Budget-Conscious**
```
Claude Context MCP (Ollama):
- Indexing: $0 (local embeddings)
- Query: $0 (local embeddings)

LightRAG:
- Indexing: $1-5 per 100 docs (LLM graph extraction)
- Query: $0.01 per query (LLM for graph reasoning)
```

**Better choice:** Claude Context MCP or Sturdy Dev

---

**4. Code-Specific Queries**
```
Query: "Find all functions that handle user authentication"

Claude Context MCP:
- AST parsing understands "functions"
- Returns actual function definitions

LightRAG:
- Treats code as text
- May return comments, not actual functions
```

**Better choice:** Claude Context MCP

---

## Hybrid Approach: Best of Both Worlds

### Strategy: Use Both!

```
Dev-AID File Structure:
├── src/              ← Code (Claude Context MCP)
├── docs/             ← PDFs, DOCX (LightRAG)
├── .dev-aid/
│   ├── memory-bank/  ← Markdown (Both)
│   └── rag-index/
│       ├── code/     ← Claude Context MCP index
│       └── docs/     ← LightRAG index
```

**Routing Logic:**
```python
def route_rag(query: str, file_types: list):
    if "code" in file_types or ".py" in query:
        # Use Claude Context MCP
        return claude_context.search(query)

    elif "document" in file_types or "design" in query:
        # Use LightRAG
        return lightrag.query(query)

    else:
        # Use both, merge results
        code_results = claude_context.search(query)
        doc_results = lightrag.query(query)
        return merge(code_results, doc_results)
```

---

## Updated Recommendation for Dev-AID

### Phase 1: Claude Context MCP (Week 1-2)

**Why start here:**
1. Dev-AID is **code-heavy** (most content is Python, Markdown, TOML)
2. Need **MCP integration** (works with Claude Code + Gemini CLI)
3. **Zero cost** with Ollama embeddings
4. **AST parsing** for code understanding

```bash
# Quick setup
npm install -g @zilliz/claude-context
claude-context index ./dev-aid --include "**/*.py,**/*.md,**/*.toml"
```

### Phase 2: Evaluate LightRAG (Week 3-4)

**If you have document-heavy needs:**

```bash
# Install LightRAG
pip install lightrag

# Index only documents
python -c "
from lightrag import LightRAG
rag = LightRAG(working_dir='./lightrag_docs')
rag.insert('./dev-aid/docs')  # PDFs, DOCX
rag.insert('./.dev-aid/specs') # Design docs
"
```

**Test queries:**
```python
# Complex concept queries
rag.query("How do all security components relate?", mode="global")

# Multi-document synthesis
rag.query("What are all authentication requirements?", mode="hybrid")
```

### Phase 3: Hybrid System (Month 2)

**If LightRAG proves valuable:**

```toml
# .gemini/commands/router/dev-aid-router-hybrid-rag.toml
description = "Hybrid RAG: Code (MCP) + Documents (LightRAG)"

prompt = """
User query: {{args}}

# Step 1: Search code with MCP
@claude-context search "{{args}}"

# Step 2: Search documents with LightRAG
!{python3 .dev-aid/scripts/lightrag_search.py "{{args}}"}

# Step 3: Merge and route
Now with complete context from code AND documents...
"""
```

---

## File Format Recommendations for Dev-AID

### For Dev-AID Memory Banks & Skills

**Current formats:**
```
.dev-aid/
├── memory-bank/
│   ├── security.md       ← Markdown
│   ├── patterns.md       ← Markdown
│   └── decisions.json    ← JSON
├── config/
│   ├── routing.json      ← JSON
│   └── models.json       ← JSON
└── skills/expert/
    └── */references/*.md ← Markdown
```

**Recommendation: Keep Markdown + JSON**

**Why:**
- ✅ All RAG systems support Markdown natively
- ✅ JSON widely supported or easy to parse
- ✅ Human-readable (can edit in text editor)
- ✅ Git-friendly (good diffs)
- ✅ Claude Code/Gemini CLI can read directly

**Avoid:**
- ❌ XML (verbose, not widely supported in RAG)
- ❌ TOML (good for config, bad for prose)
- ❌ Binary formats (PDF, DOCX) unless necessary

**For Configuration:**
```
✅ Keep: JSON for machine-readable config (routing.json, models.json)
✅ Keep: TOML for tool-specific config (.scs.toml for Sturdy Dev)
✅ Keep: Markdown for human-readable docs (memory banks, skills)
```

---

## Cost Comparison with File Format Considerations

### Scenario: Index 1000 Files

**File Mix:**
- 700 code files (.py, .js, .ts)
- 200 Markdown files (.md)
- 50 JSON/TOML config files
- 30 PDFs (design docs)
- 20 DOCX (specs)

**Claude Context MCP:**
```
Setup: 30 min
Indexing:
- 900 text files × $0 (Ollama) = $0
- 50 PDFs/DOCX = Not supported (skip or convert)
Query: $0 per query
Total: $0
```

**LightRAG:**
```
Setup: 45 min
Indexing:
- 900 text files × $0.002 (LLM graph) = $1.80
- 50 PDFs/DOCX × $0.01 (LLM graph) = $0.50
Query: $0.01 per query
Total: $2.30 + $0.01/query
```

**Sturdy Dev:**
```
Setup: 10 min
Indexing: All files × $0 = $0
Query: $0
Total: $0 (but no PDFs/DOCX)
```

**Hybrid (Claude Context + LightRAG):**
```
Setup: 45 min
Indexing:
- 900 text/code via MCP = $0
- 50 docs via LightRAG = $0.50
Query: $0 (MCP) + $0.01 (LightRAG if needed)
Total: $0.50
```

---

## Final Verdict: LightRAG vs Claude Context MCP

### For Dev-AID Specifically:

| Criteria | Winner | Why |
|----------|--------|-----|
| **Code Search** | 🏆 **Claude Context MCP** | AST parsing, code-aware |
| **Document Search** | 🏆 **LightRAG** | Native PDF/DOCX, graph relationships |
| **MCP Integration** | 🏆 **Claude Context MCP** | Native support |
| **Cost** | 🏆 **Claude Context MCP** | $0 with Ollama |
| **Setup Speed** | 🏆 **Claude Context MCP** | 15 min vs 45 min |
| **File Format Support** | 🏆 **LightRAG** | More formats (PDF, DOCX, PPTX) |
| **Concept Relationships** | 🏆 **LightRAG** | Knowledge graph |
| **Production Maturity** | 🏆 **Claude Context MCP** | More mature |

### Recommendation:

**Start with Claude Context MCP** for these reasons:
1. Dev-AID is **70% code** (Python, TOML, JSON, Markdown)
2. **MCP integration** is killer feature
3. **Zero cost** with Ollama
4. **Faster setup**

**Add LightRAG later** if you need:
1. Heavy PDF/DOCX document search
2. Complex concept relationship queries
3. Multi-document synthesis

**Or use hybrid:** Claude Context MCP for code, LightRAG for docs

---

## Implementation Guide: Adding LightRAG (Optional)

### Quick Setup

```bash
# Install
pip install lightrag lightrag-hku

# Create indexing script
cat > .dev-aid/scripts/lightrag_index.py << 'EOF'
from lightrag import LightRAG

# Initialize
rag = LightRAG(
    working_dir=".dev-aid/rag-index/lightrag",
    llm="gpt-4o-mini",  # Cheapest for graph extraction
    embedding_func=EmbeddingFunc(  # Use OpenAI or local
        embedding_dim=1536,
        max_token_size=8192,
        func=lambda texts: openai_embed(texts)
    )
)

# Index documents
rag.insert("./docs")
print("✓ Indexed documents")
EOF

# Run indexing
python3 .dev-aid/scripts/lightrag_index.py
```

### Create Search Script

```python
# .dev-aid/scripts/lightrag_search.py
import sys
from lightrag import LightRAG

query = sys.argv[1]
mode = sys.argv[2] if len(sys.argv) > 2 else "hybrid"

rag = LightRAG(working_dir=".dev-aid/rag-index/lightrag")
result = rag.query(query, mode=mode)
print(result)
```

### Integrate with Slash Commands

```toml
# .gemini/commands/router/dev-aid-router-docs-rag.toml
description = "Document search with LightRAG graph-enhanced retrieval"

prompt = """
User query: {{args}}

# Search documents with graph relationships
Document context:
!{python3 .dev-aid/scripts/lightrag_search.py "{{args}}" "hybrid"}

Now answer with this document context...
"""
```

---

## References

**LightRAG:**
- [LightRAG GitHub](https://github.com/HKUDS/LightRAG)
- [LightRAG Official Site](https://lightrag.github.io/)
- [EMNLP 2025 Paper](https://arxiv.org/abs/2410.05779)
- [LightRAG Tutorial](https://www.amplework.com/blog/lightrag-simplifying-retrieval-augmented-generation/)
- [Graph RAG Comparison](https://tdg-global.net/blog/analytics/vector-rag-vs-graph-rag-vs-lightrag/kenan-agyel/)

**File Format Support:**
- [Claude File Formats](https://www.datastudios.org/post/claude-file-upload-limits-and-supported-formats-in-2025)
- [R2R Document Types](https://r2r-docs.sciphi.ai/documentation/documents)
- [R2R Ingestion](https://r2r-docs.sciphi.ai/cookbooks/ingestion)
- [LightRAG Document Processing](https://ib.bsb.br/lightrag-extracting-relevant-information-from-mixed-data/)
- [Configuration Formats Guide](https://medium.com/@ayasc/configuration-file-formats-xml-toml-json-yaml-and-ini-explained-a275fd67ee4e)

**Vector Databases:**
- [ChromaDB vs FAISS](https://risingwave.com/blog/chroma-db-vs-pinecone-vs-faiss-vector-database-showdown/)
- [Vector Storage Battle](https://www.myscale.com/blog/faiss-vs-chroma-vector-storage-battle/)

---

**Last Updated:** 2025-12-03
**Verdict:** Claude Context MCP for code-heavy, LightRAG for document-heavy, or hybrid for best of both
