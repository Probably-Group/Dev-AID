## 3. Performance Patterns

### 3.1 Connection Reuse

```python
# Bad: Create new connection per request
async def call_tool(name: str, args: dict):
    client = MCPClient()  # New connection every time
    await client.connect()
    result = await client.call_tool(name, args)
    await client.disconnect()
    return result

# Good: Reuse connections with connection pool
class MCPClientPool:
    def __init__(self, max_connections: int = 10):
        self._pool: asyncio.Queue = asyncio.Queue(maxsize=max_connections)
        self._created = 0
        self._max = max_connections

    async def acquire(self) -> MCPClient:
        if self._pool.empty() and self._created < self._max:
            client = MCPClient()
            await client.connect()
            self._created += 1
            return client
        return await self._pool.get()

    async def release(self, client: MCPClient):
        await self._pool.put(client)
```

### 3.2 Response Caching

```python
# Bad: No caching for repeated requests
@app.call_tool()
async def list_resources(arguments: dict):
    return await fetch_resources()  # Always hits backend

# Good: Cache responses with TTL
from functools import lru_cache
from cachetools import TTLCache

class CachedMCPServer:
    def __init__(self):
        self._cache = TTLCache(maxsize=100, ttl=300)  # 5 min TTL

    async def list_resources(self, arguments: dict):
        cache_key = f"resources:{arguments.get('type', 'all')}"

        if cache_key in self._cache:
            return self._cache[cache_key]

        result = await self._fetch_resources(arguments)
        self._cache[cache_key] = result
        return result
```

### 3.3 Batch Operations

```python
# Bad: Process items one at a time
async def process_files(file_paths: list[str]):
    results = []
    for path in file_paths:
        result = await read_file(path)  # Sequential
        results.append(result)
    return results

# Good: Batch process with concurrency control
import asyncio

async def process_files_batch(file_paths: list[str], max_concurrent: int = 5):
    semaphore = asyncio.Semaphore(max_concurrent)

    async def read_with_limit(path: str):
        async with semaphore:
            return await read_file(path)

    return await asyncio.gather(*[read_with_limit(p) for p in file_paths])
```

### 3.4 Streaming Responses

```python
# Bad: Load entire response into memory
async def read_large_file(path: str):
    with open(path, 'r') as f:
        return f.read()  # Memory spike for large files

# Good: Stream response in chunks
async def stream_large_file(path: str):
    async def generate():
        async with aiofiles.open(path, 'r') as f:
            while chunk := await f.read(8192):
                yield TextContent(type="text", text=chunk)

    return StreamingResponse(generate())
```

### 3.5 Resource Cleanup

```python
# Bad: Resources may leak on error
async def execute_tool(name: str, args: dict):
    conn = await get_db_connection()
    result = await conn.execute(args["query"])  # Error leaves conn open
    return result

# Good: Always cleanup with context managers
async def execute_tool(name: str, args: dict):
    async with get_db_connection() as conn:
        result = await conn.execute(args["query"])
        return result

# Good: Explicit cleanup with try/finally
async def execute_with_timeout(tool_func, timeout: int = 5000):
    task = asyncio.create_task(tool_func())
    try:
        return await asyncio.wait_for(task, timeout=timeout/1000)
    except asyncio.TimeoutError:
        task.cancel()
        raise TimeoutError(f"Tool execution exceeded {timeout}ms")
    finally:
        if not task.done():
            task.cancel()
```

---


