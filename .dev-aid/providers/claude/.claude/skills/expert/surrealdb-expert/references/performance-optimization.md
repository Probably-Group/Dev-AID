# SurrealDB Performance Optimization

## 1. Indexing Strategy

### When to Use Indexes

Indexes dramatically improve query performance but come with trade-offs:
- **Use**: On frequently queried fields (WHERE, ORDER BY)
- **Use**: On foreign keys and relationship fields
- **Use**: For unique constraints
- **Avoid**: On fields that change frequently
- **Avoid**: On low-cardinality fields (e.g., boolean)

### Pattern 1: Single Column Index

```surreal
-- ✅ Good: Index on frequently queried field
DEFINE INDEX email_idx ON TABLE user COLUMNS email UNIQUE;
DEFINE INDEX created_idx ON TABLE post COLUMNS created_at;

-- Query that benefits from index
SELECT * FROM user WHERE email = $email;  -- Fast lookup
SELECT * FROM post WHERE created_at > $date ORDER BY created_at DESC;  -- Fast scan
```

### Pattern 2: Composite Index

```surreal
-- ✅ Good: Composite index for multi-column queries
DEFINE INDEX user_status_idx ON TABLE order COLUMNS user_id, status;

-- Query that benefits from composite index
SELECT * FROM order WHERE user_id = $user AND status = 'pending';  -- Fast lookup
```

### Pattern 3: Full-Text Search Index

```surreal
-- ✅ Good: Full-text search index
DEFINE INDEX search_idx ON TABLE article
    COLUMNS title, content
    SEARCH ANALYZER simple BM25;

-- Query using search index
SELECT * FROM article WHERE title @@ 'database' OR content @@ 'performance';
```

### Pattern 4: Index Maintenance

```surreal
-- View existing indexes
INFO FOR TABLE user;

-- Remove unused index
REMOVE INDEX old_idx ON TABLE user;

-- Rebuild index (if needed)
REMOVE INDEX email_idx ON TABLE user;
DEFINE INDEX email_idx ON TABLE user COLUMNS email UNIQUE;
```

---

## 2. Query Optimization

### Pattern 1: Avoid N+1 Queries

**Problem**:
```surreal
-- ❌ Bad: N+1 query pattern
LET $users = SELECT * FROM user;
FOR $user IN $users {
    SELECT * FROM post WHERE author = $user.id;  -- N additional queries!
};
```

**Solution 1: Graph Traversal**:
```surreal
-- ✅ Good: Single query with graph traversal
SELECT
    *,
    ->authored->post.* AS posts
FROM user;
```

**Solution 2: FETCH**:
```surreal
-- ✅ Good: Use FETCH for eager loading
SELECT * FROM user FETCH ->authored->post;
```

### Pattern 2: Select Only Needed Fields

```surreal
-- ❌ Bad: Select all fields
SELECT * FROM user;  -- Returns password hash, metadata, etc.

-- ✅ Good: Select only needed fields
SELECT id, email, name FROM user WHERE active = true;
```

### Pattern 3: Efficient Pagination

```surreal
-- ✅ Good: Cursor-based pagination
SELECT * FROM post
    WHERE created_at < $cursor
    ORDER BY created_at DESC
    LIMIT 20;

-- ✅ Good: Offset-based pagination (small datasets)
SELECT * FROM post
    ORDER BY created_at DESC
    START 0 LIMIT 20;
```

### Pattern 4: Query Result Limiting

```surreal
-- ✅ Good: Always limit results
SELECT * FROM post ORDER BY created_at DESC LIMIT 100;

-- ✅ Good: Limit graph traversal results
SELECT ->follows->user[0:10].name FROM user:john;

-- ❌ Bad: Unlimited results
SELECT * FROM post;  -- Could return millions of rows!
```

---

## 3. Graph Traversal Performance

### Pattern 1: Limit Traversal Depth

```surreal
-- ✅ Good: Limit traversal depth
SELECT ->follows->user[0:10].name FROM user:john;  -- Max 10 results

-- ❌ Bad: Unlimited depth traversal
SELECT ->follows->user->follows->user->follows->user.* FROM user:john;
```

### Pattern 2: Filter During Traversal

```surreal
-- ✅ Good: Filter during traversal
SELECT ->authored->post[WHERE published = true AND created_at > $date].*
FROM user:john;

-- ❌ Bad: Filter after traversal
LET $posts = SELECT ->authored->post.* FROM user:john;
SELECT * FROM $posts WHERE published = true;
```

### Pattern 3: Aggregate During Traversal

```surreal
-- ✅ Good: Aggregate during traversal
SELECT
    count(->authored->post) AS post_count,
    count(<-follows<-user) AS follower_count
FROM user:john;

-- ❌ Bad: Multiple queries
SELECT count() FROM post WHERE author = user:john;
SELECT count() FROM follows WHERE out = user:john;
```

---

## 4. Connection Management

### Pattern 1: Connection Pooling

```python
# ✅ Good: Connection pool
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
```

**Bad Example**:
```python
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

---

## 5. Batch Operations

### Pattern 1: Batch Inserts

```surreal
-- ✅ Good: Batch insert with transaction
BEGIN TRANSACTION;
CREATE product:1 CONTENT { name: 'Product 1', price: 10 };
CREATE product:2 CONTENT { name: 'Product 2', price: 20 };
CREATE product:3 CONTENT { name: 'Product 3', price: 30 };
COMMIT TRANSACTION;

-- ❌ Bad: Individual inserts
FOR $item IN $items {
    CREATE product CONTENT $item;  -- N separate operations!
};
```

### Pattern 2: Bulk Updates

```surreal
-- ✅ Good: Bulk update with WHERE
UPDATE product SET discount = 0.1 WHERE category = 'electronics';

-- ✅ Good: Conditional bulk update
UPDATE product SET
    status = 'discounted',
    discount = 0.2,
    updated_at = time::now()
WHERE category = 'electronics' AND price > 100;

-- ❌ Bad: Loop updates
FOR $product IN (SELECT * FROM product WHERE category = 'electronics') {
    UPDATE $product.id SET discount = 0.1;
};
```

### Pattern 3: Bulk Deletes

```surreal
-- ✅ Good: Bulk delete with conditions
DELETE post WHERE created_at < time::now() - 1y AND archived = true;

-- ✅ Good: Delete with subquery
DELETE post WHERE author IN (SELECT id FROM user WHERE deleted = true);
```

---

## 6. Caching Strategies

### Pattern 1: Application-Level Caching

```python
from functools import lru_cache
import asyncio

class UserRepository:
    def __init__(self, db, cache_size=128):
        self.db = db
        self._cache = {}
        self._cache_size = cache_size

    async def get_user_by_id(self, user_id: str):
        """Get user with caching."""
        if user_id in self._cache:
            return self._cache[user_id]

        result = await self.db.query(
            "SELECT * FROM $user_id",
            {"user_id": user_id}
        )

        if result and result[0]["result"]:
            user = result[0]["result"][0]
            # Maintain cache size
            if len(self._cache) >= self._cache_size:
                self._cache.pop(next(iter(self._cache)))
            self._cache[user_id] = user
            return user

        return None

    def invalidate_cache(self, user_id: str):
        """Invalidate cached user."""
        self._cache.pop(user_id, None)
```

### Pattern 2: Query Result Caching

```python
import hashlib
import json
from datetime import datetime, timedelta

class QueryCache:
    def __init__(self, ttl_seconds=300):
        self.cache = {}
        self.ttl = timedelta(seconds=ttl_seconds)

    def _hash_query(self, query: str, params: dict) -> str:
        """Create cache key from query and params."""
        key = f"{query}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key.encode()).hexdigest()

    async def execute(self, db, query: str, params: dict = None):
        """Execute query with caching."""
        cache_key = self._hash_query(query, params or {})

        # Check cache
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < self.ttl:
                return cached_data

        # Execute query
        result = await db.query(query, params)

        # Cache result
        self.cache[cache_key] = (result, datetime.now())

        return result

    def invalidate(self, query: str, params: dict = None):
        """Invalidate specific cached query."""
        cache_key = self._hash_query(query, params or {})
        self.cache.pop(cache_key, None)

    def clear(self):
        """Clear all cache."""
        self.cache.clear()
```

---

## 7. Monitoring and Profiling

### Pattern 1: Query Timing

```python
import time
import logging

logger = logging.getLogger(__name__)

async def execute_with_timing(db, query: str, params: dict = None):
    """Execute query with performance logging."""
    start = time.time()
    try:
        result = await db.query(query, params)
        elapsed = time.time() - start

        if elapsed > 1.0:  # Log slow queries
            logger.warning(f"Slow query ({elapsed:.2f}s): {query[:100]}")
        else:
            logger.debug(f"Query executed ({elapsed:.3f}s): {query[:100]}")

        return result
    except Exception as e:
        elapsed = time.time() - start
        logger.error(f"Query failed ({elapsed:.2f}s): {query[:100]}, Error: {e}")
        raise
```

### Pattern 2: Performance Testing

```python
import pytest
import time

@pytest.mark.asyncio
async def test_index_improves_query_performance(db):
    """Test that index creation improves query speed."""
    # Create table and data without index
    await db.query("""
        DEFINE TABLE product SCHEMAFULL;
        DEFINE FIELD sku ON TABLE product TYPE string;
        DEFINE FIELD name ON TABLE product TYPE string;
    """)

    # Insert test data
    for i in range(1000):
        await db.query(
            "CREATE product CONTENT { sku: $sku, name: $name }",
            {"sku": f"SKU-{i:04d}", "name": f"Product {i}"}
        )

    # Query without index (measure baseline)
    start = time.time()
    await db.query("SELECT * FROM product WHERE sku = 'SKU-0500'")
    time_without_index = time.time() - start

    # Create index
    await db.query("DEFINE INDEX sku_idx ON TABLE product COLUMNS sku UNIQUE")

    # Query with index
    start = time.time()
    await db.query("SELECT * FROM product WHERE sku = 'SKU-0500'")
    time_with_index = time.time() - start

    # Index should improve performance
    assert time_with_index <= time_without_index
```

---

## 8. Performance Checklist

Before deploying to production:

### Indexing
- [ ] Indexes created on all frequently queried fields
- [ ] Composite indexes for multi-column queries
- [ ] Full-text search indexes for search features
- [ ] Unique indexes for uniqueness constraints
- [ ] No indexes on frequently updated fields

### Queries
- [ ] All queries use LIMIT clauses
- [ ] Graph traversals have depth limits
- [ ] No N+1 query patterns
- [ ] Only necessary fields selected
- [ ] Pagination implemented for large result sets

### Connections
- [ ] Connection pooling implemented
- [ ] Pool size tuned for workload
- [ ] Connections reused, not created per request
- [ ] Proper connection cleanup

### Caching
- [ ] Application-level caching for hot data
- [ ] Cache invalidation strategy implemented
- [ ] TTL configured appropriately
- [ ] Cache hit/miss ratio monitored

### Monitoring
- [ ] Slow query logging enabled
- [ ] Query performance metrics collected
- [ ] Connection pool metrics monitored
- [ ] Database resource usage tracked

---

## 9. Performance Benchmarks

### Expected Performance (Baseline)

With proper indexing and optimization:
- **Point queries** (by ID): < 1ms
- **Indexed lookups**: < 5ms
- **Graph traversals** (1-2 hops): < 10ms
- **Full-text search**: < 50ms
- **Aggregations** (with index): < 100ms

### Performance Testing Example

```python
@pytest.mark.asyncio
async def test_connection_pool_handles_concurrent_requests(db):
    """Connection pool should handle concurrent requests efficiently."""
    pool = SurrealDBPool("ws://localhost:8000/rpc", "test", "test_db", pool_size=10)
    await pool.initialize({"user": "root", "pass": "root"})

    async def query_task():
        async with pool.connection() as conn:
            await conn.query("SELECT * FROM product LIMIT 10")

    # Run 100 concurrent queries
    start = time.time()
    await asyncio.gather(*[query_task() for _ in range(100)])
    elapsed = time.time() - start

    # Should complete in reasonable time with pooling
    assert elapsed < 5.0  # 5 seconds for 100 queries

    await pool.close_all()
```
