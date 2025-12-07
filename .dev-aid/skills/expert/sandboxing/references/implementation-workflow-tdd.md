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

