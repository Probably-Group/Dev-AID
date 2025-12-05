# Vue 3 & Nuxt 3 Testing Guide

This guide covers comprehensive testing patterns for Vue 3 and Nuxt 3 applications using Vitest and Vue Test Utils.

---

## Test Configuration

### Vitest Configuration

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'happy-dom',
    globals: true,
    setupFiles: ['./tests/setup.ts'],
    include: ['tests/**/*.test.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules/', 'tests/']
    }
  },
  resolve: {
    alias: {
      '~': resolve(__dirname, './')
    }
  }
})
```

### Test Setup File

```typescript
// tests/setup.ts
import { config } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'

// Global plugins
config.global.plugins = [createTestingPinia()]

// Mock Nuxt composables
vi.mock('#app', () => ({
  useNuxtApp: () => ({ $fetch: vi.fn() }),
  useRuntimeConfig: () => ({ public: {} }),
  useFetch: vi.fn(),
  useAsyncData: vi.fn(),
  navigateTo: vi.fn(),
  definePageMeta: vi.fn()
}))

// Mock $fetch globally
vi.stubGlobal('$fetch', vi.fn())
```

---

## Component Testing Patterns

### Basic Component Tests

```typescript
// tests/components/UserCard.test.ts
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import UserCard from '~/components/UserCard.vue'

describe('UserCard', () => {
  it('displays user name and email', () => {
    const wrapper = mount(UserCard, {
      props: {
        user: {
          id: '1',
          name: 'John Doe',
          email: 'john@example.com'
        }
      },
      global: {
        plugins: [createTestingPinia()]
      }
    })

    expect(wrapper.text()).toContain('John Doe')
    expect(wrapper.text()).toContain('john@example.com')
  })

  it('emits select event when clicked', async () => {
    const wrapper = mount(UserCard, {
      props: {
        user: { id: '1', name: 'John', email: 'john@test.com' }
      }
    })

    await wrapper.trigger('click')
    expect(wrapper.emitted('select')).toBeTruthy()
    expect(wrapper.emitted('select')[0]).toEqual(['1'])
  })

  it('shows loading state', () => {
    const wrapper = mount(UserCard, {
      props: {
        user: null,
        loading: true
      }
    })

    expect(wrapper.find('[data-testid="loading-skeleton"]').exists()).toBe(true)
  })
})
```

### Form Component Tests

```typescript
// tests/components/Form.test.ts
import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import Form from '~/components/Form.vue'

describe('Form', () => {
  it('validates required fields', async () => {
    const wrapper = mount(Form)

    await wrapper.find('form').trigger('submit')

    expect(wrapper.find('.error').text()).toContain('Name is required')
  })

  it('submits valid data', async () => {
    const onSubmit = vi.fn()
    const wrapper = mount(Form, {
      props: { onSubmit }
    })

    await wrapper.find('input[name="name"]').setValue('John')
    await wrapper.find('input[name="email"]').setValue('john@test.com')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(onSubmit).toHaveBeenCalledWith({
      name: 'John',
      email: 'john@test.com'
    })
  })

  it('shows loading state during submission', async () => {
    const wrapper = mount(Form, {
      props: {
        onSubmit: () => new Promise(r => setTimeout(r, 100))
      }
    })

    await wrapper.find('input[name="name"]').setValue('John')
    await wrapper.find('form').trigger('submit')

    expect(wrapper.find('button').attributes('disabled')).toBeDefined()
    expect(wrapper.find('.loading').exists()).toBe(true)
  })
})
```

---

## Composable Testing

### Testing Async Data Composable

```typescript
// tests/composables/useAsyncData.test.ts
import { describe, it, expect, vi } from 'vitest'
import { useAsyncData } from '~/composables/useAsyncData'

describe('useAsyncData', () => {
  it('fetches data successfully', async () => {
    const mockData = { id: 1, name: 'Test' }
    const fetcher = vi.fn().mockResolvedValue(mockData)

    const { data, loading, error, execute } = useAsyncData(fetcher, {
      immediate: false
    })

    expect(data.value).toBeNull()
    expect(loading.value).toBe(false)

    await execute()

    expect(fetcher).toHaveBeenCalledOnce()
    expect(data.value).toEqual(mockData)
    expect(error.value).toBeNull()
  })

  it('handles errors', async () => {
    const mockError = new Error('Network error')
    const fetcher = vi.fn().mockRejectedValue(mockError)
    const onError = vi.fn()

    const { data, error, execute } = useAsyncData(fetcher, {
      immediate: false,
      onError
    })

    await execute()

    expect(error.value).toBe(mockError)
    expect(data.value).toBeNull()
    expect(onError).toHaveBeenCalledWith(mockError)
  })

  it('transforms data', async () => {
    const fetcher = vi.fn().mockResolvedValue({ users: [{ id: 1 }] })
    const transform = (data: any) => data.users

    const { data, execute } = useAsyncData(fetcher, {
      immediate: false,
      transform
    })

    await execute()

    expect(data.value).toEqual([{ id: 1 }])
  })
})
```

### Testing API Composable

```typescript
// tests/composables/useApi.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { flushPromises } from '@vue/test-utils'
import { useApi } from '~/composables/useApi'

describe('useApi', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('handles concurrent requests', async () => {
    const results = ['first', 'second']
    let callCount = 0

    vi.mocked($fetch).mockImplementation(() =>
      Promise.resolve(results[callCount++])
    )

    const { data, execute } = useApi('/api/test')

    // Fire two requests
    execute()
    execute()
    await flushPromises()

    // Should have latest result
    expect(data.value).toBe('second')
  })

  it('cancels pending request on new request', async () => {
    const abortSpy = vi.fn()
    vi.mocked($fetch).mockImplementation((_, opts) => {
      opts?.signal?.addEventListener('abort', abortSpy)
      return new Promise(() => {})
    })

    const { execute } = useApi('/api/test')

    execute()
    execute() // Should cancel first

    expect(abortSpy).toHaveBeenCalled()
  })
})
```

---

## Pinia Store Testing

### Basic Store Tests

```typescript
// tests/stores/user.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useUserStore } from '~/stores/user'

// Mock $fetch
vi.stubGlobal('$fetch', vi.fn())

describe('useUserStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('logs in user successfully', async () => {
    const mockResponse = {
      user: { id: '1', email: 'test@test.com', name: 'Test', roles: [] },
      token: 'mock-token'
    }
    vi.mocked($fetch).mockResolvedValue(mockResponse)

    const store = useUserStore()
    await store.login('test@test.com', 'password')

    expect($fetch).toHaveBeenCalledWith('/api/auth/login', {
      method: 'POST',
      body: { email: 'test@test.com', password: 'password' }
    })
    expect(store.currentUser).toEqual(mockResponse.user)
    expect(store.isAuthenticated).toBe(true)
  })

  it('checks user roles correctly', async () => {
    const store = useUserStore()
    store.currentUser = {
      id: '1',
      email: 'admin@test.com',
      name: 'Admin',
      roles: ['admin', 'user']
    }

    expect(store.hasRole('admin')).toBe(true)
    expect(store.hasRole('superadmin')).toBe(false)
  })

  it('clears state on logout', async () => {
    vi.mocked($fetch).mockResolvedValue({})

    const store = useUserStore()
    store.currentUser = { id: '1', email: 'test@test.com', name: 'Test', roles: [] }
    store.token = 'token'

    await store.logout()

    expect(store.currentUser).toBeNull()
    expect(store.token).toBeNull()
    expect(store.isAuthenticated).toBe(false)
  })
})
```

---

## Mocking Nuxt Composables

### Mocking useFetch

```typescript
// tests/pages/index.test.ts
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import IndexPage from '~/pages/index.vue'

vi.mock('#app', () => ({
  useFetch: vi.fn(() => ({
    data: ref([
      { id: 1, name: 'Item 1' },
      { id: 2, name: 'Item 2' }
    ]),
    pending: ref(false),
    error: ref(null),
    refresh: vi.fn()
  }))
}))

describe('IndexPage', () => {
  it('displays fetched items', () => {
    const wrapper = mount(IndexPage)

    expect(wrapper.text()).toContain('Item 1')
    expect(wrapper.text()).toContain('Item 2')
  })
})
```

### Mocking useRoute

```typescript
import { describe, it, expect, vi } from 'vitest'

vi.mock('#app', () => ({
  useRoute: vi.fn(() => ({
    params: { id: '123' },
    query: { page: '1' },
    path: '/users/123'
  }))
}))

describe('UserPage', () => {
  it('uses route params', () => {
    const route = useRoute()
    expect(route.params.id).toBe('123')
  })
})
```

---

## Integration Tests

### Testing Component Interactions

```typescript
// tests/integration/userManagement.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import UserList from '~/components/UserList.vue'
import { useUserStore } from '~/stores/user'

describe('User Management Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('loads and displays users', async () => {
    const mockUsers = [
      { id: '1', name: 'John', email: 'john@test.com' },
      { id: '2', name: 'Jane', email: 'jane@test.com' }
    ]

    vi.mocked($fetch).mockResolvedValue(mockUsers)

    const wrapper = mount(UserList, {
      global: {
        plugins: [createTestingPinia()]
      }
    })

    await wrapper.vm.$nextTick()

    expect(wrapper.findAll('[data-testid="user-card"]')).toHaveLength(2)
  })

  it('handles user selection', async () => {
    const wrapper = mount(UserList, {
      global: {
        plugins: [createTestingPinia()]
      }
    })

    const userCard = wrapper.find('[data-testid="user-card"]')
    await userCard.trigger('click')

    expect(wrapper.emitted('userSelected')).toBeTruthy()
  })
})
```

---

## E2E Testing (Optional)

### Playwright Configuration

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  use: {
    baseURL: 'http://localhost:3000',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure'
  },
  webServer: {
    command: 'npm run dev',
    port: 3000,
    reuseExistingServer: !process.env.CI
  }
})
```

### E2E Test Example

```typescript
// tests/e2e/login.test.ts
import { test, expect } from '@playwright/test'

test('user can log in', async ({ page }) => {
  await page.goto('/login')

  await page.fill('input[name="email"]', 'test@example.com')
  await page.fill('input[name="password"]', 'password123')
  await page.click('button[type="submit"]')

  await expect(page).toHaveURL('/dashboard')
  await expect(page.locator('h1')).toContainText('Dashboard')
})
```

---

## Testing Best Practices

### 1. Use Data Test IDs

```vue
<template>
  <!-- Good: Use data-testid for stable selectors -->
  <button data-testid="submit-button">Submit</button>

  <!-- Avoid: Using classes or text content -->
  <button class="btn-primary">Submit</button>
</template>
```

```typescript
// Test
const button = wrapper.find('[data-testid="submit-button"]')
```

### 2. Test User Behavior, Not Implementation

```typescript
// ❌ BAD: Testing implementation details
it('sets loading to true', async () => {
  const wrapper = mount(Component)
  expect(wrapper.vm.loading).toBe(true)
})

// ✅ GOOD: Testing user-visible behavior
it('shows loading spinner', async () => {
  const wrapper = mount(Component)
  expect(wrapper.find('[data-testid="loading-spinner"]').exists()).toBe(true)
})
```

### 3. Use Factories for Test Data

```typescript
// tests/factories/user.ts
export function createUser(overrides = {}) {
  return {
    id: '1',
    name: 'Test User',
    email: 'test@example.com',
    roles: ['user'],
    ...overrides
  }
}

// Usage
const admin = createUser({ roles: ['admin'] })
const john = createUser({ name: 'John' })
```

### 4. Clean Up After Tests

```typescript
describe('Component', () => {
  let wrapper: VueWrapper

  afterEach(() => {
    wrapper?.unmount()
    vi.clearAllMocks()
  })

  it('test case', () => {
    wrapper = mount(Component)
    // test code
  })
})
```

---

## Coverage Configuration

```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      include: ['components/**', 'composables/**', 'stores/**'],
      exclude: [
        'node_modules/',
        'tests/',
        '**/*.test.ts',
        '**/*.spec.ts'
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        branches: 80,
        statements: 80
      }
    }
  }
})
```

---

## Running Tests

```bash
# Run all tests
npm run test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm run test tests/components/UserCard.test.ts

# Run E2E tests
npm run test:e2e

# Type checking
npm run typecheck

# Lint
npm run lint
```

---

## Test Commands Reference

```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage",
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui"
  }
}
```
