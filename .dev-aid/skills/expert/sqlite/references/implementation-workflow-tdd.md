## 8. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```python
# tests/test_user_repository.py
import pytest
import sqlite3

@pytest.fixture
def db():
    """In-memory SQLite for fast testing."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    yield conn
    conn.close()

class TestUserRepository:
    def test_create_user_returns_id(self, db):
        repo = UserRepository(db)
        repo.initialize_schema()
        user_id = repo.create_user("test@example.com", "Test User")
        assert user_id > 0

    def test_sql_injection_prevented(self, db):
        repo = UserRepository(db)
        repo.initialize_schema()
        malicious = "'; DROP TABLE users; --"
        user_id = repo.create_user(malicious, "Hacker")
        assert repo.get_by_id(user_id)["email"] == malicious
```

### Step 2: Implement Minimum Code to Pass

```python
# app/repositories/user.py
class UserRepository:
    def __init__(self, conn):
        self.conn = conn

    def initialize_schema(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL
            )""")
        self.conn.commit()

    def create_user(self, email: str, name: str) -> int:
        cursor = self.conn.execute(
            "INSERT INTO users (email, name) VALUES (?, ?)", (email, name))
        self.conn.commit()
        return cursor.lastrowid

    def get_by_id(self, user_id: int):
        return self.conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
```

### Step 3: Run Verification

```bash
pytest tests/test_*_repository.py -v --cov=app/repositories
```

---

