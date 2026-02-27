---
name: tauri
version: 2.0.0
description: "Tauri 2.0 desktop app development with Rust backend, IPC patterns, plugin system, and native OS integration. Use when building Tauri apps, configuring IPC commands, or integrating native features. Do NOT use for Electron or web-only applications."
compatibility: "Rust 1.70+, Tauri 2.0+, Node.js 18+"
risk_level: HIGH
token_budget: 3000
---
# Tauri Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.2 Security Patterns (security rules)

**CWE-78: Command Injection via IPC**
- Do not: Execute shell commands with frontend-provided strings
- Instead: Whitelist commands, validate all IPC arguments in Rust

**CWE-22: Path Traversal**
- Do not: `fs::read(frontend_provided_path)` without validation
- Instead: Use `tauri::api::path` scopes, validate paths are within allowed directories

**CWE-79: XSS in WebView**
- Do not: `window.__TAURI__.invoke` results directly into innerHTML
- Instead: Sanitize any data displayed, use CSP headers

**CWE-200: IPC Data Exposure**
- Do not: Send sensitive data (tokens, keys) to frontend
- Instead: Keep secrets in Rust backend, use secure storage APIs

**CWE-306: Missing IPC Authentication**
- Do not: Allow all IPC commands without origin check
- Instead: Use `tauri.conf.json` security settings, validate window origin

---

## 1. Security Principles

### 1.1 Data ≠ Code (CWE-94, CWE-78)

**Principle:** Never construct shell commands from frontend data via string operations.

```rust
// ❌ WRONG - Command injection from frontend
#[tauri::command]
fn run_command(cmd: String) -> Result<String, String> {
    std::process::Command::new("sh")
        .arg("-c")
        .arg(&cmd)  // Frontend controls the command!
        .output()
        .map(|o| String::from_utf8_lossy(&o.stdout).to_string())
        .map_err(|e| e.to_string())
}

// ✅ CORRECT - Allowlist of commands
const ALLOWED_COMMANDS: &[&str] = &["git", "npm", "node"];

#[tauri::command]
fn run_allowed_command(cmd: String, args: Vec<String>) -> Result<String, String> {
    if !ALLOWED_COMMANDS.contains(&cmd.as_str()) {
        return Err("Command not allowed".into());
    }
    std::process::Command::new(&cmd)
        .args(&args)  // Args as list, not shell string
        .output()
        .map(|o| String::from_utf8_lossy(&o.stdout).to_string())
        .map_err(|e| e.to_string())
}
```

### 1.2 Input Validation (CWE-20)

**Principle:** Validate all input at Tauri command boundaries. Frontend is untrusted.

```rust
use serde::Deserialize;
use validator::Validate;

// ❌ WRONG - No validation at IPC boundary
#[tauri::command]
fn save_file(path: String, content: String) -> Result<(), String> {
    std::fs::write(&path, &content).map_err(|e| e.to_string())
}

// ✅ CORRECT - Validate at boundary with typed input
#[derive(Deserialize, Validate)]
pub struct SaveFileInput {
    #[validate(length(min = 1, max = 255))]
    filename: String,  // Just filename, not path
    #[validate(length(max = 10_000_000))]  // 10MB limit
    content: String,
}

#[tauri::command]
fn save_file(
    input: SaveFileInput,
    app: tauri::AppHandle,
) -> Result<(), String> {
    input.validate().map_err(|e| e.to_string())?;

    // Construct safe path within app data directory
    let base = app.path().app_data_dir()
        .map_err(|e| e.to_string())?;
    let path = base.join(&input.filename);

    // Verify path is within base (path traversal prevention)
    let canonical = dunce::canonicalize(&path).map_err(|e| e.to_string())?;
    if !canonical.starts_with(&base) {
        return Err("Invalid path".into());
    }

    std::fs::write(&canonical, &input.content).map_err(|e| e.to_string())
}
```

### 1.3 Path Traversal Prevention (CWE-22)

**Principle:** Always canonicalize paths and verify containment.

```rust
use std::path::{Path, PathBuf};
use dunce::canonicalize;

// ❌ WRONG - Path traversal possible
#[tauri::command]
fn read_user_file(filename: String, app: tauri::AppHandle) -> Result<String, String> {
    let path = app.path().app_data_dir()?.join(&filename);
    std::fs::read_to_string(path).map_err(|e| e.to_string())
}

// ✅ CORRECT - Canonicalize and verify containment
#[tauri::command]
fn read_user_file(filename: String, app: tauri::AppHandle) -> Result<String, String> {
    let base = canonicalize(app.path().app_data_dir()?)
        .map_err(|e| e.to_string())?;

    // Join and canonicalize the full path
    let requested = canonicalize(base.join(&filename))
        .map_err(|_| "File not found")?;

    // Verify the resolved path is under base
    if !requested.starts_with(&base) {
        return Err("Access denied".into());
    }

    std::fs::read_to_string(&requested).map_err(|e| e.to_string())
}
```

### 1.4 Secrets ≠ Code (CWE-798)

**Principle:** Never hardcode secrets. Use OS keychain or environment.

```rust
use keyring::Entry;

// ❌ WRONG - Hardcoded secret
const API_KEY: &str = "sk-1234567890";

// ❌ WRONG - Secret in frontend code
// const API_KEY = "sk-1234567890";  // In JavaScript

// ✅ CORRECT - From OS keychain
#[tauri::command]
fn get_api_key(service: String) -> Result<String, String> {
    let entry = Entry::new(&service, "api_key")
        .map_err(|e| e.to_string())?;
    entry.get_password().map_err(|_| "API key not found".into())
}

// ✅ CORRECT - Store secret in keychain
#[tauri::command]
fn store_api_key(service: String, key: String) -> Result<(), String> {
    let entry = Entry::new(&service, "api_key")
        .map_err(|e| e.to_string())?;
    entry.set_password(&key).map_err(|e| e.to_string())
}
```

### 1.5 Fail Secure (CWE-636)

**Principle:** Default deny. On error, deny access. Never fail open.

### 1.6 Least Privilege (CWE-250)

**Principle:** Minimum Tauri capabilities. Disable unused APIs.

---

## 2. Version Requirements

Use these minimum versions:

```toml
[dependencies]
tauri = { version = "2.0", features = ["protocol-asset"] }
serde = { version = "1.0", features = ["derive"] }
validator = { version = "0.16", features = ["derive"] }
keyring = "2.3"
dunce = "1.0"
thiserror = "1.0"

[build-dependencies]
tauri-build = "2.0"
```

---

## 3. Code Patterns

### 3.1 WHEN creating Tauri commands

```rust
use serde::{Deserialize, Serialize};
use validator::Validate;
use tauri::State;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("Validation error")]
    Validation(#[from] validator::ValidationErrors),
    #[error("Not found")]
    NotFound,
    #[error("Access denied")]
    AccessDenied,
    #[error("Internal error")]
    Internal(String),
}

// Serialize safely - never expose internal details
impl Serialize for AppError {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where S: serde::Serializer {
        serializer.serialize_str(match self {
            AppError::Validation(_) => "Invalid input",
            AppError::NotFound => "Not found",
            AppError::AccessDenied => "Access denied",
            AppError::Internal(_) => "Internal error",
        })
    }
}

#[derive(Deserialize, Validate)]
pub struct CreateItemInput {
    #[validate(length(min = 1, max = 100))]
    name: String,
    #[validate(range(min = 0, max = 1000))]
    quantity: u32,
}

#[tauri::command]
async fn create_item(
    input: CreateItemInput,
    db: State<'_, DbPool>,
) -> Result<Item, AppError> {
    // Validate at boundary
    input.validate()?;

    // Process with validated input
    let item = db.create_item(&input.name, input.quantity).await
        .map_err(|e| {
            log::error!("Database error: {}", e);  // Log internally
            AppError::Internal("Failed to create item".into())  // Generic to user
        })?;

    Ok(item)
}
```

### 3.2 WHEN configuring Tauri capabilities (tauri.conf.json)

```json
{
  "$schema": "https://schema.tauri.app/config/2",
  "productName": "MyApp",
  "version": "1.0.0",
  "identifier": "com.example.myapp",
  "build": {
    "beforeBuildCommand": "npm run build",
    "frontendDist": "../dist"
  },
  "app": {
    "security": {
      "csp": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'",
      "dangerousDisableAssetCspModification": false
    },
    "windows": [
      {
        "title": "MyApp",
        "width": 800,
        "height": 600
      }
    ]
  },
  "plugins": {
    "fs": {
      "scope": ["$APPDATA/*", "$RESOURCE/*"]
    },
    "shell": {
      "open": true,
      "scope": []
    }
  }
}
```

### 3.3 WHEN handling state management

```rust
use std::sync::Mutex;
use tauri::Manager;

pub struct AppState {
    pub db: DbPool,
    pub cache: Mutex<HashMap<String, String>>,
}

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            let db = DbPool::new()?;
            app.manage(AppState {
                db,
                cache: Mutex::new(HashMap::new()),
            });
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            create_item,
            get_item,
        ])
        .run(tauri::generate_context!())
        .expect("error running tauri application");
}

#[tauri::command]
fn get_cached_value(key: String, state: State<'_, AppState>) -> Option<String> {
    let cache = state.cache.lock().unwrap();
    cache.get(&key).cloned()
}
```

### 3.4 WHEN handling file dialogs

```rust
use tauri::api::dialog::FileDialogBuilder;

#[tauri::command]
async fn open_file_dialog(app: tauri::AppHandle) -> Result<Option<String>, String> {
    let file = FileDialogBuilder::new()
        .add_filter("Text Files", &["txt", "md"])
        .add_filter("All Files", &["*"])
        .set_directory(app.path().document_dir()?)
        .pick_file();

    match file {
        Some(path) => {
            // Validate path is within allowed directories
            let content = std::fs::read_to_string(&path)
                .map_err(|e| e.to_string())?;
            Ok(Some(content))
        }
        None => Ok(None),
    }
}
```

---

## 4. Anti-Patterns

Do not:
- Pass shell commands from frontend to backend
- Trust frontend input without validation
- Expose internal error details to frontend
- Use `unwrap()` in command handlers
- Store secrets in localStorage or frontend code
- Disable CSP without explicit security review

---

## 5. Testing

Write security tests:

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_path_traversal_blocked() {
        let attacks = [
# ... (additional test cases follow same pattern)
```

---

## 6. Pre-Generation Checklist

Before generating any Tauri code:

- [ ] Commands validate all input at boundary (validator crate)
- [ ] Paths canonicalized and containment verified (dunce crate)
- [ ] No shell command construction from frontend data
- [ ] Secrets stored in OS keychain, not code
- [ ] Errors serialized without internal details
- [ ] CSP configured restrictively
- [ ] Capabilities minimized in tauri.conf.json
- [ ] No `unwrap()` in command handlers
- [ ] State properly managed with Mutex for shared data
- [ ] Tests cover path traversal and input validation

---
