## 2. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```python
# tests/test_browser_automation.py
import pytest
from playwright.sync_api import Page, expect

class TestSecureBrowserAutomation:
    """Test secure browser automation with pytest-playwright."""

    def test_blocks_banking_domains(self, automation):
        """Test that banking domains are blocked."""
        with pytest.raises(SecurityError, match="URL blocked"):
            automation.navigate("https://chase.com")

    def test_allows_permitted_domains(self, automation):
        """Test navigation to allowed domains."""
        automation.navigate("https://example.com")
        assert "Example" in automation.page.title()

    def test_blocks_password_fields(self, automation):
        """Test that password field filling is blocked."""
        automation.navigate("https://example.com/form")
        with pytest.raises(SecurityError, match="password"):
            automation.fill('input[type="password"]', "secret")

    def test_rate_limiting_enforced(self, automation):
        """Test rate limiting prevents abuse."""
        for _ in range(60):
            automation.check_request()
        with pytest.raises(RateLimitError):
            automation.check_request()

@pytest.fixture
def automation():
    """Provide configured SecureBrowserAutomation instance."""
    auto = SecureBrowserAutomation(
        domain_allowlist=['example.com'],
        permission_tier='standard'
    )
    auto.start_session()
    yield auto
    auto.close()
```

### Step 2: Implement Minimum to Pass

```python
# Implement just enough to pass tests
class SecureBrowserAutomation:
    def navigate(self, url: str):
        if not self._validate_url(url):
            raise SecurityError(f"URL blocked: {url}")
        self.page.goto(url)
```

### Step 3: Refactor Following Patterns

After tests pass, refactor to add:
- Proper error handling
- Audit logging
- Performance optimizations

### Step 4: Run Full Verification

```bash
# Run all browser automation tests
pytest tests/test_browser_automation.py -v --headed

# Run with coverage
pytest tests/test_browser_automation.py --cov=src/automation --cov-report=term-missing

# Run security-specific tests
pytest tests/test_browser_automation.py -k "security" -v
```

---

