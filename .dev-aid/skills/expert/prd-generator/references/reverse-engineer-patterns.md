# Reverse-Engineer Patterns — File-to-Section Mapping

## Scanning Order

Scan files in this order to build context progressively:

1. **Project identity** — README.md, package.json, pyproject.toml, Cargo.toml, go.mod
2. **Directory structure** — top-level and first-level subdirectories
3. **Configuration** — docker-compose.yml, .env.example, config files
4. **Route/handler files** — API endpoints, CLI commands, page routes
5. **Test files** — test names reveal features
6. **Git history** — recent branches and commit frequency by path

## Section Mapping

### 1. Problem Statement

**Primary sources:**
- `README.md` — First paragraph, "About", "Why", "Motivation" sections
- `package.json` / `pyproject.toml` — `description` field
- `ABOUT.md` or `docs/about.md`

**Inference heuristics:**
- If README starts with "X is a tool that..." → extract the problem it solves
- If README has a "Why?" or "Motivation" section → use directly
- If no explicit problem statement → mark as `UNCONFIRMED`, use project description

**Confidence rules:**
- Direct "Problem" or "Why" section in README → HIGH
- Extracted from project description field → MEDIUM
- Inferred from project name/type → LOW

### 2. Target Users

**Primary sources:**
- `README.md` — "For", "Who is this for", "Audience" sections
- `CONTRIBUTING.md` — implies developer users
- `docs/getting-started.md` — audience language reveals target users

**Inference heuristics:**
- CLI tool with `bin` field → "developers" persona
- Web app with auth → "end users" + "administrators" personas
- Library with extensive API docs → "developers integrating X" persona
- Presence of `admin/` routes → "administrators" persona

**Confidence rules:**
- Explicit audience section in README → HIGH
- Inferred from project type + auth patterns → MEDIUM
- Generic "developers" assumption → LOW

### 3. Goals and Success Metrics

**Primary sources:**
- `README.md` — "Features", "Benefits" sections (goals, not metrics)
- `CHANGELOG.md` — version history implies milestones achieved

**Inference heuristics:**
- This section is almost always `UNCONFIRMED` in reverse-engineering
- Extract feature benefits from README as goals
- Mark all metrics as `[PLACEHOLDER — add measurable targets]`

**Confidence rules:**
- Nearly always → UNCONFIRMED (metrics require human input)

### 4. Core Features

**Primary sources:**
- Route/endpoint files:
  - Express: `routes/*.js`, `app.get/post/put/delete`
  - FastAPI: `@router.get/post`, `@app.get/post`
  - Django: `urls.py`, `views.py`
  - Rails: `config/routes.rb`, `app/controllers/*`
  - Next.js: `app/*/page.tsx`, `pages/*.tsx`
  - CLI: commands directory, argument parser definitions
- Component directories: `src/components/`, `src/features/`, `src/modules/`
- Test file names: `test_auth.py`, `user.test.ts` → feature discovery

**Inference heuristics:**
- Group related routes into features: `/api/users/*` → "User management"
- Auth-related files (login, register, password reset) → "Authentication"
- Payment/billing directory → "Billing and payments"
- Search endpoint + index config → "Search functionality"
- Upload handlers + storage config → "File management"
- Notification/email templates → "Notifications"
- Admin routes/pages → "Administration panel"

**Confidence rules:**
- Route file with handler implementation → HIGH
- Directory name + dependencies match → MEDIUM
- Test name only, no implementation found → LOW

### 5. Technical Constraints

**Primary sources:**
- `package.json` — `engines`, `dependencies`, `devDependencies`
- `pyproject.toml` — `[tool.poetry.dependencies]`, `python` version
- `Cargo.toml` — `[dependencies]`, `edition`
- `go.mod` — `go` version, `require` block
- `Dockerfile` — base image, runtime version
- `.node-version`, `.python-version`, `.tool-versions`
- `tsconfig.json` — `target`, `module`, `strict`
- `browserslist` config or `package.json` `browserslist` field

**Inference heuristics:**
- Extract language + version from config files
- Extract framework from primary dependency
- Docker presence → containerized deployment
- Kubernetes configs → orchestrated deployment
- Browser targets from browserslist
- CI config → deployment platform inference

**Confidence rules:**
- Explicit version in config file → HIGH
- Inferred from Dockerfile base image → MEDIUM
- Assumed from file extensions → LOW

### 6. Out of Scope

**Primary sources:**
- `README.md` — "Limitations", "Non-goals", "Not supported" sections
- `.github/ISSUE_TEMPLATE/` — issue categories imply scope boundaries
- Closed/rejected issues (if accessible)

**Inference heuristics:**
- This section is usually `LOW` or `UNCONFIRMED` in reverse-engineering
- If README has explicit non-goals → use them
- Otherwise generate based on common exclusions for the project type

**Confidence rules:**
- Explicit "Non-goals" section → HIGH
- Inferred from project type → LOW
- No evidence → UNCONFIRMED

### 7. MVP Scope

**Primary sources:**
- Git log — first release tag, initial feature branches
- `CHANGELOG.md` — v1.0 or v0.1 entries
- GitHub releases (if accessible)

**Inference heuristics:**
- Analyze git log for commit frequency by directory → most-active areas = core features
- First tagged release contents = original MVP
- If no tags → current state IS the MVP (or pre-MVP)
- Features with the most test coverage → likely core/MVP

**Confidence rules:**
- Tagged release with changelog → HIGH
- Inferred from git commit frequency → MEDIUM
- Assumed current state = MVP → LOW

### 8. Architecture Overview

**Primary sources:**
- Directory structure (top 2 levels)
- `docker-compose.yml` — services = components
- Infrastructure configs: `terraform/`, `k8s/`, `helm/`
- `Makefile` or `justfile` — build/deploy targets
- Database migration files → data layer

**Inference heuristics:**
- `docker-compose.yml` services → system components
- Database driver in dependencies + migrations → "Database layer (PostgreSQL/MySQL/etc.)"
- Redis/memcached dependency → "Caching layer"
- Message queue dependency → "Async processing"
- `frontend/` + `backend/` split → "Client-server architecture"
- Single directory → "Monolithic application"
- Multiple service directories → "Microservices/modular architecture"

**Confidence rules:**
- docker-compose with named services → HIGH
- Inferred from directory structure + deps → MEDIUM
- Assumed from project type → LOW

### 9. Dependencies and Risks

**Primary sources:**
- Lock files: `package-lock.json`, `poetry.lock`, `Cargo.lock`, `go.sum`
- External service configs: `.env.example` (API keys imply external dependencies)
- CI/CD files: `.github/workflows/`, `.gitlab-ci.yml`

**Inference heuristics:**
- API keys in .env.example → external service dependency
- Database connection strings → database dependency
- Third-party auth (OAuth, SAML) → identity provider dependency
- CDN/storage configs → cloud service dependency
- Risks: mark all as `[NEEDS REVIEW]` — risk assessment requires human judgment

**Confidence rules:**
- External API keys in .env.example → HIGH (dependency exists)
- Risk assessment → always UNCONFIRMED

### 10. Timeline and Milestones

**Primary sources:**
- `CHANGELOG.md` — release history as past milestones
- GitHub milestones (if accessible)
- `ROADMAP.md`

**Inference heuristics:**
- Almost always `UNCONFIRMED` in reverse-engineering
- If ROADMAP.md exists → use directly
- If CHANGELOG exists → past milestones as reference
- Otherwise → `[TODO: Define timeline]`

**Confidence rules:**
- ROADMAP.md exists → HIGH
- CHANGELOG exists → MEDIUM (past only)
- No evidence → UNCONFIRMED

### 11. Open Questions

**Primary sources:**
- `TODO.md`, `FIXME` comments in code
- GitHub issues labeled "question" or "discussion" (if accessible)
- `README.md` — "Known Issues", "Limitations"

**Inference heuristics:**
- Grep for `TODO:`, `FIXME:`, `HACK:`, `XXX:` in source files
- Group by theme → open questions
- Incomplete implementations (empty handlers, stub functions) → unresolved decisions

**Confidence rules:**
- TODO/FIXME in code → HIGH (question exists)
- Inferred from stubs → MEDIUM
