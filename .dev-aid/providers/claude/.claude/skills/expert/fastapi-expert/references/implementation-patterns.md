# FastAPI Implementation Patterns

This document contains detailed implementation patterns for FastAPI applications.

## Pattern 1: FastAPI Application Structure

```python
# app/main.py - Production-ready structure
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url="/api/docs" if settings.ENVIRONMENT != "production" else None,
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Never ["*"] in production!
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

## Pattern 2: Pydantic v2 Models with Validation

```python
from pydantic import BaseModel, Field, EmailStr, field_validator
from pydantic.config import ConfigDict

class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="User email")
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=100)

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        if not any(c in '!@#$%^&*()_+-=' for c in v):
            raise ValueError('Password must contain special character')
        return v

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    username: str
    full_name: str
    is_active: bool
    # ❌ NEVER include: password_hash, tokens, secrets
```

## Pattern 3: Async Database with SQLAlchemy 2.0

```python
# app/db/session.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_recycle=3600,
)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

# app/db/models.py
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Boolean, DateTime
from datetime import datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

# app/crud/user.py
from sqlalchemy import select

async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()
```

## Pattern 4: JWT Authentication with Refresh Tokens

```python
# app/core/security.py
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

# app/api/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None or payload.get("type") != "access":
            raise HTTPException(401, "Invalid credentials")
    except JWTError:
        raise HTTPException(401, "Invalid credentials")

    user = await user_crud.get_user_by_username(db, username)
    if user is None:
        raise HTTPException(401, "User not found")
    return user

# app/api/v1/endpoints/auth.py
@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user = await user_crud.get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(401, "Incorrect username or password")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
```

## Pattern 5: Authorization with Dependency Injection

```python
# Reusable authorization checkers
from typing import List
from fastapi import Depends, HTTPException

class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(403, f"Role '{user.role}' not allowed")
        return user

# Usage in routes
@router.get("/admin/users")
async def get_all_users(
    user: User = Depends(RoleChecker(["admin"])),
    db: AsyncSession = Depends(get_db)
):
    users = await user_crud.get_users(db)
    return users
```

## Pattern 6: Request Validation & Error Handling

```python
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [{
        "field": ".".join(str(x) for x in e["loc"]),
        "message": e["msg"]
    } for e in exc.errors()]

    return JSONResponse(
        status_code=422,
        content={"detail": "Validation failed", "errors": errors}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    if settings.ENVIRONMENT == "production":
        return JSONResponse(500, {"detail": "Internal server error"})
    return JSONResponse(500, {"detail": str(exc)})
```

## Pattern 7: Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post("/auth/login")
@limiter.limit("5/minute")  # Prevent brute force
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    # Login logic
    pass
```

## Pattern 8: Background Tasks

```python
from fastapi import BackgroundTasks

async def send_welcome_email(email: str, username: str):
    # Non-blocking email sending
    await email_service.send(to=email, subject="Welcome", body=f"Hi {username}")

@router.post("/register")
async def register_user(
    user_in: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    user = await user_crud.create_user(db, user_in)
    background_tasks.add_task(send_welcome_email, user.email, user.username)
    return user
```

## Pattern 9: Testing with pytest

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import get_db

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

# tests/test_users.py
def test_create_user(client):
    response = client.post("/api/v1/users/", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "Test123!@#",
        "full_name": "Test User"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "password" not in data  # Never expose password

def test_login(client):
    response = client.post("/api/v1/auth/login",
        data={"username": "testuser", "password": "Test123!@#"})
    assert response.status_code == 200
    assert "access_token" in response.json()
```

## Pattern 10: Configuration Management

```python
# app/core/config.py
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI App"
    ENVIRONMENT: str = "development"
    SECRET_KEY: str  # MUST be set in .env
    DATABASE_URL: str
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"

settings = Settings()

# Validate production settings
if settings.ENVIRONMENT == "production":
    assert len(settings.SECRET_KEY) >= 32
    assert "*" not in settings.CORS_ORIGINS
```
