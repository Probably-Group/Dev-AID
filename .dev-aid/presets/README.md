# Dev-AID Presets

Stack-specific presets that generate substantive rules, troubleshooting playbooks,
smoke tests, and session recovery plans for target projects.

## Bundled Presets (21)

### General

| Preset | Description | Detection |
|--------|-------------|-----------|
| `generic` | Minimal scaffolding for any project | Fallback |

### Python Ecosystem

| Preset | Description | Detection |
|--------|-------------|-----------|
| `python-fastapi` | FastAPI backend — API contracts, Pydantic v2, async DB | `pyproject.toml`/`requirements.txt` with `fastapi` |
| `python-django` | Django 5+ / DRF — ORM, serializers, admin, signals | `pyproject.toml`/`requirements.txt` with `django` |
| `python-data-science` | Jupyter, pandas, scikit-learn, PyTorch — notebook hygiene | `.ipynb` files or `pandas`/`torch` deps |
| `python-celery-workers` | Celery + RabbitMQ/Redis — task patterns, messaging | `celery`/`kombu` deps |

### JavaScript / TypeScript Ecosystem

| Preset | Description | Detection |
|--------|-------------|-----------|
| `typescript-node` | Node.js backend — eslint, vitest, Zod validation | `tsconfig.json` or `typescript` dep |
| `react-nextjs` | React 19 + Next.js 15 App Router — RSC, server actions | `next` dep in `package.json` |
| `vue-nuxt` | Vue 3.5 + Nuxt 4 — Composition API, `useFetch`, Pinia | `nuxt` or `vue` dep |
| `angular` | Angular 19+ — standalone components, signals, NgRx | `@angular/core` dep |
| `svelte-kit` | Svelte 5 + SvelteKit 2 — runes, form actions, load functions | `@sveltejs/kit` or `svelte` dep |
| `fullstack` | Backend + frontend — cross-service contracts, CORS, auth flow | `backend/`+`frontend/` directories |

### Enterprise Backend

| Preset | Description | Detection |
|--------|-------------|-----------|
| `java-spring-boot` | Java 21+ / Spring Boot 4 — JPA, Security, Flyway | `pom.xml`/`build.gradle` with `spring-boot` |
| `dotnet-aspnet` | C# / .NET 9 / ASP.NET Core — Minimal APIs, EF Core | `.csproj` with `Microsoft.AspNetCore` |
| `php-laravel` | PHP 8.3+ / Laravel 11+ — Eloquent, Blade, Artisan | `composer.json` with `laravel/framework` |
| `ruby-rails` | Ruby 3.3+ / Rails 7.2+ — ActiveRecord, Hotwire, RuboCop | `Gemfile` with `rails` |

### Systems Languages

| Preset | Description | Detection |
|--------|-------------|-----------|
| `go-service` | Go 1.23+ — Gin/Echo, structured logging, errgroup | `go.mod` present |
| `rust-service` | Rust / Axum — Tokio async, SQLx, serde, clippy | `Cargo.toml` present |

### Mobile

| Preset | Description | Detection |
|--------|-------------|-----------|
| `flutter-dart` | Flutter 3.24+ / Dart 3.5+ — Riverpod, go_router, freezed | `pubspec.yaml` with `flutter:` |
| `react-native` | React Native 0.76+ / Expo SDK 52+ — Navigation, EAS Build | `react-native` dep in `package.json` |

### Infrastructure

| Preset | Description | Detection |
|--------|-------------|-----------|
| `kubernetes-gitops` | K8s + GitOps — network policies, deployment verification | `kustomize/`, `helm/`, `skaffold.yaml` |
| `talos-kubernetes` | Talos Linux + K8s + Cilium — talosctl, etcd ops, talhelper | `talconfig.yaml` or `talos/` directory |

## How Presets Work

Presets are Bash scripts that define variables consumed by `setup-dev-aid.sh`.
They are **data, not code** — they set configuration variables that the setup
phases use to generate files.

### Variables a Preset Must Define

| Variable | Purpose |
|----------|---------|
| `preset_name` | Short identifier |
| `preset_description` | One-line description |
| `RULES_FILES` | Newline-delimited `filename\|description` pairs |
| `TECH_STACK` | Markdown table rows for technology stack |
| `CONTEXT_LOADING_TABLE` | Task-to-file mapping for context loading |
| `CONTEXT_GROUPS` | Named file bundles for quick loading |
| `WORKFLOW` | Development workflow instructions |
| `PROJECT_OVERVIEW` | Default project description |
| `WORKSPACE_STRUCTURE` | Directory tree (supports `{{PROJECT_NAME}}`) |
| `TROUBLESHOOTING_SECTIONS` | Symptom/Diagnosis/Fix playbook content |
| `MEMORY_TOPICS` | `filename\|description` pairs for memory bank |
| `COMMANDS` | Newline-delimited slash command filenames |
| `RULES_CONTENT_*` | Substantive content per rules file |
| `SMOKE_SCRIPTS` | `filename\|title\|checks_var` entries (optional) |
| `LINT_LANGUAGES` | Supported lint languages description |

### Rules Content Variable Naming

`RULES_CONTENT_<FILENAME_UPPER>` where hyphens become underscores:
- `api-contracts.md` -> `RULES_CONTENT_API_CONTRACTS`
- `cross-service.md` -> `RULES_CONTENT_CROSS_SERVICE`
- `network-policies.md` -> `RULES_CONTENT_NETWORK_POLICIES`

## Community Presets

Place custom presets in `~/.dev-aid/presets/`. They follow the same format as
bundled presets and are auto-discovered during setup.

### Creating a Community Preset

1. Copy any bundled preset as a starting point:
   ```bash
   mkdir -p ~/.dev-aid/presets
   cp .dev-aid/presets/generic.sh ~/.dev-aid/presets/my-stack.sh
   ```

2. Edit `preset_name`, `preset_description`, and all variables

3. Run `setup-dev-aid.sh` — your preset will appear in the selection menu

### Sharing Presets

Community presets are regular Bash scripts. Share them via:
- Git repositories
- Gists
- Copy into `~/.dev-aid/presets/` on any machine
