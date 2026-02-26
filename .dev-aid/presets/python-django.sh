#!/usr/bin/env bash
# Preset: Python/Django backend

preset_name="python-django"
preset_description="Django 5+ / Django REST Framework / PostgreSQL / Celery-ready backend"

# Rules files: newline-delimited "filename|description" pairs
RULES_FILES="api-contracts.md|DRF serializers, ViewSets, routers, pagination, permissions, throttling
database.md|Django ORM models, migrations, QuerySet optimization, N+1 prevention
cross-service.md|Settings structure, signals, middleware, testing with pytest-django"

# Technology stack entries
TECH_STACK="| Backend Framework | Django 5+, Python 3.12+ |
| API Layer | Django REST Framework 3.15+ |
| Database | PostgreSQL 16+ (django.db.backends.postgresql) |
| Task Queue | Celery + Redis (optional) |
| Testing | pytest-django, factory_boy |
| Linting | ruff (check + format) |
| Auth | Django auth + DRF TokenAuth / JWT (simplejwt) |"

# Context loading table entries
CONTEXT_LOADING_TABLE="| **New API endpoint** | \`.claude/rules/api-contracts.md\`, \`api/views/\`, \`api/serializers/\` |
| **Database/model changes** | \`.claude/rules/database.md\`, \`apps/*/models.py\` |
| **Auth/permissions** | \`.claude/rules/api-contracts.md\` (Permissions section), \`api/permissions.py\` |
| **Settings changes** | \`.claude/rules/cross-service.md\`, \`config/settings/\` |
| **Debugging** | \`.claude/rules/troubleshooting.md\` |
| **Architecture decisions** | \`docs/decisions/index.md\` |
| **Signal/middleware work** | \`.claude/rules/cross-service.md\` |"

# Context groups
CONTEXT_GROUPS='### `api`
Read: `.claude/rules/api-contracts.md`, `api/views/`, `api/serializers/`, `api/urls.py`

### `database`
Read: `.claude/rules/database.md`, `apps/*/models.py`, `apps/*/managers.py`

### `auth`
Read: `.claude/rules/api-contracts.md` (Permissions section), `api/permissions.py`, `config/settings/base.py`

### `tasks`
Read: `apps/*/tasks.py`, `config/celery.py`

### `debug`
Read: `.claude/rules/troubleshooting.md`'

# Development workflow
WORKFLOW='```bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt  # or: pip install -e ".[dev]"

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run dev server
python manage.py runserver 0.0.0.0:8000

# Run tests
pytest -v

# Run specific app tests
pytest apps/users/ -v

# Lint
ruff check --fix .
ruff format .

# Type check
mypy apps/

# Run Celery worker (if using)
celery -A config worker -l info

# Django management
python manage.py makemigrations
python manage.py migrate
python manage.py shell_plus  # requires django-extensions
python manage.py collectstatic --noinput
```

### Admin & API Documentation

- Django Admin: `http://localhost:8000/admin/`
- DRF Browsable API: `http://localhost:8000/api/v1/`
- Schema (if drf-spectacular): `http://localhost:8000/api/schema/`
- Swagger UI: `http://localhost:8000/api/docs/`'

# Project overview
PROJECT_OVERVIEW="Django backend service with DRF API layer. All API endpoints are under \`/api/v1/\`."

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
├── config/
│   ├── __init__.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   ├── celery.py
│   └── settings/
│       ├── __init__.py
│       ├── base.py
│       ├── local.py
│       └── production.py
├── api/
│   ├── __init__.py
│   ├── urls.py
│   ├── views/
│   ├── serializers/
│   ├── permissions.py
│   ├── pagination.py
│   ├── filters.py
│   └── throttling.py
├── apps/
│   ├── users/
│   │   ├── models.py
│   │   ├── managers.py
│   │   ├── admin.py
│   │   ├── signals.py
│   │   ├── tasks.py
│   │   └── tests/
│   └── core/
│       ├── models.py
│       └── middleware.py
├── tests/
│   ├── conftest.py
│   └── factories/
├── docs/
│   ├── plans/
│   │   └── .plan-template.md
│   └── decisions/
│       ├── index.md
│       └── adr-template.md
├── scripts/
│   └── smoke-backend.sh
├── requirements/
│   ├── base.txt
│   └── dev.txt
├── manage.py
└── pyproject.toml'

# Smoke test scripts: "filename|title|checks_variable_name"
SMOKE_SCRIPTS="smoke-backend.sh|Backend Health Checks|SMOKE_BACKEND_CHECKS"

# Smoke test check bodies (referenced by variable name above)
# shellcheck disable=SC2034
SMOKE_BACKEND_CHECKS='section "Application"

if [[ -f "manage.py" ]]; then
  pass "manage.py exists"
else
  fail "manage.py not found — is this a Django project?"
fi

if python3 -c "import django" 2>/dev/null; then
  pass "Django is installed"
else
  fail "Django is not installed (pip install django)"
fi

if python3 -c "import rest_framework" 2>/dev/null; then
  pass "Django REST Framework is installed"
else
  warn "Django REST Framework is not installed (pip install djangorestframework)"
fi

section "System Check"

if python3 manage.py check --deploy 2>/dev/null; then
  pass "Django system check passes (--deploy)"
else
  if python3 manage.py check 2>/dev/null; then
    pass "Django system check passes (basic)"
    warn "Deploy checks have warnings — run: python manage.py check --deploy"
  else
    fail "Django system check fails — run: python manage.py check"
  fi
fi

section "Migrations"

MIGRATION_OUTPUT=$(python3 manage.py showmigrations --plan 2>/dev/null | grep "\[ \]" || true)
if [[ -z "$MIGRATION_OUTPUT" ]]; then
  pass "All migrations applied"
else
  warn "Unapplied migrations found — run: python manage.py migrate"
fi

MIGRATION_CHECK=$(python3 manage.py makemigrations --check --dry-run 2>/dev/null)
if [[ $? -eq 0 ]]; then
  pass "No missing migrations"
else
  warn "Model changes without migrations — run: python manage.py makemigrations"
fi

section "Configuration"

if [[ -f "requirements/base.txt" ]] || [[ -f "requirements.txt" ]] || [[ -f "pyproject.toml" ]]; then
  pass "Dependency file exists"
else
  warn "No requirements.txt or pyproject.toml found"
fi

if [[ -f "config/settings/base.py" ]] || [[ -f "config/settings.py" ]]; then
  pass "Settings module found"
else
  warn "Settings module not found in expected location"
fi

section "Linting"

if command -v ruff >/dev/null 2>&1; then
  if ruff check --quiet . 2>/dev/null; then
    pass "ruff check passes"
  else
    warn "ruff check has findings"
  fi
else
  warn "ruff not installed"
fi

section "Tests"

if command -v pytest >/dev/null 2>&1; then
  if pytest --co -q 2>/dev/null | grep -q "test"; then
    pass "Tests discovered by pytest"
  else
    warn "No tests found"
  fi
else
  warn "pytest not installed"
fi'

# Troubleshooting sections
TROUBLESHOOTING_SECTIONS='## 1. Django / Server

### Symptom: `ImproperlyConfigured: Requested setting DEFAULT_INDEX_TABLESPACE, but settings are not configured`

**Diagnosis:** `DJANGO_SETTINGS_MODULE` environment variable is not set, or the settings
module path is wrong. Django cannot locate its configuration.

**Fix:**
```bash
export DJANGO_SETTINGS_MODULE=config.settings.local
# Or add to .env and use django-environ / python-dotenv
# Verify: python -c "import django; django.setup(); print(\"OK\")"
```

---

### Symptom: `OperationalError: no such table` or `relation does not exist`

**Diagnosis:** Migrations have not been applied. The database schema is out of sync
with the Django models.

**Fix:**
```bash
python manage.py showmigrations          # see which are unapplied
python manage.py migrate                 # apply all pending
# If the migration itself is missing:
python manage.py makemigrations <app>    # generate from model changes
python manage.py migrate
```

---

## 2. Django REST Framework

### Symptom: DRF returns `{"detail": "Authentication credentials were not provided."}` for all endpoints

**Diagnosis:** `DEFAULT_PERMISSION_CLASSES` in `REST_FRAMEWORK` settings is set to
`IsAuthenticated` globally, but the request lacks valid auth credentials.

**Fix:** Either provide authentication (token/JWT) or override per-view:
```python
from rest_framework.permissions import AllowAny

class PublicViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
```
Alternatively, check `DEFAULT_AUTHENTICATION_CLASSES` — ensure the auth backend
you are using (Token, JWT, Session) is listed.

---

### Symptom: `AssertionError: The field was declared on serializer but has not been included in the fields option`

**Diagnosis:** A serializer inherits a field from the model or parent class, but `Meta.fields`
does not list it. DRF 3.14+ enforces that every declared field is in `fields` or `exclude`.

**Fix:**
```python
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "full_name"]  # include the method field
```

---

## 3. Migrations

### Symptom: `django.db.migrations.exceptions.InconsistentMigrationHistory`

**Diagnosis:** A migration was applied that depends on a migration that is no longer present,
or migrations were applied out of order (common when merging branches).

**Fix:**
```bash
# Show current state
python manage.py showmigrations

# If safe to reset (DEV ONLY):
python manage.py migrate <app> zero     # unapply all for that app
python manage.py migrate                # reapply from scratch

# If in production, create a merge migration:
python manage.py makemigrations --merge
```

---

## 4. Testing

### Symptom: Tests pass locally but fail in CI with `TransactionManagementError`

**Diagnosis:** Test code is calling ORM operations outside of an atomic block. This
commonly happens when mixing `TestCase` (wraps each test in a transaction) with code
that calls `transaction.on_commit()`.

**Fix:** Use `TransactionTestCase` for tests that rely on `on_commit` callbacks or
real transaction boundaries:
```python
from django.test import TransactionTestCase

class SignalTests(TransactionTestCase):
    def test_post_save_fires(self):
        user = User.objects.create(email="test@example.com")
        # on_commit callbacks will actually fire
```
Alternatively, use `pytest-django`s `@pytest.mark.django_db(transaction=True)`.

---

*Add entries as you encounter and solve issues. Use the Symptom -> Diagnosis -> Fix format.*'

# Memory topics: "filename|description" pairs
MEMORY_TOPICS="api-patterns.md|DRF ViewSet patterns, serializer conventions, URL routing
database-gotchas.md|ORM query issues, migration problems, N+1 query fixes
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

> **When to use:** Adding or modifying DRF endpoints, debugging serializer/view issues.
>
> **Read first for:** New ViewSets, serializer changes, permission/throttling work.

## Base URL

- **Production:** `https://api.example.com/api/v1`
- **Local dev:** `http://localhost:8000/api/v1`

## URL Configuration

```python
# config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("api.urls")),
]

# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.users import UserViewSet
from api.views.projects import ProjectViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"projects", ProjectViewSet, basename="project")

urlpatterns = [
    path("", include(router.urls)),
]
```

## ViewSet Patterns

### Standard ModelViewSet

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD for users. Supports filtering, search, ordering.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["is_active", "role"]
    search_fields = ["email", "first_name", "last_name"]
    ordering_fields = ["created_at", "email"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return (
            User.objects
            .select_related("profile")
            .prefetch_related("groups")
            .filter(organization=self.request.user.organization)
        )

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save(update_fields=["is_active"])
        return Response({"status": "deactivated"})

    @action(detail=False, methods=["get"])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
```

### Read-Only Endpoints

```python
class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ["action", "user"]

    def get_queryset(self):
        return AuditLog.objects.select_related("user").order_by("-timestamp")
```

## Serializer Conventions

```python
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    """Standard user response serializer."""
    full_name = serializers.SerializerMethodField()
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "full_name",
                  "is_active", "profile", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_full_name(self, obj) -> str:
        return f"{obj.first_name} {obj.last_name}".strip()


class UserCreateSerializer(serializers.ModelSerializer):
    """Separate serializer for creation with password handling."""
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "password"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
```

### Nested Writes

```python
class ProjectSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Project
        fields = ["id", "name", "description", "tags", "created_at"]

    def create(self, validated_data):
        tags_data = validated_data.pop("tags", [])
        project = Project.objects.create(**validated_data)
        for tag_data in tags_data:
            tag, _ = Tag.objects.get_or_create(**tag_data)
            project.tags.add(tag)
        return project
```

## Pagination

```python
# api/pagination.py
from rest_framework.pagination import PageNumberPagination

class StandardPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100

# config/settings/base.py
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "api.pagination.StandardPagination",
}
```

Response shape:
```json
{
  "count": 123,
  "next": "http://localhost:8000/api/v1/users/?page=2",
  "previous": null,
  "results": [...]
}
```

## Permissions

```python
# api/permissions.py
from rest_framework.permissions import BasePermission

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return obj.owner == request.user

class IsOrganizationMember(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "organization") and request.user.organization is not None
```

## Throttling

```python
# config/settings/base.py
REST_FRAMEWORK = {
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
    },
}
```

## Error Response Format

```json
{
  "detail": "Human-readable error message",
  "code": "error_code"
}
```

| Status | Code | When |
|--------|------|------|
| 400 | `bad_request` | Malformed input |
| 401 | `not_authenticated` | Missing or invalid credentials |
| 403 | `permission_denied` | Valid auth but insufficient permissions |
| 404 | `not_found` | Resource does not exist |
| 429 | `throttled` | Rate limit exceeded |

## Health Endpoints

```python
# api/views/health.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import connection

@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok"})

@api_view(["GET"])
@permission_classes([AllowAny])
def ready(request):
    try:
        connection.ensure_connection()
        return Response({"status": "ok", "database": "connected"})
    except Exception as e:
        return Response({"status": "error", "database": str(e)}, status=503)
```'

# shellcheck disable=SC2034
RULES_CONTENT_DATABASE='# Database Patterns

> **When to use:** Schema changes, new queries, migration work, debugging ORM issues.
>
> **Read first for:** Any model change, QuerySet optimization, N+1 prevention.

## Model Conventions

```python
from django.db import models
import uuid

class TimestampedModel(models.Model):
    """Abstract base model with created/updated timestamps."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

class User(TimestampedModel):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="members",
    )

    class Meta(TimestampedModel.Meta):
        indexes = [
            models.Index(fields=["email"], name="idx_user_email"),
            models.Index(fields=["organization", "is_active"], name="idx_user_org_active"),
        ]

    def __str__(self):
        return self.email
```

## Custom Managers

```python
class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class UserManager(models.Manager):
    def with_profile(self):
        return self.select_related("profile")

    def with_groups(self):
        return self.prefetch_related("groups")

    def active_in_org(self, org_id):
        return (
            self.select_related("profile")
            .filter(organization_id=org_id, is_active=True)
        )

class User(TimestampedModel):
    # ...
    objects = UserManager()
    active = ActiveManager()
```

## Migration Workflow

```bash
# Create migration after model changes
python manage.py makemigrations <app_name>

# Review the generated migration BEFORE applying
python manage.py sqlmigrate <app_name> <migration_number>

# Apply migrations
python manage.py migrate

# Check for missing migrations (CI gate)
python manage.py makemigrations --check --dry-run

# Show migration status
python manage.py showmigrations
```

**Rules:**
- Never modify a migration that has been applied to production
- Always review auto-generated migrations — especially `RunPython` operations
- Data migrations go in separate files from schema migrations
- Add indexes in the same migration as the table they reference
- Name data migrations explicitly: `python manage.py makemigrations --empty <app> --name populate_defaults`

## QuerySet Optimization

### Preventing N+1 Queries

```python
# BAD: N+1 — each user triggers a separate query for profile
users = User.objects.all()
for user in users:
    print(user.profile.bio)  # N additional queries

# GOOD: select_related for ForeignKey / OneToOneField (SQL JOIN)
users = User.objects.select_related("profile").all()

# GOOD: prefetch_related for ManyToMany / reverse ForeignKey (separate query)
users = User.objects.prefetch_related("groups", "projects").all()

# GOOD: Combined
users = (
    User.objects
    .select_related("profile", "organization")
    .prefetch_related("groups")
    .filter(is_active=True)
)
```

### F() Expressions and Annotations

```python
from django.db.models import F, Count, Q, Avg, Value
from django.db.models.functions import Concat

# Update without race condition — use F() to reference column value
Product.objects.filter(id=product_id).update(stock=F("stock") - quantity)

# Annotate with computed values
projects = (
    Project.objects
    .annotate(
        member_count=Count("members"),
        active_count=Count("members", filter=Q(members__is_active=True)),
    )
    .filter(member_count__gt=0)
    .order_by("-member_count")
)

# Aggregation
avg_price = Product.objects.filter(category="books").aggregate(avg=Avg("price"))
```

### Efficient Bulk Operations

```python
# Bulk create (single INSERT)
User.objects.bulk_create([
    User(email="a@example.com", first_name="A"),
    User(email="b@example.com", first_name="B"),
], batch_size=1000)

# Bulk update (single UPDATE)
users = User.objects.filter(is_active=False)
users.update(is_active=True)

# Or with individual differences:
User.objects.bulk_update(user_list, ["first_name", "last_name"], batch_size=1000)
```

### QuerySet Methods to Know

```python
# exists() instead of count() > 0
if User.objects.filter(email=email).exists():
    raise ValidationError("Email taken")

# values_list for flat column fetches
emails = User.objects.filter(is_active=True).values_list("email", flat=True)

# only() / defer() to limit fetched columns
users = User.objects.only("id", "email").all()

# Subquery for correlated lookups
from django.db.models import Subquery, OuterRef
latest_order = Order.objects.filter(user=OuterRef("pk")).order_by("-created_at")
users = User.objects.annotate(
    latest_order_date=Subquery(latest_order.values("created_at")[:1])
)
```

## Schema Conventions

- Table names: Django default (`<app>_<model>` lowercase)
- Primary keys: UUID (`uuid.uuid4`) for public APIs, auto-increment for internal
- Timestamps: `created_at` (auto_now_add), `updated_at` (auto_now), always UTC
- Foreign keys: `<model>_id` implicit from Django
- Indexes: named `idx_<model>_<columns>` for clarity
- Soft deletes: prefer `is_active` flag over actual row deletion'

# shellcheck disable=SC2034
RULES_CONTENT_CROSS_SERVICE='# Cross-Service Patterns

> **When to use:** Ensuring consistency, understanding shared conventions across the Django project.
>
> **Read first for:** Settings structure, signals, middleware, testing patterns, env variables.

## Settings Structure

```python
# config/settings/base.py — shared settings
# config/settings/local.py — local dev overrides (DEBUG=True, etc.)
# config/settings/production.py — production (read secrets from env)

# base.py
import environ

env = environ.Env()

SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

DATABASES = {
    "default": env.db("DATABASE_URL", default="postgres://localhost/myapp"),
}

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "django_filters",
    "corsheaders",
    # Local
    "apps.users",
    "apps.core",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "api.pagination.StandardPagination",
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "EXCEPTION_HANDLER": "api.exceptions.custom_exception_handler",
}
```

## Django Signals

```python
# apps/users/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.users.models import User, Profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create profile when user is created."""
    if created:
        Profile.objects.create(user=instance)

# apps/users/apps.py — register signals
class UsersConfig(AppConfig):
    name = "apps.users"

    def ready(self):
        import apps.users.signals  # noqa: F401
```

**Rules:**
- Always connect signals in `AppConfig.ready()`, never at module level
- Keep signal handlers thin — delegate to service functions
- Avoid circular imports: import models inside the handler if needed
- Prefer `post_save` with `created` check over `pre_save` when possible

## Middleware

```python
# apps/core/middleware.py
import time
import logging

logger = logging.getLogger(__name__)

class RequestTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.monotonic()
        response = self.get_response(request)
        duration = time.monotonic() - start
        logger.info(
            "request_completed",
            extra={
                "method": request.method,
                "path": request.path,
                "status": response.status_code,
                "duration_ms": round(duration * 1000, 2),
            },
        )
        return response
```

## Environment Variables

| Variable | Source | Description |
|----------|--------|-------------|
| `DATABASE_URL` | `.env` / Secret | PostgreSQL connection string |
| `SECRET_KEY` | Secret | Django secret key |
| `DEBUG` | Config | Enable debug mode (never True in prod) |
| `ALLOWED_HOSTS` | Config | Comma-separated allowed hostnames |
| `CORS_ALLOWED_ORIGINS` | Config | Comma-separated CORS origins |
| `REDIS_URL` | `.env` / Secret | Redis for caching/Celery |
| `CELERY_BROKER_URL` | `.env` / Secret | Celery broker URL |

**Secrets are NEVER committed to git.** Use `.env` locally, secrets manager in production.

## Logging

```python
# config/settings/base.py
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": env("LOG_LEVEL", default="INFO"),
    },
    "loggers": {
        "django.db.backends": {
            "level": "WARNING",  # set to DEBUG to see SQL queries
        },
    },
}
```

**Never log:** passwords, tokens, PII, full request bodies with sensitive data.

## Testing Conventions

### pytest-django Setup

```python
# conftest.py
import pytest
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def user(db):
    from apps.users.models import User
    return User.objects.create_user(
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
    )
```

### factory_boy Factories

```python
# tests/factories/users.py
import factory
from apps.users.models import User

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        self.set_password(extracted or "defaultpass123")
        if create:
            self.save(update_fields=["password"])
```

### Test Examples

```python
import pytest
from rest_framework import status

@pytest.mark.django_db
class TestUserAPI:
    def test_list_users(self, auth_client):
        response = auth_client.get("/api/v1/users/")
        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data

    def test_create_user(self, auth_client):
        data = {"email": "new@example.com", "first_name": "New", "last_name": "User", "password": "securepass123"}
        response = auth_client.post("/api/v1/users/", data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_unauthenticated_rejected(self, api_client):
        response = api_client.get("/api/v1/users/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

### TestCase vs TransactionTestCase

- **`TestCase`** (default): Wraps each test in a transaction, rolled back after. Fast.
- **`TransactionTestCase`**: Each test gets a real commit. Use when testing `on_commit` callbacks, signals that depend on committed data, or Celery tasks.
- **`pytest.mark.django_db`**: Use `@pytest.mark.django_db` for function-based tests. Add `transaction=True` when needed.

## Date/Time Format

All timestamps use **ISO 8601 UTC**: `2026-01-01T12:00:00Z`

```python
from django.utils import timezone
now = timezone.now()  # always timezone-aware
```

Always use `django.utils.timezone.now()` instead of `datetime.now()`.

## Security Best Practices

### Input Validation & Sanitization
- Use DRF serializers as the primary validation layer — never trust raw `request.data`
- Validate all serializer fields with explicit validators: `MaxLengthValidator`, `RegexValidator`, custom `validate_<field>` methods
- Use `bleach` for HTML sanitization if rendering user content

### SQL Injection Prevention
- NEVER use `.raw()` or `.extra()` with user input — use parameterized queries
- Example: `User.objects.raw("SELECT * FROM user WHERE id = %s", [user_id])` (safe)
- Prefer ORM queries over raw SQL whenever possible

### Dependency Scanning
```bash
pip-audit                    # Known vulnerabilities
safety check                 # Alternative scanner
bandit -r app/               # Python security anti-patterns
```
- Run in CI on every PR

### Secrets Management
- Never commit `.env` files — use `.env.example` as template
- Use `django-environ` / `python-decouple` for settings
- In production: use vault, AWS Secrets Manager, or K8s secrets

### Rate Limiting
- DRF throttling: configure `DEFAULT_THROTTLE_RATES` in settings
- Use `django-ratelimit` for view-level rate limiting on sensitive endpoints (login, password reset)

### CSRF Protection
- Django includes CSRF middleware by default — never disable it
- For DRF APIs: use `SessionAuthentication` with CSRF, or `TokenAuthentication`/JWT without
- Always validate `Origin` and `Referer` headers for sensitive operations

## Performance Checklist

### Database
- Use `select_related()` for ForeignKey (JOIN), `prefetch_related()` for M2M (separate query)
- Use `.only()` / `.defer()` to load only needed fields
- Add `db_index=True` to frequently filtered fields
- Use `django-debug-toolbar` to catch N+1 queries in development

### Caching
- Use Django'\''s cache framework with Redis: `CACHES = {"default": {"BACKEND": "django.core.cache.backends.redis.RedisCache"}}`
- Cache expensive querysets: `cache.get_or_set("key", queryset.all, timeout=300)`
- Use `@cache_page` decorator for view-level caching
- Invalidate cache explicitly when underlying data changes'

LINT_LANGUAGES="Python (ruff check + ruff format), SQL, YAML, Shell (shellcheck)"
