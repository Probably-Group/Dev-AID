---
name: macos-accessibility
version: 2.0.0
description: "macOS accessibility automation with AXUIElement for UI testing, element inspection, and system control. Use when automating macOS UI via accessibility APIs or AXUIElement. Do NOT use for Linux accessibility (use linux-at-spi2)."
compatibility: "macOS 10.15+, Xcode Command Line Tools"
risk_level: MEDIUM
---

# macOS Accessibility - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-284: Accessibility Permission Abuse**
- NEVER: Request accessibility for non-accessibility purposes
- ALWAYS: Minimal permissions, document why accessibility is needed

**CWE-200: Screen Content Exposure**
- NEVER: Log or transmit screen content without consent
- ALWAYS: Mask sensitive areas, user consent for any capture

### 0.3 Risk Level: MEDIUM

**Verification requirements for MEDIUM risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 TCC Permission Model (CWE-284)

**Principle:** macOS requires explicit Accessibility permission via TCC (Transparency, Consent, Control).

```swift
// ❌ WRONG - Not checking permissions
func automateUI() {
    let app = AXUIElementCreateApplication(pid)
    // Will fail silently without permission
}

// ✅ CORRECT - Check and guide permission setup
import ApplicationServices

func checkAccessibilityPermission() -> Bool {
    let options = [kAXTrustedCheckOptionPrompt.takeRetainedValue() as String: true]
    return AXIsProcessTrustedWithOptions(options as CFDictionary)
}

func automateUI() {
    guard checkAccessibilityPermission() else {
        print("Please grant Accessibility permission in System Preferences")
        return
    }
    let app = AXUIElementCreateApplication(pid)
    // Now safe to proceed
}
```

### 1.2 AXUIElement Reference Safety (CWE-416)

**Principle:** AXUIElement references become invalid when UI changes. Never cache without validation.

```swift
// ❌ WRONG - Caching stale references
class UICache {
    var cachedButton: AXUIElement?

    func clickCached() {
        AXUIElementPerformAction(cachedButton!, kAXPressAction as CFString)
        // Button may no longer exist
    }
}

// ✅ CORRECT - Validate before use
import ApplicationServices

class SafeUIReference {
    private let appPID: pid_t
    private let path: [String]  // Path from app root to element

    init(pid: pid_t, path: [String]) {
        self.appPID = pid
        self.path = path
    }

    func resolve() -> AXUIElement? {
        var current = AXUIElementCreateApplication(appPID)

        for identifier in path {
            guard let children = getChildren(of: current) else { return nil }
            guard let match = children.first(where: { getIdentifier($0) == identifier }) else {
                return nil
            }
            current = match
        }

        return isValid(current) ? current : nil
    }

    private func isValid(_ element: AXUIElement) -> Bool {
        var role: CFTypeRef?
        let result = AXUIElementCopyAttributeValue(element, kAXRoleAttribute as CFString, &role)
        return result == .success
    }
}
```

### 1.3 Bounds Validation (CWE-119)

**Principle:** Validate element positions before simulating input to prevent off-screen clicks.

---

## 2. Version Requirements

```
# macOS SDK
macOS >= 12.0 (Monterey)
Swift >= 5.7
# Framework
ApplicationServices.framework
# For Swift convenience wrappers
AXSwift >= 0.3.2 (optional)
```

---

## 3. Code Patterns

### WHEN creating AXUIElement references, always check result codes

```swift
// ❌ WRONG - Ignoring errors
var value: CFTypeRef?
AXUIElementCopyAttributeValue(element, kAXTitleAttribute as CFString, &value)
let title = value as! String  // Crash if nil

// ✅ CORRECT - Handle all AXError cases
import ApplicationServices

enum AXAttributeError: Error {
    case notSupported
    case illegalArgument
    case invalidElement
    case timeout
    case unknown(AXError)
}

func getAttribute<T>(
    _ element: AXUIElement,
    _ attribute: String
) -> Result<T, AXAttributeError> {
    var value: CFTypeRef?
    let result = AXUIElementCopyAttributeValue(
        element,
        attribute as CFString,
        &value
    )

    switch result {
    case .success:
        if let typedValue = value as? T {
            return .success(typedValue)
        }
        return .failure(.illegalArgument)
    case .attributeUnsupported:
        return .failure(.notSupported)
    case .invalidUIElement:
        return .failure(.invalidElement)
    case .cannotComplete:
        return .failure(.timeout)
    default:
        return .failure(.unknown(result))
    }
}

// Usage
switch getAttribute(button, kAXTitleAttribute as String) as Result<String, AXAttributeError> {
case .success(let title):
    print("Button: \(title)")
case .failure(.invalidElement):
    print("Element no longer exists")
case .failure(let error):
    print("Error: \(error)")
}
```

### WHEN traversing UI hierarchy, use bounded recursive search

```swift
// ❌ WRONG - Unbounded traversal
func findAll(_ element: AXUIElement) -> [AXUIElement] {
    var results: [AXUIElement] = [element]
    if let children = getChildren(element) {
        for child in children {
            results.append(contentsOf: findAll(child))  // Stack overflow risk
        }
    }
    return results
}

// ✅ CORRECT - Bounded traversal with limits
import ApplicationServices

struct AXSearchConfig {
    let maxDepth: Int
    let maxResults: Int
    let timeout: TimeInterval

    static let `default` = AXSearchConfig(
        maxDepth: 10,
        maxResults: 500,
        timeout: 5.0
    )
}

func findElements(
    root: AXUIElement,
    matching predicate: (AXUIElement) -> Bool,
    config: AXSearchConfig = .default
) -> [AXUIElement] {
    var results: [AXUIElement] = []
    var visited = Set<Int>()
    let startTime = Date()

    func search(_ element: AXUIElement, depth: Int) {
        // Check limits
        guard depth < config.maxDepth else { return }
        guard results.count < config.maxResults else { return }
        guard Date().timeIntervalSince(startTime) < config.timeout else { return }

        // Get unique identifier for cycle detection
        let hash = CFHash(element)
        guard !visited.contains(hash) else { return }
        visited.insert(hash)

        // Check match
        if predicate(element) {
            results.append(element)
        }

        // Get children
        var childrenRef: CFTypeRef?
        let result = AXUIElementCopyAttributeValue(
            element,
            kAXChildrenAttribute as CFString,
            &childrenRef
        )

        guard result == .success,
              let children = childrenRef as? [AXUIElement] else {
            return
        }

        // Limit children per node
        for child in children.prefix(50) {
            search(child, depth: depth + 1)
        }
    }

    search(root, depth: 0)
    return results
}
```

### WHEN performing actions, verify element state first

```swift
// ❌ WRONG - Click without verification
func clickButton(_ button: AXUIElement) {
    AXUIElementPerformAction(button, kAXPressAction as CFString)
}

// ✅ CORRECT - Verify enabled and visible before action
import ApplicationServices

enum ActionError: Error {
    case notEnabled
    case notVisible
    case actionFailed(AXError)
    case elementInvalid
}

func safePerformAction(
    _ element: AXUIElement,
    action: String
) -> Result<Void, ActionError> {
    // Verify element is still valid
    var role: CFTypeRef?
    guard AXUIElementCopyAttributeValue(
        element,
        kAXRoleAttribute as CFString,
        &role
    ) == .success else {
        return .failure(.elementInvalid)
    }

    // Check if enabled
    var enabled: CFTypeRef?
    if AXUIElementCopyAttributeValue(
        element,
        kAXEnabledAttribute as CFString,
        &enabled
    ) == .success {
        if let isEnabled = enabled as? Bool, !isEnabled {
            return .failure(.notEnabled)
        }
    }

    // Check if visible (has valid position)
    var position: CFTypeRef?
    guard AXUIElementCopyAttributeValue(
        element,
        kAXPositionAttribute as CFString,
        &position
    ) == .success else {
        return .failure(.notVisible)
    }

    // Perform action
    let result = AXUIElementPerformAction(element, action as CFString)
    if result == .success {
        return .success(())
    }
    return .failure(.actionFailed(result))
}

// Usage
switch safePerformAction(button, action: kAXPressAction as String) {
case .success:
    print("Button clicked")
case .failure(.notEnabled):
    print("Button is disabled")
case .failure(.elementInvalid):
    print("Button no longer exists")
case .failure(let error):
    print("Click failed: \(error)")
}
```

### WHEN observing UI changes, use AXObserver with proper cleanup

```swift
// ❌ WRONG - No cleanup of observers
var observer: AXObserver?
AXObserverCreate(pid, callback, &observer)
AXObserverAddNotification(observer!, element, kAXFocusedUIElementChangedNotification as CFString, nil)
// Leaks observer

// ✅ CORRECT - RAII-style observer management
import ApplicationServices

class AXUIObserver {
    private let observer: AXObserver
    private let element: AXUIElement
    private var notifications: Set<String> = []
    private let callback: (AXUIElement, String) -> Void

    init?(
        pid: pid_t,
        element: AXUIElement,
        callback: @escaping (AXUIElement, String) -> Void
    ) {
        self.element = element
        self.callback = callback

        var observerRef: AXObserver?
        let result = AXObserverCreate(pid, { observer, element, notification, refcon in
            guard let refcon = refcon else { return }
            let wrapper = Unmanaged<AXUIObserver>.fromOpaque(refcon).takeUnretainedValue()
            wrapper.callback(element, notification as String)
        }, &observerRef)

        guard result == .success, let obs = observerRef else {
            return nil
        }
        self.observer = obs

        // Add to run loop
        CFRunLoopAddSource(
            CFRunLoopGetMain(),
            AXObserverGetRunLoopSource(observer),
            .defaultMode
        )
    }

    func observe(_ notification: String) -> Bool {
        let refcon = Unmanaged.passUnretained(self).toOpaque()
        let result = AXObserverAddNotification(
            observer,
            element,
            notification as CFString,
            refcon
        )
        if result == .success {
            notifications.insert(notification)
            return true
        }
        return false
    }

    deinit {
        // Clean up all notifications
        for notification in notifications {
            AXObserverRemoveNotification(
                observer,
                element,
                notification as CFString
            )
        }

        // Remove from run loop
        CFRunLoopRemoveSource(
            CFRunLoopGetMain(),
            AXObserverGetRunLoopSource(observer),
            .defaultMode
        )
    }
}
```

---

## 4. Anti-Patterns

**NEVER:**
- Cache AXUIElement references without validation
- Ignore AXError return codes
- Traverse UI trees without depth/count limits
- Perform actions without checking enabled state
- Leak AXObserver references (use RAII pattern)
- Assume Accessibility permission is granted
- Click elements outside visible screen bounds

---

## 5. Testing

```swift
import XCTest
@testable import YourApp

class AXUIElementTests: XCTestCase {

    func testPermissionCheckDoesNotCrash() {
        // Should not crash even if permission denied
        let hasPermission = checkAccessibilityPermission()
        // Just verify it returns a boolean
        XCTAssertNotNil(hasPermission)
    }

    func testBoundedTraversalRespectsLimits() {
        // Create mock app element (in real tests, use actual app)
        let app = AXUIElementCreateApplication(getpid())

        let config = AXSearchConfig(maxDepth: 2, maxResults: 10, timeout: 1.0)
        let results = findElements(
            root: app,
            matching: { _ in true },
            config: config
        )

        XCTAssertLessThanOrEqual(results.count, 10)
    }

    func testSafeActionHandlesInvalidElement() {
        // Create invalid element reference
        let invalidElement = AXUIElementCreateApplication(99999)

        let result = safePerformAction(invalidElement, action: kAXPressAction as String)

        switch result {
        case .failure(.elementInvalid), .failure(.actionFailed):
            // Expected
            break
        default:
            XCTFail("Should fail for invalid element")
        }
    }

    func testObserverCleanup() {
        // Verify no leaks (run with Instruments)
        weak var weakObserver: AXUIObserver?

        autoreleasepool {
            let app = AXUIElementCreateApplication(getpid())
            let observer = AXUIObserver(pid: getpid(), element: app) { _, _ in }
            weakObserver = observer
            _ = observer?.observe(kAXFocusedUIElementChangedNotification as String)
        }

        // Observer should be deallocated
        XCTAssertNil(weakObserver)
    }
}
```

---

## 6. Pre-Generation Checklist

**BEFORE generating macOS Accessibility code:**

- [ ] Permission check: `AXIsProcessTrustedWithOptions` called first
- [ ] Error handling: All AXError cases handled explicitly
- [ ] Depth limits: Tree traversal bounded (maxDepth, maxResults)
- [ ] Timeout handling: Long operations have timeout guards
- [ ] Element validation: Check validity before actions
- [ ] State verification: Check enabled/visible before interactions
- [ ] Observer cleanup: Using RAII pattern for AXObserver
- [ ] Cycle detection: Track visited elements via CFHash

---

**Performance**: Quality over speed. Verify all code examples compile. Never skip security checks. See `template-references/performance-notes.md` for full guidelines.