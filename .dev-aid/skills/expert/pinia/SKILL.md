---
name: pinia
version: 2.0.0
description: "Pinia state management for Vue 3 with typed stores, plugins, and SSR hydration patterns. Use when managing Vue application state, creating stores, or handling SSR hydration. Do NOT use for Vuex, Redux, or non-Vue state management."
compatibility: "Vue 3.3+, Pinia 2.1+"
risk_level: LOW
---

# Pinia Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-200: Sensitive Data in Store**
- NEVER: Store secrets/tokens in Pinia state (visible in devtools, SSR serialization)
- ALWAYS: Use httpOnly cookies for auth, keep secrets server-side

**CWE-20: Action Input Validation**
- NEVER: Trust action parameters: `setUser(userData: User)`
- ALWAYS: Validate in action: `setUser(data: unknown) { const user = UserSchema.parse(data) }`

**CWE-352: CSRF in Actions**
- NEVER: Mutation actions without CSRF protection
- ALWAYS: Include CSRF token in API calls from actions

### 0.3 Risk Level: LOW

**Verification requirements for LOW risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 State Isolation (CWE-200)

**Principle:** Never expose sensitive data in state. Keep auth tokens in secure storage.

```typescript
// ❌ WRONG - Sensitive data in state
export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref('');  // Exposed in devtools!
  const password = ref('');     // NEVER store passwords
});

// ✅ CORRECT - Sensitive data in secure storage only
export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null);
  const isAuthenticated = computed(() => !!user.value);

  // Token stored in httpOnly cookie or secure storage
  // Only store non-sensitive user info in state
});
```

### 1.2 Input Validation (CWE-20)

**Principle:** Validate data before storing in state. Use Zod for runtime validation.

```typescript
import { z } from 'zod';

const UserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  role: z.enum(['user', 'admin']),
});

// ❌ WRONG - No validation
function setUser(data: unknown) {
  user.value = data as User;  // Trusting unknown data!
}

// ✅ CORRECT - Validate before storing
function setUser(data: unknown) {
  const result = UserSchema.safeParse(data);
  if (result.success) {
    user.value = result.data;
  } else {
    console.error('Invalid user data');
    user.value = null;
  }
}
```

### 1.3 XSS Prevention (CWE-79)

**Principle:** Never use v-html with state data. Sanitize user-generated content.

### 1.4 Secrets ≠ Code (CWE-798)

**Principle:** Never store API keys in state. Use environment variables server-side.

### 1.5 Fail Secure (CWE-636)

**Principle:** On hydration errors, clear state. Default to logged-out state.

### 1.6 Defense in Depth

**Principle:** Validate on input AND output. Don't trust hydrated state.

---

## 2. Version Requirements

**ALWAYS use these minimum versions:**

```json
{
  "dependencies": {
    "pinia": "^2.1.0",
    "vue": "^3.4.0",
    "zod": "^3.22.0",
    "pinia-plugin-persistedstate": "^3.2.0"
  }
}
```

---

## 3. Code Patterns

### 3.1 WHEN creating a Pinia store with Composition API

```typescript
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { z } from 'zod';

// Schema for validation
const TodoSchema = z.object({
  id: z.string().uuid(),
  title: z.string().min(1).max(200),
  completed: z.boolean(),
  createdAt: z.string().datetime(),
});

type Todo = z.infer<typeof TodoSchema>;

export const useTodoStore = defineStore('todo', () => {
  // State
  const todos = ref<Todo[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Getters (computed)
  const completedTodos = computed(() =>
    todos.value.filter(t => t.completed)
  );

  const pendingTodos = computed(() =>
    todos.value.filter(t => !t.completed)
  );

  const todoCount = computed(() => todos.value.length);

  // Actions
  async function fetchTodos() {
    loading.value = true;
    error.value = null;

    try {
      const response = await fetch('/api/todos');
      if (!response.ok) throw new Error('Failed to fetch');

      const data = await response.json();

      // Validate response data
      const validated = z.array(TodoSchema).safeParse(data);
      if (validated.success) {
        todos.value = validated.data;
      } else {
        throw new Error('Invalid data format');
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Unknown error';
      todos.value = [];  // Fail secure - clear state
    } finally {
      loading.value = false;
    }
  }

  function addTodo(title: string) {
    // Validate input
    const trimmed = title.trim();
    if (!trimmed || trimmed.length > 200) {
      error.value = 'Invalid title';
      return;
    }

    const newTodo: Todo = {
      id: crypto.randomUUID(),
      title: trimmed,
      completed: false,
      createdAt: new Date().toISOString(),
    };

    todos.value.push(newTodo);
  }

  function toggleTodo(id: string) {
    const todo = todos.value.find(t => t.id === id);
    if (todo) {
      todo.completed = !todo.completed;
    }
  }

  function removeTodo(id: string) {
    const index = todos.value.findIndex(t => t.id === id);
    if (index !== -1) {
      todos.value.splice(index, 1);
    }
  }

  function $reset() {
    todos.value = [];
    loading.value = false;
    error.value = null;
  }

  return {
    // State
    todos,
    loading,
    error,
    // Getters
    completedTodos,
    pendingTodos,
    todoCount,
    // Actions
    fetchTodos,
    addTodo,
    toggleTodo,
    removeTodo,
    $reset,
  };
});
```

### 3.2 WHEN implementing authentication store

```typescript
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { z } from 'zod';

const UserSchema = z.object({
  id: z.string(),
  email: z.string().email(),
  name: z.string(),
  role: z.enum(['user', 'admin']),
});

type User = z.infer<typeof UserSchema>;

export const useAuthStore = defineStore('auth', () => {
  // State - NEVER store tokens here, only non-sensitive user info
  const user = ref<User | null>(null);
  const loading = ref(false);

  // Getters
  const isAuthenticated = computed(() => !!user.value);
  const isAdmin = computed(() => user.value?.role === 'admin');

  // Actions
  async function login(email: string, password: string) {
    loading.value = true;

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',  // httpOnly cookies
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        throw new Error('Invalid credentials');
      }

      const data = await response.json();

      // Validate user data
      const result = UserSchema.safeParse(data.user);
      if (result.success) {
        user.value = result.data;
      } else {
        throw new Error('Invalid user data');
      }
    } catch (e) {
      user.value = null;  // Fail secure
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function logout() {
    try {
      await fetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'include',
      });
    } finally {
      // Always clear state, even on error
      user.value = null;
    }
  }

  async function checkAuth() {
    try {
      const response = await fetch('/api/auth/me', {
        credentials: 'include',
      });

      if (!response.ok) {
        user.value = null;
        return;
      }

      const data = await response.json();
      const result = UserSchema.safeParse(data);
      user.value = result.success ? result.data : null;
    } catch {
      user.value = null;
    }
  }

  return {
    user,
    loading,
    isAuthenticated,
    isAdmin,
    login,
    logout,
    checkAuth,
  };
});
```

### 3.3 WHEN using store persistence

```typescript
import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useSettingsStore = defineStore('settings', () => {
  const theme = ref<'light' | 'dark'>('light');
  const locale = ref('en');
  const sidebarCollapsed = ref(false);

  function setTheme(newTheme: 'light' | 'dark') {
    theme.value = newTheme;
  }

  function setLocale(newLocale: string) {
    // Validate locale
    const validLocales = ['en', 'es', 'fr', 'de'];
    if (validLocales.includes(newLocale)) {
      locale.value = newLocale;
    }
  }

  return {
    theme,
    locale,
    sidebarCollapsed,
    setTheme,
    setLocale,
  };
}, {
  persist: {
    key: 'app-settings',
    storage: localStorage,
    // Only persist non-sensitive data
    paths: ['theme', 'locale', 'sidebarCollapsed'],
  },
});
```

### 3.4 WHEN composing stores

```typescript
import { defineStore, storeToRefs } from 'pinia';
import { useAuthStore } from './auth';
import { computed } from 'vue';

export const useCartStore = defineStore('cart', () => {
  const authStore = useAuthStore();
  const { user, isAuthenticated } = storeToRefs(authStore);

  const items = ref<CartItem[]>([]);

  // Access auth state reactively
  const canCheckout = computed(() =>
    isAuthenticated.value && items.value.length > 0
  );

  async function checkout() {
    if (!canCheckout.value) {
      throw new Error('Cannot checkout');
    }

    // Use user info from auth store
    const userId = user.value?.id;
    // ... checkout logic
  }

  return {
    items,
    canCheckout,
    checkout,
  };
});
```

### 3.5 WHEN testing Pinia stores

```typescript
import { setActivePinia, createPinia } from 'pinia';
import { describe, beforeEach, it, expect, vi } from 'vitest';
import { useTodoStore } from './todo';

describe('Todo Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it('adds todo with valid input', () => {
    const store = useTodoStore();

    store.addTodo('Test todo');

    expect(store.todos).toHaveLength(1);
    expect(store.todos[0].title).toBe('Test todo');
    expect(store.todos[0].completed).toBe(false);
  });

  it('rejects invalid todo title', () => {
    const store = useTodoStore();

    store.addTodo('');  // Empty
    expect(store.todos).toHaveLength(0);
    expect(store.error).toBe('Invalid title');

    store.addTodo('a'.repeat(201));  // Too long
    expect(store.todos).toHaveLength(0);
  });

  it('validates fetched data', async () => {
    const store = useTodoStore();

    // Mock invalid response
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve([{ invalid: 'data' }]),
    });

    await store.fetchTodos();

    expect(store.todos).toHaveLength(0);
    expect(store.error).toBe('Invalid data format');
  });

  it('handles fetch errors securely', async () => {
    const store = useTodoStore();
    store.todos = [{ id: '1', title: 'Test', completed: false, createdAt: '' }];

    global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));

    await store.fetchTodos();

    expect(store.todos).toHaveLength(0);  // Cleared on error
    expect(store.error).toBe('Network error');
  });
});
```

---

## 4. Anti-Patterns

**NEVER:**
- Store sensitive data (tokens, passwords) in Pinia state
- Trust hydrated/persisted state without validation
- Use `any` type in store definitions
- Mutate state directly outside actions
- Skip validation on API responses
- Expose internal state without getters

---

## 5. Testing

**ALWAYS write store tests:**

```typescript
import { setActivePinia, createPinia } from 'pinia';
import { beforeEach, it, expect } from 'vitest';

describe('Auth Store Security', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it('clears state on logout even if API fails', async () => {
    const store = useAuthStore();
    store.user = { id: '1', email: 'test@test.com', name: 'Test', role: 'user' };

    global.fetch = vi.fn().mockRejectedValue(new Error('API error'));

    await store.logout();

    expect(store.user).toBeNull();
    expect(store.isAuthenticated).toBe(false);
  });

  it('validates user data from API', async () => {
    const store = useAuthStore();

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ user: { id: '1', email: 'invalid' } }),
    });

    await expect(store.login('test@test.com', 'password'))
      .rejects.toThrow('Invalid user data');

    expect(store.user).toBeNull();
  });
});
```

---

## 6. Pre-Generation Checklist

**BEFORE generating any Pinia code:**

- [ ] No sensitive data (tokens, passwords) in state
- [ ] Input validation on all action parameters
- [ ] API response validation with Zod
- [ ] Fail secure - clear state on errors
- [ ] Proper TypeScript types (no `any`)
- [ ] Computed getters for derived state
- [ ] Persistence only for non-sensitive data
- [ ] Tests for validation and error handling
- [ ] storeToRefs for reactive destructuring
- [ ] $reset function for clearing state

---

**Performance**: Quality over speed. Verify all code examples compile. Never skip security checks. See `template-references/performance-notes.md` for full guidelines.