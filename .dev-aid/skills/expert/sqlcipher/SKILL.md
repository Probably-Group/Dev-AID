---
name: SQLCipher Encrypted Database Expert
risk_level: HIGH
description: Expert in SQLCipher encrypted database development with focus on encryption key management, key rotation, secure data handling, and cryptographic best practices
version: 1.0.0
author: JARVIS AI Assistant
tags: [database, sqlcipher, encryption, security, key-management, sqlite]
model: claude-sonnet-4-5-20250929
---

# SQLCipher Encrypted Database Expert

## 0. Mandatory Reading Protocol

**CRITICAL**: Before implementing encryption operations, read the relevant reference files:

| Trigger | Reference File |
|---------|----------------|
| First-time encryption setup, key derivation, memory handling | `references/security-examples.md` |
| SQLite migration, custom PRAGMAs, performance tuning, backups | `references/advanced-patterns.md` |
| Security architecture, threat assessment, key compromise planning | `references/threat-model.md` |

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

### 0.1 Quick Risk Assessment

**Risk Level**: HIGH

**Key Risk Factors**:
- Active exploitation of critical vulnerabilities in production (CVSS 7.5+)
- 3 high-severity CVEs/security concerns in 2024-2025
- Common attack vectors: Memory corruption via SQLite bugs, Weak encryption due to OpenSSL CVEs, Key extraction via side-channels
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

   - **CVE-2025-6965** (CVSS 9.8): SQLite memory corruption affecting SQLCipher < 4.9.0
     Source: https://www.zetetic.net/blog/2025/05/15/sqlcipher-4.9.0-release-security-update/
   - **CVE-2025-0306** (CVSS 7.5): OpenSSL vulnerability in SQLCipher 4.6.1
     Source: https://discuss.zetetic.net/t/new-vulnerability-detected-in-openssl/6877
   - **CVE-2024-13176** (CVSS 7.3): OpenSSL vulnerability in SQLCipher dependencies
     Source: https://discuss.zetetic.net/t/new-vulnerabilities-in-openssl/6530

**Step 3: Common Attack Patterns**

   - Memory corruption via SQLite bugs
   - Weak encryption due to OpenSSL CVEs
   - Key extraction via side-channels
   - Malicious schema exploitation

**Step 4: MITRE ATT&CK Mapping**
- Tactic: [Initial Access, Execution, Persistence, Privilege Escalation]
- Review MITRE ATT&CK framework for latest techniques

**Update Frequency**: Check for new CVEs weekly during active development.

### 0.3 Hallucination Prevention Checklist

**CRITICAL**: These rules are ABSOLUTE. Violation = security incident.

**Domain-Specific Security Rules**:

- ❌ NEVER use SQLCipher < 4.9.0
- ❌ NEVER store encryption keys in code
- ❌ NEVER allow untrusted schema modifications
- ❌ ALWAYS use latest OpenSSL
- ❌ ALWAYS validate database integrity before decryption

**Before ANY code generation**:
1. ✅ Verify rule compliance for proposed implementation
2. ✅ Check if solution introduces any prohibited patterns
3. ✅ Validate all security assumptions against current CVEs
4. ✅ Confirm defensive coding practices are applied

**If uncertain**: STOP and research. Never guess on security.


## 1. Overview

**Risk Level: HIGH**

**Justification**: SQLCipher handles encryption of sensitive data at rest. Improper key management can lead to data exposure, weak key derivation enables brute-force attacks, and cryptographic misconfigurations can completely compromise security guarantees.

You are an expert in SQLCipher encrypted database development, specializing in:
- **Encryption key management** with secure derivation and storage
- **Key rotation** without data loss or downtime
- **Cryptographic best practices** for AES-256 configuration
- **Secure memory handling** to prevent key exposure
- **Migration strategies** from plain SQLite to encrypted databases

### Primary Use Cases
- Encrypted local storage for sensitive user data
- HIPAA/GDPR compliant data storage
- Secure credential and secret management
- Privacy-focused applications

---

## 2. Core Principles

### 2.1 Development Principles

1. **TDD First** - Write tests before implementation for all encryption operations
2. **Performance Aware** - Optimize cipher configuration and page sizes for efficiency
3. **Use strong key derivation** - PBKDF2 with high iteration counts (256000+)
4. **Never hardcode encryption keys** - Derive from user input or secure storage
5. **Secure memory handling** - Zero out keys after use
6. **Implement key rotation** - Plan for compromised keys
7. **Monitor dependencies** - Track OpenSSL and SQLite CVEs

### 2.2 Data Protection Principles

1. **Encryption at rest** with AES-256-CBC
2. **HMAC verification** for integrity checking
3. **Secure key storage** using OS keychain/credential manager
4. **Backup encryption** with independent keys
5. **Secure deletion** with PRAGMA secure_delete

---

## 3. Technical Foundation

### 3.1 Version Recommendations

| Component | Recommended | Minimum | Notes |
|-----------|-------------|---------|-------|
| SQLCipher | 4.9+ | 4.5 | Security updates |
| OpenSSL | 3.0+ | 1.1.1 | CVE patches |
| sqlcipher crate | 0.3+ | 0.3 | Rust bindings |

### 3.2 Required Dependencies (Cargo.toml)

```toml
[dependencies]
rusqlite = { version = "0.31", features = ["bundled-sqlcipher"] }
zeroize = "1.7"  # Secure memory zeroing
keyring = "2.0"  # OS credential storage
argon2 = "0.5"   # Optional: stronger KDF
```

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

## 5. Implementation Workflow (TDD)

class TestEncryptedDatabase:
    def test_database_file_is_encrypted(self, tmp_path):
        db_path = tmp_path / "test.db"
        key = "x'0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef'"
        db = EncryptedDatabase(db_path, key)
        db.execute("CREATE TABLE secrets (data...

📚 **For complete details**: See `references/implementation-workflow-tdd.md`

---
## 6. Implementation Patterns

### 5.1 Encrypted Database Initialization

```rust
use rusqlite::{Connection, Result};
use zeroize::Zeroizing;

pub struct EncryptedDatabase { conn: Connection }

impl EncryptedDatabase {
    pub fn new(path: &Path, key: &Zeroizing<String>) -> Result<Self> {
        let conn = Connection::open(path)?;
        conn.pragma_update(None, "key", key.as_str())?;  // MUST be first

        conn.execute_batch("
            PRAGMA cipher_compatibility = 4;
            PRAGMA cipher_memory_security = ON;
            PRAGMA foreign_keys = ON;
            PRAGMA journal_mode = WAL;
        ")?;

        // Verify encryption is active
        let page_size: i32 = conn.pragma_query_value(None, "cipher_page_size", |row| row.get(0))?;
        if page_size == 0 { return Err(rusqlite::Error::InvalidQuery); }

        Ok(Self { conn })
    }
}
```

### 5.2 Secure Key Derivation

```rust
use argon2::{Argon2, PasswordHasher};
use zeroize::Zeroizing;

pub fn derive_key_from_password(
    password: &str,
    stored_salt: Option<&str>
) -> Result<(Zeroizing<String>, String), argon2::password_hash::Error> {
    let salt = match stored_salt {
        Some(s) => SaltString::from_b64(s)?,
        None => SaltString::generate(&mut OsRng),
    };

    let argon2 = Argon2::new(
        argon2::Algorithm::Argon2id, argon2::Version::V0x13,
        argon2::Params::new(65536, 3, 4, Some(32)).unwrap()  // 64MB, 3 iter, 4 threads
    );

    let mut key_bytes = [0u8; 32];
    argon2.hash_password_into(password.as_bytes(), salt.as_str().as_bytes(), &mut key_bytes)?;
    let key_hex = Zeroizing::new(format!("x'{}'", hex::encode(key_bytes)));
    key_bytes.zeroize();

    Ok((key_hex, salt.as_str().to_string()))
}
```

### 5.3 OS Keychain Integration

```rust
use keyring::Entry;
use zeroize::Zeroizing;

pub struct SecureKeyStorage { service: String }

impl SecureKeyStorage {
    pub fn new(app_name: &str) -> Self {
        Self { service: format!("{}-sqlcipher", app_name) }
    }

    pub fn store_key(&self, user: &str, key: &Zeroizing<String>) -> Result<(), keyring::Error> {
        Entry::new(&self.service, user)?.set_password(key.as_str())
    }

    pub fn retrieve_key(&self, user: &str) -> Result<Zeroizing<String>, keyring::Error> {
        Ok(Zeroizing::new(Entry::new(&self.service, user)?.get_password()?))
    }
}
```

### 5.4 Key Rotation Implementation

```rust
impl EncryptedDatabase {
    pub fn rotate_key(&self, new_key: &Zeroizing<String>, backup_path: &Path) -> Result<()> {
        self.backup_database(backup_path)?;                              // Step 1: Backup
        self.conn.pragma_update(None, "rekey", new_key.as_str())?;       // Step 2: Re-encrypt

        // Step 3: Verify new key works
        let test: i32 = self.conn.pragma_query_value(None, "cipher_page_size", |row| row.get(0))?;
        if test == 0 {
            std::fs::copy(backup_path, self.path())?;  // Restore on failure
            return Err(rusqlite::Error::InvalidQuery);
        }
        Ok(())
    }
}
```

---

## 7. Performance Patterns

### 6.1 Page Size Optimization

```python
# Good: Optimize page size for workload
conn.execute("PRAGMA cipher_page_size = 4096")  # Default, good for mixed
conn.execute("PRAGMA cipher_pag## 6. Implementation Patterns

## 6. Implementation Patterns

📚 **For complete details**: See `references/implementation-patterns.md`

---
)?;
// CORRECT:
let (key, salt) = derive_key_from_password(password, stored_salt)?;
conn.pragma_update(None, "key", key.as_str())?;  // key auto-zeroed on drop
```

---

## 9. Common Mistakes

### Hardcoded Keys
```rust
// WRONG: conn.pragma_update(None, "key", "my-secret")?;
// CORRECT: Use derived key with Zeroizing wrapper
```

### Weak Key Derivation
```rust
// WRONG: let key = sha256(password);
// WRONG: conn.pragma_update(None, "kdf_iter", 10000)?;
// CORRECT: Argon2id or PBKDF2 with 256000+ iterations
```

### Missing Verification
```rust
// Always verify encryption is active after setting key
let page_size: i32 = conn.pragma_query_value(None, "cipher_page_size", |row| row.get(0))?;
if page_size == 0 { return Err(Error::EncryptionNotActive); }
```

### Insecure Backups
```rust
// WRONG: Export with empty key (unencrypted backup)
// CORRECT: Use encrypted backup with separate key
```

---

## 10. Pre-Implementation Checklist

### Phase 1: Before Writing Code

- [ ] Read threat model in `references/threat-model.md`
- [ ] Identify encryption requirements (compliance, data sensitivity)
- [ ] Choose KDF parameters (Argon2id recommended)
- [ ] Plan key storage strategy (OS keychain, hardware token)
- [ ] Design key rotation procedure
- [ ] Write failing tests for all encryption operations

### Phase 2: During Implementation

- [ ] PRAGMA key is first operation after connection
- [ ] cipher_compatibility = 4, cipher_memory_security = ON
- [ ] All keys wrapped in Zeroizing containers
- [ ] Verification query after setting key
- [ ] Parameterized queries only (no string interpolation)
- [ ] Performance patterns applied (page size, WAL mode)

### Phase 3: Before Committing

- [ ] All tests pass including encryption verification
- [ ] No hardcoded keys in codebase
- [ ] Key derivation uses 256000+ iterations
- [ ] OpenSSL and SQLite CVEs reviewed
- [ ] secure_delete = ON for sensitive tables
- [ ] Backup encryption tested
- [ ] File permissions set to 600
- [ ] Key rotation procedure documented and tested

---

## 11. Summary

Your goal is to create SQLCipher implementations that are:

- **Test-Driven**: All encryption operations verified by tests first
- **Performance-Optimized**: Proper page sizes, WAL mode, key caching
- **Cryptographically Secure**: Strong AES-256 with proper key derivation
- **Key Management Best Practices**: Secure storage, rotation, memory handling
- **Resilient**: Planned for key compromise and recovery scenarios

**Security Reminder**: Encryption is only as strong as key management. NEVER hardcode keys. ALWAYS use strong KDF. ALWAYS plan for rotation.

---

## References

- **Security Examples**: `references/security-examples.md` - Complete implementations
- **Advanced Patterns**: `references/advanced-patterns.md` - Migration, performance
- **Threat Model**: `references/threat-model.md` - Security architecture
## 7. Performance Patterns

## 7. Performance Patterns

📚 **For complete details**: See `references/performance-patterns.md`

---
## 9. Common Mistakes

## 9. Common Mistakes

📚 **For complete details**: See `references/common-mistakes.md`

---
