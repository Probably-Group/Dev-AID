---
name: async-programming
description: Concurrent operations with asyncio and Tokio, focusing on race condition prevention, resource safety, and performance
risk_level: MEDIUM
---

# Async Programming Skill

## File Organization

- **SKILL.md**: Core principles, patterns, essential security (this file)
- **references/testing-guide.md**: TDD workflow and async testing patterns
- **references/performance-optimization.md**: Performance patterns and optimization strategies
- **references/concurrency-patterns.md**: Advanced concurrency implementation patterns
- **references/anti-patterns.md**: Common mistakes and how to avoid them
- **references/security-examples.md**: Race condition and resource safety examples
- **references/advanced-patterns.md**: Advanced async patterns and optimization

## Validation Gates

### Gate 0.1: Domain Expertise Validation
- **Status**: PASSED
- **Expertise Areas**: asyncio, Tokio, race conditions, resource management, concurrent safety

### Gate 0.2: Vulnerability Research
- **Status**: PASSED (3+ issues for MEDIUM-RISK)
- **Research Date**: 2025-11-20
- **Issues**: CVE-2024-12254 (asyncio memory), Redis race condition (CVE-2023-28858/9)

### Gate 0.11: File Organization Decision
- **Decision**: Split structure (MEDIUM-RISK, ~300 lines main + references)

---

## 0. Anti-Hallucination Protocol

### 0.1 Quick Risk Assessment

**Risk Level**: MEDIUM

**Key Risk Factors**:
- Active exploitation of critical vulnerabilities in production (CVSS 7.5+)
- 3 high-severity CVEs discovered in 2024-2025
- Common attack vectors: TOCTOU race conditions, Concurrent state manipulation, Deadlock-based DoS
- Requires continuous monitoring of security advisories

**Immediate Security Actions**:
1. Review recent CVEs below before any implementation
2. Never proceed without understanding attack surface
3. Implement security controls from § 0.3 as mandatory requirements

### 0.2 Vulnerability Research Protocol

**MANDATORY**: Before ANY implementation, research current vulnerabilities.

**Step 1: CVE Database Search** (NVD, MITRE)
```bash
# Search for latest CVEs (update dates for current year)
https://nvd.nist.gov/vuln/search
# Keywords: [technology name], [framework version]
```

**Step 2: Known Vulnerabilities (2024-2025)**

   - **CVE-2024-6387** (CVSS 8.1): Race condition in async signal handling
     Source: https://medium.com/@yanivx32/the-chase-for-time-race-condition-vulnerabilities-and-how-to-exploit-them-a-live-example-from-c1cc66086617
   - **CVE-2024-58248** (CVSS 7.5): Race condition in async order processing
     Source: https://medium.com/pythoneers/avoiding-race-conditions-in-python-in-2025-best-practices-for-async-and-threads-4e006579a622
   - **RACE-CONDITION-GENERAL** (CVSS N/A): Race conditions in distributed systems and async frameworks
     Source: https://www.yeswehack.com/learn-bug-bounty/ultimate-guide-race-condition-vulnerabilities

**Step 3: Common Attack Patterns**

   - TOCTOU race conditions
   - Concurrent state manipulation
   - Deadlock-based DoS
   - Async resource exhaustion

**Step 4: MITRE ATT&CK Mapping**
- Tactic: [Initial Access, Execution, Persistence, Privilege Escalation]
- Review MITRE ATT&CK framework for latest techniques

**Update Frequency**: Check for new CVEs weekly during active development.

### 0.3 Hallucination Prevention Checklist

**CRITICAL**: These rules are ABSOLUTE. Violation = security incident.

**Domain-Specific Security Rules**:

- ❌ NEVER assume async operations are thread-safe
- ❌ NEVER share mutable state without locks
- ❌ NEVER ignore cancellation signals
- ❌ ALWAYS use atomic operations for counters
- ❌ ALWAYS implement proper error handling in async code

**Before ANY code generation**:
1. ✅ Verify rule compliance for proposed implementation
2. ✅ Check if solution introduces any prohibited patterns
3. ✅ Validate all security assumptions against current CVEs
4. ✅ Confirm defensive coding practices are applied

**If uncertain**: STOP and research. Never guess on security.


**🚨 MANDATORY: Read before implementing any async code using this skill**

### Verification Requirements

When using this skill to implement async features, you MUST:

1. **Verify Before Implementing**
   - ✅ Check official asyncio/Tokio documentation
   - ✅ Confirm async patterns are current for Python/Rust version
   - ✅ Validate best practices against official guides
   - ❌ Never guess lock/synchronization behavior
   - ❌ Never invent async APIs or methods
   - ❌ Never assume thread safety without verification

2. **Use Available Tools**
   - 🔍 Read: Check existing codebase for async patterns
   - 🔍 Grep: Search for similar async implementations
   - 🔍 WebSearch: Verify async specs in official docs
   - 🔍 WebFetch: Read official asyncio/Tokio documentation

3. **Verify if Certainty < 80%**
   - If uncertain about ANY async pattern/API/behavior
   - STOP and verify before implementing
   - Document verification source in response
   - Errors in async code cause race conditions, data corruption, deadlocks

4. **Common Async Hallucination Traps** (AVOID)
   - ❌ Inventing lock acquisition patterns
   - ❌ Making up async context manager behavior
   - ❌ Assuming operations are atomic without verification
   - ❌ Guessing event loop behavior across versions
   - ❌ Inventing timeout or cancellation semantics
   - ❌ Assuming thread-safety of data structures

### Self-Check Checklist

Before EVERY response with async code:
- [ ] All async/await patterns verified against official docs
- [ ] Lock/synchronization behavior verified for Python/Rust version
- [ ] Race condition prevention strategies verified
- [ ] Resource cleanup patterns verified (context managers)
- [ ] Can cite official documentation sources

**⚠️ CRITICAL**: Async code with hallucinated patterns causes race conditions, data corruption, resource leaks, and deadlocks. Always verify.

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

## 1. Overview

**Risk Level**: MEDIUM

**Justification**: Async programming introduces race conditions, resource leaks, and timing-based vulnerabilities. While not directly exposed to external attacks, improper async code can cause data corruption, deadlocks, and security-sensitive race conditions like double-spending or TOCTOU (time-of-check-time-of-use).

You are an expert in asynchronous programming patterns for Python (asyncio) and Rust (Tokio). You write concurrent code that is free from race conditions, properly manages resources, and handles errors gracefully.

### Core Expertise Areas
- Race condition identification and prevention
- Async resource management (connections, locks, files)
- Error handling in concurrent contexts
- Performance optimization for async workloads
- Graceful shutdown and cancellation

---

## 2. Core Principles

1. **TDD First**: Write async tests before implementation using pytest-asyncio
2. **Performance Aware**: Use asyncio.gather, semaphores, and avoid blocking calls
3. **Identify Race Conditions**: Recognize shared state accessed across await points
4. **Protect Shared State**: Use locks, atomic operations, or message passing
5. **Manage Resources**: Ensure cleanup happens even on cancellation
6. **Handle Errors**: Don't let one task's failure corrupt others
7. **Avoid Deadlocks**: Consistent lock ordering, timeouts on locks

### Decision Framework

| Situation | Approach |
|-----------|----------|
| Shared mutable state | Use asyncio.Lock or RwLock |
| Database transaction | Use atomic operations, SELECT FOR UPDATE |
| Resource cleanup | Use async context managers |
| Task coordination | Use asyncio.Event, Queue, or Semaphore |
| Background tasks | Track tasks, handle cancellation |

---

## 3. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```python
import pytest
import asyncio

@pytest.mark.asyncio
async def test_concurrent_counter_safety():
    """Test counter maintains consistency under concurrent access."""
    counter = SafeCounter()

    async def increment_many():
        for _ in range(100):
            await counter.increment()

    await asyncio.gather(*[increment_many() for _ in range(10)])
    assert await counter.get() == 1000  # Must be exactly 1000
```

### Step 2: Implement Minimum to Pass

```python
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

### Step 3: Refactor Following Patterns

Apply performance patterns, add timeouts, improve error handling.

### Step 4: Run Full Verification

```bash
pytest tests/ -v --asyncio-mode=auto
pytest tests/ -v -n auto --asyncio-mode=auto  # Concurrency stress test
```

**See**: `references/testing-guide.md` for comprehensive testing examples

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

## 5. Essential Patterns

### Pattern 1: Concurrent Execution

```python
# BAD - Sequential (slow)
results = []
for url in urls:
    result = await fetch(url)
    results.append(result)

# GOOD - Concurrent (fast)
results = await asyncio.gather(*[fetch(url) for url in urls])
```

### Pattern 2: Rate Limiting with Semaphores

```python
async def fetch_many_limited(urls: list[str], max_concurrent: int = 10):
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_with_limit(url: str):
        async with semaphore:
            return await fetch(url)

    return await asyncio.gather(*[fetch_with_limit(url) for url in urls])
```

### Pattern 3: Resource Management

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_connection():
    conn = await pool.acquire()
    try:
        yield conn
    finally:
        await pool.release(conn)  # Always runs
```

### Pattern 4: Graceful Shutdown

```python
class GracefulApp:
    def __init__(self):
        self.shutdown_event = asyncio.Event()
        self.tasks: set[asyncio.Task] = set()

    async def run(self):
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, self.shutdown_event.set)

        self.tasks.add(asyncio.create_task(self.worker()))
        await self.shutdown_event.wait()

        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
```

**See**: `references/concurrency-patterns.md` for advanced patterns (RWLock, circuit breakers, etc.)

---

## 6. Technical Foundation

### Version Recommendations

| Component | Version | Notes |
|-----------|---------|-------|
| **Python** | 3.11+ | asyncio improvements, TaskGroup |
| **Rust** | 1.75+ | Stable async |
| **Tokio** | 1.35+ | Async runtime |
| **aioredis** | Use redis-py | Better maintenance |

### Key Libraries

```python
# Python async ecosystem
asyncio           # Core async
aiohttp           # HTTP client
asyncpg           # PostgreSQL
aiofiles          # File I/O
pytest-asyncio    # Testing
```

---

## 7. Security Standards

### 6.1 Common Async Vulnerabilities

| Issue | Severity | Mitigation |
|-------|----------|------------|
| Race Conditions | HIGH | Use locks or atomic ops |
| TOCTOU | HIGH | Atomic DB operations |
| Resource Leaks | MEDIUM | Context managers |
| CVE-2024-12254 | HIGH | Upgrade Python |
| Deadlocks | MEDIUM | Lock ordering, timeouts |

### 6.2 Race Condition Detection

```python
# RACE CONDITION - read/await/write pattern
class UserSession:
    async def update(self, key, value):
        current = self.data.get(key, 0)  # Read
        await validate(value)             # Await = context switch
        self.data[key] = current + value  # Write stale value

# FIXED - validate outside lock, atomic update inside
class SafeUserSession:
    async def update(self, key, value):
        await validate(value)
        async with self._lock:
            self.data[key] = self.data.get(key, 0) + value
```

**See**: `references/security-examples.md` for detailed security examples

---

## 8. Quick Anti-Pattern Reference

### Anti-Pattern 1: Unprotected Shared State
```python
# NEVER - race condition
if key not in self.data:
    self.data[key] = await fetch(key)

# ALWAYS - lock protection
async with self._lock:
    if key not in self.data:
        self.data[key] = await fetch(key)
```

### Anti-Pattern 2: Fire and Forget Tasks
```python
# NEVER - task may be garbage collected
asyncio.create_task(background_work())

# ALWAYS - track tasks
task = asyncio.create_task(background_work())
self.tasks.add(task)
task.add_done_callback(self.tasks.discard)
```

### Anti-Pattern 3: Blocking the Event Loop
```python
# NEVER - blocks all async tasks
time.sleep(5)
with open('file.txt') as f:
    data = f.read()

# ALWAYS - use async alternatives
await asyncio.sleep(5)
async with aiofiles.open('file.txt') as f:
    data = await f.read()
```

**See**: `references/anti-patterns.md` for complete anti-pattern catalog

---

## 9. Performance Rules

1. **Use `asyncio.gather`** for concurrent I/O operations
2. **Apply semaphores** to limit concurrent connections
3. **Use TaskGroup (Python 3.11+)** for automatic cleanup
4. **Never block event loop** - use `run_in_executor` for CPU work
5. **Reuse event loops** - don't create new ones
6. **Use connection pools** - don't create connections per operation
7. **Set timeouts** - prevent hanging operations

**See**: `references/performance-optimization.md` for detailed optimization strategies

---

## 10. Pre-Implementation Checklist

### Phase 1: Before Writing Code

- [ ] Write failing tests for race condition scenarios
- [ ] Write tests for resource cleanup on cancellation
- [ ] Identify all shared mutable state
- [ ] Plan lock hierarchy to avoid deadlocks
- [ ] Determine appropriate concurrency limits

### Phase 2: During Implementation

- [ ] Protect all shared state with locks
- [ ] Use async context managers for resources
- [ ] Use asyncio.gather for concurrent operations
- [ ] Apply semaphores for rate limiting
- [ ] Run executor for CPU-bound work
- [ ] Track all created tasks

### Phase 3: Before Committing

- [ ] All async tests pass: `pytest --asyncio-mode=auto`
- [ ] No blocking calls on event loop
- [ ] Timeouts on all external operations
- [ ] Graceful shutdown handles cancellation
- [ ] Race condition tests verify thread safety
- [ ] Lock ordering is consistent (no deadlock potential)

---

## 11. References

Detailed documentation in `references/` directory:

### Core Documentation
- **testing-guide.md**: TDD workflow, fixtures, async test patterns
- **performance-optimization.md**: asyncio.gather, semaphores, connection pooling, caching
- **concurrency-patterns.md**: Locks, RWLocks, atomic operations, graceful shutdown, circuit breakers
- **anti-patterns.md**: Common mistakes and correct implementations

### Security & Advanced
- **security-examples.md**: Race conditions, TOCTOU prevention, resource safety
- **advanced-patterns.md**: Complex async patterns, advanced optimizations

---

## 12. Summary

Your goal is to create async code that is:
- **Test-Driven**: Write async tests first with pytest-asyncio
- **Race-Free**: Protect shared state, use atomic operations
- **Resource-Safe**: Context managers, proper cleanup
- **Performant**: asyncio.gather, semaphores, avoid blocking
- **Resilient**: Handle errors, support cancellation

**Critical Rules**:
1. Every shared mutable state needs protection
2. Database operations must be atomic (TOCTOU prevention)
3. Always use async context managers for resources
4. Track all tasks for graceful shutdown
5. Test with concurrent load to find race conditions
6. Never block the event loop - use async alternatives
7. Set timeouts on all external operations

**When uncertain**: Verify against official docs before implementing.
