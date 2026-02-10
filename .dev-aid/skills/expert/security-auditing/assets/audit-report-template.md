# Security Audit Report

## Document Control

| Field | Value |
|-------|-------|
| **Report Title** | [Project/System Name] Security Audit |
| **Report ID** | [AUDIT-YYYY-NNN] |
| **Classification** | [Confidential / Internal / Public] |
| **Auditor(s)** | [Names and roles] |
| **Audit Period** | [Start Date] -- [End Date] |
| **Report Date** | [Date] |
| **Version** | [1.0] |

---

## 1. Executive Summary

[2-3 paragraph overview of the audit scope, key findings, and overall risk posture. Highlight the most critical issues and whether the system is fit for purpose.]

**Overall Risk Rating:** [Critical / High / Medium / Low]

---

## 2. Scope

### 2.1 In Scope
- [Application/service name and version]
- [Infrastructure components]
- [APIs and integrations]

### 2.2 Out of Scope
- [Explicitly excluded components]

### 2.3 Constraints and Limitations
- [Time constraints, access limitations, etc.]

---

## 3. Methodology

- [Testing approach: white-box / grey-box / black-box]
- [Standards applied: OWASP Top 10, CWE/SANS Top 25, etc.]
- [Tools used: Semgrep, Bandit, Trivy, Gitleaks, etc.]
- [Manual review areas]

---

## 4. Findings Summary

| Severity | Count |
|----------|-------|
| Critical | [N] |
| High | [N] |
| Medium | [N] |
| Low | [N] |
| Informational | [N] |
| **Total** | **[N]** |

---

## 5. Detailed Findings

[Insert individual findings using finding-template.md for each]

---

## 6. Recommendations

### Immediate Actions (0-7 days)
- [Critical and high severity remediations]

### Short-Term (1-4 weeks)
- [Medium severity remediations]

### Long-Term (1-3 months)
- [Low severity and hardening measures]

---

## 7. Appendix

### A. Tool Output Summaries
- [Semgrep: N rules matched, N findings]
- [Trivy: N vulnerabilities across N dependencies]
- [Gitleaks: N potential secret leaks]

### B. Evidence References
- [Screenshot/log references for each finding]

### C. Glossary
- **CVSS** -- Common Vulnerability Scoring System
- **CWE** -- Common Weakness Enumeration
- **SAST** -- Static Application Security Testing
