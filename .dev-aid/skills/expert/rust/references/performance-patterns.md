## 8. Performance Patterns

### Pattern 1: Zero-Copy Operations

**Bad**: `data.to_vec()` then iterate - **Good**: Return iterator with lifetime
```rust
// Bad: fn process(data: &[u8]) -> Vec<u8> { data.to_vec().iter().map(|b| b+1).collect() }
fn process(data: &[u8]) -> impl Iterator<Item = u8> + '_ {
    data.iter().map(|b| b + 1)  // No allocation
}
```

### Pattern 2: Iterator Chains Over Loops

**Bad**: Manual loop with push - **Good**: Iterator chain (lazy, fused)
```rust
fn filter_transform(items: &[Item]) -> Vec<String> {
    items.iter().filter(|i| i.is_valid()).map(|i| i.name.to_uppercase()).collect()
}
```

### Pattern 3: Memory Pooling for Frequent Allocations

**Bad**: `Vec::with_capacity()` in hot path - **Good**: Object pool
```rust
static BUFFER_POOL: Lazy<Pool<Vec<u8>>> = Lazy::new(|| Pool::new(32, || Vec::with_capacity(1024)));

async fn handle_request(data: &[u8]) -> Vec<u8> {
    let mut buffer = BUFFER_POOL.pull(|| Vec::with_capacity(1024));
    buffer.clear(); process(&mut buffer, data); buffer.to_vec()
}
```

### Pattern 4: Async Runtime Selection

**Bad**: CPU work on async - **Good**: `spawn_blocking` for CPU-bound
```rust
async fn hash_password(password: String) -> Result<String, AppError> {
    tokio::task::spawn_blocking(move || {
        argon2::hash_encoded(password.as_bytes(), &salt, &config)
            .map_err(|e| AppError::Internal(e.into()))
    }).await?
}
```

### Pattern 5: Avoid Allocations in Hot Paths

**Bad**: `println!` allocates - **Good**: `write!` to preallocated buffer
```rust
fn log_metric(buffer: &mut Vec<u8>, name: &str, value: u64) {
    buffer.clear();
    write!(buffer, "{}: {}", name, value).unwrap();
    std::io::stdout().write_all(buffer).unwrap();
}
```

---

