## 6. Implementation Workflow (TDD)

### Step-by-Step TDD Process

Follow this workflow for every API endpoint:

#### Step 1: Write Failing Test First

```python
# tests/test_users_api.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_user_returns_201():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/users", json={"name": "John", "email": "john@example.com"})
    assert response.status_code == 201
    assert "id" in response.json()["data"]

@pytest.mark.asyncio
async def test_create_user_validates_email():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/users", json={"name": "John", "email": "invalid"})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_get_user_requires_auth():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/users/123")
    assert response.status_code == 401
```

#### Step 2: Implement Minimum to Pass

```python
# app/routers/users.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/api/v1/users", tags=["users"])

class CreateUserRequest(BaseModel):
    name: str
    email: EmailStr

@router.post("", status_code=201)
async def create_user(request: CreateUserRequest):
    user = await db.users.create(request.model_dump())
    return {"data": {"id": user.id, "name": user.name, "email": user.email}}
```

#### Step 3: Refactor and Add Edge Cases

```python
@pytest.mark.asyncio
async def test_get_user_prevents_bola():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/users/other-id", headers={"Authorization": f"Bearer {user_a_token}"})
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_list_users_pagination():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/users?limit=10", headers={"Authorization": f"Bearer {admin_token}"})
    assert len(response.json()["data"]) <= 10
```

#### Step 4: Run Full Verification

```bash
# Run all tests
pytest tests/test_users_api.py -v

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Run security-focused tests
pytest -m security -v
```

---

