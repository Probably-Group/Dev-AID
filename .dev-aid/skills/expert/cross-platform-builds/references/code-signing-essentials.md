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

