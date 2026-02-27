---
name: fastapi-expert
version: 2.0.0
description: "Production FastAPI applications with OAuth2/JWT authentication, Pydantic v2 validation, SQLAlchemy 2.0 async patterns, and middleware configuration. Use when building authenticated APIs, implementing database models with SQLAlchemy 2.0, configuring OAuth2 flows, or optimizing async endpoint performance. Do NOT use for Django, Flask, or GraphQL API development (use graphql-expert)."
compatibility: "Python 3.11+, FastAPI 0.115+, SQLAlchemy 2.0+, Pydantic 2.5+"
risk_level: HIGH
token_budget: 2500
---
# FastAPI Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.2 Security Patterns (security rules)

**CWE-89: SQL Injection**
- Do not: `text(f"SELECT * FROM users WHERE id = {id}")`
- Instead: `select(User).where(User.id == bindparam('id'))`

**CWE-285: Improper Authorization**
- Do not: `async def get_item(user_id: int)` - trusting client-provided ID
- Instead: `async def get_item(current_user: User = Depends(get_current_user))`

**CWE-522: Weak Password Storage**
- Do not: Store plaintext passwords or use MD5/SHA1
- Instead: `passlib.hash.bcrypt.hash(password)` with cost factor ≥12

**CWE-614: Missing Secure Cookie Flag**
- Do not: Session cookies without secure flags
- Instead: `response.set_cookie(key, value, httponly=True, secure=True, samesite="lax")`

**CWE-918: SSRF**
- Do not: `httpx.get(user_provided_url)` without validation
- Instead: Allowlist domains, block private IP ranges (10.x, 172.16.x, 192.168.x)

---

## 1. Version Requirements

**ALWAYS USE these minimum versions:**
```
fastapi>=0.115.3
starlette>=0.49.1
pydantic>=2.5.0
sqlalchemy>=2.0.0
python>=3.11
```

**WHEN generating requirements.txt or pyproject.toml** → pin these exact versions or higher.

---

## 2. Security Rules (CVE-Driven)

### 2.1 File Uploads & Multipart Forms

**NEVER** accept unbounded file uploads (CVE-2024-47874, CVE-2025-54121):
```python
# ❌ WRONG - No size limit
@router.post("/upload")
async def upload(file: UploadFile):
    contents = await file.read()

# ✅ CORRECT - Always limit size
from fastapi import UploadFile, HTTPException

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/upload")
async def upload(file: UploadFile):
    contents = await file.read(MAX_FILE_SIZE + 1)
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(413, "File too large")
```

### 2.2 Static File Serving

**NEVER** serve files from user-controlled paths (GHSA-v5gw-mw7f-84px):
```python
# ❌ WRONG - Path traversal possible
@router.get("/files/{filename}")
async def get_file(filename: str):
    return FileResponse(f"uploads/{filename}")

# ✅ CORRECT - Validate and resolve path
from pathlib import Path

UPLOAD_DIR = Path("uploads").resolve()

@router.get("/files/{filename}")
async def get_file(filename: str):
    file_path = (UPLOAD_DIR / filename).resolve()
    if not file_path.is_relative_to(UPLOAD_DIR):
        raise HTTPException(400, "Invalid path")
    if not file_path.exists():
        raise HTTPException(404)
    return FileResponse(file_path)
```

### 2.3 SQL Queries

**NEVER** use f-strings or .format() in SQL (CWE-89):
```python
# ❌ WRONG - SQL injection
query = f"SELECT * FROM users WHERE id = {user_id}"
await db.execute(text(query))

# ✅ CORRECT - Parameterized query
from sqlalchemy import select
result = await db.execute(select(User).where(User.id == user_id))

# ✅ CORRECT - If raw SQL needed
from sqlalchemy import text
result = await db.execute(text("SELECT * FROM users WHERE id = :id"), {"id": user_id})
```

### 2.4 Object Authorization (BOLA Prevention)

**ALWAYS** verify ownership before returning objects (CWE-639):
```python
# ❌ WRONG - Returns any user's data
@router.get("/orders/{order_id}")
async def get_order(order_id: int, db: AsyncSession = Depends(get_db)):
    return await db.get(Order, order_id)

# ✅ CORRECT - Verify ownership
@router.get("/orders/{order_id}")
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    order = await db.get(Order, order_id)
    if not order or order.user_id != current_user.id:
        raise HTTPException(404)
    return order
```

### 2.5 Input Validation

**ALWAYS** constrain string lengths and numeric ranges:
```python
# ❌ WRONG - Unbounded input
class UserCreate(BaseModel):
    username: str
    bio: str

# ✅ CORRECT - Constrained input
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    bio: str = Field(max_length=500)
    age: int = Field(ge=0, le=150)
```

---

## 3. Code Patterns

### 3.1 WHEN creating a new endpoint

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/items", tags=["items"])

class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)

class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    model_config = {"from_attributes": True}

@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item_in: ItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    item = Item(**item_in.model_dump(), owner_id=current_user.id)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item
```

### 3.2 WHEN implementing authentication

```python
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

SECRET_KEY = os.environ["SECRET_KEY"]  # NEVER hardcode
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(user_id), "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
    except (JWTError, ValueError, KeyError):
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
```

### 3.3 WHEN setting up database session

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

DATABASE_URL = os.environ["DATABASE_URL"]  # NEVER hardcode

engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### 3.4 WHEN adding CORS

```python
# ❌ WRONG - Allows all origins
app.add_middleware(CORSMiddleware, allow_origins=["*"])

# ✅ CORRECT - Explicit origins
from fastapi.middleware.cors import CORSMiddleware

ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # ["https://app.example.com"]
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### 3.5 WHEN implementing rate limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, credentials: LoginRequest):
    # ... login logic
```

---

## 4. Async Rules

**ALWAYS** use async for I/O operations:
```python
# ❌ WRONG - Blocking call
import requests
response = requests.get(url)

# ✅ CORRECT - Async HTTP
import httpx
async with httpx.AsyncClient() as client:
    response = await client.get(url)

# ❌ WRONG - Sync database
result = db.query(User).filter(User.id == user_id).first()

# ✅ CORRECT - Async database
from sqlalchemy import select
result = await db.execute(select(User).where(User.id == user_id))
user = result.scalar_one_or_none()
```

**WHEN running CPU-bound tasks** → use run_in_executor:
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)

async def process_image(image_data: bytes):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, cpu_intensive_function, image_data)
    return result
```

---

## 5. Error Handling

**ALWAYS** use structured error responses:
```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse

# Custom exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log full error internally
    logger.exception("Unhandled exception")
    # Return safe message to client
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# ❌ WRONG - Exposes internals
raise HTTPException(500, f"Database error: {str(e)}")

# ✅ CORRECT - Safe message
logger.error(f"Database error: {e}")
raise HTTPException(500, "Failed to process request")
```

---

## 6. Testing Pattern

**ALWAYS** write tests before implementation:
```python
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
# ... (additional test cases follow same pattern)
```

---

## 7. Pre-Commit Checklist

Before generating any FastAPI code, verify:

- [ ] All user inputs have Pydantic validation with Field constraints
- [ ] All database queries use parameterized statements
- [ ] All file operations validate paths against traversal
- [ ] All protected endpoints have Depends(get_current_user)
- [ ] All object access verifies ownership (BOLA prevention)
- [ ] CORS uses explicit origins, not "*"
- [ ] Secrets come from environment variables, not hardcoded
- [ ] Error messages don't expose internal details
- [ ] All I/O uses async/await

---
