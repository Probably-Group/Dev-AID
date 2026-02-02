---
name: api-expert
version: 2.0.0
description: "API architecture patterns for REST, GraphQL, and gRPC with versioning, rate limiting, and security best practices."
risk_level: MEDIUM
---

# API Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-285: Improper Authorization**
- NEVER: Rely solely on authentication - always check authorization
- ALWAYS: Verify user has permission for specific resource/action

**CWE-918: SSRF**
- NEVER: Fetch user-provided URLs without validation
- ALWAYS: Allowlist domains, block private IPs, validate schemes

**CWE-311: Missing TLS**
- NEVER: Transmit sensitive data over HTTP
- ALWAYS: HTTPS only, HSTS headers, TLS 1.2+

**CWE-770: Missing Rate Limiting**
- NEVER: Unlimited API requests
- ALWAYS: Rate limiting per user/IP, exponential backoff

**CWE-942: Permissive CORS**
- NEVER: `Access-Control-Allow-Origin: *` with credentials
- ALWAYS: Specific origins, validate against allowlist

### 0.3 Risk Level: MEDIUM

**Verification requirements for MEDIUM risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 Authentication & Authorization (CWE-287, CWE-862)

**Principle:** Always authenticate and authorize. Never trust client-side claims.

```typescript
// ❌ WRONG - No auth check
app.get('/api/users/:id', (req, res) => {
  return getUser(req.params.id);
});

// ✅ CORRECT - Auth + authorization
app.get('/api/users/:id', authenticate, async (req, res) => {
  const user = await getUser(req.params.id);

  // Check ownership or admin
  if (user.id !== req.user.id && req.user.role !== 'admin') {
    throw new ForbiddenError('Not authorized');
  }

  return user;
});
```

### 1.2 Rate Limiting (CWE-770)

**Principle:** Rate limit all endpoints. Different limits for auth/unauth users.

```typescript
// ❌ WRONG - No rate limiting
app.post('/api/login', loginHandler);

// ✅ CORRECT - Rate limited
import rateLimit from 'express-rate-limit';

const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 attempts
  message: { error: 'Too many attempts' },
  standardHeaders: true,
  legacyHeaders: false,
});

app.post('/api/login', authLimiter, loginHandler);
```

### 1.3 Input Validation (CWE-20)

**Principle:** Validate all input at API boundary. Use schemas, not manual checks.

### 1.4 Secrets ≠ Code (CWE-798)

**Principle:** API keys from environment. Never expose in responses or logs.

### 1.5 CORS Security (CWE-346)

**Principle:** Strict origin allowlist. Never use `*` in production.

```typescript
// ❌ WRONG - Allow all origins
app.use(cors({ origin: '*' }));

// ✅ CORRECT - Strict allowlist
app.use(cors({
  origin: ['https://app.example.com', 'https://admin.example.com'],
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  credentials: true,
}));
```

### 1.6 Error Handling (CWE-209)

**Principle:** Never expose stack traces or internal details in API errors.

---

## 2. Version Requirements

**ALWAYS use these minimum versions:**

```json
{
  "dependencies": {
    "express": "^4.19.0",
    "fastify": "^4.26.0",
    "zod": "^3.23.0",
    "openapi3-ts": "^4.2.0",
    "@hono/hono": "^4.1.0"
  }
}
```

---

## 3. Code Patterns

### 3.1 WHEN designing RESTful resources

```typescript
// Resource naming and HTTP methods
// GET    /api/users           - List users (paginated)
// POST   /api/users           - Create user
// GET    /api/users/:id       - Get single user
// PUT    /api/users/:id       - Replace user
// PATCH  /api/users/:id       - Update user fields
// DELETE /api/users/:id       - Delete user

// Nested resources
// GET    /api/users/:id/orders     - User's orders
// POST   /api/users/:id/orders     - Create order for user

// ❌ WRONG - Verbs in URL, inconsistent
// GET /api/getUser?id=123
// POST /api/createNewUser
// GET /api/user/delete/123

// ✅ CORRECT - RESTful design
import { z } from 'zod';
import { Hono } from 'hono';
import { zValidator } from '@hono/zod-validator';

const app = new Hono();

// Schema definitions
const UserCreateSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
});

const UserUpdateSchema = UserCreateSchema.partial();

const PaginationSchema = z.object({
  page: z.coerce.number().int().min(1).default(1),
  limit: z.coerce.number().int().min(1).max(100).default(20),
});

// List with pagination
app.get('/api/users', zValidator('query', PaginationSchema), async (c) => {
  const { page, limit } = c.req.valid('query');
  const offset = (page - 1) * limit;

  const [users, total] = await Promise.all([
    db.users.findMany({ skip: offset, take: limit }),
    db.users.count(),
  ]);

  return c.json({
    data: users,
    meta: {
      page,
      limit,
      total,
      totalPages: Math.ceil(total / limit),
    },
  });
});

// Create
app.post('/api/users', zValidator('json', UserCreateSchema), async (c) => {
  const data = c.req.valid('json');
  const user = await db.users.create({ data });

  return c.json(user, 201);
});

// Get single
app.get('/api/users/:id', async (c) => {
  const id = c.req.param('id');
  const user = await db.users.findUnique({ where: { id } });

  if (!user) {
    return c.json({ error: 'User not found' }, 404);
  }

  return c.json(user);
});

// Update (partial)
app.patch('/api/users/:id', zValidator('json', UserUpdateSchema), async (c) => {
  const id = c.req.param('id');
  const data = c.req.valid('json');

  const user = await db.users.update({ where: { id }, data });
  return c.json(user);
});

// Delete
app.delete('/api/users/:id', async (c) => {
  const id = c.req.param('id');
  await db.users.delete({ where: { id } });

  return c.body(null, 204);
});
```

### 3.2 WHEN implementing API versioning

```typescript
// ❌ WRONG - No versioning strategy
app.get('/api/users', getUsersV1);

// ✅ CORRECT - URL path versioning (recommended)
const v1 = new Hono();
const v2 = new Hono();

// V1 API
v1.get('/users', async (c) => {
  const users = await db.users.findMany();
  return c.json(users.map(u => ({
    id: u.id,
    name: u.name,
    email: u.email,
  })));
});

// V2 API - different response shape
v2.get('/users', async (c) => {
  const users = await db.users.findMany();
  return c.json({
    data: users.map(u => ({
      id: u.id,
      attributes: {
        name: u.name,
        email: u.email,
        createdAt: u.createdAt,
      },
    })),
    meta: { version: 'v2' },
  });
});

app.route('/api/v1', v1);
app.route('/api/v2', v2);

// Header-based versioning (alternative)
app.get('/api/users', async (c) => {
  const version = c.req.header('API-Version') || 'v1';

  switch (version) {
    case 'v2':
      return getUsersV2(c);
    default:
      return getUsersV1(c);
  }
});
```

### 3.3 WHEN implementing OpenAPI documentation

```typescript
import { OpenAPIHono, createRoute, z } from '@hono/zod-openapi';

const app = new OpenAPIHono();

// Define schemas with OpenAPI extensions
const UserSchema = z.object({
  id: z.string().uuid().openapi({ example: '123e4567-e89b-12d3-a456-426614174000' }),
  name: z.string().min(1).openapi({ example: 'John Doe' }),
  email: z.string().email().openapi({ example: 'john@example.com' }),
  createdAt: z.string().datetime().openapi({ example: '2024-01-15T10:30:00Z' }),
});

const ErrorSchema = z.object({
  error: z.string().openapi({ example: 'Resource not found' }),
  code: z.string().openapi({ example: 'NOT_FOUND' }),
});

// Define route with full OpenAPI spec
const getUserRoute = createRoute({
  method: 'get',
  path: '/api/users/{id}',
  tags: ['Users'],
  summary: 'Get a user by ID',
  description: 'Retrieves a single user by their unique identifier',
  request: {
    params: z.object({
      id: z.string().uuid().openapi({ description: 'User ID' }),
    }),
  },
  responses: {
    200: {
      description: 'User found',
      content: {
        'application/json': { schema: UserSchema },
      },
    },
    404: {
      description: 'User not found',
      content: {
        'application/json': { schema: ErrorSchema },
      },
    },
  },
  security: [{ bearerAuth: [] }],
});

app.openapi(getUserRoute, async (c) => {
  const { id } = c.req.valid('param');
  const user = await db.users.findUnique({ where: { id } });

  if (!user) {
    return c.json({ error: 'User not found', code: 'NOT_FOUND' }, 404);
  }

  return c.json(user);
});

// Serve OpenAPI spec
app.doc('/api/openapi.json', {
  openapi: '3.1.0',
  info: {
    title: 'My API',
    version: '1.0.0',
    description: 'API documentation',
  },
  servers: [
    { url: 'https://api.example.com', description: 'Production' },
    { url: 'http://localhost:3000', description: 'Development' },
  ],
  security: [{ bearerAuth: [] }],
});
```

### 3.4 WHEN implementing error handling

```typescript
import { HTTPException } from 'hono/http-exception';
import { z } from 'zod';

// Custom error classes
class ApiError extends Error {
  constructor(
    public statusCode: number,
    public code: string,
    message: string,
    public details?: unknown
  ) {
    super(message);
  }
}

class NotFoundError extends ApiError {
  constructor(resource: string) {
    super(404, 'NOT_FOUND', `${resource} not found`);
  }
}

class ValidationError extends ApiError {
  constructor(errors: z.ZodError) {
    super(400, 'VALIDATION_ERROR', 'Invalid request data',
      errors.issues.map(i => ({
        path: i.path.join('.'),
        message: i.message,
      }))
    );
  }
}

// Global error handler
app.onError((err, c) => {
  // Log error internally (with stack trace)
  console.error('API Error:', err);

  // Zod validation errors
  if (err instanceof z.ZodError) {
    return c.json({
      error: 'Validation failed',
      code: 'VALIDATION_ERROR',
      details: err.issues.map(i => ({
        path: i.path.join('.'),
        message: i.message,
      })),
    }, 400);
  }

  // Custom API errors
  if (err instanceof ApiError) {
    return c.json({
      error: err.message,
      code: err.code,
      details: err.details,
    }, err.statusCode);
  }

  // Unknown errors - don't expose details
  return c.json({
    error: 'Internal server error',
    code: 'INTERNAL_ERROR',
  }, 500);
});

// Usage
app.get('/api/users/:id', async (c) => {
  const user = await db.users.findUnique({
    where: { id: c.req.param('id') }
  });

  if (!user) {
    throw new NotFoundError('User');
  }

  return c.json(user);
});
```

### 3.5 WHEN implementing pagination

```typescript
import { z } from 'zod';

// Cursor-based pagination (recommended for large datasets)
const CursorPaginationSchema = z.object({
  cursor: z.string().optional(),
  limit: z.coerce.number().int().min(1).max(100).default(20),
});

app.get('/api/posts', zValidator('query', CursorPaginationSchema), async (c) => {
  const { cursor, limit } = c.req.valid('query');

  const posts = await db.posts.findMany({
    take: limit + 1, // Get one extra to check if more exist
    cursor: cursor ? { id: cursor } : undefined,
    orderBy: { createdAt: 'desc' },
  });

  const hasMore = posts.length > limit;
  const data = hasMore ? posts.slice(0, -1) : posts;
  const nextCursor = hasMore ? data[data.length - 1].id : null;

  return c.json({
    data,
    pagination: {
      nextCursor,
      hasMore,
    },
  });
});

// Offset-based pagination (simpler, but slower for large datasets)
const OffsetPaginationSchema = z.object({
  page: z.coerce.number().int().min(1).default(1),
  limit: z.coerce.number().int().min(1).max(100).default(20),
  sortBy: z.enum(['createdAt', 'name', 'updatedAt']).default('createdAt'),
  sortOrder: z.enum(['asc', 'desc']).default('desc'),
});

app.get('/api/users', zValidator('query', OffsetPaginationSchema), async (c) => {
  const { page, limit, sortBy, sortOrder } = c.req.valid('query');
  const skip = (page - 1) * limit;

  const [data, total] = await Promise.all([
    db.users.findMany({
      skip,
      take: limit,
      orderBy: { [sortBy]: sortOrder },
    }),
    db.users.count(),
  ]);

  return c.json({
    data,
    pagination: {
      page,
      limit,
      total,
      totalPages: Math.ceil(total / limit),
      hasNext: page * limit < total,
      hasPrev: page > 1,
    },
  });
});
```

### 3.6 WHEN implementing API authentication

```typescript
import { jwt, sign, verify } from 'hono/jwt';
import { z } from 'zod';

const JWT_SECRET = process.env.JWT_SECRET!;

// Login endpoint
const LoginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

app.post('/api/auth/login', zValidator('json', LoginSchema), async (c) => {
  const { email, password } = c.req.valid('json');

  const user = await db.users.findUnique({ where: { email } });
  if (!user || !await verifyPassword(password, user.passwordHash)) {
    return c.json({ error: 'Invalid credentials' }, 401);
  }

  const token = await sign({
    sub: user.id,
    email: user.email,
    role: user.role,
    exp: Math.floor(Date.now() / 1000) + 60 * 60 * 24, // 24 hours
  }, JWT_SECRET);

  return c.json({
    token,
    expiresIn: 86400,
    user: {
      id: user.id,
      email: user.email,
      name: user.name,
    },
  });
});

// JWT middleware
const authMiddleware = jwt({ secret: JWT_SECRET });

// Protected routes
app.use('/api/protected/*', authMiddleware);

app.get('/api/protected/me', async (c) => {
  const payload = c.get('jwtPayload');
  const user = await db.users.findUnique({ where: { id: payload.sub } });
  return c.json(user);
});

// Role-based authorization middleware
const requireRole = (...roles: string[]) => {
  return async (c: Context, next: Next) => {
    const payload = c.get('jwtPayload');

    if (!roles.includes(payload.role)) {
      return c.json({ error: 'Forbidden' }, 403);
    }

    await next();
  };
};

app.get('/api/admin/users', authMiddleware, requireRole('admin'), async (c) => {
  const users = await db.users.findMany();
  return c.json(users);
});
```

### 3.7 WHEN implementing request/response logging

```typescript
import { logger } from 'hono/logger';
import { timing } from 'hono/timing';

// Basic logging
app.use('*', logger());

// Custom logging with request ID
app.use('*', async (c, next) => {
  const requestId = c.req.header('x-request-id') || crypto.randomUUID();
  c.set('requestId', requestId);
  c.header('X-Request-ID', requestId);

  const start = Date.now();

  await next();

  const duration = Date.now() - start;

  // Structured logging (JSON)
  console.log(JSON.stringify({
    timestamp: new Date().toISOString(),
    requestId,
    method: c.req.method,
    path: c.req.path,
    status: c.res.status,
    duration,
    userAgent: c.req.header('user-agent'),
    // Don't log sensitive data!
  }));
});

// Timing headers for performance debugging
app.use('*', timing());
```

---

## 4. Anti-Patterns

**NEVER:**
- Use verbs in REST URLs (`/getUser`, `/createUser`)
- Return 200 for errors (use proper status codes)
- Expose internal IDs or stack traces in errors
- Allow unlimited pagination (cap at 100)
- Skip input validation on any endpoint
- Use `*` for CORS origins in production
- Log sensitive data (passwords, tokens, PII)

---

## 5. Testing

**ALWAYS write API tests:**

```typescript
import { describe, it, expect, beforeAll, afterAll } from 'vitest';

describe('Users API', () => {
  let authToken: string;

  beforeAll(async () => {
    // Login to get token
    const res = await app.request('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: 'test@example.com',
        password: 'password123',
      }),
    });
    const data = await res.json();
    authToken = data.token;
  });

  it('returns 401 without auth', async () => {
    const res = await app.request('/api/protected/me');
    expect(res.status).toBe(401);
  });

  it('returns user with valid token', async () => {
    const res = await app.request('/api/protected/me', {
      headers: { Authorization: `Bearer ${authToken}` },
    });
    expect(res.status).toBe(200);
    const data = await res.json();
    expect(data).toHaveProperty('id');
    expect(data).toHaveProperty('email');
  });

  it('validates input and returns 400', async () => {
    const res = await app.request('/api/users', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${authToken}`,
      },
      body: JSON.stringify({ email: 'invalid' }),
    });
    expect(res.status).toBe(400);
    const data = await res.json();
    expect(data.code).toBe('VALIDATION_ERROR');
  });

  it('paginates results correctly', async () => {
    const res = await app.request('/api/users?page=1&limit=10', {
      headers: { Authorization: `Bearer ${authToken}` },
    });
    expect(res.status).toBe(200);
    const data = await res.json();
    expect(data).toHaveProperty('data');
    expect(data).toHaveProperty('pagination');
    expect(data.pagination.limit).toBe(10);
  });
});
```

---

## 6. Pre-Generation Checklist

**BEFORE generating any API code:**

- [ ] Authentication on protected endpoints
- [ ] Authorization checks (ownership, roles)
- [ ] Rate limiting configured
- [ ] Input validation with Zod schemas
- [ ] Proper HTTP status codes
- [ ] Error responses don't leak internals
- [ ] CORS configured with specific origins
- [ ] API versioning strategy defined
- [ ] Pagination on list endpoints
- [ ] OpenAPI documentation generated
