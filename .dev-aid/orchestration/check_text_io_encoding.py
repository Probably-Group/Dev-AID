#!/usr/bin/env python3
"""
Pre-commit guard: catch Path.write_text() / Path.read_text() calls that omit
`encoding="utf-8"` in files that contain non-ASCII string literals.

Why this exists
---------------
On Windows, Python's default text encoding is cp1252 (or whatever the active
locale is), not UTF-8. A test that does:

    log_line = "Tokens: 10→20\n"
    log_path.write_text(log_line)

passes on macOS/Linux but blows up on Windows CI with:

    UnicodeEncodeError: 'charmap' codec can't encode character '\u2192'

The bug can be subtle: the non-ASCII char may be in a string literal several
lines above the call, or even constructed inside the production code that the
test then reads back via `read_text()`. Both forms have hit Dev-AID Windows CI.

Heuristic
---------
For each file, walk the AST. For every `write_text(...)`/`read_text(...)` call
that omits `encoding=`, check whether the *enclosing function/method* contains
any string literal with a non-ASCII character. If yes, flag the call. We scope
to the function (not the whole file) to avoid false positives from unrelated
docstrings while still catching the common case where the data being written
is built up a few lines above the call.

Usage
-----
    python check_text_io_encoding.py path/to/file1.py path/to/file2.py
    python check_text_io_encoding.py  # no args = scan entire .dev-aid/orchestration

Exit codes
----------
    0 = clean
    1 = violations found
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import List, Tuple

TARGET_METHODS = {"write_text", "read_text"}


def _scope_has_non_ascii_string(scope: ast.AST) -> bool:
    """True if `scope` contains any non-ASCII str constant.

    Skips the function's own docstring (it's not data being written to disk)
    so things like \"\"\"Tests for foo — covers X\"\"\" don't trigger false positives.
    """
    body = getattr(scope, "body", None)
    docstring_node: ast.AST | None = None
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
        if isinstance(body[0].value.value, str):
            docstring_node = body[0]

    for node in ast.walk(scope):
        if node is docstring_node:
            continue
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if any(ord(c) > 127 for c in node.value):
                return True
    return False


def _enclosing_function(parents: dict[int, ast.AST], node: ast.AST) -> ast.AST | None:
    """Walk up parent chain to find the nearest FunctionDef/AsyncFunctionDef."""
    cur = parents.get(id(node))
    while cur is not None:
        if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return cur
        cur = parents.get(id(cur))
    return None


def scan_file(path: Path) -> List[Tuple[int, str]]:
    """Return a list of (line_no, method_name) for risky calls in this file."""
    try:
        src = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    try:
        tree = ast.parse(src, filename=str(path))
    except SyntaxError:
        # Don't block commits on unrelated syntax errors — flake8 will catch those.
        return []

    # Build a parent map so we can find each call's enclosing function.
    parents: dict[int, ast.AST] = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[id(child)] = parent

    violations: List[Tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr not in TARGET_METHODS:
            continue
        if any(kw.arg == "encoding" for kw in node.keywords):
            continue

        scope = _enclosing_function(parents, node) or tree
        if _scope_has_non_ascii_string(scope):
            violations.append((node.lineno, node.func.attr))

    return violations


def iter_default_targets() -> List[Path]:
    root = Path(__file__).parent
    paths: List[Path] = []
    for p in root.rglob("*.py"):
        if any(part in {"venv", ".venv", "__pycache__", "node_modules"} for part in p.parts):
            continue
        paths.append(p)
    return paths


def main(argv: List[str]) -> int:
    if argv:
        targets = [Path(a) for a in argv if a.endswith(".py")]
    else:
        targets = iter_default_targets()

    if not targets:
        return 0

    total_violations = 0
    for path in targets:
        if not path.exists():
            continue
        for line_no, method in scan_file(path):
            total_violations += 1
            print(
                f'{path}:{line_no}: {method}() called without encoding="utf-8" '
                f"in a function that uses non-ASCII string literals",
                file=sys.stderr,
            )

    if total_violations:
        print("", file=sys.stderr)
        print(
            f"❌ {total_violations} risky text I/O call(s) found.\n"
            "   These crash on Windows (cp1252) when the literal contains non-ASCII\n"
            '   characters. Add encoding="utf-8" to fix.',
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
