# API Testing Guide

Comprehensive guide to testing APIs with Test-Driven Development (TDD) approach.

## Table of Contents
- [TDD Workflow](#tdd-workflow)
- [Setting Up Test Environment](#setting-up-test-environment)
- [Unit Testing API Endpoints](#unit-testing-api-endpoints)
- [Integration Testing](#integration-testing)
- [Contract Testing](#contract-testing)
- [Load Testing](#load-testing)
- [Security Testing](#security-testing)
- [Testing Best Practices](#testing-best-practices)

---

## TDD Workflow

### Step 1: Write Failing Test First

```python
# tests/test_users_api.py
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

@pytest.mark.asyncio
async def test_create_user_returns_201(client):
    response = await client.post(
        "/v1/users",
        json={"email": "test@example.com", "name": "Test"},
        headers={"Authorization": "Bearer token"}
    )
    assert response.status_code == 201
    assert "location" in response.headers
    assert "password" not in response.json()  # Never expose sensitive fields

@pytest.mark.asyncio
async def test_create_user_validates_email(client):
    response = await client.post(
        "/v1/users",
        json={"email": "invalid", "name": "Test"},
        headers={"Authorization": "Bearer token"}
    )
    assert response.status_code == 422
    assert "errors" in response.json()  # RFC 7807 format

@pytest.mark.asyncio
async def test_get_other_user_returns_403(client):
    """BOLA protection - users can't access other users' data."""
    response = await client.get(
        "/v1/users/other-id",
        headers={"Authorization": "Bearer user-token"}
    )
    assert response.status_code == 403
```

### Step 2: Implement Minimum to Pass

```python
# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, Response

router = APIRouter(prefix="/v1/users", tags=["users"])

@router.post("", status_code=201, response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    response: Response,
    current_user = Depends(get_current_user)
):
    user = await user_service.create(user_data)
    response.headers["Location"] = f"/v1/users/{user.id}"
    return user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, current_user = Depends(get_current_user)):
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden")  # BOLA protection
    return await user_service.get(user_id)
```

### Step 3: Refactor and Add Edge Cases

Add tests for rate limiting, pagination, error scenarios, then refactor.

```python
@pytest.mark.asyncio
async def test_rate_limiting(client):
    """Test rate limiting on login endpoint."""
    for _ in range(5):
        response = await client.post(
            "/v1/auth/login",
            json={"email": "test@example.com", "password": "wrong"}
        )

    # 6th request should be rate limited
    response = await client.post(
        "/v1/auth/login",
        json={"email": "test@example.com", "password": "wrong"}
    )
    assert response.status_code == 429
    assert "retry_after" in response.json()

@pytest.mark.asyncio
async def test_pagination_cursor(client):
    """Test cursor-based pagination."""
    response = await client.get("/v1/users?limit=10")
    data = response.json()

    assert len(data["data"]) <= 10
    assert "pagination" in data
    assert "next_cursor" in data["pagination"]

    # Test next page
    if data["pagination"]["next_cursor"]:
        response = await client.get(
            f"/v1/users?limit=10&cursor={data['pagination']['next_cursor']}"
        )
        assert response.status_code == 200
```

### Step 4: Run Full Verification

```bash
# Run all API tests with coverage
pytest tests/ -v --cov=app --cov-report=term-missing

# Validate OpenAPI spec
openapi-spec-validator openapi.yaml

# Security scan
bandit -r app/

# Lint code
pylint app/
flake8 app/
```

---

## Setting Up Test Environment

### Python (FastAPI/Flask)

```python
# conftest.py
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import init_db, cleanup_db

@pytest.fixture(scope="session")
async def test_db():
    """Initialize test database once per test session."""
    await init_db("test_database")
    yield
    await cleanup_db("test_database")

@pytest.fixture
async def client(test_db):
    """Create test client for each test."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

@pytest.fixture
def auth_headers(user_token):
    """Helper for authenticated requests."""
    return {"Authorization": f"Bearer {user_token}"}
```

### JavaScript (Express/NestJS)

```javascript
// test/setup.js
const request = require('supertest');
const app = require('../src/app');
const db = require('../src/database');

beforeAll(async () => {
  // Set up test database
  await db.connect(process.env.TEST_DATABASE_URL);
  await db.migrate();
});

afterAll(async () => {
  // Clean up
  await db.cleanup();
  await db.disconnect();
});

afterEach(async () => {
  // Clear data between tests
  await db.truncate();
});

module.exports = { request: request(app) };
```

---

## Unit Testing API Endpoints

### Testing CRUD Operations

```javascript
// test/users.test.js
const { request } = require('./setup');

describe('Users API', () => {
  let authToken;
  let userId;

  beforeEach(async () => {
    // Create test user and get auth token
    const loginResponse = await request
      .post('/v1/auth/login')
      .send({ email: 'test@example.com', password: 'Test123!' });
    authToken = loginResponse.body.access_token;
  });

  describe('POST /v1/users', () => {
    it('should create a new user', async () => {
      const response = await request
        .post('/v1/users')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          email: 'newuser@example.com',
          name: 'New User',
          password: 'SecurePass123!'
        });

      expect(response.status).toBe(201);
      expect(response.headers.location).toBeDefined();
      expect(response.body).toHaveProperty('id');
      expect(response.body).not.toHaveProperty('password');
      expect(response.body.email).toBe('newuser@example.com');

      userId = response.body.id;
    });

    it('should reject invalid email', async () => {
      const response = await request
        .post('/v1/users')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          email: 'invalid-email',
          name: 'Test User',
          password: 'SecurePass123!'
        });

      expect(response.status).toBe(422);
      expect(response.body.errors).toBeDefined();
      expect(response.body.errors[0].field).toBe('email');
    });

    it('should reject duplicate email', async () => {
      await request
        .post('/v1/users')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          email: 'duplicate@example.com',
          name: 'User 1',
          password: 'SecurePass123!'
        });

      const response = await request
        .post('/v1/users')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          email: 'duplicate@example.com',
          name: 'User 2',
          password: 'SecurePass123!'
        });

      expect(response.status).toBe(409);
      expect(response.body.type).toContain('duplicate');
    });
  });

  describe('GET /v1/users/:id', () => {
    it('should get user by id', async () => {
      const response = await request
        .get(`/v1/users/${userId}`)
        .set('Authorization', `Bearer ${authToken}`);

      expect(response.status).toBe(200);
      expect(response.body.id).toBe(userId);
    });

    it('should return 404 for non-existent user', async () => {
      const response = await request
        .get('/v1/users/nonexistent-id')
        .set('Authorization', `Bearer ${authToken}`);

      expect(response.status).toBe(404);
    });

    it('should return 403 when accessing other user', async () => {
      // Create another user
      const otherUser = await createTestUser('other@example.com');

      const response = await request
        .get(`/v1/users/${otherUser.id}`)
        .set('Authorization', `Bearer ${authToken}`);

      expect(response.status).toBe(403);
    });
  });

  describe('PUT /v1/users/:id', () => {
    it('should update user', async () => {
      const response = await request
        .put(`/v1/users/${userId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .send({ name: 'Updated Name' });

      expect(response.status).toBe(200);
      expect(response.body.name).toBe('Updated Name');
    });

    it('should prevent updating admin flag', async () => {
      const response = await request
        .put(`/v1/users/${userId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .send({ is_admin: true });

      expect(response.status).toBe(400);
    });
  });

  describe('DELETE /v1/users/:id', () => {
    it('should require admin role', async () => {
      const response = await request
        .delete(`/v1/users/${userId}`)
        .set('Authorization', `Bearer ${authToken}`);

      expect(response.status).toBe(403);
    });

    it('should delete user as admin', async () => {
      const adminToken = await getAdminToken();

      const response = await request
        .delete(`/v1/users/${userId}`)
        .set('Authorization', `Bearer ${adminToken}`);

      expect(response.status).toBe(204);

      // Verify deletion
      const getResponse = await request
        .get(`/v1/users/${userId}`)
        .set('Authorization', `Bearer ${adminToken}`);

      expect(getResponse.status).toBe(404);
    });
  });
});
```

---

## Integration Testing

### Testing with Real Database

```python
# tests/integration/test_users_integration.py
import pytest
from httpx import AsyncClient
from app.database import get_db

@pytest.mark.integration
async def test_user_creation_flow(client: AsyncClient, test_db):
    """Test complete user creation and retrieval flow."""

    # 1. Register user
    register_response = await client.post("/v1/auth/register", json={
        "email": "integration@example.com",
        "password": "SecurePass123!",
        "name": "Integration Test"
    })
    assert register_response.status_code == 201
    user_id = register_response.json()["id"]

    # 2. Login
    login_response = await client.post("/v1/auth/login", json={
        "email": "integration@example.com",
        "password": "SecurePass123!"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # 3. Get user profile
    profile_response = await client.get(
        f"/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert profile_response.status_code == 200
    assert profile_response.json()["email"] == "integration@example.com"

    # 4. Update profile
    update_response = await client.patch(
        f"/v1/users/{user_id}",
        json={"name": "Updated Name"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Name"

    # 5. Verify update persisted in database
    async with get_db() as db:
        user = await db.execute("SELECT name FROM users WHERE id = ?", [user_id])
        assert user[0]["name"] == "Updated Name"
```

---

## Contract Testing

### OpenAPI Validation

```python
# tests/test_openapi_compliance.py
import pytest
from openapi_core import create_spec
from openapi_core.validation.request import openapi_request_validator
from openapi_core.validation.response import openapi_response_validator

@pytest.fixture
def openapi_spec():
    with open("openapi.yaml", "r") as f:
        return create_spec(f.read())

@pytest.mark.parametrize("endpoint,method,data", [
    ("/v1/users", "POST", {"email": "test@example.com", "name": "Test"}),
    ("/v1/users/123", "GET", None),
])
def test_request_matches_openapi_spec(client, openapi_spec, endpoint, method, data):
    """Validate that requests match OpenAPI specification."""
    response = client.request(method, endpoint, json=data)

    # Validate request
    request_validator = openapi_request_validator(openapi_spec)
    request_validator.validate(request)

    # Validate response
    response_validator = openapi_response_validator(openapi_spec)
    response_validator.validate(response)
```

---

## Load Testing

### Using Locust

```python
# locustfile.py
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Login before starting tests."""
        response = self.client.post("/v1/auth/login", json={
            "email": "loadtest@example.com",
            "password": "LoadTest123!"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def list_users(self):
        self.client.get("/v1/users?limit=20", headers=self.headers)

    @task(1)
    def create_user(self):
        self.client.post("/v1/users", json={
            "email": f"user{self.environment.stats.num_requests}@example.com",
            "name": "Load Test User",
            "password": "TestPass123!"
        }, headers=self.headers)

    @task(2)
    def get_user_profile(self):
        self.client.get("/v1/users/me", headers=self.headers)
```

Run with:
```bash
locust -f locustfile.py --host=https://api.example.com
```

---

## Security Testing

### Authentication Tests

```python
@pytest.mark.security
async def test_requires_authentication(client):
    """Test that endpoints require authentication."""
    response = await client.get("/v1/users")
    assert response.status_code == 401

@pytest.mark.security
async def test_rejects_invalid_token(client):
    """Test that invalid tokens are rejected."""
    response = await client.get(
        "/v1/users",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401

@pytest.mark.security
async def test_rejects_expired_token(client, expired_token):
    """Test that expired tokens are rejected."""
    response = await client.get(
        "/v1/users",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401
```

### Authorization Tests (BOLA Prevention)

```python
@pytest.mark.security
async def test_user_cannot_access_other_user_data(client, user1_token, user2_id):
    """Test BOLA protection."""
    response = await client.get(
        f"/v1/users/{user2_id}/orders",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert response.status_code == 403

@pytest.mark.security
async def test_user_cannot_update_other_user(client, user1_token, user2_id):
    """Test that users cannot update other users' data."""
    response = await client.patch(
        f"/v1/users/{user2_id}",
        json={"name": "Hacked"},
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert response.status_code == 403
```

### Input Validation Tests

```python
@pytest.mark.security
async def test_sql_injection_protection(client, auth_headers):
    """Test SQL injection prevention."""
    response = await client.get(
        "/v1/users?email='; DROP TABLE users; --",
        headers=auth_headers
    )
    # Should not crash, should return 400 or empty results
    assert response.status_code in [200, 400]

@pytest.mark.security
async def test_xss_prevention(client, auth_headers):
    """Test XSS prevention in user input."""
    response = await client.post(
        "/v1/users",
        json={
            "email": "xss@example.com",
            "name": "<script>alert('XSS')</script>"
        },
        headers=auth_headers
    )
    # Check that script tags are escaped or rejected
    if response.status_code == 201:
        assert "<script>" not in response.json()["name"]
```

---

## Testing Best Practices

### 1. Test Structure

```python
# Use AAA pattern: Arrange, Act, Assert
async def test_create_user():
    # Arrange: Set up test data
    user_data = {"email": "test@example.com", "name": "Test"}

    # Act: Perform the action
    response = await client.post("/v1/users", json=user_data)

    # Assert: Verify the results
    assert response.status_code == 201
    assert response.json()["email"] == user_data["email"]
```

### 2. Use Fixtures for Setup

```python
@pytest.fixture
def sample_user():
    return {
        "email": "test@example.com",
        "name": "Test User",
        "password": "SecurePass123!"
    }

@pytest.fixture
async def created_user(client, sample_user):
    response = await client.post("/v1/users", json=sample_user)
    return response.json()
```

### 3. Test Edge Cases

```python
@pytest.mark.parametrize("email", [
    "",                          # Empty
    "a" * 256,                   # Too long
    "invalid",                   # Invalid format
    "test@",                     # Incomplete
    "@example.com",              # Missing local part
    None,                        # Null
])
async def test_invalid_email(client, email):
    response = await client.post("/v1/users", json={"email": email})
    assert response.status_code == 422
```

### 4. Mock External Dependencies

```python
from unittest.mock import patch

@patch('app.services.external_api.fetch_data')
async def test_with_mocked_external_api(mock_fetch, client):
    mock_fetch.return_value = {"status": "success"}

    response = await client.get("/v1/data")
    assert response.status_code == 200
```

### 5. Use Test Markers

```python
# Mark slow tests
@pytest.mark.slow
async def test_large_dataset():
    pass

# Mark integration tests
@pytest.mark.integration
async def test_database_integration():
    pass

# Run specific tests
# pytest -m "not slow"
# pytest -m integration
```

---

## Summary

**Test Coverage Checklist**:
- [ ] All CRUD operations tested
- [ ] Authentication and authorization tested
- [ ] Input validation tested
- [ ] Error responses tested (400, 401, 403, 404, 422, 500)
- [ ] Rate limiting tested
- [ ] Pagination tested
- [ ] BOLA protection tested
- [ ] Security vulnerabilities tested (SQL injection, XSS)
- [ ] OpenAPI spec compliance validated
- [ ] Load testing performed

**TDD Benefits**:
- Catch bugs early
- Improve code design
- Document expected behavior
- Enable safe refactoring
- Increase confidence in deployments
