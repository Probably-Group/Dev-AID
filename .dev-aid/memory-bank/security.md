# Security Patterns & Threats

**Purpose**: Security knowledge base
**Load Strategy**: On-demand (when working on security)
**Update Frequency**: After security reviews or incidents

---

## 🛡️ Security Architecture

### Authentication
- **Pattern**: JWT with refresh token rotation
- **Implementation**: `src/auth/`
- **Key Controls**: Short-lived tokens, HTTP-only cookies, HTTPS only

### Authorization
- **Pattern**: RBAC (Role-Based Access Control)
- **Roles**: admin, user, guest
- **Enforcement**: Middleware at route level

### Input Validation
- **Library**: Zod/Joi
- **Where**: All API endpoints
- **Pattern**: Validate at boundary, sanitize before use

---

## ⚠️ Known Vulnerabilities & Fixes

### VULN-001: SQL Injection in Legacy Code
**Date Discovered**: 2025-11-15
**Severity**: High
**Status**: Fixed

**Issue**:
```typescript
// BAD - vulnerable
db.query(`SELECT * FROM users WHERE id = ${userId}`);
```

**Fix**:
```typescript
// GOOD - parameterized
db.query('SELECT * FROM users WHERE id = $1', [userId]);
```

**Files Fixed**: `src/legacy/user.service.ts`
**Prevention**: Always use parameterized queries

---

## 🔒 OWASP Top 10 Coverage

### A01 - Broken Access Control
- ✅ RBAC implemented
- ✅ Route-level authorization
- ✅ JWT validation
- ⚠️ TODO: Fine-grained permissions

### A02 - Cryptographic Failures
- ✅ HTTPS enforced
- ✅ Passwords hashed (bcrypt, salt rounds: 12)
- ✅ Secrets in environment variables
- ✅ No sensitive data in logs

### A03 - Injection
- ✅ Parameterized queries
- ✅ Input validation (Zod)
- ✅ Output encoding
- ✅ CSP headers

### A04 - Insecure Design
- ✅ Threat modeling done
- ✅ Security reviews in SDLC
- ⚠️ TODO: Formal security requirements

### A05 - Security Misconfiguration
- ✅ Security headers (Helmet.js)
- ✅ CORS configured
- ✅ Error messages don't leak info
- ⚠️ TODO: Security scanning in CI

### A06 - Vulnerable Components
- ✅ Dependency scanning (Snyk)
- ✅ Auto-updates for security patches
- ⚠️ TODO: SCA in CI/CD

### A07 - Authentication Failures
- ✅ MFA available
- ✅ Rate limiting on login
- ✅ Account lockout after failures
- ✅ Strong password policy

### A08 - Software & Data Integrity
- ✅ Code signing
- ✅ Integrity checks
- ⚠️ TODO: Supply chain security

### A09 - Logging & Monitoring Failures
- ✅ Security events logged
- ✅ Alerts configured
- ⚠️ TODO: SIEM integration

### A10 - SSRF
- ✅ URL validation
- ✅ Whitelist for external calls
- ✅ Network segmentation

---

## 🔐 Secrets Management

**Never Commit**:
- API keys
- Database passwords
- Private keys
- OAuth secrets

**How We Store**:
- Development: `.env` (gitignored)
- Production: AWS Secrets Manager / Vault
- CI/CD: GitHub Secrets

**Rotation Schedule**:
- API keys: Quarterly
- DB passwords: Monthly
- JWT secret: Monthly
- SSL certs: Auto (Let's Encrypt)

---

## 🚨 Threat Models

### Threat: Account Takeover
**Attack Vectors**:
1. Credential stuffing
2. Phishing
3. Session hijacking

**Mitigations**:
- Rate limiting ✓
- MFA ✓
- HTTP-only cookies ✓
- Short session timeout ✓

---

## 📊 Security Metrics

**Current State** (as of 2025-11-25):
- Critical vulnerabilities: 0
- High vulnerabilities: 0
- Medium vulnerabilities: 2 (accepted risk)
- Dependency scan: Daily
- Last pentest: 2025-10-15
- Next pentest: 2026-01-15

---

**Usage**: Reference when implementing security features.
Update after security reviews, pentests, or incidents.
