---
name: secret-scanner
description: Detect exposed secrets and credentials
version: 1.0.0
category: security
auto_load: true
token_budget: 250
triggers:
  - pre_commit
  - file_write
tools:
  - Read
  - Grep
---

# Secret Scanner - Compact

**Purpose**: Block commits with exposed secrets (last line of defense)

## Detection Patterns

### API Keys
- AWS: `AKIA[0-9A-Z]{16}`
- GitHub: `ghp_[a-zA-Z0-9]{36}`
- Stripe: `sk_live_[a-zA-Z0-9]{24}`
- Generic: `[Aa]pi[_-]?[Kk]ey.*[:=]\s*['"][^'"]{20,}['"]`

### Credentials
- Passwords: `password.*[:=]\s*['"][^'"]+['"]`
- Tokens: `token.*[:=]\s*['"][^'"]{20,}['"]`
- Private keys: `-----BEGIN (RSA |)PRIVATE KEY-----`

### Common Mistakes
- `.env` files in git
- `credentials.json`
- Hardcoded DB passwords
- OAuth client secrets

## Action
```
🚨 SECRET DETECTED!
📍 File: .env
🔒 Pattern: AWS Access Key
❌ BLOCK COMMIT

Fix: Move to environment variables or secrets manager
```

**Token Budget**: ~250 tokens
**Mode**: Blocking (prevents commits with secrets)
**False Positive**: Review manually if flagged incorrectly
