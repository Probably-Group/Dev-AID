# Vue 3 Composition API & Nuxt 3 Implementation Patterns

This document contains detailed implementation patterns for Vue 3 Composition API and Nuxt 3 server routes with security-first practices.

## 1. Secure Component Structure

```vue
<script setup lang="ts">
// ✅ Type-safe props with validation
interface Props {
  hudData: HUDDisplayData
  userId: string
}

const props = defineProps<Props>()

// ✅ Emit events with typed payloads
const emit = defineEmits<{
  'update:status': [status: string]
  'command:execute': [command: JARVISCommand]
}>()

// ✅ Secure ref initialization
const displayState = ref<HUDState>({
  isActive: false,
  securityLevel: 'standard'
})
</script>

<template>
  <!-- ✅ Use v-text for user content to prevent XSS -->
  <div class="hud-panel">
    <span v-text="props.hudData.title" />
  </div>
</template>
```

## 2. Input Sanitization Pattern

```typescript
// composables/useSanitize.ts
import DOMPurify from 'isomorphic-dompurify'

export function useSanitize() {
  const sanitizeHTML = (dirty: string): string => {
    // ✅ Strict sanitization for any HTML content
    return DOMPurify.sanitize(dirty, {
      ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'span'],
      ALLOWED_ATTR: ['class']
    })
  }

  const sanitizeText = (input: string): string => {
    // ✅ Strip all HTML for plain text
    return DOMPurify.sanitize(input, { ALLOWED_TAGS: [] })
  }

  return { sanitizeHTML, sanitizeText }
}
```

## 3. Secure API Route Pattern

```typescript
// server/api/jarvis/command.post.ts
import { z } from 'zod'

// ✅ Define strict schema for command validation
const commandSchema = z.object({
  action: z.enum(['status', 'control', 'query']),
  target: z.string().max(100).regex(/^[a-zA-Z0-9-_]+$/),
  parameters: z.record(z.string()).optional()
})

export default defineEventHandler(async (event) => {
  const body = await readBody(event)

  // ✅ Validate input against schema
  const result = commandSchema.safeParse(body)
  if (!result.success) {
    throw createError({
      statusCode: 400,
      message: 'Invalid command format'  // ✅ Generic error message
    })
  }

  // ✅ Process validated command
  const command = result.data

  // Never log sensitive data
  console.log(`Processing command: ${command.action}`)

  return { success: true, commandId: generateSecureId() }
})
```

## 4. Secure Environment Configuration

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  // ✅ Security headers
  routeRules: {
    '/**': {
      headers: {
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block'
      }
    }
  },

  // ✅ Runtime config - secrets stay server-side
  runtimeConfig: {
    apiSecret: process.env.API_SECRET,  // Server only
    public: {
      apiBase: '/api'  // Client accessible
    }
  },

  // ✅ Disable devtools in production
  devtools: { enabled: process.env.NODE_ENV === 'development' }
})
```

## 5. 3D HUD Component Integration

```vue
<script setup lang="ts">
// components/HUDDisplay.vue
import { TresCanvas } from '@tresjs/core'

const props = defineProps<{
  metrics: SystemMetrics
}>()

// ✅ Validate metrics before rendering
const validatedMetrics = computed(() => {
  return {
    cpu: Math.min(100, Math.max(0, props.metrics.cpu)),
    memory: Math.min(100, Math.max(0, props.metrics.memory)),
    status: sanitizeText(props.metrics.status)
  }
})
</script>

<template>
  <TresCanvas>
    <HUDMetricsDisplay :data="validatedMetrics" />
  </TresCanvas>
</template>
```

## 6. Authentication Middleware

```typescript
// middleware/auth.ts
export default defineNuxtRouteMiddleware((to) => {
  const { authenticated } = useAuthState()

  if (!authenticated.value && to.meta.requiresAuth) {
    return navigateTo('/login')
  }
})
```

## 7. State Management Composables

```typescript
// composables/useAuthState.ts
export function useAuthState() {
  const authenticated = useState<boolean>('auth:authenticated', () => false)
  const user = useState<User | null>('auth:user', () => null)

  const login = async (credentials: Credentials) => {
    const { data } = await $fetch('/api/auth/login', {
      method: 'POST',
      body: credentials
    })

    authenticated.value = true
    user.value = data.user
  }

  const logout = async () => {
    await $fetch('/api/auth/logout', { method: 'POST' })
    authenticated.value = false
    user.value = null
  }

  return {
    authenticated,
    user,
    login,
    logout
  }
}
```

## 8. Lazy Component Loading

```typescript
// ❌ BAD - All components loaded upfront
import HeavyChart from '@/components/HeavyChart.vue'

// ✅ GOOD - Load only when needed
const HeavyChart = defineAsyncComponent(() =>
  import('@/components/HeavyChart.vue')
)

// With loading state
const HeavyChart = defineAsyncComponent({
  loader: () => import('@/components/HeavyChart.vue'),
  loadingComponent: LoadingSpinner,
  delay: 200
})
```

## 9. Key Composables Reference

```typescript
// State management
const state = useState<T>('key', () => initialValue)

// Runtime config access
const config = useRuntimeConfig()

// Route navigation
const router = useRouter()
await navigateTo('/path')

// Fetch data
const { data, error } = await useFetch('/api/endpoint')

// Async data with server-side rendering
const { data } = await useAsyncData('key', () => fetchData())
```

## 10. Reactive Form Handling

```vue
<script setup lang="ts">
import { z } from 'zod'

const formSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8)
})

type FormData = z.infer<typeof formSchema>

const formData = ref<FormData>({
  email: '',
  password: ''
})

const errors = ref<Partial<Record<keyof FormData, string>>>({})
const isSubmitting = ref(false)

const handleSubmit = async () => {
  // Client-side validation
  const result = formSchema.safeParse(formData.value)

  if (!result.success) {
    errors.value = result.error.flatten().fieldErrors
    return
  }

  isSubmitting.value = true
  errors.value = {}

  try {
    await $fetch('/api/auth/register', {
      method: 'POST',
      body: result.data
    })
    navigateTo('/dashboard')
  } catch (err) {
    errors.value = { email: 'Registration failed' }
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <form @submit.prevent="handleSubmit">
    <input
      v-model="formData.email"
      type="email"
      :disabled="isSubmitting"
    />
    <span v-if="errors.email" v-text="errors.email" />

    <input
      v-model="formData.password"
      type="password"
      :disabled="isSubmitting"
    />
    <span v-if="errors.password" v-text="errors.password" />

    <button type="submit" :disabled="isSubmitting">
      {{ isSubmitting ? 'Submitting...' : 'Submit' }}
    </button>
  </form>
</template>
```
