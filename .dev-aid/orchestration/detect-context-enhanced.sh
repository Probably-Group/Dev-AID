#!/usr/bin/env bash
#
# Script: detect-context-enhanced.sh
# Description: Enhanced context detection combining file patterns AND import analysis
# Usage: detect-context-enhanced.sh [directory]
#

# Strict mode: exit on error, undefined variables, pipe failures
set -euo pipefail

# Script directory (portable way)
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

# Cleanup function (always runs on exit)
cleanup() {
    local exit_code=$?
    [[ -n "${TEMP_COMBINED:-}" ]] && rm -f "$TEMP_COMBINED" 2>/dev/null || true
    exit "$exit_code"
}
trap cleanup EXIT INT TERM

# Configuration
readonly PROJECT_DIR="${1:-.}"

# Temporary file for combining results
TEMP_COMBINED=$(mktemp) || exit 1
chmod 600 "$TEMP_COMBINED"

# Main detection logic
main() {
    # Validate project directory
    if [[ ! -d "$PROJECT_DIR" ]]; then
        echo "Error: Directory does not exist: $PROJECT_DIR" >&2
        exit 1
    fi

    # Run both detection methods
    # 1. File-based detection (config files, file patterns)
    "$SCRIPT_DIR/detect-context.sh" "$PROJECT_DIR" >> "$TEMP_COMBINED" 2>/dev/null || true

    # 2. Import-based detection (source code analysis)
    "$SCRIPT_DIR/detect-imports.sh" "$PROJECT_DIR" 100 >> "$TEMP_COMBINED" 2>/dev/null || true

    # Combine and deduplicate results
    tr ' ' '\n' < "$TEMP_COMBINED" | \
        sort -u | \
        grep -v "^$" | \
        tr '\n' ' '

    echo  # Final newline
}

# Run main function
main
