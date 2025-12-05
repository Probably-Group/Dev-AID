# Three.js/TresJS Testing Guide

## TDD Process for 3D Components

### Step 1: Write Failing Test First

```typescript
// tests/components/hud-panel.test.ts
import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { Scene, WebGLRenderer } from 'three'
import HUDPanel from '~/components/hud/HUDPanel.vue'

describe('HUDPanel', () => {
  let wrapper: VueWrapper

  beforeEach(() => {
    // Mock WebGL context for testing
    const canvas = document.createElement('canvas')
    const gl = canvas.getContext('webgl2')
    vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue(gl)
  })

  afterEach(() => {
    wrapper?.unmount()
    vi.restoreAllMocks()
  })

  it('renders panel with correct dimensions', () => {
    wrapper = mount(HUDPanel, {
      props: { width: 2, height: 1, title: 'Status' }
    })

    // Test fails until component is implemented
    expect(wrapper.exists()).toBe(true)
  })

  it('disposes resources on unmount', async () => {
    wrapper = mount(HUDPanel, {
      props: { width: 2, height: 1, title: 'Status' }
    })

    const disposeSpy = vi.fn()
    wrapper.vm.meshRef.geometry.dispose = disposeSpy

    wrapper.unmount()
    expect(disposeSpy).toHaveBeenCalled()
  })
})
```

### Step 2: Implement Minimum to Pass

```vue
<script setup lang="ts">
import { shallowRef, onUnmounted } from 'vue'
import { Mesh } from 'three'

const props = defineProps<{
  width: number
  height: number
  title: string
}>()

const meshRef = shallowRef<Mesh | null>(null)

onUnmounted(() => {
  if (meshRef.value) {
    meshRef.value.geometry.dispose()
    ;(meshRef.value.material as any).dispose()
  }
})
</script>

<template>
  <TresMesh ref="meshRef">
    <TresPlaneGeometry :args="[props.width, props.height]" />
    <TresMeshBasicMaterial color="#001122" :transparent="true" :opacity="0.8" />
  </TresMesh>
</template>
```

### Step 3: Refactor Following Patterns

```typescript
// After tests pass, add performance optimizations
// - Use instancing for multiple panels
// - Add LOD for distant panels
// - Implement texture atlases for text
```

### Step 4: Run Full Verification

```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Type check
npm run typecheck

# Performance benchmark
npm run test:perf
```

## Testing 3D Animations

```typescript
import { describe, it, expect, vi } from 'vitest'
import { useRenderLoop } from '@tresjs/core'

describe('Animation Loop', () => {
  it('maintains 60fps during animation', async () => {
    const frameTimes: number[] = []
    let lastTime = performance.now()

    const { onLoop } = useRenderLoop()

    onLoop(() => {
      const now = performance.now()
      frameTimes.push(now - lastTime)
      lastTime = now
    })

    // Simulate 60 frames
    await new Promise(resolve => setTimeout(resolve, 1000))

    const avgFrameTime = frameTimes.reduce((a, b) => a + b, 0) / frameTimes.length
    expect(avgFrameTime).toBeLessThan(16.67) // 60fps = 16.67ms per frame
  })

  it('cleans up animation loop on unmount', () => {
    const cleanup = vi.fn()
    const { pause } = useRenderLoop()

    // Component unmounts
    pause()

    expect(cleanup).not.toThrow()
  })
})
```

## Testing Resource Disposal

```typescript
describe('Resource Management', () => {
  it('disposes all GPU resources', () => {
    const geometry = new BoxGeometry(1, 1, 1)
    const material = new MeshStandardMaterial({ color: 0x00ff41 })
    const mesh = new Mesh(geometry, material)

    const geoDispose = vi.spyOn(geometry, 'dispose')
    const matDispose = vi.spyOn(material, 'dispose')

    // Cleanup function
    mesh.geometry.dispose()
    mesh.material.dispose()

    expect(geoDispose).toHaveBeenCalled()
    expect(matDispose).toHaveBeenCalled()
  })

  it('handles material arrays correctly', () => {
    const materials = [
      new MeshBasicMaterial(),
      new MeshStandardMaterial()
    ]
    const mesh = new Mesh(new BoxGeometry(), materials)

    const spies = materials.map(m => vi.spyOn(m, 'dispose'))

    materials.forEach(m => m.dispose())

    spies.forEach(spy => expect(spy).toHaveBeenCalled())
  })
})
```

## Component Testing

```typescript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'

describe('HUD Panel', () => {
  it('sanitizes malicious title input', () => {
    const wrapper = mount(HUDPanel, {
      props: {
        title: '<script>alert("xss")</script>Status',
        value: 75
      }
    })

    expect(wrapper.vm.safeTitle).not.toContain('<script>')
  })
})
```

## Performance Testing

```typescript
describe('Instanced Mesh', () => {
  it('handles 1000 instances without frame drop', async () => {
    const scene = new Scene()
    // Setup instanced mesh...

    const startTime = performance.now()
    renderer.render(scene, camera)
    const renderTime = performance.now() - startTime

    expect(renderTime).toBeLessThan(16.67)  // 60fps target
  })
})
```
