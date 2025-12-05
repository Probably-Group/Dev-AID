# JavaScript Security Examples

## 1. XSS Prevention

### Pattern: Preventing XSS Attacks

**When to use**: Any time handling user input for DOM manipulation

```javascript
// DANGEROUS: Direct innerHTML with user input (XSS vulnerability)
function displayUserComment(comment) {
    document.getElementById('comment').innerHTML = comment;
}

// SAFE: Use textContent for plain text
function displayUserComment(comment) {
    document.getElementById('comment').textContent = comment;
}

// SAFE: Sanitize HTML if HTML content is needed
import DOMPurify from 'dompurify';

function displayUserComment(comment) {
    const clean = DOMPurify.sanitize(comment, {
        ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a'],
        ALLOWED_ATTR: ['href']
    });
    document.getElementById('comment').innerHTML = clean;
}

// SAFE: Use createElement for dynamic elements
function createUserCard(user) {
    const card = document.createElement('div');
    card.className = 'user-card';

    const name = document.createElement('h3');
    name.textContent = user.name;

    const email = document.createElement('p');
    email.textContent = user.email;

    card.appendChild(name);
    card.appendChild(email);

    return card;
}
```

---

## 2. Prototype Pollution Prevention

**When to use**: Handling object merging, user-controlled keys

```javascript
// DANGEROUS: Prototype pollution vulnerability
function merge(target, source) {
    for (let key in source) {
        target[key] = source[key];
    }
    return target;
}

// SAFE: Check for prototype pollution
function merge(target, source) {
    for (let key in source) {
        if (Object.prototype.hasOwnProperty.call(source, key)) {
            if (key === '__proto__' || key === 'constructor' || key === 'prototype') {
                continue;
            }
            target[key] = source[key];
        }
    }
    return target;
}

// BETTER: Use Object.assign or spread operator
function merge(target, source) {
    return Object.assign({}, target, source);
}

// BEST: Use Object.create(null) for maps
function createSafeMap() {
    return Object.create(null);
}
```

---

## 3. Critical Vulnerabilities

### 3.1 Cross-Site Scripting (XSS)

- Always use `textContent` over `innerHTML` for user content
- Sanitize HTML with DOMPurify if HTML rendering is required
- Set Content Security Policy headers

### 3.2 Prototype Pollution

- Never trust user-controlled object keys
- Blacklist `__proto__`, `constructor`, `prototype`
- Use Object.assign() or spread operator for safe merging

### 3.3 Regular Expression Denial of Service (ReDoS)

- Avoid catastrophic backtracking patterns
- Test regex with long inputs
- Implement timeout for user-provided regex

```javascript
// DANGEROUS: Catastrophic backtracking
const badRegex = /^(a+)+$/;

// SAFE: Linear time complexity
const goodRegex = /^a+$/;

// SAFE: Timeout protection
function safeRegexTest(pattern, str, timeout = 1000) {
    return new Promise((resolve, reject) => {
        const worker = new Worker('regex-worker.js');

        const timer = setTimeout(() => {
            worker.terminate();
            reject(new Error('Regex timeout'));
        }, timeout);

        worker.onmessage = (e) => {
            clearTimeout(timer);
            worker.terminate();
            resolve(e.data);
        };

        worker.postMessage({ pattern, str });
    });
}
```

### 3.4 Insecure Randomness

- Never use Math.random() for security (tokens, session IDs)
- Use crypto.randomBytes() in Node.js
- Use crypto.getRandomValues() in browsers

```javascript
// DANGEROUS: Predictable tokens
function generateToken() {
    return Math.random().toString(36).substring(2);
}

// SAFE: Cryptographically secure (Node.js)
const crypto = require('crypto');

function generateToken() {
    return crypto.randomBytes(32).toString('hex');
}

// SAFE: Cryptographically secure (Browser)
function generateToken() {
    const array = new Uint8Array(32);
    crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
}
```

### 3.5 Dependency Vulnerabilities

- Run npm audit before every deployment
- Use Dependabot or Snyk for continuous monitoring
- Keep dependencies up to date

```bash
# Check for vulnerabilities
npm audit

# Fix automatically (be careful!)
npm audit fix

# View detailed report
npm audit --json

# Check for outdated packages
npm outdated
```

---

## 4. OWASP Top 10 2025 Mapping

| OWASP ID | Category | Risk | Quick Mitigation |
|----------|----------|------|------------------|
| A01:2025 | Broken Access Control | Critical | Server-side validation |
| A02:2025 | Security Misconfiguration | High | Secure headers, disable debug |
| A03:2025 | Supply Chain Failures | High | npm audit, lock files |
| A04:2025 | Insecure Design | Medium | Threat modeling |
| A05:2025 | Identification & Auth | Critical | httpOnly cookies |
| A06:2025 | Vulnerable Components | High | Dependency scanning |
| A07:2025 | Cryptographic Failures | Critical | Use crypto module |
| A08:2025 | Injection | Critical | Sanitize inputs |
| A09:2025 | Logging Failures | Medium | Structured logging |
| A10:2025 | Exception Handling | Medium | Proper error handling |

---

## 5. Secure Authentication

```javascript
// DON'T: Store tokens in localStorage (XSS vulnerable)
localStorage.setItem('token', authToken);

// DO: Use httpOnly cookies
// Server-side (Express example)
app.post('/login', (req, res) => {
    const token = generateToken(user);

    res.cookie('auth_token', token, {
        httpOnly: true,
        secure: true, // HTTPS only
        sameSite: 'strict',
        maxAge: 3600000 // 1 hour
    });

    res.json({ success: true });
});

// DO: If localStorage is necessary, encrypt sensitive data
import CryptoJS from 'crypto-js';

function secureStorage(key, value, secret) {
    const encrypted = CryptoJS.AES.encrypt(value, secret).toString();
    localStorage.setItem(key, encrypted);
}

function getSecureStorage(key, secret) {
    const encrypted = localStorage.getItem(key);
    if (!encrypted) return null;

    const bytes = CryptoJS.AES.decrypt(encrypted, secret);
    return bytes.toString(CryptoJS.enc.Utf8);
}
```

---

## 6. Input Validation

```javascript
// Validate user input
function validateEmail(email) {
    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function sanitizeInput(input) {
    // Remove dangerous characters
    return input
        .replace(/[<>]/g, '') // Remove angle brackets
        .replace(/['"]/g, '') // Remove quotes
        .trim();
}

// Validate and sanitize together
function processUserInput(input) {
    if (typeof input !== 'string') {
        throw new TypeError('Input must be a string');
    }

    if (input.length > 1000) {
        throw new RangeError('Input too long');
    }

    return sanitizeInput(input);
}
```

---

## 7. Security Checklist

Before deploying JavaScript code:

- [ ] All user inputs validated and sanitized
- [ ] No `eval()` or `Function()` with user input
- [ ] XSS protection in place (textContent or DOMPurify)
- [ ] Prototype pollution checks in object operations
- [ ] Secure randomness for tokens (crypto module)
- [ ] httpOnly cookies for auth tokens
- [ ] Content Security Policy headers configured
- [ ] npm audit run and vulnerabilities fixed
- [ ] Dependencies up to date
- [ ] No sensitive data in client-side code
- [ ] HTTPS enforced in production
- [ ] Input length limits enforced
- [ ] Error messages don't leak sensitive info
