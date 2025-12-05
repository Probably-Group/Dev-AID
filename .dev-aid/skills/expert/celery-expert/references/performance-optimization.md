# Celery Performance Optimization

## Pattern 1: Task Chunking

```python
# Bad - Individual tasks for each item
for item_id in item_ids:  # 10,000 items = 10,000 tasks
    process_item.delay(item_id)

# Good - Process in batches
@app.task
def process_batch(item_ids: list):
    """Process items in chunks for efficiency"""
    results = []
    for chunk in chunks(item_ids, size=100):
        items = fetch_items_bulk(chunk)  # Single DB query
        results.extend([process(item) for item in items])
    return results

# Dispatch in chunks
for chunk in chunks(item_ids, size=100):
    process_batch.delay(chunk)  # 100 tasks instead of 10,000
```

## Pattern 2: Prefetch Tuning

```python
# Bad - Default prefetch for I/O-bound tasks
app.conf.worker_prefetch_multiplier = 4  # Too many reserved

# Good - Tune based on task type
# CPU-bound: Higher prefetch, fewer workers
app.conf.worker_prefetch_multiplier = 4
# celery -A app worker --concurrency=4

# I/O-bound: Lower prefetch, more workers
app.conf.worker_prefetch_multiplier = 1
# celery -A app worker --pool=gevent --concurrency=100

# Long tasks: Disable prefetch
app.conf.worker_prefetch_multiplier = 1
app.conf.task_acks_late = True
```

## Pattern 3: Result Backend Optimization

```python
# Bad - Storing results for fire-and-forget tasks
@app.task
def send_email(to, subject, body):
    mailer.send(to, subject, body)
    return {'sent': True}  # Stored in Redis unnecessarily

# Good - Ignore results when not needed
@app.task(ignore_result=True)
def send_email(to, subject, body):
    mailer.send(to, subject, body)

# Good - Set expiration for results you need
app.conf.result_expires = 3600  # 1 hour

# Good - Store minimal data, reference external storage
@app.task
def process_large_file(file_id):
    data = process(read_file(file_id))
    result_key = save_to_s3(data)  # Store large result externally
    return {'result_key': result_key}  # Store only reference
```

## Pattern 4: Connection Pooling

```python
# Bad - Creating new connections per task
@app.task
def query_database(query):
    conn = psycopg2.connect(...)  # New connection each time
    result = conn.execute(query)
    conn.close()
    return result

# Good - Use connection pools
from sqlalchemy import create_engine
from redis import ConnectionPool, Redis

# Initialize once at module level
db_engine = create_engine(
    'postgresql://user:pass@localhost/db',
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)
redis_pool = ConnectionPool(host='localhost', port=6379, max_connections=50)

@app.task
def query_database(query):
    with db_engine.connect() as conn:  # Uses pool
        return conn.execute(query).fetchall()

@app.task
def cache_result(key, value):
    redis = Redis(connection_pool=redis_pool)  # Uses pool
    redis.set(key, value)
```

## Pattern 5: Task Routing

```python
# Bad - All tasks in single queue
@app.task
def critical_payment(): pass

@app.task
def generate_report(): pass  # Blocks payment processing

# Good - Route to dedicated queues
from kombu import Queue, Exchange

app.conf.task_queues = (
    Queue('critical', Exchange('critical'), routing_key='critical'),
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('bulk', Exchange('bulk'), routing_key='bulk'),
)

app.conf.task_routes = {
    'tasks.critical_payment': {'queue': 'critical'},
    'tasks.generate_report': {'queue': 'bulk'},
}

# Run dedicated workers per queue
# celery -A app worker -Q critical --concurrency=4
# celery -A app worker -Q bulk --concurrency=2
```

## Key Takeaways

- **Batch Processing**: Reduce task overhead by processing items in chunks
- **Prefetch Tuning**: Match prefetch multiplier to task characteristics (CPU vs I/O)
- **Result Management**: Ignore results for fire-and-forget tasks, set expiration for others
- **Connection Pooling**: Reuse database and cache connections across tasks
- **Queue Routing**: Isolate critical tasks from bulk processing to prevent blocking
