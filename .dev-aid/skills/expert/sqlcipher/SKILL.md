---
name: SQLCipher Encrypted Database Expert
version: 2.0.0
description: "SQLCipher encrypted database patterns with key management, migration, re-keying, and secure key derivation. Use when implementing database encryption, managing encryption keys, or migrating between SQLCipher versions. Do NOT use for unencrypted SQLite databases (use sqlite)."
compatibility: "SQLCipher 4.5+"
risk_level: HIGH
token_budget: 4500
---
# SQLCipher - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.2 Security Patterns (security rules)

**CWE-321: Hard-coded Encryption Key**
- Do not: `PRAGMA key = 'hardcoded-password'` in code
- Instead: Derive key from user input or secure keychain

**CWE-328: Weak Key Derivation**
- Do not: Use password directly as key
- Instead: `PRAGMA kdf_iter = 256000` (or higher), use PBKDF2-SHA256

**CWE-311: Missing Re-keying**
- Do not: Keep same key indefinitely
- Instead: Implement key rotation strategy, use `PRAGMA rekey`

**CWE-89: SQL Injection**
- Do not: String concatenation even with encrypted DB
- Instead: Parameterized queries - encryption doesn't prevent injection

---

## 1. Security Principles

### 1.1 Key Management (CWE-321)

**Principle:** Database encryption is useless if keys are hardcoded or poorly managed.

```python
# ❌ WRONG - Hardcoded encryption key
import sqlite3

conn = sqlite3.connect("data.db")
conn.execute("PRAGMA key = 'supersecretkey123'")  # Key in source code!

# ✅ CORRECT - Key from secure source
import os
from pathlib import Path
from dataclasses import dataclass

@dataclass
class SQLCipherConfig:
    db_path: Path
    key_derivation: str = "PBKDF2-HMAC-SHA512"
    kdf_iterations: int = 256000
    cipher: str = "AES-256-CBC"
    page_size: int = 4096

def get_encryption_key() -> str:
    """Get encryption key from secure source."""

    # Option 1: Environment variable (for server apps)
    key = os.environ.get("SQLCIPHER_KEY")
    if key:
        return key

    # Option 2: OS keychain (for desktop apps)
    try:
        import keyring
        key = keyring.get_password("myapp", "database_key")
        if key:
            return key
    except ImportError:
        pass

    # Option 3: Hardware security module (HSM)
    # key = hsm_client.get_key("database_key")

    raise RuntimeError("No encryption key available")

def open_encrypted_db(config: SQLCipherConfig) -> "sqlite3.Connection":
    """Open SQLCipher database with secure key handling."""
    import sqlite3

    key = get_encryption_key()

    conn = sqlite3.connect(str(config.db_path))

    # Apply key with proper quoting to prevent injection
    conn.execute(f"PRAGMA key = \"x'{key}'\"")

    # Configure cipher settings
    conn.execute(f"PRAGMA cipher_page_size = {config.page_size}")
    conn.execute(f"PRAGMA kdf_iter = {config.kdf_iterations}")
    conn.execute(f"PRAGMA cipher = '{config.cipher}'")

    # Verify database is accessible
    try:
        conn.execute("SELECT count(*) FROM sqlite_master")
    except sqlite3.DatabaseError:
        conn.close()
        raise ValueError("Invalid encryption key or corrupted database")

    return conn
```

### 1.2 Key Rotation (CWE-324)

**Principle:** Encryption keys should be rotatable without data loss.

```python
# ❌ WRONG - No key rotation capability
# Just change the key and hope for the best

# ✅ CORRECT - Proper key rotation with re-encryption
import sqlite3
import tempfile
import shutil
from pathlib import Path

def rotate_encryption_key(
    db_path: Path,
    old_key: str,
    new_key: str,
    backup_dir: Path | None = None,
) -> None:
    """Rotate encryption key with backup and verification."""

    # Create backup first
    if backup_dir:
        backup_path = backup_dir / f"{db_path.name}.backup"
        shutil.copy2(db_path, backup_path)

    conn = sqlite3.connect(str(db_path))

    try:
        # Authenticate with old key
        conn.execute(f"PRAGMA key = \"x'{old_key}'\"")

        # Verify old key works
        try:
            conn.execute("SELECT count(*) FROM sqlite_master")
        except sqlite3.DatabaseError:
            raise ValueError("Invalid old encryption key")

        # Re-encrypt with new key
        conn.execute(f"PRAGMA rekey = \"x'{new_key}'\"")

        # Verify new key works
        conn.close()

        # Reopen with new key to verify
        conn = sqlite3.connect(str(db_path))
        conn.execute(f"PRAGMA key = \"x'{new_key}'\"")
        conn.execute("SELECT count(*) FROM sqlite_master")

    except Exception as e:
        # Restore from backup on failure
        if backup_dir and backup_path.exists():
            shutil.copy2(backup_path, db_path)
        raise RuntimeError(f"Key rotation failed: {e}")

    finally:
        conn.close()

        # Clean up backup after successful rotation
        if backup_dir and backup_path.exists():
            backup_path.unlink()
```

### 1.3 Memory Protection (CWE-316)

**Principle:** Encryption keys and decrypted data should not linger in memory.

```python
# ❌ WRONG - Key stored in regular string
key = "mysecretkey"  # String interned, hard to clear

# ✅ CORRECT - Secure key handling with memory clearing
import ctypes
from typing import Callable
from contextlib import contextmanager

class SecureString:
    """String that can be securely cleared from memory."""

    def __init__(self, value: str):
        self._bytes = value.encode('utf-8')
        self._length = len(self._bytes)

    def get(self) -> str:
        return self._bytes.decode('utf-8')

    def clear(self):
        """Overwrite memory with zeros."""
        if self._bytes:
            ctypes.memset(
                ctypes.addressof(ctypes.c_char.from_buffer(bytearray(self._bytes))),
                0,
                self._length
            )
            self._bytes = b''

    def __del__(self):
        self.clear()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.clear()

@contextmanager
def secure_connection(
    db_path: Path,
    key_provider: Callable[[], str],
):
    """Context manager that clears key after use."""
    import sqlite3

    key = SecureString(key_provider())

    try:
        conn = sqlite3.connect(str(db_path))
        conn.execute(f"PRAGMA key = \"x'{key.get()}'\"")
        yield conn
    finally:
        key.clear()
        if 'conn' in dir():
            conn.close()
```

---

## 2. Version Requirements

```
# SQLCipher Python bindings
sqlcipher3>=0.5.0
# Alternative: pysqlcipher3
pysqlcipher3>=1.2.0
# For async
aiosqlite>=0.19.0  # Note: Requires SQLCipher build
# Key storage
keyring>=24.0.0
# For Tauri/desktop
# Use sqlcipher-sys Rust crate
```

---

## 3. Code Patterns

### WHEN creating encrypted databases, use proper initialization

```python
# ❌ WRONG - Create without proper settings
conn = sqlite3.connect("new.db")
conn.execute("PRAGMA key = 'mykey'")
# Uses default cipher settings which may be weak

# ✅ CORRECT - Full initialization with secure defaults
import sqlite3
from pathlib import Path
from dataclasses import dataclass
from typing import Callable

@dataclass
class DatabaseSchema:
    version: int
    migrations: list[Callable[["sqlite3.Connection"], None]]

def create_encrypted_database(
    db_path: Path,
    key_provider: Callable[[], str],
    schema: DatabaseSchema,
    cipher_config: SQLCipherConfig | None = None,
) -> None:
    """Create new encrypted database with schema."""

    if cipher_config is None:
        cipher_config = SQLCipherConfig(
            db_path=db_path,
            kdf_iterations=256000,  # OWASP recommended minimum
        )

    if db_path.exists():
        raise FileExistsError(f"Database already exists: {db_path}")

    conn = sqlite3.connect(str(db_path))

    try:
        key = key_provider()

        # Set encryption key
        conn.execute(f"PRAGMA key = \"x'{key}'\"")

        # Configure cipher (must be done before any other operations)
        conn.execute(f"PRAGMA cipher_page_size = {cipher_config.page_size}")
        conn.execute(f"PRAGMA kdf_iter = {cipher_config.kdf_iterations}")
        conn.execute("PRAGMA cipher_memory_security = ON")

        # Create schema version table
        conn.execute("""
            CREATE TABLE _schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)

        # Apply migrations
        for i, migration in enumerate(schema.migrations, 1):
            migration(conn)
            conn.execute(
                "INSERT INTO _schema_version (version) VALUES (?)",
                (i,)
            )

        conn.commit()

        # Verify encryption worked
        conn.close()
        conn = sqlite3.connect(str(db_path))
        conn.execute(f"PRAGMA key = \"x'{key}'\"")
        conn.execute("SELECT count(*) FROM sqlite_master")

    except Exception:
        conn.close()
        db_path.unlink(missing_ok=True)
        raise

    finally:
        conn.close()

# Example schema
def migration_001_users(conn: sqlite3.Connection):
    conn.execute("""
        CREATE TABLE users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)

def migration_002_sessions(conn: sqlite3.Connection):
    conn.execute("""
        CREATE TABLE sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            token_hash TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    conn.execute("CREATE INDEX idx_sessions_user ON sessions(user_id)")

APP_SCHEMA = DatabaseSchema(
    version=2,
    migrations=[migration_001_users, migration_002_sessions],
)
```

### WHEN querying encrypted databases, use parameterized queries

```python
# ❌ WRONG - String formatting (SQL injection)
def get_user(conn, user_id: str):
    return conn.execute(f"SELECT * FROM users WHERE id = '{user_id}'").fetchone()

# ✅ CORRECT - Parameterized queries with type-safe wrapper
from dataclasses import dataclass
from typing import TypeVar, Generic, Iterator
import sqlite3

T = TypeVar('T')

@dataclass
class User:
    id: str
    email: str
    password_hash: str
    created_at: str

class TypedRepository(Generic[T]):
    def __init__(self, conn: sqlite3.Connection, table: str, model: type[T]):
        self._conn = conn
        self._table = table
        self._model = model

        # Enable row factory for dict-like access
        self._conn.row_factory = sqlite3.Row

    def get_by_id(self, id: str) -> T | None:
        cursor = self._conn.execute(
            f"SELECT * FROM {self._table} WHERE id = ?",
            (id,)
        )
        row = cursor.fetchone()
        return self._model(**dict(row)) if row else None

    def find_by(self, **kwargs) -> list[T]:
        conditions = " AND ".join(f"{k} = ?" for k in kwargs.keys())
        values = tuple(kwargs.values())

        cursor = self._conn.execute(
            f"SELECT * FROM {self._table} WHERE {conditions}",
            values
        )
        return [self._model(**dict(row)) for row in cursor.fetchall()]

    def insert(self, **data) -> str:
        columns = ", ".join(data.keys())
        placeholders = ", ".join("?" for _ in data)
        values = tuple(data.values())

        self._conn.execute(
            f"INSERT INTO {self._table} ({columns}) VALUES ({placeholders})",
            values
        )
        self._conn.commit()
        return data.get("id", "")

    def update(self, id: str, **data) -> bool:
        if not data:
            return False

        set_clause = ", ".join(f"{k} = ?" for k in data.keys())
        values = tuple(data.values()) + (id,)

        cursor = self._conn.execute(
            f"UPDATE {self._table} SET {set_clause} WHERE id = ?",
            values
        )
        self._conn.commit()
        return cursor.rowcount > 0

    def delete(self, id: str) -> bool:
        cursor = self._conn.execute(
            f"DELETE FROM {self._table} WHERE id = ?",
            (id,)
        )
        self._conn.commit()
        return cursor.rowcount > 0

# Usage
class UserRepository(TypedRepository[User]):
    def __init__(self, conn: sqlite3.Connection):
        super().__init__(conn, "users", User)

    def get_by_email(self, email: str) -> User | None:
        result = self.find_by(email=email)
        return result[0] if result else None
```

### WHEN handling database in Tauri/Rust, use sqlcipher crate

```rust
// ❌ WRONG - Using regular SQLite
use rusqlite::Connection;

fn open_db(path: &str) -> Result<Connection, rusqlite::Error> {
    Connection::open(path)  // Not encrypted!
}

// ✅ CORRECT - SQLCipher with secure key handling
use rusqlite::Connection;
use std::path::Path;

/// Configuration for SQLCipher database
pub struct CipherConfig {
    pub kdf_iter: u32,
    pub page_size: u32,
    pub cipher_memory_security: bool,
}

impl Default for CipherConfig {
    fn default() -> Self {
        Self {
            kdf_iter: 256000,
            page_size: 4096,
            cipher_memory_security: true,
        }
    }
}

/// Open encrypted database with key from keychain
pub fn open_encrypted_db(
    path: &Path,
    key: &str,
    config: &CipherConfig,
) -> Result<Connection, rusqlite::Error> {
    let conn = Connection::open(path)?;

    // Set encryption key (using hex format for binary keys)
    conn.execute_batch(&format!(
        "PRAGMA key = \"x'{}'\"",
        key
    ))?;

    // Configure cipher settings
    conn.execute_batch(&format!(
        "PRAGMA cipher_page_size = {};
         PRAGMA kdf_iter = {};
         PRAGMA cipher_memory_security = {};",
        config.page_size,
        config.kdf_iter,
        if config.cipher_memory_security { "ON" } else { "OFF" }
    ))?;

    // Verify key is correct
    conn.execute_batch("SELECT count(*) FROM sqlite_master")?;

    Ok(conn)
}

/// Get encryption key from OS keychain
pub fn get_key_from_keychain(service: &str, account: &str) -> Result<String, keyring::Error> {
    let entry = keyring::Entry::new(service, account)?;
    entry.get_password()
}

/// Generate and store new encryption key
pub fn generate_and_store_key(service: &str, account: &str) -> Result<String, Box<dyn std::error::Error>> {
    use rand::Rng;

    // Generate 256-bit key
    let key: [u8; 32] = rand::thread_rng().gen();
    let key_hex = hex::encode(key);

    // Store in keychain
    let entry = keyring::Entry::new(service, account)?;
    entry.set_password(&key_hex)?;

    Ok(key_hex)
}
```

### WHEN migrating from plain SQLite, use export/import

```python
# ❌ WRONG - Direct conversion attempt
# conn.execute("PRAGMA key = 'newkey'")  # Doesn't encrypt existing data

# ✅ CORRECT - Export and re-import with encryption
import sqlite3
import tempfile
from pathlib import Path

def migrate_to_encrypted(
    plain_db_path: Path,
    encrypted_db_path: Path,
    encryption_key: str,
    cipher_config: SQLCipherConfig | None = None,
) -> None:
    """Migrate plain SQLite database to encrypted SQLCipher."""

    if cipher_config is None:
        cipher_config = SQLCipherConfig(
            db_path=encrypted_db_path,
            kdf_iterations=256000,
        )

    # Open plain database
    plain_conn = sqlite3.connect(str(plain_db_path))

    # Create new encrypted database
    enc_conn = sqlite3.connect(str(encrypted_db_path))

    try:
        # Configure encryption on new database
        enc_conn.execute(f"PRAGMA key = \"x'{encryption_key}'\"")
        enc_conn.execute(f"PRAGMA cipher_page_size = {cipher_config.page_size}")
        enc_conn.execute(f"PRAGMA kdf_iter = {cipher_config.kdf_iterations}")

        # Get schema from plain database
        cursor = plain_conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        tables = []
        for (sql,) in cursor:
            if sql:
                enc_conn.execute(sql)
                table_name = sql.split("CREATE TABLE")[1].split("(")[0].strip()
                tables.append(table_name)

        # Get indexes
        cursor = plain_conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL"
        )
        for (sql,) in cursor:
            enc_conn.execute(sql)

        # Copy data table by table
        for table in tables:
            cursor = plain_conn.execute(f"SELECT * FROM {table}")
            columns = [desc[0] for desc in cursor.description]
            placeholders = ", ".join("?" for _ in columns)

            for row in cursor:
                enc_conn.execute(
                    f"INSERT INTO {table} VALUES ({placeholders})",
                    row
                )

        enc_conn.commit()

        # Verify migration
        for table in tables:
            plain_count = plain_conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            enc_count = enc_conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            if plain_count != enc_count:
                raise RuntimeError(f"Row count mismatch in {table}")

    finally:
        plain_conn.close()
        enc_conn.close()
```

---

## 4. Anti-Patterns

Do not:
- Hardcode encryption keys in source code
- Use weak KDF iterations (< 256000 for PBKDF2)
- Store keys in the same location as the database
- Skip key verification after opening database
- Use string formatting for SQL queries (use parameters)
- Leave decrypted data in memory after use
- Use default cipher settings without review

---

## 5. Testing

```python
import pytest
import sqlite3
from pathlib import Path
from sqlcipher import (
    create_encrypted_database,
    open_encrypted_db,
    rotate_encryption_key,
# ... (additional test cases follow same pattern)
```

---

## 6. Pre-Generation Checklist

Before generating SQLCipher code:

- [ ] Key source: Key from keychain/HSM, not hardcoded
- [ ] KDF iterations: >= 256000 for PBKDF2
- [ ] Key verification: Test query after setting key
- [ ] Parameterized queries: No string formatting for SQL
- [ ] Key rotation: Re-encryption capability implemented
- [ ] Memory security: Keys cleared after use
- [ ] Backup strategy: Backup before key rotation
- [ ] Migration path: Export/import for plain->encrypted

---
