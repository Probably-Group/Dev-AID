---
name: threejs-tresjs
version: 2.0.0
description: "3D rendering with Three.js and TresJS for Vue with scene management, WebGL optimization, and asset loading. Use when building 3D scenes, integrating Three.js with Vue, or optimizing WebGL performance. Do NOT use for 2D canvas rendering or non-WebGL graphics."
compatibility: "Three.js r160+, TresJS 4+, Vue 3.3+"
risk_level: MEDIUM
token_budget: 3000
---
# Three.js / TresJS - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.2 Security Patterns (security rules)

**CWE-79: XSS via 3D Content**
- Do not: Load GLTF/textures from user URLs without validation
- Instead: Allowlist origins, validate content types

**CWE-400: Scene Complexity DoS**
- Do not: Load unbounded user models directly
- Instead: Limit polygon count, texture size, object count

---

## 1. Security Principles

### 1.1 Model Loading Validation (CWE-20, CWE-400)

**Principle:** External 3D models can be malicious. Validate and sanitize before loading.

```typescript
// ❌ WRONG - Loading arbitrary models without validation
async function loadModel(url: string) {
  const loader = new GLTFLoader();
  return await loader.loadAsync(url);
}

// ✅ CORRECT - Validate model source and size
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';

interface ModelConfig {
  allowedOrigins: string[];
  maxFileSizeMB: number;
  maxTriangles: number;
}

const DEFAULT_CONFIG: ModelConfig = {
  allowedOrigins: ['https://cdn.example.com'],
  maxFileSizeMB: 50,
  maxTriangles: 1_000_000,
};

async function loadModelSafe(
  url: string,
  config: ModelConfig = DEFAULT_CONFIG
): Promise<THREE.Group> {
  // Validate origin
  const urlObj = new URL(url);
  if (!config.allowedOrigins.some(origin => url.startsWith(origin))) {
    throw new Error(`Untrusted model origin: ${urlObj.origin}`);
  }

  // Check file size with HEAD request
  const headRes = await fetch(url, { method: 'HEAD' });
  const contentLength = parseInt(headRes.headers.get('content-length') || '0');
  if (contentLength > config.maxFileSizeMB * 1024 * 1024) {
    throw new Error(`Model too large: ${contentLength} bytes`);
  }

  const loader = new GLTFLoader();
  const gltf = await loader.loadAsync(url);

  // Validate triangle count
  let triangleCount = 0;
  gltf.scene.traverse((child) => {
    if (child instanceof THREE.Mesh) {
      const geometry = child.geometry as THREE.BufferGeometry;
      triangleCount += geometry.index
        ? geometry.index.count / 3
        : geometry.attributes.position.count / 3;
    }
  });

  if (triangleCount > config.maxTriangles) {
    throw new Error(`Model too complex: ${triangleCount} triangles`);
  }

  return gltf.scene;
}
```

### 1.2 Resource Management (CWE-400, CWE-401)

**Principle:** WebGL resources must be explicitly disposed. Memory leaks crash browsers.

```typescript
// ❌ WRONG - No cleanup
function createScene() {
  const geometry = new THREE.BoxGeometry();
  const material = new THREE.MeshBasicMaterial();
  return new THREE.Mesh(geometry, material);
}

// ✅ CORRECT - Proper disposal pattern
class SceneManager {
  private disposables: Set<THREE.Object3D | THREE.Material | THREE.Texture> = new Set();
  private scene: THREE.Scene;

  constructor() {
    this.scene = new THREE.Scene();
  }

  createMesh(
    geometry: THREE.BufferGeometry,
    material: THREE.Material
  ): THREE.Mesh {
    const mesh = new THREE.Mesh(geometry, material);
    this.disposables.add(mesh);
    this.disposables.add(material);
    this.scene.add(mesh);
    return mesh;
  }

  dispose(): void {
    this.disposables.forEach((obj) => {
      if (obj instanceof THREE.Mesh) {
        obj.geometry.dispose();
        if (Array.isArray(obj.material)) {
          obj.material.forEach(m => m.dispose());
        } else {
          obj.material.dispose();
        }
      } else if ('dispose' in obj) {
        (obj as THREE.Material | THREE.Texture).dispose();
      }
    });
    this.disposables.clear();
    this.scene.clear();
  }
}
```

### 1.3 XSS Prevention in 3D Labels (CWE-79)

**Principle:** Text rendered in 3D (CSS2DRenderer, TextGeometry) must be sanitized.

```typescript
// ❌ WRONG - Rendering user text directly
function createLabel(text: string): CSS2DObject {
  const div = document.createElement('div');
  div.innerHTML = text; // XSS!
  return new CSS2DObject(div);
}

// ✅ CORRECT - Sanitize text content
function createLabelSafe(text: string): CSS2DObject {
  const div = document.createElement('div');
  div.textContent = text; // Safe - escapes HTML
  div.className = 'scene-label';
  return new CSS2DObject(div);
}
```

---

## 2. Version Requirements

```
three>=0.160.0
@tresjs/core>=4.0.0
@tresjs/cientos>=3.8.0
@types/three>=0.160.0
```

---

## 3. Code Patterns

### WHEN using TresJS with Vue 3, use proper component structure

```vue
<!-- ❌ WRONG - Missing reactive cleanup -->
<script setup>
const geometry = new BoxGeometry();
const material = new MeshBasicMaterial({ color: 'red' });
</script>

<template>
  <TresCanvas>
    <TresMesh :geometry="geometry" :material="material" />
  </TresCanvas>
</template>

<!-- ✅ CORRECT - Reactive with cleanup -->
<script setup lang="ts">
import { TresCanvas, useRenderLoop } from '@tresjs/core';
import { OrbitControls, Box } from '@tresjs/cientos';
import { shallowRef, onUnmounted } from 'vue';
import * as THREE from 'three';

// Use shallowRef for Three.js objects (not reactive internally)
const boxRef = shallowRef<THREE.Mesh | null>(null);

const { onLoop } = useRenderLoop();

onLoop(({ delta }) => {
  if (boxRef.value) {
    boxRef.value.rotation.y += delta;
  }
});

// Cleanup on unmount
onUnmounted(() => {
  if (boxRef.value) {
    boxRef.value.geometry.dispose();
    (boxRef.value.material as THREE.Material).dispose();
  }
});
</script>

<template>
  <TresCanvas clear-color="#1a1a1a">
    <TresPerspectiveCamera :position="[3, 3, 3]" />
    <OrbitControls />

    <Box ref="boxRef" :args="[1, 1, 1]">
      <TresMeshStandardMaterial color="orange" />
    </Box>

    <TresAmbientLight :intensity="0.5" />
    <TresDirectionalLight :position="[5, 5, 5]" :intensity="1" />
  </TresCanvas>
</template>
```

### WHEN loading textures, use proper async handling

```typescript
// ❌ WRONG - Synchronous texture loading blocks render
const texture = new THREE.TextureLoader().load('/texture.jpg');
material.map = texture;

// ✅ CORRECT - Async texture loading with loading manager
import { useTexture, useProgress } from '@tresjs/core';

// In Vue component
const { progress, isLoading } = useProgress();

// Load texture asynchronously
const texture = await useTexture('/texture.jpg');

// Or with loading manager for multiple assets
const loadingManager = new THREE.LoadingManager();
loadingManager.onProgress = (url, loaded, total) => {
  console.log(`Loading: ${(loaded / total * 100).toFixed(0)}%`);
};
loadingManager.onError = (url) => {
  console.error(`Failed to load: ${url}`);
};

const textureLoader = new THREE.TextureLoader(loadingManager);

async function loadTextures(urls: string[]): Promise<THREE.Texture[]> {
  return Promise.all(
    urls.map(url => new Promise<THREE.Texture>((resolve, reject) => {
      textureLoader.load(url, resolve, undefined, reject);
    }))
  );
}
```

### WHEN implementing animation loops, use proper timing

```typescript
// ❌ WRONG - Using Date.now() for animations (inconsistent)
let lastTime = Date.now();
function animate() {
  const now = Date.now();
  const delta = now - lastTime;
  object.rotation.y += 0.01 * delta;
  lastTime = now;
  requestAnimationFrame(animate);
}

// ✅ CORRECT - Using Three.js Clock with frame limiting
import { Clock } from 'three';
import { useRenderLoop } from '@tresjs/core';

// TresJS approach (preferred)
const { onLoop, pause, resume } = useRenderLoop();

onLoop(({ delta, elapsed, clock }) => {
  // delta is already calculated correctly
  mesh.rotation.y += delta;

  // Pause when tab not visible
  if (document.hidden) {
    pause();
  }
});

document.addEventListener('visibilitychange', () => {
  if (!document.hidden) {
    resume();
  }
});

// Pure Three.js approach
class AnimationController {
  private clock = new Clock();
  private rafId: number | null = null;
  private targetFPS = 60;
  private frameInterval = 1000 / 60;
  private lastFrameTime = 0;

  start(callback: (delta: number) => void): void {
    const animate = (currentTime: number) => {
      this.rafId = requestAnimationFrame(animate);

      const elapsed = currentTime - this.lastFrameTime;
      if (elapsed < this.frameInterval) return;

      this.lastFrameTime = currentTime - (elapsed % this.frameInterval);
      const delta = this.clock.getDelta();

      callback(Math.min(delta, 0.1)); // Cap delta to prevent jumps
    };

    this.rafId = requestAnimationFrame(animate);
  }

  stop(): void {
    if (this.rafId !== null) {
      cancelAnimationFrame(this.rafId);
      this.rafId = null;
    }
  }
}
```

### WHEN implementing post-processing, manage render targets

```typescript
// ❌ WRONG - Creating render targets without size management
const renderTarget = new THREE.WebGLRenderTarget(1920, 1080);

// ✅ CORRECT - Responsive render targets with proper disposal
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass';

class PostProcessingManager {
  private composer: EffectComposer;
  private renderer: THREE.WebGLRenderer;
  private resizeObserver: ResizeObserver;

  constructor(
    renderer: THREE.WebGLRenderer,
    scene: THREE.Scene,
    camera: THREE.Camera
  ) {
    this.renderer = renderer;

    // Create composer with proper pixel ratio
    const pixelRatio = Math.min(window.devicePixelRatio, 2);
    const size = renderer.getSize(new THREE.Vector2());

    this.composer = new EffectComposer(renderer);
    this.composer.setPixelRatio(pixelRatio);
    this.composer.setSize(size.x, size.y);

    // Add passes
    this.composer.addPass(new RenderPass(scene, camera));
    this.composer.addPass(new UnrealBloomPass(
      new THREE.Vector2(size.x, size.y),
      1.5, // strength
      0.4, // radius
      0.85 // threshold
    ));

    // Handle resize
    this.resizeObserver = new ResizeObserver(entries => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect;
        this.composer.setSize(width, height);
      }
    });
    this.resizeObserver.observe(renderer.domElement.parentElement!);
  }

  render(): void {
    this.composer.render();
  }

  dispose(): void {
    this.resizeObserver.disconnect();
    this.composer.dispose();
  }
}
```

---

## 4. Anti-Patterns

Do not:
- Load 3D models from untrusted sources without validation
- Create geometries/materials without disposal plan
- Use innerHTML for 3D text labels (XSS risk)
- Skip pixel ratio capping (performance issues on high-DPI)
- Create render targets without resize handling
- Use Date.now() for animations (use Clock)
- Block main thread with synchronous loading

---

## 5. Testing

```typescript
import { describe, it, expect, afterEach, vi } from 'vitest';
import * as THREE from 'three';

describe('SceneManager', () => {
  let manager: SceneManager;

  afterEach(() => {
# ... (additional test cases follow same pattern)
```

---

## 6. Pre-Generation Checklist

Before generating Three.js/TresJS code:

- [ ] Model loading: Origin validation, size limits, triangle count
- [ ] Resource disposal: All geometries, materials, textures tracked
- [ ] Text rendering: Using textContent, not innerHTML
- [ ] Pixel ratio: Capped at 2 for performance
- [ ] Render targets: Resize handling implemented
- [ ] Animation timing: Using Clock, delta capped
- [ ] Texture loading: Async with loading manager
- [ ] Vue integration: shallowRef for Three.js objects

---
