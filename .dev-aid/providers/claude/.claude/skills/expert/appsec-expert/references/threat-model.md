# Threat Modeling Guide (STRIDE Methodology)

## Overview

Threat modeling is a structured approach to identifying security risks before they become vulnerabilities. STRIDE is the industry-standard framework for categorizing threats.

---

## STRIDE Framework

STRIDE is an acronym for six threat categories:

| Category | Threat | Security Property Violated |
|----------|--------|---------------------------|
| **S**poofing | Impersonating users/systems | Authentication |
| **T**ampering | Modifying data/code | Integrity |
| **R**epudiation | Denying actions | Non-repudiation |
| **I**nformation Disclosure | Exposing sensitive data | Confidentiality |
| **D**enial of Service | Disrupting availability | Availability |
| **E**levation of Privilege | Gaining unauthorized access | Authorization |

---

## Threat Modeling Process

### Step 1: Identify Assets

List what needs protection:
- **Data**: User credentials, PII, financial data, API keys
- **Systems**: Web servers, databases, authentication services
- **Processes**: Payment processing, user registration, admin functions

**Example**:
```
Assets:
- User passwords (stored as Argon2id hashes)
- JWT access tokens (15 min expiry)
- Customer PII (encrypted at rest)
- Payment card data (PCI-DSS scope)
- Admin API keys (rotated every 90 days)
```

---

### Step 2: Create Data Flow Diagram (DFD)

Map how data flows through the system:

```
┌─────────┐     HTTPS      ┌──────────────┐      SQL       ┌──────────┐
│ Browser │ ──────────────▶│ Web Server   │ ──────────────▶│ Database │
│ (User)  │                │ (FastAPI)    │                │ (Postgres)│
└─────────┘                └──────────────┘                └──────────┘
     │                            │                              │
     │                            ▼                              │
     │                     ┌──────────────┐                      │
     └────────────────────▶│ Auth Service │◀─────────────────────┘
                           │ (JWT/OAuth)  │
                           └──────────────┘
```

**Trust Boundaries**: Mark where data crosses security zones
- Internet → DMZ (web server)
- DMZ → Internal network (database)
- Unauthenticated → Authenticated
- User → Admin

---

### Step 3: Apply STRIDE to Each Component

For each component, ask STRIDE questions:

#### Web Server (FastAPI)

**Spoofing**: Can attacker impersonate a user?
- ❌ Risk: Session hijacking via XSS
- ✅ Mitigation: HttpOnly cookies, CSP headers

**Tampering**: Can attacker modify requests/responses?
- ❌ Risk: MITM attack on HTTP connection
- ✅ Mitigation: Enforce HTTPS with HSTS

**Repudiation**: Can user deny their actions?
- ❌ Risk: No audit logs for user actions
- ✅ Mitigation: Structured logging with user ID, timestamp, action

**Information Disclosure**: Can attacker access sensitive data?
- ❌ Risk: Verbose error messages leak database structure
- ✅ Mitigation: Generic error messages, detailed logs server-side only

**Denial of Service**: Can attacker crash/slow the service?
- ❌ Risk: No rate limiting on API endpoints
- ✅ Mitigation: Rate limiting (100 req/min per IP)

**Elevation of Privilege**: Can user gain admin access?
- ❌ Risk: IDOR allows accessing other users' data
- ✅ Mitigation: Authorization checks on every endpoint

---

### Step 4: Prioritize Threats (Risk Rating)

Use **Risk = Impact × Likelihood** to prioritize:

| Threat | Impact | Likelihood | Risk Score | Priority |
|--------|--------|-----------|------------|----------|
| SQL Injection | High (5) | High (5) | 25 | Critical |
| Session Hijacking | High (5) | Medium (3) | 15 | High |
| DoS Attack | Medium (3) | High (5) | 15 | High |
| CSRF | Medium (3) | Medium (3) | 9 | Medium |
| Information Leakage | Low (2) | High (5) | 10 | Medium |

**Impact Scale**:
- 5 = Data breach, financial loss, regulatory fines
- 3 = Service degradation, limited data exposure
- 1 = Minimal impact, cosmetic issues

**Likelihood Scale**:
- 5 = Trivial to exploit, automated tools available
- 3 = Requires some skill, manual exploitation
- 1 = Very difficult, requires deep expertise

---

### Step 5: Document Mitigations

For each identified threat, document the security control:

```markdown
### Threat: SQL Injection (Critical)

**Description**: Attacker injects SQL commands via user input to access/modify database

**Attack Vector**: Search functionality concatenates user input into SQL query

**Impact**: Full database compromise, data exfiltration, data deletion

**Mitigation**:
1. Use parameterized queries (prepared statements) for ALL database operations
2. Input validation: reject special characters in usernames/emails
3. Least privilege: application database user has minimal permissions
4. WAF rules: block common SQLi patterns

**Verification**:
- SAST: Semgrep detects SQL string concatenation
- Testing: Penetration test with SQLMap
- Code Review: Manual review of all database query code
```

---

## STRIDE Examples by Component

### Database

**Spoofing**: Weak authentication to database
- ✅ Mitigation: Strong passwords, certificate-based auth

**Tampering**: Unauthorized data modification
- ✅ Mitigation: Least privilege, audit logging

**Repudiation**: No record of who changed data
- ✅ Mitigation: Database audit logs, trigger-based logging

**Information Disclosure**: Direct database access
- ✅ Mitigation: Network segmentation, no public internet access

**Denial of Service**: Query overload
- ✅ Mitigation: Connection pooling, query timeout limits

**Elevation of Privilege**: Over-privileged database user
- ✅ Mitigation: Separate users per application, minimal grants

---

### Authentication Service

**Spoofing**: Brute force password guessing
- ✅ Mitigation: Rate limiting, account lockout after 5 failed attempts

**Tampering**: JWT token modification
- ✅ Mitigation: HMAC signature verification

**Repudiation**: No audit trail for login attempts
- ✅ Mitigation: Log all authentication events (success/failure)

**Information Disclosure**: Password reset token enumeration
- ✅ Mitigation: Constant-time responses, same message for valid/invalid users

**Denial of Service**: Account enumeration via login timing
- ✅ Mitigation: Constant-time password verification (Argon2id)

**Elevation of Privilege**: Session fixation
- ✅ Mitigation: Regenerate session ID after login

---

### API Endpoints

**Spoofing**: API key theft
- ✅ Mitigation: Rotate keys regularly, use OAuth2 instead

**Tampering**: Request replay attacks
- ✅ Mitigation: Include timestamp and nonce in signed requests

**Repudiation**: API calls not logged
- ✅ Mitigation: Structured logging with user ID, endpoint, timestamp

**Information Disclosure**: Excessive data in API responses
- ✅ Mitigation: Return only necessary fields, paginate large responses

**Denial of Service**: Unbounded API requests
- ✅ Mitigation: Rate limiting (per user, per IP)

**Elevation of Privilege**: IDOR vulnerability
- ✅ Mitigation: Authorization check on every resource access

---

## Attack Trees

Attack trees visualize how an attacker might achieve a goal.

### Example: Steal User Credentials

```
                    Goal: Steal User Credentials
                              |
           ┌──────────────────┼──────────────────┐
           │                  │                  │
    Phishing Attack    SQL Injection      XSS Attack
           │                  │                  │
    ┌──────┴─────┐      ┌────┴────┐       ┌─────┴─────┐
 Email      SMS   String  Union    Stored  Reflected
 Phish      Phish  Concat  Query    XSS      XSS
```

**Defense**: Mitigations at each node
- Phishing: MFA (even if password stolen, can't login)
- SQL Injection: Parameterized queries
- XSS: Content Security Policy, output encoding

---

## Threat Modeling Templates

### New Feature Threat Model Template

```markdown
# Threat Model: [Feature Name]

## Overview
- **Feature**: Password reset functionality
- **Developer**: Alice
- **Date**: 2025-12-05
- **Status**: Design Review

## Assets
- User email addresses
- Password reset tokens
- New passwords

## Trust Boundaries
- Unauthenticated user → Email service
- Email link → Authenticated session

## Threats (STRIDE)

### Spoofing
- ❌ Attacker requests reset for victim's email
- ✅ Mitigation: Send reset link to registered email only

### Tampering
- ❌ Attacker modifies reset token in URL
- ✅ Mitigation: HMAC-signed tokens, 15-minute expiry

### Repudiation
- ❌ User claims they didn't reset password
- ✅ Mitigation: Log all reset requests with IP, timestamp

### Information Disclosure
- ❌ Reset endpoint reveals if email exists
- ✅ Mitigation: Same response for valid/invalid emails

### Denial of Service
- ❌ Attacker floods reset requests
- ✅ Mitigation: Rate limit to 3 resets per email per hour

### Elevation of Privilege
- ❌ Reset token works for different user
- ✅ Mitigation: Bind token to specific user ID, verify on use

## Security Requirements
1. Reset tokens must expire in 15 minutes
2. Tokens must be single-use (invalidated after use)
3. Rate limit: 3 requests per email per hour
4. Log all reset attempts (success and failure)
5. Send confirmation email after successful reset

## Testing
- [ ] Test expired token rejected
- [ ] Test reused token rejected
- [ ] Test rate limiting enforced
- [ ] Test account enumeration prevented
```

---

## Automated Threat Modeling

### Using pytm (Python Threat Modeling)

```python
# threat_model.py
from pytm import TM, Server, Datastore, Dataflow, Boundary, Actor

tm = TM("Web Application Threat Model")
tm.description = "E-commerce web application"

# Define boundaries
internet = Boundary("Internet")
dmz = Boundary("DMZ")
internal = Boundary("Internal Network")

# Define actors
user = Actor("User")
user.inBoundary = internet

# Define components
web_server = Server("Web Server")
web_server.inBoundary = dmz
web_server.OS = "Ubuntu"
web_server.providesAuthentication = True

db = Datastore("Database")
db.inBoundary = internal
db.isSQL = True
db.storesUserData = True

# Define data flows
user_request = Dataflow(user, web_server, "HTTPS Request")
user_request.protocol = "HTTPS"
user_request.data = "User credentials"

db_query = Dataflow(web_server, db, "SQL Query")
db_query.protocol = "SQL"
db_query.data = "User data"

# Generate threat report
tm.process()
```

---

## Threat Intelligence Integration

### Track Known Vulnerabilities

```python
# Track OWASP Top 10 coverage
OWASP_TOP_10_2025 = {
    "A01:2025": {
        "name": "Broken Access Control",
        "mitigations": [
            "Authorization check on every endpoint",
            "RBAC implemented",
            "IDOR tests pass"
        ],
        "status": "Mitigated"
    },
    "A02:2025": {
        "name": "Cryptographic Failures",
        "mitigations": [
            "TLS 1.3 enforced",
            "Argon2id for passwords",
            "AES-256-GCM for data at rest"
        ],
        "status": "Mitigated"
    },
    # ... continue for all 10
}
```

### CVE Tracking

```bash
# Check for known vulnerabilities in dependencies
pip-audit --desc

# Check specific CVE
grype image:app --only-fixed
```

---

## Best Practices

1. **Threat Model Early**: During design phase, before code
2. **Update Regularly**: Review after significant changes
3. **Involve Team**: Developers, security, operations
4. **Document Decisions**: Why certain risks are accepted
5. **Prioritize**: Focus on high-risk, high-likelihood threats
6. **Verify Mitigations**: Test that controls actually work
7. **Use Tools**: Automate with pytm, Microsoft Threat Modeling Tool
8. **Review OWASP**: Map threats to OWASP Top 10
9. **Track Metrics**: Number of threats identified, mitigated
10. **Learn from Incidents**: Update threat models after breaches

---

## When to Threat Model

- ✅ New features (especially security-critical)
- ✅ Architecture changes
- ✅ New third-party integrations
- ✅ After security incidents
- ✅ Before major releases
- ✅ Annual review of existing systems
- ❌ Don't wait until security incident occurs

---

## Resources

- **STRIDE**: [Microsoft STRIDE Threat Modeling](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool)
- **OWASP**: [OWASP Threat Modeling](https://owasp.org/www-community/Threat_Modeling)
- **Attack Trees**: [Attack Tree Methodology](https://www.schneier.com/academic/archives/1999/12/attack_trees.html)
- **pytm**: [Python Threat Modeling Library](https://github.com/izar/pytm)
