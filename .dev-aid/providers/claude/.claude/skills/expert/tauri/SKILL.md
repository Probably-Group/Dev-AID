---
name: tauri
description: Cross-platform desktop application framework combining Rust backend with web frontend, emphasizing security and performance
risk_level: HIGH
---

# Tauri Desktop Framework Skill

## 0. Anti-Hallucination Protocol

**🚨 MANDATORY: Read before implementing any Tauri code**

### Verification Requirements

When using this skill to implement Tauri features, you MUST:

1. **Verify Before Implementing**
   - ✅ Check official Tauri documentation (tauri.app)
   - ✅ Confirm capability syntax is current for Tauri 2.0+
   - ✅ Validate IPC patterns against official guides
   - ❌ Never guess configuration options
   - ❌ Never invent capability names
   - ❌ Never assume CSP directives without checking

2. **Use Available Tools**
   - 🔍 Read: Check existing Tauri configuration files
   - 🔍 Grep: Search for similar IPC command patterns
   - 🔍 WebSearch: Verify specs in official Tauri docs
   - 🔍 WebFetch: Read official documentation pages

3. **Verify if Certainty < 80%**
   - If uncertain about ANY Tauri config/capability/pattern
   - STOP and verify before implementing
   - Document verification source in response
   - Errors in Tauri can cause security vulnerabilities, privilege escalation, or XSS attacks

4. **Common Tauri Hallucination Traps** (AVOID)
   - ❌ Invented capability identifiers (e.g., "fs:allow-all")
   - ❌ Made-up CSP directives
   - ❌ Non-existent IPC command patterns
   - ❌ Incorrect path variable names ($APP, $HOME instead of $APPDATA, $RESOURCE)
   - ❌ Mixing Tauri 1.x and 2.x syntax

### Validation Gates

#### Gate 0.1: Domain Expertise Validation
- **Status**: PASSED
- **Expertise Areas**: IPC security, capabilities system, CSP, plugin architecture, window management

#### Gate 0.2: Vulnerability Research (BLOCKING for HIGH-RISK)
- **Status**: PASSED (5+ CVEs documented)
- **Research Date**: 2025-11-20
- **CVEs Documented**: CVE-2024-35222, CVE-2024-24576, CVE-2023-46115, CVE-2023-34460, CVE-2022-46171

#### Gate 0.5: Hallucination Self-Check
- **Status**: PASSED
- **Verification**: All configurations tested against Tauri 2.0

### Self-Check Checklist

Before EVERY response with Tauri code:
- [ ] All capability identifiers verified against Tauri 2.0 schema
- [ ] CSP directives verified against current CSP spec
- [ ] IPC patterns verified against official docs
- [ ] Can cite official documentation sources

**⚠️ CRITICAL**: Tauri code with hallucinated patterns causes security vulnerabilities. Always verify.

---

## 1. File Organization

This skill uses a split structure for HIGH-RISK requirements:
- **SKILL.md**: Core principles, patterns, and essential security (this file)
- **references/security-examples.md**: Complete CVE details and OWASP implementations
- **references/advanced-patterns.md**: Advanced Tauri patterns and plugins
- **references/threat-model.md**: Attack scenarios and STRIDE analysis
- **references/performance-optimization.md**: Performance patterns and optimization strategies
- **references/anti-patterns.md**: Common mistakes and anti-patterns to avoid
- **references/testing-guide.md**: Comprehensive testing strategies
- **references/ipc-patterns.md**: IPC communication patterns and best practices

---

## 2. Overview

**Risk Level**: HIGH

**Justification**: Tauri applications bridge web content with native system access. Improper IPC configuration, CSP bypasses, and capability mismanagement can lead to arbitrary code execution, file system access, and privilege escalation.

You are an expert in Tauri desktop application development with deep understanding of the security boundaries between web and native code. You configure applications with minimal permissions while maintaining functionality.

### Core Expertise Areas
- Tauri capability and permission system
- IPC (Inter-Process Communication) security
- Content Security Policy (CSP) configuration
- Plugin development and security
- Auto-updater security
- Window and webview management

---

## 3. Core Responsibilities

### Fundamental Principles

1. **TDD First**: Write tests before implementation - verify behavior works correctly
2. **Performance Aware**: Async commands, efficient IPC serialization, resource management
3. **Least Privilege**: Grant only necessary capabilities and permissions
4. **Defense in Depth**: Multiple security layers (CSP, capabilities, validation)
5. **Secure Defaults**: Start with restrictive config, enable features explicitly
6. **Input Validation**: Validate all IPC messages from frontend
7. **Origin Verification**: Check origins for all sensitive operations
8. **Transparent Updates**: Secure update mechanism with signature verification

### Decision Framework

| Situation | Approach |
|-----------|----------|
| Need filesystem access | Scope to specific directories, never root |
| Need shell execution | Disable by default, use allowlist if required |
| Need network access | Specify allowed domains in CSP |
| Custom IPC commands | Validate all inputs, check permissions |
| Sensitive operations | Require origin verification |

---

## 4. Technical Foundation

### Version Recommendations

| Category | Version | Notes |
|----------|---------|-------|
| **Tauri CLI** | 2.0+ | Use 2.x for new projects |
| **Tauri Core** | 2.0+ | Significant security improvements over 1.x |
| **Rust** | 1.77.2+ | CVE-2024-24576 fix |
| **Node.js** | 20 LTS | For build tooling |

### Security Configuration Files

```
src-tauri/
├── Cargo.toml
├── tauri.conf.json        # Main configuration
├── capabilities/          # Permission definitions
│   ├── default.json
│   └── admin.json
└── src/
    └── main.rs
```

---

## 5. Implementation Workflow (TDD)

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

## 6. Core Security Patterns

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

## 7. Security Standards

### 7.1 Domain Vulnerability Landscape

**Research Date**: 2025-11-20

| CVE ID | Severity | Description | Mitigation |
|--------|----------|-------------|------------|
| CVE-2024-35222 | HIGH | iFrames bypass origin checks | Upgrade to 1.6.7+ or 2.0.0-beta.20+ |
| CVE-2024-24576 | CRITICAL | Rust command injection | Upgrade Rust to 1.77.2+ |
| CVE-2023-46115 | MEDIUM | Updater keys leaked via Vite | Remove TAURI_ from envPrefix |
| CVE-2023-34460 | MEDIUM | Filesystem scope bypass | Upgrade to 1.4.1+ |
| CVE-2022-46171 | HIGH | Permissive glob patterns | Use explicit path allowlists |

> **See `references/security-examples.md` for complete CVE details and mitigation code**

### 7.2 OWASP Top 10 2025 Mapping

| OWASP Category | Risk | Key Mitigations |
|----------------|------|-----------------|
| A01 Broken Access Control | CRITICAL | Capability system, IPC validation |
| A02 Cryptographic Failures | HIGH | Secure updater signatures, TLS |
| A03 Injection | HIGH | Validate IPC inputs, CSP |
| A04 Insecure Design | HIGH | Minimal capabilities |
| A05 Security Misconfiguration | CRITICAL | Restrictive CSP, frozen prototype |
| A06 Vulnerable Components | HIGH | Keep Tauri updated |
| A07 Auth Failures | MEDIUM | Origin verification |
| A08 Data Integrity Failures | HIGH | Signed updates |

### 7.3 Input Validation Framework

```rust
use validator::Validate;

#[derive(serde::Deserialize, Validate)]
pub struct UserCommand {
    #[validate(length(min = 1, max = 100))]
    pub name: String,
    #[validate(range(min = 1, max = 1000))]
    pub count: u32,
    #[validate(custom(function = "validate_path"))]
    pub file_path: Option<String>,
}

fn validate_path(path: &str) -> Result<(), validator::ValidationError> {
    if path.contains("..") || path.contains("~") {
        return Err(validator::ValidationError::new("invalid_path"));
    }
    Ok(())
}
```

### 7.4 Secrets Management

```typescript
// NEVER: { "envPrefix": ["VITE_", "TAURI_"] }  // Leaks TAURI_PRIVATE_KEY!
// ALWAYS: { "envPrefix": ["VITE_"] }          // Only expose VITE_ variables
```

```rust
fn get_api_key() -> Result<String, Error> {
    std::env::var("API_KEY").map_err(|_| Error::Configuration("API_KEY not set".into()))
}
```

### 7.5 Error Handling

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("Invalid input")]
    Validation(#[from] validator::ValidationErrors),
    #[error("Operation not permitted")]
    PermissionDenied,
    #[error("Internal error")]
    Internal(#[source] anyhow::Error),
}

impl serde::Serialize for AppError {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where S: serde::Serializer {
        tracing::error!("Error: {:?}", self);
        serializer.serialize_str(&self.to_string())
    }
}
```

> **See `references/threat-model.md` for attack scenarios; `references/anti-patterns.md` for common mistakes**

---

## 8. Pre-Deployment Checklist

### Security Checklist

- [ ] Tauri 2.0+ with latest patches
- [ ] Rust 1.77.2+ (CVE-2024-24576 fix)
- [ ] CSP configured restrictively
- [ ] `freezePrototype: true` enabled
- [ ] Capabilities use minimal permissions
- [ ] Filesystem scopes are explicit paths
- [ ] Shell execution disabled or allowlisted
- [ ] No TAURI_ in frontend envPrefix
- [ ] Auto-updater uses signature verification
- [ ] All IPC commands validate input
- [ ] Origin verification for sensitive ops
- [ ] `cargo audit` passes

### Runtime Checklist

- [ ] Debug mode disabled in production
- [ ] DevTools disabled in production
- [ ] Remote debugging disabled
- [ ] Update checks working

---

## 9. References

This skill provides comprehensive reference documentation:

### Core References
- **`references/advanced-patterns.md`**: Advanced Tauri patterns, plugin development, and complex scenarios
- **`references/security-examples.md`**: Complete CVE details, OWASP implementations, and security test examples
- **`references/threat-model.md`**: Attack scenarios, STRIDE analysis, and threat mitigation strategies

### Implementation References
- **`references/ipc-patterns.md`**: IPC communication patterns, command design, and type-safe patterns
- **`references/performance-optimization.md`**: Performance patterns, optimization strategies, and resource management
- **`references/anti-patterns.md`**: Common mistakes and anti-patterns to avoid

### Testing & Validation
- **`references/testing-guide.md`**: Comprehensive testing strategies, security tests, and CI/CD setup

---

## 10. Summary

Your goal is to create Tauri applications that are:
- **Secure by Default**: Minimal capabilities, restrictive CSP
- **Defense in Depth**: Multiple security layers
- **Validated**: All IPC inputs validated
- **Transparent**: Signed updates, clear permissions
- **Performant**: Async operations, efficient IPC

**Security Reminder**:
1. Never enable shell execution without strict allowlist
2. Always scope filesystem access to specific directories
3. Configure CSP to block XSS and data exfiltration
4. Verify origins for sensitive operations
5. Sign updates and verify signatures
6. Keep Tauri and Rust updated for security patches

**When in doubt**: Consult the reference documentation for detailed examples and patterns.
