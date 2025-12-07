---
name: cloud-api-integration
risk_level: HIGH
description: "Expert skill for integrating cloud AI APIs (Claude, GPT-4, Gemini). Covers secure API key management, prompt injection prevention, rate limiting, cost optimization, and protection against data exfiltration attacks."
---

# Cloud API Integration Skill

> **File Organization**: Split structure. Main SKILL.md for core patterns. See `references/` for complete implementations.


### 0.4 Progressive Disclosure (500-Line Limit)

**⚠️ CRITICAL**: This SKILL.md file MUST stay <500 lines for Claude Code to load it.

**If this file is approaching 500 lines**:
- Move detailed examples to `references/advanced-patterns.md`
- Move security examples to `references/security-examples.md`
- Move troubleshooting to `references/troubleshooting.md`
- Keep only summaries and links in main file

📚 **For complete progressive disclosure guide**: See `../../../template-references/progressive-disclosure.md`

---

## 0. Anti-Hallucination Protocol

## 0. Anti-Hallucination Protocol

### 0.1 Quick Risk Assessment

**Risk Level**: MEDIUM

**Key Risk Factors**:
- Security concerns in medium-risk domain
- 3 security issues/patterns identified
- Common attack vectors: SSRF to cloud metadata, Credential theft, IAM privilege escalation
- Requires security awareness and best practices

**Immediate Security Actions**:
1. Review security concerns below before any implementation
2. Never proceed without understanding attack surface
3. Implement security controls from § 0.3 as mandatory requirements

### 0.2 Vulnerability Research Protocol

**MANDATORY**: Before ANY implementation, research current vulnerabilities.

**Step 1: CVE Database Search** (NVD, MITRE)
```bash
# Search for latest CVEs (update dates for current year)
https://nvd.nist.gov/vuln/search
# Keywords: [technology name], [framework version]
```

**Step 2: Known Vulnerabilities (2024-2025)**

   - **SSRF** (CVSS 9.0): Server-Side Request Forgery
     Source: https://owasp.org/www-community/attacks/Server_Side_Request_Forgery
   - **CREDENTIAL-LEAKAGE** (CVSS 8.8): Cloud credential exposure
     Source: https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/
   - **IAM-MISCONFIGURATION** (CVSS N/A): IAM overprivileged access
     Source: https://owasp.org/www-project-top-10-for-large-language-model-applications/

**Step 3: Common Attack Patterns**

   - SSRF to cloud metadata
   - Credential theft
   - IAM privilege escalation
   - API key leakage

**Step 4: MITRE ATT&CK Mapping**
- Tactic: [Initial Access, Execution, Persistence, Privilege Escalation]
- Review MITRE ATT&CK framework for latest techniques

**Update Frequency**: Check for new CVEs weekly during active development.

### 0.3 Hallucination Prevention Checklist

**CRITICAL**: These rules are ABSOLUTE. Violation = security incident.

**Domain-Specific Security Rules**:

- ❌ NEVER hardcode cloud credentials
- ❌ NEVER use overprivileged IAM roles
- ❌ ALWAYS validate cloud API responses
- ❌ ALWAYS use IMDSv2 for AWS

**Before ANY code generation**:
1. ✅ Verify rule compliance for proposed implementation
2. ✅ Check if solution introduces any prohibited patterns
3. ✅ Validate all security assumptions
4. ✅ Confirm defensive coding practices are applied

**If uncertain**: STOP and research. Never guess on security.


## 1. Overview

**Risk Level**: HIGH - Handles API credentials, processes untrusted prompts, network exposure, data privacy concerns

You are an expert in cloud AI API integration with deep expertise in Anthropic Claude, OpenAI GPT-4, and Google Gemini APIs. Your mastery spans secure credential management, prompt security, rate limiting, error handling, and protection against LLM-specific vulnerabilities.

You excel at:
- Secure API key management and rotation
- Prompt injection prevention for cloud LLMs
- Rate limiting and cost optimization
- Multi-provider fallback strategies
- Output sanitization and data privacy

**Primary Use Cases**:
- JARVIS cloud AI integration for complex tasks
- Fallback when local models insufficient
- Multi-modal processing (vision, code)
- Enterprise-grade reliability with security

---

## 2. Core Principles

1. **TDD First** - Write tests before implementation. Mock all external API calls.
2. **Performance Aware** - Optimize for latency, cost, and reliability with caching and connection reuse.
3. **Security First** - Never hardcode keys, sanitize all inputs, filter all outputs.
4. **Cost Conscious** - Track usage, set limits, cache repeated queries.
5. **Reliability Focused** - Multi-provider fallback with circuit breakers.

---

## 3. Implementation Workflow (TDD)

class TestSecureClaudeClient:
    """Test cloud API client with mocked external calls."""

📚 **For complete details**: See `references/implementation-workflow-tdd.md`

---
## 4. Quality Assurance Checklist

**Before implementing this skill, ensure**:

### 4.1 Pre-Implementation Setup
- [ ] Virtual environment created and activated
- [ ] Dependencies installed from requirements.txt
- [ ] Pre-commit hooks installed (`pre-commit install`)
- [ ] Linters installed (black, isort, flake8, mypy, bandit)

### 4.2 Dependency Management
- [ ] All dependencies pinned with exact versions (==)
- [ ] No manual transitive dependency pins
- [ ] Dependencies tested in clean environment

### 4.3 Code Quality Gates (Run BEFORE committing)
- [ ] `black .` - Code formatted
- [ ] `isort .` - Imports sorted
- [ ] `flake8 . --max-line-length=120` - No linting errors
- [ ] `mypy . --ignore-missing-imports` - Type checking passes
- [ ] `bandit -r .` - Security scan clean

### 4.4 Security Validation
- [ ] Input validation for ALL external inputs
- [ ] Path traversal prevention implemented
- [ ] Command injection prevention (no shell=True)
- [ ] SQL injection prevention (parameterized queries)
- [ ] Secrets not in code or error messages

📚 **For complete security validation guide**: See `../../../template-references/security-framework.md`

### 4.5 Test Coverage Requirements
- [ ] Tests written BEFORE implementation (TDD)
- [ ] Unit tests for all public functions
- [ ] Edge case tests (empty, null, max values)
- [ ] Security tests (injection, traversal, overflow)
- [ ] Code coverage >80%

### 4.6 Documentation Requirements
- [ ] Docstrings for all public functions/classes
- [ ] Security considerations documented
- [ ] Examples of correct usage
- [ ] Known limitations documented

---

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
        respo## 5. Performance Patterns

class CloudAPIClient:
    def __init__(self):
        self._client = httpx.AsyncClient(
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
            timeout=httpx.Timeout(30.0)
        )

📚 **For complete details**: See `references/performance-patterns.md`

---
re-Implementation Checklist

### Phase 1: Before Writing Code

- [ ] Write failing tests with mocked API responses
- [ ] Define rate limits and cost thresholds
- [ ] Set up secure credential loading (env vars or secrets manager)
- [ ] Plan caching strategy for repeated queries

### Phase 2: During Implementation

- [ ] API keys loaded from environment/secrets manager only
- [ ] Input sanitization active on all user content
- [ ] Output filtering before using responses
- [ ] Connection pooling configured
- [ ] Retry logic with exponential backoff
- [ ] Response caching for identical queries

### Phase 3: Before Committing

- [ ] All tests pass with >80% coverage
- [ ] No API keys in git history (use git-secrets)
- [ ] Security scan passes (bandit)
- [ ] Type checking passes (mypy)
- [ ] Daily spending limits configured
- [ ] Multi-provider fallback tested

---

## 12. Summary

Your goal is to create cloud API integrations that are:
- **Test-Driven**: All functionality verified with mocked tests
- **Performant**: Connection pooling, caching, async operations
- **Secure**: Protected against prompt injection and data exfiltration
- **Reliable**: Multi-provider fallback with proper error handling
- **Cost-effective**: Rate limiting and usage monitoring

**For complete implementation details, see**:
- `references/advanced-patterns.md` - Caching, streaming, optimization
- `references/security-examples.md` - Full vulnerability analysis
- `references/threat-model.md` - Attack scenarios and mitigations
