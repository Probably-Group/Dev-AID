# SurrealDB Security Examples

## 1. Critical Security Vulnerabilities

### Vulnerability 1: Default Full Table Permissions (GHSA-x5fr-7hhj-34j3)

**Scenario**: Tables created without explicit permissions may have insecure defaults.

**Vulnerable Code**:
```surreal
-- ❌ VULNERABLE: No permissions defined
DEFINE TABLE sensitive_data SCHEMAFULL;
-- Default is FULL for system users, NONE for record users
```

**Secure Code**:
```surreal
-- ✅ SECURE: Explicit permissions
DEFINE TABLE sensitive_data SCHEMAFULL
    PERMISSIONS
        FOR select WHERE $auth.role = 'admin'
        FOR create, update, delete NONE;
```

**Explanation**: Always define explicit permissions. Never rely on defaults, as they may change or not match your security requirements.

---

### Vulnerability 2: Injection via String Concatenation

**Scenario**: User input concatenated directly into queries.

**Vulnerable Code**:
```javascript
// ❌ VULNERABLE
const userId = req.params.id;
const query = `SELECT * FROM user:${userId}`;
await db.query(query);
```

**Secure Code**:
```javascript
// ✅ SECURE
const userId = req.params.id;
const result = await db.query(
    'SELECT * FROM $record',
    { record: `user:${userId}` }
);
```

**Explanation**: Always use parameterized queries. String concatenation can allow injection attacks where malicious input could execute arbitrary queries.

---

### Vulnerability 3: Plain Text Password Storage

**Scenario**: Passwords stored without hashing.

**Vulnerable Code**:
```surreal
-- ❌ VULNERABLE: Plain text password
DEFINE FIELD password ON TABLE user TYPE string;

CREATE user CONTENT {
    email: $email,
    password: $password  -- Stored as plain text!
};
```

**Secure Code**:
```surreal
-- ✅ SECURE: Hashed password
DEFINE FIELD password ON TABLE user TYPE string
    VALUE crypto::argon2::generate($value);

CREATE user CONTENT {
    email: $email,
    password: $password  -- Automatically hashed
};
```

**Explanation**: Use crypto::argon2::generate() to hash passwords. Argon2 is the recommended algorithm. Never store passwords in plain text.

---

### Vulnerability 4: LIVE Query Permissions Bypass

**Scenario**: LIVE queries without proper permission checks.

**Vulnerable Code**:
```surreal
-- ❌ VULNERABLE: LIVE query without permission check
LIVE SELECT * FROM user;
```

**Secure Code**:
```surreal
-- ✅ SECURE: LIVE query with permission filter
LIVE SELECT * FROM user WHERE id = $auth.id OR public = true;
```

**Explanation**: LIVE queries must include WHERE clauses that respect user permissions. Otherwise, users may receive updates for data they shouldn't access.

---

### Vulnerability 5: SSRF via Network Access

**Scenario**: Unrestricted network access from database server.

**Vulnerable Configuration**:
```bash
# ❌ VULNERABLE: Unrestricted network access
surreal start --allow-all
```

**Secure Configuration**:
```bash
# ✅ SECURE: Restrict network access
surreal start --allow-net example.com --deny-net 10.0.0.0/8
```

**Explanation**: Use --allow-net to whitelist specific domains and --deny-net to block internal networks. This prevents SSRF attacks where the database could be tricked into accessing internal resources.

---

## 2. Row-Level Security

### Scenario: Users should only access their own data

**Implementation**:
```surreal
-- ✅ SECURE: Row-level security with $auth
DEFINE TABLE user SCHEMAFULL
    PERMISSIONS
        FOR select, update, delete WHERE id = $auth.id
        FOR create WHERE $auth.role = 'admin';

DEFINE FIELD email ON TABLE user TYPE string ASSERT string::is::email($value);
DEFINE FIELD password ON TABLE user TYPE string VALUE crypto::argon2::generate($value);
DEFINE FIELD role ON TABLE user TYPE string DEFAULT 'user' ASSERT $value IN ['user', 'admin'];
DEFINE FIELD created ON TABLE user TYPE datetime DEFAULT time::now();

DEFINE INDEX unique_email ON TABLE user COLUMNS email UNIQUE;
```

**Test**:
```python
@pytest.mark.asyncio
async def test_user_cannot_access_other_users_data():
    """Row-level security should prevent access to other users' data."""
    # Sign in as regular user
    user_db = Surreal("ws://localhost:8000/rpc")
    await user_db.connect()
    await user_db.use("test", "test_db")
    await user_db.signin({
        "scope": "user_scope",
        "email": "user@test.com",
        "password": "user123"
    })

    # Try to access another user
    result = await user_db.query("SELECT * FROM user:admin")
    assert len(result[0]["result"]) == 0  # Should be empty due to permissions

    await user_db.close()
```

---

## 3. Authentication & Authorization

### Pattern 1: Secure SCOPE Definition

```surreal
-- ✅ SECURE: Scope with session expiration and proper authentication
DEFINE SCOPE user_scope
    SESSION 2h  -- Short session timeout
    SIGNUP (
        CREATE user CONTENT {
            email: $email,
            password: crypto::argon2::generate($password),
            role: 'user',
            created_at: time::now()
        }
    )
    SIGNIN (
        SELECT * FROM user WHERE email = $email
        AND crypto::argon2::compare(password, $password)
    );
```

### Pattern 2: Multi-Role Authorization

```surreal
-- Define tables with role-based permissions
DEFINE TABLE document SCHEMAFULL
    PERMISSIONS
        FOR select WHERE public = true OR owner = $auth.id OR $auth.role = 'admin'
        FOR create WHERE $auth.id != NONE
        FOR update WHERE owner = $auth.id OR $auth.role = 'admin'
        FOR delete WHERE owner = $auth.id OR $auth.role = 'admin';

DEFINE FIELD owner ON TABLE document TYPE record<user> VALUE $auth.id;
DEFINE FIELD public ON TABLE document TYPE bool DEFAULT false;
DEFINE FIELD content ON TABLE document TYPE string;
```

---

## 4. Input Validation

### Pattern 1: Field-Level Validation

```surreal
-- ✅ SECURE: Comprehensive validation
DEFINE TABLE product SCHEMAFULL;

DEFINE FIELD name ON TABLE product
    TYPE string
    ASSERT string::length($value) >= 3 AND string::length($value) <= 100;

DEFINE FIELD price ON TABLE product
    TYPE decimal
    ASSERT $value > 0 AND $value < 1000000;

DEFINE FIELD email ON TABLE product
    TYPE string
    ASSERT string::is::email($value);

DEFINE FIELD url ON TABLE product
    TYPE string
    ASSERT string::is::url($value);

DEFINE FIELD category ON TABLE product
    TYPE string
    ASSERT $value IN ['electronics', 'clothing', 'food', 'books'];

-- These will fail validation
CREATE product CONTENT { name: "AB", price: -10 };  -- ❌ Name too short, negative price
CREATE product CONTENT { email: "notanemail" };  -- ❌ Invalid email
```

### Pattern 2: Parameterized Queries

```javascript
// ✅ SECURE: Always use parameters
async function createUser(email, name, role) {
    return await db.query(
        `CREATE user CONTENT {
            email: $email,
            name: $name,
            role: $role,
            password: crypto::argon2::generate($password)
        }`,
        { email, name, role, password: generateSecurePassword() }
    );
}

// ❌ INSECURE: String interpolation
async function badCreateUser(email, name) {
    // NEVER DO THIS!
    return await db.query(`
        CREATE user CONTENT {
            email: "${email}",
            name: "${name}"
        }
    `);
}
```

---

## 5. OWASP Top 10 2025 Mapping

| OWASP ID | Category | SurrealDB Risk | Mitigation |
|----------|----------|----------------|------------|
| A01:2025 | Broken Access Control | Critical | Row-level PERMISSIONS, RBAC |
| A02:2025 | Cryptographic Failures | High | crypto::argon2 for passwords |
| A03:2025 | Injection | Critical | Parameterized queries, $variables |
| A04:2025 | Insecure Design | High | Explicit schema, ASSERT validation |
| A05:2025 | Security Misconfiguration | Critical | Explicit PERMISSIONS, --allow-net |
| A06:2025 | Vulnerable Components | Medium | Keep SurrealDB updated, monitor advisories |
| A07:2025 | Auth & Session Failures | Critical | SCOPE with SESSION expiry, RBAC |
| A08:2025 | Software/Data Integrity | High | SCHEMAFULL, type validation, ASSERT |
| A09:2025 | Logging & Monitoring | Medium | Audit LIVE queries, log auth failures |
| A10:2025 | SSRF | High | --allow-net, --deny-net flags |

---

## 6. Security Checklist

Before deploying SurrealDB to production:

### Configuration
- [ ] All tables have explicit PERMISSIONS defined
- [ ] No tables rely on default permissions
- [ ] SESSION expiration set (≤2 hours for record users)
- [ ] Network access restricted with --allow-net and --deny-net
- [ ] Root credentials not exposed to client applications
- [ ] TLS/SSL enabled for production connections

### Schema
- [ ] All critical tables use SCHEMAFULL
- [ ] Password fields use crypto::argon2::generate()
- [ ] All fields have appropriate TYPE definitions
- [ ] ASSERT validation on user input fields
- [ ] Unique indexes on email/username fields
- [ ] Foreign key constraints with TYPE record<table>

### Queries
- [ ] All queries use parameterized $variables
- [ ] No string concatenation in queries
- [ ] LIVE queries include WHERE permission clauses
- [ ] All user input validated with ASSERT
- [ ] Graph traversals have depth limits

### Authentication
- [ ] SCOPE definitions include SESSION expiration
- [ ] RBAC implemented with least privilege
- [ ] Row-level security uses $auth context
- [ ] Multi-factor authentication considered
- [ ] Failed login attempts monitored

### Testing
- [ ] Row-level security tested with different $auth contexts
- [ ] Permission boundaries tested
- [ ] Injection attacks tested
- [ ] LIVE query permissions tested
- [ ] Session expiration tested

### Monitoring
- [ ] Audit logging enabled
- [ ] Failed authentication attempts logged
- [ ] Unusual query patterns monitored
- [ ] Security advisories subscribed
- [ ] Backup and recovery tested

---

## 7. Common Security Mistakes

### Mistake 1: No Cleanup of LIVE Queries

**Problem**:
```javascript
// ❌ Memory leak
async function subscribe() {
    const uuid = await db.live('user', callback);
    // Never killed!
}
```

**Solution**:
```javascript
// ✅ Proper cleanup
const uuid = await db.live('user', callback);
// Later or on component unmount:
await db.kill(uuid);
```

### Mistake 2: Overly Permissive RBAC

**Problem**:
```surreal
-- ❌ Everyone is OWNER
DEFINE USER dev ON ROOT PASSWORD 'weak' ROLES OWNER;
```

**Solution**:
```surreal
-- ✅ Least privilege
DEFINE USER dev ON DATABASE app PASSWORD 'strong' ROLES VIEWER;
DEFINE USER admin ON ROOT PASSWORD 'very_strong' ROLES OWNER;
```

### Mistake 3: Using --allow-all in Production

**Problem**:
```bash
# ❌ DANGEROUS
surreal start --allow-all
```

**Solution**:
```bash
# ✅ Restricted
surreal start --allow-net api.example.com --deny-net 10.0.0.0/8
```

---

## 8. Security Resources

- **Security Advisories**: https://github.com/surrealdb/surrealdb/security
- **Documentation**: https://surrealdb.com/docs/surrealdb/security
- **Best Practices**: https://surrealdb.com/docs/surrealdb/reference-guide/security-best-practices
