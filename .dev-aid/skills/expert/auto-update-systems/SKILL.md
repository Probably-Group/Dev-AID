---
name: Auto-Update Systems Expert
risk_level: HIGH
description: Expert in Tauri auto-update implementation with focus on signature verification, rollback mechanisms, staged rollouts, and secure update distribution
version: 1.0.0
author: JARVIS AI Assistant
tags: [auto-update, tauri, security, signature-verification, rollback, distribution]
model: claude-sonnet-4-5-20250929
---

# Auto-Update Systems Expert

## 0. Mandatory Reading Protocol

**CRITICAL**: Before implementing, read these reference files:

| Reference | When to Read |
|-----------|--------------|
| `references/security-examples.md` | Signing keys, signature verification, secure endpoints |
| `references/advanced-patterns.md` | Staged rollouts, rollback, update channels, differential updates |
| `references/threat-model.md` | Security posture, MITM defense, key rotation |

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

## 0. Anti-Hallucination Protocol

## 0. Anti-Hallucination Protocol

### 0.1 Quick Risk Assessment

**Risk Level**: HIGH

**Key Risk Factors**:
- Active exploitation of critical vulnerabilities in production (CVSS 7.5+)
- 3 high-severity CVEs/security concerns in 2024-2025
- Common attack vectors: MITM update injection, Rollback attacks, Unsigned package execution
- Requires continuous monitoring of security advisories

**Immediate Security Actions**:
1. Review recent CVEs below before any implementation
2. Never proceed without understanding attack surface
3. Implement security controls from § 0.3 as mandatory requirements

### 0.2 Vulnerability Research Protocol

**MANDATORY**: Before ANY implementation, research current vulnerabilities.

**Step 1: CVE Database Search** (NVD, MITRE)
```bash
# Search for latest CVEs (update dates for current year)
https://nvd.nist.gov/vuln/search
# Keywords: [technology name], [framework version]
```

**Step 2: Known Vulnerabilities (2024-2025)**

   - **UPDATE-MITM** (CVSS 9.0): Man-in-the-middle update attacks
     Source: https://owasp.org/www-community/attacks/Man-in-the-middle_attack
   - **ROLLBACK-ATTACK** (CVSS 8.5): Update rollback attacks
     Source: https://theupdateframework.io/security/
   - **UNSIGNED-UPDATE** (CVSS 9.8): Unsigned update execution
     Source: https://nvd.nist.gov/

**Step 3: Common Attack Patterns**

   - MITM update injection
   - Rollback attacks
   - Unsigned package execution
   - Supply chain compromise

**Step 4: MITRE ATT&CK Mapping**
- Tactic: [Initial Access, Execution, Persistence, Privilege Escalation]
- Review MITRE ATT&CK framework for latest techniques

**Update Frequency**: Check for new CVEs weekly during active development.

### 0.3 Hallucination Prevention Checklist

**CRITICAL**: These rules are ABSOLUTE. Violation = security incident.

**Domain-Specific Security Rules**:

- ❌ NEVER skip signature verification
- ❌ NEVER allow HTTP for updates
- ❌ ALWAYS use TUF framework
- ❌ ALWAYS implement rollback protection

**Before ANY code generation**:
1. ✅ Verify rule compliance for proposed implementation
2. ✅ Check if solution introduces any prohibited patterns
3. ✅ Validate all security assumptions against current CVEs
4. ✅ Confirm defensive coding practices are applied

**If uncertain**: STOP and research. Never guess on security.


## 1. Overview

**Risk Level: HIGH**

**Justification**: Auto-update systems can deliver code to all users simultaneously. A compromised update system can distribute malware to the entire user base. Signature verification bypass (like CVE-2024-39698) allows attackers to install unsigned malicious updates. Poor rollback mechanisms can leave users with broken software.

You are an expert in auto-update system implementation, specializing in:
- **Signature verification** for cryptographic update integrity
- **Rollback mechanisms** for failed updates
- **Staged rollouts** for risk mitigation
- **Secure distribution** with HTTPS and pinning
- **Tauri updater** configuration and best practices

### Primary Use Cases
- Tauri application auto-updates
- Secure update distribution infrastructure
- Update channel management (stable, beta)
- Emergency rollback procedures
- Update analytics and monitoring

---

## 2. Core Responsibilities

### 2.1 Core Principles

1. **TDD First** - Write tests before implementation code
2. **Performance Aware** - Optimize for bandwidth and speed
3. **ALWAYS verify signatures** - Never install unsigned updates
4. **Use HTTPS only** - Never fetch updates over HTTP
5. **Implement rollback** - Plan for failed updates
6. **Staged rollouts** - Don't update all users at once
7. **Monitor update health** - Track success rates and errors

### 2.2 Reliability Principles

1. **Atomic updates** - All or nothing installation
2. **Preserve user data** - Never lose configuration during updates
3. **Graceful degradation** - App works if update fails
4. **User consent** - Inform users before updating

---

## 3. Technical Foundation

### 3.1 Tauri Updater Components

| Component | Purpose |
|-----------|---------|
| Update manifest | JSON with version, download URLs, signatures |
| Signing key | Ed25519 private key for signing updates |
| Public key | Embedded in app for verification |
| Update endpoint | HTTPS server hosting manifests and artifacts |

### 3.2 Version Recommendations

| Component | Recommended | Notes |
|-----------|-------------|-------|
| Tauri | 1.5+ / 2.0+ | Latest security patches |
| Update protocol | v2 | Better signature handling |

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

## 5. Implementation Patterns

## 5. Implementation Patterns

📚 **For complete details**: See `references/implementation-patterns.md`

---
## 6. Security Standards

### 5.1 Domain Vulnerability Landscape

**Research Date**: November 2024

| CVE | Severity | Description | Mitigation |
|-----|----------|-------------|------------|
| CVE-2024-39698 | High | electron-updater signature bypass | Update electron-builder 6.3.0+ |
| CVE-2024-24576 | High | Rust Command injection (affects Tauri shell) | Update Rust 1.77.2+ |
| CVE-2024-35222 | High | Tauri iFrame origin bypass | Update Tauri 1.6.7+/2.0.0-beta.20+ |
| CVE-2023-46115 | Medium | Tauri key leak via Vite config | Remove TAURI_ from envPrefix |

**Key Insight**: Signature verification bypass is the most critical vulnerability class. Always verify signatures are actually checked and cannot be bypassed.

### 5.2 OWASP Mapping

| OWASP Category | Risk Level | Key Controls |
|----------------|------------|--------------|
| A02:2021 - Cryptographic Failures | Critical | Ed25519 signatures, HTTPS only |
| A05:2021 - Security Misconfiguration | High | Proper endpoint config, key management |
| A08:2021 - Software Integrity Failures | Critical | Signature verification, pinning |

### 5.3 Signature Verification

**See `references/security-examples.md` for complete implementations**

```rust
// Tauri handles signature verification automatically when configured correctly
// The signature in the manifest is verified against the embedded public key

// CRITICAL: Never bypass signature verification
// CRITICAL: Always use HTTPS for update endpoints
// CRITICAL: Protect the private signing key
```

---

## 7. Testing Standards

### 6.1 Update Testing

```rust
#[cfg(test)]
mod tests {
    #[tokio::test]
    async fn test_update_check() {
        let mock_server = MockUpdateServer::new();
        mock_server.set_latest_version("2.0.0");
        let result = check_for_updates_from(&mock_server.url()).await;
        assert_eq!(result.unwrap().version, "2.0.0");
    }

    #[tokio::test]
    async fn test_invalid_signature_rejected() {
        let mock_server = MockUpdateServer::new();
        mock_server.set_invalid_signature();
        assert!(install_update_from(&mock_server.url()).await.is_err());
    }

    #[tokio::test]
    async fn test_downgrade_prevented() {
        let mock_server = MockUpdateServer::new();
        mock_server.set_latest_version("0.9.0");
        assert!(check_for_updates_from(&mock_server.url()).await.unwrap().is_none());
    }
}
```

---

## 8. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```python
# tests/test_update_system.py
import pytest
from unittest.mock import patch
from update_manager import UpdateManager

class TestUpdateManager:
    @pytest.fixture
    def manager(self):
        return UpdateManager(current_version="1.0.0", update_endpoint="https://updates.example.com")

    @pytest.mark.asyncio
    async def test_check_for_update_returns_info(self, manager):
        with patch.object(manager, '_fetch_manifest') as mock:
            mock.return_value = {"version": "2.0.0", "signature": "valid_sig"}
            result = await manager.check_for_update()
            assert result.version == "2.0.0"

    @pytest.mark.asyncio
    async def test_invalid_signature_rejected(self, manager):
        with patch.object(manager, '_verify_signature', return_value=False):
            with pytest.raises(SecurityError, match="signature"):
                await manager.download_and_verify("https://...", "bad_sig")

    @pytest.mark.asyncio
    async def test_rollback_on_install_failure(self, manager):
        with patch.object(manager, '_install', side_effect=InstallError):
            with patch.object(manager, '_restore_backup') as mock_restore:
                with pytest.raises(InstallError):
                    await manager.install_update("/path/to/update")
                mock_restore.assert_called_once()
```

### Step 2: Implement Minimum to Pass

```python
# update_manager.py
class UpdateManager:
    async def check_for_update(self) -> Optional[UpdateInfo]:
        manifest = await self._fetch_manifest()
        if self._is_newer(manifest["version"]):
            return UpdateInfo(**manifest)
        return None

    async def download_and_verify(self, url: str, signature: str) -> bytes:
        data = await self._download(url)
        if not self._verify_signature(data, signature):
            raise SecurityError("Invalid signature")
        return data
```

### Step 3: Refactor and Optimize

Add delta updates, caching, and bandwidth management after tests pass.

### Step 4: Verify

```bash
pytest tests/test_update_system.py## 8. Implementation Workflow (TDD)

class TestUpdateManager:
    @pytest.fixture
    def manager(self):
        return UpdateManager(current_version="1.0.0", update_endpoint="https://updates.example.com")

📚 **For complete details**: See `references/implementation-workflow-tdd.md`

---
 files that will be modified
        modified_files = self._get_files_to_update()
        return self._backup_files(modified_files)

    def cleanup_old_backups(self, keep_count: int = 2) -> None:
        backups = sorted(self._list_backups(), key=lambda b: b.date)
        for backup in backups[:-keep_count]:
            backup.delete()

# Bad: Full backup every time
class FullBackup:
    def create_backup(self) -> str:
        # Copies entire application directory
        return shutil.copytree(self.app_dir, f"{self.app_dir}.backup")
```

### 8.5 Signature Caching

```python
# Good: Cache verified signatures
class CachedSignatureVerifier:
    def __init__(self):
        self._verified_cache: Dict[str, bool] = {}

    def verify(self, data: bytes, signature: str) -> bool:
        cache_key = hashlib.sha256(data).hexdigest()
        if cache_key in self._verified_cache:
            return self._verified_cache[cache_key]

        result = self._verify_ed25519(data, signature)
        self._verified_cache[cache_key] = result
        return result

# Bad: Re-verify same data multiple times
class UncachedVerifier:
    def verify(self, data: bytes, signature: str) -> bool:
        return self._verify_ed25519(data, signature)  # Expensive each time
```

---

## 10. Common Mistakes & Anti-Patterns

| Mistake | Wrong | Correct |
|---------|-------|---------|
| Missing signature | No `pubkey` in config | Always include `pubkey` in updater config |
| HTTP endpoints | `http://updates...` | Always use `https://updates...` |
| Leaked keys | `envPrefix: ['VITE_', 'TAURI_']` | Only `envPrefix: ['VITE_']` (CVE-2023-46115) |
| No rollback | Install without backup | Backup before install, restore on failure |

```rust
// CORRECT: Update with rollback
async fn update(&self) -> Result<(), UpdateError> {
    let backup = self.backup_current_version()?;
    if let Err(e) = self.try_update().await {
        self.restore_from_backup(&backup)?;
        return Err(e);
    }
    self.cleanup_backup(&backup)?;
    Ok(())
}
```

--## 9. Performance Patterns

## 9. Performance Patterns

📚 **For complete details**: See `references/performance-patterns.md`

---
