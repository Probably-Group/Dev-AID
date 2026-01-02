# Python Version Requirements for Dev-AID

## Critical Finding from Dependency Update

During Phase 1 dependency updates, we discovered critical Python version constraints:

### Module Requirements

**Orchestration Module** (`.dev-aid/orchestration/`)
- `pyproject.toml` requires: **Python >= 3.11**
- Current venv uses: Python 3.8.5 (Anaconda)
- **Status:** ⚠️ MISMATCH - venv needs recreation

**Local Search Module** (`.dev-aid/local-search/`)
- `pyproject.toml` requires: **Python >= 3.9**
- Dependency `mcp==1.23.1` requires: **Python >= 3.10**
- Dependency `torch` (via sentence-transformers) requires: **Python < 3.14**
- **Effective requirement:** **Python >= 3.10 and < 3.14**

### Dependency-Specific Constraints

| Package | Minimum Python | Maximum Python | Notes |
|---------|---------------|----------------|-------|
| `mcp==1.23.1` | 3.10 | - | Model Context Protocol SDK |
| `torch` (via sentence-transformers) | 3.9 | 3.13 | No wheels for Python 3.14 yet |
| `faiss-cpu==1.8.0` | 3.9 | 3.12 | Old version pinned |
| `faiss-cpu==1.13.1` | 3.9 | 3.14 | Latest, but breaks faiss API |
| `vcrpy==6.0.2` | 3.8 | 3.10+ | urllib3 < 2 constraint on Python < 3.10 |

### Recommended Python Versions

**✅ Python 3.11 or 3.12** - Best compatibility with all dependencies

**⚠️ Python 3.10** - Works but is minimum for mcp

**❌ Python 3.8/3.9** - Too old for mcp >= 1.23

**❌ Python 3.14** - Too new for torch/faiss-cpu wheels

### Action Items

1. **Recreate both venvs with Python 3.11 or 3.12**
2. **Update `.dev-aid/local-search/pyproject.toml`**: `requires-python = ">=3.10,<3.14"`
3. **Document in README:** Python 3.11+ required for Dev-AID
4. **Consider:** Using `pyenv` or `conda` for Python version management

### Current Blockers

- [ ] Orchestration venv using Python 3.8 (should be 3.11+)
- [ ] Local search cannot install with Python 3.14 (torch incompatibility)
- [ ] Local search cannot install with Python 3.8 (mcp incompatibility)
- [ ] faiss-cpu version jump (1.8.0 → 1.13.1) may break existing indexes

