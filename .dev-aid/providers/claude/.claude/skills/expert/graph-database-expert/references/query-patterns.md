# Graph Database Query Patterns

This document provides common graph database query patterns with examples in SurrealDB and comparisons to other graph databases.

---

## Pattern 1: Entity Nodes with Typed Relationships (SurrealDB)

### Concept
Model entities as nodes and relationships as edges with properties. Direction matters for query efficiency.

### Implementation

```surreal
-- Define entity tables
DEFINE TABLE person SCHEMAFULL;
DEFINE FIELD name ON TABLE person TYPE string;
DEFINE FIELD email ON TABLE person TYPE string;
DEFINE FIELD created_at ON TABLE person TYPE datetime DEFAULT time::now();

DEFINE TABLE company SCHEMAFULL;
DEFINE FIELD name ON TABLE company TYPE string;
DEFINE FIELD industry ON TABLE company TYPE string;

-- Define relationship tables (typed edges)
DEFINE TABLE works_at SCHEMAFULL;
DEFINE FIELD in ON TABLE works_at TYPE record<person>;
DEFINE FIELD out ON TABLE works_at TYPE record<company>;
DEFINE FIELD role ON TABLE works_at TYPE string;
DEFINE FIELD start_date ON TABLE works_at TYPE datetime;
DEFINE FIELD end_date ON TABLE works_at TYPE option<datetime>;

-- Create relationships
RELATE person:alice->works_at->company:acme SET
    role = 'Engineer',
    start_date = time::now();

-- Forward traversal: Who works at this company?
SELECT <-works_at<-person.* FROM company:acme;

-- Backward traversal: Where does this person work?
SELECT ->works_at->company.* FROM person:alice;

-- Filter on edge properties
SELECT ->works_at[WHERE role = 'Engineer']->company.*
FROM person:alice;
```

### Use Cases
- Employee-company relationships
- User-group memberships
- Product-category associations
- Any bidirectional relationship with metadata

---

## Pattern 2: Multi-Hop Graph Traversal

### Concept
Graph traversals follow edges to discover connected nodes. Always set depth limits to prevent performance issues.

### Implementation

```surreal
-- Schema: person -> follows -> person -> likes -> post
DEFINE TABLE follows SCHEMAFULL;
DEFINE FIELD in ON TABLE follows TYPE record<person>;
DEFINE FIELD out ON TABLE follows TYPE record<person>;

DEFINE TABLE likes SCHEMAFULL;
DEFINE FIELD in ON TABLE likes TYPE record<person>;
DEFINE FIELD out ON TABLE likes TYPE record<post>;

-- Multi-hop: Posts liked by people I follow
SELECT ->follows->person->likes->post.* FROM person:alice;

-- Depth limit to prevent runaway queries
SELECT ->follows[..3]->person.name FROM person:alice;

-- Variable depth traversal
SELECT ->follows[1..2]->person.* FROM person:alice;

-- DON'T: Unbounded traversal (dangerous!)
-- SELECT ->follows->person.* FROM person:alice; -- Could traverse entire graph!
```

### Neo4j Equivalent

```cypher
// Multi-hop in Cypher
MATCH (alice:Person {id: 'alice'})-[:FOLLOWS*1..2]->(person:Person)
RETURN person

// Posts liked by people I follow
MATCH (alice:Person {id: 'alice'})-[:FOLLOWS]->(:Person)-[:LIKES]->(post:Post)
RETURN post
```

### Use Cases
- Social network friend-of-friend queries
- Product recommendation chains
- Organizational hierarchy traversals
- Network path analysis

### Best Practices
- **Always set depth limits**: `[..3]` or `[1..5]`
- **Add result limits**: `LIMIT 100`
- **Filter early**: Apply WHERE clauses before traversing
- **Monitor performance**: Track execution time for deep traversals

---

## Pattern 3: Bidirectional Relationships

### Concept
Symmetric relationships need careful design. Either create bidirectional edges or query in both directions.

### Implementation

```surreal
-- Model friendship (symmetric relationship)
DEFINE TABLE friendship SCHEMAFULL;
DEFINE FIELD in ON TABLE friendship TYPE record<person>;
DEFINE FIELD out ON TABLE friendship TYPE record<person>;
DEFINE FIELD created_at ON TABLE friendship TYPE datetime DEFAULT time::now();

-- Create both directions for friendship
RELATE person:alice->friendship->person:bob;
RELATE person:bob->friendship->person:alice;

-- Query friends in either direction
SELECT ->friendship->person.* FROM person:alice;
SELECT <-friendship<-person.* FROM person:alice;

-- Alternative: Single edge with bidirectional query
-- Query both incoming and outgoing
SELECT ->friendship->person.*, <-friendship<-person.*
FROM person:alice;
```

### Design Choices

**Option 1: Duplicate Edges**
- **Pros**: Faster queries (no reverse traversal)
- **Cons**: More storage, must maintain both edges
- **Use when**: Query performance is critical

**Option 2: Single Edge + Bidirectional Queries**
- **Pros**: Less storage, easier maintenance
- **Cons**: Slightly slower queries
- **Use when**: Storage is limited, updates are frequent

**Option 3: Undirected Graph Flag**
- **Pros**: Database handles directionality
- **Cons**: Database-specific feature
- **Use when**: Supported by your database

### Use Cases
- Friendships (social networks)
- Partnerships (business relationships)
- Connections (professional networks)
- Mutual follows/subscriptions

---

## Pattern 4: Hierarchical Data (Trees and DAGs)

### Concept
Trees and hierarchies are special graph patterns. Consider materialized paths or nested sets for complex queries.

### Implementation

```surreal
-- Organization hierarchy
DEFINE TABLE org_unit SCHEMAFULL;
DEFINE FIELD name ON TABLE org_unit TYPE string;
DEFINE FIELD level ON TABLE org_unit TYPE string;
DEFINE FIELD path ON TABLE org_unit TYPE string;  -- Materialized path

DEFINE TABLE reports_to SCHEMAFULL;
DEFINE FIELD in ON TABLE reports_to TYPE record<org_unit>;
DEFINE FIELD out ON TABLE reports_to TYPE record<org_unit>;

-- Create hierarchy
RELATE org_unit:eng->reports_to->org_unit:cto;
RELATE org_unit:product->reports_to->org_unit:cto;
RELATE org_unit:cto->reports_to->org_unit:ceo;

-- Get all ancestors (upward traversal)
SELECT ->reports_to[..10]->org_unit.* FROM org_unit:eng;

-- Get all descendants (downward traversal)
SELECT <-reports_to[..10]<-org_unit.* FROM org_unit:ceo;

-- Using materialized path for faster ancestor queries
-- Store as: '/ceo/cto/eng' for fast LIKE queries
UPDATE org_unit:eng SET
    path = '/ceo/cto/eng',
    level = 3;

-- Fast ancestor lookup
SELECT * FROM org_unit WHERE '/ceo/cto/eng' LIKE string::concat(path, '%');

-- Fast depth queries
SELECT * FROM org_unit WHERE level = 3;
```

### Optimization Techniques

**1. Materialized Path**
- Store full path as string: `/root/parent/child`
- Fast ancestor queries with LIKE
- Easy to calculate depth

**2. Level/Depth Field**
- Store numeric depth in hierarchy
- Fast queries by level
- Useful for limiting traversal depth

**3. Closure Table**
- Pre-compute all ancestor-descendant pairs
- Extremely fast queries
- High storage overhead

### Use Cases
- Organizational charts
- Category taxonomies
- File system structures
- Comment threads
- Bill of materials

---

## Pattern 5: Temporal Relationships (Time-Based Edges)

### Concept
Add timestamps to edges for temporal queries. Essential for audit trails, historical analysis, and versioning.

### Implementation

```surreal
-- Track relationship validity periods
DEFINE TABLE employment SCHEMAFULL;
DEFINE FIELD in ON TABLE employment TYPE record<person>;
DEFINE FIELD out ON TABLE employment TYPE record<company>;
DEFINE FIELD role ON TABLE employment TYPE string;
DEFINE FIELD valid_from ON TABLE employment TYPE datetime;
DEFINE FIELD valid_to ON TABLE employment TYPE option<datetime>;

-- Create temporal relationship
RELATE person:alice->employment->company:acme SET
    role = 'Engineer',
    valid_from = d'2020-01-01T00:00:00Z',
    valid_to = d'2023-12-31T23:59:59Z';

-- Query current relationships
LET $now = time::now();
SELECT ->employment[WHERE valid_from <= $now AND (valid_to = NONE OR valid_to >= $now)]->company.*
FROM person:alice;

-- Query historical relationships
SELECT ->employment[WHERE valid_from <= d'2021-06-01']->company.*
FROM person:alice;

-- Query all relationships with time range
SELECT
    ->employment.role,
    ->employment.valid_from,
    ->employment.valid_to,
    ->employment->company.name AS company
FROM person:alice
ORDER BY ->employment.valid_from DESC;

-- Index temporal fields for performance
DEFINE INDEX employment_valid_from ON TABLE employment COLUMNS valid_from;
DEFINE INDEX employment_valid_to ON TABLE employment COLUMNS valid_to;
```

### Temporal Query Patterns

**Point-in-time query**: What was true at specific date?
```surreal
LET $date = d'2022-06-15';
SELECT ->employment[WHERE valid_from <= $date AND (valid_to = NONE OR valid_to >= $date)]->company.*
FROM person:alice;
```

**Range query**: What changed during period?
```surreal
SELECT ->employment[WHERE
    valid_from <= d'2022-12-31' AND
    valid_from >= d'2022-01-01'
]->company.*
FROM person:alice;
```

**Current state**: What is true now?
```surreal
SELECT ->employment[WHERE valid_to = NONE OR valid_to >= time::now()]->company.*
FROM person:alice;
```

### Use Cases
- Employment history
- Membership periods
- Product pricing over time
- Access control with expiration
- Audit trails
- Version control

---

## Pattern 6: Weighted Relationships (Graph Algorithms)

### Concept
Edge properties enable graph algorithms. Weight is fundamental for pathfinding, recommendations, and network analysis.

### Implementation

```surreal
-- Social network with relationship strength
DEFINE TABLE connected_to SCHEMAFULL;
DEFINE FIELD in ON TABLE connected_to TYPE record<person>;
DEFINE FIELD out ON TABLE connected_to TYPE record<person>;
DEFINE FIELD weight ON TABLE connected_to TYPE float;
DEFINE FIELD interaction_count ON TABLE connected_to TYPE int DEFAULT 0;

-- Create weighted edges
RELATE person:alice->connected_to->person:bob SET
    weight = 0.8,
    interaction_count = 45;

RELATE person:alice->connected_to->person:charlie SET
    weight = 0.3,
    interaction_count = 5;

-- Filter by weight threshold
SELECT ->connected_to[WHERE weight > 0.5]->person.* FROM person:alice;

-- Sort by relationship strength
SELECT
    ->connected_to->person.*,
    ->connected_to.weight AS strength
FROM person:alice
ORDER BY strength DESC
LIMIT 10;

-- Aggregate relationship metrics
SELECT
    count() AS connection_count,
    math::mean(->connected_to.weight) AS avg_strength,
    math::sum(->connected_to.interaction_count) AS total_interactions
FROM person:alice;
```

### Common Weighting Strategies

**1. Interaction Frequency**
```surreal
-- Update weight based on interactions
UPDATE connected_to
SET
    interaction_count += 1,
    weight = math::min(1.0, interaction_count / 100.0)
WHERE in = person:alice AND out = person:bob;
```

**2. Recency-Based**
```surreal
-- Higher weight for recent interactions
UPDATE connected_to
SET weight = math::max(0.1, 1.0 - (time::now() - last_interaction) / (86400 * 30))
WHERE in = person:alice;
```

**3. Similarity Score**
```surreal
-- Weight based on shared attributes
RELATE person:alice->similar_to->person:bob SET
    weight = (
        -- Calculate Jaccard similarity of interests
        count(alice.interests INTERSECT bob.interests) /
        count(alice.interests UNION bob.interests)
    );
```

### Use Cases
- **Shortest weighted path**: Navigation, routing
- **Recommendation scoring**: Similar users/products
- **Fraud detection**: Unusual transaction patterns
- **Network flow analysis**: Capacity planning
- **Influence propagation**: Social network analysis

---

## Pattern 7: Avoiding N+1 Queries with Graph Traversal

### Concept
Graph databases excel at joins. Use traversal operators instead of multiple round-trip queries.

### Anti-Pattern: N+1 Queries

```surreal
-- N+1 ANTI-PATTERN: Multiple queries
-- First query
SELECT * FROM person;

-- Then for each person (N queries)
SELECT * FROM company WHERE id = (SELECT ->works_at->company FROM person:alice);
SELECT * FROM company WHERE id = (SELECT ->works_at->company FROM person:bob);
-- ... N more queries
```

### Correct Pattern: Single Traversal

```surreal
-- CORRECT: Single graph traversal
SELECT
    *,
    ->works_at->company.* AS companies
FROM person;

-- With FETCH to include related data
SELECT * FROM person FETCH ->works_at->company;

-- Complex traversal in one query
SELECT
    name,
    ->works_at->company.name AS company_name,
    ->follows->person.name AS following,
    <-follows<-person.name AS followers
FROM person:alice;
```

### Advanced Traversal Patterns

**Multiple relationship types**
```surreal
SELECT
    name,
    ->works_at->company.{name, industry} AS employers,
    ->follows->person.{name, email} AS following,
    ->posted->post.{title, created_at} AS posts
FROM person:alice;
```

**Conditional traversal**
```surreal
SELECT
    name,
    ->works_at[WHERE role = 'Engineer']->company.* AS engineering_jobs,
    ->works_at[WHERE role = 'Manager']->company.* AS management_jobs
FROM person:alice;
```

**Aggregated traversal**
```surreal
SELECT
    name,
    count(->posted->post) AS post_count,
    count(->follows->person) AS following_count,
    count(<-follows<-person) AS follower_count
FROM person;
```

### Performance Benefits
- **Reduced latency**: 1 query vs N+1 queries
- **Lower overhead**: Single connection, single round-trip
- **Better caching**: Database can optimize single query
- **Cleaner code**: Declarative instead of imperative

### Use Cases
- Loading related entities (users with posts)
- Dashboard data (aggregated metrics)
- Entity detail pages (user profile with all relationships)
- List views with preview data

---

## Pattern Comparison Matrix

| Pattern | Complexity | Performance | Use Case |
|---------|-----------|-------------|----------|
| **Typed Relationships** | Low | High | Basic entity relationships |
| **Multi-Hop Traversal** | Medium | Medium | Social networks, recommendations |
| **Bidirectional** | Medium | High | Symmetric relationships |
| **Hierarchical** | High | Medium | Trees, org charts, taxonomies |
| **Temporal** | High | Medium | History, audit trails, versioning |
| **Weighted** | Medium | Medium | Algorithms, recommendations, scoring |
| **Single Traversal** | Low | High | Avoiding N+1, complex queries |

---

## Query Optimization Checklist

For each graph query:
- [ ] Depth limits set on all traversals (`[..3]`)
- [ ] Result limits applied (`LIMIT 100`)
- [ ] Indexes exist for filtered properties
- [ ] Relationships in correct direction for query
- [ ] Single traversal used instead of N+1 queries
- [ ] Sensitive fields filtered in responses
- [ ] Query tested with explain plan
- [ ] Performance acceptable under load

---

## Further Reading

See also:
- `modeling-guide.md` - Detailed graph modeling strategies
- `query-optimization.md` - Query performance tuning
- `performance-optimization.md` - Performance patterns
- `anti-patterns.md` - Common mistakes to avoid
