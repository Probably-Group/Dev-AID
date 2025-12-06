## 5. Core Patterns

### Pattern 1: Secure Table Definition with Row-Level Security

```surreal
-- ✅ SECURE: Explicit permissions with row-level security
DEFINE TABLE user SCHEMAFULL
    PERMISSIONS
        FOR select, update, delete WHERE id = $auth.id
        FOR create WHERE $auth.role = 'admin';

DEFINE FIELD email ON TABLE user TYPE string ASSERT string::is::email($value);
DEFINE FIELD password ON TABLE user TYPE string VALUE crypto::argon2::generate($value);
DEFINE FIELD role ON TABLE user TYPE string DEFAULT 'user' ASSERT $value IN ['user', 'admin'];
DEFINE FIELD created ON TABLE user TYPE datetime DEFAULT time::now();

DEFINE INDEX unique_email ON TABLE user COLUMNS email UNIQUE;

-- ❌ UNSAFE: No permissions defined (relies on default)
DEFINE TABLE user SCHEMAFULL;
DEFINE FIELD password ON TABLE user TYPE string; -- Not hashed!
```

---

### Pattern 2: Parameterized Queries for Injection Prevention

```surreal
-- ✅ SAFE: Parameterized query
LET $user_email = "user@example.com";
SELECT * FROM user WHERE email = $user_email;

-- With SDK (JavaScript)
const email = req.body.email;
const result = await db.query(
    'SELECT * FROM user WHERE email = $email',
    { email }
);

-- ❌ UNSAFE: String concatenation (NEVER DO THIS)
const query = `SELECT * FROM user WHERE email = "${userInput}"`;
```

---

### Pattern 3: Indexing for Performance

```surreal
-- ✅ Good: Index on frequently queried fields
DEFINE INDEX email_idx ON TABLE user COLUMNS email UNIQUE;
DEFINE INDEX created_idx ON TABLE post COLUMNS created_at;
DEFINE INDEX composite_idx ON TABLE order COLUMNS user_id, status;

-- ✅ Good: Full-text search index
DEFINE INDEX search_idx ON TABLE article
    COLUMNS title, content
    SEARCH ANALYZER simple BM25;

-- Query using search index
SELECT * FROM article WHERE title @@ 'database' OR content @@ 'performance';
```

---

### Pattern 4: Graph Traversal Optimization

```surreal
-- ✅ Good: Single query with graph traversal (avoids N+1)
SELECT
    *,
    ->authored->post.* AS posts,
    ->follows->user.name AS following
FROM user:john;

-- ✅ Good: Use FETCH for eager loading
SELECT * FROM user FETCH ->authored->post, ->follows->user;

-- ✅ Good: Limit traversal depth
SELECT ->follows->user[0:10].name FROM user:john;

-- ❌ Bad: N+1 query pattern
LET $users = SELECT * FROM user;
FOR $user IN $users {
    SELECT * FROM post WHERE author = $user.id;
};
```

---

