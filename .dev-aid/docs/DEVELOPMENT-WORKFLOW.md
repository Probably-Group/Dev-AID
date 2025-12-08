# Development Workflow Guide

Ensuring all PR checks pass locally before pushing to avoid CI failures.

## Quick Start

### Option 1: Automated (Recommended) - Git Hooks

Set up once, runs automatically on every commit:

```bash
# One-time setup
./.dev-aid/scripts/setup-git-hooks.sh

# Now every commit automatically runs:
# ✓ Black formatting
# ✓ Flake8 linting
# ✓ MyPy type checking
# ✓ Pytest with coverage
# ✓ Shellcheck (for bash scripts)
```

**Benefits:**
- ✅ Can't forget to run checks
- ✅ Catches issues immediately
- ✅ Fast feedback loop
- ✅ Prevents broken commits

**To bypass** (not recommended):
```bash
git commit --no-verify
```

### Option 2: Manual - Run Before Push

Run all checks manually before pushing:

```bash
# From repo root
./.dev-aid/scripts/run-pr-checks.sh

# Or from orchestration directory
cd .dev-aid/orchestration
make check
```

### Option 3: Quick Fix - Makefile Commands

Use Makefile for common tasks:

```bash
cd .dev-aid/orchestration

# Auto-fix formatting issues
make format

# Run all checks
make check

# Auto-fix + check
make fix
make check

# Just run tests
make test
```

## Detailed Workflow

### 1. Before Starting Work

```bash
# Update dependencies
cd .dev-aid/orchestration
./setup-venv.sh

# Setup git hooks (if not done yet)
../../scripts/setup-git-hooks.sh
```

### 2. During Development

```bash
# Auto-format code as you work
make format

# Run tests frequently
make test

# Check types
make lint
```

### 3. Before Committing

**With git hooks (automatic):**
```bash
git add .
git commit -m "your message"
# Hook runs automatically, commit fails if checks fail
```

**Without git hooks (manual):**
```bash
# Run all checks
make check

# If checks pass
git add .
git commit -m "your message"
```

### 4. Before Pushing

```bash
# Final safety check (optional but recommended)
./.dev-aid/scripts/run-pr-checks.sh

# If all pass
git push origin your-branch
```

## Common Issues & Fixes

### Black Formatting Failures

**Error:**
```
would reformat /path/to/file.py
```

**Fix:**
```bash
cd .dev-aid/orchestration
make format
# Or manually:
black .
```

### Flake8 Linting Failures

**Error:**
```
router/file.py:42:1: F401 'module' imported but unused
```

**Fix:** Manually remove unused imports/variables
```bash
# Check what needs fixing
flake8 . --max-line-length=120 --extend-ignore=E203,W503

# Common issues:
# F401 - Unused import → Remove it
# F841 - Unused variable → Remove it or prefix with _
# E501 - Line too long → Break into multiple lines
```

### MyPy Type Checking Failures

**Error:**
```
router/file.py:42: error: Missing return statement
```

**Fix:** Add type hints or fix type errors
```bash
# Check errors
mypy router --ignore-missing-imports --no-strict-optional
```

### Test Failures

**Error:**
```
FAILED tests/test_file.py::test_function - AssertionError
```

**Fix:** Debug and fix the test
```bash
# Run specific test for debugging
pytest tests/test_file.py::test_function -v

# Run with more output
pytest tests/test_file.py -vv -s
```

### Coverage Too Low

**Error:**
```
FAIL Required test coverage of 59% not reached. Total coverage: 58%
```

**Fix:** Add more tests or exclude untestable code
```bash
# See what's not covered
pytest tests/ --cov=router --cov-report=html
open htmlcov/index.html

# Exclude from coverage (pyproject.toml)
[tool.coverage.run]
omit = [
    "router/cli.py",  # CLI entry points hard to test
]
```

## IDE Integration

### VS Code

Install extensions:
- **Python** (Microsoft)
- **Pylance** (Microsoft)
- **Black Formatter** (Microsoft)

Add to `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": ".dev-aid/orchestration/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.flake8Args": [
    "--max-line-length=120",
    "--extend-ignore=E203,W503"
  ],
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": [
    "--line-length=100"
  ],
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": [
    "tests"
  ]
}
```

### PyCharm / IntelliJ

1. **File → Settings → Tools → External Tools**
2. Add tool:
   - Name: "Run PR Checks"
   - Program: `$ProjectFileDir$/.dev-aid/scripts/run-pr-checks.sh`
3. **Tools → Run PR Checks** (before committing)

## CI/CD Pipeline

Our GitHub Actions workflow runs these checks:

1. **Python Lint**:
   - Black formatting check
   - Flake8 linting

2. **Python Unit Tests**:
   - Pytest with coverage (59%+ required)

3. **Type Check**:
   - MyPy static type checking

4. **Bash Lint**:
   - Shellcheck for bash scripts

**All of these are replicated in local tools** so you can catch issues before pushing.

## Best Practices

### ✅ DO

- **Set up git hooks** - automates everything
- **Run `make check`** before pushing
- **Auto-format frequently** with `make format`
- **Run tests while developing** with `make test`
- **Fix issues immediately** while context is fresh

### ❌ DON'T

- **Skip local checks** - CI will catch them anyway (wastes time)
- **Use `--no-verify`** unless absolutely necessary
- **Batch many changes** - small commits are easier to fix
- **Ignore warnings** - they often become errors later

## Troubleshooting

### Hook doesn't run

```bash
# Reinstall hooks
./.dev-aid/scripts/setup-git-hooks.sh

# Check hook exists and is executable
ls -la .git/hooks/pre-commit
```

### Venv not activated

```bash
# Manual activation
cd .dev-aid/orchestration
source venv/bin/activate

# Or recreate venv
./setup-venv.sh
```

### Make command not found

```bash
# Install make (macOS)
brew install make

# Install make (Linux)
sudo apt install make

# Or run pytest directly
pytest tests/ -v
```

## Advanced: Custom Checks

Add your own checks to pre-commit hook:

```bash
# Edit .git/hooks/pre-commit
# Add before the "All checks passed" line:

# Custom check example
echo "  → Custom security scan..."
bandit -r router/ -ll || {
    echo "❌ Security scan failed!"
    exit 1
}
```

## Summary

**Recommended Setup:**
```bash
# One-time setup
./.dev-aid/scripts/setup-git-hooks.sh
cd .dev-aid/orchestration && ./setup-venv.sh

# Daily workflow
# 1. Code
# 2. make format (auto-fix)
# 3. git commit (hooks run automatically)
# 4. git push

# If hooks disabled
make check  # Before push
```

This ensures all PR checks pass locally before CI runs, saving time and avoiding broken builds! 🚀
