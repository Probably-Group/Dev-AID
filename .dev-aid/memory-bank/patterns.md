# Code Patterns & Conventions

**Purpose**: Coding standards for AI assistants to follow when generating code
**Used by**: Claude, Gemini, Cursor, and other AI coding assistants
**Update**: When new patterns are established or conventions change

---

## Naming Conventions

### Files
| Type | Convention | Example |
|------|------------|---------|
| Components | PascalCase | `UserProfile.tsx` |
| Utilities | camelCase | `formatDate.ts` |
| Tests | *.test.ts | `userService.test.ts` |
| Types | PascalCase | `UserTypes.ts` |
| Constants | SCREAMING_SNAKE | `API_ENDPOINTS.ts` |

### Code
| Type | Convention | Example |
|------|------------|---------|
| Variables | camelCase | `userName` |
| Constants | SCREAMING_SNAKE | `MAX_RETRIES` |
| Functions | camelCase | `getUserById` |
| Classes | PascalCase | `UserService` |
| Interfaces | PascalCase with I prefix (optional) | `IUserData` or `UserData` |
| Boolean | is/has/can prefix | `isActive`, `hasPermission` |
| Handlers | handle/on prefix | `handleSubmit`, `onClick` |

---

## File Organization

```
src/
├── components/     # UI components (one component per file)
├── services/       # Business logic and API calls
├── hooks/          # Custom React hooks
├── utils/          # Pure utility functions
├── types/          # TypeScript type definitions
├── constants/      # Application constants
└── config/         # Configuration files
```

---

## Code Style

### Functions
```typescript
// Prefer arrow functions for callbacks
const items = data.map((item) => item.name);

// Use named functions for top-level declarations
function processUserData(user: User): ProcessedUser {
  // ...
}

// Always type parameters and return values
function calculateTotal(items: Item[]): number {
  return items.reduce((sum, item) => sum + item.price, 0);
}
```

### Error Handling
```typescript
// Always handle errors explicitly
try {
  const result = await fetchData();
  return result;
} catch (error) {
  logger.error('Failed to fetch data', { error });
  throw new AppError('DATA_FETCH_FAILED', 'Unable to retrieve data');
}

// Use custom error classes
class AppError extends Error {
  constructor(public code: string, message: string) {
    super(message);
  }
}
```

### Async/Await
```typescript
// Prefer async/await over .then()
// Good
const data = await fetchUser(id);

// Avoid
fetchUser(id).then(data => { ... });

// Use Promise.all for parallel operations
const [users, posts] = await Promise.all([
  fetchUsers(),
  fetchPosts()
]);
```

---

## Component Patterns

### React Components
```typescript
// Functional components with TypeScript
interface UserCardProps {
  user: User;
  onEdit?: (id: string) => void;
}

export function UserCard({ user, onEdit }: UserCardProps) {
  return (
    <div className="user-card">
      <h3>{user.name}</h3>
      {onEdit && <button onClick={() => onEdit(user.id)}>Edit</button>}
    </div>
  );
}
```

### Hooks
```typescript
// Custom hooks start with 'use'
function useUserData(userId: string) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    fetchUser(userId)
      .then(setUser)
      .catch(setError)
      .finally(() => setLoading(false));
  }, [userId]);

  return { user, loading, error };
}
```

---

## Testing Patterns

### Test Structure
```typescript
describe('UserService', () => {
  describe('getUserById', () => {
    it('should return user when found', async () => {
      // Arrange
      const userId = '123';
      const expectedUser = { id: userId, name: 'Test' };

      // Act
      const result = await userService.getUserById(userId);

      // Assert
      expect(result).toEqual(expectedUser);
    });

    it('should throw when user not found', async () => {
      await expect(userService.getUserById('invalid'))
        .rejects.toThrow('User not found');
    });
  });
});
```

---

## Anti-Patterns to Avoid

### Don't Do This
```typescript
// ❌ Magic numbers
if (status === 1) { ... }

// ✅ Use constants
if (status === UserStatus.ACTIVE) { ... }

// ❌ Nested callbacks
getData(id, (data) => {
  process(data, (result) => {
    save(result, (saved) => { ... });
  });
});

// ✅ Use async/await
const data = await getData(id);
const result = await process(data);
await save(result);

// ❌ Any type
function process(data: any) { ... }

// ✅ Proper typing
function process(data: UserData) { ... }
```

---

## Comments

```typescript
// Use comments to explain WHY, not WHAT
// ❌ Bad: Increment counter
counter++;

// ✅ Good: Compensate for zero-based index in display
counter++;

// Use JSDoc for public APIs
/**
 * Fetches user by ID with caching.
 * @param id - The user's unique identifier
 * @returns The user object or null if not found
 * @throws {NetworkError} When the API is unreachable
 */
async function getUser(id: string): Promise<User | null> {
  // ...
}
```

---

**AI Instructions**: When generating code for this project, follow these patterns.
If unsure about a convention, ask rather than guess.
