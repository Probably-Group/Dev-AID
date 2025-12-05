# SurrealDB Anti-Patterns

## 1. Security Anti-Patterns

### Anti-Pattern 1: No Permissions Defined

**Problem**: Relying on default permissions instead of explicit definitions.

**Bad Example**:
```surreal
-- ❌ DON'T: No permissions (relies on defaults)
DEFINE TABLE sensitive SCHEMAFULL;
```

**Better Approach**:
```surreal
-- ✅ DO: Explicit permissions
DEFINE TABLE sensitive SCHEMAFULL
    PERMISSIONS
        FOR select WHERE $auth.id != NONE
        FOR create, update, delete WHERE $auth.role = 'admin';
```

**Why Better**: Explicit permissions make security model clear and prevent accidental data exposure. Defaults may change between versions.

---

### Anti-Pattern 2: String Interpolation in Queries

**Problem**: Building queries with string concatenation/interpolation instead of parameters.

**Bad Example**:
```javascript
// ❌ DON'T: String interpolation
const email = userInput;
await db.query(`SELECT * FROM user WHERE email = "${email}"`);
```

**Better Approach**:
```javascript
// ✅ DO: Parameterized queries
const email = userInput;
await db.query('SELECT * FROM user WHERE email = $email', { email });
```

**Why Better**: Prevents injection attacks. User input could contain malicious SurrealQL that would be executed with string interpolation.

---

### Anti-Pattern 3: Storing Plain Text Passwords

**Problem**: Not hashing passwords before storage.

**Bad Example**:
```surreal
-- ❌ DON'T: Plain text
CREATE user CONTENT {
    email: $email,
    password: $password  -- Stored as plain text!
};
```

**Better Approach**:
```surreal
-- ✅ DO: Hash passwords
CREATE user CONTENT {
    email: $email,
    password: crypto::argon2::generate($password)
};

-- OR use VALUE in field definition
DEFINE FIELD password ON TABLE user TYPE string
    VALUE crypto::argon2::generate($value);
```

**Why Better**: If database is compromised, passwords remain secure. Use argon2, bcrypt, or pbkdf2 for hashing.

---

### Anti-Pattern 4: Not Cleaning Up LIVE Queries

**Problem**: Creating LIVE query subscriptions without cleanup handlers.

**Bad Example**:
```javascript
// ❌ DON'T: Memory leak
async function subscribe() {
    const uuid = await db.live('user', callback);
    // Never killed - memory leak!
}
```

**Better Approach**:
```javascript
// ✅ DO: Clean up subscriptions
const uuid = await db.live('user', callback);

// On component unmount or connection close:
await db.kill(uuid);
await db.close();

// OR use cleanup function
function setupSubscription() {
    let uuid;

    async function start() {
        uuid = await db.live('user', callback);
    }

    async function cleanup() {
        if (uuid) await db.kill(uuid);
    }

    return { start, cleanup };
}
```

**Why Better**: Prevents memory leaks and unnecessary database load from abandoned subscriptions.

---

### Anti-Pattern 5: Overly Permissive RBAC

**Problem**: Granting excessive privileges to users.

**Bad Example**:
```surreal
-- ❌ DON'T: Everyone is OWNER
DEFINE USER dev ON ROOT PASSWORD 'weak' ROLES OWNER;
DEFINE USER intern ON ROOT PASSWORD 'weak' ROLES OWNER;
```

**Better Approach**:
```surreal
-- ✅ DO: Least privilege principle
DEFINE USER dev ON DATABASE app PASSWORD 'strong' ROLES EDITOR;
DEFINE USER intern ON DATABASE app PASSWORD 'strong' ROLES VIEWER;
DEFINE USER admin ON ROOT PASSWORD 'very_strong' ROLES OWNER;
```

**Why Better**: Limits blast radius of compromised credentials. Follow principle of least privilege.

---

## 2. Performance Anti-Patterns

### Anti-Pattern 6: Missing Indexes on Queried Fields

**Problem**: Querying fields without indexes causes full table scans.

**Bad Example**:
```surreal
-- ❌ DON'T: Query without index
DEFINE TABLE user SCHEMAFULL;
DEFINE FIELD email ON TABLE user TYPE string;

SELECT * FROM user WHERE email = $email; -- Slow full table scan!
```

**Better Approach**:
```surreal
-- ✅ DO: Create index first
DEFINE TABLE user SCHEMAFULL;
DEFINE FIELD email ON TABLE user TYPE string;
DEFINE INDEX email_idx ON TABLE user COLUMNS email UNIQUE;

SELECT * FROM user WHERE email = $email; -- Fast indexed lookup!
```

**Why Better**: Indexes dramatically improve query performance. For 1M rows, index can reduce query time from seconds to milliseconds.

---

### Anti-Pattern 7: N+1 Query Pattern

**Problem**: Fetching related data in a loop instead of using graph traversal.

**Bad Example**:
```surreal
-- ❌ DON'T: Multiple queries (N+1 problem)
LET $users = SELECT * FROM user;
FOR $user IN $users {
    SELECT * FROM post WHERE author = $user.id;  -- N additional queries!
};
```

**Better Approach**:
```surreal
-- ✅ DO: Single query with graph traversal
SELECT *, ->authored->post.* FROM user;

-- ✅ OR: Use FETCH
SELECT * FROM user FETCH ->authored->post;
```

**Why Better**: Single query is much faster than N+1 queries. For 100 users, reduces from 101 queries to 1 query.

---

### Anti-Pattern 8: Creating New Connection Per Request

**Problem**: Creating a new database connection for every request.

**Bad Example**:
```python
# ❌ DON'T: New connection per request
async def get_user(user_id: str):
    db = Surreal("ws://localhost:8000/rpc")
    await db.connect()  # Expensive connection overhead!
    await db.use("app", "production")
    await db.signin({"user": "admin", "pass": "secure"})

    result = await db.query("SELECT * FROM user WHERE id = $id", {"id": user_id})

    await db.close()
    return result
```

**Better Approach**:
```python
# ✅ DO: Use connection pool
pool = SurrealDBPool("ws://localhost:8000/rpc", "app", "production", pool_size=20)
await pool.initialize({"user": "admin", "pass": "secure"})

async def get_user(user_id: str):
    async with pool.connection() as db:
        result = await db.query("SELECT * FROM user WHERE id = $id", {"id": user_id})
        return result
```

**Why Better**: Connection pooling reuses connections, dramatically reducing overhead. Can improve throughput by 10-100x.

---

### Anti-Pattern 9: Selecting All Fields

**Problem**: Using SELECT * when only few fields are needed.

**Bad Example**:
```surreal
-- ❌ DON'T: Select all fields
SELECT * FROM user;  -- Returns password hash, metadata, all fields!
```

**Better Approach**:
```surreal
-- ✅ DO: Select only needed fields
SELECT id, email, name FROM user WHERE active = true;
```

**Why Better**: Reduces data transfer, improves query performance, and prevents accidental exposure of sensitive fields.

---

### Anti-Pattern 10: Unlimited Graph Traversal Depth

**Problem**: Graph traversals without depth limits can cause runaway queries.

**Bad Example**:
```surreal
-- ❌ DON'T: Unlimited depth
SELECT ->follows->user->follows->user->follows->user.* FROM user:john;
```

**Better Approach**:
```surreal
-- ✅ DO: Limit traversal depth and results
SELECT ->follows->user[0:10].name FROM user:john;

-- ✅ DO: Limit with filtering
SELECT ->follows->user[WHERE active = true][0:20].* FROM user:john;
```

**Why Better**: Prevents exponential query growth. A user with 100 followers, each with 100 followers, would result in 1,000,000+ records without limits.

---

## 3. Schema Design Anti-Patterns

### Anti-Pattern 11: Using SCHEMALESS for Critical Data

**Problem**: Not enforcing schema on important data.

**Bad Example**:
```surreal
-- ❌ DON'T: Schemaless for critical data
DEFINE TABLE payment SCHEMALESS;

-- Allows inconsistent data
CREATE payment CONTENT { amount: "invalid" };  -- String instead of number!
CREATE payment CONTENT { amont: 100 };  -- Typo in field name!
```

**Better Approach**:
```surreal
-- ✅ DO: Use SCHEMAFULL with validation
DEFINE TABLE payment SCHEMAFULL;
DEFINE FIELD amount ON TABLE payment TYPE decimal ASSERT $value > 0;
DEFINE FIELD currency ON TABLE payment TYPE string ASSERT $value IN ['USD', 'EUR', 'GBP'];
DEFINE FIELD user_id ON TABLE payment TYPE record<user>;
DEFINE FIELD created_at ON TABLE payment TYPE datetime DEFAULT time::now();

-- This will fail validation
CREATE payment CONTENT { amount: "invalid" };  -- ❌ Type error
CREATE payment CONTENT { amount: -10 };  -- ❌ Assertion failed
```

**Why Better**: SCHEMAFULL ensures data integrity and catches errors early. Critical for financial, medical, or security data.

---

### Anti-Pattern 12: No Validation on User Input

**Problem**: Accepting user input without ASSERT validation.

**Bad Example**:
```surreal
-- ❌ DON'T: No validation
DEFINE FIELD email ON TABLE user TYPE string;
DEFINE FIELD age ON TABLE user TYPE int;

-- Allows invalid data
CREATE user CONTENT { email: "not-an-email", age: -5 };
```

**Better Approach**:
```surreal
-- ✅ DO: Validate with ASSERT
DEFINE FIELD email ON TABLE user TYPE string
    ASSERT string::is::email($value);
DEFINE FIELD age ON TABLE user TYPE int
    ASSERT $value >= 0 AND $value <= 150;

-- This will fail validation
CREATE user CONTENT { email: "not-an-email", age: -5 };  -- ❌ Fails assertions
```

**Why Better**: Prevents invalid data from entering database. Validation at schema level is more reliable than application-level validation.

---

### Anti-Pattern 13: Missing Unique Constraints

**Problem**: Not enforcing uniqueness on fields that should be unique.

**Bad Example**:
```surreal
-- ❌ DON'T: No unique constraint
DEFINE FIELD email ON TABLE user TYPE string;

-- Allows duplicates!
CREATE user CONTENT { email: "user@example.com" };
CREATE user CONTENT { email: "user@example.com" };  -- Duplicate!
```

**Better Approach**:
```surreal
-- ✅ DO: Enforce uniqueness with index
DEFINE FIELD email ON TABLE user TYPE string
    ASSERT string::is::email($value);
DEFINE INDEX unique_email ON TABLE user COLUMNS email UNIQUE;

-- This will fail
CREATE user CONTENT { email: "user@example.com" };
CREATE user CONTENT { email: "user@example.com" };  -- ❌ Unique constraint violation
```

**Why Better**: Prevents duplicate data and ensures data integrity at database level.

---

## 4. Testing Anti-Patterns

### Anti-Pattern 14: No Tests for Database Operations

**Problem**: Implementing database operations without tests.

**Bad Example**:
```python
# ❌ DON'T: No tests
class UserRepository:
    async def create(self, email: str, password: str):
        # No tests for this code!
        return await self.db.query(
            "CREATE user CONTENT { email: $email, password: $password }",
            {"email": email, "password": password}
        )
```

**Better Approach**:
```python
# ✅ DO: Write tests first (TDD)
@pytest.mark.asyncio
async def test_create_user_hashes_password(user_repo):
    """Test that user creation properly hashes passwords."""
    user = await user_repo.create("test@example.com", "secret123")

    assert user["email"] == "test@example.com"
    assert "password" not in user  # Should not return password

    # Verify password is hashed in database
    result = await db.query("SELECT password FROM user WHERE email = $email",
                           {"email": "test@example.com"})
    password_hash = result[0]["result"][0]["password"]
    assert password_hash.startswith("$argon2")  # Hashed with argon2
```

**Why Better**: Tests catch bugs early, document expected behavior, and enable safe refactoring.

---

### Anti-Pattern 15: Not Testing Permissions

**Problem**: Not verifying that row-level security works correctly.

**Bad Example**:
```surreal
-- ❌ DON'T: Define permissions but never test them
DEFINE TABLE document SCHEMAFULL
    PERMISSIONS FOR select WHERE owner = $auth.id;
```

**Better Approach**:
```python
# ✅ DO: Test permissions thoroughly
@pytest.mark.asyncio
async def test_user_cannot_access_other_users_documents():
    """Row-level security should prevent access to other users' documents."""
    # Create two users and documents
    await db.query("""
        CREATE user:alice CONTENT { email: 'alice@test.com' };
        CREATE user:bob CONTENT { email: 'bob@test.com' };
        CREATE document:1 CONTENT { owner: user:alice, content: 'Alice secret' };
        CREATE document:2 CONTENT { owner: user:bob, content: 'Bob secret' };
    """)

    # Sign in as Alice
    alice_db = Surreal("ws://localhost:8000/rpc")
    await alice_db.connect()
    await alice_db.use("test", "test_db")
    # ... signin as Alice ...

    # Alice should only see her document
    result = await alice_db.query("SELECT * FROM document")
    assert len(result[0]["result"]) == 1
    assert result[0]["result"][0]["id"] == "document:1"
```

**Why Better**: Verifies that security model works as expected. Security bugs are critical and must be caught.

---

## 5. Operations Anti-Patterns

### Anti-Pattern 16: Using --allow-all in Production

**Problem**: Allowing unrestricted network access from database.

**Bad Example**:
```bash
# ❌ DON'T: Unrestricted network access
surreal start --allow-all
```

**Better Approach**:
```bash
# ✅ DO: Restrict network access
surreal start \
    --allow-net api.example.com \
    --allow-net cdn.example.com \
    --deny-net 10.0.0.0/8 \
    --deny-net 172.16.0.0/12 \
    --deny-net 192.168.0.0/16
```

**Why Better**: Prevents SSRF attacks where database could be tricked into accessing internal resources or metadata endpoints.

---

### Anti-Pattern 17: Exposing Root Credentials to Clients

**Problem**: Using root/system credentials in client applications.

**Bad Example**:
```javascript
// ❌ DON'T: Root credentials in client
const db = new Surreal();
await db.connect('ws://localhost:8000/rpc');
await db.signin({
    user: 'root',
    pass: 'root'  // ROOT CREDENTIALS IN CLIENT CODE!
});
```

**Better Approach**:
```javascript
// ✅ DO: Use record user authentication with scopes
const db = new Surreal();
await db.connect('ws://localhost:8000/rpc');
await db.use({ ns: 'app', db: 'production' });

// Sign in as record user (scope-based auth)
const token = await db.signin({
    scope: 'user_scope',
    email: 'user@example.com',
    password: 'userpassword'
});
```

**Why Better**: Root credentials have unrestricted access. If exposed in client code, entire database is compromised. Use scopes and record users for client authentication.

---

### Anti-Pattern 18: No Session Expiration

**Problem**: Not setting session timeout for user authentication.

**Bad Example**:
```surreal
-- ❌ DON'T: No session expiration
DEFINE SCOPE user_scope
    SIGNUP (...)
    SIGNIN (...);
```

**Better Approach**:
```surreal
-- ✅ DO: Set reasonable session timeout
DEFINE SCOPE user_scope
    SESSION 2h  -- Sessions expire after 2 hours
    SIGNUP (...)
    SIGNIN (...);
```

**Why Better**: Limits window of opportunity if credentials are compromised. Forces periodic re-authentication.

---

## 6. Summary of Key Anti-Patterns

### Security
1. ❌ No explicit permissions defined
2. ❌ String interpolation in queries
3. ❌ Plain text passwords
4. ❌ No LIVE query cleanup
5. ❌ Overly permissive RBAC

### Performance
6. ❌ Missing indexes on queried fields
7. ❌ N+1 query pattern
8. ❌ New connection per request
9. ❌ Selecting all fields with SELECT *
10. ❌ Unlimited graph traversal depth

### Schema
11. ❌ SCHEMALESS for critical data
12. ❌ No validation with ASSERT
13. ❌ Missing unique constraints

### Testing
14. ❌ No tests for database operations
15. ❌ Not testing permissions

### Operations
16. ❌ Using --allow-all in production
17. ❌ Root credentials in client code
18. ❌ No session expiration

**Remember**: Each of these anti-patterns has caused production issues. Follow the better approaches to build secure, performant, and reliable SurrealDB applications.
