# RabbitMQ Performance Optimization

## Overview

This guide covers advanced performance optimization techniques for RabbitMQ, including prefetch tuning, batching, connection pooling, lazy queues, and publisher confirms optimization.

---

## Pattern 1: Prefetch Count Tuning

```python
# BAD: Unlimited prefetch - consumer gets overwhelmed
channel.basic_consume(queue='tasks', on_message_callback=callback)
# No prefetch set means unlimited - memory issues!

# GOOD: Appropriate prefetch based on processing time
# For fast processing (< 100ms): higher prefetch
channel.basic_qos(prefetch_count=50)

# For slow processing (> 1s): lower prefetch
channel.basic_qos(prefetch_count=1)

# For balanced workloads
channel.basic_qos(prefetch_count=10)
```

**Tuning Guidelines**:
- Fast consumers (< 100ms): prefetch 20-50
- Medium consumers (100ms-1s): prefetch 5-20
- Slow consumers (> 1s): prefetch 1-5
- Monitor consumer utilization to adjust

---

## Pattern 2: Message Batching

```python
# BAD: Publishing one message at a time with confirms
for order in orders:
    channel.basic_publish(
        exchange='orders',
        routing_key='order.created',
        body=json.dumps(order),
        properties=pika.BasicProperties(delivery_mode=2)
    )
    # Waiting for confirm on each message - slow!

# GOOD: Batch publishing with bulk confirms
channel.confirm_delivery()

# Publish batch without waiting
for order in orders:
    channel.basic_publish(
        exchange='orders',
        routing_key='order.created',
        body=json.dumps(order),
        properties=pika.BasicProperties(delivery_mode=2)
    )

# Wait for all confirms at once
try:
    channel.get_waiting_message_count()  # Forces confirm flush
except pika.exceptions.NackError as e:
    # Handle rejected messages
    logger.error(f"Messages rejected: {e.messages}")
```

---

## Pattern 3: Connection Pooling

```python
# BAD: Creating new connection for each operation
def send_message(message):
    connection = pika.BlockingConnection(params)  # Expensive!
    channel = connection.channel()
    channel.basic_publish(...)
    connection.close()

# GOOD: Reuse connections with pooling
from queue import Queue
import threading

class ConnectionPool:
    def __init__(self, params, size=10):
        self.pool = Queue(maxsize=size)
        self.params = params
        for _ in range(size):
            conn = pika.BlockingConnection(params)
            self.pool.put(conn)

    def get_connection(self):
        return self.pool.get()

    def return_connection(self, conn):
        if conn.is_open:
            self.pool.put(conn)
        else:
            # Replace dead connection
            self.pool.put(pika.BlockingConnection(self.params))

    def publish(self, exchange, routing_key, body):
        conn = self.get_connection()
        try:
            channel = conn.channel()
            channel.basic_publish(
                exchange=exchange,
                routing_key=routing_key,
                body=body,
                properties=pika.BasicProperties(delivery_mode=2)
            )
        finally:
            self.return_connection(conn)
```

**Best Practices**:
- One connection per application/thread
- Multiple channels per connection (lightweight)
- Close channels after use
- Implement connection recovery
- Set appropriate heartbeat intervals

---

## Pattern 4: Lazy Queues for Large Backlogs

```python
# BAD: Classic queue with large backlog - memory pressure
channel.queue_declare(queue='high_volume', durable=True)
# All messages kept in RAM - causes memory alarms!

# GOOD: Lazy queue moves messages to disk
channel.queue_declare(
    queue='high_volume',
    durable=True,
    arguments={
        'x-queue-mode': 'lazy'  # Messages go to disk immediately
    }
)

# BETTER: Quorum queue with memory limit
channel.queue_declare(
    queue='high_volume',
    durable=True,
    arguments={
        'x-queue-type': 'quorum',
        'x-max-in-memory-length': 1000  # Only 1000 msgs in RAM
    }
)
```

**When to Use Lazy Queues**:
- Queue depth regularly exceeds 10,000 messages
- Consumers are slower than publishers
- Memory is constrained
- Message order isn't time-critical

---

## Pattern 5: Publisher Confirms Optimization

```python
# BAD: Synchronous confirms - blocking on each message
channel.confirm_delivery()
for msg in messages:
    try:
        channel.basic_publish(...)  # Blocks until confirmed
    except Exception:
        handle_failure()

# GOOD: Asynchronous confirms with callbacks
import pika

def on_confirm(frame):
    if isinstance(frame.method, pika.spec.Basic.Ack):
        logger.debug(f"Message {frame.method.delivery_tag} confirmed")
    else:
        logger.error(f"Message {frame.method.delivery_tag} rejected")

# Use SelectConnection for async
connection = pika.SelectConnection(
    params,
    on_open_callback=on_connected
)

def on_connected(connection):
    channel = connection.channel(on_open_callback=on_channel_open)

def on_channel_open(channel):
    channel.confirm_delivery(on_confirm)
    # Now publishes are non-blocking
    channel.basic_publish(...)
```

---

## Pattern 6: Efficient Serialization

```python
# BAD: Using JSON for large binary data
import json
channel.basic_publish(
    body=json.dumps({"image": base64.b64encode(image_data).decode()})
)

# GOOD: Use appropriate serialization
import msgpack

# For structured data - MessagePack (faster, smaller)
channel.basic_publish(
    body=msgpack.packb({"user_id": 123, "action": "click"}),
    properties=pika.BasicProperties(
        content_type='application/msgpack'
    )
)

# For binary data - direct bytes
channel.basic_publish(
    body=image_data,
    properties=pika.BasicProperties(
        content_type='application/octet-stream'
    )
)
```

---

## Pattern 7: Production Configuration

```ini
# /etc/rabbitmq/rabbitmq.conf
# ✅ PRODUCTION: Secure and optimized configuration

## Network and TLS
listeners.ssl.default = 5671
ssl_options.cacertfile = /path/to/ca_certificate.pem
ssl_options.certfile   = /path/to/server_certificate.pem
ssl_options.keyfile    = /path/to/server_key.pem
ssl_options.verify     = verify_peer
ssl_options.fail_if_no_peer_cert = true

## Memory and Disk Thresholds
vm_memory_high_watermark.relative = 0.5
disk_free_limit.absolute = 10GB

## Clustering
cluster_partition_handling = autoheal
cluster_name = production-cluster

## Performance
channel_max = 2048
heartbeat = 60
frame_max = 131072

## Management Plugin (disable in production or secure)
management.tcp.port = 15672
management.ssl.port = 15671
management.ssl.cacertfile = /path/to/ca.pem
management.ssl.certfile   = /path/to/cert.pem
management.ssl.keyfile    = /path/to/key.pem

## Logging
log.file.level = info
log.console = false
log.file = /var/log/rabbitmq/rabbit.log

## Resource Limits
total_memory_available_override_value = 8GB
```

**Critical Settings**:
- `vm_memory_high_watermark`: Prevent OOM (50% recommended)
- `disk_free_limit`: Prevent disk full (10GB+ recommended)
- `cluster_partition_handling`: autoheal or pause_minority
- TLS enabled for all connections

---

## Performance Monitoring

### Key Metrics to Track

1. **Queue Depth**
   - Alert threshold: > 10,000 messages
   - Prometheus: `rabbitmq_queue_messages{queue="name"}`

2. **Message Rate**
   - Publish rate vs consume rate
   - Prometheus: `rate(rabbitmq_queue_messages_published_total[1m])`

3. **Consumer Utilization**
   - Should be > 90% for optimal throughput
   - Prometheus: `rabbitmq_consumer_utilization`

4. **Memory Usage**
   - Alert when approaching watermark
   - Prometheus: `rabbitmq_node_mem_used`

5. **Connection/Channel Counts**
   - Monitor for leaks
   - Prometheus: `rabbitmq_connections`, `rabbitmq_channels`

---

## Troubleshooting Performance Issues

### High Queue Depth

**Symptoms**: Messages accumulating in queue

**Causes**:
- Consumers too slow
- Insufficient consumer count
- Processing errors causing rejects

**Solutions**:
- Scale consumers horizontally
- Optimize processing code
- Increase prefetch count
- Use lazy queues for memory relief

### Low Throughput

**Symptoms**: Publish/consume rates below expected

**Causes**:
- Small prefetch count
- Synchronous publisher confirms
- Connection/channel churn
- Slow disk I/O

**Solutions**:
- Tune prefetch count
- Use asynchronous confirms
- Implement connection pooling
- Use faster storage (SSD)

### Memory Alarms

**Symptoms**: Publishers blocked, memory alarm triggered

**Causes**:
- Queue backlog too large
- Classic queues with all messages in RAM
- Memory watermark too high

**Solutions**:
- Use lazy queues or quorum queues
- Reduce queue depth
- Lower memory watermark
- Add more RAM

### Connection Failures

**Symptoms**: Frequent disconnects, connection errors

**Causes**:
- Heartbeat timeout
- Network issues
- Resource exhaustion
- TLS handshake failures

**Solutions**:
- Increase heartbeat interval
- Check network stability
- Monitor file descriptors
- Verify TLS configuration

---

## Benchmarking

### Testing Publish Performance

```python
import pika
import time

def benchmark_publish(message_count=10000):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.confirm_delivery()

    message = b'x' * 1024  # 1KB message

    start = time.time()
    for _ in range(message_count):
        channel.basic_publish(
            exchange='',
            routing_key='benchmark',
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)
        )
    elapsed = time.time() - start

    rate = message_count / elapsed
    print(f"Publish rate: {rate:.0f} msg/s")

    connection.close()
```

### Testing Consume Performance

```python
def benchmark_consume(message_count=10000):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.basic_qos(prefetch_count=100)

    consumed = [0]
    start = time.time()

    def callback(ch, method, properties, body):
        consumed[0] += 1
        ch.basic_ack(delivery_tag=method.delivery_tag)

        if consumed[0] >= message_count:
            elapsed = time.time() - start
            rate = message_count / elapsed
            print(f"Consume rate: {rate:.0f} msg/s")
            ch.stop_consuming()

    channel.basic_consume(queue='benchmark', on_message_callback=callback)
    channel.start_consuming()
```

---

## Performance Checklist

Before deploying to production:

- [ ] Prefetch count tuned for workload
- [ ] Publisher confirms enabled
- [ ] Connection pooling implemented
- [ ] Lazy/quorum queues for high volume
- [ ] Memory watermark configured (50%)
- [ ] Disk space monitoring enabled
- [ ] Message serialization optimized
- [ ] Heartbeat interval appropriate
- [ ] Performance benchmarks completed
- [ ] Monitoring and alerting configured
