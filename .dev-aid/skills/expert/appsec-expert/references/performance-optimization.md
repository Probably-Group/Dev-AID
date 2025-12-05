# Performance Optimization Patterns for Security

## Overview

Security scanning and testing can be resource-intensive. These patterns optimize performance while maintaining security effectiveness.

---

## Pattern 1: Incremental Scanning

**Problem**: Full codebase scans are slow for large codebases and create bottlenecks in CI/CD.

**Solution**: Scan only changed files to reduce analysis time.

```python
# Good: Scan only changed files
def incremental_sast_scan(changed_files: list[str]) -> list:
    """Scan only files that changed in current commit"""
    results = []
    for file_path in changed_files:
        if file_path.endswith(('.py', '.js', '.ts')):
            results.extend(run_semgrep(file_path))
    return results

# Bad: Full codebase scan on every commit
def full_scan():
    return run_semgrep(".")  # Slow for large codebases
```

**Benefits**:
- 10-100x faster for incremental commits
- Faster feedback in CI/CD pipeline
- Reduced resource consumption

**Implementation**:
```bash
# Get changed files in CI
git diff --name-only HEAD~1 HEAD > changed_files.txt
semgrep --config=auto $(cat changed_files.txt)
```

---

## Pattern 2: Cache Security Results

**Problem**: Re-scanning unchanged files wastes CPU cycles and time.

**Solution**: Cache scan results keyed by file content hash.

```python
# Good: Cache scan results with file hash
import hashlib
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_vulnerability_check(file_hash: str, rule_version: str):
    """Cache results by file content hash and rule version"""
    return run_security_scan(file_hash)

def scan_with_cache(file_path: str):
    content = Path(file_path).read_bytes()
    file_hash = hashlib.sha256(content).hexdigest()
    return cached_vulnerability_check(file_hash, RULE_VERSION)

# Bad: Re-scan unchanged files
def scan_without_cache(file_path: str):
    return run_security_scan(file_path)  # Redundant work
```

**Cache Invalidation**:
- Invalidate when file content changes (hash mismatch)
- Invalidate when security rules update (rule_version change)
- Set reasonable TTL (e.g., 24 hours for CI cache)

**Benefits**:
- 50-90% reduction in scan time for unchanged code
- Lower CI/CD costs
- Faster developer feedback

---

## Pattern 3: Parallel Security Analysis

**Problem**: Sequential file scanning doesn't utilize available CPU cores.

**Solution**: Process multiple files concurrently using thread pools.

```python
# Good: Parallel scanning with thread pool
from concurrent.futures import ThreadPoolExecutor

def parallel_security_scan(files: list[str], max_workers: int = 4):
    """Scan files in parallel using thread pool"""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(scan_single_file, files))
    return [r for r in results if r]

# Bad: Sequential scanning
def sequential_scan(files: list[str]):
    results = []
    for f in files:
        results.append(scan_single_file(f))  # Slow
    return results
```

**Thread Pool Sizing**:
```python
import os

# Auto-detect optimal worker count
def get_optimal_workers():
    cpu_count = os.cpu_count() or 1
    # Use CPU count - 1 to leave one core free
    return max(1, cpu_count - 1)

max_workers = get_optimal_workers()
```

**Benefits**:
- Near-linear speedup with available cores
- 4x faster on quad-core machines
- Better resource utilization

---

## Pattern 4: Targeted Security Audits

**Problem**: Deep scanning every file equally wastes time on low-risk code.

**Solution**: Focus deep analysis on high-risk areas (auth, crypto, SQL, exec).

```python
# Good: Focus on high-risk areas
HIGH_RISK_PATTERNS = ['auth', 'crypto', 'sql', 'exec', 'eval']

def targeted_audit(codebase_path: str):
    """Focus deep scanning on high-risk code"""
    high_risk_files = []
    for pattern in HIGH_RISK_PATTERNS:
        high_risk_files.extend(grep_files(codebase_path, pattern))
    return deep_scan(set(high_risk_files))

# Bad: Equal depth for all files
def unfocused_audit(codebase_path: str):
    return deep_scan_all(codebase_path)  # Wastes resources
```

**Risk-Based Scanning Strategy**:
```python
RISK_LEVELS = {
    'critical': ['auth', 'crypto', 'password', 'jwt', 'token'],
    'high': ['sql', 'query', 'exec', 'eval', 'subprocess'],
    'medium': ['upload', 'file', 'path', 'url', 'redirect'],
    'low': ['static', 'config', 'constants']
}

def risk_based_scan(codebase_path: str):
    results = {}
    for risk_level, patterns in RISK_LEVELS.items():
        files = find_files_with_patterns(codebase_path, patterns)
        scan_depth = get_scan_depth(risk_level)
        results[risk_level] = scan_files(files, depth=scan_depth)
    return results
```

**Benefits**:
- 3-5x faster audits
- More thorough analysis of critical code
- Better ROI on security testing time

---

## Pattern 5: Resource Limits for Scanning

**Problem**: Security tools can consume excessive memory/CPU, causing CI failures.

**Solution**: Set resource limits to prevent runaway processes.

```python
# Good: Set resource limits
import resource
import signal

def scan_with_limits(file_path: str):
    """Scan with memory and CPU time limits"""
    # Limit memory to 512MB
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, -1))
    # Limit CPU time to 30 seconds
    resource.setrlimit(resource.RLIMIT_CPU, (30, 30))

    try:
        return run_analysis(file_path)
    except MemoryError:
        return {"error": "File too large to analyze"}

# Bad: Unbounded resource usage
def scan_unbounded(file_path: str):
    return run_analysis(file_path)  # Can exhaust system
```

**Timeout Handling**:
```python
import signal

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Analysis timed out")

def scan_with_timeout(file_path: str, timeout_seconds: int = 60):
    """Scan with timeout protection"""
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)

    try:
        result = run_analysis(file_path)
        signal.alarm(0)  # Cancel alarm
        return result
    except TimeoutException:
        return {"error": f"Analysis exceeded {timeout_seconds}s timeout"}
```

**Benefits**:
- Prevents CI/CD pipeline hangs
- Predictable resource usage
- Graceful handling of complex files

---

## Performance Metrics to Track

### Scan Time Metrics
```python
import time

def measure_scan_performance(files: list[str]):
    """Track scan performance metrics"""
    start = time.time()
    results = scan_files(files)
    duration = time.time() - start

    return {
        'files_scanned': len(files),
        'duration_seconds': duration,
        'files_per_second': len(files) / duration,
        'vulnerabilities_found': count_vulnerabilities(results)
    }
```

### Key Performance Indicators (KPIs)
- **Scan time per file**: Target < 500ms per file
- **CI/CD overhead**: Target < 5 minutes added to pipeline
- **Cache hit rate**: Target > 70% for incremental builds
- **False positive rate**: Target < 10% of findings

---

## Best Practices Summary

1. **Incremental > Full**: Always prefer incremental scans
2. **Cache Results**: Hash-based caching with version tracking
3. **Parallelize**: Use all available CPU cores
4. **Target High-Risk**: Focus on authentication, crypto, SQL, exec
5. **Set Limits**: Memory, CPU, and time limits prevent hangs
6. **Measure Performance**: Track metrics and optimize bottlenecks

---

## Tool-Specific Optimization

### Semgrep
```bash
# Fast: Scan only Python files with critical rules
semgrep --config=p/security-audit --include="*.py" --max-target-bytes=1MB

# Faster: Use specific rule sets
semgrep --config=p/owasp-top-ten --config=p/jwt
```

### Bandit
```bash
# Fast: Skip low-confidence findings
bandit -r . -ll -ii

# Faster: Exclude test files
bandit -r . --exclude=/test/
```

### pip-audit
```bash
# Fast: Check only production dependencies
pip-audit --require-hashes --no-deps
```

### Gitleaks
```bash
# Fast: Scan only uncommitted changes
gitleaks detect --no-git --source=.

# Faster: Use baseline to ignore known issues
gitleaks detect --baseline-path=gitleaks-baseline.json
```
