# Performance Patterns

> **Reference Document**: Performance optimization patterns and implementation strategies for the UI/UX Expert skill.

---

## Table of Contents

1. [Lazy Loading](#pattern-1-lazy-loading)
2. [Image Optimization](#pattern-2-image-optimization)
3. [Critical CSS](#pattern-3-critical-css)
4. [Skeleton Screens](#pattern-4-skeleton-screens)
5. [Code Splitting](#pattern-5-code-splitting)
6. [Minimize Layout Shifts (CLS)](#pattern-6-minimize-layout-shifts-cls)

---

## Pattern 1: Lazy Loading

### Bad - Load all images immediately:
```html
<img src="/hero-large.jpg" alt="Hero image" />
<img src="/product-1.jpg" alt="Product" />
<img src="/product-2.jpg" alt="Product" />
```

### Good - Lazy load below-fold images:
```html
<!-- Critical above-fold image - load immediately -->
<img src="/hero-large.jpg" alt="Hero image" fetchpriority="high" />

<!-- Below-fold images - lazy load -->
<img src="/product-1.jpg" alt="Product" loading="lazy" decoding="async" />
<img src="/product-2.jpg" alt="Product" loading="lazy" decoding="async" />
```

### Vue component with intersection observer:
```vue
<template>
  <img
    v-if="isVisible"
    :src="src"
    :alt="alt"
    @load="onLoad"
  />
  <div v-else ref="placeholder" class="skeleton" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useIntersectionObserver } from '@vueuse/core'

const props = defineProps(['src', 'alt'])
const placeholder = ref(null)
const isVisible = ref(false)

onMounted(() => {
  const { stop } = useIntersectionObserver(
    placeholder,
    ([{ isIntersecting }]) => {
      if (isIntersecting) {
        isVisible.value = true
        stop()
      }
    },
    { rootMargin: '100px' }
  )
})
</script>
```

---

## Pattern 2: Image Optimization

### Bad - Single image size for all devices:
```html
<img src="/photo.jpg" alt="Photo" />
```

### Good - Responsive images with modern formats:
```html
<picture>
  <!-- Modern format for supporting browsers -->
  <source
    type="image/avif"
    srcset="
      /photo-400.avif 400w,
      /photo-800.avif 800w,
      /photo-1200.avif 1200w
    "
    sizes="(max-width: 600px) 100vw, 50vw"
  />
  <source
    type="image/webp"
    srcset="
      /photo-400.webp 400w,
      /photo-800.webp 800w,
      /photo-1200.webp 1200w
    "
    sizes="(max-width: 600px) 100vw, 50vw"
  />
  <!-- Fallback -->
  <img
    src="/photo-800.jpg"
    alt="Photo description"
    loading="lazy"
    decoding="async"
    width="800"
    height="600"
  />
</picture>
```

**Key Points**:
- Use modern formats (AVIF, WebP) with fallbacks
- Provide multiple sizes with `srcset` for different viewports
- Specify `width` and `height` to prevent layout shifts
- Use `loading="lazy"` for below-fold images

---

## Pattern 3: Critical CSS

### Bad - Load all CSS before rendering:
```html
<link rel="stylesheet" href="/styles.css" />
```

### Good - Inline critical CSS, defer non-critical:
```html
<head>
  <!-- Critical CSS inlined -->
  <style>
    /* Above-fold styles only */
    .hero { ... }
    .nav { ... }
    .cta-button { ... }
  </style>

  <!-- Non-critical CSS loaded async -->
  <link
    rel="preload"
    href="/styles.css"
    as="style"
    onload="this.onload=null;this.rel='stylesheet'"
  />
  <noscript>
    <link rel="stylesheet" href="/styles.css" />
  </noscript>
</head>
```

**Best Practices**:
- Inline critical CSS for above-the-fold content
- Load non-critical CSS asynchronously
- Keep critical CSS under 14KB for first TCP packet
- Use tools like Critical or Critters to extract critical CSS

---

## Pattern 4: Skeleton Screens

### Bad - Show spinner while loading:
```vue
<template>
  <div v-if="loading" class="spinner" />
  <div v-else>{{ content }}</div>
</template>
```

### Good - Show skeleton that matches final layout:
```vue
<template>
  <article class="card">
    <template v-if="loading">
      <!-- Skeleton matches final content structure -->
      <div class="skeleton-image animate-pulse bg-gray-200 h-48 rounded-t" />
      <div class="p-4 space-y-3">
        <div class="skeleton-title h-6 bg-gray-200 rounded w-3/4 animate-pulse" />
        <div class="skeleton-text h-4 bg-gray-200 rounded w-full animate-pulse" />
        <div class="skeleton-text h-4 bg-gray-200 rounded w-2/3 animate-pulse" />
      </div>
    </template>
    <template v-else>
      <img :src="image" :alt="title" class="h-48 object-cover rounded-t" />
      <div class="p-4">
        <h3 class="text-lg font-semibold">{{ title }}</h3>
        <p class="text-gray-600">{{ description }}</p>
      </div>
    </template>
  </article>
</template>
```

**Why Skeleton Screens?**:
- Reduce perceived loading time
- Prevent layout shifts
- Match the structure of final content
- Provide visual feedback without being distracting

---

## Pattern 5: Code Splitting

### Bad - Import all components upfront:
```typescript
import Dashboard from '@/views/Dashboard.vue'
import Settings from '@/views/Settings.vue'
import Analytics from '@/views/Analytics.vue'
import Admin from '@/views/Admin.vue'
```

### Good - Lazy load routes and heavy components:
```typescript
// router/index.ts
const routes = [
  {
    path: '/dashboard',
    component: () => import('@/views/Dashboard.vue')
  },
  {
    path: '/settings',
    component: () => import('@/views/Settings.vue')
  },
  {
    path: '/analytics',
    // Prefetch for likely navigation
    component: () => import(/* webpackPrefetch: true */ '@/views/Analytics.vue')
  },
  {
    path: '/admin',
    // Only load when needed
    component: () => import('@/views/Admin.vue')
  }
]

// Lazy load heavy components
const HeavyChart = defineAsyncComponent({
  loader: () => import('@/components/HeavyChart.vue'),
  loadingComponent: ChartSkeleton,
  delay: 200,
  timeout: 10000
})
```

**Code Splitting Strategies**:
- Route-based splitting (load views on demand)
- Component-based splitting for heavy components (charts, editors)
- Use `webpackPrefetch` for likely-needed routes
- Show loading components during async loading

---

## Pattern 6: Minimize Layout Shifts (CLS)

### Bad - Images without dimensions cause layout shift:
```html
<img src="/photo.jpg" alt="Photo" />
```

### Good - Reserve space to prevent shift:
```html
<!-- Always specify dimensions -->
<img
  src="/photo.jpg"
  alt="Photo"
  width="800"
  height="600"
  class="aspect-[4/3] object-cover"
/>

<!-- Use aspect-ratio for responsive images -->
<div class="aspect-video">
  <img src="/video-thumb.jpg" alt="Video" class="w-full h-full object-cover" />
</div>

<!-- Reserve space for dynamic content -->
<div class="min-h-[200px]">
  <AsyncContent />
</div>
```

**Prevent Layout Shifts**:
- Always specify `width` and `height` attributes on images
- Use `aspect-ratio` CSS property for responsive containers
- Reserve space for dynamic content with `min-height`
- Load fonts with `font-display: swap` and use fallback fonts
- Avoid inserting content above existing content
- Use transforms for animations instead of properties that affect layout

---

## Core Web Vitals Targets

When implementing these performance patterns, aim for:

- **LCP (Largest Contentful Paint)**: < 2.5 seconds
- **FID (First Input Delay)**: < 100 milliseconds
- **CLS (Cumulative Layout Shift)**: < 0.1

---

## Performance Testing

```bash
# Run Lighthouse audit
npm run lighthouse

# Check bundle size
npm run build -- --report

# Analyze Web Vitals
npm run test:performance
```

---

## Summary

Performance is a core part of good UX. Users expect:
- Fast page loads (< 3 seconds)
- Smooth interactions (60fps)
- No unexpected layout shifts
- Responsive interfaces

Implement these patterns to deliver performant experiences:
1. Lazy load below-fold content
2. Optimize and serve responsive images
3. Inline critical CSS
4. Use skeleton screens for loading states
5. Code split heavy components and routes
6. Prevent layout shifts with proper sizing

Always measure performance with real-world testing and iterate based on Core Web Vitals metrics.
