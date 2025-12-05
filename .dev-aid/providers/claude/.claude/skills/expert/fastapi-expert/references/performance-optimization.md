# FastAPI Performance Optimization

This document contains performance optimization patterns for FastAPI applications.

## Pattern 1: Connection Pooling

```python
# Bad - No connection pooling configuration
engine = create_async_engine(DATABASE_URL)

# Good - Proper connection pooling
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,           # Base number of connections
    max_overflow=10,        # Extra connections when pool is full
    pool_recycle=3600,      # Recycle connections after 1 hour
    pool_pre_ping=True,     # Check connection health before use
    pool_timeout=30,        # Wait 30s for available connection
)

# Good - Proper cleanup on shutdown
@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()
```

## Pattern 2: Concurrent Operations with asyncio.gather

```python
# Bad - Sequential async calls
async def get_user_dashboard(user_id: int, db: AsyncSession):
    user = await get_user(db, user_id)
    orders = await get_user_orders(db, user_id)
    notifications = await get_notifications(db, user_id)
    return {"user": user, "orders": orders, "notifications": notifications}

# Good - Concurrent async calls
async def get_user_dashboard(user_id: int, db: AsyncSession):
    user, orders, notifications = await asyncio.gather(
        get_user(db, user_id),
        get_user_orders(db, user_id),
        get_notifications(db, user_id),
    )
    return {"user": user, "orders": orders, "notifications": notifications}

# Good - With error handling for partial failures
async def get_user_dashboard_safe(user_id: int, db: AsyncSession):
    results = await asyncio.gather(
        get_user(db, user_id),
        get_user_orders(db, user_id),
        get_notifications(db, user_id),
        return_exceptions=True  # Don't fail all if one fails
    )

    user, orders, notifications = results
    return {
        "user": user if not isinstance(user, Exception) else None,
        "orders": orders if not isinstance(orders, Exception) else [],
        "notifications": notifications if not isinstance(notifications, Exception) else [],
    }
```

## Pattern 3: Response Caching

```python
# Bad - No caching, database hit every request
@router.get("/products")
async def get_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product))
    return result.scalars().all()

# Good - In-memory caching with TTL
from cachetools import TTLCache
from functools import wraps

cache = TTLCache(maxsize=100, ttl=300)  # 5 minutes TTL

def cached(key_func):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = key_func(*args, **kwargs)
            if key in cache:
                return cache[key]
            result = await func(*args, **kwargs)
            cache[key] = result
            return result
        return wrapper
    return decorator

@router.get("/products")
@cached(key_func=lambda: "products_list")
async def get_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product))
    return result.scalars().all()

# Good - Redis caching for distributed systems
import aioredis
import json

redis = aioredis.from_url("redis://localhost")

@router.get("/products/{product_id}")
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    # Try cache first
    cached = await redis.get(f"product:{product_id}")
    if cached:
        return json.loads(cached)

    # Fetch from database
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(404, "Product not found")

    # Cache for 5 minutes
    await redis.setex(f"product:{product_id}", 300, json.dumps(product.dict()))
    return product
```

## Pattern 4: Streaming Responses

```python
# Bad - Load entire file into memory
@router.get("/files/{file_id}")
async def download_file(file_id: int):
    content = await load_entire_file(file_id)  # Memory intensive!
    return Response(content=content, media_type="application/octet-stream")

# Good - Stream large files
from fastapi.responses import StreamingResponse
import aiofiles

@router.get("/files/{file_id}")
async def download_file(file_id: int):
    file_path = await get_file_path(file_id)

    async def file_streamer():
        async with aiofiles.open(file_path, 'rb') as f:
            while chunk := await f.read(8192):  # 8KB chunks
                yield chunk

    return StreamingResponse(
        file_streamer(),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={file_id}"}
    )

# Good - Stream database results
@router.get("/export/users")
async def export_users(db: AsyncSession = Depends(get_db)):
    async def generate():
        yield "id,email,username\n"  # CSV header

        result = await db.stream(select(User))
        async for row in result:
            user = row[0]
            yield f"{user.id},{user.email},{user.username}\n"

    return StreamingResponse(
        generate(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=users.csv"}
    )
```

## Pattern 5: Async Database Queries

```python
# Bad - Synchronous query pattern
def get_users_sync(db):
    return db.query(User).filter(User.is_active == True).all()

# Good - Async query pattern
async def get_users_async(db: AsyncSession):
    result = await db.execute(
        select(User).where(User.is_active == True)
    )
    return result.scalars().all()

# Good - Efficient pagination
async def get_users_paginated(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20
):
    result = await db.execute(
        select(User)
        .where(User.is_active == True)
        .offset(skip)
        .limit(limit)
        .order_by(User.created_at.desc())
    )
    return result.scalars().all()

# Good - Avoid N+1 with eager loading
from sqlalchemy.orm import selectinload

async def get_users_with_orders(db: AsyncSession):
    result = await db.execute(
        select(User)
        .options(selectinload(User.orders))  # Eager load orders
        .where(User.is_active == True)
    )
    return result.scalars().all()
```

## Pattern 6: Background Task Optimization

```python
# Bad - Blocking operation in request
@router.post("/users")
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await user_crud.create_user(db, user_in)
    await send_welcome_email(user.email)  # Blocks response!
    await notify_admins(user)             # More blocking!
    return user

# Good - Non-blocking background tasks
from fastapi import BackgroundTasks

@router.post("/users")
async def create_user(
    user_in: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    user = await user_crud.create_user(db, user_in)

    # Queue non-critical tasks
    background_tasks.add_task(send_welcome_email, user.email)
    background_tasks.add_task(notify_admins, user)

    return user  # Return immediately!

# Good - For heavy tasks, use task queue (Celery/ARQ)
from arq import create_pool

@router.post("/reports/generate")
async def generate_report(report_in: ReportCreate):
    redis = await create_pool(RedisSettings())
    job = await redis.enqueue_job('generate_report', report_in.dict())
    return {"job_id": job.job_id, "status": "queued"}
```
