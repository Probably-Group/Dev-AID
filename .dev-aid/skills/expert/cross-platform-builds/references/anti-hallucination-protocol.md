## 0. Anti-Hallucination Protocol

**CRITICAL**: Before implementing ANY platform-specific build configuration, you MUST read the relevant reference files.

### Trigger Conditions for Reference Files

**Read `references/build-patterns.md` WHEN**:
- Configuring GitHub Actions build matrices
- Setting up Tauri configuration for multi-platform builds
- Creating platform-specific installers (MSI, DMG, DEB, AppImage)
- Implementing CI/CD workflows

**Read `references/security-examples.md` WHEN**:
- Setting up code signing certificates (Windows, macOS, Linux)
- Configuring notarization for macOS
- Implementing secure build environments
- Managing signing credentials in CI/CD
- Verifying signatures before distribution

**Read `references/performance-optimization.md` WHEN**:
- Optimizing build times (incremental builds, caching)
- Reducing bundle sizes (LTO, tree-shaking)
- Improving application startup time
- Configuring fast linkers (mold, lld)

**Read `references/anti-patterns.md` WHEN**:
- Encountering build failures or platform-specific errors
- Setting up cross-platform path handling
- Implementing platform-specific features
- Debugging code signing or notarization issues

**Read `references/testing-guide.md` WHEN**:
- Writing tests for build configurations
- Setting up TDD workflow for builds
- Creating CI/CD test pipelines
- Validating build artifacts

**Read `references/advanced-patterns.md` WHEN**:
- Building macOS universal binaries
- Creating custom Windows installers with WiX
- Implementing auto-update functionality
- Advanced platform-specific optimizations

### Verification Requirements

When implementing cross-platform builds, you MUST:

1. **Verify Before Implementing**
   - Check official Tauri documentation for current configuration options
   - Confirm platform requirements against official docs
   - Validate certificate/signing procedures are current
   - Never guess configuration options
   - Never invent build commands
   - Never assume cross-platform compatibility without testing

2. **Use Available Tools**
   - Read: Check existing build configurations
   - Grep: Search for similar patterns in codebase
   - WebSearch: Verify against official Tauri/platform docs
   - WebFetch: Read official documentation when uncertain

3. **Verify if Certainty < 80%**
   - If uncertain about ANY build config, code signing, or platform feature
   - STOP and read relevant reference file
   - Document verification source in response
   - Errors in builds can cause failed releases, security warnings, or installation failures

4. **Common Cross-Platform Build Hallucination Traps** (AVOID)
   - Inventing Tauri configuration options
   - Making up code signing procedures
   - Assuming paths work the same on all platforms
   - Guessing platform dependency names
   - Confusing Windows/macOS/Linux build requirements

### Self-Check Checklist

Before EVERY response with cross-platform build code:
- [ ] All Tauri configuration options verified against current docs
- [ ] Platform-specific requirements verified (dependencies, certificates)
- [ ] Build commands verified against official Tauri CLI docs
- [ ] Code signing procedures verified for target platform
- [ ] Can cite official documentation sources

**CRITICAL**: Incorrect build configurations can cause failed releases, security warnings for users, or applications that won't install. Always verify against official documentation.

---


### 0.4 Progressive Disclosure (500-Line Limit)

**⚠️ CRITICAL**: This SKILL.md file MUST stay <500 lines for Claude Code to load it.

**If this file is approaching 500 lines**:
- Move detailed examples to `references/advanced-patterns.md`
- Move security examples to `references/security-examples.md`
- Move troubleshooting to `references/troubleshooting.md`
- Keep only summaries and links in main file

📚 **For complete progressive disclosure guide**: See `../../../template-references/progressive-disclosure.md`

---

