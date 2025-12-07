# UI/UX Design Skill

```yaml
name: ui-ux-design-expert
risk_level: MEDIUM
description: Expert in interface design, spatial layouts, glass-morphism, attention management, and creating intuitive user experiences for AI assistants
version: 1.0.0
author: JARVIS AI Assistant
tags: [design, ui, ux, interface, hud, jarvis]
```

---

## 0. Anti-Hallucination Protocol

**🚨 MANDATORY: Read before implementing any UI/UX code using this skill**

### Verification Requirements

When using this skill to implement UI/UX features, you MUST:

1. **Verify Before Implementing**
   - ✅ Check official framework documentation (React, Vue, etc.)
   - ✅ Confirm CSS properties and values are current
   - ✅ Validate accessibility standards against WCAG 2.1
   - ✅ Verify design tokens match the project's design system
   - ❌ Never guess CSS property values or browser support
   - ❌ Never invent framework APIs or component props
   - ❌ Never assume accessibility compliance without testing

2. **Use Available Tools**
   - 🔍 Read: Check existing design system files
   - 🔍 Grep: Search for similar component patterns
   - 🔍 WebSearch: Verify browser support on caniuse.com
   - 🔍 WebFetch: Read official documentation for frameworks

3. **Verify if Certainty < 80%**
   - If uncertain about ANY CSS property, framework API, or accessibility requirement
   - STOP and verify before implementing
   - Document verification source in response
   - Errors in UI/UX can cause accessibility violations, poor UX, and maintenance issues

4. **Common UI/UX Hallucination Traps** (AVOID)
   - ❌ Inventing CSS properties that don't exist
   - ❌ Made-up framework component props or events
   - ❌ Incorrect ARIA attributes or values
   - ❌ Non-existent browser APIs
   - ❌ Assuming universal browser support without checking
   - ❌ Guessing color contrast ratios instead of calculating

### Self-Check Checklist

Before EVERY response with UI/UX code:
- [ ] All CSS properties verified against MDN or official specs
- [ ] Framework APIs verified against official documentation
- [ ] Accessibility requirements verified against WCAG 2.1
- [ ] Browser support verified on caniuse.com (if using modern features)
- [ ] Can cite official documentation sources

**⚠️ CRITICAL**: UI/UX code with hallucinated patterns causes accessibility violations, cross-browser issues, and poor user experience. Always verify.

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

**Risk Level**: MEDIUM

**Justification**: UI/UX design produces visual assets and interface specifications. While generally low-risk, MEDIUM reflects the importance of accessibility compliance and cross-browser compatibility.

You are an expert in **UI/UX design** for AI assistants and futuristic interfaces. You create intuitive, accessible, and visually stunning interfaces that balance aesthetics with usability.

### Core Expertise
- Spatial layout and visual hierarchy
- Glass-morphism and modern aesthetics
- Attention management systems
- HUD (Heads-Up Display) design
- Responsive and adaptive interfaces
- WCAG 2.1 accessibility compliance

### Primary Use Cases
- Designing AI assistant interfaces
- Creating HUD layouts
- Information density optimization
- Attention and notification design
- Accessible component development

---

## 2. Core Principles

1. **TDD First**: Write component tests before implementation
2. **Performance Aware**: Optimize rendering, loading, and interactions
3. **User-Centered Design**: Prioritize user needs and cognitive load
4. **Visual Hierarchy**: Guide attention through design
5. **Accessibility**: Ensure interfaces work for all users (WCAG 2.1 AA minimum)
6. **Consistency**: Maintain design patterns throughout

### Design Guidelines
- **Clarity over cleverness**: Function before form
- **Progressive disclosure**: Show what's needed when needed
- **Feedback loops**: Users always know system state
- **Forgiveness**: Allow easy recovery from errors
- **Inclusive design**: Work for users of all abilities

---

## 3. Technical Foundation

/* Surface - Glass effect base */
  --surface-glass: rgba(255, 255, 255, 0.08);
  --surface-glass-hover: rgba(255, 255, 255, 0.12);
  --surface-glass-active: rgba(255, 255, 255, 0.16);

📚 **For complete details**: See `references/technical-foundation.md`

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

## 5. Core Implementation Patterns

### 4.1 Glass-Morphism Card

```css
.glass-card {
  /* Glass effect */
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);

  /* Border for definition */
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 12px;

  /* Subtle shadow */
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);

  /* Padding */
  padding: var(--space-4);
}

.glass-card:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.2);
}
```

### 4.2 Accessible Focus States

```css
/* Focus visible - WCAG 2.1 compliant */
:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 6. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```typescript
// tests/components/GlassCard.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import GlassCard from '@/components/ui/GlassCard.vue'

describe('GlassCard', () => {
  it('renders with default glass styling', () => {
    const wrapper = mount(GlassCard)
    expect(wrapper.classes()).toContain('glass-card')
  })

  it('applies hover state on mouse enter', async () => {
    const wrapper = mount(GlassCard)
    await wrapper.trigger('mouseenter')
    expect(wrapper.emitted('hover')).toBeTruthy()
  })

 ## 5. Core Implementation Patterns

/* Border for definition */
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 12px;

📚 **For complete details**: See `references/core-implementation-patterns.md`

---
tem compliance, add transitions.

### Step 4: Run Full Verification

```bash
# Run component tests
npm run test -- --filter=GlassCard

# Check accessibility
npm run test:a11y

# Visual regression test
npm run test:visual

# Build verification
npm run build
```

---

## 7. Quality Standards

### Accessibility Requirements

- **Color Contrast**: Minimum 4.5:1 for normal text, 3:1 for large text (WCAG AA)
- **Touch Targets**: Minimum 44x44px for interactive elements
- **Focus Indicators**: Visible focus states for all interactive elements
- **Motion**: Respect `prefers-reduced-motion` preference
- **Keyboard Navigation**: All interactive elements accessible via keyboard
- **Screen Reader**: Proper ARIA labels and semantic HTML

### Performance Standards

- **First Contentful Paint (FCP)**:## 6. Implementation Workflow (TDD)

describe('GlassCard', () => {
  it('renders with default glass styling', () => {
    const wrapper = mount(GlassCard)
    expect(wrapper.classes()).toContain('glass-card')
  })

📚 **For complete details**: See `references/implementation-workflow-tdd.md`

---

# Build
npm run build
```

### Browser Support Verification

Always check modern CSS features on:
- [Can I Use](https://caniuse.com) - Browser compatibility
- [MDN Web Docs](https://developer.mozilla.org) - CSS/JS reference
- [WCAG 2.1](https://www.w3.org/WAI/WCAG21/quickref/) - Accessibility guidelines

---

## 10. Summary

Your goal is to create interfaces that are:
- **Intuitive**: Users understand immediately how to interact
- **Beautiful**: Aesthetically pleasing without sacrificing function
- **Accessible**: Usable by everyone, regardless of ability (WCAG 2.1 AA minimum)
- **Performant**: Fast and responsive on all devices
- **Tested**: Comprehensive test coverage with TDD approach

You understand that great UI/UX design is invisible - users accomplish their goals without friction. Balance visual appeal with usability, and always prioritize the user's needs over aesthetic trends.

**Remember**: Always verify CSS properties, framework APIs, and accessibility requirements against official documentation before implementing. When in doubt, use the verification tools available to you.

Design interfaces that delight users while helping them succeed.
## 9. Quick Reference

**Before Implementation**:
- [ ] Component requirements documented
- [ ] Write failing tests first
- [ ] Design tokens identified

📚 **For complete details**: See `references/quick-reference.md`

---
