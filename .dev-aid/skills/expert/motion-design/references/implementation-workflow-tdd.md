## 6. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```typescript
// tests/animations/modal.test.ts
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import AnimatedModal from '~/components/AnimatedModal.vue'

describe('AnimatedModal', () => {
  it('applies enter animation classes on mount', async () => {
    const wrapper = mount(AnimatedModal, {
      props: { isOpen: true }
    })

    expect(wrapper.classes()).toContain('modal-enter-active')
  })

  it('respects reduced motion preference', async () => {
    // Mock matchMedia
    window.matchMedia = vi.fn().mockImplementation(query => ({
      matches: query === '(prefers-reduced-motion: reduce)',
      addEventListener: vi.fn(),
      removeEventListener: vi.fn()
    }))

    const wrapper = mount(AnimatedModal, {
      props: { isOpen: true }
    })

    expect(wrapper.classes()).toContain('reduced-motion')
  })

  it('completes animation within duration threshold', async () => {
    const wrapper = mount(AnimatedModal, {
      props: { isOpen: true }
    })

    const style = getComputedStyle(wrapper.element)
    const duration = parseFloat(style.animationDuration) * 1000

    expect(duration).toBeLessThanOrEqual(300) // Max 300ms for modals
  })
})
```

### Step 2: Implement Minimum to Pass

```vue
<template>
  <Transition name="modal">
    <div
      v-if="isOpen"
      class="modal"
      :class="{ 'reduced-motion': prefersReducedMotion }"
    >
      <slot />
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { useReducedMotion } from '~/composables/useReducedMotion'

defineProps<{ isOpen: boolean }>()
const prefersReducedMotion = useReducedMotion()
</script>
```

### Step 3: Refactor Following Patterns

- Extract animation timing to design tokens
- Add GPU-accelerated properties only
- Ensure proper cleanup on unmount

### Step 4: Run Full Verification

```bash
# Run animation tests
npm test -- --grep "animation"

# Check for layout thrashing
npm run lighthouse -- --only-categories=performance

# Verify reduced motion support
npm run test:a11y
```

---

