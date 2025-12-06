## 7. Performance Patterns

### Pattern 1: will-change Usage

```css
/* BAD: Always active will-change */
.animated-element {
  will-change: transform, opacity;
}

/* GOOD: Apply only when animating */
.animated-element:hover,
.animated-element:focus,
.animated-element.is-animating {
  will-change: transform, opacity;
}

/* GOOD: Remove after animation */
.animated-element {
  transition: transform 0.3s ease;
}

.animated-element.animate-complete {
  will-change: auto;
}
```

### Pattern 2: Transform vs Layout Properties

```css
/* BAD: Triggers layout recalculation */
.sidebar-toggle {
  width: 0;
  transition: width 0.3s ease;
}
.sidebar-toggle.open {
  width: 280px;
}

/* GOOD: GPU-accelerated transform */
.sidebar-toggle {
  transform: translateX(-100%);
  transition: transform 0.3s ease;
}
.sidebar-toggle.open {
  transform: translateX(0);
}
```

### Pattern 3: Hardware Acceleration

```css
/* BAD: No GPU acceleration hint */
.card {
  transition: transform 0.3s;
}

/* GOOD: Force GPU layer creation */
.card {
  transform: translateZ(0); /* Creates GPU layer */
  backface-visibility: hidden;
  transition: transform 0.3s;
}

/* GOOD: Modern approach */
.card {
  contain: layout style paint;
  transition: transform 0.3s;
}
```

### Pattern 4: Reduced Motion Handling

```typescript
/* BAD: Ignore user preference */
function animateElement(el: HTMLElement) {
  el.animate([
    { transform: 'translateY(20px)', opacity: 0 },
    { transform: 'translateY(0)', opacity: 1 }
  ], { duration: 300 })
}

/* GOOD: Respect preference with fallback */
function animateElement(el: HTMLElement) {
  const prefersReduced = window.matchMedia(
    '(prefers-reduced-motion: reduce)'
  ).matches

  if (prefersReduced) {
    el.style.opacity = '1'
    return
  }

  el.animate([
    { transform: 'translateY(20px)', opacity: 0 },
    { transform: 'translateY(0)', opacity: 1 }
  ], { duration: 300 })
}
```

### Pattern 5: Animation Batching

```typescript
/* BAD: Multiple reflows */
function animateItems(items: HTMLElement[]) {
  items.forEach((item, i) => {
    item.style.transform = `translateY(${i * 10}px)`
    item.style.opacity = '0'
  })
}

/* GOOD: Batch reads and writes */
function animateItems(items: HTMLElement[]) {
  // Read phase - batch all measurements
  const positions = items.map(item => item.getBoundingClientRect())

  // Write phase - batch all mutations
  requestAnimationFrame(() => {
    items.forEach((item, i) => {
      item.style.transform = `translateY(${i * 10}px)`
      item.style.opacity = '0'
    })
  })
}

/* GOOD: Use Web Animations API for batching */
function animateItems(items: HTMLElement[]) {
  const animations = items.map((item, i) =>
    item.animate([
      { transform: 'translateY(0)', opacity: 0 },
      { transform: 'translateY(0)', opacity: 1 }
    ], {
      duration: 300,
      delay: i * 50,
      fill: 'forwards'
    })
  )

  return Promise.all(animations.map(a => a.finished))
}
```

---

