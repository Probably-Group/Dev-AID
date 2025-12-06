---
name: fastapi
description: REST API and WebSocket development with FastAPI emphasizing security, performance, and async patterns
risk_level: HIGH
---

# FastAPI Development Skill

## File Organization

- **SKILL.md**: Core principles, patterns, essential security (this file)
- **references/security-examples.md**: CVE details and OWASP implementations
- **references/advanced-patterns.md**: Advanced FastAPI patterns
- **references/threat-model.md**: Attack scenarios and STRIDE analysis
- **references/performance-optimization.md**: Database pooling, caching, pagination, background tasks
- **references/testing-guide.md**: TDD workflow, security tests, integration tests
- **references/anti-patterns.md**: Common mistakes and how to avoid them

## Validation Gates

### Gate 0.2: Vulnerability Research (BLOCKING for HIGH-RISK)
- **Status**: PASSED (5+ CVEs documented)
- **Research Date**: 2025-11-20
- **CVEs**: CVE-2024-47874, CVE-2024-12868, CVE-2023-30798, Starlette DoS variants

---

## 0. Anti-Hallucination Protocol

**🚨 MANDATORY: Read before implementing any FastAPI code**

### Verification Requirements

When implementing FastAPI features, you MUST:

1. **Verify Before Implementing**
   - ✅ Check official FastAPI/Starlette documentation
   - ✅ Confirm security patterns are current
   - ✅ Validate middleware and dependency injection patterns
   - ❌ Never guess configuration options
   - ❌ Never invent middleware or dependency functions
   - ❌ Never assume package compatibility without checking

2. **Use Available Tools**
   - 🔍 Read: Check existing codebase for patterns
   - 🔍 Grep: Search for similar implementations
   - 🔍 WebSearch: Verify specs in official docs
   - 🔍 WebFetch: Read official FastAPI documentation

3. **Verify if Certainty < 80%**
   - If uncertain about ANY FastAPI feature/config/pattern
   - STOP and verify before implementing
   - Document verification source in response
   - Errors in FastAPI can cause security vulnerabilities, DoS, data breaches

4. **Common FastAPI Hallucination Traps** (AVOID)
   - ❌ Inventing Pydantic validator methods
   - ❌ Making up FastAPI dependency injection patterns
   - ❌ Creating non-existent middleware parameters
   - ❌ Assuming JWT library methods without verification
   - ❌ Guessing SQLAlchemy async patterns
   - ❌ Inventing security header configurations

### Self-Check Checklist

Before EVERY response with FastAPI code:
- [ ] All Pydantic models verified against official docs
- [ ] Dependency injection patterns verified
- [ ] Security configurations verified (CORS, headers, rate limiting)
- [ ] Async patterns verified (database, HTTP clients)
- [ ] Can cite official documentation sources

**⚠️ CRITICAL**: FastAPI code with hallucinated patterns causes production outages, security breaches, and data corruption. Always verify.

---


### 0.4 Progressive Disclosure (500-Line Limit)

**⚠️ CRITICAL**: This SKILL.md file MUST stay <500 lines for Claude Code to load it.

**If this file is approaching 500 lines**:
- Move detailed examples to `references/advanced-patterns.md`
- Move security examples to `references/security-examples.md`
- Move troubleshooting to `references/troubleshooting.md`
- Keep only summaries and links in main file

📚 **For complete progressive disclosure guide**: See `../../../template-references/progressive-disclosure.md`

---

## 1. Overview

**Risk Level**: HIGH

**Justification**: FastAPI applications handle authentication, database access, file uploads, and external API communication. DoS vulnerabilities in Starlette, injection risks, and improper validation can compromise availability and security.

You are an expert FastAPI developer creating secure, performant REST APIs and WebSocket services. You configure proper validation, authentication, and security headers.

### Core Expertise Areas
- Pydantic validation and dependency injection
- Authentication: OAuth2, JWT, API keys
- Security headers and CORS configuration
- Rate limiting and DoS protection
- Database integration with async ORMs
- WebSocket security

---

## 2. Core Responsibilities

### Fundamental Principles

1. **TDD First**: Write tests before implementation code
2. **Performance Aware**: Connection pooling, caching, async patterns
3. **Validate Everything**: Use Pydantic models for all inputs
4. **Secure by Default**: HTTPS, security headers, strict CORS
5. **Rate Limit**: Protect all endpoints from abuse
6. **Authenticate & Authorize**: Verify identity and permissions
7. **Handle Errors Safely**: Never leak internal details

---

## 3. Technical Foundation

### Version Recommendations

| Component | Version | Notes |
|-----------|---------|-------|
| **FastAPI** | 0.115.3+ | CVE-2024-47874 fix |
| **Starlette** | 0.40.0+ | DoS vulnerability fix |
| **Pydantic** | 2.0+ | Better validation |
| **Python** | 3.11+ | Performance |

### Security Dependencies

```toml
[project]
dependencies = [
    "fastapi>=0.115.3",
    "starlette>=0.40.0",
    "pydantic>=2.5",
    "python-jose[cryptography]>=3.3",
    "passlib[argon2]>=1.7",
    "python-multipart>=0.0.6",
    "slowapi>=0.1.9",
    "secure>=0.3",
]
```

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

## 5. Core Implementation Patterns

app = FastAPI(
    title="Secure API",
    docs_url=None if PRODUCTION else "/docs",  # Disable in prod
    redoc_url=None,
)

📚 **For complete details**: See `references/core-implementation-patterns.md`

---
## 6. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```python
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_create_item_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/items",
            json={"name": "Test Item", "price": 29.99},
            headers={"Authorization": "Bearer valid_token"}
        )
        assert response.status_code == 201
        assert "id" in response.json()
```

### Step 2: Implement Minimum to Pass

```python
@app.post("/items", status_code=201)
async def create_item(
    item: ItemCreate,
    user: User = Depends(get_current_user)
) -> ItemResponse:
    created = await item_service.create(item, user.id)
    return ItemResponse.from_orm(created)
```

### Step 3: Refactor if Needed

Improve code quality while keeping tests green.

### Step 4: Run Full Verification

```bash
pytest --cov=app --cov-report=term-missing
mypy app --strict
bandit -r app -ll
```

See `references/testing-guide.md` for comprehensive testing patterns.

---

## 7. Security Standards

### 6.1 Domain Vulnerability Landscape

| CVE ID | Severity | Description | Mitigation |
|--------|----------|-------------|------------|
| CVE-2024-47874 | HIGH | Starlette multipart DoS via memory exhaustion | Upgrade Starlette 0.40.0+ |
| CVE-2024-12868 | HIGH | Downstream DoS via fastapi dependency | Upgrade FastAPI 0.115.3+ |
| CVE-2023-30798 | HIGH | Starlette <0.25 DoS | Upgrade FastAPI 0.92+ |

### 6.2 OWASP Top 10 Mapping

| Category | Risk | Mitigations |
|----------|------|-------------|
| A01 Access Control | HIGH | Dependency injection for auth, permission decorators |
| A02 Crypto Failures | HIGH | JWT with proper algorithms, Argon2 passwords |
| A03 Injection | HIGH | Pydantic validation, parameterized queries |
| A04 Insecure Design | MEDIUM | Type safety, validation layers |
| A05 Misconfiguration | HIGH | Security headers, disable docs in prod |
| A06 Vulnerable Components | CRITICAL | Keep Starlette/FastAPI updated |
| A07 Auth Failures | HIGH | Rate limiting on auth, secure JWT |

See `references/security-examples.md` for detailed implementations.

### 6.3 Error Handling

```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    # Log full details
    logger.error(f"Unhandled error: {exc}", exc_info=True)

    # Return safe message
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
```

---

## 8. Performance Guidelines

### Key Performance Patterns

1. **Connection Pooling**: Always use database connection pools (asyncpg, SQLAlchemy async)
2. **Concurrent Requests**: Use `asyncio.gather()` for independent async operations
3. **Response Caching**: Cache expensive operations with Redis or in-memory
4. **Pagination**: Never return entire collections, use cursor-based pagination
5. **Background Tasks**: Offload heavy operations (>2s) to background tasks

See `references/performance-optimization.md` for detailed implementations and benchmarks.

---

## 9. References

### Complete Reference Documentation

- **`references/advanced-patterns.md`**: Dependency injection, WebSocket, streaming responses, OpenAPI customization
- **`references/security-examples.md`**: CVE mitigations, OWASP implementations, API key auth
- **`references/threat-model.md`**: STRIDE analysis, attack scenarios, security controls
- **`references/performance-optimization.md`**: Connection pooling, caching, pagination, background tasks
- **`references/testing-guide.md`**: TDD workflow, security tests, integration tests, mocking
- **`references/anti-patterns.md`**: Common mistakes and ## 6. Implementation Workflow (TDD)

@pytest.mark.asyncio
async def test_create_item_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/items",
            json={"name": "Test Item", "price": 29.99},
            headers={"Authori...

📚 **For complete details**: See `references/implementation-workflow-tdd.md`

---
