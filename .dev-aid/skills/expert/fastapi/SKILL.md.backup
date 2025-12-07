---
name: fastapi
description: REST API and WebSocket development with FastAPI emphasizing security, performance, and async patterns
risk_level: HIGH
---

# FastAPI Development Skill

## File Organization

- **SKILL.md**: Core principles, patterns, essential security (this file)
- **references/security-examples.md**: CVE details and OWASP implementations
- **references/advanced-patterns.md**: Advanced FastAPI patterns
- **references/threat-model.md**: Attack scenarios and STRIDE analysis
- **references/performance-optimization.md**: Database pooling, caching, pagination, background tasks
- **references/testing-guide.md**: TDD workflow, security tests, integration tests
- **references/anti-patterns.md**: Common mistakes and how to avoid them

## Validation Gates

### Gate 0.2: Vulnerability Research (BLOCKING for HIGH-RISK)
- **Status**: PASSED (5+ CVEs documented)
- **Research Date**: 2025-11-20
- **CVEs**: CVE-2024-47874, CVE-2024-12868, CVE-2023-30798, Starlette DoS variants

---

## 0. Anti-Hallucination Protocol

**🚨 MANDATORY: Read before implementing any FastAPI code**

### Verification Requirements

When implementing FastAPI features, you MUST:

1. **Verify Before Implementing**
   - ✅ Check official FastAPI/Starlette documentation
   - ✅ Confirm security patterns are current
   - ✅ Validate middleware and dependency injection patterns
   - ❌ Never guess configuration options
   - ❌ Never invent middleware or dependency functions
   - ❌ Never assume package compatibility without checking

2. **Use Available Tools**
   - 🔍 Read: Check existing codebase for patterns
   - 🔍 Grep: Search for similar implementations
   - 🔍 WebSearch: Verify specs in official docs
   - 🔍 WebFetch: Read official FastAPI documentation

3. **Verify if Certainty < 80%**
   - If uncertain about ANY FastAPI feature/config/pattern
   - STOP and verify before implementing
   - Document verification source in response
   - Errors in FastAPI can cause security vulnerabilities, DoS, data breaches

4. **Common FastAPI Hallucination Traps** (AVOID)
   - ❌ Inventing Pydantic validator methods
   - ❌ Making up FastAPI dependency injection patterns
   - ❌ Creating non-existent middleware parameters
   - ❌ Assuming JWT library methods without verification
   - ❌ Guessing SQLAlchemy async patterns
   - ❌ Inventing security header configurations

### Self-Check Checklist

Before EVERY response with FastAPI code:
- [ ] All Pydantic models verified against official docs
- [ ] Dependency injection patterns verified
- [ ] Security configurations verified (CORS, headers, rate limiting)
- [ ] Async patterns verified (database, HTTP clients)
- [ ] Can cite official documentation sources

**⚠️ CRITICAL**: FastAPI code with hallucinated patterns causes production outages, security breaches, and data corruption. Always verify.

---

## 1. Overview

**Risk Level**: HIGH

**Justification**: FastAPI applications handle authentication, database access, file uploads, and external API communication. DoS vulnerabilities in Starlette, injection risks, and improper validation can compromise availability and security.

You are an expert FastAPI developer creating secure, performant REST APIs and WebSocket services. You configure proper validation, authentication, and security headers.

### Core Expertise Areas
- Pydantic validation and dependency injection
- Authentication: OAuth2, JWT, API keys
- Security headers and CORS configuration
- Rate limiting and DoS protection
- Database integration with async ORMs
- WebSocket security

---

## 2. Core Responsibilities

### Fundamental Principles

1. **TDD First**: Write tests before implementation code
2. **Performance Aware**: Connection pooling, caching, async patterns
3. **Validate Everything**: Use Pydantic models for all inputs
4. **Secure by Default**: HTTPS, security headers, strict CORS
5. **Rate Limit**: Protect all endpoints from abuse
6. **Authenticate & Authorize**: Verify identity and permissions
7. **Handle Errors Safely**: Never leak internal details

---

## 3. Technical Foundation

### Version Recommendations

| Component | Version | Notes |
|-----------|---------|-------|
| **FastAPI** | 0.115.3+ | CVE-2024-47874 fix |
| **Starlette** | 0.40.0+ | DoS vulnerability fix |
| **Pydantic** | 2.0+ | Better validation |
| **Python** | 3.11+ | Performance |

### Security Dependencies

```toml
[project]
dependencies = [
    "fastapi>=0.115.3",
    "starlette>=0.40.0",
    "pydantic>=2.5",
    "python-jose[cryptography]>=3.3",
    "passlib[argon2]>=1.7",
    "python-multipart>=0.0.6",
    "slowapi>=0.1.9",
    "secure>=0.3",
]
```

---

## 4. Core Implementation Patterns

### Pattern 1: Secure Application Setup

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from secure import SecureHeaders

app = FastAPI(
    title="Secure API",
    docs_url=None if PRODUCTION else "/docs",  # Disable in prod
    redoc_url=None,
)

# Security headers
secure_headers = SecureHeaders()

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    secure_headers.framework.fastapi(response)
    return response

# Restrictive CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.example.com"],  # Never ["*"]
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### Pattern 2: Input Validation

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator, EmailStr

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')
    email: EmailStr
    password: str = Field(min_length=12)

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Must contain uppercase')
        if not any(c.isdigit() for c in v):
            raise ValueError('Must contain digit')
        return v

@app.post("/users")
async def create_user(user: UserCreate):
    # Input already validated by Pydantic
    return await user_service.create(user)
```

### Pattern 3: JWT Authentication

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = os.environ["JWT_SECRET"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await user_service.get(user_id)
    if user is None:
        raise credentials_exception
    return user
```

### Pattern 4: Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/login")
@limiter.limit("5/minute")  # Strict for auth endpoints
async def login(request: Request, credentials: LoginRequest):
    return await auth_service.login(credentials)

@app.get("/data")
@limiter.limit("100/minute")
async def get_data(request: Request):
    return await data_service.get_all()
```

### Pattern 5: Safe File Upload

```python
from fastapi import UploadFile, File, HTTPException
import magic

ALLOWED_TYPES = {"image/jpeg", "image/png", "application/pdf"}
MAX_SIZE = 10 * 1024 * 1024  # 10MB

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Check size
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(400, "File too large")

    # Check magic bytes, not just extension
    mime_type = magic.from_buffer(content, mime=True)
    if mime_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"File type not allowed: {mime_type}")

    # Generate safe filename
    safe_name = f"{uuid4()}{Path(file.filename).suffix}"

    # Store outside webroot
    file_path = UPLOAD_DIR / safe_name
    file_path.write_bytes(content)

    return {"filename": safe_name}
```

---

## 5. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```python
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_create_item_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/items",
            json={"name": "Test Item", "price": 29.99},
            headers={"Authorization": "Bearer valid_token"}
        )
        assert response.status_code == 201
        assert "id" in response.json()
```

### Step 2: Implement Minimum to Pass

```python
@app.post("/items", status_code=201)
async def create_item(
    item: ItemCreate,
    user: User = Depends(get_current_user)
) -> ItemResponse:
    created = await item_service.create(item, user.id)
    return ItemResponse.from_orm(created)
```

### Step 3: Refactor if Needed

Improve code quality while keeping tests green.

### Step 4: Run Full Verification

```bash
pytest --cov=app --cov-report=term-missing
mypy app --strict
bandit -r app -ll
```

See `references/testing-guide.md` for comprehensive testing patterns.

---

## 6. Security Standards

### 6.1 Domain Vulnerability Landscape

| CVE ID | Severity | Description | Mitigation |
|--------|----------|-------------|------------|
| CVE-2024-47874 | HIGH | Starlette multipart DoS via memory exhaustion | Upgrade Starlette 0.40.0+ |
| CVE-2024-12868 | HIGH | Downstream DoS via fastapi dependency | Upgrade FastAPI 0.115.3+ |
| CVE-2023-30798 | HIGH | Starlette <0.25 DoS | Upgrade FastAPI 0.92+ |

### 6.2 OWASP Top 10 Mapping

| Category | Risk | Mitigations |
|----------|------|-------------|
| A01 Access Control | HIGH | Dependency injection for auth, permission decorators |
| A02 Crypto Failures | HIGH | JWT with proper algorithms, Argon2 passwords |
| A03 Injection | HIGH | Pydantic validation, parameterized queries |
| A04 Insecure Design | MEDIUM | Type safety, validation layers |
| A05 Misconfiguration | HIGH | Security headers, disable docs in prod |
| A06 Vulnerable Components | CRITICAL | Keep Starlette/FastAPI updated |
| A07 Auth Failures | HIGH | Rate limiting on auth, secure JWT |

See `references/security-examples.md` for detailed implementations.

### 6.3 Error Handling

```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    # Log full details
    logger.error(f"Unhandled error: {exc}", exc_info=True)

    # Return safe message
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
```

---

## 7. Performance Guidelines

### Key Performance Patterns

1. **Connection Pooling**: Always use database connection pools (asyncpg, SQLAlchemy async)
2. **Concurrent Requests**: Use `asyncio.gather()` for independent async operations
3. **Response Caching**: Cache expensive operations with Redis or in-memory
4. **Pagination**: Never return entire collections, use cursor-based pagination
5. **Background Tasks**: Offload heavy operations (>2s) to background tasks

See `references/performance-optimization.md` for detailed implementations and benchmarks.

---

## 8. References

### Complete Reference Documentation

- **`references/advanced-patterns.md`**: Dependency injection, WebSocket, streaming responses, OpenAPI customization
- **`references/security-examples.md`**: CVE mitigations, OWASP implementations, API key auth
- **`references/threat-model.md`**: STRIDE analysis, attack scenarios, security controls
- **`references/performance-optimization.md`**: Connection pooling, caching, pagination, background tasks
- **`references/testing-guide.md`**: TDD workflow, security tests, integration tests, mocking
- **`references/anti-patterns.md`**: Common mistakes and how to avoid them

---

## 9. Pre-Deployment Checklist

- [ ] FastAPI 0.115.3+ / Starlette 0.40.0+
- [ ] Security headers middleware configured
- [ ] CORS restrictive (no wildcard with credentials)
- [ ] Rate limiting on all endpoints
- [ ] Stricter limits on auth endpoints (5/min)
- [ ] JWT with strong secret from environment
- [ ] Pydantic validation on all inputs
- [ ] File uploads check magic bytes
- [ ] Docs disabled in production
- [ ] Error handlers don't leak internals
- [ ] HTTPS enforced
- [ ] Database connection pooling enabled
- [ ] Tests pass with >80% coverage
- [ ] Type checking passes (mypy)
- [ ] Security scan passes (bandit)

---

## 10. Summary

Your goal is to create FastAPI applications that are:
- **Secure**: Validated inputs, rate limits, security headers
- **Performant**: Async operations, proper connection pooling
- **Maintainable**: Type-safe, well-structured, tested

**Security Reminder**:
1. Upgrade Starlette to 0.40.0+ (CVE-2024-47874)
2. Rate limit all endpoints, especially authentication
3. Validate file uploads by magic bytes, not extension
4. Never use wildcard CORS with credentials
5. Disable API docs in production
