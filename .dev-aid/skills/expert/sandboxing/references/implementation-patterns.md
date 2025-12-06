## 5. Implementation Patterns

### 4.1 Seccomp-BPF Filter (python-seccomp)

```python
import seccomp
import os

def create_minimal_sandbox():
    """Create minimal seccomp sandbox for untrusted code."""
    filter = seccomp.SyscallFilter(defaction=seccomp.KILL)

    # Essential syscalls
    essential = [
        'read', 'write', 'close', 'fstat', 'lseek',
        'mmap', 'mprotect', 'munmap', 'brk',
        'rt_sigaction', 'rt_sigprocmask', 'rt_sigreturn',
        'exit', 'exit_group', 'futex', 'clock_gettime',
    ]

    for syscall in essential:
        filter.add_rule(seccomp.ALLOW, syscall)

    return filter

def run_sandboxed(func, *args, **kwargs):
    """Execute function in seccomp sandbox."""
    filter = create_minimal_sandbox()
    pid = os.fork()

    if pid == 0:
        filter.load()
        try:
            func(*args, **kwargs)
            os._exit(0)
        except Exception:
            os._exit(1)
    else:
        _, status = os.waitpid(pid, 0)
        return os.WEXITSTATUS(status) == 0
```

**📚 For custom BPF filters and advanced seccomp**:
- See `references/advanced-patterns.md#seccomp-bpf`

### 4.2 Bubblewrap Sandbox (Recommended)

```python
import subprocess
from typing import List

class BubblewrapSandbox:
    """High-level sandboxing using bubblewrap."""

    def __init__(self):
        self._args = ['bwrap']

    def with_minimal_filesystem(self) -> 'BubblewrapSandbox':
        self._args.extend([
            '--ro-bind', '/usr', '/usr',
            '--ro-bind', '/lib', '/lib',
            '--ro-bind', '/lib64', '/lib64',
            '--symlink', 'usr/bin', '/bin',
            '--proc', '/proc', '--dev', '/dev',
            '--tmpfs', '/tmp',
        ])
        return self

    def with_network_isolation(self) -> 'BubblewrapSandbox':
        self._args.append('--unshare-net')
        return self

    def drop_capabilities(self) -> 'BubblewrapSandbox':
        self._args.append('--cap-drop ALL')
        return self

    def run(self, command: List[str], timeout: int = 30):
        return subprocess.run(
            self._args + ['--'] + command,
            capture_output=True, timeout=timeout
        )

# Usage
def run_untrusted_script(script_path: str) -> str:
    sandbox = BubblewrapSandbox()
    sandbox.with_minimal_filesystem().with_network_isolation().drop_capabilities()
    result = sandbox.run(['python3', script_path], timeout=10)
    return result.stdout.decode()
```

**📚 For namespace isolation and advanced bubblewrap**:
- See `references/advanced-patterns.md#namespaces`

### 4.3 Kubernetes SecurityContext

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: jarvis-worker
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
    seccompProfile:
      type: RuntimeDefault

  containers:
  - name: worker
    image: jarvis-worker:latest
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: [ALL]

    resources:
      limits:
        cpu: "1"
        memory: "512Mi"

    volumeMounts:
    - name: tmp
      mountPath: /tmp

  volumes:
  - name: tmp
    emptyDir:
      medium: Memory
      sizeLimit: 64Mi
```

