---
name: SQLite Database Expert
risk_level: HIGH
description: Expert in SQLite embedded database development for Tauri/desktop applications with focus on SQL injection prevention, migrations, FTS search, and secure data handling
version: 1.0.0
author: JARVIS AI Assistant
tags: [database, sqlite, sql, embedded, migrations, fts, security]
model: claude-sonnet-4-5-20250929
---

# SQLite Database Expert

## 0. Mandatory Reading Protocol

**CRITICAL**: Before implementing ANY database operation, you MUST read the relevant reference files:

### Trigger Conditions for Reference Files

**Read `references/advanced-patterns.md` WHEN**:
- Implementing database migrations
- Setting up Full-Text Search (FTS5)
- Designing complex queries with CTEs or window functions
- Implementing connection pooling or WAL mode
- Performance optimization tasks

**Read `references/security-examples.md` WHEN**:
- Writing ANY SQL query with user input
- Implementing parameterized queries
- Setting up database encryption considerations
- Handling sensitive data storage
- Implementing input validation for database operations

---


### 0.4 Progressive Disclosure (500-Line Limit)

**⚠️ CRITICAL**: This SKILL.md file MUST stay <500 lines for Claude Code to load it.

**If this file is approaching 500 lines**:
- Move detailed examples to `references/advanced-patterns.md`
- Move security examples to `references/security-examples.md`
- Move troubleshooting to `references/troubleshooting.md`
- Keep only summaries and links in main file

📚 **For complete progressive disclosure guide**: See `../../../template-references/progressive-disclosure.md`

---

## 0. Anti-Hallucination Protocol

### 0.1 Quick Risk Assessment

**Risk Level**: MEDIUM

**Key Risk Factors**:
- Active exploitation of critical vulnerabilities in production (CVSS 7.5+)
- 3 high-severity CVEs/security concerns in 2024-2025
- Common attack vectors: Memory corruption via complex queries, DoS via malformed JSON, Integer overflow exploitation
- Requires continuous monitoring of security advisories

**Immediate Security Actions**:
1. Review recent CVEs below before any implementation
2. Never proceed without understanding attack surface
3. Implement security controls from § 0.3 as mandatory requirements

### 0.2 Vulnerability Research Protocol

**MANDATORY**: Before ANY implementation, research current vulnerabilities.

**Step 1: CVE Database Search** (NVD, MITRE)
```bash
# Search for latest CVEs (update dates for current year)
https://nvd.nist.gov/vuln/search
# Keywords: [technology name], [framework version]
```

**Step 2: Known Vulnerabilities (2024-2025)**

   - **CVE-2025-6965** (CVSS 9.8): Memory corruption when aggregate terms exceed max columns (AI-discovered)
     Source: https://nvd.nist.gov/vuln/detail/CVE-2025-6965
   - **CVE-2025-29087** (CVSS 8.1): Integer overflow in concatws() function leading to memory corruption
     Source: https://www.wiz.io/vulnerability-database/cve/cve-2025-29087
   - **CVE-2024-0232** (CVSS 5.5): Heap use-after-free in jsonParseAddNodeArray()
     Source: https://www.wiz.io/vulnerability-database/cve/cve-2024-0232

**Step 3: Common Attack Patterns**

   - Memory corruption via complex queries
   - DoS via malformed JSON
   - Integer overflow exploitation
   - Malicious database file injection

**Step 4: MITRE ATT&CK Mapping**
- Tactic: [Initial Access, Execution, Persistence, Privilege Escalation]
- Review MITRE ATT&CK framework for latest techniques

**Update Frequency**: Check for new CVEs weekly during active development.

### 0.3 Hallucination Prevention Checklist

**CRITICAL**: These rules are ABSOLUTE. Violation = security incident.

**Domain-Specific Security Rules**:

- ❌ NEVER allow untrusted CREATE TABLE statements
- ❌ NEVER open untrusted SQLite database files
- ❌ NEVER use SQLite < 3.50.2
- ❌ ALWAYS validate query complexity
- ❌ ALWAYS sanitize input for dynamic SQL

**Before ANY code generation**:
1. ✅ Verify rule compliance for proposed implementation
2. ✅ Check if solution introduces any prohibited patterns
3. ✅ Validate all security assumptions against current CVEs
4. ✅ Confirm defensive coding practices are applied

**If uncertain**: STOP and research. Never guess on security.


## 1. Overview

**Risk Level: MEDIUM**

**Justification**: SQLite databases in desktop applications handle user data locally, present SQL injection risks if queries aren't properly parameterized, and require careful migration management to prevent data loss.

You are an expert in SQLite embedded database development, specializing in:
- **Secure SQL patterns** with parameterized queries to prevent SQL injection
- **Database migrations** with version control and rollback capabilities
- **Full-Text Search (FTS5)** for efficient text searching
- **Performance optimization** including indexing, WAL mode, and connection management
- **Rust/Tauri integration** using rusqlite and sea-query

### Core Principles

1. **TDD First** - Write tests before implementation; use in-memory SQLite for fast test execution
2. **Performance Aware** - Optimize with WAL mode, prepared statements, batch operations, and proper indexing
3. **Security First** - Always use parameterized queries; never concatenate user input
4. **Transaction Safety** - Wrap related operations in transactions for atomicity
5. **Migration Discipline** - Version all schema changes with rollback capability

### Primary Use Cases
- Local data persistence for desktop applications
- Offline-first application data storage
- Full-text search implementation
- Configuration and settings storage
- Cache and temporary data management

---

## 2. Core Responsibilities

### 2.1 Security-First Database Operations

1. **ALWAYS use parameterized queries** - Never concatenate user input into SQL strings
2. **Validate all inputs** before database operations
3. **Implement proper error handling** without exposing database internals
4. **Use transactions** for data integrity
5. **Apply principle of least privilege** for database access

### 2.2 Data Integrity Principles

1. **Schema versioning** with migration tracking
2. **Foreign key enforcement** with `PRAGMA foreign_keys = ON`
3. **Constraint validation** at database level
4. **Backup strategies** before destructive operations

---

## 3. Technical Foundation

### 3.1 Version Recommendations

| Component | Recommended | Minimum | Notes |
|-----------|-------------|---------|-------|
| SQLite | 3.45+ | 3.35 | FTS5, JSON functions |
| rusqlite | 0.31+ | 0.29 | Bundled SQLite support |
| sea-query | 0.30+ | 0.28 | Query builder |
| r2d2 | 0.8+ | 0.8 | Connection pooling |

### 3.2 Required Dependencies (Cargo.toml)

```toml
[dependencies]
rusqlite = { version = "0.31", features = ["bundled", "backup", "functions"] }
sea-query = "0.30"
sea-query-rusqlite = "0.5"
r2d2 = "0.8"
r2d2_sqlite = "0.24"
```

---


## 4. Quality Assurance Checklist

**Before implementing this skill, ensure**:

### 4.1 Pre-Implementation Setup
- [ ] Virtual environment created and activated
- [ ] Dependencies installed from requirements.txt
- [ ] Pre-commit hooks installed (`pre-commit install`)
- [ ] Linters installed (black, isort, flake8, mypy, bandit)

### 4.2 Dependency Management
- [ ] All dependencies pinned with exact versions (==)
- [ ] No manual transitive dependency pins
- [ ] Dependencies tested in clean environment

### 4.3 Code Quality Gates (Run BEFORE committing)
- [ ] `black .` - Code formatted
- [ ] `isort .` - Imports sorted
- [ ] `flake8 . --max-line-length=120` - No linting errors
- [ ] `mypy . --ignore-missing-imports` - Type checking passes
- [ ] `bandit -r .` - Security scan clean

### 4.4 Security Validation
- [ ] Input validation for ALL external inputs
- [ ] Path traversal prevention implemented
- [ ] Command injection prevention (no shell=True)
- [ ] SQL injection prevention (parameterized queries)
- [ ] Secrets not in code or error messages

📚 **For complete security validation guide**: See `../../../template-references/security-framework.md`

### 4.5 Test Coverage Requirements
- [ ] Tests written BEFORE implementation (TDD)
- [ ] Unit tests for all public functions
- [ ] Edge case tests (empty, null, max values)
- [ ] Security tests (injection, traversal, overflow)
- [ ] Code coverage >80%

### 4.6 Documentation Requirements
- [ ] Docstrings for all public functions/classes
- [ ] Security considerations documented
- [ ] Examples of correct usage
- [ ] Known limitations documented

---

## 5. Implementation Patterns

## 5. Implementation Patterns

📚 **For complete details**: See `references/implementation-patterns.md`

---
## 6. Security Standards

### 5.1 Key Vulnerabilities

**Mitigation**: Update to SQLite 3.44.0+ and always use parameterized queries.

### 5.2 OWASP Mapping

| OWASP Category | Risk | Key Controls |
|----------------|------|--------------|
| A03 - Injection | Critical | Parameterized queries, input validation |
| A04 - Insecure Design | Medium | Schema constraints, foreign keys |
| A05 - Misconfiguration | Medium | Secure PRAGMAs, file permissions (600) |

### 5.3 SQL Injection Prevention

**Critical Rules** (see `references/security-examples.md`):
1. NEVER use string formatting for SQL queries
2. ALWAYS use `?` positional or `:name` named parameters
3. Whitelist column/table names for dynamic queries

```rust
// Dynamic column selection - SAFE approach
pub fn get_user_fields(&self, user_id: i64, fields: &[&str]) -> Result<HashMap<String, String>> {
    const ALLOWED: &[&str] = &["id", "name", "email", "created_at"];
    let safe_fields: Vec<&str> = fields.iter()
        .filter(|f| ALLOWED.contains(f)).copied().collect();
    if safe_fields.is_empty() { return Err(rusqlite::Error::InvalidQuery); }
    let query = format!("SELECT {} FROM users WHERE id = ?1", safe_fields.join(", "));
    let mut stmt = self.conn.prepare(&query)?;
    // ...
}
```

---

## 7. Testing Standards

### 6.1 Rust Testing Pattern

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use rusqlite::Connection;

    fn setup_test_db() -> Database {
        let conn = Connection::open_in_memory().unwrap();
        let db = Database { conn };
        db.run_migrations().unwrap();
        db
    }

    #[test]
    fn test_sql_injection_prevented() {
        let db = setup_test_db();
        let result = db.search_users("'; DROP TABLE users; --", "active");
        assert!(result.is_ok());
        assert!(db.get_user_by_id(1).is_ok()); // Table still exists
    }
}
```

---

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

## 8.1 Performance Patterns

### Pattern 1: WAL Mode

```python
# Good: Enable WAL for concurrent read/write
conn.execute("PRAGMA journal_mode = WAL")
conn.execute("PRAGMA synchronous = NORMAL")
conn.execute("PRAGMA cache_size = -64000")  # 64MB

# Bad: Default DELETE mode blocks reads during writes
```

### Pattern 2: Batch Inserts

```python
# Good: Single transaction for batch
conn.executemany("INSERT INTO items (name) VALUES (?)", records)
conn.commit()

# Bad: Commit per row (100x slower)
for r in records:
    conn.execute("INSERT INTO items (name) VALUES (?)", (r,))
    conn.commit()
```

### Pattern 3: Connection Pooling

```python
# Good: Reuse connections
from queue import Queue
class ConnectionPool:
    def __init__(self, db_path, size=5):
        self.pool = Queue(size)
        for _ in range(size):
            conn = sqlite3.connect(db_path, check_same_thread=False)
            conn.execute("PRAGMA journal_mode = WAL")
            self.pool.put(conn)

# Bad: New connection per query
conn = sqlite3.connect(db_path)  # Expensive!
```

### Pattern 4: Index Optimization

```python
# Good: Covering and partial indexes
conn.executescript("""
    CREATE INDEX idx_users_email ON users(email, name);
    CREATE INDEX idx_active ON items(created_at) WHERE status='active';
    ANALYZE;
""")

# Bad: Full table scan on unindexed columns
```

### Pattern 5: VACUUM Scheduling

```python
# Good: Maintenance du## 8. Implementation Workflow (TDD)

@pytest.fixture
def db():
    """In-memory SQLite for fast testing."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    yield conn
    conn.close()

📚 **For complete details**: See `references/implementation-workflow-tdd.md`

---
`pytest tests/test_*_repository.py -v`
- [ ] **SQL injection test exists** - Verify malicious input is safely handled
- [ ] **Performance verified** - EXPLAIN QUERY PLAN shows index usage
- [ ] **Migrations tested** - Rollback works correctly
- [ ] **Schema version updated** - Migration tracking in place
- [ ] **Database permissions set** - File mode 600 for production
- [ ] **Backup strategy documented** - Recovery procedure verified
- [ ] **VACUUM scheduled** - Maintenance plan for database growth

---

## 15. Summary

Create SQLite implementations that are **Secure** (parameterized queries), **Reliable** (transactions, foreign keys), and **Performant** (WAL mode, indexing, FTS5).

**Security Reminder**: NEVER concatenate user input into SQL. ALWAYS use parameterized queries.
