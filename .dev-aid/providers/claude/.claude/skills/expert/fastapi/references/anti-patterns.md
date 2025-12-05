# FastAPI Anti-Patterns and Common Mistakes

## Security Anti-Patterns

### Anti-Pattern 1: Permissive CORS

**Problem**: Allowing all origins with credentials creates CSRF vulnerabilities.

**Bad Example**:
```python
# NEVER DO THIS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True
)
```

**Why It's Bad**:
- Any website can make authenticated requests to your API
- Opens CSRF attack vectors
- Violates CORS security model

**Good Example**:
```python
# ALWAYS specify allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app.example.com",
        "https://admin.example.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"]
)
```

**Better Approach**:
- Whitelist specific origins
- Use environment variables for different environments
- Never use `["*"]` with `allow_credentials=True`

---

### Anti-Pattern 2: No Rate Limiting

**Problem**: Endpoints without rate limiting are vulnerable to brute force and DoS attacks.

**Bad Example**:
```python
# NEVER - allows unlimited login attempts
@app.post("/login")
async def login(credentials: LoginRequest):
    user = await authenticate(credentials)
    return {"token": create_token(user)}
```

**Why It's Bad**:
- Allows brute force password attacks
- Enables account enumeration
- Can cause DoS through resource exhaustion

**Good Example**:
```python
# ALWAYS rate limit authentication endpoints
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/login")
@limiter.limit("5/minute")  # Strict for auth
async def login(request: Request, credentials: LoginRequest):
    user = await authenticate(credentials)
    return {"token": create_token(user)}

@app.get("/data")
@limiter.limit("100/minute")  # More permissive for data
async def get_data(request: Request):
    return await fetch_data()
```

---

### Anti-Pattern 3: Exposing Docs in Production

**Problem**: API documentation can reveal internal structure and security weaknesses.

**Bad Example**:
```python
# NEVER - docs always available
app = FastAPI()
# Default docs_url="/docs" and redoc_url="/redoc"
```

**Why It's Bad**:
- Exposes all endpoints and schemas to attackers
- Reveals internal implementation details
- Can expose test/debug endpoints

**Good Example**:
```python
# ALWAYS disable docs in production
import os

PRODUCTION = os.environ.get("ENV") == "production"

app = FastAPI(
    docs_url=None if PRODUCTION else "/docs",
    redoc_url=None,
    openapi_url=None if PRODUCTION else "/openapi.json"
)
```

---

### Anti-Pattern 4: Weak JWT Configuration

**Problem**: Weak secrets and algorithms compromise token security.

**Bad Example**:
```python
# NEVER - weak secret and algorithm
SECRET_KEY = "secret123"  # Hardcoded, weak
jwt.encode(data, SECRET_KEY, algorithm="none")  # No signature!
```

**Why It's Bad**:
- Hardcoded secrets in source control
- Weak secrets can be brute forced
- `none` algorithm allows unsigned tokens
- `HS256` with weak secret is vulnerable

**Good Example**:
```python
# ALWAYS use strong secrets from environment
import os
from jose import jwt

# Load from environment or secrets manager
SECRET_KEY = os.environ["JWT_SECRET"]  # 32+ character random string
ALGORITHM = "RS256"  # Asymmetric is better for distributed systems

# For HS256, ensure strong secret
# openssl rand -hex 32

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(401, "Invalid token")
```

---

### Anti-Pattern 5: File Extension Validation Only

**Problem**: Validating files by extension can be bypassed.

**Bad Example**:
```python
# NEVER - only checks filename
@app.post("/upload")
async def upload_file(file: UploadFile):
    if not file.filename.endswith(('.jpg', '.png')):
        raise HTTPException(400, "Only images allowed")

    # Attacker uploads malware.php.jpg
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
```

**Why It's Bad**:
- Extensions can be spoofed
- Doesn't validate actual file content
- Can lead to malware upload and execution

**Good Example**:
```python
# ALWAYS check magic bytes
import magic
from pathlib import Path
from uuid import uuid4

ALLOWED_TYPES = {"image/jpeg", "image/png", "application/pdf"}
MAX_SIZE = 10 * 1024 * 1024  # 10MB

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Read content
    content = await file.read()

    # Check size
    if len(content) > MAX_SIZE:
        raise HTTPException(400, "File too large")

    # Validate by magic bytes, not extension
    mime_type = magic.from_buffer(content, mime=True)
    if mime_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"File type not allowed: {mime_type}")

    # Generate safe filename (don't trust user input)
    safe_name = f"{uuid4()}{Path(file.filename).suffix}"

    # Store outside webroot
    file_path = UPLOAD_DIR / safe_name
    file_path.write_bytes(content)

    return {"filename": safe_name}
```

---

## Performance Anti-Patterns

### Anti-Pattern 6: Blocking I/O in Async Functions

**Bad Example**:
```python
# NEVER - blocks event loop
@app.get("/data")
async def get_data():
    # Using synchronous requests in async function
    response = requests.get("https://api.example.com/data")
    return response.json()
```

**Why It's Bad**:
- Blocks the event loop
- Prevents other requests from being processed
- Defeats purpose of async FastAPI

**Good Example**:
```python
# ALWAYS use async libraries
import httpx

@app.get("/data")
async def get_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
        return response.json()
```

---

### Anti-Pattern 7: No Database Connection Pooling

**Bad Example**:
```python
# NEVER - creates new connection per request
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
        return user
    finally:
        await conn.close()
```

**Why It's Bad**:
- Overhead of creating connections
- Exhausts database connections under load
- Poor performance

**Good Example**:
```python
# ALWAYS use connection pooling
from contextlib import asynccontextmanager

pool = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global pool
    pool = await asyncpg.create_pool(
        DATABASE_URL,
        min_size=10,
        max_size=50
    )
    yield
    await pool.close()

app = FastAPI(lifespan=lifespan)

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    async with pool.acquire() as conn:
        user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
        return user
```

---

### Anti-Pattern 8: Returning Entire Collections

**Bad Example**:
```python
# NEVER - returns all records
@app.get("/users")
async def list_users():
    users = await db.fetch("SELECT * FROM users")
    return users  # Could be millions of records
```

**Why It's Bad**:
- Memory exhaustion
- Slow response times
- Poor user experience

**Good Example**:
```python
# ALWAYS paginate
from fastapi import Query

@app.get("/users")
async def list_users(
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0)
):
    users = await db.fetch(
        "SELECT * FROM users LIMIT $1 OFFSET $2",
        limit,
        offset
    )
    total = await db.fetchval("SELECT COUNT(*) FROM users")

    return {
        "items": users,
        "total": total,
        "limit": limit,
        "offset": offset
    }
```

---

## Code Quality Anti-Patterns

### Anti-Pattern 9: No Input Validation

**Bad Example**:
```python
# NEVER - accepts any input
@app.post("/users")
async def create_user(data: dict):
    # What fields are required?
    # What are valid values?
    user = await db.execute(
        "INSERT INTO users (username, email) VALUES ($1, $2)",
        data["username"],  # KeyError if missing
        data["email"]
    )
    return user
```

**Good Example**:
```python
# ALWAYS use Pydantic models
from pydantic import BaseModel, Field, EmailStr, field_validator

class UserCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
        pattern=r'^[a-zA-Z0-9_-]+$'
    )
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
    # Input already validated
    hashed_pw = hash_password(user.password)
    created = await db.execute(
        "INSERT INTO users (username, email, password) VALUES ($1, $2, $3)",
        user.username,
        user.email,
        hashed_pw
    )
    return created
```

---

### Anti-Pattern 10: Leaking Internal Errors

**Bad Example**:
```python
# NEVER - exposes internal details
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await db.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
    return user  # Returns None if not found, or crashes with DB error
```

**Why It's Bad**:
- Exposes database schema in errors
- Reveals implementation details
- Poor user experience

**Good Example**:
```python
# ALWAYS handle errors gracefully
from fastapi import HTTPException

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    # Log full details internally
    logger.error(f"Unhandled error: {exc}", exc_info=True)

    # Return safe message to client
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    try:
        user = await db.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
        if not user:
            raise HTTPException(404, "User not found")
        return user
    except asyncpg.PostgresError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(500, "Failed to retrieve user")
```

---

### Anti-Pattern 11: No Type Hints

**Bad Example**:
```python
# NEVER - no type safety
@app.post("/items")
async def create_item(data):
    item = await process_item(data)
    return item
```

**Good Example**:
```python
# ALWAYS use type hints
from typing import Annotated

@app.post("/items")
async def create_item(
    item: Annotated[ItemCreate, Body(...)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> ItemResponse:
    created = await item_service.create(item, current_user.id)
    return ItemResponse.from_orm(created)
```

---

## Testing Anti-Patterns

### Anti-Pattern 12: No Tests

**Bad Example**:
```python
# Just writing code without tests
@app.post("/items")
async def create_item(item: ItemCreate):
    return await item_service.create(item)
```

**Good Example**:
```python
# Test-Driven Development
# 1. Write test first
@pytest.mark.asyncio
async def test_create_item():
    async with AsyncClient(app=app) as client:
        response = await client.post("/items", json={
            "name": "Test",
            "price": 10
        })
        assert response.status_code == 201

# 2. Then implement
@app.post("/items", status_code=201)
async def create_item(item: ItemCreate):
    return await item_service.create(item)
```

---

## Quick Reference: Always Do / Never Do

### Always Do:
- ✅ Use Pydantic models for validation
- ✅ Rate limit all endpoints
- ✅ Use async libraries (httpx, asyncpg, motor)
- ✅ Implement connection pooling
- ✅ Paginate large datasets
- ✅ Write tests first (TDD)
- ✅ Handle errors gracefully
- ✅ Use type hints
- ✅ Validate by magic bytes, not extensions
- ✅ Load secrets from environment
- ✅ Disable docs in production
- ✅ Use security headers middleware

### Never Do:
- ❌ Wildcard CORS with credentials
- ❌ Skip rate limiting
- ❌ Expose docs in production
- ❌ Hardcode secrets
- ❌ Validate files by extension only
- ❌ Block event loop with sync I/O
- ❌ Skip connection pooling
- ❌ Return entire collections
- ❌ Skip input validation
- ❌ Leak internal errors
- ❌ Skip type hints
- ❌ Skip tests
