# Performance Optimization for Accessibility

## Pattern 1: Semantic HTML Over ARIA

```html
<!-- Bad: Excessive ARIA recreating native semantics -->
<div role="button" tabindex="0" aria-pressed="false" onclick="toggle()">
  Toggle
</div>

<!-- Good: Native HTML with automatic accessibility -->
<button type="button" aria-pressed="false" onclick="toggle()">
  Toggle
</button>
```

**Why it's better**:
- Native semantics are faster to parse
- Browser provides keyboard support automatically
- Screen readers optimize for native elements
- Less JavaScript processing required

---

## Pattern 2: Efficient ARIA Updates

```typescript
// Bad: Updating entire live region on each change
function updateStatus(message: string) {
  liveRegion.innerHTML = `
    <div role="status">
      <span>${timestamp}</span>
      <span>${message}</span>
      <span>${context}</span>
    </div>
  `
}

// Good: Minimal updates to live regions
function updateStatus(message: string) {
  // Only update the text content, not structure
  statusText.textContent = message
}
```

**Performance impact**:
- Reduces DOM mutations
- Prevents screen reader re-announcement of unchanged content
- Lower memory allocation
- Faster rendering pipeline

---

## Pattern 3: Optimized Focus Management

```typescript
// Bad: Searching DOM repeatedly
function trapFocus(element: HTMLElement) {
  document.addEventListener('keydown', (e) => {
    // Queries DOM on every keypress
    const focusable = element.querySelectorAll('button, [href], input')
    // ...
  })
}

// Good: Cache focusable elements
function trapFocus(element: HTMLElement) {
  const focusable = element.querySelectorAll<HTMLElement>(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  )
  const firstFocusable = focusable[0]
  const lastFocusable = focusable[focusable.length - 1]

  function handleKeyDown(e: KeyboardEvent) {
    if (e.key !== 'Tab') return

    if (e.shiftKey && document.activeElement === firstFocusable) {
      e.preventDefault()
      lastFocusable.focus()
    } else if (!e.shiftKey && document.activeElement === lastFocusable) {
      e.preventDefault()
      firstFocusable.focus()
    }
  }

  element.addEventListener('keydown', handleKeyDown)
  return () => element.removeEventListener('keydown', handleKeyDown)
}
```

**Optimization details**:
- Query DOM once, not on every keypress
- Cache first and last focusable elements
- Early return for non-Tab keys
- Proper cleanup to prevent memory leaks

---

## Pattern 4: Reduced Motion Support

```css
/* Bad: Animations without motion preference check */
.animated-element {
  animation: slide-in 0.5s ease-out;
}

/* Good: Respect user motion preferences */
.animated-element {
  animation: slide-in 0.5s ease-out;
}

@media (prefers-reduced-motion: reduce) {
  .animated-element {
    animation: none;
    transition: none;
  }
}
```

```typescript
// JavaScript motion preference detection
const prefersReducedMotion = window.matchMedia(
  '(prefers-reduced-motion: reduce)'
).matches

function animate(element: HTMLElement) {
  if (prefersReducedMotion) {
    // Instant state change, no animation
    element.style.opacity = '1'
    return
  }

  // Full animation for users who prefer it
  element.animate([
    { opacity: 0 },
    { opacity: 1 }
  ], { duration: 300 })
}
```

**Benefits**:
- Reduces CPU/GPU usage for users who need it
- Prevents vestibular disorders from being triggered
- Improves battery life on mobile devices
- Faster perceived performance

---

## Pattern 5: Lazy Loading for Screen Readers

```html
<!-- Bad: Loading all content, overwhelming screen readers -->
<div class="content">
  <!-- 100+ items all loaded at once -->
</div>

<!-- Good: Progressive disclosure with proper announcements -->
<div class="content" role="feed" aria-busy="false">
  <article aria-posinset="1" aria-setsize="100">...</article>
  <article aria-posinset="2" aria-setsize="100">...</article>
  <!-- Load more on scroll/request -->
</div>

<div role="status" aria-live="polite" class="visually-hidden">
  <!-- Announce when new content loads -->
  Loaded 10 more items
</div>
```

```typescript
// Efficient lazy loading with accessibility
function loadMoreContent() {
  const liveRegion = document.querySelector('[role="status"]')
  const feed = document.querySelector('[role="feed"]')

  // Mark as loading
  feed?.setAttribute('aria-busy', 'true')

  // Load content
  const newItems = await fetchItems()

  // Append without reflow
  const fragment = document.createDocumentFragment()
  newItems.forEach(item => fragment.appendChild(createArticle(item)))
  feed?.appendChild(fragment)

  // Mark complete and announce
  feed?.setAttribute('aria-busy', 'false')
  if (liveRegion) {
    liveRegion.textContent = `Loaded ${newItems.length} more items`
  }
}
```

**Performance considerations**:
- Use DocumentFragment to batch DOM updates
- aria-busy prevents screen reader from announcing during load
- Announce completion in live region
- Reduces initial page load time
- Lower memory footprint

---

## Pattern 6: Debounced Live Announcements

```typescript
// Bad: Announcing every keystroke
input.addEventListener('input', (e) => {
  liveRegion.textContent = `${e.target.value.length} characters`
})

// Good: Debounced announcements
let debounceTimer: number
input.addEventListener('input', (e) => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    liveRegion.textContent = `${e.target.value.length} characters`
  }, 1000)
})
```

**Why debounce**:
- Prevents screen reader from interrupting itself
- Reduces cognitive load
- Better user experience for assistive technology users

---

## Pattern 7: Efficient Skip Links

```html
<!-- Good: Skip link that's performant -->
<a href="#main-content" class="skip-link">Skip to main content</a>

<style>
.skip-link {
  position: absolute;
  left: -10000px;
  top: auto;
  width: 1px;
  height: 1px;
  overflow: hidden;
}

.skip-link:focus {
  position: static;
  width: auto;
  height: auto;
}
</style>
```

**Performance note**: Using `position: absolute; left: -10000px` instead of `display: none` ensures the link is still in the accessibility tree without causing layout shifts.

---

## Pattern 8: Optimized Focus Indicators

```css
/* Bad: Triggering repaint on every element */
*:focus {
  box-shadow: 0 0 0 3px rgba(0, 0, 255, 0.5);
}

/* Good: Efficient outline property */
*:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
}

*:focus:not(:focus-visible) {
  outline: none;
}
```

**Performance benefits**:
- `outline` doesn't affect layout (no reflow)
- `outline` is typically GPU-accelerated
- `:focus-visible` reduces unnecessary focus indicators for mouse users
- CSS custom properties cached by browser

---

## Measuring Accessibility Performance

### Tools

1. **Lighthouse Accessibility Audit**
   ```bash
   npx lighthouse http://localhost:3000 \
     --only-categories=accessibility \
     --output json \
     --output-path ./accessibility-report.json
   ```

2. **axe-core Performance**
   ```typescript
   import { axe } from 'jest-axe'

   console.time('axe-audit')
   const results = await axe(document.body)
   console.timeEnd('axe-audit')
   ```

3. **Screen Reader Performance Testing**
   - Measure time to navigate through page
   - Count number of announcements for common tasks
   - Verify focus order matches visual order

### Performance Benchmarks

- **Focus trap**: < 5ms to handle Tab key
- **Live region update**: < 10ms to update textContent
- **Skip link activation**: < 50ms to move focus
- **ARIA state change**: < 5ms to update attribute
