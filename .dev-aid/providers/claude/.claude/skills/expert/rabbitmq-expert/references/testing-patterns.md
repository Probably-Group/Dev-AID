# RabbitMQ Testing Patterns

## Overview

Comprehensive testing strategies for RabbitMQ applications, including unit tests with mocks, integration tests with real brokers, and performance benchmarks.

---

## Unit Testing with Mocks

### Basic Mock Setup

```python
# tests/test_publisher.py
import pytest
from unittest.mock import MagicMock, patch
import pika

class TestMessagePublisher:
    """Unit tests for message publishing"""

    @pytest.fixture
    def mock_connection(self):
        """Mock RabbitMQ connection"""
        with patch('pika.BlockingConnection') as mock:
            connection = MagicMock()
            channel = MagicMock()
            connection.channel.return_value = channel
            mock.return_value = connection
            yield mock, connection, channel

    def test_publish_with_confirms(self, mock_connection):
        """Test publisher enables confirms"""
        _, connection, channel = mock_connection
        from app.publisher import OrderPublisher

        publisher = OrderPublisher()
        publisher.publish({"order_id": 123})

        channel.confirm_delivery.assert_called_once()
        channel.basic_publish.assert_called_once()

    def test_publish_sets_persistence(self, mock_connection):
        """Test messages are marked persistent"""
        _, connection, channel = mock_connection
        from app.publisher import OrderPublisher

        publisher = OrderPublisher()
        publisher.publish({"order_id": 123})

        call_args = channel.basic_publish.call_args
        props = call_args.kwargs.get('properties') or call_args[1].get('properties')
        assert props.delivery_mode == 2  # Persistent

    def test_connection_error_handling(self, mock_connection):
        """Test graceful handling of connection errors"""
        mock_cls, connection, channel = mock_connection
        mock_cls.side_effect = pika.exceptions.AMQPConnectionError()

        from app.publisher import OrderPublisher

        with pytest.raises(ConnectionError):
            publisher = OrderPublisher()
```

---

### Consumer Mock Testing

```python
# tests/test_consumer.py
import pytest
import pika
import json
from unittest.mock import MagicMock

class TestOrderConsumer:
    """Test order message processing with RabbitMQ"""

    @pytest.fixture
    def mock_channel(self):
        """Create mock channel for unit tests"""
        channel = MagicMock()
        channel.basic_qos = MagicMock()
        channel.basic_consume = MagicMock()
        channel.basic_ack = MagicMock()
        channel.basic_nack = MagicMock()
        return channel

    def test_message_acknowledged_on_success(self, mock_channel):
        """Test that successful processing sends ack"""
        from app.consumers import OrderConsumer

        consumer = OrderConsumer(mock_channel)
        message = json.dumps({"order_id": 123, "status": "pending"})

        # Create mock method with delivery tag
        method = MagicMock()
        method.delivery_tag = 1

        # Process message
        consumer.process_message(mock_channel, method, None, message.encode())

        # Verify ack was called
        mock_channel.basic_ack.assert_called_once_with(delivery_tag=1)
        mock_channel.basic_nack.assert_not_called()

    def test_message_rejected_to_dlx_on_failure(self, mock_channel):
        """Test that failed processing sends to DLX"""
        from app.consumers import OrderConsumer

        consumer = OrderConsumer(mock_channel)
        invalid_message = b"invalid json"

        method = MagicMock()
        method.delivery_tag = 2

        # Process invalid message
        consumer.process_message(mock_channel, method, None, invalid_message)

        # Verify nack was called without requeue (sends to DLX)
        mock_channel.basic_nack.assert_called_once_with(
            delivery_tag=2,
            requeue=False
        )

    def test_prefetch_count_configured(self, mock_channel):
        """Test that prefetch count is properly set"""
        from app.consumers import OrderConsumer

        consumer = OrderConsumer(mock_channel, prefetch_count=10)
        consumer.setup()

        mock_channel.basic_qos.assert_called_once_with(prefetch_count=10)
```

---

## Integration Testing with Real RabbitMQ

### Setup and Teardown

```python
# tests/integration/test_message_flow.py
import pytest
import pika
import json
import time

@pytest.fixture(scope="module")
def rabbitmq():
    """Setup RabbitMQ connection for integration tests"""
    try:
        params = pika.ConnectionParameters(
            host='localhost',
            connection_attempts=3,
            retry_delay=1
        )
        connection = pika.BlockingConnection(params)
        channel = connection.channel()

        # Setup test infrastructure
        channel.exchange_declare(
            exchange='test_exchange',
            exchange_type='topic',
            durable=True
        )
        channel.queue_declare(queue='test_queue', durable=True)
        channel.queue_bind(
            exchange='test_exchange',
            queue='test_queue',
            routing_key='test.#'
        )

        yield channel

        # Cleanup
        channel.queue_delete(queue='test_queue')
        channel.exchange_delete(exchange='test_exchange')
        connection.close()
    except pika.exceptions.AMQPConnectionError:
        pytest.skip("RabbitMQ not available")
```

---

### Publisher Confirms Integration Test

```python
class TestPublisherConfirms:
    """Integration test: verify publisher confirms work"""

    def test_publisher_confirms_enabled(self, rabbitmq):
        """Test confirms with real RabbitMQ"""
        channel = rabbitmq
        channel.confirm_delivery()

        # Declare test queue
        channel.queue_declare(queue='test_confirms', durable=True)

        # Publish with confirms - should not raise
        channel.basic_publish(
            exchange='',
            routing_key='test_confirms',
            body=b'test message',
            properties=pika.BasicProperties(delivery_mode=2)
        )

        # Cleanup
        channel.queue_delete(queue='test_confirms')

    def test_unroutable_message_returns(self, rabbitmq):
        """Test that unroutable messages are returned"""
        channel = rabbitmq
        channel.confirm_delivery()

        with pytest.raises(pika.exceptions.UnroutableError):
            channel.basic_publish(
                exchange='',
                routing_key='nonexistent_queue',
                body=b'test',
                mandatory=True
            )
```

---

### Dead Letter Exchange Integration Test

```python
class TestDeadLetterExchange:
    """Integration test: verify DLX receives rejected messages"""

    def test_dlx_receives_rejected_messages(self, rabbitmq):
        """Test DLX routing"""
        channel = rabbitmq

        # Setup DLX
        channel.exchange_declare(exchange='test_dlx', exchange_type='fanout')
        channel.queue_declare(queue='test_dead_letters')
        channel.queue_bind(exchange='test_dlx', queue='test_dead_letters')

        # Setup main queue with DLX
        channel.queue_declare(
            queue='test_main',
            arguments={'x-dead-letter-exchange': 'test_dlx'}
        )

        # Publish and reject message
        channel.basic_publish(
            exchange='',
            routing_key='test_main',
            body=b'will be rejected'
        )

        # Get and reject message
        method, props, body = channel.basic_get('test_main')
        if method:
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        # Wait for DLX delivery
        time.sleep(0.1)

        # Verify message arrived in DLX queue
        method, props, body = channel.basic_get('test_dead_letters')
        assert body == b'will be rejected'

        # Cleanup
        channel.queue_delete(queue='test_main')
        channel.queue_delete(queue='test_dead_letters')
        channel.exchange_delete(exchange='test_dlx')
```

---

### End-to-End Message Flow Test

```python
class TestMessageFlow:
    """Integration tests for complete message flows"""

    def test_publish_and_consume(self, rabbitmq):
        """Test end-to-end message flow"""
        channel = rabbitmq
        test_message = {"test_id": 123, "data": "test"}

        # Publish
        channel.basic_publish(
            exchange='test_exchange',
            routing_key='test.message',
            body=json.dumps(test_message),
            properties=pika.BasicProperties(delivery_mode=2)
        )

        # Consume
        method, props, body = channel.basic_get('test_queue')
        assert method is not None
        received = json.loads(body)
        assert received['test_id'] == 123

        channel.basic_ack(delivery_tag=method.delivery_tag)

    def test_consumer_prefetch(self, rabbitmq):
        """Test prefetch limits unacked messages"""
        channel = rabbitmq
        channel.basic_qos(prefetch_count=2)

        # Publish 5 messages
        for i in range(5):
            channel.basic_publish(
                exchange='',
                routing_key='test_queue',
                body=f'msg-{i}'.encode()
            )

        # Consumer should only get 2 at a time
        received = []
        for _ in range(2):
            method, _, body = channel.basic_get('test_queue')
            if method:
                received.append(body)
                # Don't ack yet

        # Verify we got 2 messages
        assert len(received) == 2

        # Cleanup - ack remaining messages
        while True:
            method, _, _ = channel.basic_get('test_queue')
            if not method:
                break
            channel.basic_ack(delivery_tag=method.delivery_tag)
```

---

## Performance Testing

### Throughput Benchmarks

```python
# tests/performance/test_throughput.py
import pytest
import pika
import time
import statistics

@pytest.fixture
def perf_channel():
    """Channel for performance testing"""
    connection = pika.BlockingConnection(
        pika.ConnectionParameters('localhost')
    )
    channel = connection.channel()
    channel.queue_declare(queue='perf_test', durable=True)
    channel.confirm_delivery()
    yield channel
    channel.queue_delete(queue='perf_test')
    connection.close()

class TestThroughput:
    """Performance benchmarks for RabbitMQ operations"""

    def test_publish_throughput(self, perf_channel):
        """Benchmark: publish 10,000 messages"""
        message_count = 10000
        message = b'x' * 1024  # 1KB message

        start = time.time()
        for _ in range(message_count):
            perf_channel.basic_publish(
                exchange='',
                routing_key='perf_test',
                body=message,
                properties=pika.BasicProperties(delivery_mode=2)
            )
        elapsed = time.time() - start

        rate = message_count / elapsed
        print(f"\nPublish rate: {rate:.0f} msg/s")
        assert rate > 1000, f"Publish rate {rate} below threshold"

    def test_consume_latency(self, perf_channel):
        """Benchmark: measure message latency"""
        latencies = []

        for _ in range(100):
            # Publish with timestamp
            send_time = time.time()
            perf_channel.basic_publish(
                exchange='',
                routing_key='perf_test',
                body=str(send_time).encode()
            )

            # Consume immediately
            method, _, body = perf_channel.basic_get('perf_test')
            receive_time = time.time()

            if method:
                latency = (receive_time - float(body)) * 1000  # ms
                latencies.append(latency)
                perf_channel.basic_ack(delivery_tag=method.delivery_tag)

        avg_latency = statistics.mean(latencies)
        p99_latency = statistics.quantiles(latencies, n=100)[98]

        print(f"\nAvg latency: {avg_latency:.2f}ms, P99: {p99_latency:.2f}ms")
        assert avg_latency < 10, f"Average latency {avg_latency}ms too high"
```

---

### Load Testing

```python
# tests/performance/test_load.py
import pytest
import pika
import time
import threading
import queue

class TestLoad:
    """Load testing with multiple producers/consumers"""

    def test_concurrent_publishers(self):
        """Test multiple publishers simultaneously"""
        message_count_per_thread = 1000
        thread_count = 10
        results = queue.Queue()

        def publish_worker():
            connection = pika.BlockingConnection(
                pika.ConnectionParameters('localhost')
            )
            channel = connection.channel()
            channel.confirm_delivery()

            start = time.time()
            for i in range(message_count_per_thread):
                channel.basic_publish(
                    exchange='',
                    routing_key='load_test',
                    body=f'message-{i}'.encode(),
                    properties=pika.BasicProperties(delivery_mode=2)
                )
            elapsed = time.time() - start

            connection.close()
            results.put(elapsed)

        # Create queue
        connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        channel = connection.channel()
        channel.queue_declare(queue='load_test', durable=True)
        connection.close()

        # Start publisher threads
        threads = []
        overall_start = time.time()
        for _ in range(thread_count):
            t = threading.Thread(target=publish_worker)
            t.start()
            threads.append(t)

        # Wait for completion
        for t in threads:
            t.join()

        overall_elapsed = time.time() - overall_start
        total_messages = message_count_per_thread * thread_count
        overall_rate = total_messages / overall_elapsed

        print(f"\nTotal messages: {total_messages}")
        print(f"Overall rate: {overall_rate:.0f} msg/s")
        print(f"Total time: {overall_elapsed:.2f}s")

        # Cleanup
        connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost')
        )
        channel = connection.channel()
        channel.queue_delete(queue='load_test')
        connection.close()

        assert overall_rate > 5000, f"Load test rate {overall_rate} too low"
```

---

## Test Configuration

### pytest Configuration

```python
# conftest.py
import pytest

def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers",
        "integration: integration tests requiring RabbitMQ"
    )
    config.addinivalue_line(
        "markers",
        "slow: slow tests"
    )
    config.addinivalue_line(
        "markers",
        "performance: performance benchmark tests"
    )

@pytest.fixture(scope="session")
def rabbitmq_host():
    """RabbitMQ host for testing"""
    return os.getenv('RABBITMQ_HOST', 'localhost')

@pytest.fixture(scope="session")
def rabbitmq_credentials():
    """RabbitMQ credentials for testing"""
    return pika.PlainCredentials(
        os.getenv('RABBITMQ_USER', 'guest'),
        os.getenv('RABBITMQ_PASSWORD', 'guest')
    )
```

```ini
# pytest.ini
[pytest]
markers =
    integration: integration tests requiring RabbitMQ
    slow: slow running tests
    performance: performance benchmarks

testpaths = tests
addopts = -v --tb=short --strict-markers

# Ignore performance tests by default
addopts = -m "not performance"
```

---

## Test Execution

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run only unit tests (fast, no RabbitMQ needed)
pytest tests/ -v -m "not integration and not performance"

# Run integration tests
pytest tests/ -v -m integration

# Run performance benchmarks
pytest tests/performance/ -v -m performance

# Run with coverage
pytest tests/ --cov=app --cov-report=html --cov-report=term-missing

# Run specific test file
pytest tests/test_message_queue.py -v

# Run tests matching pattern
pytest tests/ -v -k "test_publish"

# Run tests with output
pytest tests/ -v -s

# Run tests in parallel (requires pytest-xdist)
pytest tests/ -v -n auto
```

---

### CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      rabbitmq:
        image: rabbitmq:3.11-management
        ports:
          - 5672:5672
          - 15672:15672
        env:
          RABBITMQ_DEFAULT_USER: guest
          RABBITMQ_DEFAULT_PASS: guest
        options: >-
          --health-cmd "rabbitmq-diagnostics -q ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Wait for RabbitMQ
      run: |
        timeout 60 bash -c 'until curl -f http://localhost:15672; do sleep 2; done'

    - name: Run unit tests
      run: pytest tests/ -v -m "not integration" --cov=app

    - name: Run integration tests
      run: pytest tests/ -v -m integration
      env:
        RABBITMQ_HOST: localhost
        RABBITMQ_USER: guest
        RABBITMQ_PASSWORD: guest

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

---

## Docker Test Environment

### Docker Compose for Testing

```yaml
# docker-compose.test.yml
version: '3.8'

services:
  rabbitmq:
    image: rabbitmq:3.11-management
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      RABBITMQ_DEFAULT_USER: guest
      RABBITMQ_DEFAULT_PASS: guest
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  test:
    build:
      context: .
      dockerfile: Dockerfile.test
    depends_on:
      rabbitmq:
        condition: service_healthy
    environment:
      RABBITMQ_HOST: rabbitmq
      RABBITMQ_USER: guest
      RABBITMQ_PASSWORD: guest
    command: pytest tests/ -v
```

```bash
# Run tests in Docker
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

---

## Test Data Factories

### Using Factory Pattern

```python
# tests/factories.py
import factory
import json

class MessageFactory(factory.Factory):
    """Factory for creating test messages"""

    class Meta:
        model = dict

    order_id = factory.Sequence(lambda n: f"ORDER-{n:05d}")
    customer_id = factory.Faker('uuid4')
    amount = factory.Faker('pydecimal', left_digits=4, right_digits=2, positive=True)
    status = factory.Iterator(['pending', 'processing', 'completed'])

    @classmethod
    def as_json(cls, **kwargs):
        """Generate JSON-encoded message"""
        return json.dumps(cls(**kwargs)).encode()

# Usage in tests
def test_order_processing():
    message = MessageFactory.as_json(status='pending')
    # Use in test...
```

---

## Coverage Requirements

### Coverage Configuration

```ini
# .coveragerc
[run]
source = app
omit =
    */tests/*
    */venv/*
    */__pycache__/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:

show_missing = True
precision = 2

fail_under = 80
```

---

## Testing Checklist

### Before Committing

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Code coverage > 80%
- [ ] No skipped tests (unless documented)
- [ ] Performance benchmarks within acceptable range
- [ ] Tests run in CI/CD pipeline
- [ ] Mock connections properly cleaned up
- [ ] Test data factories used for consistency
- [ ] Edge cases covered (connection failures, invalid messages)
- [ ] Error handling paths tested

---

## Summary

**Testing Layers**:
1. **Unit Tests**: Fast, isolated, mock RabbitMQ
2. **Integration Tests**: Real broker, full message flow
3. **Performance Tests**: Throughput, latency benchmarks
4. **Load Tests**: Concurrent publishers/consumers

**Best Practices**:
- Use mocks for unit tests
- Use real RabbitMQ for integration tests
- Clean up test queues/exchanges
- Mark slow tests appropriately
- Run unit tests frequently
- Run integration tests before commit
- Run performance tests periodically
