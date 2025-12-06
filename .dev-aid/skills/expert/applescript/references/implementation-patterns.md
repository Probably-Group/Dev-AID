## 5. Implementation Patterns

### Pattern 1: Secure Script Execution

```python
import subprocess, re, logging

class SecureAppleScriptRunner:
    BLOCKED_PATTERNS = [
        r'do shell script.*with administrator',
        r'do shell script.*sudo',
        r'do shell script.*(rm -rf|rm -r)',
        r'do shell script.*curl.*\|.*sh',
        r'keystroke.*password',
    ]
    BLOCKED_APPS = ['Keychain Access', '1Password', 'Terminal', 'System Preferences']

    def __init__(self, permission_tier: str = 'standard'):
        self.permission_tier = permission_tier
        self.logger = logging.getLogger('applescript.security')

    def execute(self, script: str, timeout: int = 30) -> tuple[str, str]:
        self._check_blocked_patterns(script)
        self._check_blocked_apps(script)
        self.logger.info(f'applescript.execute', extra={'script': script[:100]})
        try:
            result = subprocess.run(['osascript', '-e', script],
                capture_output=True, text=True, timeout=timeout)
            return result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Script timed out after {timeout}s")

    def _check_blocked_patterns(self, script: str):
        for pattern in self.BLOCKED_PATTERNS:
            if re.search(pattern, script, re.IGNORECASE):
                raise SecurityError(f"Blocked pattern: {pattern}")

    def _check_blocked_apps(self, script: str):
        for app in self.BLOCKED_APPS:
            if app.lower() in script.lower():
                raise SecurityError(f"Access to {app} blocked")
```

### Pattern 2: Safe Input Interpolation

```python
class SafeScriptBuilder:
    """Build AppleScript with safe input interpolation."""

    @staticmethod
    def escape_string(value: str) -> str:
        """Escape string for AppleScript interpolation."""
        # Escape backslashes and quotes
        escaped = value.replace('\\', '\\\\').replace('"', '\\"')
        return escaped

    @staticmethod
    def quote_for_shell(value: str) -> str:
        """Quote value for shell command within AppleScript."""
        # Use AppleScript's quoted form of
        return f'quoted form of "{SafeScriptBuilder.escape_string(value)}"'

    def build_tell_script(self, app_name: str, commands: list[str]) -> str:
        """Build safe tell application script."""
        # Validate app name
        if not re.match(r'^[a-zA-Z0-9 ]+$', app_name):
            raise ValueError("Invalid application name")

        escaped_app = self.escape_string(app_name)
        escaped_commands = [self.escape_string(cmd) for cmd in commands]

        script = f'''
tell application "{escaped_app}"
    {chr(10).join(escaped_commands)}
end tell
'''
        return script.strip()

    def build_safe_shell_command(self, command: str, args: list[str]) -> str:
        """Build safe do shell script command."""
        # Allowlist of safe commands
        SAFE_COMMANDS = ['ls', 'pwd', 'date', 'whoami', 'echo']

        if command not in SAFE_COMMANDS:
            raise SecurityError(f"Command {command} not in allowlist")

        # Quote all arguments
        quoted_args = ' '.join(f'"{self.escape_string(arg)}"' for arg in args)

        return f'do shell script "{command} {quoted_args}"'
```

### Pattern 3: JXA (JavaScript for Automation)

```javascript
class SecureJXARunner {
    constructor() {
        this.blockedApps = ['Keychain Access', 'Terminal', 'System Preferences'];
    }

    runApplication(appName, action) {
        if (this.blockedApps.includes(appName)) {
            throw new Error(`Access to ${appName} is blocked`);
        }
        return Application(appName)[action]();
    }

    safeShellScript(command) {
        const blocked = [/rm\s+-rf/, /sudo/, /curl.*\|.*sh/];
        for (const p of blocked) {
            if (p.test(command)) throw new Error('Blocked command');
        }
        const app = Application.currentApplication();
        app.includeStandardAdditions = true;
        return app.doShellScript(command);
    }
}
```

### Pattern 4: Application Dictionary Validation

```python
class AppDictionaryValidator:
    def get_app_dictionary(self, app_name: str) -> str:
        result = subprocess.run(['sdef', f'/Applications/{app_name}.app'],
            capture_output=True, text=True)
        return result.stdout

    def is_scriptable(self, app_name: str) -> bool:
        try:
            return bool(self.get_app_dictionary(app_name).strip())
        except Exception:
            return False
```

---

