# Cross-Platform Build Patterns

This document provides detailed examples of build configurations, CI/CD patterns, and platform-specific setup for cross-platform desktop applications.

---

## 1. Tauri Configuration Examples

### 1.1 Complete Tauri Configuration

```json
// tauri.conf.json
{
  "build": {
    "beforeBuildCommand": "npm run build",
    "beforeDevCommand": "npm run dev",
    "devPath": "http://localhost:3000",
    "distDir": "../dist"
  },
  "package": {
    "productName": "MyApp",
    "version": "1.0.0"
  },
  "tauri": {
    "bundle": {
      "active": true,
      "identifier": "com.company.myapp",
      "icon": [
        "icons/32x32.png",
        "icons/128x128.png",
        "icons/128x128@2x.png",
        "icons/icon.icns",
        "icons/icon.ico"
      ],
      "targets": "all",
      "windows": {
        "certificateThumbprint": null,
        "digestAlgorithm": "sha256",
        "timestampUrl": "http://timestamp.digicert.com",
        "wix": {
          "language": "en-US"
        }
      },
      "macOS": {
        "entitlements": "./entitlements.plist",
        "exceptionDomain": "",
        "frameworks": [],
        "minimumSystemVersion": "10.15",
        "signingIdentity": null
      },
      "linux": {
        "deb": {
          "depends": ["libgtk-3-0", "libwebkit2gtk-4.0-37"]
        },
        "appimage": {
          "bundleMediaFramework": true
        }
      }
    },
    "security": {
      "csp": "default-src 'self'; script-src 'self'"
    }
  }
}
```

### 1.2 Platform-Specific Windows Configuration

```json
{
  "tauri": {
    "bundle": {
      "windows": {
        "certificateThumbprint": "YOUR_CERT_THUMBPRINT",
        "digestAlgorithm": "sha256",
        "timestampUrl": "http://timestamp.digicert.com",
        "wix": {
          "language": "en-US",
          "template": "custom-installer.wxs"
        }
      }
    }
  }
}
```

### 1.3 Platform-Specific macOS Configuration

```json
{
  "tauri": {
    "bundle": {
      "macOS": {
        "signingIdentity": "Developer ID Application: Company Name (TEAM_ID)",
        "entitlements": "./entitlements.plist",
        "minimumSystemVersion": "10.15",
        "frameworks": []
      }
    }
  }
}
```

---

## 2. GitHub Actions Build Matrix

### 2.1 Complete Multi-Platform Build Matrix

```yaml
name: Build

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    strategy:
      fail-fast: false
      matrix:
        include:
          - platform: windows-latest
            args: ''
            target: x86_64-pc-windows-msvc
          - platform: macos-latest
            args: '--target x86_64-apple-darwin'
            target: x86_64-apple-darwin
          - platform: macos-latest
            args: '--target aarch64-apple-darwin'
            target: aarch64-apple-darwin
          - platform: ubuntu-22.04
            args: ''
            target: x86_64-unknown-linux-gnu

    runs-on: ${{ matrix.platform }}

    steps:
      - uses: actions/checkout@v4

      - name: Setup Rust
        uses: dtolnay/rust-toolchain@stable
        with:
          targets: ${{ matrix.target }}

      - name: Install Linux Dependencies
        if: matrix.platform == 'ubuntu-22.04'
        run: |
          sudo apt-get update
          sudo apt-get install -y \
            libgtk-3-dev \
            libwebkit2gtk-4.0-dev \
            libappindicator3-dev \
            librsvg2-dev \
            patchelf

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install Dependencies
        run: npm ci

      - name: Build
        run: npm run tauri build -- ${{ matrix.args }}

      - name: Upload Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: ${{ matrix.target }}
          path: |
            src-tauri/target/${{ matrix.target }}/release/bundle/
```

### 2.2 Advanced Build Matrix with Code Signing

```yaml
name: Build and Sign

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    strategy:
      fail-fast: false
      matrix:
        include:
          - platform: windows-latest
            target: x86_64-pc-windows-msvc
          - platform: macos-latest
            target: x86_64-apple-darwin
          - platform: macos-latest
            target: aarch64-apple-darwin
          - platform: ubuntu-22.04
            target: x86_64-unknown-linux-gnu

    runs-on: ${{ matrix.platform }}

    steps:
      - uses: actions/checkout@v4

      - name: Setup Rust
        uses: dtolnay/rust-toolchain@stable
        with:
          targets: ${{ matrix.target }}

      - name: Install Dependencies (Linux)
        if: matrix.platform == 'ubuntu-22.04'
        run: |
          sudo apt-get update
          sudo apt-get install -y \
            libgtk-3-dev \
            libwebkit2gtk-4.0-dev \
            libappindicator3-dev \
            librsvg2-dev \
            patchelf

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install Frontend Dependencies
        run: npm ci

      - name: Import Windows Certificate
        if: matrix.platform == 'windows-latest'
        run: |
          echo "${{ secrets.WINDOWS_CERTIFICATE }}" | base64 --decode > cert.pfx
          certutil -f -p "${{ secrets.CERTIFICATE_PASSWORD }}" -importpfx cert.pfx
          Remove-Item cert.pfx

      - name: Import macOS Certificate
        if: matrix.platform == 'macos-latest'
        run: |
          echo "${{ secrets.MACOS_CERTIFICATE }}" | base64 --decode > certificate.p12
          security create-keychain -p "${{ secrets.KEYCHAIN_PASSWORD }}" build.keychain
          security default-keychain -s build.keychain
          security unlock-keychain -p "${{ secrets.KEYCHAIN_PASSWORD }}" build.keychain
          security import certificate.p12 -k build.keychain -P "${{ secrets.CERTIFICATE_PASSWORD }}" -T /usr/bin/codesign
          security set-key-partition-list -S apple-tool:,apple:,codesign: -s -k "${{ secrets.KEYCHAIN_PASSWORD }}" build.keychain
          rm certificate.p12

      - name: Build
        run: npm run tauri build -- --target ${{ matrix.target }}
        env:
          TAURI_PRIVATE_KEY: ${{ secrets.TAURI_PRIVATE_KEY }}
          TAURI_KEY_PASSWORD: ${{ secrets.TAURI_KEY_PASSWORD }}

      - name: Notarize (macOS)
        if: matrix.platform == 'macos-latest'
        run: |
          xcrun notarytool submit \
            src-tauri/target/${{ matrix.target }}/release/bundle/dmg/*.dmg \
            --apple-id "${{ secrets.APPLE_ID }}" \
            --password "${{ secrets.APPLE_APP_PASSWORD }}" \
            --team-id "${{ secrets.APPLE_TEAM_ID }}" \
            --wait
          xcrun stapler staple src-tauri/target/${{ matrix.target }}/release/bundle/dmg/*.dmg

      - name: Upload Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: ${{ matrix.target }}
          path: |
            src-tauri/target/${{ matrix.target }}/release/bundle/
```

### 2.3 Caching Strategy for Faster Builds

```yaml
- name: Cache Rust Dependencies
  uses: actions/cache@v4
  with:
    path: |
      ~/.cargo/registry
      ~/.cargo/git
      target
    key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}
    restore-keys: |
      ${{ runner.os }}-cargo-

- name: Cache Node Modules
  uses: actions/cache@v4
  with:
    path: node_modules
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-
```

---

## 3. Platform-Specific Code Patterns

### 3.1 Conditional Compilation in Rust

```rust
// src-tauri/src/main.rs

#[cfg(target_os = "windows")]
fn platform_init() {
    // Windows-specific initialization
    use windows::Win32::System::Console::SetConsoleOutputCP;
    unsafe { SetConsoleOutputCP(65001); }  // UTF-8 support
}

#[cfg(target_os = "macos")]
fn platform_init() {
    // macOS-specific initialization
    use objc::runtime::Object;
    use cocoa::appkit::{NSApp, NSApplication};
    unsafe {
        let app = NSApp();
        app.setActivationPolicy_(NSApplicationActivationPolicyRegular);
    }
}

#[cfg(target_os = "linux")]
fn platform_init() {
    // Linux-specific initialization
    use gtk::prelude::*;
    gtk::init().expect("Failed to initialize GTK");
}

fn main() {
    platform_init();

    tauri::Builder::default()
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

### 3.2 Platform-Specific Path Handling

```rust
use std::path::PathBuf;
use directories::ProjectDirs;

fn get_config_path() -> PathBuf {
    let dirs = ProjectDirs::from("com", "company", "app")
        .expect("Failed to get project directories");

    #[cfg(target_os = "windows")]
    {
        // Windows: %APPDATA%\company\app\config
        dirs.config_dir().join("config.json")
    }

    #[cfg(target_os = "macos")]
    {
        // macOS: ~/Library/Application Support/com.company.app/config
        dirs.config_dir().join("config.json")
    }

    #[cfg(target_os = "linux")]
    {
        // Linux: ~/.config/app/config.json
        dirs.config_dir().join("config.json")
    }
}
```

### 3.3 Universal Binary Creation (macOS)

```bash
#!/bin/bash
# build-universal.sh

# Build for Intel
cargo build --release --target x86_64-apple-darwin

# Build for Apple Silicon
cargo build --release --target aarch64-apple-darwin

# Create universal binary
lipo -create \
  target/x86_64-apple-darwin/release/myapp \
  target/aarch64-apple-darwin/release/myapp \
  -output target/universal/myapp

# Verify
lipo -info target/universal/myapp
# Output: Architectures in the fat file: target/universal/myapp are: x86_64 arm64
```

---

## 4. macOS Entitlements

### 4.1 Standard Entitlements

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.cs.allow-jit</key>
    <true/>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
    <key>com.apple.security.cs.disable-library-validation</key>
    <true/>
</dict>
</plist>
```

### 4.2 Network Access Entitlements

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.cs.allow-jit</key>
    <true/>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
    <key>com.apple.security.network.client</key>
    <true/>
    <key>com.apple.security.network.server</key>
    <true/>
</dict>
</plist>
```

---

## 5. Build Optimization Configurations

### 5.1 Cargo Profile Optimization

```toml
# Cargo.toml

[profile.dev]
incremental = true
opt-level = 0

[profile.release]
incremental = true
lto = "thin"
codegen-units = 1
opt-level = "z"  # Optimize for size
panic = "abort"
strip = true
```

### 5.2 Fast Linker Configuration

```toml
# .cargo/config.toml

[build]
jobs = 8  # Match CPU cores

[target.x86_64-unknown-linux-gnu]
rustflags = ["-C", "link-arg=-fuse-ld=mold"]

[target.x86_64-apple-darwin]
rustflags = ["-C", "link-arg=-fuse-ld=lld"]

[target.x86_64-pc-windows-msvc]
rustflags = ["-C", "link-arg=/INCREMENTAL:NO"]
```

### 5.3 Frontend Build Optimization (Nuxt/Vite)

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  experimental: {
    treeshakeClientOnly: true
  },
  vite: {
    build: {
      rollupOptions: {
        output: {
          manualChunks: {
            'vendor': ['vue', 'pinia'],
            'three': ['three', '@tresjs/core']
          }
        }
      },
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: true,
          drop_debugger: true
        }
      }
    }
  }
})
```

---

## 6. Build Verification Scripts

### 6.1 Cross-Platform Build Verification

```bash
#!/bin/bash
# verify-builds.sh

set -e

echo "Verifying cross-platform builds..."

# Windows
if [ -f "target/x86_64-pc-windows-msvc/release/myapp.exe" ]; then
    echo "✅ Windows x64 build exists"
else
    echo "❌ Windows x64 build missing"
    exit 1
fi

# macOS Intel
if [ -f "target/x86_64-apple-darwin/release/myapp" ]; then
    echo "✅ macOS Intel build exists"
else
    echo "❌ macOS Intel build missing"
    exit 1
fi

# macOS Apple Silicon
if [ -f "target/aarch64-apple-darwin/release/myapp" ]; then
    echo "✅ macOS Apple Silicon build exists"
else
    echo "❌ macOS Apple Silicon build missing"
    exit 1
fi

# Linux
if [ -f "target/x86_64-unknown-linux-gnu/release/myapp" ]; then
    echo "✅ Linux x64 build exists"
else
    echo "❌ Linux x64 build missing"
    exit 1
fi

echo "All builds verified successfully!"
```

### 6.2 Bundle Size Analysis

```bash
#!/bin/bash
# analyze-bundles.sh

echo "Analyzing bundle sizes..."

# Rust binary
cargo bloat --release --crates | head -20

# Frontend bundle
npx nuxi analyze

# Total bundle size
du -h src-tauri/target/release/bundle/
```

---

## 7. Platform Build Targets Reference

| Platform | Rust Target | Tauri Bundle | Notes |
|----------|-------------|--------------|-------|
| Windows x64 | x86_64-pc-windows-msvc | msi, nsis | Requires Visual Studio Build Tools |
| Windows ARM | aarch64-pc-windows-msvc | msi, nsis | Limited testing on ARM hardware |
| macOS Intel | x86_64-apple-darwin | dmg, app | Requires Xcode Command Line Tools |
| macOS Apple Silicon | aarch64-apple-darwin | dmg, app | Native ARM performance |
| Linux x64 | x86_64-unknown-linux-gnu | deb, appimage | Requires GTK3 dependencies |
| Linux ARM | aarch64-unknown-linux-gnu | deb, appimage | Raspberry Pi 4+ compatible |

---

## 8. Quick Reference Commands

```bash
# Build for current platform
npm run tauri build

# Build for specific target
npm run tauri build -- --target x86_64-pc-windows-msvc

# Build with debug symbols
npm run tauri build -- --debug

# Build all targets (requires setup)
./scripts/build-all.sh

# Verify build
./scripts/verify-builds.sh

# Analyze bundle size
cargo bloat --release --crates
npx nuxi analyze
```
