#!/usr/bin/env bash
# ============================================================================
# Dev-AID Process Skill: Isolated Development — Worktree Setup
# ============================================================================
# Creates a git worktree from the current branch, runs baseline tests in
# the worktree, and verifies clean isolation (no uncommitted changes leaking).
#
# Exit codes:
#   0 = PASS  — Worktree created and verified
#   1 = FAIL  — Worktree creation or verification failed
#   2 = WARN  — Worktree created with warnings
#
# Usage:
#   ./setup-worktree.sh [OPTIONS] <BRANCH_NAME> [WORKTREE_DIR]
#
# ============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Color Output Helpers
# ---------------------------------------------------------------------------
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    BLUE='\033[0;34m'
    BOLD='\033[1m'
    RESET='\033[0m'
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    BOLD=''
    RESET=''
fi

# ---------------------------------------------------------------------------
# Script Metadata
# ---------------------------------------------------------------------------
SCRIPT_NAME="$(basename "$0")"
SCRIPT_VERSION="1.0.0"
SCRIPT_DESC="Create git worktree, run baseline tests, verify clean isolation"

# ---------------------------------------------------------------------------
# Logging Helpers
# ---------------------------------------------------------------------------
log_pass() { printf "${GREEN}[PASS]${RESET} %s\n" "$1"; }
log_fail() { printf "${RED}[FAIL]${RESET} %s\n" "$1"; }
log_warn() { printf "${YELLOW}[WARN]${RESET} %s\n" "$1"; }
log_info() { printf "${BLUE}[INFO]${RESET} %s\n" "$1"; }
log_step() { printf "${BOLD}==> %s${RESET}\n" "$1"; }

# ---------------------------------------------------------------------------
# Result Tracking
# ---------------------------------------------------------------------------
PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

record_pass() { PASS_COUNT=$((PASS_COUNT + 1)); log_pass "$1"; }
record_fail() { FAIL_COUNT=$((FAIL_COUNT + 1)); log_fail "$1"; }
record_warn() { WARN_COUNT=$((WARN_COUNT + 1)); log_warn "$1"; }

# ---------------------------------------------------------------------------
# Usage / Help
# ---------------------------------------------------------------------------
usage() {
    cat <<EOF
${BOLD}${SCRIPT_NAME}${RESET} v${SCRIPT_VERSION} — ${SCRIPT_DESC}

${BOLD}USAGE:${RESET}
    ${SCRIPT_NAME} [OPTIONS] <BRANCH_NAME> [WORKTREE_DIR]

${BOLD}OPTIONS:${RESET}
    -h, --help          Show this help message
    -v, --verbose       Enable verbose output
    -q, --quiet         Suppress non-error output
    --skip-tests        Skip baseline test run
    --skip-install      Skip dependency installation

${BOLD}ARGUMENTS:${RESET}
    BRANCH_NAME     Name for the new branch (e.g., fix/123, feature/oauth)
    WORKTREE_DIR    Worktree directory path (defaults to .worktrees/<branch-name>)

${BOLD}EXIT CODES:${RESET}
    0   Worktree created and verified
    1   Worktree creation or verification failed
    2   Worktree created with warnings

${BOLD}EXAMPLES:${RESET}
    ${SCRIPT_NAME} fix/123                     # Create worktree for issue 123
    ${SCRIPT_NAME} feature/oauth               # Create worktree for feature
    ${SCRIPT_NAME} fix/123 /tmp/my-worktree    # Custom worktree path
    ${SCRIPT_NAME} --skip-tests fix/456        # Skip baseline tests
EOF
}

# ---------------------------------------------------------------------------
# Argument Parsing
# ---------------------------------------------------------------------------
VERBOSE=false
QUIET=false
SKIP_TESTS=false
SKIP_INSTALL=false
BRANCH_NAME=""
WORKTREE_DIR=""

parse_args() {
    while [ $# -gt 0 ]; do
        case "$1" in
            -h|--help) usage; exit 0 ;;
            -v|--verbose) VERBOSE=true ;;
            -q|--quiet) QUIET=true ;;
            --skip-tests) SKIP_TESTS=true ;;
            --skip-install) SKIP_INSTALL=true ;;
            -*)
                log_warn "Unknown option: $1"
                ;;
            *)
                if [ -z "$BRANCH_NAME" ]; then
                    BRANCH_NAME="$1"
                elif [ -z "$WORKTREE_DIR" ]; then
                    WORKTREE_DIR="$1"
                else
                    log_warn "Unexpected argument: $1"
                fi
                ;;
        esac
        shift
    done

    if [ -z "$BRANCH_NAME" ]; then
        log_fail "BRANCH_NAME is required"
        echo ""
        usage
        exit 1
    fi

    # Default worktree dir: .worktrees/<branch-name-sanitized>
    if [ -z "$WORKTREE_DIR" ]; then
        local sanitized
        sanitized=$(echo "$BRANCH_NAME" | tr '/' '-')
        WORKTREE_DIR=".worktrees/${sanitized}"
    fi
}

# ---------------------------------------------------------------------------
# Project Detection
# ---------------------------------------------------------------------------
detect_project_type() {
    local dir="${1:-.}"
    if [ -f "${dir}/pyproject.toml" ] || [ -f "${dir}/setup.py" ] || [ -f "${dir}/requirements.txt" ]; then
        echo "python"
    elif [ -f "${dir}/package.json" ]; then
        echo "node"
    elif [ -f "${dir}/Cargo.toml" ]; then
        echo "rust"
    elif [ -f "${dir}/go.mod" ]; then
        echo "go"
    else
        echo "unknown"
    fi
}

# ---------------------------------------------------------------------------
# Step 1: Verify Git Repository
# ---------------------------------------------------------------------------
check_git_repo() {
    log_step "Verifying git repository..."

    if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        record_fail "Not inside a git repository"
        return 1
    fi
    record_pass "Inside git repository"

    # Check for uncommitted changes in current worktree
    local status
    status=$(git status --porcelain 2>/dev/null)
    if [ -n "$status" ]; then
        record_warn "Current worktree has uncommitted changes — they will NOT leak to new worktree"
        if [ "$VERBOSE" = true ]; then
            printf "  %s\n" "$status"
        fi
    else
        record_pass "Current worktree is clean"
    fi
}

# ---------------------------------------------------------------------------
# Step 2: Create Worktree
# ---------------------------------------------------------------------------
create_worktree() {
    log_step "Creating worktree: ${WORKTREE_DIR} (branch: ${BRANCH_NAME})..."

    # Check if worktree already exists
    if [ -d "$WORKTREE_DIR" ]; then
        record_fail "Worktree directory already exists: ${WORKTREE_DIR}"
        log_info "Use 'git worktree remove ${WORKTREE_DIR}' to remove it first"
        return 1
    fi

    # Check if branch already exists
    if git show-ref --verify --quiet "refs/heads/${BRANCH_NAME}" 2>/dev/null; then
        log_info "Branch '${BRANCH_NAME}' already exists, checking it out in worktree"
        if git worktree add "$WORKTREE_DIR" "$BRANCH_NAME" 2>&1; then
            record_pass "Worktree created from existing branch: ${BRANCH_NAME}"
        else
            record_fail "Failed to create worktree from existing branch"
            return 1
        fi
    else
        log_info "Creating new branch '${BRANCH_NAME}' from current HEAD"
        if git worktree add "$WORKTREE_DIR" -b "$BRANCH_NAME" 2>&1; then
            record_pass "Worktree created with new branch: ${BRANCH_NAME}"
        else
            record_fail "Failed to create worktree with new branch"
            return 1
        fi
    fi
}

# ---------------------------------------------------------------------------
# Step 3: Install Dependencies
# ---------------------------------------------------------------------------
install_dependencies() {
    if [ "$SKIP_INSTALL" = true ]; then
        log_info "Skipping dependency installation (--skip-install)"
        return
    fi

    local project_type
    project_type=$(detect_project_type "$WORKTREE_DIR")

    log_step "Installing dependencies (${project_type})..."

    case "$project_type" in
        python)
            if [ -f "${WORKTREE_DIR}/pyproject.toml" ] && command -v uv >/dev/null 2>&1; then
                (cd "$WORKTREE_DIR" && uv sync 2>&1) && record_pass "Dependencies installed (uv sync)" || record_warn "uv sync failed"
            elif [ -f "${WORKTREE_DIR}/pyproject.toml" ] && command -v poetry >/dev/null 2>&1; then
                (cd "$WORKTREE_DIR" && poetry install 2>&1) && record_pass "Dependencies installed (poetry)" || record_warn "poetry install failed"
            elif [ -f "${WORKTREE_DIR}/requirements.txt" ]; then
                (cd "$WORKTREE_DIR" && pip install -r requirements.txt 2>&1) && record_pass "Dependencies installed (pip)" || record_warn "pip install failed"
            else
                record_warn "Python project detected but no standard dependency file found"
            fi
            ;;
        node)
            if [ -f "${WORKTREE_DIR}/pnpm-lock.yaml" ]; then
                (cd "$WORKTREE_DIR" && pnpm install 2>&1) && record_pass "Dependencies installed (pnpm)" || record_warn "pnpm install failed"
            elif [ -f "${WORKTREE_DIR}/yarn.lock" ]; then
                (cd "$WORKTREE_DIR" && yarn install 2>&1) && record_pass "Dependencies installed (yarn)" || record_warn "yarn install failed"
            else
                (cd "$WORKTREE_DIR" && npm install 2>&1) && record_pass "Dependencies installed (npm)" || record_warn "npm install failed"
            fi
            ;;
        rust)
            (cd "$WORKTREE_DIR" && cargo build 2>&1) && record_pass "Dependencies built (cargo)" || record_warn "cargo build failed"
            ;;
        go)
            (cd "$WORKTREE_DIR" && go mod download 2>&1) && record_pass "Dependencies downloaded (go mod)" || record_warn "go mod download failed"
            ;;
        *)
            record_warn "Unknown project type — skipping dependency installation"
            ;;
    esac
}

# ---------------------------------------------------------------------------
# Step 4: Run Baseline Tests
# ---------------------------------------------------------------------------
run_baseline_tests() {
    if [ "$SKIP_TESTS" = true ]; then
        log_info "Skipping baseline tests (--skip-tests)"
        return
    fi

    local project_type
    project_type=$(detect_project_type "$WORKTREE_DIR")

    log_step "Running baseline tests in worktree..."

    local test_output
    local test_exit=0

    case "$project_type" in
        python)
            test_output=$(cd "$WORKTREE_DIR" && python -m pytest -v 2>&1) || test_exit=$?
            ;;
        node)
            test_output=$(cd "$WORKTREE_DIR" && npm test 2>&1) || test_exit=$?
            ;;
        rust)
            test_output=$(cd "$WORKTREE_DIR" && cargo test 2>&1) || test_exit=$?
            ;;
        go)
            test_output=$(cd "$WORKTREE_DIR" && go test ./... 2>&1) || test_exit=$?
            ;;
        *)
            record_warn "Unknown project type — cannot run baseline tests"
            return
            ;;
    esac

    if [ "$test_exit" -eq 0 ]; then
        record_pass "Baseline tests pass in worktree"
    else
        record_fail "Baseline tests FAIL in worktree — fix before starting work"
        if [ "$VERBOSE" = true ] && [ -n "$test_output" ]; then
            printf "  %s\n" "$test_output" | tail -20
        fi
    fi
}

# ---------------------------------------------------------------------------
# Step 5: Verify Clean Isolation
# ---------------------------------------------------------------------------
verify_isolation() {
    log_step "Verifying clean isolation..."

    # Check worktree has no unexpected changes
    local wt_status
    wt_status=$(cd "$WORKTREE_DIR" && git status --porcelain 2>/dev/null)

    if [ -z "$wt_status" ]; then
        record_pass "Worktree is clean — no uncommitted changes"
    else
        record_warn "Worktree has uncommitted changes (possibly from dependency install)"
        if [ "$VERBOSE" = true ]; then
            printf "  %s\n" "$wt_status"
        fi
    fi

    # Verify worktree is on the correct branch
    local current_branch
    current_branch=$(cd "$WORKTREE_DIR" && git branch --show-current 2>/dev/null)

    if [ "$current_branch" = "$BRANCH_NAME" ]; then
        record_pass "Worktree is on correct branch: ${BRANCH_NAME}"
    else
        record_fail "Worktree is on wrong branch: ${current_branch} (expected: ${BRANCH_NAME})"
    fi

    # Verify main worktree was not affected
    local main_status
    main_status=$(git status --porcelain 2>/dev/null)
    local original_unchanged=true

    # Compare only tracked file status (ignore worktree dir itself)
    if [ -n "$main_status" ]; then
        # Filter out .worktrees directory from status
        local filtered_status
        filtered_status=$(echo "$main_status" | grep -v "^.. .worktrees/" || true)
        if [ -n "$filtered_status" ]; then
            original_unchanged=false
        fi
    fi

    if [ "$original_unchanged" = true ]; then
        record_pass "Main worktree unchanged — isolation verified"
    else
        record_warn "Main worktree has changes (pre-existing, not caused by worktree creation)"
    fi
}

# ---------------------------------------------------------------------------
# Main Checks
# ---------------------------------------------------------------------------
run_checks() {
    log_step "Isolated Development — Worktree Setup"
    log_info "Branch: ${BRANCH_NAME}"
    log_info "Worktree: ${WORKTREE_DIR}"
    echo ""

    check_git_repo || return 1
    echo ""
    create_worktree || return 1
    echo ""
    install_dependencies
    echo ""
    run_baseline_tests
    echo ""
    verify_isolation
}

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print_summary() {
    echo ""
    log_step "Summary"
    printf "  Passed:   %d\n" "$PASS_COUNT"
    printf "  Failed:   %d\n" "$FAIL_COUNT"
    printf "  Warnings: %d\n" "$WARN_COUNT"
    echo ""

    if [ "$FAIL_COUNT" -eq 0 ]; then
        log_info "Worktree ready at: ${WORKTREE_DIR}"
        log_info "To start working:  cd ${WORKTREE_DIR}"
    fi
}

determine_exit_code() {
    if [ "$FAIL_COUNT" -gt 0 ]; then
        log_fail "Overall: FAILED — worktree setup incomplete"
        return 1
    elif [ "$WARN_COUNT" -gt 0 ]; then
        log_warn "Overall: PASSED WITH WARNINGS"
        return 2
    else
        log_pass "Overall: ALL CHECKS PASSED — worktree ready"
        return 0
    fi
}

# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
main() {
    parse_args "$@"
    run_checks
    print_summary
    determine_exit_code
}

main "$@"
