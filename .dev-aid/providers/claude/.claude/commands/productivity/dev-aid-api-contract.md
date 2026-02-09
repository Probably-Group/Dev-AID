---
name: dev-aid-api-contract
description: Generate OpenAPI contracts, TypeScript clients, and MSW mocks from data models
category: productivity
version: 1.0.0
author: Dev-AID Team (https://probably.group)
---

# API Contract Generator - Contract-First Development

Generate complete API implementation from data models: OpenAPI spec, TypeScript client, MSW mocks, tests, and validation.

## Purpose

Unblock frontend/backend parallel development:
- **Frontend** can develop against mocks immediately
- **Backend** implements to match the contract
- **Contract** serves as single source of truth
- **Tests** verify both sides match the contract

## Task

### 1. Analyze Input Model

Accept model from various sources:
- TypeScript interface/type
- Zod schema
- JSON Schema
- Python Pydantic model
- Existing code file

**Example inputs:**

```typescript
// TypeScript interface
interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user';
  createdAt: Date;
}

// Or Zod schema
const UserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  name: z.string().min(1),
  role: z.enum(['admin', 'user']),
  createdAt: z.date()
});
```

### 2. Generate OpenAPI 3.1 Specification

Create comprehensive OpenAPI spec:

```yaml
# File: api/user-api.yaml
openapi: 3.1.0
info:
  title: User API
  version: 1.0.0
  description: User management endpoints

servers:
  - url: http://localhost:3000/api
    description: Development server
  - url: https://api.example.com
    description: Production server

components:
  schemas:
    User:
      type: object
      required: [id, email, name, role, createdAt]
      properties:
        id:
          type: string
          format: uuid
          description: Unique user identifier
        email:
          type: string
          format: email
          description: User email address
        name:
          type: string
          minLength: 1
          description: User full name
        role:
          type: string
          enum: [admin, user]
          description: User role
        createdAt:
          type: string
          format: date-time
          description: Account creation timestamp

    CreateUserRequest:
      type: object
      required: [email, name, role]
      properties:
        email:
          type: string
          format: email
        name:
          type: string
          minLength: 1
        role:
          type: string
          enum: [admin, user]
          default: user

    ErrorResponse:
      type: object
      required: [error, message]
      properties:
        error:
          type: string
        message:
          type: string
        details:
          type: object

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

paths:
  /users:
    get:
      summary: List all users
      operationId: listUsers
      tags: [Users]
      security:
        - bearerAuth: []
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            minimum: 1
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 20
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
                  pagination:
                    type: object
                    properties:
                      page: { type: integer }
                      limit: { type: integer }
                      total: { type: integer }
        '401':
          description: Unauthorized
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

    post:
      summary: Create new user
      operationId: createUser
      tags: [Users]
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
      responses:
        '201':
          description: User created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '400':
          description: Validation error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

  /users/{userId}:
    get:
      summary: Get user by ID
      operationId: getUser
      tags: [Users]
      security:
        - bearerAuth: []
      parameters:
        - name: userId
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: User found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          description: User not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'

    put:
      summary: Update user
      operationId: updateUser
      tags: [Users]
      security:
        - bearerAuth: []
      parameters:
        - name: userId
          in: path
          required: true
          schema:
            type: string
            format: uuid
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
      responses:
        '200':
          description: User updated
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'

    delete:
      summary: Delete user
      operationId: deleteUser
      tags: [Users]
      security:
        - bearerAuth: []
      parameters:
        - name: userId
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '204':
          description: User deleted
        '404':
          description: User not found
```

### 3. Generate TypeScript Client

Using `openapi-typescript` and `openapi-fetch`:

```typescript
// File: src/api/user-client.ts
/**
 * Auto-generated TypeScript client for User API
 * DO NOT EDIT MANUALLY - regenerate with /dev-aid-api-contract
 */

import createClient, { type Middleware } from 'openapi-fetch';
import type { paths, components } from './user-api.types';

// Type exports for convenience
export type User = components['schemas']['User'];
export type CreateUserRequest = components['schemas']['CreateUserRequest'];
export type ErrorResponse = components['schemas']['ErrorResponse'];

// Client configuration
export const createUserClient = (baseUrl: string, token?: string) => {
  const authMiddleware: Middleware = {
    async onRequest(req) {
      if (token) {
        req.headers.set('Authorization', `Bearer ${token}`);
      }
      return req;
    },
  };

  const client = createClient<paths>({
    baseUrl,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  client.use(authMiddleware);

  return {
    // List users
    async listUsers(params?: { page?: number; limit?: number }) {
      const { data, error } = await client.GET('/users', {
        params: { query: params },
      });
      if (error) throw new Error(error.message);
      return data;
    },

    // Get user by ID
    async getUser(userId: string) {
      const { data, error } = await client.GET('/users/{userId}', {
        params: { path: { userId } },
      });
      if (error) throw new Error(error.message);
      return data;
    },

    // Create user
    async createUser(user: CreateUserRequest) {
      const { data, error} = await client.POST('/users', {
        body: user,
      });
      if (error) throw new Error(error.message);
      return data;
    },

    // Update user
    async updateUser(userId: string, user: CreateUserRequest) {
      const { data, error } = await client.PUT('/users/{userId}', {
        params: { path: { userId } },
        body: user,
      });
      if (error) throw new Error(error.message);
      return data;
    },

    // Delete user
    async deleteUser(userId: string) {
      const { error } = await client.DELETE('/users/{userId}', {
        params: { path: { userId } },
      });
      if (error) throw new Error(error.message);
    },
  };
};

// Export default client instance
export const userApi = createUserClient(
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000/api'
);
```

### 4. Generate MSW Mock Handlers

Mock Service Worker for frontend development:

```typescript
// File: src/mocks/user.mocks.ts
/**
 * MSW mock handlers for User API
 * Enables frontend development without backend
 */

import { http, HttpResponse, delay } from 'msw';
import type { User } from '../api/user-client';

// Mock data
const mockUsers: User[] = [
  {
    id: '550e8400-e29b-41d4-a716-446655440000',
    email: 'admin@example.com',
    name: 'Admin User',
    role: 'admin',
    createdAt: new Date('2024-01-01'),
  },
  {
    id: '550e8400-e29b-41d4-a716-446655440001',
    email: 'user@example.com',
    name: 'Regular User',
    role: 'user',
    createdAt: new Date('2024-01-15'),
  },
];

export const userHandlers = [
  // GET /users - List users
  http.get('/api/users', async ({ request }) => {
    await delay(100); // Simulate network delay

    const url = new URL(request.url);
    const page = Number(url.searchParams.get('page')) || 1;
    const limit = Number(url.searchParams.get('limit')) || 20;

    const start = (page - 1) * limit;
    const end = start + limit;
    const paginatedUsers = mockUsers.slice(start, end);

    return HttpResponse.json({
      data: paginatedUsers,
      pagination: {
        page,
        limit,
        total: mockUsers.length,
      },
    });
  }),

  // GET /users/:userId - Get user
  http.get('/api/users/:userId', async ({ params }) => {
    await delay(100);

    const user = mockUsers.find((u) => u.id === params.userId);

    if (!user) {
      return HttpResponse.json(
        { error: 'NOT_FOUND', message: 'User not found' },
        { status: 404 }
      );
    }

    return HttpResponse.json(user);
  }),

  // POST /users - Create user
  http.post('/api/users', async ({ request }) => {
    await delay(150);

    const body = await request.json() as CreateUserRequest;

    // Validation
    if (!body.email || !body.name) {
      return HttpResponse.json(
        { error: 'VALIDATION_ERROR', message: 'Email and name required' },
        { status: 400 }
      );
    }

    const newUser: User = {
      id: crypto.randomUUID(),
      ...body,
      role: body.role || 'user',
      createdAt: new Date(),
    };

    mockUsers.push(newUser);

    return HttpResponse.json(newUser, { status: 201 });
  }),

  // PUT /users/:userId - Update user
  http.put('/api/users/:userId', async ({ params, request }) => {
    await delay(150);

    const userId = params.userId as string;
    const userIndex = mockUsers.findIndex((u) => u.id === userId);

    if (userIndex === -1) {
      return HttpResponse.json(
        { error: 'NOT_FOUND', message: 'User not found' },
        { status: 404 }
      );
    }

    const body = await request.json() as CreateUserRequest;
    mockUsers[userIndex] = {
      ...mockUsers[userIndex],
      ...body,
    };

    return HttpResponse.json(mockUsers[userIndex]);
  }),

  // DELETE /users/:userId - Delete user
  http.delete('/api/users/:userId', async ({ params }) => {
    await delay(100);

    const userId = params.userId as string;
    const userIndex = mockUsers.findIndex((u) => u.id === userId);

    if (userIndex === -1) {
      return HttpResponse.json(
        { error: 'NOT_FOUND', message: 'User not found' },
        { status: 404 }
      );
    }

    mockUsers.splice(userIndex, 1);

    return new HttpResponse(null, { status: 204 });
  }),
];

// Browser setup
export const setupMocks = async () => {
  if (typeof window === 'undefined') {
    const { setupServer } = await import('msw/node');
    const server = setupServer(...userHandlers);
    server.listen();
    return server;
  } else {
    const { setupWorker } = await import('msw/browser');
    const worker = setupWorker(...userHandlers);
    await worker.start();
    return worker;
  }
};
```

### 5. Generate API Tests

Contract validation tests:

```typescript
// File: src/api/__tests__/user-api.test.ts
/**
 * Contract tests for User API
 * Ensures client matches OpenAPI specification
 */

import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { setupMocks } from '../../mocks/user.mocks';
import { createUserClient } from '../user-client';

describe('User API Contract Tests', () => {
  let mockServer: any;
  let client: ReturnType<typeof createUserClient>;

  beforeAll(async () => {
    mockServer = await setupMocks();
    client = createUserClient('http://localhost:3000/api');
  });

  afterAll(() => {
    mockServer?.close();
  });

  describe('GET /users', () => {
    it('returns paginated users', async () => {
      const response = await client.listUsers({ page: 1, limit: 10 });

      expect(response.data).toBeInstanceOf(Array);
      expect(response.pagination).toMatchObject({
        page: 1,
        limit: 10,
        total: expect.any(Number),
      });
    });

    it('respects pagination params', async () => {
      const response = await client.listUsers({ page: 2, limit: 1 });

      expect(response.data).toHaveLength(1);
      expect(response.pagination.page).toBe(2);
    });
  });

  describe('GET /users/:userId', () => {
    it('returns user when found', async () => {
      const userId = '550e8400-e29b-41d4-a716-446655440000';
      const user = await client.getUser(userId);

      expect(user).toMatchObject({
        id: userId,
        email: expect.any(String),
        name: expect.any(String),
        role: expect.stringMatching(/^(admin|user)$/),
        createdAt: expect.any(Date),
      });
    });

    it('throws when user not found', async () => {
      await expect(
        client.getUser('00000000-0000-0000-0000-000000000000')
      ).rejects.toThrow();
    });
  });

  describe('POST /users', () => {
    it('creates user with valid data', async () => {
      const newUser = await client.createUser({
        email: 'new@example.com',
        name: 'New User',
        role: 'user',
      });

      expect(newUser).toMatchObject({
        id: expect.any(String),
        email: 'new@example.com',
        name: 'New User',
        role: 'user',
      });
    });

    it('validates required fields', async () => {
      await expect(
        client.createUser({ email: '', name: '', role: 'user' })
      ).rejects.toThrow();
    });
  });

  describe('PUT /users/:userId', () => {
    it('updates existing user', async () => {
      const userId = '550e8400-e29b-41d4-a716-446655440000';
      const updated = await client.updateUser(userId, {
        email: 'updated@example.com',
        name: 'Updated Name',
        role: 'admin',
      });

      expect(updated.email).toBe('updated@example.com');
      expect(updated.name).toBe('Updated Name');
    });
  });

  describe('DELETE /users/:userId', () => {
    it('deletes existing user', async () => {
      const userId = '550e8400-e29b-41d4-a716-446655440001';
      await expect(client.deleteUser(userId)).resolves.not.toThrow();
    });
  });
});
```

### 6. Generate Backend Validation Middleware

Zod schema for request validation:

```typescript
// File: src/middleware/user-validator.ts
/**
 * Request validation middleware
 * Validates against OpenAPI schema using Zod
 */

import { z } from 'zod';
import type { Request, Response, NextFunction } from 'express';

const UserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  name: z.string().min(1),
  role: z.enum(['admin', 'user']),
  createdAt: z.date(),
});

const CreateUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1),
  role: z.enum(['admin', 'user']).default('user'),
});

export const validateCreateUser = (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    req.body = CreateUserSchema.parse(req.body);
    next();
  } catch (error) {
    if (error instanceof z.ZodError) {
      res.status(400).json({
        error: 'VALIDATION_ERROR',
        message: 'Invalid request data',
        details: error.errors,
      });
    } else {
      next(error);
    }
  }
};

export const validateUpdateUser = validateCreateUser;

// Usage in routes:
// router.post('/users', validateCreateUser, userController.create);
```

### 7. Summary Output

```
✅ API contract generated successfully!

Generated files:
├─ 📄 api/user-api.yaml                    OpenAPI 3.1 specification
├─ 📦 src/api/user-api.types.ts            TypeScript types (from spec)
├─ 🔌 src/api/user-client.ts               Type-safe API client
├─ 🎭 src/mocks/user.mocks.ts              MSW mock handlers
├─ 🧪 src/api/__tests__/user-api.test.ts   Contract tests
└─ ✅ src/middleware/user-validator.ts      Request validation

📚 Documentation:
- OpenAPI UI: https://editor.swagger.io/ (paste user-api.yaml)
- Try API: npx @stoplight/prism-cli mock api/user-api.yaml

🎯 Next steps:

Frontend developers:
1. Import client: import { userApi } from './api/user-client'
2. Use types: import type { User } from './api/user-client'
3. Enable mocks: await setupMocks() (in app initialization)
4. Develop features against mocks (no backend needed!)

Backend developers:
1. Implement endpoints matching api/user-api.yaml
2. Use validation middleware: validateCreateUser
3. Run contract tests to verify compliance

Both:
4. Run tests: npm test src/api/__tests__/user-api.test.ts
5. Deploy: Ensure backend matches contract
6. Monitor: Set up contract drift detection

💰 Value unlocked:
- Frontend unblocked immediately (parallel development)
- Backend has clear contract to implement
- Tests ensure both sides stay in sync
- Single source of truth prevents API drift
```

## Usage Examples

**From TypeScript interface:**
```bash
/dev-aid-api-contract --from src/models/user.ts --name UserAPI
```

**From Zod schema:**
```bash
/dev-aid-api-contract --from src/schemas/user-schema.ts --name UserAPI
```

**From existing code:**
```bash
/dev-aid-api-contract --infer src/controllers/user-controller.ts
```

**Custom output directory:**
```bash
/dev-aid-api-contract --from src/models/user.ts --output api/generated
```

## Integration with Development Workflow

**Setup once:**
```bash
# Install dependencies
npm install --save openapi-fetch
npm install --save-dev openapi-typescript msw vitest

# Generate contract
/dev-aid-api-contract --from src/models/user.ts
```

**Frontend development:**
```typescript
// In your app
import { setupMocks } from './mocks/user.mocks';
import { userApi } from './api/user-client';

// Enable mocks for development
if (process.env.NODE_ENV === 'development') {
  await setupMocks();
}

// Use the API
const users = await userApi.listUsers({ page: 1, limit: 10 });
```

**Backend implementation:**
```typescript
// In your Express app
import { validateCreateUser } from './middleware/user-validator';

router.post('/users', validateCreateUser, async (req, res) => {
  // req.body is validated and typed
  const user = await userService.createUser(req.body);
  res.status(201).json(user);
});
```

## Contract Drift Detection

**Check for drift:**
```bash
/dev-aid-api-drift api/user-api.yaml

Checking contract compliance...

✅ GET /users - Implementation matches spec
✅ POST /users - Implementation matches spec
❌ PUT /users/:userId - Response schema mismatch
   Expected: User
   Got: { user: User, metadata: ... }

⚠️  1 endpoint out of compliance
```

## Value Proposition

**Time savings:**
- **Frontend unblocked**: No waiting for backend (2-4 weeks saved)
- **Parallel development**: Both teams work simultaneously
- **Fewer integration bugs**: Contract tests catch mismatches early
- **Faster iterations**: Mock data enables rapid prototyping

**For 100 developers (50 frontend, 50 backend):**
- Frontend: 2 weeks unblocked × 50 devs = 100 dev-weeks saved
- Backend: Clear contract reduces rework = 20 dev-weeks saved
- Integration: Fewer bugs = 15 dev-weeks saved
- **Total: 135 dev-weeks/year = $675,000 at $100/hr**

**Quality improvements:**
- Single source of truth (no API drift)
- Type safety across stack
- Automated contract testing
- Better developer experience

## Related Commands

- `/dev-aid-api-drift` - Detect contract violations
- `/dev-aid-review-staged` - Review API changes before commit
- `/dev-aid-code-health` - Overall code quality assessment

## Technical Requirements

**Dependencies needed:**
```json
{
  "dependencies": {
    "openapi-fetch": "^0.9.0",
    "zod": "^3.22.0"
  },
  "devDependencies": {
    "openapi-typescript": "^6.7.0",
    "msw": "^2.0.0",
    "vitest": "^1.0.0"
  }
}
```

**Project structure:**
```
project/
├── api/
│   └── user-api.yaml          # OpenAPI spec
├── src/
│   ├── api/
│   │   ├── user-api.types.ts  # Generated types
│   │   ├── user-client.ts     # API client
│   │   └── __tests__/
│   │       └── user-api.test.ts
│   ├── mocks/
│   │   └── user.mocks.ts      # MSW handlers
│   └── middleware/
│       └── user-validator.ts   # Validation
```
