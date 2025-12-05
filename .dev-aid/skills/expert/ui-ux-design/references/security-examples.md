# UI/UX Security and Accessibility Examples

## Overview

This document covers security-conscious UI/UX practices with a focus on accessibility, privacy, and safe user interactions.

---

## 1. Accessibility Requirements

### Color Contrast

**Requirement**: Minimum 4.5:1 contrast ratio for normal text, 3:1 for large text (WCAG AA).

**Bad Example**:
```css
/* ❌ Insufficient contrast (2.1:1) */
.text-muted {
  color: #888888;
  background-color: #ffffff;
}

.link {
  color: #00bcd4; /* Cyan on white: 2.1:1 */
}
```

**Good Example**:
```css
/* ✅ Sufficient contrast (4.5:1+) */
.text-primary {
  color: rgba(255, 255, 255, 0.95); /* 18:1 on dark bg */
  background-color: #1a1a1a;
}

.text-secondary {
  color: rgba(255, 255, 255, 0.7); /* 8.5:1 on dark bg */
  background-color: #1a1a1a;
}

.text-disabled {
  color: rgba(255, 255, 255, 0.38); /* 4.7:1 on dark bg */
  background-color: #1a1a1a;
}

.link-light {
  color: #0077cc; /* 4.5:1 on white */
}
```

**Testing**:
```javascript
// Use axe-core for automated contrast checking
import { axe } from 'jest-axe'

test('has sufficient color contrast', async () => {
  const html = `
    <div style="background: #1a1a1a; color: rgba(255, 255, 255, 0.95);">
      Test content
    </div>
  `
  const results = await axe(html)
  expect(results.violations).toHaveLength(0)
})
```

---

### Touch Targets

**Requirement**: Minimum 44x44px for all interactive elements (WCAG 2.1).

**Bad Example**:
```css
/* ❌ Too small for touch (24x24px) */
.icon-button {
  width: 24px;
  height: 24px;
  padding: 0;
}

.checkbox {
  width: 16px;
  height: 16px;
}
```

**Good Example**:
```css
/* ✅ Proper touch target (44x44px+) */
.icon-button {
  min-width: 44px;
  min-height: 44px;
  padding: 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.icon-button svg {
  width: 24px;
  height: 24px;
}

/* Checkbox with larger hit area */
.checkbox-wrapper {
  position: relative;
  min-width: 44px;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.checkbox {
  width: 20px;
  height: 20px;
}
```

**Implementation**:
```vue
<template>
  <button
    class="icon-button"
    :aria-label="label"
    type="button"
  >
    <svg
      class="icon"
      width="24"
      height="24"
      viewBox="0 0 24 24"
    >
      <path :d="iconPath" />
    </svg>
  </button>
</template>

<style scoped>
.icon-button {
  min-width: 44px;
  min-height: 44px;
  padding: 10px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.icon-button:hover {
  background-color: rgba(255, 255, 255, 0.08);
}

.icon-button:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
}
</style>
```

---

### Focus Indicators

**Requirement**: Visible focus states for all interactive elements.

**Bad Example**:
```css
/* ❌ No focus indicator */
button:focus {
  outline: none;
}

a:focus {
  outline: 0;
}
```

**Good Example**:
```css
/* ✅ Visible focus states */
:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
  border-radius: 4px;
}

/* Custom focus for buttons */
button:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(0, 188, 212, 0.2);
}

/* Focus for input fields */
input:focus-visible,
textarea:focus-visible {
  border-color: var(--color-primary-500);
  box-shadow: 0 0 0 3px rgba(0, 188, 212, 0.2);
  outline: none;
}
```

**JavaScript Enhancement**:
```typescript
// Add visible focus class only for keyboard navigation
document.addEventListener('keydown', (e) => {
  if (e.key === 'Tab') {
    document.body.classList.add('keyboard-nav')
  }
})

document.addEventListener('mousedown', () => {
  document.body.classList.remove('keyboard-nav')
})
```

```css
/* Show focus only during keyboard navigation */
body:not(.keyboard-nav) *:focus {
  outline: none;
}

body.keyboard-nav *:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
}
```

---

### Motion Preferences

**Requirement**: Respect `prefers-reduced-motion` preference.

**Bad Example**:
```css
/* ❌ Always animates */
.card {
  transition: all 0.3s ease;
}

.card:hover {
  transform: scale(1.1) rotate(5deg);
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.notification {
  animation: bounce 1s infinite;
}
```

**Good Example**:
```css
/* ✅ Respects motion preferences */
.card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Disable animations for reduced motion */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }

  /* Provide alternative feedback */
  .card:hover {
    transform: none;
    box-shadow: 0 0 0 2px var(--color-primary-500);
  }
}
```

---

## 2. Privacy and Data Protection

### Sensitive Data Display

**Use Case**: Protect sensitive information in UI while maintaining usability.

**Bad Example**:
```vue
<!-- ❌ Exposes sensitive data -->
<template>
  <div class="user-info">
    <p>Email: {{ user.email }}</p>
    <p>SSN: {{ user.ssn }}</p>
    <p>Credit Card: {{ user.creditCard }}</p>
  </div>
</template>
```

**Good Example**:
```vue
<!-- ✅ Masks sensitive data with option to reveal -->
<template>
  <div class="user-info">
    <div class="field">
      <label>Email:</label>
      <span>{{ user.email }}</span>
    </div>

    <div class="field">
      <label>SSN:</label>
      <button
        @click="toggleSSN"
        :aria-label="ssnVisible ? 'Hide SSN' : 'Show SSN'"
        class="toggle-visibility"
      >
        {{ ssnVisible ? user.ssn : maskSSN(user.ssn) }}
        <svg :class="ssnVisible ? 'eye-off' : 'eye'">...</svg>
      </button>
    </div>

    <div class="field">
      <label>Credit Card:</label>
      <span>{{ maskCreditCard(user.creditCard) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const ssnVisible = ref(false)

const maskSSN = (ssn: string) => {
  return '***-**-' + ssn.slice(-4)
}

const maskCreditCard = (card: string) => {
  return '**** **** **** ' + card.slice(-4)
}

const toggleSSN = () => {
  ssnVisible.value = !ssnVisible.value

  // Auto-hide after 10 seconds
  if (ssnVisible.value) {
    setTimeout(() => {
      ssnVisible.value = false
    }, 10000)
  }
}
</script>
```

---

### Password Input Security

**Bad Example**:
```vue
<!-- ❌ Insecure password field -->
<template>
  <input
    v-model="password"
    type="text"
    autocomplete="off"
  />
</template>
```

**Good Example**:
```vue
<!-- ✅ Secure password field -->
<template>
  <div class="password-field">
    <label for="password" class="sr-only">Password</label>
    <input
      id="password"
      v-model="password"
      :type="showPassword ? 'text' : 'password'"
      autocomplete="current-password"
      aria-describedby="password-requirements"
      :aria-invalid="!isValid"
    />
    <button
      type="button"
      @click="showPassword = !showPassword"
      :aria-label="showPassword ? 'Hide password' : 'Show password'"
      class="toggle-password"
    >
      <svg :class="showPassword ? 'eye-off' : 'eye'">...</svg>
    </button>

    <div
      id="password-requirements"
      class="password-hint"
      :class="{ 'sr-only': isValid }"
    >
      Password must be at least 12 characters with uppercase, lowercase, number, and symbol
    </div>
  </div>
</template>

<style scoped>
/* Prevent password managers from capturing visible password */
input[type="text"][autocomplete="current-password"] {
  -webkit-text-security: disc;
}
</style>
```

---

### Preventing Information Leakage

**Bad Example**:
```vue
<!-- ❌ Reveals whether email exists -->
<template>
  <div v-if="error === 'USER_NOT_FOUND'">
    This email address is not registered
  </div>
  <div v-else-if="error === 'INVALID_PASSWORD'">
    Incorrect password
  </div>
</template>
```

**Good Example**:
```vue
<!-- ✅ Generic error message -->
<template>
  <div v-if="error" class="error-message">
    Invalid email or password. Please try again.
  </div>

  <!-- Rate limiting indicator -->
  <div v-if="rateLimited" class="warning-message">
    Too many failed attempts. Please wait {{ retryAfter }} seconds.
  </div>
</template>
```

---

## 3. Secure Form Handling

### CSRF Protection

**Implementation**:
```vue
<template>
  <form @submit.prevent="handleSubmit">
    <!-- CSRF token (hidden from users) -->
    <input
      type="hidden"
      name="_csrf"
      :value="csrfToken"
    />

    <div class="form-field">
      <label for="email">Email</label>
      <input
        id="email"
        v-model="email"
        type="email"
        required
        autocomplete="email"
      />
    </div>

    <button type="submit">Submit</button>
  </form>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const csrfToken = ref('')

onMounted(async () => {
  // Fetch CSRF token from server
  const response = await fetch('/api/csrf-token')
  const data = await response.json()
  csrfToken.value = data.token
})

const handleSubmit = async () => {
  // Token automatically included in form data
  const formData = new FormData(event.target)
  await fetch('/api/submit', {
    method: 'POST',
    body: formData,
    headers: {
      'X-CSRF-Token': csrfToken.value
    }
  })
}
</script>
```

---

### Input Sanitization Display

**Bad Example**:
```vue
<!-- ❌ XSS vulnerability -->
<template>
  <div v-html="userContent"></div>
</template>
```

**Good Example**:
```vue
<!-- ✅ Sanitized content -->
<template>
  <div v-html="sanitizedContent"></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import DOMPurify from 'dompurify'

const props = defineProps<{
  userContent: string
}>()

const sanitizedContent = computed(() => {
  return DOMPurify.sanitize(props.userContent, {
    ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'a'],
    ALLOWED_ATTR: ['href', 'title'],
    ALLOW_DATA_ATTR: false
  })
})
</script>
```

---

## 4. Screen Reader Accessibility

### Proper ARIA Labels

**Bad Example**:
```vue
<!-- ❌ No context for screen readers -->
<template>
  <button @click="deleteItem">
    <svg>...</svg>
  </button>
</template>
```

**Good Example**:
```vue
<!-- ✅ Descriptive labels -->
<template>
  <button
    @click="deleteItem"
    :aria-label="`Delete ${item.name}`"
    type="button"
  >
    <svg aria-hidden="true">...</svg>
  </button>
</template>
```

---

### Live Regions

**Implementation**:
```vue
<template>
  <!-- Announce dynamic updates to screen readers -->
  <div
    role="status"
    aria-live="polite"
    aria-atomic="true"
    class="sr-only"
  >
    {{ statusMessage }}
  </div>

  <!-- Critical alerts -->
  <div
    role="alert"
    aria-live="assertive"
    class="alert-container"
    v-if="errorMessage"
  >
    {{ errorMessage }}
  </div>

  <!-- Main content -->
  <div class="content">
    <button @click="performAction">
      Perform Action
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const statusMessage = ref('')
const errorMessage = ref('')

const performAction = async () => {
  statusMessage.value = 'Processing...'

  try {
    await apiCall()
    statusMessage.value = 'Action completed successfully'
  } catch (error) {
    errorMessage.value = 'Error: Action failed. Please try again.'
  }
}
</script>

<style scoped>
/* Screen reader only class */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
</style>
```

---

## 5. Keyboard Navigation

### Focus Trap in Modals

**Implementation**:
```vue
<template>
  <Teleport to="body">
    <div
      v-if="isOpen"
      class="modal-overlay"
      @click="handleOverlayClick"
      @keydown.esc="close"
    >
      <div
        ref="modalRef"
        role="dialog"
        aria-modal="true"
        :aria-labelledby="titleId"
        class="modal"
        @click.stop
      >
        <h2 :id="titleId">{{ title }}</h2>

        <div class="modal-content">
          <slot />
        </div>

        <div class="modal-actions">
          <button
            ref="cancelButtonRef"
            @click="close"
            type="button"
          >
            Cancel
          </button>
          <button
            ref="confirmButtonRef"
            @click="confirm"
            type="button"
          >
            Confirm
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps<{
  isOpen: boolean
  title: string
}>()

const emit = defineEmits<{
  close: []
  confirm: []
}>()

const modalRef = ref<HTMLElement>()
const cancelButtonRef = ref<HTMLButtonElement>()
const previousActiveElement = ref<HTMLElement>()
const titleId = `modal-title-${Math.random().toString(36).substr(2, 9)}`

// Focus trap
const trapFocus = (e: KeyboardEvent) => {
  if (!modalRef.value) return

  const focusableElements = modalRef.value.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  )

  const firstElement = focusableElements[0] as HTMLElement
  const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement

  if (e.key === 'Tab') {
    if (e.shiftKey && document.activeElement === firstElement) {
      e.preventDefault()
      lastElement.focus()
    } else if (!e.shiftKey && document.activeElement === lastElement) {
      e.preventDefault()
      firstElement.focus()
    }
  }
}

watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    previousActiveElement.value = document.activeElement as HTMLElement
    document.addEventListener('keydown', trapFocus)

    // Focus first button when modal opens
    setTimeout(() => {
      cancelButtonRef.value?.focus()
    }, 100)
  } else {
    document.removeEventListener('keydown', trapFocus)

    // Restore focus to previous element
    previousActiveElement.value?.focus()
  }
})

onBeforeUnmount(() => {
  document.removeEventListener('keydown', trapFocus)
})

const close = () => emit('close')
const confirm = () => emit('confirm')
const handleOverlayClick = () => close()
</script>
```

---

## Security Checklist

### Before Deployment
- [ ] All form inputs validated and sanitized
- [ ] CSRF tokens implemented for state-changing operations
- [ ] Sensitive data masked or hidden by default
- [ ] Password fields use proper autocomplete attributes
- [ ] No sensitive data in URL parameters
- [ ] Error messages don't leak information
- [ ] Rate limiting implemented on forms
- [ ] ARIA labels provided for all interactive elements
- [ ] Focus management working correctly
- [ ] Keyboard navigation fully functional
- [ ] Color contrast meets WCAG AA (4.5:1)
- [ ] Touch targets ≥44px
- [ ] Motion preferences respected
- [ ] Screen reader tested (NVDA/JAWS/VoiceOver)

---

## Summary

Secure and accessible UI/UX requires:
1. **WCAG 2.1 AA compliance** minimum
2. **Privacy by design** - protect sensitive data
3. **Secure defaults** - forms, authentication, data display
4. **Keyboard accessibility** - focus management, navigation
5. **Screen reader support** - ARIA labels, live regions
6. **User preferences** - respect reduced motion, high contrast

Security and accessibility are not optional - they are fundamental requirements for quality UI/UX.
