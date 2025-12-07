## 5. Performance Patterns

### Pattern 1: Connection Pooling

```python
# Good: Reuse HTTP connections
import httpx

class CloudAPIClient:
    def __init__(self):
        self._client = httpx.AsyncClient(
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
            timeout=httpx.Timeout(30.0)
        )

    async def request(self, endpoint: str, data: dict) -> dict:
        response = await self._client.post(endpoint, json=data)
        return response.json()

    async def close(self):
        await self._client.aclose()

# Bad: Create new connection per request
async def bad_request(endpoint: str, data: dict):
    async with httpx.AsyncClient() as client:  # New connection each time!
        return await client.post(endpoint, json=data)
```

### Pattern 2: Retry with Exponential Backoff

```python
# Good: Smart retry with backoff
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class CloudAPIClient:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((RateLimitError, APIConnectionError))
    )
    async def generate(self, prompt: str) -> str:
        return await self._make_request(prompt)

# Bad: No retry or fixed delay
async def bad_generate(prompt: str):
    try:
        return await make_request(prompt)
    except Exception:
        await asyncio.sleep(1)  # Fixed delay, no backoff!
        return await make_request(prompt)
```

### Pattern 3: Response Caching

```python
# Good: Cache repeated queries with TTL
from functools import lru_cache
import hashlib
from cachetools import TTLCache

class CachedCloudClient:
    def __init__(self):
        self._cache = TTLCache(maxsize=1000, ttl=300)  # 5 min TTL

    async def generate(self, prompt: str, **kwargs) -> str:
        cache_key = self._make_key(prompt, kwargs)

        if cache_key in self._cache:
            return self._cache[cache_key]

        result = await self._client.generate(prompt, **kwargs)
        self._cache[cache_key] = result
        return result

    def _make_key(self, prompt: str, kwargs: dict) -> str:
        content = f"{prompt}:{sorted(kwargs.items())}"
        return hashlib.sha256(content.encode()).hexdigest()

# Bad: No caching
async def bad_generate(prompt: str):
    return await client.generate(prompt)  # Repeated identical calls!
```

### Pattern 4: Batch API Calls

```python
# Good: Batch multiple requests
import asyncio

class BatchCloudClient:
    async def generate_batch(self, prompts: list[str]) -> list[str]:
        """Process multiple prompts concurrently with rate limiting."""
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent

        async def limited_generate(prompt: str) -> str:
            async with semaphore:
                return await self.generate(prompt)

        tasks = [limited_generate(p) for p in prompts]
        return await asyncio.gather(*tasks)

# Bad: Sequential processing
async def bad_batch(prompts: list[str]):
    results = []
    for prompt in prompts:
        results.append(await client.generate(prompt))  # One at a time!
    return results
```

### Pattern 5: Async Request Handling

```python
# Good: Fully async with proper context management
class AsyncCloudClient:
    async def __aenter__(self):
        self._client = httpx.AsyncClient()
        return self

    async def __aexit__(self, *args):
        await self._client.aclose()

    async def generate(self, prompt: str) -> str:
        response = await self._client.post(
            self.endpoint,
            json={"prompt": prompt},
            timeout=30.0
        )
        return response.json()["text"]

# Usage
async with AsyncCloudClient() as client:
    result = await client.generate("Hello")

# Bad: Blocking calls in async context
def bad_generate(prompt: str):
    response = requests.post(endpoint, json={"prompt": prompt})  # Blocks!
    return response.json()
```

---

