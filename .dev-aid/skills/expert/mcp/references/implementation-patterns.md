## 7. Implementation Patterns

### 6.1 Secure MCP Server Setup

```python
app = Server("secure-server")

class FileReadArgs(BaseModel):
    path: str

    @validator("path")
    def validate_path(cls, v):
        if ".." in v:
            raise ValueError("Path traversal not allowed")
        if not v.startswith("/allowed/"):
            raise ValueError("Invalid directory")
        return v

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name != "read_file":
        raise ValueError("Unknown tool")

    args = FileReadArgs(**arguments)
    content = await asyncio.wait_for(
        read_file_secure(args.path), timeout=5.0
    )
    return [TextContent(type="text", text=content)]
```

### 6.2 Tool Registration with Authorization

```python
class DatabaseQueryArgs(BaseModel):
    query: str
    database: str

    @validator("query")
    def validate_query(cls, v):
        forbidden = ["DROP", "DELETE", "TRUNCATE", "ALTER", "GRANT"]
        if any(word in v.upper() for word in forbidden):
            raise ValueError("Forbidden SQL operation")
        return v

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    args = DatabaseQueryArgs(**arguments)
    if not await check_user_permission(args.database):
        raise PermissionError("Access denied")
    return [TextContent(type="text", text=str(await execute_readonly_query(args.database, args.query)))]
```

---

