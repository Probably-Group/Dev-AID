---
name: os-keychain
version: 2.0.0
description: "OS keychain integration for secure credential storage on macOS Keychain, Windows Credential Manager, and Linux Secret Service. Use when storing secrets in platform keychains, implementing credential management, or securing sensitive tokens. Do NOT use for application-level secrets via environment variables."
risk_level: HIGH
token_budget: 3500
---
# OS Keychain Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.2 Security Patterns (security rules)

**CWE-522: Weak Credential Storage**
- Do not: Store secrets in plaintext files or environment
- Instead: OS keychain APIs (Keychain, Credential Manager, Secret Service)

**CWE-311: Missing Access Control**
- Do not: Store credentials accessible to all apps
- Instead: Per-app isolation, require user auth for sensitive items

---

## 1. Security Principles

### 1.1 Never Store Secrets in Code (CWE-798)

**Principle:** Use OS keychain for all secrets. Never hardcode.

```rust
// ❌ WRONG - Hardcoded secret
const API_KEY: &str = "sk-1234567890";

// ❌ WRONG - Environment variable in desktop app
let api_key = std::env::var("API_KEY")?;  // Users don't set env vars

// ✅ CORRECT - OS keychain
use keyring::Entry;

fn get_api_key() -> Result<String, keyring::Error> {
    let entry = Entry::new("com.myapp", "api_key")?;
    entry.get_password()
}

fn set_api_key(key: &str) -> Result<(), keyring::Error> {
    let entry = Entry::new("com.myapp", "api_key")?;
    entry.set_password(key)
}
```

### 1.2 Unique Service Identifiers (CWE-522)

**Principle:** Use reverse-domain service names. Never share keychain entries.

```rust
// ❌ WRONG - Generic service name (conflicts with other apps)
let entry = Entry::new("api-key", "default")?;

// ❌ WRONG - User-controlled service name
let entry = Entry::new(&user_input, "key")?;  // Can access other apps!

// ✅ CORRECT - Reverse-domain service identifier
let entry = Entry::new("com.mycompany.myapp", "api_key")?;

// ✅ CORRECT - Separate entries per account
fn get_credential(account: &str) -> Result<Entry, Error> {
    // Validate account format
    if !account.chars().all(|c| c.is_alphanumeric() || c == '_') {
        return Err(Error::InvalidAccount);
    }
    Entry::new("com.mycompany.myapp", account)
}
```

### 1.3 Fail Secure (CWE-636)

**Principle:** Handle keychain errors gracefully. Never fall back to insecure storage.

```rust
// ❌ WRONG - Fallback to plaintext on error
fn get_secret(name: &str) -> String {
    match keyring::Entry::new("myapp", name)?.get_password() {
        Ok(s) => s,
        Err(_) => std::fs::read_to_string("fallback.txt").unwrap(),  // INSECURE!
    }
}

// ✅ CORRECT - Fail if keychain unavailable
fn get_secret(name: &str) -> Result<String, Error> {
    let entry = keyring::Entry::new("com.myapp", name)?;
    entry.get_password().map_err(|e| match e {
        keyring::Error::NoEntry => Error::SecretNotFound(name.to_string()),
        keyring::Error::Ambiguous(_) => Error::AmbiguousEntry,
        _ => Error::KeychainUnavailable,
    })
}
```

### 1.4 Input Validation (CWE-20)

**Principle:** Validate service and key names. Prevent injection.

### 1.5 Least Privilege (CWE-250)

**Principle:** Request minimal keychain access. Don't access other apps' entries.

### 1.6 Defense in Depth

**Principle:** Keychain + memory protection + secure deletion.

---

## 2. Version Requirements

Use these minimum versions:

```toml
# Rust
[dependencies]
keyring = "2.3"
secret-service = "3.0"  # Linux-specific
security-framework = "2.9"  # macOS-specific

# Python
keyring>=24.3.0

# Node.js
keytar>=7.9.0
```

---

## 3. Code Patterns

### 3.1 WHEN implementing cross-platform keychain (Rust)

```rust
use keyring::Entry;
use thiserror::Error;

const SERVICE_NAME: &str = "com.mycompany.myapp";

#[derive(Error, Debug)]
pub enum SecretError {
    #[error("Secret not found")]
    NotFound,
    #[error("Keychain unavailable")]
    KeychainUnavailable,
    #[error("Invalid key name")]
    InvalidKeyName,
    #[error("Keychain error")]
    Keychain(#[from] keyring::Error),
}

pub struct SecretStore;

impl SecretStore {
    /// Get secret from OS keychain
    pub fn get(key: &str) -> Result<String, SecretError> {
        Self::validate_key(key)?;

        let entry = Entry::new(SERVICE_NAME, key)?;
        entry.get_password().map_err(|e| match e {
            keyring::Error::NoEntry => SecretError::NotFound,
            keyring::Error::NoStorageAccess(_) => SecretError::KeychainUnavailable,
            e => SecretError::Keychain(e),
        })
    }

    /// Store secret in OS keychain
    pub fn set(key: &str, value: &str) -> Result<(), SecretError> {
        Self::validate_key(key)?;

        let entry = Entry::new(SERVICE_NAME, key)?;
        entry.set_password(value)?;
        Ok(())
    }

    /// Delete secret from OS keychain
    pub fn delete(key: &str) -> Result<(), SecretError> {
        Self::validate_key(key)?;

        let entry = Entry::new(SERVICE_NAME, key)?;
        entry.delete_credential().map_err(|e| match e {
            keyring::Error::NoEntry => SecretError::NotFound,
            e => SecretError::Keychain(e),
        })
    }

    /// Check if secret exists
    pub fn exists(key: &str) -> Result<bool, SecretError> {
        match Self::get(key) {
            Ok(_) => Ok(true),
            Err(SecretError::NotFound) => Ok(false),
            Err(e) => Err(e),
        }
    }

    fn validate_key(key: &str) -> Result<(), SecretError> {
        if key.is_empty() || key.len() > 255 {
            return Err(SecretError::InvalidKeyName);
        }
        if !key.chars().all(|c| c.is_alphanumeric() || c == '_' || c == '-') {
            return Err(SecretError::InvalidKeyName);
        }
        Ok(())
    }
}
```

### 3.2 WHEN implementing Tauri keychain commands

```rust
use tauri::State;
use serde::{Deserialize, Serialize};

#[derive(Deserialize)]
pub struct SecretInput {
    key: String,
    value: Option<String>,
}

#[derive(Serialize)]
pub struct SecretResult {
    success: bool,
    error: Option<String>,
}

#[tauri::command]
pub fn get_secret(key: String) -> Result<String, String> {
    SecretStore::get(&key).map_err(|e| match e {
        SecretError::NotFound => "Secret not found".to_string(),
        SecretError::KeychainUnavailable => "Keychain unavailable".to_string(),
        _ => "Failed to retrieve secret".to_string(),  // Generic error
    })
}

#[tauri::command]
pub fn set_secret(key: String, value: String) -> Result<(), String> {
    // Don't log the value!
    log::info!("Setting secret for key: {}", key);

    SecretStore::set(&key, &value).map_err(|e| {
        log::error!("Failed to set secret: {:?}", e);
        "Failed to store secret".to_string()
    })
}

#[tauri::command]
pub fn delete_secret(key: String) -> Result<(), String> {
    SecretStore::delete(&key).map_err(|e| match e {
        SecretError::NotFound => "Secret not found".to_string(),
        _ => "Failed to delete secret".to_string(),
    })
}

#[tauri::command]
pub fn has_secret(key: String) -> Result<bool, String> {
    SecretStore::exists(&key).map_err(|_| "Failed to check secret".to_string())
}
```

### 3.3 WHEN implementing keychain in Python

```python
import keyring
from keyring.errors import KeyringError, PasswordDeleteError
from typing import Optional

SERVICE_NAME = "com.mycompany.myapp"

class SecretStore:
    """Cross-platform secret storage using OS keychain."""

    @staticmethod
    def get(key: str) -> Optional[str]:
        """Get secret from keychain. Returns None if not found."""
        if not SecretStore._validate_key(key):
            raise ValueError("Invalid key name")

        try:
            return keyring.get_password(SERVICE_NAME, key)
        except KeyringError as e:
            raise RuntimeError("Keychain unavailable") from e

    @staticmethod
    def set(key: str, value: str) -> None:
        """Store secret in keychain."""
        if not SecretStore._validate_key(key):
            raise ValueError("Invalid key name")

        try:
            keyring.set_password(SERVICE_NAME, key, value)
        except KeyringError as e:
            raise RuntimeError("Failed to store secret") from e

    @staticmethod
    def delete(key: str) -> None:
        """Delete secret from keychain."""
        if not SecretStore._validate_key(key):
            raise ValueError("Invalid key name")

        try:
            keyring.delete_password(SERVICE_NAME, key)
        except PasswordDeleteError:
            pass  # Already deleted
        except KeyringError as e:
            raise RuntimeError("Failed to delete secret") from e

    @staticmethod
    def _validate_key(key: str) -> bool:
        """Validate key name format."""
        if not key or len(key) > 255:
            return False
        return all(c.isalnum() or c in "_-" for c in key)
```

### 3.4 WHEN implementing keychain in Node.js/TypeScript

```typescript
import keytar from 'keytar';

const SERVICE_NAME = 'com.mycompany.myapp';

export class SecretStore {
  private static validateKey(key: string): void {
    if (!key || key.length > 255) {
      throw new Error('Invalid key name');
    }
    if (!/^[a-zA-Z0-9_-]+$/.test(key)) {
      throw new Error('Invalid key name');
    }
  }

  static async get(key: string): Promise<string | null> {
    this.validateKey(key);
    return keytar.getPassword(SERVICE_NAME, key);
  }

  static async set(key: string, value: string): Promise<void> {
    this.validateKey(key);
    await keytar.setPassword(SERVICE_NAME, key, value);
  }

  static async delete(key: string): Promise<boolean> {
    this.validateKey(key);
    return keytar.deletePassword(SERVICE_NAME, key);
  }

  static async has(key: string): Promise<boolean> {
    const value = await this.get(key);
    return value !== null;
  }

  static async getAllKeys(): Promise<string[]> {
    const credentials = await keytar.findCredentials(SERVICE_NAME);
    return credentials.map(c => c.account);
  }
}

// Usage in Electron/Tauri
export async function getApiKey(): Promise<string> {
  const key = await SecretStore.get('api_key');
  if (!key) {
    throw new Error('API key not configured');
  }
  return key;
}
```

### 3.5 WHEN handling first-run setup

```rust
use dialoguer::{Input, Password};

pub async fn setup_credentials() -> Result<(), Error> {
    // Check if already configured
    if SecretStore::exists("api_key")? {
        println!("Credentials already configured.");
        return Ok(());
    }

    // Prompt for credentials (never log these!)
    let api_key: String = Password::new()
        .with_prompt("Enter your API key")
        .interact()?;

    // Validate before storing
    if api_key.len() < 20 {
        return Err(Error::InvalidApiKey);
    }

    // Store in keychain
    SecretStore::set("api_key", &api_key)?;

    // Clear from memory (best effort)
    drop(api_key);

    println!("Credentials stored securely in system keychain.");
    Ok(())
}
```

### 3.6 WHEN migrating from insecure storage

```rust
use std::fs;
use std::path::PathBuf;

pub fn migrate_to_keychain(config_path: &PathBuf) -> Result<(), Error> {
    // Read old config (if exists)
    let old_config = match fs::read_to_string(config_path) {
        Ok(c) => c,
        Err(_) => return Ok(()),  // Nothing to migrate
    };

    // Parse and extract secrets
    let config: OldConfig = toml::from_str(&old_config)?;

    if let Some(api_key) = config.api_key {
        // Store in keychain
        SecretStore::set("api_key", &api_key)?;

        // Remove from config file
        let mut new_config = config.clone();
        new_config.api_key = None;

        // Write sanitized config
        let sanitized = toml::to_string(&new_config)?;
        fs::write(config_path, sanitized)?;

        // Securely delete old file (overwrite)
        let zeros = vec![0u8; old_config.len()];
        fs::write(config_path.with_extension("old"), zeros)?;
        fs::remove_file(config_path.with_extension("old"))?;

        log::info!("Migrated secrets to system keychain");
    }

    Ok(())
}
```

---

## 4. Anti-Patterns

Do not:
- Hardcode secrets in source code
- Store secrets in config files
- Use generic service names (use reverse-domain)
- Log secret values
- Fall back to insecure storage on keychain error
- Allow user input as service name (injection risk)
- Store secrets in environment variables for desktop apps

---

## 5. Testing

**ALWAYS write keychain tests:**

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_set_get_delete() {
        let key = "test_secret";
# ... (additional test cases follow same pattern)
```

---

## 6. Pre-Generation Checklist

Before generating any keychain code:

- [ ] Using reverse-domain service identifier
- [ ] Key names validated (alphanumeric + underscore/hyphen)
- [ ] Secrets never logged or exposed in errors
- [ ] Graceful handling of keychain unavailable
- [ ] No fallback to insecure storage
- [ ] Migration path from old insecure storage
- [ ] Memory cleared after use (best effort)
- [ ] Platform-specific tests included
- [ ] First-run setup flow for credentials
- [ ] Tauri commands return generic errors only

---
