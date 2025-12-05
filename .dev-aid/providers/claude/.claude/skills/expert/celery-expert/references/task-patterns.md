# Celery Task Implementation Patterns

## Pattern 1: Task Definition Best Practices

```python
# COMPLETE TASK DEFINITION
from celery import Celery
from celery.exceptions import SoftTimeLimitExceeded
import logging

app = Celery('tasks', broker='redis://localhost:6379/0')
logger = logging.getLogger(__name__)

@app.task(
    bind=True,
    name='tasks.process_order',
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
    reject_on_worker_lost=True,
    time_limit=300,
    soft_time_limit=240,
    rate_limit='100/m',
)
def process_order(self, order_id: int):
    """Process order with proper error handling and retries"""
    try:
        logger.info(f"Processing order {order_id}", extra={'task_id': self.request.id})

        order = get_order(order_id)
        if order.status == 'processed':
            return {'order_id': order_id, 'status': 'already_processed'}

        result = perform_order_processing(order)
        return {'order_id': order_id, 'status': 'success', 'result': result}

    except SoftTimeLimitExceeded:
        cleanup_processing(order_id)
        raise
    except TemporaryError as exc:
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
    except PermanentError as exc:
        send_failure_notification(order_id, str(exc))
        raise
```

## Pattern 2: Workflow Patterns (Chains, Groups, Chords)

```python
from celery import chain, group, chord

# CHAIN: Sequential execution (A -> B -> C)
workflow = chain(
    fetch_data.s('https://api.example.com/data'),
    process_item.s(),
    send_notification.s()
)

# GROUP: Parallel execution
job = group(fetch_data.s(url) for url in urls)

# CHORD: Map-Reduce (parallel + callback)
workflow = chord(
    group(process_item.s(item) for item in items)
)(aggregate_results.s())
```

### Advanced Workflow Examples

```python
# Complex workflow: Fetch data, process in parallel, aggregate, notify
from celery import chain, group, chord

# Step 1: Fetch data from multiple sources in parallel
fetch_workflow = group(
    fetch_api_data.s('https://api1.example.com/data'),
    fetch_database_data.s(query='SELECT * FROM orders'),
    fetch_file_data.s('/path/to/file.csv')
)

# Step 2: Process each dataset
process_workflow = chord(fetch_workflow)(
    group(
        process_api_data.s(),
        process_db_data.s(),
        process_file_data.s()
    )
)

# Step 3: Aggregate and notify
full_workflow = chain(
    process_workflow,
    aggregate_all_results.s(),
    generate_report.s(),
    send_report_notification.s()
)

# Execute
result = full_workflow.apply_async()
```

## Pattern 3: Production Configuration

```python
from kombu import Exchange, Queue

app = Celery('myapp')
app.conf.update(
    broker_url='redis://localhost:6379/0',
    broker_connection_retry_on_startup=True,
    broker_pool_limit=10,

    result_backend='redis://localhost:6379/1',
    result_expires=3600,

    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],

    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_time_limit=300,
    task_soft_time_limit=240,

    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)
```

### Advanced Configuration with Multiple Queues

```python
from kombu import Exchange, Queue

app.conf.update(
    # Queue definitions
    task_queues=(
        Queue('critical', Exchange('critical'), routing_key='critical',
              queue_arguments={'x-max-priority': 10}),
        Queue('default', Exchange('default'), routing_key='default'),
        Queue('bulk', Exchange('bulk'), routing_key='bulk'),
        Queue('periodic', Exchange('periodic'), routing_key='periodic'),
    ),

    # Routing
    task_routes={
        'tasks.process_payment': {'queue': 'critical', 'priority': 10},
        'tasks.send_email': {'queue': 'default'},
        'tasks.generate_report': {'queue': 'bulk'},
        'tasks.cleanup_*': {'queue': 'periodic'},
    },

    # Dead letter queue
    task_reject_on_worker_lost=True,
    task_acks_late=True,
)
```

## Pattern 4: Retry Strategies & Error Handling

```python
from celery.exceptions import Reject

@app.task(
    bind=True,
    max_retries=5,
    autoretry_for=(RequestException,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
)
def call_external_api(self, url: str):
    """Auto-retry on RequestException with exponential backoff"""
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()
```

### Custom Retry Logic

```python
@app.task(bind=True, max_retries=3)
def custom_retry_task(self, data):
    """Custom retry with different strategies for different errors"""
    try:
        return process_data(data)
    except TemporaryError as exc:
        # Exponential backoff for temporary errors
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
    except RateLimitError as exc:
        # Fixed delay for rate limits
        raise self.retry(exc=exc, countdown=60)
    except ValidationError as exc:
        # Don't retry validation errors - permanent failure
        raise Reject(exc, requeue=False)
```

## Pattern 5: Celery Beat Scheduling

```python
from celery.schedules import crontab
from datetime import timedelta

app.conf.beat_schedule = {
    'cleanup-temp-files': {
        'task': 'tasks.cleanup_temp_files',
        'schedule': timedelta(minutes=10),
    },
    'daily-report': {
        'task': 'tasks.generate_daily_report',
        'schedule': crontab(hour=3, minute=0),
    },
    'business-hours-check': {
        'task': 'tasks.check_system_health',
        'schedule': crontab(hour='9-17', minute='*/15', day_of_week='1-5'),
    },
}
```

### Advanced Beat Patterns

```python
from celery.schedules import crontab, solar
from datetime import timedelta

app.conf.beat_schedule = {
    # Every 10 minutes
    'frequent-check': {
        'task': 'tasks.health_check',
        'schedule': timedelta(minutes=10),
    },

    # Every day at 3 AM
    'daily-backup': {
        'task': 'tasks.backup_database',
        'schedule': crontab(hour=3, minute=0),
    },

    # Every Monday at 9 AM
    'weekly-report': {
        'task': 'tasks.generate_weekly_report',
        'schedule': crontab(hour=9, minute=0, day_of_week=1),
    },

    # First day of month at midnight
    'monthly-cleanup': {
        'task': 'tasks.archive_old_data',
        'schedule': crontab(hour=0, minute=0, day_of_month=1),
    },

    # Solar schedule - sunset
    'evening-notification': {
        'task': 'tasks.send_evening_summary',
        'schedule': solar('sunset', -37.81, 144.96),  # Melbourne coordinates
    },
}
```

## Pattern 6: Task Locking (Prevent Duplicate Execution)

```python
from redis import Redis
from celery.exceptions import Reject

redis_client = Redis(host='localhost', port=6379, decode_responses=True)

@app.task(bind=True)
def locked_task(self, resource_id):
    """Ensure only one instance processes a resource"""
    lock_key = f'task_lock:{resource_id}'
    lock_acquired = redis_client.set(lock_key, self.request.id, nx=True, ex=300)

    if not lock_acquired:
        # Another task is already processing this resource
        raise Reject('Task already in progress', requeue=False)

    try:
        result = process_resource(resource_id)
        return result
    finally:
        # Release lock
        redis_client.delete(lock_key)
```

## Pattern 7: Task Callbacks and Error Handlers

```python
@app.task
def on_success_callback(result):
    """Called when task succeeds"""
    logger.info(f"Task succeeded with result: {result}")
    send_success_notification(result)

@app.task
def on_failure_callback(task_id, exc, traceback):
    """Called when task fails permanently"""
    logger.error(f"Task {task_id} failed: {exc}")
    send_alert(task_id, exc)

@app.task(
    bind=True,
    on_success=on_success_callback,
    on_failure=on_failure_callback
)
def important_task(self, data):
    """Task with callbacks"""
    return process_important_data(data)
```

## Key Takeaways

- **Comprehensive Task Definition**: Always include time limits, retry logic, and proper error handling
- **Workflow Orchestration**: Use chains, groups, and chords for complex multi-step processes
- **Production Configuration**: Set proper serialization, acks_late, and connection pooling
- **Retry Strategies**: Implement exponential backoff for temporary errors, reject permanent failures
- **Scheduling**: Use Celery Beat for periodic tasks with crontab or interval schedules
- **Task Locking**: Prevent duplicate execution with distributed locks
- **Callbacks**: Handle success and failure cases with dedicated callback tasks
