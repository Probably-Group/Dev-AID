# Sandboxing Skill

---
name: sandboxing
version: 1.0.0
domain: security/isolation
risk_level: HIGH
languages: [python, c, rust, go]
frameworks: [seccomp, apparmor, selinux, bubblewrap]
requires_security_review: true
compliance: [SOC2, FedRAMP]
last_updated: 2025-01-15
---

> **MANDATORY READING PROTOCOL**: Before implementing sandboxing, read `references/advanced-patterns.md` for defense-in-depth strategies and `references/threat-model.md` for container escape scenarios.


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

### 1.1 Purpose and Scope

This skill provides process isolation and sandboxing for JARVIS components:

- **Linux**: seccomp-bpf, AppArmor/SELinux, namespaces, cgroups
- **Windows**: AppContainer, Job Objects, Restricted Tokens
- **macOS**: sandbox-exec, App Sandbox entitlements
- **Containers**: Docker/Podman security contexts, Kubernetes SecurityContext

### 1.2 Risk Assessment

**Risk Level**: HIGH

**Justification**:
- Sandbox escapes allow full system compromise
- Misconfigurations negate all isolation benefits
- Kernel vulnerabilities bypass userspace controls
- Plugin/extension execution requires strong isolation

**Attack Surface**:
- Syscall filtering gaps
- Namespace escape vectors
- Capability misconfigurations
- Resource exhaustion attacks

## 2. Core Responsibilities

### 2.1 Primary Functions

1. **Isolate untrusted code** execution from host system
2. **Restrict syscalls** to minimum required set
3. **Limit resources** (CPU, memory, network, filesystem)
4. **Enforce security policies** via MAC (AppArmor/SELinux)
5. **Contain failures** to prevent cascade effects

### 2.2 Core Principles

- **TDD First**: Write tests for sandbox restrictions before implementation
- **Performance Aware**: Cache permissions, lazy-load capabilities, minimize syscall overhead
- **Defense in Depth**: Layer multiple isolation mechanisms
- **Least Privilege**: Grant minimum permissions required
- **Fail Secure**: Default deny all access

### 2.3 Security Principles

- **NEVER** run untrusted code without syscall filtering
- **NEVER** grant CAP_SYS_ADMIN to sandboxed processes
- **ALWAYS** drop all capabilities not explicitly required
- **ALWAYS** use read-only root filesystem where possible
- **ALWAYS** apply defense-in-depth (multiple layers)

## 3. Technology Stack

| Platform | Primary | Secondary | MAC |
|----------|---------|-----------|-----|
| Linux | seccomp-bpf | namespaces | AppArmor/SELinux |
| Windows | AppContainer | Job Objects | WDAC |
| macOS | sandbox-exec | Entitlements | TCC |
| Containers | securityContext | RuntimeClass | Pod Security |

**Recommended Tools**: bubblewrap, firejail, nsjail, gVisor


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

def create_minimal_sandbox():
    """Create minimal seccomp sandbox for untrusted code."""
    filter = seccomp.SyscallFilter(defaction=seccomp.KILL)

📚 **For complete details**: See `references/implementation-patterns.md`

---
## 6. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```python
import pytest
from sandbox import SandboxManager

class TestSandboxRestrictions:
    """Test sandbox isolation before implementation."""

    @pytest.fixture
    def sandbox(self):
        return SandboxManager()

    def test_network_blocked(self, sandbox):
        """WRITE FIRST: Network access must be blocked."""
        result = sandbox.run(['curl', '-s', 'http://example.com'])
        assert result.returncode != 0, "Network should be blocked"

    def test_filesystem_readonly(self, sandbox):
        """WRITE FIRST: Root filesystem must be read-only."""
        result = sandbox.run(['touch', '/test-file'])
        assert result.returncode != 0, "Root FS should be read-only"

    def test_capabilities_dropped(self, sandbox):
        """WRITE FIRST: All capabilities must be dropped."""
        result = sandbox.run(['cat', '/proc/self/status'])
        assert 'CapEff:\t0000000000000000' in result.stdout

    def test_syscall_blocked(self, sandbox):
        """WRITE FIRST: Dangerous syscalls must be blocked."""
        # ptrace should be blocked by seccomp
        result = sandbox.run(['strace', 'ls'])
        assert result.returncode != 0, "ptrace should be blocked"

    def test_escape_attempt_fails(self, sandbox):
        """WRITE FIRST: Container escape must fail."""
        result = sandbox.run(['ls', '/proc/1/root'])
        assert result.returncode != 0, "Namespace escape blocked"
```

### Step 2: Implement Minimum to Pass

```python
class SandboxManager:
    def __init__(self):
        self._bwrap_args = ['bwrap', '--unshare-net', '--ro-bind', '/', '/',
                           '--cap-drop', 'ALL', '--seccomp', '3']

    def run(self, command, timeout=30):
        import subprocess
        return subprocess.run(self._bwrap_args + ['--'] + command,
                              capture_output=True, text=True, timeout=timeout)
```

### Step 3: Refactor with Defense-in-Depth

```python
class SandboxManager:
    def __init__(self, profile: str = 'strict'):
        self._bwrap_args = ['bwrap', '--unshare-all']
        if profile == 'network': self._bwrap_args.append('--share-net')
        self._bwrap_args.extend(['--ro-bind', '/usr', '/usr', '--tmpfs', '/tmp',
                                 '--cap-drop', 'ALL', '--seccomp', '3'])
```

### Step 4: Run Full Verification

```bash
# Run all sandbox tests
pytest tests/sandbox/ -v --tb=short

# Test specific isolation features
pytest tests/sandbox/test_network.py -v
pytest tests/sandbox/test_capabilities.py -v
pytest tests/sandbox/test_escapes.py -v

# Security audit
python -m security_audit --sandbox
```

## 7. Performance Patterns

### 6.1 Permission Caching

```python
# Bad: Load permissions from disk on every operation
def run_sandboxed(command):
    permissions = load_permissions_from_disk()  # Slow I/O every time
    return execute(command)

# Good:## 6. Implementation Workflow (TDD)

class TestSandboxRestrictions:
    """Test sandbox isolation before implementation."""

📚 **For complete details**: See `references/implementation-workflow-tdd.md`

---
----------|------|----------------|
| A01: Broken Access Control | Critical | Namespace isolation, MAC |
| A04: Insecure Design | High | Defense in depth |
| A05: Security Misconfiguration | Critical | Secure defaults |

### 7.3 Defense-in-Depth Layers

1. **Seccomp**: Syscall filtering
2. **Namespaces**: Resource isolation
3. **Capabilities**: Privilege reduction
4. **MAC**: Mandatory access control (AppArmor/SELinux)
5. **Cgroups**: Resource limits

**📚 For detailed OWASP coverage**:
- See `references/security-examples.md`

## 9. Testing Requirements

```python
class TestSandboxSecurity:
    def test_network_isolated(self, sandbox):
        assert sandbox.run(['curl', '-s', 'https://example.com']).returncode != 0
    def test_capabilities_dropped(self, sandbox):
        assert 'CapEff:\t0' in sandbox.run(['cat', '/proc/self/status']).stdout
    def test_escape_attempts_blocked(self, sandbox):
        assert sandbox.run(['ls', '/proc/1/root']).returncode != 0
```

**📚 For complete test suite**: See `references/security-examples.md#testing`

## 10. Common Mistakes

### Critical Anti-Patterns

```yaml
# ❌ NEVER: runAsUser: 0 (root)          ✅ ALWAYS: runAsNonRoot: true, runAsUser: 1000
# ❌ NEVER: add: [SYS_ADMIN]              ✅ ALWAYS: drop: [ALL], add only needed
# ❌ NEVER: privileged: true              ✅ ALWAYS: privileged: false
# ❌ NEVER: No seccomp profile            ✅ ALWAYS: seccompProfile: RuntimeDefault
```

```yaml
# Example secure configuration
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  privileged: false
  allowPrivilegeEscalation: false
  capabilities: {drop: [ALL]}
  seccompProfile: {type: RuntimeDefault}
```

**📚 For complete anti-patterns**: See `references/advanced-patterns.md#anti-patterns`

## 11. Pre-Implementation Checklist

### Phase 1: Before Writing Code
- [ ] Identify isolation requirements from PRD
- [ ] Review threat model for attack vectors
- [ ] Define minimal capability set needed
- [ ] Choose appropriate isolation layers
- [ ] Write failing tests for all restrictions

### Phase 2: During Implementation
- [ ] Implement defense-in-depth layers
- [ ] Drop all capabilities, add back only required
- [ ] Apply seccomp filters for syscall blocking
- [ ] Configure namespace isolation
- [ ] Set up resource limits (cgroups)
- [ ] Use read-only root filesystem
- [ ] Run tests after each layer added

### Phase 3: Before Committing
- [ ] All sandbox restriction tests pass
- [ ] Escape attempt tests verified
-## 7. Performance Patterns

## 7. Performance Patterns

📚 **For complete details**: See `references/performance-patterns.md`

---
