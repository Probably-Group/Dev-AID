---
name: sqlite
version: 2.0.0
description: "SQLite patterns for desktop/Tauri apps with WAL mode, FTS5, and connection pooling."
risk_level: HIGH
---

# SQLite Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-89: SQL Injection**
- NEVER: `db.execute(f"SELECT * FROM users WHERE id = {id}")`
- ALWAYS: `db.execute("SELECT * FROM users WHERE id = ?", [id])`

**CWE-732: Database File Permissions**
- NEVER: World-readable SQLite files (0644 or worse)
- ALWAYS: `chmod 600 database.db`, restrict to application user

**CWE-311: Missing Encryption**
- NEVER: Store sensitive data in plain SQLite for sensitive apps
- ALWAYS: Use SQLCipher for encryption at rest if needed

**CWE-662: Improper Synchronization**
- NEVER: Multiple writers without WAL mode
- ALWAYS: Enable WAL mode, use proper connection pooling with serialized access

### 0.3 Risk Level: HIGH

**Verification requirements for HIGH risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 Data ≠ Code (CWE-89)

**Principle:** Never construct SQL from untrusted data via string operations.

```python
# ❌ WRONG - SQL injection
user_id = request.args.get('id')
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
cursor.execute("SELECT * FROM users WHERE id = " + user_id)

# ✅ CORRECT - Parameterized query (Python)
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# ✅ CORRECT - Named parameters
cursor.execute(
    "SELECT * FROM users WHERE name = :name AND age > :age",
    {"name": name, "age": age}
)
```

```rust
// ❌ WRONG - SQL injection (Rust)
let query = format!("SELECT * FROM users WHERE id = {}", user_id);
conn.execute(&query, [])?;

// ✅ CORRECT - Parameterized query (rusqlite)
conn.execute("SELECT * FROM users WHERE id = ?1", [&user_id])?;

// ✅ CORRECT - With sqlx
sqlx::query!("SELECT * FROM users WHERE id = $1", user_id)
    .fetch_one(&pool)
    .await?;
```

```typescript
// ❌ WRONG - SQL injection (better-sqlite3)
const user = db.prepare(`SELECT * FROM users WHERE id = ${userId}`).get();

// ✅ CORRECT - Parameterized query
const user = db.prepare('SELECT * FROM users WHERE id = ?').get(userId);

// ✅ CORRECT - Named parameters
const user = db.prepare('SELECT * FROM users WHERE id = @id').get({ id: userId });
```

### 1.2 Input Validation (CWE-20)

**Principle:** Validate all input. Use database constraints as second layer.

```sql
-- ❌ WRONG - No constraints
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT,
    age INTEGER
);

-- ✅ CORRECT - With constraints
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE CHECK(length(email) <= 255 AND email LIKE '%@%.%'),
    age INTEGER CHECK(age >= 0 AND age <= 150),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    CONSTRAINT email_format CHECK(email GLOB '*@*.*')
);
```

### 1.3 Secrets ≠ Code (CWE-798)

**Principle:** Never store unencrypted secrets. Use SQLCipher for sensitive data.

```python
# ❌ WRONG - Plaintext password storage
cursor.execute("INSERT INTO users (password) VALUES (?)", (password,))

# ✅ CORRECT - Hash passwords with Argon2
from argon2 import PasswordHasher
ph = PasswordHasher()
hash = ph.hash(password)
cursor.execute("INSERT INTO users (password_hash) VALUES (?)", (hash,))

# ✅ CORRECT - Use SQLCipher for sensitive databases
import sqlcipher3
conn = sqlcipher3.connect('encrypted.db')
conn.execute(f"PRAGMA key = '{key}'")  # Key from secure source
```

### 1.4 Fail Secure (CWE-636)

**Principle:** Use transactions. Rollback on any error.

```python
# ❌ WRONG - No transaction, partial updates possible
cursor.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
cursor.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 2")

# ✅ CORRECT - Transaction with rollback
try:
    conn.execute("BEGIN TRANSACTION")
    conn.execute("UPDATE accounts SET balance = balance - 100 WHERE id = ?", (from_id,))
    conn.execute("UPDATE accounts SET balance = balance + 100 WHERE id = ?", (to_id,))
    conn.commit()
except Exception:
    conn.rollback()
    raise
```

### 1.5 Least Privilege (CWE-250)

**Principle:** Read-only connections where possible. Minimal permissions.

### 1.6 Defense in Depth

**Principle:** Application validation + database constraints + encrypted storage.

---

## 2. Version Requirements

**ALWAYS use these minimum versions:**

```
# Python
sqlite3 (stdlib)
sqlcipher3>=0.5.0    # For encryption

# Rust
rusqlite>=0.31.0
sqlx>=0.7.0

# Node.js
better-sqlite3>=9.4.0
sql.js>=1.10.0

# Tauri
tauri-plugin-sql>=2.0.0
```

---

## 3. Code Patterns

### 3.1 WHEN creating database schema

```sql
-- Enable WAL mode for better concurrency
PRAGMA journal_mode = WAL;

-- Enable foreign keys (off by default!)
PRAGMA foreign_keys = ON;

-- Secure defaults
PRAGMA secure_delete = ON;
PRAGMA auto_vacuum = INCREMENTAL;

-- Example schema with proper constraints
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE CHECK(length(username) BETWEEN 3 AND 50),
    email TEXT NOT NULL UNIQUE CHECK(email LIKE '%@%.%'),
    password_hash TEXT NOT NULL CHECK(length(password_hash) >= 60),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Trigger for updated_at
CREATE TRIGGER IF NOT EXISTS users_updated_at
AFTER UPDATE ON users
BEGIN
    UPDATE users SET updated_at = datetime('now') WHERE id = NEW.id;
END;
```

### 3.2 WHEN implementing CRUD operations (Python)

```python
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: int
    username: str
    email: str

@contextmanager
def get_connection(db_path: str, readonly: bool = False):
    """Context manager for database connections."""
    uri = f"file:{db_path}{'?mode=ro' if readonly else ''}"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()

def get_user_by_id(db_path: str, user_id: int) -> Optional[User]:
    """Get user by ID with read-only connection."""
    with get_connection(db_path, readonly=True) as conn:
        row = conn.execute(
            "SELECT id, username, email FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        return User(**dict(row)) if row else None

def create_user(db_path: str, username: str, email: str, password_hash: str) -> int:
    """Create user with transaction."""
    with get_connection(db_path) as conn:
        try:
            cursor = conn.execute(
                """INSERT INTO users (username, email, password_hash)
                   VALUES (?, ?, ?)""",
                (username, email, password_hash)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            conn.rollback()
            if "UNIQUE constraint" in str(e):
                raise ValueError("Username or email already exists")
            raise
```

### 3.3 WHEN implementing CRUD operations (Rust/Tauri)

```rust
use rusqlite::{Connection, params, Result};
use serde::{Deserialize, Serialize};
use thiserror::Error;

#[derive(Debug, Serialize)]
pub struct User {
    pub id: i64,
    pub username: String,
    pub email: String,
}

#[derive(Error, Debug)]
pub enum DbError {
    #[error("Not found")]
    NotFound,
    #[error("Duplicate entry")]
    Duplicate,
    #[error("Database error")]
    Internal(#[from] rusqlite::Error),
}

pub fn init_db(conn: &Connection) -> Result<()> {
    conn.execute_batch(
        "PRAGMA journal_mode = WAL;
         PRAGMA foreign_keys = ON;
         PRAGMA secure_delete = ON;"
    )?;

    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )",
        [],
    )?;
    Ok(())
}

pub fn get_user(conn: &Connection, user_id: i64) -> Result<Option<User>, DbError> {
    let mut stmt = conn.prepare(
        "SELECT id, username, email FROM users WHERE id = ?1"
    )?;

    let user = stmt.query_row([user_id], |row| {
        Ok(User {
            id: row.get(0)?,
            username: row.get(1)?,
            email: row.get(2)?,
        })
    }).optional()?;

    Ok(user)
}

pub fn create_user(
    conn: &Connection,
    username: &str,
    email: &str,
    password_hash: &str,
) -> Result<i64, DbError> {
    match conn.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (?1, ?2, ?3)",
        params![username, email, password_hash],
    ) {
        Ok(_) => Ok(conn.last_insert_rowid()),
        Err(rusqlite::Error::SqliteFailure(e, _))
            if e.code == rusqlite::ErrorCode::ConstraintViolation => {
            Err(DbError::Duplicate)
        }
        Err(e) => Err(e.into()),
    }
}
```

### 3.4 WHEN implementing full-text search

```sql
-- Create FTS5 virtual table
CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(
    title,
    content,
    content=notes,
    content_rowid=id
);

-- Triggers to keep FTS in sync
CREATE TRIGGER notes_ai AFTER INSERT ON notes BEGIN
    INSERT INTO notes_fts(rowid, title, content) VALUES (NEW.id, NEW.title, NEW.content);
END;

CREATE TRIGGER notes_ad AFTER DELETE ON notes BEGIN
    INSERT INTO notes_fts(notes_fts, rowid, title, content) VALUES('delete', OLD.id, OLD.title, OLD.content);
END;

CREATE TRIGGER notes_au AFTER UPDATE ON notes BEGIN
    INSERT INTO notes_fts(notes_fts, rowid, title, content) VALUES('delete', OLD.id, OLD.title, OLD.content);
    INSERT INTO notes_fts(rowid, title, content) VALUES (NEW.id, NEW.title, NEW.content);
END;
```

```python
def search_notes(db_path: str, query: str, limit: int = 20) -> list[dict]:
    """Full-text search with highlighting."""
    # Sanitize query - remove FTS special characters
    safe_query = ''.join(c for c in query if c.isalnum() or c.isspace())

    with get_connection(db_path, readonly=True) as conn:
        rows = conn.execute(
            """SELECT n.id, n.title,
                      highlight(notes_fts, 1, '<mark>', '</mark>') as snippet,
                      rank
               FROM notes_fts
               JOIN notes n ON notes_fts.rowid = n.id
               WHERE notes_fts MATCH ?
               ORDER BY rank
               LIMIT ?""",
            (safe_query, limit)
        ).fetchall()
        return [dict(row) for row in rows]
```

---

## 4. Anti-Patterns

**NEVER:**
- Construct SQL from user input via string concatenation
- Store plaintext passwords
- Skip foreign key pragma (it's OFF by default!)
- Use database without WAL mode for concurrent access
- Expose raw SQLite errors to users
- Skip transactions for multi-statement operations

---

## 5. Testing

**ALWAYS write security tests:**

```python
import pytest
import sqlite3

def test_sql_injection_blocked():
    """Verify parameterized queries prevent injection."""
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER, name TEXT)")
    conn.execute("INSERT INTO users VALUES (1, 'alice')")

    # These should NOT return data due to parameterization
    attacks = [
        "1 OR 1=1",
        "1; DROP TABLE users; --",
        "1 UNION SELECT * FROM sqlite_master",
    ]

    for attack in attacks:
        result = conn.execute(
            "SELECT * FROM users WHERE id = ?",
            (attack,)
        ).fetchall()
        assert len(result) == 0, f"Injection not blocked: {attack}"

def test_constraints_enforced():
    """Verify database constraints work."""
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE users (
            email TEXT CHECK(email LIKE '%@%.%')
        )
    """)

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO users (email) VALUES ('invalid')")

def test_foreign_keys_enabled():
    """Verify foreign keys are enforced."""
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("CREATE TABLE parents (id INTEGER PRIMARY KEY)")
    conn.execute("""
        CREATE TABLE children (
            id INTEGER PRIMARY KEY,
            parent_id INTEGER REFERENCES parents(id)
        )
    """)

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO children (parent_id) VALUES (999)")
```

---

## 6. Pre-Generation Checklist

**BEFORE generating any SQLite code:**

- [ ] All queries use parameterized statements (?, ?1, :name)
- [ ] PRAGMA foreign_keys = ON explicitly set
- [ ] PRAGMA journal_mode = WAL for concurrent access
- [ ] Passwords hashed with Argon2, never plaintext
- [ ] Constraints defined at database level
- [ ] Transactions used for multi-statement operations
- [ ] FTS queries sanitized before execution
- [ ] Connection context managers for proper cleanup
- [ ] Read-only connections where writes not needed
- [ ] SQLite errors not exposed to end users
