# Security Auditing Anti-Patterns

This document catalogs common mistakes and anti-patterns in security auditing implementations.

## Critical Anti-Patterns

### 1. Logging Sensitive Data

**❌ NEVER: Log passwords, tokens, PII**

```python
# BAD: Exposes sensitive data in logs
logger.info(f"User {email} logged in with password {password}")
logger.info(f"API call with token: {api_token}")
logger.info(f"Processing payment for card {credit_card_number}")
```

**✅ ALWAYS: Log identifiers only**

```python
# GOOD: Only log non-sensitive identifiers
logger.info("user.login", user_id=user.id, method="password")
logger.info("api.call", request_id=request.id, endpoint="/api/users")
logger.info("payment.processed", transaction_id=transaction.id, amount_cents=1000)
```

**Why This Matters**:
- Logs are often stored in centralized systems with broad access
- Log aggregation systems may not have same security controls as production
- Compliance violations (GDPR, PCI-DSS) for exposing PII/payment data
- Credentials in logs enable credential stuffing attacks

---

### 2. Unprotected/Modifiable Logs

**❌ NEVER: Plain text logs anyone can modify**

```python
# BAD: No integrity protection
with open('audit.log', 'a') as f:
    f.write(json.dumps(event) + '\n')
```

**✅ ALWAYS: Signed, chained logs**

```python
# GOOD: Cryptographic integrity protection
entry['signature'] = hmac.new(key, data, hashlib.sha256).hexdigest()
entry['previous_hash'] = self._previous_hash.hex()
self._previous_hash = bytes.fromhex(entry['hash'])
```

**Why This Matters**:
- Attackers can modify logs to hide their tracks
- Tampered logs are inadmissible as evidence
- Compliance requirements mandate tamper-evident logs
- Chain breaks reveal tampering attempts

---

### 3. Missing Correlation IDs

**❌ NEVER: Untraced requests**

```python
# BAD: Cannot trace request across services
logger.info("Processing request")
logger.info("Database query executed")
logger.info("Response sent")
```

**✅ ALWAYS: Include correlation ID**

```python
# GOOD: Traceable across entire request lifecycle
correlation_id = request.headers.get('X-Correlation-ID', str(uuid.uuid4()))
logger.info("request.processing", correlation_id=correlation_id)
logger.info("database.query", correlation_id=correlation_id, query_type="select")
logger.info("response.sent", correlation_id=correlation_id, status_code=200)
```

**Why This Matters**:
- Impossible to trace requests across microservices
- Cannot correlate security events during incident response
- Difficult to identify root cause of failures
- Poor observability in distributed systems

---

### 4. Insufficient Log File Permissions

**❌ BAD: World-readable logs**

```bash
# Allows any user to read audit logs
chmod 644 /var/log/audit.log
```

**✅ GOOD: Restricted permissions**

```bash
# Only owner (audit daemon) can read/write
chmod 600 /var/log/audit.log
chown auditd:auditd /var/log/audit.log
```

**Why This Matters**:
- Unauthorized users can read sensitive audit data
- Violates principle of least privilege
- Compliance violation (SOC2, ISO27001)
- Enables reconnaissance by malicious insiders

---

### 5. No Log Retention Policy

**❌ BAD: Logs grow unbounded or are deleted too soon**

```python
# BAD: No rotation or retention
with open('/var/log/audit.log', 'a') as f:
    f.write(log_entry)
```

**✅ GOOD: Retention policy with rotation**

```python
# GOOD: Automated rotation and retention
import logging.handlers

handler = logging.handlers.RotatingFileHandler(
    '/var/log/audit.log',
    maxBytes=100_000_000,  # 100MB
    backupCount=90         # Keep 90 days
)
```

**Compliance Requirements**:
- **GDPR**: Delete logs after retention period
- **PCI-DSS**: Retain 1 year, 3 months readily available
- **HIPAA**: Retain 6 years
- **SOC2**: Define and enforce retention policy

---

### 6. Missing Audit Events

**❌ BAD: Only log authentication, miss authorization**

```python
# BAD: Missing critical security events
def login(username, password):
    if authenticate(username, password):
        logger.info("user.login", user=username)
        return True
```

**✅ GOOD: Comprehensive audit trail**

```python
# GOOD: Log all security-relevant events
def login(username, password):
    logger.info("auth.attempt", user=username, ip=request.remote_addr)

    if authenticate(username, password):
        logger.info("auth.success", user=username)
        return True
    else:
        logger.warning("auth.failed", user=username, reason="invalid_credentials")
        return False

def access_resource(user, resource, action):
    logger.info("authz.check", user=user, resource=resource, action=action)

    if has_permission(user, resource, action):
        logger.info("authz.granted", user=user, resource=resource)
        logger.info("data.access", user=user, resource=resource, action=action)
        return True
    else:
        logger.warning("authz.denied", user=user, resource=resource)
        return False
```

**Events to Always Log**:
- ✅ Authentication attempts (success/failure)
- ✅ Authorization decisions (allow/deny)
- ✅ Data access (read/write/delete)
- ✅ Configuration changes
- ✅ Privilege escalations
- ✅ Security policy changes
- ✅ User management (create/delete/modify)

---

### 7. Synchronous SIEM Forwarding

**❌ BAD: Block request on SIEM failure**

```python
# BAD: Application fails if SIEM is down
def log_and_forward(event):
    logger.info(event)
    siem_client.send(event)  # Blocks if SIEM is down!
    return process_request()
```

**✅ GOOD: Async forwarding with queue**

```python
# GOOD: Non-blocking SIEM forwarding
from queue import Queue
from threading import Thread

siem_queue = Queue()

def siem_worker():
    while True:
        event = siem_queue.get()
        try:
            siem_client.send(event)
        except Exception as e:
            logger.error("siem.forward.failed", error=str(e))
        siem_queue.task_done()

Thread(target=siem_worker, daemon=True).start()

def log_and_forward(event):
    logger.info(event)
    siem_queue.put(event)  # Non-blocking
    return process_request()
```

**Why This Matters**:
- SIEM downtime doesn't break production application
- Better performance (no waiting for network calls)
- Graceful degradation during incidents
- Can buffer events during SIEM maintenance

---

### 8. No Log Verification

**❌ BAD: Never verify log integrity**

```python
# BAD: Write logs but never verify chain
logger.log_tamper_evident(event)
```

**✅ GOOD: Regular verification**

```python
# GOOD: Periodic integrity verification
from apscheduler.schedulers.background import BackgroundScheduler

def verify_audit_logs():
    """Verify log chain integrity daily."""
    valid, errors = audit_logger.verify_chain()
    if not valid:
        alert_security_team("Log tampering detected!", errors)

scheduler = BackgroundScheduler()
scheduler.add_job(verify_audit_logs, 'cron', hour=2)  # 2 AM daily
scheduler.start()
```

**Verification Schedule**:
- **Real-time**: Verify on read (performance cost)
- **Daily**: Scheduled verification job
- **On-demand**: Manual verification tool
- **Compliance**: Before audit review

---

### 9. Logging Without Context

**❌ BAD: Vague log messages**

```python
# BAD: Useless for investigation
logger.info("Error occurred")
logger.info("Request processed")
logger.info("Database updated")
```

**✅ GOOD: Rich contextual data**

```python
# GOOD: Actionable information
logger.info(
    "error.occurred",
    error_type="ValidationError",
    field="email",
    value_hash=hashlib.sha256(email.encode()).hexdigest()[:8],
    user_id=user.id
)

logger.info(
    "request.processed",
    method="POST",
    endpoint="/api/users",
    status_code=201,
    duration_ms=142,
    user_id=user.id
)

logger.info(
    "database.updated",
    table="users",
    operation="UPDATE",
    row_id=123,
    fields_changed=["last_login", "login_count"]
)
```

**Essential Context Fields**:
- `timestamp` - When event occurred
- `user_id` - Who performed action
- `ip_address` - Where request came from
- `correlation_id` - Request trace
- `resource` - What was accessed
- `action` - What operation was performed
- `outcome` - Success/failure/partial

---

### 10. Hard-Coded Secrets in Audit Config

**❌ BAD: Secrets in code**

```python
# BAD: Exposed signing key
audit_logger = TamperEvidentLogger(
    signing_key=b"my-secret-key-12345",
    output_path="/var/log/audit.log"
)
```

**✅ GOOD: Environment variables or secret manager**

```python
# GOOD: Secret from environment
import os

audit_logger = TamperEvidentLogger(
    signing_key=os.environ['AUDIT_SIGNING_KEY'].encode(),
    output_path=os.environ.get('AUDIT_LOG_PATH', '/var/log/audit.log')
)

# BETTER: Use secret manager
from cloud_secrets import SecretManager

secrets = SecretManager()
audit_logger = TamperEvidentLogger(
    signing_key=secrets.get('audit-signing-key').encode(),
    output_path="/var/log/audit.log"
)
```

---

## Summary

**Top 10 Anti-Patterns to Avoid**:

1. ❌ Logging passwords, PII, or tokens
2. ❌ Unprotected logs without integrity verification
3. ❌ Missing correlation IDs
4. ❌ World-readable log files
5. ❌ No retention policy
6. ❌ Missing critical audit events
7. ❌ Synchronous SIEM forwarding
8. ❌ Never verifying log integrity
9. ❌ Logging without context
10. ❌ Hard-coded secrets

**Quick Checklist**:
- [ ] No sensitive data in logs (passwords, PII, tokens)
- [ ] Logs have cryptographic integrity protection
- [ ] All events include correlation IDs
- [ ] Log files have restrictive permissions (600)
- [ ] Retention policy defined and enforced
- [ ] All security events logged (auth, authz, data access)
- [ ] SIEM forwarding is asynchronous
- [ ] Log integrity verified regularly
- [ ] Rich contextual data in every log entry
- [ ] Secrets from environment/secret manager

**Remember**: Anti-patterns in audit logging lead to compliance failures, inadmissible evidence, and blind spots during security incidents.
