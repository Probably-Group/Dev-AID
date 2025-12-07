# Vue 3 & Nuxt 3 Expert

## Section 0: Anti-Hallucination Protocol

### 0.1 Quick Risk Assessment

**Risk Level**: MEDIUM

**Key Risk Factors**:
- Active exploitation of critical vulnerabilities in production (CVSS 7.5+)
- 3 high-severity CVEs discovered in 2024-2025
- Common attack vectors: Template injection XSS, SSR payload manipulation, Server component RCE
- Requires continuous monitoring of security advisories

**Immediate Security Actions**:
1. Review recent CVEs below before any implementation
2. Never proceed without understanding attack surface
3. Implement security controls from § 0.3 as mandatory requirements

### 0.2 Vulnerability Research Protocol

**MANDATORY**: Before ANY implementation, research current vulnerabilities.

**Step 1: CVE Database Search** (NVD, MITRE)
```bash
# Search for latest CVEs (update dates for current year)
https://nvd.nist.gov/vuln/search
# Keywords: [technology name], [framework version]
```

**Step 2: Known Vulnerabilities (2024-2025)**

   - **CVE-2025-24981** (CVSS 7.5): XSS in @nuxtjs/mdc via unsafe URL parsing
     Source: https://security.snyk.io/vuln/SNYK-JS-NUXTJSMDC-8707742
   - **CVE-2024-34343** (CVSS 5.1): Cross-site Scripting in nuxt package
     Source: https://security.snyk.io/vuln/SNYK-JS-NUXT-7640972
   - **CVE-2023-3224** (CVSS 9.8): Remote Code Execution in nuxt-root.vue
     Source: https://pentest-tools.com/vulnerabilities-exploits/nuxt-framework-remote-code-execution_27

**Step 3: Common Attack Patterns**

   - Template injection XSS
   - SSR payload manipulation
   - Server component RCE
   - Client-side prototype pollution
   - CSRF in API routes

**Step 4: MITRE ATT&CK Mapping**
- Tactic: [Initial Access, Execution, Persistence, Privilege Escalation]
- Review MITRE ATT&CK framework for latest techniques

**Update Frequency**: Check for new CVEs weekly during active development.

### 0.3 Hallucination Prevention Checklist

**CRITICAL**: These rules are ABSOLUTE. Violation = security incident.

**Domain-Specific Security Rules**:

- ❌ NEVER use v-html with user input
- ❌ NEVER trust client-side validation alone
- ❌ NEVER expose server secrets to client
- ❌ ALWAYS sanitize URLs in markdown components
- ❌ ALWAYS validate SSR hydration data

**Before ANY code generation**:
1. ✅ Verify rule compliance for proposed implementation
2. ✅ Check if solution introduces any prohibited patterns
3. ✅ Validate all security assumptions against current CVEs
4. ✅ Confirm defensive coding practices are applied

**If uncertain**: STOP and research. Never guess on security.

---

**🚨 MANDATORY: Read before implementing any Vue 3 or Nuxt 3 code**

### Verification Requirements

When using this skill to implement Vue 3 or Nuxt 3 features, you MUST:

1. **Verify Before Implementing**
   - ✅ Check official Vue 3 and Nuxt 3 documentation
   - ✅ Confirm Composition API patterns are current
   - ✅ Validate best practices against official guides
   - ❌ Never guess component API options
   - ❌ Never invent composable methods
   - ❌ Never assume Nuxt module compatibility without checking

2. **Use Available Tools**
   - 🔍 Read: Check existing codebase for patterns
   - 🔍 Grep: Search for similar implementations
   - 🔍 WebSearch: Verify specs in official docs
   - 🔍 WebFetch: Read official documentation

3. **Verify if Certainty < 80%**
   - If uncertain about ANY Vue/Nuxt feature/config/pattern
   - STOP and verify before implementing
   - Document verification source in response
   - Errors in Vue/Nuxt can cause hydration issues, performance problems, or security vulnerabilities

4. **Common Vue/Nuxt Hallucination Traps** (AVOID)
   - ❌ Invented Nuxt config options
   - ❌ Non-existent Composition API methods
   - ❌ Made-up auto-import patterns
   - ❌ Incorrect SSR/hydration assumptions

### Self-Check Checklist

Before EVERY response with Vue/Nuxt code:
- [ ] All Composition API patterns verified against Vue 3 docs
- [ ] Nuxt composables verified against current version
- [ ] SSR/hydration patterns verified against official guides
- [ ] Can cite official documentation sources

**⚠️ CRITICAL**: Vue/Nuxt code with hallucinated patterns causes hydration mismatches, performance issues, and runtime errors. Always verify.

---

## Section 1: Overview

**Risk Level**: MEDIUM

**Expertise Areas**:
- Vue 3.4+ with Composition API and TypeScript
- Nuxt 3.10+ server-side rendering (SSR) and static site generation (SSG)
- State management with Pinia and composables
- Performance optimization and Core Web Vitals
- Client-side security (XSS, CSRF, injection attacks)
- Modern build tooling (Vite, Nitro)

**Target Users**: Frontend engineers building modern, performant, type-safe web applications

**Key Focus**: Type-safe component architecture, composable logic, SSR/SSG patterns, and client-side security

### Core Principles

1. **TDD First** - Write tests before implementation using Vitest and Vue Test Utils
2. **Performance Aware** - Optimize reactivity, use computed over methods, implement lazy loading
3. **Type Safety** - Use TypeScript strict mode with proper component and composable typing
4. **Composable-First** - Extract reusable logic into composables for maximum reusability
5. **Security-Conscious** - Prevent XSS, validate inputs, configure CSP headers
6. **SSR-Compatible** - Always consider server-side rendering implications

---

## Section 2: Implementation Workflow (TDD)

### Step 1: Write Failing Test First

Create component tests using Vitest and Vue Test Utils:
- Test component rendering with props
- Test user interactions and events
- Test computed properties and reactive state
- Use data-testid for stable selectors

```typescript
// Example: tests/components/UserCard.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import UserCard from '~/components/UserCard.vue'

describe('UserCard', () => {
  it('displays user data and emits events', async () => {
    const wrapper = mount(UserCard, {
      props: { user: { id: '1', name: 'John' } }
    })
    expect(wrapper.text()).toContain('John')
    await wrapper.trigger('click')
    expect(wrapper.emitted('select')).toBeTruthy()
  })
})
```

### Step 2: Implement Minimum Code to Pass

Write component using script setup with TypeScript:
- Type all props with `defineProps<T>()`
- Type all emits with `defineEmits<T>()`
- Use composition API patterns
- Handle loading and error states

### Step 3: Run Full Verification

```bash
npm run test      # Run all tests
npm run typecheck # Type checking
npm run lint      # Lint code
npm run build     # Verify build succeeds
```

For detailed testing patterns including composable tests, E2E tests, and mocking strategies, see [references/testing-guide.md](./references/testing-guide.md).

---

## Section 3: Core Responsibilities

### 1. Component Architecture & Composition API
- Design scalable component hierarchies using script setup syntax
- Create reusable composables following Vue 3 best practices
- Implement proper TypeScript typing for components and composables
- Manage reactivity with ref, reactive, computed, and watch
- Optimize component rendering with proper key usage and v-memo

### 2. Nuxt 3 Application Development
- Configure Nuxt 3 apps for SSR, SSG, or hybrid rendering
- Implement file-based routing with dynamic routes and middleware
- Create server routes and API endpoints with Nitro
- Optimize bundle size and code splitting
- Configure auto-imports and module layer architecture

### 3. State Management
- Design Pinia stores with proper TypeScript support
- Implement state persistence and hydration strategies
- Create shared composables for cross-component logic
- Manage global state vs local component state
- Handle async state and loading patterns

### 4. Performance Optimization
- Implement lazy loading for routes and components
- Optimize images with Nuxt Image module
- Configure caching strategies (client, server, CDN)
- Monitor and improve Core Web Vitals
- Implement virtual scrolling for large lists

### 5. Type Safety & Developer Experience
- Configure TypeScript with strict mode
- Generate types for Nuxt auto-imports
- Type API responses and store state
- Set up ESLint and Prettier for Vue/Nuxt
- Implement proper error handling and boundaries

### 6. Client-Side Security
- Prevent XSS through proper template sanitization
- Configure Content Security Policy (CSP)
- Validate and sanitize user inputs
- Implement secure authentication flows
- Protect against CSRF attacks

---

## Section 4: Key Implementation Patterns

### Pattern 1: Type-Safe Pinia Store

Use setup store syntax with TypeScript for full type inference:

```typescript
// stores/user.ts
export const useUserStore = defineStore('user', () => {
  const currentUser = ref<User | null>(null)
  const isAuthenticated = computed(() => !!currentUser.value)

  async function login(email: string, password: string) {
    const response = await $fetch<{ user: User }>('/api/auth/login', {
      method: 'POST',
      body: { email, password }
    })
    currentUser.value = response.user
  }

  return { currentUser, isAuthenticated, login }
})
```

### Pattern 2: Nuxt Middleware & Route Guards

Implement global or route-specific middleware:

```typescript
// middleware/auth.global.ts
export default defineNuxtRouteMiddleware((to) => {
  const userStore = useUserStore()
  if (!userStore.isAuthenticated && to.path !== '/login') {
    return navigateTo('/login')
  }
})
```

### Pattern 3: Server API Routes with Validation

Use Zod for runtime validation in server endpoints:

```typescript
// server/api/users/[id].post.ts
const schema = z.object({
  name: z.string().min(2),
  email: z.string().email()
})

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const result = schema.safeParse(body)
  if (!result.success) {
    throw createError({ statusCode: 400, data: result.error })
  }
  return await db.users.update(getRouterParam(event, 'id'), result.data)
})
```

### Pattern 4: SSR-Safe Data Fetching

Always use Nuxt composables for data fetching:

```vue
<script setup lang="ts">
// ✅ CORRECT: SSR-compatible
const { data: posts } = await useFetch('/api/posts', {
  key: 'posts-list',
  transform: (data) => data.posts
})

// With reactive params
const route = useRoute()
const { data: post } = await useFetch(() => `/api/posts/${route.params.id}`, {
  watch: [() => route.params.id]
})

// ❌ WRONG: Direct fetch executes twice (server + client)
// const response = await fetch('/api/posts')
</script>
```

For more patterns including advanced reactivity, VueUse integration, and complex state management, see:
- [references/composition-api-guide.md](./references/composition-api-guide.md)
- [references/nuxt-patterns.md](./references/nuxt-patterns.md)
- [references/advanced-patterns.md](./references/advanced-patterns.md)

---

## Section 5: Security

**Risk Level**: MEDIUM - Client-side applications are vulnerable to XSS, injection, and data exposure

### Top 3 Critical Vulnerabilities

#### 1. Cross-Site Scripting (XSS)
**Prevention**:
- Vue templates automatically escape HTML in `{{ }}` bindings
- Only use `v-html` with sanitized content (use DOMPurify)
- Sanitize user input on both client and server
- Configure Content Security Policy headers

```vue
<template>
  <!-- ✅ SAFE: Automatic escaping -->
  <div>{{ userInput }}</div>

  <!-- ⚠️ DANGEROUS: Only with sanitized content -->
  <div v-html="DOMPurify.sanitize(userHtml)"></div>
</template>
```

#### 2. Insecure Data Exposure
**Prevention**:
- Keep API keys and secrets in server-only code
- Use `useRuntimeConfig()` for environment variables
- Never expose secrets in client bundles
- Implement proper API authentication

```typescript
// ✅ Server API route - secrets stay on server
export default defineEventHandler(async (event) => {
  const apiKey = useRuntimeConfig().stripeSecretKey // Server-only
  return await stripe.charges.create({ amount: 1000 }, { apiKey })
})
```

#### 3. CSRF (Cross-Site Request Forgery)
**Prevention**:
- Configure CORS and security headers in nuxt.config.ts
- Use SameSite cookies for authentication
- Implement CSRF tokens for state-changing operations
- Validate origin headers on server

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  security: {
    headers: {
      crossOriginEmbedderPolicy: 'require-corp',
      crossOriginOpenerPolicy: 'same-origin'
    }
  }
})
```

For detailed security implementations including input validation, CSP configuration, and secure authentication patterns, see [references/security-examples.md](./references/security-examples.md).

---

## Section 6: Critical Reminders

### Type Safety
- Always enable TypeScript strict mode
- Type all component props with `defineProps<T>()`
- Generate types for Nuxt auto-imports: `nuxt prepare`
- Use runtime validation (Zod) for API inputs

### Performance
- Use `useFetch`/`useAsyncData` for data fetching (SSR-compatible)
- Implement lazy loading: `defineAsyncComponent()`
- Optimize images: Use Nuxt Image module
- Monitor bundle size: `nuxi analyze`
- Use `v-memo` for expensive lists

### Security
- Never use `v-html` with unsanitized user input
- Configure CSP headers in `nuxt.config.ts`
- Validate all inputs on both client and server
- Store secrets in `.env`, never in client code
- Use `httpOnly` cookies for sensitive tokens

### SSR/SSG
- Check `process.client` before accessing browser APIs
- Use Nuxt data fetching composables, not raw fetch
- Handle hydration mismatches with `<ClientOnly>`
- Set appropriate cache headers

For common mistakes, see [references/anti-patterns.md](./references/anti-patterns.md).
For performance optimization, see [references/performance-optimization.md](./references/performance-optimization.md).

---

## Section 7: Pre-Implementation Checklist

### Before Writing Code
- [ ] **Identify requirements** - Parse user story into acceptance criteria
- [ ] **Design component structure** - Sketch component hierarchy
- [ ] **Plan composables** - Identify reusable logic
- [ ] **Consider SSR** - Determine rendering strategy
- [ ] **Write test cases** - Create failing tests
- [ ] **Plan state management** - Decide local vs store state

### During Implementation
- [ ] **TDD cycle** - Write test → Implement → Refactor
- [ ] **Type everything** - Props, emits, composables, API responses
- [ ] **Use computed** - For derived state
- [ ] **Optimize reactivity** - shallowRef for large objects
- [ ] **Handle edge cases** - Loading, errors, empty data
- [ ] **SSR safety** - Check `process.client`
- [ ] **Security checks** - No v-html with user input

### Before Committing
- [ ] **All tests pass** - `npm run test`
- [ ] **Type check passes** - `npm run typecheck`
- [ ] **Lint passes** - `npm run lint`
- [ ] **Build succeeds** - `npm run build`
- [ ] **Performance check** - No warnings, smooth rendering
- [ ] **Security review** - No exposed secrets

---

## Section 8: References

See `references/` directory for detailed guides:

- **[composition-api-guide.md](./references/composition-api-guide.md)** - Composable patterns, reactivity, VueUse integration
- **[nuxt-patterns.md](./references/nuxt-patterns.md)** - Middleware, server routes, SSR, plugins, modules
- **[performance-optimization.md](./references/performance-optimization.md)** - Bundle optimization, Core Web Vitals, caching
- **[anti-patterns.md](./references/anti-patterns.md)** - Common mistakes and how to avoid them
- **[testing-guide.md](./references/testing-guide.md)** - Component, composable, and E2E testing
- **[advanced-patterns.md](./references/advanced-patterns.md)** - Advanced implementations and techniques
- **[security-examples.md](./references/security-examples.md)** - Security-focused implementations

---

## Section 9: Summary

This skill provides expertise in building modern, performant, type-safe Vue 3 and Nuxt 3 applications.

**Key Takeaways**:

**Architecture**: Design component hierarchies with Composition API, extract logic into composables, manage state with Pinia. Follow the composable-first approach for maximum reusability.

**Nuxt 3 Patterns**: Leverage file-based routing, auto-imports, and Nitro server for full-stack development. Configure rendering strategies (SSR/SSG/hybrid) per route.

**Type Safety**: Use TypeScript strict mode throughout. Type components, stores, and API responses. Combine compile-time TypeScript with runtime validation (Zod).

**Performance**: Implement strategic code splitting, lazy loading, and optimized data fetching with `useFetch`. Monitor Core Web Vitals and set performance budgets.

**Security**: Prevent XSS through proper escaping. Validate all inputs. Configure CSP headers. Keep secrets on the server. Implement CSRF protection.

**Best Practices**:
- Keep components focused and composable
- Extract and test composables independently
- Use VueUse for common patterns
- Configure ESLint and Prettier
- Write tests for critical logic
- Monitor performance and bundle size

**Risk Level**: MEDIUM - Primary concerns are client-side security (XSS, data exposure) and performance (bundle size, SSR complexity).


## 4. Quality Assurance Checklist

**Before implementing this skill, ensure**:

### 4.1 Pre-Implementation Setup
- [ ] Virtual environment created and activated
- [ ] Dependencies installed from requirements.txt
- [ ] Pre-commit hooks installed (`pre-commit install`)
- [ ] Linters installed (black, isort, flake8, mypy, bandit)

### 4.2 Dependency Management
- [ ] All dependencies pinned with exact versions (==)
- [ ] No manual transitive dependency pins
- [ ] Dependencies tested in clean environment

### 4.3 Code Quality Gates (Run BEFORE committing)
- [ ] `black .` - Code formatted
- [ ] `isort .` - Imports sorted
- [ ] `flake8 . --max-line-length=120` - No linting errors
- [ ] `mypy . --ignore-missing-imports` - Type checking passes
- [ ] `bandit -r .` - Security scan clean

### 4.4 Security Validation
- [ ] Input validation for ALL external inputs
- [ ] Path traversal prevention implemented
- [ ] Command injection prevention (no shell=True)
- [ ] SQL injection prevention (parameterized queries)
- [ ] Secrets not in code or error messages

📚 **For complete security validation guide**: See `../../../template-references/security-framework.md`

### 4.5 Test Coverage Requirements
- [ ] Tests written BEFORE implementation (TDD)
- [ ] Unit tests for all public functions
- [ ] Edge case tests (empty, null, max values)
- [ ] Security tests (injection, traversal, overflow)
- [ ] Code coverage >80%

### 4.6 Documentation Requirements
- [ ] Docstrings for all public functions/classes
- [ ] Security considerations documented
- [ ] Examples of correct usage
- [ ] Known limitations documented

---
