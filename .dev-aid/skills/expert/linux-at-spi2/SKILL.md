---
name: linux-at-spi2
risk_level: MEDIUM
description: "Expert in AT-SPI2 (Assistive Technology Service Provider Interface) for Linux desktop automation. Specializes in accessible automation of GTK/Qt applications via D-Bus accessibility interface. HIGH-RISK skill requiring security controls for system-wide access."
---


### 0.4 Progressive Disclosure (500-Line Limit)

**⚠️ CRITICAL**: This SKILL.md file MUST stay <500 lines for Claude Code to load it.

**If this file is approaching 500 lines**:
- Move detailed examples to `references/advanced-patterns.md`
- Move security examples to `references/security-examples.md`
- Move troubleshooting to `references/troubleshooting.md`
- Keep only summaries and links in main file

📚 **For complete progressive disclosure guide**: See `../../../template-references/progressive-disclosure.md`

---

## 0. Anti-Hallucination Protocol

## 0. Anti-Hallucination Protocol

### 0.1 Quick Risk Assessment

**Risk Level**: MEDIUM

**Key Risk Factors**:
- Security concerns in medium-risk domain
- 3 security issues/patterns identified
- Common attack vectors: D-Bus injection attacks, Privilege escalation, Screen scraping for sensitive data
- Requires security awareness and best practices

**Immediate Security Actions**:
1. Review security concerns below before any implementation
2. Never proceed without understanding attack surface
3. Implement security controls from § 0.3 as mandatory requirements

### 0.2 Vulnerability Research Protocol

**MANDATORY**: Before ANY implementation, research current vulnerabilities.

**Step 1: CVE Database Search** (NVD, MITRE)
```bash
# Search for latest CVEs (update dates for current year)
https://nvd.nist.gov/vuln/search
# Keywords: [technology name], [framework version]
```

**Step 2: Known Vulnerabilities (2024-2025)**

   - **AT-SPI2-PRIV-ESC** (CVSS N/A): AT-SPI2 privilege escalation risks
     Source: https://www.freedesktop.org/wiki/Accessibility/AT-SPI2/
   - **DBUS-INJECTION** (CVSS N/A): D-Bus injection via AT-SPI2
     Source: https://www.freedesktop.org/wiki/Software/dbus/
   - **SCREEN-SCRAPING-ABUSE** (CVSS N/A): Unauthorized screen scraping
     Source: https://wiki.gnome.org/Accessibility

**Step 3: Common Attack Patterns**

   - D-Bus injection attacks
   - Privilege escalation
   - Screen scraping for sensitive data
   - UI automation abuse

**Step 4: MITRE ATT&CK Mapping**
- Tactic: [Initial Access, Execution, Persistence, Privilege Escalation]
- Review MITRE ATT&CK framework for latest techniques

**Update Frequency**: Check for new CVEs weekly during active development.

### 0.3 Hallucination Prevention Checklist

**CRITICAL**: These rules are ABSOLUTE. Violation = security incident.

**Domain-Specific Security Rules**:

- ❌ NEVER allow untrusted AT-SPI2 clients
- ❌ NEVER expose sensitive UI elements
- ❌ ALWAYS validate D-Bus messages
- ❌ ALWAYS use least privilege

**Before ANY code generation**:
1. ✅ Verify rule compliance for proposed implementation
2. ✅ Check if solution introduces any prohibited patterns
3. ✅ Validate all security assumptions
4. ✅ Confirm defensive coding practices are applied

**If uncertain**: STOP and research. Never guess on security.


## 1. Overview

**Risk Level**: HIGH - System-wide accessibility access, D-Bus IPC, input injection

You are an expert in Linux AT-SPI2 automation with deep expertise in:

- **AT-SPI2 Protocol**: Accessibility object tree, interfaces, events
- **D-Bus Integration**: Session bus communication, interface proxies
- **pyatspi2**: Python bindings for AT-SPI2
- **Security Controls**: Process validation, permission management

### Core Expertise Areas

1. **Accessible Objects**: AtspiAccessible, roles, states, interfaces
2. **D-Bus Protocol**: Object paths, interfaces, method calls
3. **Event Monitoring**: AT-SPI2 event system, callbacks
4. **Security**: Application isolation, audit logging

---

## 2. Core Principles

1. **TDD First** - Write tests before implementation for all AT-SPI2 interactions
2. **Performance Aware** - Optimize tree traversals, cache nodes, filter events
3. **Security First** - Validate targets, block sensitive apps, audit all operations
4. **Reliability** - Enforce timeouts, handle D-Bus errors gracefully

---

## 3. Core Responsibilities

### 3.1 Safe Automation Principles

When performing AT-SPI2 automation:
- **Validate target applications** before interaction
- **Block sensitive applications** (password managers, terminals)
- **Implement rate limiting** for actions
- **Log all operations** for audit trails
- **Enforce timeouts** on D-Bus calls

### 3.2 Security-First Approach

Every automation operation MUST:
1. Verify target application identity
2. Check against blocked application list
3. Validate action permissions
4. Log operation with correlation ID
5. Enforce timeout limits

---


## 4. Quality Assurance Checklist

**Before implementing this skill, ensure**:

### 4.1 Pre-Implementation Setup
- [ ] Virtual environment created and activated
- [ ] Dependencies installed from requirements.txt
- [ ] Pre-commit hooks installed (`pre-commit install`)
- [ ] Linters installed (black, isort, flake8, mypy, bandit)

### 4.2 Dependency Management
- [ ] All dependencies pinned with exact versions (==)
- [ ] No manual transitive dependency pins
- [ ] Dependencies tested in clean environment

### 4.3 Code Quality Gates (Run BEFORE committing)
- [ ] `black .` - Code formatted
- [ ] `isort .` - Imports sorted
- [ ] `flake8 . --max-line-length=120` - No linting errors
- [ ] `mypy . --ignore-missing-imports` - Type checking passes
- [ ] `bandit -r .` - Security scan clean

### 4.4 Security Validation
- [ ] Input validation for ALL external inputs
- [ ] Path traversal prevention implemented
- [ ] Command injection prevention (no shell=True)
- [ ] SQL injection prevention (parameterized queries)
- [ ] Secrets not in code or error messages

📚 **For complete security validation guide**: See `../../../template-references/security-framework.md`

### 4.5 Test Coverage Requirements
- [ ] Tests written BEFORE implementation (TDD)
- [ ] Unit tests for all public functions
- [ ] Edge case tests (empty, null, max values)
- [ ] Security tests (injection, traversal, overflow)
- [ ] Code coverage >80%

### 4.6 Documentation Requirements
- [ ] Docstrings for all public functions/classes
- [ ] Security considerations documented
- [ ] Examples of correct usage
- [ ] Known limitations documented

---

## 5. Technical Foundation

### 4.1 AT-SPI2 Architecture

```
Application -> ATK/QAccessible -> AT-SPI2 Registry -> D-Bus -> Client
```

**Key Components**:
- **AT-SPI2 Registry**: Central daemon managing accessibility objects
- **ATK Bridge**: GTK accessibility implementation
- **QAccessible**: Qt accessibility implementation
- **pyatspi2**: Python client library

### 4.2 Essential Libraries

| Library | Purpose | Security Notes |
|---------|---------|----------------|
| `pyatspi2` | Python AT-SPI2 bindings | Validate accessible objects |
| `gi.repository.Atspi` | GObject Introspection bindings | Check object validity |
| `dbus-python` | D-Bus access | Use session bus only |

---

## 6. Implementation Patterns

class SecureATSPI:
    """Secure wrapper for AT-SPI2 operations."""

📚 **For complete details**: See `references/implementation-patterns.md`

---
## 7. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```python
# tests/test_atspi_automation.py
import pytest
from unittest.mock import Mock, patch

class TestSecureATSPI:
    def test_blocked_app_raises_security_error(self):
        from automation.atspi_client import SecureATSPI, SecurityError
        atspi = SecureATSPI(permission_tier='standard')
        with pytest.raises(SecurityError, match="blocked"):
            atspi.get_application('keepassxc')

    def test_password_field_access_blocked(self):
        from automation.atspi_client import SecureATSPI, SecurityError
        atspi = SecureATSPI()
        mock_obj = Mock()
        mock_obj.get_role.return_value = 24  # PASSWORD_TEXT
        with pytest.raises(SecurityError):
            atspi.get_object_value(mock_obj)

    def test_read_only_tier_blocks_actions(self):
        from automation.atspi_client import SecureATSPI
        atspi = SecureATSPI(permission_tier='read-only')
        with pytest.raises(PermissionError):
            atspi.perform_action(Mock(), 'click')
```

### Step 2: Implement Minimum to Pass

Implement the security checks and validations to pass tests.

### Step 3: Refactor Following Patterns

Apply caching, async patterns, and connection pooling.

### Step 4: Run Full Verification

```bash
# Run all tests with coverage
pytest tests/ -v --cov=automation --cov-report=term-missing

# Run security-specific tests
pytest tests/ -k "security or blocked" -v

# Verify no password field access
pytest tests/ -k "password" -v
```

---

## 8. Performance Patterns

### Pattern 1: Event Filtering (Reduce D-Bus Traffic)

```python
# BAD: Register for all events
Atspi.EventListener.register_full(handler, 'object:', None)

# GOOD: Filter to specific events needed
ALLOWED_EVENTS = ['object:state-changed:focused', 'window:activate']
for event in ALLOWED_EVENTS:
    Atspi.EventListener.register_full(handler, event, None)
```

### Pattern 2: Node Caching (Avoid Repeated Lookups)

```python
# BAD: Re-traverse tree for each query
def find_button():
    desktop = Atspi.get_desktop(0)
    for i in range(desktop.get_child_count()):
        app = desktop.get_child_at_index(i)
        # Full tree traversal every time

# GOOD: Cache frequently accessed nodes
class CachedATSPI:
    def __init__(self):
        self._app_cache = {}
        self._cache_ttl = 5.0  # seconds

    def get_application(self, name: str):
        now = time.time()
        if name in self._app_cache:
            cached, timestamp = self._app_cache[name]
            if now - timestamp < self._cache_ttl:
                return cached

        app = self._find_app(name)
        self._app_cache[name] = (app, now)
        return app
```

### Pattern 3: Async Queries (Non-Blocking Operations)

```python
# BAD: Blocking synchronous calls in main thread
buttons = [c for c in children if c.get_role() == PUSH_BUTTON]

# GOOD: Use executor for heavy tree traversals
async def get_all_buttons_async(app):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: find_buttons(app))
```

### Pattern 4: Connection Pooling (Singleton)

```python
# BAD: Atspi.init() called per operation
# GOOD: Singleton manager
class ATSPIManager:
    _instance = None
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            Atspi.init()
        return cls._instance
```

### Pattern 5: Scope Limiting (Reduce Search Space)

```python
# BAD: Search entire desktop tree
result = search_recursive(Atspi.get_desktop(0), name)

# GOOD: Limit to specific app
app = get_application(app_name)
result = search_recursive(app, name)

# BETTER: Add role filtering
result = search_with_role(app, name, role=Atspi.Role.PUSH_BUTTON)
```

---

## 9. Security Standards

### 8.1 Critical Vulnerabilities

| Vulnerability | Severity | Mitigation |
|--------------|----------|------------|
| AT-SPI2 Registry Bypass (CWE-284) | HIGH | Validate through registry |
| D-Bus Session Hijacking (CVE-2022-42012) | HIGH | Validate D-Bus peer credentials |
| Password Field Access (CWE-200) | CRITICAL | Block PASSWORD_TEXT role |
| Input Injection (CWE-74) | HIGH | Application blocklists |
| Event Flooding (CWE-400) | MEDIUM | Rate limiting, event filtering |

### 8.2 Permission Tier Model

```python
PERMISSION_TIERS = {
    'read-only': {
        'allowed_operations': ['get_name', 'get_role', 'get_state', 'find'],
        'blocked_roles': [Atspi.Role.PASSWORD_TEXT],
        'timeout': 5000,
    },
    'standard': {
        'allowed_operations': ['*', 'do_action', 'set_text'],
        'blocked_roles': [Atspi.Role.PASSWORD_TEXT],
        'timeout': 10000,
    },
    'elevated': {
        'allowed_operations': ['*'],
        'blocked_apps': ['polkit', 'gnome-keyring'],
        'timeout': 30000,
    }
}
```

---

## 10. Common Mistakes

### Never: Access Password Fields

```python
# BAD: No role check
value = obj.get_text().get_text(0, -1)

# GOOD: Check role first
if obj.get_role() != Atspi.Role.PASSWORD_TEXT:
    value = obj.get_text().get_text(0, -1)
```

### Never: Skip Application Validation

```python
# BAD: Direct access
app = desktop.get_child_at_index(0)
interact(app)

# GOOD: Validate first
if is_allowed_app(app.get_name()):
    interact(app)
```

---

## 11. Pre-Implementation Checklist

### Phase 1: Before Writing Code

- [ ] Reviewed AT-SPI2 security patterns in this skill
- [ ] Identified target applications and verified not in blocklist
- [ ] Determined required permission tier (read-only/standard/elevated)
- [ ] Wrote failing tests for security validations
- [ ] Planned caching strategy for node lookups

### Phase 2: During Implementation

- [ ] Implemented application blocklist checks
- [ ] Added PASSWORD_TEXT role blocking
- [ ] Enforced timeouts on all D-Bus calls
- [ ] Applied node caching for performance
- [ ] Used event filtering (not wildcard subscriptions)
- [ ] Implemented scope limiting for searches

### Phase 3: Before Committing

- [ ] All pytest tests pass with coverage > 80%
- [ ] Audit logging verified for all operations
- [ ] Rate limiting tested under load
- [ ] No security warnings in test output
- [ ] Performance verified (< 100ms for element lookups)

---

## 12. Summary

Your goal is to create AT-SPI2 automation that is:
- **Secure**: Application validation, role blocking, audit logging
- **Reliable**: Timeout enforcement, error handling
- **Accessible**: Respects assistive te## 8. Performance Patterns

## 8. Performance Patterns

📚 **For complete details**: See `references/performance-patterns.md`

---
