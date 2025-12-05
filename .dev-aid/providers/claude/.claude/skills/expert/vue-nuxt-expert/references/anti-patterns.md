# Vue 3 & Nuxt 3 Anti-Patterns and Common Mistakes

This guide covers common mistakes and anti-patterns to avoid when building Vue 3 and Nuxt 3 applications.

---

## Mistake 1: Reactivity Loss with Destructuring

**Problem:**
```typescript
// ❌ WRONG: Loses reactivity
const userStore = useUserStore()
const { currentUser } = userStore // Not reactive!

watch(currentUser, () => {
  console.log('This will never trigger!')
})
```

**Solution:**
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

**Why it happens:** Destructuring extracts the plain value at that moment, breaking the reactive connection. `storeToRefs` converts store properties to refs while maintaining reactivity.

---

## Mistake 2: Memory Leaks from Event Listeners

**Problem:**
```typescript
// ❌ WRONG: Event listener not cleaned up
onMounted(() => {
  window.addEventListener('resize', handleResize)
})
// Component unmounts but listener persists!
```

**Solution:**
```typescript
// ✅ CORRECT: Clean up in onUnmounted
onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

// ✅ BETTER: Use VueUse composable
import { useEventListener } from '@vueuse/core'
useEventListener(window, 'resize', handleResize) // Auto cleanup!
```

**Why it happens:** Event listeners attached to global objects (window, document) persist even after the component is destroyed, causing memory leaks.

---

## Mistake 3: Incorrect useFetch Usage

**Problem:**
```typescript
// ❌ WRONG: useFetch in event handler
const handleClick = async () => {
  const { data } = await useFetch('/api/data') // Error! Not allowed in functions
}

// ❌ WRONG: Inside conditional
if (someCondition) {
  const { data } = await useFetch('/api/data') // Error! Must be top-level
}
```

**Solution:**
```typescript
// ✅ CORRECT: Use $fetch for programmatic calls
const handleClick = async () => {
  const data = await $fetch('/api/data') // Works in functions
}

// ✅ CORRECT: useFetch at component top-level
const { data, refresh } = await useFetch('/api/data', {
  immediate: false
})

const handleClick = () => {
  refresh() // Trigger refetch
}
```

**Why it happens:** `useFetch` is a composable that must be called at the top level during setup. For programmatic fetching, use `$fetch` instead.

---

## Mistake 4: Not Handling SSR/Client Differences

**Problem:**
```typescript
// ❌ WRONG: Accessing browser APIs during SSR
const windowWidth = ref(window.innerWidth) // Error! window undefined on server

onMounted(() => {
  localStorage.setItem('key', 'value') // Error! localStorage undefined on server
})
```

**Solution:**
```typescript
// ✅ CORRECT: Check environment
const windowWidth = ref(0)

onMounted(() => {
  if (process.client) {
    windowWidth.value = window.innerWidth
  }
})

// ✅ BETTER: Use VueUse with SSR safety
import { useWindowSize, useLocalStorage } from '@vueuse/core'

const { width } = useWindowSize() // SSR-safe
const stored = useLocalStorage('key', 'default') // SSR-safe
```

**Why it happens:** Browser APIs like `window`, `document`, and `localStorage` don't exist on the server during SSR.

---

## Mistake 5: Inefficient Watchers

**Problem:**
```typescript
// ❌ WRONG: Watching entire object (triggers on any property change)
const form = reactive({
  name: '',
  email: '',
  phone: '',
  address: ''
})

watch(form, () => {
  console.log('Triggers for ANY field change!')
})
```

**Solution:**
```typescript
// ✅ CORRECT: Watch specific properties
watch(() => form.email, (newEmail) => {
  validateEmail(newEmail)
})

// ✅ CORRECT: Watch multiple specific properties
watch([() => form.email, () => form.phone], ([email, phone]) => {
  validateContactInfo(email, phone)
})

// ✅ CORRECT: Deep watch with debounce when needed
import { useDebounceFn } from '@vueuse/core'

const debouncedSave = useDebounceFn(() => {
  saveFormDraft(form)
}, 500)

watch(form, () => {
  debouncedSave()
}, { deep: true })
```

**Why it happens:** Watching an entire reactive object with `deep: true` triggers on every property change, causing unnecessary re-runs.

---

## Mistake 6: Mutating Props Directly

**Problem:**
```vue
<script setup lang="ts">
const props = defineProps<{ user: User }>()

// ❌ WRONG: Mutating prop directly
const updateUser = () => {
  props.user.name = 'New Name' // Error! Props are readonly
}
</script>
```

**Solution:**
```vue
<script setup lang="ts">
const props = defineProps<{ user: User }>()
const emit = defineEmits<{
  update: [user: User]
}>()

// ✅ CORRECT: Emit event to parent
const updateUser = () => {
  emit('update', { ...props.user, name: 'New Name' })
}

// ✅ ALTERNATIVE: Use v-model
const props = defineProps<{ modelValue: User }>()
const emit = defineEmits<{
  'update:modelValue': [user: User]
}>()

const localUser = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})
</script>
```

**Why it happens:** Vue enforces one-way data flow. Props should never be mutated directly in child components.

---

## Mistake 7: Using Methods Instead of Computed

**Problem:**
```vue
<script setup lang="ts">
const items = ref([...])

// ❌ WRONG: Method called on every render
const getFilteredItems = () => {
  console.log('Filtering...') // Called many times
  return items.value.filter(item => item.active)
}
</script>

<template>
  <div v-for="item in getFilteredItems()" :key="item.id">
    {{ item.name }}
  </div>
</template>
```

**Solution:**
```vue
<script setup lang="ts">
const items = ref([...])

// ✅ CORRECT: Computed property caches result
const filteredItems = computed(() => {
  console.log('Filtering...') // Only called when items change
  return items.value.filter(item => item.active)
})
</script>

<template>
  <div v-for="item in filteredItems" :key="item.id">
    {{ item.name }}
  </div>
</template>
```

**Why it happens:** Methods are called every time the template re-renders, while computed properties are cached and only recalculate when dependencies change.

---

## Mistake 8: Forgetting Keys in v-for

**Problem:**
```vue
<template>
  <!-- ❌ WRONG: No key -->
  <div v-for="item in items">
    {{ item.name }}
  </div>

  <!-- ❌ WRONG: Using index as key (problematic for dynamic lists) -->
  <div v-for="(item, index) in items" :key="index">
    {{ item.name }}
  </div>
</template>
```

**Solution:**
```vue
<template>
  <!-- ✅ CORRECT: Unique, stable key -->
  <div v-for="item in items" :key="item.id">
    {{ item.name }}
  </div>

  <!-- ✅ CORRECT: Composite key if needed -->
  <div v-for="item in items" :key="`${item.category}-${item.id}`">
    {{ item.name }}
  </div>
</template>
```

**Why it happens:** Without keys or with index keys, Vue can't efficiently track which elements changed, leading to rendering bugs and performance issues.

---

## Mistake 9: Using v-if with v-for

**Problem:**
```vue
<template>
  <!-- ❌ WRONG: v-if and v-for on same element -->
  <div v-for="item in items" v-if="item.active" :key="item.id">
    {{ item.name }}
  </div>
</template>
```

**Solution:**
```vue
<script setup lang="ts">
// ✅ CORRECT: Use computed to filter first
const activeItems = computed(() => items.value.filter(item => item.active))
</script>

<template>
  <div v-for="item in activeItems" :key="item.id">
    {{ item.name }}
  </div>
</template>
```

**Why it happens:** When `v-if` and `v-for` are on the same element, `v-if` has higher priority in Vue 3, which can cause unexpected behavior. Always filter in computed first.

---

## Mistake 10: Not Cleaning Up Async Operations

**Problem:**
```vue
<script setup lang="ts">
let timer: NodeJS.Timeout

onMounted(() => {
  // ❌ WRONG: Timer not cleaned up
  timer = setInterval(() => {
    fetchData()
  }, 1000)
})
// Component unmounts but timer keeps running!
</script>
```

**Solution:**
```vue
<script setup lang="ts">
let timer: NodeJS.Timeout

onMounted(() => {
  timer = setInterval(() => {
    fetchData()
  }, 1000)
})

// ✅ CORRECT: Clean up timer
onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})

// ✅ BETTER: Use VueUse
import { useIntervalFn } from '@vueuse/core'
const { pause, resume } = useIntervalFn(() => {
  fetchData()
}, 1000)

// Auto pauses on unmount
</script>
```

**Why it happens:** Timers, intervals, and pending async operations continue running even after component unmount, causing memory leaks.

---

## Mistake 11: Incorrect Async/Await in setup

**Problem:**
```vue
<script setup lang="ts">
// ❌ WRONG: Can cause hydration mismatch
const data = ref(null)
const response = await fetch('/api/data')
data.value = await response.json()
</script>
```

**Solution:**
```vue
<script setup lang="ts">
// ✅ CORRECT: Use Nuxt data fetching
const { data } = await useFetch('/api/data')

// ✅ CORRECT: Or handle SSR properly
const data = ref(null)

if (process.server) {
  const response = await $fetch('/api/data')
  data.value = response
} else {
  onMounted(async () => {
    const response = await $fetch('/api/data')
    data.value = response
  })
}
</script>
```

**Why it happens:** Using raw `fetch` or `await` in `<script setup>` can cause SSR/hydration issues. Always use Nuxt's data fetching composables.

---

## Mistake 12: Overusing Reactive

**Problem:**
```typescript
// ❌ WRONG: Reactive for primitive values
const count = reactive({ value: 0 })

// ❌ WRONG: Reactive for arrays (ref is simpler)
const items = reactive([1, 2, 3])
```

**Solution:**
```typescript
// ✅ CORRECT: Use ref for primitives
const count = ref(0)

// ✅ CORRECT: Use ref for arrays
const items = ref([1, 2, 3])

// ✅ CORRECT: Use reactive for objects
const user = reactive({
  name: '',
  email: '',
  age: 0
})
```

**Why it happens:** `reactive` only works with objects. For primitives and arrays, `ref` is simpler and more idiomatic.

---

## Mistake 13: Not Using TypeScript Generics Properly

**Problem:**
```typescript
// ❌ WRONG: No type safety
const data = ref(null)
const items = ref([])
```

**Solution:**
```typescript
// ✅ CORRECT: Type the refs
const data = ref<User | null>(null)
const items = ref<Item[]>([])

// ✅ CORRECT: Type computed
const fullName = computed<string>(() => {
  return `${firstName.value} ${lastName.value}`
})

// ✅ CORRECT: Type composables
function useData<T>(url: string) {
  const data = ref<T | null>(null)
  // ...
  return { data }
}
```

**Why it happens:** Without proper typing, you lose type safety and IntelliSense support.

---

## Mistake 14: Exposing Secrets in Client Code

**Problem:**
```typescript
// ❌ WRONG: API key in client code
const API_KEY = 'sk_live_123456789'

const fetchData = async () => {
  const response = await fetch('https://api.example.com/data', {
    headers: {
      'Authorization': `Bearer ${API_KEY}`
    }
  })
}
```

**Solution:**
```typescript
// ✅ CORRECT: Use server API route
// server/api/data.get.ts
export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig(event)
  const API_KEY = config.apiSecret // Server-only

  const data = await $fetch('https://api.example.com/data', {
    headers: {
      'Authorization': `Bearer ${API_KEY}`
    }
  })

  return data
})

// Client code
const { data } = await useFetch('/api/data')
```

**Why it happens:** Anything in client code is visible to users. Always keep secrets on the server.

---

## Mistake 15: Not Using Proper Error Boundaries

**Problem:**
```vue
<script setup lang="ts">
// ❌ WRONG: Unhandled errors crash the app
const { data } = await useFetch('/api/data')
</script>
```

**Solution:**
```vue
<script setup lang="ts">
// ✅ CORRECT: Handle errors
const { data, error } = await useFetch('/api/data')

if (error.value) {
  console.error('Failed to fetch data:', error.value)
  // Show error UI or redirect
}

// ✅ CORRECT: Global error handler
// app.vue
const error = useError()

// ✅ CORRECT: Try-catch for unexpected errors
try {
  const result = await dangerousOperation()
} catch (err) {
  console.error('Operation failed:', err)
  // Handle error
}
</script>
```

**Why it happens:** Unhandled errors can crash the application or leave it in a broken state.

---

## Mistake 16: Using v-html with Unsanitized Input

**Problem:**
```vue
<script setup lang="ts">
const userInput = ref('<script>alert("XSS")</script>')
</script>

<template>
  <!-- ❌ WRONG: XSS vulnerability -->
  <div v-html="userInput"></div>
</template>
```

**Solution:**
```vue
<script setup lang="ts">
import DOMPurify from 'isomorphic-dompurify'

const userInput = ref('<script>alert("XSS")</script>')
const sanitized = computed(() => DOMPurify.sanitize(userInput.value))
</script>

<template>
  <!-- ✅ CORRECT: Sanitized HTML -->
  <div v-html="sanitized"></div>

  <!-- ✅ BETTER: Use text interpolation (auto-escaped) -->
  <div>{{ userInput }}</div>
</template>
```

**Why it happens:** `v-html` renders raw HTML without escaping, making it vulnerable to XSS attacks if used with user input.

---

## Mistake 17: Ignoring Hydration Mismatches

**Problem:**
```vue
<script setup lang="ts">
// ❌ WRONG: Different content on server vs client
const timestamp = new Date().toISOString()
</script>

<template>
  <div>{{ timestamp }}</div>
</template>
```

**Solution:**
```vue
<script setup lang="ts">
// ✅ CORRECT: Use ClientOnly for client-specific content
const timestamp = ref('')

onMounted(() => {
  timestamp.value = new Date().toISOString()
})
</script>

<template>
  <ClientOnly>
    <div>{{ timestamp }}</div>
    <template #fallback>
      <div>Loading...</div>
    </template>
  </ClientOnly>
</template>
```

**Why it happens:** Server and client rendering different HTML causes hydration mismatches, leading to console warnings and potential bugs.

---

## Mistake 18: Not Optimizing Bundle Size

**Problem:**
```typescript
// ❌ WRONG: Importing entire library
import _ from 'lodash'
import moment from 'moment'

// ❌ WRONG: Not code splitting
import HugeComponent from './HugeComponent.vue'
```

**Solution:**
```typescript
// ✅ CORRECT: Import only what you need
import { debounce, throttle } from 'lodash-es'
import { format } from 'date-fns'

// ✅ CORRECT: Lazy load components
const HugeComponent = defineAsyncComponent(() =>
  import('./HugeComponent.vue')
)
```

**Why it happens:** Large bundles slow down initial load time. Always optimize imports and use code splitting.

---

## Summary Checklist

Before deploying, check for these common mistakes:

- [ ] No destructuring of store state without `storeToRefs`
- [ ] All event listeners and timers cleaned up
- [ ] `useFetch` only at top level, `$fetch` for programmatic calls
- [ ] Browser APIs checked with `process.client`
- [ ] Watchers optimized (not watching entire objects unnecessarily)
- [ ] Props never mutated directly
- [ ] Computed used instead of methods for derived state
- [ ] Unique keys on all `v-for` loops
- [ ] No `v-if` with `v-for` on same element
- [ ] All async operations cleaned up in `onUnmounted`
- [ ] Proper TypeScript typing on refs and composables
- [ ] No secrets in client code
- [ ] Error handling implemented
- [ ] No `v-html` with unsanitized user input
- [ ] Hydration mismatches handled with `<ClientOnly>`
- [ ] Bundle size optimized
