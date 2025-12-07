# Encryption Skill

---
name: encryption
version: 1.0.0
domain: security/cryptography
risk_level: HIGH
languages: [python, typescript, rust, go]
frameworks: [sqlcipher, cryptography, libsodium]
requires_security_review: true
compliance: [GDPR, HIPAA, PCI-DSS, SOC2]
last_updated: 2025-01-15
---

> **MANDATORY READING PROTOCOL**: Before implementing ANY encryption, read `references/advanced-patterns.md` for key derivation and `references/security-examples.md` for implementation patterns.


## 0. Anti-Hallucination Protocol

### 0.1 Quick Risk Assessment

**Risk Level**: HIGH

**Key Risk Factors**:
- Active exploitation of critical vulnerabilities in production (CVSS 7.5+)
- 3 high-severity CVEs discovered in 2024-2025
- Common attack vectors: Timing attacks for key recovery, Padding oracle attacks, Downgrade attacks to weak ciphers
- Requires continuous monitoring of security advisories

**Immediate Security Actions**:
1. Review recent CVEs below before any implementation
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

   - **CVE-2025-9230** (CVSS 7.5): OpenSSL - DoS via malformed TLS handshake
     Source: https://www.openssl.org/news/secadv/20250116.txt
   - **CVE-2025-9231** (CVSS 5.9): OpenSSL - Private key recovery via timing attacks
     Source: https://www.openssl.org/news/secadv/20250116.txt
   - **CVE-2024-12797** (CVSS 7.5): OpenSSL - Certificate validation bypass
     Source: https://nvd.nist.gov/vuln/detail/CVE-2024-12797

**Step 3: Common Attack Patterns**

   - Timing attacks for key recovery
   - Padding oracle attacks
   - Downgrade attacks to weak ciphers
   - Side-channel attacks via cache timing

**Step 4: MITRE ATT&CK Mapping**
- Tactic: [Initial Access, Execution, Persistence, Privilege Escalation]
- Review MITRE ATT&CK framework for latest techniques

**Update Frequency**: Check for new CVEs weekly during active development.

### 0.3 Hallucination Prevention Checklist

**CRITICAL**: These rules are ABSOLUTE. Violation = security incident.

**Domain-Specific Security Rules**:

- ❌ NEVER use ECB mode for encryption
- ❌ NEVER implement custom cryptography
- ❌ NEVER use hardcoded encryption keys
- ❌ ALWAYS use authenticated encryption (GCM, ChaCha20-Poly1305)
- ❌ ALWAYS validate certificates with proper chain verification

**Before ANY code generation**:
1. ✅ Verify rule compliance for proposed implementation
2. ✅ Check if solution introduces any prohibited patterns
3. ✅ Validate all security assumptions against current CVEs
4. ✅ Confirm defensive coding practices are applied

**If uncertain**: STOP and research. Never guess on security.

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

This skill provides secure-by-default patterns for implementing encryption in JARVIS AI Assistant, covering:

- **SQLCipher**: Encrypted SQLite database with AES-256-GCM
- **Argon2id**: Memory-hard key derivation function
- **Key Management**: Secure generation, storage, rotation, and destruction
- **Secure Memory**: Protection against memory disclosure attacks

### 1.2 Risk Assessment

**Risk Level**: HIGH

**Justification**:
- Cryptographic failures expose all protected data
- Key compromise leads to complete confidentiality loss
- Implementation errors are catastrophic and often undetectable
- Regulatory violations (GDPR, HIPAA, PCI-DSS) carry severe penalties

**Attack Surface**:
- Key derivation weaknesses
- Insecure random number generation
- Timing side-channels
- Memory disclosure (cold boot, crash dumps)
- Key reuse across contexts

## 2. Core Responsibilities

### 2.1 Primary Functions

1. **Encrypt data at rest** using AES-256-GCM with authenticated encryption
2. **Derive keys securely** using Argon2id with appropriate parameters
3. **Manage key lifecycle** including rotation, escrow, and destruction
4. **Protect key material** in memory and during operations
5. **Integrate with OS keychains** for master key storage

### 2.2 Core Principles

1. **TDD First** - Write tests before implementation; test encryption/decryption round-trips, authentication failures, and edge cases
2. **Performance Aware** - Cache derived keys, use streaming for large data, leverage hardware acceleration
3. **Security by Default** - Use authenticated encryption modes, memory-hard KDFs, secure random sources
4. **Defense in Depth** - Multiple layers of protection, fail securely, minimize key exposure

### 2.3 Security Principles

- **NEVER** implement custom cryptographic algorithms
- **NEVER** use ECB mode or unauthenticated encryption
- **ALWAYS** use cryptographically secure random number generators
- **ALWAYS** validate ciphertext authenticity before decryption
- **ALWAYS** use constant-time comparison for authentication tags

## 3. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```python
import pytest
from cryptography.exceptions import InvalidTag

class TestEncryptionTDD:
    """TDD tests for encryption implementation."""

    def test_encrypt_decrypt_roundtrip(self):
        """Test that encryption followed by decryption returns original data."""
        from jarvis.security.encryption import SecureEncryption

        key = secrets.token_bytes(32)
        encryptor = SecureEncryption(key)

        plaintext = b"sensitive data for JARVIS"
        ciphertext = encryptor.encrypt(plaintext)
        decrypted = encryptor.decrypt(ciphertext)

        assert decrypted == plaintext
        assert ciphertext != plaintext  # Must be encrypted

    def test_tampered_ciphertext_raises_error(self):
        """Test that tampered ciphertext is rejected."""
        from jarvis.security.encryption import SecureEncryption

        key = secrets.token_bytes(32)
        encryptor = SecureEncryption(key)

        ciphertext = encryptor.encrypt(b"secret")
        tampered = ciphertext[:-1] + bytes([ciphertext[-1] ^ 0xFF])

        with pytest.raises(InvalidTag):
            encryptor.decrypt(tampered)

    def test_key_derivation_consistency(self):
        """Same password + salt = same key; different salt = different key."""
        from jarvis.security.encryption import SecureKeyDerivation
        password = "strong_password_123"
        salt = secrets.token_bytes(16)
        key1, _ = SecureKeyDerivation.derive_key(password, salt)
        key2, _ = SecureKeyDerivation.derive_key(password, salt)
        assert key1 == key2 and len(key1) == 32

        key3, salt3 = SecureKeyDerivation.derive_key(password)
        assert key1 != key3  # Different salt = different key
```

### Step 2: Implement Minimum to Pass

Implement only what's needed to pass the tests. Start with basic encryption/decryption, then add key derivation.

### Step 3: Refactor Following Patterns

After tests pass, add: memory protection, error handling, AAD support, key caching.

### Step 4: Run Full Verification

```bash
# Run encryption tests with coverage
pytest tests/security/test_encryption.py -v --cov=jarvis.security.encryption --cov-fail-under=90

# Run security-specific tests
pytest tests/security/ -k "encryption or crypto" -v

# Check for timing vulnerabilities
pytest tests/security/test_timing.py -v

# Verify no secrets in output
pytest --log-cli-level=DEBUG 2>&1 | grep -i "key\|secret\|password" && echo "WARNING: Secrets in logs!"
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

## 5. Technology Stack

### 4.1 Recommended Libraries

| Language | Library | Version | Notes |
|----------|---------|---------|-------|
| Python | `cryptography` | >=42.0.0 | Uses OpenSSL 3.x backend |
| Python | `argon2-cffi` | >=23.1.0 | Reference Argon2 implementation |
| TypeScript | `@noble/ciphers` | >=0.5.0 | Audited pure-JS implementation |
| Rust | `ring` | >=0.17.0 | BoringSSL-backed |
| Go | `crypto/cipher` | stdlib | Use with `golang.org/x/crypto` |

### 4.2 SQLCipher Configuration

**Minimum Version**: SQLCipher 4.5.6+ (includes SQLite 3.44.2)

```python
# SQLCipher secure configuration
SQLCIPHER_PRAGMAS = {
    'key': None,  # Set via secure key injection
    'cipher': 'aes-256-gcm',
    'kdf_iter': 256000,  # PBKDF2 iterations
    'cipher_page_size': 4096,
    'cipher_kdf_algorithm': 'PBKDF2_HMAC_SHA512',
    'cipher_hmac_algorithm': 'HMAC_SHA512',
    'cipher_plaintext_header_size': 0,
}
```

## 6. Performance Patterns

**Bad:** Deriving key on every operation (~500ms per Argon2id call)

📚 **For complete details**: See `references/performance-patterns.md`

---
## 7. Implementation Patterns

### 6.1 Key Derivation with Argon2id

```python
from argon2 import PasswordHasher
from argon2.low_level import hash_secret_raw, Type
import secrets

class SecureKeyDerivation:
    """Derive encryption keys from passwords using Argon2id."""

    # OWASP recommended parameters for sensitive data
    TIME_COST = 3        # Iterations
    MEMORY_COST = 65536  # 64 MiB
    PARALLELISM = 4      # Threads
    HASH_LEN = 32        # 256 bits for AES-256
    SALT_LEN = 16        # 128 bits minimum

    @classmethod
    def derive_key(cls, password: str, salt: bytes = None) -> tuple[bytes, bytes]:
        """
        Derive a 256-bit key from password.

        Returns:
            tuple: (derived_key, salt) for storage
        """
        if salt is None:
            salt = secrets.token_bytes(cls.SALT_LEN)

        # Validate inputs
        if not password or len(password) < 12:
            raise ValueError("Password must be at least 12 characters")

        key = hash_secret_raw(
            secret=password.encode('utf-8'),
            salt=salt,
            time_cost=cls.TIME_COST,
            memory_cost=cls.MEMORY_COST,
            parallelism=cls.PARALLELISM,
            hash_len=cls.HASH_LEN,
            type=Type.ID  # Argon2id
        )

        return key, salt
```

### 6.2 AES-256-GCM Encryption

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import secrets

class SecureEncryption:
    """AES-256-GCM authenticated encryption."""

    NONCE_SIZE = 12  # 96 bits recommended for GCM
    KEY_SIZE = 32    # 256 bits

    def __init__(self, key: bytes):
        if len(key) != self.KEY_SIZE:
            raise ValueError(f"Key must be {self.KEY_SIZE} bytes")
        self._aesgcm = AESGCM(key)

    def encrypt(self, plaintext: bytes, associated_data: bytes = None) -> bytes:
        """
        Encrypt with random nonce, prepended to ciphertext.

        Returns:
            bytes: nonce || ciphertext || tag
        """
        nonce = secrets.token_bytes(self.NONCE_SIZE)
        ciphertext = self._aesgcm.encrypt(nonce, plaintext, associated_data)
        return nonce + ciphertext

    def decrypt(self, ciphertext: bytes, associated_data: bytes = None) -> bytes:
        """
        Decrypt ## 7. Implementation Patterns

class SecureKeyDerivation:
    """Derive encryption keys from passwords using Argon2id."""

📚 **For complete details**: See `references/implementation-patterns.md`

---
nces/threat-model.md`
- [ ] Identify data classification (PII, PHI, credentials)
- [ ] Choose appropriate algorithm (AES-256-GCM or ChaCha20-Poly1305)
- [ ] Design key derivation strategy (Argon2id parameters)
- [ ] Plan key storage (OS keychain integration)
- [ ] Write failing tests for encrypt/decrypt round-trips
- [ ] Write tests for authentication tag verification
- [ ] Write tests for key derivation consistency

### Phase 2: During Implementation

- [ ] Use `cryptography` library (not custom implementations)
- [ ] Generate nonces with `secrets.token_bytes(12)`
- [ ] Implement key caching with TTL for performance
- [ ] Use streaming for files >10MB
- [ ] Zero key material after use (SecureKeyHolder pattern)
- [ ] Add associated data (AAD) for context binding
- [ ] Handle InvalidTag exceptions without leaking info
- [ ] Run tests after each function implementation

### Phase 3: Before Committing

- [ ] All TDD tests pass with 90%+ coverage
- [ ] Nonce uniqueness validated over 10,000+ operations
- [ ] Key derivation timing variance <10%
- [ ] No secrets in logs (`grep -i "key\|secret\|password"`)
- [ ] Dependency scanning clean (no CVEs)
- [ ] Performance benchmarks meet targets:
  - Key derivation: <1s
  - Encryption: >100MB/s
  - Batch operations: Linear scaling
- [ ] Security review requested for HIGH risk code

## 12. Summary

**Key Objectives**: AES-256-GCM with random nonces, Argon2id KDF, OS keychain integration, authenticated encryption, key rotation support.

**Security Reminders**: No custom crypto, use audited libraries, test auth tags, rotate keys on schedule.

**References**: `references/advanced-patterns.md`, `references/security-examples.md`, `references/threat-model.md`

---

**Encryption done wrong is worse than no encryption - it provides false confidence.**
