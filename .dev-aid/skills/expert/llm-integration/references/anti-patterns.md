# LLM Integration Anti-Patterns and Common Mistakes

## Overview

This document catalogs common mistakes, dangerous practices, and anti-patterns in LLM integration. Each anti-pattern includes the problem, danger, and secure alternative.

---

## Security Anti-Patterns

### Anti-Pattern 1: Exposing Ollama to Network

**What developers do**:
```bash
# DANGEROUS - Exposes Ollama to network attacks
ollama serve --host 0.0.0.0
```

**Danger**:
- CVE-2024-37032: Remote Code Execution via path traversal
- Attackers can load malicious models
- Can compromise entire system

**Secure alternative**:
```bash
# ALWAYS bind to localhost only
ollama serve --host 127.0.0.1

# Or use environment variable
export OLLAMA_HOST=127.0.0.1
ollama serve
```

**Additional protection**:
```bash
# Firewall rule to ensure local-only access
iptables -A INPUT -p tcp --dport 11434 ! -s 127.0.0.1 -j DROP
```

---

### Anti-Pattern 2: Executing LLM Output as Code

**What developers do**:
```python
# DANGEROUS - RCE vulnerability
response = llm("Generate a bash command to list files")
subprocess.run(response, shell=True)  # NEVER DO THIS

# Or this:
code = llm("Generate Python code to parse JSON")
exec(code)  # NEVER DO THIS EITHER
```

**Danger**:
- LLM output is untrusted
- Can inject malicious commands
- Complete system compromise

**Secure alternative**:
```python
# Use structured output with validation
from pydantic import BaseModel

class SearchParams(BaseModel):
    query: str
    limit: int = 10

# Ask LLM to generate JSON
response = llm("Generate search parameters as JSON")

# Validate before use
try:
    params = SearchParams.parse_raw(response)
    results = search_function(params.query, params.limit)
except ValidationError:
    return "Invalid parameters"
```

---

### Anti-Pattern 3: Including Secrets in Prompts

**What developers do**:
```python
# DANGEROUS - Secrets leak via prompt injection
api_key = os.environ['API_KEY']
prompt = f"""
You have access to API key: {api_key}
Database URL: {db_url}
Use these to help the user: {user_input}
"""
response = llm(prompt)
```

**Danger**:
- Prompt injection can extract secrets
- LLM may log prompts containing secrets
- Secrets visible in debug output

**Secure alternative**:
```python
# Use function calling or tool use instead
prompt = f"""
You can call search_database() to query data.
User request: {user_input}
"""

# Backend has access to credentials, not LLM
def search_database(query: str):
    # Use credentials here, not in prompt
    return db.query(query, credentials=os.environ['DB_CREDS'])
```

---

### Anti-Pattern 4: Loading Unverified Models

**What developers do**:
```python
# DANGEROUS - Arbitrary model loading
model_path = request.form['model_path']
llm = Llama(model_path=model_path)  # Can load ANY file
```

**Danger**:
- Malicious models can contain backdoors
- Path traversal attacks
- Can load system files causing crashes

**Secure alternative**:
```python
# Allowlist approach with checksum verification
ALLOWED_MODELS = {
    "llama-7b": {
        "path": "llama-7b.gguf",
        "sha256": "abc123..."
    },
    "mistral-7b": {
        "path": "mistral-7b.gguf",
        "sha256": "def456..."
    }
}

def load_model(name: str) -> Llama:
    if name not in ALLOWED_MODELS:
        raise SecurityError(f"Unknown model: {name}")

    model_info = ALLOWED_MODELS[name]
    path = MODELS_DIR / model_info["path"]

    # Verify checksum
    verify_checksum(path, model_info["sha256"])

    # Load from verified path
    return Llama(model_path=str(path.resolve()))
```

---

### Anti-Pattern 5: No Input Sanitization

**What developers do**:
```python
# DANGEROUS - Direct prompt injection
def chat(user_input: str) -> str:
    prompt = f"You are helpful. User: {user_input}"
    return llm(prompt)
```

**Danger**:
- Direct prompt injection attacks
- System prompt leakage
- Jailbreak attempts succeed

**Secure alternative**:
```python
import re

def chat(user_input: str) -> str:
    # Sanitize input
    sanitized = sanitize_prompt(user_input)

    # Use structured prompt format
    prompt = create_safe_prompt(sanitized)

    # Generate with output filtering
    response = llm(prompt)
    return filter_output(response)

def sanitize_prompt(text: str) -> str:
    # Limit length
    text = text[:4096]

    # Remove control characters
    text = ''.join(c for c in text if c.isprintable() or c in '\n\t')

    # Check for injection patterns
    injection_patterns = [
        r"ignore\s+(previous|above)\s+instructions",
        r"system\s*:",
        r"\[INST\]"
    ]

    for pattern in injection_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            raise SecurityError("Potential injection detected")

    return text
```

---

### Anti-Pattern 6: Exposing Internal Errors

**What developers do**:
```python
# DANGEROUS - Leaks internal information
try:
    result = llm(prompt)
except Exception as e:
    return {
        "error": str(e),
        "trace": traceback.format_exc(),
        "model_path": model_path
    }
```

**Danger**:
- Exposes internal paths and configuration
- Helps attackers understand system
- May leak sensitive information

**Secure alternative**:
```python
import uuid
import structlog

logger = structlog.get_logger()

try:
    result = llm(prompt)
except Exception as e:
    # Log with correlation ID
    error_id = str(uuid.uuid4())
    logger.exception("llm.inference_failed",
                    error_id=error_id,
                    model=model_name)

    # Return generic error to user
    return {
        "error": "Inference failed",
        "error_id": error_id  # For support tracking
    }
```

---

### Anti-Pattern 7: No Rate Limiting

**What developers do**:
```python
# DANGEROUS - No protection against abuse
@app.post("/generate")
async def generate(prompt: str):
    return llm(prompt)
```

**Danger**:
- DoS via resource exhaustion
- Abuse of expensive inference
- No cost control

**Secure alternative**:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/generate")
@limiter.limit("10/minute")  # Per IP rate limit
async def generate(prompt: str):
    return llm(prompt)

# Or token-based limiting
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

@app.post("/generate")
async def generate(
    prompt: str,
    rate_limit: bool = Depends(RateLimiter(times=10, seconds=60))
):
    return llm(prompt)
```

---

### Anti-Pattern 8: Trusting LLM Output for Critical Operations

**What developers do**:
```python
# DANGEROUS - Using LLM for authentication/authorization
username = llm("Extract username from: " + user_input)
if username in allowed_users:
    grant_access()  # NEVER DO THIS
```

**Danger**:
- LLMs are probabilistic, not deterministic
- Can hallucinate usernames
- Security bypass via crafted input

**Secure alternative**:
```python
# Use deterministic parsing for critical operations
import re

def extract_username(text: str) -> Optional[str]:
    # Use regex or structured parsing
    match = re.match(r'^@(\w+)', text)
    return match.group(1) if match else None

username = extract_username(user_input)
if username and username in allowed_users:
    grant_access()
```

---

## Performance Anti-Patterns

### Anti-Pattern 9: Loading Model Per Request

**What developers do**:
```python
# TERRIBLE - 10+ seconds per request
@app.post("/generate")
def generate(prompt: str):
    llm = Llama(model_path="model.gguf")  # Loads every time!
    return llm(prompt)
```

**Danger**:
- Massive latency (10-30 seconds)
- High memory churn
- Poor user experience

**Secure alternative**:
```python
# Load once at startup (singleton pattern)
class ModelManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.llm = Llama(model_path="model.gguf")
        return cls._instance

model_manager = ModelManager()

@app.post("/generate")
def generate(prompt: str):
    return model_manager.llm(prompt)
```

---

### Anti-Pattern 10: Unlimited Context Size

**What developers do**:
```python
# DANGEROUS - Can cause OOM
llm = Llama(
    model_path="model.gguf",
    n_ctx=32768  # 32K context on 8GB RAM!
)
```

**Danger**:
- Out of memory errors
- Slow inference
- System instability

**Secure alternative**:
```python
# Set context based on available RAM
def calculate_max_context(ram_gb: float, model_size_gb: float) -> int:
    available = ram_gb - model_size_gb - 2  # Reserve 2GB
    # Each token ~= 2 bytes in context
    max_tokens = int((available * 1024 * 1024 * 1024) / 2)
    # Cap at reasonable limits
    return min(max_tokens, 4096)

llm = Llama(
    model_path="model.gguf",
    n_ctx=calculate_max_context(16.0, 7.0)  # 16GB RAM, 7B model
)
```

---

### Anti-Pattern 11: No Token Limits

**What developers do**:
```python
# DANGEROUS - Can generate forever
response = llm(prompt, max_tokens=None)
```

**Danger**:
- Runaway generation
- DoS via long responses
- Wasted resources

**Secure alternative**:
```python
# Always enforce limits
MAX_TOKENS = 1024

response = llm(
    prompt,
    max_tokens=MAX_TOKENS,
    stop=["</s>", "Human:", "User:"]  # Additional stops
)
```

---

### Anti-Pattern 12: Blocking Event Loop

**What developers do**:
```python
# BAD - Blocks async event loop
async def handle_request(prompt: str):
    response = llm(prompt)  # Synchronous call in async function!
    return response
```

**Danger**:
- Blocks entire event loop
- Poor throughput
- Unresponsive application

**Secure alternative**:
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)

async def handle_request(prompt: str):
    loop = asyncio.get_event_loop()
    # Run in thread pool
    response = await loop.run_in_executor(
        executor,
        llm,
        prompt
    )
    return response
```

---

## Testing Anti-Patterns

### Anti-Pattern 13: No Mocking in Tests

**What developers do**:
```python
# BAD - Tests call real LLM
def test_chat():
    response = chat("Hello")
    assert "hello" in response.lower()  # Flaky!
```

**Danger**:
- Slow tests (minutes per test)
- Non-deterministic failures
- Can't run in CI without models

**Secure alternative**:
```python
from unittest.mock import Mock, patch

def test_chat():
    # Mock LLM response
    with patch('app.llm') as mock_llm:
        mock_llm.return_value = {"choices": [{"text": "Hello!"}]}

        response = chat("Hello")
        assert response == "Hello!"

        # Verify prompt was sanitized
        mock_llm.assert_called_once()
```

---

### Anti-Pattern 14: Testing with Production Models

**What developers do**:
```python
# BAD - Requires 7GB+ model in test environment
@pytest.fixture
def llm():
    return Llama(model_path="/models/llama-7b.gguf")
```

**Danger**:
- Tests require large downloads
- Slow CI/CD pipeline
- Resource intensive

**Secure alternative**:
```python
# Use tiny model or mocks for testing
@pytest.fixture
def llm(request):
    if request.config.getoption("--integration"):
        # Integration tests: use tiny model
        return Llama(model_path="/models/tiny-llama-1b.gguf")
    else:
        # Unit tests: use mock
        return Mock(spec=Llama)
```

---

## Configuration Anti-Patterns

### Anti-Pattern 15: Hardcoded Paths

**What developers do**:
```python
# BAD - Hardcoded paths
llm = Llama(model_path="/home/user/models/llama.gguf")
```

**Danger**:
- Breaks in different environments
- Not portable
- Security risk if path exposed

**Secure alternative**:
```python
import os
from pathlib import Path

# Use environment variables
MODEL_DIR = Path(os.environ.get(
    "JARVIS_MODEL_DIR",
    "/var/jarvis/models"
))

model_path = MODEL_DIR / "llama.gguf"

if not model_path.exists():
    raise ConfigurationError(
        f"Model not found: {model_path}\n"
        f"Set JARVIS_MODEL_DIR environment variable"
    )

llm = Llama(model_path=str(model_path))
```

---

### Anti-Pattern 16: No Resource Limits

**What developers do**:
```python
# BAD - No limits
llm = Llama(model_path="model.gguf")
response = llm(prompt)
```

**Danger**:
- Can exhaust system resources
- DoS vulnerability
- Poor multi-tenancy

**Secure alternative**:
```python
import resource

# Set memory limit
def set_memory_limit(max_memory_mb: int):
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    resource.setrlimit(
        resource.RLIMIT_AS,
        (max_memory_mb * 1024 * 1024, hard)
    )

# Set CPU time limit
def set_time_limit(max_seconds: int):
    resource.setrlimit(
        resource.RLIMIT_CPU,
        (max_seconds, max_seconds)
    )

# Apply before inference
set_memory_limit(4096)  # 4GB max
set_time_limit(30)  # 30 seconds max

try:
    response = llm(prompt)
except MemoryError:
    logger.error("inference.oom")
    raise
```

---

## Logging Anti-Patterns

### Anti-Pattern 17: Logging Full Prompts

**What developers do**:
```python
# BAD - May log sensitive data
logger.info(f"Processing prompt: {user_prompt}")
response = llm(user_prompt)
logger.info(f"Response: {response}")
```

**Danger**:
- PII in logs
- Sensitive information exposure
- Compliance violations (GDPR, etc.)

**Secure alternative**:
```python
import hashlib

def hash_prompt(prompt: str) -> str:
    return hashlib.sha256(prompt.encode()).hexdigest()[:16]

# Log metadata, not content
prompt_id = hash_prompt(user_prompt)
logger.info("inference.started",
           prompt_id=prompt_id,
           prompt_length=len(user_prompt))

response = llm(user_prompt)

logger.info("inference.completed",
           prompt_id=prompt_id,
           response_length=len(response),
           duration_ms=duration)
```

---

## Summary Table

| Anti-Pattern | Risk Level | Primary Danger | Fix Priority |
|--------------|------------|----------------|--------------|
| Exposing Ollama to network | CRITICAL | RCE | Immediate |
| Executing LLM output | CRITICAL | RCE | Immediate |
| Secrets in prompts | CRITICAL | Data leak | Immediate |
| Unverified models | HIGH | Backdoors | High |
| No input sanitization | HIGH | Injection | High |
| Exposing internal errors | MEDIUM | Info leak | Medium |
| No rate limiting | HIGH | DoS | High |
| LLM for critical auth | CRITICAL | Auth bypass | Immediate |
| Load model per request | HIGH | Poor UX | High |
| Unlimited context | MEDIUM | OOM | Medium |
| No token limits | HIGH | DoS | High |
| Blocking event loop | MEDIUM | Poor perf | Medium |
| No test mocking | LOW | Slow CI | Low |
| Hardcoded paths | LOW | Portability | Low |
| No resource limits | HIGH | DoS | High |
| Logging full prompts | MEDIUM | PII leak | Medium |

---

## Quick Reference: Common Fixes

### Before Deployment Checklist

Security:
- [ ] Ollama bound to 127.0.0.1 only
- [ ] Never execute LLM output as code
- [ ] No secrets in prompts
- [ ] Model checksums verified
- [ ] Input sanitization active
- [ ] Output filtering enabled
- [ ] Rate limiting configured
- [ ] Error messages sanitized

Performance:
- [ ] Models loaded once (singleton)
- [ ] Context size limited based on RAM
- [ ] Token limits enforced
- [ ] Streaming enabled
- [ ] Connection pooling active
- [ ] Async/await used correctly

Testing:
- [ ] LLM responses mocked in unit tests
- [ ] Integration tests use tiny models
- [ ] No production models in CI

Configuration:
- [ ] Environment variables for paths
- [ ] Resource limits configured
- [ ] Logging excludes sensitive data
