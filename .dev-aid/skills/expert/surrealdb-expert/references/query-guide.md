# SurrealDB Query Guide

## 1. Basic Queries

### SELECT Queries

```surreal
-- Select all records from table
SELECT * FROM user;

-- Select specific fields
SELECT id, email, name FROM user;

-- Select with WHERE clause
SELECT * FROM user WHERE active = true;

-- Select with multiple conditions
SELECT * FROM user WHERE active = true AND role = 'admin';

-- Select with OR conditions
SELECT * FROM user WHERE role = 'admin' OR role = 'moderator';
```

### CREATE Queries

```surreal
-- Create with auto-generated ID
CREATE user CONTENT {
    email: 'user@example.com',
    name: 'John Doe',
    created_at: time::now()
};

-- Create with specific ID
CREATE user:john CONTENT {
    email: 'john@example.com',
    name: 'John Doe'
};

-- Create multiple records
CREATE user CONTENT { email: 'user1@example.com' };
CREATE user CONTENT { email: 'user2@example.com' };
CREATE user CONTENT { email: 'user3@example.com' };
```

### UPDATE Queries

```surreal
-- Update specific record
UPDATE user:john SET active = true;

-- Update with MERGE (partial update)
UPDATE user:john MERGE {
    last_login: time::now(),
    login_count += 1
};

-- Update with CONTENT (full replace)
UPDATE user:john CONTENT {
    email: 'john@example.com',
    name: 'John Doe',
    active: true
};

-- Update multiple records with WHERE
UPDATE user SET active = false WHERE last_login < time::now() - 30d;
```

### DELETE Queries

```surreal
-- Delete specific record
DELETE user:john;

-- Delete with WHERE clause
DELETE user WHERE active = false AND created_at < time::now() - 1y;

-- Delete all records from table (be careful!)
DELETE user;
```

---

## 2. Parameterized Queries

Always use parameters for user input to prevent injection attacks:

```surreal
-- ✅ SAFE: Using parameters
LET $email = "user@example.com";
SELECT * FROM user WHERE email = $email;

-- With SDK (JavaScript)
const result = await db.query(
    'SELECT * FROM user WHERE email = $email',
    { email: 'user@example.com' }
);

-- ✅ SAFE: Creating with parameters
await db.query(
    `CREATE user CONTENT {
        email: $email,
        password: crypto::argon2::generate($password),
        name: $name
    }`,
    {
        email: 'user@example.com',
        password: 'secret123',
        name: 'John Doe'
    }
);

-- ❌ UNSAFE: String concatenation (NEVER DO THIS!)
const email = userInput;
const query = `SELECT * FROM user WHERE email = "${email}"`;  // VULNERABLE!
```

---

## 3. Graph Traversal Queries

### Basic Graph Operations

```surreal
-- Create graph relationship
RELATE user:john->authored->post:123;

-- Traverse outbound (->)
SELECT ->authored->post.* FROM user:john;

-- Traverse inbound (<-)
SELECT <-authored<-user.* FROM post:123;

-- Bidirectional traversal
SELECT
    ->follows->user.name AS following,
    <-follows<-user.name AS followers
FROM user:john;
```

### Advanced Graph Traversal

```surreal
-- Multi-hop traversal
SELECT ->authored->post->commented->comment.* FROM user:john;

-- Traversal with filtering
SELECT ->authored->post[WHERE published = true].* FROM user:john;

-- Limit traversal results
SELECT ->follows->user[0:10].name FROM user:john;  -- Max 10 results

-- Traversal with conditions and limits
SELECT ->authored->post[WHERE published = true AND created_at > $date][0:20].*
FROM user:john;
```

### Graph Aggregation

```surreal
-- Count relationships
SELECT
    count(->authored->post) AS post_count,
    count(<-follows<-user) AS follower_count,
    count(->follows->user) AS following_count
FROM user:john;

-- Aggregate during traversal
SELECT
    ->authored->post.title,
    math::sum(->authored->post.views) AS total_views
FROM user:john;
```

---

## 4. Advanced Query Patterns

### Pagination

```surreal
-- Offset-based pagination (simple but not recommended for large datasets)
SELECT * FROM post ORDER BY created_at DESC START 0 LIMIT 20;
SELECT * FROM post ORDER BY created_at DESC START 20 LIMIT 20;

-- Cursor-based pagination (recommended)
SELECT * FROM post
    WHERE created_at < $cursor
    ORDER BY created_at DESC
    LIMIT 20;
```

### Sorting

```surreal
-- Sort ascending
SELECT * FROM post ORDER BY created_at ASC;

-- Sort descending
SELECT * FROM post ORDER BY created_at DESC;

-- Multi-column sort
SELECT * FROM post ORDER BY category ASC, created_at DESC;
```

### Filtering

```surreal
-- Equality
SELECT * FROM user WHERE role = 'admin';

-- Comparison operators
SELECT * FROM product WHERE price > 100;
SELECT * FROM product WHERE price >= 100 AND price <= 1000;

-- IN operator
SELECT * FROM user WHERE role IN ['admin', 'moderator'];

-- String operations
SELECT * FROM user WHERE string::lowercase(email) CONTAINS '@example.com';

-- Date/time filtering
SELECT * FROM post WHERE created_at > time::now() - 7d;
SELECT * FROM post WHERE created_at BETWEEN '2024-01-01' AND '2024-12-31';
```

### Aggregation

```surreal
-- Count
SELECT count() FROM user;
SELECT count() FROM user WHERE active = true;

-- Group by
SELECT category, count() AS count FROM product GROUP BY category;

-- Multiple aggregations
SELECT
    category,
    count() AS count,
    math::sum(price) AS total,
    math::avg(price) AS average,
    math::max(price) AS max_price,
    math::min(price) AS min_price
FROM product
GROUP BY category;
```

---

## 5. Full-Text Search

```surreal
-- Define search index
DEFINE INDEX search_idx ON TABLE article
    COLUMNS title, content
    SEARCH ANALYZER simple BM25;

-- Search queries
SELECT * FROM article WHERE title @@ 'database';
SELECT * FROM article WHERE content @@ 'performance optimization';

-- Search with multiple terms
SELECT * FROM article
    WHERE title @@ 'database' OR content @@ 'database'
    ORDER BY relevance DESC;
```

---

## 6. Transactions

```surreal
-- Begin transaction
BEGIN TRANSACTION;

-- Execute multiple operations
CREATE user:john CONTENT { email: 'john@example.com', balance: 1000 };
CREATE user:jane CONTENT { email: 'jane@example.com', balance: 500 };

-- Transfer money
UPDATE user:john SET balance -= 100;
UPDATE user:jane SET balance += 100;

-- Commit if all succeed
COMMIT TRANSACTION;

-- Or rollback on error
CANCEL TRANSACTION;
```

---

## 7. FETCH for Eager Loading

```surreal
-- Basic FETCH (avoid N+1 queries)
SELECT * FROM user FETCH ->authored->post;

-- Multiple FETCH
SELECT * FROM user
    FETCH ->authored->post,
          ->follows->user;

-- Nested FETCH
SELECT * FROM user
    FETCH ->authored->post->commented->comment;
```

---

## 8. Subqueries

```surreal
-- Subquery in WHERE
SELECT * FROM post
    WHERE author IN (SELECT id FROM user WHERE role = 'admin');

-- Subquery in SELECT
SELECT
    *,
    (SELECT count() FROM post WHERE author = $parent.id) AS post_count
FROM user;
```

---

## 9. LET Variables

```surreal
-- Define variables
LET $admin_role = 'admin';
LET $recent_date = time::now() - 7d;

-- Use in queries
SELECT * FROM user WHERE role = $admin_role;
SELECT * FROM post WHERE created_at > $recent_date;

-- Complex variable
LET $active_admins = (SELECT id FROM user WHERE role = 'admin' AND active = true);
SELECT * FROM audit_log WHERE user IN $active_admins;
```

---

## 10. Functions

### String Functions

```surreal
-- Lowercase/uppercase
SELECT string::lowercase(email) FROM user;
SELECT string::uppercase(name) FROM user;

-- String length
SELECT * FROM user WHERE string::length(name) > 10;

-- Concatenation
SELECT string::concat(first_name, ' ', last_name) AS full_name FROM user;

-- Validation
SELECT * FROM user WHERE string::is::email(email);
```

### Math Functions

```surreal
-- Aggregations
SELECT math::sum(price) FROM product;
SELECT math::avg(price) FROM product;
SELECT math::max(price) FROM product;
SELECT math::min(price) FROM product;

-- Calculations
SELECT price, math::round(price * 1.1, 2) AS price_with_tax FROM product;
SELECT math::abs(balance) FROM account;
```

### Time Functions

```surreal
-- Current time
SELECT time::now();

-- Time arithmetic
SELECT time::now() - 7d AS week_ago;
SELECT time::now() + 1h AS in_one_hour;

-- Format time
SELECT time::format(created_at, '%Y-%m-%d') FROM post;

-- Extract components
SELECT
    time::year(created_at) AS year,
    time::month(created_at) AS month,
    time::day(created_at) AS day
FROM post;
```

### Crypto Functions

```surreal
-- Password hashing
SELECT crypto::argon2::generate('password123');
SELECT crypto::bcrypt::generate('password123');

-- Password verification
SELECT crypto::argon2::compare(password, 'password123') FROM user WHERE email = $email;

-- UUID generation
SELECT rand::uuid();
```

---

## 11. Schema Definition Queries

### Table Definition

```surreal
-- Define table
DEFINE TABLE user SCHEMAFULL;

-- With permissions
DEFINE TABLE user SCHEMAFULL
    PERMISSIONS
        FOR select WHERE id = $auth.id
        FOR create, update, delete WHERE $auth.role = 'admin';
```

### Field Definition

```surreal
-- Basic field
DEFINE FIELD email ON TABLE user TYPE string;

-- With validation
DEFINE FIELD email ON TABLE user TYPE string
    ASSERT string::is::email($value);

-- With default value
DEFINE FIELD created_at ON TABLE user TYPE datetime
    DEFAULT time::now();

-- With auto-generation (password hash)
DEFINE FIELD password ON TABLE user TYPE string
    VALUE crypto::argon2::generate($value);

-- Enum-like validation
DEFINE FIELD role ON TABLE user TYPE string
    DEFAULT 'user'
    ASSERT $value IN ['user', 'admin', 'moderator'];
```

### Index Definition

```surreal
-- Simple index
DEFINE INDEX email_idx ON TABLE user COLUMNS email;

-- Unique index
DEFINE INDEX email_idx ON TABLE user COLUMNS email UNIQUE;

-- Composite index
DEFINE INDEX user_status_idx ON TABLE order COLUMNS user_id, status;

-- Search index
DEFINE INDEX search_idx ON TABLE article
    COLUMNS title, content
    SEARCH ANALYZER simple BM25;
```

---

## 12. LIVE Queries (Real-Time)

```javascript
// Subscribe to table changes
const queryUuid = await db.live(
    'user',
    (action, result) => {
        console.log(`Action: ${action}`);  // CREATE, UPDATE, or DELETE
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

// With filtering
const queryUuid = await db.query(`
    LIVE SELECT * FROM post
    WHERE author = $auth.id OR public = true;
`);

// Cleanup (IMPORTANT!)
await db.kill(queryUuid);
```

---

## 13. Common Query Patterns

### Find or Create

```surreal
-- Check if exists, create if not
LET $user = (SELECT * FROM user WHERE email = $email LIMIT 1);
IF !$user {
    CREATE user CONTENT { email: $email, name: $name };
} ELSE {
    RETURN $user;
};
```

### Upsert (Update or Insert)

```surreal
-- Update if exists, create if not
UPDATE user:john CONTENT {
    email: 'john@example.com',
    name: 'John Doe',
    updated_at: time::now()
} RETURN AFTER;
```

### Conditional Update

```surreal
-- Update only if condition met
UPDATE user:john SET balance -= $amount
    WHERE balance >= $amount
    RETURN BEFORE, AFTER;
```

### Soft Delete

```surreal
-- Mark as deleted instead of removing
UPDATE user:john SET deleted = true, deleted_at = time::now();

-- Query active records
SELECT * FROM user WHERE deleted != true;
```

---

## 14. Testing Queries

### Explain Query Plan

```surreal
-- Show query execution plan
EXPLAIN SELECT * FROM user WHERE email = $email;
```

### Info Commands

```surreal
-- Show database info
INFO FOR DB;

-- Show table info
INFO FOR TABLE user;

-- Show namespace info
INFO FOR NS;
```

---

## 15. Quick Reference

### Most Common Patterns

```surreal
-- Parameterized select
SELECT * FROM user WHERE email = $email;

-- Create with hash
CREATE user CONTENT {
    email: $email,
    password: crypto::argon2::generate($password)
};

-- Update specific fields
UPDATE user:john MERGE { last_login: time::now() };

-- Graph traversal
SELECT ->authored->post.* FROM user:john;

-- Pagination
SELECT * FROM post ORDER BY created_at DESC LIMIT 20;

-- Count
SELECT count() FROM user WHERE active = true;

-- Transaction
BEGIN TRANSACTION;
-- operations
COMMIT TRANSACTION;
```

### Performance Tips

1. Always use indexes on queried fields
2. Use parameterized queries ($variables)
3. Limit result sets with LIMIT
4. Use FETCH to avoid N+1 queries
5. Filter early in graph traversals
6. Select only needed fields (avoid SELECT *)
7. Use connection pooling
8. Batch operations in transactions
