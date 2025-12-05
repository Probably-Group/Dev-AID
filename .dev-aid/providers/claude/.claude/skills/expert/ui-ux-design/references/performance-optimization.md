# UI/UX Performance Optimization

## Pattern 1: Lazy Loading Components

**Use Case**: Reduce initial bundle size by loading off-screen or non-critical components on demand.

**Bad Example**:
```typescript
// Loads all components upfront
import HeavyWidget from '@/components/HeavyWidget.vue'
import DataChart from '@/components/DataChart.vue'
import VideoPlayer from '@/components/VideoPlayer.vue'
```

**Good Example**:
```typescript
// Lazy load off-screen components
const HeavyWidget = defineAsyncComponent(() =>
  import('@/components/HeavyWidget.vue')
)

const DataChart = defineAsyncComponent({
  loader: () => import('@/components/DataChart.vue'),
  loadingComponent: ChartSkeleton,
  delay: 200
})

const VideoPlayer = defineAsyncComponent({
  loader: () => import('@/components/VideoPlayer.vue'),
  loadingComponent: PlayerSkeleton,
  errorComponent: PlayerError,
  delay: 200,
  timeout: 10000
})
```

**Benefits**:
- Reduces initial JavaScript bundle size
- Faster initial page load
- Better First Contentful Paint (FCP) scores
- Progressive loading improves perceived performance

---

## Pattern 2: Image Optimization

**Use Case**: Serve optimized, responsive images with modern formats and lazy loading.

**Bad Example**:
```vue
<!-- Unoptimized images -->
<img src="/hero.png" />
<img src="/large-photo.jpg" />
```

**Good Example**:
```vue
<!-- Optimized with lazy loading and sizing -->
<template>
  <picture>
    <source
      srcset="/hero.avif"
      type="image/avif"
    />
    <source
      srcset="/hero.webp"
      type="image/webp"
    />
    <img
      src="/hero.png"
      alt="Hero image"
      loading="lazy"
      decoding="async"
      width="800"
      height="600"
    />
  </picture>
</template>
```

**Best Practices**:
- Use modern formats (AVIF, WebP) with fallbacks
- Always specify width and height to prevent layout shift
- Use `loading="lazy"` for below-the-fold images
- Use `decoding="async"` to prevent blocking rendering
- Provide appropriate `alt` text for accessibility
- Use responsive images with `srcset` for different screen sizes

---

## Pattern 3: Critical CSS Inlining

**Use Case**: Inline critical above-the-fold CSS to eliminate render-blocking requests.

**Bad Example**:
```typescript
// All styles in one bundle - blocks rendering
import './styles/all.css'
import './styles/components.css'
import './styles/utilities.css'
```

**Good Example**:
```typescript
// In nuxt.config.ts or vite.config.ts
export default defineNuxtConfig({
  css: ['~/assets/css/critical.css'],
  app: {
    head: {
      link: [
        {
          rel: 'preload',
          href: '/styles/non-critical.css',
          as: 'style',
          onload: "this.onload=null;this.rel='stylesheet'"
        }
      ]
    }
  }
})
```

**Implementation Steps**:
1. Identify critical above-the-fold styles
2. Inline critical CSS in `<head>`
3. Async load non-critical CSS
4. Use tools like `critical` or `critters` to automate extraction

**Critical CSS Should Include**:
- Layout structure for above-the-fold content
- Typography for visible text
- Colors and backgrounds
- Basic button styles

**Defer Everything Else**:
- Below-the-fold component styles
- Animation keyframes
- Print styles
- Third-party widget styles

---

## Pattern 4: Skeleton Screens

**Use Case**: Provide visual feedback during loading to improve perceived performance.

**Bad Example**:
```vue
<!-- Spinner or blank state -->
<template>
  <div v-if="loading">
    <Spinner />
  </div>
  <div v-else>
    <UserCard :user="data" />
  </div>
</template>
```

**Good Example**:
```vue
<!-- Skeleton matching content shape -->
<template>
  <div v-if="loading" class="skeleton-container">
    <div class="skeleton skeleton-avatar" />
    <div class="skeleton skeleton-text w-3/4" />
    <div class="skeleton skeleton-text w-1/2" />
    <div class="skeleton skeleton-text w-full" />
  </div>
  <div v-else>
    <UserCard :user="data" />
  </div>
</template>

<style scoped>
.skeleton {
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.06) 25%,
    rgba(255, 255, 255, 0.12) 50%,
    rgba(255, 255, 255, 0.06) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

.skeleton-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
}

.skeleton-text {
  height: 16px;
  margin: 8px 0;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
```

**Benefits**:
- Users perceive faster loading
- Reduces perceived wait time by up to 30%
- Matches final content layout
- More sophisticated than spinners

---

## Pattern 5: Progressive Enhancement

**Use Case**: Provide base functionality for all users, enhance for capable devices.

**Bad Example**:
```vue
<!-- All-or-nothing rendering -->
<template>
  <ComplexAnimation v-if="supportsWebGL" />
  <div v-else>Your browser doesn't support this feature</div>
</template>
```

**Good Example**:
```vue
<!-- Progressive enhancement -->
<template>
  <div class="hero-section">
    <!-- Base: works everywhere -->
    <StaticHero :content="heroData" />

    <!-- Enhanced: CSS animations -->
    <Transition v-if="prefersMotion" name="fade">
      <CSSAnimatedHero :content="heroData" />
    </Transition>

    <!-- Premium: WebGL effects -->
    <ClientOnly>
      <WebGLHero
        v-if="supportsWebGL && prefersMotion && !reducedData"
        :content="heroData"
      />
    </ClientOnly>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const prefersMotion = ref(true)
const supportsWebGL = ref(false)
const reducedData = ref(false)

onMounted(() => {
  // Check motion preference
  prefersMotion.value = !window.matchMedia(
    '(prefers-reduced-motion: reduce)'
  ).matches

  // Check WebGL support
  supportsWebGL.value = (() => {
    try {
      const canvas = document.createElement('canvas')
      return !!canvas.getContext('webgl2')
    } catch {
      return false
    }
  })()

  // Check data saver mode
  reducedData.value = 'connection' in navigator &&
    (navigator.connection as any)?.saveData === true
})
</script>
```

**Enhancement Layers**:
1. **Base**: Static HTML/CSS - works everywhere
2. **Enhanced**: CSS animations - works on modern browsers
3. **Premium**: WebGL/Canvas - works on powerful devices

**Progressive Enhancement Checklist**:
- [ ] Core content accessible without JavaScript
- [ ] Basic styles work without modern CSS features
- [ ] Interactive features degrade gracefully
- [ ] Check for feature support before using advanced APIs
- [ ] Respect user preferences (motion, data saver)
- [ ] Provide alternatives for unsupported features

---

## Pattern 6: Virtual Scrolling

**Use Case**: Render only visible items in long lists to maintain performance.

**Implementation**:
```vue
<template>
  <div class="virtual-list" @scroll="handleScroll" ref="container">
    <div class="spacer" :style="{ height: `${totalHeight}px` }">
      <div
        v-for="item in visibleItems"
        :key="item.id"
        class="list-item"
        :style="{ transform: `translateY(${item.offset}px)` }"
      >
        <slot :item="item.data" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

interface Props {
  items: any[]
  itemHeight: number
}

const props = defineProps<Props>()
const container = ref<HTMLElement>()
const scrollTop = ref(0)

const visibleCount = computed(() =>
  Math.ceil((container.value?.clientHeight || 0) / props.itemHeight) + 2
)

const startIndex = computed(() =>
  Math.floor(scrollTop.value / props.itemHeight)
)

const visibleItems = computed(() =>
  props.items
    .slice(startIndex.value, startIndex.value + visibleCount.value)
    .map((data, i) => ({
      id: data.id,
      data,
      offset: (startIndex.value + i) * props.itemHeight
    }))
)

const totalHeight = computed(() => props.items.length * props.itemHeight)

const handleScroll = (e: Event) => {
  scrollTop.value = (e.target as HTMLElement).scrollTop
}
</script>
```

**When to Use**:
- Lists with 100+ items
- Fixed or consistent item heights
- Scrollable containers
- Performance-critical applications

---

## Pattern 7: Code Splitting

**Use Case**: Split code by routes or features to reduce initial bundle size.

**Implementation**:
```typescript
// router/index.ts
const routes = [
  {
    path: '/',
    component: () => import('@/views/Home.vue')
  },
  {
    path: '/dashboard',
    component: () => import('@/views/Dashboard.vue'),
    children: [
      {
        path: 'analytics',
        component: () => import('@/views/dashboard/Analytics.vue')
      },
      {
        path: 'reports',
        component: () => import('@/views/dashboard/Reports.vue')
      }
    ]
  },
  {
    path: '/admin',
    component: () => import('@/views/Admin.vue'),
    // Prefetch admin bundle on hover/focus
    meta: { prefetch: true }
  }
]
```

**Prefetching Strategy**:
```typescript
// Prefetch on link hover
const prefetchOnHover = (route: string) => {
  const link = document.createElement('link')
  link.rel = 'prefetch'
  link.href = route
  document.head.appendChild(link)
}
```

---

## Performance Budget

### Recommended Metrics

| Metric | Target | Max |
|--------|--------|-----|
| First Contentful Paint (FCP) | < 1.8s | < 3.0s |
| Largest Contentful Paint (LCP) | < 2.5s | < 4.0s |
| Time to Interactive (TTI) | < 3.8s | < 7.3s |
| Total Blocking Time (TBT) | < 200ms | < 600ms |
| Cumulative Layout Shift (CLS) | < 0.1 | < 0.25 |
| First Input Delay (FID) | < 100ms | < 300ms |

### Bundle Size Targets

| Resource | Target | Max |
|----------|--------|-----|
| Initial JS | < 200 KB | < 350 KB |
| Initial CSS | < 50 KB | < 100 KB |
| Total Initial Load | < 1 MB | < 2 MB |
| Route Chunk | < 100 KB | < 200 KB |

### Monitoring Tools

- **Lighthouse**: Overall performance audit
- **WebPageTest**: Real-world testing
- **Chrome DevTools**: Performance profiling
- **Webpack Bundle Analyzer**: Bundle size analysis

---

## Performance Checklist

### Before Implementation
- [ ] Define performance budget
- [ ] Identify critical rendering path
- [ ] Plan code splitting strategy
- [ ] Choose appropriate loading patterns

### During Development
- [ ] Lazy load non-critical components
- [ ] Optimize images (format, size, lazy loading)
- [ ] Implement skeleton screens for loading states
- [ ] Use virtual scrolling for long lists
- [ ] Minimize DOM depth (< 15 levels)
- [ ] Avoid layout thrashing

### Before Deployment
- [ ] Run Lighthouse audit (score > 90)
- [ ] Test on low-end devices
- [ ] Verify bundle sizes within budget
- [ ] Check Core Web Vitals metrics
- [ ] Test with slow 3G connection
- [ ] Validate progressive enhancement

---

## Common Performance Anti-Patterns

### ❌ Importing Entire Libraries

```typescript
// Bad - imports entire library
import _ from 'lodash'
import moment from 'moment'

// Good - import only what you need
import debounce from 'lodash/debounce'
import { format } from 'date-fns'
```

### ❌ Excessive Re-renders

```vue
<!-- Bad - re-renders on every mouse move -->
<template>
  <div @mousemove="handleMove">
    {{ position.x }}, {{ position.y }}
  </div>
</template>

<!-- Good - debounced updates -->
<template>
  <div @mousemove="debouncedHandleMove">
    {{ position.x }}, {{ position.y }}
  </div>
</template>

<script setup>
import { useDebounceFn } from '@vueuse/core'

const debouncedHandleMove = useDebounceFn(handleMove, 100)
</script>
```

### ❌ Unoptimized Blur Effects

```css
/* Bad - expensive blur on large element */
.page-background {
  backdrop-filter: blur(40px);
}

/* Good - blur only on small focused areas */
.modal-overlay {
  backdrop-filter: blur(8px);
}

/* Better - disable on low-end devices */
@media (prefers-reduced-motion: reduce) {
  .modal-overlay {
    backdrop-filter: none;
    background: rgba(0, 0, 0, 0.8);
  }
}
```
