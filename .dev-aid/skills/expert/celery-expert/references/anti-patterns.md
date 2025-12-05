# Celery Anti-Patterns and Common Mistakes

## Mistake 1: Using Pickle Serialization

### The Problem
Pickle serialization creates a critical security vulnerability allowing arbitrary code execution.

### DON'T
```python
app.conf.task_serializer = 'pickle'
app.conf.result_serializer = 'pickle'
app.conf.accept_content = ['pickle', 'json']
```

### DO
```python
app.conf.task_serializer = 'json'
app.conf.result_serializer = 'json'
app.conf.accept_content = ['json']
```

### Why It Matters
Pickle can execute arbitrary code during deserialization. An attacker with access to your message broker can inject malicious tasks that execute code on your workers.

---

## Mistake 2: Not Making Tasks Idempotent

### The Problem
Non-idempotent tasks produce incorrect results when retried.

### DON'T
```python
# Retries will increment multiple times
@app.task
def increment_counter(user_id):
    user = User.get(user_id)
    user.counter += 1
    user.save()
```

**Issue**: If the task fails after incrementing but before returning, a retry will increment again, leading to incorrect counter values.

### DO
```python
# Safe to retry - sets to specific value
@app.task
def set_counter(user_id, value):
    user = User.get(user_id)
    user.counter = value
    user.save()

# Or use database operations that are inherently idempotent
@app.task
def increment_counter_safe(user_id, request_id):
    # Use unique request_id to prevent duplicate processing
    if ProcessedRequest.exists(request_id):
        return {'status': 'already_processed'}

    user = User.get(user_id)
    user.counter += 1
    user.save()
    ProcessedRequest.create(request_id)
    return {'status': 'success'}
```

### Why It Matters
Tasks can fail after partial execution. Retries must not cause unintended side effects or data corruption.

---

## Mistake 3: Missing Time Limits

### The Problem
Tasks without time limits can run indefinitely, blocking workers and consuming resources.

### DON'T
```python
@app.task
def slow_task():
    # Calls external API with no timeout
    response = requests.get('https://api.example.com/slow')
    return response.json()
```

### DO
```python
@app.task(time_limit=30, soft_time_limit=25)
def safe_task():
    try:
        # Request timeout shorter than task limit
        response = requests.get('https://api.example.com/slow', timeout=20)
        return response.json()
    except SoftTimeLimitExceeded:
        # Cleanup before hard limit
        logger.warning("Task approaching time limit, cleaning up")
        raise
```

### Why It Matters
- Prevents worker starvation when external services hang
- Ensures predictable resource usage
- Allows workers to be recycled/restarted without waiting for stuck tasks

---

## Mistake 4: Storing Large Results

### The Problem
Storing large data in result backend wastes memory and can crash Redis.

### DON'T
```python
@app.task
def process_file(file_id):
    # Returns 100MB file content stored in Redis!
    return read_large_file(file_id)

@app.task
def generate_report(user_id):
    # Returns huge dataset
    return {
        'users': list(User.all()),  # 1M records
        'transactions': list(Transaction.all()),  # 10M records
    }
```

### DO
```python
@app.task
def process_file(file_id):
    content = read_large_file(file_id)
    # Store in S3/object storage
    result_key = save_to_s3(content)
    # Store only reference in result backend
    return {'result_key': result_key}

@app.task(ignore_result=True)
def generate_report(user_id):
    """Fire-and-forget task - no result needed"""
    report = generate_user_report(user_id)
    email_report(user_id, report)
    # No return value - result ignored
```

### Why It Matters
- Result backend (Redis) has memory limits
- Large results slow down task completion
- Results should be references to external storage, not the data itself

---

## Mistake 5: Not Using acks_late for Critical Tasks

### The Problem
Default acknowledgment happens before task execution, risking task loss on worker crash.

### DON'T
```python
# Default: acks early (before execution)
@app.task
def critical_payment(payment_id):
    process_payment(payment_id)
```

**Issue**: If worker crashes during execution, task is lost (already acknowledged).

### DO
```python
@app.task(
    acks_late=True,
    reject_on_worker_lost=True
)
def critical_payment(payment_id):
    process_payment(payment_id)
```

### Why It Matters
- `acks_late=True`: Acknowledge only after successful completion
- `reject_on_worker_lost=True`: Requeue if worker crashes
- Ensures critical tasks aren't lost due to worker failures

---

## Mistake 6: Ignoring Result Expiration

### The Problem
Results accumulate in backend forever, consuming memory.

### DON'T
```python
app = Celery('tasks')
# No result_expires set - results never cleaned up
```

### DO
```python
app.conf.result_expires = 3600  # 1 hour

# Or per-task
@app.task(expires=1800)  # 30 minutes
def temp_task():
    return "result"

# Or ignore results entirely
@app.task(ignore_result=True)
def fire_and_forget():
    send_email()
```

### Why It Matters
Without expiration, Redis/database fills with old results, eventually causing memory exhaustion.

---

## Mistake 7: No Connection Pooling

### The Problem
Creating new connections per task is inefficient and can exhaust connection limits.

### DON'T
```python
@app.task
def query_database(query):
    # New connection every task
    conn = psycopg2.connect(
        host='localhost',
        database='mydb',
        user='user',
        password='password'
    )
    result = conn.execute(query)
    conn.close()
    return result
```

### DO
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Create engine once at module level
engine = create_engine(
    'postgresql://user:password@localhost/mydb',
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before use
)

@app.task
def query_database(query):
    # Uses connection from pool
    with engine.connect() as conn:
        result = conn.execute(query)
        return result.fetchall()
```

### Why It Matters
- Connection creation is expensive
- Connection pools reuse existing connections
- Prevents exhausting database connection limits

---

## Mistake 8: Not Routing Tasks to Appropriate Queues

### The Problem
All tasks in one queue means critical tasks wait behind slow bulk tasks.

### DON'T
```python
# All tasks go to default queue
@app.task
def critical_payment():
    pass

@app.task
def generate_monthly_report():  # Takes 30 minutes
    pass
```

**Issue**: Payment processing waits for report generation to complete.

### DO
```python
from kombu import Queue, Exchange

app.conf.task_queues = (
    Queue('critical', Exchange('critical'), routing_key='critical'),
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('bulk', Exchange('bulk'), routing_key='bulk'),
)

app.conf.task_routes = {
    'tasks.critical_payment': {'queue': 'critical'},
    'tasks.generate_monthly_report': {'queue': 'bulk'},
}

# Run dedicated workers
# celery -A app worker -Q critical --concurrency=4 --pool=prefork
# celery -A app worker -Q bulk --concurrency=2 --pool=prefork
```

### Why It Matters
- Isolates critical tasks from slow bulk operations
- Allows different concurrency/pool strategies per queue type
- Prevents head-of-line blocking

---

## Mistake 9: Not Validating Task Inputs

### The Problem
Accepting arbitrary inputs creates security vulnerabilities and runtime errors.

### DON'T
```python
@app.task
def process_order(order_id, amount, email):
    # No validation - trusts all inputs
    db.execute(f"UPDATE orders SET amount={amount} WHERE id={order_id}")
    send_email(email, "Order processed")
```

**Vulnerabilities**:
- SQL injection via `amount`
- Command injection via `email`
- Type errors (string passed as integer)

### DO
```python
from pydantic import BaseModel, EmailStr, Field

class OrderData(BaseModel):
    order_id: int = Field(gt=0)
    amount: float = Field(gt=0, le=1000000)
    email: EmailStr

@app.task
def process_order_validated(order_data: dict):
    # Validate and sanitize inputs
    validated = OrderData(**order_data)

    # Safe to use validated data
    db.execute(
        "UPDATE orders SET amount=? WHERE id=?",
        (validated.amount, validated.order_id)
    )
    send_email(validated.email, "Order processed")
```

### Why It Matters
- Prevents injection attacks
- Catches type errors early
- Provides clear error messages for invalid inputs

---

## Mistake 10: Exposing Flower Without Authentication

### The Problem
Flower exposes sensitive task data and worker controls without authentication.

### DON'T
```bash
# Exposes Flower on public IP without auth
celery -A app flower --address=0.0.0.0 --port=5555
```

**Risk**: Anyone can view task history, results, and control workers.

### DO
```bash
# Option 1: Basic authentication
celery -A app flower \
    --basic_auth=admin:strong_password \
    --address=127.0.0.1 \
    --port=5555

# Option 2: Behind authenticated reverse proxy
# nginx config with authentication
```

### Why It Matters
Flower shows:
- Task arguments (may contain sensitive data)
- Task results (may contain PII, credentials)
- Worker control (can shutdown workers, purge queues)

---

## Mistake 11: Hardcoding Credentials

### The Problem
Hardcoded secrets in code are exposed in version control and logs.

### DON'T
```python
app.conf.broker_url = 'redis://:hardcoded_password@localhost:6379/0'
API_KEY = 'sk-1234567890abcdef'

@app.task
def call_api():
    requests.get('https://api.example.com', headers={'Authorization': f'Bearer {API_KEY}'})
```

### DO
```python
import os

# Load from environment variables
app.conf.broker_url = os.environ['CELERY_BROKER_URL']

# Or use secrets manager
from secretmanager import get_secret

@app.task
def call_api():
    api_key = get_secret('external_api_key')
    requests.get('https://api.example.com', headers={'Authorization': f'Bearer {api_key}'})
```

### Why It Matters
- Secrets in code are exposed in git history
- Harder to rotate credentials
- Violates security best practices

---

## Mistake 12: No Retry Logic or Improper Retry

### The Problem
Tasks fail permanently on transient errors, or retry forever on permanent errors.

### DON'T
```python
# No retry - fails on transient errors
@app.task
def call_api():
    return requests.get('https://api.example.com/data').json()

# Retries forever - even on permanent errors
@app.task(bind=True, max_retries=None)
def process_data(self, data_id):
    try:
        return process(data_id)
    except Exception as exc:
        raise self.retry(exc=exc)  # Retries even on ValidationError!
```

### DO
```python
from celery.exceptions import Reject

@app.task(
    bind=True,
    max_retries=3,
    autoretry_for=(RequestException, TimeoutError),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
)
def call_api_with_retry(self):
    return requests.get('https://api.example.com/data', timeout=10).json()

@app.task(bind=True, max_retries=3)
def process_data(self, data_id):
    try:
        return process(data_id)
    except TemporaryError as exc:
        # Retry transient errors
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
    except ValidationError as exc:
        # Don't retry permanent errors
        raise Reject(exc, requeue=False)
```

### Why It Matters
- Transient errors (network issues) should retry with backoff
- Permanent errors (validation failures) should fail fast
- Infinite retries waste resources and delay detection

---

## Summary of Anti-Patterns

| Anti-Pattern | Impact | Solution |
|--------------|--------|----------|
| Pickle serialization | Security vulnerability | Use JSON |
| Non-idempotent tasks | Data corruption on retry | Design for idempotency |
| Missing time limits | Resource exhaustion | Set time_limit and soft_time_limit |
| Large results | Memory exhaustion | Store externally, return references |
| Early acknowledgment | Task loss on crash | Use acks_late=True |
| No result expiration | Memory leaks | Set result_expires |
| No connection pooling | Poor performance | Use connection pools |
| Single queue | Head-of-line blocking | Route to dedicated queues |
| No input validation | Security vulnerabilities | Validate with Pydantic |
| Exposed Flower | Information disclosure | Add authentication |
| Hardcoded credentials | Security risk | Use env vars or secrets manager |
| Poor retry logic | Reliability issues | Retry transient, reject permanent |
