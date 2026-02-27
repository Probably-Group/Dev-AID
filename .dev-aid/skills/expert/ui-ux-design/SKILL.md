---
name: ui-ux-design
version: 2.0.0
description: "UI/UX design patterns for user flows, wireframes, interaction design, and form security patterns. Use when designing user flows, creating wireframes, or implementing secure form interactions. Do NOT use for user research or usability testing (use ui-ux-expert)."
risk_level: LOW
token_budget: 3000
---
# UI/UX Design - Code Generation Rules

---

## 1. Security Principles

### 1.1 Form Security Patterns (CWE-352, CWE-20)

**Principle:** Forms are primary attack vectors. Implement proper CSRF protection and validation.

```html
<!-- ❌ WRONG - No CSRF protection -->
<form action="/api/update" method="POST">
  <input name="email" type="email">
  <button type="submit">Update</button>
</form>

<!-- ✅ CORRECT - CSRF token, autocomplete, validation -->
<form action="/api/update" method="POST">
  <input type="hidden" name="_csrf" value="{{ csrfToken }}">

  <label for="email">Email</label>
  <input
    id="email"
    name="email"
    type="email"
    autocomplete="email"
    required
    pattern="[^@]+@[^@]+\.[^@]+"
    aria-describedby="email-error"
  >
  <span id="email-error" role="alert" aria-live="polite"></span>

  <button type="submit">Update</button>
</form>
```

### 1.2 Sensitive Field Handling (CWE-200)

**Principle:** Mask sensitive data. Don't expose in autocomplete or errors.

```html
<!-- ❌ WRONG - Autocomplete enabled on sensitive fields -->
<input type="password" name="password" autocomplete="on">
<input type="text" name="ssn" value="123-45-6789">

<!-- ✅ CORRECT - Proper sensitive field handling -->
<input
  type="password"
  name="new-password"
  autocomplete="new-password"
  aria-label="New password"
  minlength="12"
>

<!-- Masked display for SSN -->
<input
  type="text"
  name="ssn"
  inputmode="numeric"
  autocomplete="off"
  pattern="\d{3}-\d{2}-\d{4}"
  placeholder="XXX-XX-XXXX"
  aria-label="Social Security Number"
>
```

### 1.3 Error Message Security (CWE-209)

**Principle:** Error messages should be helpful but not reveal system internals.

```typescript
// ❌ WRONG - Revealing system details
const errorMessages = {
  login: "User admin@company.com not found in database users_prod",
  api: "PostgreSQL error: connection timeout at 192.168.1.100:5432",
};

// ✅ CORRECT - User-friendly, secure messages
const errorMessages = {
  login: "Invalid email or password. Please try again.",
  api: "Something went wrong. Please try again later.",
  validation: {
    email: "Please enter a valid email address.",
    password: "Password must be at least 12 characters.",
  },
};
```

---

## 2. Version Requirements

```
# Design system tooling
tailwindcss>=3.4.0
postcss>=8.4.0
autoprefixer>=10.4.0
# Accessibility testing
axe-core>=4.8.0
```

---

## 3. Code Patterns

### WHEN designing forms, follow accessibility-first patterns

```html
<!-- ❌ WRONG - Missing labels, poor structure -->
<div>
  <input placeholder="Email">
  <input placeholder="Password" type="password">
  <button>Login</button>
  <span style="color: red">Error!</span>
</div>

<!-- ✅ CORRECT - Accessible form structure -->
<form class="space-y-4" novalidate @submit.prevent="handleSubmit">
  <div class="form-group">
    <label for="email" class="block text-sm font-medium">
      Email address
      <span class="text-red-500" aria-hidden="true">*</span>
    </label>
    <input
      id="email"
      v-model="form.email"
      type="email"
      autocomplete="email"
      required
      :aria-invalid="errors.email ? 'true' : undefined"
      aria-describedby="email-hint email-error"
      class="mt-1 block w-full rounded-md border-gray-300"
    >
    <p id="email-hint" class="mt-1 text-sm text-gray-500">
      We'll never share your email.
    </p>
    <p
      v-if="errors.email"
      id="email-error"
      role="alert"
      class="mt-1 text-sm text-red-600"
    >
      {{ errors.email }}
    </p>
  </div>

  <div class="form-group">
    <label for="password" class="block text-sm font-medium">
      Password
      <span class="text-red-500" aria-hidden="true">*</span>
    </label>
    <div class="relative">
      <input
        id="password"
        v-model="form.password"
        :type="showPassword ? 'text' : 'password'"
        autocomplete="current-password"
        required
        minlength="12"
        :aria-invalid="errors.password ? 'true' : undefined"
        aria-describedby="password-requirements password-error"
        class="mt-1 block w-full rounded-md border-gray-300 pr-10"
      >
      <button
        type="button"
        class="absolute inset-y-0 right-0 px-3"
        :aria-label="showPassword ? 'Hide password' : 'Show password'"
        @click="showPassword = !showPassword"
      >
        <EyeIcon v-if="!showPassword" class="h-5 w-5" />
        <EyeOffIcon v-else class="h-5 w-5" />
      </button>
    </div>
    <p id="password-requirements" class="mt-1 text-sm text-gray-500">
      Minimum 12 characters
    </p>
  </div>

  <button
    type="submit"
    :disabled="isSubmitting"
    class="w-full btn btn-primary"
  >
    <span v-if="isSubmitting" class="flex items-center gap-2">
      <Spinner class="h-4 w-4 animate-spin" />
      Signing in...
    </span>
    <span v-else>Sign in</span>
  </button>
</form>
```

### WHEN implementing loading states, provide feedback

```vue
<!-- ❌ WRONG - No loading indication -->
<template>
  <button @click="save">Save</button>
</template>

<!-- ✅ CORRECT - Comprehensive loading states -->
<template>
  <div>
    <!-- Button with loading state -->
    <button
      :disabled="state === 'loading'"
      :aria-busy="state === 'loading'"
      class="btn btn-primary relative"
      @click="save"
    >
      <span :class="{ 'opacity-0': state === 'loading' }">
        Save changes
      </span>
      <span
        v-if="state === 'loading'"
        class="absolute inset-0 flex items-center justify-center"
      >
        <Spinner class="h-5 w-5 animate-spin" aria-hidden="true" />
        <span class="sr-only">Saving...</span>
      </span>
    </button>

    <!-- Success feedback -->
    <Transition name="fade">
      <div
        v-if="state === 'success'"
        role="status"
        class="mt-2 text-green-600 flex items-center gap-2"
      >
        <CheckIcon class="h-5 w-5" aria-hidden="true" />
        Changes saved successfully
      </div>
    </Transition>

    <!-- Error feedback -->
    <Transition name="fade">
      <div
        v-if="state === 'error'"
        role="alert"
        class="mt-2 text-red-600 flex items-center gap-2"
      >
        <ExclamationIcon class="h-5 w-5" aria-hidden="true" />
        {{ errorMessage }}
        <button class="underline" @click="save">
          Try again
        </button>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
type State = 'idle' | 'loading' | 'success' | 'error';

const state = ref<State>('idle');
const errorMessage = ref('');

async function save() {
  state.value = 'loading';
  try {
    await api.save(form.value);
    state.value = 'success';
    // Auto-reset after 3 seconds
    setTimeout(() => { state.value = 'idle'; }, 3000);
  } catch (e) {
    state.value = 'error';
    errorMessage.value = 'Failed to save. Please try again.';
  }
}
</script>
```

### WHEN designing responsive layouts, use mobile-first

```vue
<!-- ❌ WRONG - Desktop-first, hiding on mobile -->
<template>
  <div class="sidebar hidden md:block">
    <!-- Sidebar content -->
  </div>
</template>

<!-- ✅ CORRECT - Mobile-first responsive layout -->
<template>
  <div class="min-h-screen flex flex-col lg:flex-row">
    <!-- Mobile navigation -->
    <header class="lg:hidden sticky top-0 z-40 bg-white border-b">
      <div class="flex items-center justify-between p-4">
        <Logo />
        <button
          :aria-expanded="mobileMenuOpen"
          aria-controls="mobile-menu"
          class="p-2 rounded-md"
          @click="mobileMenuOpen = !mobileMenuOpen"
        >
          <span class="sr-only">
            {{ mobileMenuOpen ? 'Close menu' : 'Open menu' }}
          </span>
          <MenuIcon v-if="!mobileMenuOpen" class="h-6 w-6" />
          <XIcon v-else class="h-6 w-6" />
        </button>
      </div>

      <!-- Mobile menu -->
      <Transition name="slide-down">
        <nav
          v-if="mobileMenuOpen"
          id="mobile-menu"
          class="border-t bg-white"
        >
          <NavLinks @click="mobileMenuOpen = false" />
        </nav>
      </Transition>
    </header>

    <!-- Desktop sidebar -->
    <aside class="hidden lg:flex lg:flex-col lg:w-64 lg:fixed lg:inset-y-0 border-r">
      <div class="flex-1 flex flex-col overflow-y-auto">
        <Logo class="p-4" />
        <nav class="flex-1 px-4 pb-4">
          <NavLinks />
        </nav>
      </div>
    </aside>

    <!-- Main content -->
    <main class="flex-1 lg:pl-64">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <slot />
      </div>
    </main>
  </div>
</template>
```

### WHEN implementing dark mode, use CSS variables

```css
/* ❌ WRONG - Hardcoded colors everywhere */
.card {
  background: white;
  color: #1a1a1a;
  border: 1px solid #e5e5e5;
}

.dark .card {
  background: #1a1a1a;
  color: white;
  border: 1px solid #333;
}

/* ✅ CORRECT - CSS custom properties */
:root {
  --color-bg-primary: 255 255 255;
  --color-bg-secondary: 249 250 251;
  --color-text-primary: 17 24 39;
  --color-text-secondary: 107 114 128;
  --color-border: 229 231 235;
}

:root.dark {
  --color-bg-primary: 17 24 39;
  --color-bg-secondary: 31 41 55;
  --color-text-primary: 249 250 251;
  --color-text-secondary: 156 163 175;
  --color-border: 55 65 81;
}

/* Tailwind config */
/* tailwind.config.js */
module.exports = {
  theme: {
    extend: {
      colors: {
        surface: {
          primary: 'rgb(var(--color-bg-primary) / <alpha-value>)',
          secondary: 'rgb(var(--color-bg-secondary) / <alpha-value>)',
        },
        content: {
          primary: 'rgb(var(--color-text-primary) / <alpha-value>)',
          secondary: 'rgb(var(--color-text-secondary) / <alpha-value>)',
        },
      },
    },
  },
};
```

---

## 4. Anti-Patterns

Do not:
- Create forms without CSRF protection
- Show detailed error messages to users (log details server-side)
- Enable autocomplete on sensitive fields (SSN, credit card)
- Use placeholder as the only label
- Hide content with display:none for accessibility (use sr-only)
- Rely solely on color to convey information
- Use custom scrollbars that break accessibility
- Implement infinite scroll without pagination fallback

---

## 5. Testing

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/vue';
import { axe, toHaveNoViolations } from 'jest-axe';
import LoginForm from './LoginForm.vue';

expect.extend(toHaveNoViolations);

# ... (additional test cases follow same pattern)
```

---

## 6. Pre-Generation Checklist

Before generating UI code:

- [ ] Forms: CSRF tokens, proper labels, validation messages
- [ ] Accessibility: ARIA attributes, focus management, screen reader text
- [ ] Loading states: Buttons disabled, spinners, feedback messages
- [ ] Error handling: User-friendly messages, no system details
- [ ] Responsive: Mobile-first, proper breakpoints
- [ ] Dark mode: CSS variables, no hardcoded colors
- [ ] Sensitive fields: Autocomplete off, masked display
- [ ] Touch targets: Minimum 44x44px for mobile

---
