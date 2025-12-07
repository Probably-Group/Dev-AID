## 7. Implementation Patterns

### Pattern 1: Origin Validation (Critical for CSWSH Prevention)

```python
from fastapi import WebSocket

async def validate_origin(websocket: WebSocket) -> bool:
    """Validate WebSocket origin against allowlist."""
    origin = websocket.headers.get("origin")
    if not origin or origin not in ALLOWED_ORIGINS:
        await websocket.close(code=4003, reason="Invalid origin")
        return False
    return True

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    if not await validate_origin(websocket):
        return
    await websocket.accept()
```

### Pattern 2: Token-Based Authentication

```python
from jose import jwt, JWTError

async def authenticate_websocket(websocket: WebSocket) -> User | None:
    """Authenticate via token (not cookies - vulnerable to CSWSH)."""
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Authentication required")
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user = await user_service.get(payload.get("sub"))
        if not user:
            await websocket.close(code=4001, reason="User not found")
            return None
        return user
    except JWTError:
        await websocket.close(code=4001, reason="Invalid token")
        return None
```

### Pattern 3: Per-Message Authorization

```python
from pydantic import BaseModel, field_validator

class WebSocketMessage(BaseModel):
    action: str
    data: dict

    @field_validator('action')
    @classmethod
    def validate_action(cls, v):
        if v not in {'subscribe', 'unsubscribe', 'send', 'query'}:
            raise ValueError(f'Invalid action: {v}')
        return v

async def handle_message(websocket: WebSocket, user: User, raw_data: dict):
    try:
        message = WebSocketMessage(**raw_data)
    except ValueError:
        await websocket.send_json({"error": "Invalid message format"})
        return

    if not user.has_permission(f"ws:{message.action}"):
        await websocket.send_json({"error": "Permission denied"})
        return

    result = await handlers[message.action](user, message.data)
    await websocket.send_json(result)
```

### Pattern 4: Connection Manager with Rate Limiting

```python
from collections import defaultdict
from time import time

class SecureConnectionManager:
    def __init__(self):
        self.connections: dict[str, WebSocket] = {}
        self.message_counts: dict[str, list[float]] = defaultdict(list)
        self.connections_per_ip: dict[str, int] = defaultdict(int)

    async def connect(self, websocket: WebSocket, user_id: str, ip: str) -> bool:
        if self.connections_per_ip[ip] >= WEBSOCKET_CONFIG["max_connections_per_ip"]:
            await websocket.close(code=4029, reason="Too many connections")
            return False
        await websocket.accept()
        self.connections[user_id] = websocket
        self.connections_per_ip[ip] += 1
        return True

    def check_rate_limit(self, user_id: str) -> bool:
        now = time()
        self.message_counts[user_id] = [
            ts for ts in self.message_counts[user_id] if ts > now - 60
        ]
        if len(self.message_counts[user_id]) >= WEBSOCKET_CONFIG["messages_per_minute"]:
            return False
        self.message_counts[user_id].append(now)
        return True
```

### Pattern 5: Complete Secure Handler

```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    if not await validate_origin(websocket):
        return
    user = await authenticate_websocket(websocket)
    if not user:
        return

    ip = websocket.client.host
    if not await manager.connect(websocket, user.id, ip):
        return

    try:
        while True:
            raw = await asyncio.wait_for(
                websocket.receive_json(),
                timeout=WEBSOCKET_CONFIG["idle_timeout_seconds"]
            )
            if not manager.check_rate_limit(user.id):
                await websocket.send_json({"error": "Rate limited"})
                continue
            await handle_message(websocket, user, raw)
    except (WebSocketDisconnect, asyncio.TimeoutError):
        pass
    finally:
        manager.disconnect(user.id, ip)
```

---

