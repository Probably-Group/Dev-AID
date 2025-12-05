# Async Programming Anti-Patterns

This document catalogs common mistakes and anti-patterns in async programming, along with correct alternatives.

---

## Anti-Pattern 1: Unprotected Shared State

### The Problem
Accessing shared mutable state without synchronization leads to race conditions and data corruption.

### Bad Example - Race Condition on Cache
```python
class UnsafeCache:
    def __init__(self):
        self.data = {}

    async def get_or_fetch(self, key):
        # RACE CONDITION: Multiple tasks can reach this point simultaneously
        if key not in self.data:
            # Task A checks, finds key missing
            # Task B checks, finds key missing
            # Both fetch the same data
            self.data[key] = await fetch(key)
        return self.data[key]
```

**Problem**: Two concurrent calls can both see the key missing and both fetch it, causing duplicate work and race conditions.

### Correct Implementation
```python
class SafeCache:
    def __init__(self):
        self.data = {}
        self._lock = asyncio.Lock()

    async def get_or_fetch(self, key):
        async with self._lock:
            if key not in self.data:
                self.data[key] = await fetch(key)
            return self.data[key]
```

**Why Better**: Lock ensures only one task can check and update at a time.

### Real-World Example: Counter Race Condition
```python
# BAD - Lost updates
class BrokenCounter:
    def __init__(self):
        self.value = 0

    async def increment(self):
        current = self.value  # Read
        await asyncio.sleep(0)  # Context switch
        self.value = current + 1  # Write stale value
        # Lost updates when multiple tasks run concurrently

# GOOD - Atomic updates
class SafeCounter:
    def __init__(self):
        self.value = 0
        self._lock = asyncio.Lock()

    async def increment(self):
        async with self._lock:
            self.value += 1
```

---

## Anti-Pattern 2: Fire and Forget Tasks

### The Problem
Creating tasks without tracking them can lead to silent failures and resource leaks.

### Bad Example - Lost Task Reference
```python
async def process_request(data):
    # PROBLEM: Task may be garbage collected before completion
    asyncio.create_task(send_notification(data))
    return "OK"
```

**Problems**:
1. Task can be garbage collected mid-execution
2. Exceptions are silently lost
3. No way to wait for completion during shutdown
4. Resource leaks if tasks hold connections

### Correct Implementation
```python
class TaskTracker:
    def __init__(self):
        self.tasks: set[asyncio.Task] = set()

    def create_task(self, coro):
        task = asyncio.create_task(coro)
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)
        return task

    async def shutdown(self):
        """Wait for all tasks to complete."""
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)

tracker = TaskTracker()

async def process_request(data):
    tracker.create_task(send_notification(data))
    return "OK"
```

**Why Better**: Tasks are tracked and can be properly cleaned up.

---

## Anti-Pattern 3: Blocking the Event Loop

### The Problem
Using blocking operations freezes the entire event loop, preventing all async tasks from running.

### Bad Example - Blocking Calls
```python
import time

async def broken_handler():
    # BLOCKS ENTIRE EVENT LOOP
    time.sleep(5)  # All async tasks freeze
    with open('file.txt') as f:  # Blocking I/O
        data = f.read()
    result = expensive_computation()  # CPU-bound blocks loop
    return result
```

**Impact**: While `broken_handler` runs, NO other async task can execute.

### Correct Implementation
```python
import asyncio
import aiofiles

async def correct_handler():
    # Non-blocking sleep
    await asyncio.sleep(5)

    # Non-blocking file I/O
    async with aiofiles.open('file.txt') as f:
        data = await f.read()

    # CPU-bound work in executor
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, expensive_computation)

    return result
```

### Common Blocking Operations to Avoid

| Never Use (Blocking) | Use Instead (Async) |
|---------------------|-------------------|
| `time.sleep()` | `asyncio.sleep()` |
| `requests.get()` | `aiohttp.get()` or `httpx.get()` |
| `open()` | `aiofiles.open()` |
| `subprocess.run()` | `asyncio.create_subprocess_exec()` |
| `sqlite3.connect()` | `aiosqlite.connect()` |
| CPU-intensive work | `loop.run_in_executor()` |

---

## Anti-Pattern 4: Ignoring CancelledError

### The Problem
Not properly handling task cancellation leads to resource leaks.

### Bad Example - Swallowing Cancellation
```python
async def worker():
    while True:
        try:
            await do_work()
        except asyncio.CancelledError:
            print("Cancelled, but continuing anyway")
            # PROBLEM: Task never actually stops
            continue
        except Exception:
            continue
```

### Correct Implementation
```python
async def worker():
    try:
        while True:
            await do_work()
    except asyncio.CancelledError:
        # Clean up resources
        await cleanup()
        # Re-raise to complete cancellation
        raise
    except Exception as e:
        logger.error(f"Worker error: {e}")
        raise
```

**Why Better**: Respects cancellation and ensures cleanup.

---

## Anti-Pattern 5: Nested Event Loops

### The Problem
Creating nested event loops causes errors and unexpected behavior.

### Bad Example - Creating New Loop Inside Async Function
```python
async def outer():
    # WRONG: Already inside an event loop
    result = asyncio.run(inner())  # RuntimeError!
    return result
```

### Correct Implementation
```python
async def outer():
    # Just await the coroutine
    result = await inner()
    return result
```

---

## Anti-Pattern 6: Modifying Shared Data During await

### The Problem
Shared data can be modified by other tasks during await points.

### Bad Example - TOCTOU (Time of Check, Time of Use)
```python
async def withdraw(account_id: int, amount: int):
    # Check balance
    balance = await db.fetchval(
        "SELECT balance FROM accounts WHERE id = $1",
        account_id
    )

    # VULNERABLE: Balance can change here by another task
    await asyncio.sleep(0.1)

    if balance >= amount:
        # Use stale balance value
        await db.execute(
            "UPDATE accounts SET balance = $1 WHERE id = $2",
            balance - amount,
            account_id
        )
```

**Problem**: Another task can withdraw money between the check and update, causing negative balance.

### Correct Implementation
```python
async def withdraw(account_id: int, amount: int):
    # Atomic check-and-update
    result = await db.fetchval(
        """
        UPDATE accounts
        SET balance = balance - $1
        WHERE id = $2 AND balance >= $1
        RETURNING balance
        """,
        amount,
        account_id
    )
    if result is None:
        raise InsufficientFunds()
    return result
```

**Why Better**: Database handles atomicity; no race condition window.

---

## Anti-Pattern 7: Not Using Connection Pools

### The Problem
Creating new connections for each operation is expensive and slow.

### Bad Example - Creating Connection Each Time
```python
async def query_user(user_id: int):
    # EXPENSIVE: New connection every call
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
        return user
    finally:
        await conn.close()
```

**Problems**:
1. Connection overhead on every call
2. Exhausts server connections under load
3. SSL handshake repeated unnecessarily

### Correct Implementation
```python
# Create pool once at startup
pool = await asyncpg.create_pool(DATABASE_URL, min_size=10, max_size=20)

async def query_user(user_id: int):
    # Reuse connection from pool
    async with pool.acquire() as conn:
        user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
        return user
```

**Why Better**: Connections are reused, dramatically improving performance.

---

## Anti-Pattern 8: Sequential Instead of Concurrent

### The Problem
Not using concurrency when operations are independent.

### Bad Example - Sequential API Calls
```python
async def fetch_all_data(ids: list[int]):
    results = []
    for id in ids:
        # SLOW: Waits for each call to complete
        result = await fetch_user(id)
        results.append(result)
    return results
    # Total time: 10 calls × 1s = 10s
```

### Correct Implementation
```python
async def fetch_all_data(ids: list[int]):
    # FAST: All calls run concurrently
    return await asyncio.gather(*[fetch_user(id) for id in ids])
    # Total time: ~1s (max of all calls)
```

**Performance Impact**: Can be 10-100x faster for I/O-bound operations.

---

## Anti-Pattern 9: No Timeouts

### The Problem
Operations without timeouts can hang forever.

### Bad Example - No Timeout
```python
async def fetch_data(url: str):
    # Can hang forever if server is unresponsive
    return await http.get(url)
```

### Correct Implementation
```python
async def fetch_data(url: str, timeout: float = 30.0):
    try:
        async with asyncio.timeout(timeout):
            return await http.get(url)
    except asyncio.TimeoutError:
        raise RequestTimeout(f"Request to {url} timed out after {timeout}s")
```

**Why Better**: Prevents resource exhaustion from hanging requests.

---

## Anti-Pattern 10: Catching All Exceptions Including CancelledError

### The Problem
Catching `Exception` or bare `except:` can mask cancellation.

### Bad Example - Masking Cancellation
```python
async def worker():
    while True:
        try:
            await process_item()
        except Exception:  # Catches CancelledError in Python < 3.8
            pass  # Task can never be cancelled!
```

### Correct Implementation
```python
async def worker():
    while True:
        try:
            await process_item()
        except asyncio.CancelledError:
            # Handle cancellation specifically
            await cleanup()
            raise  # Re-raise to complete cancellation
        except Exception as e:
            # Handle other errors
            logger.error(f"Error: {e}")
```

---

## Anti-Pattern 11: Using Global Event Loop

### The Problem
Accessing global event loop in async context is deprecated.

### Bad Example - Deprecated Loop Access
```python
# DEPRECATED in Python 3.10+
loop = asyncio.get_event_loop()
```

### Correct Implementation
```python
# Inside async function
loop = asyncio.get_running_loop()

# At top level
asyncio.run(main())
```

---

## Anti-Pattern 12: Not Handling Background Task Errors

### The Problem
Exceptions in background tasks are silently ignored.

### Bad Example - Silent Failures
```python
task = asyncio.create_task(background_job())
# If background_job() raises exception, it's silently lost
```

### Correct Implementation
```python
def handle_task_result(task: asyncio.Task):
    try:
        task.result()
    except asyncio.CancelledError:
        pass  # Expected
    except Exception as e:
        logger.error(f"Background task failed: {e}")

task = asyncio.create_task(background_job())
task.add_done_callback(handle_task_result)
```

---

## Anti-Pattern 13: Lock Ordering Issues (Deadlock)

### The Problem
Acquiring locks in different orders can cause deadlock.

### Bad Example - Inconsistent Lock Ordering
```python
# Task 1
async def transfer_a_to_b():
    async with account_a.lock:
        async with account_b.lock:
            # Transfer money

# Task 2
async def transfer_b_to_a():
    async with account_b.lock:  # Different order!
        async with account_a.lock:
            # DEADLOCK possible
```

### Correct Implementation
```python
async def transfer(from_account, to_account, amount):
    # Always acquire locks in consistent order (e.g., by ID)
    accounts = sorted([from_account, to_account], key=lambda a: a.id)
    async with accounts[0].lock:
        async with accounts[1].lock:
            # Safe: locks always acquired in same order
```

---

## Summary: Key Rules to Avoid Anti-Patterns

1. **Protect shared state** with locks or atomic operations
2. **Track all tasks** - never fire-and-forget
3. **Never block** the event loop - use async alternatives
4. **Respect cancellation** - always re-raise `CancelledError`
5. **Use connection pools** - never create connections per operation
6. **Use concurrency** - `asyncio.gather` for independent operations
7. **Always set timeouts** - prevent hanging operations
8. **Handle errors** - especially in background tasks
9. **Consistent lock ordering** - prevent deadlocks
10. **Use atomic database operations** - prevent TOCTOU

These anti-patterns are the most common sources of bugs in async code. Following the correct patterns ensures robust, high-performance async applications.
