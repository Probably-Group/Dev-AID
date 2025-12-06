# Motion Design Skill

```yaml
name: motion-design-expert
risk_level: LOW
description: Expert in HUD animations, timing tokens, spring physics, reduced motion support, and creating purposeful interface animations
version: 1.0.0
author: JARVIS AI Assistant
tags: [design, animation, motion, transitions, hud]
```

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

## 0. Anti-Hallucination Protocol

## 0. Anti-Hallucination Protocol

### 0.1 Quick Risk Assessment

**Risk Level**: LOW

**Key Risk Factors**:
- Security concerns in low-risk domain
- 3 security issues/patterns identified
- Common attack vectors: SVG XSS, Animation DoS, Canvas manipulation
- Requires security awareness and best practices

**Immediate Security Actions**:
1. Review security concerns below before any implementation
2. Never proceed without understanding attack surface
3. Implement security controls from § 0.3 as mandatory requirements

### 0.3 Hallucination Prevention Checklist

**CRITICAL**: These rules are ABSOLUTE. Violation = security incident.

**Domain-Specific Security Rules**:

- ❌ NEVER use unsanitized SVG
- ❌ NEVER create infinite animations
- ❌ ALWAYS validate animation data

**Before ANY code generation**:
1. ✅ Verify rule compliance for proposed implementation
2. ✅ Check if solution introduces any prohibited patterns
3. ✅ Validate all security assumptions
4. ✅ Confirm defensive coding practices are applied

**If uncertain**: STOP and research. Never guess on security.


## 1. Overview

**Risk Level**: LOW-RISK

**Justification**: Motion design produces animation specifications and CSS/JS without direct code execution or data processing.

You are an expert in **motion design** for interfaces. You create purposeful animations that enhance usability, provide feedback, and create delightful experiences while respecting accessibility needs.

### Core Expertise
- Timing and easing functions
- Spring physics animations
- Micro-interactions
- State transitions
- Reduced motion support

### Primary Use Cases
- HUD interface animations
- Loading and progress indicators
- State change transitions
- Attention-drawing effects

---

## 2. Core Principles

1. **TDD First**: Write animation tests before implementation
2. **Performance Aware**: Target 60fps, use GPU-accelerated properties only
3. **Purposeful Motion**: Every animation serves a function
4. **Accessibility**: Support reduced motion preferences
5. **Consistency**: Use standardized timing tokens

### Motion Guidelines
- **Inform hierarchy**: Motion shows relationships
- **Provide feedback**: Users know actions registered
- **Guide attention**: Direct focus appropriately
- **Maintain context**: Preserve spatial understanding

---

## 3. Technical Foundation

### Timing Tokens

```css
:root {
  /* Duration scale */
  --duration-instant: 0ms;
  --duration-fast: 100ms;
  --duration-normal: 200ms;
  --duration-slow: 300ms;
  --duration-slower: 500ms;

  /* Easing functions */
  --ease-in: cubic-bezier(0.4, 0, 1, 1);
  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);

  /* Spring-like easing */
  --ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
  --ease-spring: cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
```

### Usage Guidelines

| Animation Type | Duration | Easing |
|----------------|----------|--------|
| Micro-interaction | 100-200ms | ease-out |
| State change | 200-300ms | ease-in-out |
| Enter/reveal | 300-500ms | ease-out |
| Exit/hide | 200-300ms | ease-in |
| Complex choreography | 500-800ms | custom |

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

## 5. Implementation Patterns

/* Usage */
.element-enter {
  animation: slideUpFadeIn var(--duration-normal) var(--ease-out) forwards;
}
```

📚 **For complete details**: See `references/implementation-patterns.md`

---
## 6. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```typescript
// tests/animations/modal.test.ts
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import AnimatedModal from '~/components/AnimatedModal.vue'

describe('AnimatedModal', () => {
  it('applies enter animation classes on mount', async () => {
    const wrapper = mount(AnimatedModal, {
      props: { isOpen: true }
    })

    expect(wrapper.classes()).toContain('modal-enter-active')
  })

  it('respects reduced motion preference', async () => {
    // Mock matchMedia
    window.matchMedia = vi.fn().mockImplementation(query => ({
      matches: query === '(prefers-reduced-motion: reduce)',
      addEventListener: vi.fn(),
      removeEventListener: vi.fn()
    }))

    const wrapper = mount(AnimatedModal, {
      props: { isOpen: true }
    })

    expect(wrapper.classes()).toContain('reduced-motion')
  })

  it('completes animation within duration threshold', async () => {
    const wrapper = mount(AnimatedModal, {
      props: { isOpen: true }
    })

    const style = getComputedStyle(wrapper.element)
    const duration = parseFloat(style.animationDuration) * 1000

    expect(duration).toBeLessThanOrEqual(300) // Max 300ms for modals
  })
})
```

### Step 2: Implement Minimum to Pass

```vue
<template>
  <Transition name="modal">
    <div
      v-if="isOpen"
   ## 6. Implementation Workflow (TDD)

describe('AnimatedModal', () => {
  it('applies enter animation classes on mount', async () => {
    const wrapper = mount(AnimatedModal, {
      props: { isOpen: true }
    })

📚 **For complete details**: See `references/implementation-workflow-tdd.md`

---
m: 'translateY(20px)', opacity: 0 },
    { transform: 'translateY(0)', opacity: 1 }
  ], { duration: 300 })
}

/* GOOD: Respect preference with fallback */
function animateElement(el: HTMLElement) {
  const prefersReduced = window.matchMedia(
    '(prefers-reduced-motion: reduce)'
  ).matches

  if (prefersReduced) {
    el.style.opacity = '1'
    return
  }

  el.animate([
    { transform: 'translateY(20px)', opacity: 0 },
    { transform: 'translateY(0)', opacity: 1 }
  ], { duration: 300 })
}
```

### Pattern 5: Animation Batching

```typescript
/* BAD: Multiple reflows */
function animateItems(items: HTMLElement[]) {
  items.forEach((item, i) => {
    item.style.transform = `translateY(${i * 10}px)`
    item.style.opacity = '0'
  })
}

/* GOOD: Batch reads and writes */
function animateItems(items: HTMLElement[]) {
  // Read phase - batch all measurements
  const positions = items.map(item => item.getBoundingClientRect())

  // Write phase - batch all mutations
  requestAnimationFrame(() => {
    items.forEach((item, i) => {
      item.style.transform = `translateY(${i * 10}px)`
      item.style.opacity = '0'
    })
  })
}

/* GOOD: Use Web Animations API for batching */
function animateItems(items: HTMLElement[]) {
  const animations = items.map((item, i) =>
    item.animate([
      { transform: 'translateY(0)', opacity: 0 },
      { transform: 'translateY(0)', opacity: 1 }
    ], {
      duration: 300,
      delay: i * 50,
      fill: 'forwards'
    })
  )

  return Promise.all(animations.map(a => a.finished))
}
```

---

## 8. Quality Standards

### Performance Requirements
- Target 60fps (16.67ms per frame)
- Use `transform` and `opacity` for animations
- Avoid animating `width`, `height`, `margin`, `padding`
- Use `will-change` sparingly

```css
/* ✅ GPU-accelerated properties */
.animated {
  trans## 7. Performance Patterns

/* GOOD: Apply only when animating */
.animated-element:hover,
.animated-element:focus,
.animated-element.is-animating {
  will-change: transform, opacity;
}

📚 **For complete details**: See `references/performance-patterns.md`

---
