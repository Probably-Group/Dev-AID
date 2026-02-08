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
| **Opengrep** | SAST | Code patterns | 35+ languages with auto-detected language-specific rulesets |

### Language-Specific Tools (auto-detected, optional)

| Tool | Type | Language | Detection | What It Scans |
|------|------|----------|-----------|---------------|
| **ShellCheck** | SAST | Bash/Shell | `*.sh` files exist | Injection, unquoted vars, globbing attacks, eval risks |
| **Flawfinder** | SAST | C/C++ | `*.c`/`*.h`/`*.cpp`/`*.cc`/`*.cxx`/`*.hpp` | CWE-mapped: buffer overflows, format strings, race conditions |
| **mobsfscan** | SAST | Swift | `*.swift` files exist | OWASP MASVS/MSTG: insecure storage, weak crypto, hardcoded secrets |
| **Bandit** | SAST | Python | `*.py` files exist | SQL injection, exec(), hardcoded passwords, weak crypto |
| **pip-audit** | Deps | Python | `requirements*.txt` or `pyproject.toml` | Dependency CVEs via PyPI advisory database |
| **npm audit** | Deps | JS/TS | `package-lock.json` or `yarn.lock` | Dependency CVEs via npm registry |
| **cargo audit** | Deps | Rust | `Cargo.lock` | Dependency CVEs via RustSec advisory database |
| **govulncheck** | Deps | Go | `go.mod` | Vulnerability analysis (official Go team tool) |

### Opengrep Language-Aware Rulesets (auto-detected)

Opengrep natively supports **35+ languages**. The pre-push hook auto-detects which languages are present and adds language-specific rulesets:

| Language | Ruleset | Detection |
|----------|---------|-----------|
| Python | `p/python` | `*.py` |
| JavaScript | `p/javascript` | `*.js`, `*.jsx` |
| TypeScript | `p/typescript` | `*.ts`, `*.tsx` |
| Go | `p/golang` | `*.go` |
| Rust | `p/rust` | `*.rs` |
| Swift | `p/swift` | `*.swift` |
| Java | `p/java` | `*.java` |
| Kotlin | `p/kotlin` | `*.kt` |
| Ruby | `p/ruby` | `*.rb` |
| PHP | `p/php` | `*.php` |
| C# | `p/csharp` | `*.cs` |
| Scala | `p/scala` | `*.scala` |

These are added on top of the 10 universal rulesets (see Opengrep section below).

**Why this architecture?**
- **Universal tools** catch language-agnostic issues (secrets, IaC misconfig, generic SAST patterns)
- **Opengrep** provides broad SAST across 35+ languages with auto-detected rulesets
- **Dedicated SAST tools** (ShellCheck, Flawfinder, mobsfscan, Bandit) go deeper than pattern matching for specific languages
- **Dependency scanners** (pip-audit, npm audit, cargo audit, govulncheck) check ecosystem-specific advisory databases
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

## 3. Opengrep (SAST — 35+ Languages, Auto-Detected Rulesets)

**What is it?**
Open-source fork of Semgrep created in January 2025 by a consortium of security companies after Semgrep moved critical features behind paywalls.

**Supported languages (GA):** Python, JavaScript, TypeScript, Go, Rust, Swift, C, C++, C#, Java, Kotlin, Scala, Ruby, PHP, JSX, TSX, Terraform (HCL), JSON, and more. Experimental support for Bash, Dockerfile, HTML, YAML, Solidity, and others.

**What it finds:**
- SQL injection, XSS, Command injection, Path traversal
- Insecure deserialization, Hardcoded credentials, Weak cryptography
- OWASP Top 10 and CWE Top 25 vulnerabilities
- CI/CD security issues (GitHub Actions, etc.)
- JWT misconfigurations, Insecure transport (HTTP vs HTTPS)
- Language-specific anti-patterns (per auto-detected rulesets)

**Installation:**
```bash
curl -fsSL https://raw.githubusercontent.com/opengrep/opengrep/main/install.sh | bash
```

**Dev-AID Universal Rulesets (10 rulesets, always active):**
```bash
opengrep scan \
  --config p/default \            # Semgrep curated defaults
  --config p/security-audit \     # Comprehensive security patterns
  --config p/secrets \            # Hardcoded credentials
  --config p/ci \                 # CI/CD security (GitHub Actions)
  --config p/cwe-top-25 \         # MITRE CWE Top 25
  --config p/owasp-top-ten \      # OWASP Top 10 categories
  --config p/trailofbits \        # Trail of Bits professional audit rules
  --config p/command-injection \  # Command injection across languages
  --config p/insecure-transport \ # HTTP where HTTPS expected
  --config p/jwt \                # JWT misconfigurations
  .
```

**Auto-detected language rulesets** (added when files are present):
`p/python`, `p/javascript`, `p/typescript`, `p/golang`, `p/rust`, `p/swift`, `p/java`, `p/kotlin`, `p/ruby`, `p/php`, `p/csharp`, `p/scala`

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
# SARIF output for CI/CD
opengrep scan --config=auto --sarif --output report.sarif .

# With timeout (for git hooks)
opengrep scan --config=auto --timeout 5 .

# Framework-specific rulesets (available but not in default set)
opengrep scan --config p/django --config p/flask .     # Python frameworks
opengrep scan --config p/react --config p/express .    # JS frameworks
opengrep scan --config p/spring .                      # Java framework
```

---

## 4. ShellCheck (Bash/Shell SAST)

**What it finds:**
- Unquoted variables (globbing/word splitting — key injection vector)
- Glob patterns interpreted as command-line options (option injection)
- `eval` usage with user-controlled data
- Shell injection in `find -exec` commands
- Catastrophic `rm` with unquoted/unvalidated paths
- Incorrect quoting patterns
- Word splitting and globbing attacks
- 100+ distinct check categories (SC codes)

**Installation:**
```bash
# Via homebrew (macOS)
brew install shellcheck

# Via apt (Debian/Ubuntu)
apt install shellcheck

# Via cabal (Haskell)
cabal install ShellCheck
```

**Usage:**
```bash
# Scan with warning+ severity (used in pre-push hook)
shellcheck -S warning script.sh

# Scan multiple files
shellcheck -S warning *.sh

# JSON output
shellcheck -f json script.sh

# Exclude specific checks
shellcheck --exclude=SC2086,SC2035 script.sh

# Check specific shell dialect
shellcheck --shell=bash script.sh
```

**Exit Codes:**
- `0` — No issues found
- `1` — Issues found

**Key SC codes (security-relevant):**
| Code | Description |
|------|-------------|
| SC2086 | Unquoted variable (injection/globbing vector) |
| SC2035 | Glob expanded as command-line option |
| SC2046 | Unquoted command substitution |
| SC2091 | Command substitution in condition |
| SC2155 | Declare and assign separately to avoid masking return values |

---

## 5. Flawfinder (C/C++ SAST)

**What it finds:**
- Buffer overflows (`strcpy`, `strcat`, `gets`, `sprintf`)
- Format string vulnerabilities (`printf` family)
- Race conditions (TOCTOU via `access`, `stat`)
- Temporary file issues (`mktemp`, `tmpnam`)
- Random number generation weaknesses (`rand`, `srand`)
- Shell execution risks (`system`, `popen`, `exec`)
- All findings are CWE-mapped

**Installation:**
```bash
# Via pipx (recommended)
pipx install flawfinder

# Via pip
pip install --user flawfinder
```

**Usage:**
```bash
# Scan with medium+ severity (used in pre-push hook)
flawfinder --minlevel=2 .

# CSV output for parsing
flawfinder --minlevel=2 --dataonly --csv .

# HTML report
flawfinder --html --minlevel=2 . > report.html

# Show CWE mappings
flawfinder --cwecounts .

# Scan specific files
flawfinder src/crypto.c src/network.c
```

**Exit Codes:**
- `0` — Always (even with findings; check output)

**Severity Levels:**
| Level | Risk | Example |
|-------|------|---------|
| 0 | No risk | Informational |
| 1 | Low | Minor issues |
| 2 | Medium | `strlen`, `getenv` |
| 3 | Medium-High | `getopt`, environment access |
| 4 | High | `strcpy`, `strcat`, `sprintf` |
| 5 | Critical | `gets` (always buffer overflow) |

---

## 6. mobsfscan (Swift SAST)

**What it finds:**
- Insecure data storage (UserDefaults for secrets, unprotected Keychain)
- Weak cryptographic algorithms (MD5, SHA1, DES, ECB mode)
- Hardcoded secrets and API keys
- Insecure network connections (HTTP without ATS)
- Insecure random number generation
- WebView security issues (JavaScript enabled, universal access)
- Jailbreak detection bypass risks
- Based on OWASP MASVS (Mobile Application Security Verification Standard)

**Installation:**
```bash
# Via pipx (recommended)
pipx install mobsfscan

# Via pip
pip install --user mobsfscan
```

**Usage:**
```bash
# Scan current directory
mobsfscan .

# JSON output (used in pre-push hook)
mobsfscan --json -o report.json .

# SARIF output for CI/CD
mobsfscan --sarif -o report.sarif .

# Scan specific directory
mobsfscan /path/to/swift/project
```

**Exit Codes:**
- `0` — Scan completed (check findings count in output)

**Note:** mobsfscan also supports Objective-C and Android (Java/Kotlin) scanning. In the pre-push hook, it runs when `*.swift` files are detected, but it will also catch issues in any co-located Objective-C files.

---

## 7. Bandit (Python SAST)

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

## 8. pip-audit (Python Dependency Vulnerabilities)

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

## 9. npm audit (JS/TS Dependency Vulnerabilities)

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

## 10. cargo audit (Rust Dependency Vulnerabilities)

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

## 11. govulncheck (Go Vulnerability Checker)

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
gitleaks detect                    # includes git history
opengrep scan [10 universal + auto-detected language rulesets] .
trivy fs --scanners vuln,misconfig,secret --severity HIGH,CRITICAL .

# Language-specific SAST (auto-detected)
shellcheck -S warning *.sh                                   # if *.sh files exist
flawfinder --minlevel=2 .                                    # if *.c/*.h/*.cpp files exist
mobsfscan .                                                  # if *.swift files exist
bandit -r . -ll -ii --exclude '*/venv/*,*/node_modules/*'    # if *.py files exist

# Language-specific dependency audit (auto-detected)
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

### Language-Specific SAST Tools

**ShellCheck:**
- GitHub: https://github.com/koalaman/shellcheck
- Wiki (SC codes): https://www.shellcheck.net/wiki/

**Flawfinder:**
- GitHub: https://github.com/david-a-wheeler/flawfinder
- Docs: https://dwheeler.com/flawfinder/

**mobsfscan:**
- GitHub: https://github.com/MobSF/mobsfscan
- OWASP MASVS: https://mas.owasp.org/

**Bandit:**
- GitHub: https://github.com/PyCQA/bandit
- Docs: https://bandit.readthedocs.io/

### Language-Specific Dependency Tools

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
