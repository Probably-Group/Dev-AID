# Dev-AID Storage Locations

## Overview

Dev-AID stores files in three locations to optimize for portability, privacy, and Git workflow.

---

## 📁 Storage Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Storage Locations                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. Project Repository (.dev-aid/)                           │
│     ✅ Committed to Git                                      │
│     Size: ~5MB (configuration + scripts)                     │
│                                                               │
│  2. User Home (~/.local/share/)                              │
│     ❌ NOT in Git (shared across projects)                   │
│     Size: ~1.2GB (RAG model + installation)                  │
│                                                               │
│  3. User Home (~/.claude_code_search/)                       │
│     ❌ NOT in Git (per-project index)                        │
│     Size: Varies (semantic index of YOUR codebase)           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Project Repository (.dev-aid/)

**Location**: `<project-root>/.dev-aid/`

**What's stored**:
```
.dev-aid/
├── config/                    # ✅ Commit (team config)
│   ├── routing.json
│   ├── models.json
│   ├── settings.json
│   ├── mcp-template.json
│   └── .env                   # ❌ NEVER commit (API keys)
│
├── providers/                 # ✅ Commit (skills, commands)
│   ├── claude/
│   ├── gemini/
│   └── openai/
│
├── memory-bank/               # ✅ Commit (team knowledge)
│   ├── activeContext.md
│   ├── patterns.md
│   └── decisions.md
│
├── scripts/                   # ✅ Commit (setup scripts)
│   ├── setup-dev-aid.sh
│   ├── init-repo.sh           # (backward compat)
│   ├── setup-rag.sh
│   └── reindex-codebase.sh
│
├── orchestration/             # ✅ Commit (router code)
│   ├── router/               # Python package
│   ├── requirements.txt
│   └── .venv/                 # ❌ Git ignored (70MB per project)
│
├── logs/                      # ❌ Git ignored (runtime logs)
│   ├── routing.log
│   ├── costs.json
│   └── rag-index.log
│
└── docs/                      # ✅ Commit (documentation)
    ├── DEPENDENCY-ISOLATION.md
    └── router/README.md
```

**Git behavior**:
- ✅ **Committed**: Configuration, skills, scripts, memory bank, documentation
- ❌ **Ignored**: API keys (.env), logs, virtual environment (.venv)

**Why in repository**:
- Team shares same expert skills
- Consistent routing configuration
- Portable across projects

**Size**: ~5MB (without .venv)

---

## 2. claude-context-local Installation

**Location**: `~/.local/share/claude-context-local/`

**What's stored**:
```
~/.local/share/claude-context-local/
├── mcp_server/              # MCP server implementation
│   └── server.py
├── pyproject.toml           # uv dependency config
├── uv.lock                  # Dependency lockfile
└── .venv/                   # uv-managed environment
    ├── bin/
    └── lib/python3.x/site-packages/
        ├── torch/           # PyTorch (~500MB)
        ├── transformers/    # Hugging Face (~200MB)
        └── faiss/           # FAISS (~50MB)
```

**Size**: ~1.2GB (one-time, shared across all projects)

**Git behavior**: ❌ **NOT in any project Git** (stored in home directory)

**Why in home directory**:
- EmbeddingGemma model is 1.2GB - too large for project repos
- Shared across ALL projects that use Dev-AID
- Managed by `uv` (automatic dependency isolation)
- Installed once, used everywhere

**Installation**: `./.dev-aid/scripts/setup-rag.sh`

---

## 3. RAG Model & Index Storage

**Location**: `~/.claude_code_search/`

**What's stored**:
```
~/.claude_code_search/
├── models/                  # EmbeddingGemma model
│   ├── embedding-gemma-2b/  # ~1.2GB (downloaded once)
│   └── tokenizer/
│
└── index/                   # Per-project semantic index
    ├── <project-1>/        # Your first project
    │   ├── faiss.index     # FAISS vector index
    │   ├── metadata.db     # File paths, chunks
    │   └── stats.json      # Index statistics
    │
    └── <project-2>/        # Your second project
        ├── faiss.index
        └── metadata.db
```

**Size**:
- **Model**: 1.2GB (one-time download, shared)
- **Index per project**: 10-500MB (depends on codebase size)

**Git behavior**: ❌ **NOT in Git** (generated from source code)

**Why in home directory**:
- Model shared across all projects
- Index is regenerated from source code (not needed in Git)
- Each project gets its own index subdirectory
- Can reindex anytime with: `./.dev-aid/scripts/reindex-codebase.sh`

**Regeneration**: Index can always be recreated from source code

---

## 🎯 What Should Be in Git?

### ✅ Always Commit

| Path | Why |
|------|-----|
| `.dev-aid/config/` | Team configuration (except .env) |
| `.dev-aid/providers/` | Expert skills, slash commands |
| `.dev-aid/memory-bank/` | Team knowledge, ADRs |
| `.dev-aid/scripts/` | Setup and automation scripts |
| `.dev-aid/orchestration/router/` | Router Python code |
| `.dev-aid/orchestration/requirements.txt` | Dependencies list |
| `.dev-aid/docs/` | Documentation |

### ❌ Never Commit

| Path | Why | Size |
|------|-----|------|
| `.dev-aid/config/.env` | **SECURITY**: Contains API keys | <1KB |
| `.dev-aid/logs/` | Runtime logs, regenerated | ~1MB |
| `.dev-aid/orchestration/.venv/` | Virtual environment, reproducible | ~70MB |
| `~/.local/share/claude-context-local/` | Not in project, in home | ~1.2GB |
| `~/.claude_code_search/` | Not in project, in home | ~1.5GB |

---

## 🔄 Multi-Project Sharing

### Shared Across All Projects (Home Directory)

**claude-context-local** (~1.2GB):
- ✅ Installed ONCE in `~/.local/share/`
- ✅ Used by ALL projects
- ✅ No duplication

**EmbeddingGemma Model** (~1.2GB):
- ✅ Downloaded ONCE to `~/.claude_code_search/models/`
- ✅ Used by ALL projects
- ✅ No duplication

### Per-Project (Repository)

**Dev-AID Configuration** (~5MB per project):
```bash
project-a/.dev-aid/  # Project A config
project-b/.dev-aid/  # Project B config (can be different)
```

**Router Virtual Environment** (~70MB per project):
```bash
project-a/.dev-aid/orchestration/.venv/  # Isolated dependencies
project-b/.dev-aid/orchestration/.venv/  # Isolated dependencies
```

**RAG Index** (varies, in `~/.claude_code_search/index/`):
```bash
~/.claude_code_search/index/project-a/  # Project A index
~/.claude_code_search/index/project-b/  # Project B index
```

---

## 📊 Total Disk Usage

### Single Project with Dev-AID

```
In repository:
  .dev-aid/                    ~5MB   (committed)
  .dev-aid/.venv/             ~70MB   (git ignored)
  .dev-aid/logs/              ~1MB    (git ignored)

In home directory (shared):
  ~/.local/share/...          ~1.2GB  (one-time)
  ~/.claude_code_search/      ~1.5GB  (one-time + per-project index)

Total first project:          ~2.8GB
Total second project:         ~76MB  (only .venv + index, model reused)
```

---

## 🧹 Cleanup

### Remove Dev-AID from Single Project

```bash
# Remove from project (keeps shared components for other projects)
cd your-project
rm -rf .dev-aid

# Repository size reduction: ~5MB (excluding .venv which wasn't committed)
```

### Remove claude-context-local Completely

```bash
# Remove installation (affects ALL projects)
rm -rf ~/.local/share/claude-context-local

# Remove all indexes and model
rm -rf ~/.claude_code_search

# Disk space freed: ~2.7GB
```

### Remove Router Virtual Environment

```bash
# Per-project cleanup
cd your-project
rm -rf .dev-aid/orchestration/.venv

# Disk space freed: ~70MB per project
# Can recreate with: ./setup-venv.sh
```

---

## 🔍 Verification Commands

### Check Storage Usage

```bash
# Check repository size
du -sh .dev-aid/
# Expected: ~5MB (without .venv)

# Check what's committed
git ls-files .dev-aid/ | head -20

# Check virtual environment size
du -sh .dev-aid/orchestration/.venv/
# Expected: ~70MB

# Check RAG installation
du -sh ~/.local/share/claude-context-local/
# Expected: ~1.2GB

# Check RAG index
du -sh ~/.claude_code_search/
# Expected: ~1.5GB (model + indexes)
```

### Verify .gitignore Working

```bash
# Should NOT show these files:
git status --ignored | grep -E "(\.env|\.venv|logs)"

# Should show (if they exist):
# .dev-aid/config/.env        (ignored)
# .dev-aid/orchestration/.venv/  (ignored)
# .dev-aid/logs/              (ignored)
```

---

## 🎓 Best Practices

### For Individual Developers

**Clone repository**:
```bash
git clone <repo>
cd project
ls .dev-aid/  # ✅ Dev-AID config already there
```

**Setup dependencies**:
```bash
# Router venv (per-project, ~5 minutes)
./.dev-aid/orchestration/setup-venv.sh

# RAG (one-time, ~10 minutes)
./.dev-aid/scripts/setup-rag.sh
```

### For Teams

**Commit to repository**:
- ✅ All `.dev-aid/` except `.env`, `.venv`, `logs/`
- ✅ Updated skills, routing config, memory bank
- ❌ Never commit `.env` (API keys are personal)

**Document in README**:
```markdown
## Setup Dev-AID

1. Clone repo (includes .dev-aid/ config)
2. Setup router: `./.dev-aid/orchestration/setup-venv.sh`
3. Optional RAG: `./.dev-aid/scripts/setup-rag.sh`
4. Copy `.dev-aid/config/.env.example` to `.env` and add your API keys
```

### For CI/CD

**What to cache**:
```yaml
# .github/workflows/ci.yml
cache:
  paths:
    - .dev-aid/orchestration/.venv/  # Router deps
    - ~/.local/share/claude-context-local/  # RAG (if needed)
```

**What NOT to cache**:
- API keys (use GitHub Secrets instead)
- Logs (regenerated)
- RAG indexes (regenerate in CI)

---

## 📚 Related Documentation

- [DEPENDENCY-ISOLATION.md](./DEPENDENCY-ISOLATION.md) - Virtual environment architecture
- [Updating Dev-AID](./UPDATING.md) - How to update to new versions
- [.gitignore](../../.gitignore) - Files excluded from Git

---

**Summary**: Dev-AID stores 5MB of configuration in your repository (committed), ~70MB of virtual environment per project (ignored), and ~2.7GB of shared RAG components in your home directory (one-time). Your repository stays clean while getting enterprise-grade AI capabilities.
