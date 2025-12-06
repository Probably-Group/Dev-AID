## 8. Security Standards

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

