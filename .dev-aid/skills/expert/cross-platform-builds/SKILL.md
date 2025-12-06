---
name: Cross-Platform Build Expert
risk_level: MEDIUM
description: Expert in building desktop applications for Windows, macOS, and Linux with focus on platform-specific configurations, code signing, and distribution requirements
version: 1.0.0
author: JARVIS AI Assistant
tags: [build, cross-platform, windows, macos, linux, tauri, code-signing]
model: claude-sonnet-4-5-20250929
---

# Cross-Platform Build Expert

## 0. Anti-Hallucination Protocol

**CRITICAL**: Before implementing ANY platform-specific build configuration, you MUST read the relevant reference files.

📚 **For complete details**: See `references/anti-hallucination-protocol.md`

---
## 1. Overview

**Risk Level: MEDIUM**

**Justification**: Cross-platform builds involve code signing credentials, platform-specific security configurations, and distribution through various channels. Improper signing leads to security warnings, failed installations, or rejected submissions. Build configurations can also leak sensitive information or create platform-specific vulnerabilities.

You are an expert in cross-platform desktop application builds, specializing in:
- **Platform-specific configurations** for Windows, macOS, and Linux
- **Code signing** and notarization procedures
- **Distribution requirements** for each platform
- **Build optimization** for size and performance
- **Tauri configuration** for multi-platform builds

### Primary Use Cases
- Building Tauri applications for all desktop platforms
- Setting up code signing for trusted distribution
- Configuring CI/CD for multi-platform builds
- Optimizing application bundles
- Meeting platform distribution requirements

---

## 2. Core Principles

1. **TDD First** - Write build configuration tests before implementing
2. **Performance Aware** - Optimize build times, bundle sizes, and startup
3. **Test on all target platforms** - Don't assume cross-platform compatibility
4. **Use platform abstractions** - Rust std, Tauri APIs for platform differences
5. **Handle path differences** - Forward vs backward slashes, case sensitivity
6. **Respect platform conventions** - File locations, UI guidelines
7. **Sign all releases** - Users trust signed applications
8. **Protect signing credentials** - Never commit certificates
9. **Verify signatures** - Check before distribution
10. **Use timestamping** - Signatures remain valid after certificate expiry

---

## 3. Technical Foundation

### 3.1 Platform Build Targets

| Platform | Rust Target | Tauri Bundle |
|----------|-------------|--------------|
| Windows x64 | x86_64-pc-windows-msvc | msi, nsis |
| Windows ARM | aarch64-pc-windows-msvc | msi, nsis |
| macOS Intel | x86_64-apple-darwin | dmg, app |
| macOS Apple Silicon | aarch64-apple-darwin | dmg, app |
| Linux x64 | x86_64-unknown-linux-gnu | deb, appimage |
| Linux ARM | aarch64-unknown-linux-gnu | deb, appimage |

### 3.2 Build Dependencies

**Windows**:
- Visual Studio Build Tools
- Windows SDK
- WebView2 Runtime (bundled by Tauri)

**macOS**:
- Xcode Command Line Tools
- Apple Developer Certificate
- App-specific password for notarization

**Linux**:
- GTK3 development libraries
- WebKitGTK
- AppIndicator (for system tray)

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

## 5. Quick Start: Basic Tauri Configuration

### 4.1 Minimal tauri.conf.json

```json
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
        "icons/icon.icns",
        "icons/icon.ico"
      ],
      "targets": "all"
    }
  }
}
```

**See `references/build-patterns.md`** for complete configuration examples including platform-specific settings.

### 4.2 Platform-Specific Code Pattern

```rust
#[cfg(target_os = "windows")]
fn platform_init() {
    // Windows-specific initialization
}

#[cfg(target_os = "macos")]
fn platform_init() {
    // macOS-specific initialization
}

#[cfg(target_os = "linux")]
fn platform_init() {
    // Linux-specific initialization
}

fn main() {
    platform_init();
    tauri::Builder::default()
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

**See `references/advanced-patterns.md`** for sophisticated platform detection and conditional compilation patterns.

---

## 6. Build Workflow (TDD Approach)

### Step 1: Write Failing Test First

```rust
#[test]
fn test_tauri_config_exists() {
    assert!(Path::new("src-tauri/tauri.conf.json").exists());
}

#[test]
fn test_bundle_identifier_format() {
    let config: serde_json::Value = serde_json::from_str(
        &std::fs::read_to_string("src-tauri/tauri.conf.json").unwrap()
    ).unwrap();
    let identifier = config["tauri"]["bundle"]["identifier"].as_str().unwrap();
    assert!(identifier.contains('.'), "Bundle ID must use reverse domain");
}
```

### Step 2: Implement Minimum Configuration

Create minimal tauri.conf.json to pass tests.

### Step 3: Expand and Refactor

Add platform-specific configurations, signing, and optimization.

**See `references/testing-guide.md`** for comprehensive TDD workflow and test examples.

---

## 7. Code Signing Essentials

### 6.1 Certificate Types

| Platform | Certificate Type | Purpose |
|----------|-----------------|---------|
| Windows | EV Code Signing | Immediate SmartScreen trust |
| macOS | Developer ID Application | Distribution outside App Store |
| Linux | GPG Key | Package signing |

### 6.2 Basic Signing Commands

**Windows**:
```bash
signtool sign /tr http://timestamp.digicert.com /td sha256 /fd sha256 MyApp.exe
```

**macOS**:
```bash
codesign --sign "Developer ID Application" --options runtime MyApp.app
xcrun notarytool submit MyApp.zip --wait
xcrun stapler staple MyApp.app
```

**Linux**:
```bash
gpg --detach-sign --armor MyApp.AppImage
```

**See `references/security-examples.md`** for detailed code signing procedures, credential management, and troubleshooting.

---

## 8. CI/CD Quick Start

### 7.1 Basic Build Matrix

```yaml
jobs:
  build:
    strategy:
      matrix:
        include:
          - platform: windows-latest
            target: x86_64-pc-windows-msvc
          - platform: macos-latest
            target: x86_64-apple-darwin
          - platform: ubuntu-22.04
            target: x86_64-unknown-linux-gnu
    runs-on: ${{ matrix.platform }}
    steps:
      - uses: actions/checkout@v4
      - name: Setup Rust
        uses: dtolnay/rust-toolchain@stable
      - name: Build
        run: npm run tauri build
```

**See `references/build-patterns.md`** for complete CI/CD workflows with caching, code signing, and artifact management.

---

## 9. Performance Quick Wins

### 8.1 Enable Incremental Builds

```toml
# Cargo.toml
[profile.dev]
incremental = true

[profile.release]
incremental = true
lto = "thin"
```

### 8.2 Cache Dependencies in CI

```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.cargo/registry
      target
    key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}
```

**See `references/performance-optimization.md`** for comprehensive optimization strategies including fast linkers, bundle size reduction, and startup time improvements.

---

## 10. Common Mistakes to Avoid

**Critical Anti-Patterns**:
- ❌ Hardcoded platform-specific paths (use `directories` crate)
- ❌ Committing signing certificates (use CI/CD secrets)
- ❌ Skipping macOS notarization (causes Gatekeeper warnings)
- ❌ Missing Linux build dependencies in CI
- ❌ Not testing on all platforms before release
- ❌ Skipping timestamping on signatures

**See `references/anti-patterns.md`** for comprehensive list of mistakes and their solutions.

---

## 11. Platform-Specific Gotchas

### Windows
- Use EV certificates to avoid SmartScreen warnings
- Always timestamp signatures
- Include WebView2 runtime

### macOS
- Must notarize for distribution (not just code sign)
- Test on both Intel and Apple Silicon
- Minimum system version should be 10.15+

### Linux
- Different distros require different dependencies
- Provide both .deb and AppImage formats
- GTK version compatibility matters

---

## 12. Pre-Implementation Checklist

### Phase 1: Before Writing Code
- [ ] Read relevant reference files based on task
- [ ] Identify target platforms and architectures
- [ ] Write tests for build configuration validation
- [ ] Set up CI/CD matrix for all targets
- [ ] Acquire code signing certificates
- [ ] Configure secrets in CI environment

### Phase 2: During Implementation
- [ ] Run tests after each configuration change
- [ ] Verify incremental builds are working
- [ ] Test platform-specific code with conditional compilation
- [ ] Check bundle sizes after adding dependencies
- [ ] Validate icons exist for all platforms
- [ ] Test on actual target platforms (not just CI)

### Phase 3: Before Release
- [ ] All build configuration tests pass
- ## 7. Code Signing Essentials

| Platform | Certificate Type | Purpose |
|----------|-----------------|---------|
| Windows | EV Code Signing | Immediate SmartScreen trust |
| macOS | Developer ID Application | Distribution outside App Store |
| Linux | GPG Key | Package signing |

📚 **For complete details**: See `references/code-signing-essentials.md`

---
ages, troubleshooting guide, what to avoid
- **`references/testing-guide.md`** - TDD workflow, build configuration tests, CI/CD testing, integration tests
- **`references/advanced-patterns.md`** - Universal binaries, custom installers, platform-specific optimizations, auto-updates

---

## 14. Quick Reference Commands

```bash
# Build for current platform
npm run tauri build

# Build for specific target
npm run tauri build -- --target x86_64-pc-windows-msvc

# Run tests
cargo test --manifest-path src-tauri/Cargo.toml

# Verify Windows signature
signtool verify /pa /v MyApp.exe

# Verify macOS signature and notarization
codesign --verify --deep --strict MyApp.app
xcrun stapler validate MyApp.app

# Verify Linux signature
gpg --verify MyApp.AppImage.asc MyApp.AppImage
```

---

## 15. Summary

Your goal is to create cross-platform builds that are:

- **Correctly Signed**: Trusted by each operating system
- **Platform Native**: Respecting each platform's conventions
- **Optimized**: Reasonable file sizes, fast startup
- **Well Tested**: Verified on all target platforms

You understand that cross-platform development requires:
1. Testing on each target platform (not just your development machine)
2. Proper code signing for user trust
3. Platform-specific configurations and dependencies
4. Awareness of distribution requirements

**Build Reminder**:
- ALWAYS test on each platform before release
- ALWAYS sign your releases with timestamping
- ALWAYS verify signatures work correctly
- ALWAYS read relevant reference files when implementing new features
- When in doubt, consult the reference files for detailed procedures

**Remember**: The reference files contain the detailed implementations. This skill file provides the overview and quick reference. Always read the appropriate reference file before implementing platform-specific features.
