#!/usr/bin/env bash
# Preset: Svelte 5 + SvelteKit 2

preset_name="svelte-kit"
preset_description="Svelte 5 with runes, SvelteKit 2+, TypeScript, and file-based routing"

# Rules files: newline-delimited "filename|description" pairs
RULES_FILES="components.md|Svelte 5 runes (\$state, \$derived, \$effect, \$props, \$bindable), snippets, component composition
routing.md|SvelteKit file routing, load functions, form actions, hooks, error/redirect handling
cross-service.md|TypeScript patterns, environment variables, error handling, adapter configuration"

# Technology stack entries
TECH_STACK="| Frontend | Svelte 5, SvelteKit 2+, TypeScript 5+ |
| Styling | *Tailwind CSS / UnoCSS / vanilla CSS* |
| Testing | Vitest, @testing-library/svelte, Playwright |
| Linting | ESLint (eslint-plugin-svelte), Prettier (prettier-plugin-svelte) |
| Build | Vite |
| Package Manager | *pnpm / npm / bun* |"

# Context loading table entries
CONTEXT_LOADING_TABLE="| **New component** | \`.claude/rules/components.md\`, \`src/lib/components/\` |
| **New page / route** | \`.claude/rules/routing.md\`, \`src/routes/\` |
| **Form action** | \`.claude/rules/routing.md\` (Form Actions), \`src/routes/\` |
| **Server load function** | \`.claude/rules/routing.md\` (Load Functions), \`src/routes/\` |
| **Debugging** | \`.claude/rules/troubleshooting.md\` |
| **Architecture decisions** | \`docs/decisions/index.md\` |
| **Shared utilities** | \`.claude/rules/cross-service.md\`, \`src/lib/\` |"

# Context groups
CONTEXT_GROUPS='### `components`
Read: `.claude/rules/components.md`, `src/lib/components/`

### `routing`
Read: `.claude/rules/routing.md`, `src/routes/`

### `lib`
Read: `.claude/rules/cross-service.md`, `src/lib/`, `src/lib/server/`

### `config`
Read: `svelte.config.js`, `vite.config.ts`, `tsconfig.json`, `package.json`

### `debug`
Read: `.claude/rules/troubleshooting.md`'

# Development workflow
WORKFLOW='```bash
# Setup
pnpm install  # or: npm install / bun install

# Run dev server
pnpm dev  # http://localhost:5173

# Build for production
pnpm build

# Preview production build
pnpm preview

# Run tests
pnpm test          # Vitest unit tests
pnpm test:e2e      # Playwright E2E tests

# Lint & format
pnpm lint          # ESLint
pnpm format        # Prettier

# Type check
pnpm check         # svelte-check (svelte + TS diagnostics)

# SvelteKit utilities
npx svelte-kit sync   # Regenerate types from routes/config
```

### Dev Tools

- **Svelte Inspector:** Ctrl+Shift+I in dev to click-to-source on components
- **Svelte DevTools:** Browser extension for component tree and state'

# Project overview
PROJECT_OVERVIEW="SvelteKit 2 application with Svelte 5 runes, TypeScript, and server-side rendering."

# Workspace structure
WORKSPACE_STRUCTURE='{{PROJECT_NAME}}/
├── CLAUDE.md
├── .claude/
│   ├── rules/
│   │   ├── components.md
│   │   ├── routing.md
│   │   ├── cross-service.md
│   │   └── troubleshooting.md
│   ├── hooks/
│   │   └── lint-on-edit.sh
│   ├── memory/
│   │   ├── MEMORY.md
│   │   ├── component-patterns.md
│   │   ├── routing-gotchas.md
│   │   └── debugging.md
│   └── commands/
│       ├── review.md
│       ├── test.md
│       ├── plan.md
│       ├── smoke.md
│       ├── lint.md
│       └── typecheck.md
├── svelte.config.js
├── vite.config.ts
├── src/
│   ├── app.html
│   ├── app.d.ts
│   ├── hooks.server.ts
│   ├── routes/
│   │   ├── +layout.svelte
│   │   ├── +page.svelte
│   │   ├── +page.server.ts
│   │   ├── +error.svelte
│   │   └── api/
│   │       └── health/
│   │           └── +server.ts
│   └── lib/
│       ├── components/
│       ├── server/
│       ├── stores/
│       ├── utils/
│       └── index.ts
├── static/
├── tests/
├── docs/
│   ├── plans/
│   │   └── .plan-template.md
│   └── decisions/
│       ├── index.md
│       └── adr-template.md
├── scripts/
│   └── smoke-sveltekit.sh
├── package.json
└── tsconfig.json'

# Smoke test scripts: "filename|title|checks_variable_name"
SMOKE_SCRIPTS="smoke-sveltekit.sh|SvelteKit Application Health Checks|SMOKE_SVELTEKIT_CHECKS"

# shellcheck disable=SC2034
SMOKE_SVELTEKIT_CHECKS='section "Application"

if [[ -f "svelte.config.js" ]]; then
  pass "svelte.config.js exists"
else
  fail "svelte.config.js not found"
fi

if [[ -f "src/app.html" ]]; then
  pass "src/app.html exists"
else
  fail "src/app.html not found — SvelteKit entry point missing"
fi

if [[ -f "src/routes/+page.svelte" ]]; then
  pass "Root page exists (src/routes/+page.svelte)"
else
  warn "No root page — src/routes/+page.svelte not found"
fi

if [[ -f "package.json" ]]; then
  pass "package.json exists"
else
  fail "package.json not found"
fi

section "Dependencies"

if [[ -d "node_modules" ]]; then
  pass "node_modules exists"
else
  fail "node_modules missing — run pnpm install"
fi

if [[ -d "node_modules/@sveltejs/kit" ]]; then
  pass "@sveltejs/kit is installed"
else
  fail "@sveltejs/kit not found in node_modules"
fi

section "Type Generation"

if npx svelte-kit sync 2>/dev/null; then
  pass "svelte-kit sync succeeds (types generated)"
else
  warn "svelte-kit sync failed — route types may be stale"
fi

section "Type Checking"

if npx svelte-check --threshold error 2>/dev/null; then
  pass "svelte-check passes without errors"
else
  warn "svelte-check has errors — run pnpm check"
fi

section "Build"

if pnpm build 2>/dev/null; then
  pass "Vite build succeeds"
else
  warn "Build has errors"
fi

section "Linting"

if npx eslint --quiet src/ 2>/dev/null; then
  pass "ESLint passes"
else
  warn "ESLint has findings"
fi

section "Tests"

if npx vitest --run --reporter=silent 2>/dev/null; then
  pass "Unit tests pass"
else
  warn "Unit tests failing or not found"
fi'

# Troubleshooting sections
TROUBLESHOOTING_SECTIONS='## 1. Svelte 5 Runes

### Symptom: `$state is not defined` or `$derived is not defined` at runtime

**Diagnosis:** Runes are compiler directives, not runtime functions. They only work
inside `.svelte` files or `.svelte.ts`/`.svelte.js` files. Plain `.ts` files fail.

**Fix:**
```bash
# Rename to .svelte.ts extension
mv src/lib/stores/counter.ts src/lib/stores/counter.svelte.ts
```
```typescript
// src/lib/stores/counter.svelte.ts  <-- must be .svelte.ts
export function createCounter() {
  let count = $state(0)
  const doubled = $derived(count * 2)
  return {
    get count() { return count },
    get doubled() { return doubled },
    increment() { count++ },
  }
}
```

---

### Symptom: `Cannot use $state as a variable declaration`

**Diagnosis:** Svelte compiler not processing the file. Either `svelte.config.js` is
misconfigured or Svelte 4 is installed instead of Svelte 5.

**Fix:**
```bash
pnpm list svelte          # Should show svelte@5.x.x
npx svelte-kit sync       # Regenerate types
```

---

## 2. Routing / Load Functions

### Symptom: Load function data is `undefined` in the page component

**Diagnosis:** Load function must return a plain object (not a Response). Or the page
is not accessing `data` correctly with `$props()`.

**Fix:**
```typescript
// +page.server.ts
export const load: PageServerLoad = async ({ params }) => {
  const item = await db.items.findUnique({ where: { id: params.id } })
  if (!item) error(404, "Item not found")
  return { item }  // Plain object, not Response
}
```
```svelte
<!-- +page.svelte -->
<script lang="ts">
  let { data }: { data: PageData } = $props()
</script>
<h1>{data.item.name}</h1>
```

---

### Symptom: Form action succeeds but page data is stale

**Diagnosis:** Custom `use:enhance` callback does not call `update()`, so SvelteKit
does not re-run load functions after the action.

**Fix:**
```svelte
<form method="POST" action="?/create" use:enhance={() => {
  return async ({ result, update }) => {
    if (result.type === "success") await update()
  }
}}>
```

---

## 3. Build / Deployment

### Symptom: `Could not detect a supported production environment`

**Diagnosis:** Missing SvelteKit adapter.

**Fix:**
```bash
pnpm add -D @sveltejs/adapter-node    # or adapter-auto, adapter-static
```
```javascript
// svelte.config.js
import adapter from "@sveltejs/adapter-node"
export default { kit: { adapter: adapter({ out: "build" }) } }
```

---

## 4. TypeScript

### Symptom: `Cannot find module "./$types"` in load functions

**Diagnosis:** Route types not generated. `.svelte-kit/types/` is missing or stale.

**Fix:**
```bash
npx svelte-kit sync
# If still missing: rm -rf .svelte-kit && pnpm install && npx svelte-kit sync
# Ensure tsconfig.json: { "extends": "./.svelte-kit/tsconfig.json" }
```

---

*Add entries as you encounter and solve issues. Use the Symptom -> Diagnosis -> Fix format.*'

# Memory topics: "filename|description" pairs
MEMORY_TOPICS="component-patterns.md|Rune patterns, component composition, snippet conventions
routing-gotchas.md|Load function issues, form action edge cases, hook patterns
debugging.md|Common errors encountered and their solutions"

# Slash commands to scaffold
COMMANDS="review.md
test.md
plan.md
smoke.md
lint.md
typecheck.md"

# --- Substantive Rules Content ---

# shellcheck disable=SC2034
RULES_CONTENT_COMPONENTS='# Svelte 5 Component Patterns

> **When to use:** Building or modifying components, working with runes, component composition.
>
> **Read first for:** Any component work, rune patterns, snippets, two-way binding.

## Runes (Svelte 5 Reactivity)

Runes are compiler directives in `.svelte` and `.svelte.ts` files.

### `$state` — Reactive State

```svelte
<script lang="ts">
  let count = $state(0)
  let items = $state<string[]>([])
  function increment() { count++ }          // Direct mutation tracked
  function addItem(s: string) { items.push(s) }  // Array mutations tracked
</script>
<button onclick={increment}>Count: {count}</button>
```

### `$derived` — Computed Values

```svelte
<script lang="ts">
  let count = $state(0)
  let doubled = $derived(count * 2)
  let summary = $derived.by(() => count === 0 ? "zero" : count < 10 ? "small" : "large")
</script>
```

### `$effect` — Side Effects

```svelte
<script lang="ts">
  let query = $state("")
  $effect(() => {
    if (query.length < 3) return
    const controller = new AbortController()
    fetch(`/api/search?q=${query}`, { signal: controller.signal })
      .then((r) => r.json()).then((data) => { results = data })
    return () => controller.abort()  // Cleanup runs before next effect
  })
</script>
```

### `$props` — Component Props

```svelte
<script lang="ts">
  let {
    title,
    count = 0,
    variant = "primary" as "primary" | "secondary",
    children,
    onclick,
  }: {
    title: string
    count?: number
    variant?: "primary" | "secondary"
    children?: import("svelte").Snippet
    onclick?: (e: MouseEvent) => void
  } = $props()
</script>
<div class="card {variant}">
  <h2>{title} ({count})</h2>
  {#if children}{@render children()}{/if}
  <button {onclick}>Click me</button>
</div>
```

### `$bindable` — Two-way Binding Props

```svelte
<!-- Toggle.svelte -->
<script lang="ts">
  let { checked = $bindable(false) }: { checked?: boolean } = $props()
</script>
<button onclick={() => checked = !checked}>{checked ? "ON" : "OFF"}</button>
<!-- Parent: <Toggle bind:checked={isEnabled} /> -->
```

## Snippets (Replacing Slots)

```svelte
<!-- Card.svelte: typed snippet props -->
<script lang="ts">
  let { header, children, footer }: {
    header?: import("svelte").Snippet
    children: import("svelte").Snippet
    footer?: import("svelte").Snippet<[{ itemCount: number }]>
  } = $props()
</script>
<div class="card">
  {#if header}<header>{@render header()}</header>{/if}
  <main>{@render children()}</main>
  {#if footer}<footer>{@render footer({ itemCount: 3 })}</footer>{/if}
</div>

<!-- Usage: {#snippet name()} defines, {@render name()} renders -->
<!-- <Card>
  {#snippet header()}<h2>Title</h2>{/snippet}
  <p>Default content</p>
  {#snippet footer({ itemCount })}<span>{itemCount} items</span>{/snippet}
</Card> -->
```

## Reactive Stores (`.svelte.ts` files)

```typescript
// src/lib/stores/auth.svelte.ts — class-based store with runes
class AuthState {
  user = $state<User | null>(null)
  token = $state<string | null>(null)
  isAuthenticated = $derived(!!this.token)

  async login(email: string, password: string) {
    const res = await fetch("/api/auth/login", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    })
    const data = await res.json()
    this.user = data.user; this.token = data.token
  }
  logout() { this.user = null; this.token = null }
}
export const auth = new AuthState()
```

## Component Organization

- PascalCase files: `UserCard.svelte`
- Import from `$lib`: `import UserCard from "$lib/components/domain/UserCard.svelte"`
- Structure: `src/lib/components/ui/`, `src/lib/components/domain/`

## Event Handling

```svelte
<script lang="ts">
  // Pass handlers via props (no createEventDispatcher in Svelte 5)
  let { onsubmit }: { onsubmit?: (value: string) => void } = $props()
</script>
<button onclick={() => count++}>Count: {count}</button>
```'

# shellcheck disable=SC2034
RULES_CONTENT_ROUTING='# SvelteKit Routing & Data Loading

> **When to use:** Adding pages, API endpoints, load functions, form actions, hooks.
>
> **Read first for:** Any page or route work, server-side data loading, form handling.

## File-Based Routing

```
src/routes/
├── +page.svelte                # /
├── +page.server.ts             # Server load + form actions for /
├── +layout.svelte              # Root layout
├── +error.svelte               # Error page
├── users/
│   ├── +page.svelte            # /users
│   └── [id]/
│       ├── +page.svelte        # /users/:id
│       └── +page.server.ts     # Server load for /users/:id
├── blog/
│   └── [...slug]/
│       └── +page.svelte        # /blog/* (catch-all)
└── api/
    └── health/
        └── +server.ts          # GET /api/health
```

| File | Purpose | Runs On |
|------|---------|---------|
| `+page.svelte` | Page component | Client + SSR |
| `+page.ts` | Universal load | Client + Server |
| `+page.server.ts` | Server-only load + form actions | Server only |
| `+layout.svelte` | Layout wrapper | Client + SSR |
| `+server.ts` | API endpoint (GET, POST, etc.) | Server only |

## Load Functions

```typescript
// src/routes/users/+page.server.ts
import type { PageServerLoad } from "./$types"

export const load: PageServerLoad = async ({ url, depends }) => {
  depends("app:users")
  const page = Number(url.searchParams.get("page")) || 1
  const [users, total] = await Promise.all([
    db.users.findMany({ skip: (page - 1) * 20, take: 20 }),
    db.users.count(),
  ])
  return { users, total, page }
}
```

```svelte
<!-- +page.svelte: access load data via $props() -->
<script lang="ts">
  import type { PageData } from "./$types"
  let { data }: { data: PageData } = $props()
</script>
<ul>
  {#each data.users as user (user.id)}
    <li><a href="/users/{user.id}">{user.name}</a></li>
  {/each}
</ul>
```

## Form Actions

```typescript
// +page.server.ts: validate with Zod, return fail() or redirect()
import { fail, redirect } from "@sveltejs/kit"
import { z } from "zod"

const Schema = z.object({ name: z.string().min(1), email: z.string().email() })

export const actions: Actions = {
  create: async ({ request }) => {
    const result = Schema.safeParse(Object.fromEntries(await request.formData()))
    if (!result.success) return fail(400, { errors: result.error.flatten().fieldErrors })
    const user = await db.users.create({ data: result.data })
    redirect(303, `/users/${user.id}`)
  },
}
```

```svelte
<!-- use:enhance for progressive enhancement (re-runs load on success) -->
<script lang="ts">
  import { enhance } from "$app/forms"
  let { data, form }: { data: PageData; form: ActionData } = $props()
</script>
<form method="POST" action="?/create" use:enhance>
  <input name="name" />
  {#if form?.errors?.name}<span class="error">{form.errors.name[0]}</span>{/if}
  <button>Create</button>
</form>
```

## API Routes (`+server.ts`)

```typescript
// src/routes/api/health/+server.ts
import { json } from "@sveltejs/kit"
export const GET: RequestHandler = async () => {
  return json({ status: "ok", timestamp: new Date().toISOString() })
}
```

## Hooks (`src/hooks.server.ts`)

```typescript
export const handle: Handle = async ({ event, resolve }) => {
  const token = event.cookies.get("session")
  if (token) event.locals.user = await getUserFromToken(token)
  return await resolve(event)
}
```

## Navigation

```typescript
import { goto, invalidate, invalidateAll } from "$app/navigation"
await goto("/users")
await invalidate("app:users")   // Re-run load functions by depends() key
await invalidateAll()            // Re-run all load functions
```

## Page Options

```typescript
export const prerender = true        // Static generation
export const ssr = false             // Client-only SPA mode
```'

# shellcheck disable=SC2034
RULES_CONTENT_CROSS_SERVICE='# Cross-Service Patterns

> **When to use:** TypeScript config, environment variables, error handling, shared conventions.
>
> **Read first for:** Env vars, error/redirect patterns, adapter config, testing.

## Environment Variables

SvelteKit has four env modules with security boundaries:

```typescript
import { DATABASE_URL } from "$env/static/private"   // Server-only, build-time
import { PUBLIC_APP_NAME } from "$env/static/public"  // Client+server, build-time
import { env } from "$env/dynamic/private"             // Server-only, runtime
import { env as pubEnv } from "$env/dynamic/public"    // Client+server, runtime
```

| Prefix | Access | Set At | Module |
|--------|--------|--------|--------|
| (none) | Server only | Build | `$env/static/private` |
| `PUBLIC_` | Client + Server | Build | `$env/static/public` |
| (none) | Server only | Runtime | `$env/dynamic/private` |
| `PUBLIC_` | Client + Server | Runtime | `$env/dynamic/public` |

**Secrets are NEVER committed to git.** Build-time privates error if undefined.

## Error Handling

```typescript
import { error, redirect, fail } from "@sveltejs/kit"

error(404, "User not found")                    // Error page
error(403, { message: "Not authorized" })       // Structured
redirect(303, "/login")                         // Redirect (3xx only)
fail(400, { errors: { email: "Invalid" } })     // Form validation failure
```

```svelte
<!-- src/routes/+error.svelte -->
<script lang="ts">
  import { page } from "$app/state"
</script>
<h1>{page.status}</h1>
<p>{page.error?.message}</p>
```

## Adapter Configuration

```javascript
// svelte.config.js
import adapter from "@sveltejs/adapter-node"
import { vitePreprocess } from "@sveltejs/vite-plugin-svelte"

export default {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter({ out: "build", precompress: true }),
    alias: { $components: "src/lib/components" },
  },
}
```

| Adapter | Use Case |
|---------|----------|
| `adapter-auto` | Auto-detect (Vercel, Netlify, Cloudflare) |
| `adapter-node` | Self-hosted Node.js server |
| `adapter-static` | Fully static site |

## TypeScript Conventions

- **Strict mode** (extends `.svelte-kit/tsconfig.json`)
- Run `npx svelte-kit sync` after route changes to regenerate types
- Use `interface` for objects, `type` for unions — never use `any`

## `$lib` Convention

```
src/lib/
├── components/     # $lib/components/...
├── server/         # $lib/server/... (server-only — build error if client imports)
├── stores/         # $lib/stores/... (.svelte.ts files for runes)
├── utils/          # $lib/utils/...
└── index.ts        # Re-exports for $lib
```

## Testing Patterns

```typescript
// Unit test
import { render, screen, fireEvent } from "@testing-library/svelte"
import Button from "$lib/components/ui/Button.svelte"

it("calls onclick handler", async () => {
  let clicked = false
  render(Button, { props: { onclick: () => { clicked = true } } })
  await fireEvent.click(screen.getByRole("button"))
  expect(clicked).toBe(true)
})

// E2E test (Playwright)
test("can create user", async ({ page }) => {
  await page.goto("/users")
  await page.fill("input[name=name]", "Alice")
  await page.click("button[type=submit]")
  await expect(page.locator("text=Alice")).toBeVisible()
})
```

## Import Order

1. SvelteKit (`@sveltejs/kit`, `$app/*`) 2. Env (`$env/*`) 3. Lib (`$lib/*`) 4. External

**Never log:** passwords, tokens, PII, full request bodies with sensitive data.

## Security Best Practices

### XSS Prevention
- Svelte auto-escapes all `{expressions}` in templates — this is your primary defense
- **Never** use `{@html ...}` with user-supplied input
- If rendering user HTML is unavoidable, sanitize with DOMPurify:
```svelte
<script lang="ts">
  import DOMPurify from "dompurify"
  let { rawHtml }: { rawHtml: string } = $props()
  let safeHtml = $derived(DOMPurify.sanitize(rawHtml))
</script>
{@html safeHtml}
```

### Content Security Policy
Configure CSP in `src/hooks.server.ts`:
```typescript
// src/hooks.server.ts
import type { Handle } from "@sveltejs/kit"

export const handle: Handle = async ({ event, resolve }) => {
  const response = await resolve(event)
  response.headers.set(
    "Content-Security-Policy",
    [
      "default-src '\''self'\''",
      "script-src '\''self'\''",
      "style-src '\''self'\'' '\''unsafe-inline'\''",
      "img-src '\''self'\'' data: https:",
      "connect-src '\''self'\'' https://api.example.com",
      "frame-ancestors '\''none'\''",
    ].join("; ")
  )
  return response
}
```

### CSRF Protection
- SvelteKit form actions are automatically protected against CSRF (validates `Origin` header)
- For custom API routes (`+server.ts`), validate the origin manually:
```typescript
export const POST: RequestHandler = async ({ request, url }) => {
  const origin = request.headers.get("origin")
  if (origin !== url.origin) {
    return new Response("Forbidden", { status: 403 })
  }
  // ... handle request
}
```
- Use `SameSite=Strict` cookies for session tokens

### Authentication Token Storage
- **Never** store tokens in `localStorage` (XSS-accessible)
- Use `httpOnly` cookies for session tokens (not accessible via JavaScript)
- For SPAs: short-lived access token in memory + `httpOnly` refresh cookie
- Use `event.cookies.set()` in server load functions and form actions:
```typescript
event.cookies.set("session", token, {
  path: "/",
  httpOnly: true,
  secure: true,
  sameSite: "strict",
  maxAge: 60 * 60 * 24, // 1 day
})
```

### Dependency Security
```bash
pnpm audit --production
npx better-npm-audit audit
```
Run `pnpm audit` in CI and block merges on critical/high vulnerabilities.

## Performance Checklist

### Bundle Optimization
- SvelteKit auto-splits code per route — each `+page.svelte` is a separate chunk
- Use dynamic imports for heavy components:
```svelte
<script lang="ts">
  import { onMount } from "svelte"
  let HeavyChart: typeof import("$lib/components/HeavyChart.svelte").default | null = $state(null)
  onMount(async () => {
    HeavyChart = (await import("$lib/components/HeavyChart.svelte")).default
  })
</script>
{#if HeavyChart}<svelte:component this={HeavyChart} data={chartData} />{/if}
```
- Tree shaking: use named imports (`import { debounce } from "lodash-es"` not `import _ from "lodash"`)
- Analyze bundle:
```bash
npx vite-bundle-visualizer
```

### Rendering Performance
- Use `$derived` for computed values (auto-tracked, no manual dependency arrays)
- Svelte'\''s compiler eliminates the virtual DOM — updates are surgical, per-binding
- Use `{#key expression}` to force re-creation of components when data changes
- Virtualize long lists with `svelte-virtual-list` or `@tanstack/svelte-virtual`:
```svelte
<script lang="ts">
  import { createVirtualizer } from "@tanstack/svelte-virtual"
  let parentEl: HTMLDivElement
  const virtualizer = createVirtualizer({
    count: items.length,
    getScrollElement: () => parentEl,
    estimateSize: () => 50,
  })
</script>
<div bind:this={parentEl} class="h-[600px] overflow-auto">
  <div style="height: {$virtualizer.getTotalSize()}px; position: relative;">
    {#each $virtualizer.getVirtualItems() as row (row.key)}
      <div style="position: absolute; top: {row.start}px; height: {row.size}px; width: 100%;">
        {items[row.index].name}
      </div>
    {/each}
  </div>
</div>
```

### Image Optimization
- Use `enhanced:img` (Vite imagetools) for automatic optimization:
```svelte
<enhanced:img src="$lib/assets/hero.jpg" alt="Hero" />
```
- Or use `@sveltejs/enhanced-img`:
```bash
pnpm add -D @sveltejs/enhanced-img
```
- Always specify `width` and `height` to prevent layout shift
- Use WebP/AVIF with `<picture>` fallbacks for manual optimization

### Core Web Vitals
- **LCP < 2.5s:** Preload hero images, use `fetchpriority="high"` on LCP elements
- **FID < 100ms:** Svelte'\''s compiled output is minimal JS — leverage SSR for initial load
- **CLS < 0.1:** Always set image dimensions, reserve space for dynamic content with CSS
- Use `preloadData` in `hooks.server.ts` or preload links for critical resources:
```svelte
<svelte:head>
  <link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossorigin="anonymous" />
</svelte:head>
```
- Configure prerendering for static pages:
```typescript
// +page.ts
export const prerender = true
```'

LINT_LANGUAGES="TypeScript/Svelte (eslint + prettier), JSON, YAML, Shell (shellcheck)"
