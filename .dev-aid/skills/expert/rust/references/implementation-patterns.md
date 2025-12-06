## 6. Implementation Patterns

### Pattern 1: Secure Input Validation

Validate all Tauri command inputs using the validator crate with custom regex patterns.

```rust
use serde::Deserialize;
use validator::Validate;

#[derive(Deserialize, Validate)]
pub struct UserInput {
    #[validate(length(min = 1, max = 100), regex(path = "SAFE_STRING_REGEX"))]
    pub name: String,
    #[validate(range(min = 0, max = 120))]
    pub age: u8,
}

#[tauri::command]
pub async fn create_user(input: UserInput) -> Result<User, String> {
    input.validate().map_err(|e| format!("Validation error: {}", e))?;
    Ok(User::new(input))
}
```

> **See `references/advanced-patterns.md` for complete validation patterns with regex definitions**

### Pattern 2: Safe Error Handling

Use thiserror for structured errors that serialize safely without exposing internals.

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("Database error")]
    Database(#[from] sqlx::Error),
    #[error("Validation failed: {0}")]
    Validation(String),
    #[error("Not found")]
    NotFound,
}

impl serde::Serialize for AppError {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where S: serde::Serializer {
        serializer.serialize_str(&self.to_string()) // Never expose internals
    }
}
```

### Pattern 3: Secure File Operations

Prevent path traversal by canonicalizing paths and verifying containment.

```rust
pub fn safe_path_join(base: &Path, user_input: &str) -> Result<PathBuf, AppError> {
    if user_input.contains("..") || user_input.contains("~") {
        return Err(AppError::Validation("Invalid path characters".into()));
    }
    let canonical = dunce::canonicalize(base.join(user_input))
        .map_err(|_| AppError::NotFound)?;
    let base_canonical = dunce::canonicalize(base)
        .map_err(|_| AppError::Internal(anyhow::anyhow!("Invalid base")))?;

    if !canonical.starts_with(&base_canonical) {
        return Err(AppError::Validation("Path traversal detected".into()));
    }
    Ok(canonical)
}
```

### Pattern 4: Safe Command Execution

Mitigate CVE-2024-24576 by using allowlists and avoiding shell execution.

```rust
pub fn safe_command(program: &str, args: &[&str]) -> Result<String, AppError> {
    const ALLOWED: &[&str] = &["git", "cargo", "rustc"];
    if !ALLOWED.contains(&program) {
        return Err(AppError::Validation("Program not allowed".into()));
    }

    let output = Command::new(program).args(args).output()
        .map_err(|e| AppError::Internal(e.into()))?;

    if output.status.success() {
        String::from_utf8(output.stdout).map_err(|e| AppError::Internal(e.into()))
    } else {
        Err(AppError::Internal(anyhow::anyhow!("Command failed")))
    }
}
```

### Pattern 5: Safe Async State Management

Use Arc<RwLock<T>> for thread-safe shared state in Tauri applications.

```rust
pub struct AppState {
    users: Arc<RwLock<HashMap<String, User>>>,
    config: Arc<Config>,
}

impl AppState {
    pub async fn get_user(&self, id: &str) -> Option<User> {
        self.users.read().await.get(id).cloned()
    }

    pub async fn update_user(&self, id: &str, user: User) -> Result<(), AppError> {
        self.users.write().await.insert(id.to_string(), user);
        Ok(())
    }
}
```

> **See `references/advanced-patterns.md` for advanced state patterns and Tauri integration**

---

