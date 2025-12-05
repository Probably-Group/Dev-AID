# CI/CD Testing Guide

This document covers comprehensive testing strategies for CI/CD pipelines, including workflow validation, security testing, and integration testing.

---

## 1. Workflow Validation Testing

### 1.1 YAML Syntax Validation

**Test workflow YAML syntax on every change:**
```yaml
name: Validate Workflows

on:
  pull_request:
    paths:
      - '.github/workflows/**'
  push:
    paths:
      - '.github/workflows/**'

jobs:
  validate-yaml:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install yamllint
        run: pip install yamllint

      - name: Validate YAML syntax
        run: yamllint .github/workflows/

      - name: Check for valid YAML structure
        run: |
          for file in .github/workflows/*.yml .github/workflows/*.yaml; do
            if [ -f "$file" ]; then
              python -c "import yaml; yaml.safe_load(open('$file'))"
            fi
          done
```

**yamllint configuration (.yamllint):**
```yaml
extends: default

rules:
  line-length:
    max: 120
    level: warning
  indentation:
    spaces: 2
  comments:
    min-spaces-from-content: 1
```

### 1.2 Action Linting with actionlint

**Comprehensive workflow linting:**
```yaml
- name: Install actionlint
  run: |
    bash <(curl https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash)
    sudo mv actionlint /usr/local/bin/

- name: Lint workflows
  run: actionlint -color -verbose

- name: Check for common issues
  run: |
    actionlint -format '{{json .}}' | jq '.[] | select(.severity == "error")'
```

**actionlint catches:**
- Invalid action references
- Type mismatches in expressions
- Deprecated syntax
- Missing required inputs
- Invalid event triggers

---

## 2. Security Compliance Testing

### 2.1 Permission Validation

**Test that all workflows have explicit permissions:**
```yaml
test-security-compliance:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4

    - name: Check permissions are explicit
      run: |
        EXIT_CODE=0
        for f in .github/workflows/*.yml .github/workflows/*.yaml; do
          if [ -f "$f" ]; then
            if ! grep -q "^permissions:" "$f"; then
              echo "❌ FAIL: $f missing explicit permissions"
              EXIT_CODE=1
            else
              echo "✅ PASS: $f has explicit permissions"
            fi
          fi
        done
        exit $EXIT_CODE

    - name: Check for write-all permissions
      run: |
        if grep -r "permissions:.*write-all" .github/workflows/; then
          echo "❌ FAIL: Found dangerous write-all permissions"
          exit 1
        fi
        echo "✅ PASS: No write-all permissions found"
```

### 2.2 Action Pinning Validation

**Test that all actions are pinned by SHA:**
```yaml
- name: Check actions are SHA-pinned
  run: |
    EXIT_CODE=0

    # Find all uses: statements
    grep -rh "uses:" .github/workflows/ | while read -r line; do
      # Extract action reference
      ACTION=$(echo "$line" | sed 's/.*uses:[[:space:]]*//' | tr -d '"' | tr -d "'")

      # Skip local actions and Docker images
      if [[ "$ACTION" == ./* ]] || [[ "$ACTION" == docker://* ]]; then
        continue
      fi

      # Check if pinned by SHA (40 hex characters)
      if ! echo "$ACTION" | grep -qE '@[a-f0-9]{40}'; then
        echo "❌ FAIL: Unpinned action: $ACTION"
        EXIT_CODE=1
      fi
    done

    if [ $EXIT_CODE -eq 0 ]; then
      echo "✅ PASS: All actions are SHA-pinned"
    fi
    exit $EXIT_CODE
```

### 2.3 Secret Exposure Detection

**Test that secrets are not exposed in logs:**
```yaml
- name: Check for secret exposure
  run: |
    EXIT_CODE=0

    # Check for secrets in echo statements
    if grep -r 'echo.*secrets\.' .github/workflows/; then
      echo "❌ FAIL: Found secrets in echo statements"
      EXIT_CODE=1
    fi

    # Check for secrets in command line arguments
    if grep -rE 'run:.*\$\{\{\s*secrets\.' .github/workflows/; then
      echo "❌ FAIL: Found secrets in run commands"
      EXIT_CODE=1
    fi

    # Check for secrets in script blocks
    if grep -rE 'script:.*secrets\.' .github/workflows/; then
      echo "❌ FAIL: Found secrets in script blocks"
      EXIT_CODE=1
    fi

    if [ $EXIT_CODE -eq 0 ]; then
      echo "✅ PASS: No secret exposure detected"
    fi
    exit $EXIT_CODE
```

### 2.4 pull_request_target Safety Check

**Test for unsafe pull_request_target usage:**
```yaml
- name: Check pull_request_target safety
  run: |
    EXIT_CODE=0

    for f in .github/workflows/*.yml .github/workflows/*.yaml; do
      if [ -f "$f" ] && grep -q "pull_request_target:" "$f"; then
        echo "⚠️  Found pull_request_target in $f"

        # Check for dangerous patterns
        if grep -A 10 "pull_request_target:" "$f" | grep -q "github.event.pull_request.head"; then
          echo "❌ FAIL: $f checks out PR code with pull_request_target"
          EXIT_CODE=1
        fi

        if grep -A 20 "pull_request_target:" "$f" | grep -q "secrets\."; then
          echo "⚠️  WARNING: $f uses secrets with pull_request_target"
        fi
      fi
    done

    exit $EXIT_CODE
```

---

## 3. Integration Testing

### 3.1 Local Testing with act

**Test workflows locally before pushing:**
```bash
# Install act
brew install act  # macOS
# or: curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Test workflow locally
act push

# Test specific job
act -j build

# Test with secrets
act --secret-file .secrets

# Dry run to see what would execute
act -n
```

**Example .secrets file (DO NOT COMMIT):**
```
GITHUB_TOKEN=ghp_xxx
NPM_TOKEN=npm_xxx
```

### 3.2 Workflow Testing in Pull Requests

**Dedicated PR workflow for testing changes:**
```yaml
name: Test Workflow Changes

on:
  pull_request:
    paths:
      - '.github/workflows/**'

jobs:
  test-syntax:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: yamllint .github/workflows/

  test-security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run security checks
        run: |
          # Permission checks
          bash .github/scripts/check-permissions.sh
          # Action pinning checks
          bash .github/scripts/check-pinning.sh

  test-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Test workflow would succeed
        run: |
          # Simulate workflow execution
          echo "Testing build workflow..."
          # Run build commands that workflow would run
```

---

## 4. Performance Testing

### 4.1 Build Time Benchmarking

**Track build time changes in PRs:**
```yaml
name: Performance Testing

on:
  pull_request:
    paths:
      - '.github/workflows/**'
      - 'src/**'

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Need history for comparison

      - name: Benchmark current branch
        id: current
        run: |
          START=$(date +%s)
          npm ci && npm run build
          END=$(date +%s)
          DURATION=$((END - START))
          echo "duration=$DURATION" >> $GITHUB_OUTPUT

      - name: Checkout base branch
        run: git checkout ${{ github.base_ref }}

      - name: Benchmark base branch
        id: base
        run: |
          START=$(date +%s)
          npm ci && npm run build
          END=$(date +%s)
          DURATION=$((END - START))
          echo "duration=$DURATION" >> $GITHUB_OUTPUT

      - name: Compare results
        run: |
          CURRENT=${{ steps.current.outputs.duration }}
          BASE=${{ steps.base.outputs.duration }}
          DIFF=$((CURRENT - BASE))
          PERCENT=$(( (DIFF * 100) / BASE ))

          echo "📊 Build Time Comparison"
          echo "Base: ${BASE}s"
          echo "Current: ${CURRENT}s"
          echo "Difference: ${DIFF}s (${PERCENT}%)"

          if [ $PERCENT -gt 10 ]; then
            echo "::warning::Build time increased by more than 10%"
          fi
```

### 4.2 Cache Hit Rate Testing

**Monitor cache effectiveness:**
```yaml
- name: Test cache effectiveness
  run: |
    # First run - should miss cache
    CACHE_HIT_1="${{ steps.cache.outputs.cache-hit }}"

    # Simulate second run
    # ...run build...

    CACHE_HIT_2="${{ steps.cache.outputs.cache-hit }}"

    if [ "$CACHE_HIT_2" == "true" ]; then
      echo "✅ Cache working correctly"
    else
      echo "❌ Cache not working as expected"
      exit 1
    fi
```

---

## 5. Test-Driven Workflow Development

### 5.1 Write Test First

**Before creating a workflow, write tests:**

**Test file (.github/tests/test-build-workflow.sh):**
```bash
#!/bin/bash
set -e

echo "Testing build workflow requirements..."

# Test 1: Workflow must exist
test -f .github/workflows/build.yml || {
  echo "FAIL: build.yml does not exist"
  exit 1
}
echo "✅ Workflow file exists"

# Test 2: Workflow must have explicit permissions
grep -q "^permissions:" .github/workflows/build.yml || {
  echo "FAIL: Missing explicit permissions"
  exit 1
}
echo "✅ Explicit permissions set"

# Test 3: All actions must be SHA-pinned
! grep -E 'uses:.*@v[0-9]' .github/workflows/build.yml || {
  echo "FAIL: Found unpinned actions"
  exit 1
}
echo "✅ All actions SHA-pinned"

# Test 4: Build job must exist
grep -q "jobs:.*build:" .github/workflows/build.yml || {
  echo "FAIL: Build job not found"
  exit 1
}
echo "✅ Build job exists"

echo "All tests passed!"
```

**Run test before implementing workflow:**
```bash
bash .github/tests/test-build-workflow.sh
# Tests fail - workflow doesn't exist yet
```

### 5.2 Implement Workflow

**Create minimal workflow to pass tests:**
```yaml
name: Build

on: [push]

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@8ade135a41bc03ea155e62e844d188df1ea18608  # v4.1.0
      - run: npm ci && npm run build
```

### 5.3 Verify Tests Pass

```bash
bash .github/tests/test-build-workflow.sh
# ✅ All tests pass
```

---

## 6. Continuous Testing

### 6.1 Automated Workflow Testing

**Master test workflow that runs on every change:**
```yaml
name: CI/CD Tests

on:
  push:
  pull_request:
  schedule:
    - cron: '0 0 * * 0'  # Weekly validation

jobs:
  validate-all-workflows:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install tools
        run: |
          pip install yamllint
          bash <(curl https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash)
          sudo mv actionlint /usr/local/bin/

      - name: YAML validation
        run: yamllint .github/workflows/

      - name: Workflow linting
        run: actionlint

      - name: Security compliance
        run: bash .github/scripts/security-checks.sh

      - name: Performance benchmarks
        run: bash .github/scripts/benchmark.sh

      - name: Integration tests
        run: bash .github/tests/integration-tests.sh
```

---

## 7. Regression Testing

### 7.1 Test for Known Issues

**Prevent regression of previously fixed issues:**
```yaml
- name: Regression tests
  run: |
    echo "Testing for known regressions..."

    # Regression 1: CVE-2023-49291 - Unpinned actions
    ! grep -rE 'uses:.*@v[0-9]' .github/workflows/ || {
      echo "REGRESSION: Unpinned actions found (CVE-2023-49291)"
      exit 1
    }

    # Regression 2: Secret exposure in logs
    ! grep -r 'echo.*secrets\.' .github/workflows/ || {
      echo "REGRESSION: Secret exposure detected"
      exit 1
    }

    # Regression 3: Missing permissions
    for f in .github/workflows/*.yml; do
      grep -q "^permissions:" "$f" || {
        echo "REGRESSION: $f missing permissions"
        exit 1
      }
    done

    echo "✅ No regressions detected"
```

---

## 8. Security Testing

### 8.1 Dependency Scanning

**Test for vulnerable dependencies:**
```yaml
- name: Security scanning
  uses: github/dependency-review-action@v3
  if: github.event_name == 'pull_request'

- name: SAST scanning
  uses: github/codeql-action/analyze@v2

- name: Secret scanning
  uses: trufflesecurity/trufflehog@main
  with:
    path: .github/workflows/
```

### 8.2 Supply Chain Verification

**Test action provenance:**
```yaml
- name: Verify action signatures
  run: |
    # Check if critical actions are from verified publishers
    grep -h "uses:" .github/workflows/*.yml | while read -r line; do
      ACTION=$(echo "$line" | sed 's/.*uses:[[:space:]]*//')

      # Verify trusted organizations
      if [[ "$ACTION" == actions/* ]] || [[ "$ACTION" == github/* ]]; then
        echo "✅ Verified: $ACTION"
      else
        echo "⚠️  Unverified: $ACTION - Review required"
      fi
    done
```

---

## 9. Testing Checklist

Before merging workflow changes:

**Syntax & Structure**:
- [ ] YAML syntax validated with yamllint
- [ ] Workflows linted with actionlint
- [ ] All jobs have explicit names

**Security**:
- [ ] All workflows have explicit permissions
- [ ] No `permissions: write-all`
- [ ] All actions pinned by SHA
- [ ] No secrets in command line arguments
- [ ] No unsafe `pull_request_target` usage
- [ ] Secret scanning passed

**Functionality**:
- [ ] Workflow triggers are appropriate
- [ ] Dependencies cached properly
- [ ] Jobs parallelized where possible
- [ ] Artifacts handled correctly

**Performance**:
- [ ] Build time benchmarks acceptable
- [ ] Cache hit rate monitored
- [ ] No unnecessary workflow runs

**Testing**:
- [ ] Local testing with `act` completed
- [ ] Integration tests passed
- [ ] Regression tests passed
- [ ] Security scans completed

---

## 10. Test Automation Script

**Complete test script (.github/scripts/test-workflows.sh):**
```bash
#!/bin/bash
set -e

echo "🧪 Running CI/CD Workflow Tests"
echo "================================"

# 1. YAML Syntax
echo "1️⃣ Validating YAML syntax..."
yamllint .github/workflows/ || {
  echo "❌ YAML validation failed"
  exit 1
}
echo "✅ YAML syntax valid"

# 2. Workflow Linting
echo "2️⃣ Linting workflows..."
actionlint -color || {
  echo "❌ Workflow linting failed"
  exit 1
}
echo "✅ Workflows linted successfully"

# 3. Security Checks
echo "3️⃣ Running security checks..."

# Check permissions
for f in .github/workflows/*.yml; do
  grep -q "^permissions:" "$f" || {
    echo "❌ $f missing explicit permissions"
    exit 1
  }
done
echo "✅ All workflows have explicit permissions"

# Check action pinning
if grep -rE 'uses:.*@v[0-9]' .github/workflows/; then
  echo "❌ Found unpinned actions"
  exit 1
fi
echo "✅ All actions SHA-pinned"

# Check secret exposure
if grep -r 'echo.*secrets\.' .github/workflows/; then
  echo "❌ Found secret exposure"
  exit 1
fi
echo "✅ No secret exposure detected"

# 4. Test Coverage
echo "4️⃣ Checking test coverage..."
# Verify all critical workflows are tested
REQUIRED_WORKFLOWS=("build.yml" "test.yml" "release.yml")
for workflow in "${REQUIRED_WORKFLOWS[@]}"; do
  if [ ! -f ".github/workflows/$workflow" ]; then
    echo "⚠️  Warning: $workflow not found"
  fi
done

echo ""
echo "✅ All tests passed!"
echo "================================"
```

**Usage:**
```bash
# Make executable
chmod +x .github/scripts/test-workflows.sh

# Run tests
.github/scripts/test-workflows.sh
```

---

## 11. Continuous Improvement

### 11.1 Test Metrics

Track test effectiveness over time:
- Workflow failure rate
- Security check pass rate
- Performance benchmark trends
- Cache hit rates

### 11.2 Test Maintenance

Regularly update tests for:
- New security threats
- New GitHub Actions features
- Updated best practices
- Tool version updates

---

## References

- [GitHub Actions Testing Best Practices](https://docs.github.com/en/actions/guides/about-continuous-integration)
- [actionlint Documentation](https://github.com/rhysd/actionlint)
- [act - Local GitHub Actions Testing](https://github.com/nektos/act)
- [yamllint Documentation](https://yamllint.readthedocs.io/)
