# CI/CD Performance Optimization Patterns

This document covers performance optimization strategies for CI/CD pipelines, focusing on caching, parallelization, artifact management, and incremental builds.

---

## 1. Caching Strategies

### 1.1 Aggressive Caching with Proper Keys

**Good - Comprehensive caching with smart cache keys:**
```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.npm
      node_modules
      ~/.cargo/registry
      target
    key: ${{ runner.os }}-deps-${{ hashFiles('**/package-lock.json', '**/Cargo.lock') }}
    restore-keys: |
      ${{ runner.os }}-deps-
```

**Why This Works**:
- Caches multiple dependency directories
- Uses hash of lock files for cache key (changes only when dependencies change)
- Includes fallback restore-keys for partial cache hits
- Dramatically reduces build times

**Bad - No caching or poor cache keys:**
```yaml
# Missing caching - slow builds every time
- run: npm ci
- run: cargo build
```

**Why This Fails**:
- Downloads and builds dependencies from scratch every time
- Wastes CI minutes and increases build times
- No benefit from unchanged dependencies

### 1.2 Multi-Level Caching

**Advanced pattern - Layer caching for maximum efficiency:**
```yaml
jobs:
  build:
    steps:
      # Level 1: Package manager cache
      - uses: actions/cache@v4
        with:
          path: ~/.npm
          key: ${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}

      # Level 2: node_modules cache
      - uses: actions/cache@v4
        with:
          path: node_modules
          key: ${{ runner.os }}-modules-${{ hashFiles('**/package-lock.json') }}

      # Level 3: Build output cache
      - uses: actions/cache@v4
        with:
          path: dist/
          key: ${{ runner.os }}-build-${{ github.sha }}
          restore-keys: |
            ${{ runner.os }}-build-
```

**Benefits**:
- Different cache invalidation strategies per layer
- Faster cache restoration for partial changes
- Reuse build outputs when possible

---

## 2. Parallel Jobs

### 2.1 Independent Job Parallelization

**Good - Independent jobs run in parallel:**
```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm run lint

  test-unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm run test:unit

  test-e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm run test:e2e

  build:
    needs: [lint, test-unit, test-e2e]  # Waits for all parallel jobs
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm run build
```

**Performance Gain**: 3-4x faster than sequential execution

**Bad - Sequential jobs that could be parallel:**
```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps: [...]

  test-unit:
    needs: lint  # Unnecessary dependency
    steps: [...]

  test-e2e:
    needs: test-unit  # Unnecessary dependency
    steps: [...]
```

**Why This Fails**:
- Jobs wait unnecessarily
- Total pipeline time = sum of all job times
- No utilization of parallel runners

### 2.2 Matrix Strategy for Multi-Platform Builds

**Good - Parallel builds across platforms:**
```yaml
jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        node-version: [18, 20]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm ci && npm run build
```

**Benefits**:
- 6 builds run in parallel (3 OS × 2 Node versions)
- Catches platform-specific issues early
- Total time = slowest build, not sum of all builds

---

## 3. Artifact Optimization

### 3.1 Compress and Limit Retention

**Good - Optimized artifact handling:**
```yaml
- name: Upload artifacts
  uses: actions/upload-artifact@v4
  with:
    name: build-output
    path: dist/
    retention-days: 7
    compression-level: 9
    if-no-files-found: error
```

**Why This Works**:
- Compression reduces storage costs
- Short retention for non-release builds
- Fails fast if expected artifacts missing

**Bad - Large uncompressed artifacts with long retention:**
```yaml
- uses: actions/upload-artifact@v4
  with:
    name: everything
    path: .  # Uploads entire repo including node_modules!
    retention-days: 90
```

**Costs**:
- Massive storage costs
- Slow upload/download times
- Wastes GitHub Actions storage quota

### 3.2 Conditional Artifact Upload

**Good - Upload artifacts only when needed:**
```yaml
- name: Upload build artifacts
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
  uses: actions/upload-artifact@v4
  with:
    name: production-build
    path: dist/

- name: Upload test coverage
  if: always()  # Upload even on failure
  uses: actions/upload-artifact@v4
  with:
    name: coverage
    path: coverage/
    retention-days: 3
```

**Benefits**:
- Reduces artifact storage for PR builds
- Always preserves important debug info (coverage)
- Longer retention for production builds

---

## 4. Incremental Builds

### 4.1 Path-Based Change Detection

**Good - Skip unchanged components:**
```yaml
- name: Check for changes
  id: changes
  uses: dorny/paths-filter@v2
  with:
    filters: |
      frontend:
        - 'src/frontend/**'
      backend:
        - 'src/backend/**'
      docs:
        - 'docs/**'

- name: Build frontend
  if: steps.changes.outputs.frontend == 'true'
  run: npm run build:frontend

- name: Build backend
  if: steps.changes.outputs.backend == 'true'
  run: cargo build --release

- name: Build docs
  if: steps.changes.outputs.docs == 'true'
  run: npm run build:docs
```

**Performance Gain**: Skip entire build stages when component unchanged

**Bad - Always rebuild everything:**
```yaml
- run: npm run build:frontend
- run: cargo build --release
- run: npm run build:docs
# Runs even when no changes to those components
```

**Wasted Resources**: Rebuilds unchanged code on every commit

### 4.2 Turbo/Nx Monorepo Caching

**Good - Smart monorepo builds with Turborepo:**
```yaml
- name: Setup Turborepo cache
  uses: actions/cache@v4
  with:
    path: .turbo
    key: ${{ runner.os }}-turbo-${{ github.sha }}
    restore-keys: |
      ${{ runner.os }}-turbo-

- name: Build
  run: npx turbo build --cache-dir=.turbo
```

**Benefits**:
- Only rebuilds changed packages
- Shares build cache across CI runs
- Massive speedup for large monorepos

---

## 5. Conditional Workflows

### 5.1 Path Filters at Workflow Level

**Good - Run expensive jobs only when needed:**
```yaml
on:
  push:
    branches: [main]
    paths:
      - 'src/**'
      - 'Cargo.toml'
      - 'package.json'
      - '.github/workflows/**'  # Also run when workflow changes

jobs:
  expensive-test:
    if: contains(github.event.head_commit.message, '[full-test]') || github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - run: npm run test:e2e:all
```

**Benefits**:
- Workflow doesn't even start if paths don't match
- Commit message override for manual full testing
- Reduced CI minutes usage

**Bad - Run everything on every push:**
```yaml
on: [push]  # Triggers on every branch, every commit

jobs:
  full-e2e-suite:  # Expensive job runs unnecessarily
    runs-on: ubuntu-latest
    steps:
      - run: npm run test:e2e:all  # 30+ minutes
```

**Waste**: Runs expensive tests even for documentation changes

### 5.2 Branch-Based Conditional Logic

**Good - Different behavior per branch:**
```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to staging
        if: github.ref == 'refs/heads/develop'
        run: npm run deploy:staging

      - name: Deploy to production
        if: github.ref == 'refs/heads/main'
        run: npm run deploy:production

      - name: Preview deploy for PRs
        if: github.event_name == 'pull_request'
        run: npm run deploy:preview
```

**Benefits**:
- Single workflow handles all environments
- Clear conditions for each deployment
- No duplicate workflow definitions

---

## 6. Build Time Optimization

### 6.1 Docker Layer Caching

**Good - Optimal Dockerfile layer ordering:**
```dockerfile
# Least changing layers first
FROM node:20-alpine

# Dependencies layer (changes rarely)
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Source code layer (changes frequently)
COPY . .
RUN npm run build

# Each layer cached independently
```

**GitHub Actions Docker caching:**
```yaml
- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v3

- name: Build with cache
  uses: docker/build-push-action@v5
  with:
    context: .
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

**Performance Gain**: 10x faster Docker builds with proper caching

### 6.2 Compiler Caching (Rust/C++)

**Good - Cache Rust compilation artifacts:**
```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.cargo/registry
      ~/.cargo/git
      target/
    key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}

- uses: Swatinem/rust-cache@v2
  with:
    shared-key: "stable"
```

**Performance Gain**: 5-10x faster Rust builds

**C++ with ccache:**
```yaml
- name: Setup ccache
  uses: hendrikmuhs/ccache-action@v1

- name: Build with ccache
  run: |
    export CC="ccache gcc"
    export CXX="ccache g++"
    cmake --build build
```

---

## 7. Network Optimization

### 7.1 Shallow Clones for Large Repos

**Good - Fetch only what's needed:**
```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 1  # Shallow clone
    submodules: false  # Skip unless needed
```

**Performance Gain**: 10x faster checkout for repos with long history

**When to use full history:**
```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0  # Full history needed for changelogs, git describe
```

### 7.2 Dependency Proxies

**Good - Use GitHub's dependency proxy (npm, Maven):**
```yaml
- name: Configure npm registry
  run: npm config set registry https://registry.npmjs.org

- uses: actions/setup-node@v4
  with:
    node-version: 20
    registry-url: https://npm.pkg.github.com  # GitHub's proxy
```

**Benefits**:
- Faster downloads within GitHub network
- Reduced external network calls
- Better reliability

---

## 8. Resource Management

### 8.1 Runner Size Selection

**Good - Use larger runners for heavy builds:**
```yaml
jobs:
  build-large:
    runs-on: ubuntu-latest-8-cores  # For compute-intensive builds
    steps:
      - run: cargo build --release -j 8

  build-small:
    runs-on: ubuntu-latest  # 2 cores sufficient
    steps:
      - run: npm run lint
```

**Cost/Performance Trade-off**:
- Larger runners cost more but finish faster
- Calculate total cost: (runner cost per minute) × (build time)
- Often larger runners are cheaper overall

### 8.2 Timeout Configuration

**Good - Set appropriate timeouts:**
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 10  # Fail fast if stuck
    steps:
      - run: npm run build
        timeout-minutes: 5  # Per-step timeout
```

**Benefits**:
- Prevents stuck jobs consuming CI minutes
- Faster feedback on hung processes
- Clear failure signals

---

## 9. Performance Monitoring

### 9.1 Build Time Tracking

**Good - Track and alert on slow builds:**
```yaml
- name: Build with timing
  run: |
    START_TIME=$(date +%s)
    npm run build
    END_TIME=$(date +%s)
    BUILD_TIME=$((END_TIME - START_TIME))
    echo "Build took ${BUILD_TIME}s"

    if [ $BUILD_TIME -gt 300 ]; then
      echo "::warning::Build took longer than 5 minutes"
    fi
```

**Benefits**:
- Visibility into build performance regression
- Alerts when builds slow down
- Data for optimization decisions

### 9.2 Cache Hit Rate Monitoring

**Good - Track cache effectiveness:**
```yaml
- uses: actions/cache@v4
  id: cache
  with:
    path: node_modules
    key: ${{ hashFiles('package-lock.json') }}

- name: Report cache status
  run: |
    if [ "${{ steps.cache.outputs.cache-hit }}" == "true" ]; then
      echo "✅ Cache hit - saved $(date +%s) seconds"
    else
      echo "❌ Cache miss - rebuilding dependencies"
    fi
```

---

## 10. Performance Checklist

Before merging CI/CD changes:

- [ ] All dependencies cached with proper keys
- [ ] Independent jobs run in parallel
- [ ] Artifacts compressed and retention limited
- [ ] Path filters configured for incremental builds
- [ ] Workflow triggers optimized (paths, branches)
- [ ] Docker layers ordered least-to-most changing
- [ ] Shallow clones used where possible
- [ ] Appropriate runner sizes selected
- [ ] Timeouts configured to fail fast
- [ ] Build time monitoring in place

**Target Metrics**:
- PR builds: < 5 minutes
- Main branch builds: < 10 minutes
- Release builds: < 20 minutes
- Cache hit rate: > 80%

---

## References

- [GitHub Actions Caching](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)
- [Turborepo CI Guide](https://turbo.build/repo/docs/ci)
- [Docker Build Cache](https://docs.docker.com/build/cache/)
- [Actions Cache Best Practices](https://docs.github.com/en/actions/guides/caching-dependencies-to-speed-up-workflows)
