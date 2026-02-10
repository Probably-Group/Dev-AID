---
name: json-rpc
version: 2.0.0
description: "JSON-RPC 2.0 protocol implementation with method routing, batch requests, error codes, and transport-agnostic design. Use when implementing JSON-RPC servers or clients, designing method registries, handling batch requests, or building MCP-compatible transports. Do NOT use for REST APIs (use rest-api-design), GraphQL (use graphql-expert), or gRPC services."
risk_level: MEDIUM
---

# JSON-RPC 2.0 - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-20: Method Name Injection**
- NEVER: Dynamic method dispatch from user input
- ALWAYS: Whitelist allowed methods, validate method exists

**CWE-94: Code Injection via Params**
- NEVER: `eval()` or dynamic execution of parameters
- ALWAYS: Strict schema validation for each method's params

**CWE-285: Batch Request Authorization**
- NEVER: Skip auth checks for batch requests
- ALWAYS: Authorize EACH request in batch independently

### 0.3 Risk Level: MEDIUM

**Verification requirements for MEDIUM risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 Method Execution Safety (CWE-94)

**Principle:** Never execute arbitrary methods. Use explicit allowlist.

```typescript
// ❌ WRONG - Arbitrary method execution
async function handleRequest(req: JsonRpcRequest) {
  const method = methods[req.method];  // User controls method!
  return method(req.params);
}

// ✅ CORRECT - Explicit method allowlist
const handlers = new Map<string, Handler>([
  ['user.get', getUserHandler],
  ['user.create', createUserHandler],
]);

async function handleRequest(req: JsonRpcRequest) {
  const handler = handlers.get(req.method);
  if (!handler) {
    throw new JsonRpcError(-32601, 'Method not found');
  }
  return handler(req.params);
}
```

### 1.2 Parameter Validation (CWE-20)

**Principle:** Validate all parameters with schemas. Type check before use.

```typescript
// ❌ WRONG - No validation
async function getUser({ id }: any) {
  return db.users.findById(id);
}

// ✅ CORRECT - Schema validation
const GetUserSchema = z.object({
  id: z.string().uuid(),
});

async function getUser(params: unknown) {
  const { id } = GetUserSchema.parse(params);
  return db.users.findById(id);
}
```

### 1.3 Secrets ≠ Code (CWE-798)

**Principle:** Never include secrets in RPC responses or error messages.

### 1.4 Batch Request Limits (CWE-400)

**Principle:** Limit batch request size. Prevent resource exhaustion.

```typescript
// ❌ WRONG - Unlimited batch size
async function handleBatch(requests: JsonRpcRequest[]) {
  return Promise.all(requests.map(handleRequest));
}

// ✅ CORRECT - Limited batch size
const MAX_BATCH_SIZE = 100;

async function handleBatch(requests: JsonRpcRequest[]) {
  if (requests.length > MAX_BATCH_SIZE) {
    throw new JsonRpcError(-32600, `Batch size exceeds limit of ${MAX_BATCH_SIZE}`);
  }
  return Promise.all(requests.map(handleRequest));
}
```

### 1.5 Error Information Leakage (CWE-209)

**Principle:** Don't expose internal details in error responses.

### 1.6 Authentication (CWE-287)

**Principle:** Authenticate before processing requests. Use transport-level auth.

---

## 2. Version Requirements

**ALWAYS use these minimum versions:**

```json
{
  "dependencies": {
    "zod": "^3.23.0",
    "jayson": "^4.1.0"
  }
}
```

**JSON-RPC Version:** 2.0 (strict compliance)

---

## 3. Code Patterns

### 3.1 WHEN implementing a JSON-RPC server

```typescript
import { z } from 'zod';
import http from 'http';

// JSON-RPC 2.0 types
interface JsonRpcRequest {
  jsonrpc: '2.0';
  method: string;
  params?: unknown;
  id?: string | number | null;
}

interface JsonRpcResponse {
  jsonrpc: '2.0';
  result?: unknown;
  error?: JsonRpcErrorObject;
  id: string | number | null;
}

interface JsonRpcErrorObject {
  code: number;
  message: string;
  data?: unknown;
}

// Standard error codes
const ErrorCodes = {
  PARSE_ERROR: -32700,
  INVALID_REQUEST: -32600,
  METHOD_NOT_FOUND: -32601,
  INVALID_PARAMS: -32602,
  INTERNAL_ERROR: -32603,
} as const;

class JsonRpcError extends Error {
  constructor(
    public code: number,
    message: string,
    public data?: unknown
  ) {
    super(message);
  }
}

// Request validation schema
const RequestSchema = z.object({
  jsonrpc: z.literal('2.0'),
  method: z.string().min(1),
  params: z.unknown().optional(),
  id: z.union([z.string(), z.number(), z.null()]).optional(),
});

// Method handler type
type Handler<P = unknown, R = unknown> = (
  params: P,
  context: RequestContext
) => Promise<R>;

interface RequestContext {
  requestId: string | number | null;
  remoteAddress?: string;
}

// Method registry with type safety
class JsonRpcServer {
  private handlers = new Map<string, { handler: Handler; schema?: z.ZodType }>();
  private maxBatchSize = 100;

  // Register a method
  method<P, R>(
    name: string,
    handler: Handler<P, R>,
    schema?: z.ZodType<P>
  ): this {
    this.handlers.set(name, { handler: handler as Handler, schema });
    return this;
  }

  // Handle single request
  private async handleSingle(
    request: JsonRpcRequest,
    context: RequestContext
  ): Promise<JsonRpcResponse | undefined> {
    const id = request.id ?? null;

    try {
      // Validate request structure
      const validated = RequestSchema.parse(request);

      // Find handler
      const entry = this.handlers.get(validated.method);
      if (!entry) {
        throw new JsonRpcError(
          ErrorCodes.METHOD_NOT_FOUND,
          `Method not found: ${validated.method}`
        );
      }

      // Validate params if schema provided
      let params = validated.params;
      if (entry.schema) {
        try {
          params = entry.schema.parse(params);
        } catch (e) {
          if (e instanceof z.ZodError) {
            throw new JsonRpcError(
              ErrorCodes.INVALID_PARAMS,
              'Invalid params',
              e.errors.map(err => ({
                path: err.path.join('.'),
                message: err.message,
              }))
            );
          }
          throw e;
        }
      }

      // Execute handler
      const result = await entry.handler(params, { ...context, requestId: id });

      // Notification (no id) doesn't get response
      if (request.id === undefined) {
        return undefined;
      }

      return {
        jsonrpc: '2.0',
        result,
        id,
      };
    } catch (e) {
      // Notification errors are discarded
      if (request.id === undefined) {
        console.error('Notification error:', e);
        return undefined;
      }

      if (e instanceof JsonRpcError) {
        return {
          jsonrpc: '2.0',
          error: {
            code: e.code,
            message: e.message,
            data: e.data,
          },
          id,
        };
      }

      // Don't expose internal errors
      console.error('Internal error:', e);
      return {
        jsonrpc: '2.0',
        error: {
          code: ErrorCodes.INTERNAL_ERROR,
          message: 'Internal error',
        },
        id,
      };
    }
  }

  // Handle request (single or batch)
  async handle(body: string, context: Omit<RequestContext, 'requestId'>): Promise<string | null> {
    let parsed: unknown;

    try {
      parsed = JSON.parse(body);
    } catch {
      return JSON.stringify({
        jsonrpc: '2.0',
        error: {
          code: ErrorCodes.PARSE_ERROR,
          message: 'Parse error',
        },
        id: null,
      });
    }

    // Batch request
    if (Array.isArray(parsed)) {
      if (parsed.length === 0) {
        return JSON.stringify({
          jsonrpc: '2.0',
          error: {
            code: ErrorCodes.INVALID_REQUEST,
            message: 'Empty batch',
          },
          id: null,
        });
      }

      if (parsed.length > this.maxBatchSize) {
        return JSON.stringify({
          jsonrpc: '2.0',
          error: {
            code: ErrorCodes.INVALID_REQUEST,
            message: `Batch size exceeds limit of ${this.maxBatchSize}`,
          },
          id: null,
        });
      }

      const responses = await Promise.all(
        parsed.map(req => this.handleSingle(req as JsonRpcRequest, { ...context, requestId: null }))
      );

      const filtered = responses.filter((r): r is JsonRpcResponse => r !== undefined);
      return filtered.length > 0 ? JSON.stringify(filtered) : null;
    }

    // Single request
    const response = await this.handleSingle(parsed as JsonRpcRequest, { ...context, requestId: null });
    return response ? JSON.stringify(response) : null;
  }

  // Create HTTP server
  listen(port: number): http.Server {
    const server = http.createServer(async (req, res) => {
      if (req.method !== 'POST') {
        res.writeHead(405, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          jsonrpc: '2.0',
          error: { code: -32600, message: 'Only POST allowed' },
          id: null,
        }));
        return;
      }

      const chunks: Buffer[] = [];
      req.on('data', chunk => chunks.push(chunk));
      req.on('end', async () => {
        const body = Buffer.concat(chunks).toString();
        const remoteAddress = req.socket.remoteAddress;

        const response = await this.handle(body, { remoteAddress });

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(response ?? '');
      });
    });

    server.listen(port);
    return server;
  }
}
```

### 3.2 WHEN defining methods with validation

```typescript
// Method schemas
const GetUserSchema = z.object({
  id: z.string().uuid(),
});

const CreateUserSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
});

const ListUsersSchema = z.object({
  page: z.number().int().min(1).default(1),
  limit: z.number().int().min(1).max(100).default(20),
});

// Create server with methods
const server = new JsonRpcServer()
  .method('user.get', async (params: z.infer<typeof GetUserSchema>) => {
    const user = await db.users.findById(params.id);
    if (!user) {
      throw new JsonRpcError(-32000, 'User not found');
    }
    return user;
  }, GetUserSchema)

  .method('user.create', async (params: z.infer<typeof CreateUserSchema>) => {
    // Check for existing user
    const existing = await db.users.findByEmail(params.email);
    if (existing) {
      throw new JsonRpcError(-32001, 'Email already registered');
    }

    const user = await db.users.create(params);
    return { id: user.id };
  }, CreateUserSchema)

  .method('user.list', async (params: z.infer<typeof ListUsersSchema>) => {
    const { page, limit } = params;
    const offset = (page - 1) * limit;

    const [users, total] = await Promise.all([
      db.users.findMany({ skip: offset, take: limit }),
      db.users.count(),
    ]);

    return {
      data: users,
      pagination: { page, limit, total },
    };
  }, ListUsersSchema);

server.listen(3000);
```

### 3.3 WHEN implementing a JSON-RPC client

```typescript
import { z } from 'zod';

class JsonRpcClient {
  private id = 0;
  private baseUrl: string;
  private timeout: number;

  constructor(baseUrl: string, options: { timeout?: number } = {}) {
    this.baseUrl = baseUrl;
    this.timeout = options.timeout ?? 30000;
  }

  async call<T>(
    method: string,
    params?: unknown,
    schema?: z.ZodType<T>
  ): Promise<T> {
    const requestId = ++this.id;

    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0',
        method,
        params,
        id: requestId,
      }),
      signal: AbortSignal.timeout(this.timeout),
    });

    if (!response.ok) {
      throw new Error(`HTTP error: ${response.status}`);
    }

    const data = await response.json();

    // Check for JSON-RPC error
    if (data.error) {
      const err = new Error(data.error.message) as Error & {
        code: number;
        data?: unknown;
      };
      err.code = data.error.code;
      err.data = data.error.data;
      throw err;
    }

    // Validate response if schema provided
    if (schema) {
      return schema.parse(data.result);
    }

    return data.result as T;
  }

  async notify(method: string, params?: unknown): Promise<void> {
    await fetch(this.baseUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0',
        method,
        params,
        // No id = notification
      }),
      signal: AbortSignal.timeout(this.timeout),
    });
  }

  async batch<T extends Record<string, unknown>>(
    calls: Array<{ method: string; params?: unknown }>
  ): Promise<T[]> {
    const requests = calls.map((call, index) => ({
      jsonrpc: '2.0' as const,
      method: call.method,
      params: call.params,
      id: index,
    }));

    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requests),
      signal: AbortSignal.timeout(this.timeout),
    });

    const data = await response.json();

    // Sort responses by id to match request order
    const sorted = (data as Array<{ id: number; result?: T; error?: unknown }>)
      .sort((a, b) => a.id - b.id);

    return sorted.map(r => {
      if (r.error) {
        throw new Error(`Batch call ${r.id} failed`);
      }
      return r.result as T;
    });
  }
}

// Usage
const client = new JsonRpcClient('http://localhost:3000/rpc');

const UserSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string(),
});

const user = await client.call('user.get', { id: '123' }, UserSchema);
```

### 3.4 WHEN implementing WebSocket transport

```typescript
import { WebSocketServer, WebSocket } from 'ws';

class JsonRpcWebSocketServer {
  private wss: WebSocketServer;
  private rpcServer: JsonRpcServer;

  constructor(port: number, rpcServer: JsonRpcServer) {
    this.rpcServer = rpcServer;
    this.wss = new WebSocketServer({ port });

    this.wss.on('connection', (ws, req) => {
      const remoteAddress = req.socket.remoteAddress;

      ws.on('message', async (data) => {
        try {
          const response = await this.rpcServer.handle(
            data.toString(),
            { remoteAddress }
          );

          if (response) {
            ws.send(response);
          }
        } catch (e) {
          console.error('WebSocket handler error:', e);
          ws.send(JSON.stringify({
            jsonrpc: '2.0',
            error: {
              code: -32603,
              message: 'Internal error',
            },
            id: null,
          }));
        }
      });

      ws.on('error', (err) => {
        console.error('WebSocket error:', err);
      });
    });
  }

  // Broadcast notification to all clients
  broadcast(method: string, params?: unknown): void {
    const message = JSON.stringify({
      jsonrpc: '2.0',
      method,
      params,
    });

    this.wss.clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(message);
      }
    });
  }

  close(): void {
    this.wss.close();
  }
}
```

### 3.5 WHEN implementing authentication

```typescript
import { IncomingMessage } from 'http';

interface AuthenticatedContext extends RequestContext {
  user?: { id: string; role: string };
}

class AuthenticatedJsonRpcServer extends JsonRpcServer {
  private authenticator: (req: IncomingMessage) => Promise<{ id: string; role: string } | null>;

  constructor(authenticator: (req: IncomingMessage) => Promise<{ id: string; role: string } | null>) {
    super();
    this.authenticator = authenticator;
  }

  // Override listen to add authentication
  listen(port: number): http.Server {
    const server = http.createServer(async (req, res) => {
      // Authenticate
      const user = await this.authenticator(req);

      if (!user) {
        res.writeHead(401, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          jsonrpc: '2.0',
          error: { code: -32000, message: 'Unauthorized' },
          id: null,
        }));
        return;
      }

      // Continue with normal handling
      if (req.method !== 'POST') {
        res.writeHead(405);
        res.end();
        return;
      }

      const chunks: Buffer[] = [];
      req.on('data', chunk => chunks.push(chunk));
      req.on('end', async () => {
        const body = Buffer.concat(chunks).toString();
        const response = await this.handle(body, {
          remoteAddress: req.socket.remoteAddress,
          user,
        } as AuthenticatedContext);

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(response ?? '');
      });
    });

    server.listen(port);
    return server;
  }
}

// Usage with Bearer token authentication
const server = new AuthenticatedJsonRpcServer(async (req) => {
  const auth = req.headers.authorization;
  if (!auth?.startsWith('Bearer ')) {
    return null;
  }

  const token = auth.slice(7);
  try {
    const payload = await verifyJwt(token);
    return { id: payload.sub, role: payload.role };
  } catch {
    return null;
  }
});

// Method with authorization check
server.method('admin.getStats', async (params, context: AuthenticatedContext) => {
  if (context.user?.role !== 'admin') {
    throw new JsonRpcError(-32000, 'Admin access required');
  }
  return getSystemStats();
});
```

---

## 4. Anti-Patterns

**NEVER:**
- Execute methods from arbitrary strings without allowlist
- Skip parameter validation
- Expose stack traces in error responses
- Allow unlimited batch sizes
- Process requests without authentication on protected endpoints
- Log sensitive parameter values
- Use JSON-RPC 1.0 (always use 2.0)

---

## 5. Testing

**ALWAYS write JSON-RPC tests:**

```typescript
import { describe, it, expect, beforeAll, afterAll } from 'vitest';

describe('JSON-RPC Server', () => {
  let server: JsonRpcServer;

  beforeAll(() => {
    server = createTestServer();
  });

  it('handles valid request', async () => {
    const response = await server.handle(
      JSON.stringify({
        jsonrpc: '2.0',
        method: 'user.get',
        params: { id: 'test-uuid' },
        id: 1,
      }),
      {}
    );

    const parsed = JSON.parse(response!);
    expect(parsed.jsonrpc).toBe('2.0');
    expect(parsed.result).toBeDefined();
    expect(parsed.id).toBe(1);
  });

  it('returns method not found for unknown method', async () => {
    const response = await server.handle(
      JSON.stringify({
        jsonrpc: '2.0',
        method: 'unknown.method',
        id: 1,
      }),
      {}
    );

    const parsed = JSON.parse(response!);
    expect(parsed.error.code).toBe(-32601);
  });

  it('returns invalid params for bad input', async () => {
    const response = await server.handle(
      JSON.stringify({
        jsonrpc: '2.0',
        method: 'user.get',
        params: { id: 'not-a-uuid' },
        id: 1,
      }),
      {}
    );

    const parsed = JSON.parse(response!);
    expect(parsed.error.code).toBe(-32602);
  });

  it('handles batch requests', async () => {
    const response = await server.handle(
      JSON.stringify([
        { jsonrpc: '2.0', method: 'user.get', params: { id: 'id1' }, id: 1 },
        { jsonrpc: '2.0', method: 'user.get', params: { id: 'id2' }, id: 2 },
      ]),
      {}
    );

    const parsed = JSON.parse(response!);
    expect(parsed).toHaveLength(2);
  });

  it('rejects oversized batches', async () => {
    const requests = Array(200).fill({
      jsonrpc: '2.0',
      method: 'user.get',
      params: { id: 'id' },
      id: 1,
    });

    const response = await server.handle(JSON.stringify(requests), {});
    const parsed = JSON.parse(response!);
    expect(parsed.error.code).toBe(-32600);
  });

  it('returns null for notifications', async () => {
    const response = await server.handle(
      JSON.stringify({
        jsonrpc: '2.0',
        method: 'log.event',
        params: { event: 'test' },
        // No id = notification
      }),
      {}
    );

    expect(response).toBeNull();
  });
});
```

---

## 6. Pre-Generation Checklist

**BEFORE generating any JSON-RPC code:**

- [ ] Method names explicitly allowlisted
- [ ] All parameters validated with Zod schemas
- [ ] Batch request size limited
- [ ] Error responses don't leak internals
- [ ] Authentication implemented for protected methods
- [ ] Notifications handled (no response required)
- [ ] Proper JSON-RPC 2.0 error codes used
- [ ] Timeout handling for long operations
- [ ] Response ids match request ids
- [ ] Parse errors return proper JSON-RPC error

---

**Performance**: Quality over speed. Verify all code examples compile. Never skip security checks. See `template-references/performance-notes.md` for full guidelines.