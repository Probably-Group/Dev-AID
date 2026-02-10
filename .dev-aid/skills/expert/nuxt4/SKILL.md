---
name: nuxt4
version: 2.0.0
description: "Nuxt 4 full-stack patterns with server routes, useFetch, hybrid rendering, and runtime config security. Use when building Nuxt applications, configuring SSR/SSG, or implementing server routes. Do NOT use for plain Vue without SSR or routing (use vue3)."
compatibility: "Nuxt 4+, Vue 3.3+, Node.js 18+"
risk_level: MEDIUM
---

# Nuxt 4 - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-20: Server Route Input Validation**
- NEVER: `const body = await readBody(event)` without validation
- ALWAYS: `const body = await readValidatedBody(event, schema.parse)`

**CWE-200: Runtime Config Secrets**
- NEVER: `runtimeConfig: { public: { apiKey: process.env.SECRET } }` - exposed to client
- ALWAYS: Secrets in `runtimeConfig` root (private), only safe values in `public`

**CWE-79: XSS in SSR**
- NEVER: `<div v-html="serverData">` with user content
- ALWAYS: Text interpolation `{{ content }}` or sanitize with isomorphic-dompurify

**CWE-352: CSRF on Server Routes**
- NEVER: State-changing routes without CSRF validation
- ALWAYS: Validate CSRF token from header against session

### 0.3 Risk Level: MEDIUM

**Verification requirements for MEDIUM risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 Server Route Input Validation (CWE-20)

**Principle:** All server route inputs must be validated. User input flows directly to server.

```typescript
// ❌ WRONG - No input validation in server route
export default defineEventHandler(async (event) => {
  const body = await readBody(event);
  const user = await db.users.findById(body.userId);
  return user;
});

// ✅ CORRECT - Validate with Zod schemas
import { z } from 'zod';

const GetUserSchema = z.object({
  userId: z.string().uuid(),
});

export default defineEventHandler(async (event) => {
  const body = await readBody(event);

  const result = GetUserSchema.safeParse(body);
  if (!result.success) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Invalid input',
      data: result.error.flatten(),
    });
  }

  const user = await db.users.findById(result.data.userId);
  if (!user) {
    throw createError({
      statusCode: 404,
      statusMessage: 'User not found',
    });
  }

  return user;
});
```

### 1.2 Runtime Config Security (CWE-200)

**Principle:** Never expose secrets via public runtime config. Use private config for server-only values.

```typescript
// ❌ WRONG - Secret in public config (exposed to client!)
// nuxt.config.ts
export default defineNuxtConfig({
  runtimeConfig: {
    public: {
      apiKey: process.env.API_KEY, // Exposed to browser!
    },
  },
});

// ✅ CORRECT - Secrets in private config only
// nuxt.config.ts
export default defineNuxtConfig({
  runtimeConfig: {
    // Private - server only
    apiKey: process.env.API_KEY,
    databaseUrl: process.env.DATABASE_URL,

    // Public - safe to expose
    public: {
      apiBase: '/api',
      appName: 'My App',
    },
  },
});

// Access in server route
export default defineEventHandler((event) => {
  const config = useRuntimeConfig(event);
  // config.apiKey - available
  // config.public.apiBase - available
});

// Access in component (only public available)
const config = useRuntimeConfig();
// config.apiKey - undefined (correctly hidden)
// config.public.apiBase - available
```

### 1.3 CSRF Protection for Server Routes (CWE-352)

**Principle:** Protect state-changing server routes from CSRF attacks.

```typescript
// ❌ WRONG - No CSRF protection
export default defineEventHandler(async (event) => {
  const body = await readBody(event);
  await db.users.delete(body.userId);
  return { success: true };
});

// ✅ CORRECT - CSRF token validation
// server/utils/csrf.ts
import { createHash, randomBytes } from 'crypto';

export function generateCsrfToken(sessionId: string): string {
  const secret = useRuntimeConfig().csrfSecret;
  const token = randomBytes(32).toString('hex');
  const hash = createHash('sha256')
    .update(`${sessionId}:${token}:${secret}`)
    .digest('hex');
  return `${token}:${hash}`;
}

export function validateCsrfToken(
  sessionId: string,
  token: string
): boolean {
  const [rawToken, hash] = token.split(':');
  const secret = useRuntimeConfig().csrfSecret;
  const expectedHash = createHash('sha256')
    .update(`${sessionId}:${rawToken}:${secret}`)
    .digest('hex');
  return hash === expectedHash;
}

// server/api/users/[id].delete.ts
export default defineEventHandler(async (event) => {
  const session = await getUserSession(event);
  const csrfToken = getHeader(event, 'x-csrf-token');

  if (!csrfToken || !validateCsrfToken(session.id, csrfToken)) {
    throw createError({
      statusCode: 403,
      statusMessage: 'Invalid CSRF token',
    });
  }

  const id = getRouterParam(event, 'id');
  await db.users.delete(id);
  return { success: true };
});
```

### 1.4 Hybrid Rendering Security (CWE-79)

**Principle:** Server-rendered content must escape user data. Avoid v-html with untrusted content.

```vue
<!-- ❌ WRONG - XSS via server-rendered content -->
<template>
  <div v-html="userContent" />
</template>

<script setup lang="ts">
const { data } = await useFetch('/api/content');
const userContent = data.value?.content; // Raw HTML from user!
</script>

<!-- ✅ CORRECT - Sanitize or use text interpolation -->
<template>
  <!-- Safe: text interpolation -->
  <div>{{ userContent }}</div>

  <!-- If HTML needed: sanitize -->
  <div v-html="sanitizedContent" />
</template>

<script setup lang="ts">
import DOMPurify from 'isomorphic-dompurify';

const { data } = await useFetch('/api/content');
const userContent = data.value?.content ?? '';

// Sanitize if HTML is required
const sanitizedContent = computed(() =>
  DOMPurify.sanitize(userContent, {
    ALLOWED_TAGS: ['p', 'b', 'i', 'em', 'strong', 'a'],
    ALLOWED_ATTR: ['href', 'title'],
  })
);
</script>
```

---

## 2. Version Requirements

```json
{
  "dependencies": {
    "nuxt": "^4.0.0",
    "vue": "^3.5.0"
  },
  "devDependencies": {
    "@nuxt/devtools": "^2.0.0",
    "@nuxt/test-utils": "^3.15.0",
    "@nuxtjs/tailwindcss": "^7.0.0",
    "zod": "^3.23.0",
    "isomorphic-dompurify": "^2.16.0"
  }
}
```

---

## 3. Code Patterns

### WHEN using data fetching, prefer useFetch with proper error handling

```typescript
// ❌ WRONG - No error handling, no typing
const { data } = await useFetch('/api/users');
console.log(data.value.name); // Could be null!

// ✅ CORRECT - Typed with error handling
interface User {
  id: string;
  name: string;
  email: string;
}

const {
  data: user,
  error,
  status,
  refresh,
} = await useFetch<User>('/api/users/me', {
  // Transform response
  transform: (response) => ({
    ...response,
    name: response.name.trim(),
  }),

  // Cache key for deduplication
  key: 'current-user',

  // Only fetch on client if needed
  lazy: true,

  // Watch reactive sources
  watch: [userId],
});

// Handle loading and error states
if (status.value === 'pending') {
  // Show skeleton
}

if (error.value) {
  throw createError({
    statusCode: error.value.statusCode,
    statusMessage: error.value.message,
  });
}
```

### WHEN using composables, follow Nuxt 4 conventions

```typescript
// ❌ WRONG - Composable outside setup context
// utils/helpers.ts
export function getUser() {
  const user = useState('user'); // Error: useState outside setup!
  return user;
}

// ✅ CORRECT - Composable with proper context
// composables/useUser.ts
export function useUser() {
  const user = useState<User | null>('user', () => null);
  const isAuthenticated = computed(() => !!user.value);

  async function login(credentials: Credentials) {
    const { data, error } = await useFetch<User>('/api/auth/login', {
      method: 'POST',
      body: credentials,
    });

    if (error.value) {
      throw createError({
        statusCode: 401,
        statusMessage: 'Invalid credentials',
      });
    }

    user.value = data.value;
  }

  async function logout() {
    await useFetch('/api/auth/logout', { method: 'POST' });
    user.value = null;
    await navigateTo('/login');
  }

  return {
    user: readonly(user),
    isAuthenticated,
    login,
    logout,
  };
}
```

### WHEN using server components, handle hydration properly

```vue
<!-- ❌ WRONG - Server component with client interactivity -->
<!-- components/UserCard.server.vue -->
<template>
  <div @click="handleClick"> <!-- Won't work! -->
    {{ user.name }}
  </div>
</template>

<!-- ✅ CORRECT - Server component for static, client for interactive -->
<!-- components/UserCard.server.vue -->
<template>
  <div class="user-card">
    <span>{{ user.name }}</span>
    <!-- Slot for client-side interactivity -->
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{ user: User }>();
</script>

<!-- pages/users.vue -->
<template>
  <UserCard :user="user">
    <!-- Client-side interactive button -->
    <button @click="follow(user.id)">Follow</button>
  </UserCard>
</template>
```

### WHEN implementing middleware, use route rules efficiently

```typescript
// ❌ WRONG - Middleware runs on every route
// middleware/auth.global.ts
export default defineNuxtRouteMiddleware((to) => {
  const { isAuthenticated } = useUser();
  if (!isAuthenticated.value) {
    return navigateTo('/login');
  }
});

// ✅ CORRECT - Route rules with targeted middleware
// nuxt.config.ts
export default defineNuxtConfig({
  routeRules: {
    // Static pages - prerender
    '/': { prerender: true },
    '/about': { prerender: true },

    // Protected routes - no prerender, auth required
    '/dashboard/**': { ssr: true },
    '/api/admin/**': { cors: false },

    // API routes - caching
    '/api/public/**': {
      cache: { maxAge: 60 },
      cors: true,
    },
  },
});

// middleware/auth.ts (not global)
export default defineNuxtRouteMiddleware((to) => {
  // Only runs when explicitly applied
  const { isAuthenticated } = useUser();
  if (!isAuthenticated.value) {
    return navigateTo('/login');
  }
});

// pages/dashboard.vue
<script setup lang="ts">
definePageMeta({
  middleware: 'auth', // Apply auth middleware
});
</script>
```

### WHEN using Nuxt 4 directory structure, follow new conventions

```
// ❌ WRONG - Nuxt 3 structure (still works but not recommended)
├── pages/
├── components/
├── composables/
├── server/
└── nuxt.config.ts

// ✅ CORRECT - Nuxt 4 app directory structure
├── app/
│   ├── pages/
│   ├── components/
│   ├── composables/
│   ├── layouts/
│   ├── middleware/
│   ├── plugins/
│   └── app.vue
├── server/
│   ├── api/
│   ├── middleware/
│   ├── plugins/
│   └── utils/
├── public/
├── shared/           # Shared between app and server
│   ├── types/
│   └── utils/
└── nuxt.config.ts
```

### WHEN implementing API routes, use proper HTTP methods and validation

```typescript
// ❌ WRONG - Single handler for all methods
// server/api/users.ts
export default defineEventHandler(async (event) => {
  if (event.method === 'GET') { /* ... */ }
  if (event.method === 'POST') { /* ... */ }
});

// ✅ CORRECT - Separate files per method with validation
// server/api/users/index.get.ts
import { z } from 'zod';

const QuerySchema = z.object({
  page: z.coerce.number().min(1).default(1),
  limit: z.coerce.number().min(1).max(100).default(20),
  search: z.string().optional(),
});

export default defineEventHandler(async (event) => {
  const query = await getValidatedQuery(event, QuerySchema.parse);

  const users = await db.users.findMany({
    skip: (query.page - 1) * query.limit,
    take: query.limit,
    where: query.search
      ? { name: { contains: query.search } }
      : undefined,
  });

  return {
    data: users,
    meta: {
      page: query.page,
      limit: query.limit,
    },
  };
});

// server/api/users/index.post.ts
const CreateUserSchema = z.object({
  name: z.string().min(2).max(100),
  email: z.string().email(),
  password: z.string().min(8).max(100),
});

export default defineEventHandler(async (event) => {
  const body = await readValidatedBody(event, CreateUserSchema.parse);

  // Hash password before storing
  const hashedPassword = await hashPassword(body.password);

  const user = await db.users.create({
    data: {
      ...body,
      password: hashedPassword,
    },
  });

  // Don't return password
  const { password: _, ...safeUser } = user;
  return safeUser;
});
```

### WHEN managing state, use useState with proper typing

```typescript
// ❌ WRONG - Multiple useState calls create separate states
// Component A
const count = useState('count', () => 0);
count.value++;

// Component B
const count = useState('count', () => 0); // Gets fresh 0!

// ✅ CORRECT - Centralized state in composable
// composables/useCounter.ts
export function useCounter() {
  const count = useState<number>('counter', () => 0);

  function increment() {
    count.value++;
  }

  function decrement() {
    count.value--;
  }

  function reset() {
    count.value = 0;
  }

  return {
    count: readonly(count),
    increment,
    decrement,
    reset,
  };
}

// Any component
const { count, increment } = useCounter();
// All components share the same state
```

### WHEN using TypeScript, leverage Nuxt 4 auto-imports

```typescript
// ❌ WRONG - Manual imports for Nuxt utilities
import { ref, computed, watch } from 'vue';
import { useFetch, useState, navigateTo } from '#imports';

// ✅ CORRECT - Auto-imported (nuxt.config.ts enables this by default)
// Just use directly - TypeScript knows the types
const count = ref(0);
const doubled = computed(() => count.value * 2);
const { data } = await useFetch('/api/data');

// For custom composables, ensure they're in composables/
// They're auto-imported with correct types

// Type augmentation for custom properties
// types/nuxt.d.ts
declare module '#app' {
  interface NuxtApp {
    $myPlugin: MyPluginAPI;
  }
}

declare module 'vue' {
  interface ComponentCustomProperties {
    $myPlugin: MyPluginAPI;
  }
}
```

---

## 4. Anti-Patterns

**NEVER:**
- Expose secrets in `runtimeConfig.public`
- Use `v-html` with unsanitized user content
- Skip input validation in server routes
- Use `$fetch` instead of `useFetch` in components (loses SSR benefits)
- Create global middleware when route-specific suffices
- Mix client-only interactivity in `.server.vue` components
- Forget error handling in data fetching
- Use synchronous operations in server routes

---

## 5. Testing

```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { setup, $fetch, createPage } from '@nuxt/test-utils/e2e';

describe('Nuxt 4 Application', () => {
  beforeEach(async () => {
    await setup({
      server: true,
      browser: true,
    });
  });

  describe('Server Routes', () => {
    it('should validate input and return 400 for invalid data', async () => {
      const response = await $fetch('/api/users', {
        method: 'POST',
        body: { email: 'invalid' },
        ignoreResponseError: true,
      });

      expect(response.statusCode).toBe(400);
    });

    it('should not expose private config', async () => {
      const page = await createPage('/');
      const config = await page.evaluate(() => {
        return (window as any).__NUXT__.config;
      });

      expect(config.apiKey).toBeUndefined();
      expect(config.public.apiBase).toBeDefined();
    });
  });

  describe('CSRF Protection', () => {
    it('should reject requests without CSRF token', async () => {
      const response = await $fetch('/api/users/123', {
        method: 'DELETE',
        ignoreResponseError: true,
      });

      expect(response.statusCode).toBe(403);
    });
  });

  describe('XSS Prevention', () => {
    it('should sanitize user content', async () => {
      const page = await createPage('/content');
      const html = await page.innerHTML('.user-content');

      expect(html).not.toContain('<script>');
      expect(html).not.toContain('onerror=');
    });
  });

  describe('Data Fetching', () => {
    it('should handle useFetch errors gracefully', async () => {
      const page = await createPage('/users/nonexistent');

      // Should show error state, not crash
      const errorMessage = await page.textContent('.error-message');
      expect(errorMessage).toContain('not found');
    });
  });
});
```

---

## 6. Pre-Generation Checklist

**BEFORE generating Nuxt 4 code:**

- [ ] Runtime config: Secrets in private only, public for client-safe values
- [ ] Server routes: Input validation with Zod on all endpoints
- [ ] CSRF: Token validation on state-changing operations
- [ ] XSS: No v-html with unsanitized content, use DOMPurify if needed
- [ ] Data fetching: useFetch with proper typing and error handling
- [ ] Composables: Defined in composables/ for auto-import
- [ ] Directory structure: Using Nuxt 4 app/ directory conventions
- [ ] Middleware: Route-specific when possible, global only when necessary
- [ ] Server components: No client interactivity, use slots for interactive parts
- [ ] State: Centralized in composables, proper typing with useState

---

**Performance**: Quality over speed. Verify all code examples compile. Never skip security checks. See `template-references/performance-notes.md` for full guidelines.