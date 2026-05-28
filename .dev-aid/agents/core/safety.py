"""
Safety configuration and enforcement for agent tool execution.

Provides SafetyConfig to control which tools agents can use,
which commands are blocked, path restrictions, and dry-run mode.
"""

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)

# Commands that are always blocked regardless of configuration.
# NOTE: Path-based rm/chmod/chown are handled by BLOCKED_COMMAND_PATTERNS
# with negative lookaheads to allow safe paths like /tmp.
DEFAULT_BLOCKED_COMMANDS: List[str] = [
    "mkfs",
    "dd if=",
    ":(){:|:&};:",
    "shutdown",
    "reboot",
    "halt",
    "init 0",
    "init 6",
    "> /dev/sda",
    "wget|sh",
    "curl|sh",
    "wget|bash",
    "curl|bash",
]

# Pattern-based blocking for dangerous command structures
BLOCKED_COMMAND_PATTERNS: List[str] = [
    # rm with recursive+force in any flag style targeting root paths
    r"rm\s+(-[a-zA-Z]*f[a-zA-Z]*\s+)?/(?!tmp)",  # rm -rf / (but allow /tmp)
    r"rm\s+.*--recursive.*--force.*/(?!tmp)",  # rm --recursive --force /
    r"rm\s+.*--force.*--recursive.*/(?!tmp)",  # rm --force --recursive /
    r"rm\s+(-\w+\s+)*-\w*r\w*\s+(-\w+\s+)*-\w*f\w*\s+/(?!tmp)",  # rm -r -f /
    r"rm\s+(-\w+\s+)*-\w*f\w*\s+(-\w+\s+)*-\w*r\w*\s+/(?!tmp)",  # rm -f -r /
    r">\s*/dev/[a-z]+",  # redirect to block devices
    r"mkfs\.",  # format filesystems
    r"dd\s+if=.*of=/dev",  # dd to block devices
    r":()\{.*\|.*&\}\s*;",  # fork bomb
    r"chmod\s+(-\w+\s+)*777\s+/",  # chmod 777 on root paths
    r"chown\s+(-\w+\s+)*-R\s+.*\s+/(?!tmp)",  # chown -R on root paths
    # Interpreter-based bypass attempts (CWE-78)
    r"python[23]?\s+(-c\s+|.*-c\s+)",  # python -c "code"
    r"perl\s+-e\s+",  # perl -e "code"
    r"ruby\s+-e\s+",  # ruby -e "code"
    r"node\s+-e\s+",  # node -e "code"
    r"php\s+-r\s+",  # php -r "code"
    r"base64\s+(-d|--decode)\s*\|",  # base64 -d | sh
    r"\beval\s+",  # eval command
    r"\bexec\s+\d*[<>]",  # exec with redirections
    r"\bsource\s+/dev/",  # source /dev/tcp etc.
    r"/dev/tcp/",  # bash /dev/tcp connections
    r"xargs\s+.*sh\b",  # xargs piping to shell
    r"\bnc\s+(-e|-c)\s+",  # netcat reverse shell
    r"\bchmod\s+[+]?[ugo]*s",  # setuid/setgid bits
]

_COMPILED_BLOCKED_PATTERNS = [re.compile(p) for p in BLOCKED_COMMAND_PATTERNS]

# Tools that mutate files. Used by the Dev-AID scope guard (issue #147) to
# block writes to `.dev-aid/` for host-project tasks. Read tools (read_file,
# list_directory, glob_files) are intentionally NOT in this set — agents
# routinely need to read scaffold files (skill defs, agent prompts, etc.)
# even when the task itself is host-project work.
WRITE_TOOL_NAMES: Set[str] = {"write_file", "edit_file"}

# Path segment that identifies the Dev-AID scaffold inside a host project.
# Comparing on a resolved Path with this segment lets the guard work both
# when the scaffold lives at <project>/.dev-aid and when the project root is
# a symlink — see is_dev_aid_path() for the resolution logic.
_DEV_AID_DIR_NAME = ".dev-aid"


@dataclass
class SafetyConfig:
    """Safety configuration for agent execution."""

    dry_run: bool = False
    allowed_tools: Optional[Set[str]] = None  # None = all tools allowed
    blocked_commands: List[str] = field(
        default_factory=lambda: list(DEFAULT_BLOCKED_COMMANDS)
    )
    max_bash_timeout_ms: int = 30000
    allowed_paths: Optional[List[Path]] = None  # None = no path restrictions
    max_file_size_bytes: int = 10 * 1024 * 1024  # 10 MB
    # Issue #147: by default, agents invoked for host-project tasks must NOT
    # be able to silently mutate .dev-aid/ scaffold files. The user has to
    # opt in explicitly (e.g. via `--scope dev-aid` on the CLI) when their
    # actual intent is to contribute upstream to Dev-AID itself. Read access
    # is unaffected — only write_file / edit_file are gated.
    allow_dev_aid_writes: bool = False

    def is_tool_allowed(self, tool_name: str) -> bool:
        """Check if a tool is allowed by the safety config."""
        if self.allowed_tools is None:
            return True
        return tool_name in self.allowed_tools

    def is_command_safe(self, command: str) -> bool:
        """Check if a bash command is safe to execute."""
        cmd_lower = command.lower().strip()

        # Check exact matches (also compare with whitespace stripped)
        cmd_nospace = cmd_lower.replace(" ", "")
        for blocked in self.blocked_commands:
            blocked_lower = blocked.lower()
            if (
                blocked_lower in cmd_lower
                or blocked_lower.replace(" ", "") in cmd_nospace
            ):
                logger.warning("Blocked command (exact match): %s", command[:100])
                return False

        # Check pattern matches
        for pattern in _COMPILED_BLOCKED_PATTERNS:
            if pattern.search(cmd_lower):
                logger.warning("Blocked command (pattern match): %s", command[:100])
                return False

        return True

    def is_path_allowed(self, path: Path) -> bool:
        """Check if a file path is within allowed boundaries."""
        if self.allowed_paths is None:
            return True

        resolved = path.resolve()
        for allowed in self.allowed_paths:
            allowed_resolved = allowed.resolve()
            try:
                resolved.relative_to(allowed_resolved)
                return True
            except ValueError:
                continue

        logger.warning("Path outside allowed boundaries: %s", path)
        return False

    @staticmethod
    def is_dev_aid_path(path: Path) -> bool:
        """
        Return True if ``path`` resolves to something inside a ``.dev-aid``
        directory.

        Used by the issue #147 scope guard. We resolve the path so that
        symlinks (e.g. a host project where ``CLAUDE.md`` is a symlink into
        ``.dev-aid/providers/...``) get matched correctly. The check looks
        for ``.dev-aid`` as a path component anywhere in the resolved path,
        not just at the root, so it works regardless of where the host
        project lives on disk.
        """
        try:
            resolved = path.resolve()
        except (OSError, RuntimeError):
            # Path doesn't exist yet (e.g. about-to-be-created file) or
            # symlink loop. Fall back to lexical check on the raw path.
            resolved = path
        return _DEV_AID_DIR_NAME in resolved.parts

    def check_tool_execution(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        risk_level: str = "safe",
    ) -> "SafetyCheckResult":
        """Perform comprehensive safety check before tool execution."""
        if not self.is_tool_allowed(tool_name):
            return SafetyCheckResult(
                allowed=False,
                reason=f"Tool '{tool_name}' is not in the allowed tools list",
            )

        if self.dry_run and risk_level != "safe":
            return SafetyCheckResult(
                allowed=False,
                reason=f"Dry-run mode: blocking {risk_level} tool '{tool_name}'",
                dry_run_blocked=True,
            )

        # Check bash commands
        if tool_name == "run_bash":
            command = arguments.get("command", "")
            if not self.is_command_safe(command):
                return SafetyCheckResult(
                    allowed=False,
                    reason=f"Command blocked by safety rules: {command[:100]}",
                )
            cwd = arguments.get("cwd")
            if cwd and not self.is_path_allowed(Path(cwd)):
                return SafetyCheckResult(
                    allowed=False,
                    reason=f"Working directory '{cwd}' is outside allowed boundaries",
                )

        # Check file paths
        for key in ("path", "file_path"):
            if key in arguments:
                path = Path(arguments[key])
                if not self.is_path_allowed(path):
                    return SafetyCheckResult(
                        allowed=False,
                        reason=f"Path '{path}' is outside allowed boundaries",
                    )

                # Issue #147: refuse writes into .dev-aid/ unless the user
                # opted in. Read tools are NOT in WRITE_TOOL_NAMES so they
                # pass through. The check happens AFTER is_path_allowed so
                # that the message order matches what the user would expect
                # ("outside allowed boundaries" beats "scaffold scope" if
                # both apply).
                if (
                    tool_name in WRITE_TOOL_NAMES
                    and not self.allow_dev_aid_writes
                    and self.is_dev_aid_path(path)
                ):
                    return SafetyCheckResult(
                        allowed=False,
                        reason=(
                            f"Refusing to {tool_name} '{path}': path is inside the "
                            ".dev-aid/ scaffold and the agent was not invoked with "
                            "scope=dev-aid. If you intended to contribute upstream "
                            "to Dev-AID, re-run with `--scope dev-aid`. Otherwise "
                            "edit a host-project file instead. (See "
                            ".dev-aid/HOST_PROJECT.md for the scope rules.)"
                        ),
                    )

        return SafetyCheckResult(allowed=True)


@dataclass
class SafetyCheckResult:
    """Result of a safety check."""

    allowed: bool
    reason: str = ""
    dry_run_blocked: bool = False
