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


### 0.4 Progressive Disclosure (500-Line Limit)

**⚠️ CRITICAL**: This SKILL.md file MUST stay <500 lines for Claude Code to load it.

**If this file is approaching 500 lines**:
- Move detailed examples to `references/advanced-patterns.md`
- Move security examples to `references/security-examples.md`
- Move troubleshooting to `references/troubleshooting.md`
- Keep only summaries and links in main file

📚 **For complete progressive disclosure guide**: See `../../../template-references/progressive-disclosure.md`

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


## 4. Quality Assurance Checklist

**Before implementing this skill, ensure**:

### 4.1 Pre-Implementation Setup
- [ ] Virtual environment created and activated
- [ ] Dependencies installed from requirements.txt
- [ ] Pre-commit hooks installed (`pre-commit install`)
- [ ] Linters installed (black, isort, flake8, mypy, bandit)

### 4.2 Dependency Management
- [ ] All dependencies pinned with exact versions (==)
- [ ] No manual transitive dependency pins
- [ ] Dependencies tested in clean environment

### 4.3 Code Quality Gates (Run BEFORE committing)
- [ ] `black .` - Code formatted
- [ ] `isort .` - Imports sorted
- [ ] `flake8 . --max-line-length=120` - No linting errors
- [ ] `mypy . --ignore-missing-imports` - Type checking passes
- [ ] `bandit -r .` - Security scan clean

### 4.4 Security Validation
- [ ] Input validation for ALL external inputs
- [ ] Path traversal prevention implemented
- [ ] Command injection prevention (no shell=True)
- [ ] SQL injection prevention (parameterized queries)
- [ ] Secrets not in code or error messages

📚 **For complete security validation guide**: See `../../../template-references/security-framework.md`

### 4.5 Test Coverage Requirements
- [ ] Tests written BEFORE implementation (TDD)
- [ ] Unit tests for all public functions
- [ ] Edge case tests (empty, null, max values)
- [ ] Security tests (injection, traversal, overflow)
- [ ] Code coverage >80%

### 4.6 Documentation Requirements
- [ ] Docstrings for all public functions/classes
- [ ] Security considerations documented
- [ ] Examples of correct usage
- [ ] Known limitations documented

---

## 5. Technical Foundation

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

## 6. Implementation Workflow (TDD)

**Rust Backend Test:**
```rust
#[cfg(test)]
mod tests {
    use super::*;

📚 **For complete details**: See `references/implementation-workflow-tdd.md`

---
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
    i## 7. Core Security Patterns

## 7. Core Security Patterns

📚 **For complete details**: See `references/core-security-patterns.md`

---

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

## 9. Pre-Deployment Checklist

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

## 10. References

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
- **`references/testing-guide.md`**: Comprehensive test## 8. Security Standards

## 8. Security Standards

📚 **For complete details**: See `references/security-standards.md`

---
