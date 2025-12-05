# Advanced SurrealDB Patterns

## Pattern 1: Graph Relations with Typed Edges

### Use Case
When modeling complex relationships between entities with metadata on the relationships themselves.

### Implementation

```surreal
-- Define graph schema with typed relationships
DEFINE TABLE user SCHEMAFULL;
DEFINE TABLE post SCHEMAFULL;
DEFINE TABLE comment SCHEMAFULL;

-- Define relationship tables (edges)
DEFINE TABLE authored SCHEMAFULL
    PERMISSIONS FOR select WHERE in = $auth.id OR out.public = true;
DEFINE FIELD in ON TABLE authored TYPE record<user>;
DEFINE FIELD out ON TABLE authored TYPE record<post>;
DEFINE FIELD created_at ON TABLE authored TYPE datetime DEFAULT time::now();

DEFINE TABLE commented SCHEMAFULL;
DEFINE FIELD in ON TABLE commented TYPE record<user>;
DEFINE FIELD out ON TABLE commented TYPE record<comment>;

-- Create relationships
RELATE user:john->authored->post:123 SET created_at = time::now();
RELATE user:jane->commented->comment:456;

-- Graph traversal queries
-- Get all posts by a user
SELECT ->authored->post.* FROM user:john;

-- Get author of a post
SELECT <-authored<-user.* FROM post:123;

-- Multi-hop traversal: Get comments on user's posts
SELECT ->authored->post->commented->comment.* FROM user:john;

-- Bidirectional with filtering
SELECT ->authored->post[WHERE published = true].* FROM user:john;
```

### Pros
- Type-safe relationships
- Queryable edge metadata
- Bidirectional traversals
- Efficient graph operations

### Cons
- More complex schema definition
- Additional storage for edge tables
- Learning curve for graph syntax

---

## Pattern 2: Graph Traversal Optimization

### Use Case
Optimizing graph queries for large datasets with complex relationships.

### Implementation

```surreal
-- ✅ Good: Limit traversal depth
SELECT ->follows->user[0:10].name FROM user:john;  -- Max 10 results

-- ✅ Good: Filter during traversal
SELECT ->authored->post[WHERE published = true AND created_at > $date].*
FROM user:john;

-- ✅ Good: Use specific edge tables
SELECT ->authored->post.* FROM user:john;  -- Direct edge traversal

-- ✅ Good: Bidirectional with early filtering
SELECT
    <-follows<-user[WHERE active = true].name AS followers,
    ->follows->user[WHERE active = true].name AS following
FROM user:john;

-- ❌ Bad: Unlimited depth traversal
SELECT ->follows->user->follows->user->follows->user.* FROM user:john;

-- ❌ Bad: No filtering on large datasets
SELECT ->authored->post.* FROM user;  -- All posts from all users!

-- ✅ Good: Aggregate during traversal
SELECT
    count(->authored->post) AS post_count,
    count(<-follows<-user) AS follower_count
FROM user:john;
```

### Trade-offs

**Pros**:
- Prevents runaway queries
- Better performance on large graphs
- Controlled resource usage

**Cons**:
- Need to know appropriate limits
- May need pagination for large result sets

---

## Pattern 3: Batch Operations

### Use Case
Efficiently handling bulk operations to minimize round trips and improve performance.

### Implementation

```surreal
-- ✅ Good: Batch insert with single transaction
BEGIN TRANSACTION;
CREATE product:1 CONTENT { name: 'Product 1', price: 10 };
CREATE product:2 CONTENT { name: 'Product 2', price: 20 };
CREATE product:3 CONTENT { name: 'Product 3', price: 30 };
COMMIT TRANSACTION;

-- ✅ Good: Bulk update with WHERE
UPDATE product SET discount = 0.1 WHERE category = 'electronics';

-- ✅ Good: Bulk delete
DELETE post WHERE created_at < time::now() - 1y AND archived = true;

-- ❌ Bad: Individual operations in loop
FOR $item IN $items {
    CREATE product CONTENT $item;  -- N separate operations!
};
```

### Trade-offs

**Pros**:
- Reduced network overhead
- Atomic operations
- Better performance

**Cons**:
- All-or-nothing with transactions
- May need to handle partial failures

---

## Pattern 4: LIVE Queries for Real-Time Subscriptions

### Use Case
Building real-time applications that need instant updates when data changes.

### Implementation

```javascript
// ✅ CORRECT: Real-time subscription with cleanup
import Surreal from 'surrealdb.js';

const db = new Surreal();

async function setupRealTimeUpdates() {
    await db.connect('ws://localhost:8000/rpc');
    await db.use({ ns: 'app', db: 'production' });

    // Authenticate
    await db.signin({
        username: 'user',
        password: 'pass'
    });

    // Subscribe to live updates
    const queryUuid = await db.live(
        'user',
        (action, result) => {
            console.log(`Action: ${action}`);
            console.log('Data:', result);

            switch(action) {
                case 'CREATE':
                    handleNewUser(result);
                    break;
                case 'UPDATE':
                    handleUserUpdate(result);
                    break;
                case 'DELETE':
                    handleUserDelete(result);
                    break;
            }
        }
    );

    // ✅ IMPORTANT: Clean up on unmount/disconnect
    return () => {
        db.kill(queryUuid);
        db.close();
    };
}

// ✅ With permissions check
const liveQuery = `
    LIVE SELECT * FROM post
    WHERE author = $auth.id OR public = true;
`;

// ❌ UNSAFE: No cleanup, connection leaks
async function badExample() {
    const db = new Surreal();
    await db.connect('ws://localhost:8000/rpc');
    await db.live('user', callback); // Never cleaned up!
}
```

### Trade-offs

**Pros**:
- Real-time updates without polling
- Efficient WebSocket communication
- Filtered at database level

**Cons**:
- Requires connection management
- Memory leaks if not cleaned up
- WebSocket infrastructure needed

---

## Pattern 5: RBAC Implementation

### Use Case
Implementing role-based access control with different permission levels.

### Implementation

```surreal
-- ✅ System users with role-based access
DEFINE USER admin ON ROOT PASSWORD 'secure_password' ROLES OWNER;
DEFINE USER editor ON DATABASE app PASSWORD 'secure_password' ROLES EDITOR;
DEFINE USER viewer ON DATABASE app PASSWORD 'secure_password' ROLES VIEWER;

-- ✅ Record user authentication with scope
DEFINE SCOPE user_scope
    SESSION 2h
    SIGNUP (
        CREATE user CONTENT {
            email: $email,
            password: crypto::argon2::generate($password),
            created_at: time::now()
        }
    )
    SIGNIN (
        SELECT * FROM user WHERE email = $email
        AND crypto::argon2::compare(password, $password)
    );

-- Client authentication
const token = await db.signup({
    scope: 'user_scope',
    email: 'user@example.com',
    password: 'userpassword'
});

-- Or signin
const token = await db.signin({
    scope: 'user_scope',
    email: 'user@example.com',
    password: 'userpassword'
});

-- ✅ Use $auth in permissions
DEFINE TABLE document SCHEMAFULL
    PERMISSIONS
        FOR select WHERE public = true OR owner = $auth.id
        FOR create WHERE $auth.id != NONE
        FOR update, delete WHERE owner = $auth.id;

DEFINE FIELD owner ON TABLE document TYPE record<user> VALUE $auth.id;
DEFINE FIELD public ON TABLE document TYPE bool DEFAULT false;
```

### Trade-offs

**Pros**:
- Fine-grained access control
- Integrated authentication
- Session management built-in

**Cons**:
- Complex setup for multi-tenant apps
- Need to manage scope definitions

---

## Pattern 6: Strict Schema Validation

### Use Case
Ensuring data integrity with comprehensive validation rules.

### Implementation

```surreal
-- ✅ STRICT: Type-safe schema with validation
DEFINE TABLE product SCHEMAFULL
    PERMISSIONS FOR select WHERE published = true OR $auth.role = 'admin';

DEFINE FIELD name ON TABLE product
    TYPE string
    ASSERT string::length($value) >= 3 AND string::length($value) <= 100;

DEFINE FIELD price ON TABLE product
    TYPE decimal
    ASSERT $value > 0;

DEFINE FIELD category ON TABLE product
    TYPE string
    ASSERT $value IN ['electronics', 'clothing', 'food', 'books'];

DEFINE FIELD tags ON TABLE product
    TYPE array<string>
    DEFAULT [];

DEFINE FIELD inventory ON TABLE product
    TYPE object;

DEFINE FIELD inventory.quantity ON TABLE product
    TYPE int
    ASSERT $value >= 0;

DEFINE FIELD inventory.warehouse ON TABLE product
    TYPE string;

-- ✅ Validation on insert/update
CREATE product CONTENT {
    name: "Laptop",
    price: 999.99,
    category: "electronics",
    tags: ["computer", "portable"],
    inventory: {
        quantity: 50,
        warehouse: "west-1"
    }
};

-- ❌ This will FAIL assertion
CREATE product CONTENT {
    name: "AB", -- Too short
    price: -10, -- Negative price
    category: "invalid" -- Not in allowed list
};
```

### Trade-offs

**Pros**:
- Data integrity guaranteed
- Clear validation errors
- Self-documenting schema

**Cons**:
- More verbose definitions
- Schema migrations needed for changes
- Less flexibility

---

## Pattern 7: Connection Pooling

### Use Case
Managing database connections efficiently in high-throughput applications.

### Implementation

```python
# ✅ Good: Connection pool with proper management
import asyncio
from contextlib import asynccontextmanager
from surrealdb import Surreal

class SurrealDBPool:
    def __init__(self, url: str, ns: str, db: str, pool_size: int = 10):
        self.url = url
        self.ns = ns
        self.db = db
        self.pool_size = pool_size
        self._pool: asyncio.Queue = asyncio.Queue(maxsize=pool_size)
        self._semaphore = asyncio.Semaphore(pool_size)

    async def initialize(self, auth: dict):
        """Initialize pool with authenticated connections."""
        for _ in range(self.pool_size):
            conn = Surreal(self.url)
            await conn.connect()
            await conn.use(self.ns, self.db)
            await conn.signin(auth)
            await self._pool.put(conn)

    @asynccontextmanager
    async def connection(self):
        """Get connection from pool with automatic return."""
        async with self._semaphore:
            conn = await self._pool.get()
            try:
                yield conn
            except Exception as e:
                # Reconnect on error
                await conn.close()
                conn = Surreal(self.url)
                await conn.connect()
                raise e
            finally:
                await self._pool.put(conn)

    async def close_all(self):
        """Gracefully close all connections."""
        while not self._pool.empty():
            conn = await self._pool.get()
            await conn.close()

# Usage
pool = SurrealDBPool("ws://localhost:8000/rpc", "app", "production", pool_size=20)
await pool.initialize({"user": "admin", "pass": "secure"})

async with pool.connection() as db:
    result = await db.query("SELECT * FROM user WHERE id = $id", {"id": user_id})

# ❌ Bad: New connection per request
async def bad_query(user_id: str):
    db = Surreal("ws://localhost:8000/rpc")
    await db.connect()  # Expensive!
    await db.use("app", "production")
    await db.signin({"user": "admin", "pass": "secure"})
    result = await db.query("SELECT * FROM user WHERE id = $id", {"id": user_id})
    await db.close()
    return result
```

### Trade-offs

**Pros**:
- Reuse connections
- Better performance
- Controlled resource usage

**Cons**:
- More complex setup
- Need to manage pool lifecycle
- Connection state management
