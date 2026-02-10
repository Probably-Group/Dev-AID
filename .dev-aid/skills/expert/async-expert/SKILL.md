---
name: async-expert
version: 2.0.0
description: "Cross-language async and concurrency patterns for Python asyncio/TaskGroup, TypeScript promises/async-await, and Rust Tokio with proper error handling and cancellation. Use when designing concurrent architectures, debugging race conditions, implementing task pools, or choosing between async patterns across languages. Do NOT use for synchronous-only code without concurrency needs or simple sequential scripts."
risk_level: MEDIUM
---

# Async Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-362: Race Conditions**
- NEVER: Shared mutable state without synchronization
- ALWAYS: Locks, atomic operations, or message passing

**CWE-400: Unbounded Concurrency**
- NEVER: Spawn unlimited tasks from user requests
- ALWAYS: Semaphores, task pools, bounded queues

**CWE-404: Resource Leaks**
- NEVER: Skip cleanup on cancellation
- ALWAYS: Context managers, finally blocks, cancellation-safe code

### 0.3 Risk Level: MEDIUM

**Verification requirements for MEDIUM risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 Race Condition Prevention (CWE-362)

**Principle:** Protect shared state. Use locks, atomics, or message passing.

```python
# ❌ WRONG - Race condition
counter = 0
async def increment():
    global counter
    temp = counter  # Read
    await asyncio.sleep(0.001)  # Context switch!
    counter = temp + 1  # Write stale value

# ✅ CORRECT - Use lock
import asyncio

lock = asyncio.Lock()
counter = 0

async def increment():
    global counter
    async with lock:
        counter += 1
```

### 1.2 Resource Cleanup (CWE-404)

**Principle:** Always close resources in finally. Use context managers.

```python
# ❌ WRONG - Resource leak on exception
async def fetch():
    session = aiohttp.ClientSession()
    response = await session.get(url)  # If this raises...
    await session.close()  # ...this never runs!

# ✅ CORRECT - Context manager ensures cleanup
async def fetch():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()
```

### 1.3 Timeout Protection (CWE-400)

**Principle:** All async operations need timeouts. Never wait forever.

```python
# ❌ WRONG - No timeout
await fetch(url)  # Could hang forever

# ✅ CORRECT - Always timeout
async with asyncio.timeout(30):
    await fetch(url)
```

### 1.4 Secrets ≠ Code (CWE-798)

**Principle:** Don't log async stack traces with sensitive data.

### 1.5 Fail Secure (CWE-636)

**Principle:** On cancellation, clean up resources. Don't leave partial state.

### 1.6 Defense in Depth

**Principle:** Timeout + retry + circuit breaker for external calls.

---

## 2. Version Requirements

**ALWAYS use these minimum versions:**

```
# Python
asyncio (stdlib)
aiohttp>=3.9.0
anyio>=4.2.0

# Node.js (built-in Promises)
node>=20.0.0

# Rust
tokio = "1.35"
async-trait = "0.1"
```

---

## 3. Code Patterns

### 3.1 WHEN using Python TaskGroup (Python 3.11+)

```python
# ❌ WRONG - fire-and-forget tasks, no error handling
async def main():
    asyncio.create_task(do_work())  # Task may be garbage collected!
    await asyncio.sleep(1)

# ✅ CORRECT - Structured concurrency with TaskGroup
import asyncio

async def main():
    async with asyncio.TaskGroup() as tg:
        # All tasks managed, exceptions propagated
        tg.create_task(fetch_user(1))
        tg.create_task(fetch_user(2))
        tg.create_task(fetch_user(3))
    # All tasks complete here, or exception raised

# With timeout and cancellation handling
async def fetch_with_timeout(url: str, timeout: float = 30.0) -> str:
    try:
        async with asyncio.timeout(timeout):
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    return await response.text()
    except asyncio.TimeoutError:
        raise TimeoutError(f"Request to {url} timed out after {timeout}s")
    except asyncio.CancelledError:
        # Clean up and re-raise
        raise
    except aiohttp.ClientError as e:
        raise ConnectionError(f"Failed to fetch {url}: {e}")
```

### 3.2 WHEN implementing async context managers

```python
# ❌ WRONG - No cleanup on error
class DatabasePool:
    async def connect(self):
        self.pool = await create_pool()

    async def close(self):
        await self.pool.close()

# ✅ CORRECT - Async context manager with proper cleanup
from contextlib import asynccontextmanager
from typing import AsyncGenerator

class DatabasePool:
    def __init__(self, dsn: str, min_size: int = 5, max_size: int = 20):
        self.dsn = dsn
        self.min_size = min_size
        self.max_size = max_size
        self._pool: asyncpg.Pool | None = None

    async def __aenter__(self) -> "DatabasePool":
        self._pool = await asyncpg.create_pool(
            self.dsn,
            min_size=self.min_size,
            max_size=self.max_size,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        if self._pool:
            await self._pool.close()
        return False  # Don't suppress exceptions

    @asynccontextmanager
    async def acquire(self) -> AsyncGenerator[asyncpg.Connection, None]:
        if not self._pool:
            raise RuntimeError("Pool not initialized")

        async with self._pool.acquire() as conn:
            try:
                yield conn
            except Exception:
                raise

# Usage
async def main():
    async with DatabasePool("postgresql://localhost/db") as pool:
        async with pool.acquire() as conn:
            result = await conn.fetch("SELECT * FROM users")
```

### 3.3 WHEN implementing concurrent tasks (Python)

```python
import asyncio
from typing import TypeVar, Sequence
from dataclasses import dataclass

T = TypeVar('T')

@dataclass
class TaskResult[T]:
    value: T | None
    error: Exception | None
    success: bool

async def gather_with_errors(
    *coros,
    timeout: float = 30.0
) -> list[TaskResult]:
    """Run tasks concurrently, capturing errors."""
    results = []

    async def wrap(coro):
        try:
            async with asyncio.timeout(timeout):
                value = await coro
                return TaskResult(value=value, error=None, success=True)
        except Exception as e:
            return TaskResult(value=None, error=e, success=False)

    tasks = [asyncio.create_task(wrap(c)) for c in coros]
    results = await asyncio.gather(*tasks)
    return results

# Usage
async def main():
    results = await gather_with_errors(
        fetch_user(1),
        fetch_user(2),
        fetch_user(3),
        timeout=10.0
    )

    for result in results:
        if result.success:
            print(f"Got: {result.value}")
        else:
            print(f"Error: {result.error}")
```

### 3.2 WHEN implementing rate-limited concurrency (Python)

```python
import asyncio
from typing import Callable, TypeVar, Awaitable

T = TypeVar('T')

class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(self, rate: float, burst: int = 1):
        self.rate = rate  # Requests per second
        self.burst = burst
        self.tokens = burst
        self.last_update = asyncio.get_event_loop().time()
        self.lock = asyncio.Lock()

    async def acquire(self):
        async with self.lock:
            now = asyncio.get_event_loop().time()
            elapsed = now - self.last_update
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
            self.last_update = now

            if self.tokens < 1:
                wait_time = (1 - self.tokens) / self.rate
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1

async def concurrent_map(
    func: Callable[[T], Awaitable],
    items: list[T],
    concurrency: int = 10,
    rate_limit: float | None = None,
) -> list:
    """Map function over items with bounded concurrency."""
    semaphore = asyncio.Semaphore(concurrency)
    rate_limiter = RateLimiter(rate_limit) if rate_limit else None

    async def limited_func(item):
        if rate_limiter:
            await rate_limiter.acquire()
        async with semaphore:
            return await func(item)

    return await asyncio.gather(*[limited_func(item) for item in items])

# Usage
async def fetch_all_users(user_ids: list[int]) -> list[User]:
    return await concurrent_map(
        fetch_user,
        user_ids,
        concurrency=5,
        rate_limit=10.0  # 10 requests/second
    )
```

### 3.3 WHEN implementing retry with exponential backoff (Python)

```python
import asyncio
import random
from functools import wraps
from typing import TypeVar, Callable, Awaitable

T = TypeVar('T')

class RetryError(Exception):
    def __init__(self, message: str, last_error: Exception):
        super().__init__(message)
        self.last_error = last_error

def retry(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: tuple = (Exception,),
):
    """Retry decorator with exponential backoff."""

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_error: Exception | None = None
            delay = initial_delay

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_error = e

                    if attempt == max_retries:
                        break

                    # Add jitter
                    if jitter:
                        delay *= (0.5 + random.random())

                    await asyncio.sleep(min(delay, max_delay))
                    delay *= exponential_base

            raise RetryError(
                f"Failed after {max_retries + 1} attempts",
                last_error
            )

        return wrapper
    return decorator

# Usage
@retry(max_retries=3, retryable_exceptions=(ConnectionError, TimeoutError))
async def fetch_with_retry(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with asyncio.timeout(10):
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.text()
```

### 3.4 WHEN implementing async in TypeScript

```typescript
// Rate-limited concurrent execution
async function concurrentMap<T, R>(
  items: T[],
  fn: (item: T) => Promise<R>,
  options: { concurrency?: number; rateLimit?: number } = {}
): Promise<R[]> {
  const { concurrency = 10, rateLimit } = options;
  const results: R[] = new Array(items.length);
  let index = 0;
  let lastCall = 0;

  async function worker(): Promise<void> {
    while (index < items.length) {
      const currentIndex = index++;

      // Rate limiting
      if (rateLimit) {
        const now = Date.now();
        const minDelay = 1000 / rateLimit;
        const elapsed = now - lastCall;
        if (elapsed < minDelay) {
          await new Promise(r => setTimeout(r, minDelay - elapsed));
        }
        lastCall = Date.now();
      }

      results[currentIndex] = await fn(items[currentIndex]);
    }
  }

  // Start workers
  const workers = Array(Math.min(concurrency, items.length))
    .fill(null)
    .map(() => worker());

  await Promise.all(workers);
  return results;
}

// Retry with exponential backoff
async function withRetry<T>(
  fn: () => Promise<T>,
  options: {
    maxRetries?: number;
    initialDelay?: number;
    maxDelay?: number;
  } = {}
): Promise<T> {
  const { maxRetries = 3, initialDelay = 1000, maxDelay = 30000 } = options;
  let lastError: Error | null = null;
  let delay = initialDelay;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      if (attempt === maxRetries) break;

      // Exponential backoff with jitter
      await new Promise(r =>
        setTimeout(r, Math.min(delay * (0.5 + Math.random()), maxDelay))
      );
      delay *= 2;
    }
  }

  throw lastError;
}

// Usage
const users = await concurrentMap(
  userIds,
  async (id) => withRetry(() => fetchUser(id)),
  { concurrency: 5, rateLimit: 10 }
);
```

### 3.5 WHEN implementing async in Rust

```rust
use tokio::sync::Semaphore;
use std::sync::Arc;
use std::time::Duration;
use futures::future::join_all;

/// Run futures with bounded concurrency
pub async fn concurrent_map<T, F, Fut, R>(
    items: Vec<T>,
    concurrency: usize,
    f: F,
) -> Vec<Result<R, anyhow::Error>>
where
    T: Send + 'static,
    F: Fn(T) -> Fut + Send + Sync + 'static,
    Fut: std::future::Future<Output = Result<R, anyhow::Error>> + Send,
    R: Send + 'static,
{
    let semaphore = Arc::new(Semaphore::new(concurrency));
    let f = Arc::new(f);

    let tasks: Vec<_> = items
        .into_iter()
        .map(|item| {
            let semaphore = Arc::clone(&semaphore);
            let f = Arc::clone(&f);

            tokio::spawn(async move {
                let _permit = semaphore.acquire().await.unwrap();
                f(item).await
            })
        })
        .collect();

    let results = join_all(tasks).await;
    results
        .into_iter()
        .map(|r| r.unwrap_or_else(|e| Err(e.into())))
        .collect()
}

/// Retry with exponential backoff
pub async fn with_retry<F, Fut, T>(
    f: F,
    max_retries: u32,
    initial_delay: Duration,
) -> Result<T, anyhow::Error>
where
    F: Fn() -> Fut,
    Fut: std::future::Future<Output = Result<T, anyhow::Error>>,
{
    let mut delay = initial_delay;

    for attempt in 0..=max_retries {
        match f().await {
            Ok(value) => return Ok(value),
            Err(e) => {
                if attempt == max_retries {
                    return Err(e);
                }

                // Exponential backoff with jitter
                let jitter = rand::random::<f64>() * 0.5 + 0.5;
                let sleep_time = delay.mul_f64(jitter);
                tokio::time::sleep(sleep_time).await;
                delay *= 2;
            }
        }
    }

    unreachable!()
}

/// Timeout wrapper
pub async fn with_timeout<F, T>(
    f: F,
    timeout: Duration,
) -> Result<T, anyhow::Error>
where
    F: std::future::Future<Output = Result<T, anyhow::Error>>,
{
    tokio::time::timeout(timeout, f)
        .await
        .map_err(|_| anyhow::anyhow!("Operation timed out"))?
}

// Usage
async fn fetch_all_users(ids: Vec<i64>) -> Vec<Result<User, anyhow::Error>> {
    concurrent_map(ids, 10, |id| async move {
        with_timeout(
            with_retry(
                || fetch_user(id),
                3,
                Duration::from_secs(1),
            ),
            Duration::from_secs(30),
        ).await
    }).await
}
```

### 3.6 WHEN implementing graceful shutdown

```python
import asyncio
import signal
from typing import Set

class GracefulShutdown:
    """Handle graceful shutdown with task cleanup."""

    def __init__(self):
        self.shutdown_event = asyncio.Event()
        self.tasks: Set[asyncio.Task] = set()

    def setup_signals(self):
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(
                sig,
                lambda: asyncio.create_task(self.shutdown())
            )

    async def shutdown(self):
        self.shutdown_event.set()

        # Cancel all tracked tasks
        for task in self.tasks:
            task.cancel()

        # Wait for cancellation
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)

    def track_task(self, coro) -> asyncio.Task:
        task = asyncio.create_task(coro)
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)
        return task

    async def wait_for_shutdown(self):
        await self.shutdown_event.wait()

# Usage
async def main():
    shutdown = GracefulShutdown()
    shutdown.setup_signals()

    # Start background tasks
    shutdown.track_task(background_worker())
    shutdown.track_task(health_check_server())

    # Wait for shutdown signal
    await shutdown.wait_for_shutdown()
    print("Shutting down gracefully...")
```

### 3.9 WHEN implementing async worker pools

```python
# ❌ WRONG - No backpressure, unbounded queue
queue = asyncio.Queue()
async def producer():
    while True:
        await queue.put(generate_item())  # Memory exhaustion!

# ✅ CORRECT - Bounded queue with backpressure
from asyncio import Queue
from typing import Generic, TypeVar, Callable, Awaitable

T = TypeVar('T')

class AsyncWorkerPool(Generic[T]):
    def __init__(
        self,
        worker_fn: Callable[[T], Awaitable[None]],
        num_workers: int = 5,
        max_queue_size: int = 100,
    ):
        self.worker_fn = worker_fn
        self.num_workers = num_workers
        self.queue: Queue[T | None] = Queue(maxsize=max_queue_size)
        self._workers: list[asyncio.Task] = []
        self._running = False

    async def start(self) -> None:
        if self._running:
            raise RuntimeError("Pool already running")

        self._running = True
        self._workers = [
            asyncio.create_task(self._worker(i))
            for i in range(self.num_workers)
        ]

    async def stop(self, timeout: float = 30.0) -> None:
        if not self._running:
            return

        self._running = False

        # Signal workers to stop
        for _ in self._workers:
            await self.queue.put(None)

        # Wait for workers with timeout
        try:
            async with asyncio.timeout(timeout):
                await asyncio.gather(*self._workers, return_exceptions=True)
        except asyncio.TimeoutError:
            for worker in self._workers:
                worker.cancel()

    async def submit(self, item: T) -> None:
        if not self._running:
            raise RuntimeError("Pool not running")
        await self.queue.put(item)

    async def _worker(self, worker_id: int) -> None:
        while self._running:
            try:
                item = await self.queue.get()

                if item is None:  # Shutdown signal
                    break

                try:
                    await self.worker_fn(item)
                except Exception as e:
                    print(f"Worker {worker_id} error: {e}")
                finally:
                    self.queue.task_done()

            except asyncio.CancelledError:
                break

# Usage
async def process_item(item: dict) -> None:
    await asyncio.sleep(0.1)
    print(f"Processed: {item}")

async def main():
    pool = AsyncWorkerPool(process_item, num_workers=5, max_queue_size=50)
    await pool.start()

    try:
        for i in range(100):
            await pool.submit({"id": i})
        await pool.queue.join()
    finally:
        await pool.stop()
```

---

## 4. Anti-Patterns

**NEVER:**
- Use `asyncio.create_task()` without tracking the task
- Access shared state without synchronization
- Forget to await async functions
- Use blocking I/O in async code
- Skip timeouts on external calls
- Ignore task cancellation
- Create unbounded task queues
- Mix sync and async without proper bridging

---

## 5. Testing

**ALWAYS write async tests:**

```python
import pytest
import asyncio

@pytest.fixture
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.mark.asyncio
async def test_concurrent_map():
    results = []

    async def slow_task(x):
        await asyncio.sleep(0.1)
        return x * 2

    items = [1, 2, 3, 4, 5]
    results = await concurrent_map(slow_task, items, concurrency=2)

    assert results == [2, 4, 6, 8, 10]

@pytest.mark.asyncio
async def test_retry_succeeds_after_failures():
    attempts = 0

    @retry(max_retries=3)
    async def flaky_function():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ConnectionError("Failed")
        return "success"

    result = await flaky_function()

    assert result == "success"
    assert attempts == 3

@pytest.mark.asyncio
async def test_timeout_raises():
    async def slow_function():
        await asyncio.sleep(10)

    with pytest.raises(asyncio.TimeoutError):
        async with asyncio.timeout(0.1):
            await slow_function()

@pytest.mark.asyncio
async def test_race_condition_prevented():
    counter = 0
    lock = asyncio.Lock()

    async def increment():
        nonlocal counter
        async with lock:
            temp = counter
            await asyncio.sleep(0.001)
            counter = temp + 1

    await asyncio.gather(*[increment() for _ in range(100)])

    assert counter == 100  # Without lock, would be < 100
```

---

## 6. Pre-Generation Checklist

**BEFORE generating any async code:**

- [ ] Shared state protected (locks, atomics, channels)
- [ ] All async operations have timeouts
- [ ] Resources cleaned up in finally/context managers
- [ ] Cancellation handled gracefully
- [ ] Retry logic for transient failures
- [ ] Bounded concurrency (semaphores)
- [ ] No blocking calls in async context
- [ ] Graceful shutdown implemented
- [ ] Race conditions considered
- [ ] Error handling doesn't swallow exceptions

---

**Performance**: Quality over speed. Verify all code examples compile. Never skip security checks. See `template-references/performance-notes.md` for full guidelines.