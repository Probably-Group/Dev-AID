---
name: applescript
version: 2.0.0
description: "macOS automation with AppleScript and JXA for system scripting, app control, and workflow automation. Use when automating macOS apps, system events, or JXA scripting. Do NOT use for cross-platform scripting (use bash-expert)."
compatibility: "macOS 10.15+"
risk_level: MEDIUM
---

# AppleScript & JXA Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-78: Command Injection**
- NEVER: `do shell script userInput`
- ALWAYS: Escape with `quoted form of`, validate inputs

**CWE-732: Permission Escalation**
- NEVER: Unnecessary `administrator privileges`
- ALWAYS: Minimal permissions, prompt only when needed

### 0.3 Risk Level: MEDIUM

**Verification requirements for MEDIUM risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 Script Injection Prevention (CWE-94)

**Principle:** Never construct AppleScript from untrusted data. Use JXA with proper escaping.

```applescript
-- ❌ WRONG - Script injection vulnerability
set userInput to "test\" & (do shell script \"rm -rf ~\") & \""
do shell script "echo " & userInput

-- ✅ CORRECT - Use quoted form
set userInput to "untrusted data"
do shell script "echo " & quoted form of userInput
```

```javascript
// ❌ WRONG - JXA injection
const app = Application.currentApplication();
app.doShellScript(`echo ${userInput}`);

// ✅ CORRECT - JXA with proper escaping
const app = Application.currentApplication();
const escapedInput = userInput.replace(/'/g, "'\\''");
app.doShellScript(`echo '${escapedInput}'`);
```

### 1.2 Application Scripting Safety (CWE-20)

**Principle:** Validate application availability and permissions before automation.

```javascript
// ❌ WRONG - No permission check
const finder = Application('Finder');
finder.selection();

// ✅ CORRECT - Check application with permission handling
function getApp(name) {
  try {
    const app = Application(name);
    app.includeStandardAdditions = true;
    // Test accessibility
    app.name();
    return app;
  } catch (e) {
    throw new Error(`Cannot access ${name}: ${e.message}`);
  }
}
```

### 1.3 File Path Validation (CWE-22)

**Principle:** Validate all paths. Use POSIX paths with proper expansion.

```javascript
// ❌ WRONG - Path traversal possible
const file = `${userDir}/${filename}`;

// ✅ CORRECT - Validate path bounds
function safePath(basePath, filename) {
  const ObjC = $.NSString.alloc;
  const base = ObjC.initWithString(basePath).stringByStandardizingPath.js;
  const full = ObjC.initWithString(`${basePath}/${filename}`)
    .stringByStandardizingPath.js;

  if (!full.startsWith(base)) {
    throw new Error('Path traversal detected');
  }
  return full;
}
```

### 1.4 Secrets ≠ Code (CWE-798)

**Principle:** Use Keychain for secrets. Never hardcode credentials.

### 1.5 Privilege Escalation (CWE-269)

**Principle:** Avoid `with administrator privileges` unless absolutely necessary.

### 1.6 Shell Command Safety (CWE-78)

**Principle:** Always use `quoted form of` for shell arguments.

---

## 2. Version Requirements

**ALWAYS use these minimum versions:**

```
macOS: 10.15+ (Catalina) for JXA stability
osascript: System default
JavaScript for Automation (JXA): Preferred over AppleScript
```

**Recommended:** Use JXA (JavaScript for Automation) over AppleScript for better error handling and modern syntax.

---

## 3. Code Patterns

### 3.1 WHEN creating JXA applications

```javascript
#!/usr/bin/env osascript -l JavaScript

// ❌ WRONG - No error handling, global pollution
Application('Finder').selection();

// ✅ CORRECT - Proper JXA structure
function run(argv) {
  'use strict';

  ObjC.import('Foundation');

  const app = Application.currentApplication();
  app.includeStandardAdditions = true;

  try {
    return main(argv);
  } catch (e) {
    console.log(`Error: ${e.message}`);
    return 1;
  }
}

function main(argv) {
  // Parse arguments safely
  const config = parseArgs(argv);

  // Validate inputs
  if (!config.valid) {
    throw new Error(`Invalid arguments: ${config.error}`);
  }

  // Execute with proper error handling
  return execute(config);
}

function parseArgs(argv) {
  if (argv.length < 1) {
    return { valid: false, error: 'Missing required argument' };
  }

  return {
    valid: true,
    input: argv[0],
  };
}
```

### 3.2 WHEN automating Finder operations

```javascript
// ❌ WRONG - No validation, unsafe operations
const finder = Application('Finder');
finder.delete(finder.selection());

// ✅ CORRECT - Safe Finder automation
function safeFinderOperation(operation) {
  const finder = Application('Finder');
  finder.includeStandardAdditions = true;

  const selection = finder.selection();

  if (selection.length === 0) {
    throw new Error('No items selected');
  }

  // Validate items before operation
  const items = selection.map(item => {
    const path = decodeURI(item.url()).replace('file://', '');

    // Prevent operations on system directories
    const protectedPaths = ['/System', '/Library', '/usr', '/bin', '/sbin'];
    if (protectedPaths.some(p => path.startsWith(p))) {
      throw new Error(`Cannot operate on protected path: ${path}`);
    }

    return { item, path };
  });

  // Execute operation
  return items.map(({ item, path }) => {
    try {
      return operation(finder, item, path);
    } catch (e) {
      return { path, error: e.message };
    }
  });
}

// Usage
const results = safeFinderOperation((finder, item, path) => {
  // Move to trash instead of delete
  finder.delete(item);
  return { path, success: true };
});
```

### 3.3 WHEN executing shell commands

```javascript
// ❌ WRONG - Command injection vulnerability
function runCommand(input) {
  const app = Application.currentApplication();
  return app.doShellScript(`echo ${input}`);
}

// ✅ CORRECT - Safe shell command execution
function safeShellCommand(command, args = [], options = {}) {
  const app = Application.currentApplication();
  app.includeStandardAdditions = true;

  // Escape arguments
  const escapedArgs = args.map(arg => {
    if (typeof arg !== 'string') {
      throw new Error('Arguments must be strings');
    }
    // Use single quotes with escaped single quotes inside
    return `'${arg.replace(/'/g, "'\\''")}'`;
  });

  // Build command safely
  const fullCommand = [command, ...escapedArgs].join(' ');

  // Execute with options
  const shellOptions = {};

  if (options.asAdmin) {
    shellOptions.administratorPrivileges = true;
  }

  if (options.timeout) {
    // JXA doesn't support timeout natively, use timeout command
    return app.doShellScript(
      `timeout ${options.timeout} ${fullCommand}`,
      shellOptions
    );
  }

  return app.doShellScript(fullCommand, shellOptions);
}

// Usage
const output = safeShellCommand('grep', ['-r', searchTerm, directory]);
```

### 3.4 WHEN working with Keychain

```javascript
// ❌ WRONG - Hardcoded credentials
const password = 'secret123';

// ✅ CORRECT - Use Keychain for secrets
function getKeychainPassword(service, account) {
  const app = Application.currentApplication();
  app.includeStandardAdditions = true;

  try {
    // Use security command to access keychain
    const cmd = `/usr/bin/security find-generic-password -s '${
      service.replace(/'/g, "'\\''")
    }' -a '${
      account.replace(/'/g, "'\\''")
    }' -w`;

    return app.doShellScript(cmd);
  } catch (e) {
    throw new Error(`Keychain access failed: ${e.message}`);
  }
}

function setKeychainPassword(service, account, password) {
  const app = Application.currentApplication();
  app.includeStandardAdditions = true;

  // Delete existing entry first (ignore errors)
  try {
    safeShellCommand('/usr/bin/security', [
      'delete-generic-password',
      '-s', service,
      '-a', account,
    ]);
  } catch (e) {
    // Entry may not exist
  }

  // Add new entry
  return safeShellCommand('/usr/bin/security', [
    'add-generic-password',
    '-s', service,
    '-a', account,
    '-w', password,
    '-U',  // Update if exists
  ]);
}
```

### 3.5 WHEN using Objective-C bridge

```javascript
// ❌ WRONG - No memory management awareness
function processFiles(paths) {
  paths.forEach(path => {
    const data = $.NSData.dataWithContentsOfFile(path);
    // Memory leak potential
  });
}

// ✅ CORRECT - Proper ObjC bridge usage
function processFilesSafely(paths) {
  ObjC.import('Foundation');

  return paths.map(path => {
    // Use autoreleasepool for memory management
    const pool = $.NSAutoreleasePool.alloc.init;

    try {
      const nsPath = $.NSString.alloc.initWithUTF8String(path);
      const fileManager = $.NSFileManager.defaultManager;

      // Check file exists
      if (!fileManager.fileExistsAtPath(nsPath)) {
        return { path, error: 'File not found' };
      }

      // Read file safely
      const data = $.NSData.dataWithContentsOfFile(nsPath);
      if (data.isNil()) {
        return { path, error: 'Could not read file' };
      }

      // Convert to string
      const content = $.NSString.alloc
        .initWithDataEncoding(data, $.NSUTF8StringEncoding).js;

      return { path, content, size: data.length };
    } finally {
      pool.drain;
    }
  });
}
```

### 3.6 WHEN creating dialogs and user interaction

```javascript
// ❌ WRONG - No input validation from dialogs
const app = Application.currentApplication();
const input = app.displayDialog('Enter value:').textReturned;
executeCommand(input);

// ✅ CORRECT - Validate dialog input
function getValidatedInput(prompt, validator) {
  const app = Application.currentApplication();
  app.includeStandardAdditions = true;

  const maxAttempts = 3;

  for (let i = 0; i < maxAttempts; i++) {
    try {
      const result = app.displayDialog(prompt, {
        defaultAnswer: '',
        buttons: ['Cancel', 'OK'],
        defaultButton: 'OK',
        cancelButton: 'Cancel',
        withTitle: 'Input Required',
        hiddenAnswer: false,
      });

      const input = result.textReturned.trim();

      // Validate input
      const validation = validator(input);
      if (validation.valid) {
        return validation.value;
      }

      // Show error and retry
      app.displayAlert('Invalid Input', {
        message: validation.error,
        as: 'warning',
      });
    } catch (e) {
      // User cancelled
      if (e.errorNumber === -128) {
        return null;
      }
      throw e;
    }
  }

  throw new Error('Maximum input attempts exceeded');
}

// Usage
const filename = getValidatedInput('Enter filename:', input => {
  if (!input) {
    return { valid: false, error: 'Filename cannot be empty' };
  }
  if (!/^[\w\-. ]+$/.test(input)) {
    return { valid: false, error: 'Invalid characters in filename' };
  }
  if (input.includes('..')) {
    return { valid: false, error: 'Path traversal not allowed' };
  }
  return { valid: true, value: input };
});
```

---

## 4. Anti-Patterns

**NEVER:**
- Use `do shell script` without `quoted form of`
- Construct AppleScript strings from user input
- Use `with administrator privileges` unnecessarily
- Store credentials in scripts
- Ignore errors from application calls
- Use `eval()` or dynamic script generation
- Access system paths without validation

---

## 5. Testing

**ALWAYS write tests for automation scripts:**

```javascript
// Test framework for JXA
function runTests() {
  const tests = [
    testSafePathValidation,
    testShellCommandEscaping,
    testInputValidation,
    testApplicationAccess,
  ];

  const results = tests.map(test => {
    try {
      test();
      return { name: test.name, passed: true };
    } catch (e) {
      return { name: test.name, passed: false, error: e.message };
    }
  });

  const passed = results.filter(r => r.passed).length;
  console.log(`Tests: ${passed}/${results.length} passed`);

  results.filter(r => !r.passed).forEach(r => {
    console.log(`FAILED: ${r.name} - ${r.error}`);
  });

  return results.every(r => r.passed);
}

function testSafePathValidation() {
  // Test path traversal prevention
  try {
    safePath('/Users/test', '../../../etc/passwd');
    throw new Error('Should have thrown');
  } catch (e) {
    if (!e.message.includes('traversal')) {
      throw new Error('Wrong error type');
    }
  }
}

function testShellCommandEscaping() {
  // Test that special characters are escaped
  const result = safeShellCommand('echo', ["test'; rm -rf /; echo '"]);
  if (result.includes('rm -rf')) {
    throw new Error('Command injection possible');
  }
}
```

---

## 6. Pre-Generation Checklist

**BEFORE generating any AppleScript/JXA code:**

- [ ] Using JXA instead of AppleScript where possible
- [ ] Shell commands use `quoted form of` or proper escaping
- [ ] No string concatenation with user input
- [ ] Paths validated against traversal
- [ ] Keychain used for credentials
- [ ] Application permissions verified before access
- [ ] Error handling for all operations
- [ ] Protected paths checked before file operations
- [ ] `administrator privileges` justified if used
- [ ] Input validation for all dialogs

---

**Performance**: Quality over speed. Verify all code examples compile. Never skip security checks. See `template-references/performance-notes.md` for full guidelines.