#!/usr/bin/env bash
# ============================================================================
# Dev-AID Process Skill: TDD Protocol — TDD Gate Check
# ============================================================================
# Checks for failing tests before allowing implementation code. Detects
# project type, runs the appropriate test framework, and verifies the RED
# phase: at least one test must fail.
#
# Exit codes:
#   0 = PASS  — TDD gate passed (failing test exists, RED phase confirmed)
#   1 = FAIL  — No failing test found or wrong failure type
#   2 = WARN  — Partial compliance
#
# Usage:
#   ./tdd-gate.sh [OPTIONS] [PROJECT_DIR]
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
SCRIPT_DESC="Verify RED phase: at least one test must fail before implementation"

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
    ${SCRIPT_NAME} [OPTIONS] [PROJECT_DIR]

${BOLD}OPTIONS:${RESET}
    -h, --help      Show this help message
    -v, --verbose   Enable verbose output
    -q, --quiet     Suppress non-error output
    --check-only    Only check for test files, don't run tests

${BOLD}ARGUMENTS:${RESET}
    PROJECT_DIR     Path to project root (defaults to current directory)

${BOLD}EXIT CODES:${RESET}
    0   TDD gate passed (RED phase confirmed)
    1   No failing test or wrong failure type
    2   Partial compliance

${BOLD}EXAMPLES:${RESET}
    ${SCRIPT_NAME}                  # Check current directory
    ${SCRIPT_NAME} --verbose        # Verbose output
    ${SCRIPT_NAME} --check-only     # Only verify test files exist
EOF
}

# ---------------------------------------------------------------------------
# Argument Parsing
# ---------------------------------------------------------------------------
VERBOSE=false
QUIET=false
CHECK_ONLY=false
PROJECT_DIR="."

parse_args() {
    while [ $# -gt 0 ]; do
        case "$1" in
            -h|--help) usage; exit 0 ;;
            -v|--verbose) VERBOSE=true ;;
            -q|--quiet) QUIET=true ;;
            --check-only) CHECK_ONLY=true ;;
            -*) log_warn "Unknown option: $1" ;;
            *) PROJECT_DIR="$1" ;;
        esac
        shift
    done
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
# Check: New/Modified Test Files Exist
# ---------------------------------------------------------------------------
check_test_files() {
    log_step "Checking for test files..."

    local dir="$PROJECT_DIR"
    local project_type
    project_type=$(detect_project_type "$dir")

    # Check for recently added/modified test files
    local new_tests=""
    new_tests=$(cd "$dir" && git diff --name-only HEAD 2>/dev/null | grep -iE "test_|_test\.|\.test\.|\.spec\.|tests/" || true)

    # Also check staged files
    local staged_tests=""
    staged_tests=$(cd "$dir" && git diff --cached --name-only 2>/dev/null | grep -iE "test_|_test\.|\.test\.|\.spec\.|tests/" || true)

    # Also check unstaged (new files)
    local untracked_tests=""
    untracked_tests=$(cd "$dir" && git ls-files --others --exclude-standard 2>/dev/null | grep -iE "test_|_test\.|\.test\.|\.spec\.|tests/" || true)

    local all_tests=""
    if [ -n "$new_tests" ]; then
        all_tests="${all_tests}${new_tests}"$'\n'
    fi
    if [ -n "$staged_tests" ]; then
        all_tests="${all_tests}${staged_tests}"$'\n'
    fi
    if [ -n "$untracked_tests" ]; then
        all_tests="${all_tests}${untracked_tests}"$'\n'
    fi

    # Deduplicate
    all_tests=$(echo "$all_tests" | sort -u | grep -v '^$' || true)

    if [ -n "$all_tests" ]; then
        local count
        count=$(echo "$all_tests" | wc -l | tr -d '[:space:]')
        record_pass "Found ${count} new/modified test file(s)"
        if [ "$VERBOSE" = true ]; then
            echo "$all_tests" | while IFS= read -r f; do
                [ -n "$f" ] && log_info "  ${f}"
            done
        fi
    else
        record_fail "No new or modified test files found — write your test first!"
        log_info "TDD requires writing a failing test BEFORE implementation code"
        log_info "Test file patterns: test_*.py, *.test.ts, *_test.go, *_test.rs"
    fi
}

# ---------------------------------------------------------------------------
# Check: Run Tests and Verify RED Phase
# ---------------------------------------------------------------------------
check_red_phase() {
    if [ "$CHECK_ONLY" = true ]; then
        log_info "Skipping test execution (--check-only)"
        return
    fi

    log_step "Verifying RED phase (at least one test must fail)..."

    local dir="$PROJECT_DIR"
    local project_type
    project_type=$(detect_project_type "$dir")

    local test_output=""
    local test_exit=0

    case "$project_type" in
        python)
            test_output=$(cd "$dir" && python -m pytest -v --tb=short 2>&1) || test_exit=$?
            ;;
        node)
            test_output=$(cd "$dir" && npm test 2>&1) || test_exit=$?
            ;;
        rust)
            test_output=$(cd "$dir" && cargo test 2>&1) || test_exit=$?
            ;;
        go)
            test_output=$(cd "$dir" && go test -v ./... 2>&1) || test_exit=$?
            ;;
        *)
            record_warn "Unknown project type — cannot run tests automatically"
            log_info "Manually verify that your new test fails before implementing"
            return
            ;;
    esac

    if [ "$test_exit" -ne 0 ]; then
        # Tests failed — this is what we WANT in RED phase
        record_pass "RED phase confirmed: tests fail (exit code ${test_exit})"

        # Check for correct failure type (not import/syntax errors)
        local wrong_failures=false

        case "$project_type" in
            python)
                if echo "$test_output" | grep -qE "ImportError|SyntaxError|ModuleNotFoundError|FileNotFoundError"; then
                    if ! echo "$test_output" | grep -qE "AssertionError|AssertError|TypeError|AttributeError|ValueError|FAILED"; then
                        wrong_failures=true
                    fi
                fi
                ;;
            node)
                if echo "$test_output" | grep -qE "Cannot find module|SyntaxError|ReferenceError"; then
                    if ! echo "$test_output" | grep -qE "AssertionError|expect\(.*\)\.|FAIL"; then
                        wrong_failures=true
                    fi
                fi
                ;;
        esac

        if [ "$wrong_failures" = true ]; then
            record_warn "Tests fail but possibly for wrong reasons (import/syntax errors)"
            log_info "Ensure tests fail because of MISSING IMPLEMENTATION, not infrastructure issues"
        else
            record_pass "Failure type looks correct (assertion/behavior failure)"
        fi

        # Show failure summary
        if [ "$VERBOSE" = true ]; then
            log_info "Test output (last 20 lines):"
            echo "$test_output" | tail -20 | while IFS= read -r line; do
                printf "  %s\n" "$line"
            done
        fi
    else
        # Tests pass — this means RED phase is NOT confirmed
        record_fail "All tests PASS — you need at least one FAILING test before implementation"
        log_info "TDD RED phase: Write a test that describes expected behavior"
        log_info "The test must FAIL before you write implementation code"

        # Count test results for context
        case "$project_type" in
            python)
                local passed
                passed=$(echo "$test_output" | grep -oE "[0-9]+ passed" | head -1 || true)
                if [ -n "$passed" ]; then
                    log_info "Current test results: ${passed}"
                fi
                ;;
        esac
    fi
}

# ---------------------------------------------------------------------------
# Check: No Implementation Without Test
# ---------------------------------------------------------------------------
check_implementation_guard() {
    log_step "Checking for premature implementation code..."

    local dir="$PROJECT_DIR"

    # Get changed non-test files
    local impl_files=""
    impl_files=$(cd "$dir" && git diff --name-only HEAD 2>/dev/null | grep -viE "test_|_test\.|\.test\.|\.spec\.|tests/|__pycache__" || true)

    local staged_impl=""
    staged_impl=$(cd "$dir" && git diff --cached --name-only 2>/dev/null | grep -viE "test_|_test\.|\.test\.|\.spec\.|tests/|__pycache__" || true)

    if [ -n "$impl_files" ] || [ -n "$staged_impl" ]; then
        # Check if test files also exist
        local has_tests=false
        local test_files=""
        test_files=$(cd "$dir" && git diff --name-only HEAD 2>/dev/null | grep -iE "test_|_test\.|\.test\.|\.spec\." || true)
        local staged_test_files=""
        staged_test_files=$(cd "$dir" && git diff --cached --name-only 2>/dev/null | grep -iE "test_|_test\.|\.test\.|\.spec\." || true)

        if [ -n "$test_files" ] || [ -n "$staged_test_files" ]; then
            has_tests=true
        fi

        if [ "$has_tests" = true ]; then
            record_pass "Implementation files changed alongside test files"
        else
            record_warn "Implementation files changed but no test files modified"
            log_info "Remember: write the test FIRST, see it fail, then implement"
        fi
    else
        record_pass "No implementation code changes detected (test-first is on track)"
    fi
}

# ---------------------------------------------------------------------------
# Main Checks
# ---------------------------------------------------------------------------
run_checks() {
    local project_type
    project_type=$(detect_project_type "$PROJECT_DIR")

    log_step "TDD Protocol — Gate Check"
    log_info "Project directory: ${PROJECT_DIR}"
    log_info "Detected project type: ${project_type}"
    echo ""

    check_test_files
    echo ""
    check_red_phase
    echo ""
    check_implementation_guard
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
}

determine_exit_code() {
    if [ "$FAIL_COUNT" -gt 0 ]; then
        log_fail "Overall: TDD GATE BLOCKED — write a failing test first"
        return 1
    elif [ "$WARN_COUNT" -gt 0 ]; then
        log_warn "Overall: TDD GATE PASSED WITH WARNINGS"
        return 2
    else
        log_pass "Overall: TDD GATE PASSED — RED phase confirmed"
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
