# Windows UI Automation - Testing Guide (TDD)

## Test-Driven Development Workflow

This guide follows strict TDD principles: **Write tests first, then implement.**

---

## Phase 1: Write Failing Tests First

Before writing ANY implementation code, write comprehensive tests that define expected behavior.

### Example: Testing Secure UI Automation

```python
# tests/test_ui_automation.py
import pytest
from unittest.mock import MagicMock, patch
from automation import SecureUIAutomation, SecurityError, RateLimitError, TimeoutError

class TestSecureUIAutomation:
    """TDD tests for UI automation security."""

    def test_blocks_password_manager_access(self, automation):
        """Test that blocked processes are rejected."""
        with pytest.raises(SecurityError, match="blocked"):
            automation.find_element('keepass.exe', 'PasswordField')

    def test_blocks_security_software(self, automation):
        """Test that security software is blocked."""
        blocked_apps = [
            '1password.exe',
            'lastpass.exe',
            'bitwarden.exe',
            'keepass.exe'
        ]
        for app in blocked_apps:
            with pytest.raises(SecurityError):
                automation.find_element(app, 'Field')

    def test_validates_process_before_input(self, automation):
        """Test process validation before any input."""
        with patch.object(automation, '_validate_process') as mock_validate:
            mock_validate.return_value = False
            with pytest.raises(SecurityError):
                automation.send_keys('test', hwnd=12345)
            mock_validate.assert_called_once()

    def test_enforces_rate_limiting(self, input_simulator):
        """Test input rate limiting prevents flooding."""
        # Send max allowed inputs
        for _ in range(100):
            input_simulator.send_keys('a', hwnd=12345)

        # Next input should fail
        with pytest.raises(RateLimitError):
            input_simulator.send_keys('a', hwnd=12345)

    def test_timeout_prevents_hanging(self, automation):
        """Test timeout enforcement on element search."""
        with pytest.raises(TimeoutError):
            with automation.timeout(0.001):  # Very short timeout
                automation.find_element('app.exe', 'NonExistentElement')

    def test_logs_all_operations(self, automation, mock_logger):
        """Test that all operations are logged."""
        automation.find_element('notepad.exe', 'Edit1')
        mock_logger.info.assert_called()
        assert 'element_found' in str(mock_logger.info.call_args)

    def test_permission_tier_enforcement(self, automation):
        """Test that permission tier restricts operations."""
        read_only = SecureUIAutomation(permission_tier='read-only')

        # Read operations should work
        element = read_only.find_element('notepad.exe', 'Edit1')
        value = read_only.get_value(element)

        # Write operations should fail
        with pytest.raises(PermissionError):
            read_only.send_keys('test', hwnd=12345)

    def test_elevation_boundary_check(self, automation):
        """Test that elevated processes cannot be automated from non-elevated."""
        with patch('automation.is_elevated_process') as mock_elevated:
            mock_elevated.side_effect = lambda pid: pid == 9999  # pid 9999 is elevated

            with pytest.raises(SecurityError, match="elevation"):
                automation.find_element_by_pid(9999, 'Button')

@pytest.fixture
def automation():
    """Create SecureUIAutomation instance for testing."""
    return SecureUIAutomation(permission_tier='standard')

@pytest.fixture
def input_simulator():
    """Create SafeInputSimulator for testing."""
    from automation import SafeInputSimulator
    return SafeInputSimulator(permission_tier='standard')

@pytest.fixture
def mock_logger():
    """Create mock logger for testing."""
    with patch('automation.logging.getLogger') as mock:
        yield mock.return_value
```

---

## Phase 2: Implement Minimum Code to Pass Tests

Write the **minimum** implementation needed to pass the tests. No more, no less.

```python
# automation.py
from comtypes.client import CreateObject
import logging
import time

class SecurityError(Exception):
    """Security policy violation."""
    pass

class RateLimitError(Exception):
    """Rate limit exceeded."""
    pass

class PermissionError(Exception):
    """Insufficient permissions."""
    pass

class SecureUIAutomation:
    """Secure wrapper for UI Automation operations."""

    BLOCKED_PROCESSES = {
        'keepass.exe', '1password.exe', 'lastpass.exe',
        'bitwarden.exe', 'mmc.exe', 'secpol.msc',
        'gpedit.msc', 'regedit.exe', 'cmd.exe',
        'powershell.exe', 'taskmgr.exe', 'procexp.exe',
    }

    def __init__(self, permission_tier: str = 'read-only'):
        self.permission_tier = permission_tier
        self.uia = CreateObject('UIAutomationClient.CUIAutomation')
        self.logger = logging.getLogger('uia.security')
        self.operation_timeout = 30

    def find_element(self, process_name: str, element_id: str):
        """Find element with security validation."""
        # Security check: blocked processes
        if process_name.lower() in self.BLOCKED_PROCESSES:
            self.logger.warning(
                'blocked_process_access',
                extra={'process': process_name, 'reason': 'security_policy'}
            )
            raise SecurityError(f"Access to {process_name} is blocked")

        # Find element (minimal implementation)
        root = self.uia.GetRootElement()
        condition = self.uia.CreatePropertyCondition(30003, process_name)
        element = root.FindFirst(4, condition)

        if element:
            self._audit_log('element_found', process_name, element_id)

        return element

    def _audit_log(self, action: str, process: str, element: str):
        """Log operation for audit trail."""
        self.logger.info(
            f'uia.{action}',
            extra={
                'process': process,
                'element': element,
                'permission_tier': self.permission_tier,
            }
        )

class SafeInputSimulator:
    """Input simulation with security controls."""

    def __init__(self, permission_tier: str):
        if permission_tier == 'read-only':
            raise PermissionError("Input requires 'standard' or 'elevated' tier")

        self.permission_tier = permission_tier
        self.rate_limit = 100
        self._input_count = 0
        self._last_reset = time.time()

    def send_keys(self, keys: str, hwnd: int):
        """Send keystrokes with validation."""
        self._check_rate_limit()
        # Minimal implementation
        pass

    def _check_rate_limit(self):
        """Prevent input flooding."""
        now = time.time()
        if now - self._last_reset > 1.0:
            self._input_count = 0
            self._last_reset = now

        self._input_count += 1
        if self._input_count > self.rate_limit:
            raise RateLimitError("Input rate limit exceeded")
```

---

## Phase 3: Run Tests and Verify

```bash
# Run all tests
pytest tests/test_ui_automation.py -v

# Run with coverage
pytest tests/ -v --cov=automation --cov-report=term-missing

# Run only security tests
pytest tests/ -k "security or blocked" -v
```

**Expected output** (all tests should pass):
```
tests/test_ui_automation.py::TestSecureUIAutomation::test_blocks_password_manager_access PASSED
tests/test_ui_automation.py::TestSecureUIAutomation::test_blocks_security_software PASSED
tests/test_ui_automation.py::TestSecureUIAutomation::test_validates_process_before_input PASSED
tests/test_ui_automation.py::TestSecureUIAutomation::test_enforces_rate_limiting PASSED
tests/test_ui_automation.py::TestSecureUIAutomation::test_timeout_prevents_hanging PASSED

======================== 5 passed in 0.42s ========================
```

---

## Phase 4: Refactor with Full Security Patterns

After tests pass, refactor to add complete implementation with security patterns.

```python
class SecureUIAutomation:
    """Enhanced implementation with full security patterns."""

    def __init__(self, permission_tier: str = 'read-only'):
        self.permission_tier = permission_tier
        self.uia = CreateObject('UIAutomationClient.CUIAutomation')
        self.logger = logging.getLogger('uia.security')
        self.operation_timeout = 30
        self.process_validator = ProcessValidator()
        self.timeout_manager = TimeoutManager()

    def find_element(self, process_name: str, element_id: str):
        """Find element with full security validation."""
        # Security validations
        self._validate_not_blocked(process_name)
        self._validate_permission_tier('find_element')

        # Find process
        pid = self._get_process_pid(process_name)
        if not self.process_validator.validate_process(pid):
            raise SecurityError(f"Process validation failed: {process_name}")

        # Check elevation boundaries
        if not self._validate_elevation_match(pid):
            raise SecurityError("Cannot automate across elevation boundary")

        # Find element with timeout
        with self.timeout_manager.timeout(self.operation_timeout):
            element = self._find_element_internal(process_name, element_id)

        # Audit log
        self._audit_log('element_found', process_name, element_id, success=True)

        return element

    def _validate_not_blocked(self, process_name: str):
        """Validate process is not in blocklist."""
        if process_name.lower() in self.BLOCKED_PROCESSES:
            self._audit_log('blocked_access', process_name, '', success=False)
            raise SecurityError(f"Access to {process_name} is blocked")

    def _validate_elevation_match(self, target_pid: int) -> bool:
        """Ensure automation doesn't cross elevation boundaries."""
        import os
        current_pid = os.getpid()

        source_elevated = is_elevated_process(current_pid)
        target_elevated = is_elevated_process(target_pid)

        if target_elevated and not source_elevated:
            return False
        return True
```

---

## Phase 5: Integration Testing

After unit tests pass, write integration tests.

```python
# tests/integration/test_ui_automation_integration.py
import pytest
import subprocess
import time

@pytest.mark.integration
class TestUIAutomationIntegration:
    """Integration tests with real applications."""

    def test_notepad_automation(self, automation):
        """Test automation of Notepad application."""
        # Launch Notepad
        process = subprocess.Popen(['notepad.exe'])
        time.sleep(1)  # Wait for window

        try:
            # Find window
            window = automation.find_window('Untitled - Notepad')
            assert window is not None

            # Find text field
            text_field = automation.find_element_by_class(window, 'Edit')
            assert text_field is not None

            # Type text
            automation.send_keys_to_element(text_field, 'Hello, World!')

            # Verify text
            value = automation.get_element_value(text_field)
            assert value == 'Hello, World!'

        finally:
            # Cleanup
            process.terminate()

    def test_blocked_process_enforcement(self, automation):
        """Verify blocked processes cannot be automated."""
        # This test assumes KeePass is NOT running
        # If it were running, it should be blocked

        with pytest.raises(SecurityError):
            automation.find_element('keepass.exe', 'AnyField')

    @pytest.mark.slow
    def test_timeout_enforcement(self, automation):
        """Verify timeout enforcement with real delay."""
        start = time.time()

        with pytest.raises(TimeoutError):
            automation.find_element('NonExistentApp.exe', 'Field')

        elapsed = time.time() - start
        assert elapsed < 35  # Should timeout around 30s
```

---

## Phase 6: Security Testing

Write tests specifically for security vulnerabilities.

```python
# tests/security/test_security.py
import pytest

class TestSecurityVulnerabilities:
    """Tests for specific security vulnerabilities."""

    def test_cve_2023_28218_privilege_escalation(self, automation):
        """Test mitigation for CVE-2023-28218."""
        # Attempt to automate elevated process from non-elevated
        with pytest.raises(SecurityError, match="elevation"):
            # Simulate elevated process (mock)
            with patch('automation.is_elevated_process') as mock:
                mock.side_effect = lambda pid: pid == 9999
                automation.find_element_by_pid(9999, 'Button')

    def test_cve_2022_30190_input_injection(self, input_simulator):
        """Test mitigation for CVE-2022-30190."""
        # Attempt to inject Ctrl+Alt+Del
        with pytest.raises(SecurityError, match="Blocked key combination"):
            input_simulator.send_keys('ctrl+alt+delete', hwnd=12345)

    def test_credential_field_protection(self, automation):
        """Test that credential fields are protected."""
        # Mock element with password field
        with patch.object(automation, 'find_element') as mock_find:
            mock_element = MagicMock()
            mock_element.name = 'PasswordField'
            mock_find.return_value = mock_element

            # Attempt to read password field should be blocked or logged
            with pytest.raises(SecurityError):
                automation.get_element_value(mock_element)

    def test_audit_logging_completeness(self, automation, mock_logger):
        """Verify all security events are logged."""
        # Trigger blocked access
        with pytest.raises(SecurityError):
            automation.find_element('keepass.exe', 'Field')

        # Verify logged
        assert mock_logger.warning.called
        log_call = str(mock_logger.warning.call_args)
        assert 'blocked_process_access' in log_call
```

---

## Running Tests

### Full Test Suite
```bash
# All tests with coverage
pytest tests/ -v --cov=automation --cov-report=html

# Open coverage report
open htmlcov/index.html
```

### Security Tests Only
```bash
pytest tests/security/ -v
```

### Integration Tests Only
```bash
pytest tests/integration/ -v -m integration
```

### Fast Tests (Unit Only)
```bash
pytest tests/ -v -m "not integration and not slow"
```

---

## Coverage Requirements

**Minimum Coverage**: 80%
**Target Coverage**: 90%+

**Critical Paths** (must be 100% covered):
- Security validation logic
- Permission tier enforcement
- Timeout management
- Process validation
- Audit logging

```bash
# Generate coverage report
pytest tests/ --cov=automation --cov-report=term-missing --cov-fail-under=80
```

---

## Test Organization

```
tests/
├── unit/
│   ├── test_secure_automation.py
│   ├── test_input_simulator.py
│   ├── test_process_validator.py
│   └── test_timeout_manager.py
├── integration/
│   ├── test_notepad_automation.py
│   ├── test_calculator_automation.py
│   └── test_multi_window.py
├── security/
│   ├── test_cve_mitigations.py
│   ├── test_access_control.py
│   └── test_audit_logging.py
└── performance/
    ├── test_benchmarks.py
    └── test_scalability.py
```

---

## Continuous Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run unit tests
        run: pytest tests/unit/ -v --cov=automation

      - name: Run security tests
        run: pytest tests/security/ -v

      - name: Run integration tests
        run: pytest tests/integration/ -v

      - name: Check coverage
        run: pytest tests/ --cov=automation --cov-fail-under=80
```

---

## Pre-Commit Hooks

```bash
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest-unit
        name: Run unit tests
        entry: pytest tests/unit/ -v
        language: system
        pass_filenames: false
        always_run: true

      - id: pytest-security
        name: Run security tests
        entry: pytest tests/security/ -v
        language: system
        pass_filenames: false
        always_run: true
```

---

## Mocking Strategies

### Mock COM Objects

```python
@pytest.fixture
def mock_uia():
    """Mock UI Automation COM object."""
    mock = MagicMock()
    mock.GetRootElement.return_value = MagicMock()
    mock.CreatePropertyCondition.return_value = MagicMock()
    return mock
```

### Mock Process Validation

```python
@pytest.fixture
def mock_process_validator():
    """Mock process validator."""
    with patch('automation.ProcessValidator') as mock:
        validator = mock.return_value
        validator.validate_process.return_value = True
        yield validator
```

### Mock Windows API

```python
@pytest.fixture
def mock_win32api():
    """Mock Win32 API calls."""
    with patch('ctypes.windll.user32') as mock:
        mock.SendInput.return_value = 1
        mock.SetForegroundWindow.return_value = True
        yield mock
```

---

## Testing Checklist

Before committing code:
- [ ] All unit tests pass
- [ ] All security tests pass
- [ ] Integration tests pass
- [ ] Coverage >= 80%
- [ ] No new security vulnerabilities
- [ ] Performance benchmarks met
- [ ] Type checking passes: `mypy automation --strict`
- [ ] Linting passes: `flake8 automation tests`
- [ ] No hardcoded secrets in tests

---

## TDD Best Practices

1. **Red-Green-Refactor**
   - Write failing test (Red)
   - Write minimum code to pass (Green)
   - Refactor and improve (Refactor)

2. **Test One Thing**
   - Each test should verify one behavior
   - Clear test names describing what's tested

3. **Fast Tests**
   - Unit tests should run in milliseconds
   - Use mocks to avoid slow operations

4. **Isolated Tests**
   - Tests should not depend on each other
   - Each test should clean up after itself

5. **Readable Tests**
   - Tests are documentation
   - Clear arrange-act-assert structure

---

## Summary

**TDD Workflow**:
1. ✅ Write failing tests first
2. ✅ Implement minimum code to pass
3. ✅ Run tests and verify
4. ✅ Refactor with full patterns
5. ✅ Add integration tests
6. ✅ Add security tests
7. ✅ Verify coverage >= 80%

**Key Principles**:
- Tests define behavior
- Security tests are critical
- Mock expensive operations
- Integration tests verify real-world usage
- Continuous testing in CI/CD
