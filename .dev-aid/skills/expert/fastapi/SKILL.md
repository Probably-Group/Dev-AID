---
name: fastapi
version: 2.0.0
description: "FastAPI development patterns for JARVIS project including async API endpoints, WebSocket communication, and Pydantic model validation. Use when building JARVIS FastAPI services, adding WebSocket endpoints, or writing Pydantic schemas for the JARVIS assistant. Do NOT use for production auth patterns like OAuth2/JWT or SQLAlchemy integration (use fastapi-expert)."
compatibility: "Python 3.11+, FastAPI 0.115+"
risk_level: HIGH
---

# FastAPI Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-89: SQL Injection**
- NEVER: f-strings in queries: `db.execute(f"SELECT * FROM users WHERE id = {id}")`
- ALWAYS: SQLAlchemy ORM or parameterized: `db.execute(select(User).where(User.id == id))`

**CWE-285: Improper Authorization**
- NEVER: Trust client-provided user ID for authorization
- ALWAYS: Extract user from validated JWT token, check permissions server-side

**CWE-352: CSRF**
- NEVER: State-changing GET requests
- ALWAYS: Use POST/PUT/DELETE with CSRF tokens for browser clients

**CWE-22: Path Traversal in StaticFiles**
- NEVER: `StaticFiles(directory=user_input)` or serve user-controlled paths
- ALWAYS: Hardcode static directories, validate any file paths

**CWE-400: Resource Exhaustion**
- NEVER: Unlimited file uploads or request body size
- ALWAYS: Set `max_upload_size`, use streaming for large files

### 0.3 Risk Level: HIGH

**Verification requirements for HIGH risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 SQL Injection Prevention (CWE-89)

**Principle:** Never use f-strings in SQL. Always use parameterized queries.

```python
# ❌ WRONG - SQL injection
@app.get("/users")
async def get_users(name: str):
    query = f"SELECT * FROM users WHERE name = '{name}'"
    return await db.execute(query)

# ✅ CORRECT - Parameterized query
@app.get("/users")
async def get_users(name: str):
    query = "SELECT * FROM users WHERE name = :name"
    return await db.execute(query, {"name": name})

# ✅ CORRECT - SQLAlchemy ORM
@app.get("/users")
async def get_users(name: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.name == name)
    )
    return result.scalars().all()
```

### 1.2 Input Validation (CWE-20)

**Principle:** All input validated via Pydantic models. Use strict types.

```python
# ❌ WRONG - No validation
@app.post("/users")
async def create_user(data: dict):
    return await db.create_user(**data)

# ✅ CORRECT - Pydantic validation
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    model_config = ConfigDict(strict=True)

    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    age: int = Field(ge=0, le=150)

@app.post("/users")
async def create_user(data: UserCreate):
    return await db.create_user(**data.model_dump())
```

### 1.3 Authentication Required (CWE-306)

**Principle:** Protect all endpoints by default. Explicitly mark public endpoints.

### 1.4 Secrets ≠ Code (CWE-798)

**Principle:** All secrets from environment. Never commit .env files.

### 1.5 CORS Security (CWE-346)

**Principle:** Strict origin allowlist. Never use `*` in production.

### 1.6 Rate Limiting (CWE-770)

**Principle:** Rate limit all endpoints. Stricter limits on auth endpoints.

---

## 2. Version Requirements

**ALWAYS use these minimum versions:**

```
fastapi>=0.115.0
pydantic>=2.5.0
starlette>=0.40.0
python-multipart>=0.0.6
uvicorn>=0.30.0
slowapi>=0.1.9
sqlalchemy>=2.0.0
```

---

## 3. Code Patterns

### 3.1 WHEN creating the application

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up...")
    await init_db()
    yield
    # Shutdown
    logger.info("Shutting down...")
    await close_db()

app = FastAPI(
    title="My API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    openapi_url="/api/openapi.json" if settings.DEBUG else None,
)

# CORS - strict origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # List of allowed origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "code": "INTERNAL_ERROR"},
    )
```

### 3.2 WHEN implementing authentication

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel
from datetime import datetime, timedelta

security = HTTPBearer()

class TokenPayload(BaseModel):
    sub: str
    exp: datetime
    role: str

class User(BaseModel):
    id: str
    email: str
    role: str

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        token_data = TokenPayload(**payload)

        if token_data.exp < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = await get_user_by_id(token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return User(id=user.id, email=user.email, role=token_data.role)

def require_role(*roles: str):
    async def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user
    return role_checker

# Usage
@app.get("/admin/users")
async def list_users(user: User = Depends(require_role("admin"))):
    return await get_all_users()
```

### 3.3 WHEN defining Pydantic models

```python
from pydantic import BaseModel, ConfigDict, Field, EmailStr, field_validator
from datetime import datetime
from typing import Annotated
from uuid import UUID

# Reusable annotated types
UserId = Annotated[UUID, Field(description="User ID")]
Email = Annotated[EmailStr, Field(description="Email address")]
Name = Annotated[str, Field(min_length=1, max_length=100)]

class UserBase(BaseModel):
    """Base user fields shared across schemas."""
    email: Email
    name: Name

class UserCreate(UserBase):
    """Schema for creating a user."""
    model_config = ConfigDict(strict=True)

    password: str = Field(min_length=8, max_length=100)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain digit")
        return v

class UserUpdate(BaseModel):
    """Schema for updating a user (all optional)."""
    email: Email | None = None
    name: Name | None = None

class UserResponse(UserBase):
    """Schema for user responses (no sensitive data)."""
    model_config = ConfigDict(from_attributes=True)

    id: UserId
    role: str
    created_at: datetime
    updated_at: datetime

class UserList(BaseModel):
    """Paginated user list response."""
    data: list[UserResponse]
    meta: "PaginationMeta"

class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool
```

### 3.4 WHEN implementing CRUD endpoints

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

router = APIRouter(prefix="/api/v1/users", tags=["users"])

# Dependency for pagination
class PaginationParams:
    def __init__(
        self,
        page: Annotated[int, Query(ge=1)] = 1,
        limit: Annotated[int, Query(ge=1, le=100)] = 20,
    ):
        self.page = page
        self.limit = limit
        self.offset = (page - 1) * limit

@router.get("", response_model=UserList)
async def list_users(
    pagination: Annotated[PaginationParams, Depends()],
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    status_filter: str | None = Query(None, alias="status"),
):
    """List users with pagination and filtering."""
    query = select(UserModel)

    if status_filter:
        query = query.where(UserModel.status == status_filter)

    # Get total count
    total = await db.scalar(select(func.count()).select_from(query.subquery()))

    # Get paginated results
    query = query.offset(pagination.offset).limit(pagination.limit)
    result = await db.execute(query)
    users = result.scalars().all()

    return UserList(
        data=[UserResponse.model_validate(u) for u in users],
        meta=PaginationMeta(
            page=pagination.page,
            limit=pagination.limit,
            total=total,
            total_pages=(total + pagination.limit - 1) // pagination.limit,
            has_next=pagination.page * pagination.limit < total,
            has_prev=pagination.page > 1,
        ),
    )

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    """Create a new user."""
    # Check for existing user
    existing = await db.execute(
        select(UserModel).where(UserModel.email == data.email)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Hash password
    password_hash = hash_password(data.password)

    new_user = UserModel(
        email=data.email,
        name=data.name,
        password_hash=password_hash,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return UserResponse.model_validate(new_user)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific user."""
    result = await db.execute(
        select(UserModel).where(UserModel.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse.model_validate(user)

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a user."""
    # Check authorization
    if str(current_user.id) != str(user_id) and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user",
        )

    result = await db.execute(
        select(UserModel).where(UserModel.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update only provided fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Delete a user."""
    result = await db.execute(
        select(UserModel).where(UserModel.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()
```

### 3.5 WHEN implementing rate limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"error": "Rate limit exceeded", "code": "RATE_LIMITED"},
        headers={"Retry-After": str(exc.detail)},
    )

# Apply rate limits
@app.post("/auth/login")
@limiter.limit("5/minute")  # Strict for auth
async def login(request: Request, credentials: LoginRequest):
    ...

@app.get("/api/users")
@limiter.limit("100/minute")  # Normal API limit
async def list_users(request: Request):
    ...
```

### 3.6 WHEN implementing database sessions

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
```

---

## 4. Anti-Patterns

**NEVER:**
- Use f-strings in SQL queries
- Skip Pydantic validation for request bodies
- Return 200 for all responses
- Expose passwords or sensitive data in responses
- Use `*` for CORS origins in production
- Skip rate limiting on auth endpoints
- Use synchronous database calls in async handlers
- Catch all exceptions silently

---

## 5. Testing

**ALWAYS write FastAPI tests:**

```python
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def auth_headers():
    token = create_test_token(user_id="test-user", role="user")
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_create_user_success(client: AsyncClient, auth_headers):
    response = await client.post(
        "/api/v1/users",
        json={
            "email": "new@example.com",
            "name": "New User",
            "password": "SecurePass123",
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@example.com"
    assert "password" not in data

@pytest.mark.asyncio
async def test_create_user_invalid_email(client: AsyncClient, auth_headers):
    response = await client.post(
        "/api/v1/users",
        json={"email": "invalid", "name": "Test", "password": "SecurePass123"},
        headers=auth_headers,
    )

    assert response.status_code == 422

@pytest.mark.asyncio
async def test_unauthorized_without_token(client: AsyncClient):
    response = await client.get("/api/v1/users")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_rate_limiting(client: AsyncClient):
    # Make requests until rate limited
    for i in range(10):
        response = await client.post(
            "/auth/login",
            json={"email": "test@test.com", "password": "wrong"},
        )
        if response.status_code == 429:
            break

    assert response.status_code == 429
```

---

## 6. Pre-Generation Checklist

**BEFORE generating any FastAPI code:**

- [ ] Pydantic models for all request/response bodies
- [ ] Authentication dependency on protected endpoints
- [ ] Authorization checks (ownership, roles)
- [ ] Parameterized SQL queries (no f-strings)
- [ ] Proper HTTP status codes
- [ ] Rate limiting configured
- [ ] CORS with specific origins
- [ ] Error responses don't leak internals
- [ ] Pagination with max limits
- [ ] Async database sessions

---

**Performance**: Quality over speed. Verify all code examples compile. Never skip security checks. See `template-references/performance-notes.md` for full guidelines.