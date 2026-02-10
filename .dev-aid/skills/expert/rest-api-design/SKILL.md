---
name: rest-api-design
version: 2.0.0
description: "RESTful API design patterns with resource modeling, HATEOAS, pagination, versioning, OpenAPI specifications, and proper HTTP semantics. Use when designing REST endpoints, writing OpenAPI specs, implementing pagination strategies, or structuring API resource hierarchies. Do NOT use for GraphQL APIs (use graphql-expert) or gRPC service definitions."
risk_level: MEDIUM
---

# REST API Design - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-285: IDOR (Insecure Direct Object Reference)**
- NEVER: `/api/users/123/orders` without verifying user 123 is requester
- ALWAYS: Check ownership/permissions for every resource access

**CWE-359: Mass Assignment**
- NEVER: `user.update(**request.json())` - updating all fields from input
- ALWAYS: Whitelist allowed fields, use DTOs/schemas

**CWE-204: Information Exposure in Response**
- NEVER: Return internal IDs, stack traces, or sensitive fields
- ALWAYS: Explicit response schemas, filter sensitive data

**CWE-400: Unbounded Resource Consumption**
- NEVER: Return unlimited results: `GET /users` returning 1M records
- ALWAYS: Pagination with max page size, cursor-based for large datasets

### 0.3 Risk Level: MEDIUM

**Verification requirements for MEDIUM risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 Authentication Required (CWE-306)

**Principle:** All API endpoints must require authentication except public documentation.

```yaml
# ❌ WRONG - No authentication
paths:
  /api/users:
    get:
      responses:
        200:
          description: List users

# ✅ CORRECT - Authentication required
paths:
  /api/users:
    get:
      security:
        - bearerAuth: []
      responses:
        200:
          description: List users
```

### 1.2 Authorization on Resources (CWE-862)

**Principle:** Check authorization on every resource access. Never rely on URL obscurity.

### 1.3 Input Validation (CWE-20)

**Principle:** Define schemas for all request bodies and parameters. Reject invalid requests.

### 1.4 Rate Limiting (CWE-770)

**Principle:** Rate limit all endpoints. Stricter limits on auth endpoints.

### 1.5 CORS Security (CWE-346)

**Principle:** Strict origin allowlists. Never use `*` in production.

### 1.6 Error Disclosure (CWE-209)

**Principle:** Return consistent error shapes. Never expose stack traces or internal details.

---

## 2. Version Requirements

**ALWAYS use these API standards:**

```yaml
openapi: 3.1.0
info:
  title: API Name
  version: 1.0.0
```

**Versioning:** URL path versioning (e.g., `/api/v1/`)

---

## 3. Code Patterns

### 3.1 WHEN designing resource URLs

```yaml
# ❌ WRONG - Verbs in URLs, inconsistent naming
paths:
  /api/getUsers:
  /api/createUser:
  /api/user/delete/{id}:
  /api/fetch-all-orders:

# ✅ CORRECT - Noun resources, consistent plural naming
paths:
  # Collection resources
  /api/v1/users:
    get:
      summary: List users
      operationId: listUsers
      parameters:
        - $ref: '#/components/parameters/Page'
        - $ref: '#/components/parameters/Limit'
        - name: status
          in: query
          schema:
            type: string
            enum: [active, inactive]
      responses:
        200:
          description: User list
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserList'
    post:
      summary: Create user
      operationId: createUser
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUser'
      responses:
        201:
          description: User created
          headers:
            Location:
              schema:
                type: string
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'

  # Individual resources
  /api/v1/users/{userId}:
    parameters:
      - name: userId
        in: path
        required: true
        schema:
          type: string
          format: uuid
    get:
      summary: Get user
      operationId: getUser
      responses:
        200:
          $ref: '#/components/responses/User'
        404:
          $ref: '#/components/responses/NotFound'
    patch:
      summary: Update user
      operationId: updateUser
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UpdateUser'
      responses:
        200:
          $ref: '#/components/responses/User'
    delete:
      summary: Delete user
      operationId: deleteUser
      responses:
        204:
          description: User deleted

  # Nested resources
  /api/v1/users/{userId}/orders:
    get:
      summary: List user's orders
      operationId: listUserOrders
```

### 3.2 WHEN defining request/response schemas

```yaml
components:
  schemas:
    # Base entity with timestamps
    User:
      type: object
      required:
        - id
        - email
        - name
        - createdAt
      properties:
        id:
          type: string
          format: uuid
          readOnly: true
          example: "550e8400-e29b-41d4-a716-446655440000"
        email:
          type: string
          format: email
          example: "user@example.com"
        name:
          type: string
          minLength: 1
          maxLength: 100
          example: "John Doe"
        role:
          type: string
          enum: [user, admin]
          default: user
        createdAt:
          type: string
          format: date-time
          readOnly: true
        updatedAt:
          type: string
          format: date-time
          readOnly: true

    # Create request (no ID, no read-only fields)
    CreateUser:
      type: object
      required:
        - email
        - name
        - password
      properties:
        email:
          type: string
          format: email
        name:
          type: string
          minLength: 1
          maxLength: 100
        password:
          type: string
          format: password
          minLength: 8
          writeOnly: true

    # Update request (all optional)
    UpdateUser:
      type: object
      properties:
        email:
          type: string
          format: email
        name:
          type: string
          minLength: 1
          maxLength: 100

    # Paginated list response
    UserList:
      type: object
      required:
        - data
        - meta
      properties:
        data:
          type: array
          items:
            $ref: '#/components/schemas/User'
        meta:
          $ref: '#/components/schemas/PaginationMeta'

    PaginationMeta:
      type: object
      required:
        - page
        - limit
        - total
        - totalPages
      properties:
        page:
          type: integer
          minimum: 1
        limit:
          type: integer
          minimum: 1
          maximum: 100
        total:
          type: integer
          minimum: 0
        totalPages:
          type: integer
          minimum: 0
        hasNext:
          type: boolean
        hasPrev:
          type: boolean
```

### 3.3 WHEN defining error responses

```yaml
components:
  schemas:
    Error:
      type: object
      required:
        - error
        - code
      properties:
        error:
          type: string
          description: Human-readable error message
        code:
          type: string
          description: Machine-readable error code
          example: "VALIDATION_ERROR"
        details:
          type: array
          items:
            type: object
            properties:
              field:
                type: string
              message:
                type: string
        requestId:
          type: string
          description: Request ID for debugging

  responses:
    BadRequest:
      description: Invalid request
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            error: "Validation failed"
            code: "VALIDATION_ERROR"
            details:
              - field: "email"
                message: "Invalid email format"

    Unauthorized:
      description: Authentication required
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            error: "Authentication required"
            code: "UNAUTHORIZED"

    Forbidden:
      description: Access denied
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            error: "You don't have permission to access this resource"
            code: "FORBIDDEN"

    NotFound:
      description: Resource not found
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            error: "User not found"
            code: "NOT_FOUND"

    TooManyRequests:
      description: Rate limit exceeded
      headers:
        Retry-After:
          schema:
            type: integer
        X-RateLimit-Limit:
          schema:
            type: integer
        X-RateLimit-Remaining:
          schema:
            type: integer
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            error: "Too many requests"
            code: "RATE_LIMITED"
```

### 3.4 WHEN implementing HTTP methods correctly

```yaml
# ❌ WRONG - Using GET for mutations
paths:
  /api/users/{id}/activate:
    get:  # GET shouldn't change state
      summary: Activate user

# ✅ CORRECT - Proper method usage
paths:
  /api/users/{id}:
    # GET - Retrieve (safe, cacheable, idempotent)
    get:
      summary: Get a specific user
      responses:
        200:
          description: User details
        304:
          description: Not modified (cached)

    # PUT - Replace entire resource (idempotent)
    put:
      summary: Replace user
      description: Replaces all user fields. Missing fields are cleared.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUser'
      responses:
        200:
          description: User replaced
        201:
          description: User created (if didn't exist)

    # PATCH - Partial update (not necessarily idempotent)
    patch:
      summary: Update user fields
      description: Updates only provided fields.
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UpdateUser'
      responses:
        200:
          description: User updated

    # DELETE - Remove resource (idempotent)
    delete:
      summary: Delete user
      responses:
        204:
          description: User deleted
        404:
          description: User not found

  # Actions as sub-resources
  /api/users/{id}/actions/activate:
    post:  # POST for non-idempotent actions
      summary: Activate user account
      responses:
        200:
          description: User activated
```

### 3.5 WHEN implementing pagination

```yaml
# ❌ WRONG - No pagination limits
paths:
  /api/users:
    get:
      parameters:
        - name: limit
          in: query
          schema:
            type: integer  # No max limit!

# ✅ CORRECT - Bounded pagination
components:
  parameters:
    Page:
      name: page
      in: query
      description: Page number (1-indexed)
      schema:
        type: integer
        minimum: 1
        default: 1
    Limit:
      name: limit
      in: query
      description: Items per page
      schema:
        type: integer
        minimum: 1
        maximum: 100
        default: 20
    Cursor:
      name: cursor
      in: query
      description: Cursor for cursor-based pagination
      schema:
        type: string

paths:
  /api/users:
    get:
      parameters:
        - $ref: '#/components/parameters/Page'
        - $ref: '#/components/parameters/Limit'
        - name: sort
          in: query
          schema:
            type: string
            enum: [createdAt, name, email]
            default: createdAt
        - name: order
          in: query
          schema:
            type: string
            enum: [asc, desc]
            default: desc
      responses:
        200:
          description: Paginated user list
          headers:
            Link:
              schema:
                type: string
              description: |
                Links to related pages:
                <https://api.example.com/users?page=2>; rel="next",
                <https://api.example.com/users?page=10>; rel="last"
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserList'
```

### 3.6 WHEN implementing filtering and search

```yaml
paths:
  /api/users:
    get:
      summary: List users with filtering
      parameters:
        # Exact match filters
        - name: status
          in: query
          schema:
            type: string
            enum: [active, inactive, pending]
        - name: role
          in: query
          schema:
            type: string
            enum: [user, admin]

        # Range filters
        - name: createdAfter
          in: query
          schema:
            type: string
            format: date-time
        - name: createdBefore
          in: query
          schema:
            type: string
            format: date-time

        # Full-text search
        - name: q
          in: query
          description: Search query (searches name and email)
          schema:
            type: string
            minLength: 2
            maxLength: 100

        # Multiple values
        - name: ids
          in: query
          description: Filter by multiple IDs
          schema:
            type: array
            items:
              type: string
              format: uuid
            maxItems: 50
          style: form
          explode: false  # ids=1,2,3

  # Complex search as POST
  /api/users/search:
    post:
      summary: Advanced user search
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                filters:
                  type: array
                  items:
                    type: object
                    required: [field, operator, value]
                    properties:
                      field:
                        type: string
                        enum: [name, email, createdAt, role]
                      operator:
                        type: string
                        enum: [eq, ne, gt, gte, lt, lte, contains]
                      value:
                        oneOf:
                          - type: string
                          - type: number
                          - type: boolean
                sort:
                  type: array
                  items:
                    type: object
                    properties:
                      field:
                        type: string
                      order:
                        type: string
                        enum: [asc, desc]
```

### 3.7 WHEN implementing versioning

```yaml
# URL Path Versioning (Recommended)
servers:
  - url: https://api.example.com/v1
    description: Version 1 (current)
  - url: https://api.example.com/v2
    description: Version 2 (beta)

paths:
  /users:  # Full path: /v1/users
    get:
      summary: List users (v1)
      deprecated: false

# Deprecation headers
components:
  headers:
    Deprecation:
      schema:
        type: string
        format: date-time
      description: When this endpoint will be removed
    Sunset:
      schema:
        type: string
        format: date-time
      description: When this endpoint will stop working
    Link:
      schema:
        type: string
      description: Link to newer version

# Example deprecated endpoint
paths:
  /users:
    get:
      deprecated: true
      summary: List users (deprecated - use v2)
      responses:
        200:
          headers:
            Deprecation:
              schema:
                type: string
              example: "2024-06-01T00:00:00Z"
            Sunset:
              schema:
                type: string
              example: "2025-01-01T00:00:00Z"
            Link:
              schema:
                type: string
              example: "</v2/users>; rel=\"successor-version\""
```

---

## 4. Anti-Patterns

**NEVER:**
- Use verbs in resource URLs (`/getUsers`, `/createUser`)
- Return 200 for all responses (use proper status codes)
- Return different error shapes
- Skip pagination on list endpoints
- Allow unlimited page sizes
- Use query params for sensitive data
- Include passwords in responses
- Expose internal IDs or implementation details

---

## 5. Testing

**ALWAYS write API contract tests:**

```typescript
import { describe, it, expect } from 'vitest';

describe('REST API Contract', () => {
  describe('GET /api/v1/users', () => {
    it('returns paginated list', async () => {
      const response = await fetch('/api/v1/users?page=1&limit=10');
      expect(response.status).toBe(200);

      const body = await response.json();
      expect(body).toHaveProperty('data');
      expect(body).toHaveProperty('meta');
      expect(body.meta).toHaveProperty('page', 1);
      expect(body.meta).toHaveProperty('limit', 10);
      expect(body.meta).toHaveProperty('total');
    });

    it('enforces max limit', async () => {
      const response = await fetch('/api/v1/users?limit=1000');
      expect(response.status).toBe(200);

      const body = await response.json();
      expect(body.meta.limit).toBeLessThanOrEqual(100);
    });
  });

  describe('POST /api/v1/users', () => {
    it('creates user with 201', async () => {
      const response = await fetch('/api/v1/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'test@example.com',
          name: 'Test User',
          password: 'securePassword123',
        }),
      });

      expect(response.status).toBe(201);
      expect(response.headers.get('Location')).toMatch(/\/users\/[\w-]+/);
    });

    it('returns 400 for invalid data', async () => {
      const response = await fetch('/api/v1/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'invalid' }),
      });

      expect(response.status).toBe(400);
      const body = await response.json();
      expect(body.code).toBe('VALIDATION_ERROR');
    });
  });

  describe('DELETE /api/v1/users/{id}', () => {
    it('returns 204 on success', async () => {
      const response = await fetch('/api/v1/users/123', { method: 'DELETE' });
      expect(response.status).toBe(204);
    });

    it('is idempotent (204 even if not found)', async () => {
      const response = await fetch('/api/v1/users/nonexistent', { method: 'DELETE' });
      expect([204, 404]).toContain(response.status);
    });
  });
});
```

---

## 6. Pre-Generation Checklist

**BEFORE generating any REST API design:**

- [ ] Authentication required on all endpoints
- [ ] Authorization checked per resource
- [ ] Proper HTTP methods (GET safe, PUT/DELETE idempotent)
- [ ] Consistent resource naming (nouns, plural)
- [ ] Pagination with max limit enforced
- [ ] Standard error response shape
- [ ] Proper status codes (201 create, 204 delete, etc.)
- [ ] Request/response schemas defined
- [ ] Rate limiting configured
- [ ] API versioning strategy defined

**Templates**: See `assets/` for reusable output templates.

---

**Performance**: Quality over speed. Verify all code examples compile. Never skip security checks. See `template-references/performance-notes.md` for full guidelines.