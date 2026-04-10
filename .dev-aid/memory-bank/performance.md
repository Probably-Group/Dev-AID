> **DEV-AID DEFAULT CONTENT** — replace with project-specific rules.
> Until edited, AI assistants should treat this as generic guidance,
> not a binding host-project convention.

# Performance Guidelines

**Purpose**: Performance best practices for AI assistants when generating code
**Used by**: Claude, Gemini, Cursor, and other AI coding assistants
**Update**: When performance patterns change or issues are discovered

---

## Performance Rules for AI

When generating code, prioritize:
1. **Correctness first** - Don't sacrifice correctness for speed
2. **Readability second** - Maintainable code is optimizable code
3. **Performance third** - Optimize when there's a proven need

---

## Database Queries

### Avoid N+1 Queries
```typescript
// ❌ N+1 problem - makes 101 queries for 100 users
const users = await db.users.findMany();
for (const user of users) {
  user.posts = await db.posts.findMany({ where: { userId: user.id } });
}

// ✅ Single query with join - 1 query total
const users = await db.users.findMany({
  include: { posts: true }
});
```

### Use Indexes
```sql
-- Add indexes for frequently queried columns
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_posts_user_created ON posts(user_id, created_at);
```

### Paginate Large Results
```typescript
// ✅ Always paginate list endpoints
const users = await db.users.findMany({
  skip: (page - 1) * pageSize,
  take: pageSize,
  orderBy: { createdAt: 'desc' }
});
```

---

## Caching Patterns

### When to Cache
- Expensive calculations
- Frequently accessed, rarely changed data
- External API responses

### Cache Implementation
```typescript
// Simple in-memory cache with TTL
async function getCachedUser(userId: string): Promise<User> {
  const cacheKey = `user:${userId}`;

  // Try cache first
  const cached = await redis.get(cacheKey);
  if (cached) {
    return JSON.parse(cached);
  }

  // Fetch from database
  const user = await db.users.findUnique({ where: { id: userId } });

  // Cache for 1 hour
  await redis.setex(cacheKey, 3600, JSON.stringify(user));

  return user;
}
```

### Cache Invalidation
```typescript
// Invalidate on update
async function updateUser(userId: string, data: UpdateData) {
  const user = await db.users.update({ where: { id: userId }, data });
  await redis.del(`user:${userId}`); // Invalidate cache
  return user;
}
```

---

## Frontend Performance

### Code Splitting
```typescript
// ✅ Lazy load routes
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Settings = lazy(() => import('./pages/Settings'));

// With suspense
<Suspense fallback={<Loading />}>
  <Dashboard />
</Suspense>
```

### Memoization
```typescript
// ✅ Memoize expensive calculations
const expensiveResult = useMemo(() => {
  return computeExpensiveValue(data);
}, [data]);

// ✅ Memoize callbacks passed to children
const handleClick = useCallback((id: string) => {
  doSomething(id);
}, [doSomething]);
```

### Avoid Re-renders
```typescript
// ❌ Creates new object every render
<Component style={{ color: 'red' }} />

// ✅ Define outside or memoize
const style = { color: 'red' };
<Component style={style} />
```

---

## API Performance

### Parallel Requests
```typescript
// ❌ Sequential - slow
const users = await fetchUsers();
const posts = await fetchPosts();
const comments = await fetchComments();

// ✅ Parallel - fast
const [users, posts, comments] = await Promise.all([
  fetchUsers(),
  fetchPosts(),
  fetchComments()
]);
```

### Response Compression
```typescript
// Enable gzip compression
import compression from 'compression';
app.use(compression());
```

### Selective Fields
```typescript
// ✅ Only fetch needed fields
const users = await db.users.findMany({
  select: {
    id: true,
    name: true,
    email: true
    // Don't select large fields like 'bio' if not needed
  }
});
```

---

## Memory Management

### Avoid Memory Leaks
```typescript
// ✅ Clean up subscriptions
useEffect(() => {
  const subscription = eventEmitter.subscribe(handler);
  return () => subscription.unsubscribe(); // Cleanup
}, []);

// ✅ Clean up timers
useEffect(() => {
  const timer = setInterval(tick, 1000);
  return () => clearInterval(timer); // Cleanup
}, []);
```

### Stream Large Data
```typescript
// ❌ Load entire file into memory
const data = fs.readFileSync('large-file.json');

// ✅ Stream for large files
const stream = fs.createReadStream('large-file.json');
stream.pipe(responseStream);
```

---

## Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| API P95 | <100ms | Most endpoints |
| API P95 | <500ms | Complex queries |
| LCP | <2.5s | Largest Contentful Paint |
| FID | <100ms | First Input Delay |
| Bundle size | <200KB | Initial JS bundle |

---

**AI Instructions**: When generating code:
- Use efficient patterns by default (joins, pagination, etc.)
- Don't over-optimize prematurely
- If suggesting an optimization, explain the trade-off
- Flag potential performance issues when you see them

<!-- DEV-AID-DEFAULT-UNCHANGED -->
