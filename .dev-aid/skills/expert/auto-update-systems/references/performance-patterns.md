## 9. Performance Patterns

### 8.1 Delta Updates

```python
# Good: Download only changed bytes
class DeltaUpdateManager:
    async def download_delta(self, from_version: str, to_version: str) -> bytes:
        delta_url = f"{self.endpoint}/deltas/{from_version}-{to_version}.patch"
        delta = await self._download(delta_url)
        return self._apply_delta(self.current_binary, delta)

# Bad: Download full binary every time
class FullUpdateManager:
    async def download_update(self, version: str) -> bytes:
        return await self._download(f"{self.endpoint}/full/{version}.tar.gz")
```

### 8.2 Background Downloads

```python
# Good: Download in background without blocking UI
class BackgroundDownloader:
    async def download_in_background(self, url: str) -> None:
        self._download_task = asyncio.create_task(self._download(url))
        self._download_task.add_done_callback(self._on_download_complete)

    def get_progress(self) -> float:
        return self._bytes_downloaded / self._total_bytes

# Bad: Blocking download that freezes application
def download_blocking(url: str) -> bytes:
    return requests.get(url).content  # Blocks entire app
```

### 8.3 Bandwidth Throttling

```python
# Good: Respect user's bandwidth limits
class ThrottledDownloader:
    def __init__(self, max_bytes_per_sec: int = 1_000_000):
        self.rate_limiter = RateLimiter(max_bytes_per_sec)

    async def download(self, url: str) -> bytes:
        chunks = []
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                async for chunk in response.content.iter_chunked(8192):
                    await self.rate_limiter.acquire(len(chunk))
                    chunks.append(chunk)
        return b''.join(chunks)

# Bad: Saturate user's connection
async def download_unlimited(url: str) -> bytes:
    async with aiohttp.ClientSession() as session:
        return await (await session.get(url)).read()
```

### 8.4 Rollback Optimization

```python
# Good: Keep only necessary backup data
class SmartRollback:
    def create_backup(self) -> BackupHandle:
        # Only backup files that will be modified
        modified_files = self._get_files_to_update()
        return self._backup_files(modified_files)

    def cleanup_old_backups(self, keep_count: int = 2) -> None:
        backups = sorted(self._list_backups(), key=lambda b: b.date)
        for backup in backups[:-keep_count]:
            backup.delete()

# Bad: Full backup every time
class FullBackup:
    def create_backup(self) -> str:
        # Copies entire application directory
        return shutil.copytree(self.app_dir, f"{self.app_dir}.backup")
```

### 8.5 Signature Caching

```python
# Good: Cache verified signatures
class CachedSignatureVerifier:
    def __init__(self):
        self._verified_cache: Dict[str, bool] = {}

    def verify(self, data: bytes, signature: str) -> bool:
        cache_key = hashlib.sha256(data).hexdigest()
        if cache_key in self._verified_cache:
            return self._verified_cache[cache_key]

        result = self._verify_ed25519(data, signature)
        self._verified_cache[cache_key] = result
        return result

# Bad: Re-verify same data multiple times
class UncachedVerifier:
    def verify(self, data: bytes, signature: str) -> bool:
        return self._verify_ed25519(data, signature)  # Expensive each time
```

---

