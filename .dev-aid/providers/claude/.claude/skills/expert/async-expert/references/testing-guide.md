# Async Testing Guide

Comprehensive guide to testing asynchronous code.

---

## Setup

### Python - pytest-asyncio

```bash
pip install pytest pytest-asyncio pytest-asyncio-cooperative
```

**pytest.ini or pyproject.toml**:
```ini
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

### JavaScript - Jest

```bash
npm install --save-dev jest @types/jest
```

**jest.config.js**:
```javascript
module.exports = {
  testEnvironment: 'node',
  testMatch: ['**/__tests__/**/*.test.js'],
};
```

---

## Pattern 1: Basic Async Test

### Python

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_async_function():
    """Test basic async function."""
    result = await async_add(2, 3)
    assert result == 5

async def async_add(a, b):
    await asyncio.sleep(0.1)  # Simulate async work
    return a + b
```

### JavaScript

```javascript
describe('async functions', () => {
  test('should add numbers', async () => {
    const result = await asyncAdd(2, 3);
    expect(result).toBe(5);
  });
});

async function asyncAdd(a, b) {
  await new Promise(r => setTimeout(r, 100));
  return a + b;
}
```

---

## Pattern 2: Testing with Mocks

### Python - AsyncMock

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_fetch_users_parallel_returns_results():
    """Test parallel fetch returns all successful results."""
    # Create mock that returns different results for each call
    mock_fetch = AsyncMock(side_effect=lambda uid: {
        "id": uid,
        "name": f"User {uid}"
    })

    with patch("app.fetcher.fetch_user", mock_fetch):
        from app.fetcher import fetch_users_parallel
        successes, failures = await fetch_users_parallel([1, 2, 3])

    assert len(successes) == 3
    assert len(failures) == 0
    assert mock_fetch.call_count == 3
    mock_fetch.assert_any_call(1)
    mock_fetch.assert_any_call(2)
    mock_fetch.assert_any_call(3)


@pytest.mark.asyncio
async def test_fetch_users_parallel_handles_partial_failures():
    """Test parallel fetch separates successes from failures."""
    async def mock_fetch(uid):
        if uid == 2:
            raise ConnectionError("Network error")
        return {"id": uid, "name": f"User {uid}"}

    with patch("app.fetcher.fetch_user", mock_fetch):
        from app.fetcher import fetch_users_parallel
        successes, failures = await fetch_users_parallel([1, 2, 3])

    assert len(successes) == 2
    assert len(failures) == 1
    assert isinstance(failures[0], ConnectionError)
    assert successes[0]["id"] in [1, 3]
    assert successes[1]["id"] in [1, 3]
```

### JavaScript - Jest mocks

```javascript
import { fetchUsersParallel } from './fetcher';
import { fetchUser } from './api';

jest.mock('./api');

describe('fetchUsersParallel', () => {
  test('returns all successful results', async () => {
    fetchUser.mockImplementation(async (uid) => ({
      id: uid,
      name: `User ${uid}`,
    }));

    const { successes, failures } = await fetchUsersParallel([1, 2, 3]);

    expect(successes).toHaveLength(3);
    expect(failures).toHaveLength(0);
    expect(fetchUser).toHaveBeenCalledTimes(3);
  });

  test('handles partial failures', async () => {
    fetchUser.mockImplementation(async (uid) => {
      if (uid === 2) {
        throw new Error('Network error');
      }
      return { id: uid, name: `User ${uid}` };
    });

    const { successes, failures } = await fetchUsersParallel([1, 2, 3]);

    expect(successes).toHaveLength(2);
    expect(failures).toHaveLength(1);
    expect(failures[0].message).toBe('Network error');
  });
});
```

---

## Pattern 3: Testing Timeouts

### Python

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_fetch_with_timeout_returns_none_on_timeout():
    """Test timeout returns None instead of raising."""
    async def slow_fetch():
        await asyncio.sleep(10)  # Takes 10 seconds
        return "data"

    with patch("app.fetcher.fetch_data", slow_fetch):
        from app.fetcher import fetch_with_timeout
        # Timeout after 0.1 seconds
        result = await fetch_with_timeout("http://example.com", timeout=0.1)

    assert result is None


@pytest.mark.asyncio
async def test_fetch_with_timeout_returns_data_when_fast():
    """Test successful fetch within timeout."""
    async def fast_fetch():
        await asyncio.sleep(0.01)
        return "success"

    with patch("app.fetcher.fetch_data", fast_fetch):
        from app.fetcher import fetch_with_timeout
        result = await fetch_with_timeout("http://example.com", timeout=1.0)

    assert result == "success"
```

### JavaScript

```javascript
describe('fetchWithTimeout', () => {
  test('returns null on timeout', async () => {
    const slowFetch = () => new Promise(r => setTimeout(() => r('data'), 10000));

    jest.spyOn(global, 'fetch').mockImplementation(slowFetch);

    const result = await fetchWithTimeout('http://example.com', 100);

    expect(result).toBeNull();
  });

  test('returns data when fast enough', async () => {
    const fastFetch = () => Promise.resolve({
      json: async () => ({ data: 'success' })
    });

    jest.spyOn(global, 'fetch').mockImplementation(fastFetch);

    const result = await fetchWithTimeout('http://example.com', 1000);

    expect(result).toEqual({ data: 'success' });
  });
});
```

---

## Pattern 4: Testing Cancellation

### Python

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_task_cleanup_on_cancellation():
    """Test task performs cleanup when cancelled."""
    cleanup_called = False

    async def cancellable_task():
        nonlocal cleanup_called
        try:
            await asyncio.sleep(10)
        except asyncio.CancelledError:
            cleanup_called = True
            raise

    task = asyncio.create_task(cancellable_task())
    await asyncio.sleep(0.1)  # Let task start
    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task

    assert cleanup_called
```

### JavaScript

```javascript
describe('cancellation', () => {
  test('task performs cleanup on abort', async () => {
    let cleanupCalled = false;

    async function cancellableTask(signal) {
      try {
        await new Promise((resolve, reject) => {
          signal.addEventListener('abort', () => reject(new Error('Aborted')));
          setTimeout(resolve, 10000);
        });
      } catch (error) {
        if (error.message === 'Aborted') {
          cleanupCalled = true;
        }
        throw error;
      }
    }

    const controller = new AbortController();
    const promise = cancellableTask(controller.signal);

    setTimeout(() => controller.abort(), 100);

    await expect(promise).rejects.toThrow('Aborted');
    expect(cleanupCalled).toBe(true);
  });
});
```

---

## Pattern 5: Testing Retry Logic

### Python

```python
import pytest
import asyncio
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_retry_succeeds_after_failures():
    """Test retry logic eventually succeeds."""
    attempt = 0

    async def flaky_function():
        nonlocal attempt
        attempt += 1
        if attempt < 3:
            raise ConnectionError("Network error")
        return "success"

    result = await retry_with_backoff(
        flaky_function,
        max_retries=5,
        base_delay=0.01  # Fast for testing
    )

    assert result == "success"
    assert attempt == 3


@pytest.mark.asyncio
async def test_retry_fails_after_max_attempts():
    """Test retry exhausts all attempts and raises."""
    async def always_fails():
        raise ValueError("Always fails")

    with pytest.raises(ValueError, match="Always fails"):
        await retry_with_backoff(
            always_fails,
            max_retries=3,
            base_delay=0.01
        )
```

### JavaScript

```javascript
describe('retryWithBackoff', () => {
  test('succeeds after failures', async () => {
    let attempt = 0;

    const flakyFunction = async () => {
      attempt++;
      if (attempt < 3) {
        throw new Error('Network error');
      }
      return 'success';
    };

    const result = await retryWithBackoff(flakyFunction, {
      maxRetries: 5,
      baseDelay: 10,
    });

    expect(result).toBe('success');
    expect(attempt).toBe(3);
  });

  test('fails after max attempts', async () => {
    const alwaysFails = async () => {
      throw new Error('Always fails');
    };

    await expect(
      retryWithBackoff(alwaysFails, {
        maxRetries: 3,
        baseDelay: 10,
      })
    ).rejects.toThrow('Always fails');
  });
});
```

---

## Pattern 6: Testing Concurrent Operations

### Python

```python
import pytest
import asyncio
from unittest.mock import AsyncMock, call

@pytest.mark.asyncio
async def test_concurrent_execution():
    """Test operations run concurrently, not sequentially."""
    mock_operation = AsyncMock(side_effect=lambda x: asyncio.sleep(0.1))

    start_time = asyncio.get_event_loop().time()

    # Run 3 operations concurrently
    await asyncio.gather(
        mock_operation(1),
        mock_operation(2),
        mock_operation(3)
    )

    elapsed_time = asyncio.get_event_loop().time() - start_time

    # Should take ~0.1s (concurrent), not ~0.3s (sequential)
    assert elapsed_time < 0.2
    assert mock_operation.call_count == 3


@pytest.mark.asyncio
async def test_semaphore_limits_concurrency():
    """Test semaphore enforces concurrency limit."""
    active_count = 0
    max_active = 0

    async def task():
        nonlocal active_count, max_active
        active_count += 1
        max_active = max(max_active, active_count)
        await asyncio.sleep(0.1)
        active_count -= 1

    semaphore = asyncio.Semaphore(3)

    async def bounded_task():
        async with semaphore:
            await task()

    # Create 10 tasks
    await asyncio.gather(*[bounded_task() for _ in range(10)])

    # Max concurrent should never exceed 3
    assert max_active == 3
```

### JavaScript

```javascript
describe('concurrent operations', () => {
  test('run concurrently, not sequentially', async () => {
    const operation = jest.fn(async (x) => {
      await new Promise(r => setTimeout(r, 100));
    });

    const startTime = Date.now();

    await Promise.all([
      operation(1),
      operation(2),
      operation(3),
    ]);

    const elapsedTime = Date.now() - startTime;

    // Should take ~100ms (concurrent), not ~300ms (sequential)
    expect(elapsedTime).toBeLessThan(200);
    expect(operation).toHaveBeenCalledTimes(3);
  });
});
```

---

## Pattern 7: Time Manipulation for Testing

### Python - pytest-freezegun

```bash
pip install freezegun
```

```python
import pytest
import asyncio
from freezegun import freeze_time
from datetime import datetime, timedelta

@pytest.mark.asyncio
@freeze_time("2024-01-01 12:00:00")
async def test_cache_expiration():
    """Test cache expires after TTL."""
    cache = AsyncCache(ttl_seconds=60)

    # Add item to cache
    await cache.set("key", "value")

    # Item should be in cache
    assert await cache.get("key") == "value"

    # Fast-forward time by 61 seconds
    with freeze_time("2024-01-01 12:01:01"):
        # Item should be expired
        assert await cache.get("key") is None
```

### JavaScript - jest.useFakeTimers

```javascript
describe('cache expiration', () => {
  test('cache expires after TTL', async () => {
    jest.useFakeTimers();

    const cache = new AsyncCache({ ttlMs: 60000 });

    await cache.set('key', 'value');
    expect(await cache.get('key')).toBe('value');

    // Fast-forward time by 61 seconds
    jest.advanceTimersByTime(61000);

    expect(await cache.get('key')).toBeNull();

    jest.useRealTimers();
  });
});
```

---

## Pattern 8: Testing Resource Cleanup

### Python

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_connection_closed_after_error():
    """Test connection is closed even when error occurs."""
    connection = MockConnection()

    with pytest.raises(ValueError):
        async with get_db_connection(connection):
            raise ValueError("Simulated error")

    assert connection.closed


@pytest.mark.asyncio
async def test_connection_closed_after_success():
    """Test connection is closed after successful operation."""
    connection = MockConnection()

    async with get_db_connection(connection):
        await connection.execute("SELECT 1")

    assert connection.closed


class MockConnection:
    def __init__(self):
        self.closed = False
        self.connected = False

    async def connect(self):
        self.connected = True

    async def close(self):
        self.closed = True

    async def execute(self, query):
        return []
```

---

## Testing Best Practices

### 1. Use Fast Timeouts in Tests

```python
# Don't wait 5 seconds in tests
@pytest.mark.asyncio
async def test_timeout_bad():
    await fetch_with_timeout(url, timeout=5.0)  # Slow!

# Use short timeouts
@pytest.mark.asyncio
async def test_timeout_good():
    await fetch_with_timeout(url, timeout=0.1)  # Fast!
```

### 2. Mock External Dependencies

```python
# Don't make real network calls in tests
@pytest.mark.asyncio
async def test_bad():
    result = await fetch("https://api.example.com")  # Slow, flaky!

# Mock external calls
@pytest.mark.asyncio
async def test_good():
    with patch("app.fetch") as mock_fetch:
        mock_fetch.return_value = {"data": "test"}
        result = await fetch("https://api.example.com")
```

### 3. Test Both Success and Failure Cases

```python
@pytest.mark.asyncio
async def test_fetch_success():
    """Test successful API call."""
    result = await fetch_user(123)
    assert result["id"] == 123

@pytest.mark.asyncio
async def test_fetch_network_error():
    """Test handling of network errors."""
    with patch("app.api.http_get", side_effect=ConnectionError):
        with pytest.raises(ConnectionError):
            await fetch_user(123)

@pytest.mark.asyncio
async def test_fetch_timeout():
    """Test handling of timeouts."""
    with patch("app.api.http_get", side_effect=asyncio.TimeoutError):
        result = await fetch_user_safe(123)
        assert result is None
```

### 4. Use Fixtures for Common Setup

```python
@pytest.fixture
async def mock_api_client():
    """Fixture providing mocked API client."""
    client = AsyncMock()
    client.get.return_value = {"data": "test"}
    return client

@pytest.mark.asyncio
async def test_with_fixture(mock_api_client):
    """Test using fixture."""
    result = await fetch_data(mock_api_client, "/endpoint")
    assert result["data"] == "test"
```

---

## Running Tests

### Python

```bash
# Run all async tests
pytest tests/ -v --asyncio-mode=auto

# Run with coverage
pytest --cov=app --cov-report=term-missing

# Run specific test
pytest tests/test_async.py::test_fetch_users_parallel -v

# Run with markers
pytest -m asyncio -v
```

### JavaScript

```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test
npm test -- tests/async.test.js

# Run in watch mode
npm test -- --watch
```

---

## Debugging Async Tests

### Python - Print Statements

```python
@pytest.mark.asyncio
async def test_with_debug():
    print(f"Starting test at {datetime.now()}")
    result = await some_function()
    print(f"Result: {result}")
    assert result == expected
```

### Python - pdb Debugger

```python
@pytest.mark.asyncio
async def test_with_debugger():
    import pdb; pdb.set_trace()
    result = await some_function()
    assert result == expected
```

### JavaScript - console.log

```javascript
test('with debug', async () => {
  console.log('Starting test');
  const result = await someFunction();
  console.log('Result:', result);
  expect(result).toBe(expected);
});
```

---

## Common Test Issues

### Issue 1: Test Hangs

**Cause**: Forgot to await async call

```python
# ❌ BAD - Test hangs
@pytest.mark.asyncio
async def test_hangs():
    result = fetch_data()  # Missing await!
    assert result == "data"

# ✅ GOOD
@pytest.mark.asyncio
async def test_works():
    result = await fetch_data()
    assert result == "data"
```

### Issue 2: Unhandled Exceptions in Background Tasks

```python
# ❌ BAD - Background task exception not caught
@pytest.mark.asyncio
async def test_bad():
    asyncio.create_task(failing_task())
    await asyncio.sleep(0.1)
    # Test passes but task failed

# ✅ GOOD - Await and handle task
@pytest.mark.asyncio
async def test_good():
    task = asyncio.create_task(failing_task())
    with pytest.raises(ValueError):
        await task
```

### Issue 3: Race Conditions in Tests

```python
# ❌ BAD - Race condition
@pytest.mark.asyncio
async def test_race():
    asyncio.create_task(update_value())
    # May or may not be updated yet
    assert value == expected

# ✅ GOOD - Properly synchronize
@pytest.mark.asyncio
async def test_synchronized():
    await update_value()
    assert value == expected
```
