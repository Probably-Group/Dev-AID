## 3. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```python
# tests/test_user_repository.py
import pytest
from surrealdb import Surreal

@pytest.fixture
async def db():
    """Set up test database connection."""
    client = Surreal("ws://localhost:8000/rpc")
    await client.connect()
    await client.use("test", "test_db")
    await client.signin({"user": "root", "pass": "root"})
    yield client
    await client.query("DELETE user;")
    await client.close()

@pytest.mark.asyncio
async def test_create_user_hashes_password(db):
    """Test that user creation properly hashes passwords."""
    result = await db.query(
        """
        CREATE user CONTENT {
            email: $email,
            password: crypto::argon2::generate($password)
        } RETURN id, email, password;
        """,
        {"email": "test@example.com", "password": "secret123"}
    )

    user = result[0]["result"][0]
    assert user["email"] == "test@example.com"
    assert user["password"] != "secret123"
    assert user["password"].startswith("$argon2")
```

### Step 2: Implement Minimum to Pass

```python
# src/repositories/user_repository.py
from surrealdb import Surreal
from typing import Optional

class UserRepository:
    def __init__(self, db: Surreal):
        self.db = db

    async def initialize_schema(self):
        """Create user table with security permissions."""
        await self.db.query("""
            DEFINE TABLE user SCHEMAFULL
                PERMISSIONS
                    FOR select, update, delete WHERE id = $auth.id
                    FOR create WHERE $auth.id != NONE;

            DEFINE FIELD email ON TABLE user TYPE string
                ASSERT string::is::email($value);
            DEFINE FIELD password ON TABLE user TYPE string
                VALUE crypto::argon2::generate($value);
            DEFINE FIELD created_at ON TABLE user TYPE datetime
                DEFAULT time::now();

            DEFINE INDEX email_idx ON TABLE user COLUMNS email UNIQUE;
        """)

    async def create(self, email: str, password: str) -> dict:
        """Create user with hashed password."""
        result = await self.db.query(
            """
            CREATE user CONTENT {
                email: $email,
                password: $password
            } RETURN id, email, created_at;
            """,
            {"email": email, "password": password}
        )
        return result[0]["result"][0]
```

### Step 3: Run Full Verification

```bash
# Run all SurrealDB tests
pytest tests/test_surrealdb/ -v --asyncio-mode=auto

# Run with coverage
pytest tests/test_surrealdb/ --cov=src/repositories --cov-report=term-missing
```

---


