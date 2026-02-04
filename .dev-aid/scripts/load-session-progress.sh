#!/usr/bin/env bash
#
# Script: load-session-progress.sh
# Description: Loads previous session progress for context continuity
# Usage: Called by provider hooks at session start
#
# Outputs session context to stdout for LLM consumption
#

set -euo pipefail

# Script configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Determine project root
find_project_root() {
    local dir="${1:-.}"
    while [[ "$dir" != "/" ]]; do
        if [[ -d "$dir/.git" ]]; then
            echo "$dir"
            return 0
        fi
        dir="$(dirname "$dir")"
    done
    echo "."
}

# Main function
main() {
    local project_root="${1:-$(pwd)}"
    project_root="$(find_project_root "$project_root")"

    local progress_dir="$project_root/.dev-aid/session-progress"
    local latest_link="$progress_dir/latest.json"

    # Check if progress exists
    if [[ ! -f "$latest_link" ]]; then
        return 0
    fi

    # Read latest progress
    local progress_file
    progress_file=$(readlink "$latest_link" 2>/dev/null || echo "")
    if [[ -z "$progress_file" ]]; then
        return 0
    fi

    local full_path="$progress_dir/$progress_file"
    if [[ ! -f "$full_path" ]]; then
        return 0
    fi

    # Check if progress is recent (within last 24 hours)
    local file_age
    if [[ "$(uname)" == "Darwin" ]]; then
        file_age=$(( $(date +%s) - $(stat -f %m "$full_path") ))
    else
        file_age=$(( $(date +%s) - $(stat -c %Y "$full_path") ))
    fi

    if (( file_age > 86400 )); then
        # Progress is more than 24 hours old, skip
        return 0
    fi

    # Parse and output relevant context
    echo ""
    echo "## Previous Session Context"
    echo ""

    # Extract key information
    local branch timestamp modified staged

    if command -v jq &>/dev/null; then
        branch=$(jq -r '.git.branch // ""' "$full_path" 2>/dev/null || echo "")
        timestamp=$(jq -r '.timestamp // ""' "$full_path" 2>/dev/null || echo "")
        modified=$(jq -r '.git.modified_files | length' "$full_path" 2>/dev/null || echo "0")
        staged=$(jq -r '.git.staged_files | length' "$full_path" 2>/dev/null || echo "0")
        local pending_tasks
        pending_tasks=$(jq -r '.tasks.pending | length' "$full_path" 2>/dev/null || echo "0")

        if [[ -n "$branch" ]]; then
            echo "- **Branch**: $branch"
        fi

        if [[ -n "$timestamp" ]]; then
            echo "- **Last session**: $timestamp"
        fi

        if [[ "$modified" -gt 0 ]]; then
            echo "- **Uncommitted changes**: $modified files"
            echo ""
            echo "**Modified files:**"
            jq -r '.git.modified_files[]' "$full_path" 2>/dev/null | while read -r file; do
                echo "  - \`$file\`"
            done
        fi

        if [[ "$staged" -gt 0 ]]; then
            echo ""
            echo "**Staged for commit:**"
            jq -r '.git.staged_files[]' "$full_path" 2>/dev/null | while read -r file; do
                echo "  - \`$file\`"
            done
        fi

        if [[ "$pending_tasks" -gt 0 ]]; then
            echo ""
            echo "**Pending tasks:**"
            jq -r '.tasks.pending[]' "$full_path" 2>/dev/null | while read -r task; do
                echo "$task"
            done
        fi

        # Show context summary if available
        local context_summary
        context_summary=$(jq -r '.context_summary // ""' "$full_path" 2>/dev/null || echo "")
        if [[ -n "$context_summary" && "$context_summary" != "null" && "$context_summary" != '""' ]]; then
            echo ""
            echo "**Context from previous session:**"
            echo "$context_summary" | head -20
        fi
    else
        # Fallback without jq - just show that progress exists
        echo "Previous session progress available at: $full_path"
        echo "(Install jq for detailed parsing)"
    fi

    echo ""
}

# Run main with provided arguments
main "$@"
