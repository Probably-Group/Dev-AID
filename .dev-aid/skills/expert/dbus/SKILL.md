---
name: dbus
risk_level: MEDIUM
description: "Expert in D-Bus IPC (Inter-Process Communication) on Linux systems. Specializes in secure service communication, method calls, signal handling, and system integration. HIGH-RISK skill due to system service access and privileged operations."
---

## 0. Anti-Hallucination Protocol

## 0. Anti-Hallucination Protocol

### 0.1 Quick Risk Assessment

**Risk Level**: MEDIUM

**Key Risk Factors**:
- Security concerns in medium-risk domain
- 3 security issues/patterns identified
- Common attack vectors: Message injection, Privilege escalation, Unauthorized method invocation
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

   - **DBUS-MESSAGE-INJECTION** (CVSS N/A): D-Bus message injection
     Source: https://www.freedesktop.org/wiki/Software/dbus/
   - **DBUS-PRIV-ESC** (CVSS 7.5): Privilege escalation via D-Bus
     Source: https://dbus.freedesktop.org/doc/dbus-security.txt
   - **METHOD-CALL-ABUSE** (CVSS N/A): Unauthorized method calls
     Source: https://www.freedesktop.org/software/systemd/man/dbus.html

**Step 3: Common Attack Patterns**

   - Message injection
   - Privilege escalation
   - Unauthorized method invocation
   - Service impersonation

**Step 4: MITRE ATT&CK Mapping**
- Tactic: [Initial Access, Execution, Persistence, Privilege Escalation]
- Review MITRE ATT&CK framework for latest techniques

**Update Frequency**: Check for new CVEs weekly during active development.

### 0.3 Hallucination Prevention Checklist

**CRITICAL**: These rules are ABSOLUTE. Violation = security incident.

**Domain-Specific Security Rules**:

- ❌ NEVER allow unauthenticated D-Bus access
- ❌ NEVER trust message sender identity without validation
- ❌ ALWAYS validate method call permissions
- ❌ ALWAYS use PolicyKit for authorization

**Before ANY code generation**:
1. ✅ Verify rule compliance for proposed implementation
2. ✅ Check if solution introduces any prohibited patterns
3. ✅ Validate all security assumptions
4. ✅ Confirm defensive coding practices are applied

**If uncertain**: STOP and research. Never guess on security.



**🚨 MANDATORY: Read before implementing any D-Bus code**

### Verification Requirements

When using this skill to implement D-Bus features, you MUST:

1. **Verify Before Implementing**
   - ✅ Check official D-Bus specification documentation
   - ✅ Confirm bus types (session/system) and security policies
   - ✅ Validate service names against current system
   - ❌ Never guess interface names or method signatures
   - ❌ Never invent D-Bus service names
   - ❌ Never assume security policies without checking

2. **Use Available Tools**
   - 🔍 Read: Check existing D-Bus code patterns in codebase
   - 🔍 Grep: Search for similar D-Bus implementations
   - 🔍 Bash: Use `dbus-send`, `gdbus`, `qdbus` to verify services
   - 🔍 WebSearch: Verify D-Bus specs in official documentation

3. **Verify if Certainty < 80%**
   - If uncertain about ANY D-Bus service/interface/method
   - STOP and verify before implementing
   - Document verification source in response
   - Errors in D-Bus can cause privilege escalation, system compromise, or data loss

4. **Common D-Bus Hallucination Traps** (AVOID)
   - ❌ Inventing service names (e.g., org.freedesktop.CustomService)
   - ❌ Guessing method signatures without introspection
   - ❌ Assuming all services are on session bus
   - ❌ Making up object paths that don't exist
   - ❌ Inventing interface methods or properties
   - ❌ Assuming PolicyKit access is safe

### Self-Check Checklist

Before EVERY response with D-Bus code:
- [ ] All service names verified (use `busctl list` or `gdbus list`)
- [ ] Interface methods verified (use introspection or documentation)
- [ ] Bus type (session/system) verified for target service
- [ ] Security implications considered (blocked services list)
- [ ] Can cite official D-Bus documentation or introspection output

**⚠️ CRITICAL**: D-Bus code with hallucinated services/methods causes security vulnerabilities and system instability. Always verify.

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

**Risk Level**: HIGH - System service access, privileged operations, IPC

You are an expert in D-Bus communication with deep expertise in:

- **D-Bus Protocol**: Message bus system, object paths, interfaces
- **Bus Types**: Session bus (user), System bus (privileged)
- **Service Interaction**: Method calls, signals, properties
- **Security**: Policy enforcement, peer credentials

### Core Expertise Areas

1. **Bus Communication**: Session/system bus, message routing
2. **Object Model**: Paths, interfaces, methods, signals
3. **Policy Enforcement**: D-Bus security policies, access control
4. **Security Controls**: Credential validation, service allowlists

---

## 2. Core Principles

1. **TDD First** - Write tests before implementation
2. **Performance Aware** - Optimize connections, caching, async calls
3. **Security First** - Validate targets, block privileged services
4. **Minimal Privilege** - Session bus by default, least access

---

## 3. Core Responsibilities

### 3.1 Safe IPC Principles

When using D-Bus:
- **Validate service targets** before method calls
- **Use session bus** unless system access required
- **Block privileged services** (PolicyKit, systemd)
- **Log all method invocations**
- **Enforce call timeouts**

### 3.2 Security-First Approach

Every D-Bus operation MUST:
1. Validate target service/interface
2. Check against blocked service list
3. Use appropriate bus type
4. Log operation details
5. Enforce timeout limits

### 3.3 Bus Type Policy

- **Session Bus**: User applications, non-privileged
- **System Bus**: System services, requires elevated permissions
- **Default**: Always prefer session bus

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

### 4.1 D-Bus Architecture

```
Application -> D-Bus Library -> D-Bus Daemon -> Target Service
```

**Key Concepts**:
- **Bus Name**: Service identifier (e.g., `org.freedesktop.Notifications`)
- **Object Path**: Object location (e.g., `/org/freedesktop/Notifications`)
- **Interface**: Method grouping (e.g., `org.freedesktop.Notifications`)
- **Member**: Method or signal name

### 4.2 Libraries

| Library | Purpose | Security Notes |
|---------|---------|----------------|
| `dbus-python` | Python bindings | Validate peer credentials |
| `pydbus` | Modern Python D-Bus | Use with service filtering |
| `dasbus` | Async D-Bus | Enforce timeouts |
| `gi.repository.Gio` | GIO D-Bus bindings | Built-in security |

---

## 6. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```python
# tests/test_dbus_client.py
import pytest
from unittest.mock import MagicMock, patch

class TestSecureDBusClient:
    """Test D-Bus client with mocked bus."""

    @pytest.fixture
    def mock_bus(self):
        with patch('dbus.SessionBus') as mock:
            yield mock.return_value

    def test_blocks_privileged_services(self, mock_bus):
        """Should reject access to blocked services."""
        from secure_dbus import SecureDBusClient

        client = SecureDBusClient()

        with pytest.raises(SecurityError) as exc:
            client.get_object('org.freedesktop.PolicyKit1', '/')

        assert 'blocked' in str(exc.value).lower()

    def test_validates_bus_name_format(self, mock_bus):
        """Should reject malformed bus names."""
        from secure_dbus import SecureDBusClient

        client = SecureDBusClient()

        with pytest.raises(ValueError):
            client.get_object('invalid..name', '/')

    def test_enforces_timeout(self, mock_bus):
        """Should timeout long-running calls."""
        from secure_dbus import SecureDBusClient

        client = SecureDBusClient()
        client.timeout = 1

        mock_bus.get_object.return_value.SomeMethod.side_effect = \
            Exception('Timeout')

        with pytest.raises(TimeoutError):
            client.call_method(
                'org.test.Service', '/', 'org.test.Interface', 'SomeMethod'
            )
```

### Step 2: Implement Minimum to Pass

```python
# secure_dbus.py
class SecureDBusClient:
    BLOCKED_SERVICES = {'org.freedesktop.PolicyKit1'}

    def get_object(self, bus_name: str, object_path: str):
        if bus_name in self.BLOCKED_SERVICES:
            raise SecurityError(f"Access to {bus_name} is blocked")
        if not self._validate_bus_name(bus_name):
            raise ValueError(f"Invalid bus name: {bus_name}")
        return self.bus.get_object(bus_name, object_path)
```

### Step 3: Refactor Following Patterns

Add logging, credential validation, and property caching.

### Step 4: Run Full Verification

```bash
# Run tests
pytest tests/test_dbus_client.py -v

# Type checking
mypy secure_dbus.py --strict

# Coverage
pytest --cov=secure_dbus --cov-report=term-missing
```

---

## 7. Performance Best Practices

D-Bus operations can be performance-critical. Follow these key principles:

1. **Connection Reuse**: Create D-Bus connections once and reuse them
2. **Signal Filtering**: Filter signals at subscription time, not in handlers
3. **Async Operations**: Use async calls for non-blocking operations
4. **Message Batching**: Use `GetAll()` instead of individual property reads
5. **Property Caching**: Cache frequently accessed properties with TTL

**See**: `references/performance-optimization.md` for detailed patterns and benchmarks

---

## 8. Security-First D-Bus Client

**Key Components**:

1. **SecureDBusClient**: Core client with service blocklists and validation
2. **SecureSignalMonitor**: Signal handling with allowlists
3. **SecurePropertyAccess**: Property operations with access control
4. **ServiceDiscovery**: Safe service introspection

**Blocked Services** (CRITICAL - Never allow access):
- `org.freedesktop.PolicyKit1` - Privilege escalation
- `org.freedesktop.systemd1` - System service control
- `org.freedesktop.login1` - Session/power management
- `org.gnome.keyring`, `org.freedesktop.secrets` - Secret storage
- `org.freedesktop.PackageKit` - Package installation

**Implementation Example**:
```python
from secure_dbus import SecureDBusClient

# Create secure client (session bus, standard tier)
client = SecureDBusClient(bus_type='session', permission_tier='standard')

# Call method with automatic validation and logging
result = client.call_method(
    'org.freedesktop.Notifications',
    '/org/freedesktop/Notifications',
    'org.freedesktop.Notifications',
    'Notify',
    'App', 0, '', 'Summary', 'Body', [], {}, 5000
)
```

**See**: `references/advanced-patterns.md` for complete implementation patterns

---

## 9. Security Standards

### Critical Vulnerabilities to Mitigate

1. **Privilege Escalation via PolicyKit** (CVE-2021-4034) - CRITICAL
   - Mitigation: Block PolicyKit service access

2. **D-Bus Authentication Bypass** (CVE-2022-42012) - HIGH
   - Mitigation: Validate peer credentials

3. **Service Impersonation** (CWE-290) - HIGH
   - Mitigation: Verify service credentials

4. **Method Injection** (CWE-74) - MEDIUM
   - Mitigation: Input validation, service allowlists

5. **Information Disclosure** (CWE-200) - MEDIUM
   - Mitigation: Property access control

### Permission Tier Model

- **read-only**: Session bus, read operations only
- **standard**: Session bus, full operations (default)
- **elevated**: System bus access (requires explicit approval)

**See**: `references/threat-model.md` for complete STRIDE analysis and security controls
**See**: `references/security-examples.md` for secure implementation examples

---

## 10. Anti-Patterns to Avoid

Common D-Bus mistakes that lead to security issues and poor performance:

1. ❌ Using system bus when session bus is sufficient
2. ❌ Allowing access to PolicyKit and systemd
3. ❌ Skipping timeout enforcement
4. ❌ Creating new connections for each operation
5. ❌ Not validating bus names and paths
6. ❌ No audit logging
7. ❌ Receiving all signals without filtering
8. ❌ Skipping peer credential validation
9. ❌ Individual property reads instead of batching
10. ❌ Generic exception handling losing error details

**See**: `references/anti-patterns.md` for detailed examples and corrections

---

## 11. Pre-Deployment Checklist

Before deploying D-Bus code:
- [ ] Service blocklist configured and enforced
- [ ] Session bus preferred over system bus
- [ ] Timeout enforcement on all method calls
- [ ] Peer credential validation implemented
- [ ] Comprehensive audit logging enabled
- [ ] Property access control configured
- [ ] Connection pooling/reuse implemented
- [ ] Error handling with specific D-Bus exceptions

---

## 12. Summary

Your goal is to create D-Bus automation that is:
- **Secure**: Service blocklists, credential validation, access control
- **Reliable**: Timeout enforcement, error handling, retry logic
- **Performant**: Connection reuse, signal filtering, property caching
- **Minimal**: Session bus by default, least privilege principle

**Security Reminders**:
1. Always prefer session bus over system bus
2. Block access to PolicyKit and systemd services
3. Validate peer credentials for sensitive operations
4. Enforce timeouts on all method calls
5. Log all operations for security audit

---

## 13. References

### Core Documentation
- `references/advanced-patterns.md` - Complete implementation patterns
- `references/security-examples.md` - Security-focused code examples
- `references/threat-model.md` - STRIDE analysis and threat scenarios
- `references/performance-optimization.md` - Performance patterns and benchmarks
- `references/anti-patterns.md` - Common mistakes and how to avoid them

### External Resources
- [D-Bus Specification](https://dbus.freedesktop.org/doc/dbus-specification.html)
- [D-Bus Tutorial](https://dbus.freedesktop.org/doc/dbus-tutorial.html)
- [Python D-Bus Documentation](https://dbus.freedesktop.org/doc/dbus-python/)
