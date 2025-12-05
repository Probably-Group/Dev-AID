---
name: vue-nuxt
description: Vue 3 and Nuxt 3 for JARVIS AI Assistant UI development with security-first patterns
risk_level: MEDIUM
version: 1.0.0
---

# Vue 3 / Nuxt 3 Development Skill

> **File Organization**: This skill uses split structure. See `references/` for advanced patterns, security examples, performance optimization, testing guides, and anti-patterns.

## 0. Anti-Hallucination Protocol

**🚨 MANDATORY: Read before implementing any Vue/Nuxt code**

### Verification Requirements

When using this skill to implement Vue 3 or Nuxt 3 features, you MUST:

1. **Verify Before Implementing**
   - ✅ Check official Vue 3 and Nuxt 3 documentation
   - ✅ Confirm API methods exist in current versions
   - ✅ Validate composable patterns against official guides
   - ❌ Never guess configuration options
   - ❌ Never invent API methods or composables
   - ❌ Never assume package compatibility without checking

2. **Use Available Tools**
   - 🔍 Read: Check existing codebase for patterns
   - 🔍 Grep: Search for similar implementations
   - 🔍 WebSearch: Verify specs in official docs
   - 🔍 WebFetch: Read official Vue/Nuxt documentation

3. **Verify if Certainty < 80%**
   - If uncertain about ANY Vue/Nuxt API, composable, or pattern
   - STOP and verify before implementing
   - Document verification source in response
   - Errors in Vue/Nuxt can cause runtime failures, security vulnerabilities, or hydration mismatches

4. **Common Vue/Nuxt Hallucination Traps** (AVOID)
   - ❌ Invented composables (e.g., `useVueX`, `useNuxtState` - verify actual names)
   - ❌ Non-existent Nuxt config options (e.g., made-up `experimental` flags)
   - ❌ Wrong reactivity APIs (mixing Vue 2/3 syntax, incorrect ref usage)
   - ❌ Fake lifecycle hooks or incorrect hook names
   - ❌ Made-up plugin patterns or module configurations

### Self-Check Checklist

Before EVERY response with Vue/Nuxt code:
- [ ] All composables verified against official docs
- [ ] Configuration options verified against current Nuxt version
- [ ] Reactivity patterns verified (ref vs reactive vs shallowRef)
- [ ] Can cite official documentation sources

**⚠️ CRITICAL**: Vue/Nuxt code with hallucinated patterns causes runtime errors, hydration mismatches, and security vulnerabilities. Always verify.

---

## 1. Overview

This skill provides expertise for building the JARVIS AI Assistant user interface using Vue 3 and Nuxt 3. It focuses on creating responsive, performant 3D HUD interfaces with security-first development practices.

**Risk Level**: MEDIUM - Handles user input, renders dynamic content, potential XSS vectors

**Primary Use Cases**:
- Building reactive 3D HUD components for JARVIS interface
- Server-side rendering for initial load performance
- Client-side state management integration
- Secure handling of user inputs and API responses

## 2. Core Responsibilities

### 2.1 Fundamental Principles

1. **TDD First**: Write tests before implementation - red/green/refactor cycle
2. **Performance Aware**: Use computed, shallowRef, lazy components for optimal reactivity
3. **Composition API First**: Use Vue 3 Composition API with `<script setup>` for better TypeScript inference
4. **Server-Side Security**: Leverage Nuxt's server routes for sensitive operations, never expose secrets to client
5. **Reactive State Safety**: Use `ref()` and `reactive()` with proper typing to prevent state corruption
6. **Input Sanitization**: Always sanitize user inputs before rendering or processing
7. **Performance Optimization**: Implement lazy loading, code splitting, and efficient reactivity for 3D HUD performance
8. **Type Safety**: Enforce TypeScript throughout for compile-time error detection
9. **Secure Defaults**: Configure CSP headers, disable dangerous features by default

## 3. Technology Stack & Versions

### 3.1 Recommended Versions

| Package | Version | Security Notes |
|---------|---------|----------------|
| Vue | ^3.4.0 | Latest stable with improved reactivity |
| Nuxt | ^3.12.4+ | **CRITICAL**: Fixes CVE-2024-34344 RCE |
| @nuxt/devtools | ^1.3.9+ | **CRITICAL**: Fixes CVE-2024-23657 |
| vite | ^5.0.0 | Latest with security patches |

### 3.2 Security-Critical Dependencies

```json
{
  "dependencies": {
    "nuxt": "^3.12.4",
    "vue": "^3.4.0",
    "dompurify": "^3.0.6",
    "isomorphic-dompurify": "^2.0.0"
  },
  "devDependencies": {
    "@nuxt/devtools": "^1.3.9",
    "eslint-plugin-vue": "^9.0.0",
    "eslint-plugin-security": "^2.0.0"
  }
}
```

## 4. Quick Implementation Reference

### 4.1 Basic Component Pattern

```vue
<script setup lang="ts">
// Type-safe props
interface Props {
  hudData: HUDDisplayData
}

const props = defineProps<Props>()

// Typed emits
const emit = defineEmits<{
  'update:status': [status: string]
}>()

// Reactive state
const displayState = ref<HUDState>({
  isActive: false,
  securityLevel: 'standard'
})
</script>

<template>
  <!-- Use v-text for user content to prevent XSS -->
  <div class="hud-panel">
    <span v-text="props.hudData.title" />
  </div>
</template>
```

### 4.2 Secure API Route Pattern

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

  return { success: true, commandId: generateSecureId() }
})
```

### 4.3 Environment Configuration

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  // Security headers
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

  // Runtime config - secrets stay server-side
  runtimeConfig: {
    apiSecret: process.env.API_SECRET,  // Server only
    public: {
      apiBase: '/api'  // Client accessible
    }
  },

  // Disable devtools in production
  devtools: { enabled: process.env.NODE_ENV === 'development' }
})
```

## 5. TDD Workflow (Summary)

### Step 1: Write Failing Test
```typescript
describe('VoiceIndicator', () => {
  it('displays idle state by default', () => {
    const wrapper = mount(VoiceIndicator)
    expect(wrapper.find('.indicator').classes()).toContain('idle')
  })
})
```

### Step 2: Implement Minimum Code
```vue
<template>
  <div class="indicator idle">Ready</div>
</template>
```

### Step 3: Refactor
Improve code quality while keeping tests passing.

### Step 4: Verify
```bash
npx vitest run
npx eslint . --ext .vue,.ts
npx nuxi typecheck
npm run build
```

**See**: `references/testing-guide.md` for comprehensive testing patterns

## 6. Performance Essentials

### Key Patterns
- **Computed Properties**: Cache derived state
- **shallowRef**: For large objects (3D data, large arrays)
- **defineAsyncComponent**: Lazy load heavy components
- **v-memo**: Skip re-renders for unchanged items
- **Virtual Scrolling**: For long lists (>100 items)
- **Debounced Watchers**: Reduce API calls

**See**: `references/performance-optimization.md` for detailed patterns and examples

## 7. Security Standards

### 7.1 Known Vulnerabilities (CVE Research)

| CVE | Severity | Description | Mitigation |
|-----|----------|-------------|------------|
| CVE-2024-34344 | HIGH | Nuxt RCE via test component | Update to Nuxt 3.12.4+ |
| CVE-2024-23657 | HIGH | Devtools path traversal/RCE | Update devtools to 1.3.9+ |
| CVE-2023-3224 | CRITICAL | Dev server code injection | Update to Nuxt 3.4.4+, never expose dev server |

**See**: `references/security-examples.md` for detailed mitigation code

### 7.2 OWASP Top 10 Coverage

| OWASP Category | Risk | Mitigation Strategy |
|----------------|------|---------------------|
| A01 Broken Access Control | HIGH | Server-side route guards, middleware auth |
| A03 Injection | HIGH | Input validation with Zod, parameterized queries |
| A05 Security Misconfiguration | MEDIUM | CSP headers, secure nuxt.config |
| A07 XSS | HIGH | v-text directive, DOMPurify sanitization |

### 7.3 Critical Security Rules

```typescript
// ❌ DANGEROUS - Direct v-html with user input
<div v-html="userMessage" />

// ✅ SECURE - Sanitized HTML or plain text
<div v-html="sanitizeHTML(userMessage)" />
<span v-text="userMessage" />

// ❌ DANGEROUS - Secret in public config
runtimeConfig: {
  public: {
    apiKey: process.env.API_KEY  // Exposed to client!
  }
}

// ✅ SECURE - Secrets stay server-side
runtimeConfig: {
  apiKey: process.env.API_KEY,  // Server only
  public: { apiBase: '/api' }
}
```

**See**: `references/security-examples.md` for comprehensive security patterns

## 8. Common Patterns

### 8.1 JARVIS HUD Component Workflow

1. **Define TypeScript interfaces** for all data structures
2. **Create composable** for shared logic
3. **Implement component** with Composition API
4. **Add input validation** at component boundary
5. **Write security tests** for XSS/injection
6. **Integrate with 3D scene** via TresJS

### 8.2 API Integration Workflow

1. **Define Zod schema** for request/response
2. **Create server route** with validation
3. **Implement client composable** with error handling
4. **Add loading/error states** to UI
5. **Test error cases** and edge conditions

## 9. Essential Composables Reference

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

// Async data with SSR
const { data } = await useAsyncData('key', () => fetchData())
```

**See**: `references/composition-patterns.md` for detailed implementation patterns

## 10. Common Mistakes to Avoid

### Critical Anti-Patterns
- ❌ Never use v-html with unsanitized input (XSS)
- ❌ Never expose secrets in runtimeConfig.public
- ❌ Never trust client-side validation alone
- ❌ Never mutate props directly
- ❌ Never use browser APIs during SSR without checks
- ❌ Avoid deep reactivity on large objects (use shallowRef)
- ❌ Avoid watchers when computed would work
- ❌ Never ignore hydration mismatch warnings

**See**: `references/anti-patterns.md` for comprehensive examples and solutions

## 11. Pre-Deployment Checklist

### Security Verification
- [ ] Nuxt version >= 3.12.4 (CVE-2024-34344 fix)
- [ ] Devtools version >= 1.3.9 (CVE-2024-23657 fix)
- [ ] CSP headers configured in nuxt.config
- [ ] No secrets in `runtimeConfig.public`
- [ ] All user inputs sanitized with DOMPurify
- [ ] Server routes validate with Zod schemas
- [ ] Authentication middleware on protected routes
- [ ] Devtools disabled in production

### Build Verification
- [ ] `npm audit` shows no high/critical vulnerabilities
- [ ] TypeScript compilation passes
- [ ] All security tests pass
- [ ] Production build completes without errors

## 12. References

This skill uses a split file structure for better organization. See the `references/` directory:

- **`composition-patterns.md`** - Vue 3 Composition API patterns, secure component structure, composables, and 3D HUD integration
- **`performance-optimization.md`** - Computed properties, shallowRef, lazy loading, v-memo, virtual scrolling, debouncing, SSR optimization
- **`testing-guide.md`** - TDD workflow, component testing, security testing, E2E testing with Playwright
- **`anti-patterns.md`** - Common mistakes, security anti-patterns, performance pitfalls, and proper solutions
- **`security-examples.md`** - CVE mitigations, XSS prevention, authentication, authorization, input validation, rate limiting

## 13. Summary

This Vue/Nuxt skill provides secure patterns for building the JARVIS AI Assistant HUD interface:

1. **Security First**: Always sanitize inputs, validate on server, use CSP headers
2. **Type Safety**: TypeScript throughout with strict validation schemas
3. **Performance**: Composition API, lazy loading, efficient reactivity
4. **Maintainability**: Clear component structure, composables for reuse
5. **TDD**: Write tests before implementation, verify with comprehensive test suite

**Remember**: The JARVIS HUD handles sensitive system data. Every component must treat user input as potentially malicious and validate all data boundaries.

---

**Version**: 1.0.0
**Last Updated**: 2025-12-05
**Risk Level**: MEDIUM
