# RabbitMQ Anti-Patterns and Common Mistakes

## Overview

This guide covers common mistakes, anti-patterns, and pitfalls to avoid when working with RabbitMQ. Learn from these examples to build more reliable and maintainable message broker systems.

---

## Mistake 1: Using Auto-Acknowledgments

### ❌ Problem

```python
# DON'T: Auto-ack causes message loss on crash
channel.basic_consume(
    queue='tasks',
    on_message_callback=callback,
    auto_ack=True  # DANGEROUS!
)

def callback(ch, method, properties, body):
    # If this crashes, message is already acked and lost!
    process_task(body)
```

### Why It's Wrong

- Message is acknowledged before processing starts
- If consumer crashes during processing, message is lost forever
- No way to retry failed messages
- Violates reliability guarantees

### ✅ Solution

```python
# DO: Manual acknowledgments
channel.basic_consume(
    queue='tasks',
    on_message_callback=callback,
    auto_ack=False  # Manual ack
)

def callback(ch, method, properties, body):
    try:
        process_task(body)
        # Only ack on success
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        # Reject and send to DLX
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
```

---

## Mistake 2: Non-Durable Queues/Exchanges

### ❌ Problem

```python
# DON'T: Queues disappear on broker restart
channel.queue_declare(queue='tasks')
channel.exchange_declare(exchange='orders')

# If RabbitMQ restarts, all queues and messages are LOST!
```

### Why It's Wrong

- Queues and exchanges are in-memory only
- Broker restart causes total data loss
- No persistence for critical business data
- Production outages lose customer data

### ✅ Solution

```python
# DO: Durable queues survive restarts
channel.queue_declare(queue='tasks', durable=True)
channel.exchange_declare(exchange='orders', exchange_type='topic', durable=True)

# Also set messages as persistent
channel.basic_publish(
    exchange='orders',
    routing_key='order.created',
    body='order data',
    properties=pika.BasicProperties(
        delivery_mode=2  # Persistent
    )
)
```

---

## Mistake 3: Unlimited Prefetch Count

### ❌ Problem

```python
# DON'T: Consumer gets all messages at once
# (No prefetch limit set)
channel.basic_consume(queue='tasks', on_message_callback=callback)

# Consumer receives ALL unacked messages
# - Memory overflow
# - Unfair distribution
# - Consumer crashes from overload
```

### Why It's Wrong

- Consumer memory explodes with large queues
- One fast consumer gets all messages (unfair)
- No backpressure mechanism
- Difficult to scale consumers

### ✅ Solution

```python
# DO: Limit unacknowledged messages
channel.basic_qos(prefetch_count=10)
channel.basic_consume(queue='tasks', on_message_callback=callback)

# Consumer only gets 10 messages at a time
# Fair distribution across multiple consumers
# Memory usage controlled
```

**Tuning Guide**:
- Fast processing (< 100ms): prefetch 20-50
- Medium processing (100ms-1s): prefetch 5-20
- Slow processing (> 1s): prefetch 1-5

---

## Mistake 4: No Dead Letter Exchange

### ❌ Problem

```python
# DON'T: Failed messages get requeued infinitely
def callback(ch, method, properties, body):
    try:
        process_message(body)
    except Exception:
        # Requeue forever - message loops infinitely!
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
```

### Why It's Wrong

- Poison messages loop forever
- Consumes resources processing same bad message
- Blocks queue with unprocessable messages
- No visibility into failed messages

### ✅ Solution

```python
# DO: Configure DLX for failed messages
channel.exchange_declare(exchange='dlx', exchange_type='fanout', durable=True)
channel.queue_declare(queue='failed_messages', durable=True)
channel.queue_bind(exchange='dlx', queue='failed_messages')

channel.queue_declare(
    queue='tasks',
    durable=True,
    arguments={
        'x-dead-letter-exchange': 'dlx',
        'x-message-ttl': 60000,  # 60 seconds max
        'x-max-length': 10000    # Max queue length
    }
)

def callback(ch, method, properties, body):
    try:
        process_message(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        # Send to DLX, don't requeue
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
```

---

## Mistake 5: Classic Mirrored Queues Instead of Quorum

### ❌ Problem

```python
# DON'T: Classic mirrored queues (deprecated)
channel.queue_declare(
    queue='tasks',
    arguments={'x-ha-policy': 'all'}
)

# Classic mirrored queues:
# - Deprecated in RabbitMQ 3.8+
# - Potential data loss on network partitions
# - No poison message detection
# - Inconsistent in split-brain scenarios
```

### Why It's Wrong

- Legacy technology being phased out
- Weaker consistency guarantees
- No built-in poison message handling
- More prone to split-brain issues

### ✅ Solution

```python
# DO: Use quorum queues for HA
channel.queue_declare(
    queue='tasks',
    durable=True,
    arguments={
        'x-queue-type': 'quorum',
        'x-delivery-limit': 5,  # Poison message detection
        'x-max-in-memory-length': 1000
    }
)

# Quorum queues provide:
# - Strong consistency (Raft consensus)
# - Automatic poison message handling
# - Better split-brain handling
# - Recommended for production HA
```

---

## Mistake 6: Ignoring Connection Failures

### ❌ Problem

```python
# DON'T: No connection recovery
connection = pika.BlockingConnection(params)
channel = connection.channel()

# Connection drops = application crashes
# No retry logic
# No exponential backoff
```

### Why It's Wrong

- Network issues cause application failure
- No graceful degradation
- Cascading failures in distributed systems
- Poor user experience

### ✅ Solution

```python
# DO: Implement retry logic with exponential backoff
import time
import logging

def create_connection(params, max_retries=5):
    """Create connection with retry logic"""
    retries = 0
    while retries < max_retries:
        try:
            connection = pika.BlockingConnection(params)
            logging.info("Connected to RabbitMQ")
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            retries += 1
            delay = min(2 ** retries, 60)  # Exponential backoff, max 60s
            logging.warning(f"Connection failed (attempt {retries}/{max_retries}), "
                          f"retrying in {delay}s: {e}")
            if retries < max_retries:
                time.sleep(delay)
            else:
                raise Exception(f"Failed to connect after {max_retries} attempts")

# Usage
connection = create_connection(params)
```

---

## Mistake 7: Not Monitoring Queue Depth

### ❌ Problem

```python
# DON'T: Ignore queue buildup
# No alerts when queue depth grows
# No max queue length
# Memory exhaustion inevitable
```

### Why It's Wrong

- Memory alarms triggered unexpectedly
- Publishers blocked when memory full
- Consumers can't keep up (silent failure)
- System instability

### ✅ Solution

```python
# DO: Set max queue length
channel.queue_declare(
    queue='tasks',
    durable=True,
    arguments={
        'x-max-length': 50000,  # Drop old messages after 50k
        'x-overflow': 'reject-publish'  # Or 'drop-head'
    }
)

# Monitor with Prometheus
# Alert when: rabbitmq_queue_messages{queue="tasks"} > 10000

# Set up alerting
import requests

def check_queue_depth(queue_name, threshold=10000):
    """Alert on high queue depth"""
    response = requests.get(
        f'http://localhost:15672/api/queues/%2f/{queue_name}',
        auth=('admin', 'password')
    )
    queue_info = response.json()
    depth = queue_info.get('messages', 0)

    if depth > threshold:
        send_alert(f"Queue {queue_name} depth: {depth} (threshold: {threshold})")
```

---

## Mistake 8: Hardcoded Credentials

### ❌ Problem

```python
# DON'T: Hardcode credentials in code
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='rabbitmq.prod.example.com',
        credentials=pika.PlainCredentials('admin', 'password123')
    )
)

# Credentials in version control
# Security breach waiting to happen
# Difficult to rotate credentials
```

### Why It's Wrong

- Credentials exposed in source code
- Committed to Git (permanent record)
- Same credentials across environments
- Security audit failure

### ✅ Solution

```python
# DO: Use environment variables or secrets manager
import os

credentials = pika.PlainCredentials(
    os.environ['RABBITMQ_USER'],
    os.environ['RABBITMQ_PASSWORD']
)

parameters = pika.ConnectionParameters(
    host=os.environ['RABBITMQ_HOST'],
    virtual_host=os.environ.get('RABBITMQ_VHOST', '/'),
    credentials=credentials
)

# Or use secrets manager (Vault, AWS Secrets Manager, etc.)
```

---

## Mistake 9: Not Using Publisher Confirms

### ❌ Problem

```python
# DON'T: Publish without confirms
channel.basic_publish(
    exchange='orders',
    routing_key='order.created',
    body='critical order data'
)

# No guarantee message was received
# Silent message loss possible
# Network failures undetected
```

### Why It's Wrong

- Message may never reach broker
- No delivery guarantee
- Silent failures
- Data loss in production

### ✅ Solution

```python
# DO: Enable publisher confirms
channel.confirm_delivery()

try:
    channel.basic_publish(
        exchange='orders',
        routing_key='order.created',
        body='critical order data',
        properties=pika.BasicProperties(
            delivery_mode=2,  # Persistent
            mandatory=True    # Return if unroutable
        )
    )
    logging.info("Message confirmed by broker")
except pika.exceptions.UnroutableError:
    logging.error("Message could not be routed")
    # Handle unroutable message
except pika.exceptions.NackError:
    logging.error("Message rejected by broker")
    # Handle rejection
```

---

## Mistake 10: Single-Node Production Deployments

### ❌ Problem

```bash
# DON'T: Single RabbitMQ node in production
# - No high availability
# - Single point of failure
# - Maintenance = downtime
```

### Why It's Wrong

- Broker restart = application downtime
- Hardware failure = complete outage
- No rolling updates possible
- Poor production reliability

### ✅ Solution

```bash
# DO: Deploy 3+ node cluster with quorum queues
# Odd number of nodes (3, 5, 7)
# Load balancer in front
# Quorum queues for HA

# Example 3-node cluster setup
rabbitmqctl join_cluster rabbit@node1
rabbitmqctl set_policy ha-all ".*" '{"ha-mode":"all","ha-sync-mode":"automatic"}'

# Use quorum queues
channel.queue_declare(
    queue='critical_tasks',
    durable=True,
    arguments={'x-queue-type': 'quorum'}
)
```

---

## Mistake 11: Not Setting Message TTL

### ❌ Problem

```python
# DON'T: Infinite message lifetime
channel.queue_declare(queue='tasks', durable=True)

# Messages never expire
# Stale messages accumulate
# Queue grows indefinitely
```

### Why It's Wrong

- Old/irrelevant messages consume resources
- Queue depth grows unbounded
- Processing outdated data
- Memory pressure

### ✅ Solution

```python
# DO: Set appropriate TTL
channel.queue_declare(
    queue='tasks',
    durable=True,
    arguments={
        'x-message-ttl': 3600000,  # 1 hour in milliseconds
        'x-dead-letter-exchange': 'dlx'  # Expired -> DLX
    }
)

# Or per-message TTL
channel.basic_publish(
    exchange='',
    routing_key='tasks',
    body='time-sensitive data',
    properties=pika.BasicProperties(
        delivery_mode=2,
        expiration='60000'  # 60 seconds
    )
)
```

---

## Mistake 12: Creating/Deleting Resources in Consumers

### ❌ Problem

```python
# DON'T: Declare queues in hot path
def callback(ch, method, properties, body):
    # This runs for EVERY message!
    ch.queue_declare(queue='temp_queue')  # SLOW!
    ch.exchange_declare(exchange='temp_exchange')  # SLOW!

    process_message(body)
    ch.basic_ack(delivery_tag=method.delivery_tag)
```

### Why It's Wrong

- Severe performance degradation
- Network round-trip for every message
- Creates unnecessary load on broker
- Slows message processing dramatically

### ✅ Solution

```python
# DO: Declare resources once during setup
def setup():
    """One-time setup"""
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    # Declare resources ONCE
    channel.queue_declare(queue='tasks', durable=True)
    channel.exchange_declare(exchange='orders', exchange_type='topic', durable=True)
    channel.queue_bind(exchange='orders', queue='tasks', routing_key='order.#')

    return connection, channel

# Then consume
connection, channel = setup()
channel.basic_consume(queue='tasks', on_message_callback=callback)
```

---

## Mistake 13: Not Using Connection Pooling

### ❌ Problem

```python
# DON'T: Create connection for each operation
def send_message(message):
    connection = pika.BlockingConnection(params)  # Expensive!
    channel = connection.channel()
    channel.basic_publish(...)
    connection.close()  # Wasteful!

# Called 1000 times = 1000 connections opened/closed
for msg in messages:
    send_message(msg)  # VERY SLOW!
```

### Why It's Wrong

- Connection creation is expensive (TCP, TLS, auth)
- Massive overhead for each message
- Connection limit exhaustion
- Poor throughput

### ✅ Solution

```python
# DO: Reuse connections with pooling
class ConnectionPool:
    def __init__(self, params, size=10):
        self.pool = []
        for _ in range(size):
            conn = pika.BlockingConnection(params)
            self.pool.append(conn)
        self.available = Queue(maxsize=size)
        for conn in self.pool:
            self.available.put(conn)

    def get(self):
        return self.available.get()

    def release(self, conn):
        self.available.put(conn)

# Usage
pool = ConnectionPool(params, size=5)
for msg in messages:
    conn = pool.get()
    try:
        channel = conn.channel()
        channel.basic_publish(...)
    finally:
        pool.release(conn)
```

---

## Mistake 14: Ignoring Memory/Disk Alarms

### ❌ Problem

```ini
# DON'T: Default thresholds too high
# vm_memory_high_watermark.relative = 0.4 (default)

# Publishers blocked when memory hits 40%
# Too late - system already under pressure
# Cascading failures likely
```

### Why It's Wrong

- Alarm triggers too late
- System already degraded when alarm fires
- Publishers blocked, causing upstream issues
- Difficult recovery

### ✅ Solution

```ini
# DO: Set conservative thresholds
# /etc/rabbitmq/rabbitmq.conf

vm_memory_high_watermark.relative = 0.5  # 50% threshold
disk_free_limit.absolute = 10GB  # Min 10GB free

# Monitor proactively
# Alert at 70% memory usage (before alarm)
# Alert at < 20GB disk space

# Set up paging to disk
vm_memory_high_watermark_paging_ratio = 0.75
```

---

## Mistake 15: Using Default Exchange Incorrectly

### ❌ Problem

```python
# DON'T: Rely on default exchange for complex routing
channel.basic_publish(
    exchange='',  # Default exchange
    routing_key='some.complex.pattern',
    body='message'
)

# Default exchange only does direct routing by queue name
# Can't do topic routing
# Can't do fanout
# Limited flexibility
```

### Why It's Wrong

- Default exchange is direct-only
- Routing key must match queue name exactly
- No pattern matching
- Not suitable for pub/sub

### ✅ Solution

```python
# DO: Use explicit exchange with appropriate type
channel.exchange_declare(
    exchange='events',
    exchange_type='topic',  # Flexible routing
    durable=True
)

channel.queue_bind(
    exchange='events',
    queue='order_processor',
    routing_key='order.#'  # Pattern matching
)

channel.basic_publish(
    exchange='events',
    routing_key='order.created',
    body='order data'
)
```

---

## Anti-Pattern Summary

### Top 5 Most Critical

1. **Auto-Ack** - Causes message loss
2. **No Durability** - Data loss on restart
3. **No DLX** - Poison messages loop forever
4. **Single Node** - No high availability
5. **No Publisher Confirms** - Silent message loss

### Quick Checklist

Before deploying to production, verify:

- [ ] `auto_ack=False` everywhere
- [ ] Durable queues and exchanges
- [ ] Dead letter exchange configured
- [ ] Prefetch count set appropriately
- [ ] Publisher confirms enabled
- [ ] Multi-node cluster (3+ nodes)
- [ ] Quorum queues for critical data
- [ ] Connection retry logic implemented
- [ ] Credentials in secrets manager
- [ ] Queue depth monitoring enabled
- [ ] Memory/disk alarms configured
- [ ] TLS enabled for all connections

### Recovery Actions

If you find these anti-patterns in your code:

1. **Add tests first** - Verify current behavior
2. **Fix incrementally** - One anti-pattern at a time
3. **Test thoroughly** - Unit + integration tests
4. **Deploy carefully** - Blue/green or canary
5. **Monitor closely** - Watch for issues post-deployment

---

## Additional Resources

- See `performance-optimization.md` for performance best practices
- See `security-examples.md` for security patterns
- See `clustering-guide.md` for HA architecture
- See `testing-patterns.md` for test strategies
