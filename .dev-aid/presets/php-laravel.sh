#!/usr/bin/env bash
# Preset: PHP 8.3+ / Laravel 11+ / Eloquent ORM / Blade templates

preset_name="php-laravel"
preset_description="PHP 8.3+ / Laravel 11+ with Eloquent ORM, Blade templates, Pest testing"

# Rules files: newline-delimited "filename|description" pairs
RULES_FILES="api-contracts.md|Resource controllers, API resources, Form Requests, route model binding
database.md|Eloquent models, relationships, migrations, query scopes, eager loading
cross-service.md|Service providers, facades, config, queues, events, middleware, testing"

# Technology stack entries
TECH_STACK="| Language | PHP 8.3+ |
| Framework | Laravel 11+ |
| ORM | Eloquent |
| Templates | Blade |
| Testing | Pest / PHPUnit |
| Code Style | Laravel Pint (PSR-12) |
| Database | *MySQL 8+ / PostgreSQL 16+ / SQLite* |
| Package Manager | Composer 2 |
| Frontend | *Livewire / Inertia.js + Vue / Blade only* |"

# Context loading table entries
CONTEXT_LOADING_TABLE="| **New API endpoint** | \`.claude/rules/api-contracts.md\`, \`app/Http/Controllers/\` |
| **Database changes** | \`.claude/rules/database.md\`, \`app/Models/\`, \`database/migrations/\` |
| **Validation** | \`.claude/rules/api-contracts.md\` (Form Requests section), \`app/Http/Requests/\` |
| **Queue jobs** | \`.claude/rules/cross-service.md\` (Queues section), \`app/Jobs/\` |
| **Debugging** | \`.claude/rules/troubleshooting.md\` |
| **Events/Listeners** | \`.claude/rules/cross-service.md\` (Events section), \`app/Events/\`, \`app/Listeners/\` |
| **Middleware** | \`.claude/rules/cross-service.md\` (Middleware section), \`app/Http/Middleware/\` |"

# Context groups
CONTEXT_GROUPS='### `api`
Read: `.claude/rules/api-contracts.md`, `app/Http/Controllers/`, `app/Http/Requests/`, `routes/api.php`

### `database`
Read: `.claude/rules/database.md`, `app/Models/`, `database/migrations/`

### `config`
Read: `.claude/rules/cross-service.md`, `config/`, `.env.example`

### `debug`
Read: `.claude/rules/troubleshooting.md`'

# Development workflow
WORKFLOW='```bash
# Setup
composer install
cp .env.example .env
php artisan key:generate
php artisan migrate

# Run dev server
php artisan serve  # http://localhost:8000

# Run tests
php artisan test
# or with Pest directly:
./vendor/bin/pest --parallel

# Code style (Laravel Pint)
./vendor/bin/pint

# Static analysis (if using Larastan)
./vendor/bin/phpstan analyse

# Database
php artisan migrate                    # run pending migrations
php artisan migrate:rollback           # rollback last batch
php artisan migrate:fresh --seed       # drop all, re-migrate, seed
php artisan db:seed                    # run seeders

# Artisan generators
php artisan make:model User -mfcr     # model + migration + factory + controller (resource)
php artisan make:request StoreUserRequest
php artisan make:resource UserResource
php artisan make:job ProcessPayment
php artisan make:event OrderShipped
php artisan make:listener SendShipmentNotification --event=OrderShipped

# Cache management
php artisan config:cache               # cache config for production
php artisan route:cache                # cache routes for production
php artisan view:cache                 # cache Blade views
php artisan optimize                   # all caches at once
php artisan optimize:clear             # clear all caches
```

### Useful Artisan Commands

- `php artisan tinker` — interactive REPL with app context
- `php artisan route:list --path=api` — show registered API routes
- `php artisan model:show User` — show model schema and relationships
- `php artisan queue:work --tries=3` — start queue worker'

# Project overview
PROJECT_OVERVIEW="Laravel application with API endpoints under \`/api/\` and web routes under \`/\`. Models follow Eloquent conventions with relationships, scopes, and form request validation."

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
│   │   ├── eloquent-patterns.md
│   │   ├── api-gotchas.md
│   │   └── debugging.md
│   └── commands/
│       ├── review.md
│       ├── test.md
│       ├── plan.md
│       ├── smoke.md
│       └── lint.md
├── app/
│   ├── Console/
│   ├── Events/
│   ├── Exceptions/
│   ├── Http/
│   │   ├── Controllers/
│   │   ├── Middleware/
│   │   ├── Requests/
│   │   └── Resources/
│   ├── Jobs/
│   ├── Listeners/
│   ├── Models/
│   ├── Policies/
│   ├── Providers/
│   └── Services/
├── bootstrap/
├── config/
├── database/
│   ├── factories/
│   ├── migrations/
│   └── seeders/
├── resources/
│   ├── views/
│   ├── css/
│   └── js/
├── routes/
│   ├── api.php
│   ├── web.php
│   └── console.php
├── tests/
│   ├── Feature/
│   ├── Unit/
│   └── Pest.php
├── docs/
│   ├── plans/
│   │   └── .plan-template.md
│   └── decisions/
│       ├── index.md
│       └── adr-template.md
├── scripts/
│   └── smoke-laravel.sh
├── composer.json
├── phpunit.xml
└── .env.example'

# Smoke test scripts: "filename|title|checks_variable_name"
SMOKE_SCRIPTS="smoke-laravel.sh|Laravel Health Checks|SMOKE_LARAVEL_CHECKS"

# Smoke test check bodies (referenced by variable name above)
# shellcheck disable=SC2034
SMOKE_LARAVEL_CHECKS='section "Application"

if [[ -f "artisan" ]]; then
  pass "Laravel artisan found"
else
  fail "artisan not found — not a Laravel project root"
fi

if [[ -f "composer.json" ]]; then
  pass "composer.json exists"
else
  fail "composer.json not found"
fi

if [[ -d "vendor" ]]; then
  pass "vendor/ directory exists"
else
  fail "vendor/ missing — run: composer install"
fi

section "Configuration"

if [[ -f ".env" ]]; then
  pass ".env file exists"
else
  warn ".env missing — run: cp .env.example .env && php artisan key:generate"
fi

if php artisan config:cache --no-interaction 2>/dev/null; then
  pass "Config caches successfully"
  php artisan config:clear --no-interaction 2>/dev/null
else
  warn "Config cache failed — check .env and config/ files"
fi

section "Composer"

if composer validate --no-check-all --no-check-publish 2>/dev/null; then
  pass "composer.json is valid"
else
  warn "composer.json has validation issues"
fi

section "Database"

if php artisan migrate:status --no-interaction 2>/dev/null | grep -q "Ran"; then
  pass "Database migrations have been applied"
else
  warn "Database not migrated or not reachable — run: php artisan migrate"
fi

section "Code Style"

if [[ -f "vendor/bin/pint" ]]; then
  if ./vendor/bin/pint --test 2>/dev/null; then
    pass "Laravel Pint passes"
  else
    warn "Pint has style findings — run: ./vendor/bin/pint"
  fi
else
  warn "Laravel Pint not installed (composer require laravel/pint --dev)"
fi

section "Tests"

if php artisan test --no-interaction 2>/dev/null; then
  pass "Tests pass"
else
  warn "Tests failing — run: php artisan test"
fi'

# Troubleshooting sections
TROUBLESHOOTING_SECTIONS='## 1. Configuration / Environment

### Symptom: `No application encryption key has been specified`

**Diagnosis:** The `APP_KEY` in `.env` is empty or missing. Laravel requires this
key for encryption, session management, and signed URLs.

**Fix:**
```bash
php artisan key:generate
# Verify .env has APP_KEY=base64:...
```

---

### Symptom: `SQLSTATE[HY000] [2002] Connection refused` or `No such file or directory`

**Diagnosis:** Database connection failed. Either the database server is not running,
the credentials in `.env` are wrong, or the socket path is incorrect.

**Fix:**
```bash
# Check DB_CONNECTION, DB_HOST, DB_PORT, DB_DATABASE, DB_USERNAME, DB_PASSWORD in .env

# For MySQL via Docker:
docker compose up -d mysql
php artisan migrate:status

# For SQLite:
touch database/database.sqlite
# Set in .env: DB_CONNECTION=sqlite, DB_DATABASE=database/database.sqlite
```

---

## 2. Eloquent / Database

### Symptom: N+1 query detected — hundreds of queries on a single page

**Diagnosis:** Lazy loading relationships inside a loop. Each iteration fires
a separate query instead of eager-loading them upfront.

**Fix:**
```php
// BAD — N+1: one query per post for comments
$posts = Post::all();
foreach ($posts as $post) {
    echo $post->comments->count(); // lazy load each time
}

// GOOD — eager load with with()
$posts = Post::with("comments")->get();

// PREVENTION — add to AppServiceProvider::boot()
Model::preventLazyLoading(!app()->isProduction());
```

---

### Symptom: `MassAssignmentException` when creating or updating models

**Diagnosis:** Attempting to fill attributes that are not in the model `$fillable`
array (or are in `$guarded`).

**Fix:**
```php
// In the model — explicitly list fillable fields
class User extends Model
{
    protected $fillable = ["name", "email", "role"];

    // Or guard only specific fields:
    // protected $guarded = ["id", "is_admin"];
}

// Never use: protected $guarded = []; in production
```

---

## 3. Routing / Controllers

### Symptom: `404 Not Found` for routes that exist in `routes/api.php`

**Diagnosis:** API routes require the `/api` prefix by default. The route cache
may also be stale.

**Fix:**
```bash
# Clear route cache
php artisan route:clear

# Verify the route is registered
php artisan route:list --path=api/users

# API routes automatically get /api prefix:
# Route::apiResource("users", UserController::class);
# This creates: /api/users, /api/users/{user}, etc.
```

---

### Symptom: `419 Page Expired` on form submission

**Diagnosis:** CSRF token mismatch. Blade forms must include `@csrf`, and AJAX
requests need the `X-CSRF-TOKEN` header. API routes (routes/api.php) are exempt
from CSRF by default.

**Fix:**
```blade
{{-- In Blade forms --}}
<form method="POST" action="/users">
    @csrf
    ...
</form>

{{-- For AJAX --}}
<meta name="csrf-token" content="{{ csrf_token() }}">
<script>
axios.defaults.headers.common["X-CSRF-TOKEN"] =
    document.querySelector("meta[name=csrf-token]").content;
</script>
```

---

## 4. Testing

### Symptom: Tests pass individually but fail when run together

**Diagnosis:** Test isolation issue. One test is modifying shared state (database,
config, static properties) that another test depends on.

**Fix:**
```php
// Use RefreshDatabase trait to reset DB between tests
use Illuminate\Foundation\Testing\RefreshDatabase;

class UserTest extends TestCase
{
    use RefreshDatabase;

    public function test_create_user(): void
    {
        $response = $this->postJson("/api/users", [
            "name" => "Test User",
            "email" => "test@example.com",
        ]);
        $response->assertStatus(201);
    }
}

// Or use DatabaseTransactions for speed (rolls back instead of re-migrating)
use Illuminate\Foundation\Testing\DatabaseTransactions;
```

---

*Add entries as you encounter and solve issues. Use the Symptom -> Diagnosis -> Fix format.*'

# Memory topics: "filename|description" pairs
MEMORY_TOPICS="eloquent-patterns.md|Eloquent relationship patterns, query scopes, accessors/mutators
api-gotchas.md|API resource gotchas, validation edge cases, route model binding issues
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

> **When to use:** Adding or modifying API endpoints, form validation, API resources.
>
> **Read first for:** New endpoints, request validation, response formatting, route model binding.

## Base URL

- **Production:** `https://api.example.com/api`
- **Local dev:** `http://localhost:8000/api`

## Resource Controllers

```php
// routes/api.php
use App\Http\Controllers\UserController;
use App\Http\Controllers\PostController;

Route::apiResource("users", UserController::class);
Route::apiResource("users.posts", PostController::class)->scoped();

// Generated routes:
// GET    /api/users              → index
// POST   /api/users              → store
// GET    /api/users/{user}       → show
// PUT    /api/users/{user}       → update
// DELETE /api/users/{user}       → destroy
```

### Controller Pattern

```php
namespace App\Http\Controllers;

use App\Http\Requests\StoreUserRequest;
use App\Http\Requests\UpdateUserRequest;
use App\Http\Resources\UserResource;
use App\Http\Resources\UserCollection;
use App\Models\User;

class UserController extends Controller
{
    public function index(): UserCollection
    {
        $users = User::with("posts")
            ->latest()
            ->paginate(15);

        return new UserCollection($users);
    }

    public function store(StoreUserRequest $request): UserResource
    {
        $user = User::create($request->validated());

        return (new UserResource($user))
            ->response()
            ->setStatusCode(201);
    }

    public function show(User $user): UserResource
    {
        return new UserResource($user->load("posts", "profile"));
    }

    public function update(UpdateUserRequest $request, User $user): UserResource
    {
        $user->update($request->validated());

        return new UserResource($user);
    }

    public function destroy(User $user): \Illuminate\Http\JsonResponse
    {
        $user->delete();

        return response()->json(null, 204);
    }
}
```

## API Resources

```php
namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class UserResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            "id" => $this->id,
            "name" => $this->name,
            "email" => $this->email,
            "avatar_url" => $this->avatar_url,
            "posts_count" => $this->whenCounted("posts"),
            "posts" => PostResource::collection($this->whenLoaded("posts")),
            "profile" => new ProfileResource($this->whenLoaded("profile")),
            "created_at" => $this->created_at->toIso8601String(),
            "updated_at" => $this->updated_at->toIso8601String(),
        ];
    }
}
```

### Collections with Pagination Metadata

```php
namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\ResourceCollection;

class UserCollection extends ResourceCollection
{
    public function toArray(Request $request): array
    {
        return [
            "data" => $this->collection,
            "meta" => [
                "current_page" => $this->currentPage(),
                "last_page" => $this->lastPage(),
                "per_page" => $this->perPage(),
                "total" => $this->total(),
            ],
        ];
    }
}
```

## Form Request Validation

```php
namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;

class StoreUserRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true; // or: $this->user()->can("create", User::class)
    }

    public function rules(): array
    {
        return [
            "name" => ["required", "string", "min:2", "max:255"],
            "email" => ["required", "email", Rule::unique("users", "email")],
            "role" => ["sometimes", "string", Rule::in(["admin", "editor", "viewer"])],
            "password" => ["required", "string", "min:8", "confirmed"],
        ];
    }

    public function messages(): array
    {
        return [
            "email.unique" => "This email address is already registered.",
        ];
    }
}

class UpdateUserRequest extends FormRequest
{
    public function rules(): array
    {
        return [
            "name" => ["sometimes", "string", "min:2", "max:255"],
            "email" => [
                "sometimes", "email",
                Rule::unique("users")->ignore($this->route("user")),
            ],
            "role" => ["sometimes", "string", Rule::in(["admin", "editor", "viewer"])],
        ];
    }
}
```

## Route Model Binding

```php
// Implicit binding — Laravel resolves {user} to User model automatically
Route::get("/api/users/{user}", [UserController::class, "show"]);

// Scoped binding — nested resources must belong to parent
Route::get("/api/users/{user}/posts/{post}", function (User $user, Post $post) {
    // $post is guaranteed to belong to $user
    return new PostResource($post);
})->scopeBindings();

// Custom key — resolve by slug instead of ID
// In User model:
public function getRouteKeyName(): string
{
    return "slug"; // resolves /api/users/{user} by slug column
}
```

## API Versioning

```php
// routes/api.php — version in URL prefix
Route::prefix("v1")->group(function () {
    Route::apiResource("users", V1\UserController::class);
});

Route::prefix("v2")->group(function () {
    Route::apiResource("users", V2\UserController::class);
});
```

## Rate Limiting

```php
// bootstrap/app.php (Laravel 11+)
use Illuminate\Cache\RateLimiting\Limit;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\RateLimiter;

->withMiddleware(function (Middleware $middleware) {
    RateLimiter::for("api", function (Request $request) {
        return Limit::perMinute(60)->by($request->user()?->id ?: $request->ip());
    });
})

// Per-route throttle
Route::middleware("throttle:api")->group(function () {
    Route::apiResource("users", UserController::class);
});

// Custom limiter for expensive endpoints
RateLimiter::for("exports", function (Request $request) {
    return Limit::perHour(5)->by($request->user()->id);
});
Route::post("/api/exports", ExportController::class)->middleware("throttle:exports");
```

## Error Response Format

```json
{
    "message": "The given data was invalid.",
    "errors": {
        "email": ["The email has already been taken."],
        "name": ["The name field is required."]
    }
}
```

| Status | When |
|--------|------|
| 200 | Success (show, update, index) |
| 201 | Resource created (store) |
| 204 | Resource deleted (destroy) |
| 401 | Unauthenticated |
| 403 | Unauthorized (policy check failed) |
| 404 | Model not found (route model binding) |
| 422 | Validation error (Form Request) |
| 429 | Rate limited |

## Health Endpoints

```php
// routes/api.php
Route::get("/health", function () {
    return response()->json(["status" => "ok"]);
});

Route::get("/ready", function () {
    try {
        DB::connection()->getPdo();
        Cache::store()->get("health-check");
        return response()->json(["status" => "ready", "db" => true, "cache" => true]);
    } catch (\Exception $e) {
        return response()->json(["status" => "degraded", "error" => $e->getMessage()], 503);
    }
});
```'

# shellcheck disable=SC2034
RULES_CONTENT_DATABASE='# Database Patterns

> **When to use:** Schema changes, new models, relationships, query optimization.
>
> **Read first for:** Any database-related task, migrations, Eloquent relationships.

## Eloquent Models

```php
namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\SoftDeletes;

class Post extends Model
{
    use HasFactory, SoftDeletes;

    protected $fillable = [
        "title",
        "slug",
        "body",
        "status",
        "published_at",
        "user_id",
        "category_id",
    ];

    protected function casts(): array
    {
        return [
            "published_at" => "datetime",
            "status" => PostStatus::class,      // enum cast
            "metadata" => "array",              // JSON column
        ];
    }

    // --- Relationships ---

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function category(): BelongsTo
    {
        return $this->belongsTo(Category::class);
    }

    public function comments(): HasMany
    {
        return $this->hasMany(Comment::class);
    }

    public function tags(): \Illuminate\Database\Eloquent\Relations\BelongsToMany
    {
        return $this->belongsToMany(Tag::class)->withTimestamps();
    }

    // --- Scopes ---

    public function scopePublished($query)
    {
        return $query->where("status", PostStatus::Published)
                     ->where("published_at", "<=", now());
    }

    public function scopeByAuthor($query, int $userId)
    {
        return $query->where("user_id", $userId);
    }

    // --- Accessors / Mutators (Laravel 11+ attribute style) ---

    protected function title(): \Illuminate\Database\Eloquent\Casts\Attribute
    {
        return Attribute::make(
            get: fn (string $value) => ucfirst($value),
            set: fn (string $value) => strtolower($value),
        );
    }
}
```

## Relationships Reference

```php
// One-to-Many
class User extends Model {
    public function posts(): HasMany { return $this->hasMany(Post::class); }
}
class Post extends Model {
    public function user(): BelongsTo { return $this->belongsTo(User::class); }
}

// Many-to-Many (pivot table: post_tag)
class Post extends Model {
    public function tags(): BelongsToMany {
        return $this->belongsToMany(Tag::class)->withTimestamps();
    }
}

// Has-One-Through
class Country extends Model {
    public function ownerPhone(): HasOneThrough {
        return $this->hasOneThrough(Phone::class, User::class);
    }
}

// Polymorphic
class Comment extends Model {
    public function commentable(): MorphTo { return $this->morphTo(); }
}
class Post extends Model {
    public function comments(): MorphMany { return $this->morphMany(Comment::class, "commentable"); }
}
class Video extends Model {
    public function comments(): MorphMany { return $this->morphMany(Comment::class, "commentable"); }
}
```

## Migrations

```php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create("posts", function (Blueprint $table) {
            $table->id();
            $table->foreignId("user_id")->constrained()->cascadeOnDelete();
            $table->foreignId("category_id")->nullable()->constrained()->nullOnDelete();
            $table->string("title");
            $table->string("slug")->unique();
            $table->text("body");
            $table->string("status")->default("draft");
            $table->timestamp("published_at")->nullable();
            $table->json("metadata")->nullable();
            $table->timestamps();
            $table->softDeletes();

            $table->index(["status", "published_at"]);
            $table->fullText("body");
        });
    }

    public function down(): void
    {
        Schema::dropIfExists("posts");
    }
};
```

**Migration rules:**
- Never modify a migration that has been run in production — create a new one
- Always include a `down()` method for rollback
- Add indexes in the same migration as the table
- Use `foreignId()->constrained()` for foreign keys

### Common Migration Commands

```bash
php artisan make:migration create_posts_table
php artisan make:migration add_slug_to_posts_table --table=posts
php artisan migrate
php artisan migrate:rollback --step=1
php artisan migrate:status
```

## Eager Loading (N+1 Prevention)

```php
// ALWAYS eager load relationships you will access
$posts = Post::with(["user", "comments.user", "tags"])->paginate(15);

// Conditional eager loading
$posts = Post::with(["comments" => function ($query) {
    $query->where("approved", true)->latest()->limit(5);
}])->get();

// Lazy eager loading (when you already have the collection)
$posts = Post::all();
$posts->load("user", "tags");

// Count without loading
$users = User::withCount("posts")->get();
// $user->posts_count

// PREVENTION — detect N+1 in development
// In AppServiceProvider::boot()
Model::preventLazyLoading(!app()->isProduction());
```

## Query Scopes and Builders

```php
// Reusable scope chains
$posts = Post::published()
    ->byAuthor($userId)
    ->with("comments")
    ->latest("published_at")
    ->paginate(15);

// Complex queries with the query builder
$stats = DB::table("posts")
    ->select(
        DB::raw("DATE(created_at) as date"),
        DB::raw("COUNT(*) as total"),
        DB::raw("SUM(CASE WHEN status = ? THEN 1 ELSE 0 END) as published", ["published"])
    )
    ->where("created_at", ">=", now()->subDays(30))
    ->groupBy("date")
    ->orderBy("date")
    ->get();
```

## Schema Conventions

- Table names: lowercase plural snake_case (`users`, `blog_posts`, `order_items`)
- Primary keys: `id` (unsigned big integer, auto-increment)
- Timestamps: `created_at`, `updated_at` (via `$table->timestamps()`)
- Foreign keys: `<singular_table>_id` (e.g., `user_id`, `category_id`)
- Pivot tables: alphabetical singular (`post_tag`, `role_user`)
- Indexes: Laravel auto-names them, or use `idx_<table>_<columns>` manually
- Soft deletes: `deleted_at` (via `$table->softDeletes()`)'

# shellcheck disable=SC2034
RULES_CONTENT_CROSS_SERVICE='# Cross-Service Patterns

> **When to use:** Application wiring, shared conventions, testing, jobs, events.
>
> **Read first for:** Service providers, middleware, queue jobs, testing setup.

## Service Providers

```php
// app/Providers/AppServiceProvider.php
namespace App\Providers;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    public function register(): void
    {
        // Bind interfaces to implementations
        $this->app->bind(PaymentGateway::class, StripeGateway::class);

        // Singleton binding
        $this->app->singleton(SearchService::class, function ($app) {
            return new SearchService(config("services.search.key"));
        });
    }

    public function boot(): void
    {
        // Strict mode in development
        Model::preventLazyLoading(!app()->isProduction());
        Model::preventSilentlyDiscardingAttributes(!app()->isProduction());
        Model::preventAccessingMissingAttributes(!app()->isProduction());
    }
}
```

## Configuration Management

```php
// Access config values
$appName = config("app.name");
$dbHost = config("database.connections.mysql.host");

// With default fallback
$timeout = config("services.api.timeout", 30);

// NEVER use env() outside config files — it returns null when config is cached
// BAD:  $key = env("API_KEY");
// GOOD: $key = config("services.api.key");

// In config/services.php:
return [
    "api" => [
        "key" => env("API_KEY"),
        "timeout" => env("API_TIMEOUT", 30),
    ],
];
```

## Queue Jobs

```php
namespace App\Jobs;

use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Queue\Middleware\WithoutOverlapping;

class ProcessPayment implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public int $tries = 3;
    public int $backoff = 60;   // seconds between retries
    public int $timeout = 120;  // max execution time

    public function __construct(
        public readonly Order $order,
    ) {}

    public function handle(PaymentGateway $gateway): void
    {
        $gateway->charge($this->order->total, $this->order->payment_method);
        $this->order->update(["status" => "paid"]);
    }

    public function failed(\Throwable $exception): void
    {
        // Runs after all retries exhausted
        $this->order->update(["status" => "payment_failed"]);
        logger()->error("Payment failed", [
            "order_id" => $this->order->id,
            "error" => $exception->getMessage(),
        ]);
    }

    public function middleware(): array
    {
        // Prevent duplicate processing of same order
        return [new WithoutOverlapping($this->order->id)];
    }
}

// Dispatching
ProcessPayment::dispatch($order);
ProcessPayment::dispatch($order)->onQueue("payments");
ProcessPayment::dispatch($order)->delay(now()->addMinutes(5));
```

```bash
# Start queue worker
php artisan queue:work --queue=payments,default --tries=3 --backoff=60

# Process a single job (useful for debugging)
php artisan queue:work --once

# Restart workers after code deploy
php artisan queue:restart
```

## Events and Listeners

```php
// app/Events/OrderShipped.php
class OrderShipped
{
    use Dispatchable, InteractsWithSockets, SerializesModels;

    public function __construct(public readonly Order $order) {}
}

// app/Listeners/SendShipmentNotification.php
class SendShipmentNotification implements ShouldQueue
{
    public function handle(OrderShipped $event): void
    {
        $event->order->user->notify(new ShipmentNotification($event->order));
    }
}

// Dispatching
OrderShipped::dispatch($order);

// Registration in EventServiceProvider (or auto-discovery):
protected $listen = [
    OrderShipped::class => [
        SendShipmentNotification::class,
        UpdateInventory::class,
    ],
];
```

## Middleware

```php
// app/Http/Middleware/EnsureJsonResponse.php
namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class EnsureJsonResponse
{
    public function handle(Request $request, Closure $next): Response
    {
        $request->headers->set("Accept", "application/json");
        return $next($request);
    }
}

// Register in bootstrap/app.php (Laravel 11+):
->withMiddleware(function (Middleware $middleware) {
    $middleware->api(prepend: [
        EnsureJsonResponse::class,
    ]);
})
```

## Environment Variables

| Variable | Source | Description |
|----------|--------|-------------|
| `APP_KEY` | `.env` / Secret | Application encryption key |
| `APP_ENV` | `.env` | Environment (local, staging, production) |
| `APP_DEBUG` | `.env` | Debug mode (true/false) |
| `DB_CONNECTION` | `.env` | Database driver (mysql, pgsql, sqlite) |
| `DB_HOST` | `.env` | Database host |
| `DB_DATABASE` | `.env` | Database name |
| `DB_USERNAME` | `.env` / Secret | Database user |
| `DB_PASSWORD` | `.env` / Secret | Database password |
| `QUEUE_CONNECTION` | `.env` | Queue driver (sync, database, redis, sqs) |
| `CACHE_STORE` | `.env` | Cache driver (file, redis, memcached) |
| `MAIL_MAILER` | `.env` | Mail driver (smtp, ses, mailgun) |

**Secrets are NEVER committed to git.** Use `.env` locally, secrets manager in production.

## Testing with Pest

```php
// tests/Feature/UserTest.php
use App\Models\User;
use function Pest\Laravel\{getJson, postJson, deleteJson};

it("lists users with pagination", function () {
    User::factory()->count(20)->create();

    getJson("/api/users")
        ->assertOk()
        ->assertJsonCount(15, "data")
        ->assertJsonPath("meta.total", 20);
});

it("creates a user with valid data", function () {
    $payload = [
        "name" => "Jane Doe",
        "email" => "jane@example.com",
        "password" => "securepassword",
        "password_confirmation" => "securepassword",
    ];

    postJson("/api/users", $payload)
        ->assertCreated()
        ->assertJsonPath("data.name", "Jane Doe");

    $this->assertDatabaseHas("users", ["email" => "jane@example.com"]);
});

it("validates required fields on create", function () {
    postJson("/api/users", [])
        ->assertUnprocessable()
        ->assertJsonValidationErrors(["name", "email", "password"]);
});

it("deletes a user", function () {
    $user = User::factory()->create();

    deleteJson("/api/users/{$user->id}")
        ->assertNoContent();

    $this->assertSoftDeleted("users", ["id" => $user->id]);
});

it("prevents unauthorized access", function () {
    getJson("/api/admin/dashboard")
        ->assertUnauthorized();
});
```

### Testing with PHPUnit

```php
namespace Tests\Feature;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class UserTest extends TestCase
{
    use RefreshDatabase;

    public function test_user_can_be_created(): void
    {
        $response = $this->postJson("/api/users", [
            "name" => "Test User",
            "email" => "test@example.com",
            "password" => "securepassword",
            "password_confirmation" => "securepassword",
        ]);

        $response->assertStatus(201);
        $this->assertDatabaseHas("users", ["email" => "test@example.com"]);
    }
}
```

## Artisan Commands Reference

```bash
# Code generation
php artisan make:model Post -mfcr   # model + migration + factory + resource controller
php artisan make:request StorePostRequest
php artisan make:resource PostResource
php artisan make:job ProcessExport
php artisan make:event OrderCreated
php artisan make:listener NotifyUser --event=OrderCreated
php artisan make:policy PostPolicy --model=Post
php artisan make:middleware EnsureApiJson
php artisan make:test UserTest        # Feature test
php artisan make:test UserTest --unit # Unit test
php artisan make:test UserTest --pest # Pest test

# Inspection
php artisan route:list --path=api
php artisan model:show Post
php artisan about

# Maintenance
php artisan optimize           # cache config + routes + views
php artisan optimize:clear     # clear all caches
php artisan queue:work
php artisan schedule:run
```

## Logging

```php
use Illuminate\Support\Facades\Log;

Log::info("Order created", ["order_id" => $order->id, "user_id" => $user->id]);
Log::error("Payment failed", ["order_id" => $order->id, "error" => $e->getMessage()]);

// Contextual logging in controllers
logger()->info("User logged in", ["user_id" => auth()->id(), "ip" => request()->ip()]);
```

**Never log:** passwords, tokens, PII, full request bodies with sensitive data.'

LINT_LANGUAGES="PHP (Laravel Pint / PSR-12), Blade (blade-formatter), YAML, JSON, Shell (shellcheck)"
