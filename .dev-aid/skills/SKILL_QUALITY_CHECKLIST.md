# Skill Development Quality Checklist

Add this section to all skill templates to prevent CI failures and ensure code quality.

## Pre-Implementation Checklist

### 1. Development Environment Setup
```bash
# Install pre-commit hooks
pre-commit install

# Install linters locally
pip install black isort flake8 mypy bandit
brew install shellcheck  # or apt-get install shellcheck
```

### 2. Dependency Management
- [ ] Use exact version pins (==) in requirements.txt
- [ ] Test dependency installation in clean venv
- [ ] Verify compatibility with existing dependencies
- [ ] Document version constraints and why they exist
- [ ] Never manually pin transitive dependencies (let pip resolve)

**Example:**
```python
# ✅ Good - Direct dependencies only
anthropic==0.75.0  # Compatible with httpx 0.28+
httpx==0.28.1      # Modern HTTP client

# ❌ Bad - Manually pinning transitive deps
urllib3==2.2.3     # Let pip resolve this
certifi==2024.8.30 # Let pip resolve this
```

### 3. Code Quality Gates (Run BEFORE committing)
```bash
# Python code
black .                          # Format
isort .                          # Sort imports
flake8 . --max-line-length=120   # Lint
mypy . --ignore-missing-imports  # Type check

# Bash scripts
shellcheck **/*.sh               # Lint all shell scripts

# Security
bandit -r .                      # Security scan
```

### 4. Security Validation
- [ ] Input validation for all external inputs
- [ ] Path traversal prevention (realpath + containment check)
- [ ] Command injection prevention (no shell=True, parameterized commands)
- [ ] Template injection detection (if using templates)
- [ ] API key/secret validation and sanitization in error messages

**Template:**
```python
def validate_safe_path(filepath: str, base_dir: str) -> Path:
    """Prevent path traversal attacks"""
    resolved = Path(filepath).resolve()
    base = Path(base_dir).resolve()

    if not str(resolved).startswith(str(base)):
        raise ValueError("Path traversal detected")

    return resolved
```

### 5. Test Coverage Requirements
- [ ] Write tests BEFORE implementation (TDD)
- [ ] Unit tests for all public functions
- [ ] Edge case tests (empty, null, max values, unicode)
- [ ] Security tests (injection, traversal, overflow)
- [ ] Integration tests for critical paths
- [ ] Minimum 80% code coverage

**Test Template:**
```python
import pytest

class TestFeature:
    def test_happy_path(self):
        """Normal operation"""
        pass

    def test_edge_case_empty(self):
        """Handle empty input"""
        pass

    def test_edge_case_null(self):
        """Handle None/null"""
        pass

    def test_security_injection(self):
        """Prevent injection attacks"""
        pass

    def test_error_handling(self):
        """Graceful error handling"""
        pass
```

### 6. Documentation Requirements
- [ ] Docstrings for all public functions/classes
- [ ] Security considerations documented
- [ ] Examples of correct usage
- [ ] Known limitations documented
- [ ] Update TESTING.md with new test info

## Pre-Commit Automation

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.8.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 7.1.1
    hooks:
      - id: flake8
        args: [--max-line-length=120, --extend-ignore=E203,W503]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-yaml
      - id: check-json
      - id: check-merge-conflict
      - id: trailing-whitespace
      - id: end-of-file-fixer

  - repo: https://github.com/koalaman/shellcheck-precommit
    rev: v0.9.0
    hooks:
      - id: shellcheck
```

## CI/CD Pipeline Checklist

Ensure your CI pipeline includes:
- [ ] Dependency installation test (clean environment)
- [ ] Python linting (black, isort, flake8)
- [ ] Bash linting (shellcheck)
- [ ] Type checking (mypy)
- [ ] Unit tests with coverage
- [ ] Security scanning (bandit, safety)
- [ ] Integration tests

## Common Pitfalls to Avoid

### Python
❌ **Don't:**
```python
import os  # unused import
except Exception as e:  # unused variable
f"string without {placeholders}"  # empty f-string
```

✅ **Do:**
```python
# Only import what you use
except Exception:  # or use: except Exception as ex
"string without placeholders"  # regular string
```

### Bash
❌ **Don't:**
```bash
local var="value"  # at script level (not in function)
echo "$15/month"   # interpreted as positional param
if [[ "$x" =~ [<>] ]]; then  # unescaped in regex
```

✅ **Do:**
```bash
var="value"  # at script level
echo "\$15/month"  # escape dollar sign
if [[ "$x" =~ [\<\>] ]]; then  # escape in regex
```

### Dependencies
❌ **Don't:**
```txt
httpx>=0.26  # unpinned, could break
urllib3==2.6.0  # manually pinning transitive dep
```

✅ **Do:**
```txt
httpx==0.28.1  # exact pin with reason
# Let pip resolve: urllib3, certifi, etc
```

## Skill Template Addition

Add this section to your skill templates:

```markdown
## Quality Assurance Checklist

Before submitting this skill:
- [ ] All pre-commit hooks pass
- [ ] Dependencies tested in clean venv
- [ ] Code coverage >80%
- [ ] Security scan clean (bandit)
- [ ] shellcheck passes (if bash scripts)
- [ ] Documentation complete
- [ ] Tests cover edge cases
```

## Skills Enhancement Validation

### Scripts (Process Skills)
- [ ] Scripts pass `shellcheck` with no errors
- [ ] Scripts use standard exit codes (0=pass, 1=fail, 2=warn)
- [ ] Scripts are based on `template-references/script-template.sh`
- [ ] Scripts are executable (`chmod +x`)

### Rollback (Process Skills)
- [ ] `## Rollback Procedures` section present in SKILL.md
- [ ] Rollback triggers documented
- [ ] Specific undo steps provided
- [ ] Reset-to-clean-state instructions included

### Performance Notes (Expert Skills)
- [ ] Performance reference line present at end of SKILL.md
- [ ] Links to `template-references/performance-notes.md`

### Compatibility (Tool-Specific Skills)
- [ ] `compatibility:` field present in frontmatter where applicable
- [ ] Version requirements are specific (e.g., `Python 3.11+` not just `Python`)

### Assets (Document-Generating Skills)
- [ ] `assets/` directory exists with relevant templates
- [ ] Templates use placeholders (`[...]`) for customization
- [ ] SKILL.md references the assets directory

## Automation Recommendations

1. **GitHub Actions Template** - Pre-configured CI for all repos
2. **Pre-commit Hook Template** - One command setup
3. **Skill Scaffolding Tool** - Generate skills with quality checks built-in
4. **Dependency Lock File** - requirements.lock for reproducible builds

## Summary

The issues weren't about insecure code, but rather:
1. **Process gaps** - No automated quality gates
2. **Technical debt** - Code quality issues accumulated
3. **Dependency hygiene** - Version management not strict enough
4. **Testing discipline** - Tests written after code, not before

**Fix:** Shift left - catch issues at development time, not in CI.
