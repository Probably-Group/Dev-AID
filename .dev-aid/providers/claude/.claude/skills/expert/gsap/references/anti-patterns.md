# GSAP Anti-Patterns and Common Mistakes

This file documents common mistakes and anti-patterns to avoid when using GSAP.

## 8.1 Critical Anti-Patterns

### Never: Skip Cleanup

**Problem**: Animations continue running after component unmount, causing memory leaks.

#### Bad Example

```typescript
// ❌ MEMORY LEAK - Animation never cleaned up
onMounted(() => {
  gsap.to(element, { x: 100, duration: 1 })
})
```

#### Good Example

```typescript
// ✅ PROPER CLEANUP - Animation killed on unmount
let tween: gsap.core.Tween

onMounted(() => {
  tween = gsap.to(element, { x: 100, duration: 1 })
})

onUnmounted(() => {
  tween?.kill()
})
```

#### Why It Matters

- Memory leaks accumulate over time
- Can cause browser slowdowns
- Multiple component mounts/unmounts will create many zombie animations
- Hard to debug in production

### Never: Animate Layout Properties

**Problem**: Layout properties force browser reflow, causing janky animations.

#### Bad Example

```typescript
// ❌ BAD - Causes layout thrashing, 30fps or worse
gsap.to(element, {
  width: 200,
  height: 100,
  left: 50,
  top: 25,
  margin: 10,
  padding: 5
})
```

#### Good Example

```typescript
// ✅ GOOD - GPU accelerated, smooth 60fps
gsap.to(element, {
  scaleX: 2,      // Instead of width
  scaleY: 1,      // Instead of height
  x: 50,          // Instead of left
  y: 25,          // Instead of top
  opacity: 0.8    // GPU accelerated
})
```

#### Why It Matters

- Layout properties trigger reflow/repaint (CPU)
- Transform properties use GPU acceleration
- Can mean the difference between 60fps and 15fps
- Especially important on mobile devices

### Never: Ignore Reduced Motion

**Problem**: Animations can trigger vestibular disorders, causing nausea and dizziness.

#### Bad Example

```typescript
// ❌ BAD - Ignores accessibility
gsap.from(element, {
  opacity: 0,
  scale: 0.5,
  rotation: 360,
  duration: 1
})
```

#### Good Example

```typescript
// ✅ GOOD - Respects user preference
const prefersReducedMotion = window.matchMedia(
  '(prefers-reduced-motion: reduce)'
).matches

if (prefersReducedMotion) {
  gsap.set(element, { opacity: 1 })
} else {
  gsap.from(element, { opacity: 0, scale: 0.5, rotation: 360, duration: 1 })
}
```

#### Why It Matters

- Required for WCAG 2.1 Level AAA compliance
- Affects users with vestibular disorders
- Can cause physical discomfort or illness
- Shows respect for user preferences

### Never: Create Animations in Loops Without Cleanup

**Problem**: Creating animations in loops without tracking them causes memory leaks.

#### Bad Example

```typescript
// ❌ BAD - No way to clean up these animations
items.forEach(item => {
  gsap.to(item, { x: 100, duration: 1 })
})
```

#### Good Example

```typescript
// ✅ GOOD - Store animations for cleanup
const animations: gsap.core.Tween[] = []

items.forEach(item => {
  const tween = gsap.to(item, { x: 100, duration: 1 })
  animations.push(tween)
})

onUnmounted(() => {
  animations.forEach(a => a.kill())
})
```

#### Why It Matters

- Loops can create dozens or hundreds of animations
- Without cleanup, memory usage grows unbounded
- Can crash browser on slow devices

## 8.2 Common Mistakes

### Mistake: Not Using Timelines for Sequences

**Problem**: Hard to manage and synchronize multiple animations.

#### Bad Example

```typescript
// ❌ Hard to maintain, timing is brittle
gsap.to('.logo', { opacity: 1, duration: 0.5 })
gsap.to('.panel', { x: 0, duration: 0.5, delay: 0.5 })
gsap.to('.status', { opacity: 1, duration: 0.3, delay: 1 })
```

#### Good Example

```typescript
// ✅ Clear sequence, easy to adjust timing
const tl = gsap.timeline()
  .to('.logo', { opacity: 1, duration: 0.5 })
  .to('.panel', { x: 0, duration: 0.5 })
  .to('.status', { opacity: 1, duration: 0.3 })
```

### Mistake: Over-Using will-change

**Problem**: Keeping will-change active uses excessive memory.

#### Bad Example

```typescript
// ❌ will-change stays active forever
element.style.willChange = 'transform, opacity'
gsap.to(element, { x: 100, opacity: 0.8 })
// Never removed!
```

#### Good Example

```typescript
// ✅ Apply before, remove after
element.style.willChange = 'transform, opacity'

gsap.to(element, {
  x: 100,
  opacity: 0.8,
  onComplete: () => {
    element.style.willChange = 'auto'
  }
})
```

### Mistake: Not Batching ScrollTrigger

**Problem**: Creating individual ScrollTrigger for each element is inefficient.

#### Bad Example

```typescript
// ❌ Creates 50 ScrollTrigger instances
items.forEach(item => {
  gsap.to(item, {
    scrollTrigger: { trigger: item },
    opacity: 1
  })
})
```

#### Good Example

```typescript
// ✅ Single ScrollTrigger batch
ScrollTrigger.batch('.item', {
  onEnter: elements => gsap.to(elements, { opacity: 1, stagger: 0.1 })
})
```

### Mistake: Animating During Render

**Problem**: Animations in render cycle cause infinite loops.

#### Bad Example

```vue
<!-- ❌ BAD - Animates every render -->
<script setup>
const count = ref(0)

// This runs on EVERY render!
gsap.to('.element', { x: count.value * 10 })
</script>
```

#### Good Example

```vue
<!-- ✅ GOOD - Animate in response to state changes -->
<script setup>
const count = ref(0)

watch(count, (newValue) => {
  gsap.to('.element', { x: newValue * 10 })
})
</script>
```

### Mistake: Not Killing ScrollTrigger on Unmount

**Problem**: ScrollTrigger instances persist after component unmount.

#### Bad Example

```typescript
// ❌ BAD - ScrollTrigger never cleaned up
onMounted(() => {
  gsap.to('.element', {
    scrollTrigger: {
      trigger: '.element',
      start: 'top 80%'
    },
    opacity: 1
  })
})
```

#### Good Example

```typescript
// ✅ GOOD - Properly clean up ScrollTrigger
onMounted(() => {
  gsap.to('.element', {
    scrollTrigger: {
      trigger: '.element',
      start: 'top 80%'
    },
    opacity: 1
  })
})

onUnmounted(() => {
  ScrollTrigger.getAll().forEach(trigger => trigger.kill())
})
```

## 8.3 Subtle Anti-Patterns

### Using Inline Styles Instead of Classes

**Problem**: Inline styles are harder to override and maintain.

#### Better Approach

```typescript
// Instead of this:
gsap.to(element, { backgroundColor: '#ff0000' })

// Consider this:
element.classList.add('error-state')
gsap.to(element, { className: '+=active' })
```

### Not Using Defaults in Timelines

**Problem**: Repeating the same options for every tween.

#### Bad Example

```typescript
const tl = gsap.timeline()
  .to('.a', { opacity: 1, duration: 0.5, ease: 'power2.out' })
  .to('.b', { opacity: 1, duration: 0.5, ease: 'power2.out' })
  .to('.c', { opacity: 1, duration: 0.5, ease: 'power2.out' })
```

#### Good Example

```typescript
const tl = gsap.timeline({
  defaults: { duration: 0.5, ease: 'power2.out' }
})
  .to('.a', { opacity: 1 })
  .to('.b', { opacity: 1 })
  .to('.c', { opacity: 1 })
```

### Not Using Stagger

**Problem**: Manually calculating delays for similar animations.

#### Bad Example

```typescript
items.forEach((item, index) => {
  gsap.to(item, {
    opacity: 1,
    delay: index * 0.1,
    duration: 0.5
  })
})
```

#### Good Example

```typescript
gsap.to(items, {
  opacity: 1,
  stagger: 0.1,
  duration: 0.5
})
```

### Creating New Timelines on Every Interaction

**Problem**: Excessive object creation and garbage collection.

#### Bad Example

```typescript
const show = () => {
  // New timeline every time!
  gsap.timeline()
    .to('.panel', { opacity: 1 })
    .to('.content', { opacity: 1 })
}

const hide = () => {
  // Another new timeline!
  gsap.timeline()
    .to('.content', { opacity: 0 })
    .to('.panel', { opacity: 0 })
}
```

#### Good Example

```typescript
// Create once, reuse
const timeline = gsap.timeline({ paused: true })
  .to('.panel', { opacity: 1 })
  .to('.content', { opacity: 1 })

const show = () => timeline.play()
const hide = () => timeline.reverse()
```

## Anti-Pattern Checklist

Before committing animation code, verify:

- [ ] All animations have cleanup in onUnmounted
- [ ] Only GPU-accelerated properties used (transform, opacity)
- [ ] Reduced motion preference checked
- [ ] ScrollTrigger instances killed on unmount
- [ ] will-change applied before and removed after
- [ ] Timelines reused instead of recreated
- [ ] ScrollTrigger animations batched
- [ ] No animations in render/reactive cycles
- [ ] Stagger used for multiple similar animations
- [ ] Timeline defaults used for repeated options

## Resources

- [GSAP Performance Tips](https://greensock.com/performance/)
- [Animation Performance](https://developers.google.com/web/fundamentals/performance/rendering/stick-to-compositor-only-properties-and-manage-layer-count)
- [Reduced Motion Query](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion)
