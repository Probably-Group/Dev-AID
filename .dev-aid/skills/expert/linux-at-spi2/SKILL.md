---
name: linux-at-spi2
version: 2.0.0
description: "Linux accessibility automation with AT-SPI2 for GTK/Qt application testing, D-Bus a11y, and UI control. Use when automating Linux desktop apps via AT-SPI or accessibility APIs. Do NOT use for macOS automation (use macos-accessibility)."
risk_level: MEDIUM
---

# Linux AT-SPI2 - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-284: D-Bus Access Control**
- NEVER: Open D-Bus accessibility to all users
- ALWAYS: Restrict to session bus, validate caller

**CWE-78: Command Injection via Accessibility**
- NEVER: Execute commands from accessibility text content
- ALWAYS: Treat all accessibility data as untrusted input

### 0.3 Risk Level: MEDIUM

**Verification requirements for MEDIUM risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 D-Bus Access Control (CWE-284)

**Principle:** AT-SPI2 operates over D-Bus session bus. Validate all received data as untrusted IPC.

```python
# ❌ WRONG - Trusting D-Bus data without validation
def handle_accessible(proxy):
    name = proxy.Name  # Could be malicious string
    exec(f"log_{name}()")  # Code injection

# ✅ CORRECT - Validate D-Bus responses
import re
from gi.repository import Atspi

SAFE_NAME_PATTERN = re.compile(r'^[\w\s\-\.]{1,256}$')

def handle_accessible(accessible: Atspi.Accessible) -> str | None:
    try:
        name = accessible.get_name()
        if name and SAFE_NAME_PATTERN.match(name):
            return name
        return None
    except GLib.Error:
        return None  # D-Bus timeout or disconnected
```

### 1.2 Resource Exhaustion Prevention (CWE-400)

**Principle:** AT-SPI trees can be massive. Always limit traversal depth and implement timeouts.

```python
# ❌ WRONG - Unbounded tree traversal
def find_all_buttons(root):
    buttons = []
    for child in root:
        buttons.extend(find_all_buttons(child))  # Stack overflow risk
    return buttons

# ✅ CORRECT - Bounded traversal with limits
from gi.repository import Atspi, GLib

MAX_DEPTH = 15
MAX_NODES = 5000

def find_buttons_bounded(
    accessible: Atspi.Accessible,
    depth: int = 0,
    visited: set[int] | None = None
) -> list[Atspi.Accessible]:
    if visited is None:
        visited = set()

    if depth > MAX_DEPTH or len(visited) > MAX_NODES:
        return []

    unique_id = accessible.get_index_in_parent()
    if unique_id in visited:
        return []  # Cycle detection
    visited.add(unique_id)

    buttons = []
    role = accessible.get_role()
    if role == Atspi.Role.PUSH_BUTTON:
        buttons.append(accessible)

    try:
        child_count = accessible.get_child_count()
        for i in range(min(child_count, 100)):  # Limit children
            child = accessible.get_child_at_index(i)
            if child:
                buttons.extend(find_buttons_bounded(child, depth + 1, visited))
    except GLib.Error:
        pass  # Handle disconnected objects

    return buttons
```

### 1.3 Privilege Separation (CWE-250)

**Principle:** AT-SPI2 requires accessibility permissions. Run automation in isolated process.

---

## 2. Version Requirements

```
# AT-SPI2 (via PyGObject)
PyGObject>=3.42.0
# Atspi bindings (system package)
libatspi>=2.46
# GLib for main loop
glib>=2.74
```

---

## 3. Code Patterns

### WHEN querying accessibility tree, use Atspi bindings with GLib main loop

```python
# ❌ WRONG - Blocking calls without main loop
from gi.repository import Atspi

desktop = Atspi.get_desktop(0)
app = desktop.get_child_at_index(0)  # May hang

# ✅ CORRECT - Async with GLib main loop
from gi.repository import Atspi, GLib

class ATSPIClient:
    def __init__(self):
        Atspi.init()
        self.loop = GLib.MainLoop()
        self.result: list[Atspi.Accessible] = []

    def find_by_role(
        self,
        role: Atspi.Role,
        timeout_ms: int = 5000
    ) -> list[Atspi.Accessible]:
        self.result = []

        def search():
            desktop = Atspi.get_desktop(0)
            for i in range(desktop.get_child_count()):
                app = desktop.get_child_at_index(i)
                if app:
                    self._search_recursive(app, role, depth=0)
            self.loop.quit()
            return False

        GLib.timeout_add(0, search)
        GLib.timeout_add(timeout_ms, self.loop.quit)
        self.loop.run()
        return self.result

    def _search_recursive(
        self,
        node: Atspi.Accessible,
        target_role: Atspi.Role,
        depth: int
    ):
        if depth > 10 or len(self.result) > 100:
            return

        try:
            if node.get_role() == target_role:
                self.result.append(node)

            for i in range(min(node.get_child_count(), 50)):
                child = node.get_child_at_index(i)
                if child:
                    self._search_recursive(child, target_role, depth + 1)
        except GLib.Error:
            pass  # Object no longer valid
```

### WHEN performing actions, verify state before acting

```python
# ❌ WRONG - Click without checking actionable
def click_button(button):
    action = button.get_action_iface()
    action.do_action(0)

# ✅ CORRECT - Verify action availability
from gi.repository import Atspi, GLib

def safe_click(accessible: Atspi.Accessible) -> bool:
    """Click an accessible element safely."""
    try:
        # Verify it's visible and sensitive
        states = accessible.get_state_set()
        if not states.contains(Atspi.StateType.VISIBLE):
            return False
        if not states.contains(Atspi.StateType.SENSITIVE):
            return False

        # Get action interface
        action = accessible.get_action_iface()
        if not action:
            return False

        # Find click action
        n_actions = action.get_n_actions()
        for i in range(n_actions):
            action_name = action.get_action_name(i)
            if action_name in ('click', 'press', 'activate'):
                return action.do_action(i)

        return False
    except GLib.Error as e:
        print(f"Action failed: {e}")
        return False
```

### WHEN listening to events, use proper event subscription

```python
# ❌ WRONG - Polling for changes
while True:
    check_for_changes()
    time.sleep(0.1)

# ✅ CORRECT - Event-driven with AT-SPI listeners
from gi.repository import Atspi, GLib
from typing import Callable

class ATSPIEventListener:
    def __init__(self):
        Atspi.init()
        self.loop = GLib.MainLoop()
        self._listeners: list[Atspi.EventListener] = []

    def on_focus_change(
        self,
        callback: Callable[[Atspi.Accessible], None]
    ):
        def handler(event: Atspi.Event):
            if event.source:
                callback(event.source)

        listener = Atspi.EventListener.new(handler)
        listener.register('focus:')
        self._listeners.append(listener)

    def on_window_create(
        self,
        callback: Callable[[Atspi.Accessible], None]
    ):
        def handler(event: Atspi.Event):
            if event.source:
                callback(event.source)

        listener = Atspi.EventListener.new(handler)
        listener.register('window:create')
        self._listeners.append(listener)

    def start(self):
        self.loop.run()

    def stop(self):
        for listener in self._listeners:
            listener.deregister('focus:')
            listener.deregister('window:create')
        self.loop.quit()

# Usage
listener = ATSPIEventListener()
listener.on_focus_change(lambda acc: print(f"Focus: {acc.get_name()}"))
listener.start()
```

### WHEN finding elements by text, use match rules

```python
# ❌ WRONG - Manual text comparison everywhere
def find_by_name(root, name):
    if root.get_name() == name:
        return root
    # ... recursive search

# ✅ CORRECT - Use Atspi match rules for efficient search
from gi.repository import Atspi

def find_by_match_rule(
    root: Atspi.Accessible,
    name: str | None = None,
    role: Atspi.Role | None = None,
    states: list[Atspi.StateType] | None = None
) -> list[Atspi.Accessible]:
    """Find elements using AT-SPI match rules."""

    # Build state set if provided
    state_set = Atspi.StateSet.new([])
    if states:
        for state in states:
            state_set.add(state)

    # Build attribute dict (empty for now)
    attributes = GLib.HashTable.new(None, None)

    # Create match rule
    rule = Atspi.MatchRule.new(
        state_set,
        Atspi.CollectionMatchType.ALL,  # All states must match
        attributes,
        Atspi.CollectionMatchType.ANY,
        [role] if role else [],
        Atspi.CollectionMatchType.ANY,
        [],  # interfaces
        Atspi.CollectionMatchType.ANY,
        False  # invert
    )

    # Get collection interface
    collection = root.get_collection_iface()
    if not collection:
        return []

    # Query with limits
    matches = collection.get_matches(
        rule,
        Atspi.CollectionSortOrder.CANONICAL,
        100,   # max results
        False  # traverse
    )

    # Filter by name if provided
    if name:
        return [m for m in matches if m.get_name() == name]
    return matches
```

---

## 4. Anti-Patterns

**NEVER:**
- Traverse accessibility trees without depth limits
- Assume D-Bus responses are immediate (use timeouts)
- Hold references to stale Accessible objects
- Poll for changes instead of using event listeners
- Ignore GLib.Error exceptions from D-Bus calls
- Run automation without accessibility permissions enabled

---

## 5. Testing

```python
import pytest
from unittest.mock import Mock, patch
from gi.repository import Atspi, GLib

class TestATSPIClient:
    @pytest.fixture
    def mock_desktop(self):
        desktop = Mock(spec=Atspi.Accessible)
        desktop.get_child_count.return_value = 2
        return desktop

    def test_bounded_traversal_respects_depth_limit(self, mock_desktop):
        """Verify traversal stops at MAX_DEPTH."""
        # Create deeply nested structure
        current = mock_desktop
        for _ in range(20):
            child = Mock(spec=Atspi.Accessible)
            child.get_child_count.return_value = 1
            child.get_role.return_value = Atspi.Role.PANEL
            current.get_child_at_index.return_value = child
            current = child

        result = find_buttons_bounded(mock_desktop)
        # Should not traverse full depth
        assert mock_desktop.get_child_at_index.call_count < 20

    def test_handles_dbus_disconnection(self, mock_desktop):
        """Verify graceful handling of D-Bus errors."""
        mock_desktop.get_child_at_index.side_effect = GLib.Error("Disconnected")

        result = find_buttons_bounded(mock_desktop)
        assert result == []  # No crash

    def test_safe_click_verifies_state(self):
        """Verify click checks element state."""
        button = Mock(spec=Atspi.Accessible)
        state_set = Mock()
        state_set.contains.return_value = False  # Not visible
        button.get_state_set.return_value = state_set

        result = safe_click(button)
        assert result is False
```

---

## 6. Pre-Generation Checklist

**BEFORE generating AT-SPI2 code:**

- [ ] Depth limits: Tree traversal bounded (MAX_DEPTH=15)
- [ ] Timeouts: All D-Bus calls have timeout handling
- [ ] Error handling: GLib.Error caught on all Atspi calls
- [ ] Event-driven: Using listeners instead of polling
- [ ] Resource limits: MAX_NODES limit on search results
- [ ] State verification: Check VISIBLE/SENSITIVE before actions
- [ ] Cycle detection: Track visited nodes in traversal
- [ ] GLib main loop: Async operations use proper event loop

---

**Performance**: Quality over speed. Verify all code examples compile. Never skip security checks. See `template-references/performance-notes.md` for full guidelines.