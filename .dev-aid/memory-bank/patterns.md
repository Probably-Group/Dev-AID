# Code Patterns - Team Conventions

**Purpose**: Document established patterns and anti-patterns (team-shared)
**Note**: For personal AI notes, use Claude's built-in memory (`~/.claude/projects/*/memory/`)

---

## Architecture Patterns

### Pattern: [Pattern Name]
**Category**: Architecture/Design/Implementation
**Status**: Active | Deprecated | Evolving

**When to Use**:
- Scenario 1
- Scenario 2

**Implementation**:
```typescript
// Code example
```

**Why This Works**:
- Reason 1
- Reason 2

**Real Example**:
- File: `src/path/to/example.ts`

---

## Anti-Patterns to Avoid

### Anti-Pattern: [Name]
**Why It's Bad**:
- Problem 1
- Problem 2

**What to Do Instead**:
```typescript
// Better approach
```

---

## Naming Conventions

### Files
- Components: `PascalCase.tsx`
- Utils: `camelCase.ts`
- Tests: `*.test.ts`

### Variables
- Constants: `UPPER_SNAKE_CASE`
- Functions: `camelCase`
- Classes: `PascalCase`

### Functions
- Boolean: `isXyz`, `hasXyz`, `canXyz`
- Handlers: `handleXyz`, `onXyz`
- Async: `fetchXyz`, `loadXyz`

---

## File Organization

```
src/
├── components/    # UI components
├── services/      # Business logic
├── utils/         # Pure utility functions
└── types/         # TypeScript types
```

---

**Usage**: Reference when implementing similar functionality.
Add new patterns as they're proven in production.
