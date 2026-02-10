#!/usr/bin/env bash
# ============================================================================
# Dev-AID Process Skill: Systematic Debugging — Debugging State Checker
# ============================================================================
# Validates that debugging follows the systematic protocol: hypothesis
# documented, reproduction steps exist, and 3-strike counter is tracked.
#
# Exit codes:
#   0 = PASS  — All debugging state checks passed
#   1 = FAIL  — Missing required debugging artifacts
#   2 = WARN  — Partial compliance
#
# Usage:
#   ./check-debugging-state.sh [OPTIONS] [PROJECT_DIR]
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
SCRIPT_DESC="Validate hypothesis doc, reproduction steps, and 3-strike counter"

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

${BOLD}ARGUMENTS:${RESET}
    PROJECT_DIR     Path to project root (defaults to current directory)

${BOLD}EXIT CODES:${RESET}
    0   All debugging state checks passed
    1   Missing required debugging artifacts
    2   Partial compliance (warnings)

${BOLD}EXAMPLES:${RESET}
    ${SCRIPT_NAME}                  # Check current directory
    ${SCRIPT_NAME} --verbose        # Verbose output
EOF
}

# ---------------------------------------------------------------------------
# Argument Parsing
# ---------------------------------------------------------------------------
VERBOSE=false
QUIET=false
PROJECT_DIR="."

parse_args() {
    while [ $# -gt 0 ]; do
        case "$1" in
            -h|--help) usage; exit 0 ;;
            -v|--verbose) VERBOSE=true ;;
            -q|--quiet) QUIET=true ;;
            -*) log_warn "Unknown option: $1" ;;
            *) PROJECT_DIR="$1" ;;
        esac
        shift
    done
}

# ---------------------------------------------------------------------------
# Check: Hypothesis Documentation
# ---------------------------------------------------------------------------
check_hypothesis_doc() {
    log_step "Checking for hypothesis documentation..."

    local dir="$PROJECT_DIR"
    local found=false

    # Check for common hypothesis/debugging doc patterns
    local hypothesis_files=(
        "HYPOTHESIS.md"
        "hypothesis.md"
        "DEBUGGING.md"
        "debugging.md"
        "debugging-notes.md"
        "debug-notes.md"
        "investigation.md"
        "INVESTIGATION.md"
        ".debug/hypothesis.md"
        ".dev-aid/debugging/hypothesis.md"
    )

    for f in "${hypothesis_files[@]}"; do
        if [ -f "${dir}/${f}" ]; then
            found=true
            if [ "$VERBOSE" = true ]; then
                log_info "Found hypothesis doc: ${f}"
            fi

            # Check for hypothesis content pattern
            if grep -qi "hypothesis\|root.cause\|theory\|suspect\|believe.*because" "${dir}/${f}" 2>/dev/null; then
                record_pass "Hypothesis doc exists with hypothesis content: ${f}"
            else
                record_warn "Hypothesis doc exists but lacks hypothesis statement: ${f}"
            fi
            break
        fi
    done

    # Also check git log for hypothesis mentions in recent commits
    if [ "$found" = false ]; then
        local git_hypothesis
        git_hypothesis=$(cd "$dir" && git log --oneline -20 --grep="hypothesis\|root.cause\|debug\|investigate" 2>/dev/null | head -5) || true

        if [ -n "$git_hypothesis" ]; then
            found=true
            record_warn "No hypothesis doc file, but git log contains debugging commits"
            if [ "$VERBOSE" = true ]; then
                printf "  Recent debugging commits:\n"
                printf "  %s\n" "$git_hypothesis"
            fi
        fi
    fi

    # Check for inline debugging comments in recently changed files
    if [ "$found" = false ]; then
        local inline_debug
        inline_debug=$(cd "$dir" && git diff HEAD~3..HEAD 2>/dev/null | grep -i "TODO.*debug\|FIXME.*debug\|hypothesis\|root.cause" | head -5) || true

        if [ -n "$inline_debug" ]; then
            found=true
            record_warn "No dedicated hypothesis doc, but found inline debugging comments"
        fi
    fi

    if [ "$found" = false ]; then
        record_fail "No hypothesis documentation found — document your hypothesis before fixing"
    fi
}

# ---------------------------------------------------------------------------
# Check: Reproduction Steps
# ---------------------------------------------------------------------------
check_reproduction_steps() {
    log_step "Checking for reproduction steps..."

    local dir="$PROJECT_DIR"
    local found=false

    # Check hypothesis/debugging files for reproduction steps
    local doc_files=(
        "HYPOTHESIS.md"
        "hypothesis.md"
        "DEBUGGING.md"
        "debugging.md"
        "debugging-notes.md"
        "debug-notes.md"
        "investigation.md"
        "INVESTIGATION.md"
        "REPRODUCE.md"
        "reproduce.md"
        "BUG.md"
    )

    for f in "${doc_files[@]}"; do
        if [ -f "${dir}/${f}" ]; then
            if grep -qi "repro\|steps to\|how to trigger\|to reproduce\|reproduction" "${dir}/${f}" 2>/dev/null; then
                found=true
                record_pass "Reproduction steps documented in: ${f}"
                break
            fi
        fi
    done

    # Check for test files that act as reproduction
    if [ "$found" = false ]; then
        local repro_tests
        repro_tests=$(cd "$dir" && git diff --name-only HEAD~3..HEAD 2>/dev/null | grep -i "test.*repro\|repro.*test\|test.*bug\|test.*regression" | head -3) || true

        if [ -n "$repro_tests" ]; then
            found=true
            record_pass "Reproduction captured in test file(s): ${repro_tests}"
        fi
    fi

    # Check recent git diff for test additions
    if [ "$found" = false ]; then
        local new_tests
        new_tests=$(cd "$dir" && git diff HEAD~3..HEAD --name-only 2>/dev/null | grep -E "test_|_test\.|\.test\.|\.spec\." | head -3) || true

        if [ -n "$new_tests" ]; then
            found=true
            record_warn "New test files found (may serve as reproduction): ${new_tests}"
        fi
    fi

    if [ "$found" = false ]; then
        record_fail "No reproduction steps found — document how to reproduce the issue"
    fi
}

# ---------------------------------------------------------------------------
# Check: 3-Strike Counter
# ---------------------------------------------------------------------------
check_strike_counter() {
    log_step "Checking 3-strike counter..."

    local dir="$PROJECT_DIR"

    # Count fix attempts in recent git history
    local fix_attempts
    fix_attempts=$(cd "$dir" && git log --oneline -30 2>/dev/null | grep -ic "fix\|attempt\|try\|retry\|revert" || true)

    # Count reverts specifically
    local revert_count
    revert_count=$(cd "$dir" && git log --oneline -30 2>/dev/null | grep -ic "revert\|undo\|rollback" || true)

    # Check for strike patterns in notes/docs
    local strike_doc=false
    local doc_files=("HYPOTHESIS.md" "hypothesis.md" "DEBUGGING.md" "debugging.md" "debugging-notes.md")
    for f in "${doc_files[@]}"; do
        if [ -f "${dir}/${f}" ]; then
            if grep -qi "strike\|attempt.*[0-9]\|try.*[0-9]\|failed.*attempt" "${dir}/${f}" 2>/dev/null; then
                strike_doc=true
                break
            fi
        fi
    done

    if [ "$VERBOSE" = true ]; then
        log_info "Fix-related commits in last 30: ${fix_attempts}"
        log_info "Revert commits in last 30: ${revert_count}"
    fi

    if [ "$fix_attempts" -ge 3 ] && [ "$strike_doc" = false ]; then
        record_warn "3+ fix attempts detected (${fix_attempts}) but no strike tracking documented"
        log_info "Consider: Are you fixing the symptom instead of the root cause?"
    elif [ "$fix_attempts" -ge 3 ] && [ "$strike_doc" = true ]; then
        record_pass "3+ fix attempts with strike tracking documented"
    elif [ "$revert_count" -ge 2 ]; then
        record_warn "Multiple reverts detected (${revert_count}) — re-examine your approach"
    else
        record_pass "Fix attempts within acceptable range (${fix_attempts} in last 30 commits)"
    fi

    # Hard fail on excessive attempts without progress
    if [ "$fix_attempts" -ge 6 ]; then
        record_fail "6+ fix attempts detected — STOP and request architectural review"
    fi
}

# ---------------------------------------------------------------------------
# Main Checks
# ---------------------------------------------------------------------------
run_checks() {
    log_step "Systematic Debugging — State Validation"
    log_info "Project directory: ${PROJECT_DIR}"
    echo ""

    check_hypothesis_doc
    echo ""
    check_reproduction_steps
    echo ""
    check_strike_counter
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
        log_fail "Overall: FAILED — debugging state incomplete"
        return 1
    elif [ "$WARN_COUNT" -gt 0 ]; then
        log_warn "Overall: PASSED WITH WARNINGS — improve debugging documentation"
        return 2
    else
        log_pass "Overall: ALL CHECKS PASSED — debugging state is well-documented"
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
