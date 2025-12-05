# Vue 3 & Nuxt 3 Performance Optimization

This guide covers performance optimization patterns for Vue 3 and Nuxt 3 applications.

---

## Pattern 1: Use Computed Over Methods

**Bad - Method called on every render:**
```vue
<script setup lang="ts">
const items = ref([...])

// ❌ BAD: Recalculates on every render
const getFilteredItems = () => {
  return items.value.filter(item => item.active)
}
</script>

<template>
  <div v-for="item in getFilteredItems()" :key="item.id">
    {{ item.name }}
  </div>
</template>
```

**Good - Computed caches result:**
```vue
<script setup lang="ts">
const items = ref([...])

// ✅ GOOD: Only recalculates when items change
const filteredItems = computed(() => {
  return items.value.filter(item => item.active)
})
</script>

<template>
  <div v-for="item in filteredItems" :key="item.id">
    {{ item.name }}
  </div>
</template>
```

---

## Pattern 2: Use shallowRef for Large Objects

**Bad - Deep reactivity on large objects:**
```typescript
// ❌ BAD: Creates deep reactive proxy for entire object
const largeDataset = ref<DataItem[]>([])

// Every nested property becomes reactive
largeDataset.value = await fetchLargeDataset()
```

**Good - Shallow reactivity when deep tracking not needed:**
```typescript
// ✅ GOOD: Only tracks the reference, not nested properties
const largeDataset = shallowRef<DataItem[]>([])

// Manually trigger updates
largeDataset.value = await fetchLargeDataset()

// Use triggerRef for in-place mutations
largeDataset.value.push(newItem)
triggerRef(largeDataset)
```

---

## Pattern 3: Use v-memo for Expensive Lists

**Bad - Re-renders all items on any change:**
```vue
<template>
  <!-- ❌ BAD: All items re-render when anything changes -->
  <div v-for="item in items" :key="item.id">
    <ExpensiveComponent :data="item" />
  </div>
</template>
```

**Good - Memoize items that haven't changed:**
```vue
<template>
  <!-- ✅ GOOD: Only re-renders when item.id or item.updated changes -->
  <div
    v-for="item in items"
    :key="item.id"
    v-memo="[item.id, item.updated]"
  >
    <ExpensiveComponent :data="item" />
  </div>
</template>
```

---

## Pattern 4: Lazy Load Components

**Bad - All components loaded upfront:**
```vue
<script setup lang="ts">
// ❌ BAD: Imported even if never shown
import HeavyChart from '~/components/HeavyChart.vue'
import AdminPanel from '~/components/AdminPanel.vue'
import DataTable from '~/components/DataTable.vue'
</script>
```

**Good - Components loaded on demand:**
```vue
<script setup lang="ts">
// ✅ GOOD: Only loaded when rendered
const HeavyChart = defineAsyncComponent(() =>
  import('~/components/HeavyChart.vue')
)

const AdminPanel = defineAsyncComponent({
  loader: () => import('~/components/AdminPanel.vue'),
  loadingComponent: LoadingSpinner,
  delay: 200,
  timeout: 5000
})

// With Nuxt lazy prefix
// components/lazy/DataTable.vue automatically becomes lazy
</script>

<template>
  <HeavyChart v-if="showChart" />
  <AdminPanel v-if="isAdmin" />
  <LazyDataTable v-if="showTable" />
</template>
```

---

## Pattern 5: Virtual Scrolling for Large Lists

**Bad - Render all items at once:**
```vue
<template>
  <!-- ❌ BAD: Renders 10,000 DOM nodes -->
  <div v-for="item in tenThousandItems" :key="item.id">
    {{ item.name }}
  </div>
</template>
```

**Good - Only render visible items:**
```vue
<script setup lang="ts">
import { useVirtualList } from '@vueuse/core'

const items = ref(generateLargeList(10000))

const { list, containerProps, wrapperProps } = useVirtualList(items, {
  itemHeight: 50,
  overscan: 5
})
</script>

<template>
  <!-- ✅ GOOD: Only renders ~20 visible items -->
  <div v-bind="containerProps" class="h-[400px] overflow-auto">
    <div v-bind="wrapperProps">
      <div v-for="{ data, index } in list" :key="index" class="h-[50px]">
        {{ data.name }}
      </div>
    </div>
  </div>
</template>
```

---

## Pattern 6: Optimize Watchers

**Bad - Watch entire object unnecessarily:**
```typescript
// ❌ BAD: Triggers on any property change
watch(form, () => {
  validateForm()
}, { deep: true })
```

**Good - Watch specific properties:**
```typescript
// ✅ GOOD: Only triggers when email changes
watch(() => form.email, (newEmail) => {
  validateEmail(newEmail)
})

// ✅ GOOD: Watch multiple specific props
watch(
  [() => form.email, () => form.password],
  ([email, password]) => {
    validateCredentials(email, password)
  }
)
```

---

## Pattern 7: Debounce Expensive Operations

**Bad - Run on every keystroke:**
```vue
<script setup lang="ts">
const searchQuery = ref('')

// ❌ BAD: API call on every keystroke
watch(searchQuery, async (query) => {
  results.value = await searchAPI(query)
})
</script>
```

**Good - Debounce the operation:**
```vue
<script setup lang="ts">
import { useDebounceFn } from '@vueuse/core'

const searchQuery = ref('')

// ✅ GOOD: Wait for user to stop typing
const debouncedSearch = useDebounceFn(async (query: string) => {
  results.value = await searchAPI(query)
}, 300)

watch(searchQuery, (query) => {
  debouncedSearch(query)
})
</script>
```

---

## Pattern 8: Optimized Component Loading

**Implement strategic code splitting and lazy loading:**

```vue
<script setup lang="ts">
// Lazy load heavy components
const HeavyChart = defineAsyncComponent(() =>
  import('~/components/HeavyChart.vue')
)

const AdminPanel = defineAsyncComponent({
  loader: () => import('~/components/AdminPanel.vue'),
  loadingComponent: () => h('div', 'Loading...'),
  delay: 200,
  timeout: 3000
})

const showChart = ref(false)
const userStore = useUserStore()

// Only load when needed
const loadChart = () => {
  showChart.value = true
}
</script>

<template>
  <div>
    <button @click="loadChart">Show Chart</button>

    <!-- Component only loads when showChart is true -->
    <HeavyChart v-if="showChart" :data="chartData" />

    <!-- Admin panel only for admins -->
    <AdminPanel v-if="userStore.hasRole('admin')" />
  </div>
</template>
```

**Nuxt configuration for optimal splitting:**

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  vite: {
    build: {
      rollupOptions: {
        output: {
          manualChunks: {
            'vendor-vue': ['vue', 'vue-router', 'pinia'],
            'vendor-ui': ['@headlessui/vue', '@heroicons/vue'],
          }
        }
      }
    }
  },

  experimental: {
    payloadExtraction: true, // Extract payload for better caching
    componentIslands: true    // Islands architecture for partial hydration
  }
})
```

---

## Pattern 9: Core Web Vitals Optimization

### Optimize Largest Contentful Paint (LCP)

```vue
<script setup lang="ts">
// Preload critical images
useHead({
  link: [
    {
      rel: 'preload',
      as: 'image',
      href: '/hero-image.webp'
    }
  ]
})
</script>

<template>
  <!-- Use Nuxt Image for optimization -->
  <NuxtImg
    src="/hero-image.jpg"
    format="webp"
    loading="eager"
    fetchpriority="high"
    width="1200"
    height="600"
    alt="Hero image"
  />
</template>
```

### Minimize Cumulative Layout Shift (CLS)

```vue
<template>
  <!-- Always specify dimensions -->
  <img
    src="/image.jpg"
    width="800"
    height="600"
    alt="Description"
  />

  <!-- Use aspect-ratio for responsive images -->
  <div class="aspect-w-16 aspect-h-9">
    <NuxtImg src="/video-thumbnail.jpg" />
  </div>

  <!-- Reserve space for dynamic content -->
  <div class="min-h-[200px]">
    <AsyncContent />
  </div>
</template>
```

### Optimize First Input Delay (FID)

```typescript
// Defer non-critical JavaScript
export default defineNuxtConfig({
  app: {
    head: {
      script: [
        {
          src: '/analytics.js',
          defer: true
        }
      ]
    }
  }
})

// Use requestIdleCallback for non-urgent tasks
onMounted(() => {
  if ('requestIdleCallback' in window) {
    requestIdleCallback(() => {
      // Non-critical initialization
      initAnalytics()
    })
  } else {
    setTimeout(() => {
      initAnalytics()
    }, 1)
  }
})
```

---

## Bundle Size Optimization

### Analyze Bundle

```bash
# Generate bundle analysis
nuxi analyze

# Check bundle size
nuxi build --analyze
```

### Tree Shaking

```typescript
// ✅ GOOD: Import only what you need
import { ref, computed } from 'vue'
import { debounce } from 'lodash-es'

// ❌ BAD: Imports entire library
import _ from 'lodash'
```

### Dynamic Imports

```typescript
// Route-level code splitting
const routes = [
  {
    path: '/admin',
    component: () => import('~/pages/admin.vue')
  }
]

// Component-level splitting
const HeavyComponent = defineAsyncComponent(() =>
  import('~/components/HeavyComponent.vue')
)
```

---

## SSR Performance

### Enable Caching

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  routeRules: {
    // Cache static pages
    '/about': { swr: 3600 },
    // Cache API routes
    '/api/**': { cache: { maxAge: 60 } },
    // ISR (Incremental Static Regeneration)
    '/blog/**': { swr: true }
  }
})
```

### Reduce Server-Side Processing

```vue
<script setup lang="ts">
// Use lazy loading for non-critical data
const { data: comments } = await useLazyFetch('/api/comments')

// Defer client-side hydration
const { data: ads } = await useFetch('/api/ads', {
  server: false // Only fetch on client
})
</script>
```

---

## Memory Management

### Clean Up Event Listeners

```typescript
// ✅ CORRECT: Clean up in onUnmounted
onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

// ✅ BETTER: Use VueUse composable
import { useEventListener } from '@vueuse/core'
useEventListener(window, 'resize', handleResize) // Auto cleanup!
```

### Avoid Memory Leaks

```typescript
// ❌ BAD: Creates memory leak
const interval = setInterval(() => {
  // Do something
}, 1000)

// ✅ GOOD: Clean up interval
const interval = setInterval(() => {
  // Do something
}, 1000)

onUnmounted(() => {
  clearInterval(interval)
})

// ✅ BETTER: Use VueUse
import { useIntervalFn } from '@vueuse/core'
const { pause, resume } = useIntervalFn(() => {
  // Do something
}, 1000)
```

---

## Performance Monitoring

### Track Core Web Vitals

```typescript
// composables/useWebVitals.ts
import { onCLS, onFID, onLCP, onFCP, onTTFB } from 'web-vitals'

export function useWebVitals() {
  onMounted(() => {
    onCLS(console.log)
    onFID(console.log)
    onLCP(console.log)
    onFCP(console.log)
    onTTFB(console.log)
  })
}
```

### Monitor Performance

```typescript
// plugins/performance.client.ts
export default defineNuxtPlugin(() => {
  if (process.client && 'PerformanceObserver' in window) {
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        // Send to analytics
        console.log(entry.name, entry.duration)
      }
    })

    observer.observe({ entryTypes: ['measure', 'navigation'] })
  }
})
```
