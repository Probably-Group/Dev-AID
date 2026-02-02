---
name: glsl
version: 2.0.0
description: "GLSL shader programming for fragment and vertex shaders with WebGL integration and optimization."
risk_level: LOW
---

# GLSL Shader Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-119: Buffer Access**
- NEVER: `array[userIndex]` without bounds check
- ALWAYS: Clamp indices, use defined array bounds

**CWE-835: Infinite Loops**
- NEVER: `while(true)` or unbounded loops in shaders
- ALWAYS: Maximum iteration counts, early exit conditions

### 0.3 Risk Level: LOW

**Verification requirements for LOW risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 Shader Injection Prevention (CWE-94)

**Principle:** Never construct shaders from user input. Use precompiled shaders.

```javascript
// ❌ WRONG - Shader injection vulnerability
function createShader(userCode) {
  return `
    void main() {
      ${userCode}  // User can inject arbitrary shader code!
    }
  `;
}

// ✅ CORRECT - Parameterized shader with validated uniforms
const fragmentShader = `
  precision highp float;
  uniform vec3 u_color;
  uniform float u_intensity;

  void main() {
    gl_FragColor = vec4(u_color * u_intensity, 1.0);
  }
`;

// Validate uniform values
function setColor(gl, program, r, g, b) {
  if (![r, g, b].every(v => v >= 0 && v <= 1)) {
    throw new Error('Color values must be between 0 and 1');
  }
  const loc = gl.getUniformLocation(program, 'u_color');
  gl.uniform3f(loc, r, g, b);
}
```

### 1.2 Resource Exhaustion Prevention (CWE-400)

**Principle:** Limit shader complexity. Avoid unbounded loops.

```glsl
// ❌ WRONG - Unbounded loop can freeze GPU
for (int i = 0; i < iterations; i++) {
  // Could run millions of times
}

// ✅ CORRECT - Bounded loop with compile-time constant
#define MAX_ITERATIONS 100
for (int i = 0; i < MAX_ITERATIONS; i++) {
  if (i >= actualIterations) break;
}
```

### 1.3 Precision Specification (CWE-681)

**Principle:** Always specify precision to prevent cross-platform issues.

### 1.4 Division Safety (CWE-369)

**Principle:** Guard against division by zero.

### 1.5 Memory Bounds (CWE-125)

**Principle:** Validate array indices. Avoid out-of-bounds access.

### 1.6 Cross-Platform Compatibility

**Principle:** Test on multiple GPUs. Avoid vendor-specific extensions.

---

## 2. Version Requirements

**ALWAYS use these specifications:**

```glsl
// WebGL 1.0 (OpenGL ES 2.0)
#version 100

// WebGL 2.0 (OpenGL ES 3.0)
#version 300 es

// Desktop OpenGL
#version 330 core
#version 450 core
```

---

## 3. Code Patterns

### 3.1 WHEN creating a basic vertex/fragment shader pair

```glsl
// ❌ WRONG - No precision, poor structure
attribute vec3 position;
varying vec3 vPos;
void main() {
  vPos = position;
  gl_Position = vec4(position, 1.0);
}

// ✅ CORRECT - WebGL 2.0 vertex shader
#version 300 es
precision highp float;

// Uniforms
uniform mat4 u_modelMatrix;
uniform mat4 u_viewMatrix;
uniform mat4 u_projectionMatrix;
uniform mat3 u_normalMatrix;

// Vertex attributes
in vec3 a_position;
in vec3 a_normal;
in vec2 a_texCoord;

// Outputs to fragment shader
out vec3 v_worldPosition;
out vec3 v_worldNormal;
out vec2 v_texCoord;

void main() {
    // Transform to world space
    vec4 worldPosition = u_modelMatrix * vec4(a_position, 1.0);
    v_worldPosition = worldPosition.xyz;

    // Transform normal to world space
    v_worldNormal = normalize(u_normalMatrix * a_normal);

    // Pass through texture coordinates
    v_texCoord = a_texCoord;

    // Final clip space position
    gl_Position = u_projectionMatrix * u_viewMatrix * worldPosition;
}
```

```glsl
// ✅ CORRECT - WebGL 2.0 fragment shader with PBR lighting
#version 300 es
precision highp float;

// Constants
const float PI = 3.14159265359;
const float EPSILON = 0.0001;

// Uniforms
uniform vec3 u_cameraPosition;
uniform vec3 u_lightPosition;
uniform vec3 u_lightColor;
uniform float u_lightIntensity;

// Material properties
uniform vec3 u_albedo;
uniform float u_metallic;
uniform float u_roughness;
uniform float u_ao;

// Inputs from vertex shader
in vec3 v_worldPosition;
in vec3 v_worldNormal;
in vec2 v_texCoord;

// Output
out vec4 fragColor;

// PBR functions
float distributionGGX(vec3 N, vec3 H, float roughness) {
    float a = roughness * roughness;
    float a2 = a * a;
    float NdotH = max(dot(N, H), 0.0);
    float NdotH2 = NdotH * NdotH;

    float denom = (NdotH2 * (a2 - 1.0) + 1.0);
    denom = PI * denom * denom;

    return a2 / max(denom, EPSILON);  // Guard division
}

float geometrySchlickGGX(float NdotV, float roughness) {
    float r = roughness + 1.0;
    float k = (r * r) / 8.0;

    float denom = NdotV * (1.0 - k) + k;
    return NdotV / max(denom, EPSILON);
}

float geometrySmith(vec3 N, vec3 V, vec3 L, float roughness) {
    float NdotV = max(dot(N, V), 0.0);
    float NdotL = max(dot(N, L), 0.0);
    return geometrySchlickGGX(NdotV, roughness) *
           geometrySchlickGGX(NdotL, roughness);
}

vec3 fresnelSchlick(float cosTheta, vec3 F0) {
    return F0 + (1.0 - F0) * pow(clamp(1.0 - cosTheta, 0.0, 1.0), 5.0);
}

void main() {
    vec3 N = normalize(v_worldNormal);
    vec3 V = normalize(u_cameraPosition - v_worldPosition);
    vec3 L = normalize(u_lightPosition - v_worldPosition);
    vec3 H = normalize(V + L);

    // Calculate reflectance at normal incidence
    vec3 F0 = vec3(0.04);
    F0 = mix(F0, u_albedo, u_metallic);

    // Cook-Torrance BRDF
    float D = distributionGGX(N, H, u_roughness);
    float G = geometrySmith(N, V, L, u_roughness);
    vec3 F = fresnelSchlick(max(dot(H, V), 0.0), F0);

    vec3 numerator = D * G * F;
    float denominator = 4.0 * max(dot(N, V), 0.0) * max(dot(N, L), 0.0);
    vec3 specular = numerator / max(denominator, EPSILON);

    // Energy conservation
    vec3 kS = F;
    vec3 kD = vec3(1.0) - kS;
    kD *= 1.0 - u_metallic;

    // Final lighting
    float NdotL = max(dot(N, L), 0.0);
    vec3 radiance = u_lightColor * u_lightIntensity;
    vec3 Lo = (kD * u_albedo / PI + specular) * radiance * NdotL;

    // Ambient
    vec3 ambient = vec3(0.03) * u_albedo * u_ao;
    vec3 color = ambient + Lo;

    // HDR tonemapping
    color = color / (color + vec3(1.0));

    // Gamma correction
    color = pow(color, vec3(1.0 / 2.2));

    fragColor = vec4(color, 1.0);
}
```

### 3.2 WHEN implementing noise functions

```glsl
// ❌ WRONG - Non-deterministic or slow noise
float noise(vec2 p) {
  return fract(sin(p.x * 12.9898 + p.y * 78.233) * 43758.5453);
}

// ✅ CORRECT - High-quality Simplex noise
#version 300 es
precision highp float;

// Permutation polynomial
vec3 permute(vec3 x) {
    return mod(((x * 34.0) + 1.0) * x, 289.0);
}

// 2D Simplex noise
float snoise(vec2 v) {
    const vec4 C = vec4(
        0.211324865405187,   // (3.0-sqrt(3.0))/6.0
        0.366025403784439,   // 0.5*(sqrt(3.0)-1.0)
        -0.577350269189626,  // -1.0 + 2.0 * C.x
        0.024390243902439    // 1.0 / 41.0
    );

    // First corner
    vec2 i = floor(v + dot(v, C.yy));
    vec2 x0 = v - i + dot(i, C.xx);

    // Other corners
    vec2 i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
    vec4 x12 = x0.xyxy + C.xxzz;
    x12.xy -= i1;

    // Permutations
    i = mod(i, 289.0);
    vec3 p = permute(permute(i.y + vec3(0.0, i1.y, 1.0)) + i.x + vec3(0.0, i1.x, 1.0));

    vec3 m = max(0.5 - vec3(dot(x0, x0), dot(x12.xy, x12.xy), dot(x12.zw, x12.zw)), 0.0);
    m = m * m;
    m = m * m;

    // Gradients
    vec3 x = 2.0 * fract(p * C.www) - 1.0;
    vec3 h = abs(x) - 0.5;
    vec3 ox = floor(x + 0.5);
    vec3 a0 = x - ox;

    // Normalize gradients
    m *= 1.79284291400159 - 0.85373472095314 * (a0 * a0 + h * h);

    // Compute final value
    vec3 g;
    g.x = a0.x * x0.x + h.x * x0.y;
    g.yz = a0.yz * x12.xz + h.yz * x12.yw;
    return 130.0 * dot(m, g);
}

// Fractal Brownian Motion
float fbm(vec2 p, int octaves) {
    float value = 0.0;
    float amplitude = 0.5;
    float frequency = 1.0;

    // Bounded loop
    const int MAX_OCTAVES = 8;
    for (int i = 0; i < MAX_OCTAVES; i++) {
        if (i >= octaves) break;

        value += amplitude * snoise(p * frequency);
        frequency *= 2.0;
        amplitude *= 0.5;
    }

    return value;
}
```

### 3.3 WHEN implementing post-processing effects

```glsl
// ❌ WRONG - Hardcoded values, no safety
void main() {
  vec4 color = texture(u_texture, v_texCoord);
  color.rgb = pow(color.rgb, vec3(1.0/2.2));  // No bounds check
  fragColor = color;
}

// ✅ CORRECT - Bloom post-processing with safety
#version 300 es
precision highp float;

uniform sampler2D u_sceneTexture;
uniform sampler2D u_bloomTexture;
uniform float u_bloomIntensity;
uniform float u_exposure;
uniform float u_gamma;

in vec2 v_texCoord;
out vec4 fragColor;

// Safe pow for HDR
vec3 safePow(vec3 base, float exponent) {
    return pow(max(base, vec3(0.0)), vec3(exponent));
}

// ACES Filmic Tone Mapping
vec3 acesFilm(vec3 x) {
    float a = 2.51;
    float b = 0.03;
    float c = 2.43;
    float d = 0.59;
    float e = 0.14;
    return clamp((x * (a * x + b)) / (x * (c * x + d) + e), 0.0, 1.0);
}

// Gaussian blur kernel
vec3 gaussianBlur(sampler2D tex, vec2 uv, vec2 direction) {
    vec3 color = vec3(0.0);
    vec2 texelSize = 1.0 / vec2(textureSize(tex, 0));

    // 9-tap Gaussian
    const float weights[5] = float[](0.227027, 0.1945946, 0.1216216, 0.054054, 0.016216);

    color += texture(tex, uv).rgb * weights[0];

    for (int i = 1; i < 5; i++) {
        vec2 offset = direction * texelSize * float(i);
        color += texture(tex, uv + offset).rgb * weights[i];
        color += texture(tex, uv - offset).rgb * weights[i];
    }

    return color;
}

void main() {
    // Sample textures
    vec3 sceneColor = texture(u_sceneTexture, v_texCoord).rgb;
    vec3 bloomColor = texture(u_bloomTexture, v_texCoord).rgb;

    // Combine scene and bloom
    vec3 color = sceneColor + bloomColor * clamp(u_bloomIntensity, 0.0, 2.0);

    // Apply exposure
    color *= clamp(u_exposure, 0.1, 10.0);

    // Tone mapping
    color = acesFilm(color);

    // Gamma correction
    float gamma = clamp(u_gamma, 1.0, 3.0);
    color = safePow(color, 1.0 / gamma);

    fragColor = vec4(color, 1.0);
}
```

### 3.4 WHEN implementing SDF raymarching

```glsl
// ❌ WRONG - Unbounded raymarching
for (int i = 0; i < 1000000; i++) {  // Can freeze GPU!
  float d = map(p);
  if (d < 0.001) break;
  p += d * rd;
}

// ✅ CORRECT - Safe SDF raymarching
#version 300 es
precision highp float;

uniform vec2 u_resolution;
uniform float u_time;
uniform vec3 u_cameraPosition;

out vec4 fragColor;

// SDF primitives
float sdSphere(vec3 p, float r) {
    return length(p) - r;
}

float sdBox(vec3 p, vec3 b) {
    vec3 d = abs(p) - b;
    return length(max(d, 0.0)) + min(max(d.x, max(d.y, d.z)), 0.0);
}

float sdTorus(vec3 p, vec2 t) {
    vec2 q = vec2(length(p.xz) - t.x, p.y);
    return length(q) - t.y;
}

// Smooth minimum for blending
float smin(float a, float b, float k) {
    float h = clamp(0.5 + 0.5 * (b - a) / k, 0.0, 1.0);
    return mix(b, a, h) - k * h * (1.0 - h);
}

// Scene SDF
float map(vec3 p) {
    // Animated spheres
    float d = sdSphere(p - vec3(sin(u_time), 0.0, 0.0), 0.5);

    // Add torus
    d = smin(d, sdTorus(p - vec3(0.0, 0.0, 1.5), vec2(0.6, 0.2)), 0.3);

    // Ground plane
    d = min(d, p.y + 1.0);

    return d;
}

// Calculate normal via gradient
vec3 calcNormal(vec3 p) {
    const float h = 0.0001;
    const vec2 k = vec2(1.0, -1.0);
    return normalize(
        k.xyy * map(p + k.xyy * h) +
        k.yyx * map(p + k.yyx * h) +
        k.yxy * map(p + k.yxy * h) +
        k.xxx * map(p + k.xxx * h)
    );
}

// Safe raymarching
float raymarch(vec3 ro, vec3 rd) {
    float t = 0.0;

    // Bounded iteration with compile-time constant
    const int MAX_STEPS = 128;
    const float MAX_DIST = 100.0;
    const float SURF_DIST = 0.001;

    for (int i = 0; i < MAX_STEPS; i++) {
        vec3 p = ro + rd * t;
        float d = map(p);

        // Hit surface
        if (d < SURF_DIST) return t;

        // Too far
        if (t > MAX_DIST) break;

        // Advance safely (prevent overshooting)
        t += d * 0.9;
    }

    return -1.0;  // No hit
}

// Soft shadows
float softShadow(vec3 ro, vec3 rd, float mint, float maxt, float k) {
    float res = 1.0;
    float t = mint;

    const int MAX_STEPS = 64;
    for (int i = 0; i < MAX_STEPS; i++) {
        if (t > maxt) break;

        float h = map(ro + rd * t);
        if (h < 0.001) return 0.0;

        res = min(res, k * h / t);
        t += clamp(h, 0.01, 0.2);
    }

    return clamp(res, 0.0, 1.0);
}

void main() {
    // Normalized coordinates
    vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution) / u_resolution.y;

    // Camera setup
    vec3 ro = u_cameraPosition;
    vec3 rd = normalize(vec3(uv, 1.0));

    // Raymarch
    float t = raymarch(ro, rd);

    vec3 color = vec3(0.0);

    if (t > 0.0) {
        vec3 p = ro + rd * t;
        vec3 n = calcNormal(p);

        // Lighting
        vec3 lightPos = vec3(2.0, 4.0, -2.0);
        vec3 lightDir = normalize(lightPos - p);

        float diff = max(dot(n, lightDir), 0.0);
        float shadow = softShadow(p + n * 0.01, lightDir, 0.01, 10.0, 16.0);

        color = vec3(0.8) * diff * shadow + vec3(0.1);
    }

    // Gamma correction
    color = pow(color, vec3(1.0 / 2.2));

    fragColor = vec4(color, 1.0);
}
```

### 3.5 WHEN using Three.js with custom shaders

```typescript
// ❌ WRONG - Inline shader strings, no validation
const material = new THREE.ShaderMaterial({
  vertexShader: 'void main() { gl_Position = vec4(position, 1.0); }',
  fragmentShader: 'void main() { gl_FragColor = vec4(1.0); }',
});

// ✅ CORRECT - Structured shader management
import * as THREE from 'three';

// Type-safe uniform definitions
interface CustomUniforms {
  u_time: THREE.IUniform<number>;
  u_resolution: THREE.IUniform<THREE.Vector2>;
  u_mouse: THREE.IUniform<THREE.Vector2>;
  u_color: THREE.IUniform<THREE.Color>;
}

// Vertex shader with proper attributes
const vertexShader = /* glsl */ `
  precision highp float;

  uniform float u_time;

  varying vec2 vUv;
  varying vec3 vNormal;
  varying vec3 vPosition;

  void main() {
    vUv = uv;
    vNormal = normalize(normalMatrix * normal);
    vPosition = (modelMatrix * vec4(position, 1.0)).xyz;

    // Vertex animation
    vec3 pos = position;
    pos.z += sin(pos.x * 2.0 + u_time) * 0.1;

    gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
  }
`;

// Fragment shader
const fragmentShader = /* glsl */ `
  precision highp float;

  uniform float u_time;
  uniform vec2 u_resolution;
  uniform vec3 u_color;

  varying vec2 vUv;
  varying vec3 vNormal;
  varying vec3 vPosition;

  void main() {
    // Simple lighting
    vec3 lightDir = normalize(vec3(1.0, 1.0, 1.0));
    float diff = max(dot(vNormal, lightDir), 0.0);

    vec3 color = u_color * (diff * 0.8 + 0.2);

    gl_FragColor = vec4(color, 1.0);
  }
`;

// Create material with type safety
function createCustomMaterial(): THREE.ShaderMaterial {
  const uniforms: CustomUniforms = {
    u_time: { value: 0 },
    u_resolution: { value: new THREE.Vector2(window.innerWidth, window.innerHeight) },
    u_mouse: { value: new THREE.Vector2(0.5, 0.5) },
    u_color: { value: new THREE.Color(0x00ff88) },
  };

  const material = new THREE.ShaderMaterial({
    uniforms,
    vertexShader,
    fragmentShader,
    side: THREE.DoubleSide,
  });

  // Validate shader compilation
  const renderer = new THREE.WebGLRenderer();
  const testScene = new THREE.Scene();
  const testMesh = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), material);
  testScene.add(testMesh);

  // Force compilation to check for errors
  renderer.compile(testScene, new THREE.PerspectiveCamera());

  const gl = renderer.getContext();
  const program = renderer.properties.get(material).program;

  if (program) {
    const vertexShaderLog = gl.getShaderInfoLog(program.vertexShader);
    const fragmentShaderLog = gl.getShaderInfoLog(program.fragmentShader);

    if (vertexShaderLog) console.warn('Vertex shader:', vertexShaderLog);
    if (fragmentShaderLog) console.warn('Fragment shader:', fragmentShaderLog);
  }

  renderer.dispose();

  return material;
}

// Animation loop with safe uniform updates
function animate(material: THREE.ShaderMaterial, clock: THREE.Clock) {
  const uniforms = material.uniforms as CustomUniforms;

  // Update time (prevent overflow)
  uniforms.u_time.value = clock.getElapsedTime() % 1000;

  requestAnimationFrame(() => animate(material, clock));
}
```

---

## 4. Anti-Patterns

**NEVER:**
- Construct shaders from user input
- Use unbounded loops
- Skip precision declarations
- Divide without zero-check
- Use vendor-specific extensions without fallback
- Hardcode resolution or screen-dependent values
- Skip gamma correction
- Use `discard` excessively (kills early-z)

---

## 5. Testing

**ALWAYS test shaders:**

```typescript
import { describe, it, expect } from 'vitest';

describe('Shader Compilation', () => {
  it('compiles vertex shader without errors', () => {
    const gl = createWebGLContext();
    const shader = gl.createShader(gl.VERTEX_SHADER)!;
    gl.shaderSource(shader, vertexShader);
    gl.compileShader(shader);

    const success = gl.getShaderParameter(shader, gl.COMPILE_STATUS);
    if (!success) {
      console.error(gl.getShaderInfoLog(shader));
    }
    expect(success).toBe(true);
  });

  it('compiles fragment shader without errors', () => {
    const gl = createWebGLContext();
    const shader = gl.createShader(gl.FRAGMENT_SHADER)!;
    gl.shaderSource(shader, fragmentShader);
    gl.compileShader(shader);

    const success = gl.getShaderParameter(shader, gl.COMPILE_STATUS);
    expect(success).toBe(true);
  });

  it('links program successfully', () => {
    const gl = createWebGLContext();
    const program = createProgram(gl, vertexShader, fragmentShader);

    const success = gl.getProgramParameter(program, gl.LINK_STATUS);
    expect(success).toBe(true);
  });

  it('handles uniform updates without errors', () => {
    const gl = createWebGLContext();
    const program = createProgram(gl, vertexShader, fragmentShader);
    gl.useProgram(program);

    const timeLoc = gl.getUniformLocation(program, 'u_time');
    expect(timeLoc).not.toBeNull();

    // Should not throw
    gl.uniform1f(timeLoc, 1.5);
  });
});

function createWebGLContext(): WebGL2RenderingContext {
  const canvas = document.createElement('canvas');
  const gl = canvas.getContext('webgl2');
  if (!gl) throw new Error('WebGL2 not supported');
  return gl;
}

function createProgram(
  gl: WebGL2RenderingContext,
  vsSource: string,
  fsSource: string
): WebGLProgram {
  const vs = gl.createShader(gl.VERTEX_SHADER)!;
  gl.shaderSource(vs, vsSource);
  gl.compileShader(vs);

  const fs = gl.createShader(gl.FRAGMENT_SHADER)!;
  gl.shaderSource(fs, fsSource);
  gl.compileShader(fs);

  const program = gl.createProgram()!;
  gl.attachShader(program, vs);
  gl.attachShader(program, fs);
  gl.linkProgram(program);

  return program;
}
```

---

## 6. Pre-Generation Checklist

**BEFORE generating any GLSL code:**

- [ ] Precision specified for all floats
- [ ] All loops have compile-time bounds
- [ ] Division by zero guarded
- [ ] No shader code from user input
- [ ] Uniforms validated before upload
- [ ] Cross-platform tested (WebGL 1/2)
- [ ] Gamma correction applied
- [ ] Array accesses bounds-checked
- [ ] No vendor-specific extensions
- [ ] Performance profiled on target hardware
