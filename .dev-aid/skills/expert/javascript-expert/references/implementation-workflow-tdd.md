## 5. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```javascript
// Using Vitest
import { describe, it, expect } from 'vitest';
import { calculateTotal, applyDiscount } from '../cart';

describe('Cart calculations', () => {
    it('should calculate total from items', () => {
        const items = [
            { price: 10, quantity: 2 },
            { price: 5, quantity: 3 }
        ];

        expect(calculateTotal(items)).toBe(35);
    });

    it('should apply percentage discount', () => {
        const total = 100;
        const discount = 10; // 10%

        expect(applyDiscount(total, discount)).toBe(90);
    });

    it('should handle empty cart', () => {
        expect(calculateTotal([])).toBe(0);
    });

    it('should throw on invalid discount', () => {
        expect(() => applyDiscount(100, -5)).toThrow('Invalid discount');
    });
});
```

### Step 2: Implement Minimum Code to Pass

```javascript
// cart.js - Minimum implementation
export function calculateTotal(items) {
    if (!items || items.length === 0) return 0;

    return items.reduce((sum, item) => {
        return sum + (item.price * item.quantity);
    }, 0);
}

export function applyDiscount(total, discount) {
    if (discount < 0 || discount > 100) {
        throw new Error('Invalid discount');
    }

    return total - (total * discount / 100);
}
```

### Step 3: Refactor if Needed

```javascript
// cart.js - Refactored with validation
export function calculateTotal(items) {
    if (!Array.isArray(items)) {
        throw new TypeError('Items must be an array');
    }

    return items.reduce((sum, item) => {
        const price = Number(item.price) || 0;
        const quantity = Number(item.quantity) || 0;
        return sum + (price * quantity);
    }, 0);
}

export function applyDiscount(total, discount) {
    if (typeof total !== 'number' || typeof discount !== 'number') {
        throw new TypeError('Arguments must be numbers');
    }

    if (discount < 0 || discount > 100) {
        throw new RangeError('Invalid discount: must be 0-100');
    }

    return total * (1 - discount / 100);
}
```

### Step 4: Run Full Verification

```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- cart.test.js

# Run in watch mode during development
npm test -- --watch
```

**See**: `references/testing-examples.md` for comprehensive testing patterns

---

