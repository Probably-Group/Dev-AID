> **DEV-AID DEFAULT CONTENT** — replace with project-specific rules.
> Until edited, AI assistants should treat this as generic guidance,
> not a binding host-project convention.

# Testing Guidelines

**Purpose**: Testing standards for AI assistants to follow when writing tests
**Used by**: Claude, Gemini, Cursor, and other AI coding assistants
**Update**: When testing strategy changes

---

## Testing Philosophy

1. **Test behavior, not implementation** - Tests should survive refactoring
2. **One assertion per test** (when practical) - Clear failure messages
3. **Arrange-Act-Assert** - Consistent structure
4. **Fast tests** - Unit tests should run in milliseconds

---

## Test Structure

```typescript
describe('ComponentOrFunction', () => {
  // Setup shared across tests
  beforeEach(() => {
    // Reset state, mocks, etc.
  });

  describe('methodName', () => {
    it('should [expected behavior] when [condition]', () => {
      // Arrange - Setup test data
      const input = createTestData();

      // Act - Execute the code
      const result = methodUnderTest(input);

      // Assert - Verify the outcome
      expect(result).toBe(expectedValue);
    });

    it('should throw when [error condition]', () => {
      expect(() => methodUnderTest(invalidInput))
        .toThrow('Expected error message');
    });
  });
});
```

---

## What to Test

### Always Test
- Business logic and calculations
- Edge cases (empty arrays, null values, boundaries)
- Error handling paths
- API response contracts
- Security-sensitive operations

### Don't Test
- Framework code (React, Express, etc.)
- Third-party libraries
- Simple getters/setters
- Implementation details that may change

---

## Test Naming

```typescript
// Pattern: should [expected] when [condition]
it('should return empty array when no users found', () => {});
it('should throw ValidationError when email is invalid', () => {});
it('should call api once when cache is empty', () => {});

// For error cases
it('should reject with NotFoundError when user does not exist', () => {});
```

---

## Mocking

```typescript
// Mock external dependencies
jest.mock('../services/emailService');

// Mock specific implementations
const mockSendEmail = jest.fn().mockResolvedValue({ sent: true });
emailService.send = mockSendEmail;

// Verify mock calls
expect(mockSendEmail).toHaveBeenCalledWith({
  to: 'user@example.com',
  subject: expect.stringContaining('Welcome')
});

// Reset between tests
beforeEach(() => {
  jest.clearAllMocks();
});
```

---

## Test Data

```typescript
// Use factories for consistent test data
function createTestUser(overrides = {}) {
  return {
    id: 'test-user-id',
    name: 'Test User',
    email: 'test@example.com',
    createdAt: new Date('2024-01-01'),
    ...overrides
  };
}

// Usage
const activeUser = createTestUser({ status: 'active' });
const adminUser = createTestUser({ role: 'admin' });
```

---

## Async Testing

```typescript
// Async/await (preferred)
it('should fetch user data', async () => {
  const user = await userService.getById('123');
  expect(user.name).toBe('Test User');
});

// Testing rejections
it('should throw on invalid id', async () => {
  await expect(userService.getById('invalid'))
    .rejects
    .toThrow('User not found');
});

// With timeouts for slow operations
it('should complete within timeout', async () => {
  const result = await slowOperation();
  expect(result).toBeDefined();
}, 10000); // 10 second timeout
```

---

## Integration Tests

```typescript
describe('POST /api/users', () => {
  // Use test database
  beforeAll(async () => {
    await db.connect(process.env.TEST_DATABASE_URL);
  });

  afterAll(async () => {
    await db.disconnect();
  });

  beforeEach(async () => {
    await db.users.deleteMany(); // Clean state
  });

  it('should create user and return 201', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({ name: 'Test', email: 'test@example.com' })
      .expect(201);

    expect(response.body).toMatchObject({
      id: expect.any(String),
      name: 'Test',
      email: 'test@example.com'
    });

    // Verify database state
    const user = await db.users.findByEmail('test@example.com');
    expect(user).toBeDefined();
  });
});
```

---

## Coverage Goals

| Type | Target | Notes |
|------|--------|-------|
| Unit | 80%+ | Business logic must be covered |
| Integration | 70%+ | API endpoints and DB operations |
| E2E | Critical paths | Login, checkout, key user flows |

---

**AI Instructions**: When writing tests:
- Follow the Arrange-Act-Assert pattern
- Write descriptive test names that explain the expected behavior
- Test edge cases and error conditions, not just happy paths
- Don't mock everything - some integration is valuable
- Keep tests fast and independent

<!-- DEV-AID-DEFAULT-UNCHANGED -->
