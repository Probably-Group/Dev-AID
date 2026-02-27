---
name: surrealdb-expert
version: 2.0.0
description: "SurrealDB multi-model database with SurrealQL, graph queries, real-time subscriptions, and document storage. Use when designing SurrealDB schemas, writing SurrealQL, or building multi-model data layers. Do NOT use for traditional SQL databases (use database-design)."
compatibility: "SurrealDB 1.4+"
risk_level: MEDIUM
token_budget: 3000
---
# SurrealDB Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.2 Security Patterns (security rules)

**CWE-89: SurrealQL Injection (GHSA-ccj3-5p93-8p42)**
- Do not: Concatenate user input into SurrealQL with string interpolation
- Instead: Use `bind` method or `vars` argument for parameters

**CWE-200: LIVE Query Exposure (CVE-2025-11060)**
- Do not: Allow untrusted users LIVE query subscriptions without restrictions
- Instead: Fine-grained DEFINE TABLE/FIELD permissions, restrict by role

**CWE-674: Parser Stack Overflow**
- Do not: Accept deeply nested SurrealQL without depth limits
- Instead: Upgrade to 1.1.0+, implement query complexity limits

**CWE-284: Backup Import Injection**
- Do not: Import backups from untrusted sources
- Instead: Validate backup integrity, audit imported data

---

## 1. Security Principles

### 1.1 Permission System (CWE-284, CWE-639)

**Principle:** SurrealDB has a powerful RBAC system. Always define proper PERMISSIONS on tables.

```surql
-- ❌ WRONG - No permissions (full access by default)
DEFINE TABLE users SCHEMAFULL;

-- ✅ CORRECT - Explicit permissions
DEFINE TABLE users SCHEMAFULL
    PERMISSIONS
        FOR select WHERE id = $auth.id OR $auth.role = 'admin'
        FOR create WHERE $auth.role = 'admin'
        FOR update WHERE id = $auth.id OR $auth.role = 'admin'
        FOR delete WHERE $auth.role = 'admin';

-- Define field-level permissions
DEFINE FIELD email ON users
    PERMISSIONS
        FOR select WHERE id = $auth.id OR $auth.role = 'admin'
        FOR update WHERE id = $auth.id;
```

### 1.2 Input Validation with Schema (CWE-20)

**Principle:** Use SCHEMAFULL tables with ASSERT constraints. Never trust client data.

```surql
-- ❌ WRONG - Schemaless, no constraints
DEFINE TABLE posts SCHEMALESS;

-- ✅ CORRECT - Strict schema with assertions
DEFINE TABLE posts SCHEMAFULL;

DEFINE FIELD title ON posts TYPE string
    ASSERT string::len($value) >= 1 AND string::len($value) <= 200;

DEFINE FIELD content ON posts TYPE string
    ASSERT string::len($value) <= 50000;

DEFINE FIELD author ON posts TYPE record<users>
    ASSERT $value != NONE;

DEFINE FIELD status ON posts TYPE string
    ASSERT $value IN ['draft', 'published', 'archived'];

DEFINE FIELD created_at ON posts TYPE datetime
    VALUE time::now()
    READONLY;
```

### 1.3 Authentication Scopes (CWE-287)

**Principle:** Define authentication scopes with proper session duration and validation.

```surql
-- ❌ WRONG - Weak authentication
DEFINE SCOPE user SESSION 1y
    SIGNIN (SELECT * FROM users WHERE email = $email);

-- ✅ CORRECT - Proper password verification
DEFINE SCOPE user SESSION 24h
    SIGNUP {
        LET $hashed = crypto::argon2::generate($password);
        CREATE users SET
            email = $email,
            password = $hashed,
            created_at = time::now()
    }
    SIGNIN {
        SELECT * FROM users
        WHERE email = $email
            AND crypto::argon2::compare(password, $password)
    };

-- Use token-based auth for APIs
DEFINE TOKEN api_token ON SCOPE user TYPE HS512 VALUE $secret;
```

### 1.4 Parameterized Queries (CWE-89)

**Principle:** Always use parameters. Never interpolate user data into queries.

```python
# ❌ WRONG - String interpolation (SurrealQL injection)
async def get_user(db, user_id: str):
    result = await db.query(f"SELECT * FROM users WHERE id = '{user_id}'")
    return result

# ✅ CORRECT - Parameterized query
async def get_user(db, user_id: str) -> dict | None:
    result = await db.query(
        "SELECT * FROM users WHERE id = $user_id",
        {"user_id": user_id}
    )
    return result[0]["result"][0] if result[0]["result"] else None

# ✅ CORRECT - Using record ID directly
from surrealdb import RecordID

async def get_user_by_record(db, user_id: str) -> dict | None:
    # RecordID validates format automatically
    record_id = RecordID("users", user_id)
    result = await db.select(record_id)
    return result
```

---

## 2. Version Requirements

```
surrealdb>=1.0.0
pysurrealdb>=0.3.0
# Or official SDK
surrealdb[http]>=0.3.0
surrealdb[websocket]>=0.3.0
```

---

## 3. Code Patterns

### WHEN connecting to SurrealDB, use connection pooling and error handling

```python
# ❌ WRONG - No connection management
from surrealdb import Surreal

async def query_data():
    db = Surreal("ws://localhost:8000/rpc")
    await db.signin({"user": "root", "pass": "root"})
    return await db.query("SELECT * FROM users")

# ✅ CORRECT - Connection pool with context manager
from surrealdb import Surreal
from contextlib import asynccontextmanager
from dataclasses import dataclass
import os

@dataclass
class SurrealConfig:
    url: str
    namespace: str
    database: str
    username: str
    password: str

    @classmethod
    def from_env(cls) -> "SurrealConfig":
        return cls(
            url=os.environ["SURREAL_URL"],
            namespace=os.environ["SURREAL_NS"],
            database=os.environ["SURREAL_DB"],
            username=os.environ["SURREAL_USER"],
            password=os.environ["SURREAL_PASS"],
        )

class SurrealPool:
    def __init__(self, config: SurrealConfig, pool_size: int = 10):
        self._config = config
        self._pool: list[Surreal] = []
        self._pool_size = pool_size
        self._semaphore = asyncio.Semaphore(pool_size)

    async def _create_connection(self) -> Surreal:
        db = Surreal(self._config.url)
        await db.connect()
        await db.signin({
            "user": self._config.username,
            "pass": self._config.password,
        })
        await db.use(self._config.namespace, self._config.database)
        return db

    @asynccontextmanager
    async def acquire(self):
        async with self._semaphore:
            if self._pool:
                db = self._pool.pop()
            else:
                db = await self._create_connection()
            try:
                yield db
            finally:
                self._pool.append(db)
```

### WHEN using graph relationships, use proper RELATE with validation

```surql
-- ❌ WRONG - Manual foreign keys
CREATE follows SET
    follower = 'users:alice',
    following = 'users:bob';

-- ✅ CORRECT - Graph edge with RELATE
RELATE users:alice->follows->users:bob SET
    created_at = time::now();

-- Define the relation table with permissions
DEFINE TABLE follows SCHEMAFULL
    PERMISSIONS
        FOR select FULL
        FOR create WHERE in = $auth.id
        FOR delete WHERE in = $auth.id;

DEFINE FIELD in ON follows TYPE record<users>;
DEFINE FIELD out ON follows TYPE record<users>;
DEFINE FIELD created_at ON follows TYPE datetime VALUE time::now();

-- Query with graph traversal
SELECT id, name, ->follows->users AS following FROM users WHERE id = $auth.id;

-- Reverse traversal
SELECT id, name, <-follows<-users AS followers FROM users WHERE id = $auth.id;
```

### WHEN implementing live queries, handle connection lifecycle

```python
# ❌ WRONG - No cleanup of live queries
async def watch_posts(db):
    live_id = await db.live("posts")
    async for notification in db.live_notifications(live_id):
        print(notification)

# ✅ CORRECT - Proper lifecycle management
from dataclasses import dataclass
from typing import AsyncIterator, Callable
import asyncio

@dataclass
class LiveQueryHandle:
    db: Surreal
    query_id: str
    _cancelled: bool = False

    async def cancel(self):
        if not self._cancelled:
            await self.db.kill(self.query_id)
            self._cancelled = True

class LiveQueryManager:
    def __init__(self, pool: SurrealPool):
        self._pool = pool
        self._handles: list[LiveQueryHandle] = []

    async def subscribe(
        self,
        table: str,
        callback: Callable[[dict], None],
    ) -> LiveQueryHandle:
        """Subscribe to live updates with automatic cleanup."""
        async with self._pool.acquire() as db:
            query_id = await db.live(table)
            handle = LiveQueryHandle(db, query_id)
            self._handles.append(handle)

            async def process_notifications():
                try:
                    async for notification in db.live_notifications(query_id):
                        if handle._cancelled:
                            break
                        await callback(notification)
                except asyncio.CancelledError:
                    await handle.cancel()

            asyncio.create_task(process_notifications())
            return handle

    async def cleanup(self):
        """Cancel all live queries."""
        for handle in self._handles:
            await handle.cancel()
        self._handles.clear()
```

### WHEN using transactions, ensure atomicity

```python
# ❌ WRONG - Multiple queries without transaction
async def transfer_credits(db, from_user: str, to_user: str, amount: int):
    await db.query(
        "UPDATE users SET credits -= $amount WHERE id = $from_user",
        {"from_user": from_user, "amount": amount}
    )
    await db.query(
        "UPDATE users SET credits += $amount WHERE id = $to_user",
        {"to_user": to_user, "amount": amount}
    )

# ✅ CORRECT - Atomic transaction
async def transfer_credits(
    db,
    from_user: str,
    to_user: str,
    amount: int,
) -> bool:
    """Transfer credits atomically with validation."""
    result = await db.query("""
        BEGIN TRANSACTION;

        -- Check sufficient balance
        LET $sender = (SELECT credits FROM users WHERE id = $from_user);
        IF $sender.credits < $amount THEN
            THROW "Insufficient credits";
        END;

        -- Perform transfer
        UPDATE users SET credits -= $amount WHERE id = $from_user;
        UPDATE users SET credits += $amount WHERE id = $to_user;

        -- Log transaction
        CREATE transactions SET
            from = $from_user,
            to = $to_user,
            amount = $amount,
            created_at = time::now();

        COMMIT TRANSACTION;
    """, {
        "from_user": from_user,
        "to_user": to_user,
        "amount": amount,
    })

    return not any(r.get("status") == "ERR" for r in result)
```

---

## 4. Anti-Patterns

Do not:
- Use SCHEMALESS tables in production (use SCHEMAFULL)
- Skip PERMISSIONS on tables
- Interpolate user data into SurrealQL queries
- Use root credentials in application code
- Create sessions without expiration (SESSION 1y)
- Store passwords without crypto::argon2
- Ignore live query cleanup (memory leaks)

---

## 5. Testing

```python
import pytest
from surrealdb import Surreal

@pytest.fixture
async def db():
    """Test database with isolated namespace."""
    db = Surreal("ws://localhost:8000/rpc")
# ... (additional test cases follow same pattern)
```

---

## 6. Pre-Generation Checklist

Before generating SurrealDB code:

- [ ] Tables use SCHEMAFULL with ASSERT constraints
- [ ] PERMISSIONS defined on all tables
- [ ] Authentication scopes have reasonable SESSION duration
- [ ] Passwords hashed with crypto::argon2
- [ ] All queries use parameters (not string interpolation)
- [ ] Graph relations use RELATE (not manual foreign keys)
- [ ] Live queries have cleanup handlers
- [ ] Transactions used for multi-step operations
- [ ] No root credentials in application code

---
