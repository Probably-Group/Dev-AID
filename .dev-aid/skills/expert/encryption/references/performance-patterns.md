## 6. Performance Patterns

### 5.1 Key Caching

**Bad:** Deriving key on every operation (~500ms per Argon2id call)

**Good - Cache with TTL:**
```python
class CachedKeyManager:
    def __init__(self, cache_ttl: int = 300):
        self._cache: dict[str, tuple[bytes, float]] = {}
        self._ttl = cache_ttl

    def get_key(self, password: str, salt: bytes) -> bytes:
        cache_key = f"{hash(password)}:{salt.hex()}"
        if cache_key in self._cache:
            key, ts = self._cache[cache_key]
            if time.time() - ts < self._ttl:
                return key
        key, _ = SecureKeyDerivation.derive_key(password, salt)
        self._cache[cache_key] = (key, time.time())
        return key
```

### 5.2 Streaming Encryption for Large Data

**Bad:** `data = f.read()` loads entire file into memory

**Good - Stream with chunking (64KB chunks):**
```python
nonce = secrets.token_bytes(12)
encryptor = Cipher(algorithms.AES(key), modes.GCM(nonce)).encryptor()
with open(input_path, 'rb') as fin, open(output_path, 'wb') as fout:
    fout.write(nonce)
    while chunk := fin.read(64 * 1024):
        fout.write(encryptor.update(chunk))
    fout.write(encryptor.finalize() + encryptor.tag)
```

### 5.3 Hardware Acceleration

**Bad:** PyCryptodome without OpenSSL backend (10-100x slower)

**Good:** Use `cryptography` library - auto-detects AES-NI via OpenSSL 3.x backend

### 5.4 Batch Operations

**Bad - Individual loop with append:**
```python
results = []
for record in records:
    results.append(encryptor.encrypt(record))
```

**Good - List comprehension with single encryptor:**
```python
encryptor = SecureEncryption(key)
results = [encryptor.encrypt(record) for record in records]

# For large batches, use ProcessPoolExecutor for parallelization
```

### 5.5 Memory-Safe Key Handling

**Bad - Keys remain in memory:**
```python
self.key = SecureKeyDerivation.derive_key(password)  # Never cleared
```

**Good - Zero keys after use with context manager:**
```python
import ctypes

class SecureKeyHolder:
    def __init__(self, password: str):
        self._key, self.salt = SecureKeyDerivation.derive_key(password)

    def __exit__(self, *args):
        if self._key:
            key_buffer = (ctypes.c_char * len(self._key)).from_buffer_copy(self._key)
            ctypes.memset(key_buffer, 0, len(self._key))
            self._key = None

# Usage: with SecureKeyHolder(password) as kh: encrypt(kh._key, data)
```

