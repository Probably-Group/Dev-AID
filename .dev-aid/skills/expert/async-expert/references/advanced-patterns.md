# Advanced Async Patterns

This document contains advanced async programming patterns for experienced developers.

---

## Pattern 1: Parallel Execution with Error Handling

**Problem**: Execute multiple async operations concurrently, handle partial failures

**Python**:
```python
from typing import List, Tuple
import asyncio

async def fetch_users_parallel(user_ids: List[int]) -> Tuple[List[dict], List[Exception]]:
    """Fetch multiple users concurrently, separating successes from failures."""
    tasks = [fetch_user(uid) for uid in user_ids]

    # gather with return_exceptions=True prevents one failure from canceling others
    results = await asyncio.gather(*tasks, return_exceptions=True)

    successes = [r for r in results if not isinstance(r, Exception)]
    failures = [r for r in results if isinstance(r, Exception)]

    return successes, failures
```

**JavaScript**:
```javascript
async function fetchUsersParallel(userIds) {
  const results = await Promise.allSettled(
    userIds.map(id => fetchUser(id))
  );

  const successes = results
    .filter(r => r.status === 'fulfilled')
    .map(r => r.value);

  const failures = results
    .filter(r => r.status === 'rejected')
    .map(r => r.reason);

  return { successes, failures };
}
```

**Key Points**:
- `asyncio.gather(..., return_exceptions=True)` collects both results and exceptions
- `Promise.allSettled()` waits for all promises regardless of success/failure
- Allows graceful handling of partial failures
- Useful for bulk operations where some failures are acceptable

---

## Pattern 2: Timeout and Cancellation

**Problem**: Prevent async operations from running indefinitely

**Python**:
```python
from typing import Optional
import asyncio

async def fetch_with_timeout(url: str, timeout: float = 5.0) -> Optional[str]:
    """Fetch with timeout, return None instead of raising."""
    try:
        async with asyncio.timeout(timeout):  # Python 3.11+
            return await fetch_data(url)
    except asyncio.TimeoutError:
        return None

async def cancellable_task():
    """Handle cancellation gracefully with cleanup."""
    try:
        await long_running_operation()
    except asyncio.CancelledError:
        # Perform cleanup before re-raising
        await cleanup()
        raise  # Re-raise to signal cancellation
```

**Python 3.10 and earlier**:
```python
async def fetch_with_timeout_legacy(url: str, timeout: float = 5.0) -> Optional[str]:
    try:
        return await asyncio.wait_for(fetch_data(url), timeout=timeout)
    except asyncio.TimeoutError:
        return None
```

**JavaScript**:
```javascript
async function fetchWithTimeout(url, timeoutMs = 5000) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, { signal: controller.signal });
    clearTimeout(timeoutId);
    return await response.json();
  } catch (error) {
    if (error.name === 'AbortError') {
      return null; // Timeout occurred
    }
    throw error; // Re-throw other errors
  }
}
```

**Key Points**:
- Always set timeouts for network operations
- Use `asyncio.timeout()` (3.11+) or `asyncio.wait_for()` (older)
- JavaScript: Use `AbortController` for cancellation
- Always re-raise `CancelledError` after cleanup

---

## Pattern 3: Retry with Exponential Backoff

**Problem**: Retry failed async operations with increasing delays

**Python**:
```python
import asyncio
import random
from typing import Callable, Any

async def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    exponential_base: float = 2.0,
    jitter: bool = True
) -> Any:
    """Retry with exponential backoff and optional jitter."""
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise  # Final attempt failed, propagate error

            # Calculate delay: base * exponential^attempt, capped at 60s
            delay = min(base_delay * (exponential_base ** attempt), 60.0)

            # Add jitter to prevent thundering herd
            if jitter:
                delay *= (0.5 + random.random())

            print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s...")
            await asyncio.sleep(delay)
```

**JavaScript**:
```javascript
async function retryWithBackoff(
  fn,
  { maxRetries = 3, baseDelay = 1000 } = {}
) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      if (attempt === maxRetries - 1) {
        throw error; // Final attempt failed
      }

      // Calculate delay with exponential backoff, capped at 60s
      const delay = Math.min(
        baseDelay * Math.pow(2, attempt),
        60000
      );

      console.log(`Attempt ${attempt + 1} failed. Retrying in ${delay}ms...`);
      await new Promise(r => setTimeout(r, delay));
    }
  }
}
```

**Usage Example**:
```python
# Python
async def unreliable_api_call():
    response = await fetch_data("https://api.example.com/data")
    return response

result = await retry_with_backoff(
    unreliable_api_call,
    max_retries=5,
    base_delay=1.0
)
```

**Key Points**:
- Start with small delay, increase exponentially
- Add jitter to prevent synchronized retries
- Cap maximum delay to reasonable value (60s)
- Only retry on transient errors (network, 5xx), not client errors (4xx)

---

## Pattern 4: Async Context Manager / Resource Cleanup

**Problem**: Ensure resources are properly cleaned up even on errors

**Python**:
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_db_connection(dsn: str):
    """Async context manager for database connections."""
    conn = DatabaseConnection(dsn)
    try:
        await conn.connect()
        yield conn
    finally:
        if conn.connected:
            await conn.close()

# Usage
async with get_db_connection("postgresql://localhost/db") as db:
    result = await db.execute("SELECT * FROM users")
    # Connection automatically closed, even on errors
```

**Class-based async context manager**:
```python
class DatabasePool:
    def __init__(self, dsn: str, min_size: int = 5, max_size: int = 20):
        self.dsn = dsn
        self.min_size = min_size
        self.max_size = max_size
        self.pool = None

    async def __aenter__(self):
        self.pool = await asyncpg.create_pool(
            self.dsn,
            min_size=self.min_size,
            max_size=self.max_size
        )
        return self.pool

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.pool:
            await self.pool.close()
        return False  # Don't suppress exceptions

# Usage
async with DatabasePool("postgresql://localhost/db") as pool:
    async with pool.acquire() as conn:
        result = await conn.fetch("SELECT * FROM users")
```

**JavaScript**:
```javascript
async function withConnection(dsn, callback) {
  const conn = new DatabaseConnection(dsn);
  try {
    await conn.connect();
    return await callback(conn);
  } finally {
    if (conn.connected) {
      await conn.close();
    }
  }
}

// Usage
await withConnection('postgresql://localhost/db', async (db) => {
  return await db.execute('SELECT * FROM users');
});
```

**Key Points**:
- Use `@asynccontextmanager` decorator for simple cases
- Implement `__aenter__` and `__aexit__` for class-based managers
- Always clean up in `finally` block
- Useful for connections, locks, file handles, sessions

---

## Pattern 5: Async Queue for Producer-Consumer

**Problem**: Coordinate multiple producers and consumers with backpressure

**Python**:
```python
import asyncio
from asyncio import Queue

async def producer(queue: Queue, producer_id: int):
    """Produce items and add to queue."""
    for i in range(10):
        item = f"item-{producer_id}-{i}"
        await queue.put(item)
        print(f"Producer {producer_id} added {item}")
        await asyncio.sleep(0.1)

async def consumer(queue: Queue, consumer_id: int):
    """Consume items from queue."""
    while True:
        item = await queue.get()
        try:
            print(f"Consumer {consumer_id} processing {item}")
            await asyncio.sleep(0.5)  # Simulate work
        finally:
            queue.task_done()

async def main():
    # Bounded queue provides backpressure
    queue = Queue(maxsize=5)

    # Start producers
    producers = [
        asyncio.create_task(producer(queue, i))
        for i in range(3)
    ]

    # Start consumers
    consumers = [
        asyncio.create_task(consumer(queue, i))
        for i in range(2)
    ]

    # Wait for all items to be produced
    await asyncio.gather(*producers)

    # Wait for all items to be consumed
    await queue.join()

    # Cancel consumers (they run forever)
    for task in consumers:
        task.cancel()
```

**Key Points**:
- Bounded queue (`maxsize`) provides backpressure
- `queue.task_done()` signals completion
- `queue.join()` waits for all items to be processed
- Useful for rate limiting, buffering, work distribution

---

## Pattern 6: Async Iterator / Stream Processing

**Problem**: Process large datasets or streams without loading everything into memory

**Python**:
```python
import asyncio
from typing import AsyncIterator

async def fetch_page(page: int) -> list[dict]:
    """Fetch a page of data from API"""
    await asyncio.sleep(0.1)
    return [{"id": i, "page": page} for i in range(10)]

async def fetch_all_items() -> AsyncIterator[dict]:
    """Async generator that yields items one at a time"""
    page = 1
    while True:
        items = await fetch_page(page)
        if not items:
            break

        for item in items:
            yield item

        page += 1
        if page > 5:  # Limit for example
            break

async def process_stream():
    """Process items as they arrive"""
    async for item in fetch_all_items():
        # Process each item without loading all into memory
        result = await process_item(item)
        print(f"Processed: {result}")

async def process_item(item: dict) -> dict:
    await asyncio.sleep(0.01)
    return {**item, "processed": True}

# Advanced: Transform stream with async comprehension
async def main():
    processed_items = [
        item async for item in fetch_all_items()
        if item["id"] % 2 == 0  # Filter even IDs
    ]
    print(f"Processed {len(processed_items)} items")
```

**JavaScript**:
```javascript
// Async generator function
async function* fetchAllItems() {
  let page = 1;

  while (true) {
    const items = await fetchPage(page);
    if (items.length === 0) break;

    for (const item of items) {
      yield item;
    }

    page++;
    if (page > 5) break; // Limit for example
  }
}

async function fetchPage(page) {
  await new Promise(r => setTimeout(r, 100));
  return Array.from({ length: 10 }, (_, i) => ({ id: i, page }));
}

async function processStream() {
  // For-await-of loop
  for await (const item of fetchAllItems()) {
    const result = await processItem(item);
    console.log(`Processed: ${JSON.stringify(result)}`);
  }
}

async function processItem(item) {
  await new Promise(r => setTimeout(r, 10));
  return { ...item, processed: true };
}

// Usage
await processStream();
```

---

## Pattern 7: Circuit Breaker

**Problem**: Prevent cascading failures when a service is down

**Python**:
```python
import asyncio
from datetime import datetime, timedelta
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    async def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout):
                self.state = CircuitState.HALF_OPEN
                print("Circuit breaker: HALF_OPEN (testing recovery)")
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        print("Circuit breaker: CLOSED (normal operation)")

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            print(f"Circuit breaker: OPEN (failed {self.failure_count} times)")

# Usage
async def unreliable_service():
    """Simulates a failing service"""
    import random
    if random.random() < 0.8:
        raise ConnectionError("Service unavailable")
    return "Success"

async def main():
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=5.0)

    for i in range(10):
        try:
            result = await breaker.call(unreliable_service)
            print(f"Request {i}: {result}")
        except Exception as e:
            print(f"Request {i} failed: {e}")

        await asyncio.sleep(1)
```

---

## Pattern 8: Structured Concurrency / Task Groups

**Problem**: Manage lifecycle of multiple related tasks

**Python 3.11+**:
```python
import asyncio

async def task1():
    print("Task 1 starting")
    await asyncio.sleep(2)
    print("Task 1 done")
    return "result1"

async def task2():
    print("Task 2 starting")
    await asyncio.sleep(1)
    raise ValueError("Task 2 failed!")

async def task3():
    print("Task 3 starting")
    await asyncio.sleep(3)
    print("Task 3 done")
    return "result3"

async def main():
    # TaskGroup ensures all tasks are cleaned up
    try:
        async with asyncio.TaskGroup() as tg:
            t1 = tg.create_task(task1())
            t2 = tg.create_task(task2())
            t3 = tg.create_task(task3())

        # If we reach here, all tasks succeeded
        print(f"Results: {t1.result()}, {t3.result()}")
    except* ValueError as eg:
        # Exception group handling
        print(f"Tasks failed: {eg.exceptions}")
    # All tasks are guaranteed to be cancelled/completed
```

**JavaScript (AbortController for task groups)**:
```javascript
class TaskGroup {
  constructor() {
    this.tasks = [];
    this.controller = new AbortController();
  }

  add(fn) {
    const task = fn(this.controller.signal);
    this.tasks.push(task);
    return task;
  }

  async run() {
    try {
      return await Promise.all(this.tasks);
    } catch (error) {
      // Cancel all tasks on any failure
      this.controller.abort();
      throw error;
    }
  }
}

async function task1(signal) {
  console.log('Task 1 starting');
  await new Promise(r => setTimeout(r, 2000));
  if (signal.aborted) throw new Error('Aborted');
  console.log('Task 1 done');
  return 'result1';
}

async function task2(signal) {
  console.log('Task 2 starting');
  await new Promise(r => setTimeout(r, 1000));
  throw new Error('Task 2 failed!');
}

// Usage
const group = new TaskGroup();
group.add(task1);
group.add(task2);

try {
  await group.run();
} catch (error) {
  console.log('Task group failed:', error.message);
}
```
