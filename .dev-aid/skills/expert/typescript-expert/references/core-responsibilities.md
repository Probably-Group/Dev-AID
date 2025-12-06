## 5. Core Responsibilities

### 1. Strict Type Safety

You will enforce strict type checking:
- Enable all strict mode flags in tsconfig.json
- Avoid `any` type - use `unknown` or proper types
- Use `strictNullChecks` to handle null/undefined explicitly
- Implement discriminated unions for complex state management
- Use type guards and type predicates for runtime checks
- Never use type assertions (`as`) unless absolutely necessary

**Example: Strict Configuration**
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
        "noUncheckedIndexedAccess": true
    }
}
```

### 2. Advanced Type System Usage

You will leverage TypeScript's type system:
- Create reusable generic types and functions
- Use utility types (Partial, Pick, Omit, Record, etc.)
- Implement conditional types for type transformations
- Use template literal types for string manipulation
- Create branded/nominal types for type safety
- Implement recursive types when appropriate

**Example: Generic Constraints**
```typescript
interface Entity {
    id: string;
    createdAt: Date;
}

function findById<T extends Entity>(items: T[], id: string): T | undefined {
    return items.find(item => item.id === id);
}
```

### 3. Clean Architecture with Types

You will structure code with proper typing:
- Define interfaces for all public APIs
- Use type aliases for complex types
- Separate types into dedicated files for reusability
- Use `readonly` for immutable data structures
- Implement proper error types with discriminated unions
- Use const assertions for literal types

**Example: Result Type Pattern**
```typescript
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

### 4. Configuration Excellence

You will configure TypeScript optimally:
- Use strict mode with all checks enabled
- Configure path aliases for clean imports
- Set up project references for monorepos
- Optimize compiler options for performance
- Configure source maps for debugging
- Set up incremental compilation

**Example: Optimized tsconfig.json**
```json
{
    "compilerOptions": {
        "target": "ES2022",
        "module": "ESNext",
        "moduleResolution": "bundler",
        "strict": true,
        "esModuleInterop": true,
        "skipLibCheck": true,
        "forceConsistentCasingInFileNames": true,
        "resolveJsonModule": true,
        "isolatedModules": true,
        "incremental": true,
        "sourceMap": true,
        "declaration": true,
        "declarationMap": true,
        "paths": {
            "@/*": ["./src/*"]
        }
    },
    "include": ["src/**/*"],
    "exclude": ["node_modules", "dist"]
}
```

---

