#!/usr/bin/env bash
# Preset: Go microservice

preset_name="go-service"
preset_description="Go microservice with Gin/Echo/stdlib, PostgreSQL, structured logging"

# Rules files: newline-delimited "filename|description" pairs
RULES_FILES="api-contracts.md|Handler patterns, request binding, validation, middleware, error responses
error-handling.md|Error wrapping, sentinel errors, custom error types, panic recovery
cross-service.md|Context propagation, config, structured logging, testing, linting"

# Technology stack entries
TECH_STACK="| Language | Go 1.23+ |
| HTTP Framework | *Gin / Echo / stdlib net/http* |
| Database | PostgreSQL (pgx / sqlx / GORM) |
| Validation | go-playground/validator v10 |
| Logging | slog (stdlib structured logging) |
| Testing | testing + testify |
| Linting | golangci-lint (go vet, staticcheck, gosec, errcheck) |"

# Context loading table entries
CONTEXT_LOADING_TABLE="| **New API endpoint** | \`.claude/rules/api-contracts.md\`, \`internal/handler/\` |
| **Error handling** | \`.claude/rules/error-handling.md\`, \`internal/apperror/\` |
| **Database changes** | \`internal/repository/\`, \`migrations/\` |
| **Debugging** | \`.claude/rules/troubleshooting.md\` |
| **Architecture decisions** | \`docs/decisions/index.md\` |
| **Cross-service patterns** | \`.claude/rules/cross-service.md\` |"

# Context groups
CONTEXT_GROUPS='### `api`
Read: `.claude/rules/api-contracts.md`, `internal/handler/`, `internal/model/`

### `errors`
Read: `.claude/rules/error-handling.md`, `internal/apperror/`

### `database`
Read: `internal/repository/`, `migrations/`

### `config`
Read: `cmd/`, `internal/config/`, `.env.example`

### `debug`
Read: `.claude/rules/troubleshooting.md`'

# Development workflow
WORKFLOW='```bash
# Setup
go mod download

# Run dev server
go run ./cmd/server/

# Run tests
go test ./...

# Run tests with race detector and coverage
go test -race -coverprofile=coverage.out ./...
go tool cover -html=coverage.out -o coverage.html

# Lint
golangci-lint run ./...

# Vet & format
go vet ./...
gofmt -w .
goimports -w .

# Build
go build -o bin/server ./cmd/server/

# Database migrations (golang-migrate)
migrate -path migrations -database "$DATABASE_URL" up
migrate -path migrations -database "$DATABASE_URL" down 1
migrate create -ext sql -dir migrations -seq add_users_table
```

### API Documentation

If using Swagger:
- Swagger UI: `http://localhost:8080/swagger/index.html`
- Generate: `swag init -g cmd/server/main.go`'

# Project overview
PROJECT_OVERVIEW="Go microservice. All API endpoints are under \`/api/v1/\`. Standard Go project layout."

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
│   │   └── debugging.md
│   └── commands/
│       ├── review.md
│       ├── test.md
│       ├── plan.md
│       ├── smoke.md
│       └── lint.md
├── cmd/
│   └── server/
│       └── main.go
├── internal/
│   ├── handler/
│   ├── model/
│   ├── repository/
│   ├── service/
│   ├── middleware/
│   ├── apperror/
│   └── config/
├── pkg/
├── migrations/
├── tests/
│   └── integration/
├── docs/
│   ├── plans/
│   │   └── .plan-template.md
│   └── decisions/
│       ├── index.md
│       └── adr-template.md
├── scripts/
│   └── smoke-backend.sh
├── go.mod
├── go.sum
├── Makefile
└── Dockerfile'

# Smoke test scripts: "filename|title|checks_variable_name"
SMOKE_SCRIPTS="smoke-backend.sh|Backend Health Checks|SMOKE_BACKEND_CHECKS"

# Smoke test check bodies (referenced by variable name above)
# shellcheck disable=SC2034
SMOKE_BACKEND_CHECKS='section "Application"

if [[ -f "go.mod" ]]; then
  pass "go.mod exists"
else
  fail "go.mod not found — run go mod init"
fi

if [[ -f "cmd/server/main.go" ]]; then
  pass "cmd/server/main.go exists"
else
  fail "cmd/server/main.go not found"
fi

section "Build"

if go build ./... 2>/dev/null; then
  pass "go build ./... succeeds"
else
  fail "go build ./... failed — check compilation errors"
fi

section "Vet & Lint"

if go vet ./... 2>/dev/null; then
  pass "go vet passes"
else
  warn "go vet has findings"
fi

if command -v golangci-lint >/dev/null 2>&1; then
  if golangci-lint run --timeout 60s ./... 2>/dev/null; then
    pass "golangci-lint passes"
  else
    warn "golangci-lint has findings"
  fi
else
  warn "golangci-lint not installed — see https://golangci-lint.run/welcome/install/"
fi

section "Tests"

if go test -short ./... 2>/dev/null; then
  pass "go test passes"
else
  warn "Some tests are failing"
fi'

# Troubleshooting sections
TROUBLESHOOTING_SECTIONS='## 1. Build & Compilation

### Symptom: `cannot find package` or `missing go.sum entry`

**Diagnosis:** Dependencies are not downloaded, or `go.sum` is stale after editing `go.mod`.

**Fix:**
```bash
go mod download
go mod tidy
```

---

### Symptom: `imported and not used` compilation error

**Diagnosis:** Go enforces that every import is used. Unused imports fail compilation.

**Fix:** Remove the unused import, or use `_` for required side-effect imports:
```go
import _ "github.com/lib/pq" // driver registration side effect
```

---

## 2. Runtime & HTTP

### Symptom: Handler returns 404 but route is registered

**Diagnosis:** Route group prefix mismatch or trailing slash inconsistency.
Gin treats `/users` and `/users/` as different routes by default.

**Fix:** Enable `router.RedirectTrailingSlash = true` in Gin. Echo handles this automatically.

---

### Symptom: `context deadline exceeded` on database calls

**Diagnosis:** The `context.Context` timeout is shorter than query execution time,
or the connection pool is exhausted.

**Fix:**
```go
ctx, cancel := context.WithTimeout(ctx, 10*time.Second)
defer cancel()
// Also check pool settings: db.SetMaxOpenConns(25)
```

---

## 3. Testing

### Symptom: Tests pass individually but fail with `go test ./...`

**Diagnosis:** Shared mutable state between tests. Packages run in parallel by default.

**Fix:**
```go
func TestGetUser(t *testing.T) {
    t.Parallel()
    // Use unique ports: net.Listen("tcp", ":0")
}
```

---

*Add entries as you encounter and solve issues. Use the Symptom -> Diagnosis -> Fix format.*'

# Memory topics: "filename|description" pairs
MEMORY_TOPICS="api-patterns.md|Handler patterns, middleware stack, request binding conventions
error-gotchas.md|Error wrapping issues, nil pointer traps, goroutine leak patterns
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

> **When to use:** Adding or modifying HTTP handlers, debugging request/response issues.
>
> **Read first for:** New endpoints, request binding, validation, middleware changes.

## Base URL

- **Production:** `https://api.example.com/api/v1`
- **Local dev:** `http://localhost:8080/api/v1`

## Handler Patterns (Gin)

```go
func (h *Handler) GetUser(c *gin.Context) {
    id := c.Param("id")
    user, err := h.userService.GetByID(c.Request.Context(), id)
    if err != nil {
        handleServiceError(c, err)
        return
    }
    c.JSON(http.StatusOK, user)
}

func (h *Handler) CreateUser(c *gin.Context) {
    var req CreateUserRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(http.StatusBadRequest, ErrorResponse{Detail: "Invalid request body", Code: "BAD_REQUEST"})
        return
    }
    if err := validate.Struct(req); err != nil {
        c.JSON(http.StatusUnprocessableEntity, ErrorResponse{Detail: "Validation failed", Code: "VALIDATION_ERROR"})
        return
    }
    user, err := h.userService.Create(c.Request.Context(), req)
    if err != nil {
        handleServiceError(c, err)
        return
    }
    c.JSON(http.StatusCreated, user)
}
```

## Request Binding & Validation

```go
import "github.com/go-playground/validator/v10"

var validate = validator.New()

type CreateUserRequest struct {
    Name  string `json:"name" validate:"required,min=1,max=255"`
    Email string `json:"email" validate:"required,email"`
    Role  string `json:"role" validate:"required,oneof=admin user viewer"`
}
```

## Middleware

```go
func AuthMiddleware(jwtSecret string) gin.HandlerFunc {
    return func(c *gin.Context) {
        token := c.GetHeader("Authorization")
        if token == "" || !strings.HasPrefix(token, "Bearer ") {
            c.AbortWithStatusJSON(http.StatusUnauthorized, ErrorResponse{
                Detail: "Missing or invalid authorization header", Code: "UNAUTHORIZED",
            })
            return
        }
        claims, err := validateJWT(strings.TrimPrefix(token, "Bearer "), jwtSecret)
        if err != nil {
            c.AbortWithStatusJSON(http.StatusUnauthorized, ErrorResponse{
                Detail: "Invalid or expired token", Code: "UNAUTHORIZED",
            })
            return
        }
        c.Set("user_id", claims.Subject)
        c.Next()
    }
}
```

## Error Response Format

```go
type ErrorResponse struct {
    Detail string            `json:"detail"`
    Code   string            `json:"code"`
    Status int               `json:"status,omitempty"`
    Errors []ValidationError `json:"errors,omitempty"`
}
```

| Status | Code | When |
|--------|------|------|
| 400 | `BAD_REQUEST` | Malformed JSON, missing required fields |
| 401 | `UNAUTHORIZED` | Missing or invalid token |
| 403 | `FORBIDDEN` | Valid token but insufficient permissions |
| 404 | `NOT_FOUND` | Resource does not exist |
| 422 | `VALIDATION_ERROR` | Struct validation failed |
| 429 | `RATE_LIMITED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Unexpected server error |

## Health Endpoints

```go
r.GET("/health", func(c *gin.Context) {
    c.JSON(http.StatusOK, gin.H{"status": "ok"})
})

r.GET("/ready", func(c *gin.Context) {
    if err := db.PingContext(c.Request.Context()); err != nil {
        c.JSON(http.StatusServiceUnavailable, gin.H{"status": "not_ready", "detail": "database unreachable"})
        return
    }
    c.JSON(http.StatusOK, gin.H{"status": "ready"})
})
```'

# shellcheck disable=SC2034
RULES_CONTENT_ERROR_HANDLING='# Error Handling

> **When to use:** Defining, wrapping, or propagating errors across layers.
>
> **Read first for:** Any new service method, repository function, or handler error path.

## Sentinel Errors

```go
package apperror

import "errors"

var (
    ErrNotFound      = errors.New("resource not found")
    ErrAlreadyExists = errors.New("resource already exists")
    ErrUnauthorized  = errors.New("unauthorized")
    ErrForbidden     = errors.New("forbidden")
    ErrValidation    = errors.New("validation failed")
)
```

## Error Wrapping with fmt.Errorf

```go
func (r *UserRepo) GetByID(ctx context.Context, id string) (*User, error) {
    var user User
    err := r.db.QueryRowContext(ctx,
        "SELECT id, name, email FROM users WHERE id = $1", id,
    ).Scan(&user.ID, &user.Name, &user.Email)
    if err != nil {
        if errors.Is(err, sql.ErrNoRows) {
            return nil, fmt.Errorf("user %s: %w", id, apperror.ErrNotFound)
        }
        return nil, fmt.Errorf("querying user %s: %w", id, err)
    }
    return &user, nil
}
```

**Rules:**
- Always use `%w` (not `%v`) when wrapping errors callers need to inspect
- Include context: what operation failed and which identifier was involved

## Custom Error Types

```go
type AppError struct {
    Code    string
    Message string
    Err     error
}

func (e *AppError) Error() string {
    if e.Err != nil {
        return fmt.Sprintf("%s: %s: %v", e.Code, e.Message, e.Err)
    }
    return fmt.Sprintf("%s: %s", e.Code, e.Message)
}

func (e *AppError) Unwrap() error { return e.Err }
```

## errors.Is and errors.As

```go
// Check sentinel
if errors.Is(err, apperror.ErrNotFound) { /* handle */ }

// Extract typed error
var appErr *apperror.AppError
if errors.As(err, &appErr) {
    log.Printf("code: %s, message: %s", appErr.Code, appErr.Message)
}
```

## Panic Recovery Middleware

```go
func RecoveryMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        defer func() {
            if r := recover(); r != nil {
                slog.Error("panic recovered", "panic", r, "stack", string(debug.Stack()))
                c.AbortWithStatusJSON(http.StatusInternalServerError, ErrorResponse{
                    Detail: "Internal server error", Code: "INTERNAL_ERROR",
                })
            }
        }()
        c.Next()
    }
}
```

## Handler Error Mapping

```go
func handleServiceError(c *gin.Context, err error) {
    switch {
    case errors.Is(err, apperror.ErrNotFound):
        c.JSON(http.StatusNotFound, ErrorResponse{Detail: "Not found", Code: "NOT_FOUND"})
    case errors.Is(err, apperror.ErrAlreadyExists):
        c.JSON(http.StatusConflict, ErrorResponse{Detail: "Already exists", Code: "CONFLICT"})
    case errors.Is(err, apperror.ErrUnauthorized):
        c.JSON(http.StatusUnauthorized, ErrorResponse{Detail: "Unauthorized", Code: "UNAUTHORIZED"})
    case errors.Is(err, apperror.ErrValidation):
        c.JSON(http.StatusUnprocessableEntity, ErrorResponse{Detail: err.Error(), Code: "VALIDATION_ERROR"})
    default:
        slog.Error("unhandled error", "error", err, "path", c.Request.URL.Path)
        c.JSON(http.StatusInternalServerError, ErrorResponse{Detail: "Internal server error", Code: "INTERNAL_ERROR"})
    }
}
```

## Defer Best Practices

```go
// Always check defer close errors for writers
func writeFile(path string, data []byte) (retErr error) {
    f, err := os.Create(path)
    if err != nil {
        return fmt.Errorf("creating file: %w", err)
    }
    defer func() {
        if closeErr := f.Close(); closeErr != nil && retErr == nil {
            retErr = fmt.Errorf("closing file: %w", closeErr)
        }
    }()
    if _, err := f.Write(data); err != nil {
        return fmt.Errorf("writing file: %w", err)
    }
    return nil
}
```'

# shellcheck disable=SC2034
RULES_CONTENT_CROSS_SERVICE='# Cross-Service Patterns

> **When to use:** Ensuring consistency, understanding shared conventions.
>
> **Read first for:** Context propagation, config, logging, testing patterns.

## Context Propagation

```go
// Always pass context.Context as the first parameter
func (s *UserService) GetByID(ctx context.Context, id string) (*User, error) {
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()
    return s.repo.GetByID(ctx, id)
}
```

**Rules:**
- Never store `context.Context` in a struct
- Always `defer cancel()` after `context.WithTimeout` / `context.WithCancel`
- Use `context.TODO()` only as a temporary placeholder

## Environment Config

```go
import "github.com/kelseyhightower/envconfig"

type Config struct {
    Port        int    `envconfig:"PORT" default:"8080"`
    DatabaseURL string `envconfig:"DATABASE_URL" required:"true"`
    JWTSecret   string `envconfig:"JWT_SECRET" required:"true"`
    LogLevel    string `envconfig:"LOG_LEVEL" default:"info"`
    Environment string `envconfig:"ENVIRONMENT" default:"development"`
}

func Load() (*Config, error) {
    var cfg Config
    if err := envconfig.Process("", &cfg); err != nil {
        return nil, fmt.Errorf("loading config: %w", err)
    }
    return &cfg, nil
}
```

**Secrets are NEVER committed to git.** Use `.env` locally, secrets manager in production.

## Structured Logging with slog

```go
// Initialize at startup
handler := slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelInfo})
slog.SetDefault(slog.New(handler))

// Usage — always use structured key-value pairs
slog.Info("user created", "user_id", user.ID, "email", user.Email)
slog.Error("query failed", "error", err, "query", "GetUserByID", "user_id", id)
```

**Never log:** passwords, tokens, PII, full request bodies with sensitive data.

## Testing Conventions

### Table-Driven Tests
```go
func TestParseUserRole(t *testing.T) {
    tests := []struct {
        name    string
        input   string
        want    Role
        wantErr bool
    }{
        {name: "valid admin", input: "admin", want: RoleAdmin},
        {name: "empty string", input: "", wantErr: true},
        {name: "unknown role", input: "superadmin", wantErr: true},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := ParseUserRole(tt.input)
            if tt.wantErr {
                assert.Error(t, err)
                return
            }
            assert.NoError(t, err)
            assert.Equal(t, tt.want, got)
        })
    }
}
```

### Interface-Driven Design for Testability
```go
// Define interfaces at the consumer, not the provider
type UserRepository interface {
    GetByID(ctx context.Context, id string) (*User, error)
    Create(ctx context.Context, user *User) error
}

type UserService struct { repo UserRepository }
```

### HTTP Handler Tests
```go
func TestGetUserHandler(t *testing.T) {
    router := gin.New()
    mockSvc := new(mockUserService)
    h := NewHandler(mockSvc)
    router.GET("/api/v1/users/:id", h.GetUser)

    mockSvc.On("GetByID", mock.Anything, "user-123").
        Return(&User{ID: "user-123", Name: "Alice"}, nil)

    req := httptest.NewRequest(http.MethodGet, "/api/v1/users/user-123", nil)
    w := httptest.NewRecorder()
    router.ServeHTTP(w, req)

    assert.Equal(t, http.StatusOK, w.Code)
}
```

## Concurrency Patterns

```go
import "golang.org/x/sync/errgroup"

func (s *DashboardService) GetDashboard(ctx context.Context, userID string) (*Dashboard, error) {
    g, ctx := errgroup.WithContext(ctx)
    var user *User
    var orders []*Order

    g.Go(func() error {
        var err error
        user, err = s.userRepo.GetByID(ctx, userID)
        return err
    })
    g.Go(func() error {
        var err error
        orders, err = s.orderRepo.ListByUser(ctx, userID)
        return err
    })

    if err := g.Wait(); err != nil {
        return nil, fmt.Errorf("fetching dashboard data: %w", err)
    }
    return &Dashboard{User: user, Orders: orders}, nil
}
```

## Go Module Management

```bash
go get github.com/gin-gonic/gin@latest  # Add dependency
go mod tidy                               # Remove unused
govulncheck ./...                         # Check vulnerabilities
```

## Code Generation

```go
//go:generate mockgen -source=internal/service/user.go -destination=internal/service/mock_user.go
//go:embed migrations/*.sql
var migrationsFS embed.FS
```'

LINT_LANGUAGES="Go (golangci-lint: go vet, staticcheck, gosec, errcheck), SQL, YAML, Shell (shellcheck)"
