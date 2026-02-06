#!/usr/bin/env python3
"""
Python Skill Compliance Validator (AST-based).

Validates Python files against python skill standards:
  1. subprocess calls with shell=True
  2. eval()/exec() calls
  3. pickle.load/pickle.loads
  4. Hardcoded secrets in string literals
  5. Bare except: or except Exception
  6. print() outside __main__ blocks
  7. Missing return type annotations
  8. Test coverage >= 80% (optional, if tests/ dir exists)

Usage:
    validate.py [--strict] [--json] [--target-dir <dir>] [--skip-tests] [files...]
"""

import ast
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

# Import shared validator library
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "lib"))
from validator_common import (  # noqa: E402
    Violation,
    ValidatorResult,
    create_argument_parser,
    run_validator_main,
    find_files,
)

VALIDATOR_NAME = "python"
SKILL_PATH = str(Path(__file__).resolve().parent)


# ── AST Checks ───────────────────────────────────────────────────────────────


def check_shell_true(tree: ast.Module, filepath: str) -> List[Violation]:
    """Detect subprocess calls with shell=True."""
    violations: List[Violation] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        for kw in node.keywords:
            if (
                kw.arg == "shell"
                and isinstance(kw.value, ast.Constant)
                and kw.value.value is True
            ):
                violations.append(
                    Violation(
                        filepath, node.lineno, "shell=True",
                        "subprocess call with shell=True", "FAIL",
                    )
                )
    return violations


def check_eval_exec(tree: ast.Module, filepath: str) -> List[Violation]:
    """Detect eval() and exec() calls."""
    violations: List[Violation] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func_name: Optional[str] = None
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        if func_name in ("eval", "exec"):
            violations.append(
                Violation(
                    filepath, node.lineno, "eval/exec",
                    f"use of {func_name}()", "FAIL",
                )
            )
    return violations


def check_pickle_load(tree: ast.Module, filepath: str) -> List[Violation]:
    """Detect pickle.load/pickle.loads calls."""
    violations: List[Violation] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Attribute) and node.func.attr in (
            "load",
            "loads",
        ):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "pickle":
                violations.append(
                    Violation(
                        filepath, node.lineno, "pickle",
                        f"use of pickle.{node.func.attr}() (deserialization risk)",
                        "FAIL",
                    )
                )
    return violations


SECRET_PATTERNS = re.compile(
    r"(api[_-]?key|secret[_-]?key|password|token|auth[_-]?token|private[_-]?key)"
    r"\s*=\s*['\"][^'\"]{8,}['\"]",
    re.IGNORECASE,
)


def check_hardcoded_secrets(
    tree: ast.Module, filepath: str
) -> List[Violation]:
    """Detect potential hardcoded secrets in string literals."""
    violations: List[Violation] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            target_name = ""
            if isinstance(target, ast.Name):
                target_name = target.id
            elif isinstance(target, ast.Attribute):
                target_name = target.attr
            if not target_name:
                continue
            lower_name = target_name.lower()
            if any(
                pat in lower_name
                for pat in ("api_key", "secret", "password", "token", "private_key")
            ):
                if isinstance(node.value, ast.Constant) and isinstance(
                    node.value.value, str
                ):
                    val = node.value.value
                    if len(val) > 8 and not val.startswith(
                        ("{", "<", "your_", "CHANGE")
                    ):
                        violations.append(
                            Violation(
                                filepath, node.lineno, "hardcoded-secret",
                                f"possible hardcoded secret in '{target_name}'",
                                "WARN",
                            )
                        )
    return violations


def check_generic_exceptions(tree: ast.Module, filepath: str) -> List[Violation]:
    """Detect bare except: or except Exception."""
    violations: List[Violation] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ExceptHandler):
            continue
        if node.type is None:
            violations.append(
                Violation(
                    filepath, node.lineno, "generic-except",
                    "bare except: (catch specific exceptions)", "FAIL",
                )
            )
        elif isinstance(node.type, ast.Name) and node.type.id == "Exception":
            violations.append(
                Violation(
                    filepath, node.lineno, "generic-except",
                    "except Exception (catch specific exceptions)", "FAIL",
                )
            )
    return violations


def _is_in_main_block(node: ast.AST, tree: ast.Module) -> bool:
    """Check if a node is inside an if __name__ == '__main__' block."""
    for top_node in ast.walk(tree):
        if not isinstance(top_node, ast.If):
            continue
        test = top_node.test
        if isinstance(test, ast.Compare):
            if (
                isinstance(test.left, ast.Name)
                and test.left.id == "__name__"
                and len(test.comparators) == 1
                and isinstance(test.comparators[0], ast.Constant)
                and test.comparators[0].value == "__main__"
            ):
                for child in ast.walk(top_node):
                    if child is node:
                        return True
    return False


def check_print_in_libs(tree: ast.Module, filepath: str) -> List[Violation]:
    """Detect print() calls outside if __name__ == '__main__' blocks."""
    violations: List[Violation] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            if not _is_in_main_block(node, tree):
                violations.append(
                    Violation(
                        filepath, node.lineno, "print-in-lib",
                        "print() in library code (use logging instead)", "WARN",
                    )
                )
    return violations


def check_type_annotations(tree: ast.Module, filepath: str) -> List[Violation]:
    """Check that function definitions have return type annotations."""
    violations: List[Violation] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name.startswith("__") and node.name.endswith("__"):
            continue
        if node.returns is None:
            violations.append(
                Violation(
                    filepath, node.lineno, "type-annotation",
                    f"function '{node.name}' missing return type annotation",
                    "WARN",
                )
            )
    return violations


# ── Coverage Check ───────────────────────────────────────────────────────────


def run_coverage_check(
    directory: Path, filepath: str
) -> List[Violation]:
    """Run pytest with coverage threshold if tests/ dir exists."""
    tests_dir = directory / "tests"
    if not tests_dir.is_dir():
        return []

    # Try to find venv python
    venv_python = directory / "venv" / "bin" / "python"
    if not venv_python.exists():
        venv_python = directory / ".venv" / "bin" / "python"
    if not venv_python.exists():
        return []  # No venv, skip coverage

    try:
        result = subprocess.run(
            [
                str(venv_python), "-m", "pytest",
                str(tests_dir),
                "--cov-fail-under=80",
                "--tb=short", "-q",
            ],
            capture_output=True,
            text=True,
            cwd=str(directory),
            timeout=120,
        )
        if result.returncode == 0:
            return []
        for line in result.stdout.splitlines():
            if "TOTAL" in line or "Required" in line or "FAIL" in line:
                return [Violation(filepath, 0, "coverage", line.strip(), "FAIL")]
        return [
            Violation(filepath, 0, "coverage", f"pytest exited with code {result.returncode}", "FAIL")
        ]
    except subprocess.TimeoutExpired:
        return [Violation(filepath, 0, "coverage", "pytest timed out (120s)", "FAIL")]
    except FileNotFoundError as exc:
        return [Violation(filepath, 0, "coverage", f"could not run pytest: {exc}", "FAIL")]


# ── File Classification ──────────────────────────────────────────────────────


def is_test_file(filepath: Path) -> bool:
    """Check if a file is a test file."""
    name = filepath.name
    return name.startswith("test_") or name.endswith("_test.py") or "conftest" in name


# ── Main Validation ──────────────────────────────────────────────────────────


def validate_file(
    filepath: Path, base_dir: Path
) -> List[Violation]:
    """Run all AST-based checks on a single Python file."""
    violations: List[Violation] = []
    try:
        rel_path = str(filepath.relative_to(base_dir))
    except ValueError:
        rel_path = str(filepath)
    is_test = is_test_file(filepath)

    try:
        source = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [Violation(rel_path, 0, "parse", f"could not read file: {exc}", "FAIL")]

    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError as exc:
        return [Violation(rel_path, exc.lineno or 0, "syntax", f"syntax error: {exc.msg}", "FAIL")]

    # Always run security checks
    violations.extend(check_shell_true(tree, rel_path))
    violations.extend(check_eval_exec(tree, rel_path))
    violations.extend(check_pickle_load(tree, rel_path))

    # Skip certain checks for test files
    if not is_test:
        violations.extend(check_generic_exceptions(tree, rel_path))
        violations.extend(check_hardcoded_secrets(tree, rel_path))
        violations.extend(check_print_in_libs(tree, rel_path))
        violations.extend(check_type_annotations(tree, rel_path))

    return violations


def main() -> int:
    """Entry point."""
    parser = create_argument_parser(
        "python-validator",
        "Python Skill Compliance Validator (AST-based)",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip pytest/coverage check",
    )
    args = parser.parse_args()

    target_dir = Path(args.target_dir).resolve()

    # Determine files to scan
    if args.files:
        py_files = [Path(f).resolve() for f in args.files]
    else:
        py_files = find_files(str(target_dir), [".py"])

    all_violations: List[Violation] = []
    for pyfile in py_files:
        all_violations.extend(validate_file(pyfile, target_dir))

    # Coverage check (optional)
    if not args.skip_tests:
        all_violations.extend(run_coverage_check(target_dir, "pytest"))

    result = ValidatorResult(
        name="Python Compliance",
        skill_path=SKILL_PATH,
        files_scanned=len(py_files),
        violations=all_violations,
    )

    return run_validator_main(result, args)


if __name__ == "__main__":
    sys.exit(main())
