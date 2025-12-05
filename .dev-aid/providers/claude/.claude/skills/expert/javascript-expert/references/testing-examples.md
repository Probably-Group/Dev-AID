# JavaScript Testing Examples

## Unit Testing with Vitest/Jest

### Setup: vitest.config.js

```javascript
import { defineConfig } from 'vitest/config';

export default defineConfig({
    test: {
        environment: 'jsdom',
        coverage: {
            provider: 'v8',
            reporter: ['text', 'json', 'html'],
            threshold: {
                branches: 80,
                functions: 80,
                lines: 80,
                statements: 80
            }
        }
    }
});
```

---

## Basic Unit Tests

```javascript
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

describe('UserService', () => {
    let service;
    let mockFetch;

    beforeEach(() => {
        mockFetch = vi.fn();
        global.fetch = mockFetch;
        service = new UserService();
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    it('should fetch user successfully', async () => {
        const mockUser = { id: 1, name: 'John' };
        mockFetch.mockResolvedValue({
            ok: true,
            json: () => Promise.resolve(mockUser)
        });

        const user = await service.getUser(1);

        expect(mockFetch).toHaveBeenCalledWith('/api/users/1');
        expect(user).toEqual(mockUser);
    });

    it('should handle fetch errors', async () => {
        mockFetch.mockResolvedValue({
            ok: false,
            status: 404,
            statusText: 'Not Found'
        });

        await expect(service.getUser(999))
            .rejects
            .toThrow('User not found');
    });

    it('should handle network errors', async () => {
        mockFetch.mockRejectedValue(new Error('Network error'));

        await expect(service.getUser(1))
            .rejects
            .toThrow('Network error');
    });
});
```

---

## Testing Async Functions

```javascript
describe('Async operations', () => {
    it('should handle Promise.all correctly', async () => {
        const results = await Promise.all([
            fetchData('a'),
            fetchData('b')
        ]);

        expect(results).toHaveLength(2);
    });

    it('should timeout long operations', async () => {
        vi.useFakeTimers();

        const promise = timeoutOperation(1000);
        vi.advanceTimersByTime(1000);

        await expect(promise).rejects.toThrow('Timeout');

        vi.useRealTimers();
    });

    it('should retry failed operations', async () => {
        const mockFn = vi.fn()
            .mockRejectedValueOnce(new Error('Fail 1'))
            .mockRejectedValueOnce(new Error('Fail 2'))
            .mockResolvedValue('Success');

        const result = await retry(mockFn, 3);

        expect(mockFn).toHaveBeenCalledTimes(3);
        expect(result).toBe('Success');
    });
});
```

---

## Integration Testing

```javascript
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { createServer } from '../server';

describe('API Integration', () => {
    let server;
    let baseUrl;

    beforeAll(async () => {
        server = await createServer();
        baseUrl = `http://localhost:${server.address().port}`;
    });

    afterAll(async () => {
        await server.close();
    });

    it('should create and fetch user', async () => {
        // Create user
        const createRes = await fetch(`${baseUrl}/api/users`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: 'Test User' })
        });

        const created = await createRes.json();
        expect(created.id).toBeDefined();

        // Fetch user
        const fetchRes = await fetch(`${baseUrl}/api/users/${created.id}`);
        const fetched = await fetchRes.json();

        expect(fetched.name).toBe('Test User');
    });

    it('should handle validation errors', async () => {
        const res = await fetch(`${baseUrl}/api/users`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: '' }) // Invalid
        });

        expect(res.status).toBe(400);
        const error = await res.json();
        expect(error.message).toContain('validation');
    });
});
```

---

## DOM Testing

```javascript
import { describe, it, expect, beforeEach } from 'vitest';
import { JSDOM } from 'jsdom';

describe('DOM manipulation', () => {
    let document;

    beforeEach(() => {
        const dom = new JSDOM('<!DOCTYPE html><div id="app"></div>');
        document = dom.window.document;
    });

    it('should render list items', () => {
        const app = document.getElementById('app');
        const items = ['a', 'b', 'c'];

        renderList(app, items);

        const listItems = app.querySelectorAll('li');
        expect(listItems.length).toBe(3);
        expect(listItems[0].textContent).toBe('a');
    });

    it('should handle click events', () => {
        const button = document.createElement('button');
        let clicked = false;

        button.addEventListener('click', () => { clicked = true; });
        button.click();

        expect(clicked).toBe(true);
    });

    it('should sanitize user input', () => {
        const div = document.createElement('div');
        const maliciousInput = '<script>alert("XSS")</script>';

        // Using textContent (safe)
        div.textContent = maliciousInput;
        expect(div.innerHTML).toBe('&lt;script&gt;alert("XSS")&lt;/script&gt;');
    });
});
```

---

## Mocking and Spies

```javascript
describe('Mocking', () => {
    it('should mock function calls', () => {
        const mockFn = vi.fn();
        mockFn.mockReturnValue(42);

        const result = mockFn(1, 2, 3);

        expect(mockFn).toHaveBeenCalledWith(1, 2, 3);
        expect(mockFn).toHaveBeenCalledTimes(1);
        expect(result).toBe(42);
    });

    it('should spy on object methods', () => {
        const obj = {
            method: (x) => x * 2
        };

        const spy = vi.spyOn(obj, 'method');

        obj.method(5);

        expect(spy).toHaveBeenCalledWith(5);
        expect(spy).toHaveReturnedWith(10);

        spy.mockRestore();
    });

    it('should mock module imports', async () => {
        vi.mock('../api', () => ({
            fetchUser: vi.fn().mockResolvedValue({ id: 1, name: 'Mock' })
        }));

        const { fetchUser } = await import('../api');
        const user = await fetchUser(1);

        expect(user).toEqual({ id: 1, name: 'Mock' });
    });
});
```

---

## Testing Error Handling

```javascript
describe('Error handling', () => {
    it('should throw on invalid input', () => {
        expect(() => divide(10, 0)).toThrow('Division by zero');
    });

    it('should catch async errors', async () => {
        await expect(fetchInvalidData()).rejects.toThrow('Invalid data');
    });

    it('should handle custom error types', () => {
        class CustomError extends Error {
            constructor(message) {
                super(message);
                this.name = 'CustomError';
            }
        }

        function riskyOperation() {
            throw new CustomError('Something went wrong');
        }

        expect(() => riskyOperation()).toThrow(CustomError);
        expect(() => riskyOperation()).toThrow('Something went wrong');
    });
});
```

---

## Testing with Timers

```javascript
describe('Timer operations', () => {
    beforeEach(() => {
        vi.useFakeTimers();
    });

    afterEach(() => {
        vi.useRealTimers();
    });

    it('should debounce function calls', () => {
        const mockFn = vi.fn();
        const debounced = debounce(mockFn, 100);

        debounced();
        debounced();
        debounced();

        expect(mockFn).not.toHaveBeenCalled();

        vi.advanceTimersByTime(100);

        expect(mockFn).toHaveBeenCalledTimes(1);
    });

    it('should throttle function calls', () => {
        const mockFn = vi.fn();
        const throttled = throttle(mockFn, 100);

        throttled();
        expect(mockFn).toHaveBeenCalledTimes(1);

        throttled();
        throttled();
        expect(mockFn).toHaveBeenCalledTimes(1);

        vi.advanceTimersByTime(100);
        throttled();
        expect(mockFn).toHaveBeenCalledTimes(2);
    });
});
```

---

## Snapshot Testing

```javascript
describe('Snapshot tests', () => {
    it('should match component snapshot', () => {
        const component = createComponent({
            title: 'Test',
            items: ['a', 'b', 'c']
        });

        expect(component.outerHTML).toMatchSnapshot();
    });

    it('should match inline snapshot', () => {
        const data = { id: 1, name: 'Test' };
        expect(data).toMatchInlineSnapshot(`
          {
            "id": 1,
            "name": "Test",
          }
        `);
    });
});
```

---

## Test Coverage Best Practices

```javascript
// Run tests with coverage
// npm test -- --coverage

// Example of well-covered function
export function calculatePrice(quantity, unitPrice, discount = 0) {
    // Test: quantity validation
    if (quantity <= 0) {
        throw new Error('Quantity must be positive');
    }

    // Test: unitPrice validation
    if (unitPrice < 0) {
        throw new Error('Unit price cannot be negative');
    }

    // Test: discount validation
    if (discount < 0 || discount > 100) {
        throw new Error('Discount must be between 0 and 100');
    }

    // Test: normal calculation
    const subtotal = quantity * unitPrice;
    const discountAmount = subtotal * (discount / 100);
    return subtotal - discountAmount;
}

// Comprehensive test suite
describe('calculatePrice', () => {
    it('should calculate price without discount', () => {
        expect(calculatePrice(10, 5)).toBe(50);
    });

    it('should calculate price with discount', () => {
        expect(calculatePrice(10, 5, 10)).toBe(45);
    });

    it('should throw on invalid quantity', () => {
        expect(() => calculatePrice(0, 5)).toThrow('Quantity must be positive');
    });

    it('should throw on negative unit price', () => {
        expect(() => calculatePrice(10, -5)).toThrow('Unit price cannot be negative');
    });

    it('should throw on invalid discount', () => {
        expect(() => calculatePrice(10, 5, 101)).toThrow('Discount must be between 0 and 100');
    });
});
```

---

## Testing Checklist

- [ ] Test happy path (normal operation)
- [ ] Test edge cases (empty, null, undefined)
- [ ] Test error conditions (invalid input, failures)
- [ ] Test async operations (promises, callbacks)
- [ ] Test error handling (try/catch, rejections)
- [ ] Mock external dependencies (API calls, DB)
- [ ] Test event handlers and DOM interactions
- [ ] Achieve >80% code coverage
- [ ] Use descriptive test names
- [ ] Follow AAA pattern (Arrange, Act, Assert)
- [ ] Clean up resources (mocks, timers, listeners)
- [ ] Test in isolation (unit tests)
- [ ] Test integration points (integration tests)
