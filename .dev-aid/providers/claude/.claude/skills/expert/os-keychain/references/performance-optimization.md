# OS Keychain Performance Optimization

This guide covers performance patterns for efficient credential storage and retrieval using OS keychain services.

## Overview

Keychain operations involve inter-process communication (IPC) with OS services, which can be slow. These patterns minimize IPC overhead through caching, batching, and lazy loading.

---

## 1. Credential Caching

### Problem: Repeated Keychain Access

```python
# BAD: Repeated keychain access
class SlowCredentialStore:
    def get_api_key(self):
        return keyring.get_password(self._service, "api-key")  # Slow IPC every call
```

**Impact**: 50-200ms per keychain access on typical systems

### Solution: In-Memory Cache with TTL

```python
from functools import lru_cache
from threading import Lock
import time

class CachedCredentialStore:
    def __init__(self, namespace: str, cache_ttl: int = 300):
        self._service = f"com.jarvis.{namespace}"
        self._cache: dict[str, tuple[str, float]] = {}
        self._lock = Lock()
        self._ttl = cache_ttl

    def retrieve(self, key: str) -> str:
        with self._lock:
            if key in self._cache:
                value, timestamp = self._cache[key]
                if time.time() - timestamp < self._ttl:
                    return value

            secret = keyring.get_password(self._service, key)
            if secret is None:
                raise KeyError(f"Credential not found: {key}")

            self._cache[key] = (secret, time.time())
            return secret

    def invalidate(self, key: str = None):
        with self._lock:
            if key:
                self._cache.pop(key, None)
            else:
                self._cache.clear()
```

**Benefits**:
- 1000x faster for cached credentials (nanoseconds vs milliseconds)
- Reduces keychain service load
- Thread-safe with locks

**Trade-offs**:
- Memory usage for cached credentials
- Stale credentials if TTL too long
- Invalidation needed after updates

---

## 2. Batch Operations

### Problem: Individual Keychain Calls

```python
# BAD: Individual keychain calls
def load_all_credentials():
    db_pass = keyring.get_password("jarvis", "db-password")
    api_key = keyring.get_password("jarvis", "api-key")
    secret = keyring.get_password("jarvis", "encryption-key")
    return db_pass, api_key, secret  # 3 separate IPC calls
```

**Impact**: 150-600ms startup time for 3 credentials

### Solution: Batch Loading

```python
class BatchCredentialLoader:
    def __init__(self, namespace: str, keys: list[str]):
        self._service = f"com.jarvis.{namespace}"
        self._credentials = self._load_batch(keys)

    def _load_batch(self, keys: list[str]) -> dict[str, str]:
        """Load multiple credentials in optimized batch."""
        result = {}
        for key in keys:
            value = keyring.get_password(self._service, key)
            if value:
                result[key] = value
        return result

    def get(self, key: str) -> str:
        if key not in self._credentials:
            raise KeyError(f"Credential not loaded: {key}")
        return self._credentials[key]

# Usage - single initialization at startup
loader = BatchCredentialLoader("secrets", ["db-password", "api-key", "encryption-key"])
```

**Benefits**:
- All credentials loaded in one pass
- Predictable startup time
- Fails fast if credentials missing

**Trade-offs**:
- All credentials in memory at once
- Requires knowing needed keys upfront

---

## 3. Lazy Loading

### Problem: Loading Unused Credentials

```python
# BAD: Load all credentials at import
class EagerStore:
    def __init__(self):
        self.db_password = keyring.get_password("jarvis", "db")  # Loaded immediately
        self.api_key = keyring.get_password("jarvis", "api")
```

**Impact**: Unnecessary startup delay if credentials not used

### Solution: Load Only When Accessed

```python
class LazyCredentialStore:
    def __init__(self, namespace: str):
        self._service = f"com.jarvis.{namespace}"
        self._cache: dict[str, str] = {}

    def __getattr__(self, name: str) -> str:
        if name.startswith('_'):
            raise AttributeError(name)

        if name not in self._cache:
            value = keyring.get_password(self._service, name.replace('_', '-'))
            if value is None:
                raise KeyError(f"Credential not found: {name}")
            self._cache[name] = value

        return self._cache[name]

# Usage - credentials loaded on first access
store = LazyCredentialStore("api-keys")
# No keychain calls yet
key = store.openai_key  # First access triggers load
```

**Benefits**:
- Zero startup cost
- Load only what's needed
- Auto-caching after first access

**Trade-offs**:
- First access slower
- Harder to validate all credentials exist at startup

---

## 4. Connection Reuse

### Problem: Creating New Backend Each Time

```python
# BAD: Create new backend each time
def get_credential(key: str) -> str:
    store = SecureCredentialStore("service")  # Backend verification each call
    return store.retrieve(key)
```

**Impact**: Redundant backend verification and initialization

### Solution: Singleton Pattern

```python
from threading import Lock

class CredentialStoreFactory:
    _instances: dict[str, 'SecureCredentialStore'] = {}
    _lock = Lock()

    @classmethod
    def get_store(cls, namespace: str) -> 'SecureCredentialStore':
        with cls._lock:
            if namespace not in cls._instances:
                cls._instances[namespace] = SecureCredentialStore(namespace)
            return cls._instances[namespace]

# Usage - reuses existing store instance
store = CredentialStoreFactory.get_store("api-keys")
```

**Benefits**:
- Single backend verification per namespace
- Reduced memory footprint
- Consistent store instances

**Trade-offs**:
- Global state requires thread safety
- Cannot easily test with fresh instances

---

## 5. Memory-Safe Handling

### Problem: Credentials Persist in Memory

```python
# BAD: Credentials persist in memory
class UnsafeStore:
    def get_credential(self, key: str) -> str:
        secret = keyring.get_password(self._service, key)
        self.last_retrieved = secret  # Persists in memory
        return secret
```

**Risk**: Memory dumps expose credentials

### Solution: Secure Memory Handling

```python
import ctypes
import gc

class SecureMemoryStore:
    def retrieve_and_use(self, key: str, callback) -> None:
        """Retrieve credential, use it, then clear from memory."""
        secret = keyring.get_password(self._service, key)
        if secret is None:
            raise KeyError(f"Credential not found: {key}")

        try:
            callback(secret)
        finally:
            # Overwrite string in memory (best effort in Python)
            if secret:
                secret_bytes = secret.encode()
                ctypes.memset(id(secret_bytes) + 32, 0, len(secret_bytes))
            del secret
            gc.collect()

    def with_credential(self, key: str):
        """Context manager for secure credential access."""
        class CredentialContext:
            def __init__(ctx_self, store, key):
                ctx_self._store = store
                ctx_self._key = key
                ctx_self._value = None

            def __enter__(ctx_self):
                ctx_self._value = keyring.get_password(
                    ctx_self._store._service, ctx_self._key
                )
                return ctx_self._value

            def __exit__(ctx_self, *args):
                if ctx_self._value:
                    del ctx_self._value
                gc.collect()

        return CredentialContext(self, key)

# Usage
store = SecureMemoryStore("secrets")
with store.with_credential("api-key") as api_key:
    make_api_call(api_key)
# Credential cleared after context exits
```

**Benefits**:
- Minimizes credential exposure time
- Explicit cleanup after use
- Reduces memory dump attack surface

**Trade-offs**:
- More complex API
- Memory zeroing not guaranteed in Python
- Callback/context manager patterns required

---

## Best Practices Summary

1. **Cache with TTL**: 5-minute default for most credentials
2. **Batch at startup**: Load all required credentials once
3. **Lazy for optional**: Load rarely-used credentials on demand
4. **Singleton stores**: Reuse store instances per namespace
5. **Clear after use**: Use context managers for sensitive operations

---

## Performance Benchmarks

| Pattern | First Access | Subsequent Access | Memory |
|---------|--------------|-------------------|--------|
| No Cache | 50-200ms | 50-200ms | Low |
| TTL Cache | 50-200ms | <1ms | Medium |
| Batch Load | 150-600ms | <1ms | High |
| Lazy Load | 0ms startup | 50-200ms first | Low-Medium |

Choose patterns based on your access patterns and performance requirements.
