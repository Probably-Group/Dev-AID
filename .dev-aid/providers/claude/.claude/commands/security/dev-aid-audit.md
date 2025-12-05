---
name: aid-audit
description: Comprehensive security audit with OWASP Top 10, dependency scanning, and vulnerability assessment
category: security
author: Dev-AID Team (adapted from Tresor)
version: 1.0.0
---

# Security Audit - Comprehensive Security Assessment

Perform a comprehensive security audit of your codebase following DevSecOps best practices.

## Overview

This command conducts a multi-phase security audit:
- **Phase 1**: Tech stack detection and scope planning
- **Phase 2**: OWASP Top 10 vulnerability scanning
- **Phase 3**: Dependency security analysis
- **Phase 4**: Infrastructure security review
- **Phase 5**: Consolidation and remediation roadmap

## Dev-AID Integration

### Memory Bank Updates
This command updates:
- `.dev-aid/memory-bank/security.md` - Security findings and remediation status
- `.dev-aid/memory-bank/patterns.md` - Security anti-patterns discovered

### Report Output
Reports are saved to:
- `.dev-aid/reports/security/audit-[timestamp]/`

### Multi-Provider Support
This command works with all enabled providers (Claude, Gemini, OpenAI).

---

## Execution Steps

### Phase 1: Tech Stack Detection

First, analyze the codebase to detect technologies:

```bash
# Detect programming languages and frameworks
echo "=== Tech Stack Detection ==="

# Check for JavaScript/TypeScript
if [ -f "package.json" ]; then
  echo "✓ Node.js project detected"
  echo "Dependencies:"
  jq -r '.dependencies | keys[]' package.json | head -10
fi

# Check for Python
if [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
  echo "✓ Python project detected"
fi

# Check for Go
if [ -f "go.mod" ]; then
  echo "✓ Go project detected"
fi

# Check for Rust
if [ -f "Cargo.toml" ]; then
  echo "✓ Rust project detected"
fi

# Check for infrastructure
if [ -f "Dockerfile" ]; then
  echo "✓ Docker detected"
fi

if [ -f "docker-compose.yml" ]; then
  echo "✓ Docker Compose detected"
fi

if [ -d ".github/workflows" ]; then
  echo "✓ GitHub Actions detected"
fi
```

### Phase 2: OWASP Top 10 Vulnerability Scanning

Scan for common security vulnerabilities:

**1. SQL Injection**
```bash
# Search for potential SQL injection vulnerabilities
echo "=== Checking for SQL Injection Vulnerabilities ==="
grep -rn --include="*.js" --include="*.ts" --include="*.py" \
  -E "(SELECT|INSERT|UPDATE|DELETE).*(req\.|request\.|input|params)" . | head -20
```

**2. XSS (Cross-Site Scripting)**
```bash
# Search for unescaped output
echo "=== Checking for XSS Vulnerabilities ==="
grep -rn --include="*.js" --include="*.jsx" --include="*.ts" --include="*.tsx" \
  -E "innerHTML|dangerouslySetInnerHTML" . | head -20
```

**3. Broken Authentication**
```bash
# Check for weak authentication patterns
echo "=== Checking Authentication Security ==="
grep -rn --include="*.js" --include="*.py" \
  -E "(password|secret|token).*=.*['\"]" . | head -20
```

**4. Sensitive Data Exposure**
```bash
# Search for hardcoded secrets
echo "=== Checking for Hardcoded Secrets ==="
grep -rn -E "(api[_-]?key|secret|password|token).*=.*['\"][a-zA-Z0-9]{20,}" . \
  --exclude-dir=node_modules --exclude-dir=.git | head -20
```

**5. Security Misconfiguration**
```bash
# Check for security misconfigurations
echo "=== Checking for Security Misconfigurations ==="

# Check CORS configuration
grep -rn "cors.*origin.*\*" . --include="*.js" --include="*.py"

# Check DEBUG mode
grep -rn "DEBUG.*=.*true" . --include="*.js" --include="*.py" --include="*.env*"
```

### Phase 3: Dependency Security Analysis

Check dependencies for known vulnerabilities:

**For Node.js:**
```bash
if [ -f "package.json" ]; then
  echo "=== Running npm audit ==="
  npm audit --audit-level=moderate

  echo "=== Checking for outdated packages ==="
  npm outdated
fi
```

**For Python:**
```bash
if [ -f "requirements.txt" ]; then
  echo "=== Checking Python dependencies ==="
  # Install pip-audit if needed: pip install pip-audit
  pip-audit --desc 2>/dev/null || echo "Tip: Install pip-audit for CVE scanning"
fi
```

**For Go:**
```bash
if [ -f "go.mod" ]; then
  echo "=== Checking Go dependencies ==="
  go list -m all | grep -v "^go$" | head -20
fi
```

### Phase 4: Infrastructure Security Review

**Docker Security:**
```bash
if [ -f "Dockerfile" ]; then
  echo "=== Checking Dockerfile Security ==="

  # Check for running as root
  grep -n "^USER" Dockerfile || echo "⚠️  WARNING: No USER directive found (running as root)"

  # Check for latest tag usage
  grep -n ":latest" Dockerfile && echo "⚠️  WARNING: Using :latest tag (not reproducible)"

  # Check for secrets in build args
  grep -n "ARG.*SECRET\|ARG.*PASSWORD\|ARG.*API_KEY" Dockerfile
fi
```

**Kubernetes Security:**
```bash
if [ -d "k8s" ] || [ -d "kubernetes" ]; then
  echo "=== Checking Kubernetes Security ==="

  # Check for privileged containers
  grep -rn "privileged: true" k8s/ kubernetes/ 2>/dev/null

  # Check for hostPath volumes
  grep -rn "hostPath:" k8s/ kubernetes/ 2>/dev/null
fi
```

### Phase 5: Generate Report

Create a comprehensive security audit report:

```bash
# Create report directory
TIMESTAMP=$(date +%Y-%m-%d-%H%M%S)
REPORT_DIR=".dev-aid/reports/security/audit-${TIMESTAMP}"
mkdir -p "$REPORT_DIR"

# Generate final report
cat > "$REPORT_DIR/audit-report.md" <<EOF
# Security Audit Report

**Date**: $(date)
**Project**: $(basename $(pwd))
**Audit ID**: audit-${TIMESTAMP}

## Summary

- Tech stack detected: [Auto-detected stack]
- OWASP vulnerabilities: [Number found]
- Dependency vulnerabilities: [Number found]
- Infrastructure issues: [Number found]

## Critical Findings

### High Priority
[List critical findings here]

### Medium Priority
[List medium priority findings here]

### Low Priority
[List low priority findings here]

## Remediation Roadmap

### Immediate (< 1 day)
- [ ] Fix critical SQL injection vulnerabilities
- [ ] Remove hardcoded API keys
- [ ] Fix critical CVEs in dependencies

### Short-term (1-7 days)
- [ ] Implement input validation
- [ ] Add security headers
- [ ] Update vulnerable dependencies

### Long-term (> 7 days)
- [ ] Implement security testing in CI/CD
- [ ] Add automated dependency scanning
- [ ] Security training for team

## Next Steps

1. Review this report: $REPORT_DIR/audit-report.md
2. Update security.md: .dev-aid/memory-bank/security.md
3. Run \`/dev-aid-vulnerability-scan\` for deep CVE analysis
4. Run \`/dev-aid-deploy-validate\` before next deployment

---

**Report Location**: $REPORT_DIR/
EOF

echo "✅ Security audit complete!"
echo "📄 Report: $REPORT_DIR/audit-report.md"
```

---

## Update Memory Bank

After completing the audit, update the security memory bank:

```bash
# Append findings to security.md
cat >> .dev-aid/memory-bank/security.md <<EOF

## Security Audit - $(date +%Y-%m-%d)

**Audit ID**: audit-${TIMESTAMP}
**Critical Issues**: [Number]
**Status**: In Progress

### Key Findings
- [Finding 1]
- [Finding 2]
- [Finding 3]

### Actions Taken
- [Action 1]
- [Action 2]

### Next Audit**: $(date -d "+90 days" +%Y-%m-%d)
EOF
```

---

## Expert Skills Integration

For deep security analysis, Dev-AID includes expert security skills:

- **devsecops-expert**: DevSecOps best practices and CI/CD security
- **appsec-expert**: Application security and OWASP expertise
- **security-auditing**: Comprehensive security auditing
- **encryption**: Cryptography and encryption best practices

To leverage these skills, you can:
```bash
# Use DevSecOps expert for infrastructure security
# The skill will be auto-activated when working on security tasks
```

---

## Configuration

Default behavior:
- **Scope**: Full audit (code + dependencies + infrastructure)
- **Depth**: Medium (critical + high vulnerabilities)
- **Output**: Markdown report + memory bank update

---

## Usage Examples

### Basic Audit
```bash
/dev-aid-audit
```

### Focus on Web Application Security
After running the audit, manually review:
- SQL injection findings
- XSS vulnerabilities
- Authentication/authorization issues
- CSRF protection

### Focus on Infrastructure
After running the audit, manually review:
- Docker security findings
- Kubernetes misconfigurations
- Cloud security settings

---

## Success Criteria

Audit is successful if:
- ✅ Tech stack detected
- ✅ OWASP Top 10 scan completed
- ✅ Dependency vulnerabilities identified
- ✅ Infrastructure security reviewed
- ✅ Report generated
- ✅ Memory bank updated

---

## Related Commands

- `/dev-aid-vulnerability-scan` - Deep CVE scanning with exploit correlation
- `/dev-aid-compliance-check` - GDPR, SOC2, HIPAA compliance validation
- `/dev-aid-deploy-validate` - Pre-deployment security validation

---

**Note**: This command provides a comprehensive security overview. For production systems, consider using additional specialized security tools like:
- **SAST**: SonarQube, Semgrep, CodeQL
- **DAST**: OWASP ZAP, Burp Suite
- **SCA**: Snyk, Dependabot, npm audit
- **Container Scanning**: Trivy, Clair, Anchore

---

**Begin comprehensive security audit.**
