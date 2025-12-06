## 7. Performance Patterns

### 6.1 Pagination (Cursor-Based)

```python
# BAD: Offset pagination - O(n) scanning
@router.get("/users")
async def list_users(offset: int = 0, limit: int = 20):
    return await db.execute(f"SELECT * FROM users LIMIT {limit} OFFSET {offset}")

# GOOD: Cursor-based pagination - O(1) seek
@router.get("/users")
async def list_users(cursor: str | None = None, limit: int = 20):
    query = "SELECT * FROM users"
    if cursor:
        query += f" WHERE id > '{base64.b64decode(cursor).decode()}'"
    query += f" ORDER BY id LIMIT {limit + 1}"

    results = await db.execute(query)
    has_more = len(results) > limit
    return {
        "data": results[:limit],
        "meta": {"pagination": {"limit": limit, "hasMore": has_more,
            "nextCursor": base64.b64encode(results[-1]["id"].encode()).decode() if has_more else None}}
    }
```

### 6.2 Caching Headers

```python
# BAD: No caching strategy
@router.get("/products/{id}")
async def get_product(id: str):
    return await db.products.find_by_id(id)

# GOOD: ETag and Cache-Control headers
@router.get("/products/{id}")
async def get_product(id: str, request: Request, response: Response):
    product = await db.products.find_by_id(id)
    etag = f'"{hashlib.md5(json.dumps(product).encode()).hexdigest()}"'

    if request.headers.get("If-None-Match") == etag:
        return Response(status_code=304)  # Not Modified

    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "public, max-age=300, must-revalidate"
    return {"data": product}
```

### 6.3 Compression

```python
# BAD: No compression
app = FastAPI()

# GOOD: Enable gzip middleware
from fastapi.middleware.gzip import GZipMiddleware
app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)  # Compress responses > 1KB
```

### 6.4 Rate Limiting

```python
# BAD: No rate limiting
@router.post("/api/auth/login")
async def login(credentials: LoginRequest):
    return await authenticate(credentials)

# GOOD: Tiered rate limiting with slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/api/auth/login")
@limiter.limit("5/minute")  # Strict for auth
async def login(request: Request, credentials: LoginRequest):
    return await authenticate(credentials)

@router.get("/api/v1/users")
@limiter.limit("100/minute")  # Standard for API
async def list_users(request: Request):
    return await get_users()
```

### 6.5 Connection Keep-Alive

```python
# BAD: Creating new connections per request
async def call_external_api():
    async with httpx.AsyncClient() as client:  # New connection each time
        return await client.get("https://api.example.com/data")

# GOOD: App-level client with connection pooling
http_client: httpx.AsyncClient | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global http_client
    http_client = httpx.AsyncClient(
        limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
    )
    yield
    await http_client.aclose()

app = FastAPI(lifespan=lifespan)
```

---

