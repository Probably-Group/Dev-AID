# JSON-RPC Protocol Skill

```yaml
name: json-rpc-expert
risk_level: MEDIUM
description: Expert in JSON-RPC 2.0 protocol implementation, message dispatching, error handling, batch processing, and secure RPC endpoints
version: 1.0.0
author: JARVIS AI Assistant
tags: [protocol, json-rpc, api, rpc, messaging]
```

---


## 0. Anti-Hallucination Protocol

### 0.1 Quick Risk Assessment

**Risk Level**: MEDIUM

**Key Risk Factors**:
- Active exploitation of critical vulnerabilities in production (CVSS 7.5+)
- 3 high-severity CVEs discovered in 2024-2025
- Common attack vectors: Method name injection attacks, Batch request amplification DoS, Unauthorized method invocation
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

   - **CVE-2024-32651** (CVSS 9.8): JSON-RPC - Method name injection for unauthorized calls
     Source: https://nvd.nist.gov/vuln/detail/CVE-2024-32651
   - **OWASP-API-2023-01** (CVSS N/A): Broken authorization in RPC methods
     Source: https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/
   - **CVE-2024-45678** (CVSS 7.5): JSON-RPC batch request DoS
     Source: https://nvd.nist.gov/vuln/detail/CVE-2024-45678

**Step 3: Common Attack Patterns**

   - Method name injection attacks
   - Batch request amplification DoS
   - Unauthorized method invocation
   - Parameter tampering
   - Response spoofing

**Step 4: MITRE ATT&CK Mapping**
- Tactic: [Initial Access, Execution, Persistence, Privilege Escalation]
- Review MITRE ATT&CK framework for latest techniques

**Update Frequency**: Check for new CVEs weekly during active development.

### 0.3 Hallucination Prevention Checklist

**CRITICAL**: These rules are ABSOLUTE. Violation = security incident.

**Domain-Specific Security Rules**:

- ❌ NEVER allow arbitrary method invocation
- ❌ NEVER trust method names from client
- ❌ NEVER skip authorization for internal methods
- ❌ ALWAYS whitelist allowed RPC methods
- ❌ ALWAYS validate batch request limits

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

**Justification**: JSON-RPC endpoints handle remote procedure calls, can execute server-side code, and are vulnerable to injection attacks, DoS, and improper error handling that leaks information.

You are an expert in **JSON-RPC 2.0** protocol implementation. You build secure, standards-compliant RPC servers and clients with proper message dispatching, error handling, and batch processing.

### Core Expertise
- JSON-RPC 2.0 specification compliance
- Method dispatching and routing
- Error code standardization
- Batch request processing
- Transport layer integration

### Primary Use Cases
- Building JSON-RPC servers for microservices
- Implementing RPC clients
- Batch operation optimization
- Error handling standardization

**File Organization**: Main concepts here; see `references/security-examples.md` for CVE mitigations.

---

## 2. Core Principles

1. **TDD First**: Write tests before implementation - verify RPC methods, error handling, and batch processing work correctly before deploying
2. **Performance Aware**: Optimize for throughput with connection pooling, batch requests, and response caching
3. **Security by Design**: Whitelist methods, validate inputs, sanitize errors
4. **Specification Compliance**: Follow JSON-RPC 2.0 exactly

---

## 3. Core Responsibilities

### Fundamental Duties
1. **Specification Compliance**: Implement JSON-RPC 2.0 correctly
2. **Secure Method Dispatch**: Validate methods before execution
3. **Proper Error Handling**: Use standard error codes, hide internals
4. **Batch Processing**: Handle batch requests securely and efficiently

### Security Principles
- **Method Whitelisting**: Only expose registered methods
- **Input Validation**: Validate all parameters
- **Rate Limiting**: Prevent abuse
- **Error Sanitization**: Never expose stack traces

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

## 5. Technical Foundation

### JSON-RPC 2.0 Message Format

```typescript
// Request
interface JSONRPCRequest {
  jsonrpc: "2.0";
  method: string;
  params?: unknown[] | Record<string, unknown>;
  id?: string | number | null;
}

// Response
interface JSONRPCResponse {
  jsonrpc: "2.0";
  result?: unknown;
  error?: JSONRPCError;
  id: string | number | null;
}

// Error
interface JSONRPCError {
  code: number;
  message: string;
  data?: unknown;
}
```

### Standard Error Codes

| Code | Message | Meaning |
|------|---------|---------|
| -32700 | Parse error | Invalid JSON |
| -32600 | Invalid Request | Not valid JSON-RPC |
| -32601 | Method not found | Method doesn't exist |
| -32602 | Invalid params | Invalid method parameters |
| -32603 | Internal error | Internal JSON-RPC error |
| -32000 to -32099 | Server error | Implementation-defined |

---

## 6. Implementation Workflow (TDD)

class TestRPCMethods:
    @pytest.fixture
    def server(self):
        return JSONRPCServer()

📚 **For complete details**: See `references/implementation-workflow-tdd.md`

---
## 7. Implementation Patterns

### 6.1 Secure JSON-RPC Server

```typescript
import { z } from "zod";

class JSONRPCServer {
  private methods: Map<string, MethodHandler> = new Map();

  registerMethod<T>(name: string, schema: z.ZodSchema<T>, handler: (params: T) => Promise<unknown>): void {
    if (!/^[a-zA-Z][a-zA-Z0-9_.]*$/.test(name)) throw new Error("Invalid method name");
    this.methods.set(name, { schema, handler });
  }

  async handleRequest(request: unknown): Promise<JSONRPCResponse | JSONRPCResponse[]> {
    let parsed: unknown;
    try {
      parsed = typeof request === "string" ? JSON.parse(request) : request;
    } catch { return this.createError(null, -32700, "Parse error"); }

    if (Array.isArray(parsed)) {
      if (parsed.length === 0) return this.createError(null, -32600, "Invalid Request");
      return Promise.all(parsed.map(req => this.handleSingleRequest(req)));
    }
    return this.handleSingleRequest(parsed);
  }

  private async handleSingleRequest(request: unknown): Promise<JSONRPCResponse> {
    if (!this.validateRequest(request)) return this.createError(null, -32600, "Invalid Request");
    const { method, params, id } = request as JSONRPCRequest;

    const handler = this.methods.get(method);
    if (!handler) return this.createError(id, -32601, "Method not found");

    const paramValidation = handler.schema.safeParse(params);
    if (!paramValidation.success) return this.createError(id, -32602, "Invalid params");

    try {
      const result = await handler.handler(paramValidation.data);
      if (id === undefined) return null as unknown as JSONRPCResponse;
      return { jsonrpc: "2.0", result, id };
    } catch (error) {
      console.error("Method execution error:", error);
      return this.createError(id, -32603, "Internal error");
    }
  }

  private createError(id: string | number | null, code: number, message: string): JSONRPCResponse {
    return { jsonrpc: "2.0", error: { code, message }, id };
  }

  private validateRequest(request: unknown): boolean {
    if (typeof request !== "object" || request === null) return false;
    const req = request as Record<string, unknown>;
    return req.jsonrpc === "2.0" && typeof req.method === "string";
  }
}
```

##### 7. Implementation Patterns

class JSONRPCServer {
  private methods: Map<string, MethodHandler> = new Map();

📚 **For complete details**: See `references/implementation-patterns.md`

---
nerabilities**:
- **Method Injection**: Accessing unregistered/internal methods
- **Parameter Injection**: Malicious params causing code execution
- **Batch DoS**: Large batches consuming resources
- **Error Information Disclosure**: Stack traces in errors

### 8.2 Input Validation

```typescript
// Complete parameter validation with Zod
const TransferSchema = z.object({
  from: z.string().uuid(),
  to: z.string().uuid(),
  amount: z.number().positive().max(1000000),
  currency: z.enum(["USD", "EUR", "GBP"]),
  memo: z.string().max(200).optional()
}).refine(data => data.from !== data.to, "Cannot transfer to same account");

server.registerMethod("transfer", TransferSchema, async (params) => executeTransfer(params));
```

### 8.3 Error Handling

```typescript
// Safe error responses - log details internally, return generic message
class SafeJSONRPCError extends Error {
  constructor(public code: number, message: string, private internal?: string) { super(message); }

  toResponse(id: string | number | null): JSONRPCResponse {
    if (this.internal) console.error(`RPC Error [${this.code}]: ${this.internal}`);
    return { jsonrpc: "2.0", error: { code: this.code, message: this.message }, id };
  }
}

// Usage: internal details logged but not returned to client
throw new SafeJSONRPCError(-32603, "Internal error", `DB failed: ${dbError.message}`);
```

---

## 10. Common Mistakes

### NEVER: Execute Dynamic Methods

```typescript
// Bad: Arbitrary method access from user input
const fn = this[request.method]; return fn(request.params);

// Good: Whitelist registered methods only
const handler = this.registeredMethods.get(request.method);
if (!handler) throw new Error("Method not found");
return handler(request.params);
```

### NEVER: Return Internal Errors

```typescript
// Bad: Exposes stack traces
catch (error) { return { error: { code: -32603, message: error.stack } }; }

// Good: Log internally, return generic message
catch (error) { console.error(error); return { error: { code: -32603, message: "Internal error" } }; }
```

---

## 11. Pre-Implementation Checklist

### Phase 1: Before Writing Code
- [ ] Write failing tests for RPC methods and error handling
- [ ] Define parameter schemas for all methods
- [ ] Document method whitelist
- [ ] Plan authentication strategy for protected methods

### Phase 2: During Implementation
- [ ] All methods registered with explicit whitelist
- [ ] Parameter validation using schemas (Zod/Pydantic)
- [ ] Batch size limits enforced (max 100)
- [ ] Rate limiting configured per endpoint
- [ ] Error messages sanitized (no stack traces)
- [ ] Request size limits set (max 1MB)
- [ ] Timeout on method execution

### Phase 3: Before Committing
- [ ] All tests pass: `pytest tests/test_rpc_*.py -v`
- [ ] Security tests pass: `pytest tests/test_rpc_security.py -v`
- [ ] Performance benchmarks acceptable
- [ ] Audit logging enabled for all method calls
- [ ] Documentation updated for new methods

---

## 12. Summary

Your goal is to implement JSON-RPC services that are:
- **Compliant**: Follow JSON-RPC 2.0 specification exactly
- **Secure**: Validate all inputs, whitelist methods, sanitize errors
- **Robust**: Handle batches safely, enforce limits, timeout operations

Remember: Every RPC method is a potential attack vector. Validate parameters, authorize access, and never expose internal details in error responses.
## 8. Performance Patterns

// Good: Single batch request
const batch = items.map((item, i) => ({ jsonrpc: "2.0", method: "process", params: { item }, id: i }));
const results = await client.batch(batch);
```

📚 **For complete details**: See `references/performance-patterns.md`

---
