#!/usr/bin/env bash
#
# Script: sync-worktrees.sh
# Description: Sync and check for conflicts between git worktrees
# Usage: ./sync-worktrees.sh [options]
#
# Checks for potential merge conflicts between worktrees before they happen.
#

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[0;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m'

# Logging
log_info() { echo -e "${BLUE}[sync]${NC} $*"; }
log_success() { echo -e "${GREEN}[sync]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[sync]${NC} $*"; }
log_error() { echo -e "${RED}[sync]${NC} $*" >&2; }

# Find git root
find_git_root() {
    git rev-parse --show-toplevel 2>/dev/null
}

# Show usage
usage() {
    cat <<EOF
Usage: $SCRIPT_NAME [options]

Sync worktrees and detect potential conflicts before merge.

Options:
  -c, --check      Check for conflicts only (no updates)
  -v, --verbose    Show detailed conflict analysis
  -f, --fix        Attempt to rebase worktrees on latest base
  -l, --list       List all worktrees with status
  -h, --help       Show this help message

Examples:
  $SCRIPT_NAME --check       # Check all worktrees for conflicts
  $SCRIPT_NAME --list        # Show worktree status
  $SCRIPT_NAME --verbose     # Detailed conflict report
EOF
}

# List all worktrees
list_worktrees() {
    local git_root="$1"
    local verbose="${2:-false}"

    echo ""
    echo -e "${CYAN}Git Worktrees:${NC}"
    echo ""

    # Get worktree list from git
    while IFS= read -r line; do
        local wt_path branch commit

        # Parse git worktree list output
        wt_path=$(echo "$line" | awk '{print $1}')
        commit=$(echo "$line" | awk '{print $2}')
        branch=$(echo "$line" | sed 's/.*\[\(.*\)\].*/\1/' | grep -oE '[^]]+' || echo "detached")

        # Get status
        local status="clean"
        local changes=0
        if [[ -d "$wt_path" ]]; then
            changes=$(git -C "$wt_path" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
            if [[ "$changes" -gt 0 ]]; then
                status="$changes changes"
            fi
        fi

        # Check scope
        local scope_status=""
        if [[ -f "$wt_path/SCOPE.md" ]]; then
            scope_status="[scope declared]"
        fi

        echo -e "  ${GREEN}$branch${NC}"
        echo "    Path: $wt_path"
        echo "    Status: $status $scope_status"

        if [[ "$verbose" == "true" && -f "$wt_path/SCOPE.md" ]]; then
            echo "    Scope:"
            grep -E '^\s*-\s*`' "$wt_path/SCOPE.md" 2>/dev/null | head -5 | while read -r scope_line; do
                echo "      $scope_line"
            done
        fi
        echo ""

    done < <(git worktree list 2>/dev/null)
}

# Get modified files for a worktree
get_modified_files() {
    local wt_path="$1"
    local base_branch="$2"

    if [[ ! -d "$wt_path" ]]; then
        return
    fi

    # Get files modified in this worktree compared to base
    git -C "$wt_path" diff --name-only "$base_branch"...HEAD 2>/dev/null || true
}

# Check for potential conflicts between worktrees
check_conflicts() {
    local git_root="$1"
    local verbose="${2:-false}"

    log_info "Checking for potential conflicts between worktrees..."
    echo ""

    local worktree_files=()
    local worktree_names=()

    # Collect modified files from each worktree
    while IFS= read -r line; do
        local wt_path branch

        wt_path=$(echo "$line" | awk '{print $1}')
        branch=$(echo "$line" | sed 's/.*\[\(.*\)\].*/\1/' | grep -oE '[^]]+' || echo "")

        [[ -z "$branch" || "$branch" == "detached" ]] && continue

        # Skip main worktree
        [[ "$wt_path" == "$git_root" ]] && continue

        # Get base branch (default to main)
        local base_branch="main"
        if git -C "$wt_path" show-ref --verify --quiet refs/heads/main 2>/dev/null; then
            base_branch="main"
        elif git -C "$wt_path" show-ref --verify --quiet refs/heads/master 2>/dev/null; then
            base_branch="master"
        fi

        # Get modified files
        local files
        files=$(get_modified_files "$wt_path" "$base_branch")

        if [[ -n "$files" ]]; then
            worktree_names+=("$branch")
            worktree_files+=("$files")
        fi

    done < <(git worktree list 2>/dev/null)

    # Check for overlapping files
    local conflicts_found=false
    local conflict_count=0

    for i in "${!worktree_names[@]}"; do
        for j in "${!worktree_names[@]}"; do
            [[ $i -ge $j ]] && continue

            local branch1="${worktree_names[$i]}"
            local branch2="${worktree_names[$j]}"
            local files1="${worktree_files[$i]}"
            local files2="${worktree_files[$j]}"

            # Find common files
            local common_files
            common_files=$(comm -12 <(echo "$files1" | sort) <(echo "$files2" | sort) 2>/dev/null)

            if [[ -n "$common_files" ]]; then
                conflicts_found=true
                conflict_count=$((conflict_count + $(echo "$common_files" | wc -l)))

                echo -e "${YELLOW}Potential conflict:${NC} $branch1 <-> $branch2"

                if [[ "$verbose" == "true" ]]; then
                    echo "  Common files:"
                    echo "$common_files" | while read -r file; do
                        echo "    - $file"
                    done
                else
                    local file_count
                    file_count=$(echo "$common_files" | wc -l | tr -d ' ')
                    echo "  $file_count file(s) modified in both branches"
                fi
                echo ""
            fi
        done
    done

    if [[ "$conflicts_found" == "true" ]]; then
        echo ""
        log_warn "Found $conflict_count potential conflict(s)"
        echo ""
        echo "Recommendations:"
        echo "  1. Merge one branch first, then rebase the other"
        echo "  2. Coordinate with team members working on conflicting files"
        echo "  3. Run 'git merge-tree' to preview conflicts"
        return 1
    else
        log_success "No potential conflicts detected between worktrees"
        return 0
    fi
}

# Update worktrees from base branch
update_worktrees() {
    local git_root="$1"

    log_info "Updating worktrees from base branches..."

    while IFS= read -r line; do
        local wt_path branch

        wt_path=$(echo "$line" | awk '{print $1}')
        branch=$(echo "$line" | sed 's/.*\[\(.*\)\].*/\1/' | grep -oE '[^]]+' || echo "")

        [[ -z "$branch" || "$branch" == "detached" ]] && continue
        [[ "$wt_path" == "$git_root" ]] && continue

        echo ""
        log_info "Updating $branch..."

        # Fetch latest
        git -C "$wt_path" fetch origin 2>/dev/null || true

        # Check for uncommitted changes
        local changes
        changes=$(git -C "$wt_path" status --porcelain 2>/dev/null | wc -l | tr -d ' ')
        if [[ "$changes" -gt 0 ]]; then
            log_warn "Skipping $branch - has uncommitted changes"
            continue
        fi

        # Try to pull/rebase
        if git -C "$wt_path" pull --rebase 2>/dev/null; then
            log_success "Updated $branch"
        else
            log_warn "Could not update $branch - may need manual intervention"
        fi

    done < <(git worktree list 2>/dev/null)
}

# Main function
main() {
    local check_only=false
    local verbose=false
    local do_fix=false
    local list_only=false

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                usage
                exit 0
                ;;
            -c|--check)
                check_only=true
                shift
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            -f|--fix)
                do_fix=true
                shift
                ;;
            -l|--list)
                list_only=true
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done

    # Find git root
    local git_root
    git_root=$(find_git_root)
    if [[ -z "$git_root" ]]; then
        log_error "Not in a git repository"
        exit 1
    fi

    # List worktrees
    if [[ "$list_only" == "true" ]]; then
        list_worktrees "$git_root" "$verbose"
        exit 0
    fi

    # Check for conflicts
    echo ""
    list_worktrees "$git_root" "$verbose"

    if ! check_conflicts "$git_root" "$verbose"; then
        exit 1
    fi

    # Update if requested
    if [[ "$do_fix" == "true" && "$check_only" == "false" ]]; then
        update_worktrees "$git_root"
    fi
}

main "$@"
