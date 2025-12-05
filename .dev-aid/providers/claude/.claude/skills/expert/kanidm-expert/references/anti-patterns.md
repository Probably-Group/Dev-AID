# Kanidm Common Mistakes and Anti-Patterns

## 1. Insecure LDAP Configuration

```bash
# ❌ DON'T - Plain LDAP exposes credentials
ldapsearch -H ldap://idm.example.com:389 ...

# ✅ DO - Always use LDAPS
ldapsearch -H ldaps://idm.example.com:3636 ...

# ❌ DON'T - Overprivileged bind account
kanidm group add-members idm_admins ldap_bind

# ✅ DO - Minimal read-only access
kanidm group add-members idm_account_read_priv ldap_bind
```

## 2. Weak RADIUS Shared Secrets

```bash
# ❌ DON'T - Predictable or short secrets
kanidm radius set-secret wifi_controller "password123"

# ✅ DO - Use generate-secret for strong random secrets
kanidm radius generate-secret wifi_controller
```

## 3. Missing WebAuthn for Privileged Accounts

```bash
# ❌ DON'T - Password-only for admin access
kanidm person credential set-password admin

# ✅ DO - Require WebAuthn for admins
# User must enroll WebAuthn via web UI
# Configure credential policy to require WebAuthn
kanidm credential-policy create admin_policy --require-webauthn
kanidm group add-members idm_admins admin
kanidm credential-policy apply admin_policy idm_admins
```

## 4. OAuth2 Redirect URI Wildcards

```bash
# ❌ DON'T - Wildcard URIs enable token theft
kanidm oauth2 add-redirect-url myapp "https://*.example.com/callback"

# ✅ DO - Exact URI matching
kanidm oauth2 add-redirect-url myapp "https://app.example.com/callback"
kanidm oauth2 add-redirect-url myapp "https://app2.example.com/callback"
```

## 5. No Backup Strategy

```bash
# ❌ DON'T - No backups
# [Server runs with no backup procedures]

# ✅ DO - Automated daily backups
# Create backup script
cat > /usr/local/bin/kanidm-backup.sh <<'EOF'
#!/bin/bash
BACKUP_DIR="/data/backups"
DATE=$(date +%Y%m%d-%H%M%S)
kanidmd backup "${BACKUP_DIR}/kanidm-${DATE}.json"
# Keep last 30 days
find "${BACKUP_DIR}" -name "kanidm-*.json" -mtime +30 -delete
EOF

# Cron job
0 2 * * * /usr/local/bin/kanidm-backup.sh
```

## 6. UID/GID Reuse

```bash
# ❌ DON'T - Reuse UIDs after account deletion
# User jsmith (uid=10001) deleted
kanidm person create newuser "New User" --gidnumber 10001  # DANGEROUS!

# ✅ DO - Increment UIDs, never reuse
kanidm person create newuser "New User" --gidnumber 10015  # Next available
```

## 7. Exposing Server Without Protection

```bash
# ❌ DON'T - Direct internet exposure
bindaddress = "0.0.0.0:8443"  # No firewall, no reverse proxy

# ✅ DO - Behind reverse proxy with rate limiting
# nginx reverse proxy with rate limiting
location / {
    proxy_pass https://localhost:8443;
    limit_req zone=auth burst=5;
}

# Or firewall restriction
ufw allow from 10.0.0.0/8 to any port 8443
```

## 8. Missing Audit Trail

```bash
# ❌ DON'T - Delete accounts (loses audit trail)
kanidm person delete jsmith

# ✅ DO - Lock accounts to preserve history
kanidm account lock jsmith --reason "Offboarding - 2025-11-19"

# Review locked accounts
kanidm person get jsmith
```
