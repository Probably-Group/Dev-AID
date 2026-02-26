#!/usr/bin/env bash
# Preset: Angular 19+ with standalone components, signals, TypeScript

preset_name="angular"
preset_description="Angular 19+ with standalone components, signals, typed forms, and NgRx signal store"

# Rules files: newline-delimited "filename|description" pairs
RULES_FILES="components.md|Standalone components, signals, input/output, change detection, zoneless
state.md|NgRx signals store, RxJS patterns, effects, reactive state management
cross-service.md|Dependency injection, routing, lazy loading, interceptors, testing"

# Technology stack entries
TECH_STACK="| Framework | Angular 19+ (standalone components) |
| Language | TypeScript 5.5+ (strict mode) |
| State Management | NgRx Signal Store / lightweight signals |
| Styling | *Tailwind CSS / Angular Material / SCSS* |
| Testing | Karma + Jasmine (unit), Playwright (e2e) |
| Linting | ESLint (@angular-eslint) |
| Build | Angular CLI (esbuild + Vite dev server) |
| Package Manager | *npm / pnpm* |"

# Context loading table entries
CONTEXT_LOADING_TABLE="| **New component** | \`.claude/rules/components.md\`, \`src/app/\` |
| **State management** | \`.claude/rules/state.md\`, \`src/app/store/\` |
| **Routing changes** | \`.claude/rules/cross-service.md\` (Routing section), \`app.routes.ts\` |
| **Service / DI** | \`.claude/rules/cross-service.md\` (DI section), \`src/app/services/\` |
| **HTTP / interceptors** | \`.claude/rules/cross-service.md\` (HTTP section) |
| **Forms** | \`.claude/rules/components.md\` (Forms section) |
| **Debugging** | \`.claude/rules/troubleshooting.md\` |
| **Architecture decisions** | \`docs/decisions/index.md\` |"

# Context groups
CONTEXT_GROUPS='### `components`
Read: `.claude/rules/components.md`, `src/app/components/`, `src/app/shared/`

### `state`
Read: `.claude/rules/state.md`, `src/app/store/`

### `routing`
Read: `.claude/rules/cross-service.md` (Routing section), `src/app/app.routes.ts`

### `config`
Read: `angular.json`, `tsconfig.json`, `package.json`, `.env`

### `debug`
Read: `.claude/rules/troubleshooting.md`'

# Development workflow
WORKFLOW='```bash
# Setup
npm install  # or: pnpm install

# Run dev server (Vite-based, HMR enabled)
ng serve
# => http://localhost:4200

# Run tests
ng test               # unit tests (Karma + Jasmine)
ng e2e                # e2e tests (Playwright)

# Lint
ng lint

# Type check (included in build)
npx tsc --noEmit

# Build (production)
ng build

# Generate component/service/pipe/etc
ng generate component features/user-profile --standalone
ng generate service services/auth
ng generate pipe pipes/date-format
```

### Useful URLs in Development

- App: `http://localhost:4200`
- Angular DevTools: Chrome extension for inspecting component tree and change detection'

# Project overview
PROJECT_OVERVIEW="Angular 19+ application with standalone components, signals-based reactivity, and TypeScript."

# Workspace structure
WORKSPACE_STRUCTURE='{{PROJECT_NAME}}/
+-- CLAUDE.md
+-- .claude/
|   +-- rules/
|   |   +-- components.md
|   |   +-- state.md
|   |   +-- cross-service.md
|   |   +-- troubleshooting.md
|   +-- hooks/
|   |   +-- lint-on-edit.sh
|   +-- memory/
|   |   +-- MEMORY.md
|   |   +-- component-patterns.md
|   |   +-- state-gotchas.md
|   |   +-- debugging.md
|   |   +-- di-patterns.md
|   +-- commands/
|       +-- review.md
|       +-- test.md
|       +-- plan.md
|       +-- smoke.md
|       +-- lint.md
|       +-- typecheck.md
+-- src/
|   +-- app/
|   |   +-- app.component.ts
|   |   +-- app.config.ts
|   |   +-- app.routes.ts
|   |   +-- features/
|   |   |   +-- home/
|   |   |   +-- dashboard/
|   |   |   +-- auth/
|   |   +-- shared/
|   |   |   +-- components/
|   |   |   +-- directives/
|   |   |   +-- pipes/
|   |   +-- core/
|   |   |   +-- services/
|   |   |   +-- interceptors/
|   |   |   +-- guards/
|   |   |   +-- models/
|   |   +-- store/
|   +-- assets/
|   +-- environments/
|   |   +-- environment.ts
|   |   +-- environment.prod.ts
|   +-- styles.scss
|   +-- index.html
|   +-- main.ts
+-- tests/
+-- docs/
|   +-- plans/
|   |   +-- .plan-template.md
|   +-- decisions/
|       +-- index.md
|       +-- adr-template.md
+-- scripts/
|   +-- smoke-angular.sh
+-- angular.json
+-- tsconfig.json
+-- tsconfig.app.json
+-- tsconfig.spec.json
+-- package.json'

# Smoke test scripts: "filename|title|checks_variable_name"
SMOKE_SCRIPTS="smoke-angular.sh|Angular App Health Checks|SMOKE_ANGULAR_CHECKS"

# shellcheck disable=SC2034
SMOKE_ANGULAR_CHECKS='section "Application Structure"

if [[ -f "angular.json" ]]; then
  pass "angular.json exists"
else
  fail "angular.json not found — is this an Angular project?"
fi

if [[ -f "src/main.ts" ]]; then
  pass "src/main.ts exists (bootstrap entry)"
else
  fail "src/main.ts not found"
fi

if [[ -f "src/app/app.component.ts" ]]; then
  pass "src/app/app.component.ts exists (root component)"
else
  fail "src/app/app.component.ts not found"
fi

if [[ -f "src/app/app.routes.ts" ]]; then
  pass "src/app/app.routes.ts exists (route definitions)"
else
  warn "src/app/app.routes.ts not found — using module-based routing?"
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

section "Build"

if npx ng build 2>/dev/null; then
  pass "ng build succeeds"
else
  fail "ng build failed — check for errors"
fi

section "Linting"

if npx ng lint --quiet 2>/dev/null; then
  pass "ng lint passes"
else
  warn "ng lint has findings"
fi

section "Tests"

if npx ng test --watch=false --browsers=ChromeHeadless 2>/dev/null; then
  pass "Unit tests pass"
else
  warn "Unit tests failing or not configured"
fi'

# Troubleshooting sections
TROUBLESHOOTING_SECTIONS='## 1. Standalone Components / Signals

### Symptom: `NG0303: Can'"'"'t bind to '"'"'ngIf'"'"' since it isn'"'"'t a known property`

**Diagnosis:** In Angular 19 with standalone components, common directives like `*ngIf`
and `*ngFor` are no longer available by default. The old `NgIf`/`NgFor` directives require
importing `CommonModule`. However, Angular 17+ introduced built-in control flow that
does not require any imports.

**Fix:** Use the new built-in control flow syntax instead of structural directives:
```typescript
// OLD (requires CommonModule import)
// <div *ngIf="isLoading">Loading...</div>
// <div *ngFor="let item of items">{{ item.name }}</div>

// NEW (built-in, no imports needed)
@if (isLoading) {
  <div>Loading...</div>
}

@for (item of items; track item.id) {
  <div>{{ item.name }}</div>
} @empty {
  <div>No items found</div>
}

@switch (status) {
  @case ("loading") { <Spinner /> }
  @case ("error") { <ErrorMessage /> }
  @default { <Content /> }
}
```

---

### Symptom: `NG0100: ExpressionChangedAfterItHasBeenCheckedError`

**Diagnosis:** A value bound in the template changed after Angular'"'"'s change detection
ran. This is common when modifying state in `ngAfterViewInit` or when a child component
changes a parent'"'"'s bound property.

**Fix:**
1. Move the state change to `ngOnInit` or use a `signal()` (signals notify change detection properly):
```typescript
// Instead of setting a value in ngAfterViewInit:
title = signal("Default")

ngOnInit() {
  this.title.set("Loaded Title")
}
```
2. For zoneless apps, ensure you use signals for all reactive state — signals automatically
   schedule change detection when their value changes.

---

### Symptom: `signal()` value does not update the template

**Diagnosis:** You are reassigning the signal variable instead of calling `.set()` or
`.update()`. Signals are functions — you must call them to read and use `.set()` to write.

**Fix:**
```typescript
// WRONG — reassigns the variable, loses reactivity
count = signal(0)
this.count = signal(1)  // creates a new signal, template still reads the old one

// CORRECT — mutates the existing signal
count = signal(0)
this.count.set(1)
this.count.update(c => c + 1)

// Reading in template: {{ count() }} — note the parentheses
// Reading in TypeScript: this.count()
```

---

## 2. Routing / Lazy Loading

### Symptom: Blank page after navigation, no errors in console

**Diagnosis:** The route exists but the component is not rendering. Common causes:
1. Missing `<router-outlet>` in the parent component template.
2. The route path has a typo or does not match the URL.
3. A guard is silently rejecting the navigation.

**Fix:**
```typescript
// Ensure the parent component has <router-outlet>
@Component({
  standalone: true,
  imports: [RouterOutlet],
  template: `
    <app-header />
    <router-outlet />
  `,
})
export class LayoutComponent {}

// Check route configuration
export const routes: Routes = [
  {
    path: "dashboard",
    loadComponent: () => import("./features/dashboard/dashboard.component")
      .then(m => m.DashboardComponent),
  },
]
```

---

### Symptom: `Error: NG04002: Cannot match any routes. URL Segment: '...'`

**Diagnosis:** No route matches the requested URL. The route may be misspelled, not
included in the routes array, or missing a wildcard/redirect.

**Fix:** Add the missing route or a wildcard catch-all:
```typescript
export const routes: Routes = [
  { path: "", component: HomeComponent },
  { path: "dashboard", loadComponent: () => import("./features/dashboard/dashboard.component").then(m => m.DashboardComponent) },
  { path: "**", redirectTo: "" },  // catch-all redirect
]
```

---

## 3. Dependency Injection

### Symptom: `NullInjectorError: No provider for XxxService!`

**Diagnosis:** The service is not provided in the injector tree. In standalone component
apps, services must either use `providedIn: '"'"'root'"'"'` or be explicitly provided in the
component/route config.

**Fix:**
```typescript
// Option A: providedIn root (recommended for singletons)
@Injectable({ providedIn: "root" })
export class AuthService { }

// Option B: provide in route config
export const routes: Routes = [
  {
    path: "admin",
    providers: [AdminService],
    loadComponent: () => import("./admin.component").then(m => m.AdminComponent),
  },
]

// Option C: provide in component (creates instance per component)
@Component({
  standalone: true,
  providers: [FormService],
  ...
})
```

---

## 4. HTTP / Interceptors

### Symptom: HTTP requests not sending auth token, interceptor seems ignored

**Diagnosis:** Functional interceptors (Angular 17+) must be registered with
`provideHttpClient(withInterceptors([...]))`. The old class-based `HTTP_INTERCEPTORS`
token does not work with `provideHttpClient`.

**Fix:**
```typescript
// app.config.ts
import { provideHttpClient, withInterceptors } from "@angular/common/http"
import { authInterceptor } from "./core/interceptors/auth.interceptor"

export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(withInterceptors([authInterceptor])),
  ],
}
```

```typescript
// core/interceptors/auth.interceptor.ts
import { HttpInterceptorFn } from "@angular/common/http"
import { inject } from "@angular/core"
import { AuthService } from "../services/auth.service"

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService)
  const token = auth.getToken()

  if (token) {
    req = req.clone({
      setHeaders: { Authorization: `Bearer ${token}` },
    })
  }
  return next(req)
}
```

---

## 5. Testing

### Symptom: `Error: NG0302: The pipe '"'"'xxx'"'"' could not be found` in tests

**Diagnosis:** The test is rendering a standalone component that uses a pipe, but the
pipe is not imported in the test configuration.

**Fix:** Use the component'"'"'s own imports (standalone components are self-contained):
```typescript
// The component already declares its imports
@Component({
  standalone: true,
  imports: [DatePipe, CurrencyPipe],
  template: `{{ amount | currency }}`
})
export class PriceComponent { }

// In the test — just declare the component, its imports come along
TestBed.configureTestingModule({
  imports: [PriceComponent],
})
```

---

*Add entries as you encounter and solve issues. Use the Symptom -> Diagnosis -> Fix format.*'

# Memory topics: "filename|description" pairs
MEMORY_TOPICS="component-patterns.md|Component conventions, signal patterns, template syntax decisions
state-gotchas.md|State management edge cases, signal vs observable decisions, NgRx patterns
debugging.md|Common errors encountered and their solutions
di-patterns.md|Dependency injection patterns, provider scopes, injection tokens"

# Slash commands to scaffold
COMMANDS="review.md
test.md
plan.md
smoke.md
lint.md
typecheck.md"

# --- Substantive Rules Content ---

# shellcheck disable=SC2034
RULES_CONTENT_COMPONENTS='# Component Patterns

> **When to use:** Creating or modifying Angular components, working with signals, forms, or templates.
>
> **Read first for:** Component structure, signal patterns, control flow, forms.

## Standalone Components (Default in Angular 19)

All components must be standalone. Do **not** create NgModules for new code.

```typescript
import { Component, signal, computed, input, output } from "@angular/core"

@Component({
  selector: "app-user-card",
  standalone: true,
  imports: [RouterLink],
  template: `
    <div class="card">
      <h3>{{ name() }}</h3>
      <p>{{ email() }}</p>
      <span class="badge">{{ role() | titlecase }}</span>
      <button (click)="onSelect.emit(name())">Select</button>
    </div>
  `,
})
export class UserCardComponent {
  // Signal-based inputs (Angular 17.1+)
  name = input.required<string>()
  email = input.required<string>()
  role = input<string>("user")

  // Signal-based output
  onSelect = output<string>()

  // Computed signal derived from inputs
  displayName = computed(() => `${this.name()} (${this.role()})`)
}
```

## Signals

Signals are Angular'"'"'s reactive primitive. Use them for all component state.

```typescript
import { signal, computed, effect } from "@angular/core"

@Component({
  standalone: true,
  template: `
    <p>Count: {{ count() }}</p>
    <p>Double: {{ doubleCount() }}</p>
    <button (click)="increment()">+1</button>
    <button (click)="reset()">Reset</button>
  `,
})
export class CounterComponent {
  // Writable signal
  count = signal(0)

  // Computed signal (read-only, derived)
  doubleCount = computed(() => this.count() * 2)

  constructor() {
    // Effect — runs when any read signal changes
    effect(() => {
      console.log("Count changed to:", this.count())
    })
  }

  increment() {
    this.count.update(c => c + 1)
  }

  reset() {
    this.count.set(0)
  }
}
```

### Signal Rules

- **Read signals** by calling them: `this.count()` in TS, `{{ count() }}` in templates
- **Write signals** with `.set(value)` or `.update(fn)`
- **Never reassign** a signal variable (`this.x = signal(...)` — this breaks reactivity)
- Use `computed()` for derived state (automatically tracks dependencies)
- Use `effect()` for side effects (logging, localStorage sync, analytics)
- Inputs via `input()` / `input.required()` are read-only signals

## Built-in Control Flow

Angular 17+ control flow — no imports required, works everywhere.

```html
<!-- @if / @else -->
@if (user(); as user) {
  <app-user-card [name]="user.name" [email]="user.email" />
} @else {
  <p>Please log in</p>
}

<!-- @for with required track -->
@for (item of items(); track item.id) {
  <app-item-row [item]="item" />
} @empty {
  <p>No items found.</p>
}

<!-- @switch -->
@switch (status()) {
  @case ("loading") {
    <app-spinner />
  }
  @case ("error") {
    <app-error [message]="errorMessage()" />
  }
  @default {
    <app-content [data]="data()" />
  }
}
```

## @defer Blocks (Lazy Loading Templates)

Defer loading of heavy components until they are needed:

```html
@defer (on viewport) {
  <app-heavy-chart [data]="chartData()" />
} @placeholder {
  <div class="chart-placeholder">Chart loading area</div>
} @loading (minimum 500ms) {
  <app-spinner />
} @error {
  <p>Failed to load chart component</p>
}

<!-- Other triggers -->
@defer (on idle) { ... }
@defer (on interaction) { ... }
@defer (on hover) { ... }
@defer (on timer(3s)) { ... }
@defer (when isVisible()) { ... }
```

## Typed Reactive Forms

Always use typed forms (Angular 14+). Never use `any` form controls.

```typescript
import { Component } from "@angular/core"
import { FormBuilder, ReactiveFormsModule, Validators } from "@angular/forms"

@Component({
  standalone: true,
  imports: [ReactiveFormsModule],
  template: `
    <form [formGroup]="form" (ngSubmit)="onSubmit()">
      <label>
        Name
        <input formControlName="name" />
        @if (form.controls.name.errors?.["required"]) {
          <span class="error">Name is required</span>
        }
      </label>
      <label>
        Email
        <input formControlName="email" type="email" />
        @if (form.controls.email.errors?.["email"]) {
          <span class="error">Invalid email</span>
        }
      </label>
      <button type="submit" [disabled]="form.invalid">Submit</button>
    </form>
  `,
})
export class UserFormComponent {
  private fb = inject(FormBuilder)

  // Fully typed — form.value is { name: string; email: string }
  form = this.fb.nonNullable.group({
    name: ["", [Validators.required, Validators.minLength(2)]],
    email: ["", [Validators.required, Validators.email]],
  })

  onSubmit() {
    if (this.form.valid) {
      const value = this.form.getRawValue()
      // value is typed as { name: string; email: string }
      console.log(value)
    }
  }
}
```

## Component Communication

```typescript
// Parent → Child: signal inputs
@Component({
  template: `<app-child [name]="userName()" />`,
})
export class ParentComponent {
  userName = signal("Alice")
}

// Child → Parent: output
@Component({
  template: `<button (click)="clicked.emit()">Click</button>`,
})
export class ChildComponent {
  clicked = output()
}

// Unrelated components: use a shared service with signals
@Injectable({ providedIn: "root" })
export class NotificationService {
  private _messages = signal<string[]>([])
  messages = this._messages.asReadonly()

  add(msg: string) {
    this._messages.update(msgs => [...msgs, msg])
  }
}
```

## Change Detection

### Zoneless (Recommended for new projects, Angular 19+)

```typescript
// app.config.ts
import { provideExperimentalZonelessChangeDetection } from "@angular/core"

export const appConfig: ApplicationConfig = {
  providers: [
    provideExperimentalZonelessChangeDetection(),
  ],
}
```

With zoneless change detection:
- **Signals** automatically trigger change detection when they change
- No need for `zone.js` (smaller bundle, faster)
- Async operations (setTimeout, fetch) do NOT trigger change detection — use signals
- `ChangeDetectionStrategy.OnPush` is effectively the default behavior

### OnPush (if using zone.js)

```typescript
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  ...
})
```'

# shellcheck disable=SC2034
RULES_CONTENT_STATE='# State Management

> **When to use:** Managing application state, side effects, async operations.
>
> **Read first for:** Store patterns, signal-based state, RxJS integration.

## Decision Guide

| Complexity | Solution |
|-----------|----------|
| Component-local state | `signal()` in the component |
| Shared state (2-3 components) | Service with signals |
| Feature-level state | NgRx Signal Store |
| App-wide complex state with effects | NgRx Signal Store + `rxMethod` |

## Lightweight: Service with Signals

For simple shared state, a service with signals is sufficient:

```typescript
@Injectable({ providedIn: "root" })
export class CartService {
  private _items = signal<CartItem[]>([])

  // Public read-only signal
  items = this._items.asReadonly()
  totalItems = computed(() => this._items().length)
  totalPrice = computed(() =>
    this._items().reduce((sum, item) => sum + item.price * item.quantity, 0)
  )

  addItem(product: Product) {
    this._items.update(items => {
      const existing = items.find(i => i.productId === product.id)
      if (existing) {
        return items.map(i =>
          i.productId === product.id
            ? { ...i, quantity: i.quantity + 1 }
            : i
        )
      }
      return [...items, { productId: product.id, name: product.name, price: product.price, quantity: 1 }]
    })
  }

  removeItem(productId: string) {
    this._items.update(items => items.filter(i => i.productId !== productId))
  }

  clear() {
    this._items.set([])
  }
}
```

## NgRx Signal Store (Feature-Level State)

```typescript
import {
  signalStore,
  withState,
  withComputed,
  withMethods,
  patchState,
} from "@ngrx/signals"
import { computed, inject } from "@angular/core"
import { rxMethod } from "@ngrx/signals/rxjs-interop"
import { pipe, switchMap, tap } from "rxjs"

// 1. Define state interface
interface TodoState {
  todos: Todo[]
  loading: boolean
  filter: "all" | "active" | "completed"
  error: string | null
}

// 2. Initial state
const initialState: TodoState = {
  todos: [],
  loading: false,
  filter: "all",
  error: null,
}

// 3. Create store
export const TodoStore = signalStore(
  { providedIn: "root" },
  withState(initialState),

  withComputed((store) => ({
    filteredTodos: computed(() => {
      const filter = store.filter()
      const todos = store.todos()
      switch (filter) {
        case "active":
          return todos.filter(t => !t.completed)
        case "completed":
          return todos.filter(t => t.completed)
        default:
          return todos
      }
    }),
    completedCount: computed(() =>
      store.todos().filter(t => t.completed).length
    ),
  })),

  withMethods((store, todoService = inject(TodoService)) => ({
    setFilter(filter: "all" | "active" | "completed") {
      patchState(store, { filter })
    },

    addTodo(title: string) {
      const todo: Todo = { id: crypto.randomUUID(), title, completed: false }
      patchState(store, { todos: [...store.todos(), todo] })
    },

    toggleTodo(id: string) {
      patchState(store, {
        todos: store.todos().map(t =>
          t.id === id ? { ...t, completed: !t.completed } : t
        ),
      })
    },

    // Async method using rxMethod for RxJS integration
    loadTodos: rxMethod<void>(
      pipe(
        tap(() => patchState(store, { loading: true, error: null })),
        switchMap(() =>
          todoService.getAll().pipe(
            tap({
              next: (todos) => patchState(store, { todos, loading: false }),
              error: (err) => patchState(store, { error: err.message, loading: false }),
            }),
          ),
        ),
      ),
    ),
  })),
)
```

### Using the Store in a Component

```typescript
@Component({
  standalone: true,
  imports: [FormsModule],
  template: `
    <div>
      <input [(ngModel)]="newTitle" (keyup.enter)="addTodo()" />
      <button (click)="addTodo()">Add</button>
    </div>

    <nav>
      <button (click)="store.setFilter('"'"'all'"'"')">All</button>
      <button (click)="store.setFilter('"'"'active'"'"')">Active</button>
      <button (click)="store.setFilter('"'"'completed'"'"')">Completed</button>
    </nav>

    @if (store.loading()) {
      <app-spinner />
    } @else {
      @for (todo of store.filteredTodos(); track todo.id) {
        <div>
          <input type="checkbox" [checked]="todo.completed"
                 (change)="store.toggleTodo(todo.id)" />
          <span [class.done]="todo.completed">{{ todo.title }}</span>
        </div>
      } @empty {
        <p>No todos found.</p>
      }
    }

    <p>{{ store.completedCount() }} completed</p>
  `,
})
export class TodoListComponent implements OnInit {
  store = inject(TodoStore)
  newTitle = ""

  ngOnInit() {
    this.store.loadTodos()
  }

  addTodo() {
    if (this.newTitle.trim()) {
      this.store.addTodo(this.newTitle.trim())
      this.newTitle = ""
    }
  }
}
```

## RxJS Patterns

### When to Use RxJS vs Signals

| Use Signals | Use RxJS |
|------------|----------|
| Synchronous state | HTTP requests |
| UI state (toggle, count) | WebSocket streams |
| Computed/derived values | Debounced search |
| Component inputs/outputs | Complex async flows |
| Simple shared state | Race conditions handling |

### Common RxJS Patterns

```typescript
// Debounced search
searchControl = new FormControl("")

results$ = this.searchControl.valueChanges.pipe(
  debounceTime(300),
  distinctUntilChanged(),
  filter((q): q is string => q !== null && q.length >= 2),
  switchMap(query => this.searchService.search(query)),
)

// Convert Observable to Signal
import { toSignal } from "@angular/core/rxjs-interop"

results = toSignal(this.results$, { initialValue: [] })
```

### Signal-Observable Interop

```typescript
import { toSignal, toObservable } from "@angular/core/rxjs-interop"

// Observable → Signal
const data = toSignal(this.http.get<Data[]>("/api/data"), {
  initialValue: [],
})

// Signal → Observable (useful for triggering HTTP based on signal changes)
const filter = signal("active")
const filter$ = toObservable(this.filter)

const results = toSignal(
  filter$.pipe(
    debounceTime(300),
    switchMap(f => this.service.getFiltered(f)),
  ),
  { initialValue: [] },
)
```

## Resource API (Angular 19.2+)

For HTTP data fetching with automatic lifecycle management:

```typescript
import { resource, signal } from "@angular/core"

@Component({
  standalone: true,
  template: `
    @if (usersResource.isLoading()) {
      <app-spinner />
    } @else if (usersResource.error()) {
      <p>Error: {{ usersResource.error() }}</p>
    } @else {
      @for (user of usersResource.value(); track user.id) {
        <app-user-card [user]="user" />
      }
    }
  `,
})
export class UsersComponent {
  private http = inject(HttpClient)
  roleFilter = signal("admin")

  usersResource = resource({
    request: () => ({ role: this.roleFilter() }),
    loader: ({ request }) =>
      firstValueFrom(
        this.http.get<User[]>(`/api/users?role=${request.role}`)
      ),
  })
}
```'

# shellcheck disable=SC2034
RULES_CONTENT_CROSS_SERVICE='# Cross-Service Patterns

> **When to use:** Ensuring consistency, understanding shared conventions.
>
> **Read first for:** DI patterns, routing, interceptors, testing, env vars.

## Dependency Injection

### `inject()` Function (Preferred)

Always use the `inject()` function instead of constructor injection:

```typescript
import { inject } from "@angular/core"

@Component({ ... })
export class DashboardComponent {
  // Preferred: inject() function
  private authService = inject(AuthService)
  private router = inject(Router)
  private route = inject(ActivatedRoute)
}
```

### Provider Scopes

| Scope | How | When |
|-------|-----|------|
| App-wide singleton | `@Injectable({ providedIn: "root" })` | Most services |
| Feature-scoped | `providers: [...]` in route config | Feature-specific services |
| Component-scoped | `providers: [...]` in `@Component` | Per-instance services |

### Injection Tokens

```typescript
import { InjectionToken, inject } from "@angular/core"

export const API_BASE_URL = new InjectionToken<string>("API_BASE_URL")

// Provide in app config
export const appConfig: ApplicationConfig = {
  providers: [
    { provide: API_BASE_URL, useValue: "https://api.example.com" },
  ],
}

// Inject in service
@Injectable({ providedIn: "root" })
export class ApiService {
  private baseUrl = inject(API_BASE_URL)
}
```

## Routing

### Route Configuration (Standalone)

```typescript
// app.routes.ts
import { Routes } from "@angular/router"

export const routes: Routes = [
  { path: "", redirectTo: "home", pathMatch: "full" },
  {
    path: "home",
    loadComponent: () => import("./features/home/home.component")
      .then(m => m.HomeComponent),
  },
  {
    path: "dashboard",
    canActivate: [authGuard],
    loadComponent: () => import("./features/dashboard/dashboard.component")
      .then(m => m.DashboardComponent),
  },
  {
    path: "admin",
    canActivate: [authGuard, adminGuard],
    loadChildren: () => import("./features/admin/admin.routes")
      .then(m => m.ADMIN_ROUTES),
    providers: [AdminService],
  },
  { path: "**", redirectTo: "home" },
]
```

### App Configuration (Bootstrap)

```typescript
// app.config.ts
import { ApplicationConfig, provideExperimentalZonelessChangeDetection } from "@angular/core"
import { provideRouter, withComponentInputBinding, withViewTransitions } from "@angular/router"
import { provideHttpClient, withInterceptors } from "@angular/common/http"
import { routes } from "./app.routes"
import { authInterceptor } from "./core/interceptors/auth.interceptor"
import { errorInterceptor } from "./core/interceptors/error.interceptor"

export const appConfig: ApplicationConfig = {
  providers: [
    provideExperimentalZonelessChangeDetection(),
    provideRouter(
      routes,
      withComponentInputBinding(),  // bind route params to component inputs
      withViewTransitions(),        // CSS view transitions on navigation
    ),
    provideHttpClient(
      withInterceptors([authInterceptor, errorInterceptor]),
    ),
  ],
}
```

### Functional Guards

```typescript
// core/guards/auth.guard.ts
import { inject } from "@angular/core"
import { Router, CanActivateFn } from "@angular/router"
import { AuthService } from "../services/auth.service"

export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService)
  const router = inject(Router)

  if (auth.isAuthenticated()) {
    return true
  }
  return router.createUrlTree(["/login"])
}
```

## HTTP Client & Interceptors

### Service Pattern

```typescript
@Injectable({ providedIn: "root" })
export class UserService {
  private http = inject(HttpClient)
  private baseUrl = inject(API_BASE_URL)

  getAll(): Observable<User[]> {
    return this.http.get<User[]>(`${this.baseUrl}/users`)
  }

  getById(id: string): Observable<User> {
    return this.http.get<User>(`${this.baseUrl}/users/${id}`)
  }

  create(user: CreateUserDto): Observable<User> {
    return this.http.post<User>(`${this.baseUrl}/users`, user)
  }

  update(id: string, data: Partial<User>): Observable<User> {
    return this.http.patch<User>(`${this.baseUrl}/users/${id}`, data)
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/users/${id}`)
  }
}
```

### Error Interceptor

```typescript
// core/interceptors/error.interceptor.ts
import { HttpInterceptorFn, HttpErrorResponse } from "@angular/common/http"
import { inject } from "@angular/core"
import { catchError, throwError } from "rxjs"
import { Router } from "@angular/router"

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const router = inject(Router)

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      switch (error.status) {
        case 401:
          router.navigate(["/login"])
          break
        case 403:
          router.navigate(["/forbidden"])
          break
        case 0:
          console.error("Network error — check your connection")
          break
      }
      return throwError(() => error)
    }),
  )
}
```

## Environment Variables

```typescript
// environments/environment.ts (development)
export const environment = {
  production: false,
  apiBaseUrl: "http://localhost:3000/api",
}

// environments/environment.prod.ts (production)
export const environment = {
  production: true,
  apiBaseUrl: "https://api.example.com/api",
}
```

Angular CLI replaces environment files during build via `angular.json` file replacements.

**Secrets are NEVER committed to git.** Use environment files for non-secret config only.
Use a backend proxy or secrets manager for API keys.

## TypeScript Conventions

- **Strict mode** enabled in `tsconfig.json`
- Prefer `interface` for object shapes, `type` for unions/intersections
- Use `unknown` over `any` — narrow types explicitly
- Always type HTTP responses: `this.http.get<User[]>(...)`
- Use `inject()` function, never constructor injection in new code

## Import Conventions

```typescript
// 1. Angular core
import { Component, signal, computed, inject } from "@angular/core"
import { RouterLink, RouterOutlet } from "@angular/router"

// 2. Angular packages
import { HttpClient } from "@angular/common/http"
import { ReactiveFormsModule } from "@angular/forms"

// 3. Third-party
import { signalStore, withState, withMethods } from "@ngrx/signals"

// 4. Internal — feature modules
import { AuthService } from "@/core/services/auth.service"
import type { User } from "@/core/models/user.model"
```

## Testing Patterns

### Component Testing

```typescript
import { ComponentFixture, TestBed } from "@angular/core/testing"
import { provideHttpClientTesting } from "@angular/common/http/testing"
import { provideHttpClient } from "@angular/common/http"

describe("UserCardComponent", () => {
  let component: UserCardComponent
  let fixture: ComponentFixture<UserCardComponent>

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UserCardComponent],
    }).compileComponents()

    fixture = TestBed.createComponent(UserCardComponent)
    component = fixture.componentInstance

    // Set signal inputs via componentRef
    fixture.componentRef.setInput("name", "Alice")
    fixture.componentRef.setInput("email", "alice@example.com")

    fixture.detectChanges()
  })

  it("should display the user name", () => {
    const el: HTMLElement = fixture.nativeElement
    expect(el.textContent).toContain("Alice")
  })
})
```

### Service Testing

```typescript
describe("AuthService", () => {
  let service: AuthService
  let httpTesting: HttpTestingController

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    })
    service = TestBed.inject(AuthService)
    httpTesting = TestBed.inject(HttpTestingController)
  })

  afterEach(() => {
    httpTesting.verify()
  })

  it("should login and store token", () => {
    service.login("user", "pass").subscribe(result => {
      expect(result.token).toBe("abc123")
    })

    const req = httpTesting.expectOne("/api/auth/login")
    expect(req.request.method).toBe("POST")
    req.flush({ token: "abc123" })
  })
})
```

## Logging

```typescript
// Simple console logging with context
console.log("[AuthService]", "User logged in", { userId })
console.error("[HttpError]", "Request failed", { url, status, message })
```

**Never log:** passwords, tokens, PII, full request bodies with sensitive data.'

LINT_LANGUAGES="TypeScript (angular-eslint), HTML templates (angular-eslint), SCSS, JSON, Shell (shellcheck)"
