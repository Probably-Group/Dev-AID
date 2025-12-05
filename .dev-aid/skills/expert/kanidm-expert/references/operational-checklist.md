# Kanidm Operational Checklist

## Pre-Implementation Checklist

### Phase 1: Before Writing Code

- [ ] **Understand Requirements**
  - [ ] Review identity management requirements
  - [ ] Identify authentication methods needed (WebAuthn, TOTP, password)
  - [ ] Document integration points (OAuth2, LDAP, RADIUS, SSH)
  - [ ] Define user/group structure and access policies

- [ ] **Security Planning**
  - [ ] Identify credential policy requirements per user tier
  - [ ] Plan TLS certificate strategy (CA-signed for production)
  - [ ] Define RADIUS shared secret rotation schedule
  - [ ] Document OAuth2 client requirements and scopes

- [ ] **Write Tests First (TDD)**
  - [ ] Create unit tests for service layer
  - [ ] Create integration tests for LDAP/OAuth2/RADIUS
  - [ ] Create security tests for TLS, lockout, redirect validation
  - [ ] Verify tests fail before implementation

### Phase 2: During Implementation

- [ ] **Core Configuration**
  - [ ] Configure Kanidm server with TLS
  - [ ] Set up backup procedures
  - [ ] Create users and groups with proper POSIX attributes
  - [ ] Configure credential policies

- [ ] **Authentication Setup**
  - [ ] Enable WebAuthn for privileged accounts
  - [ ] Configure TOTP as backup
  - [ ] Set strong password policies
  - [ ] Configure account lockout thresholds

- [ ] **Integration Configuration**
  - [ ] Register OAuth2 clients with exact redirect URIs
  - [ ] Enable PKCE for public clients
  - [ ] Configure LDAP bind accounts with minimal privileges
  - [ ] Set up RADIUS clients with strong shared secrets
  - [ ] Configure SSH key distribution

- [ ] **Run Tests Continuously**
  - [ ] Run unit tests after each component
  - [ ] Run integration tests after configuration changes
  - [ ] Verify security tests pass

### Phase 3: Before Committing/Deploying

- [ ] **Security Verification**
  - [ ] TLS certificates from trusted CA (not self-signed in prod)
  - [ ] WebAuthn enforced for all admin accounts
  - [ ] Strong credential policies configured
  - [ ] Account lockout policies enabled
  - [ ] Audit logging configured
  - [ ] LDAPS only (plain LDAP disabled)
  - [ ] Strong RADIUS shared secrets (generated, not manual)
  - [ ] OAuth2 redirect URIs exact match (no wildcards)
  - [ ] No default passwords

- [ ] **All Tests Pass**
  - [ ] Unit tests: `pytest tests/test_*.py -v`
  - [ ] Integration tests: `pytest tests/integration/ -v`
  - [ ] Security tests: `pytest tests/security/ -v`
  - [ ] E2E tests: `pytest tests/e2e/ -v`

- [ ] **High Availability & Backup**
  - [ ] Daily automated backups configured
  - [ ] Backup restore tested successfully
  - [ ] Off-site backup storage configured
  - [ ] Database integrity verification scheduled
  - [ ] Replication configured (if HA required)
  - [ ] Disaster recovery plan documented

- [ ] **Integration Verification**
  - [ ] LDAP integration tested with legacy apps
  - [ ] OAuth2/OIDC tested with all clients
  - [ ] RADIUS tested with network devices
  - [ ] SSH key distribution tested
  - [ ] PAM authentication tested
  - [ ] Group membership propagation verified

- [ ] **Operational Readiness**
  - [ ] Monitoring and alerting configured
  - [ ] Log aggregation set up
  - [ ] Admin procedures documented
  - [ ] Incident response plan ready
  - [ ] Admin accounts have WebAuthn enrolled
  - [ ] Service account credentials rotated
  - [ ] Access review schedule established

- [ ] **Network Security**
  - [ ] Firewall rules configured
  - [ ] Rate limiting enabled
  - [ ] Reverse proxy configured (if applicable)
  - [ ] TLS 1.2+ enforced
  - [ ] No direct internet exposure without protection

## Key Configuration Files

### Server Configuration: /etc/kanidm/server.toml
- Verify domain and origin settings
- Confirm TLS certificate paths
- Check bind addresses
- Validate backup path

### Client Configuration: /etc/kanidm/config
- Correct server URI
- TLS verification enabled
- Valid CA certificate

### SSH Integration: /etc/ssh/sshd_config
- AuthorizedKeysCommand configured
- PubkeyAuthentication enabled

### PAM Integration: /etc/pam.d/
- pam_kanidm.so configured
- Correct order of auth modules
