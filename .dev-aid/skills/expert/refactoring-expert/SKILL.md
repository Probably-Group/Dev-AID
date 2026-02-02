---
name: refactoring-expert
version: 2.0.0
description: "Legacy code refactoring with technical debt reduction, incremental migration, and test coverage."
risk_level: MEDIUM
---

# Refactoring Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE providing guidance:**
1. Verify claims against authoritative sources
2. Distinguish between established practices and opinions
3. Never invent statistics, studies, or references
4. If unsure, state uncertainty explicitly

### 0.2 Risk Level: MEDIUM

**Verification requirements:**
- Cross-reference recommendations with industry standards
- Cite sources when making specific claims
- Acknowledge when best practices vary by context

---

## 1. Security Principles

### 1.1 Preserve Security Controls (CWE-284)

**Principle:** Refactoring must never weaken existing security controls.

```python
# ❌ WRONG - Refactoring removes validation
# Before: Verbose but secure
def get_user(user_id: str) -> User:
    if not user_id.isalnum():
        raise ValueError("Invalid user ID")
    return db.query(User).filter(User.id == user_id).first()

# After: "Simplified" but insecure
def get_user(user_id: str) -> User:
    return db.query(User).filter(User.id == user_id).first()  # No validation!

# ✅ CORRECT - Extract validation, preserve behavior
from functools import wraps
from typing import Callable

def validate_id(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(user_id: str, *args, **kwargs):
        if not user_id.isalnum():
            raise ValueError("Invalid user ID")
        return func(user_id, *args, **kwargs)
    return wrapper

@validate_id
def get_user(user_id: str) -> User:
    return db.query(User).filter(User.id == user_id).first()
```

### 1.2 Maintain Test Coverage (CWE-1164)

**Principle:** Refactoring without tests is guessing. Always ensure tests pass before and after.

```bash
# ❌ WRONG - Refactor without running tests
git commit -m "Refactor user service"

# ✅ CORRECT - Test-driven refactoring cycle
# 1. Run tests before
pytest tests/ -v --tb=short

# 2. Make small refactoring change

# 3. Run tests after each change
pytest tests/ -v --tb=short

# 4. Commit only when green
git commit -m "Refactor: Extract validation to decorator"
```

### 1.3 Atomic Refactoring (CWE-362)

**Principle:** Each refactoring should be a single, complete transformation. Partial refactors create inconsistent states.

---

## 2. Version Requirements

```
# Testing
pytest>=8.0.0
pytest-cov>=4.0.0
# Static analysis
ruff>=0.1.0
mypy>=1.8.0
# Refactoring tools
rope>=1.12.0  # Python refactoring library
jscodeshift>=0.15.0  # JavaScript/TypeScript codemods
```

---

## 3. Code Patterns

### WHEN extracting methods, preserve single responsibility

```python
# ❌ WRONG - Extract creates another god method
class OrderService:
    def process_order(self, order: Order):
        # 200 lines of code doing everything
        pass

    def _helper(self, order: Order):
        # Still 150 lines doing too much
        pass

# ✅ CORRECT - Extract to focused, testable methods
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

class PaymentStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class PaymentResult:
    status: PaymentStatus
    transaction_id: str | None
    error: str | None = None

class OrderService:
    def __init__(
        self,
        inventory: InventoryService,
        payment: PaymentService,
        notification: NotificationService,
    ):
        self._inventory = inventory
        self._payment = payment
        self._notification = notification

    def process_order(self, order: Order) -> OrderResult:
        """Orchestrates order processing. Each step is a separate, testable unit."""

        # Step 1: Validate inventory
        inventory_result = self._check_inventory(order)
        if not inventory_result.available:
            return OrderResult.failed("Items not in stock")

        # Step 2: Calculate totals
        totals = self._calculate_totals(order)

        # Step 3: Process payment
        payment_result = self._process_payment(order, totals)
        if payment_result.status == PaymentStatus.FAILED:
            return OrderResult.failed(payment_result.error)

        # Step 4: Update inventory
        self._reserve_inventory(order)

        # Step 5: Send confirmation
        self._send_confirmation(order, payment_result)

        return OrderResult.success(order.id)

    def _check_inventory(self, order: Order) -> InventoryResult:
        """Single responsibility: Check if items are available."""
        return self._inventory.check_availability(order.items)

    def _calculate_totals(self, order: Order) -> OrderTotals:
        """Single responsibility: Calculate order totals."""
        subtotal = sum(item.price * item.quantity for item in order.items)
        tax = subtotal * order.tax_rate
        return OrderTotals(subtotal=subtotal, tax=tax, total=subtotal + tax)

    def _process_payment(self, order: Order, totals: OrderTotals) -> PaymentResult:
        """Single responsibility: Process payment."""
        return self._payment.charge(order.payment_method, totals.total)

    def _reserve_inventory(self, order: Order) -> None:
        """Single responsibility: Reserve inventory."""
        self._inventory.reserve(order.items)

    def _send_confirmation(self, order: Order, payment: PaymentResult) -> None:
        """Single responsibility: Send notification."""
        self._notification.send_order_confirmation(order, payment.transaction_id)
```

### WHEN removing duplication, use the Rule of Three

```python
# ❌ WRONG - Premature abstraction after seeing duplication once
# "DRY says no duplication, so I'll abstract immediately"

# ✅ CORRECT - Wait for third occurrence, then abstract
# First occurrence: Just write the code
def validate_user_email(email: str) -> bool:
    return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email))

# Second occurrence: Note the duplication, but don't abstract yet
def validate_contact_email(email: str) -> bool:
    return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email))

# Third occurrence: NOW abstract, with clear understanding of variations
def validate_admin_email(email: str) -> bool:
    return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email))

# After third: Extract with confidence
import re
from functools import lru_cache

@lru_cache(maxsize=1)
def _get_email_pattern() -> re.Pattern:
    return re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')

def validate_email(email: str) -> bool:
    """Validate email format. Used by user, contact, and admin validation."""
    if not email or len(email) > 254:  # RFC 5321
        return False
    return bool(_get_email_pattern().match(email))
```

### WHEN refactoring conditionals, use polymorphism or strategy pattern

```python
# ❌ WRONG - Giant if/elif chain
def calculate_shipping(order: Order) -> Decimal:
    if order.shipping_type == "standard":
        if order.total > 50:
            return Decimal("0")
        return Decimal("5.99")
    elif order.shipping_type == "express":
        if order.total > 100:
            return Decimal("9.99")
        return Decimal("14.99")
    elif order.shipping_type == "overnight":
        return Decimal("24.99")
    elif order.shipping_type == "international":
        base = Decimal("29.99")
        if order.country in ["CA", "MX"]:
            return base
        return base + Decimal("15.00")
    else:
        raise ValueError(f"Unknown shipping type: {order.shipping_type}")

# ✅ CORRECT - Strategy pattern with registry
from abc import ABC, abstractmethod
from decimal import Decimal
from dataclasses import dataclass

class ShippingStrategy(ABC):
    @abstractmethod
    def calculate(self, order: Order) -> Decimal:
        pass

class StandardShipping(ShippingStrategy):
    FREE_THRESHOLD = Decimal("50")
    BASE_RATE = Decimal("5.99")

    def calculate(self, order: Order) -> Decimal:
        if order.total > self.FREE_THRESHOLD:
            return Decimal("0")
        return self.BASE_RATE

class ExpressShipping(ShippingStrategy):
    DISCOUNT_THRESHOLD = Decimal("100")
    BASE_RATE = Decimal("14.99")
    DISCOUNTED_RATE = Decimal("9.99")

    def calculate(self, order: Order) -> Decimal:
        if order.total > self.DISCOUNT_THRESHOLD:
            return self.DISCOUNTED_RATE
        return self.BASE_RATE

class OvernightShipping(ShippingStrategy):
    RATE = Decimal("24.99")

    def calculate(self, order: Order) -> Decimal:
        return self.RATE

class InternationalShipping(ShippingStrategy):
    BASE_RATE = Decimal("29.99")
    EXTENDED_RATE = Decimal("44.99")
    NEARBY_COUNTRIES = {"CA", "MX"}

    def calculate(self, order: Order) -> Decimal:
        if order.country in self.NEARBY_COUNTRIES:
            return self.BASE_RATE
        return self.EXTENDED_RATE

# Registry pattern for extensibility
SHIPPING_STRATEGIES: dict[str, type[ShippingStrategy]] = {
    "standard": StandardShipping,
    "express": ExpressShipping,
    "overnight": OvernightShipping,
    "international": InternationalShipping,
}

def calculate_shipping(order: Order) -> Decimal:
    strategy_class = SHIPPING_STRATEGIES.get(order.shipping_type)
    if not strategy_class:
        raise ValueError(f"Unknown shipping type: {order.shipping_type}")
    return strategy_class().calculate(order)
```

### WHEN simplifying complex functions, use early returns

```python
# ❌ WRONG - Deeply nested conditionals
def process_request(request: Request) -> Response:
    if request.is_authenticated:
        if request.has_permission("read"):
            if request.resource_exists:
                if not request.is_rate_limited:
                    data = fetch_data(request.resource_id)
                    if data:
                        return Response(200, data)
                    else:
                        return Response(404, "Not found")
                else:
                    return Response(429, "Rate limited")
            else:
                return Response(404, "Resource not found")
        else:
            return Response(403, "Permission denied")
    else:
        return Response(401, "Not authenticated")

# ✅ CORRECT - Early returns (guard clauses)
def process_request(request: Request) -> Response:
    # Guard clauses handle error cases first
    if not request.is_authenticated:
        return Response(401, "Not authenticated")

    if not request.has_permission("read"):
        return Response(403, "Permission denied")

    if not request.resource_exists:
        return Response(404, "Resource not found")

    if request.is_rate_limited:
        return Response(429, "Rate limited")

    # Happy path is now clear and flat
    data = fetch_data(request.resource_id)
    if not data:
        return Response(404, "Not found")

    return Response(200, data)
```

### WHEN breaking dependencies, use dependency injection

```python
# ❌ WRONG - Hard-coded dependencies
class UserService:
    def __init__(self):
        self.db = PostgresDatabase()  # Hard to test
        self.cache = RedisCache()      # Hard to test
        self.email = SendGridClient()  # Hard to test

    def get_user(self, user_id: str) -> User:
        cached = self.cache.get(f"user:{user_id}")
        if cached:
            return cached
        user = self.db.query(User).get(user_id)
        self.cache.set(f"user:{user_id}", user)
        return user

# ✅ CORRECT - Dependency injection with protocols
from typing import Protocol

class Database(Protocol):
    def query(self, model: type) -> QueryBuilder: ...

class Cache(Protocol):
    def get(self, key: str) -> Any | None: ...
    def set(self, key: str, value: Any, ttl: int = 3600) -> None: ...

class EmailClient(Protocol):
    def send(self, to: str, subject: str, body: str) -> bool: ...

class UserService:
    def __init__(
        self,
        db: Database,
        cache: Cache,
        email: EmailClient,
    ):
        self._db = db
        self._cache = cache
        self._email = email

    def get_user(self, user_id: str) -> User | None:
        # Now testable with mock implementations
        cached = self._cache.get(f"user:{user_id}")
        if cached:
            return cached

        user = self._db.query(User).get(user_id)
        if user:
            self._cache.set(f"user:{user_id}", user)
        return user

# Factory for production
def create_user_service() -> UserService:
    return UserService(
        db=PostgresDatabase(settings.DATABASE_URL),
        cache=RedisCache(settings.REDIS_URL),
        email=SendGridClient(settings.SENDGRID_API_KEY),
    )

# Easy testing with mocks
def test_get_user_from_cache():
    mock_cache = Mock(spec=Cache)
    mock_cache.get.return_value = User(id="123", name="Test")

    service = UserService(
        db=Mock(spec=Database),
        cache=mock_cache,
        email=Mock(spec=EmailClient),
    )

    user = service.get_user("123")
    assert user.name == "Test"
    mock_cache.get.assert_called_once_with("user:123")
```

---

## 4. Anti-Patterns

**NEVER:**
- Refactor without tests (or skip running tests after changes)
- Remove validation "for simplicity"
- Abstract after seeing duplication once (Rule of Three)
- Make multiple unrelated changes in one refactoring
- Refactor and add features simultaneously
- Leave code in inconsistent state between commits
- Ignore IDE refactoring warnings/suggestions

---

## 5. Testing

```python
import pytest
from decimal import Decimal
from unittest.mock import Mock

class TestShippingRefactoring:

    @pytest.mark.parametrize("shipping_type,total,expected", [
        ("standard", Decimal("30"), Decimal("5.99")),
        ("standard", Decimal("60"), Decimal("0")),
        ("express", Decimal("50"), Decimal("14.99")),
        ("express", Decimal("150"), Decimal("9.99")),
        ("overnight", Decimal("100"), Decimal("24.99")),
    ])
    def test_shipping_calculation_matches_original(
        self, shipping_type, total, expected
    ):
        """Verify refactored code produces same results as original."""
        order = Order(shipping_type=shipping_type, total=total, country="US")
        result = calculate_shipping(order)
        assert result == expected

    def test_unknown_shipping_type_raises(self):
        """Error handling preserved after refactoring."""
        order = Order(shipping_type="teleport", total=Decimal("100"), country="US")
        with pytest.raises(ValueError, match="Unknown shipping type"):
            calculate_shipping(order)

class TestDependencyInjection:

    def test_user_service_uses_cache_first(self):
        """Verify cache is checked before database."""
        mock_db = Mock(spec=Database)
        mock_cache = Mock(spec=Cache)
        mock_cache.get.return_value = User(id="123", name="Cached")

        service = UserService(mock_db, mock_cache, Mock())
        user = service.get_user("123")

        mock_cache.get.assert_called_once()
        mock_db.query.assert_not_called()  # Should not hit DB
        assert user.name == "Cached"

    def test_user_service_falls_back_to_db(self):
        """Verify DB is used when cache misses."""
        mock_db = Mock(spec=Database)
        mock_db.query.return_value.get.return_value = User(id="123", name="FromDB")
        mock_cache = Mock(spec=Cache)
        mock_cache.get.return_value = None

        service = UserService(mock_db, mock_cache, Mock())
        user = service.get_user("123")

        mock_db.query.assert_called_once()
        mock_cache.set.assert_called_once()  # Should cache result
        assert user.name == "FromDB"

class TestSecurityPreservation:

    def test_validation_preserved_after_refactoring(self):
        """Security validation must survive refactoring."""
        # Test that invalid IDs are still rejected
        with pytest.raises(ValueError, match="Invalid user ID"):
            get_user("../../../etc/passwd")

        with pytest.raises(ValueError, match="Invalid user ID"):
            get_user("'; DROP TABLE users;--")
```

---

## 6. Pre-Generation Checklist

**BEFORE refactoring code:**

- [ ] Tests exist: Code has tests that pass before refactoring
- [ ] Security audit: Identified all security controls to preserve
- [ ] Atomic changes: Each refactoring is a single transformation
- [ ] Rule of Three: Not abstracting prematurely
- [ ] Tests after: All tests pass after each change
- [ ] No feature mix: Refactoring only, no new functionality
- [ ] Dependency injection: Breaking hard-coded dependencies
- [ ] Guard clauses: Using early returns for clarity
