---
name: glsl
description: GLSL shader programming for JARVIS holographic effects
risk_level: LOW
version: 1.1.0
---

# GLSL Shader Programming Skill

> **File Organization**: This skill uses split structure. See `references/` for advanced shader patterns.


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

**Risk Level**: LOW

**Key Risk Factors**:
- Security concerns in low-risk domain
- 3 security issues/patterns identified
- Common attack vectors: Shader complexity DoS, GPU memory exhaustion, Timing side-channels
- Requires security awareness and best practices

**Immediate Security Actions**:
1. Review security concerns below before any implementation
2. Never proceed without understanding attack surface
3. Implement security controls from § 0.3 as mandatory requirements

### 0.3 Hallucination Prevention Checklist

**CRITICAL**: These rules are ABSOLUTE. Violation = security incident.

**Domain-Specific Security Rules**:

- ❌ NEVER allow unbounded shader complexity
- ❌ NEVER trust user-supplied shaders
- ❌ ALWAYS implement shader validation

**Before ANY code generation**:
1. ✅ Verify rule compliance for proposed implementation
2. ✅ Check if solution introduces any prohibited patterns
3. ✅ Validate all security assumptions
4. ✅ Confirm defensive coding practices are applied

**If uncertain**: STOP and research. Never guess on security.


## 1. Overview

This skill provides GLSL shader expertise for creating holographic visual effects in the JARVIS AI Assistant HUD. It focuses on efficient GPU programming for real-time rendering.

**Risk Level**: LOW - GPU-side code with limited attack surface, but can cause performance issues

**Primary Use Cases**:
- Holographic panel effects with scanlines
- Animated energy fields and particle systems
- Data visualization with custom rendering
- Post-processing effects (bloom, glitch, chromatic aberration)

## 2. Core Responsibilities

### 2.1 Fundamental Principles

1. **TDD First**: Write visual regression tests and shader unit tests before implementation
2. **Performance Aware**: Profile GPU performance, optimize for 60 FPS target
3. **Precision Matters**: Use appropriate precision qualifiers for performance
4. **Avoid Branching**: Minimize conditionals in shaders for GPU efficiency
5. **Optimize Math**: Use built-in functions, avoid expensive operations
6. **Uniform Safety**: Validate uniform inputs before sending to GPU
7. **Loop Bounds**: Always use constant loop bounds to prevent GPU hangs
8. **Memory Access**: Optimize texture lookups and varying interpolation

## 3. Implementation Workflow (TDD)

describe('HolographicPanelShader', () => {
  let ctx: WebGLTestContext

📚 **For complete details**: See `references/implementation-workflow-tdd.md`

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

## 5. Technology Stack & Versions

### 4.1 GLSL Versions

| Version | Context | Features |
|---------|---------|----------|
| GLSL ES 3.00 | WebGL 2.0 | Modern features, better precision |
| GLSL ES 1.00 | WebGL 1.0 | Legacy support |

### 4.2 Shader Setup

```glsl
#version 300 es
precision highp float;
precision highp int;

// WebGL 2.0 shader header
```

## 6. Performance Patterns

### 5.1 Avoid Branching - Use Mix/Step

```glsl
// ❌ BAD - GPU branch divergence
vec3 getColor(float value) {
  if (value < 0.3) {
    return vec3(1.0, 0.0, 0.0);  // Red
  } else if (value < 0.7) {
    return vec3(1.0, 1.0, 0.0);  // Yellow
  } else {
    return vec3(0.0, 1.0, 0.0);  // Green
  }
}

// ✅ GOOD - Branchless with mix/step
vec3 getColor(float value) {
  vec3 red = vec3(1.0, 0.0, 0.0);
  vec3 yellow = vec3(1.0, 1.0, 0.0);
  vec3 green = vec3(0.0, 1.0, 0.0);

  vec3 color = mix(red, yellow, smoothstep(0.3, 0.31, value));
  color = mix(color, green, smoothstep(0.7, 0.71, value));
  return color;
}
```

### 5.2 Texture Atlases - Reduce Draw Calls

```glsl
// ❌ BAD - Multiple texture bindings
uniform sampler2D uIcon1;
uniform sampler2D uIcon2;
uniform sampler2D uIcon3;

vec4 getIcon(int id) {
  if (id == 0) return texture(uIcon1, vUv);
  if (id == 1) return texture(uIcon2, vUv);
  return texture(uIcon3, vUv);
}

// ✅ GOOD - Single atlas texture
uniform sampler2D uIconAtlas;
uniform vec4 uAtlasOffsets[3];  // [x, y, width, height] for each icon

vec4 getIcon(int id) {
  vec4 offset = uAtlasOffsets[id];
  vec2 atlasUV = offset.xy + vUv * offset.zw;
  return texture(uIconAtlas, atlasUV);
}
```

### 5.3 Level of Detail (LOD) - Distance-Based Quality

```glsl
// ❌ BAD - Same quality regardless of distance
const int NOISE_OCTAVES = 8;

float noise(vec3 p) {
  float result = 0.0;
  for (int i = 0; i < NOISE_OCTAVES; i++) {
    result += snoise(p * pow(2.0, float(i)));
  }
  return result;
}

// ✅ GOOD - Reduce octaves based on distance
uniform float uCameraDistance;

float noise(vec3 p) {
  // Fewer octaves when far away (detail not visible)
  int octaves = int(mix(2.0, 8.0, 1.0 - smoothstep(10.0, 100.0, uCameraDistance)));
  float result = 0.0;
  for (int i = 0; i < 8; i++) {
    if (i >= octaves) break;
    result += snoise(p * pow(2.0, float(i)));
  }
  return result;
}
```

### 5.4 Uniform Batching - Minimize CPU-GPU Transfers

```glsl
// ❌ BAD - Many individual uniforms
uniform float uPosX;
uniform float uPosY;
uniform float uPosZ;
uniform float uRotX;
uniform float uRotY;
uniform float uRotZ;
uniform float uScaleX;
uniform float uScaleY;
uniform float uScaleZ;

// ✅ GOOD - Packed into vectors/matrices
uniform vec3 uPosition;
uniform vec3 uRotation;
uniform vec3 uScale;
// Or even better:
uniform mat4 uTransform;
```

### 5.5 Precision Optimization - Use Appropriate Precision

```glsl
// ❌ BAD - Everything highp (wastes GPU cycles)
precision highp float;

highp vec3 color;
high## 6. Performance Patterns

// ✅ GOOD - Branchless with mix/step
vec3 getColor(float value) {
  vec3 red = vec3(1.0, 0.0, 0.0);
  vec3 yellow = vec3(1.0, 1.0, 0.0);
  vec3 green = vec3(0.0, 1.0, 0.0);

📚 **For complete details**: See `references/performance-patterns.md`

---
nt(uCount)) break;
}
```

## 9. Common Mistakes & Anti-Patterns

### 8.1 Never: Use Dynamic Loop Bounds

```glsl
// ❌ DANGEROUS - May cause GPU hang
for (int i = 0; i < uniformValue; i++) { }

// ✅ SAFE - Constant bound with early exit
const int MAX = 100;
for (int i = 0; i < MAX; i++) {
  if (i >= uniformValue) break;
}
```

### 8.2 Never: Divide Without Checking Zero

```glsl
// ❌ DANGEROUS - Division by zero
float result = value / divisor;

// ✅ SAFE - Guard against zero
float result = value / max(divisor, 0.0001);
```

## 10. Pre-Implementation Checklist

### Phase 1: Before Writing Code

- [ ] Write shader compilation test
- [ ] Write uniform accessibility test
- [ ] Create baseline images for visual regression tests
- [ ] Define performance targets (FPS, draw calls)
- [ ] Review existing shaders for reusable patterns

### Phase 2: During Implementation

- [ ] All loops have constant bounds
- [ ] No division by zero possible
- [ ] Using branchless patterns (mix/step)
- [ ] Appropriate precision qualifiers
- [ ] Texture lookups cached
- [ ] Uniforms batched into vectors/matrices

### Phase 3: Before Committing

- [ ] All shader tests pass: `npm run test:shaders`
- [ ] Visual regression tests pass: `npm run test:visual`
- [ ] Performance benchmark meets targets: `npm run bench:shaders`
- [ ] Cross-browser compatibility verified
- [ ] No artifacts at edge cases (UV 0,0 and 1,1)
- [ ] Smooth animation timing verified

## 11. Summary

GLSL shaders power the visual effects in JARVIS HUD:

1. **TDD First**: Write tests before shaders - compilation, uniforms, visual regression
2. **Performance**: Use branchless patterns, texture atlases, LOD, precision optimization
3. **Safety**: Constant loop bounds, guard divisions
4. **Testing**: Verify across target browsers, benchmark GPU performance

**Remember**: Shaders run on GPU - a single bad shader can freeze the entire system.

---

**References**:
- `references/advanced-patterns.md` - Complex shader techniques
## 7. Implementation Patterns

uniform float uTime;
uniform vec3 uColor;
uniform float uOpacity;
uniform vec2 uResolution;

📚 **For complete details**: See `references/implementation-patterns.md`

---
