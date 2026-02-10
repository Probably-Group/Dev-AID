---
name: browser-automation
version: 2.0.0
description: "Browser automation with Puppeteer, Playwright, CDP, and WebDriver for testing, scraping, and web interaction. Use when automating browsers, web scraping, or end-to-end testing. Do NOT use for native app automation."
risk_level: HIGH
---

# Browser Automation Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-79: XSS via evaluate**
- NEVER: `page.evaluate(userString)` - execute user code
- ALWAYS: Parameterize, use `evaluateHandle` with sanitized data

**CWE-200: Credential Exposure**
- NEVER: Screenshot/video with credentials visible
- ALWAYS: Mask sensitive data, use environment variables for creds

**CWE-611: SSRF via Navigation**
- NEVER: `page.goto(userUrl)` without validation
- ALWAYS: Allowlist domains, validate URL format

### 0.3 Risk Level: HIGH

**Verification requirements for HIGH risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 No Arbitrary Code Execution (CWE-94)

**Principle:** Never execute untrusted code via page.evaluate(). Validate all data.

```typescript
// ❌ WRONG - Executing untrusted code
async function scrape(page: Page, userSelector: string) {
  // User could inject: '); document.cookie; //'
  return await page.evaluate(`document.querySelector('${userSelector}')`);
}

// ✅ CORRECT - Pass data as arguments, not code
async function scrape(page: Page, selector: string) {
  // Validate selector first
  if (!/^[a-zA-Z0-9\s\[\]\.#\-_="':>+~*]+$/.test(selector)) {
    throw new Error('Invalid selector');
  }

  return await page.evaluate((sel) => {
    return document.querySelector(sel)?.textContent;
  }, selector);  // Passed as argument, not interpolated
}
```

### 1.2 Credential Protection (CWE-798)

**Principle:** Never screenshot pages with credentials. Mask sensitive data.

```typescript
// ❌ WRONG - Screenshot might capture credentials
await page.type('#password', process.env.PASSWORD!);
await page.screenshot({ path: 'debug.png' });  // Password visible!

// ✅ CORRECT - Clear sensitive fields before screenshot
await page.type('#password', process.env.PASSWORD!);

// Mask before screenshot
await page.evaluate(() => {
  document.querySelectorAll('input[type="password"]').forEach(el => {
    (el as HTMLInputElement).value = '********';
  });
});
await page.screenshot({ path: 'debug.png' });
```

### 1.3 Input Validation (CWE-20)

**Principle:** Validate all URLs and selectors. Whitelist allowed domains.

### 1.4 Secrets ≠ Code (CWE-798)

**Principle:** Credentials from environment/vault only. Never log credentials.

### 1.5 Fail Secure (CWE-636)

**Principle:** On error, close browser. Don't leave sessions open.

### 1.6 Defense in Depth

**Principle:** Network isolation, proxy support, user-agent rotation.

---

## 2. Version Requirements

**ALWAYS use these minimum versions:**

```json
{
  "dependencies": {
    "playwright": "^1.41.0",
    "puppeteer": "^22.0.0",
    "zod": "^3.22.0"
  }
}
```

---

## 3. Code Patterns

### 3.1 WHEN setting up Playwright with security

```typescript
import { chromium, Browser, BrowserContext, Page } from 'playwright';

interface BrowserConfig {
  proxy?: { server: string; username?: string; password?: string };
  allowedDomains: string[];
  timeout: number;
}

export class SecureBrowser {
  private browser: Browser | null = null;
  private context: BrowserContext | null = null;
  private config: BrowserConfig;

  constructor(config: BrowserConfig) {
    this.config = config;
  }

  async launch(): Promise<void> {
    this.browser = await chromium.launch({
      headless: true,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-extensions',
        // Block dangerous features
        '--disable-background-networking',
        '--disable-default-apps',
        '--disable-sync',
      ],
    });

    this.context = await this.browser.newContext({
      // Limit permissions
      permissions: [],
      // Block geolocation
      geolocation: undefined,
      // Set user agent
      userAgent: 'Mozilla/5.0 (compatible; Bot/1.0)',
      // Proxy if configured
      proxy: this.config.proxy,
      // Timeout
      navigationTimeout: this.config.timeout,
    });

    // Block requests to non-allowed domains
    await this.context.route('**/*', async (route) => {
      const url = new URL(route.request().url());
      if (!this.config.allowedDomains.some(d => url.hostname.endsWith(d))) {
        await route.abort('blockedbyclient');
        return;
      }
      await route.continue();
    });
  }

  async newPage(): Promise<Page> {
    if (!this.context) throw new Error('Browser not launched');
    return await this.context.newPage();
  }

  async close(): Promise<void> {
    await this.context?.close();
    await this.browser?.close();
    this.context = null;
    this.browser = null;
  }
}

// Usage with cleanup guarantee
async function withBrowser<T>(
  config: BrowserConfig,
  fn: (browser: SecureBrowser) => Promise<T>
): Promise<T> {
  const browser = new SecureBrowser(config);
  try {
    await browser.launch();
    return await fn(browser);
  } finally {
    await browser.close();  // Always close
  }
}
```

### 3.2 WHEN implementing safe page navigation

```typescript
import { Page } from 'playwright';
import { z } from 'zod';

const UrlSchema = z.string().url().refine(
  (url) => {
    const parsed = new URL(url);
    return ['http:', 'https:'].includes(parsed.protocol);
  },
  { message: 'Only HTTP(S) URLs allowed' }
);

const ALLOWED_DOMAINS = ['example.com', 'api.example.com'];

async function navigateSafely(page: Page, url: string): Promise<void> {
  // Validate URL format
  const validatedUrl = UrlSchema.parse(url);

  // Check domain whitelist
  const parsed = new URL(validatedUrl);
  if (!ALLOWED_DOMAINS.some(d => parsed.hostname === d || parsed.hostname.endsWith(`.${d}`))) {
    throw new Error(`Domain not allowed: ${parsed.hostname}`);
  }

  // Navigate with timeout
  await page.goto(validatedUrl, {
    waitUntil: 'domcontentloaded',
    timeout: 30000,
  });

  // Verify we're on expected domain (no redirects to malicious sites)
  const currentUrl = new URL(page.url());
  if (!ALLOWED_DOMAINS.some(d => currentUrl.hostname === d || currentUrl.hostname.endsWith(`.${d}`))) {
    throw new Error(`Unexpected redirect to: ${currentUrl.hostname}`);
  }
}
```

### 3.3 WHEN extracting data safely

```typescript
import { Page } from 'playwright';
import { z } from 'zod';

// Define expected data schema
const ProductSchema = z.object({
  title: z.string().min(1).max(500),
  price: z.number().positive(),
  description: z.string().max(5000).optional(),
  url: z.string().url(),
});

type Product = z.infer<typeof ProductSchema>;

async function extractProduct(page: Page): Promise<Product | null> {
  // Extract data using page.evaluate with serializable return
  const rawData = await page.evaluate(() => {
    const title = document.querySelector('h1')?.textContent?.trim();
    const priceText = document.querySelector('.price')?.textContent;
    const price = priceText ? parseFloat(priceText.replace(/[^0-9.]/g, '')) : null;
    const description = document.querySelector('.description')?.textContent?.trim();

    return {
      title,
      price,
      description,
      url: window.location.href,
    };
  });

  // Validate extracted data
  const result = ProductSchema.safeParse(rawData);
  if (!result.success) {
    console.error('Invalid data extracted:', result.error);
    return null;
  }

  return result.data;
}
```

### 3.4 WHEN handling authentication securely

```typescript
import { Page, BrowserContext } from 'playwright';

interface Credentials {
  username: string;
  password: string;
}

async function authenticateSecurely(
  context: BrowserContext,
  loginUrl: string,
  credentials: Credentials
): Promise<void> {
  const page = await context.newPage();

  try {
    await page.goto(loginUrl);

    // Type credentials without logging
    await page.fill('#username', credentials.username);
    await page.fill('#password', credentials.password);

    // Click login
    await page.click('button[type="submit"]');

    // Wait for authentication
    await page.waitForURL('**/dashboard**', { timeout: 10000 });

    // Verify authentication succeeded
    const isLoggedIn = await page.evaluate(() => {
      return !!document.querySelector('.user-menu');
    });

    if (!isLoggedIn) {
      throw new Error('Authentication failed');
    }

    // Save session state for reuse
    await context.storageState({ path: 'auth-state.json' });

  } finally {
    // Clear sensitive fields
    await page.evaluate(() => {
      document.querySelectorAll('input[type="password"]').forEach(el => {
        (el as HTMLInputElement).value = '';
      });
    });

    await page.close();
  }
}

// Reuse authenticated session
async function withAuthenticatedContext(
  browser: Browser,
  fn: (context: BrowserContext) => Promise<void>
): Promise<void> {
  const context = await browser.newContext({
    storageState: 'auth-state.json',  // Reuse session
  });

  try {
    await fn(context);
  } finally {
    await context.close();
  }
}
```

### 3.5 WHEN implementing rate limiting

```typescript
import { Page } from 'playwright';

class RateLimitedScraper {
  private lastRequest = 0;
  private minDelay: number;
  private requestCount = 0;
  private maxRequests: number;

  constructor(minDelayMs: number = 1000, maxRequestsPerSession: number = 100) {
    this.minDelay = minDelayMs;
    this.maxRequests = maxRequestsPerSession;
  }

  async scrape<T>(page: Page, fn: () => Promise<T>): Promise<T> {
    // Check request limit
    if (this.requestCount >= this.maxRequests) {
      throw new Error('Request limit exceeded');
    }

    // Enforce minimum delay
    const now = Date.now();
    const elapsed = now - this.lastRequest;
    if (elapsed < this.minDelay) {
      await new Promise(r => setTimeout(r, this.minDelay - elapsed));
    }

    this.lastRequest = Date.now();
    this.requestCount++;

    // Add random jitter
    const jitter = Math.random() * 500;
    await new Promise(r => setTimeout(r, jitter));

    return await fn();
  }
}

// Usage
const scraper = new RateLimitedScraper(2000, 50);  // 2s delay, max 50 requests

const data = await scraper.scrape(page, async () => {
  await page.goto('https://example.com/data');
  return await page.evaluate(() => document.body.textContent);
});
```

### 3.6 WHEN handling errors and cleanup

```typescript
import { Browser, BrowserContext, Page } from 'playwright';

class BrowserSession {
  private browser: Browser;
  private context: BrowserContext;
  private pages: Set<Page> = new Set();

  constructor(browser: Browser, context: BrowserContext) {
    this.browser = browser;
    this.context = context;
  }

  async newPage(): Promise<Page> {
    const page = await this.context.newPage();
    this.pages.add(page);

    // Auto-cleanup on page close
    page.on('close', () => this.pages.delete(page));

    return page;
  }

  async cleanup(): Promise<void> {
    // Close all pages
    for (const page of this.pages) {
      try {
        await page.close();
      } catch {
        // Ignore errors during cleanup
      }
    }
    this.pages.clear();

    // Close context
    try {
      await this.context.close();
    } catch {
      // Ignore
    }

    // Close browser
    try {
      await this.browser.close();
    } catch {
      // Ignore
    }
  }
}

// Error handling wrapper
async function withRetry<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  delayMs: number = 1000
): Promise<T> {
  let lastError: Error | null = null;

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      // Don't retry on certain errors
      if (lastError.message.includes('net::ERR_NAME_NOT_RESOLVED')) {
        throw lastError;
      }

      if (i < maxRetries - 1) {
        await new Promise(r => setTimeout(r, delayMs * Math.pow(2, i)));
      }
    }
  }

  throw lastError;
}
```

---

## 4. Anti-Patterns

**NEVER:**
- Execute user-provided code via page.evaluate()
- Screenshot pages with visible credentials
- Navigate to non-whitelisted domains
- Leave browser sessions open on error
- Log credentials or sensitive data
- Scrape without rate limiting
- Trust data from page without validation

---

## 5. Testing

**ALWAYS write automation tests:**

```typescript
import { test, expect } from '@playwright/test';

test.describe('Scraper Security', () => {
  test('rejects invalid selectors', async ({ page }) => {
    const maliciousSelector = "'); alert(1); //";

    await expect(
      scrape(page, maliciousSelector)
    ).rejects.toThrow('Invalid selector');
  });

  test('blocks non-whitelisted domains', async ({ page }) => {
    await expect(
      navigateSafely(page, 'https://evil.com')
    ).rejects.toThrow('Domain not allowed');
  });

  test('validates extracted data', async ({ page }) => {
    await page.setContent('<h1></h1>');  // Empty title

    const result = await extractProduct(page);
    expect(result).toBeNull();  // Fails validation
  });

  test('enforces rate limiting', async ({ page }) => {
    const scraper = new RateLimitedScraper(100, 2);

    await scraper.scrape(page, async () => {});
    await scraper.scrape(page, async () => {});

    await expect(
      scraper.scrape(page, async () => {})
    ).rejects.toThrow('Request limit exceeded');
  });
});
```

---

## 6. Pre-Generation Checklist

**BEFORE generating any browser automation code:**

- [ ] No user input in page.evaluate() code strings
- [ ] URL validation and domain whitelisting
- [ ] Credentials from environment variables only
- [ ] No credentials visible in screenshots
- [ ] Rate limiting implemented
- [ ] Browser/context cleanup in finally blocks
- [ ] Data validation with Zod schemas
- [ ] Redirect validation after navigation
- [ ] Timeout on all operations
- [ ] Retry logic with exponential backoff

---

**Performance**: Quality over speed. Verify all code examples compile. Never skip security checks. See `template-references/performance-notes.md` for full guidelines.