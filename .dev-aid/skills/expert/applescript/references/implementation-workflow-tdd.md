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

