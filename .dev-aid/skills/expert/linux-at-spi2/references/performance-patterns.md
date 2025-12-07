## 8. Performance Patterns

### Pattern 1: Event Filtering (Reduce D-Bus Traffic)

```python
# BAD: Register for all events
Atspi.EventListener.register_full(handler, 'object:', None)

# GOOD: Filter to specific events needed
ALLOWED_EVENTS = ['object:state-changed:focused', 'window:activate']
for event in ALLOWED_EVENTS:
    Atspi.EventListener.register_full(handler, event, None)
```

### Pattern 2: Node Caching (Avoid Repeated Lookups)

```python
# BAD: Re-traverse tree for each query
def find_button():
    desktop = Atspi.get_desktop(0)
    for i in range(desktop.get_child_count()):
        app = desktop.get_child_at_index(i)
        # Full tree traversal every time

# GOOD: Cache frequently accessed nodes
class CachedATSPI:
    def __init__(self):
        self._app_cache = {}
        self._cache_ttl = 5.0  # seconds

    def get_application(self, name: str):
        now = time.time()
        if name in self._app_cache:
            cached, timestamp = self._app_cache[name]
            if now - timestamp < self._cache_ttl:
                return cached

        app = self._find_app(name)
        self._app_cache[name] = (app, now)
        return app
```

### Pattern 3: Async Queries (Non-Blocking Operations)

```python
# BAD: Blocking synchronous calls in main thread
buttons = [c for c in children if c.get_role() == PUSH_BUTTON]

# GOOD: Use executor for heavy tree traversals
async def get_all_buttons_async(app):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: find_buttons(app))
```

### Pattern 4: Connection Pooling (Singleton)

```python
# BAD: Atspi.init() called per operation
# GOOD: Singleton manager
class ATSPIManager:
    _instance = None
    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            Atspi.init()
        return cls._instance
```

### Pattern 5: Scope Limiting (Reduce Search Space)

```python
# BAD: Search entire desktop tree
result = search_recursive(Atspi.get_desktop(0), name)

# GOOD: Limit to specific app
app = get_application(app_name)
result = search_recursive(app, name)

# BETTER: Add role filtering
result = search_with_role(app, name, role=Atspi.Role.PUSH_BUTTON)
```

---

