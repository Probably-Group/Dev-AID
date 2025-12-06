## 9. Common Mistakes & Anti-Patterns

### No Origin Validation

```python
# NEVER - vulnerable to CSWSH
@app.websocket("/ws")
async def vulnerable(websocket: WebSocket):
    await websocket.accept()  # Accepts any origin!

# ALWAYS - validate origin first
if websocket.headers.get("origin") not in ALLOWED_ORIGINS:
    await websocket.close(code=4003)
    return
```

### Cookie-Only Authentication

```python
# NEVER - cookies sent automatically in CSWSH attacks
session = websocket.cookies.get("session")

# ALWAYS - require explicit token parameter
token = websocket.query_params.get("token")
```

### No Per-Message Authorization

```python
# NEVER - assumes connection = full access
if data["action"] == "delete":
    await delete_resource(data["id"])

# ALWAYS - check permission for each action
if not user.has_permission("delete"):
    return {"error": "Permission denied"}
```

### No Input Validation

```python
# NEVER - trust WebSocket messages
await db.execute(f"SELECT * FROM {data['table']}")  # SQL injection!

# ALWAYS - validate with Pydantic
message = WebSocketMessage(**data)
```

---

