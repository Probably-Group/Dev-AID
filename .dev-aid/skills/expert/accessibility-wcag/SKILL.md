---
name: accessibility-wcag
version: 2.0.0
description: "WCAG 2.2 compliance patterns for accessible web applications with ARIA, keyboard navigation, and screen reader support."
risk_level: HIGH
---

# Accessibility WCAG - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE providing guidance:**
1. Verify claims against authoritative sources
2. Distinguish between established practices and opinions
3. Never invent statistics, studies, or references
4. If unsure, state uncertainty explicitly

### 0.2 Risk Level: HIGH

**Verification requirements:**
- Cross-reference recommendations with industry standards
- Cite sources when making specific claims
- Acknowledge when best practices vary by context

---

## 1. Security Principles

### 1.1 Focus Management Security (CWE-1021)

**Principle:** Never trap focus or allow focus to escape modals to sensitive controls.

```html
<!-- ❌ WRONG - Focus trap allows escape -->
<div class="modal">
  <button>Close</button>
  <!-- Tab can escape to page behind -->
</div>

<!-- ✅ CORRECT - Proper focus trap -->
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="modal-title"
>
  <!-- Focus trapped within modal -->
</div>
```

### 1.2 XSS in ARIA Labels (CWE-79)

**Principle:** Sanitize all dynamic ARIA content. Never use innerHTML for labels.

```javascript
// ❌ WRONG - XSS via aria-label
element.setAttribute('aria-label', userInput);

// ✅ CORRECT - Sanitized
element.setAttribute('aria-label', sanitizeText(userInput));
```

### 1.3 Visible Security Indicators

**Principle:** Security states must be perceivable by all users (visual, auditory, programmatic).

### 1.4 Error Messages Accessible

**Principle:** Error messages must be announced to screen readers and visible.

### 1.5 Timeout Warnings

**Principle:** Users must be warned before session timeout with accessible notifications.

### 1.6 CAPTCHA Alternatives

**Principle:** Provide accessible CAPTCHA alternatives (audio, logic puzzles).

---

## 2. Version Requirements

**ALWAYS use these minimum versions:**

```json
{
  "devDependencies": {
    "@axe-core/playwright": "^4.8.0",
    "axe-core": "^4.8.0",
    "pa11y": "^6.2.0",
    "jest-axe": "^8.0.0"
  }
}
```

**WCAG Version:** 2.2 Level AA (minimum)

---

## 3. Code Patterns

### 3.1 WHEN implementing keyboard navigation

```typescript
// ❌ WRONG - Click only, no keyboard support
<div onClick={handleAction}>Action</div>

// ❌ WRONG - Incorrect tab handling
<div tabIndex={5}>Item</div>

// ✅ CORRECT - Full keyboard support
interface FocusableItemProps {
  onActivate: () => void;
  children: React.ReactNode;
}

function FocusableItem({ onActivate, children }: FocusableItemProps) {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Enter and Space activate
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onActivate();
    }
  };

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onActivate}
      onKeyDown={handleKeyDown}
      style={{ cursor: 'pointer' }}
    >
      {children}
    </div>
  );
}

// Arrow key navigation for lists
function NavigableList({ items }: { items: Item[] }) {
  const [focusIndex, setFocusIndex] = useState(0);
  const itemRefs = useRef<(HTMLElement | null)[]>([]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setFocusIndex(prev => Math.min(prev + 1, items.length - 1));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setFocusIndex(prev => Math.max(prev - 1, 0));
        break;
      case 'Home':
        e.preventDefault();
        setFocusIndex(0);
        break;
      case 'End':
        e.preventDefault();
        setFocusIndex(items.length - 1);
        break;
    }
  };

  useEffect(() => {
    itemRefs.current[focusIndex]?.focus();
  }, [focusIndex]);

  return (
    <ul role="listbox" onKeyDown={handleKeyDown}>
      {items.map((item, index) => (
        <li
          key={item.id}
          ref={el => (itemRefs.current[index] = el)}
          role="option"
          tabIndex={index === focusIndex ? 0 : -1}
          aria-selected={index === focusIndex}
        >
          {item.label}
        </li>
      ))}
    </ul>
  );
}
```

### 3.2 WHEN implementing focus management

```typescript
// Focus trap for modals
function useFocusTrap(isOpen: boolean) {
  const containerRef = useRef<HTMLElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (!isOpen || !containerRef.current) return;

    // Store previous focus
    previousFocusRef.current = document.activeElement as HTMLElement;

    // Get focusable elements
    const focusableSelector = [
      'button:not([disabled])',
      'input:not([disabled])',
      'select:not([disabled])',
      'textarea:not([disabled])',
      'a[href]',
      '[tabindex]:not([tabindex="-1"])',
    ].join(',');

    const focusableElements = containerRef.current.querySelectorAll(
      focusableSelector
    ) as NodeListOf<HTMLElement>;

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    // Focus first element
    firstElement?.focus();

    // Trap focus
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement?.focus();
        }
      } else {
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement?.focus();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      // Restore focus when closing
      previousFocusRef.current?.focus();
    };
  }, [isOpen]);

  return containerRef;
}

// Modal component with focus trap
function AccessibleModal({
  isOpen,
  onClose,
  title,
  children,
}: ModalProps) {
  const modalRef = useFocusTrap(isOpen);

  if (!isOpen) return null;

  return (
    <div
      className="modal-overlay"
      onClick={onClose}
      role="presentation"
    >
      <div
        ref={modalRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        onClick={e => e.stopPropagation()}
      >
        <h2 id="modal-title">{title}</h2>
        {children}
        <button onClick={onClose}>Close</button>
      </div>
    </div>
  );
}
```

### 3.3 WHEN implementing form validation

```typescript
// ❌ WRONG - Errors not announced, no association
<input type="email" />
{error && <span style={{ color: 'red' }}>{error}</span>}

// ✅ CORRECT - Accessible form validation
interface FormFieldProps {
  id: string;
  label: string;
  type?: string;
  required?: boolean;
  error?: string;
  description?: string;
}

function FormField({
  id,
  label,
  type = 'text',
  required = false,
  error,
  description,
}: FormFieldProps) {
  const errorId = `${id}-error`;
  const descriptionId = `${id}-description`;

  // Build aria-describedby
  const describedBy = [
    description && descriptionId,
    error && errorId,
  ].filter(Boolean).join(' ') || undefined;

  return (
    <div className="form-field">
      <label htmlFor={id}>
        {label}
        {required && <span aria-hidden="true"> *</span>}
        {required && <span className="sr-only"> (required)</span>}
      </label>

      {description && (
        <p id={descriptionId} className="field-description">
          {description}
        </p>
      )}

      <input
        id={id}
        type={type}
        required={required}
        aria-invalid={!!error}
        aria-describedby={describedBy}
      />

      {error && (
        <p
          id={errorId}
          role="alert"
          className="field-error"
        >
          {error}
        </p>
      )}
    </div>
  );
}

// Form with live validation feedback
function AccessibleForm() {
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [announcements, setAnnouncements] = useState('');

  const validate = (name: string, value: string) => {
    // Validation logic
    if (name === 'email' && !value.includes('@')) {
      return 'Please enter a valid email address';
    }
    return '';
  };

  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    const error = validate(e.target.name, e.target.value);
    setErrors(prev => ({ ...prev, [e.target.name]: error }));

    // Announce error to screen reader
    if (error) {
      setAnnouncements(error);
    }
  };

  return (
    <form>
      {/* Live region for announcements */}
      <div
        role="status"
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
      >
        {announcements}
      </div>

      <FormField
        id="email"
        label="Email"
        type="email"
        required
        error={errors.email}
        description="We'll never share your email"
      />

      <button type="submit">Submit</button>
    </form>
  );
}
```

### 3.4 WHEN implementing live regions

```typescript
// ❌ WRONG - No announcement of dynamic content
<div>{statusMessage}</div>

// ✅ CORRECT - Live regions for dynamic announcements
function LiveAnnouncer() {
  const [politeMessage, setPoliteMessage] = useState('');
  const [assertiveMessage, setAssertiveMessage] = useState('');

  // Polite: waits for user to stop interacting
  const announcePolite = (message: string) => {
    setPoliteMessage('');
    // Clear and set to trigger re-announcement
    setTimeout(() => setPoliteMessage(message), 100);
  };

  // Assertive: interrupts immediately
  const announceAssertive = (message: string) => {
    setAssertiveMessage('');
    setTimeout(() => setAssertiveMessage(message), 100);
  };

  return (
    <>
      {/* Polite announcements */}
      <div
        role="status"
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
      >
        {politeMessage}
      </div>

      {/* Assertive announcements */}
      <div
        role="alert"
        aria-live="assertive"
        aria-atomic="true"
        className="sr-only"
      >
        {assertiveMessage}
      </div>
    </>
  );
}

// Toast notification with live region
function Toast({ message, type }: { message: string; type: 'success' | 'error' }) {
  return (
    <div
      role={type === 'error' ? 'alert' : 'status'}
      aria-live={type === 'error' ? 'assertive' : 'polite'}
      className={`toast toast-${type}`}
    >
      <span className="sr-only">
        {type === 'error' ? 'Error: ' : 'Success: '}
      </span>
      {message}
    </div>
  );
}
```

### 3.5 WHEN implementing skip links and landmarks

```html
<!-- Skip links at page start -->
<body>
  <a href="#main-content" class="skip-link">
    Skip to main content
  </a>
  <a href="#main-nav" class="skip-link">
    Skip to navigation
  </a>

  <header role="banner">
    <nav id="main-nav" role="navigation" aria-label="Main">
      <!-- Navigation content -->
    </nav>
  </header>

  <main id="main-content" role="main" tabindex="-1">
    <!-- Main content -->
  </main>

  <aside role="complementary" aria-label="Related content">
    <!-- Sidebar -->
  </aside>

  <footer role="contentinfo">
    <!-- Footer content -->
  </footer>
</body>

<style>
/* Skip link styles */
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  padding: 8px 16px;
  background: #000;
  color: #fff;
  z-index: 1000;
  text-decoration: none;
}

.skip-link:focus {
  top: 0;
}

/* Screen reader only class */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
```

### 3.6 WHEN implementing accessible images and media

```html
<!-- ❌ WRONG - Missing alt text -->
<img src="chart.png" />

<!-- ❌ WRONG - Redundant alt text -->
<img src="logo.png" alt="Image of logo" />

<!-- ✅ CORRECT - Informative image -->
<img
  src="chart.png"
  alt="Sales increased 25% from Q1 to Q2 2024"
/>

<!-- ✅ CORRECT - Decorative image -->
<img src="decoration.png" alt="" role="presentation" />

<!-- ✅ CORRECT - Complex image with long description -->
<figure>
  <img
    src="complex-diagram.png"
    alt="System architecture diagram"
    aria-describedby="diagram-description"
  />
  <figcaption id="diagram-description">
    The diagram shows three main components: a web server
    connected to an API gateway, which routes requests to
    microservices A, B, and C...
  </figcaption>
</figure>

<!-- ✅ CORRECT - Video with captions -->
<video controls>
  <source src="video.mp4" type="video/mp4" />
  <track
    kind="captions"
    src="captions.vtt"
    srclang="en"
    label="English captions"
    default
  />
  <track
    kind="descriptions"
    src="descriptions.vtt"
    srclang="en"
    label="Audio descriptions"
  />
</video>
```

### 3.7 WHEN implementing color and contrast

```css
/* ❌ WRONG - Color only indicator */
.error {
  color: red;
}

/* ❌ WRONG - Insufficient contrast */
.text {
  color: #999;
  background: #fff;
}

/* ✅ CORRECT - Multiple indicators + sufficient contrast */
.error {
  color: #b91c1c; /* 4.5:1 contrast ratio */
  border-left: 4px solid #b91c1c;
  background: #fef2f2;
}

.error::before {
  content: "⚠ Error: ";
}

/* ✅ CORRECT - Focus indicators */
:focus-visible {
  outline: 2px solid #2563eb;
  outline-offset: 2px;
}

/* ✅ CORRECT - High contrast mode support */
@media (prefers-contrast: more) {
  .button {
    border: 2px solid currentColor;
  }
}

/* ✅ CORRECT - Reduced motion */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### 3.8 WHEN implementing accessible tables

```html
<!-- ❌ WRONG - No structure -->
<table>
  <tr><td>Name</td><td>Age</td></tr>
  <tr><td>John</td><td>30</td></tr>
</table>

<!-- ✅ CORRECT - Properly structured table -->
<table aria-label="User information">
  <caption>
    List of registered users
    <span class="sr-only">Sorted by name ascending</span>
  </caption>

  <thead>
    <tr>
      <th scope="col" aria-sort="ascending">
        Name
        <button aria-label="Sort by name descending">
          ▲
        </button>
      </th>
      <th scope="col">Age</th>
      <th scope="col">Actions</th>
    </tr>
  </thead>

  <tbody>
    <tr>
      <th scope="row">John Doe</th>
      <td>30</td>
      <td>
        <button aria-label="Edit John Doe">Edit</button>
        <button aria-label="Delete John Doe">Delete</button>
      </td>
    </tr>
  </tbody>
</table>

<!-- Complex table with row and column headers -->
<table aria-label="Quarterly sales by region">
  <thead>
    <tr>
      <td></td>
      <th scope="col">Q1</th>
      <th scope="col">Q2</th>
      <th scope="col">Q3</th>
      <th scope="col">Q4</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">North</th>
      <td>$100k</td>
      <td>$120k</td>
      <td>$110k</td>
      <td>$150k</td>
    </tr>
    <tr>
      <th scope="row">South</th>
      <td>$80k</td>
      <td>$90k</td>
      <td>$85k</td>
      <td>$95k</td>
    </tr>
  </tbody>
</table>
```

---

## 4. Anti-Patterns

**NEVER:**
- Use color alone to convey information
- Remove focus outlines without replacement
- Use `tabindex` > 0 (disrupts natural order)
- Use `aria-hidden="true"` on focusable elements
- Create keyboard traps (except modals)
- Use placeholder as label replacement
- Auto-play media without controls
- Use CAPTCHA without accessible alternative

---

## 5. Testing

**ALWAYS write accessibility tests:**

```typescript
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Accessibility', () => {
  test('homepage has no WCAG violations', async ({ page }) => {
    await page.goto('/');

    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag22aa'])
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test('form is keyboard navigable', async ({ page }) => {
    await page.goto('/contact');

    // Tab through form
    await page.keyboard.press('Tab');
    await expect(page.locator('input[name="name"]')).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(page.locator('input[name="email"]')).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(page.locator('textarea')).toBeFocused();

    await page.keyboard.press('Tab');
    await expect(page.locator('button[type="submit"]')).toBeFocused();
  });

  test('modal traps focus', async ({ page }) => {
    await page.goto('/');
    await page.click('button[aria-haspopup="dialog"]');

    // Focus should be inside modal
    const modal = page.locator('[role="dialog"]');
    await expect(modal).toBeVisible();

    // Tab should cycle within modal
    const firstFocusable = modal.locator('button').first();
    const lastFocusable = modal.locator('button').last();

    await lastFocusable.focus();
    await page.keyboard.press('Tab');
    await expect(firstFocusable).toBeFocused();
  });

  test('images have alt text', async ({ page }) => {
    await page.goto('/');

    const images = await page.locator('img').all();
    for (const img of images) {
      const alt = await img.getAttribute('alt');
      const role = await img.getAttribute('role');

      // Must have alt (can be empty for decorative)
      expect(alt !== null || role === 'presentation').toBeTruthy();
    }
  });

  test('screen reader announcements work', async ({ page }) => {
    await page.goto('/form');

    // Submit invalid form
    await page.click('button[type="submit"]');

    // Check live region announces error
    const liveRegion = page.locator('[role="alert"]');
    await expect(liveRegion).toContainText('error');
  });
});
```

---

## 6. Pre-Generation Checklist

**BEFORE generating any UI code:**

- [ ] All interactive elements keyboard accessible
- [ ] Focus order is logical (no positive tabindex)
- [ ] Focus visible on all interactive elements
- [ ] Form inputs have associated labels
- [ ] Error messages use role="alert" or aria-live
- [ ] Images have appropriate alt text
- [ ] Color contrast meets WCAG AA (4.5:1 text, 3:1 UI)
- [ ] Skip links provided
- [ ] Landmarks properly used (main, nav, etc.)
- [ ] Reduced motion preference respected
