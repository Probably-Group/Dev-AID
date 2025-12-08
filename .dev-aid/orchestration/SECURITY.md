# Security Guidelines for Dev-AID Orchestration

This document outlines security measures implemented in the Dev-AID orchestration layer and provides guidelines for maintaining security.

## Table of Contents
1. [Environment Variable Isolation](#environment-variable-isolation)
2. [Input Validation](#input-validation)
3. [Dependency Management](#dependency-management)
4. [Secrets Management](#secrets-management)
5. [Security Testing](#security-testing)

---

## Environment Variable Isolation

### Overview
The MCP client implements **least privilege** environment variable passing to prevent secret leakage to third-party MCP servers.

### Implementation
**File**: `router/mcp_client.py:59-67`

```python
# SECURITY: Only pass whitelisted environment variables to prevent secret leakage
env_whitelist = {'PATH', 'HOME', 'USER', 'LANG', 'LC_ALL', 'TMPDIR', 'TEMP', 'TMP'}

# Build isolated environment with only whitelisted vars
safe_env = {k: v for k, v in os.environ.items() if k in env_whitelist}

# Add server-specific environment variables (if provided)
if self.config.env:
    safe_env.update(self.config.env)
```

### What's Protected
The following environment variables are **explicitly blocked** from MCP servers:
- `ANTHROPIC_API_KEY` - Anthropic Claude API key
- `OPENAI_API_KEY` - OpenAI API key
- `GOOGLE_API_KEY` - Google Gemini API key
- `AWS_*` - AWS credentials
- Any other custom API keys or secrets

### What's Allowed
Only these system-level variables are passed:
- `PATH` - Binary search path (required for command execution)
- `HOME` - User home directory
- `USER` - Current username
- `LANG`, `LC_ALL` - Locale settings
- `TMPDIR`, `TEMP`, `TMP` - Temporary directory locations

### Server-Specific Variables
MCP servers can define their own environment variables in the server configuration:

```python
config = MCPServerConfig(
    name="my-server",
    command="npx",
    args=["-y", "my-mcp-server"],
    env={"SERVER_API_KEY": "safe-to-pass"}  # ✅ Explicitly allowed
)
```

### Threat Model

#### Attack Scenario (Before Fix)
1. User installs a malicious MCP server from npm
2. Server receives full environment (including `ANTHROPIC_API_KEY`)
3. Server exfiltrates API key to attacker's server
4. Attacker uses stolen API key for unauthorized API calls

#### Mitigation (After Fix)
1. User installs a malicious MCP server from npm
2. Server receives **only** whitelisted environment variables
3. API keys are **not available** to the server
4. ✅ Attack prevented

### Testing
Environment isolation is verified by comprehensive tests:

**File**: `tests/test_mcp.py:125-224`

```python
def test_environment_isolation(self):
    """Test that API keys and secrets are not leaked to MCP subprocesses"""
    # Sets up environment with secrets
    # Verifies ANTHROPIC_API_KEY is NOT passed
    # Verifies OPENAI_API_KEY is NOT passed
    # Verifies whitelisted vars ARE passed
```

---

## Input Validation

### Overview
All external inputs are validated using Pydantic models with strict validation rules.

### Key Validators

#### ExecuteRequest
**File**: `router/validators.py:32-69`

Blocks injection attempts:
- `__import__` - Python module imports
- `eval(`, `exec(`, `compile(` - Code execution
- `os.system` - System commands
- `../` - Path traversal
- `${`, `{{` - Template injection (JNDI, Jinja2)

#### SafePath
**File**: `router/validators.py:115-145`

Prevents directory traversal:
- Rejects `..` in paths
- Validates resolved path stays within base directory
- Blocks control characters and null bytes

#### SubprocessCommand
**File**: `router/validators.py:148-185`

Subprocess execution safety:
- **Allowlist-based**: Only `git`, `python`, `python3`, `pip`, `pip3`
- Blocks shell metacharacters: `;`, `|`, `&`, `$`, `` ` ``
- Prevents command injection

### Testing
Comprehensive security tests cover OWASP Top 10:

**File**: `tests/test_security.py`

300 lines of security tests including:
- Path traversal prevention (A03:2021)
- Command injection prevention (A03:2021)
- Input sanitization (A04:2021)
- API key handling (A02:2021)
- DoS prevention (A05:2021)

---

## Dependency Management

### Pinned Versions
All dependencies are pinned to **exact versions** in `requirements.txt`.

**File**: `requirements.txt:1-11`

```txt
# SECURITY: All dependencies are pinned to exact versions for reproducibility.
# This prevents supply chain attacks and ensures deterministic builds.

anthropic==0.75.0
google-genai==1.53.0
openai==1.54.5
pydantic==2.10.3
```

### Why Pinning Matters
- ✅ **Reproducible builds** - Same code produces same behavior
- ✅ **Supply chain security** - Prevents malicious version injection
- ✅ **Stability** - No unexpected breaking changes
- ✅ **Audit trail** - Know exactly what versions are running

### Updating Dependencies
See [DEPENDENCY_UPDATE_GUIDE.md](./DEPENDENCY_UPDATE_GUIDE.md) for safe update procedures.

### Vulnerability Scanning
Dependencies are scanned in CI/CD:

```bash
# Automated scans
pip-audit --desc         # Check for known vulnerabilities
safety check --json      # Alternative vulnerability scanner
bandit -r router/ -ll    # Static code analysis
```

---

## Secrets Management

### Best Practices

#### ✅ DO
- Store secrets in environment variables
- Use `.env` files (add to `.gitignore`)
- Load secrets via `os.getenv()`
- Validate secrets format (not content)
- Use `secrets` module for tokens
- Compare secrets with `secrets.compare_digest()` (timing-attack resistant)

#### ❌ DON'T
- Hardcode secrets in source code
- Commit secrets to version control
- Log secrets in error messages
- Pass secrets as command-line arguments (visible in `ps`)
- Use `random` module for security-sensitive operations

### Example: Loading API Keys

```python
import os
from dotenv import load_dotenv

# Load from .env file
load_dotenv()

# Get API key with validation
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not set")

# ✅ Secret never appears in code
# ✅ Not committed to git
# ✅ Not passed to untrusted subprocesses
```

### Error Message Safety
**File**: `tests/test_security.py:168-184`

```python
def test_api_key_not_in_error_messages(self):
    """Test that API keys are not leaked in error messages"""
    # Verifies error messages don't contain API keys
```

---

## Security Testing

### Running Security Tests

```bash
# Full security test suite
pytest tests/test_security.py -v

# Quick security checks
./run_security_checks.sh
```

### CI/CD Integration
Security checks run on every commit:

```yaml
# .github/workflows/security.yml
- name: Security Scan
  run: |
    pip install -r requirements.txt
    bandit -r router/ -ll
    pip-audit --desc
    pytest tests/test_security.py -v
```

### Test Coverage Requirements
- Minimum 80% code coverage
- 100% coverage on security-critical paths:
  - Input validation
  - Authentication/authorization
  - Subprocess execution
  - File operations

---

## Reporting Security Issues

If you discover a security vulnerability:

1. **DO NOT** open a public GitHub issue
2. Email security contact (if configured) or create private security advisory
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

---

## Security Checklist

Before deploying to production:

- [ ] All dependencies pinned to exact versions
- [ ] `pip-audit` and `safety check` pass with no vulnerabilities
- [ ] All security tests pass (`pytest tests/test_security.py`)
- [ ] No hardcoded secrets in code
- [ ] `.env` files not committed to git
- [ ] Environment variable isolation enabled for MCP servers
- [ ] Input validation enabled for all external inputs
- [ ] Subprocess execution uses allowlist
- [ ] Error messages don't leak sensitive information
- [ ] Static analysis (`bandit`, `mypy`) passes

---

## References

- [OWASP Top 10 2021](https://owasp.org/www-project-top-ten/)
- [CWE Top 25 Most Dangerous Software Weaknesses](https://cwe.mitre.org/top25/)
- [Pydantic Security Best Practices](https://docs.pydantic.dev/latest/concepts/security/)
- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security.html)

---

**Last Updated**: 2025-12-07
**Version**: 1.0.0
