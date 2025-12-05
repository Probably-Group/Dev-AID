# Nuxt 3 Patterns and Best Practices

This guide covers Nuxt 3-specific patterns for routing, middleware, server API routes, and SSR.

---

## Pattern 1: Nuxt 3 Middleware & Route Guards

**Implement authentication and authorization middleware:**

```typescript
// middleware/auth.global.ts
export default defineNuxtRouteMiddleware((to, from) => {
  const userStore = useUserStore()
  const publicRoutes = ['/login', '/register', '/forgot-password']

  // Allow public routes
  if (publicRoutes.includes(to.path)) {
    return
  }

  // Redirect to login if not authenticated
  if (!userStore.isAuthenticated) {
    return navigateTo('/login', { redirectCode: 401 })
  }

  // Check role-based access
  if (to.meta.requiresAdmin && !userStore.hasRole('admin')) {
    return abortNavigation({
      statusCode: 403,
      message: 'Access denied'
    })
  }
})
```

**Page with metadata:**
```vue
<script setup lang="ts">
definePageMeta({
  requiresAdmin: true,
  layout: 'admin'
})

const users = await useFetch('/api/admin/users')
</script>
```

---

## Pattern 2: Server API Routes with Validation

**Create type-safe API endpoints with input validation:**

```typescript
// server/api/users/[id].post.ts
import { z } from 'zod'
import { createError } from 'h3'

const updateUserSchema = z.object({
  name: z.string().min(2).max(100),
  email: z.string().email(),
  age: z.number().int().min(18).max(120).optional()
})

export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')

  if (!id) {
    throw createError({
      statusCode: 400,
      message: 'User ID is required'
    })
  }

  // Validate request body
  const body = await readBody(event)
  const result = updateUserSchema.safeParse(body)

  if (!result.success) {
    throw createError({
      statusCode: 400,
      message: 'Invalid request data',
      data: result.error.format()
    })
  }

  // Check authentication
  const session = await requireUserSession(event)

  // Check authorization (users can only update themselves unless admin)
  if (session.user.id !== id && !session.user.roles.includes('admin')) {
    throw createError({
      statusCode: 403,
      message: 'Not authorized to update this user'
    })
  }

  // Update user in database
  const updatedUser = await db.users.update(id, result.data)

  return updatedUser
})
```

---

## Pattern 3: SSR-Safe Data Fetching

**Handle data fetching correctly for SSR/SSG:**

```vue
<script setup lang="ts">
// ✅ CORRECT: Use Nuxt data fetching composables
// These work on both server and client, with automatic hydration

// Basic fetch
const { data: posts } = await useFetch('/api/posts', {
  key: 'posts-list',
  transform: (data) => data.posts,
  getCachedData: (key) => useNuxtApp().static.data[key]
})

// With params
const route = useRoute()
const { data: post } = await useFetch(`/api/posts/${route.params.id}`, {
  key: `post-${route.params.id}`,
  watch: [() => route.params.id] // Refetch when ID changes
})

// With lazy loading (client-side only initially)
const { data: comments, pending } = await useLazyFetch(`/api/posts/${route.params.id}/comments`)

// Using useAsyncData for custom async operations
const { data: userData, refresh } = await useAsyncData(
  'user-profile',
  async () => {
    const [profile, settings] = await Promise.all([
      $fetch('/api/user/profile'),
      $fetch('/api/user/settings')
    ])
    return { profile, settings }
  },
  {
    server: true,  // Fetch on server
    lazy: false,   // Wait for data before rendering
    default: () => ({ profile: null, settings: null })
  }
)

// ❌ WRONG: Direct fetch calls will execute twice (server + client)
// const response = await fetch('/api/posts') // Don't do this!
</script>

<template>
  <div>
    <article v-if="post">
      <h1>{{ post.title }}</h1>
      <p>{{ post.content }}</p>
    </article>

    <section v-if="!pending">
      <h2>Comments ({{ comments?.length || 0 }})</h2>
      <div v-for="comment in comments" :key="comment.id">
        {{ comment.text }}
      </div>
    </section>
    <div v-else>Loading comments...</div>
  </div>
</template>
```

---

## Pattern 4: Nuxt Plugins

**Create plugins for global functionality:**

```typescript
// plugins/api.ts
export default defineNuxtPlugin(() => {
  const api = $fetch.create({
    baseURL: '/api',
    onRequest({ options }) {
      // Add auth token
      const token = useCookie('auth_token')
      if (token.value) {
        options.headers = {
          ...options.headers,
          Authorization: `Bearer ${token.value}`
        }
      }
    },
    onResponseError({ response }) {
      if (response.status === 401) {
        // Redirect to login
        navigateTo('/login')
      }
    }
  })

  return {
    provide: {
      api
    }
  }
})
```

**Usage:**
```vue
<script setup lang="ts">
const { $api } = useNuxtApp()

const { data } = await useAsyncData('users', () =>
  $api<User[]>('/users')
)
</script>
```

---

## Pattern 5: Nuxt Layouts

**Dynamic layouts with transitions:**

```vue
<!-- layouts/default.vue -->
<template>
  <div>
    <AppHeader />
    <main>
      <slot />
    </main>
    <AppFooter />
  </div>
</template>
```

```vue
<!-- layouts/admin.vue -->
<template>
  <div class="admin-layout">
    <AdminSidebar />
    <main>
      <slot />
    </main>
  </div>
</template>
```

**Using layouts in pages:**
```vue
<script setup lang="ts">
// Static layout
definePageMeta({
  layout: 'admin'
})

// Dynamic layout
const layout = computed(() =>
  isAdmin.value ? 'admin' : 'default'
)

setPageLayout(layout.value)
</script>
```

---

## Pattern 6: Nuxt Composables

**Auto-imported composables:**

```typescript
// composables/useAuth.ts
export function useAuth() {
  const user = useState<User | null>('user', () => null)
  const isAuthenticated = computed(() => !!user.value)

  const login = async (email: string, password: string) => {
    const response = await $fetch('/api/auth/login', {
      method: 'POST',
      body: { email, password }
    })
    user.value = response.user
  }

  const logout = async () => {
    await $fetch('/api/auth/logout', { method: 'POST' })
    user.value = null
  }

  return {
    user,
    isAuthenticated,
    login,
    logout
  }
}
```

**Usage (auto-imported):**
```vue
<script setup lang="ts">
const { user, login, logout } = useAuth()
</script>
```

---

## Pattern 7: Route Rules and Caching

**Configure rendering strategies per route:**

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  routeRules: {
    // Static pages (pre-rendered at build time)
    '/': { prerender: true },
    '/about': { prerender: true },

    // SSR with caching (Stale-While-Revalidate)
    '/blog/**': { swr: 3600 },

    // Client-side only (SPA mode)
    '/dashboard/**': { ssr: false },

    // API routes with caching
    '/api/**': {
      cache: {
        maxAge: 60,
        staleMaxAge: 300
      }
    },

    // Redirect rules
    '/old-path': { redirect: '/new-path' },

    // ISR (Incremental Static Regeneration)
    '/products/**': {
      swr: true,
      isr: {
        expiration: 3600
      }
    }
  }
})
```

---

## Pattern 8: Server Middleware

**Global server middleware:**

```typescript
// server/middleware/log.ts
export default defineEventHandler((event) => {
  console.log(`${event.method} ${event.path}`)
})
```

**CORS middleware:**

```typescript
// server/middleware/cors.ts
export default defineEventHandler((event) => {
  setResponseHeaders(event, {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
  })

  if (event.method === 'OPTIONS') {
    event.node.res.statusCode = 204
    event.node.res.end()
  }
})
```

---

## Pattern 9: Nuxt Modules

**Create custom modules:**

```typescript
// modules/my-module/index.ts
import { defineNuxtModule, addPlugin, createResolver } from '@nuxt/kit'

export default defineNuxtModule({
  meta: {
    name: 'my-module',
    configKey: 'myModule'
  },
  defaults: {
    enabled: true
  },
  setup(options, nuxt) {
    if (!options.enabled) return

    const resolver = createResolver(import.meta.url)

    // Add plugin
    addPlugin(resolver.resolve('./runtime/plugin'))

    // Add composables
    nuxt.hook('imports:dirs', (dirs) => {
      dirs.push(resolver.resolve('./runtime/composables'))
    })
  }
})
```

---

## Pattern 10: Error Handling

**Global error page:**

```vue
<!-- error.vue -->
<script setup lang="ts">
interface Props {
  error: {
    statusCode: number
    statusMessage: string
    message: string
  }
}

const props = defineProps<Props>()

const handleClear = () => clearError({ redirect: '/' })
</script>

<template>
  <div class="error-page">
    <h1>{{ error.statusCode }}</h1>
    <p>{{ error.statusMessage }}</p>
    <button @click="handleClear">Go Home</button>
  </div>
</template>
```

**Error handling in components:**

```vue
<script setup lang="ts">
const { data, error } = await useFetch('/api/data')

if (error.value) {
  throw createError({
    statusCode: 404,
    statusMessage: 'Data not found',
    fatal: true
  })
}
</script>
```

---

## Pattern 11: State Management with useState

**Shared state across components:**

```typescript
// composables/useCounter.ts
export function useCounter() {
  // Shared state (SSR-safe)
  const count = useState('counter', () => 0)

  const increment = () => count.value++
  const decrement = () => count.value--

  return { count, increment, decrement }
}
```

**Usage:**
```vue
<!-- components/Counter.vue -->
<script setup lang="ts">
const { count, increment } = useCounter()
</script>

<template>
  <div>
    <p>Count: {{ count }}</p>
    <button @click="increment">Increment</button>
  </div>
</template>
```

---

## Pattern 12: Nuxt Image Optimization

**Optimized image loading:**

```vue
<template>
  <!-- Automatic format optimization (WebP, AVIF) -->
  <NuxtImg
    src="/images/hero.jpg"
    width="800"
    height="600"
    format="webp"
    quality="80"
    loading="lazy"
    alt="Hero image"
  />

  <!-- Responsive images -->
  <NuxtImg
    src="/images/hero.jpg"
    sizes="sm:100vw md:50vw lg:400px"
    densities="x1 x2"
    alt="Hero image"
  />

  <!-- Picture element with multiple formats -->
  <NuxtPicture
    src="/images/hero.jpg"
    :img-attrs="{ alt: 'Hero image' }"
  />
</template>
```

---

## Pattern 13: Runtime Config

**Environment-specific configuration:**

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  runtimeConfig: {
    // Server-side only (private)
    apiSecret: process.env.API_SECRET,
    dbUrl: process.env.DATABASE_URL,

    // Public (exposed to client)
    public: {
      apiBase: process.env.API_BASE || '/api',
      environment: process.env.NODE_ENV
    }
  }
})
```

**Usage:**

```vue
<script setup lang="ts">
// Client-side
const config = useRuntimeConfig()
console.log(config.public.apiBase)
</script>
```

```typescript
// Server-side
export default defineEventHandler((event) => {
  const config = useRuntimeConfig(event)
  const secret = config.apiSecret // Only available on server
  const apiBase = config.public.apiBase
})
```

---

## Pattern 14: Nitro Server Utilities

**Storage layer:**

```typescript
// server/api/cache/[key].get.ts
export default defineEventHandler(async (event) => {
  const key = getRouterParam(event, 'key')
  const storage = useStorage()

  const value = await storage.getItem(`cache:${key}`)
  return { value }
})
```

**KV storage:**

```typescript
// server/api/cache/[key].post.ts
export default defineEventHandler(async (event) => {
  const key = getRouterParam(event, 'key')
  const body = await readBody(event)
  const storage = useStorage()

  await storage.setItem(`cache:${key}`, body.value, {
    ttl: 3600 // 1 hour
  })

  return { success: true }
})
```

---

## Pattern 15: Head Management

**SEO and meta tags:**

```vue
<script setup lang="ts">
// Page-level meta
useHead({
  title: 'My Page Title',
  meta: [
    { name: 'description', content: 'Page description' },
    { property: 'og:title', content: 'OG Title' },
    { property: 'og:description', content: 'OG Description' }
  ],
  link: [
    { rel: 'canonical', href: 'https://example.com/page' }
  ]
})

// Dynamic meta
const title = ref('Initial Title')
useHead({
  title: () => title.value
})

// SEO meta with useSeoMeta
useSeoMeta({
  title: 'My Page',
  ogTitle: 'My Page',
  description: 'Page description',
  ogDescription: 'OG Description',
  ogImage: 'https://example.com/image.jpg',
  twitterCard: 'summary_large_image'
})
</script>
```

---

## Pattern 16: Islands Architecture

**Component islands for partial hydration:**

```vue
<!-- pages/index.vue -->
<template>
  <div>
    <!-- Static content (no hydration) -->
    <StaticContent />

    <!-- Interactive island (hydrated) -->
    <NuxtIsland name="InteractiveCounter" />

    <!-- Lazy island (hydrated on interaction) -->
    <NuxtIsland name="Comments" :lazy="true" />
  </div>
</template>
```

**Island component:**

```vue
<!-- components/islands/InteractiveCounter.vue -->
<script setup lang="ts">
const count = ref(0)
</script>

<template>
  <div>
    <p>Count: {{ count }}</p>
    <button @click="count++">Increment</button>
  </div>
</template>
```

---

## Pattern 17: Auto-imports Configuration

**Configure auto-imports:**

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  imports: {
    dirs: [
      // Additional composables directories
      'composables/**',
      'utils/**'
    ],
    presets: [
      {
        from: 'vue-i18n',
        imports: ['useI18n']
      }
    ]
  },

  components: {
    dirs: [
      {
        path: '~/components/base',
        prefix: 'Base'
      },
      {
        path: '~/components/ui',
        prefix: 'Ui'
      }
    ]
  }
})
```
