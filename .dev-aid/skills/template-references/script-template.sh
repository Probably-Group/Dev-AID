#!/usr/bin/env bash
# ============================================================================
# Dev-AID Process Skill Script Template
# ============================================================================
# Usage: Copy this template for new process skill scripts.
# All scripts should be POSIX-compliant and pass shellcheck.
#
# Exit codes:
#   0 = PASS  — All checks passed
#   1 = FAIL  — One or more checks failed
#   2 = WARN  — Checks passed with warnings
#
# Usage pattern:
#   ./script-name.sh [OPTIONS] [ARGUMENTS]
#
# shellcheck disable=SC2034  # Template variables may appear unused
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
# Script Metadata (customize per script)
# ---------------------------------------------------------------------------
SCRIPT_NAME="$(basename "$0")"
SCRIPT_VERSION="1.0.0"
SCRIPT_DESC="Description of what this script does"

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
    ${SCRIPT_NAME} [OPTIONS] [ARGUMENTS]

${BOLD}OPTIONS:${RESET}
    -h, --help      Show this help message
    -v, --verbose   Enable verbose output
    -q, --quiet     Suppress non-error output

${BOLD}EXIT CODES:${RESET}
    0   All checks passed
    1   One or more checks failed
    2   Checks passed with warnings

${BOLD}EXAMPLES:${RESET}
    ${SCRIPT_NAME}                  # Run with defaults
    ${SCRIPT_NAME} --verbose        # Run with verbose output
EOF
}

# ---------------------------------------------------------------------------
# Argument Parsing
# ---------------------------------------------------------------------------
VERBOSE=false
QUIET=false

parse_args() {
    while [ $# -gt 0 ]; do
        case "$1" in
            -h|--help) usage; exit 0 ;;
            -v|--verbose) VERBOSE=true ;;
            -q|--quiet) QUIET=true ;;
            *) log_warn "Unknown option: $1" ;;
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
# Main Check Functions (customize these)
# ---------------------------------------------------------------------------
run_checks() {
    log_step "Running checks..."

    # Example check 1
    # if some_condition; then
    #     record_pass "Check 1 passed"
    # else
    #     record_fail "Check 1 failed: reason"
    # fi

    # Example check 2 (warning)
    # if some_condition; then
    #     record_pass "Check 2 passed"
    # elif partial_condition; then
    #     record_warn "Check 2: partial compliance"
    # else
    #     record_fail "Check 2 failed: reason"
    # fi

    log_info "Replace these placeholder checks with actual validations"
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
        log_fail "Overall: FAILED"
        return 1
    elif [ "$WARN_COUNT" -gt 0 ]; then
        log_warn "Overall: PASSED WITH WARNINGS"
        return 2
    else
        log_pass "Overall: ALL CHECKS PASSED"
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
