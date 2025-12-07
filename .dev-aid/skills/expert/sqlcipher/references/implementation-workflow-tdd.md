## 5. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```python
# tests/test_encrypted_db.py
import pytest
from pathlib import Path

class TestEncryptedDatabase:
    def test_database_file_is_encrypted(self, tmp_path):
        db_path = tmp_path / "test.db"
        key = "x'0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef'"
        db = EncryptedDatabase(db_path, key)
        db.execute("CREATE TABLE secrets (data TEXT)")
        db.execute("INSERT INTO secrets VALUES ('super-secret-value')")
        db.close()
        raw_content = db_path.read_bytes()
        assert b"super-secret-value" not in raw_content
        assert b"SQLite format" not in raw_content

    def test_wrong_key_fails_to_open(self, tmp_path):
        db_path = tmp_path / "test.db"
        correct_key = "x'0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef'"
        wrong_key = "x'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'"
        db = EncryptedDatabase(db_path, correct_key)
        db.execute("CREATE TABLE test (id INTEGER)")
        db.close()
        with pytest.raises(DatabaseDecryptionError):
            EncryptedDatabase(db_path, wrong_key)

    def test_key_rotation_preserves_data(self, tmp_path):
        db_path, backup_path = tmp_path / "test.db", tmp_path / "backup.db"
        old_key = "x'0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef'"
        new_key = "x'fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210'"
        db = EncryptedDatabase(db_path, old_key)
        db.execute("CREATE TABLE data (value TEXT)")
        db.execute("INSERT INTO data VALUES ('preserved')")
        db.rotate_key(new_key, backup_path)
        db.close()
        with pytest.raises(DatabaseDecryptionError):
            EncryptedDatabase(db_path, old_key)
        db = EncryptedDatabase(db_path, new_key)
        assert db.query("SELECT value FROM data")[0][0] == "preserved"

    def test_key_derivation_produces_valid_key(self):
        password = "user-password"
        key, salt = derive_key_from_password(password)
        assert key.startswith("x'") and key.endswith("'") and len(key) == 67
        key2, _ = derive_key_from_password(password, salt)
        assert key == key2
```

### Step 2: Implement Minimum to Pass

```python
# src/encrypted_db.py
import sqlite3
from pathlib import Path

class DatabaseDecryptionError(Exception):
    pass

class EncryptedDatabase:
    def __init__(self, path: Path, key: str):
        self.path = path
        self.conn = sqlite3.connect(str(path))
        self.conn.execute(f"PRAGMA key = {key}")  # MUST be first
        self.conn.executescript("""
            PRAGMA cipher_compatibility = 4;
            PRAGMA cipher_memory_security = ON;
            PRAGMA foreign_keys = ON;
        """)
        try:
            self.conn.execute("SELECT count(*) FROM sqlite_master").fetchone()
        except sqlite3.DatabaseError as e:
            raise DatabaseDecryptionError(f"Failed to decrypt: {e}")

    def rotate_key(self, new_key: str, backup_path: Path) -> None:
        backup = sqlite3.connect(str(backup_path))
        self.conn.backup(backup)
        backup.close()
        self.conn.execute(f"PRAGMA rekey = {new_key}")
```

### Step 3: Refactor and Optimize

Apply performance patterns from Section 6 after tests pass.

### Step 4: Run Full Verification

```bash
# Run all tests with coverage
pytest tests/test_encrypted_db.py -v --cov=src --cov-report=term-missing

# Security-specific tests
pytest tests/test_encrypted_db.py -k "encrypted or key" -v

# Performance benchmarks
pytest tests/test_encrypted_db.py --benchmark-only
```

---

