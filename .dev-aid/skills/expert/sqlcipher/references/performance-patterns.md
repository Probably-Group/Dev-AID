## 7. Performance Patterns

### 6.1 Page Size Optimization

```python
# Good: Optimize page size for workload
conn.execute("PRAGMA cipher_page_size = 4096")  # Default, good for mixed
conn.execute("PRAGMA cipher_page_size = 8192")  # Better for large BLOBs
conn.execute("PRAGMA cipher_page_size = 1024")  # Better for small records

# Bad: Using default without consideration
conn.execute("PRAGMA key = ...")
# No page size optimization
```

### 6.2 Cipher Configuration Tuning

```python
# Good: Balance security and performance
conn.executescript("""
    PRAGMA kdf_iter = 256000;           -- Strong but not excessive
    PRAGMA cipher_plaintext_header_size = 32;  -- Allow mmap optimization
    PRAGMA cipher_use_hmac = ON;        -- Required for integrity
""")

# Bad: Excessive iterations slowing operations
conn.execute("PRAGMA kdf_iter = 1000000")  -- Unnecessary, hurts open time
```

### 6.3 Connection and Key Caching

```python
# Good: Cache connection, derive key once
class DatabasePool:
    _instance = None
    _key_cache = {}

    def get_connection(self, db_name: str, password: str):
        if db_name not in self._key_cache:
            self._key_cache[db_name] = derive_key(password)
        return EncryptedDatabase(db_name, self._key_cache[db_name])

# Bad: Deriving key on every operation
def query(password, sql):
    key = derive_key(password)  # Expensive! ~100ms each time
    db = EncryptedDatabase("app.db", key)
    return db.execute(sql)
```

### 6.4 WAL Mode with Encryption

```python
# Good: Enable WAL for concurrent reads
conn.executescript("""
    PRAGMA key = ...;
    PRAGMA journal_mode = WAL;
    PRAGMA synchronous = NORMAL;        -- Faster, still safe with WAL
    PRAGMA wal_autocheckpoint = 1000;   -- Checkpoint every 1000 pages
""")

# Bad: Default journal mode
conn.execute("PRAGMA key = ...")
# Uses DELETE journal - slower, blocks readers
```

### 6.5 Memory Security Trade-offs

```python
# Good: Enable memory security for sensitive apps
conn.execute("PRAGMA cipher_memory_security = ON")  # Zeros freed memory

# Good: Disable for performance-critical, lower-security contexts
conn.execute("PRAGMA cipher_memory_security = OFF")  # 10-15% faster

# Bad: No explicit choice - relying on default
```

---

