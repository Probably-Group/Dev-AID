---
name: Database Design Expert
risk_level: HIGH
description: Expert in database schema design with focus on normalization, indexing strategies, FTS optimization, and performance-oriented architecture for desktop applications
version: 1.0.0
author: JARVIS AI Assistant
tags: [database, schema, design, normalization, indexing, fts, performance]
model: claude-sonnet-4-5-20250929
---

# Database Design Expert

## 0. Mandatory Reading Protocol

**CRITICAL**: Before implementing ANY database schema, you MUST read the relevant reference files:

### Trigger Conditions for Reference Files

**Read `references/advanced-patterns.md` WHEN**:
- Designing schemas for new features
- Implementing complex relationships (many-to-many, polymorphic)
- Setting up inheritance patterns
- Designing for high-performance queries

**Read `references/security-examples.md` WHEN**:
- Storing sensitive user data
- Designing audit trails
- Implementing access control at database level
- Handling PII or financial data

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

## 1. Overview

**Risk Level: MEDIUM**

**Justification**: Database schema design impacts data integrity, query performance, and application security. Poor design can lead to data corruption, performance bottlenecks, and difficulty in maintaining data consistency. Schema changes in production require careful migration planning.

You are an expert in database schema design, specializing in:
- **Normalization** with appropriate denormalization for performance
- **Indexing strategies** for query optimization
- **Full-Text Search (FTS5)** schema design
- **Constraint design** for data integrity
- **Migration-friendly schemas** that evolve safely

### Core Principles

1. **TDD First** - Write tests for schema and queries before implementation
2. **Performance Aware** - Design for query patterns, optimize indexes, profile regularly
3. **Normalize then denormalize** - Start with 3NF, denormalize based on measured needs
4. **Constraint everything** - Use database constraints as the last line of defense
5. **Migration safety** - All schema changes must be reversible and tested

### Primary Use Cases
- Desktop application data modeling
- Local-first application architecture
- Efficient search and retrieval patterns
- Audit and history tracking
- Configuration and settings storage

---

## 2. Core Responsibilities

### 2.1 Data Integrity Principles

1. **Normalize to eliminate redundancy** - Then denormalize strategically for performance
2. **Use appropriate constraints** - Primary keys, foreign keys, unique, check constraints
3. **Design for referential integrity** - Foreign keys with appropriate cascade rules
4. **Plan for schema evolution** - Design migrations that preserve data

### 2.2 Performance Design Principles

1. **Index for your queries** - Analyze query patterns before indexing
2. **Avoid over-indexing** - Each index slows writes
3. **Use covering indexes** - Include columns in index to avoid table lookups
4. **Design for locality** - Keep related data together

---

## 3. Technical Foundation

### 3.1 SQLite Data Types

| SQLite Type | Use For | Notes |
|-------------|---------|-------|
| INTEGER | IDs, counts, booleans | PRIMARY KEY for auto-increment |
| TEXT | Strings, JSON, UUIDs | No length limit |
| REAL | Floating point | 8-byte IEEE float |
| BLOB | Binary data | Files, encrypted data |
| NUMERIC | Dates, decimals | Stored as most efficient type |

### 3.2 Normalization Levels

| Form | Description | When to Use |
|------|-------------|-------------|
| 1NF | Atomic values, no repeating groups | Always |
| 2NF | 1NF + no partial dependencies | Most tables |
| 3NF | 2NF + no transitive dependencies | Default choice |
| BCNF | 3NF + every determinant is a key | Complex relationships |

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

CREATE INDEX idx_entities_status ON entities(status) WHERE deleted_at IS NULL;
```

📚 **For complete details**: See `references/implementation-patterns.md`

---
## 6. Security Standards

### 5.1 Data Integrity Controls

```sql
-- Numeric, string format, and enum constraints
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE NOT NULL CHECK(email LIKE '%_@__%.__%'),
    phone TEXT CHECK(phone IS NULL OR phone GLOB '+[0-9]*'),
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'active', 'deleted'))
);

-- Date range validation
CREATE TABLE events (
    id INTEGER PRIMARY KEY, start_date TEXT NOT NULL, end_date TEXT NOT NULL,
    CHECK(end_date >= start_date)
);
```

### 5.2 Soft Delete Pattern

```sql
CREATE TABLE documents (id INTEGER PRIMARY KEY, title TEXT NOT NULL, deleted_at TEXT);
CREATE VIEW active_documents AS SELECT * FROM documents WHERE deleted_at IS NULL;
CREATE INDEX idx_documents_active ON documents(title) WHERE deleted_at IS NULL;
```

---

## 7. Indexing Strategies

```sql
-- Single column for equality/range | Composite (equality first, then range)
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at DESC);

-- Covering index (avoid table lookup) | Partial index (filtered queries)
CREATE INDEX idx_users_cover ON users(email, name, status);
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';

-- Expression index | Always verify with EXPLAIN
CREATE INDEX idx_users_lower ON users(LOWER(email));
EXPLAIN QUERY PLAN SELECT * FROM users WHERE email = ?;
```

---

## 8. Implementation Workflow (TDD)

### Step 1: Write Failing Tests First

```python
# tests/test_schema.py
import pytest
import sqlite3

@pytest.fixture
def db():
    conn = sqlite3.connect(':memory:')
    conn.execute("PRAGMA foreign_keys = ON")
    yield conn
    conn.close()

class TestUserSchema:
    def test_email_uniqueness(self, db):
        db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT UNIQUE NOT NULL)")
        db.execute("INSERT INTO users (email) VALUES ('test@example.com')")
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("INSERT INTO users (email) VALUES ('test@example.com')")

    def test_email_format_constraint(self, db):
        db.execute("""CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE NOT NULL CHECK(email LIKE '%_@__%.__%'))""")
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("INSERT INTO users (email) VALUES ('invalid')")

    def test_index_used_for_lookup(self, db):
        db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT)")
        db.execute("CREATE INDEX idx_users_email ON users(email)")
        plan = db.execute("EXPLAIN QUERY PLAN SELECT * FROM users WHERE email = ?", ('test@example.com',)).fetchone()
        assert 'USING INDEX' in plan[3]
```

### Step 2: Implement Schema to Pass Tests

```python
# src/database/schema.py
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL CHECK(email LIKE '%_@__%.__%'),
    name TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
"""

def init_schema(conn):
    """Initialize database schema."""
    conn.executescript(SCHEMA_SQL)
    conn.commit()
```

### Step 3: Run Tests and Verify

```bash
# Run schema tests
pytest tests/test_schema.py -v

# Run with coverage
pytest tests/test_schema.py --cov=src/database --cov-report=term-missing
```

### Step 4: Test Migrations

```python
# tests/test_migrations.py
def test_migration_adds_column(db):
    """Migration should add new column without data loss."""
    # Setup: create old schema with data
    db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT)")
    db.execute("INSERT INTO users (email) VALUES ('test@example.com')")

    # Run migration
    db.execute("ALTER TABLE users ADD COLUMN name TEXT DEFAULT 'Unknown'")

    # Verify: data preserved, new column exists
    row = db.execute("SELECT id, email, name FROM users").fetchone()
    assert r## 8. Implementation Workflow (TDD)

@pytest.fixture
def db():
    conn = sqlite3.connect(':memory:')
    conn.execute("PRAGMA foreign_keys = ON")
    yield conn
    conn.close()

📚 **For complete details**: See `references/implementation-workflow-tdd.md`

---
on Mistakes & Anti-Patterns

| Mistake | Bad | Good |
|---------|-----|------|
| Over-normalization | Separate tables for first_name, last_name | Store directly in users table |
| Missing FK | `user_id INTEGER` (no FK) | `user_id INTEGER REFERENCES users(id)` |
| Wrong index order | `INDEX(created_at, user_id)` for `WHERE user_id=? AND created_at>?` | `INDEX(user_id, created_at)` |
| CSV in column | `tags TEXT -- "a,b,c"` | Junction table with proper FK |

---

## 11. Pre-Implementation Checklist

### Phase 1: Before Writing Code
- [ ] Query patterns identified and documented
- [ ] Performance requirements defined (latency, throughput)
- [ ] Data volume estimates calculated
- [ ] Test fixtures designed for schema validation
- [ ] Migration strategy planned (if modifying existing schema)
- [ ] Reference files read (`references/advanced-patterns.md`, `references/security-examples.md`)

### Phase 2: During Implementation
- [ ] All tables have PRIMARY KEY
- [ ] Foreign keys defined for all relationships
- [ ] Appropriate ON DELETE actions (CASCADE, RESTRICT, SET NULL)
- [ ] CHECK constraints for data validation
- [ ] UNIQUE constraints where needed
- [ ] NOT NULL for required fields
- [ ] Indexes created for all foreign keys
- [ ] Composite indexes with correct column order (equality before range)
- [ ] FTS5 tables with sync triggers if needed
- [ ] Tests written and passing for constraints

### Phase 3: Before Committing
- [ ] `pytest tests/test_schema.py -v` passes
- [ ] EXPLAIN QUERY PLAN verified for critical queries
- [ ] No redundant indexes
- [ ] Migrations tested with rollback
- [ ] No data loss in migrations
- [ ] Performance benchmarks meet requirements
- [ ] Schema version tracked

---

## 12. Summary

Your goal is to create database schemas that are:

- **Normalized**: Eliminate redundancy while allowing strategic denormalization
- **Performant**: Proper indexing, covering indexes, efficient query patterns
- **Maintainable**: Clear naming, documented relationships, migration-friendly
- **Secure**: Constraints for validation, foreign keys for integrity

You understand that schema design requires balancing:
1. Normalization vs. query performance
2. Indexing benefits vs. write overhead
3. Flexibility vs. constraints
4. Current needs vs. future evolution

**Design Reminder**: Start with 3NF normalization, add indexes based on actual query pat## 9. Performance Patterns

**Good: Composite index with correct column order**
```sql
-- Query: WHERE user_id = ? AND created_at > ? ORDER BY created_at DESC
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at DESC);
```

📚 **For complete details**: See `references/performance-patterns.md`

---
