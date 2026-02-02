---
name: auto-update-systems
version: 2.0.0
description: "Auto-update implementation with signature verification, staged rollouts, and rollback capabilities for desktop apps."
risk_level: CRITICAL
---

# Auto-Update Systems Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-494: Unsigned Updates**
- NEVER: Apply updates without signature verification
- ALWAYS: Cryptographic signature on all update packages

**CWE-295: Improper Certificate Validation**
- NEVER: Skip TLS verification for update downloads
- ALWAYS: Pin certificates or verify chain, use HTTPS only

**CWE-829: Update Server Compromise**
- NEVER: Single point of failure for updates
- ALWAYS: Multiple signature keys, threshold signing, rollback capability

### 0.3 Risk Level: CRITICAL

**Verification requirements for CRITICAL risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 Signature Verification (CWE-347, CWE-494)

**Principle:** Always verify update signatures. Never install unsigned updates.

```rust
// ❌ WRONG - No signature verification
async fn download_and_install(url: &str) -> Result<(), Error> {
    let bytes = reqwest::get(url).await?.bytes().await?;
    std::fs::write("update.exe", bytes)?;
    std::process::Command::new("update.exe").spawn()?;  // Unsigned!
    Ok(())
}

// ✅ CORRECT - Verify Ed25519 signature
use ed25519_dalek::{Verifier, VerifyingKey, Signature};

const PUBLIC_KEY: &str = "...";  // Hardcoded public key is OK

async fn verify_and_install(
    bytes: &[u8],
    signature: &[u8],
) -> Result<(), Error> {
    // Parse public key
    let public_key_bytes = base64::decode(PUBLIC_KEY)?;
    let verifying_key = VerifyingKey::from_bytes(
        &public_key_bytes.try_into()?
    )?;

    // Verify signature
    let signature = Signature::from_bytes(signature.try_into()?);
    verifying_key.verify(bytes, &signature)?;  // Fails if invalid

    // Only install after verification
    install_update(bytes).await
}
```

### 1.2 Secure Transport (CWE-319)

**Principle:** Always use HTTPS. Pin certificates for critical updates.

```rust
// ❌ WRONG - HTTP or no certificate validation
let client = reqwest::Client::builder()
    .danger_accept_invalid_certs(true)  // NEVER DO THIS
    .build()?;

// ✅ CORRECT - HTTPS with certificate pinning
use reqwest::Certificate;

let cert = Certificate::from_pem(include_bytes!("update-server.pem"))?;

let client = reqwest::Client::builder()
    .https_only(true)
    .add_root_certificate(cert)
    .min_tls_version(reqwest::tls::Version::TLS_1_2)
    .build()?;
```

### 1.3 Rollback Capability (CWE-636)

**Principle:** Always support rollback. Never leave users stuck on broken version.

```rust
// ❌ WRONG - No rollback support
fn update(new_binary: &[u8]) -> Result<(), Error> {
    std::fs::write("app.exe", new_binary)?;  // Old version gone!
    Ok(())
}

// ✅ CORRECT - Backup before update
fn update_with_rollback(new_binary: &[u8]) -> Result<(), Error> {
    let app_path = std::env::current_exe()?;
    let backup_path = app_path.with_extension("backup");

    // Create backup
    std::fs::copy(&app_path, &backup_path)?;

    // Install new version
    match install_new_version(new_binary) {
        Ok(_) => {
            // Verify new version works
            if !verify_installation() {
                rollback(&backup_path, &app_path)?;
                return Err(Error::VerificationFailed);
            }
            Ok(())
        }
        Err(e) => {
            rollback(&backup_path, &app_path)?;
            Err(e)
        }
    }
}
```

### 1.4 Version Validation (CWE-20)

**Principle:** Validate version info. Prevent downgrade attacks.

```rust
use semver::Version;

// ❌ WRONG - No version comparison
fn should_update(remote_version: &str) -> bool {
    remote_version != env!("CARGO_PKG_VERSION")  // Allows downgrades!
}

// ✅ CORRECT - Semantic version comparison
fn should_update(remote_version: &str) -> Result<bool, Error> {
    let current = Version::parse(env!("CARGO_PKG_VERSION"))?;
    let remote = Version::parse(remote_version)?;

    // Only allow upgrades, not downgrades
    Ok(remote > current)
}
```

### 1.5 Secrets ≠ Code (CWE-798)

**Principle:** Public keys can be embedded. Private keys never in client code.

### 1.6 Defense in Depth

**Principle:** Multiple checks - signature, TLS, version, checksum.

---

## 2. Version Requirements

**ALWAYS use these minimum versions:**

```toml
[dependencies]
# Tauri
tauri = "2.0"
tauri-plugin-updater = "2.0"

# Cryptography
ed25519-dalek = "2.1"
ring = "0.17"

# HTTP
reqwest = { version = "0.12", features = ["rustls-tls"] }

# Versioning
semver = "1.0"
```

---

## 3. Code Patterns

### 3.1 WHEN configuring Tauri updater

```json
// tauri.conf.json
{
  "plugins": {
    "updater": {
      "active": true,
      "endpoints": [
        "https://releases.myapp.com/{{target}}/{{arch}}/{{current_version}}"
      ],
      "pubkey": "dW50cnVzdGVkIGNvbW1lbnQ6IG1pbmlzaWduIHB1YmxpYyBrZXk...",
      "windows": {
        "installMode": "passive"
      }
    }
  },
  "bundle": {
    "createUpdaterArtifacts": true
  }
}
```

### 3.2 WHEN implementing Tauri update check

```rust
use tauri_plugin_updater::UpdaterExt;
use tauri::Manager;

#[tauri::command]
async fn check_for_update(app: tauri::AppHandle) -> Result<Option<UpdateInfo>, String> {
    let updater = app.updater_builder().build().map_err(|e| e.to_string())?;

    match updater.check().await {
        Ok(Some(update)) => {
            // Log update info (not to user-facing logs)
            log::info!(
                "Update available: {} -> {}",
                update.current_version,
                update.version
            );

            Ok(Some(UpdateInfo {
                version: update.version.clone(),
                notes: update.body.clone(),
                date: update.date.clone(),
            }))
        }
        Ok(None) => Ok(None),
        Err(e) => {
            log::error!("Update check failed: {}", e);
            Err("Failed to check for updates".into())  // Generic error to user
        }
    }
}

#[tauri::command]
async fn install_update(app: tauri::AppHandle) -> Result<(), String> {
    let updater = app.updater_builder().build().map_err(|e| e.to_string())?;

    let update = updater.check().await
        .map_err(|e| e.to_string())?
        .ok_or("No update available")?;

    // Download and verify signature (automatic with Tauri updater)
    update.download_and_install(|progress, total| {
        // Report progress to UI
        let _ = app.emit("update-progress", (progress, total));
    }, || {
        // Restart callback
        log::info!("Update installed, restarting...");
    }).await.map_err(|e| e.to_string())?;

    Ok(())
}
```

### 3.3 WHEN implementing custom update server response

```json
// Update server response format
{
  "version": "2.1.0",
  "notes": "Bug fixes and performance improvements",
  "pub_date": "2024-01-15T12:00:00Z",
  "platforms": {
    "darwin-x86_64": {
      "signature": "dW50cnVzdGVkIGNvbW1lbnQ6IHNpZ25hdHVyZSBmcm9...",
      "url": "https://releases.myapp.com/v2.1.0/myapp-2.1.0-x86_64.dmg"
    },
    "darwin-aarch64": {
      "signature": "...",
      "url": "https://releases.myapp.com/v2.1.0/myapp-2.1.0-aarch64.dmg"
    },
    "windows-x86_64": {
      "signature": "...",
      "url": "https://releases.myapp.com/v2.1.0/myapp-2.1.0-x64-setup.exe"
    },
    "linux-x86_64": {
      "signature": "...",
      "url": "https://releases.myapp.com/v2.1.0/myapp-2.1.0-x86_64.AppImage"
    }
  }
}
```

### 3.4 WHEN implementing staged rollout

```rust
use rand::Rng;
use sha2::{Sha256, Digest};

struct StagedRollout {
    percentage: u8,  // 0-100
    salt: String,
}

impl StagedRollout {
    /// Deterministic rollout based on installation ID
    fn should_update(&self, installation_id: &str) -> bool {
        // Hash installation ID with salt for consistent result
        let mut hasher = Sha256::new();
        hasher.update(installation_id.as_bytes());
        hasher.update(self.salt.as_bytes());
        let hash = hasher.finalize();

        // Use first byte as rollout percentage check
        let value = hash[0] as u8;
        value < (self.percentage as u16 * 255 / 100) as u8
    }
}

// Server-side: include rollout in response
#[derive(Serialize)]
struct UpdateResponse {
    version: String,
    url: String,
    signature: String,
    rollout: Option<StagedRollout>,
}

// Client-side: check rollout before offering update
async fn check_update_with_rollout(
    installation_id: &str,
) -> Result<Option<UpdateInfo>, Error> {
    let response = fetch_update_info().await?;

    if let Some(rollout) = &response.rollout {
        if !rollout.should_update(installation_id) {
            log::info!("Update {} not in rollout group", response.version);
            return Ok(None);
        }
    }

    Ok(Some(response.into()))
}
```

### 3.5 WHEN generating update signing keys

```bash
# Generate Ed25519 key pair for signing updates
# Use tauri CLI for proper format

# Generate keys (run ONCE, store private key securely)
tauri signer generate -w ~/.tauri/myapp.key

# Output:
# Private key: ~/.tauri/myapp.key (KEEP SECRET, use in CI only)
# Public key: dW50cnVzdGVkIGNvbW1lbnQ6... (embed in tauri.conf.json)

# Sign update artifact in CI
export TAURI_SIGNING_PRIVATE_KEY=$(cat ~/.tauri/myapp.key)
tauri build

# Or sign manually
tauri signer sign -k ~/.tauri/myapp.key target/release/bundle/msi/myapp.msi
```

### 3.6 WHEN implementing update in CI/CD

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags: ['v*']

jobs:
  release:
    strategy:
      matrix:
        include:
          - os: macos-latest
            target: aarch64-apple-darwin
          - os: macos-latest
            target: x86_64-apple-darwin
          - os: windows-latest
            target: x86_64-pc-windows-msvc
          - os: ubuntu-latest
            target: x86_64-unknown-linux-gnu

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4

      - name: Build and sign
        env:
          # Private key from GitHub Secrets
          TAURI_SIGNING_PRIVATE_KEY: ${{ secrets.TAURI_SIGNING_PRIVATE_KEY }}
          TAURI_SIGNING_PRIVATE_KEY_PASSWORD: ${{ secrets.TAURI_KEY_PASSWORD }}
        run: |
          npm ci
          npm run tauri build -- --target ${{ matrix.target }}

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: release-${{ matrix.target }}
          path: |
            target/${{ matrix.target }}/release/bundle/**/*.dmg
            target/${{ matrix.target }}/release/bundle/**/*.exe
            target/${{ matrix.target }}/release/bundle/**/*.AppImage
            target/${{ matrix.target }}/release/bundle/**/*.sig
```

---

## 4. Anti-Patterns

**NEVER:**
- Install updates without signature verification
- Use HTTP for update downloads
- Allow downgrade attacks (always compare versions)
- Store private signing keys in client code
- Skip rollback mechanism
- Trust user-provided update URLs
- Expose detailed update errors to users

---

## 5. Testing

**ALWAYS write update security tests:**

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_signature_verification_rejects_invalid() {
        let valid_binary = include_bytes!("../fixtures/valid_update.bin");
        let invalid_sig = &[0u8; 64];

        let result = verify_signature(valid_binary, invalid_sig);
        assert!(result.is_err());
    }

    #[test]
    fn test_signature_verification_accepts_valid() {
        let valid_binary = include_bytes!("../fixtures/valid_update.bin");
        let valid_sig = include_bytes!("../fixtures/valid_update.sig");

        let result = verify_signature(valid_binary, valid_sig);
        assert!(result.is_ok());
    }

    #[test]
    fn test_downgrade_prevention() {
        assert!(!should_update("1.0.0").unwrap());  // Current is 2.0.0
        assert!(should_update("2.1.0").unwrap());
        assert!(should_update("3.0.0").unwrap());
    }

    #[test]
    fn test_staged_rollout_deterministic() {
        let rollout = StagedRollout {
            percentage: 50,
            salt: "test-salt".into(),
        };

        // Same ID should always get same result
        let id = "user-123";
        let result1 = rollout.should_update(id);
        let result2 = rollout.should_update(id);
        assert_eq!(result1, result2);
    }

    #[test]
    fn test_rollback_on_failure() {
        // Simulate update failure and verify rollback works
    }
}
```

---

## 6. Pre-Generation Checklist

**BEFORE generating any auto-update code:**

- [ ] Ed25519 signature verification implemented
- [ ] Public key embedded, private key in CI secrets only
- [ ] HTTPS-only with TLS 1.2+ minimum
- [ ] Semantic version comparison (no downgrades)
- [ ] Rollback mechanism with backup
- [ ] Staged rollout support considered
- [ ] Update errors logged internally, generic to user
- [ ] CI/CD signs artifacts with protected secret
- [ ] Certificate pinning for update server
- [ ] Installation verification after update
