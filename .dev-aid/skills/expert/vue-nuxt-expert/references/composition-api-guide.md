# Vue 3 Composition API Guide

This guide covers best practices and patterns for using the Vue 3 Composition API effectively.

---

## Pattern 1: Composable-First Architecture

**Use composables to extract and reuse logic across components:**

```typescript
// composables/useAsyncData.ts
import { ref, type Ref } from 'vue'

export interface UseAsyncDataOptions<T> {
  immediate?: boolean
  onError?: (error: Error) => void
  transform?: (data: any) => T
}

export function useAsyncData<T>(
  fetcher: () => Promise<T>,
  options: UseAsyncDataOptions<T> = {}
) {
  const { immediate = true, onError, transform } = options

  const data: Ref<T | null> = ref(null)
  const error: Ref<Error | null> = ref(null)
  const loading = ref(false)

  const execute = async () => {
    loading.value = true
    error.value = null

    try {
      const result = await fetcher()
      data.value = transform ? transform(result) : result
    } catch (e) {
      error.value = e as Error
      onError?.(e as Error)
    } finally {
      loading.value = false
    }
  }

  if (immediate) execute()

  return { data, error, loading, execute }
}
```

**Usage:**
```vue
<script setup lang="ts">
import { useAsyncData } from '~/composables/useAsyncData'

interface User {
  id: string
  name: string
}

const { data: user, loading, error } = useAsyncData<User>(
  () => $fetch('/api/user/me'),
  { immediate: true }
)
</script>
```

---

## Pattern 2: Type-Safe Pinia Stores

**Create strongly-typed stores with composition API:**

```typescript
// stores/user.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface User {
  id: string
  email: string
  name: string
  roles: string[]
}

export const useUserStore = defineStore('user', () => {
  // State
  const currentUser = ref<User | null>(null)
  const token = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!currentUser.value)
  const hasRole = computed(() => (role: string) =>
    currentUser.value?.roles.includes(role) ?? false
  )

  // Actions
  async function login(email: string, password: string) {
    const response = await $fetch<{ user: User; token: string }>('/api/auth/login', {
      method: 'POST',
      body: { email, password }
    })

    currentUser.value = response.user
    token.value = response.token

    // Persist token
    if (process.client) {
      localStorage.setItem('auth_token', response.token)
    }
  }

  async function logout() {
    await $fetch('/api/auth/logout', { method: 'POST' })
    currentUser.value = null
    token.value = null

    if (process.client) {
      localStorage.removeItem('auth_token')
    }
  }

  async function fetchCurrentUser() {
    if (!token.value) return

    try {
      const user = await $fetch<User>('/api/user/me', {
        headers: { Authorization: `Bearer ${token.value}` }
      })
      currentUser.value = user
    } catch (error) {
      // Token invalid, clear auth state
      await logout()
    }
  }

  return {
    currentUser,
    token,
    isAuthenticated,
    hasRole,
    login,
    logout,
    fetchCurrentUser
  }
})
```

---

## Pattern 3: VueUse Integration

**Leverage VueUse composables for robust functionality:**

```vue
<script setup lang="ts">
import { useLocalStorage, useMediaQuery, useIntersectionObserver } from '@vueuse/core'
import { ref, watch } from 'vue'

// Persistent dark mode
const isDark = useLocalStorage('dark-mode', false)

// Responsive breakpoints
const isMobile = useMediaQuery('(max-width: 768px)')
const isTablet = useMediaQuery('(min-width: 769px) and (max-width: 1024px)')
const isDesktop = useMediaQuery('(min-width: 1025px)')

// Infinite scroll with intersection observer
const target = ref<HTMLElement | null>(null)
const isVisible = ref(false)

useIntersectionObserver(
  target,
  ([{ isIntersecting }]) => {
    isVisible.value = isIntersecting
  },
  { threshold: 0.5 }
)

// Load more when target is visible
watch(isVisible, (visible) => {
  if (visible && !loading.value) {
    loadMore()
  }
})

const loadMore = async () => {
  // Load more items
}
</script>

<template>
  <div :class="{ dark: isDark }">
    <button @click="isDark = !isDark">
      Toggle {{ isDark ? 'Light' : 'Dark' }} Mode
    </button>

    <div v-if="isMobile">Mobile View</div>
    <div v-else-if="isTablet">Tablet View</div>
    <div v-else>Desktop View</div>

    <!-- Items list -->
    <div v-for="item in items" :key="item.id">
      {{ item.name }}
    </div>

    <!-- Intersection observer target for infinite scroll -->
    <div ref="target" class="loading-trigger">
      <span v-if="isVisible">Loading more...</span>
    </div>
  </div>
</template>
```

---

## Advanced Composable Patterns

### Composable with Lifecycle Management

```typescript
// composables/useWebSocket.ts
import { ref, onUnmounted } from 'vue'

export function useWebSocket(url: string) {
  const ws = ref<WebSocket | null>(null)
  const data = ref<any>(null)
  const status = ref<'connecting' | 'connected' | 'disconnected'>('connecting')

  const connect = () => {
    ws.value = new WebSocket(url)

    ws.value.onopen = () => {
      status.value = 'connected'
    }

    ws.value.onmessage = (event) => {
      data.value = JSON.parse(event.data)
    }

    ws.value.onclose = () => {
      status.value = 'disconnected'
    }
  }

  const send = (message: any) => {
    if (ws.value?.readyState === WebSocket.OPEN) {
      ws.value.send(JSON.stringify(message))
    }
  }

  const close = () => {
    ws.value?.close()
  }

  // Auto cleanup
  onUnmounted(() => {
    close()
  })

  connect()

  return {
    data,
    status,
    send,
    close,
    reconnect: connect
  }
}
```

### Composable with Dependency Injection

```typescript
// composables/useNotifications.ts
import { inject, provide, ref, type InjectionKey } from 'vue'

interface Notification {
  id: string
  type: 'success' | 'error' | 'info'
  message: string
}

interface NotificationService {
  notifications: Ref<Notification[]>
  add: (notification: Omit<Notification, 'id'>) => void
  remove: (id: string) => void
}

const NotificationSymbol: InjectionKey<NotificationService> = Symbol('notifications')

export function provideNotifications() {
  const notifications = ref<Notification[]>([])

  const add = (notification: Omit<Notification, 'id'>) => {
    const id = Math.random().toString(36).substr(2, 9)
    notifications.value.push({ ...notification, id })

    // Auto remove after 5 seconds
    setTimeout(() => remove(id), 5000)
  }

  const remove = (id: string) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  const service = { notifications, add, remove }
  provide(NotificationSymbol, service)

  return service
}

export function useNotifications() {
  const service = inject(NotificationSymbol)
  if (!service) {
    throw new Error('useNotifications must be used within a provider')
  }
  return service
}
```

**Usage:**
```vue
<!-- app.vue -->
<script setup lang="ts">
const { notifications } = provideNotifications()
</script>

<template>
  <div>
    <NuxtPage />
    <NotificationList :notifications="notifications" />
  </div>
</template>
```

```vue
<!-- pages/index.vue -->
<script setup lang="ts">
const { add } = useNotifications()

const handleSuccess = () => {
  add({ type: 'success', message: 'Operation completed!' })
}
</script>
```

---

## Reactivity Best Practices

### Preserving Reactivity with Destructuring

```typescript
// ❌ WRONG: Loses reactivity
const userStore = useUserStore()
const { currentUser } = userStore // Not reactive!

watch(currentUser, () => {
  console.log('This will never trigger!')
})
```

```typescript
// ✅ CORRECT: Preserve reactivity with storeToRefs
import { storeToRefs } from 'pinia'

const userStore = useUserStore()
const { currentUser } = storeToRefs(userStore) // Reactive!

watch(currentUser, () => {
  console.log('This works!')
})

// Or access directly
watch(() => userStore.currentUser, () => {
  console.log('This also works!')
})
```

### Using toRefs and toRef

```typescript
import { reactive, toRefs, toRef } from 'vue'

const state = reactive({
  count: 0,
  name: 'John'
})

// Convert all properties to refs
const { count, name } = toRefs(state)

// Convert single property to ref
const count = toRef(state, 'count')

// Both preserve reactivity
watch(count, (newCount) => {
  console.log('Count changed:', newCount)
})
```

---

## Component Communication Patterns

### Props and Emits with TypeScript

```vue
<script setup lang="ts">
interface User {
  id: string
  name: string
  email: string
}

interface Props {
  user: User | null
  loading?: boolean
  variant?: 'default' | 'compact' | 'detailed'
}

interface Emits {
  select: [id: string]
  update: [user: User]
  delete: [id: string]
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  variant: 'default'
})

const emit = defineEmits<Emits>()

const handleSelect = () => {
  if (props.user) {
    emit('select', props.user.id)
  }
}

const handleUpdate = (updatedUser: User) => {
  emit('update', updatedUser)
}
</script>
```

### Provide/Inject for Deep Component Trees

```typescript
// Parent component
const theme = ref<'light' | 'dark'>('light')
provide('theme', theme)

// Deep child component
const theme = inject<Ref<'light' | 'dark'>>('theme')

// With default value
const theme = inject('theme', ref('light'))

// With type safety and symbol
import type { InjectionKey } from 'vue'

const ThemeKey: InjectionKey<Ref<'light' | 'dark'>> = Symbol('theme')

// Provider
provide(ThemeKey, theme)

// Consumer
const theme = inject(ThemeKey)
```

---

## Computed and Watch Patterns

### Advanced Computed

```typescript
// Computed with setter
const fullName = computed({
  get: () => `${firstName.value} ${lastName.value}`,
  set: (newValue) => {
    const parts = newValue.split(' ')
    firstName.value = parts[0]
    lastName.value = parts[1] || ''
  }
})

// Computed with complex logic
const sortedFilteredItems = computed(() => {
  return items.value
    .filter(item => item.active)
    .sort((a, b) => a.name.localeCompare(b.name))
})

// Memoized expensive computation
import { computed, shallowRef } from 'vue'

const expensiveResult = computed(() => {
  // Expensive calculation
  return heavyComputation(largeDataset.value)
})
```

### Advanced Watch Patterns

```typescript
// Watch with immediate and deep
watch(
  () => form.value,
  (newForm, oldForm) => {
    console.log('Form changed:', newForm, oldForm)
  },
  { immediate: true, deep: true }
)

// Watch multiple sources
watch(
  [() => route.params.id, () => userStore.currentUser],
  ([id, user]) => {
    if (id && user) {
      loadData(id, user)
    }
  }
)

// WatchEffect - auto-tracks dependencies
watchEffect(() => {
  // Automatically re-runs when any reactive dependency changes
  console.log(`Count is ${count.value}, name is ${name.value}`)
})

// Watch with flush timing
watch(
  source,
  callback,
  {
    flush: 'pre' // 'pre' | 'post' | 'sync'
  }
)

// Stop watcher programmatically
const stop = watch(source, callback)
// Later...
stop()
```

---

## Refs and Template Refs

### Template Refs

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'

const inputRef = ref<HTMLInputElement | null>(null)
const componentRef = ref<InstanceType<typeof MyComponent> | null>(null)

onMounted(() => {
  // Access DOM element
  inputRef.value?.focus()

  // Access component instance
  componentRef.value?.someMethod()
})
</script>

<template>
  <input ref="inputRef" type="text" />
  <MyComponent ref="componentRef" />
</template>
```

### Multiple Template Refs

```vue
<script setup lang="ts">
const itemRefs = ref<HTMLElement[]>([])

const setItemRef = (el: HTMLElement | null, index: number) => {
  if (el) {
    itemRefs.value[index] = el
  }
}
</script>

<template>
  <div
    v-for="(item, index) in items"
    :key="item.id"
    :ref="el => setItemRef(el as HTMLElement, index)"
  >
    {{ item.name }}
  </div>
</template>
```

---

## Async Component Patterns

### Loading States

```typescript
const AsyncComponent = defineAsyncComponent({
  loader: () => import('./HeavyComponent.vue'),
  loadingComponent: LoadingSpinner,
  errorComponent: ErrorDisplay,
  delay: 200,
  timeout: 3000,
  onError(error, retry, fail, attempts) {
    if (attempts <= 3) {
      retry()
    } else {
      fail()
    }
  }
})
```

### Suspense

```vue
<template>
  <Suspense>
    <template #default>
      <AsyncComponent />
    </template>
    <template #fallback>
      <LoadingSpinner />
    </template>
  </Suspense>
</template>
```
