# Three.js/TresJS Anti-Patterns

## Critical Security Anti-Patterns

### Never: Parse User Colors Directly

**Problem**: Direct color parsing from user input can cause ReDoS (Regular Expression Denial of Service) attacks.

**Bad Example**:
```typescript
// ❌ DANGEROUS - ReDoS vulnerability
function setColor(userInput: string) {
  const color = new Color(userInput)  // Potential ReDoS
  mesh.material.color = color
}
```

**Good Example**:
```typescript
// ✅ SECURE - Validated input
import { safeParseColor } from '~/utils/safeColor'

function setColor(userInput: string) {
  const color = safeParseColor(userInput)
  mesh.material.color = color
}
```

**Why This Matters**: Three.js versions before 0.125.0 had a ReDoS vulnerability in color parsing that could freeze the browser with carefully crafted input strings.

---

### Never: Skip Resource Disposal

**Problem**: Forgetting to dispose of Three.js resources leads to memory leaks and GPU memory exhaustion.

**Bad Example**:
```typescript
// ❌ MEMORY LEAK
function removeObject() {
  const mesh = new Mesh(geometry, material)
  scene.remove(mesh)
  // Geometry and material still in GPU memory!
}
```

**Good Example**:
```typescript
// ✅ PROPER CLEANUP
function removeObject() {
  scene.remove(mesh)
  mesh.geometry.dispose()

  if (Array.isArray(mesh.material)) {
    mesh.material.forEach(m => m.dispose())
  } else {
    mesh.material.dispose()
  }
}
```

**Why This Matters**: WebGL resources are not garbage collected automatically. They must be explicitly disposed to free GPU memory.

---

## Performance Anti-Patterns

### Avoid: Creating Objects in Render Loop

**Problem**: Creating new objects every frame causes excessive garbage collection and frame drops.

**Bad Example**:
```typescript
// ❌ BAD - Creates garbage every frame
function animate() {
  requestAnimationFrame(animate)

  mesh.position.add(new Vector3(0, 0.01, 0))  // New object every frame!
  mesh.rotation.setFromAxisAngle(new Vector3(0, 1, 0), 0.01)  // Another new object!

  renderer.render(scene, camera)
}
```

**Good Example**:
```typescript
// ✅ GOOD - Reuse objects
const velocity = new Vector3(0, 0.01, 0)
const axis = new Vector3(0, 1, 0)

function animate() {
  requestAnimationFrame(animate)

  mesh.position.add(velocity)
  mesh.rotation.y += 0.01

  renderer.render(scene, camera)
}
```

**Why This Matters**: Creating objects in the render loop triggers frequent garbage collection, causing frame stuttering.

---

### Avoid: Cloning Geometries and Materials

**Problem**: Each clone consumes additional GPU memory unnecessarily.

**Bad Example**:
```typescript
// ❌ BAD - Clones use separate GPU memory
for (let i = 0; i < 100; i++) {
  const mesh = new Mesh(
    geometry.clone(),    // Separate GPU buffer!
    material.clone()     // Separate shader program!
  )
  scene.add(mesh)
}
```

**Good Example**:
```typescript
// ✅ GOOD - Share resources or use instancing
const sharedGeometry = new BoxGeometry(1, 1, 1)
const sharedMaterial = new MeshStandardMaterial()

// For identical objects: Use InstancedMesh
const instancedMesh = new InstancedMesh(sharedGeometry, sharedMaterial, 100)

// For objects with different materials: Share geometry
for (let i = 0; i < 100; i++) {
  const mesh = new Mesh(sharedGeometry, sharedMaterial)
  scene.add(mesh)
}
```

**Why This Matters**: Instancing can render 100+ objects with the performance of rendering just one.

---

### Avoid: Updating Uniforms Unnecessarily

**Problem**: Updating shader uniforms that haven't changed wastes CPU cycles.

**Bad Example**:
```typescript
// ❌ BAD - Updates every frame even if unchanged
function animate() {
  material.uniforms.color.value.set(0, 1, 0.25)  // Same value every frame!
  material.uniforms.time.value = clock.getElapsedTime()

  renderer.render(scene, camera)
}
```

**Good Example**:
```typescript
// ✅ GOOD - Only update what changes
function animate() {
  // Only update time uniform (changes every frame)
  material.uniforms.time.value = clock.getElapsedTime()

  renderer.render(scene, camera)
}

// Update color only when needed
function setColor(r: number, g: number, b: number) {
  material.uniforms.color.value.set(r, g, b)
}
```

**Why This Matters**: Unnecessary uniform updates consume CPU time and can cause shader recompilation.

---

## Vue/TresJS Integration Anti-Patterns

### Avoid: Using Reactive Refs for Three.js Objects

**Problem**: Vue's reactivity system adds overhead that Three.js objects don't need.

**Bad Example**:
```typescript
// ❌ BAD - Vue tracks internal Three.js properties
const mesh = ref(new Mesh(geometry, material))
```

**Good Example**:
```typescript
// ✅ GOOD - Use shallowRef to avoid deep reactivity
const mesh = shallowRef(new Mesh(geometry, material))
```

**Why This Matters**: Vue's reactivity tracking Three.js internal properties causes unnecessary overhead and can lead to bugs.

---

### Avoid: Forgetting onUnmounted Cleanup

**Problem**: Components that create Three.js objects must clean them up.

**Bad Example**:
```vue
<script setup lang="ts">
// ❌ BAD - No cleanup on component unmount
const mesh = new Mesh(
  new BoxGeometry(1, 1, 1),
  new MeshStandardMaterial()
)
</script>
```

**Good Example**:
```vue
<script setup lang="ts">
import { onUnmounted, shallowRef } from 'vue'

const meshRef = shallowRef<Mesh | null>(null)

// ✅ GOOD - Cleanup on unmount
onUnmounted(() => {
  if (meshRef.value) {
    meshRef.value.geometry.dispose()
    meshRef.value.material.dispose()
  }
})
</script>
```

**Why This Matters**: Vue components can be mounted/unmounted frequently. Without cleanup, memory leaks accumulate quickly.

---

## Architecture Anti-Patterns

### Avoid: Monolithic Scene Setup

**Problem**: Putting all 3D logic in one component makes it hard to test and maintain.

**Bad Example**:
```vue
<!-- ❌ BAD - Everything in one component -->
<template>
  <TresCanvas>
    <!-- 500 lines of HUD components -->
    <!-- Mixed concerns: lighting, camera, objects, effects -->
  </TresCanvas>
</template>
```

**Good Example**:
```vue
<!-- ✅ GOOD - Separated concerns -->
<template>
  <TresCanvas>
    <SceneLighting />
    <HUDPanels />
    <MetricsDisplay />
    <ParticleEffects />
    <PostProcessing />
  </TresCanvas>
</template>
```

**Why This Matters**: Separation allows testing, reusing, and maintaining components independently.

---

### Avoid: Direct DOM Manipulation

**Problem**: Bypassing TresJS's component model breaks reactivity.

**Bad Example**:
```typescript
// ❌ BAD - Direct Three.js API usage in Vue component
function addPanel() {
  const mesh = new Mesh(geometry, material)
  scene.add(mesh)  // Bypasses Vue reactivity!
}
```

**Good Example**:
```vue
<!-- ✅ GOOD - Use TresJS components -->
<script setup lang="ts">
const panels = ref([{ id: 1 }, { id: 2 }])

function addPanel() {
  panels.value.push({ id: panels.value.length + 1 })
}
</script>

<template>
  <TresGroup>
    <HUDPanel
      v-for="panel in panels"
      :key="panel.id"
    />
  </TresGroup>
</template>
```

**Why This Matters**: Using TresJS components keeps Vue reactivity working and makes the code more maintainable.

---

## Common Mistakes Summary

| Anti-Pattern | Impact | Solution |
|--------------|--------|----------|
| Parse user colors directly | ReDoS vulnerability | Use `safeParseColor()` |
| Skip resource disposal | Memory leaks | Always dispose in `onUnmounted()` |
| Create objects in render loop | GC pressure, frame drops | Pre-allocate and reuse |
| Clone unnecessarily | GPU memory waste | Share resources or use instancing |
| Use reactive refs | Performance overhead | Use `shallowRef()` |
| Monolithic components | Hard to test/maintain | Separate concerns |
| Update all uniforms | Wasted CPU cycles | Only update what changes |
| Direct Three.js API usage | Breaks Vue reactivity | Use TresJS components |

---

## Testing for Anti-Patterns

### Checklist for Code Review

- [ ] All user inputs validated before color parsing?
- [ ] Every `new Geometry()` has corresponding `.dispose()`?
- [ ] Every `new Material()` has corresponding `.dispose()`?
- [ ] No object allocations in render loop?
- [ ] Using `shallowRef()` for Three.js objects?
- [ ] `onUnmounted()` cleanup implemented?
- [ ] Instancing used for repeated objects (>10)?
- [ ] Components separated by concern?

### Automated Checks

```typescript
// Example: ESLint rule to detect missing disposal
// Place in .eslintrc.js custom rules
{
  'no-undisposed-geometry': {
    create(context) {
      return {
        NewExpression(node) {
          if (node.callee.name?.endsWith('Geometry')) {
            // Check if dispose() is called somewhere
          }
        }
      }
    }
  }
}
```
