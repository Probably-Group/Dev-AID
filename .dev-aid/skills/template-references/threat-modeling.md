## 15. Threat Modeling & Attack Scenarios

**Template Instructions**: Required for HIGH-risk domains (5+ scenarios), recommended for MEDIUM-risk (3 scenarios).

**Example Structure**:
```markdown
## 15. Threat Modeling & Attack Scenarios

### Threat Model Overview for [Domain Name]

**Domain Risk Level**: [High/Medium/Low] (see Section 0.1)

**Assets to Protect**:
1. **[Asset 1]**: [Description] - **Sensitivity**: [Critical/High/Medium/Low]
2. **[Asset 2]**: [Description] - **Sensitivity**: [Critical/High/Medium/Low]
3. **[Asset 3]**: [Description] - **Sensitivity**: [Critical/High/Medium/Low]

**Threat Actors**:
1. **External Attackers** - Motivation: Financial gain, data theft - Capabilities: Automated scanning, SQL injection, credential stuffing
2. **Malicious Insiders** - Motivation: Data exfiltration, sabotage - Capabilities: Privileged access, knowledge of internal systems
3. **Script Kiddies** - Motivation: Opportunistic attacks - Capabilities: Using public exploits, automated tools
4. **Nation-State Actors** (if applicable) - Motivation: Espionage, disruption - Capabilities: Advanced persistent threats, zero-days

**Attack Surface**:
- Public-facing web application/API
- Authentication system
- Database
- Third-party integrations
- Admin interfaces
- [Domain-specific surfaces]

---

### Attack Scenario 1: [Attack Name - e.g., "SQL Injection via Search Parameter"]

**Threat Category**: OWASP A05:2025 - Injection / CWE-89

**Threat Level**: 🔴 Critical

**Attack Description**:
Attacker exploits insufficient input validation in the search functionality to inject malicious SQL queries, potentially accessing or modifying database contents.

**Preconditions**:
- Search endpoint accepts user input
- Input not properly validated/sanitized
- SQL queries use string concatenation

**Attack Flow**:
```
1. Attacker navigates to search functionality
2. Attacker inputs: `admin' OR '1'='1` in search field
3. Application constructs query: SELECT * FROM users WHERE username = 'admin' OR '1'='1'
4. Query returns all users (authentication bypass)
5. Attacker gains admin access
6. Attacker exfiltrates sensitive data or modifies records
```

**Impact**:
- **Confidentiality**: HIGH - Full database access, all user data exposed
- **Integrity**: HIGH - Attacker can modify/delete records
- **Availability**: MEDIUM - Attacker could drop tables (DoS)
- **Business Impact**: Data breach, regulatory fines, reputation damage

**Likelihood**: HIGH (if not mitigated) - SQL injection is consistently in OWASP Top 10, automated scanners test for this

**Mitigation**:

**Primary Control - Parameterized Queries**:
```[language]
# ✅ SECURE: Parameterized query
def search_users(search_term: str):
    # ORM handles parameterization automatically
    return db.query(User).filter(User.username.contains(search_term)).all()

    # Or with raw SQL using parameters:
    query = "SELECT * FROM users WHERE username LIKE ?"
    return db.execute(query, (f"%{search_term}%",)).fetchall()
```

**Additional Controls**:
- Input validation: Restrict search terms to alphanumeric characters
- Least privilege: Database user has read-only access (no DROP, DELETE permissions)
- WAF rules: Block common SQL injection patterns
- Rate limiting: Prevent automated scanning

**Detection**:
```python
# SAST detection
# Run: semgrep --config=p/sql-injection src/

# WAF logs showing SQL injection attempts
SELECT * FROM logs WHERE request_body LIKE '%OR 1=1%' OR request_body LIKE '%UNION SELECT%'

# Database query monitoring for suspicious patterns
SELECT query FROM pg_stat_activity WHERE query LIKE '%OR%=%'
```

**Testing**:
```python
def test_sql_injection_prevented():
    """Test that SQL injection attempts are safely handled."""
    malicious_inputs = [
        "admin' OR '1'='1",
        "'; DROP TABLE users; --",
        "' UNION SELECT * FROM users --"
    ]

    for malicious in malicious_inputs:
        results = search_users(malicious)
        # Should return zero or safe results, not execute injection
        assert len(results) == 0 or all(malicious not in r.username for r in results)
```

**References**:
- OWASP SQL Injection: https://owasp.org/www-community/attacks/SQL_Injection
- CWE-89: https://cwe.mitre.org/data/definitions/89.html
- [Domain-specific vulnerability advisory if applicable]

---

### Attack Scenario 2: [e.g., "Broken Access Control - IDOR (Insecure Direct Object Reference)"]

**Threat Category**: OWASP A01:2025 - Broken Access Control / CWE-639

**Threat Level**: 🔴 Critical / 🟠 High

**Attack Description**:
Attacker modifies resource IDs in API requests to access other users' data without proper authorization checks.

**Attack Flow**:
```
1. Attacker logs in as user with ID 123
2. Attacker accesses own profile: GET /api/users/123/profile (authorized)
3. Attacker changes ID to 456: GET /api/users/456/profile
4. Application returns user 456's profile data (no authorization check!)
5. Attacker enumerates all users (IDs 1-1000)
6. Attacker harvests PII, sensitive data
```

**Impact**:
- **Confidentiality**: HIGH - Unauthorized access to all user data
- **Integrity**: HIGH - If combined with PUT/DELETE, can modify other users' data
- **Availability**: LOW
- **Business Impact**: Privacy violation, GDPR fines, data breach

**Likelihood**: HIGH - Common vulnerability, easy to exploit, often missed in code reviews

**Mitigation**:

```[language]
# ❌ VULNERABLE: No authorization check
@app.get("/api/users/{user_id}/profile")
async def get_profile(user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# ✅ SECURE: Authorization check
@app.get("/api/users/{user_id}/profile")
async def get_profile(user_id: int, current_user: User = Depends(get_current_user)):
    # Authorization: user can only access own profile (unless admin)
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")

    return db.query(User).filter(User.id == user_id).first()
```

**Additional Controls**:
- Use UUIDs instead of sequential IDs (makes enumeration harder, but not sufficient on its own)
- Centralized authorization middleware
- Audit logging for access attempts

**Detection**:
```python
# Monitor for access pattern anomalies
SELECT user_id, COUNT(DISTINCT accessed_user_id) as distinct_accesses
FROM audit_log
WHERE action = 'profile_access'
GROUP BY user_id
HAVING COUNT(DISTINCT accessed_user_id) > 10  -- Suspicious enumeration
```

**Testing**:
```python
def test_user_cannot_access_other_users_data():
    user_a = create_user()
    user_b = create_user()

    response = client.get(
        f"/api/users/{user_b.id}/profile",
        headers={"Authorization": f"Bearer {user_a.token}"}
    )

    assert response.status_code == 403
```

---

### Attack Scenario 3-5: [Additional Scenarios]

[Repeat structure for 3-5 total attack scenarios based on domain risk level]

**Example Additional Scenarios**:
- Authentication Bypass via JWT Token Tampering (A07:2025)
- Cross-Site Scripting (XSS) via User-Generated Content (A05:2025)
- Server-Side Request Forgery (SSRF) via URL Parameter (A01:2025 - now part of Broken Access Control)
- Privilege Escalation via Role Manipulation (A01:2025)
- Denial of Service via Resource Exhaustion (A10:2025 - Mishandling of Exceptional Conditions)
- Software Supply Chain Attack via Malicious Dependency (A03:2025)

---

### STRIDE Analysis (Optional - for High-risk domains)

**STRIDE Threat Modeling Framework**:

| Category | Threats Identified | Mitigations | Priority |
|----------|-------------------|-------------|----------|
| **Spoofing** | Weak password policy, no MFA | Strong passwords + MFA, rate limiting | HIGH |
| **Tampering** | SQL injection, XSS, command injection | Parameterized queries, input validation, output encoding | CRITICAL |
| **Repudiation** | No audit logs for critical actions | Immutable audit logs, log authentication/authorization events | MEDIUM |
| **Information Disclosure** | Error messages leak stack traces | Safe error messages, log details internally only | HIGH |
| **Denial of Service** | No rate limiting, resource exhaustion | Rate limiting, request size limits, circuit breakers | MEDIUM |
| **Elevation of Privilege** | IDOR, broken access control | Resource-based authorization, principle of least privilege | CRITICAL |

---

### Security Testing Coverage for Threat Scenarios

**Automated Testing**:
- [ ] SAST scans detect injection vulnerabilities
- [ ] DAST scans test for authentication bypass
- [ ] Dependency scanning detects vulnerable libraries
- [ ] Fuzzing tests input handlers

**Manual Testing**:
- [ ] Penetration testing covers all attack scenarios (annually)
- [ ] Security code review for authorization logic
- [ ] Threat model review and update (quarterly)
```

---

