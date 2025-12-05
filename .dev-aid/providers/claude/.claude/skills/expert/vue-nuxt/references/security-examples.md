# Vue 3 / Nuxt 3 Security Examples

This document provides comprehensive security examples and mitigation strategies for Vue 3 and Nuxt 3 applications, with focus on known CVEs and OWASP Top 10 vulnerabilities.

## 1. Known Vulnerabilities (CVE Mitigation)

### CVE-2024-34344: Nuxt RCE via Test Component

**Severity**: HIGH (CVSS 8.6)
**Affected Versions**: Nuxt < 3.12.4
**Description**: Remote Code Execution through malicious test component injection

**Mitigation**:
```json
// package.json
{
  "dependencies": {
    "nuxt": "^3.12.4"  // ✅ Fixed version
  }
}
```

**Secure Configuration**:
```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  // Disable component auto-import in production if not needed
  components: process.env.NODE_ENV === 'production' ? false : {
    dirs: ['~/components']
  },

  // Strict CSP headers
  routeRules: {
    '/**': {
      headers: {
        'Content-Security-Policy': [
          "default-src 'self'",
          "script-src 'self'",
          "style-src 'self' 'unsafe-inline'",
          "img-src 'self' data: blob:",
          "connect-src 'self' wss:",
          "frame-ancestors 'none'"
        ].join('; ')
      }
    }
  }
})
```

### CVE-2024-23657: Devtools Path Traversal/RCE

**Severity**: HIGH (CVSS 9.3)
**Affected Versions**: @nuxt/devtools < 1.3.9
**Description**: Path traversal leading to arbitrary file read and potential RCE

**Mitigation**:
```json
// package.json
{
  "devDependencies": {
    "@nuxt/devtools": "^1.3.9"  // ✅ Fixed version
  }
}
```

**Configuration**:
```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  // ✅ CRITICAL: Disable devtools in production
  devtools: {
    enabled: process.env.NODE_ENV === 'development'
  },

  // Production override
  $production: {
    devtools: { enabled: false }
  }
})
```

### CVE-2023-3224: Dev Server Code Injection

**Severity**: CRITICAL (CVSS 9.8)
**Affected Versions**: Nuxt < 3.4.4

**Mitigation**:
```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  // ✅ NEVER expose dev server to public network
  devServer: {
    host: 'localhost',  // Only localhost
    port: 3000
  }
})
```

## 2. XSS Prevention Patterns

### Comprehensive Sanitization

```typescript
// composables/useSanitize.ts
import DOMPurify from 'isomorphic-dompurify'

export function useSanitize() {
  const sanitizeHTML = (dirty: string): string => {
    return DOMPurify.sanitize(dirty, {
      ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'span', 'p', 'br'],
      ALLOWED_ATTR: ['class'],
      FORBID_TAGS: ['script', 'object', 'embed', 'iframe'],
      FORBID_ATTR: ['onerror', 'onload', 'onclick']
    })
  }

  const sanitizeText = (input: string): string => {
    return DOMPurify.sanitize(input, { ALLOWED_TAGS: [] })
  }

  const sanitizeURL = (url: string): string => {
    const clean = DOMPurify.sanitize(url, { ALLOWED_TAGS: [] })
    if (!/^https?:\/\//i.test(clean)) {
      return ''
    }
    return clean
  }

  return { sanitizeHTML, sanitizeText, sanitizeURL }
}
```

### Safe Dynamic Component Rendering

```vue
<script setup lang="ts">
// ❌ DANGEROUS - Dynamic component from user input
// <component :is="userInput" />

// ✅ SECURE - Allowlist of valid components
const componentMap = {
  'status-panel': StatusPanel,
  'metrics-display': MetricsDisplay,
  'alert-banner': AlertBanner
} as const

const props = defineProps<{
  componentType: string
}>()

const safeComponent = computed(() => {
  const key = props.componentType as keyof typeof componentMap
  return componentMap[key] || FallbackComponent
})
</script>

<template>
  <component :is="safeComponent" />
</template>
```

## 3. Authentication & Authorization

### Secure JWT Implementation

```typescript
// server/utils/jwt.ts
import jwt from 'jsonwebtoken'

const config = useRuntimeConfig()

export function signToken(payload: object): string {
  return jwt.sign(payload, config.jwtSecret, {
    expiresIn: '1h',
    issuer: 'jarvis-app',
    audience: 'jarvis-users'
  })
}

export function verifyToken(token: string): object {
  try {
    return jwt.verify(token, config.jwtSecret, {
      issuer: 'jarvis-app',
      audience: 'jarvis-users'
    })
  } catch (error) {
    throw createError({
      statusCode: 401,
      message: 'Invalid token'
    })
  }
}
```

### Route Protection Middleware

```typescript
// middleware/auth.global.ts
export default defineNuxtRouteMiddleware(async (to) => {
  const { user, refreshToken } = useAuth()

  // Public routes
  if (to.meta.public) return

  // Check authentication
  if (!user.value) {
    const refreshed = await refreshToken()
    if (!refreshed) {
      return navigateTo({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    }
  }

  // Check authorization
  if (to.meta.requiredRole) {
    if (!user.value?.roles.includes(to.meta.requiredRole)) {
      throw createError({
        statusCode: 403,
        message: 'Insufficient permissions'
      })
    }
  }
})
```

### CSRF Protection

```typescript
// server/middleware/csrf.ts
export default defineEventHandler(async (event) => {
  // Skip for GET requests
  if (event.method === 'GET') return

  const csrfToken = getHeader(event, 'x-csrf-token')
  const sessionToken = await getSession(event)

  if (!csrfToken || csrfToken !== sessionToken.csrf) {
    throw createError({
      statusCode: 403,
      message: 'Invalid CSRF token'
    })
  }
})
```

## 4. Input Validation with Zod

### API Route Validation

```typescript
// server/api/jarvis/command.post.ts
import { z } from 'zod'

const commandSchema = z.object({
  action: z.enum(['status', 'control', 'query']),
  target: z.string().max(100).regex(/^[a-zA-Z0-9-_]+$/),
  parameters: z.record(z.string()).optional()
})

export default defineEventHandler(async (event) => {
  const body = await readBody(event)

  const result = commandSchema.safeParse(body)
  if (!result.success) {
    throw createError({
      statusCode: 400,
      message: 'Invalid command format'
    })
  }

  const command = result.data
  return { success: true, commandId: generateSecureId() }
})
```

## 5. Rate Limiting

```typescript
// server/utils/rateLimit.ts
const rateLimits = new Map<string, { count: number; resetAt: number }>()

export function checkRateLimit(key: string, limit: number, windowMs: number): boolean {
  const now = Date.now()
  const record = rateLimits.get(key)

  if (!record || now > record.resetAt) {
    rateLimits.set(key, { count: 1, resetAt: now + windowMs })
    return true
  }

  if (record.count >= limit) {
    return false
  }

  record.count++
  return true
}

// server/api/protected.post.ts
export default defineEventHandler(async (event) => {
  const ip = getRequestIP(event) || 'unknown'

  if (!checkRateLimit(`api:${ip}`, 100, 60000)) {
    throw createError({
      statusCode: 429,
      message: 'Too many requests'
    })
  }

  // Process request
})
```

## 6. Secure Cookie Configuration

```typescript
// server/api/auth/login.post.ts
export default defineEventHandler(async (event) => {
  const { email, password } = await readBody(event)
  const user = await validateCredentials(email, password)

  if (!user) {
    throw createError({
      statusCode: 401,
      message: 'Invalid credentials'
    })
  }

  const token = signToken({ userId: user.id })

  setCookie(event, 'auth-token', token, {
    httpOnly: true,       // Not accessible via JavaScript
    secure: true,         // HTTPS only
    sameSite: 'strict',   // CSRF protection
    maxAge: 3600,         // 1 hour
    path: '/'
  })

  return { success: true }
})
```

## Security Checklist

- [ ] Nuxt >= 3.12.4 (CVE-2024-34344)
- [ ] Devtools >= 1.3.9 (CVE-2024-23657)
- [ ] CSP headers configured
- [ ] No secrets in runtimeConfig.public
- [ ] All inputs validated with Zod
- [ ] DOMPurify for HTML sanitization
- [ ] Authentication on protected routes
- [ ] Rate limiting enabled
- [ ] HTTPS enforced
- [ ] Secure cookie configuration
