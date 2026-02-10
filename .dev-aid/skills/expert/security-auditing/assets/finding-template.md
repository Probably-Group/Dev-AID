## [SEVERITY] [Finding Title]

| Field | Value |
|-------|-------|
| **Finding ID** | FIND-[NNN] |
| **Title** | [Descriptive title of the vulnerability] |
| **Severity** | [Critical / High / Medium / Low / Informational] |
| **CVSS Score** | [0.0 - 10.0] ([Vector string, e.g. CVSS:3.1/AV:N/AC:L/...]) |
| **CWE** | [CWE-NNN: Name] |
| **Status** | [Open / Confirmed / Remediated / Accepted Risk] |

---

### Description

[Clear explanation of the vulnerability. What is the issue, why does it matter, and what is the potential impact? 2-4 sentences.]

---

### Affected Component

- **File/Path:** [src/auth/login.py, /api/v1/users, etc.]
- **Line(s):** [Line numbers or range, if applicable]
- **Environment:** [Production / Staging / All]

---

### Steps to Reproduce

1. [Step-by-step instructions to trigger the vulnerability]
2. [Include specific URLs, payloads, or commands]
3. [Expected vs. actual behavior]

---

### Evidence

```
[Paste relevant code snippet, HTTP request/response, tool output, or screenshot reference]
```

**Tool:** [Tool that detected it, e.g. Semgrep rule ID, Bandit B101, manual review]

---

### Impact

[Describe the real-world impact: data exposure, privilege escalation, service disruption, compliance violation, etc.]

---

### Remediation

**Recommended Fix:**
[Specific, actionable remediation steps. Include code examples if helpful.]

```
[Example remediated code or configuration]
```

**Verification:**
[How to confirm the fix is effective]

---

### References

- [Link to CWE entry]
- [Link to OWASP guidance]
- [Link to relevant documentation or advisory]
