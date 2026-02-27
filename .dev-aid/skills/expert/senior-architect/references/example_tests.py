# Reference implementation — extracted from senior-architect/SKILL.md for context reduction
#
# Example tests for ArchitectureAnalyzer, ComplexityAnalyzer, and APIConsistencyChecker.
# Demonstrates how to write architectural validation tests with tmp_path fixtures.

import pytest
from pathlib import Path

from architecture_analyzer import ArchitectureAnalyzer
from complexity_analyzer import ComplexityAnalyzer
from api_consistency_checker import (
    APIConsistencyChecker,
    HTTPMethod,
    EndpointDefinition,
)


class TestArchitectureAnalysis:

    def test_detects_circular_dependency(self, tmp_path):
        """Should detect circular imports."""
        (tmp_path / "a.py").write_text("from b import B")
        (tmp_path / "b.py").write_text("from a import A")

        analyzer = ArchitectureAnalyzer(tmp_path)
        violations = analyzer.analyze()

        assert any(v.violation_type == "circular" for v in violations)

    def test_detects_layer_violation(self, tmp_path):
        """Should detect layer boundary violations."""
        (tmp_path / "api").mkdir()
        (tmp_path / "api" / "__init__.py").write_text("")
        (tmp_path / "api" / "routes.py").write_text(
            "from repositories import UserRepo"
        )

        (tmp_path / "repositories").mkdir()
        (tmp_path / "repositories" / "__init__.py").write_text("class UserRepo: pass")

        analyzer = ArchitectureAnalyzer(tmp_path)
        analyzer.define_layers(
            {
                "api": ["services"],  # api can only import services
                "services": ["repositories"],
                "repositories": [],
            }
        )

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
        checker.add_endpoint(
            EndpointDefinition(
                method=HTTPMethod.GET,
                path="/userProfiles",  # Wrong: camelCase
                request_schema=None,
                response_schema={"data": {}},
                status_codes=[200],
            )
        )

        violations = checker.check_consistency()
        assert any(v.violation_type == "naming" for v in violations)

    def test_detects_response_inconsistency(self):
        """Should flag inconsistent response structures."""
        checker = APIConsistencyChecker()
        checker.add_endpoint(
            EndpointDefinition(
                method=HTTPMethod.GET,
                path="/users",
                request_schema=None,
                response_schema={"data": []},  # Uses data wrapper
                status_codes=[200],
            )
        )
        checker.add_endpoint(
            EndpointDefinition(
                method=HTTPMethod.GET,
                path="/products",
                request_schema=None,
                response_schema={"products": []},  # Different wrapper
                status_codes=[200],
            )
        )

        violations = checker.check_consistency()
        assert any(v.violation_type == "response_structure" for v in violations)
