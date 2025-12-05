# Tauri Performance Optimization Patterns

This document provides comprehensive performance optimization strategies for Tauri applications.

---

## Pattern 1: Async Commands for Heavy Operations

**Problem**: Blocking operations freeze the UI and degrade user experience.

**Bad Example - Blocking Main Thread**:
```rust
// NEVER: Blocking the main thread
#[command]
fn process_file(path: String) -> Result<String, String> {
    // Blocks UI during file I/O
    std::fs::read_to_string(path).map_err(|e| e.to_string())
}

#[command]
fn heavy_computation(data: Vec<u8>) -> Result<Vec<u8>, String> {
    // Blocks UI during processing
    expensive_operation(data)
}
```

**Good Example - Async with Tokio**:
```rust
// ALWAYS: Use async for I/O operations
#[command]
async fn process_file(path: String) -> Result<String, String> {
    tokio::fs::read_to_string(path)
        .await
        .map_err(|e| e.to_string())
}

// For CPU-intensive work, use spawn_blocking
#[command]
async fn heavy_computation(data: Vec<u8>) -> Result<Vec<u8>, String> {
    tokio::task::spawn_blocking(move || {
        expensive_operation(data)
    })
    .await
    .map_err(|e| e.to_string())?
}
```

**Benefits**:
- Non-blocking UI - application remains responsive
- Better resource utilization
- Enables concurrent operations
- Proper error propagation

---

## Pattern 2: Efficient IPC Serialization

**Problem**: Large data transfers between frontend and backend cause lag.

**Bad Example - Large Nested Structures**:
```rust
#[derive(serde::Serialize)]
struct ComplexObject {
    id: String,
    metadata: HashMap<String, Value>,
    nested_data: Vec<SubObject>,
    binary_data: Vec<u8>,  // Can be megabytes!
    relationships: Vec<Relationship>,
}

// NEVER: Returns megabytes of data in one call
#[command]
fn get_all_data() -> Result<Vec<ComplexObject>, String> {
    // Serializes and transfers huge amount of data
    Ok(database.get_all())  // Could be 10MB+
}
```

**Good Example - Paginated Responses with Minimal Fields**:
```rust
#[derive(serde::Serialize)]
struct MinimalItem {
    id: String,
    title: String,
    preview: String,  // Only essential data
}

#[derive(serde::Serialize)]
struct DataPage {
    items: Vec<MinimalItem>,
    cursor: Option<String>,
    total: usize,
}

// ALWAYS: Return small batches with pagination
#[command]
async fn get_data_page(
    cursor: Option<String>,
    limit: usize,
) -> Result<DataPage, String> {
    let limit = limit.min(100);  // Cap maximum page size
    let items = database
        .get_page(cursor, limit)
        .await?
        .into_iter()
        .map(|item| MinimalItem {
            id: item.id,
            title: item.title,
            preview: item.content[..100].to_string(),
        })
        .collect();

    Ok(DataPage {
        items,
        cursor: calculate_next_cursor(),
        total: database.count().await?,
    })
}

// Separate command for full details when needed
#[command]
async fn get_item_details(id: String) -> Result<ComplexObject, String> {
    database.get_by_id(id).await
}
```

**Benefits**:
- Faster initial page loads
- Reduced memory usage
- Better perceived performance
- Network-friendly for remote webviews

---

## Pattern 3: Resource Cleanup and Lifecycle Management

**Problem**: Resources leak when windows close or operations are cancelled.

**Bad Example - No Cleanup**:
```rust
use std::sync::Arc;
use parking_lot::Mutex;

fn setup_handler(app: &mut App) {
    let active_connections = Arc::new(Mutex::new(Vec::new()));
    let handle = app.handle().clone();

    // Resources accumulate and never get cleaned up
    // Even when windows close or app exits
    tauri::async_runtime::spawn(async move {
        loop {
            let conn = create_connection().await;
            active_connections.lock().push(conn);
            tokio::time::sleep(Duration::from_secs(5)).await;
        }
    });
}
```

**Good Example - Proper Lifecycle Management**:
```rust
use std::sync::Arc;
use parking_lot::Mutex;
use std::collections::HashMap;

#[derive(Default)]
struct WindowResources {
    connections: Vec<Connection>,
    subscriptions: Vec<Subscription>,
    handles: Vec<tokio::task::JoinHandle<()>>,
}

type ResourceMap = Arc<Mutex<HashMap<String, WindowResources>>>;

fn setup_handler(app: &mut App) -> Result<(), Box<dyn std::error::Error>> {
    let resources: ResourceMap = Arc::new(Mutex::new(HashMap::new()));
    let resources_clone = resources.clone();

    // Track resources per window
    app.on_window_event(move |window, event| {
        let label = window.label().to_string();

        match event {
            tauri::WindowEvent::Destroyed => {
                // Cleanup all resources for this window
                if let Some(mut window_resources) = resources_clone.lock().remove(&label) {
                    // Close connections
                    for conn in window_resources.connections.drain(..) {
                        let _ = conn.close();
                    }

                    // Cancel subscriptions
                    for sub in window_resources.subscriptions.drain(..) {
                        sub.unsubscribe();
                    }

                    // Abort background tasks
                    for handle in window_resources.handles.drain(..) {
                        handle.abort();
                    }

                    tracing::info!("Cleaned up resources for window: {}", label);
                }
            }
            _ => {}
        }
    });

    Ok(())
}

// Helper function to register resources
fn register_window_resource<R: tauri::Runtime>(
    app: &AppHandle<R>,
    window_label: &str,
    resource: WindowResources,
) {
    let resources: State<ResourceMap> = app.state();
    resources.lock().insert(window_label.to_string(), resource);
}
```

**Benefits**:
- Prevents memory leaks
- Proper resource cleanup
- Better application stability
- Clean shutdown process

---

## Pattern 4: State Management Optimization

**Problem**: Expensive state cloning on every access impacts performance.

**Bad Example - Expensive Cloning**:
```rust
use tauri::State;

#[derive(Clone)]
struct AppState {
    large_data: Vec<String>,  // Could be thousands of entries
    config: Config,
    cache: HashMap<String, Vec<u8>>,
}

// NEVER: Clones entire state on every call
#[command]
fn get_state(state: State<'_, AppState>) -> AppState {
    state.inner().clone()  // Expensive clone operation!
}

#[command]
fn get_config(state: State<'_, AppState>) -> Config {
    state.inner().config.clone()  // Still cloning entire struct
}
```

**Good Example - Arc for Shared State**:
```rust
use std::sync::Arc;
use parking_lot::RwLock;
use tauri::State;

// Wrap expensive data in Arc
#[derive(Clone)]
struct AppState {
    config: Arc<AppConfig>,          // Cheap to clone
    cache: Arc<RwLock<Cache>>,       // Shared mutable state
    data: Arc<RwLock<Vec<String>>>,  // Shared mutable data
}

// ALWAYS: Use Arc for cheap clones
#[command]
fn get_config(state: State<'_, AppState>) -> Arc<AppConfig> {
    Arc::clone(&state.config)  // Just increments reference count
}

#[command]
fn get_cache_item(state: State<'_, AppState>, key: String) -> Option<Vec<u8>> {
    state.cache.read().get(&key).cloned()  // Only clone the item
}

#[command]
fn update_cache(
    state: State<'_, AppState>,
    key: String,
    value: Vec<u8>,
) -> Result<(), String> {
    state.cache.write().insert(key, value);
    Ok(())
}

// For read-only config, use Arc without RwLock
#[command]
fn get_setting(state: State<'_, AppState>, key: &str) -> Option<String> {
    state.config.get(key).map(|s| s.to_string())
}
```

**Best Practices**:
- Use `Arc<T>` for immutable shared data
- Use `Arc<RwLock<T>>` or `Arc<Mutex<T>>` for mutable shared data
- Prefer `RwLock` over `Mutex` for read-heavy workloads
- Consider `parking_lot` crate for faster locks
- Only clone what you need, not entire state

---

## Pattern 5: Window Management Optimization

**Problem**: Creating new windows for every dialog/modal is expensive.

**Bad Example - Creating Windows Repeatedly**:
```typescript
// Frontend: Creates new window every time
async function showDialog() {
    // Creates DOM, webview, allocates resources every time
    await new WebviewWindow('dialog', {
        url: '/dialog',
        width: 400,
        height: 300,
    })
}

async function showSettings() {
    // Another new window every time
    await new WebviewWindow('settings', {
        url: '/settings',
        width: 600,
        height: 500,
    })
}

// User opens and closes dialog 20 times = 20 window creations!
```

**Good Example - Reuse Existing Windows**:
```typescript
import { WebviewWindow } from '@tauri-apps/api/webviewWindow'

class WindowManager {
    private static instances = new Map<string, WebviewWindow>()

    static async show(
        label: string,
        options?: {
            url: string
            width?: number
            height?: number
            resizable?: boolean
        }
    ): Promise<WebviewWindow> {
        // Try to get existing window
        let window = WebviewWindow.getByLabel(label)

        if (window) {
            // Window exists - just show and focus it
            await window.show()
            await window.setFocus()
            return window
        }

        // Create new window only if needed
        window = new WebviewWindow(label, {
            url: options?.url || `/${label}`,
            width: options?.width || 400,
            height: options?.height || 300,
            resizable: options?.resizable ?? true,
            visible: true,
            center: true,
        })

        this.instances.set(label, window)

        // Clean up on close
        window.once('tauri://close-requested', () => {
            this.instances.delete(label)
        })

        return window
    }

    static async hide(label: string): Promise<void> {
        const window = WebviewWindow.getByLabel(label)
        if (window) {
            await window.hide()
        }
    }

    static async close(label: string): Promise<void> {
        const window = WebviewWindow.getByLabel(label)
        if (window) {
            await window.close()
            this.instances.delete(label)
        }
    }
}

// Usage
async function showDialog() {
    await WindowManager.show('dialog', {
        url: '/dialog',
        width: 400,
        height: 300,
    })
}

async function showSettings() {
    await WindowManager.show('settings', {
        url: '/settings',
        width: 600,
        height: 500,
        resizable: true,
    })
}
```

**Advanced Pattern - Window Pooling**:
```typescript
// For frequently shown/hidden windows, keep them hidden instead of destroying
class DialogPool {
    private static pool = new Map<string, WebviewWindow>()
    private static maxPoolSize = 5

    static async getOrCreate(
        type: 'dialog' | 'confirm' | 'alert',
        options: any
    ): Promise<WebviewWindow> {
        const poolKey = `${type}_pool_${this.pool.size}`

        // Reuse hidden window from pool
        for (const [key, window] of this.pool) {
            if (key.startsWith(type)) {
                await window.show()
                await window.setFocus()
                return window
            }
        }

        // Create new window if pool not full
        if (this.pool.size < this.maxPoolSize) {
            const window = new WebviewWindow(poolKey, options)
            this.pool.set(poolKey, window)
            return window
        }

        // Pool full, create temporary window
        return new WebviewWindow(`${type}_temp`, options)
    }

    static async returnToPool(window: WebviewWindow): Promise<void> {
        await window.hide()
        // Window stays in pool for reuse
    }
}
```

**Benefits**:
- Much faster dialog/modal display
- Reduced memory churn
- Better user experience
- Lower resource usage

---

## Performance Monitoring

### Measuring Command Performance

```rust
use std::time::Instant;

#[command]
async fn monitored_command(data: String) -> Result<String, String> {
    let start = Instant::now();

    let result = expensive_operation(data).await?;

    let duration = start.elapsed();
    if duration.as_millis() > 100 {
        tracing::warn!(
            "Slow command execution: {}ms",
            duration.as_millis()
        );
    }

    Ok(result)
}
```

### Frontend Performance Tracking

```typescript
import { invoke } from '@tauri-apps/api/core'

async function trackedInvoke<T>(
    cmd: string,
    args?: Record<string, unknown>
): Promise<T> {
    const start = performance.now()

    try {
        const result = await invoke<T>(cmd, args)
        const duration = performance.now() - start

        if (duration > 100) {
            console.warn(`Slow IPC call: ${cmd} took ${duration.toFixed(2)}ms`)
        }

        return result
    } catch (error) {
        const duration = performance.now() - start
        console.error(`Failed IPC call: ${cmd} (${duration.toFixed(2)}ms)`, error)
        throw error
    }
}
```

---

## Performance Checklist

Before deploying:
- [ ] Heavy operations use async/await
- [ ] CPU-intensive work uses `spawn_blocking`
- [ ] Large data sets use pagination
- [ ] State management uses Arc/RwLock appropriately
- [ ] Windows are reused when possible
- [ ] Resources cleaned up on window close
- [ ] Performance monitoring in place
- [ ] IPC payloads kept under 100KB per call
- [ ] No synchronous filesystem operations in hot paths
- [ ] Database queries optimized and indexed

---

## Common Performance Issues

**Issue**: UI freezes during heavy operations
**Solution**: Use async commands and spawn_blocking for CPU work

**Issue**: Slow pagination with large datasets
**Solution**: Implement cursor-based pagination, index database queries

**Issue**: High memory usage over time
**Solution**: Implement proper resource cleanup on window events

**Issue**: Slow window switching
**Solution**: Reuse windows instead of creating new ones

**Issue**: Large IPC payloads causing lag
**Solution**: Paginate data, send minimal required fields
