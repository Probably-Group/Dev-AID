# Security Auditing Skill

---
name: security-auditing
version: 1.0.0
domain: security/compliance
risk_level: HIGH
languages: [python, go, typescript]
frameworks: [structlog, opentelemetry, falco]
requires_security_review: true
compliance: [GDPR, HIPAA, PCI-DSS, SOC2, ISO27001]
last_updated: 2025-01-15
---

> **MANDATORY READING PROTOCOL**: Before implementing audit logging, read `references/advanced-patterns.md` for tamper-evident patterns and `references/threat-model.md` for log integrity attacks.

## 0. Anti-Hallucination Protocol

## 0. Anti-Hallucination Protocol

### 0.1 Quick Risk Assessment

**Risk Level**: MEDIUM

**Key Risk Factors**:
- Active exploitation of critical vulnerabilities in production (CVSS 7.5+)
- 3 high-severity CVEs/security concerns in 2024-2025
- Common attack vectors: Log injection, Audit bypass, SIEM evasion
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

   - **LOG-INJECTION** (CVSS 7.5): Log injection attacks
     Source: https://owasp.org/
   - **AUDIT-BYPASS** (CVSS 8.0): Audit trail manipulation
     Source: https://nvd.nist.gov/
   - **SIEM-EVASION** (CVSS N/A): SIEM evasion techniques
     Source: https://attack.mitre.org/

**Step 3: Common Attack Patterns**

   - Log injection
   - Audit bypass
   - SIEM evasion
   - Log tampering

**Step 4: MITRE ATT&CK Mapping**
- Tactic: [Initial Access, Execution, Persistence, Privilege Escalation]
- Review MITRE ATT&CK framework for latest techniques

**Update Frequency**: Check for new CVEs weekly during active development.

### 0.3 Hallucination Prevention Checklist

**CRITICAL**: These rules are ABSOLUTE. Violation = security incident.

**Domain-Specific Security Rules**:

- ❌ NEVER skip log validation
- ❌ NEVER trust logs without integrity checks
- ❌ ALWAYS implement tamper-proof logging
- ❌ ALWAYS validate audit trails

**Before ANY code generation**:
1. ✅ Verify rule compliance for proposed implementation
2. ✅ Check if solution introduces any prohibited patterns
3. ✅ Validate all security assumptions against current CVEs
4. ✅ Confirm defensive coding practices are applied

**If uncertain**: STOP and research. Never guess on security.



**🚨 MANDATORY: Read before implementing any security auditing code**

### Verification Requirements

When using this skill to implement security auditing features, you MUST:

1. **Verify Before Implementing**
   - ✅ Check official security standards (OWASP, NIST, CIS)
   - ✅ Confirm cryptographic algorithms are current and secure
   - ✅ Validate compliance requirements against official regulations
   - ❌ Never guess security configurations
   - ❌ Never invent cryptographic methods
   - ❌ Never assume compliance requirements without verification

2. **Use Available Tools**
   - 🔍 Read: Check existing security implementations
   - 🔍 Grep: Search for similar audit logging patterns
   - 🔍 WebSearch: Verify security standards and best practices
   - 🔍 WebFetch: Read official compliance documentation

3. **Verify if Certainty < 80%**
   - If uncertain about ANY security feature/config/pattern
   - STOP and verify before implementing
   - Document verification source in response
   - Errors in security auditing can cause: compliance violations, evidence loss, security breaches, legal liability

4. **Common Security Auditing Hallucination Traps** (AVOID)
   - ❌ Invented cryptographic signature schemes
   - ❌ Made-up compliance requirements (e.g., fake GDPR articles)
   - ❌ Non-existent SIEM integration formats
   - ❌ Incorrect log retention policies
   - ❌ Fabricated CVE numbers or severity ratings
   - ❌ Imaginary tamper-evident log verification methods

### Self-Check Checklist

Before EVERY response with security auditing code:
- [ ] All cryptographic operations verified against official standards
- [ ] Compliance requirements verified against actual regulations
- [ ] SIEM integration formats verified against vendor documentation
- [ ] Can cite official security standards and documentation sources

**⚠️ CRITICAL**: Security auditing code with hallucinated patterns causes compliance failures, legal liability, and evidence inadmissibility. Always verify.

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

## 1. Overview

### 1.1 Purpose and Scope

This skill provides security auditing and compliance capabilities:

- **Tamper-Evident Logging**: Cryptographically signed audit trails
- **SIEM Integration**: Forward events to security monitoring systems
- **Vulnerability Assessment**: Automated security scanning and reporting
- **Compliance Reporting**: Generate audit reports for regulations

### 1.2 Risk Assessment

**Risk Level**: HIGH

**Justification**:
- Audit logs are evidence in incident investigations
- Log tampering hides attacker activity
- Compliance violations result in legal penalties
- Missing logs = blind spots in security monitoring

**Attack Surface**:
- Log injection attacks
- Log tampering/deletion
- SIEM misconfiguration
- Sensitive data in logs (PII leakage)
- Log storage exhaustion

## 2. Core Responsibilities

### 2.1 Primary Functions

1. **Generate tamper-evident audit logs** for security events
2. **Forward events to SIEM** for correlation and alerting
3. **Assess vulnerabilities** through automated scanning
4. **Produce compliance reports** for regulatory requirements
5. **Detect anomalies** in user behavior and system activity

### 2.2 Core Principles

- **TDD First**: Write tests for security checks before implementation
- **Performance Aware**: Use incremental scanning and caching for efficiency
- **NEVER** log sensitive data (passwords, PII, secrets)
- **NEVER** trust log data without integrity verification
- **ALWAYS** use structured logging (JSON)
- **ALWAYS** include correlation IDs for request tracing
- **ALWAYS** protect logs from unauthorized modification

## 3. Technology Stack

| Component | Recommended | Purpose |
|-----------|-------------|---------|
| Structured Logging | `structlog` (Python) | JSON log generation |
| Log Aggregation | Elasticsearch, Loki | Centralized storage |
| SIEM | Splunk, QRadar, Sentinel | Security monitoring |
| Integrity | Signed logs, WORM storage | Tamper evidence |
| Compliance | OpenSCAP, Prowler, Trivy | Assessment tools |


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

### 4.1 Tamper-Evident Audit Logging (Summary)

```python
import hashlib
import hmac
import json
from datetime import datetime, timezone

class TamperEvidentLogger:
    """Audit logger with cryptographic integrity protection."""

    def __init__(self, signing_key: bytes, output_path: str):
        self._key = signing_key
        self._path = output_path
        self._sequence = 0
        self._previous_hash = b'\x00' * 32

    def log(self, event: str, actor: str = None, **context) -> dict:
        """Log a tamper-evident audit entry."""
        self._sequence += 1

        entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'sequence': self._sequence,
            'event': event,
            'actor': actor,
            'context': context,
            'previous_hash': self._previous_hash.hex(),
        }

        # Calculate and sign
        entry_bytes = json.dumps(entry, sort_keys=True).encode()
        entry['hash'] = hashlib.sha256(entry_bytes).hexdigest()
        entry['signature'] = hmac.new(
            self._key, entry_bytes, hashlib.sha256
        ).hexdigest()

        self._previous_hash = bytes.fromhex(entry['hash'])

        with open(self._path, 'a') as f:
            f.write(json.dumps(entry) + '\n')

        return entry
```

**📚 For complete implementation** (verification, chain validation):
- See `references/advanced-patterns.md`

### 4.2 Structured Security Logging

```python
import structlog

logger = structlog.get_logger()

class SecurityAuditLogger:
    """Security-focused audit logging."""

    @staticmethod
    def log_authentication(user_id: str, success: bool, method: str, ip: str):
        """Log authentication attempt."""
        logger.info(
            "auth.attempt",
            user_id=user_id,  # Never log email for privacy
            success=success,
            method=method,
            ip_address=ip
        )

    @staticmethod
    def log_authorization(user_id: str, resource: str, action: str, allowed: bool):
        """Log authorization decision."""
        logger.info(
            "authz.decision",
            user_id=user_id,
            resource=resource,
            action=action,
            allowed=allowed
        )

    @staticmethod
    def log_data_access(user_id: str, resource_type: str, resource_id: str, action: str):
        """Log data access for compliance."""
        logger.info(
            "data.access",
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action
        )
```

**📚 For complete patterns** (decorators, context managers, SIEM integration):
- See `references/security-examples.md`

### 4.3 SIEM Integration (CEF Format)

```python
class SIEMForwarder:
    def _to_cef(self, event: dict) -> str:
        """Convert event to CEF format for SIEM ingestion."""
        severity = self._map_severity(event.get('level', 'INFO'))
        return (f"CEF:0|JARVIS|SecurityAudit|1.0|{event.get('event', 'unknown')}|"
                f"{event.get('event', 'Unknown Event')}|{severity}|"
                f"src={event.get('ip_address', '')} suser={event.get('user_id', '')}")
```

**📚 For full SIEM implementation**: See `references/security-examples.md#siem-integration`

### 4.4 Vulnerability Assessment

```python
from dataclasses import dataclass
from typing import List

@dataclass
class Vulnerability:
    id: str
    severity: str
    package: str
    fixed_version: str

class VulnerabilityScanner:
    def scan_dependencies(self, path: str) -> List[Vulnerability]:
        """Scan dependencies using pip-audit, trivy for containers."""
        pass
```

**📚 For complete scanner**: See `references/advanced-patterns.md#vulnerability-assessment`

## 6. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```python
import pytest
from security_auditing import TamperEvidentLogger, SecurityAuditLogger

class TestTamperEvidentLogger:
    def test_log_entry_contains_required_fields(self, tmp_path):
        """Each log entry must have timestamp, sequence, hash, signature."""
        logger = TamperEvidentLogger(b'test-key', str(tmp_path / 'audit.log'))
        entry = logger.log("user.login", actor="user123")
        assert all(k in entry for k in ['timestamp', 'sequence', 'hash', 'signature'])

    def test_chain_integrity_detects_tampering(self, tmp_path):
        """Tampered logs must be detected via chain validation."""
        log_path = tmp_path / 'audit.log'
        logger = TamperEvidentLogger(b'test-key', str(log_path))
        logger.log("event1", actor="user1")

        # Tamper with log file
        tampered = log_path.read_text().replace('"event1"', '"TAMPERED"')
        log_path.write_text(tampered)

        valid, errors = logger.verify_chain()
        assert not valid and len(errors) > 0

    def test_no_pii_in_log_output(self, tmp_path):
        """PII patterns must not appear in logs."""
        import re
        log_path = tmp_path / 'audit.log'
        logger = SecurityAuditLogger(str(log_path))
        logger.log_authentication(user_id="user123", success=True, method="password", ip="192.168.1.1")
        content = log_path.read_text()
        assert not re.search(r'[\w\.-]+@[\w\.-]+', content)  # No emails
```

### Step 2: Implement Minimum to Pass

```python
# Implement only what's needed to pass the tests
class TamperEvidentLogger:
    def __init__(self, signing_key: bytes, output_path: str):
        self._key, self._path = signing_key, output_path
        self._sequence, self._previous_hash = 0, b'\x00' * 32

    def log(self, event: str, actor: str = None, **context) -> dict:
        self._sequence += 1
        entry = {'timestamp': datetime.now(timezone.utc).isoformat(),
                 'sequence': self._sequence, 'event': event, 'actor': actor}
        # Add hash and signature...
        return entry
```

### Step 3: Refactor Following Patterns

After tests pass, refactor for better error handling, performance optimizations, and security hardening.

### Step 4: Run Full Verification

```bash
pytest tests/security_auditing/ -v --tb=short
pytest tests/security_auditing/ --cov=security_auditing --cov-report=term-missing
```

## 7. Performance Patterns

**Key Principles**:
- Use incremental scanning (only scan changed files)
- Cache scan results and vulnerability data
- Parallelize multi-project scans
- Set resource limits to prevent exhaustion

**📚 For detailed performance patterns**:
- See `references/performance-patterns.md` for complete implementations

## 8. Security Standards

### 7.1 Known Vulnerabilities

| CVE | Severity | Component | Mitigation |
|-----|----------|-----------|------------|
| CVE-2023-50960 | Critical | QRadar | Command injection - Update QRadar |
| CVE-2023-50961 | High | QRadar | Stored XSS - Update QRadar |
| CVE-2023-2976 | Medium | Guava | File exposure - Update to 32.0+ |
| CVE-2024-22365 | Medium | PAM | DoS - Update Linux PAM |
| CVE-2023-22875 | Medium | QRadar | Info disclosure - Update |

### 7.2 OWASP Mapping

| OWASP 2025 | Risk | Implementation |
|------------|------|----------------|
| A09: Security Logging Failures | Critical | Tamper-evident logs, SIEM forwarding |
| A05: Security Misconfiguration | High | Log protection, retention policies |
| A01: Broken Access Control | High | Log access auditing |

**📚 For detailed OWASP guidance**:
- See `references/security-examples.md#owasp-coverage`

### 7.3 Compliance Requirements

- **GDPR Article 30**: Records of processing activities
- **HIPAA 164.312(b)**: Audit controls
- **PCI-DSS 10**: Track all access to network resources
- **SOC2 CC7.2**: Monitor system components

## 9. Testing Requirements

```python
def test_log_integrity_tamper_detection(audit_logger):
    """Tampered logs must be detected."""
    audit_logger.log("test.event", actor="user1")

    # Tamper and verify detection
    valid, errors = audit_logger.verify_chain()
    assert not valid

def test_no_pii_in_logs(audit_logger):
    """PII must not appear in logs."""
    # Check for email, phone, SSN patterns in log output
    pass
```

**📚 For complete test suite**:
- See `references/security-examples.md#testing`

## 10. Common Mistakes

**Critical Anti-Patterns to Avoid**:
- ❌ Logging passwords, tokens, or PII
- ❌ Unprotected logs without integrity verification
- ❌ Missing correlation IDs for request tracing
- ❌ World-readable log files (use `chmod 600`)
- ❌ Synchronous SIEM forwarding (blocks on failure)

**📚 For complete anti-patterns catalog**: See `references/anti-patterns.md`

## 11. Pre-Implementation Checklist

**Three Phases**:
1. **Before Code**: Read threat model, identify compliance needs, design format, plan SIEM integration
2. **During Implementation**: Structured logging, tamper-evident signing, no PII, correlation IDs, performance patterns
3. **Before Committing**: Tests pass, log protection verified, SIEM tested, retention policies enforced

**📚 For complete checklists**: See `references/audit-checklists.md` (includes GDPR, HIPAA, PCI-DSS, SOC2, ISO27001 compliance checklists)

## 12. Summary

### Key Objectives

1. **Tamper-evident logs**: Cryptographic signing and chaining
2. **Centralized monitoring**: SIEM integration for all events
3. **Compliance ready**: Meet GDPR, HIPAA, PCI-DSS requirements
4. **Privacy protection**: No PII/secrets in logs

### References

**Core Documentation**:
- `references/advanced-patterns.md` - Full implementations, WORM storage, chain verification
- `references/security-examples.md` - SIEM configs, compliance reports, testing examples
- `references/threat-model.md` - Log integrity attack scenarios, threat analysis

**Specialized Guides**:
- `references/performance-patterns.md` - Optimization strategies (caching, incremental scanning, parallelization)
- `references/anti-patterns.md` - Common mistakes and how to avoid them
- `references/audit-checklists.md` - Implementation checklists for GDPR, HIPAA, PCI-DSS, SOC2, ISO27001

---

**If it's not logged, it didn't happen. If logs can be tampered, you can't prove anything.**
