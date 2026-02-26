#!/usr/bin/env bash
# Preset: Vue 3 + Nuxt 4

preset_name="vue-nuxt"
preset_description="Vue 3.5+ Composition API with Nuxt 4, TypeScript, Pinia, and SSR/hybrid rendering"

# Rules files: newline-delimited "filename|description" pairs
RULES_FILES="components.md|Vue 3 Composition API, script setup, defineProps/defineEmits/defineModel, composables, provide/inject
routing.md|Nuxt file-based routing, useFetch/useAsyncData, server routes, middleware, definePageMeta
cross-service.md|Pinia stores, runtime config, error handling with createError, Nitro server engine"

# Technology stack entries
TECH_STACK="| Frontend | Vue 3.5+, Nuxt 4, TypeScript 5+ |
| State Management | Pinia |
| Styling | *Tailwind CSS / UnoCSS / Nuxt UI* |
| Testing | Vitest, @vue/test-utils, Playwright |
| Linting | ESLint (with @nuxt/eslint-config), Prettier |
| Server Engine | Nitro |
| Package Manager | *pnpm / npm / bun* |"

# Context loading table entries
CONTEXT_LOADING_TABLE="| **New component** | \`.claude/rules/components.md\`, \`components/\` |
| **New page / route** | \`.claude/rules/routing.md\`, \`pages/\`, \`server/api/\` |
| **State management** | \`.claude/rules/cross-service.md\`, \`stores/\` |
| **Server route / API** | \`.claude/rules/routing.md\` (Server Routes), \`server/api/\` |
| **Debugging** | \`.claude/rules/troubleshooting.md\` |
| **Architecture decisions** | \`docs/decisions/index.md\` |
| **Composables** | \`.claude/rules/components.md\` (Composables), \`composables/\` |"

# Context groups
CONTEXT_GROUPS='### `components`
Read: `.claude/rules/components.md`, `components/`, `composables/`

### `routing`
Read: `.claude/rules/routing.md`, `pages/`, `server/api/`, `middleware/`

### `state`
Read: `.claude/rules/cross-service.md`, `stores/`

### `config`
Read: `nuxt.config.ts`, `tsconfig.json`, `package.json`, `app.config.ts`

### `debug`
Read: `.claude/rules/troubleshooting.md`'

# Development workflow
WORKFLOW='```bash
# Setup
pnpm install  # or: npm install / bun install

# Run dev server (SSR enabled)
pnpm dev  # http://localhost:3000

# Build for production
pnpm build

# Preview production build
pnpm preview

# Run tests
pnpm test          # Vitest unit tests
pnpm test:e2e      # Playwright E2E tests

# Lint & format
pnpm lint --fix    # ESLint with auto-fix
pnpm format        # Prettier

# Type check
pnpm typecheck     # nuxi typecheck (vue-tsc)

# Nuxt utilities
npx nuxi cleanup   # Clear .nuxt, .output, node_modules/.cache
npx nuxi analyze   # Bundle analysis
```

### Dev Tools

- **Nuxt DevTools:** Automatically available in dev mode
- **Vue DevTools:** Browser extension for component and state inspection'

# Project overview
PROJECT_OVERVIEW="Nuxt 4 application with Vue 3 Composition API, server-side rendering, and Pinia state management."

# Workspace structure
WORKSPACE_STRUCTURE='{{PROJECT_NAME}}/
├── CLAUDE.md
├── .claude/
│   ├── rules/
│   │   ├── components.md
│   │   ├── routing.md
│   │   ├── cross-service.md
│   │   └── troubleshooting.md
│   ├── hooks/
│   │   └── lint-on-edit.sh
│   ├── memory/
│   │   ├── MEMORY.md
│   │   ├── component-patterns.md
│   │   ├── routing-gotchas.md
│   │   └── debugging.md
│   └── commands/
│       ├── review.md
│       ├── test.md
│       ├── plan.md
│       ├── smoke.md
│       ├── lint.md
│       └── typecheck.md
├── app.vue
├── nuxt.config.ts
├── app.config.ts
├── pages/
├── components/
├── composables/
├── stores/
├── server/
│   ├── api/
│   ├── middleware/
│   └── utils/
├── middleware/
├── layouts/
├── plugins/
├── public/
├── assets/
├── tests/
├── docs/
│   ├── plans/
│   │   └── .plan-template.md
│   └── decisions/
│       ├── index.md
│       └── adr-template.md
├── scripts/
│   └── smoke-nuxt.sh
├── package.json
└── tsconfig.json'

# Smoke test scripts: "filename|title|checks_variable_name"
SMOKE_SCRIPTS="smoke-nuxt.sh|Nuxt Application Health Checks|SMOKE_NUXT_CHECKS"

# shellcheck disable=SC2034
SMOKE_NUXT_CHECKS='section "Application"

if [[ -f "nuxt.config.ts" ]]; then
  pass "nuxt.config.ts exists"
else
  fail "nuxt.config.ts not found"
fi

if [[ -f "app.vue" ]] || [[ -d "pages" ]]; then
  pass "App entry point exists (app.vue or pages/)"
else
  fail "No app.vue or pages/ directory found"
fi

if [[ -f "package.json" ]]; then
  pass "package.json exists"
else
  fail "package.json not found"
fi

section "Dependencies"

if [[ -d "node_modules" ]]; then
  pass "node_modules exists"
else
  fail "node_modules missing — run pnpm install"
fi

if [[ -d "node_modules/nuxt" ]]; then
  pass "nuxt is installed"
else
  fail "nuxt package not found in node_modules"
fi

section "Type Checking"

if npx nuxi typecheck 2>/dev/null; then
  pass "TypeScript compiles without errors (vue-tsc)"
else
  warn "TypeScript compilation errors found — run pnpm typecheck"
fi

section "Build"

if npx nuxt build 2>/dev/null; then
  pass "Nuxt build succeeds"
else
  warn "Nuxt build has errors"
fi

section "Linting"

if npx eslint --quiet . 2>/dev/null; then
  pass "ESLint passes"
else
  warn "ESLint has findings"
fi

section "Tests"

if npx vitest --run --reporter=silent 2>/dev/null; then
  pass "Unit tests pass"
else
  warn "Unit tests failing or not found"
fi'

# Troubleshooting sections
TROUBLESHOOTING_SECTIONS='## 1. Hydration / SSR

### Symptom: `Hydration node mismatch` or `Hydration text content mismatch` in console

**Diagnosis:** Server-rendered HTML differs from client output. Causes: browser-only
APIs during SSR (`window`, `localStorage`), or rendering based on client-only values.

**Fix:**
```vue
<script setup lang="ts">
import { onMounted, ref } from "vue"
const windowWidth = ref(0)
onMounted(() => { windowWidth.value = window.innerWidth })
</script>
<template>
  <ClientOnly>
    <BrowserOnlyComponent />
    <template #fallback><div>Loading...</div></template>
  </ClientOnly>
</template>
```

---

### Symptom: `500 - [nuxt] instance unavailable` on page load

**Diagnosis:** A composable called outside setup context — after `await` or in `setTimeout`.

**Fix:**
```typescript
// BAD — composable after await loses context
const data = await someAsyncOperation()
const config = useRuntimeConfig() // ERROR

// GOOD — call composables before any await
const config = useRuntimeConfig()
const data = await someAsyncOperation()
```

---

## 2. Data Fetching

### Symptom: Data refetch not updating the UI after `navigateTo`

**Diagnosis:** `useFetch`/`useAsyncData` cache responses by key. Same route with different
params serves stale data if the key does not include the changing parameter.

**Fix:**
```typescript
const route = useRoute()
const { data } = await useFetch(
  () => `/api/items/${route.params.id}`,
  { watch: [() => route.params.id] }
)
```

---

## 3. TypeScript / Auto-imports

### Symptom: `Cannot find name` errors in IDE but the app runs fine

**Diagnosis:** Nuxt auto-imports not picked up by TypeScript. `.nuxt/tsconfig.json` stale.

**Fix:**
```bash
npx nuxi prepare        # Regenerate types
npx nuxi cleanup        # If above fails, clean first
# Ensure tsconfig.json: { "extends": "./.nuxt/tsconfig.json" }
```

---

## 4. Build / Deployment

### Symptom: `Cannot find module` errors after `nuxt build` in production

**Diagnosis:** Dependency in `devDependencies` instead of `dependencies`, or module
not registered in `nuxt.config.ts`.

**Fix:**
```bash
pnpm add <package-name>  # Move to dependencies
# Ensure nuxt.config.ts modules: ["@pinia/nuxt", "@nuxt/eslint"]
```

---

*Add entries as you encounter and solve issues. Use the Symptom -> Diagnosis -> Fix format.*'

# Memory topics: "filename|description" pairs
MEMORY_TOPICS="component-patterns.md|Component patterns, composable conventions, prop/emit signatures
routing-gotchas.md|Routing issues, data fetching edge cases, middleware patterns
debugging.md|Common errors encountered and their solutions"

# Slash commands to scaffold
COMMANDS="review.md
test.md
plan.md
smoke.md
lint.md
typecheck.md"

# --- Substantive Rules Content ---

# shellcheck disable=SC2034
RULES_CONTENT_COMPONENTS='# Vue 3 Component Patterns

> **When to use:** Building or modifying components, writing composables, props/emits/slots.
>
> **Read first for:** Any component work, composable patterns, provide/inject, v-model.

## Script Setup (Mandatory)

All components use `<script setup lang="ts">`. Never use the Options API.

```vue
<script setup lang="ts">
import { ref, computed, watch } from "vue"

const props = withDefaults(defineProps<{
  title: string
  count?: number
  variant?: "primary" | "secondary"
}>(), {
  count: 0,
  variant: "primary",
})

const emit = defineEmits<{
  update: [value: string]
  delete: [id: string]
}>()

const isOpen = ref(false)
const doubledCount = computed(() => props.count * 2)

watch(() => props.count, (newVal) => {
  console.log("Count changed:", newVal)
})
</script>
```

## defineModel (Two-way Binding)

Use `defineModel` for `v-model` bindings instead of prop + emit pairs:

```vue
<script setup lang="ts">
const modelValue = defineModel<string>()             // v-model
const title = defineModel<string>("title")            // v-model:title
const count = defineModel<number>("count", { default: 0 })
</script>
<!-- Parent: <MyInput v-model="query" v-model:title="pageTitle" /> -->
```

## Composables

Primary pattern for reusable stateful logic. Prefix with `use`.

```typescript
// composables/useCounter.ts
import { ref, computed } from "vue"

export function useCounter(initial = 0) {
  const count = ref(initial)
  const doubled = computed(() => count.value * 2)
  function increment() { count.value++ }
  function decrement() { count.value-- }
  return { count, doubled, increment, decrement }
}
```

**Rules:** File as `composables/use<Name>.ts` (Nuxt auto-imports). Return plain objects.
Accept options as single object parameter. Clean up side effects with `onUnmounted`.

## Provide / Inject

Use typed `InjectionKey` for deep prop drilling avoidance:

```typescript
// types/injection-keys.ts
import type { InjectionKey, Ref } from "vue"
export const ThemeKey: InjectionKey<Ref<"light" | "dark">> = Symbol("theme")

// Provider: provide(ThemeKey, ref<"light" | "dark">("light"))
// Consumer: const theme = inject(ThemeKey)
```

## Component Organization

- Multi-word names (ESLint enforced): `UserCard`, not `Card`
- Nuxt auto-imports from `components/` — no manual imports needed
- Prefix generic UI: `UiButton`, `UiModal`
- Structure: `components/ui/`, `components/domain/`, `components/layout/`

## Slots

```vue
<template>
  <div class="card">
    <header v-if="$slots.header"><slot name="header" /></header>
    <main><slot /></main>
    <footer v-if="$slots.footer">
      <slot name="footer" :item-count="items.length" />
    </footer>
  </div>
</template>
```

## Lifecycle

| Hook | Use For |
|------|---------|
| `onMounted` | DOM access, browser APIs, client-only data fetch |
| `onUnmounted` | Cleanup: listeners, timers, subscriptions |
| `watch` / `watchEffect` | Reactive side effects (preferred over lifecycle for data) |'

# shellcheck disable=SC2034
RULES_CONTENT_ROUTING='# Nuxt Routing & Data Fetching

> **When to use:** Adding pages, API routes, middleware, data fetching, navigation.
>
> **Read first for:** Any page or route work, server API changes, middleware additions.

## File-Based Routing

```
pages/
├── index.vue                  # /
├── about.vue                  # /about
├── users/
│   ├── index.vue              # /users
│   └── [id].vue               # /users/:id
├── posts/
│   └── [...slug].vue          # /posts/* (catch-all)
└── admin/
    └── [[dashboard]].vue      # /admin or /admin/dashboard (optional)
```

## Page Meta & SEO

```vue
<script setup lang="ts">
definePageMeta({ layout: "admin", middleware: ["auth"], keepalive: true })
useSeoMeta({
  title: "Dashboard",
  ogTitle: "Dashboard - My App",
  description: "Admin dashboard overview",
})
</script>
```

## Data Fetching

### `useFetch` (Primary — SSR + client)

```vue
<script setup lang="ts">
const { data: users, status, error, refresh } = await useFetch<User[]>("/api/users")

// Reactive query params
const page = ref(1)
const { data } = await useFetch<User[]>("/api/users", {
  query: { page, limit: 20 },
  watch: [page],
})
</script>
<template>
  <div v-if="status === '\''pending'\''">Loading...</div>
  <div v-else-if="error">Error: {{ error.message }}</div>
  <ul v-else>
    <li v-for="user in users" :key="user.id">{{ user.name }}</li>
  </ul>
</template>
```

### `useAsyncData` / `$fetch`

```typescript
// Multiple parallel requests
const { data } = await useAsyncData("dashboard", async () => {
  const [users, stats] = await Promise.all([
    $fetch<User[]>("/api/users"),
    $fetch<Stats>("/api/stats"),
  ])
  return { users, stats }
})

// $fetch for mutations (event handlers, NOT setup)
async function deleteUser(id: string) {
  await $fetch(`/api/users/${id}`, { method: "DELETE" })
  await refreshNuxtData("users")
}
```

| Scenario | Use |
|----------|-----|
| Page/component setup | `useFetch` or `useAsyncData` |
| Event handlers, mutations | `$fetch` |
| Multiple parallel requests | `useAsyncData` with `Promise.all` |

## Server Routes (Nitro)

```
server/api/
├── users/
│   ├── index.get.ts       # GET /api/users
│   ├── index.post.ts      # POST /api/users
│   └── [id].get.ts        # GET /api/users/:id
└── health.get.ts          # GET /api/health
```

```typescript
// server/api/users/index.post.ts
import { z } from "zod"

const CreateUserSchema = z.object({
  name: z.string().min(1).max(255),
  email: z.string().email(),
})

export default defineEventHandler(async (event) => {
  const body = await readValidatedBody(event, CreateUserSchema.parse)
  const user = await db.users.create({ data: body })
  setResponseStatus(event, 201)
  return user
})
```

## Middleware

```typescript
// middleware/auth.ts
export default defineNuxtRouteMiddleware((to, from) => {
  const { user } = useAuth()
  if (!user.value && to.meta.requiresAuth !== false) {
    return navigateTo("/login", { redirectCode: 301 })
  }
})
```

## Navigation

```typescript
await navigateTo("/users")
await navigateTo({ path: "/users", query: { page: 2 } })
```

```vue
<template>
  <NuxtLink to="/users">Users</NuxtLink>
</template>
```

## Runtime Config

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  runtimeConfig: {
    secretKey: "",       // Server-only: NUXT_SECRET_KEY
    databaseUrl: "",     // Server-only: NUXT_DATABASE_URL
    public: {
      apiBase: "",       // Client+server: NUXT_PUBLIC_API_BASE
    },
  },
})
// Override at runtime with NUXT_ env vars
```'

# shellcheck disable=SC2034
RULES_CONTENT_CROSS_SERVICE='# Cross-Service Patterns

> **When to use:** State management, config, error handling, shared conventions.
>
> **Read first for:** Pinia stores, runtime config, error handling, environment variables.

## Pinia Stores (Setup Syntax Only)

```typescript
// stores/auth.ts
export const useAuthStore = defineStore("auth", () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const isAuthenticated = computed(() => !!token.value)

  async function login(credentials: { email: string; password: string }) {
    const res = await $fetch<{ user: User; token: string }>("/api/auth/login", {
      method: "POST", body: credentials,
    })
    user.value = res.user
    token.value = res.token
  }

  function logout() {
    user.value = null
    token.value = null
    navigateTo("/login")
  }

  return { user, token, isAuthenticated, login, logout }
})
```

**Rules:** One store per domain. Setup syntax only. Keep stores lean — logic in composables.

## Error Handling

```typescript
// Throw from server routes or middleware
throw createError({
  statusCode: 404,
  statusMessage: "Page Not Found",
  fatal: true, // Shows full-screen error page
})
```

```vue
<!-- error.vue (project root) -->
<script setup lang="ts">
import type { NuxtError } from "#app"
defineProps<{ error: NuxtError }>()
</script>
<template>
  <div>
    <h1>{{ error.statusCode }}</h1>
    <p>{{ error.message }}</p>
    <button @click="clearError({ redirect: '\''/'\'', })">Go Home</button>
  </div>
</template>
```

## Environment Variables

| Variable | Access | Description |
|----------|--------|-------------|
| `NUXT_SECRET_KEY` | `useRuntimeConfig().secretKey` | Server-only secret |
| `NUXT_DATABASE_URL` | `useRuntimeConfig().databaseUrl` | Server-only DB string |
| `NUXT_PUBLIC_API_BASE` | `useRuntimeConfig().public.apiBase` | Client-accessible API URL |

**Pattern:** All overrides use `NUXT_` prefix. Nested keys use `_` separator.
**Secrets are NEVER committed to git.** Use `.env` locally, secrets manager in production.

## Nuxt Config Patterns

```typescript
export default defineNuxtConfig({
  devtools: { enabled: true },
  modules: ["@pinia/nuxt", "@nuxt/eslint"],
  ssr: true,
  routeRules: {
    "/":         { prerender: true },       // Static at build time
    "/api/**":   { cors: true },            // CORS for API routes
    "/admin/**": { ssr: false },            // Client-only SPA
    "/blog/**":  { swr: 3600 },             // Stale-while-revalidate
  },
  typescript: { strict: true, typeCheck: true },
})
```

## TypeScript Conventions

- **Strict mode** enabled (extends `.nuxt/tsconfig.json`)
- Run `npx nuxi prepare` after config changes to regenerate types
- Use `interface` for objects, `type` for unions — never use `any`
- Auto-imports: `ref`, `computed`, `useFetch`, etc. need no manual imports

## Testing Patterns

```typescript
// Component test with @nuxt/test-utils
import { mountSuspended } from "@nuxt/test-utils/runtime"
import UserCard from "~/components/domain/UserCard.vue"

it("renders user name", async () => {
  const wrapper = await mountSuspended(UserCard, {
    props: { user: { id: "1", name: "Alice", email: "alice@example.com" } },
  })
  expect(wrapper.text()).toContain("Alice")
})

// Pinia store test
import { setActivePinia, createPinia } from "pinia"
beforeEach(() => setActivePinia(createPinia()))
it("starts unauthenticated", () => {
  expect(useAuthStore().isAuthenticated).toBe(false)
})
```

**Never log:** passwords, tokens, PII, full request bodies with sensitive data.

## Security Best Practices

### XSS Prevention
- Vue auto-escapes all template interpolations (`{{ }}`) — this is your primary defense
- **Never** use `v-html` with user-supplied input
- If rendering user HTML is unavoidable, sanitize with DOMPurify:
```vue
<script setup lang="ts">
import DOMPurify from "dompurify"
const props = defineProps<{ rawHtml: string }>()
const safeHtml = computed(() => DOMPurify.sanitize(props.rawHtml))
</script>
<template>
  <div v-html="safeHtml" />
</template>
```

### Content Security Policy
Use the `nuxt-security` module for automatic CSP headers:
```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  modules: ["nuxt-security"],
  security: {
    headers: {
      contentSecurityPolicy: {
        "default-src": ["'\''self'\''"],
        "script-src": ["'\''self'\''"],
        "style-src": ["'\''self'\''", "'\''unsafe-inline'\''"],
        "img-src": ["'\''self'\''", "data:", "https:"],
        "connect-src": ["'\''self'\''", "https://api.example.com"],
        "frame-ancestors": ["'\''none'\''"],
      },
    },
  },
})
```
Install: `pnpm add nuxt-security`

### CSRF Protection
- Use `SameSite=Strict` cookies for session tokens
- `nuxt-security` module includes built-in CSRF protection for Nitro server routes
- For manual CSRF tokens, use a Nitro middleware:
```typescript
// server/middleware/csrf.ts
export default defineEventHandler((event) => {
  if (["POST", "PUT", "PATCH", "DELETE"].includes(event.method)) {
    const csrfToken = getCookie(event, "csrf-token")
    const headerToken = getHeader(event, "x-csrf-token")
    if (!csrfToken || csrfToken !== headerToken) {
      throw createError({ statusCode: 403, statusMessage: "Invalid CSRF token" })
    }
  }
})
```

### Authentication Token Storage
- **Never** store tokens in `localStorage` (XSS-accessible)
- Use `httpOnly` cookies for session tokens (not accessible via JavaScript)
- For SPAs: short-lived access token in memory + `httpOnly` refresh cookie
- Use `useCookie` with `httpOnly` server-side for secure session handling

### Dependency Security
```bash
pnpm audit --production
npx better-npm-audit audit
npx nuxi upgrade  # check for Nuxt security patches
```
Run `pnpm audit` in CI and block merges on critical/high vulnerabilities.

## Performance Checklist

### Bundle Optimization
- Use `defineAsyncComponent` for heavy client-only components:
```typescript
const HeavyChart = defineAsyncComponent(() => import("~/components/HeavyChart.vue"))
```
- Nuxt auto-splits routes — each `pages/*.vue` is a separate chunk
- Use `@defer` / `<LazyComponent />` pattern (Nuxt auto-prefixes with `Lazy`):
```vue
<template>
  <LazyHeavyChart v-if="showChart" :data="chartData" />
</template>
```
- Tree shaking: use named imports (`import { debounce } from "lodash-es"` not `import _ from "lodash"`)
- Analyze bundle:
```bash
npx nuxi analyze
```

### Rendering Performance
- Use `v-once` for content that never changes after initial render
- Use `v-memo` for expensive list items that rarely update
- Use `shallowRef` / `shallowReactive` for large objects where deep reactivity is unnecessary
- Virtualize long lists with `vue-virtual-scroller`:
```vue
<script setup lang="ts">
import { RecycleScroller } from "vue-virtual-scroller"
import "vue-virtual-scroller/dist/vue-virtual-scroller.css"
</script>
<template>
  <RecycleScroller :items="items" :item-size="50" key-field="id" v-slot="{ item }">
    <div>{{ item.name }}</div>
  </RecycleScroller>
</template>
```

### Image Optimization
- Use `nuxt/image` module for automatic optimization:
```vue
<template>
  <NuxtImg src="/hero.jpg" width="1200" height="600" format="webp" loading="eager" />
  <NuxtPicture src="/photo.jpg" width="800" height="400" />
</template>
```
- Always specify `width` and `height` to prevent layout shift
- Use `loading="eager"` only for above-the-fold images (LCP candidates)
- Configure providers (Cloudinary, imgix, etc.) in `nuxt.config.ts`

### Core Web Vitals
- **LCP < 2.5s:** Mark hero images with `loading="eager"`, preload critical fonts
- **FID < 100ms:** Minimize client JS by leveraging SSR and server components
- **CLS < 0.1:** Always set image dimensions, use `aspect-ratio` CSS, avoid injecting content above fold
- Use `useHead` to preload critical resources:
```typescript
useHead({
  link: [
    { rel: "preload", href: "/fonts/inter.woff2", as: "font", type: "font/woff2", crossorigin: "" },
  ],
})
```
- Configure `routeRules` for optimal caching:
```typescript
routeRules: {
  "/": { prerender: true },
  "/blog/**": { swr: 3600 },
  "/api/**": { cors: true, headers: { "cache-control": "no-store" } },
}
```'

LINT_LANGUAGES="TypeScript/Vue (eslint + prettier), JSON, YAML, Shell (shellcheck)"
