# Reference implementation — extracted from senior-architect/SKILL.md for context reduction
#
# ArchitectureAnalyzer: Structured dependency analysis with circular dependency
# detection and layer boundary enforcement. Uses AST parsing to build a full
# module dependency graph, then runs DFS for cycle detection and validates
# imports against defined layer rules.

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
                cycle = path_stack[path_stack.index(mod_name) :] + [mod_name]
                violations.append(
                    DependencyViolation(
                        source=mod_name,
                        target=path_stack[-1],
                        violation_type="circular",
                        description=f"Circular dependency: {' -> '.join(cycle)}",
                    )
                )
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
                if (
                    target_layer
                    and target_layer not in allowed
                    and target_layer != source_layer
                ):
                    violations.append(
                        DependencyViolation(
                            source=mod_name,
                            target=imp,
                            violation_type="layer_skip",
                            description=f"Layer violation: {source_layer} cannot import from {target_layer}",
                        )
                    )

        return violations

    def _get_layer(self, mod_name: str) -> str | None:
        parts = mod_name.split(".")
        for part in parts:
            if part in self._layer_rules:
                return part
        return None
