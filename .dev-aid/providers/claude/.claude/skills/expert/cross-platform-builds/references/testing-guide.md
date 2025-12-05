# Cross-Platform Build Testing Guide

This document provides comprehensive guidance on test-driven development (TDD) for cross-platform builds, including build configuration tests, platform-specific tests, and verification workflows.

---

## 1. TDD Workflow Overview

### The Red-Green-Refactor Cycle

1. **🔴 Red**: Write a failing test first
2. **🟢 Green**: Write minimum code to make it pass
3. **🔵 Refactor**: Improve code while keeping tests passing
4. **🔁 Repeat**: Continue for each requirement

**Why TDD for Builds?**
- Catches configuration errors before they break CI/CD
- Documents expected build behavior
- Prevents regressions when updating configs
- Makes platform-specific issues visible early

---

## 2. Build Configuration Tests

### 2.1 Testing Tauri Configuration

```rust
// tests/build_config_test.rs
#[cfg(test)]
mod tauri_config_tests {
    use std::path::Path;
    use serde_json::Value;

    fn load_tauri_config() -> Value {
        let config_str = std::fs::read_to_string("src-tauri/tauri.conf.json")
            .expect("Failed to read tauri.conf.json");
        serde_json::from_str(&config_str)
            .expect("Failed to parse tauri.conf.json")
    }

    #[test]
    fn test_tauri_config_exists() {
        assert!(Path::new("src-tauri/tauri.conf.json").exists(),
            "tauri.conf.json must exist");
    }

    #[test]
    fn test_bundle_identifier_format() {
        let config = load_tauri_config();
        let identifier = config["tauri"]["bundle"]["identifier"]
            .as_str()
            .expect("Bundle identifier must be a string");

        assert!(identifier.contains('.'),
            "Bundle ID must use reverse domain notation (e.g., com.company.app)");
        assert!(!identifier.starts_with('.'),
            "Bundle ID cannot start with a dot");
        assert!(!identifier.ends_with('.'),
            "Bundle ID cannot end with a dot");
    }

    #[test]
    fn test_product_name_exists() {
        let config = load_tauri_config();
        let product_name = config["package"]["productName"]
            .as_str()
            .expect("Product name must be a string");

        assert!(!product_name.is_empty(),
            "Product name cannot be empty");
    }

    #[test]
    fn test_version_format() {
        let config = load_tauri_config();
        let version = config["package"]["version"]
            .as_str()
            .expect("Version must be a string");

        // Simple semver validation
        let parts: Vec<&str> = version.split('.').collect();
        assert_eq!(parts.len(), 3,
            "Version must be in format X.Y.Z");

        for part in parts {
            part.parse::<u32>()
                .expect("Version parts must be numbers");
        }
    }
}
```

### 2.2 Testing Icon Availability

```rust
#[cfg(test)]
mod icon_tests {
    use std::path::Path;

    #[test]
    fn test_icons_all_platforms() {
        let required_icons = vec![
            "src-tauri/icons/icon.ico",      // Windows
            "src-tauri/icons/icon.icns",     // macOS
            "src-tauri/icons/32x32.png",     // Linux/Windows
            "src-tauri/icons/128x128.png",   // All platforms
        ];

        for icon in required_icons {
            assert!(Path::new(icon).exists(),
                "Missing required icon: {}", icon);
        }
    }

    #[test]
    fn test_icon_sizes() {
        // Verify PNG icons have correct dimensions
        use image::GenericImageView;

        let icons = vec![
            ("src-tauri/icons/32x32.png", 32, 32),
            ("src-tauri/icons/128x128.png", 128, 128),
        ];

        for (path, expected_width, expected_height) in icons {
            let img = image::open(path)
                .expect(&format!("Failed to open {}", path));
            let (width, height) = img.dimensions();

            assert_eq!(width, expected_width,
                "{} width must be {}", path, expected_width);
            assert_eq!(height, expected_height,
                "{} height must be {}", path, expected_height);
        }
    }
}
```

### 2.3 Testing Platform-Specific Configurations

```rust
#[cfg(test)]
mod platform_config_tests {
    use serde_json::Value;

    fn load_tauri_config() -> Value {
        let config_str = std::fs::read_to_string("src-tauri/tauri.conf.json")
            .expect("Failed to read tauri.conf.json");
        serde_json::from_str(&config_str).unwrap()
    }

    #[test]
    fn test_windows_signing_config() {
        let config = load_tauri_config();
        let windows = &config["tauri"]["bundle"]["windows"];

        assert!(windows["timestampUrl"].as_str().is_some(),
            "Windows build must have timestamp URL for code signing");
        assert_eq!(windows["digestAlgorithm"].as_str().unwrap(), "sha256",
            "Must use SHA256 digest algorithm");
    }

    #[test]
    fn test_macos_minimum_version() {
        let config = load_tauri_config();
        let min_ver = config["tauri"]["bundle"]["macOS"]["minimumSystemVersion"]
            .as_str()
            .expect("macOS minimum version must be specified");

        // Parse version (e.g., "10.15")
        let parts: Vec<&str> = min_ver.split('.').collect();
        let major: u32 = parts[0].parse().unwrap();
        let minor: u32 = parts[1].parse().unwrap();

        // Must support at least macOS 10.15 (Catalina)
        assert!(major > 10 || (major == 10 && minor >= 15),
            "Must support macOS 10.15 or later");
    }

    #[test]
    fn test_macos_entitlements_exist() {
        let config = load_tauri_config();
        let entitlements_path = config["tauri"]["bundle"]["macOS"]["entitlements"]
            .as_str()
            .expect("macOS entitlements path must be specified");

        let full_path = format!("src-tauri/{}", entitlements_path);
        assert!(std::path::Path::new(&full_path).exists(),
            "macOS entitlements file must exist at: {}", full_path);
    }

    #[test]
    fn test_linux_dependencies_specified() {
        let config = load_tauri_config();
        let deb_depends = &config["tauri"]["bundle"]["linux"]["deb"]["depends"];

        assert!(deb_depends.is_array(),
            "Linux .deb dependencies must be specified");

        let deps = deb_depends.as_array().unwrap();
        assert!(!deps.is_empty(),
            "Linux .deb must have at least one dependency");
    }
}
```

---

## 3. Frontend Build Tests

### 3.1 Testing Frontend Build Process

```rust
#[cfg(test)]
mod frontend_tests {
    use std::process::Command;

    #[test]
    fn test_frontend_builds_successfully() {
        let output = Command::new("npm")
            .args(["run", "build"])
            .output()
            .expect("Failed to run npm build");

        assert!(output.status.success(),
            "Frontend build failed:\n{}",
            String::from_utf8_lossy(&output.stderr));
    }

    #[test]
    fn test_dist_directory_created() {
        // Ensure build creates dist directory
        let dist_exists = std::path::Path::new("dist").exists();
        assert!(dist_exists,
            "Frontend build must create 'dist' directory");
    }

    #[test]
    fn test_frontend_lint_passes() {
        let output = Command::new("npm")
            .args(["run", "lint"])
            .output()
            .expect("Failed to run npm lint");

        assert!(output.status.success(),
            "Frontend lint failed:\n{}",
            String::from_utf8_lossy(&output.stderr));
    }
}
```

---

## 4. TDD Implementation Example

### Step 1: Write Failing Test First

```rust
// tests/build_config_test.rs
#[test]
fn test_custom_protocol_configured() {
    let config = load_tauri_config();
    let protocol = &config["tauri"]["security"]["assetProtocol"];

    assert!(protocol["enable"].as_bool().unwrap_or(false),
        "Custom asset protocol must be enabled");
    assert_eq!(protocol["scope"].as_array().unwrap().len(), 1,
        "Asset protocol scope must be configured");
}
```

**Run test**:
```bash
cargo test test_custom_protocol_configured
# ❌ FAILS: assetProtocol not configured
```

### Step 2: Implement Minimum to Pass

```json
// tauri.conf.json
{
  "tauri": {
    "security": {
      "assetProtocol": {
        "enable": true,
        "scope": ["**/*"]
      }
    }
  }
}
```

**Run test**:
```bash
cargo test test_custom_protocol_configured
# ✅ PASSES
```

### Step 3: Refactor and Expand

Add more specific tests:

```rust
#[test]
fn test_asset_protocol_scope_restricted() {
    let config = load_tauri_config();
    let scope = config["tauri"]["security"]["assetProtocol"]["scope"]
        .as_array()
        .expect("Scope must be an array");

    // Ensure scope is not too permissive
    let scope_str = scope[0].as_str().unwrap();
    assert_ne!(scope_str, "**/*",
        "Asset protocol scope should be more restrictive than '**/*'");
}
```

Refine configuration:

```json
{
  "tauri": {
    "security": {
      "assetProtocol": {
        "enable": true,
        "scope": ["$APPDATA/**", "$RESOURCE/**"]
      }
    }
  }
}
```

### Step 4: Run Full Verification

```bash
# Run all build tests
cargo test --manifest-path src-tauri/Cargo.toml

# Run frontend tests
npm test

# Verify build succeeds
npm run tauri build
```

---

## 5. Platform-Specific Testing

### 5.1 Conditional Test Execution

```rust
#[cfg(target_os = "windows")]
#[test]
fn test_windows_specific_feature() {
    // Only runs on Windows
    use windows::Win32::System::Console::GetConsoleCP;
    unsafe {
        let cp = GetConsoleCP();
        assert_ne!(cp, 0, "Console code page must be valid");
    }
}

#[cfg(target_os = "macos")]
#[test]
fn test_macos_bundle_structure() {
    // Only runs on macOS
    use std::path::Path;
    assert!(Path::new("/Applications").exists(),
        "Must be running on macOS");
}

#[cfg(target_os = "linux")]
#[test]
fn test_linux_desktop_entry() {
    // Only runs on Linux
    // Test .desktop file generation, etc.
}
```

### 5.2 Cross-Platform Test Patterns

```rust
#[test]
fn test_app_data_directory_accessible() {
    use directories::ProjectDirs;

    let dirs = ProjectDirs::from("com", "company", "myapp")
        .expect("Failed to get project directories");

    let data_dir = dirs.data_dir();

    // Create directory if it doesn't exist
    std::fs::create_dir_all(data_dir)
        .expect("Failed to create data directory");

    // Verify it's accessible
    assert!(data_dir.exists(), "Data directory must be accessible");

    // Verify we can write to it
    let test_file = data_dir.join("test.txt");
    std::fs::write(&test_file, "test")
        .expect("Must be able to write to data directory");

    // Clean up
    std::fs::remove_file(&test_file).ok();
}
```

---

## 6. CI/CD Testing Strategy

### 6.1 GitHub Actions Test Workflow

```yaml
name: Test

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-22.04, windows-latest, macos-latest]

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4

      - name: Setup Rust
        uses: dtolnay/rust-toolchain@stable

      - name: Install Linux Dependencies
        if: matrix.os == 'ubuntu-22.04'
        run: |
          sudo apt-get update
          sudo apt-get install -y libgtk-3-dev libwebkit2gtk-4.0-dev

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install Dependencies
        run: npm ci

      - name: Run Rust Tests
        run: cargo test --manifest-path src-tauri/Cargo.toml

      - name: Run Frontend Tests
        run: npm test

      - name: Lint Frontend
        run: npm run lint

      - name: Build Config Tests
        run: cargo test --test build_config_test

      - name: Test Build Process
        run: npm run tauri build -- --debug
```

### 6.2 Test Coverage for Build Configs

```yaml
- name: Validate Build Artifacts
  run: |
    # Windows
    if [ "${{ matrix.os }}" == "windows-latest" ]; then
      test -f src-tauri/target/release/bundle/msi/*.msi || exit 1
    fi

    # macOS
    if [ "${{ matrix.os }}" == "macos-latest" ]; then
      test -d src-tauri/target/release/bundle/macos/*.app || exit 1
    fi

    # Linux
    if [ "${{ matrix.os }}" == "ubuntu-22.04" ]; then
      test -f src-tauri/target/release/bundle/deb/*.deb || exit 1
      test -f src-tauri/target/release/bundle/appimage/*.AppImage || exit 1
    fi
```

---

## 7. Integration Tests

### 7.1 End-to-End Build Test

```rust
#[test]
#[ignore]  // Run with: cargo test -- --ignored
fn test_full_build_process() {
    use std::process::Command;

    // Clean
    let clean = Command::new("cargo")
        .args(["clean"])
        .current_dir("src-tauri")
        .status()
        .expect("Failed to run cargo clean");
    assert!(clean.success(), "Clean failed");

    // Build frontend
    let frontend = Command::new("npm")
        .args(["run", "build"])
        .status()
        .expect("Failed to build frontend");
    assert!(frontend.success(), "Frontend build failed");

    // Build Tauri
    let tauri = Command::new("npm")
        .args(["run", "tauri", "build", "--", "--debug"])
        .status()
        .expect("Failed to build Tauri");
    assert!(tauri.success(), "Tauri build failed");

    // Verify artifacts exist
    #[cfg(target_os = "windows")]
    {
        let msi_exists = glob::glob("src-tauri/target/debug/bundle/msi/*.msi")
            .unwrap()
            .next()
            .is_some();
        assert!(msi_exists, "MSI installer not created");
    }

    #[cfg(target_os = "macos")]
    {
        let app_exists = glob::glob("src-tauri/target/debug/bundle/macos/*.app")
            .unwrap()
            .next()
            .is_some();
        assert!(app_exists, "macOS app bundle not created");
    }

    #[cfg(target_os = "linux")]
    {
        let deb_exists = glob::glob("src-tauri/target/debug/bundle/deb/*.deb")
            .unwrap()
            .next()
            .is_some();
        assert!(deb_exists, "Debian package not created");
    }
}
```

---

## 8. Pre-Commit Build Verification

### 8.1 Git Hook for Build Tests

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running build configuration tests..."

# Run build config tests
cargo test --test build_config_test --manifest-path src-tauri/Cargo.toml
if [ $? -ne 0 ]; then
    echo "❌ Build configuration tests failed"
    exit 1
fi

# Validate tauri.conf.json
echo "Validating tauri.conf.json..."
jq empty src-tauri/tauri.conf.json
if [ $? -ne 0 ]; then
    echo "❌ tauri.conf.json is not valid JSON"
    exit 1
fi

# Check for version consistency
PACKAGE_VERSION=$(jq -r '.version' package.json)
TAURI_VERSION=$(jq -r '.package.version' src-tauri/tauri.conf.json)
CARGO_VERSION=$(grep '^version = ' src-tauri/Cargo.toml | head -1 | sed 's/version = "\(.*\)"/\1/')

if [ "$PACKAGE_VERSION" != "$TAURI_VERSION" ] || [ "$PACKAGE_VERSION" != "$CARGO_VERSION" ]; then
    echo "❌ Version mismatch:"
    echo "   package.json: $PACKAGE_VERSION"
    echo "   tauri.conf.json: $TAURI_VERSION"
    echo "   Cargo.toml: $CARGO_VERSION"
    exit 1
fi

echo "✅ All build verification checks passed"
```

---

## 9. Test Organization Structure

```
project/
├── src-tauri/
│   ├── tests/
│   │   ├── build_config_test.rs       # Build configuration tests
│   │   ├── platform_specific_test.rs  # Platform-specific tests
│   │   └── integration_test.rs        # Full build integration tests
│   ├── Cargo.toml
│   └── tauri.conf.json
├── tests/
│   ├── frontend/
│   │   ├── build.test.ts              # Frontend build tests
│   │   └── bundle.test.ts             # Bundle size tests
│   └── e2e/
│       └── app.test.ts                # End-to-end tests
└── scripts/
    └── verify-builds.sh                # Build verification script
```

---

## 10. Testing Checklist

### Phase 1: Before Writing Code
- [ ] Write test for build configuration requirement
- [ ] Test fails (Red)
- [ ] Document expected behavior in test

### Phase 2: During Implementation
- [ ] Write minimum code to pass test
- [ ] Test passes (Green)
- [ ] Refactor if needed while keeping tests passing

### Phase 3: Before Committing
- [ ] All build configuration tests pass
- [ ] All frontend tests pass
- [ ] Lint checks pass
- [ ] Build succeeds on local platform
- [ ] Version numbers consistent across files
- [ ] Icons exist for all platforms
- [ ] Configuration files are valid JSON/TOML

### Phase 4: CI/CD Verification
- [ ] Tests pass on all platforms (Windows, macOS, Linux)
- [ ] Builds succeed on all platforms
- [ ] Build artifacts created correctly
- [ ] No test failures or warnings

---

## 11. Quick Reference Commands

```bash
# Run all Rust tests
cargo test --manifest-path src-tauri/Cargo.toml

# Run specific test file
cargo test --test build_config_test

# Run frontend tests
npm test

# Run linter
npm run lint

# Run integration tests (ignored by default)
cargo test -- --ignored

# Test build process (debug mode)
npm run tauri build -- --debug

# Verify all builds
./scripts/verify-builds.sh

# Pre-commit hook
.git/hooks/pre-commit
```

---

## Summary

**TDD for Cross-Platform Builds**:
1. ✅ Write tests for build configurations before implementing
2. ✅ Test platform-specific features conditionally
3. ✅ Verify icons, configs, and dependencies in tests
4. ✅ Run tests on all platforms in CI/CD
5. ✅ Use pre-commit hooks for quick feedback
6. ✅ Maintain version consistency across files
7. ✅ Test full build process end-to-end
8. ✅ Validate artifacts are created correctly

**Remember**: Tests catch configuration errors before they break production builds!
