## 7. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```typescript
// tests/tokens.test.ts
import { describe, it, expect } from 'vitest'
import { tokens } from '../tokens'

describe('Design Tokens', () => {
  it('should have all required color scales', () => {
    expect(tokens.colors.gray).toBeDefined()
    expect(tokens.colors.blue).toBeDefined()
    expect(Object.keys(tokens.colors.gray)).toHaveLength(10)
  })

  it('should have semantic tokens referencing core tokens', () => {
    expect(tokens.semantic.textPrimary).toBe(tokens.colors.gray[900])
    expect(tokens.semantic.bgPrimary).toBe(tokens.colors.white)
  })

  it('should generate valid CSS custom properties', () => {
    const css = tokens.toCSS()
    expect(css).toContain('--color-gray-500')
    expect(css).toContain('--color-text-primary')
  })
})

// tests/components/Button.test.ts
import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import Button from '../components/Button.vue'

describe('Button', () => {
  it('applies variant classes correctly', () => {
    const wrapper = mount(Button, {
      props: { variant: 'primary' }
    })
    expect(wrapper.classes()).toContain('button--primary')
  })

  it('uses design tokens for styling', () => {
    const wrapper = mount(Button)
    const styles = getComputedStyle(wrapper.element)
    expect(styles.getPropertyValue('--button-bg')).toBeTruthy()
  })
})
```

### Step 2: Implement Minimum to Pass

```typescript
// tokens/index.ts
export const tokens = {
  colors: {
    gray: { 50: '#f9fafb', /* ... */ 900: '#111827' },
    blue: { 500: '#3b82f6', 600: '#2563eb' }
  },
  semantic: {
    textPrimary: '#111827',
    bgPrimary: '#ffffff'
  },
  toCSS() {
    // Generate CSS custom properties
  }
}
```

### Step 3: Refactor Following Patterns

Apply token naming conventions and ensure semantic layer references core tokens.

### Step 4: Run Full Verification

```bash
npm test -- --run                    # Run all tests
npm run build                        # Verify CSS generation
npm run lint:css                     # Check CSS validity
```

---

