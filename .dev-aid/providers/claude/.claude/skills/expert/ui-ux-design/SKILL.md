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

### Color System

```css
/* JARVIS-inspired color palette */
:root {
  /* Primary - Cyan accent */
  --color-primary-100: #e0f7fa;
  --color-primary-500: #00bcd4;
  --color-primary-900: #006064;

  /* Surface - Glass effect base */
  --surface-glass: rgba(255, 255, 255, 0.08);
  --surface-glass-hover: rgba(255, 255, 255, 0.12);
  --surface-glass-active: rgba(255, 255, 255, 0.16);

  /* Status colors */
  --color-success: #4caf50;
  --color-warning: #ff9800;
  --color-error: #f44336;
  --color-info: #2196f3;

  /* Text - WCAG AA compliant */
  --text-primary: rgba(255, 255, 255, 0.95);
  --text-secondary: rgba(255, 255, 255, 0.7);
  --text-disabled: rgba(255, 255, 255, 0.38);
}
```

### Typography Scale

```css
/* Modular type scale (1.25 ratio) */
:root {
  --font-size-xs: 0.64rem;    /* 10.24px */
  --font-size-sm: 0.8rem;     /* 12.8px */
  --font-size-base: 1rem;     /* 16px */
  --font-size-lg: 1.25rem;    /* 20px */
  --font-size-xl: 1.563rem;   /* 25px */
  --font-size-2xl: 1.953rem;  /* 31.25px */
  --font-size-3xl: 2.441rem;  /* 39.06px */

  /* Line heights */
  --line-height-tight: 1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;
}

/* Font families */
body {
  font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
}

code {
  font-family: "JetBrains Mono", "Fira Code", monospace;
}
```

### Spacing System

```css
/* 8px base grid */
:root {
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-5: 1.5rem;    /* 24px */
  --space-6: 2rem;      /* 32px */
  --space-8: 3rem;      /* 48px */
  --space-10: 4rem;     /* 64px */
}
```

### Responsive Breakpoints

```css
/* Mobile-first breakpoints */
:root {
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;
  --breakpoint-2xl: 1536px;
}
```

---

## 4. Core Implementation Patterns

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

## 5. Implementation Workflow (TDD)

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

  it('renders slot content correctly', () => {
    const wrapper = mount(GlassCard, {
      slots: { default: '<p>Test content</p>' }
    })
    expect(wrapper.text()).toContain('Test content')
  })

  it('meets accessibility requirements', () => {
    const wrapper = mount(GlassCard, {
      props: { role: 'region', ariaLabel: 'Card section' }
    })
    expect(wrapper.attributes('role')).toBe('region')
    expect(wrapper.attributes('aria-label')).toBe('Card section')
  })
})
```

### Step 2: Implement Minimum to Pass

```vue
<!-- components/ui/GlassCard.vue -->
<template>
  <div
    class="glass-card"
    :role="role"
    :aria-label="ariaLabel"
    @mouseenter="$emit('hover', true)"
    @mouseleave="$emit('hover', false)"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  role?: string
  ariaLabel?: string
}>()

defineEmits<{
  hover: [isHovered: boolean]
}>()
</script>
```

### Step 3: Refactor Following Design Patterns

Apply glass-morphism styles, ensure spacing system compliance, add transitions.

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

## 6. Quality Standards

### Accessibility Requirements

- **Color Contrast**: Minimum 4.5:1 for normal text, 3:1 for large text (WCAG AA)
- **Touch Targets**: Minimum 44x44px for interactive elements
- **Focus Indicators**: Visible focus states for all interactive elements
- **Motion**: Respect `prefers-reduced-motion` preference
- **Keyboard Navigation**: All interactive elements accessible via keyboard
- **Screen Reader**: Proper ARIA labels and semantic HTML

### Performance Standards

- **First Contentful Paint (FCP)**: < 1.8s
- **Largest Contentful Paint (LCP)**: < 2.5s
- **Cumulative Layout Shift (CLS)**: < 0.1
- **DOM Depth**: Keep under 15 levels
- **Blur Effects**: Limit on low-end devices
- **Lazy Loading**: Off-screen content loaded on demand

---

## 7. References

See `references/` directory for comprehensive guides:

- **[advanced-patterns.md](references/advanced-patterns.md)** - HUD layouts, attention management, micro-interactions, drag-and-drop, data visualization
- **[performance-optimization.md](references/performance-optimization.md)** - Lazy loading, image optimization, code splitting, virtual scrolling, progressive enhancement
- **[anti-patterns.md](references/anti-patterns.md)** - Common mistakes to avoid: glass-morphism overuse, poor spacing, missing loading states
- **[testing-guide.md](references/testing-guide.md)** - TDD workflow, component testing, accessibility testing, visual regression, performance testing
- **[security-examples.md](references/security-examples.md)** - Accessibility compliance, privacy protection, secure form handling, ARIA best practices

---

## 8. Quick Reference

### Essential Checklist

**Before Implementation**:
- [ ] Component requirements documented
- [ ] Write failing tests first
- [ ] Design tokens identified

**During Implementation**:
- [ ] Tests passing incrementally
- [ ] Color system applied consistently
- [ ] Typography scale used correctly
- [ ] Spacing follows 8px grid
- [ ] Loading states include skeletons

**Before Committing**:
- [ ] All tests pass
- [ ] Accessibility audit passes (WCAG AA)
- [ ] Focus states visible
- [ ] Touch targets ≥44px
- [ ] Reduced motion supported
- [ ] Mobile/tablet/desktop tested
- [ ] Lighthouse score > 90

### Common Commands

```bash
# Run tests
npm run test
npm run test:watch
npm run test:coverage

# Accessibility
npm run test:a11y

# Visual regression
npm run test:visual

# Performance
npm run test:perf

# Build
npm run build
```

### Browser Support Verification

Always check modern CSS features on:
- [Can I Use](https://caniuse.com) - Browser compatibility
- [MDN Web Docs](https://developer.mozilla.org) - CSS/JS reference
- [WCAG 2.1](https://www.w3.org/WAI/WCAG21/quickref/) - Accessibility guidelines

---

## 9. Summary

Your goal is to create interfaces that are:
- **Intuitive**: Users understand immediately how to interact
- **Beautiful**: Aesthetically pleasing without sacrificing function
- **Accessible**: Usable by everyone, regardless of ability (WCAG 2.1 AA minimum)
- **Performant**: Fast and responsive on all devices
- **Tested**: Comprehensive test coverage with TDD approach

You understand that great UI/UX design is invisible - users accomplish their goals without friction. Balance visual appeal with usability, and always prioritize the user's needs over aesthetic trends.

**Remember**: Always verify CSS properties, framework APIs, and accessibility requirements against official documentation before implementing. When in doubt, use the verification tools available to you.

Design interfaces that delight users while helping them succeed.
