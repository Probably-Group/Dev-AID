# TypeScript Implementation Patterns

This document contains detailed implementation patterns for TypeScript development.

## Pattern 1: Strict Null Checking

```typescript
// ❌ UNSAFE: Not handling null/undefined
function getUser(id: string) {
    const user = users.find(u => u.id === id);
    return user.name; // Error if user is undefined!
}

// ✅ SAFE: Explicit null handling
function getUser(id: string): string | undefined {
    const user = users.find(u => u.id === id);
    return user?.name;
}

// ✅ BETTER: Type guard
function getUser(id: string): string {
    const user = users.find(u => u.id === id);
    if (!user) {
        throw new Error(`User ${id} not found`);
    }
    return user.name;
}

// ✅ BEST: Result type pattern
type Result<T, E = Error> =
    | { success: true; data: T }
    | { success: false; error: E };

function getUser(id: string): Result<User> {
    const user = users.find(u => u.id === id);
    if (!user) {
        return { success: false, error: new Error('User not found') };
    }
    return { success: true, data: user };
}
```

---

## Pattern 2: Discriminated Unions

```typescript
// ✅ Type-safe state management
type LoadingState<T> =
    | { status: 'idle' }
    | { status: 'loading' }
    | { status: 'success'; data: T }
    | { status: 'error'; error: Error };

function renderUser(state: LoadingState<User>) {
    switch (state.status) {
        case 'idle':
            return 'Click to load';
        case 'loading':
            return 'Loading...';
        case 'success':
            return state.data.name;
        case 'error':
            return state.error.message;
    }
}

// ✅ API response types
type ApiResponse<T> =
    | { kind: 'success'; data: T; timestamp: number }
    | { kind: 'error'; error: string; code: number }
    | { kind: 'redirect'; url: string };
```

---

## Pattern 3: Generic Constraints

```typescript
// ✅ Constrained generics
interface Entity {
    id: string;
    createdAt: Date;
}

function findById<T extends Entity>(items: T[], id: string): T | undefined {
    return items.find(item => item.id === id);
}

// ✅ Multiple type parameters
function merge<T extends object, U extends object>(obj1: T, obj2: U): T & U {
    return { ...obj1, ...obj2 };
}

// ✅ Conditional types
type AsyncReturnType<T extends (...args: any) => any> =
    T extends (...args: any) => Promise<infer R> ? R : never;
```

---

## Pattern 4: Type Guards

```typescript
// ✅ Type guard function
function isUser(value: unknown): value is User {
    return (
        typeof value === 'object' &&
        value !== null &&
        'id' in value &&
        'name' in value &&
        typeof (value as any).id === 'string'
    );
}

// ✅ Assertion function
function assertIsUser(value: unknown): asserts value is User {
    if (!isUser(value)) {
        throw new Error('Not a user');
    }
}

function handleUser(value: unknown) {
    assertIsUser(value);
    console.log(value.name); // TypeScript knows value is User
}
```

---

## Pattern 5: Utility Types

```typescript
interface User {
    id: string;
    name: string;
    email: string;
    password: string;
}

// ✅ Partial - optional properties
type UserUpdate = Partial<User>;

// ✅ Pick - select properties
type UserPublic = Pick<User, 'id' | 'name' | 'email'>;

// ✅ Omit - exclude properties
type UserCreate = Omit<User, 'id'>;

// ✅ Record - object type
type UserRoles = Record<string, 'admin' | 'user'>;

// ✅ Readonly - immutable
type ImmutableUser = Readonly<User>;
```

---

## Pattern 6: Branded Types

```typescript
// ✅ Nominal typing for type safety
type Brand<T, TBrand> = T & { __brand: TBrand };

type UserId = Brand<string, 'UserId'>;
type EmailAddress = Brand<string, 'EmailAddress'>;

function createUserId(id: string): UserId {
    return id as UserId;
}

function sendEmail(to: EmailAddress) {
    // Implementation
}

const userId = createUserId('123');
const email = 'user@example.com' as EmailAddress;

sendEmail(userId); // Error!
sendEmail(email); // OK
```

---

## Pattern 7: Const Assertions

```typescript
// ✅ Const assertion for literal types
const config = {
    apiUrl: 'https://api.example.com',
    timeout: 5000
} as const;
// Type: { readonly apiUrl: "https://api.example.com"; readonly timeout: 5000 }

// ✅ Enum alternative
const Colors = {
    RED: '#ff0000',
    GREEN: '#00ff00'
} as const;

type Color = typeof Colors[keyof typeof Colors];
```
