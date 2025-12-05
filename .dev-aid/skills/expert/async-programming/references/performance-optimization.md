# Async Programming Performance Optimization

This document provides detailed performance patterns and optimization strategies for async programming in Python (asyncio) and Rust (Tokio).

---

## Pattern 1: asyncio.gather for Concurrency

### Problem
Sequential execution of async operations wastes time waiting for each operation to complete before starting the next.

### Bad Example - Sequential Execution
```python
async def fetch_all_sequential(urls: list[str]) -> list[str]:
    results = []
    for url in urls:
        result = await fetch(url)  # Waits for each
        results.append(result)
    return results  # Total time: sum of all fetches
```

**Performance**: If each fetch takes 1 second and you have 10 URLs, total time = 10 seconds.

### Good Example - Concurrent Execution
```python
async def fetch_all_concurrent(urls: list[str]) -> list[str]:
    return await asyncio.gather(*[fetch(url) for url in urls])
    # Total time: max of all fetches
```

**Performance**: With 10 URLs taking 1 second each, total time = ~1 second.

### When to Use
- Multiple independent I/O operations (API calls, database queries, file reads)
- Operations that can run in parallel without interdependencies
- When you need all results before proceeding

### Trade-offs
**Pros**:
- Dramatic performance improvement for I/O-bound workloads
- Simple and readable syntax
- Automatically handles exceptions with `return_exceptions=True`

**Cons**:
- All tasks run unbounded (can overwhelm servers)
- Consumes more resources (connections, memory)
- Requires careful error handling

---

## Pattern 2: Semaphores for Rate Limiting

### Problem
Unbounded concurrency can overwhelm external services, exhaust connection pools, or violate rate limits.

### Bad Example - Unbounded Concurrency
```python
async def fetch_many(urls: list[str]):
    # May create 1000s of connections simultaneously
    return await asyncio.gather(*[fetch(url) for url in urls])
```

**Risk**: Server refuses connections, connection pool exhausted, rate limit errors.

### Good Example - Bounded Concurrency with Semaphore
```python
async def fetch_many_limited(urls: list[str], max_concurrent: int = 10):
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_with_limit(url: str):
        async with semaphore:
            return await fetch(url)

    return await asyncio.gather(*[fetch_with_limit(url) for url in urls])
```

**Performance**: Maximum 10 concurrent requests, respects server limits.

### When to Use
- External API calls with rate limits
- Database connection pools with limited connections
- File I/O with system resource limits
- Any resource-constrained operation

### Choosing max_concurrent Value
```python
# Too low: Underutilizes resources
max_concurrent = 1  # Essentially sequential

# Too high: May overwhelm server
max_concurrent = 1000  # Risk of connection exhaustion

# Good starting points:
# - HTTP APIs: 10-50 depending on rate limits
# - Database: Match connection pool size (e.g., 20)
# - File I/O: 10-20 (system-dependent)
```

---

## Pattern 3: Task Groups (Python 3.11+)

### Problem
Manual task tracking is error-prone and doesn't handle cancellation properly.

### Bad Example - Manual Task Tracking
```python
async def process_items_manual(items):
    tasks = []
    for item in items:
        task = asyncio.create_task(process(item))
        tasks.append(task)
    return await asyncio.gather(*tasks)
    # Problem: If one task fails, others keep running
```

### Good Example - Task Groups with Automatic Cleanup
```python
async def process_items_taskgroup(items):
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(process(item)) for item in items]
    return [task.result() for task in tasks]
    # Automatic cancellation of all tasks on any failure
```

### When to Use
- Python 3.11+ environments
- When you need fail-fast behavior (cancel all on first error)
- When you want automatic cleanup on exit

### Benefits
- Automatic cancellation of remaining tasks on first exception
- Proper cleanup even on cancellation
- Cleaner error handling
- No need to manually track tasks

---

## Pattern 4: Efficient Event Loop Usage

### Problem
Creating new event loops is expensive and can cause issues with nested loops.

### Bad Example - Creating New Event Loop
```python
def run_async_bad():
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(main())
    finally:
        loop.close()
    # Problem: Resource overhead, potential nested loop issues
```

### Good Example - asyncio.run
```python
def run_async_good():
    return asyncio.run(main())  # Handles loop lifecycle automatically
```

### Good Example - For Library Code
```python
async def library_function():
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    # Use the existing loop
    return future
```

### When to Use
- `asyncio.run()`: Top-level application entry points
- `get_running_loop()`: Inside async functions, library code
- NEVER create new loop inside running async context

---

## Pattern 5: Avoiding Blocking Calls

### Problem
Blocking calls freeze the entire event loop, preventing all async tasks from running.

### Bad Example - Blocks Event Loop
```python
import time
import hashlib

async def process_file_bad(path: str):
    with open(path) as f:  # Blocking I/O
        data = f.read()
    result = hashlib.sha256(data).hexdigest()  # CPU-bound blocks loop
    return result
```

**Impact**: While processing one file, ALL other async tasks are frozen.

### Good Example - Non-blocking with aiofiles and executor
```python
import aiofiles
import asyncio

async def process_file_good(path: str):
    # Non-blocking file I/O
    async with aiofiles.open(path, 'rb') as f:
        data = await f.read()

    # CPU-bound work in executor (separate thread/process)
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None, lambda: hashlib.sha256(data).hexdigest()
    )
    return result
```

### Common Blocking Operations to Avoid

| Blocking Operation | Non-Blocking Alternative |
|-------------------|-------------------------|
| `open()`, `file.read()` | `aiofiles` |
| `requests.get()` | `aiohttp`, `httpx` |
| `time.sleep()` | `asyncio.sleep()` |
| CPU-intensive work | `loop.run_in_executor()` |
| `sqlite3` operations | `aiosqlite` |
| `subprocess.run()` | `asyncio.create_subprocess_exec()` |

---

## Pattern 6: Connection Pooling

### Problem
Creating new connections for each operation is expensive.

### Bad Example - No Connection Pooling
```python
async def query_many(queries: list[str]):
    results = []
    for query in queries:
        conn = await asyncpg.connect(DATABASE_URL)  # New connection each time
        result = await conn.fetchval(query)
        await conn.close()
        results.append(result)
    return results
```

### Good Example - Connection Pool
```python
# Initialize pool once at startup
pool = await asyncpg.create_pool(
    DATABASE_URL,
    min_size=10,
    max_size=20,
    command_timeout=60
)

async def query_many(queries: list[str]):
    results = []
    for query in queries:
        async with pool.acquire() as conn:  # Reuse from pool
            result = await conn.fetchval(query)
            results.append(result)
    return results
```

### Connection Pool Best Practices

```python
# Good pool configuration
pool = await asyncpg.create_pool(
    DATABASE_URL,
    min_size=10,              # Keep 10 connections warm
    max_size=20,              # Max 20 concurrent connections
    command_timeout=60,       # Timeout queries after 60s
    max_inactive_connection_lifetime=300  # Recycle idle connections
)

# Graceful shutdown
await pool.close()
```

---

## Pattern 7: Caching and Memoization

### Problem
Repeated async operations fetch the same data multiple times.

### Good Example - Cache with TTL
```python
from datetime import datetime, timedelta

class AsyncCache:
    def __init__(self, ttl_seconds: int = 300):
        self._cache = {}
        self._ttl = timedelta(seconds=ttl_seconds)
        self._lock = asyncio.Lock()

    async def get_or_fetch(self, key: str, fetch_fn):
        async with self._lock:
            if key in self._cache:
                value, timestamp = self._cache[key]
                if datetime.now() - timestamp < self._ttl:
                    return value

            # Cache miss or expired
            value = await fetch_fn()
            self._cache[key] = (value, datetime.now())
            return value
```

### Usage
```python
cache = AsyncCache(ttl_seconds=300)

async def get_user(user_id: int):
    return await cache.get_or_fetch(
        f"user:{user_id}",
        lambda: db.fetch_user(user_id)
    )
```

---

## Pattern 8: Batching Operations

### Problem
Making many small database queries is inefficient.

### Bad Example - Individual Queries
```python
async def get_users(user_ids: list[int]):
    users = []
    for user_id in user_ids:
        user = await db.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
        users.append(user)
    return users
    # Makes N database round trips
```

### Good Example - Batch Query
```python
async def get_users(user_ids: list[int]):
    return await db.fetch(
        "SELECT * FROM users WHERE id = ANY($1::int[])",
        user_ids
    )
    # Single database round trip
```

---

## Performance Measurement

### Timing Async Operations

```python
import time
import asyncio

async def measure_performance():
    start = time.perf_counter()
    result = await expensive_operation()
    elapsed = time.perf_counter() - start
    print(f"Operation took {elapsed:.2f}s")
    return result
```

### Profiling Async Code

```python
import cProfile
import pstats

def profile_async():
    profiler = cProfile.Profile()
    profiler.enable()

    asyncio.run(main())

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)
```

---

## Key Performance Rules Summary

1. **Use `asyncio.gather`** for concurrent I/O operations
2. **Apply semaphores** to limit concurrent connections
3. **Use TaskGroup (Python 3.11+)** for automatic cleanup
4. **Never block event loop** - use `run_in_executor` for CPU work
5. **Reuse event loops** - don't create new ones
6. **Use connection pools** - don't create connections per operation
7. **Cache when possible** - avoid redundant fetches
8. **Batch operations** - minimize round trips
9. **Profile regularly** - measure before optimizing
10. **Set timeouts** - prevent hanging operations
