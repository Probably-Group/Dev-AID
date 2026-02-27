---
name: security-auditing
version: 2.0.0
description: "Security audit methodology with vulnerability assessment, compliance checking, and remediation tracking. Use when conducting security audits, evaluating infrastructure compliance, or tracking remediation efforts. Do NOT use for application code review (use appsec-expert)."
risk_level: HIGH
token_budget: 4000
---
# Security Auditing - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.2 Security Patterns (security rules)

**CWE-778: Insufficient Logging**
- Do not: Skip logging for security events
- Instead: Log auth attempts, access control failures, input validation failures

**CWE-209: Error Information Leakage**
- Do not: Return stack traces or internal errors to users
- Instead: Generic error messages, detailed logs server-side

**CWE-523: Unprotected Transport**
- Do not: HTTP for any authenticated endpoint
- Instead: HTTPS, HSTS, secure cookies

**CWE-250: Excessive Privileges**
- Do not: Run services as root/admin
- Instead: Principle of least privilege, dedicated service accounts

---

## 1. Security Principles

### 1.1 Audit Trail Integrity (CWE-778)

**Principle:** Audit logs must be tamper-evident and include sufficient context for investigation.

```python
# ❌ WRONG - Minimal logging without context
logger.info(f"User {user_id} accessed resource")

# ✅ CORRECT - Structured audit log with context
import json
import hashlib
from datetime import datetime, UTC
from dataclasses import dataclass, asdict
from enum import Enum

class AuditAction(Enum):
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    PRIVILEGE_ESCALATION = "privilege_escalation"

@dataclass
class AuditEvent:
    timestamp: str
    event_id: str
    action: AuditAction
    actor_id: str
    actor_ip: str
    resource_type: str
    resource_id: str
    outcome: str  # "success" | "failure" | "denied"
    details: dict
    previous_hash: str  # Chain for tamper evidence

    def compute_hash(self) -> str:
        """Compute hash for tamper detection."""
        data = json.dumps(asdict(self), sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()

class AuditLogger:
    def __init__(self, storage: "AuditStorage"):
        self._storage = storage
        self._previous_hash = "genesis"

    def log(
        self,
        action: AuditAction,
        actor_id: str,
        actor_ip: str,
        resource_type: str,
        resource_id: str,
        outcome: str,
        details: dict | None = None,
    ) -> AuditEvent:
        import uuid

        event = AuditEvent(
            timestamp=datetime.now(UTC).isoformat(),
            event_id=str(uuid.uuid4()),
            action=action,
            actor_id=actor_id,
            actor_ip=actor_ip,
            resource_type=resource_type,
            resource_id=resource_id,
            outcome=outcome,
            details=details or {},
            previous_hash=self._previous_hash,
        )

        self._previous_hash = event.compute_hash()
        self._storage.append(event)
        return event
```

### 1.2 Finding Classification (CWE-693)

**Principle:** Security findings must be classified by severity and exploitability.

```python
# ❌ WRONG - Vague finding report
findings = ["SQL injection found", "XSS vulnerability"]

# ✅ CORRECT - Structured finding with CVSS-like scoring
from dataclasses import dataclass
from enum import Enum

class Severity(Enum):
    CRITICAL = 4  # CVSS 9.0-10.0
    HIGH = 3      # CVSS 7.0-8.9
    MEDIUM = 2    # CVSS 4.0-6.9
    LOW = 1       # CVSS 0.1-3.9
    INFO = 0      # Informational

class Exploitability(Enum):
    TRIVIAL = "trivial"      # Script kiddie level
    MODERATE = "moderate"    # Requires some skill
    DIFFICULT = "difficult"  # Expert level
    THEORETICAL = "theoretical"  # Not proven exploitable

@dataclass
class SecurityFinding:
    id: str
    title: str
    severity: Severity
    exploitability: Exploitability
    cwe_id: str
    affected_component: str
    description: str
    proof_of_concept: str | None
    remediation: str
    references: list[str]

    def to_report(self) -> str:
        return f"""
## [{self.severity.name}] {self.title}

**ID:** {self.id}
**CWE:** {self.cwe_id}
**Exploitability:** {self.exploitability.value}
**Affected Component:** {self.affected_component}

### Description
{self.description}

### Proof of Concept
```
{self.proof_of_concept or "N/A"}
```

### Remediation
{self.remediation}

### References
{chr(10).join(f"- {ref}" for ref in self.references)}
"""
```

### 1.3 Evidence Preservation (CWE-779)

**Principle:** Preserve evidence for findings without modifying the target system.

---

## 2. Version Requirements

```
# SAST/DAST Tools
bandit>=1.7.0          # Python SAST
semgrep>=1.50.0        # Multi-language SAST
trivy>=0.48.0          # Container/IaC scanning
# Dependency scanning
pip-audit>=2.6.0       # Python deps
npm-audit              # Node deps
# Secrets detection
gitleaks>=8.18.0
trufflehog>=3.60.0
```

---

## 3. Code Patterns

### WHEN performing code review for security, use SAST integration

```python
# ❌ WRONG - Manual grep for vulnerabilities
os.system("grep -r 'eval(' ./src")

# ✅ CORRECT - Structured SAST scanning with Semgrep
import subprocess
import json
from pathlib import Path
from dataclasses import dataclass

@dataclass
class SASTResult:
    rule_id: str
    severity: str
    message: str
    file_path: str
    line_start: int
    line_end: int
    code_snippet: str

def run_semgrep_scan(
    target_dir: Path,
    config: str = "p/owasp-top-ten"
) -> list[SASTResult]:
    """Run Semgrep SAST scan and parse results."""

    result = subprocess.run(
        [
            "semgrep", "scan",
            "--config", config,
            "--json",
            "--no-git-ignore",
            str(target_dir),
        ],
        capture_output=True,
        text=True,
        timeout=300,
    )

    if result.returncode not in (0, 1):  # 1 means findings found
        raise RuntimeError(f"Semgrep failed: {result.stderr}")

    data = json.loads(result.stdout)
    findings = []

    for match in data.get("results", []):
        findings.append(SASTResult(
            rule_id=match["check_id"],
            severity=match["extra"]["severity"],
            message=match["extra"]["message"],
            file_path=match["path"],
            line_start=match["start"]["line"],
            line_end=match["end"]["line"],
            code_snippet=match.get("extra", {}).get("lines", ""),
        ))

    return findings

def run_bandit_scan(target_dir: Path) -> list[SASTResult]:
    """Run Bandit Python SAST scan."""

    result = subprocess.run(
        [
            "bandit",
            "-r", str(target_dir),
            "-f", "json",
            "--severity-level", "low",
        ],
        capture_output=True,
        text=True,
        timeout=300,
    )

    data = json.loads(result.stdout)
    findings = []

    for issue in data.get("results", []):
        findings.append(SASTResult(
            rule_id=issue["test_id"],
            severity=issue["issue_severity"],
            message=issue["issue_text"],
            file_path=issue["filename"],
            line_start=issue["line_number"],
            line_end=issue["line_number"],
            code_snippet=issue.get("code", ""),
        ))

    return findings
```

### WHEN scanning for secrets, use multiple detection tools

```python
# ❌ WRONG - Simple regex for secrets
if re.search(r'password\s*=\s*["\']', code):
    print("Found hardcoded password")

# ✅ CORRECT - Multi-tool secret scanning
import subprocess
import json
from dataclasses import dataclass
from pathlib import Path

@dataclass
class SecretFinding:
    detector: str
    secret_type: str
    file_path: str
    line_number: int
    commit: str | None
    snippet: str  # Redacted
    verified: bool

def run_gitleaks_scan(repo_path: Path) -> list[SecretFinding]:
    """Scan git repo for leaked secrets."""

    result = subprocess.run(
        [
            "gitleaks", "detect",
            "--source", str(repo_path),
            "--report-format", "json",
            "--report-path", "/dev/stdout",
            "--no-banner",
        ],
        capture_output=True,
        text=True,
        timeout=600,
    )

    findings = []
    if result.stdout:
        for leak in json.loads(result.stdout):
            # Redact the actual secret
            snippet = leak.get("Match", "")
            redacted = snippet[:4] + "..." + snippet[-4:] if len(snippet) > 8 else "***"

            findings.append(SecretFinding(
                detector="gitleaks",
                secret_type=leak["RuleID"],
                file_path=leak["File"],
                line_number=leak["StartLine"],
                commit=leak.get("Commit"),
                snippet=redacted,
                verified=False,
            ))

    return findings

def run_trufflehog_scan(repo_path: Path) -> list[SecretFinding]:
    """Scan with TruffleHog for verified secrets."""

    result = subprocess.run(
        [
            "trufflehog", "filesystem",
            str(repo_path),
            "--json",
            "--only-verified",  # Only report verified secrets
        ],
        capture_output=True,
        text=True,
        timeout=600,
    )

    findings = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        data = json.loads(line)

        findings.append(SecretFinding(
            detector="trufflehog",
            secret_type=data.get("DetectorName", "unknown"),
            file_path=data.get("SourceMetadata", {}).get("filename", ""),
            line_number=data.get("SourceMetadata", {}).get("line", 0),
            commit=None,
            snippet="[VERIFIED SECRET REDACTED]",
            verified=True,
        ))

    return findings
```

### WHEN auditing dependencies, check multiple vulnerability databases

```python
# ❌ WRONG - Only checking one source
pip_audit_output = subprocess.run(["pip-audit"], capture_output=True)

# ✅ CORRECT - Multi-source dependency audit
import subprocess
import json
from dataclasses import dataclass
from pathlib import Path

@dataclass
class VulnerableDependency:
    package: str
    installed_version: str
    vulnerable_versions: str
    fixed_version: str | None
    cve_ids: list[str]
    severity: str
    description: str
    source: str

def audit_python_deps(requirements_path: Path) -> list[VulnerableDependency]:
    """Audit Python dependencies using pip-audit."""

    result = subprocess.run(
        [
            "pip-audit",
            "-r", str(requirements_path),
            "--format", "json",
            "--progress-spinner", "off",
        ],
        capture_output=True,
        text=True,
    )

    findings = []
    data = json.loads(result.stdout)

    for dep in data.get("dependencies", []):
        for vuln in dep.get("vulns", []):
            findings.append(VulnerableDependency(
                package=dep["name"],
                installed_version=dep["version"],
                vulnerable_versions=vuln.get("affected_versions", ""),
                fixed_version=vuln.get("fix_versions", [None])[0],
                cve_ids=[vuln.get("id", "")],
                severity=vuln.get("severity", "UNKNOWN"),
                description=vuln.get("description", ""),
                source="pip-audit",
            ))

    return findings

def audit_with_trivy(target: Path) -> list[VulnerableDependency]:
    """Audit with Trivy for comprehensive scanning."""

    result = subprocess.run(
        [
            "trivy", "fs",
            "--format", "json",
            "--scanners", "vuln",
            str(target),
        ],
        capture_output=True,
        text=True,
        timeout=300,
    )

    findings = []
    data = json.loads(result.stdout)

    for result_item in data.get("Results", []):
        for vuln in result_item.get("Vulnerabilities", []):
            findings.append(VulnerableDependency(
                package=vuln["PkgName"],
                installed_version=vuln["InstalledVersion"],
                vulnerable_versions="",
                fixed_version=vuln.get("FixedVersion"),
                cve_ids=[vuln["VulnerabilityID"]],
                severity=vuln["Severity"],
                description=vuln.get("Description", ""),
                source="trivy",
            ))

    return findings
```

### WHEN generating audit reports, use structured templates

```python
# ❌ WRONG - Unstructured text report
report = f"Found {len(findings)} issues"

# ✅ CORRECT - Structured audit report generation
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal
import json

@dataclass
class AuditReport:
    title: str
    scope: str
    methodology: str
    start_date: datetime
    end_date: datetime
    auditor: str
    findings: list[SecurityFinding] = field(default_factory=list)
    executive_summary: str = ""

    def add_finding(self, finding: SecurityFinding):
        self.findings.append(finding)
        self.findings.sort(key=lambda f: f.severity.value, reverse=True)

    def get_statistics(self) -> dict:
        stats = {s.name: 0 for s in Severity}
        for f in self.findings:
            stats[f.severity.name] += 1
        return stats

    def to_markdown(self) -> str:
        stats = self.get_statistics()

        sections = [
            f"# {self.title}",
            "",
            "## Executive Summary",
            self.executive_summary,
            "",
            "## Audit Details",
            f"- **Scope:** {self.scope}",
            f"- **Methodology:** {self.methodology}",
            f"- **Period:** {self.start_date.date()} to {self.end_date.date()}",
            f"- **Auditor:** {self.auditor}",
            "",
            "## Findings Summary",
            "",
            "| Severity | Count |",
            "|----------|-------|",
        ]

        for severity in Severity:
            sections.append(f"| {severity.name} | {stats[severity.name]} |")

        sections.extend(["", "## Detailed Findings", ""])

        for finding in self.findings:
            sections.append(finding.to_report())

        return "\n".join(sections)

    def to_json(self) -> str:
        return json.dumps({
            "title": self.title,
            "scope": self.scope,
            "methodology": self.methodology,
            "period": {
                "start": self.start_date.isoformat(),
                "end": self.end_date.isoformat(),
            },
            "auditor": self.auditor,
            "statistics": self.get_statistics(),
            "findings": [
                {
                    "id": f.id,
                    "title": f.title,
                    "severity": f.severity.name,
                    "cwe": f.cwe_id,
                    "component": f.affected_component,
                    "remediation": f.remediation,
                }
                for f in self.findings
            ],
        }, indent=2)
```

---

## 4. Anti-Patterns

Do not:
- Report vulnerabilities without proof of concept
- Skip severity classification on findings
- Store audit logs in modifiable locations
- Run active scans without authorization
- Expose actual secrets in reports (always redact)
- Use single-source vulnerability databases
- Generate reports without remediation guidance

---

## 5. Testing

```python
import pytest
from datetime import datetime
from security_auditing import (
    AuditLogger,
    AuditEvent,
    AuditAction,
    SecurityFinding,
# ... (additional test cases follow same pattern)
```

---

## 6. Pre-Generation Checklist

Before generating security audit code:

- [ ] Authorization: Written permission for active scanning
- [ ] Audit logging: Tamper-evident chain implemented
- [ ] Finding classification: Severity and CWE mapping
- [ ] Secret redaction: No plain secrets in outputs
- [ ] Multi-source: Using multiple vulnerability databases
- [ ] Evidence preservation: Read-only access to targets
- [ ] Report structure: Executive summary + detailed findings
- [ ] Remediation: Each finding has fix guidance

**Templates**: See `assets/` for reusable output templates.

---
