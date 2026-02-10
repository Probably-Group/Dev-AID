---
name: graphql-expert
version: 2.0.0
description: "GraphQL API design with schema patterns, resolver implementation, real-time subscriptions, and Apollo federation for distributed graphs. Use when designing GraphQL schemas, implementing resolvers, configuring Apollo Gateway/Federation, or adding query depth/complexity limits. Do NOT use for REST API design (use rest-api-design) or gRPC services."
risk_level: HIGH
---

# GraphQL Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-400: Query Complexity DoS**
- NEVER: Allow unlimited query depth/complexity
- ALWAYS: Depth limiting, complexity analysis, query cost limits

**CWE-285: Authorization in Resolvers**
- NEVER: Trust query structure for authorization
- ALWAYS: Check permissions in EVERY resolver, not just entry points

**CWE-200: Introspection in Production**
- NEVER: Enable introspection in production (exposes schema)
- ALWAYS: Disable introspection or restrict to authenticated users

**CWE-943: N+1 Query Injection**
- NEVER: Unbounded nested queries
- ALWAYS: Use DataLoader, limit nesting depth, query cost analysis

### 0.3 Risk Level: HIGH

**Verification requirements for HIGH risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 Query Complexity & Depth Limits (CWE-400)

**Principle:** Prevent denial of service through complex/deep queries.

```typescript
// ❌ WRONG - No limits, allows resource exhaustion
const server = new ApolloServer({
  typeDefs,
  resolvers,
});

// ✅ CORRECT - Depth and complexity limits
import depthLimit from 'graphql-depth-limit';
import { createComplexityLimitRule } from 'graphql-validation-complexity';

const server = new ApolloServer({
  typeDefs,
  resolvers,
  validationRules: [
    depthLimit(5),  // Max 5 levels deep
    createComplexityLimitRule(1000, {
      scalarCost: 1,
      objectCost: 10,
      listFactor: 10,
    }),
  ],
});
```

### 1.2 Authorization Per Field (CWE-862)

**Principle:** Check authorization at resolver level, not just query level.

```typescript
// ❌ WRONG - No authorization check
const resolvers = {
  Query: {
    user: async (_, { id }) => {
      return db.users.findById(id);  // Anyone can query any user!
    },
  },
};

// ✅ CORRECT - Authorization in every resolver
const resolvers = {
  Query: {
    user: async (_, { id }, context) => {
      // Check authentication
      if (!context.user) {
        throw new AuthenticationError('Not authenticated');
      }

      // Check authorization
      if (context.user.id !== id && !context.user.isAdmin) {
        throw new ForbiddenError('Access denied');
      }

      return db.users.findById(id);
    },
  },
  User: {
    // Field-level authorization
    email: async (parent, _, context) => {
      if (context.user?.id !== parent.id && !context.user?.isAdmin) {
        return null;  // Hide email from unauthorized users
      }
      return parent.email;
    },
  },
};
```

### 1.3 Input Validation (CWE-20)

**Principle:** Validate all input at resolver boundaries.

```typescript
import { z } from 'zod';
import { UserInputError } from 'apollo-server-errors';

// Define validation schemas
const CreateUserSchema = z.object({
  username: z.string().min(3).max(50).regex(/^[a-zA-Z0-9_]+$/),
  email: z.string().email().max(255),
  age: z.number().int().min(0).max(150).optional(),
});

// ❌ WRONG - No validation
const resolvers = {
  Mutation: {
    createUser: async (_, { input }) => {
      return db.users.create(input);  // Trusting raw input!
    },
  },
};

// ✅ CORRECT - Validate with Zod
const resolvers = {
  Mutation: {
    createUser: async (_, { input }) => {
      const result = CreateUserSchema.safeParse(input);
      if (!result.success) {
        throw new UserInputError('Invalid input', {
          validationErrors: result.error.flatten(),
        });
      }
      return db.users.create(result.data);
    },
  },
};
```

### 1.4 SQL Injection Prevention (CWE-89)

**Principle:** Never construct queries from GraphQL arguments.

```typescript
// ❌ WRONG - SQL injection via GraphQL
const resolvers = {
  Query: {
    users: async (_, { filter }) => {
      return db.raw(`SELECT * FROM users WHERE name LIKE '%${filter}%'`);
    },
  },
};

// ✅ CORRECT - Parameterized queries
const resolvers = {
  Query: {
    users: async (_, { filter }) => {
      return db.users
        .where('name', 'like', `%${filter}%`)
        .limit(100);  // Always limit results
    },
  },
};
```

### 1.5 Information Disclosure Prevention (CWE-209)

**Principle:** Never expose internal errors to clients.

```typescript
// ❌ WRONG - Exposes internal details
const server = new ApolloServer({
  formatError: (error) => error,  // Raw errors!
});

// ✅ CORRECT - Safe error formatting
const server = new ApolloServer({
  formatError: (error) => {
    // Log full error internally
    console.error('GraphQL Error:', error);

    // Return safe error to client
    if (error.extensions?.code === 'INTERNAL_SERVER_ERROR') {
      return {
        message: 'An internal error occurred',
        extensions: { code: 'INTERNAL_SERVER_ERROR' },
      };
    }

    // Return validation/auth errors as-is
    return {
      message: error.message,
      extensions: { code: error.extensions?.code },
    };
  },
});
```

### 1.6 Rate Limiting (CWE-770)

**Principle:** Limit requests per user/IP to prevent abuse.

---

## 2. Version Requirements

**ALWAYS use these minimum versions:**

```json
{
  "dependencies": {
    "@apollo/server": "^4.10.0",
    "graphql": "^16.8.0",
    "graphql-depth-limit": "^1.1.0",
    "graphql-validation-complexity": "^0.4.0",
    "zod": "^3.22.0"
  }
}
```

---

## 3. Code Patterns

### 3.1 WHEN creating GraphQL schema

```graphql
# Define clear, validated types
type User {
  id: ID!
  username: String!
  email: String  # Nullable - may be hidden from unauthorized users
  createdAt: DateTime!
}

# Use input types for mutations
input CreateUserInput {
  username: String!
  email: String!
  age: Int
}

# Pagination for lists (prevent unbounded queries)
type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type UserEdge {
  node: User!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

type Query {
  user(id: ID!): User
  users(first: Int = 10, after: String): UserConnection!
}

type Mutation {
  createUser(input: CreateUserInput!): User!
  updateUser(id: ID!, input: UpdateUserInput!): User!
  deleteUser(id: ID!): Boolean!
}
```

### 3.2 WHEN implementing resolvers with auth

```typescript
import { ApolloServer } from '@apollo/server';
import { GraphQLError } from 'graphql';
import { z } from 'zod';

// Context type
interface Context {
  user: { id: string; role: string } | null;
  db: Database;
}

// Auth helpers
function requireAuth(context: Context) {
  if (!context.user) {
    throw new GraphQLError('Not authenticated', {
      extensions: { code: 'UNAUTHENTICATED' },
    });
  }
  return context.user;
}

function requireRole(context: Context, role: string) {
  const user = requireAuth(context);
  if (user.role !== role && user.role !== 'admin') {
    throw new GraphQLError('Access denied', {
      extensions: { code: 'FORBIDDEN' },
    });
  }
  return user;
}

// Validation schemas
const CreateUserSchema = z.object({
  username: z.string().min(3).max(50).regex(/^[a-zA-Z0-9_]+$/),
  email: z.string().email().max(255),
});

// Resolvers
const resolvers = {
  Query: {
    user: async (_: unknown, { id }: { id: string }, context: Context) => {
      requireAuth(context);
      return context.db.users.findById(id);
    },

    users: async (
      _: unknown,
      { first = 10, after }: { first?: number; after?: string },
      context: Context
    ) => {
      requireAuth(context);

      // Enforce maximum page size
      const limit = Math.min(first, 100);

      const users = await context.db.users
        .findMany({ cursor: after, take: limit + 1 });

      const hasNextPage = users.length > limit;
      const edges = users.slice(0, limit).map(user => ({
        node: user,
        cursor: user.id,
      }));

      return {
        edges,
        pageInfo: {
          hasNextPage,
          hasPreviousPage: !!after,
          startCursor: edges[0]?.cursor,
          endCursor: edges[edges.length - 1]?.cursor,
        },
        totalCount: await context.db.users.count(),
      };
    },
  },

  Mutation: {
    createUser: async (
      _: unknown,
      { input }: { input: unknown },
      context: Context
    ) => {
      requireRole(context, 'admin');

      // Validate input
      const result = CreateUserSchema.safeParse(input);
      if (!result.success) {
        throw new GraphQLError('Invalid input', {
          extensions: {
            code: 'BAD_USER_INPUT',
            validationErrors: result.error.flatten(),
          },
        });
      }

      return context.db.users.create(result.data);
    },
  },

  User: {
    // Field-level authorization
    email: (parent: any, _: unknown, context: Context) => {
      // Only show email to owner or admin
      if (context.user?.id === parent.id || context.user?.role === 'admin') {
        return parent.email;
      }
      return null;
    },
  },
};
```

### 3.3 WHEN setting up Apollo Server

```typescript
import { ApolloServer } from '@apollo/server';
import { expressMiddleware } from '@apollo/server/express4';
import express from 'express';
import depthLimit from 'graphql-depth-limit';
import { createComplexityLimitRule } from 'graphql-validation-complexity';
import { rateLimit } from 'express-rate-limit';

const app = express();

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: { errors: [{ message: 'Too many requests' }] },
});

app.use('/graphql', limiter);

// Apollo Server with security features
const server = new ApolloServer({
  typeDefs,
  resolvers,
  validationRules: [
    depthLimit(5),
    createComplexityLimitRule(1000),
  ],
  formatError: (formattedError, error) => {
    // Log full error for debugging
    console.error('GraphQL Error:', error);

    // Don't expose internal errors
    if (formattedError.extensions?.code === 'INTERNAL_SERVER_ERROR') {
      return {
        message: 'Internal server error',
        extensions: { code: 'INTERNAL_SERVER_ERROR' },
      };
    }

    return formattedError;
  },
  introspection: process.env.NODE_ENV !== 'production',
});

await server.start();

app.use(
  '/graphql',
  express.json(),
  expressMiddleware(server, {
    context: async ({ req }) => {
      // Extract user from JWT/session
      const token = req.headers.authorization?.replace('Bearer ', '');
      const user = token ? await verifyToken(token) : null;

      return {
        user,
        db: database,
      };
    },
  })
);
```

### 3.4 WHEN implementing subscriptions securely

```typescript
import { WebSocketServer } from 'ws';
import { useServer } from 'graphql-ws/lib/use/ws';

const wsServer = new WebSocketServer({
  server: httpServer,
  path: '/graphql',
});

useServer(
  {
    schema,
    context: async (ctx) => {
      // Authenticate WebSocket connection
      const token = ctx.connectionParams?.authToken;
      if (!token) {
        throw new Error('Not authenticated');
      }

      const user = await verifyToken(token as string);
      if (!user) {
        throw new Error('Invalid token');
      }

      return { user, db: database };
    },
    onSubscribe: async (ctx, msg) => {
      // Validate subscription is allowed for this user
      const { user } = ctx.extra;

      // Rate limit subscriptions per user
      const activeSubscriptions = getActiveSubscriptions(user.id);
      if (activeSubscriptions >= 10) {
        throw new Error('Too many active subscriptions');
      }
    },
  },
  wsServer
);
```

---

## 4. Anti-Patterns

**NEVER:**
- Allow unbounded query depth or complexity
- Skip authorization checks in resolvers
- Expose raw database errors to clients
- Trust GraphQL input without validation
- Allow introspection in production
- Skip rate limiting on GraphQL endpoints
- Construct SQL from GraphQL arguments

---

## 5. Testing

**ALWAYS write security tests:**

```typescript
import { createTestClient } from '@apollo/server/testing';

describe('GraphQL Security', () => {
  test('rejects deep queries', async () => {
    const { query } = createTestClient(server);

    const result = await query({
      query: `
        query DeepQuery {
          user(id: "1") {
            friends {
              friends {
                friends {
                  friends {
                    friends {
                      id  # 6 levels deep - should be rejected
                    }
                  }
                }
              }
            }
          }
        }
      `,
    });

    expect(result.errors).toBeDefined();
    expect(result.errors[0].message).toContain('depth');
  });

  test('requires authentication', async () => {
    const { query } = createTestClient(server);

    const result = await query({
      query: `query { user(id: "1") { id } }`,
    });

    expect(result.errors[0].extensions.code).toBe('UNAUTHENTICATED');
  });

  test('enforces authorization', async () => {
    const { query } = createTestClient(server, {
      contextValue: { user: { id: '2', role: 'user' } },
    });

    const result = await query({
      query: `mutation { deleteUser(id: "1") }`,
    });

    expect(result.errors[0].extensions.code).toBe('FORBIDDEN');
  });

  test('validates input', async () => {
    const { mutate } = createTestClient(server, {
      contextValue: { user: { id: '1', role: 'admin' } },
    });

    const result = await mutate({
      mutation: `
        mutation {
          createUser(input: { username: "a", email: "invalid" }) { id }
        }
      `,
    });

    expect(result.errors[0].extensions.code).toBe('BAD_USER_INPUT');
  });
});
```

---

## 6. Pre-Generation Checklist

**BEFORE generating any GraphQL code:**

- [ ] Query depth limit configured (max 5-7 levels)
- [ ] Query complexity limit configured
- [ ] Authorization checked in every resolver
- [ ] Field-level authorization for sensitive data
- [ ] Input validated with Zod/Yup at resolver boundary
- [ ] Pagination required for list queries (no unbounded lists)
- [ ] Rate limiting applied to GraphQL endpoint
- [ ] Internal errors not exposed to clients
- [ ] Introspection disabled in production
- [ ] Subscriptions authenticated and rate-limited

---

**Performance**: Quality over speed. Verify all code examples compile. Never skip security checks. See `template-references/performance-notes.md` for full guidelines.