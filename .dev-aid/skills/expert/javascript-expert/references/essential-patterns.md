## 6. Essential Patterns

### Pattern 1: Async Error Handling

```javascript
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
```

### Pattern 2: XSS Prevention

```javascript
// SAFE: Use textContent for plain text
function displayUserComment(comment) {
    document.getElementById('comment').textContent = comment;
}

// SAFE: Sanitize HTML if needed
import DOMPurify from 'dompurify';

function displayUserComment(comment) {
    const clean = DOMPurify.sanitize(comment, {
        ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a'],
        ALLOWED_ATTR: ['href']
    });
    document.getElementById('comment').innerHTML = clean;
}
```

### Pattern 3: Prototype Pollution Prevention

```javascript
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
```

### Pattern 4: Parallel Async Operations

```javascript
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

### Pattern 5: Event Delegation

```javascript
// EFFICIENT: Event delegation
function setupItemListeners() {
    const container = document.getElementById('item-container');

    container.addEventListener('click', (e) => {
        const item = e.target.closest('.item');
        if (item) {
            console.log('Clicked:', item.dataset.id);
        }
    });
}

// IMPORTANT: Clean up event listeners
class ItemManager {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.handleClick = this.handleClick.bind(this);
        this.container.addEventListener('click', this.handleClick);
    }

    handleClick(e) {
        const item = e.target.closest('.item');
        if (item) {
            this.processItem(item);
        }
    }

    processItem(item) {
        console.log('Processing:', item.dataset.id);
    }

    destroy() {
        this.container.removeEventListener('click', this.handleClick);
    }
}
```

---

