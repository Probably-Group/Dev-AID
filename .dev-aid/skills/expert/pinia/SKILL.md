---
name: pinia
description: Pinia state management for JARVIS system state
risk_level: MEDIUM
version: 1.0.0
---

# Pinia State Management Skill

> **File Organization**: This skill uses split structure. See `references/` for advanced patterns and security examples.


### 0.4 Progressive Disclosure (500-Line Limit)

**⚠️ CRITICAL**: This SKILL.md file MUST stay <500 lines for Claude Code to load it.

**If this file is approaching 500 lines**:
- Move detailed examples to `references/advanced-patterns.md`
- Move security examples to `references/security-examples.md`
- Move troubleshooting to `references/troubleshooting.md`
- Keep only summaries and links in main file

📚 **For complete progressive disclosure guide**: See `../../../template-references/progressive-disclosure.md`

---

## 1. Overview

This skill provides Pinia expertise for managing application state in the JARVIS AI Assistant, including system metrics, user preferences, and HUD configuration.

**Risk Level**: MEDIUM - Manages sensitive state, SSR considerations, potential data exposure

**Primary Use Cases**:
- System metrics and status tracking
- User preferences and settings
- HUD configuration state
- Command history and queue
- Real-time data synchronization

## 2. Core Responsibilities

### 2.1 Core Principles

1. **TDD First**: Write store tests before implementation
2. **Performance Aware**: Optimize subscriptions and computed values
3. **Type Safety**: Define stores with full TypeScript typing
4. **SSR Security**: Prevent state leakage between requests
5. **Composition API**: Use setup stores for better TypeScript support
6. **Minimal State**: Store only necessary data, derive the rest
7. **Action Validation**: Validate inputs in actions before mutations
8. **Persistence Security**: Never persist sensitive data to localStorage

## 3. Technology Stack & Versions

| Package | Version | Notes |
|---------|---------|-------|
| pinia | ^2.1.0 | Latest stable |
| @pinia/nuxt | ^0.5.0 | Nuxt integration |
| pinia-plugin-persistedstate | ^3.0.0 | Optional persistence |

📚 **For complete details**: See `references/technology-stack-versions.md`

---
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

## 5. Implementation Patterns

### 4.1 Setup Store with TypeScript

```typescript
// stores/jarvis.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

interface SystemMetrics {
  cpu: number
  memory: number
  network: number
  timestamp: number
}

interface JARVISState {
  status: 'idle' | 'listening' | 'processing' | 'responding'
  securityLevel: 'normal' | 'elevated' | 'lockdown'
}

export const useJarvisStore = defineStore('jarvis', () => {
  // State
  const state = ref<JARVISState>({
    status: 'idle',
    securityLevel: 'normal'
  })

  const metrics = ref<SystemMetrics>({
    cpu: 0,
    memory: 0,
    network: 0,
    timestamp: Date.now()
  })

  // Getters
  const isActive = computed(() =>
    state.value.status !== 'idle'
  )

  const systemHealth = computed(() => {
    const avg = (metrics.value.cpu + metrics.value.memory) / 2
    if (avg > 90) return 'critical'
    if (avg > 70) return 'warning'
    return 'healthy'
  })

  // Actions
  function updateMetrics(newMetrics: Partial<SystemMetrics>) {
    // ✅ Validate input
    if (newMetrics.cpu !== undefined) {
      metrics.value.cpu = Math.max(0, Math.min(100, newMetrics.cpu))
    }
    if (newMetrics.memory !== undefined) {
      metrics.value.memory = Math.max(0, Math.min(100, newMetrics.memory))
    }
    if (newMetrics.network !== undefined) {
      metrics.value.network = Math.max(0, newMetrics.network)
    }
    metrics.value.timestamp = Date.now()
  }

  function setStatus(newStatus: JARVISState['status']) {
    state.value.status = newStatus
  }

  function setSecurityLevel(level: JARVISState['securityLevel']) {
    state.value.securityLevel = level

    // ✅ Audit security changes
    console.info(`Security level changed to: ${level}`)
  }

  return {
    state,
    metrics,
    isActive,
    systemHealth,
    updateMetrics,
    setStatus,
    setSecurityLevel
  }
})
```

### 4.2 User Preferences Store (with Persistence)

```typescript
// stores/preferences.ts
## 5. Implementation Patterns

interface SystemMetrics {
  cpu: number
  memory: number
  network: number
  timestamp: number
}

📚 **For complete details**: See `references/implementation-patterns.md`

---
tore()
  }
  return heavyStore.value
}
```

### Pattern 5: Optimistic Updates

```typescript
// BAD - Wait for server response
async function deleteItem(id: string) {
  await api.delete(`/items/${id}`)
  items.value = items.value.filter(i => i.id !== id)
}

// GOOD - Update immediately, rollback on error
async function deleteItem(id: string) {
  const backup = [...items.value]
  items.value = items.value.filter(i => i.id !== id)

  try {
    await api.delete(`/items/${id}`)
  } catch (error) {
    items.value = backup  // Rollback
    throw error
  }
}
```

## 7. Testing & Quality

See **Section 3.3** for complete TDD workflow with vitest examples.

## 9. Common Anti-Patterns

### Security Anti-Patterns

```typescript
// ❌ Global state leaks between SSR users
const state = reactive({ user: null })

// ✅ Pinia isolates per-request
export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  return { user }
})

// ❌ Never persist auth tokens (XSS risk)
persist: { paths: ['authToken'] }

// ✅ Use httpOnly cookies for auth
```

### Performance Anti-Patterns

See **Section 5.5** for detailed performance patterns with Good/Bad examples.

## 14. Pre-Implementation Checklist

### Phase 1: Before Writing Code

- [ ] Store interface designed with TypeScript types
- [ ] Test file created with failing tests
- [ ] Security requirements identified (persistence, SSR)
- [ ] Performance patterns selected for use case

### Phase 2: During Implementation

- [ ] Tests passing after each feature added
- [ ] Actions validate all inputs
- [ ] Computed values use minimal dependencies
- [ ] No sensitive data in persisted state
- [ ] SSR state properly isolated

### Phase 3: Before Committing

- [ ] All store tests passing: `npm run test -- --filter=stores`
- [ ] Type check passing: `npm run typecheck`
- [ ] Build succeeds: `npm run build`
- [ ] No global state outside Pinia
- [ ] State shape documented in types

## 15. Summary

Pinia provides type-safe state management for JARVIS:

1. **TDD First**: Write store tests before implementation
2. **Performance**: Optimize subscriptions and computed values
3. **Security**: Never persist sensitive data, isolate SSR state
4. **Type Safety**: Use setup stores with full TypeScript

**References**: See `references/` for advanced patterns and security examples.
