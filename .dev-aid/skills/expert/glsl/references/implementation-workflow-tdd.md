## 3. Implementation Workflow (TDD)

### 3.1 Step 1: Write Failing Test First

```typescript
// tests/shaders/holographic-panel.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { WebGLTestContext, captureFramebuffer, compareImages } from '../utils/webgl-test'

describe('HolographicPanelShader', () => {
  let ctx: WebGLTestContext

  beforeEach(() => {
    ctx = new WebGLTestContext(256, 256)
  })

  // Unit test: Shader compiles
  it('should compile without errors', () => {
    const shader = ctx.compileShader(holoFragSource, ctx.gl.FRAGMENT_SHADER)
    expect(shader).not.toBeNull()
    expect(ctx.getShaderErrors()).toEqual([])
  })

  // Unit test: Uniforms are accessible
  it('should have required uniforms', () => {
    const program = ctx.createProgram(vertSource, holoFragSource)
    expect(ctx.getUniformLocation(program, 'uTime')).not.toBeNull()
    expect(ctx.getUniformLocation(program, 'uColor')).not.toBeNull()
    expect(ctx.getUniformLocation(program, 'uOpacity')).not.toBeNull()
  })

  // Visual regression test
  it('should render scanlines correctly', async () => {
    ctx.renderShader(holoFragSource, { uTime: 0, uColor: [0, 0.5, 1], uOpacity: 1 })
    const result = captureFramebuffer(ctx)
    const baseline = await loadBaseline('holographic-scanlines.png')
    expect(compareImages(result, baseline, { threshold: 0.01 })).toBeLessThan(0.01)
  })

  // Edge case test
  it('should handle extreme UV values', () => {
    const testCases = [
      { uv: [0, 0], expected: 'no crash' },
      { uv: [1, 1], expected: 'no crash' },
      { uv: [0.5, 0.5], expected: 'no crash' }
    ]
    testCases.forEach(({ uv }) => {
      expect(() => ctx.renderAtUV(holoFragSource, uv)).not.toThrow()
    })
  })
})
```

### 3.2 Step 2: Implement Minimum to Pass

```glsl
// Start with minimal shader that passes tests
#version 300 es
precision highp float;

uniform float uTime;
uniform vec3 uColor;
uniform float uOpacity;

in vec2 vUv;
out vec4 fragColor;

void main() {
  // Minimal implementation to pass compilation test
  fragColor = vec4(uColor, uOpacity);
}
```

### 3.3 Step 3: Refactor with Full Implementation

```glsl
// Expand to full implementation after tests pass
void main() {
  vec2 uv = vUv;
  float scanline = sin(uv.y * 100.0) * 0.1 + 0.9;
  float pulse = sin(uTime * 2.0) * 0.1 + 0.9;
  vec3 color = uColor * scanline * pulse;
  fragColor = vec4(color, uOpacity);
}
```

### 3.4 Step 4: Run Full Verification

```bash
# Run all shader tests
npm run test:shaders

# Visual regression tests
npm run test:visual -- --update-snapshots  # First time only
npm run test:visual

# Performance benchmark
npm run bench:shaders

# Cross-browser compilation check
npm run test:webgl-compat
```


