# TypeScript Anti-Patterns

This document lists common mistakes and anti-patterns to avoid in TypeScript development.

## Mistake 1: Using `any`

The `any` type defeats the purpose of TypeScript by disabling all type checking.

```typescript
// ❌ DON'T: Bypasses all type safety
function process(data: any) {
    return data.foo.bar.baz;  // No type checking, runtime errors likely
}

// ✅ DO: Use `unknown` for unknown types
function process(data: unknown) {
    if (isValidData(data)) {
        return data.foo.bar.baz;  // Type-safe after validation
    }
    throw new Error('Invalid data');
}

// ✅ DO: Use proper types
interface Data {
    foo: {
        bar: {
            baz: string;
        };
    };
}

function process(data: Data) {
    return data.foo.bar.baz;  // Fully type-safe
}
```

**Why it's bad**:
- Disables type checking
- No IDE autocompletion
- Runtime errors not caught at compile time
- Makes refactoring dangerous

---

## Mistake 2: Ignoring Strict Mode

Running TypeScript without strict mode misses many potential bugs.

```typescript
// ❌ DON'T: Disable strict mode
{
    "compilerOptions": {
        "strict": false
    }
}

// ✅ DO: Always enable strict mode
{
    "compilerOptions": {
        "strict": true,
        "noImplicitAny": true,
        "strictNullChecks": true,
        "strictFunctionTypes": true,
        "strictBindCallApply": true,
        "strictPropertyInitialization": true,
        "noImplicitThis": true,
        "alwaysStrict": true
    }
}
```

**Why it's bad**:
- Misses null/undefined errors
- Allows implicit `any` types
- No function type checking
- Property initialization not enforced

---

## Mistake 3: Type Assertion Abuse

Type assertions bypass TypeScript's type checker and should be used sparingly.

```typescript
// ❌ DON'T: Assert without validation
const user = apiResponse as User;
user.email.toLowerCase();  // Crashes if email is undefined

// ❌ DON'T: Double assertion
const value = (data as any) as User;

// ✅ DO: Validate before asserting
function validateUser(data: unknown): User {
    if (
        typeof data === 'object' &&
        data !== null &&
        'id' in data &&
        'email' in data &&
        typeof (data as any).email === 'string'
    ) {
        return data as User;
    }
    throw new Error('Invalid user data');
}

const user = validateUser(apiResponse);
```

**Why it's bad**:
- Bypasses type safety
- No runtime validation
- Source of runtime errors
- Breaks refactoring

---

## Mistake 4: Not Using Utility Types

Manually creating partial or picked types leads to maintenance issues.

```typescript
// ❌ DON'T: Manually create partial types
interface User {
    id: string;
    name: string;
    email: string;
}

interface UserUpdate {
    id?: string;
    name?: string;
    email?: string;
}

// ✅ DO: Use Partial utility type
type UserUpdate = Partial<User>;

// ❌ DON'T: Manually pick properties
interface UserPublic {
    id: string;
    name: string;
}

// ✅ DO: Use Pick utility type
type UserPublic = Pick<User, 'id' | 'name'>;

// ❌ DON'T: Manually omit properties
interface UserCreate {
    name: string;
    email: string;
}

// ✅ DO: Use Omit utility type
type UserCreate = Omit<User, 'id'>;
```

**Why it's bad**:
- Duplicate code
- Doesn't stay in sync with source
- More maintenance burden
- Easy to forget properties

---

## Mistake 5: Overusing Enums

Enums have runtime overhead and can be replaced with union types.

```typescript
// ❌ DON'T: Use enums unnecessarily
enum Status {
    Active = 'active',
    Inactive = 'inactive',
    Pending = 'pending'
}

// ✅ DO: Use const objects with 'as const'
const Status = {
    Active: 'active',
    Inactive: 'inactive',
    Pending: 'pending'
} as const;

type Status = typeof Status[keyof typeof Status];

// ✅ DO: Use string literal unions
type Status = 'active' | 'inactive' | 'pending';
```

**Why it's bad**:
- Adds runtime code
- Can't tree-shake
- Reverse mapping adds size
- Union types are simpler

---

## Mistake 6: Not Handling Null/Undefined

Failing to handle null/undefined leads to runtime crashes.

```typescript
// ❌ DON'T: Ignore potential null/undefined
function getUserName(id: string): string {
    const user = users.find(u => u.id === id);
    return user.name;  // Crashes if user is undefined
}

// ✅ DO: Handle null/undefined explicitly
function getUserName(id: string): string | null {
    const user = users.find(u => u.id === id);
    return user?.name ?? null;
}

// ✅ DO: Use optional chaining
function getUserName(id: string): string | undefined {
    return users.find(u => u.id === id)?.name;
}

// ✅ DO: Throw if required
function getUserName(id: string): string {
    const user = users.find(u => u.id === id);
    if (!user) {
        throw new Error(`User ${id} not found`);
    }
    return user.name;
}
```

**Why it's bad**:
- Runtime crashes
- Poor user experience
- Hard to debug
- No error handling

---

## Mistake 7: Using `@ts-ignore`

`@ts-ignore` comments suppress errors without fixing the underlying issue.

```typescript
// ❌ DON'T: Suppress errors
// @ts-ignore
const result = someFunction();

// ❌ DON'T: Use @ts-expect-error without reason
// @ts-expect-error
const value = data.property;

// ✅ DO: Fix the type issue
function someFunction(): ReturnType {
    // Implementation
}
const result = someFunction();

// ✅ DO: Use type guards
if (hasProperty(data, 'property')) {
    const value = data.property;
}
```

**Why it's bad**:
- Hides real issues
- Breaks with code changes
- No explanation for future developers
- Technical debt

---

## Mistake 8: Non-null Assertion Abuse

The `!` operator asserts non-null without validation.

```typescript
// ❌ DON'T: Use ! without certainty
function getUser(id: string) {
    return users.find(u => u.id === id)!;  // Crashes if not found
}

// ✅ DO: Handle undefined case
function getUser(id: string): User | undefined {
    return users.find(u => u.id === id);
}

// ✅ DO: Validate before asserting
function getUser(id: string): User {
    const user = users.find(u => u.id === id);
    if (!user) {
        throw new Error(`User ${id} not found`);
    }
    return user;
}
```

**Why it's bad**:
- Runtime crashes
- No null safety
- Defeats strictNullChecks
- Hard to debug

---

## Mistake 9: Implicit Return Types

Not specifying return types can lead to unexpected type inference.

```typescript
// ❌ DON'T: Omit return types for public APIs
function getUser(id: string) {
    return users.find(u => u.id === id);
}
// Return type might change unexpectedly

// ✅ DO: Specify return types
function getUser(id: string): User | undefined {
    return users.find(u => u.id === id);
}
```

**Why it's bad**:
- API changes not caught
- Inference can be wrong
- Poor documentation
- Breaking changes silent

---

## Mistake 10: Not Using `readonly`

Mutable data structures can lead to bugs.

```typescript
// ❌ DON'T: Allow mutation of arrays/objects
interface Config {
    ports: number[];
    settings: { [key: string]: string };
}

// ✅ DO: Use readonly for immutable data
interface Config {
    readonly ports: readonly number[];
    readonly settings: Readonly<Record<string, string>>;
}

// ✅ DO: Use ReadonlyArray
function process(items: ReadonlyArray<Item>) {
    items.push(newItem);  // Compile error - prevents mutation
}
```

**Why it's bad**:
- Unexpected mutations
- Hard to reason about state
- Race conditions
- Bug source

---

## Common Anti-Pattern Summary

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Using `any` | No type safety | Use `unknown` or proper types |
| Disabled strict mode | Misses bugs | Enable strict mode |
| Type assertion abuse | Bypasses checks | Validate before asserting |
| Manual types | Duplication | Use utility types |
| Overusing enums | Runtime overhead | Use const objects/unions |
| Ignoring null/undefined | Runtime crashes | Handle explicitly |
| Using `@ts-ignore` | Hides issues | Fix underlying problem |
| Non-null assertion `!` | Crashes | Validate first |
| Implicit return types | API instability | Specify return types |
| Mutable data | Unexpected changes | Use `readonly` |

---

## Quick Checklist: Avoid These

- [ ] No `any` types
- [ ] Strict mode enabled
- [ ] No type assertions without validation
- [ ] Using utility types where appropriate
- [ ] Prefer const objects over enums
- [ ] Handling null/undefined explicitly
- [ ] No `@ts-ignore` or `@ts-expect-error`
- [ ] No `!` non-null assertions without validation
- [ ] Return types specified for public APIs
- [ ] Using `readonly` for immutable data
