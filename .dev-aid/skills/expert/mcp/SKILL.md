---
name: mcp
version: 2.0.0
description: "Model Context Protocol server implementation for extending Claude with custom tools, resources, and prompts. Use when building MCP servers, MCP tools, or resource providers. Do NOT use for general API design (use api-expert)."
risk_level: HIGH
token_budget: 4500
---
# Model Context Protocol (MCP) - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.2 Security Patterns (security rules)

**CWE-78: Tool Command Injection**
- Do not: Pass user input directly to shell tools
- Instead: Validate/sanitize all tool parameters

**CWE-285: Resource Authorization**
- Do not: Expose resources without access control
- Instead: Scope resources to user context, validate permissions

**CWE-200: Context Exposure**
- Do not: Include secrets in tool responses
- Instead: Filter sensitive data from responses

---

## 1. Security Principles

### 1.1 Tool Execution Safety (CWE-78)

**Principle:** Never execute arbitrary commands from tool arguments. Validate and allowlist.

```typescript
// ❌ WRONG - Command injection
server.tool("execute", async ({ command }) => {
  return exec(command);  // User controls command!
});

// ✅ CORRECT - Allowlisted commands only
const ALLOWED_COMMANDS = ['ls', 'pwd', 'whoami'] as const;

server.tool("execute", async ({ command }) => {
  if (!ALLOWED_COMMANDS.includes(command as any)) {
    throw new Error(`Command not allowed: ${command}`);
  }
  return exec(command);
});
```

### 1.2 Input Validation (CWE-20)

**Principle:** Validate all tool inputs with strict schemas. Reject malformed requests.

```typescript
// ❌ WRONG - No validation
server.tool("read_file", async ({ path }) => {
  return fs.readFileSync(path, 'utf-8');
});

// ✅ CORRECT - Validated with path restrictions
import { z } from 'zod';
import path from 'path';

const ReadFileSchema = z.object({
  path: z.string()
    .refine(p => !p.includes('..'), 'Path traversal not allowed')
    .refine(p => p.startsWith('/allowed/'), 'Path outside allowed directory'),
});

server.tool("read_file", ReadFileSchema, async ({ path: filePath }) => {
  const resolved = path.resolve('/allowed', filePath);
  if (!resolved.startsWith('/allowed/')) {
    throw new Error('Path traversal detected');
  }
  return fs.readFileSync(resolved, 'utf-8');
});
```

### 1.3 Secrets Protection (CWE-798)

**Principle:** Never expose secrets through tool responses or errors.

```typescript
// ❌ WRONG - Leaks secrets in error
server.tool("connect", async ({ url }) => {
  const apiKey = process.env.API_KEY;
  throw new Error(`Failed to connect to ${url} with key ${apiKey}`);
});

// ✅ CORRECT - Sanitized errors
server.tool("connect", async ({ url }) => {
  try {
    return await connectToService(url);
  } catch (e) {
    throw new Error(`Failed to connect to ${url}`);
  }
});
```

### 1.4 Resource Access Control (CWE-862)

**Principle:** Implement capability-based access. Don't give tools more access than needed.

### 1.5 Rate Limiting (CWE-770)

**Principle:** Rate limit expensive operations. Prevent resource exhaustion.

### 1.6 Prompt Injection Defense (CWE-74)

**Principle:** Sanitize all data before including in prompts. Mark user content clearly.

---

## 2. Version Requirements

Use these minimum versions:

```json
{
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.0.0",
    "zod": "^3.23.0"
  }
}
```

---

## 3. Code Patterns

### 3.1 WHEN creating an MCP server

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";

// Create server with metadata
const server = new Server(
  {
    name: "my-mcp-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
      resources: {},
      prompts: {},
    },
  }
);

// Define tool schemas
const SearchSchema = z.object({
  query: z.string().min(1).max(1000),
  limit: z.number().int().min(1).max(100).default(10),
});

const ReadFileSchema = z.object({
  path: z.string()
    .refine(p => !p.includes('..'), 'No path traversal')
    .refine(p => p.startsWith('/workspace/'), 'Must be in workspace'),
});

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "search",
        description: "Search for content in the knowledge base",
        inputSchema: {
          type: "object",
          properties: {
            query: { type: "string", description: "Search query" },
            limit: { type: "number", description: "Max results (1-100)" },
          },
          required: ["query"],
        },
      },
      {
        name: "read_file",
        description: "Read a file from the workspace",
        inputSchema: {
          type: "object",
          properties: {
            path: { type: "string", description: "File path within workspace" },
          },
          required: ["path"],
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  switch (name) {
    case "search": {
      const { query, limit } = SearchSchema.parse(args);
      const results = await searchKnowledgeBase(query, limit);
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(results, null, 2),
          },
        ],
      };
    }

    case "read_file": {
      const { path: filePath } = ReadFileSchema.parse(args);
      const content = await fs.promises.readFile(filePath, "utf-8");
      return {
        content: [
          {
            type: "text",
            text: content,
          },
        ],
      };
    }

    default:
      throw new Error(`Unknown tool: ${name}`);
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("MCP server started");
}

main().catch(console.error);
```

### 3.2 WHEN implementing resources

```typescript
import { ListResourcesRequestSchema, ReadResourceRequestSchema } from "@modelcontextprotocol/sdk/types.js";

// Define resources
interface ResourceDefinition {
  uri: string;
  name: string;
  mimeType: string;
  description?: string;
}

const resources: Map<string, ResourceDefinition> = new Map([
  ["config://app/settings", {
    uri: "config://app/settings",
    name: "Application Settings",
    mimeType: "application/json",
    description: "Current application configuration",
  }],
  ["file://workspace/readme", {
    uri: "file://workspace/readme",
    name: "README",
    mimeType: "text/markdown",
    description: "Project documentation",
  }],
]);

// List resources
server.setRequestHandler(ListResourcesRequestSchema, async () => {
  return {
    resources: Array.from(resources.values()).map(r => ({
      uri: r.uri,
      name: r.name,
      mimeType: r.mimeType,
      description: r.description,
    })),
  };
});

// Read resource
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const { uri } = request.params;

  // Validate URI format
  const parsed = new URL(uri);

  switch (parsed.protocol) {
    case "config:": {
      if (uri === "config://app/settings") {
        const settings = await loadSettings();
        return {
          contents: [
            {
              uri,
              mimeType: "application/json",
              text: JSON.stringify(settings, null, 2),
            },
          ],
        };
      }
      break;
    }

    case "file:": {
      // Validate path is within workspace
      const filePath = parsed.pathname;
      const resolved = path.resolve("/workspace", filePath);

      if (!resolved.startsWith("/workspace/")) {
        throw new Error("Access denied: path outside workspace");
      }

      const content = await fs.promises.readFile(resolved, "utf-8");
      const resource = resources.get(uri);

      return {
        contents: [
          {
            uri,
            mimeType: resource?.mimeType || "text/plain",
            text: content,
          },
        ],
      };
    }
  }

  throw new Error(`Unknown resource: ${uri}`);
});
```

### 3.3 WHEN implementing prompts

```typescript
import {
  ListPromptsRequestSchema,
  GetPromptRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

// Define prompt templates
const prompts = new Map([
  ["code-review", {
    name: "code-review",
    description: "Review code for quality and security issues",
    arguments: [
      {
        name: "code",
        description: "The code to review",
        required: true,
      },
      {
        name: "language",
        description: "Programming language",
        required: false,
      },
    ],
  }],
  ["explain", {
    name: "explain",
    description: "Explain code or concept in detail",
    arguments: [
      {
        name: "topic",
        description: "What to explain",
        required: true,
      },
    ],
  }],
]);

// List prompts
server.setRequestHandler(ListPromptsRequestSchema, async () => {
  return {
    prompts: Array.from(prompts.values()),
  };
});

// Get prompt
server.setRequestHandler(GetPromptRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  const prompt = prompts.get(name);

  if (!prompt) {
    throw new Error(`Unknown prompt: ${name}`);
  }

  switch (name) {
    case "code-review": {
      const code = args?.code as string;
      const language = args?.language as string || "unknown";

      // Sanitize user input before including in prompt
      const sanitizedCode = code.slice(0, 10000); // Limit size

      return {
        messages: [
          {
            role: "user",
            content: {
              type: "text",
              text: `Please review the following ${language} code for:
1. Security vulnerabilities
2. Performance issues
3. Code quality and best practices
4. Potential bugs

<code language="${language}">
${sanitizedCode}
</code>

Provide specific, actionable feedback.`,
            },
          },
        ],
      };
    }

    case "explain": {
      const topic = args?.topic as string;
      return {
        messages: [
          {
            role: "user",
            content: {
              type: "text",
              text: `Please explain the following topic in detail:

Topic: ${topic}

Provide:
1. A clear definition
2. Key concepts
3. Practical examples
4. Common pitfalls to avoid`,
            },
          },
        ],
      };
    }

    default:
      throw new Error(`Unknown prompt: ${name}`);
  }
});
```

### 3.4 WHEN implementing tool execution with timeouts

```typescript
import { setTimeout } from "timers/promises";

// Timeout wrapper
async function withTimeout<T>(
  promise: Promise<T>,
  ms: number,
  message = "Operation timed out"
): Promise<T> {
  const timeout = setTimeout(ms).then(() => {
    throw new Error(message);
  });

  return Promise.race([promise, timeout]);
}

// Rate limiter for expensive operations
class RateLimiter {
  private tokens: number;
  private lastRefill: number;
  private readonly maxTokens: number;
  private readonly refillRate: number;

  constructor(maxTokens: number, refillRatePerSecond: number) {
    this.maxTokens = maxTokens;
    this.tokens = maxTokens;
    this.refillRate = refillRatePerSecond;
    this.lastRefill = Date.now();
  }

  async acquire(): Promise<void> {
    this.refill();

    if (this.tokens < 1) {
      const waitTime = (1 - this.tokens) / this.refillRate * 1000;
      await setTimeout(waitTime);
      this.refill();
    }

    this.tokens -= 1;
  }

  private refill(): void {
    const now = Date.now();
    const elapsed = (now - this.lastRefill) / 1000;
    this.tokens = Math.min(this.maxTokens, this.tokens + elapsed * this.refillRate);
    this.lastRefill = now;
  }
}

const searchRateLimiter = new RateLimiter(10, 1); // 10 burst, 1/sec refill

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "search") {
    // Rate limit
    await searchRateLimiter.acquire();

    // Execute with timeout
    const result = await withTimeout(
      searchKnowledgeBase(args.query as string),
      30000,
      "Search timed out after 30 seconds"
    );

    return {
      content: [{ type: "text", text: JSON.stringify(result) }],
    };
  }

  throw new Error(`Unknown tool: ${name}`);
});
```

### 3.5 WHEN creating an MCP client

```typescript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { spawn } from "child_process";

async function createMCPClient(serverCommand: string, serverArgs: string[]) {
  // Spawn server process
  const serverProcess = spawn(serverCommand, serverArgs, {
    stdio: ["pipe", "pipe", "pipe"],
  });

  // Create transport
  const transport = new StdioClientTransport({
    reader: serverProcess.stdout,
    writer: serverProcess.stdin,
  });

  // Create client
  const client = new Client(
    {
      name: "my-client",
      version: "1.0.0",
    },
    {
      capabilities: {},
    }
  );

  await client.connect(transport);

  return { client, serverProcess };
}

// Use the client
async function main() {
  const { client, serverProcess } = await createMCPClient(
    "node",
    ["./my-mcp-server.js"]
  );

  try {
    // List available tools
    const tools = await client.listTools();
    console.log("Available tools:", tools.tools.map(t => t.name));

    // Call a tool
    const result = await client.callTool({
      name: "search",
      arguments: { query: "MCP protocol", limit: 5 },
    });

    console.log("Search result:", result.content);

    // List resources
    const resources = await client.listResources();
    console.log("Available resources:", resources.resources.map(r => r.uri));

    // Read a resource
    const content = await client.readResource({
      uri: "config://app/settings",
    });

    console.log("Resource content:", content.contents);

  } finally {
    await client.close();
    serverProcess.kill();
  }
}
```

### 3.6 WHEN handling errors properly

```typescript
import {
  McpError,
  ErrorCode,
} from "@modelcontextprotocol/sdk/types.js";

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    // Validate arguments
    if (!args || typeof args !== "object") {
      throw new McpError(
        ErrorCode.InvalidParams,
        "Arguments must be an object"
      );
    }

    switch (name) {
      case "read_file": {
        const schema = z.object({ path: z.string() });
        const { path: filePath } = schema.parse(args);

        try {
          const content = await fs.promises.readFile(filePath, "utf-8");
          return {
            content: [{ type: "text", text: content }],
          };
        } catch (e) {
          if ((e as NodeJS.ErrnoException).code === "ENOENT") {
            throw new McpError(
              ErrorCode.InvalidParams,
              `File not found: ${filePath}`
            );
          }
          if ((e as NodeJS.ErrnoException).code === "EACCES") {
            throw new McpError(
              ErrorCode.InvalidParams,
              `Permission denied: ${filePath}`
            );
          }
          throw e;
        }
      }

      default:
        throw new McpError(
          ErrorCode.MethodNotFound,
          `Unknown tool: ${name}`
        );
    }
  } catch (e) {
    // Zod validation errors
    if (e instanceof z.ZodError) {
      throw new McpError(
        ErrorCode.InvalidParams,
        `Invalid arguments: ${e.errors.map(err => err.message).join(", ")}`
      );
    }

    // Re-throw MCP errors
    if (e instanceof McpError) {
      throw e;
    }

    // Wrap unknown errors (don't leak internal details)
    console.error("Tool error:", e);
    throw new McpError(
      ErrorCode.InternalError,
      "An internal error occurred"
    );
  }
});
```

---

## 4. Anti-Patterns

Do not:
- Execute arbitrary commands from tool arguments
- Allow path traversal in file operations
- Expose secrets in tool responses or errors
- Skip input validation on any tool
- Allow unlimited resource access
- Include unsanitized user data in prompts
- Ignore timeouts on long-running operations

---

## 5. Testing

**ALWAYS write MCP server tests:**

```typescript
import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { InMemoryTransport } from "@modelcontextprotocol/sdk/inMemory.js";
import { createServer } from "./server.js";

describe("MCP Server", () => {
  let client: Client;
# ... (additional test cases follow same pattern)
```

---

## 6. Pre-Generation Checklist

Before generating any MCP code:

- [ ] All tool inputs validated with Zod schemas
- [ ] Path operations prevent traversal attacks
- [ ] Commands allowlisted (no arbitrary execution)
- [ ] Secrets not exposed in responses or errors
- [ ] Timeouts on all external/long operations
- [ ] Rate limiting for expensive operations
- [ ] Resource URIs validated and restricted
- [ ] User content sanitized before prompts
- [ ] Proper MCP error codes used
- [ ] Tool descriptions accurate and complete

---
