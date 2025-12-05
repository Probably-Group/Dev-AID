# Async Programming Testing Guide

This document provides comprehensive testing strategies for async code using pytest-asyncio and Test-Driven Development (TDD).

---

## TDD Workflow for Async Code

### Step 1: Write Failing Test First

Always start by writing tests that capture the behavior you want, especially for race conditions and resource cleanup.

#### Example 1: Testing Concurrent Counter Safety

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_concurrent_counter_safety():
    """Test counter maintains consistency under concurrent access."""
    counter = SafeCounter()  # Not implemented yet - will fail

    async def increment_many():
        for _ in range(100):
            await counter.increment()

    # Run 10 concurrent incrementers
    await asyncio.gather(*[increment_many() for _ in range(10)])

    # Must be exactly 1000 (no lost updates)
    assert await counter.get() == 1000
```

#### Example 2: Testing Resource Cleanup on Cancellation

```python
@pytest.mark.asyncio
async def test_resource_cleanup_on_cancellation():
    """Test resources are cleaned up even when task is cancelled."""
    cleanup_called = False

    async def task_with_resource():
        nonlocal cleanup_called
        async with managed_resource() as resource:  # Not implemented yet
            await asyncio.sleep(10)  # Long operation
        cleanup_called = True

    task = asyncio.create_task(task_with_resource())
    await asyncio.sleep(0.1)
    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task

    assert cleanup_called  # Cleanup must happen
```

#### Example 3: Testing Race Condition Prevention

```python
@pytest.mark.asyncio
async def test_cache_no_duplicate_fetches():
    """Test cache doesn't fetch same key multiple times concurrently."""
    fetch_count = 0

    async def fetch_data(key):
        nonlocal fetch_count
        fetch_count += 1
        await asyncio.sleep(0.1)
        return f"data-{key}"

    cache = SafeCache(fetch_data)  # Not implemented yet

    # Multiple concurrent requests for same key
    results = await asyncio.gather(*[
        cache.get("key1") for _ in range(10)
    ])

    # Should only fetch once
    assert fetch_count == 1
    # All should get same result
    assert all(r == "data-key1" for r in results)
```

---

### Step 2: Implement Minimum to Pass

Write just enough code to make the tests pass.

#### Implementation 1: Safe Counter

```python
import asyncio

class SafeCounter:
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
```

#### Implementation 2: Resource Manager

```python
from contextlib import asynccontextmanager

class Resource:
    def __init__(self):
        self.closed = False

    async def close(self):
        self.closed = True

@asynccontextmanager
async def managed_resource():
    resource = Resource()
    try:
        yield resource
    finally:
        await resource.close()  # Always runs, even on cancellation
```

#### Implementation 3: Safe Cache

```python
class SafeCache:
    def __init__(self, fetch_fn):
        self._data = {}
        self._locks = {}
        self._global_lock = asyncio.Lock()
        self._fetch_fn = fetch_fn

    async def get(self, key: str):
        # Get or create lock for this key
        async with self._global_lock:
            if key not in self._locks:
                self._locks[key] = asyncio.Lock()
            key_lock = self._locks[key]

        # Use key-specific lock
        async with key_lock:
            if key not in self._data:
                self._data[key] = await self._fetch_fn(key)
            return self._data[key]
```

---

### Step 3: Refactor

Improve the implementation while keeping tests passing.

```python
class OptimizedSafeCache:
    """Cache with timeout and memory limits."""
    def __init__(self, fetch_fn, max_size: int = 1000, ttl: int = 300):
        self._data = {}
        self._locks = {}
        self._global_lock = asyncio.Lock()
        self._fetch_fn = fetch_fn
        self._max_size = max_size
        self._ttl = ttl

    async def get(self, key: str):
        async with self._global_lock:
            if key not in self._locks:
                self._locks[key] = asyncio.Lock()
            key_lock = self._locks[key]

        async with key_lock:
            # Check if cached and not expired
            if key in self._data:
                value, timestamp = self._data[key]
                if time.time() - timestamp < self._ttl:
                    return value

            # Fetch new value
            value = await self._fetch_fn(key)
            self._data[key] = (value, time.time())

            # Evict oldest if over size limit
            if len(self._data) > self._max_size:
                oldest_key = min(self._data, key=lambda k: self._data[k][1])
                del self._data[oldest_key]

            return value
```

---

### Step 4: Run Full Verification

```bash
# Run async tests
pytest tests/ -v --asyncio-mode=auto

# Check for blocking calls
python -m asyncio debug

# Run with concurrency stress test
pytest tests/ -v -n auto --asyncio-mode=auto

# Run with coverage
pytest tests/ --cov=myapp --cov-report=html
```

---

## Testing Patterns

### Pattern 1: Testing Timeouts

```python
@pytest.mark.asyncio
async def test_operation_timeout():
    """Test operation respects timeout."""
    async def slow_operation():
        await asyncio.sleep(10)
        return "done"

    with pytest.raises(asyncio.TimeoutError):
        async with asyncio.timeout(0.1):
            await slow_operation()
```

### Pattern 2: Testing Error Handling

```python
@pytest.mark.asyncio
async def test_error_propagation():
    """Test errors are properly propagated."""
    async def failing_task():
        raise ValueError("Test error")

    with pytest.raises(ValueError, match="Test error"):
        await failing_task()
```

### Pattern 3: Testing Graceful Shutdown

```python
@pytest.mark.asyncio
async def test_graceful_shutdown():
    """Test application shuts down gracefully."""
    app = GracefulApp()

    # Start background tasks
    app_task = asyncio.create_task(app.run())
    await asyncio.sleep(0.1)

    # Trigger shutdown
    app.shutdown_event.set()

    # Should complete without hanging
    async with asyncio.timeout(5.0):
        await app_task

    # All tasks should be cleaned up
    assert len(app.background_tasks) == 0
```

### Pattern 4: Testing with Mocks

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_with_mock():
    """Test using async mocks."""
    mock_db = AsyncMock()
    mock_db.fetchval.return_value = 42

    result = await get_user_count(mock_db)

    assert result == 42
    mock_db.fetchval.assert_called_once_with("SELECT COUNT(*) FROM users")
```

### Pattern 5: Testing Race Conditions

```python
@pytest.mark.asyncio
async def test_no_race_condition():
    """Test for race conditions under concurrent load."""
    account = BankAccount(initial_balance=1000)

    async def deposit(amount):
        for _ in range(100):
            await account.deposit(amount)

    async def withdraw(amount):
        for _ in range(100):
            await account.withdraw(amount)

    # Run concurrent deposits and withdrawals
    await asyncio.gather(
        deposit(10),
        deposit(10),
        withdraw(10),
        withdraw(10)
    )

    # Balance should be exactly 1000 (no lost updates)
    assert await account.get_balance() == 1000
```

### Pattern 6: Testing Connection Pool Behavior

```python
@pytest.mark.asyncio
async def test_connection_pool_limits():
    """Test connection pool respects max_size."""
    pool = await asyncpg.create_pool(
        DATABASE_URL,
        min_size=1,
        max_size=2
    )

    acquired = []

    async def acquire_conn():
        conn = await pool.acquire()
        acquired.append(conn)
        await asyncio.sleep(1)
        await pool.release(conn)

    # Try to acquire 3 connections (max is 2)
    task1 = asyncio.create_task(acquire_conn())
    task2 = asyncio.create_task(acquire_conn())
    task3 = asyncio.create_task(acquire_conn())

    await asyncio.sleep(0.1)

    # Only 2 should be acquired
    assert len(acquired) == 2

    await asyncio.gather(task1, task2, task3)
    await pool.close()
```

### Pattern 7: Testing Retry Logic

```python
@pytest.mark.asyncio
async def test_retry_logic():
    """Test retry mechanism works correctly."""
    call_count = 0

    async def flaky_function():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError("Temporary failure")
        return "success"

    result = await retry_with_backoff(flaky_function, max_retries=5)

    assert result == "success"
    assert call_count == 3  # Failed twice, succeeded on third
```

### Pattern 8: Testing Circuit Breaker

```python
@pytest.mark.asyncio
async def test_circuit_breaker_opens():
    """Test circuit breaker opens after threshold failures."""
    breaker = CircuitBreaker(failure_threshold=3)

    async def failing_call():
        raise ConnectionError("Service down")

    # First 3 calls fail
    for _ in range(3):
        with pytest.raises(ConnectionError):
            await breaker.call(failing_call)

    # Circuit should now be open
    assert breaker.state == CircuitState.OPEN

    # Next call should fail immediately
    with pytest.raises(CircuitBreakerOpen):
        await breaker.call(failing_call)
```

---

## Fixtures for Async Testing

### Basic Fixtures

```python
import pytest
import asyncio

@pytest.fixture
def event_loop():
    """Create event loop for tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def database():
    """Provide database connection for tests."""
    db = await connect_to_db()
    yield db
    await db.close()

@pytest.fixture
async def cache():
    """Provide cache instance for tests."""
    cache = SafeCache()
    yield cache
    await cache.clear()
```

### Advanced Fixtures

```python
@pytest.fixture
async def worker_pool():
    """Provide worker pool with automatic cleanup."""
    pool = WorkerPool(num_workers=4)
    await pool.start()
    yield pool
    await pool.stop()

@pytest.fixture
async def mock_api_server():
    """Provide mock HTTP server for testing."""
    from aiohttp import web

    app = web.Application()
    app.router.add_get('/users/{id}', mock_get_user)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()

    yield 'http://localhost:8080'

    await runner.cleanup()
```

---

## Testing Best Practices

### 1. Use pytest-asyncio Configuration

```python
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

### 2. Test at Different Concurrency Levels

```python
@pytest.mark.parametrize("num_tasks", [1, 10, 100])
@pytest.mark.asyncio
async def test_concurrent_safety(num_tasks):
    """Test with varying concurrency levels."""
    counter = SafeCounter()
    await asyncio.gather(*[counter.increment() for _ in range(num_tasks)])
    assert await counter.get() == num_tasks
```

### 3. Test Cancellation Scenarios

```python
@pytest.mark.asyncio
async def test_cancellation_cleanup():
    """Test cleanup happens on cancellation."""
    resources = []

    async def task_with_resource():
        resource = await acquire_resource()
        resources.append(resource)
        try:
            await asyncio.sleep(10)
        finally:
            await resource.close()
            resources.remove(resource)

    task = asyncio.create_task(task_with_resource())
    await asyncio.sleep(0.1)
    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task

    # Resource should be cleaned up
    assert len(resources) == 0
```

### 4. Use Timeouts in Tests

```python
@pytest.mark.asyncio
async def test_with_timeout():
    """Prevent tests from hanging."""
    async with asyncio.timeout(5.0):
        result = await long_running_operation()
    assert result is not None
```

### 5. Test Error Handling

```python
@pytest.mark.asyncio
async def test_error_handling():
    """Test proper error handling in async code."""
    async def task_with_error():
        raise ValueError("Test error")

    with pytest.raises(ValueError, match="Test error"):
        await task_with_error()
```

---

## Performance Testing

### Load Testing

```python
@pytest.mark.asyncio
async def test_throughput():
    """Test system throughput under load."""
    start_time = time.time()
    requests = 1000

    results = await asyncio.gather(*[
        process_request(i) for i in range(requests)
    ])

    elapsed = time.time() - start_time
    throughput = requests / elapsed

    assert throughput > 100  # Should handle 100 req/s
    assert all(r is not None for r in results)
```

### Memory Testing

```python
@pytest.mark.asyncio
async def test_memory_usage():
    """Test memory doesn't leak under load."""
    import tracemalloc

    tracemalloc.start()
    initial_memory = tracemalloc.get_traced_memory()[0]

    # Run workload
    for _ in range(100):
        await process_large_dataset()

    final_memory = tracemalloc.get_traced_memory()[0]
    tracemalloc.stop()

    # Memory growth should be minimal
    growth = (final_memory - initial_memory) / initial_memory
    assert growth < 0.1  # Less than 10% growth
```

---

## Summary

Key testing strategies:
1. **Write tests first** - TDD approach
2. **Test race conditions** - Concurrent access scenarios
3. **Test cancellation** - Resource cleanup
4. **Test timeouts** - Prevent hanging tests
5. **Use fixtures** - Reusable test infrastructure
6. **Mock external services** - Isolate async code
7. **Test at scale** - Vary concurrency levels
8. **Measure performance** - Ensure efficiency

Always run tests with:
```bash
pytest tests/ -v --asyncio-mode=auto -n auto
```
