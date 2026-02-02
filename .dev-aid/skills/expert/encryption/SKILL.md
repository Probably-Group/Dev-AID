---
name: encryption
version: 2.0.0
description: "Cryptography patterns for encryption, key management, secure key derivation, and certificate handling."
risk_level: CRITICAL
---

# Encryption Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-327: Broken Crypto**
- NEVER: MD5, SHA1 for security, DES, RC4, ECB mode
- ALWAYS: SHA-256+, AES-256-GCM, ChaCha20-Poly1305

**CWE-321: Hardcoded Keys**
- NEVER: Encryption keys in source code
- ALWAYS: Key management service, HSM, secure key derivation

**CWE-328: Weak KDF**
- NEVER: Single SHA256(password) for key derivation
- ALWAYS: Argon2id, PBKDF2 (100k+ iterations), scrypt

**CWE-329: Missing IV/Nonce**
- NEVER: Reuse IV/nonce with same key
- ALWAYS: Random IV per encryption, store IV with ciphertext

**CWE-347: Missing Signature Verification**
- NEVER: Trust encrypted data without authentication
- ALWAYS: Use AEAD (GCM, Poly1305) or encrypt-then-MAC

### 0.3 Risk Level: CRITICAL

**Verification requirements for CRITICAL risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 Modern Cryptography Only (CWE-327, CWE-328)

**Principle:** Use modern, audited cryptography. Never roll your own.

```python
# ❌ WRONG - Weak/broken algorithms
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()
password_hash = hashlib.sha1(password.encode()).hexdigest()
password_hash = hashlib.sha256(password.encode()).hexdigest()  # No salt!

from Crypto.Cipher import DES  # DES is broken
cipher = DES.new(key, DES.MODE_ECB)  # ECB mode is insecure

# ✅ CORRECT - Argon2id for passwords
from argon2 import PasswordHasher
ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4)
hash = ph.hash(password)

# ✅ CORRECT - AES-256-GCM for encryption
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
key = AESGCM.generate_key(bit_length=256)
aesgcm = AESGCM(key)
nonce = os.urandom(12)  # 96 bits for GCM
ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)
```

```rust
// ❌ WRONG - Weak algorithms
use md5::Md5;
use sha1::Sha1;

// ✅ CORRECT - Argon2id for passwords
use argon2::{Argon2, PasswordHasher, PasswordVerifier};
use argon2::password_hash::SaltString;

let salt = SaltString::generate(&mut OsRng);
let argon2 = Argon2::default();
let hash = argon2.hash_password(password.as_bytes(), &salt)?;

// ✅ CORRECT - ChaCha20-Poly1305 for encryption
use chacha20poly1305::{ChaCha20Poly1305, Key, Nonce, aead::Aead};

let key = ChaCha20Poly1305::generate_key(&mut OsRng);
let cipher = ChaCha20Poly1305::new(&key);
let nonce = ChaCha20Poly1305::generate_nonce(&mut OsRng);
let ciphertext = cipher.encrypt(&nonce, plaintext)?;
```

### 1.2 Secure Random Number Generation (CWE-330)

**Principle:** Always use cryptographically secure random sources.

```python
# ❌ WRONG - Predictable random
import random
key = bytes([random.randint(0, 255) for _ in range(32)])
token = ''.join(random.choices(string.ascii_letters, k=32))

# ✅ CORRECT - Cryptographically secure
import secrets
import os

key = os.urandom(32)  # For keys
token = secrets.token_urlsafe(32)  # For tokens
nonce = secrets.token_bytes(12)  # For nonces
```

```rust
// ❌ WRONG - Predictable random
use rand::Rng;
let key: [u8; 32] = rand::thread_rng().gen();

// ✅ CORRECT - Cryptographically secure
use rand::rngs::OsRng;
let key: [u8; 32] = OsRng.gen();
```

### 1.3 Key Management (CWE-321, CWE-798)

**Principle:** Never hardcode keys. Use proper key derivation and storage.

```python
# ❌ WRONG - Hardcoded key
KEY = b"mysecretkey12345"

# ❌ WRONG - Key from password without KDF
key = password.encode()[:32]

# ✅ CORRECT - Key derivation from password
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

salt = os.urandom(16)
kdf = Scrypt(salt=salt, length=32, n=2**17, r=8, p=1)
key = kdf.derive(password.encode())

# ✅ CORRECT - Key from secure storage
import keyring
key = keyring.get_password("myapp", "encryption_key")
```

### 1.4 Authenticated Encryption (CWE-347)

**Principle:** Always use authenticated encryption (AEAD). Never encrypt without MAC.

```python
# ❌ WRONG - Encryption without authentication
from Crypto.Cipher import AES
cipher = AES.new(key, AES.MODE_CBC, iv)
ciphertext = cipher.encrypt(plaintext)  # No integrity check!

# ✅ CORRECT - AEAD mode (GCM)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

aesgcm = AESGCM(key)
nonce = os.urandom(12)
# tag is automatically appended
ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)
```

### 1.5 Constant-Time Comparison (CWE-208)

**Principle:** Use constant-time comparison for secrets to prevent timing attacks.

```python
# ❌ WRONG - Vulnerable to timing attack
if user_token == stored_token:
    grant_access()

# ✅ CORRECT - Constant-time comparison
import hmac
if hmac.compare_digest(user_token, stored_token):
    grant_access()
```

### 1.6 Defense in Depth

**Principle:** Multiple layers - encryption at rest + in transit + access control.

---

## 2. Version Requirements

**ALWAYS use these minimum versions:**

```
# Python
cryptography>=42.0.0
argon2-cffi>=21.3.0
PyNaCl>=1.5.0

# Rust
ring>=0.17
chacha20poly1305>=0.10
argon2>=0.5
aes-gcm>=0.10

# Node.js
Use built-in crypto module (Node 16+)
```

---

## 3. Code Patterns

### 3.1 WHEN encrypting data at rest (Python)

```python
import os
import json
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

class EncryptedStorage:
    """Encrypt data at rest with AES-256-GCM."""

    NONCE_SIZE = 12
    KEY_SIZE = 32
    SALT_SIZE = 16

    def __init__(self, password: str, salt: bytes | None = None):
        self.salt = salt or os.urandom(self.SALT_SIZE)
        self.key = self._derive_key(password)
        self.cipher = AESGCM(self.key)

    def _derive_key(self, password: str) -> bytes:
        """Derive encryption key from password using Scrypt."""
        kdf = Scrypt(
            salt=self.salt,
            length=self.KEY_SIZE,
            n=2**17,  # CPU/memory cost
            r=8,
            p=1,
        )
        return kdf.derive(password.encode())

    def encrypt(self, plaintext: bytes) -> bytes:
        """Encrypt with random nonce. Returns: nonce + ciphertext + tag."""
        nonce = os.urandom(self.NONCE_SIZE)
        ciphertext = self.cipher.encrypt(nonce, plaintext, None)
        return nonce + ciphertext

    def decrypt(self, data: bytes) -> bytes:
        """Decrypt data encrypted by encrypt()."""
        nonce = data[:self.NONCE_SIZE]
        ciphertext = data[self.NONCE_SIZE:]
        return self.cipher.decrypt(nonce, ciphertext, None)

    def encrypt_json(self, obj: dict) -> str:
        """Encrypt JSON object to base64 string."""
        plaintext = json.dumps(obj).encode()
        encrypted = self.encrypt(plaintext)
        return base64.b64encode(encrypted).decode()

    def decrypt_json(self, data: str) -> dict:
        """Decrypt base64 string to JSON object."""
        encrypted = base64.b64decode(data)
        plaintext = self.decrypt(encrypted)
        return json.loads(plaintext)
```

### 3.2 WHEN encrypting data at rest (Rust)

```rust
use aes_gcm::{
    aead::{Aead, KeyInit, OsRng},
    Aes256Gcm, Nonce,
};
use argon2::Argon2;
use rand::RngCore;

const NONCE_SIZE: usize = 12;
const SALT_SIZE: usize = 16;
const KEY_SIZE: usize = 32;

pub struct EncryptedStorage {
    cipher: Aes256Gcm,
    salt: [u8; SALT_SIZE],
}

impl EncryptedStorage {
    pub fn new(password: &str, salt: Option<[u8; SALT_SIZE]>) -> Result<Self, Box<dyn std::error::Error>> {
        let salt = salt.unwrap_or_else(|| {
            let mut s = [0u8; SALT_SIZE];
            OsRng.fill_bytes(&mut s);
            s
        });

        let key = Self::derive_key(password, &salt)?;
        let cipher = Aes256Gcm::new_from_slice(&key)?;

        Ok(Self { cipher, salt })
    }

    fn derive_key(password: &str, salt: &[u8]) -> Result<[u8; KEY_SIZE], argon2::Error> {
        let mut key = [0u8; KEY_SIZE];
        Argon2::default().hash_password_into(
            password.as_bytes(),
            salt,
            &mut key,
        )?;
        Ok(key)
    }

    pub fn encrypt(&self, plaintext: &[u8]) -> Result<Vec<u8>, aes_gcm::Error> {
        let mut nonce_bytes = [0u8; NONCE_SIZE];
        OsRng.fill_bytes(&mut nonce_bytes);
        let nonce = Nonce::from_slice(&nonce_bytes);

        let ciphertext = self.cipher.encrypt(nonce, plaintext)?;

        // nonce + ciphertext
        let mut result = nonce_bytes.to_vec();
        result.extend(ciphertext);
        Ok(result)
    }

    pub fn decrypt(&self, data: &[u8]) -> Result<Vec<u8>, aes_gcm::Error> {
        let nonce = Nonce::from_slice(&data[..NONCE_SIZE]);
        let ciphertext = &data[NONCE_SIZE..];
        self.cipher.decrypt(nonce, ciphertext)
    }
}
```

### 3.3 WHEN hashing passwords

```python
from argon2 import PasswordHasher, Type
from argon2.exceptions import VerifyMismatchError

# Configure Argon2id with OWASP recommendations
ph = PasswordHasher(
    time_cost=3,        # Number of iterations
    memory_cost=65536,  # 64 MB
    parallelism=4,      # Number of threads
    hash_len=32,
    type=Type.ID,       # Argon2id (recommended)
)

def hash_password(password: str) -> str:
    """Hash password for storage."""
    return ph.hash(password)

def verify_password(hash: str, password: str) -> bool:
    """Verify password against hash. Returns False on mismatch."""
    try:
        ph.verify(hash, password)
        return True
    except VerifyMismatchError:
        return False

def needs_rehash(hash: str) -> bool:
    """Check if hash needs to be upgraded."""
    return ph.check_needs_rehash(hash)
```

### 3.4 WHEN generating secure tokens

```python
import secrets
import hashlib
import hmac

def generate_api_key() -> tuple[str, str]:
    """Generate API key and its hash for storage.

    Returns: (plaintext_key, hash_for_storage)
    """
    key = secrets.token_urlsafe(32)
    # Store only the hash
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    return key, key_hash

def verify_api_key(provided_key: str, stored_hash: str) -> bool:
    """Verify API key using constant-time comparison."""
    provided_hash = hashlib.sha256(provided_key.encode()).hexdigest()
    return hmac.compare_digest(provided_hash, stored_hash)

def generate_session_token() -> str:
    """Generate cryptographically secure session token."""
    return secrets.token_urlsafe(32)

def generate_csrf_token() -> str:
    """Generate CSRF token."""
    return secrets.token_hex(32)
```

### 3.5 WHEN implementing key rotation

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class EncryptedData:
    key_id: str  # Which key was used
    nonce: bytes
    ciphertext: bytes
    created_at: datetime

class KeyRotatingEncryption:
    """Encryption with key rotation support."""

    def __init__(self, keys: dict[str, bytes], current_key_id: str):
        self.keys = keys
        self.current_key_id = current_key_id
        self.ciphers = {
            kid: AESGCM(key) for kid, key in keys.items()
        }

    def encrypt(self, plaintext: bytes) -> EncryptedData:
        """Encrypt with current key."""
        nonce = os.urandom(12)
        cipher = self.ciphers[self.current_key_id]
        ciphertext = cipher.encrypt(nonce, plaintext, None)

        return EncryptedData(
            key_id=self.current_key_id,
            nonce=nonce,
            ciphertext=ciphertext,
            created_at=datetime.utcnow(),
        )

    def decrypt(self, data: EncryptedData) -> bytes:
        """Decrypt using the key that was used for encryption."""
        cipher = self.ciphers.get(data.key_id)
        if not cipher:
            raise ValueError(f"Unknown key: {data.key_id}")
        return cipher.decrypt(data.nonce, data.ciphertext, None)

    def needs_reencryption(self, data: EncryptedData) -> bool:
        """Check if data should be re-encrypted with current key."""
        return data.key_id != self.current_key_id
```

---

## 4. Anti-Patterns

**NEVER:**
- Use MD5, SHA1, or unsalted SHA256 for passwords
- Use ECB mode for any encryption
- Use DES, 3DES, RC4, or Blowfish
- Generate keys from weak random sources
- Hardcode encryption keys
- Encrypt without authentication (use AEAD)
- Compare secrets with == (use constant-time comparison)
- Implement your own cryptographic algorithms
- Reuse nonces/IVs with the same key

---

## 5. Testing

**ALWAYS write security tests:**

```python
import pytest
import os

def test_encryption_roundtrip():
    """Verify encrypt/decrypt returns original data."""
    storage = EncryptedStorage("test-password")
    plaintext = b"secret message"

    encrypted = storage.encrypt(plaintext)
    decrypted = storage.decrypt(encrypted)

    assert decrypted == plaintext

def test_different_ciphertext_each_time():
    """Verify random nonce produces different ciphertext."""
    storage = EncryptedStorage("test-password")
    plaintext = b"same message"

    ct1 = storage.encrypt(plaintext)
    ct2 = storage.encrypt(plaintext)

    assert ct1 != ct2  # Different nonces

def test_tampered_ciphertext_rejected():
    """Verify authentication detects tampering."""
    storage = EncryptedStorage("test-password")
    encrypted = storage.encrypt(b"secret")

    # Tamper with ciphertext
    tampered = bytearray(encrypted)
    tampered[-1] ^= 0xFF

    with pytest.raises(Exception):  # InvalidTag
        storage.decrypt(bytes(tampered))

def test_wrong_password_fails():
    """Verify wrong password cannot decrypt."""
    storage1 = EncryptedStorage("password1")
    storage2 = EncryptedStorage("password2")

    encrypted = storage1.encrypt(b"secret")

    with pytest.raises(Exception):
        storage2.decrypt(encrypted)

def test_password_hash_not_reversible():
    """Verify password hashes are one-way."""
    from argon2 import PasswordHasher
    ph = PasswordHasher()

    hash1 = ph.hash("password123")
    hash2 = ph.hash("password123")

    # Same password, different hashes (random salt)
    assert hash1 != hash2
    # Both verify correctly
    assert ph.verify(hash1, "password123")
    assert ph.verify(hash2, "password123")
```

---

## 6. Pre-Generation Checklist

**BEFORE generating any cryptographic code:**

- [ ] Using AES-256-GCM or ChaCha20-Poly1305 (authenticated encryption)
- [ ] Using Argon2id for password hashing
- [ ] Keys generated from os.urandom() or OsRng
- [ ] Nonces/IVs are random and never reused
- [ ] Keys derived from passwords use Scrypt or Argon2
- [ ] Secrets compared with constant-time functions
- [ ] No hardcoded keys or secrets
- [ ] Key rotation strategy implemented
- [ ] Using cryptography library (Python) or ring/aes-gcm (Rust)
- [ ] Minimum key sizes: AES-256, RSA-3072, Ed25519
