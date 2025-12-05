# Three.js/TresJS Performance Optimization

## Geometry Instancing

```typescript
// Good: Use InstancedMesh for repeated objects
import { InstancedMesh, Matrix4, Object3D } from 'three'

const COUNT = 1000
const mesh = new InstancedMesh(geometry, material, COUNT)
const dummy = new Object3D()

for (let i = 0; i < COUNT; i++) {
  dummy.position.set(Math.random() * 10, Math.random() * 10, Math.random() * 10)
  dummy.updateMatrix()
  mesh.setMatrixAt(i, dummy.matrix)
}
mesh.instanceMatrix.needsUpdate = true

// Bad: Creating individual meshes
for (let i = 0; i < COUNT; i++) {
  const mesh = new Mesh(geometry.clone(), material.clone()) // Memory waste!
  scene.add(mesh)
}
```

## Texture Atlases

```typescript
// Good: Single texture atlas for multiple sprites
const atlas = new TextureLoader().load('/textures/hud-atlas.png')
const materials = {
  panel: new SpriteMaterial({ map: atlas }),
  icon: new SpriteMaterial({ map: atlas })
}

// Set UV offsets for different sprites
materials.panel.map.offset.set(0, 0.5)
materials.panel.map.repeat.set(0.5, 0.5)

// Bad: Loading separate textures
const panelTex = new TextureLoader().load('/textures/panel.png')
const iconTex = new TextureLoader().load('/textures/icon.png')
// Multiple draw calls, more GPU memory
```

## Level of Detail (LOD)

```typescript
// Good: Use LOD for complex objects
import { LOD } from 'three'

const lod = new LOD()

// High detail - close up
const highDetail = new Mesh(
  new SphereGeometry(1, 32, 32),
  material
)
lod.addLevel(highDetail, 0)

// Medium detail - mid range
const medDetail = new Mesh(
  new SphereGeometry(1, 16, 16),
  material
)
lod.addLevel(medDetail, 10)

// Low detail - far away
const lowDetail = new Mesh(
  new SphereGeometry(1, 8, 8),
  material
)
lod.addLevel(lowDetail, 20)

scene.add(lod)

// Bad: Always rendering high detail
const sphere = new Mesh(new SphereGeometry(1, 64, 64), material)
```

## Frustum Culling

```typescript
// Good: Enable frustum culling (default, but verify)
mesh.frustumCulled = true

// For custom bounds optimization
mesh.geometry.computeBoundingSphere()
mesh.geometry.computeBoundingBox()

// Manual visibility check for complex scenes
const frustum = new Frustum()
const matrix = new Matrix4().multiplyMatrices(
  camera.projectionMatrix,
  camera.matrixWorldInverse
)
frustum.setFromProjectionMatrix(matrix)

objects.forEach(obj => {
  obj.visible = frustum.intersectsObject(obj)
})

// Bad: Disabling culling or rendering everything
mesh.frustumCulled = false // Renders even when off-screen
```

## Object Pooling

```typescript
// Good: Pool and reuse objects
class ParticlePool {
  private pool: Mesh[] = []
  private active: Set<Mesh> = new Set()

  constructor(private geometry: BufferGeometry, private material: Material) {
    // Pre-allocate pool
    for (let i = 0; i < 100; i++) {
      const mesh = new Mesh(geometry, material)
      mesh.visible = false
      this.pool.push(mesh)
    }
  }

  acquire(): Mesh | null {
    const mesh = this.pool.find(m => !this.active.has(m))
    if (mesh) {
      mesh.visible = true
      this.active.add(mesh)
      return mesh
    }
    return null
  }

  release(mesh: Mesh): void {
    mesh.visible = false
    this.active.delete(mesh)
  }
}

// Bad: Creating/destroying objects each frame
function spawnParticle() {
  const mesh = new Mesh(geometry, material) // GC pressure!
  scene.add(mesh)
  setTimeout(() => {
    scene.remove(mesh)
    mesh.geometry.dispose()
  }, 1000)
}
```

## RequestAnimationFrame Optimization

```typescript
// Good: Efficient render loop
let lastTime = 0
const targetFPS = 60
const frameInterval = 1000 / targetFPS

function animate(currentTime: number) {
  requestAnimationFrame(animate)

  const delta = currentTime - lastTime

  // Skip frame if too soon (for battery saving)
  if (delta < frameInterval) return

  lastTime = currentTime - (delta % frameInterval)

  // Update only what changed
  if (needsUpdate) {
    updateScene()
    renderer.render(scene, camera)
  }
}

// Bad: Rendering every frame unconditionally
function animate() {
  requestAnimationFrame(animate)

  // Always updates everything
  updateAllObjects()
  renderer.render(scene, camera) // Even if nothing changed
}
```

## Shader Optimization

```typescript
// Good: Simple, optimized shaders
const material = new ShaderMaterial({
  vertexShader: `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    varying vec2 vUv;
    uniform vec3 color;
    void main() {
      gl_FragColor = vec4(color, 1.0);
    }
  `,
  uniforms: {
    color: { value: new Color(0x00ff41) }
  }
})

// Bad: Complex calculations in fragment shader
// Avoid: loops, conditionals, texture lookups when possible
```

## Memory Management Best Practices

### 1. Dispose Resources Properly

```typescript
function cleanupMesh(mesh: Mesh) {
  // Dispose geometry
  mesh.geometry.dispose()

  // Dispose materials
  if (Array.isArray(mesh.material)) {
    mesh.material.forEach(m => m.dispose())
  } else {
    mesh.material.dispose()
  }

  // Dispose textures
  const disposeMaterial = (mat: Material) => {
    Object.values(mat).forEach(value => {
      if (value instanceof Texture) {
        value.dispose()
      }
    })
  }

  if (Array.isArray(mesh.material)) {
    mesh.material.forEach(disposeMaterial)
  } else {
    disposeMaterial(mesh.material)
  }
}
```

### 2. Use Shared Resources

```typescript
// Good: Share geometry and materials
const sharedGeometry = new BoxGeometry(1, 1, 1)
const sharedMaterial = new MeshStandardMaterial({ color: 0x00ff41 })

for (let i = 0; i < 100; i++) {
  const mesh = new Mesh(sharedGeometry, sharedMaterial)
  scene.add(mesh)
}

// Bad: Clone for each instance
for (let i = 0; i < 100; i++) {
  const mesh = new Mesh(
    new BoxGeometry(1, 1, 1),  // New geometry each time!
    new MeshStandardMaterial({ color: 0x00ff41 })  // New material each time!
  )
  scene.add(mesh)
}
```

### 3. Minimize Allocations in Render Loop

```typescript
// Good: Reuse objects
const tempVector = new Vector3()
const tempQuaternion = new Quaternion()

function animate() {
  // Reuse temp objects
  tempVector.set(x, y, z)
  mesh.position.copy(tempVector)
}

// Bad: Create new objects each frame
function animate() {
  mesh.position.add(new Vector3(0, 0.01, 0))  // GC pressure!
}
```

## GPU Resource Limits

```typescript
// Monitor and limit GPU resources
export function useResourceLimit() {
  const MAX_TRIANGLES = 1_000_000
  const MAX_DRAW_CALLS = 100

  let triangleCount = 0

  function checkGeometry(geometry: BufferGeometry): boolean {
    const triangles = geometry.index
      ? geometry.index.count / 3
      : geometry.attributes.position.count / 3

    if (triangleCount + triangles > MAX_TRIANGLES) {
      console.error('Triangle limit exceeded')
      return false
    }

    triangleCount += triangles
    return true
  }

  return { checkGeometry }
}
```
