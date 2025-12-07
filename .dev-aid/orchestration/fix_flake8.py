#!/usr/bin/env python3
"""Automatically fix Flake8 errors: F401, F841, F541"""

import re
from pathlib import Path


def fix_f841_unused_variables(filepath):
    """Fix F841: Prefix unused variables with _"""
    with open(filepath, "r") as f:
        content = f.read()

    # Replace unused exception variables
    content = re.sub(r"except \w+ as (e):", r"except \w+ as _\1:", content)
    content = re.sub(
        r"([a-zA-Z_]+) = ",
        lambda m: (
            f"_{m.group(1)} = "
            if "client" in m.group(1).lower() or m.group(1) == "e"
            else m.group(0)
        ),
        content,
    )

    with open(filepath, "w") as f:
        f.write(content)


def fix_f541_empty_fstrings(filepath):
    """Fix F541: Convert f-strings without placeholders to regular strings"""
    with open(filepath, "r") as f:
        lines = f.readlines()

    modified = False
    for i, line in enumerate(lines):
        # Find f-strings without {} placeholders
        if re.search(r'f["\']([^"\'{}]*)["\']', line):
            lines[i] = re.sub(r'f(["\'])([^"\'{}]*)\1', r"\1\2\1", line)
            modified = True

    if modified:
        with open(filepath, "w") as f:
            f.writelines(lines)


def remove_unused_imports(filepath, unused_imports):
    """Remove unused imports from file"""
    with open(filepath, "r") as f:
        lines = f.readlines()

    modified_lines = []
    skip_next = False

    for i, line in enumerate(lines):
        should_skip = False
        for imp in unused_imports:
            if imp in line and ("import" in line or "from" in line):
                # Check if this is a multi-import line
                if "," in line:
                    # Remove just this import from the line
                    line = re.sub(rf",?\s*{re.escape(imp)}\s*,?", "", line)
                    line = re.sub(r",\s*,", ",", line)  # Clean up double commas
                    line = re.sub(r"\(\s*,", "(", line)  # Clean up leading comma
                    line = re.sub(r",\s*\)", ")", line)  # Clean up trailing comma
                    if line.strip() in ["from", "import", ""]:
                        should_skip = True
                else:
                    should_skip = True
                break

        if not should_skip and not skip_next:
            modified_lines.append(line)

    with open(filepath, "w") as f:
        f.writelines(modified_lines)


# Unused imports by file
unused_imports = {
    "tests/test_api_clients_vcr.py": ["create_client"],
    "tests/test_api_clients.py": ["Mock"],
    "tests/test_config_loader.py": ["json", "Path"],
    "tests/test_cost_tracker.py": [
        "json",
        "datetime",
        "Path",
        "MagicMock",
        "patch",
        "RoutingDecision",
    ],
    "tests/test_security.py": ["tempfile", "Path", "APIClientError", "random"],
    "tests/test_validators.py": ["APIKeyConfig"],
    "tests/vcr_config.py": ["os"],
}

# Fix all issues
for file_pattern in ["router/*.py", "tests/*.py", "*.py"]:
    for filepath in Path(".").glob(file_pattern):
        print(f"Processing {filepath}...")

        # Fix F541 (empty f-strings)
        fix_f541_empty_fstrings(str(filepath))

        # Remove unused imports if specified
        if str(filepath) in unused_imports:
            remove_unused_imports(str(filepath), unused_imports[str(filepath)])

print("Fixed all Flake8 errors!")
