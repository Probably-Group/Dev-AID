## 2. Implementation Workflow (TDD)

### Step 1: Write Failing Accessibility Test First

```typescript
// tests/components/button.a11y.test.ts
import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/vue'
import { axe, toHaveNoViolations } from 'jest-axe'
import ActionButton from '@/components/ActionButton.vue'

expect.extend(toHaveNoViolations)

describe('ActionButton Accessibility', () => {
  it('should have no accessibility violations', async () => {
    const { container } = render(ActionButton, {
      props: { label: 'Submit Form' }
    })

    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have accessible name', async () => {
    const { getByRole } = render(ActionButton, {
      props: { label: 'Submit Form' }
    })

    const button = getByRole('button', { name: 'Submit Form' })
    expect(button).toBeTruthy()
  })

  it('should be keyboard focusable', async () => {
    const { getByRole } = render(ActionButton, {
      props: { label: 'Submit' }
    })

    const button = getByRole('button')
    button.focus()
    expect(document.activeElement).toBe(button)
  })

  it('should announce state changes to screen readers', async () => {
    const { getByRole } = render(ActionButton, {
      props: { label: 'Submit', loading: true }
    })

    const button = getByRole('button')
    expect(button).toHaveAttribute('aria-busy', 'true')
  })
})
```

### Step 2: Implement Minimum to Pass

```vue
<template>
  <button
    :aria-busy="loading"
    :disabled="disabled || loading"
    class="action-button"
  >
    <span v-if="loading" aria-hidden="true" class="spinner" />
    <span>{{ label }}</span>
  </button>
</template>

<style scoped>
.action-button:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
}
</style>
```

### Step 3: Refactor Following WCAG Patterns

Enhance with additional accessibility features:
- Add proper color contrast (4.5:1 minimum for AA)
- Implement focus trap for modals
- Add live region announcements
- Optimize for screen reader navigation

### Step 4: Run Full Accessibility Verification

```bash
# Run accessibility tests
npm run test -- --grep "a11y"

# Run axe-core audit
npx @axe-core/cli http://localhost:3000

# Check with Lighthouse
npx lighthouse http://localhost:3000 --only-categories=accessibility
```

---

