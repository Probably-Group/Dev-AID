## 6. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

**Rust Backend Test:**
```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_file_read_validates_path() {
        let request = FileRequest { path: "../secret".to_string() };
        assert!(request.validate().is_err(), "Should reject path traversal");
    }

    #[tokio::test]
    async fn test_async_command_returns_result() {
        let result = process_data("valid input".to_string()).await;
        assert!(result.is_ok());
    }
}
```

**Frontend Vitest Test:**
```typescript
import { describe, it, expect, vi } from 'vitest'
import { invoke } from '@tauri-apps/api/core'

vi.mock('@tauri-apps/api/core')

describe('Tauri IPC', () => {
  it('invokes read_file command correctly', async () => {
    vi.mocked(invoke).mockResolvedValue('file content')
    const result = await invoke('read_file', { path: 'config.json' })
    expect(result).toBe('file content')
  })
})
```

### Step 2: Implement Minimum to Pass

Write only the code necessary to make the test pass:
```rust
#[command]
pub async fn process_data(input: String) -> Result<String, String> {
    // Minimum implementation to pass test
    Ok(format!("Processed: {}", input))
}
```

### Step 3: Refactor if Needed

After tests pass, improve code structure without changing behavior:
- Extract common validation logic
- Improve error messages
- Add documentation

### Step 4: Run Full Verification

```bash
# Rust tests and linting
cd src-tauri && cargo test
cd src-tauri && cargo clippy -- -D warnings
cd src-tauri && cargo audit

# Frontend tests
npm test
npm run typecheck
```

> **For comprehensive testing strategies, see `references/testing-guide.md`**

---

