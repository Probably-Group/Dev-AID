---
name: vue3
version: 2.0.0
description: "Vue 3 Composition API patterns with reactivity, composables, provide/inject, and XSS prevention."
risk_level: MEDIUM
---

# Vue 3 - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-79: XSS via v-html**
- NEVER: `<div v-html="userContent"></div>` with untrusted data
- ALWAYS: `<div>{{ userContent }}</div>` (auto-escaped) or sanitize with DOMPurify

**CWE-20: Props Validation**
- NEVER: Trust props at runtime - TypeScript types are compile-time only
- ALWAYS: Runtime validation with Zod in `onMounted` for external data

**CWE-200: Secrets Exposure**
- NEVER: `const API_KEY = import.meta.env.VITE_SECRET` - bundled into client JS
- ALWAYS: Secrets on server only, use API routes for sensitive operations

**CWE-352: CSRF**
- NEVER: State-changing requests without CSRF protection
- ALWAYS: Include CSRF token in headers for mutations, validate server-side

### 0.3 Risk Level: MEDIUM

**Verification requirements for MEDIUM risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 XSS Prevention (CWE-79)

**Principle:** Never use v-html with untrusted data. Vue auto-escapes text interpolation.

```vue
<!-- ❌ WRONG - XSS vulnerability -->
<div v-html="userContent"></div>

<!-- ✅ CORRECT - Auto-escaped -->
<div>{{ userContent }}</div>

<!-- ✅ CORRECT - Sanitize if HTML needed -->
<script setup lang="ts">
import DOMPurify from 'dompurify';

const props = defineProps<{ rawHtml: string }>();
const sanitizedHtml = computed(() =>
  DOMPurify.sanitize(props.rawHtml, {
    ALLOWED_TAGS: ['p', 'b', 'i', 'em', 'strong', 'a'],
    ALLOWED_ATTR: ['href', 'title'],
  })
);
</script>

<template>
  <div v-html="sanitizedHtml" />
</template>
```

### 1.2 Props Validation (CWE-20)

**Principle:** Always validate props with runtime type checking. TypeScript types are compile-time only.

```typescript
// ❌ WRONG - No runtime validation
const props = defineProps<{
  userId: string;
  role: 'admin' | 'user';
}>();
// Props could be anything at runtime!

// ✅ CORRECT - Runtime validation with Zod
import { z } from 'zod';

const PropsSchema = z.object({
  userId: z.string().uuid(),
  role: z.enum(['admin', 'user']),
});

const props = defineProps<z.infer<typeof PropsSchema>>();

// Validate in onMounted or watch
onMounted(() => {
  const result = PropsSchema.safeParse(props);
  if (!result.success) {
    console.error('Invalid props:', result.error);
  }
});
```

### 1.3 Event Payload Security (CWE-20)

**Principle:** Validate data emitted from child components before using it.

```typescript
// ❌ WRONG - Trusting emitted data
// Parent.vue
<ChildForm @submit="handleSubmit" />

function handleSubmit(data: FormData) {
  // data could be manipulated!
  api.post('/users', data);
}

// ✅ CORRECT - Validate emitted data
import { z } from 'zod';

const FormDataSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
});

function handleSubmit(data: unknown) {
  const result = FormDataSchema.safeParse(data);
  if (!result.success) {
    console.error('Invalid form data');
    return;
  }
  api.post('/users', result.data);
}
```

### 1.4 Secrets ≠ Code (CWE-798)

**Principle:** Never expose secrets in client-side Vue code. All env vars are bundled.

```typescript
// ❌ WRONG - Secret exposed to client
const API_KEY = import.meta.env.VITE_API_KEY;
// This is bundled into JS and visible in browser!

// ✅ CORRECT - Secrets only on server
// Use API routes or backend proxy for sensitive operations
async function fetchData() {
  // Call your own backend, which has the secret
  return fetch('/api/data');
}
```

---

## 2. Version Requirements

```json
{
  "dependencies": {
    "vue": "^3.5.0",
    "vue-router": "^4.4.0",
    "pinia": "^2.2.0",
    "zod": "^3.23.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "typescript": "^5.4.0",
    "@vue/test-utils": "^2.4.0",
    "vitest": "^2.0.0"
  }
}
```

---

## 3. Code Patterns

### WHEN using Composition API, follow conventions

```vue
<!-- ❌ WRONG - Mixed patterns, no organization -->
<script setup lang="ts">
const count = ref(0);
function increment() { count.value++; }
const user = ref(null);
const doubled = computed(() => count.value * 2);
async function fetchUser() { /* ... */ }
const name = ref('');
</script>

<!-- ✅ CORRECT - Organized by concern -->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { z } from 'zod';

// Props & Emits
const props = defineProps<{
  initialCount?: number;
}>();

const emit = defineEmits<{
  change: [count: number];
}>();

// Reactive state
const count = ref(props.initialCount ?? 0);
const user = ref<User | null>(null);
const loading = ref(false);
const error = ref<string | null>(null);

// Computed
const doubled = computed(() => count.value * 2);
const isValid = computed(() => count.value >= 0);

// Methods
function increment() {
  count.value++;
  emit('change', count.value);
}

async function fetchUser(id: string) {
  loading.value = true;
  error.value = null;
  try {
    const response = await fetch(`/api/users/${id}`);
    user.value = await response.json();
  } catch (e) {
    error.value = 'Failed to fetch user';
  } finally {
    loading.value = false;
  }
}

// Lifecycle
onMounted(() => {
  fetchUser('123');
});
</script>
```

### WHEN creating composables, ensure proper cleanup

```typescript
// ❌ WRONG - No cleanup, memory leak
// composables/useWindowSize.ts
export function useWindowSize() {
  const width = ref(window.innerWidth);
  const height = ref(window.innerHeight);

  window.addEventListener('resize', () => {
    width.value = window.innerWidth;
    height.value = window.innerHeight;
  });
  // Listener never removed!

  return { width, height };
}

// ✅ CORRECT - Proper cleanup with onUnmounted
import { ref, onMounted, onUnmounted, readonly } from 'vue';

export function useWindowSize() {
  const width = ref(window.innerWidth);
  const height = ref(window.innerHeight);

  function onResize() {
    width.value = window.innerWidth;
    height.value = window.innerHeight;
  }

  onMounted(() => {
    window.addEventListener('resize', onResize);
  });

  onUnmounted(() => {
    window.removeEventListener('resize', onResize);
  });

  return { width: readonly(width), height: readonly(height) };
}
```

### WHEN using reactive objects, avoid reactivity loss

```typescript
// ❌ WRONG - Reactivity lost through destructuring
const state = reactive({ count: 0, name: 'Vue' });
const { count } = state;  // count is now a plain number!

// ❌ WRONG - Replacing reactive object
let state = reactive({ count: 0 });
state = reactive({ count: 1 });  // Components won't update!

// ✅ CORRECT - Use toRefs for destructuring
const state = reactive({ count: 0, name: 'Vue' });
const { count, name } = toRefs(state);  // count is Ref<number>

// ✅ CORRECT - Or just use ref for primitive values
const count = ref(0);
const name = ref('Vue');
```

### WHEN defining emits, use typed emit

```vue
<!-- ❌ WRONG - Untyped emits -->
<script setup>
const emit = defineEmits(['update', 'delete']);
emit('update', { id: 1 });  // No type checking!
</script>

<!-- ✅ CORRECT - Typed emits with validation -->
<script setup lang="ts">
const emit = defineEmits<{
  update: [payload: { id: number; data: Record<string, unknown> }];
  delete: [id: number];
}>();

// TypeScript enforces correct payload
emit('update', { id: 1, data: { name: 'test' } });
emit('delete', 123);
</script>
```

### WHEN using provide/inject, ensure type safety

```typescript
// ❌ WRONG - No type safety
// Parent
provide('user', user);

// Child
const user = inject('user');  // Type is unknown

// ✅ CORRECT - Type-safe provide/inject with InjectionKey
import { type InjectionKey, type Ref, provide, inject, ref } from 'vue';

interface User {
  id: string;
  name: string;
}

// Define key with type
const UserKey: InjectionKey<Ref<User | null>> = Symbol('user');

// Parent
const user = ref<User | null>(null);
provide(UserKey, user);

// Child
const user = inject(UserKey);  // Type is Ref<User | null> | undefined

// With default value
const user = inject(UserKey, ref(null));  // Type is Ref<User | null>
```

### WHEN handling async state, use proper loading patterns

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue';

// State machine for async operations
type AsyncState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: Error };

const userState = ref<AsyncState<User>>({ status: 'idle' });

async function fetchUser(id: string) {
  userState.value = { status: 'loading' };

  try {
    const response = await fetch(`/api/users/${id}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const data = await response.json();
    userState.value = { status: 'success', data };
  } catch (e) {
    userState.value = {
      status: 'error',
      error: e instanceof Error ? e : new Error(String(e)),
    };
  }
}

onMounted(() => fetchUser('123'));
</script>

<template>
  <div v-if="userState.status === 'loading'">Loading...</div>
  <div v-else-if="userState.status === 'error'" class="error">
    {{ userState.error.message }}
  </div>
  <div v-else-if="userState.status === 'success'">
    <h1>{{ userState.data.name }}</h1>
  </div>
</template>
```

### WHEN using v-model, implement proper two-way binding

```vue
<!-- ❌ WRONG - Mutating props directly -->
<script setup>
const props = defineProps(['modelValue']);
function update(e) {
  props.modelValue = e.target.value;  // Error!
}
</script>

<!-- ✅ CORRECT - Proper v-model implementation -->
<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  modelValue: string;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: string];
}>();

// Computed with getter/setter for v-model
const model = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
});
</script>

<template>
  <input v-model="model" />
</template>

<!-- Usage in parent -->
<!-- <CustomInput v-model="username" /> -->
```

---

## 4. Anti-Patterns

**NEVER:**
- Use v-html with untrusted user content
- Destructure reactive objects without toRefs
- Forget cleanup in composables (event listeners, timers)
- Expose secrets in client-side code
- Skip runtime validation of props/emits
- Mutate props directly
- Use provide/inject without InjectionKey

---

## 5. Testing

```typescript
import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { ref, nextTick } from 'vue';
import UserCard from './UserCard.vue';

describe('UserCard', () => {
  it('renders user name', () => {
    const wrapper = mount(UserCard, {
      props: {
        user: { id: '1', name: 'John', email: 'john@example.com' },
      },
    });

    expect(wrapper.text()).toContain('John');
  });

  it('emits delete event with user id', async () => {
    const wrapper = mount(UserCard, {
      props: {
        user: { id: '123', name: 'John', email: 'john@example.com' },
      },
    });

    await wrapper.find('[data-testid="delete-btn"]').trigger('click');

    expect(wrapper.emitted('delete')).toEqual([['123']]);
  });

  it('handles loading state', async () => {
    const wrapper = mount(UserCard, {
      props: {
        user: null,
        loading: true,
      },
    });

    expect(wrapper.find('.skeleton').exists()).toBe(true);
  });
});

// Testing composables
import { useWindowSize } from './useWindowSize';

describe('useWindowSize', () => {
  it('returns current window dimensions', () => {
    const { width, height } = useWindowSize();

    expect(width.value).toBe(window.innerWidth);
    expect(height.value).toBe(window.innerHeight);
  });

  it('updates on resize', async () => {
    const { width } = useWindowSize();

    // Simulate resize
    window.innerWidth = 800;
    window.dispatchEvent(new Event('resize'));

    await nextTick();
    expect(width.value).toBe(800);
  });
});
```

---

## 6. Pre-Generation Checklist

**BEFORE generating Vue 3 code:**

- [ ] XSS: No v-html with untrusted content, use DOMPurify if needed
- [ ] Props: Runtime validation with Zod for external data
- [ ] Emits: Typed with proper payload validation
- [ ] Reactivity: No destructuring reactive objects without toRefs
- [ ] Composables: Cleanup in onUnmounted (listeners, timers)
- [ ] Provide/Inject: Using InjectionKey for type safety
- [ ] Async state: Proper loading/error/success states
- [ ] v-model: Proper emit pattern, no prop mutation
- [ ] Secrets: Never in client-side code
- [ ] Tests: Cover props, emits, and composables
