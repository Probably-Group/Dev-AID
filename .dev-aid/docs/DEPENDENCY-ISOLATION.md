# Dependency Isolation in Dev-AID

**TL;DR**: Dev-AID uses three separate isolated environments. **Zero system-wide Python package installations required.** No dependency conflicts, ever.

---

## 🎯 Architecture Overview

Dev-AID implements a **multi-layer isolation strategy** to ensure your development environment remains clean and conflict-free:

```
┌─────────────────────────────────────────────────────────┐
│                    Dev-AID Repository                    │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────┐ │
│  │ Router Package │  │ claude-context │  │   Bash     │ │
│  │                │  │     -local     │  │  Scripts   │ │
│  ├────────────────┤  ├────────────────┤  ├────────────┤ │
│  │ Python venv    │  │ uv environment │  │  Built-in  │ │
│  │ .venv/         │  │ ~/.local/...   │  │  modules   │ │
│  ├────────────────┤  ├────────────────┤  ├────────────┤ │
│  │ • anthropic    │  │ • torch        │  │ • json     │ │
│  │ • openai       │  │ • transformers │  │ • git      │ │
│  │ • google-gen   │  │ • faiss        │  │ • curl     │ │
│  └────────────────┘  └────────────────┘  └────────────┘ │
│                                                           │
│         ✅ No Conflicts    ✅ No System Pollution        │
└─────────────────────────────────────────────────────────┘
```

---

## 🔒 Isolation Layers

### Layer 1: Router Virtual Environment

**Location**: `.dev-aid/orchestration/.venv/`

**Purpose**: Multi-AI orchestration engine

**Isolation Method**: Python's built-in `venv` module

**Dependencies**:
```
anthropic==0.75.0
google-genai==1.53.0
openai==1.54.5
python-dotenv==1.0.1
pydantic==2.10.6
rich==14.2.0
typer==0.20.0
httpx==0.28.1
```

**How it works**:
1. User runs `./dev-aid/orchestration/setup-venv.sh`
2. Creates isolated Python environment in `.venv/`
3. `router-cli.sh` automatically activates venv when needed
4. Deactivates after execution completes

**Benefits**:
- ✅ Completely separate from system Python
- ✅ Can use different package versions than other projects
- ✅ Easy cleanup: `rm -rf .venv`
- ✅ Lightweight (~50MB)
- ✅ Standard Python practice

---

### Layer 2: RAG Environment (claude-context-local)

**Location**: `~/.local/share/claude-context-local/`

**Purpose**: Local semantic code search with MCP integration

**Isolation Method**: `uv` package manager (automatic)

**Dependencies**:
```
torch
transformers
faiss-cpu / faiss-gpu
sentence-transformers
numpy
```

**How it works**:
1. User runs `./.dev-aid/scripts/setup-rag.sh`
2. Installs claude-context-local via official script
3. `uv` automatically manages isolated environment
4. MCP server runs via: `uv run --directory ~/.local/share/claude-context-local python mcp_server/server.py`

**Benefits**:
- ✅ Zero manual environment management
- ✅ `uv` handles isolation automatically
- ✅ No conflicts with router or system Python
- ✅ Modern, fast package management
- ✅ Works offline after initial setup

---

### Layer 3: System Python (Built-ins Only)

**Location**: System Python installation

**Purpose**: Basic utilities in bash scripts

**What's used**:
```bash
python3 -m json.tool  # Pretty-print JSON (built-in module)
```

**Dependencies installed**: **ZERO**

**Benefits**:
- ✅ No package installations required
- ✅ System Python stays pristine
- ✅ Uses only built-in modules (json, sys, etc.)
- ✅ No maintenance needed

---

## 📊 Dependency Conflict Matrix

| Environment A | Environment B | Can Conflict? | Reason |
|--------------|---------------|---------------|---------|
| Router venv | System Python | ❌ **NO** | Separate directories |
| Router venv | RAG (uv) | ❌ **NO** | Different isolation mechanisms |
| RAG (uv) | System Python | ❌ **NO** | uv manages own environment |
| Project A venv | Project B venv | ❌ **NO** | Each project has own .venv/ |

**Verdict**: ✅ **Zero possibility of dependency conflicts between any components**

---

## 🚀 Setup Process

### Automated Setup (Recommended)

```bash
# Initialize Dev-AID (offers to setup both environments)
./.dev-aid/scripts/setup-dev-aid.sh

# When prompted:
# 1. "Setup router with virtual environment? (Y/n)" → Y
# 2. "Setup RAG with claude-context-local? (Y/n)" → Y

# Both environments created automatically!
```

### Manual Setup

```bash
# Setup router venv
./.dev-aid/orchestration/setup-venv.sh

# Setup RAG environment
./.dev-aid/scripts/setup-rag.sh
```

---

## 🧪 Verify Isolation

### Test 1: System Python Remains Clean

```bash
# Capture system packages before Dev-AID
pip list > /tmp/before.txt

# Setup Dev-AID (both router and RAG)
./.dev-aid/scripts/setup-dev-aid.sh

# Capture system packages after Dev-AID
pip list > /tmp/after.txt

# Compare (should be identical)
diff /tmp/before.txt /tmp/after.txt
# Expected output: (no differences)
```

### Test 2: Router Uses Venv

```bash
# Check active Python when router runs
./.dev-aid/orchestration/router-cli.sh execute "test" --verbose | grep "Python:"

# Expected: Python: /path/to/Dev-AID/.dev-aid/orchestration/.venv/bin/python3
```

### Test 3: RAG Uses uv Environment

```bash
# Check where torch is installed (if RAG setup)
uv pip list --directory ~/.local/share/claude-context-local | grep torch

# Expected: torch package listed (NOT in system Python)
```

---

## 📁 File Locations

### Router Environment

```
.dev-aid/orchestration/
├── .venv/                          # Virtual environment
│   ├── bin/
│   │   ├── python3                 # Isolated Python
│   │   ├── pip                     # Isolated pip
│   │   └── activate                # Activation script
│   ├── lib/python3.x/site-packages/ # Router dependencies here
│   └── pyvenv.cfg                  # venv configuration
├── requirements.txt                # Router dependencies
└── setup-venv.sh                   # Setup script
```

### RAG Environment

```
~/.local/share/claude-context-local/
├── mcp_server/
│   └── server.py                   # MCP server
├── pyproject.toml                  # uv dependency config
├── uv.lock                         # uv lockfile
└── .venv/                          # uv-managed environment
    └── lib/python3.x/site-packages/ # RAG dependencies here
```

---

## 🎓 Why This Approach?

### Why venv instead of Anaconda?

| Feature | Python venv | Anaconda |
|---------|-------------|----------|
| **Size** | ~50MB | ~3GB |
| **Installation** | Built into Python 3.3+ | Separate download |
| **Speed** | Fast | Slower |
| **Use Case** | Pure Python projects ✅ | Data science + system libs |
| **Complexity** | Simple | More features, more complex |
| **Dev-AID needs** | ✅ Perfect fit | ❌ Overkill |

**Verdict**: venv is lightweight, standard, and perfect for Dev-AID's pure-Python dependencies.

### Why uv for RAG?

| Feature | uv | pip + venv |
|---------|----|--------------|
| **Speed** | 10-100x faster | Standard |
| **Automatic isolation** | ✅ Yes | Manual setup |
| **Lockfiles** | ✅ Built-in | Requires pip-tools |
| **Project-aware** | ✅ Yes | Need activation |
| **Used by** | claude-context-local | Traditional Python |

**Verdict**: RAG tool chose uv, so we use it. No manual env management needed.

---

## 🔄 How Components Execute

### Router Execution Flow

```bash
# User runs:
./.dev-aid/orchestration/router-cli.sh execute "Implement OAuth"

# Internally:
1. router-cli.sh checks if .venv/ exists
2. If yes: source .venv/bin/activate
3. Runs: python3 -m router.cli execute "Implement OAuth"
   - Uses .venv/lib/python3.x/site-packages/anthropic
   - NOT system Python packages
4. Deactivates venv: deactivate
5. Returns to system Python

# User's system Python never touched! ✅
```

### RAG Execution Flow

```bash
# Claude Code uses RAG via MCP:
uv run --directory ~/.local/share/claude-context-local python mcp_server/server.py

# Internally:
1. uv reads pyproject.toml for dependencies
2. uv checks if environment exists
3. If not: uv creates isolated environment automatically
4. Runs Python with isolated dependencies
5. No manual activation needed

# User's system Python never touched! ✅
```

---

## 🧹 Cleanup

### Remove Router Environment

```bash
# Delete venv (safe - just a directory)
rm -rf .dev-aid/orchestration/.venv

# System Python unaffected ✅
```

### Remove RAG Environment

```bash
# Delete entire claude-context-local installation
rm -rf ~/.local/share/claude-context-local

# Also remove index if desired
rm -rf ~/.claude_code_search

# System Python unaffected ✅
```

### Verify Clean System

```bash
# Check system Python packages
pip list

# Should NOT see:
# - anthropic, openai, google-generativeai (router packages)
# - torch, transformers, faiss (RAG packages)
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'anthropic'"

**Cause**: Router venv not activated or not created

**Fix**:
```bash
# Recreate venv
./.dev-aid/orchestration/setup-venv.sh

# Or activate manually
source .dev-aid/orchestration/.venv/bin/activate
```

### "Router fails but system Python has all packages"

**Cause**: System packages installed, but router needs venv

**Why**: Router looks for venv first (preferred isolation)

**Fix**:
```bash
# Create venv properly
./.dev-aid/orchestration/setup-venv.sh

# Router will use venv automatically
```

### "RAG says Python 3.12+ required but I have 3.9"

**Cause**: Different Python versions needed for router vs RAG

**Solution**: This is FINE! They're isolated:
- Router venv uses Python 3.9+ ✅
- RAG needs system Python 3.12+ (separate) ✅
- No conflict because they run in different environments

**Fix**: Install Python 3.12+ system-wide (RAG will use it, router keeps using 3.9)

---

## 📚 Best Practices

### 1. Always Use Provided Scripts

✅ **Good**:
```bash
./.dev-aid/orchestration/router-cli.sh execute "request"
```

❌ **Avoid**:
```bash
python3 -m router.cli execute "request"  # Might use wrong Python
```

**Why**: Scripts handle activation/deactivation automatically

### 2. Let uv Manage RAG

✅ **Good**:
```bash
# Let claude-context-local setup handle everything
./.dev-aid/scripts/setup-rag.sh
```

❌ **Avoid**:
```bash
# Don't try to manually manage RAG environment
pip install torch transformers  # Wrong approach
```

**Why**: uv automatically creates isolated environment

### 3. Keep Venvs Per-Project

✅ **Good**:
```
~/projects/Dev-AID/.dev-aid/orchestration/.venv/
~/projects/other-project/.venv/
```

❌ **Avoid**:
```bash
# Don't create shared global venvs
~/global-venv/  # Bad idea
```

**Why**: Each project should have isolated dependencies

---

## 🎯 Summary

| Question | Answer |
|----------|--------|
| Does Dev-AID pollute system Python? | ❌ **NO** |
| Can router dependencies conflict with other projects? | ❌ **NO** |
| Can RAG dependencies conflict with router? | ❌ **NO** |
| Do I need to manually activate environments? | ❌ **NO** - Scripts handle it |
| Do I need Anaconda or conda? | ❌ **NO** - venv is sufficient |
| What needs system-wide installation? | Only Python itself + curl/git |
| What if I delete .venv/? | ✅ Just run setup-venv.sh again |
| Can I use Dev-AID in multiple projects? | ✅ Yes, each has own venv |

---

## 🔗 Related Documentation

- [Router Installation Guide](../orchestration/ROUTER-INSTALL.md)
- [Virtual Environment Setup](../orchestration/VENV-INFO.md)
- [RAG Setup Guide](../scripts/setup-rag.sh)
- [Dev-AID Architecture](./SKILLS-ARCHITECTURE.md)

---

**Last Updated**: 2025-12-08
**Status**: ✅ Production-ready isolation strategy
