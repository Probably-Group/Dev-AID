# Security Auditing Performance Patterns

This document contains performance optimization patterns for security auditing implementations.

## 1. Incremental Scanning

**Problem**: Running full security scans on every execution is wasteful and slow.

**Solution**: Track file changes and only scan when dependencies or configurations change.

### Bad Example

```python
# BAD: Full scan every time
def scan_all_dependencies():
    return subprocess.run(['pip-audit', '--format=json'], capture_output=True)
```

### Good Example

```python
# GOOD: Incremental scan based on changes
class IncrementalScanner:
    def scan_if_changed(self, requirements_path: str) -> List[Vulnerability]:
        current_hash = self._hash_file(requirements_path)
        if current_hash == self._last_hash:
            return self._load_cached_results()
        results = self._full_scan(requirements_path)
        self._save_cache(current_hash, results)
        return results
```

**Benefits**:
- Reduces scan time by 90%+ for unchanged files
- Preserves system resources
- Faster CI/CD pipelines

---

## 2. Caching Scan Results

**Problem**: Repeatedly fetching vulnerability information from external APIs is slow and can hit rate limits.

**Solution**: Cache vulnerability data with appropriate TTL (time-to-live).

### Bad Example

```python
# BAD: No caching - fetch every time
def get_vulnerability_info(cve_id: str) -> dict:
    return requests.get(f"https://nvd.nist.gov/vuln/detail/{cve_id}")
```

### Good Example

```python
# GOOD: Cache with TTL
class VulnerabilityCache:
    def get_vulnerability(self, cve_id: str) -> dict:
        if cve_id in self._cache:
            data, timestamp = self._cache[cve_id]
            if datetime.now() - timestamp < self._ttl:
                return data
        data = self._fetch_from_api(cve_id)
        self._cache[cve_id] = (data, datetime.now())
        return data
```

**Recommended TTL**:
- CVE data: 24 hours (NVD updates daily)
- CVSS scores: 7 days (rarely change)
- Dependency metadata: 1 hour

---

## 3. Parallel Analysis

**Problem**: Sequential scanning of multiple projects is slow.

**Solution**: Use thread pools to scan multiple projects concurrently.

### Bad Example

```python
# BAD: Sequential scanning
def scan_multiple_projects(paths: List[str]) -> List[Report]:
    return [scan_project(path) for path in paths]
```

### Good Example

```python
# GOOD: Parallel scanning with thread pool
from concurrent.futures import ThreadPoolExecutor, as_completed

def scan_multiple_projects_parallel(paths: List[str], max_workers: int = 4):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(scan_project, p): p for p in paths}
        return [f.result() for f in as_completed(futures)]
```

**Best Practices**:
- Use `max_workers=4` for I/O-bound scanning
- Use `ProcessPoolExecutor` for CPU-bound analysis
- Monitor memory usage with large workloads

---

## 4. Targeted Audits

**Problem**: Running all security scans on every change wastes resources.

**Solution**: Analyze changed files and only run relevant scans.

### Bad Example

```python
# BAD: Scan everything always
def full_security_audit(project_path: str):
    scan_dependencies(project_path)
    scan_secrets(project_path)
    scan_code_vulnerabilities(project_path)
```

### Good Example

```python
# GOOD: Targeted scans based on changes
def targeted_security_audit(project_path: str, changed_files: List[str]):
    scans_needed = set()
    for file in changed_files:
        if file.endswith(('requirements.txt', 'package.json')):
            scans_needed.add('dependencies')
        elif file.endswith(('.env', '.yml', '.yaml')):
            scans_needed.add('secrets')
        elif file.endswith(('.py', '.js', '.ts')):
            scans_needed.add('code')
    # Only run needed scans
    return {scan: globals()[f'scan_{scan}'](project_path) for scan in scans_needed}
```

**File Pattern Mapping**:
- `requirements.txt`, `package.json`, `go.mod` → Dependency scan
- `.env`, `.yml`, `.yaml`, `.json` → Secret scan
- `.py`, `.js`, `.ts`, `.go`, `.java` → Code vulnerability scan
- `Dockerfile`, `docker-compose.yml` → Container scan

---

## 5. Resource Limits

**Problem**: Large codebases can cause memory exhaustion or infinite scanning.

**Solution**: Set explicit resource limits and file count thresholds.

### Bad Example

```python
# BAD: Unbounded resource usage
def scan_large_codebase(path: str):
    for root, dirs, files in os.walk(path):
        for file in files:
            analyze_file(os.path.join(root, file))
```

### Good Example

```python
# GOOD: Resource-bounded scanning
class BoundedScanner:
    def __init__(self, max_memory_mb: int = 512, max_files: int = 10000):
        self._max_memory = max_memory_mb * 1024 * 1024
        self._max_files = max_files

    def scan_with_limits(self, path: str):
        import resource
        resource.setrlimit(resource.RLIMIT_AS, (self._max_memory, -1))
        files_scanned = 0
        for root, _, files in os.walk(path):
            for file in files:
                if files_scanned >= self._max_files:
                    return
                files_scanned += 1
                analyze_file(os.path.join(root, file))
```

**Recommended Limits**:
- Memory: 512MB for CLI tools, 2GB for CI/CD
- File count: 10,000 files per scan
- Timeout: 5 minutes per project
- File size: Skip files > 10MB

**Performance Monitoring**:
```python
import time
import psutil

class PerformanceMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.process = psutil.Process()

    def get_metrics(self) -> dict:
        return {
            'elapsed_seconds': time.time() - self.start_time,
            'memory_mb': self.process.memory_info().rss / 1024 / 1024,
            'cpu_percent': self.process.cpu_percent()
        }
```

---

## Summary

**Performance Best Practices**:
1. **Cache aggressively** - Store scan results and vulnerability data
2. **Scan incrementally** - Only process changed files
3. **Parallelize work** - Use thread pools for I/O-bound tasks
4. **Set resource limits** - Prevent memory exhaustion
5. **Target scans** - Only run relevant security checks

**Expected Performance Gains**:
- Incremental scanning: 90%+ faster for unchanged files
- Caching: 80%+ reduction in API calls
- Parallel execution: 3-4x faster with 4 workers
- Targeted audits: 50-70% reduction in scan time

**When to Optimize**:
- Scan time > 1 minute → Add incremental scanning
- Many API calls → Add caching layer
- Multiple projects → Add parallelization
- Large codebases → Add resource limits
