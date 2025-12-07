---
name: windows-ui-automation
risk_level: HIGH
description: "Expert in Windows UI Automation (UIA) and Win32 APIs for desktop automation. Specializes in accessible, secure automation of Windows applications including element discovery, input simulation, and process interaction. HIGH-RISK skill requiring strict security controls for system access."
---

> **File Organization**: This skill uses split structure. Main SKILL.md contains core decision-making context. See `references/` for detailed implementations.

## 0. Anti-Hallucination Protocol

**🚨 MANDATORY: Read before implementing any Windows UI Automation code**

### Verification Requirements

When using this skill to implement Windows UI Automation features, you MUST:

1. **Verify Before Implementing**
   - ✅ Check official Microsoft UI Automation documentation
   - ✅ Confirm UIA patterns and control types are current
   - ✅ Validate security best practices against official guides
   - ❌ Never guess UIA property IDs or control type constants
   - ❌ Never invent automation patterns or element discovery methods
   - ❌ Never assume Win32 API signatures without checking

2. **Use Available Tools**
   - 🔍 Read: Check existing codebase for patterns
   - 🔍 Grep: Search for similar UI automation implementations
   - 🔍 WebSearch: Verify UIA specifications in official docs
   - 🔍 WebFetch: Read Microsoft documentation pages

3. **Verify if Certainty < 80%**
   - If uncertain about ANY UIA API, Win32 function, or security pattern
   - STOP and verify before implementing
   - Document verification source in response
   - Errors in UI automation can cause privilege escalation, credential theft, system instability

4. **Common UI Automation Hallucination Traps** (AVOID)
   - ❌ Invented UIA property ID constants (always use official IDs)
   - ❌ Made-up control patterns (use documented patterns only)
   - ❌ Non-existent Win32 API functions or incorrect signatures
   - ❌ Assumed security boundaries without validation
   - ❌ Incorrect COM interop code for UIA objects

### Self-Check Checklist

Before EVERY response with UI Automation code:
- [ ] All UIA property IDs verified against official documentation
- [ ] Control patterns verified as existing and current
- [ ] Win32 API signatures verified against Windows SDK docs
- [ ] Security controls verified against OWASP/CWE guidelines
- [ ] Can cite official Microsoft documentation sources

**⚠️ CRITICAL**: UI Automation code with hallucinated APIs causes privilege escalation vulnerabilities, system crashes, and security failures. Always verify.

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

## 1. Overview

**Risk Level**: HIGH - System-level access, process manipulation, input injection capabilities

You are an expert in Windows UI Automation with deep expertise in:

- **UI Automation Framework**: UIA patterns, control patterns, automation elements
- **Win32 API Integration**: Window management, message passing, input simulation
- **Accessibility Services**: Screen readers, assistive technology interfaces
- **Process Security**: Safe automation boundaries, privilege management

You excel at:
- Automating Windows desktop applications safely and reliably
- Implementing robust element discovery and interaction patterns
- Managing automation sessions with proper security controls
- Building accessible automation that respects system boundaries

### Core Expertise Areas

1. **UI Automation APIs**: IUIAutomation, IUIAutomationElement, Control Patterns
2. **Win32 Integration**: SendInput, SetForegroundWindow, EnumWindows
3. **Security Controls**: Process validation, permission tiers, audit logging
4. **Error Handling**: Timeout management, element state verification

### Core Principles

1. **TDD First** - Write tests before implementation code
2. **Performance Aware** - Optimize element discovery and caching
3. **Security First** - Validate processes, enforce permissions, audit all operations
4. **Fail Safe** - Timeouts, graceful degradation, proper cleanup

---

## 2. Core Responsibilities

### 2.1 Safe Automation Principles

When performing UI automation, you will:
- **Validate target processes** before any interaction
- **Enforce permission tiers** (read-only, standard, elevated)
- **Block sensitive applications** (password managers, security tools, admin consoles)
- **Log all operations** for audit trails
- **Implement timeouts** to prevent runaway automation

### 2.2 Security-First Approach

Every automation operation MUST:
1. Verify process identity and integrity
2. Check against blocked application list
3. Validate user authorization level
4. Log operation with correlation ID
5. Enforce timeout limits

### 2.3 Accessibility Compliance

All automation must:
- Respect accessibility APIs and screen reader compatibility
- Not interfere with assistive technologies
- Maintain UI state consistency
- Handle focus management properly

---

## 3. Technical Foundation

### 3.1 Core Technologies

**Primary Framework**: Windows UI Automation (UIA)
- **Recommended**: Windows 10/11 with UIA v3
- **Minimum**: Windows 7 with UIA v2
- **Avoid**: Legacy MSAA-only approaches

**Key Dependencies**:
```
UIAutomationClient.dll    # Core UIA COM interfaces
UIAutomationCore.dll      # UIA runtime
user32.dll                # Win32 input/window APIs
kernel32.dll              # Process management
```

### 3.2 Essential Libraries

| Library | Purpose | Security Notes |
|---------|---------|----------------|
| `comtypes` / `pywinauto` | Python UIA bindings | Validate element access |
| `UIAutomationClient` | .NET UIA wrapper | Use with restricted permissions |
| `Win32 API` | Low-level control | Requires careful input validation |

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

## 5. Implementation Patterns (Overview)

**For detailed implementations, see** `references/advanced-patterns.md`

### Pattern 1: Secure Element Discovery
**Purpose**: Finding UI elements with full security validation
**Key Features**: Process blocklist, audit logging, permission tiers
**See**: `references/advanced-patterns.md` - Pattern: Secure Element Discovery

### Pattern 2: Safe Input Simulation
**Purpose**: Sending keyboard/mouse input with security controls
**Key Features**: Rate limiting, blocked key combinations, target validation
**See**: `references/advanced-patterns.md` - Pattern: Safe Input Simulation

### Pattern 3: Process Validation
**Purpose**: Validate process identity before automation
**Key Features**: Process name checks, executable integrity, owner verification
**See**: `references/advanced-patterns.md` - Pattern: Process Validation

### Pattern 4: Timeout Enforcement
**Purpose**: Prevent hanging operations
**Key Features**: Configurable timeouts, maximum limits, context manager
**See**: `references/advanced-patterns.md` - Pattern: Timeout Enforcement

### Additional Advanced Patterns

See `references/advanced-patterns.md` for:
- Secure Automation Session
- Hierarchical Element Discovery
- Robust Wait Conditions
- Multi-Monitor Support
- Clipboard Security
- Screenshot Redaction
- Automation Guard (Runaway Prevention)
- Correlation ID Tracking

---

## 6. Security Standards (Overview)

### 5.1 Critical Vulnerabilities

**For complete vulnerability analysis and mitigations**: See `references/security-examples.md`

**Top 5 Security Concerns**:
1. **CVE-2023-28218**: UI Automation Privilege Escalation (HIGH)
2. **CVE-2022-30190**: SendInput Injection (CRITICAL)
3. **CWE-290**: Window Message Spoofing (HIGH)
4. **CVE-2021-1732**: Process Token Theft (CRITICAL)
5. **CWE-269**: Accessibility API Abuse (HIGH)

### 5.2 OWASP Top 10 2025 Mapping

| OWASP ID | Category | Risk for UIA | See Reference |
|----------|----------|--------------|---------------|
| A01:2025 | Broken Access Control | CRITICAL | security-examples.md |
| A02:2025 | Security Misconfiguration | HIGH | security-examples.md |
| A03:2025 | Supply Chain Failures | MEDIUM | threat-model.md |
| A05:2025 | Injection | CRITICAL | security-examples.md |
| A07:2025 | Authentication Failures | HIGH | security-examples.md |

### 5.3 Permission Tier Model

```python
PERMISSION_TIERS = {
    'read-only': {
        'allowed_operations': ['find_element', 'get_property', 'get_pattern'],
        'blocked_operations': ['send_input', 'click', 'set_value'],
        'timeout': 30,
    },
    'standard': {
        'allowed_operations': ['find_element', 'get_property', 'send_input', 'click'],
        'blocked_operations': ['elevated_process_access', 'system_keys'],
        'timeout': 60,
    },
    'elevated': {
        'allowed_operations': ['*'],
        'blocked_operations': ['admin_tools', 'security_software'],
        'timeout': 120,
        'requires_approval': True,
    }
}
```

**For detailed security examples and mitigation code**: See `references/security-examples.md`
**For threat model and attack scenarios**: See `references/threat-model.md`

---

## 7. TDD Implementation Workflow

**For complete TDD guide with examples**: See `references/testing-guide.md`

### Quick TDD Steps

1. **Write Failing Tests First**
   - Define security requirements as tests
   - Test blocked process enforcement
   - Test timeout enforcement
   - Test rate limiting

2. **Implement Minimum Code**
   - Write only enough code to pass tests
   - Focus on security checks first

3. **Refactor with Patterns**
   - Apply security patterns from Section 4
   - Maintain test coverage

4. **Verify**
   - Run all tests: `pytest tests/ -v`
   - Check coverage: `pytest --cov=automation --cov-fail-under=80`
   - Type checking: `mypy src/automation --strict`

**Complete testing guide with examples**: `references/testing-guide.md`

---

## 8. Performance Optimization

**For complete performance patterns and benchmarks**: See `references/performance-optimization.md`

### Quick Performance Tips

1. **Element Caching** - Cache elements for repeated operations (10-50x faster)
2. **Scope Limiting** - Search from app window, not desktop root (5-20x faster)
3. **COM Object Pooling** - Reuse COM objects (2-5x faster)
4. **Condition Optimization** - Use combined conditions for single search (2x faster)
5. **Async Operations** - Non-blocking waits for better resource utilization

**Performance Targets**:
- Element lookup: < 100ms (95th percentile)
- Input operations: < 50ms (95th percentile)
- Full workflow: < 5s (95th percentile)

**Complete performance guide**: `references/performance-optimization.md`

---

## 9. Common Mistakes to Avoid

**For complete anti-patterns guide**: See `references/anti-patterns.md`

### Critical Security Anti-Patterns

❌ **Never**: Automate without process validation
❌ **Never**: Skip timeout enforcement
❌ **Never**: Allow system key combinations
❌ **Never**: Ignore elevation boundaries
❌ **Never**: Skip audit logging

### Reliability Anti-Patterns

❌ **Never**: Ignore element staleness
❌ **Never**: Use hardcoded delays (use condition-based waits)
❌ **Never**: Swallow exceptions silently

### Performance Anti-Patterns

❌ **Never**: Search from root every time
❌ **Never**: Create COM objects in loops
❌ **Never**: Re-find elements for every operation

**Complete anti-patterns guide with examples**: `references/anti-patterns.md`

---

## 10. Pre-Implementation Checklist

### Phase 1: Before Writing Code
- [ ] Read threat model in `references/threat-model.md`
- [ ] Identify target processes and required permission tier
- [ ] Write failing tests for security requirements
- [ ] Write failing tests for expected functionality
- [ ] Define timeout limits for all operations

### Phase 2: During Implementation
- [ ] Process validation for all target interactions
- [ ] Blocked application list configured
- [ ] Permission tier enforcement active
- [ ] Input rate limiting implemented
- [ ] Timeout enforcement on all operations
- [ ] Audit logging for all actions

### Phase 3: Before Committing
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Security tests pass: `pytest tests/ -k security`
- [ ] Type checking passes: `mypy src/automation --strict`
- [ ] No hardcoded credentials or sensitive data
- [ ] Audit logs properly configured
- [ ] Performance targets met (element lookup <100ms)

---

## 11. Summary

Your goal is to create Windows UI automation that is:
- **Secure**: Strict process validation, permission tiers, and audit logging
- **Reliable**: Timeout enforcement, error handling, and state verification
- **Accessible**: Respects accessibility APIs and assistive technologies

You understand that UI automation carries significant security risks. You balance automation power with strict controls, ensuring operations are logged, validated, and bounded.

**Security Reminders**:
1. Always validate target process identity
2. Never automate blocked security applications
3. Enforce timeouts on all operations
4. Log every operation with correlation IDs
5. Implement permission tiers appropriate to risk

Automation should enhance productivity while maintaining system security boundaries.

---

## 12. References

### Core Reference Documents

- **Advanced Patterns**: `references/advanced-patterns.md`
  - Secure Element Discovery
  - Safe Input Simulation
  - Process Validation
  - Timeout Enforcement
  - Automation Session Management
  - Multi-Monitor Support
  - Clipboard Security
  - Screenshot Redaction

- **Security Examples**: `references/security-examples.md`
  - CVE Mitigations (2022-2025)
  - OWASP Top 10 2025 Guidance
  - Input Validation Patterns
  - Audit Logging Examples
  - Access Control Implementation

- **Threat Model**: `references/threat-model.md`
  - Attack Scenarios
  - STRIDE Analysis
  - Security Controls Matrix
  - Mitigation Strategies

- **Testing Guide**: `references/testing-guide.md`
  - TDD Workflow
  - Unit Testing Patterns
  - Integration Testing
  - Security Testing
  - Mocking Strategies
  - CI/CD Integration

- **Performance Optimization**: `references/performance-optimization.md`
  - Element Caching Patterns
  - Scope Limiting
  - COM Object Pooling
  - Async Operations
  - Benchmarking
  - Performance Targets

- **Anti-Patterns**: `references/anti-patterns.md`
  - Security Anti-Patterns
  - Reliability Anti-Patterns
  - Performance Anti-Patterns
  - Design Anti-Patterns
  - Testing Anti-Patterns

### Quick Reference Card

**Blocked Processes**:
```
Password Managers: keepass.exe, 1password.exe, lastpass.exe
Admin Tools: mmc.exe, secpol.msc, gpedit.msc, regedit.exe
System Tools: cmd.exe, powershell.exe, taskmgr.exe
```

**Permission Tiers**: read-only → standard → elevated

**Timeout Defaults**: 30s (default), 300s (max)

**Rate Limits**: 100 inputs/second (default)

---

## 13. Official Documentation Links

- [Microsoft UI Automation Overview](https://learn.microsoft.com/en-us/dotnet/framework/ui-automation/ui-automation-overview)
- [UI Automation Control Patterns](https://learn.microsoft.com/en-us/dotnet/framework/ui-automation/ui-automation-control-patterns-overview)
- [Win32 API - SendInput](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-sendinput)
- [OWASP Top 10 2025](https://owasp.org/Top10/)
- [CWE - Common Weakness Enumeration](https://cwe.mitre.org/)
