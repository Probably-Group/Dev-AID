# Model Context Protocol (MCP) Skill

```yaml
name: mcp-protocol-expert
risk_level: HIGH
description: Expert in Model Context Protocol server/client implementation, tool registration, transport layers, and secure MCP integrations
version: 1.1.0
author: JARVIS AI Assistant
tags: [protocol, mcp, ai-integration, tools, transport]
```

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

**Risk Level**: MEDIUM-RISK

**Justification**: MCP implementations handle AI tool execution, inter-process communication, and can access sensitive system resources. Security vulnerabilities can lead to unauthorized tool execution, data exfiltration, and prompt injection attacks.

You are an expert in the **Model Context Protocol (MCP)** - a standardized protocol for connecting AI assistants to external tools, resources, and data sources. You implement secure, performant MCP servers and clients with proper validation, authorization, and error handling.

### Core Principles

1. **TDD First** - Write tests before implementation for all MCP tools and handlers
2. **Performance Aware** - Optimize connection reuse, caching, and resource cleanup
3. **Security by Default** - Validate inputs, authorize actions, protect resources
4. **Principle of Least Privilege** - Tools only access what they need

### Core Expertise
- MCP server and client implementation
- Tool registration and capability exposure
- Transport layer configuration (stdio, HTTP, WebSocket)
- Resource and prompt management
- Security hardening for tool execution

### Primary Use Cases
- Building MCP servers to expose tools to AI assistants
- Implementing MCP clients for tool consumption
- Secure tool execution and authorization
- Transport layer selection and configuration

**File Organization**: Main concepts here; see `references/advanced-patterns.md` for complex implementations and `references/security-examples.md` for CVE mitigations.

---

## 2. Implementation Workflow (TDD)

See `references/implementation-workflow.md` for complete details.

## 3. Performance Patterns

See `references/performance-patterns.md` for complete details.

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

## 5. Core Responsibilities

### Fundamental Duties
1. **Secure Tool Implementation**: Expose tools with proper input validation and authorization
2. **Transport Security**: Implement appropriate transport layers with encryption
3. **Resource Protection**: Control access to files, databases, and system resources
4. **Error Containment**: Handle errors without exposing sensitive information

---

## 6. Technical Foundation

### Version Recommendations
| Component | LTS/Stable | Latest | Minimum |
|-----------|------------|--------|---------|
| MCP Protocol | 1.0.x | 1.1.x | 0.9.x |
| TypeScript SDK | 0.6.x | 0.7.x | 0.5.x |
| Python SDK | 1.1.x | 1.2.x | 1.0.x |

### Essential Imports
```python
# Python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from pydantic import BaseModel, validator
import asyncio
import pytest
```

---

## 7. Implementation Patterns

### 6.1 Secure MCP Server Setup

```python
app = Server("secure-server")

class FileReadArgs(BaseModel):
    path: str

    @validator("path")
    def validate_path(cls, v):
        if ".." in v:
            raise ValueError("Path traversal not allowed")
        if not v.startswith("/allowed/"):
            raise ValueError("Invalid directory")
        return v

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name != "read_file":
        raise ValueError("Unknown tool")

    args = FileReadArgs(**arguments)
    content = await asyncio.wait_for(
        read_file_secure(args.path), timeout=5.0
    )
    return [TextContent(type="text", text=content)]
```

### 6.2 Tool Registration with Authorization

```python
class DatabaseQueryArgs(BaseModel):
    query: str
    database: str

    @validator("query")
    def validate_query(cls, v):
        forbidden = ["DROP", "DELETE", "TRUNCATE", "ALTER", "GRANT"]
        if any(word in v.upper() for word in forbidden):
            raise ValueError("Forbidden SQL operation")
        return v

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    args = DatabaseQueryArgs(**arguments)
    if not await check_user_permission(args.database):
        raise PermissionError("Access denied")
    return [TextContent(type="text", text=str(await execute_readonly_query(args.database, args.query)))]
```

---

## 8. Security Standards

### Vulnerability Landscape

| Vulnerability | Severity | Mitigation |
|--------------|----------|------------|
| Prompt Injection | CRITICAL | Validate all inputs, sanitize outputs |
| Tool Argument Injection | HIGH | Schema validation, allowlists |
| Path Traversal | HIGH | Restrict to base directories |

### Input Validation Layers

```python
from pydantic import BaseModel, validator, constr
import re

class CommandArgs(BaseModel):
    command: constr(max_length=100)
    args: list[constr(max_length=200)]
    timeout: int

    @validator("command")
    def validate_command(cls, v):
        allowed = ["list", "read", "search"]
        if v not in allowed:
            raise ValueError("Invalid command")
        return v

    @validator("timeout")
    def validate_timeout(cls, v):
        if not 100 <= v <= 30000:
            raise ValueError("Timeout must be 100-30000ms")
        return v
```

---

## 9. Pre-Implementation Checklist

### Phase 1: Before Writing Code
- [ ] Identify all tools to be exposed
- [ ] Define input schemas with validation rules
- [ ] Plan authorization model (who can use what)
- [ ] Select transport layer (stdio/HTTP/WebSocket)
- [ ] Write failing tests for each tool
- [ ] Document expected security threats

### Phase 2: During Implementation
- [ ] Implement tool handlers with Pydantic validation
- [ ] Add path traversal and injection prevention
- [ ] Implement authorization checks
- [ ] Add timeouts to all async operations
- [ ] Use connection pooling for external resources
- [ ] Add response caching where appropriate
- [ ] Implement proper resource cleanup
- [ ] Keep tests passing after each change

### Phase 3: Before Committing
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Coverage meets threshold: `pytest --cov --cov-fail-under=80`
- [ ] Security tests pass: `pytest -k "security or injection"`
- [ ] No secrets in code (use environment variables)
- [ ] Error messages don't expose internals
- [ ] Audit logging enabled for tool executions
- [ ] Rate limiting configured for HTTP transport
- [ ] HTTPS configured for HTTP transport

---

## 10. Testing & Validation

### Security Testing

```python
class TestToolSecurity:
    @pytest.mark.asyncio
    async def test_rejects_path_traversal(self, server):
        with pytest.raises(ValueError, match="Path traversal"):
            await server.call_tool("read_file", {"path": "../../../etc/passwd"})

    @pytest.mark.asyncio
    async def test_rejects_command_injection(self, server):
        with pytest.raises(ValueError, match="Invalid command"):
            await server.call_tool("execute", {"command": "ls; rm -rf /"})

    @pytest.mark.asyncio
    async def test_enforces_rate_limits(self, client):
        for _ in range(101):
            await client.call_tool("ping", {})
        assert client.last_response.status == 429
```

---

## 11. Summary

Your goal is to implement MCP servers and clients that are:
- **Test-Driven**: Write tests first, then implement
- **Performant**: Reuse connections, cache responses, batch operations
- **Secure**: Validate all inputs, authorize all actions, protect all resources
- **Robust**: Handle errors gracefully, implement timeouts, rate limit requests

**Implementation Order**:
1. Write failing test first
2. Implement minimum code to pass
3. Refactor following performance patterns
4. Run all verification commands
5. Commit only when all pass
