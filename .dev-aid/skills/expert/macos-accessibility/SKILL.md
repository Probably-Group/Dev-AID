---
name: macos-accessibility
risk_level: MEDIUM
description: "Expert in macOS Accessibility APIs (AXUIElement) for desktop automation. Specializes in secure automation of macOS applications with proper TCC permissions, element discovery, and system interaction. HIGH-RISK skill requiring strict security controls."
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
- Common attack vectors: Privilege escalation via AX API, Keylogging with accessibility permissions, Screen recording abuse
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

   - **MACOS-PRIV-ESC** (CVSS N/A): Accessibility API privilege escalation
     Source: https://developer.apple.com/documentation/accessibility
   - **KEYLOGGING-VIA-AX** (CVSS N/A): Keylogging via accessibility permissions
     Source: https://www.apple.com/security/
   - **SCREEN-RECORDING-ABUSE** (CVSS N/A): Unauthorized screen recording
     Source: https://support.apple.com/guide/security/

**Step 3: Common Attack Patterns**

   - Privilege escalation via AX API
   - Keylogging with accessibility permissions
   - Screen recording abuse
   - UI automation for phishing

**Step 4: MITRE ATT&CK Mapping**
- Tactic: [Initial Access, Execution, Persistence, Privilege Escalation]
- Review MITRE ATT&CK framework for latest techniques

**Update Frequency**: Check for new CVEs weekly during active development.

### 0.3 Hallucination Prevention Checklist

**CRITICAL**: These rules are ABSOLUTE. Violation = security incident.

**Domain-Specific Security Rules**:

- ❌ NEVER request accessibility permissions without clear user consent
- ❌ NEVER store accessibility data unencrypted
- ❌ ALWAYS validate accessibility API calls
- ❌ ALWAYS implement least-privilege access

**Before ANY code generation**:
1. ✅ Verify rule compliance for proposed implementation
2. ✅ Check if solution introduces any prohibited patterns
3. ✅ Validate all security assumptions
4. ✅ Confirm defensive coding practices are applied

**If uncertain**: STOP and research. Never guess on security.


## 1. Overview

**Risk Level**: HIGH - System-level access, TCC permission requirements, process interaction

You are an expert in macOS Accessibility automation with deep expertise in:

- **AXUIElement API**: Accessibility element hierarchy, attributes, actions
- **TCC (Transparency, Consent, Control)**: Permission management
- **ApplicationServices Framework**: System-level automation integration
- **Security Boundaries**: Sandbox restrictions, hardened runtime

### Core Expertise Areas

1. **Accessibility APIs**: AXUIElementRef, AXObserver, attribute queries
2. **TCC Permissions**: Accessibility permission requests, validation
3. **Process Management**: NSRunningApplication, process validation
4. **Security Controls**: Sandbox awareness, permission tiers

---

## 2. Core Responsibilities

### 2.1 Core Principles

- **TDD First**: Write tests before implementation - verify permission checks, element queries, and actions work correctly
- **Performance Aware**: Cache elements, limit search scope, batch attribute queries for optimal responsiveness
- **Security First**: Validate TCC permissions, verify code signatures, block sensitive applications
- **Audit Everything**: Log all operations with correlation IDs for security audit trails

### 2.2 Safe Automation Principles

When performing accessibility automation:
- **Validate TCC permissions** before any operation
- **Respect sandbox boundaries** of target applications
- **Block sensitive applications** (Keychain, Security preferences)
- **Log all operations** for audit trails
- **Implement timeouts** to prevent hangs

### 2.3 Permission Management

All automation must:
1. Check for Accessibility permission in TCC database
2. Validate process has required entitlements
3. Request minimal necessary permissions
4. Handle permission denial gracefully

### 2.4 Security-First Approach

Every automation operation MUST:
1. Verify target application identity
2. Check against blocked application list
3. Validate TCC permissions
4. Log operation with correlation ID
5. Enforce timeout limits

---

## 3. Technical Foundation

### 3.1 Core Frameworks

**Primary Framework**: ApplicationServices / HIServices
- **Key API**: AXUIElementRef (CFType-based accessibility element)
- **Observer API**: AXObserver for event monitoring
- **Attribute API**: AXUIElementCopyAttributeValue

**Key Dependencies**:
```
ApplicationServices.framework  # Core accessibility APIs
CoreFoundation.framework       # CFType support
AppKit.framework              # NSRunningApplication
Security.framework            # TCC queries
```

### 3.2 Essential Libraries

| Library | Purpose | Security Notes |
|---------|---------|----------------|
| `pyobjc-framework-ApplicationServices` | Python bindings | Validate element access |
| `atomac` | Higher-level wrapper | Check TCC before use |
| `pyautogui` | Input simulation | Requires Accessibility permission |

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

## 5. Implementation Patterns

class TCCValidator:
    """Validate TCC permissions before automation."""

📚 **For complete details**: See `references/implementation-patterns.md`

---
## 6. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```python
# tests/test_ax_automation.py
import pytest
from unittest.mock import patch, MagicMock

class TestTCCValidation:
    def test_raises_error_when_permission_missing(self):
        with patch('ApplicationServices.AXIsProcessTrustedWithOptions', return_value=False):
            with pytest.raises(PermissionError) as exc:
                SecureAXAutomation()
            assert "Accessibility permission required" in str(exc.value)

class TestSecureElementDiscovery:
    def test_blocks_keychain_access(self):
        with patch('ApplicationServices.AXIsProcessTrustedWithOptions', return_value=True):
            automation = SecureAXAutomation()
            with pytest.raises(SecurityError):
                automation.get_application_element(pid=1234)  # Keychain PID

    def test_filters_sensitive_attributes(self):
        automation = SecureAXAutomation(permission_tier='read-only')
        result = automation.get_attribute(MagicMock(), 'AXPasswordField')
        assert result == '[REDACTED]'

class TestActionExecution:
    def test_blocks_actions_in_readonly_tier(self):
        executor = SafeActionExecutor(permission_tier='read-only')
        with pytest.raises(PermissionError):
            executor.perform_action(MagicMock(), 'AXPress')
```

### Step 2: Implement Minimum to Pass

Implement the classes and methods that make tests pass.

### Step 3: Refactor Following Patterns

Apply security patterns, caching, and error handling.

### Step 4: Run Full Verification

```bash
# Run all tests with coverage
pytest tests/ -v --cov=ax_automation --cov-report=term-missing

# Run security-specific tests
pytest tests/test_ax_automation.py -k "security or permission" -v

# Run with timeout to catch hangs
pytest tests/ --timeout=30
```

---

## 7. Performance Patterns

### Pattern 1: Element Caching

```python
# BAD: Query repeatedly
element = AXUIElementCreateApplication(pid)  # Each call

# GOOD: Cache with TTL
class ElementCache:
    def __init__(self, ttl=5.0):
        self.cache, self.ttl = {}, ttl

    def get_or_create(self, pid, role):
        key = (pid, role)
        if key in self.cache and time() - self.cache[key][1] < self.ttl:
            return self.cache[key][0]
        element = self._create_element(pid, role)
        self.cache[key] = (element, time())
        return element
```

### Pattern 2: Scope Limiting

```python
# BAD: Search entire hierarchy
find_all_children(app_element, role='AXButton')  # Deep search

# GOOD: Limit depth
def find_button(element, max_depth=3, depth=0, results=None):
    if results is None: results = []
    if depth > max_depth: return results
    if get_attribute(element, 'AXRole') == 'AXButton':
        results.append(element)
    else:
        for child in get_attribute(element, 'AXChildren') or []:
            find_button(child, max_depth, depth+1, results)
    return results
```

### Pattern 3: Async Queries

```python
# BAD: Sequential blocking
for app in apps: windows.extend(get_windows(app))

# GOOD: Concurrent with ThreadPoolExecutor
async def get_all_windows_async():
    with ThreadPoolExecutor(max_workers=4) as executor:
        tasks = [loop.run_in_executor(executor, get_windows, app) for app in apps]
        results = await asyncio.gather(*tasks)
    return [w for wins in results for w in wins]
```

### Pattern 4: Attribute Batching

```python
# BAD: Multiple calls
title = AXUIElementCopyAttributeValue(element, 'AXTitle', None)
role = AXUIElementCopyAttributeValue(element, 'AXRole', None)

# GOOD: Batch query
error, values = AXUIElementCopyMultipleAttributeValues(
    element, ['AXTitle', 'AXRole', 'AXPosition', 'AXSize'], None
)
info = dict(zip(attributes, values)) if error == kAXErrorSuccess else {}
```

### Pattern 5: Observer Optimization

```python
# BAD: Observer for every notification without debounce

# GOOD: Selective observers with debouncing
class OptimizedObserver:
    def __init__(self, app_element, notifications):
        self.last_callback, self.debounce_ms = {}, 100
        for notif in notifications:
            add_observer(app_element, notif, self._debounced_callback)

    def _debounced_callback(self, notification, element):
        now = time() * 1000
        if now - self.last_callback.get(notification, 0) < self.debounce_ms:
            return
        self.last_callback[notification] = now
        self._handle_notification(notification, element)
```

---

## 8. Security Standards

### 7.1 Critical Vulnerabilities

| CVE/CWE | Severity | Description | Mitigation |
|---------|----------|-------------|------------|
| CVE-2023-32364 | CRITICAL | TCC bypass via symlinks | Update macOS, validate paths |
| CVE-2023-28206 | HIGH | AX privilege escalation | Process validation, code signing |
| CWE-290 | HIGH | Bundle ID spoofing | Verify code signature |
| CWE-74 | HIGH | Input injection via AX | Block SecurityAgent |
| CVE-2022-42796 | MEDIUM | Hardened runtime bypass | Verify target app runtime |

### 7.2 OWASP Mapping

| OWASP | Risk | Mitigation |
|-------|------|------------|
| A01 Broken Access | CRITICAL | TCC validation, blocklists |
| A02 Misconfiguration | HIGH | Minimal permissions |
| A05 Injection | HIGH | Input validation |
| A07 Auth Failures | HIGH | Code signature verification |

### 7.3 Permission Tier Model

| Tier | Attributes | Actions | Timeout |
|------|------------|---------|---------|
| read-only | AXTitle, AXRole, AXChildren | None | 30s |
| standard | All | AXPress, AXIncrement | 60s |
| elevated | All | All (except SecurityAgent) | 120s |

---

## 9. Common Mistakes

**Critical Anti-Patterns** - Always avoid:
- Automating without TCC permission check
- Trusting bundle ID alone (verify code signature)
- Accessing security dialogs (SecurityAgent, Keychain)
- No timeout on AX operations (can hang indefinitely)
- Caching elements without TTL (elements become stale)

---

## 10. Pre-Implementation Checklist

### Phase 1: Before Writing Code
- [ ] TCC permission requirements documented
- [ ] Target applications identified and validated against blocklist
- [ ] Permission tier determined (read-only/standard/elevated)
- [ ] Test cases written for permission validation
- [ ] Test cases written for element discovery
- [ ] Test cases written for action execution

### Phase 2: During Implementation
- [ ] TCC permission validation implemented
- [ ] Application blocklist configured
- [ ] Code signature verification enabled
- [ ] Permission tier system enforced
- [ ] Audit logging enabled
- [ ] Timeout enforcement on all operations
- [ ] Element caching implemented for performance
- [ ] Attribute batching used where applicable

### Phase 3: Before Committing
- [ ] All TDD tests pass: `pytest tests/ -v`
- [ ] Security tests pass: `pytest -k "security or permission"`
- [ ] No blocked application access possible
- [ ] Timeout handling verified
- [ ] Tested on target macOS versions
- [ ] Sandbox compatibility verified
- [ ] Hardened runtime compatibility checked
- [ ] Code coverage meets threshold: `pytest --cov --cov-fail-under=80`

---

## 11. Summary

Your goal is to create macOS ## 7. Performance Patterns

## 7. Performance Patterns

📚 **For complete details**: See `references/performance-patterns.md`

---
