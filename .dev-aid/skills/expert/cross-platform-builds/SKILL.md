---
name: cross-platform-builds
version: 2.0.0
description: "Cross-platform build systems for Windows, macOS, and Linux desktop applications with code signing, cross-compilation, and distribution packaging. Use when configuring multi-platform CI builds, setting up platform-specific code signing, creating installers (MSI, DMG, AppImage), or managing cross-compile toolchains. Do NOT use for web-only builds or server-side deployments."
risk_level: HIGH
token_budget: 4000
---
# Cross-Platform Builds Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.2 Security Patterns (security rules)

**CWE-494: Missing Code Signing**
- Do not: Distribute unsigned binaries
- Instead: Sign all platforms, verify signatures in installer

**CWE-829: Build Dependency Attacks**
- Do not: Build with unverified tools/compilers
- Instead: Verified toolchains, reproducible builds, SBOM

---

## 1. Security Principles

### 1.1 Code Signing (CWE-494)

**Principle:** Sign all binaries for distribution. Verify signatures during updates.

```rust
// ❌ WRONG - Unsigned binary distribution
fn build() {
    Command::new("cargo")
        .args(["build", "--release"])
        .status()?;
    // No signing!
}

// ✅ CORRECT - Signed with verification
fn build_and_sign() -> Result<()> {
    // Build
    Command::new("cargo")
        .args(["build", "--release", "--target", target])
        .status()?;

    // Sign for macOS
    #[cfg(target_os = "macos")]
    Command::new("codesign")
        .args([
            "--sign", "Developer ID Application: Company",
            "--options", "runtime",
            "--timestamp",
            "--deep",
            &binary_path,
        ])
        .status()?;

    Ok(())
}
```

### 1.2 Notarization (CWE-494)

**Principle:** Notarize macOS apps for Gatekeeper approval.

### 1.3 Dependency Verification (CWE-829)

**Principle:** Verify all dependencies with checksums. Use lockfiles.

### 1.4 Build Isolation (CWE-250)

**Principle:** Build in isolated environments. Use containers or sandboxes.

### 1.5 Secret Handling (CWE-798)

**Principle:** Never embed signing keys in builds. Use CI secrets.

### 1.6 Reproducible Builds (CWE-1357)

**Principle:** Ensure builds are reproducible for verification.

---

## 2. Version Requirements

Use these minimum versions:

```toml
# Rust
[build-dependencies]
tauri-build = "2.0"

# Tauri
[dependencies]
tauri = "2.0"

# Node.js for frontend
node = ">=20.0.0"

# Build tools
cargo = ">=1.75.0"
```

---

## 3. Code Patterns

### 3.1 WHEN configuring Tauri for cross-platform

```json
// ❌ WRONG - Missing platform configs
{
  "build": {
    "beforeBuildCommand": "npm run build"
  }
}

// ✅ CORRECT - tauri.conf.json with full cross-platform config
{
  "$schema": "https://raw.githubusercontent.com/tauri-apps/tauri/v2/packages/api/src/tauri.schema.json",
  "productName": "MyApp",
  "version": "1.0.0",
  "identifier": "com.company.myapp",

  "build": {
    "beforeDevCommand": "npm run dev",
    "beforeBuildCommand": "npm run build",
    "devUrl": "http://localhost:5173",
    "frontendDist": "../dist"
  },

  "bundle": {
    "active": true,
    "targets": "all",
    "icon": [
      "icons/32x32.png",
      "icons/128x128.png",
      "icons/128x128@2x.png",
      "icons/icon.icns",
      "icons/icon.ico"
    ],

    "macOS": {
      "minimumSystemVersion": "10.15",
      "exceptionDomain": null,
      "signingIdentity": null,
      "entitlements": "./entitlements.plist",
      "frameworks": [],
      "providerShortName": null
    },

    "windows": {
      "certificateThumbprint": null,
      "digestAlgorithm": "sha256",
      "timestampUrl": "http://timestamp.digicert.com",
      "wix": {
        "language": ["en-US"]
      },
      "nsis": {
        "installerIcon": "icons/icon.ico",
        "installMode": "currentUser"
      }
    },

    "linux": {
      "appimage": {
        "bundleMediaFramework": true
      },
      "deb": {
        "depends": ["libwebkit2gtk-4.1-0", "libgtk-3-0"]
      },
      "rpm": {
        "requires": ["webkit2gtk4.1", "gtk3"]
      }
    }
  },

  "security": {
    "csp": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'",
    "dangerousDisableAssetCspModification": false,
    "freezePrototype": true,
    "pattern": {
      "use": "isolation"
    }
  },

  "app": {
    "withGlobalTauri": false,
    "windows": [
      {
        "title": "MyApp",
        "width": 1200,
        "height": 800,
        "resizable": true,
        "fullscreen": false,
        "alwaysOnTop": false,
        "decorations": true,
        "transparent": false
      }
    ]
  },

  "plugins": {
    "updater": {
      "active": true,
      "pubkey": "dW50cnVzdGVkIGNvbW1lbnQ6...",
      "endpoints": [
        "https://releases.myapp.com/{{target}}/{{arch}}/{{current_version}}"
      ]
    }
  }
}
```

### 3.2 WHEN setting up GitHub Actions for cross-platform

```yaml
# ✅ CORRECT - Cross-platform build workflow
name: Build

on:
  push:
    tags:
      - 'v*'

permissions:
  contents: write

jobs:
  build:
    strategy:
      fail-fast: false
      matrix:
        include:
          # macOS (Apple Silicon)
          - platform: macos-14
            target: aarch64-apple-darwin
            args: '--target aarch64-apple-darwin'
            artifact: app-macos-arm64

          # macOS (Intel)
          - platform: macos-14
            target: x86_64-apple-darwin
            args: '--target x86_64-apple-darwin'
            artifact: app-macos-x64

          # Linux (x64)
          - platform: ubuntu-22.04
            target: x86_64-unknown-linux-gnu
            args: ''
            artifact: app-linux-x64

          # Linux (ARM64)
          - platform: ubuntu-22.04
            target: aarch64-unknown-linux-gnu
            args: '--target aarch64-unknown-linux-gnu'
            artifact: app-linux-arm64
            cross: true

          # Windows (x64)
          - platform: windows-latest
            target: x86_64-pc-windows-msvc
            args: ''
            artifact: app-windows-x64

    runs-on: ${{ matrix.platform }}

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Rust
        uses: dtolnay/rust-toolchain@stable
        with:
          targets: ${{ matrix.target }}

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install Linux dependencies
        if: matrix.platform == 'ubuntu-22.04'
        run: |
          sudo apt-get update
          sudo apt-get install -y \
            libwebkit2gtk-4.1-dev \
            libappindicator3-dev \
            librsvg2-dev \
            patchelf

      - name: Install cross-compilation tools
        if: matrix.cross
        run: |
          sudo apt-get install -y \
            gcc-aarch64-linux-gnu \
            g++-aarch64-linux-gnu

      - name: Install frontend dependencies
        run: npm ci

      - name: Build frontend
        run: npm run build

      # macOS code signing
      - name: Setup macOS signing
        if: startsWith(matrix.platform, 'macos')
        env:
          APPLE_CERTIFICATE: ${{ secrets.APPLE_CERTIFICATE }}
          APPLE_CERTIFICATE_PASSWORD: ${{ secrets.APPLE_CERTIFICATE_PASSWORD }}
          KEYCHAIN_PASSWORD: ${{ secrets.KEYCHAIN_PASSWORD }}
        run: |
          echo "$APPLE_CERTIFICATE" | base64 --decode > certificate.p12

          security create-keychain -p "$KEYCHAIN_PASSWORD" build.keychain
          security default-keychain -s build.keychain
          security unlock-keychain -p "$KEYCHAIN_PASSWORD" build.keychain
          security set-keychain-settings -lut 7200 build.keychain

          security import certificate.p12 \
            -k build.keychain \
            -P "$APPLE_CERTIFICATE_PASSWORD" \
            -T /usr/bin/codesign \
            -T /usr/bin/security

          security set-key-partition-list -S apple-tool:,apple: \
            -s -k "$KEYCHAIN_PASSWORD" build.keychain

          rm certificate.p12

      # Windows code signing
      - name: Setup Windows signing
        if: matrix.platform == 'windows-latest'
        env:
          WINDOWS_CERTIFICATE: ${{ secrets.WINDOWS_CERTIFICATE }}
        run: |
          echo "$env:WINDOWS_CERTIFICATE" > certificate.b64
          certutil -decode certificate.b64 certificate.pfx
          del certificate.b64

      - name: Build Tauri
        uses: tauri-apps/tauri-action@v0
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          # macOS
          APPLE_SIGNING_IDENTITY: ${{ secrets.APPLE_SIGNING_IDENTITY }}
          APPLE_ID: ${{ secrets.APPLE_ID }}
          APPLE_PASSWORD: ${{ secrets.APPLE_PASSWORD }}
          APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}
          # Windows
          TAURI_SIGNING_PRIVATE_KEY: ${{ secrets.TAURI_SIGNING_PRIVATE_KEY }}
          TAURI_SIGNING_PRIVATE_KEY_PASSWORD: ${{ secrets.TAURI_SIGNING_PRIVATE_KEY_PASSWORD }}
        with:
          tagName: ${{ github.ref_name }}
          releaseName: 'v__VERSION__'
          releaseBody: 'See CHANGELOG.md for details.'
          releaseDraft: true
          prerelease: false
          args: ${{ matrix.args }}

      - name: Cleanup Windows certificate
        if: matrix.platform == 'windows-latest' && always()
        run: del certificate.pfx -ErrorAction SilentlyContinue
```

### 3.3 WHEN implementing platform-specific code

```rust
// ❌ WRONG - No platform handling
fn get_config_path() -> PathBuf {
    PathBuf::from("~/.config/myapp")  // Won't work on Windows!
}

// ✅ CORRECT - Platform-aware paths
use directories::ProjectDirs;
use std::path::PathBuf;

pub fn get_config_dir() -> Result<PathBuf, Error> {
    ProjectDirs::from("com", "company", "myapp")
        .map(|dirs| dirs.config_dir().to_path_buf())
        .ok_or_else(|| Error::NoConfigDir)
}

pub fn get_data_dir() -> Result<PathBuf, Error> {
    ProjectDirs::from("com", "company", "myapp")
        .map(|dirs| dirs.data_dir().to_path_buf())
        .ok_or_else(|| Error::NoDataDir)
}

// Platform-specific behavior
#[cfg(target_os = "macos")]
pub fn setup_app() -> Result<()> {
    // macOS-specific setup
    use cocoa::appkit::NSApplication;
    // ...
    Ok(())
}

#[cfg(target_os = "windows")]
pub fn setup_app() -> Result<()> {
    // Windows-specific setup
    use windows::Win32::UI::Shell::SetCurrentProcessExplicitAppUserModelID;
    unsafe {
        SetCurrentProcessExplicitAppUserModelID(w!("com.company.myapp"))?;
    }
    Ok(())
}

#[cfg(target_os = "linux")]
pub fn setup_app() -> Result<()> {
    // Linux-specific setup
    // Set up D-Bus, etc.
    Ok(())
}
```

### 3.4 WHEN handling file paths cross-platform

```rust
// ❌ WRONG - Hardcoded path separators
let path = format!("data/config/{}.json", name);

// ✅ CORRECT - Use std::path
use std::path::{Path, PathBuf};

pub fn get_config_file(name: &str) -> PathBuf {
    let mut path = get_config_dir().expect("Config dir required");
    path.push(name);
    path.set_extension("json");
    path
}

// Cross-platform path handling
pub fn ensure_parent_exists(path: &Path) -> std::io::Result<()> {
    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    Ok(())
}

// Safe path joining (prevents traversal)
pub fn safe_join(base: &Path, relative: &str) -> Result<PathBuf, Error> {
    let relative = Path::new(relative);

    // Reject absolute paths
    if relative.is_absolute() {
        return Err(Error::InvalidPath("Absolute path not allowed"));
    }

    // Reject path traversal
    for component in relative.components() {
        if matches!(component, std::path::Component::ParentDir) {
            return Err(Error::InvalidPath("Path traversal not allowed"));
        }
    }

    let joined = base.join(relative);
    let canonical = joined.canonicalize()?;

    // Verify result is still under base
    if !canonical.starts_with(base.canonicalize()?) {
        return Err(Error::InvalidPath("Path escaped base directory"));
    }

    Ok(canonical)
}
```

### 3.5 WHEN setting up auto-updates

```rust
// ✅ CORRECT - Tauri updater with signature verification
// Cargo.toml
// [dependencies]
// tauri = { version = "2.0", features = ["updater"] }

// src-tauri/src/main.rs
use tauri::Manager;
use tauri_plugin_updater::UpdaterExt;

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_updater::Builder::new().build())
        .setup(|app| {
            let handle = app.handle().clone();

            tauri::async_runtime::spawn(async move {
                if let Err(e) = check_for_updates(handle).await {
                    eprintln!("Update check failed: {}", e);
                }
            });

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

async fn check_for_updates(app: tauri::AppHandle) -> Result<(), Box<dyn std::error::Error>> {
    let updater = app.updater_builder().build()?;

    if let Some(update) = updater.check().await? {
        println!("Update available: {}", update.version);

        // Download and verify signature
        let mut downloaded = 0;
        update.download_and_install(
            |chunk_length, content_length| {
                downloaded += chunk_length;
                if let Some(total) = content_length {
                    println!("Downloaded {}/{} bytes", downloaded, total);
                }
            },
            || {
                println!("Download complete, restarting...");
            },
        ).await?;
    }

    Ok(())
}
```

### 3.6 WHEN creating entitlements for macOS

```xml
<!-- ✅ CORRECT - entitlements.plist with minimal permissions -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- Required for notarization with hardened runtime -->
    <key>com.apple.security.app-sandbox</key>
    <false/>

    <key>com.apple.security.cs.allow-jit</key>
    <false/>

    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <false/>

    <key>com.apple.security.cs.disable-library-validation</key>
    <false/>

    <!-- Network access -->
    <key>com.apple.security.network.client</key>
    <true/>

    <!-- File access (if needed) -->
    <key>com.apple.security.files.user-selected.read-write</key>
    <true/>

    <!-- Keychain access (if needed) -->
    <key>com.apple.security.keychain-access-groups</key>
    <array>
        <string>$(AppIdentifierPrefix)com.company.myapp</string>
    </array>
</dict>
</plist>
```

---

## 4. Anti-Patterns

Do not:
- Distribute unsigned binaries
- Skip notarization for macOS
- Hardcode path separators (`/` or `\`)
- Use `~` expansion (not cross-platform)
- Embed signing keys in source code
- Skip update signature verification
- Use different versions across platforms
- Ignore platform-specific security features

---

## 5. Testing

**ALWAYS test cross-platform builds:**

```bash
#!/bin/bash
# Test cross-platform build locally

set -euo pipefail

# Test each target
targets=(
# ... (additional test cases follow same pattern)
```

---

## 6. Pre-Generation Checklist

Before generating any cross-platform build code:

- [ ] Code signing configured for all platforms
- [ ] macOS notarization set up
- [ ] Windows certificate configured
- [ ] Update signature verification enabled
- [ ] Platform-specific paths handled correctly
- [ ] Entitlements/capabilities minimized
- [ ] CI builds all target platforms
- [ ] Lockfiles committed for reproducibility
- [ ] Platform-specific dependencies documented
- [ ] Testing covers all target platforms

---
