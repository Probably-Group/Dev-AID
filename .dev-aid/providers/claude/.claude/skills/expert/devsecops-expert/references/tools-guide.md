# DevSecOps Tools and Performance Guide

This document provides performance optimization patterns and tool-specific configurations for DevSecOps implementations.

## Performance Optimization Patterns

### Pattern 1: Incremental Scanning

Scan only changed files instead of entire codebase to reduce CI time.

**Bad - Full scan on every commit**:
```yaml
# ❌ Scans entire codebase every time (slow: ~5-10 minutes)
sast:
  steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0  # Full history
    - run: semgrep --config auto .  # Scans everything
```

**Good - Scan only changed files**:
```yaml
# ✅ Incremental scan of changed files only (fast: ~30 seconds)
sast:
  steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 2  # Current + parent only

    - name: Get changed files
      id: changed
      run: |
        echo "files=$(git diff --name-only HEAD~1 | grep -E '\.(py|js|ts)$' | tr '\n' ' ')" >> $GITHUB_OUTPUT

    - name: Scan changed files only
      if: steps.changed.outputs.files != ''
      run: semgrep --config auto ${{ steps.changed.outputs.files }}
```

**Performance Impact**: 90% faster for typical PRs changing <10 files

---

### Pattern 2: Parallel Analysis

Run all security gates in parallel instead of sequentially.

**Bad - Sequential security gates**:
```yaml
# ❌ Each job waits for previous (slow: 15 minutes total)
jobs:
  sast:
    runs-on: ubuntu-latest
    steps:
      - run: semgrep --config auto  # 5 min

  sca:
    needs: sast  # Waits for SAST
    runs-on: ubuntu-latest
    steps:
      - run: npm audit  # 3 min

  container:
    needs: sca   # Waits for SCA
    runs-on: ubuntu-latest
    steps:
      - run: trivy image app:test  # 7 min
```

**Good - Parallel execution**:
```yaml
# ✅ All scans run simultaneously (fast: 7 minutes total)
jobs:
  sast:
    runs-on: ubuntu-latest
    steps:
      - run: semgrep --config auto  # 5 min

  sca:
    runs-on: ubuntu-latest  # No dependency - runs in parallel
    steps:
      - run: npm audit  # 3 min

  container:
    runs-on: ubuntu-latest  # No dependency - runs in parallel
    steps:
      - run: trivy image app:test  # 7 min (slowest)

  # Only deploy needs all gates
  deploy:
    needs: [sast, sca, container]
    runs-on: ubuntu-latest
    steps:
      - run: kubectl apply -f k8s/
```

**Performance Impact**: 50% faster by eliminating sequential waits

---

### Pattern 3: Caching Scan Results

Cache vulnerability databases and dependencies between CI runs.

**Bad - No caching, downloads every time**:
```yaml
# ❌ Downloads vulnerability DB on every run (~2 min overhead)
container-scan:
  steps:
    - name: Scan image
      run: trivy image app:test  # Downloads DB each time
```

**Good - Cache vulnerability databases**:
```yaml
# ✅ Cache Trivy DB between runs (30 seconds overhead)
container-scan:
  steps:
    - name: Cache Trivy DB
      uses: actions/cache@v4
      with:
        path: ~/.cache/trivy
        key: trivy-db-${{ github.run_id }}
        restore-keys: trivy-db-

    - name: Scan image with cached DB
      run: trivy image --cache-dir ~/.cache/trivy app:test
```

**Advanced Caching Strategy**:
```yaml
# ✅ Multi-level caching
security-scan:
  steps:
    # Cache 1: NPM packages
    - uses: actions/cache@v4
      with:
        path: ~/.npm
        key: npm-${{ hashFiles('**/package-lock.json') }}
        restore-keys: npm-

    # Cache 2: Trivy DB
    - uses: actions/cache@v4
      with:
        path: ~/.cache/trivy
        key: trivy-db-${{ github.run_id }}
        restore-keys: trivy-db-

    # Cache 3: Semgrep rules
    - uses: actions/cache@v4
      with:
        path: ~/.semgrep
        key: semgrep-rules-${{ github.run_id }}
        restore-keys: semgrep-rules-

    # Cache 4: Docker layers
    - uses: docker/setup-buildx-action@v3
    - uses: actions/cache@v4
      with:
        path: /tmp/.buildx-cache
        key: buildx-${{ github.sha }}
        restore-keys: buildx-
```

**Performance Impact**: 70% faster with comprehensive caching

---

### Pattern 4: Targeted Audits

Only scan when relevant files change.

**Bad - Scan everything always**:
```yaml
# ❌ Full IaC scan even for non-IaC changes
iac-scan:
  steps:
    - run: checkov --directory terraform/  # Always runs full scan
```

**Good - Conditional scanning based on changes**:
```yaml
# ✅ Only scan when relevant files change
iac-scan:
  if: |
    contains(github.event.pull_request.changed_files, 'terraform/') ||
    contains(github.event.pull_request.changed_files, 'k8s/')
  steps:
    - name: Get changed IaC files
      id: iac-changes
      run: |
        CHANGED=$(git diff --name-only origin/main | grep -E '^(terraform|k8s)/')
        echo "files=$CHANGED" >> $GITHUB_OUTPUT

    - name: Scan changed IaC only
      if: steps.iac-changes.outputs.files != ''
      run: |
        for file in ${{ steps.iac-changes.outputs.files }}; do
          checkov --file "$file"
        done
```

**Performance Impact**: Skip unnecessary scans, save 3-5 minutes when no IaC changes

---

### Pattern 5: Layer Caching for Container Builds

Use Docker BuildKit cache modes for maximum build speed.

**Bad - Rebuild entire image**:
```yaml
# ❌ No layer caching (~10 min builds)
build:
  steps:
    - run: docker build -t app .
```

**Good - Cache Docker layers**:
```yaml
# ✅ Cache layers for faster builds (~2 min with cache)
build:
  steps:
    - uses: docker/setup-buildx-action@v3

    - name: Cache Docker layers
      uses: actions/cache@v4
      with:
        path: /tmp/.buildx-cache
        key: buildx-${{ github.sha }}
        restore-keys: buildx-

    - name: Build with cache
      uses: docker/build-push-action@v5
      with:
        context: .
        cache-from: type=local,src=/tmp/.buildx-cache
        cache-to: type=local,dest=/tmp/.buildx-cache-new,mode=max
        tags: app:${{ github.sha }}

    # Prevent cache from growing indefinitely
    - name: Rotate cache
      run: |
        rm -rf /tmp/.buildx-cache
        mv /tmp/.buildx-cache-new /tmp/.buildx-cache
```

**Advanced Registry Cache**:
```yaml
# ✅ Use registry as cache backend (shared across runners)
build:
  steps:
    - uses: docker/setup-buildx-action@v3

    - name: Build with registry cache
      uses: docker/build-push-action@v5
      with:
        context: .
        cache-from: type=registry,ref=ghcr.io/${{ github.repository }}:cache
        cache-to: type=registry,ref=ghcr.io/${{ github.repository }}:cache,mode=max
        tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
        push: true
```

**Performance Impact**: 80% faster builds with cache hits

---

## Tool-Specific Configurations

### SAST: Semgrep

**Optimized Semgrep Configuration**:
```yaml
# .semgrep/config.yml
rules:
  - id: security-audit
    mode: auto
    paths:
      include:
        - src/
        - lib/
      exclude:
        - "*.test.js"
        - "*.spec.ts"
        - node_modules/
        - vendor/

# Performance tuning
max-memory: 2048
timeout: 30
jobs: 4  # Parallel jobs
```

**CI Integration**:
```yaml
# .github/workflows/semgrep.yml
name: Semgrep SAST

on:
  pull_request:
    branches: [main]

jobs:
  semgrep:
    runs-on: ubuntu-latest
    container:
      image: semgrep/semgrep
    steps:
      - uses: actions/checkout@v4

      - name: Run Semgrep
        run: |
          semgrep \
            --config p/security-audit \
            --config p/secrets \
            --exclude 'test/' \
            --exclude '*.test.*' \
            --json \
            --output semgrep-results.json \
            --metrics off \
            --error

      - uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: semgrep-results.json
```

**Performance Tips**:
- Use `--metrics off` to disable telemetry
- Exclude test files and dependencies
- Use `--jobs` for parallel execution
- Cache `.semgrep` directory

---

### SCA: Trivy

**Optimized Trivy Configuration**:
```yaml
# trivy.yaml
scan:
  security-checks:
    - vuln
    - config
    - secret
  severity:
    - CRITICAL
    - HIGH
  skip-dirs:
    - node_modules
    - vendor
    - test
  timeout: 5m

cache:
  dir: ~/.cache/trivy

db:
  skip-update: false
  repository: ghcr.io/aquasecurity/trivy-db
```

**CI Integration**:
```yaml
# .github/workflows/trivy.yml
name: Trivy Container Scan

on: [push]

jobs:
  trivy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Cache Trivy DB
      - uses: actions/cache@v4
        with:
          path: ~/.cache/trivy
          key: trivy-db-${{ github.run_id }}
          restore-keys: trivy-db-

      - name: Build image
        run: docker build -t app:${{ github.sha }} .

      - name: Run Trivy filesystem scan
        uses: aquasecurity/trivy-action@0.16.1
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-fs-results.sarif'

      - name: Run Trivy image scan
        uses: aquasecurity/trivy-action@0.16.1
        with:
          image-ref: app:${{ github.sha }}
          format: 'sarif'
          output: 'trivy-image-results.sarif'
          severity: 'CRITICAL,HIGH'
          exit-code: '1'

      - name: Upload to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: 'trivy-image-results.sarif'
```

**Performance Tips**:
- Cache Trivy database (~200MB)
- Use `--skip-update` for faster scans when cache is fresh
- Scan filesystem before building image
- Use `--severity HIGH,CRITICAL` to reduce noise

---

### IaC Scanning: Checkov

**Optimized Checkov Configuration**:
```yaml
# .checkov.yml
framework:
  - terraform
  - kubernetes
  - dockerfile

skip-check:
  - CKV_DOCKER_2  # Example: Skip specific checks if needed

output:
  - cli
  - sarif

download-external-modules: true

quiet: false
compact: true

hard-fail-on:
  - HIGH
  - CRITICAL
```

**CI Integration**:
```yaml
# .gitlab-ci.yml
checkov-scan:
  stage: security-scan
  image: bridgecrew/checkov:latest
  script:
    - checkov \
        --directory terraform/ \
        --framework terraform \
        --config-file .checkov.yml \
        --output cli \
        --output sarif \
        --output-file-path reports/ \
        --hard-fail-on HIGH,CRITICAL
  artifacts:
    reports:
      sast: reports/results_sarif.sarif
    paths:
      - reports/
```

**Performance Tips**:
- Use `--compact` for less verbose output
- Skip low-severity checks
- Cache external modules
- Run only relevant frameworks

---

### Secret Scanning: TruffleHog

**Optimized TruffleHog Configuration**:
```yaml
# .trufflehog.yml
rules:
  - id: aws-access-key
    regex: 'AKIA[0-9A-Z]{16}'
    description: AWS Access Key
    severity: high

  - id: private-key
    regex: '-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----'
    description: Private Key
    severity: critical

exclude_paths:
  - node_modules/
  - vendor/
  - '*.test.js'
```

**CI Integration**:
```yaml
# .github/workflows/secret-scan.yml
name: Secret Scanning

on:
  push:
  pull_request:

jobs:
  trufflehog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for comprehensive scan

      - name: TruffleHog Scan
        uses: trufflesecurity/trufflehog@v3.63.0
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
          extra_args: |
            --fail
            --json
            --no-verification
            --exclude-paths .trufflehog-exclude
```

**Performance Tips**:
- Use `--no-verification` for faster scans (verify separately)
- Scan only changed commits in PRs
- Exclude test fixtures and dependencies
- Use verified secrets detection when possible

---

### Container Signing: Cosign

**Optimized Cosign Workflow**:
```yaml
# .github/workflows/sign-image.yml
name: Build, Sign, and Verify

on:
  push:
    tags: ['v*']

permissions:
  id-token: write
  packages: write
  contents: read

jobs:
  build-and-sign:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: docker/setup-buildx-action@v3

      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        id: build
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.ref_name }}
          cache-from: type=registry,ref=ghcr.io/${{ github.repository }}:cache
          cache-to: type=registry,ref=ghcr.io/${{ github.repository }}:cache,mode=max

      - uses: sigstore/cosign-installer@v3

      - name: Sign image with keyless signing
        run: |
          cosign sign --yes \
            ghcr.io/${{ github.repository }}@${{ steps.build.outputs.digest }}

      - name: Verify signature
        run: |
          cosign verify \
            --certificate-identity https://github.com/${{ github.repository }}/.github/workflows/sign-image.yml@${{ github.ref }} \
            --certificate-oidc-issuer https://token.actions.githubusercontent.com \
            ghcr.io/${{ github.repository }}@${{ steps.build.outputs.digest }}
```

**Performance Tips**:
- Use keyless signing (no key management overhead)
- Sign by digest, not tag
- Verify signatures in separate job
- Cache cosign binary

---

## Performance Benchmarks

### Typical CI Pipeline Times

| Stage | Without Optimization | With Optimization | Improvement |
|-------|---------------------|-------------------|-------------|
| **Checkout** | 30s | 15s (shallow clone) | 50% |
| **SAST** | 5m | 30s (incremental) | 90% |
| **SCA** | 3m | 1m (cached) | 67% |
| **Container Build** | 10m | 2m (layer cache) | 80% |
| **Container Scan** | 7m | 3m (DB cache) | 57% |
| **IaC Scan** | 4m | 1m (conditional) | 75% |
| **Secret Scan** | 2m | 30s (optimized) | 75% |
| **Deploy** | 1m | 1m | 0% |
| **TOTAL** | **32m** | **9m** | **72%** |

---

## Best Practices Summary

### Speed Optimizations
1. ✅ Run security gates in parallel
2. ✅ Cache vulnerability databases
3. ✅ Scan only changed files
4. ✅ Use incremental analysis
5. ✅ Implement layer caching
6. ✅ Skip scans when not needed

### Resource Optimizations
1. ✅ Use minimal container images
2. ✅ Limit CI job concurrency
3. ✅ Reuse build artifacts
4. ✅ Clean up old cache entries
5. ✅ Use self-hosted runners for heavy workloads

### Reliability Improvements
1. ✅ Retry on transient failures
2. ✅ Set appropriate timeouts
3. ✅ Monitor scan success rates
4. ✅ Alert on performance degradation
5. ✅ Maintain fallback strategies

---

## Monitoring and Metrics

### Key Metrics to Track

```yaml
# Prometheus metrics for security pipeline
security_scan_duration_seconds{stage="sast"} 30
security_scan_duration_seconds{stage="sca"} 60
security_scan_duration_seconds{stage="container"} 180
security_scan_success_rate{stage="sast"} 0.98
security_scan_success_rate{stage="container"} 0.95
vulnerabilities_detected_total{severity="critical"} 2
vulnerabilities_detected_total{severity="high"} 15
```

### Alerting Rules

```yaml
# Alert if scans take too long
groups:
  - name: security_pipeline
    rules:
      - alert: SecurityScanSlow
        expr: security_scan_duration_seconds > 300
        annotations:
          summary: "Security scan taking longer than 5 minutes"

      - alert: SecurityScanFailureRate
        expr: security_scan_success_rate < 0.90
        annotations:
          summary: "Security scan failure rate above 10%"
```

---

## Troubleshooting

### Problem: Slow SAST scans

**Solution**:
- Enable incremental scanning
- Exclude test files
- Use parallel jobs
- Cache Semgrep rules

### Problem: Trivy DB download fails

**Solution**:
- Use cache for Trivy DB
- Mirror Trivy DB internally
- Increase timeout
- Check network connectivity

### Problem: Out of memory during build

**Solution**:
- Use multi-stage builds
- Limit parallel jobs
- Increase runner memory
- Clean up intermediate layers

### Problem: Cache misses

**Solution**:
- Use consistent cache keys
- Include relevant files in hash
- Set appropriate restore-keys
- Monitor cache hit rates
