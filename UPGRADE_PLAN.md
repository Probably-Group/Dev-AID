# Dev-AID Dependency Upgrade Plan
**Created:** 2025-12-07
**Status:** Ready for Execution

This document provides the **exact commands and steps** to safely upgrade Dev-AID dependencies based on the analysis in `DEPENDENCY_ANALYSIS.md`.

---

## Quick Summary

**Total Updates Available:** 20 packages
- 🔴 High Risk (Major versions): 3 packages
- 🟡 Medium Risk (Minor versions): 7 packages
- 🟢 Low Risk (Patches): 10 packages

**Recommended Approach:** Phased rollout (4 phases over 2-4 weeks)

---

## Phase 1: Low-Risk Patches ✅ SAFE TO EXECUTE NOW

**Time Required:** 1-2 hours (including testing)
**Risk Level:** 🟢 LOW

### Files to Update

#### `.dev-aid/orchestration/requirements.txt`

```bash
cd /Users/martinholovsky/Github/Dev-AID/.dev-aid/orchestration

# Backup current requirements
cp requirements.txt requirements-backup-$(date +%Y%m%d).txt

# Update these lines:
sed -i.bak 's/pydantic==2.10.3/pydantic==2.10.6/' requirements.txt
sed -i.bak 's/pytest==8.3.4/pytest==8.3.5/' requirements.txt
sed -i.bak 's/mypy==1.13.0/mypy==1.14.1/' requirements.txt
sed -i.bak 's/email-validator==2.2.0/email-validator==2.3.0/' requirements.txt
sed -i.bak 's/flake8==7.1.1/flake8==7.1.2/' requirements.txt

# Install updated dependencies
source venv/bin/activate
pip install -r requirements.txt
```

**Or manually edit:**
```diff
- pydantic==2.10.3
+ pydantic==2.10.6

- pytest==8.3.4
+ pytest==8.3.5

- mypy==1.13.0
+ mypy==1.14.1

- email-validator==2.2.0
+ email-validator==2.3.0

- flake8==7.1.1
+ flake8==7.1.2
```

#### `.dev-aid/local-search/pyproject.toml`

```bash
cd /Users/martinholovsky/Github/Dev-AID/.dev-aid/local-search

# Backup
cp pyproject.toml pyproject-backup-$(date +%Y%m%d).toml
```

**Manual edit:**
```diff
dependencies = [
-   "pydantic==2.10.3",
+   "pydantic==2.10.6",
-   "click==8.1.7",
+   "click==8.1.8",
-   "faiss-cpu==1.8.0",
+   "faiss-cpu==1.8.0.post1",
    # ... rest unchanged
]
```

### Testing Commands

```bash
# Test orchestration module
cd /Users/martinholovsky/Github/Dev-AID/.dev-aid/orchestration
source venv/bin/activate

# Run full test suite
pytest tests/ -v --tb=short

# Check code quality
black --check router/ tests/
isort --check router/ tests/
flake8 router/ tests/
mypy router/

# Security scans
bandit -r router/
safety check
pip-audit

# Test coverage
pytest tests/ --cov=router --cov-report=term-missing

# Expected: All tests pass, coverage ≥ 59%
```

```bash
# Test local-search module
cd /Users/martinholovsky/Github/Dev-AID/.dev-aid/local-search
source venv/bin/activate || python3 -m venv venv && source venv/bin/activate

# Install dependencies
pip install -e .
pip install -e ".[dev]"

# Run tests
pytest tests/ -v --tb=short

# Expected: All 47 tests pass
```

### Rollback if Needed

```bash
# Orchestration
cd .dev-aid/orchestration
cp requirements-backup-$(date +%Y%m%d).txt requirements.txt
pip install -r requirements.txt

# Local Search
cd .dev-aid/local-search
cp pyproject-backup-$(date +%Y%m%d).toml pyproject.toml
pip install -e .
```

### Git Commit

```bash
cd /Users/martinholovsky/Github/Dev-AID
git add .dev-aid/orchestration/requirements.txt
git add .dev-aid/local-search/pyproject.toml

git commit -m "chore: update low-risk dependencies (Phase 1)

- pydantic: 2.10.3 → 2.10.6 (patch)
- pytest: 8.3.4 → 8.3.5 (patch)
- mypy: 1.13.0 → 1.14.1 (minor)
- email-validator: 2.2.0 → 2.3.0 (minor)
- flake8: 7.1.1 → 7.1.2 (patch)
- click: 8.1.7 → 8.1.8 (patch)
- faiss-cpu: 1.8.0 → 1.8.0.post1 (patch)

All tests passing. Low-risk updates only.
"
```

---

## Phase 2: Medium-Risk Updates ⚠️ TEST THOROUGHLY

**Time Required:** 4-6 hours (including testing)
**Risk Level:** 🟡 MEDIUM
**Prerequisites:** Phase 1 completed successfully

### Files to Update

#### Both modules: Update Rich

```bash
# Orchestration
cd /Users/martinholovsky/Github/Dev-AID/.dev-aid/orchestration
sed -i.bak 's/rich==13.9.4/rich==14.2.0/' requirements.txt

# Local Search
cd /Users/martinholovsky/Github/Dev-AID/.dev-aid/local-search
# Update pyproject.toml manually
```

```diff
# .dev-aid/orchestration/requirements.txt
- rich==13.9.4
+ rich==14.2.0

# .dev-aid/local-search/pyproject.toml
- "rich==13.9.4",
+ "rich==14.2.0",
```

#### Orchestration only: Update Typer & Safety

```diff
# .dev-aid/orchestration/requirements.txt
- typer==0.15.1
+ typer==0.20.0

- safety==3.2.11
+ safety==3.6.2
```

#### Local Search only: Update Sentence Transformers

```diff
# .dev-aid/local-search/pyproject.toml
- "sentence-transformers==3.0.1",
+ "sentence-transformers==3.2.1",
```

### Testing Commands

```bash
# Orchestration - Test CLI visually
cd .dev-aid/orchestration
source venv/bin/activate
pip install -r requirements.txt

# Visual inspection of CLI output
dev-aid-router --help
dev-aid-router query "test prompt" --provider anthropic --dry-run

# Test security tools
safety check --full-report
pip-audit --desc

# Run full test suite
pytest tests/ -v
```

```bash
# Local Search - Test embeddings & search
cd .dev-aid/local-search
source venv/bin/activate
pip install -e ".[dev]"

# Test embedding generation (critical path)
pytest tests/test_embeddings.py -v

# Test index building
pytest tests/test_index.py -v

# Full test suite
pytest tests/ -v

# Manual smoke test
devaid-code-search build --help
```

### Visual Testing Checklist

Since `rich` controls terminal output, **manually verify**:

- [ ] Help text renders correctly
- [ ] Progress bars display properly
- [ ] Tables are formatted correctly
- [ ] Colors are appropriate
- [ ] Error messages are readable
- [ ] Logging output is clear

### Git Commit

```bash
git add .dev-aid/orchestration/requirements.txt
git add .dev-aid/local-search/pyproject.toml

git commit -m "chore: update medium-risk dependencies (Phase 2)

- rich: 13.9.4 → 14.2.0 (major, terminal UI)
- typer: 0.15.1 → 0.20.0 (minor, CLI framework)
- safety: 3.2.11 → 3.6.2 (minor, security scanner)
- sentence-transformers: 3.0.1 → 3.2.1 (minor, ML library)

All tests passing. Visual CLI output verified.
"
```

---

## Phase 3: High-Risk SDK Updates 🔴 REQUIRES EXTENSIVE TESTING

**Time Required:** 8-12 hours (including testing)
**Risk Level:** 🔴 HIGH
**Prerequisites:** Phases 1 & 2 completed successfully

### 3A: Investigate httpx Constraint

**Current constraint:** `httpx<0.27` for proxy compatibility

```bash
# Test if httpx 0.28.1 works with proxies
cd .dev-aid/orchestration
source venv/bin/activate

# Create test script
cat > test_httpx_proxy.py << 'EOF'
import httpx
import os

# Test with proxy environment variables
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:8080'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:8080'

try:
    with httpx.Client() as client:
        # Test basic proxy functionality
        print(f"httpx version: {httpx.__version__}")
        print(f"Proxy support: {client._mounts}")
        print("✓ Proxy initialization successful")
except Exception as e:
    print(f"✗ Proxy test failed: {e}")
EOF

# Install httpx 0.28.1
pip install httpx==0.28.1

# Run test
python test_httpx_proxy.py

# Clean up
rm test_httpx_proxy.py
```

**Decision:**
- ✅ If test passes → Remove `<0.27` constraint, upgrade to 0.28.1
- ❌ If test fails → Keep `<0.27` constraint, check anthropic compatibility

### 3B: Update Anthropic SDK (Conditional)

**Only proceed if httpx constraint resolved or anthropic 0.72.0 compatible with httpx<0.27**

```bash
# Check anthropic 0.72.0 requirements
pip download anthropic==0.72.0 --no-deps
tar -xzf anthropic-0.72.0.tar.gz
grep -A5 "install_requires" anthropic-0.72.0/setup.py | grep httpx
# Or check: cat anthropic-0.72.0/pyproject.toml | grep httpx
```

**If compatible:**

```diff
# .dev-aid/orchestration/requirements.txt
- anthropic==0.39.0
+ anthropic==0.72.0

- httpx==0.26.0
+ httpx==0.28.1  # Only if proxy test passed
```

**Testing:**

```bash
cd .dev-aid/orchestration
source venv/bin/activate
pip install -r requirements.txt

# Test anthropic provider
pytest tests/test_providers.py::test_anthropic_provider -v

# Test MCP integration
pytest tests/test_mcp.py -v

# Integration test with real API (if API key available)
dev-aid-router query "Hello, test message" --provider anthropic

# Verify cost tracking still works
pytest tests/test_cost_tracking.py -v
```

### 3C: Update OpenAI SDK (v1 → v2 MAJOR)

**⚠️ BREAKING CHANGES EXPECTED**

**Before updating:**
1. Read migration guide: https://github.com/openai/openai-python/releases/tag/v2.0.0
2. Review all code using `openai` module
3. Identify breaking changes in Dev-AID codebase

```bash
# Find all OpenAI usage
cd /Users/martinholovsky/Github/Dev-AID
grep -r "from openai" .dev-aid/orchestration/
grep -r "import openai" .dev-aid/orchestration/
```

**Expected changes:**
- API method signatures
- Response object structure
- Error handling
- Streaming interface

**Migration:**

```diff
# .dev-aid/orchestration/requirements.txt
- openai==1.54.5
+ openai==2.7.1
```

**Testing:**

```bash
# Test OpenAI provider thoroughly
pytest tests/test_providers.py::test_openai_provider -v

# Test streaming (if used)
# Test tool calling (if used)
# Test embeddings (if used)

# Integration test
dev-aid-router query "Hello, test message" --provider openai

# Cost tracking
pytest tests/test_cost_tracking.py -v
```

### 3D: Update Google Generative AI (RC → Stable)

**First, find latest stable:**

```bash
# Check PyPI manually or use web search
# Visit: https://pypi.org/project/google-generativeai/

# Or try:
curl -s https://pypi.org/pypi/google-generativeai/json | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['info']['version'])"
```

**Update:**

```diff
# .dev-aid/orchestration/requirements.txt
- google-generativeai==0.1.0rc1
+ google-generativeai==<LATEST_STABLE_VERSION>
```

**Testing:**

```bash
pytest tests/test_providers.py::test_google_provider -v

# Integration test
dev-aid-router query "Hello, test message" --provider google
```

### Git Commit (per SDK)

**Commit after each SDK update, don't batch them:**

```bash
# After anthropic update
git add .dev-aid/orchestration/requirements.txt
git commit -m "chore: update anthropic SDK to 0.72.0

- anthropic: 0.39.0 → 0.72.0
- httpx: 0.26.0 → 0.28.1 (if updated)

All anthropic provider tests passing.
Verified: API calls, MCP integration, cost tracking.
"

# After openai update
git commit -m "chore: update openai SDK to v2.7.1 (MAJOR)

- openai: 1.54.5 → 2.7.1 (v1 → v2)

Breaking changes handled:
- [list specific changes made to code]

All OpenAI provider tests passing.
"

# After google-generativeai update
git commit -m "chore: migrate google-generativeai from RC to stable

- google-generativeai: 0.1.0rc1 → <VERSION>

Now using stable release instead of release candidate.
All Google provider tests passing.
"
```

---

## Phase 4: Tree-Sitter Investigation 🔍 RESEARCH REQUIRED

**Time Required:** 2-4 hours
**Risk Level:** ⚠️ UNKNOWN

### Investigation Steps

1. **Check PyPI manually:**

```bash
# Visit in browser
open "https://pypi.org/project/tree-sitter/"

# Check version history
# Look for 0.23.2 in release history
```

2. **Verify installed version:**

```bash
cd .dev-aid/local-search
source venv/bin/activate
pip show tree-sitter

# Check actual version
python -c "import tree_sitter; print(tree_sitter.__version__)"
```

3. **Check tree-sitter-* bindings compatibility:**

```bash
# Verify all language bindings are compatible with tree-sitter==0.23.2
pip show tree-sitter-python | grep Requires
pip show tree-sitter-javascript | grep Requires
pip show tree-sitter-typescript | grep Requires
# ... repeat for all language bindings
```

4. **Test code parsing:**

```bash
# Run parser tests
pytest tests/test_chunker.py -v

# Manual test with different languages
python -c "
from chunking.chunker import CodeChunker
chunker = CodeChunker()

# Test Python parsing
python_code = '''
def hello():
    print('Hello, world!')
'''
chunks = chunker.chunk_code(python_code, 'python')
print(f'Python chunks: {len(chunks)}')

# Test JavaScript parsing
js_code = '''
function hello() {
    console.log('Hello, world!');
}
'''
chunks = chunker.chunk_code(js_code, 'javascript')
print(f'JavaScript chunks: {len(chunks)}')
"
```

### Possible Outcomes

**Outcome A:** 0.23.2 is correct, PyPI index is wrong/stale
- **Action:** Keep 0.23.2, document in DEPENDENCY_ANALYSIS.md

**Outcome B:** 0.23.2 doesn't exist, we have wrong version
- **Action:** Check what's actually installed, update pyproject.toml to match

**Outcome C:** Should downgrade to 0.21.3
- **Action:** Test downgrade, verify bindings compatibility, update if safe

**Outcome D:** Different versioning scheme/source
- **Action:** Investigate source (conda, GitHub, etc.), document correct approach

### Git Commit (based on outcome)

```bash
# If keeping 0.23.2
git add DEPENDENCY_ANALYSIS.md
git commit -m "docs: document tree-sitter version discrepancy

PyPI shows 0.21.3 as latest, but 0.23.2 is correct.
Reason: [explanation from investigation]

All parser tests passing with 0.23.2.
"

# If updating
git add .dev-aid/local-search/pyproject.toml
git commit -m "fix: correct tree-sitter version to match PyPI

- tree-sitter: 0.23.2 → 0.21.3

Reason: [explanation]
All parser tests passing.
"
```

---

## Emergency Rollback Procedure

### If Anything Goes Wrong

```bash
# Stop immediately
cd /Users/martinholovsky/Github/Dev-AID

# Revert to last working commit
git status  # Check what changed
git diff    # Review changes

# Option 1: Revert specific files
git checkout HEAD -- .dev-aid/orchestration/requirements.txt
git checkout HEAD -- .dev-aid/local-search/pyproject.toml

# Option 2: Revert entire commit
git log --oneline -5  # Find commit hash
git revert <commit-hash>

# Reinstall old versions
cd .dev-aid/orchestration && source venv/bin/activate && pip install -r requirements.txt
cd .dev-aid/local-search && source venv/bin/activate && pip install -e ".[dev]"

# Verify tests pass
pytest .dev-aid/orchestration/tests/ -v
pytest .dev-aid/local-search/tests/ -v
```

---

## Recommended Execution Timeline

### Week 1
- **Monday:** Execute Phase 1, commit if tests pass
- **Tuesday:** Execute Phase 2, commit if tests pass
- **Wednesday:** Phase 4 investigation (tree-sitter)

### Week 2-3
- **Prepare:** Review SDK migration guides
- **Test:** Set up test environment for Phase 3
- **Execute:** Phase 3A (httpx investigation)
- **Execute:** Phase 3B (anthropic) if compatible

### Week 4
- **Execute:** Phase 3C (OpenAI v2 migration)
- **Execute:** Phase 3D (Google Gemini stable)
- **Verify:** Full integration testing
- **Document:** Update DEPENDENCY_ANALYSIS.md with results

---

## Success Criteria

### Phase 1 Success
- ✅ All tests pass in both modules
- ✅ Code quality checks pass (black, isort, flake8, mypy)
- ✅ Security scans pass (bandit, safety, pip-audit)
- ✅ Test coverage maintained (≥ 59% orchestration)

### Phase 2 Success
- ✅ All Phase 1 criteria met
- ✅ CLI output renders correctly (visual inspection)
- ✅ Semantic search quality unchanged
- ✅ No performance regression

### Phase 3 Success
- ✅ All Phase 1-2 criteria met
- ✅ All 3 AI providers work correctly
- ✅ Cost tracking accurate
- ✅ MCP integration functional
- ✅ No breaking changes in API behavior

### Phase 4 Success
- ✅ Version discrepancy explained and documented
- ✅ Code parsing works for all supported languages
- ✅ Decision made and documented

---

## Post-Upgrade Checklist

After completing all phases:

- [ ] Update `DEPENDENCY_ANALYSIS.md` with actual versions used
- [ ] Document any issues encountered and solutions
- [ ] Update `.github/dependabot.yml` if exists
- [ ] Create PR with all changes
- [ ] Tag release with updated dependencies
- [ ] Update changelog
- [ ] Notify users of any breaking changes

---

**Document Version:** 1.0
**Last Updated:** 2025-12-07
**Next Review:** After Phase 1 completion
