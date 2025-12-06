## 6. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```typescript
// tests/components/GlassCard.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import GlassCard from '@/components/ui/GlassCard.vue'

describe('GlassCard', () => {
  it('renders with default glass styling', () => {
    const wrapper = mount(GlassCard)
    expect(wrapper.classes()).toContain('glass-card')
  })

  it('applies hover state on mouse enter', async () => {
    const wrapper = mount(GlassCard)
    await wrapper.trigger('mouseenter')
    expect(wrapper.emitted('hover')).toBeTruthy()
  })

  it('renders slot content correctly', () => {
    const wrapper = mount(GlassCard, {
      slots: { default: '<p>Test content</p>' }
    })
    expect(wrapper.text()).toContain('Test content')
  })

  it('meets accessibility requirements', () => {
    const wrapper = mount(GlassCard, {
      props: { role: 'region', ariaLabel: 'Card section' }
    })
    expect(wrapper.attributes('role')).toBe('region')
    expect(wrapper.attributes('aria-label')).toBe('Card section')
  })
})
```

### Step 2: Implement Minimum to Pass

```vue
<!-- components/ui/GlassCard.vue -->
<template>
  <div
    class="glass-card"
    :role="role"
    :aria-label="ariaLabel"
    @mouseenter="$emit('hover', true)"
    @mouseleave="$emit('hover', false)"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  role?: string
  ariaLabel?: string
}>()

defineEmits<{
  hover: [isHovered: boolean]
}>()
</script>
```

### Step 3: Refactor Following Design Patterns

Apply glass-morphism styles, ensure spacing system compliance, add transitions.

### Step 4: Run Full Verification

```bash
# Run component tests
npm run test -- --filter=GlassCard

# Check accessibility
npm run test:a11y

# Visual regression test
npm run test:visual

# Build verification
npm run build
```

---

