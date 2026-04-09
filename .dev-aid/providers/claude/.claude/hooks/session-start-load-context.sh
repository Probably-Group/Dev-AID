#!/usr/bin/env bash
# Session Start Hook - Load Memory Bank Foundation
# Auto-loads CLAUDE-activeContext.md (~300 tokens)
# Runs once per session

set -euo pipefail

# Cleanup handler
cleanup() {
    local exit_code=$?
    # No resources to clean up, but trap is good practice
    exit "$exit_code"
}

trap cleanup EXIT INT TERM

# Validate CLAUDE_PROJECT_DIR environment variable (CVE-2014-6271: Shellshock)
if [[ -z "${CLAUDE_PROJECT_DIR:-}" ]]; then
    echo "Error: CLAUDE_PROJECT_DIR environment variable not set" >&2
    exit 1
fi

# Check for shellshock patterns
if [[ "$CLAUDE_PROJECT_DIR" =~ ^\(\)[[:space:]]*\{ ]]; then
    echo "Error: Potential shellshock exploit detected in CLAUDE_PROJECT_DIR" >&2
    exit 1
fi

# Validate CLAUDE_PROJECT_DIR is a safe path
readonly RESOLVED_PROJECT_DIR="$(realpath -m "$CLAUDE_PROJECT_DIR" 2>/dev/null)" || {
    echo "Error: Failed to resolve CLAUDE_PROJECT_DIR: $CLAUDE_PROJECT_DIR" >&2
    exit 1
}

# Ensure it's not a system directory
readonly UNSAFE_PATHS=("/" "/etc" "/usr" "/bin" "/sbin" "/boot" "/sys" "/proc" "/dev")
for unsafe_path in "${UNSAFE_PATHS[@]}"; do
    if [[ "$RESOLVED_PROJECT_DIR" == "$unsafe_path" ]] || [[ "$RESOLVED_PROJECT_DIR" == "$unsafe_path"/* ]]; then
        echo "Error: CLAUDE_PROJECT_DIR points to a system directory: $RESOLVED_PROJECT_DIR" >&2
        exit 1
    fi
done

readonly MEMORY_BANK_DIR="$CLAUDE_PROJECT_DIR/memory-bank"
readonly ACTIVE_CONTEXT="$MEMORY_BANK_DIR/CLAUDE-activeContext.md"

# ----------------------------------------------------------------------------
# Host-project scope announcement
#
# When Dev-AID is installed into a host project (e.g. a JARVIS-style product
# repo), the top-level CLAUDE.md is a symlink to
# .dev-aid/providers/claude/CLAUDE.md (created by claude-md-init.sh's
# create_symlink). When the user is working inside the Dev-AID source repo
# itself, CLAUDE.md is a regular file. We use that distinction to decide
# whether to print the host-project scope reminder — the reminder only makes
# sense in installs, not in upstream Dev-AID development.
#
# This is the SessionStart half of issue #144. The matching pieces are
# .dev-aid/HOST_PROJECT.md and the visual divider in the CLAUDE.md template
# generators (.dev-aid/scripts/lib/claude-md-merger.sh).
# ----------------------------------------------------------------------------
readonly TOP_CLAUDE_MD="$CLAUDE_PROJECT_DIR/CLAUDE.md"
if [[ -L "$TOP_CLAUDE_MD" ]]; then
    echo "🛡️  Dev-AID scaffold loaded — host project root: $CLAUDE_PROJECT_DIR"
    echo "    Default scope: edit host-project files. Treat .dev-aid/ as managed"
    echo "    scaffold (see .dev-aid/HOST_PROJECT.md). Ask before editing scaffold"
    echo "    files unless the user explicitly asked to contribute to Dev-AID."
    echo ""
fi

# Validate memory bank path containment
resolved_memory_bank="$(realpath -m "$MEMORY_BANK_DIR" 2>/dev/null)" || {
    echo "ℹ️  Memory Bank directory not found. Initialize with /update-memory-bank"
    exit 0
}

if [[ "$resolved_memory_bank" != "$RESOLVED_PROJECT_DIR"* ]]; then
    echo "Error: Path traversal detected! Memory bank outside project directory" >&2
    exit 1
fi

# Check if memory bank exists
if [[ ! -f "$ACTIVE_CONTEXT" ]]; then
    echo "ℹ️  Memory Bank not found. Initialize with /update-memory-bank"
    exit 0
fi

# Load active context
echo "🧠 Loading Memory Bank..."
echo ""
echo "📋 Active Context loaded from: $ACTIVE_CONTEXT"
echo ""
echo "Available context files:"
echo "  - CLAUDE-activeContext.md (current session state)"
echo "  - CLAUDE-patterns.md (proven code patterns)"
echo "  - CLAUDE-decisions.md (architecture decisions)"
echo "  - CLAUDE-security.md (security patterns)"
echo "  - CLAUDE-performance.md (performance baselines)"
echo "  - CLAUDE-testing.md (test strategies)"
echo "  - CLAUDE-chaos.md (resilience experiments)"
echo ""
echo "💡 Load specific context with: 'Load CLAUDE-patterns.md'"
echo ""

# Display current session state summary
if grep -q "## 🎯 Current Sprint/Session Goals" "$ACTIVE_CONTEXT"; then
  echo "🎯 Current Session Goals:"
  grep -A 5 "## 🎯 Current Sprint/Session Goals" "$ACTIVE_CONTEXT" | grep "- \[ \]" | head -3
  echo ""
fi

# Exit successfully
exit 0
