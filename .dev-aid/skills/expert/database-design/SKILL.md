---
name: database-design
version: 2.0.0
description: "Database schema design with normalization, indexing strategies, full-text search, and migration patterns."
risk_level: HIGH
---

# Database Design Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-89: SQL Injection**
- NEVER: String concatenation in queries
- ALWAYS: Parameterized queries, ORM methods, prepared statements

**CWE-312: Cleartext Storage of Sensitive Data**
- NEVER: Store passwords, tokens, PII in plaintext
- ALWAYS: Hash passwords (bcrypt/argon2), encrypt PII, use column encryption

**CWE-732: Insecure Permissions**
- NEVER: Application user with admin/superuser privileges
- ALWAYS: Principle of least privilege, separate read/write users

**CWE-209: Error Message Information Leak**
- NEVER: Return database errors to client
- ALWAYS: Log details server-side, return generic error to client

### 0.3 Risk Level: HIGH

**Verification requirements for HIGH risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 SQL Injection Prevention (CWE-89)

**Principle:** Never concatenate user input into SQL. Always use parameterized queries.

```sql
-- ❌ WRONG - String concatenation
EXECUTE 'SELECT * FROM users WHERE name = ''' || user_input || '''';

-- ❌ WRONG - Format strings
cursor.execute(f"SELECT * FROM users WHERE name = '{name}'")

-- ✅ CORRECT - Parameterized queries
-- PostgreSQL
SELECT * FROM users WHERE name = $1;

-- MySQL
SELECT * FROM users WHERE name = ?;

-- Python
cursor.execute("SELECT * FROM users WHERE name = %s", (name,))
```

### 1.2 Data Validation at Schema Level (CWE-20)

**Principle:** Enforce constraints in the database. Don't rely solely on application validation.

```sql
-- ❌ WRONG - No constraints
CREATE TABLE users (
    email TEXT,
    age INTEGER,
    status TEXT
);

-- ✅ CORRECT - Constraints enforced
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE
        CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    age INTEGER CHECK (age >= 0 AND age <= 150),
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'inactive', 'pending')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### 1.3 Secrets ≠ Code (CWE-798)

**Principle:** Connection strings from environment. Never hardcode credentials.

### 1.4 Least Privilege (CWE-250)

**Principle:** Application user gets minimum permissions. Never use superuser.

```sql
-- ❌ WRONG - Application uses superuser
GRANT ALL ON ALL TABLES TO app_user;

-- ✅ CORRECT - Minimum required permissions
CREATE ROLE app_readonly;
GRANT SELECT ON users, orders, products TO app_readonly;

CREATE ROLE app_writer;
GRANT SELECT, INSERT, UPDATE ON users, orders TO app_writer;
GRANT SELECT ON products TO app_writer;

-- No DELETE, no TRUNCATE, no DDL
```

### 1.5 Fail Secure (CWE-636)

**Principle:** Transactions fail completely or succeed completely.

### 1.6 Defense in Depth

**Principle:** Application validation + database constraints + row-level security.

---

## 2. Version Requirements

**ALWAYS use these minimum versions:**

```
PostgreSQL >= 15.0
MySQL >= 8.0
SQLite >= 3.44.0 (for JSON and FTS5)
```

---

## 3. Code Patterns

### 3.1 WHEN designing normalized schema

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE
        CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    password_hash TEXT NOT NULL,  -- Never store plaintext!
    name TEXT NOT NULL CHECK (length(name) BETWEEN 1 AND 100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Organizations (1:N with users)
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL CHECK (length(name) BETWEEN 1 AND 200),
    slug TEXT NOT NULL UNIQUE CHECK (slug ~* '^[a-z0-9-]+$'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Organization membership (N:N)
CREATE TABLE organization_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role TEXT NOT NULL DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member')),
    joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (organization_id, user_id)
);

-- Index for common queries
CREATE INDEX idx_org_members_user ON organization_members(user_id);
CREATE INDEX idx_org_members_org ON organization_members(organization_id);
```

### 3.2 WHEN implementing soft deletes

```sql
-- Add soft delete columns
ALTER TABLE users ADD COLUMN deleted_at TIMESTAMPTZ;

-- Create view for active records
CREATE VIEW active_users AS
SELECT * FROM users WHERE deleted_at IS NULL;

-- Partial index for efficient queries
CREATE INDEX idx_users_active ON users(id) WHERE deleted_at IS NULL;

-- Soft delete function
CREATE OR REPLACE FUNCTION soft_delete()
RETURNS TRIGGER AS $$
BEGIN
    NEW.deleted_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Application query pattern
SELECT * FROM users
WHERE deleted_at IS NULL
  AND id = $1;

-- Soft delete instead of DELETE
UPDATE users SET deleted_at = NOW() WHERE id = $1;
```

### 3.3 WHEN implementing full-text search

```sql
-- PostgreSQL FTS
ALTER TABLE articles ADD COLUMN search_vector tsvector;

-- Update search vector on insert/update
CREATE OR REPLACE FUNCTION update_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector = to_tsvector('english',
        coalesce(NEW.title, '') || ' ' ||
        coalesce(NEW.body, '')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER articles_search_update
    BEFORE INSERT OR UPDATE ON articles
    FOR EACH ROW EXECUTE FUNCTION update_search_vector();

-- GIN index for fast search
CREATE INDEX idx_articles_search ON articles USING GIN(search_vector);

-- Search query
SELECT id, title,
       ts_rank(search_vector, query) AS rank
FROM articles,
     to_tsquery('english', $1) query
WHERE search_vector @@ query
ORDER BY rank DESC
LIMIT 20;
```

### 3.4 WHEN implementing audit logging

```sql
-- Audit log table
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    record_id UUID NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
    old_data JSONB,
    new_data JSONB,
    user_id UUID,
    ip_address INET,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Partition by month for performance
CREATE TABLE audit_log_y2024m01 PARTITION OF audit_log
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Generic audit trigger
CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
DECLARE
    old_data JSONB;
    new_data JSONB;
BEGIN
    IF TG_OP = 'DELETE' THEN
        old_data = to_jsonb(OLD);
        new_data = NULL;
    ELSIF TG_OP = 'UPDATE' THEN
        old_data = to_jsonb(OLD);
        new_data = to_jsonb(NEW);
    ELSIF TG_OP = 'INSERT' THEN
        old_data = NULL;
        new_data = to_jsonb(NEW);
    END IF;

    INSERT INTO audit_log (table_name, record_id, action, old_data, new_data, user_id)
    VALUES (TG_TABLE_NAME, COALESCE(NEW.id, OLD.id), TG_OP, old_data, new_data,
            current_setting('app.current_user_id', true)::UUID);

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Apply to tables
CREATE TRIGGER audit_users
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION audit_trigger();
```

### 3.5 WHEN implementing row-level security

```sql
-- Enable RLS
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Policy: users can only see their own documents
CREATE POLICY documents_select ON documents
    FOR SELECT
    USING (owner_id = current_setting('app.current_user_id')::UUID);

-- Policy: users can only update their own documents
CREATE POLICY documents_update ON documents
    FOR UPDATE
    USING (owner_id = current_setting('app.current_user_id')::UUID)
    WITH CHECK (owner_id = current_setting('app.current_user_id')::UUID);

-- Policy: admins can see all documents
CREATE POLICY documents_admin ON documents
    FOR ALL
    USING (current_setting('app.current_role') = 'admin');

-- Set user context before queries (in application)
SELECT set_config('app.current_user_id', $1::TEXT, true);
SELECT set_config('app.current_role', $2, true);
```

### 3.6 WHEN designing for performance

```sql
-- Proper indexing
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at DESC);
CREATE INDEX idx_orders_status ON orders(status) WHERE status = 'pending';

-- Covering index (includes all needed columns)
CREATE INDEX idx_users_email_name ON users(email) INCLUDE (name);

-- Composite index for common filters
CREATE INDEX idx_products_category_price ON products(category_id, price)
    WHERE deleted_at IS NULL;

-- Use EXPLAIN ANALYZE
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT * FROM orders
WHERE user_id = $1 AND created_at > NOW() - INTERVAL '30 days';
```

### 3.7 WHEN implementing migrations

```sql
-- Migration: 001_create_users.sql
-- Up
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Down
DROP TABLE users;

-- Migration: 002_add_user_name.sql
-- Up
ALTER TABLE users ADD COLUMN name TEXT;

-- Backfill with default
UPDATE users SET name = split_part(email, '@', 1) WHERE name IS NULL;

-- Add constraint after backfill
ALTER TABLE users ALTER COLUMN name SET NOT NULL;
ALTER TABLE users ADD CONSTRAINT users_name_length CHECK (length(name) BETWEEN 1 AND 100);

-- Down
ALTER TABLE users DROP CONSTRAINT users_name_length;
ALTER TABLE users DROP COLUMN name;
```

---

## 4. Anti-Patterns

**NEVER:**
- Concatenate user input into SQL strings
- Store passwords in plaintext
- Use database superuser for application
- Skip foreign key constraints
- Create tables without primary keys
- Store sensitive data without encryption
- Skip database-level validation
- Use SELECT * in production code

---

## 5. Testing

**ALWAYS write database tests:**

```python
import pytest
from sqlalchemy import create_engine, text

@pytest.fixture
def db():
    engine = create_engine("postgresql://test@localhost/test_db")
    with engine.connect() as conn:
        conn.execute(text("BEGIN"))
        yield conn
        conn.execute(text("ROLLBACK"))

def test_email_constraint(db):
    """Verify email format is enforced."""
    with pytest.raises(Exception) as exc:
        db.execute(text(
            "INSERT INTO users (email, name) VALUES ('invalid', 'Test')"
        ))
    assert "violates check constraint" in str(exc.value)

def test_unique_email(db):
    """Verify email uniqueness."""
    db.execute(text(
        "INSERT INTO users (email, name) VALUES ('test@example.com', 'Test')"
    ))
    with pytest.raises(Exception) as exc:
        db.execute(text(
            "INSERT INTO users (email, name) VALUES ('test@example.com', 'Test2')"
        ))
    assert "unique" in str(exc.value).lower()

def test_cascade_delete(db):
    """Verify cascade delete works."""
    db.execute(text(
        "INSERT INTO organizations (id, name, slug) VALUES ('org-1', 'Org', 'org')"
    ))
    db.execute(text(
        "INSERT INTO organization_members (organization_id, user_id) "
        "VALUES ('org-1', 'user-1')"
    ))

    db.execute(text("DELETE FROM organizations WHERE id = 'org-1'"))

    result = db.execute(text(
        "SELECT COUNT(*) FROM organization_members WHERE organization_id = 'org-1'"
    ))
    assert result.scalar() == 0
```

---

## 6. Pre-Generation Checklist

**BEFORE generating any database code:**

- [ ] All tables have primary keys (prefer UUID)
- [ ] Foreign keys with appropriate ON DELETE behavior
- [ ] CHECK constraints for data validation
- [ ] NOT NULL where appropriate (explicit about nullability)
- [ ] Indexes for common query patterns
- [ ] Parameterized queries only (no string concatenation)
- [ ] Timestamps with timezone (TIMESTAMPTZ)
- [ ] Application user has minimum permissions
- [ ] Sensitive data encrypted or hashed
- [ ] Audit logging for sensitive tables
