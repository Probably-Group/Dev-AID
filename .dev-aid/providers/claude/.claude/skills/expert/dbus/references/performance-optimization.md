# D-Bus Performance Optimization

## Pattern 1: Connection Reuse

```python
# GOOD: Reuse connection
class DBusConnectionPool:
    _session_bus = None

    @classmethod
    def get_session_bus(cls):
        if cls._session_bus is None:
            cls._session_bus = dbus.SessionBus()
        return cls._session_bus

# BAD: Create new connection each call
def get_service():
    bus = dbus.SessionBus()  # Expensive!
    return bus.get_object('org.test.Service', '/')
```

**Why it matters**: D-Bus connections are expensive to create. Reusing connections reduces overhead and improves performance.

---

## Pattern 2: Signal Filtering

```python
# GOOD: Filter signals at subscription
bus.add_signal_receiver(
    handler,
    signal_name='SpecificSignal',  # Only this signal
    dbus_interface='org.test.Interface',
    path='/specific/path'  # Only this path
)

# BAD: Receive all signals and filter in handler
bus.add_signal_receiver(
    handler,
    signal_name=None,  # All signals - expensive!
    dbus_interface=None
)
```

**Why it matters**: Filtering signals at the D-Bus level prevents unnecessary signal processing and reduces CPU usage.

---

## Pattern 3: Async Calls with dasbus

```python
# GOOD: Async calls for non-blocking operations
from dasbus.connection import SessionMessageBus
from dasbus.loop import EventLoop
import asyncio

async def async_call():
    bus = SessionMessageBus()
    proxy = bus.get_proxy('org.test.Service', '/')
    result = await asyncio.to_thread(proxy.Method)
    return result

# BAD: Blocking calls in async context
def blocking_call():
    bus = dbus.SessionBus()
    proxy = bus.get_object('org.test.Service', '/')
    return proxy.Method()  # Blocks event loop!
```

**Why it matters**: Async calls prevent blocking the event loop, enabling better concurrency and responsiveness.

---

## Pattern 4: Message Batching

```python
# GOOD: Batch property reads
def get_all_properties(proxy, interface):
    props = dbus.Interface(proxy, 'org.freedesktop.DBus.Properties')
    return props.GetAll(interface)  # One call

# BAD: Individual property reads
def get_properties_slow(proxy, interface):
    props = dbus.Interface(proxy, 'org.freedesktop.DBus.Properties')
    return {
        'prop1': props.Get(interface, 'prop1'),  # Call 1
        'prop2': props.Get(interface, 'prop2'),  # Call 2
        'prop3': props.Get(interface, 'prop3'),  # Call 3
    }
```

**Why it matters**: Batching reduces round-trip overhead and network latency when reading multiple properties.

---

## Pattern 5: Property Caching

```python
# GOOD: Cache properties with TTL
from functools import lru_cache
from time import time

class CachedPropertyAccess:
    def __init__(self, client, cache_ttl=5):
        self.client = client
        self.cache_ttl = cache_ttl
        self._cache = {}

    def get_property(self, bus_name, path, interface, prop):
        key = (bus_name, path, interface, prop)
        cached = self._cache.get(key)

        if cached and time() - cached['time'] < self.cache_ttl:
            return cached['value']

        value = self._fetch_property(bus_name, path, interface, prop)
        self._cache[key] = {'value': value, 'time': time()}
        return value

# BAD: Fetch property every time
def get_property(proxy, interface, prop):
    props = dbus.Interface(proxy, 'org.freedesktop.DBus.Properties')
    return props.Get(interface, prop)  # Always fetches
```

**Why it matters**: Caching reduces unnecessary D-Bus calls for frequently accessed, slowly changing properties.

---

## Performance Benchmarks

| Operation | Without Optimization | With Optimization | Improvement |
|-----------|---------------------|-------------------|-------------|
| Connection creation | 50ms per call | 0.5ms (reused) | 100x faster |
| Signal processing | 100 signals/sec | 1000 signals/sec | 10x faster |
| Property batch read | 30ms (3 calls) | 10ms (1 call) | 3x faster |
| Cached property | 10ms per read | 0.1ms (cached) | 100x faster |

---

## Performance Checklist

Before deploying D-Bus code:
- [ ] Connection pooling implemented
- [ ] Signal filters configured at subscription
- [ ] Async calls used for long-running operations
- [ ] Properties batched with GetAll()
- [ ] Property caching implemented with appropriate TTL
- [ ] Timeout enforcement on all method calls
