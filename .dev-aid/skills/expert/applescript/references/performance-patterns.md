## 7. Performance Patterns

### Pattern 1: Script Caching

```python
# BAD: Recompile script every execution
result = subprocess.run(['osascript', '-e', script], capture_output=True)

# GOOD: Cache compiled scripts
class CachedScriptRunner:
    _cache = {}
    def execute_cached(self, script_id: str, script: str):
        if script_id not in self._cache:
            import tempfile
            _, path = tempfile.mkstemp(suffix='.scpt')
            subprocess.run(['osacompile', '-o', path, '-e', script])
            self._cache[script_id] = path
        return subprocess.run(['osascript', self._cache[script_id]], capture_output=True)
```

### Pattern 2: Batch Operations

```python
# BAD: Multiple separate script calls
subprocess.run(['osascript', '-e', f'tell app "{app}" to set bounds...'])
subprocess.run(['osascript', '-e', f'tell app "{app}" to activate'])

# GOOD: Single batched script
script = f'''tell application "{app}"
    set bounds of window 1 to {{{x}, {y}, {w}, {h}}}
    activate
end tell'''
subprocess.run(['osascript', '-e', script], capture_output=True)
```

### Pattern 3: Async Execution

```python
# BAD: Blocking execution
result = subprocess.run(['osascript', '-e', script], capture_output=True)

# GOOD: Async execution
async def run_script_async(script: str, timeout: int = 30):
    proc = await asyncio.create_subprocess_exec('osascript', '-e', script,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout)
    return stdout.decode().strip(), stderr.decode().strip()
```

### Pattern 4: Result Filtering

```python
# BAD: Return full unfiltered output
script = 'tell app "System Events" to get properties of every window of every process'

# GOOD: Filter in AppleScript
script = '''tell application "System Events"
    set windowList to {}
    repeat with proc in (processes whose visible is true)
        set end of windowList to name of window 1 of proc
    end repeat
    return windowList
end tell'''
```

### Pattern 5: Minimal App Activation

```python
# BAD: Activate app for every operation
subprocess.run(['osascript', '-e', f'tell app "{app}" to activate'])

# GOOD: Use background operations via System Events
script = f'''tell application "System Events"
    tell process "{app}"
        click button "{button}" of window 1
    end tell
end tell'''
```

---

