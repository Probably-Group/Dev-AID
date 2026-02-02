# Investigation Patterns

Common debugging patterns organized by error category.

## Error Category Patterns

### 1. NullPointerException / TypeError: Cannot read property 'X' of undefined

**Common Causes:**
- Uninitialized variable
- Missing null check
- Async operation not awaited
- Incorrect API response structure

**Investigation Steps:**
1. Find where the null/undefined value originates
2. Trace backward through the call stack
3. Check if data source (API, DB) returns expected shape
4. Verify initialization order

**Common Fixes:**
- Add null checks / optional chaining
- Initialize with default values
- Add type guards
- Fix async/await usage

---

### 2. Connection Refused / Network Error

**Common Causes:**
- Service not running
- Wrong host/port
- Firewall blocking
- SSL/TLS mismatch
- DNS resolution failure

**Investigation Steps:**
1. Verify service is running: `curl localhost:PORT/health`
2. Check if port is listening: `netstat -an | grep PORT`
3. Test DNS resolution: `nslookup hostname`
4. Check firewall rules
5. Verify SSL certificates if applicable

**Common Fixes:**
- Start the required service
- Fix environment variable for host/port
- Update firewall rules
- Fix SSL configuration

---

### 3. Authentication / Authorization Errors (401, 403)

**Common Causes:**
- Expired token
- Missing token
- Wrong credentials
- Insufficient permissions
- Token not being sent correctly

**Investigation Steps:**
1. Check if token exists in request headers
2. Verify token format (Bearer, etc.)
3. Decode JWT to check expiration
4. Verify user has required permissions
5. Check CORS configuration for browser requests

**Common Fixes:**
- Refresh token before expiration
- Fix header formatting
- Update user permissions
- Fix CORS configuration

---

### 4. Database Errors

**Common Causes:**
- Connection pool exhausted
- Query syntax error
- Constraint violation
- Missing migration
- Deadlock

**Investigation Steps:**
1. Check connection pool status
2. Run query directly in database client
3. Check for constraint violations (unique, foreign key)
4. Verify migrations are up to date
5. Check for long-running transactions

**Common Fixes:**
- Increase connection pool size
- Fix query syntax
- Handle constraint violations
- Run pending migrations
- Fix transaction handling

---

### 5. Race Conditions / Timing Issues

**Symptoms:**
- Intermittent failures
- Works in debugging but fails in production
- Different results with each run

**Investigation Steps:**
1. Add timestamps to all log entries
2. Identify shared mutable state
3. Check for missing await/async
4. Look for order-dependent operations
5. Review concurrent access to resources

**Common Fixes:**
- Add proper locking/mutex
- Use atomic operations
- Fix async/await chains
- Add retry with exponential backoff
- Use transaction isolation

---

### 6. Memory Issues

**Symptoms:**
- OOM (Out of Memory) errors
- Increasing memory usage over time
- Slow response times

**Investigation Steps:**
1. Check for memory leaks (heap snapshots)
2. Look for unbounded collections
3. Check for event listener leaks
4. Review caching strategies
5. Check for circular references

**Common Fixes:**
- Add cleanup for event listeners
- Implement LRU cache bounds
- Fix circular references
- Add pagination for large datasets
- Stream instead of loading all in memory

---

### 7. Build/Compile Errors

**Common Causes:**
- Missing dependency
- Version mismatch
- Type errors
- Circular imports

**Investigation Steps:**
1. Check error message for specific file/line
2. Verify all dependencies installed
3. Check for version conflicts in lock file
4. Look for circular imports
5. Verify TypeScript/compiler configuration

**Common Fixes:**
- Install missing dependency
- Update or pin dependency version
- Fix type errors
- Refactor circular imports
- Update compiler configuration

---

### 8. API Response Errors (400, 500)

**Investigation Steps:**
1. Check request payload format
2. Verify required fields present
3. Check server logs for stack trace
4. Test endpoint with known good data
5. Compare with API documentation

**Common Fixes:**
- Fix request payload format
- Add missing required fields
- Handle server-side validation errors
- Fix data transformation logic

---

## Security-Related Investigation

When debugging involves security:

### Check Security Tools First

```bash
# Check for exposed secrets
gitleaks detect

# Check for vulnerabilities
trivy fs .

# Check for SAST issues
opengrep scan
```

### Security Error Categories

| Error Pattern | Possible Security Issue |
|--------------|------------------------|
| SQL syntax error | SQL injection attempt |
| Path contains ".." | Path traversal attempt |
| Token format invalid | Token manipulation |
| Request body too large | DoS attempt |
| Unexpected character in input | XSS attempt |

---

## Debug Logging Strategy

### What to Log

```
✅ Entry point: function name, key parameters (not secrets)
✅ Decision points: which branch was taken, why
✅ Exit point: return value summary, duration
✅ External calls: service called, request ID, response status
✅ State changes: before/after values
```

### What NOT to Log

```
❌ Passwords, tokens, API keys
❌ PII (emails, names, addresses)
❌ Full request/response bodies in production
❌ Sensitive business logic details
```

### Log Levels

| Level | When to Use |
|-------|-------------|
| ERROR | Something failed, needs attention |
| WARN | Something unexpected, but handled |
| INFO | Significant state changes |
| DEBUG | Detailed execution flow |

---

## Git-Based Investigation

### Find When Bug Was Introduced

```bash
# Binary search for bad commit
git bisect start
git bisect bad HEAD
git bisect good <known-good-commit>
# Then test each commit git bisect suggests

# View changes to specific file
git log -p -- path/to/file.py

# Find who changed a specific line
git blame path/to/file.py
```

### Review Recent Changes

```bash
# Changes since last working state
git diff <last-good-commit>..HEAD

# Changes to affected files only
git diff <last-good-commit>..HEAD -- src/affected/

# Commits touching affected files
git log --oneline -- src/affected/
```

---

## Environment Comparison

When bug appears in one environment but not another:

| Check | Command/Method |
|-------|---------------|
| Environment variables | `env | diff - <other-env>` |
| Package versions | Compare lock files |
| Configuration | Diff config files |
| Database state | Compare relevant tables |
| External service status | Check health endpoints |
| Time/timezone | Verify system time settings |
| Resource limits | Check memory, CPU, disk |

---

## Asking for Help

When to escalate:

1. **3+ fix attempts failed**
2. **No reproduction steps found**
3. **Security implications unclear**
4. **Affects multiple systems**
5. **Time spent > estimated value**

What to include in help request:

```markdown
## Problem
[One sentence description]

## Reproduction Steps
1. [Step 1]
2. [Step 2]
3. [Error occurs]

## Expected vs Actual
- Expected: [X]
- Actual: [Y]

## Investigation So Far
- Hypothesis 1: [X] - Result: [disproved because Y]
- Hypothesis 2: [Z] - Result: [partially confirmed]

## Relevant Code
[Link or snippet]

## Environment
- OS: [X]
- Language version: [X]
- Relevant dependencies: [X]
```
