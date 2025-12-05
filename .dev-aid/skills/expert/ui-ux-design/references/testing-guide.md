# UI/UX Testing Guide

## Overview

This guide provides comprehensive testing strategies for UI/UX implementations, following Test-Driven Development (TDD) principles.

---

## Pre-Implementation Checklist

### Phase 1: Before Writing Code

**Requirements Gathering**:
- [ ] Component requirements documented
- [ ] User stories defined with acceptance criteria
- [ ] Design mockups or wireframes reviewed
- [ ] Interaction patterns identified
- [ ] Edge cases documented

**Test Planning**:
- [ ] Write failing tests for component behavior
- [ ] Write accessibility tests (ARIA, focus, contrast)
- [ ] Write responsive layout tests
- [ ] Write interaction tests (clicks, keyboard, etc.)
- [ ] Define performance budget for component

**Design Tokens**:
- [ ] Design tokens identified from system
- [ ] Color palette verified for contrast
- [ ] Typography scale selected
- [ ] Spacing values defined (following 8px grid)
- [ ] Animation timing defined

---

### Phase 2: During Implementation

**TDD Workflow**:
- [ ] Tests passing incrementally
- [ ] Write test → See it fail → Implement → See it pass
- [ ] Refactor after each passing test
- [ ] No implementation without test coverage

**Design System Compliance**:
- [ ] Color system applied consistently
- [ ] Typography scale used correctly
- [ ] Spacing follows 8px grid
- [ ] Visual hierarchy guides attention
- [ ] Design patterns followed

**State Management**:
- [ ] Loading states include skeletons
- [ ] Error states display helpful messages
- [ ] Empty states provide clear guidance
- [ ] Success states provide feedback

**Performance**:
- [ ] Images optimized (WebP/AVIF, lazy loading)
- [ ] Components lazy loaded when appropriate
- [ ] Animations use CSS transforms
- [ ] No layout thrashing
- [ ] Virtual scrolling for long lists (if needed)

---

### Phase 3: Before Committing

**Component Tests**:
- [ ] All component tests pass
- [ ] Integration tests pass
- [ ] Visual regression tests pass
- [ ] Snapshot tests updated (if applicable)

**Accessibility Audit**:
- [ ] Accessibility audit passes (WCAG AA minimum)
- [ ] Focus states visible on all interactive elements
- [ ] Touch targets ≥44px on mobile
- [ ] Reduced motion supported
- [ ] Color contrast meets 4.5:1 ratio
- [ ] Screen reader tested (NVDA/JAWS/VoiceOver)
- [ ] Keyboard navigation works completely

**Responsive Testing**:
- [ ] Mobile layout tested (320px - 767px)
- [ ] Tablet layout tested (768px - 1023px)
- [ ] Desktop layout tested (1024px+)
- [ ] Touch interactions work on mobile
- [ ] Mouse interactions work on desktop

**Performance**:
- [ ] Animations run at 60fps
- [ ] No layout thrashing
- [ ] Critical CSS inlined
- [ ] Lighthouse score > 90
- [ ] Core Web Vitals meet targets
- [ ] Tested on slow 3G connection

**Code Quality**:
- [ ] Build completes without errors
- [ ] No console errors or warnings
- [ ] TypeScript types properly defined
- [ ] Code follows style guide
- [ ] Comments added for complex logic

---

## Component Testing Patterns

### Pattern 1: Basic Component Test

```typescript
// tests/components/Button.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Button from '@/components/ui/Button.vue'

describe('Button', () => {
  it('renders default button', () => {
    const wrapper = mount(Button, {
      props: { label: 'Click me' }
    })
    expect(wrapper.text()).toContain('Click me')
    expect(wrapper.classes()).toContain('button')
  })

  it('emits click event when clicked', async () => {
    const wrapper = mount(Button)
    await wrapper.trigger('click')
    expect(wrapper.emitted('click')).toBeTruthy()
  })

  it('is disabled when disabled prop is true', () => {
    const wrapper = mount(Button, {
      props: { disabled: true }
    })
    expect(wrapper.attributes('disabled')).toBeDefined()
    expect(wrapper.classes()).toContain('button--disabled')
  })

  it('applies variant class correctly', () => {
    const wrapper = mount(Button, {
      props: { variant: 'primary' }
    })
    expect(wrapper.classes()).toContain('button--primary')
  })
})
```

---

### Pattern 2: Accessibility Test

```typescript
// tests/components/Modal.a11y.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Modal from '@/components/ui/Modal.vue'

describe('Modal Accessibility', () => {
  it('has correct ARIA attributes', () => {
    const wrapper = mount(Modal, {
      props: {
        isOpen: true,
        title: 'Confirm Action'
      }
    })

    expect(wrapper.attributes('role')).toBe('dialog')
    expect(wrapper.attributes('aria-modal')).toBe('true')
    expect(wrapper.attributes('aria-labelledby')).toBeDefined()
  })

  it('traps focus within modal when open', async () => {
    const wrapper = mount(Modal, {
      props: { isOpen: true },
      attachTo: document.body
    })

    // Focus should be trapped in modal
    const firstFocusable = wrapper.find('[data-focus-first]')
    const lastFocusable = wrapper.find('[data-focus-last]')

    lastFocusable.element.focus()
    // Simulate Tab key
    await lastFocusable.trigger('keydown.tab')

    expect(document.activeElement).toBe(firstFocusable.element)
  })

  it('closes on Escape key', async () => {
    const wrapper = mount(Modal, {
      props: { isOpen: true }
    })

    await wrapper.trigger('keydown.esc')
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('has sufficient color contrast', () => {
    const wrapper = mount(Modal)
    const styles = window.getComputedStyle(wrapper.element)
    const color = styles.color
    const backgroundColor = styles.backgroundColor

    // Check contrast ratio (simplified)
    // In real tests, use a proper contrast checker
    expect(color).toBeDefined()
    expect(backgroundColor).toBeDefined()
  })
})
```

---

### Pattern 3: Responsive Test

```typescript
// tests/components/Navigation.responsive.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import Navigation from '@/components/Navigation.vue'

describe('Navigation Responsive Behavior', () => {
  beforeEach(() => {
    // Reset viewport
    window.innerWidth = 1024
    window.dispatchEvent(new Event('resize'))
  })

  it('shows desktop menu on large screens', () => {
    window.innerWidth = 1024
    const wrapper = mount(Navigation)

    expect(wrapper.find('.desktop-menu').isVisible()).toBe(true)
    expect(wrapper.find('.mobile-menu-toggle').exists()).toBe(false)
  })

  it('shows mobile menu toggle on small screens', () => {
    window.innerWidth = 375
    window.dispatchEvent(new Event('resize'))

    const wrapper = mount(Navigation)

    expect(wrapper.find('.mobile-menu-toggle').isVisible()).toBe(true)
    expect(wrapper.find('.desktop-menu').exists()).toBe(false)
  })

  it('opens mobile menu when toggle is clicked', async () => {
    window.innerWidth = 375
    const wrapper = mount(Navigation)

    const toggle = wrapper.find('.mobile-menu-toggle')
    await toggle.trigger('click')

    expect(wrapper.find('.mobile-menu').isVisible()).toBe(true)
  })
})
```

---

### Pattern 4: Visual Regression Test

```typescript
// tests/visual/Button.visual.test.ts
import { test, expect } from '@playwright/test'

test.describe('Button Visual Regression', () => {
  test('default button matches snapshot', async ({ page }) => {
    await page.goto('/components/button')
    const button = page.locator('[data-testid="default-button"]')

    await expect(button).toHaveScreenshot('button-default.png')
  })

  test('button hover state matches snapshot', async ({ page }) => {
    await page.goto('/components/button')
    const button = page.locator('[data-testid="default-button"]')

    await button.hover()
    await expect(button).toHaveScreenshot('button-hover.png')
  })

  test('button focus state matches snapshot', async ({ page }) => {
    await page.goto('/components/button')
    const button = page.locator('[data-testid="default-button"]')

    await button.focus()
    await expect(button).toHaveScreenshot('button-focus.png')
  })

  test('disabled button matches snapshot', async ({ page }) => {
    await page.goto('/components/button')
    const button = page.locator('[data-testid="disabled-button"]')

    await expect(button).toHaveScreenshot('button-disabled.png')
  })
})
```

---

### Pattern 5: Performance Test

```typescript
// tests/performance/DataTable.perf.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import DataTable from '@/components/DataTable.vue'

describe('DataTable Performance', () => {
  it('renders 1000 rows in under 100ms', async () => {
    const data = Array.from({ length: 1000 }, (_, i) => ({
      id: i,
      name: `Item ${i}`,
      value: Math.random() * 100
    }))

    const start = performance.now()
    const wrapper = mount(DataTable, {
      props: { data }
    })
    await wrapper.vm.$nextTick()
    const end = performance.now()

    expect(end - start).toBeLessThan(100)
  })

  it('does not cause layout thrashing on scroll', async () => {
    const wrapper = mount(DataTable, {
      props: {
        data: Array.from({ length: 100 }, (_, i) => ({ id: i }))
      }
    })

    let layoutCount = 0
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.name === 'layout') layoutCount++
      }
    })

    observer.observe({ entryTypes: ['measure'] })

    const scrollable = wrapper.find('[data-scroll-container]')
    await scrollable.trigger('scroll', { target: { scrollTop: 1000 } })

    expect(layoutCount).toBeLessThan(5)
  })
})
```

---

## Accessibility Testing Tools

### Automated Tools

**axe-core**:
```typescript
import { axe, toHaveNoViolations } from 'jest-axe'
expect.extend(toHaveNoViolations)

it('has no accessibility violations', async () => {
  const wrapper = mount(Component)
  const results = await axe(wrapper.element)
  expect(results).toHaveNoViolations()
})
```

**Lighthouse CI**:
```yaml
# .lighthouserc.json
{
  "ci": {
    "collect": {
      "numberOfRuns": 3,
      "url": ["http://localhost:3000"]
    },
    "assert": {
      "assertions": {
        "categories:accessibility": ["error", {"minScore": 0.9}],
        "categories:performance": ["error", {"minScore": 0.9}]
      }
    }
  }
}
```

### Manual Testing Checklist

**Keyboard Navigation**:
- [ ] Tab through all interactive elements
- [ ] Shift+Tab navigates backwards
- [ ] Enter/Space activates buttons
- [ ] Escape closes modals/dropdowns
- [ ] Arrow keys navigate lists/menus
- [ ] Focus visible at all times

**Screen Reader Testing**:
- [ ] Test with NVDA (Windows)
- [ ] Test with JAWS (Windows)
- [ ] Test with VoiceOver (macOS/iOS)
- [ ] All images have alt text
- [ ] Form fields have labels
- [ ] Error messages announced
- [ ] Dynamic content updates announced

**Color Blindness**:
- [ ] Test with deuteranopia filter
- [ ] Test with protanopia filter
- [ ] Test with tritanopia filter
- [ ] Don't rely on color alone for information

---

## Testing Commands

### Run All Tests
```bash
# Unit tests
npm run test

# Watch mode for TDD
npm run test:watch

# Coverage report
npm run test:coverage

# Accessibility tests
npm run test:a11y

# Visual regression tests
npm run test:visual

# E2E tests
npm run test:e2e

# Performance tests
npm run test:perf
```

### Pre-Commit Verification
```bash
#!/bin/bash
# pre-commit.sh

echo "Running pre-commit checks..."

# Run tests
npm run test || exit 1

# Run accessibility audit
npm run test:a11y || exit 1

# Check TypeScript
npm run typecheck || exit 1

# Lint code
npm run lint || exit 1

# Build verification
npm run build || exit 1

echo "✅ All checks passed!"
```

---

## Performance Metrics Targets

### Core Web Vitals

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| LCP (Largest Contentful Paint) | < 2.5s | 2.5s - 4.0s | > 4.0s |
| FID (First Input Delay) | < 100ms | 100ms - 300ms | > 300ms |
| CLS (Cumulative Layout Shift) | < 0.1 | 0.1 - 0.25 | > 0.25 |

### Additional Metrics

| Metric | Target | Max |
|--------|--------|-----|
| Time to Interactive (TTI) | < 3.8s | < 7.3s |
| Total Blocking Time (TBT) | < 200ms | < 600ms |
| First Contentful Paint (FCP) | < 1.8s | < 3.0s |

---

## Continuous Integration

### GitHub Actions Example

```yaml
# .github/workflows/ui-tests.yml
name: UI Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Run unit tests
        run: npm run test:coverage

      - name: Run accessibility tests
        run: npm run test:a11y

      - name: Run visual regression tests
        run: npm run test:visual

      - name: Upload coverage
        uses: codecov/codecov-action@v3

      - name: Lighthouse CI
        run: |
          npm install -g @lhci/cli
          lhci autorun
```

---

## Summary

Effective UI/UX testing requires:
1. **TDD mindset**: Write tests before implementation
2. **Comprehensive coverage**: Unit, integration, visual, accessibility, performance
3. **Automated checks**: CI/CD pipeline with quality gates
4. **Manual testing**: Real devices, assistive technologies, edge cases
5. **Continuous monitoring**: Track metrics over time

Quality UI/UX comes from disciplined testing practices and user-centered design principles.
