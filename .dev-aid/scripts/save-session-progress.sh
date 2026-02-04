#!/usr/bin/env bash
#
# Script: save-session-progress.sh
# Description: Captures session progress for persistence across restarts
# Usage: Called by provider hooks at session end
#
# Captures:
#   - Git diff --stat (what changed)
#   - Modified files list
#   - Current branch name
#   - Timestamp
#   - Session duration (if available)
#   - Active tasks/todos
#

set -euo pipefail

# Script configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[0;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[info]${NC} $*"; }
log_success() { echo -e "${GREEN}[ok]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[warn]${NC} $*"; }
log_error() { echo -e "${RED}[error]${NC} $*" >&2; }

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
    local progress_file="$progress_dir/session-$(date +%Y%m%d-%H%M%S).json"
    local latest_link="$progress_dir/latest.json"

    # Create progress directory if needed
    mkdir -p "$progress_dir"

    # Collect git information
    local branch=""
    local diff_stat=""
    local modified_files=""
    local staged_files=""
    local untracked_files=""

    if git -C "$project_root" rev-parse --is-inside-work-tree &>/dev/null; then
        branch=$(git -C "$project_root" branch --show-current 2>/dev/null || echo "detached")
        diff_stat=$(git -C "$project_root" diff --stat 2>/dev/null | tail -20 || echo "")
        modified_files=$(git -C "$project_root" diff --name-only 2>/dev/null | head -50 || echo "")
        staged_files=$(git -C "$project_root" diff --cached --name-only 2>/dev/null | head -50 || echo "")
        untracked_files=$(git -C "$project_root" ls-files --others --exclude-standard 2>/dev/null | head -20 || echo "")
    fi

    # Get current timestamp
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    # Check for active tasks (if todo.md exists)
    local active_tasks=""
    if [[ -f "$project_root/.dev-aid/todo.md" ]]; then
        active_tasks=$(grep -E "^\s*- \[ \]" "$project_root/.dev-aid/todo.md" 2>/dev/null | head -10 || echo "")
    fi

    # Check for memory bank context
    local active_context=""
    if [[ -f "$project_root/memory-bank/CLAUDE-activeContext.md" ]]; then
        active_context=$(head -50 "$project_root/memory-bank/CLAUDE-activeContext.md" 2>/dev/null || echo "")
    fi

    # Get provider from environment (set by hook caller)
    local provider="${DEV_AID_PROVIDER:-unknown}"

    # Get session start time if available
    local session_start="${DEV_AID_SESSION_START:-}"
    local session_duration=""
    if [[ -n "$session_start" ]]; then
        local now
        now=$(date +%s)
        local duration=$((now - session_start))
        local hours=$((duration / 3600))
        local minutes=$(((duration % 3600) / 60))
        session_duration="${hours}h ${minutes}m"
    fi

    # Build JSON output
    cat > "$progress_file" <<EOF
{
  "version": "1.0.0",
  "timestamp": "$timestamp",
  "provider": "$provider",
  "session_duration": "$session_duration",
  "git": {
    "branch": "$branch",
    "diff_summary": $(echo "$diff_stat" | tail -1 | jq -Rs . 2>/dev/null || echo '""'),
    "modified_files": $(echo "$modified_files" | jq -Rs 'split("\n") | map(select(length > 0))' 2>/dev/null || echo '[]'),
    "staged_files": $(echo "$staged_files" | jq -Rs 'split("\n") | map(select(length > 0))' 2>/dev/null || echo '[]'),
    "untracked_files": $(echo "$untracked_files" | jq -Rs 'split("\n") | map(select(length > 0))' 2>/dev/null || echo '[]')
  },
  "tasks": {
    "pending": $(echo "$active_tasks" | jq -Rs 'split("\n") | map(select(length > 0))' 2>/dev/null || echo '[]')
  },
  "context_summary": $(echo "$active_context" | head -200 | jq -Rs . 2>/dev/null || echo '""')
}
EOF

    # Update latest symlink
    ln -sf "$(basename "$progress_file")" "$latest_link"

    # Print summary
    echo ""
    log_success "Session progress saved"
    echo ""

    if [[ -n "$branch" ]]; then
        echo "  Branch: $branch"
    fi

    if [[ -n "$modified_files" ]]; then
        local file_count
        file_count=$(echo "$modified_files" | wc -l | tr -d ' ')
        echo "  Modified files: $file_count"
    fi

    if [[ -n "$staged_files" ]]; then
        local staged_count
        staged_count=$(echo "$staged_files" | wc -l | tr -d ' ')
        echo "  Staged files: $staged_count"
    fi

    if [[ -n "$session_duration" ]]; then
        echo "  Duration: $session_duration"
    fi

    echo ""
    echo "  Progress file: $progress_file"
    echo ""

    # Cleanup old progress files (keep last 10)
    local old_files
    old_files=$(ls -1t "$progress_dir"/session-*.json 2>/dev/null | tail -n +11)
    if [[ -n "$old_files" ]]; then
        echo "$old_files" | xargs rm -f 2>/dev/null || true
        log_info "Cleaned up old progress files"
    fi
}

# Run main with provided arguments
main "$@"
