---
name: webgl
description: WebGL shaders and effects for JARVIS 3D HUD
risk_level: MEDIUM
version: 1.0.0
---

# WebGL Development Skill

> **File Organization**: This skill uses split structure. See `references/` for advanced patterns and security examples.


### 0.4 Progressive Disclosure (500-Line Limit)

**⚠️ CRITICAL**: This SKILL.md file MUST stay <500 lines for Claude Code to load it.

**If this file is approaching 500 lines**:
- Move detailed examples to `references/advanced-patterns.md`
- Move security examples to `references/security-examples.md`
- Move troubleshooting to `references/troubleshooting.md`
- Keep only summaries and links in main file

📚 **For complete progressive disclosure guide**: See `../../../template-references/progressive-disclosure.md`

---

## 0. Anti-Hallucination Protocol

## 0. Anti-Hallucination Protocol

### 0.1 Quick Risk Assessment

**Risk Level**: MEDIUM

**Key Risk Factors**:
- Security concerns in medium-risk domain
- 3 security issues/patterns identified
- Common attack vectors: Memory exhaustion, GPU fingerprinting, Shader DoS
- Requires security awareness and best practices

**Immediate Security Actions**:
1. Review security concerns below before any implementation
2. Never proceed without understanding attack surface
3. Implement security controls from § 0.3 as mandatory requirements

### 0.2 Vulnerability Research Protocol

**MANDATORY**: Before ANY implementation, research current vulnerabilities.

**Step 1: CVE Database Search** (NVD, MITRE)
```bash
# Search for latest CVEs (update dates for current year)
https://nvd.nist.gov/vuln/search
# Keywords: [technology name], [framework version]
```

**Step 2: Known Vulnerabilities (2024-2025)**

   - **WEBGL-MEMORY-LEAK** (CVSS N/A): WebGL memory leaks
     Source: https://www.khronos.org/webgl/security/
   - **GPU-FINGERPRINTING** (CVSS N/A): GPU fingerprinting attacks
     Source: https://browserleaks.com/webgl
   - **SHADER-DOS** (CVSS N/A): DoS via malicious shaders
     Source: https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices

**Step 3: Common Attack Patterns**

   - Memory exhaustion
   - GPU fingerprinting
   - Shader DoS
   - Cross-origin texture leaks

**Step 4: MITRE ATT&CK Mapping**
- Tactic: [Initial Access, Execution, Persistence, Privilege Escalation]
- Review MITRE ATT&CK framework for latest techniques

**Update Frequency**: Check for new CVEs weekly during active development.

### 0.3 Hallucination Prevention Checklist

**CRITICAL**: These rules are ABSOLUTE. Violation = security incident.

**Domain-Specific Security Rules**:

- ❌ NEVER render untrusted content in WebGL
- ❌ NEVER allow unlimited texture sizes
- ❌ ALWAYS validate shader complexity
- ❌ ALWAYS use CORS for textures

**Before ANY code generation**:
1. ✅ Verify rule compliance for proposed implementation
2. ✅ Check if solution introduces any prohibited patterns
3. ✅ Validate all security assumptions
4. ✅ Confirm defensive coding practices are applied

**If uncertain**: STOP and research. Never guess on security.


## 1. Overview

This skill provides WebGL expertise for creating custom shaders and visual effects in the JARVIS AI Assistant HUD. It focuses on GPU-accelerated rendering with security considerations.

**Risk Level**: MEDIUM - Direct GPU access, potential for resource exhaustion, driver vulnerabilities

**Primary Use Cases**:
- Custom shaders for holographic effects
- Post-processing effects (bloom, glitch)
- Particle systems with compute shaders
- Real-time data visualization

## 2. Core Responsibilities

### 2.1 Fundamental Principles

1. **TDD First**: Write tests before implementation - test shaders, contexts, and resources
2. **Performance Aware**: Optimize GPU usage - batch draws, reuse buffers, compress textures
3. **GPU Safety**: Implement timeout mechanisms and resource limits
4. **Shader Validation**: Validate all shader inputs before compilation
5. **Context Management**: Handle context loss gracefully
6. **Performance Budgets**: Set strict limits on draw calls and triangles
7. **Fallback Strategy**: Provide non-WebGL fallbacks
8. **Memory Management**: Track and limit texture/buffer usage

## 3. Technology Stack & Versions

### 3.1 Browser Support

| Browser | WebGL 2.0 | Notes |
|---------|-----------|-------|
| Chrome | 56+ | Full support |
| Firefox | 51+ | Full support |
| Safari | 15+ | WebGL 2.0 support |
| Edge | 79+ | Chromium-based |

### 3.2 Security Considerations

```typescript
// Check WebGL support and capabilities
function getWebGLContext(canvas: HTMLCanvasElement): WebGL2RenderingContext | null {
  const gl = canvas.getContext('webgl2', {
    alpha: true,
    antialias: true,
    powerPreference: 'high-performance',
    failIfMajorPerformanceCaveat: true  // Fail if software rendering
  })

  if (!gl) {
    console.warn('WebGL 2.0 not supported')
    return null
  }

  return gl
}
```


## 4. Quality Assurance Checklist

**Before implementing this skill, ensure**:

### 4.1 Pre-Implementation Setup
- [ ] Virtual environment created and activated
- [ ] Dependencies installed from requirements.txt
- [ ] Pre-commit hooks installed (`pre-commit install`)
- [ ] Linters installed (black, isort, flake8, mypy, bandit)

### 4.2 Dependency Management
- [ ] All dependencies pinned with exact versions (==)
- [ ] No manual transitive dependency pins
- [ ] Dependencies tested in clean environment

### 4.3 Code Quality Gates (Run BEFORE committing)
- [ ] `black .` - Code formatted
- [ ] `isort .` - Imports sorted
- [ ] `flake8 . --max-line-length=120` - No linting errors
- [ ] `mypy . --ignore-missing-imports` - Type checking passes
- [ ] `bandit -r .` - Security scan clean

### 4.4 Security Validation
- [ ] Input validation for ALL external inputs
- [ ] Path traversal prevention implemented
- [ ] Command injection prevention (no shell=True)
- [ ] SQL injection prevention (parameterized queries)
- [ ] Secrets not in code or error messages

📚 **For complete security validation guide**: See `../../../template-references/security-framework.md`

### 4.5 Test Coverage Requirements
- [ ] Tests written BEFORE implementation (TDD)
- [ ] Unit tests for all public functions
- [ ] Edge case tests (empty, null, max values)
- [ ] Security tests (injection, traversal, overflow)
- [ ] Code coverage >80%

### 4.6 Documentation Requirements
- [ ] Docstrings for all public functions/classes
- [ ] Security considerations documented
- [ ] Examples of correct usage
- [ ] Known limitations documented

---

## 5. Implementation Patterns

// ✅ Safe shader compilation with error handling
export function compileShader(
  gl: WebGL2RenderingContext,
  source: string,
  type: number
): WebGLShader | null {
  const shader = gl.createShader(type)
  if (!shader) return null

📚 **For complete details**: See `references/implementation-patterns.md`

---
## 6. Implementation Workflow (TDD)

### 5.1 Step-by-Step Process

1. **Write failing test** -> 2. **Implement minimum** -> 3. **Refactor** -> 4. **Verify**

```typescript
// Step 1: tests/webgl/shaderCompilation.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { compileShader } from '@/utils/shaderUtils'

describe('WebGL Shader Compilation', () => {
  let gl: WebGL2RenderingContext

  beforeEach(() => {
    gl = document.createElement('canvas').getContext('webgl2')!
  })

  it('should compile valid shader', () => {
    const source = `#version 300 es
      in vec4 aPosition;
      void main() { gl_Position = aPosition; }`
    expect(compileShader(gl, source, gl.VERTEX_SHADER)).not.toBeNull()
  })

  it('should return null for invalid shader', () => {
    expect(compileShader(gl, 'invalid', gl.FRAGMENT_SHADER)).toBeNull()
  })
})

// Step 2-3: Implement and refactor (see section 4.1)
// Step 4: npm test && npm run typecheck && npm run build
```

### 5.2 Testing Context and Resources

```typescript
describe('WebGL Context', () => {
  it('should handle context loss', async () => {
    const { gl, contextLost } = useWebGL(ref(canvas))
    gl.value?.getExtension('WEBGL_lose_context')?.loseContext()
    await nextTick()
    expect(contextLost.value).toBe(true)
  })
})

describe('Resource Manager', () => {
  it('should enforce memory limits', () => {
    const manager = new WebGLResourceManager(gl)
    expect(manager.createTexture(1024, 1024)).not.toBeNull()
    expect(manager.createTexture(16384, 16384)).toBeNull() // Exceeds limit
  })
})
```

## 7. Performance Patterns

### 6.1 Buffer Reuse

```typescript
// Bad - Creates new buffer every frame
const buffer = gl.createBuffer()
gl.bufferData(gl.ARRAY_BUFFER, data, gl.DYNAMIC_DRAW)
gl.deleteBuffer(buffer)

// Good - Reuse buffer, update only data
gl.bufferSubData(gl.ARRAY_BUFFER, 0, data)  // Update existing buffer
```

### 6.2 Draw Call Batching

```typescript
// Bad - One draw call per object
objects.forEach(obj => {
  gl.useProgram(obj.program)
  gl.drawElements(...)
})

// Good - Batch by material/shader
const batches = groupByMaterial(objects)
batches.forEach(batch => {
  gl.useProgram(batch.program)
  batch.objects.forEach(obj => gl.drawElements(...))
})
```

### 6.3 Texture Compression

```typescript
// Bad - Always uncompressed RGBA
gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, image)

// Good - Use compressed formats when available
const ext = gl.getExtension('WEBGL_compressed_texture_s3tc')
if (ext) gl.compressedTexImage2D(gl.TEXTURE_2D, 0, ext.COMPRESSED_RGBA_S3TC_DXT5_EXT, ...)
```

### 6.4 Instanced Rendering

```typescript
// Bad - Individual draw calls for particles
particles.forEach(p => {
  gl.uniform3fv(uPosition, p.position)
  gl.drawArrays(gl.TRIANGLES, 0, 6)
})

// Good - Single instanced draw call
gl.drawArraysInstanced(gl.TRIANGLES, 0, 6, particles.length)
```

### 6.5 VAO Usage

```typescript
// Bad - Rebind attributes every frame
gl.enableVertexAttribArray(0)
gl.vertexAttribPointer(0, 3, gl.FLOAT, false, 0, 0)

// Good - Use VAO to store attribute state
const vao = gl.createVertexArray()
gl.bindVertexArray(vao)
// Set up once, then just bind VAO for rendering
```

## 8. Security Standards

### 7.1 Known Vulnerabilities

| CVE | Severity | Description | Mitigation |
|-----|----------|-------------|------------|
| CVE-2024-11691 | HIGH | Apple M series memory corruption | Update browser, OS patches |
| CVE-2023-1531 | HIGH | Chrome use-after-free | Update Chrome |

### 7.2 OWASP Top 10 Coverage

| OWASP Category | Risk | Mitigation |
|----------------|------|------------|
| A06 Vulnerable Components | HIGH | Keep browsers updated |
| A10 SSRF | LOW | Context isolation by browser |

### 7.3 GPU Resource Protection

```typescript
// ✅ Implement resource limits
const LIMITS = {
  maxDrawCalls: 100,
  maxTriangles: 1_000_000,
  maxTextures: 32,
  maxTextureSize: 4096
}

function checkLimits(stats: RenderStats): boolean {
  if (stats.drawCalls > LIMITS.maxDrawCalls) {
    console.error('Draw call limit exceeded')
    return false
  }
  if (stats.triangles > LIMITS.maxTriangles) {
    console.error('Triangle limit exceeded')
    return false
  }
  return true
}
```

## 9. Common Mistakes & Anti-Patterns

### 8.1 Critical Security Anti-Patterns

#### Never: Skip Context Loss Handling

```typescript
// ❌ DANGEROUS - App crashes on context loss
const gl = canvas.getContext('webgl2')
// No context loss handler!

// ✅ SECURE - Handle gracefully
canvas.addEventListener('webglcontextlost', handleLoss)
canvas.addEventListener('webglcontextrestored', handleRestore)
```

#### Never: Unlimited Resource Allocation

```typescript
// ❌ DANGEROUS - GPU memory exhaustion
for (let i = 0; i < userCount; i++) {
  textures.push(gl.createTexture())
}

// ✅ SECURE - Enforce limits
if (textureCount < MAX_TEXTURES) {
  textures.push(gl.createTexture())
}
```

### 8.2 Performance Anti-Patterns

#### Avoid: Excessive State Changes

```typescript
// ❌ BAD - Unbatched draw calls
objects.forEach(obj => {
  gl.useProgram(obj.program)
  gl.bindTexture(gl.TEXTURE_2D, obj.texture)
  gl.drawElements(...)
})

// ✅ GOOD - Batch by material
batches.forEach(batch => {
  gl.useProgram(batch.program)
  gl.bindTexture(gl.TEXTURE_2D, batch.texture)
  batch.objects.forEach(obj => gl.drawElements(...))
})
```

## 10. Pre-Implementation Checklist

### Phase 1: Before Writing Code
- [ ] Write failing tests for shaders, context, and resources
- [ ] Define performance budgets (draw calls <100, memory <256MB)
- [ ] Identify required WebGL extensions

### Phase 2: During Implementation
- [ ] Context loss handling with recovery
- [ ] Resource limits and memory tracking
- [ ] Shader validation before compilation
- [ ] Use VAOs, batch draws, reuse buffers
- [ ] Instanced rendering for particles

##### 7. Performance Patterns

// Good - Reuse buffer, update only data
gl.bufferSubData(gl.ARRAY_BUFFER, 0, data)  // Update existing buffer
```

📚 **For complete details**: See `references/performance-patterns.md`

---
## 9. Common Mistakes & Anti-Patterns

## 9. Common Mistakes & Anti-Patterns

📚 **For complete details**: See `references/common-mistakes-anti-patterns.md`

---
