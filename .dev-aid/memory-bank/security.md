# Security Patterns & Guidelines

**Purpose**: Security knowledge base (team-shared)
**Note**: For personal AI notes, use Claude's built-in memory (`~/.claude/projects/*/memory/`)

---

## Security Architecture

### Authentication
- **Pattern**: [JWT/Sessions/OAuth2]
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

## Known Vulnerabilities & Fixes

### VULN-001: [Description]
**Date Discovered**: YYYY-MM-DD
**Severity**: Critical | High | Medium | Low
**Status**: Open | Fixed

**Issue**: Description of the vulnerability

**Fix**: How it was fixed

**Files Fixed**: `path/to/file.ts`
**Prevention**: How to prevent in future

---

## OWASP Top 10 Coverage

### A01 - Broken Access Control
- [ ] RBAC implemented
- [ ] Route-level authorization
- [ ] JWT validation

### A02 - Cryptographic Failures
- [ ] HTTPS enforced
- [ ] Passwords properly hashed
- [ ] Secrets in environment variables
- [ ] No sensitive data in logs

### A03 - Injection
- [ ] Parameterized queries
- [ ] Input validation
- [ ] Output encoding

---

## Secrets Management

**Never Commit**:
- API keys
- Database passwords
- Private keys
- OAuth secrets

**How We Store**:
- Development: `.env` (gitignored)
- Production: Secrets manager
- CI/CD: GitHub/GitLab Secrets

---

## Security Tools

**Gitleaks**: Secret scanning (git history + current)
**Trivy**: CVE + Misconfig + Secrets
**Opengrep**: SAST with 340+ rules

See: `.dev-aid/docs/SECURITY-TOOLS-REFERENCE.md`

---

**Usage**: Reference when implementing security features.
Update after security reviews, pentests, or incidents.
