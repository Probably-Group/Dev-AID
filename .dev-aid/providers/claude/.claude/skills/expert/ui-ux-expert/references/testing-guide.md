# UI/UX Testing Guide

> **Reference Document**: Comprehensive testing strategies for UI components, including unit tests, visual regression, accessibility audits, and performance testing for the UI/UX Expert skill.

---

## Table of Contents

1. [Unit Tests for UI Components](#unit-tests-for-ui-components)
2. [Visual Regression Tests](#visual-regression-tests)
3. [Accessibility Audit Tests](#accessibility-audit-tests)
4. [Performance Tests](#performance-tests)
5. [Manual Testing Checklist](#manual-testing-checklist)
6. [Testing Tools and Setup](#testing-tools-and-setup)

---

## Unit Tests for UI Components

Test accessibility, responsiveness, and interactions with Vitest/Jest:

### Modal Component Example

```typescript
// tests/components/Modal.test.ts
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import Modal from '@/components/ui/Modal.vue'

describe('Modal', () => {
  // Accessibility tests
  it('has correct ARIA attributes', () => {
    const wrapper = mount(Modal, {
      props: { isOpen: true, title: 'Test Modal' }
    })
    expect(wrapper.attributes('role')).toBe('dialog')
    expect(wrapper.attributes('aria-modal')).toBe('true')
    expect(wrapper.attributes('aria-labelledby')).toBeDefined()
  })

  it('traps focus within modal', async () => {
    const wrapper = mount(Modal, {
      props: { isOpen: true, title: 'Focus Trap' },
      attachTo: document.body
    })

    const focusableElements = wrapper.findAll('button, [tabindex="0"]')
    expect(focusableElements.length).toBeGreaterThan(0)
  })

  it('closes on Escape key', async () => {
    const wrapper = mount(Modal, {
      props: { isOpen: true, title: 'Escape Test' }
    })

    await wrapper.trigger('keydown.escape')
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('announces to screen readers when opened', () => {
    const wrapper = mount(Modal, {
      props: { isOpen: true, title: 'Announcement' }
    })

    const liveRegion = wrapper.find('[aria-live]')
    expect(liveRegion.exists()).toBe(true)
  })

  // Touch target tests
  it('close button meets touch target size', () => {
    const wrapper = mount(Modal, {
      props: { isOpen: true, title: 'Touch Target' }
    })

    const closeButton = wrapper.find('[aria-label="Close"]')
    expect(closeButton.classes()).toContain('touch-target')
  })
})
```

### Button Component Example

```typescript
// tests/components/Button.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Button from '@/components/ui/Button.vue'

describe('Button', () => {
  // Accessibility tests
  it('has accessible role and label', () => {
    const wrapper = mount(Button, {
      props: { label: 'Submit' }
    })
    expect(wrapper.attributes('role')).toBe('button')
    expect(wrapper.text()).toContain('Submit')
  })

  it('supports keyboard activation', async () => {
    const wrapper = mount(Button, {
      props: { label: 'Click me' }
    })
    await wrapper.trigger('keydown.enter')
    expect(wrapper.emitted('click')).toBeTruthy()
  })

  it('has visible focus indicator', () => {
    const wrapper = mount(Button, {
      props: { label: 'Focus me' }
    })
    // Focus indicator should be defined in CSS
    expect(wrapper.classes()).not.toContain('no-outline')
  })

  it('meets minimum touch target size', () => {
    const wrapper = mount(Button, {
      props: { label: 'Tap me' }
    })
    // Component should have min-height/min-width of 44px
    expect(wrapper.classes()).toContain('touch-target')
  })

  // Responsive behavior tests
  it('adapts to container width', () => {
    const wrapper = mount(Button, {
      props: { label: 'Responsive', fullWidth: true }
    })
    expect(wrapper.classes()).toContain('w-full')
  })

  // Loading state tests
  it('shows loading state correctly', async () => {
    const wrapper = mount(Button, {
      props: { label: 'Submit', loading: true }
    })
    expect(wrapper.find('[aria-busy="true"]').exists()).toBe(true)
    expect(wrapper.attributes('disabled')).toBeDefined()
  })

  // Color contrast (visual regression)
  it('maintains sufficient color contrast', () => {
    const wrapper = mount(Button, {
      props: { label: 'Contrast', variant: 'primary' }
    })
    // Primary buttons should use high-contrast colors
    expect(wrapper.classes()).toContain('bg-primary')
  })
})
```

### Form Component Example

```typescript
// tests/components/FormInput.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import FormInput from '@/components/ui/FormInput.vue'

describe('FormInput', () => {
  it('associates label with input', () => {
    const wrapper = mount(FormInput, {
      props: { id: 'email', label: 'Email Address' }
    })

    const label = wrapper.find('label')
    const input = wrapper.find('input')

    expect(label.attributes('for')).toBe('email')
    expect(input.attributes('id')).toBe('email')
  })

  it('shows error state correctly', async () => {
    const wrapper = mount(FormInput, {
      props: {
        id: 'email',
        label: 'Email',
        error: 'Email is required'
      }
    })

    const input = wrapper.find('input')
    expect(input.attributes('aria-invalid')).toBe('true')
    expect(input.attributes('aria-describedby')).toBeDefined()

    const errorMessage = wrapper.find('[role="alert"]')
    expect(errorMessage.exists()).toBe(true)
    expect(errorMessage.text()).toContain('Email is required')
  })

  it('marks required fields correctly', () => {
    const wrapper = mount(FormInput, {
      props: {
        id: 'email',
        label: 'Email',
        required: true
      }
    })

    const input = wrapper.find('input')
    expect(input.attributes('required')).toBeDefined()
    expect(input.attributes('aria-required')).toBe('true')
  })
})
```

---

## Visual Regression Tests

Use Playwright or similar tools for visual regression testing:

### Button States Test

```typescript
// tests/visual/button.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Button Visual Tests', () => {
  test('button states render correctly', async ({ page }) => {
    await page.goto('/storybook/button')

    // Default state
    await expect(page.locator('.btn-primary')).toHaveScreenshot('button-default.png')

    // Hover state
    await page.locator('.btn-primary').hover()
    await expect(page.locator('.btn-primary')).toHaveScreenshot('button-hover.png')

    // Focus state
    await page.locator('.btn-primary').focus()
    await expect(page.locator('.btn-primary')).toHaveScreenshot('button-focus.png')

    // Disabled state
    await expect(page.locator('.btn-primary[disabled]')).toHaveScreenshot('button-disabled.png')
  })

  test('button has sufficient contrast', async ({ page }) => {
    await page.goto('/storybook/button')

    // Check color contrast using axe
    const results = await new AxeBuilder({ page }).analyze()
    expect(results.violations).toHaveLength(0)
  })

  test('button maintains design across viewports', async ({ page }) => {
    await page.goto('/storybook/button')

    // Desktop
    await page.setViewportSize({ width: 1920, height: 1080 })
    await expect(page.locator('.btn-primary')).toHaveScreenshot('button-desktop.png')

    // Tablet
    await page.setViewportSize({ width: 768, height: 1024 })
    await expect(page.locator('.btn-primary')).toHaveScreenshot('button-tablet.png')

    // Mobile
    await page.setViewportSize({ width: 375, height: 667 })
    await expect(page.locator('.btn-primary')).toHaveScreenshot('button-mobile.png')
  })
})
```

### Form Validation Visual Tests

```typescript
// tests/visual/form.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Form Visual Tests', () => {
  test('form validation states', async ({ page }) => {
    await page.goto('/forms/contact')

    // Default state
    await expect(page.locator('form')).toHaveScreenshot('form-default.png')

    // Error state
    await page.locator('button[type="submit"]').click()
    await expect(page.locator('form')).toHaveScreenshot('form-errors.png')

    // Success state
    await page.fill('#name', 'John Doe')
    await page.fill('#email', 'john@example.com')
    await page.locator('button[type="submit"]').click()
    await expect(page.locator('.success-message')).toHaveScreenshot('form-success.png')
  })
})
```

---

## Accessibility Audit Tests

Use axe-core for automated accessibility testing:

### Page-Level Accessibility Tests

```typescript
// tests/a11y/pages.spec.ts
import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

test.describe('Accessibility Audits', () => {
  test('home page passes accessibility audit', async ({ page }) => {
    await page.goto('/')

    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag22aa'])
      .analyze()

    expect(results.violations).toHaveLength(0)
  })

  test('form page has accessible inputs', async ({ page }) => {
    await page.goto('/contact')

    const results = await new AxeBuilder({ page })
      .include('form')
      .analyze()

    expect(results.violations).toHaveLength(0)
  })

  test('navigation is keyboard accessible', async ({ page }) => {
    await page.goto('/')

    // Tab through navigation
    await page.keyboard.press('Tab')
    const firstNavItem = page.locator('nav a:first-child')
    await expect(firstNavItem).toBeFocused()

    // Can activate with Enter
    await page.keyboard.press('Enter')
    await expect(page).toHaveURL(/.*about/)
  })

  test('modal traps focus correctly', async ({ page }) => {
    await page.goto('/demo/modal')

    // Open modal
    await page.click('button[aria-label="Open modal"]')

    // Modal should be focused
    const modal = page.locator('[role="dialog"]')
    await expect(modal).toBeFocused()

    // Tab should stay within modal
    await page.keyboard.press('Tab')
    await page.keyboard.press('Tab')
    const focusedElement = page.locator(':focus')
    await expect(modal.locator('button')).toContainElement(focusedElement)

    // Escape should close modal
    await page.keyboard.press('Escape')
    await expect(modal).not.toBeVisible()
  })

  test('skip links are present and functional', async ({ page }) => {
    await page.goto('/')

    // Tab to skip link
    await page.keyboard.press('Tab')
    const skipLink = page.locator('a[href="#main-content"]')
    await expect(skipLink).toBeFocused()

    // Activate skip link
    await page.keyboard.press('Enter')
    const mainContent = page.locator('#main-content')
    await expect(mainContent).toBeFocused()
  })
})
```

### Component-Specific Accessibility Tests

```typescript
// tests/a11y/components.spec.ts
import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

test.describe('Component Accessibility', () => {
  test('dropdown menu is accessible', async ({ page }) => {
    await page.goto('/components/dropdown')

    // Verify ARIA attributes
    const button = page.locator('[aria-haspopup="true"]')
    await expect(button).toHaveAttribute('aria-expanded', 'false')

    // Open dropdown with keyboard
    await button.focus()
    await page.keyboard.press('Enter')
    await expect(button).toHaveAttribute('aria-expanded', 'true')

    // Navigate with arrow keys
    await page.keyboard.press('ArrowDown')
    const firstItem = page.locator('[role="menuitem"]').first()
    await expect(firstItem).toBeFocused()

    // Run accessibility audit
    const results = await new AxeBuilder({ page }).analyze()
    expect(results.violations).toHaveLength(0)
  })

  test('tabs component is accessible', async ({ page }) => {
    await page.goto('/components/tabs')

    const tablist = page.locator('[role="tablist"]')
    const tabs = tablist.locator('[role="tab"]')

    // First tab should be selected by default
    await expect(tabs.first()).toHaveAttribute('aria-selected', 'true')

    // Arrow keys navigate between tabs
    await tabs.first().focus()
    await page.keyboard.press('ArrowRight')
    await expect(tabs.nth(1)).toBeFocused()
    await expect(tabs.nth(1)).toHaveAttribute('aria-selected', 'true')

    // Associated panel should be visible
    const panel = page.locator('[role="tabpanel"][aria-labelledby]')
    await expect(panel).toBeVisible()
  })
})
```

---

## Performance Tests

Test Core Web Vitals and performance metrics:

### Core Web Vitals Tests

```typescript
// tests/performance/core-web-vitals.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Core Web Vitals', () => {
  test('LCP is under 2.5 seconds', async ({ page }) => {
    await page.goto('/')

    const lcp = await page.evaluate(() => {
      return new Promise((resolve) => {
        new PerformanceObserver((list) => {
          const entries = list.getEntries()
          resolve(entries[entries.length - 1].startTime)
        }).observe({ entryTypes: ['largest-contentful-paint'] })
      })
    })

    expect(lcp).toBeLessThan(2500)
  })

  test('FID is under 100 milliseconds', async ({ page }) => {
    await page.goto('/')

    const fid = await page.evaluate(() => {
      return new Promise((resolve) => {
        new PerformanceObserver((list) => {
          const firstInput = list.getEntries()[0]
          resolve(firstInput.processingStart - firstInput.startTime)
        }).observe({ entryTypes: ['first-input'] })

        // Trigger an interaction
        document.body.click()
      })
    })

    expect(fid).toBeLessThan(100)
  })

  test('CLS is under 0.1', async ({ page }) => {
    await page.goto('/')

    const cls = await page.evaluate(() => {
      return new Promise((resolve) => {
        let clsValue = 0
        new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (!entry.hadRecentInput) {
              clsValue += entry.value
            }
          }
          resolve(clsValue)
        }).observe({ entryTypes: ['layout-shift'] })

        setTimeout(() => resolve(clsValue), 5000)
      })
    })

    expect(cls).toBeLessThan(0.1)
  })
})
```

### Image Loading Performance

```typescript
// tests/performance/images.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Image Performance', () => {
  test('images use lazy loading', async ({ page }) => {
    await page.goto('/gallery')

    const images = page.locator('img')
    const count = await images.count()

    for (let i = 0; i < count; i++) {
      const img = images.nth(i)
      const loading = await img.getAttribute('loading')

      // Below-fold images should be lazy loaded
      if (i > 2) {
        expect(loading).toBe('lazy')
      }
    }
  })

  test('images specify dimensions', async ({ page }) => {
    await page.goto('/')

    const images = page.locator('img')
    const count = await images.count()

    for (let i = 0; i < count; i++) {
      const img = images.nth(i)
      const width = await img.getAttribute('width')
      const height = await img.getAttribute('height')

      // Images should have explicit dimensions
      expect(width).not.toBeNull()
      expect(height).not.toBeNull()
    }
  })

  test('responsive images use srcset', async ({ page }) => {
    await page.goto('/')

    const images = page.locator('img[srcset]')
    const count = await images.count()

    expect(count).toBeGreaterThan(0)

    for (let i = 0; i < count; i++) {
      const img = images.nth(i)
      const srcset = await img.getAttribute('srcset')

      // srcset should contain multiple sources
      expect(srcset).toContain('w,')
    }
  })
})
```

---

## Manual Testing Checklist

### Accessibility Testing

**Keyboard Navigation**:
- [ ] All interactive elements reachable with Tab key
- [ ] Tab order follows visual order
- [ ] Focus indicators clearly visible (3px minimum outline)
- [ ] Escape closes modals/dropdowns
- [ ] Enter/Space activates buttons
- [ ] Arrow keys navigate menus and tabs
- [ ] No keyboard traps

**Screen Reader Testing** (NVDA, JAWS, VoiceOver):
- [ ] Page structure makes sense (headings, landmarks)
- [ ] All images have alt text
- [ ] Form inputs have associated labels
- [ ] Error messages are announced
- [ ] Loading states are announced
- [ ] Button purposes are clear
- [ ] Dynamic content updates are announced

**Color and Contrast**:
- [ ] Text contrast meets 4.5:1 (normal text)
- [ ] UI component contrast meets 3:1
- [ ] Information not conveyed by color alone
- [ ] Tested with color blindness simulators

**Touch Targets**:
- [ ] All targets at least 44x44px
- [ ] Adequate spacing between targets (8px minimum)
- [ ] Tested on actual mobile devices

### Visual Design Testing

**Typography**:
- [ ] Font sizes readable at all viewport sizes
- [ ] Line height adequate (1.5 for body text)
- [ ] Line length not too long (50-75 characters)
- [ ] Heading hierarchy is clear

**Spacing**:
- [ ] Consistent spacing throughout
- [ ] Adequate white space around elements
- [ ] Related items grouped together

**Responsive Design**:
- [ ] Tested on mobile (375px)
- [ ] Tested on tablet (768px)
- [ ] Tested on desktop (1920px)
- [ ] No horizontal scrolling on mobile
- [ ] Touch-friendly on mobile devices

### Interaction Testing

**Forms**:
- [ ] Inline validation works
- [ ] Error messages are clear and helpful
- [ ] Success states are shown
- [ ] Can submit with Enter key
- [ ] Required fields are marked

**Loading States**:
- [ ] Buttons show loading state
- [ ] Skeleton screens for content
- [ ] Progress bars for long operations
- [ ] Users cannot double-submit

**Error Handling**:
- [ ] Error messages are specific and helpful
- [ ] Users can recover from errors
- [ ] Network errors are handled gracefully

---

## Testing Tools and Setup

### Recommended Tools

**Unit Testing**:
- Vitest or Jest
- @vue/test-utils or @testing-library/react
- @testing-library/user-event

**Accessibility Testing**:
- @axe-core/playwright or @axe-core/react
- pa11y
- WAVE browser extension
- Lighthouse CI

**Visual Regression**:
- Playwright
- Percy
- Chromatic

**Screen Readers**:
- NVDA (Windows, free)
- JAWS (Windows, paid)
- VoiceOver (macOS/iOS, built-in)

### Test Setup Example

```bash
# Install testing dependencies
npm install -D vitest @vue/test-utils happy-dom
npm install -D @playwright/test @axe-core/playwright
npm install -D @testing-library/user-event

# package.json scripts
{
  "scripts": {
    "test:unit": "vitest",
    "test:a11y": "playwright test tests/a11y",
    "test:visual": "playwright test tests/visual",
    "test:perf": "playwright test tests/performance",
    "test:all": "npm run test:unit && npm run test:a11y && npm run test:visual"
  }
}
```

---

## Summary

Comprehensive UI/UX testing includes:

1. **Unit Tests**: Test components in isolation for accessibility, interactions, and responsive behavior
2. **Visual Regression**: Catch unintended visual changes across components and states
3. **Accessibility Audits**: Ensure WCAG 2.2 compliance with automated and manual testing
4. **Performance Tests**: Verify Core Web Vitals (LCP, FID, CLS) meet targets
5. **Manual Testing**: Test with keyboard, screen readers, and real devices

**Testing Strategy**:
- Write tests before or alongside implementation (TDD)
- Run automated tests in CI/CD pipeline
- Conduct manual accessibility testing regularly
- Test on real devices, not just emulators
- Include users with disabilities in testing when possible

Quality UI/UX requires continuous testing and validation. Make testing a core part of your development workflow.
