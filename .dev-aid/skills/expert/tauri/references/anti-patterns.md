# Tauri Anti-Patterns and Common Mistakes

This document catalogs common mistakes and anti-patterns to avoid when developing Tauri applications, along with secure alternatives.

---

## Anti-Pattern 1: Overly Permissive Capabilities

**Problem**: Granting broad filesystem or system access creates security vulnerabilities.

**Bad Example - Unrestricted Access**:
```json
// NEVER: Grants access to entire filesystem
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "dangerous",
  "permissions": [
    "fs:default",           // Too broad
    "fs:scope-home",        // Access to entire home directory
    "shell:allow-execute",  // Can execute any command
    "shell:allow-open"      // Can open any file/URL
  ]
}
```

**Why This is Dangerous**:
- Malicious code can read sensitive files (`~/.ssh/`, `~/.aws/`, etc.)
- Can modify system files if run with elevated privileges
- Can execute arbitrary commands
- Violates principle of least privilege

**Good Example - Scoped Access**:
```json
// ALWAYS: Scope to specific directories with explicit paths
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "secure",
  "description": "Minimal permissions for app functionality",
  "windows": ["main"],
  "permissions": [
    "core:event:default",
    "core:window:default",
    {
      "identifier": "fs:read-files",
      "allow": [
        "$APPDATA/myapp/*",      // Only app's data directory
        "$RESOURCE/assets/*"      // Only bundled resources
      ]
    },
    {
      "identifier": "fs:write-files",
      "allow": [
        "$APPDATA/myapp/config/*",    // Only config directory
        "$APPDATA/myapp/user-data/*"  // Only user data directory
      ],
      "deny": [
        "$APPDATA/myapp/config/private/*"  // Explicit denials
      ]
    }
  ]
}
```

**Best Practices**:
- Start with zero permissions, add only what's needed
- Use path variables (`$APPDATA`, `$RESOURCE`) instead of hardcoded paths
- Prefer `allow` lists over `deny` lists
- Use explicit wildcards (`/*`) not recursive (`/**`)
- Document why each permission is needed

---

## Anti-Pattern 2: Disabled or Weak CSP

**Problem**: Weak Content Security Policy allows XSS and data exfiltration.

**Bad Example - CSP Disabled or Weak**:
```json
// NEVER: Disables CSP entirely
{
  "app": {
    "security": {
      "csp": null  // Catastrophic security hole!
    }
  }
}

// NEVER: Overly permissive CSP
{
  "app": {
    "security": {
      "csp": {
        "default-src": "*",              // Allows everything
        "script-src": "'self' 'unsafe-eval' 'unsafe-inline'",  // Allows eval()
        "connect-src": "*"               // Can connect anywhere
      }
    }
  }
}
```

**Risks**:
- XSS attacks can execute arbitrary JavaScript
- Data can be exfiltrated to any domain
- Inline scripts can bypass security measures
- Third-party scripts can access IPC commands

**Good Example - Restrictive CSP**:
```json
// ALWAYS: Strict CSP with explicit allowlists
{
  "app": {
    "security": {
      "csp": {
        "default-src": "'self'",
        "script-src": "'self'",  // No eval, no inline scripts
        "style-src": "'self' 'unsafe-inline'",  // Inline styles for frameworks
        "img-src": "'self' data: https:",
        "font-src": "'self' data:",
        "connect-src": "'self' https://api.example.com https://cdn.example.com",
        "object-src": "'none'",
        "base-uri": "'self'",
        "frame-ancestors": "'none'",
        "form-action": "'self'",
        "upgrade-insecure-requests": true
      },
      "dangerousDisableAssetCspModification": false,
      "freezePrototype": true  // Prevent prototype pollution
    }
  }
}
```

**CSP Best Practices**:
- Never use `'unsafe-eval'` - opens eval() and Function() attacks
- Minimize use of `'unsafe-inline'` - prefer nonces or hashes
- Use `'self'` as default, add external domains explicitly
- Include `frame-ancestors 'none'` to prevent clickjacking
- Always enable `freezePrototype` to prevent prototype pollution
- Test CSP with browser console (shows violations)

---

## Anti-Pattern 3: Shell Execution Enabled

**Problem**: Shell execution is a critical security risk if not properly restricted.

**Bad Example - Unrestricted Shell Access**:
```json
// NEVER: Allows arbitrary command execution
{
  "permissions": [
    "shell:allow-execute",  // Can execute ANY command
    "shell:allow-open"      // Can open ANY file/URL
  ]
}
```

```rust
// NEVER: Unsanitized shell commands
#[command]
fn run_command(cmd: String) -> Result<String, String> {
    // Command injection vulnerability!
    Command::new("sh")
        .arg("-c")
        .arg(cmd)  // User input directly in shell
        .output()
        .map(|o| String::from_utf8_lossy(&o.stdout).to_string())
        .map_err(|e| e.to_string())
}
```

**Attack Vector**:
```typescript
// Attacker can inject commands
await invoke('run_command', {
    cmd: 'ls; rm -rf /'  // Command injection!
})
```

**Good Example - Disabled or Strict Allowlist**:
```json
// BEST: Disable shell execution entirely
{
  "permissions": []  // No shell permissions
}

// IF NEEDED: Use strict allowlist with fixed arguments
{
  "permissions": [
    {
      "identifier": "shell:allow-execute",
      "allow": [
        {
          "name": "git-status",
          "cmd": "git",
          "args": ["status", "--porcelain"],
          "sidecar": false
        },
        {
          "name": "git-log",
          "cmd": "git",
          "args": ["log", "--oneline", "-n", "10"],
          "sidecar": false
        }
      ]
    }
  ]
}
```

```rust
// ALWAYS: Use sidecar binaries or strict validation
#[command]
fn git_status() -> Result<String, String> {
    // Fixed command, no user input
    Command::new("git")
        .args(["status", "--porcelain"])
        .current_dir(get_repo_dir()?)  // Controlled directory
        .output()
        .map(|o| String::from_utf8_lossy(&o.stdout).to_string())
        .map_err(|e| e.to_string())
}

// If you MUST accept parameters, validate strictly
#[command]
fn git_log(max_count: u32) -> Result<String, String> {
    let max_count = max_count.min(100);  // Cap at 100

    Command::new("git")
        .args(["log", "--oneline", "-n", &max_count.to_string()])
        .current_dir(get_repo_dir()?)
        .output()
        .map(|o| String::from_utf8_lossy(&o.stdout).to_string())
        .map_err(|e| e.to_string())
}
```

**Shell Security Rules**:
1. Disable shell execution unless absolutely required
2. Never execute user-provided shell commands
3. Use allowlist with fixed commands and arguments
4. Prefer sidecar binaries over system commands
5. Validate and sanitize ALL inputs
6. Use absolute paths for executables
7. Set safe working directory explicitly

---

## Anti-Pattern 4: Exposing Tauri Private Keys

**Problem**: Vite configuration leaking private keys to frontend bundle.

**Bad Example - Keys Leaked to Frontend**:
```typescript
// vite.config.ts - NEVER DO THIS
export default defineConfig({
  envPrefix: ['VITE_', 'TAURI_'],  // Exposes TAURI_PRIVATE_KEY!

  // This puts your private key in the browser bundle!
  // Anyone can extract it from your compiled JavaScript
})
```

**Impact**:
- `TAURI_PRIVATE_KEY` is included in frontend bundle
- Attackers can extract key from compiled JavaScript
- Can forge update signatures
- Compromises entire update mechanism

**Good Example - Secure Environment Configuration**:
```typescript
// vite.config.ts - ALWAYS
export default defineConfig({
  envPrefix: ['VITE_'],  // ONLY expose VITE_ variables

  // TAURI_ variables stay in backend only
})
```

```rust
// Backend: Access Tauri keys securely
fn get_updater_config() -> Result<UpdaterConfig, Error> {
    // Private key stays in environment, never in frontend
    let private_key = std::env::var("TAURI_PRIVATE_KEY")
        .map_err(|_| Error::Configuration("TAURI_PRIVATE_KEY not set".into()))?;

    // Never log or expose this value
    Ok(UpdaterConfig { private_key })
}
```

**Environment Variable Rules**:
- Only expose `VITE_` prefix to frontend
- Keep `TAURI_` variables backend-only
- Never commit `.env` files with secrets
- Use `.env.example` for documentation
- Validate required env vars on startup
- Never log sensitive values

---

## Anti-Pattern 5: No Input Validation on IPC Commands

**Problem**: Trusting frontend input without validation creates vulnerabilities.

**Bad Example - No Validation**:
```rust
// NEVER: Directly use user input
#[command]
fn read_file(path: String) -> String {
    // Path traversal vulnerability!
    std::fs::read_to_string(path).unwrap()  // Can read ANY file
}

#[command]
fn save_data(key: String, value: String) -> Result<(), String> {
    // SQL injection if using SQL
    // No length limits, can exhaust memory
    database.insert(&key, &value)
}

#[command]
fn process_amount(amount: f64) -> Result<(), String> {
    // No bounds checking
    // Can be negative, NaN, or infinity
    charge_customer(amount)
}
```

**Attack Examples**:
```typescript
// Path traversal
await invoke('read_file', { path: '../../../etc/passwd' })

// Memory exhaustion
await invoke('save_data', {
    key: 'x',
    value: 'A'.repeat(1000000000)  // Gigabytes of data
})

// Logic errors
await invoke('process_amount', { amount: -1000 })  // Negative amount
await invoke('process_amount', { amount: NaN })     // Not a number
```

**Good Example - Comprehensive Validation**:
```rust
use validator::{Validate, ValidationError};
use std::path::{Path, PathBuf};

#[derive(serde::Deserialize, Validate)]
pub struct FileRequest {
    #[validate(length(min = 1, max = 255))]
    #[validate(custom(function = "validate_no_path_traversal"))]
    path: String,
}

fn validate_no_path_traversal(path: &str) -> Result<(), ValidationError> {
    if path.contains("..") || path.contains("~") || path.starts_with('/') {
        return Err(ValidationError::new("path_traversal"));
    }
    Ok(())
}

// ALWAYS: Validate all inputs
#[command]
pub async fn read_file(
    request: FileRequest,
    app: AppHandle,
) -> Result<String, String> {
    // Validate input structure
    request.validate()
        .map_err(|e| format!("Validation error: {}", e))?;

    // Resolve path within app directory only
    let app_dir = app.path().app_data_dir()
        .map_err(|e| e.to_string())?;
    let full_path = app_dir.join(&request.path);

    // Canonicalize to resolve symlinks and .. components
    let canonical = dunce::canonicalize(&full_path)
        .map_err(|_| "Invalid path")?;

    // Verify path is still within app directory
    if !canonical.starts_with(&app_dir) {
        return Err("Access denied: path traversal detected".into());
    }

    // Check file size before reading
    let metadata = tokio::fs::metadata(&canonical).await
        .map_err(|e| format!("File error: {}", e))?;

    if metadata.len() > 10_000_000 {  // 10MB limit
        return Err("File too large".into());
    }

    // Finally read the file
    tokio::fs::read_to_string(canonical).await
        .map_err(|e| format!("Read error: {}", e))
}

#[derive(serde::Deserialize, Validate)]
pub struct SaveDataRequest {
    #[validate(length(min = 1, max = 100))]
    #[validate(regex(path = "ALPHANUMERIC_REGEX"))]
    key: String,

    #[validate(length(min = 1, max = 1_000_000))]  // 1MB limit
    value: String,
}

#[command]
pub async fn save_data(request: SaveDataRequest) -> Result<(), String> {
    request.validate()
        .map_err(|e| format!("Validation error: {}", e))?;

    database.insert(&request.key, &request.value).await
}

#[derive(serde::Deserialize, Validate)]
pub struct AmountRequest {
    #[validate(range(min = 0.01, max = 10000.0))]
    amount: f64,
}

#[command]
pub async fn process_amount(request: AmountRequest) -> Result<(), String> {
    request.validate()
        .map_err(|e| format!("Validation error: {}", e))?;

    // Additional validation for special float values
    if !request.amount.is_finite() {
        return Err("Invalid amount: must be a finite number".into());
    }

    charge_customer(request.amount).await
}
```

**Validation Best Practices**:
- Use `validator` crate for declarative validation
- Validate length, range, format, and content
- Canonicalize file paths and check they stay in bounds
- Set maximum sizes for strings, arrays, file uploads
- Check for NaN, Infinity in float inputs
- Use regex for format validation (email, phone, etc.)
- Return clear error messages (but don't leak system info)
- Log validation failures for security monitoring

---

## Anti-Pattern 6: Exposing Internal Errors to Frontend

**Problem**: Leaking internal error details can expose system information to attackers.

**Bad Example - Information Disclosure**:
```rust
// NEVER: Expose internal errors directly
#[command]
fn database_query(query: String) -> Result<Vec<Row>, String> {
    database.execute(&query)
        .map_err(|e| e.to_string())  // Exposes SQL errors, table names, etc.
}

// Frontend sees: "table 'admin_users' does not exist"
// Reveals internal database structure!
```

**Good Example - Safe Error Handling**:
```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("Invalid input provided")]
    Validation(#[from] validator::ValidationErrors),

    #[error("Operation not permitted")]
    PermissionDenied,

    #[error("Resource not found")]
    NotFound,

    #[error("An internal error occurred")]
    Internal(#[source] anyhow::Error),
}

// Safe serialization - log details internally, return generic message
impl serde::Serialize for AppError {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where S: serde::Serializer {
        // Log full error details for debugging
        tracing::error!("Error occurred: {:?}", self);

        // Return safe message to frontend
        serializer.serialize_str(&self.to_string())
    }
}

#[command]
fn database_query(query: Query) -> Result<Vec<Row>, AppError> {
    database.execute(&query)
        .map_err(|e| AppError::Internal(e.into()))
}
```

---

## Anti-Pattern 7: Synchronous File Operations in Commands

**Problem**: Blocking operations freeze the UI.

**Bad Example**:
```rust
// NEVER: Blocks the event loop
#[command]
fn load_large_file(path: String) -> Result<String, String> {
    std::fs::read_to_string(path).map_err(|e| e.to_string())
}
```

**Good Example**:
```rust
// ALWAYS: Use async
#[command]
async fn load_large_file(path: String) -> Result<String, String> {
    tokio::fs::read_to_string(path).await.map_err(|e| e.to_string())
}
```

---

## Anti-Pattern 8: Global State Without Synchronization

**Problem**: Race conditions and data corruption in concurrent access.

**Bad Example**:
```rust
// NEVER: Unsynchronized global state
static mut COUNTER: i32 = 0;

#[command]
fn increment() -> i32 {
    unsafe {
        COUNTER += 1;  // Race condition!
        COUNTER
    }
}
```

**Good Example**:
```rust
use std::sync::atomic::{AtomicI32, Ordering};

static COUNTER: AtomicI32 = AtomicI32::new(0);

#[command]
fn increment() -> i32 {
    COUNTER.fetch_add(1, Ordering::SeqCst)
}

// Or use Mutex/RwLock for complex state
use parking_lot::Mutex;
use tauri::State;

#[command]
fn update_state(state: State<'_, Mutex<AppState>>) -> Result<(), String> {
    let mut state = state.lock();
    state.update();
    Ok(())
}
```

---

## Security Anti-Patterns Summary

**Never Do**:
- ❌ Grant broad filesystem access
- ❌ Disable or weaken CSP
- ❌ Enable shell execution without allowlist
- ❌ Expose TAURI_ environment variables to frontend
- ❌ Trust frontend input without validation
- ❌ Leak internal error details to frontend
- ❌ Use synchronous I/O in commands
- ❌ Access global state without synchronization

**Always Do**:
- ✅ Use principle of least privilege
- ✅ Configure strict CSP
- ✅ Validate all IPC inputs
- ✅ Use async for I/O operations
- ✅ Canonicalize and scope file paths
- ✅ Handle errors safely
- ✅ Keep secrets in backend only
- ✅ Use proper synchronization primitives
