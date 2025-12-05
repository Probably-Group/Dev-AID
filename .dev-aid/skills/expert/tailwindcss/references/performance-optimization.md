# Tailwind CSS Performance Optimization

## 1. Purge Optimization

```javascript
// tailwind.config.js
// Good: Specific content paths
export default {
  content: [
    './components/**/*.{vue,js,ts}',
    './layouts/**/*.vue',
    './pages/**/*.vue',
    './composables/**/*.ts'
  ]
}

// Bad: Too broad, includes unused files
export default {
  content: ['./src/**/*']  // Includes tests, stories, etc.
}
```

## 2. JIT Mode Efficiency

```javascript
// Good: Let JIT generate only used utilities
export default {
  mode: 'jit',  // Default in v3+
  theme: {
    extend: {
      // Only extend what you need
      colors: {
        jarvis: {
          primary: '#00ff41',
          secondary: '#0891b2'
        }
      }
    }
  }
}

// Bad: Defining unused variants
export default {
  variants: {
    extend: {
      backgroundColor: ['active', 'group-hover', 'disabled']  // May not use all
    }
  }
}
```

## 3. @apply Extraction Strategy

```vue
<!-- Good: Extract when pattern repeats 3+ times -->
<style>
@layer components {
  .btn-jarvis {
    @apply px-4 py-2 rounded font-medium transition-all duration-200
           focus:outline-none focus:ring-2 focus:ring-offset-2;
  }
}
</style>

<!-- Bad: @apply for single-use styles -->
<style>
.my-unique-element {
  @apply p-4 m-2 text-white;  /* Just use utilities in template */
}
</style>
```

## 4. Responsive Breakpoints Efficiency

```vue
<!-- Good: Mobile-first, minimal breakpoints -->
<div class="p-2 md:p-4 lg:p-6">
  <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4">
</div>

<!-- Bad: Redundant breakpoint definitions -->
<div class="p-2 sm:p-2 md:p-4 lg:p-4 xl:p-6">
  <div class="grid grid-cols-1 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-2">
</div>
```

## 5. Dark Mode Efficiency

```javascript
// Good: Single dark mode strategy (JARVIS is always dark)
export default {
  darkMode: 'class',  // Use 'class' for explicit control
  theme: {
    extend: {
      colors: {
        jarvis: {
          bg: {
            dark: '#0a0a0f',  // Define dark colors directly
            panel: '#111827'
          }
        }
      }
    }
  }
}

// Bad: Light/dark variants when app is always dark
<div class="bg-white dark:bg-gray-900">  // Unnecessary light styles
```

## 6. Animation Performance

```javascript
// Good: GPU-accelerated properties
export default {
  theme: {
    extend: {
      keyframes: {
        glow: {
          '0%, 100%': { opacity: '0.5' },  // opacity is GPU-accelerated
          '50%': { opacity: '1' }
        }
      }
    }
  }
}

// Bad: Layout-triggering properties
keyframes: {
  resize: {
    '0%': { width: '100px' },  // Triggers layout recalc
    '100%': { width: '200px' }
  }
}
```

## 7. Build Size Optimization

### Check Bundle Size

```bash
# Build and check CSS output size
npm run build && ls -lh .output/public/_nuxt/*.css

# Analyze unused CSS
npx tailwindcss --content './components/**/*.vue' --output /dev/null
```

### CSS Output Best Practices

- Keep final CSS bundle under 50KB (gzipped)
- Avoid generating unused utility variants
- Use specific content paths to exclude test files
- Leverage JIT mode for on-demand class generation

## 8. Performance Checklist

Before deploying Tailwind CSS changes:

- [ ] Content paths are specific and exclude non-production files
- [ ] JIT mode is enabled (default in v3+)
- [ ] @apply is used only for patterns that repeat 3+ times
- [ ] Responsive breakpoints follow mobile-first approach
- [ ] Animations use GPU-accelerated properties (transform, opacity)
- [ ] Dark mode strategy matches app requirements (JARVIS is always dark)
- [ ] Build size hasn't grown unexpectedly
- [ ] No unused variants are being generated
