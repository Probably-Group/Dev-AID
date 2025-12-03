# Code Patterns - Proven Solutions

**Purpose**: Institutional knowledge of proven code patterns
**Load Strategy**: On-demand (not auto-loaded)
**Update Frequency**: Weekly or when new pattern established

---

## 🏗️ Architecture Patterns

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

**Trade-offs**:
- Advantage: X
- Disadvantage: Y

**Real Example**:
- File: `src/path/to/example.ts`
- Lines: 45-67

---

## ❌ Anti-Patterns to Avoid

### Anti-Pattern: [Name]
**Why It's Bad**:
- Problem 1
- Problem 2

**What We Did Instead**:
```typescript
// Better approach
```

**Lesson Learned**:
- Insight from experience

---

## 🔒 Security Patterns

### Pattern: Authentication Flow
**Implementation**:
```typescript
// Secure auth pattern
```

**Security Considerations**:
- Check 1
- Check 2

**Common Mistakes**:
- Mistake 1 and why it's dangerous
- Mistake 2 and how to avoid

---

## ⚡ Performance Patterns

### Pattern: Caching Strategy
**Where**: [Component/Module]
**Improvement**: [Metric before/after]

**Implementation**:
```typescript
// Caching code
```

**Results**:
- Before: X ms
- After: Y ms
- Improvement: Z%

---

## 🧪 Testing Patterns

### Pattern: Test Structure
**Framework**: Jest/Vitest/Pytest

**Template**:
```typescript
// Test pattern
```

**Coverage Goals**:
- Unit: >80%
- Integration: >70%
- E2E: Critical paths

---

## 🔄 Data Flow Patterns

### Pattern: State Management
**Library**: [Redux/Zustand/Context/etc.]

**Flow**:
1. Action triggered
2. State updated
3. UI reflects change

**Code**:
```typescript
// State management pattern
```

---

## 📚 Naming Conventions

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

## 🔗 Related

**See Also**:
- CLAUDE-decisions.md for why we chose these patterns
- CLAUDE-troubleshooting.md for issues encountered
- CLAUDE-security.md for security-specific patterns

---

**Usage**: Reference when implementing similar functionality.
Add new patterns as they're proven in production.
