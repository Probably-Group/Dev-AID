---
name: graph-database-expert
version: 2.0.0
description: "Graph database design with traversal queries, relationship modeling, and query optimization."
risk_level: MEDIUM
---

# Graph Database Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-943: Cypher/Gremlin Injection**
- NEVER: Build queries with string concatenation: `"MATCH (n) WHERE n.id = '" + input + "'"`
- ALWAYS: Parameterized queries: `MATCH (n) WHERE n.id = $id` with params

**CWE-918: SSRF via LOAD CSV**
- NEVER: Allow user-controlled URLs in `LOAD CSV FROM` statements
- ALWAYS: Whitelist sources, disable `apoc.import.file.use_neo4j_config=false`

**CWE-400: Traversal DoS**
- NEVER: Unbounded traversals: `MATCH path=(n)-[*]->(m)` without limits
- ALWAYS: Set `dbms.cypher.max_plan_depth`, use LIMIT, query timeouts

**CWE-611: XXE in GraphML (CVE-2023-23926)**
- NEVER: Use `apoc.import.graphml` without secure parser config
- ALWAYS: Upgrade APOC to 5.5.0+, disable external entity resolution

### 0.3 Risk Level: MEDIUM

**Verification requirements for MEDIUM risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 Cypher/Query Injection Prevention (CWE-89)

**Principle:** Never construct graph queries from untrusted input. Use parameterized queries.

```javascript
// ❌ WRONG - Cypher injection vulnerability
const query = `MATCH (u:User {name: '${userName}'}) RETURN u`;
await session.run(query);

// ✅ CORRECT - Parameterized Cypher query
const query = `MATCH (u:User {name: $name}) RETURN u`;
await session.run(query, { name: userName });
```

```python
# ❌ WRONG - Gremlin string injection
query = f"g.V().has('name', '{name}')"

# ✅ CORRECT - Parameterized Gremlin
g.V().has('name', name)  # Python driver handles parameterization
```

### 1.2 Traversal Depth Limits (CWE-400)

**Principle:** Always limit traversal depth to prevent resource exhaustion.

```cypher
// ❌ WRONG - Unbounded traversal
MATCH path = (a)-[*]-(b) RETURN path

// ✅ CORRECT - Bounded traversal
MATCH path = (a)-[*1..5]-(b) RETURN path LIMIT 100
```

### 1.3 Authorization on Graph Access (CWE-862)

**Principle:** Implement row-level security. Users should only traverse accessible nodes.

### 1.4 Connection Security (CWE-319)

**Principle:** Always use TLS for database connections. Verify certificates.

### 1.5 Credential Management (CWE-798)

**Principle:** Never hardcode database credentials. Use environment or secret managers.

### 1.6 Query Timeouts (CWE-770)

**Principle:** Set query timeouts to prevent long-running queries from consuming resources.

---

## 2. Version Requirements

**ALWAYS use these minimum versions:**

```yaml
# Neo4j
neo4j: "5.15+"
neo4j-driver: "5.15+"

# Amazon Neptune
neptune: "1.3.0+"

# ArangoDB
arangodb: "3.11+"

# SurrealDB
surrealdb: "1.2+"

# Drivers
py2neo: "2021.1+"
gremlinpython: "3.7+"
```

---

## 3. Code Patterns

### 3.1 WHEN modeling graph schemas

```cypher
// ❌ WRONG - No constraints, no indexes
CREATE (u:User {name: 'Alice'})

// ✅ CORRECT - Neo4j schema with constraints and indexes
// Create uniqueness constraints
CREATE CONSTRAINT user_email_unique IF NOT EXISTS
FOR (u:User) REQUIRE u.email IS UNIQUE;

CREATE CONSTRAINT user_id_unique IF NOT EXISTS
FOR (u:User) REQUIRE u.id IS UNIQUE;

// Create existence constraints
CREATE CONSTRAINT user_email_exists IF NOT EXISTS
FOR (u:User) REQUIRE u.email IS NOT NULL;

// Create indexes for common lookups
CREATE INDEX user_name_index IF NOT EXISTS
FOR (u:User) ON (u.name);

CREATE INDEX user_created_index IF NOT EXISTS
FOR (u:User) ON (u.createdAt);

// Composite index for common query patterns
CREATE INDEX user_status_created IF NOT EXISTS
FOR (u:User) ON (u.status, u.createdAt);

// Full-text index for search
CREATE FULLTEXT INDEX user_search IF NOT EXISTS
FOR (u:User) ON EACH [u.name, u.bio];
```

### 3.2 WHEN implementing a Neo4j repository in TypeScript

```typescript
// ❌ WRONG - No parameterization, no error handling
async function findUser(name: string) {
  const result = await session.run(`MATCH (u:User {name: '${name}'}) RETURN u`);
  return result.records[0];
}

// ✅ CORRECT - Type-safe Neo4j repository
import neo4j, { Driver, Session, Transaction } from 'neo4j-driver';
import { z } from 'zod';

// Schema validation
const UserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  name: z.string().min(1).max(100),
  createdAt: z.date(),
});

type User = z.infer<typeof UserSchema>;

interface GraphConfig {
  uri: string;
  username: string;
  password: string;
  database?: string;
  maxConnectionPoolSize?: number;
  connectionTimeout?: number;
}

class Neo4jRepository {
  private driver: Driver;
  private database: string;

  constructor(config: GraphConfig) {
    this.driver = neo4j.driver(
      config.uri,
      neo4j.auth.basic(config.username, config.password),
      {
        maxConnectionPoolSize: config.maxConnectionPoolSize ?? 50,
        connectionTimeout: config.connectionTimeout ?? 30000,
        encrypted: 'ENCRYPTION_ON',
        trust: 'TRUST_SYSTEM_CA_SIGNED_CERTIFICATES',
      }
    );
    this.database = config.database ?? 'neo4j';
  }

  async findUserById(id: string): Promise<User | null> {
    const session = this.driver.session({ database: this.database });
    try {
      const result = await session.run(
        `MATCH (u:User {id: $id})
         RETURN u {.id, .email, .name, .createdAt} AS user`,
        { id }
      );

      if (result.records.length === 0) return null;

      const record = result.records[0].get('user');
      return UserSchema.parse({
        ...record,
        createdAt: new Date(record.createdAt),
      });
    } finally {
      await session.close();
    }
  }

  async findUserConnections(
    userId: string,
    relationshipType: string,
    maxDepth: number = 3,
    limit: number = 100
  ): Promise<User[]> {
    // Validate inputs
    if (maxDepth > 5) {
      throw new Error('Max depth cannot exceed 5');
    }
    if (limit > 1000) {
      throw new Error('Limit cannot exceed 1000');
    }

    // Allowlist relationship types
    const allowedRelTypes = ['FOLLOWS', 'FRIENDS_WITH', 'WORKS_WITH'];
    if (!allowedRelTypes.includes(relationshipType)) {
      throw new Error(`Invalid relationship type: ${relationshipType}`);
    }

    const session = this.driver.session({ database: this.database });
    try {
      const result = await session.run(
        `MATCH (start:User {id: $userId})
         MATCH path = (start)-[:${relationshipType}*1..${maxDepth}]-(connected:User)
         WHERE connected.id <> $userId
         RETURN DISTINCT connected {.id, .email, .name, .createdAt} AS user
         LIMIT $limit`,
        { userId, limit: neo4j.int(limit) }
      );

      return result.records.map(record => {
        const data = record.get('user');
        return UserSchema.parse({
          ...data,
          createdAt: new Date(data.createdAt),
        });
      });
    } finally {
      await session.close();
    }
  }

  async createUserWithTransaction(user: Omit<User, 'createdAt'>): Promise<User> {
    const session = this.driver.session({ database: this.database });
    const tx = session.beginTransaction();

    try {
      // Create user
      const result = await tx.run(
        `CREATE (u:User {
          id: $id,
          email: $email,
          name: $name,
          createdAt: datetime()
        })
        RETURN u {.id, .email, .name, .createdAt} AS user`,
        user
      );

      // Create audit log
      await tx.run(
        `MATCH (u:User {id: $userId})
         CREATE (log:AuditLog {
           action: 'USER_CREATED',
           entityId: $userId,
           timestamp: datetime()
         })
         CREATE (u)-[:HAS_AUDIT]->(log)`,
        { userId: user.id }
      );

      await tx.commit();

      const record = result.records[0].get('user');
      return UserSchema.parse({
        ...record,
        createdAt: new Date(record.createdAt),
      });
    } catch (error) {
      await tx.rollback();
      throw error;
    } finally {
      await session.close();
    }
  }

  async close(): Promise<void> {
    await this.driver.close();
  }
}

// Factory with config from environment
function createNeo4jRepository(): Neo4jRepository {
  return new Neo4jRepository({
    uri: process.env.NEO4J_URI!,
    username: process.env.NEO4J_USERNAME!,
    password: process.env.NEO4J_PASSWORD!,
    database: process.env.NEO4J_DATABASE,
  });
}
```

### 3.3 WHEN implementing graph traversal algorithms

```cypher
// ❌ WRONG - No depth limit, inefficient
MATCH path = shortestPath((a:User)-[*]-(b:User))
WHERE a.id = $startId AND b.id = $endId
RETURN path

// ✅ CORRECT - Optimized shortest path with limits
MATCH (start:User {id: $startId}), (end:User {id: $endId})
CALL apoc.algo.dijkstra(start, end, 'CONNECTED_TO', 'weight') YIELD path, weight
WHERE length(path) <= 10
RETURN path, weight
LIMIT 1
```

```python
# ✅ CORRECT - Python graph traversal with safeguards
from neo4j import GraphDatabase
from typing import Generator, Optional
from dataclasses import dataclass

@dataclass
class TraversalConfig:
    max_depth: int = 5
    max_results: int = 1000
    timeout_seconds: int = 30
    relationship_types: list[str] | None = None

class GraphTraverser:
    def __init__(self, driver: GraphDatabase.driver):
        self.driver = driver

    def bfs_traverse(
        self,
        start_node_id: str,
        config: TraversalConfig,
    ) -> Generator[dict, None, None]:
        """Breadth-first traversal with configurable limits."""

        # Build relationship filter
        rel_filter = ""
        if config.relationship_types:
            # Allowlist validation
            allowed = {'FOLLOWS', 'FRIENDS_WITH', 'WORKS_WITH', 'REPORTS_TO'}
            invalid = set(config.relationship_types) - allowed
            if invalid:
                raise ValueError(f"Invalid relationship types: {invalid}")
            rel_filter = ":" + "|".join(config.relationship_types)

        query = f"""
        MATCH (start {{id: $startId}})
        CALL apoc.path.subgraphNodes(start, {{
            relationshipFilter: '{rel_filter}',
            maxLevel: $maxDepth,
            limit: $maxResults
        }}) YIELD node
        RETURN node {{.*}} AS n
        """

        with self.driver.session() as session:
            result = session.run(
                query,
                startId=start_node_id,
                maxDepth=min(config.max_depth, 10),  # Hard cap
                maxResults=min(config.max_results, 10000),  # Hard cap
                timeout=config.timeout_seconds,
            )

            for record in result:
                yield dict(record["n"])

    def find_shortest_paths(
        self,
        start_id: str,
        end_id: str,
        max_paths: int = 5,
        max_depth: int = 10,
    ) -> list[list[str]]:
        """Find multiple shortest paths between nodes."""

        query = """
        MATCH (start {id: $startId}), (end {id: $endId})
        CALL apoc.algo.allSimplePaths(start, end, '', $maxDepth)
        YIELD path
        WITH path
        ORDER BY length(path)
        LIMIT $maxPaths
        RETURN [node IN nodes(path) | node.id] AS nodeIds
        """

        with self.driver.session() as session:
            result = session.run(
                query,
                startId=start_id,
                endId=end_id,
                maxDepth=min(max_depth, 15),
                maxPaths=min(max_paths, 100),
            )

            return [record["nodeIds"] for record in result]

    def pagerank(
        self,
        label: str,
        relationship_type: str,
        top_n: int = 100,
    ) -> list[tuple[str, float]]:
        """Calculate PageRank for nodes."""

        # Validate label (prevent injection)
        if not label.isalnum():
            raise ValueError("Label must be alphanumeric")
        if not relationship_type.isalnum():
            raise ValueError("Relationship type must be alphanumeric")

        query = f"""
        CALL gds.pageRank.stream({{
            nodeProjection: '{label}',
            relationshipProjection: '{relationship_type}',
            maxIterations: 20,
            dampingFactor: 0.85
        }})
        YIELD nodeId, score
        RETURN gds.util.asNode(nodeId).id AS id, score
        ORDER BY score DESC
        LIMIT $topN
        """

        with self.driver.session() as session:
            result = session.run(query, topN=min(top_n, 1000))
            return [(record["id"], record["score"]) for record in result]
```

### 3.4 WHEN implementing Gremlin queries for Neptune/TinkerPop

```python
# ❌ WRONG - No error handling, string concatenation
def find_user(g, name):
    return g.V().has('name', name).next()

# ✅ CORRECT - Type-safe Gremlin traversals
from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.process.graph_traversal import GraphTraversalSource, __
from gremlin_python.process.traversal import T, P, Order
from typing import Optional, TypedDict
from contextlib import contextmanager
import ssl

class VertexData(TypedDict):
    id: str
    label: str
    properties: dict

class NeptuneConfig:
    endpoint: str
    port: int = 8182
    use_ssl: bool = True
    region: str = "us-east-1"

class NeptuneRepository:
    def __init__(self, config: NeptuneConfig):
        self.config = config
        self._connection: Optional[DriverRemoteConnection] = None

    @contextmanager
    def _get_traversal(self):
        """Context manager for graph traversal with connection cleanup."""
        connection_string = f"wss://{self.config.endpoint}:{self.config.port}/gremlin"

        # SSL context for Neptune
        ssl_context = ssl.create_default_context()

        connection = DriverRemoteConnection(
            connection_string,
            'g',
            transport_factory=lambda: ssl_context,
        )

        try:
            g = traversal().withRemote(connection)
            yield g
        finally:
            connection.close()

    def find_vertex_by_id(self, vertex_id: str) -> Optional[VertexData]:
        """Find vertex by ID with property map."""
        with self._get_traversal() as g:
            result = (
                g.V(vertex_id)
                .project('id', 'label', 'properties')
                .by(T.id)
                .by(T.label)
                .by(__.valueMap(True))
                .toList()
            )

            if not result:
                return None

            return result[0]

    def find_connected_vertices(
        self,
        start_id: str,
        edge_label: str,
        max_depth: int = 3,
        limit: int = 100,
    ) -> list[VertexData]:
        """Find vertices connected within max_depth hops."""

        # Validate edge_label (prevent injection)
        allowed_edges = {'follows', 'friends_with', 'works_with'}
        if edge_label not in allowed_edges:
            raise ValueError(f"Invalid edge label: {edge_label}")

        # Cap limits
        max_depth = min(max_depth, 5)
        limit = min(limit, 1000)

        with self._get_traversal() as g:
            return (
                g.V(start_id)
                .repeat(__.out(edge_label).simplePath())
                .times(max_depth)
                .emit()
                .dedup()
                .limit(limit)
                .project('id', 'label', 'properties')
                .by(T.id)
                .by(T.label)
                .by(__.valueMap(True))
                .toList()
            )

    def create_vertex_with_edges(
        self,
        label: str,
        properties: dict,
        edges: list[tuple[str, str, str]],  # (edge_label, direction, target_id)
    ) -> str:
        """Atomically create vertex with edges."""

        # Validate label
        if not label.isalnum():
            raise ValueError("Label must be alphanumeric")

        with self._get_traversal() as g:
            # Start with vertex creation
            t = g.addV(label)

            # Add properties
            for key, value in properties.items():
                if not key.isalnum():
                    raise ValueError(f"Property key must be alphanumeric: {key}")
                t = t.property(key, value)

            # Store vertex for edge creation
            t = t.as_('new_vertex')

            # Add edges
            for edge_label, direction, target_id in edges:
                if not edge_label.isalnum():
                    raise ValueError(f"Edge label must be alphanumeric: {edge_label}")

                if direction == 'out':
                    t = t.addE(edge_label).to(__.V(target_id)).from_('new_vertex')
                elif direction == 'in':
                    t = t.addE(edge_label).from_(__.V(target_id)).to('new_vertex')
                else:
                    raise ValueError(f"Invalid direction: {direction}")

            # Return to vertex and get ID
            result = t.select('new_vertex').id_().next()
            return str(result)

    def upsert_vertex(
        self,
        label: str,
        key_property: str,
        key_value: str,
        properties: dict,
    ) -> str:
        """Upsert vertex by key property."""

        with self._get_traversal() as g:
            result = (
                g.V()
                .has(label, key_property, key_value)
                .fold()
                .coalesce(
                    __.unfold(),
                    __.addV(label).property(key_property, key_value)
                )
                .as_('v')
            )

            # Update properties
            for key, value in properties.items():
                result = result.property(key, value)

            return str(result.id_().next())
```

### 3.5 WHEN implementing graph search

```cypher
-- ❌ WRONG - Full scan without index
MATCH (u:User)
WHERE u.name CONTAINS $searchTerm
RETURN u

-- ✅ CORRECT - Full-text search with Neo4j
CALL db.index.fulltext.queryNodes('user_search', $searchTerm + '~')
YIELD node, score
WHERE score > 0.5
RETURN node {.id, .name, .email} AS user, score
ORDER BY score DESC
LIMIT 20
```

---

## 4. Anti-Patterns

**NEVER:**
- Construct Cypher/Gremlin queries from user input
- Allow unbounded graph traversals
- Skip connection encryption (TLS)
- Hardcode database credentials
- Return unlimited result sets
- Allow arbitrary relationship types in traversals
- Skip query timeouts
- Expose internal node IDs to clients

---

## 5. Testing

**ALWAYS test graph database code:**

```typescript
import { describe, it, expect, beforeAll, afterAll } from 'vitest';

describe('Neo4jRepository', () => {
  let repo: Neo4jRepository;

  beforeAll(async () => {
    repo = new Neo4jRepository({
      uri: process.env.NEO4J_TEST_URI!,
      username: 'neo4j',
      password: 'test',
      database: 'test',
    });
  });

  afterAll(async () => {
    await repo.close();
  });

  it('prevents Cypher injection', async () => {
    const maliciousInput = "' OR 1=1 --";
    const result = await repo.findUserById(maliciousInput);
    expect(result).toBeNull(); // Should not find anything
  });

  it('enforces traversal depth limits', async () => {
    await expect(
      repo.findUserConnections('user-1', 'FOLLOWS', 10)
    ).rejects.toThrow('Max depth cannot exceed 5');
  });

  it('validates relationship types', async () => {
    await expect(
      repo.findUserConnections('user-1', 'MALICIOUS_REL', 2)
    ).rejects.toThrow('Invalid relationship type');
  });

  it('respects result limits', async () => {
    const results = await repo.findUserConnections('user-1', 'FOLLOWS', 3, 10);
    expect(results.length).toBeLessThanOrEqual(10);
  });

  it('handles transactions correctly', async () => {
    const user = await repo.createUserWithTransaction({
      id: crypto.randomUUID(),
      email: 'test@example.com',
      name: 'Test User',
    });

    expect(user.id).toBeDefined();

    // Verify audit log was created
    const session = repo['driver'].session();
    try {
      const result = await session.run(
        `MATCH (u:User {id: $id})-[:HAS_AUDIT]->(log:AuditLog)
         RETURN log`,
        { id: user.id }
      );
      expect(result.records.length).toBe(1);
    } finally {
      await session.close();
    }
  });
});
```

---

## 6. Pre-Generation Checklist

**BEFORE generating any graph database code:**

- [ ] All queries use parameterization (no string concatenation)
- [ ] Traversal depth is bounded (max 5-10 levels)
- [ ] Result sets are limited
- [ ] Query timeouts configured
- [ ] Connection uses TLS encryption
- [ ] Credentials from environment variables
- [ ] Relationship types validated against allowlist
- [ ] Indexes created for common query patterns
- [ ] Constraints enforce data integrity
- [ ] Node IDs are UUIDs (not internal IDs)
