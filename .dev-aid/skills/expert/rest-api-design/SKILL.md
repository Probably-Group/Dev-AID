# REST API Design Skill

```yaml
name: rest-api-design-expert
risk_level: MEDIUM
description: Expert in RESTful API design, resource modeling, HTTP semantics, pagination, versioning, and secure API implementation
version: 1.0.0
author: JARVIS AI Assistant
tags: [api, rest, http, design, web-services]
```

---


## 0. Anti-Hallucination Protocol

### 0.1 Quick Risk Assessment

**Risk Level**: MEDIUM

**Key Risk Factors**:
- Active exploitation of critical vulnerabilities in production (CVSS 7.5+)
- 3 high-severity CVEs discovered in 2024-2025
- Common attack vectors: OWASP API Top 10 2023 attacks, IDOR attacks via predictable IDs, Rate limit bypass techniques
- Requires continuous monitoring of security advisories

**Immediate Security Actions**:
1. Review recent CVEs below before any implementation
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

   - **OWASP-API-2023-01** (CVSS N/A): BOLA (Broken Object Level Authorization) - 40% of attacks
     Source: https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/
   - **OWASP-API-2023-06** (CVSS N/A): Unrestricted access to business flows (NEW in 2023)
     Source: https://owasp.org/API-Security/editions/2023/en/0xa6-unrestricted-access-to-sensitive-business-flows/
   - **OWASP-API-2023-07** (CVSS N/A): Server-Side Request Forgery (NEW in 2023)
     Source: https://owasp.org/API-Security/editions/2023/en/0xa7-server-side-request-forgery/

**Step 3: Common Attack Patterns**

   - OWASP API Top 10 2023 attacks
   - IDOR attacks via predictable IDs
   - Rate limit bypass techniques
   - Mass assignment vulnerabilities
   - SSRF via webhook callbacks

**Step 4: MITRE ATT&CK Mapping**
- Tactic: [Initial Access, Execution, Persistence, Privilege Escalation]
- Review MITRE ATT&CK framework for latest techniques

**Update Frequency**: Check for new CVEs weekly during active development.

### 0.3 Hallucination Prevention Checklist

**CRITICAL**: These rules are ABSOLUTE. Violation = security incident.

**Domain-Specific Security Rules**:

- ❌ NEVER use sequential IDs for resources
- ❌ NEVER expose internal endpoints publicly
- ❌ NEVER trust HTTP headers for authorization
- ❌ ALWAYS implement object-level authorization
- ❌ ALWAYS validate and sanitize webhook URLs

**Before ANY code generation**:
1. ✅ Verify rule compliance for proposed implementation
2. ✅ Check if solution introduces any prohibited patterns
3. ✅ Validate all security assumptions against current CVEs
4. ✅ Confirm defensive coding practices are applied

**If uncertain**: STOP and research. Never guess on security.

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

**Risk Level**: MEDIUM-RISK

**Justification**: REST APIs expose business logic, handle authentication, and process user data. Poor design leads to security vulnerabilities, data exposure, and injection attacks.

You are an expert in **RESTful API design**. You create well-structured, secure, and performant APIs following HTTP semantics and industry best practices.

### Core Expertise
- Resource modeling, URI design, HTTP semantics
- Pagination, filtering, versioning
- Security best practices (BOLA, injection, validation)

### Primary Use Cases
- Designing and refactoring REST APIs
- API documentation and security hardening

**File Organization**: Core concepts here; see `references/security-examples.md` for CVE mitigations and detailed patterns.

---

## 2. Core Responsibilities

### Core Principles
1. **TDD First**: Write API tests before implementation
2. **Performance Aware**: Optimize for latency, throughput, and efficiency
3. **Security by Design**: Protect endpoints from common attacks
4. **Resource-Oriented**: Model resources, not actions

### Fundamental Duties
1. **Resource-Oriented Design**: Model resources, not actions
2. **HTTP Semantics**: Use correct methods and status codes
3. **Consistent Conventions**: Follow naming and structure patterns
4. **Security by Design**: Protect endpoints from common attacks

### Design Principles
- **Nouns, not verbs**: `/users/{id}` not `/getUser/{id}`
- **Plural resources**: `/users` not `/user`
- **Hierarchical relationships**: `/users/{id}/orders`
- **Stateless operations**: No server-side session state

---

## 3. Technical Foundation

### HTTP Methods

| Method | Purpose | Idempotent | Safe | Request Body |
|--------|---------|------------|------|--------------|
| GET | Retrieve resource | Yes | Yes | No |
| POST | Create resource | No | No | Yes |
| PUT | Replace resource | Yes | No | Yes |
| PATCH | Partial update | No | No | Yes |
| DELETE | Remove resource | Yes | No | No |

### Status Codes

**Success (2xx)**: `200 OK`, `201 Created`, `204 No Content`

**Client Error (4xx)**: `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `409 Conflict`, `422 Unprocessable Entity`, `429 Too Many Requests`

**Server Error (5xx)**: `500 Internal Server Error`, `503 Service Unavailable`

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

## 5. Implementation Patterns

// Instance operations
GET    /api/v1/users/{id}         // Get user
PUT    /api/v1/users/{id}         // Replace user
PATCH  /api/v1/users/{id}         // Update user
DELETE /api/v1/users/{id}         // Delete user

📚 **For complete details**: See `references/implementation-patterns.md`

---
## 6. Implementation Workflow (TDD)

### Step-by-Step TDD Process

Follow this workflow for every API endpoint:

#### Step 1: Write Failing Test First

```python
# tests/test_users_api.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_user_returns_201():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.post("/api/v1/users", json={"name": "John", "email": "john@example.com"})
    assert response.status_code == 201
    assert "id" in response.json()["data"]

@pytest.mark.asyncio
async def test_create_user_validates_email():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.post("/api/v1/users", json={"name": "John", "email": "invalid"})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_get_user_requires_auth():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/api/v1/users/123")
    assert response.status_code == 401
```

#### Step 2: Implement Minimum to Pass

```python
# app/routers/users.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/api/v1/users", tags=["users"])

class CreateUserRequest(BaseModel):
    name: str
    email: EmailStr

@router.post("", status_code=201)
async def create_user(request: CreateUserRequest):
    user = await db.users.create(request.model_dump())
    return {"data": {"id": user.id, "name": user.name, "email": user.email}}
```

#### Step 3: Refactor and Add Edge Cases

```python
@pytest.mark.asyncio
async def test_get_user_prevents_bola():
    async with AsyncClient(app=app, base_url="http://testserver") as clien## 6. Implementation Workflow (TDD)

## 6. Implementation Workflow (TDD)

📚 **For complete details**: See `references/implementation-workflow-tdd.md`

---
press responses > 1KB
```

### 6.4 Rate Limiting

```python
# BAD: No rate limiting
@router.post("/api/auth/login")
async def login(credentials: LoginRequest):
    return await authenticate(credentials)

# GOOD: Tiered rate limiting with slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/api/auth/login")
@limiter.limit("5/minute")  # Strict for auth
async def login(request: Request, credentials: LoginRequest):
    return await authenticate(credentials)

@router.get("/api/v1/users")
@limiter.limit("100/minute")  # Standard for API
async def list_users(request: Request):
    return await get_users()
```

### 6.5 Connection Keep-Alive

```python
# BAD: Creating new connections per request
async def call_external_api():
    async with httpx.AsyncClient() as client:  # New connection each time
        return await client.get("https://api.example.com/data")

# GOOD: App-level client with connection pooling
http_client: httpx.AsyncClient | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global http_client
    http_client = httpx.AsyncClient(
        limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
    )
    yield
    await http_client.aclose()

app = FastAPI(lifespan=lifespan)
```

---

## 8. Security Standards

> **See** `references/security-examples.md` for complete CVE details and mitigation patterns.

### Top API Vulnerabilities
- **BOLA**: Accessing other users' resources without authorization
- **Mass Assignment**: Updating protected fields via request body
- **Injection**: SQL/NoSQL injection via parameters
- **Excessive Data Exposure**: Returning sensitive fields

### Input Validation & Authorization

```typescript
import { z } from "zod";

const CreateUserSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
  password: z.string().min(12).max(100)
});

app.post("/api/v1/users", async (req, res) => {
  const validation = CreateUserSchema.safeParse(req.body);
  if (!validation.success) {
    return res.status(422).json({ error: { code: "VALIDATION_ERROR", details: validation.error.errors }});
  }
  res.status(201).json({ data: await createUser(validation.data) });
});

// BOLA prevention - always check obje## 7. Performance Patterns

## 7. Performance Patterns

📚 **For complete details**: See `references/performance-patterns.md`

---
s
- [ ] Authentication and error codes documented
- [ ] CORS configured restrictively, HTTPS enforced
- [ ] Performance tested with expected load

---

## 12. Summary

Design REST APIs that are **Intuitive** (REST conventions, HTTP semantics), **Secure** (validate inputs, authorize access, filter outputs), and **Consistent** (uniform responses, errors, pagination).

**Security Essentials**: Check object-level authorization, validate input with schemas, filter output fields, use parameterized queries, implement rate limiting.

Build APIs that are secure by default and easy to use correctly.
