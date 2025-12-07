## 5. Implementation Patterns

### 4.1 Branded Types for Security

```typescript
// types/branded.ts
declare const __brand: unique symbol

type Brand<T, B> = T & { [__brand]: B }

// ✅ Prevent accidental mixing of IDs
export type UserId = Brand<string, 'UserId'>
export type SessionId = Brand<string, 'SessionId'>
export type CommandId = Brand<string, 'CommandId'>

// Factory functions with validation
export function createUserId(id: string): UserId {
  if (!/^usr_[a-zA-Z0-9]{16}$/.test(id)) {
    throw new Error('Invalid user ID format')
  }
  return id as UserId
}

// ✅ Type system prevents mixing IDs
function getUser(id: UserId): User { /* ... */ }
function getSession(id: SessionId): Session { /* ... */ }

// This won't compile:
// getUser(sessionId) // Error: SessionId not assignable to UserId
```

### 4.2 Discriminated Unions for State

```typescript
// types/jarvis-state.ts

// ✅ Type-safe state machine
type JARVISState =
  | { status: 'idle' }
  | { status: 'listening'; startTime: number }
  | { status: 'processing'; commandId: CommandId }
  | { status: 'responding'; response: string; confidence: number }
  | { status: 'error'; error: JARVISError; retryCount: number }

// ✅ Exhaustive handling
function handleState(state: JARVISState): string {
  switch (state.status) {
    case 'idle':
      return 'Ready'
    case 'listening':
      return `Listening for ${Date.now() - state.startTime}ms`
    case 'processing':
      return `Processing ${state.commandId}`
    case 'responding':
      return `${state.response} (${state.confidence}%)`
    case 'error':
      return `Error: ${state.error.message}`
    default:
      // ✅ Compile-time exhaustiveness check
      const _exhaustive: never = state
      return _exhaustive
  }
}
```

### 4.3 Runtime Validation with Zod

```typescript
// schemas/command.ts
import { z } from 'zod'

// ✅ Schema-first approach
export const commandSchema = z.object({
  id: z.string().regex(/^cmd_[a-zA-Z0-9]{16}$/),
  action: z.enum(['navigate', 'control', 'query', 'configure']),
  target: z.string().min(1).max(100),
  parameters: z.record(z.unknown()).optional(),
  timestamp: z.number().int().positive(),
  priority: z.number().min(0).max(10).default(5)
})

// ✅ Infer TypeScript type from schema
export type Command = z.infer<typeof commandSchema>

// ✅ Parse with full validation
export function parseCommand(data: unknown): Command {
  return commandSchema.parse(data)
}

// ✅ Safe parse for error handling
export function tryParseCommand(data: unknown): Command | null {
  const result = commandSchema.safeParse(data)
  return result.success ? result.data : null
}
```

### 4.4 Generic Patterns for HUD Components

```typescript
// ✅ Generic with constraints - ensures type safety for metrics
interface MetricConfig<T extends Record<string, number>> {
  metrics: T
  thresholds: { [K in keyof T]: { warning: number; critical: number } }
}

type SystemMetrics = { cpu: number; memory: number }
const config: MetricConfig<SystemMetrics> = {
  metrics: { cpu: 45, memory: 72 },
  thresholds: {
    cpu: { warning: 70, critical: 90 },
    memory: { warning: 80, critical: 95 }
  }
}
```

### 4.5 Type Guards for Narrowing

```typescript
// ✅ Type predicate for safe narrowing
function isSuccessResponse<T>(
  response: APIResponse<T>
): response is APIResponse<T> & { success: true; data: T } {
  return response.success && response.data !== undefined
}

// Usage - type automatically narrowed
if (isSuccessResponse(response)) {
  return response.data // ✅ Type is T, not T | undefined
}
```

### 4.6 Utility Types for JARVIS

```typescript
// types/utilities.ts

// ✅ Deep readonly for immutable state
type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K]
}

// ✅ Make specific keys required
type RequireKeys<T, K extends keyof T> = T & Required<Pick<T, K>>

// ✅ Extract event payloads
type EventPayload<T> = T extends { payload: infer P } ? P : never

// ✅ Async function return type
type AsyncReturnType<T extends (...args: any[]) => Promise<any>> =
  T extends (...args: any[]) => Promise<infer R> ? R : never
```

