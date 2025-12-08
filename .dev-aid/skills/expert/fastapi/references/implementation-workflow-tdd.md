## 6. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```python
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_create_item_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
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

