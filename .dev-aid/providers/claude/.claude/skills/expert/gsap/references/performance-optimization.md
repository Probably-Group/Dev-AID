# GSAP Performance Optimization

This file contains detailed performance optimization strategies for GSAP animations.

## 6.1 will-change Property Usage

### Good: Apply will-change Before Animation

```typescript
const animatePanel = (element: HTMLElement) => {
  element.style.willChange = 'transform, opacity'

  gsap.to(element, {
    x: 100,
    opacity: 0.8,
    duration: 0.5,
    onComplete: () => {
      // ✅ Remove will-change after animation completes
      element.style.willChange = 'auto'
    }
  })
}
```

### Bad: Never Removing will-change

```typescript
// ❌ MEMORY LEAK - will-change stays active forever
const animatePanelBad = (element: HTMLElement) => {
  element.style.willChange = 'transform, opacity' // Memory leak!
  gsap.to(element, { x: 100, opacity: 0.8 })
}
```

### Best Practice

```typescript
// Use composable for will-change management
export function useWillChange(
  element: Ref<HTMLElement | null>,
  properties: string[]
) {
  const enable = () => {
    if (!element.value) return
    element.value.style.willChange = properties.join(', ')
  }

  const disable = () => {
    if (!element.value) return
    element.value.style.willChange = 'auto'
  }

  onUnmounted(disable)

  return { enable, disable }
}

// Usage in component
const { enable, disable } = useWillChange(panelRef, ['transform', 'opacity'])

const animate = () => {
  enable()
  gsap.to(panelRef.value, {
    x: 100,
    opacity: 0.8,
    onComplete: disable
  })
}
```

## 6.2 Transform vs Layout Properties

### GPU-Accelerated Properties (Good)

```typescript
// ✅ GOOD - Use transforms (GPU accelerated)
gsap.to(element, {
  x: 100,           // translateX
  y: 50,            // translateY
  scale: 1.2,       // scale
  rotation: 45,     // rotate
  opacity: 0.5      // opacity
})
```

### Layout-Triggering Properties (Bad)

```typescript
// ❌ BAD - Layout-triggering properties (CPU, causes reflow)
gsap.to(element, {
  left: 100,        // Triggers layout
  top: 50,          // Triggers layout
  width: '120%',    // Triggers layout
  height: 200,      // Triggers layout
  margin: 10        // Triggers layout
})
```

### Performance Comparison

| Property | Type | Performance | Use Case |
|----------|------|-------------|----------|
| `x`, `y` | Transform | 🚀 GPU | Position changes |
| `left`, `top` | Layout | 🐌 CPU | Avoid for animations |
| `scale` | Transform | 🚀 GPU | Size changes |
| `width`, `height` | Layout | 🐌 CPU | Avoid for animations |
| `rotation` | Transform | 🚀 GPU | Rotation |
| `opacity` | Composite | 🚀 GPU | Fade effects |

## 6.3 Timeline Reuse

### Good: Reuse Timeline Instance

```typescript
// ✅ Create once, reuse many times
const timeline = gsap.timeline({ paused: true })
timeline
  .to(element, { opacity: 1, duration: 0.3 })
  .to(element, { y: -20, duration: 0.5 })

// Play/reverse as needed
const show = () => timeline.play()
const hide = () => timeline.reverse()
```

### Bad: Creating New Timeline Each Time

```typescript
// ❌ Creates new timeline every call (memory inefficient)
const showBad = () => {
  gsap.timeline()
    .to(element, { opacity: 1, duration: 0.3 })
    .to(element, { y: -20, duration: 0.5 })
}

const hideBad = () => {
  gsap.timeline()
    .to(element, { opacity: 0, duration: 0.3 })
    .to(element, { y: 0, duration: 0.5 })
}
```

### Best Practice with Composable

```typescript
export function useReusableTimeline(
  createTimeline: () => gsap.core.Timeline
) {
  let timeline: gsap.core.Timeline | null = null

  const getTimeline = () => {
    if (!timeline) {
      timeline = createTimeline()
    }
    return timeline
  }

  const play = () => getTimeline().play()
  const reverse = () => getTimeline().reverse()
  const restart = () => getTimeline().restart()

  onUnmounted(() => {
    timeline?.kill()
    timeline = null
  })

  return { play, reverse, restart }
}

// Usage
const { play, reverse } = useReusableTimeline(() => {
  return gsap.timeline({ paused: true })
    .to(element, { opacity: 1, duration: 0.3 })
    .to(element, { y: -20, duration: 0.5 })
})
```

## 6.4 ScrollTrigger Batching

### Good: Batch ScrollTrigger Animations

```typescript
// ✅ Single ScrollTrigger for multiple elements
ScrollTrigger.batch('.animate-item', {
  onEnter: (elements) => {
    gsap.to(elements, {
      opacity: 1,
      y: 0,
      stagger: 0.1,
      overwrite: true
    })
  },
  onLeave: (elements) => {
    gsap.to(elements, {
      opacity: 0,
      y: -20,
      overwrite: true
    })
  }
})
```

### Bad: Individual ScrollTrigger Per Element

```typescript
// ❌ Creates separate ScrollTrigger for EACH element (inefficient)
document.querySelectorAll('.animate-item').forEach(item => {
  gsap.to(item, {
    scrollTrigger: {
      trigger: item,
      start: 'top 80%'
    },
    opacity: 1,
    y: 0
  })
})
```

### Advanced Batching with Options

```typescript
export function batchScrollAnimation(
  selector: string,
  options: {
    interval?: number
    batchMax?: number
    onEnter?: gsap.TweenVars
    onLeave?: gsap.TweenVars
  } = {}
) {
  const {
    interval = 0.1,
    batchMax = 5,
    onEnter = { opacity: 1, y: 0 },
    onLeave = { opacity: 0, y: -20 }
  } = options

  ScrollTrigger.batch(selector, {
    interval,
    batchMax,
    onEnter: (elements) => {
      gsap.to(elements, {
        ...onEnter,
        stagger: { each: 0.1, from: 'start' },
        overwrite: true
      })
    },
    onLeave: (elements) => {
      gsap.to(elements, {
        ...onLeave,
        overwrite: true
      })
    }
  })
}

// Usage
batchScrollAnimation('.panel-item', {
  interval: 0.2,
  batchMax: 3,
  onEnter: { opacity: 1, x: 0, scale: 1 },
  onLeave: { opacity: 0, x: -30, scale: 0.95 }
})
```

## 6.5 Lazy Initialization

### Good: Initialize Only When Needed

```typescript
let panelAnimation: gsap.core.Timeline | null = null

const getPanelAnimation = () => {
  if (!panelAnimation) {
    panelAnimation = gsap.timeline({ paused: true })
      .from('.panel', { opacity: 0, y: 20 })
      .from('.panel-content', { opacity: 0, stagger: 0.1 })
  }
  return panelAnimation
}

const showPanel = () => getPanelAnimation().play()
const hidePanel = () => getPanelAnimation().reverse()
```

### Bad: Initialize All Animations On Mount

```typescript
// ❌ Creates all timelines even if never used
onMounted(() => {
  const animation1 = gsap.timeline().to('.panel1', { x: 100 })
  const animation2 = gsap.timeline().to('.panel2', { y: 100 })
  const animation3 = gsap.timeline().to('.panel3', { scale: 1.2 })
  // These animations consume memory even if panels are never shown
})
```

### Best Practice with Composable

```typescript
export function useLazyAnimation<T extends Record<string, any>>(
  animations: Record<keyof T, () => gsap.core.Timeline | gsap.core.Tween>
) {
  const cache = new Map<keyof T, gsap.core.Timeline | gsap.core.Tween>()

  const get = (name: keyof T) => {
    if (!cache.has(name)) {
      cache.set(name, animations[name]())
    }
    return cache.get(name)!
  }

  const play = (name: keyof T) => {
    const animation = get(name)
    if ('play' in animation) animation.play()
  }

  const cleanup = () => {
    cache.forEach(animation => animation.kill())
    cache.clear()
  }

  onUnmounted(cleanup)

  return { play, get, cleanup }
}

// Usage
const { play } = useLazyAnimation({
  intro: () => gsap.timeline()
    .from('.logo', { opacity: 0, scale: 0 })
    .from('.panels', { opacity: 0, x: -30, stagger: 0.1 }),

  exit: () => gsap.timeline()
    .to('.panels', { opacity: 0, x: 30, stagger: 0.05 })
    .to('.logo', { opacity: 0, scale: 0 })
})

// Only creates timeline when first played
play('intro')
```

## 6.6 QuickSetter for Frequent Updates

### Good: Use quickSetter for High-Frequency Updates

```typescript
// ✅ Much faster for frequent updates (e.g., mouse tracking)
const setX = gsap.quickSetter(element, 'x', 'px')
const setY = gsap.quickSetter(element, 'y', 'px')
const setRotation = gsap.quickSetter(element, 'rotation', 'deg')

// In animation loop or event handler
function onMouseMove(e: MouseEvent) {
  setX(e.clientX)
  setY(e.clientY)
  setRotation(e.clientX * 0.1)
}
```

### Bad: Using gsap.set in Loops

```typescript
// ❌ Slower for frequent updates
function onMouseMove(e: MouseEvent) {
  gsap.set(element, {
    x: e.clientX,
    y: e.clientY,
    rotation: e.clientX * 0.1
  })
}
```

### Performance Comparison

| Method | Updates/sec | Use Case |
|--------|-------------|----------|
| `quickSetter` | ~10,000 | Mouse tracking, game loops |
| `gsap.set` | ~1,000 | Occasional updates |
| Regular CSS | ~100 | Static styling |

## 6.7 Force3D Optimization

### Enable 3D Transforms for Better Performance

```typescript
// ✅ Force GPU layer creation
gsap.to(element, {
  x: 100,
  force3D: true,  // Creates GPU layer immediately
  duration: 1
})

// Or set globally
gsap.config({ force3D: true })
```

### When to Use force3D

- ✅ Complex animations with multiple properties
- ✅ Animations that may stutter
- ✅ Elements that animate frequently
- ❌ Simple fade-in/out (unnecessary overhead)
- ❌ Static elements (wastes memory)

## Performance Monitoring

### Check Animation Performance

```typescript
// Enable GSAP performance metrics
gsap.ticker.lagSmoothing(0)

// Monitor frame rate
let frameCount = 0
let lastTime = performance.now()

gsap.ticker.add(() => {
  frameCount++
  const currentTime = performance.now()

  if (currentTime - lastTime >= 1000) {
    console.log(`FPS: ${frameCount}`)
    frameCount = 0
    lastTime = currentTime
  }
})
```

### Memory Leak Detection

```typescript
// Check for leaked animations
const checkLeaks = () => {
  const activeAnimations = gsap.globalTimeline.getChildren()
  console.log(`Active animations: ${activeAnimations.length}`)

  if (activeAnimations.length > 50) {
    console.warn('⚠️ Possible memory leak: too many active animations')
  }
}

// Run periodically in development
if (import.meta.env.DEV) {
  setInterval(checkLeaks, 5000)
}
```

## Performance Checklist

Before deploying animations:

- [ ] All animations use GPU-accelerated properties (transform, opacity)
- [ ] will-change applied before animation, removed after
- [ ] Timelines reused instead of recreated
- [ ] ScrollTrigger animations batched
- [ ] Complex animations lazy-initialized
- [ ] quickSetter used for high-frequency updates
- [ ] All animations killed on unmount
- [ ] No memory leaks (check DevTools)
- [ ] 60fps maintained (test with performance monitor)
- [ ] force3D enabled for complex animations
