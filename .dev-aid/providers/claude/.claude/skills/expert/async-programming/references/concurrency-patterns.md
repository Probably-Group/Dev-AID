# Async Concurrency Patterns

This document provides detailed implementation patterns for managing concurrency, shared state, and resource safety in async programming.

---

## Pattern 1: Protecting Shared State with Locks

### When to Use
- Multiple async tasks access the same mutable data
- Operations involve read-modify-write sequences
- Data consistency is critical

### Implementation

```python
import asyncio

class SafeCounter:
    """Thread-safe counter for async contexts."""
    def __init__(self):
        self._value = 0
        self._lock = asyncio.Lock()

    async def increment(self) -> int:
        async with self._lock:
            self._value += 1
            return self._value

    async def get(self) -> int:
        async with self._lock:
            return self._value

    async def add(self, amount: int) -> int:
        async with self._lock:
            self._value += amount
            return self._value
```

### Advanced: Read-Write Lock

For scenarios with many reads and few writes, use a read-write lock:

```python
import asyncio

class RWLock:
    """Read-write lock allowing multiple readers or one writer."""
    def __init__(self):
        self._readers = 0
        self._writer = False
        self._read_lock = asyncio.Lock()
        self._write_lock = asyncio.Lock()

    async def acquire_read(self):
        async with self._read_lock:
            while self._writer:
                await asyncio.sleep(0.01)
            self._readers += 1

    async def release_read(self):
        async with self._read_lock:
            self._readers -= 1

    async def acquire_write(self):
        await self._write_lock.acquire()
        self._writer = True
        # Wait for all readers to finish
        while self._readers > 0:
            await asyncio.sleep(0.01)

    async def release_write(self):
        self._writer = False
        self._write_lock.release()

class CachedData:
    def __init__(self):
        self._data = {}
        self._rwlock = RWLock()

    async def get(self, key: str):
        await self._rwlock.acquire_read()
        try:
            return self._data.get(key)
        finally:
            await self._rwlock.release_read()

    async def set(self, key: str, value):
        await self._rwlock.acquire_write()
        try:
            self._data[key] = value
        finally:
            await self._rwlock.release_write()
```

---

## Pattern 2: Atomic Database Operations

### Problem
Race conditions in database operations (TOCTOU - Time of Check, Time of Use).

### Bad Example - Race Condition
```python
async def transfer_unsafe(db, from_id: int, to_id: int, amount: int):
    # RACE CONDITION: Another transaction can modify between check and update
    from_account = await db.fetchrow("SELECT * FROM accounts WHERE id = $1", from_id)
    if from_account['balance'] < amount:
        raise ValueError("Insufficient funds")

    # Another transaction could modify here!
    await db.execute("UPDATE accounts SET balance = balance - $1 WHERE id = $2", amount, from_id)
    await db.execute("UPDATE accounts SET balance = balance + $1 WHERE id = $2", amount, to_id)
```

### Good Example - Atomic with Row Locks
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def transfer_safe(db: AsyncSession, from_id: int, to_id: int, amount: int):
    """Atomic transfer using row locks."""
    async with db.begin():
        # Lock both rows for update
        stmt = (
            select(Account)
            .where(Account.id.in_([from_id, to_id]))
            .with_for_update()  # Prevents other transactions from modifying
        )
        accounts = {a.id: a for a in (await db.execute(stmt)).scalars()}

        if accounts[from_id].balance < amount:
            raise ValueError("Insufficient funds")

        accounts[from_id].balance -= amount
        accounts[to_id].balance += amount
        # Transaction commits atomically
```

### Alternative: Optimistic Locking
```python
async def update_with_version(db, account_id: int, new_balance: int, expected_version: int):
    """Update only if version matches (optimistic locking)."""
    result = await db.execute(
        """
        UPDATE accounts
        SET balance = $1, version = version + 1
        WHERE id = $2 AND version = $3
        RETURNING id
        """,
        new_balance, account_id, expected_version
    )
    if not result:
        raise ConcurrentModificationError("Account was modified by another transaction")
```

---

## Pattern 3: Resource Management with Context Managers

### Basic Async Context Manager

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_connection():
    """Ensure connection cleanup even on cancellation."""
    conn = await pool.acquire()
    try:
        yield conn
    finally:
        await pool.release(conn)

# Usage
async def query_data():
    async with get_connection() as conn:
        return await conn.fetch("SELECT * FROM users")
```

### Advanced: Nested Resource Management

```python
@asynccontextmanager
async def transaction_context(pool):
    """Manage connection and transaction together."""
    async with pool.acquire() as conn:
        async with conn.transaction():
            yield conn
            # Auto-commit on success, rollback on exception

# Usage
async def atomic_operation():
    async with transaction_context(pool) as conn:
        await conn.execute("INSERT INTO logs ...")
        await conn.execute("UPDATE accounts ...")
        # Both succeed or both rollback
```

### Timeout Context Manager

```python
@asynccontextmanager
async def with_timeout(seconds: float):
    """Add timeout to operations."""
    try:
        async with asyncio.timeout(seconds):
            yield
    except asyncio.TimeoutError:
        raise OperationTimeout(f"Operation exceeded {seconds}s")

# Usage
async def fetch_with_timeout():
    async with with_timeout(5.0):
        return await slow_api_call()
```

---

## Pattern 4: Graceful Shutdown

### Complete Shutdown Pattern

```python
import asyncio
import signal

class GracefulApp:
    def __init__(self):
        self.shutdown_event = asyncio.Event()
        self.tasks: set[asyncio.Task] = set()
        self.background_tasks: set[asyncio.Task] = set()

    def create_task(self, coro) -> asyncio.Task:
        """Create and track a task."""
        task = asyncio.create_task(coro)
        self.background_tasks.add(task)
        task.add_done_callback(self.background_tasks.discard)
        return task

    async def run(self):
        """Main application loop with graceful shutdown."""
        loop = asyncio.get_event_loop()

        # Register signal handlers
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, self._handle_shutdown)

        try:
            # Start background workers
            self.create_task(self.worker())
            self.create_task(self.health_check())

            # Wait for shutdown signal
            await self.shutdown_event.wait()

        finally:
            await self._cleanup()

    def _handle_shutdown(self):
        """Signal handler for graceful shutdown."""
        print("Shutdown signal received, cleaning up...")
        self.shutdown_event.set()

    async def _cleanup(self):
        """Cancel all tasks and wait for cleanup."""
        # Cancel all background tasks
        for task in self.background_tasks:
            task.cancel()

        # Wait for all tasks to complete cancellation
        await asyncio.gather(*self.background_tasks, return_exceptions=True)

        print("All tasks cleaned up successfully")

    async def worker(self):
        """Example background worker."""
        try:
            while not self.shutdown_event.is_set():
                await self.do_work()
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            print("Worker cancelled, cleaning up...")
            raise  # Re-raise to complete cancellation
```

---

## Pattern 5: Task Coordination with Events

### Event-Based Coordination

```python
import asyncio

class DataProcessor:
    def __init__(self):
        self.data_ready = asyncio.Event()
        self.data = None

    async def producer(self):
        """Produce data and signal when ready."""
        await asyncio.sleep(2)  # Simulate work
        self.data = {"result": "computed"}
        self.data_ready.set()  # Signal consumers
        print("Data ready!")

    async def consumer(self, consumer_id: int):
        """Wait for data to be ready."""
        print(f"Consumer {consumer_id} waiting...")
        await self.data_ready.wait()  # Block until set
        print(f"Consumer {consumer_id} processing: {self.data}")

# Usage
async def main():
    processor = DataProcessor()
    await asyncio.gather(
        processor.producer(),
        processor.consumer(1),
        processor.consumer(2),
        processor.consumer(3),
    )
```

### Condition Variables

```python
class BoundedQueue:
    """Queue with bounded size using condition variables."""
    def __init__(self, max_size: int):
        self.queue = []
        self.max_size = max_size
        self.condition = asyncio.Condition()

    async def put(self, item):
        async with self.condition:
            # Wait until space available
            while len(self.queue) >= self.max_size:
                await self.condition.wait()

            self.queue.append(item)
            self.condition.notify()  # Wake up consumers

    async def get(self):
        async with self.condition:
            # Wait until items available
            while not self.queue:
                await self.condition.wait()

            item = self.queue.pop(0)
            self.condition.notify()  # Wake up producers
            return item
```

---

## Pattern 6: Message Passing with Queues

### Producer-Consumer Pattern

```python
import asyncio
from typing import Optional

class WorkerPool:
    def __init__(self, num_workers: int = 4):
        self.queue: asyncio.Queue = asyncio.Queue()
        self.num_workers = num_workers
        self.workers: list[asyncio.Task] = []

    async def worker(self, worker_id: int):
        """Worker that processes items from queue."""
        while True:
            item = await self.queue.get()

            if item is None:  # Poison pill
                self.queue.task_done()
                break

            try:
                await self.process_item(item)
            except Exception as e:
                print(f"Worker {worker_id} error: {e}")
            finally:
                self.queue.task_done()

    async def process_item(self, item):
        """Override this method with actual processing logic."""
        await asyncio.sleep(1)  # Simulate work
        print(f"Processed: {item}")

    async def start(self):
        """Start all workers."""
        self.workers = [
            asyncio.create_task(self.worker(i))
            for i in range(self.num_workers)
        ]

    async def submit(self, item):
        """Submit item for processing."""
        await self.queue.put(item)

    async def stop(self):
        """Stop all workers gracefully."""
        # Send poison pills
        for _ in self.workers:
            await self.queue.put(None)

        # Wait for all items to be processed
        await self.queue.join()

        # Wait for workers to finish
        await asyncio.gather(*self.workers)

# Usage
async def main():
    pool = WorkerPool(num_workers=4)
    await pool.start()

    # Submit work
    for i in range(20):
        await pool.submit(f"task-{i}")

    # Shutdown
    await pool.stop()
```

---

## Pattern 7: Retry with Exponential Backoff

```python
import asyncio
import random
from typing import TypeVar, Callable

T = TypeVar('T')

async def retry_with_backoff(
    func: Callable[[], T],
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential: bool = True
) -> T:
    """Retry async function with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise

            # Calculate delay
            if exponential:
                delay = min(base_delay * (2 ** attempt), max_delay)
            else:
                delay = base_delay

            # Add jitter to prevent thundering herd
            jitter = random.uniform(0, delay * 0.1)
            await asyncio.sleep(delay + jitter)

            print(f"Retry {attempt + 1}/{max_retries} after {delay:.1f}s: {e}")

# Usage
async def unreliable_api_call():
    if random.random() < 0.7:
        raise ConnectionError("API unavailable")
    return "success"

result = await retry_with_backoff(unreliable_api_call, max_retries=5)
```

---

## Pattern 8: Circuit Breaker

```python
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        success_threshold: int = 2
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold

        self.state = CircuitState.CLOSED
        self.failures = 0
        self.successes = 0
        self.last_failure_time: Optional[datetime] = None

    async def call(self, func):
        """Execute function through circuit breaker."""
        if self.state == CircuitState.OPEN:
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout):
                self.state = CircuitState.HALF_OPEN
                self.successes = 0
            else:
                raise CircuitBreakerOpen("Circuit breaker is open")

        try:
            result = await func()
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        if self.state == CircuitState.HALF_OPEN:
            self.successes += 1
            if self.successes >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.failures = 0
        elif self.state == CircuitState.CLOSED:
            self.failures = 0

    def _on_failure(self):
        self.failures += 1
        self.last_failure_time = datetime.now()

        if self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Usage
breaker = CircuitBreaker(failure_threshold=3, timeout=30.0)

async def call_external_api():
    return await breaker.call(lambda: external_api_request())
```

---

## Pattern 9: Timeouts and Deadlines

### Operation Timeouts

```python
import asyncio

async def fetch_with_timeout(url: str, timeout: float = 5.0):
    """Fetch with timeout."""
    try:
        async with asyncio.timeout(timeout):
            return await fetch(url)
    except asyncio.TimeoutError:
        raise RequestTimeout(f"Request to {url} timed out after {timeout}s")

# Multiple operations with overall deadline
async def fetch_all_with_deadline(urls: list[str], deadline: float = 30.0):
    """Fetch all URLs within overall deadline."""
    try:
        async with asyncio.timeout(deadline):
            return await asyncio.gather(*[fetch(url) for url in urls])
    except asyncio.TimeoutError:
        raise DeadlineExceeded(f"Failed to fetch all URLs within {deadline}s")
```

---

## Pattern 10: Async Iterators and Generators

### Async Generator for Streaming

```python
async def stream_large_dataset(query: str):
    """Stream results without loading all into memory."""
    async with get_connection() as conn:
        cursor = await conn.cursor(query)
        async for row in cursor:
            yield row
        await cursor.close()

# Usage
async def process_stream():
    async for item in stream_large_dataset("SELECT * FROM large_table"):
        await process(item)
```

### Async Context Iterator

```python
class AsyncFileReader:
    """Async iterator for reading files line by line."""
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.file = None

    async def __aenter__(self):
        self.file = await aiofiles.open(self.filepath, 'r')
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.file.close()

    def __aiter__(self):
        return self

    async def __anext__(self):
        line = await self.file.readline()
        if not line:
            raise StopAsyncIteration
        return line.strip()

# Usage
async with AsyncFileReader('large_file.txt') as reader:
    async for line in reader:
        await process_line(line)
```

---

## Summary

These patterns provide robust solutions for:
- **Shared state protection**: Locks, RWLocks
- **Database atomicity**: Row locks, optimistic locking
- **Resource safety**: Context managers, cleanup
- **Graceful shutdown**: Signal handling, task cancellation
- **Task coordination**: Events, conditions, queues
- **Resilience**: Retries, circuit breakers, timeouts
- **Streaming**: Async iterators and generators

Choose patterns based on your specific concurrency requirements and failure scenarios.
