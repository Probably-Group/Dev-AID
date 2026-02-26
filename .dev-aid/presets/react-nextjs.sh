#!/usr/bin/env bash
# Preset: React 19 + Next.js 15 App Router + TypeScript

preset_name="react-nextjs"
preset_description="React 19 + Next.js 15 App Router with RSC, server actions, Vitest + Testing Library"

# Rules files: newline-delimited "filename|description" pairs
RULES_FILES="app-router.md|App Router conventions, RSC, server/client components, route handlers, middleware
components.md|Component patterns, data fetching, Suspense/error boundaries, image optimization
cross-service.md|TypeScript conventions, env vars, testing with Vitest + Testing Library"

# Technology stack entries
TECH_STACK="| Framework | Next.js 15 (App Router) |
| UI Library | React 19 |
| Language | TypeScript 5.5+ (strict mode) |
| Styling | Tailwind CSS 4 |
| Testing | Vitest + @testing-library/react |
| Linting | ESLint (eslint-config-next) + Prettier |
| Package Manager | *npm / pnpm / bun* |
| Deployment | *Vercel / Docker / Node.js standalone* |"

# Context loading table entries
CONTEXT_LOADING_TABLE="| **New page or route** | \`.claude/rules/app-router.md\`, \`app/\` directory |
| **New component** | \`.claude/rules/components.md\`, \`components/\` |
| **Data fetching** | \`.claude/rules/components.md\` (Data Fetching section) |
| **Server actions** | \`.claude/rules/app-router.md\` (Server Actions section) |
| **API route handler** | \`.claude/rules/app-router.md\` (Route Handlers section) |
| **Middleware** | \`.claude/rules/app-router.md\` (Middleware section), \`middleware.ts\` |
| **Debugging** | \`.claude/rules/troubleshooting.md\` |
| **Architecture decisions** | \`docs/decisions/index.md\` |
| **Cross-cutting concerns** | \`.claude/rules/cross-service.md\` |"

# Context groups
CONTEXT_GROUPS='### `routing`
Read: `.claude/rules/app-router.md`, `app/`, `middleware.ts`

### `components`
Read: `.claude/rules/components.md`, `components/`, `app/**/page.tsx`

### `config`
Read: `next.config.ts`, `tsconfig.json`, `package.json`, `.env.example`

### `debug`
Read: `.claude/rules/troubleshooting.md`

### `api`
Read: `.claude/rules/app-router.md` (Route Handlers section), `app/api/`'

# Development workflow
WORKFLOW='```bash
# Setup
npm install  # or: pnpm install / bun install

# Run dev server (Turbopack enabled by default)
npm run dev
# => http://localhost:3000

# Run tests
npm test              # Vitest
npm run test:watch    # Vitest watch mode

# Lint & format
npm run lint          # next lint (ESLint)
npx prettier --check .

# Type check
npx tsc --noEmit

# Build (production)
npm run build

# Start production server
npm start
```

### Useful URLs in Development

- App: `http://localhost:3000`
- Next.js DevTools: built into the dev overlay'

# Project overview
PROJECT_OVERVIEW="Next.js 15 App Router application with React 19 and TypeScript."

# Workspace structure
WORKSPACE_STRUCTURE='{{PROJECT_NAME}}/
+-- CLAUDE.md
+-- .claude/
|   +-- rules/
|   |   +-- app-router.md
|   |   +-- components.md
|   |   +-- cross-service.md
|   |   +-- troubleshooting.md
|   +-- hooks/
|   |   +-- lint-on-edit.sh
|   +-- memory/
|   |   +-- MEMORY.md
|   |   +-- component-patterns.md
|   |   +-- routing-gotchas.md
|   |   +-- debugging.md
|   +-- commands/
|       +-- review.md
|       +-- test.md
|       +-- plan.md
|       +-- smoke.md
|       +-- lint.md
|       +-- typecheck.md
+-- app/
|   +-- layout.tsx
|   +-- page.tsx
|   +-- loading.tsx
|   +-- error.tsx
|   +-- not-found.tsx
|   +-- globals.css
|   +-- api/
|   +-- (auth)/
|   +-- (dashboard)/
+-- components/
|   +-- ui/
|   +-- forms/
|   +-- layout/
+-- lib/
|   +-- actions/
|   +-- utils.ts
+-- public/
+-- tests/
+-- docs/
|   +-- plans/
|   |   +-- .plan-template.md
|   +-- decisions/
|       +-- index.md
|       +-- adr-template.md
+-- scripts/
|   +-- smoke-nextjs.sh
+-- next.config.ts
+-- tailwind.config.ts
+-- tsconfig.json
+-- package.json
+-- middleware.ts'

# Smoke test scripts: "filename|title|checks_variable_name"
SMOKE_SCRIPTS="smoke-nextjs.sh|Next.js App Health Checks|SMOKE_NEXTJS_CHECKS"

# shellcheck disable=SC2034
SMOKE_NEXTJS_CHECKS='section "Application Structure"

if [[ -f "next.config.ts" ]] || [[ -f "next.config.js" ]] || [[ -f "next.config.mjs" ]]; then
  pass "next.config file exists"
else
  fail "next.config.{ts,js,mjs} not found"
fi

if [[ -f "app/layout.tsx" ]]; then
  pass "app/layout.tsx exists (root layout)"
else
  fail "app/layout.tsx not found — required for App Router"
fi

if [[ -f "app/page.tsx" ]]; then
  pass "app/page.tsx exists (home page)"
else
  warn "app/page.tsx not found"
fi

section "Dependencies"

if [[ -f "package.json" ]]; then
  pass "package.json exists"
else
  fail "package.json not found"
fi

if [[ -d "node_modules" ]]; then
  pass "node_modules exists"
else
  fail "node_modules missing — run npm install"
fi

section "Type Checking"

if npx tsc --noEmit 2>/dev/null; then
  pass "TypeScript compiles without errors"
else
  warn "TypeScript compilation errors found"
fi

section "Build"

if npm run build 2>/dev/null; then
  pass "next build succeeds"
else
  fail "next build failed — check for errors"
fi

section "Linting"

if npx next lint --quiet 2>/dev/null; then
  pass "next lint passes"
else
  warn "next lint has findings"
fi

section "Tests"

if npx vitest --run --reporter=silent 2>/dev/null; then
  pass "Tests pass"
else
  warn "Tests failing or not found"
fi'

# Troubleshooting sections
TROUBLESHOOTING_SECTIONS='## 1. App Router / RSC

### Symptom: `Error: useState/useEffect only works in Client Components`

**Diagnosis:** You are using React hooks (`useState`, `useEffect`, `useRef`, etc.) inside
a Server Component. In the App Router, all components are Server Components by default.

**Fix:** Add the `"use client"` directive at the top of the file:
```tsx
"use client"

import { useState } from "react"

export function Counter() {
  const [count, setCount] = useState(0)
  return <button onClick={() => setCount(c => c + 1)}>{count}</button>
}
```

---

### Symptom: `Error: Functions cannot be passed directly to Client Components unless you explicitly expose it by marking it with "use server"`

**Diagnosis:** You are passing a function from a Server Component to a Client Component
as a prop. Only serializable data can cross the server-client boundary.

**Fix:** Either:
1. Mark the function as a server action with `"use server"`:
```tsx
async function handleSubmit(formData: FormData) {
  "use server"
  // process on server
}
```
2. Or move the function definition into the Client Component itself.

---

### Symptom: `Error: Unsupported Server Component type: undefined` or hydration mismatch

**Diagnosis:** A Server Component is importing a Client-only library (e.g., a charting
library, or a component using `window`/`document`). Server Components run on the server
where browser APIs are unavailable.

**Fix:** Use dynamic import with `ssr: false`:
```tsx
import dynamic from "next/dynamic"

const Chart = dynamic(() => import("@/components/Chart"), { ssr: false })
```

---

## 2. Data Fetching / Caching

### Symptom: Stale data — page shows old content after mutation

**Diagnosis:** Next.js aggressively caches `fetch` responses and rendered pages. After
mutating data (e.g., via a server action), the cache is not automatically invalidated.

**Fix:** Call `revalidatePath` or `revalidateTag` after mutation:
```tsx
"use server"
import { revalidatePath } from "next/cache"

async function createPost(formData: FormData) {
  await db.posts.create(...)
  revalidatePath("/posts")  // purge cached page
}
```

---

### Symptom: `TypeError: fetch failed` or `ECONNREFUSED` in Server Components

**Diagnosis:** Server Components run on the server, so `fetch` calls to `localhost:3000`
will fail during build time (server is not running). Also, relative URLs do not work
in Server Components.

**Fix:** Use absolute URLs for external APIs, or access the database/ORM directly
in Server Components (no need to go through an API route):
```tsx
// Prefer direct data access in Server Components
import { db } from "@/lib/db"

export default async function PostsPage() {
  const posts = await db.posts.findMany()
  return <PostList posts={posts} />
}
```

---

## 3. Middleware / Routing

### Symptom: Middleware runs on every request including static assets

**Diagnosis:** The `middleware.ts` matcher is too broad or missing. Without a matcher
config, middleware runs on every request.

**Fix:** Add a matcher config to exclude static files and API health checks:
```ts
// middleware.ts
export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
}
```

---

## 4. Build / Deployment

### Symptom: `Error: Page "/xyz" is missing "generateStaticParams()"` during build

**Diagnosis:** A dynamic route segment (`[slug]`) is configured for static generation
but does not export `generateStaticParams`.

**Fix:** Either export `generateStaticParams` or set `dynamic = "force-dynamic"`:
```tsx
// Option A: provide params
export async function generateStaticParams() {
  const posts = await getPosts()
  return posts.map((post) => ({ slug: post.slug }))
}

// Option B: opt out of static generation
export const dynamic = "force-dynamic"
```

---

### Symptom: `Module not found: Can'"'"'t resolve '"'"'@/...'"'"'` during build

**Diagnosis:** The path alias `@/` is not configured in `tsconfig.json`, or the paths
do not match the actual file structure.

**Fix:** Verify `tsconfig.json` has the correct paths configuration:
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

---

*Add entries as you encounter and solve issues. Use the Symptom -> Diagnosis -> Fix format.*'

# Memory topics: "filename|description" pairs
MEMORY_TOPICS="component-patterns.md|Component conventions, RSC vs Client Component decisions, reusable patterns
routing-gotchas.md|App Router edge cases, caching issues, middleware pitfalls
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
RULES_CONTENT_APP_ROUTER='# App Router Conventions

> **When to use:** Adding pages, routes, layouts, server actions, API route handlers, or middleware.
>
> **Read first for:** Any routing, data mutation, or middleware task.

## File Conventions

The App Router uses file-system based routing. Every folder in `app/` represents a route segment.

| File | Purpose |
|------|---------|
| `page.tsx` | Unique UI for a route (makes the route publicly accessible) |
| `layout.tsx` | Shared UI that wraps child routes (preserved across navigations) |
| `loading.tsx` | Loading UI (Suspense fallback) |
| `error.tsx` | Error UI (Error Boundary, must be `"use client"`) |
| `not-found.tsx` | 404 UI for a route segment |
| `template.tsx` | Like layout but re-mounts on navigation (no state preservation) |
| `default.tsx` | Fallback for parallel routes |
| `route.ts` | API route handler (GET, POST, PUT, DELETE, PATCH) |
| `middleware.ts` | Runs before every matched request (at project root, not in `app/`) |

## Server vs Client Components

**Default: Server Components.** All components in the App Router are Server Components unless
explicitly marked with `"use client"`.

### When to use Server Components (default)
- Data fetching (direct DB/ORM access, no API round-trip)
- Accessing backend resources (filesystem, environment variables)
- Keeping sensitive logic on the server (API keys, tokens)
- Reducing client bundle size

### When to use Client Components (`"use client"`)
- Interactivity: `useState`, `useEffect`, `useRef`, event handlers (`onClick`, `onChange`)
- Browser APIs: `window`, `document`, `localStorage`, `IntersectionObserver`
- Third-party client-only libraries (charts, maps, editors)

```tsx
// app/dashboard/page.tsx — Server Component (default)
import { db } from "@/lib/db"
import { DashboardChart } from "@/components/DashboardChart"

export default async function DashboardPage() {
  const stats = await db.stats.getLatest()
  return (
    <div>
      <h1>Dashboard</h1>
      {/* Pass serializable data to Client Component */}
      <DashboardChart data={stats} />
    </div>
  )
}
```

```tsx
// components/DashboardChart.tsx — Client Component
"use client"

import { useState } from "react"

export function DashboardChart({ data }: { data: Stats }) {
  const [range, setRange] = useState("7d")
  return (
    <div>
      <select value={range} onChange={(e) => setRange(e.target.value)}>
        <option value="7d">7 days</option>
        <option value="30d">30 days</option>
      </select>
      {/* render chart with data filtered by range */}
    </div>
  )
}
```

## Server Actions

Server actions are async functions that run on the server, callable from Client Components.

```tsx
// lib/actions/posts.ts
"use server"

import { revalidatePath } from "next/cache"
import { redirect } from "next/navigation"
import { db } from "@/lib/db"

export async function createPost(formData: FormData) {
  const title = formData.get("title") as string
  const content = formData.get("content") as string

  await db.posts.create({ data: { title, content } })
  revalidatePath("/posts")
  redirect("/posts")
}

export async function deletePost(id: string) {
  await db.posts.delete({ where: { id } })
  revalidatePath("/posts")
}
```

Usage in a Client Component:
```tsx
"use client"
import { createPost } from "@/lib/actions/posts"

export function NewPostForm() {
  return (
    <form action={createPost}>
      <input name="title" required />
      <textarea name="content" required />
      <button type="submit">Create Post</button>
    </form>
  )
}
```

## Route Handlers (API Routes)

```tsx
// app/api/posts/route.ts
import { NextRequest, NextResponse } from "next/server"
import { db } from "@/lib/db"

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const limit = Number(searchParams.get("limit") ?? 50)

  const posts = await db.posts.findMany({ take: limit })
  return NextResponse.json(posts)
}

export async function POST(request: NextRequest) {
  const body = await request.json()
  const post = await db.posts.create({ data: body })
  return NextResponse.json(post, { status: 201 })
}
```

Dynamic route handler:
```tsx
// app/api/posts/[id]/route.ts
export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params
  const post = await db.posts.findUnique({ where: { id } })
  if (!post) {
    return NextResponse.json({ error: "Not found" }, { status: 404 })
  }
  return NextResponse.json(post)
}
```

## Middleware

Middleware runs before every matched request. Place `middleware.ts` at the project root.

```tsx
// middleware.ts
import { NextResponse } from "next/server"
import type { NextRequest } from "next/server"

export function middleware(request: NextRequest) {
  // Example: redirect unauthenticated users
  const token = request.cookies.get("session")?.value
  if (!token && request.nextUrl.pathname.startsWith("/dashboard")) {
    return NextResponse.redirect(new URL("/login", request.url))
  }
  return NextResponse.next()
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
}
```

## Metadata & SEO

```tsx
// app/layout.tsx — static metadata
import type { Metadata } from "next"

export const metadata: Metadata = {
  title: { default: "My App", template: "%s | My App" },
  description: "Application description",
}
```

```tsx
// app/posts/[slug]/page.tsx — dynamic metadata
import type { Metadata } from "next"

export async function generateMetadata(
  { params }: { params: Promise<{ slug: string }> }
): Promise<Metadata> {
  const { slug } = await params
  const post = await getPost(slug)
  return {
    title: post.title,
    description: post.excerpt,
    openGraph: { title: post.title, images: [post.coverImage] },
  }
}
```

## Route Segment Config

Export these constants from any `page.tsx` or `layout.tsx` to control behavior:

```tsx
export const dynamic = "force-dynamic"       // always SSR, never cache
export const revalidate = 3600               // ISR: revalidate every hour
export const fetchCache = "default-no-store" // opt out of fetch caching
export const runtime = "edge"                // use Edge Runtime
```

## Parallel Routes

Use named slots for rendering multiple pages simultaneously:

```
app/
  @modal/
    login/page.tsx
    default.tsx
  @feed/
    page.tsx
    default.tsx
  layout.tsx
  page.tsx
```

```tsx
// app/layout.tsx
export default function Layout({
  children,
  modal,
  feed,
}: {
  children: React.ReactNode
  modal: React.ReactNode
  feed: React.ReactNode
}) {
  return (
    <div>
      {children}
      {feed}
      {modal}
    </div>
  )
}
```

## Intercepting Routes

Use `(.)`, `(..)`, `(..)(..)`, or `(...)` to intercept navigation:

```
app/
  feed/
    page.tsx
    @modal/
      (..)photo/[id]/page.tsx   # intercepts /photo/[id] when navigating from /feed
  photo/
    [id]/
      page.tsx                  # direct URL access gets this page
```'

# shellcheck disable=SC2034
RULES_CONTENT_COMPONENTS='# Component Patterns

> **When to use:** Creating or modifying React components, data fetching, error handling.
>
> **Read first for:** Component structure, fetching patterns, Suspense and error boundaries.

## Component Structure

```
components/
  ui/                    # Reusable design-system primitives
    Button.tsx
    Card.tsx
    Dialog.tsx
  forms/                 # Form components
    Input.tsx
    Select.tsx
  layout/                # Layout building blocks
    Header.tsx
    Sidebar.tsx
    Footer.tsx
```

### Naming Conventions

- **Files:** PascalCase matching the export (`Button.tsx`, `UserProfile.tsx`)
- **Components:** PascalCase (`export function Button()`)
- **Hooks:** camelCase with `use` prefix (`useAuth`, `useDebounce`)
- **Utilities:** camelCase (`formatDate`, `cn`)

## Data Fetching

### Server Components (preferred)

Fetch data directly in Server Components. No `useEffect` or `useState` needed.

```tsx
// app/posts/page.tsx — Server Component
import { db } from "@/lib/db"
import { Suspense } from "react"
import { PostList } from "@/components/PostList"
import { PostListSkeleton } from "@/components/PostListSkeleton"

export default function PostsPage() {
  return (
    <Suspense fallback={<PostListSkeleton />}>
      <PostListLoader />
    </Suspense>
  )
}

async function PostListLoader() {
  const posts = await db.posts.findMany({
    orderBy: { createdAt: "desc" },
    take: 20,
  })
  return <PostList posts={posts} />
}
```

### Fetch with Caching

```tsx
// Use Next.js extended fetch for caching
const data = await fetch("https://api.example.com/data", {
  next: { revalidate: 3600 },  // revalidate every hour
})

// Or tag-based revalidation
const data = await fetch("https://api.example.com/posts", {
  next: { tags: ["posts"] },
})

// Invalidate from a server action
"use server"
import { revalidateTag } from "next/cache"
revalidateTag("posts")
```

### Client-Side Fetching (when needed)

For user-specific data, real-time updates, or infinite scroll:

```tsx
"use client"

import useSWR from "swr"

const fetcher = (url: string) => fetch(url).then((r) => r.json())

export function UserNotifications() {
  const { data, error, isLoading } = useSWR("/api/notifications", fetcher, {
    refreshInterval: 30000,  // poll every 30s
  })

  if (isLoading) return <Skeleton />
  if (error) return <ErrorMessage error={error} />
  return <NotificationList items={data} />
}
```

## Suspense Boundaries

Wrap async Server Components in `<Suspense>` to show loading states:

```tsx
import { Suspense } from "react"

export default function DashboardPage() {
  return (
    <div className="grid grid-cols-2 gap-4">
      <Suspense fallback={<CardSkeleton />}>
        <RevenueCard />
      </Suspense>
      <Suspense fallback={<CardSkeleton />}>
        <UsersCard />
      </Suspense>
      <Suspense fallback={<TableSkeleton />}>
        <RecentOrders />
      </Suspense>
    </div>
  )
}
```

Multiple `<Suspense>` boundaries enable **streaming**: each section loads independently.

## Error Boundaries

`error.tsx` files act as error boundaries for their route segment:

```tsx
// app/dashboard/error.tsx
"use client"

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div role="alert">
      <h2>Something went wrong</h2>
      <p>{error.message}</p>
      <button onClick={reset}>Try again</button>
    </div>
  )
}
```

## Image Optimization

Always use `next/image` instead of `<img>`:

```tsx
import Image from "next/image"

// Local image (auto size detection)
import heroImage from "@/public/hero.png"

export function Hero() {
  return (
    <Image
      src={heroImage}
      alt="Hero banner"
      placeholder="blur"            // auto blur placeholder for local images
      priority                       // preload above-the-fold images
    />
  )
}

// Remote image (must specify dimensions or use fill)
export function Avatar({ src, name }: { src: string; name: string }) {
  return (
    <Image
      src={src}
      alt={name}
      width={48}
      height={48}
      className="rounded-full"
    />
  )
}
```

Configure remote image domains in `next.config.ts`:
```ts
// next.config.ts
const nextConfig = {
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "cdn.example.com" },
    ],
  },
}
```

## React 19 Patterns

### `use` Hook

Read promises and context in render:

```tsx
import { use } from "react"

function PostContent({ postPromise }: { postPromise: Promise<Post> }) {
  const post = use(postPromise)  // suspends until resolved
  return <article>{post.content}</article>
}
```

### `useActionState` (form state from server actions)

```tsx
"use client"
import { useActionState } from "react"
import { createUser } from "@/lib/actions/users"

export function SignupForm() {
  const [state, formAction, isPending] = useActionState(createUser, null)

  return (
    <form action={formAction}>
      <input name="email" type="email" required />
      {state?.error && <p className="text-red-500">{state.error}</p>}
      <button type="submit" disabled={isPending}>
        {isPending ? "Creating..." : "Sign Up"}
      </button>
    </form>
  )
}
```

### `useOptimistic` (optimistic UI updates)

```tsx
"use client"
import { useOptimistic } from "react"
import { likePost } from "@/lib/actions/posts"

export function LikeButton({ likes, postId }: { likes: number; postId: string }) {
  const [optimisticLikes, addOptimisticLike] = useOptimistic(
    likes,
    (current) => current + 1,
  )

  async function handleLike() {
    addOptimisticLike(null)
    await likePost(postId)
  }

  return (
    <form action={handleLike}>
      <button type="submit">{optimisticLikes} Likes</button>
    </form>
  )
}
```

## Props & TypeScript

```tsx
// Always define props as an interface or type
interface ButtonProps {
  variant?: "primary" | "secondary" | "ghost"
  size?: "sm" | "md" | "lg"
  children: React.ReactNode
  onClick?: () => void
  disabled?: boolean
}

export function Button({
  variant = "primary",
  size = "md",
  children,
  ...props
}: ButtonProps) {
  return (
    <button className={cn(variants[variant], sizes[size])} {...props}>
      {children}
    </button>
  )
}
```

## Composition Over Configuration

Prefer composable components over prop-heavy components:

```tsx
// Prefer this (composable)
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
  <CardContent>Content</CardContent>
</Card>

// Over this (prop-heavy)
<Card title="Title" content="Content" headerStyle="..." />
```'

# shellcheck disable=SC2034
RULES_CONTENT_CROSS_SERVICE='# Cross-Service Patterns

> **When to use:** Ensuring consistency, understanding shared conventions.
>
> **Read first for:** TypeScript patterns, env vars, testing, code style.

## TypeScript Conventions

- **Strict mode** enabled in `tsconfig.json`
- Prefer `interface` for object shapes, `type` for unions/intersections
- Use `unknown` over `any` — narrow types explicitly
- Never use `as` type assertions unless absolutely necessary (prefer type guards)
- Always type component props explicitly (no `any` props)

```typescript
// Type guards over assertions
function isApiError(error: unknown): error is ApiError {
  return (
    typeof error === "object" &&
    error !== null &&
    "code" in error &&
    "message" in error
  )
}
```

## Date/Time Format

All timestamps use **ISO 8601 UTC**: `2026-01-01T12:00:00Z`

```typescript
const now = new Date().toISOString()
```

## Environment Variables

Next.js has two types of env vars:

| Prefix | Available In | Use For |
|--------|-------------|---------|
| `NEXT_PUBLIC_` | Client + Server | Public config (API URLs, feature flags) |
| (no prefix) | Server only | Secrets (API keys, DB URLs) |

```typescript
// lib/env.ts — validate at startup
import { z } from "zod"

const envSchema = z.object({
  DATABASE_URL: z.string().url(),
  NEXTAUTH_SECRET: z.string().min(32),
  NEXT_PUBLIC_APP_URL: z.string().url(),
})

export const env = envSchema.parse(process.env)
```

**Secrets are NEVER committed to git.** Use `.env.local` locally (auto-gitignored by Next.js).

| Variable | Prefix | Description |
|----------|--------|-------------|
| `DATABASE_URL` | (none) | Database connection string |
| `NEXTAUTH_SECRET` | (none) | Auth.js signing secret |
| `NEXTAUTH_URL` | (none) | Canonical app URL (production) |
| `NEXT_PUBLIC_APP_URL` | `NEXT_PUBLIC_` | App URL accessible in client code |

## Import Conventions

```typescript
// 1. React / Next.js
import { Suspense } from "react"
import Image from "next/image"
import Link from "next/link"

// 2. External packages
import { z } from "zod"

// 3. Internal modules (use @ alias)
import { db } from "@/lib/db"
import { Button } from "@/components/ui/Button"
import type { Post } from "@/types"
```

## Error Handling

```typescript
// For server actions: return error state, never throw
"use server"
export async function createPost(prevState: unknown, formData: FormData) {
  try {
    const post = await db.posts.create(...)
    revalidatePath("/posts")
    return { success: true }
  } catch (error) {
    return { success: false, error: "Failed to create post" }
  }
}

// For API routes: return appropriate status codes
export async function GET() {
  try {
    const data = await fetchData()
    return NextResponse.json(data)
  } catch {
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    )
  }
}
```

## Testing Patterns

### Component Testing (Vitest + Testing Library)

```typescript
// tests/components/Button.test.tsx
import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, it, expect, vi } from "vitest"
import { Button } from "@/components/ui/Button"

describe("Button", () => {
  it("renders children", () => {
    render(<Button>Click me</Button>)
    expect(screen.getByRole("button", { name: "Click me" })).toBeInTheDocument()
  })

  it("calls onClick handler", async () => {
    const onClick = vi.fn()
    render(<Button onClick={onClick}>Click</Button>)
    await userEvent.click(screen.getByRole("button"))
    expect(onClick).toHaveBeenCalledOnce()
  })

  it("disables button when disabled prop is true", () => {
    render(<Button disabled>Click</Button>)
    expect(screen.getByRole("button")).toBeDisabled()
  })
})
```

### Vitest Configuration

```typescript
// vitest.config.ts
import { defineConfig } from "vitest/config"
import react from "@vitejs/plugin-react"
import path from "path"

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: ["./tests/setup.ts"],
    globals: true,
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "."),
    },
  },
})
```

```typescript
// tests/setup.ts
import "@testing-library/jest-dom/vitest"
```

## Logging

```typescript
// Server-side only (Server Components, route handlers, server actions)
console.log("[posts]", "Created post", { postId, userId })
console.error("[posts]", "Failed to create post", { error })

// For structured logging in production, use pino:
import pino from "pino"
const logger = pino({ level: process.env.LOG_LEVEL ?? "info" })
```

**Never log:** passwords, tokens, PII, full request bodies with sensitive data.

## Code Style

- Use `cn()` utility (clsx + tailwind-merge) for conditional Tailwind classes
- Use `className` prop for styling — never inline `style` objects
- Colocate components with their styles and tests when practical

```typescript
// lib/utils.ts
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```'

LINT_LANGUAGES="TypeScript/TSX (next lint + prettier), JSON, YAML, Shell (shellcheck)"
