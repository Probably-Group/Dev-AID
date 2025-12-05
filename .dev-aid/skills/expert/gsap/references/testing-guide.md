# GSAP Animation Testing Guide

This file contains comprehensive testing strategies for GSAP animations.

## Animation Testing

### Basic Animation Test

```typescript
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { gsap } from 'gsap'
import HUDPanel from '~/components/HUDPanel.vue'

describe('HUDPanel Animation', () => {
  beforeEach(() => {
    // Mock reduced motion
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: vi.fn().mockImplementation(query => ({
        matches: false,
        media: query
      }))
    })
  })

  afterEach(() => {
    // Verify cleanup
    gsap.globalTimeline.clear()
  })

  it('animates panel entrance with correct properties', async () => {
    const wrapper = mount(HUDPanel)

    // Wait for animation to complete
    await new Promise(resolve => setTimeout(resolve, 600))

    const panel = wrapper.find('.hud-panel')
    expect(panel.exists()).toBe(true)
  })

  it('cleans up animations on unmount', async () => {
    const wrapper = mount(HUDPanel)
    const childCount = gsap.globalTimeline.getChildren().length

    await wrapper.unmount()

    // All animations should be killed
    expect(gsap.globalTimeline.getChildren().length).toBeLessThan(childCount)
  })

  it('respects reduced motion preference', async () => {
    // Mock reduced motion enabled
    window.matchMedia = vi.fn().mockImplementation(() => ({
      matches: true
    }))

    const wrapper = mount(HUDPanel)
    const panel = wrapper.find('.hud-panel').element

    // Should set final state immediately without animation
    expect(gsap.getProperty(panel, 'opacity')).toBe(1)
  })
})
```

## Testing Timeline Sequences

```typescript
describe('Timeline Sequence', () => {
  it('executes timeline in correct order', async () => {
    const events: string[] = []

    const tl = gsap.timeline()
      .add(() => events.push('start'))
      .to('.element', { x: 100, duration: 0.1 })
      .add(() => events.push('middle'))
      .to('.element', { y: 100, duration: 0.1 })
      .add(() => events.push('end'))

    await tl.then()

    expect(events).toEqual(['start', 'middle', 'end'])
  })

  it('properly handles timeline labels', () => {
    const tl = gsap.timeline({ paused: true })
      .add('intro')
      .to('.element', { opacity: 1 }, 'intro')
      .add('main', '+=0.5')
      .to('.element', { x: 100 }, 'main')

    // Jump to label
    tl.seek('main')

    expect(tl.time()).toBeGreaterThan(0)
  })
})
```

## Testing ScrollTrigger

```typescript
import { ScrollTrigger } from 'gsap/ScrollTrigger'

describe('ScrollTrigger Animation', () => {
  beforeEach(() => {
    gsap.registerPlugin(ScrollTrigger)
  })

  afterEach(() => {
    ScrollTrigger.getAll().forEach(trigger => trigger.kill())
  })

  it('creates ScrollTrigger instance', () => {
    const element = document.createElement('div')
    document.body.appendChild(element)

    gsap.to(element, {
      scrollTrigger: {
        trigger: element,
        start: 'top 80%'
      },
      opacity: 1
    })

    const triggers = ScrollTrigger.getAll()
    expect(triggers.length).toBe(1)
  })

  it('cleans up ScrollTrigger on kill', () => {
    const element = document.createElement('div')

    const animation = gsap.to(element, {
      scrollTrigger: {
        trigger: element,
        start: 'top 80%'
      },
      opacity: 1
    })

    animation.kill()

    expect(ScrollTrigger.getAll().length).toBe(0)
  })
})
```

## Testing Reduced Motion

```typescript
describe('Reduced Motion Support', () => {
  it('skips animation when reduced motion is preferred', () => {
    window.matchMedia = vi.fn().mockImplementation(() => ({
      matches: true
    }))

    const element = document.createElement('div')
    const prefersReducedMotion = window.matchMedia(
      '(prefers-reduced-motion: reduce)'
    ).matches

    if (prefersReducedMotion) {
      gsap.set(element, { opacity: 1 })
    } else {
      gsap.from(element, { opacity: 0, duration: 0.5 })
    }

    expect(gsap.getProperty(element, 'opacity')).toBe(1)
  })

  it('enables animation when reduced motion is not preferred', () => {
    window.matchMedia = vi.fn().mockImplementation(() => ({
      matches: false
    }))

    const element = document.createElement('div')
    const prefersReducedMotion = window.matchMedia(
      '(prefers-reduced-motion: reduce)'
    ).matches

    expect(prefersReducedMotion).toBe(false)
  })
})
```

## Memory Leak Testing

```typescript
describe('Memory Leak Prevention', () => {
  it('prevents memory leaks with proper cleanup', async () => {
    const elements = Array.from({ length: 100 }, () =>
      document.createElement('div')
    )

    const animations = elements.map(el =>
      gsap.to(el, { x: 100, duration: 1 })
    )

    // Kill all animations
    animations.forEach(a => a.kill())

    // No animations should remain
    expect(gsap.globalTimeline.getChildren().length).toBe(0)
  })

  it('detects animation leaks', () => {
    // Create animations without cleanup
    for (let i = 0; i < 10; i++) {
      gsap.to(document.createElement('div'), { x: 100 })
    }

    const activeCount = gsap.globalTimeline.getChildren().length
    expect(activeCount).toBeGreaterThan(0)

    // Cleanup
    gsap.globalTimeline.clear()
  })
})
```

## Performance Testing

```typescript
describe('Animation Performance', () => {
  it('maintains 60fps for simple animations', async () => {
    const element = document.createElement('div')
    const frameRates: number[] = []
    let lastTime = performance.now()

    const ticker = () => {
      const currentTime = performance.now()
      const fps = 1000 / (currentTime - lastTime)
      frameRates.push(fps)
      lastTime = currentTime
    }

    gsap.ticker.add(ticker)

    gsap.to(element, { x: 100, duration: 1 })

    await new Promise(resolve => setTimeout(resolve, 1000))

    gsap.ticker.remove(ticker)

    const avgFps = frameRates.reduce((a, b) => a + b, 0) / frameRates.length
    expect(avgFps).toBeGreaterThan(50) // Allow some variance
  })

  it('uses GPU-accelerated properties', () => {
    const element = document.createElement('div')

    gsap.to(element, {
      x: 100,
      y: 50,
      rotation: 45,
      scale: 1.2,
      opacity: 0.5
    })

    // Check that transform is used (not left/top)
    const transform = getComputedStyle(element).transform
    expect(transform).not.toBe('none')
  })
})
```

## Integration Testing with Vue Components

```typescript
describe('Vue Component Integration', () => {
  it('animates component on mount', async () => {
    const wrapper = mount(AnimatedPanel)

    await wrapper.vm.$nextTick()

    const panel = wrapper.find('.panel').element
    const opacity = gsap.getProperty(panel, 'opacity')

    expect(opacity).toBeGreaterThan(0)
  })

  it('cleans up on component unmount', async () => {
    const wrapper = mount(AnimatedPanel)
    const initialCount = gsap.globalTimeline.getChildren().length

    await wrapper.unmount()

    const finalCount = gsap.globalTimeline.getChildren().length
    expect(finalCount).toBeLessThan(initialCount)
  })

  it('responds to prop changes', async () => {
    const wrapper = mount(AnimatedPanel, {
      props: { isVisible: false }
    })

    await wrapper.setProps({ isVisible: true })
    await wrapper.vm.$nextTick()

    const panel = wrapper.find('.panel').element
    expect(gsap.getProperty(panel, 'opacity')).toBe(1)
  })
})
```

## Test Utilities

### Animation Test Helper

```typescript
export function waitForAnimation(duration: number): Promise<void> {
  return new Promise(resolve => {
    setTimeout(resolve, duration * 1000 + 100) // Add buffer
  })
}

export function mockReducedMotion(enabled: boolean) {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation(() => ({
      matches: enabled,
      media: '(prefers-reduced-motion: reduce)'
    }))
  })
}

export function getActiveAnimationCount(): number {
  return gsap.globalTimeline.getChildren().length
}

export function clearAllAnimations(): void {
  gsap.globalTimeline.clear()
  ScrollTrigger.getAll().forEach(trigger => trigger.kill())
}
```

### Usage Example

```typescript
import { waitForAnimation, mockReducedMotion, clearAllAnimations } from './test-utils'

describe('With Test Utilities', () => {
  beforeEach(() => {
    mockReducedMotion(false)
  })

  afterEach(() => {
    clearAllAnimations()
  })

  it('completes animation', async () => {
    const element = document.createElement('div')
    gsap.to(element, { x: 100, duration: 0.5 })

    await waitForAnimation(0.5)

    expect(gsap.getProperty(element, 'x')).toBe(100)
  })
})
```

## Test Coverage Checklist

- [ ] Animation executes with correct properties
- [ ] Animation completes successfully
- [ ] Cleanup on unmount (no memory leaks)
- [ ] Reduced motion preference respected
- [ ] Timeline sequences execute in order
- [ ] ScrollTrigger instances created/destroyed
- [ ] Performance maintains 60fps
- [ ] GPU-accelerated properties used
- [ ] Props/state changes trigger animations
- [ ] Error handling (missing elements, etc.)

## Continuous Integration

```yaml
# .github/workflows/animation-tests.yml
name: Animation Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm install
      - run: npm test -- --grep "Animation"
      - run: npm run test:memory
      - run: npm run test:performance
```
