# Three.js/TresJS 3D-Specific Patterns

## JARVIS HUD Interface Patterns

### Holographic Panel Design

```vue
<script setup lang="ts">
import { computed, shallowRef } from 'vue'
import { Text } from '@tresjs/cientos'
import { Color } from 'three'

interface Props {
  title: string
  data: Record<string, any>
  position?: [number, number, number]
  opacity?: number
}

const props = withDefaults(defineProps<Props>(), {
  position: () => [0, 0, 0],
  opacity: 0.8
})

// Sanitize for XSS
const safeTitle = computed(() =>
  props.title.replace(/[<>]/g, '').slice(0, 50)
)

const panelColor = new Color(0x001122)
const accentColor = '#00ff41'
</script>

<template>
  <TresGroup :position="props.position">
    <!-- Panel background with glow -->
    <TresMesh>
      <TresPlaneGeometry :args="[3, 2]" />
      <TresMeshBasicMaterial
        :color="panelColor"
        :transparent="true"
        :opacity="props.opacity"
      />
    </TresMesh>

    <!-- Border glow effect -->
    <TresLine>
      <TresEdgesGeometry :args="[new PlaneGeometry(3, 2)]" />
      <TresLineBasicMaterial :color="accentColor" />
    </TresLine>

    <!-- Title -->
    <Text
      :text="safeTitle"
      :font-size="0.2"
      :color="accentColor"
      :position="[-1.3, 0.8, 0.01]"
    />

    <!-- Data display -->
    <slot />
  </TresGroup>
</template>
```

### Animated Status Indicators

```vue
<script setup lang="ts">
import { useRenderLoop } from '@tresjs/core'
import { shallowRef } from 'vue'
import { Mesh } from 'three'

interface Props {
  status: 'ok' | 'warning' | 'error'
  position?: [number, number, number]
}

const props = withDefaults(defineProps<Props>(), {
  position: () => [0, 0, 0]
})

const statusColors = {
  ok: 0x00ff41,
  warning: 0xffaa00,
  error: 0xff0000
}

const ringRef = shallowRef<Mesh | null>(null)

useRenderLoop().onLoop(({ elapsed }) => {
  if (ringRef.value) {
    ringRef.value.rotation.z = elapsed * 2
    // Pulse effect
    const scale = 1 + Math.sin(elapsed * 3) * 0.1
    ringRef.value.scale.set(scale, scale, 1)
  }
})
</script>

<template>
  <TresGroup :position="props.position">
    <!-- Rotating ring -->
    <TresMesh ref="ringRef">
      <TresRingGeometry :args="[0.4, 0.5, 32]" />
      <TresMeshBasicMaterial :color="statusColors[props.status]" />
    </TresMesh>

    <!-- Center indicator -->
    <TresMesh :position="[0, 0, 0.01]">
      <TresCircleGeometry :args="[0.3, 32]" />
      <TresMeshBasicMaterial
        :color="statusColors[props.status]"
        :transparent="true"
        :opacity="0.5"
      />
    </TresMesh>
  </TresGroup>
</template>
```

### Particle System for Data Visualization

```vue
<script setup lang="ts">
import { onMounted, onUnmounted, shallowRef } from 'vue'
import { useRenderLoop } from '@tresjs/core'
import { Points, BufferGeometry, BufferAttribute, PointsMaterial } from 'three'

const particleCount = 1000
const particlesRef = shallowRef<Points | null>(null)

onMounted(() => {
  if (!particlesRef.value) return

  const geometry = particlesRef.value.geometry as BufferGeometry
  const positions = new Float32Array(particleCount * 3)
  const velocities = new Float32Array(particleCount * 3)

  for (let i = 0; i < particleCount * 3; i += 3) {
    positions[i] = (Math.random() - 0.5) * 10
    positions[i + 1] = (Math.random() - 0.5) * 10
    positions[i + 2] = (Math.random() - 0.5) * 10

    velocities[i] = (Math.random() - 0.5) * 0.02
    velocities[i + 1] = (Math.random() - 0.5) * 0.02
    velocities[i + 2] = (Math.random() - 0.5) * 0.02
  }

  geometry.setAttribute('position', new BufferAttribute(positions, 3))
  geometry.setAttribute('velocity', new BufferAttribute(velocities, 3))
})

useRenderLoop().onLoop(() => {
  if (!particlesRef.value) return

  const geometry = particlesRef.value.geometry as BufferGeometry
  const positions = geometry.attributes.position.array as Float32Array
  const velocities = geometry.attributes.velocity.array as Float32Array

  for (let i = 0; i < positions.length; i += 3) {
    positions[i] += velocities[i]
    positions[i + 1] += velocities[i + 1]
    positions[i + 2] += velocities[i + 2]

    // Boundary check
    if (Math.abs(positions[i]) > 5) velocities[i] *= -1
    if (Math.abs(positions[i + 1]) > 5) velocities[i + 1] *= -1
    if (Math.abs(positions[i + 2]) > 5) velocities[i + 2] *= -1
  }

  geometry.attributes.position.needsUpdate = true
})

onUnmounted(() => {
  if (particlesRef.value) {
    particlesRef.value.geometry.dispose()
    ;(particlesRef.value.material as PointsMaterial).dispose()
  }
})
</script>

<template>
  <TresPoints ref="particlesRef">
    <TresBufferGeometry />
    <TresPointsMaterial
      color="#00ff41"
      :size="0.05"
      :transparent="true"
      :opacity="0.6"
    />
  </TresPoints>
</template>
```

## Advanced 3D Techniques

### Dynamic Level of Detail (LOD)

```vue
<script setup lang="ts">
import { LOD } from 'three'
import { shallowRef, onMounted } from 'vue'

const lodRef = shallowRef<LOD | null>(null)

onMounted(() => {
  // LOD levels are set up via template
  // Can also be configured programmatically here
})
</script>

<template>
  <TresLOD ref="lodRef">
    <!-- High detail - close range (0-10 units) -->
    <TresMesh :distance="0">
      <TresSphereGeometry :args="[1, 32, 32]" />
      <TresMeshStandardMaterial color="#00ff41" />
    </TresMesh>

    <!-- Medium detail - mid range (10-20 units) -->
    <TresMesh :distance="10">
      <TresSphereGeometry :args="[1, 16, 16]" />
      <TresMeshStandardMaterial color="#00ff41" />
    </TresMesh>

    <!-- Low detail - far range (20+ units) -->
    <TresMesh :distance="20">
      <TresSphereGeometry :args="[1, 8, 8]" />
      <TresMeshBasicMaterial color="#00ff41" />
    </TresMesh>
  </TresLOD>
</template>
```

### Ray-cast Interaction

```vue
<script setup lang="ts">
import { useRaycaster } from '@tresjs/core'
import { shallowRef } from 'vue'
import { Mesh } from 'three'

const meshRef = shallowRef<Mesh | null>(null)
const isHovered = ref(false)

const { onClick, onPointerMove } = useRaycaster()

onPointerMove((intersects) => {
  isHovered.value = intersects.some(i => i.object === meshRef.value)
})

onClick((intersects) => {
  const hit = intersects.find(i => i.object === meshRef.value)
  if (hit) {
    console.log('Panel clicked at:', hit.point)
    emit('click', hit)
  }
})
</script>

<template>
  <TresMesh ref="meshRef">
    <TresPlaneGeometry :args="[2, 1]" />
    <TresMeshBasicMaterial
      :color="isHovered ? '#00ff41' : '#001122'"
      :transparent="true"
      :opacity="0.8"
    />
  </TresMesh>
</template>
```

### Camera Animation Patterns

```vue
<script setup lang="ts">
import { useRenderLoop } from '@tresjs/core'
import { shallowRef } from 'vue'
import { PerspectiveCamera, Vector3 } from 'three'
import { gsap } from 'gsap'

const cameraRef = shallowRef<PerspectiveCamera | null>(null)

function animateToPosition(target: Vector3, lookAt: Vector3) {
  if (!cameraRef.value) return

  gsap.to(cameraRef.value.position, {
    x: target.x,
    y: target.y,
    z: target.z,
    duration: 2,
    ease: 'power2.inOut',
    onUpdate: () => {
      cameraRef.value?.lookAt(lookAt)
    }
  })
}

defineExpose({ animateToPosition })
</script>

<template>
  <TresPerspectiveCamera
    ref="cameraRef"
    :position="[0, 0, 5]"
    :fov="75"
    :near="0.1"
    :far="1000"
  />
</template>
```

### Post-Processing Stack

```vue
<script setup lang="ts">
import { EffectComposer, Bloom, ChromaticAberration, Glitch } from '@tresjs/post-processing'

const bloomOptions = {
  luminanceThreshold: 0.9,
  luminanceSmoothing: 0.3,
  intensity: 1.5
}

const chromaticAberrationOptions = {
  offset: [0.002, 0.002]
}

const glitchActive = ref(false)

// Trigger glitch on system alerts
function triggerGlitch() {
  glitchActive.value = true
  setTimeout(() => {
    glitchActive.value = false
  }, 500)
}

defineExpose({ triggerGlitch })
</script>

<template>
  <EffectComposer>
    <Bloom v-bind="bloomOptions" />
    <ChromaticAberration v-bind="chromaticAberrationOptions" />
    <Glitch
      :active="glitchActive"
      :strength="[0.3, 0.3]"
      :delay="[0.5, 1]"
    />
  </EffectComposer>
</template>
```

## Performance Patterns for 3D Scenes

### Instanced HUD Elements

```vue
<script setup lang="ts">
import { onMounted, shallowRef } from 'vue'
import { InstancedMesh, Object3D, Matrix4 } from 'three'

const instanceCount = 50
const instancedMeshRef = shallowRef<InstancedMesh | null>(null)

interface DataPoint {
  position: [number, number, number]
  color: number
  scale: number
}

const props = defineProps<{
  dataPoints: DataPoint[]
}>()

onMounted(() => {
  updateInstances()
})

watch(() => props.dataPoints, updateInstances)

function updateInstances() {
  if (!instancedMeshRef.value) return

  const dummy = new Object3D()

  props.dataPoints.forEach((point, i) => {
    dummy.position.set(...point.position)
    dummy.scale.setScalar(point.scale)
    dummy.updateMatrix()

    instancedMeshRef.value?.setMatrixAt(i, dummy.matrix)
    instancedMeshRef.value?.setColorAt(i, new Color(point.color))
  })

  instancedMeshRef.value.instanceMatrix.needsUpdate = true
  if (instancedMeshRef.value.instanceColor) {
    instancedMeshRef.value.instanceColor.needsUpdate = true
  }
}
</script>

<template>
  <TresInstancedMesh ref="instancedMeshRef" :args="[null, null, instanceCount]">
    <TresBoxGeometry :args="[0.2, 0.2, 0.2]" />
    <TresMeshBasicMaterial />
  </TresInstancedMesh>
</template>
```

### Occlusion-Based Rendering

```vue
<script setup lang="ts">
import { useRenderLoop } from '@tresjs/core'
import { Frustum, Matrix4, Camera, Object3D } from 'three'

const frustum = new Frustum()
const projectionMatrix = new Matrix4()

function checkVisibility(camera: Camera, objects: Object3D[]) {
  projectionMatrix.multiplyMatrices(
    camera.projectionMatrix,
    camera.matrixWorldInverse
  )
  frustum.setFromProjectionMatrix(projectionMatrix)

  objects.forEach(obj => {
    obj.visible = frustum.intersectsObject(obj)
  })
}

useRenderLoop().onLoop(({ camera }) => {
  // Check visibility for expensive objects only
  checkVisibility(camera, expensiveObjects.value)
})
</script>
```

## Best Practices Summary

### Do's
- ✅ Use instancing for repeated HUD elements
- ✅ Implement LOD for complex 3D models
- ✅ Use particle systems for data visualization
- ✅ Apply post-processing sparingly (performance cost)
- ✅ Animate cameras smoothly with easing
- ✅ Use raycasting for user interaction
- ✅ Implement frustum culling for large scenes

### Don'ts
- ❌ Don't render off-screen panels at full detail
- ❌ Don't update all instances every frame
- ❌ Don't use high-poly models for background elements
- ❌ Don't skip LOD for distant objects
- ❌ Don't create new objects during animations
- ❌ Don't use complex shaders on mobile devices
