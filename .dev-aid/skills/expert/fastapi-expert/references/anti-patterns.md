# FastAPI Anti-Patterns

This document contains common mistakes to avoid when building FastAPI applications.

## Anti-Pattern 1: Not Using async/await

```python
# ❌ DON'T
@app.get("/users")
def get_users():  # Blocking!
    users = db.query(User).all()
    return users

# ✅ DO
@app.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()
```

**Why Better**: Async operations prevent blocking the event loop, allowing FastAPI to handle many concurrent requests efficiently.

## Anti-Pattern 2: Exposing Sensitive Data

```python
# ❌ DON'T
@app.get("/users/{id}")
async def get_user(id: int):
    return user  # Exposes password_hash!

# ✅ DO
@app.get("/users/{id}", response_model=UserResponse)
async def get_user(id: int):
    return user  # Pydantic filters fields
```

**Why Better**: Response models ensure only intended fields are exposed, preventing accidental leakage of sensitive data like password hashes, tokens, or secrets.

## Anti-Pattern 3: Missing Input Validation

```python
# ❌ DON'T
@app.post("/users")
async def create_user(data: dict):  # No validation!
    pass

# ✅ DO
@app.post("/users")
async def create_user(user_in: UserCreate):  # Validated!
    pass
```

**Why Better**: Pydantic models validate all inputs automatically, preventing invalid data from entering your system and providing clear error messages.

## Anti-Pattern 4: Weak Password Hashing

```python
# ❌ DON'T
import hashlib
hash = hashlib.md5(password.encode()).hexdigest()  # INSECURE!

# ✅ DO
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"])
hash = pwd_context.hash(password)
```

**Why Better**: bcrypt is designed for password hashing with adaptive cost factors, making it resistant to brute-force attacks. MD5/SHA1 are cryptographically broken for password storage.

## Anti-Pattern 5: No Rate Limiting

```python
# ❌ DON'T
@app.post("/login")
async def login():  # Vulnerable to brute force!
    pass

# ✅ DO
@app.post("/login")
@limiter.limit("5/minute")
async def login(request: Request):
    pass
```

**Why Better**: Rate limiting prevents brute-force attacks on authentication endpoints and protects against API abuse.

## Anti-Pattern 6: Improper Error Handling

```python
# ❌ DON'T
@app.get("/users/{id}")
async def get_user(id: int):
    return user.data  # Can raise AttributeError

# ✅ DO
@app.get("/users/{id}")
async def get_user(id: int):
    if not user:
        raise HTTPException(404, "User not found")
    return user
```

**Why Better**: Explicit error handling provides clear, consistent error responses and prevents exposing internal implementation details through exception messages.

## Anti-Pattern 7: Not Using Dependency Injection

```python
# ❌ DON'T
@app.get("/protected")
async def route(token: str):
    # Manually verify token every time
    user = verify_token(token)
    if not user:
        raise HTTPException(401)

# ✅ DO
@app.get("/protected")
async def route(user: User = Depends(get_current_user)):
    # Authentication handled by dependency
    pass
```

**Why Better**: Dependency injection centralizes authentication logic, reduces code duplication, and makes testing easier through dependency overrides.
