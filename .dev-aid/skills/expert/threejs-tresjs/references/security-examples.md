# Three.js/TresJS Security Examples

## Security Standards

### Known Vulnerabilities

| CVE | Severity | Description | Mitigation |
|-----|----------|-------------|------------|
| CVE-2020-28496 | HIGH | ReDoS in color parsing | Update to 0.125.0+, validate colors |
| CVE-2022-0177 | MEDIUM | XSS in docs | Update to 0.137.0+ |

### OWASP Top 10 Coverage

| OWASP Category | Risk | Mitigation |
|----------------|------|------------|
| A05 Injection | MEDIUM | Validate all color/text inputs |
| A06 Vulnerable Components | HIGH | Keep Three.js updated |

### Recommended Versions

| Package | Version | Security Notes |
|---------|---------|----------------|
| three | ^0.160.0+ | Latest stable, fixes CVE-2020-28496 ReDoS |
| @tresjs/core | ^4.0.0 | Vue 3 integration |
| @tresjs/cientos | ^3.0.0 | Component library |
| postprocessing | ^6.0.0 | Effects library |

**Note**: Versions before 0.137.0 have XSS vulnerabilities, before 0.125.0 have ReDoS vulnerabilities.

---

## ReDoS Prevention

### Safe Color Input

```typescript
// Regex that caused ReDoS in Three.js < 0.125.0
// was in Color.setStyle() for rgb/hsl parsing

// ✅ Safe color validation
const COLOR_PATTERNS = {
  hex3: /^#[0-9a-fA-F]{3}$/,
  hex6: /^#[0-9a-fA-F]{6}$/,
  rgb: /^rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)$/,
  hsl: /^hsl\(\s*(\d{1,3})\s*,\s*(\d{1,3})%\s*,\s*(\d{1,3})%\s*\)$/
}

export function validateColorInput(input: string): boolean {
  return Object.values(COLOR_PATTERNS).some(pattern => pattern.test(input))
}

export function safeColorFromString(input: string, fallback = '#00ff41'): Color {
  if (!validateColorInput(input)) {
    console.warn(`Invalid color: ${input}, using fallback`)
    return new Color(fallback)
  }
  return new Color(input)
}
```

## Memory Leak Prevention

### Complete Disposal Pattern

```typescript
export function disposeObject(object: Object3D): void {
  object.traverse((child) => {
    if (child instanceof Mesh) {
      // Dispose geometry
      child.geometry.dispose()

      // Dispose materials
      const materials = Array.isArray(child.material)
        ? child.material
        : [child.material]

      materials.forEach((material) => {
        // Dispose textures
        Object.values(material).forEach((value) => {
          if (value instanceof Texture) {
            value.dispose()
          }
        })
        material.dispose()
      })
    }
  })
}
```

## Frame Rate Protection

### GPU Timeout Detection

```typescript
export function useGPUTimeout(maxFrameTime = 100) {
  let lastFrameTime = performance.now()
  let consecutiveLongFrames = 0

  return {
    checkFrame(): boolean {
      const now = performance.now()
      const frameTime = now - lastFrameTime
      lastFrameTime = now

      if (frameTime > maxFrameTime) {
        consecutiveLongFrames++
        if (consecutiveLongFrames > 5) {
          console.error('GPU performance issue detected')
          return false
        }
      } else {
        consecutiveLongFrames = 0
      }
      return true
    }
  }
}
```

---

## GPU Resource Protection

```typescript
// composables/useResourceLimit.ts
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

---

## Security Checklist

### Pre-Deployment Security Verification

- [ ] Three.js version >= 0.137.0 (XSS fix)
- [ ] All color inputs validated before parsing
- [ ] No user input directly to `new Color()`
- [ ] Resource limits enforced
- [ ] All geometries/materials disposed on unmount
- [ ] No unvalidated text rendering
- [ ] WebGL context error handling implemented
- [ ] GPU resource monitoring active
