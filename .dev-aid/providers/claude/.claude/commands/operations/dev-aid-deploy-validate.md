---
name: aid-deploy-validate
description: Pre-deployment validation with tests, security checks, and environment readiness verification
category: operations
author: Dev-AID Team (adapted from Tresor)
version: 1.0.0
---

# Deploy Validation - Pre-Deployment Safety Checks

Perform comprehensive pre-deployment validation to prevent production outages.

## Overview

This command validates deployment readiness:
- **Phase 1**: Test suite execution
- **Phase 2**: Configuration safety review
- **Phase 3**: Security pre-deployment check
- **Phase 4**: Build validation
- **Phase 5**: Go/No-Go decision

## Dev-AID Integration

### Memory Bank Updates
This command updates:
- `.dev-aid/memory-bank/activeContext.md` - Deployment status and readiness

### Report Output
Reports are saved to:
- `.dev-aid/reports/operations/deploy-[timestamp]/`

### Multi-Provider Support
Works with all enabled providers (Claude, Gemini, OpenAI).

---

## Execution Steps

### Phase 1: Run Test Suite

Verify all tests pass before deployment:

```bash
echo "=== Running Test Suite ==="
TIMESTAMP=$(date +%Y-%m-%d-%H%M%S)
REPORT_DIR=".dev-aid/reports/operations/deploy-${TIMESTAMP}"
mkdir -p "$REPORT_DIR"

# Initialize test results
TESTS_PASSED=true

# Node.js Tests
if [ -f "package.json" ]; then
  echo "Running Node.js tests..."

  if npm test > "$REPORT_DIR/test-results.txt" 2>&1; then
    echo "✅ Node.js tests PASSED"
  else
    echo "❌ Node.js tests FAILED"
    TESTS_PASSED=false
    cat "$REPORT_DIR/test-results.txt"
  fi
fi

# Python Tests
if [ -f "pytest.ini" ] || [ -f "setup.py" ]; then
  echo "Running Python tests..."

  if pytest > "$REPORT_DIR/pytest-results.txt" 2>&1; then
    echo "✅ Python tests PASSED"
  else
    echo "❌ Python tests FAILED"
    TESTS_PASSED=false
    cat "$REPORT_DIR/pytest-results.txt"
  fi
fi

# Go Tests
if [ -f "go.mod" ]; then
  echo "Running Go tests..."

  if go test ./... > "$REPORT_DIR/go-test-results.txt" 2>&1; then
    echo "✅ Go tests PASSED"
  else
    echo "❌ Go tests FAILED"
    TESTS_PASSED=false
    cat "$REPORT_DIR/go-test-results.txt"
  fi
fi

# Rust Tests
if [ -f "Cargo.toml" ]; then
  echo "Running Rust tests..."

  if cargo test > "$REPORT_DIR/cargo-test-results.txt" 2>&1; then
    echo "✅ Rust tests PASSED"
  else
    echo "❌ Rust tests FAILED"
    TESTS_PASSED=false
    cat "$REPORT_DIR/cargo-test-results.txt"
  fi
fi

if [ "$TESTS_PASSED" = false ]; then
  echo ""
  echo "❌ DEPLOYMENT BLOCKED: Tests failed"
  echo "Fix failing tests before deploying."
  exit 1
fi
```

### Phase 2: Configuration Safety Review

Review configuration files for production safety:

```bash
echo ""
echo "=== Configuration Safety Review ==="
CONFIG_SAFE=true

# Check for hardcoded secrets in .env files
if [ -f ".env" ] || [ -f ".env.production" ]; then
  echo "Checking environment files..."

  # Check for localhost in production config
  if grep -q "localhost" .env.production 2>/dev/null; then
    echo "❌ WARNING: 'localhost' found in .env.production"
    CONFIG_SAFE=false
  fi

  # Check for development API keys
  if grep -q "test_\|dev_\|development" .env.production 2>/dev/null; then
    echo "❌ WARNING: Development credentials in .env.production"
    CONFIG_SAFE=false
  fi

  # Check for DEBUG mode
  if grep -q "DEBUG=true\|DEBUG=1" .env.production 2>/dev/null; then
    echo "❌ WARNING: DEBUG mode enabled in production"
    CONFIG_SAFE=false
  fi
fi

# Check Docker configuration
if [ -f "Dockerfile" ]; then
  echo "Checking Dockerfile..."

  # Check if running as root
  if ! grep -q "^USER" Dockerfile; then
    echo "⚠️  WARNING: Dockerfile doesn't specify USER (running as root)"
  fi

  # Check for :latest tag
  if grep -q ":latest" Dockerfile; then
    echo "⚠️  WARNING: Using :latest tag (not reproducible)"
  fi
fi

# Check Kubernetes configuration
if [ -d "k8s" ] || [ -d "kubernetes" ]; then
  echo "Checking Kubernetes configuration..."

  # Check for resource limits
  if ! grep -rq "resources:" k8s/ kubernetes/ 2>/dev/null; then
    echo "⚠️  WARNING: No resource limits defined"
  fi

  # Check for privileged containers
  if grep -rq "privileged: true" k8s/ kubernetes/ 2>/dev/null; then
    echo "❌ ERROR: Privileged containers found"
    CONFIG_SAFE=false
  fi
fi

if [ "$CONFIG_SAFE" = false ]; then
  echo ""
  echo "❌ DEPLOYMENT BLOCKED: Configuration issues found"
  echo "Review and fix configuration before deploying."
  exit 1
fi
```

### Phase 3: Security Pre-Deployment Check

Quick security validation:

```bash
echo ""
echo "=== Security Pre-Deployment Check ==="
SECURITY_SAFE=true

# Check for hardcoded secrets in code
echo "Scanning for hardcoded secrets..."
SECRET_MATCHES=$(grep -r -E "(api[_-]?key|secret|password|token).*=.*['\"][a-zA-Z0-9]{20,}" . \
  --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist --exclude-dir=build \
  --include="*.js" --include="*.ts" --include="*.py" --include="*.go" 2>/dev/null | wc -l)

if [ "$SECRET_MATCHES" -gt 0 ]; then
  echo "❌ ERROR: Found $SECRET_MATCHES potential hardcoded secrets"
  SECURITY_SAFE=false
fi

# Run dependency security check
echo "Checking for critical vulnerabilities..."

if [ -f "package.json" ]; then
  # Check npm audit
  CRITICAL_VULNS=$(npm audit --audit-level=critical --json 2>/dev/null | \
    jq -r '.metadata.vulnerabilities.critical // 0')

  if [ "$CRITICAL_VULNS" -gt 0 ]; then
    echo "❌ ERROR: Found $CRITICAL_VULNS critical vulnerabilities"
    echo "Run: npm audit fix"
    SECURITY_SAFE=false
  fi
fi

if [ "$SECURITY_SAFE" = false ]; then
  echo ""
  echo "❌ DEPLOYMENT BLOCKED: Security issues found"
  echo "Run /dev-aid-vulnerability-scan for detailed analysis"
  exit 1
fi
```

### Phase 4: Build Validation

Verify production build succeeds:

```bash
echo ""
echo "=== Build Validation ==="
BUILD_SUCCESSFUL=true

# Node.js Build
if [ -f "package.json" ] && grep -q "\"build\":" package.json; then
  echo "Running production build..."

  if npm run build > "$REPORT_DIR/build-output.txt" 2>&1; then
    echo "✅ Production build SUCCESSFUL"

    # Check build size
    if [ -d "dist" ] || [ -d "build" ]; then
      BUILD_SIZE=$(du -sh dist build 2>/dev/null | awk '{print $1}' | head -1)
      echo "Build size: $BUILD_SIZE"
    fi
  else
    echo "❌ Production build FAILED"
    BUILD_SUCCESSFUL=false
    cat "$REPORT_DIR/build-output.txt"
  fi
fi

# Docker Build
if [ -f "Dockerfile" ]; then
  echo "Testing Docker build..."

  if docker build -t deployment-test:latest . > "$REPORT_DIR/docker-build.txt" 2>&1; then
    echo "✅ Docker build SUCCESSFUL"

    # Check image size
    IMAGE_SIZE=$(docker images deployment-test:latest --format "{{.Size}}")
    echo "Docker image size: $IMAGE_SIZE"

    # Cleanup test image
    docker rmi deployment-test:latest 2>/dev/null || true
  else
    echo "❌ Docker build FAILED"
    BUILD_SUCCESSFUL=false
    tail -50 "$REPORT_DIR/docker-build.txt"
  fi
fi

if [ "$BUILD_SUCCESSFUL" = false ]; then
  echo ""
  echo "❌ DEPLOYMENT BLOCKED: Build failed"
  echo "Fix build errors before deploying."
  exit 1
fi
```

### Phase 5: Generate Go/No-Go Decision

Create deployment decision report:

```bash
echo ""
echo "=== Deployment Decision ==="

# Calculate risk score
RISK_SCORE=0

# Test failures increase risk
if [ "$TESTS_PASSED" = false ]; then
  RISK_SCORE=$((RISK_SCORE + 100))
fi

# Config issues increase risk
if [ "$CONFIG_SAFE" = false ]; then
  RISK_SCORE=$((RISK_SCORE + 50))
fi

# Security issues increase risk
if [ "$SECURITY_SAFE" = false ]; then
  RISK_SCORE=$((RISK_SCORE + 50))
fi

# Build failures increase risk
if [ "$BUILD_SUCCESSFUL" = false ]; then
  RISK_SCORE=$((RISK_SCORE + 100))
fi

# Determine deployment decision
if [ "$RISK_SCORE" -eq 0 ]; then
  DECISION="✅ GO - Safe to deploy"
  CONFIDENCE="HIGH"
elif [ "$RISK_SCORE" -lt 50 ]; then
  DECISION="⚠️  GO WITH CAUTION - Deploy with enhanced monitoring"
  CONFIDENCE="MEDIUM"
else
  DECISION="❌ NO-GO - Fix critical issues before deploying"
  CONFIDENCE="HIGH"
fi

# Generate decision report
cat > "$REPORT_DIR/deployment-decision.md" <<EOF
# Deployment Validation Report

**Date**: $(date)
**Project**: $(basename $(pwd))
**Deploy ID**: deploy-${TIMESTAMP}

## Decision: $DECISION
**Confidence**: $CONFIDENCE
**Risk Score**: $RISK_SCORE / 100

---

## Validation Results

### ✅ Tests
- Status: $([ "$TESTS_PASSED" = true ] && echo "PASSED" || echo "FAILED")
- Test results: test-results.txt

### ✅ Configuration Safety
- Status: $([ "$CONFIG_SAFE" = true ] && echo "SAFE" || echo "ISSUES FOUND")
- No hardcoded secrets: $([ "$CONFIG_SAFE" = true ] && echo "✓" || echo "✗")
- Production config valid: $([ "$CONFIG_SAFE" = true ] && echo "✓" || echo "✗")

### ✅ Security
- Status: $([ "$SECURITY_SAFE" = true ] && echo "SAFE" || echo "ISSUES FOUND")
- Critical vulnerabilities: $([ "$SECURITY_SAFE" = true ] && echo "0" || echo ">0")
- No exposed secrets: $([ "$SECURITY_SAFE" = true ] && echo "✓" || echo "✗")

### ✅ Build
- Status: $([ "$BUILD_SUCCESSFUL" = true ] && echo "SUCCESS" || echo "FAILED")
- Production build: $([ "$BUILD_SUCCESSFUL" = true ] && echo "✓" || echo "✗")

---

## Risk Assessment

**Risk Level**: $(
  if [ "$RISK_SCORE" -eq 0 ]; then
    echo "LOW"
  elif [ "$RISK_SCORE" -lt 50 ]; then
    echo "MEDIUM"
  else
    echo "HIGH"
  fi
)

### Risk Breakdown
- Tests: $([ "$TESTS_PASSED" = false ] && echo "+100" || echo "0")
- Configuration: $([ "$CONFIG_SAFE" = false ] && echo "+50" || echo "0")
- Security: $([ "$SECURITY_SAFE" = false ] && echo "+50" || echo "0")
- Build: $([ "$BUILD_SUCCESSFUL" = false ] && echo "+100" || echo "0")

---

## Deployment Checklist

EOF

if [ "$RISK_SCORE" -eq 0 ]; then
  cat >> "$REPORT_DIR/deployment-decision.md" <<EOF
### Pre-Deployment
- [x] All tests pass
- [x] Configuration validated
- [x] No security issues
- [x] Build succeeds

### Post-Deployment Monitoring
- [ ] Monitor error rates (first 30 minutes)
- [ ] Check application logs
- [ ] Verify health endpoints
- [ ] Monitor performance metrics

### Rollback Plan
- Database: Reversible migrations
- Code: \`git revert\` or redeploy previous version
- Infrastructure: Previous deployment snapshot

EOF
else
  cat >> "$REPORT_DIR/deployment-decision.md" <<EOF
### Blocking Issues

$([ "$TESTS_PASSED" = false ] && echo "- ❌ Tests are failing - fix before deploying")
$([ "$CONFIG_SAFE" = false ] && echo "- ❌ Configuration issues - review and fix")
$([ "$SECURITY_SAFE" = false ] && echo "- ❌ Security issues - run /dev-aid-vulnerability-scan")
$([ "$BUILD_SUCCESSFUL" = false ] && echo "- ❌ Build is failing - fix build errors")

### Next Steps

1. Fix all blocking issues above
2. Re-run /dev-aid-deploy-validate
3. Only deploy when risk score = 0

EOF
fi

cat >> "$REPORT_DIR/deployment-decision.md" <<EOF
---

## Reports Generated

- Deployment Decision: deployment-decision.md
- Test Results: test-results.txt
- Build Output: build-output.txt
- All reports: $REPORT_DIR/

## Related Commands

- \`/dev-aid-audit\` - Full security audit
- \`/dev-aid-vulnerability-scan\` - Deep CVE scanning
- \`/dev-aid-health-check\` - Post-deployment validation

---

**Report Location**: $REPORT_DIR/
EOF

# Show decision
echo ""
cat "$REPORT_DIR/deployment-decision.md"

# Update memory bank
cat >> .dev-aid/memory-bank/activeContext.md <<EOF

## Deployment Validation - $(date +%Y-%m-%d)

**Deploy ID**: deploy-${TIMESTAMP}
**Decision**: $DECISION
**Risk Score**: $RISK_SCORE / 100

### Validation Results
- Tests: $([ "$TESTS_PASSED" = true ] && echo "✓ PASSED" || echo "✗ FAILED")
- Config: $([ "$CONFIG_SAFE" = true ] && echo "✓ SAFE" || echo "✗ ISSUES")
- Security: $([ "$SECURITY_SAFE" = true ] && echo "✓ SAFE" || echo "✗ ISSUES")
- Build: $([ "$BUILD_SUCCESSFUL" = true ] && echo "✓ SUCCESS" || echo "✗ FAILED")

EOF

echo ""
echo "✅ Deployment validation complete!"
echo "📄 Full Report: $REPORT_DIR/deployment-decision.md"

# Exit with appropriate code
if [ "$RISK_SCORE" -ge 100 ]; then
  echo ""
  echo "❌ DEPLOYMENT BLOCKED"
  exit 1
else
  echo ""
  echo "✅ Safe to proceed with deployment"
  exit 0
fi
```

---

## Usage Examples

### Basic Validation
```bash
/dev-aid-deploy-validate
```

### Before Production Deployment
```bash
# 1. Run full validation
/dev-aid-deploy-validate

# 2. If validation passes, deploy
git push origin main  # Triggers CI/CD

# 3. Monitor deployment
/dev-aid-health-check
```

### Integration with CI/CD

**GitHub Actions:**
```yaml
name: Deploy Validation
on:
  push:
    branches: [main]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: npm test
      - run: npm audit --audit-level=high
      - run: npm run build
```

**GitLab CI:**
```yaml
validate:
  stage: test
  script:
    - npm test
    - npm audit --audit-level=high
    - npm run build
  only:
    - main
```

---

## Deployment Environments

### Staging
- Tests must pass
- Configuration warnings allowed
- Security issues logged but not blocking

### Production
- All tests must pass
- Zero critical configuration issues
- Zero critical security vulnerabilities
- Build must succeed

---

## Success Criteria

Validation succeeds if:
- ✅ All tests pass
- ✅ Configuration is safe
- ✅ No critical security issues
- ✅ Production build succeeds
- ✅ Risk score < 100

---

**Begin pre-deployment validation.**
