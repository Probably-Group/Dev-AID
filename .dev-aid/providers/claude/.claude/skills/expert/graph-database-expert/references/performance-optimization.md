# Graph Database Performance Optimization

This document provides detailed performance patterns and optimization strategies for graph databases.

## Pattern 1: Indexing Strategy

**Good: Create indexes before queries need them**
```surreal
-- Index frequently queried properties
DEFINE INDEX person_email ON TABLE person COLUMNS email UNIQUE;
DEFINE INDEX person_name ON TABLE person COLUMNS name;

-- Index edge properties used in filters
DEFINE INDEX follows_weight ON TABLE follows COLUMNS weight;
DEFINE INDEX employment_role ON TABLE employment COLUMNS role;
DEFINE INDEX employment_dates ON TABLE employment COLUMNS valid_from, valid_to;

-- Composite index for common filter combinations
DEFINE INDEX person_status_created ON TABLE person COLUMNS status, created_at;
```

**Bad: Query without indexes**
```surreal
-- Full table scan on every query!
SELECT * FROM person WHERE email = 'alice@example.com';
SELECT ->follows[WHERE weight > 0.5]->person.* FROM person:alice;
```

---

## Pattern 2: Query Optimization

**Good: Bounded traversals with limits**
```surreal
-- Always set depth limits
SELECT ->follows[..3]->person.name FROM person:alice;

-- Use pagination for large results
SELECT ->follows->person.* FROM person:alice LIMIT 50 START 0;

-- Filter early to reduce traversal
SELECT ->follows[WHERE weight > 0.5][..2]->person.name
FROM person:alice
LIMIT 100;
```

**Bad: Unbounded queries**
```surreal
-- Can traverse entire graph!
SELECT ->follows->person.* FROM person:alice;

-- No limits on results
SELECT * FROM person WHERE status = 'active';
```

---

## Pattern 3: Caching Frequent Traversals

**Good: Cache expensive traversals**
```python
from functools import lru_cache
from datetime import datetime, timedelta

class GraphCache:
    def __init__(self, ttl_seconds: int = 300):
        self.cache = {}
        self.ttl = timedelta(seconds=ttl_seconds)

    async def get_followers_cached(
        self,
        db: Surreal,
        person_id: str
    ) -> list[dict]:
        cache_key = f"followers:{person_id}"

        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if datetime.now() - entry['time'] < self.ttl:
                return entry['data']

        # Execute query
        result = await db.query(
            "SELECT <-follows<-person.* FROM $person LIMIT 100",
            {"person": person_id}
        )

        # Cache result
        self.cache[cache_key] = {
            'data': result[0]['result'],
            'time': datetime.now()
        }

        return result[0]['result']

    def invalidate(self, person_id: str):
        """Invalidate cache when graph changes."""
        keys_to_remove = [
            k for k in self.cache
            if person_id in k
        ]
        for key in keys_to_remove:
            del self.cache[key]
```

**Bad: No caching for repeated queries**
```python
# Every call hits the database
async def get_followers(db, person_id):
    return await db.query(
        "SELECT <-follows<-person.* FROM $person",
        {"person": person_id}
    )
```

---

## Pattern 4: Batch Operations

**Good: Batch multiple operations**
```surreal
-- Batch create nodes
CREATE person CONTENT [
    { id: 'person:alice', name: 'Alice' },
    { id: 'person:bob', name: 'Bob' },
    { id: 'person:charlie', name: 'Charlie' }
];

-- Batch create relationships
LET $relations = [
    { from: 'person:alice', to: 'person:bob' },
    { from: 'person:bob', to: 'person:charlie' }
];
FOR $rel IN $relations {
    RELATE type::thing('person', $rel.from)->follows->type::thing('person', $rel.to);
};
```

```python
# Python batch operations
async def batch_create_relationships(
    db: Surreal,
    relationships: list[dict]
) -> None:
    """Create multiple relationships in one transaction."""
    queries = []
    for rel in relationships:
        queries.append(
            f"RELATE {rel['from']}->follows->{rel['to']};"
        )

    # Execute as single transaction
    await db.query("BEGIN TRANSACTION; " + " ".join(queries) + " COMMIT;")
```

**Bad: Individual operations**
```python
# N database round trips!
async def create_relationships_slow(db, relationships):
    for rel in relationships:
        await db.query(
            f"RELATE {rel['from']}->follows->{rel['to']};"
        )
```

---

## Pattern 5: Connection Pooling

**Good: Use connection pool**
```python
from contextlib import asynccontextmanager
import asyncio

class SurrealPool:
    def __init__(self, url: str, pool_size: int = 10):
        self.url = url
        self.pool_size = pool_size
        self._pool = asyncio.Queue(maxsize=pool_size)
        self._created = 0

    async def initialize(self):
        """Pre-create connections."""
        for _ in range(self.pool_size):
            conn = await self._create_connection()
            await self._pool.put(conn)

    async def _create_connection(self) -> Surreal:
        db = Surreal(self.url)
        await db.connect()
        await db.signin({"user": "root", "pass": "root"})
        await db.use("jarvis", "main")
        self._created += 1
        return db

    @asynccontextmanager
    async def acquire(self):
        """Get connection from pool."""
        conn = await self._pool.get()
        try:
            yield conn
        finally:
            await self._pool.put(conn)

    async def close(self):
        """Close all connections."""
        while not self._pool.empty():
            conn = await self._pool.get()
            await conn.close()

# Usage
pool = SurrealPool("ws://localhost:8000/rpc")
await pool.initialize()

async with pool.acquire() as db:
    result = await db.query("SELECT * FROM person LIMIT 10")
```

**Bad: Create connection per query**
```python
# Connection overhead on every query!
async def query_slow(query: str):
    db = Surreal("ws://localhost:8000/rpc")
    await db.connect()
    await db.signin({"user": "root", "pass": "root"})
    result = await db.query(query)
    await db.close()
    return result
```

---

## Performance Testing

### Benchmark Tests

```python
# tests/performance/test_graph_performance.py
import pytest
import time

@pytest.mark.slow
@pytest.mark.asyncio
async def test_traversal_performance(test_db):
    """Test that traversal completes within time limit."""
    # Setup large graph
    await test_db.query("""
        FOR $i IN 1..100 {
            CREATE person SET name = $i;
        };
        FOR $i IN 1..99 {
            RELATE type::thing('person', $i)->follows->type::thing('person', $i + 1);
        };
    """)

    start = time.time()

    # Run bounded traversal
    result = await test_db.query(
        "SELECT ->follows[..5]->person.* FROM person:1"
    )

    elapsed = time.time() - start

    # Should complete in under 100ms
    assert elapsed < 0.1, f"Traversal took {elapsed}s"

    # Should return limited results
    assert len(result[0]['result']) <= 5
```

---

## Performance Monitoring

### Key Metrics to Track

1. **Query Execution Time**
   - Monitor slow queries (> 100ms)
   - Track query patterns over time
   - Alert on performance degradation

2. **Traversal Depth**
   - Maximum depth reached
   - Average traversal depth
   - Deep traversals (> 5 hops)

3. **Result Set Size**
   - Average results per query
   - Large result sets (> 1000 records)
   - Memory usage for large traversals

4. **Index Usage**
   - Queries using indexes
   - Full table scans
   - Index hit rate

5. **Cache Performance**
   - Cache hit rate
   - Cache memory usage
   - Cache invalidation frequency

---

## Performance Optimization Checklist

Before deploying graph queries:
- [ ] All frequent queries have appropriate indexes
- [ ] All traversals have depth limits (max 5-10 hops)
- [ ] Large result sets use pagination
- [ ] Expensive queries are cached with TTL
- [ ] Batch operations used for bulk inserts
- [ ] Connection pooling configured
- [ ] Query performance tested under load
- [ ] Monitoring and alerts configured
- [ ] Query explain plans reviewed
- [ ] Memory limits set for large traversals
