#!/usr/bin/env bash
# Preset: C# / .NET / ASP.NET Core backend

preset_name="dotnet-aspnet"
preset_description="C# / .NET 9+ / ASP.NET Core Minimal APIs with Entity Framework Core"

# Rules files: newline-delimited "filename|description" pairs
RULES_FILES="api-contracts.md|Minimal API endpoints, TypedResults, validation, ProblemDetails error format
database.md|EF Core DbContext, migrations, LINQ queries, repository pattern
cross-service.md|Dependency injection, middleware, configuration, logging, testing"

# Technology stack entries
TECH_STACK="| Backend API | ASP.NET Core Minimal APIs |
| Language | C# 13+ (.NET 9+), nullable reference types |
| ORM | Entity Framework Core |
| Migrations | dotnet ef (EF Core Migrations) |
| Validation | *FluentValidation / DataAnnotations* |
| Logging | Serilog / Microsoft.Extensions.Logging |
| Testing | xUnit, WebApplicationFactory, NSubstitute |
| Build | dotnet CLI |"

# Context loading table entries
CONTEXT_LOADING_TABLE="| **New API endpoint** | \`.claude/rules/api-contracts.md\`, \`src/Endpoints/\` |
| **Database changes** | \`.claude/rules/database.md\`, \`src/Data/\`, \`src/Entities/\` |
| **Auth / middleware** | \`.claude/rules/cross-service.md\` (Security section), \`src/Middleware/\` |
| **Debugging** | \`.claude/rules/troubleshooting.md\` |
| **Architecture decisions** | \`docs/decisions/index.md\` |
| **Cross-service patterns** | \`.claude/rules/cross-service.md\` |"

# Context groups
CONTEXT_GROUPS='### `api`
Read: `.claude/rules/api-contracts.md`, `src/Endpoints/`, `src/Models/`

### `database`
Read: `.claude/rules/database.md`, `src/Data/`, `src/Entities/`

### `auth`
Read: `.claude/rules/cross-service.md` (Security section), `src/Middleware/`

### `debug`
Read: `.claude/rules/troubleshooting.md`'

# Development workflow
WORKFLOW='```bash
# Setup
dotnet restore

# Run dev server (with hot reload)
dotnet watch run --project src/

# Run without hot reload
dotnet run --project src/

# Run tests
dotnet test

# Run tests with coverage
dotnet test --collect:"XPlat Code Coverage"

# Add EF Core migration
dotnet ef migrations add AddUsersTable --project src/

# Apply migrations
dotnet ef database update --project src/

# Build release
dotnet publish -c Release -o ./publish

# Format code
dotnet format

# Check for code style issues without fixing
dotnet format --verify-no-changes
```

### API Documentation

ASP.NET Core auto-generates OpenAPI docs:
- Swagger UI: `https://localhost:5001/swagger`
- OpenAPI JSON: `https://localhost:5001/openapi/v1.json`'

# Project overview
PROJECT_OVERVIEW="ASP.NET Core Minimal API service. All endpoints are under \`/api/v1/\`."

# Workspace structure
WORKSPACE_STRUCTURE='{{PROJECT_NAME}}/
├── CLAUDE.md
├── .claude/
│   ├── rules/
│   │   ├── api-contracts.md
│   │   ├── database.md
│   │   ├── cross-service.md
│   │   └── troubleshooting.md
│   ├── hooks/
│   │   └── lint-on-edit.sh
│   ├── memory/
│   │   ├── MEMORY.md
│   │   ├── api-patterns.md
│   │   ├── database-gotchas.md
│   │   └── debugging.md
│   └── commands/
│       ├── review.md
│       ├── test.md
│       ├── plan.md
│       ├── smoke.md
│       └── lint.md
├── src/
│   ├── Program.cs
│   ├── Endpoints/
│   ├── Entities/
│   ├── Data/
│   │   ├── AppDbContext.cs
│   │   └── Migrations/
│   ├── Models/
│   ├── Services/
│   ├── Middleware/
│   ├── Configuration/
│   ├── appsettings.json
│   └── appsettings.Development.json
├── tests/
│   ├── Unit/
│   └── Integration/
├── docs/
│   ├── plans/
│   │   └── .plan-template.md
│   └── decisions/
│       ├── index.md
│       └── adr-template.md
├── scripts/
│   └── smoke-backend.sh
├── {{PROJECT_NAME}}.sln
└── global.json'

# Smoke test scripts: "filename|title|checks_variable_name"
SMOKE_SCRIPTS="smoke-backend.sh|Backend Health Checks|SMOKE_BACKEND_CHECKS"

# Smoke test check bodies (referenced by variable name above)
# shellcheck disable=SC2034
SMOKE_BACKEND_CHECKS='section ".NET Runtime"

if command -v dotnet >/dev/null 2>&1; then
  dotnet_ver=$(dotnet --version 2>&1)
  pass ".NET SDK installed: $dotnet_ver"
  dotnet_major=$(echo "$dotnet_ver" | cut -d. -f1)
  if [[ "$dotnet_major" -ge 9 ]]; then
    pass ".NET SDK version >= 9"
  else
    warn ".NET SDK version < 9 — recommend .NET 9 or later"
  fi
else
  fail ".NET SDK not found — install from https://dotnet.microsoft.com/download"
fi

section "Project Structure"

sln_count=$(find . -maxdepth 1 -name "*.sln" 2>/dev/null | wc -l | tr -d " ")
if [[ "$sln_count" -gt 0 ]]; then
  pass "Solution file (.sln) found"
else
  warn "No .sln file found in project root"
fi

if find . -name "*.csproj" 2>/dev/null | grep -q .; then
  pass "C# project file (.csproj) found"
else
  fail "No .csproj file found"
fi

if [[ -f "src/Program.cs" ]] || find src -name "Program.cs" 2>/dev/null | grep -q .; then
  pass "Program.cs entry point found"
else
  warn "No Program.cs found in src/"
fi

section "Configuration"

if [[ -f "src/appsettings.json" ]] || find src -name "appsettings.json" 2>/dev/null | grep -q .; then
  pass "appsettings.json exists"
else
  warn "No appsettings.json found"
fi

if [[ -f "global.json" ]]; then
  pass "global.json exists (SDK version pinned)"
else
  warn "No global.json — consider pinning SDK version"
fi

section "Build"

if dotnet build --nologo -v q 2>/dev/null; then
  pass "dotnet build succeeds"
else
  warn "dotnet build failed — run: dotnet build"
fi

section "Tests"

if find tests -name "*Tests.cs" -o -name "*Test.cs" 2>/dev/null | grep -q .; then
  pass "Test files found"
  if dotnet test --nologo -v q 2>/dev/null; then
    pass "dotnet test passes"
  else
    warn "Some tests failing — run: dotnet test"
  fi
else
  warn "No test files found in tests/"
fi

section "EF Core Tools"

if dotnet ef --version 2>/dev/null | grep -q "Entity Framework"; then
  pass "EF Core tools installed"
else
  warn "EF Core tools not installed — run: dotnet tool install --global dotnet-ef"
fi'

# Troubleshooting sections
TROUBLESHOOTING_SECTIONS='## 1. ASP.NET Core Startup

### Symptom: `System.InvalidOperationException: Unable to resolve service for type`

**Diagnosis:** A service was injected via constructor or parameter but was never registered
in the DI container. This is the most common ASP.NET Core startup error.

**Fix:**
```csharp
// Register the missing service in Program.cs
builder.Services.AddScoped<IUserService, UserService>();

// Or if it is a DbContext:
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("Default")));

// Check the full exception message — it tells you exactly which type is unresolved
```

---

### Symptom: `HTTPS development certificate not trusted` warning on startup

**Diagnosis:** The .NET HTTPS development certificate has not been trusted on this machine.

**Fix:**
```bash
dotnet dev-certs https --trust
# Restart the application after trusting
```

---

## 2. Entity Framework Core / Database

### Symptom: `Microsoft.EntityFrameworkCore.DbUpdateException` — duplicate key violation

**Diagnosis:** Attempting to insert an entity with a primary key or unique constraint
that already exists. Common when manually setting IDs or replaying seed data.

**Fix:**
```csharp
// Check if entity exists before inserting
if (!await context.Users.AnyAsync(u => u.Email == request.Email))
{
    context.Users.Add(newUser);
    await context.SaveChangesAsync();
}

// Or use upsert pattern:
var existing = await context.Users.FindAsync(id);
if (existing is not null)
{
    context.Entry(existing).CurrentValues.SetValues(updatedUser);
}
else
{
    context.Users.Add(updatedUser);
}
await context.SaveChangesAsync();
```

---

### Symptom: `No migrations were found` or `The migration has already been applied`

**Diagnosis:** EF Core migration tooling cannot find the migrations assembly, or
migrations are out of sync with the database.

**Fix:**
```bash
# List current migration status
dotnet ef migrations list --project src/

# If migrations are missing, add a new one
dotnet ef migrations add FixSchema --project src/

# If the database is ahead of migrations, remove the last migration
dotnet ef migrations remove --project src/

# Nuclear option — reset migration history (DEV ONLY)
dotnet ef database drop --project src/
dotnet ef database update --project src/
```

---

## 3. Minimal API Routing

### Symptom: 404 Not Found on endpoints that are defined

**Diagnosis:** Endpoints are defined but the route group prefix does not match the
request URL, or `app.MapGet(...)` was called after `app.Run()`.

**Fix:**
```csharp
// Ensure endpoint mapping happens BEFORE app.Run()
var app = builder.Build();

// Middleware pipeline
app.UseAuthentication();
app.UseAuthorization();

// Map endpoints BEFORE Run
app.MapUserEndpoints();  // extension method
app.MapHealthEndpoints();

app.Run();  // must be last
```

---

## 4. Testing

### Symptom: `WebApplicationFactory` tests fail with `Could not find assembly`

**Diagnosis:** The test project cannot locate the main application assembly. This
happens when the entry point class is `Program` with top-level statements and there
is no explicit class to reference.

**Fix:**
```csharp
// Add to the bottom of Program.cs (or a separate file in the src project):
public partial class Program { }

// In your test project, reference it:
public class ApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public ApiTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task GetUsers_ReturnsOk()
    {
        var response = await _client.GetAsync("/api/v1/users");
        response.EnsureSuccessStatusCode();
    }
}
```

---

### Symptom: Tests intermittently fail due to database state

**Diagnosis:** Integration tests share database state. One test inserts data that
causes another test to fail due to unique constraint violations or unexpected counts.

**Fix:**
```csharp
// Use Respawn or manual cleanup in test fixtures
public class DatabaseFixture : IAsyncLifetime
{
    public async Task InitializeAsync()
    {
        // Reset database before each test class
        await using var context = CreateDbContext();
        await context.Database.EnsureDeletedAsync();
        await context.Database.EnsureCreatedAsync();
    }

    public Task DisposeAsync() => Task.CompletedTask;
}
```

---

*Add entries as you encounter and solve issues. Use the Symptom -> Diagnosis -> Fix format.*'

# Memory topics: "filename|description" pairs
MEMORY_TOPICS="api-patterns.md|Endpoint patterns, validation conventions, middleware pipeline
database-gotchas.md|EF Core query issues, migration problems, LINQ pitfalls
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

> **When to use:** Adding or modifying Minimal API endpoints, validation, error handling.
>
> **Read first for:** Any new endpoint, request/response shape changes, error handling.

## Base URL

- **Production:** `https://api.example.com/api/v1`
- **Local dev:** `https://localhost:5001/api/v1`

## Authentication

All protected endpoints require `Authorization: Bearer <jwt>` header. JWT is validated
by the built-in `AddAuthentication().AddJwtBearer()` middleware.

```csharp
// Program.cs — JWT configuration
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidIssuer = builder.Configuration["Jwt:Issuer"],
            ValidateAudience = true,
            ValidAudience = builder.Configuration["Jwt:Audience"],
            ValidateIssuerSigningKey = true,
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes(builder.Configuration["Jwt:Secret"]!)),
            ValidateLifetime = true,
            ClockSkew = TimeSpan.Zero
        };
    });

builder.Services.AddAuthorization();
```

## Minimal API Endpoint Patterns

### Organizing endpoints with extension methods

```csharp
// Endpoints/UserEndpoints.cs
public static class UserEndpoints
{
    public static void MapUserEndpoints(this WebApplication app)
    {
        var group = app.MapGroup("/api/v1/users")
            .WithTags("Users")
            .RequireAuthorization();

        group.MapGet("/", GetAll);
        group.MapGet("/{id:int}", GetById);
        group.MapPost("/", Create);
        group.MapPut("/{id:int}", Update);
        group.MapDelete("/{id:int}", Delete);
    }

    private static async Task<Results<Ok<PagedResponse<UserResponse>>, BadRequest>>
        GetAll([AsParameters] PaginationQuery query, IUserService service)
    {
        var result = await service.GetAllAsync(query.Page, query.Size, query.Sort);
        return TypedResults.Ok(result);
    }

    private static async Task<Results<Ok<UserResponse>, NotFound<ProblemDetails>>>
        GetById(int id, IUserService service)
    {
        var user = await service.GetByIdAsync(id);
        return user is not null
            ? TypedResults.Ok(user)
            : TypedResults.NotFound(new ProblemDetails
              {
                  Title = "User not found",
                  Detail = $"No user with ID {id}",
                  Status = 404
              });
    }

    private static async Task<Results<Created<UserResponse>, ValidationProblem>>
        Create(UserCreateRequest request, IValidator<UserCreateRequest> validator,
               IUserService service)
    {
        var validation = await validator.ValidateAsync(request);
        if (!validation.IsValid)
            return TypedResults.ValidationProblem(validation.ToDictionary());

        var user = await service.CreateAsync(request);
        return TypedResults.Created($"/api/v1/users/{user.Id}", user);
    }

    private static async Task<Results<Ok<UserResponse>, NotFound<ProblemDetails>, ValidationProblem>>
        Update(int id, UserUpdateRequest request, IValidator<UserUpdateRequest> validator,
               IUserService service)
    {
        var validation = await validator.ValidateAsync(request);
        if (!validation.IsValid)
            return TypedResults.ValidationProblem(validation.ToDictionary());

        var user = await service.UpdateAsync(id, request);
        return user is not null
            ? TypedResults.Ok(user)
            : TypedResults.NotFound(new ProblemDetails
              {
                  Title = "User not found",
                  Detail = $"No user with ID {id}",
                  Status = 404
              });
    }

    private static async Task<Results<NoContent, NotFound<ProblemDetails>>>
        Delete(int id, IUserService service)
    {
        var deleted = await service.DeleteAsync(id);
        return deleted
            ? TypedResults.NoContent()
            : TypedResults.NotFound(new ProblemDetails
              {
                  Title = "User not found",
                  Detail = $"No user with ID {id}",
                  Status = 404
              });
    }
}
```

### Parameter binding with [AsParameters]

```csharp
// Models/PaginationQuery.cs
public record PaginationQuery(
    [property: Range(0, int.MaxValue)] int Page = 0,
    [property: Range(1, 100)] int Size = 20,
    string? Sort = "CreatedAt"
);
```

## DTO Patterns with Records

```csharp
// Models/UserModels.cs
public record UserCreateRequest(
    [property: Required, StringLength(255)] string Name,
    [property: Required, EmailAddress] string Email,
    [property: Required, MinLength(8)] string Password
);

public record UserUpdateRequest(
    [property: StringLength(255)] string? Name,
    [property: EmailAddress] string? Email
);

public record UserResponse(
    int Id,
    string Name,
    string Email,
    DateTimeOffset CreatedAt,
    DateTimeOffset UpdatedAt
)
{
    public static UserResponse From(User entity) => new(
        entity.Id, entity.Name, entity.Email,
        entity.CreatedAt, entity.UpdatedAt
    );
}

public record PagedResponse<T>(
    List<T> Items,
    int Page,
    int Size,
    int TotalCount,
    int TotalPages
);
```

## Validation with FluentValidation

```csharp
public class UserCreateRequestValidator : AbstractValidator<UserCreateRequest>
{
    public UserCreateRequestValidator(AppDbContext context)
    {
        RuleFor(x => x.Name).NotEmpty().MaximumLength(255);
        RuleFor(x => x.Email).NotEmpty().EmailAddress()
            .MustAsync(async (email, ct) =>
                !await context.Users.AnyAsync(u => u.Email == email, ct))
            .WithMessage("Email already in use");
        RuleFor(x => x.Password).NotEmpty().MinimumLength(8);
    }
}

// Register in Program.cs
builder.Services.AddValidatorsFromAssemblyContaining<Program>();
```

## Error Response Format — ProblemDetails (RFC 9457)

```json
{
  "type": "https://tools.ietf.org/html/rfc9110#section-15.5.5",
  "title": "Not Found",
  "status": 404,
  "detail": "No user with ID 42",
  "instance": "/api/v1/users/42"
}
```

Configure globally:
```csharp
builder.Services.AddProblemDetails(options =>
{
    options.CustomizeProblemDetails = context =>
    {
        context.ProblemDetails.Extensions["traceId"] =
            context.HttpContext.TraceIdentifier;
    };
});
```

| Status | Title | When |
|--------|-------|------|
| 400 | `Bad Request` | Malformed input |
| 401 | `Unauthorized` | Missing or invalid token |
| 403 | `Forbidden` | Valid token but insufficient claims |
| 404 | `Not Found` | Resource does not exist |
| 422 | `Validation Error` | FluentValidation / DataAnnotations failed |
| 429 | `Too Many Requests` | Rate limit exceeded |

## Health Endpoints

```csharp
builder.Services.AddHealthChecks()
    .AddNpgSql(connectionString, name: "postgres")
    .AddRedis(redisConnection, name: "redis");

app.MapHealthChecks("/health", new HealthCheckOptions
{
    Predicate = _ => false  // liveness — no dependency checks
});
app.MapHealthChecks("/ready", new HealthCheckOptions
{
    ResponseWriter = UIResponseWriter.WriteHealthCheckUIResponse
});
```'

# shellcheck disable=SC2034
RULES_CONTENT_DATABASE='# Database Patterns

> **When to use:** Schema changes, new queries, migration work, EF Core entity changes.
>
> **Read first for:** Any database-related task.

## DbContext Configuration

```csharp
// Data/AppDbContext.cs
public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    public DbSet<User> Users => Set<User>();
    public DbSet<Order> Orders => Set<Order>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);
    }

    // Automatic audit timestamps
    public override async Task<int> SaveChangesAsync(CancellationToken ct = default)
    {
        foreach (var entry in ChangeTracker.Entries<BaseEntity>())
        {
            if (entry.State == EntityState.Added)
                entry.Entity.CreatedAt = DateTimeOffset.UtcNow;
            if (entry.State is EntityState.Added or EntityState.Modified)
                entry.Entity.UpdatedAt = DateTimeOffset.UtcNow;
        }
        return await base.SaveChangesAsync(ct);
    }
}

// Register in Program.cs
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("Default")));
```

## Entity Patterns

```csharp
// Entities/BaseEntity.cs
public abstract class BaseEntity
{
    public int Id { get; set; }
    public DateTimeOffset CreatedAt { get; set; }
    public DateTimeOffset UpdatedAt { get; set; }
}

// Entities/User.cs
public class User : BaseEntity
{
    public required string Name { get; set; }
    public required string Email { get; set; }
    public required string PasswordHash { get; set; }
    public ICollection<Order> Orders { get; set; } = new List<Order>();
}

// Entities/Order.cs
public class Order : BaseEntity
{
    public required string Description { get; set; }
    public decimal Total { get; set; }
    public int UserId { get; set; }
    public User User { get; set; } = null!;
    public ICollection<OrderItem> Items { get; set; } = new List<OrderItem>();
}
```

### Entity Configuration (Fluent API)

```csharp
// Data/Configurations/UserConfiguration.cs
public class UserConfiguration : IEntityTypeConfiguration<User>
{
    public void Configure(EntityTypeBuilder<User> builder)
    {
        builder.ToTable("users");
        builder.HasKey(u => u.Id);
        builder.Property(u => u.Name).IsRequired().HasMaxLength(255);
        builder.Property(u => u.Email).IsRequired().HasMaxLength(255);
        builder.HasIndex(u => u.Email).IsUnique();
        builder.Property(u => u.PasswordHash).IsRequired();
        builder.HasMany(u => u.Orders)
            .WithOne(o => o.User)
            .HasForeignKey(o => o.UserId)
            .OnDelete(DeleteBehavior.Cascade);
    }
}
```

### Entity Conventions

- Table names: lowercase plural (`users`, `orders`, `organizations`)
- Primary keys: `Id` (auto-increment `int` or GUID)
- Timestamps: `CreatedAt`, `UpdatedAt` (UTC `DateTimeOffset`, auto-set in `SaveChangesAsync`)
- Foreign keys: `<EntityName>Id` (e.g., `UserId`, `OrganizationId`)
- Navigation properties: always initialize collections with `new List<T>()`
- Use `required` keyword for non-nullable reference properties

## Repository Pattern (optional)

```csharp
// Services/IRepository.cs
public interface IRepository<T> where T : BaseEntity
{
    Task<T?> GetByIdAsync(int id, CancellationToken ct = default);
    Task<(List<T> Items, int TotalCount)> GetPagedAsync(int page, int size, CancellationToken ct = default);
    Task<T> AddAsync(T entity, CancellationToken ct = default);
    Task UpdateAsync(T entity, CancellationToken ct = default);
    Task DeleteAsync(T entity, CancellationToken ct = default);
}

// Services/Repository.cs
public class Repository<T> : IRepository<T> where T : BaseEntity
{
    private readonly AppDbContext _context;
    private readonly DbSet<T> _dbSet;

    public Repository(AppDbContext context)
    {
        _context = context;
        _dbSet = context.Set<T>();
    }

    public async Task<T?> GetByIdAsync(int id, CancellationToken ct = default)
        => await _dbSet.FindAsync([id], ct);

    public async Task<(List<T> Items, int TotalCount)> GetPagedAsync(
        int page, int size, CancellationToken ct = default)
    {
        var total = await _dbSet.CountAsync(ct);
        var items = await _dbSet
            .OrderByDescending(e => e.CreatedAt)
            .Skip(page * size)
            .Take(size)
            .ToListAsync(ct);
        return (items, total);
    }

    public async Task<T> AddAsync(T entity, CancellationToken ct = default)
    {
        _dbSet.Add(entity);
        await _context.SaveChangesAsync(ct);
        return entity;
    }

    public async Task UpdateAsync(T entity, CancellationToken ct = default)
    {
        _dbSet.Update(entity);
        await _context.SaveChangesAsync(ct);
    }

    public async Task DeleteAsync(T entity, CancellationToken ct = default)
    {
        _dbSet.Remove(entity);
        await _context.SaveChangesAsync(ct);
    }
}
```

## LINQ Query Patterns

### IQueryable optimization — build queries lazily, materialize once

```csharp
public async Task<(List<UserResponse> Items, int TotalCount)> SearchAsync(
    string? query, string? role, int page, int size, CancellationToken ct)
{
    IQueryable<User> users = _context.Users.AsNoTracking();

    if (!string.IsNullOrWhiteSpace(query))
        users = users.Where(u => u.Name.Contains(query) || u.Email.Contains(query));

    if (!string.IsNullOrWhiteSpace(role))
        users = users.Where(u => u.Role == role);

    var total = await users.CountAsync(ct);
    var items = await users
        .OrderByDescending(u => u.CreatedAt)
        .Skip(page * size)
        .Take(size)
        .Select(u => UserResponse.From(u))  // project to DTO in query
        .ToListAsync(ct);

    return (items, total);
}
```

### Eager loading with Include

```csharp
// Load related entities to avoid N+1
var order = await _context.Orders
    .Include(o => o.User)
    .Include(o => o.Items)
    .FirstOrDefaultAsync(o => o.Id == id, ct);

// Filtered include — only load active items
var order = await _context.Orders
    .Include(o => o.Items.Where(i => i.IsActive))
    .FirstOrDefaultAsync(o => o.Id == id, ct);
```

### Projection to DTOs — most efficient for read-only queries

```csharp
var users = await _context.Users
    .AsNoTracking()
    .Select(u => new UserResponse(u.Id, u.Name, u.Email, u.CreatedAt, u.UpdatedAt))
    .ToListAsync(ct);
```

## Migration Patterns

```bash
# Add a migration
dotnet ef migrations add CreateUsersTable --project src/

# Apply pending migrations
dotnet ef database update --project src/

# Generate SQL script instead of applying (for production)
dotnet ef migrations script --idempotent --project src/ -o migrations.sql

# Remove last unapplied migration
dotnet ef migrations remove --project src/

# List migration status
dotnet ef migrations list --project src/
```

**Rules:**
- Never modify a migration that has been applied to production
- Always review generated migration code before applying
- Use `--idempotent` SQL scripts for production deployments
- Add indexes in the same migration as the table they reference
- Use `DateTimeOffset` for all timestamp columns (stores UTC offset)'

# shellcheck disable=SC2034
RULES_CONTENT_CROSS_SERVICE='# Cross-Service Patterns

> **When to use:** Ensuring consistency, understanding shared conventions.
>
> **Read first for:** DI registration, middleware order, configuration, testing strategy.

## Dependency Injection Registration

```csharp
// Program.cs — service registration order
var builder = WebApplication.CreateBuilder(args);

// 1. Configuration
builder.Services.Configure<JwtOptions>(builder.Configuration.GetSection("Jwt"));

// 2. Infrastructure
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("Default")));

// 3. Repositories & Services
builder.Services.AddScoped(typeof(IRepository<>), typeof(Repository<>));
builder.Services.AddScoped<IUserService, UserService>();
builder.Services.AddScoped<IOrderService, OrderService>();

// 4. Validation
builder.Services.AddValidatorsFromAssemblyContaining<Program>();

// 5. Auth
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(/* ... */);
builder.Services.AddAuthorization();

// 6. OpenAPI / Swagger
builder.Services.AddOpenApi();

// 7. Health checks
builder.Services.AddHealthChecks()
    .AddNpgSql(builder.Configuration.GetConnectionString("Default")!);
```

### Service Lifetimes

| Lifetime | When to use |
|----------|-------------|
| `AddTransient<T>()` | Lightweight, stateless services |
| `AddScoped<T>()` | Per-request services (DbContext, repositories, services) |
| `AddSingleton<T>()` | Thread-safe shared state (caches, configuration) |

**Rule:** DbContext must ALWAYS be scoped. Never register DbContext as singleton.

## Middleware Pipeline Order

```csharp
var app = builder.Build();

// 1. Exception handling (must be first)
app.UseExceptionHandler();
app.UseStatusCodePages();

// 2. HTTPS redirection
if (!app.Environment.IsDevelopment())
    app.UseHsts();
app.UseHttpsRedirection();

// 3. Static files (if any)
app.UseStaticFiles();

// 4. Routing
app.UseRouting();

// 5. CORS
app.UseCors("Default");

// 6. Authentication & Authorization
app.UseAuthentication();
app.UseAuthorization();

// 7. Custom middleware
app.UseMiddleware<RequestLoggingMiddleware>();

// 8. Endpoints
app.MapUserEndpoints();
app.MapOrderEndpoints();
app.MapHealthChecks("/health");

// 9. OpenAPI / Swagger
if (app.Environment.IsDevelopment())
    app.MapOpenApi();

app.Run();
```

**Critical:** Middleware order matters. Authentication must come before Authorization.
UseRouting must come before UseCors and UseAuthentication.

## IOptions<T> Configuration Pattern

```csharp
// Configuration/JwtOptions.cs
public class JwtOptions
{
    public const string SectionName = "Jwt";
    public required string Secret { get; init; }
    public required string Issuer { get; init; }
    public required string Audience { get; init; }
    public int ExpirationMinutes { get; init; } = 1440;
}

// Register:
builder.Services.Configure<JwtOptions>(builder.Configuration.GetSection(JwtOptions.SectionName));

// Inject via IOptions<T>:
public class JwtService(IOptions<JwtOptions> options)
{
    private readonly JwtOptions _jwt = options.Value;
}
```

```json
// appsettings.json
{
  "Jwt": {
    "Secret": "OVERRIDE_WITH_ENV_VARIABLE",
    "Issuer": "my-service",
    "Audience": "my-service",
    "ExpirationMinutes": 1440
  },
  "ConnectionStrings": {
    "Default": "Host=localhost;Database=mydb;Username=postgres;Password="
  }
}
```

## Environment Variables

| Variable | Source | Description |
|----------|--------|-------------|
| `ConnectionStrings__Default` | Secret | Database connection string |
| `Jwt__Secret` | Secret | JWT signing key |
| `ASPNETCORE_ENVIRONMENT` | Config | Environment (Development, Staging, Production) |
| `ASPNETCORE_URLS` | Config | Listen URLs (default: http://localhost:5000) |

**Secrets are NEVER committed to git.** Use `dotnet user-secrets` locally, environment
variables or Azure Key Vault in production.

```bash
# Local secrets management
dotnet user-secrets init --project src/
dotnet user-secrets set "Jwt:Secret" "my-super-secret-key-at-least-32-chars" --project src/
dotnet user-secrets set "ConnectionStrings:Default" "Host=localhost;Database=mydb;..." --project src/
```

## Logging with Serilog

```csharp
// Program.cs
builder.Host.UseSerilog((context, config) =>
    config.ReadFrom.Configuration(context.Configuration));

// In services — use ILogger<T>
public class UserService(ILogger<UserService> logger, AppDbContext context)
{
    public async Task<UserResponse> CreateAsync(UserCreateRequest request)
    {
        logger.LogInformation("Creating user with email {Email}", request.Email);
        // ... business logic
        logger.LogDebug("User created with ID {UserId}", user.Id);
        return UserResponse.From(user);
    }
}
```

```json
// appsettings.json — Serilog config
{
  "Serilog": {
    "Using": ["Serilog.Sinks.Console"],
    "MinimumLevel": {
      "Default": "Information",
      "Override": {
        "Microsoft.AspNetCore": "Warning",
        "Microsoft.EntityFrameworkCore": "Warning"
      }
    },
    "WriteTo": [{ "Name": "Console" }]
  }
}
```

**Never log:** passwords, tokens, PII, full request bodies with sensitive data.
Use structured logging with named parameters `{Name}` not string interpolation.

## Date/Time Format

All timestamps use **ISO 8601 UTC** via `DateTimeOffset`:

```csharp
DateTimeOffset now = DateTimeOffset.UtcNow;  // 2026-01-01T12:00:00+00:00
```

Configure System.Text.Json serialization:
```csharp
builder.Services.ConfigureHttpJsonOptions(options =>
{
    options.SerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.CamelCase;
    options.SerializerOptions.DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull;
});
```

## Global Usings

```csharp
// GlobalUsings.cs — reduce boilerplate across the project
global using Microsoft.EntityFrameworkCore;
global using Microsoft.AspNetCore.Http.HttpResults;
global using System.ComponentModel.DataAnnotations;
global using FluentValidation;
```

## Testing Conventions

### Unit Tests (xUnit + NSubstitute)

```csharp
public class UserServiceTests
{
    private readonly AppDbContext _context;
    private readonly UserService _service;

    public UserServiceTests()
    {
        var options = new DbContextOptionsBuilder<AppDbContext>()
            .UseInMemoryDatabase(Guid.NewGuid().ToString())
            .Options;
        _context = new AppDbContext(options);
        _service = new UserService(
            NullLogger<UserService>.Instance,
            _context
        );
    }

    [Fact]
    public async Task CreateAsync_ShouldReturnUser()
    {
        var request = new UserCreateRequest("Alice", "alice@test.com", "password123");

        var result = await _service.CreateAsync(request);

        Assert.Equal("Alice", result.Name);
        Assert.Equal("alice@test.com", result.Email);
        Assert.Single(await _context.Users.ToListAsync());
    }

    [Fact]
    public async Task GetByIdAsync_ShouldReturnNull_WhenNotFound()
    {
        var result = await _service.GetByIdAsync(999);

        Assert.Null(result);
    }
}
```

### Integration Tests (WebApplicationFactory)

```csharp
public class UserEndpointTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public UserEndpointTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.WithWebHostBuilder(builder =>
        {
            builder.ConfigureServices(services =>
            {
                // Replace real DB with in-memory for tests
                services.RemoveAll(typeof(DbContextOptions<AppDbContext>));
                services.AddDbContext<AppDbContext>(options =>
                    options.UseInMemoryDatabase("TestDb"));
            });
        }).CreateClient();
    }

    [Fact]
    public async Task PostUser_ReturnsCreated()
    {
        var request = new UserCreateRequest("Bob", "bob@test.com", "password123");
        var response = await _client.PostAsJsonAsync("/api/v1/users", request);

        Assert.Equal(HttpStatusCode.Created, response.StatusCode);

        var user = await response.Content.ReadFromJsonAsync<UserResponse>();
        Assert.Equal("Bob", user!.Name);
    }

    [Fact]
    public async Task GetUser_ReturnsNotFound_WhenMissing()
    {
        var response = await _client.GetAsync("/api/v1/users/99999");

        Assert.Equal(HttpStatusCode.NotFound, response.StatusCode);
    }
}
```

## Security Best Practices

### Input Validation
- Validate ALL user input at API boundaries using FluentValidation or DataAnnotations
- Use `[Required]`, `[StringLength]`, `[EmailAddress]`, `[Range]` on DTO record properties
- Reject unexpected fields — `System.Text.Json` ignores unknown properties by default
- Use `AbstractValidator<T>` for complex cross-field validation rules

```csharp
public class UserCreateRequestValidator : AbstractValidator<UserCreateRequest>
{
    public UserCreateRequestValidator()
    {
        RuleFor(x => x.Name).NotEmpty().MaximumLength(255);
        RuleFor(x => x.Email).NotEmpty().EmailAddress();
        RuleFor(x => x.Password).NotEmpty().MinimumLength(8);
    }
}
```

### SQL Injection Prevention
- NEVER concatenate user input into queries
- Use EF Core LINQ queries, parameterized `FromSqlInterpolated`, or Dapper with parameters

```csharp
// SAFE — EF Core LINQ (parameterized automatically)
var user = await context.Users.FirstOrDefaultAsync(u => u.Email == email);

// SAFE — raw SQL with interpolation (EF Core parameterizes it)
var users = await context.Users
    .FromSqlInterpolated($"SELECT * FROM users WHERE email = {email}")
    .ToListAsync();

// UNSAFE — string concatenation (NEVER do this)
// context.Users.FromSqlRaw("SELECT * FROM users WHERE email = '\''" + email + "'\''");
```

### Rate Limiting
- Use built-in `Microsoft.AspNetCore.RateLimiting` middleware (.NET 7+)
- Apply stricter limits to auth endpoints (5 requests/min) and general API (100 requests/min)

```csharp
builder.Services.AddRateLimiter(options =>
{
    options.AddFixedWindowLimiter("auth", opt =>
    {
        opt.PermitLimit = 5;
        opt.Window = TimeSpan.FromMinutes(1);
    });
    options.AddFixedWindowLimiter("api", opt =>
    {
        opt.PermitLimit = 100;
        opt.Window = TimeSpan.FromMinutes(1);
    });
});
app.UseRateLimiter();
```

### CORS Configuration
- Configure CORS via `AddCors` with named policies — never use `AllowAnyOrigin()` with credentials
- Whitelist specific origins

```csharp
builder.Services.AddCors(options =>
{
    options.AddPolicy("Default", policy =>
    {
        policy.WithOrigins("https://app.example.com")
              .AllowAnyMethod()
              .AllowAnyHeader()
              .AllowCredentials();
    });
});
```

### Secrets Management
- Never commit secrets to git — use `dotnet user-secrets` locally, Azure Key Vault or env vars in production
- Use `IOptions<T>` pattern to bind configuration sections
- Rotate secrets immediately on suspected compromise

```bash
dotnet user-secrets set "Jwt:Secret" "your-secret-key" --project src/
```

### Dependency Scanning
- Run `dotnet list package --vulnerable` in CI on every PR
- Enable Dependabot or Renovate for automated NuGet dependency updates
- Use `dotnet-retire` or Snyk for deeper vulnerability scanning

### HTTPS / TLS
- Enforce HTTPS in production with `app.UseHsts()` and `app.UseHttpsRedirection()`
- Use HSTS header: `Strict-Transport-Security: max-age=63072000; includeSubDomains`
- Configure `ForwardedHeaders` when behind a reverse proxy

## Performance Checklist

### Database Performance
- Prevent N+1 queries: use `.Include()` and `.ThenInclude()` for eager loading
- Add database indexes via Fluent API (`builder.HasIndex()`) or migrations
- Use connection pooling (Npgsql pools connections by default) — tune `MaxPoolSize` in connection string
- Profile slow queries: enable EF Core query logging with `LogLevel.Information` on `Microsoft.EntityFrameworkCore.Database.Command`

### Caching Strategy
- Use `IMemoryCache` for in-process caching or `IDistributedCache` with Redis
- Cache expensive computations and external API responses with `MemoryCacheEntryOptions`

```csharp
var user = await cache.GetOrCreateAsync($"user:{id}", async entry =>
{
    entry.SetAbsoluteExpiration(TimeSpan.FromMinutes(5));
    return await context.Users.FindAsync(id);
});
```

### API Response Optimization
- Always paginate list endpoints using `Skip()`/`Take()` with total count
- Compress responses: enable `app.UseResponseCompression()` with gzip/brotli
- Set appropriate `Cache-Control` headers for cacheable responses
- Use `AsNoTracking()` for read-only queries and DTO projections with `Select()`'

LINT_LANGUAGES="C# (dotnet format, Roslyn analyzers), JSON, YAML, Shell (shellcheck)"
