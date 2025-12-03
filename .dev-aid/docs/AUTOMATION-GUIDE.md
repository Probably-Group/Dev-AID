# Dev-AID Automation Guide

Complete guide to automated security and quality checks in Dev-AID.

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Architecture](#architecture)
4. [Git Hooks](#git-hooks)
5. [CI/CD Integration](#cicd-integration)
6. [Security Tools](#security-tools)
7. [Configuration](#configuration)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Overview

### The Problem

Developers need to remember:
- ❌ Run security scans before commits
- ❌ Check for secrets in code
- ❌ Scan dependencies for CVEs
- ❌ Follow TDD practices
- ❌ Run linters and formatters
- ❌ Validate Dockerfiles
- ❌ Check IaC configurations

**Result:** Things get forgotten, security issues slip through

### The Solution

**Dev-AID Automation** - A 3-tier defense system that runs checks automatically:

```
┌─────────────────────────────────────────────┐
│  TIER 1: Pre-Commit Hook (~10s)             │
│  • Secrets scan (Gitleaks)                  │
│  • Critical code issues (Opengrep)          │
│  • Critical CVEs (Trivy)                    │
│  ✓ Fast, catches obvious issues             │
└─────────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  TIER 2: Pre-Push Hook (~60s)               │
│  • Full secret scan + git history           │
│  • Complete SAST scan (all severities)      │
│  • Dependency scan (HIGH + CRITICAL)        │
│  • Dockerfile lint (if exists)              │
│  ✓ Thorough, prevents bad code from remote  │
└─────────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  TIER 3: CI/CD Pipeline (~3-5 min)          │
│  • All above checks                         │
│  • Container scanning                       │
│  • IaC scanning (Checkov)                   │
│  • License compliance                       │
│  • SBOM generation                          │
│  ✓ Complete, blocks PR/deployment           │
└─────────────────────────────────────────────┘
```

**Result:** Developers can't forget - automation remembers for them!

---

## Quick Start

### 1. Install Security Tools

```bash
# Run the installer
./.dev-aid/automation/tools/install-security-tools.sh

# Verify installation
opengrep --version
gitleaks version
trivy --version
hadolint --version
checkov --version
```

### 2. Install Git Hooks

```bash
# Install pre-commit and pre-push hooks
./.dev-aid/automation/git-hooks/install.sh

# Verify
ls -la .git/hooks/pre-commit .git/hooks/pre-push
```

### 3. Set Up CI/CD (Optional)

**For GitHub Actions:**
```bash
# Copy template
mkdir -p .github/workflows
cp .dev-aid/automation/ci-cd/github-actions-security.yml .github/workflows/security.yml

# Commit and push
git add .github/workflows/security.yml
git commit -m "ci: Add security scanning workflow"
git push
```

**For GitLab CI:**
```bash
# Copy template to project root
cp .dev-aid/automation/ci-cd/gitlab-ci-security.yml .gitlab-ci.yml

# Commit and push
git add .gitlab-ci.yml
git commit -m "ci: Add security scanning"
git push
```

### 4. Test the Automation

```bash
# Create a test commit (should trigger pre-commit hook)
echo "test" > test.txt
git add test.txt
git commit -m "test: Verify hooks work"

# Try to push (should trigger pre-push hook)
git push
```

---

## Architecture

### Directory Structure

```
dev-aid/.dev-aid/
├── automation/
│   ├── tools/
│   │   └── install-security-tools.sh   # Tool installer
│   ├── git-hooks/
│   │   ├── pre-commit                  # Fast checks
│   │   ├── pre-push                    # Thorough checks
│   │   └── install.sh                  # Hook installer
│   └── ci-cd/
│       ├── github-actions-security.yml # GitHub Actions template
│       └── gitlab-ci-security.yml      # GitLab CI template
├── docs/
│   ├── AUTOMATION-GUIDE.md             # This file
│   └── SECURITY-TOOLS-REFERENCE.md     # Tool reference
└── providers/
    └── claude/.claude/
        └── commands/
            ├── security/
            │   ├── aid-audit.md
            │   └── aid-vulnerability-scan.md
            ├── operations/
            │   └── aid-deploy-validate.md
            └── quality/
                ├── aid-code-health.md
                └── aid-debt-analysis.md
```

### Security Tool Stack

| Layer | Tool | Purpose | When |
|-------|------|---------|------|
| **SAST** | Opengrep | Code vulnerability scanning | All tiers |
| **Secrets** | Gitleaks | API keys, passwords, tokens | All tiers |
| **Dependencies** | Trivy | CVE scanning in dependencies | All tiers |
| **Containers** | Trivy | Docker image scanning | Tier 3 (CI/CD) |
| **Dockerfile** | Hadolint | Dockerfile best practices | Tier 2 & 3 |
| **IaC** | Checkov | Terraform, K8s, etc. | Tier 3 (CI/CD) |

---

## Git Hooks

### Pre-Commit Hook

**Purpose:** Catch critical issues before commit (~10 seconds)

**What it does:**
1. **Secret Scanning** - Gitleaks (staged files only, no git history)
2. **SAST** - Opengrep (ERROR severity only, 5s timeout)
3. **Dependencies** - Trivy (CRITICAL severity only)

**Output:**
```bash
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PRE-COMMIT] Running fast security checks...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[PRE-COMMIT] 1/3 Scanning for secrets...
[PRE-COMMIT] ✓ No secrets found

[PRE-COMMIT] 2/3 Scanning code for critical vulnerabilities...
[PRE-COMMIT] ✓ No critical vulnerabilities found

[PRE-COMMIT] 3/3 Scanning dependencies for critical CVEs...
[PRE-COMMIT] ✓ No critical CVEs found

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PRE-COMMIT] ✓ All checks passed! (8s)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Bypass:**
```bash
# If you need to commit anyway (use sparingly!)
git commit --no-verify -m "WIP: Temporary commit"
```

---

### Pre-Push Hook

**Purpose:** Thorough checks before pushing (~60 seconds)

**What it does:**
1. **Secret Scanning** - Gitleaks (full scan including git history)
2. **SAST** - Opengrep (all severities, comprehensive rules)
3. **Dependencies** - Trivy (HIGH + CRITICAL severities)
4. **Dockerfile** - Hadolint (if Dockerfile exists)
5. **IaC Preview** - Basic checks (full scan in CI/CD)

**Output:**
```bash
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PRE-PUSH] Running comprehensive security checks...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[PRE-PUSH] 1/5 Scanning for secrets (including git history)...
[PRE-PUSH] ✓ No secrets found

[PRE-PUSH] 2/5 Running static code analysis...
[PRE-PUSH] ⚠️  3 warning(s) found
[PRE-PUSH] Run: opengrep scan --config=auto . | less

[PRE-PUSH] 3/5 Scanning dependencies for vulnerabilities...
[PRE-PUSH] ⚠️  2 high severity CVEs found
[PRE-PUSH] Run: trivy fs --scanners vuln --severity HIGH,CRITICAL .

[PRE-PUSH] 4/5 Scanning Dockerfile...
[PRE-PUSH] ✓ Dockerfile looks good

[PRE-PUSH] 5/5 No IaC files found (skipping)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[PRE-PUSH] ✓ No critical issues (5 warnings) (52s)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Bypass:**
```bash
# If you need to push anyway
git push --no-verify
```

---

## CI/CD Integration

### GitHub Actions

**Features:**
- ✅ Runs on: PR, push to main/master/develop, manual trigger, weekly schedule
- ✅ Uploads SARIF to GitHub Security tab
- ✅ Creates security summary in PR
- ✅ Uploads artifacts (reports) for 30 days
- ✅ Fails build on critical issues

**Setup:**
```bash
# Copy template
mkdir -p .github/workflows
cp .dev-aid/automation/ci-cd/github-actions-security.yml .github/workflows/security.yml

# Customize (optional)
vim .github/workflows/security.yml

# Commit and push
git add .github/workflows/security.yml
git commit -m "ci: Add security scanning"
git push
```

**View Results:**
1. Go to GitHub repo → Actions tab
2. Click on the latest workflow run
3. View security summary
4. Check "Security" tab for SARIF findings

---

### GitLab CI

**Features:**
- ✅ Native GitLab Security Dashboard integration
- ✅ SAST, Dependency Scanning, Container Scanning reports
- ✅ Merge Request widgets show security status
- ✅ Artifacts stored for 30 days

**Setup:**
```bash
# Copy template
cp .dev-aid/automation/ci-cd/gitlab-ci-security.yml .gitlab-ci.yml

# Or append to existing .gitlab-ci.yml
cat .dev-aid/automation/ci-cd/gitlab-ci-security.yml >> .gitlab-ci.yml

# Commit and push
git add .gitlab-ci.yml
git commit -m "ci: Add security scanning"
git push
```

**View Results:**
1. Go to GitLab project → CI/CD → Pipelines
2. Click on latest pipeline
3. View security reports in Merge Request
4. Check Security & Compliance → Vulnerability Report

---

## Security Tools

See [SECURITY-TOOLS-REFERENCE.md](./SECURITY-TOOLS-REFERENCE.md) for detailed documentation on:

- **Opengrep** - SAST (Static Application Security Testing)
- **Gitleaks** - Secret scanning
- **Trivy** - Dependencies, containers, IaC
- **Hadolint** - Dockerfile linting
- **Checkov** - Infrastructure-as-Code scanning

---

## Configuration

### Customizing Git Hooks

Edit hooks in `.dev-aid/automation/git-hooks/`:

**Example: Reduce pre-commit timeout**
```bash
# Edit pre-commit
vim .dev-aid/automation/git-hooks/pre-commit

# Change timeout from 5s to 3s
opengrep scan --config=auto --severity ERROR --timeout 3 .

# Reinstall hooks
./.dev-aid/automation/git-hooks/install.sh
```

**Example: Add language-specific checks**
```bash
# Add to pre-commit hook
if [ -f "package.json" ]; then
  npm run lint || true
fi
```

---

### Tool Configuration Files

**Gitleaks** - Create `.gitleaks.toml`:
```toml
title = "Dev-AID Gitleaks Config"

[allowlist]
description = "Allowlist for false positives"
paths = [
    ".*test.*",
    ".*mock.*",
    ".*.example"
]

regexes = [
    # Allow test API keys
    "test-api-key-.*"
]
```

**Opengrep** - Create `.opengrep.yml`:
```yaml
rules:
  - id: sql-injection-check
    pattern: db.execute($USER_INPUT)
    message: Potential SQL injection
    severity: ERROR
    languages: [python, javascript]

  - id: hardcoded-secret
    pattern: password = "..."
    message: Hardcoded password
    severity: ERROR
```

**Trivy** - Create `trivy.yaml`:
```yaml
severity:
  - CRITICAL
  - HIGH

scan:
  skip-dirs:
    - node_modules
    - .git
    - vendor
    - .venv

vulnerability:
  type:
    - os
    - library
```

**Hadolint** - Create `.hadolint.yaml`:
```yaml
ignored:
  - DL3008  # Pin versions in apt-get (if you want flexible versions)
  - DL3009  # Delete apt cache (if using multi-stage builds)

trustedRegistries:
  - docker.io
  - gcr.io
```

**Checkov** - Create `.checkov.yml`:
```yaml
framework:
  - terraform
  - kubernetes

skip-check:
  - CKV_AWS_20  # S3 public access (if intentional)
  - CKV_K8S_8   # Liveness probe (if not applicable)
```

---

## Best Practices

### 1. Developer Workflow

**Recommended flow:**
```bash
# 1. Work on feature
vim src/auth.ts

# 2. Run tests locally (optional but recommended)
npm test

# 3. Stage changes
git add src/auth.ts

# 4. Commit (pre-commit hook runs automatically)
git commit -m "feat: Add OAuth authentication"
# → Hook runs (~10s), blocks if critical issues

# 5. Push (pre-push hook runs automatically)
git push
# → Hook runs (~60s), blocks if critical issues

# 6. Create PR
# → CI/CD runs full scan (~3-5 min)

# 7. Merge after CI passes
```

---

### 2. Handling False Positives

**Gitleaks false positive:**
```bash
# Add to .gitleaks.toml
[allowlist]
paths = ["tests/fixtures/mock-data.json"]
```

**Opengrep false positive:**
```bash
# Inline suppression
password = get_password()  # nosemgrep: hardcoded-password

# Or in .opengrep.yml
paths:
  exclude:
    - "tests/**"
```

**Trivy false positive:**
```bash
# Create .trivyignore
CVE-2024-12345  # False positive, see issue #123
```

**Checkov false positive:**
```bash
# Inline suppression
#checkov:skip=CKV_AWS_20:Intentionally public S3 bucket
```

---

### 3. Optimizing Hook Performance

**If pre-commit is too slow:**
```bash
# Option 1: Scan only staged files
git diff --cached --name-only | grep '\.py$' | xargs opengrep scan --config=auto

# Option 2: Reduce timeout
opengrep scan --config=auto --timeout 3 .

# Option 3: Skip some checks locally (not recommended)
git commit --no-verify
```

**If pre-push is too slow:**
```bash
# Option 1: Run thorough checks only in CI
# (Remove or simplify pre-push hook)

# Option 2: Skip DB updates
trivy fs --skip-db-update .
```

---

### 4. Team Adoption

**Make adoption smooth:**

1. **Gradual rollout:**
   ```bash
   # Week 1: Install tools, no enforcement
   # Week 2: Add pre-commit (warnings only)
   # Week 3: Add pre-push (warnings only)
   # Week 4: Enforce all checks
   ```

2. **Document bypass procedure:**
   ```markdown
   # When to use --no-verify:
   - Emergency hotfix (document in commit message)
   - Work-in-progress commit (will fix before push)
   - False positive (document and fix config)

   # When NOT to use --no-verify:
   - "I don't want to fix the issue" ❌
   - "It's taking too long" ❌
   ```

3. **Provide training:**
   - Share this guide with team
   - Walk through common scenarios
   - Set up pairing sessions for first week

---

## Troubleshooting

### Hooks not running

**Problem:** Git hooks don't execute

**Solutions:**
```bash
# 1. Check if hooks are installed
ls -la .git/hooks/pre-commit .git/hooks/pre-push

# 2. Check permissions
chmod +x .git/hooks/pre-commit .git/hooks/pre-push

# 3. Reinstall hooks
./.dev-aid/automation/git-hooks/install.sh

# 4. Check if hooks are enabled
git config core.hooksPath  # Should be empty or point to .git/hooks
```

---

### Tools not found

**Problem:** `command not found: opengrep`

**Solutions:**
```bash
# 1. Check if tools are installed
which opengrep gitleaks trivy

# 2. Install missing tools
./.dev-aid/automation/tools/install-security-tools.sh

# 3. Add to PATH
export PATH="$HOME/.dev-aid/bin:$PATH"

# 4. Reload shell
source ~/.bashrc  # or ~/.zshrc
```

---

### Slow performance

**Problem:** Hooks take too long

**Solutions:**
```bash
# 1. Measure individual tools
time opengrep scan --config=auto --timeout 5 .
time gitleaks detect --no-git
time trivy fs --scanners vuln --severity CRITICAL .

# 2. Skip DB updates (Trivy)
trivy fs --skip-db-update .

# 3. Reduce scan scope
opengrep scan --config=auto src/  # Only src directory

# 4. Use faster configs
opengrep scan --config=p/security-audit --timeout 3 .
```

---

### CI/CD failures

**Problem:** CI pipeline fails but local hooks pass

**Solutions:**
```bash
# 1. Run same commands locally as CI
opengrep scan --config=auto --sarif --output report.sarif .
trivy fs --scanners vuln --severity HIGH,CRITICAL .

# 2. Check tool versions
opengrep --version  # Should match CI
trivy --version

# 3. Update local tools
./.dev-aid/automation/tools/install-security-tools.sh

# 4. Check CI logs for specific failures
# GitHub: Actions tab → Click on failed run
# GitLab: CI/CD → Pipelines → Click on failed job
```

---

## FAQ

**Q: Can I disable specific tools?**
```bash
# Yes, edit the hook files and comment out tools you don't need
vim .dev-aid/automation/git-hooks/pre-commit
```

**Q: How do I update tools?**
```bash
# Rerun the installer
./.dev-aid/automation/tools/install-security-tools.sh
```

**Q: Can I use different tools?**
```bash
# Yes, edit hooks and add your preferred tools
vim .dev-aid/automation/git-hooks/pre-commit
# Add: snyk test || true
```

**Q: What if a tool has a bug?**
```bash
# Skip that specific tool temporarily
# Option 1: Edit hook file, comment out the tool
# Option 2: Use --no-verify (not recommended)
```

**Q: How do I see detailed reports?**
```bash
# All tools support JSON/SARIF output
gitleaks detect --report-path report.json
opengrep scan --config=auto --json --output report.json .
trivy fs --format json --output report.json .
```

---

## Next Steps

1. ✅ Install tools: `./.dev-aid/automation/tools/install-security-tools.sh`
2. ✅ Install hooks: `./.dev-aid/automation/git-hooks/install.sh`
3. ✅ Set up CI/CD: Copy template from `.dev-aid/automation/ci-cd/`
4. ✅ Customize configs: Create tool config files as needed
5. ✅ Train team: Share this guide and walk through examples
6. ✅ Monitor and iterate: Review findings weekly, tune configs

---

## Resources

- **Opengrep:** [GitHub](https://github.com/opengrep/opengrep) | [Docs](https://www.opengrep.dev/)
- **Gitleaks:** [GitHub](https://github.com/gitleaks/gitleaks)
- **Trivy:** [GitHub](https://github.com/aquasecurity/trivy) | [Docs](https://aquasecurity.github.io/trivy/)
- **Hadolint:** [GitHub](https://github.com/hadolint/hadolint)
- **Checkov:** [GitHub](https://github.com/bridgecrewio/checkov) | [Docs](https://www.checkov.io/)

---

**Questions or issues?** Open an issue in the Dev-AID repository or consult the [Security Tools Reference](./SECURITY-TOOLS-REFERENCE.md).
