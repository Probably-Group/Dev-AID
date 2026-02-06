#!/usr/bin/env python3
"""
Bash Expert Skill Compliance Validator.

Validates bash scripts against bash-expert skill standards:
  - Shebang, strict mode, IFS, cleanup trap
  - Syntax check (bash -n)
  - Dangerous patterns (eval, backticks)
  - Test brackets, variable braces
  - Local variables in functions
  - Readonly constants, chmod permissions
  - mktemp usage, curl pipe, unquoted subshell

Usage:
    validate.py [--strict] [--json] [--target-dir <dir>] [files...]
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import List

# Import shared validator library
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "lib"))
from validator_common import (  # noqa: E402
    Violation,
    ValidatorResult,
    create_argument_parser,
    run_validator_main,
    find_files,
)

VALIDATOR_NAME = "bash-expert"
SKILL_PATH = str(Path(__file__).resolve().parent)


# ── Check Functions ──────────────────────────────────────────────────────────


def check_shebang(lines: List[str], filepath: str) -> List[Violation]:
    """Verify #!/usr/bin/env bash shebang."""
    violations: List[Violation] = []
    if not lines:
        violations.append(
            Violation(filepath, 1, "shebang", "empty file", "FAIL")
        )
        return violations

    first_line = lines[0].rstrip()
    if first_line == "#!/usr/bin/env bash":
        return violations
    elif first_line == "#!/bin/bash":
        violations.append(
            Violation(
                filepath, 1, "shebang",
                "#!/bin/bash (must be #!/usr/bin/env bash)", "FAIL",
            )
        )
    else:
        violations.append(
            Violation(
                filepath, 1, "shebang",
                f"missing or incorrect shebang (found: {first_line})", "FAIL",
            )
        )
    return violations


def check_strict_mode(lines: List[str], filepath: str) -> List[Violation]:
    """Check for set -euo pipefail."""
    for line in lines:
        if re.match(r"^set -euo pipefail", line):
            return []
    return [Violation(filepath, 0, "strict_mode", "missing 'set -euo pipefail'", "FAIL")]


def check_ifs(lines: List[str], filepath: str) -> List[Violation]:
    """Check for IFS=$'\\n\\t'."""
    for line in lines:
        if "IFS=$'\\n\\t'" in line:
            return []
    return [Violation(filepath, 0, "ifs", "missing IFS=$'\\n\\t' after strict mode", "FAIL")]


def check_cleanup_trap(lines: List[str], filepath: str) -> List[Violation]:
    """Check for trap ... EXIT."""
    for lineno, line in enumerate(lines, 1):
        if re.match(r"^trap\s+\S+\s+.*EXIT", line):
            return []
    return [Violation(filepath, 0, "cleanup_trap", "no 'trap ... EXIT' found", "FAIL")]


def check_syntax(script_path: str, filepath: str) -> List[Violation]:
    """Run bash -n syntax check."""
    try:
        result = subprocess.run(
            ["bash", "-n", script_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            msg = result.stderr.strip().split("\n")[0] if result.stderr else "syntax error"
            return [Violation(filepath, 0, "syntax", f"bash -n failed: {msg}", "FAIL")]
    except subprocess.TimeoutExpired:
        return [Violation(filepath, 0, "syntax", "bash -n timed out", "FAIL")]
    except FileNotFoundError:
        return [Violation(filepath, 0, "syntax", "bash not found", "FAIL")]
    return []


def check_dangerous_patterns(lines: List[str], filepath: str) -> List[Violation]:
    """Detect eval usage and backticks."""
    violations: List[Violation] = []
    for lineno, line in enumerate(lines, 1):
        stripped = line.lstrip()
        # Skip comments
        if stripped.startswith("#"):
            continue
        # Skip lines that are themselves grep/check patterns
        if any(kw in line for kw in ("grep", "log_", "echo", "check_", "# ")):
            continue

        # Check for eval
        if re.search(r"\beval\b", stripped):
            violations.append(
                Violation(filepath, lineno, "dangerous_patterns", "uses 'eval' (avoid)", "FAIL")
            )

        # Check for backticks
        if "`" in stripped:
            violations.append(
                Violation(
                    filepath, lineno, "dangerous_patterns",
                    "uses backticks (use $() instead)", "FAIL",
                )
            )
    return violations


def check_test_brackets(lines: List[str], filepath: str) -> List[Violation]:
    """Detect single [ ] instead of [[ ]]."""
    violations: List[Violation] = []
    for lineno, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        if any(kw in line for kw in ("grep", "echo", "log_")):
            continue
        # Match single [ followed by space, but not [[
        if re.search(r"(?<!\[)\[\s", line) and "[[" not in line:
            violations.append(
                Violation(
                    filepath, lineno, "test_brackets",
                    "uses single [ ] instead of [[ ]]", "FAIL",
                )
            )
    return violations


def check_variable_braces(lines: List[str], filepath: str) -> List[Violation]:
    """Detect $VAR without ${VAR} braces."""
    count = 0
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        # Find "$VAR" without braces (should be "${VAR}")
        if re.search(r'^\s*[^#]*"\$[A-Za-z_][A-Za-z_0-9]*[^}]', line):
            count += 1
    if count > 0:
        return [
            Violation(
                filepath, 0, "variable_braces",
                f"~{count} variable(s) without ${{}} braces", "WARN",
            )
        ]
    return []


def check_local_in_functions(lines: List[str], filepath: str) -> List[Violation]:
    """State machine: track function bodies and check for 'local' declarations."""
    # First pass: collect top-level global variable names
    global_vars = set()
    for line in lines:
        # Top-level declare/readonly
        m = re.match(r"^(declare|readonly)\s+(?:[-a-zA-Z]*\s+)?([a-zA-Z_]\w*)", line)
        if m:
            global_vars.add(m.group(2))
        # Top-level VAR= (no leading whitespace)
        m = re.match(r"^([a-zA-Z_]\w*)=", line)
        if m:
            global_vars.add(m.group(1))

    # Second pass: check functions
    in_function = False
    local_vars: set = set()
    found_issues = False

    for line in lines:
        # Detect function start
        if re.match(r"^\s*(function\s+)?([a-zA-Z_]\w*)\s*\(\)\s*\{", line):
            in_function = True
            local_vars = set()
            continue

        # Detect function end
        if in_function and re.match(r"^\s*\}\s*$", line):
            in_function = False
            local_vars = set()
            continue

        if not in_function:
            continue

        stripped = line.lstrip()
        # Skip comments, empty lines
        if stripped.startswith("#") or not stripped:
            continue

        # Track local/declare vars
        m = re.match(r"^\s*(local|declare)\s+(?:[-a-zA-Z]*\s+)?([a-zA-Z_]\w*)", line)
        if m:
            local_vars.add(m.group(2))
            continue

        # Skip lines with export/readonly/typeset
        if re.match(r"^\s*(readonly|export|typeset)\s", line):
            continue

        # Skip control flow, commands
        if re.match(
            r"^\s*(if|then|else|elif|fi|for|while|do|done|case|esac|"
            r"return|echo|continue|break|total_|log_)",
            stripped,
        ):
            continue

        # Match: VAR= or VAR+= (assignment inside function)
        m = re.match(r"^\s+([a-zA-Z_]\w*)\+?=", line)
        if m:
            var_name = m.group(1)
            if var_name not in local_vars and var_name not in global_vars:
                found_issues = True

    if found_issues:
        return [
            Violation(
                filepath, 0, "local_in_functions",
                "function variable(s) assigned without 'local'", "FAIL",
            )
        ]
    return []


def check_readonly_constants(lines: List[str], filepath: str) -> List[Violation]:
    """Check top-level UPPERCASE= assignments without readonly."""
    builtins = {"IFS", "PATH", "PS1", "PS2", "PS4", "HOME", "SHELL", "TERM", "LANG"}
    count = 0
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#") or not stripped:
            continue
        # Match top-level uppercase assignments
        m = re.match(r"^([A-Z_][A-Z_0-9]*)=", line)
        if m:
            var = m.group(1)
            # Skip if starts with readonly/declare/export
            if re.match(r"^(readonly|declare|export)\s", line):
                continue
            # Skip builtins and LC_ vars
            if var in builtins or var.startswith("LC_"):
                continue
            count += 1

    if count > 0:
        return [
            Violation(
                filepath, 0, "readonly_constants",
                f"{count} top-level constant(s) without 'readonly'", "WARN",
            )
        ]
    return []


def check_chmod_permissions(lines: List[str], filepath: str) -> List[Violation]:
    """Detect insecure chmod (777/666/o+w)."""
    for lineno, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        if re.search(r"chmod\s+(777|666)|chmod\s+o\+w", line):
            return [
                Violation(
                    filepath, lineno, "chmod_permissions",
                    "insecure chmod (777/666/o+w) detected", "FAIL",
                )
            ]
    return []


def check_mktemp_usage(lines: List[str], filepath: str) -> List[Violation]:
    """Detect hardcoded /tmp/ paths without mktemp."""
    for lineno, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        if any(kw in line for kw in ("mktemp", "grep", "echo", "log_")):
            continue
        if "/tmp/" in line:
            return [
                Violation(
                    filepath, lineno, "mktemp_usage",
                    "hardcoded /tmp/ path (use mktemp instead)", "WARN",
                )
            ]
    return []


def check_curl_pipe(lines: List[str], filepath: str) -> List[Violation]:
    """Detect curl | bash patterns."""
    for lineno, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        if any(kw in line for kw in ("grep", "log_", "echo", "check_")):
            continue
        if re.search(r"curl\s.*\|\s*(ba)?sh", line):
            return [
                Violation(
                    filepath, lineno, "curl_pipe",
                    "curl | bash pattern detected (never pipe to shell)", "FAIL",
                )
            ]
    return []


def check_unquoted_subshell(lines: List[str], filepath: str) -> List[Violation]:
    """Detect unquoted command substitution: VAR=$(...) without quotes."""
    count = 0
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        if re.search(r'[a-zA-Z_]+=[^"]*\$\(', line):
            count += 1

    if count > 0:
        return [
            Violation(
                filepath, 0, "unquoted_subshell",
                f"~{count} unquoted command substitution(s)", "WARN",
            )
        ]
    return []


# ── Main Validation ──────────────────────────────────────────────────────────


def validate_script(
    script_path: Path, base_dir: Path
) -> List[Violation]:
    """Run all checks on a single bash script."""
    violations: List[Violation] = []
    try:
        rel_path = str(script_path.relative_to(base_dir))
    except ValueError:
        rel_path = str(script_path)

    try:
        content = script_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [Violation(rel_path, 0, "read", f"could not read file: {exc}", "FAIL")]

    lines = content.splitlines()

    violations.extend(check_shebang(lines, rel_path))
    violations.extend(check_strict_mode(lines, rel_path))
    violations.extend(check_ifs(lines, rel_path))
    violations.extend(check_cleanup_trap(lines, rel_path))
    violations.extend(check_syntax(str(script_path), rel_path))
    violations.extend(check_dangerous_patterns(lines, rel_path))
    violations.extend(check_test_brackets(lines, rel_path))
    violations.extend(check_variable_braces(lines, rel_path))
    violations.extend(check_local_in_functions(lines, rel_path))
    violations.extend(check_readonly_constants(lines, rel_path))
    violations.extend(check_chmod_permissions(lines, rel_path))
    violations.extend(check_mktemp_usage(lines, rel_path))
    violations.extend(check_curl_pipe(lines, rel_path))
    violations.extend(check_unquoted_subshell(lines, rel_path))

    return violations


def main() -> int:
    """Entry point."""
    parser = create_argument_parser(
        "bash-expert-validator",
        "Bash Expert Skill Compliance Validator",
    )
    args = parser.parse_args()

    target_dir = Path(args.target_dir).resolve()

    # Determine files to scan
    if args.files:
        scripts = [Path(f).resolve() for f in args.files]
    else:
        scripts = find_files(str(target_dir), [".sh"])

    all_violations: List[Violation] = []
    for script in scripts:
        all_violations.extend(validate_script(script, target_dir))

    result = ValidatorResult(
        name="Bash Expert Compliance",
        skill_path=SKILL_PATH,
        files_scanned=len(scripts),
        violations=all_violations,
    )

    return run_validator_main(result, args)


if __name__ == "__main__":
    sys.exit(main())
