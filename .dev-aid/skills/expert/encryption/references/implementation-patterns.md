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
        Decrypt and verify authenticity.

        Raises:
            InvalidTag: If authentication fails
        """
        if len(ciphertext) < self.NONCE_SIZE + 16:  # nonce + tag minimum
            raise ValueError("Ciphertext too short")

        nonce = ciphertext[:self.NONCE_SIZE]
        actual_ciphertext = ciphertext[self.NONCE_SIZE:]

        return self._aesgcm.decrypt(nonce, actual_ciphertext, associated_data)
```

### 6.3 SQLCipher Database Integration

```python
import sqlcipher3
from contextlib import contextmanager

class EncryptedDatabase:
    """Encrypted SQLite database using SQLCipher."""

    def __init__(self, db_path: str, key: bytes):
        self._db_path = db_path
        self._key = key
        self._conn = None

    @contextmanager
    def connect(self):
        """Context manager for database connections."""
        conn = sqlcipher3.connect(self._db_path)
        try:
            # Apply security pragmas
            conn.execute(f"PRAGMA key = \"x'{self._key.hex()}'\";")
            conn.execute("PRAGMA cipher = 'aes-256-gcm';")
            conn.execute("PRAGMA kdf_iter = 256000;")
            conn.execute("PRAGMA cipher_page_size = 4096;")

            # Verify encryption is active
            result = conn.execute("PRAGMA cipher_version;").fetchone()
            if not result:
                raise RuntimeError("SQLCipher encryption not active")

            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def rekey(self, new_key: bytes):
        """Rotate database encryption key."""
        with self.connect() as conn:
            conn.execute(f"PRAGMA rekey = \"x'{new_key.hex()}'\";")
        self._key = new_key
```

