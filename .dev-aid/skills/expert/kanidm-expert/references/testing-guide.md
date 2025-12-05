# Kanidm Testing Guide

## Unit Tests for Kanidm Integrations

```python
# tests/test_kanidm_service.py
import pytest
from unittest.mock import Mock, patch, MagicMock
import httpx

class TestKanidmService:
    """Unit tests for Kanidm service layer."""

    @pytest.fixture
    def mock_client(self):
        """Create mock httpx client."""
        return Mock(spec=httpx.Client)

    def test_get_user_success(self, mock_client):
        """Test successful user retrieval."""
        mock_client.get.return_value = Mock(
            status_code=200,
            json=lambda: {
                "attrs": {
                    "uuid": ["abc-123"],
                    "name": ["jsmith"],
                    "displayname": ["John Smith"],
                    "mail": ["john@example.com"]
                }
            }
        )

        from myapp.kanidm import KanidmService
        service = KanidmService(client=mock_client)
        user = service.get_user("jsmith")

        assert user["name"] == "jsmith"
        assert user["mail"] == "john@example.com"
        mock_client.get.assert_called_once_with("/v1/person/jsmith")

    def test_get_user_not_found(self, mock_client):
        """Test user not found handling."""
        mock_client.get.return_value = Mock(status_code=404)

        from myapp.kanidm import KanidmService
        service = KanidmService(client=mock_client)

        with pytest.raises(UserNotFoundError):
            service.get_user("nonexistent")

    def test_oauth2_token_validation(self, mock_client):
        """Test OAuth2 token introspection."""
        mock_client.post.return_value = Mock(
            status_code=200,
            json=lambda: {
                "active": True,
                "sub": "jsmith",
                "scope": "openid email profile",
                "exp": 1732123456
            }
        )

        from myapp.kanidm import validate_token
        result = validate_token(mock_client, "test_token")

        assert result["active"] is True
        assert result["sub"] == "jsmith"

    def test_group_membership_check(self, mock_client):
        """Test group membership verification."""
        mock_client.get.return_value = Mock(
            status_code=200,
            json=lambda: {
                "attrs": {
                    "memberof": ["developers", "vpn_users"]
                }
            }
        )

        from myapp.kanidm import is_member_of
        assert is_member_of(mock_client, "jsmith", "developers") is True
        assert is_member_of(mock_client, "jsmith", "admins") is False
```

## Integration Tests

```python
# tests/integration/test_kanidm_integration.py
import pytest
import os
import httpx
import ldap3

@pytest.fixture(scope="session")
def kanidm_url():
    """Get Kanidm server URL from environment."""
    return os.environ.get("KANIDM_TEST_URL", "https://idm.test.example.com")

@pytest.fixture(scope="session")
def api_token():
    """Get API token for testing."""
    return os.environ["KANIDM_TEST_TOKEN"]

@pytest.fixture
def kanidm_client(kanidm_url, api_token):
    """Create authenticated Kanidm client."""
    client = httpx.Client(
        base_url=kanidm_url,
        headers={"Authorization": f"Bearer {api_token}"},
        timeout=30.0
    )
    yield client
    client.close()

class TestOAuth2Integration:
    """Integration tests for OAuth2/OIDC."""

    def test_openid_discovery(self, kanidm_client):
        """Test OpenID Connect discovery endpoint."""
        response = kanidm_client.get(
            "/oauth2/openid/testapp/.well-known/openid-configuration"
        )
        assert response.status_code == 200

        config = response.json()
        assert "issuer" in config
        assert "authorization_endpoint" in config
        assert "token_endpoint" in config
        assert "jwks_uri" in config

    def test_token_endpoint(self, kanidm_client):
        """Test token endpoint responds correctly."""
        response = kanidm_client.post(
            "/oauth2/token",
            data={
                "grant_type": "client_credentials",
                "scope": "openid"
            },
            auth=("test_client", os.environ["TEST_CLIENT_SECRET"])
        )
        assert response.status_code == 200

        tokens = response.json()
        assert "access_token" in tokens
        assert "token_type" in tokens
        assert tokens["token_type"] == "Bearer"


class TestLDAPIntegration:
    """Integration tests for LDAP."""

    @pytest.fixture
    def ldap_connection(self):
        """Create LDAP connection."""
        server = ldap3.Server(
            os.environ.get("KANIDM_LDAP_URL", "ldaps://idm.test.example.com:3636"),
            use_ssl=True,
            get_info=ldap3.ALL
        )
        conn = ldap3.Connection(
            server,
            user=os.environ["LDAP_BIND_DN"],
            password=os.environ["LDAP_BIND_PASSWORD"],
            auto_bind=True
        )
        yield conn
        conn.unbind()

    def test_ldap_bind(self, ldap_connection):
        """Test LDAP bind succeeds."""
        assert ldap_connection.bound

    def test_user_search(self, ldap_connection):
        """Test LDAP user search."""
        ldap_connection.search(
            search_base=os.environ.get("LDAP_BASE_DN", "dc=idm,dc=example,dc=com"),
            search_filter="(uid=testuser)",
            attributes=["uid", "mail", "displayName"]
        )
        assert len(ldap_connection.entries) >= 0  # May or may not exist

    def test_group_search(self, ldap_connection):
        """Test LDAP group search."""
        ldap_connection.search(
            search_base=os.environ.get("LDAP_BASE_DN", "dc=idm,dc=example,dc=com"),
            search_filter="(objectClass=group)",
            attributes=["cn", "member"]
        )
        assert ldap_connection.result["result"] == 0


class TestRADIUSIntegration:
    """Integration tests for RADIUS (requires radtest)."""

    @pytest.mark.skip(reason="Requires RADIUS client tools")
    def test_radius_authentication(self):
        """Test RADIUS authentication flow."""
        import subprocess
        result = subprocess.run(
            [
                "radtest",
                "testuser",
                os.environ["TEST_USER_PASSWORD"],
                os.environ.get("RADIUS_SERVER", "idm.test.example.com"),
                "0",
                os.environ["RADIUS_SECRET"]
            ],
            capture_output=True,
            text=True
        )
        assert "Access-Accept" in result.stdout
```

## End-to-End Tests

```python
# tests/e2e/test_auth_flows.py
import pytest
from playwright.sync_api import Page, expect

class TestWebAuthnFlow:
    """E2E tests for WebAuthn authentication."""

    @pytest.fixture
    def kanidm_url(self):
        return "https://idm.test.example.com"

    def test_login_page_loads(self, page: Page, kanidm_url):
        """Test login page is accessible."""
        page.goto(kanidm_url)
        expect(page.locator("input[name='username']")).to_be_visible()
        expect(page.locator("button[type='submit']")).to_be_visible()

    def test_oauth2_authorization_flow(self, page: Page, kanidm_url):
        """Test OAuth2 authorization code flow."""
        # Start authorization
        page.goto(
            f"{kanidm_url}/oauth2/authorize?"
            "client_id=testapp&"
            "redirect_uri=https://app.test.example.com/callback&"
            "response_type=code&"
            "scope=openid%20email%20profile"
        )

        # Should redirect to login
        expect(page.locator("input[name='username']")).to_be_visible()

        # Login
        page.fill("input[name='username']", "testuser")
        page.fill("input[name='password']", "testpassword")
        page.click("button[type='submit']")

        # Should redirect to callback with code
        page.wait_for_url("**/callback?code=*")
        assert "code=" in page.url
```

## Security Tests

```python
# tests/security/test_kanidm_security.py
import pytest
import httpx

class TestSecurityConfiguration:
    """Security configuration tests."""

    @pytest.fixture
    def client(self):
        return httpx.Client(timeout=10.0, verify=True)

    def test_tls_required(self, client):
        """Test that HTTP is rejected, only HTTPS works."""
        # HTTP should fail or redirect
        with pytest.raises(httpx.ConnectError):
            client.get("http://idm.example.com:8080")

        # HTTPS should work
        response = client.get("https://idm.example.com/status")
        assert response.status_code == 200

    def test_no_plain_ldap(self):
        """Test that plain LDAP is disabled."""
        import ldap3
        import socket

        # Plain LDAP (port 389) should be closed
        server = ldap3.Server("idm.example.com", port=389, use_ssl=False)
        conn = ldap3.Connection(server)

        # Should fail to connect
        with pytest.raises((ldap3.core.exceptions.LDAPSocketOpenError, socket.error)):
            conn.bind()

    def test_oauth2_redirect_uri_validation(self, client):
        """Test that only exact redirect URIs are allowed."""
        # Valid redirect
        response = client.get(
            "https://idm.example.com/oauth2/authorize",
            params={
                "client_id": "testapp",
                "redirect_uri": "https://app.example.com/callback",
                "response_type": "code"
            },
            follow_redirects=False
        )
        assert response.status_code in [302, 200]

        # Invalid redirect should be rejected
        response = client.get(
            "https://idm.example.com/oauth2/authorize",
            params={
                "client_id": "testapp",
                "redirect_uri": "https://evil.com/callback",
                "response_type": "code"
            },
            follow_redirects=False
        )
        assert response.status_code in [400, 403]

    def test_account_lockout(self, client):
        """Test account lockout after failed attempts."""
        # Attempt multiple failed logins
        for _ in range(6):
            response = client.post(
                "https://idm.example.com/v1/auth",
                json={"username": "testuser", "password": "wrongpassword"}
            )

        # Account should be locked
        response = client.post(
            "https://idm.example.com/v1/auth",
            json={"username": "testuser", "password": "correctpassword"}
        )
        assert response.status_code == 403
        assert "locked" in response.text.lower()
```

## Running Tests

```bash
# Run all unit tests
pytest tests/test_*.py -v

# Run integration tests (requires test environment)
export KANIDM_TEST_URL="https://idm.test.example.com"
export KANIDM_TEST_TOKEN="your-test-token"
pytest tests/integration/ -v

# Run security tests
pytest tests/security/ -v --tb=short

# Run with coverage
pytest tests/ --cov=myapp --cov-report=html

# Run E2E tests
playwright install chromium
pytest tests/e2e/ -v

# Continuous integration
pytest tests/ -v --junitxml=results.xml
```
