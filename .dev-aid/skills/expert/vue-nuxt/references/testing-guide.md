# Vue 3 / Nuxt 3 Testing Guide

This document provides comprehensive testing patterns for Vue 3 and Nuxt 3 applications following Test-Driven Development (TDD) methodology.

## 1. TDD Implementation Workflow

### Step 1: Write Failing Test First

Always start by writing tests that define expected behavior:

```typescript
// tests/components/VoiceIndicator.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import VoiceIndicator from '@/components/VoiceIndicator.vue'

describe('VoiceIndicator', () => {
  it('displays idle state by default', () => {
    const wrapper = mount(VoiceIndicator)
    expect(wrapper.find('.indicator').classes()).toContain('idle')
    expect(wrapper.text()).toContain('Ready')
  })

  it('shows listening state when active', async () => {
    const wrapper = mount(VoiceIndicator, {
      props: { isListening: true }
    })
    expect(wrapper.find('.indicator').classes()).toContain('listening')
    expect(wrapper.find('.pulse-animation').exists()).toBe(true)
  })

  it('emits cancel event on escape key', async () => {
    const wrapper = mount(VoiceIndicator, {
      props: { isListening: true }
    })
    await wrapper.trigger('keydown.escape')
    expect(wrapper.emitted('cancel')).toBeTruthy()
  })
})
```

### Step 2: Implement Minimum to Pass

Write only enough code to make the tests pass:

```vue
<script setup lang="ts">
const props = defineProps<{ isListening?: boolean }>()
const emit = defineEmits<{ 'cancel': [] }>()

const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Escape') emit('cancel')
}
</script>

<template>
  <div
    class="indicator"
    :class="isListening ? 'listening' : 'idle'"
    @keydown="handleKeydown"
    tabindex="0"
  >
    <span v-if="!isListening">Ready</span>
    <div v-else class="pulse-animation" />
  </div>
</template>
```

### Step 3: Refactor if Needed

After tests pass, improve code quality without changing behavior. Re-run tests after each refactor.

```vue
<script setup lang="ts">
// Refactored version with better organization
interface Props {
  isListening?: boolean
}

interface Emits {
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  isListening: false
})

const emit = defineEmits<Emits>()

const indicatorClass = computed(() => ({
  'indicator': true,
  'listening': props.isListening,
  'idle': !props.isListening
}))

const handleKeydown = (e: KeyboardEvent) => {
  if (e.key === 'Escape') {
    emit('cancel')
  }
}
</script>

<template>
  <div
    :class="indicatorClass"
    @keydown="handleKeydown"
    tabindex="0"
  >
    <span v-if="!isListening">Ready</span>
    <div v-else class="pulse-animation" />
  </div>
</template>
```

### Step 4: Run Full Verification

```bash
# Run all verification steps before committing
npx vitest run                    # Unit tests
npx eslint . --ext .vue,.ts       # Linting
npx nuxi typecheck                # Type checking
npm run build                     # Build verification
```

## 2. Component Testing Patterns

### Testing Props and Events

```typescript
// tests/components/HUDPanel.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import HUDPanel from '@/components/HUDPanel.vue'

describe('HUDPanel', () => {
  it('renders with required props', () => {
    const wrapper = mount(HUDPanel, {
      props: {
        title: 'System Status',
        status: 'active'
      }
    })

    expect(wrapper.text()).toContain('System Status')
    expect(wrapper.find('.status').classes()).toContain('active')
  })

  it('emits update event on user interaction', async () => {
    const wrapper = mount(HUDPanel, {
      props: { title: 'Test' }
    })

    await wrapper.find('.update-button').trigger('click')

    expect(wrapper.emitted()).toHaveProperty('update')
    expect(wrapper.emitted('update')?.[0]).toEqual([{ timestamp: expect.any(Number) }])
  })
})
```

### Testing Composables

```typescript
// tests/composables/useSanitize.test.ts
import { describe, it, expect } from 'vitest'
import { useSanitize } from '@/composables/useSanitize'

describe('useSanitize', () => {
  const { sanitizeHTML, sanitizeText } = useSanitize()

  describe('sanitizeHTML', () => {
    it('allows safe HTML tags', () => {
      const input = '<strong>Bold</strong> <em>italic</em>'
      const result = sanitizeHTML(input)
      expect(result).toContain('<strong>')
      expect(result).toContain('<em>')
    })

    it('removes dangerous tags', () => {
      const input = '<script>alert("xss")</script><strong>Safe</strong>'
      const result = sanitizeHTML(input)
      expect(result).not.toContain('<script>')
      expect(result).toContain('<strong>')
    })

    it('removes javascript: URLs', () => {
      const input = '<a href="javascript:alert(1)">Click</a>'
      const result = sanitizeHTML(input)
      expect(result).not.toContain('javascript:')
    })
  })

  describe('sanitizeText', () => {
    it('strips all HTML tags', () => {
      const input = '<div><p>Hello <strong>World</strong></p></div>'
      const result = sanitizeText(input)
      expect(result).toBe('Hello World')
      expect(result).not.toContain('<')
    })
  })
})
```

### Testing Async Operations

```typescript
// tests/composables/useDataFetch.test.ts
import { describe, it, expect, vi } from 'vitest'
import { useDataFetch } from '@/composables/useDataFetch'

// Mock $fetch
global.$fetch = vi.fn()

describe('useDataFetch', () => {
  it('fetches data successfully', async () => {
    const mockData = { id: 1, name: 'Test' }
    global.$fetch.mockResolvedValueOnce(mockData)

    const { data, error, loading, fetchData } = useDataFetch()

    expect(loading.value).toBe(false)

    const promise = fetchData('/api/test')
    expect(loading.value).toBe(true)

    await promise

    expect(loading.value).toBe(false)
    expect(data.value).toEqual(mockData)
    expect(error.value).toBeNull()
  })

  it('handles fetch errors', async () => {
    const mockError = new Error('Network error')
    global.$fetch.mockRejectedValueOnce(mockError)

    const { data, error, loading, fetchData } = useDataFetch()

    await fetchData('/api/test')

    expect(loading.value).toBe(false)
    expect(data.value).toBeNull()
    expect(error.value).toBe(mockError)
  })
})
```

### Testing with Pinia Stores

```typescript
// tests/stores/auth.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('initializes with logged out state', () => {
    const auth = useAuthStore()

    expect(auth.isAuthenticated).toBe(false)
    expect(auth.user).toBeNull()
  })

  it('updates state on login', async () => {
    const auth = useAuthStore()
    const mockUser = { id: 1, email: 'test@example.com' }

    await auth.login({ email: 'test@example.com', password: 'password' })

    expect(auth.isAuthenticated).toBe(true)
    expect(auth.user).toEqual(mockUser)
  })

  it('clears state on logout', async () => {
    const auth = useAuthStore()
    await auth.login({ email: 'test@example.com', password: 'password' })

    await auth.logout()

    expect(auth.isAuthenticated).toBe(false)
    expect(auth.user).toBeNull()
  })
})
```

## 3. Security Testing

### XSS Prevention Tests

```typescript
// tests/security/xss.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import HUDPanel from '@/components/HUDPanel.vue'

describe('XSS Prevention', () => {
  it('should sanitize malicious input', () => {
    const wrapper = mount(HUDPanel, {
      props: {
        title: '<script>alert("xss")</script>Hello'
      }
    })

    expect(wrapper.html()).not.toContain('<script>')
    expect(wrapper.text()).toContain('Hello')
  })

  it('should prevent javascript: URLs', () => {
    const wrapper = mount(HUDPanel, {
      props: {
        link: 'javascript:alert(1)'
      }
    })

    const anchor = wrapper.find('a')
    expect(anchor.attributes('href')).not.toContain('javascript:')
  })

  it('should escape user-provided HTML attributes', () => {
    const wrapper = mount(HUDPanel, {
      props: {
        customClass: '" onload="alert(1)'
      }
    })

    expect(wrapper.html()).not.toContain('onload=')
  })
})
```

### Input Validation Tests

```typescript
// tests/components/HUDDisplay.test.ts
describe('HUDDisplay', () => {
  it('validates metric bounds', () => {
    const wrapper = mount(HUDDisplay, {
      props: {
        metrics: { cpu: 150, memory: -10, status: 'active' }
      }
    })

    // Should clamp values to valid range
    expect(wrapper.vm.validatedMetrics.cpu).toBe(100)
    expect(wrapper.vm.validatedMetrics.memory).toBe(0)
  })

  it('sanitizes text fields', () => {
    const wrapper = mount(HUDDisplay, {
      props: {
        metrics: {
          cpu: 50,
          memory: 60,
          status: '<script>alert("xss")</script>Normal'
        }
      }
    })

    expect(wrapper.text()).not.toContain('<script>')
    expect(wrapper.text()).toContain('Normal')
  })
})
```

## 4. Server Route Testing

### API Route Tests

```typescript
// tests/server/api/command.test.ts
import { describe, it, expect } from 'vitest'
import { setup, $fetch } from '@nuxt/test-utils'

describe('/api/jarvis/command', () => {
  await setup()

  it('rejects invalid command format', async () => {
    const response = await $fetch('/api/jarvis/command', {
      method: 'POST',
      body: {
        action: 'invalid',
        target: 'test'
      }
    }).catch(err => err)

    expect(response.statusCode).toBe(400)
    expect(response.message).toContain('Invalid command format')
  })

  it('accepts valid command', async () => {
    const response = await $fetch('/api/jarvis/command', {
      method: 'POST',
      body: {
        action: 'status',
        target: 'system-01'
      }
    })

    expect(response.success).toBe(true)
    expect(response.commandId).toBeDefined()
  })

  it('validates target format', async () => {
    const response = await $fetch('/api/jarvis/command', {
      method: 'POST',
      body: {
        action: 'status',
        target: '../../../etc/passwd'  // Path traversal attempt
      }
    }).catch(err => err)

    expect(response.statusCode).toBe(400)
  })
})
```

### Middleware Tests

```typescript
// tests/middleware/auth.test.ts
import { describe, it, expect } from 'vitest'
import { setup } from '@nuxt/test-utils'

describe('auth middleware', () => {
  await setup()

  it('redirects unauthenticated users to login', async () => {
    const { statusCode, headers } = await $fetch('/dashboard', {
      redirect: 'manual'
    })

    expect(statusCode).toBe(302)
    expect(headers.get('location')).toBe('/login')
  })

  it('allows authenticated users', async () => {
    const { statusCode } = await $fetch('/dashboard', {
      headers: {
        Cookie: 'auth-token=valid-token'
      }
    })

    expect(statusCode).toBe(200)
  })
})
```

## 5. E2E Testing with Playwright

### Basic E2E Test

```typescript
// tests/e2e/dashboard.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Dashboard', () => {
  test('displays HUD components', async ({ page }) => {
    await page.goto('/dashboard')

    await expect(page.locator('.hud-panel')).toBeVisible()
    await expect(page.locator('.status-indicator')).toHaveText('Active')
  })

  test('handles voice command interaction', async ({ page }) => {
    await page.goto('/dashboard')

    await page.click('.voice-button')
    await expect(page.locator('.voice-indicator')).toHaveClass(/listening/)

    await page.keyboard.press('Escape')
    await expect(page.locator('.voice-indicator')).not.toHaveClass(/listening/)
  })
})
```

### Testing with Authentication

```typescript
// tests/e2e/auth.setup.ts
import { test as setup } from '@playwright/test'

setup('authenticate', async ({ page }) => {
  await page.goto('/login')
  await page.fill('[name="email"]', 'test@example.com')
  await page.fill('[name="password"]', 'password')
  await page.click('button[type="submit"]')

  await page.waitForURL('/dashboard')
  await page.context().storageState({ path: 'tests/e2e/.auth/user.json' })
})
```

## 6. Test Configuration

### Vitest Configuration

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'jsdom',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.d.ts',
        '**/*.config.*'
      ]
    },
    globals: true,
    setupFiles: ['tests/setup.ts']
  }
})
```

### Test Setup File

```typescript
// tests/setup.ts
import { config } from '@vue/test-utils'
import { vi } from 'vitest'

// Mock Nuxt composables
config.global.mocks = {
  $fetch: vi.fn(),
  useRuntimeConfig: () => ({
    public: {
      apiBase: '/api'
    }
  })
}

// Mock router
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn()
  }),
  useRoute: () => ({
    params: {},
    query: {}
  })
}))
```

## 7. Testing Best Practices

### Test Organization
- Group related tests with `describe()`
- Use descriptive test names that explain the behavior
- Follow AAA pattern: Arrange, Act, Assert
- One assertion per test (when possible)

### Coverage Goals
- Aim for 80%+ code coverage
- 100% coverage for security-critical code
- Focus on behavior, not implementation details

### Common Patterns
```typescript
// ✅ Test behavior, not implementation
it('updates display when metrics change', async () => {
  const wrapper = mount(HUDDisplay, {
    props: { metrics: { cpu: 50 } }
  })

  await wrapper.setProps({ metrics: { cpu: 75 } })

  expect(wrapper.text()).toContain('75')
})

// ❌ Don't test implementation details
it('calls updateDisplay method', async () => {
  // This is testing implementation, not behavior
  const wrapper = mount(HUDDisplay)
  const spy = vi.spyOn(wrapper.vm, 'updateDisplay')

  await wrapper.setProps({ metrics: { cpu: 75 } })

  expect(spy).toHaveBeenCalled()
})
```

## Testing Checklist

- [ ] Write tests before implementation (TDD)
- [ ] Test all component props and events
- [ ] Test error states and edge cases
- [ ] Security tests for XSS and injection
- [ ] API route validation tests
- [ ] E2E tests for critical user flows
- [ ] Achieve 80%+ code coverage
- [ ] Run all tests before committing
