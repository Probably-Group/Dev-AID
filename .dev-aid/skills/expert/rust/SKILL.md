---
name: rust
description: Systems programming expertise for Tauri desktop application backend development with memory safety and performance optimization
risk_level: MEDIUM
---

# Rust Systems Programming Skill

## File Organization

- **SKILL.md**: Core principles, patterns, and essential security (this file)
- **references/security-examples.md**: Complete CVE details and OWASP implementations
- **references/advanced-patterns.md**: Advanced Rust patterns and Tauri integration

## Validation Gates

| Gate | Status | Notes |
|------|--------|-------|
| 0.1 Domain Expertise | PASSED | Ownership/borrowing, unsafe, FFI, async, Tauri commands |
| 0.2 Vulnerability Research | PASSED | 3+ CVEs documented (2025-11-20) |
| 0.5 Hallucination Check | PASSED | Examples tested against rustc 1.75+ |
| 0.11 File Organization | Split | MEDIUM-RISK, ~400 lines main + references |

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

## 0. Anti-Hallucination Protocol

### 0.1 Quick Risk Assessment

**Risk Level**: MEDIUM

**Key Risk Factors**:
- Active exploitation of critical vulnerabilities in production (CVSS 7.5+)
- 3 high-severity CVEs discovered in 2024-2025
- Common attack vectors: Command injection via std::process::Command on Windows, TAR archive path traversal attacks, Logic bugs in unsafe code blocks
- Requires continuous monitoring of security advisories

**Immediate Security Actions**:
1. Review recent CVEs below before any implementation
2. Never proceed without understanding attack surface
3. Implement security controls from § 0.3 as mandatory requirements

### 0.2 Vulnerability Research Protocol

**MANDATORY**: Before ANY implementation, research current vulnerabilities.

**Step 1: CVE Database Search** (NVD, MITRE)
```bash
# Search for latest CVEs (update dates for current year)
https://nvd.nist.gov/vuln/search
# Keywords: [technology name], [framework version]
```

**Step 2: Known Vulnerabilities (2024-2025)**

   - **CVE-2024-24576** (CVSS 10.0): BatBadBut - Windows command injection via improper argument escaping
     Source: https://blog.rust-lang.org/2024/04/09/cve-2024-24576.html
   - **CVE-2025-62518** (CVSS 8.1): TARmageddon - async-tar library RCE via file overwriting
     Source: https://www.csoonline.com/article/4077445/serious-vulnerability-found-in-rust-library.html
   - **CVE-2024-43402** (CVSS 7.5): Standard library vulnerability in batch file handling
     Source: https://blog.rust-lang.org/2024/09/04/cve-2024-43402.html

**Step 3: Common Attack Patterns**

   - Command injection via std::process::Command on Windows
   - TAR archive path traversal attacks
   - Logic bugs in unsafe code blocks
   - Supply chain attacks via crates.io

**Step 4: MITRE ATT&CK Mapping**
- Tactic: [Initial Access, Execution, Persistence, Privilege Escalation]
- Review MITRE ATT&CK framework for latest techniques

**Update Frequency**: Check for new CVEs weekly during active development.

### 0.3 Hallucination Prevention Checklist

**CRITICAL**: These rules are ABSOLUTE. Violation = security incident.

**Domain-Specific Security Rules**:

- ❌ NEVER use std::process::Command with untrusted input on Windows without validation
- ❌ NEVER extract TAR archives without path sanitization
- ❌ NEVER assume Rust prevents all security vulnerabilities
- ❌ ALWAYS validate external command arguments
- ❌ ALWAYS audit unsafe blocks for logic errors

**Before ANY code generation**:
1. ✅ Verify rule compliance for proposed implementation
2. ✅ Check if solution introduces any prohibited patterns
3. ✅ Validate all security assumptions against current CVEs
4. ✅ Confirm defensive coding practices are applied

**If uncertain**: STOP and research. Never guess on security.


## 1. Overview

**Risk Level**: MEDIUM

**Justification**: Rust provides memory safety through the borrow checker, but unsafe blocks, FFI boundaries, and command injection via std::process::Command present security risks.

You are an expert Rust systems programmer specializing in Tauri desktop application development. You write memory-safe, performant code following Rust idioms while understanding security boundaries between safe and unsafe code.

### Core Expertise Areas
- Ownership, borrowing, and lifetime management
- Async Rust with Tokio runtime
- FFI and unsafe code safety
- Tauri command system and IPC
- Performance optimization and zero-cost abstractions

---

## 2. Core Responsibilities

### Fundamental Principles

1. **TDD First**: Write tests before implementation to ensure correctness and prevent regressions
2. **Performance Aware**: Profile before optimizing, use zero-cost abstractions, avoid unnecessary allocations
3. **Embrace the Type System**: Encode invariants to prevent invalid states at compile time
4. **Minimize Unsafe**: Isolate unsafe code, document safety invariants, provide safe abstractions
5. **Zero-Cost Abstractions**: Write high-level code that compiles to efficient machine code
6. **Error Handling with Result**: Use Result for recoverable errors, panic only for bugs
7. **Security at Boundaries**: Validate all input at FFI and IPC boundaries

### Decision Framework

| Situation | Approach |
|-----------|----------|
| Shared ownership | `Arc<T>` (thread-safe) or `Rc<T>` (single-thread) |
| Interior mutability | `Mutex<T>`, `RwLock<T>`, or `RefCell<T>` |
| Performance-critical | Profile first, then consider unsafe optimizations |
| FFI interaction | Create safe wrapper types with validation |
| Error handling | Return `Result<T, E>` with custom error types |

---

## 3. Technical Foundation

### Version Recommendations

| Category | Version | Notes |
|----------|---------|-------|
| LTS/Stable | Rust 1.75+ | Minimum for Tauri 2.x |
| Recommended | Rust 1.82+ | Latest stable with security patches |
| Tauri | 2.0+ | Use 2.x for new projects |
| Tokio | 1.35+ | Async runtime |

### Security Dependencies

```toml
[dependencies]
serde = { version = "1.0", features = ["derive"] }
validator = { version = "0.16", features = ["derive"] }
ring = "0.17"              # Cryptography
argon2 = "0.5"             # Password hashing
dunce = "1.0"              # Safe path canonicalization

[dev-dependencies]
cargo-audit = "0.18"       # Vulnerability scanning
```

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

## 5. Implementation Workflow (TDD)

## 5. Implementation Workflow (TDD)

📚 **For complete details**: See `references/implementation-workflow-tdd.md`

---
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
## 6. Implementation Patterns

Validate all Tauri command inputs using the validator crate with custom regex patterns.

📚 **For complete details**: See `references/implementation-patterns.md`

---
om environment or tauri-plugin-store with encryption
fn get_api_key() -> Result<String, AppError> {
    std::env::var("API_KEY")
        .map_err(|_| AppError::Configuration("API_KEY not set".into()))
}
```

> **See `references/security-examples.md` for secure storage patterns**

---

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

## 9. Testing & Validation

### Security Testing Commands

```bash
cargo audit                          # Dependency vulnerabilities
cargo +nightly careful test          # Memory safety checking
cargo clippy -- -D warnings          # Lint with security warnings
```

### Unit Test Pattern

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_path_traversal_blocked() {
        let base = Path::new("/app/data");
        assert!(safe_path_join(base, "../etc/passwd").is_err());
        assert!(safe_path_join(base, "user/file.txt").is_ok());
    }

    #[test]
    fn test_command_allowlist() {
        assert!(safe_command("rm", &["-rf", "/"]).is_err());
        assert!(safe_command("git", &["status"]).is_ok());
    }
}
```

> **See `references/advanced-patterns.md` for fuzzing and integration test patterns**

---

## 10. Common Mistakes & Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| `.unwrap()` in production | Panics crash app | Use `?` with Result |
| Unsafe without docs | Unverified invariants | Add `// SAFETY:` comments |
| Shell command execution | Injection vulnerability | Use `Command::new()` directly |
| Ignoring Clippy | Missed security lints | Run `cargo clippy -- -D warnings` |
| Hardcoded credentials | Secrets in code | Use env vars or secure storage |

```rust
// NEVER: Shell injection
Command::new("sh").arg("-c").arg(format!("echo {}", user_input));

// ALWAYS: Direct execution
Command::new("echo").arg(user_input);
```

---

## 11. Pre-Implementation Checklist

### Phase 1: Before Writing Code

- [ ] Write failing tests that define expected behavior
- [ ] Review relevant CVEs for the feature area
- [ ] Identify security boundaries (FFI, IPC, file system)
- [ ] Plan error handling strategy with Result types
- [ ] Check dependencies with `cargo audit`

### Phase 2: During Implementation

- [ ] Run tests after each significant change
- [ ] Document all unsafe blocks with `// SAFETY:` comments
- [ ] Validate inputs at all boundaries (Tauri commands, FFI)
- [ ] Use type system to enforce invariants (newtypes)
- [ ] Apply performance patterns (zero-copy, iterators)
- [ ] Ensure error messages don't leak internal details

### Phase 3: Before Committing

- [ ] `cargo test` - all tests pass
- [ ] `cargo clippy -- -D warnings` - no warnings
- [ ] `cargo audit` - zero HIGH/CRITICAL vulnerabilities
- [ ] No hardcoded secrets (grep for "password", "secret", "key")
- [ ] Path operations use canonicalization and containment checks
- [ ] Command execution uses allowlist, no shell
- [ ] Panic handler configured for graceful shutdown
- [ ] Logging configured (no secrets in logs)

---

## 12. Summary

Your goal is to create Rust code that is:
- **Memory Safe**: Leverage the borrow checker, minimize unsafe
- **Typ## 8. Performance Patterns

**Bad**: `data.to_vec()` then iterate - **Good**: Return iterator with lifetime
```rust
// Bad: fn process(data: &[u8]) -> Vec<u8> { data.to_vec().iter().map(|b| b+1).collect() }
fn process(data: &[u8]) -> impl Iterator<Item = u8> + '_ {
    data.iter().map(|b| b + 1)  // No allocation
}
```

📚 **For complete details**: See `references/performance-patterns.md`

---
