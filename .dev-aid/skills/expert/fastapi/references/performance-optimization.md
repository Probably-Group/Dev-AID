# FastAPI Performance Optimization Reference

## Pattern 1: Connection Pooling for Database

```python
# BAD - Creates new connection per request
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        return await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
    finally:
        await conn.close()

# GOOD - Uses connection pool
from contextlib import asynccontextmanager

pool: asyncpg.Pool = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global pool
    pool = await asyncpg.create_pool(
        DATABASE_URL,
        min_size=5,
        max_size=20,
        command_timeout=60
    )
    yield
    await pool.close()

app = FastAPI(lifespan=lifespan)

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    async with pool.acquire() as conn:
        return await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
```

**Key Points**:
- Use connection pooling for all database operations
- Configure appropriate pool sizes based on load
- Always use context managers for connection acquisition
- Set reasonable timeouts

---

## Pattern 2: Concurrent Requests with asyncio.gather

```python
# BAD - Sequential external API calls
@app.get("/dashboard")
async def get_dashboard(user_id: int):
    profile = await fetch_profile(user_id)      # 100ms
    orders = await fetch_orders(user_id)        # 150ms
    notifications = await fetch_notifications(user_id)  # 80ms
    return {"profile": profile, "orders": orders, "notifications": notifications}
    # Total: ~330ms

# GOOD - Concurrent calls
@app.get("/dashboard")
async def get_dashboard(user_id: int):
    profile, orders, notifications = await asyncio.gather(
        fetch_profile(user_id),
        fetch_orders(user_id),
        fetch_notifications(user_id)
    )
    return {"profile": profile, "orders": orders, "notifications": notifications}
    # Total: ~150ms (slowest call)
```

**Key Points**:
- Use `asyncio.gather()` for independent async operations
- Can reduce latency by up to 50-70% for multiple I/O calls
- Handle exceptions with `return_exceptions=True` if needed
- Order of results matches order of input coroutines

---

## Pattern 3: Response Caching

```python
# BAD - Recomputes expensive data every request
@app.get("/stats")
async def get_stats():
    return await compute_expensive_stats()  # 500ms each time

# GOOD - Cache with Redis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="api-cache")
    yield

@app.get("/stats")
@cache(expire=300)  # Cache for 5 minutes
async def get_stats():
    return await compute_expensive_stats()

# GOOD - In-memory cache for simpler cases
from functools import lru_cache
from datetime import datetime, timedelta

_cache = {}
_cache_time = {}

async def get_cached_config(key: str, ttl: int = 60):
    now = datetime.utcnow()
    if key in _cache and _cache_time[key] > now:
        return _cache[key]

    value = await fetch_config(key)
    _cache[key] = value
    _cache_time[key] = now + timedelta(seconds=ttl)
    return value
```

**Key Points**:
- Use Redis for distributed caching
- Use in-memory caching for single-instance deployments
- Set appropriate TTL based on data freshness requirements
- Consider cache invalidation strategies

---

## Pattern 4: Pagination for Large Datasets

```python
# BAD - Returns all records
@app.get("/items")
async def list_items():
    return await db.fetch("SELECT * FROM items")  # Could be millions

# GOOD - Cursor-based pagination
from pydantic import BaseModel

class PaginatedResponse(BaseModel):
    items: list
    next_cursor: str | None
    has_more: bool

@app.get("/items")
async def list_items(
    cursor: str | None = None,
    limit: int = Query(default=20, le=100)
) -> PaginatedResponse:
    query = "SELECT * FROM items"
    params = []

    if cursor:
        query += " WHERE id > $1"
        params.append(decode_cursor(cursor))

    query += f" ORDER BY id LIMIT {limit + 1}"

    rows = await db.fetch(query, *params)
    has_more = len(rows) > limit
    items = rows[:limit]

    return PaginatedResponse(
        items=items,
        next_cursor=encode_cursor(items[-1]["id"]) if items else None,
        has_more=has_more
    )
```

**Key Points**:
- Always paginate large result sets
- Cursor-based pagination is more efficient than offset-based
- Limit maximum page size to prevent abuse
- Include `has_more` flag for client convenience

---

## Pattern 5: Background Tasks for Heavy Operations

```python
# BAD - Blocks response for slow operations
@app.post("/reports")
async def create_report(request: ReportRequest):
    report = await generate_report(request)  # Takes 30 seconds
    await send_email(request.email, report)
    return {"status": "completed"}

# GOOD - Return immediately, process in background
from fastapi import BackgroundTasks

@app.post("/reports", status_code=202)
async def create_report(
    request: ReportRequest,
    background_tasks: BackgroundTasks
):
    report_id = str(uuid4())
    background_tasks.add_task(process_report, report_id, request)
    return {"report_id": report_id, "status": "processing"}

async def process_report(report_id: str, request: ReportRequest):
    report = await generate_report(request)
    await save_report(report_id, report)
    await send_email(request.email, report)

@app.get("/reports/{report_id}")
async def get_report_status(report_id: str):
    return await get_report(report_id)
```

**Key Points**:
- Use background tasks for operations > 2 seconds
- Return 202 Accepted for async processing
- Provide status endpoint for clients to poll
- Consider using Celery/RQ for more complex job queues

---

## Additional Performance Tips

### 1. Use Async Everywhere

```python
# Use async database drivers
import asyncpg  # Not psycopg2
import motor    # Not pymongo
import httpx    # Not requests

# Use async file I/O
import aiofiles

async with aiofiles.open('file.txt', 'r') as f:
    content = await f.read()
```

### 2. Optimize Pydantic Models

```python
from pydantic import ConfigDict

class User(BaseModel):
    model_config = ConfigDict(
        # Skip validation for trusted sources
        validate_assignment=False,
        # Use slots for memory efficiency
        use_enum_values=True
    )
```

### 3. Database Query Optimization

```python
# Load related data in one query (avoid N+1)
from sqlalchemy.orm import selectinload

stmt = select(User).options(
    selectinload(User.posts),
    selectinload(User.comments)
)
```

### 4. Response Compression

```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)
```

### 5. Limit Request Body Size

```python
@app.middleware("http")
async def limit_upload_size(request: Request, call_next):
    if request.method in ["POST", "PUT", "PATCH"]:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 10_000_000:  # 10MB
            return JSONResponse(
                status_code=413,
                content={"detail": "Request body too large"}
            )
    return await call_next(request)
```

---

## Performance Testing

### Load Testing with Locust

```python
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # Login and get token
        response = self.client.post("/token", {
            "username": "test",
            "password": "test"
        })
        self.token = response.json()["access_token"]
        self.client.headers["Authorization"] = f"Bearer {self.token}"

    @task(3)
    def get_items(self):
        self.client.get("/items")

    @task(1)
    def create_item(self):
        self.client.post("/items", json={
            "name": "Test Item",
            "price": 29.99
        })
```

### Profiling Endpoints

```python
import cProfile
import pstats
from io import StringIO

@app.middleware("http")
async def profile_request(request: Request, call_next):
    if request.query_params.get("profile"):
        profiler = cProfile.Profile()
        profiler.enable()

        response = await call_next(request)

        profiler.disable()
        s = StringIO()
        stats = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
        stats.print_stats()

        # Log or return profiling data
        print(s.getvalue())
        return response

    return await call_next(request)
```

---

## Performance Checklist

Before deploying to production:

- [ ] Database connection pooling configured
- [ ] Independent async operations use `asyncio.gather()`
- [ ] Expensive computations cached (Redis or in-memory)
- [ ] Large datasets paginated (cursor-based preferred)
- [ ] Long-running operations use background tasks
- [ ] Response compression enabled
- [ ] Request body size limits enforced
- [ ] Load tested with realistic traffic patterns
- [ ] Slow endpoints profiled and optimized
- [ ] Database queries optimized (no N+1)
