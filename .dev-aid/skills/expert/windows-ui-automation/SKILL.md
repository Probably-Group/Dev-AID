---
name: windows-ui-automation
version: 2.0.0
description: "Windows UI Automation with UIA, Win32 API, and accessibility tree navigation for desktop testing and control. Use when automating Windows desktop apps, UIA patterns, or Win32 interactions. Do NOT use for macOS or Linux automation."
compatibility: "Windows 10+, .NET or Win32 API access"
risk_level: HIGH
token_budget: 3500
---
# Windows UI Automation - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.2 Security Patterns (security rules)

**CWE-284: UIAutomation Permissions**
- Do not: Run automation with admin when not needed
- Instead: Minimum required privileges, UAC awareness

**CWE-200: Sensitive Data Capture**
- Do not: Capture/log password fields
- Instead: Skip password controls, mask sensitive patterns

---

## 1. Security Principles

### 1.1 Process Targeting Validation (CWE-284)

**Principle:** Only automate explicitly targeted processes. Never interact with system processes.

```rust
// ❌ WRONG - Automating arbitrary processes
fn click_button(window_title: &str) {
    let hwnd = FindWindowW(None, window_title);
    // Could match system dialogs, security prompts!
    SendMessage(hwnd, WM_LBUTTONDOWN, 0, 0);
}

// ✅ CORRECT - Validate process before automation
use windows::Win32::UI::WindowsAndMessaging::*;
use windows::Win32::Foundation::*;
use std::collections::HashSet;

struct ProcessConfig {
    allowed_exe_names: HashSet<String>,
    blocked_window_classes: HashSet<String>,
}

impl Default for ProcessConfig {
    fn default() -> Self {
        Self {
            allowed_exe_names: HashSet::new(),
            blocked_window_classes: [
                "Credential Dialog Xaml Host",
                "Windows Security",
                "UAC",
                "#32770", // System dialogs
            ].into_iter().map(String::from).collect(),
        }
    }
}

fn validate_target(hwnd: HWND, config: &ProcessConfig) -> Result<(), AutomationError> {
    // Get window class
    let mut class_name = [0u16; 256];
    let len = unsafe { GetClassNameW(hwnd, &mut class_name) };
    let class = String::from_utf16_lossy(&class_name[..len as usize]);

    if config.blocked_window_classes.contains(&class) {
        return Err(AutomationError::BlockedWindow(class));
    }

    // Get process ID
    let mut pid = 0u32;
    unsafe { GetWindowThreadProcessId(hwnd, Some(&mut pid)) };

    // Verify it's in allowed list
    let exe_name = get_process_exe_name(pid)?;
    if !config.allowed_exe_names.is_empty() && !config.allowed_exe_names.contains(&exe_name) {
        return Err(AutomationError::UnauthorizedProcess(exe_name));
    }

    Ok(())
}
```

### 1.2 Elevated Privilege Handling (CWE-250)

**Principle:** Never request more privileges than needed. Check elevation status.

```rust
// ❌ WRONG - Running as admin by default
fn main() {
    if !is_elevated() {
        run_as_admin(); // Unnecessary privilege escalation!
    }
    automate_app();
}

// ✅ CORRECT - Minimal privileges, explicit elevation only when needed
use windows::Win32::Security::*;
use windows::Win32::System::Threading::*;

fn is_elevated() -> bool {
    unsafe {
        let mut token: HANDLE = HANDLE::default();
        if OpenProcessToken(GetCurrentProcess(), TOKEN_QUERY, &mut token).is_err() {
            return false;
        }

        let mut elevation = TOKEN_ELEVATION::default();
        let mut size = 0u32;
        let result = GetTokenInformation(
            token,
            TokenElevation,
            Some(&mut elevation as *mut _ as *mut _),
            std::mem::size_of::<TOKEN_ELEVATION>() as u32,
            &mut size,
        );

        CloseHandle(token);
        result.is_ok() && elevation.TokenIsElevated != 0
    }
}

fn automate_app(config: &AutomationConfig) -> Result<(), AutomationError> {
    let target = find_target_window(&config.window_title)?;

    // Check if target requires elevation
    if requires_elevation(&target)? {
        if !config.allow_elevation {
            return Err(AutomationError::ElevationRequired);
        }

        // Log elevation request for audit
        log::warn!("Elevation required for target: {:?}", target);

        if !is_elevated() {
            return Err(AutomationError::NotElevated);
        }
    }

    perform_automation(&target)
}
```

### 1.3 COM Initialization Safety (CWE-362)

**Principle:** COM must be properly initialized per thread. Use RAII pattern.

```rust
// ❌ WRONG - Manual COM management
fn automate() {
    CoInitializeEx(None, COINIT_MULTITHREADED);
    // If panic occurs, CoUninitialize never called!
    do_automation();
    CoUninitialize();
}

// ✅ CORRECT - RAII COM wrapper
use windows::Win32::System::Com::*;

struct ComGuard;

impl ComGuard {
    fn new(apartment: COINIT) -> Result<Self, windows::core::Error> {
        unsafe { CoInitializeEx(None, apartment)? };
        Ok(Self)
    }
}

impl Drop for ComGuard {
    fn drop(&mut self) {
        unsafe { CoUninitialize() };
    }
}

fn automate() -> Result<(), AutomationError> {
    let _com = ComGuard::new(COINIT_APARTMENTTHREADED)?;

    // COM is initialized, will be cleaned up even on panic
    do_automation()
}
```

---

## 2. Version Requirements

```toml
[dependencies]
# Windows crate for safe Win32 bindings
windows = { version = ">=0.52.0", features = [
    "Win32_Foundation",
    "Win32_UI_Accessibility",
    "Win32_UI_WindowsAndMessaging",
    "Win32_System_Com",
    "Win32_Security",
]}
# For UIAutomation specifically
uiautomation = ">=0.1.0"
```

---

## 3. Code Patterns

### WHEN using UI Automation, implement proper element caching

```rust
// ❌ WRONG - Fetching properties repeatedly
fn find_and_click(automation: &IUIAutomation, name: &str) {
    let root = automation.GetRootElement()?;
    let condition = automation.CreatePropertyCondition(UIA_NamePropertyId, name)?;

    loop {
        let element = root.FindFirst(TreeScope_Children, condition)?;
        let current_name = element.GetCurrentPropertyValue(UIA_NamePropertyId)?;
        // Each call crosses process boundary!
    }
}

// ✅ CORRECT - Use caching for batch property fetching
use windows::Win32::UI::Accessibility::*;

struct CachedElement {
    element: IUIAutomationElement,
    name: String,
    control_type: i32,
    bounding_rect: RECT,
    is_enabled: bool,
}

fn create_cache_request(automation: &IUIAutomation) -> Result<IUIAutomationCacheRequest> {
    let cache_request = unsafe { automation.CreateCacheRequest()? };

    // Add properties to cache
    unsafe {
        cache_request.AddProperty(UIA_NamePropertyId)?;
        cache_request.AddProperty(UIA_ControlTypePropertyId)?;
        cache_request.AddProperty(UIA_BoundingRectanglePropertyId)?;
        cache_request.AddProperty(UIA_IsEnabledPropertyId)?;
    }

    Ok(cache_request)
}

fn find_element_cached(
    parent: &IUIAutomationElement,
    condition: &IUIAutomationCondition,
    cache_request: &IUIAutomationCacheRequest,
) -> Result<CachedElement> {
    let element = unsafe {
        parent.FindFirstBuildCache(TreeScope_Descendants, condition, cache_request)?
    };

    // Properties fetched from cache (no IPC)
    Ok(CachedElement {
        name: unsafe { element.GetCachedPropertyValue(UIA_NamePropertyId)?.to_string() },
        control_type: unsafe { element.GetCachedPropertyValue(UIA_ControlTypePropertyId)?.as_raw() },
        bounding_rect: unsafe { element.GetCachedPropertyValue(UIA_BoundingRectanglePropertyId)?.try_into()? },
        is_enabled: unsafe { element.GetCachedPropertyValue(UIA_IsEnabledPropertyId)?.as_raw() != 0 },
        element,
    })
}
```

### WHEN handling UI events, use proper event registration

```rust
// ❌ WRONG - Polling for state changes
fn wait_for_window(title: &str) -> HWND {
    loop {
        if let Some(hwnd) = find_window(title) {
            return hwnd;
        }
        std::thread::sleep(Duration::from_millis(100)); // Wasteful!
    }
}

// ✅ CORRECT - Event-based detection
use windows::Win32::UI::Accessibility::*;
use std::sync::mpsc;

struct WindowOpenHandler {
    tx: mpsc::Sender<IUIAutomationElement>,
    target_name: String,
}

impl IUIAutomationEventHandler_Impl for WindowOpenHandler {
    fn HandleAutomationEvent(
        &self,
        sender: Option<&IUIAutomationElement>,
        event_id: UIA_EVENT_ID,
    ) -> windows::core::Result<()> {
        if event_id == UIA_Window_WindowOpenedEventId {
            if let Some(element) = sender {
                let name = unsafe { element.CurrentName()?.to_string() };
                if name.contains(&self.target_name) {
                    let _ = self.tx.send(element.clone());
                }
            }
        }
        Ok(())
    }
}

fn wait_for_window_event(
    automation: &IUIAutomation,
    target_name: &str,
    timeout: Duration,
) -> Result<IUIAutomationElement> {
    let (tx, rx) = mpsc::channel();

    let handler = WindowOpenHandler {
        tx,
        target_name: target_name.to_string(),
    };

    let root = unsafe { automation.GetRootElement()? };

    // Register event handler
    unsafe {
        automation.AddAutomationEventHandler(
            UIA_Window_WindowOpenedEventId,
            &root,
            TreeScope_Descendants,
            None,
            &handler.into(),
        )?;
    }

    // Wait with timeout
    rx.recv_timeout(timeout)
        .map_err(|_| AutomationError::Timeout)
}
```

### WHEN performing mouse/keyboard input, use SendInput

```rust
// ❌ WRONG - Using deprecated APIs
fn click(x: i32, y: i32) {
    unsafe {
        SetCursorPos(x, y);
        mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0);
        mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0);
    }
}

// ✅ CORRECT - Using SendInput with proper structure
use windows::Win32::UI::Input::KeyboardAndMouse::*;

fn click_at(x: i32, y: i32) -> Result<(), AutomationError> {
    // Convert to normalized coordinates
    let screen_width = unsafe { GetSystemMetrics(SM_CXSCREEN) };
    let screen_height = unsafe { GetSystemMetrics(SM_CYSCREEN) };

    let normalized_x = (x * 65535) / screen_width;
    let normalized_y = (y * 65535) / screen_height;

    let inputs = [
        INPUT {
            r#type: INPUT_MOUSE,
            Anonymous: INPUT_0 {
                mi: MOUSEINPUT {
                    dx: normalized_x,
                    dy: normalized_y,
                    mouseData: 0,
                    dwFlags: MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE,
                    time: 0,
                    dwExtraInfo: 0,
                },
            },
        },
        INPUT {
            r#type: INPUT_MOUSE,
            Anonymous: INPUT_0 {
                mi: MOUSEINPUT {
                    dwFlags: MOUSEEVENTF_LEFTDOWN,
                    ..Default::default()
                },
            },
        },
        INPUT {
            r#type: INPUT_MOUSE,
            Anonymous: INPUT_0 {
                mi: MOUSEINPUT {
                    dwFlags: MOUSEEVENTF_LEFTUP,
                    ..Default::default()
                },
            },
        },
    ];

    let sent = unsafe {
        SendInput(&inputs, std::mem::size_of::<INPUT>() as i32)
    };

    if sent != inputs.len() as u32 {
        return Err(AutomationError::InputFailed);
    }

    Ok(())
}
```

### WHEN traversing UI tree, implement depth limits

```rust
// ❌ WRONG - Unbounded recursion
fn find_all_buttons(element: &IUIAutomationElement) -> Vec<IUIAutomationElement> {
    let mut buttons = vec![];
    visit_all(element, &mut buttons); // Could be infinite!
    buttons
}

fn visit_all(element: &IUIAutomationElement, buttons: &mut Vec<IUIAutomationElement>) {
    if is_button(element) {
        buttons.push(element.clone());
    }
    for child in get_children(element) {
        visit_all(&child, buttons); // No depth limit!
    }
}

// ✅ CORRECT - Bounded traversal
struct TraversalConfig {
    max_depth: usize,
    max_elements: usize,
    timeout: Duration,
}

impl Default for TraversalConfig {
    fn default() -> Self {
        Self {
            max_depth: 20,
            max_elements: 1000,
            timeout: Duration::from_secs(10),
        }
    }
}

fn find_elements(
    root: &IUIAutomationElement,
    condition: &IUIAutomationCondition,
    config: &TraversalConfig,
) -> Result<Vec<IUIAutomationElement>> {
    let start = Instant::now();
    let mut found = vec![];
    let mut stack = vec![(root.clone(), 0usize)];

    while let Some((element, depth)) = stack.pop() {
        // Check timeout
        if start.elapsed() > config.timeout {
            log::warn!("Traversal timeout reached");
            break;
        }

        // Check element limit
        if found.len() >= config.max_elements {
            log::warn!("Element limit reached");
            break;
        }

        // Check depth limit
        if depth >= config.max_depth {
            continue;
        }

        // Check if matches
        if matches_condition(&element, condition)? {
            found.push(element.clone());
        }

        // Add children (reverse order for DFS)
        if let Ok(children) = get_children(&element) {
            for child in children.into_iter().rev() {
                stack.push((child, depth + 1));
            }
        }
    }

    Ok(found)
}
```

---

## 4. Anti-Patterns

Do not:
- Automate system security dialogs (UAC, credentials)
- Skip process validation before sending input
- Use deprecated mouse_event/keybd_event APIs
- Traverse UI tree without depth/element limits
- Forget to uninitialize COM (use RAII)
- Request elevation when not strictly necessary
- Poll for UI changes (use events)
- Cross-process automate without explicit permission

---

## 5. Testing

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_blocked_window_classes() {
        let config = ProcessConfig::default();
# ... (additional test cases follow same pattern)
```

---

## 6. Pre-Generation Checklist

Before generating Windows UI Automation code:

- [ ] Process validation: Allowlist of target executables
- [ ] Blocked windows: Security dialogs, UAC prompts excluded
- [ ] COM initialization: RAII pattern for cleanup
- [ ] Elevation: Minimal privileges, explicit elevation only
- [ ] UI caching: Batch property fetching across process boundary
- [ ] Event-based: Use events instead of polling
- [ ] Input method: SendInput, not deprecated APIs
- [ ] Tree traversal: Depth and element count limits

---
