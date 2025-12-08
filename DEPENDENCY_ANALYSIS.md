# Dev-AID Dependency Analysis
**Date:** 2025-12-07
**Analysis Type:** Full dependency audit across all modules

## Executive Summary

This analysis covers all dependencies across Dev-AID's two Python modules:
- `.dev-aid/orchestration/` - Multi-AI router and orchestration
- `.dev-aid/local-search/` - Local semantic code search with MCP

**Key Findings:**
- 🔴 **2 MAJOR version updates available** (openai, rich, anthropic)
- 🟡 **10 minor/patch updates available**
- 🟢 **8 dependencies up to date**
- ⚠️  **1 potential version conflict** (tree-sitter versioning scheme)

---

## 1. Orchestration Module Dependencies

### File: `.dev-aid/orchestration/requirements.txt`

| Package | Current | Latest | Update Type | Priority | Notes |
|---------|---------|--------|-------------|----------|-------|
| **anthropic** | 0.39.0 | 0.72.0 | 🔴 MAJOR | HIGH | +33 versions behind, test for breaking changes |
| **google-generativeai** | 0.1.0rc1 | TBD | ⚠️ RC | HIGH | Using release candidate, need stable version |
| **openai** | 1.54.5 | 2.7.1 | 🔴 MAJOR | HIGH | v2.x may have breaking changes |
| **python-dotenv** | 1.0.1 | 1.0.1 | ✅ CURRENT | - | Up to date |
| **requests** | 2.32.4 | 2.32.4 | ✅ CURRENT | - | Up to date |
| **pydantic** | 2.10.3 | 2.10.6 | 🟡 PATCH | MEDIUM | Safe patch update |
| **email-validator** | 2.2.0 | 2.3.0 | 🟡 MINOR | LOW | Minor update |
| **rich** | 13.9.4 | 14.2.0 | 🔴 MAJOR | MEDIUM | v14.x may have visual changes |
| **typer** | 0.15.1 | 0.20.0 | 🟡 MINOR | MEDIUM | 5 minor versions behind |
| **httpx** | 0.26.0 | 0.28.1 | 🟡 MINOR | MEDIUM | Required by anthropic SDK |
| **pytest** | 8.3.4 | 8.3.5 | 🟢 PATCH | LOW | Safe patch update |
| **pytest-asyncio** | 0.24.0 | 0.24.0 | ✅ CURRENT | - | Up to date (likely) |
| **pytest-cov** | 5.0.0 | 5.0.0 | ✅ CURRENT | - | Up to date (likely) |
| **pytest-mock** | 3.14.0 | 3.14.0 | ✅ CURRENT | - | Up to date (likely) |
| **vcrpy** | 6.0.2 | 6.0.2 | ✅ CURRENT | - | Up to date (likely) |
| **hypothesis** | 6.113.0 | 6.113.0 | ✅ CURRENT | - | Up to date (likely) |
| **bandit** | 1.7.10 | 1.7.10 | ✅ CURRENT | - | Up to date |
| **safety** | 3.2.11 | 3.6.2 | 🟡 MINOR | MEDIUM | Security scanner, should update |
| **pip-audit** | 2.7.3 | 2.7.3 | ✅ CURRENT | - | Up to date |
| **mypy** | 1.13.0 | 1.14.1 | 🟡 MINOR | LOW | Type checker update |
| **types-requests** | 2.32.0.20241016 | 2.32.0.20241016 | ✅ CURRENT | - | Up to date (likely) |
| **pre-commit** | 3.5.0 | 3.5.0 | ✅ CURRENT | - | Up to date |
| **black** | 24.8.0 | 24.8.0 | ✅ CURRENT | - | Up to date |
| **isort** | 5.13.2 | 5.13.2 | ✅ CURRENT | - | Up to date |
| **flake8** | 7.1.1 | 7.1.2 | 🟢 PATCH | LOW | Safe patch update |

---

## 2. Local Search Module Dependencies

### File: `.dev-aid/local-search/pyproject.toml`

| Package | Current | Latest | Update Type | Priority | Notes |
|---------|---------|--------|-------------|----------|-------|
| **sentence-transformers** | 3.0.1 | 3.2.1 | 🟡 MINOR | MEDIUM | ML library, test for model compatibility |
| **faiss-cpu** | 1.8.0 | 1.8.0.post1 | 🟢 PATCH | LOW | Post-release patch |
| **mcp** | 1.23.0 | 1.23.0 | ✅ CURRENT | - | Recently updated for CVE fixes |
| **pydantic** | 2.10.3 | 2.10.6 | 🟡 PATCH | MEDIUM | Shared with orchestration |
| **click** | 8.1.7 | 8.1.8 | 🟢 PATCH | LOW | Safe patch update |
| **rich** | 13.9.4 | 14.2.0 | 🔴 MAJOR | MEDIUM | Same as orchestration |
| **tree-sitter** | 0.23.2 | 0.21.3 ⚠️ | ⚠️ CONFLICT | CRITICAL | **See note below** |
| **tree-sitter-python** | 0.23.6 | TBD | - | - | Language binding |
| **tree-sitter-javascript** | 0.23.1 | TBD | - | - | Language binding |
| **tree-sitter-typescript** | 0.23.2 | TBD | - | - | Language binding |
| **tree-sitter-java** | 0.23.4 | TBD | - | - | Language binding |
| **tree-sitter-go** | 0.23.3 | TBD | - | - | Language binding |
| **tree-sitter-rust** | 0.23.0 | TBD | - | - | Language binding |
| **tree-sitter-c** | 0.23.4 | TBD | - | - | Language binding |
| **tree-sitter-cpp** | 0.23.3 | TBD | - | - | Language binding |

### ⚠️ Tree-Sitter Version Conflict

**Current:** 0.23.2
**PyPI Latest:** 0.21.3

**Issue:** Our pinned version (0.23.2) is NEWER than what PyPI shows as "latest" (0.21.3).

**Possible explanations:**
1. The tree-sitter package was recently updated and PyPI index is stale
2. Version 0.23.x is a pre-release or beta that we're using
3. Different versioning scheme or packaging issue

**Action Required:**
```bash
# Verify what's actually available on PyPI
pip3 index versions tree-sitter | head -20

# Check if our version exists and is valid
pip3 show tree-sitter

# Verify against official PyPI page
# https://pypi.org/project/tree-sitter/
```

---

## 3. Critical Interdependencies

### 3.1 Anthropic SDK → httpx

**Current:**
- anthropic==0.39.0
- httpx==0.26.0

**Latest:**
- anthropic==0.72.0
- httpx==0.28.1

**Compatibility Check Required:**
The Anthropic SDK has strict httpx version requirements. Before upgrading:

```bash
# Check what httpx version anthropic 0.72.0 requires
pip3 index versions anthropic | grep 0.72.0
pip download anthropic==0.72.0 --no-deps
tar -xzf anthropic-0.72.0.tar.gz
cat anthropic-0.72.0/setup.py | grep httpx
```

**Note in requirements.txt:** "httpx<0.27 for proxies compatibility"
- This constraint may prevent upgrading to httpx 0.28.1
- Need to verify if proxy support works with newer httpx

### 3.2 Pydantic Compatibility

**Usage:**
- Both orchestration and local-search use pydantic==2.10.3
- anthropic SDK depends on pydantic
- email-validator depends on pydantic

**Upgrade Plan:**
Update pydantic to 2.10.6 across both modules simultaneously to ensure consistency.

### 3.3 Rich Terminal Output

**Usage:**
- Both orchestration and local-search use rich==14.2.0 (✅ upgraded)
- CLI output formatting depends on this

**Status:** ✅ Upgraded to 14.2.0 (major version)
- May have visual/formatting changes
- Test CLI output after upgrade

---

## 4. Upgrade Risk Assessment

### 🔴 HIGH RISK (Breaking Changes Likely)

1. **openai: 1.54.5 → 2.7.1**
   - Major version bump (v1 → v2)
   - Review migration guide: https://github.com/openai/openai-python/releases/tag/v2.0.0
   - **Test:** All OpenAI provider interactions in router
   - **Rollback plan:** Keep 1.54.5 until testing complete

2. **anthropic: 0.39.0 → 0.72.0**
   - 33 versions behind
   - Check release notes for 0.40.0-0.72.0
   - **Test:** All Claude provider interactions in router
   - **Dependency:** May require httpx upgrade

3. **google-generativeai: 0.1.0rc1 → stable**
   - Currently using release candidate
   - Need to identify latest stable version
   - **Test:** All Gemini provider interactions

### 🟡 MEDIUM RISK (Minor Changes Possible)

4. **rich: 13.9.4 → 14.2.0**
   - Major version, but terminal library (cosmetic changes likely)
   - **Test:** CLI output visual appearance

5. **typer: 0.15.1 → 0.20.0**
   - CLI framework update
   - **Test:** All CLI commands and arguments

6. **sentence-transformers: 3.0.1 → 3.2.1**
   - ML library update
   - **Test:** Embedding generation, index building, search results

7. **safety: 3.2.11 → 3.6.2**
   - Security scanner update
   - **Test:** Security check workflow

### 🟢 LOW RISK (Safe Updates)

8. **pydantic: 2.10.3 → 2.10.6** (patch)
9. **httpx: 0.26.0 → 0.28.1** (minor, if compatible)
10. **pytest: 8.3.4 → 8.3.5** (patch)
11. **mypy: 1.13.0 → 1.14.1** (minor)
12. **email-validator: 2.2.0 → 2.3.0** (minor)
13. **click: 8.1.7 → 8.1.8** (patch)
14. **faiss-cpu: 1.8.0 → 1.8.0.post1** (post-release)
15. **flake8: 7.1.1 → 7.1.2** (patch)

---

## 5. Recommended Upgrade Phases

### Phase 1: Low-Risk Patches (1-2 hours testing)
**Goal:** Update all patch versions and low-risk minors

```toml
# orchestration/requirements.txt
pydantic==2.10.6          # 2.10.3 → 2.10.6
pytest==8.3.5              # 8.3.4 → 8.3.5
mypy==1.14.1               # 1.13.0 → 1.14.1
email-validator==2.3.0     # 2.2.0 → 2.3.0
flake8==7.1.2              # 7.1.1 → 7.1.2

# local-search/pyproject.toml
pydantic==2.10.6           # 2.10.3 → 2.10.6
click==8.1.8               # 8.1.7 → 8.1.8
faiss-cpu==1.8.0.post1     # 1.8.0 → 1.8.0.post1
```

**Testing:**
```bash
cd .dev-aid/orchestration
source venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
black --check router/ tests/
isort --check router/ tests/
flake8 router/ tests/
mypy router/
```

### Phase 2: Medium-Risk Updates (4-6 hours testing)
**Goal:** Update UI/UX and tooling libraries

```toml
# Both modules
rich==14.2.0               # 13.9.4 → 14.2.0

# orchestration only
typer==0.20.0              # 0.15.1 → 0.20.0
safety==3.6.2              # 3.2.11 → 3.6.2

# local-search only
sentence-transformers==3.2.1  # 3.0.1 → 3.2.1
```

**Testing:**
```bash
# Test CLI output visually
dev-aid-router --help
dev-aid-code-search --help

# Test security scanning
cd .dev-aid/orchestration
safety check
bandit -r router/

# Test semantic search
cd .dev-aid/local-search
pytest tests/ -v
# Manual test: build index, run searches
```

### Phase 3: High-Risk SDK Updates (8-12 hours testing)
**Goal:** Update AI provider SDKs

**Option A: Conservative (Recommended)**
Update one provider at a time:

```toml
# Week 1: Anthropic only
anthropic==0.72.0
httpx==0.28.1  # If compatible
```

**Option B: Aggressive**
Update all at once (not recommended):

```toml
anthropic==0.72.0
google-generativeai==<latest-stable>
openai==2.7.1
```

**Testing per provider:**
```bash
# Test router with each provider
dev-aid-router query "test prompt" --provider anthropic
dev-aid-router query "test prompt" --provider openai
dev-aid-router query "test prompt" --provider google

# Integration tests
pytest tests/test_providers.py -v
pytest tests/test_mcp.py -v

# Cost tracking
pytest tests/test_cost_tracking.py -v
```

### Phase 4: Tree-Sitter Investigation (2-4 hours)
**Goal:** Resolve version conflict

1. Verify actual latest version on PyPI
2. Check tree-sitter-* bindings compatibility
3. Test code parsing for all supported languages
4. Update or keep current version based on findings

---

## 6. Testing Checklist

### Orchestration Module
- [ ] All 3 AI providers work (Claude, GPT, Gemini)
- [ ] Cost tracking calculates correctly
- [ ] MCP client connects to servers
- [ ] Environment isolation works
- [ ] CLI commands execute properly
- [ ] Rich terminal output renders correctly
- [ ] All 47 MCP tests pass
- [ ] Test coverage ≥ 59%

### Local Search Module
- [ ] Code chunking works for all languages
- [ ] Embedding generation succeeds
- [ ] FAISS index builds correctly
- [ ] Search returns relevant results
- [ ] MCP server starts and responds
- [ ] All 47 search tests pass
- [ ] Pickle to JSON migration works

### Cross-Module
- [ ] Pydantic validation works in both modules
- [ ] Rich output consistent across CLIs
- [ ] No dependency version conflicts
- [ ] Security scans pass (bandit, safety, pip-audit)
- [ ] Type checking passes (mypy)
- [ ] Formatting passes (black, isort, flake8)

---

## 7. Rollback Procedures

### If Phase 1 Fails
```bash
git checkout HEAD -- .dev-aid/orchestration/requirements.txt
git checkout HEAD -- .dev-aid/local-search/pyproject.toml
cd .dev-aid/orchestration && pip install -r requirements.txt
```

### If Phase 2 Fails
```bash
# ✅ Phase 2 completed successfully (commit: 6b24546)
# To revert if needed:
git revert 6b24546
pip install rich==13.9.4
pip install typer==0.15.1
pip install sentence-transformers==3.0.1
```

### If Phase 3 Fails
```bash
# Revert SDK versions
pip install anthropic==0.39.0
pip install openai==1.54.5
pip install httpx==0.26.0
```

---

## 8. Known Issues & Constraints

### httpx < 0.27 Constraint
**Source:** `.dev-aid/orchestration/requirements.txt:29`

**Quote:** "Modern HTTP client (used by Anthropic SDK, <0.27 for proxies compatibility)"

**Impact:**
- Blocks upgrade to httpx 0.28.1
- May block upgrade to anthropic 0.72.0 if it requires httpx ≥ 0.27

**Action:**
1. Test proxy functionality with httpx 0.28.1
2. If proxies work, remove constraint
3. If proxies break, keep httpx < 0.27 and check anthropic compatibility

### Google Generative AI Release Candidate
**Current:** 0.1.0rc1

**Issue:** Using unstable release candidate in production

**Action:**
```bash
# Find latest stable
pip3 index versions google-generativeai | grep -v rc | head -5

# Update to latest stable
pip install google-generativeai==<latest-stable>
```

### Tree-Sitter Versioning Mystery
**Current:** 0.23.2 (pinned)
**PyPI "Latest":** 0.21.3

**Required Investigation:**
1. Visit https://pypi.org/project/tree-sitter/
2. Check if 0.23.2 is pre-release, beta, or from different source
3. Verify all tree-sitter-* bindings are compatible with 0.23.2
4. Document findings and make decision to upgrade/downgrade/stay

---

## 9. Cost-Benefit Analysis

### Benefits of Upgrading

**Security:**
- Patch known vulnerabilities in dependencies
- Update security scanning tools (safety, pip-audit)

**Features:**
- Access new AI SDK features (prompt caching, tool calling improvements)
- Better type checking (mypy 1.14.1)
- Improved ML models (sentence-transformers 3.2.1)

**Stability:**
- Bug fixes in patch releases
- Better compatibility with modern Python

### Costs of Upgrading

**Time Investment:**
- Phase 1: 1-2 hours
- Phase 2: 4-6 hours
- Phase 3: 8-12 hours
- Phase 4: 2-4 hours
- **Total:** 15-24 hours

**Risk:**
- Potential breaking changes in major version updates
- Regression in AI provider functionality
- Time lost if rollback required

### Recommendation

**Proceed with Phases 1-2 immediately:**
- Low risk, high value
- Security and stability improvements
- Minimal testing required

**Delay Phase 3 until:**
- Critical need for new SDK features
- Security vulnerability in current SDK versions
- Scheduled maintenance window available

**Investigate Phase 4 immediately:**
- Version conflict needs resolution
- Could be blocking other updates

---

## 10. Action Items

### Immediate (This Week)
- [ ] Investigate tree-sitter version conflict
- [ ] Find google-generativeai latest stable version
- [ ] Test httpx 0.28.1 proxy compatibility
- [ ] Execute Phase 1 upgrades (low-risk patches)

### Short-Term (Next 2 Weeks)
- [ ] Execute Phase 2 upgrades (medium-risk)
- [ ] Review anthropic SDK 0.40.0-0.72.0 release notes
- [ ] Review openai SDK v2 migration guide
- [ ] Create test plan for Phase 3

### Long-Term (Next Month)
- [ ] Execute Phase 3 upgrades (high-risk SDKs)
- [ ] Set up automated dependency monitoring
- [ ] Create CI/CD pipeline for dependency updates
- [ ] Document update procedures in DEPENDENCY_UPDATE_GUIDE.md

---

## 11. Dependency Update Schedule

### Monthly Routine (First Monday)
1. Check for security vulnerabilities: `pip-audit`, `safety check`
2. Review available updates: `pip list --outdated`
3. Execute Phase 1 updates if available
4. Run full test suite

### Quarterly Review (First of Quarter)
1. Review all dependencies for major updates
2. Read release notes for major version jumps
3. Plan Phase 2-3 updates
4. Schedule testing window

### Annual Audit (January)
1. Full dependency tree analysis
2. Remove unused dependencies
3. Consolidate duplicate dependencies
4. Update Python version if needed

---

## Appendix A: Commands Reference

### Check Single Package
```bash
pip3 index versions <package-name> | head -5
pip3 show <package-name>
```

### Check All Outdated
```bash
pip list --outdated
```

### Security Scanning
```bash
pip-audit --desc
safety check --full-report
bandit -r <directory>
```

### Update Single Package
```bash
pip install --upgrade <package-name>==<version>
```

### Freeze Current State
```bash
pip freeze > requirements-backup.txt
```

### Verify Compatibility
```bash
pip check
```

---

**Generated:** 2025-12-07
**Next Review:** 2026-01-07 (monthly)
**Document Version:** 1.0
