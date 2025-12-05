# JavaScript Anti-Patterns

Common mistakes to avoid in JavaScript development.

---

## Mistake 1: Unhandled Promise Rejections

```javascript
// DON'T
fetch('/api/data').then(res => res.json());

// DO
fetch('/api/data')
    .then(res => res.json())
    .catch(err => console.error('Failed:', err));

// BETTER
async function getData() {
    try {
        const res = await fetch('/api/data');
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        return await res.json();
    } catch (error) {
        console.error('Failed to fetch data:', error);
        throw error;
    }
}
```

**Why it's bad**: Silent failures make debugging impossible. Always handle promise rejections.

---

## Mistake 2: Memory Leaks from Event Listeners

```javascript
// DON'T
function setupWidget() {
    const button = document.getElementById('btn');
    button.addEventListener('click', handleClick);
}

// DO
function setupWidget() {
    const button = document.getElementById('btn');
    const handleClick = () => { /* ... */ };
    button.addEventListener('click', handleClick);

    return {
        destroy() {
            button.removeEventListener('click', handleClick);
        }
    };
}

// BETTER: Using class
class Widget {
    constructor(buttonId) {
        this.button = document.getElementById(buttonId);
        this.handleClick = this.handleClick.bind(this);
        this.button.addEventListener('click', this.handleClick);
    }

    handleClick() {
        // Handler logic
    }

    destroy() {
        this.button.removeEventListener('click', this.handleClick);
    }
}
```

**Why it's bad**: Event listeners hold references to DOM elements and closures, preventing garbage collection.

---

## Mistake 3: Using var

```javascript
// DON'T
for (var i = 0; i < 5; i++) {
    setTimeout(() => console.log(i), 100);
}
// Prints: 5, 5, 5, 5, 5

// DO
for (let i = 0; i < 5; i++) {
    setTimeout(() => console.log(i), 100);
}
// Prints: 0, 1, 2, 3, 4

// BETTER: Use const by default
const items = [1, 2, 3, 4, 5];
items.forEach((item, i) => {
    setTimeout(() => console.log(i), 100);
});
```

**Why it's bad**: `var` has function scope and hoisting behavior that leads to bugs. Use `const` by default, `let` when reassignment is needed.

---

## Mistake 4: Loose Equality

```javascript
// DON'T
if (value == '0') { }
if (items.length == 0) { }
if (user.age == 18) { }

// DO
if (value === '0') { }
if (items.length === 0) { }
if (user.age === 18) { }
```

**Why it's bad**: `==` performs type coercion, leading to unexpected results:
- `'' == 0` → true
- `null == undefined` → true
- `'0' == false` → true

---

## Mistake 5: Blocking Event Loop

```javascript
// DON'T
function processLargeData(data) {
    for (let i = 0; i < 1000000; i++) {
        complexCalculation(data[i]);
    }
}

// DO: Use Web Worker
const worker = new Worker('processor.js');
worker.postMessage(data);
worker.onmessage = (e) => {
    const results = e.data;
};

// DO: Break into chunks
async function processLargeData(data, chunkSize = 1000) {
    for (let i = 0; i < data.length; i += chunkSize) {
        const chunk = data.slice(i, i + chunkSize);
        await processChunk(chunk);
        // Allow event loop to process other tasks
        await new Promise(resolve => setTimeout(resolve, 0));
    }
}
```

**Why it's bad**: Long-running synchronous code freezes the UI and prevents other operations.

---

## Mistake 6: Mutating Function Arguments

```javascript
// DON'T
function addItem(array, item) {
    array.push(item);
    return array;
}

// DO
function addItem(array, item) {
    return [...array, item];
}

// DON'T
function updateUser(user, updates) {
    Object.assign(user, updates);
    return user;
}

// DO
function updateUser(user, updates) {
    return { ...user, ...updates };
}
```

**Why it's bad**: Mutating arguments leads to unexpected side effects and makes code harder to reason about.

---

## Mistake 7: Not Validating User Input

```javascript
// DON'T
function createUser(data) {
    return {
        id: generateId(),
        email: data.email,
        age: data.age
    };
}

// DO
function createUser(data) {
    if (!data || typeof data !== 'object') {
        throw new TypeError('Invalid data');
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(data.email)) {
        throw new Error('Invalid email format');
    }

    const age = Number(data.age);
    if (isNaN(age) || age < 0 || age > 150) {
        throw new Error('Invalid age');
    }

    return {
        id: generateId(),
        email: data.email.toLowerCase().trim(),
        age: age
    };
}
```

**Why it's bad**: Unvalidated input leads to bugs, crashes, and security vulnerabilities.

---

## Mistake 8: Swallowing Errors

```javascript
// DON'T
try {
    dangerousOperation();
} catch (error) {
    // Silent failure
}

// DON'T
promise.catch(() => {}); // Swallowing error

// DO
try {
    dangerousOperation();
} catch (error) {
    console.error('Operation failed:', error);
    throw error; // Re-throw if caller should handle
}

// DO
promise.catch((error) => {
    console.error('Promise failed:', error);
    // Handle or re-throw
    throw error;
});
```

**Why it's bad**: Swallowing errors hides bugs and makes debugging impossible.

---

## Mistake 9: Using eval() or Function Constructor

```javascript
// DON'T
const code = getUserInput();
eval(code); // DANGEROUS!

// DON'T
const fn = new Function('return ' + getUserInput()); // DANGEROUS!

// DO
// Use safe alternatives like JSON.parse for data
const data = JSON.parse(userInput);

// DO
// Use sandboxed environments for user code
const vm = require('vm');
const sandbox = { console, result: null };
vm.createContext(sandbox);
vm.runInContext(userCode, sandbox, { timeout: 1000 });
```

**Why it's bad**: `eval()` executes arbitrary code, creating major security vulnerabilities and performance issues.

---

## Mistake 10: Not Using Strict Mode

```javascript
// DON'T
function badFunction() {
    x = 10; // Creates global variable
    return x;
}

// DO
'use strict';

function goodFunction() {
    // x = 10; // ReferenceError in strict mode
    const x = 10;
    return x;
}

// BETTER: ES6 modules are automatically in strict mode
export function modernFunction() {
    // Already in strict mode
    const x = 10;
    return x;
}
```

**Why it's bad**: Non-strict mode allows dangerous behaviors like implicit globals and silent failures.

---

## Mistake 11: Inefficient String Concatenation

```javascript
// DON'T
let html = '';
for (let i = 0; i < 1000; i++) {
    html += '<div>' + items[i] + '</div>';
}

// DO
const html = items.map(item => `<div>${item}</div>`).join('');

// BETTER: Use template literals
const html = items.map(item => `
    <div class="item">
        ${item.name}
    </div>
`).join('');
```

**Why it's bad**: String concatenation in loops creates many intermediate strings, wasting memory and CPU.

---

## Mistake 12: Not Using Optional Chaining

```javascript
// DON'T
const userName = user && user.profile && user.profile.name;
const firstPost = user && user.posts && user.posts[0];

// DO
const userName = user?.profile?.name;
const firstPost = user?.posts?.[0];

// BETTER: With nullish coalescing
const userName = user?.profile?.name ?? 'Anonymous';
const postCount = user?.posts?.length ?? 0;
```

**Why it's bad**: Verbose null checking makes code harder to read and more error-prone.

---

## Summary: Never Do

1. Leave promises without `.catch()` or try/catch
2. Use `var` - always use `const` or `let`
3. Use loose equality (`==`) - always use strict (`===`)
4. Block the event loop with long operations
5. Mutate function arguments
6. Skip input validation
7. Swallow errors silently
8. Use `eval()` or `Function()` constructor with user input
9. Forget to clean up event listeners
10. Use `Math.random()` for security purposes
11. Store sensitive data in localStorage without encryption
12. Trust user input without sanitization

## Summary: Always Do

1. Handle all errors explicitly
2. Use `const` by default, `let` when needed
3. Use strict equality (`===`)
4. Validate and sanitize user input
5. Use async/await for cleaner async code
6. Clean up resources (listeners, intervals, workers)
7. Use modern ES6+ features (optional chaining, nullish coalescing)
8. Profile performance with DevTools
9. Write tests for critical functionality
10. Use TypeScript or JSDoc for type safety
