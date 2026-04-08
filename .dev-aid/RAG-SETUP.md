# Local Semantic Search Setup

**Status:** Embedded in Dev-AID (`.dev-aid/local-search/`)
**Inspired by:** claude-context-local by FarhanAliRaza (reimplemented as a self-contained Dev-AID module)
**Cost:** $0 forever
**Privacy:** 100% local

---

## Quick Start

### Option 1: During Repository Initialization

```bash
# Clone/setup Dev-AID
cd dev-aid

# Run init script (will prompt for RAG setup)
./.dev-aid/scripts/setup-dev-aid.sh
```

### Option 2: Add to Existing Dev-AID

```bash
# If Dev-AID already set up
cd dev-aid

# Run RAG setup
./.dev-aid/scripts/setup-rag.sh
```

**Time: 5 minutes**

---

## What Gets Installed

### claude-context-local

**GitHub:** https://github.com/FarhanAliRaza/claude-context-local

**Components:**
- ✅ EmbeddingGemma model (Google, 768-dim, ~1.2GB)
- ✅ FAISS vector index (GPU-accelerated if available)
- ✅ MCP server integration
- ✅ tree-sitter parsers (8 languages: python, javascript, typescript, java, go, rust, c, cpp)

**Storage:**
```
~/.local/share/claude-context-local/  # Installation
~/.claude_code_search/                # Index and models
  ├── models/
  │   └── embedding-gemma-300m/      # 1.2GB
  ├── index/
  │   ├── code.index                  # FAISS vectors
  │   ├── metadata.db                 # SQLite
  │   └── stats.json                  # Index stats
```

**Local Dev-AID scripts:**
```
.dev-aid/scripts/
├── setup-rag.sh           # Initial setup
├── reindex-codebase.sh    # Reindex after changes
└── rag-status.sh          # Check status
```

---

## How It Works

### Architecture

```
Your Query
    ↓
MCP code-search tool
    ↓
EmbeddingGemma (local, 768-dim vectors)
    ↓
FAISS similarity search (local index)
    ↓
Top 5-10 relevant code chunks
    ↓
Injected into Claude/Gemini context
    ↓
AI responds with perfect context
```

**No cloud APIs • No costs • Works offline**

### What Gets Indexed

**Parsed with AST/tree-sitter (8 languages):**
- Python (.py) - Functions, classes, methods
- JavaScript (.js, .jsx)
- TypeScript (.ts, .tsx)
- Java (.java)
- Go (.go)
- Rust (.rs)
- C (.c, .h)
- C++ (.cpp, .cc, .cxx, .hpp)

**Indexed as text:**
- Markdown (.md)
- JSON (.json)
- TOML (.toml)
- YAML (.yaml)
- Text (.txt)

**Automatically excluded:**
- node_modules/, .venv/, __pycache__/
- build/, dist/, .git/
- Binary files

---

## Usage

### In Claude Code (Automatic)

```
You: "Find all authentication functions in this codebase"

Claude: *automatically uses @code-search MCP tool*
*Returns relevant functions with context*
```

### In Gemini CLI (via MCP)

```bash
# After MCP configured
gemini> "Search for OAuth2 implementation"
# Uses code-search tool via MCP
```

### With Router Commands

**RAG-enhanced challenger mode:**
```
/dev-aid-router-challenger-rag "Implement password reset"
```

**What happens:**
1. Semantic search finds: existing auth code, security guidelines, similar implementations
2. Claude generates using your codebase patterns
3. Gemini reviews with same context
4. You get implementation that matches your codebase style

---

## Maintenance

### Check Status

```bash
./.dev-aid/scripts/rag-status.sh
```

**Output:**
```
╔════════════════════════════════════════════╗
║   claude-context-local Status              ║
╚════════════════════════════════════════════╝

✓ Installed: v1.0.0
✓ Index directory: ~/.claude_code_search/index
✓ Indexed files: 342
✓ Chunks: 1,247
Index size: 6 MB
✓ EmbeddingGemma downloaded (1.2 GB)

MCP Integration:
✓ Claude Code: Registered
- Gemini CLI: Not installed

Recent Queries:
[2025-12-03 10:23] "authentication functions" - 8 results
[2025-12-03 10:25] "password validation" - 5 results
```

### Reindex After Changes

**Manual:**
```bash
./.dev-aid/scripts/reindex-codebase.sh
```

**Automatic (via git hook):**
```bash
# Already set up during install if you chose it
# Reindexes automatically after commits with 5+ file changes
```

**When to reindex:**
- Added new features (new files)
- Significant refactoring (changed many files)
- Updated security guidelines in memory bank
- Weekly (optional, for freshness)

---

## Performance

### Indexing Speed

**Dev-AID (342 files) on M1 MacBook:**
```
Parse files:      12 seconds
Generate vectors: 45 seconds
Build FAISS:       3 seconds
Total:            60 seconds
```

**On NVIDIA GPU:** ~30 seconds
**On CPU only:** ~90 seconds

### Query Speed

```
Query: "Find authentication functions"
Search: 0.15 seconds (local FAISS)
Total: 0.15 seconds

(vs cloud APIs: 0.3-0.5 seconds + network latency)
```

### Storage

```
Model (one-time):     1.2 GB
Index (per project):  ~6 MB (for 342 files)
Metadata:            ~1 MB
```

---

## Cost Analysis

### Setup

```
Installation:       $0 (free)
Model download:     $0 (1.2GB, one-time)
Time:              5 minutes
```

### Usage (1000 queries/month)

```
Embedding generation: $0 (local)
Vector search:        $0 (local)
Storage:             $0 (local disk)

vs Cloud RAG:
- OpenAI embeddings:  $1.30/month
- Vector DB:          $0-20/month

Savings: $15-250/year
```

---

## Supported Languages

| Language | Support | Parser | Features |
|----------|---------|--------|----------|
| Python | ✅ Full | tree-sitter | Functions, classes, methods |
| JavaScript | ✅ Full | tree-sitter | Functions, classes, exports |
| TypeScript | ✅ Full | tree-sitter | Types, interfaces, functions |
| Java | ✅ Full | tree-sitter | Classes, methods, interfaces |
| Go | ✅ Full | tree-sitter | Functions, structs, interfaces |
| Rust | ✅ Full | tree-sitter | Functions, structs, traits |
| C | ✅ Full | tree-sitter | Functions, structs |
| C++ | ✅ Full | tree-sitter | Functions, classes, structs |
| Markdown | ⚠️ Text | None | Line-based fallback |
| JSON/TOML | ⚠️ Text | None | Line-based fallback |

---

## Troubleshooting

### "MCP tool 'code-search' not found"

**Problem:** MCP server not registered

**Solution:**
```bash
# Re-run setup
./.dev-aid/scripts/setup-rag.sh

# Or manually register
claude mcp add code-search --scope user -- \
  uv run --directory ~/.local/share/claude-context-local \
  python mcp_server/server.py

# Verify
claude mcp list
```

### "No results found" or Poor Quality Results

**Problem:** Index is stale or empty

**Solution:**
```bash
# Check what's indexed
./.dev-aid/scripts/rag-status.sh

# Reindex
./.dev-aid/scripts/reindex-codebase.sh

# Verify index size
du -sh ~/.claude_code_search/index/
```

### Slow Performance

**Problem:** Running on CPU instead of GPU

**Check GPU status:**
```bash
./.dev-aid/scripts/rag-status.sh
# Look for "GPU acceleration" line
```

**For NVIDIA:**
```bash
# Check CUDA
nvidia-smi

# If CUDA available but not detected, reinstall
pip install faiss-gpu
```

**For Apple Silicon:**
```bash
# MPS should be auto-detected
# If not working, check Python version >= 3.12
```

### Model Download Failed

**Problem:** EmbeddingGemma download interrupted

**Solution:**
```bash
# Clear partial download
rm -rf ~/.claude_code_search/models/

# Re-run setup
./.dev-aid/scripts/setup-rag.sh
```

### Permission Errors

**Problem:** Can't write to install directory

**Solution:**
```bash
# Check ownership
ls -la ~/.local/share/claude-context-local/

# Fix permissions
chmod -R u+w ~/.local/share/claude-context-local/
```

---

## Advanced Configuration

### Custom MCP Configuration

**Location:** `~/.claude/mcp.json` or `~/.gemini/mcp.json`

**Template provided:** `.dev-aid/config/mcp-template.json`

**Customize:**
```json
{
  "mcpServers": {
    "code-search": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "~/.local/share/claude-context-local",
        "python",
        "mcp_server/server.py"
      ],
      "env": {
        "TOP_K": "10",           // Return top 10 results (default: 5)
        "MIN_SIMILARITY": "0.7"   // Minimum similarity threshold
      }
    }
  }
}
```

### Exclude Additional Directories

**Edit:** `~/.local/share/claude-context-local/config.toml`

```toml
[indexing]
exclude_dirs = [
    "node_modules",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    ".git",
    "tmp",              # Add custom exclusions
    "cache",
    "vendor"
]
```

### Change Embedding Model

**Default:** EmbeddingGemma-300m (768-dim)

**Alternatives:** (requires code changes)
- all-MiniLM-L6-v2 (384-dim, faster, less accurate)
- text-embedding-ada-002 (1536-dim, requires API)

**Not recommended:** Stick with default EmbeddingGemma for best results

---

## Comparison to Other Solutions

| Feature | claude-context-local | @zilliz/claude-context | LightRAG |
|---------|---------------------|------------------------|----------|
| **Cost** | $0 forever | $0-0.13/M tokens | $1-5/100 docs |
| **Privacy** | 100% local | Cloud optional | Local optional |
| **Setup** | 5 min (1 command) | 10-15 min | 30 min |
| **MCP Native** | ✅ Yes | ✅ Yes | ❌ No |
| **AST Parsing** | ✅ 8 languages (tree-sitter) | ✅ Yes | ❌ Text only |
| **PDF/DOCX** | ❌ No | ❌ No | ✅ Yes |
| **Offline** | ✅ Always | Partial | Yes |
| **API Keys** | ✅ None | Required* | Required |
| **Maturity** | Beta | Production | Research |

**Winner for Dev-AID:** claude-context-local (code-heavy, local, zero cost)

---

## FAQ

**Q: Do I need an API key?**
A: No API keys needed for RAG. You still need API keys for Claude/Gemini generation, but not for semantic search.

**Q: Does it work offline?**
A: Yes, after initial model download (1.2GB). Everything runs locally.

**Q: How much does it cost?**
A: $0 forever. No API fees, no subscription.

**Q: Is my code sent to the cloud?**
A: No, never. All processing happens on your machine.

**Q: What about large codebases?**
A: Handles 10k+ files easily. Index size scales linearly (~6MB per 350 files).

**Q: Can I use it with VS Code?**
A: Not directly. It's designed for Claude Code and Gemini CLI via MCP. For VS Code, consider other solutions.

**Q: How often should I reindex?**
A: After significant changes (10+ files). Optional: weekly for freshness. Git hook does it automatically.

**Q: Can I index multiple projects?**
A: Yes, run `claude-context-local index` in each project. Indexes are separate.

**Q: What about PDF/DOCX documents?**
A: Not supported. For document search, add LightRAG in hybrid setup.

---

## Related Documentation

- **CLAUDE-CONTEXT-LOCAL.md** - Detailed analysis and comparison
- **RAG-IMPLEMENTATION.md** - Overview of RAG options
- **LIGHTRAG-AND-FORMATS.md** - LightRAG analysis and format support
- **CROSS-PLATFORM-ROUTER.md** - Router implementation guide

---

## Support

**GitHub Issues:** https://github.com/FarhanAliRaza/claude-context-local/issues
**Dev-AID Issues:** https://github.com/Probably-Group/Dev-AID/issues

**Check status:**
```bash
./.dev-aid/scripts/rag-status.sh
```

**Get help:**
```bash
claude-context-local --help
```

---

**Last Updated:** 2026-04-08
**Version:** 1.5.1
**Status:** Production-ready
