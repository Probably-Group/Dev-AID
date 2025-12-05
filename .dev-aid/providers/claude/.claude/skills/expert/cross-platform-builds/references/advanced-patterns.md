# Advanced Cross-Platform Build Patterns

This document covers advanced techniques, complex build configurations, and expert-level patterns for cross-platform desktop application development.

---

## 1. Advanced Platform Detection

### 1.1 Runtime Platform Detection

```rust
use std::env;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Platform {
    Windows,
    MacOS,
    Linux,
}

impl Platform {
    pub fn current() -> Self {
        #[cfg(target_os = "windows")]
        return Platform::Windows;

        #[cfg(target_os = "macos")]
        return Platform::MacOS;

        #[cfg(target_os = "linux")]
        return Platform::Linux;
    }

    pub fn is_windows(&self) -> bool {
        matches!(self, Platform::Windows)
    }

    pub fn is_macos(&self) -> bool {
        matches!(self, Platform::MacOS)
    }

    pub fn is_linux(&self) -> bool {
        matches!(self, Platform::Linux)
    }

    pub fn name(&self) -> &'static str {
        match self {
            Platform::Windows => "Windows",
            Platform::MacOS => "macOS",
            Platform::Linux => "Linux",
        }
    }
}

// Usage
fn main() {
    let platform = Platform::current();
    println!("Running on: {}", platform.name());

    if platform.is_windows() {
        // Windows-specific initialization
    }
}
```

### 1.2 Architecture Detection

```rust
pub enum Architecture {
    X86_64,
    Aarch64,
    Other(String),
}

impl Architecture {
    pub fn current() -> Self {
        match env::consts::ARCH {
            "x86_64" => Architecture::X86_64,
            "aarch64" => Architecture::Aarch64,
            arch => Architecture::Other(arch.to_string()),
        }
    }

    pub fn is_arm(&self) -> bool {
        matches!(self, Architecture::Aarch64)
    }
}
```

---

## 2. Advanced Conditional Compilation

### 2.1 Feature-Based Platform Code

```rust
// Cargo.toml
[features]
default = []
windows-native = ["windows"]
macos-native = ["cocoa", "objc"]
linux-native = ["gtk", "gdk"]

// src/platform/mod.rs
#[cfg(feature = "windows-native")]
pub mod windows_impl;

#[cfg(feature = "macos-native")]
pub mod macos_impl;

#[cfg(feature = "linux-native")]
pub mod linux_impl;

// Unified interface
pub trait PlatformApi {
    fn show_notification(&self, title: &str, body: &str);
    fn set_app_icon(&self, icon_path: &str);
}

#[cfg(feature = "windows-native")]
pub fn create_platform() -> Box<dyn PlatformApi> {
    Box::new(windows_impl::WindowsPlatform::new())
}

#[cfg(feature = "macos-native")]
pub fn create_platform() -> Box<dyn PlatformApi> {
    Box::new(macos_impl::MacOSPlatform::new())
}

#[cfg(feature = "linux-native")]
pub fn create_platform() -> Box<dyn PlatformApi> {
    Box::new(linux_impl::LinuxPlatform::new())
}
```

### 2.2 Multi-Target Compilation Flags

```toml
# .cargo/config.toml

[target.x86_64-pc-windows-msvc]
rustflags = [
    "-C", "target-feature=+crt-static",
    "-C", "link-arg=/SUBSYSTEM:WINDOWS",
]

[target.x86_64-apple-darwin]
rustflags = [
    "-C", "link-arg=-mmacosx-version-min=10.15",
]

[target.aarch64-apple-darwin]
rustflags = [
    "-C", "link-arg=-mmacosx-version-min=11.0",
]

[target.x86_64-unknown-linux-gnu]
rustflags = [
    "-C", "link-arg=-Wl,--as-needed",
    "-C", "link-arg=-Wl,--gc-sections",
]
```

---

## 3. Advanced macOS Universal Binaries

### 3.1 Automated Universal Binary Creation

```bash
#!/bin/bash
# scripts/build-universal-macos.sh

set -e

APP_NAME="MyApp"
VERSION="1.0.0"

echo "Building universal macOS binary..."

# Build both architectures
echo "Building x86_64..."
cargo build --release --target x86_64-apple-darwin

echo "Building aarch64..."
cargo build --release --target aarch64-apple-darwin

# Create universal binary directory
mkdir -p target/universal-apple-darwin/release

# Create universal binary
echo "Creating universal binary..."
lipo -create \
  target/x86_64-apple-darwin/release/${APP_NAME} \
  target/aarch64-apple-darwin/release/${APP_NAME} \
  -output target/universal-apple-darwin/release/${APP_NAME}

# Verify
echo "Verifying universal binary..."
lipo -info target/universal-apple-darwin/release/${APP_NAME}

# Create app bundle
echo "Creating app bundle..."
mkdir -p "target/universal-apple-darwin/release/${APP_NAME}.app/Contents/MacOS"
mkdir -p "target/universal-apple-darwin/release/${APP_NAME}.app/Contents/Resources"

# Copy binary
cp target/universal-apple-darwin/release/${APP_NAME} \
   "target/universal-apple-darwin/release/${APP_NAME}.app/Contents/MacOS/"

# Create Info.plist
cat > "target/universal-apple-darwin/release/${APP_NAME}.app/Contents/Info.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>${APP_NAME}</string>
    <key>CFBundleIdentifier</key>
    <string>com.company.${APP_NAME}</string>
    <key>CFBundleName</key>
    <string>${APP_NAME}</string>
    <key>CFBundleVersion</key>
    <string>${VERSION}</string>
    <key>CFBundleShortVersionString</key>
    <string>${VERSION}</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
</dict>
</plist>
PLIST

echo "✅ Universal binary created successfully!"
```

### 3.2 Universal Binary with Different Optimizations

```bash
#!/bin/bash
# scripts/build-optimized-universal.sh

# Build Intel with specific optimizations
RUSTFLAGS="-C target-cpu=haswell" \
  cargo build --release --target x86_64-apple-darwin

# Build ARM with specific optimizations
RUSTFLAGS="-C target-cpu=apple-m1" \
  cargo build --release --target aarch64-apple-darwin

# Create universal binary
lipo -create \
  target/x86_64-apple-darwin/release/myapp \
  target/aarch64-apple-darwin/release/myapp \
  -output target/universal/myapp
```

---

## 4. Advanced Windows Installer Customization

### 4.1 Custom WiX Configuration

```xml
<!-- custom-installer.wxs -->
<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*" 
           Name="MyApp" 
           Language="1033" 
           Version="1.0.0" 
           Manufacturer="Company Name" 
           UpgradeCode="YOUR-GUID-HERE">
    
    <Package InstallerVersion="400" 
             Compressed="yes" 
             InstallScope="perMachine" />
    
    <!-- Major upgrade logic -->
    <MajorUpgrade 
      DowngradeErrorMessage="A newer version is already installed." 
      Schedule="afterInstallExecute" />
    
    <MediaTemplate EmbedCab="yes" />
    
    <!-- Custom install location -->
    <Property Id="WIXUI_INSTALLDIR" Value="INSTALLFOLDER" />
    
    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="ProgramFilesFolder">
        <Directory Id="INSTALLFOLDER" Name="MyApp">
          <Component Id="MainExecutable" Guid="YOUR-GUID-HERE">
            <File Id="MainExe" 
                  Source="target/release/myapp.exe" 
                  KeyPath="yes" />
            
            <!-- Desktop shortcut -->
            <Shortcut Id="DesktopShortcut" 
                      Directory="DesktopFolder" 
                      Name="MyApp" 
                      WorkingDirectory="INSTALLFOLDER" 
                      Icon="AppIcon.exe" 
                      IconIndex="0" />
            
            <!-- Start menu shortcut -->
            <Shortcut Id="StartMenuShortcut" 
                      Directory="ProgramMenuFolder" 
                      Name="MyApp" 
                      WorkingDirectory="INSTALLFOLDER" 
                      Icon="AppIcon.exe" 
                      IconIndex="0" />
          </Component>
        </Directory>
      </Directory>
      
      <Directory Id="DesktopFolder" Name="Desktop" />
      <Directory Id="ProgramMenuFolder" Name="Programs" />
    </Directory>
    
    <!-- Features -->
    <Feature Id="Complete" Level="1">
      <ComponentRef Id="MainExecutable" />
    </Feature>
    
    <!-- UI -->
    <UIRef Id="WixUI_InstallDir" />
    
    <!-- Icon -->
    <Icon Id="AppIcon.exe" SourceFile="icons/icon.ico" />
  </Product>
</Wix>
```

### 4.2 Auto-Update Configuration (Windows)

```json
// tauri.conf.json
{
  "tauri": {
    "updater": {
      "active": true,
      "endpoints": [
        "https://releases.myapp.com/{{target}}/{{current_version}}"
      ],
      "dialog": true,
      "pubkey": "YOUR_PUBLIC_KEY_HERE"
    }
  }
}
```

```rust
// src-tauri/src/main.rs
use tauri::updater::UpdaterBuilder;

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            #[cfg(not(debug_assertions))]
            {
                let handle = app.handle();
                tauri::async_runtime::spawn(async move {
                    match UpdaterBuilder::new(&handle)
                        .build()
                        .unwrap()
                        .check()
                        .await
                    {
                        Ok(Some(update)) => {
                            println!("Update available: {}", update.version);
                            update.download_and_install().await.ok();
                        }
                        Ok(None) => println!("No updates available"),
                        Err(e) => eprintln!("Update check failed: {}", e),
                    }
                });
            }
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

---

## 5. Advanced Linux Packaging

### 5.1 Custom Debian Package

```bash
#!/bin/bash
# scripts/build-debian.sh

APP_NAME="myapp"
VERSION="1.0.0"
ARCH="amd64"

# Build binary
cargo build --release --target x86_64-unknown-linux-gnu

# Create package structure
mkdir -p debian-package/DEBIAN
mkdir -p debian-package/usr/bin
mkdir -p debian-package/usr/share/applications
mkdir -p debian-package/usr/share/pixmaps

# Copy binary
cp target/x86_64-unknown-linux-gnu/release/${APP_NAME} \
   debian-package/usr/bin/

# Create control file
cat > debian-package/DEBIAN/control << EOF
Package: ${APP_NAME}
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: ${ARCH}
Depends: libgtk-3-0, libwebkit2gtk-4.0-37
Maintainer: Your Name <your.email@example.com>
Description: My awesome application
 A longer description of the application
 that spans multiple lines.
