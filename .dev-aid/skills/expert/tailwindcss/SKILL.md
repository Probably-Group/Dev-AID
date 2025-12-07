---
name: tailwindcss
description: Tailwind CSS utility-first styling for JARVIS UI components
risk_level: LOW
version: 1.1.0
---

# Tailwind CSS Development Skill

> **File Organization**: This skill uses split structure. See `references/` for advanced patterns.

## 0. Anti-Hallucination Protocol

## 0. Anti-Hallucination Protocol

### 0.1 Quick Risk Assessment

**Risk Level**: LOW

**Key Risk Factors**:
- Active exploitation of critical vulnerabilities in production (CVSS 7.5+)
- 3 high-severity CVEs discovered in 2024-2025
- Common attack vectors: XSS via dynamic arbitrary values, Dependency vulnerabilities, CSS injection attacks
- Requires continuous monitoring of security advisories

**Immediate Security Actions**:
1. Review recent CVEs below before any implementation
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

   - **CVE-2024-4068** (CVSS 7.5): Vulnerability in braces dependency
     Source: https://github.com/tailwindlabs/tailwindcss/issues/14258
   - **CVE-2024-4067** (CVSS 7.5): Vulnerability in micromatch dependency
     Source: https://github.com/tailwindlabs/tailwindcss/issues/14258
   - **ARBITRARY-VALUE-XSS** (CVSS N/A): XSS via unsanitized arbitrary values
     Source: https://dansasser.me/posts/navigating-the-security-risks-of-arbitrary-values-in-tailwind-css/

**Step 3: Common Attack Patterns**

   - XSS via dynamic arbitrary values
   - Dependency vulnerabilities
   - CSS injection attacks

**Step 4: MITRE ATT&CK Mapping**
- Tactic: [Initial Access, Execution, Persistence, Privilege Escalation]
- Review MITRE ATT&CK framework for latest techniques

**Update Frequency**: Check for new CVEs weekly during active development.

### 0.3 Hallucination Prevention Checklist

**CRITICAL**: These rules are ABSOLUTE. Violation = security incident.

**Domain-Specific Security Rules**:

- ❌ NEVER use user input directly in arbitrary values
- ❌ NEVER skip sanitization for dynamic classes
- ❌ ALWAYS use safelist for dynamic classes
- ❌ ALWAYS validate class names

**Before ANY code generation**:
1. ✅ Verify rule compliance for proposed implementation
2. ✅ Check if solution introduces any prohibited patterns
3. ✅ Validate all security assumptions against current CVEs
4. ✅ Confirm defensive coding practices are applied

**If uncertain**: STOP and research. Never guess on security.



**🚨 MANDATORY: Read before implementing any Tailwind CSS code**

### Verification Requirements

When using this skill to implement Tailwind CSS styling, you MUST:

1. **Verify Before Implementing**
   - ✅ Check official Tailwind CSS documentation at tailwindcss.com
   - ✅ Confirm utility classes exist in current version (v3.4+)
   - ✅ Validate configuration options against official guides
   - ❌ Never guess utility class names
   - ❌ Never invent configuration options
   - ❌ Never assume plugin APIs without checking docs

2. **Use Available Tools**
   - 🔍 Read: Check existing components for Tailwind patterns
   - 🔍 Grep: Search codebase for similar styling implementations
   - 🔍 WebSearch: Verify utility classes in official Tailwind docs
   - 🔍 WebFetch: Read official Tailwind CSS documentation

3. **Verify if Certainty < 80%**
   - If uncertain about ANY utility class, configuration, or plugin
   - STOP and verify before implementing
   - Document verification source in response
   - Errors in Tailwind CSS can cause build failures and visual bugs

4. **Common Tailwind CSS Hallucination Traps** (AVOID)
   - ❌ Inventing utility class names that don't exist
   - ❌ Making up configuration options not in Tailwind config
   - ❌ Assuming plugin APIs without checking documentation
   - ❌ Using deprecated classes from older Tailwind versions
   - ❌ Confusing Tailwind utilities with other CSS frameworks

### Self-Check Checklist

Before EVERY response with Tailwind CSS code:
- [ ] All utility classes verified against Tailwind v3.4+ docs
- [ ] Configuration options verified in tailwind.config.js docs
- [ ] Plugin usage verified against official plugin documentation
- [ ] Can cite official Tailwind CSS documentation sources

**⚠️ CRITICAL**: Tailwind CSS code with hallucinated classes causes build failures and visual inconsistencies. Always verify.

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

This skill provides Tailwind CSS expertise for styling the JARVIS AI Assistant interface with utility-first CSS, creating consistent and maintainable HUD designs.

**Risk Level**: LOW - Styling framework with minimal security surface

**Primary Use Cases**:
- Holographic UI panel styling
- Responsive HUD layouts
- Animation utilities for transitions
- Custom JARVIS theme configuration

## 2. Core Responsibilities

### 2.1 Fundamental Principles

1. **TDD First**: Write component tests before styling implementation
2. **Performance Aware**: Optimize CSS output size and rendering performance
3. **Utility-First**: Compose styles from utility classes, extract components when patterns repeat
4. **Design System**: Define JARVIS color palette and spacing in config
5. **Responsive Design**: Mobile-first with breakpoint utilities
6. **Dark Mode Default**: HUD is always dark-themed
7. **Accessibility**: Maintain sufficient contrast ratios

## 3. Implementation Workflow (TDD)

### 3.1 TDD Process for Styled Components

Follow this workflow for every styled component:

#### Step 1: Write Failing Test First

```typescript
// tests/components/HUDPanel.test.ts
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import HUDPanel from '~/components/HUDPanel.vue'

describe('HUDPanel', () => {
  it('renders with correct JARVIS theme classes', () => {
    const wrapper = mount(HUDPanel, {
      props: { title: 'System Status' }
    })

    const panel = wrapper.find('[data-testid="hud-panel"]')
    expect(panel.classes()).toContain('bg-jarvis-bg-panel/80')
    expect(panel.classes()).toContain('border-jarvis-primary/30')
    expect(panel.classes()).toContain('backdrop-blur-sm')
  })

  it('applies responsive grid layout', () => {
    const wrapper = mount(HUDPanel)
    const grid = wrapper.find('[data-testid="panel-grid"]')

    expect(grid.classes()).toContain('grid-cols-1')
    expect(grid.classes()).toContain('md:grid-cols-2')
    expect(grid.classes()).toContain('lg:grid-cols-3')
  })

  it('shows correct status indicator colors', async () => {
    const wrapper = mount(HUDPanel, {
      props: { status: 'active' }
    })

    const indicator = wrapper.find('[data-testid="status-indicator"]')
    expect(indicator.classes()).toContain('bg-jarvis-primary')
    expect(indicator.classes()).toContain('animate-pulse')

    await wrapper.setProps({ status: 'error' })
    expect(indicator.classes()).toContain('bg-jarvis-danger')
  })

  it('maintains accessibility focus styles', () => {
    const wrapper = mount(HUDPanel)
    const button = wrapper.find('button')

    expect(button.classes()).toContain('focus:ring-2')
    expect(button.classes()).toContain('focus:outline-none')
  })
})
```

#### Step 2: Implement Minimum to Pass

```vue
<!-- components/HUDPanel.vue -->
<template>
  <div
    data-testid="hud-panel"
    class="bg-jarvis-bg-panel/80 border border-jarvis-primary/30 backdrop-blur-sm rounded-lg p-4"
  >
    <div
      data-testid="panel-grid"
      class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
    >
      <slot />
    </div>
    <span
      data-testid="status-indicator"
      :class="statusClasses"
    />
    <button class="focus:ring-2 focus:outline-none focus:ring-jarvis-primary">
      Action
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  title?: string
  status?: 'active' | 'warning' | 'error' | 'inactive'
}>()

const statusClasses = computed(() => ({
  'bg-jarvis-primary animate-pulse': props.status === 'active',
  'bg-jarvis-warning': props.status === 'warning',
  'bg-jarvis-danger': props.status === 'error',
  'bg-gray-500': props.status === 'inactive'
}))
</script>
```

#### Step 3: Refactor if Needed

Extract repeated patterns to @apply directives:

```css
/* assets/css/components.css */
@layer components {
  .hud-panel {
    @apply bg-jarvis-bg-panel/80 border border-jarvis-primary/30 backdrop-blur-sm rounded-lg p-4;
  }

  .hud-grid {
    @apply grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4;
  }
}
```

#### Step 4: Run Full Verification

```bash
# Run all style-related tests
npm run test -- --grep "HUDPanel"

# Check for unused CSS
npx tailwindcss --content './components/**/*.vue' --output /dev/null

# Verify build size
npm run build && ls -lh .output/public/_nuxt/*.css
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

## 5. Performance Patterns

For detailed performance optimization strategies, see `references/performance-optimization.md`.

**Key principles**:
- Optimize content paths to exclude non-production files
- Use JIT mode (default in v3+) for on-demand class generation
- Extract patterns with @apply only when they repeat 3+ times
- Follow mobile-first approach with minimal breakpoints
- Use GPU-accelerated properties for animations (transform, opacity)
- Keep CSS bundle under 50KB (gzipped)

## 6. Technology Stack & Versions

### 5.1 Recommended Versions

| Package | Version | Notes |
|---------|---------|-------|
| tailwindcss | ^3.4.0 | Latest with JIT mode |
| @nuxtjs/tailwindcss | ^6.0.0 | Nuxt integration |
| tailwindcss-animate | ^1.0.0 | Animation utilities |

### 5.2 Configuration

```javascript
// tailwind.config.js
export default {
  content: [
    './components/**/*.{vue,js,ts}',
    './layouts/**/*.vue',
    './pages/**/*.vue',
    './composables/**/*.ts',
    './plugins/**/*.ts'
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        jarvis: {
          primary: '#00ff41',
          secondary: '#0891b2',
          warning: '#f59e0b',
          danger: '#ef4444',
          bg: {
            dark: '#0a0a0f',
            panel: '#111827'
          }
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'monospace'],
        display: ['Orbitron', 'sans-serif']
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'scan': 'scan 2s linear infinite',
        'glow': 'glow 2s ease-in-out infinite alternate'
      },
      keyframes: {
        scan: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' }
        },
        glow: {
          '0%': { boxShadow: '0 0 5px #00ff41' },
          '100%': { boxShadow: '0 0 20px #00ff41' }
        }
      }
    }
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('tailwindcss-animate')
  ]
}
```

## 7. Implementation Patterns

For complete implementation examples, see `references/advanced-patterns.md`.

**Common patterns**:
- HUD Panel Components with holographic effects
- Status Indicators with animated states
- Button Variants (primary, secondary, danger)
- Complex Dashboard Grid Layouts
- Responsive Mobile-First Designs
- Custom Animation Keyframes
- Holographic Glow Plugin

**Quick example**:
```vue
<div class="bg-jarvis-bg-panel/80 border border-jarvis-primary/30 backdrop-blur-sm rounded-lg p-4">
  <h3 class="font-display text-jarvis-primary text-lg uppercase tracking-wider mb-2">
    System Status
  </h3>
  <slot />
</div>
```

## 8. Quality Standards

### 7.1 Accessibility

```vue
<!-- Good - Sufficient contrast -->
<span class="text-jarvis-primary"><!-- #00ff41 on dark bg --></span>

<!-- Good - Focus visible -->
<button class="focus:ring-2 focus:ring-jarvis-primary focus:outline-none">

<!-- Good - Screen reader text -->
<span class="sr-only">Status: Active</span>
```

### 7.2 Design System Consistency

- Use theme colors defined in `tailwind.config.js`
- Follow spacing scale: 4, 8, 12, 16, 20, 24... (rem units)
- Apply consistent border radius: rounded, rounded-lg, rounded-xl
- Maintain typography hierarchy with font-display and font-mono

### 7.3 Performance Standards

- CSS bundle size under 50KB (gzipped)
- All animations use GPU-accelerated properties
- Content paths exclude test and build files
- No unused utility variants generated

## 9. Common Mistakes & Anti-Patterns

For comprehensive anti-patterns guide, see `references/anti-patterns.md`.

**Common mistakes to avoid**:
- ❌ Writing custom CSS when utilities exist
- ❌ Using inconsistent spacing values
- ❌ Hardcoding colors instead of theme references
- ❌ Overusing @apply for single-use styles
- ❌ Redundant breakpoint definitions
- ❌ Missing focus states on interactive elements
- ❌ Layout-triggering animation properties
- ❌ Overly broad content paths

**Quick fix**:
```vue
<!-- Bad -->
<div class="text-[#00ff41] p-3 mt-5">

<!-- Good -->
<div class="text-jarvis-primary p-4 mt-4">
```

## 10. Pre-Implementation Checklist

### Phase 1: Before Writing Code

- [ ] Write component tests for expected class applications
- [ ] Verify JARVIS theme colors are defined in config
- [ ] Check content paths include all source files
- [ ] Review existing components for reusable patterns

### Phase 2: During Implementation

- [ ] Use utilities before custom CSS
- [ ] Apply consistent spacing scale (4, 8, 12, 16...)
- [ ] Include focus states for all interactive elements
- [ ] Test responsive breakpoints at each size
- [ ] Use theme colors, never hardcoded hex values

### Phase 3: Before Committing

- [ ] All component tests pass: `npm test`
- [ ] Build completes without CSS errors: `npm run build`
- [ ] Check CSS bundle size hasn't grown unexpectedly
- [ ] Verify no unused @apply extractions
- [ ] Test accessibility with keyboard navigation

## 11. Summary

Tailwind CSS provides utility-first styling for JARVIS:

1. **TDD**: Write tests for class applications before implementation
2. **Performance**: Optimize content paths and use JIT mode
3. **Theme**: Define JARVIS colors and fonts in config
4. **Utilities**: Compose styles from utilities, extract patterns with @apply
5. **Accessibility**: Maintain focus states and sufficient contrast

**Remember**: The JARVIS HUD has a distinct visual identity - maintain consistency with the theme configuration and test all styling with vitest.

---

## 12. References

See `references/` directory for detailed guides:

- **`advanced-patterns.md`** - Implementation patterns, complex layouts, custom animations, and plugins
- **`performance-optimization.md`** - Build optimization, JIT mode, responsive strategies, and performance checklist
- **`anti-patterns.md`** - Common mistakes, bad practices, and how to fix them

**Official Documentation**:
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Tailwind Configuration](https://tailwindcss.com/docs/configuration)
- [Tailwind Plugins](https://tailwindcss.com/docs/plugins)

---

**Version**: 1.1.0
**Last Updated**: 2025-12-05
**Skill Type**: Expert - Frontend Styling
