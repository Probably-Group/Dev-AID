## 8. Implementation Workflow (TDD)

### Step 1: Write Failing Tests First

```python
# tests/test_schema.py
import pytest
import sqlite3

@pytest.fixture
def db():
    conn = sqlite3.connect(':memory:')
    conn.execute("PRAGMA foreign_keys = ON")
    yield conn
    conn.close()

class TestUserSchema:
    def test_email_uniqueness(self, db):
        db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT UNIQUE NOT NULL)")
        db.execute("INSERT INTO users (email) VALUES ('test@example.com')")
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("INSERT INTO users (email) VALUES ('test@example.com')")

    def test_email_format_constraint(self, db):
        db.execute("""CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE NOT NULL CHECK(email LIKE '%_@__%.__%'))""")
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("INSERT INTO users (email) VALUES ('invalid')")

    def test_index_used_for_lookup(self, db):
        db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT)")
        db.execute("CREATE INDEX idx_users_email ON users(email)")
        plan = db.execute("EXPLAIN QUERY PLAN SELECT * FROM users WHERE email = ?", ('test@example.com',)).fetchone()
        assert 'USING INDEX' in plan[3]
```

### Step 2: Implement Schema to Pass Tests

```python
# src/database/schema.py
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL CHECK(email LIKE '%_@__%.__%'),
    name TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
"""

def init_schema(conn):
    """Initialize database schema."""
    conn.executescript(SCHEMA_SQL)
    conn.commit()
```

### Step 3: Run Tests and Verify

```bash
# Run schema tests
pytest tests/test_schema.py -v

# Run with coverage
pytest tests/test_schema.py --cov=src/database --cov-report=term-missing
```

### Step 4: Test Migrations

```python
# tests/test_migrations.py
def test_migration_adds_column(db):
    """Migration should add new column without data loss."""
    # Setup: create old schema with data
    db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT)")
    db.execute("INSERT INTO users (email) VALUES ('test@example.com')")

    # Run migration
    db.execute("ALTER TABLE users ADD COLUMN name TEXT DEFAULT 'Unknown'")

    # Verify: data preserved, new column exists
    row = db.execute("SELECT id, email, name FROM users").fetchone()
    assert row == (1, 'test@example.com', 'Unknown')
```

---

