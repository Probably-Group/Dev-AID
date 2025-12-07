---
name: threejs-tresjs
description: 3D HUD rendering with Three.js and TresJS for JARVIS AI Assistant
risk_level: MEDIUM
version: 1.0.0
---

# Three.js / TresJS Development Skill

> **File Organization**: This skill uses split structure. See `references/` for detailed patterns, examples, and guides.

## 0. Anti-Hallucination Protocol

**🚨 MANDATORY: Read before implementing any Three.js/TresJS code**

### Verification Requirements

When using this skill to implement 3D rendering features, you MUST:

1. **Verify Before Implementing**
   - ✅ Check official Three.js documentation at threejs.org
   - ✅ Confirm TresJS API methods at tresjs.org
   - ✅ Validate WebGL best practices against official guides
   - ❌ Never guess Three.js API methods
   - ❌ Never invent geometry/material properties
   - ❌ Never assume compatibility without checking versions

2. **Use Available Tools**
   - 🔍 Read: Check existing codebase for 3D patterns
   - 🔍 Grep: Search for similar Three.js implementations
   - 🔍 WebSearch: Verify Three.js API documentation
   - 🔍 WebFetch: Read official Three.js/TresJS docs

3. **Verify if Certainty < 80%**
   - If uncertain about ANY Three.js feature/API/pattern
   - STOP and verify before implementing
   - Document verification source in response
   - Errors in 3D rendering can cause GPU crashes, memory leaks, security vulnerabilities

4. **Common Three.js Hallucination Traps** (AVOID)
   - ❌ Inventing Three.js class methods that don't exist
   - ❌ Confusing Three.js versions (APIs change between versions)
   - ❌ Making up TresJS component props
   - ❌ Assuming automatic resource disposal (must call .dispose())
   - ❌ Inventing shader uniform names
   - ❌ Guessing geometry constructor parameters

### Self-Check Checklist

Before EVERY response with Three.js/TresJS code:
- [ ] All Three.js classes/methods verified against official docs
- [ ] TresJS component props verified against TresJS docs
- [ ] Resource disposal (geometry/material) included
- [ ] Color inputs validated (ReDoS prevention)
- [ ] Can cite official documentation sources

**⚠️ CRITICAL**: Three.js code with hallucinated APIs causes runtime errors, GPU memory leaks, and security vulnerabilities. Always verify.

---


### 0.4 Progressive Disclosure (500-Line Limit)

**⚠️ CRITICAL**: This SKILL.md file MUST stay <500 lines for Claude Code to load it.

**If this file is approaching 500 lines**:
- Move detailed examples to `references/advanced-patterns.md`
- Move security examples to `references/security-examples.md`
- Move troubleshooting to `references/troubleshooting.md`
- Keep only summaries and links in main file

📚 **For complete progressive disclosure guide**: See `../../../template-references/progressive-disclosure.md`

---

## 1. Overview

This skill provides expertise for building 3D HUD interfaces using Three.js and TresJS (Vue 3 integration). It focuses on creating performant, visually stunning holographic displays for the JARVIS AI Assistant.

**Risk Level**: MEDIUM - GPU resource consumption, potential ReDoS in color parsing, WebGL security considerations

**Primary Use Cases**:
- Rendering 3D holographic HUD panels
- Animated status indicators and gauges
- Particle effects for system visualization
- Real-time metric displays with 3D elements

### Key Technologies

| Package | Version | Purpose |
|---------|---------|---------|
| three | ^0.160.0+ | Core 3D rendering engine |
| @tresjs/core | ^4.0.0 | Vue 3 integration |
| @tresjs/cientos | ^3.0.0 | Component library |
| postprocessing | ^6.0.0 | Visual effects |

**Security Note**: Always use Three.js >= 0.137.0 to avoid known XSS and ReDoS vulnerabilities.

---

## 2. Core Responsibilities

### 2.1 Fundamental Principles

1. **TDD First**: Write tests before implementation - verify 3D components render correctly
2. **Performance Aware**: Optimize for 60fps with instancing, LOD, and efficient render loops
3. **Resource Management**: Always dispose of geometries, materials, and textures to prevent memory leaks
4. **Vue Reactivity Integration**: Use TresJS for seamless Vue 3 composition API integration
5. **Safe Color Parsing**: Validate color inputs to prevent ReDoS attacks (CVE-2020-28496)
6. **GPU Protection**: Implement safeguards against GPU resource exhaustion
7. **Accessibility**: Provide fallbacks for devices without WebGL support

### 2.2 Security Priorities

**Critical Vulnerabilities to Mitigate**:
- **CVE-2020-28496** (HIGH): ReDoS in color parsing - validate all color inputs
- **CVE-2022-0177** (MEDIUM): XSS in documentation - keep dependencies updated
- **GPU Resource Exhaustion**: Limit triangle count and draw calls
- **Memory Leaks**: Always dispose Three.js objects on component unmount

---

## 3. Implementation Workflow (TDD)

### Quick TDD Process

1. **Write Failing Test First**
   ```typescript
   it('renders HUD panel with correct dimensions', () => {
     const wrapper = mount(HUDPanel, { props: { width: 2, height: 1 } })
     expect(wrapper.exists()).toBe(true)
   })
   ```

2. **Implement Minimum Code**
   ```vue
   <template>
     <TresMesh>
       <TresPlaneGeometry :args="[props.width, props.height]" />
       <TresMeshBasicMaterial color="#001122" />
     </TresMesh>
   </template>
   ```

3. **Refactor & Optimize**
   - Add resource disposal
   - Implement performance optimizations
   - Add error handling

4. **Verify**
   ```bash
   npm test && npm run typecheck
   ```

**See `references/testing-guide.md` for comprehensive TDD patterns**

---


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

## 5. Quick Start Patterns

### 4.1 Basic Scene Setup

```vue
<script setup lang="ts">
import { TresCanvas } from '@tresjs/core'

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
    <TresAmbientLight :intensity="0.5" />
    <TresDirectionalLight :position="[5, 5, 5]" />

    <HUDPanels />
  </TresCanvas>
</template>
```

### 4.2 Safe Color Handling (ReDoS Prevention)

```typescript
// ✅ SECURE - Validated color parsing
export function safeParseColor(input: string): Color {
  const hexPattern = /^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$/

  if (!hexPattern.test(input)) {
    console.warn('Invalid color, using default')
    return new Color(0x00ff00)
  }

  return new Color(input)
}

// ❌ DANGEROUS - Never do this
// const color = new Color(userInput)  // ReDoS vulnerability!
```

### 4.3 Memory-Safe Component

```vue
<script setup lang="ts">
import { onUnmounted, shallowRef } from 'vue'
import { Mesh } from 'three'

// ✅ Use shallowRef for Three.js objects
const meshRef = shallowRef<Mesh | null>(null)

// ✅ Always cleanup on unmount
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

**See `references/implementation-patterns.md` for more patterns**

---

## 6. Performance Guidelines

### Key Optimization Strategies

1. **Use Instancing** - Render 1000+ objects as efficiently as 1 object
2. **Implement LOD** - Reduce detail for distant objects
3. **Object Pooling** - Reuse objects instead of creating/destroying
4. **Frustum Culling** - Don't render off-screen objects
5. **Minimize Allocations** - Never create objects in render loop
6. **Share Resources** - Reuse geometries and materials

### Quick Performance Check

```typescript
// ❌ BAD - Creates new objects every frame
function animate() {
  mesh.position.add(new Vector3(0, 0.01, 0))  // GC pressure!
}

// ✅ GOOD - Reuse objects
const velocity = new Vector3(0, 0.01, 0)
function animate() {
  mesh.position.add(velocity)
}
```

**See `references/performance-optimization.md` for detailed strategies**

---

## 7. Security Best Practices

### Critical Security Checks

- [ ] Three.js version >= 0.137.0 (XSS fix)
- [ ] All color inputs validated before parsing
- [ ] No user input directly to `new Color()`
- [ ] Resource limits enforced (max triangles, draw calls)
- [ ] All geometries/materials disposed on unmount
- [ ] Text content sanitized before rendering

### GPU Resource Limits

```typescript
export function useResourceLimit() {
  const MAX_TRIANGLES = 1_000_000
  const MAX_DRAW_CALLS = 100

  function checkGeometry(geometry: BufferGeometry): boolean {
    const triangles = geometry.index
      ? geometry.index.count / 3
      : geometry.attributes.position.count / 3

    if (triangles > MAX_TRIANGLES) {
      console.error('Triangle limit exceeded')
      return false
    }
    return true
  }

  return { checkGeometry }
}
```

**See `references/security-examples.md` for comprehensive security patterns**

---

## 8. Common Mistakes to Avoid

### Critical Anti-Patterns

| Anti-Pattern | Impact | Solution |
|--------------|--------|----------|
| Parse user colors directly | ReDoS vulnerability | Use `safeParseColor()` |
| Skip resource disposal | Memory leaks | Always dispose in `onUnmounted()` |
| Create objects in render loop | GC pressure | Pre-allocate and reuse |
| Clone unnecessarily | GPU memory waste | Share resources or use instancing |
| Use reactive refs | Performance overhead | Use `shallowRef()` |

### Quick Anti-Pattern Check

```typescript
// ❌ DANGEROUS
const color = new Color(userInput)  // ReDoS!
const mesh = ref(new Mesh())        // Reactive overhead!

// ✅ SECURE
const color = safeParseColor(userInput)
const mesh = shallowRef(new Mesh())
```

**See `references/anti-patterns.md` for detailed anti-patterns and solutions**

---

## 9. Testing Strategy

### Test Coverage Requirements

1. **Component Tests**: Verify rendering, props, disposal
2. **Performance Tests**: Ensure 60fps with target load
3. **Security Tests**: Validate input sanitization
4. **Resource Tests**: Verify cleanup on unmount

### Example Test

```typescript
describe('HUDPanel', () => {
  it('disposes resources on unmount', () => {
    const wrapper = mount(HUDPanel)
    const disposeSpy = vi.spyOn(wrapper.vm.meshRef.geometry, 'dispose')

    wrapper.unmount()

    expect(disposeSpy).toHaveBeenCalled()
  })
})
```

**See `references/testing-guide.md` for comprehensive testing patterns**

---

## 10. Pre-Deployment Checklist

### Security Verification
- [ ] Three.js version >= 0.137.0
- [ ] All color inputs validated
- [ ] Resource limits enforced
- [ ] No unvalidated text rendering

### Performance Verification
- [ ] All resources disposed on unmount
- [ ] Instancing used for repeated objects (>10)
- [ ] No object creation in render loop
- [ ] LOD implemented for complex scenes
- [ ] Frame rate >= 60fps under target load

### Code Quality
- [ ] All tests passing
- [ ] TypeScript errors resolved
- [ ] ESLint warnings addressed
- [ ] Components separated by concern

---

## 11. References

### Detailed Documentation

- **`references/implementation-patterns.md`** - Complete implementation examples for HUD panels, instancing, text rendering
- **`references/testing-guide.md`** - TDD workflow, component tests, performance tests, resource disposal tests
- **`references/performance-optimization.md`** - Instancing, LOD, frustum culling, object pooling, shader optimization
- **`references/security-examples.md`** - Security standards, ReDoS prevention, GPU protection, vulnerability mitigation
- **`references/anti-patterns.md`** - Common mistakes, security anti-patterns, performance anti-patterns, Vue integration issues
- **`references/3d-patterns.md`** - HUD interface patterns, particle systems, camera animations, post-processing
- **`references/advanced-patterns.md`** - Custom shaders, post-processing effects, physics integration

### Official Documentation

- Three.js: https://threejs.org/docs/
- TresJS: https://tresjs.org/
- WebGL Best Practices: https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices

---

## 12. Quick Reference

### Common Operations

```typescript
// Create and dispose mesh
const mesh = new Mesh(geometry, material)
scene.add(mesh)

// Later: ALWAYS dispose
mesh.geometry.dispose()
mesh.material.dispose()

// Update uniforms
material.uniforms.time.value = clock.getElapsedTime()

// Instance multiple objects
const instances = new InstancedMesh(geometry, material, 1000)
```

### Troubleshooting

**Problem**: Memory usage keeps increasing
**Solution**: Check that all geometries/materials are disposed on unmount

**Problem**: Frame rate drops below 60fps
**Solution**: Use instancing, implement LOD, reduce draw calls

**Problem**: Browser freezes on color input
**Solution**: Validate color input before passing to `new Color()`

**Problem**: Components not updating reactively
**Solution**: Use `shallowRef()` for Three.js objects, not `ref()`

---

## 13. Summary

Three.js/TresJS provides powerful 3D rendering for the JARVIS HUD:

1. **Security**: Validate all inputs, especially colors to prevent ReDoS
2. **Memory**: Always dispose resources on component unmount
3. **Performance**: Use instancing, avoid allocations in render loop
4. **Integration**: TresJS provides seamless Vue 3 reactivity

**Remember**: WebGL has direct GPU access - always validate inputs and manage resources carefully. Test thoroughly before deployment.
