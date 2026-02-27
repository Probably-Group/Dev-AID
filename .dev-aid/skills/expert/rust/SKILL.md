---
name: rust
version: 2.0.0
description: "Rust systems programming with memory safety, error handling, async Tokio, and FFI patterns. Use when writing Rust code, designing safe abstractions, or implementing async services. Do NOT use for Tauri-specific patterns like IPC or plugins (use tauri)."
compatibility: "Rust 1.70+, cargo"
risk_level: MEDIUM
token_budget: 3500
---
# Rust Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.2 Security Patterns (security rules)

**CWE-119: Unsafe Memory Access**
- Do not: `unsafe {}` without documented justification and safety invariants
- Instead: Prefer safe abstractions, document why unsafe is necessary

**CWE-78: Command Injection**
- Do not: `Command::new("sh").arg("-c").arg(user_string)`
- Instead: `Command::new(binary).args(&validated_args)` - no shell

**CWE-252: Unchecked Return Value**
- Do not: `.unwrap()` in production code or libraries
- Instead: Proper error handling with `?`, `match`, or `unwrap_or_default()`

**CWE-457: Uninitialized Memory**
- Do not: `MaybeUninit` without proper initialization
- Instead: Initialize all memory before use, use safe constructors

**CWE-362: Race Conditions**
- Do not: `static mut` variables
- Instead: Use `Mutex`, `RwLock`, `AtomicT`, or message passing

---

## 1. Security Principles

### 1.1 Data ≠ Code (CWE-78, CWE-94)

**Principle:** Never construct shell commands from untrusted data via string operations.

**NEVER** use shell string construction (CVE-2024-24576 BatBadBut):
```rust
// ❌ WRONG - Command injection via shell
use std::process::Command;

let user_input = get_user_input();
Command::new("sh")
    .arg("-c")
    .arg(format!("echo {}", user_input))  // Injection!
    .output();

// ❌ WRONG - Windows bat file execution (CVE-2024-24576)
Command::new("cmd")
    .args(["/C", &format!("script.bat {}", user_input)])
    .output();

// ✅ CORRECT - Direct execution with argument list
Command::new("echo")
    .arg(&user_input)  // Passed as single argument
    .output();

// ✅ CORRECT - Command allowlist
const ALLOWED_COMMANDS: &[&str] = &["git", "ls", "cat"];

fn safe_command(cmd: &str, args: &[&str]) -> Result<Output, AppError> {
    if !ALLOWED_COMMANDS.contains(&cmd) {
        return Err(AppError::CommandNotAllowed);
    }
    Command::new(cmd).args(args).output().map_err(Into::into)
}
```

### 1.2 Input Validation (CWE-20)

**Principle:** Validate all input at trust boundaries (Tauri commands, FFI, files).

```rust
// ❌ WRONG - No validation at Tauri command boundary
#[tauri::command]
fn process_input(data: String) -> String {
    // data could be anything
    data.to_uppercase()
}

// ✅ CORRECT - Validation with validator crate
use serde::Deserialize;
use validator::Validate;

#[derive(Deserialize, Validate)]
pub struct UserInput {
    #[validate(length(min = 1, max = 100))]
    #[validate(regex(path = "*SAFE_STRING_RE"))]
    pub name: String,

    #[validate(range(min = 0, max = 150))]
    pub age: u8,
}

lazy_static! {
    static ref SAFE_STRING_RE: Regex = Regex::new(r"^[a-zA-Z0-9_-]+$").unwrap();
}

#[tauri::command]
fn process_input(input: UserInput) -> Result<String, String> {
    input.validate().map_err(|e| format!("Invalid input: {}", e))?;
    Ok(input.name.to_uppercase())
}
```

### 1.3 Path Traversal Prevention (CWE-22)

**Principle:** Always canonicalize and verify path containment.

```rust
use std::path::{Path, PathBuf};
use dunce::canonicalize;  // Cross-platform canonicalization

// ❌ WRONG - Path traversal possible
fn read_user_file(base: &Path, filename: &str) -> std::io::Result<String> {
    let path = base.join(filename);  // "../../../etc/passwd" works!
    std::fs::read_to_string(path)
}

// ✅ CORRECT - Canonicalize and verify containment
fn safe_read_file(base: &Path, filename: &str) -> Result<String, AppError> {
    let base = canonicalize(base)?;
    let requested = canonicalize(base.join(filename))?;

    // Verify the resolved path is under base
    if !requested.starts_with(&base) {
        return Err(AppError::PathTraversal);
    }

    std::fs::read_to_string(requested).map_err(Into::into)
}
```

### 1.4 Archive Extraction Safety (CWE-22, CVE-2025-62518)

**Principle:** Never extract archives without path validation.

```rust
// ❌ WRONG - TARmageddon vulnerability
use tar::Archive;

fn extract_archive(path: &Path, dest: &Path) -> std::io::Result<()> {
    let file = std::fs::File::open(path)?;
    let mut archive = Archive::new(file);
    archive.unpack(dest)?;  // Can overwrite arbitrary files!
    Ok(())
}

// ✅ CORRECT - Validate each entry path
fn safe_extract(archive_path: &Path, dest: &Path) -> Result<(), AppError> {
    let dest = dunce::canonicalize(dest)?;
    let file = std::fs::File::open(archive_path)?;
    let mut archive = Archive::new(file);

    for entry in archive.entries()? {
        let mut entry = entry?;
        let path = entry.path()?;

        // Verify no path traversal
        let full_path = dest.join(&path);
        let canonical = dunce::canonicalize(&full_path)?;

        if !canonical.starts_with(&dest) {
            return Err(AppError::PathTraversal);
        }

        entry.unpack(&canonical)?;
    }
    Ok(())
}
```

### 1.5 Unsafe Code Discipline

**Principle:** Minimize unsafe. Always document safety invariants.

```rust
// ❌ WRONG - Unsafe without documentation
unsafe fn process(ptr: *const u8, len: usize) -> &[u8] {
    std::slice::from_raw_parts(ptr, len)
}

// ❌ WRONG - Undefined behavior
unsafe {
    let ptr: *const i32 = std::ptr::null();
    *ptr  // Null pointer dereference!
}

// ✅ CORRECT - Documented safety invariants
/// # Safety
/// - `ptr` must be valid for reads of `len` bytes
/// - `ptr` must be properly aligned
/// - The memory must not be mutated for the lifetime of the returned slice
/// - `len` must not exceed isize::MAX
unsafe fn process(ptr: *const u8, len: usize) -> &[u8] {
    debug_assert!(!ptr.is_null());
    debug_assert!(len <= isize::MAX as usize);
    // SAFETY: Caller guarantees ptr is valid, aligned, and len is correct
    std::slice::from_raw_parts(ptr, len)
}
```

### 1.6 Error Handling - No Unwrap in Production

**Principle:** Never use `.unwrap()` or `.expect()` in production code paths.

```rust
// ❌ WRONG - Panics crash the application
fn get_user(id: i64) -> User {
    db.query_one(&query, &[&id]).unwrap()  // Panics if not found!
}

// ❌ WRONG - expect is still a panic
let config = std::fs::read_to_string("config.json").expect("Config required");

// ✅ CORRECT - Propagate errors with ?
fn get_user(id: i64) -> Result<User, AppError> {
    db.query_one(&query, &[&id]).map_err(|e| match e {
        sqlx::Error::RowNotFound => AppError::NotFound,
        e => AppError::Database(e),
    })
}

// ✅ CORRECT - Custom error types
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("Not found")]
    NotFound,
    #[error("Database error")]
    Database(#[from] sqlx::Error),
    #[error("Path traversal blocked")]
    PathTraversal,
}
```

### 1.7 Secrets ≠ Code (CWE-798)

**Principle:** Never hardcode secrets. Use environment or secure storage.

```rust
// ❌ WRONG - Hardcoded secret
const API_KEY: &str = "sk-1234567890";
const DB_PASSWORD: &str = "supersecret";

// ❌ WRONG - Secrets in error messages
return Err(format!("Failed to connect with key: {}", api_key));

// ✅ CORRECT - From environment
fn get_api_key() -> Result<String, AppError> {
    std::env::var("API_KEY").map_err(|_| AppError::ConfigMissing("API_KEY"))
}

// ✅ CORRECT - OS keychain for desktop apps
use keyring::Entry;

fn get_secret(service: &str, key: &str) -> Result<String, AppError> {
    let entry = Entry::new(service, key)?;
    entry.get_password().map_err(Into::into)
}
```

### 1.8 Serialization Safety (CWE-502)

**Principle:** Use safe serialization formats. Never expose internal details.

```rust
use serde::{Deserialize, Serialize};

// ❌ WRONG - Error exposes internal details
#[derive(Serialize)]
pub enum AppError {
    Database { query: String, error: String },  // Leaks query!
}

// ✅ CORRECT - Safe error serialization
#[derive(Debug)]
pub enum AppError {
    Database(sqlx::Error),
    NotFound,
}

impl Serialize for AppError {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: serde::Serializer,
    {
        // Only expose safe error message, never internals
        serializer.serialize_str(match self {
            AppError::Database(_) => "Database error",
            AppError::NotFound => "Not found",
        })
    }
}
```

---

## 2. Version Requirements

Use these minimum versions:
```toml
[dependencies]
# Core (CVE-2024-24576, CVE-2024-43402 fixes require 1.77.2+)
rust-version = "1.77.2"

# Validation
serde = { version = "1.0", features = ["derive"] }
validator = { version = "0.16", features = ["derive"] }

# Security
ring = "0.17"              # Cryptography
argon2 = "0.5"             # Password hashing
dunce = "1.0"              # Safe path canonicalization

# Error handling
thiserror = "1.0"

[dev-dependencies]
cargo-audit = "0.18"
```

**WHEN generating Cargo.toml** → pin these exact versions or higher.

---

## 3. Code Patterns

### 3.1 WHEN creating Tauri commands

```rust
use serde::Deserialize;
use validator::Validate;
use tauri::State;

#[derive(Deserialize, Validate)]
pub struct CreateUserInput {
    #[validate(length(min = 1, max = 100))]
    name: String,
    #[validate(email)]
    email: String,
}

#[tauri::command]
pub async fn create_user(
    input: CreateUserInput,
    db: State<'_, DbPool>,
) -> Result<User, String> {
    // Validate at boundary
    input.validate().map_err(|e| e.to_string())?;

    // Process with validated input
    let user = db.create_user(&input.name, &input.email)
        .await
        .map_err(|e| "Failed to create user".to_string())?;  // Safe message

    Ok(user)
}
```

### 3.2 WHEN handling Result types

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("Not found")]
    NotFound,
    #[error("Invalid input: {0}")]
    Validation(String),
    #[error("Database error")]
    Database(#[from] sqlx::Error),
    #[error("IO error")]
    Io(#[from] std::io::Error),
}

// Propagate with ?
async fn get_user(db: &DbPool, id: i64) -> Result<User, AppError> {
    let user = sqlx::query_as!(User, "SELECT * FROM users WHERE id = $1", id)
        .fetch_optional(db)
        .await?
        .ok_or(AppError::NotFound)?;
    Ok(user)
}
```

### 3.3 WHEN doing async operations

```rust
use tokio::task::spawn_blocking;

// CPU-bound work: use spawn_blocking
async fn hash_password(password: String) -> Result<String, AppError> {
    spawn_blocking(move || {
        let salt = argon2::password_hash::SaltString::generate(&mut OsRng);
        let hash = Argon2::default()
            .hash_password(password.as_bytes(), &salt)?
            .to_string();
        Ok(hash)
    })
    .await?
}

// IO-bound work: direct async
async fn fetch_data(url: &str) -> Result<String, AppError> {
    let response = reqwest::get(url).await?;
    let body = response.text().await?;
    Ok(body)
}
```

### 3.4 WHEN using generics with constraints

```rust
use std::fmt::Display;

// Generic with trait bounds
fn process<T: Display + Send + Sync>(item: T) -> String {
    format!("Processed: {}", item)
}

// Where clause for complex bounds
fn merge<K, V>(map1: HashMap<K, V>, map2: HashMap<K, V>) -> HashMap<K, V>
where
    K: Eq + Hash + Clone,
    V: Clone,
{
    let mut result = map1;
    result.extend(map2);
    result
}
```

---

## 4. Anti-Patterns

### 4.1 Unwrap in Production

**NEVER** use `.unwrap()` or `.expect()` in production:
```rust
// ❌ WRONG - Application crash
let value = map.get("key").unwrap();

// ✅ CORRECT - Handle the None case
let value = map.get("key").ok_or(AppError::KeyNotFound)?;
```

### 4.2 Shell Command Construction

**NEVER** construct shell commands from user input (CVE-2024-24576):
```rust
// ❌ WRONG - Command injection
Command::new("sh").arg("-c").arg(format!("echo {}", user_input));

// ✅ CORRECT - Direct execution
Command::new("echo").arg(user_input);
```

### 4.3 Unsafe Without Documentation

**NEVER** write unsafe without safety documentation:
```rust
// ❌ WRONG
unsafe { ... }

// ✅ CORRECT
// SAFETY: ptr is valid, aligned, and len is within bounds
unsafe { ... }
```

### 4.4 Panic in Libraries

**NEVER** panic in library code:
```rust
// ❌ WRONG - Forces caller to handle panic
pub fn parse(input: &str) -> Data {
    if input.is_empty() { panic!("Empty input"); }
    ...
}

// ✅ CORRECT - Return Result
pub fn parse(input: &str) -> Result<Data, ParseError> {
    if input.is_empty() { return Err(ParseError::Empty); }
    ...
}
```

---

## 5. Testing

**ALWAYS write tests before implementation:**
```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_path_traversal_blocked() {
        let base = Path::new("/app/data");
# ... (additional test cases follow same pattern)
```

**Test coverage requirements:**
- [ ] Path traversal prevention
- [ ] Command injection prevention
- [ ] Input validation
- [ ] Error handling (no panics)
- [ ] Async operations

---

## 6. Pre-Generation Checklist

Before generating any Rust code:

- [ ] Data ≠ Code: No shell strings, use Command::new().arg()
- [ ] Input validation: validator crate at all boundaries
- [ ] Path safety: canonicalize + containment check
- [ ] Archive extraction: validate each entry path
- [ ] No unwrap: Use Result with ? operator
- [ ] Unsafe documented: SAFETY comments for all unsafe blocks
- [ ] Secrets: From environment or keychain, never hardcoded
- [ ] Error handling: thiserror, no internal details exposed
- [ ] Dependencies audited: cargo audit passes
- [ ] Tests: Security tests for boundaries

---
