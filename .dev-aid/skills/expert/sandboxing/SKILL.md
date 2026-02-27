---
name: sandboxing
version: 2.0.0
description: "Application sandboxing patterns for process isolation, capability restrictions, and secure containment. Use when implementing sandboxing, restricting process capabilities, or designing isolation boundaries. Do NOT use for container orchestration (use Kubernetes or Tauri skills)."
risk_level: HIGH
token_budget: 4000
---
# Sandboxing Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.2 Security Patterns (security rules)

**CWE-269: Privilege Escalation**
- Do not: Sandbox with root/admin capabilities
- Instead: Drop privileges, use capability restrictions

**CWE-284: Improper Access Control**
- Do not: Shared filesystem/network with host
- Instead: Minimal mounts, network isolation, seccomp filters

**CWE-693: Sandbox Escape**
- Do not: Trust sandboxed code to stay sandboxed
- Instead: Defense in depth, monitor for escape attempts

---

## 1. Security Principles

### 1.1 Principle of Least Privilege (CWE-250)

**Principle:** Grant minimum permissions. Drop privileges immediately after acquisition.

```rust
// ❌ WRONG - Running with full privileges
fn process_untrusted_data(data: &[u8]) {
    // Processing with full system access!
    let result = parse(data);
}

// ✅ CORRECT - Drop privileges before processing
use caps::{CapSet, Capability, set};

fn process_untrusted_data(data: &[u8]) -> Result<(), Error> {
    // Drop all capabilities
    set(None, CapSet::Effective, &[])?;
    set(None, CapSet::Permitted, &[])?;

    // Now process with minimal privileges
    let result = parse(data)?;
    Ok(())
}
```

### 1.2 Defense in Depth (CWE-636)

**Principle:** Multiple isolation layers. Don't rely on single sandbox mechanism.

```rust
// ❌ WRONG - Single layer of isolation
fn sandbox_process() {
    chroot("/sandbox");  // Only filesystem isolation
    run_untrusted_code();
}

// ✅ CORRECT - Multiple isolation layers
fn sandbox_process() -> Result<(), Error> {
    // 1. Filesystem isolation
    chroot("/sandbox")?;

    // 2. Namespace isolation
    unshare(CloneFlags::CLONE_NEWPID | CloneFlags::CLONE_NEWNET)?;

    // 3. Seccomp filtering
    apply_seccomp_filter()?;

    // 4. Capability dropping
    drop_all_capabilities()?;

    // 5. Resource limits
    set_resource_limits()?;

    // Now run with multiple protection layers
    run_untrusted_code()
}
```

### 1.3 Fail Secure (CWE-636)

**Principle:** On sandbox setup failure, abort. Never run untrusted code without sandbox.

```rust
// ❌ WRONG - Fallback to unsandboxed execution
fn execute(code: &str) {
    if sandbox_setup().is_err() {
        // Running without sandbox!
        run(code);
    }
}

// ✅ CORRECT - Abort on sandbox failure
fn execute(code: &str) -> Result<Output, Error> {
    sandbox_setup()?;  // Propagate error, don't run if fails
    run(code)
}
```

### 1.4 Input Validation (CWE-20)

**Principle:** Validate all data crossing sandbox boundaries. Sanitize before deserialization.

### 1.5 No Escape Paths (CWE-284)

**Principle:** Close all file descriptors except allowed. No symlink following.

### 1.6 Resource Limits (CWE-400)

**Principle:** Set CPU, memory, file descriptor limits. Prevent DoS from inside sandbox.

---

## 2. Version Requirements

Use these minimum versions:

```toml
# Rust
[dependencies]
seccompiler = "0.4"
nix = "0.29"
caps = "0.5"
landlock = "0.3"  # Linux 5.13+

# Python
seccomp>=2.5.0
pyprctl>=1.8.0

# Node.js
isolated-vm>=4.7.0
```

---

## 3. Code Patterns

### 3.1 WHEN implementing Linux seccomp filter (Rust)

```rust
use seccompiler::{
    BpfMap, SeccompAction, SeccompFilter, SeccompRule,
    TargetArch, SeccompCmpOp, SeccompCmpArgLen,
};
use std::collections::BTreeMap;

/// Create restrictive seccomp filter for untrusted code
pub fn create_sandbox_filter() -> Result<BpfMap, Error> {
    let mut rules: BTreeMap<i64, Vec<SeccompRule>> = BTreeMap::new();

    // Allow basic operations
    let allowed_syscalls = [
        libc::SYS_read,
        libc::SYS_write,
        libc::SYS_exit,
        libc::SYS_exit_group,
        libc::SYS_brk,
        libc::SYS_mmap,
        libc::SYS_munmap,
        libc::SYS_clock_gettime,
    ];

    for syscall in allowed_syscalls {
        rules.insert(syscall, vec![SeccompRule::new(vec![])]);
    }

    // Allow write only to stdout/stderr (fd 1, 2)
    rules.insert(
        libc::SYS_write,
        vec![
            SeccompRule::new(vec![
                seccompiler::SeccompCondition::new(
                    0,  // arg0 = fd
                    SeccompCmpArgLen::Dword,
                    SeccompCmpOp::Eq,
                    1,  // stdout
                )?,
            ]),
            SeccompRule::new(vec![
                seccompiler::SeccompCondition::new(
                    0,
                    SeccompCmpArgLen::Dword,
                    SeccompCmpOp::Eq,
                    2,  // stderr
                )?,
            ]),
        ],
    );

    // Build filter - default action is KILL
    let filter = SeccompFilter::new(
        rules,
        SeccompAction::KillProcess,  // Kill on disallowed syscall
        SeccompAction::Allow,
        TargetArch::x86_64,
    )?;

    Ok(filter.try_into()?)
}

/// Apply seccomp filter to current process
pub fn apply_seccomp() -> Result<(), Error> {
    let filter = create_sandbox_filter()?;

    // Apply filter - no going back after this
    seccompiler::apply_filter(&filter)?;

    Ok(())
}
```

### 3.2 WHEN implementing Linux namespaces isolation (Rust)

```rust
use nix::sched::{unshare, CloneFlags};
use nix::unistd::{chroot, chdir, setuid, setgid, Uid, Gid};
use nix::mount::{mount, MsFlags};
use std::fs;

pub struct SandboxConfig {
    pub root_dir: PathBuf,
    pub uid: u32,
    pub gid: u32,
    pub memory_limit_mb: u64,
    pub cpu_time_limit_secs: u64,
}

/// Create isolated sandbox using Linux namespaces
pub fn create_namespace_sandbox(config: &SandboxConfig) -> Result<(), Error> {
    // 1. Create new namespaces
    unshare(
        CloneFlags::CLONE_NEWUSER |   // User namespace
        CloneFlags::CLONE_NEWPID |    // PID namespace
        CloneFlags::CLONE_NEWNET |    // Network namespace
        CloneFlags::CLONE_NEWNS |     // Mount namespace
        CloneFlags::CLONE_NEWIPC |    // IPC namespace
        CloneFlags::CLONE_NEWUTS      // UTS namespace
    )?;

    // 2. Set up minimal filesystem
    setup_sandbox_filesystem(&config.root_dir)?;

    // 3. Chroot into sandbox
    chroot(&config.root_dir)?;
    chdir("/")?;

    // 4. Drop to unprivileged user
    setgid(Gid::from_raw(config.gid))?;
    setuid(Uid::from_raw(config.uid))?;

    // 5. Set resource limits
    set_rlimits(config)?;

    Ok(())
}

fn setup_sandbox_filesystem(root: &Path) -> Result<(), Error> {
    // Create minimal directory structure
    fs::create_dir_all(root.join("tmp"))?;
    fs::create_dir_all(root.join("dev"))?;

    // Mount minimal /dev
    mount(
        Some("devtmpfs"),
        &root.join("dev"),
        Some("devtmpfs"),
        MsFlags::MS_NOSUID | MsFlags::MS_NOEXEC,
        None::<&str>,
    )?;

    // Create /dev/null, /dev/zero, /dev/urandom
    create_device_node(&root.join("dev/null"), 1, 3)?;
    create_device_node(&root.join("dev/zero"), 1, 5)?;
    create_device_node(&root.join("dev/urandom"), 1, 9)?;

    // Make root read-only
    mount(
        None::<&str>,
        root,
        None::<&str>,
        MsFlags::MS_REMOUNT | MsFlags::MS_RDONLY,
        None::<&str>,
    )?;

    Ok(())
}

fn set_rlimits(config: &SandboxConfig) -> Result<(), Error> {
    use nix::sys::resource::{setrlimit, Resource};

    // Memory limit
    let mem_bytes = config.memory_limit_mb * 1024 * 1024;
    setrlimit(Resource::RLIMIT_AS, mem_bytes, mem_bytes)?;

    // CPU time limit
    setrlimit(
        Resource::RLIMIT_CPU,
        config.cpu_time_limit_secs,
        config.cpu_time_limit_secs,
    )?;

    // File descriptor limit
    setrlimit(Resource::RLIMIT_NOFILE, 64, 64)?;

    // No core dumps
    setrlimit(Resource::RLIMIT_CORE, 0, 0)?;

    // No new processes
    setrlimit(Resource::RLIMIT_NPROC, 0, 0)?;

    Ok(())
}
```

### 3.3 WHEN implementing Landlock filesystem sandbox (Rust)

```rust
use landlock::{
    Access, AccessFs, PathBeneath, PathFd, Ruleset,
    RulesetAttr, RulesetCreatedAttr, ABI,
};

/// Create Landlock sandbox restricting filesystem access
pub fn create_landlock_sandbox(
    read_paths: &[&Path],
    write_paths: &[&Path],
) -> Result<(), Error> {
    // Check Landlock support
    let abi = ABI::V3;  // Linux 6.2+

    // Create ruleset - deny all by default
    let mut ruleset = Ruleset::new()
        .handle_access(AccessFs::from_all(abi))?
        .create()?;

    // Allow read access to specific paths
    for path in read_paths {
        let path_fd = PathFd::new(path)?;
        ruleset = ruleset.add_rule(PathBeneath::new(
            path_fd,
            AccessFs::ReadFile | AccessFs::ReadDir | AccessFs::Execute,
        ))?;
    }

    // Allow write access to specific paths
    for path in write_paths {
        let path_fd = PathFd::new(path)?;
        ruleset = ruleset.add_rule(PathBeneath::new(
            path_fd,
            AccessFs::from_write(abi),
        ))?;
    }

    // Enforce ruleset - no going back
    ruleset.restrict_self()?;

    Ok(())
}

// Usage example
fn sandbox_code_execution() -> Result<(), Error> {
    // Only allow reading from /usr and writing to /tmp
    create_landlock_sandbox(
        &[Path::new("/usr"), Path::new("/lib")],
        &[Path::new("/tmp/sandbox")],
    )?;

    // Now filesystem access is restricted
    execute_untrusted_code()
}
```

### 3.4 WHEN implementing macOS sandbox (Rust)

```rust
use std::process::Command;

/// macOS sandbox profile for untrusted code
const SANDBOX_PROFILE: &str = r#"
(version 1)
(deny default)

;; Allow read-only access to system libraries
(allow file-read*
    (subpath "/usr/lib")
    (subpath "/System/Library/Frameworks")
    (subpath "/Library/Frameworks"))

;; Allow read/write to sandbox directory only
(allow file-read* file-write*
    (subpath "/tmp/sandbox"))

;; Allow basic process operations
(allow process-fork)
(allow signal (target self))

;; Deny network access
(deny network*)

;; Deny hardware access
(deny iokit*)
"#;

/// Execute code in macOS sandbox
pub fn execute_in_sandbox(command: &str, args: &[&str]) -> Result<Output, Error> {
    let output = Command::new("sandbox-exec")
        .arg("-p")
        .arg(SANDBOX_PROFILE)
        .arg(command)
        .args(args)
        .output()?;

    Ok(output)
}
```

### 3.5 WHEN implementing WebAssembly sandbox

```rust
use wasmtime::*;

pub struct WasmSandbox {
    engine: Engine,
    store: Store<SandboxState>,
    linker: Linker<SandboxState>,
}

struct SandboxState {
    memory_used: usize,
    fuel_remaining: u64,
}

impl WasmSandbox {
    pub fn new(memory_limit_mb: usize, fuel_limit: u64) -> Result<Self, Error> {
        let mut config = Config::new();

        // Enable fuel-based execution limits
        config.consume_fuel(true);

        // Memory limits
        config.max_wasm_stack(1024 * 1024);  // 1MB stack

        let engine = Engine::new(&config)?;

        let mut store = Store::new(
            &engine,
            SandboxState {
                memory_used: 0,
                fuel_remaining: fuel_limit,
            },
        );

        // Set fuel limit
        store.set_fuel(fuel_limit)?;

        let mut linker = Linker::new(&engine);

        // Only link safe, controlled imports
        linker.func_wrap("env", "print", |caller: Caller<'_, SandboxState>, ptr: i32, len: i32| {
            // Controlled print function - no filesystem access
            let mem = caller.get_export("memory")
                .and_then(|e| e.into_memory())
                .ok_or(anyhow::anyhow!("no memory"))?;

            let data = mem.data(&caller);
            let msg = std::str::from_utf8(&data[ptr as usize..(ptr + len) as usize])?;
            println!("WASM: {}", msg);
            Ok(())
        })?;

        Ok(Self { engine, store, linker })
    }

    pub fn execute(&mut self, wasm_bytes: &[u8]) -> Result<Vec<Val>, Error> {
        // Validate WASM module
        let module = Module::new(&self.engine, wasm_bytes)?;

        // Instantiate with limited imports
        let instance = self.linker.instantiate(&mut self.store, &module)?;

        // Get and call main function
        let main = instance
            .get_typed_func::<(), ()>(&mut self.store, "_start")?;

        main.call(&mut self.store, ())?;

        // Check fuel consumption
        let fuel_used = self.store.get_data().fuel_remaining - self.store.get_fuel()?;
        println!("Fuel used: {}", fuel_used);

        Ok(vec![])
    }
}
```

### 3.6 WHEN implementing Node.js isolated-vm sandbox

```typescript
import ivm from 'isolated-vm';

interface SandboxOptions {
  memoryLimitMb: number;
  timeoutMs: number;
}

export class JavaScriptSandbox {
  private isolate: ivm.Isolate;
  private context: ivm.Context;

  constructor(options: SandboxOptions) {
    // Create isolate with memory limit
    this.isolate = new ivm.Isolate({
      memoryLimit: options.memoryLimitMb,
    });

    // Create context (separate global)
    this.context = this.isolate.createContextSync();

    // Set up safe globals
    this.setupSafeGlobals();
  }

  private setupSafeGlobals(): void {
    const jail = this.context.global;

    // Expose safe console.log
    jail.setSync('log', new ivm.Callback((msg: string) => {
      console.log('Sandbox:', msg);
    }));

    // NO access to: require, process, fs, network, etc.
  }

  async execute(code: string, timeoutMs: number): Promise<unknown> {
    // Compile in isolate
    const script = await this.isolate.compileScript(code);

    // Run with timeout
    const result = await script.run(this.context, {
      timeout: timeoutMs,
    });

    return result;
  }

  dispose(): void {
    this.context.release();
    this.isolate.dispose();
  }
}

// Usage
async function runUntrustedCode(userCode: string) {
  const sandbox = new JavaScriptSandbox({
    memoryLimitMb: 128,
    timeoutMs: 5000,
  });

  try {
    const result = await sandbox.execute(userCode, 5000);
    return result;
  } finally {
    sandbox.dispose();
  }
}
```

---

## 4. Anti-Patterns

Do not:
- Run untrusted code without sandbox setup
- Fall back to unsandboxed execution on errors
- Allow sandbox to access network (unless required)
- Use chroot alone (not a security boundary)
- Keep file descriptors open in sandbox
- Trust data from sandboxed process without validation
- Skip resource limits (CPU, memory, file descriptors)

---

## 5. Testing

**ALWAYS test sandbox escapes:**

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sandbox_blocks_file_access() {
        let sandbox = create_sandbox("/tmp/test").unwrap();
# ... (additional test cases follow same pattern)
```

---

## 6. Pre-Generation Checklist

Before generating any sandboxing code:

- [ ] Multiple isolation layers (namespace + seccomp + capabilities)
- [ ] Fail secure - abort if sandbox setup fails
- [ ] Resource limits set (CPU, memory, file descriptors)
- [ ] Network access denied by default
- [ ] Filesystem access minimal and read-only where possible
- [ ] All file descriptors closed except required
- [ ] No symlink following in sandbox
- [ ] Capabilities dropped after setup
- [ ] Data from sandbox validated before use
- [ ] Platform-specific mechanisms used (Landlock/seccomp on Linux, sandbox-exec on macOS)

---
