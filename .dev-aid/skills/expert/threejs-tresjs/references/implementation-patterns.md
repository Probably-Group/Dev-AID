# Three.js/TresJS Implementation Patterns

## 4.1 Basic HUD Scene Setup

```vue
<script setup lang="ts">
import { TresCanvas } from '@tresjs/core'
import { OrbitControls } from '@tresjs/cientos'

const gl = {
  clearColor: '#000011',
  alpha: true,
  antialias: true,
  powerPreference: 'high-performance'
}
</script>

<template>
  <TresCanvas v-bind="gl">
    <TresPerspectiveCamera :position="[0, 0, 5]" />
    <OrbitControls :enable-damping="true" />

    <HUDPanels />
    <MetricsDisplay />
    <ParticleEffects />
  </TresCanvas>
</template>
```

## 4.2 Secure Color Handling

```typescript
// utils/safeColor.ts
import { Color } from 'three'

// ✅ Safe color parsing with validation
export function safeParseColor(input: string): Color {
  // Validate format to prevent ReDoS
  const hexPattern = /^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$/
  const rgbPattern = /^rgb\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*\)$/

  if (!hexPattern.test(input) && !rgbPattern.test(input)) {
    console.warn('Invalid color format, using default')
    return new Color(0x00ff00)  // Default JARVIS green
  }

  return new Color(input)
}

// ❌ DANGEROUS - User input directly to Color
// const color = new Color(userInput)  // Potential ReDoS

// ✅ SECURE - Validated input
const color = safeParseColor(userInput)
```

## 4.3 Memory-Safe Component

```vue
<script setup lang="ts">
import { onUnmounted, shallowRef } from 'vue'
import { Mesh, BoxGeometry, MeshStandardMaterial } from 'three'

// ✅ Use shallowRef for Three.js objects
const meshRef = shallowRef<Mesh | null>(null)

// ✅ Cleanup on unmount
onUnmounted(() => {
  if (meshRef.value) {
    meshRef.value.geometry.dispose()
    if (Array.isArray(meshRef.value.material)) {
      meshRef.value.material.forEach(m => m.dispose())
    } else {
      meshRef.value.material.dispose()
    }
  }
})
</script>

<template>
  <TresMesh ref="meshRef">
    <TresBoxGeometry :args="[1, 1, 1]" />
    <TresMeshStandardMaterial color="#00ff41" />
  </TresMesh>
</template>
```

## 4.4 Performance-Optimized Instancing

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { InstancedMesh, Object3D, Matrix4 } from 'three'

const instanceCount = 1000
const instancedMeshRef = ref<InstancedMesh | null>(null)

onMounted(() => {
  if (!instancedMeshRef.value) return

  const dummy = new Object3D()
  const matrix = new Matrix4()

  // ✅ Batch updates for performance
  for (let i = 0; i < instanceCount; i++) {
    dummy.position.set(
      Math.random() * 10 - 5,
      Math.random() * 10 - 5,
      Math.random() * 10 - 5
    )
    dummy.updateMatrix()
    instancedMeshRef.value.setMatrixAt(i, dummy.matrix)
  }

  instancedMeshRef.value.instanceMatrix.needsUpdate = true
})
</script>

<template>
  <TresInstancedMesh ref="instancedMeshRef" :args="[null, null, instanceCount]">
    <TresSphereGeometry :args="[0.05, 8, 8]" />
    <TresMeshBasicMaterial color="#00ff41" />
  </TresInstancedMesh>
</template>
```

## 4.5 HUD Panel with Text

```vue
<script setup lang="ts">
import { Text } from '@tresjs/cientos'

const props = defineProps<{
  title: string
  value: number
}>()

// ✅ Sanitize text content
const safeTitle = computed(() =>
  props.title.replace(/[<>]/g, '').slice(0, 50)
)
</script>

<template>
  <TresGroup>
    <!-- Panel background -->
    <TresMesh>
      <TresPlaneGeometry :args="[2, 1]" />
      <TresMeshBasicMaterial
        color="#001122"
        :transparent="true"
        :opacity="0.8"
      />
    </TresMesh>

    <!-- Title text -->
    <Text
      :text="safeTitle"
      :font-size="0.15"
      color="#00ff41"
      :position="[-0.8, 0.3, 0.01]"
    />

    <!-- Value display -->
    <Text
      :text="String(props.value)"
      :font-size="0.3"
      color="#ffffff"
      :position="[0, -0.1, 0.01]"
    />
  </TresGroup>
</template>
```
