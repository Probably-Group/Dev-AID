# D-Bus Anti-Patterns and Common Mistakes

## Anti-Pattern 1: Access System Bus Without Need

**Problem**: Always using system bus instead of session bus increases security risk and requires elevated permissions unnecessarily.

**Bad Example**:
```python
# BAD: Always use system bus
bus = dbus.SystemBus()
```

**Better Approach**:
```python
# GOOD: Prefer session bus
bus = dbus.SessionBus()
# Only use system bus when required and with elevated permissions
```

**Why Better**: Session bus is user-scoped and doesn't require elevated privileges. System bus should only be used for system-wide services that genuinely need it.

---

## Anti-Pattern 2: Allow PolicyKit Access

**Problem**: Allowing access to PolicyKit service can lead to privilege escalation vulnerabilities.

**Bad Example**:
```python
# BAD: No service filtering
result = client.call_method('org.freedesktop.PolicyKit1', ...)
```

**Better Approach**:
```python
# GOOD: Block privileged services
BLOCKED_SERVICES = {
    'org.freedesktop.PolicyKit1',
    'org.freedesktop.systemd1',
    'org.freedesktop.login1',
}

if service not in BLOCKED_SERVICES:
    result = client.call_method(service, ...)
else:
    raise SecurityError(f"Access to {service} is blocked")
```

**Why Better**: Blocking privileged services prevents privilege escalation attacks and unauthorized system modifications.

---

## Anti-Pattern 3: Skip Timeout Enforcement

**Problem**: Not setting timeouts can cause indefinite hangs and resource exhaustion.

**Bad Example**:
```python
# BAD: No timeout
result = iface.SomeMethod()
```

**Better Approach**:
```python
# GOOD: With timeout
result = iface.SomeMethod(timeout=30)
```

**Why Better**: Timeouts prevent resource exhaustion and ensure responsive applications.

---

## Anti-Pattern 4: Create New Connections Repeatedly

**Problem**: Creating new D-Bus connections for each operation is expensive and wastes resources.

**Bad Example**:
```python
# BAD: New connection each time
def send_notification():
    bus = dbus.SessionBus()  # Expensive!
    proxy = bus.get_object('org.freedesktop.Notifications', '/')
    return proxy.Notify(...)
```

**Better Approach**:
```python
# GOOD: Reuse connection
class NotificationClient:
    def __init__(self):
        self.bus = dbus.SessionBus()  # Create once
        self.proxy = self.bus.get_object(
            'org.freedesktop.Notifications',
            '/org/freedesktop/Notifications'
        )

    def send_notification(self):
        return self.proxy.Notify(...)
```

**Why Better**: Connection reuse reduces overhead and improves performance significantly.

---

## Anti-Pattern 5: Skip Input Validation

**Problem**: Not validating bus names, object paths, and interface names can lead to security vulnerabilities.

**Bad Example**:
```python
# BAD: No validation
def get_object(bus_name, object_path):
    return bus.get_object(bus_name, object_path)
```

**Better Approach**:
```python
# GOOD: Validate inputs
import re

def validate_bus_name(name: str) -> bool:
    pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)+$'
    return bool(re.match(pattern, name)) and len(name) <= 255

def get_object(bus_name, object_path):
    if not validate_bus_name(bus_name):
        raise ValueError(f"Invalid bus name: {bus_name}")
    return bus.get_object(bus_name, object_path)
```

**Why Better**: Input validation prevents injection attacks and malformed requests.

---

## Anti-Pattern 6: No Audit Logging

**Problem**: Not logging D-Bus operations makes security incidents hard to investigate.

**Bad Example**:
```python
# BAD: No logging
def call_method(service, method):
    return iface.method()
```

**Better Approach**:
```python
# GOOD: Log all operations
import logging

logger = logging.getLogger('dbus.audit')

def call_method(service, method):
    logger.info(f'Calling {service}.{method}')
    try:
        result = iface.method()
        logger.info(f'Success: {service}.{method}')
        return result
    except Exception as e:
        logger.error(f'Failed: {service}.{method}: {e}')
        raise
```

**Why Better**: Audit logging enables security monitoring and incident response.

---

## Anti-Pattern 7: Receive All Signals Without Filtering

**Problem**: Receiving all signals and filtering in the handler is inefficient.

**Bad Example**:
```python
# BAD: Receive all signals - expensive!
bus.add_signal_receiver(
    handler,
    signal_name=None,  # All signals
    dbus_interface=None
)

def handler(signal_name, *args):
    if signal_name == 'SpecificSignal':
        # Process
        pass
```

**Better Approach**:
```python
# GOOD: Filter signals at subscription
bus.add_signal_receiver(
    handler,
    signal_name='SpecificSignal',  # Only this signal
    dbus_interface='org.test.Interface',
    path='/specific/path'  # Only this path
)
```

**Why Better**: Filtering at the D-Bus level reduces CPU usage and improves performance.

---

## Anti-Pattern 8: Skip Peer Credential Validation

**Problem**: Not validating peer credentials can allow malicious processes to impersonate trusted services.

**Bad Example**:
```python
# BAD: No credential check
proxy = bus.get_object(service_name, '/')
return proxy.SensitiveMethod()
```

**Better Approach**:
```python
# GOOD: Validate peer
def validate_peer(bus, service_name, expected_uid=None):
    dbus_obj = bus.get_object('org.freedesktop.DBus', '/org/freedesktop/DBus')
    dbus_iface = dbus.Interface(dbus_obj, 'org.freedesktop.DBus')

    uid = dbus_iface.GetConnectionUnixUser(service_name)
    if expected_uid and uid != expected_uid:
        raise SecurityError(f"Unexpected UID: {uid}")
    return True

validate_peer(bus, service_name, expected_uid=os.getuid())
proxy = bus.get_object(service_name, '/')
return proxy.SensitiveMethod()
```

**Why Better**: Credential validation prevents service impersonation attacks.

---

## Anti-Pattern 9: Individual Property Reads

**Problem**: Reading properties individually when you need multiple values is inefficient.

**Bad Example**:
```python
# BAD: Individual property reads
props = dbus.Interface(proxy, 'org.freedesktop.DBus.Properties')
value1 = props.Get(interface, 'Property1')  # Call 1
value2 = props.Get(interface, 'Property2')  # Call 2
value3 = props.Get(interface, 'Property3')  # Call 3
```

**Better Approach**:
```python
# GOOD: Batch property reads
props = dbus.Interface(proxy, 'org.freedesktop.DBus.Properties')
all_props = props.GetAll(interface)  # One call
value1 = all_props['Property1']
value2 = all_props['Property2']
value3 = all_props['Property3']
```

**Why Better**: Batching reduces round-trip overhead and improves performance.

---

## Anti-Pattern 10: Ignore D-Bus Exceptions

**Problem**: Generic exception handling loses valuable error information.

**Bad Example**:
```python
# BAD: Generic exception handling
try:
    result = iface.Method()
except Exception:
    return None  # Lost error information!
```

**Better Approach**:
```python
# GOOD: Specific D-Bus exception handling
from dbus.exceptions import DBusException

try:
    result = iface.Method()
except DBusException as e:
    error_name = e.get_dbus_name()
    if 'ServiceUnknown' in error_name:
        raise ServiceNotFoundError("Service not available")
    elif 'AccessDenied' in error_name:
        raise PermissionError("Access denied")
    elif 'Timeout' in error_name:
        raise TimeoutError("Operation timed out")
    else:
        logger.error(f"D-Bus error: {error_name}: {e}")
        raise
```

**Why Better**: Specific exception handling enables better error recovery and debugging.

---

## Summary of Anti-Patterns to Avoid

1. ❌ Using system bus when session bus is sufficient
2. ❌ Allowing access to PolicyKit and systemd
3. ❌ Skipping timeout enforcement
4. ❌ Creating new connections for each operation
5. ❌ Not validating bus names and paths
6. ❌ No audit logging
7. ❌ Receiving all signals without filtering
8. ❌ Skipping peer credential validation
9. ❌ Individual property reads instead of batching
10. ❌ Generic exception handling losing error details

**Remember**: Following best practices prevents security vulnerabilities, improves performance, and makes debugging easier.
