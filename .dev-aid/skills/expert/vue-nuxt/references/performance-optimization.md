# Vue 3 / Nuxt 3 Performance Optimization

This document contains comprehensive performance optimization patterns for Vue 3 and Nuxt 3 applications, particularly for 3D HUD interfaces.

## 1. Computed Properties for Derived State

```typescript
// ❌ BAD - Recalculates in template on every render
<template>
  <div>{{ items.filter(i => i.active).length }} active</div>
</template>

// ✅ GOOD - Cached until dependencies change
const activeCount = computed(() => items.value.filter(i => i.active).length)
<template>
  <div>{{ activeCount }} active</div>
</template>
```

### Why This Matters
- Template expressions re-evaluate on every render
- Computed properties cache results and only recalculate when dependencies change
- Especially important for expensive operations like filtering, sorting, or calculations

### Best Practices
```typescript
// ✅ Complex derived state with multiple dependencies
const filteredAndSortedItems = computed(() => {
  return items.value
    .filter(item => item.status === filter.value)
    .sort((a, b) => a.priority - b.priority)
})

// ✅ Chaining computed properties
const activeItems = computed(() => items.value.filter(i => i.active))
const activeCount = computed(() => activeItems.value.length)
const hasActiveItems = computed(() => activeCount.value > 0)
```

## 2. shallowRef for Large Objects

```typescript
// ❌ BAD - Deep reactivity on large 3D data
const meshData = ref<MeshData>({ vertices: new Float32Array(100000), ... })

// ✅ GOOD - Shallow reactivity, manual trigger
const meshData = shallowRef<MeshData>({ vertices: new Float32Array(100000), ... })
// Trigger update explicitly
meshData.value = { ...newData }
triggerRef(meshData)
```

### When to Use shallowRef
- Large arrays or typed arrays (Float32Array, etc.)
- 3D mesh data with many vertices
- Large objects where you control updates
- Data structures with frequent deep mutations

### Performance Impact
```typescript
// ❌ Deep reactivity overhead
const largeArray = ref(new Array(10000).fill({}))
// Creates thousands of reactive proxy objects

// ✅ Shallow reactivity
const largeArray = shallowRef(new Array(10000).fill({}))
// Creates single reactive wrapper
```

### Related APIs
```typescript
// shallowReactive for objects
const state = shallowReactive({
  data: new Float32Array(100000),
  metadata: { count: 0 }
})

// triggerRef to force update
triggerRef(meshData)

// shallowReadonly for read-only data
const config = shallowReadonly({ settings: largeConfig })
```

## 3. defineAsyncComponent for Lazy Loading

```typescript
// ❌ BAD - All components loaded upfront
import HeavyChart from '@/components/HeavyChart.vue'

// ✅ GOOD - Load only when needed
const HeavyChart = defineAsyncComponent(() =>
  import('@/components/HeavyChart.vue')
)

// With loading state
const HeavyChart = defineAsyncComponent({
  loader: () => import('@/components/HeavyChart.vue'),
  loadingComponent: LoadingSpinner,
  delay: 200
})
```

### Advanced Configuration
```typescript
const HeavyComponent = defineAsyncComponent({
  loader: () => import('@/components/HeavyComponent.vue'),
  loadingComponent: LoadingSpinner,
  errorComponent: ErrorDisplay,
  delay: 200,        // Delay before showing loading component
  timeout: 3000,     // Timeout for loading
  suspensible: true, // Use with Suspense
  onError(error, retry, fail, attempts) {
    if (attempts <= 3) {
      retry()  // Retry on failure
    } else {
      fail()
    }
  }
})
```

### Route-Level Code Splitting
```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  // Enable automatic code splitting
  vite: {
    build: {
      rollupOptions: {
        output: {
          manualChunks: {
            'three': ['three', '@tresjs/core'],
            'charts': ['chart.js', 'vue-chartjs']
          }
        }
      }
    }
  }
})
```

## 4. v-memo for List Optimization

```vue
<!-- ❌ BAD - Re-renders all items on any change -->
<div v-for="item in items" :key="item.id">
  <ExpensiveComponent :data="item" />
</div>

<!-- ✅ GOOD - Skip re-render if item unchanged -->
<div v-for="item in items" :key="item.id" v-memo="[item.id, item.updated]">
  <ExpensiveComponent :data="item" />
</div>
```

### v-memo Best Practices
```vue
<!-- ✅ Memoize with multiple dependencies -->
<div
  v-for="item in items"
  :key="item.id"
  v-memo="[item.id, item.status, item.priority]"
>
  <ComplexItem :data="item" />
</div>

<!-- ✅ Conditional memoization -->
<div
  v-for="item in items"
  :key="item.id"
  v-memo="item.isStatic ? [item.id] : undefined"
>
  <DynamicItem :data="item" />
</div>

<!-- ✅ Memoize entire component -->
<ComplexDashboard v-memo="[userId, timestamp]" />
```

### When v-memo Helps Most
- Long lists with complex child components
- Items that update infrequently
- Expensive render operations
- Components with heavy computed properties

## 5. Virtual Scrolling for Long Lists

```vue
<script setup lang="ts">
import { useVirtualList } from '@vueuse/core'

const { list, containerProps, wrapperProps } = useVirtualList(
  items,
  { itemHeight: 50 }
)
</script>

<template>
  <!-- ✅ Only renders visible items -->
  <div v-bind="containerProps" class="h-[400px] overflow-auto">
    <div v-bind="wrapperProps">
      <div v-for="{ data, index } in list" :key="index">
        {{ data.name }}
      </div>
    </div>
  </div>
</template>
```

### Variable Height Items
```typescript
import { useVirtualList } from '@vueuse/core'

// Dynamic item heights
const { list, containerProps, wrapperProps } = useVirtualList(
  items,
  {
    itemHeight: (index) => {
      // Calculate height based on item content
      return items.value[index].isExpanded ? 200 : 50
    },
    overscan: 5  // Render 5 extra items for smooth scrolling
  }
)
```

### Performance Comparison
```
Without virtual scrolling (1000 items):
- DOM nodes: 1000+
- Initial render: 500-1000ms
- Memory: High

With virtual scrolling (1000 items):
- DOM nodes: ~20 (only visible)
- Initial render: 50-100ms
- Memory: Low
```

## 6. Debounced Watchers

```typescript
// ❌ BAD - Fires on every keystroke
watch(searchQuery, async (query) => {
  results.value = await searchAPI(query)
})

// ✅ GOOD - Debounced to reduce API calls
import { watchDebounced } from '@vueuse/core'

watchDebounced(
  searchQuery,
  async (query) => {
    results.value = await searchAPI(query)
  },
  { debounce: 300 }
)

// Alternative with manual debounce
watch(searchQuery, useDebounceFn(async (query) => {
  results.value = await searchAPI(query)
}, 300))
```

### Advanced Debouncing Patterns
```typescript
// ✅ Debounce with throttle for real-time updates
import { watchThrottled } from '@vueuse/core'

watchThrottled(
  mousPosition,
  (pos) => {
    updateCursor(pos)
  },
  { throttle: 16 }  // ~60fps
)

// ✅ Debounce with immediate first call
import { useDebounceFn } from '@vueuse/core'

const debouncedSearch = useDebounceFn(
  async (query) => {
    results.value = await searchAPI(query)
  },
  300,
  { maxWait: 1000 }  // Force execution after 1s
)
```

## 7. Efficient Reactivity Patterns

### Use markRaw for Non-Reactive Data
```typescript
// ❌ BAD - Three.js objects made reactive unnecessarily
const scene = ref(new THREE.Scene())

// ✅ GOOD - Mark as raw to skip reactivity
const scene = markRaw(new THREE.Scene())
const camera = markRaw(new THREE.PerspectiveCamera())

// Store in shallowRef if you need reactivity for replacement
const scene = shallowRef(markRaw(new THREE.Scene()))
```

### Batch Updates with nextTick
```typescript
// ❌ BAD - Multiple reactive updates
const updateMetrics = (newData) => {
  metrics.cpu = newData.cpu        // Trigger 1
  metrics.memory = newData.memory  // Trigger 2
  metrics.disk = newData.disk      // Trigger 3
}

// ✅ GOOD - Single batched update
const updateMetrics = async (newData) => {
  metrics.cpu = newData.cpu
  metrics.memory = newData.memory
  metrics.disk = newData.disk
  await nextTick()  // All updates batched
  // DOM is now updated
}

// ✅ BETTER - Use Object.assign for objects
const updateMetrics = (newData) => {
  Object.assign(metrics, newData)  // Single update
}
```

## 8. Nuxt-Specific Optimizations

### Server-Side Rendering (SSR) Optimization
```typescript
// ✅ Minimize client-side hydration
const { data } = await useAsyncData('posts', () => $fetch('/api/posts'))

// ✅ Client-only heavy components
<ClientOnly>
  <Heavy3DRenderer />
  <template #fallback>
    <LoadingState />
  </template>
</ClientOnly>

// ✅ Lazy hydration
const LazyComponent = defineAsyncComponent({
  loader: () => import('@/components/Heavy.vue'),
  hydrate: 'whenIdle'  // Hydrate during browser idle time
})
```

### Route Prefetching
```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  experimental: {
    payloadExtraction: true  // Extract page payloads
  },
  router: {
    prefetchLinks: true  // Prefetch on hover
  }
})
```

### Image Optimization
```vue
<!-- ✅ Use Nuxt Image for automatic optimization -->
<NuxtImg
  src="/large-image.jpg"
  width="800"
  height="600"
  loading="lazy"
  format="webp"
/>

<!-- ✅ Responsive images -->
<NuxtPicture
  src="/hero.jpg"
  :imgAttrs="{ alt: 'Hero image' }"
  sizes="sm:100vw md:50vw lg:400px"
/>
```

## 9. Build-Time Optimizations

### Vite Configuration
```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  vite: {
    build: {
      // Enable compression
      minify: 'terser',
      terserOptions: {
        compress: {
          drop_console: true,  // Remove console.logs
          drop_debugger: true
        }
      },
      // Chunk size optimization
      chunkSizeWarningLimit: 1000,
      rollupOptions: {
        output: {
          manualChunks: {
            'vendor': ['vue', 'vue-router'],
            'three': ['three']
          }
        }
      }
    },
    // Enable CSS code splitting
    css: {
      devSourcemap: false
    }
  }
})
```

### Tree Shaking
```typescript
// ✅ Import only what you need
import { computed, ref } from 'vue'  // ✅
import * as Vue from 'vue'           // ❌

import { debounce } from 'lodash-es' // ✅
import _ from 'lodash'               // ❌
```

## 10. Monitoring Performance

### Use Performance API
```typescript
// Measure component render time
const measureRender = () => {
  performance.mark('render-start')

  onMounted(() => {
    performance.mark('render-end')
    performance.measure('component-render', 'render-start', 'render-end')

    const measure = performance.getEntriesByName('component-render')[0]
    console.log(`Render time: ${measure.duration}ms`)
  })
}
```

### Vue DevTools Performance
```typescript
// Enable performance tracking
if (process.env.NODE_ENV === 'development') {
  app.config.performance = true
}
```

## Performance Checklist

- [ ] Use computed properties for derived state
- [ ] Use shallowRef/shallowReactive for large data
- [ ] Implement lazy loading for heavy components
- [ ] Use v-memo for expensive list items
- [ ] Implement virtual scrolling for long lists (>100 items)
- [ ] Debounce user input handlers
- [ ] Mark non-reactive objects with markRaw
- [ ] Use ClientOnly for client-side-only components
- [ ] Configure proper code splitting
- [ ] Enable image optimization
- [ ] Monitor performance metrics
