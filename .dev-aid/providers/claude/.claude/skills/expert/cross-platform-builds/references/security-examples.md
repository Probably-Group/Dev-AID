# Cross-Platform Build Security Examples

This document provides comprehensive examples of code signing, notarization, and security best practices for cross-platform desktop application builds.

---

## 1. Code Signing Requirements

### 1.1 Certificate Types by Platform

| Platform | Certificate Type | Purpose | Acquisition Time |
|----------|-----------------|---------|------------------|
| Windows | EV Code Signing | Immediate SmartScreen trust | 3-5 business days |
| Windows | Standard Code Signing | Trust after reputation | 1-2 business days |
| macOS | Developer ID Application | Distribution outside App Store | Immediate (with Apple Developer account) |
| macOS | Developer ID Installer | Signed PKG installers | Immediate (with Apple Developer account) |
| Linux | GPG Key | Package signing | Immediate (self-generated) |

### 1.2 Certificate Costs

- **Windows EV Code Signing**: $300-500/year (DigiCert, Sectigo)
- **Windows Standard Code Signing**: $100-200/year
- **macOS Developer Program**: $99/year (includes all certificates)
- **Linux GPG**: Free

---

## 2. Windows Code Signing

### 2.1 Tauri Configuration for Windows

```json
{
  "tauri": {
    "bundle": {
      "windows": {
        "certificateThumbprint": "YOUR_CERT_THUMBPRINT",
        "digestAlgorithm": "sha256",
        "timestampUrl": "http://timestamp.digicert.com",
        "wix": {
          "language": "en-US"
        }
      }
    }
  }
}
```

### 2.2 Finding Certificate Thumbprint

```powershell
# List all code signing certificates
Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert

# Get thumbprint for specific certificate
Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert | Where-Object { $_.Subject -like "*YourCompany*" } | Select-Object Thumbprint, Subject
```

### 2.3 Manual Windows Signing (signtool)

```bash
# Sign executable
signtool sign /tr http://timestamp.digicert.com /td sha256 /fd sha256 /a MyApp.exe

# Sign with specific certificate
signtool sign /sha1 YOUR_CERT_THUMBPRINT /tr http://timestamp.digicert.com /td sha256 /fd sha256 MyApp.exe

# Sign MSI installer
signtool sign /tr http://timestamp.digicert.com /td sha256 /fd sha256 /a MyApp.msi
```

### 2.4 Verifying Windows Signatures

```bash
# Verify signature
signtool verify /pa /v MyApp.exe

# Expected output:
# Signing Certificate Chain:
#     Issued to: DigiCert SHA2 Assured ID Code Signing CA
#     ...
# Successfully verified: MyApp.exe

# Check timestamp
signtool verify /pa /v MyApp.exe | findstr /i "timestamp"
```

### 2.5 Windows Signing in GitHub Actions

```yaml
- name: Import Windows Certificate
  if: matrix.platform == 'windows-latest'
  run: |
    echo "${{ secrets.WINDOWS_CERTIFICATE }}" | base64 --decode > cert.pfx
    certutil -f -p "${{ secrets.CERTIFICATE_PASSWORD }}" -importpfx cert.pfx
    Remove-Item cert.pfx

- name: Build and Sign
  run: npm run tauri build
  env:
    TAURI_SIGNING_PRIVATE_KEY: ${{ secrets.TAURI_PRIVATE_KEY }}
    TAURI_SIGNING_PASSWORD: ${{ secrets.TAURI_KEY_PASSWORD }}

- name: Verify Signature
  run: |
    $msi = Get-ChildItem -Path src-tauri\target\release\bundle\msi\*.msi | Select-Object -First 1
    signtool verify /pa /v $msi.FullName
```

---

## 3. macOS Code Signing

### 3.1 Tauri Configuration for macOS

```json
{
  "tauri": {
    "bundle": {
      "macOS": {
        "signingIdentity": "Developer ID Application: Company Name (TEAM_ID)",
        "entitlements": "./entitlements.plist",
        "minimumSystemVersion": "10.15"
      }
    }
  }
}
```

### 3.2 Creating macOS Certificates

```bash
# List available signing identities
security find-identity -v -p codesigning

# Expected output:
#   1) ABC123... "Developer ID Application: Company Name (TEAM_ID)"
#   2) DEF456... "Apple Development: developer@company.com (TEAM_ID)"
```

### 3.3 macOS Entitlements File

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- Required for JIT compilation (JavaScript engines) -->
    <key>com.apple.security.cs.allow-jit</key>
    <true/>

    <!-- Required for unsigned executable memory -->
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>

    <!-- Required for dynamic libraries -->
    <key>com.apple.security.cs.disable-library-validation</key>
    <true/>

    <!-- Network access (if needed) -->
    <key>com.apple.security.network.client</key>
    <true/>
    <key>com.apple.security.network.server</key>
    <true/>

    <!-- File access (if needed) -->
    <key>com.apple.security.files.user-selected.read-write</key>
    <true/>
</dict>
</plist>
```

### 3.4 Manual macOS Signing

```bash
# Sign app bundle with hardened runtime
codesign --sign "Developer ID Application: Company Name (TEAM_ID)" \
  --options runtime \
  --entitlements entitlements.plist \
  --force \
  --deep \
  MyApp.app

# Verify signature
codesign --verify --deep --strict MyApp.app

# Check if Gatekeeper accepts it
spctl --assess --type execute MyApp.app

# Expected output: MyApp.app: accepted
```

### 3.5 macOS Notarization

**Step 1: Create App-Specific Password**
1. Go to https://appleid.apple.com
2. Sign in with Apple ID
3. Generate app-specific password
4. Save it securely

**Step 2: Submit for Notarization**

```bash
# Create a zip for notarization
ditto -c -k --keepParent MyApp.app MyApp.zip

# Submit to notarization service
xcrun notarytool submit MyApp.zip \
  --apple-id "developer@company.com" \
  --password "app-specific-password" \
  --team-id "TEAM_ID" \
  --wait

# Expected output:
# Submission ID: abc123-def456-...
# Status: Accepted
```

**Step 3: Staple Notarization Ticket**

```bash
# Staple the ticket to the app
xcrun stapler staple MyApp.app

# Verify stapling
xcrun stapler validate MyApp.app

# Expected output: The validate action worked!
```

### 3.6 macOS Signing in GitHub Actions

```yaml
- name: Import macOS Certificate
  if: matrix.platform == 'macos-latest'
  run: |
    # Decode and import certificate
    echo "${{ secrets.MACOS_CERTIFICATE }}" | base64 --decode > certificate.p12

    # Create temporary keychain
    security create-keychain -p "${{ secrets.KEYCHAIN_PASSWORD }}" build.keychain
    security default-keychain -s build.keychain
    security unlock-keychain -p "${{ secrets.KEYCHAIN_PASSWORD }}" build.keychain

    # Import certificate
    security import certificate.p12 \
      -k build.keychain \
      -P "${{ secrets.CERTIFICATE_PASSWORD }}" \
      -T /usr/bin/codesign

    # Allow codesign to use the key
    security set-key-partition-list -S apple-tool:,apple:,codesign: \
      -s -k "${{ secrets.KEYCHAIN_PASSWORD }}" build.keychain

    # Clean up
    rm certificate.p12

- name: Build
  run: npm run tauri build -- --target ${{ matrix.target }}

- name: Notarize
  run: |
    # Find the DMG file
    DMG=$(find src-tauri/target/${{ matrix.target }}/release/bundle/dmg -name "*.dmg" | head -1)

    # Submit for notarization
    xcrun notarytool submit "$DMG" \
      --apple-id "${{ secrets.APPLE_ID }}" \
      --password "${{ secrets.APPLE_APP_PASSWORD }}" \
      --team-id "${{ secrets.APPLE_TEAM_ID }}" \
      --wait

    # Staple the ticket
    xcrun stapler staple "$DMG"

    # Verify
    xcrun stapler validate "$DMG"

- name: Cleanup Keychain
  if: always()
  run: |
    security delete-keychain build.keychain
```

---

## 4. Linux Package Signing

### 4.1 GPG Key Generation

```bash
# Generate GPG key
gpg --full-generate-key

# Choose:
# - Type: RSA and RSA
# - Size: 4096
# - Expiration: 2 years
# - Name: Company Name
# - Email: releases@company.com

# List keys
gpg --list-secret-keys --keyid-format LONG

# Export public key
gpg --armor --export releases@company.com > public-key.asc

# Export private key (for CI)
gpg --armor --export-secret-keys releases@company.com > private-key.asc
```

### 4.2 Signing Debian Packages

```bash
# Sign .deb package
dpkg-sig --sign builder myapp_1.0.0_amd64.deb

# Verify signature
dpkg-sig --verify myapp_1.0.0_amd64.deb
```

### 4.3 Signing AppImages

```bash
# Sign AppImage
gpg --detach-sign --armor MyApp.AppImage

# This creates MyApp.AppImage.asc

# Verify
gpg --verify MyApp.AppImage.asc MyApp.AppImage
```

### 4.4 Linux Signing in GitHub Actions

```yaml
- name: Import GPG Key
  if: matrix.platform == 'ubuntu-22.04'
  run: |
    echo "${{ secrets.GPG_PRIVATE_KEY }}" | base64 --decode | gpg --import
    echo "${{ secrets.GPG_PASSPHRASE }}" | gpg --batch --yes --passphrase-fd 0 --quick-add-uid

- name: Sign Packages
  run: |
    # Sign all .deb files
    for deb in src-tauri/target/release/bundle/deb/*.deb; do
      dpkg-sig --sign builder "$deb"
    done

    # Sign all AppImages
    for appimage in src-tauri/target/release/bundle/appimage/*.AppImage; do
      gpg --detach-sign --armor "$appimage"
    done
```

---

## 5. Build Security Checklist

### 5.1 Pre-Release Security Verification

- [ ] **Certificates**
  - [ ] Windows certificate is EV or has built reputation
  - [ ] macOS Developer ID certificate is valid
  - [ ] Linux GPG key is generated and secure

- [ ] **Signing**
  - [ ] All executables are signed
  - [ ] All installers are signed
  - [ ] Signatures use timestamping
  - [ ] Signatures verified before distribution

- [ ] **Credentials Management**
  - [ ] Certificates stored in CI/CD secrets only
  - [ ] No certificates in repository
  - [ ] Private keys encrypted
  - [ ] App-specific passwords used (not main password)

- [ ] **Build Environment**
  - [ ] Build happens on clean/ephemeral environment
  - [ ] Dependencies pinned and verified
  - [ ] Build logs don't expose secrets
  - [ ] Artifacts checksummed after signing

- [ ] **Distribution**
  - [ ] Windows SmartScreen passes
  - [ ] macOS Gatekeeper passes
  - [ ] Installer tested on clean systems
  - [ ] Auto-update URLs are HTTPS

### 5.2 Signing Best Practices

**DO:**
- ✅ Use timestamping on all signatures
- ✅ Sign on tagged releases only
- ✅ Verify signatures before publishing
- ✅ Keep certificates in secure CI secrets
- ✅ Use EV certificates for Windows (if possible)
- ✅ Notarize all macOS applications
- ✅ Test installers on clean systems
- ✅ Document signing procedures

**DON'T:**
- ❌ Commit certificates to repository
- ❌ Share signing credentials
- ❌ Sign debug builds
- ❌ Skip timestamping
- ❌ Use expired certificates
- ❌ Self-sign for production (Windows/macOS)
- ❌ Skip notarization (macOS)
- ❌ Reuse development certificates for production

---

## 6. Verification Commands Reference

### Windows Verification

```bash
# Verify signature
signtool verify /pa /v MyApp.exe

# Check certificate details
signtool verify /pa /v /d MyApp.exe

# Verify timestamp
signtool verify /pa /v MyApp.exe | findstr /i "timestamp"
```

### macOS Verification

```bash
# Verify code signature
codesign --verify --deep --strict MyApp.app

# Check Gatekeeper
spctl --assess --type execute MyApp.app

# Verify notarization
xcrun stapler validate MyApp.app

# Display signature details
codesign -dvv MyApp.app

# Check entitlements
codesign -d --entitlements - MyApp.app
```

### Linux Verification

```bash
# Verify .deb signature
dpkg-sig --verify myapp.deb

# Verify AppImage signature
gpg --verify MyApp.AppImage.asc MyApp.AppImage

# Check GPG signature details
gpg --verify --verbose MyApp.AppImage.asc
```

---

## 7. Troubleshooting Common Signing Issues

### Windows

**Problem**: SmartScreen warning appears
```
Solution: Use EV certificate or build reputation over time (100+ users)
```

**Problem**: "The digital signature of the object did not verify"
```
Solution: Ensure certificate is installed in Current User\Personal store
Check with: certutil -store -user My
```

**Problem**: Timestamp server unreachable
```
Solution: Try alternative timestamp servers:
- http://timestamp.digicert.com
- http://timestamp.sectigo.com
- http://timestamp.comodoca.com
```

### macOS

**Problem**: "App is damaged and can't be opened"
```
Solution:
1. Ensure app is signed with Developer ID
2. Notarize the application
3. Staple the notarization ticket
4. Verify: xcrun stapler validate MyApp.app
```

**Problem**: Notarization fails with "Invalid Code Signature"
```
Solution:
1. Sign with --options runtime
2. Include proper entitlements
3. Ensure all binaries in bundle are signed
4. Re-sign and re-submit
```

**Problem**: "No identity found"
```
Solution:
1. Download certificates from Apple Developer portal
2. Import into Keychain
3. Verify: security find-identity -v -p codesigning
```

### Linux

**Problem**: GPG verification fails
```
Solution:
1. Ensure GPG public key is distributed with package
2. Import key: gpg --import public-key.asc
3. Trust key: gpg --edit-key <key-id>, then: trust, 5, quit
```

---

## 8. Security Best Practices Summary

1. **Never commit signing credentials** - Use CI/CD secrets
2. **Always use timestamping** - Signatures remain valid after cert expires
3. **Verify before distributing** - Check signatures work correctly
4. **Use hardened runtime** - macOS apps with runtime hardening
5. **Test on clean systems** - Verify installers work for users
6. **Keep certificates secure** - Use hardware tokens for EV certs
7. **Rotate credentials regularly** - Update certificates before expiry
8. **Document procedures** - Ensure team knows signing process
9. **Monitor certificate expiry** - Set up alerts 30 days before expiry
10. **Audit signing logs** - Review who signs what and when
