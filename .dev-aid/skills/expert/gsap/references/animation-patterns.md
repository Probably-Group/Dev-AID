# GSAP Animation Patterns

This file contains detailed implementation patterns for common GSAP animations in the JARVIS HUD.

## 4.1 Panel Entrance Animation

```vue
<script setup lang="ts">
import { gsap } from 'gsap'
import { onMounted, onUnmounted, ref } from 'vue'

const panelRef = ref<HTMLElement | null>(null)
let animation: gsap.core.Tween | null = null

onMounted(() => {
  if (!panelRef.value) return

  // ✅ Check reduced motion preference
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    gsap.set(panelRef.value, { opacity: 1 })
    return
  }

  animation = gsap.from(panelRef.value, {
    opacity: 0,
    y: 20,
    scale: 0.95,
    duration: 0.5,
    ease: 'power2.out'
  })
})

// ✅ Cleanup on unmount
onUnmounted(() => {
  animation?.kill()
})
</script>

<template>
  <div ref="panelRef" class="hud-panel">
    <slot />
  </div>
</template>
```

## 4.2 Status Indicator Animation

```typescript
// composables/useStatusAnimation.ts
import { gsap } from 'gsap'

export function useStatusAnimation(element: Ref<HTMLElement | null>) {
  const timeline = ref<gsap.core.Timeline | null>(null)

  const animateStatus = (status: string) => {
    if (!element.value) return

    timeline.value?.kill()

    timeline.value = gsap.timeline()

    switch (status) {
      case 'active':
        timeline.value
          .to(element.value, {
            scale: 1.2,
            duration: 0.2,
            ease: 'power2.out'
          })
          .to(element.value, {
            scale: 1,
            duration: 0.3,
            ease: 'elastic.out(1, 0.3)'
          })
        break

      case 'warning':
        timeline.value.to(element.value, {
          backgroundColor: '#f59e0b',
          boxShadow: '0 0 10px #f59e0b',
          duration: 0.3,
          repeat: 2,
          yoyo: true
        })
        break

      case 'error':
        timeline.value.to(element.value, {
          x: -5,
          duration: 0.05,
          repeat: 5,
          yoyo: true
        })
        break
    }
  }

  onUnmounted(() => {
    timeline.value?.kill()
  })

  return { animateStatus }
}
```

## 4.3 Data Visualization Animation

```vue
<script setup lang="ts">
import { gsap } from 'gsap'

const props = defineProps<{
  data: number[]
}>()

const barsRef = ref<HTMLElement[]>([])
let animations: gsap.core.Tween[] = []

watch(() => props.data, (newData) => {
  // Kill previous animations
  animations.forEach(a => a.kill())
  animations = []

  // Animate each bar
  newData.forEach((value, index) => {
    const bar = barsRef.value[index]
    if (!bar) return

    const tween = gsap.to(bar, {
      height: `${value}%`,
      duration: 0.5,
      delay: index * 0.05,
      ease: 'power2.out'
    })

    animations.push(tween)
  })
}, { immediate: true })

onUnmounted(() => {
  animations.forEach(a => a.kill())
})
</script>

<template>
  <div class="flex items-end h-40 gap-1">
    <div
      v-for="(_, index) in data"
      :key="index"
      ref="barsRef"
      class="w-4 bg-jarvis-primary"
    />
  </div>
</template>
```

## 4.4 Timeline Sequence

```typescript
// Create complex HUD startup sequence
export function createStartupSequence(elements: {
  logo: HTMLElement
  panels: HTMLElement[]
  status: HTMLElement
}): gsap.core.Timeline {
  const tl = gsap.timeline({
    defaults: { ease: 'power2.out' }
  })

  // Logo reveal
  tl.from(elements.logo, {
    opacity: 0,
    scale: 0,
    duration: 0.8,
    ease: 'back.out(1.7)'
  })

  // Panels stagger in
  tl.from(elements.panels, {
    opacity: 0,
    x: -30,
    stagger: 0.1,
    duration: 0.5
  }, '-=0.3')

  // Status indicator
  tl.from(elements.status, {
    opacity: 0,
    y: 10,
    duration: 0.3
  }, '-=0.2')

  return tl
}
```

## 4.5 Scroll-Triggered Animation

```vue
<script setup lang="ts">
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

const sectionRef = ref<HTMLElement | null>(null)

onMounted(() => {
  if (!sectionRef.value) return

  gsap.from(sectionRef.value.querySelectorAll('.animate-item'), {
    scrollTrigger: {
      trigger: sectionRef.value,
      start: 'top 80%',
      end: 'bottom 20%',
      toggleActions: 'play none none reverse'
    },
    opacity: 0,
    y: 30,
    stagger: 0.1,
    duration: 0.5
  })
})

onUnmounted(() => {
  ScrollTrigger.getAll().forEach(trigger => trigger.kill())
})
</script>
```

## Best Practices for Animation Patterns

### Pattern Selection

- **Simple entrance/exit**: Use single tweens (4.1)
- **State changes**: Use timelines with multiple steps (4.2)
- **Data updates**: Use arrays and stagger (4.3)
- **Complex sequences**: Use labeled timelines (4.4)
- **Scroll effects**: Use ScrollTrigger with batch (4.5)

### Performance Considerations

- Always use GPU-accelerated properties (transform, opacity)
- Clean up animations on unmount
- Respect reduced motion preferences
- Use `will-change` hints for complex animations (remove after)
- Batch similar animations together

### Accessibility

All patterns should check for reduced motion:

```typescript
const prefersReducedMotion = window.matchMedia(
  '(prefers-reduced-motion: reduce)'
).matches

if (prefersReducedMotion) {
  gsap.set(element, { opacity: 1 })
} else {
  gsap.from(element, { opacity: 0, duration: 0.5 })
}
```
