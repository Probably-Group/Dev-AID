# Cross-Platform Build Anti-Patterns and Common Mistakes

This document catalogs common mistakes, anti-patterns, and pitfalls to avoid when building cross-platform desktop applications.

---

## 1. Hardcoded Paths

### Anti-Pattern: Platform-Specific Path Hardcoding

**WRONG**: Windows-style path
```rust
let config = std::fs::read("C:\\Users\\app\\config.json")?;
// ❌ Fails on macOS and Linux
// ❌ Assumes specific Windows drive letter
// ❌ Hardcoded user directory
```

**WRONG**: Unix-style absolute path
```rust
let config = std::fs::read("/home/user/.config/app/config.json")?;
// ❌ Fails on Windows
// ❌ Fails on macOS (uses /Users instead of /home)
// ❌ Hardcoded username
```

**WRONG**: Relative path without proper base
```rust
let config = std::fs::read("./config.json")?;
// ❌ Depends on current working directory
// ❌ Breaks when app is launched from different directory
```

**CORRECT**: Platform-appropriate paths using directories crate
```rust
use directories::ProjectDirs;

let dirs = ProjectDirs::from("com", "company", "app")
    .expect("Failed to get project directories");
let config_path = dirs.config_dir().join("config.json");
let config = std::fs::read(config_path)?;

// ✅ Works on all platforms
// ✅ Uses standard config directories:
//    Windows: %APPDATA%\company\app\
//    macOS: ~/Library/Application Support/com.company.app/
//    Linux: ~/.config/app/
```

### Path Separator Issues

**WRONG**: Hardcoded separators
```rust
let path = "data/files/config.json";  // Works on Unix
let path = "data\\files\\config.json";  // Works on Windows

// ❌ Platform-specific
```

**CORRECT**: Use PathBuf
```rust
use std::path::PathBuf;

let path = PathBuf::from("data")
    .join("files")
    .join("config.json");

// ✅ Correct separators on all platforms
```

---

## 2. Missing Platform Dependencies

### Anti-Pattern: Ignoring Linux Build Dependencies

**WRONG**: Missing Linux dependencies in CI
```yaml
- name: Build
  run: npm run tauri build
  # ❌ Fails on Linux with cryptic errors about missing GTK, WebKit, etc.
```

**Error you'll see**:
```
error: failed to run custom build command for `webkit2gtk-sys`
Package gtk+-3.0 was not found in the pkg-config search path
```

**CORRECT**: Install platform dependencies
```yaml
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

- name: Build
  run: npm run tauri build
  # ✅ Now builds successfully on Linux
```

### Anti-Pattern: Assuming Dependencies Are Available

**WRONG**: Not documenting required system dependencies
```markdown
# README.md
## Building
npm install
npm run tauri build
```

**CORRECT**: Document all platform-specific dependencies
```markdown
# README.md
## Building

### Prerequisites

**Windows**:
- Visual Studio Build Tools 2019 or later
- Windows SDK

**macOS**:
- Xcode Command Line Tools: `xcode-select --install`

**Linux (Debian/Ubuntu)**:
```bash
sudo apt-get install libgtk-3-dev libwebkit2gtk-4.0-dev \
  libappindicator3-dev librsvg2-dev patchelf
```

Then:
```bash
npm install
npm run tauri build
```
```

---

## 3. Universal Binary Issues (macOS)

### Anti-Pattern: Building Universal Without Both Targets

**WRONG**: Build universal without both architectures available
```yaml
- name: Build macOS Universal
  run: npm run tauri build -- --target universal-apple-darwin
  # ❌ Fails if x86_64 or aarch64 Rust targets not installed
```

**Error you'll see**:
```
error: failed to build app: target not found
```

**CORRECT**: Build each architecture separately, then combine
```yaml
- name: Install Rust Targets
  run: |
    rustup target add x86_64-apple-darwin
    rustup target add aarch64-apple-darwin

- name: Build macOS Intel
  run: npm run tauri build -- --target x86_64-apple-darwin

- name: Build macOS ARM
  run: npm run tauri build -- --target aarch64-apple-darwin

- name: Create Universal Binary
  run: |
    lipo -create \
      target/x86_64-apple-darwin/release/myapp \
      target/aarch64-apple-darwin/release/myapp \
      -output target/universal/myapp

    # Verify
    lipo -info target/universal/myapp
    # Output: Architectures in the fat file: ... are: x86_64 arm64
```

### Anti-Pattern: Not Testing on Target Architecture

**WRONG**: Only testing on Apple Silicon
```bash
# Developer has M1 Mac, only tests on ARM
cargo build --release
# ✅ Works on ARM
# ❌ Never tested on Intel - might have architecture-specific bugs
```

**CORRECT**: Test on both architectures (or in CI)
```yaml
strategy:
  matrix:
    include:
      - platform: macos-latest  # M1
        target: aarch64-apple-darwin
      - platform: macos-13  # Intel
        target: x86_64-apple-darwin
```

---

## 4. Missing Notarization (macOS)

### Anti-Pattern: Signing Without Notarization

**WRONG**: Sign without notarization
```bash
codesign --sign "Developer ID Application" MyApp.app
# ✅ App is signed
# ❌ Users get Gatekeeper warnings: "App cannot be opened because it is from an unidentified developer"
```

**CORRECT**: Sign AND notarize
```bash
# 1. Sign with hardened runtime
codesign --sign "Developer ID Application: Company Name (TEAM_ID)" \
  --options runtime \
  --entitlements entitlements.plist \
  --force \
  --deep \
  MyApp.app

# 2. Create archive for notarization
ditto -c -k --keepParent MyApp.app MyApp.zip

# 3. Submit for notarization
xcrun notarytool submit MyApp.zip \
  --apple-id "$APPLE_ID" \
  --password "$APP_PASSWORD" \
  --team-id "$TEAM_ID" \
  --wait

# 4. Staple notarization ticket
xcrun stapler staple MyApp.app

# ✅ App opens without warnings
```

### Anti-Pattern: Distributing Before Notarization Completes

**WRONG**: Distribute immediately after submission
```bash
xcrun notarytool submit MyApp.zip ... &  # Background process
# Don't wait...
cp MyApp.dmg /releases/  # ❌ Not notarized yet!
```

**CORRECT**: Wait for notarization to complete
```bash
xcrun notarytool submit MyApp.zip \
  --apple-id "$APPLE_ID" \
  --password "$APP_PASSWORD" \
  --team-id "$TEAM_ID" \
  --wait  # ✅ Blocks until complete

xcrun stapler staple MyApp.app
# ✅ Now safe to distribute
```

---

## 5. Code Signing Mistakes

### Anti-Pattern: Committing Certificates to Repository

**WRONG**: Certificate in repository
```bash
git add certificates/code-signing-cert.pfx
git commit -m "Add signing certificate"
# ❌❌❌ MAJOR SECURITY ISSUE
# Anyone with repo access can sign malicious code as you
```

**CORRECT**: Use CI/CD secrets
```yaml
- name: Import Certificate
  run: |
    echo "${{ secrets.WINDOWS_CERTIFICATE }}" | base64 --decode > cert.pfx
    certutil -importpfx cert.pfx -p "${{ secrets.CERT_PASSWORD }}"
    rm cert.pfx  # Clean up immediately
```

### Anti-Pattern: Skipping Timestamping

**WRONG**: Sign without timestamp
```bash
signtool sign MyApp.exe
# ❌ Signature becomes invalid when certificate expires
```

**CORRECT**: Always use timestamping
```bash
signtool sign /tr http://timestamp.digicert.com /td sha256 MyApp.exe
# ✅ Signature remains valid even after certificate expires
```

### Anti-Pattern: Not Verifying Signatures

**WRONG**: Build and distribute without verification
```bash
npm run tauri build
# Assume it's signed correctly...
# ❌ Might not be signed at all!
```

**CORRECT**: Verify before distributing
```bash
npm run tauri build

# Windows
signtool verify /pa /v target/release/MyApp.exe

# macOS
codesign --verify --deep --strict target/release/MyApp.app
spctl --assess --type execute target/release/MyApp.app

# ✅ Confirmed signed correctly
```

---

## 6. Build Configuration Mistakes

### Anti-Pattern: Mixing Debug and Release Dependencies

**WRONG**: Debug dependencies in release
```toml
[dependencies]
env_logger = "0.10"  # Only needed for debugging
pretty_env_logger = "0.5"  # Only needed for debugging

# ❌ Bloats release binary with debug tools
```

**CORRECT**: Use dev-dependencies
```toml
[dependencies]
# Production dependencies only

[dev-dependencies]
env_logger = "0.10"
pretty_env_logger = "0.5"

# ✅ Not included in release builds
```

### Anti-Pattern: Ignoring Platform-Specific Features

**WRONG**: Enable all features for all platforms
```toml
[dependencies]
windows = { version = "0.48", features = ["full"] }

# ❌ Includes Windows APIs on Linux/macOS
# ❌ Increases compile time on non-Windows
```

**CORRECT**: Use target-specific dependencies
```toml
[target.'cfg(windows)'.dependencies]
windows = { version = "0.48", features = ["Win32_System_Console"] }

# ✅ Only compiled on Windows
# ✅ Only includes needed features
```

---

## 7. CI/CD Anti-Patterns

### Anti-Pattern: No Caching

**WRONG**: Build from scratch every time
```yaml
- name: Build
  run: |
    cargo build --release
    # Every build downloads all dependencies: ~5-10 minutes
```

**CORRECT**: Cache dependencies
```yaml
- name: Cache Cargo
  uses: actions/cache@v4
  with:
    path: |
      ~/.cargo/registry
      ~/.cargo/git
      target
    key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}

- name: Build
  run: cargo build --release
  # First build: ~5-10 minutes
  # Cached builds: ~1-2 minutes
```

### Anti-Pattern: Sequential Platform Builds

**WRONG**: Build platforms one by one
```yaml
jobs:
  build-windows:
    runs-on: windows-latest
    # Runs first: 10 minutes

  build-macos:
    needs: build-windows
    runs-on: macos-latest
    # Waits for Windows, then runs: +10 minutes

  build-linux:
    needs: build-macos
    runs-on: ubuntu-latest
    # Waits for Windows + macOS, then runs: +10 minutes
    # Total: 30 minutes
```

**CORRECT**: Build in parallel
```yaml
jobs:
  build:
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-22.04]
    runs-on: ${{ matrix.os }}
    # All build simultaneously
    # Total: 10 minutes
```

---

## 8. Frontend Build Mistakes

### Anti-Pattern: Bundling Everything

**WRONG**: Import entire libraries
```typescript
import * as THREE from 'three'
import * as _ from 'lodash'
import moment from 'moment'

// ❌ Includes all of Three.js, Lodash, Moment
// ❌ Bundle size: 500+ KB
```

**CORRECT**: Import only what you need
```typescript
import { Scene, PerspectiveCamera } from 'three'
import { debounce } from 'lodash-es'
import { format } from 'date-fns'

// ✅ Tree-shaking removes unused code
// ✅ Bundle size: 50-100 KB
```

### Anti-Pattern: No Code Splitting

**WRONG**: Single bundle
```typescript
// main.ts
import EditorComponent from './editor'
import ChartsComponent from './charts'
import ThreeDViewer from './3d-viewer'

// All loaded immediately
// ❌ Initial bundle: 2+ MB
// ❌ Slow initial load
```

**CORRECT**: Lazy load components
```typescript
// main.ts
const EditorComponent = defineAsyncComponent(() => import('./editor'))
const ChartsComponent = defineAsyncComponent(() => import('./charts'))
const ThreeDViewer = defineAsyncComponent(() => import('./3d-viewer'))

// ✅ Initial bundle: 200 KB
// ✅ Fast initial load
// ✅ Components load on demand
```

---

## 9. Version Management Mistakes

### Anti-Pattern: Inconsistent Version Numbers

**WRONG**: Different versions in different files
```json
// package.json
{
  "version": "1.2.0"
}

// tauri.conf.json
{
  "package": {
    "version": "1.1.0"  // ❌ Out of sync!
  }
}

// Cargo.toml
[package]
version = "1.0.0"  // ❌ Different version!
```

**CORRECT**: Single source of truth
```json
// package.json
{
  "version": "1.2.0",
  "scripts": {
    "version": "npm run sync-versions"
  }
}
```

```bash
#!/bin/bash
# scripts/sync-versions.sh
VERSION=$(node -p "require('./package.json').version")

# Update tauri.conf.json
jq ".package.version = \"$VERSION\"" tauri.conf.json > tmp.json
mv tmp.json tauri.conf.json

# Update Cargo.toml
sed -i "s/^version = .*/version = \"$VERSION\"/" src-tauri/Cargo.toml

# ✅ All files use same version
```

---

## 10. Testing Mistakes

### Anti-Pattern: Not Testing on Target Platforms

**WRONG**: Only test on development machine
```bash
# Developer on macOS M1
cargo test
npm test
# ✅ Works on macOS ARM
# ❌ Never tested on Windows, Linux, or macOS Intel
# ❌ Platform-specific bugs go undetected
```

**CORRECT**: Test in CI on all platforms
```yaml
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-22.04, windows-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - run: cargo test
      - run: npm test
```

### Anti-Pattern: No Build Tests

**WRONG**: No tests for build configuration
```rust
// No tests...

// ❌ Invalid bundle ID might go unnoticed
// ❌ Missing icons not caught until build fails
// ❌ Broken tauri.conf.json not detected
```

**CORRECT**: Test build configuration
```rust
#[test]
fn test_tauri_config_valid() {
    let config: serde_json::Value = serde_json::from_str(
        &std::fs::read_to_string("src-tauri/tauri.conf.json").unwrap()
    ).unwrap();

    assert!(config["tauri"]["bundle"]["identifier"].as_str().is_some());
    assert!(config["package"]["version"].as_str().is_some());
}

#[test]
fn test_all_icons_exist() {
    let required_icons = vec![
        "icons/icon.ico",   // Windows
        "icons/icon.icns",  // macOS
        "icons/icon.png",   // Linux
    ];
    for icon in required_icons {
        assert!(Path::new(&format!("src-tauri/{}", icon)).exists());
    }
}
```

---

## 11. Quick Reference: Anti-Patterns to Avoid

### Path Handling
- ❌ Hardcoded absolute paths
- ❌ Platform-specific path separators
- ✅ Use `directories` crate
- ✅ Use `PathBuf::join()`

### Dependencies
- ❌ Missing platform dependencies
- ❌ Not documenting prerequisites
- ✅ Document all platform requirements
- ✅ Install dependencies in CI

### macOS
- ❌ Skipping notarization
- ❌ Building universal without both targets
- ✅ Always notarize production builds
- ✅ Test on both Intel and ARM

### Code Signing
- ❌ Committing certificates
- ❌ Skipping timestamping
- ❌ Not verifying signatures
- ✅ Use CI/CD secrets
- ✅ Always timestamp
- ✅ Verify before distributing

### CI/CD
- ❌ No caching
- ❌ Sequential builds
- ✅ Cache dependencies
- ✅ Parallel platform builds

### Frontend
- ❌ Bundling everything
- ❌ No code splitting
- ✅ Import only needed code
- ✅ Lazy load components

### Testing
- ❌ Only testing on dev machine
- ❌ No build configuration tests
- ✅ Test on all platforms in CI
- ✅ Test build configs

---

## 12. Common Error Messages and Solutions

### "Package gtk+-3.0 was not found"
```bash
# Solution:
sudo apt-get install libgtk-3-dev libwebkit2gtk-4.0-dev
```

### "App is damaged and can't be opened" (macOS)
```bash
# Solution: Sign and notarize
codesign --sign "Developer ID" --options runtime MyApp.app
xcrun notarytool submit MyApp.zip --wait
xcrun stapler staple MyApp.app
```

### "Windows protected your PC" SmartScreen
```bash
# Solutions:
# 1. Use EV code signing certificate
# 2. Build reputation (100+ users)
# 3. Contact Microsoft for reputation review
```

### "error: failed to run custom build command"
```bash
# Usually means missing system dependencies
# Check the error for package names, install with:
# - Windows: Visual Studio Build Tools
# - macOS: xcode-select --install
# - Linux: sudo apt-get install <missing-packages>
```

---

## Summary

**Most Common Mistakes**:
1. Hardcoded platform-specific paths
2. Missing Linux build dependencies
3. Not notarizing macOS apps
4. Committing signing certificates
5. No caching in CI/CD
6. Not testing on all platforms
7. Bundling entire libraries in frontend
8. Inconsistent version numbers
9. Skipping signature verification
10. Building platforms sequentially instead of parallel

**Remember**: Test on all target platforms early and often!
