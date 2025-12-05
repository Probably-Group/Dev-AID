# TypeScript Performance Optimization

This document contains performance optimization patterns and best practices for TypeScript development.

## Pattern 1: Type Inference Optimization

```typescript
// Bad: Redundant type annotations slow down IDE and compiler
const users: Array<User> = [];
const result: Result<User, Error> = getUser(id);
const handler: (event: MouseEvent) => void = (event: MouseEvent) => {
    console.log(event.target);
};

// Good: Let TypeScript infer types
const users: User[] = [];
const result = getUser(id);  // Type inferred from function return
const handler = (event: MouseEvent) => {
    console.log(event.target);
};

// Bad: Over-specifying generic parameters
function identity<T>(value: T): T {
    return value;
}
const num = identity<number>(42);

// Good: Let inference work
const num = identity(42);  // T inferred as number
```

## Pattern 2: Efficient Conditional Types

```typescript
// Bad: Complex nested conditionals computed on every use
type DeepReadonly<T> = T extends (infer U)[]
    ? DeepReadonlyArray<U>
    : T extends object
    ? DeepReadonlyObject<T>
    : T;

type DeepReadonlyArray<T> = ReadonlyArray<DeepReadonly<T>>;
type DeepReadonlyObject<T> = {
    readonly [P in keyof T]: DeepReadonly<T[P]>;
};

// Good: Use built-in utility types when possible
type SimpleReadonly<T> = Readonly<T>;

// Good: Cache complex type computations
type CachedDeepReadonly<T> = T extends object
    ? { readonly [K in keyof T]: CachedDeepReadonly<T[K]> }
    : T;

// Bad: Excessive type unions
type Status = 'a' | 'b' | 'c' | 'd' | 'e' | /* ... 100 more */;

// Good: Use string literal with validation
type Status = string & { __status: true };
function isValidStatus(s: string): s is Status {
    return ['active', 'pending', 'completed'].includes(s);
}
```

## Pattern 3: Memoization with Types

```typescript
// Bad: No memoization for expensive computations
function expensiveTypeOperation<T extends object>(obj: T): ProcessedType<T> {
    // Called every render
    return processObject(obj);
}

// Good: Memoize with useMemo and proper typing
import { useMemo } from 'react';

function useProcessedData<T extends object>(obj: T): ProcessedType<T> {
    return useMemo(() => processObject(obj), [obj]);
}

// Bad: Creating new type guards on every call
function Component({ data }: Props) {
    const isValid = (item: unknown): item is ValidItem => {
        return validateItem(item);
    };
    return data.filter(isValid);
}

// Good: Define type guards outside component
function isValidItem(item: unknown): item is ValidItem {
    return validateItem(item);
}

function Component({ data }: Props) {
    return data.filter(isValidItem);
}

// Good: Memoize derived types with const assertions
const CONFIG = {
    modes: ['light', 'dark', 'system'] as const,
    themes: ['default', 'compact'] as const
};

type Mode = typeof CONFIG.modes[number];  // Computed once
type Theme = typeof CONFIG.themes[number];
```

## Pattern 4: Tree-Shaking Friendly Types

```typescript
// Bad: Barrel exports prevent tree-shaking
// index.ts
export * from './user';
export * from './product';
export * from './order';
// Imports entire module even if only using one type

// Good: Direct imports enable tree-shaking
import { User } from './models/user';
import { createUser } from './services/user-service';

// Bad: Class with many unused methods
class UserService {
    createUser() { }
    updateUser() { }
    deleteUser() { }
    // All methods bundled even if one used
}

// Good: Individual functions for tree-shaking
export function createUser() { }
export function updateUser() { }
export function deleteUser() { }

// Bad: Large type unions imported everywhere
import { AllEvents } from './events';

// Good: Import specific event types
import type { ClickEvent, KeyEvent } from './events/user-input';

// Good: Use `import type` for type-only imports
import type { User, Product } from './types';  // Stripped at compile time
import { createUser } from './services';       // Actual runtime import
```

## Pattern 5: Lazy Type Loading

```typescript
// Bad: Eager loading of all types
import { HeavyComponent, HeavyProps } from './heavy-module';

// Good: Dynamic import with proper typing
const HeavyComponent = lazy(() => import('./heavy-module'));
type HeavyProps = React.ComponentProps<typeof HeavyComponent>;

// Bad: Importing entire library for one type
import { z } from 'zod';  // Entire zod library

// Good: Import only what you need
import { z } from 'zod/lib/types';  // If available
// Or use type-only import
import type { ZodSchema } from 'zod';
```

## Performance Best Practices

1. **Minimize Type Complexity**: Avoid deeply nested conditional types
2. **Use Type Inference**: Let TypeScript infer types when possible
3. **Cache Type Computations**: Define complex types once and reuse
4. **Enable Tree-Shaking**: Use direct imports and `import type`
5. **Memoize Runtime Values**: Use `useMemo` for expensive computations
6. **Optimize Compiler Options**: Enable incremental compilation
7. **Avoid Redundant Annotations**: Only annotate when necessary
8. **Use Const Assertions**: For literal types computed once
