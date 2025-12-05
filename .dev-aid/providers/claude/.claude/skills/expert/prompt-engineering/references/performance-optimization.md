# Prompt Engineering Performance Optimization

## Overview

This guide covers performance optimization techniques for prompt engineering, focusing on token efficiency, caching strategies, and response optimization.

---

## Pattern 1: Token Optimization

### Anti-Pattern: Verbose Prompts

```python
# BAD: Verbose, wastes tokens
system_prompt = """
You are a helpful AI assistant called JARVIS. You should always be polite
and helpful. When users ask questions, you should provide detailed and
comprehensive answers. Make sure to be thorough in your responses and
consider all aspects of the question...
"""
```

### Best Practice: Concise Prompts

```python
# GOOD: Concise, same behavior
system_prompt = """You are JARVIS, a helpful AI assistant.
Be polite, thorough, and address all aspects of user questions."""
```

**Benefits**:
- 70% token reduction
- Same behavioral outcome
- Faster processing
- Lower API costs

---

## Pattern 2: Response Caching

### Anti-Pattern: Repeated API Calls

```python
# BAD: Repeated calls for same classification
async def classify_intent(user_input: str) -> str:
    return await llm.generate(classification_prompt + user_input)
```

### Best Practice: Intelligent Caching

```python
# GOOD: Cache common patterns
from functools import lru_cache
import hashlib

class IntentClassifier:
    def __init__(self):
        self._cache = {}

    async def classify(self, user_input: str) -> str:
        # Normalize and hash for cache key
        normalized = user_input.lower().strip()
        cache_key = hashlib.md5(normalized.encode()).hexdigest()

        if cache_key in self._cache:
            return self._cache[cache_key]

        result = await self._llm_classify(normalized)
        self._cache[cache_key] = result
        return result
```

**Benefits**:
- Instant responses for common queries
- Reduced API costs
- Consistent classifications
- Lower latency

**Cache Invalidation**:
```python
def invalidate_cache(self):
    """Clear cache after model updates."""
    self._cache.clear()

def invalidate_old_entries(self, max_age: int = 3600):
    """Remove entries older than max_age seconds."""
    current_time = time.time()
    self._cache = {
        k: v for k, v in self._cache.items()
        if current_time - v["timestamp"] < max_age
    }
```

---

## Pattern 3: Few-Shot Example Selection

### Anti-Pattern: Include All Examples

```python
# BAD: Include all examples (wastes tokens)
examples = load_all_examples()  # 50 examples
prompt = f"Examples:\n{examples}\n\nClassify: {input}"
```

### Best Practice: Dynamic Example Selection

```python
# GOOD: Select relevant examples dynamically
from sklearn.metrics.pairwise import cosine_similarity

class FewShotSelector:
    def __init__(self, examples: list[dict], embedder):
        self.examples = examples
        self.embedder = embedder
        self.embeddings = embedder.encode([e["text"] for e in examples])

    def select(self, query: str, k: int = 3) -> list[dict]:
        """Select k most relevant examples for query."""
        query_emb = self.embedder.encode([query])
        similarities = cosine_similarity(query_emb, self.embeddings)[0]
        top_k = similarities.argsort()[-k:][::-1]
        return [self.examples[i] for i in top_k]
```

**Usage**:
```python
selector = FewShotSelector(all_examples, embedder)

# Only include relevant examples
relevant = selector.select(user_query, k=3)
prompt = build_few_shot_prompt(relevant, user_query)
```

**Benefits**:
- Reduces tokens by 70-90%
- More relevant examples = better accuracy
- Scales to large example sets

---

## Pattern 4: Prompt Compression

### Anti-Pattern: Full Conversation History

```python
# BAD: Full conversation history
history = [{"role": "user", "content": msg} for msg in all_messages]
prompt = build_prompt(history)  # Could be 10k+ tokens
```

### Best Practice: Intelligent History Compression

```python
# GOOD: Compress history, keep recent context
class HistoryCompressor:
    def compress(self, history: list[dict], max_tokens: int = 2000) -> list[dict]:
        """Compress history while preserving key context."""
        # Keep system + last N turns
        recent = history[-6:]  # Last 3 exchanges

        # Summarize older context if needed
        if len(history) > 6:
            older = history[:-6]
            summary = self._summarize(older)
            return [{"role": "system", "content": f"Context: {summary}"}] + recent

        return recent

    def _summarize(self, messages: list[dict]) -> str:
        """Use smaller model for summarization."""
        return summarizer.generate(messages, max_tokens=200)
```

**Advanced Strategies**:

1. **Sliding Window**:
```python
def sliding_window(history: list[dict], window_size: int = 10) -> list[dict]:
    """Keep only recent messages."""
    return history[-window_size:]
```

2. **Importance-Based Retention**:
```python
def importance_filter(history: list[dict], threshold: float = 0.5) -> list[dict]:
    """Keep messages above importance threshold."""
    scored = [(msg, calculate_importance(msg)) for msg in history]
    return [msg for msg, score in scored if score > threshold]
```

3. **Topic-Based Compression**:
```python
def topic_compress(history: list[dict]) -> list[dict]:
    """Group by topic and summarize each."""
    topics = cluster_by_topic(history)
    return [summarize_topic(topic) for topic in topics]
```

---

## Pattern 5: Structured Output Optimization

### Anti-Pattern: Free-Form Output

```python
# BAD: Free-form output requires complex parsing
prompt = "Extract the entities from this text and describe them."
# Response: "The text mentions John (a person), NYC (a city)..."
```

### Best Practice: JSON Schema

```python
# GOOD: JSON schema for direct parsing
prompt = """Extract entities as JSON:
{"entities": [{"name": str, "type": "person"|"location"|"org"}]}

Text: {input}
JSON:"""
```

### Even Better: Function Calling

```python
# BEST: Use function calling
tools = [{
    "name": "extract_entities",
    "parameters": {
        "type": "object",
        "properties": {
            "entities": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "type": {"enum": ["person", "location", "org"]}
                    }
                }
            }
        }
    }
}]
```

**Benefits**:
- No parsing errors
- Type-safe responses
- Easier validation
- Automatic retry on schema mismatch

---

## Pattern 6: Batch Processing

### Anti-Pattern: Sequential Processing

```python
# BAD: Process one at a time
results = []
for item in items:
    result = await llm.generate(prompt + item)
    results.append(result)
```

### Best Practice: Batch Processing

```python
# GOOD: Batch processing with concurrency
import asyncio

async def batch_process(items: list[str], batch_size: int = 10):
    """Process items in batches with concurrency control."""
    results = []

    for i in range(0, len(items), batch_size):
        batch = items[i:i+batch_size]

        # Process batch concurrently
        tasks = [llm.generate(prompt + item) for item in batch]
        batch_results = await asyncio.gather(*tasks)

        results.extend(batch_results)

    return results
```

**Benefits**:
- 10x faster for large datasets
- Better resource utilization
- Reduced total API time

---

## Pattern 7: Model Selection Optimization

### Strategy: Right Model for the Task

```python
class ModelSelector:
    """Select optimal model based on task complexity."""

    MODELS = {
        "simple": {
            "name": "claude-haiku",
            "cost_per_token": 0.00001,
            "speed": "fast"
        },
        "medium": {
            "name": "claude-sonnet",
            "cost_per_token": 0.00003,
            "speed": "balanced"
        },
        "complex": {
            "name": "claude-opus",
            "cost_per_token": 0.00015,
            "speed": "slow"
        }
    }

    def select(self, task: str) -> dict:
        """Select model based on task complexity."""
        complexity = self._analyze_complexity(task)
        return self.MODELS[complexity]

    def _analyze_complexity(self, task: str) -> str:
        """Analyze task complexity."""
        # Simple: classification, extraction, formatting
        simple_keywords = ["classify", "extract", "format", "list"]
        if any(kw in task.lower() for kw in simple_keywords):
            return "simple"

        # Complex: reasoning, analysis, creative
        complex_keywords = ["analyze", "explain", "design", "create"]
        if any(kw in task.lower() for kw in complex_keywords):
            return "complex"

        return "medium"
```

**Cost Optimization**:
```python
# Use Haiku for simple tasks (10x cheaper)
if is_simple_classification(task):
    model = "claude-haiku"
else:
    model = "claude-sonnet"
```

---

## Pattern 8: Prompt Template Caching

### Strategy: Pre-compile Common Templates

```python
class TemplateCache:
    """Cache and reuse prompt templates."""

    def __init__(self):
        self.templates = {
            "classification": """Classify this into one of: {categories}

Input: {input}
Category:""",

            "extraction": """Extract {entities} from this text:

Text: {text}
JSON:""",

            "summarization": """Summarize this in {length} words:

{content}
Summary:"""
        }

    def get_prompt(self, template_name: str, **kwargs) -> str:
        """Get compiled prompt from template."""
        template = self.templates[template_name]
        return template.format(**kwargs)
```

**Benefits**:
- Consistent prompts
- Easy to test and update
- No runtime string manipulation
- Versioned templates

---

## Performance Benchmarks

### Token Optimization Impact

| Technique | Token Reduction | Cost Savings | Implementation Effort |
|-----------|----------------|--------------|---------------------|
| Concise prompts | 50-70% | High | Low |
| Few-shot selection | 70-90% | Very High | Medium |
| History compression | 60-80% | High | Medium |
| Structured output | 20-30% | Medium | Low |

### Latency Optimization

| Technique | Latency Reduction | Complexity |
|-----------|------------------|------------|
| Response caching | 90-100% (cache hit) | Low |
| Batch processing | 50-80% | Medium |
| Model selection | 30-70% | Low |

---

## Monitoring and Metrics

### Key Metrics to Track

```python
class PerformanceMonitor:
    """Monitor prompt performance metrics."""

    def log_request(self, prompt: str, response: str, latency: float):
        """Log request metrics."""
        metrics = {
            "prompt_tokens": count_tokens(prompt),
            "response_tokens": count_tokens(response),
            "total_tokens": count_tokens(prompt) + count_tokens(response),
            "latency_ms": latency * 1000,
            "cost_usd": calculate_cost(prompt, response)
        }

        logger.info("llm.request", **metrics)
        return metrics
```

**Dashboards**:
- Average tokens per request
- Cache hit rate
- Cost per request type
- Latency percentiles (p50, p95, p99)

---

## Summary

**Token Optimization**:
1. Use concise prompts
2. Select relevant examples dynamically
3. Compress conversation history

**Latency Optimization**:
1. Cache frequent requests
2. Batch process when possible
3. Use appropriate model for task

**Cost Optimization**:
1. Choose right model for complexity
2. Implement aggressive caching
3. Monitor and optimize high-cost patterns
