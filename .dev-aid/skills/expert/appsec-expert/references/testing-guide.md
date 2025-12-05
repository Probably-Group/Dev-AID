# Security Testing Guide (TDD Approach)

## Overview

Test-Driven Development (TDD) for security ensures security controls are testable, verifiable, and correct. Always write security tests before implementing security features.

---

## TDD Security Workflow

### Step 1: Write Failing Security Test First

Write comprehensive security tests that verify the security control behavior BEFORE implementing the control.

```python
# tests/test_auth_security.py
import pytest
from app.auth import SecureAuth, InputValidator

class TestPasswordSecurity:
    """Security tests for password handling"""

    def test_rejects_weak_password(self):
        """Password must meet minimum requirements"""
        auth = SecureAuth()
        with pytest.raises(ValueError, match="at least 12 characters"):
            auth.hash_password("short")

    def test_password_hash_uses_argon2(self):
        """Must use Argon2id algorithm"""
        auth = SecureAuth()
        hashed = auth.hash_password("SecurePassword123!")
        assert hashed.startswith("$argon2id$")

    def test_different_salts_per_hash(self):
        """Each hash must have unique salt"""
        auth = SecureAuth()
        hash1 = auth.hash_password("TestPassword123!")
        hash2 = auth.hash_password("TestPassword123!")
        assert hash1 != hash2

    def test_verify_correct_password(self):
        """Correct password should verify"""
        auth = SecureAuth()
        password = "SecurePassword123!"
        hashed = auth.hash_password(password)
        assert auth.verify_password(password, hashed) is True

    def test_verify_incorrect_password(self):
        """Incorrect password should not verify"""
        auth = SecureAuth()
        hashed = auth.hash_password("SecurePassword123!")
        assert auth.verify_password("WrongPassword!", hashed) is False

class TestInputValidation:
    """Security tests for input validation"""

    def test_rejects_sql_injection_in_email(self):
        """Must reject SQL injection attempts"""
        assert not InputValidator.validate_email("admin'--@test.com")
        assert not InputValidator.validate_email("test@test.com'; DROP TABLE users--")

    def test_rejects_xss_in_username(self):
        """Must reject XSS payloads"""
        assert not InputValidator.validate_username("<script>alert(1)</script>")
        assert not InputValidator.validate_username("user<img src=x onerror=alert(1)>")

    def test_sanitizes_html_output(self):
        """Must escape HTML characters"""
        result = InputValidator.sanitize_html("<script>alert(1)</script>")
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_accepts_valid_email(self):
        """Valid emails should be accepted"""
        assert InputValidator.validate_email("user@example.com")
        assert InputValidator.validate_email("test.user+tag@domain.co.uk")

    def test_accepts_valid_username(self):
        """Valid usernames should be accepted"""
        assert InputValidator.validate_username("validuser123")
        assert InputValidator.validate_username("user_name")

class TestAuthorizationChecks:
    """Security tests for authorization"""

    def test_user_cannot_access_admin_endpoint(self):
        """Regular user must not access admin endpoints"""
        client = TestClient()
        response = client.get("/admin/users", headers={"role": "user"})
        assert response.status_code == 403

    def test_admin_can_access_admin_endpoint(self):
        """Admin user must access admin endpoints"""
        client = TestClient()
        response = client.get("/admin/users", headers={"role": "admin"})
        assert response.status_code == 200

    def test_anonymous_redirected_to_login(self):
        """Unauthenticated requests must redirect to login"""
        client = TestClient()
        response = client.get("/profile", allow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]
```

---

### Step 2: Implement Minimum Security Control

Implement just enough code to make the security tests pass. Start simple, then refactor.

```python
# app/auth.py - Implement to pass tests
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import re
from html import escape

class SecureAuth:
    """Secure authentication using Argon2id"""

    def __init__(self):
        # OWASP recommended parameters for Argon2id
        self.ph = PasswordHasher(
            time_cost=3,        # Iterations
            memory_cost=65536,  # 64 MB
            parallelism=4       # Threads
        )

    def hash_password(self, password: str) -> str:
        """Hash password with Argon2id"""
        if len(password) < 12:
            raise ValueError("Password must be at least 12 characters")
        return self.ph.hash(password)

    def verify_password(self, password: str, hash: str) -> bool:
        """Verify password against hash"""
        try:
            self.ph.verify(hash, password)
            return True
        except VerifyMismatchError:
            return False


class InputValidator:
    """Input validation using allowlist approach"""

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email using strict regex"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email)) and len(email) <= 254

    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username - alphanumeric only, 3-20 chars"""
        pattern = r'^[a-zA-Z0-9_]{3,20}$'
        return bool(re.match(pattern, username))

    @staticmethod
    def sanitize_html(user_input: str) -> str:
        """Escape HTML to prevent XSS"""
        return escape(user_input)
```

---

### Step 3: Run Security Verification

Run all security tests and scanning tools to verify implementation.

```bash
# Run security tests
pytest tests/test_auth_security.py -v

# Run SAST analysis
semgrep --config=auto app/

# Run secrets detection
gitleaks detect --source=. --verbose

# Run dependency check
pip-audit

# Run full test suite
pytest tests/ -v --cov=app --cov-report=term-missing
```

**Expected Output**:
```
tests/test_auth_security.py::TestPasswordSecurity::test_rejects_weak_password PASSED
tests/test_auth_security.py::TestPasswordSecurity::test_password_hash_uses_argon2 PASSED
tests/test_auth_security.py::TestPasswordSecurity::test_different_salts_per_hash PASSED
tests/test_auth_security.py::TestInputValidation::test_rejects_sql_injection_in_email PASSED
tests/test_auth_security.py::TestInputValidation::test_rejects_xss_in_username PASSED
tests/test_auth_security.py::TestInputValidation::test_sanitizes_html_output PASSED

========================== 6 passed in 0.42s ==========================
```

---

## Security Test Categories

### 1. Authentication Tests

```python
class TestAuthenticationSecurity:
    """Test authentication mechanisms"""

    def test_login_requires_valid_credentials(self):
        """Login must require valid username and password"""
        response = login("invalid_user", "invalid_pass")
        assert response.status_code == 401

    def test_login_rate_limiting(self):
        """Must rate limit failed login attempts"""
        for _ in range(5):
            login("user", "wrong_password")

        # 6th attempt should be rate limited
        response = login("user", "wrong_password")
        assert response.status_code == 429  # Too Many Requests

    def test_session_expires_after_timeout(self):
        """Session must expire after inactivity"""
        session = create_session(user_id=1)
        time.sleep(SESSION_TIMEOUT + 1)
        assert is_session_valid(session.id) is False

    def test_logout_invalidates_session(self):
        """Logout must invalidate session token"""
        session = create_session(user_id=1)
        logout(session.id)
        assert is_session_valid(session.id) is False
```

### 2. Authorization Tests

```python
class TestAuthorizationSecurity:
    """Test authorization controls"""

    def test_user_can_only_access_own_data(self):
        """User must only access their own resources"""
        user1 = create_user("user1")
        user2 = create_user("user2")

        response = get_profile(user_id=user2.id, requester=user1)
        assert response.status_code == 403

    def test_role_based_access_control(self):
        """RBAC must enforce role permissions"""
        user = create_user("user", roles=["user"])
        admin = create_user("admin", roles=["admin"])

        # User cannot delete
        assert can_delete_user(user, target_id=999) is False
        # Admin can delete
        assert can_delete_user(admin, target_id=999) is True
```

### 3. Injection Prevention Tests

```python
class TestInjectionPrevention:
    """Test injection attack prevention"""

    def test_sql_injection_prevented(self):
        """SQL injection must be prevented"""
        malicious_input = "' OR '1'='1'; DROP TABLE users--"
        result = search_users(username=malicious_input)
        assert result == []  # No results, no error

    def test_command_injection_prevented(self):
        """Command injection must be prevented"""
        malicious_filename = "file.txt; rm -rf /"
        with pytest.raises(ValueError):
            process_file(malicious_filename)

    def test_ldap_injection_prevented(self):
        """LDAP injection must be prevented"""
        malicious_username = "admin)(|(uid=*))"
        with pytest.raises(ValueError):
            ldap_search(username=malicious_username)
```

### 4. Cryptography Tests

```python
class TestCryptographySecurity:
    """Test cryptographic implementations"""

    def test_uses_secure_random(self):
        """Must use cryptographically secure random"""
        token1 = generate_token()
        token2 = generate_token()
        assert token1 != token2
        assert len(token1) >= 32  # Minimum 256 bits

    def test_encryption_uses_authenticated_encryption(self):
        """Must use authenticated encryption (AES-GCM)"""
        plaintext = "sensitive data"
        ciphertext = encrypt(plaintext)

        # Verify AEAD tag prevents tampering
        tampered = ciphertext[:-1] + b'X'
        with pytest.raises(DecryptionError):
            decrypt(tampered)

    def test_jwt_signature_verified(self):
        """JWT signatures must be verified"""
        valid_token = create_jwt(user_id=1)
        tampered_token = valid_token[:-10] + "tampered99"

        with pytest.raises(InvalidSignatureError):
            verify_jwt(tampered_token)
```

---

## Integration Testing with Security

### API Security Tests

```python
# tests/test_api_security.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAPISecurityHeaders:
    """Test security headers in API responses"""

    def test_hsts_header_present(self):
        """HSTS header must be present"""
        response = client.get("/")
        assert "Strict-Transport-Security" in response.headers

    def test_csp_header_present(self):
        """CSP header must be present"""
        response = client.get("/")
        assert "Content-Security-Policy" in response.headers

    def test_no_server_header(self):
        """Server header must not leak version info"""
        response = client.get("/")
        server_header = response.headers.get("Server", "")
        assert "version" not in server_header.lower()

class TestAPICORS:
    """Test CORS configuration"""

    def test_cors_restricts_origins(self):
        """CORS must not allow all origins"""
        response = client.options(
            "/api/data",
            headers={"Origin": "https://evil.com"}
        )
        assert response.headers.get("Access-Control-Allow-Origin") != "*"

    def test_cors_allows_whitelisted_origin(self):
        """CORS must allow whitelisted origins"""
        response = client.options(
            "/api/data",
            headers={"Origin": "https://trusted.com"}
        )
        assert "Access-Control-Allow-Origin" in response.headers
```

---

## Security Test Automation in CI/CD

### pytest Configuration

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Security-specific markers
markers =
    security: Security-focused tests
    critical: Critical security tests (must pass)
    integration: Integration security tests
    auth: Authentication tests
    authz: Authorization tests
    injection: Injection prevention tests
```

### Run Only Security Tests

```bash
# Run all security tests
pytest -m security -v

# Run critical security tests
pytest -m critical -v

# Run authentication tests
pytest -m auth -v
```

### CI/CD Integration

```yaml
# .github/workflows/security.yml
name: Security Testing

on: [push, pull_request]

jobs:
  security-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Security Tests
        run: pytest -m security -v

      - name: Run SAST
        run: semgrep --config=auto . --sarif -o semgrep.sarif

      - name: Run Secrets Scan
        run: gitleaks detect --source=. --verbose

      - name: Run Dependency Audit
        run: pip-audit

      - name: Upload Results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: semgrep.sarif
```

---

## Coverage Requirements

Security-critical code must have 100% test coverage:

```bash
# Check coverage for auth module
pytest tests/test_auth_security.py --cov=app.auth --cov-report=term-missing --cov-fail-under=100

# Coverage report
app/auth.py                     50     0    100%
```

**Critical modules requiring 100% coverage**:
- Authentication (`app/auth.py`)
- Authorization (`app/authz.py`)
- Input validation (`app/validation.py`)
- Cryptography (`app/crypto.py`)
- Session management (`app/session.py`)

---

## Best Practices Summary

1. **Test First**: Always write security tests before implementing
2. **Test Negative Cases**: Test that attacks are blocked, not just happy paths
3. **Test Boundaries**: Test edge cases, empty inputs, max lengths
4. **Test Real Attacks**: Use actual attack payloads (SQLi, XSS, etc.)
5. **Test Authorization**: Verify users can only access authorized resources
6. **Test Cryptography**: Verify algorithms, key sizes, and secure defaults
7. **Automate in CI/CD**: Run security tests on every commit
8. **Require Coverage**: 100% coverage for security-critical code
9. **Document Tests**: Explain what attack each test prevents
10. **Keep Tests Fast**: Security tests should run in < 30 seconds

---

## Example: Complete TDD Security Feature

### Feature: API Rate Limiting

**Step 1: Write Tests**
```python
class TestRateLimiting:
    def test_allows_requests_under_limit(self):
        for _ in range(10):
            response = client.get("/api/data")
            assert response.status_code == 200

    def test_blocks_requests_over_limit(self):
        for _ in range(100):
            client.get("/api/data")

        response = client.get("/api/data")
        assert response.status_code == 429

    def test_reset_after_window(self):
        for _ in range(100):
            client.get("/api/data")

        time.sleep(61)  # Wait for rate limit window reset

        response = client.get("/api/data")
        assert response.status_code == 200
```

**Step 2: Implement**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/data")
@limiter.limit("100/minute")
async def get_data():
    return {"data": "value"}
```

**Step 3: Verify**
```bash
pytest tests/test_rate_limiting.py -v
semgrep --config=p/security-audit .
```

✅ **Result**: Feature is secure, tested, and verified before deployment.
