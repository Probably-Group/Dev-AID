> **DEV-AID DEFAULT CONTENT** — replace with project-specific rules.
> Until edited, AI assistants should treat this as generic guidance,
> not a binding host-project convention.

# Resilience & Error Handling

**Purpose**: Error handling and resilience patterns for AI assistants
**Used by**: Claude, Gemini, Cursor, and other AI coding assistants
**Update**: After incidents or when resilience patterns change

---

## Error Handling Philosophy

1. **Fail fast** - Detect errors early, don't propagate bad state
2. **Fail gracefully** - Provide useful error messages
3. **Fail safely** - Don't expose sensitive info in errors

---

## Error Handling Patterns

### Custom Error Classes
```typescript
// Define domain-specific errors
class AppError extends Error {
  constructor(
    public code: string,
    message: string,
    public statusCode: number = 500
  ) {
    super(message);
    this.name = 'AppError';
  }
}

class NotFoundError extends AppError {
  constructor(resource: string, id: string) {
    super('NOT_FOUND', `${resource} with id ${id} not found`, 404);
  }
}

class ValidationError extends AppError {
  constructor(message: string) {
    super('VALIDATION_ERROR', message, 400);
  }
}
```

### Error Handler Middleware
```typescript
// Express error handler
function errorHandler(err: Error, req: Request, res: Response, next: NextFunction) {
  // Log full error internally
  logger.error('Request failed', {
    error: err,
    path: req.path,
    method: req.method
  });

  // Return safe error to client
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({
      error: err.code,
      message: err.message
    });
  }

  // Don't leak internal errors
  return res.status(500).json({
    error: 'INTERNAL_ERROR',
    message: 'An unexpected error occurred'
  });
}
```

---

## Resilience Patterns

### Circuit Breaker
```typescript
// Prevent cascading failures
class CircuitBreaker {
  private failures = 0;
  private lastFailure: Date | null = null;
  private state: 'closed' | 'open' | 'half-open' = 'closed';

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    if (this.state === 'open') {
      if (this.shouldAttemptReset()) {
        this.state = 'half-open';
      } else {
        throw new Error('Circuit breaker is open');
      }
    }

    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }
}
```

### Retry with Backoff
```typescript
async function withRetry<T>(
  fn: () => Promise<T>,
  options: { attempts: number; delay: number; factor: number }
): Promise<T> {
  let lastError: Error;

  for (let i = 0; i < options.attempts; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;
      if (i < options.attempts - 1) {
        const delay = options.delay * Math.pow(options.factor, i);
        await sleep(delay);
      }
    }
  }

  throw lastError!;
}

// Usage
const result = await withRetry(
  () => fetchExternalApi(),
  { attempts: 3, delay: 1000, factor: 2 }
);
```

### Timeouts
```typescript
// Always set timeouts for external calls
async function fetchWithTimeout(url: string, timeout = 5000): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    return await fetch(url, { signal: controller.signal });
  } finally {
    clearTimeout(timeoutId);
  }
}
```

---

## Graceful Degradation

```typescript
// Provide fallbacks when services fail
async function getUserProfile(userId: string): Promise<UserProfile> {
  try {
    // Try to get full profile
    return await profileService.getFullProfile(userId);
  } catch (error) {
    logger.warn('Profile service unavailable, using cached data', { userId });

    // Fall back to cached/basic data
    const cachedProfile = await cache.get(`profile:${userId}`);
    if (cachedProfile) {
      return { ...cachedProfile, _degraded: true };
    }

    // Minimum viable response
    const user = await db.users.findUnique({ where: { id: userId } });
    return {
      id: user.id,
      name: user.name,
      _degraded: true
    };
  }
}
```

---

## Health Checks

```typescript
// Implement health endpoints
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

app.get('/health/ready', async (req, res) => {
  const checks = await Promise.allSettled([
    checkDatabase(),
    checkCache(),
    checkExternalApi()
  ]);

  const status = checks.every(c => c.status === 'fulfilled') ? 'ok' : 'degraded';
  const statusCode = status === 'ok' ? 200 : 503;

  res.status(statusCode).json({
    status,
    checks: {
      database: checks[0].status === 'fulfilled',
      cache: checks[1].status === 'fulfilled',
      externalApi: checks[2].status === 'fulfilled'
    }
  });
});
```

---

## Logging Best Practices

```typescript
// Structured logging
logger.info('User action completed', {
  userId: user.id,
  action: 'purchase',
  amount: order.total,
  duration: Date.now() - startTime
});

// Error logging with context
logger.error('Payment failed', {
  error: error.message,
  stack: error.stack,
  userId: user.id,
  orderId: order.id,
  // Don't log sensitive data like card numbers
});
```

---

**AI Instructions**: When generating code:
- Always include error handling
- Use appropriate error types (don't catch generic Error when specific types exist)
- Include timeouts for external calls
- Add logging for debugging but never log sensitive data
- Consider what happens when dependencies fail

<!-- DEV-AID-DEFAULT-UNCHANGED -->
