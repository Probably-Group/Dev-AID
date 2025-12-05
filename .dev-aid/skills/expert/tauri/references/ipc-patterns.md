# Tauri IPC Communication Patterns

Comprehensive guide to Inter-Process Communication (IPC) patterns in Tauri, covering secure command design, data serialization, and bidirectional communication.

---

## 1. Basic Command Patterns

### Simple Synchronous Command

```rust
use tauri::command;

#[command]
fn greet(name: String) -> String {
    format!("Hello, {}!", name)
}
```

```typescript
import { invoke } from '@tauri-apps/api/core'

const greeting = await invoke<string>('greet', { name: 'World' })
console.log(greeting) // "Hello, World!"
```

### Async Command with Error Handling

```rust
use tauri::command;

#[command]
async fn fetch_data(id: String) -> Result<Data, String> {
    database::get_by_id(&id)
        .await
        .map_err(|e| format!("Database error: {}", e))
}
```

```typescript
try {
    const data = await invoke<Data>('fetch_data', { id: '123' })
    console.log(data)
} catch (error) {
    console.error('Failed to fetch data:', error)
}
```

---

## 2. Secure IPC Command Pattern

### Complete Secure Command Implementation

```rust
use tauri::{command, AppHandle, State};
use validator::Validate;
use serde::{Deserialize, Serialize};

// 1. Define request with validation
#[derive(Deserialize, Validate)]
pub struct SecureRequest {
    #[validate(length(min = 1, max = 255))]
    #[validate(custom(function = "validate_safe_string"))]
    pub data: String,

    #[validate(range(min = 1, max = 1000))]
    pub limit: u32,
}

fn validate_safe_string(s: &str) -> Result<(), validator::ValidationError> {
    // Prevent dangerous characters
    if s.contains("..") || s.contains("~") || s.contains('\0') {
        return Err(validator::ValidationError::new("unsafe_string"));
    }
    Ok(())
}

// 2. Define response
#[derive(Serialize)]
pub struct SecureResponse {
    pub results: Vec<String>,
    pub count: usize,
}

// 3. Implement command with full validation
#[command]
pub async fn secure_command(
    request: SecureRequest,
    app: AppHandle,
    state: State<'_, AppState>,
) -> Result<SecureResponse, String> {
    // Validate request
    request.validate()
        .map_err(|e| format!("Validation failed: {}", e))?;

    // Perform operation
    let results = process_request(&request, &state).await?;

    Ok(SecureResponse {
        count: results.len(),
        results,
    })
}
```

```typescript
interface SecureRequest {
    data: string
    limit: number
}

interface SecureResponse {
    results: string[]
    count: number
}

async function callSecureCommand(data: string, limit: number): Promise<SecureResponse> {
    // Client-side validation
    if (!data || data.length > 255) {
        throw new Error('Invalid data length')
    }
    if (limit < 1 || limit > 1000) {
        throw new Error('Invalid limit')
    }

    return await invoke<SecureResponse>('secure_command', {
        data,
        limit,
    })
}
```

---

## 3. File Operations Pattern

### Safe File Reading with Path Validation

```rust
use tauri::{command, AppHandle};
use std::path::{Path, PathBuf};
use validator::Validate;

#[derive(serde::Deserialize, Validate)]
pub struct ReadFileRequest {
    #[validate(length(min = 1, max = 255))]
    path: String,
}

#[command]
pub async fn read_file(
    request: ReadFileRequest,
    app: AppHandle,
) -> Result<String, String> {
    // Validate request
    request.validate()
        .map_err(|e| format!("Validation error: {}", e))?;

    // Get app data directory (safe base path)
    let app_dir = app.path().app_data_dir()
        .map_err(|e| e.to_string())?;

    // Join with user-provided path
    let full_path = app_dir.join(&request.path);

    // Canonicalize to resolve symlinks and .. components
    let canonical = dunce::canonicalize(&full_path)
        .map_err(|_| "Invalid path".to_string())?;

    // CRITICAL: Verify path is still within app directory
    if !canonical.starts_with(&app_dir) {
        return Err("Access denied: path traversal detected".into());
    }

    // Check file size before reading
    let metadata = tokio::fs::metadata(&canonical).await
        .map_err(|e| format!("File error: {}", e))?;

    if metadata.len() > 10_000_000 {  // 10MB limit
        return Err("File too large".into());
    }

    // Read file
    tokio::fs::read_to_string(canonical).await
        .map_err(|e| format!("Read error: {}", e))
}
```

### Safe File Writing

```rust
#[derive(serde::Deserialize, Validate)]
pub struct WriteFileRequest {
    #[validate(length(min = 1, max = 255))]
    path: String,

    #[validate(length(max = 10_000_000))]  // 10MB limit
    content: String,
}

#[command]
pub async fn write_file(
    request: WriteFileRequest,
    app: AppHandle,
) -> Result<(), String> {
    request.validate()
        .map_err(|e| format!("Validation error: {}", e))?;

    let app_dir = app.path().app_data_dir()
        .map_err(|e| e.to_string())?;

    let full_path = app_dir.join(&request.path);
    let canonical = dunce::canonicalize(full_path.parent().unwrap())
        .map_err(|_| "Invalid directory".to_string())?
        .join(full_path.file_name().unwrap());

    if !canonical.starts_with(&app_dir) {
        return Err("Access denied: path traversal detected".into());
    }

    // Create parent directories if needed
    if let Some(parent) = canonical.parent() {
        tokio::fs::create_dir_all(parent).await
            .map_err(|e| format!("Failed to create directory: {}", e))?;
    }

    // Write file
    tokio::fs::write(&canonical, request.content).await
        .map_err(|e| format!("Write error: {}", e))
}
```

---

## 4. State Management Pattern

### Shared Application State

```rust
use std::sync::Arc;
use parking_lot::RwLock;
use tauri::{command, State};

// Define application state
#[derive(Default)]
pub struct AppState {
    pub config: Arc<Config>,
    pub cache: Arc<RwLock<HashMap<String, String>>>,
    pub connections: Arc<RwLock<Vec<Connection>>>,
}

// Read from state
#[command]
pub fn get_config(state: State<'_, AppState>) -> Arc<Config> {
    Arc::clone(&state.config)
}

// Write to state
#[command]
pub fn update_cache(
    state: State<'_, AppState>,
    key: String,
    value: String,
) -> Result<(), String> {
    let mut cache = state.cache.write();
    cache.insert(key, value);
    Ok(())
}

// Read from mutable state
#[command]
pub fn get_cache_value(
    state: State<'_, AppState>,
    key: String,
) -> Option<String> {
    let cache = state.cache.read();
    cache.get(&key).cloned()
}

// Register state in main
fn main() {
    tauri::Builder::default()
        .manage(AppState::default())
        .invoke_handler(tauri::generate_handler![
            get_config,
            update_cache,
            get_cache_value
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

---

## 5. Event-Based Communication Pattern

### Backend to Frontend Events

```rust
use tauri::{AppHandle, Manager};
use serde::Serialize;

#[derive(Clone, Serialize)]
struct ProgressPayload {
    current: usize,
    total: usize,
    message: String,
}

#[command]
async fn long_running_task(app: AppHandle) -> Result<(), String> {
    let total = 100;

    for i in 0..=total {
        // Simulate work
        tokio::time::sleep(tokio::time::Duration::from_millis(50)).await;

        // Emit progress event
        app.emit_all("progress", ProgressPayload {
            current: i,
            total,
            message: format!("Processing item {}/{}", i, total),
        }).map_err(|e| e.to_string())?;
    }

    // Emit completion event
    app.emit_all("task-complete", ()).map_err(|e| e.to_string())?;

    Ok(())
}
```

```typescript
import { listen } from '@tauri-apps/api/event'

interface ProgressPayload {
    current: number
    total: number
    message: string
}

// Listen for progress events
const unlisten = await listen<ProgressPayload>('progress', (event) => {
    const { current, total, message } = event.payload
    console.log(`Progress: ${current}/${total} - ${message}`)
    updateProgressBar(current / total)
})

// Listen for completion
await listen('task-complete', () => {
    console.log('Task completed!')
    unlisten() // Clean up listener
})

// Start the task
await invoke('long_running_task')
```

### Frontend to Backend Events

```typescript
import { emit } from '@tauri-apps/api/event'

// Emit event from frontend
await emit('user-action', {
    action: 'button-clicked',
    timestamp: Date.now(),
})
```

```rust
use tauri::{App, Manager};

fn setup_event_listeners(app: &App) {
    let handle = app.handle();

    // Listen to frontend events
    handle.listen_global("user-action", move |event| {
        if let Some(payload) = event.payload() {
            tracing::info!("Received user action: {}", payload);
        }
    });
}

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            setup_event_listeners(app);
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

---

## 6. Stream Pattern for Large Data

### Paginated Data Streaming

```rust
use serde::Serialize;

#[derive(Serialize)]
pub struct DataPage<T> {
    items: Vec<T>,
    cursor: Option<String>,
    has_more: bool,
}

#[command]
pub async fn fetch_page(
    cursor: Option<String>,
    limit: usize,
) -> Result<DataPage<Item>, String> {
    let limit = limit.min(100); // Cap at 100 items per page

    let (items, next_cursor) = database::fetch_page(cursor, limit)
        .await
        .map_err(|e| e.to_string())?;

    Ok(DataPage {
        has_more: items.len() == limit,
        cursor: next_cursor,
        items,
    })
}
```

```typescript
interface DataPage<T> {
    items: T[]
    cursor: string | null
    has_more: boolean
}

async function* streamAllData(): AsyncGenerator<Item[]> {
    let cursor: string | null = null

    do {
        const page = await invoke<DataPage<Item>>('fetch_page', {
            cursor,
            limit: 50,
        })

        yield page.items
        cursor = page.cursor

        if (!page.has_more) break
    } while (cursor !== null)
}

// Usage
for await (const items of streamAllData()) {
    processItems(items)
}
```

---

## 7. Window-Specific Commands Pattern

### Commands with Window Context

```rust
use tauri::{command, Window};

#[command]
pub async fn window_specific_action(
    window: Window,
    data: String,
) -> Result<(), String> {
    let label = window.label();
    tracing::info!("Command called from window: {}", label);

    // Perform action specific to this window
    let result = process_data(&data).await?;

    // Emit event only to this window
    window.emit("action-result", result)
        .map_err(|e| e.to_string())?;

    Ok(())
}

#[command]
pub fn get_window_info(window: Window) -> WindowInfo {
    WindowInfo {
        label: window.label().to_string(),
        url: window.url().to_string(),
        scale_factor: window.scale_factor().unwrap_or(1.0),
    }
}
```

---

## 8. Origin Verification Pattern

### Verify Request Origin

```rust
use tauri::{command, Window};
use url::Url;

#[command]
pub async fn sensitive_operation(window: Window) -> Result<(), String> {
    // Verify origin
    verify_window_origin(&window)?;

    // Perform sensitive operation
    perform_sensitive_action().await
}

fn verify_window_origin(window: &Window) -> Result<(), String> {
    let url = window.url();

    match url.origin() {
        url::Origin::Tuple(scheme, host, port) => {
            // Allow tauri:// protocol
            if scheme == "tauri" {
                return Ok(());
            }

            // Allow localhost in development
            if scheme == "http" || scheme == "https" {
                if host.to_string() == "localhost" || host.to_string() == "127.0.0.1" {
                    return Ok(());
                }
            }

            // Allow specific production domain
            if scheme == "https" && host.to_string() == "app.example.com" {
                return Ok(());
            }

            Err("Invalid origin".into())
        }
        _ => Err("Invalid origin".into()),
    }
}
```

---

## 9. Batch Operations Pattern

### Efficient Batch Processing

```rust
use serde::{Deserialize, Serialize};

#[derive(Deserialize)]
pub struct BatchRequest<T> {
    items: Vec<T>,
}

#[derive(Serialize)]
pub struct BatchResponse<T> {
    results: Vec<Result<T, String>>,
    success_count: usize,
    failure_count: usize,
}

#[command]
pub async fn batch_process(
    request: BatchRequest<Item>,
) -> Result<BatchResponse<ProcessedItem>, String> {
    // Limit batch size
    if request.items.len() > 100 {
        return Err("Batch size exceeds maximum of 100 items".into());
    }

    let mut results = Vec::with_capacity(request.items.len());
    let mut success_count = 0;
    let mut failure_count = 0;

    // Process each item
    for item in request.items {
        match process_item(item).await {
            Ok(result) => {
                results.push(Ok(result));
                success_count += 1;
            }
            Err(e) => {
                results.push(Err(e.to_string()));
                failure_count += 1;
            }
        }
    }

    Ok(BatchResponse {
        results,
        success_count,
        failure_count,
    })
}
```

---

## 10. Request/Response with Timeout Pattern

```rust
use tokio::time::{timeout, Duration};

#[command]
pub async fn fetch_with_timeout(url: String) -> Result<String, String> {
    // Set 30 second timeout
    match timeout(Duration::from_secs(30), fetch_data(url)).await {
        Ok(Ok(data)) => Ok(data),
        Ok(Err(e)) => Err(format!("Fetch error: {}", e)),
        Err(_) => Err("Request timed out".into()),
    }
}
```

```typescript
async function fetchWithClientTimeout(url: string): Promise<string> {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 30000)

    try {
        const result = await invoke<string>('fetch_with_timeout', { url })
        clearTimeout(timeoutId)
        return result
    } catch (error) {
        clearTimeout(timeoutId)
        throw error
    }
}
```

---

## 11. Command Registration Pattern

### Organizing Commands

```rust
// commands/mod.rs
pub mod auth;
pub mod files;
pub mod database;

use tauri::Builder;

pub fn register_commands(builder: Builder) -> Builder {
    builder.invoke_handler(tauri::generate_handler![
        // Auth commands
        auth::login,
        auth::logout,
        auth::verify_session,

        // File commands
        files::read_file,
        files::write_file,
        files::list_directory,

        // Database commands
        database::query,
        database::insert,
        database::update,
    ])
}

// main.rs
fn main() {
    let builder = tauri::Builder::default();
    let builder = commands::register_commands(builder);

    builder
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

---

## 12. Type-Safe IPC with TypeScript

### Generate TypeScript Types from Rust

```rust
// Use ts-rs crate for type generation
use ts_rs::TS;

#[derive(Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/")]
pub struct User {
    pub id: String,
    pub name: String,
    pub email: String,
}

#[derive(Serialize, Deserialize, TS)]
#[ts(export, export_to = "../src/bindings/")]
pub struct LoginRequest {
    pub username: String,
    pub password: String,
}
```

```typescript
// Auto-generated types in src/bindings/User.ts
import { User } from './bindings/User'
import { LoginRequest } from './bindings/LoginRequest'

const request: LoginRequest = {
    username: 'user@example.com',
    password: 'password123',
}

const user = await invoke<User>('login', request)
```

---

## 13. Error Handling Pattern

### Structured Error Responses

```rust
use serde::Serialize;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum CommandError {
    #[error("Invalid input: {0}")]
    Validation(String),

    #[error("Resource not found")]
    NotFound,

    #[error("Permission denied")]
    PermissionDenied,

    #[error("An internal error occurred")]
    Internal(#[from] anyhow::Error),
}

#[derive(Serialize)]
pub struct ErrorResponse {
    error: String,
    code: String,
}

impl From<CommandError> for ErrorResponse {
    fn from(err: CommandError) -> Self {
        let code = match err {
            CommandError::Validation(_) => "VALIDATION_ERROR",
            CommandError::NotFound => "NOT_FOUND",
            CommandError::PermissionDenied => "PERMISSION_DENIED",
            CommandError::Internal(_) => "INTERNAL_ERROR",
        };

        ErrorResponse {
            error: err.to_string(),
            code: code.to_string(),
        }
    }
}
```

```typescript
interface ErrorResponse {
    error: string
    code: string
}

async function handleCommand() {
    try {
        await invoke('my_command', { data: 'test' })
    } catch (error) {
        const err = error as ErrorResponse
        switch (err.code) {
            case 'VALIDATION_ERROR':
                showValidationError(err.error)
                break
            case 'NOT_FOUND':
                showNotFoundError()
                break
            case 'PERMISSION_DENIED':
                showPermissionError()
                break
            default:
                showGenericError()
        }
    }
}
```

---

## IPC Best Practices Summary

1. **Always validate inputs** - Use `validator` crate for declarative validation
2. **Use async for I/O** - Keep commands non-blocking
3. **Verify origins** - Check window origin for sensitive operations
4. **Limit payload sizes** - Cap request/response sizes to prevent memory issues
5. **Use type-safe patterns** - Generate TypeScript types from Rust structs
6. **Handle errors properly** - Return structured errors, log internally
7. **Emit events for progress** - Use events for long-running operations
8. **Scope file paths** - Always verify paths stay within allowed directories
9. **Use state wisely** - Arc/RwLock for shared state
10. **Document commands** - Clear documentation for each IPC command
