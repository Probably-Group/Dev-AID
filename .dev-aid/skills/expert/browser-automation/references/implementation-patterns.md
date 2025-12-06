## 7. Implementation Patterns

### Pattern 1: Secure Browser Session

```python
from playwright.sync_api import sync_playwright
import logging
import re
from urllib.parse import urlparse

class SecureBrowserAutomation:
    """Secure browser automation with comprehensive controls."""

    BLOCKED_DOMAINS = {
        'chase.com', 'bankofamerica.com', 'wellsfargo.com',
        'accounts.google.com', 'login.microsoft.com',
        'paypal.com', 'venmo.com', 'stripe.com',
    }

    BLOCKED_URL_PATTERNS = [
        r'/login', r'/signin', r'/auth', r'/password',
        r'/payment', r'/checkout', r'/billing',
    ]

    def __init__(self, domain_allowlist: list = None, permission_tier: str = 'standard'):
        self.domain_allowlist = domain_allowlist
        self.permission_tier = permission_tier
        self.logger = logging.getLogger('browser.security')
        self.timeout = 30000

    def start_session(self):
        """Start browser with security settings."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=True,
            args=['--disable-extensions', '--disable-plugins', '--no-sandbox']
        )
        self.context = self.browser.new_context(ignore_https_errors=False)
        self.context.set_default_timeout(self.timeout)
        self.page = self.context.new_page()

    def navigate(self, url: str):
        """Navigate with URL validation."""
        if not self._validate_url(url):
            raise SecurityError(f"URL blocked: {url}")
        self._audit_log('navigate', url)
        self.page.goto(url, wait_until='networkidle')

    def _validate_url(self, url: str) -> bool:
        """Validate URL against security rules."""
        parsed = urlparse(url)
        domain = parsed.netloc.lower().removeprefix('www.')
        if any(domain == d or domain.endswith('.' + d) for d in self.BLOCKED_DOMAINS):
            return False
        if self.domain_allowlist:
            if not any(domain == d or domain.endswith('.' + d) for d in self.domain_allowlist):
                return False
        return not any(re.search(p, url, re.I) for p in self.BLOCKED_URL_PATTERNS)

    def close(self):
        """Clean up browser session."""
        if hasattr(self, 'context'):
            self.context.clear_cookies()
            self.context.close()
        if hasattr(self, 'browser'):
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
```

### Pattern 2: Rate Limiting

```python
import time

class BrowserRateLimiter:
    """Rate limit browser operations."""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.request_times = []

    def check_request(self):
        """Check if request is allowed."""
        cutoff = time.time() - 60
        self.request_times = [t for t in self.request_times if t > cutoff]
        if len(self.request_times) >= self.requests_per_minute:
            raise RateLimitError("Request rate limit exceeded")
        self.request_times.append(time.time())
```

---

