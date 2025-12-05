# Graph Database Security Examples

This document provides security patterns and examples for graph database implementations.

## 1. Access Control

### Row-Level Security on Nodes

```surreal
-- Row-level security on nodes
DEFINE TABLE document SCHEMAFULL
    PERMISSIONS
        FOR select WHERE public = true OR owner = $auth.id
        FOR create WHERE $auth.id != NONE
        FOR update, delete WHERE owner = $auth.id;

-- Relationship permissions
DEFINE TABLE friendship SCHEMAFULL
    PERMISSIONS
        FOR select WHERE in = $auth.id OR out = $auth.id
        FOR create WHERE in = $auth.id
        FOR delete WHERE in = $auth.id OR out = $auth.id;

-- Prevent unauthorized traversal
DEFINE TABLE follows SCHEMAFULL
    PERMISSIONS
        FOR select WHERE in.public = true OR in.id = $auth.id;
```

### Hierarchical Access Control

```surreal
-- Organization hierarchy with access control
DEFINE TABLE org_unit SCHEMAFULL
    PERMISSIONS
        FOR select WHERE
            id = $auth.org_unit OR
            id IN (SELECT ->manages[..5]->org_unit.id FROM $auth.org_unit);

-- Restrict traversal to authorized paths
SELECT ->reports_to[..3]->org_unit.*
FROM $auth.org_unit
WHERE $auth.role = 'manager';
```

---

## 2. Injection Prevention

### Parameterized Queries

**SECURE: Parameterized queries**
```surreal
-- Always use parameters
LET $person_id = "person:alice";
SELECT ->follows->person.* FROM $person_id;
```

```python
# Python SDK with parameters
async def get_followers_secure(db: Surreal, user_id: str) -> list[dict]:
    """Secure query with parameterization."""
    result = await db.query(
        'SELECT <-follows<-person.* FROM $person LIMIT 100',
        {"person": f"person:{user_id}"}
    )
    return result[0]['result']
```

**VULNERABLE: String concatenation**
```python
# DON'T DO THIS - SQL injection risk!
async def get_followers_vulnerable(db: Surreal, user_id: str):
    # Attacker could inject: "alice; DELETE FROM person; --"
    query = f"SELECT <-follows<-person.* FROM person:{user_id}"
    return await db.query(query)
```

### Input Validation

```python
import re
from typing import Optional

def validate_record_id(record_id: str) -> Optional[str]:
    """Validate record ID format before use."""
    # Allow only alphanumeric and underscore
    if not re.match(r'^[a-zA-Z0-9_]+:[a-zA-Z0-9_]+$', record_id):
        raise ValueError(f"Invalid record ID format: {record_id}")
    return record_id

async def get_user_secure(db: Surreal, user_id: str) -> dict:
    """Get user with input validation."""
    # Validate before using in query
    validate_record_id(f"person:{user_id}")

    result = await db.query(
        "SELECT * FROM $person",
        {"person": f"person:{user_id}"}
    )
    return result[0]['result'][0]
```

---

## 3. Query Depth Limits

### Prevent Denial of Service

**SAFE: Bounded traversal**
```surreal
-- Always set depth limits
SELECT ->follows[..3]->person.* FROM person:alice;

-- Limit results
SELECT ->follows->person.* FROM person:alice LIMIT 100;

-- Combined limits
SELECT ->follows[..2]->person.name
FROM person:alice
LIMIT 50;
```

**DANGEROUS: Unbounded traversal**
```surreal
-- DON'T: Could traverse millions of nodes!
-- SELECT ->follows->person.* FROM person:alice;

-- DON'T: Infinite recursion possible
-- SELECT ->follows[..]->person.* FROM person:alice;
```

### Application-Level Depth Limits

```python
class GraphQueryService:
    MAX_DEPTH = 5
    MAX_RESULTS = 1000

    def __init__(self, db: Surreal):
        self.db = db

    async def get_connections(
        self,
        node_id: str,
        relationship: str,
        depth: int = 2
    ) -> list[dict]:
        """Get connected nodes with enforced limits."""
        # Enforce maximum depth
        if depth > self.MAX_DEPTH:
            raise ValueError(
                f"Maximum depth is {self.MAX_DEPTH} to prevent runaway queries"
            )

        # Enforce depth > 0
        if depth < 1:
            raise ValueError("Depth must be at least 1")

        query = f"""
            SELECT ->{relationship}[..{depth}]->*.*
            FROM $node_id
            LIMIT {self.MAX_RESULTS}
        """

        result = await self.db.query(query, {"node_id": node_id})
        return result[0]['result']
```

---

## 4. Data Exposure Prevention

### Filter Sensitive Fields

**Good: Selective field exposure**
```surreal
-- Only expose necessary fields
SELECT
    name,
    public_bio,
    ->follows->person.{name, public_bio} AS following
FROM person:alice;

-- Filter sensitive data in traversals
SELECT
    id,
    name,
    ->works_at->company.{name, industry} AS employers
FROM person
WHERE id = $auth.id;
```

**Bad: Expose all fields**
```surreal
-- DON'T: May include email, phone, private data
-- SELECT ->follows->person.* FROM person:alice;

-- DON'T: Traversal may leak sensitive relationships
-- SELECT ->*->*.* FROM person:alice;
```

### Data Masking

```python
from typing import Any

def mask_sensitive_fields(data: dict[str, Any]) -> dict[str, Any]:
    """Mask sensitive fields in query results."""
    sensitive_fields = {'email', 'phone', 'ssn', 'password_hash'}

    masked = {}
    for key, value in data.items():
        if key in sensitive_fields:
            masked[key] = "***REDACTED***"
        elif isinstance(value, dict):
            masked[key] = mask_sensitive_fields(value)
        elif isinstance(value, list):
            masked[key] = [
                mask_sensitive_fields(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            masked[key] = value

    return masked

async def get_user_public(db: Surreal, user_id: str) -> dict:
    """Get user data with sensitive fields masked."""
    result = await db.query(
        "SELECT * FROM $person",
        {"person": f"person:{user_id}"}
    )

    user_data = result[0]['result'][0]
    return mask_sensitive_fields(user_data)
```

---

## 5. Rate Limiting

### Query Rate Limits

```python
from datetime import datetime, timedelta
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_queries: int = 100, window_seconds: int = 60):
        self.max_queries = max_queries
        self.window = timedelta(seconds=window_seconds)
        self.queries = defaultdict(list)

    def check_rate_limit(self, user_id: str) -> bool:
        """Check if user has exceeded rate limit."""
        now = datetime.now()
        cutoff = now - self.window

        # Remove old queries
        self.queries[user_id] = [
            ts for ts in self.queries[user_id]
            if ts > cutoff
        ]

        # Check limit
        if len(self.queries[user_id]) >= self.max_queries:
            return False

        # Record query
        self.queries[user_id].append(now)
        return True

# Usage
rate_limiter = RateLimiter(max_queries=100, window_seconds=60)

async def execute_query_with_rate_limit(
    db: Surreal,
    user_id: str,
    query: str
) -> list[dict]:
    """Execute query with rate limiting."""
    if not rate_limiter.check_rate_limit(user_id):
        raise PermissionError(
            f"Rate limit exceeded for user {user_id}. "
            "Try again later."
        )

    return await db.query(query)
```

---

## 6. Audit Logging

### Query Audit Trail

```python
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AuditedGraphService:
    def __init__(self, db: Surreal):
        self.db = db

    async def query_with_audit(
        self,
        query: str,
        params: dict,
        user_id: str,
        operation: str
    ) -> list[dict]:
        """Execute query with audit logging."""
        start_time = datetime.now()

        try:
            result = await self.db.query(query, params)

            # Log successful query
            logger.info(
                "Graph query executed",
                extra={
                    "user_id": user_id,
                    "operation": operation,
                    "query": query[:100],  # Truncate for logs
                    "params": params,
                    "duration_ms": (datetime.now() - start_time).total_seconds() * 1000,
                    "result_count": len(result[0].get('result', [])),
                    "timestamp": datetime.now().isoformat()
                }
            )

            return result

        except Exception as e:
            # Log failed query
            logger.error(
                "Graph query failed",
                extra={
                    "user_id": user_id,
                    "operation": operation,
                    "query": query[:100],
                    "params": params,
                    "error": str(e),
                    "duration_ms": (datetime.now() - start_time).total_seconds() * 1000,
                    "timestamp": datetime.now().isoformat()
                },
                exc_info=True
            )
            raise
```

---

## 7. Secure Configuration

### Database Connection Security

```python
from pydantic import BaseSettings, SecretStr

class DatabaseConfig(BaseSettings):
    """Secure database configuration."""
    url: str = "ws://localhost:8000/rpc"
    username: SecretStr
    password: SecretStr
    namespace: str
    database: str

    # SSL/TLS settings
    use_tls: bool = True
    verify_ssl: bool = True
    ca_cert_path: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

async def create_secure_connection(config: DatabaseConfig) -> Surreal:
    """Create database connection with security settings."""
    db = Surreal(config.url)
    await db.connect()

    # Use secure authentication
    await db.signin({
        "user": config.username.get_secret_value(),
        "pass": config.password.get_secret_value()
    })

    await db.use(config.namespace, config.database)
    return db
```

---

## Security Checklist

Before deploying graph database code:

### Query Security
- [ ] All queries use parameterization (no string concatenation)
- [ ] Input validation on all user-provided values
- [ ] Depth limits set on all traversals (max 5-10)
- [ ] Result limits on all queries (max 1000)
- [ ] Sensitive fields filtered in responses

### Access Control
- [ ] Row-level security defined on all tables
- [ ] Relationship permissions configured
- [ ] Authentication required for all operations
- [ ] Authorization checks for traversals

### Monitoring & Auditing
- [ ] Query audit logging enabled
- [ ] Rate limiting configured
- [ ] Performance monitoring active
- [ ] Alert thresholds set for anomalies

### Configuration
- [ ] Credentials stored in environment variables
- [ ] TLS/SSL enabled for connections
- [ ] Certificate validation enabled
- [ ] No hardcoded secrets in code

### Testing
- [ ] Security tests cover injection scenarios
- [ ] Access control tests verify permissions
- [ ] Rate limiting tests verify enforcement
- [ ] Depth limit tests prevent DoS

---

## Common Security Vulnerabilities

### 1. Graph Traversal Injection

**Vulnerability**: User input in traversal paths
```python
# VULNERABLE
async def get_related(db, user_id, rel_type):
    # Attacker could inject: "follows->person->DELETE person"
    query = f"SELECT ->{rel_type}->*.* FROM person:{user_id}"
    return await db.query(query)
```

**Mitigation**: Validate relationship types
```python
# SECURE
ALLOWED_RELATIONSHIPS = {'follows', 'works_at', 'friends_with'}

async def get_related_secure(db, user_id, rel_type):
    if rel_type not in ALLOWED_RELATIONSHIPS:
        raise ValueError(f"Invalid relationship type: {rel_type}")

    query = f"SELECT ->{rel_type}->*.* FROM $person LIMIT 100"
    return await db.query(query, {"person": f"person:{user_id}"})
```

### 2. Unauthorized Data Exfiltration

**Vulnerability**: Traversal exposes private data
```surreal
-- User can see private connections
SELECT ->follows->person.* FROM person:attacker;
```

**Mitigation**: Filter based on privacy settings
```surreal
-- Only show public profiles
SELECT ->follows->person.{name, public_bio}
FROM person:alice
WHERE ->follows->person.public = true;
```

### 3. Denial of Service via Deep Traversal

**Vulnerability**: No depth limits
```surreal
-- Could traverse entire graph
SELECT ->follows->person.* FROM person:alice;
```

**Mitigation**: Enforce depth and result limits
```surreal
-- Bounded traversal
SELECT ->follows[..2]->person.* FROM person:alice LIMIT 50;
```
