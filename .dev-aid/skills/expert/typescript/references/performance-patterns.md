## 7. Performance Patterns

### 6.1 Memoization

```typescript
// ❌ BAD - Recalculates on every render
const processed = data.map(item => heavyTransform(item))

// ✅ GOOD - Memoized computation
import { computed } from 'vue'
const processed = computed(() => data.value.map(item => heavyTransform(item)))
```

### 6.2 Lazy Loading

```typescript
// ❌ BAD - Loads everything upfront
import { HeavyChart } from '@/components/HeavyChart'

// ✅ GOOD - Lazy load heavy components
import { defineAsyncComponent } from 'vue'
const HeavyChart = defineAsyncComponent(() => import('@/components/HeavyChart'))
```

### 6.3 Debounce/Throttle

```typescript
// ❌ BAD - API call on every keystroke
const handleSearch = (q: string) => fetchResults(q)

// ✅ GOOD - Debounced search (300ms delay)
import { useDebounceFn } from '@vueuse/core'
const debouncedSearch = useDebounceFn((q: string) => fetchResults(q), 300)
```

### 6.4 Efficient Data Structures

```typescript
// ❌ BAD - O(n) lookup
const user = users.find(u => u.id === id)

// ✅ GOOD - O(1) lookup with Map
const userMap = new Map(users.map(u => [u.id, u]))
const user = userMap.get(id)

// ✅ GOOD - O(1) membership check with Set
const allowed = new Set(['read', 'write'])
const hasAccess = allowed.has(permission)
```

### 6.5 Parallel Async Operations

```typescript
// ❌ BAD - Sequential (total = sum of times)
const user = await fetchUser()
const metrics = await fetchMetrics()

// ✅ GOOD - Parallel (total = max of times)
const [user, metrics] = await Promise.all([fetchUser(), fetchMetrics()])

// ✅ GOOD - With error handling
const results = await Promise.allSettled([fetchUser(), fetchMetrics()])
```

