# Security Tools Reference

Complete reference for security scanning tools used in Dev-AID automation.

---

## Tool Overview

Dev-AID uses **3 tools** for comprehensive security coverage:

| Tool | Purpose | Scan Types | Coverage |
|------|---------|------------|----------|
| **Gitleaks** | Secret scanning | Secrets | Git history + current files |
| **Trivy** | Multi-scanner | CVE, Misconfig, Secrets | Dependencies, Dockerfiles, Terraform, K8s, GitHub Actions |
| **Opengrep** | SAST | Code patterns | OWASP Top 10, CWE Top 25, CI/CD security (340+ rules) |

**Why 3 tools?**
- **Trivy's `misconfig` scanner** covers Dockerfile and IaC scanning (replaces Hadolint/Checkov)
- **Opengrep** covers SAST with 340+ rules across 5 comprehensive rulesets
- **Gitleaks** specializes in git history scanning (Trivy only scans current files)

---

## 1. Gitleaks (Secret Scanning)

**What it finds:**
- API keys (AWS, Azure, GCP, GitHub, etc.)
- Private keys (SSH, PGP, TLS)
- Database credentials
- OAuth tokens
- JWT secrets
- Generic passwords and secrets

**Installation:**
```bash
# Via homebrew (macOS/Linux)
brew install gitleaks

# Via installer script
./.dev-aid/automation/tools/install-security-tools.sh
```

**Basic Usage:**
```bash
# Scan current directory (staged files only)
gitleaks detect --no-git

# Scan with git history
gitleaks detect

# Verbose output
gitleaks detect --verbose

# Generate report
gitleaks detect --report-path gitleaks-report.json
```

**Advanced Usage:**
```bash
# Scan specific commit range
gitleaks detect --log-opts="--since=2025-01-01"

# Custom config
gitleaks detect --config .gitleaks.toml

# Baseline (ignore existing secrets)
gitleaks detect --baseline-path gitleaks-baseline.json
```

**Exit Codes:**
- `0` - No leaks found
- `1` - Leaks found
- `2` - Error occurred

---

## 2. Trivy (Multi-Purpose Scanner)

**What it scans:**
1. **vuln** - CVEs in dependencies (npm, pip, go, cargo, maven, etc.)
2. **misconfig** - Dockerfiles, Terraform, K8s, CloudFormation, GitHub Actions
3. **secret** - Secrets in current files
4. **license** - License compliance checking
5. **sbom** - Software Bill of Materials generation

**Installation:**
```bash
# Via homebrew
brew install aquasecurity/trivy/trivy

# Via script
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
```

**Basic Usage:**
```bash
# Scan filesystem for all issues
trivy fs --scanners vuln,misconfig,secret .

# Scan with specific severity
trivy fs --severity HIGH,CRITICAL .

# Scan Docker image
trivy image myimage:latest
```

**Advanced Usage:**
```bash
# All scanners with HIGH+ severity
trivy fs --scanners vuln,misconfig,secret --severity HIGH,CRITICAL .

# SARIF output for GitHub
trivy fs --format sarif --output trivy.sarif .

# JSON output for parsing
trivy fs --format json --output trivy.json .

# Generate SBOM (CycloneDX)
trivy fs --format cyclonedx --output sbom.json .

# Generate SBOM (SPDX)
trivy fs --format spdx-json --output sbom-spdx.json .

# Skip directories
trivy fs --skip-dirs node_modules --skip-dirs .venv .
```

**Misconfig Coverage (replaces Hadolint/Checkov):**
- Dockerfile best practices and security
- Terraform security misconfigurations
- Kubernetes manifest security
- CloudFormation template issues
- GitHub Actions workflow security
- Helm chart security

---

## 3. Opengrep (SAST - 340+ Rules)

**What is it?**
Open-source fork of Semgrep created in January 2025 by a consortium of security companies after Semgrep moved critical features behind paywalls.

**What it finds:**
- SQL injection
- XSS (Cross-Site Scripting)
- Command injection
- Path traversal
- Insecure deserialization
- Hardcoded credentials
- Weak cryptography
- OWASP Top 10 vulnerabilities
- CWE Top 25 vulnerabilities
- CI/CD security issues

**Installation:**
```bash
curl -fsSL https://raw.githubusercontent.com/opengrep/opengrep/main/install.sh | bash
```

**Dev-AID Default Rulesets (340+ rules):**
```bash
opengrep scan \
  --config p/default \        # Semgrep curated defaults
  --config p/security-audit \ # Comprehensive security patterns
  --config p/secrets \        # Hardcoded credentials
  --config p/ci \             # CI/CD security (GitHub Actions)
  --config p/cwe-top-25 \     # MITRE CWE Top 25
  .
```

**Basic Usage:**
```bash
# Quick scan with auto-detection
opengrep scan --config=auto .

# Scan with specific severity
opengrep scan --config=auto --severity ERROR .

# JSON output
opengrep scan --config=auto --json --output report.json .
```

**Advanced Usage:**
```bash
# Multiple rulesets (Dev-AID default)
opengrep scan --config p/default --config p/security-audit --config p/secrets .

# SARIF output for CI/CD
opengrep scan --config=auto --sarif --output report.sarif .

# With timeout (for git hooks)
opengrep scan --config=auto --timeout 5 .
```

---

## Quick Reference

### Git Hooks

**Pre-commit (~10s):**
```bash
gitleaks detect --no-git
opengrep scan --config p/default --config p/security-audit --config p/secrets --severity ERROR .
trivy fs --scanners vuln,misconfig,secret --severity CRITICAL .
```

**Pre-push (~60s):**
```bash
gitleaks detect  # includes git history
opengrep scan --config p/default --config p/security-audit --config p/secrets --config p/ci --config p/cwe-top-25 .
trivy fs --scanners vuln,misconfig,secret --severity HIGH,CRITICAL .
```

### CI/CD (Complete)

```bash
# Full security suite (~3-5 min)
gitleaks detect --report-path gitleaks.json
opengrep scan --config p/security-audit --sarif --output opengrep.sarif .
trivy fs --scanners vuln,misconfig,secret --format sarif --output trivy.sarif .
trivy fs --format cyclonedx --output sbom.json .  # SBOM generation
```

---

## Configuration Files

### Gitleaks Config (.gitleaks.toml)
```toml
title = "Dev-AID Gitleaks Config"

[allowlist]
description = "Allowlist for false positives"
paths = [
    '''.*test.*''',
    '''.*example.*''',
    '''.*SKILL\.md'''
]
```

### Trivy Config (trivy.yaml)
```yaml
severity:
  - CRITICAL
  - HIGH

scan:
  skip-dirs:
    - node_modules
    - .git
    - .venv
    - venv
```

### Opengrep Config (.opengrep.yml)
```yaml
rules:
  - id: custom-sql-injection
    pattern: $DB.execute($USER_INPUT)
    message: Potential SQL injection
    severity: ERROR
    languages: [python, javascript]
```

---

## Troubleshooting

### Gitleaks
**Issue:** Too many false positives
```bash
# Create baseline
gitleaks detect --report-path baseline.json
gitleaks detect --baseline-path baseline.json
```

### Trivy
**Issue:** Slow DB updates
```bash
# Skip DB update in git hooks
trivy fs --skip-db-update .
```

**Issue:** Can't scan without internet
```bash
# Download DB manually
trivy image --download-db-only
```

### Opengrep
**Issue:** "No rules found"
```bash
# Specify config explicitly
opengrep scan --config=p/security-audit .
```

**Issue:** Timeout in git hook
```bash
# Reduce timeout
opengrep scan --config=auto --timeout 3 .
```

---

## Resources

**Gitleaks:**
- GitHub: https://github.com/gitleaks/gitleaks
- Rules: https://github.com/gitleaks/gitleaks/blob/master/config/gitleaks.toml

**Trivy:**
- GitHub: https://github.com/aquasecurity/trivy
- Docs: https://aquasecurity.github.io/trivy/

**Opengrep:**
- GitHub: https://github.com/opengrep/opengrep
- Docs: https://www.opengrep.dev/
- Rules: https://semgrep.dev/r (compatible with Opengrep)

---

## Next Steps

1. **Install tools:** `.dev-aid/automation/tools/install-security-tools.sh`
2. **Install git hooks:** `.dev-aid/automation/git-hooks/install.sh`
3. **Run full scan:** `.dev-aid/scripts/security-scan.sh`
4. **Generate SBOM:** `.dev-aid/scripts/security-scan.sh --sbom`
