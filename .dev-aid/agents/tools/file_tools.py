"""
File operation tools for agents.

Provides read_file, write_file, list_directory, and glob_files
with safety-aware path handling.
"""

from pathlib import Path
from typing import List, Optional

from ..core.models import ToolDefinition

# ── Tool Definitions ──────────────────────────────────────────────────

READ_FILE_DEFINITION = ToolDefinition(
    name="read_file",
    description="Read the contents of a file. Returns the file content as text.",
    parameters={
        "path": {"type": "string", "description": "Absolute path to the file to read"},
        "offset": {
            "type": "integer",
            "description": "Line number to start reading from (1-based). Optional.",
        },
        "limit": {
            "type": "integer",
            "description": "Maximum number of lines to read. Optional.",
        },
    },
    required_params=["path"],
    risk_level="safe",
)

WRITE_FILE_DEFINITION = ToolDefinition(
    name="write_file",
    description=(
        "Write content to a file. Creates the file if it doesn't exist, " "overwrites if it does."
    ),
    parameters={
        "path": {"type": "string", "description": "Absolute path to the file to write"},
        "content": {"type": "string", "description": "Content to write to the file"},
    },
    required_params=["path", "content"],
    risk_level="moderate",
)

LIST_DIRECTORY_DEFINITION = ToolDefinition(
    name="list_directory",
    description="List the contents of a directory, showing files and subdirectories.",
    parameters={
        "path": {"type": "string", "description": "Absolute path to the directory to list"},
    },
    required_params=["path"],
    risk_level="safe",
)

GLOB_FILES_DEFINITION = ToolDefinition(
    name="glob_files",
    description="Find files matching a glob pattern within a directory.",
    parameters={
        "pattern": {
            "type": "string",
            "description": "Glob pattern to match (e.g. '**/*.py', 'src/**/*.ts')",
        },
        "path": {
            "type": "string",
            "description": "Base directory to search in. Defaults to current directory.",
        },
    },
    required_params=["pattern"],
    risk_level="safe",
)

ALL_DEFINITIONS: List[ToolDefinition] = [
    READ_FILE_DEFINITION,
    WRITE_FILE_DEFINITION,
    LIST_DIRECTORY_DEFINITION,
    GLOB_FILES_DEFINITION,
]


# ── Tool Implementations ─────────────────────────────────────────────


def read_file(
    path: str,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
) -> str:
    """Read a file's contents with optional offset and limit."""
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    content = file_path.read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines(keepends=True)

    start = (offset - 1) if offset and offset > 0 else 0
    end = (start + limit) if limit else None

    selected = lines[start:end]
    return "".join(selected)


def write_file(path: str, content: str) -> str:
    """Write content to a file, creating parent directories as needed."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return f"Successfully wrote {len(content)} bytes to {path}"


def list_directory(path: str) -> str:
    """List directory contents with type indicators."""
    dir_path = Path(path)
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {path}")

    entries: List[str] = []
    for entry in sorted(dir_path.iterdir()):
        if entry.name.startswith("."):
            continue
        prefix = "d " if entry.is_dir() else "f "
        entries.append(f"{prefix}{entry.name}")

    if not entries:
        return "(empty directory)"
    return "\n".join(entries)


def glob_files(pattern: str, path: Optional[str] = None) -> str:
    """Find files matching a glob pattern."""
    base = Path(path) if path else Path.cwd()
    if not base.is_dir():
        raise NotADirectoryError(f"Not a directory: {base}")

    matches: List[str] = []
    for match in sorted(base.glob(pattern)):
        if match.is_file():
            matches.append(str(match))

    if not matches:
        return "No files found matching pattern."
    return "\n".join(matches[:500])  # Cap at 500 results
