#!/usr/bin/env bash
# Post Tool Use Hook - Track File Modifications
# Runs after Edit, MultiEdit, Write operations
# Appends a single line to .claude/modification-log.txt per invocation.

set -euo pipefail

# CLAUDE_PROJECT_DIR is required to know where to write the log.
if [[ -z "${CLAUDE_PROJECT_DIR:-}" ]]; then
    exit 0
fi

# Validate CLAUDE_PROJECT_DIR is a real directory before writing into it.
if [[ ! -d "$CLAUDE_PROJECT_DIR" ]]; then
    exit 0
fi

LOG_DIR="$CLAUDE_PROJECT_DIR/.claude"
LOG_FILE="$LOG_DIR/modification-log.txt"

# Ensure .claude/ exists (it should, but be defensive).
mkdir -p "$LOG_DIR"

# Use ISO-8601 UTC for stable, sortable timestamps.
timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
tool_name="${CLAUDE_TOOL_NAME:-unknown}"
modified_files="${CLAUDE_MODIFIED_FILES:-}"

# One line per invocation: timestamp | tool | files
printf '%s | %s | %s\n' "$timestamp" "$tool_name" "$modified_files" >> "$LOG_FILE"

exit 0
