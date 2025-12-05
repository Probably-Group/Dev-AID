# Windows UI Automation - Advanced Patterns

## Pattern: Secure Automation Session

```python
from contextlib import contextmanager
import uuid

class SecureAutomationSession:
    """Managed automation session with full security controls."""

    def __init__(self, permission_tier: str = 'read-only'):
        self.session_id = str(uuid.uuid4())
        self.permission_tier = permission_tier
        self.uia = None
        self.audit_logger = UIAuditLogger()
        self.timeout_manager = TimeoutManager()
        self.guard = AutomationGuard()

    @contextmanager
    def session(self):
        """Context manager for safe automation session."""
        try:
            self._initialize()
            yield self
        finally:
            self._cleanup()

    def _initialize(self):
        """Initialize automation with security checks."""
        self.uia = CreateObject('UIAutomationClient.CUIAutomation')
        self.audit_logger.log_session_start(self.session_id, self.permission_tier)

    def _cleanup(self):
        """Clean up automation session."""
        self.audit_logger.log_session_end(self.session_id)
        self.uia = None

    def find_and_interact(self, process: str, element_id: str, action: str, **kwargs):
        """Find element and perform action with full validation."""
        # Check limits
        self.guard.check_limits()

        # Validate process
        pid = get_process_pid(process)
        if not ProcessValidator().validate_process(pid):
            raise SecurityError(f"Process validation failed: {process}")

        # Find element with timeout
        with self.timeout_manager.timeout(30):
            element = self._find_element(process, element_id)

        # Perform action based on permission tier
        if action == 'get_value':
            return self._get_value(element)
        elif action == 'click':
            return self._click(element)
        elif action == 'send_keys':
            return self._send_keys(element, kwargs.get('keys', ''))

    def _find_element(self, process: str, element_id: str):
        """Find element with caching and validation."""
        root = self.uia.GetRootElement()
        # Implementation details...
        pass
```

## Pattern: Hierarchical Element Discovery

```python
class ElementDiscovery:
    """Safe hierarchical element discovery."""

    def find_element_path(self, path: list[str]) -> 'UIElement':
        """Find element by path with validation at each level."""
        current = self.uia.GetRootElement()

        for level, identifier in enumerate(path):
            # Validate identifier
            if not validate_element_identifier(identifier):
                raise ValidationError(f"Invalid identifier: {identifier}")

            # Find child element
            child = self._find_child(current, identifier)
            if not child:
                raise ElementNotFoundError(f"Element not found: {identifier}")

            # Validate we can access this element
            if not self._can_access(child):
                raise SecurityError(f"Access denied to element: {identifier}")

            current = child

        return current
```

## Pattern: Robust Wait Conditions

```python
class WaitConditions:
    """Wait for UI conditions with timeout and safety."""

    def wait_for_element(
        self,
        condition: callable,
        timeout: int = 30,
        poll_interval: float = 0.5
    ) -> 'UIElement':
        """Wait for element matching condition."""
        start = time.time()

        while time.time() - start < timeout:
            try:
                element = condition()
                if element:
                    return element
            except Exception:
                pass

            time.sleep(poll_interval)

        raise TimeoutError(f"Element not found within {timeout}s")

    def wait_for_window(self, title: str, timeout: int = 30):
        """Wait for window to appear."""
        return self.wait_for_element(
            lambda: self._find_window_by_title(title),
            timeout=timeout
        )

    def wait_for_element_state(self, element, state: str, timeout: int = 10):
        """Wait for element to reach state."""
        return self.wait_for_element(
            lambda: element if element.get_state() == state else None,
            timeout=timeout
        )
```

## Pattern: Multi-Monitor Support

```python
class MultiMonitorAutomation:
    """Handle automation across multiple monitors."""

    def get_element_monitor(self, element) -> int:
        """Determine which monitor contains element."""
        rect = element.bounding_rectangle
        monitors = self._enumerate_monitors()

        for idx, monitor in enumerate(monitors):
            if self._rect_in_monitor(rect, monitor):
                return idx

        return 0  # Primary monitor fallback

    def ensure_visible(self, element):
        """Ensure element is visible on screen."""
        rect = element.bounding_rectangle
        monitor = self.get_element_monitor(element)

        if not self._is_fully_visible(rect, monitor):
            element.scroll_into_view()
```

## Pattern: Clipboard Security

```python
class SecureClipboard:
    """Secure clipboard operations for automation."""

    def copy_to_clipboard(self, text: str, clear_after: int = 30):
        """Copy text with automatic clearing."""
        # Set clipboard
        ctypes.windll.user32.OpenClipboard(0)
        ctypes.windll.user32.EmptyClipboard()
        # ... set text ...
        ctypes.windll.user32.CloseClipboard()

        # Schedule clearing
        threading.Timer(clear_after, self._clear_clipboard).start()

    def _clear_clipboard(self):
        """Clear clipboard contents."""
        ctypes.windll.user32.OpenClipboard(0)
        ctypes.windll.user32.EmptyClipboard()
        ctypes.windll.user32.CloseClipboard()
```

## Pattern: Screenshot Redaction

```python
class SecureScreenCapture:
    """Screenshot capture with sensitive content redaction."""

    def capture_with_redaction(self, hwnd: int) -> bytes:
        """Capture window with sensitive areas redacted."""
        # Capture screenshot
        image = self._capture_window(hwnd)

        # Find sensitive elements
        sensitive_rects = self._find_sensitive_regions(hwnd)

        # Redact sensitive areas
        for rect in sensitive_rects:
            image = self._redact_region(image, rect)

        return image

    def _find_sensitive_regions(self, hwnd: int) -> list:
        """Find regions containing sensitive content."""
        regions = []
        elements = self._enumerate_elements(hwnd)

        for element in elements:
            if is_credential_element(element.name):
                regions.append(element.bounding_rectangle)

        return regions
```

---

## Core Implementation Patterns from SKILL.md

### Pattern: Secure Element Discovery

**Use Case**: Finding UI elements for automation with full security validation.

**Implementation**:
```python
from comtypes.client import GetModule, CreateObject
import hashlib
import logging

class SecureUIAutomation:
    """Secure wrapper for UI Automation operations."""

    BLOCKED_PROCESSES = {
        'keepass.exe', '1password.exe', 'lastpass.exe',    # Password managers
        'mmc.exe', 'secpol.msc', 'gpedit.msc',             # Admin tools
        'regedit.exe', 'cmd.exe', 'powershell.exe',        # System tools
        'taskmgr.exe', 'procexp.exe',                       # Process tools
    }

    def __init__(self, permission_tier: str = 'read-only'):
        self.permission_tier = permission_tier
        self.uia = CreateObject('UIAutomationClient.CUIAutomation')
        self.logger = logging.getLogger('uia.security')
        self.operation_timeout = 30  # seconds

    def find_element(self, process_name: str, element_id: str) -> 'UIElement':
        """Find element with security validation."""
        # Security check: blocked processes
        if process_name.lower() in self.BLOCKED_PROCESSES:
            self.logger.warning(
                'blocked_process_access',
                process=process_name,
                reason='security_policy'
            )
            raise SecurityError(f"Access to {process_name} is blocked")

        # Find process window
        root = self.uia.GetRootElement()
        condition = self.uia.CreatePropertyCondition(
            30003,  # UIA_NamePropertyId
            process_name
        )

        element = root.FindFirst(4, condition)  # TreeScope_Children

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
                'correlation_id': self._get_correlation_id()
            }
        )
```

**Security Features**:
- Process blocklist enforcement
- Comprehensive audit logging
- Permission tier management
- Correlation IDs for tracking

---

### Pattern: Safe Input Simulation

**Use Case**: Sending keyboard/mouse input to applications with security controls.

**Implementation**:
```python
import ctypes
from ctypes import wintypes
import time

class SafeInputSimulator:
    """Input simulation with security controls."""

    # Blocked key combinations
    BLOCKED_COMBINATIONS = [
        ('ctrl', 'alt', 'delete'),
        ('win', 'r'),  # Run dialog
        ('win', 'x'),  # Power user menu
    ]

    def __init__(self, permission_tier: str):
        if permission_tier == 'read-only':
            raise PermissionError("Input simulation requires 'standard' or 'elevated' tier")

        self.permission_tier = permission_tier
        self.rate_limit = 100  # max inputs per second
        self._input_count = 0
        self._last_reset = time.time()

    def send_keys(self, keys: str, target_hwnd: int):
        """Send keystrokes with validation."""
        # Rate limiting
        self._check_rate_limit()

        # Validate target window
        if not self._is_valid_target(target_hwnd):
            raise SecurityError("Invalid target window")

        # Check for blocked combinations
        if self._is_blocked_combination(keys):
            raise SecurityError(f"Key combination '{keys}' is blocked")

        # Ensure target has focus
        if not self._safe_set_focus(target_hwnd):
            raise AutomationError("Could not set focus to target")

        # Send input
        self._send_input_safe(keys)

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

**Security Features**:
- Rate limiting to prevent input flooding
- Blocked key combination enforcement
- Target window validation
- Focus management

---

### Pattern: Process Validation

**Use Case**: Validating process identity and integrity before automation.

**Implementation**:
```python
import psutil
import hashlib

class ProcessValidator:
    """Validate processes before automation."""

    def __init__(self):
        self.known_hashes = {}  # Load from secure config

    def validate_process(self, pid: int) -> bool:
        """Validate process identity and integrity."""
        try:
            proc = psutil.Process(pid)

            # Check process name against blocklist
            if proc.name().lower() in BLOCKED_PROCESSES:
                return False

            # Verify executable integrity (optional, HIGH security)
            exe_path = proc.exe()
            if not self._verify_integrity(exe_path):
                return False

            # Check process owner
            if not self._check_owner(proc):
                return False

            return True

        except psutil.NoSuchProcess:
            return False

    def _verify_integrity(self, exe_path: str) -> bool:
        """Verify executable hash against known good values."""
        if exe_path not in self.known_hashes:
            return True  # Skip if no hash available

        with open(exe_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()

        return file_hash == self.known_hashes[exe_path]
```

**Security Features**:
- Process name validation
- Executable integrity checking (hash verification)
- Process owner verification
- Graceful handling of non-existent processes

---

### Pattern: Timeout Enforcement

**Use Case**: Preventing runaway automation operations.

**Implementation**:
```python
import signal
from contextlib import contextmanager

class TimeoutManager:
    """Enforce operation timeouts."""

    DEFAULT_TIMEOUT = 30  # seconds
    MAX_TIMEOUT = 300     # 5 minutes absolute max

    @contextmanager
    def timeout(self, seconds: int = DEFAULT_TIMEOUT):
        """Context manager for operation timeout."""
        if seconds > self.MAX_TIMEOUT:
            seconds = self.MAX_TIMEOUT

        def handler(signum, frame):
            raise TimeoutError(f"Operation timed out after {seconds}s")

        old_handler = signal.signal(signal.SIGALRM, handler)
        signal.alarm(seconds)

        try:
            yield
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)

# Usage
timeout_mgr = TimeoutManager()

with timeout_mgr.timeout(10):
    element = automation.find_element('notepad.exe', 'Edit1')
```

**Features**:
- Configurable timeout per operation
- Maximum timeout enforcement
- Context manager for clean resource management
- Automatic cleanup on exit

---

## Additional Advanced Patterns

### Pattern: Automation Guard (Runaway Prevention)

```python
class AutomationGuard:
    """Prevent runaway automation."""

    MAX_OPERATIONS = 1000
    MAX_DURATION = 300  # seconds

    def __init__(self):
        self.operation_count = 0
        self.start_time = time.time()

    def check_limits(self):
        """Check if limits exceeded."""
        self.operation_count += 1

        if self.operation_count > self.MAX_OPERATIONS:
            raise AutomationError("Operation limit exceeded")

        if time.time() - self.start_time > self.MAX_DURATION:
            raise AutomationError("Duration limit exceeded")

    def reset(self):
        """Reset counters."""
        self.operation_count = 0
        self.start_time = time.time()
```

### Pattern: Correlation ID Tracking

```python
import uuid

class CorrelationTracker:
    """Track operations with correlation IDs."""

    def __init__(self):
        self.correlation_id = None

    def start_session(self):
        """Start new session with correlation ID."""
        self.correlation_id = str(uuid.uuid4())
        return self.correlation_id

    def get_correlation_id(self):
        """Get current correlation ID."""
        if self.correlation_id is None:
            self.correlation_id = str(uuid.uuid4())
        return self.correlation_id

    def log_with_correlation(self, logger, message, **kwargs):
        """Log message with correlation ID."""
        logger.info(
            message,
            extra={'correlation_id': self.get_correlation_id(), **kwargs}
        )
```
