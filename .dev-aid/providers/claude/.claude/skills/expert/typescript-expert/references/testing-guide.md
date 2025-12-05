# TypeScript Testing Guide

This document contains comprehensive testing patterns for TypeScript applications.

## Type Testing with expect-type

```typescript
// tests/types.test.ts
import { expectTypeOf } from 'expect-type';
import type { User, CreateUserInput, Result } from '../src/types';

describe('Type definitions', () => {
    it('User should have correct shape', () => {
        expectTypeOf<User>().toHaveProperty('id');
        expectTypeOf<User>().toHaveProperty('email');
        expectTypeOf<User['id']>().toBeString();
    });

    it('Result type should be discriminated union', () => {
        type SuccessResult = Extract<Result<User>, { success: true }>;
        type ErrorResult = Extract<Result<User>, { success: false }>;

        expectTypeOf<SuccessResult>().toHaveProperty('data');
        expectTypeOf<ErrorResult>().toHaveProperty('error');
    });
});
```

## Unit Testing with Vitest

```typescript
// tests/user-service.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { UserService } from '../src/user-service';

describe('UserService', () => {
    let service: UserService;

    beforeEach(() => {
        service = new UserService();
    });

    it('should create user with valid input', async () => {
        const input = { name: 'Test', email: 'test@example.com' };
        const result = await service.create(input);

        expect(result.success).toBe(true);
        if (result.success) {
            expect(result.data).toMatchObject({
                name: 'Test',
                email: 'test@example.com'
            });
        }
    });

    it('should handle errors gracefully', async () => {
        const result = await service.create({ name: '', email: '' });

        expect(result.success).toBe(false);
        if (!result.success) {
            expect(result.error).toBeDefined();
        }
    });
});
```

## Mocking with Type Safety

```typescript
import { vi, type Mock } from 'vitest';
import type { ApiClient } from '../src/api-client';

// Type-safe mock
const mockApiClient: jest.Mocked<ApiClient> = {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
};

// Typed mock return values
mockApiClient.get.mockResolvedValue({
    success: true,
    data: { id: '1', name: 'Test' }
});
```

## Testing Best Practices

### 1. Test Type Definitions

Always test your type definitions to ensure they work as expected:

```typescript
import { expectTypeOf } from 'expect-type';

describe('Type Tests', () => {
    it('should enforce correct types', () => {
        expectTypeOf<User>().toMatchTypeOf<{ id: string }>();
        expectTypeOf<User['email']>().toBeString();
    });
});
```

### 2. Test Type Guards

Ensure type guards work correctly:

```typescript
describe('Type Guards', () => {
    it('isUser should correctly identify users', () => {
        const validUser = { id: '1', name: 'Test', email: 'test@example.com' };
        const invalidUser = { id: '1' };

        expect(isUser(validUser)).toBe(true);
        expect(isUser(invalidUser)).toBe(false);
    });
});
```

### 3. Test Discriminated Unions

Verify discriminated unions handle all cases:

```typescript
describe('Discriminated Unions', () => {
    it('should handle all LoadingState cases', () => {
        const idle: LoadingState<User> = { status: 'idle' };
        const loading: LoadingState<User> = { status: 'loading' };
        const success: LoadingState<User> = {
            status: 'success',
            data: { id: '1', name: 'Test' }
        };
        const error: LoadingState<User> = {
            status: 'error',
            error: new Error('Failed')
        };

        expect(renderUser(idle)).toBe('Click to load');
        expect(renderUser(loading)).toBe('Loading...');
        expect(renderUser(success)).toBe('Test');
        expect(renderUser(error)).toContain('Failed');
    });
});
```

### 4. Test Generic Functions

Test generic functions with different types:

```typescript
describe('Generic Functions', () => {
    it('findById should work with any Entity', () => {
        interface User extends Entity {
            name: string;
        }

        interface Product extends Entity {
            price: number;
        }

        const users: User[] = [{ id: '1', name: 'Test', createdAt: new Date() }];
        const products: Product[] = [{ id: '1', price: 100, createdAt: new Date() }];

        expect(findById(users, '1')?.name).toBe('Test');
        expect(findById(products, '1')?.price).toBe(100);
    });
});
```

## Testing Configuration

### vitest.config.ts

```typescript
import { defineConfig } from 'vitest/config';

export default defineConfig({
    test: {
        globals: true,
        environment: 'node',
        coverage: {
            provider: 'v8',
            reporter: ['text', 'json', 'html'],
            exclude: [
                'node_modules/',
                'dist/',
                '**/*.test.ts',
                '**/*.spec.ts'
            ]
        }
    }
});
```

### tsconfig.json for Tests

```json
{
    "extends": "./tsconfig.json",
    "compilerOptions": {
        "types": ["vitest/globals", "node"]
    },
    "include": ["tests/**/*", "src/**/*"]
}
```

## Test Coverage Goals

- **Unit Tests**: 80%+ coverage
- **Type Tests**: All public APIs
- **Integration Tests**: Critical paths
- **E2E Tests**: User workflows

## Testing Checklist

- [ ] Type definitions tested with expect-type
- [ ] Type guards tested with valid/invalid inputs
- [ ] Discriminated unions cover all cases
- [ ] Generic functions tested with multiple types
- [ ] Error cases tested
- [ ] Edge cases covered
- [ ] Mock types match actual types
- [ ] Test coverage meets goals
