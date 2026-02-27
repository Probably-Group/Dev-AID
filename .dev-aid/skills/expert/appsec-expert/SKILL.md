---
name: appsec-expert
version: 2.0.0
description: "Application security expertise covering OWASP Top 10, threat modeling (STRIDE), secure SDLC, and penetration testing patterns. Use when reviewing application code for vulnerabilities, implementing secure coding patterns, or conducting threat analysis. Do NOT use for CI/CD pipeline security (use devsecops-expert)."
risk_level: CRITICAL
---

# Application Security Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.2 Security Patterns (security rules)

**CWE-89/78/79: Injection Flaws**
- Do not: Concatenate user input into queries, commands, or HTML
- Instead: Parameterization, encoding, sanitization per context

**CWE-287: Broken Authentication**
- Do not: Custom auth schemes, weak session tokens
- Instead: Proven frameworks, secure session management, MFA

**CWE-862: Missing Authorization**
- Do not: Assume authenticated = authorized
- Instead: Check permissions for every action/resource

**CWE-311: Missing Encryption**
- Do not: Sensitive data without encryption in transit/at rest
- Instead: TLS everywhere, encrypt PII and secrets at rest

**CWE-502: Insecure Deserialization**
- Do not: Deserialize untrusted data
- Instead: JSON with strict schemas, never pickle/yaml.load

---

## 1. Security Principles (OWASP Top 10 2025)

### 1.1 A01: Broken Access Control (CWE-639, CWE-284)

**Principle:** Authorize every request. Never trust client-side checks.

```python
# ✅ Server-side authorization on every request
@app.get("/users/{user_id}/documents")
async def get_documents(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(403, "Access denied")
    return db.query(Document).filter(Document.user_id == user_id).all()
```

### 1.2 A02: Cryptographic Failures (CWE-327, CWE-328)

**Principle:** Use modern cryptography. Never roll your own.

```python
# ✅ Argon2id for passwords
from argon2 import PasswordHasher
ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4)
hash = ph.hash(password)

# ✅ AES-GCM for encryption
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
key = AESGCM.generate_key(bit_length=256)
aesgcm = AESGCM(key)
ciphertext = aesgcm.encrypt(os.urandom(12), plaintext, associated_data)
```

### 1.3 A03: Injection (CWE-89, CWE-78, CWE-79)

**Principle:** Data != Code. Never construct queries/commands from user input.

```python
# ✅ Parameterized SQL
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# ✅ Safe command execution
subprocess.run(["ping", "-c", "4", hostname], check=True)

# ✅ Output encoding
return f"<div>Hello, {html.escape(username)}</div>"
```

### 1.4 A04: Insecure Design (CWE-306, CWE-307)

**Principle:** Security must be designed in, not bolted on.

```python
# ✅ Rate limiting + account lockout
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/login")
@limiter.limit("5/minute")
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

**Principle:** Secure defaults. Restrict CORS. Add security headers.

```python
# ✅ Restricted CORS + security headers
ALLOWED_ORIGINS = os.environ["ALLOWED_ORIGINS"].split(",")
app.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True, allow_methods=["GET", "POST", "PUT", "DELETE"])

@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response
```

### 1.6 A07: Authentication Failures (CWE-287, CWE-384)

**Principle:** Short-lived tokens with proper validation.

```python
ACCESS_TOKEN_EXPIRE = timedelta(minutes=15)
REFRESH_TOKEN_EXPIRE = timedelta(days=7)
SECRET_KEY = os.environ["JWT_SECRET_KEY"]

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=["HS256"],
            options={"require_exp": True}
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

### 1.7 A10: Server-Side Request Forgery (CWE-918)

**Principle:** Validate and restrict outbound requests.

```python
import ipaddress
from urllib.parse import urlparse

ALLOWED_DOMAINS = {"api.example.com", "cdn.example.com"}

def is_safe_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname not in ALLOWED_DOMAINS:
            return False
        ip = ipaddress.ip_address(parsed.hostname)
        return not (ip.is_private or ip.is_loopback or ip.is_reserved)
    except:
        return False

@app.get("/fetch")
async def fetch_url(url: str):
    if not is_safe_url(url):
        raise HTTPException(400, "Invalid URL")
    return requests.get(url, timeout=10).text
```

---

## 2. Version Requirements

Use these minimum versions:
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
from jose import jwt
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
    return jwt.encode(
        {"sub": str(user_id), "exp": datetime.now(timezone.utc) + ACCESS_TOKEN_EXPIRE},
        SECRET_KEY, algorithm=ALGORITHM)
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

## 4. Security Testing

Always write tests covering:
- **Injection**: Send SQL/XSS payloads, verify they are neutralized
- **Authorization**: Verify regular users get 403 on admin endpoints, test IDOR by accessing other users' resources
- **Rate limiting**: Exceed login attempts, verify 429 response
- **Token expiry**: Use expired JWT, verify rejection
- **SSRF**: Attempt internal IP/localhost URLs, verify rejection

Use `secrets.token_urlsafe(32)` for any security-relevant randomness (never `random`).
Log errors internally with detail, return generic messages to users.

---

## 5. Pre-Generation Checklist

Before generating security-sensitive code:

- [ ] A01: Authorization check on every endpoint (server-side, not client-only)
- [ ] A02: Argon2id for passwords, AES-GCM for encryption
- [ ] A04: Rate limiting and account lockout on auth endpoints
- [ ] A07: JWT 15min access / 7d refresh, `require_exp` enforced
- [ ] A10: URL validation with domain allowlist + private IP blocking for SSRF