# CI Optimization Guide

How to make GitHub Actions workflows faster and more cost-effective.

## ⚡ Quick Wins (Implemented)

### 1. **Concurrency Groups** - Cancel Outdated Runs
**Speed improvement:** ~70% for rapid pushes
**Cost savings:** Significant when pushing multiple commits

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

**What it does:** Automatically cancels older workflow runs when you push new commits. If you push 3 commits in a row, only the latest one runs.

### 2. **Virtual Environment Caching** - Skip Reinstalls
**Speed improvement:** 30-40 seconds per job
**Current:** 50-60s → **Optimized:** 10-20s

```yaml
- uses: actions/cache@v3
  with:
    path: .dev-aid/orchestration/.venv
    key: venv-${{ runner.os }}-py3.11-${{ hashFiles('requirements.txt') }}
```

**What it does:** Caches the entire virtual environment. Dependencies only install once, then reuse across all jobs and future runs until requirements.txt changes.

### 3. **Shared Setup Job** - Install Once, Use Everywhere
**Speed improvement:** Eliminates 3x redundant installs
**Before:** Each job installs independently (4 jobs × 50s = 200s)
**After:** Install once (50s), restore cache 3 times (3 × 5s = 15s)

```yaml
jobs:
  setup:
    # Install all dependencies once

  python-lint:
    needs: setup  # Reuses cached dependencies

  python-test:
    needs: setup  # Reuses cached dependencies
```

### 4. **Explicit Ubuntu Version** - Faster Startup
**Speed improvement:** 2-5 seconds per job
**Change:** `ubuntu-latest` → `ubuntu-22.04`

**Why:** GitHub's "latest" tag adds a resolution step. Explicit versions skip it.

### 5. **Parallel Lint Execution** - Run Tools Together
**Speed improvement:** 5-10 seconds
**Before:** Black → Isort → Flake8 (sequential)
**After:** All three at once (parallel)

```bash
black --check . &
isort --check . &
flake8 . &
wait  # Wait for all to finish
```

## 🚫 Why NOT Alpine?

**Alpine Linux is NOT recommended for Python workflows** despite being smaller:

| Factor | ubuntu-22.04 | alpine:latest |
|--------|-------------|---------------|
| **Image size** | ~2 GB | ~5 MB |
| **Python compatibility** | ✅ glibc (standard) | ❌ musl libc (incompatible) |
| **Package builds** | Pre-compiled wheels work | Must compile from source |
| **Build time** | Fast (use wheels) | Slow (compile everything) |
| **Compatibility** | 99.9% of packages | ~60-70% of packages |

**Real-world example:**
```bash
# ubuntu-22.04: Install numpy (uses wheel)
pip install numpy==1.24.0
# Time: ~3 seconds

# alpine: Install numpy (must compile)
pip install numpy==1.24.0
# Time: ~120 seconds (40x slower!)
# Often fails: "error: command 'gcc' failed"
```

**Packages that break on Alpine:**
- numpy, scipy, pandas (scientific computing)
- cryptography (SSL/TLS)
- psycopg2 (PostgreSQL)
- Many others with C extensions

**Verdict:** Ubuntu is actually faster for Python despite being larger!

## 📊 Performance Comparison

### Current vs Optimized Workflow

| Stage | Current | Optimized | Savings |
|-------|---------|-----------|---------|
| **Setup Python** | 4 × 10s = 40s | 1 × 10s = 10s | -75% |
| **Install deps** | 4 × 50s = 200s | 1 × 50s = 50s | -75% |
| **Restore cache** | 0s (no cache) | 3 × 5s = 15s | - |
| **Run checks** | 60s (sequential) | 50s (parallel) | -17% |
| **Total** | ~300s (5 min) | ~125s (2 min) | **-58%** |

**With cache hit (2nd run):**
| Stage | Current | Optimized | Savings |
|-------|---------|-----------|---------|
| **Setup Python** | 4 × 10s = 40s | 1 × 10s = 10s | -75% |
| **Install deps** | 4 × 50s = 200s | 1 × 5s = 5s | **-97.5%** |
| **Restore cache** | 0s | 3 × 5s = 15s | - |
| **Run checks** | 60s | 50s | -17% |
| **Total** | ~300s (5 min) | ~80s (1.3 min) | **-73%** |

## 🚀 Advanced Optimizations

### 6. **Pytest Parallel Execution** (pytest-xdist)

Run tests in parallel across CPU cores:

```bash
# Install
pip install pytest-xdist

# Use in CI
pytest tests/ -n auto  # Auto-detect CPU count
```

**Speed improvement:** 30-50% for test suites with 50+ tests

**Add to requirements.txt:**
```
pytest-xdist==3.5.0
```

### 7. **Matrix Strategy** - Test Multiple Versions

If you need to test multiple Python versions, use matrix:

```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11', '3.12']

steps:
  - uses: actions/setup-python@v5
    with:
      python-version: ${{ matrix.python-version }}
```

**Runs in parallel** - all 3 versions test simultaneously.

### 8. **Fail-Fast Strategy**

Stop all jobs if one fails (saves time when there's an obvious error):

```yaml
strategy:
  fail-fast: true  # Stop all jobs if one fails
```

**Use carefully:** Only enable if you want to stop everything on first failure.

### 9. **Skip CI for Documentation Changes**

Skip CI for docs-only commits:

```yaml
on:
  push:
    paths-ignore:
      - '**.md'
      - 'docs/**'
```

Or use commit message: `[skip ci]` or `[ci skip]`

### 10. **Sparse Checkout** (For Large Repos)

Only checkout files needed for tests:

```yaml
- uses: actions/checkout@v4
  with:
    sparse-checkout: |
      .dev-aid/orchestration
      .github
```

**Speed improvement:** Significant for repos with large assets/data.

## 💰 Cost Optimization

### GitHub Actions Pricing (2024)

- **Free tier:** 2,000 minutes/month (public repos unlimited)
- **Paid:** $0.008/minute (Ubuntu)
- **Monthly cost estimate:**
  - 100 PRs/month × 5 min = 500 minutes = **$4/month**
  - With optimization: 100 PRs × 2 min = 200 minutes = **$1.60/month**
  - **Savings:** $2.40/month (60% reduction)

### Enterprise Scale

For a team with 50 developers:
- **Before:** 1,000 PRs/month × 5 min = 5,000 min = **$40/month**
- **After:** 1,000 PRs × 2 min = 2,000 min = **$16/month**
- **Annual savings:** $288/year per team

## 🔧 Implementation Plan

### Phase 1: Low-Hanging Fruit (5 minutes)

1. **Add concurrency groups** (instant speedup for rapid pushes)
2. **Use explicit ubuntu-22.04** (2-5s per job)
3. **Enable pip caching** (already done in current workflow ✅)

### Phase 2: Caching Strategy (15 minutes)

4. **Add venv caching** (30-40s per job on cache hit)
5. **Create shared setup job** (eliminate redundant installs)

### Phase 3: Parallel Execution (10 minutes)

6. **Parallelize linting** (5-10s savings)
7. **Add pytest-xdist** (30-50% faster tests)

### Phase 4: Polish (optional)

8. **Add matrix testing** (if needed for multiple Python versions)
9. **Configure fail-fast** (if you want to stop on first failure)
10. **Sparse checkout** (if repo is large)

## 📈 Monitoring Performance

### Check Workflow Duration

```bash
# List recent workflow runs
gh run list --workflow="PR Check" --limit 5

# View specific run timing
gh run view <run-id> --log
```

### Analyze Cache Hit Rate

Check Actions cache usage:
```
https://github.com/<owner>/<repo>/actions/caches
```

**Goal:** 80%+ cache hit rate for dependencies

## 🎯 Expected Results

### Before Optimization
```
PR Check workflow:
├─ Python Lint: 50s
├─ Python Tests: 60s
├─ Type Check: 55s
└─ Bash Lint: 15s
Total: ~5 minutes (parallel execution)
```

### After Optimization (First Run)
```
PR Check workflow:
├─ Setup: 50s (cache dependencies)
├─ Python Lint: 15s (cached venv + parallel)
├─ Python Tests: 35s (cached venv + parallel tests)
├─ Type Check: 20s (cached venv)
└─ Bash Lint: 10s
Total: ~2 minutes (parallel execution)
```

### After Optimization (Subsequent Runs - Cache Hit)
```
PR Check workflow:
├─ Setup: 5s (restore cache)
├─ Python Lint: 10s (cached venv + parallel)
├─ Python Tests: 25s (cached venv + parallel tests)
├─ Type Check: 15s (cached venv)
└─ Bash Lint: 10s
Total: ~1.5 minutes (parallel execution)
```

## ✅ Recommendations

### For Dev-AID (Current State)

1. ✅ **Implement concurrency groups** (immediate benefit)
2. ✅ **Add venv caching** (biggest speedup - 30-40s per job)
3. ✅ **Use shared setup job** (eliminate redundant installs)
4. ✅ **Switch to ubuntu-22.04** (minor speedup)
5. ⚠️  **Consider pytest-xdist** (if test suite grows beyond 100 tests)

### NOT Recommended

- ❌ **Alpine Linux** - Compatibility issues outweigh size benefits
- ❌ **Windows/macOS runners** - 2-3x more expensive, only if needed
- ❌ **Self-hosted runners** - Maintenance overhead unless at scale

## 🤖 Automated CI Generation with `--optimize` Flag

Dev-AID includes a smart CI generator that can automatically create optimized workflows for your project—applying all the optimizations described in this guide with a single command!

### Quick Start

```bash
# Navigate to Dev-AID orchestration directory
cd .dev-aid/orchestration

# Generate optimized workflow (recommended)
python ci-generator.py /path/to/your/project --optimize

# Or for current directory
python ci-generator.py . --optimize
```

### What Gets Generated

The CI generator:
1. **Detects your tech stack** - Python, Node.js, Go, Rust, Java, C#, PHP, Ruby, C++
2. **Identifies package manager** - pip/poetry/uv, npm/pnpm/yarn/bun, cargo, etc.
3. **Applies tech-stack-specific optimizations** - Different caching strategies per language
4. **Includes security scanning** - Gitleaks + Trivy by default
5. **Creates production-ready workflow** - `.github/workflows/ci.yml`

### Optimization Features by Language

**Python:**
```yaml
✅ Concurrency groups (cancel outdated runs)
✅ Virtual environment caching (full .venv cache)
✅ Shared setup job (install once, reuse 3x)
✅ Parallel linting (black & isort & flake8 & wait)
✅ Explicit ubuntu-22.04 (faster startup)
```

**Node.js:**
```yaml
✅ Concurrency groups
✅ node_modules caching (faster installs)
✅ Package manager cache (npm/pnpm/yarn/bun)
✅ Parallel linting (eslint & prettier & tsc & wait)
✅ Explicit ubuntu-22.04
```

**Go:**
```yaml
✅ Concurrency groups
✅ Go module cache (automatic)
✅ Build artifact cache (~/.cache/go-build)
✅ Parallel checks (gofmt & go vet & wait)
✅ Explicit ubuntu-22.04
```

**Rust:**
```yaml
✅ Concurrency groups
✅ Cargo registry cache
✅ Cargo git index cache
✅ Build target cache (incremental compilation)
✅ Parallel checks (cargo fmt & cargo clippy & wait)
✅ Explicit ubuntu-22.04
```

**Java (Maven/Gradle):**
```yaml
✅ Concurrency groups
✅ Maven .m2/repository cache
✅ Parallel builds (mvn -T 1C)
✅ Explicit ubuntu-22.04
```

**C#/.NET:**
```yaml
✅ Concurrency groups
✅ NuGet package cache
✅ Parallel builds (--parallel flag)
✅ Explicit ubuntu-22.04
```

### Standard vs Optimized Templates

| Feature | Standard Template | Optimized Template |
|---------|------------------|-------------------|
| **Security scanning** | ✅ Gitleaks + Trivy | ✅ Gitleaks + Trivy |
| **Concurrency groups** | ❌ | ✅ Cancel outdated runs |
| **Advanced caching** | Basic (package manager) | ✅ Full (venv/node_modules/cargo) |
| **Parallel execution** | ❌ Sequential | ✅ Parallel linting/checks |
| **Shared setup job** | ❌ Each job installs | ✅ Install once, reuse |
| **Runner** | ubuntu-latest | ubuntu-22.04 (faster) |
| **Expected CI time** | 5 minutes | 1.5-2 minutes |

### Example Output

```bash
$ python ci-generator.py . --optimize

🔍 Detecting project context...
✅ Detected: python
   Package Manager: pip
   Docker: Yes

⚡ Using optimized template with:
   - Concurrency groups (cancel outdated runs)
   - Advanced caching (dependencies + build artifacts)
   - Parallel execution (linting, testing)
   - Explicit ubuntu-22.04 (faster startup)
   - Expected speedup: 40-70% faster CI runs

🛠️  Generating CI workflow...
✅ Generated: .github/workflows/ci.yml
   Lines: 183

📋 Commands configured:
   install: pip install -r requirements.txt
   test: pytest
   lint: flake8 .
   type_check: mypy .

✅ Done! Workflow includes:
   - Security scanning (Gitleaks + Trivy)
   - Linting and type checking
   - Testing across multiple versions

⚡ Optimization features:
   - Concurrency control for faster iteration
   - Comprehensive caching for reduced build times
   - Parallel execution where possible
   📖 See .dev-aid/docs/CI-OPTIMIZATION-GUIDE.md for details
```

### When to Use Standard vs Optimized

**Use Standard Template When:**
- ⚡ Simple project with fast CI already (< 2 min)
- 🧪 Testing the generator for the first time
- 📚 Learning GitHub Actions basics
- 🔒 Strict organizational policies on workflow structure

**Use Optimized Template When:**
- 🚀 CI is slow (> 3 min) and you want faster feedback
- 💰 Reducing GitHub Actions costs (for teams/orgs)
- 🔁 Frequent commits trigger many workflow runs
- ✅ Ready for production-grade CI/CD
- 👥 Team project with multiple contributors

### Manual Application

If you prefer to manually apply optimizations to an existing workflow:

1. **Review this guide** - Understand each optimization
2. **Start with quick wins** - Concurrency groups + explicit ubuntu-22.04
3. **Add caching** - Tech-stack specific (venv, node_modules, cargo, etc.)
4. **Enable parallelization** - Linting, testing where applicable
5. **Test thoroughly** - Ensure caching works correctly

### Troubleshooting

**Issue: Cache not working**
```bash
# Check cache key matches file hashes
# For Python: hashFiles('requirements.txt', 'pyproject.toml')
# For Node.js: hashFiles('package-lock.json', 'yarn.lock', 'pnpm-lock.yaml')
# For Rust: hashFiles('**/Cargo.lock')
```

**Issue: Parallel execution fails**
```bash
# Some linters don't support parallel execution
# Use sequential fallback:
black --check . && isort --check . && flake8 .
```

**Issue: ubuntu-22.04 not available**
```bash
# Fallback to ubuntu-latest if 22.04 is deprecated
runs-on: ubuntu-latest  # GitHub will provide latest stable
```

## 🔗 References

- [GitHub Actions: Caching dependencies](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)
- [GitHub Actions: Concurrency](https://docs.github.com/en/actions/using-jobs/using-concurrency)
- [Why not Alpine for Python](https://pythonspeed.com/articles/alpine-docker-python/)
- [pytest-xdist documentation](https://pytest-xdist.readthedocs.io/)

## 📝 Summary

**Best optimizations for Python CI:**
1. 🚀 Concurrency groups (cancel outdated runs)
2. 💾 Virtual environment caching
3. 🔄 Shared setup job
4. ⚡ Parallel execution (linting + tests)
5. 🎯 Explicit ubuntu-22.04

**Expected speedup:** 58-73% faster (5 min → 1.5-2 min)

**Alpine Linux:** ❌ NOT recommended for Python workflows
