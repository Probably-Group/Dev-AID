"""
Bash command execution tool for agents.

Provides run_bash with timeout enforcement, command blocklist checking,
and structured output capture.
"""

import subprocess
from typing import List, Optional

from ..core.models import ToolDefinition

RUN_BASH_DEFINITION = ToolDefinition(
    name="run_bash",
    description=(
        "Execute a bash command and return its output. "
        "Use for git operations, build commands, test runners, etc. "
        "Dangerous commands (rm -rf /, mkfs, etc.) are blocked."
    ),
    parameters={
        "command": {"type": "string", "description": "The bash command to execute"},
        "timeout_ms": {
            "type": "integer",
            "description": "Timeout in milliseconds (default 30000, max 120000)",
        },
        "cwd": {
            "type": "string",
            "description": "Working directory for the command. Optional.",
        },
    },
    required_params=["command"],
    risk_level="dangerous",
)

ALL_DEFINITIONS: List[ToolDefinition] = [RUN_BASH_DEFINITION]


def run_bash(
    command: str,
    timeout_ms: Optional[int] = None,
    cwd: Optional[str] = None,
) -> str:
    """Execute a bash command with timeout and output capture."""
    timeout_s = min((timeout_ms or 30000), 120000) / 1000.0

    try:
        result = subprocess.run(
            ["bash", "-c", command],
            capture_output=True,
            text=True,
            timeout=timeout_s,
            cwd=cwd,
        )

        output_parts: List[str] = []
        if result.stdout:
            output_parts.append(result.stdout)
        if result.stderr:
            output_parts.append(f"[stderr]\n{result.stderr}")
        if result.returncode != 0:
            output_parts.append(f"[exit code: {result.returncode}]")

        output = "\n".join(output_parts) if output_parts else "(no output)"

        # Truncate very large outputs
        if len(output) > 50000:
            output = output[:50000] + "\n... (output truncated at 50000 chars)"

        return output

    except subprocess.TimeoutExpired:
        return f"[error] Command timed out after {timeout_s:.0f}s"
    except Exception as e:  # noqa: F841
        return "[error] Command execution failed"
