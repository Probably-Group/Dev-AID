# Kanidm Implementation Patterns

## Pattern 1: Secure Kanidm Server Setup

```bash
# Install Kanidm server
# For production: use proper TLS certificates
kanidmd cert-generate --ca-path /data/ca.pem --cert-path /data/cert.pem \
  --key-path /data/key.pem --domain idm.example.com

# Configure server.toml
cat > /etc/kanidm/server.toml <<EOF
# Core settings
bindaddress = "[::]:8443"
ldapbindaddress = "[::]:3636"
domain = "idm.example.com"
origin = "https://idm.example.com"

# Database
db_path = "/data/kanidm.db"

# TLS (REQUIRED for production)
tls_chain = "/data/cert.pem"
tls_key = "/data/key.pem"

# Logging
log_level = "info"

# Backup (CRITICAL)
online_backup = "/data/backups/"
EOF

# Initialize database (FIRST TIME ONLY)
kanidmd database init

# Recover admin password
kanidmd recover-account admin

# Start server
kanidmd server -c /etc/kanidm/server.toml
```

## Pattern 2: User Account Lifecycle

```bash
# Create user with full attributes
kanidm person create jsmith "John Smith" \
  --mail john.smith@example.com

# Set POSIX attributes for Unix/Linux
kanidm person posix set jsmith --gidnumber 10000

# Add to groups
kanidm group add-members developers jsmith
kanidm group add-members vpn_users jsmith

# Set strong password policy
kanidm person credential set-password jsmith

# Enable WebAuthn (REQUIRED for privileged accounts)
# User enrolls via web UI: https://idm.example.com/

# Suspend account (don't delete - audit trail)
kanidm account lock jsmith --reason "Offboarding - 2025-11-19"

# Generate API token for service accounts
kanidm service-account api-token generate svc_gitlab \
  --name "GitLab OIDC Integration" --expiry "2026-01-01"
```

## Pattern 3: OAuth2/OIDC Integration

```bash
# Register OAuth2 client for application
kanidm oauth2 create gitlab_oidc "GitLab SSO" \
  --origin https://gitlab.example.com

# Add redirect URIs (EXACT MATCH REQUIRED)
kanidm oauth2 add-redirect-url gitlab_oidc \
  https://gitlab.example.com/users/auth/openid_connect/callback

# Enable required scopes
kanidm oauth2 enable-scope gitlab_oidc openid email profile groups

# Set token lifetimes
kanidm oauth2 set-token-lifetime gitlab_oidc --access 3600 --refresh 86400

# Enable PKCE for mobile/SPA clients
kanidm oauth2 enable-pkce mobile_app

# Map groups to claims (for authorization)
kanidm oauth2 create-scope-map gitlab_oidc groups developers admins

# Get client credentials
kanidm oauth2 show-basic-secret gitlab_oidc
# Output: client_id and client_secret

# Application configuration
# Provider: https://idm.example.com/oauth2/openid/gitlab_oidc
# Discovery: https://idm.example.com/oauth2/openid/gitlab_oidc/.well-known/openid-configuration
```

## Pattern 4: LDAP Integration for Legacy Systems

```bash
# Create LDAP bind account
kanidm service-account create ldap_bind "LDAP Bind Account"
kanidm service-account credential set-password ldap_bind

# Grant LDAP read access
kanidm group add-members idm_account_read_priv ldap_bind

# LDAP connection parameters
# Server: ldaps://idm.example.com:3636
# Base DN: dc=idm,dc=example,dc=com
# Bind DN: name=ldap_bind,dc=idm,dc=example,dc=com
# Bind Password: [set above]

# Test LDAP search
ldapsearch -H ldaps://idm.example.com:3636 \
  -D "name=ldap_bind,dc=idm,dc=example,dc=com" \
  -W -b "dc=idm,dc=example,dc=com" \
  "(uid=jsmith)"

# Common LDAP attributes
# uid: username
# mail: email address
# displayName: full name
# memberOf: group memberships
# uidNumber: POSIX UID
# gidNumber: POSIX GID
# loginShell: /bin/bash
# homeDirectory: /home/username
```

## Pattern 5: RADIUS for Network Authentication

```bash
# Configure RADIUS client (network device)
kanidm radius create wifi_controller "Wireless Controller" \
  --address 10.0.1.100

# Generate strong shared secret
kanidm radius generate-secret wifi_controller
# Output: Strong random secret - configure on network device

# Grant RADIUS access to group
kanidm group create wifi_users "Wireless Network Users"
kanidm group add-members wifi_users jsmith
kanidm radius add-group wifi_controller wifi_users

# Configure network device
# RADIUS Server: idm.example.com
# Authentication Port: 1812
# Accounting Port: 1813
# Shared Secret: [from generate-secret above]

# Test RADIUS authentication
# Use tool like radtest or network device test
radtest jsmith password idm.example.com 0 shared-secret

# Monitor RADIUS logs
journalctl -u kanidmd -f | grep radius
```

## Pattern 6: SSH Key Management & PAM Integration

```bash
# User uploads SSH public key via CLI
kanidm person ssh add-publickey jsmith "ssh-name" \
  "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIExample..."

# Configure SSH server to fetch keys from Kanidm
# Install kanidm-ssh package on target systems

# /etc/ssh/sshd_config
cat >> /etc/ssh/sshd_config <<EOF
# Kanidm SSH key management
AuthorizedKeysCommand /usr/bin/kanidm_ssh_authorizedkeys %u
AuthorizedKeysCommandUser nobody
PubkeyAuthentication yes
EOF

# Configure kanidm-ssh client
cat > /etc/kanidm/config <<EOF
uri = "https://idm.example.com"
verify_ca = true
verify_hostnames = true
EOF

# Restart SSH
systemctl restart sshd

# PAM integration for password authentication
# /etc/pam.d/common-auth (Debian/Ubuntu)
auth    sufficient    pam_kanidm.so
auth    required      pam_deny.so

# NSS integration for user resolution
# /etc/nsswitch.conf
passwd: files kanidm
group:  files kanidm
shadow: files kanidm

# Test PAM authentication
pamtester login jsmith authenticate
```

## Pattern 7: Security Hardening & Monitoring

```bash
# Create strong credential policy
kanidm credential-policy create high_security \
  --minimum-length 16 \
  --require-uppercase \
  --require-lowercase \
  --require-number \
  --require-symbol \
  --password-history 12

# Apply to privileged group
kanidm group create privileged_users "High Security Policy Users"
kanidm group add-members privileged_users admin sysadmin
kanidm credential-policy apply high_security privileged_users

# Configure account lockout
kanidm account-policy set-lockout --threshold 5 --duration 3600

# Enable comprehensive audit logging
# server.toml
log_level = "info"  # or "debug" for detailed auditing

# Monitor authentication failures
journalctl -u kanidmd -f | grep "authentication failure"

# Regular backup (CRITICAL)
# Online backup (server running)
kanidmd backup /data/backups/kanidm-$(date +%Y%m%d-%H%M%S).json

# Offline backup (server stopped)
kanidmd database backup /data/backups/

# Test restore procedure
kanidmd database restore /data/backups/kanidm-20251119.json

# Verify database integrity
kanidmd database verify

# Export audit logs
kanidm audit-log export --since "2025-11-01" --format json > audit.json
```
