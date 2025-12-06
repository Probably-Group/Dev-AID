# OS Keychain Skill

---
name: os-keychain
version: 1.1.0
domain: security/credential-storage
risk_level: HIGH
languages: [python, typescript, rust, go]
frameworks: [keyring, security-framework, libsecret]
requires_security_review: true
compliance: [GDPR, HIPAA, PCI-DSS, SOC2]
last_updated: 2025-01-15
---

> **MANDATORY READING PROTOCOL**: Before implementing credential storage, read `references/advanced-patterns.md` for cross-platform patterns and `references/security-examples.md` for platform-specific implementations.

## 0. Anti-Hallucination Protocol

**🚨 MANDATORY: Read before implementing any code using this skill**

### Verification Requirements

When using this skill to implement credential storage, you MUST:

1. **Verify Before Implementing**
   - ✅ Check official keyring/platform documentation
   - ✅ Confirm keychain APIs are current for target OS
   - ✅ Validate security patterns against official guides
   - ❌ Never guess keychain service names or formats
   - ❌ Never invent keyring backend names
   - ❌ Never assume cross-platform compatibility without testing

2. **Use Available Tools**
   - 🔍 Read: Check existing codebase for credential patterns
   - 🔍 Grep: Search for keyring usage examples
   - 🔍 WebSearch: Verify keyring library APIs
   - 🔍 WebFetch: Read official platform documentation

3. **Verify if Certainty < 80%**
   - If uncertain about ANY keychain API, backend, or pattern
   - STOP and verify before implementing
   - Document verification source in response
   - Errors in credential storage expose all dependent systems

4. **Common Keychain Hallucination Traps** (AVOID)
   - ❌ Inventing keyring backend names (e.g., "SystemKeyring", "OSKeyring")
   - ❌ Making up keyring library methods (e.g., `keyring.list_passwords()`)
   - ❌ Assuming all platforms support same features
   - ❌ Invented service name formats or conventions
   - ❌ Non-existent security features (e.g., automatic encryption levels)

### Self-Check Checklist

Before EVERY response with keychain code:
- [ ] All keyring APIs verified against current library docs
- [ ] Platform-specific features verified (macOS/Windows/Linux)
- [ ] Backend detection logic verified against keyring documentation
- [ ] Can cite official documentation sources

**⚠️ CRITICAL**: Keychain code with hallucinated APIs causes credential exposure and system compromise. Always verify.

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

### 1.1 Purpose and Scope

This skill provides secure credential storage using OS-native keychain services:

- **Windows**: Credential Manager (DPAPI-backed)
- **macOS**: Keychain Services (Secure Enclave integration)
- **Linux**: Secret Service API (GNOME Keyring, KWallet)

### 1.2 Risk Assessment

**Risk Level**: HIGH

**Justification**:
- Master keys and sensitive credentials stored
- Compromise exposes all dependent systems
- Platform API misuse leads to insecure storage
- Privilege escalation can access all credentials

**Attack Surface**:
- Inter-process communication (D-Bus, XPC)
- Access control misconfigurations
- Memory disclosure attacks
- Privilege escalation to access keychain

## 2. Core Principles

1. **TDD First** - Write tests before implementing credential operations
2. **Performance Aware** - Cache credentials, batch operations, minimize keychain calls
3. **Platform-native storage** - Use OS keychain services for all credentials
4. **Access isolation** - Unique service names prevent cross-contamination
5. **Secure by default** - Reject insecure backends automatically
6. **Cross-platform support** - Unified API across Windows, macOS, Linux

### 2.1 Security Principles

- **NEVER** store secrets in environment variables or files
- **NEVER** log credential values or access patterns with identifiers
- **ALWAYS** use platform-native keychain services
- **ALWAYS** validate application identity before credential access
- **ALWAYS** use unique service names per credential type

## 3. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```python
import pytest
from unittest.mock import MagicMock, patch

class TestCredentialStoreOperations:
    """TDD tests for credential store - write these FIRST."""

    def test_store_credential_success(self):
        """Test storing a credential in keychain."""
        store = SecureCredentialStore("test-service")
        store.store("api-key", "sk-test-12345")

        assert store.exists("api-key") is True
        assert store.retrieve("api-key") == "sk-test-12345"

    def test_retrieve_nonexistent_raises_keyerror(self):
        """Test retrieving nonexistent credential raises KeyError."""
        store = SecureCredentialStore("test-service")

        with pytest.raises(KeyError, match="Credential not found"):
            store.retrieve("nonexistent-key")

    def test_credential_isolation_between_namespaces(self):
        """Test credentials are isolated by namespace."""
        store1 = SecureCredentialStore("namespace-a")
        store2 = SecureCredentialStore("namespace-b")

        store1.store("shared-key", "value-a")
        store2.store("shared-key", "value-b")

        assert store1.retrieve("shared-key") == "value-a"
        assert store2.retrieve("shared-key") == "value-b"
```

**For complete test suite**: See `references/testing-guide.md`

### Step 2: Implement Minimum to Pass

```python
import keyring
from keyring.errors import KeyringError
import logging

logger = logging.getLogger(__name__)

class SecureCredentialStore:
    """Minimal implementation to pass tests."""

    SERVICE_PREFIX = "com.jarvis.assistant"

    def __init__(self, namespace: str):
        self._service = f"{self.SERVICE_PREFIX}.{namespace}"
        self._verify_backend()

    def _verify_backend(self):
        backend = keyring.get_keyring()
        backend_name = type(backend).__name__
        insecure = ['PlaintextKeyring', 'NullKeyring', 'ChainerBackend']
        if backend_name in insecure:
            raise RuntimeError(f"Insecure keyring backend: {backend_name}")

    def store(self, key: str, secret: str) -> None:
        keyring.set_password(self._service, key, secret)

    def retrieve(self, key: str) -> str:
        secret = keyring.get_password(self._service, key)
        if secret is None:
            raise KeyError(f"Credential not found: {key}")
        return secret

    def delete(self, key: str) -> None:
        keyring.delete_password(self._service, key)

    def exists(self, key: str) -> bool:
        return keyring.get_password(self._service, key) is not None
```

### Step 3: Refactor with Performance Patterns

After tests pass, add caching and logging. See `references/performance-optimization.md` for:
- Credential caching with TTL
- Batch operations
- Lazy loading
- Memory-safe handling

### Step 4: Run Full Verification

```bash
# Run all tests with coverage
pytest tests/security/test_keychain.py -v --cov=src/security/keychain

# Run security-specific tests
pytest tests/security/ -k "keychain or credential" -v

# Verify no credential leaks in logs
grep -r "sk-\|password\|secret" logs/ && echo "FAIL: Credentials in logs"
```


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

## 5. Core Responsibilities

### 4.1 Primary Functions

1. **Store secrets securely** using OS-native encryption
2. **Retrieve secrets** with proper access control verification
3. **Manage credential lifecycle** including rotation and deletion
4. **Abstract platform differences** for cross-platform code
5. **Integrate with encryption skill** for master key storage

## 6. Technology Stack

### 5.1 Recommended Libraries

| Platform | Library | API | Notes |
|----------|---------|-----|-------|
| Python (cross-platform) | `keyring` | Unified | Auto-detects backend |
| macOS | `Security.framework` | Keychain Services | Native Swift/ObjC |
| Windows | `Windows.Security.Credentials` | Credential Manager | WinRT API |
| Linux | `libsecret` | Secret Service D-Bus | GNOME Keyring backend |

### 5.2 Platform Requirements

- **macOS**: 10.15+ (Keychain Access improvements)
- **Windows**: 10 1903+ (Credential Guard support)
- **Linux**: libsecret 0.20+, GNOME Keyring 3.36+

## 7. Implementation Patterns

### 6.1 Cross-Platform Python Implementation

```python
import keyring
from keyring.errors import KeyringError
import logging

logger = logging.getLogger(__name__)

class SecureCredentialStore:
    """Cross-platform credential storage using OS keychain."""

    SERVICE_PREFIX = "com.jarvis.assistant"

    def __init__(self, namespace: str):
        self._service = f"{self.SERVICE_PREFIX}.{namespace}"
        self._verify_backend()

    def _verify_backend(self):
        """Verify secure keyring backend is available."""
        backend = keyring.get_keyring()
        backend_name = type(backend).__name__

        insecure_backends = ['PlaintextKeyring', 'NullKeyring', 'ChainerBackend']
        if backend_name in insecure_backends:
            raise RuntimeError(f"Insecure keyring backend: {backend_name}")

        logger.info("keychain.backend.initialized", extra={'backend': backend_name})

    def store(self, key: str, secret: str) -> None:
        """Store a credential securely."""
        keyring.set_password(self._service, key, secret)
        logger.info("keychain.credential.stored", extra={'key': key})

    def retrieve(self, key: str) -> str:
        """Retrieve a credential. Raises KeyError if not found."""
        secret = keyring.get_password(self._service, key)
        if secret is None:
            raise KeyError(f"Credential not found: {key}")
        return secret

    def delete(self, key: str) -> None:
        """Delete a credential."""
        keyring.delete_password(self._service, key)
        logger.info("keychain.credential.deleted", extra={'key': key})

    def exists(self, key: str) -> bool:
        """Check if credential exists."""
        return keyring.get_password(self._service, key) is not None
```

### 6.2 Platform-Specific Implementations

For detailed platform-specific implementations with advanced features:

- **macOS Keychain** (ACLs, Touch ID, Secure Enclave): See `references/security-examples.md#macos-keychain`
- **Windows Credential Manager** (DPAPI, Credential Guard): See `references/security-examples.md#windows-credential-manager`
- **Linux Secret Service** (D-Bus, GNOME Keyring): See `references/security-examples.md#linux-secret-service`

## 8. Security Standards

### 7.1 Known Vulnerabilities

| CVE | Severity | Platform | Mitigation |
|-----|----------|----------|------------|
| CVE-2023-21726 | High (7.8) | Windows | Windows Update Jan 2023 |
| CVE-2024-54490 | High | macOS | Update to macOS 15.2+ |
| CVE-2024-44162 | High | macOS | Update to macOS 14.7+ |
| CVE-2024-44243 | High | macOS | Update to macOS 15.2+ |
| CVE-2024-1086 | High (7.8) | Linux | Kernel 6.6.15+ |

### 7.2 OWASP Mapping

| OWASP 2025 | Implementation |
|------------|----------------|
| A01: Broken Access Control | OS-level ACLs, app sandboxing |
| A02: Cryptographic Failures | Platform-native encryption |
| A04: Insecure Design | Defense in depth, least privilege |
| A07: Identification Failures | Credential isolation per service |

### 7.3 Platform Security Features

**macOS**: Secure Enclave, per-item ACLs, code signing, Touch ID gating

**Windows**: DPAPI encryption, Credential Guard, virtualization-based security

**Linux**: D-Bus access control, collection locking, session keyring isolation

For detailed threat analysis, see `references/threat-model.md`.

## 9. Pre-Implementation Checklist

### Phase 1: Before Writing Code

- [ ] Read `references/advanced-patterns.md` for cross-platform patterns
- [ ] Read `references/security-examples.md` for platform implementations
- [ ] Read `references/anti-patterns.md` for common mistakes
- [ ] Review threat model in `references/threat-model.md`
- [ ] Identify required credential namespaces
- [ ] Design test cases for credential operations
- [ ] Plan caching strategy for performance

### Phase 2: During Implementation

- [ ] Write failing tests first (TDD workflow)
- [ ] Implement minimum code to pass tests
- [ ] Add credential caching with TTL
- [ ] Implement batch loading for multiple credentials
- [ ] Use lazy loading for optional credentials
- [ ] Add memory-safe handling for sensitive operations
- [ ] Verify secure keyring backend at startup
- [ ] Log operations without credential values

### Phase 3: Before Committing

- [ ] All tests pass with `pytest -v`
- [ ] No credentials in test fixtures or logs
- [ ] Cross-platform tests verified
- [ ] Memory leak tests pass
- [ ] Security scan shows no credential leaks
- [ ] Code review for anti-patterns complete

### Platform-Specific Verification

- [ ] **macOS**: Code signing verified for Keychain access
- [ ] **Windows**: Credential Guard compatibility tested
- [ ] **Linux**: Secret Service daemon running, D-Bus accessible
- [ ] OS security updates applied (check CVE list above)

## 10. Summary

### Key Objectives

1. **TDD workflow**: Write tests before implementing credential operations
2. **Performance optimization**: Cache credentials, batch operations, lazy loading
3. **Platform-native storage**: Use OS keychain services for all credentials
4. **Access isolation**: Unique service names prevent cross-contamination
5. **Secure by default**: Reject insecure backends automatically

### Security Reminders

- Credentials in environment variables are NOT secure
- File-based credential storage is NOT secure
- Always verify keyring backend at application startup
- Log credential operations but NEVER values
- Keep OS updated to address keychain vulnerabilities

### Quick Anti-Pattern Check

❌ **NEVER**:
- Store credentials in environment variables
- Hardcode credentials in source code
- Store credentials in plain files (even base64-encoded)
- Log credential values
- Use single service name for all credentials

✅ **ALWAYS**:
- Use OS keychain services
- Verify secure backend at startup
- Use unique namespaces per credential type
- Cache credentials for performance
- Log metadata only, never values

## 11. References

See `references/` directory for detailed guides:

- **`advanced-patterns.md`** - Cross-platform patterns, migration strategies, advanced usage
- **`security-examples.md`** - Complete platform-specific implementations (macOS, Windows, Linux)
- **`threat-model.md`** - Comprehensive threat analysis and attack scenarios
- **`performance-optimization.md`** - Caching, batching, lazy loading, memory-safe patterns
- **`anti-patterns.md`** - Common mistakes and how to avoid them
- **`testing-guide.md`** - Complete testing strategies with TDD examples

---

**The OS keychain is your first line of defense. Misuse negates all downstream encryption.**
