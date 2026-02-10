---
name: senior-architect
version: 2.0.0
description: "Architectural review for identifying anti-patterns, scalability issues, and systemic design problems. Use when reviewing architecture, evaluating trade-offs, or diagnosing O(n squared) bottlenecks. Do NOT use for code-level refactoring (use refactoring-expert)."
risk_level: MEDIUM
---

# Senior Architect - Code Generation Rules

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

## 1. Architecture Principles

### 1.1 Complexity Detection (CWE-1120)

**Principle:** Identify O(n²) algorithms, circular dependencies, and unnecessary complexity.

```python
# ❌ WRONG - O(n²) hidden in innocent-looking code
def find_duplicates(items: list[str]) -> list[str]:
    duplicates = []
    for item in items:
        if items.count(item) > 1 and item not in duplicates:  # O(n) inside O(n)
            duplicates.append(item)
    return duplicates

# ✅ CORRECT - O(n) with proper data structure
from collections import Counter

def find_duplicates(items: list[str]) -> list[str]:
    counts = Counter(items)  # O(n)
    return [item for item, count in counts.items() if count > 1]  # O(n)
```

### 1.2 Dependency Management (CWE-1047)

**Principle:** Detect circular dependencies, tight coupling, and dependency direction violations.

```python
# ❌ WRONG - Circular dependency
# file: user_service.py
from order_service import OrderService  # user -> order

class UserService:
    def __init__(self):
        self.orders = OrderService()

# file: order_service.py
from user_service import UserService  # order -> user (CIRCULAR!)

class OrderService:
    def __init__(self):
        self.users = UserService()

# ✅ CORRECT - Dependency inversion
from abc import ABC, abstractmethod

# file: interfaces.py (no dependencies)
class UserRepository(ABC):
    @abstractmethod
    def get_user(self, user_id: str) -> "User": ...

class OrderRepository(ABC):
    @abstractmethod
    def get_orders_for_user(self, user_id: str) -> list["Order"]: ...

# file: user_service.py (depends on interface)
class UserService:
    def __init__(self, user_repo: UserRepository, order_repo: OrderRepository):
        self._users = user_repo
        self._orders = order_repo

    def get_user_with_orders(self, user_id: str):
        user = self._users.get_user(user_id)
        user.orders = self._orders.get_orders_for_user(user_id)
        return user
```

### 1.3 Scalability Analysis

**Principle:** Identify bottlenecks before they become production problems.

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

```python
# ❌ WRONG - Manual dependency tracking
dependencies = []
for file in project_files:
    imports = extract_imports(file)
    dependencies.extend(imports)

# ✅ CORRECT - Structured dependency analysis
from dataclasses import dataclass, field
from pathlib import Path
import ast
from collections import defaultdict

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

class ArchitectureAnalyzer:
    def __init__(self, root: Path):
        self.root = root
        self.modules: dict[str, Module] = {}
        self._layer_rules: dict[str, set[str]] = {}

    def define_layers(self, rules: dict[str, list[str]]):
        """Define allowed dependencies between layers.

        Example:
            {
                "api": ["services", "domain"],
                "services": ["domain", "repositories"],
                "repositories": ["domain"],
                "domain": [],  # No dependencies
            }
        """
        self._layer_rules = {k: set(v) for k, v in rules.items()}

    def analyze(self) -> list[DependencyViolation]:
        violations = []

        # Parse all Python files
        for py_file in self.root.rglob("*.py"):
            self._parse_module(py_file)

        # Build reverse dependency graph
        for mod_name, module in self.modules.items():
            for imp in module.imports:
                if imp in self.modules:
                    self.modules[imp].imported_by.add(mod_name)

        # Check for violations
        violations.extend(self._find_circular_deps())
        violations.extend(self._find_layer_violations())

        return violations

    def _parse_module(self, path: Path):
        rel_path = path.relative_to(self.root)
        mod_name = str(rel_path).replace("/", ".").replace(".py", "")

        try:
            tree = ast.parse(path.read_text())
        except SyntaxError:
            return

        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])

        self.modules[mod_name] = Module(path=path, imports=imports)

    def _find_circular_deps(self) -> list[DependencyViolation]:
        violations = []
        visited = set()
        path_stack = []

        def dfs(mod_name: str):
            if mod_name in path_stack:
                cycle = path_stack[path_stack.index(mod_name):] + [mod_name]
                violations.append(DependencyViolation(
                    source=mod_name,
                    target=path_stack[-1],
                    violation_type="circular",
                    description=f"Circular dependency: {' -> '.join(cycle)}",
                ))
                return

            if mod_name in visited:
                return

            visited.add(mod_name)
            path_stack.append(mod_name)

            module = self.modules.get(mod_name)
            if module:
                for imp in module.imports:
                    if imp in self.modules:
                        dfs(imp)

            path_stack.pop()

        for mod_name in self.modules:
            dfs(mod_name)

        return violations

    def _find_layer_violations(self) -> list[DependencyViolation]:
        violations = []

        for mod_name, module in self.modules.items():
            source_layer = self._get_layer(mod_name)
            if not source_layer:
                continue

            allowed = self._layer_rules.get(source_layer, set())

            for imp in module.imports:
                target_layer = self._get_layer(imp)
                if target_layer and target_layer not in allowed and target_layer != source_layer:
                    violations.append(DependencyViolation(
                        source=mod_name,
                        target=imp,
                        violation_type="layer_skip",
                        description=f"Layer violation: {source_layer} cannot import from {target_layer}",
                    ))

        return violations

    def _get_layer(self, mod_name: str) -> str | None:
        parts = mod_name.split(".")
        for part in parts:
            if part in self._layer_rules:
                return part
        return None
```

### WHEN identifying performance issues, measure complexity

```python
# ❌ WRONG - Subjective complexity assessment
# "This function looks complex"

# ✅ CORRECT - Objective complexity metrics
import ast
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ComplexityReport:
    function_name: str
    file_path: str
    line_number: int
    cyclomatic_complexity: int
    cognitive_complexity: int
    loc: int
    parameter_count: int

    def is_concerning(self) -> bool:
        return (
            self.cyclomatic_complexity > 10 or
            self.cognitive_complexity > 15 or
            self.loc > 50 or
            self.parameter_count > 5
        )

class ComplexityAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.reports: list[ComplexityReport] = []
        self._current_file: str = ""

    def analyze_file(self, path: Path):
        self._current_file = str(path)
        tree = ast.parse(path.read_text())
        self.visit(tree)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        cyclomatic = self._calculate_cyclomatic(node)
        cognitive = self._calculate_cognitive(node)

        self.reports.append(ComplexityReport(
            function_name=node.name,
            file_path=self._current_file,
            line_number=node.lineno,
            cyclomatic_complexity=cyclomatic,
            cognitive_complexity=cognitive,
            loc=node.end_lineno - node.lineno + 1,
            parameter_count=len(node.args.args),
        ))

        self.generic_visit(node)

    def _calculate_cyclomatic(self, node: ast.FunctionDef) -> int:
        """Count decision points."""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.comprehension):
                complexity += 1
                if child.ifs:
                    complexity += len(child.ifs)

        return complexity

    def _calculate_cognitive(self, node: ast.FunctionDef, nesting: int = 0) -> int:
        """Cognitive complexity considers nesting depth."""
        complexity = 0

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1 + nesting  # Nesting penalty
                complexity += self._calculate_cognitive(child, nesting + 1)
            elif isinstance(child, ast.BoolOp):
                complexity += 1
            elif isinstance(child, ast.Try):
                complexity += 1
                for handler in child.handlers:
                    complexity += self._calculate_cognitive(handler, nesting + 1)

        return complexity

def analyze_project(root: Path) -> list[ComplexityReport]:
    analyzer = ComplexityAnalyzer()

    for py_file in root.rglob("*.py"):
        try:
            analyzer.analyze_file(py_file)
        except SyntaxError:
            continue

    # Sort by complexity, worst first
    return sorted(
        analyzer.reports,
        key=lambda r: (r.cyclomatic_complexity, r.cognitive_complexity),
        reverse=True,
    )
```

### WHEN designing APIs, enforce consistency patterns

```python
# ❌ WRONG - Inconsistent API patterns
# GET /users/{id}          -> { user: {...} }
# GET /products/{id}       -> {...}           # Different structure!
# POST /users              -> { id: "123" }
# POST /orders             -> { order_id: "456" }  # Different key!

# ✅ CORRECT - API design consistency checker
from dataclasses import dataclass
from enum import Enum
import re

class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"

@dataclass
class EndpointDefinition:
    method: HTTPMethod
    path: str
    request_schema: dict | None
    response_schema: dict
    status_codes: list[int]

@dataclass
class APIConsistencyViolation:
    endpoint: str
    violation_type: str
    description: str
    recommendation: str

class APIConsistencyChecker:
    def __init__(self):
        self.endpoints: list[EndpointDefinition] = []
        self.violations: list[APIConsistencyViolation] = []

    def add_endpoint(self, endpoint: EndpointDefinition):
        self.endpoints.append(endpoint)

    def check_consistency(self) -> list[APIConsistencyViolation]:
        self.violations = []

        self._check_naming_conventions()
        self._check_response_structure()
        self._check_status_code_usage()
        self._check_crud_completeness()

        return self.violations

    def _check_naming_conventions(self):
        """Check URL path naming consistency."""
        for ep in self.endpoints:
            # Should use kebab-case or snake_case consistently
            if re.search(r'[A-Z]', ep.path):
                self.violations.append(APIConsistencyViolation(
                    endpoint=f"{ep.method.value} {ep.path}",
                    violation_type="naming",
                    description="Path contains uppercase letters",
                    recommendation="Use lowercase with hyphens: /user-profiles instead of /userProfiles",
                ))

            # Should use plural nouns for collections
            parts = ep.path.strip("/").split("/")
            if parts and not parts[0].endswith("s") and "{" not in parts[0]:
                self.violations.append(APIConsistencyViolation(
                    endpoint=f"{ep.method.value} {ep.path}",
                    violation_type="naming",
                    description="Resource name should be plural",
                    recommendation=f"Use /{parts[0]}s instead of /{parts[0]}",
                ))

    def _check_response_structure(self):
        """Check response envelope consistency."""
        envelope_patterns = set()

        for ep in self.endpoints:
            if ep.method == HTTPMethod.GET:
                keys = set(ep.response_schema.keys())
                # Track which wrapper pattern is used
                if "data" in keys:
                    envelope_patterns.add("data_wrapper")
                elif len(keys) == 1:
                    envelope_patterns.add(f"single_key:{list(keys)[0]}")
                else:
                    envelope_patterns.add("direct")

        if len(envelope_patterns) > 1:
            self.violations.append(APIConsistencyViolation(
                endpoint="ALL GET endpoints",
                violation_type="response_structure",
                description=f"Inconsistent response envelopes: {envelope_patterns}",
                recommendation="Use consistent envelope: { data: {...}, meta: {...} }",
            ))

    def _check_status_code_usage(self):
        """Check HTTP status code consistency."""
        post_codes = set()
        for ep in self.endpoints:
            if ep.method == HTTPMethod.POST:
                post_codes.update(ep.status_codes)

        if 200 in post_codes and 201 in post_codes:
            self.violations.append(APIConsistencyViolation(
                endpoint="POST endpoints",
                violation_type="status_codes",
                description="Inconsistent success codes for POST (200 and 201 both used)",
                recommendation="Use 201 Created for resource creation, 200 for actions",
            ))

    def _check_crud_completeness(self):
        """Check if CRUD operations are complete for resources."""
        resources: dict[str, set[HTTPMethod]] = {}

        for ep in self.endpoints:
            # Extract resource name from path
            parts = ep.path.strip("/").split("/")
            if parts:
                resource = parts[0]
                if resource not in resources:
                    resources[resource] = set()
                resources[resource].add(ep.method)

        for resource, methods in resources.items():
            if HTTPMethod.GET in methods and HTTPMethod.POST in methods:
                # If create and read exist, update and delete should too
                if HTTPMethod.PUT not in methods and HTTPMethod.PATCH not in methods:
                    self.violations.append(APIConsistencyViolation(
                        endpoint=f"/{resource}",
                        violation_type="crud_completeness",
                        description="Missing update operation (PUT or PATCH)",
                        recommendation=f"Add PUT or PATCH /{resource}/{{id}} endpoint",
                    ))
```

---

## 4. Anti-Patterns

**NEVER:**
- Ignore O(n²) algorithms in hot paths
- Allow circular dependencies between modules
- Skip layer boundary enforcement
- Accept complexity metrics without investigation
- Design APIs without consistency patterns
- Leave dead code in the codebase
- Create god classes/modules (>500 LOC)

---

## 5. Testing

```python
import pytest
from pathlib import Path
from senior_architect import (
    ArchitectureAnalyzer,
    ComplexityAnalyzer,
    APIConsistencyChecker,
    HTTPMethod,
    EndpointDefinition,
)

class TestArchitectureAnalysis:

    def test_detects_circular_dependency(self, tmp_path):
        """Should detect circular imports."""
        # Create circular dependency
        (tmp_path / "a.py").write_text("from b import B")
        (tmp_path / "b.py").write_text("from a import A")

        analyzer = ArchitectureAnalyzer(tmp_path)
        violations = analyzer.analyze()

        assert any(v.violation_type == "circular" for v in violations)

    def test_detects_layer_violation(self, tmp_path):
        """Should detect layer boundary violations."""
        (tmp_path / "api").mkdir()
        (tmp_path / "api" / "__init__.py").write_text("")
        (tmp_path / "api" / "routes.py").write_text("from repositories import UserRepo")

        (tmp_path / "repositories").mkdir()
        (tmp_path / "repositories" / "__init__.py").write_text("class UserRepo: pass")

        analyzer = ArchitectureAnalyzer(tmp_path)
        analyzer.define_layers({
            "api": ["services"],  # api can only import services
            "services": ["repositories"],
            "repositories": [],
        })

        violations = analyzer.analyze()
        assert any(v.violation_type == "layer_skip" for v in violations)

class TestComplexityAnalysis:

    def test_high_cyclomatic_complexity_flagged(self, tmp_path):
        """Should flag functions with high cyclomatic complexity."""
        complex_code = """
def complex_function(a, b, c, d, e):
    if a:
        if b:
            if c:
                if d:
                    if e:
                        return 1
    return 0
"""
        (tmp_path / "complex.py").write_text(complex_code)

        analyzer = ComplexityAnalyzer()
        analyzer.analyze_file(tmp_path / "complex.py")

        assert len(analyzer.reports) == 1
        assert analyzer.reports[0].cyclomatic_complexity >= 5
        assert analyzer.reports[0].is_concerning()

class TestAPIConsistency:

    def test_detects_naming_inconsistency(self):
        """Should flag inconsistent naming."""
        checker = APIConsistencyChecker()
        checker.add_endpoint(EndpointDefinition(
            method=HTTPMethod.GET,
            path="/userProfiles",  # Wrong: camelCase
            request_schema=None,
            response_schema={"data": {}},
            status_codes=[200],
        ))

        violations = checker.check_consistency()
        assert any(v.violation_type == "naming" for v in violations)

    def test_detects_response_inconsistency(self):
        """Should flag inconsistent response structures."""
        checker = APIConsistencyChecker()
        checker.add_endpoint(EndpointDefinition(
            method=HTTPMethod.GET,
            path="/users",
            request_schema=None,
            response_schema={"data": []},  # Uses data wrapper
            status_codes=[200],
        ))
        checker.add_endpoint(EndpointDefinition(
            method=HTTPMethod.GET,
            path="/products",
            request_schema=None,
            response_schema={"products": []},  # Different wrapper
            status_codes=[200],
        ))

        violations = checker.check_consistency()
        assert any(v.violation_type == "response_structure" for v in violations)
```

---

## 6. Pre-Generation Checklist

**BEFORE generating architectural code:**

- [ ] Complexity check: No O(n²) in hot paths
- [ ] Dependency graph: No circular dependencies
- [ ] Layer rules: Dependency direction enforced
- [ ] API consistency: Naming, responses, status codes uniform
- [ ] Dead code: Removed unused code paths
- [ ] Module size: No files > 500 LOC
- [ ] Function complexity: Cyclomatic < 10, cognitive < 15
- [ ] Parameter count: Functions have < 5 parameters

**Templates**: See `assets/` for reusable output templates.

---

**Performance**: Quality over speed. Verify all code examples compile. Never skip security checks. See `template-references/performance-notes.md` for full guidelines.