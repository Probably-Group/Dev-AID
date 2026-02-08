# Security Tools Reference

Complete reference for security scanning tools used in Dev-AID automation.

---

## Tool Overview

Dev-AID uses **3 universal tools** plus **language-specific scanners** for comprehensive security coverage:

### Universal Tools (always run)

| Tool | Purpose | Scan Types | Coverage |
|------|---------|------------|----------|
| **Gitleaks** | Secret scanning | Secrets | Git history + current files |
| **Trivy** | Multi-scanner | CVE, Misconfig, Secrets | Dependencies, Dockerfiles, Terraform, K8s, GitHub Actions |
| **Opengrep** | SAST | Code patterns | OWASP Top 10, CWE Top 25, CI/CD security (340+ rules) |

### Language-Specific Tools (auto-detected, optional)

| Tool | Language | Detection | What It Scans |
|------|----------|-----------|---------------|
| **Bandit** | Python | `*.py` files exist | SAST — SQL injection, exec(), hardcoded passwords, weak crypto |
| **pip-audit** | Python | `requirements*.txt` or `pyproject.toml` | Dependency CVEs via PyPI advisory database |
| **npm audit** | JS/TS | `package-lock.json` or `yarn.lock` | Dependency CVEs via npm registry |
| **cargo audit** | Rust | `Cargo.lock` | Dependency CVEs via RustSec advisory database |
| **govulncheck** | Go | `go.mod` | Vulnerability analysis (official Go team tool) |

**Why this architecture?**
- **Universal tools** catch language-agnostic issues (secrets, IaC misconfig, generic SAST patterns)
- **Language-specific tools** provide deeper analysis tuned to each ecosystem's vulnerability patterns
- **Auto-detection** means no configuration needed — if the language isn't in the repo, checks skip silently
- **Missing tools emit warnings**, not errors — they're optional enhancements

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

## 4. Bandit (Python SAST)

**What it finds:**
- SQL injection via string formatting
- Use of `exec()`, `eval()`, `assert`
- Hardcoded passwords and secrets
- Weak cryptographic algorithms (MD5, SHA1, DES)
- Insecure temp file usage
- Shell injection via `subprocess` with `shell=True`
- Unsafe YAML loading (`yaml.load()` without `Loader`)

**Installation:**
```bash
# Via pipx (recommended — isolated environment)
pipx install bandit

# Via pip
pip install --user bandit
```

**Usage:**
```bash
# Scan with medium+ severity and confidence
bandit -r . -ll -ii --exclude '*/venv/*,*/node_modules/*,*/.git/*'

# JSON output
bandit -r . -ll -f json -o bandit-report.json

# Show only high severity
bandit -r . -lll

# Skip specific tests
bandit -r . --skip B101,B601
```

**Exit Codes:**
- `0` — No issues found
- `1` — Issues found

**Common Test IDs:**
| ID | Description |
|----|-------------|
| B101 | `assert` used (removed in optimized bytecode) |
| B103 | `os.chmod` with permissive mode |
| B301 | Pickle usage (deserialization risk) |
| B601 | Shell injection via `subprocess` |
| B608 | SQL injection via string formatting |

---

## 5. pip-audit (Python Dependency Vulnerabilities)

**What it finds:**
- Known CVEs in installed Python packages
- Vulnerabilities reported to PyPI advisory database
- Outdated packages with security fixes available

**Installation:**
```bash
# Via pipx (recommended)
pipx install pip-audit

# Via pip
pip install --user pip-audit
```

**Usage:**
```bash
# Audit current environment
pip-audit --desc

# Audit a requirements file
pip-audit -r requirements.txt --desc

# JSON output
pip-audit -f json -o pip-audit-report.json

# Fix vulnerabilities automatically
pip-audit --fix
```

**Exit Codes:**
- `0` — No vulnerabilities
- `1` — Vulnerabilities found

---

## 6. npm audit (JS/TS Dependency Vulnerabilities)

**What it finds:**
- Known CVEs in npm dependencies
- Vulnerabilities from the npm advisory database
- Transitive dependency vulnerabilities

**Installation:**
Built-in with Node.js/npm — no separate installation needed.

**Usage:**
```bash
# Audit with high+ threshold (used in pre-push hook)
npm audit --audit-level=high

# Full audit (all severities)
npm audit

# JSON output
npm audit --json

# Fix vulnerabilities automatically
npm audit fix

# Force fix (may include breaking changes)
npm audit fix --force
```

**Exit Codes:**
- `0` — No vulnerabilities at or above the audit level
- `1` — Vulnerabilities found

**Note:** Requires `package-lock.json` or `yarn.lock` — won't work with just `package.json`.

---

## 7. cargo audit (Rust Dependency Vulnerabilities)

**What it finds:**
- Known CVEs in Rust crate dependencies
- Vulnerabilities from the RustSec Advisory Database
- Unmaintained crates
- Yanked crate versions

**Installation:**
```bash
cargo install cargo-audit
```

**Usage:**
```bash
# Audit dependencies
cargo audit

# JSON output
cargo audit --json

# Fix vulnerabilities (update Cargo.lock)
cargo audit fix
```

**Exit Codes:**
- `0` — No vulnerabilities
- `1` — Vulnerabilities found

---

## 8. govulncheck (Go Vulnerability Checker)

**What it finds:**
- Known vulnerabilities in Go dependencies
- Vulnerabilities that affect code paths actually used by your project
- Issues from the Go vulnerability database (vuln.go.dev)

**Installation:**
```bash
go install golang.org/x/vuln/cmd/govulncheck@latest
```

**Usage:**
```bash
# Check all packages
govulncheck ./...

# JSON output
govulncheck -json ./...

# Check specific package
govulncheck ./cmd/myapp
```

**Exit Codes:**
- `0` — No vulnerabilities affecting your code
- `3` — Vulnerabilities found

**Key feature:** Unlike most dependency scanners, govulncheck only reports vulnerabilities in functions your code actually calls, reducing false positives.

---

## Quick Reference

### Git Hooks

**Pre-commit (~10s):**
```bash
gitleaks detect --no-git
opengrep scan --config p/default --config p/security-audit --config p/secrets --severity ERROR .
trivy fs --scanners vuln,misconfig,secret --severity CRITICAL .
```

**Pre-push (~60-90s):**
```bash
# Universal checks (always run)
gitleaks detect  # includes git history
opengrep scan --config p/default --config p/security-audit --config p/secrets --config p/ci --config p/cwe-top-25 .
trivy fs --scanners vuln,misconfig,secret --severity HIGH,CRITICAL .

# Language-specific checks (auto-detected)
bandit -r . -ll -ii --exclude '*/venv/*,*/node_modules/*'   # if *.py files exist
pip-audit --desc                                             # if requirements*.txt or pyproject.toml
npm audit --audit-level=high                                 # if package-lock.json or yarn.lock
cargo audit                                                  # if Cargo.lock
govulncheck ./...                                            # if go.mod
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

### Universal Tools

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

### Language-Specific Tools

**Bandit:**
- GitHub: https://github.com/PyCQA/bandit
- Docs: https://bandit.readthedocs.io/

**pip-audit:**
- GitHub: https://github.com/pypa/pip-audit

**npm audit:**
- Docs: https://docs.npmjs.com/cli/commands/npm-audit

**cargo audit:**
- GitHub: https://github.com/rustsec/rustsec/tree/main/cargo-audit
- Advisory DB: https://github.com/rustsec/advisory-db

**govulncheck:**
- Docs: https://pkg.go.dev/golang.org/x/vuln/cmd/govulncheck
- Vulnerability DB: https://vuln.go.dev/

---

## Next Steps

1. **Install tools:** `.dev-aid/automation/tools/install-security-tools.sh`
2. **Install git hooks:** `.dev-aid/automation/git-hooks/install.sh`
3. **Run full scan:** `.dev-aid/scripts/security-scan.sh`
4. **Generate SBOM:** `.dev-aid/scripts/security-scan.sh --sbom`
