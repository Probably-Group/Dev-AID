---
name: senior-architect
version: 2.0.0
description: "Architectural review for identifying anti-patterns, scalability issues, and systemic design problems. Use when reviewing architecture, evaluating trade-offs, or diagnosing O(n squared) bottlenecks. Do NOT use for code-level refactoring (use refactoring-expert)."
risk_level: MEDIUM
---

# Senior Architect - Code Generation Rules

---

## 1. Architecture Principles

### 1.1 Complexity Detection (CWE-1120)

**Principle:** Identify O(n^2) algorithms, circular dependencies, and unnecessary complexity.

```python
# WRONG - O(n^2) hidden in innocent-looking code
def find_duplicates(items: list[str]) -> list[str]:
    duplicates = []
    for item in items:
        if items.count(item) > 1 and item not in duplicates:  # O(n) inside O(n)
            duplicates.append(item)
    return duplicates

# CORRECT - O(n) with proper data structure
from collections import Counter

def find_duplicates(items: list[str]) -> list[str]:
    counts = Counter(items)  # O(n)
    return [item for item, count in counts.items() if count > 1]  # O(n)
```

### 1.2 Dependency Management (CWE-1047)

**Principle:** Detect circular dependencies, tight coupling, and dependency direction violations.

```python
# WRONG - Circular dependency
# file: user_service.py
from order_service import OrderService  # user -> order

# file: order_service.py
from user_service import UserService    # order -> user (CIRCULAR!)

# CORRECT - Dependency inversion via interfaces
# file: interfaces.py (no dependencies)
class UserRepository(ABC):
    @abstractmethod
    def get_user(self, user_id: str) -> "User": ...

class OrderRepository(ABC):
    @abstractmethod
    def get_orders_for_user(self, user_id: str) -> list["Order"]: ...

# file: user_service.py (depends on interface, not on order_service)
class UserService:
    def __init__(self, user_repo: UserRepository, order_repo: OrderRepository):
        self._users = user_repo
        self._orders = order_repo
```

### 1.3 Scalability Analysis

**Principle:** Identify bottlenecks before they become production problems.

Common scalability red flags:
- **N+1 queries**: Fetching related records in a loop instead of a single JOIN/batch
- **Unbounded collections**: Loading all records without pagination or cursor limits
- **Synchronous I/O in hot paths**: Blocking calls where async would prevent thread starvation
- **Missing caching**: Recomputing expensive results that rarely change
- **Lock contention**: Broad locks where fine-grained or lock-free structures suffice

```python
# WRONG - N+1 query pattern
for user in get_all_users():
    orders = get_orders_for_user(user.id)  # 1 query per user

# CORRECT - Batch fetch
users = get_all_users()
orders_by_user = get_orders_for_users([u.id for u in users])  # 1 query total
```

### 1.4 Layer Architecture Rules

**Principle:** Enforce unidirectional dependency flow between architectural layers.

Define allowed import directions explicitly. Each layer may only depend on layers
below it in the hierarchy. Violations indicate coupling that will resist future changes.

```
Allowed dependency direction (top imports from bottom):

  api          -> services, domain
  services     -> domain, repositories
  repositories -> domain
  domain       -> (nothing — pure business logic)
```

Common layer violations:
- Domain importing from infrastructure (DB, HTTP, file I/O)
- Repository importing from API layer (reverse dependency)
- Service-to-service imports without an orchestration layer

---

## 2. Version Requirements

```
# Architecture analysis tools
pydeps>=1.12.0         # Dependency visualization
import-linter>=1.12.0  # Dependency rules enforcement
vulture>=2.10          # Dead code detection
# Metrics
radon>=6.0.0           # Cyclomatic complexity
xenon>=0.9.0           # Complexity threshold enforcement
```

---

## 3. Code Patterns

### WHEN reviewing architecture, analyze dependency structure

Build a structured dependency graph using AST parsing. Walk all Python files to extract
imports, build a reverse-dependency map, then run DFS for circular dependency detection
and validate imports against defined layer rules (e.g., `api` may only import `services`).

See `references/architecture_analyzer.py` for the full `ArchitectureAnalyzer` implementation
with `Module`, `DependencyViolation` data classes and `define_layers()` / `analyze()` API.

Approach summary:
1. Parse all `.py` files with `ast` to extract import statements
2. Build a forward and reverse dependency graph (`Module.imports` / `Module.imported_by`)
3. Run DFS to detect cycles (circular dependencies)
4. Validate each import against defined layer rules to catch boundary violations

Key data models:

```python
@dataclass
class Module:
    path: Path
    imports: set[str] = field(default_factory=set)
    imported_by: set[str] = field(default_factory=set)

@dataclass
class DependencyViolation:
    source: str
    target: str
    violation_type: str  # "circular", "layer_skip", "forbidden"
    description: str
```

### WHEN identifying performance issues, measure complexity

Use AST-based analysis to compute cyclomatic complexity (decision point count) and
cognitive complexity (nesting-weighted branches). Flag functions exceeding thresholds:
cyclomatic > 10, cognitive > 15, LOC > 50, parameters > 5.

See `references/complexity_analyzer.py` for the full `ComplexityAnalyzer` implementation
with `ComplexityReport` data class and `analyze_project()` entry point.

Approach summary:
1. Walk AST nodes to count decision points (`if`, `while`, `for`, `except`, `BoolOp`) for cyclomatic complexity
2. Add nesting-depth penalties for cognitive complexity (each nested branch costs `1 + depth`)
3. Collect LOC and parameter count per function
4. Sort results by complexity (worst first) for prioritized review

Thresholds:

| Metric | Concerning | Action |
|--------|-----------|--------|
| Cyclomatic complexity | > 10 | Split function |
| Cognitive complexity | > 15 | Reduce nesting |
| Lines of code | > 50 | Extract helpers |
| Parameter count | > 5 | Introduce parameter object |

### WHEN designing APIs, enforce consistency patterns

Check all endpoints for naming conventions (lowercase paths, plural nouns), response
envelope uniformity, HTTP status code consistency, and CRUD completeness per resource.

See `references/api_consistency_checker.py` for the full `APIConsistencyChecker`
implementation with `EndpointDefinition`, `APIConsistencyViolation` data classes.

Checks performed:
1. **Naming conventions** -- Paths must be lowercase; resource names must be plural nouns
2. **Response envelopes** -- All GET endpoints must use the same wrapper pattern
3. **Status codes** -- POST endpoints should consistently use 201 for creation, 200 for actions
4. **CRUD completeness** -- If GET and POST exist for a resource, PUT/PATCH and DELETE should too

Common API inconsistencies to catch:

```
# Inconsistent response envelopes:
GET /users/{id}    -> { user: {...} }
GET /products/{id} -> {...}              # Different structure!

# Inconsistent creation response keys:
POST /users        -> { id: "123" }
POST /orders       -> { order_id: "456" }  # Different key!
```

**Rule:** Use consistent envelope `{ data: {...}, meta: {...} }` across all endpoints.

---

## 4. Anti-Patterns

Do not:
- Ignore O(n^2) algorithms in hot paths
- Allow circular dependencies between modules
- Skip layer boundary enforcement
- Accept complexity metrics without investigation
- Design APIs without consistency patterns
- Leave dead code in the codebase
- Create god classes/modules (>500 LOC)

### God Class / God Module Detection

A module is a "god module" when it:
- Exceeds 500 LOC (hard limit) or 300 LOC (review trigger)
- Has more than 10 direct dependencies (high fan-out)
- Is imported by more than 10 other modules (high fan-in)
- Mixes concerns from multiple architectural layers

**Resolution**: Extract cohesive subsets into focused modules. Use the dependency graph
to identify natural seams -- clusters of functions that share the same imports.

### Premature Abstraction

Equally dangerous as missing abstraction:
- Interfaces with only one implementation (unless required for testing)
- Generic frameworks built before the second use case exists
- Inheritance hierarchies deeper than 3 levels
- Configuration-driven behavior that could be simple if/else

---

## 5. Testing

Architectural analysis code should be tested with `tmp_path` fixtures that create
minimal file structures exercising each violation type (circular deps, layer violations,
high complexity, naming inconsistencies, response envelope mismatches).

See `references/example_tests.py` for full test implementations covering
`ArchitectureAnalyzer`, `ComplexityAnalyzer`, and `APIConsistencyChecker`.

Key test patterns:

- **Circular dependency detection**: Create two files that import each other, verify `violation_type == "circular"`
- **Layer violation detection**: Create an `api/` module importing directly from `repositories/`, verify `violation_type == "layer_skip"`
- **Complexity flagging**: Write a deeply nested function, verify `is_concerning() == True`
- **API naming**: Add a camelCase endpoint path, verify `violation_type == "naming"`
- **Response consistency**: Add GET endpoints with different envelope patterns, verify `violation_type == "response_structure"`

---

## 6. Review Workflow

When conducting an architectural review, follow this sequence:

1. **Dependency analysis** -- Map the module graph, identify cycles and layer violations
2. **Complexity scan** -- Measure cyclomatic/cognitive complexity, flag hotspots
3. **API audit** -- Check endpoint consistency (naming, envelopes, status codes, CRUD)
4. **Dead code sweep** -- Run `vulture` to identify unused exports and unreachable paths
5. **Scalability assessment** -- Check for N+1 queries, unbounded collections, sync I/O in hot paths
6. **Report** -- Prioritize findings by impact (P0: production risk, P1: maintainability, P2: style)

---

## 7. Pre-Generation Checklist

Before generating architectural code:

- [ ] Complexity check: No O(n^2) in hot paths
- [ ] Dependency graph: No circular dependencies
- [ ] Layer rules: Dependency direction enforced
- [ ] API consistency: Naming, responses, status codes uniform
- [ ] Module size: No files > 500 LOC

**Templates**: See `assets/` for reusable output templates.
