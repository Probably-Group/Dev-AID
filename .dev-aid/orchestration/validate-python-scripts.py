#!/usr/bin/env python3
"""
Validates Python files for python skill compliance using AST analysis.

Usage:
    validate-python-scripts.py [--strict] [--skip-tests] [directory ...]

Default: scans .dev-aid/orchestration/ and .dev-aid/local-search/
Excludes: venv/, __pycache__/, .git/
"""

import argparse
import ast
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Tuple


# ── Data Types ───────────────────────────────────────────────────────────────


class Violation(NamedTuple):
    """A single compliance violation."""

    file: str
    line: int
    check: str
    message: str
    severity: str  # "FAIL" or "WARN"


# ── Colors ───────────────────────────────────────────────────────────────────

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
BOLD = "\033[1m"
NC = "\033[0m"


def color(text: str, code: str) -> str:
    """Wrap text in ANSI color code."""
    if not sys.stdout.isatty():
        return text
    return f"{code}{text}{NC}"


# ── AST Checks ──────────────────────────────────────────────────────────────


def check_shell_true(tree: ast.Module, filepath: str) -> List[Violation]:
    """Detect subprocess calls with shell=True."""
    violations: List[Violation] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        for kw in node.keywords:
            if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                violations.append(
                    Violation(
                        file=filepath,
                        line=node.lineno,
                        check="shell=True",
                        message="subprocess call with shell=True",
                        severity="FAIL",
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
                    file=filepath,
                    line=node.lineno,
                    check="eval/exec",
                    message=f"use of {func_name}()",
                    severity="FAIL",
                )
            )
    return violations


def check_pickle_load(tree: ast.Module, filepath: str) -> List[Violation]:
    """Detect pickle.load/pickle.loads calls."""
    violations: List[Violation] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Attribute) and node.func.attr in ("load", "loads"):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "pickle":
                violations.append(
                    Violation(
                        file=filepath,
                        line=node.lineno,
                        check="pickle",
                        message=f"use of pickle.{node.func.attr}() (deserialization risk)",
                        severity="FAIL",
                    )
                )
    return violations


# Patterns that suggest hardcoded secrets
SECRET_PATTERNS = re.compile(
    r"(api[_-]?key|secret[_-]?key|password|token|auth[_-]?token|private[_-]?key)"
    r"\s*=\s*['\"][^'\"]{8,}['\"]",
    re.IGNORECASE,
)


def check_hardcoded_secrets(tree: ast.Module, filepath: str, source: str) -> List[Violation]:
    """Detect potential hardcoded secrets in string literals."""
    violations: List[Violation] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
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
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        val = node.value.value
                        # Skip obvious placeholders/empty
                        if len(val) > 8 and not val.startswith(("{", "<", "your_", "CHANGE")):
                            violations.append(
                                Violation(
                                    file=filepath,
                                    line=node.lineno,
                                    check="hardcoded-secret",
                                    message=f"possible hardcoded secret in '{target_name}'",
                                    severity="WARN",
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
                    file=filepath,
                    line=node.lineno,
                    check="generic-except",
                    message="bare except: (catch specific exceptions)",
                    severity="FAIL",
                )
            )
        elif isinstance(node.type, ast.Name) and node.type.id == "Exception":
            violations.append(
                Violation(
                    file=filepath,
                    line=node.lineno,
                    check="generic-except",
                    message="except Exception (catch specific exceptions)",
                    severity="FAIL",
                )
            )
    return violations


def _is_in_main_block(node: ast.AST, tree: ast.Module) -> bool:
    """Check if a node is inside an if __name__ == '__main__' block."""
    for top_node in ast.walk(tree):
        if not isinstance(top_node, ast.If):
            continue
        # Check: if __name__ == "__main__"
        test = top_node.test
        if isinstance(test, ast.Compare):
            if (
                isinstance(test.left, ast.Name)
                and test.left.id == "__name__"
                and len(test.comparators) == 1
                and isinstance(test.comparators[0], ast.Constant)
                and test.comparators[0].value == "__main__"
            ):
                # Check if our node is in this block's body
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
                        file=filepath,
                        line=node.lineno,
                        check="print-in-lib",
                        message="print() in library code (use logging instead)",
                        severity="WARN",
                    )
                )
    return violations


def check_type_annotations(tree: ast.Module, filepath: str) -> List[Violation]:
    """Check that function definitions have return type annotations."""
    violations: List[Violation] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        # Skip __init__ and dunder methods
        if node.name.startswith("__") and node.name.endswith("__"):
            continue
        if node.returns is None:
            violations.append(
                Violation(
                    file=filepath,
                    line=node.lineno,
                    check="type-annotation",
                    message=f"function '{node.name}' missing return type annotation",
                    severity="WARN",
                )
            )
    return violations


# ── File Discovery ───────────────────────────────────────────────────────────

EXCLUDE_DIRS = {"venv", "__pycache__", ".git", ".mypy_cache", ".pytest_cache", "node_modules"}


def find_python_files(directory: Path) -> List[Path]:
    """Find all Python files in directory, excluding venv and __pycache__."""
    results: List[Path] = []
    if not directory.is_dir():
        return results
    for root_str, dirs, files in os.walk(directory):
        # Prune excluded directories in-place
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for fname in sorted(files):
            if fname.endswith(".py"):
                results.append(Path(root_str) / fname)
    return results


def is_test_file(filepath: Path) -> bool:
    """Check if a file is a test file."""
    name = filepath.name
    return name.startswith("test_") or name.endswith("_test.py") or "conftest" in name


# ── Validation Runner ────────────────────────────────────────────────────────


def validate_file(filepath: Path, base_dir: Path, is_test: bool) -> List[Violation]:
    """Run all AST-based checks on a single Python file."""
    violations: List[Violation] = []
    rel_path = str(filepath.relative_to(base_dir))

    try:
        source = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        violations.append(
            Violation(
                file=rel_path,
                line=0,
                check="parse",
                message=f"could not read file: {exc}",
                severity="FAIL",
            )
        )
        return violations

    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError as exc:
        violations.append(
            Violation(
                file=rel_path,
                line=exc.lineno or 0,
                check="syntax",
                message=f"syntax error: {exc.msg}",
                severity="FAIL",
            )
        )
        return violations

    # Always run these checks
    violations.extend(check_shell_true(tree, rel_path))
    violations.extend(check_eval_exec(tree, rel_path))
    violations.extend(check_pickle_load(tree, rel_path))

    # Skip certain checks for test files
    if not is_test:
        violations.extend(check_generic_exceptions(tree, rel_path))
        violations.extend(check_hardcoded_secrets(tree, rel_path, source))
        violations.extend(check_print_in_libs(tree, rel_path))
        violations.extend(check_type_annotations(tree, rel_path))

    return violations


def run_coverage_check(directory: Path) -> Tuple[bool, str]:
    """Run pytest with coverage threshold check."""
    venv_python = directory / "venv" / "bin" / "python"
    if not venv_python.exists():
        return False, f"venv not found at {venv_python}"

    try:
        result = subprocess.run(
            [
                str(venv_python),
                "-m",
                "pytest",
                str(directory / "tests"),
                "--cov=router",
                "--cov-fail-under=80",
                "--tb=short",
                "-q",
            ],
            capture_output=True,
            text=True,
            cwd=str(directory),
            timeout=120,
        )
        if result.returncode == 0:
            return True, "coverage >= 80%"
        # Extract the coverage line
        for line in result.stdout.splitlines():
            if "TOTAL" in line or "Required" in line or "FAIL" in line:
                return False, line.strip()
        return False, f"pytest exited with code {result.returncode}"
    except subprocess.TimeoutExpired:
        return False, "pytest timed out (120s)"
    except FileNotFoundError as exc:
        return False, f"could not run pytest: {exc}"


# ── Output ───────────────────────────────────────────────────────────────────


def print_violations(violations: List[Violation], strict: bool) -> Tuple[int, int, int]:
    """Print violations grouped by file, return (pass_count, fail_count, warn_count)."""
    fail_count = 0
    warn_count = 0

    # Group by file
    by_file: Dict[str, List[Violation]] = {}
    for v in violations:
        by_file.setdefault(v.file, []).append(v)

    for filepath, file_violations in sorted(by_file.items()):
        print(f"\n{color(f'── {filepath} ──', BOLD)}")
        for v in sorted(file_violations, key=lambda x: x.line):
            sev = v.severity
            if strict and sev == "WARN":
                sev = "FAIL"

            if sev == "FAIL":
                tag = color("FAIL", RED)
                fail_count += 1
            else:
                tag = color("WARN", YELLOW)
                warn_count += 1

            line_ref = f":{v.line}" if v.line > 0 else ""
            print(f"  {tag}  [{v.check}] {v.message} ({filepath}{line_ref})")

    # Total checks = files_with_no_violations * checks_per_file + violations
    pass_count = 0  # We'll calculate from totals
    return pass_count, fail_count, warn_count


# ── Main ─────────────────────────────────────────────────────────────────────


def main() -> int:
    """Entry point. Returns exit code."""
    parser = argparse.ArgumentParser(description="Python skill compliance validator (AST-based)")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat WARN as FAIL",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip pytest/coverage check (faster lint-only mode)",
    )
    parser.add_argument(
        "directories",
        nargs="*",
        help="Directories to scan (default: orchestration + local-search)",
    )
    args = parser.parse_args()

    # Determine script location and project root
    script_dir = Path(__file__).resolve().parent
    dev_aid_dir = script_dir.parent

    # Default directories
    if args.directories:
        scan_dirs = [Path(d).resolve() for d in args.directories]
    else:
        scan_dirs = [
            dev_aid_dir / "orchestration",
            dev_aid_dir / "local-search",
        ]

    print(f"{color('Python Skill Compliance Validator', BOLD)}")
    print("========================================")
    if args.strict:
        print(color("Mode: STRICT (WARN → FAIL)", YELLOW))
    if args.skip_tests:
        print(color("Mode: SKIP-TESTS (no pytest/coverage)", BLUE))

    all_violations: List[Violation] = []
    total_files = 0

    for scan_dir in scan_dirs:
        if not scan_dir.is_dir():
            print(f"\n{color(f'Directory not found: {scan_dir}', RED)}")
            continue

        py_files = find_python_files(scan_dir)
        print(f"\nScanning: {scan_dir.relative_to(dev_aid_dir)} ({len(py_files)} files)")

        for pyfile in py_files:
            is_test = is_test_file(pyfile)
            violations = validate_file(pyfile, dev_aid_dir, is_test)
            all_violations.extend(violations)
            total_files += 1

    # Coverage check
    if not args.skip_tests:
        orchestration_dir = dev_aid_dir / "orchestration"
        if orchestration_dir.is_dir():
            print(f"\n{color('── Coverage Check ──', BOLD)}")
            passed, msg = run_coverage_check(orchestration_dir)
            if passed:
                print(f"  {color('PASS', GREEN)}  [coverage] {msg}")
            else:
                print(f"  {color('FAIL', RED)}  [coverage] {msg}")
                all_violations.append(
                    Violation(
                        file="pytest",
                        line=0,
                        check="coverage",
                        message=msg,
                        severity="FAIL",
                    )
                )

    # Print violations
    if all_violations:
        _, fail_count, warn_count = print_violations(all_violations, args.strict)
    else:
        fail_count = 0
        warn_count = 0

    # Compute pass count from total checks
    # Each file gets 7 checks (shell_true, eval_exec, pickle, generic_except,
    # secrets, print, type_annot) minus test-skipped ones
    total_checks = total_files * 7  # approximate
    pass_count = max(0, total_checks - fail_count - warn_count)

    # Summary
    print("\n========================================")
    print(f"{color('Summary', BOLD)}")
    print("========================================")
    print(f"Files scanned: {total_files}")
    print(f"{color('PASS:', GREEN)} ~{pass_count} (checks with no violations)")
    print(f"{color('FAIL:', RED)} {fail_count}")
    print(f"{color('WARN:', YELLOW)} {warn_count}")
    print(f"Total violations: {len(all_violations)}")
    print()

    if fail_count > 0:
        print(color(f"RESULT: FAILED ({fail_count} failure(s))", RED))
        return 1
    else:
        print(color(f"RESULT: PASSED ({warn_count} warning(s))", GREEN))
        return 0


if __name__ == "__main__":
    sys.exit(main())
