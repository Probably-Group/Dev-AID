# FastAPI Testing Guide

## TDD Workflow

### Step 1: Write Failing Test First

Always start with tests that define expected behavior:

```python
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_create_item_success():
    """Test successful item creation with valid data."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/items",
            json={"name": "Test Item", "price": 29.99},
            headers={"Authorization": "Bearer valid_token"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Item"
        assert "id" in data

@pytest.mark.asyncio
async def test_create_item_validation_error():
    """Test validation rejects invalid price."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/items",
            json={"name": "Test", "price": -10},
            headers={"Authorization": "Bearer valid_token"}
        )
        assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_item_unauthorized():
    """Test endpoint requires authentication."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/items", json={"name": "Test", "price": 10})
        assert response.status_code == 401
```

### Step 2: Implement Minimum to Pass

Write only the code needed to make tests pass:

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

Improve code quality while keeping tests green. Extract common patterns, improve naming, optimize queries.

### Step 4: Run Full Verification

```bash
# Run all tests with coverage
pytest --cov=app --cov-report=term-missing

# Type checking
mypy app --strict

# Security scan
bandit -r app -ll

# All must pass before committing
```

---

## Test Configuration

### conftest.py Setup

```python
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.config import get_settings

# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost/test_db"

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()

@pytest.fixture
async def test_db(test_engine):
    """Create test database session."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def client(test_db):
    """Create test client with database override."""
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()

@pytest.fixture
async def authenticated_client(client, test_db):
    """Create authenticated test client."""
    # Create test user
    user = User(username="testuser", email="test@example.com")
    user.hashed_password = hash_password("testpass123")
    test_db.add(user)
    await test_db.commit()

    # Login and get token
    response = await client.post("/token", data={
        "username": "testuser",
        "password": "testpass123"
    })
    token = response.json()["access_token"]

    # Add token to headers
    client.headers["Authorization"] = f"Bearer {token}"

    yield client
```

---

## Security Tests

### Rate Limiting Tests

```python
def test_rate_limiting():
    """Test rate limiting on login endpoint."""
    client = TestClient(app)

    # Exceed rate limit
    for i in range(10):
        response = client.post("/login", json={
            "username": "test",
            "password": "test"
        })

    # Should return 429 Too Many Requests
    assert response.status_code == 429

def test_rate_limit_per_ip():
    """Test rate limiting is per IP address."""
    client1 = TestClient(app, headers={"X-Forwarded-For": "1.1.1.1"})
    client2 = TestClient(app, headers={"X-Forwarded-For": "2.2.2.2"})

    # Client 1 exceeds limit
    for _ in range(6):
        client1.post("/login", json={"username": "test", "password": "test"})

    # Client 2 should still work
    response = client2.post("/login", json={"username": "test", "password": "test"})
    assert response.status_code in [200, 401]  # Not 429
```

### Authentication Tests

```python
def test_invalid_jwt_rejected():
    """Test invalid JWT is rejected."""
    client = TestClient(app)
    response = client.get(
        "/protected",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    assert response.status_code == 401

def test_expired_jwt_rejected():
    """Test expired JWT is rejected."""
    # Create token that expired 1 hour ago
    expired_token = create_access_token(
        {"sub": "testuser"},
        expires_delta=timedelta(hours=-1)
    )

    client = TestClient(app)
    response = client.get(
        "/protected",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401

def test_missing_auth_rejected():
    """Test requests without auth are rejected."""
    client = TestClient(app)
    response = client.get("/protected")
    assert response.status_code == 401
```

### Input Validation Tests

```python
def test_sql_injection_prevented():
    """Test SQL injection attempts are handled safely."""
    client = TestClient(app)
    response = client.get("/users", params={
        "search": "'; DROP TABLE users; --"
    })
    # Should not cause 500 (SQL error)
    assert response.status_code in [200, 400]

def test_xss_in_input_sanitized():
    """Test XSS payloads are sanitized."""
    client = TestClient(app)
    response = client.post("/items", json={
        "name": "<script>alert('xss')</script>",
        "price": 10
    })
    if response.status_code == 201:
        data = response.json()
        assert "<script>" not in data["name"]

def test_negative_price_rejected():
    """Test validation rejects negative prices."""
    client = TestClient(app)
    response = client.post("/items", json={
        "name": "Test",
        "price": -10
    })
    assert response.status_code == 422
```

### File Upload Security Tests

```python
def test_file_upload_type_validation():
    """Test file upload validates by magic bytes not extension."""
    client = TestClient(app)

    # Try uploading executable disguised as image
    response = client.post(
        "/upload",
        files={
            "file": ("malware.jpg", b"MZ\x90\x00", "image/jpeg")  # EXE magic bytes
        }
    )
    assert response.status_code == 400
    assert "not allowed" in response.json()["detail"].lower()

def test_file_upload_size_limit():
    """Test file upload respects size limits."""
    client = TestClient(app)

    # Create 11MB file (over 10MB limit)
    large_file = b"x" * (11 * 1024 * 1024)

    response = client.post(
        "/upload",
        files={"file": ("large.jpg", large_file, "image/jpeg")}
    )
    assert response.status_code == 400
    assert "too large" in response.json()["detail"].lower()
```

---

## Integration Tests

### Database Integration

```python
@pytest.mark.asyncio
async def test_user_creation_persists(test_db):
    """Test user creation persists to database."""
    user = User(username="testuser", email="test@example.com")
    user.hashed_password = hash_password("password123")

    test_db.add(user)
    await test_db.commit()

    # Verify user exists
    stmt = select(User).where(User.username == "testuser")
    result = await test_db.execute(stmt)
    saved_user = result.scalar_one()

    assert saved_user.username == "testuser"
    assert saved_user.email == "test@example.com"

@pytest.mark.asyncio
async def test_transaction_rollback_on_error(test_db):
    """Test database transactions rollback on errors."""
    user = User(username="testuser", email="test@example.com")
    test_db.add(user)

    try:
        # Cause error by adding duplicate
        duplicate = User(username="testuser", email="test@example.com")
        test_db.add(duplicate)
        await test_db.commit()
        assert False, "Should have raised error"
    except Exception:
        await test_db.rollback()

    # Verify neither user was saved
    stmt = select(User).where(User.username == "testuser")
    result = await test_db.execute(stmt)
    assert result.scalar_one_or_none() is None
```

### External API Integration

```python
@pytest.mark.asyncio
async def test_external_api_integration(client, httpx_mock):
    """Test integration with external API."""
    # Mock external API response
    httpx_mock.add_response(
        url="https://api.example.com/data",
        json={"result": "success"}
    )

    response = await client.get("/external-data")
    assert response.status_code == 200
    assert response.json()["result"] == "success"

@pytest.mark.asyncio
async def test_external_api_timeout_handling(client, httpx_mock):
    """Test handling of external API timeouts."""
    httpx_mock.add_exception(httpx.TimeoutException("Timeout"))

    response = await client.get("/external-data")
    assert response.status_code == 504  # Gateway timeout
```

---

## Mocking and Fixtures

### Mocking Dependencies

```python
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_user_service():
    """Mock user service."""
    mock = AsyncMock()
    mock.get.return_value = User(id=1, username="test", email="test@example.com")
    mock.create.return_value = User(id=1, username="newuser", email="new@example.com")
    return mock

def test_with_mocked_service(client, mock_user_service):
    """Test endpoint with mocked service."""
    app.dependency_overrides[get_user_service] = lambda: mock_user_service

    response = client.get("/users/1")
    assert response.status_code == 200
    assert response.json()["username"] == "test"

    mock_user_service.get.assert_called_once_with(1)

    # Cleanup
    app.dependency_overrides.clear()
```

### Factory Fixtures

```python
import factory
from factory.alchemy import SQLAlchemyModelFactory

class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = None

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    hashed_password = factory.LazyFunction(lambda: hash_password("password123"))

@pytest.fixture
def user_factory(test_db):
    """User factory fixture."""
    UserFactory._meta.sqlalchemy_session = test_db
    return UserFactory

@pytest.mark.asyncio
async def test_with_factory(user_factory):
    """Test using factory fixture."""
    user1 = user_factory.create()
    user2 = user_factory.create()

    assert user1.username != user2.username
    assert "@example.com" in user1.email
```

---

## Coverage and Quality

### Running Tests with Coverage

```bash
# Install coverage tools
pip install pytest-cov

# Run with coverage
pytest --cov=app --cov-report=html --cov-report=term-missing

# Fail if coverage below threshold
pytest --cov=app --cov-fail-under=80
```

### Coverage Configuration

```ini
# .coveragerc
[run]
source = app
omit =
    */tests/*
    */migrations/*
    */__init__.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
```

---

## Testing Checklist

Before deploying:

- [ ] All endpoints have success tests
- [ ] All endpoints have error/validation tests
- [ ] Authentication/authorization tested
- [ ] Rate limiting tested
- [ ] Input validation tested (SQL injection, XSS)
- [ ] File upload security tested
- [ ] Database transactions tested
- [ ] External API integration tested (with mocks)
- [ ] Error handlers tested
- [ ] Coverage > 80%
- [ ] Type checking passes (mypy)
- [ ] Security scan passes (bandit)
