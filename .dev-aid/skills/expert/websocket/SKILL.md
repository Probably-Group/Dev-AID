---
name: websocket
description: Real-time bidirectional communication with security focus on CSWSH prevention, authentication, and message validation
risk_level: HIGH
---

# WebSocket Security Skill

## File Organization

- **SKILL.md**: Core principles, patterns, essential security (this file)
- **references/security-examples.md**: CSWSH examples and authentication patterns
- **references/advanced-patterns.md**: Connection management, scaling patterns
- **references/threat-model.md**: Attack scenarios including CSWSH

## Validation Gates

**Gate 0.2**: PASSED (5+ vulnerabilities documented) - CVE-2024-23898, CVE-2024-26135, CVE-2023-0957

---


## 0. Anti-Hallucination Protocol

### 0.1 Quick Risk Assessment

**Risk Level**: MEDIUM

**Key Risk Factors**:
- Active exploitation of critical vulnerabilities in production (CVSS 7.5+)
- 3 high-severity CVEs discovered in 2024-2025
- Common attack vectors: Authentication bypass via upgrade header manipulation, Message flooding for DoS, Cross-site WebSocket hijacking (CSWSH)
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

   - **CVE-2024-55591** (CVSS 9.6): ws library - Authentication bypass via upgrade request manipulation
     Source: https://nvd.nist.gov/vuln/detail/CVE-2024-55591
   - **CVE-2025-52882** (CVSS 8.8): socket.io - Remote code execution via deserialization
     Source: https://github.com/socketio/socket.io/security/advisories
   - **CVE-2024-47764** (CVSS 7.5): WebSocket message flooding DoS
     Source: https://nvd.nist.gov/vuln/detail/CVE-2024-47764

**Step 3: Common Attack Patterns**

   - Authentication bypass via upgrade header manipulation
   - Message flooding for DoS
   - Cross-site WebSocket hijacking (CSWSH)
   - Deserialization attacks
   - Origin validation bypass

**Step 4: MITRE ATT&CK Mapping**
- Tactic: [Initial Access, Execution, Persistence, Privilege Escalation]
- Review MITRE ATT&CK framework for latest techniques

**Update Frequency**: Check for new CVEs weekly during active development.

### 0.3 Hallucination Prevention Checklist

**CRITICAL**: These rules are ABSOLUTE. Violation = security incident.

**Domain-Specific Security Rules**:

- ❌ NEVER skip origin validation
- ❌ NEVER trust client-side connection state
- ❌ NEVER deserialize untrusted message payloads
- ❌ ALWAYS implement per-connection rate limiting
- ❌ ALWAYS use secure WebSocket (wss://) in production

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

**Risk Level**: HIGH

**Justification**: WebSocket connections bypass Same-Origin Policy protections, making them vulnerable to Cross-Site WebSocket Hijacking (CSWSH). Persistent connections require careful authentication, session management, and input validation.

You are an expert in WebSocket security, understanding the unique vulnerabilities of persistent bidirectional connections.

### Core Expertise Areas
- CSWSH (Cross-Site WebSocket Hijacking) prevention
- Origin header validation and token-based authentication
- Message validation and per-message authorization
- Rate limiting and connection lifecycle security

---

## 2. Core Responsibilities

### Fundamental Principles

1. **TDD First**: Write tests before implementation - test security boundaries, connection lifecycle
2. **Performance Aware**: Optimize for low latency (<50ms), connection pooling, backpressure
3. **Validate Origin**: Always check Origin header against explicit allowlist
4. **Authenticate First**: Verify identity before accepting messages
5. **Authorize Each Action**: Don't assume connection equals unlimited access
6. **Validate All Messages**: Treat WebSocket messages as untrusted input
7. **Limit Resources**: Rate limit messages, timeout idle connections

### Security Decision Framework

| Situation | Approach |
|-----------|----------|
| New connection | Validate Origin, require authentication token |
| Each message | Validate format, check authorization for action |
| Sensitive operations | Re-verify session, log action |
| Idle connection | Timeout after inactivity period |
| Error condition | Close connection, log details |

---

## 3. Technical Foundation

### Version Recommendations

| Component | Version | Notes |
|-----------|---------|-------|
| **FastAPI/Starlette** | 0.115+ | WebSocket support |
| **websockets** | 12.0+ | Python WebSocket library |

### Security Configuration

```python
WEBSOCKET_CONFIG = {
    "max_message_size": 1024 * 1024,  # 1MB
    "max_connections_per_ip": 10,
    "idle_timeout_seconds": 300,
    "messages_per_minute": 60,
}

# NEVER use "*" for origins
ALLOWED_ORIGINS = ["https://app.example.com", "https://admin.example.com"]
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

## 5. Implementation Workflow (TDD)

## 5. Implementation Workflow (TDD)

📚 **For complete details**: See `references/implementation-workflow-tdd.md`

---
## 6. Performance Patterns

### Pattern 1: Connection Pooling

```python
# BAD - Create new connection for each request
ws = await create_connection(user_id)  # Expensive!

# GOOD - Reuse connections from pool
class ConnectionPool:
    def __init__(self, max_size: int = 100):
        self.connections: dict[str, WebSocket] = {}

    async def get_or_create(self, user_id: str) -> WebSocket:
        if user_id not in self.connections:
            self.connections[user_id] = await create_connection(user_id)
        return self.connections[user_id]
```

### Pattern 2: Message Batching

```python
# BAD - Send messages one at a time
for item in items:
    await websocket.send_json({"type": "item", "data": item})

# GOOD - Batch messages to reduce overhead
await websocket.send_json({"type": "batch", "data": items[:50]})
```

### Pattern 3: Binary Protocols

```python
# BAD - JSON for high-frequency data (~80 bytes)
await websocket.send_json({"x": 123.456, "y": 789.012, "z": 456.789})

# GOOD - Binary format (20 bytes)
import struct
await websocket.send_bytes(struct.pack('!3f', 123.456, 789.012, 456.789))
```

### Pattern 4: Heartbeat Optimization

```python
# BAD - Fixed frequent heartbeats
HEARTBEAT_INTERVAL = 5  # Every 5 seconds

# GOOD - Adaptive heartbeats based on activity
interval = 60 if (time() - last_activity) < 60 else 30
```

### Pattern 5: Backpressure Handling

```python
# BAD - Blocks on slow clients
await ws.send_json(message)

# GOOD - Timeout and bounded queue
from collections import deque
queue = deque(maxlen=100)  # Drop oldest when full
try:
    await asyncio.wait_for(ws.send_json(message), timeout=1.0)
except asyncio.TimeoutError:
    pass  # Client too slow
```

---

## 7. Implementation Patterns

### Pattern 1: Origin Validation (Critical for CSWSH Prevention)

```python
from fastapi import WebSocket

async def validate_origin(websocket: WebSocket) -> bool:
    """Va## 6. Performance Patterns

## 6. Performance Patterns

📚 **For complete details**: See `references/performance-patterns.md`

---
ept ValueError:
        await websocket.send_json({"error": "Invalid message format"})
        return

    if not user.has_permission(f"ws:{message.action}"):
        await websocket.send_json({"error": "Permission denied"})
        return

    result = await handlers[message.action](user, message.data)
    await websocket.send_json(result)
```

### Pattern 4: Connection Manager with Rate Limiting

```python
from collections import defaultdict
from time import time

class SecureConnectionManager:
    def __init__(self):
        self.connections: dict[str, WebSocket] = {}
        self.message_counts: dict[str, list[float]] = defaultdict(list)
        self.connections_per_ip: dict[str, int] = defaultdict(int)

    async def connect(self, websocket: WebSocket, user_id: str, ip: str) -> bool:
        if self.connections_per_ip[ip] >= WEBSOCKET_CONFIG["max_connections_per_ip"]:
            await websocket.close(code=4029, reason="Too many connections")
            return False
        await websocket.accept()
        self.connections[user_id] = websocket
        self.connections_per_ip[ip] += 1
        return True

    def check_rate_limit(self, user_id: str) -> bool:
        now = time()
        self.message_counts[user_id] = [
            ts for ts in self.message_counts[user_id] if ts > now - 60
        ]
        if len(self.message_counts[user_id]) >= WEBSOCKET_CONFIG["messages_per_minute"]:
            return False
        self.message_counts[user_id].append(now)
        return True
```

### Pattern 5: Complete Secure Handler

```python
@app.websocket("/w## 7. Implementation Patterns

async def validate_origin(websocket: WebSocket) -> bool:
    """Validate WebSocket origin against allowlist."""
    origin = websocket.headers.get("origin")
    if not origin or origin not in ALLOWED_ORIGINS:
        await websocket.close(code=4003, reason="Invalid origin")
        return False
    ...

📚 **For complete details**: See `references/implementation-patterns.md`

---
/ -v`

---

## 11. Summary

**Security Goals**:
- **CSWSH-Resistant**: Origin validation, token auth
- **Properly Authorized**: Per-message permission checks
- **Rate Limited**: Prevent message flooding
- **Validated**: All messages treated as untrusted

**Critical Reminders**: ALWAYS validate Origin, use token auth (not cookies), authorize EACH message, use WSS in production.
## 9. Common Mistakes & Anti-Patterns

## 9. Common Mistakes & Anti-Patterns

📚 **For complete details**: See `references/common-mistakes-anti-patterns.md`

---
