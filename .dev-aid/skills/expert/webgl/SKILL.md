---
name: webgl
version: 2.0.0
description: "WebGL rendering with shaders, buffers, textures, and GPU performance optimization. Use when building WebGL shaders, rendering pipelines, or GPU effects. Do NOT use for Three.js abstraction layers (use threejs-tresjs)."
risk_level: MEDIUM
---

# WebGL - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-119: Shader Buffer Overflow**
- NEVER: Unbounded array access in shaders
- ALWAYS: Bounds checking, validate array indices

**CWE-400: GPU Resource Exhaustion**
- NEVER: Unlimited texture size or draw calls from user input
- ALWAYS: Limit texture dimensions, max vertices, monitor GPU memory

### 0.3 Risk Level: MEDIUM

**Verification requirements for MEDIUM risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 Shader Compilation Validation (CWE-20)

**Principle:** Shader code can crash the browser. Always check compilation status.

```typescript
// ❌ WRONG - No error checking
function createShader(gl: WebGLRenderingContext, source: string, type: number) {
  const shader = gl.createShader(type);
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  return shader;
}

// ✅ CORRECT - Comprehensive error handling
function createShaderSafe(
  gl: WebGLRenderingContext,
  source: string,
  type: number
): WebGLShader {
  const shader = gl.createShader(type);
  if (!shader) {
    throw new Error('Failed to create shader');
  }

  gl.shaderSource(shader, source);
  gl.compileShader(shader);

  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    const info = gl.getShaderInfoLog(shader);
    gl.deleteShader(shader);
    throw new Error(`Shader compilation failed: ${info}`);
  }

  return shader;
}

function createProgramSafe(
  gl: WebGLRenderingContext,
  vertexShader: WebGLShader,
  fragmentShader: WebGLShader
): WebGLProgram {
  const program = gl.createProgram();
  if (!program) {
    throw new Error('Failed to create program');
  }

  gl.attachShader(program, vertexShader);
  gl.attachShader(program, fragmentShader);
  gl.linkProgram(program);

  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
    const info = gl.getProgramInfoLog(program);
    gl.deleteProgram(program);
    throw new Error(`Program linking failed: ${info}`);
  }

  return program;
}
```

### 1.2 Context Loss Handling (CWE-754)

**Principle:** WebGL context can be lost at any time. Handle gracefully.

```typescript
// ❌ WRONG - No context loss handling
class Renderer {
  private gl: WebGLRenderingContext;

  init(canvas: HTMLCanvasElement) {
    this.gl = canvas.getContext('webgl')!;
    this.setupScene();
  }

  render() {
    // Crashes if context lost
    this.gl.clear(this.gl.COLOR_BUFFER_BIT);
  }
}

// ✅ CORRECT - Proper context loss handling
class SafeRenderer {
  private gl: WebGLRenderingContext | null = null;
  private canvas: HTMLCanvasElement;
  private isContextLost = false;
  private resources: WebGLResource[] = [];

  constructor(canvas: HTMLCanvasElement) {
    this.canvas = canvas;

    canvas.addEventListener('webglcontextlost', (e) => {
      e.preventDefault();
      this.isContextLost = true;
      console.warn('WebGL context lost');
    });

    canvas.addEventListener('webglcontextrestored', () => {
      this.isContextLost = false;
      this.initGL();
      console.info('WebGL context restored');
    });

    this.initGL();
  }

  private initGL(): void {
    this.gl = this.canvas.getContext('webgl', {
      alpha: false,
      antialias: true,
      depth: true,
      failIfMajorPerformanceCaveat: true,
      powerPreference: 'default',
      preserveDrawingBuffer: false,
    });

    if (!this.gl) {
      throw new Error('WebGL not supported');
    }

    this.recreateResources();
  }

  private recreateResources(): void {
    // Re-create all shaders, buffers, textures after context restore
    for (const resource of this.resources) {
      resource.recreate(this.gl!);
    }
  }

  render(): void {
    if (this.isContextLost || !this.gl) {
      return; // Silently skip if context lost
    }

    this.gl.clear(this.gl.COLOR_BUFFER_BIT | this.gl.DEPTH_BUFFER_BIT);
    // ... render scene
  }
}
```

### 1.3 Resource Limits (CWE-400)

**Principle:** WebGL has hardware-specific limits. Check before allocating.

```typescript
// ❌ WRONG - Assuming unlimited resources
function createLargeTexture(gl: WebGLRenderingContext) {
  const texture = gl.createTexture();
  gl.bindTexture(gl.TEXTURE_2D, texture);
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, 8192, 8192, 0, gl.RGBA, gl.UNSIGNED_BYTE, null);
}

// ✅ CORRECT - Check limits before allocation
interface WebGLLimits {
  maxTextureSize: number;
  maxCubeMapSize: number;
  maxRenderbufferSize: number;
  maxVertexAttribs: number;
  maxTextureUnits: number;
}

function getWebGLLimits(gl: WebGLRenderingContext): WebGLLimits {
  return {
    maxTextureSize: gl.getParameter(gl.MAX_TEXTURE_SIZE),
    maxCubeMapSize: gl.getParameter(gl.MAX_CUBE_MAP_TEXTURE_SIZE),
    maxRenderbufferSize: gl.getParameter(gl.MAX_RENDERBUFFER_SIZE),
    maxVertexAttribs: gl.getParameter(gl.MAX_VERTEX_ATTRIBS),
    maxTextureUnits: gl.getParameter(gl.MAX_TEXTURE_IMAGE_UNITS),
  };
}

function createTextureSafe(
  gl: WebGLRenderingContext,
  width: number,
  height: number,
  limits: WebGLLimits
): WebGLTexture {
  if (width > limits.maxTextureSize || height > limits.maxTextureSize) {
    throw new Error(
      `Texture size ${width}x${height} exceeds maximum ${limits.maxTextureSize}`
    );
  }

  const texture = gl.createTexture();
  if (!texture) {
    throw new Error('Failed to create texture');
  }

  gl.bindTexture(gl.TEXTURE_2D, texture);
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, width, height, 0, gl.RGBA, gl.UNSIGNED_BYTE, null);

  // Check for GL errors
  const error = gl.getError();
  if (error !== gl.NO_ERROR) {
    gl.deleteTexture(texture);
    throw new Error(`Texture creation failed with GL error: ${error}`);
  }

  return texture;
}
```

---

## 2. Version Requirements

```
# WebGL is native - no npm packages required for core
# For GLSL syntax and utilities:
glslify>=7.1.0
glsl-noise>=0.0.0
# For testing:
gl>=6.0.0  # Headless WebGL for Node.js
```

---

## 3. Code Patterns

### WHEN writing shaders, use precision qualifiers

```glsl
// ❌ WRONG - No precision specified
varying vec2 vUv;
uniform sampler2D uTexture;

void main() {
  gl_FragColor = texture2D(uTexture, vUv);
}

// ✅ CORRECT - Explicit precision for mobile compatibility
precision mediump float;

varying vec2 vUv;
uniform sampler2D uTexture;

void main() {
  vec4 color = texture2D(uTexture, vUv);

  // Clamp output to prevent artifacts
  gl_FragColor = clamp(color, 0.0, 1.0);
}
```

### WHEN managing WebGL state, use a state machine wrapper

```typescript
// ❌ WRONG - Global state pollution
function renderMesh(gl: WebGLRenderingContext, mesh: Mesh) {
  gl.enable(gl.DEPTH_TEST);
  gl.enable(gl.BLEND);
  // Render...
  // Forgot to restore state!
}

// ✅ CORRECT - State machine with restoration
class GLState {
  private gl: WebGLRenderingContext;
  private stateStack: Map<number, boolean>[] = [];

  constructor(gl: WebGLRenderingContext) {
    this.gl = gl;
  }

  push(): void {
    const state = new Map<number, boolean>();
    const capabilities = [
      this.gl.DEPTH_TEST,
      this.gl.BLEND,
      this.gl.CULL_FACE,
      this.gl.SCISSOR_TEST,
    ];

    for (const cap of capabilities) {
      state.set(cap, this.gl.isEnabled(cap));
    }

    this.stateStack.push(state);
  }

  pop(): void {
    const state = this.stateStack.pop();
    if (!state) return;

    for (const [cap, enabled] of state) {
      if (enabled) {
        this.gl.enable(cap);
      } else {
        this.gl.disable(cap);
      }
    }
  }

  withState(config: Partial<GLStateConfig>, fn: () => void): void {
    this.push();

    if (config.depthTest !== undefined) {
      config.depthTest ? this.gl.enable(this.gl.DEPTH_TEST) : this.gl.disable(this.gl.DEPTH_TEST);
    }
    if (config.blend !== undefined) {
      config.blend ? this.gl.enable(this.gl.BLEND) : this.gl.disable(this.gl.BLEND);
    }
    if (config.cullFace !== undefined) {
      config.cullFace ? this.gl.enable(this.gl.CULL_FACE) : this.gl.disable(this.gl.CULL_FACE);
    }

    try {
      fn();
    } finally {
      this.pop();
    }
  }
}
```

### WHEN loading textures, handle async and compression

```typescript
// ❌ WRONG - Synchronous, no compression support
function loadTexture(gl: WebGLRenderingContext, url: string) {
  const image = new Image();
  image.src = url;
  // Texture not ready!
  return createTextureFromImage(gl, image);
}

// ✅ CORRECT - Async loading with compression support
interface TextureOptions {
  minFilter?: number;
  magFilter?: number;
  wrapS?: number;
  wrapT?: number;
  generateMipmaps?: boolean;
}

async function loadTexture(
  gl: WebGLRenderingContext,
  url: string,
  options: TextureOptions = {}
): Promise<WebGLTexture> {
  const texture = gl.createTexture();
  if (!texture) {
    throw new Error('Failed to create texture');
  }

  // Bind placeholder while loading
  gl.bindTexture(gl.TEXTURE_2D, texture);
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, 1, 1, 0, gl.RGBA, gl.UNSIGNED_BYTE,
    new Uint8Array([255, 0, 255, 255]) // Magenta placeholder
  );

  const image = await loadImage(url);

  gl.bindTexture(gl.TEXTURE_2D, texture);
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, image);

  // Set filtering
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER,
    options.minFilter ?? gl.LINEAR_MIPMAP_LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER,
    options.magFilter ?? gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S,
    options.wrapS ?? gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T,
    options.wrapT ?? gl.CLAMP_TO_EDGE);

  if (options.generateMipmaps !== false && isPowerOf2(image.width) && isPowerOf2(image.height)) {
    gl.generateMipmap(gl.TEXTURE_2D);
  }

  return texture;
}

function loadImage(url: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.crossOrigin = 'anonymous';
    image.onload = () => resolve(image);
    image.onerror = () => reject(new Error(`Failed to load image: ${url}`));
    image.src = url;
  });
}

function isPowerOf2(value: number): boolean {
  return (value & (value - 1)) === 0;
}
```

### WHEN handling uniforms, cache locations

```typescript
// ❌ WRONG - Looking up locations every frame
function render(gl: WebGLRenderingContext, program: WebGLProgram) {
  const uTime = gl.getUniformLocation(program, 'uTime'); // Expensive!
  gl.uniform1f(uTime, performance.now());
}

// ✅ CORRECT - Cache uniform and attribute locations
class ShaderProgram {
  private gl: WebGLRenderingContext;
  private program: WebGLProgram;
  private uniforms = new Map<string, WebGLUniformLocation>();
  private attributes = new Map<string, number>();

  constructor(gl: WebGLRenderingContext, vertexSource: string, fragmentSource: string) {
    this.gl = gl;
    this.program = this.compile(vertexSource, fragmentSource);
    this.cacheLocations();
  }

  private compile(vertexSource: string, fragmentSource: string): WebGLProgram {
    const vertexShader = createShaderSafe(this.gl, vertexSource, this.gl.VERTEX_SHADER);
    const fragmentShader = createShaderSafe(this.gl, fragmentSource, this.gl.FRAGMENT_SHADER);
    return createProgramSafe(this.gl, vertexShader, fragmentShader);
  }

  private cacheLocations(): void {
    const gl = this.gl;

    // Cache all active uniforms
    const uniformCount = gl.getProgramParameter(this.program, gl.ACTIVE_UNIFORMS);
    for (let i = 0; i < uniformCount; i++) {
      const info = gl.getActiveUniform(this.program, i);
      if (info) {
        const location = gl.getUniformLocation(this.program, info.name);
        if (location) {
          this.uniforms.set(info.name, location);
        }
      }
    }

    // Cache all active attributes
    const attributeCount = gl.getProgramParameter(this.program, gl.ACTIVE_ATTRIBUTES);
    for (let i = 0; i < attributeCount; i++) {
      const info = gl.getActiveAttrib(this.program, i);
      if (info) {
        const location = gl.getAttribLocation(this.program, info.name);
        this.attributes.set(info.name, location);
      }
    }
  }

  setUniform1f(name: string, value: number): void {
    const location = this.uniforms.get(name);
    if (location) {
      this.gl.uniform1f(location, value);
    }
  }

  setUniformMatrix4fv(name: string, value: Float32Array): void {
    const location = this.uniforms.get(name);
    if (location) {
      this.gl.uniformMatrix4fv(location, false, value);
    }
  }

  getAttribute(name: string): number {
    return this.attributes.get(name) ?? -1;
  }

  use(): void {
    this.gl.useProgram(this.program);
  }

  dispose(): void {
    this.gl.deleteProgram(this.program);
    this.uniforms.clear();
    this.attributes.clear();
  }
}
```

---

## 4. Anti-Patterns

**NEVER:**
- Skip shader compilation error checking
- Ignore WebGL context loss events
- Create textures larger than MAX_TEXTURE_SIZE
- Look up uniform/attribute locations every frame
- Forget to unbind/restore GL state
- Use synchronous texture loading
- Skip precision qualifiers in fragment shaders

---

## 5. Testing

```typescript
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import createContext from 'gl';

describe('WebGL utilities', () => {
  let gl: WebGLRenderingContext;

  beforeEach(() => {
    gl = createContext(800, 600);
  });

  afterEach(() => {
    gl.getExtension('STACKGL_destroy_context')?.destroy();
  });

  describe('createShaderSafe', () => {
    it('should throw on invalid shader', () => {
      const invalidSource = 'this is not valid GLSL';
      expect(() => {
        createShaderSafe(gl, invalidSource, gl.FRAGMENT_SHADER);
      }).toThrow('Shader compilation failed');
    });

    it('should compile valid shader', () => {
      const source = `
        precision mediump float;
        void main() { gl_FragColor = vec4(1.0); }
      `;
      const shader = createShaderSafe(gl, source, gl.FRAGMENT_SHADER);
      expect(shader).toBeTruthy();
    });
  });

  describe('getWebGLLimits', () => {
    it('should return reasonable limits', () => {
      const limits = getWebGLLimits(gl);
      expect(limits.maxTextureSize).toBeGreaterThanOrEqual(1024);
      expect(limits.maxTextureUnits).toBeGreaterThanOrEqual(8);
    });
  });

  describe('createTextureSafe', () => {
    it('should reject oversized textures', () => {
      const limits = getWebGLLimits(gl);
      expect(() => {
        createTextureSafe(gl, limits.maxTextureSize + 1, 1, limits);
      }).toThrow('exceeds maximum');
    });
  });
});
```

---

## 6. Pre-Generation Checklist

**BEFORE generating WebGL code:**

- [ ] Shader compilation: Error checking on compile and link
- [ ] Context loss: Event listeners, resource recreation
- [ ] Resource limits: Check MAX_TEXTURE_SIZE before allocation
- [ ] Uniform caching: Locations cached at program creation
- [ ] State management: Push/pop or explicit restoration
- [ ] Texture loading: Async with placeholder, power-of-2 checks
- [ ] Precision: mediump/highp specified in fragment shaders
- [ ] GL errors: Check getError() after critical operations

---

**Performance**: Quality over speed. Verify all code examples compile. Never skip security checks. See `template-references/performance-notes.md` for full guidelines.