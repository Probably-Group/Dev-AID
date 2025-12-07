## 5. Implementation Patterns

### 4.1 Safe Shader Compilation

```typescript
// utils/shaderUtils.ts

// ✅ Safe shader compilation with error handling
export function compileShader(
  gl: WebGL2RenderingContext,
  source: string,
  type: number
): WebGLShader | null {
  const shader = gl.createShader(type)
  if (!shader) return null

  gl.shaderSource(shader, source)
  gl.compileShader(shader)

  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
    const error = gl.getShaderInfoLog(shader)
    console.error('Shader compilation error:', error)
    gl.deleteShader(shader)
    return null
  }

  return shader
}

// ✅ Safe program linking
export function createProgram(
  gl: WebGL2RenderingContext,
  vertexShader: WebGLShader,
  fragmentShader: WebGLShader
): WebGLProgram | null {
  const program = gl.createProgram()
  if (!program) return null

  gl.attachShader(program, vertexShader)
  gl.attachShader(program, fragmentShader)
  gl.linkProgram(program)

  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
    const error = gl.getProgramInfoLog(program)
    console.error('Program linking error:', error)
    gl.deleteProgram(program)
    return null
  }

  return program
}
```

### 4.2 Context Loss Handling

```typescript
// composables/useWebGL.ts
export function useWebGL(canvas: Ref<HTMLCanvasElement | null>) {
  const gl = ref<WebGL2RenderingContext | null>(null)
  const contextLost = ref(false)

  onMounted(() => {
    if (!canvas.value) return

    // ✅ Handle context loss
    canvas.value.addEventListener('webglcontextlost', (e) => {
      e.preventDefault()
      contextLost.value = true
      console.warn('WebGL context lost')
    })

    canvas.value.addEventListener('webglcontextrestored', () => {
      contextLost.value = false
      initializeGL()
      console.info('WebGL context restored')
    })

    initializeGL()
  })

  function initializeGL() {
    gl.value = getWebGLContext(canvas.value!)
    // Reinitialize all resources
  }

  return { gl, contextLost }
}
```

### 4.3 Holographic Shader

```glsl
// shaders/holographic.frag
#version 300 es
precision highp float;

uniform float uTime;
uniform vec3 uColor;
uniform float uScanlineIntensity;

in vec2 vUv;
out vec4 fragColor;

void main() {
  // Scanline effect
  float scanline = sin(vUv.y * 200.0 + uTime * 2.0) * 0.5 + 0.5;
  scanline = mix(1.0, scanline, uScanlineIntensity);

  // Edge glow
  float edge = smoothstep(0.0, 0.1, vUv.x) *
               smoothstep(1.0, 0.9, vUv.x) *
               smoothstep(0.0, 0.1, vUv.y) *
               smoothstep(1.0, 0.9, vUv.y);

  vec3 color = uColor * scanline * edge;
  float alpha = edge * 0.8;

  fragColor = vec4(color, alpha);
}
```

### 4.4 Resource Management

```typescript
// utils/resourceManager.ts
export class WebGLResourceManager {
  private textures: Set<WebGLTexture> = new Set()
  private buffers: Set<WebGLBuffer> = new Set()
  private programs: Set<WebGLProgram> = new Set()

  private textureMemory = 0
  private readonly MAX_TEXTURE_MEMORY = 256 * 1024 * 1024  // 256MB

  constructor(private gl: WebGL2RenderingContext) {}

  createTexture(width: number, height: number): WebGLTexture | null {
    const size = width * height * 4  // RGBA

    // ✅ Enforce memory limits
    if (this.textureMemory + size > this.MAX_TEXTURE_MEMORY) {
      console.error('Texture memory limit exceeded')
      return null
    }

    const texture = this.gl.createTexture()
    if (texture) {
      this.textures.add(texture)
      this.textureMemory += size
    }
    return texture
  }

  dispose(): void {
    this.textures.forEach(t => this.gl.deleteTexture(t))
    this.buffers.forEach(b => this.gl.deleteBuffer(b))
    this.programs.forEach(p => this.gl.deleteProgram(p))
    this.textureMemory = 0
  }
}
```

### 4.5 Uniform Validation

```typescript
// ✅ Type-safe uniform setting
export function setUniforms(
  gl: WebGL2RenderingContext,
  program: WebGLProgram,
  uniforms: Record<string, number | number[] | Float32Array>
): void {
  for (const [name, value] of Object.entries(uniforms)) {
    const location = gl.getUniformLocation(program, name)
    if (!location) {
      console.warn(`Uniform '${name}' not found`)
      continue
    }

    if (typeof value === 'number') {
      gl.uniform1f(location, value)
    } else if (Array.isArray(value)) {
      switch (value.length) {
        case 2: gl.uniform2fv(location, value); break
        case 3: gl.uniform3fv(location, value); break
        case 4: gl.uniform4fv(location, value); break
        case 16: gl.uniformMatrix4fv(location, false, value); break
      }
    }
  }
}
```

