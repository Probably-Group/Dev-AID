# Kanidm Implementation Workflow (TDD)

Follow this workflow for all Kanidm implementations:

## Step 1: Write Failing Test First

```python
# tests/test_kanidm_oauth2.py
import pytest
import httpx

class TestOAuth2Integration:
    """Test OAuth2/OIDC integration with Kanidm."""

    @pytest.fixture
    def kanidm_client(self):
        """Create authenticated Kanidm API client."""
        return httpx.Client(
            base_url="https://idm.example.com",
            verify=True,
            timeout=30.0
        )

    def test_oauth2_client_registration(self, kanidm_client):
        """Test OAuth2 client is properly registered."""
        # This test will fail until implementation
        response = kanidm_client.get(
            "/oauth2/openid/myapp/.well-known/openid-configuration"
        )
        assert response.status_code == 200
        config = response.json()
        assert "authorization_endpoint" in config
        assert "token_endpoint" in config
        assert "userinfo_endpoint" in config

    def test_oauth2_scopes_configured(self, kanidm_client):
        """Test required scopes are enabled."""
        response = kanidm_client.get(
            "/oauth2/openid/myapp/.well-known/openid-configuration"
        )
        config = response.json()
        scopes = config.get("scopes_supported", [])

        required_scopes = ["openid", "email", "profile", "groups"]
        for scope in required_scopes:
            assert scope in scopes, f"Missing scope: {scope}"

    def test_token_exchange_flow(self, kanidm_client):
        """Test token exchange with authorization code."""
        # Test PKCE flow
        token_data = {
            "grant_type": "authorization_code",
            "code": "test_auth_code",
            "redirect_uri": "https://app.example.com/callback",
            "code_verifier": "test_verifier"
        }
        response = kanidm_client.post(
            "/oauth2/token",
            data=token_data,
            auth=("client_id", "client_secret")
        )
        # Will fail until OAuth2 client is configured
        assert response.status_code in [200, 400]  # 400 for invalid code is OK
```

```python
# tests/test_kanidm_ldap.py
import ldap3

class TestLDAPIntegration:
    """Test LDAP integration with Kanidm."""

    def test_ldap_connection(self):
        """Test LDAPS connection to Kanidm."""
        server = ldap3.Server(
            "ldaps://idm.example.com:3636",
            use_ssl=True,
            get_info=ldap3.ALL
        )
        conn = ldap3.Connection(
            server,
            user="name=ldap_bind,dc=idm,dc=example,dc=com",
            password="test_password",
            auto_bind=True
        )
        assert conn.bound, "LDAP bind failed"
        conn.unbind()

    def test_user_search(self):
        """Test LDAP user search."""
        # Setup connection...
        conn.search(
            "dc=idm,dc=example,dc=com",
            "(uid=jsmith)",
            attributes=["uid", "mail", "displayName", "memberOf"]
        )
        assert len(conn.entries) == 1
        user = conn.entries[0]
        assert user.uid.value == "jsmith"
        assert user.mail.value is not None

    def test_group_membership(self):
        """Test user group memberships via LDAP."""
        # Verify user is in expected groups
        conn.search(
            "dc=idm,dc=example,dc=com",
            "(uid=jsmith)",
            attributes=["memberOf"]
        )
        groups = conn.entries[0].memberOf.values
        assert "developers" in str(groups)
```

```bash
# tests/test_kanidm_config.sh
#!/bin/bash
# Test Kanidm configuration

set -e

echo "Testing Kanidm server connectivity..."
curl -sf https://idm.example.com/status || exit 1

echo "Testing OAuth2 endpoint..."
curl -sf https://idm.example.com/oauth2/openid/myapp/.well-known/openid-configuration || exit 1

echo "Testing LDAPS connectivity..."
ldapsearch -H ldaps://idm.example.com:3636 \
  -D "name=ldap_bind,dc=idm,dc=example,dc=com" \
  -w "$LDAP_BIND_PASSWORD" \
  -b "dc=idm,dc=example,dc=com" \
  "(objectClass=*)" -LLL | head -1 || exit 1

echo "Testing user existence..."
kanidm person get jsmith || exit 1

echo "Testing group membership..."
kanidm group list-members developers | grep -q jsmith || exit 1

echo "All tests passed!"
```

## Step 2: Implement Minimum to Pass

```bash
# Implement OAuth2 client registration
kanidm oauth2 create myapp "My Application" \
  --origin https://app.example.com

kanidm oauth2 add-redirect-url myapp \
  https://app.example.com/callback

kanidm oauth2 enable-scope myapp openid email profile groups

# Implement LDAP bind account
kanidm service-account create ldap_bind "LDAP Bind Account"
kanidm service-account credential set-password ldap_bind
kanidm group add-members idm_account_read_priv ldap_bind

# Implement user and group
kanidm person create jsmith "John Smith" --mail john.smith@example.com
kanidm group add-members developers jsmith
```

## Step 3: Refactor if Needed

```bash
# Add security hardening
kanidm oauth2 enable-pkce myapp
kanidm oauth2 set-token-lifetime myapp --access 3600 --refresh 86400

# Add scope mapping for authorization
kanidm oauth2 create-scope-map myapp groups developers admins
```

## Step 4: Run Full Verification

```bash
# Run all tests
pytest tests/test_kanidm_*.py -v

# Run integration tests
bash tests/test_kanidm_config.sh

# Verify security configuration
kanidm oauth2 get myapp | grep -q "pkce_enabled: true"
kanidm audit-log export --since "1 hour ago" --format json | jq .
```
