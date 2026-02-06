#!/usr/bin/env python3
"""
Dev-AID Validator Runner — auto-discovers and runs skill validators.

Discovers validate.py scripts inside .dev-aid/skills/{core,expert,process}/*/
and runs them as subprocesses. Optionally filters by project context.

Usage:
    run-validators.py [--strict] [--json] [--filter-context] [--target-dir <dir>] [--validators <name,...>]

Exit codes:
    0 = all validators pass
    1 = at least one FAIL found
    2 = runner error
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

# ── ANSI Colors ──────────────────────────────────────────────────────────────

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
BOLD = "\033[1m"
NC = "\033[0m"


def _color(text: str, code: str) -> str:
    if not sys.stdout.isatty():
        return text
    return f"{code}{text}{NC}"


# ── Constants ────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
DEV_AID_DIR = SCRIPT_DIR.parent
SKILL_CATEGORIES = ["core", "expert", "process"]

# Mapping from skill directory names to the languages they validate
# Used for --filter-context to decide which validators to run
SKILL_LANGUAGE_MAP: Dict[str, Set[str]] = {
    "bash-expert": {"bash", "shell", "sh"},
    "python": {"python", "py"},
    "javascript-expert": {"javascript", "js", "node.js", "node"},
    "typescript-expert": {"typescript", "ts"},
    "rust": {"rust", "rs"},
}


# ── Discovery ────────────────────────────────────────────────────────────────


def discover_validators() -> List[Dict[str, str]]:
    """
    Walk .dev-aid/skills/{core,expert,process}/*/validate.py
    Returns list of dicts with 'name', 'path', 'category'.
    """
    validators: List[Dict[str, str]] = []
    skills_dir = DEV_AID_DIR / "skills"

    for category in SKILL_CATEGORIES:
        cat_dir = skills_dir / category
        if not cat_dir.is_dir():
            continue
        for skill_dir in sorted(cat_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            validate_py = skill_dir / "validate.py"
            if validate_py.is_file():
                validators.append(
                    {
                        "name": skill_dir.name,
                        "path": str(validate_py),
                        "category": category,
                    }
                )

    return validators


# ── Context Detection ────────────────────────────────────────────────────────


def detect_project_technologies(target_dir: str) -> Set[str]:
    """
    Detect project technologies by running context-detector.py if available,
    or by simple file extension scanning.
    """
    context_detector = DEV_AID_DIR / "orchestration" / "context-detector.py"

    if context_detector.is_file():
        try:
            result = subprocess.run(
                [sys.executable, str(context_detector), "detect", target_dir],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0 and result.stdout.strip():
                return {kw.lower() for kw in result.stdout.strip().split()}
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    # Fallback: simple extension scanning
    technologies: Set[str] = set()
    ext_map = {
        ".py": "python",
        ".sh": "bash",
        ".js": "javascript",
        ".ts": "typescript",
        ".rs": "rust",
        ".go": "go",
        ".rb": "ruby",
        ".vue": "vue",
    }
    exclude_dirs = {"venv", ".venv", "node_modules", ".git", "__pycache__", "target"}
    target_path = Path(target_dir)

    file_count = 0
    for dirpath, dirnames, filenames in os.walk(target_path):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        for fname in filenames:
            ext = Path(fname).suffix.lower()
            if ext in ext_map:
                technologies.add(ext_map[ext])
            file_count += 1
            if file_count > 2000:
                break
        if file_count > 2000:
            break

    return technologies


def should_run_validator(
    validator: Dict[str, str],
    technologies: Set[str],
) -> bool:
    """Determine if a validator should run based on detected technologies."""
    # Core validators always run
    if validator["category"] == "core":
        return True

    name = validator["name"]
    if name in SKILL_LANGUAGE_MAP:
        required_langs = SKILL_LANGUAGE_MAP[name]
        return bool(required_langs & technologies)

    # If no language mapping, run by default
    return True


# ── Execution ────────────────────────────────────────────────────────────────


def run_single_validator(
    validator: Dict[str, str],
    target_dir: str,
    strict: bool = False,
) -> Optional[Dict]:
    """Run a single validator as a subprocess with --json output."""
    cmd = [sys.executable, validator["path"], "--json", "--target-dir", target_dir]
    if strict:
        cmd.append("--strict")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
        )
        # Parse JSON output
        if result.stdout.strip():
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {
                    "name": validator["name"],
                    "skill_path": validator["path"],
                    "files_scanned": 0,
                    "violations": [],
                    "totals": {"fail": 0, "warn": 0},
                    "status": "ERROR",
                    "error": f"Invalid JSON output: {result.stdout[:200]}",
                }
        else:
            return {
                "name": validator["name"],
                "skill_path": validator["path"],
                "files_scanned": 0,
                "violations": [],
                "totals": {"fail": 0, "warn": 0},
                "status": "ERROR",
                "error": result.stderr.strip()[:200] if result.stderr else "no output",
            }
    except subprocess.TimeoutExpired:
        return {
            "name": validator["name"],
            "skill_path": validator["path"],
            "files_scanned": 0,
            "violations": [],
            "totals": {"fail": 0, "warn": 0},
            "status": "ERROR",
            "error": "validator timed out (300s)",
        }
    except FileNotFoundError as exc:
        return {
            "name": validator["name"],
            "skill_path": validator["path"],
            "files_scanned": 0,
            "violations": [],
            "totals": {"fail": 0, "warn": 0},
            "status": "ERROR",
            "error": str(exc),
        }


# ── Output ───────────────────────────────────────────────────────────────────


def print_text_report(
    results: List[Dict],
    target_dir: str,
    filter_context: bool,
    technologies: Optional[Set[str]] = None,
) -> None:
    """Print human-readable aggregate report."""
    print(f"{_color('Dev-AID Validator Runner', BOLD)}")
    print("=" * 50)
    print(f"Target: {target_dir}")
    if filter_context and technologies:
        print(f"Detected: {', '.join(sorted(technologies))}")
    print(f"Validators: {len(results)}")
    print()

    total_fail = 0
    total_warn = 0
    total_files = 0

    for r in results:
        status = r.get("status", "UNKNOWN")
        name = r.get("name", "unknown")
        files = r.get("files_scanned", 0)
        fail = r.get("totals", {}).get("fail", 0)
        warn = r.get("totals", {}).get("warn", 0)

        total_fail += fail
        total_warn += warn
        total_files += files

        if status == "ERROR":
            tag = _color("ERROR", RED)
            print(f"  {tag} {name}: {r.get('error', 'unknown error')}")
        elif status == "FAIL":
            tag = _color("FAIL", RED)
            print(f"  {tag}  {name} ({files} files, {fail} failures, {warn} warnings)")
        else:
            tag = _color("PASS", GREEN)
            print(f"  {tag}  {name} ({files} files, {warn} warnings)")

        # Print individual violations
        for v in r.get("violations", []):
            sev = v.get("severity", "WARN")
            if sev == "FAIL":
                vtag = _color("FAIL", RED)
            else:
                vtag = _color("WARN", YELLOW)
            vfile = v.get("file", "")
            vline = v.get("line", 0)
            line_ref = f":{vline}" if vline > 0 else ""
            print(f"    {vtag}  [{v.get('check', '')}] {v.get('message', '')} ({vfile}{line_ref})")

    print()
    print("=" * 50)
    print(f"{_color('Totals', BOLD)}")
    print(f"  Files scanned: {total_files}")
    print(f"  {_color('FAIL:', RED)} {total_fail}")
    print(f"  {_color('WARN:', YELLOW)} {total_warn}")
    print()

    if total_fail > 0:
        print(_color(f"RESULT: FAILED ({total_fail} failure(s))", RED))
    else:
        print(_color(f"RESULT: PASSED ({total_warn} warning(s))", GREEN))


def print_json_report(
    results: List[Dict],
    target_dir: str,
) -> None:
    """Print JSON aggregate report."""
    total_fail = sum(r.get("totals", {}).get("fail", 0) for r in results)
    total_warn = sum(r.get("totals", {}).get("warn", 0) for r in results)

    report = {
        "target_dir": target_dir,
        "validators_run": len(results),
        "results": results,
        "totals": {
            "pass": sum(1 for r in results if r.get("status") == "PASS"),
            "fail": sum(1 for r in results if r.get("status") == "FAIL"),
            "error": sum(1 for r in results if r.get("status") == "ERROR"),
            "total_violations_fail": total_fail,
            "total_violations_warn": total_warn,
        },
    }
    print(json.dumps(report, indent=2))


# ── Main ─────────────────────────────────────────────────────────────────────


def main() -> int:
    """Entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Dev-AID Validator Runner — auto-discovers and runs skill validators",
    )
    parser.add_argument("--strict", action="store_true", help="Treat WARN as FAIL")
    parser.add_argument("--json", action="store_true", dest="json_output", help="JSON output")
    parser.add_argument(
        "--filter-context",
        action="store_true",
        help="Only run validators matching detected project technologies",
    )
    parser.add_argument(
        "--target-dir",
        type=str,
        default=".",
        help="Directory to scan (default: current directory)",
    )
    parser.add_argument(
        "--validators",
        type=str,
        default=None,
        help="Comma-separated list of validator names to run",
    )
    args = parser.parse_args()

    target_dir = str(Path(args.target_dir).resolve())

    # Discover validators
    all_validators = discover_validators()
    if not all_validators:
        if args.json_output:
            print(json.dumps({"error": "no validators found", "validators_run": 0}))
        else:
            print(_color("No validators found in .dev-aid/skills/", RED))
        return 2

    # Filter by name if specified
    if args.validators:
        requested = {n.strip() for n in args.validators.split(",")}
        all_validators = [v for v in all_validators if v["name"] in requested]
        if not all_validators:
            if args.json_output:
                print(json.dumps({"error": f"no matching validators: {args.validators}", "validators_run": 0}))
            else:
                print(_color(f"No matching validators: {args.validators}", RED))
            return 2

    # Context filtering
    technologies: Optional[Set[str]] = None
    if args.filter_context:
        technologies = detect_project_technologies(target_dir)
        all_validators = [
            v for v in all_validators
            if should_run_validator(v, technologies)
        ]

    # Run validators
    results: List[Dict] = []
    for validator in all_validators:
        result = run_single_validator(validator, target_dir, strict=args.strict)
        if result is not None:
            results.append(result)

    # Output
    if args.json_output:
        print_json_report(results, target_dir)
    else:
        print_text_report(results, target_dir, args.filter_context, technologies)

    # Exit code
    has_fail = any(
        r.get("totals", {}).get("fail", 0) > 0
        for r in results
    )
    has_error = any(r.get("status") == "ERROR" for r in results)

    if has_fail:
        return 1
    if has_error:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
