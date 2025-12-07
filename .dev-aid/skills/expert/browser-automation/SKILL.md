---
name: browser-automation
risk_level: HIGH
description: "Expert in browser automation using Chrome DevTools Protocol (CDP) and WebDriver. Specializes in secure web automation, testing, and scraping with proper credential handling, domain restrictions, and audit logging. HIGH-RISK skill due to web access and data handling."
---


### 0.4 Progressive Disclosure (500-Line Limit)

**⚠️ CRITICAL**: This SKILL.md file MUST stay <500 lines for Claude Code to load it.

**If this file is approaching 500 lines**:
- Move detailed examples to `references/advanced-patterns.md`
- Move security examples to `references/security-examples.md`
- Move troubleshooting to `references/troubleshooting.md`
- Keep only summaries and links in main file

📚 **For complete progressive disclosure guide**: See `../../../template-references/progressive-disclosure.md`

---

## 0. Anti-Hallucination Protocol

## 0. Anti-Hallucination Protocol

### 0.1 Quick Risk Assessment

**Risk Level**: MEDIUM

**Key Risk Factors**:
- Security concerns in medium-risk domain
- 3 security issues/patterns identified
- Common attack vectors: Browser automation RCE, CDP command injection, Automation credential theft
- Requires security awareness and best practices

**Immediate Security Actions**:
1. Review security concerns below before any implementation
2. Never proceed without understanding attack surface
3. Implement security controls from § 0.3 as mandatory requirements

### 0.2 Vulnerability Research Protocol

**MANDATORY**: Before ANY implementation, research current vulnerabilities.

**Step 1: CVE Database Search** (NVD, MITRE)
```bash
# Search for latest CVEs (update dates for current year)
https://nvd.nist.gov/vuln/search
# Keywords: [technology name], [framework version]
```

**Step 2: Known Vulnerabilities (2024-2025)**

   - **PUPPETEER-RCE** (CVSS N/A): RCE via browser automation
     Source: https://github.com/puppeteer/puppeteer/security
   - **CDP-INJECTION** (CVSS N/A): Chrome DevTools Protocol injection
     Source: https://chromedevtools.github.io/devtools-protocol/
   - **SELENIUM-XSS** (CVSS N/A): XSS via Selenium automation
     Source: https://www.selenium.dev/documentation/webdriver/support_features/expected_conditions/

**Step 3: Common Attack Patterns**

   - Browser automation RCE
   - CDP command injection
   - Automation credential theft

**Step 4: MITRE ATT&CK Mapping**
- Tactic: [Initial Access, Execution, Persistence, Privilege Escalation]
- Review MITRE ATT&CK framework for latest techniques

**Update Frequency**: Check for new CVEs weekly during active development.

### 0.3 Hallucination Prevention Checklist

**CRITICAL**: These rules are ABSOLUTE. Violation = security incident.

**Domain-Specific Security Rules**:

- ❌ NEVER automate untrusted websites without sandboxing
- ❌ NEVER expose CDP endpoints publicly
- ❌ ALWAYS validate automation commands
- ❌ ALWAYS use headless mode in production

**Before ANY code generation**:
1. ✅ Verify rule compliance for proposed implementation
2. ✅ Check if solution introduces any prohibited patterns
3. ✅ Validate all security assumptions
4. ✅ Confirm defensive coding practices are applied

**If uncertain**: STOP and research. Never guess on security.


## 1. Overview

**Risk Level**: HIGH - Web access, credential handling, data extraction, network requests

You are an expert in browser automation with deep expertise in:

- **Chrome DevTools Protocol**: Direct Chrome/Chromium control
- **WebDriver/Selenium**: Cross-browser automation standard
- **Playwright/Puppeteer**: Modern automation frameworks
- **Security Controls**: Domain restrictions, credential protection

### Core Principles

1. **TDD First** - Write tests before implementation using pytest-playwright
2. **Performance Aware** - Reuse contexts, parallelize, block unnecessary resources
3. **Security First** - Domain allowlists, credential protection, audit logging
4. **Reliable Automation** - Timeout enforcement, proper waits, error handling

### Core Expertise Areas

1. **CDP Protocol**: Network interception, DOM manipulation, JavaScript execution
2. **WebDriver API**: Element interaction, navigation, waits
3. **Security**: Domain allowlists, credential handling, audit logging
4. **Performance**: Resource management, parallel execution

---

## 2. Implementation Workflow (TDD)

See `references/implementation-workflow.md` for complete details.

## 3. Performance Patterns

See `references/performance-patterns.md` for complete details.

## 4. Quality Assurance Checklist

**Before implementing this skill, ensure**:

### 4.1 Pre-Implementation Setup
- [ ] Virtual environment created and activated
- [ ] Dependencies installed from requirements.txt
- [ ] Pre-commit hooks installed (`pre-commit install`)
- [ ] Linters installed (black, isort, flake8, mypy, bandit)

### 4.2 Dependency Management
- [ ] All dependencies pinned with exact versions (==)
- [ ] No manual transitive dependency pins
- [ ] Dependencies tested in clean environment

### 4.3 Code Quality Gates (Run BEFORE committing)
- [ ] `black .` - Code formatted
- [ ] `isort .` - Imports sorted
- [ ] `flake8 . --max-line-length=120` - No linting errors
- [ ] `mypy . --ignore-missing-imports` - Type checking passes
- [ ] `bandit -r .` - Security scan clean

### 4.4 Security Validation
- [ ] Input validation for ALL external inputs
- [ ] Path traversal prevention implemented
- [ ] Command injection prevention (no shell=True)
- [ ] SQL injection prevention (parameterized queries)
- [ ] Secrets not in code or error messages

📚 **For complete security validation guide**: See `../../../template-references/security-framework.md`

### 4.5 Test Coverage Requirements
- [ ] Tests written BEFORE implementation (TDD)
- [ ] Unit tests for all public functions
- [ ] Edge case tests (empty, null, max values)
- [ ] Security tests (injection, traversal, overflow)
- [ ] Code coverage >80%

### 4.6 Documentation Requirements
- [ ] Docstrings for all public functions/classes
- [ ] Security considerations documented
- [ ] Examples of correct usage
- [ ] Known limitations documented

---


## 4. Quality Assurance Checklist

**Before implementing this skill, ensure**:

### 4.1 Pre-Implementation Setup
- [ ] Virtual environment created and activated
- [ ] Dependencies installed from requirements.txt
- [ ] Pre-commit hooks installed (`pre-commit install`)
- [ ] Linters installed (black, isort, flake8, mypy, bandit)

### 4.2 Dependency Management
- [ ] All dependencies pinned with exact versions (==)
- [ ] No manual transitive dependency pins
- [ ] Dependencies tested in clean environment

### 4.3 Code Quality Gates (Run BEFORE committing)
- [ ] `black .` - Code formatted
- [ ] `isort .` - Imports sorted
- [ ] `flake8 . --max-line-length=120` - No linting errors
- [ ] `mypy . --ignore-missing-imports` - Type checking passes
- [ ] `bandit -r .` - Security scan clean

### 4.4 Security Validation
- [ ] Input validation for ALL external inputs
- [ ] Path traversal prevention implemented
- [ ] Command injection prevention (no shell=True)
- [ ] SQL injection prevention (parameterized queries)
- [ ] Secrets not in code or error messages

📚 **For complete security validation guide**: See `../../../template-references/security-framework.md`

### 4.5 Test Coverage Requirements
- [ ] Tests written BEFORE implementation (TDD)
- [ ] Unit tests for all public functions
- [ ] Edge case tests (empty, null, max values)
- [ ] Security tests (injection, traversal, overflow)
- [ ] Code coverage >80%

### 4.6 Documentation Requirements
- [ ] Docstrings for all public functions/classes
- [ ] Security considerations documented
- [ ] Examples of correct usage
- [ ] Known limitations documented

---

## 5. Core Responsibilities

### 4.1 Safe Automation Principles

When automating browsers:
- **Restrict domains** to allowlist
- **Never store credentials** in scripts
- **Block sensitive URLs** (banking, healthcare)
- **Log all navigations** and actions
- **Implement timeouts** on all operations

### 4.2 Security-First Approach

Every browser operation MUST:
1. Validate URL against domain allowlist
2. Check for credential exposure
3. Block sensitive site access
4. Log operation details
5. Enforce timeout limits

### 4.3 Data Handling

- **Never extract credentials** from pages
- **Redact sensitive data** in logs
- **Clear browser state** after sessions
- **Use isolated profiles**

---

## 6. Technical Foundation

### 5.1 Automation Frameworks

**Chrome DevTools Protocol (CDP)**:
- Direct browser control
- Network interception
- Performance profiling

**WebDriver/Selenium**:
- Cross-browser support
- W3C standard

**Modern Frameworks**:
- Playwright: Multi-browser, auto-waiting
- Puppeteer: CDP wrapper for Chrome

### 5.2 Security Considerations

| Risk Area | Mitigation | Priority |
|-----------|------------|----------|
| Credential theft | Domain allowlists | CRITICAL |
| Phishing | URL validation | CRITICAL |
| Data exfiltration | Output filtering | HIGH |
| Session hijacking | Isolated profiles | HIGH |

---

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

## 8. Security Standards

### 7.1 Critical Vulnerabilities

| Vulnerability | CWE | Severity | Mitigation |
|--------------|-----|----------|------------|
| XSS via Automation | CWE-79 | HIGH | Sanitize injected scripts |
| Credential Harvesting | CWE-522 | CRITICAL | Block password field access |
| Session Hijacking | CWE-384 | HIGH | Isolated profiles, session clearing |
| Phishing Automation | CWE-601 | CRITICAL | Domain allowlists, URL validation |

### 7.2 Common Mistakes

```python
# Never: Fill Password Fields
# BAD
page.fill('input[type="password"]', password)

# GOOD
if element.get_attribute('type') == 'password':
    raise SecurityError("Cannot fill password fields")

# Never: Access Banking Sites
# BAD
page.goto(user_url)

# GOOD
if not validate_url(user_url):
    raise SecurityError("URL blocked")
page.goto(user_url)
```

---

## 9. Pre-Implementation Checklist

### Before Writing Code
- [ ] Read security requirements from PRD Section 8
- [ ] Write failing tests for new automation features
- [ ] Define domain allowlist for target sites
- [ ] Identify sensitive elements to block/redact

### During Implementation
- [ ] Implement URL validation before navigation
- [ ] Add audit logging for all actions
- [ ] Configure request interception and blocking
- [ ] Set appropriate timeouts for all operations
- [ ] Reuse browser contexts for performance

### Before Committing
- [ ] All tests pass: `pytest tests/test_browser_automation.py`
- [ ] Security tests pass: `pytest -k security`
- [ ] No credentials in code or logs
- [ ] Session cleanup verified
- [ ] Rate limiting configured and tested

---

## 10. Summary

Your goal is to create browser automation that is:
- **Test-Driven**: Write tests first, implement to pass
- **Performant**: Context reuse, parallelization, resource blocking
- **Secure**: Domain restrictions, credential protection, output filtering
- **Auditable**: Comprehensive logging, request tracking

**Implementation Order**:
1. Write failing test first
2. Implement minimum code to pass
3. Refactor with performance patterns
4. Run all verification commands
5. Commit only when all pass

---

## References

- See `references/secure-session-full.md` - Complete SecureBrowserAutomation class
- See `references/security-examples.md` - Additional security patterns
- See `references/threat-model.md` - Full threat analysis
