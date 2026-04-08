"""
Search tools for agents.

Provides grep_search and find_files for codebase exploration.
"""

import fnmatch
import os
import subprocess
from typing import List, Optional

from ..core.models import ToolDefinition

GREP_SEARCH_DEFINITION = ToolDefinition(
    name="grep_search",
    description=(
        "Search file contents for a regex pattern. "
        "Returns matching lines with file paths and line numbers."
    ),
    parameters={
        "pattern": {"type": "string", "description": "Regex pattern to search for."},
        "path": {
            "type": "string",
            "description": "Directory or file to search in. Defaults to current directory.",
        },
        "glob": {
            "type": "string",
            "description": "File glob filter (e.g. '*.py', '*.ts'). Optional.",
        },
        "case_insensitive": {
            "type": "boolean",
            "description": "Case insensitive search. Default false.",
        },
    },
    required_params=["pattern"],
    risk_level="safe",
)

FIND_FILES_DEFINITION = ToolDefinition(
    name="find_files",
    description="Find files by name pattern in a directory tree.",
    parameters={
        "pattern": {
            "type": "string",
            "description": "Filename pattern to match (e.g. '*.py', 'test_*.js').",
        },
        "path": {
            "type": "string",
            "description": "Base directory to search. Defaults to current directory.",
        },
    },
    required_params=["pattern"],
    risk_level="safe",
)

ALL_DEFINITIONS: List[ToolDefinition] = [
    GREP_SEARCH_DEFINITION,
    FIND_FILES_DEFINITION,
]


def grep_search(
    pattern: str,
    path: Optional[str] = None,
    glob: Optional[str] = None,
    case_insensitive: bool = False,
) -> str:
    """Search file contents using ripgrep (rg) or grep."""
    search_path = path or "."

    # Try ripgrep first (faster), fall back to grep
    for cmd_name in ["rg", "grep"]:
        args: List[str] = [cmd_name]

        if cmd_name == "rg":
            args.extend(["-n", "--no-heading"])
            if case_insensitive:
                args.append("-i")
            if glob:
                args.extend(["--glob", glob])
            args.extend([pattern, search_path])
        else:
            args.extend(["-rn"])
            if case_insensitive:
                args.append("-i")
            args.extend([pattern, search_path])
            if glob:
                args.extend(["--include", glob])

        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = result.stdout.strip()
            if not output:
                return "No matches found."

            # Truncate large results
            lines = output.split("\n")
            if len(lines) > 200:
                output = (
                    "\n".join(lines[:200]) + f"\n... ({len(lines) - 200} more matches)"
                )
            return output
        except FileNotFoundError:
            continue  # Try next search tool
        except subprocess.TimeoutExpired:
            return f"[error] Search timed out after 30s for pattern: {pattern[:50]}"

    return "[error] Neither rg nor grep found on this system."


def find_files(pattern: str, path: Optional[str] = None) -> str:
    """Find files matching a name pattern."""
    base = path or "."
    matches: List[str] = []

    for root, dirs, files in os.walk(base):
        # Skip hidden directories and common large directories
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".")
            and d not in ("node_modules", "__pycache__", "venv", ".git")
        ]
        for filename in files:
            if fnmatch.fnmatch(filename, pattern):
                matches.append(os.path.join(root, filename))

    if not matches:
        return "No files found matching pattern."

    matches.sort()
    if len(matches) > 500:
        return "\n".join(matches[:500]) + f"\n... ({len(matches) - 500} more files)"
    return "\n".join(matches)
