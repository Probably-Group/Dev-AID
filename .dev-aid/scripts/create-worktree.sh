#!/usr/bin/env bash
#
# Script: create-worktree.sh
# Description: Create isolated git worktree for feature development
# Usage: ./create-worktree.sh <branch-name> [base-branch]
#
# Creates a worktree in .worktrees/<branch-name> with:
#   - Scope declaration file
#   - Architecture lock awareness
#   - Pre-configured for isolated development
#

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[0;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# Logging
log_info() { echo -e "${BLUE}[worktree]${NC} $*"; }
log_success() { echo -e "${GREEN}[worktree]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[worktree]${NC} $*"; }
log_error() { echo -e "${RED}[worktree]${NC} $*" >&2; }

# Find git root
find_git_root() {
    git rev-parse --show-toplevel 2>/dev/null
}

# Show usage
usage() {
    cat <<EOF
Usage: $SCRIPT_NAME <branch-name> [base-branch] [options]

Create an isolated git worktree for parallel development.

Arguments:
  branch-name     Name for the new branch/worktree
  base-branch     Branch to base off (default: current branch)

Options:
  -d, --dir DIR   Custom worktree directory (default: .worktrees/<branch>)
  -s, --scope     Scope declaration (files/directories this work touches)
  -h, --help      Show this help message

Examples:
  $SCRIPT_NAME feature/auth-oauth
  $SCRIPT_NAME fix/login-bug main
  $SCRIPT_NAME feature/new-api --scope "src/api,tests/api"

Safeguards:
  - Creates scope declaration file for conflict detection
  - Checks for architecture locks before creation
  - Warns about overlapping scopes with other worktrees
EOF
}

# Check for architecture locks
check_architecture_locks() {
    local git_root="$1"
    local scope="$2"

    local locks_dir="$git_root/.dev-aid/architecture-locks"
    if [[ ! -d "$locks_dir" ]]; then
        return 0
    fi

    local conflicts=()
    for lock_file in "$locks_dir"/*.lock; do
        [[ -f "$lock_file" ]] || continue

        local lock_name
        lock_name=$(basename "$lock_file" .lock)

        # Check if scope overlaps with locked paths
        while IFS= read -r locked_path; do
            [[ -z "$locked_path" || "$locked_path" == \#* ]] && continue

            IFS=',' read -ra scope_paths <<< "$scope"
            for scope_path in "${scope_paths[@]}"; do
                if [[ "$scope_path" == "$locked_path"* || "$locked_path" == "$scope_path"* ]]; then
                    conflicts+=("$lock_name: $locked_path")
                fi
            done
        done < "$lock_file"
    done

    if [[ ${#conflicts[@]} -gt 0 ]]; then
        log_warn "Architecture locks detected for requested scope:"
        for conflict in "${conflicts[@]}"; do
            echo "  - $conflict"
        done
        return 1
    fi

    return 0
}

# Check for scope overlap with existing worktrees
check_scope_overlap() {
    local git_root="$1"
    local scope="$2"
    local new_branch="$3"

    local worktrees_dir="$git_root/.worktrees"
    if [[ ! -d "$worktrees_dir" ]]; then
        return 0
    fi

    local overlaps=()
    for scope_file in "$worktrees_dir"/*/SCOPE.md; do
        [[ -f "$scope_file" ]] || continue

        local wt_dir
        wt_dir=$(dirname "$scope_file")
        local wt_name
        wt_name=$(basename "$wt_dir")

        # Skip if same worktree
        [[ "$wt_name" == "$new_branch" ]] && continue

        # Extract paths from scope file
        local wt_paths
        wt_paths=$(grep -E '^\s*-\s*`' "$scope_file" 2>/dev/null | sed 's/.*`\([^`]*\)`.*/\1/' || true)

        for wt_path in $wt_paths; do
            IFS=',' read -ra scope_paths <<< "$scope"
            for scope_path in "${scope_paths[@]}"; do
                if [[ "$scope_path" == "$wt_path"* || "$wt_path" == "$scope_path"* ]]; then
                    overlaps+=("$wt_name: $wt_path")
                fi
            done
        done
    done

    if [[ ${#overlaps[@]} -gt 0 ]]; then
        log_warn "Scope overlap detected with existing worktrees:"
        for overlap in "${overlaps[@]}"; do
            echo "  - $overlap"
        done
        echo ""
        log_warn "Consider coordinating changes to avoid merge conflicts."
        return 0  # Warning only, don't block
    fi

    return 0
}

# Create scope declaration file
create_scope_declaration() {
    local worktree_dir="$1"
    local branch="$2"
    local scope="$3"
    local description="$4"

    cat > "$worktree_dir/SCOPE.md" <<EOF
# Worktree Scope Declaration

**Branch**: $branch
**Created**: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
**Author**: $(git config user.name 2>/dev/null || echo "Unknown")

## Description

$description

## Affected Paths

EOF

    if [[ -n "$scope" ]]; then
        IFS=',' read -ra scope_paths <<< "$scope"
        for path in "${scope_paths[@]}"; do
            echo "- \`$path\`" >> "$worktree_dir/SCOPE.md"
        done
    else
        echo "- *Scope not declared - please update*" >> "$worktree_dir/SCOPE.md"
    fi

    cat >> "$worktree_dir/SCOPE.md" <<'EOF'

## Guidelines

1. **Stay within scope**: Only modify files in the declared paths
2. **Update scope**: If you need to touch other files, update this declaration
3. **Sync regularly**: Run `sync-worktrees.sh` before merging
4. **Resolve conflicts early**: Don't wait until merge time

## Conflict Prevention

Before merging:
```bash
.dev-aid/scripts/sync-worktrees.sh --check
```

## Cleanup

When done:
```bash
git worktree remove .worktrees/<branch-name>
```
EOF

    log_success "Created SCOPE.md in worktree"
}

# Main function
main() {
    local branch_name=""
    local base_branch=""
    local custom_dir=""
    local scope=""

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                usage
                exit 0
                ;;
            -d|--dir)
                custom_dir="$2"
                shift 2
                ;;
            -s|--scope)
                scope="$2"
                shift 2
                ;;
            -*)
                log_error "Unknown option: $1"
                usage
                exit 1
                ;;
            *)
                if [[ -z "$branch_name" ]]; then
                    branch_name="$1"
                elif [[ -z "$base_branch" ]]; then
                    base_branch="$1"
                fi
                shift
                ;;
        esac
    done

    if [[ -z "$branch_name" ]]; then
        log_error "Branch name required"
        usage
        exit 1
    fi

    if [[ "$branch_name" =~ ^- ]]; then
        log_error "Invalid branch name (cannot start with -): $branch_name"
        exit 1
    fi

    # Find git root
    local git_root
    git_root=$(find_git_root)
    if [[ -z "$git_root" ]]; then
        log_error "Not in a git repository"
        exit 1
    fi

    # Default base branch to current branch
    if [[ -z "$base_branch" ]]; then
        base_branch=$(git branch --show-current)
    fi

    # Determine worktree directory
    local worktree_dir
    if [[ -n "$custom_dir" ]]; then
        worktree_dir="$custom_dir"
    else
        worktree_dir="$git_root/.worktrees/$branch_name"
    fi

    log_info "Creating worktree for branch: $branch_name"
    log_info "Base branch: $base_branch"
    log_info "Worktree directory: $worktree_dir"

    # Check for architecture locks
    if [[ -n "$scope" ]]; then
        if ! check_architecture_locks "$git_root" "$scope"; then
            echo ""
            read -p "Continue despite architecture locks? [y/N] " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                log_info "Aborted"
                exit 1
            fi
        fi

        # Check for scope overlap
        check_scope_overlap "$git_root" "$scope" "$branch_name"
    fi

    # Create worktrees directory if needed
    mkdir -p "$(dirname "$worktree_dir")"

    # Check if branch already exists
    if git show-ref --verify --quiet "refs/heads/$branch_name" 2>/dev/null; then
        log_info "Branch $branch_name already exists, using existing branch"
        git worktree add "$worktree_dir" "$branch_name"
    else
        log_info "Creating new branch $branch_name from $base_branch"
        git worktree add -b "$branch_name" "$worktree_dir" "$base_branch"
    fi

    # Prompt for description
    echo ""
    read -p "Brief description of this work: " description
    description="${description:-No description provided}"

    # Create scope declaration
    create_scope_declaration "$worktree_dir" "$branch_name" "$scope" "$description"

    # Create architecture locks directory if needed
    mkdir -p "$git_root/.dev-aid/architecture-locks"

    # Print summary
    echo ""
    log_success "Worktree created successfully!"
    echo ""
    echo "  Directory: $worktree_dir"
    echo "  Branch: $branch_name"
    echo "  Base: $base_branch"
    echo ""
    echo "To start working:"
    echo "  cd $worktree_dir"
    echo ""
    echo "When finished:"
    echo "  git worktree remove $worktree_dir"
}

main "$@"
