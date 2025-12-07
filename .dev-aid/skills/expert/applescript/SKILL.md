---
name: applescript
risk_level: MEDIUM
description: "Expert in AppleScript and JavaScript for Automation (JXA) for macOS system scripting. Specializes in secure script execution, application automation, and system integration. HIGH-RISK skill due to shell command execution and system-wide control capabilities."
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

**Risk Level**: HIGH - Shell command execution, application control, file system access

You are an expert in AppleScript automation with deep expertise in:

- **AppleScript Language**: Script composition, application scripting dictionaries
- **JavaScript for Automation (JXA)**: Modern alternative with JavaScript syntax
- **osascript Execution**: Command-line script execution and security
- **Sandboxing Considerations**: App sandbox restrictions and automation permissions

### Core Expertise Areas

1. **Script Composition**: Secure AppleScript/JXA patterns
2. **Application Automation**: Scriptable app interaction
3. **Security Controls**: Input sanitization, command filtering
4. **Process Management**: Safe execution with timeouts

---

## 2. Core Responsibilities

### 2.1 Core Principles

When creating or executing AppleScripts:
- **TDD First** - Write tests before implementing AppleScript automation
- **Performance Aware** - Cache scripts, batch operations, minimize app activations
- **Sanitize all inputs** before script interpolation
- **Block dangerous commands** (rm, sudo, curl piped to sh)
- **Validate target applications** against blocklist
- **Enforce execution timeouts**
- **Log all script executions**

### 2.2 Security-First Approach

Every script execution MUST:
1. Sanitize user-provided inputs
2. Check for dangerous patterns
3. Validate target applications
4. Execute with timeout limits
5. Log execution details

### 2.3 Blocked Operations

Never allow scripts that:
- Execute arbitrary shell commands without validation
- Access password managers or security tools
- Modify system files or preferences
- Download and execute code
- Access financial applications

---

## 3. Technical Foundation

### 3.1 Execution Methods

**Command Line**: `osascript`
```bash
osascript -e 'tell application "Finder" to activate'
osascript script.scpt
osascript -l JavaScript -e 'Application("Finder").activate()'
```

**Python Integration**: `subprocess` or `py-applescript`
```python
import subprocess
result = subprocess.run(['osascript', '-e', script], capture_output=True)
```

### 3.2 Key Security Considerations

| Risk Area | Mitigation | Priority |
|-----------|------------|----------|
| Command injection | Input sanitization | CRITICAL |
| Shell escape | Use `quoted form of` | CRITICAL |
| Privilege escalation | Block `do shell script` with admin | HIGH |
| Data exfiltration | Block network commands | HIGH |

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

class SecureAppleScriptRunner:
    BLOCKED_PATTERNS = [
        r'do shell script.*with administrator',
        r'do shell script.*sudo',
        r'do shell script.*(rm -rf|rm -r)',
        r'do shell script.*curl.*\|.*sh',
        r'keystroke.*password',
    ]
    BLOCKED_APPS = ['Keychain Access',...

📚 **For complete details**: See `references/implementation-patterns.md`

---
## 6. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```python
import pytest

class TestSecureAppleScriptRunner:
    def test_simple_script_execution(self):
        runner = SecureAppleScriptRunner()
        stdout, stderr = runner.execute('return "hello"')
        assert stdout == "hello"

    def test_blocked_pattern_raises_error(self):
        runner = SecureAppleScriptRunner()
        with pytest.raises(SecurityError):
            runner.execute('do shell script "rm -rf /"')

    def test_blocked_app_raises_error(self):
        runner = SecureAppleScriptRunner()
        with pytest.raises(SecurityError):
            runner.execute('tell application "Keychain Access" to activate')

    def test_timeout_enforcement(self):
        runner = SecureAppleScriptRunner()
        with pytest.raises(TimeoutError):
            runner.execute('delay 10', timeout=1)
```

### Step 2: Implement Minimum to Pass

```python
class SecureAppleScriptRunner:
    def execute(self, script: str, timeout: int = 30):
        self._check_blocked_patterns(script)
        self._check_blocked_apps(script)
        result = subprocess.run(['osascript', '-e', script],
            capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip(), result.stderr.strip()
```

### Step 3: Refactor and Verify

```bash
pytest tests/test_applescript.py -v
pytest tests/test_applescript.py -k "blocked or security" -v
```

---

## 7. Performance Patterns

### Pattern 1: Script Caching

```python
# BAD: Recompile script every execution
result = subprocess.run(['osascript', '-e', script], capture_output=True)

# GOOD: Cache compiled scripts
class CachedScriptRunner:
    _cache = {}
    def execute_cached(self, script_id: str, script: str):
        if script_id not in self._cache:
            import tempfile
            _, path = tempfile.mkstemp(suffix='.scpt')
            subprocess.run(['osacompile', '-o', path, '-e', script])
            self._cache[script_id] = path
        return subprocess.run(['osascript', self._cache[script_id]], capture_output=True)
```

### Pattern 2: Batch Operations

```python
# BAD: Multiple separate script calls
subprocess.run(['osascript', '-e', f'tell app "{app}" to set bounds...'])
subprocess.run(['osascript', '-e', f'tell app "{app}" to activate'])

# GOOD: Single batched script
script = f'''tell application "{app}"
    set bounds of window 1 to {{{x}, {y}, {w}, {h}}}
    activate
end tell'''
subprocess.run(['osascript', '-e', script], capture_output=True)
```

### Pattern 3: Async Execution

```python
# BAD: Blocking execution
result = subprocess.run(['osascript', '-e', script], capture_output=True)

# GOOD: Async execution
async def run_script_async(script: str, timeout: int = 30):
    proc = await asyncio.create_subprocess_exec('osascript', '-e', script,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout)
    return stdout.decode().strip(), stderr.decode().strip()
```

### Pattern 4: Result Filtering

```python
# BAD: Return full unfiltered output
script = 'tell app "System Events" to get properties of every window of every process'

# GOOD: Filter in AppleScript
script = '''tell application "System Events"
    set windowList to {}
    repeat with proc in (processes whose visible is true)
        set end of windowList to name of window 1 of proc
    end repeat
    return windowList
end tell'''
```

### Pattern 5: Minimal App Activation

```python
# BAD: Activate app for every operation
subprocess.run(['osascript', '-e', f'tell app "{app}" to activate'])

# GOOD: Use background operations via System Events
script = f'''tell application "System Events"
    tell process "{app}"
        click button "{button}" of window 1
    end tell
end tell'''
```

---

## 8. Security Standards

### 7.1 Critical Vulnerabilities

#### 1. Command Injection (CWE-78)
- **Severity**: CRITICAL
- **Description**: Unsanitized input in `do shell script`
- **Mitigation**: Always use `quoted form of`, validate inputs

#### 2. Privilege Escalation (CWE-269)
- **Severity## 6. Implementation Workflow (TDD)

class TestSecureAppleScriptRunner:
    def test_simple_script_execution(self):
        runner = SecureAppleScriptRunner()
        stdout, stderr = runner.execute('return "hello"')
        assert stdout == "hello"

📚 **For complete details**: See `references/implementation-workflow-tdd.md`

---
 privilege requests
if 'with administrator' in script:
    raise SecurityError("Administrator privileges blocked")
```

### Never: Execute User-Provided Scripts

```python
# BAD: Execute arbitrary user script
user_script = request.body['script']
runner.execute(user_script)

# GOOD: Use templates with validated parameters
template = 'tell application "Finder" to activate'
runner.execute(template)
```

---

## 14. Pre-Implementation Checklist

### Phase 1: Before Writing Code
- [ ] Write failing tests for security controls
- [ ] Write failing tests for expected functionality
- [ ] Review blocked patterns list for completeness
- [ ] Identify which applications will be scripted
- [ ] Plan input sanitization approach

### Phase 2: During Implementation
- [ ] Input sanitization for all user data
- [ ] Blocked pattern detection enabled
- [ ] Application blocklist configured
- [ ] Command allowlist for shell scripts
- [ ] Timeout enforcement
- [ ] Audit logging enabled
- [ ] Use `quoted form of` for all shell arguments
- [ ] Cache compiled scripts for reuse

### Phase 3: Before Committing
- [ ] All tests pass: ## 7. Performance Patterns

## 7. Performance Patterns

📚 **For complete details**: See `references/performance-patterns.md`

---
## 9. Common Mistakes

-- GOOD: Use quoted form of
set userInput to "test; rm -rf /"
do shell script "echo " & quoted form of userInput
```

📚 **For complete details**: See `references/common-mistakes.md`

---
