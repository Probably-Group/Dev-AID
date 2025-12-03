# Security Tools Reference

Complete reference for all security scanning tools used in Dev-AID automation.

---

## Tool Overview

| Tool | Purpose | Speed | Languages | License |
|------|---------|-------|-----------|---------|
| **Opengrep** | SAST (code analysis) | Fast | 30+ | LGPL |
| **Gitleaks** | Secret scanning | Very Fast | All | MIT |
| **Trivy** | Dependencies + Containers + IaC | Fast | All | Apache 2.0 |
| **Hadolint** | Dockerfile linting | Very Fast | Dockerfile | GPL |
| **Checkov** | IaC scanning | Medium | Terraform, K8s, etc. | Apache 2.0 |

---

## 1. Opengrep (SAST)

**What is it?**
Open-source fork of Semgrep created in January 2025 by a consortium of security companies (Aikido, Endor Labs, Jit, Kodem, etc.) after Semgrep moved critical features behind paywalls.

**What it finds:**
- SQL injection
- XSS (Cross-Site Scripting)
- Command injection
- Path traversal
- Insecure deserialization
- Hardcoded credentials
- Weak cryptography
- OWASP Top 10 vulnerabilities

**Installation:**
```bash
curl -fsSL https://raw.githubusercontent.com/opengrep/opengrep/main/install.sh | bash
```

**Basic Usage:**
```bash
# Quick scan with auto-detection
opengrep scan --config=auto .

# Scan with specific severity
opengrep scan --config=auto --severity ERROR .

# SARIF output for CI/CD
opengrep scan --config=auto --sarif --output report.sarif .

# JSON output for parsing
opengrep scan --config=auto --json --output report.json .
```

**Advanced Usage:**
```bash
# Use security audit ruleset
opengrep scan --config=p/security-audit .

# Multiple rulesets
opengrep scan --config=p/security-audit --config=p/owasp-top-ten .

# Scan specific files
opengrep scan --config=auto src/auth/*.ts

# With timeout (for git hooks)
opengrep scan --config=auto --timeout 5 .
```

**Key Features vs. Semgrep:**
- ✅ All features fully open source (LGPL)
- ✅ No commercial restrictions
- ✅ Restored features: fingerprints, LOC tracking, metavariables
- ✅ Planned: Windows compatibility, cross-file analysis
- ✅ Backward compatible with Semgrep rules and workflows

**Sources:**
- [Opengrep GitHub](https://github.com/opengrep/opengrep)
- [Launching Opengrep](https://www.aikido.dev/blog/launching-opengrep-why-we-forked-semgrep)

---

## 2. Gitleaks (Secret Scanning)

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

# Via wget
wget https://github.com/gitleaks/gitleaks/releases/download/v8.18.4/gitleaks_8.18.4_linux_amd64.tar.gz
tar xzf gitleaks_8.18.4_linux_amd64.tar.gz
sudo mv gitleaks /usr/local/bin/
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
# Scan specific commit
gitleaks detect --log-opts="--since=2025-01-01"

# Scan specific directory
gitleaks detect --source ./src

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

## 3. Trivy (Multi-Purpose Scanner)

**What it scans:**
1. **Dependencies** - CVEs in npm, pip, go, cargo, maven, gradle, etc.
2. **Containers** - Docker images, OCI images
3. **IaC** - Terraform, CloudFormation, Kubernetes YAML
4. **Config files** - Misconfigurations in config files
5. **Licenses** - License compliance checking

**Installation:**
```bash
# Via homebrew
brew install aquasecurity/trivy/trivy

# Via script
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
```

**Basic Usage:**
```bash
# Scan filesystem for vulnerabilities
trivy fs .

# Scan with specific severity
trivy fs --severity HIGH,CRITICAL .

# Scan only dependencies
trivy fs --scanners vuln .

# Scan Docker image
trivy image myimage:latest

# Scan IaC files
trivy config ./terraform
```

**Advanced Usage:**
```bash
# Multiple scanners
trivy fs --scanners vuln,secret,misconfig .

# SARIF output for GitHub
trivy fs --format sarif --output trivy.sarif .

# JSON output for parsing
trivy fs --format json --output trivy.json .

# Ignore unfixed vulnerabilities
trivy fs --ignore-unfixed .

# Custom severity
trivy fs --severity CRITICAL,HIGH,MEDIUM .

# Skip DB update (for faster scans)
trivy fs --skip-db-update .
```

**Vulnerability Databases:**
- NVD (National Vulnerability Database)
- GHSA (GitHub Security Advisories)
- OSV (Open Source Vulnerabilities)

---

## 4. Hadolint (Dockerfile Linter)

**What it checks:**
- Best practices violations
- Security misconfigurations
- Performance anti-patterns
- Deprecated instructions
- Invalid syntax

**Installation:**
```bash
# Via homebrew
brew install hadolint

# Via wget
wget https://github.com/hadolint/hadolint/releases/download/v2.12.0/hadolint-Linux-x86_64
chmod +x hadolint-Linux-x86_64
sudo mv hadolint-Linux-x86_64 /usr/local/bin/hadolint
```

**Basic Usage:**
```bash
# Lint Dockerfile
hadolint Dockerfile

# JSON output
hadolint Dockerfile --format json

# Ignore specific rules
hadolint Dockerfile --ignore DL3006

# Strict mode (treat warnings as errors)
hadolint Dockerfile --failure-threshold warning
```

**Common Issues Detected:**
- `DL3003` - Use WORKDIR instead of cd
- `DL3006` - Always tag images, avoid :latest
- `DL3008` - Pin versions in apt-get install
- `DL3009` - Delete apt-get lists after installing
- `DL3025` - Use JSON notation for CMD and ENTRYPOINT
- `DL4006` - Set SHELL with pipefail option

---

## 5. Checkov (IaC Scanner)

**What it scans:**
- Terraform (.tf files)
- CloudFormation (YAML/JSON)
- Kubernetes manifests
- Helm charts
- Dockerfile
- ARM templates
- Serverless framework

**Installation:**
```bash
# Via pip
pip install checkov

# Via homebrew
brew install checkov
```

**Basic Usage:**
```bash
# Scan directory
checkov -d .

# Scan specific file
checkov -f terraform/main.tf

# Compact output
checkov -d . --compact

# Quiet mode
checkov -d . --quiet
```

**Advanced Usage:**
```bash
# Scan specific frameworks
checkov -d . --framework terraform

# Skip specific checks
checkov -d . --skip-check CKV_AWS_20

# Only run specific checks
checkov -d . --check CKV_AWS_19

# JSON output
checkov -d . --output json

# SARIF output for GitHub
checkov -d . --output sarif --output-file checkov.sarif

# Set baseline
checkov -d . --baseline checkov-baseline.json
```

**Common Checks:**
- `CKV_AWS_20` - S3 bucket has public access
- `CKV_AWS_19` - S3 bucket has server-side encryption
- `CKV_K8S_8` - Liveness probe not defined
- `CKV_K8S_14` - Image pull policy not set to Always
- `CKV_DOCKER_2` - HEALTHCHECK not defined in Dockerfile

---

## Quick Reference

### Git Hooks (Fast)
```bash
# Pre-commit (~10s)
gitleaks detect --no-git
opengrep scan --config=auto --severity ERROR --timeout 5 .
trivy fs --scanners vuln --severity CRITICAL .
```

### Git Hooks (Thorough)
```bash
# Pre-push (~60s)
gitleaks detect
opengrep scan --config=auto .
trivy fs --scanners vuln --severity HIGH,CRITICAL .
hadolint Dockerfile  # if exists
```

### CI/CD (Complete)
```bash
# Full security suite (~3-5 min)
gitleaks detect --report-path gitleaks.json
opengrep scan --config=auto --sarif --output opengrep.sarif .
trivy fs --scanners vuln,secret,misconfig --format sarif --output trivy.sarif .
trivy image --severity HIGH,CRITICAL myimage:latest
hadolint Dockerfile --format json > hadolint.json
checkov -d . --output sarif --output-file checkov.sarif
```

---

## Tool Comparison

### Speed Comparison (Typical Project)
| Tool | Git Hook (Fast) | Git Hook (Thorough) | CI/CD (Full) |
|------|----------------|---------------------|--------------|
| Gitleaks | 2s | 10s | 10s |
| Opengrep | 5s | 30s | 60s |
| Trivy | 3s | 20s | 90s |
| Hadolint | 1s | 1s | 1s |
| Checkov | - | - | 90s |
| **Total** | **~10s** | **~60s** | **~4 min** |

### Accuracy Comparison
| Tool | False Positives | False Negatives | Overall |
|------|----------------|-----------------|---------|
| Opengrep | Low | Medium | ⭐⭐⭐⭐ |
| Gitleaks | Very Low | Low | ⭐⭐⭐⭐⭐ |
| Trivy | Low | Low | ⭐⭐⭐⭐⭐ |
| Hadolint | Very Low | Low | ⭐⭐⭐⭐ |
| Checkov | Medium | Medium | ⭐⭐⭐ |

---

## Configuration Files

### Gitleaks Config (.gitleaks.toml)
```toml
title = "Dev-AID Gitleaks Config"

[allowlist]
description = "Allowlist for false positives"
paths = [
    ".*test.*",
    ".*example.*"
]
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

### Trivy Config (trivy.yaml)
```yaml
severity:
  - CRITICAL
  - HIGH
scan:
  skip-dirs:
    - node_modules
    - .git
```

---

## Troubleshooting

### Opengrep
**Issue:** "No rules found"
```bash
# Solution: Specify config explicitly
opengrep scan --config=p/security-audit .
```

**Issue:** Timeout in git hook
```bash
# Solution: Reduce timeout or scan only changed files
opengrep scan --config=auto --timeout 5 --include "*.py" .
```

### Gitleaks
**Issue:** Too many false positives
```bash
# Solution: Create baseline
gitleaks detect --report-path baseline.json
gitleaks detect --baseline-path baseline.json
```

### Trivy
**Issue:** Slow DB updates
```bash
# Solution: Skip DB update in git hooks
trivy fs --skip-db-update .
```

**Issue:** Can't scan without internet
```bash
# Solution: Download DB manually
trivy image --download-db-only
```

---

## Resources

**Opengrep:**
- GitHub: https://github.com/opengrep/opengrep
- Docs: https://www.opengrep.dev/
- Rules: https://github.com/opengrep/opengrep-rules

**Gitleaks:**
- GitHub: https://github.com/gitleaks/gitleaks
- Rules: https://github.com/gitleaks/gitleaks/blob/master/config/gitleaks.toml

**Trivy:**
- GitHub: https://github.com/aquasecurity/trivy
- Docs: https://aquasecurity.github.io/trivy/

**Hadolint:**
- GitHub: https://github.com/hadolint/hadolint
- Rules: https://github.com/hadolint/hadolint#rules

**Checkov:**
- GitHub: https://github.com/bridgecrewio/checkov
- Docs: https://www.checkov.io/
- Policies: https://www.checkov.io/5.Policy%20Index/all.html

---

## Next Steps

1. **Install tools:** `.dev-aid/automation/tools/install-security-tools.sh`
2. **Install git hooks:** `.dev-aid/automation/git-hooks/install.sh`
3. **Set up CI/CD:** Copy template from `.dev-aid/automation/ci-cd/`
4. **Read guide:** `.dev-aid/docs/AUTOMATION-GUIDE.md`
