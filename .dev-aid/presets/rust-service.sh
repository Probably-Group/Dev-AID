#!/usr/bin/env bash
# Preset: Rust service (Axum/Actix + Tokio)

preset_name="rust-service"
preset_description="Rust service with Axum/Actix, Tokio async runtime, SQLx, serde"

# Rules files: newline-delimited "filename|description" pairs
RULES_FILES="api-contracts.md|Axum handler patterns, extractors, middleware, error responses
error-handling.md|thiserror, anyhow, custom AppError, From impls, Result patterns
cross-service.md|Cargo workspace, clippy, serde, config, tracing, testing"

# Technology stack entries
TECH_STACK="| Language | Rust (latest stable) |
| Async Runtime | Tokio |
| HTTP Framework | *Axum / Actix-web* |
| Database | PostgreSQL (SQLx) |
| Serialization | serde + serde_json |
| Error Handling | thiserror (library) + anyhow (application) |
| Logging | tracing + tracing-subscriber |
| Testing | cargo test + tokio::test |
| Linting | clippy + rustfmt |"

# Context loading table entries
CONTEXT_LOADING_TABLE="| **New API endpoint** | \`.claude/rules/api-contracts.md\`, \`src/handlers/\` |
| **Error handling** | \`.claude/rules/error-handling.md\`, \`src/error.rs\` |
| **Database changes** | \`src/repository/\`, \`migrations/\` |
| **Debugging** | \`.claude/rules/troubleshooting.md\` |
| **Architecture decisions** | \`docs/decisions/index.md\` |
| **Cross-service patterns** | \`.claude/rules/cross-service.md\` |"

# Context groups
CONTEXT_GROUPS='### `api`
Read: `.claude/rules/api-contracts.md`, `src/handlers/`, `src/models/`

### `errors`
Read: `.claude/rules/error-handling.md`, `src/error.rs`

### `database`
Read: `src/repository/`, `migrations/`

### `config`
Read: `src/config.rs`, `.env.example`, `Cargo.toml`

### `debug`
Read: `.claude/rules/troubleshooting.md`'

# Development workflow
WORKFLOW='```bash
# Setup
cargo build

# Run dev server (with auto-reload via cargo-watch)
cargo watch -x run

# Run tests
cargo test

# Run tests with output
cargo test -- --nocapture

# Lint & format
cargo clippy -- -D warnings
cargo fmt

# Check without building (faster feedback)
cargo check

# Database migrations (sqlx-cli)
sqlx database create
sqlx migrate run
sqlx migrate add -r add_users_table
sqlx migrate revert

# Prepare offline query checking
cargo sqlx prepare
```

### Performance

```bash
cargo build --release
cargo bench  # if using criterion
```'

# Project overview
PROJECT_OVERVIEW="Rust async service on Tokio. All API endpoints under \`/api/v1/\`. Uses SQLx for compile-time checked queries."

# Workspace structure
WORKSPACE_STRUCTURE='{{PROJECT_NAME}}/
├── CLAUDE.md
├── .claude/
│   ├── rules/
│   │   ├── api-contracts.md
│   │   ├── error-handling.md
│   │   ├── cross-service.md
│   │   └── troubleshooting.md
│   ├── hooks/
│   │   └── lint-on-edit.sh
│   ├── memory/
│   │   ├── MEMORY.md
│   │   ├── api-patterns.md
│   │   ├── error-gotchas.md
│   │   ├── lifetime-notes.md
│   │   └── debugging.md
│   └── commands/
│       ├── review.md
│       ├── test.md
│       ├── plan.md
│       ├── smoke.md
│       └── lint.md
├── src/
│   ├── main.rs
│   ├── lib.rs
│   ├── config.rs
│   ├── error.rs
│   ├── handlers/
│   ├── models/
│   ├── repository/
│   └── services/
├── migrations/
├── tests/
├── docs/
│   ├── plans/
│   │   └── .plan-template.md
│   └── decisions/
│       ├── index.md
│       └── adr-template.md
├── scripts/
│   └── smoke-backend.sh
├── Cargo.toml
├── Cargo.lock
├── .env.example
└── Dockerfile'

# Smoke test scripts: "filename|title|checks_variable_name"
SMOKE_SCRIPTS="smoke-backend.sh|Backend Health Checks|SMOKE_BACKEND_CHECKS"

# Smoke test check bodies (referenced by variable name above)
# shellcheck disable=SC2034
SMOKE_BACKEND_CHECKS='section "Application"

if [[ -f "Cargo.toml" ]]; then
  pass "Cargo.toml exists"
else
  fail "Cargo.toml not found — not a Rust project"
fi

if [[ -f "src/main.rs" ]]; then
  pass "src/main.rs exists"
else
  fail "src/main.rs not found"
fi

section "Build"

if cargo check 2>/dev/null; then
  pass "cargo check succeeds"
else
  fail "cargo check failed — compilation errors"
fi

section "Lint"

if cargo clippy -- -D warnings 2>/dev/null; then
  pass "cargo clippy passes (warnings as errors)"
else
  warn "cargo clippy has warnings"
fi

if cargo fmt --check 2>/dev/null; then
  pass "cargo fmt check passes"
else
  warn "Code is not formatted — run cargo fmt"
fi

section "Tests"

if cargo test 2>/dev/null; then
  pass "cargo test passes"
else
  warn "Some tests are failing"
fi

section "Database"

if command -v sqlx >/dev/null 2>&1; then
  if [[ -d "migrations" ]]; then
    pass "migrations/ directory exists"
  else
    warn "No migrations/ directory found"
  fi
else
  warn "sqlx-cli not installed — cargo install sqlx-cli"
fi'

# Troubleshooting sections
TROUBLESHOOTING_SECTIONS='## 1. Compilation & Borrow Checker

### Symptom: `cannot borrow *self as mutable because it is also borrowed as immutable`

**Diagnosis:** Holding an immutable reference while trying to create a mutable one in the same scope.

**Fix:** Clone to release the borrow, or restructure into separate scopes:
```rust
let val = self.data[key].clone(); // clone releases the borrow
self.cache.insert(key, val);      // now safe to mutate
```
For complex cases, use `RefCell<T>` (single-threaded) or `RwLock<T>` (multi-threaded).

---

### Symptom: `future cannot be sent between threads safely`

**Diagnosis:** An async function holds a non-Send type (e.g., `Rc`, `MutexGuard`) across an `.await` point.

**Fix:** Drop non-Send types before `.await`:
```rust
let data = {
    let guard = mutex.lock().unwrap();
    guard.clone()
}; // guard dropped here
some_async_fn(data).await;
```

---

## 2. Axum / HTTP

### Symptom: `Handler<_, _> is not implemented` for an async function

**Diagnosis:** Extractors in wrong order or return type not implementing `IntoResponse`.
The `Json` extractor consumes the body and MUST be the last parameter.

**Fix:**
```rust
// Correct order: State first, Path/Query, then Json LAST
async fn create_user(
    State(pool): State<PgPool>,
    Path(org_id): Path<String>,
    Json(body): Json<CreateUserRequest>, // body MUST be last
) -> Result<Json<UserResponse>, AppError> { /* ... */ }
```

---

## 3. SQLx / Database

### Symptom: `sqlx compile-time verification failed` in CI

**Diagnosis:** `sqlx-data.json` is stale — generated against a different schema.

**Fix:**
```bash
sqlx migrate run
cargo sqlx prepare
git add sqlx-data.json
```

---

## 4. Testing

### Symptom: Integration tests interfere with each other

**Diagnosis:** Tests share a database and mutate the same rows. `cargo test` runs in parallel.

**Fix:** Use per-test transactions that roll back:
```rust
let mut tx = pool.begin().await.unwrap();
// Run queries against &mut *tx
// tx drops here — transaction rolls back automatically
```

---

*Add entries as you encounter and solve issues. Use the Symptom -> Diagnosis -> Fix format.*'

# Memory topics: "filename|description" pairs
MEMORY_TOPICS="api-patterns.md|Handler patterns, extractor ordering, middleware layer conventions
error-gotchas.md|Error type conversion pitfalls, trait object gotchas, Send bound issues
lifetime-notes.md|Lifetime patterns, borrow checker workarounds, Arc/Clone decisions
debugging.md|Common errors encountered and their solutions"

# Slash commands to scaffold
COMMANDS="review.md
test.md
plan.md
smoke.md
lint.md"

# --- Substantive Rules Content ---

# shellcheck disable=SC2034
RULES_CONTENT_API_CONTRACTS='# API Contracts

> **When to use:** Adding or modifying HTTP handlers, working with extractors or middleware.
>
> **Read first for:** New endpoints, request/response types, extractor patterns.

## Base URL

- **Production:** `https://api.example.com/api/v1`
- **Local dev:** `http://localhost:3000/api/v1`

## Axum Handler Patterns

```rust
use axum::{extract::{State, Path, Query, Json}, http::StatusCode, response::IntoResponse};

async fn get_user(
    State(pool): State<PgPool>,
    Path(user_id): Path<String>,
) -> Result<Json<UserResponse>, AppError> {
    let user = sqlx::query_as!(UserResponse,
        "SELECT id, name, email, created_at FROM users WHERE id = $1", user_id)
        .fetch_optional(&pool).await.map_err(AppError::Database)?
        .ok_or(AppError::NotFound("User not found".into()))?;
    Ok(Json(user))
}

async fn create_user(
    State(pool): State<PgPool>,
    Json(body): Json<CreateUserRequest>,
) -> Result<(StatusCode, Json<UserResponse>), AppError> {
    let user = sqlx::query_as!(UserResponse,
        r#"INSERT INTO users (name, email) VALUES ($1, $2)
           RETURNING id, name, email, created_at"#, body.name, body.email)
        .fetch_one(&pool).await
        .map_err(|e| match e {
            sqlx::Error::Database(ref db_err) if db_err.constraint() == Some("users_email_key") =>
                AppError::Conflict("Email already exists".into()),
            _ => AppError::Database(e),
        })?;
    Ok((StatusCode::CREATED, Json(user)))
}
```

## Request/Response Types

```rust
#[derive(Debug, Serialize, Deserialize)]
pub struct CreateUserRequest {
    pub name: String,
    pub email: String,
    #[serde(default)]
    pub role: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, sqlx::FromRow)]
pub struct UserResponse {
    pub id: String,
    pub name: String,
    pub email: String,
    pub created_at: DateTime<Utc>,
}
```

## Middleware with Tower

```rust
fn build_router(pool: PgPool) -> Router {
    let middleware_stack = ServiceBuilder::new()
        .layer(TraceLayer::new_for_http())
        .layer(TimeoutLayer::new(Duration::from_secs(30)))
        .layer(CompressionLayer::new())
        .layer(CorsLayer::permissive());

    Router::new()
        .route("/api/v1/users", get(list_users).post(create_user))
        .route("/api/v1/users/:id", get(get_user).patch(update_user))
        .route("/health", get(health_check))
        .route("/ready", get(readiness_check))
        .layer(middleware_stack)
        .with_state(pool)
}
```

### Auth middleware
```rust
async fn auth_middleware(
    State(jwt_secret): State<String>,
    mut req: Request,
    next: Next,
) -> Result<Response, AppError> {
    let token = req.headers().get("Authorization")
        .and_then(|v| v.to_str().ok())
        .and_then(|v| v.strip_prefix("Bearer "))
        .ok_or(AppError::Unauthorized("Missing authorization header".into()))?;
    let claims = validate_jwt(token, &jwt_secret)
        .map_err(|_| AppError::Unauthorized("Invalid or expired token".into()))?;
    req.extensions_mut().insert(claims);
    Ok(next.run(req).await)
}
```

## Error Response Format

```rust
#[derive(Debug, Serialize)]
pub struct ErrorResponse {
    pub detail: String,
    pub code: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub status: Option<u16>,
}
```

| Status | Code | When |
|--------|------|------|
| 400 | `BAD_REQUEST` | Malformed JSON, missing fields |
| 401 | `UNAUTHORIZED` | Missing or invalid token |
| 403 | `FORBIDDEN` | Valid token but insufficient permissions |
| 404 | `NOT_FOUND` | Resource does not exist |
| 409 | `CONFLICT` | Unique constraint violation |
| 422 | `VALIDATION_ERROR` | Request body validation failed |
| 500 | `INTERNAL_ERROR` | Unexpected server error |

## Health Endpoints

```rust
async fn health_check() -> impl IntoResponse {
    Json(serde_json::json!({"status": "ok"}))
}

async fn readiness_check(State(pool): State<PgPool>) -> impl IntoResponse {
    match sqlx::query("SELECT 1").execute(&pool).await {
        Ok(_) => (StatusCode::OK, Json(serde_json::json!({"status": "ready"}))),
        Err(_) => (StatusCode::SERVICE_UNAVAILABLE,
            Json(serde_json::json!({"status": "not_ready", "detail": "database unreachable"}))),
    }
}

// Extractor ordering: State first, Path/Query next, Json LAST (consumes body).
// Wrong order gives confusing "Handler is not implemented" error.
```'

# shellcheck disable=SC2034
RULES_CONTENT_ERROR_HANDLING='# Error Handling

> **When to use:** Defining error types, converting between error kinds, propagating with `?`.
>
> **Read first for:** New service methods, repository functions, handler error paths.

## Application Error Type with IntoResponse

```rust
use axum::{http::StatusCode, response::{IntoResponse, Response}, Json};
use thiserror::Error;

#[derive(Debug, Error)]
pub enum AppError {
    #[error("not found: {0}")]
    NotFound(String),
    #[error("unauthorized: {0}")]
    Unauthorized(String),
    #[error("forbidden: {0}")]
    Forbidden(String),
    #[error("conflict: {0}")]
    Conflict(String),
    #[error("validation error: {0}")]
    Validation(String),
    #[error("database error: {0}")]
    Database(#[from] sqlx::Error),
    #[error("internal error: {0}")]
    Internal(#[from] anyhow::Error),
}

impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        let (status, code) = match &self {
            AppError::NotFound(_) => (StatusCode::NOT_FOUND, "NOT_FOUND"),
            AppError::Unauthorized(_) => (StatusCode::UNAUTHORIZED, "UNAUTHORIZED"),
            AppError::Forbidden(_) => (StatusCode::FORBIDDEN, "FORBIDDEN"),
            AppError::Conflict(_) => (StatusCode::CONFLICT, "CONFLICT"),
            AppError::Validation(_) => (StatusCode::UNPROCESSABLE_ENTITY, "VALIDATION_ERROR"),
            AppError::Database(_) | AppError::Internal(_) => {
                tracing::error!(error = %self, "internal error");
                (StatusCode::INTERNAL_SERVER_ERROR, "INTERNAL_ERROR")
            }
        };
        // Never expose internal details to clients
        let detail = match &self {
            AppError::Database(_) | AppError::Internal(_) => "Internal server error".to_string(),
            other => other.to_string(),
        };
        (status, Json(ErrorResponse { detail, code: code.to_string(), status: Some(status.as_u16()) })).into_response()
    }
}
```

## thiserror for Domain Errors

```rust
#[derive(Debug, Error)]
pub enum UserError {
    #[error("user {id} not found")]
    NotFound { id: String },
    #[error("email {email} is already registered")]
    DuplicateEmail { email: String },
    #[error("invalid role: {role}")]
    InvalidRole { role: String },
}
```

**Rules:**
- Use `thiserror` for error enums in library/domain code
- Use `#[from]` for automatic `From` impl (one per source type)
- Use `#[source]` when you want source chain without `From` conversion

## anyhow for Application Code

```rust
use anyhow::{Context, Result};

async fn run_server() -> Result<()> {
    let config = Config::from_env().context("failed to load configuration")?;
    let pool = PgPoolOptions::new()
        .max_connections(config.db_max_connections)
        .connect(&config.database_url).await
        .context("failed to connect to database")?;
    sqlx::migrate!().run(&pool).await.context("failed to run migrations")?;
    axum::serve(listener, build_router(pool)).await.context("server error")?;
    Ok(())
}
```

## From Implementations (Domain -> AppError)

```rust
impl From<UserError> for AppError {
    fn from(err: UserError) -> Self {
        match err {
            UserError::NotFound { id } => AppError::NotFound(format!("User {id} not found")),
            UserError::DuplicateEmail { email } => AppError::Conflict(format!("{email} already registered")),
            UserError::InvalidRole { role } => AppError::Validation(format!("Invalid role: {role}")),
        }
    }
}
```

## The `?` Operator

```rust
async fn get_user(pool: &PgPool, id: &str) -> Result<User, AppError> {
    let user = sqlx::query_as!(User, "SELECT * FROM users WHERE id = $1", id)
        .fetch_optional(pool)
        .await?  // sqlx::Error -> AppError::Database via #[from]
        .ok_or_else(|| AppError::NotFound(format!("User {id} not found")))?;
    Ok(user)
}
```

## Layer-by-Layer Error Strategy

| Layer | Error Type | Strategy |
|-------|-----------|----------|
| **Repository** | `sqlx::Error` | Return raw, or map to domain error |
| **Service** | Custom `thiserror` enum | Domain-specific, no HTTP awareness |
| **Handler** | `AppError` | Convert domain errors via `From`, map to HTTP status |'

# shellcheck disable=SC2034
RULES_CONTENT_CROSS_SERVICE='# Cross-Service Patterns

> **When to use:** Ensuring consistency, understanding shared conventions.
>
> **Read first for:** Cargo setup, clippy config, serde patterns, logging, testing.

## Cargo Workspace

```toml
# Cargo.toml (workspace root)
[workspace]
members = ["crates/api", "crates/domain", "crates/db"]

[workspace.dependencies]
tokio = { version = "1", features = ["full"] }
axum = "0.8"
sqlx = { version = "0.8", features = ["runtime-tokio-rustls", "postgres", "chrono", "uuid"] }
serde = { version = "1", features = ["derive"] }
tracing = "0.1"
anyhow = "1"
thiserror = "2"
```

## Clippy Configuration

```toml
# Cargo.toml
[lints.clippy]
pedantic = { level = "warn", priority = -1 }
module_name_repetitions = "allow"
```

## Serde Patterns

```rust
#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub struct UserResponse {
    pub id: String,
    pub name: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub avatar_url: Option<String>,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum UserRole { Admin, User, Viewer }
```

## Environment Config

```rust
impl Config {
    pub fn from_env() -> anyhow::Result<Self> {
        dotenvy::dotenv().ok();
        Ok(Self {
            port: env::var("PORT").unwrap_or_else(|_| "3000".into()).parse()
                .context("PORT must be a number")?,
            database_url: env::var("DATABASE_URL").context("DATABASE_URL is required")?,
            jwt_secret: env::var("JWT_SECRET").context("JWT_SECRET is required")?,
            log_level: env::var("LOG_LEVEL").unwrap_or_else(|_| "info".into()),
        })
    }
}
```

**Secrets are NEVER committed to git.** Use `.env` locally, secrets manager in production.

## Structured Logging with tracing

```rust
fn init_tracing(log_level: &str) {
    tracing_subscriber::registry()
        .with(EnvFilter::try_from_default_env()
            .unwrap_or_else(|_| EnvFilter::new(format!("{}={},tower_http=info", env!("CARGO_CRATE_NAME"), log_level))))
        .with(tracing_subscriber::fmt::layer().json())
        .init();
}

// Use #[instrument] for automatic span creation
#[instrument(skip(pool), fields(user_id = %id))]
async fn get_user(pool: &PgPool, id: &str) -> Result<User, AppError> {
    info!("fetching user");
    // ...
}
```

**Never log:** passwords, tokens, PII, full request bodies with sensitive data.

## Testing Patterns

### Async tests with sqlx
```rust
#[sqlx::test]
async fn test_create_user(pool: PgPool) {
    sqlx::migrate!().run(&pool).await.unwrap();
    let user = create_user(&pool, "Alice", "alice@example.com").await.unwrap();
    assert_eq!(user.name, "Alice");
}
```

### Handler integration tests
```rust
use tower::ServiceExt;

#[tokio::test]
async fn test_get_user_not_found() {
    let pool = setup_test_pool().await;
    let app = build_router(pool);
    let response = app.oneshot(
        Request::builder().uri("/api/v1/users/nonexistent").body(Body::empty()).unwrap()
    ).await.unwrap();
    assert_eq!(response.status(), StatusCode::NOT_FOUND);
}
```

## Shared State with Arc

```rust
#[derive(Clone)]
pub struct AppState {
    pub pool: PgPool,
    pub config: Arc<Config>,
}

Router::new().route("/api/v1/users", get(list_users)).with_state(state);
```

## Dependency Management

```bash
cargo add axum                  # Add dependency
cargo add tokio --features full # With features
cargo update                    # Update all
cargo audit                     # Check vulnerabilities
```

## Security Best Practices

### Input Validation
- Validate ALL user input at API boundaries using Axum extractors with serde deserialization
- Use `validator` crate for struct-level validation with `#[derive(Validate)]`
- Reject unexpected fields — use `#[serde(deny_unknown_fields)]` on request structs

```rust
use validator::Validate;

#[derive(Debug, Deserialize, Validate)]
#[serde(deny_unknown_fields)]
pub struct CreateUserRequest {
    #[validate(length(min = 1, max = 255))]
    pub name: String,
    #[validate(email)]
    pub email: String,
}
```

### SQL Injection Prevention
- NEVER concatenate user input into queries
- Use SQLx compile-time checked queries with `$1` parameterized placeholders

```rust
// SAFE — parameterized query (compile-time checked)
let user = sqlx::query_as!(User,
    "SELECT * FROM users WHERE email = $1", email
).fetch_optional(&pool).await?;

// UNSAFE — format string (NEVER do this)
// let q = format!("SELECT * FROM users WHERE email = '\''{}'\''", email);
```

### Rate Limiting
- Use `tower::limit::RateLimitLayer` or `governor` crate for rate limiting
- Apply stricter limits to auth endpoints (5 requests/min) and general API (100 requests/min)

```rust
use tower::limit::RateLimitLayer;
use std::time::Duration;

Router::new()
    .route("/api/v1/auth/login", post(login))
    .layer(RateLimitLayer::new(5, Duration::from_secs(60)))
```

### CORS Configuration
- Use `tower_http::cors::CorsLayer` — never use `CorsLayer::permissive()` in production
- Whitelist specific origins

```rust
use tower_http::cors::{CorsLayer, AllowOrigin};

let cors = CorsLayer::new()
    .allow_origin(AllowOrigin::exact("https://app.example.com".parse().unwrap()))
    .allow_methods([Method::GET, Method::POST, Method::PUT, Method::DELETE])
    .allow_headers([AUTHORIZATION, CONTENT_TYPE])
    .allow_credentials(true)
    .max_age(Duration::from_secs(600));
```

### Secrets Management
- Never commit secrets to git — use `.env` locally, secrets manager in production
- Load secrets via `dotenvy` from environment variables
- Rotate secrets immediately on suspected compromise

### Dependency Scanning
- Run `cargo audit` in CI on every PR to detect known vulnerabilities
- Run `cargo deny check` for license and advisory checks
- Review `Cargo.lock` changes in PRs

### HTTPS / TLS
- Enforce HTTPS in production — use `axum_server::tls_rustls` for TLS termination
- Use HSTS header: `Strict-Transport-Security: max-age=63072000; includeSubDomains`
- Configure `rustls` with TLS 1.2+ minimum

## Performance Checklist

### Database Performance
- Prevent N+1 queries: use JOINs or batch-fetch with `WHERE id = ANY($1)` in SQLx
- Add database indexes for frequently queried columns
- Use connection pooling via `PgPoolOptions::new().max_connections(25)`
- Profile slow queries with `EXPLAIN ANALYZE` and enable query logging in PostgreSQL

### Caching Strategy
- Use Redis (`fred` or `deadpool-redis`) or in-memory caches (`moka`, `mini-moka`)
- Cache expensive computations and external API responses
- Use cache invalidation strategies: TTL for read-heavy data, event-based for write-heavy data

```rust
use moka::future::Cache;

let cache: Cache<String, User> = Cache::builder()
    .max_capacity(10_000)
    .time_to_live(Duration::from_secs(300))
    .build();
```

### API Response Optimization
- Always paginate list endpoints — use `LIMIT`/`OFFSET` or cursor-based pagination
- Compress responses with `tower_http::compression::CompressionLayer`
- Set appropriate `Cache-Control` headers for cacheable responses
- Use `tokio::time::timeout` to prevent slow queries from blocking the runtime'

LINT_LANGUAGES="Rust (cargo clippy + rustfmt), TOML, SQL, YAML, Shell (shellcheck)"
