## 7. Core Security Patterns

### Pattern 1: Minimal Capability Configuration

```json
// src-tauri/capabilities/default.json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "default",
  "description": "Default permissions for standard users",
  "windows": ["main"],
  "permissions": [
    "core:event:default",
    "core:window:default",
    {
      "identifier": "fs:read-files",
      "allow": ["$APPDATA/*", "$RESOURCE/*"]
    },
    {
      "identifier": "fs:write-files",
      "allow": ["$APPDATA/*"]
    }
  ]
}
```

### Pattern 2: Secure CSP Configuration

```json
// tauri.conf.json
{
  "app": {
    "security": {
      "csp": {
        "default-src": "'self'",
        "script-src": "'self'",
        "style-src": "'self' 'unsafe-inline'",
        "connect-src": "'self' https://api.example.com",
        "object-src": "'none'",
        "frame-ancestors": "'none'"
      },
      "freezePrototype": true
    }
  }
}
```

### Pattern 3: Secure IPC Commands

```rust
use tauri::{command, AppHandle};
use validator::Validate;

#[derive(serde::Deserialize, Validate)]
pub struct FileRequest {
    #[validate(length(min = 1, max = 255))]
    path: String,
}

#[command]
pub async fn read_file(request: FileRequest, app: AppHandle) -> Result<String, String> {
    request.validate().map_err(|e| format!("Validation error: {}", e))?;
    let app_dir = app.path().app_data_dir().map_err(|e| e.to_string())?;
    let canonical = dunce::canonicalize(app_dir.join(&request.path)).map_err(|_| "Invalid path")?;
    if !canonical.starts_with(&app_dir) {
        return Err("Access denied: path traversal detected".into());
    }
    std::fs::read_to_string(canonical).map_err(|e| format!("Failed: {}", e))
}
```

> **For complete IPC patterns, see `references/ipc-patterns.md`**

### Pattern 4: Origin Verification

```rust
#[command]
pub async fn sensitive_operation(window: Window) -> Result<(), String> {
    match window.url().origin() {
        url::Origin::Tuple(scheme, host, _) => {
            if (scheme != "tauri" && scheme != "https") ||
               (host.to_string() != "localhost" && host.to_string() != "tauri.localhost") {
                return Err("Invalid origin".into());
            }
        }
        _ => return Err("Invalid origin".into()),
    }
    Ok(())
}
```

### Pattern 5: Secure Auto-Updater

```rust
pub fn configure_updater(app: &mut tauri::App) -> Result<(), Box<dyn std::error::Error>> {
    let handle = app.handle().clone();
    tauri::async_runtime::spawn(async move {
        let updater = handle.updater_builder()
            .endpoints(vec!["https://releases.example.com/{{target}}/{{current_version}}".into()])
            .pubkey("YOUR_PUBLIC_KEY_HERE")
            .build()?;
        if let Ok(Some(update)) = updater.check().await {
            let _ = update.download_and_install(|_, _| {}, || {}).await;
        }
        Ok::<_, Box<dyn std::error::Error + Send + Sync>>(())
    });
    Ok(())
}
```

> **For advanced patterns, see `references/advanced-patterns.md` and `references/ipc-patterns.md`**

---

