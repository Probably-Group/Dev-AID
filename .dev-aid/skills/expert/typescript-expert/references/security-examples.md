# TypeScript Security Examples

This document contains security best practices and examples for TypeScript development.

## TypeScript-Specific Security

### 1. Avoid Type Assertions

Type assertions can bypass TypeScript's type safety, leading to runtime errors and security vulnerabilities.

```typescript
// ❌ UNSAFE: Type assertion bypasses validation
const user = data as User;
// If data is malicious, all properties are accessible without validation

// ✅ SAFE: Use type guards for runtime validation
function isUser(value: unknown): value is User {
    return (
        typeof value === 'object' &&
        value !== null &&
        'id' in value &&
        'name' in value &&
        'email' in value &&
        typeof (value as any).id === 'string' &&
        typeof (value as any).name === 'string' &&
        typeof (value as any).email === 'string'
    );
}

if (isUser(data)) {
    const user = data;  // Type-safe and validated
}
```

### 2. Strict Null Checks

Enable strict null checks to prevent null/undefined reference errors that can lead to DoS attacks.

```json
{
    "compilerOptions": {
        "strictNullChecks": true,
        "strict": true
    }
}
```

```typescript
// ❌ UNSAFE: May throw at runtime
function getUserName(id: string) {
    const user = users.find(u => u.id === id);
    return user.name;  // Crashes if user is undefined
}

// ✅ SAFE: Explicit null handling
function getUserName(id: string): string | null {
    const user = users.find(u => u.id === id);
    return user?.name ?? null;
}
```

### 3. No Implicit Any

Prevent untyped data from entering your system.

```typescript
// ❌ UNSAFE: data can be anything
function process(data) {
    // No type checking on data
    return data.dangerousProperty;
}

// ✅ SAFE: Explicitly handle unknown data
function process(data: unknown) {
    if (isValidData(data)) {
        return data.safeProperty;
    }
    throw new Error('Invalid data');
}
```

## OWASP Top 10 2025 Mapping

### A01:2025 - Broken Access Control

Use branded types to prevent ID confusion:

```typescript
type UserId = string & { __brand: 'UserId' };
type AdminId = string & { __brand: 'AdminId' };

function getUserData(userId: UserId) { }
function getAdminData(adminId: AdminId) { }

// Prevents accidentally passing wrong ID type
const userId = 'user-123' as UserId;
const adminId = 'admin-456' as AdminId;

getUserData(adminId);  // Type error!
```

### A02:2025 - Security Misconfiguration

Enforce strict TypeScript configuration:

```json
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
        "noImplicitReturns": true,
        "noFallthroughCasesInSwitch": true
    }
}
```

### A03:2025 - Supply Chain

Validate @types packages and use type-safe wrappers:

```typescript
// ✅ Type-safe wrapper for external library
import type { ExternalLibConfig } from 'external-lib';

interface SafeConfig {
    apiKey: string;
    endpoint: string;
}

function validateConfig(config: unknown): SafeConfig {
    if (
        typeof config === 'object' &&
        config !== null &&
        'apiKey' in config &&
        'endpoint' in config
    ) {
        return config as SafeConfig;
    }
    throw new Error('Invalid configuration');
}
```

### A04:2025 - Insecure Design

Use discriminated unions for secure state management:

```typescript
type AuthState =
    | { status: 'unauthenticated' }
    | { status: 'authenticating' }
    | { status: 'authenticated'; user: User; token: string }
    | { status: 'error'; error: Error };

// Impossible to access user/token in wrong state
function renderApp(state: AuthState) {
    switch (state.status) {
        case 'authenticated':
            return state.user.name;  // Type-safe access
        case 'unauthenticated':
            return 'Please login';
        case 'authenticating':
            return 'Loading...';
        case 'error':
            return state.error.message;
    }
}
```

### A05:2025 - Identification & Authentication

Use branded types for sensitive data:

```typescript
type HashedPassword = string & { __brand: 'HashedPassword' };
type PlainPassword = string & { __brand: 'PlainPassword' };

function hashPassword(plain: PlainPassword): HashedPassword {
    // Hash implementation
    return hash(plain) as HashedPassword;
}

function verifyPassword(plain: PlainPassword, hashed: HashedPassword): boolean {
    return hash(plain) === hashed;
}

// Prevents accidentally storing plain passwords
function storeUser(password: HashedPassword) { }

const plain = 'password123' as PlainPassword;
storeUser(plain);  // Type error! Must hash first
storeUser(hashPassword(plain));  // OK
```

### A06:2025 - Vulnerable Components

Create type-safe wrappers for vulnerable components:

```typescript
// ✅ Safe wrapper for dangerous eval-like operations
type SafeExpression = string & { __validated: true };

function validateExpression(expr: string): SafeExpression | null {
    // Whitelist allowed operations
    if (/^[a-zA-Z0-9+\-*/() ]+$/.test(expr)) {
        return expr as SafeExpression;
    }
    return null;
}

function calculate(expr: SafeExpression): number {
    // Safe to evaluate
    return eval(expr);
}
```

### A07:2025 - Cryptographic Failures

Type-safe cryptography:

```typescript
type EncryptedData = string & { __brand: 'Encrypted' };
type DecryptedData = string & { __brand: 'Decrypted' };

function encrypt(data: DecryptedData): EncryptedData {
    // Encryption implementation
    return encrypted as EncryptedData;
}

function decrypt(data: EncryptedData): DecryptedData {
    // Decryption implementation
    return decrypted as DecryptedData;
}

// Type system prevents using encrypted data directly
function processData(data: DecryptedData) { }

const encrypted = encrypt('sensitive' as DecryptedData);
processData(encrypted);  // Type error!
processData(decrypt(encrypted));  // OK
```

### A08:2025 - Injection

Use template literal types to prevent injection:

```typescript
type SqlQuery = `SELECT ${string} FROM ${string}`;
type TableName = 'users' | 'products' | 'orders';

function query(sql: SqlQuery, table: TableName) {
    // Only allows whitelisted table names
    return db.query(sql);
}

// ❌ This won't compile
query('DROP TABLE users', 'malicious');

// ✅ Type-safe query
query('SELECT * FROM users', 'users');
```

### A09:2025 - Logging Failures

Structured, type-safe logging:

```typescript
interface LogEntry {
    level: 'info' | 'warn' | 'error';
    message: string;
    timestamp: Date;
    context?: Record<string, unknown>;
}

function log(entry: LogEntry) {
    // Ensures all logs have consistent structure
    console.log(JSON.stringify(entry));
}

// ❌ Prevents accidentally logging sensitive data
interface SanitizedUser {
    id: string;
    name: string;
    // email and password excluded
}

function logUserAction(user: User) {
    const sanitized: SanitizedUser = {
        id: user.id,
        name: user.name
    };
    log({
        level: 'info',
        message: 'User action',
        timestamp: new Date(),
        context: { user: sanitized }
    });
}
```

### A10:2025 - Exception Handling

Type-safe error handling with Result types:

```typescript
type Result<T, E = Error> =
    | { success: true; data: T }
    | { success: false; error: E };

function riskyOperation(): Result<User> {
    try {
        const user = performOperation();
        return { success: true, data: user };
    } catch (error) {
        return {
            success: false,
            error: error instanceof Error ? error : new Error('Unknown error')
        };
    }
}

// Forces explicit error handling
const result = riskyOperation();
if (result.success) {
    console.log(result.data.name);  // Type-safe
} else {
    console.error(result.error.message);  // Type-safe
}
```

## Security Checklist

Before deploying TypeScript code:

- [ ] Strict mode enabled in tsconfig.json
- [ ] No `any` types in production code
- [ ] All external data validated with type guards
- [ ] Branded types used for sensitive data
- [ ] No type assertions without validation
- [ ] Discriminated unions for state management
- [ ] Input validation at boundaries
- [ ] Secure dependencies with @types validated
- [ ] Error handling with Result types
- [ ] Logging excludes sensitive data
