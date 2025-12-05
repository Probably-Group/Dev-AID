# Graph Database Anti-Patterns

This document lists common mistakes and anti-patterns in graph database design and implementation, along with recommended solutions.

---

## Anti-Pattern 1: Unbounded Graph Traversals

### Problem
Traversing without depth limits can traverse the entire graph, causing performance issues and potential denial of service.

### Bad Example
```surreal
-- DON'T: No depth limit
SELECT ->follows->person.* FROM person:alice;
-- Could traverse entire social network!

-- DON'T: Infinite depth
SELECT ->follows[..]->person.* FROM person:alice;
-- Will never terminate on cycles!
```

### Good Example
```surreal
-- DO: Set depth limits
SELECT ->follows[..2]->person.* FROM person:alice;

-- DO: Limit results as well
SELECT ->follows[1..3]->person.* FROM person:alice LIMIT 100;

-- DO: Filter during traversal
SELECT ->follows[..2][WHERE active = true]->person.*
FROM person:alice
LIMIT 50;
```

### Why This Matters
- **Performance**: Unbounded traversals can take minutes or hours on large graphs
- **Resource Usage**: Can consume all available memory
- **Availability**: Can cause database crashes or timeouts
- **Cost**: Expensive queries waste compute resources

### Recommended Limits
- Maximum depth: 5-10 hops depending on graph size
- Maximum results: 1000 records per query
- Query timeout: 5-30 seconds

---

## Anti-Pattern 2: Missing Indexes on Traversal Paths

### Problem
Querying node or edge properties without indexes causes full table scans.

### Bad Example
```surreal
-- DON'T: Query without indexes (full table scan!)
SELECT * FROM person WHERE email = 'alice@example.com';

-- DON'T: Filter edges without index
SELECT ->follows[WHERE weight > 0.5]->person.* FROM person:alice;

-- DON'T: Complex filters without composite index
SELECT * FROM person
WHERE status = 'active' AND created_at > d'2024-01-01';
```

### Good Example
```surreal
-- DO: Create indexes first
DEFINE INDEX email_idx ON TABLE person COLUMNS email UNIQUE;
DEFINE INDEX name_idx ON TABLE person COLUMNS name;

-- Index edge properties used in filters
DEFINE INDEX follows_weight ON TABLE follows COLUMNS weight;
DEFINE INDEX works_at_role ON TABLE works_at COLUMNS role;

-- Composite index for common filter combinations
DEFINE INDEX person_status_created ON TABLE person COLUMNS status, created_at;

-- Then query with indexes
SELECT * FROM person WHERE email = 'alice@example.com';
SELECT ->follows[WHERE weight > 0.5]->person.* FROM person:alice;
```

### Impact
- **Query Speed**: 10-1000x slower without indexes
- **Database Load**: High CPU usage for full scans
- **Scalability**: Performance degrades linearly with data size

### Indexing Strategy
1. Index all properties used in WHERE clauses
2. Index foreign key fields (in, out on edges)
3. Create composite indexes for common filter combinations
4. Monitor slow queries and add indexes proactively

---

## Anti-Pattern 3: Wrong Relationship Direction

### Problem
Modeling edges in the wrong direction forces inefficient backward traversals.

### Bad Example
```surreal
-- Inefficient: Traversing against primary direction
-- If you commonly query "posts by author"
-- But model as: post->authored_by->person

-- Query requires backward traversal
SELECT <-authored_by<-post.* FROM person:alice;
```

### Good Example
```surreal
-- Better: Traverse with primary direction
-- Model as: person->authored->post

-- Efficient forward traversal
SELECT ->authored->post.* FROM person:alice;

-- Design rule: Model edges in the direction of common queries
```

### How to Choose Direction
1. **Identify most common query**: What will you query most often?
2. **Model in query direction**: Design edges to match common traversal
3. **Consider cardinality**: One-to-many should point from one to many
4. **Bidirectional when needed**: Create both directions for symmetric relationships

### Example: Social Network
```surreal
-- Good: person->follows->person
SELECT ->follows->person.* FROM person:alice;  -- Who Alice follows
SELECT <-follows<-person.* FROM person:alice;  -- Who follows Alice

-- Good: person->posted->post (one user, many posts)
SELECT ->posted->post.* FROM person:alice;

-- Good for symmetric: friendship
RELATE person:alice->friends->person:bob;
RELATE person:bob->friends->person:alice;
```

---

## Anti-Pattern 4: N+1 Query Pattern in Graphs

### Problem
Executing separate queries for each related entity instead of using graph traversal.

### Bad Example
```python
# DON'T: Multiple round trips
# First query
persons = await db.query("SELECT * FROM person")

# Then for each person (N queries)
for person in persons:
    companies = await db.query(
        f"SELECT * FROM company WHERE id = "
        f"(SELECT ->works_at->company FROM {person['id']})"
    )
```

```surreal
-- DON'T: Separate queries
SELECT * FROM person;
-- Then for each result:
SELECT * FROM company WHERE id = (SELECT ->works_at->company FROM person:1);
SELECT * FROM company WHERE id = (SELECT ->works_at->company FROM person:2);
-- ... N more queries
```

### Good Example
```surreal
-- DO: Single graph traversal
SELECT
    *,
    ->works_at->company.* AS companies
FROM person;

-- DO: Use FETCH to include related data
SELECT * FROM person FETCH ->works_at->company;

-- DO: Complex traversal in one query
SELECT
    name,
    ->works_at->company.name AS company_name,
    ->follows->person.name AS following,
    <-follows<-person.name AS followers
FROM person:alice;
```

```python
# DO: Single query with traversal
result = await db.query("""
    SELECT
        *,
        ->works_at->company.* AS companies,
        ->follows->person.{name, email} AS following
    FROM person
    LIMIT 100
""")
```

### Impact
- **Latency**: N+1 queries add network overhead
- **Database Load**: Many small queries instead of one efficient query
- **Performance**: 10-100x slower than single traversal

---

## Anti-Pattern 5: Over-Normalizing Relationship Data

### Problem
Creating separate tables/nodes for simple properties that should be embedded.

### Bad Example
```surreal
-- DON'T: Over-normalize simple properties
DEFINE TABLE person_email SCHEMAFULL;
DEFINE FIELD person ON TABLE person_email TYPE record<person>;
DEFINE FIELD email ON TABLE person_email TYPE string;

-- DON'T: Separate node for single attribute
CREATE email:alice SET value = 'alice@example.com';
RELATE person:alice->has_email->email:alice;

-- Query requires join/traversal for simple property
SELECT ->has_email->email.value FROM person:alice;
```

### Good Example
```surreal
-- DO: Embed simple properties
DEFINE TABLE person SCHEMAFULL;
DEFINE FIELD name ON TABLE person TYPE string;
DEFINE FIELD email ON TABLE person TYPE string;
DEFINE FIELD phone ON TABLE person TYPE string;

-- Direct access
SELECT email FROM person:alice;
```

### When to Use Relationships
Use relationships for:
- **Many-to-many associations**: Users ↔ Groups
- **Entities with independent lifecycle**: Person → Company
- **Rich metadata on relationships**: Employment with start_date, end_date, role
- **Separate data with own properties**: Person → Address (with street, city, zip)

Use embedded fields for:
- **Simple scalar values**: name, email, age
- **One-to-one attributes**: person.birth_date
- **Data that doesn't exist independently**: phone_number (not a separate entity)

---

## Anti-Pattern 6: Not Handling Cycles

### Problem
Circular references can cause infinite loops or incorrect results.

### Bad Example
```python
# DON'T: No cycle detection
async def traverse_all_followers(db, person_id, visited=None):
    if visited is None:
        visited = set()

    # Missing cycle check - infinite loop if A->B->C->A
    result = await db.query(
        "SELECT <-follows<-person.* FROM $person",
        {"person": person_id}
    )

    for follower in result[0]['result']:
        await traverse_all_followers(db, follower['id'], visited)
```

### Good Example
```surreal
-- DO: Set depth limit to prevent infinite loops
SELECT ->follows[..5]->person.* FROM person:alice;

-- DO: Use bounded traversal
SELECT ->follows[1..3]->person.* FROM person:alice;
```

```python
# DO: Track visited nodes
async def traverse_with_cycle_detection(
    db,
    person_id: str,
    visited: set | None = None,
    max_depth: int = 5,
    current_depth: int = 0
) -> list[dict]:
    """Traverse with cycle detection."""
    if visited is None:
        visited = set()

    # Depth limit
    if current_depth >= max_depth:
        return []

    # Cycle detection
    if person_id in visited:
        return []

    visited.add(person_id)

    result = await db.query(
        "SELECT <-follows<-person.* FROM $person LIMIT 100",
        {"person": person_id}
    )

    followers = result[0]['result']

    # Recursive traversal with tracking
    for follower in followers:
        await traverse_with_cycle_detection(
            db,
            follower['id'],
            visited,
            max_depth,
            current_depth + 1
        )

    return list(visited)
```

### Cycle Handling Strategies
1. **Depth limits**: Always set maximum traversal depth
2. **Visited tracking**: Maintain set of visited nodes
3. **Path detection**: Store path and check for repeats
4. **Timeout**: Set query timeout to prevent runaway queries

---

## Anti-Pattern 7: Ignoring Query Explain Plans

### Problem
Not analyzing query performance leads to inefficient queries in production.

### Bad Example
```python
# DON'T: Never check query performance
async def slow_query(db):
    # No idea if this is using indexes
    result = await db.query("""
        SELECT * FROM person
        WHERE email = 'alice@example.com'
    """)
    return result
```

### Good Example
```surreal
-- DO: Use EXPLAIN to analyze queries
-- (Database-specific syntax)

-- SurrealDB: Monitor query performance
-- Neo4j: EXPLAIN / PROFILE commands
EXPLAIN SELECT ->follows->person.* FROM person:alice;
PROFILE SELECT * FROM person WHERE email = 'alice@example.com';
```

```python
# DO: Performance monitoring
import logging
import time

logger = logging.getLogger(__name__)

async def query_with_monitoring(db, query: str, params: dict):
    """Execute query with performance monitoring."""
    start = time.time()

    result = await db.query(query, params)

    elapsed = time.time() - start

    # Log slow queries
    if elapsed > 0.1:  # 100ms threshold
        logger.warning(
            f"Slow query detected: {elapsed:.3f}s",
            extra={
                "query": query[:100],
                "params": params,
                "duration": elapsed
            }
        )

    return result
```

### Query Plan Analysis
Look for:
- **Full table scans**: Add indexes
- **Missing indexes**: Create appropriate indexes
- **Cartesian products**: Refactor query
- **Excessive traversal depth**: Add depth limits
- **Large intermediate results**: Add filters earlier

---

## Anti-Pattern 8: Storing Large Blobs in Graph Nodes

### Problem
Storing large binary data or documents in graph nodes causes performance issues.

### Bad Example
```surreal
-- DON'T: Store large data in nodes
CREATE person:alice SET
    name = 'Alice',
    profile_image = <binary data 5MB>,
    resume_pdf = <binary data 2MB>;

-- Traversals load all this data
SELECT ->follows->person.* FROM person:bob;
-- Loads all profile images and PDFs!
```

### Good Example
```surreal
-- DO: Store references to external storage
CREATE person:alice SET
    name = 'Alice',
    profile_image_url = 's3://bucket/alice-profile.jpg',
    resume_url = 's3://bucket/alice-resume.pdf';

-- DO: Separate table for large data
DEFINE TABLE document SCHEMAFULL;
DEFINE FIELD content ON TABLE document TYPE string;
DEFINE FIELD content_type ON TABLE document TYPE string;

RELATE person:alice->has_document->document:resume;

-- Fetch large data only when needed
SELECT ->has_document->document.* FROM person:alice;
```

### Best Practices for Large Data
1. **External storage**: Use S3, blob storage for files
2. **Store URLs**: Keep only references in graph
3. **Lazy loading**: Fetch large data on demand
4. **Separate tables**: Isolate large fields
5. **Pagination**: Never load all large objects at once

---

## Anti-Pattern 9: No Transaction Boundaries

### Problem
Not using transactions for multi-step operations leads to inconsistent state.

### Bad Example
```python
# DON'T: No transaction for related operations
async def transfer_relationship(db, from_id, to_id, person_id):
    # If this succeeds but next fails, inconsistent state
    await db.query(f"DELETE {from_id}->follows->{person_id}")

    # If this fails, relationship is lost
    await db.query(f"RELATE {to_id}->follows->{person_id}")
```

### Good Example
```surreal
-- DO: Use transactions
BEGIN TRANSACTION;

DELETE person:alice->follows->person:charlie;
RELATE person:bob->follows->person:charlie;

COMMIT TRANSACTION;
```

```python
# DO: Wrap in transaction
async def transfer_relationship_safe(db, from_id, to_id, person_id):
    """Transfer relationship with transaction."""
    try:
        await db.query("BEGIN TRANSACTION")

        await db.query(
            f"DELETE {from_id}->follows->{person_id}"
        )

        await db.query(
            f"RELATE {to_id}->follows->{person_id}"
        )

        await db.query("COMMIT TRANSACTION")

    except Exception as e:
        await db.query("ROLLBACK TRANSACTION")
        raise
```

### When to Use Transactions
- **Multi-step operations**: Multiple related changes
- **Data consistency**: Operations must succeed together
- **Relationship changes**: Creating/deleting related nodes
- **Atomic updates**: All-or-nothing requirements

---

## Anti-Pattern 10: Hardcoded Connection Strings

### Problem
Hardcoding credentials and configuration in code.

### Bad Example
```python
# DON'T: Hardcode credentials
async def connect():
    db = Surreal("ws://localhost:8000/rpc")
    await db.connect()
    await db.signin({
        "user": "root",
        "pass": "secretpassword123"  # Hardcoded!
    })
    return db
```

### Good Example
```python
# DO: Use environment variables
import os
from pydantic import BaseSettings, SecretStr

class Config(BaseSettings):
    db_url: str
    db_user: str
    db_password: SecretStr
    db_namespace: str
    db_database: str

    class Config:
        env_file = ".env"

async def connect_secure():
    config = Config()

    db = Surreal(config.db_url)
    await db.connect()
    await db.signin({
        "user": config.db_user,
        "pass": config.db_password.get_secret_value()
    })
    await db.use(config.db_namespace, config.db_database)

    return db
```

---

## Summary: Anti-Pattern Checklist

Before deploying graph database code, check for these anti-patterns:

- [ ] No unbounded traversals (all have depth limits)
- [ ] All frequently queried properties have indexes
- [ ] Relationship direction matches query patterns
- [ ] No N+1 query patterns (use graph traversals)
- [ ] Simple properties embedded, not over-normalized
- [ ] Cycle detection or depth limits in place
- [ ] Query plans analyzed for performance
- [ ] Large blobs stored externally, not in nodes
- [ ] Transactions used for multi-step operations
- [ ] No hardcoded credentials or configuration
