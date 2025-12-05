# RabbitMQ Security Examples

## Overview

This guide covers comprehensive security practices for RabbitMQ, including authentication, authorization, TLS configuration, secrets management, and OWASP Top 10 2025 mappings.

---

## Authentication and Authorization

### 1. Disable Default Guest User

```bash
# Remove default guest user
rabbitmqctl delete_user guest

# Create admin user
rabbitmqctl add_user admin SecureP@ssw0rd
rabbitmqctl set_user_tags admin administrator

# Create application user with limited permissions
rabbitmqctl add_user app_user AppP@ssw0rd
rabbitmqctl set_permissions -p / app_user ".*" ".*" ".*"
```

**Best Practices**:
- Always delete `guest` user in production
- Use strong passwords (min 16 characters, mixed case, numbers, symbols)
- Create separate users for different applications
- Use least privilege principle

---

### 2. Virtual Hosts for Isolation

```bash
# Create separate vhosts for environments
rabbitmqctl add_vhost production
rabbitmqctl add_vhost staging
rabbitmqctl add_vhost development

# Set permissions per vhost
rabbitmqctl set_permissions -p production app_user "^app-.*" "^app-.*" "^app-.*"
rabbitmqctl set_permissions -p staging app_user ".*" ".*" ".*"
```

**Virtual Host Pattern Matching**:
- First argument: Configure permission (declare exchanges/queues)
- Second argument: Write permission (publish messages)
- Third argument: Read permission (consume messages)

**Examples**:
```bash
# Read-only consumer
rabbitmqctl set_permissions -p production consumer_user "" "" ".*"

# Write-only publisher
rabbitmqctl set_permissions -p production publisher_user "" ".*" ""

# Limited to specific queues
rabbitmqctl set_permissions -p production limited_user "^orders\..*" "^orders\..*" "^orders\..*"
```

---

### 3. Topic Permissions

```bash
# Restrict publishing to specific exchanges
rabbitmqctl set_topic_permissions -p production app_user amq.topic "^orders\..*" "^orders\..*"

# Allow only consuming from specific topics
rabbitmqctl set_topic_permissions -p production consumer_user amq.topic "" "^logs\..*"
```

**Use Cases**:
- Limit publishers to specific routing keys
- Restrict consumers to authorized topics
- Implement role-based access to message streams

---

## TLS/SSL Configuration

### Server-Side TLS Configuration

```ini
# /etc/rabbitmq/rabbitmq.conf

## Enable SSL listener
listeners.ssl.default = 5671

## SSL Options
ssl_options.cacertfile = /etc/rabbitmq/ssl/ca_certificate.pem
ssl_options.certfile   = /etc/rabbitmq/ssl/server_certificate.pem
ssl_options.keyfile    = /etc/rabbitmq/ssl/server_key.pem

## Require client certificates
ssl_options.verify     = verify_peer
ssl_options.fail_if_no_peer_cert = true

## TLS versions (disable old versions)
ssl_options.versions.1 = tlsv1.3
ssl_options.versions.2 = tlsv1.2

## Cipher suites (strong ciphers only)
ssl_options.ciphers.1 = ECDHE-ECDSA-AES256-GCM-SHA384
ssl_options.ciphers.2 = ECDHE-RSA-AES256-GCM-SHA384
ssl_options.ciphers.3 = ECDHE-ECDSA-AES128-GCM-SHA256

## Disable plain TCP (optional, for maximum security)
listeners.tcp = none
```

---

### Client-Side TLS Configuration

```python
# ✅ SECURE: TLS-enabled connection
import pika
import ssl

# Create SSL context
ssl_context = ssl.create_default_context(
    cafile="/path/to/ca_certificate.pem"
)

# Load client certificate (mutual TLS)
ssl_context.load_cert_chain(
    certfile="/path/to/client_certificate.pem",
    keyfile="/path/to/client_key.pem"
)

# Enforce hostname checking
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED

# Create credentials
credentials = pika.PlainCredentials('app_user', 'SecurePassword')

# Connect with TLS
parameters = pika.ConnectionParameters(
    host='rabbitmq.example.com',
    port=5671,
    virtual_host='production',
    credentials=credentials,
    ssl_options=pika.SSLOptions(ssl_context)
)

connection = pika.BlockingConnection(parameters)
channel = connection.channel()
```

---

### Generating TLS Certificates

```bash
#!/bin/bash
# Generate self-signed certificates for testing

# CA Certificate
openssl genrsa -out ca_key.pem 4096
openssl req -new -x509 -days 365 -key ca_key.pem -out ca_certificate.pem \
  -subj "/CN=MyCA/O=MyOrg/C=US"

# Server Certificate
openssl genrsa -out server_key.pem 4096
openssl req -new -key server_key.pem -out server_csr.pem \
  -subj "/CN=rabbitmq.example.com/O=MyOrg/C=US"
openssl x509 -req -days 365 -in server_csr.pem \
  -CA ca_certificate.pem -CAkey ca_key.pem -CAcreateserial \
  -out server_certificate.pem

# Client Certificate
openssl genrsa -out client_key.pem 4096
openssl req -new -key client_key.pem -out client_csr.pem \
  -subj "/CN=app_user/O=MyOrg/C=US"
openssl x509 -req -days 365 -in client_csr.pem \
  -CA ca_certificate.pem -CAkey ca_key.pem -CAcreateserial \
  -out client_certificate.pem

# Set permissions
chmod 600 *_key.pem
chmod 644 *_certificate.pem ca_certificate.pem
```

---

## Secrets Management

### Environment Variables (Basic)

```python
# ✅ GOOD: Use environment variables
import os
import pika

credentials = pika.PlainCredentials(
    os.environ['RABBITMQ_USER'],
    os.environ['RABBITMQ_PASSWORD']
)

parameters = pika.ConnectionParameters(
    host=os.environ['RABBITMQ_HOST'],
    virtual_host=os.environ.get('RABBITMQ_VHOST', '/'),
    credentials=credentials
)
```

---

### Kubernetes Secrets

```yaml
# ✅ SECURE: Use Kubernetes secrets
apiVersion: v1
kind: Secret
metadata:
  name: rabbitmq-credentials
type: Opaque
stringData:
  username: app_user
  password: SecureP@ssw0rd
  erlang_cookie: SecureErlangCookie123!

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  template:
    spec:
      containers:
      - name: app
        env:
        - name: RABBITMQ_USER
          valueFrom:
            secretKeyRef:
              name: rabbitmq-credentials
              key: username
        - name: RABBITMQ_PASSWORD
          valueFrom:
            secretKeyRef:
              name: rabbitmq-credentials
              key: password
```

---

### HashiCorp Vault Integration

```python
import hvac
import pika

# Connect to Vault
vault_client = hvac.Client(url='https://vault.example.com')
vault_client.token = os.environ['VAULT_TOKEN']

# Read RabbitMQ credentials
secret = vault_client.secrets.kv.v2.read_secret_version(
    path='rabbitmq/production'
)

credentials = pika.PlainCredentials(
    secret['data']['data']['username'],
    secret['data']['data']['password']
)

parameters = pika.ConnectionParameters(
    host='rabbitmq.example.com',
    credentials=credentials
)
```

---

## OWASP Top 10 2025 Mapping

### A01:2025 - Broken Access Control

**Threat**: Unauthorized access to queues/exchanges

**Mitigation**:
```bash
# Use virtual hosts for isolation
rabbitmqctl add_vhost tenant_a
rabbitmqctl add_vhost tenant_b

# Restrict user to their vhost only
rabbitmqctl set_permissions -p tenant_a user_a ".*" ".*" ".*"
# user_a cannot access tenant_b
```

---

### A02:2025 - Security Misconfiguration

**Threat**: Default credentials, exposed management interface

**Mitigation**:
```ini
# /etc/rabbitmq/rabbitmq.conf

# Disable guest user
loopback_users = none  # Removes guest default access

# Secure management interface
management.tcp.port = 15672
management.tcp.ip = 127.0.0.1  # Localhost only

# Or use TLS with authentication
management.ssl.port = 15671
management.ssl.cacertfile = /path/to/ca.pem
management.ssl.certfile = /path/to/cert.pem
management.ssl.keyfile = /path/to/key.pem
```

---

### A03:2025 - Supply Chain

**Threat**: Compromised RabbitMQ packages or plugins

**Mitigation**:
```bash
# Verify package signatures
apt-key fingerprint rabbitmq

# Use official repositories only
deb https://packagecloud.io/rabbitmq/rabbitmq-server/ubuntu/ focal main

# Pin specific versions
apt-cache policy rabbitmq-server
apt install rabbitmq-server=3.11.15-1
```

---

### A04:2025 - Insecure Design

**Threat**: Sensitive data in message bodies without encryption

**Mitigation**:
```python
from cryptography.fernet import Fernet
import pika

# Generate key (store securely)
key = Fernet.generate_key()
cipher = Fernet(key)

# Encrypt sensitive data before publishing
sensitive_data = {"ssn": "123-45-6789", "credit_card": "4111111111111111"}
encrypted = cipher.encrypt(json.dumps(sensitive_data).encode())

channel.basic_publish(
    exchange='',
    routing_key='sensitive_queue',
    body=encrypted,
    properties=pika.BasicProperties(
        content_type='application/octet-stream',
        content_encoding='encrypted'
    )
)
```

---

### A05:2025 - Identification and Authentication Failures

**Threat**: Weak passwords, credential stuffing

**Mitigation**:
```bash
# Enforce strong passwords
# Use external authentication (LDAP, OAuth2)

# LDAP configuration
auth_backends.1 = ldap
auth_ldap.servers.1 = ldap.example.com
auth_ldap.user_dn_pattern = cn=${username},ou=users,dc=example,dc=com
auth_ldap.dn_lookup_bind.user_dn = cn=admin,dc=example,dc=com
auth_ldap.dn_lookup_bind.password = AdminPassword

# Certificate-based authentication (mutual TLS)
ssl_cert_login_from = common_name
ssl_options.verify = verify_peer
ssl_options.fail_if_no_peer_cert = true
```

---

### A06:2025 - Vulnerable and Outdated Components

**Threat**: Unpatched Erlang or RabbitMQ versions

**Mitigation**:
```bash
# Regular updates
apt update
apt upgrade rabbitmq-server erlang

# Check for security advisories
curl https://www.rabbitmq.com/security.html

# Monitor CVE databases
# Subscribe to RabbitMQ security mailing list
```

---

### A07:2025 - Cryptographic Failures

**Threat**: Unencrypted connections, weak TLS configurations

**Mitigation**:
```ini
# Force TLS 1.2+ only
ssl_options.versions.1 = tlsv1.3
ssl_options.versions.2 = tlsv1.2

# Strong cipher suites only
ssl_options.honor_cipher_order = true
ssl_options.ciphers.1 = ECDHE-ECDSA-AES256-GCM-SHA384
ssl_options.ciphers.2 = ECDHE-RSA-AES256-GCM-SHA384

# Disable insecure protocols
listeners.tcp = none  # Force SSL only
```

---

### A08:2025 - Injection

**Threat**: Malicious routing keys, header injection

**Mitigation**:
```python
import re

def sanitize_routing_key(key):
    """Validate routing key format"""
    # Allow only alphanumeric, dots, hyphens
    if not re.match(r'^[a-zA-Z0-9._-]+$', key):
        raise ValueError(f"Invalid routing key: {key}")
    return key

# Validate before publishing
routing_key = sanitize_routing_key(user_input)

channel.basic_publish(
    exchange='orders',
    routing_key=routing_key,
    body=message
)
```

---

### A09:2025 - Logging and Monitoring Failures

**Threat**: Undetected security incidents

**Mitigation**:
```ini
# /etc/rabbitmq/rabbitmq.conf

# Enable audit logging
log.file.level = info
log.connection.level = info
log.channel.level = warning

# Log authentication failures
auth_mechanisms.1 = PLAIN
auth_mechanisms.2 = AMQPLAIN
log.default.level = info

# Send logs to SIEM
log.file = /var/log/rabbitmq/rabbit.log
```

```python
# Monitor failed authentication attempts
import requests

response = requests.get(
    'http://localhost:15672/api/auth/attempts',
    auth=('admin', 'password')
)

for attempt in response.json():
    if not attempt['success']:
        print(f"Failed login: {attempt['username']} from {attempt['ip']}")
```

---

### A10:2025 - Server-Side Request Forgery (SSRF)

**Threat**: Malicious federation/shovel URIs

**Mitigation**:
```bash
# Restrict federation to known hosts
rabbitmqctl set_parameter federation-upstream safe-upstream \
  '{"uri":"amqp://trusted-host:5672"}'

# Use allowlists for shovel destinations
# Never allow user-controlled URIs in federation/shovel

# Network segmentation
# Place RabbitMQ in private network
# Use firewall rules to restrict outbound connections
```

---

## Security Checklist

### Pre-Deployment

- [ ] Default `guest` user deleted
- [ ] Strong passwords for all users (16+ chars)
- [ ] TLS enabled for all connections (port 5671)
- [ ] Client certificates configured (mutual TLS)
- [ ] Management interface secured or disabled
- [ ] Virtual hosts configured per environment
- [ ] User permissions follow least privilege
- [ ] Topic permissions restrict access
- [ ] Secrets stored in vault (not in code)
- [ ] Erlang cookie is strong and secret

### Post-Deployment

- [ ] Connection attempts monitored
- [ ] Failed authentication logged
- [ ] Security updates applied regularly
- [ ] Certificate expiry monitored
- [ ] Access logs reviewed
- [ ] Anomalous traffic detected
- [ ] Incident response plan documented
- [ ] Security audits scheduled

---

## Common Security Mistakes

### ❌ DON'T

```python
# Hardcoded credentials
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='localhost',
        credentials=pika.PlainCredentials('guest', 'guest')
    )
)

# Unencrypted connections in production
parameters = pika.ConnectionParameters(
    host='rabbitmq.prod.example.com',
    port=5672  # Plain TCP
)

# Overly permissive permissions
rabbitmqctl set_permissions -p / app_user ".*" ".*" ".*"
```

### ✅ DO

```python
# Environment-based credentials
credentials = pika.PlainCredentials(
    os.environ['RABBITMQ_USER'],
    os.environ['RABBITMQ_PASSWORD']
)

# TLS-encrypted connections
ssl_context = ssl.create_default_context()
parameters = pika.ConnectionParameters(
    host='rabbitmq.prod.example.com',
    port=5671,
    ssl_options=pika.SSLOptions(ssl_context),
    credentials=credentials
)

# Least privilege permissions
rabbitmqctl set_permissions -p production app_user \
  "^app\\..*" "^app\\..*" "^app\\..*"
```

---

## Penetration Testing

### Test Cases

1. **Authentication Bypass**
   - Attempt default credentials
   - Test weak passwords
   - Try SQL injection in username

2. **Authorization Bypass**
   - Access other vhosts
   - Publish to restricted exchanges
   - Consume from unauthorized queues

3. **Network Security**
   - Attempt plaintext connections
   - Test TLS downgrade attacks
   - Verify certificate validation

4. **Management Interface**
   - Access without authentication
   - Test for XSS in management UI
   - Check for CSRF vulnerabilities

---

## Compliance Considerations

### GDPR

- Encrypt PII in message bodies
- Implement data retention policies (message TTL)
- Enable audit logging for data access
- Document data processing flows

### PCI-DSS

- Use strong cryptography (TLS 1.2+)
- Restrict access to cardholder data
- Log all access to queues with payment data
- Regular security assessments

### HIPAA

- Encrypt PHI in transit (TLS) and at rest
- Implement access controls (vhosts, permissions)
- Audit all access to health data queues
- Business Associate Agreement with hosting provider

---

## Summary

**Security Layers**:
1. **Network**: TLS encryption, firewall rules
2. **Authentication**: Strong passwords, certificates, external auth
3. **Authorization**: Virtual hosts, user permissions, topic permissions
4. **Data**: Message encryption, secure serialization
5. **Monitoring**: Audit logs, intrusion detection, alerting

**Never**:
- ❌ Use default credentials
- ❌ Deploy without TLS
- ❌ Grant excessive permissions
- ❌ Ignore security updates

**Always**:
- ✅ Enable TLS with strong ciphers
- ✅ Use least privilege access
- ✅ Monitor authentication failures
- ✅ Keep software updated
