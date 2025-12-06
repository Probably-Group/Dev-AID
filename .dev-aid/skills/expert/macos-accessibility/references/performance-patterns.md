## 7. Performance Patterns

### Pattern 1: Element Caching

```python
# BAD: Query repeatedly
element = AXUIElementCreateApplication(pid)  # Each call

# GOOD: Cache with TTL
class ElementCache:
    def __init__(self, ttl=5.0):
        self.cache, self.ttl = {}, ttl

    def get_or_create(self, pid, role):
        key = (pid, role)
        if key in self.cache and time() - self.cache[key][1] < self.ttl:
            return self.cache[key][0]
        element = self._create_element(pid, role)
        self.cache[key] = (element, time())
        return element
```

### Pattern 2: Scope Limiting

```python
# BAD: Search entire hierarchy
find_all_children(app_element, role='AXButton')  # Deep search

# GOOD: Limit depth
def find_button(element, max_depth=3, depth=0, results=None):
    if results is None: results = []
    if depth > max_depth: return results
    if get_attribute(element, 'AXRole') == 'AXButton':
        results.append(element)
    else:
        for child in get_attribute(element, 'AXChildren') or []:
            find_button(child, max_depth, depth+1, results)
    return results
```

### Pattern 3: Async Queries

```python
# BAD: Sequential blocking
for app in apps: windows.extend(get_windows(app))

# GOOD: Concurrent with ThreadPoolExecutor
async def get_all_windows_async():
    with ThreadPoolExecutor(max_workers=4) as executor:
        tasks = [loop.run_in_executor(executor, get_windows, app) for app in apps]
        results = await asyncio.gather(*tasks)
    return [w for wins in results for w in wins]
```

### Pattern 4: Attribute Batching

```python
# BAD: Multiple calls
title = AXUIElementCopyAttributeValue(element, 'AXTitle', None)
role = AXUIElementCopyAttributeValue(element, 'AXRole', None)

# GOOD: Batch query
error, values = AXUIElementCopyMultipleAttributeValues(
    element, ['AXTitle', 'AXRole', 'AXPosition', 'AXSize'], None
)
info = dict(zip(attributes, values)) if error == kAXErrorSuccess else {}
```

### Pattern 5: Observer Optimization

```python
# BAD: Observer for every notification without debounce

# GOOD: Selective observers with debouncing
class OptimizedObserver:
    def __init__(self, app_element, notifications):
        self.last_callback, self.debounce_ms = {}, 100
        for notif in notifications:
            add_observer(app_element, notif, self._debounced_callback)

    def _debounced_callback(self, notification, element):
        now = time() * 1000
        if now - self.last_callback.get(notification, 0) < self.debounce_ms:
            return
        self.last_callback[notification] = now
        self._handle_notification(notification, element)
```

---

