# Testing Strategies & Coverage

**Purpose**: Testing approach and coverage tracking
**Load Strategy**: On-demand
**Update Frequency**: Weekly or after test refactoring

---

## 🎯 Coverage Goals

| Type | Target | Current | Status |
|------|--------|---------|--------|
| Unit | >80% | 82% | ✅ Good |
| Integration | >70% | 68% | ⚠️ Close |
| E2E | Critical paths | 85% | ✅ Good |
| Mutation | >70% | 65% | ⚠️ Needs work |

**Last Updated**: 2025-11-25

---

## 🧪 Test Strategy

### Test Pyramid
```
        /\
       /E2E\      5% - Critical user paths
      /------\
     /Integration\ 20% - API contracts, DB integration
    /------------\
   /    Unit      \ 75% - Business logic, utilities
  /----------------\
```

### What to Test
- ✅ Business logic (pure functions)
- ✅ API endpoints (contract tests)
- ✅ Database queries
- ✅ Error handling
- ✅ Edge cases
- ❌ Implementation details
- ❌ Third-party libraries

---

## 📋 Test Patterns

### Unit Test Template
```typescript
describe('calculateTotal', () => {
  it('should sum prices correctly', () => {
    // Arrange
    const items = [{ price: 10 }, { price: 20 }];

    // Act
    const result = calculateTotal(items);

    // Assert
    expect(result).toBe(30);
  });

  it('should handle empty array', () => {
    expect(calculateTotal([])).toBe(0);
  });

  it('should throw on negative prices', () => {
    expect(() => calculateTotal([{ price: -10 }]))
      .toThrow('Price cannot be negative');
  });
});
```

### Integration Test Template
```typescript
describe('POST /api/users', () => {
  beforeEach(async () => {
    await db.users.deleteMany();
  });

  it('should create user and return 201', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({ name: 'Test', email: 'test@example.com' });

    expect(response.status).toBe(201);
    expect(response.body).toHaveProperty('id');

    const user = await db.users.findUnique({
      where: { email: 'test@example.com' }
    });
    expect(user).toBeDefined();
  });
});
```

---

## 🐛 Flaky Tests Tracking

### FLAKY-001: User List E2E Test
**Test**: `e2e/users.spec.ts:45`
**Issue**: Race condition in DB seed
**Frequency**: 15% failure rate
**Fix**: Add await for seed completion
**Status**: Fixed 2025-11-20

---

## 🔄 TDD Workflow

1. **RED**: Write failing test
2. **GREEN**: Write minimal code to pass
3. **REFACTOR**: Improve code quality

**Example**:
```typescript
// 1. RED - Test fails
test('should validate email', () => {
  expect(isValidEmail('invalid')).toBe(false);
});

// 2. GREEN - Make it pass
function isValidEmail(email) {
  return email.includes('@');
}

// 3. REFACTOR - Improve
function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}
```

---

## 📊 Test Metrics

**Run Frequency**:
- Unit: On every save (watch mode)
- Integration: Pre-commit hook
- E2E: CI/CD pipeline
- Load: Weekly scheduled

**Performance**:
- Unit suite: <5 seconds
- Integration suite: <30 seconds
- E2E suite: <3 minutes

---

**Usage**: Reference for test strategies and patterns.
Update coverage weekly.
Track and fix flaky tests immediately.
