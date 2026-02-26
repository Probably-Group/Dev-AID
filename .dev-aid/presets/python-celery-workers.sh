#!/usr/bin/env bash
# Preset: Python Celery + RabbitMQ/Redis async task processing

preset_name="python-celery-workers"
preset_description="Python Celery workers with RabbitMQ/Redis, task routing, Flower monitoring, beat scheduling"

# Rules files: newline-delimited "filename|description" pairs
RULES_FILES="task-patterns.md|Celery task definitions, retries, chains/groups/chords, idempotency
messaging.md|RabbitMQ topology, dead letter queues, message serialization, consumer patterns
cross-service.md|Django/FastAPI integration, Flower monitoring, beat scheduling, testing, logging"

# Technology stack entries
TECH_STACK="| Task Queue | Celery 5.4+ |
| Broker | RabbitMQ 3.13+ / Redis 7+ |
| Result Backend | Redis / PostgreSQL / RPC |
| Monitoring | Flower, Prometheus + Grafana |
| Scheduling | Celery Beat (database or file) |
| Framework | *Django / FastAPI / standalone* |
| Language | Python 3.12+ |
| Testing | pytest, pytest-celery |
| Linting | ruff (check + format) |"

# Context loading table entries
CONTEXT_LOADING_TABLE="| **New task** | \`.claude/rules/task-patterns.md\`, \`app/tasks/\` |
| **Queue/routing changes** | \`.claude/rules/messaging.md\`, \`celeryconfig.py\` |
| **Retry/error handling** | \`.claude/rules/task-patterns.md\` (Retry section) |
| **Beat schedule** | \`.claude/rules/cross-service.md\` (Beat section), \`celeryconfig.py\` |
| **Debugging** | \`.claude/rules/troubleshooting.md\` |
| **Broker topology** | \`.claude/rules/messaging.md\` (Exchange/Queue section) |
| **Integration patterns** | \`.claude/rules/cross-service.md\` |"

# Context groups
CONTEXT_GROUPS='### `tasks`
Read: `.claude/rules/task-patterns.md`, `app/tasks/`, `app/celery.py`

### `messaging`
Read: `.claude/rules/messaging.md`, `celeryconfig.py`, `docker-compose.yml` (broker section)

### `config`
Read: `.claude/rules/cross-service.md`, `celeryconfig.py`, `.env.example`

### `debug`
Read: `.claude/rules/troubleshooting.md`'

# Development workflow
WORKFLOW='```bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # or: pip install -e ".[dev]"

# Start broker (RabbitMQ or Redis)
docker compose up -d rabbitmq redis

# Start Celery worker
celery -A app.celery worker --loglevel=info --concurrency=4

# Start Celery Beat (periodic tasks)
celery -A app.celery beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler

# Start Flower monitoring
celery -A app.celery flower --port=5555

# Run a task manually from shell
python -c "from app.tasks.example import add; add.delay(4, 6)"

# Inspect active workers
celery -A app.celery inspect active

# Purge all messages from a queue
celery -A app.celery purge -Q default

# Run tests
pytest -v

# Lint
ruff check --fix .
ruff format .
```

### Monitoring Dashboards

- Flower: `http://localhost:5555`
- RabbitMQ Management: `http://localhost:15672` (guest/guest)
- Redis Commander (optional): `http://localhost:8081`'

# Project overview
PROJECT_OVERVIEW="Celery-based async task processing system. Tasks are defined in \`app/tasks/\` and routed to specialized queues via \`celeryconfig.py\`."

# Workspace structure
WORKSPACE_STRUCTURE='{{PROJECT_NAME}}/
├── CLAUDE.md
├── .claude/
│   ├── rules/
│   │   ├── task-patterns.md
│   │   ├── messaging.md
│   │   ├── cross-service.md
│   │   └── troubleshooting.md
│   ├── hooks/
│   │   └── lint-on-edit.sh
│   ├── memory/
│   │   ├── MEMORY.md
│   │   ├── task-patterns.md
│   │   ├── broker-issues.md
│   │   └── debugging.md
│   └── commands/
│       ├── review.md
│       ├── test.md
│       ├── plan.md
│       ├── smoke.md
│       └── lint.md
├── app/
│   ├── __init__.py
│   ├── celery.py
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── email.py
│   │   ├── reports.py
│   │   ├── data_pipeline.py
│   │   └── maintenance.py
│   ├── models/
│   ├── services/
│   └── utils/
├── celeryconfig.py
├── tests/
│   ├── conftest.py
│   ├── test_tasks/
│   └── test_integration/
├── docs/
│   ├── plans/
│   │   └── .plan-template.md
│   └── decisions/
│       ├── index.md
│       └── adr-template.md
├── scripts/
│   └── smoke-workers.sh
├── docker-compose.yml
├── requirements.txt
└── pyproject.toml'

# Smoke test scripts: "filename|title|checks_variable_name"
SMOKE_SCRIPTS="smoke-workers.sh|Worker Health Checks|SMOKE_WORKERS_CHECKS"

# Smoke test check bodies (referenced by variable name above)
# shellcheck disable=SC2034
SMOKE_WORKERS_CHECKS='section "Application"

if [[ -f "app/celery.py" ]]; then
  pass "app/celery.py exists"
else
  fail "app/celery.py not found"
fi

if python3 -c "import celery" 2>/dev/null; then
  pass "Celery is installed"
else
  fail "Celery is not installed (pip install celery)"
fi

if [[ -f "celeryconfig.py" ]]; then
  pass "celeryconfig.py exists"
else
  warn "celeryconfig.py not found — using defaults or in-app config"
fi

section "Broker Connectivity"

if docker compose ps 2>/dev/null | grep -q "rabbitmq.*running"; then
  pass "RabbitMQ container is running"
elif python3 -c "import redis; redis.Redis().ping()" 2>/dev/null; then
  pass "Redis is reachable"
else
  warn "No broker detected — start RabbitMQ or Redis (docker compose up -d)"
fi

if celery -A app.celery inspect ping --timeout=5 2>/dev/null | grep -q "pong"; then
  pass "Celery worker is responding"
else
  warn "No Celery worker responding — start with: celery -A app.celery worker"
fi

section "Flower Monitoring"

if curl -s -o /dev/null -w "%{http_code}" http://localhost:5555/api/workers 2>/dev/null | grep -q "200"; then
  pass "Flower is accessible at http://localhost:5555"
else
  warn "Flower not running — start with: celery -A app.celery flower"
fi

section "Linting"

if command -v ruff >/dev/null 2>&1; then
  if ruff check --quiet app/ 2>/dev/null; then
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
TROUBLESHOOTING_SECTIONS='## 1. Worker / Task Execution

### Symptom: `Received unregistered task` error in worker logs

**Diagnosis:** The worker cannot find the task module. This happens when task
auto-discovery misses the module, or the worker was started with a different app
instance than where tasks are defined.

**Fix:**
```bash
# Verify task is registered
celery -A app.celery inspect registered

# Ensure autodiscovery includes the module
# In app/celery.py:
app.autodiscover_tasks(["app.tasks"])

# Restart the worker after code changes
celery -A app.celery worker --loglevel=info
```

---

### Symptom: Tasks stuck in `PENDING` state, never execute

**Diagnosis:** Either no worker is consuming the queue the task was routed to,
or the broker connection is down. PENDING is also the default state for unknown
task IDs, so the task may not have been sent at all.

**Fix:**
```bash
# Check active queues
celery -A app.celery inspect active_queues

# Check if task was actually sent (check broker)
rabbitmqctl list_queues name messages messages_ready

# Ensure routing matches — task_routes must match worker -Q flag
celery -A app.celery worker -Q default,emails,reports --loglevel=info
```

---

### Symptom: `MaxRetriesExceededError` after repeated failures

**Diagnosis:** Task hit its `max_retries` limit. The underlying error (e.g.,
network timeout, API rate limit) was never resolved between retries.

**Fix:**
```python
# Use exponential backoff to space retries
@shared_task(bind=True, max_retries=5, autoretry_for=(ConnectionError,),
             retry_backoff=True, retry_backoff_max=600, retry_jitter=True)
def call_external_api(self, url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()
```

---

## 2. Broker (RabbitMQ / Redis)

### Symptom: `kombu.exceptions.OperationalError: [Errno 111] Connection refused`

**Diagnosis:** The Celery worker cannot connect to the broker. Either the broker
is not running, the connection URL is wrong, or a firewall is blocking the port.

**Fix:**
```bash
# Check broker is running
docker compose ps rabbitmq
# or
redis-cli ping

# Verify CELERY_BROKER_URL in .env
# RabbitMQ: amqp://guest:guest@localhost:5672//
# Redis: redis://localhost:6379/0

# Check from inside the container
docker compose exec worker python -c "
from app.celery import app
print(app.connection().ensure_connection(max_retries=3))
"
```

---

### Symptom: RabbitMQ queues growing unbounded, memory alarm triggered

**Diagnosis:** Consumers are not keeping up with producers. Workers may be too
slow, have crashed, or the prefetch count is too low.

**Fix:**
```bash
# Check consumer count per queue
rabbitmqctl list_queues name consumers messages

# Scale workers horizontally
celery -A app.celery worker --concurrency=8 -Q default

# Set prefetch to allow batching
# In celeryconfig.py:
worker_prefetch_multiplier = 4

# Add TTL / dead-letter to prevent unbounded growth
# See messaging.md for exchange/queue topology
```

---

## 3. Beat Scheduler

### Symptom: Periodic tasks run multiple times simultaneously

**Diagnosis:** Multiple Beat instances are running. Celery Beat is not designed
for multiple instances — each one will independently schedule tasks.

**Fix:**
```bash
# Ensure only ONE beat instance runs
# Use a PID file:
celery -A app.celery beat --pidfile=/var/run/celery/beat.pid

# Or use django-celery-beat with DatabaseScheduler (supports locking):
celery -A app.celery beat --scheduler django_celery_beat.schedulers:DatabaseScheduler

# Check for duplicate processes
ps aux | grep "celery beat"
```

---

## 4. Testing

### Symptom: Tests hang when calling `.delay()` or `.apply_async()`

**Diagnosis:** Tests are trying to send tasks to a real broker. Without a
running worker, the result `.get()` call blocks forever.

**Fix:**
```python
# In conftest.py — force synchronous execution
@pytest.fixture(autouse=True)
def celery_eager(settings):
    # Django
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True

# Or in celeryconfig.py for test env
import os
if os.environ.get("TESTING"):
    task_always_eager = True
    task_eager_propagates = True

# Or call the task directly (preferred for unit tests)
result = my_task("arg1", "arg2")  # call, not .delay()
```

---

*Add entries as you encounter and solve issues. Use the Symptom -> Diagnosis -> Fix format.*'

# Memory topics: "filename|description" pairs
MEMORY_TOPICS="task-patterns.md|Task design patterns, routing rules, retry strategies
broker-issues.md|Broker configuration issues, connection problems, queue management
debugging.md|Common errors encountered and their solutions"

# Slash commands to scaffold
COMMANDS="review.md
test.md
plan.md
smoke.md
lint.md"

# --- Substantive Rules Content ---

# shellcheck disable=SC2034
RULES_CONTENT_TASK_PATTERNS='# Task Patterns

> **When to use:** Defining new tasks, configuring retries, building task workflows.
>
> **Read first for:** Any new task, retry logic, chain/group/chord patterns, idempotency.

## Task Definition Styles

### `@shared_task` vs `@app.task`

```python
from celery import shared_task

# PREFERRED: shared_task — framework-agnostic, works with Django/FastAPI
@shared_task(bind=True, name="emails.send_welcome")
def send_welcome_email(self, user_id: int) -> dict:
    """Send welcome email to a new user."""
    user = get_user(user_id)
    send_email(user.email, "Welcome!", render_template("welcome.html", user=user))
    return {"user_id": user_id, "status": "sent"}

# AVOID unless standalone Celery app with no framework integration
from app.celery import app

@app.task(bind=True)
def standalone_task(self, arg):
    pass
```

**Always use `bind=True`** to access the task instance (`self`) for retries, logging, and request metadata.

### Naming Convention

```python
# Explicit task names prevent import path issues
@shared_task(bind=True, name="<module>.<action>")

# Examples:
@shared_task(bind=True, name="emails.send_welcome")
@shared_task(bind=True, name="reports.generate_monthly")
@shared_task(bind=True, name="data.sync_inventory")
```

## Retry Strategies

### Automatic Retry with Backoff

```python
@shared_task(
    bind=True,
    max_retries=5,
    autoretry_for=(ConnectionError, TimeoutError, requests.HTTPError),
    retry_backoff=True,         # exponential: 1s, 2s, 4s, 8s, 16s
    retry_backoff_max=600,      # cap at 10 minutes
    retry_jitter=True,          # randomize to prevent thundering herd
)
def fetch_external_data(self, url: str) -> dict:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()
```

### Manual Retry with Custom Logic

```python
@shared_task(bind=True, max_retries=3)
def process_payment(self, order_id: int) -> dict:
    try:
        order = get_order(order_id)
        result = payment_gateway.charge(order.total, order.payment_method)
        return {"order_id": order_id, "transaction_id": result.id}
    except PaymentDeclinedError:
        # Do NOT retry — permanent failure
        mark_order_failed(order_id)
        raise
    except PaymentGatewayTimeout:
        # Retry with increasing delay
        raise self.retry(countdown=60 * (self.request.retries + 1))
```

### Retry-Safe (Idempotent) Tasks

```python
@shared_task(bind=True, max_retries=3, autoretry_for=(ConnectionError,),
             retry_backoff=True)
def sync_user_to_crm(self, user_id: int) -> dict:
    """Idempotent: uses upsert so retries are safe."""
    user = get_user(user_id)
    # Upsert — same result regardless of how many times it runs
    crm_client.upsert_contact(
        external_id=str(user.id),
        email=user.email,
        name=user.full_name,
    )
    return {"user_id": user_id, "synced": True}
```

**Idempotency rules:**
- Use database upserts instead of inserts
- Check if work was already done before doing it again
- Use unique constraint / dedup key for external API calls
- Store a task execution ID to detect duplicates

## Task Workflows

### Chain — Sequential Pipeline

```python
from celery import chain

# Each task passes its return value to the next
workflow = chain(
    download_file.s(url),
    parse_csv.s(),
    validate_rows.s(),
    import_to_database.s(),
)
result = workflow.apply_async()
```

### Group — Parallel Fan-Out

```python
from celery import group

# Run all tasks in parallel, collect results
workflow = group([
    process_image.s(image_id)
    for image_id in image_ids
])
result = workflow.apply_async()
all_results = result.get(timeout=300)  # list of individual results
```

### Chord — Fan-Out Then Aggregate

```python
from celery import chord

# Run group in parallel, then call callback with all results
workflow = chord(
    [analyze_page.s(page_id) for page_id in page_ids],
    aggregate_report.s(report_id=report_id),
)
result = workflow.apply_async()
```

### ETA and Countdown Scheduling

```python
from datetime import datetime, timedelta, timezone

# Execute after 60-second delay
send_reminder.apply_async(args=[user_id], countdown=60)

# Execute at a specific time
eta = datetime.now(timezone.utc) + timedelta(hours=24)
send_digest.apply_async(args=[user_id], eta=eta)
```

## Task Routing

```python
# celeryconfig.py
task_routes = {
    "emails.*":   {"queue": "emails"},
    "reports.*":  {"queue": "reports"},
    "data.*":     {"queue": "data_pipeline"},
    "*":          {"queue": "default"},
}

# Start workers for specific queues
# celery -A app.celery worker -Q emails --concurrency=2
# celery -A app.celery worker -Q reports --concurrency=1
# celery -A app.celery worker -Q default,data_pipeline --concurrency=4
```

## Task Signatures and Immutable Signatures

```python
from celery import signature

# Partial application — fill in args later
sig = send_email.s(user_id)           # mutable (chain passes result)
sig = send_email.si(user_id)          # immutable (ignores previous result)

# Use immutable signatures in chords when callback does not need group results
chord(
    [fetch_data.s(url) for url in urls],
    notify_complete.si(job_id=job_id),  # si() — ignore group results
)
```

## Late Acknowledgement

```python
# celeryconfig.py
task_acks_late = True         # ack AFTER task completes, not before
task_reject_on_worker_lost = True  # requeue if worker crashes mid-task
```

**Use `acks_late` when:** tasks are expensive and must not be lost if a worker crashes.
**Caveat:** tasks must be idempotent since they may execute more than once.'

# shellcheck disable=SC2034
RULES_CONTENT_MESSAGING='# Messaging Patterns

> **When to use:** Configuring broker topology, debugging message flow, tuning consumer performance.
>
> **Read first for:** Queue setup, dead letter exchanges, serialization, connection issues.

## Broker Configuration

### RabbitMQ

```python
# celeryconfig.py
broker_url = "amqp://user:password@rabbitmq-host:5672/vhost"
broker_connection_retry_on_startup = True
broker_pool_limit = 10          # connection pool size
broker_heartbeat = 120          # seconds between heartbeats
```

### Redis

```python
# celeryconfig.py
broker_url = "redis://redis-host:6379/0"
broker_transport_options = {
    "visibility_timeout": 3600,   # 1 hour — must exceed longest task duration
    "queue_order_strategy": "priority",
    "sep": ":",
}
```

**Choose RabbitMQ when:** you need complex routing (topic/fanout exchanges), dead letter
queues, publisher confirms, or message priorities.

**Choose Redis when:** you want simplicity, already use Redis for caching, or need
the result backend and broker on the same service.

## RabbitMQ Exchange/Queue Topology

### Default Setup (Direct Exchange)

```python
# celeryconfig.py
from kombu import Exchange, Queue

task_default_exchange = "tasks"
task_default_exchange_type = "direct"
task_default_routing_key = "default"

task_queues = (
    Queue("default",   Exchange("tasks", type="direct"), routing_key="default"),
    Queue("emails",    Exchange("tasks", type="direct"), routing_key="emails"),
    Queue("reports",   Exchange("tasks", type="direct"), routing_key="reports"),
    Queue("data_pipeline", Exchange("tasks", type="direct"), routing_key="data_pipeline"),
)
```

### Dead Letter Queues

```python
from kombu import Exchange, Queue

# Dead letter exchange — receives messages that fail or expire
dlx = Exchange("dead-letters", type="direct")

task_queues = (
    Queue("default", Exchange("tasks", type="direct"), routing_key="default",
          queue_arguments={
              "x-dead-letter-exchange": "dead-letters",
              "x-dead-letter-routing-key": "dead.default",
          }),
    Queue("emails", Exchange("tasks", type="direct"), routing_key="emails",
          queue_arguments={
              "x-dead-letter-exchange": "dead-letters",
              "x-dead-letter-routing-key": "dead.emails",
              "x-message-ttl": 86400000,  # 24h TTL in milliseconds
          }),
    # DLQ consumers — monitor these for failed messages
    Queue("dead.default", dlx, routing_key="dead.default"),
    Queue("dead.emails", dlx, routing_key="dead.emails"),
)
```

### Message TTL and Queue Limits

```python
Queue("reports", Exchange("tasks"), routing_key="reports",
      queue_arguments={
          "x-message-ttl": 3600000,        # messages expire after 1 hour
          "x-max-length": 10000,            # max 10k messages in queue
          "x-overflow": "reject-publish",   # reject new messages when full
      })
```

## Consumer Configuration

### Prefetch Count

```python
# celeryconfig.py
worker_prefetch_multiplier = 1   # 1 = fetch one task at a time per worker process
                                 # Higher = more throughput, but less fair scheduling
                                 # 0 = unlimited (only for very fast tasks)
```

**Rule of thumb:**
- I/O-bound tasks (API calls, email): `prefetch = 1`
- CPU-bound tasks (data processing): `prefetch = 1`
- Very fast tasks (<100ms): `prefetch = 4-8`

### Concurrency

```bash
# prefork (default) — one process per CPU core
celery -A app.celery worker --pool=prefork --concurrency=4

# gevent — for I/O-bound tasks, many concurrent greenlets
celery -A app.celery worker --pool=gevent --concurrency=100

# solo — single-threaded, useful for debugging
celery -A app.celery worker --pool=solo
```

## Message Serialization

```python
# celeryconfig.py
task_serializer = "json"        # ALWAYS use json for safety
result_serializer = "json"
accept_content = ["json"]       # reject pickle — security risk
event_serializer = "json"

# For binary payloads or performance-critical paths:
# task_serializer = "msgpack"
# accept_content = ["json", "msgpack"]
# pip install msgpack
```

**Never use pickle** — it allows arbitrary code execution from untrusted messages.

## Publisher Confirms (RabbitMQ)

```python
# celeryconfig.py — confirm broker received the message
broker_transport_options = {
    "confirm_publish": True,
}

# In code — check that the task was actually enqueued
result = my_task.apply_async(args=[data])
# result.id is set immediately, but task may not be on broker yet without confirms
```

## Connection Pooling

```python
# celeryconfig.py
broker_pool_limit = 10           # max broker connections per worker
result_backend_transport_options = {
    "max_connections": 20,       # for Redis result backend
}
```'

# shellcheck disable=SC2034
RULES_CONTENT_CROSS_SERVICE='# Cross-Service Patterns

> **When to use:** Setting up Celery with Django/FastAPI, monitoring, scheduling, testing.
>
> **Read first for:** App initialization, Flower, beat config, test fixtures, logging.

## Celery App Setup

### Django Integration

```python
# proj/celery.py
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proj.settings")

app = Celery("proj")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# proj/__init__.py
from .celery import app as celery_app
__all__ = ("celery_app",)
```

```python
# proj/settings.py
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "amqp://localhost")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
```

### FastAPI Integration

```python
# app/celery.py
from celery import Celery

celery_app = Celery("app")
celery_app.config_from_object("celeryconfig")
celery_app.autodiscover_tasks(["app.tasks"])
```

```python
# app/main.py — trigger tasks from FastAPI endpoints
from fastapi import FastAPI, BackgroundTasks
from app.tasks.reports import generate_report

app = FastAPI()

@app.post("/api/v1/reports")
async def create_report(report_request: ReportRequest):
    result = generate_report.delay(report_request.dict())
    return {"task_id": result.id, "status": "queued"}

@app.get("/api/v1/tasks/{task_id}")
async def get_task_status(task_id: str):
    from celery.result import AsyncResult
    result = AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
    }
```

## Result Backends

```python
# celeryconfig.py

# Redis (fast, volatile)
result_backend = "redis://localhost:6379/1"
result_expires = 3600  # results expire after 1 hour

# PostgreSQL via SQLAlchemy (persistent)
result_backend = "db+postgresql://user:pass@localhost/celery_results"

# RPC (results returned via reply queue — no persistent storage)
result_backend = "rpc://"
result_persistent = False

# Disable results entirely (saves resources if you never call .get())
result_backend = None  # or omit
task_ignore_result = True
```

## Flower Monitoring

```bash
# Start Flower
celery -A app.celery flower \
  --port=5555 \
  --broker_api=http://guest:guest@localhost:15672/api/ \
  --basic_auth=admin:changeme

# Flower API examples
curl http://localhost:5555/api/workers           # list workers
curl http://localhost:5555/api/tasks             # recent tasks
curl http://localhost:5555/api/task/info/{id}    # task detail
curl -X POST http://localhost:5555/api/task/revoke/{id}  # cancel task
```

## Beat Scheduling

### Static Schedule (celeryconfig.py)

```python
from celery.schedules import crontab

beat_schedule = {
    "cleanup-expired-sessions": {
        "task": "maintenance.cleanup_sessions",
        "schedule": crontab(minute=0, hour="*/6"),  # every 6 hours
    },
    "send-daily-digest": {
        "task": "emails.send_daily_digest",
        "schedule": crontab(minute=0, hour=8),       # 08:00 UTC daily
    },
    "sync-inventory": {
        "task": "data.sync_inventory",
        "schedule": 300.0,                           # every 5 minutes
    },
    "generate-weekly-report": {
        "task": "reports.generate_weekly",
        "schedule": crontab(minute=0, hour=9, day_of_week=1),  # Monday 09:00
        "args": (),
        "kwargs": {"report_type": "weekly"},
    },
}

beat_schedule_filename = "celerybeat-schedule"  # persistence file
```

### Dynamic Schedule (Django Celery Beat)

```bash
pip install django-celery-beat

# Add to INSTALLED_APPS
# "django_celery_beat"

# Run migrations
python manage.py migrate django_celery_beat

# Start beat with database scheduler
celery -A proj beat --scheduler django_celery_beat.schedulers:DatabaseScheduler

# Manage schedules via Django admin at /admin/django_celery_beat/
```

## Environment Variables

| Variable | Source | Description |
|----------|--------|-------------|
| `CELERY_BROKER_URL` | `.env` / Secret | Broker connection string |
| `CELERY_RESULT_BACKEND` | `.env` / Secret | Result backend connection string |
| `CELERY_WORKER_CONCURRENCY` | Config | Number of worker processes |
| `CELERY_TASK_ALWAYS_EAGER` | Config | Force synchronous (testing only) |
| `FLOWER_BASIC_AUTH` | Secret | Flower dashboard credentials |
| `RABBITMQ_DEFAULT_USER` | Secret | RabbitMQ admin username |
| `RABBITMQ_DEFAULT_PASS` | Secret | RabbitMQ admin password |

**Secrets are NEVER committed to git.** Use `.env` locally, secrets manager in production.

## Structured Logging

```python
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task(bind=True, name="emails.send_welcome")
def send_welcome_email(self, user_id: int):
    logger.info("task_started", extra={
        "task_id": self.request.id,
        "user_id": user_id,
        "queue": self.request.delivery_info.get("routing_key"),
    })
    try:
        send_email(user_id)
        logger.info("task_completed", extra={"user_id": user_id})
    except Exception as exc:
        logger.error("task_failed", extra={
            "user_id": user_id,
            "error": str(exc),
            "retries": self.request.retries,
        })
        raise
```

**Never log:** passwords, tokens, PII, full message bodies with sensitive data.

## Testing Tasks

### Synchronous Execution (Unit Tests)

```python
# conftest.py
import pytest

@pytest.fixture(autouse=True)
def celery_config():
    """Force tasks to run synchronously in tests."""
    from app.celery import celery_app
    celery_app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
    )

# test_tasks.py
def test_send_welcome_email(db_session, user_factory):
    user = user_factory.create()
    result = send_welcome_email(user.id)  # runs synchronously
    assert result["status"] == "sent"
    assert result["user_id"] == user.id
```

### Testing Task Retries

```python
from unittest.mock import patch

def test_retry_on_connection_error():
    with patch("app.tasks.email.send_email") as mock_send:
        mock_send.side_effect = [ConnectionError("timeout"), {"status": "sent"}]
        # With eager mode, retries execute inline
        result = send_welcome_email(user_id=1)
        assert mock_send.call_count == 2
```

### Testing Chains and Groups

```python
def test_data_pipeline_chain():
    """Test the full pipeline as a chain."""
    result = chain(
        download_file.s("https://example.com/data.csv"),
        parse_csv.s(),
        validate_rows.s(),
    ).apply()  # .apply() runs synchronously
    assert result.get() is not None
```'

LINT_LANGUAGES="Python (ruff check + ruff format), YAML, Docker (hadolint), Shell (shellcheck)"
