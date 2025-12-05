# Async Patterns in JavaScript

## Pattern 1: Async/Await Error Handling

**When to use**: All asynchronous operations

```javascript
// DANGEROUS: Unhandled promise rejection
async function fetchUser(id) {
    const response = await fetch(`/api/users/${id}`);
    return response.json();
}

// SAFE: Proper error handling
async function fetchUser(id) {
    try {
        const response = await fetch(`/api/users/${id}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return { success: true, data };
    } catch (error) {
        console.error('Failed to fetch user:', error);
        return { success: false, error: error.message };
    }
}

// BETTER: Custom error types
class APIError extends Error {
    constructor(message, statusCode) {
        super(message);
        this.name = 'APIError';
        this.statusCode = statusCode;
    }
}

async function fetchUser(id) {
    try {
        const response = await fetch(`/api/users/${id}`);

        if (!response.ok) {
            throw new APIError(
                `Failed to fetch user: ${response.statusText}`,
                response.status
            );
        }

        return await response.json();
    } catch (error) {
        if (error instanceof APIError) {
            throw error;
        }
        throw new Error(`Network error: ${error.message}`);
    }
}
```

---

## Pattern 2: Proper Promise Handling

**When to use**: Managing multiple async operations

```javascript
// SLOW: Sequential execution
async function loadUserData(userId) {
    const user = await fetchUser(userId);
    const posts = await fetchUserPosts(userId);
    const comments = await fetchUserComments(userId);
    return { user, posts, comments };
}

// FAST: Parallel execution with Promise.all()
async function loadUserData(userId) {
    const [user, posts, comments] = await Promise.all([
        fetchUser(userId),
        fetchUserPosts(userId),
        fetchUserComments(userId)
    ]);
    return { user, posts, comments };
}

// RESILIENT: Promise.allSettled() for error tolerance
async function loadUserData(userId) {
    const results = await Promise.allSettled([
        fetchUser(userId),
        fetchUserPosts(userId),
        fetchUserComments(userId)
    ]);

    return {
        user: results[0].status === 'fulfilled' ? results[0].value : null,
        posts: results[1].status === 'fulfilled' ? results[1].value : [],
        comments: results[2].status === 'fulfilled' ? results[2].value : [],
        errors: results.filter(r => r.status === 'rejected').map(r => r.reason)
    };
}
```

---

## Pattern 3: Promise Composition

**When to use**: Chaining dependent async operations

```javascript
// Basic promise chaining
function processUserData(userId) {
    return fetchUser(userId)
        .then(user => enrichUserData(user))
        .then(enriched => validateUserData(enriched))
        .then(validated => saveUserData(validated))
        .catch(error => {
            console.error('Pipeline failed:', error);
            throw error;
        });
}

// With async/await
async function processUserData(userId) {
    try {
        const user = await fetchUser(userId);
        const enriched = await enrichUserData(user);
        const validated = await validateUserData(enriched);
        return await saveUserData(validated);
    } catch (error) {
        console.error('Pipeline failed:', error);
        throw error;
    }
}
```

---

## Pattern 4: Timeout and Cancellation

**When to use**: Long-running operations that need limits

```javascript
// Timeout wrapper
function withTimeout(promise, ms) {
    const timeout = new Promise((_, reject) =>
        setTimeout(() => reject(new Error('Operation timed out')), ms)
    );
    return Promise.race([promise, timeout]);
}

// Usage
try {
    const data = await withTimeout(fetchData(), 5000);
} catch (error) {
    if (error.message === 'Operation timed out') {
        console.error('Request took too long');
    }
}

// AbortController for fetch cancellation
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 5000);

try {
    const response = await fetch('/api/data', {
        signal: controller.signal
    });
    clearTimeout(timeoutId);
    return await response.json();
} catch (error) {
    if (error.name === 'AbortError') {
        console.error('Request was aborted');
    }
    throw error;
}
```

---

## Pattern 5: Retry Logic

**When to use**: Unreliable network operations

```javascript
async function retry(fn, maxAttempts = 3, delay = 1000) {
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
        try {
            return await fn();
        } catch (error) {
            if (attempt === maxAttempts) {
                throw error;
            }

            console.log(`Attempt ${attempt} failed, retrying in ${delay}ms...`);
            await new Promise(resolve => setTimeout(resolve, delay));

            // Exponential backoff
            delay *= 2;
        }
    }
}

// Usage
const data = await retry(() => fetchData(), 3, 1000);
```

---

## Pattern 6: Queue and Rate Limiting

**When to use**: Managing API rate limits

```javascript
class AsyncQueue {
    constructor(concurrency = 1) {
        this.concurrency = concurrency;
        this.running = 0;
        this.queue = [];
    }

    async add(fn) {
        while (this.running >= this.concurrency) {
            await new Promise(resolve => this.queue.push(resolve));
        }

        this.running++;
        try {
            return await fn();
        } finally {
            this.running--;
            const resolve = this.queue.shift();
            if (resolve) resolve();
        }
    }
}

// Usage
const queue = new AsyncQueue(3); // Max 3 concurrent requests

const results = await Promise.all(
    urls.map(url => queue.add(() => fetch(url)))
);
```

---

## Anti-Pattern: Unhandled Promise Rejections

```javascript
// DON'T: Silent failure
fetch('/api/data').then(res => res.json());

// DO: Always handle rejections
fetch('/api/data')
    .then(res => res.json())
    .catch(err => console.error('Failed:', err));

// DO: With async/await
async function getData() {
    try {
        const res = await fetch('/api/data');
        return await res.json();
    } catch (error) {
        console.error('Failed:', error);
        throw error;
    }
}
```
