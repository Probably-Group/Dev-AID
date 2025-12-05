# Async Performance Optimization

Performance patterns and best practices for optimizing asynchronous code.

---

## Pattern 1: Use asyncio.gather for Parallel Execution

**Problem**: Sequential async calls waste time when operations could run concurrently

**Bad Example (Sequential - 3 seconds total)**:
```python
async def fetch_all_sequential():
    user = await fetch_user()      # 1 sec
    posts = await fetch_posts()    # 1 sec
    comments = await fetch_comments()  # 1 sec
    return user, posts, comments
```

**Good Example (Parallel - 1 second total)**:
```python
async def fetch_all_parallel():
    return await asyncio.gather(
        fetch_user(),
        fetch_posts(),
        fetch_comments()
    )
```

**Key Points**:
- Use `asyncio.gather()` to run independent operations concurrently
- Operations complete in the time of the slowest, not the sum of all
- Especially beneficial for I/O-bound operations (network, database)

---

## Pattern 2: Semaphores for Concurrency Limits

**Problem**: Unbounded concurrency can overwhelm servers, exhaust resources

**Bad Example (Unbounded concurrency)**:
```python
async def process_all_bad(items):
    # Creates 10,000 simultaneous connections!
    return await asyncio.gather(*[process(item) for item in items])
```

**Good Example (Limited concurrency)**:
```python
async def process_all_good(items, max_concurrent=100):
    semaphore = asyncio.Semaphore(max_concurrent)

    async def bounded(item):
        async with semaphore:
            return await process(item)

    return await asyncio.gather(*[bounded(item) for item in items])
```

**Key Points**:
- Semaphores limit concurrent operations to a reasonable number
- Prevents overwhelming downstream services
- Typical limits: 100-1000 for HTTP requests, 10-50 for database connections
- Adjust based on server capacity and response times

---

## Pattern 3: Task Groups for Structured Concurrency (Python 3.11+)

**Problem**: Manual task management is error-prone and verbose

**Bad Example (Manual task management)**:
```python
async def fetch_all_manual():
    tasks = [asyncio.create_task(fetch(url)) for url in urls]
    try:
        return await asyncio.gather(*tasks)
    except Exception:
        # Must manually cancel all tasks
        for task in tasks:
            task.cancel()
        raise
```

**Good Example (TaskGroup handles cancellation)**:
```python
async def fetch_all_taskgroup():
    results = []
    async with asyncio.TaskGroup() as tg:
        for url in urls:
            task = tg.create_task(fetch(url))
            results.append(task)
    return [task.result() for task in results]
```

**Key Points**:
- TaskGroup automatically cancels all tasks if one fails
- Cleaner error handling with exception groups
- Ensures no tasks are left running after errors
- Available in Python 3.11+

---

## Pattern 4: Event Loop Optimization

**Problem**: CPU-intensive work blocks the event loop

**Bad Example (Blocking)**:
```python
async def process_data_bad(data):
    # Blocks event loop - other tasks freeze!
    result = heavy_cpu_computation(data)
    return result
```

**Good Example (Run in executor)**:
```python
async def process_data_good(data):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        heavy_cpu_computation,
        data
    )
    return result
```

**Key Points**:
- Use `run_in_executor()` for CPU-intensive work
- Runs blocking code in thread/process pool
- Keeps event loop responsive for I/O operations
- Consider `ProcessPoolExecutor` for CPU-bound work

---

## Pattern 5: Avoid Blocking Operations

**Problem**: Using blocking libraries in async code defeats the purpose

### Example 1: HTTP Requests

**Bad (Blocks event loop)**:
```python
import requests

async def fetch_bad(url):
    # requests.get() is blocking!
    return requests.get(url).json()
```

**Good (Non-blocking)**:
```python
import aiohttp

async def fetch_good(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

### Example 2: Sleep

**Bad (Blocks event loop)**:
```python
import time

async def delay_bad():
    time.sleep(1)  # Blocks everything!
```

**Good (Yields to event loop)**:
```python
async def delay_good():
    await asyncio.sleep(1)  # Other tasks can run
```

### Example 3: File I/O

**Bad (Blocking)**:
```python
async def read_file_bad(path):
    with open(path) as f:
        return f.read()  # Blocks on I/O
```

**Good (Non-blocking)**:
```python
import aiofiles

async def read_file_good(path):
    async with aiofiles.open(path) as f:
        return await f.read()
```

**Common Async Libraries**:
- HTTP: `aiohttp`, `httpx`
- Database: `asyncpg` (PostgreSQL), `motor` (MongoDB), `aiomysql` (MySQL)
- File I/O: `aiofiles`
- Redis: `aioredis`, `redis-py` (async mode)
- MQTT: `asyncio-mqtt`

---

## Pattern 6: Connection Pooling

**Problem**: Creating new connections for each request is expensive

**Bad Example (No pooling)**:
```python
async def fetch_users_bad(user_ids):
    results = []
    for uid in user_ids:
        # Creates new connection every time!
        async with aiohttp.ClientSession() as session:
            async with session.get(f'/users/{uid}') as resp:
                results.append(await resp.json())
    return results
```

**Good Example (Reuse session/pool)**:
```python
async def fetch_users_good(session, user_ids):
    # Session passed in, reused across calls
    tasks = [
        session.get(f'/users/{uid}')
        for uid in user_ids
    ]
    responses = await asyncio.gather(*tasks)
    return [await r.json() for r in responses]

# Usage
async with aiohttp.ClientSession() as session:
    results = await fetch_users_good(session, [1, 2, 3])
```

**Key Points**:
- Reuse ClientSession across multiple requests
- Database connection pools: `asyncpg.create_pool()`
- Pools amortize connection overhead
- Configure pool size based on load

---

## Pattern 7: Batch Operations

**Problem**: Making individual requests when batch operations are available

**Bad Example (N requests)**:
```python
async def fetch_users_one_by_one(user_ids):
    users = []
    for uid in user_ids:
        user = await fetch_user(uid)  # Separate API call each time
        users.append(user)
    return users
```

**Good Example (Batch request)**:
```python
async def fetch_users_batch(user_ids):
    # Single API call for all users
    return await fetch_users_by_ids(user_ids)
```

**Key Points**:
- Use batch APIs when available (e.g., `GET /users?ids=1,2,3`)
- Database: Use bulk insert/update operations
- GraphQL: Combine queries with fragments
- Reduces network round trips and server load

---

## Pattern 8: Caching

**Problem**: Repeatedly fetching the same data

**Example with TTL cache**:
```python
from datetime import datetime, timedelta

class AsyncCache:
    def __init__(self, ttl_seconds=300):
        self.cache = {}
        self.ttl = timedelta(seconds=ttl_seconds)

    async def get_or_fetch(self, key, fetch_func):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < self.ttl:
                return value

        # Cache miss or expired
        value = await fetch_func()
        self.cache[key] = (value, datetime.now())
        return value

# Usage
cache = AsyncCache(ttl_seconds=60)

async def get_user(user_id):
    return await cache.get_or_fetch(
        f"user:{user_id}",
        lambda: fetch_user_from_db(user_id)
    )
```

**Key Points**:
- Cache frequently accessed, rarely changing data
- Use TTL to prevent stale data
- Consider using Redis for distributed caching
- Implement cache invalidation strategy

---

## Performance Profiling

### Monitoring Event Loop Lag

```python
import asyncio
import time

async def monitor_event_loop():
    """Detect if event loop is blocked"""
    while True:
        start = time.perf_counter()
        await asyncio.sleep(0.1)
        elapsed = time.perf_counter() - start

        if elapsed > 0.15:  # Should be ~0.1s
            lag = (elapsed - 0.1) * 1000
            print(f"⚠️ Event loop lag: {lag:.1f}ms")
```

### Profiling Async Code

```python
import asyncio
import cProfile
import pstats

async def main():
    # Your async code here
    pass

# Profile with cProfile
profiler = cProfile.Profile()
profiler.enable()
asyncio.run(main())
profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

---

## Performance Checklist

Before deploying async code:
- [ ] All I/O uses async libraries (no `requests`, `time.sleep`, blocking file I/O)
- [ ] CPU-intensive work runs in executor
- [ ] Concurrency limits set with semaphores
- [ ] Connection pooling configured
- [ ] Batch operations used where possible
- [ ] Caching implemented for repeated data
- [ ] Timeouts set on all network calls
- [ ] Event loop lag monitored in production
- [ ] Load testing performed under realistic conditions
- [ ] Resource usage profiled (memory, file descriptors, connections)
