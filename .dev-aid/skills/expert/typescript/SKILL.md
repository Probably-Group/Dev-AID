---
name: typescript
description: Type-safe development patterns for JARVIS AI Assistant
risk_level: MEDIUM
version: 1.0.0
---

# TypeScript Development Skill

> **File Organization**: This skill uses split structure. See `references/` for advanced patterns and security examples.


### 0.4 Progressive Disclosure (500-Line Limit)

**⚠️ CRITICAL**: This SKILL.md file MUST stay <500 lines for Claude Code to load it.

**If this file is approaching 500 lines**:
- Move detailed examples to `references/advanced-patterns.md`
- Move security examples to `references/security-examples.md`
- Move troubleshooting to `references/troubleshooting.md`
- Keep only summaries and links in main file

📚 **For complete progressive disclosure guide**: See `../../../template-references/progressive-disclosure.md`

---

## 1. Overview

This skill provides TypeScript expertise for the JARVIS AI Assistant, ensuring type safety across the entire codebase including Vue components, API routes, 3D rendering, and state management.

**Risk Level**: MEDIUM - Type system prevents runtime errors, enforces contracts, but misconfiguration can lead to security gaps

**Primary Use Cases**:
- Defining type-safe interfaces for JARVIS system data
- Runtime validation with Zod schemas
- Generic patterns for reusable HUD components
- Strict null checking to prevent crashes

## 2. Core Responsibilities

### 2.1 Fundamental Principles

1. **TDD First**: Write tests before implementation - red, green, refactor
2. **Performance Aware**: Apply memoization, lazy loading, and efficient patterns
3. **Strict Mode Always**: Enable all strict compiler options - no shortcuts
4. **Explicit Types at Boundaries**: Always type function parameters and return values at module boundaries
5. **Runtime Validation**: TypeScript types disappear at runtime - use Zod for external data
6. **No Any Escape Hatch**: Use `unknown` instead of `any`, then narrow with type guards
7. **Immutable by Default**: Prefer `readonly` and `as const` for data integrity
8. **Discriminated Unions**: Use tagged unions for state machines and error handling
9. **Branded Types**: Create nominal types for IDs and sensitive values

## 3. Technology Stack & Versions

### 3.1 Recommended Versions

| Package | Version | Security Notes |
|---------|---------|----------------|
| typescript | ^5.3.0 | Latest stable with improved type inference |
| zod | ^3.22.0 | Runtime validation, schema-first |
| @types/node | ^20.0.0 | Match Node.js version |

### 3.2 Compiler Configuration

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "exactOptionalPropertyTypes": true,
    "noPropertyAccessFromIndexSignature": true,
    "forceConsistentCasingInFileNames": true,
    "verbatimModuleSyntax": true,
    "moduleResolution": "bundler",
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"]
  }
}
```


## 4. Quality Assurance Checklist

**Before implementing this skill, ensure**:

### 4.1 Pre-Implementation Setup
- [ ] Virtual environment created and activated
- [ ] Dependencies installed from requirements.txt
- [ ] Pre-commit hooks installed (`pre-commit install`)
- [ ] Linters installed (black, isort, flake8, mypy, bandit)

### 4.2 Dependency Management
- [ ] All dependencies pinned with exact versions (==)
- [ ] No manual transitive dependency pins
- [ ] Dependencies tested in clean environment

### 4.3 Code Quality Gates (Run BEFORE committing)
- [ ] `black .` - Code formatted
- [ ] `isort .` - Imports sorted
- [ ] `flake8 . --max-line-length=120` - No linting errors
- [ ] `mypy . --ignore-missing-imports` - Type checking passes
- [ ] `bandit -r .` - Security scan clean

### 4.4 Security Validation
- [ ] Input validation for ALL external inputs
- [ ] Path traversal prevention implemented
- [ ] Command injection prevention (no shell=True)
- [ ] SQL injection prevention (parameterized queries)
- [ ] Secrets not in code or error messages

📚 **For complete security validation guide**: See `../../../template-references/security-framework.md`

### 4.5 Test Coverage Requirements
- [ ] Tests written BEFORE implementation (TDD)
- [ ] Unit tests for all public functions
- [ ] Edge case tests (empty, null, max values)
- [ ] Security tests (injection, traversal, overflow)
- [ ] Code coverage >80%

### 4.6 Documentation Requirements
- [ ] Docstrings for all public functions/classes
- [ ] Security considerations documented
- [ ] Examples of correct usage
- [ ] Known limitations documented

---

## 5. Implementation Patterns

## 5. Implementation Patterns

📚 **For complete details**: See `references/implementation-patterns.md`

---
## 6. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```typescript
// tests/utils/command-parser.test.ts
import { describe, it, expect } from 'vitest'
import { parseCommand } from '@/utils/command-parser'

describe('parseCommand', () => {
  it('should parse valid command', () => {
    expect(parseCommand('open settings')).toEqual({
      action: 'open', target: 'settings', parameters: {}
    })
  })

  it('should extract parameters', () => {
    expect(parseCommand('set volume to 80')).toEqual({
      action: 'set', target: 'volume', parameters: { value: 80 }
    })
  })

  it('should throw on empty command', () => {
    expect(() => parseCommand('')).toThrow('Command cannot be empty')
  })
})
```

### Step 2: Implement Minimum to Pass

Write only code needed to make tests green.

### Step 3: Refactor if Needed

Improve code quality while keeping tests green.

### Step 4: Run Full Verification

```bash
npx vitest run              # Unit tests
npx eslint . --ext .ts,.tsx # Linting
npx tsc --noEmit            # Type checking
```

## 7. Performance Patterns

### 6.1 Memoization

```typescript
// ❌ BAD - Recalculates on every render
const processed = data.map(item => heavyTransform(item))

// ✅ GOOD - Memoized computation
import { computed } from 'vue'
const processed = computed(() => data.value.map(item => heavyTransform(item)))
```

### 6.2 Lazy Loading

```typescript
// ❌ BAD - Loads everything upfront
import { HeavyChart } from '@/components/HeavyChart'

// ✅ GOOD - Lazy load heavy components
import { defineAsyncComponent } from 'vue'
const HeavyChart = defineAsyncComponent(() => import('@/components/HeavyChart'))
```

### 6.3 Debounce/Throttle

```typescript
// ❌ BAD - API call on every keystroke
const handleSearch = (q: string) => fetchResults(q)

// ✅ GOOD - Debounced search (300ms delay)
import { useDebounceFn } from '@vueuse/core'
const debouncedSearch = useDebounceFn((q: string) => fetchResults(q), 300)
```

### 6.4 Efficient Data Structures

```typescript
// ❌ BAD - O(n) lookup
const user = users.find(u => u.id === id)

// ✅ GOOD - O(1) lookup with Map
const userMap = new Map(users.map(u => [u.id, u]))
const user = userMap.get(id)

// ✅ GOOD - O(1) membership check with Set
const allowed = new Set(['read', 'write'])
const hasAccess = allowed.has(permission)
```

### 6.5 Parallel Async Operations

```typescript
// ❌ BAD - Sequential (total = sum of times)
const user = await fetchUser()
const metrics = await fetchMetrics()

// ✅ GOOD - Parallel (total = max of times)
const [user, metrics] = await Promise.all([fetchUser(), fetchMetrics()])

// ✅ GOOD - With error handling
const results = await Promise.allSettled([fetchUser(), fetchMetrics()])
```

## 8. Security Standards

### 7.1 Known Vulnerabilities

TypeScript itself has a strong security record. Main risks come from:

| Risk Area | Description | Mitigation |
|-----------|-------------|------------|
| Type Erasure | Types don't exist at runtime | Use Zod for external data validation |
| Any Type | Disables type checking | Enable noImplicitAny, use unknown |
| Type Assertions | Can bypass type system | Avoid `as`, use type guards instead |

### 7.2 OWASP Top 10 Coverage

| OWASP Category | TypeScript Mitigation |
|----------------|----------------------|
| A03 Injection | Typed APIs prevent string interpolation in queries |
| A04 Insecure Design | Strong typing enforces secure interfaces |
| A08 Software Integrity | Compile-time checks catch errors before deployment |

### 7.3 Secure Type Patterns

```typescript
// ❌ DANGEROUS - Type assertion bypasses safety
const userData = apiResponse as User

// ✅ SECURE - Runtime validation
const userData = userSchema.parse(apiResponse)

// ❌ DANGEROUS - any disables all checks
function process(data: any) { /* ... */ }

// ✅ SECURE - unknown requires narrowing
function process(data: unknown) {
  const validated = commandSchema.parse(data)
  // Now safely typed
}
```

## 9. Testing & Quality

```typescript
// Type testing with vitest
import { expectTypeOf } from 'vitest'

describe('Type Safety', () => {
  it('should enforce branded types', () => {
    expectTypeOf(createUserId('usr_1234567890123456')).toEqualTypeOf<UserId>()
  })
})

// Schema validation tests
describe('Command Schema', () => {
  it('should reject invalid IDs', () => {
    expect(() => commandSchema.parse({ id: 'invalid' })).toThrow()
  })

  it('should accept valid commands', () => {
    const result = commandSchema.parse({ id: 'cmd_1234567890123456', action: 'query' })
    expect(result.action).toBe('query')
  })
})
```

## 10. Common Mistakes & Anti-Patterns

### 9.1 Critical Security Anti-Patterns

#### Never: Use Type Assertions for External Data

```typescript
// ❌ DANGEROUS - No runtime validation
const user = JSON.parse(data) as User

// ✅ SECURE - Validate at runtime
const user = userSchema.parse(JSON.parse(data))
```

#### Never: Ignore Null/Undefined Checks

```typescript
// ❌ DANGEROUS - Runtime crash if undefined
function getConfig(key: string) {
  return config[key]## 7. Performance Patterns

// ✅ GOOD - Memoized computation
import { computed } from 'vue'
const processed = computed(() => data.value.map(item => heavyTransform(item)))
```

📚 **For complete details**: See `references/performance-patterns.md`

---
ore Committing

- [ ] All tests pass (`npx vitest run`)
- [ ] No linting errors (`npx eslint .`)
- [ ] No TypeScript errors (`npx tsc --noEmit`)
- [ ] All API inputs validated at runtime
- [ ] No type assertions on external data
- [ ] Performance patterns applied where needed

## 12. Summary

TypeScript provides compile-time safety for JARVIS development:

1. **Strict Configuration**: Enable all strict options for maximum safety
2. **Runtime Validation**: Types disappear at runtime - use Zod
3. **Branded Types**: Prevent mixing of IDs and sensitive values
4. **Type Guards**: Safely narrow `unknown` data with predicates

**Remember**: TypeScript only checks at compile time. Every boundary with external data must have runtime validation.

---

**References**:
- `references/advanced-patterns.md` - Complex type patterns
- `references/security-examples.md` - Secure typing practices
## 10. Common Mistakes & Anti-Patterns

## 10. Common Mistakes & Anti-Patterns

📚 **For complete details**: See `references/common-mistakes-anti-patterns.md`

---
