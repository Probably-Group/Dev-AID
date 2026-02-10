---
name: rabbitmq-expert
version: 2.0.0
description: "RabbitMQ message broker patterns with exchange topologies, queue configuration, dead letter handling, and clustering for high availability. Use when designing AMQP exchange/queue architectures, configuring RabbitMQ clustering, implementing pub/sub messaging, or troubleshooting message routing. Do NOT use for Kafka, Redis pub/sub, or NATS messaging systems."
risk_level: HIGH
---

# RabbitMQ Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-502: Message Deserialization**
- NEVER: Deserialize pickled/arbitrary format messages
- ALWAYS: JSON with schema validation, reject unknown message types

**CWE-306: Missing Authentication**
- NEVER: Default guest/guest credentials in production
- ALWAYS: Strong credentials, TLS for connections, vhost isolation

**CWE-285: Queue Permissions**
- NEVER: Single user with full permissions
- ALWAYS: Separate users per service, minimum required permissions

### 0.3 Risk Level: HIGH

**Verification requirements for HIGH risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 Message Validation (CWE-20)

**Principle:** Validate all incoming messages. Never trust message content.

```python
# ❌ WRONG - No message validation
def callback(ch, method, properties, body):
    data = json.loads(body)
    process_order(data['order_id'], data['amount'])  # Trusting raw input!
    ch.basic_ack(delivery_tag=method.delivery_tag)

# ✅ CORRECT - Validate with Pydantic
from pydantic import BaseModel, Field, ValidationError

class OrderMessage(BaseModel):
    order_id: str = Field(pattern=r'^[A-Z0-9]{8,32}$')
    amount: float = Field(gt=0, le=1000000)
    user_id: str

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        msg = OrderMessage(**data)
        process_order(msg.order_id, msg.amount)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except (json.JSONDecodeError, ValidationError) as e:
        logger.warning(f"Invalid message: {e}")
        # Send to dead letter queue
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
```

### 1.2 Connection Security (CWE-319)

**Principle:** Always use TLS. Never expose credentials.

```python
# ❌ WRONG - No TLS, hardcoded credentials
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='rabbitmq.example.com',
        credentials=pika.PlainCredentials('admin', 'password123')
    )
)

# ✅ CORRECT - TLS with credentials from environment
import ssl
import os

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=os.environ['RABBITMQ_HOST'],
        port=5671,  # TLS port
        credentials=pika.PlainCredentials(
            os.environ['RABBITMQ_USER'],
            os.environ['RABBITMQ_PASSWORD']
        ),
        ssl_options=pika.SSLOptions(ssl_context),
        heartbeat=600,
        blocked_connection_timeout=300,
    )
)
```

### 1.3 Acknowledgment Safety (CWE-400)

**Principle:** Always ack/nack messages. Never lose messages silently.

```python
# ❌ WRONG - Auto-ack, message lost on crash
channel.basic_consume(queue='orders', on_message_callback=callback, auto_ack=True)

# ❌ WRONG - No error handling, ack before processing
def callback(ch, method, properties, body):
    ch.basic_ack(delivery_tag=method.delivery_tag)  # Ack before process!
    process(body)  # If this crashes, message lost

# ✅ CORRECT - Manual ack after successful processing
channel.basic_consume(queue='orders', on_message_callback=callback, auto_ack=False)

def callback(ch, method, properties, body):
    try:
        process(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except RecoverableError:
        # Requeue for retry
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    except FatalError:
        # Dead letter queue
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
```

### 1.4 Secrets ≠ Code (CWE-798)

**Principle:** Never hardcode credentials. Use environment or vault.

### 1.5 Queue Durability (CWE-636)

**Principle:** Use durable queues and persistent messages for critical data.

### 1.6 Defense in Depth

**Principle:** Dead letter queues, message TTL, and consumer limits.

---

## 2. Version Requirements

**ALWAYS use these minimum versions:**

```
# Python
pika>=1.3.0
aio-pika>=9.4.0
pydantic>=2.6.0

# Node.js
amqplib>=0.10.0

# Go
github.com/rabbitmq/amqp091-go v1.9.0
```

---

## 3. Code Patterns

### 3.1 WHEN setting up RabbitMQ connection (Python)

```python
import pika
import ssl
import os
from contextlib import contextmanager

class RabbitMQConfig:
    def __init__(self):
        self.host = os.environ['RABBITMQ_HOST']
        self.port = int(os.environ.get('RABBITMQ_PORT', 5671))
        self.user = os.environ['RABBITMQ_USER']
        self.password = os.environ['RABBITMQ_PASSWORD']
        self.vhost = os.environ.get('RABBITMQ_VHOST', '/')

    def get_connection_params(self) -> pika.ConnectionParameters:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = True
        ssl_context.verify_mode = ssl.CERT_REQUIRED

        return pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            virtual_host=self.vhost,
            credentials=pika.PlainCredentials(self.user, self.password),
            ssl_options=pika.SSLOptions(ssl_context),
            heartbeat=600,
            blocked_connection_timeout=300,
            connection_attempts=3,
            retry_delay=5,
        )

@contextmanager
def get_rabbitmq_channel():
    """Context manager for RabbitMQ connection."""
    config = RabbitMQConfig()
    connection = pika.BlockingConnection(config.get_connection_params())
    try:
        channel = connection.channel()
        channel.basic_qos(prefetch_count=10)  # Limit unacked messages
        yield channel
    finally:
        connection.close()
```

### 3.2 WHEN declaring queues with dead letter handling

```python
def setup_queues(channel):
    """Set up queues with dead letter exchange."""
    # Dead letter exchange
    channel.exchange_declare(
        exchange='dlx',
        exchange_type='direct',
        durable=True,
    )

    # Dead letter queue
    channel.queue_declare(
        queue='orders.dlq',
        durable=True,
        arguments={
            'x-message-ttl': 86400000,  # 24 hours
        },
    )
    channel.queue_bind(
        queue='orders.dlq',
        exchange='dlx',
        routing_key='orders',
    )

    # Main queue with DLX
    channel.queue_declare(
        queue='orders',
        durable=True,
        arguments={
            'x-dead-letter-exchange': 'dlx',
            'x-dead-letter-routing-key': 'orders',
            'x-message-ttl': 3600000,  # 1 hour
            'x-max-length': 100000,    # Max queue size
        },
    )
```

### 3.3 WHEN publishing messages

```python
from pydantic import BaseModel
import json
import uuid

class OrderEvent(BaseModel):
    order_id: str
    user_id: str
    amount: float
    timestamp: str

def publish_order(channel, order: OrderEvent):
    """Publish order with persistent delivery."""
    channel.basic_publish(
        exchange='',
        routing_key='orders',
        body=order.model_dump_json(),
        properties=pika.BasicProperties(
            delivery_mode=2,  # Persistent
            content_type='application/json',
            message_id=str(uuid.uuid4()),
            timestamp=int(time.time()),
            headers={
                'version': '1.0',
                'source': 'order-service',
            },
        ),
        mandatory=True,  # Return if unroutable
    )

def confirm_publish(channel):
    """Enable publisher confirms for reliability."""
    channel.confirm_delivery()

    try:
        publish_order(channel, order)
    except pika.exceptions.UnroutableError:
        logger.error("Message was returned - no queue bound")
        raise
```

### 3.4 WHEN consuming messages with retry logic

```python
from pydantic import BaseModel, ValidationError
import json

class OrderMessage(BaseModel):
    order_id: str
    user_id: str
    amount: float

class MessageConsumer:
    def __init__(self, channel, max_retries: int = 3):
        self.channel = channel
        self.max_retries = max_retries

    def process_message(self, ch, method, properties, body):
        """Process message with retry tracking."""
        retry_count = (properties.headers or {}).get('x-retry-count', 0)

        try:
            # Parse and validate
            data = json.loads(body)
            msg = OrderMessage(**data)

            # Process
            self._handle_order(msg)

            # Acknowledge success
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except json.JSONDecodeError:
            logger.error("Invalid JSON, sending to DLQ")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        except RecoverableError as e:
            if retry_count < self.max_retries:
                logger.warning(f"Retry {retry_count + 1}/{self.max_retries}")
                self._republish_with_retry(ch, body, properties, retry_count + 1)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                logger.error("Max retries exceeded, sending to DLQ")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def _republish_with_retry(self, ch, body, properties, retry_count):
        """Republish with incremented retry count."""
        headers = dict(properties.headers or {})
        headers['x-retry-count'] = retry_count

        ch.basic_publish(
            exchange='',
            routing_key='orders',
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2,
                headers=headers,
            ),
        )

    def _handle_order(self, order: OrderMessage):
        """Business logic here."""
        pass
```

### 3.5 WHEN using async with aio-pika

```python
import aio_pika
import ssl
import os
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_rabbitmq_connection():
    """Async context manager for RabbitMQ."""
    ssl_context = ssl.create_default_context()

    connection = await aio_pika.connect_robust(
        host=os.environ['RABBITMQ_HOST'],
        port=5671,
        login=os.environ['RABBITMQ_USER'],
        password=os.environ['RABBITMQ_PASSWORD'],
        ssl=True,
        ssl_context=ssl_context,
    )
    try:
        yield connection
    finally:
        await connection.close()

async def consume_orders():
    """Async consumer with QoS."""
    async with get_rabbitmq_connection() as connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)

        queue = await channel.declare_queue('orders', durable=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    try:
                        data = json.loads(message.body)
                        order = OrderMessage(**data)
                        await process_order(order)
                    except Exception as e:
                        logger.error(f"Processing failed: {e}")
                        raise  # Will nack and requeue
```

---

## 4. Anti-Patterns

**NEVER:**
- Use auto_ack=True for important messages
- Acknowledge before processing completes
- Hardcode credentials in connection strings
- Skip TLS in production
- Ignore dead letter queues
- Process messages without validation
- Use unbounded queues (set x-max-length)

---

## 5. Testing

**ALWAYS write integration tests:**

```python
import pytest
from testcontainers.rabbitmq import RabbitMqContainer

@pytest.fixture(scope="session")
def rabbitmq_container():
    with RabbitMqContainer("rabbitmq:3.12-management") as rabbitmq:
        yield rabbitmq

def test_message_validation(rabbitmq_container):
    """Verify invalid messages are rejected."""
    # Publish invalid message
    channel.basic_publish(
        exchange='',
        routing_key='orders',
        body=json.dumps({'invalid': 'data'}),
    )

    # Should end up in DLQ
    time.sleep(1)
    method, _, body = channel.basic_get('orders.dlq')
    assert method is not None

def test_retry_logic(rabbitmq_container):
    """Verify retry count increments."""
    # Simulate failure
    with mock.patch('handler.process_order', side_effect=RecoverableError):
        # Consume and verify retry header
        pass

def test_dlq_on_fatal_error(rabbitmq_container):
    """Verify fatal errors go to DLQ."""
    pass
```

---

## 6. Pre-Generation Checklist

**BEFORE generating any RabbitMQ code:**

- [ ] TLS enabled for all connections
- [ ] Credentials from environment variables
- [ ] Manual acknowledgment (auto_ack=False)
- [ ] Dead letter exchange configured
- [ ] Message validation with Pydantic
- [ ] Durable queues for persistent data
- [ ] Persistent message delivery (delivery_mode=2)
- [ ] QoS/prefetch limit set
- [ ] Retry logic with max retries
- [ ] Publisher confirms for critical messages

---

**Performance**: Quality over speed. Verify all code examples compile. Never skip security checks. See `template-references/performance-notes.md` for full guidelines.