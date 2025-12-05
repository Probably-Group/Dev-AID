# API Performance Optimization

Comprehensive guide to optimizing API performance for scalability and efficiency.

## Table of Contents
- [Response Caching](#response-caching)
- [Cursor-Based Pagination](#cursor-based-pagination)
- [Response Compression](#response-compression)
- [Connection Pooling](#connection-pooling)
- [Rate Limiting](#rate-limiting)
- [Query Optimization](#query-optimization)
- [Database Indexing](#database-indexing)
- [Load Balancing](#load-balancing)

---

## Response Caching

### Pattern 1: Redis Cache with Headers

```python
# Bad: No caching
@router.get("/v1/products/{id}")
async def get_product(id: str):
    return await db.products.find_one({"_id": id})

# Good: Redis cache with headers
@router.get("/v1/products/{id}")
async def get_product(id: str, response: Response):
    cached = await redis_cache.get(f"product:{id}")
    if cached:
        response.headers["X-Cache"] = "HIT"
        return cached

    product = await db.products.find_one({"_id": id})
    await redis_cache.setex(f"product:{id}", 300, product)
    response.headers["Cache-Control"] = "public, max-age=300"
    response.headers["X-Cache"] = "MISS"
    return product
```

### Pattern 2: HTTP Cache Headers

```javascript
// ETags for conditional requests
app.get('/v1/users/:id', async (req, res) => {
  const user = await getUser(req.params.id);
  const etag = generateETag(user);

  if (req.headers['if-none-match'] === etag) {
    return res.status(304).end(); // Not Modified
  }

  res.set({
    'ETag': etag,
    'Cache-Control': 'private, max-age=300',
    'Last-Modified': user.updated_at
  });
  res.json(user);
});
```

### Pattern 3: Cache Invalidation

```javascript
// Cache invalidation on updates
const invalidateCache = async (key) => {
  await redis.del(key);
  await redis.publish('cache:invalidate', key); // Notify other instances
};

app.put('/v1/products/:id', async (req, res) => {
  const product = await updateProduct(req.params.id, req.body);
  await invalidateCache(`product:${req.params.id}`);
  res.json(product);
});
```

---

## Cursor-Based Pagination

### Efficient Cursor Implementation

```python
# Bad: Offset pagination - O(n) skip
@router.get("/v1/users")
async def list_users(offset: int = 0, limit: int = 100):
    return await db.users.find().skip(offset).limit(limit)

# Good: Cursor-based - O(1) performance
@router.get("/v1/users")
async def list_users(cursor: str = None, limit: int = Query(default=20, le=100)):
    query = {"_id": {"$gt": ObjectId(cursor)}} if cursor else {}
    users = await db.users.find(query).sort("_id", 1).limit(limit + 1).to_list()
    has_next = len(users) > limit

    return {
        "data": users[:limit],
        "pagination": {
            "next_cursor": str(users[-1]["_id"]) if has_next else None,
            "has_more": has_next
        }
    }
```

### Composite Cursor for Multi-Field Sorting

```javascript
// For complex sorting (timestamp + ID)
const encodeCursor = (item) => {
  const cursor = {
    created_at: item.created_at,
    id: item.id
  };
  return Buffer.from(JSON.stringify(cursor)).toString('base64');
};

const decodeCursor = (cursorString) => {
  return JSON.parse(Buffer.from(cursorString, 'base64').toString());
};

app.get('/v1/items', async (req, res) => {
  let query = db.select().from('items');

  if (req.query.cursor) {
    const cursor = decodeCursor(req.query.cursor);
    query = query
      .where('created_at', '<', cursor.created_at)
      .orWhere((builder) => {
        builder
          .where('created_at', '=', cursor.created_at)
          .where('id', '<', cursor.id);
      });
  }

  query = query
    .orderBy('created_at', 'desc')
    .orderBy('id', 'desc')
    .limit(limit + 1);

  const items = await query;
  // Process results...
});
```

---

## Response Compression

### Pattern 1: GZip Middleware

```python
# Bad: No compression
app = FastAPI()

# Good: GZip middleware for responses > 500 bytes
from fastapi.middleware.gzip import GZipMiddleware
app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=500)
```

### Pattern 2: Conditional Compression

```javascript
// Compress based on content type
const compression = require('compression');

app.use(compression({
  filter: (req, res) => {
    // Don't compress responses marked as "no-transform"
    if (req.headers['x-no-compression']) {
      return false;
    }
    // Use compression for all other requests
    return compression.filter(req, res);
  },
  level: 6 // Compression level (1-9, 6 is default)
}));
```

---

## Connection Pooling

### Pattern 1: Database Connection Pool

```python
# Bad: New connection per request
@router.get("/v1/data")
async def get_data():
    client = AsyncIOMotorClient("mongodb://localhost")  # Expensive!
    return await client.db.collection.find_one()

# Good: Shared pool via lifespan
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.db = AsyncIOMotorClient(
        "mongodb://localhost",
        maxPoolSize=50,
        minPoolSize=10
    )
    yield
    app.state.db.close()

app = FastAPI(lifespan=lifespan)

@router.get("/v1/data")
async def get_data(request: Request):
    return await request.app.state.db.mydb.collection.find_one()
```

### Pattern 2: HTTP Connection Pool

```javascript
// Use keep-alive connections
const axios = require('axios');
const http = require('http');
const https = require('https');

const httpAgent = new http.Agent({
  keepAlive: true,
  maxSockets: 50,
  maxFreeSockets: 10,
  timeout: 60000
});

const httpsAgent = new https.Agent({
  keepAlive: true,
  maxSockets: 50,
  maxFreeSockets: 10,
  timeout: 60000
});

const client = axios.create({
  httpAgent,
  httpsAgent
});

// Reuse connections across requests
app.get('/v1/external-data', async (req, res) => {
  const response = await client.get('https://external-api.com/data');
  res.json(response.data);
});
```

---

## Rate Limiting

### Pattern 1: Tiered Rate Limits

```python
# Bad: No rate limiting
@router.post("/v1/auth/login")
async def login(credentials: LoginRequest):
    return await auth_service.login(credentials)

# Good: Tiered limits with Redis
from fastapi_limiter.depends import RateLimiter

@router.post("/v1/auth/login", dependencies=[Depends(RateLimiter(times=5, minutes=15))])
async def login(credentials: LoginRequest):
    return await auth_service.login(credentials)

@router.get("/v1/users", dependencies=[Depends(RateLimiter(times=100, minutes=1))])
async def list_users():
    return await user_service.list()
```

### Pattern 2: User-Based Rate Limiting

```javascript
// Different limits based on user tier
const getRateLimit = (user) => {
  const limits = {
    free: { requests: 100, window: 3600 },
    premium: { requests: 1000, window: 3600 },
    enterprise: { requests: 10000, window: 3600 }
  };
  return limits[user.tier] || limits.free;
};

const userRateLimiter = async (req, res, next) => {
  const user = req.user;
  const limit = getRateLimit(user);

  const key = `rl:user:${user.id}`;
  const current = await redis.incr(key);

  if (current === 1) {
    await redis.expire(key, limit.window);
  }

  if (current > limit.requests) {
    return res.status(429).json({
      error: 'Rate limit exceeded',
      retry_after: await redis.ttl(key)
    });
  }

  next();
};
```

---

## Query Optimization

### Pattern 1: Avoid N+1 Queries

```javascript
// Bad: N+1 queries
app.get('/v1/users', async (req, res) => {
  const users = await db.query('SELECT * FROM users LIMIT 100');

  // This executes 100 additional queries!
  for (const user of users) {
    user.orders = await db.query(
      'SELECT * FROM orders WHERE user_id = ?',
      [user.id]
    );
  }

  res.json(users);
});

// Good: Single query with join or batch loading
app.get('/v1/users', async (req, res) => {
  const users = await db.query('SELECT * FROM users LIMIT 100');
  const userIds = users.map(u => u.id);

  // Single query for all orders
  const orders = await db.query(
    'SELECT * FROM orders WHERE user_id IN (?)',
    [userIds]
  );

  // Group orders by user
  const ordersByUser = orders.reduce((acc, order) => {
    if (!acc[order.user_id]) acc[order.user_id] = [];
    acc[order.user_id].push(order);
    return acc;
  }, {});

  users.forEach(user => {
    user.orders = ordersByUser[user.id] || [];
  });

  res.json(users);
});
```

### Pattern 2: Select Only Required Fields

```python
# Bad: Select all fields
@router.get("/v1/products")
async def list_products():
    products = await db.execute("SELECT * FROM products")
    return products

# Good: Select only needed fields
@router.get("/v1/products")
async def list_products():
    products = await db.execute(
        "SELECT id, name, price, image_url FROM products"
    )
    return products
```

### Pattern 3: Use Database Aggregation

```javascript
// Bad: Aggregate in application code
app.get('/v1/analytics/revenue', async (req, res) => {
  const orders = await db.query('SELECT * FROM orders');
  const revenue = orders.reduce((sum, order) => sum + order.total, 0);
  res.json({ revenue });
});

// Good: Use database aggregation
app.get('/v1/analytics/revenue', async (req, res) => {
  const result = await db.query(
    'SELECT SUM(total) as revenue FROM orders'
  );
  res.json({ revenue: result[0].revenue });
});
```

---

## Database Indexing

### Best Practices

```sql
-- Index frequently queried fields
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);

-- Composite indexes for multi-field queries
CREATE INDEX idx_orders_user_status ON orders(user_id, status);
CREATE INDEX idx_products_category_price ON products(category_id, price);

-- Covering indexes (include all queried fields)
CREATE INDEX idx_users_email_name ON users(email, name, created_at);

-- Index for sorting
CREATE INDEX idx_orders_created_at ON orders(created_at DESC);
```

### Monitoring Query Performance

```javascript
// Log slow queries
const logSlowQuery = (query, duration) => {
  if (duration > 1000) { // More than 1 second
    logger.warn({
      message: 'Slow query detected',
      query,
      duration,
      stack: new Error().stack
    });
  }
};

// Wrap database queries
const executeQuery = async (query, params) => {
  const start = Date.now();
  const result = await db.query(query, params);
  const duration = Date.now() - start;
  logSlowQuery(query, duration);
  return result;
};
```

---

## Load Balancing

### Pattern 1: Round-Robin Load Balancing

```nginx
# Nginx configuration
upstream api_servers {
    server api1.example.com:3000 weight=1;
    server api2.example.com:3000 weight=1;
    server api3.example.com:3000 weight=2;  # More capacity

    keepalive 32;  # Connection pooling
}

server {
    listen 80;
    server_name api.example.com;

    location /v1/ {
        proxy_pass http://api_servers;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # Connection timeout
        proxy_connect_timeout 5s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
```

### Pattern 2: Health Checks

```javascript
// Health check endpoint
app.get('/health', async (req, res) => {
  try {
    // Check database connectivity
    await db.query('SELECT 1');

    // Check Redis connectivity
    await redis.ping();

    // Check external dependencies
    const externalApiHealthy = await checkExternalAPI();

    res.json({
      status: 'healthy',
      timestamp: new Date().toISOString(),
      services: {
        database: 'up',
        cache: 'up',
        external_api: externalApiHealthy ? 'up' : 'degraded'
      }
    });
  } catch (error) {
    res.status(503).json({
      status: 'unhealthy',
      error: error.message
    });
  }
});
```

---

## Summary

**Key Performance Optimizations**:

1. **Caching**: Implement Redis caching with proper cache headers and invalidation
2. **Pagination**: Use cursor-based pagination for large datasets
3. **Compression**: Enable GZip compression for API responses
4. **Connection Pooling**: Reuse database and HTTP connections
5. **Rate Limiting**: Protect endpoints with tiered rate limits
6. **Query Optimization**: Avoid N+1 queries, use database aggregation
7. **Database Indexing**: Index frequently queried and sorted fields
8. **Load Balancing**: Distribute traffic across multiple servers

**Performance Monitoring**:
- Track response times with APM tools
- Monitor slow queries
- Set up alerts for high latency
- Use health checks for load balancer routing
- Implement distributed tracing for debugging
