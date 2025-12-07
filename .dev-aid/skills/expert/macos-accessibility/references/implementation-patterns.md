## 5. Implementation Patterns

### Pattern 1: TCC Permission Validation

```python
import subprocess
from ApplicationServices import (
    AXIsProcessTrustedWithOptions,
    kAXTrustedCheckOptionPrompt
)

class TCCValidator:
    """Validate TCC permissions before automation."""

    @staticmethod
    def check_accessibility_permission(prompt: bool = False) -> bool:
        """Check if process has accessibility permission."""
        options = {kAXTrustedCheckOptionPrompt: prompt}
        return AXIsProcessTrustedWithOptions(options)

    @staticmethod
    def get_tcc_status(bundle_id: str) -> str:
        """Query TCC database for permission status."""
        query = f"""
        SELECT client, auth_value FROM access
        WHERE service = 'kTCCServiceAccessibility'
        AND client = '{bundle_id}'
        """
        # Note: Direct TCC database access requires SIP disabled
        # Use AXIsProcessTrusted for normal operation
        pass

    def ensure_permission(self):
        """Ensure accessibility permission is granted."""
        if not self.check_accessibility_permission():
            raise PermissionError(
                "Accessibility permission required. "
                "Enable in System Preferences > Security & Privacy > Accessibility"
            )
```

### Pattern 2: Secure Element Discovery

```python
from ApplicationServices import (
    AXUIElementCreateSystemWide,
    AXUIElementCreateApplication,
    AXUIElementCopyAttributeValue,
    AXUIElementCopyAttributeNames,
)
from Quartz import kAXErrorSuccess
import logging

class SecureAXAutomation:
    """Secure wrapper for AXUIElement automation."""

    BLOCKED_APPS = {
        'com.apple.keychainaccess',           # Keychain Access
        'com.apple.systempreferences',         # System Preferences
        'com.apple.SecurityAgent',             # Security dialogs
        'com.apple.Terminal',                  # Terminal
        'com.1password.1password',             # 1Password
    }

    def __init__(self, permission_tier: str = 'read-only'):
        self.permission_tier = permission_tier
        self.logger = logging.getLogger('ax.security')
        self.operation_timeout = 30

        # Validate TCC permission on init
        if not TCCValidator.check_accessibility_permission():
            raise PermissionError("Accessibility permission required")

    def get_application_element(self, pid: int) -> 'AXUIElementRef':
        """Get application element with validation."""
        # Get bundle ID
        bundle_id = self._get_bundle_id(pid)

        # Security check
        if bundle_id in self.BLOCKED_APPS:
            self.logger.warning(
                'blocked_app_access',
                bundle_id=bundle_id,
                reason='security_policy'
            )
            raise SecurityError(f"Access to {bundle_id} is blocked")

        # Create element
        app_element = AXUIElementCreateApplication(pid)

        self._audit_log('app_element_created', bundle_id, pid)
        return app_element

    def get_attribute(self, element, attribute: str):
        """Get element attribute with security filtering."""
        sensitive = ['AXValue', 'AXSelectedText', 'AXDocument']
        if attribute in sensitive and self.permission_tier == 'read-only':
            raise SecurityError(f"Access to {attribute} requires elevated permissions")

        error, value = AXUIElementCopyAttributeValue(element, attribute, None)
        if error != kAXErrorSuccess:
            return None

        # Redact password values
        return '[REDACTED]' if 'password' in str(attribute).lower() else value

    def _audit_log(self, action: str, bundle_id: str, pid: int):
        self.logger.info(f'ax.{action}', extra={
            'bundle_id': bundle_id, 'pid': pid, 'permission_tier': self.permission_tier
        })
```

### Pattern 3: Safe Action Execution

```python
from ApplicationServices import AXUIElementPerformAction

class SafeActionExecutor:
    """Execute AX actions with security controls."""
    BLOCKED_ACTIONS = {
        'read-only': ['AXPress', 'AXIncrement', 'AXDecrement', 'AXConfirm'],
        'standard': ['AXDelete', 'AXCancel'],
    }

    def __init__(self, permission_tier: str):
        self.permission_tier = permission_tier

    def perform_action(self, element, action: str):
        blocked = self.BLOCKED_ACTIONS.get(self.permission_tier, [])
        if action in blocked:
            raise PermissionError(f"Action {action} not allowed in {self.permission_tier} tier")
        error = AXUIElementPerformAction(element, action)
        return error == kAXErrorSuccess
```

### Pattern 4: Application Monitoring

```python
from AppKit import NSWorkspace, NSRunningApplication

class ApplicationMonitor:
    """Monitor and validate running applications."""

    def get_frontmost_app(self) -> dict:
        app = NSWorkspace.sharedWorkspace().frontmostApplication()
        return {
            'pid': app.processIdentifier(),
            'bundle_id': app.bundleIdentifier(),
            'name': app.localizedName(),
        }

    def validate_application(self, pid: int) -> bool:
        app = NSRunningApplication.runningApplicationWithProcessIdentifier_(pid)
        if not app or app.bundleIdentifier() in SecureAXAutomation.BLOCKED_APPS:
            return False
        # Verify code signature
        result = subprocess.run(['codesign', '-v', app.bundleURL().path()], capture_output=True)
        return result.returncode == 0
```

---

