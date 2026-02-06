"""
GitHub CLI (gh) wrapper tools for agents.

Provides gh_issue_view, gh_pr_view, and gh_pr_create
using the gh CLI tool.
"""

import subprocess
from typing import List, Optional

from ..core.models import ToolDefinition

GH_ISSUE_VIEW_DEFINITION = ToolDefinition(
    name="gh_issue_view",
    description="View a GitHub issue's details including title, body, labels, and comments.",
    parameters={
        "number": {"type": "integer", "description": "Issue number."},
        "repo": {
            "type": "string",
            "description": "Repository in owner/repo format. Optional (uses current repo).",
        },
    },
    required_params=["number"],
    risk_level="safe",
)

GH_PR_VIEW_DEFINITION = ToolDefinition(
    name="gh_pr_view",
    description=(
        "View a pull request's details including title, body, " "diff stats, and review status."
    ),
    parameters={
        "number": {"type": "integer", "description": "PR number."},
        "repo": {
            "type": "string",
            "description": "Repository in owner/repo format. Optional (uses current repo).",
        },
    },
    required_params=["number"],
    risk_level="safe",
)

GH_PR_CREATE_DEFINITION = ToolDefinition(
    name="gh_pr_create",
    description="Create a new pull request from the current branch.",
    parameters={
        "title": {"type": "string", "description": "PR title."},
        "body": {"type": "string", "description": "PR description body (markdown)."},
        "base": {
            "type": "string",
            "description": "Base branch to merge into (default: main).",
        },
        "draft": {
            "type": "boolean",
            "description": "Create as draft PR. Default false.",
        },
    },
    required_params=["title", "body"],
    risk_level="moderate",
)

ALL_DEFINITIONS: List[ToolDefinition] = [
    GH_ISSUE_VIEW_DEFINITION,
    GH_PR_VIEW_DEFINITION,
    GH_PR_CREATE_DEFINITION,
]


def _run_gh(args: List[str]) -> str:
    """Run a gh CLI command and return output."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout
        if result.stderr and result.returncode != 0:
            output += f"\n[stderr] {result.stderr}" if output else result.stderr
        return output.strip() or "(no output)"
    except FileNotFoundError:
        return "[error] gh CLI not found. Install from https://cli.github.com/"
    except subprocess.TimeoutExpired:
        return "[error] gh command timed out after 30s"
    except Exception as e:
        return f"[error] gh command failed: {e}"


def gh_issue_view(number: int, repo: Optional[str] = None) -> str:
    """View a GitHub issue."""
    args = ["issue", "view", str(number)]
    if repo:
        args.extend(["--repo", repo])
    return _run_gh(args)


def gh_pr_view(number: int, repo: Optional[str] = None) -> str:
    """View a pull request."""
    args = ["pr", "view", str(number)]
    if repo:
        args.extend(["--repo", repo])
    return _run_gh(args)


def gh_pr_create(
    title: str,
    body: str,
    base: str = "main",
    draft: bool = False,
) -> str:
    """Create a pull request."""
    args = ["pr", "create", "--title", title, "--body", body, "--base", base]
    if draft:
        args.append("--draft")
    return _run_gh(args)
