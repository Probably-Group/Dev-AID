## 5. Core Patterns

### Pattern 1: Work Queue with Manual Acknowledgments

```python
# ✅ RELIABLE: Manual acknowledgments with error handling
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# Declare durable queue
channel.queue_declare(queue='tasks', durable=True)

# Set prefetch count to limit unacked messages
channel.basic_qos(prefetch_count=1)

def callback(ch, method, properties, body):
    try:
        print(f"Processing: {body}")
        process_task(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

channel.basic_consume(
    queue='tasks',
    on_message_callback=callback,
    auto_ack=False  # CRITICAL: Manual ack
)

channel.start_consuming()
```

---

### Pattern 2: Publisher Confirms for Delivery Guarantees

```python
# ✅ RELIABLE: Ensure messages are confirmed by broker
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# Enable publisher confirms
channel.confirm_delivery()

# Declare durable exchange and queue
channel.exchange_declare(exchange='orders', exchange_type='topic', durable=True)
channel.queue_declare(queue='order_processing', durable=True)
channel.queue_bind(exchange='orders', queue='order_processing', routing_key='order.created')

try:
    channel.basic_publish(
        exchange='orders',
        routing_key='order.created',
        body='{"order_id": 12345}',
        properties=pika.BasicProperties(
            delivery_mode=2,  # Persistent message
            content_type='application/json'
        ),
        mandatory=True
    )
    print("Message confirmed by broker")
except pika.exceptions.UnroutableError:
    print("Message could not be routed")
except pika.exceptions.NackError:
    print("Message was rejected by broker")
```

---

### Pattern 3: Dead Letter Exchange (DLX)

```python
# ✅ RELIABLE: Handle failed messages with DLX
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# Declare DLX
channel.exchange_declare(exchange='dlx', exchange_type='fanout', durable=True)
channel.queue_declare(queue='failed_messages', durable=True)
channel.queue_bind(exchange='dlx', queue='failed_messages')

# Declare main queue with DLX configuration
channel.queue_declare(
    queue='tasks',
    durable=True,
    arguments={
        'x-dead-letter-exchange': 'dlx',
        'x-message-ttl': 60000,  # 60 seconds
        'x-max-length': 10000    # Max queue length
    }
)

def callback(ch, method, properties, body):
    try:
        process_message(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Processing failed, sending to DLX: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

channel.basic_consume(queue='tasks', on_message_callback=callback, auto_ack=False)
```

---

### Pattern 4: Topic Exchange for Flexible Routing

```python
# ✅ SCALABLE: Topic-based routing for complex scenarios
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# Declare topic exchange
channel.exchange_declare(exchange='logs', exchange_type='topic', durable=True)

# Bind queues with different patterns
channel.queue_declare(queue='error_logs', durable=True)
channel.queue_bind(exchange='logs', queue='error_logs', routing_key='*.error')

channel.queue_declare(queue='db_logs', durable=True)
channel.queue_bind(exchange='logs', queue='db_logs', routing_key='db.*')

# Publish with routing keys
channel.basic_publish(
    exchange='logs',
    routing_key='app.error',
    body='Application error occurred',
    properties=pika.BasicProperties(delivery_mode=2)
)
```

**Routing Key Patterns**:
- `*` matches exactly one word
- `#` matches zero or more words
- Example: `user.*.created` matches `user.account.created`
- Example: `user.#` matches `user.created`, `user.account.updated`

---

### Pattern 5: Quorum Queues for High Availability

```python
# ✅ HA: Quorum queues with replication
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq-node-1'))
channel = connection.channel()

# Declare quorum queue (replicated across cluster)
channel.queue_declare(
    queue='ha_tasks',
    durable=True,
    arguments={
        'x-queue-type': 'quorum',
        'x-max-in-memory-length': 0,
        'x-delivery-limit': 5
    }
)

channel.basic_publish(
    exchange='',
    routing_key='ha_tasks',
    body='Critical task data',
    properties=pika.BasicProperties(delivery_mode=2)
)
```

**Quorum Queue Benefits**:
- Data replication across nodes (consensus-based)
- Automatic failover without message loss
- Poison message detection with delivery limits
- Better consistency than classic mirrored queues

---

