---
name: gsap
description: GSAP animations for JARVIS HUD transitions and effects
risk_level: LOW
version: 1.0.0
---

# GSAP Animation Skill

> **File Organization**: This skill uses split structure. See `references/` for detailed patterns and examples.

## 0. Anti-Hallucination Protocol

**🚨 MANDATORY: Read before implementing any GSAP animations**

### Verification Requirements

When using this skill to implement GSAP animations, you MUST:

1. **Verify Before Implementing**
   - ✅ Check official GSAP documentation for API methods
   - ✅ Confirm plugin availability (ScrollTrigger, Flip, etc.)
   - ✅ Validate easing functions exist in current version
   - ❌ Never guess animation property names
   - ❌ Never invent GSAP methods or plugins
   - ❌ Never assume ScrollTrigger methods without checking

2. **Use Available Tools**
   - 🔍 Read: Check existing codebase for GSAP patterns
   - 🔍 Grep: Search for similar animation implementations
   - 🔍 WebSearch: Verify API in official GSAP docs
   - 🔍 WebFetch: Read official GSAP documentation

3. **Verify if Certainty < 80%**
   - If uncertain about ANY GSAP method/property/plugin
   - STOP and verify before implementing
   - Document verification source in response
   - Errors in animations can cause UI freezes, memory leaks, accessibility issues

4. **Common GSAP Hallucination Traps** (AVOID)
   - ❌ Inventing easing function names (use official eases only)
   - ❌ Made-up ScrollTrigger properties
   - ❌ Non-existent timeline methods
   - ❌ Incorrect plugin registration syntax
   - ❌ Assuming all properties are animatable

### Self-Check Checklist

Before EVERY response with GSAP code:
- [ ] All GSAP methods verified against official docs
- [ ] Plugin imports verified (ScrollTrigger, Flip, etc.)
- [ ] Easing functions verified against GSAP ease list
- [ ] Can cite official documentation sources

**⚠️ CRITICAL**: GSAP code with hallucinated methods causes runtime errors and broken animations. Always verify.

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

This skill provides GSAP (GreenSock Animation Platform) expertise for creating smooth, professional animations in the JARVIS AI Assistant HUD.

**Risk Level**: LOW - Animation library with minimal security surface

**Primary Use Cases**:
- HUD panel entrance/exit animations
- Status indicator transitions
- Data visualization animations
- Scroll-triggered effects
- Complex timeline sequences

## 2. Core Responsibilities

### 2.1 Fundamental Principles

1. **TDD First**: Write animation tests before implementation
2. **Performance Aware**: Use transforms/opacity for GPU acceleration, avoid layout thrashing
3. **Cleanup Required**: Always kill animations on component unmount
4. **Timeline Organization**: Use timelines for complex sequences
5. **Easing Selection**: Choose appropriate easing for HUD feel
6. **Accessibility**: Respect reduced motion preferences
7. **Memory Management**: Avoid memory leaks with proper cleanup

## 2.5 Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```typescript
// tests/animations/panel-animation.test.ts
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { gsap } from 'gsap'
import HUDPanel from '~/components/HUDPanel.vue'

describe('HUDPanel Animation', () => {
  beforeEach(() => {
    // Mock reduced motion
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: vi.fn().mockImplementation(query => ({
        matches: false,
        media: query
      }))
    })
  })

  afterEach(() => {
    gsap.globalTimeline.clear()
  })

  it('animates panel entrance with correct properties', async () => {
    const wrapper = mount(HUDPanel)
    await new Promise(resolve => setTimeout(resolve, 600))

    const panel = wrapper.find('.hud-panel')
    expect(panel.exists()).toBe(true)
  })

  it('cleans up animations on unmount', async () => {
    const wrapper = mount(HUDPanel)
    const childCount = gsap.globalTimeline.getChildren().length

    await wrapper.unmount()

    expect(gsap.globalTimeline.getChildren().length).toBeLessThan(childCount)
  })

  it('respects reduced motion preference', async () => {
    window.matchMedia = vi.fn().mockImplementation(() => ({
      matches: true
    }))

    const wrapper = mount(HUDPanel)
    const panel = wrapper.find('.hud-panel').element

    expect(gsap.getProperty(panel, 'opacity')).toBe(1)
  })
})
```

### Step 2: Implement Minimum to Pass

```typescript
// components/HUDPanel.vue
const animation = ref<gsap.core.Tween | null>(null)

onMounted(() => {
  if (!panelRef.value) return

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    gsap.set(panelRef.value, { opacity: 1 })
    return
  }

  animation.value = gsap.from(panelRef.value, {
    opacity: 0,
    y: 20,
    duration: 0.5
  })
})

onUnmounted(() => {
  animation.value?.kill()
})
```

### Step 3: Refactor Following Patterns

```typescript
// Extract to composable for reusability
export function usePanelAnimation(elementRef: Ref<HTMLElement | null>) {
  const animation = ref<gsap.core.Tween | null>(null)

  const animate = () => {
    if (!elementRef.value) return

    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      gsap.set(elementRef.value, { opacity: 1 })
      return
    }

    animation.value = gsap.from(elementRef.value, {
      opacity: 0,
      y: 20,
      duration: 0.5,
      ease: 'power2.out'
    })
  }

  onMounted(animate)
  onUnmounted(() => animation.value?.kill())

  return { animation }
}
```

### Step 4: Run Full Verification

```bash
# Run animation tests
npm test -- --grep "Animation"

# Check for memory leaks
npm run test:memory

# Verify 60fps performance
npm run test:performance
```

## 3. Technology Stack & Versions

### 3.1 Recommended Versions

| Package | Version | Notes |
|---------|---------|-------|
| gsap | ^3.12.0 | Core library |
| @gsap/vue | ^3.12.0 | Vue integration |
| ScrollTrigger | included | Scroll effects |

### 3.2 Vue Integration

```typescript
// plugins/gsap.ts
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

export default defineNuxtPlugin(() => {
  gsap.registerPlugin(ScrollTrigger)

  return {
    provide: {
      gsap,
      ScrollTrigger
    }
  }
})
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

**See `references/animation-patterns.md` for detailed implementations**

Common patterns include:
- **Panel Entrance**: Fade in with slide up animation
- **Status Indicator**: Scale pulse and color transitions
- **Data Visualization**: Staggered bar chart animations
- **Timeline Sequences**: Multi-step HUD startup sequences
- **Scroll-Triggered**: Elements animate on scroll into view

### Quick Example: Simple Panel Animation

```vue
<script setup lang="ts">
import { gsap } from 'gsap'
import { onMounted, onUnmounted, ref } from 'vue'

const panelRef = ref<HTMLElement | null>(null)
let animation: gsap.core.Tween | null = null

onMounted(() => {
  if (!panelRef.value) return

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    gsap.set(panelRef.value, { opacity: 1 })
    return
  }

  animation = gsap.from(panelRef.value, {
    opacity: 0,
    y: 20,
    scale: 0.95,
    duration: 0.5,
    ease: 'power2.out'
  })
})

onUnmounted(() => {
  animation?.kill()
})
</script>

<template>
  <div ref="panelRef" class="hud-panel">
    <slot />
  </div>
</template>
```

## 6. Quality Standards

### 5.1 Performance

```typescript
// ✅ GOOD - Use transforms for GPU acceleration
gsap.to(element, {
  x: 100,
  y: 50,
  rotation: 45,
  scale: 1.2
})

// ❌ BAD - Triggers layout recalculation
gsap.to(element, {
  left: 100,
  top: 50,
  width: '120%'
})
```

### 5.2 Accessibility

```typescript
// ✅ Respect reduced motion
const prefersReducedMotion = window.matchMedia(
  '(prefers-reduced-motion: reduce)'
).matches

if (prefersReducedMotion) {
  gsap.set(element, { opacity: 1 })
} else {
  gsap.from(element, { opacity: 0, duration: 0.5 })
}
```

## 7. Performance Optimization

**See `references/performance-optimization.md` for detailed strategies**

Key optimizations:
- **will-change**: Apply before animation, remove after
- **Transform Properties**: Use x/y instead of left/top
- **Timeline Reuse**: Create once, play/reverse multiple times
- **ScrollTrigger Batching**: Batch similar scroll animations
- **Lazy Initialization**: Only create animations when needed
- **QuickSetter**: For high-frequency updates (mouse tracking)

## 8. Testing & Quality

**See `references/testing-guide.md` for comprehensive testing examples**

Essential tests:
- Animation executes with correct properties
- Cleanup on unmount (no memory leaks)
- Reduced motion preference respected
- Timeline sequences execute in order
- ScrollTrigger instances properly destroyed

## 9. Common Mistakes & Anti-Patterns

**See `references/anti-patterns.md` for detailed examples**

Critical anti-patterns to avoid:
- ❌ **Skip Cleanup**: Always kill animations on unmount
- ❌ **Animate Layout Properties**: Use transforms instead
- ❌ **Ignore Reduced Motion**: Check user preference
- ❌ **No Animation Tracking**: Store references for cleanup

## 14. Pre-Implementation Checklist

### Phase 1: Before Writing Code

- [ ] Write failing tests for animation behavior
- [ ] Define animation timing and easing requirements
- [ ] Identify elements that need will-change hints
- [ ] Plan cleanup strategy for all animations
- [ ] Check if reduced motion support is needed

### Phase 2: During Implementation

- [ ] Use transforms/opacity only (no layout properties)
- [ ] Store animation references for cleanup
- [ ] Apply will-change before, remove after animation
- [ ] Use timelines for sequences
- [ ] Batch ScrollTrigger animations
- [ ] Implement lazy initialization for complex animations

### Phase 3: Before Committing

- [ ] All tests pass (npm test -- --grep "Animation")
- [ ] All animations cleaned up on unmount
- [ ] Reduced motion preference respected
- [ ] No memory leaks (check with DevTools)
- [ ] 60fps maintained (test with performance monitor)
- [ ] ScrollTrigger instances properly killed

## 15. Summary

GSAP provides professional animations for JARVIS HUD:

1. **Cleanup**: Always kill animations on unmount
2. **Performance**: Use transforms and opacity only
3. **Accessibility**: Respect reduced motion preference
4. **Organization**: Use timelines for sequences

**Remember**: Every animation must be cleaned up to prevent memory leaks.

---

## References

**Core Documentation**:
- `references/animation-patterns.md` - Detailed implementation patterns with examples
- `references/performance-optimization.md` - Performance strategies and best practices
- `references/testing-guide.md` - Comprehensive testing examples and utilities
- `references/anti-patterns.md` - Common mistakes and how to avoid them
- `references/advanced-patterns.md` - Complex animation patterns and techniques

**Official Resources**:
- [GSAP Documentation](https://greensock.com/docs/)
- [GSAP Ease Visualizer](https://greensock.com/ease-visualizer/)
- [ScrollTrigger Documentation](https://greensock.com/docs/v3/Plugins/ScrollTrigger)
