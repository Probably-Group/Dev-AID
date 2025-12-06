## 3. Technology Stack & Versions

### 3.1 Recommended Versions

| Package | Version | Notes |
|---------|---------|-------|
| pinia | ^2.1.0 | Latest stable |
| @pinia/nuxt | ^0.5.0 | Nuxt integration |
| pinia-plugin-persistedstate | ^3.0.0 | Optional persistence |

### 3.2 Nuxt Configuration

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  modules: ['@pinia/nuxt'],
  pinia: {
    storesDirs: ['./stores/**']
  }
})
```

### 3.3 Implementation Workflow (TDD)

Follow this workflow for every store:

**Step 1: Write Failing Test First**

```typescript
// tests/stores/metrics.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useMetricsStore } from '~/stores/metrics'

describe('MetricsStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should initialize with default values', () => {
    const store = useMetricsStore()
    expect(store.cpu).toBe(0)
    expect(store.memory).toBe(0)
  })

  it('should clamp values within valid range', () => {
    const store = useMetricsStore()
    store.updateCpu(150)
    expect(store.cpu).toBe(100)
    store.updateCpu(-50)
    expect(store.cpu).toBe(0)
  })

  it('should compute health status correctly', () => {
    const store = useMetricsStore()
    store.updateCpu(95)
    store.updateMemory(90)
    expect(store.healthStatus).toBe('critical')
  })
})
```

**Step 2: Implement Minimum to Pass**

```typescript
// stores/metrics.ts
export const useMetricsStore = defineStore('metrics', () => {
  const cpu = ref(0)
  const memory = ref(0)

  const healthStatus = computed(() => {
    const avg = (cpu.value + memory.value) / 2
    if (avg > 90) return 'critical'
    if (avg > 70) return 'warning'
    return 'healthy'
  })

  function updateCpu(value: number) {
    cpu.value = Math.max(0, Math.min(100, value))
  }

  function updateMemory(value: number) {
    memory.value = Math.max(0, Math.min(100, value))
  }

  return { cpu, memory, healthStatus, updateCpu, updateMemory }
})
```

**Step 3: Refactor Following Patterns**

- Extract validation logic
- Add TypeScript interfaces
- Optimize computed dependencies

**Step 4: Run Full Verification**

```bash
npm run test -- --filter=stores
npm run typecheck
npm run build
```


