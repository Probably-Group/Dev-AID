---
name: ui-ux-expert
version: 2.0.0
description: "UI/UX expertise for user research, usability testing, responsive design systems, and frontend security patterns. Use when conducting user research, planning usability tests, or designing responsive layouts. Do NOT use for accessibility compliance auditing (use accessibility-wcag)."
risk_level: LOW
token_budget: 4000
---
# UI/UX Expert - Code Generation Rules

---

## 1. Security Principles

### 1.1 Clickjacking Prevention (CWE-1021)

**Principle:** Prevent UI elements from being embedded in malicious iframes.

```typescript
// ❌ WRONG - No frame protection
// Page can be embedded anywhere

// ✅ CORRECT - Frame busting and CSP headers
// nuxt.config.ts or server middleware
export default defineNuxtConfig({
  routeRules: {
    '/**': {
      headers: {
        'X-Frame-Options': 'DENY',
        'Content-Security-Policy': "frame-ancestors 'none'",
      },
    },
  },
});

// Client-side backup (for legacy browser support)
if (window.self !== window.top) {
  window.top.location = window.self.location;
}
```

### 1.2 Safe External Links (CWE-601)

**Principle:** External links must prevent tabnabbing attacks.

```html
<!-- ❌ WRONG - Vulnerable to tabnabbing -->
<a href="https://external.com" target="_blank">External Link</a>

<!-- ✅ CORRECT - Safe external link -->
<a
  href="https://external.com"
  target="_blank"
  rel="noopener noreferrer"
>
  External Link
  <span class="sr-only">(opens in new tab)</span>
  <ExternalLinkIcon class="h-4 w-4 inline" aria-hidden="true" />
</a>

<!-- Component for safe external links -->
<script setup lang="ts">
interface Props {
  href: string;
  showIcon?: boolean;
}
const props = withDefaults(defineProps<Props>(), {
  showIcon: true,
});

const isExternal = computed(() => {
  try {
    const url = new URL(props.href, window.location.origin);
    return url.origin !== window.location.origin;
  } catch {
    return false;
  }
});
</script>

<template>
  <a
    :href="href"
    :target="isExternal ? '_blank' : undefined"
    :rel="isExternal ? 'noopener noreferrer' : undefined"
    class="link"
  >
    <slot />
    <template v-if="isExternal && showIcon">
      <span class="sr-only">(opens in new tab)</span>
      <ExternalLinkIcon class="h-4 w-4 inline ml-1" aria-hidden="true" />
    </template>
  </a>
</template>
```

### 1.3 Copy Protection for Sensitive Data (CWE-200)

**Principle:** Prevent accidental copying/sharing of sensitive information.

```vue
<script setup lang="ts">
const sensitiveValue = ref('');
const masked = computed(() => sensitiveValue.value.replace(/./g, '•'));
const isRevealed = ref(false);

function handleCopy(e: ClipboardEvent) {
  // Prevent copying masked value
  if (!isRevealed.value) {
    e.preventDefault();
    // Optionally copy the actual value
    navigator.clipboard.writeText(sensitiveValue.value);
  }
}
</script>

<template>
  <div class="relative">
    <input
      :value="isRevealed ? sensitiveValue : masked"
      readonly
      :aria-label="isRevealed ? 'API key (visible)' : 'API key (hidden)'"
      @copy="handleCopy"
    >
    <div class="absolute right-0 flex gap-2">
      <button
        :aria-label="isRevealed ? 'Hide' : 'Reveal'"
        @click="isRevealed = !isRevealed"
      >
        <EyeIcon v-if="!isRevealed" />
        <EyeOffIcon v-else />
      </button>
      <button
        aria-label="Copy to clipboard"
        @click="navigator.clipboard.writeText(sensitiveValue)"
      >
        <CopyIcon />
      </button>
    </div>
  </div>
</template>
```

---

## 2. Version Requirements

```
# Component libraries
@headlessui/vue>=1.7.0
@heroicons/vue>=2.1.0
# Animation
framer-motion>=11.0.0
# Testing
@testing-library/vue>=8.0.0
vitest>=1.2.0
```

---

## 3. Code Patterns

### WHEN building modals, implement focus trap and escape handling

```vue
<!-- ❌ WRONG - Focus escapes modal, no keyboard handling -->
<template>
  <div v-if="isOpen" class="modal-backdrop">
    <div class="modal">
      <slot />
      <button @click="close">Close</button>
    </div>
  </div>
</template>

<!-- ✅ CORRECT - Accessible modal with HeadlessUI -->
<script setup lang="ts">
import {
  Dialog,
  DialogPanel,
  DialogTitle,
  DialogDescription,
  TransitionRoot,
  TransitionChild,
} from '@headlessui/vue';

interface Props {
  open: boolean;
  title: string;
  description?: string;
}
const props = defineProps<Props>();
const emit = defineEmits<{
  close: [];
}>();
</script>

<template>
  <TransitionRoot :show="open" as="template">
    <Dialog
      :open="open"
      class="relative z-50"
      @close="emit('close')"
    >
      <!-- Backdrop -->
      <TransitionChild
        enter="ease-out duration-300"
        enter-from="opacity-0"
        enter-to="opacity-100"
        leave="ease-in duration-200"
        leave-from="opacity-100"
        leave-to="opacity-0"
      >
        <div class="fixed inset-0 bg-black/30" aria-hidden="true" />
      </TransitionChild>

      <!-- Full-screen container -->
      <div class="fixed inset-0 flex items-center justify-center p-4">
        <TransitionChild
          enter="ease-out duration-300"
          enter-from="opacity-0 scale-95"
          enter-to="opacity-100 scale-100"
          leave="ease-in duration-200"
          leave-from="opacity-100 scale-100"
          leave-to="opacity-0 scale-95"
        >
          <DialogPanel class="w-full max-w-md rounded-lg bg-white p-6 shadow-xl">
            <DialogTitle class="text-lg font-semibold">
              {{ title }}
            </DialogTitle>

            <DialogDescription v-if="description" class="mt-2 text-gray-600">
              {{ description }}
            </DialogDescription>

            <div class="mt-4">
              <slot />
            </div>

            <div class="mt-6 flex justify-end gap-3">
              <button
                class="btn btn-secondary"
                @click="emit('close')"
              >
                Cancel
              </button>
              <slot name="actions" />
            </div>
          </DialogPanel>
        </TransitionChild>
      </div>
    </Dialog>
  </TransitionRoot>
</template>
```

### WHEN implementing dropdowns, handle keyboard navigation

```vue
<!-- ❌ WRONG - No keyboard support -->
<template>
  <div @click="open = !open">
    <button>Menu</button>
    <div v-if="open">
      <a href="#">Item 1</a>
      <a href="#">Item 2</a>
    </div>
  </div>
</template>

<!-- ✅ CORRECT - Full keyboard navigation with HeadlessUI -->
<script setup lang="ts">
import { Menu, MenuButton, MenuItems, MenuItem } from '@headlessui/vue';

interface MenuItem {
  label: string;
  action: () => void;
  icon?: Component;
  danger?: boolean;
}

interface Props {
  items: MenuItem[];
  label?: string;
}
defineProps<Props>();
</script>

<template>
  <Menu as="div" class="relative">
    <MenuButton
      class="flex items-center gap-2 rounded-md px-3 py-2 hover:bg-gray-100"
    >
      <span class="sr-only">{{ label || 'Open menu' }}</span>
      <span v-if="$slots.default"><slot /></span>
      <ChevronDownIcon class="h-5 w-5" aria-hidden="true" />
    </MenuButton>

    <Transition
      enter-active-class="transition duration-100 ease-out"
      enter-from-class="transform scale-95 opacity-0"
      enter-to-class="transform scale-100 opacity-100"
      leave-active-class="transition duration-75 ease-in"
      leave-from-class="transform scale-100 opacity-100"
      leave-to-class="transform scale-95 opacity-0"
    >
      <MenuItems
        class="absolute right-0 mt-2 w-56 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black/5 focus:outline-none"
      >
        <div class="py-1">
          <MenuItem
            v-for="item in items"
            :key="item.label"
            v-slot="{ active }"
          >
            <button
              :class="[
                'flex w-full items-center gap-2 px-4 py-2 text-left text-sm',
                active ? 'bg-gray-100' : '',
                item.danger ? 'text-red-600' : 'text-gray-700',
              ]"
              @click="item.action"
            >
              <component
                :is="item.icon"
                v-if="item.icon"
                class="h-5 w-5"
                aria-hidden="true"
              />
              {{ item.label }}
            </button>
          </MenuItem>
        </div>
      </MenuItems>
    </Transition>
  </Menu>
</template>
```

### WHEN displaying data tables, implement proper semantics

```vue
<!-- ❌ WRONG - div soup, no semantics -->
<template>
  <div class="table">
    <div class="row header">
      <div>Name</div>
      <div>Email</div>
    </div>
    <div v-for="user in users" class="row">
      <div>{{ user.name }}</div>
      <div>{{ user.email }}</div>
    </div>
  </div>
</template>

<!-- ✅ CORRECT - Semantic table with accessibility -->
<script setup lang="ts">
interface Column<T> {
  key: keyof T;
  label: string;
  sortable?: boolean;
  align?: 'left' | 'center' | 'right';
}

interface Props<T> {
  columns: Column<T>[];
  data: T[];
  caption: string;
  sortBy?: keyof T;
  sortOrder?: 'asc' | 'desc';
}

const props = defineProps<Props<User>>();
const emit = defineEmits<{
  sort: [key: keyof User];
}>();
</script>

<template>
  <div class="overflow-x-auto">
    <table class="min-w-full divide-y divide-gray-200">
      <caption class="sr-only">{{ caption }}</caption>

      <thead class="bg-gray-50">
        <tr>
          <th
            v-for="column in columns"
            :key="String(column.key)"
            scope="col"
            :class="[
              'px-6 py-3 text-xs font-medium uppercase tracking-wider',
              column.align === 'right' ? 'text-right' : 'text-left',
            ]"
          >
            <button
              v-if="column.sortable"
              class="group inline-flex items-center gap-1"
              :aria-sort="
                sortBy === column.key
                  ? sortOrder === 'asc' ? 'ascending' : 'descending'
                  : 'none'
              "
              @click="emit('sort', column.key)"
            >
              {{ column.label }}
              <span class="flex-none rounded">
                <ChevronUpIcon
                  v-if="sortBy === column.key && sortOrder === 'asc'"
                  class="h-4 w-4"
                />
                <ChevronDownIcon
                  v-else-if="sortBy === column.key && sortOrder === 'desc'"
                  class="h-4 w-4"
                />
                <ChevronUpDownIcon
                  v-else
                  class="h-4 w-4 opacity-0 group-hover:opacity-100"
                />
              </span>
            </button>
            <span v-else>{{ column.label }}</span>
          </th>
        </tr>
      </thead>

      <tbody class="bg-white divide-y divide-gray-200">
        <tr
          v-for="(row, index) in data"
          :key="index"
          class="hover:bg-gray-50"
        >
          <td
            v-for="column in columns"
            :key="String(column.key)"
            :class="[
              'px-6 py-4 whitespace-nowrap text-sm',
              column.align === 'right' ? 'text-right' : 'text-left',
            ]"
          >
            <slot :name="column.key" :row="row" :value="row[column.key]">
              {{ row[column.key] }}
            </slot>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
```

### WHEN implementing toast notifications, use proper ARIA

```vue
<!-- ❌ WRONG - No live region, notifications missed by screen readers -->
<template>
  <div v-for="toast in toasts" class="toast">
    {{ toast.message }}
  </div>
</template>

<!-- ✅ CORRECT - Accessible toast system -->
<script setup lang="ts">
import { TransitionGroup } from 'vue';

interface Toast {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
}

const toasts = ref<Toast[]>([]);

function addToast(toast: Omit<Toast, 'id'>) {
  const id = crypto.randomUUID();
  toasts.value.push({ ...toast, id });

  if (toast.duration !== 0) {
    setTimeout(() => removeToast(id), toast.duration || 5000);
  }
}

function removeToast(id: string) {
  const index = toasts.value.findIndex(t => t.id === id);
  if (index !== -1) toasts.value.splice(index, 1);
}

// Expose for global access
defineExpose({ addToast, removeToast });
</script>

<template>
  <!-- Live region for screen reader announcements -->
  <div
    role="status"
    aria-live="polite"
    aria-atomic="true"
    class="sr-only"
  >
    <template v-for="toast in toasts" :key="toast.id">
      {{ toast.type }}: {{ toast.message }}
    </template>
  </div>

  <!-- Visual toasts -->
  <div
    aria-hidden="true"
    class="fixed bottom-4 right-4 z-50 flex flex-col gap-2"
  >
    <TransitionGroup
      enter-active-class="transition ease-out duration-300"
      enter-from-class="translate-x-full opacity-0"
      enter-to-class="translate-x-0 opacity-100"
      leave-active-class="transition ease-in duration-200"
      leave-from-class="translate-x-0 opacity-100"
      leave-to-class="translate-x-full opacity-0"
    >
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="[
          'flex items-center gap-3 rounded-lg px-4 py-3 shadow-lg',
          {
            'bg-green-50 text-green-800': toast.type === 'success',
            'bg-red-50 text-red-800': toast.type === 'error',
            'bg-yellow-50 text-yellow-800': toast.type === 'warning',
            'bg-blue-50 text-blue-800': toast.type === 'info',
          },
        ]"
      >
        <component
          :is="iconMap[toast.type]"
          class="h-5 w-5 flex-shrink-0"
        />
        <p class="text-sm font-medium">{{ toast.message }}</p>
        <button
          class="ml-auto flex-shrink-0 rounded p-1 hover:bg-black/5"
          @click="removeToast(toast.id)"
        >
          <XIcon class="h-4 w-4" />
          <span class="sr-only">Dismiss</span>
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>
```

---

## 4. Anti-Patterns

Do not:
- Use target="_blank" without rel="noopener noreferrer"
- Build modals without focus trap and escape key handling
- Create dropdowns without arrow key navigation
- Use divs for tables (semantic HTML matters)
- Display toast notifications outside of ARIA live regions
- Allow iframes on sensitive pages without CSP
- Copy sensitive data to clipboard without user action
- Skip loading/error states on async operations

---

## 5. Testing

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/vue';
import userEvent from '@testing-library/user-event';
import Modal from './Modal.vue';
import Dropdown from './Dropdown.vue';

describe('Modal', () => {
# ... (additional test cases follow same pattern)
```

---

## 6. Pre-Generation Checklist

Before generating UI component code:

- [ ] External links: rel="noopener noreferrer" on target="_blank"
- [ ] Modals: Focus trap, escape key, proper ARIA roles
- [ ] Dropdowns: Arrow key navigation, proper menu roles
- [ ] Tables: Semantic HTML (table, th, td), sortable columns with aria-sort
- [ ] Toasts: ARIA live region, auto-dismiss with undo option
- [ ] Frame protection: X-Frame-Options, CSP frame-ancestors
- [ ] Sensitive data: Copy protection, masked display
- [ ] Focus management: Visible focus indicators, logical tab order

---
