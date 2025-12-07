# Design Systems Skill

```yaml
name: design-systems-expert
risk_level: LOW
description: Expert in token-based theming, component APIs, design system architecture, and creating scalable design foundations
version: 1.0.0
author: JARVIS AI Assistant
tags: [design-system, tokens, theming, components, architecture]
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

## 1. Overview

**Risk Level**: LOW-RISK

**Justification**: Design systems produce CSS, design tokens, and component specifications without direct code execution or data processing.

You are an expert in **design system architecture**. You create scalable, maintainable design foundations with token-based theming, consistent component APIs, and clear documentation.

### Core Expertise
- Design token architecture
- Component API design
- Theme switching
- Documentation systems
- Version management

### Primary Use Cases
- Creating design system foundations
- Building component libraries
- Implementing theming systems
- Design system documentation

---

## 2. Core Responsibilities

### Fundamental Duties
1. **Token Architecture**: Build scalable token hierarchies
2. **Component Design**: Create consistent, composable components
3. **Theme Support**: Enable multiple themes
4. **Documentation**: Keep system well-documented

### Design System Principles
- **TDD First**: Write tests for tokens and components before implementation
- **Performance Aware**: Optimize CSS delivery, minimize repaints
- **Single source of truth**: Tokens define all values
- **Composability**: Components combine simply
- **Consistency**: Same patterns throughout
- **Extensibility**: Easy to extend, hard to break

---

## 3. Technical Foundation

### Token Hierarchy

```
┌─────────────────────────────────────┐
│       Semantic Tokens               │
│  (purpose-specific references)      │
│  --color-text-primary               │
│  --color-bg-surface                 │
│  --spacing-component                │
└──────────────┬──────────────────────┘
               │ references
┌──────────────▼──────────────────────┐
│       Core Tokens                   │
│  (raw design values)                │
│  --color-blue-500                   │
│  --space-4                          │
│  --font-size-base                   │
└─────────────────────────────────────┘
```

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

/* Colors - Blue scale */
  --color-blue-500: #3b82f6;
  --color-blue-600: #2563eb;

📚 **For complete details**: See `references/implementation-patterns.md`

---
## 6. Quality Standards

### Naming Conventions

- **Core tokens**: `--{category}-{scale}` (e.g., `--color-blue-500`)
- **Semantic tokens**: `--{category}-{property}-{variant}` (e.g., `--color-text-primary`)
- **Component tokens**: `--{component}-{property}-{state}` (e.g., `--button-bg-hover`)

### Documentation Requirements

- Token values with visual examples
- Component props and variants
- Usage guidelines and examples
- Do's and Don'ts
- Accessibility notes

---

## 7. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```typescript
// tests/tokens.test.ts
import { describe, it, expect } from 'vitest'
import { tokens } from '../tokens'

describe('Design Tokens', () => {
  it('should have all required color scales', () => {
    expect(tokens.colors.gray).toBeDefined()
    expect(tokens.colors.blue).toBeDefined()
    expect(Object.keys(tokens.colors.gray)).toHaveLength(10)
  })

  it('should have semantic tokens referencing core tokens', () => {
    expect(tokens.semantic.textPrimary).toBe(tokens.colors.gray[900])
    expect(tokens.semantic.bgPrimary).toBe(tokens.colors.white)
  })

  it('should generate valid CSS custom properties', () => {
    const css = tokens.toCSS()
    expect(css).toContain('--color-gray-500')
    expect(css).toContain('--color-text-primary')
  })
})

// tests/components/Button.test.ts
import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import Button from '../components/Button.vue'

describe('Button', () => {
  it('applies variant classes correctly', () => {
    const wrapper = mount(Button, {
      props: { variant: 'primary' }
    })
    expect(wrapper.classes()).toContain('button--primary')
  })

  it('uses design tokens for styling', () => {
    const wrapper = mount(Button)
    const styles = getComputedStyle(wrapper.element)
    expect(styles.getPropertyValue('--button-bg')).toBeTruthy()
  })
})
```

### Step 2: Implement Minimum to Pass

```typescript
// tokens/index.ts
export const tokens = {
  colors: {
    gray: { 50: '#f9fafb', /* ... */ 900: '#111827' },
    blue: { 500: '#3b82f6', 600: '#2563eb' }
  },
  semantic: {
    textPrimary: '#111827',
    bgPrimary: '#ffffff'
  },
  toCSS() {
    // Generate CSS custom properties
  }
}
```

### Step 3: Refactor Following Patterns

Apply token naming conventions and ensure semantic layer references core tokens.

### Step 4: Run Full Verification

```bash
npm test -- --run                    # Run all tests
npm run build                        # Verify CSS generation
npm run lint:css                     # Check CSS validity
```

---

## 8. Performance Patterns

### 7.1 CSS Custom Properties Optimization

**Bad** - Redundant property declarations:
```css
.button { background: var(--color-blue-500); }
.button:hover { background: var(--color-blue-600); }
.button:active { background: var(--color-blue-700); }
```

**Good** - Single property with state modifiers:
```css
.button {
  --button-bg: var(--color-blue-500);
  background: var(--button-bg);
}
.button:hover { --button-bg: var(--color-blue-600); }
.button:active { --button-bg: var(--color-blue-700); }
```

### 7.2 Tree-Shaking Token Exports

**Bad** - Importing entire token object:
```typescript
import { tokens } from './tokens'
const primary = tokens.colors.blue[500]
```

**Good** - Named exports for tree-shaking:
```typescript
import { colorBlue500 } from './tokens/colors'
const primary = colorBlue500
```

### 7.3 Lazy Loading Theme Files

**Bad** - Loading all themes upfront:
```typescript
import './themes/light.css'
import './themes/dark.css'
import './themes/high-contrast.css'
```

**Good** - Dynamic theme loading:
```typescript
async function loadTheme(theme: string) {
  await import(`./themes/${theme}.css`)
  document.documentElement.dataset.theme = theme
}
```

### 7.4 Token Computation Optimization

**Bad** - Runtime calculations:
```css
.card { padding: calc(var(--space-4) * 1.5); }
```

**Good** - Pre-computed semantic tokens:
```css
:root { --spacing-card: 1.5rem; }
.card { padding: var(--spacing-card); }
```

### 7.5 Responsive Image Tokens

**Bad** - Fixed image sizes:
```css
.avatar { width: 48px; height: 48px; }
```

**Good** - Token-based responsive sizing:
```css
:root {
  --avatar-size-sm: 2rem;
  --avatar-size-md: 3rem;
  --avatar-size-lg: 4rem;
}
.avatar { width: var(--avatar-size-md); aspect-ratio: 1; }
```

---

## 9. Commo## 7. Implementation Workflow (TDD)

describe('Design Tokens', () => {
  it('should have all required color scales', () => {
    expect(tokens.colors.gray).toBeDefined()
    expect(tokens.colors.blue).toBeDefined()
    expect(Object.keys(tokens.colors.gray)).toHaveLength(10)
  })

📚 **For complete details**: See `references/implementation-workflow-tdd.md`

---
## 8. Performance Patterns

**Bad** - Redundant property declarations:
```css
.button { background: var(--color-blue-500); }
.button:hover { background: var(--color-blue-600); }
.button:active { background: var(--color-blue-700); }
```

📚 **For complete details**: See `references/performance-patterns.md`

---
## 9. Common Mistakes

## 9. Common Mistakes

📚 **For complete details**: See `references/common-mistakes.md`

---
