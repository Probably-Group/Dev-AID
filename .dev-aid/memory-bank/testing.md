# Testing Strategies & Coverage

**Purpose**: Testing approach and coverage tracking (team-shared)
**Note**: For personal AI notes, use Claude's built-in memory (`~/.claude/projects/*/memory/`)

---

## Coverage Goals

| Type | Target | Current | Status |
|------|--------|---------|--------|
| Unit | >80% | --% | -- |
| Integration | >70% | --% | -- |
| E2E | Critical paths | --% | -- |

---

## Test Strategy

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
- Business logic (pure functions)
- API endpoints (contract tests)
- Database queries
- Error handling
- Edge cases

### What NOT to Test
- Implementation details
- Third-party libraries
- Simple getters/setters

---

## Test Patterns

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
  });
});
```

---

## Test Metrics

**Run Frequency**:
- Unit: On every save (watch mode)
- Integration: Pre-commit hook
- E2E: CI/CD pipeline

**Performance Targets**:
- Unit suite: <5 seconds
- Integration suite: <30 seconds
- E2E suite: <3 minutes

---

**Usage**: Reference for test strategies and patterns.
Update coverage weekly.
