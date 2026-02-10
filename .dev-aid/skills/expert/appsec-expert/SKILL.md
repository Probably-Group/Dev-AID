---
name: appsec-expert
version: 2.0.0
description: "Application security expertise covering OWASP Top 10, threat modeling (STRIDE), secure SDLC, and penetration testing patterns. Use when reviewing application code for vulnerabilities, implementing secure coding patterns, or conducting threat analysis. Do NOT use for CI/CD pipeline security (use devsecops-expert)."
risk_level: CRITICAL
---

# Application Security Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-89/78/79: Injection Flaws**
- NEVER: Concatenate user input into queries, commands, or HTML
- ALWAYS: Parameterization, encoding, sanitization per context

**CWE-287: Broken Authentication**
- NEVER: Custom auth schemes, weak session tokens
- ALWAYS: Proven frameworks, secure session management, MFA

**CWE-862: Missing Authorization**
- NEVER: Assume authenticated = authorized
- ALWAYS: Check permissions for every action/resource

**CWE-311: Missing Encryption**
- NEVER: Sensitive data without encryption in transit/at rest
- ALWAYS: TLS everywhere, encrypt PII and secrets at rest

**CWE-502: Insecure Deserialization**
- NEVER: Deserialize untrusted data
- ALWAYS: JSON with strict schemas, never pickle/yaml.load

### 0.3 Risk Level: CRITICAL

**Verification requirements for CRITICAL risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles (OWASP Top 10 2025)

### 1.1 A01: Broken Access Control (CWE-639, CWE-284)

**Principle:** Authorize every request. Never trust client-side checks.

```python
# ❌ WRONG - No authorization check (IDOR vulnerability)
@app.get("/users/{user_id}/documents")
async def get_documents(user_id: int):
    return db.query(Document).filter(Document.user_id == user_id).all()

# ❌ WRONG - Client-side only authorization
# Frontend: if (user.role === 'admin') showDeleteButton()
# Backend has no check!

# ✅ CORRECT - Server-side authorization on every request
@app.get("/users/{user_id}/documents")
async def get_documents(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    # Verify ownership or admin role
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(403, "Access denied")
    return db.query(Document).filter(Document.user_id == user_id).all()
```

### 1.2 A02: Cryptographic Failures (CWE-327, CWE-328)

**Principle:** Use modern cryptography. Never roll your own.

```python
# ❌ WRONG - Weak password hashing
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()
password_hash = hashlib.sha256(password.encode()).hexdigest()

# ❌ WRONG - Weak encryption
from Crypto.Cipher import DES  # DES is broken
cipher = DES.new(key, DES.MODE_ECB)  # ECB mode is insecure

# ✅ CORRECT - Argon2id for passwords
from argon2 import PasswordHasher
ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4)
hash = ph.hash(password)

# ✅ CORRECT - AES-GCM for encryption
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
key = AESGCM.generate_key(bit_length=256)
aesgcm = AESGCM(key)
nonce = os.urandom(12)
ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)
```

### 1.3 A03: Injection (CWE-89, CWE-78, CWE-79)

**Principle:** Data ≠ Code. Never construct queries/commands from user input.

```python
# ❌ WRONG - SQL injection
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)

# ❌ WRONG - Command injection
os.system(f"ping {hostname}")
subprocess.run(f"convert {filename}", shell=True)

# ❌ WRONG - XSS
return f"<div>Hello, {username}</div>"

# ✅ CORRECT - Parameterized SQL
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# ✅ CORRECT - Safe command execution
subprocess.run(["ping", "-c", "4", hostname], check=True)

# ✅ CORRECT - Output encoding
import html
return f"<div>Hello, {html.escape(username)}</div>"
```

### 1.4 A04: Insecure Design (CWE-306, CWE-307)

**Principle:** Security must be designed in, not bolted on.

```python
# ❌ WRONG - No rate limiting on authentication
@app.post("/login")
async def login(credentials: Credentials):
    user = authenticate(credentials)  # No limit = brute force!

# ❌ WRONG - No account lockout
failed_attempts = 0  # Only in memory, reset on restart

# ✅ CORRECT - Rate limiting + account lockout
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/login")
@limiter.limit("5/minute")  # 5 attempts per minute per IP
async def login(credentials: Credentials, request: Request):
    if is_account_locked(credentials.username):
        raise HTTPException(429, "Account locked. Try again later.")

    user = authenticate(credentials)
    if not user:
        increment_failed_attempts(credentials.username)
        if get_failed_attempts(credentials.username) >= 5:
            lock_account(credentials.username, duration=timedelta(minutes=15))
        raise HTTPException(401, "Invalid credentials")

    reset_failed_attempts(credentials.username)
    return create_tokens(user)
```

### 1.5 A05: Security Misconfiguration (CWE-16)

**Principle:** Secure defaults. Disable debug in production.

```python
# ❌ WRONG - Debug enabled in production
app = FastAPI(debug=True)  # Exposes stack traces!

# ❌ WRONG - Permissive CORS
app.add_middleware(CORSMiddleware, allow_origins=["*"])

# ❌ WRONG - Missing security headers
# No CSP, HSTS, X-Frame-Options

# ✅ CORRECT - Secure configuration
import os
app = FastAPI(debug=os.getenv("DEBUG", "false").lower() == "true")

# ✅ CORRECT - Restricted CORS
ALLOWED_ORIGINS = os.environ["ALLOWED_ORIGINS"].split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
)

# ✅ CORRECT - Security headers
@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

### 1.6 A06: Vulnerable Components (CWE-829)

**Principle:** Audit dependencies. Pin versions. Update regularly.

```bash
# ❌ WRONG - No version pinning
pip install requests
npm install lodash

# ❌ WRONG - Never audited
# No CI/CD security checks

# ✅ CORRECT - Pin versions
pip install requests==2.31.0
npm install --save-exact lodash@4.17.21

# ✅ CORRECT - Audit in CI/CD
pip-audit
npm audit
snyk test
dependabot alerts enabled
```

### 1.7 A07: Authentication Failures (CWE-287, CWE-384)

**Principle:** Secure session management. Short-lived tokens.

```python
# ❌ WRONG - Long-lived tokens
ACCESS_TOKEN_EXPIRE = timedelta(days=30)  # Way too long!

# ❌ WRONG - Secrets in code
SECRET_KEY = "my-secret-key-12345"

# ❌ WRONG - No token expiration check
def get_current_user(token):
    payload = jwt.decode(token, SECRET_KEY)  # No verification!
    return payload["sub"]

# ✅ CORRECT - Short-lived access, longer refresh
ACCESS_TOKEN_EXPIRE = timedelta(minutes=15)
REFRESH_TOKEN_EXPIRE = timedelta(days=7)

SECRET_KEY = os.environ["JWT_SECRET_KEY"]  # From environment

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=["HS256"],
            options={"require_exp": True}  # Require expiration
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(401, "Invalid token")
        return get_user(user_id)
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.JWTError:
        raise HTTPException(401, "Invalid token")
```

### 1.8 A10: Server-Side Request Forgery (CWE-918)

**Principle:** Validate and restrict outbound requests.

```python
# ❌ WRONG - User controls URL
@app.get("/fetch")
async def fetch_url(url: str):
    response = requests.get(url)  # Can access internal services!
    return response.text

# ✅ CORRECT - URL validation and allowlist
import ipaddress
from urllib.parse import urlparse

ALLOWED_DOMAINS = {"api.example.com", "cdn.example.com"}

def is_safe_url(url: str) -> bool:
    try:
        parsed = urlparse(url)

        # Only HTTPS
        if parsed.scheme != "https":
            return False

        # Domain allowlist
        if parsed.hostname not in ALLOWED_DOMAINS:
            return False

        # Block internal IPs
        ip = ipaddress.ip_address(parsed.hostname)
        if ip.is_private or ip.is_loopback or ip.is_reserved:
            return False

        return True
    except:
        return False

@app.get("/fetch")
async def fetch_url(url: str):
    if not is_safe_url(url):
        raise HTTPException(400, "Invalid URL")
    response = requests.get(url, timeout=10)
    return response.text
```

---

## 2. Version Requirements

**ALWAYS use these minimum versions:**
```
# Python Security
argon2-cffi>=21.3.0     # Password hashing
PyJWT>=2.8.0            # JWT with security fixes
cryptography>=42.0.0    # Modern crypto

# Security Testing
semgrep>=1.50.0         # SAST
bandit>=1.7.0           # Python security linter
pip-audit>=2.6.0        # Dependency audit

# JavaScript Security
helmet>=7.1.0           # Express security headers
bcrypt>=5.1.0           # Password hashing
jsonwebtoken>=9.0.0     # JWT
```

---

## 3. Code Patterns

### 3.1 WHEN implementing authentication

```python
from datetime import datetime, timedelta, timezone
from argon2 import PasswordHasher
from jose import jwt, JWTError
import os

SECRET_KEY = os.environ["JWT_SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = timedelta(minutes=15)

ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4)

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(hash: str, password: str) -> bool:
    try:
        ph.verify(hash, password)
        return True
    except:
        return False

def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + ACCESS_TOKEN_EXPIRE
    return jwt.encode(
        {"sub": str(user_id), "exp": expire},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
```

### 3.2 WHEN implementing authorization

```python
from functools import wraps
from enum import Enum

class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"

def require_role(required_role: Role):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if current_user.role != required_role and current_user.role != Role.ADMIN:
                raise HTTPException(403, "Insufficient permissions")
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

@app.delete("/users/{user_id}")
@require_role(Role.ADMIN)
async def delete_user(user_id: int, current_user: User = Depends(get_current_user)):
    # Only admins can reach here
    db.delete(User, user_id)
```

### 3.3 WHEN implementing input validation

```python
from pydantic import BaseModel, Field, field_validator
import re

class UserInput(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(max_length=255)
    age: int = Field(ge=0, le=150)

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must be alphanumeric')
        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v
```

---

## 4. Anti-Patterns

### 4.1 Client-Side Authorization

**NEVER** rely on client-side checks:
```javascript
// ❌ WRONG - Frontend-only authorization
if (user.role === 'admin') {
    showDeleteButton();  // Anyone can modify JS!
}

// ✅ CORRECT - Server validates every request
// Backend must check authorization regardless of UI
```

### 4.2 Insecure Randomness

**NEVER** use weak random for security:
```python
# ❌ WRONG - Predictable
import random
token = ''.join(random.choices(string.ascii_letters, k=32))

# ✅ CORRECT - Cryptographically secure
import secrets
token = secrets.token_urlsafe(32)
```

### 4.3 Error Message Information Disclosure

**NEVER** expose internal details:
```python
# ❌ WRONG - Leaks database schema
except Exception as e:
    return {"error": str(e)}  # "Column 'password_hash' doesn't exist"

# ✅ CORRECT - Generic message
except Exception as e:
    logger.error(f"Database error: {e}")  # Log internally
    return {"error": "An error occurred"}  # Generic to user
```

---

## 5. Testing

**ALWAYS write security tests:**
```python
import pytest

class TestAuthSecurity:
    def test_sql_injection_blocked(self, client):
        payloads = ["' OR '1'='1", "'; DROP TABLE users; --", "admin'--"]
        for payload in payloads:
            response = client.get(f"/users?search={payload}")
            assert response.status_code in [200, 400]
            assert "DROP" not in response.text

    def test_authorization_enforced(self, client, regular_user_token):
        # Regular user cannot access admin endpoint
        response = client.delete(
            "/admin/users/1",
            headers={"Authorization": f"Bearer {regular_user_token}"}
        )
        assert response.status_code == 403

    def test_rate_limiting_works(self, client):
        # Exceed rate limit
        for _ in range(10):
            client.post("/login", json={"username": "test", "password": "wrong"})
        response = client.post("/login", json={"username": "test", "password": "wrong"})
        assert response.status_code == 429

    def test_xss_prevented(self, client, auth_headers):
        response = client.post(
            "/comments",
            json={"content": "<script>alert('xss')</script>"},
            headers=auth_headers
        )
        assert "<script>" not in response.text
```

---

## 6. Pre-Generation Checklist

**BEFORE generating any security-sensitive code:**

- [ ] A01: Authorization check on every endpoint
- [ ] A02: Argon2id for passwords, AES-GCM for encryption
- [ ] A03: Parameterized queries, no string concatenation
- [ ] A04: Rate limiting, account lockout
- [ ] A05: Debug disabled, security headers set
- [ ] A06: Dependencies audited, versions pinned
- [ ] A07: JWT expires (15min access, 7d refresh)
- [ ] A10: URL validation, domain allowlist for SSRF
- [ ] Secrets from environment, never hardcoded
- [ ] Generic error messages to users
- [ ] Security tests written

---

**Performance**: Quality over speed. Verify all code examples compile. Never skip security checks. See `template-references/performance-notes.md` for full guidelines.