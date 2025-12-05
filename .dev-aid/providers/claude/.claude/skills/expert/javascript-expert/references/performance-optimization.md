# JavaScript Performance Optimization

## Pattern 1: Memoization

**When to use**: Expensive pure functions called multiple times with same arguments

```javascript
// Bad: Recalculates every time
function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

// Good: Memoized version
function memoize(fn) {
    const cache = new Map();
    return function(...args) {
        const key = JSON.stringify(args);
        if (cache.has(key)) {
            return cache.get(key);
        }
        const result = fn.apply(this, args);
        cache.set(key, result);
        return result;
    };
}

const fibonacciMemo = memoize(function(n) {
    if (n <= 1) return n;
    return fibonacciMemo(n - 1) + fibonacciMemo(n - 2);
});

// Good: React-style useMemo pattern
function expensiveCalculation(data) {
    // Cache based on data reference
    if (expensiveCalculation.lastData === data) {
        return expensiveCalculation.lastResult;
    }

    const result = data.reduce((acc, item) => {
        // Complex calculation
        return acc + complexOperation(item);
    }, 0);

    expensiveCalculation.lastData = data;
    expensiveCalculation.lastResult = result;
    return result;
}
```

---

## Pattern 2: Debounce and Throttle

**When to use**: Frequent events like scroll, resize, input

```javascript
// Debounce: Execute after delay when events stop
function debounce(fn, delay) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn.apply(this, args), delay);
    };
}

// Good: Debounced search
const searchInput = document.getElementById('search');
const debouncedSearch = debounce(async (query) => {
    const results = await fetchSearchResults(query);
    displayResults(results);
}, 300);

searchInput.addEventListener('input', (e) => {
    debouncedSearch(e.target.value);
});

// Throttle: Execute at most once per interval
function throttle(fn, interval) {
    let lastTime = 0;
    return function(...args) {
        const now = Date.now();
        if (now - lastTime >= interval) {
            lastTime = now;
            fn.apply(this, args);
        }
    };
}

// Good: Throttled scroll handler
const throttledScroll = throttle(() => {
    updateScrollPosition();
}, 100);

window.addEventListener('scroll', throttledScroll);
```

---

## Pattern 3: Lazy Loading

**When to use**: Large modules, images, or data not needed immediately

```javascript
// Bad: Import everything upfront
import { heavyChartLibrary } from 'chart-lib';
import { pdfGenerator } from 'pdf-lib';

// Good: Dynamic imports
async function showChart(data) {
    const { heavyChartLibrary } = await import('chart-lib');
    return heavyChartLibrary.render(data);
}

// Good: Lazy load images with Intersection Observer
function lazyLoadImages() {
    const images = document.querySelectorAll('img[data-src]');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => observer.observe(img));
}

// Good: Lazy load data on scroll
class InfiniteScroll {
    constructor(container, loadMore) {
        this.container = container;
        this.loadMore = loadMore;
        this.loading = false;

        this.observer = new IntersectionObserver(
            (entries) => this.handleIntersect(entries),
            { rootMargin: '100px' }
        );

        this.observer.observe(this.container.lastElementChild);
    }

    async handleIntersect(entries) {
        if (entries[0].isIntersecting && !this.loading) {
            this.loading = true;
            await this.loadMore();
            this.loading = false;
            this.observer.observe(this.container.lastElementChild);
        }
    }
}
```

---

## Pattern 4: Web Workers

**When to use**: CPU-intensive tasks that would block the main thread

```javascript
// Bad: Blocking the main thread
function processLargeDataset(data) {
    return data.map(item => expensiveOperation(item));
}

// Good: Offload to Web Worker
// worker.js
self.onmessage = function(e) {
    const { data, operation } = e.data;

    let result;
    switch (operation) {
        case 'sort':
            result = data.sort((a, b) => a.value - b.value);
            break;
        case 'filter':
            result = data.filter(item => item.active);
            break;
        case 'transform':
            result = data.map(item => expensiveTransform(item));
            break;
    }

    self.postMessage(result);
};

// main.js
class DataProcessor {
    constructor() {
        this.worker = new Worker('worker.js');
    }

    process(data, operation) {
        return new Promise((resolve, reject) => {
            this.worker.onmessage = (e) => resolve(e.data);
            this.worker.onerror = (e) => reject(e);
            this.worker.postMessage({ data, operation });
        });
    }

    terminate() {
        this.worker.terminate();
    }
}

// Usage
const processor = new DataProcessor();
const sortedData = await processor.process(largeArray, 'sort');
```

---

## Pattern 5: Efficient DOM Operations

**When to use**: Any DOM manipulation, especially in loops

```javascript
// Bad: Multiple reflows
function addItems(items) {
    const container = document.getElementById('list');
    items.forEach(item => {
        const li = document.createElement('li');
        li.textContent = item.name;
        container.appendChild(li); // Reflow on each append
    });
}

// Good: Use DocumentFragment
function addItems(items) {
    const container = document.getElementById('list');
    const fragment = document.createDocumentFragment();

    items.forEach(item => {
        const li = document.createElement('li');
        li.textContent = item.name;
        fragment.appendChild(li);
    });

    container.appendChild(fragment); // Single reflow
}

// Good: Batch style changes
function updateStyles(elements, styles) {
    // Bad: Multiple reflows
    // elements.forEach(el => {
    //     el.style.width = styles.width;
    //     el.style.height = styles.height;
    //     el.style.margin = styles.margin;
    // });

    // Good: Use CSS class
    elements.forEach(el => el.classList.add('updated-style'));
}

// Good: Use requestAnimationFrame for visual updates
function animateElement(element, targetX) {
    let currentX = 0;

    function step() {
        currentX += (targetX - currentX) * 0.1;
        element.style.transform = `translateX(${currentX}px)`;

        if (Math.abs(targetX - currentX) > 0.1) {
            requestAnimationFrame(step);
        }
    }

    requestAnimationFrame(step);
}

// Good: Virtual scrolling for large lists
class VirtualList {
    constructor(container, items, itemHeight) {
        this.container = container;
        this.items = items;
        this.itemHeight = itemHeight;
        this.visibleCount = Math.ceil(container.clientHeight / itemHeight) + 2;

        this.container.addEventListener('scroll', () => this.render());
        this.render();
    }

    render() {
        const scrollTop = this.container.scrollTop;
        const startIndex = Math.floor(scrollTop / this.itemHeight);
        const endIndex = startIndex + this.visibleCount;

        // Only render visible items
        const visibleItems = this.items.slice(startIndex, endIndex);
        // ... render logic
    }
}
```

---

## Pattern 6: Event Delegation

**When to use**: Handling events on multiple elements

```javascript
// INEFFICIENT: Multiple event listeners
function setupItemListeners() {
    const items = document.querySelectorAll('.item');
    items.forEach(item => {
        item.addEventListener('click', (e) => {
            console.log('Clicked:', e.target.dataset.id);
        });
    });
}

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

## Pattern 7: Memory Management

```javascript
// Bad: Memory leaks from closures
function createButtons() {
    const data = new Array(1000000).fill('large data');

    document.querySelectorAll('button').forEach(btn => {
        btn.addEventListener('click', () => {
            // This closure holds reference to 'data'
            console.log(data.length);
        });
    });
}

// Good: Release references when done
function createButtons() {
    const dataLength = new Array(1000000).fill('large data').length;

    document.querySelectorAll('button').forEach(btn => {
        btn.addEventListener('click', () => {
            // Only stores the number, not the array
            console.log(dataLength);
        });
    });
}

// Good: Clean up with WeakMap
const cache = new WeakMap();

function processElement(element) {
    if (cache.has(element)) {
        return cache.get(element);
    }

    const result = expensiveCalculation(element);
    cache.set(element, result);
    return result;
}
// When element is removed from DOM, WeakMap entry is garbage collected
```

---

## Performance Checklist

- [ ] Minimize DOM manipulation, use DocumentFragment
- [ ] Use event delegation over multiple listeners
- [ ] Implement debouncing/throttling for frequent events
- [ ] Optimize loops (avoid unnecessary work)
- [ ] Use Web Workers for CPU-intensive tasks
- [ ] Implement code splitting and lazy loading
- [ ] Profile with Chrome DevTools
- [ ] Use requestAnimationFrame for animations
- [ ] Avoid memory leaks (clean up listeners)
- [ ] Use WeakMap/WeakSet for temporary caches
- [ ] Minimize reflows and repaints
- [ ] Use virtual scrolling for long lists
