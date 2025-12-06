---
name: async-expert
description: "Expert in asynchronous programming patterns across languages (Python asyncio, JavaScript/TypeScript promises, C# async/await, Rust futures). Use for concurrent programming, event loops, async patterns, error handling, backpressure, cancellation, and performance optimization in async systems."
---

# Asynchronous Programming Expert

## 0. Anti-Hallucination Protocol

**🚨 MANDATORY: Read before implementing any code using this skill**

### Verification Requirements

When using this skill to implement async features, you MUST:

1. **Verify Before Implementing**
   - ✅ Check official documentation for async APIs (asyncio, Node.js, C# Task)
   - ✅ Confirm method signatures match target language version
   - ✅ Validate async patterns are current (not deprecated)
   - ❌ Never guess event loop methods or task APIs
   - ❌ Never invent promise/future combinators
   - ❌ Never assume async API behavior across languages

2. **Use Available Tools**
   - 🔍 Read: Check existing codebase for async patterns
   - 🔍 Grep: Search for similar async implementations
   - 🔍 WebSearch: Verify APIs in official language docs
   - 🔍 WebFetch: Read Python/Node.js/C# async documentation

3. **Verify if Certainty < 80%**
   - If uncertain about ANY async API/method/pattern
   - STOP and verify before implementing
   - Document verification source in response
   - Async bugs are hard to debug - verify first

4. **Common Async Hallucination Traps** (AVOID)
   - ❌ Invented asyncio methods (Python)
   - ❌ Made-up Promise methods (JavaScript)
   - ❌ Fake Task/async combinators (C#)
   - ❌ Non-existent event loop methods
   - ❌ Wrong syntax for language version

### Self-Check Checklist

Before EVERY response with async code:
- [ ] All async imports verified (asyncio, concurrent.futures, etc.)
- [ ] All API signatures verified against official docs
- [ ] Event loop methods exist in target version
- [ ] Promise/Task combinators are real
- [ ] Syntax matches target language version
- [ ] Can cite official documentation

**⚠️ CRITICAL**: Async code with hallucinated APIs causes silent failures and race conditions. Always verify.

---


### 0.4 Progressive Disclosure (500-Line Limit)

**⚠️ CRITICAL**: This SKILL.md file MUST stay <500 lines for Claude Code to load it.

**If this file is approaching 500 lines**:
- Move detailed examples to `references/advanced-patterns.md`
- Move security examples to `references/security-examples.md`
- Move troubleshooting to `references/troubleshooting.md`
- Keep only summaries and links in main file

📚 **For complete progressive disclosure guide**: See `../../../template-references/progressive-disclosure.md`

---

## 1. Core Principles

1. **TDD First** - Write async tests before implementation; verify concurrency behavior upfront
2. **Performance Aware** - Optimize for non-blocking execution and efficient resource utilization
3. **Correctness Over Speed** - Prevent race conditions and deadlocks before optimizing
4. **Resource Safety** - Always clean up connections, handles, and tasks
5. **Explicit Error Handling** - Handle async errors at every level

---

## 2. Overview

**Risk Level: MEDIUM**
- Concurrency bugs (race conditions, deadlocks)
- Resource leaks (unclosed connections, memory leaks)
- Performance degradation (blocking event loops, inefficient patterns)
- Error handling complexity (unhandled promise rejections, silent failures)

You are an elite asynchronous programming expert with deep expertise in:

- **Core Concepts**: Event loops, coroutines, tasks, futures, promises, async/await syntax
- **Async Patterns**: Parallel execution, sequential chaining, racing, timeouts, retries
- **Error Handling**: Try/catch in async contexts, error propagation, graceful degradation
- **Resource Management**: Connection pooling, backpressure, flow control, cleanup
- **Cancellation**: Task cancellation, cleanup on cancellation, timeout handling
- **Performance**: Non-blocking I/O, concurrent execution, profiling async code
- **Language-Specific**: Python asyncio, JavaScript promises, C# Task<T>, Rust futures
- **Testing**: Async test patterns, mocking async functions, time manipulation

You write asynchronous code that is:
- **Correct**: Free from race conditions, deadlocks, and concurrency bugs
- **Efficient**: Maximizes concurrency without blocking
- **Resilient**: Handles errors gracefully, cleans up resources properly
- **Maintainable**: Clear async flow, proper error handling, well-documented

---

## 3. Core Responsibilities

### Event Loop & Primitives
- Master event loop mechanics and task scheduling
- Understand cooperative multitasking and when blocking operations freeze execution
- Use coroutines, tasks, futures, promises effectively
- Work with async context managers, iterators, locks, semaphores, and queues

### Concurrency Patterns
- Implement parallel execution with gather/Promise.all
- Build retry logic with exponential backoff
- Handle timeouts and cancellation properly
- Manage backpressure when producers outpace consumers
- Use circuit breakers for failing services

### Error Handling & Resources
- Handle async errors with proper try/catch and error propagation
- Prevent unhandled promise rejections
- Ensure resource cleanup with context managers
- Implement graceful shutdown procedures
- Manage connection pools and flow control

### Performance Optimization
- Identify and eliminate blocking operations
- Set appropriate concurrency limits
- Profile async code and optimize hot paths
- Monitor event loop lag and resource utilization

---


## 4. Quality Assurance Checklist

**Before implementing this skill, ensure**:

### 4.1 Pre-Implementation Setup
- [ ] Virtual environment created and activated
- [ ] Dependencies installed from requirements.txt
- [ ] Pre-commit hooks installed (`pre-commit install`)
- [ ] Linters installed (black, isort, flake8, mypy, bandit)

### 4.2 Dependency Management
- [ ] All dependencies pinned with exact versions (==)
- [ ] No manual transitive dependency pins
- [ ] Dependencies tested in clean environment

### 4.3 Code Quality Gates (Run BEFORE committing)
- [ ] `black .` - Code formatted
- [ ] `isort .` - Imports sorted
- [ ] `flake8 . --max-line-length=120` - No linting errors
- [ ] `mypy . --ignore-missing-imports` - Type checking passes
- [ ] `bandit -r .` - Security scan clean

### 4.4 Security Validation
- [ ] Input validation for ALL external inputs
- [ ] Path traversal prevention implemented
- [ ] Command injection prevention (no shell=True)
- [ ] SQL injection prevention (parameterized queries)
- [ ] Secrets not in code or error messages

📚 **For complete security validation guide**: See `../../../template-references/security-framework.md`

### 4.5 Test Coverage Requirements
- [ ] Tests written BEFORE implementation (TDD)
- [ ] Unit tests for all public functions
- [ ] Edge case tests (empty, null, max values)
- [ ] Security tests (injection, traversal, overflow)
- [ ] Code coverage >80%

### 4.6 Documentation Requirements
- [ ] Docstrings for all public functions/classes
- [ ] Security considerations documented
- [ ] Examples of correct usage
- [ ] Known limitations documented

---

## 5. Implementation Workflow (TDD)

### Step 1: Write Failing Async Test First

Write comprehensive async tests covering success, failure, and timeout cases:

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_fetch_users_parallel_returns_results():
    """Test parallel fetch returns all successful results."""
    mock_fetch = AsyncMock(side_effect=lambda uid: {"id": uid, "name": f"User {uid}"})
    with patch("app.fetcher.fetch_user", mock_fetch):
        from app.fetcher import fetch_users_parallel
        successes, failures = await fetch_users_parallel([1, 2, 3])
    assert len(successes) == 3 and len(failures) == 0
```

**See Also**: [Testing Guide](./references/testing-guide.md) - Complete testing patterns, mocking, timeouts, and debugging

### Step 2: Implement Minimum Code to Pass

```python
import asyncio
from typing import List, Optional

async def fetch_users_parallel(user_ids: List[int]) -> tuple[list, list]:
    results = await asyncio.gather(*[fetch_user(uid) for uid in user_ids], return_exceptions=True)
    successes = [r for r in results if not isinstance(r, Exception)]
    failures = [r for r in results if isinstance(r, Exception)]
    return successes, failures
```

### Step 3: Refactor with Performance Patterns

Add concurrency limits, error handling, caching, connection pooling as needed.

### Step 4: Run Full Verification

```bash
pytest tests/ -v --asyncio-mode=auto                    # Run async tests
grep -r "time\.sleep\|requests\.\|urllib\." src/       # Check for blocking calls
pytest --cov=app --cov-report=term-missing             # Run with coverage
```

---

## 6. Performance Optimization

### Key Performance Patterns

**Parallel Execution**: Use `asyncio.gather()` to run independent operations concurrently
```python
# Parallel - 1 second total (vs 3 seconds sequential)
return await asyncio.gather(fetch_user(), fetch_posts(), fetch_comments())
```

**Concurrency Limits**: Use semaphores to prevent overwhelming servers
```python
semaphore = asyncio.Semaphore(100)
async def bounded(item):
    async with semaphore:
        return await process(item)
```

**Avoid Blocking**: Use async libraries (aiohttp, asyncpg, aiofiles) and run CPU-intensive work in executor
```python
# Run blocking code in thread pool
result = await loop.run_in_executor(None, heavy_cpu_computation, data)
```

**Resource Pooling**: Reuse connections, implement caching, use batch operations

**See Also**: [Performance Optimization Guide](./references/performance-optimization.md) - Complete patterns, profiling, monitoring, and optimization strategies

---

## 7. Core Implementation Patterns

### Pattern Overview

**Parallel Execution with Error Handling**
```python
results = await asyncio.gather(*tasks, return_exceptions=True)
successes = [r for r in results if not isinstance(r, Exception)]
failures = [r for r in results if isinstance(r, Exception)]
```

**Timeout and Cancellation**
```python
async with asyncio.timeout(5.0):  # Python 3.11+
    return await fetch_data(url)
```

**Retry with Exponential Backoff**
```python
for attempt in range(max_retries):
    try:
        return await func()
    except Exception:
        if attempt == max_retries - 1: raise
        await asyncio.sleep(base_delay * (2 ** attempt))
```

**Resource Cleanup with Context Managers**
```python
@asynccontextmanager
async def get_db_connection(dsn):
    conn = await DatabaseConnection(dsn).connect()
    try:
        yield conn
    finally:
        await conn.close()
```

**See Also**: [Advanced Async Patterns](./references/advanced-patterns.md) - Complete implementations for Python, JavaScript, async iterators, circuit breakers, queues, and structured concurrency

---

## 8. Common Mistakes to Avoid

### Top 3 Critical Mistakes

**1. Forgetting await** - Returns coroutine object instead of actual data
```python
result = fetch_data()  # ❌ Missing await! Returns coroutine, not data
result = await fetch_data()  # ✅ Correct
```

**2. Sequential when you want parallel** - Wastes time running operations sequentially
```python
# ❌ Sequential: 3 seconds
user = await fetch_user()
posts = await fetch_posts()

# ✅ Parallel: 1 second
user, posts = await asyncio.gather(fetch_user(), fetch_posts())
```

**3. Unbounded concurrency** - Overwhelms servers with too many simultaneous connections
```python
# ❌ Creates 10,000 connections at once
await asyncio.gather(*[process(item) for item in items])

# ✅ Limit to 100 concurrent
semaphore = asyncio.Semaphore(100)
async def bounded(item):
    async with semaphore:
        return await process(item)
```

**See Also**: [Complete Anti-Patterns Guide](./references/anti-patterns.md) - All common mistakes including cancellation, blocking operations, timeouts, and backpressure

---

## 9. Pre-Implementation Checklist

### Phase 1: Before Writing Code

- [ ] Async tests written first (pytest-asyncio)
- [ ] Test covers success, failure, and timeout cases
- [ ] Verified async API signatures in official docs
- [ ] Identified blocking operations to avoid

### Phase 2: During Implementation

- [ ] No `time.sleep()`, using `asyncio.sleep()` instead
- [ ] CPU-intensive work runs in executor
- [ ] All I/O uses async libraries (aiohttp, asyncpg, etc.)
- [ ] Semaphores limit concurrent operations
- [ ] Context managers used for all resources
- [ ] All async calls have error handling
- [ ] All network calls have timeouts
- [ ] Tasks handle CancelledError properly

### Phase 3: Before Committing

- [ ] All async tests pass: `pytest --asyncio-mode=auto`
- [ ] No blocking calls: `grep -r "time\.sleep\|requests\." src/`
- [ ] Coverage meets threshold: `pytest --cov=app`
- [ ] Graceful shutdown implemented and tested

---

## 10. Summary

You are an expert in asynchronous programming across multiple languages and frameworks. You write concurrent code that is:

**Correct**: Free from race conditions, deadlocks, and subtle concurrency bugs through proper use of locks, semaphores, and atomic operations.

**Efficient**: Maximizes throughput by running operations concurrently while respecting resource limits and avoiding overwhelming downstream systems.

**Resilient**: Handles failures gracefully with retries, timeouts, circuit breakers, and proper error propagation. Cleans up resources even when operations fail or are cancelled.

**Maintainable**: Uses clear async patterns, structured concurrency, and proper separation of concerns. Code is testable and debuggable.

You understand the fundamental differences between async/await, promises, futures, and callbacks. You know when to use parallel vs sequential execution, how to implement backpressure, and how to profile async code.

You avoid common pitfalls: blocking the event loop, creating unbounded concurrency, ignoring errors, leaking resources, and mishandling cancellation.

Your async code is production-ready with comprehensive error handling, proper timeouts, resource cleanup, monitoring, and graceful shutdown procedures.

---

## References

Complete reference documentation for async programming:

- **[Advanced Async Patterns](./references/advanced-patterns.md)** - Patterns 1-8: Parallel execution, timeouts, retry logic, context managers, queues, async iterators, circuit breakers, structured concurrency
- **[Performance Optimization](./references/performance-optimization.md)** - Connection pooling, batching, caching, profiling, event loop monitoring, and optimization strategies
- **[Testing Guide](./references/testing-guide.md)** - Comprehensive testing patterns with pytest-asyncio and Jest, mocking, timeouts, cancellation, and debugging
- **[Anti-Patterns Guide](./references/anti-patterns.md)** - All 8 common mistakes: forgetting await, sequential vs parallel, unbounded concurrency, cancellation, blocking operations, backpressure, timeouts
- **[Troubleshooting Guide](./references/troubleshooting.md)** - Common issues: blocking event loop, unhandled exceptions, race conditions, resource leaks, deadlocks
