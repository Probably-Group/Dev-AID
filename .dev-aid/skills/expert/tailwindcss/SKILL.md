---
name: tailwindcss
version: 2.0.0
description: "Tailwind CSS patterns with utility composition, custom plugins, responsive design, and dark mode. Use when styling with Tailwind utilities, creating custom plugins, or building responsive layouts. Do NOT use for CSS-in-JS or styled-components approaches."
compatibility: "Tailwind CSS 3.4+, Node.js 18+"
risk_level: LOW
token_budget: 3000
---
# Tailwind CSS Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.2 Security Patterns (security rules)

**CWE-79: XSS via Dynamic Classes**
- Do not: `class="${userInput}"` or dynamic class names from user input
- Instead: Whitelist allowed classes, use static class mappings

**CWE-94: Arbitrary Code in Config**
- Do not: `tailwind.config.js` with dynamic imports from user input
- Instead: Static config, validate any customization inputs

**CWE-400: Build-time DoS**
- Do not: Allow user-controlled content in Tailwind's content paths
- Instead: Restrict content scanning to known directories

---

## 1. Security Principles

### 1.1 No Dynamic Class Construction (CWE-94)

**Principle:** Never construct class names from user input. Use complete class names.

```html
<!-- ❌ WRONG - Dynamic class construction -->
<div :class="`bg-${userColor}-500`">
  <!-- User could inject: "red-500 hidden" or worse -->
</div>

<div :class="`text-${size}`">
  <!-- Tailwind can't purge dynamic classes -->
</div>

<!-- ✅ CORRECT - Complete class names with safelist -->
<div :class="colorClasses[userColor]">
  <!-- Mapped to predefined classes -->
</div>

<script setup>
const colorClasses = {
  red: 'bg-red-500',
  blue: 'bg-blue-500',
  green: 'bg-green-500',
} as const;
</script>
```

### 1.2 Content Security (CWE-79)

**Principle:** Never use v-html or innerHTML with user content in styled elements.

```html
<!-- ❌ WRONG - XSS risk -->
<div class="prose" v-html="userContent"></div>

<!-- ✅ CORRECT - Sanitized or text only -->
<div class="prose">{{ sanitizedContent }}</div>
```

### 1.3 Safelist for Dynamic Classes

**Principle:** Use safelist in config for any dynamically selected classes.

```javascript
// tailwind.config.js
module.exports = {
  safelist: [
    // Explicit safelist for dynamic themes
    'bg-red-500', 'bg-blue-500', 'bg-green-500',
    'text-red-500', 'text-blue-500', 'text-green-500',
    // Pattern-based safelist
    {
      pattern: /^(bg|text|border)-(primary|secondary|accent)/,
    },
  ],
};
```

### 1.4 Fail Secure (CWE-636)

**Principle:** Missing classes should render safely. Always have fallback styles.

### 1.5 Defense in Depth

**Principle:** Combine Tailwind with CSS custom properties for theming.

---

## 2. Version Requirements

Use these minimum versions:

```json
{
  "devDependencies": {
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0",
    "@tailwindcss/forms": "^0.5.0",
    "@tailwindcss/typography": "^0.5.0"
  }
}
```

---

## 3. Code Patterns

### 3.1 WHEN configuring Tailwind

```javascript
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
    // Include component libraries
    './node_modules/@myorg/ui/**/*.{vue,js,ts}',
  ],

  theme: {
    extend: {
      // Custom colors with semantic names
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        secondary: {
          50: '#f8fafc',
          500: '#64748b',
          700: '#334155',
        },
      },

      // Custom spacing
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },

      // Custom breakpoints
      screens: {
        'xs': '475px',
        '3xl': '1920px',
      },

      // Animation
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },

  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],

  // Safelist for dynamic classes
  safelist: [
    'bg-red-500', 'bg-green-500', 'bg-blue-500',
    'text-red-500', 'text-green-500', 'text-blue-500',
  ],
};
```

### 3.2 WHEN creating reusable component styles

```vue
<!-- Button.vue -->
<template>
  <button
    :class="[
      // Base styles
      'inline-flex items-center justify-center',
      'font-medium rounded-lg',
      'focus:outline-none focus:ring-2 focus:ring-offset-2',
      'disabled:opacity-50 disabled:cursor-not-allowed',
      'transition-colors duration-200',
      // Size variants
      sizeClasses[size],
      // Color variants
      variantClasses[variant],
    ]"
    :disabled="disabled || loading"
  >
    <svg
      v-if="loading"
      class="animate-spin -ml-1 mr-2 h-4 w-4"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        class="opacity-25"
        cx="12" cy="12" r="10"
        stroke="currentColor"
        stroke-width="4"
      />
      <path
        class="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
      />
    </svg>
    <slot />
  </button>
</template>

<script setup lang="ts">
defineProps<{
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  disabled?: boolean;
}>();

// Complete class names - no dynamic construction
const sizeClasses = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-sm',
  lg: 'px-6 py-3 text-base',
} as const;

const variantClasses = {
  primary: 'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500',
  secondary: 'bg-secondary-100 text-secondary-700 hover:bg-secondary-200 focus:ring-secondary-500',
  danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
  ghost: 'bg-transparent text-secondary-700 hover:bg-secondary-100 focus:ring-secondary-500',
} as const;
</script>
```

### 3.3 WHEN implementing dark mode

```javascript
// tailwind.config.js
module.exports = {
  darkMode: 'class', // or 'media' for system preference

  theme: {
    extend: {
      // Colors that work in both modes
      colors: {
        surface: {
          light: '#ffffff',
          dark: '#1f2937',
        },
      },
    },
  },
};
```

```vue
<!-- Layout.vue -->
<template>
  <div :class="[
    'min-h-screen transition-colors duration-300',
    'bg-white dark:bg-gray-900',
    'text-gray-900 dark:text-gray-100',
  ]">
    <slot />
  </div>
</template>

<!-- Component with dark mode -->
<template>
  <div class="
    bg-white dark:bg-gray-800
    border border-gray-200 dark:border-gray-700
    rounded-lg shadow-sm dark:shadow-gray-900/20
    p-4
  ">
    <h3 class="text-gray-900 dark:text-white font-semibold">
      {{ title }}
    </h3>
    <p class="text-gray-600 dark:text-gray-400 mt-2">
      {{ description }}
    </p>
  </div>
</template>
```

### 3.4 WHEN creating responsive layouts

```vue
<template>
  <!-- Responsive grid -->
  <div class="
    grid
    grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4
    gap-4 md:gap-6 lg:gap-8
  ">
    <div v-for="item in items" :key="item.id">
      <!-- Responsive card -->
      <div class="
        p-4 md:p-6
        rounded-lg
        hover:shadow-lg
        transition-shadow
      ">
        <!-- Responsive text -->
        <h3 class="text-lg md:text-xl lg:text-2xl font-bold">
          {{ item.title }}
        </h3>

        <!-- Hide on mobile, show on desktop -->
        <p class="hidden md:block text-gray-600">
          {{ item.description }}
        </p>

        <!-- Show on mobile only -->
        <p class="md:hidden text-gray-600 line-clamp-2">
          {{ item.shortDescription }}
        </p>
      </div>
    </div>
  </div>

  <!-- Responsive navigation -->
  <nav class="
    flex flex-col md:flex-row
    items-center
    space-y-2 md:space-y-0 md:space-x-4
  ">
    <a href="#" class="
      w-full md:w-auto
      px-4 py-2
      text-center
      rounded-lg
      hover:bg-gray-100
    ">
      Link
    </a>
  </nav>
</template>
```

### 3.5 WHEN implementing forms with @tailwindcss/forms

```vue
<template>
  <form @submit.prevent="submit" class="space-y-6">
    <!-- Text input -->
    <div>
      <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        Email
      </label>
      <input
        id="email"
        v-model="form.email"
        type="email"
        required
        :class="[
          'mt-1 block w-full rounded-md shadow-sm',
          'focus:ring-primary-500 focus:border-primary-500',
          errors.email
            ? 'border-red-300 text-red-900 placeholder-red-300'
            : 'border-gray-300 dark:border-gray-600 dark:bg-gray-700',
        ]"
      />
      <p v-if="errors.email" class="mt-1 text-sm text-red-600">
        {{ errors.email }}
      </p>
    </div>

    <!-- Select -->
    <div>
      <label for="country" class="block text-sm font-medium text-gray-700">
        Country
      </label>
      <select
        id="country"
        v-model="form.country"
        class="
          mt-1 block w-full rounded-md border-gray-300 shadow-sm
          focus:ring-primary-500 focus:border-primary-500
        "
      >
        <option value="">Select a country</option>
        <option v-for="c in countries" :key="c.code" :value="c.code">
          {{ c.name }}
        </option>
      </select>
    </div>

    <!-- Checkbox -->
    <div class="flex items-center">
      <input
        id="terms"
        v-model="form.acceptTerms"
        type="checkbox"
        class="
          h-4 w-4 rounded
          border-gray-300
          text-primary-600
          focus:ring-primary-500
        "
      />
      <label for="terms" class="ml-2 text-sm text-gray-700">
        I accept the terms and conditions
      </label>
    </div>

    <!-- Submit button -->
    <button
      type="submit"
      :disabled="loading"
      class="
        w-full flex justify-center
        py-2 px-4
        border border-transparent rounded-md shadow-sm
        text-sm font-medium text-white
        bg-primary-600 hover:bg-primary-700
        focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500
        disabled:opacity-50 disabled:cursor-not-allowed
      "
    >
      {{ loading ? 'Submitting...' : 'Submit' }}
    </button>
  </form>
</template>
```

### 3.6 WHEN using CSS custom properties with Tailwind

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        // Reference CSS custom properties
        brand: 'var(--color-brand)',
        surface: 'var(--color-surface)',
      },
    },
  },
};
```

```css
/* styles/themes.css */
:root {
  --color-brand: #3b82f6;
  --color-surface: #ffffff;
}

.dark {
  --color-brand: #60a5fa;
  --color-surface: #1f2937;
}

/* Custom theme */
.theme-purple {
  --color-brand: #8b5cf6;
}
```

```vue
<template>
  <!-- Now you can use bg-brand, text-brand, etc. -->
  <div class="bg-surface text-brand">
    Theme-aware content
  </div>
</template>
```

---

## 4. Anti-Patterns

Do not:
- Construct class names dynamically from user input
- Use string interpolation for class names
- Inline styles when Tailwind classes exist
- Override Tailwind with !important
- Use arbitrary values `[...]` excessively (configure in theme instead)
- Forget to safelist dynamically selected classes

---

## 5. Testing

**ALWAYS test responsive and dark mode:**

```typescript
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import Button from './Button.vue';

describe('Button Component', () => {
  it('applies correct size classes', () => {
    const wrapper = mount(Button, {
# ... (additional test cases follow same pattern)
```

---

## 6. Pre-Generation Checklist

Before generating any Tailwind code:

- [ ] No dynamic class name construction from user input
- [ ] Complete class names used (not interpolated)
- [ ] Safelist configured for dynamically selected classes
- [ ] Dark mode variants included where needed
- [ ] Responsive breakpoints considered
- [ ] Focus states for accessibility
- [ ] Disabled states for interactive elements
- [ ] Transition utilities for smooth UX
- [ ] Custom values in theme config (not arbitrary `[...]`)
- [ ] Form plugin for form elements

---
