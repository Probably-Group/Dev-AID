# Reference implementation — extracted from senior-architect/SKILL.md for context reduction
#
# ComplexityAnalyzer: AST-based cyclomatic and cognitive complexity measurement.
# Walks Python AST to count decision points (cyclomatic) and nesting-weighted
# branches (cognitive). Flags functions exceeding thresholds:
#   cyclomatic > 10, cognitive > 15, LOC > 50, parameters > 5.

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
            self.cyclomatic_complexity > 10
            or self.cognitive_complexity > 15
            or self.loc > 50
            or self.parameter_count > 5
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

        self.reports.append(
            ComplexityReport(
                function_name=node.name,
                file_path=self._current_file,
                line_number=node.lineno,
                cyclomatic_complexity=cyclomatic,
                cognitive_complexity=cognitive,
                loc=node.end_lineno - node.lineno + 1,
                parameter_count=len(node.args.args),
            )
        )

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
