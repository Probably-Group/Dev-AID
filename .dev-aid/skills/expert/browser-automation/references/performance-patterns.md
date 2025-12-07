## 3. Performance Patterns

### Pattern 1: Browser Context Reuse

```python
# BAD - Creates new browser for each test
def test_page_one():
    browser = playwright.chromium.launch()
    page = browser.new_page()
    page.goto("https://example.com/one")
    browser.close()

def test_page_two():
    browser = playwright.chromium.launch()  # Slow startup again
    page = browser.new_page()
    page.goto("https://example.com/two")
    browser.close()

# GOOD - Reuse browser context
@pytest.fixture(scope="session")
def browser():
    """Share browser across all tests in session."""
    pw = sync_playwright().start()
    browser = pw.chromium.launch()
    yield browser
    browser.close()
    pw.stop()

@pytest.fixture
def page(browser):
    """Create fresh context per test for isolation."""
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()
```

### Pattern 2: Parallel Execution

```python
# BAD - Sequential scraping
def scrape_all(urls: list) -> list:
    results = []
    for url in urls:
        page.goto(url)
        results.append(page.content())
    return results  # Very slow for many URLs

# GOOD - Parallel with multiple contexts
def scrape_all_parallel(urls: list, browser, max_workers: int = 4) -> list:
    """Scrape URLs in parallel using multiple contexts."""
    from concurrent.futures import ThreadPoolExecutor, as_completed

    def scrape_url(url: str) -> str:
        context = browser.new_context()
        page = context.new_page()
        try:
            page.goto(url, wait_until='domcontentloaded')
            return page.content()
        finally:
            context.close()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(scrape_url, url): url for url in urls}
        return [future.result() for future in as_completed(futures)]
```

### Pattern 3: Network Interception for Speed

```python
# BAD - Load all resources
page.goto("https://example.com")  # Loads images, fonts, analytics

# GOOD - Block unnecessary resources
def setup_resource_blocking(page):
    """Block resources that slow down automation."""
    page.route("**/*", lambda route: (
        route.abort() if route.request.resource_type in [
            "image", "media", "font", "stylesheet"
        ] else route.continue_()
    ))

# Usage
setup_resource_blocking(page)
page.goto("https://example.com")  # 2-3x faster
```

### Pattern 4: Request Blocking for Analytics

```python
# BAD - Allow all tracking requests
page.goto(url)  # Slow due to analytics loading

# GOOD - Block tracking domains
BLOCKED_DOMAINS = [
    '*google-analytics.com*',
    '*googletagmanager.com*',
    '*facebook.com/tr*',
    '*doubleclick.net*',
]

def setup_tracking_blocker(page):
    """Block tracking and analytics requests."""
    for pattern in BLOCKED_DOMAINS:
        page.route(pattern, lambda route: route.abort())

# Apply before navigation
setup_tracking_blocker(page)
page.goto(url)  # Faster, no tracking overhead
```

### Pattern 5: Efficient Selectors

```python
# BAD - Slow selectors
page.locator("//div[@class='container']//span[contains(text(), 'Submit')]").click()
page.wait_for_selector(".dynamic-content", timeout=30000)

# GOOD - Fast, specific selectors
page.locator("[data-testid='submit-button']").click()  # Direct attribute
page.locator("#unique-id").click()  # ID is fastest

# GOOD - Use role selectors for accessibility
page.get_by_role("button", name="Submit").click()
page.get_by_label("Email").fill("test@example.com")

# GOOD - Combine selectors for specificity without XPath
page.locator("form.login >> button[type='submit']").click()
```

---


