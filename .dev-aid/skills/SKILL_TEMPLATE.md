# [Skill Name]

---
name: skill-name-kebab-case
version: 1.0.0
domain: category/subcategory
risk_level: LOW|MEDIUM|HIGH
languages: [python, typescript, rust, go]
frameworks: [framework1, framework2]
requires_security_review: false
compliance: []
last_updated: YYYY-MM-DD
---

> **MANDATORY**: Read this entire template before creating a new skill. Follow ALL quality checkpoints.

## 1. Overview

### 1.1 Purpose and Scope

Brief description of what this skill does and why it exists.

**Core Capabilities:**
- Capability 1
- Capability 2
- Capability 3

**Out of Scope:**
- What this skill does NOT handle
- When to use a different skill

### 1.2 Risk Assessment

**Risk Level**: [LOW|MEDIUM|HIGH]

**Justification:**
- Why this risk level?
- What are the consequences of failure?

**Attack Surface:**
- Potential security concerns
- Data handling risks
- External dependency risks

## 2. Core Responsibilities

### 2.1 Primary Functions

1. Function 1 - Description
2. Function 2 - Description
3. Function 3 - Description

### 2.2 Core Principles

1. **TDD First** - Write tests BEFORE implementation
2. **Performance Aware** - Consider scalability and efficiency
3. **Security by Default** - Validate inputs, sanitize outputs
4. **Defense in Depth** - Multiple layers of protection

### 2.3 Security Principles

- **NEVER** [anti-pattern 1]
- **NEVER** [anti-pattern 2]
- **ALWAYS** [best practice 1]
- **ALWAYS** [best practice 2]

## 3. Implementation Workflow (TDD)

### Step 1: Setup Development Environment

```bash
# Install pre-commit hooks
pre-commit install

# Create virtual environment (Python) or equivalent
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install linters
pip install black isort flake8 mypy bandit
```

### Step 2: Write Failing Tests First

```python
import pytest

class TestFeatureTDD:
    """TDD tests for [feature]."""

    def test_happy_path(self):
        """Test normal operation."""
        # Given
        # When
        # Then
        pass

    def test_edge_case_empty(self):
        """Test handling of empty input."""
        pass

    def test_edge_case_null(self):
        """Test handling of None/null."""
        pass

    def test_security_injection(self):
        """Test injection attack prevention."""
        pass

    def test_error_handling(self):
        """Test graceful error handling."""
        pass
```

### Step 3: Implement to Pass Tests

```python
def feature_implementation():
    """Implementation with security considerations."""
    pass
```

### Step 4: Refactor and Review

```bash
# Run linters
black .
isort .
flake8 . --max-line-length=120
mypy . --ignore-missing-imports

# Run security scan
bandit -r .

# Run tests with coverage
pytest --cov=. --cov-report=term-missing
```

## 4. Quality Assurance Checklist

### 4.1 Pre-Implementation Setup
- [ ] Virtual environment created and activated
- [ ] Dependencies installed and tested
- [ ] Pre-commit hooks installed (`pre-commit install`)
- [ ] Linters installed (black, isort, flake8, mypy)
- [ ] Security scanner installed (bandit)

### 4.2 Dependency Management
- [ ] All dependencies pinned with exact versions (==)
- [ ] Dependencies tested in clean environment
- [ ] No manual transitive dependency pins
- [ ] requirements.txt includes comments explaining version constraints
- [ ] Compatibility verified with existing project dependencies

**Example requirements.txt:**
```python
# Core dependencies
library-name==1.2.3  # Reason for this version

# DO NOT manually pin transitive dependencies
# Let pip resolve: urllib3, certifi, etc.
```

### 4.3 Code Quality Gates (Run BEFORE committing)
- [ ] `black .` - Code formatted
- [ ] `isort .` - Imports sorted
- [ ] `flake8 . --max-line-length=120` - No linting errors
- [ ] `mypy . --ignore-missing-imports` - Type checking passes
- [ ] `bandit -r .` - Security scan clean
- [ ] No unused imports (F401)
- [ ] No unused variables (F841)
- [ ] No f-strings without placeholders (F541)

### 4.4 Security Validation
- [ ] Input validation for ALL external inputs
- [ ] Path traversal prevention implemented
- [ ] Command injection prevention (no shell=True)
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (output sanitization)
- [ ] API keys/secrets not in code or error messages
- [ ] Authentication/authorization checks in place

**Security Code Template:**
```python
from pathlib import Path

def validate_safe_path(filepath: str, base_dir: str) -> Path:
    """Prevent path traversal attacks."""
    resolved = Path(filepath).resolve()
    base = Path(base_dir).resolve()

    if not str(resolved).startswith(str(base)):
        raise ValueError("Path traversal detected")

    return resolved

def sanitize_input(user_input: str) -> str:
    """Sanitize user input."""
    # Remove shell metacharacters
    dangerous_chars = [';', '|', '&', '$', '`', '(', ')', '<', '>']
    for char in dangerous_chars:
        if char in user_input:
            raise ValueError(f"Invalid character: {char}")

    return user_input.strip()
```

### 4.5 Test Coverage Requirements
- [ ] Tests written BEFORE implementation (TDD)
- [ ] Unit tests for all public functions
- [ ] Edge case tests (empty, null, max values, unicode)
- [ ] Security tests (injection, traversal, overflow)
- [ ] Integration tests for critical paths
- [ ] Code coverage >80%
- [ ] All tests passing
- [ ] No skipped tests without good reason

### 4.6 Bash Script Quality (if applicable)
- [ ] `shellcheck *.sh` passes
- [ ] No SC1037 errors (escaped dollar signs: `\$10`)
- [ ] No SC2168 errors (no `local` at script level)
- [ ] No SC2287 errors (command syntax correct)
- [ ] All variables declared properly
- [ ] Error handling on all commands

**Bash Best Practices:**
```bash
#!/usr/bin/env bash
set -euo pipefail  # Exit on error, undefined vars, pipe failures

# ✅ Good
var="value"  # Script level
echo "\$15/month"  # Escaped dollar
if [[ "$x" =~ [\<\>] ]]; then  # Escaped in regex

# ❌ Bad
local var="value"  # Invalid at script level
echo "$15/month"   # Interpreted as $15 variable
if [[ "$x" =~ [<>] ]]; then  # Unescaped
```

### 4.7 Documentation Requirements
- [ ] Docstrings for all public functions/classes
- [ ] Security considerations documented
- [ ] Examples of correct usage
- [ ] Known limitations documented
- [ ] TESTING.md updated with test info
- [ ] References to related skills

### 4.8 CI/CD Readiness
- [ ] GitHub Actions workflow configured
- [ ] All CI checks pass locally
- [ ] No hardcoded paths or environment assumptions
- [ ] Cross-platform compatibility verified (if applicable)

## 5. Common Pitfalls to Avoid

### Python
```python
# ❌ BAD
import os  # unused import
f"string without {placeholders}"  # empty f-string
except Exception as e:  # unused variable e

# ✅ GOOD
# Only import what you use
"string without placeholders"  # regular string
except Exception:  # or use exception if needed
```

### Dependencies
```python
# ❌ BAD
httpx>=0.26  # Unpinned - could break
urllib3==2.6.0  # Manual transitive dependency pin

# ✅ GOOD
httpx==0.26.0  # Exact pin with reason comment
# Let pip resolve: urllib3, certifi, etc.
```

### Security
```python
# ❌ BAD
os.system(user_input)  # Command injection
query = f"SELECT * FROM users WHERE id={user_id}"  # SQL injection
html = f"<div>{user_content}</div>"  # XSS

# ✅ GOOD
subprocess.run([cmd, arg1, arg2])  # Parameterized command
cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))  # Parameterized query
html = escape(user_content)  # Sanitized output
```

## 6. Implementation Examples

### 6.1 Minimal Working Example

```python
"""Minimal working example of this skill."""

# Implementation here
```

### 6.2 Security-Hardened Example

```python
"""Production-ready example with security."""

# Full implementation with validation, error handling, logging
```

### 6.3 Performance-Optimized Example

```python
"""Optimized version for high-throughput scenarios."""

# Caching, batching, async operations
```

## 7. Testing Strategy

### 7.1 Unit Tests

```python
class TestUnit:
    """Unit tests for individual functions."""
    pass
```

### 7.2 Integration Tests

```python
class TestIntegration:
    """Integration tests for workflows."""
    pass
```

### 7.3 Security Tests

```python
class TestSecurity:
    """Security validation tests."""

    def test_path_traversal_prevention(self):
        """Verify path traversal attacks are blocked."""
        pass

    def test_injection_prevention(self):
        """Verify injection attacks are blocked."""
        pass
```

## 8. Monitoring and Observability

### 8.1 Key Metrics

- Metric 1: What to measure
- Metric 2: Success criteria
- Metric 3: Performance targets

### 8.2 Error Handling

```python
# Proper error handling with logging
import logging

logger = logging.getLogger(__name__)

try:
    # Operation
    pass
except SpecificError as e:
    logger.error("Operation failed: %s", str(e))
    # Sanitize error message - don't leak sensitive data
    raise
```

## 9. Maintenance and Updates

### 9.1 Version History

- v1.0.0 (YYYY-MM-DD): Initial release

### 9.2 Known Limitations

1. Limitation 1 and workaround
2. Limitation 2 and mitigation

### 9.3 Future Enhancements

1. Planned enhancement 1
2. Planned enhancement 2

## 10. References

### 10.1 Related Skills

- Related Skill 1: When to use
- Related Skill 2: How they interact

### 10.2 External Documentation

- [Library Docs](https://example.com)
- [Security Best Practices](https://owasp.org)

### 10.3 Compliance & Standards

- OWASP Top 10 (if applicable)
- Industry standards (PCI-DSS, HIPAA, etc.)

---

## Final Checklist Before Submission

**Critical Items:**
- [ ] All quality gates pass (section 4)
- [ ] All tests pass with >80% coverage
- [ ] Security scan clean (bandit)
- [ ] Linters pass (black, isort, flake8, mypy)
- [ ] shellcheck passes (if bash scripts)
- [ ] Documentation complete
- [ ] No hardcoded secrets or API keys
- [ ] Error messages don't leak sensitive data

**Review Items:**
- [ ] Code reviewed by at least one other person
- [ ] Security review if risk_level is MEDIUM or HIGH
- [ ] Performance tested with realistic data
- [ ] Cross-platform compatibility verified
- [ ] Backward compatibility maintained

**CI/CD Items:**
- [ ] All GitHub Actions pass
- [ ] No failing tests
- [ ] No critical security issues
- [ ] Dependencies updated in requirements.txt

---

**Template Version**: 2.0.0 (Updated 2025-12-06 with CI failure lessons)
**Status**: Production-ready template incorporating all quality learnings
