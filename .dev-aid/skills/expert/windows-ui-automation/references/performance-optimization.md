# Windows UI Automation - Performance Optimization

## Pattern 1: Element Caching

**Problem**: Re-finding elements every operation is expensive.

**Bad Approach**:
```python
# BAD: Re-find element every operation
for i in range(100):
    element = uia.find_element('app.exe', 'TextField')
    element.send_keys(str(i))
```

**Optimized Approach**:
```python
# GOOD: Cache element reference
element = uia.find_element('app.exe', 'TextField')
for i in range(100):
    if element.is_valid():
        element.send_keys(str(i))
    else:
        element = uia.find_element('app.exe', 'TextField')
```

**Performance Gain**: 10-50x faster for repeated operations

**Trade-offs**:
- Must validate element is still valid
- Requires staleness detection
- Memory overhead for cached references

---

## Pattern 2: Scope Limiting

**Problem**: Searching from desktop root is slow.

**Bad Approach**:
```python
# BAD: Search from root every time
root = uia.GetRootElement()
element = root.FindFirst(TreeScope.Descendants, condition)  # Searches entire desktop
```

**Optimized Approach**:
```python
# GOOD: Narrow search scope
app_window = uia.find_window('notepad.exe')
element = app_window.FindFirst(TreeScope.Children, condition)  # Only direct children
```

**Performance Gain**: 5-20x faster depending on desktop complexity

**Best Practices**:
- Always use most specific scope possible
- Use `TreeScope.Children` when structure is known
- Only use `TreeScope.Descendants` when necessary
- Cache parent elements for repeated searches

---

## Pattern 3: Async Operations

**Problem**: Blocking waits tie up threads.

**Bad Approach**:
```python
# BAD: Blocking wait for element
while not element.is_enabled():
    time.sleep(0.1)  # Blocks thread
```

**Optimized Approach**:
```python
# GOOD: Async with timeout
import asyncio

async def wait_for_element(element, timeout=10):
    start = asyncio.get_event_loop().time()
    while not element.is_enabled():
        if asyncio.get_event_loop().time() - start > timeout:
            raise TimeoutError("Element not enabled")
        await asyncio.sleep(0.05)  # Non-blocking
```

**Performance Gain**: Better resource utilization, concurrent operations

**Additional Benefits**:
- Can wait for multiple elements simultaneously
- Better timeout handling
- Non-blocking for other operations

---

## Pattern 4: COM Object Pooling

**Problem**: Creating COM objects is expensive.

**Bad Approach**:
```python
# BAD: Create new COM object per operation
def find_element(name):
    uia = CreateObject('UIAutomationClient.CUIAutomation')  # Expensive
    return uia.GetRootElement().FindFirst(...)
```

**Optimized Approach**:
```python
# GOOD: Reuse COM object
class UIAutomationPool:
    _instance = None

    @classmethod
    def get_automation(cls):
        if cls._instance is None:
            cls._instance = CreateObject('UIAutomationClient.CUIAutomation')
        return cls._instance
```

**Performance Gain**: 2-5x faster for frequent operations

**Implementation Notes**:
- Thread-safe singleton pattern
- Cleanup on process exit
- Consider thread-local storage for multi-threaded scenarios

---

## Pattern 5: Condition Optimization

**Problem**: Multiple sequential searches are inefficient.

**Bad Approach**:
```python
# BAD: Multiple sequential conditions
name_cond = uia.CreatePropertyCondition(UIA_NamePropertyId, 'Submit')
type_cond = uia.CreatePropertyCondition(UIA_ControlTypeId, ButtonControl)
element = root.FindFirst(TreeScope.Descendants, name_cond)
if element.ControlType != ButtonControl:
    element = None
```

**Optimized Approach**:
```python
# GOOD: Combined condition for single search
and_cond = uia.CreateAndCondition(
    uia.CreatePropertyCondition(UIA_NamePropertyId, 'Submit'),
    uia.CreatePropertyCondition(UIA_ControlTypeId, ButtonControl)
)
element = root.FindFirst(TreeScope.Descendants, and_cond)
```

**Performance Gain**: 2x faster, single tree traversal

**Advanced Optimization**:
```python
# BEST: Complex condition with OR/AND combinations
complex_cond = uia.CreateOrCondition(
    uia.CreateAndCondition(
        uia.CreatePropertyCondition(UIA_NamePropertyId, 'Submit'),
        uia.CreatePropertyCondition(UIA_ControlTypeId, ButtonControl)
    ),
    uia.CreateAndCondition(
        uia.CreatePropertyCondition(UIA_AutomationIdPropertyId, 'btnSubmit'),
        uia.CreatePropertyCondition(UIA_ControlTypeId, ButtonControl)
    )
)
```

---

## Pattern 6: Batch Operations

**Problem**: Individual operations have overhead.

**Bad Approach**:
```python
# BAD: Individual property reads
name = element.GetPropertyValue(UIA_NamePropertyId)
type = element.GetPropertyValue(UIA_ControlTypeId)
enabled = element.GetPropertyValue(UIA_IsEnabledPropertyId)
```

**Optimized Approach**:
```python
# GOOD: Batch property reads
properties = {
    'name': UIA_NamePropertyId,
    'type': UIA_ControlTypeId,
    'enabled': UIA_IsEnabledPropertyId,
}

values = {}
for key, prop_id in properties.items():
    try:
        values[key] = element.GetPropertyValue(prop_id)
    except:
        values[key] = None
```

**Performance Gain**: Reduced COM marshaling overhead

---

## Pattern 7: Element Staleness Detection

**Problem**: Cached elements may become stale.

**Implementation**:
```python
class CachedElement:
    """Element wrapper with staleness detection."""

    def __init__(self, element):
        self._element = element
        self._runtime_id = element.GetRuntimeId()
        self._is_stale = False

    def is_valid(self) -> bool:
        """Check if element is still valid."""
        if self._is_stale:
            return False

        try:
            # Verify runtime ID hasn't changed
            current_id = self._element.GetRuntimeId()
            if current_id != self._runtime_id:
                self._is_stale = True
                return False
            return True
        except:
            self._is_stale = True
            return False

    def refresh(self, parent):
        """Refresh element reference."""
        # Re-find element from parent
        # Update internal reference
        pass
```

---

## Pattern 8: Lazy Property Loading

**Problem**: Loading all properties upfront is wasteful.

**Implementation**:
```python
class LazyElement:
    """Element with lazy property loading."""

    def __init__(self, element):
        self._element = element
        self._cache = {}

    @property
    def name(self):
        if 'name' not in self._cache:
            self._cache['name'] = self._element.GetPropertyValue(UIA_NamePropertyId)
        return self._cache['name']

    @property
    def control_type(self):
        if 'type' not in self._cache:
            self._cache['type'] = self._element.GetPropertyValue(UIA_ControlTypeId)
        return self._cache['type']

    def invalidate_cache(self):
        """Clear cached properties."""
        self._cache.clear()
```

---

## Pattern 9: Parallel Element Search

**Problem**: Sequential searches are slow.

**Implementation**:
```python
import concurrent.futures

def parallel_find_elements(search_configs: list) -> dict:
    """Search for multiple elements in parallel."""
    results = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = {}
        for config in search_configs:
            future = executor.submit(
                find_element,
                config['parent'],
                config['condition']
            )
            futures[future] = config['id']

        for future in concurrent.futures.as_completed(futures):
            element_id = futures[future]
            try:
                results[element_id] = future.result()
            except Exception as e:
                results[element_id] = None

    return results
```

**Use Case**: Finding multiple elements on a complex form

**Performance Gain**: Near-linear speedup with number of cores

---

## Pattern 10: Event-Driven Updates

**Problem**: Polling for changes is inefficient.

**Implementation**:
```python
class EventDrivenAutomation:
    """Use UIA events instead of polling."""

    def __init__(self):
        self.uia = CreateObject('UIAutomationClient.CUIAutomation')
        self.event_handlers = {}

    def wait_for_window(self, title: str, timeout: int = 30):
        """Wait for window using events instead of polling."""
        event = threading.Event()
        result = {}

        def on_window_opened(sender, e):
            element = e.Element
            if element.Name == title:
                result['element'] = element
                event.set()

        # Register event handler
        handler_id = self.uia.AddAutomationEventHandler(
            UIA_Window_WindowOpenedEventId,
            self.uia.GetRootElement(),
            TreeScope.Subtree,
            None,
            on_window_opened
        )

        # Wait for event
        if event.wait(timeout):
            return result['element']
        else:
            raise TimeoutError(f"Window '{title}' not found")
```

---

## Performance Benchmarks

### Element Discovery
- **Root search (Descendants)**: ~500-2000ms
- **Root search (Children)**: ~50-200ms
- **Scoped search (Descendants)**: ~100-500ms
- **Scoped search (Children)**: ~10-50ms
- **Cached element access**: ~1-5ms

### Input Operations
- **SendInput (single key)**: ~10-20ms
- **SendInput (string)**: ~50-200ms per string
- **Pattern.Invoke()**: ~20-50ms
- **ValuePattern.SetValue()**: ~20-50ms

### COM Operations
- **Create COM object**: ~50-100ms
- **Get property**: ~5-10ms
- **FindFirst**: ~50-500ms
- **FindAll**: ~100-2000ms

---

## Performance Testing

```python
import time
import statistics

def benchmark_operation(operation, iterations=100):
    """Benchmark automation operation."""
    times = []

    for _ in range(iterations):
        start = time.perf_counter()
        operation()
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    return {
        'mean': statistics.mean(times),
        'median': statistics.median(times),
        'stdev': statistics.stdev(times) if len(times) > 1 else 0,
        'min': min(times),
        'max': max(times),
    }

# Usage
results = benchmark_operation(
    lambda: automation.find_element('notepad.exe', 'Edit1'),
    iterations=50
)
print(f"Mean: {results['mean']*1000:.2f}ms")
```

---

## Performance Checklist

Before deploying automation:
- [ ] Element caching implemented for repeated operations
- [ ] Search scope narrowed to minimum necessary
- [ ] COM objects reused (singleton pattern)
- [ ] Combined conditions used instead of sequential searches
- [ ] Async operations for I/O-bound tasks
- [ ] Event-driven updates instead of polling
- [ ] Performance benchmarks meet targets:
  - Element lookup: < 100ms (95th percentile)
  - Input operations: < 50ms (95th percentile)
  - Full workflow: < 5s (95th percentile)

---

## Common Performance Anti-Patterns

### Anti-Pattern 1: Polling Too Frequently
```python
# BAD: 10ms polling interval
while not element.is_enabled():
    time.sleep(0.01)  # Too frequent, wastes CPU

# GOOD: 50-100ms polling interval
while not element.is_enabled():
    time.sleep(0.05)  # Balance responsiveness and CPU
```

### Anti-Pattern 2: Not Using Timeouts
```python
# BAD: No timeout
element = uia.find_element(condition)  # Could hang forever

# GOOD: With timeout
with timeout_context(30):
    element = uia.find_element(condition)
```

### Anti-Pattern 3: Synchronous Waits in Loops
```python
# BAD: Blocking waits in loop
for item in items:
    element = find_element(item)  # Blocks on each
    element.click()
    time.sleep(1)  # Wasteful

# GOOD: Async/parallel processing
async def process_items(items):
    tasks = [process_item(item) for item in items]
    await asyncio.gather(*tasks)
```

---

## Performance Monitoring

```python
class PerformanceMonitor:
    """Monitor automation performance metrics."""

    def __init__(self):
        self.metrics = []

    def record_operation(self, operation: str, duration: float, success: bool):
        """Record operation metrics."""
        self.metrics.append({
            'operation': operation,
            'duration': duration,
            'success': success,
            'timestamp': time.time()
        })

    def get_stats(self, operation: str = None):
        """Get performance statistics."""
        if operation:
            data = [m for m in self.metrics if m['operation'] == operation]
        else:
            data = self.metrics

        durations = [m['duration'] for m in data if m['success']]

        if not durations:
            return None

        return {
            'count': len(durations),
            'mean': statistics.mean(durations),
            'p50': statistics.median(durations),
            'p95': statistics.quantiles(durations, n=20)[18] if len(durations) > 20 else max(durations),
            'p99': statistics.quantiles(durations, n=100)[98] if len(durations) > 100 else max(durations),
        }
```
