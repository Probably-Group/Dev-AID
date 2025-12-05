# Tailwind CSS Anti-Patterns & Common Mistakes

## 1. Excessive Custom CSS

### Problem
Writing custom CSS when Tailwind utilities already exist defeats the purpose of utility-first CSS.

### Bad Example

```vue
<style>
.custom-panel {
  padding: 1rem;
  border-radius: 0.5rem;
  background-color: #111827;
}
</style>

<template>
  <div class="custom-panel">Content</div>
</template>
```

### Good Example

```vue
<template>
  <div class="p-4 rounded-lg bg-gray-900">Content</div>
</template>
```

### Why Better
- Uses existing utilities from Tailwind
- Maintains consistency with spacing scale
- Easier to modify and maintain
- Reduces CSS bundle size

---

## 2. Inconsistent Spacing

### Problem
Using arbitrary spacing values breaks the design system's visual rhythm.

### Bad Example

```vue
<!-- Mixed spacing values -->
<div class="p-3 mt-5 mb-2">
  <div class="mx-7 my-1">Content</div>
</div>
```

### Good Example

```vue
<!-- Consistent scale (4, 8, 12, 16...) -->
<div class="p-4 my-4">
  <div class="m-4">Content</div>
</div>
```

### Why Better
- Follows Tailwind's spacing scale (4px increments)
- Creates visual consistency across the app
- Easier to maintain and reason about
- Aligns with design system principles

---

## 3. Hardcoded Colors

### Problem
Using arbitrary color values instead of theme colors breaks consistency and makes theming difficult.

### Bad Example

```vue
<!-- Hardcoded hex values -->
<div class="text-[#00ff41] bg-[#111827]">
  <span class="border-[#0891b2]">Status</span>
</div>
```

### Good Example

```vue
<!-- Theme color references -->
<div class="text-jarvis-primary bg-jarvis-bg-panel">
  <span class="border-jarvis-secondary">Status</span>
</div>
```

### Why Better
- Centralizes color management in config
- Enables easy theme changes
- Maintains consistency across components
- Supports design token approach

---

## 4. Overusing @apply

### Problem
Extracting every element to a custom class defeats the utility-first approach and creates CSS bloat.

### Bad Example

```vue
<style>
.my-unique-element {
  @apply p-4 m-2 text-white bg-gray-900;
}

.another-unique-element {
  @apply flex items-center justify-center;
}

.one-time-use {
  @apply rounded-lg shadow-md;
}
</style>
```

### Good Example

```vue
<!-- Use utilities directly in template -->
<div class="p-4 m-2 text-white bg-gray-900">Content</div>
<div class="flex items-center justify-center">Content</div>
<div class="rounded-lg shadow-md">Content</div>

<!-- Only extract when pattern repeats 3+ times -->
<style>
@layer components {
  .btn-jarvis {
    @apply px-4 py-2 rounded font-medium transition-all duration-200
           focus:outline-none focus:ring-2 focus:ring-offset-2;
  }
}
</style>
```

### Why Better
- Keeps markup readable and self-documenting
- Reduces CSS bundle size
- Only extracts truly reusable patterns
- Maintains utility-first benefits

---

## 5. Redundant Breakpoint Definitions

### Problem
Defining the same value across multiple breakpoints creates unnecessary CSS.

### Bad Example

```vue
<!-- Redundant breakpoint values -->
<div class="p-2 sm:p-2 md:p-4 lg:p-4 xl:p-6">
  <div class="grid grid-cols-1 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-2">
  </div>
</div>
```

### Good Example

```vue
<!-- Mobile-first, minimal breakpoints -->
<div class="p-2 md:p-4 xl:p-6">
  <div class="grid grid-cols-1 md:grid-cols-2">
  </div>
</div>
```

### Why Better
- Follows mobile-first approach
- Reduces CSS output
- Easier to read and maintain
- Only defines changes at each breakpoint

---

## 6. Unnecessary Light Mode Styles

### Problem
Including light mode styles when the app only uses dark mode creates unused CSS.

### Bad Example

```vue
<!-- Light mode styles that are never used -->
<div class="bg-white text-black dark:bg-gray-900 dark:text-white">
  <span class="text-gray-900 dark:text-gray-100">Content</span>
</div>
```

### Good Example

```vue
<!-- Only dark mode (JARVIS is always dark) -->
<div class="bg-jarvis-bg-panel text-white">
  <span class="text-gray-100">Content</span>
</div>
```

### Why Better
- Reduces CSS bundle size
- Simplifies markup
- No unused variant generation
- Matches app requirements

---

## 7. Layout-Triggering Animations

### Problem
Animating properties that trigger layout recalculation causes poor performance.

### Bad Example

```javascript
// Bad: Layout-triggering properties
keyframes: {
  resize: {
    '0%': { width: '100px', height: '50px' },
    '100%': { width: '200px', height: '100px' }
  },
  move: {
    '0%': { left: '0', top: '0' },
    '100%': { left: '100px', top: '100px' }
  }
}
```

### Good Example

```javascript
// Good: GPU-accelerated properties
keyframes: {
  scale: {
    '0%': { transform: 'scale(1)' },
    '100%': { transform: 'scale(2)' }
  },
  fade: {
    '0%': { opacity: '0' },
    '100%': { opacity: '1' }
  }
}
```

### Why Better
- Uses GPU-accelerated properties (transform, opacity)
- Avoids layout recalculation
- Smooth 60fps animations
- Better battery life on mobile

---

## 8. Overly Broad Content Paths

### Problem
Including too many files in content paths slows build and may include unused classes.

### Bad Example

```javascript
// Too broad, includes everything
export default {
  content: [
    './src/**/*',
    './**/*.{js,ts,vue,html}'
  ]
}
```

### Good Example

```javascript
// Specific paths to actual source files
export default {
  content: [
    './components/**/*.{vue,js,ts}',
    './layouts/**/*.vue',
    './pages/**/*.vue',
    './composables/**/*.ts',
    './plugins/**/*.ts'
  ]
}
```

### Why Better
- Faster build times
- More accurate CSS purging
- Excludes test and build files
- Better production bundle size

---

## 9. Ignoring Focus States

### Problem
Missing focus states makes the interface inaccessible for keyboard navigation.

### Bad Example

```vue
<!-- No focus styles -->
<button class="px-4 py-2 bg-jarvis-primary text-black">
  Submit
</button>

<!-- Focus outline removed without replacement -->
<input class="outline-none border-0" />
```

### Good Example

```vue
<!-- Visible focus states -->
<button class="px-4 py-2 bg-jarvis-primary text-black
               focus:outline-none focus:ring-2 focus:ring-jarvis-primary focus:ring-offset-2">
  Submit
</button>

<input class="outline-none border border-gray-300
              focus:border-jarvis-primary focus:ring-2 focus:ring-jarvis-primary/20" />
```

### Why Better
- Maintains keyboard accessibility
- Provides visual focus indication
- Meets WCAG guidelines
- Better user experience

---

## 10. Not Using Arbitrary Values Appropriately

### Problem
Overusing arbitrary values when theme values exist, or not using them when needed.

### Bad Example

```vue
<!-- Arbitrary value when theme color exists -->
<div class="bg-[#00ff41]"><!-- Use theme color instead --></div>

<!-- Hard to maintain magic numbers -->
<div class="w-[247px] h-[93px] mt-[17px]">Content</div>
```

### Good Example

```vue
<!-- Use theme colors -->
<div class="bg-jarvis-primary">Content</div>

<!-- Arbitrary values for truly custom needs -->
<div class="w-[calc(100%-2rem)] aspect-[16/9]">Video</div>
```

### Why Better
- Uses theme values when available
- Arbitrary values only for special cases
- Maintains design system consistency
- Self-documenting intent

---

## Quick Checklist: Avoiding Anti-Patterns

Before committing Tailwind CSS changes:

- [ ] Used utilities instead of custom CSS where possible
- [ ] Applied consistent spacing from Tailwind scale (4, 8, 12, 16...)
- [ ] Referenced theme colors, not hardcoded hex values
- [ ] Only used @apply for patterns that repeat 3+ times
- [ ] Followed mobile-first approach with minimal breakpoints
- [ ] Removed unused light mode styles (JARVIS is always dark)
- [ ] Used GPU-accelerated properties for animations
- [ ] Configured specific content paths, not overly broad
- [ ] Included focus states for all interactive elements
- [ ] Used arbitrary values appropriately (not overused, not underused)
