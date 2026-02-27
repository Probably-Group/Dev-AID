---
name: celery-expert
version: 2.0.0
description: "Distributed task queues with Celery including Redis/RabbitMQ backends, Flower monitoring, beat scheduling, and task chaining. Use when configuring Celery workers, designing task workflows with chains and chords, setting up periodic tasks, or debugging task failures. Do NOT use for simple Python threading, non-Python task queues, or raw RabbitMQ without Celery (use rabbitmq-expert)."
compatibility: "Python 3.11+, Celery 5.3+, Redis or RabbitMQ"
risk_level: MEDIUM
token_budget: 3500
---
# Celery Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.2 Security Patterns (security rules)

**CWE-502: Insecure Deserialization**
- Do not: `accept_content = ['pickle']` in Celery config
- Instead: `accept_content = ['json']`, avoid pickle serialization

**CWE-94: Code Injection via Task Names**
- Do not: Dynamic task names from user input
- Instead: Whitelist allowed task names, validate before dispatch

**CWE-400: Resource Exhaustion**
- Do not: Unlimited task retries or no timeouts
- Instead: `@task(max_retries=3, time_limit=300, soft_time_limit=240)`

**CWE-285: Improper Authorization**
- Do not: Trust task arguments for authorization decisions
- Instead: Re-validate permissions inside task, fetch fresh user context

---

## 1. Security Principles

### 1.1 Data ≠ Code (CWE-502, CWE-94)

**Principle:** Never deserialize untrusted data into executable code.

**NEVER** use pickle serialization (CWE-502):
```python
# ❌ WRONG - Pickle allows arbitrary code execution
app.conf.update(
    task_serializer='pickle',
    result_serializer='pickle',
    accept_content=['pickle'],
)

# ❌ WRONG - Accepting pickle in content types
accept_content=['json', 'pickle']  # pickle is dangerous

# ✅ CORRECT - JSON-only serialization
app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],  # Only accept JSON
)
```

### 1.2 Input Validation (CWE-20)

**Principle:** Validate all task arguments at trust boundaries.

```python
# ❌ WRONG - No validation of task arguments
@app.task
def process_user(user_id, action):
    # user_id could be anything, action could be SQL injection
    db.execute(f"UPDATE users SET {action} WHERE id = {user_id}")

# ✅ CORRECT - Pydantic validation
from pydantic import BaseModel, Field
from typing import Literal

class ProcessUserArgs(BaseModel):
    user_id: int = Field(gt=0)
    action: Literal["activate", "deactivate", "suspend"]

@app.task(bind=True)
def process_user(self, user_id: int, action: str):
    args = ProcessUserArgs(user_id=user_id, action=action)  # Validates
    db.execute(
        "UPDATE users SET status = :action WHERE id = :id",
        {"action": args.action, "id": args.user_id}
    )
```

### 1.3 Idempotency (CWE-362, CWE-367)

**Principle:** Tasks MUST be safe to retry without unintended side effects.

```python
# ❌ WRONG - Non-idempotent: double-sends email on retry
@app.task
def send_email(user_id: int):
    user = get_user(user_id)
    email_service.send(user.email, "Welcome!")  # Sends again on retry!

# ✅ CORRECT - Idempotent with deduplication
@app.task(bind=True)
def send_email(self, user_id: int, idempotency_key: str):
    # Check if already processed
    if redis.exists(f"sent:{idempotency_key}"):
        return {"status": "already_sent"}

    user = get_user(user_id)
    email_service.send(user.email, "Welcome!")

    # Mark as processed (with TTL)
    redis.setex(f"sent:{idempotency_key}", 86400, "1")
    return {"status": "sent"}
```

### 1.4 Fail Secure (CWE-636)

**Principle:** Tasks should fail safely and not lose data.

```python
# ❌ WRONG - Silent failure, task not retried
@app.task
def process_payment(payment_id: int):
    try:
        process(payment_id)
    except Exception:
        pass  # Payment lost!

# ✅ CORRECT - Explicit retry with acks_late
@app.task(
    bind=True,
    max_retries=5,
    acks_late=True,  # Only ack after success
    reject_on_worker_lost=True,  # Re-queue if worker dies
)
def process_payment(self, payment_id: int):
    try:
        process(payment_id)
    except TemporaryError as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
    except PermanentError as exc:
        # Log and move to dead letter queue
        logger.error(f"Payment {payment_id} failed permanently: {exc}")
        move_to_dlq(payment_id, str(exc))
        return {"status": "failed", "reason": "permanent_error"}
```

### 1.5 Secrets ≠ Code (CWE-798)

**Principle:** Never hardcode broker credentials or API keys.

```python
# ❌ WRONG - Hardcoded credentials
app = Celery(
    'tasks',
    broker='redis://:mysecretpassword@localhost:6379/0'
)

# ❌ WRONG - Credentials in task code
@app.task
def call_api():
    api_key = "sk-123456789"
    requests.get(url, headers={"Authorization": api_key})

# ✅ CORRECT - From environment
import os

app = Celery(
    'tasks',
    broker=os.environ['CELERY_BROKER_URL'],
    backend=os.environ['CELERY_RESULT_BACKEND'],
)

@app.task
def call_api():
    api_key = os.environ['API_KEY']
    requests.get(url, headers={"Authorization": api_key})
```

### 1.6 Time Limits (CWE-400)

**Principle:** Always set time limits to prevent resource exhaustion.

```python
# ❌ WRONG - No time limit, can run forever
@app.task
def process_data(data_id: int):
    # Could hang indefinitely

# ✅ CORRECT - Explicit time limits
@app.task(
    time_limit=300,       # Hard limit: kill after 5 min
    soft_time_limit=240,  # Soft limit: raise exception after 4 min
)
def process_data(self, data_id: int):
    try:
        process(data_id)
    except SoftTimeLimitExceeded:
        logger.warning(f"Task {self.request.id} approaching timeout")
        save_checkpoint(data_id)  # Save progress
        raise  # Re-raise to be retried
```

### 1.7 Result Expiration (CWE-400, CWE-772)

**Principle:** Always expire results to prevent memory exhaustion.

```python
# ❌ WRONG - Results never expire, memory leak
app.conf.update(
    result_backend='redis://localhost:6379/1',
    # No result_expires set - leaks memory!
)

# ✅ CORRECT - Results expire after 1 hour
app.conf.update(
    result_backend='redis://localhost:6379/1',
    result_expires=3600,  # 1 hour
)

# ✅ CORRECT - Fire-and-forget tasks ignore results entirely
@app.task(ignore_result=True)
def log_event(event_data: dict):
    logger.info(f"Event: {event_data}")
```

### 1.8 Broker Authentication

**Principle:** Always authenticate broker connections.

```python
# ❌ WRONG - No authentication
broker_url='redis://localhost:6379/0'

# ✅ CORRECT - Redis with password
broker_url='redis://:password@localhost:6379/0'

# ✅ CORRECT - RabbitMQ with credentials and TLS
broker_url='amqps://user:password@broker.example.com:5671/vhost'
broker_use_ssl={
    'keyfile': '/path/to/client.key',
    'certfile': '/path/to/client.crt',
    'ca_certs': '/path/to/ca.crt',
}
```

---

## 2. Version Requirements

Use these minimum versions:
```
celery>=5.3.0           # Security fixes, Python 3.12 support
redis>=4.5.0            # Async support, security fixes
kombu>=5.3.0            # Message transport
pydantic>=2.0.0         # Task argument validation
flower>=2.0.0           # Monitoring
```

**WHEN generating requirements.txt** → pin these exact versions or higher.

---

## 3. Code Patterns

### 3.1 WHEN defining a production task

```python
from celery import Celery
from celery.exceptions import SoftTimeLimitExceeded
from pydantic import BaseModel, Field
import logging
import os

app = Celery('tasks', broker=os.environ['CELERY_BROKER_URL'])
logger = logging.getLogger(__name__)

class ProcessOrderArgs(BaseModel):
    order_id: int = Field(gt=0)

@app.task(
    bind=True,
    max_retries=5,
    time_limit=300,
    soft_time_limit=240,
    acks_late=True,
    reject_on_worker_lost=True,
)
def process_order(self, order_id: int):
    # Validate input
    args = ProcessOrderArgs(order_id=order_id)

    # Log with correlation ID
    logger.info(
        f"Processing order {args.order_id}",
        extra={'task_id': self.request.id, 'order_id': args.order_id}
    )

    try:
        result = do_processing(args.order_id)
        return {'status': 'success', 'order_id': args.order_id}
    except TemporaryError as exc:
        countdown = 2 ** self.request.retries
        logger.warning(f"Retrying in {countdown}s: {exc}")
        raise self.retry(exc=exc, countdown=countdown)
    except SoftTimeLimitExceeded:
        save_checkpoint(args.order_id)
        raise
```

### 3.2 WHEN creating workflow (chain/group/chord)

```python
from celery import chain, group, chord

# Sequential: fetch -> process -> notify
workflow = chain(
    fetch_data.s(url='https://api.example.com/data'),
    process_item.s(),
    send_notification.s()
)
result = workflow.apply_async()

# Parallel with aggregation (chord)
workflow = chord(
    group(process_item.s(item_id) for item_id in item_ids)
)(aggregate_results.s())

# Error handling in chains
@app.task(bind=True)
def on_workflow_error(self, request, exc, traceback):
    logger.error(f"Workflow failed: {exc}", extra={
        'task_id': request.id,
        'exception': str(exc),
    })
```

### 3.3 WHEN configuring production app

```python
import os

app.conf.update(
    # Broker
    broker_url=os.environ['CELERY_BROKER_URL'],
    broker_connection_retry_on_startup=True,

    # Results
    result_backend=os.environ['CELERY_RESULT_BACKEND'],
    result_expires=3600,

    # Security - JSON ONLY
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],

    # Reliability
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_time_limit=300,
    task_soft_time_limit=240,

    # Performance
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)
```

### 3.4 WHEN implementing Celery Beat scheduling

```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    'cleanup-daily': {
        'task': 'myapp.tasks.cleanup_old_data',
        'schedule': crontab(hour=2, minute=0),  # 2:00 AM daily
        'options': {'queue': 'maintenance'},
    },
    'sync-every-5-min': {
        'task': 'myapp.tasks.sync_external_data',
        'schedule': 300.0,  # Every 5 minutes
    },
}

# Prevent overlapping runs with locking
@app.task(bind=True)
def sync_external_data(self):
    lock_id = 'sync_external_data_lock'
    lock = redis.lock(lock_id, timeout=300)
    if not lock.acquire(blocking=False):
        logger.info("Task already running, skipping")
        return

    try:
        do_sync()
    finally:
        lock.release()
```

---

## 4. Anti-Patterns

### 4.1 Pickle Serialization

**NEVER** use pickle (CWE-502):
```python
# ❌ WRONG - Remote code execution vulnerability
task_serializer='pickle'
accept_content=['pickle']

# ✅ CORRECT - JSON only
task_serializer='json'
accept_content=['json']
```

### 4.2 Non-Idempotent Tasks

**NEVER** create tasks that cause duplicate side effects:
```python
# ❌ WRONG - Double charges on retry
@app.task
def charge_customer(customer_id, amount):
    payment_service.charge(customer_id, amount)  # Charges again on retry!

# ✅ CORRECT - Idempotent with payment ID
@app.task(bind=True)
def charge_customer(self, customer_id, amount, payment_id):
    if payment_service.exists(payment_id):
        return {"status": "already_charged"}
    payment_service.charge(customer_id, amount, payment_id)
```

### 4.3 Missing Time Limits

**NEVER** run without time limits (CWE-400):
```python
# ❌ WRONG - Can hang forever
@app.task
def process():
    while True:
        ...  # Worker stuck

# ✅ CORRECT - Always set limits
@app.task(time_limit=300, soft_time_limit=240)
def process():
    ...
```

### 4.4 Large Results

**NEVER** store large data in result backend:
```python
# ❌ WRONG - 100MB in Redis
@app.task
def process_file():
    return {"data": large_file_contents}  # Redis OOM!

# ✅ CORRECT - Store externally, return reference
@app.task
def process_file():
    result_key = store_in_s3(large_file_contents)
    return {"result_key": result_key}  # Small reference
```

---

## 5. Testing

**ALWAYS write tests before implementation:**
```python
import pytest
from celery.contrib.testing.tasks import ping

@pytest.fixture
def celery_config():
    return {
        'broker_url': 'memory://',
# ... (additional test cases follow same pattern)
```

**Test coverage requirements:**
- [ ] Task success path
- [ ] Task idempotency (safe retry)
- [ ] Input validation
- [ ] Retry on temporary errors
- [ ] Timeout handling

---

## 6. Pre-Generation Checklist

Before generating any Celery code:

- [ ] Serialization: JSON only, never pickle
- [ ] Time limits: Both soft_time_limit and time_limit set
- [ ] Idempotency: Task safe to retry without side effects
- [ ] Acks late: `acks_late=True` for critical tasks
- [ ] Result expiration: `result_expires` configured
- [ ] Input validation: Pydantic for task arguments
- [ ] Retry logic: Exponential backoff with max_retries
- [ ] Error handling: Explicit handling, move to DLQ if permanent
- [ ] Broker auth: Credentials from environment
- [ ] Logging: Correlation ID (task_id) in all logs

---
