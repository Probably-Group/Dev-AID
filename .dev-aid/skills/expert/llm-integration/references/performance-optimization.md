# LLM Performance Optimization Patterns

## Overview

This document contains performance optimization patterns specifically for LLM inference, focusing on reducing latency, optimizing token usage, and improving throughput for real-time applications like JARVIS.

---

## Pattern 1: Streaming Responses (Reduced TTFB)

**Goal**: Minimize Time To First Byte for better user experience

**Good Implementation**:
```python
# Stream tokens for immediate user feedback
async def stream_generate(self, model: str, prompt: str):
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST", f"{self.base_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": True}
        ) as response:
            async for line in response.aiter_lines():
                if line:
                    yield json.loads(line).get("response", "")
```

**Bad Implementation**:
```python
# Wait for complete response
def generate_blocking(self, model: str, prompt: str) -> str:
    response = self.client.post(...)  # User waits for entire generation
    return response.json()["response"]
```

**Performance Impact**:
- Reduces perceived latency by 50-80%
- Enables real-time feedback for voice assistants
- Better user experience with progressive output

---

## Pattern 2: Token Optimization

**Goal**: Minimize token usage while maintaining quality

**Implementation**:
```python
import tiktoken

class TokenOptimizer:
    def __init__(self, model: str = "cl100k_base"):
        self.encoder = tiktoken.get_encoding(model)

    def optimize_prompt(self, prompt: str, max_tokens: int = 2048) -> str:
        """Optimize prompt to fit within token budget."""
        tokens = self.encoder.encode(prompt)
        if len(tokens) > max_tokens:
            # Truncate from middle, keep start and end
            keep = max_tokens // 2
            tokens = tokens[:keep] + tokens[-keep:]
        return self.encoder.decode(tokens)

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoder.encode(text))
```

**Bad Implementation**:
```python
# Send unlimited context without token awareness
def generate(prompt):
    return llm(prompt)  # May exceed context window or waste tokens
```

**Performance Impact**:
- Prevents context window overflow
- Reduces inference time by 30-50% for long prompts
- Better cost control for cloud-based models

---

## Pattern 3: Response Caching

**Goal**: Avoid redundant inference for identical prompts

**Implementation**:
```python
from functools import lru_cache
import hashlib
from cachetools import TTLCache

class CachedLLMClient:
    def __init__(self, client, cache_size: int = 100, ttl: int = 300):
        self.client = client
        self.cache = TTLCache(maxsize=cache_size, ttl=ttl)

    async def generate(self, model: str, prompt: str, **kwargs) -> str:
        cache_key = hashlib.sha256(
            f"{model}:{prompt}:{kwargs}".encode()
        ).hexdigest()

        if cache_key in self.cache:
            return self.cache[cache_key]

        result = await self.client.generate(model, prompt, **kwargs)
        self.cache[cache_key] = result
        return result
```

**Bad Implementation**:
```python
# No caching - repeated identical requests hit LLM
async def generate(prompt):
    return await llm.generate(prompt)  # Always calls LLM
```

**Performance Impact**:
- Instant responses for repeated prompts
- Reduces inference load by 40-60% in typical usage
- Lower latency for common queries

**Trade-offs**:
- Memory usage for cache
- Stale responses if model updates
- Not suitable for highly variable prompts

---

## Pattern 4: Batch Request Processing

**Goal**: Maximize throughput with concurrent inference

**Implementation**:
```python
import asyncio

class BatchLLMProcessor:
    def __init__(self, client, max_concurrent: int = 4):
        self.client = client
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def process_batch(self, prompts: list[str], model: str) -> list[str]:
        """Process multiple prompts with controlled concurrency."""
        async def process_one(prompt: str) -> str:
            async with self.semaphore:
                return await self.client.generate(model, prompt)

        return await asyncio.gather(*[process_one(p) for p in prompts])
```

**Bad Implementation**:
```python
# Sequential processing
async def process_all(prompts):
    results = []
    for prompt in prompts:
        results.append(await llm.generate(prompt))  # One at a time
    return results
```

**Performance Impact**:
- 4x throughput improvement with 4 concurrent requests
- Better resource utilization
- Reduced total processing time

**Considerations**:
- Balance concurrency with memory limits
- Monitor system resources
- Consider model-specific limits

---

## Pattern 5: Connection Pooling

**Goal**: Reduce connection overhead for multiple requests

**Implementation**:
```python
import httpx

class PooledLLMClient:
    def __init__(self, config: OllamaConfig):
        self.config = config
        # Connection pool with keep-alive
        self.client = httpx.AsyncClient(
            base_url=f"http://{config.host}:{config.port}",
            timeout=config.timeout,
            limits=httpx.Limits(
                max_keepalive_connections=10,
                max_connections=20,
                keepalive_expiry=30.0
            )
        )

    async def close(self):
        await self.client.aclose()
```

**Bad Implementation**:
```python
# Create new connection per request
async def generate(prompt):
    async with httpx.AsyncClient() as client:  # New connection each time
        return await client.post(...)
```

**Performance Impact**:
- Reduces connection overhead by 50-70%
- Faster response times for subsequent requests
- Better resource utilization

---

## Pattern 6: Model Preloading and Warmup

**Goal**: Eliminate cold start latency

**Implementation**:
```python
class ModelWarmer:
    def __init__(self, model_manager):
        self.manager = model_manager

    async def warmup(self, model_name: str):
        """Preload and warm up model."""
        model = self.manager.get_model(model_name)

        # Run warmup inference
        warmup_prompt = "Test"
        _ = model(warmup_prompt, max_tokens=1)

        logger.info("model.warmed", name=model_name)

    async def warmup_all(self, model_names: list[str]):
        """Warm up multiple models in parallel."""
        await asyncio.gather(*[
            self.warmup(name) for name in model_names
        ])
```

**Performance Impact**:
- Eliminates 2-10 second cold start
- Consistent first-request performance
- Better user experience

---

## Pattern 7: Adaptive Token Budgeting

**Goal**: Dynamically adjust token allocation based on context

**Implementation**:
```python
class AdaptiveTokenBudget:
    def __init__(self, base_budget: int = 2048):
        self.base_budget = base_budget
        self.usage_history = []

    def calculate_budget(self, prompt_tokens: int) -> tuple[int, int]:
        """Calculate input/output token budget."""
        # Reserve tokens for response based on historical average
        avg_response_length = self._get_avg_response_length()

        # Allocate budget
        max_prompt_tokens = int(self.base_budget * 0.6)
        max_response_tokens = self.base_budget - prompt_tokens

        return min(prompt_tokens, max_prompt_tokens), max_response_tokens

    def _get_avg_response_length(self) -> int:
        if not self.usage_history:
            return 512
        return sum(self.usage_history[-10:]) // len(self.usage_history[-10:])

    def record_usage(self, response_tokens: int):
        """Track response token usage."""
        self.usage_history.append(response_tokens)
        if len(self.usage_history) > 100:
            self.usage_history.pop(0)
```

**Performance Impact**:
- Prevents truncated responses
- Optimizes token utilization
- Adapts to usage patterns

---

## Pattern 8: Progressive Response Timeout

**Goal**: Balance latency and quality with adaptive timeouts

**Implementation**:
```python
class ProgressiveTimeout:
    def __init__(self, initial_timeout: float = 10.0):
        self.initial = initial_timeout
        self.timeouts = {}

    async def generate_with_progressive_timeout(
        self, model: str, prompt: str
    ) -> str:
        """Generate with adaptive timeout based on prompt complexity."""
        complexity = self._estimate_complexity(prompt)
        timeout = self.initial * (1 + complexity / 10)

        try:
            return await asyncio.wait_for(
                self._generate(model, prompt),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.warning("inference.timeout",
                          model=model,
                          timeout=timeout,
                          complexity=complexity)
            raise

    def _estimate_complexity(self, prompt: str) -> float:
        """Estimate prompt complexity (0-10 scale)."""
        # Simple heuristic: length + question marks + complexity keywords
        length_score = min(len(prompt) / 500, 5)
        question_score = prompt.count('?') * 0.5
        complexity_keywords = ['analyze', 'explain', 'compare', 'synthesize']
        keyword_score = sum(1 for kw in complexity_keywords if kw in prompt.lower())

        return min(length_score + question_score + keyword_score, 10)
```

**Performance Impact**:
- Prevents unnecessary timeouts for complex prompts
- Faster failure detection for simple prompts
- Better resource utilization

---

## Pattern 9: Memory-Mapped Model Loading

**Goal**: Faster model loading with lower memory footprint

**Implementation**:
```python
from llama_cpp import Llama

def load_model_optimized(model_path: str) -> Llama:
    """Load model with memory mapping for efficiency."""
    return Llama(
        model_path=model_path,
        n_ctx=4096,
        n_batch=512,
        n_threads=os.cpu_count() // 2,
        use_mmap=True,      # Memory-map file (faster loading)
        use_mlock=False,    # Don't lock in RAM (allows swapping)
        n_gpu_layers=0,     # CPU-only (adjust for GPU)
        verbose=False
    )
```

**Performance Impact**:
- 3-5x faster model loading
- Shared memory across processes
- Lower peak memory usage

---

## Pattern 10: Request Deduplication

**Goal**: Avoid processing duplicate concurrent requests

**Implementation**:
```python
from asyncio import Event, Task
from typing import Dict

class RequestDeduplicator:
    def __init__(self):
        self.pending: Dict[str, tuple[Task, list[Event]]] = {}

    async def deduplicated_generate(
        self, model: str, prompt: str, client
    ) -> str:
        """Process request, deduplicating concurrent identical requests."""
        key = f"{model}:{prompt}"

        if key in self.pending:
            # Request already in progress
            event = Event()
            self.pending[key][1].append(event)
            await event.wait()
            result = self.pending[key][0].result()
        else:
            # New request
            task = asyncio.create_task(client.generate(model, prompt))
            self.pending[key] = (task, [])

            result = await task

            # Notify waiting requesters
            for event in self.pending[key][1]:
                event.set()

            del self.pending[key]

        return result
```

**Performance Impact**:
- Eliminates redundant computation
- Reduces load during traffic spikes
- Better resource utilization

---

## Performance Monitoring

### Key Metrics to Track

```python
import structlog
from time import time

class InferenceMetrics:
    def __init__(self):
        self.logger = structlog.get_logger()

    async def timed_inference(self, model: str, prompt: str, client) -> tuple[str, float]:
        """Run inference with timing metrics."""
        start = time()
        prompt_tokens = count_tokens(prompt)

        result = await client.generate(model, prompt)

        duration = time() - start
        response_tokens = count_tokens(result)
        tokens_per_second = response_tokens / duration if duration > 0 else 0

        self.logger.info(
            "inference.completed",
            model=model,
            duration_ms=duration * 1000,
            prompt_tokens=prompt_tokens,
            response_tokens=response_tokens,
            tokens_per_second=tokens_per_second
        )

        return result, duration
```

### Performance Targets

| Metric | Target | Critical |
|--------|--------|----------|
| Time to First Token | <500ms | <1000ms |
| Tokens per Second | >20 | >10 |
| Request Timeout | 30s | 60s |
| Cache Hit Rate | >40% | >20% |
| Memory Usage | <4GB | <8GB |

---

## Optimization Checklist

Before deploying:
- [ ] Streaming enabled for all user-facing endpoints
- [ ] Response caching configured with appropriate TTL
- [ ] Connection pooling enabled
- [ ] Token budgets enforced
- [ ] Models preloaded and warmed up
- [ ] Batch processing for bulk operations
- [ ] Metrics collection and monitoring active
- [ ] Performance targets validated under load

---

## Anti-Patterns

### Anti-Pattern 1: Loading Model Per Request
**Problem**: Seconds of latency per request
**Solution**: Singleton pattern, load once at startup

### Anti-Pattern 2: Unlimited Context Size
**Problem**: OOM errors, slow inference
**Solution**: Set appropriate n_ctx based on hardware

### Anti-Pattern 3: No Token Limits
**Problem**: Runaway generation, DoS
**Solution**: Enforce max_tokens on all requests

### Anti-Pattern 4: Synchronous Inference
**Problem**: Blocks event loop, poor throughput
**Solution**: Use async/await patterns

### Anti-Pattern 5: No Request Timeouts
**Problem**: Hung requests, resource exhaustion
**Solution**: Progressive timeouts based on complexity
