"""
Git operation tools for agents.

Provides git_status, git_diff, git_log, git_add, and git_commit
using subprocess calls to git CLI.
"""

import subprocess
from typing import List, Optional

from ..core.models import ToolDefinition

GIT_STATUS_DEFINITION = ToolDefinition(
    name="git_status",
    description="Show the working tree status (modified, staged, untracked files).",
    parameters={
        "cwd": {"type": "string", "description": "Repository path. Optional."},
    },
    required_params=[],
    risk_level="safe",
)

GIT_DIFF_DEFINITION = ToolDefinition(
    name="git_diff",
    description="Show changes between commits, working tree, and staging area.",
    parameters={
        "staged": {
            "type": "boolean",
            "description": "Show staged changes only (--cached). Default false.",
        },
        "target": {
            "type": "string",
            "description": "Diff target (branch, commit, file path). Optional.",
        },
        "cwd": {"type": "string", "description": "Repository path. Optional."},
    },
    required_params=[],
    risk_level="safe",
)

GIT_LOG_DEFINITION = ToolDefinition(
    name="git_log",
    description="Show recent commit history.",
    parameters={
        "count": {
            "type": "integer",
            "description": "Number of commits to show (default 10).",
        },
        "oneline": {
            "type": "boolean",
            "description": "Use one-line format. Default true.",
        },
        "cwd": {"type": "string", "description": "Repository path. Optional."},
    },
    required_params=[],
    risk_level="safe",
)

GIT_ADD_DEFINITION = ToolDefinition(
    name="git_add",
    description=(
        "Stage files for commit. Specify individual files "
        "rather than using '.' for safety."
    ),
    parameters={
        "files": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of file paths to stage.",
        },
        "cwd": {"type": "string", "description": "Repository path. Optional."},
    },
    required_params=["files"],
    risk_level="moderate",
)

GIT_COMMIT_DEFINITION = ToolDefinition(
    name="git_commit",
    description="Create a git commit with the staged changes.",
    parameters={
        "message": {"type": "string", "description": "Commit message."},
        "cwd": {"type": "string", "description": "Repository path. Optional."},
    },
    required_params=["message"],
    risk_level="moderate",
)

ALL_DEFINITIONS: List[ToolDefinition] = [
    GIT_STATUS_DEFINITION,
    GIT_DIFF_DEFINITION,
    GIT_LOG_DEFINITION,
    GIT_ADD_DEFINITION,
    GIT_COMMIT_DEFINITION,
]


def _run_git(args: List[str], cwd: Optional[str] = None) -> str:
    """Run a git command and return output."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=cwd,
        )
        output = result.stdout
        if result.stderr:
            output += f"\n{result.stderr}" if output else result.stderr
        if result.returncode != 0 and not output.strip():
            output = f"git command failed with exit code {result.returncode}"
        return output.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return "[error] Git command timed out after 30s"
    except Exception as e:
        return f"[error] Git command failed: {e}"


def git_status(cwd: Optional[str] = None) -> str:
    """Show working tree status."""
    return _run_git(["status", "--short"], cwd=cwd)


def git_diff(
    staged: bool = False,
    target: Optional[str] = None,
    cwd: Optional[str] = None,
) -> str:
    """Show diffs."""
    args = ["diff"]
    if staged:
        args.append("--cached")
    if target:
        args.extend(["--", target])
    output = _run_git(args, cwd=cwd)
    # Truncate large diffs
    if len(output) > 50000:
        output = output[:50000] + "\n... (diff truncated at 50000 chars)"
    return output


def git_log(
    count: int = 10,
    oneline: bool = True,
    cwd: Optional[str] = None,
) -> str:
    """Show recent commits."""
    args = ["log", f"-{min(count, 100)}"]
    if oneline:
        args.append("--oneline")
    return _run_git(args, cwd=cwd)


def git_add(files: List[str], cwd: Optional[str] = None) -> str:
    """Stage files for commit."""
    if not files:
        return "No files specified to stage."
    return _run_git(["add", "--"] + files, cwd=cwd)


def git_commit(message: str, cwd: Optional[str] = None) -> str:
    """Create a commit."""
    if not message.strip():
        return "Empty commit message not allowed."
    return _run_git(["commit", "-m", message], cwd=cwd)
