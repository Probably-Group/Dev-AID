## 5. Implementation Patterns

### 4.1 Resource Design

```typescript
// Collection operations
GET    /api/v1/users              // List users
POST   /api/v1/users              // Create user

// Instance operations
GET    /api/v1/users/{id}         // Get user
PUT    /api/v1/users/{id}         // Replace user
PATCH  /api/v1/users/{id}         // Update user
DELETE /api/v1/users/{id}         // Delete user

// Nested resources
GET    /api/v1/users/{id}/orders  // Get user's orders
POST   /api/v1/users/{id}/orders  // Create order for user

// Actions (when necessary)
POST   /api/v1/users/{id}/verify  // Trigger verification
```

### 4.2 Request/Response Format

```typescript
// Consistent response envelope
interface APIResponse<T> {
  data: T;
  meta?: { pagination?: PaginationMeta; timestamp: string; requestId: string; };
}

interface APIError {
  error: { code: string; message: string; details?: ValidationError[]; };
}
```

### 4.3 Pagination

```typescript
// Cursor-based (recommended) - returns nextCursor in meta.pagination
GET /api/v1/users?limit=20&cursor=eyJpZCI6MTAwfQ

// Offset-based (simpler but O(n))
GET /api/v1/users?limit=20&offset=40
```

### 4.4 Filtering, Sorting, and Versioning

```typescript
// Filtering and sorting
GET /api/v1/users?status=active&role=admin&sort=created_at:desc
GET /api/v1/users?fields=id,name,email  // Field selection

// URL path versioning (recommended)
GET /api/v1/users
GET /api/v2/users

// Deprecation headers for old versions
res.set("Deprecation", "true");
res.set("Sunset", "Sat, 01 Jun 2025 00:00:00 GMT");
```

### 4.5 Authentication

```typescript
// Bearer token authentication
app.use("/api", (req, res, next) => {
  const authHeader = req.headers.authorization;
  if (!authHeader?.startsWith("Bearer ")) {
    return res.status(401).json({ error: { code: "UNAUTHORIZED", message: "Bearer token required" }});
  }
  try {
    req.user = jwt.verify(authHeader.substring(7), process.env.JWT_SECRET);
    next();
  } catch {
    return res.status(401).json({ error: { code: "INVALID_TOKEN", message: "Invalid or expired token" }});
  }
});
```

---

