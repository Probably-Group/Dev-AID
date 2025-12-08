## 5. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```python
import pytest
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient

# Test security boundaries first
@pytest.mark.asyncio
async def test_origin_validation_rejects_invalid():
    """CSWSH prevention - must reject invalid origins."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver"
    ) as client:
        # This should fail until origin validation is implemented
        with pytest.raises(Exception):
            async with client.websocket_connect(
                "/ws?token=valid",
                headers={"Origin": "https://evil.com"}
            ):
                pass

@pytest.mark.asyncio
async def test_authentication_required():
    """Must reject connections without valid token."""
    with TestClient(app) as client:
        with pytest.raises(Exception):
            with client.websocket_connect("/ws") as ws:
                pass

@pytest.mark.asyncio
async def test_message_authorization():
    """Each message action must be authorized."""
    with TestClient(app) as client:
        with client.websocket_connect(
            "/ws?token=readonly_user",
            headers={"Origin": "https://app.example.com"}
        ) as ws:
            ws.send_json({"action": "delete", "id": "123"})
            response = ws.receive_json()
            assert response.get("error") == "Permission denied"
```

### Step 2: Implement Minimum to Pass

```python
# Implement only what's needed to pass the test
async def validate_origin(websocket: WebSocket) -> bool:
    origin = websocket.headers.get("origin")
    if not origin or origin not in ALLOWED_ORIGINS:
        await websocket.close(code=4003, reason="Invalid origin")
        return False
    return True
```

### Step 3: Refactor and Verify

```bash
# Run all WebSocket tests
pytest tests/websocket/ -v --asyncio-mode=auto

# Check for security issues
bandit -r src/websocket/

# Verify no regressions
pytest tests/ -v
```

---

