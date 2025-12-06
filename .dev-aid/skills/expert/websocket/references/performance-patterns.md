## 6. Performance Patterns

### Pattern 1: Connection Pooling

```python
# BAD - Create new connection for each request
ws = await create_connection(user_id)  # Expensive!

# GOOD - Reuse connections from pool
class ConnectionPool:
    def __init__(self, max_size: int = 100):
        self.connections: dict[str, WebSocket] = {}

    async def get_or_create(self, user_id: str) -> WebSocket:
        if user_id not in self.connections:
            self.connections[user_id] = await create_connection(user_id)
        return self.connections[user_id]
```

### Pattern 2: Message Batching

```python
# BAD - Send messages one at a time
for item in items:
    await websocket.send_json({"type": "item", "data": item})

# GOOD - Batch messages to reduce overhead
await websocket.send_json({"type": "batch", "data": items[:50]})
```

### Pattern 3: Binary Protocols

```python
# BAD - JSON for high-frequency data (~80 bytes)
await websocket.send_json({"x": 123.456, "y": 789.012, "z": 456.789})

# GOOD - Binary format (20 bytes)
import struct
await websocket.send_bytes(struct.pack('!3f', 123.456, 789.012, 456.789))
```

### Pattern 4: Heartbeat Optimization

```python
# BAD - Fixed frequent heartbeats
HEARTBEAT_INTERVAL = 5  # Every 5 seconds

# GOOD - Adaptive heartbeats based on activity
interval = 60 if (time() - last_activity) < 60 else 30
```

### Pattern 5: Backpressure Handling

```python
# BAD - Blocks on slow clients
await ws.send_json(message)

# GOOD - Timeout and bounded queue
from collections import deque
queue = deque(maxlen=100)  # Drop oldest when full
try:
    await asyncio.wait_for(ws.send_json(message), timeout=1.0)
except asyncio.TimeoutError:
    pass  # Client too slow
```

---

