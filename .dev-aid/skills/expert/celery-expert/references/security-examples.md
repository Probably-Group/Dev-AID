# Celery Security Examples

## 1. Secure Serialization

### The Pickle Vulnerability

**Problem**: Pickle serialization allows arbitrary code execution when deserializing malicious payloads.

**Vulnerable Code**:
```python
# DANGEROUS: Pickle allows code execution
app.conf.task_serializer = 'pickle'  # NEVER!
app.conf.result_serializer = 'pickle'  # NEVER!
app.conf.accept_content = ['pickle']  # NEVER!
```

**Attack Scenario**:
```python
# Attacker can inject malicious pickle payload
import pickle
import os

class Exploit:
    def __reduce__(self):
        return (os.system, ('rm -rf /',))

# This gets serialized and executed on worker
malicious_task.delay(pickle.dumps(Exploit()))
```

**Secure Code**:
```python
# SECURE: Use JSON serialization
app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],  # Only accept JSON
)
```

**Why This is Secure**: JSON serialization only supports basic data types (strings, numbers, lists, dicts) and cannot execute arbitrary code.

---

## 2. Broker Authentication & TLS

### Redis Security

**Vulnerable Code**:
```python
# No authentication or encryption
app.conf.broker_url = 'redis://localhost:6379/0'
```

**Secure Code**:
```python
# Redis with password and TLS
app.conf.broker_url = 'redis://:strong_password@localhost:6379/0'
app.conf.broker_use_ssl = {
    'ssl_cert_reqs': 'required',
    'ssl_ca_certs': '/path/to/ca-bundle.crt',
    'ssl_certfile': '/path/to/client-cert.pem',
    'ssl_keyfile': '/path/to/client-key.pem',
}

# Result backend with same security
app.conf.result_backend = 'redis://:strong_password@localhost:6379/1'
app.conf.redis_backend_use_ssl = {
    'ssl_cert_reqs': 'required',
    'ssl_ca_certs': '/path/to/ca-bundle.crt',
}
```

### RabbitMQ Security

**Vulnerable Code**:
```python
# No authentication or encryption
app.conf.broker_url = 'amqp://guest:guest@localhost:5672//'
```

**Secure Code**:
```python
# RabbitMQ with TLS and authentication
app.conf.broker_url = 'amqps://celery_user:strong_password@localhost:5671/celery_vhost'
app.conf.broker_use_ssl = {
    'keyfile': '/path/to/key.pem',
    'certfile': '/path/to/cert.pem',
    'ca_certs': '/path/to/ca.pem',
    'cert_reqs': ssl.CERT_REQUIRED,
}
```

---

## 3. Input Validation

### Without Validation (Vulnerable)

```python
@app.task
def process_order(order_id, amount, user_email):
    """No validation - accepts any input"""
    # Direct use of unvalidated input
    db.execute(f"UPDATE orders SET amount={amount} WHERE id={order_id}")
    send_email(user_email, "Order processed")
```

**Vulnerabilities**:
- SQL injection via `amount` parameter
- Command injection via `user_email`
- Type confusion (strings passed as numbers)

### With Validation (Secure)

```python
from pydantic import BaseModel, EmailStr, Field, validator

class OrderData(BaseModel):
    order_id: int = Field(gt=0)
    amount: float = Field(gt=0, le=1000000)
    user_email: EmailStr

    @validator('amount')
    def validate_amount(cls, v):
        if v < 0.01:
            raise ValueError('Amount must be at least 0.01')
        return round(v, 2)

@app.task
def process_order_validated(order_data: dict):
    """Validates all inputs before processing"""
    try:
        validated = OrderData(**order_data)
    except ValidationError as e:
        logger.error(f"Invalid order data: {e}")
        raise Reject(f"Validation failed: {e}", requeue=False)

    # Now safe to use validated data
    db.execute(
        "UPDATE orders SET amount=? WHERE id=?",
        (validated.amount, validated.order_id)
    )
    send_email(validated.user_email, "Order processed")
```

---

## 4. Task Signature Validation (Message Signing)

### Purpose
Prevent unauthorized tasks from being injected into your queue.

**Vulnerable Code**:
```python
# No message signing - anyone with broker access can inject tasks
app = Celery('tasks', broker='redis://localhost:6379/0')
```

**Attack Scenario**:
```python
# Attacker with Redis access can inject malicious tasks
import redis
import json

r = redis.Redis()
malicious_task = {
    'task': 'tasks.delete_all_data',
    'args': [],
    'kwargs': {}
}
r.lpush('celery', json.dumps(malicious_task))
```

**Secure Code**:
```python
# Enable message signing
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    task_protocol=2,
    # Message signing
    task_publish_retry_policy={
        'max_retries': 3,
        'interval_start': 0,
        'interval_step': 0.2,
        'interval_max': 0.2,
    }
)

# Use auth backend for task signatures
from celery.security import setup_security
setup_security(
    allowed_serializers=['json'],
    key='/path/to/private_key.pem',
    cert='/path/to/certificate.pem',
    store='/path/to/ca_certs',
)
```

---

## 5. Flower Monitoring Security

### Vulnerable Configuration

```python
# Flower exposed without authentication on public IP
celery -A app flower --address=0.0.0.0 --port=5555
```

**Risk**: Anyone can access task history, results, worker control.

### Secure Configuration

```python
# Option 1: Basic authentication
celery -A app flower \
    --basic_auth=admin:strong_password \
    --address=127.0.0.1 \
    --port=5555

# Option 2: OAuth2 with Google
celery -A app flower \
    --auth=google.com \
    --oauth2_key=your_client_id \
    --oauth2_secret=your_client_secret \
    --oauth2_redirect_uri=https://flower.example.com/login \
    --address=127.0.0.1 \
    --port=5555

# Option 3: Behind reverse proxy with authentication
# nginx config:
# location /flower/ {
#     auth_basic "Restricted";
#     auth_basic_user_file /etc/nginx/.htpasswd;
#     proxy_pass http://127.0.0.1:5555/;
# }
```

---

## 6. Secrets Management

### Vulnerable Code

```python
# Hardcoded secrets in code
app.conf.broker_url = 'redis://:hardcoded_password@localhost:6379/0'
API_KEY = 'sk-1234567890abcdef'

@app.task
def call_api(endpoint):
    response = requests.get(endpoint, headers={'Authorization': f'Bearer {API_KEY}'})
    return response.json()
```

### Secure Code

```python
# Use environment variables and secrets management
import os
from pathlib import Path

# Load from environment
app.conf.broker_url = os.environ['CELERY_BROKER_URL']
app.conf.result_backend = os.environ['CELERY_RESULT_BACKEND']

# Or use secrets manager (AWS Secrets Manager example)
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Load secrets at app initialization
secrets = get_secret('celery/prod/credentials')
app.conf.broker_url = secrets['broker_url']

@app.task
def call_api(endpoint):
    api_key = get_secret('api/keys')['external_api_key']
    response = requests.get(
        endpoint,
        headers={'Authorization': f'Bearer {api_key}'}
    )
    return response.json()
```

---

## 7. Rate Limiting (Prevent Resource Exhaustion)

### Vulnerable Code

```python
@app.task
def call_external_api(url):
    """No rate limiting - can overwhelm external service"""
    return requests.get(url).json()

# Attacker can flood queue
for i in range(10000):
    call_external_api.delay('https://api.example.com/data')
```

### Secure Code

```python
from celery.exceptions import Reject
import time

@app.task(
    bind=True,
    rate_limit='10/m',  # Max 10 tasks per minute
    max_retries=3
)
def call_external_api_limited(self, url):
    """Rate limited API calls"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as exc:
        # Exponential backoff on rate limit errors
        if hasattr(exc.response, 'status_code') and exc.response.status_code == 429:
            retry_after = int(exc.response.headers.get('Retry-After', 60))
            raise self.retry(exc=exc, countdown=retry_after)
        raise

# Additional: Global rate limiting with Redis
from redis import Redis
import hashlib

redis_client = Redis()

@app.task(bind=True)
def rate_limited_task(self, resource_id):
    """Per-resource rate limiting"""
    rate_key = f'rate_limit:{resource_id}'
    current_count = redis_client.incr(rate_key)

    if current_count == 1:
        redis_client.expire(rate_key, 60)  # 1 minute window

    if current_count > 10:  # Max 10 per minute
        raise Reject('Rate limit exceeded', requeue=True)

    return process_resource(resource_id)
```

---

## Security Checklist

Before deploying Celery to production:

- [ ] **Serialization**: JSON only (never pickle)
- [ ] **Broker Authentication**: Password protection enabled
- [ ] **TLS/SSL**: Encrypted broker connections
- [ ] **Input Validation**: All task inputs validated with Pydantic
- [ ] **Message Signing**: Task signature validation enabled (optional but recommended)
- [ ] **Flower Security**: Authentication enabled (basic auth, OAuth, or reverse proxy)
- [ ] **Secrets Management**: No hardcoded credentials (use env vars or secrets manager)
- [ ] **Rate Limiting**: Task rate limits configured
- [ ] **Time Limits**: All tasks have time_limit and soft_time_limit
- [ ] **Result Expiration**: result_expires configured to prevent data leaks
- [ ] **Worker Isolation**: Workers run with minimal privileges (non-root user)
- [ ] **Network Security**: Broker accessible only from application network
- [ ] **Logging**: No sensitive data in task logs
- [ ] **Monitoring**: Alerts configured for task failures and queue buildup

---

## Common Security Mistakes

### 1. Trusting Task Arguments
```python
# BAD - Command injection vulnerability
@app.task
def run_command(cmd):
    os.system(cmd)  # NEVER!

# GOOD - Whitelist allowed commands
@app.task
def run_command(command_name):
    allowed_commands = {
        'backup': '/usr/local/bin/backup.sh',
        'cleanup': '/usr/local/bin/cleanup.sh',
    }
    if command_name not in allowed_commands:
        raise ValueError(f"Command not allowed: {command_name}")
    subprocess.run([allowed_commands[command_name]], check=True)
```

### 2. Exposing Sensitive Data in Results
```python
# BAD - Storing sensitive data in result backend
@app.task
def process_payment(card_number, cvv, expiry):
    result = charge_card(card_number, cvv, expiry)
    return {
        'card_number': card_number,  # NEVER!
        'result': result
    }

# GOOD - Store only transaction ID
@app.task
def process_payment(payment_token):
    # Use tokenized payment
    result = charge_card_with_token(payment_token)
    return {
        'transaction_id': result['id'],
        'status': result['status']
    }
```

### 3. Missing Time Limits
```python
# BAD - Task can run forever
@app.task
def process_large_file(file_path):
    data = read_file(file_path)  # Could be huge
    return process(data)

# GOOD - Time limits prevent resource exhaustion
@app.task(time_limit=300, soft_time_limit=240)
def process_large_file(file_path):
    data = read_file(file_path)
    return process(data)
```
