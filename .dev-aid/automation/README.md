# Dev-AID Automation

Automated security and quality checks for your development workflow.

## Quick Start

```bash
# 1. Install security tools
./tools/install-security-tools.sh

# 2. Install git hooks
./git-hooks/install.sh

# 3. Set up CI/CD (optional)
# Copy github-actions-security.yml to .github/workflows/
# OR copy gitlab-ci-security.yml to .gitlab-ci.yml
```

## Directory Structure

```
automation/
├── tools/
│   └── install-security-tools.sh    # Installs Gitleaks, Trivy, Opengrep
├── git-hooks/
│   ├── pre-commit                   # Fast checks (~10s)
│   ├── pre-push                     # Thorough checks (~60s)
│   └── install.sh                   # Hook installer
└── ci-cd/
    ├── github-actions-security.yml  # GitHub Actions template
    └── gitlab-ci-security.yml       # GitLab CI template
```

## Security Tools

| Tool | Purpose | Scan Types |
|------|---------|------------|
| **Gitleaks** | Secret scanning | Git history + current files |
| **Trivy** | Multi-scanner | CVE, Misconfig, Secrets (deps, Dockerfiles, IaC) |
| **Opengrep** | SAST (340+ rules) | OWASP Top 10, CWE Top 25, CI/CD security |

## Automation Tiers

### Tier 1: Pre-Commit (~10s)
- ✅ Secrets scan (Gitleaks)
- ✅ Critical code issues (Opengrep)
- ✅ Critical CVEs (Trivy)

### Tier 2: Pre-Push (~60s)
- ✅ Full secret scan + git history
- ✅ Complete SAST scan (340+ rules)
- ✅ CVE + Misconfig scan (HIGH + CRITICAL)

### Tier 3: CI/CD (~3-5 min)
- ✅ All above checks
- ✅ Full misconfig scan (Dockerfiles, IaC)
- ✅ License compliance
- ✅ SBOM generation (CycloneDX + SPDX)

## Documentation

- **[Automation Guide](../docs/AUTOMATION-GUIDE.md)** - Complete setup and usage guide
- **[Security Tools Reference](../docs/SECURITY-TOOLS-REFERENCE.md)** - Detailed tool documentation

## Bypass Hooks

```bash
# Pre-commit
git commit --no-verify

# Pre-push
git push --no-verify
```

**Use sparingly!** Only for emergencies or work-in-progress commits.

## Troubleshooting

**Hooks not running?**
```bash
# Reinstall hooks
./git-hooks/install.sh
```

**Tools not found?**
```bash
# Reinstall tools
./tools/install-security-tools.sh

# Add to PATH
export PATH="$HOME/.dev-aid/bin:$PATH"
```

**Hooks too slow?**
```bash
# Edit hooks to reduce scope or timeout
vim git-hooks/pre-commit
vim git-hooks/pre-push
```

## Next Steps

1. Read [AUTOMATION-GUIDE.md](../docs/AUTOMATION-GUIDE.md) for comprehensive documentation
2. Configure tools as needed (see guide for config examples)
3. Set up CI/CD using templates in `ci-cd/` directory
4. Train your team on the automation workflow
