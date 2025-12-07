## 7. Performance Patterns

### 6.1 Permission Caching

```python
# Bad: Load permissions from disk on every operation
def run_sandboxed(command):
    permissions = load_permissions_from_disk()  # Slow I/O every time
    return execute(command)

# Good: Cache with TTL
class PermissionCache:
    def __init__(self, ttl=300):
        self._cache, self._ttl = {}, ttl

    def get(self, profile):
        if profile in self._cache and time() - self._cache[profile][1] < self._ttl:
            return self._cache[profile][0]
        perms = load_from_disk(profile)
        self._cache[profile] = (perms, time())
        return perms
```

### 6.2 Lazy Capability Loading

```python
# Bad: Load all security modules at startup
class Sandbox:
    def __init__(self):
        self.seccomp = load_seccomp_filters()      # Expensive
        self.apparmor = load_apparmor_profiles()   # Expensive

# Good: Lazy load only when needed
class Sandbox:
    _seccomp = None
    @property
    def seccomp(self):
        if self._seccomp is None: self._seccomp = load_seccomp_filters()
        return self._seccomp
```

### 6.3 Efficient IPC

```python
# Bad: Serialize full state for each call
def send_to_sandbox(data):
    return sandbox.communicate(serialize_full_state() + data)

# Good: Use shared memory for large data
class EfficientIPC:
    def __init__(self, size=1024*1024):
        self._shm = mmap.mmap(-1, size)
    def send(self, data): self._shm.seek(0); self._shm.write(data)
    def recv(self, size): self._shm.seek(0); return self._shm.read(size)
```

### 6.4 Resource Pooling

```python
# Bad: Create new sandbox for each task
for task in tasks:
    sandbox = create_sandbox()  # Expensive
    sandbox.run(task); sandbox.destroy()

# Good: Pool and reuse
class SandboxPool:
    def __init__(self, size=4):
        self._pool = Queue(size)
        for _ in range(size): self._pool.put(create_sandbox())
    def acquire(self): return self._pool.get()
    def release(self, sb): sb.reset(); self._pool.put(sb)
```

### 6.5 Minimal Privilege Sets

```python
# Bad: Request all capabilities upfront
CAPS = ['CAP_NET_ADMIN', 'CAP_SYS_ADMIN', 'CAP_DAC_OVERRIDE', ...]

# Good: Minimal sets per operation
CAPABILITY_SETS = {
    'network_bind': ['CAP_NET_BIND_SERVICE'],
    'file_read': [],
    'file_write': ['CAP_DAC_OVERRIDE'],
}
def get_caps(op): return CAPABILITY_SETS.get(op, [])
```

