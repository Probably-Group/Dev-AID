---
name: typescript-expert
version: 2.0.0
description: "TypeScript patterns with runtime validation (Zod), branded types, and strict type safety."
risk_level: MEDIUM
---

# TypeScript Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-20: Types ≠ Runtime Validation**
- NEVER: Trust TypeScript types for security: `function process(input: SafeInput)`
- ALWAYS: Runtime validation with Zod: `const validated = SafeInputSchema.parse(input)`

**CWE-79: XSS**
- NEVER: `element.innerHTML = userInput` even with typed input
- ALWAYS: `textContent` or sanitize with DOMPurify

**CWE-1321: Prototype Pollution**
- NEVER: Spread untrusted objects: `{...base, ...userObject}`
- ALWAYS: Validate with Zod `.strict()`, use `Object.create(null)`

**CWE-704: Incorrect Type Assertion**
- NEVER: `const user = data as User` without validation
- ALWAYS: `const user = UserSchema.parse(data)` - validate then type

**CWE-476: Null Pointer via Non-null Assertion**
- NEVER: `user.profile!.name` without certainty
- ALWAYS: `user.profile?.name ?? 'default'` with optional chaining

### 0.3 Risk Level: MEDIUM

**Verification requirements for MEDIUM risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 Types ≠ Runtime Safety (CWE-20)

**Principle:** TypeScript types are ONLY compile-time. They provide ZERO runtime security. Always validate at runtime.

```typescript
// ❌ WRONG - Types don't protect at runtime
interface UserInput {
    userId: number;
    role: 'admin' | 'user';
}

function processInput(input: UserInput) {
    // At runtime, input could be ANYTHING
    db.query(`SELECT * FROM users WHERE id = ${input.userId}`);  // SQL injection!
}

// ✅ CORRECT - Runtime validation with Zod
import { z } from 'zod';

const UserInputSchema = z.object({
    userId: z.number().int().positive(),
    role: z.enum(['admin', 'user']),
});

function processInput(rawInput: unknown) {
    const input = UserInputSchema.parse(rawInput);  // Runtime validation
    db.query('SELECT * FROM users WHERE id = $1', [input.userId]);  // Parameterized
}
```

### 1.2 No `any` Type (CWE-1287)

**Principle:** `any` bypasses ALL type checking. Use `unknown` and narrow types explicitly.

```typescript
// ❌ WRONG - any allows any operation
function processData(data: any) {
    return data.toUpperCase();  // No error, crashes at runtime if not string
}

// ❌ WRONG - Type assertion without validation
const userData = JSON.parse(response) as User;  // Could be anything!

// ✅ CORRECT - unknown requires explicit narrowing
function processData(data: unknown): string {
    if (typeof data !== 'string') {
        throw new Error('Expected string');
    }
    return data.toUpperCase();  // TypeScript knows it's string now
}

// ✅ CORRECT - Runtime validation
import { z } from 'zod';
const UserSchema = z.object({ name: z.string(), email: z.string().email() });
const userData = UserSchema.parse(JSON.parse(response));
```

### 1.3 Prototype Pollution Prevention (CWE-1321)

**Principle:** Never use Object.assign or spread with untrusted data on objects that could affect prototypes.

```typescript
// ❌ WRONG - Prototype pollution possible
function mergeConfig(base: object, userInput: object) {
    return { ...base, ...userInput };  // userInput could have __proto__
}

// ❌ WRONG - Directly mutating with untrusted data
Object.assign(config, JSON.parse(userProvidedJson));

// ✅ CORRECT - Validate and whitelist properties
import { z } from 'zod';

const ConfigSchema = z.object({
    theme: z.enum(['light', 'dark']),
    language: z.string().max(10),
}).strict();  // Rejects unknown keys

function mergeConfig(base: Config, userInput: unknown): Config {
    const validated = ConfigSchema.parse(userInput);
    return { ...base, ...validated };
}

// ✅ CORRECT - Use Object.create(null) for dictionaries
const safeDict: Record<string, string> = Object.create(null);
```

### 1.4 XSS Prevention (CWE-79)

**Principle:** Never insert user data into DOM without proper encoding.

```typescript
// ❌ WRONG - innerHTML with user data
element.innerHTML = `<div>${userData}</div>`;

// ❌ WRONG - React dangerouslySetInnerHTML
<div dangerouslySetInnerHTML={{ __html: userContent }} />

// ✅ CORRECT - Use textContent (auto-escapes)
element.textContent = userData;

// ✅ CORRECT - React auto-escapes by default
<div>{userData}</div>

// ✅ CORRECT - If HTML needed, sanitize with DOMPurify
import DOMPurify from 'dompurify';
const sanitized = DOMPurify.sanitize(userContent);
<div dangerouslySetInnerHTML={{ __html: sanitized }} />
```

### 1.5 Strict TypeScript Configuration

**Principle:** Always enable strict mode. It catches errors that cause security issues.

```json
// ❌ WRONG - Loose configuration
{
    "compilerOptions": {
        "strict": false,
        "noImplicitAny": false
    }
}

// ✅ CORRECT - Maximum strictness
{
    "compilerOptions": {
        "strict": true,
        "noImplicitAny": true,
        "strictNullChecks": true,
        "strictFunctionTypes": true,
        "strictBindCallApply": true,
        "strictPropertyInitialization": true,
        "noImplicitThis": true,
        "alwaysStrict": true,
        "noUncheckedIndexedAccess": true,
        "exactOptionalPropertyTypes": true
    }
}
```

### 1.6 Secrets ≠ Code (CWE-798)

**Principle:** Never hardcode secrets. Never expose secrets to client-side code.

```typescript
// ❌ WRONG - Hardcoded secret
const API_KEY = 'sk-1234567890';

// ❌ WRONG - Secret in client bundle
// In React/Vue/Angular (client-side):
const apiKey = process.env.REACT_APP_SECRET_KEY;  // Bundled into JS!

// ✅ CORRECT - Server-side only secrets
// In Node.js (server-side):
const API_KEY = process.env.API_KEY;
if (!API_KEY) throw new Error('API_KEY required');

// ✅ CORRECT - Validate environment variables with Zod
import { z } from 'zod';

const EnvSchema = z.object({
    API_KEY: z.string().min(1),
    DATABASE_URL: z.string().url(),
});

const env = EnvSchema.parse(process.env);
```

### 1.7 Type Assertions Are Dangerous

**Principle:** Type assertions (`as`) bypass type checking. Avoid unless you've validated the data.

```typescript
// ❌ WRONG - Assertion without validation
const user = JSON.parse(data) as User;  // No guarantee it's actually a User

// ❌ WRONG - Double assertion
const value = (input as unknown) as AdminUser;  // Complete bypass

// ❌ WRONG - Non-null assertion without certainty
const name = user.profile!.name;  // Crashes if profile is null

// ✅ CORRECT - Type guard with validation
function isUser(data: unknown): data is User {
    return (
        typeof data === 'object' &&
        data !== null &&
        'id' in data &&
        typeof (data as any).id === 'number'
    );
}

if (isUser(data)) {
    console.log(data.id);  // TypeScript knows it's User
}

// ✅ CORRECT - Optional chaining with fallback
const name = user.profile?.name ?? 'Unknown';
```

### 1.8 Supply Chain Security (CWE-829)

**Principle:** Audit dependencies. Pin versions. Use lockfiles.

```bash
# ❌ WRONG - No version pinning
npm install lodash

# ❌ WRONG - No lockfile
.gitignore: package-lock.json

# ✅ CORRECT - Pin exact versions
npm install --save-exact lodash@4.17.21

# ✅ CORRECT - Audit regularly
npm audit
npm audit fix

# ✅ CORRECT - Use lockfile
git add package-lock.json
```

---

## 2. Version Requirements

**ALWAYS use these minimum versions:**
```
typescript>=5.3.0       # satisfies operator, better inference
zod>=3.22.0             # Runtime validation
@types/node>=20.0.0     # Node.js types
eslint>=8.50.0          # TypeScript ESLint support
```

**WHEN generating package.json** → pin these exact versions or higher.

---

## 3. Code Patterns

### 3.1 WHEN validating external input

```typescript
import { z } from 'zod';

// Define schema
const CreateUserSchema = z.object({
    name: z.string().min(1).max(100),
    email: z.string().email(),
    age: z.number().int().min(0).max(150).optional(),
});

// Infer TypeScript type from schema
type CreateUserInput = z.infer<typeof CreateUserSchema>;

// Validate at runtime
function createUser(rawInput: unknown): User {
    const input = CreateUserSchema.parse(rawInput);  // Throws if invalid
    // Now input is typed and validated
    return db.users.create(input);
}

// Safe parsing (no throw)
const result = CreateUserSchema.safeParse(rawInput);
if (!result.success) {
    console.error(result.error.issues);
    return;
}
// result.data is validated
```

### 3.2 WHEN creating discriminated unions

```typescript
// API response with proper error handling
type ApiResponse<T> =
    | { success: true; data: T }
    | { success: false; error: string; code: number };

function handleResponse<T>(response: ApiResponse<T>): T {
    if (!response.success) {
        throw new Error(`API Error ${response.code}: ${response.error}`);
    }
    return response.data;  // TypeScript knows it's success case
}

// State management with discriminated unions
type LoadingState<T> =
    | { status: 'idle' }
    | { status: 'loading' }
    | { status: 'success'; data: T }
    | { status: 'error'; error: Error };

function render(state: LoadingState<User>) {
    switch (state.status) {
        case 'idle':
            return <Idle />;
        case 'loading':
            return <Spinner />;
        case 'success':
            return <UserProfile user={state.data} />;  // data is available
        case 'error':
            return <Error message={state.error.message} />;
    }
}
```

### 3.3 WHEN creating type-safe API clients

```typescript
import { z } from 'zod';

const UserSchema = z.object({
    id: z.number(),
    name: z.string(),
    email: z.string().email(),
});

type User = z.infer<typeof UserSchema>;

async function fetchUser(id: number): Promise<User> {
    const response = await fetch(`/api/users/${id}`);
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }
    const json = await response.json();
    return UserSchema.parse(json);  // Validates response
}
```

### 3.4 WHEN using generics

```typescript
// Generic with constraints
interface HasId {
    id: string | number;
}

function findById<T extends HasId>(items: T[], id: T['id']): T | undefined {
    return items.find(item => item.id === id);
}

// Generic factory with proper typing
function createRepository<T extends HasId>() {
    const items: T[] = [];

    return {
        add(item: T): void {
            items.push(item);
        },
        findById(id: T['id']): T | undefined {
            return items.find(item => item.id === id);
        },
        getAll(): readonly T[] {
            return items;
        },
    };
}
```

### 3.5 WHEN using branded types for type-safe IDs

```typescript
// ❌ WRONG - String IDs can be mixed up
function getUser(userId: string): User { /* ... */ }
function getPost(postId: string): Post { /* ... */ }

// Accidentally passing wrong ID compiles!
const user = getUser(postId);

// ✅ CORRECT - Branded types prevent mixing
type UserId = string & { readonly brand: unique symbol };
type PostId = string & { readonly brand: unique symbol };

function createUserId(id: string): UserId {
  return id as UserId;
}

function createPostId(id: string): PostId {
  return id as PostId;
}

function getUser(id: UserId): User { /* ... */ }
function getPost(id: PostId): Post { /* ... */ }

// Now this is a compile error!
const userId = createUserId('user-123');
const postId = createPostId('post-456');
// getUser(postId); // Error: Argument of type 'PostId' is not assignable
```

### 3.6 WHEN using utility types

```typescript
// Pick and Omit
interface User {
  id: string;
  email: string;
  password: string;
  name: string;
}

type PublicUser = Omit<User, 'password'>;
type UserCredentials = Pick<User, 'email' | 'password'>;

// Partial and Required
type UserUpdate = Partial<Omit<User, 'id'>>;
type RequiredUser = Required<User>;

// Record for dictionaries
type UserMap = Record<string, User>;

// Extract and Exclude
type EventTypes = 'click' | 'scroll' | 'keydown' | 'keyup';
type KeyboardEvents = Extract<EventTypes, `key${string}`>;  // 'keydown' | 'keyup'
type NonKeyboardEvents = Exclude<EventTypes, `key${string}`>;  // 'click' | 'scroll'

// Template literal types
type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';
type ApiRoute = `/api/${string}`;
type ApiEndpoint = `${HttpMethod} ${ApiRoute}`;

// Conditional types
type ArrayElement<T> = T extends (infer E)[] ? E : never;

// Mapped types with key remapping
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};

type UserGetters = Getters<User>;
// { getId: () => string; getEmail: () => string; ... }
```

### 3.7 WHEN handling nullable values

```typescript
// ❌ WRONG - Non-null assertion
const name = user.profile!.name;

// ✅ CORRECT - Optional chaining with fallback
const name = user.profile?.name ?? 'Unknown';

// ✅ CORRECT - Explicit null check
function getProfileName(user: User): string {
    if (user.profile === null || user.profile === undefined) {
        return 'No profile';
    }
    return user.profile.name;
}

// ✅ CORRECT - Type guard
function hasProfile(user: User): user is User & { profile: Profile } {
    return user.profile !== null && user.profile !== undefined;
}

if (hasProfile(user)) {
    console.log(user.profile.name);  // TypeScript knows profile exists
}
```

---

## 4. Anti-Patterns

### 4.1 Using `any`

**NEVER** use `any` (CWE-1287):
```typescript
// ❌ WRONG - Completely disables type checking
function process(data: any) { ... }
const x: any = unknownValue;

// ✅ CORRECT - Use unknown and narrow
function process(data: unknown) {
    if (typeof data === 'string') { ... }
}
```

### 4.2 Type Assertions Without Validation

**NEVER** assert types without runtime validation:
```typescript
// ❌ WRONG - No runtime guarantee
const user = response.data as User;

// ✅ CORRECT - Validate first
const user = UserSchema.parse(response.data);
```

### 4.3 Ignoring strictNullChecks

**NEVER** disable strict null checks:
```typescript
// ❌ WRONG - Null errors at runtime
{
    "compilerOptions": {
        "strictNullChecks": false
    }
}

// ✅ CORRECT - Handle nulls explicitly
const name = user?.name ?? 'default';
```

### 4.4 eval and Function Constructor

**NEVER** use eval or new Function with user input (CWE-94):
```typescript
// ❌ WRONG - Code injection
eval(userInput);
new Function(userInput)();

// ✅ CORRECT - Use proper parsing/validation
const result = JSON.parse(userInput);
```

---

## 5. Testing

**ALWAYS write tests with type coverage:**
```typescript
import { describe, it, expect } from 'vitest';
import { expectTypeOf } from 'expect-type';

describe('createUser', () => {
    it('should create user with valid input', () => {
        const user = createUser({ name: 'John', email: 'john@example.com' });
        expect(user.name).toBe('John');
        expect(user.email).toBe('john@example.com');
    });

    it('should reject invalid email', () => {
        expect(() => createUser({ name: 'John', email: 'invalid' }))
            .toThrow('Invalid email');
    });

    it('should have correct types', () => {
        const user = createUser({ name: 'John', email: 'john@example.com' });
        expectTypeOf(user).toMatchTypeOf<User>();
        expectTypeOf(user.name).toBeString();
    });
});

// Type-level tests
describe('types', () => {
    it('ApiResponse type is correct', () => {
        type SuccessResponse = Extract<ApiResponse<User>, { success: true }>;
        expectTypeOf<SuccessResponse>().toHaveProperty('data');
    });
});
```

**Test coverage requirements:**
- [ ] Runtime behavior tests
- [ ] Type tests with expect-type
- [ ] Error case tests (invalid input)
- [ ] Edge case tests (null, undefined, empty)

---

## 6. Pre-Generation Checklist

**BEFORE generating any TypeScript code:**

- [ ] Strict mode: `"strict": true` in tsconfig.json
- [ ] No `any`: Use `unknown` and narrow types
- [ ] Runtime validation: Zod/Yup for external input
- [ ] Nullable handling: Optional chaining, nullish coalescing
- [ ] No type assertions: Validate instead of asserting
- [ ] XSS prevention: textContent, not innerHTML
- [ ] Secrets: Server-side only, from environment
- [ ] Dependencies: Pinned versions, audited
- [ ] Type tests: expect-type for type correctness
- [ ] Discriminated unions: For state management
