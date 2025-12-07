# Dependency Update Guide

This guide explains how to safely update pinned dependencies in the Dev-AID orchestration layer.

## Table of Contents
1. [Why Dependencies Are Pinned](#why-dependencies-are-pinned)
2. [When to Update](#when-to-update)
3. [Update Procedure](#update-procedure)
4. [Testing After Updates](#testing-after-updates)
5. [Emergency Updates](#emergency-updates)

---

## Why Dependencies Are Pinned

All dependencies in `requirements.txt` are pinned to **exact versions** (using `==`) for:

### Security
- **Supply chain protection**: Prevents automatic installation of compromised packages
- **Known vulnerabilities**: Easier to track which specific versions have CVEs
- **Audit trail**: Clear record of what code is running in production

### Stability
- **Reproducible builds**: Same code produces identical environments
- **No surprises**: Breaking changes don't automatically propagate
- **Predictable behavior**: Easier to debug issues when versions don't change

### Example
```txt
# ✅ GOOD: Pinned version
anthropic==0.39.0

# ❌ BAD: Loose constraint (allows breaking changes)
anthropic>=0.39.0

# ❌ BAD: Version range (unpredictable)
anthropic>=0.39.0,<1.0.0
```

---

## When to Update

### Scheduled Updates (Quarterly)
Review all dependencies every 3 months:
- Check for new releases
- Review changelogs
- Test compatibility
- Update if beneficial

### Security Updates (Immediate)
Update immediately when:
- CVE published for current version
- `pip-audit` or `safety check` reports vulnerability
- Security advisory from package maintainer
- Upstream fix for critical bug

### Feature Updates (As Needed)
Update when:
- New feature required for Dev-AID
- Performance improvement available
- Bug fix needed
- Better API available

---

## Update Procedure

### Step 1: Create Isolated Environment

```bash
# Navigate to orchestration directory
cd .dev-aid/orchestration

# Create test virtual environment
python3 -m venv venv-test
source venv-test/bin/activate

# Install current dependencies
pip install -r requirements.txt
```

### Step 2: Check for Updates

```bash
# Show outdated packages
pip list --outdated

# Example output:
# Package                Version   Latest    Type
# ---------------------- --------- --------- -----
# anthropic              0.39.0    0.40.0    wheel
# pydantic               2.10.3    2.11.0    wheel
```

### Step 3: Research Changes

Before updating, review:

#### Changelog
```bash
# View package homepage
pip show anthropic | grep Home-page

# Check GitHub releases
# Example: https://github.com/anthropics/anthropic-sdk-python/releases
```

#### Breaking Changes
Look for:
- Major version bumps (e.g., `2.x.x` → `3.0.0`)
- Deprecated APIs
- Changed behavior
- New requirements

#### Security Advisories
```bash
# Check for vulnerabilities in new version
pip-audit --desc
safety check --json
```

### Step 4: Update One Package at a Time

```bash
# Update single package
pip install --upgrade anthropic==0.40.0

# Generate new requirements
pip freeze > requirements-test.txt

# Edit requirements-test.txt to include only direct dependencies
# (Remove transitive dependencies to avoid version conflicts)
```

### Step 5: Run Full Test Suite

```bash
# Run all tests
pytest tests/ -v

# Run security tests
pytest tests/test_security.py -v

# Run coverage check
pytest tests/ --cov=router --cov-fail-under=80

# Run static analysis
bandit -r router/ -ll
mypy router/ --strict --ignore-missing-imports

# Run code quality checks
black --check router/ tests/
isort --check router/ tests/
flake8 router/ --max-line-length=100
```

### Step 6: Manual Testing

Test critical functionality:

```bash
# Test AI provider connections
python -c "from router.api_clients import AnthropicClient; print('✓ Anthropic import OK')"

# Test configuration loading
python -c "from router.config_loader import ConfigLoader; print('✓ Config import OK')"

# Test validators
python -c "from router.validators import ExecuteRequest; print('✓ Validators OK')"
```

### Step 7: Update requirements.txt

If all tests pass:

```bash
# Backup current requirements
cp requirements.txt requirements.txt.backup

# Update only the changed package(s)
# Edit requirements.txt manually to update version
vim requirements.txt

# Verify it works
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run full test suite again
./run_security_checks.sh
```

### Step 8: Document the Change

Update comments in `requirements.txt`:

```txt
# Updated 2025-12-07: anthropic 0.39.0 → 0.40.0
# Reason: Security fix for CVE-2025-XXXX
# Tested: All tests pass, no breaking changes
anthropic==0.40.0
```

### Step 9: Commit and Test in CI

```bash
git add requirements.txt
git commit -m "chore: update anthropic to 0.40.0 for security fix

- Fixes CVE-2025-XXXX
- Tested locally, all checks pass
- No breaking changes"

git push origin feature/update-deps
```

Wait for CI/CD to run all tests before merging.

---

## Testing After Updates

### Automated Tests
```bash
# Quick verification
pytest tests/ -v --tb=short

# Full security suite
./run_security_checks.sh
```

### Manual Verification Checklist

- [ ] Dev-AID router starts without errors
- [ ] Can connect to Anthropic API
- [ ] Can connect to OpenAI API
- [ ] Can connect to Google Gemini API
- [ ] MCP servers can be loaded
- [ ] Context building works
- [ ] Cost tracking functional
- [ ] All modes work (solo, ensemble, challenger)
- [ ] Configuration files load correctly
- [ ] Validators reject malicious inputs
- [ ] No new security warnings

---

## Emergency Updates

For critical security vulnerabilities:

### Fast Track Procedure

```bash
# 1. Create hotfix branch
git checkout -b hotfix/cve-2025-xxxx

# 2. Update vulnerable package
vim requirements.txt  # Change version

# 3. Quick test
source venv/bin/activate
pip install -r requirements.txt
pytest tests/test_security.py -v  # Security tests only

# 4. Deploy immediately
git commit -m "security: emergency update for CVE-2025-XXXX"
git push origin hotfix/cve-2025-xxxx

# 5. Create PR and merge immediately
gh pr create --title "Security: Fix CVE-2025-XXXX" --body "Emergency security update"
```

### Skip These (Only for Emergencies)
- ⚠️ Full test suite (run security tests only)
- ⚠️ Manual testing (verify core functionality only)
- ⚠️ Code review (single approver sufficient)

### Don't Skip These (Even in Emergencies)
- ✅ Security tests (`test_security.py`)
- ✅ Vulnerability scan (`pip-audit`)
- ✅ Syntax validation (`python -m py_compile`)

---

## Common Issues

### Dependency Conflicts

**Problem**: Two packages require incompatible versions of a shared dependency.

**Solution**:
```bash
# Use pip's dependency resolver
pip install --upgrade --upgrade-strategy eager anthropic

# Or specify compatible versions manually
pip install anthropic==0.40.0 httpx==0.26.0
```

### Breaking API Changes

**Problem**: New version breaks existing code.

**Solution**:
1. Check migration guide in package changelog
2. Update code to use new API
3. Add compatibility layer if needed
4. Test thoroughly before deploying

**Example**:
```python
# Old API (v1.x)
client.create_message(model="claude-3", prompt="Hello")

# New API (v2.x)
client.messages.create(model="claude-3", messages=[{"role": "user", "content": "Hello"}])
```

### Test Failures After Update

**Problem**: Tests fail with new package version.

**Solution**:
1. Read test failure messages carefully
2. Check if behavior changed legitimately
3. Update tests if new behavior is correct
4. Revert update if behavior is broken
5. Report bug to package maintainer

---

## Rollback Procedure

If update causes issues in production:

```bash
# 1. Revert to backup
cp requirements.txt.backup requirements.txt

# 2. Reinstall old versions
pip install --force-reinstall -r requirements.txt

# 3. Verify functionality
./run_security_checks.sh

# 4. Deploy rollback
git revert <commit-hash>
git push origin main
```

---

## Automation (Future)

Consider automating dependency updates with:

### Dependabot (GitHub)
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: pip
    directory: "/.dev-aid/orchestration"
    schedule:
      interval: weekly
    open-pull-requests-limit: 5
    reviewers:
      - "@security-team"
```

### Renovate Bot
```json
{
  "extends": ["config:base"],
  "packageRules": [
    {
      "matchUpdateTypes": ["patch", "minor"],
      "automerge": true,
      "requiredStatusChecks": ["tests", "security-scan"]
    }
  ]
}
```

---

## Version Policy

### Semantic Versioning

We follow semantic versioning when updating:

- **Patch** (x.y.**Z**): Bug fixes, security patches → Update immediately if needed
- **Minor** (x.**Y**.z): New features, backwards compatible → Update quarterly
- **Major** (**X**.y.z): Breaking changes → Update when needed, test thoroughly

### Support Policy

- Keep dependencies **within 6 months** of latest stable
- Update **immediately** for security issues
- Test **thoroughly** before major version bumps
- Maintain **compatibility** with Python 3.8+

---

## Resources

- [Pip Documentation](https://pip.pypa.io/en/stable/)
- [pip-audit](https://github.com/pypa/pip-audit)
- [Safety](https://github.com/pyupio/safety)
- [Dependabot](https://docs.github.com/en/code-security/dependabot)
- [Semantic Versioning](https://semver.org/)

---

**Last Updated**: 2025-12-07
**Version**: 1.0.0
