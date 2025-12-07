## 3. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```typescript
// tests/user-service.test.ts
import { describe, it, expect } from 'vitest';
import { createUser, type User, type CreateUserInput } from '../src/user-service';

describe('createUser', () => {
    it('should create a user with valid input', () => {
        const input: CreateUserInput = {
            name: 'John Doe',
            email: 'john@example.com'
        };

        const result = createUser(input);

        expect(result.success).toBe(true);
        if (result.success) {
            expect(result.data.id).toBeDefined();
            expect(result.data.name).toBe('John Doe');
            expect(result.data.email).toBe('john@example.com');
        }
    });

    it('should fail with invalid email', () => {
        const input: CreateUserInput = {
            name: 'John',
            email: 'invalid'
        };

        const result = createUser(input);

        expect(result.success).toBe(false);
    });
});
```

### Step 2: Implement Minimum to Pass

```typescript
// src/user-service.ts
export interface User {
    id: string;
    name: string;
    email: string;
    createdAt: Date;
}

export interface CreateUserInput {
    name: string;
    email: string;
}

type Result<T, E = Error> =
    | { success: true; data: T }
    | { success: false; error: E };

function isValidEmail(email: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

export function createUser(input: CreateUserInput): Result<User> {
    if (!isValidEmail(input.email)) {
        return { success: false, error: new Error('Invalid email') };
    }

    const user: User = {
        id: crypto.randomUUID(),
        name: input.name,
        email: input.email,
        createdAt: new Date()
    };

    return { success: true, data: user };
}
```

### Step 3: Refactor If Needed

```typescript
// Refactor to use branded types for better type safety
type EmailAddress = string & { __brand: 'EmailAddress' };
type UserId = string & { __brand: 'UserId' };

export interface User {
    id: UserId;
    name: string;
    email: EmailAddress;
    createdAt: Date;
}

function validateEmail(email: string): EmailAddress | null {
    if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        return email as EmailAddress;
    }
    return null;
}
```

### Step 4: Run Full Verification

```bash
# Type checking
npx tsc --noEmit

# Run tests with coverage
npx vitest run --coverage

# Lint checking
npx eslint src --ext .ts

# Build verification
npm run build
```

---


