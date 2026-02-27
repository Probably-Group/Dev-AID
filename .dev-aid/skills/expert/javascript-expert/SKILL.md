---
name: javascript-expert
version: 2.0.0
description: "Modern JavaScript with ES6+ patterns, async/await, module systems, and Node.js best practices. Use when writing vanilla JS, working with promises, or building Node.js services. Do NOT use for TypeScript-specific features like generics or branded types (use typescript-expert)."
compatibility: "Node.js 18+, ES2022+"
risk_level: MEDIUM
token_budget: 3000
---
# JavaScript Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.2 Security Patterns (security rules)

**CWE-79: Cross-Site Scripting (XSS)**
- Do not: `element.innerHTML = userInput` or `document.write(userInput)`
- Instead: `element.textContent = userInput` or sanitize with DOMPurify

**CWE-1321: Prototype Pollution**
- Do not: `Object.assign(target, JSON.parse(userInput))` without validation
- Instead: Validate keys, use `Object.create(null)` for dictionaries, reject `__proto__`

**CWE-94: eval Injection**
- Do not: `eval(userInput)` or `new Function(userInput)()`
- Instead: Use JSON.parse for data, avoid dynamic code execution

**CWE-918: SSRF in Node.js**
- Do not: `fetch(userProvidedUrl)` without validation
- Instead: Allowlist domains, validate URL scheme (https only), block private IPs

**CWE-400: ReDoS (Regular Expression DoS)**
- Do not: Complex regex with user input: `new RegExp(userInput)`
- Instead: Sanitize regex special chars, use timeout, prefer simple patterns

---

## 1. Security Principles

### 1.1 XSS Prevention (CWE-79)

**Principle:** Never use innerHTML with untrusted data. Use textContent or sanitize.

```javascript
// ❌ WRONG - XSS vulnerability
element.innerHTML = userInput;

// ❌ WRONG - Still XSS
document.write(userInput);

// ✅ CORRECT - Safe text insertion
element.textContent = userInput;

// ✅ CORRECT - If HTML needed, sanitize
import DOMPurify from 'dompurify';
element.innerHTML = DOMPurify.sanitize(userInput);
```

### 1.2 Prototype Pollution (CWE-1321)

**Principle:** Never use user input as object keys directly.

```javascript
// ❌ WRONG - Prototype pollution
function merge(target, source) {
  for (const key in source) {
    target[key] = source[key];  // Can pollute __proto__
  }
}

// ✅ CORRECT - Safe merge
function safeMerge(target, source) {
  for (const key of Object.keys(source)) {
    if (key === '__proto__' || key === 'constructor' || key === 'prototype') {
      continue;
    }
    target[key] = source[key];
  }
}

// ✅ BETTER - Use Object.assign or spread
const merged = { ...target, ...source };
```

### 1.3 eval() and Function() (CWE-94)

**Principle:** Never use eval() or new Function() with user input.

### 1.4 Secrets ≠ Code (CWE-798)

**Principle:** Never expose secrets in client-side code. Use server-side proxies.

### 1.5 JSON Parsing (CWE-502)

**Principle:** Always try-catch JSON.parse. Validate parsed data.

### 1.6 URL Handling (CWE-601)

**Principle:** Validate URLs before redirects. Use allowlists for external links.

---

## 2. Version Requirements

Use these minimum versions:

```json
{
  "engines": {
    "node": ">=20.0.0"
  },
  "dependencies": {
    "zod": "^3.23.0"
  }
}
```

**Target:** ES2022+ for modern features.

---

## 3. Code Patterns

### 3.1 WHEN handling async operations

```javascript
// ❌ WRONG - Callback hell
getData(function(data) {
  processData(data, function(result) {
    saveResult(result, function(response) {
      console.log(response);
    });
  });
});

// ❌ WRONG - Missing error handling
async function fetchData() {
  const response = await fetch('/api/data');
  return response.json();
}

// ✅ CORRECT - Proper async/await with error handling
async function fetchData() {
  try {
    const response = await fetch('/api/data');

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Fetch failed:', error);
    throw error;
  }
}

// Promise.all for concurrent operations
async function fetchAllUsers(ids) {
  const results = await Promise.all(
    ids.map(id => fetchUser(id).catch(e => ({ error: e, id })))
  );

  const successes = results.filter(r => !r.error);
  const failures = results.filter(r => r.error);

  return { successes, failures };
}

// Promise.allSettled for graceful failure handling
async function fetchWithFallback(urls) {
  const results = await Promise.allSettled(
    urls.map(url => fetch(url).then(r => r.json()))
  );

  return results
    .filter(r => r.status === 'fulfilled')
    .map(r => r.value);
}
```

### 3.2 WHEN using modern array methods

```javascript
// ❌ WRONG - Mutating in map
const doubled = arr.map(x => {
  x.value *= 2;  // Mutates original!
  return x;
});

// ✅ CORRECT - Immutable operations
const doubled = arr.map(x => ({ ...x, value: x.value * 2 }));

// Chaining with proper error handling
const result = users
  .filter(user => user.active)
  .map(user => ({
    id: user.id,
    name: user.name,
    email: user.email,
  }))
  .sort((a, b) => a.name.localeCompare(b.name));

// reduce for complex transformations
const grouped = items.reduce((acc, item) => {
  const key = item.category;
  acc[key] = acc[key] ?? [];
  acc[key].push(item);
  return acc;
}, {});

// Object.groupBy (ES2024)
const grouped = Object.groupBy(items, item => item.category);

// flatMap for one-to-many transformations
const allTags = posts.flatMap(post => post.tags);

// at() for negative indexing
const last = array.at(-1);
const secondToLast = array.at(-2);
```

### 3.3 WHEN handling errors

```javascript
// ❌ WRONG - Swallowing errors
try {
  await riskyOperation();
} catch (e) {
  // Silent failure
}

// ❌ WRONG - Catching all, returning undefined
function getData() {
  try {
    return JSON.parse(input);
  } catch {
    return undefined;  // Caller doesn't know it failed
  }
}

// ✅ CORRECT - Custom error classes
class ValidationError extends Error {
  constructor(message, field) {
    super(message);
    this.name = 'ValidationError';
    this.field = field;
  }
}

class NotFoundError extends Error {
  constructor(resource, id) {
    super(`${resource} not found: ${id}`);
    this.name = 'NotFoundError';
    this.resource = resource;
    this.id = id;
  }
}

// ✅ CORRECT - Result pattern
function parseJson(input) {
  try {
    return { ok: true, value: JSON.parse(input) };
  } catch (error) {
    return { ok: false, error };
  }
}

// ✅ CORRECT - Error boundary with proper logging
async function handleRequest(req) {
  try {
    return await processRequest(req);
  } catch (error) {
    if (error instanceof ValidationError) {
      return { status: 400, body: { error: error.message, field: error.field } };
    }
    if (error instanceof NotFoundError) {
      return { status: 404, body: { error: error.message } };
    }

    // Log unexpected errors, don't expose details
    console.error('Unexpected error:', error);
    return { status: 500, body: { error: 'Internal server error' } };
  }
}
```

### 3.4 WHEN working with objects and data

```javascript
// ❌ WRONG - Mutating objects
function updateUser(user, updates) {
  user.name = updates.name;
  return user;
}

// ✅ CORRECT - Immutable updates
function updateUser(user, updates) {
  return { ...user, ...updates, updatedAt: new Date() };
}

// Deep cloning
const clone = structuredClone(original);

// Object.hasOwn (preferred over hasOwnProperty)
if (Object.hasOwn(obj, 'key')) {
  console.log(obj.key);
}

// Nullish coalescing and optional chaining
const name = user?.profile?.name ?? 'Anonymous';
const count = data.count ?? 0;  // Only null/undefined, not 0 or ''

// Object.fromEntries for transformations
const inverted = Object.fromEntries(
  Object.entries(obj).map(([k, v]) => [v, k])
);

// WeakMap for private data
const privateData = new WeakMap();

class User {
  constructor(name) {
    privateData.set(this, { secret: 'hidden' });
    this.name = name;
  }

  getSecret() {
    return privateData.get(this).secret;
  }
}
```

### 3.5 WHEN using ES modules

```javascript
// ❌ WRONG - require() in ESM
const fs = require('fs');

// ✅ CORRECT - ESM imports
import fs from 'node:fs/promises';
import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';

// Dynamic imports for code splitting
async function loadModule(name) {
  const module = await import(`./modules/${name}.js`);
  return module.default;
}

// Named exports (preferred)
export function processData(data) { /* ... */ }
export function validateData(data) { /* ... */ }

// Default export for main functionality
export default class DataProcessor {
  // ...
}

// Re-exports
export { processData as process } from './processor.js';
export * from './utils.js';
```

### 3.6 WHEN validating data

```javascript
import { z } from 'zod';

// Define schemas
const UserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  age: z.number().int().min(0).max(150),
  role: z.enum(['admin', 'user', 'guest']),
  preferences: z.object({
    theme: z.enum(['light', 'dark']).default('light'),
    notifications: z.boolean().default(true),
  }).optional(),
});

// Parse with validation
function createUser(input) {
  const user = UserSchema.parse(input);
  return user;
}

// Safe parse for error handling
function tryCreateUser(input) {
  const result = UserSchema.safeParse(input);

  if (!result.success) {
    return {
      ok: false,
      errors: result.error.issues.map(i => ({
        path: i.path.join('.'),
        message: i.message,
      })),
    };
  }

  return { ok: true, user: result.data };
}

// Transform and validate
const ApiResponseSchema = z.object({
  data: z.array(UserSchema),
  meta: z.object({
    total: z.number(),
    page: z.number(),
  }),
});

async function fetchUsers() {
  const response = await fetch('/api/users');
  const json = await response.json();
  return ApiResponseSchema.parse(json);
}
```

### 3.7 WHEN using Web APIs safely

```javascript
// Safe URL construction
function buildUrl(base, params) {
  const url = new URL(base);
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      url.searchParams.set(key, String(value));
    }
  });
  return url.toString();
}

// Safe redirect validation
const ALLOWED_DOMAINS = ['example.com', 'trusted.com'];

function safeRedirect(urlString) {
  try {
    const url = new URL(urlString);
    if (!ALLOWED_DOMAINS.includes(url.hostname)) {
      throw new Error('Redirect to untrusted domain blocked');
    }
    window.location.href = url.toString();
  } catch (error) {
    console.error('Invalid redirect URL:', error);
    window.location.href = '/';
  }
}

// AbortController for cancellation
async function fetchWithTimeout(url, timeout = 5000) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, { signal: controller.signal });
    return response;
  } finally {
    clearTimeout(timeoutId);
  }
}

// IntersectionObserver for lazy loading
function lazyLoadImages() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        observer.unobserve(img);
      }
    });
  });

  document.querySelectorAll('img[data-src]').forEach(img => {
    observer.observe(img);
  });
}
```

---

## 4. Anti-Patterns

Do not:
- Use `eval()` or `new Function()` with user input
- Use `innerHTML` with untrusted data
- Mutate function arguments
- Use `var` (use `const` or `let`)
- Use `==` (use `===`)
- Catch errors without handling them
- Use `for...in` on arrays (use `for...of`)
- Trust client-side validation alone

---

## 5. Testing

**ALWAYS write comprehensive tests:**

```javascript
import { describe, it, expect, vi } from 'vitest';

describe('fetchData', () => {
  it('returns parsed data on success', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ data: [1, 2, 3] }),
# ... (additional test cases follow same pattern)
```

---

## 6. Pre-Generation Checklist

Before generating any JavaScript code:

- [ ] No innerHTML with untrusted data
- [ ] No eval() or new Function() with user input
- [ ] All external data validated (Zod)
- [ ] Proper error handling (no silent catches)
- [ ] Immutable data patterns used
- [ ] Modern syntax (const/let, arrow functions, etc.)
- [ ] AbortController for cancellable requests
- [ ] URL validation for redirects
- [ ] Object property access safety (?., ??)
- [ ] No prototype pollution vectors

---
