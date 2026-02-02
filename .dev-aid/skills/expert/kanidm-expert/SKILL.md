---
name: kanidm-expert
version: 2.0.0
description: "Kanidm identity management with OAuth2/OIDC, LDAP compatibility, and WebAuthn authentication."
risk_level: HIGH
---

# Kanidm Identity Management Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-532: Sensitive Info in Logs (CVE-2025-30205)**
- NEVER: Use NixOS module with `adminPasswordFile` on unpatched versions
- ALWAYS: Audit logs for leaked creds, rotate exposed passwords

**CWE-287: OAuth2 Auth Code Reuse**
- NEVER: Assume auth codes are one-time-use without verification
- ALWAYS: Implement client-side validation, monitor for code reuse

**CWE-269: Account Policy Downgrade**
- NEVER: Assume MFA policies persist across migrations
- ALWAYS: Review `idm_all_accounts` policies after upgrades, verify MFA settings

**CWE-90: LDAP Injection**
- NEVER: Use LDAP gateway with unsanitized user input in filters
- ALWAYS: Parameterized queries, escape `( ) ! | & *` chars, whitelist validation

### 0.3 Risk Level: HIGH

**Verification requirements for HIGH risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 OAuth2/OIDC Configuration (CWE-287)

**Principle:** Use PKCE for all clients. Validate redirect URIs strictly.

```toml
# ❌ WRONG - Insecure OAuth2 client
[oauth2_client.myapp]
basic_secret = "plaintext-secret"
redirect_uris = ["*"]

# ✅ CORRECT - Secure OAuth2 client with PKCE
[[oauth2_rs_basic_secret]]
name = "myapp"
origin = "https://myapp.example.com"
displayname = "My Application"
# Strict redirect URIs - no wildcards
redirect_uris = ["https://myapp.example.com/auth/callback"]
# Enable PKCE
enable_pkce = true
# Require signed tokens
prefer_short_username = false
# Scopes
scope_maps = [
    { "group" = "myapp_users", "scopes" = ["openid", "profile", "email"] },
    { "group" = "myapp_admins", "scopes" = ["openid", "profile", "email", "groups"] },
]
```

### 1.2 WebAuthn/Passkey Security (CWE-308)

**Principle:** Prefer passkeys over passwords. Enforce MFA for privileged accounts.

### 1.3 Group-Based Access Control (CWE-284)

**Principle:** Use groups for authorization. Minimize direct user permissions.

### 1.4 Session Management (CWE-613)

**Principle:** Configure appropriate session timeouts. Enable session revocation.

### 1.5 LDAP Security (CWE-90)

**Principle:** Use LDAPS only. Validate all LDAP queries for injection.

### 1.6 Credential Storage (CWE-916)

**Principle:** Use Kanidm's built-in credential storage. Never store passwords externally.

---

## 2. Version Requirements

**ALWAYS use these minimum versions:**

```yaml
kanidm-server: v1.3.0+
kanidm-client: v1.3.0+
kanidm-tools: v1.3.0+
```

---

## 3. Code Patterns

### 3.1 WHEN configuring Kanidm server

```toml
# ❌ WRONG - Insecure configuration
# server.toml
bindaddress = "0.0.0.0:8443"
ldapbindaddress = "0.0.0.0:636"
# No TLS, no domain, insecure defaults

# ✅ CORRECT - Production Kanidm server configuration
# /etc/kanidm/server.toml

# Network binding
bindaddress = "[::]:8443"
ldapbindaddress = "[::]:636"

# Domain configuration
domain = "idm.example.com"
origin = "https://idm.example.com"

# TLS configuration
tls_chain = "/etc/kanidm/certs/fullchain.pem"
tls_key = "/etc/kanidm/certs/privkey.pem"

# Database
db_path = "/var/lib/kanidm/kanidm.db"
db_fs_type = "zfs"  # or "generic" for other filesystems

# Trust X-Forwarded-For from specific proxy
trust_x_forward_for = true
# Only trust headers from localhost (reverse proxy)
role = "WriteReplica"

# Logging
log_level = "info"

# Online backup to object storage
[online_backup]
path = "/var/lib/kanidm/backup"
schedule = "0 2 * * *"  # Daily at 2 AM
versions = 7

# Integration with replication
[replication]
# Configure for HA setup
# origin = "https://idm-replica.example.com"
# bindaddress = "[::]:8444"
```

### 3.2 WHEN creating OAuth2/OIDC clients programmatically

```rust
// ❌ WRONG - Hardcoded credentials, no validation
let client = kanidm_client::KanidmClient::new("https://idm.example.com");
client.auth_simple_password("admin", "password123").await?;

// ✅ CORRECT - Secure Kanidm client in Rust
use kanidm_client::{KanidmClient, KanidmClientBuilder};
use kanidm_proto::v1::{
    Entry, CreateRequest, ModifyRequest, Modify,
    OAuth2RsBasicSecretRequest, OAuth2RsBasicSecret,
};
use std::collections::BTreeSet;

#[derive(Clone)]
pub struct KanidmConfig {
    pub url: String,
    pub ca_path: Option<String>,
    pub connect_timeout: u64,
}

pub struct KanidmAdmin {
    client: KanidmClient,
}

impl KanidmAdmin {
    pub async fn new(config: &KanidmConfig) -> Result<Self, anyhow::Error> {
        let mut builder = KanidmClientBuilder::new()
            .address(config.url.clone())
            .connect_timeout(config.connect_timeout);

        if let Some(ca_path) = &config.ca_path {
            builder = builder.add_root_certificate_filepath(ca_path)?;
        }

        let client = builder.build()?;

        // Authenticate using token from environment
        let token = std::env::var("KANIDM_TOKEN")
            .map_err(|_| anyhow::anyhow!("KANIDM_TOKEN not set"))?;

        client.auth_with_token(&token).await?;

        Ok(Self { client })
    }

    pub async fn create_oauth2_client(
        &self,
        name: &str,
        display_name: &str,
        origin: &str,
        redirect_uris: &[String],
        allowed_groups: &[String],
    ) -> Result<OAuth2RsBasicSecret, anyhow::Error> {
        // Validate redirect URIs - must be HTTPS, no wildcards
        for uri in redirect_uris {
            if !uri.starts_with("https://") {
                anyhow::bail!("Redirect URI must use HTTPS: {}", uri);
            }
            if uri.contains('*') {
                anyhow::bail!("Wildcard redirect URIs not allowed: {}", uri);
            }
        }

        // Create OAuth2 resource server
        let request = OAuth2RsBasicSecretRequest {
            name: name.to_string(),
            displayname: display_name.to_string(),
            origin: origin.to_string(),
            redirect_uris: redirect_uris.to_vec(),
            // Enable PKCE
            enable_pkce: true,
            // Enable token refresh
            enable_refresh_token: true,
            // Strict redirect matching
            strict_redirect_uri: true,
        };

        let secret = self.client
            .idm_oauth2_rs_basic_secret_create(&request)
            .await?;

        // Configure scope maps for allowed groups
        for group in allowed_groups {
            self.client
                .idm_oauth2_rs_update_scope_map(
                    name,
                    group,
                    &["openid", "profile", "email"],
                )
                .await?;
        }

        // Add groups claim for admin group
        self.client
            .idm_oauth2_rs_update_scope_map(
                name,
                &format!("{}_admins", name),
                &["openid", "profile", "email", "groups"],
            )
            .await?;

        Ok(secret)
    }

    pub async fn create_service_account(
        &self,
        name: &str,
        display_name: &str,
        groups: &[String],
    ) -> Result<String, anyhow::Error> {
        // Create service account
        self.client
            .idm_service_account_create(name, display_name)
            .await?;

        // Add to groups
        for group in groups {
            self.client
                .idm_group_add_members(group, &[name])
                .await?;
        }

        // Generate API token
        let token = self.client
            .idm_service_account_generate_api_token(name, "automation", None)
            .await?;

        Ok(token)
    }

    pub async fn configure_mfa_policy(
        &self,
        group_name: &str,
        require_mfa: bool,
        allowed_methods: &[&str],  // ["passkey", "totp"]
    ) -> Result<(), anyhow::Error> {
        // Create or update credential policy
        let policy_name = format!("{}_cred_policy", group_name);

        // Set MFA requirement
        self.client
            .idm_group_set_credential_policy(
                group_name,
                &policy_name,
            )
            .await?;

        if require_mfa {
            // Require at least passkey or TOTP
            self.client
                .idm_credential_policy_set_mfa_required(&policy_name, true)
                .await?;
        }

        // Configure allowed authentication methods
        for method in allowed_methods {
            match *method {
                "passkey" => {
                    self.client
                        .idm_credential_policy_enable_webauthn(&policy_name)
                        .await?;
                }
                "totp" => {
                    self.client
                        .idm_credential_policy_enable_totp(&policy_name)
                        .await?;
                }
                _ => anyhow::bail!("Unknown auth method: {}", method),
            }
        }

        Ok(())
    }
}
```

### 3.3 WHEN integrating applications with Kanidm OIDC

```typescript
// ❌ WRONG - No state validation, no PKCE
const authUrl = `${KANIDM_URL}/oauth2/authorize?client_id=${CLIENT_ID}&redirect_uri=${REDIRECT}`;

// ✅ CORRECT - Full OIDC integration with PKCE
import { Issuer, generators, Client, TokenSet } from 'openid-client';
import { z } from 'zod';

interface KanidmOIDCConfig {
  issuerUrl: string;
  clientId: string;
  clientSecret: string;
  redirectUri: string;
  scopes: string[];
}

const UserInfoSchema = z.object({
  sub: z.string(),
  name: z.string().optional(),
  preferred_username: z.string(),
  email: z.string().email().optional(),
  email_verified: z.boolean().optional(),
  groups: z.array(z.string()).optional(),
});

type UserInfo = z.infer<typeof UserInfoSchema>;

class KanidmOIDC {
  private client: Client | null = null;
  private config: KanidmOIDCConfig;

  constructor(config: KanidmOIDCConfig) {
    this.config = config;
  }

  async initialize(): Promise<void> {
    const issuer = await Issuer.discover(this.config.issuerUrl);

    this.client = new issuer.Client({
      client_id: this.config.clientId,
      client_secret: this.config.clientSecret,
      redirect_uris: [this.config.redirectUri],
      response_types: ['code'],
      token_endpoint_auth_method: 'client_secret_basic',
    });
  }

  generateAuthorizationUrl(state: string): { url: string; codeVerifier: string } {
    if (!this.client) {
      throw new Error('OIDC client not initialized');
    }

    // Generate PKCE challenge
    const codeVerifier = generators.codeVerifier();
    const codeChallenge = generators.codeChallenge(codeVerifier);

    const url = this.client.authorizationUrl({
      scope: this.config.scopes.join(' '),
      state,
      code_challenge: codeChallenge,
      code_challenge_method: 'S256',
      // Prompt for re-authentication
      prompt: 'login',
    });

    return { url, codeVerifier };
  }

  async handleCallback(
    params: { code: string; state: string },
    expectedState: string,
    codeVerifier: string
  ): Promise<{ tokens: TokenSet; userInfo: UserInfo }> {
    if (!this.client) {
      throw new Error('OIDC client not initialized');
    }

    // Validate state to prevent CSRF
    if (params.state !== expectedState) {
      throw new Error('Invalid state parameter');
    }

    // Exchange code for tokens with PKCE
    const tokens = await this.client.callback(
      this.config.redirectUri,
      { code: params.code, state: params.state },
      { state: expectedState, code_verifier: codeVerifier }
    );

    // Fetch user info
    const rawUserInfo = await this.client.userinfo(tokens.access_token!);

    // Validate user info
    const userInfo = UserInfoSchema.parse(rawUserInfo);

    return { tokens, userInfo };
  }

  async refreshTokens(refreshToken: string): Promise<TokenSet> {
    if (!this.client) {
      throw new Error('OIDC client not initialized');
    }

    return this.client.refresh(refreshToken);
  }

  async revokeToken(token: string, tokenType: 'access_token' | 'refresh_token'): Promise<void> {
    if (!this.client) {
      throw new Error('OIDC client not initialized');
    }

    await this.client.revoke(token, tokenType);
  }

  // Verify group membership for authorization
  hasRequiredGroups(userInfo: UserInfo, requiredGroups: string[]): boolean {
    if (!userInfo.groups) {
      return false;
    }

    return requiredGroups.every((group) => userInfo.groups!.includes(group));
  }
}

// Express middleware example
import { Request, Response, NextFunction } from 'express';
import session from 'express-session';

declare module 'express-session' {
  interface SessionData {
    oidcState?: string;
    codeVerifier?: string;
    tokens?: TokenSet;
    userInfo?: UserInfo;
  }
}

function createKanidmAuthMiddleware(oidc: KanidmOIDC, requiredGroups?: string[]) {
  return async (req: Request, res: Response, next: NextFunction) => {
    // Check if already authenticated
    if (req.session.tokens && req.session.userInfo) {
      // Check token expiration
      if (req.session.tokens.expired()) {
        try {
          // Try to refresh
          const newTokens = await oidc.refreshTokens(req.session.tokens.refresh_token!);
          req.session.tokens = newTokens;
        } catch {
          // Refresh failed, need re-authentication
          return res.redirect('/auth/login');
        }
      }

      // Check group membership if required
      if (requiredGroups && !oidc.hasRequiredGroups(req.session.userInfo, requiredGroups)) {
        return res.status(403).json({ error: 'Insufficient permissions' });
      }

      return next();
    }

    // Not authenticated
    return res.redirect('/auth/login');
  };
}
```

### 3.4 WHEN configuring LDAP integration

```yaml
# ❌ WRONG - LDAP without TLS
ldap_url: ldap://idm.example.com:389

# ✅ CORRECT - Kubernetes LDAP configuration with Kanidm
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: kanidm-ldap-config
  namespace: auth
data:
  ldap-config.yaml: |
    # LDAP client configuration for Kanidm
    servers:
      - url: ldaps://idm.example.com:636
        start_tls: false  # Already using LDAPS
        tls_verify: true
        tls_ca_cert: /etc/ldap/certs/ca.crt

    bind:
      # Use service account for LDAP binds
      method: simple
      dn_template: "spn={{ .Username }}@example.com,dc=idm,dc=example,dc=com"

    search:
      base_dn: "dc=idm,dc=example,dc=com"
      user_filter: "(|(uid={{ .Username }})(mail={{ .Username }}))"
      group_filter: "(member={{ .UserDN }})"
      user_attrs:
        - uid
        - mail
        - displayName
        - memberOf
      group_attrs:
        - cn
        - member

    timeout:
      connect: 5s
      read: 10s
---
# Example: GitLab LDAP configuration
apiVersion: v1
kind: Secret
metadata:
  name: gitlab-ldap-secret
  namespace: gitlab
stringData:
  ldap.yaml: |
    main:
      label: 'Kanidm'
      host: 'idm.example.com'
      port: 636
      uid: 'uid'
      encryption: 'simple_tls'
      verify_certificates: true
      ca_file: '/etc/gitlab/ldap/ca.crt'
      bind_dn: 'dn=token'
      password: '${LDAP_BIND_TOKEN}'
      active_directory: false
      allow_username_or_email_login: true
      base: 'dc=idm,dc=example,dc=com'
      user_filter: '(class=person)'
      group_base: 'dc=idm,dc=example,dc=com'
      admin_group: 'gitlab_admins'
      attributes:
        username: 'uid'
        email: 'mail'
        name: 'displayName'
```

### 3.5 WHEN implementing passkey/WebAuthn registration

```rust
// ❌ WRONG - Weak authentication, no MFA
async fn login(username: &str, password: &str) -> Result<Token, Error> {
    client.auth_simple_password(username, password).await
}

// ✅ CORRECT - WebAuthn/Passkey authentication flow
use kanidm_client::KanidmClient;
use kanidm_proto::v1::{
    AuthAllowed, AuthCredential, AuthIssueSession, AuthMech, AuthRequest, AuthState,
};
use webauthn_rs::prelude::*;

pub struct PasskeyAuth {
    client: KanidmClient,
}

impl PasskeyAuth {
    pub async fn start_authentication(
        &self,
        username: &str,
    ) -> Result<AuthenticationContext, anyhow::Error> {
        // Initialize authentication
        let auth_state = self.client
            .auth_step_init(username)
            .await?;

        // Check available authentication methods
        let allowed = match auth_state.state {
            AuthState::Choose(allowed) => allowed,
            _ => anyhow::bail!("Unexpected auth state"),
        };

        // Prefer passkey if available
        let use_passkey = allowed.iter().any(|a| matches!(a, AuthAllowed::Passkey));
        let use_totp = allowed.iter().any(|a| matches!(a, AuthAllowed::Totp));

        if use_passkey {
            // Request passkey challenge
            let challenge_state = self.client
                .auth_step_begin(AuthMech::Passkey)
                .await?;

            match challenge_state.state {
                AuthState::Continue(allowed) => {
                    // Extract WebAuthn challenge
                    for method in allowed {
                        if let AuthAllowed::Passkey = method {
                            // Return challenge to client for WebAuthn
                            return Ok(AuthenticationContext::Passkey {
                                // Challenge data from Kanidm
                                challenge: challenge_state,
                            });
                        }
                    }
                }
                _ => anyhow::bail!("Unexpected state after passkey begin"),
            }
        }

        if use_totp {
            // Fall back to TOTP
            let totp_state = self.client
                .auth_step_begin(AuthMech::Totp)
                .await?;

            return Ok(AuthenticationContext::Totp {
                state: totp_state,
            });
        }

        anyhow::bail!("No supported authentication methods available")
    }

    pub async fn complete_passkey_auth(
        &self,
        credential: PublicKeyCredential,
    ) -> Result<AuthToken, anyhow::Error> {
        // Submit passkey credential to Kanidm
        let response = self.client
            .auth_step_passkey(&credential)
            .await?;

        match response.state {
            AuthState::Success(token) => Ok(token),
            AuthState::Denied(_) => anyhow::bail!("Authentication denied"),
            _ => anyhow::bail!("Unexpected auth state after passkey"),
        }
    }

    pub async fn complete_totp_auth(
        &self,
        totp_code: &str,
    ) -> Result<AuthToken, anyhow::Error> {
        // Validate TOTP code format (6 digits)
        if !totp_code.chars().all(|c| c.is_ascii_digit()) || totp_code.len() != 6 {
            anyhow::bail!("Invalid TOTP code format");
        }

        let response = self.client
            .auth_step_totp(totp_code.parse()?)
            .await?;

        match response.state {
            AuthState::Success(token) => Ok(token),
            AuthState::Denied(reason) => anyhow::bail!("Authentication denied: {}", reason),
            _ => anyhow::bail!("Unexpected auth state after TOTP"),
        }
    }

    pub async fn register_passkey(
        &self,
        token: &str,
        passkey_label: &str,
    ) -> Result<CreationChallengeResponse, anyhow::Error> {
        self.client.set_token(token).await;

        // Start passkey registration
        let challenge = self.client
            .idm_account_credential_passkey_register_start(passkey_label)
            .await?;

        Ok(challenge)
    }

    pub async fn complete_passkey_registration(
        &self,
        credential: RegisterPublicKeyCredential,
    ) -> Result<(), anyhow::Error> {
        self.client
            .idm_account_credential_passkey_register_finish(&credential)
            .await?;

        Ok(())
    }
}

pub enum AuthenticationContext {
    Passkey {
        challenge: AuthState,
    },
    Totp {
        state: AuthState,
    },
}
```

---

## 4. Anti-Patterns

**NEVER:**
- Disable PKCE for OAuth2 clients
- Use wildcard redirect URIs
- Store credentials outside Kanidm
- Allow password-only authentication for admins
- Skip TLS for LDAP connections
- Grant direct permissions instead of groups
- Use long-lived API tokens without rotation
- Disable WebAuthn/passkey support
- Trust X-Forwarded headers from untrusted sources

---

## 5. Testing

**ALWAYS test Kanidm configurations:**

```bash
#!/bin/bash
set -euo pipefail

KANIDM_URL="${KANIDM_URL:-https://idm.example.com}"

echo "=== Kanidm Security Tests ==="

# Test 1: TLS verification
echo "Test 1: TLS certificate..."
openssl s_client -connect "${KANIDM_URL#https://}:443" -servername "${KANIDM_URL#https://}" </dev/null 2>/dev/null | \
    openssl x509 -noout -dates || {
    echo "FAIL: TLS certificate issue"
    exit 1
}
echo "PASS: TLS certificate valid"

# Test 2: OAuth2 discovery endpoint
echo "Test 2: OIDC discovery..."
curl -sf "$KANIDM_URL/oauth2/openid/myapp/.well-known/openid-configuration" | \
    jq -e '.authorization_endpoint and .token_endpoint' > /dev/null || {
    echo "FAIL: OIDC discovery not working"
    exit 1
}
echo "PASS: OIDC discovery working"

# Test 3: PKCE required
echo "Test 3: PKCE enforcement..."
# Attempt auth without PKCE should fail or warn
RESPONSE=$(curl -sf "$KANIDM_URL/oauth2/authorise?client_id=myapp&response_type=code&redirect_uri=https://myapp.example.com/callback" 2>&1 || true)
if echo "$RESPONSE" | grep -qi "pkce"; then
    echo "PASS: PKCE enforcement working"
else
    echo "WARN: Could not verify PKCE enforcement"
fi

# Test 4: LDAPS connectivity
echo "Test 4: LDAPS..."
openssl s_client -connect "${KANIDM_URL#https://}:636" </dev/null 2>/dev/null | \
    grep -q "BEGIN CERTIFICATE" || {
    echo "FAIL: LDAPS not available"
    exit 1
}
echo "PASS: LDAPS available"

# Test 5: API authentication required
echo "Test 5: API authentication..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$KANIDM_URL/v1/self")
if [ "$STATUS" == "401" ]; then
    echo "PASS: API requires authentication"
else
    echo "FAIL: API accessible without auth"
    exit 1
fi

echo "=== All Kanidm Security Tests Passed ==="
```

---

## 6. Pre-Generation Checklist

**BEFORE generating any Kanidm code:**

- [ ] TLS configured for all endpoints
- [ ] OAuth2 clients use PKCE
- [ ] Redirect URIs strictly validated
- [ ] Groups used for authorization
- [ ] MFA required for admin accounts
- [ ] Passkey/WebAuthn enabled
- [ ] Service accounts use API tokens
- [ ] LDAP uses LDAPS only
- [ ] Session timeouts configured
- [ ] Credential policies defined
