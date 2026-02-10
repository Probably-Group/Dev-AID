---
name: secret-scanner
description: "Scans files for exposed secrets, API keys, and credentials before commit with blocking enforcement. Key capabilities: AWS/GitHub/Stripe key detection, password/token/private-key patterns, .env file detection, commit blocking. Use when editing any file that might contain credentials, before committing changes. Do NOT use for already-scanned committed code or public configuration files."
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
