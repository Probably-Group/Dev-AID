#!/usr/bin/env python3
"""
Shared library for Dev-AID skill compliance validators.

Provides common types, argument parsing, output formatting, and file discovery
used by all validate.py scripts across skills.
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Sequence

# ── ANSI Colors ──────────────────────────────────────────────────────────────

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
BOLD = "\033[1m"
NC = "\033[0m"


def _color(text: str, code: str) -> str:
    """Wrap text in ANSI color code (only if stdout is a TTY)."""
    if not sys.stdout.isatty():
        return text
    return f"{code}{text}{NC}"


# ── Data Types ───────────────────────────────────────────────────────────────


class Violation(NamedTuple):
    """A single compliance violation."""

    file: str
    line: int
    check: str
    message: str
    severity: str  # "FAIL" or "WARN"


@dataclass
class ValidatorResult:
    """Wraps a validator's complete output."""

    name: str
    skill_path: str
    files_scanned: int
    violations: List[Violation] = field(default_factory=list)

    @property
    def fail_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == "FAIL")

    @property
    def warn_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == "WARN")

    def to_dict(self, strict: bool = False) -> Dict:
        """Serialize to dict for JSON output."""
        violations_list = []
        for v in self.violations:
            sev = "FAIL" if (strict and v.severity == "WARN") else v.severity
            violations_list.append(
                {
                    "file": v.file,
                    "line": v.line,
                    "check": v.check,
                    "message": v.message,
                    "severity": sev,
                }
            )
        fail = sum(1 for v in violations_list if v["severity"] == "FAIL")
        warn = sum(1 for v in violations_list if v["severity"] == "WARN")
        return {
            "name": self.name,
            "skill_path": self.skill_path,
            "files_scanned": self.files_scanned,
            "violations": violations_list,
            "totals": {"fail": fail, "warn": warn},
            "status": "FAIL" if fail > 0 else "PASS",
        }


# ── Argument Parsing ─────────────────────────────────────────────────────────


def create_argument_parser(name: str, description: str) -> argparse.ArgumentParser:
    """Create a standard argument parser for validators."""
    parser = argparse.ArgumentParser(
        prog=name,
        description=description,
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat WARN as FAIL",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--target-dir",
        type=str,
        default=".",
        help="Directory to scan (default: current directory)",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Specific files to validate (overrides --target-dir)",
    )
    return parser


# ── Output Formatting ────────────────────────────────────────────────────────


def format_text_report(result: ValidatorResult, strict: bool = False) -> str:
    """Format a ValidatorResult as colored text output."""
    lines: List[str] = []
    lines.append(f"{_color(result.name, BOLD)}")
    lines.append("=" * 40)
    if strict:
        lines.append(_color("Mode: STRICT (WARN -> FAIL)", YELLOW))

    fail_count = 0
    warn_count = 0

    # Group violations by file
    by_file: Dict[str, List[Violation]] = {}
    for v in result.violations:
        by_file.setdefault(v.file, []).append(v)

    if by_file:
        for filepath, file_violations in sorted(by_file.items()):
            lines.append(f"\n{_color(f'-- {filepath} --', BOLD)}")
            for v in sorted(file_violations, key=lambda x: x.line):
                sev = v.severity
                if strict and sev == "WARN":
                    sev = "FAIL"

                if sev == "FAIL":
                    tag = _color("FAIL", RED)
                    fail_count += 1
                else:
                    tag = _color("WARN", YELLOW)
                    warn_count += 1

                line_ref = f":{v.line}" if v.line > 0 else ""
                lines.append(
                    f"  {tag}  [{v.check}] {v.message} ({filepath}{line_ref})"
                )
    else:
        lines.append(f"\n  {_color('PASS', GREEN)}  All checks passed")

    lines.append("\n" + "=" * 40)
    lines.append(f"Files scanned: {result.files_scanned}")
    lines.append(f"{_color('FAIL:', RED)} {fail_count}")
    lines.append(f"{_color('WARN:', YELLOW)} {warn_count}")

    if fail_count > 0:
        lines.append(
            _color(f"\nRESULT: FAILED ({fail_count} failure(s))", RED)
        )
    else:
        lines.append(
            _color(f"\nRESULT: PASSED ({warn_count} warning(s))", GREEN)
        )

    return "\n".join(lines)


def format_json_report(result: ValidatorResult, strict: bool = False) -> str:
    """Format a ValidatorResult as JSON."""
    return json.dumps(result.to_dict(strict), indent=2)


# ── Entry Point ──────────────────────────────────────────────────────────────


def run_validator_main(result: ValidatorResult, args: argparse.Namespace) -> int:
    """
    Standard entry point: format output based on args and return exit code.

    Returns:
        0 if all checks pass, 1 if any FAIL found.
    """
    if args.json_output:
        print(format_json_report(result, strict=args.strict))
    else:
        print(format_text_report(result, strict=args.strict))

    d = result.to_dict(strict=args.strict)
    return 1 if d["totals"]["fail"] > 0 else 0


# ── File Discovery ───────────────────────────────────────────────────────────

DEFAULT_EXCLUDE_DIRS = {
    "venv",
    ".venv",
    "__pycache__",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    "node_modules",
    ".tox",
    "dist",
    "build",
    "target",
}


def find_files(
    directory: str,
    extensions: Sequence[str],
    exclude_dirs: Optional[set] = None,
) -> List[Path]:
    """
    Find files with given extensions under directory.

    Args:
        directory: Root directory to search.
        extensions: File extensions to include (e.g., [".py", ".pyi"]).
        exclude_dirs: Directory names to skip (defaults to common ones).

    Returns:
        Sorted list of matching Path objects.
    """
    if exclude_dirs is None:
        exclude_dirs = DEFAULT_EXCLUDE_DIRS

    results: List[Path] = []
    root_path = Path(directory)

    if not root_path.is_dir():
        return results

    for dirpath_str, dirnames, filenames in os.walk(root_path):
        # Prune excluded directories in-place
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        for fname in sorted(filenames):
            if any(fname.endswith(ext) for ext in extensions):
                results.append(Path(dirpath_str) / fname)

    return results


# ── Frontmatter Parser ───────────────────────────────────────────────────────

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
_YAML_LIST_RE = re.compile(r"\[([^\]]*)\]")


def parse_skill_frontmatter(skill_md_path: str) -> Dict[str, str]:
    """
    Parse YAML frontmatter from a SKILL.md file.

    Handles simple key: value pairs and inline lists like:
        languages: [python, bash]

    Returns a dict of frontmatter fields.
    """
    try:
        content = Path(skill_md_path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return {}

    match = _FRONTMATTER_RE.match(content)
    if not match:
        return {}

    result: Dict[str, str] = {}
    for line in match.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        # Handle inline YAML lists: [python, bash]
        list_match = _YAML_LIST_RE.match(value)
        if list_match:
            items = [item.strip().strip('"').strip("'") for item in list_match.group(1).split(",")]
            value = ",".join(items)

        result[key] = value

    return result
