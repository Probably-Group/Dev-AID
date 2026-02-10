#!/usr/bin/env bash
# ============================================================================
# Dev-AID Process Skill: Staged Review — Security Checks Runner
# ============================================================================
# Runs gitleaks (if available) for secret scanning and shellcheck on any
# .sh files in staged changes. Aggregates results with pass/fail/warn.
#
# Exit codes:
#   0 = PASS  — All security checks passed
#   1 = FAIL  — Secrets detected or critical issues found
#   2 = WARN  — Checks passed with warnings
#
# Usage:
#   ./run-security-checks.sh [OPTIONS] [PROJECT_DIR]
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
SCRIPT_DESC="Run gitleaks and shellcheck on staged changes"

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
    -h, --help          Show this help message
    -v, --verbose       Enable verbose output
    -q, --quiet         Suppress non-error output
    --staged-only       Only check staged (git add) files
    --all               Check all files, not just staged

${BOLD}ARGUMENTS:${RESET}
    PROJECT_DIR     Path to project root (defaults to current directory)

${BOLD}EXIT CODES:${RESET}
    0   All security checks passed
    1   Secrets detected or critical issues found
    2   Checks passed with warnings

${BOLD}EXAMPLES:${RESET}
    ${SCRIPT_NAME}                  # Check current directory
    ${SCRIPT_NAME} --staged-only    # Only check staged files
    ${SCRIPT_NAME} --verbose        # Verbose output
EOF
}

# ---------------------------------------------------------------------------
# Argument Parsing
# ---------------------------------------------------------------------------
VERBOSE=false
QUIET=false
STAGED_ONLY=false
CHECK_ALL=false
PROJECT_DIR="."

parse_args() {
    while [ $# -gt 0 ]; do
        case "$1" in
            -h|--help) usage; exit 0 ;;
            -v|--verbose) VERBOSE=true ;;
            -q|--quiet) QUIET=true ;;
            --staged-only) STAGED_ONLY=true ;;
            --all) CHECK_ALL=true ;;
            -*) log_warn "Unknown option: $1" ;;
            *) PROJECT_DIR="$1" ;;
        esac
        shift
    done
}

# ---------------------------------------------------------------------------
# Check: Gitleaks Secret Scanning
# ---------------------------------------------------------------------------
run_gitleaks() {
    log_step "Secret scanning (gitleaks)..."

    if ! command -v gitleaks >/dev/null 2>&1; then
        record_warn "gitleaks not installed — skipping secret scanning"
        log_info "Install: brew install gitleaks (macOS) or see https://github.com/gitleaks/gitleaks"
        return
    fi

    local gitleaks_output
    local gitleaks_exit=0

    if [ "$STAGED_ONLY" = true ]; then
        gitleaks_output=$(cd "$PROJECT_DIR" && gitleaks detect --staged --no-banner 2>&1) || gitleaks_exit=$?
    else
        gitleaks_output=$(cd "$PROJECT_DIR" && gitleaks detect --source . --no-git --no-banner 2>&1) || gitleaks_exit=$?
    fi

    if [ "$gitleaks_exit" -eq 0 ]; then
        record_pass "No secrets detected by gitleaks"
    else
        record_fail "Gitleaks found potential secrets!"
        if [ -n "$gitleaks_output" ]; then
            printf "  %s\n" "$gitleaks_output" | head -30
        fi
    fi
}

# ---------------------------------------------------------------------------
# Check: Shellcheck on Shell Scripts
# ---------------------------------------------------------------------------
run_shellcheck() {
    log_step "Shell script analysis (shellcheck)..."

    if ! command -v shellcheck >/dev/null 2>&1; then
        record_warn "shellcheck not installed — skipping shell analysis"
        log_info "Install: brew install shellcheck (macOS) or apt install shellcheck (Linux)"
        return
    fi

    # Find shell scripts to check
    local shell_files=()

    if [ "$STAGED_ONLY" = true ]; then
        # Get staged .sh files
        while IFS= read -r file; do
            if [ -n "$file" ] && [ -f "${PROJECT_DIR}/${file}" ]; then
                shell_files+=("${PROJECT_DIR}/${file}")
            fi
        done < <(cd "$PROJECT_DIR" && git diff --cached --name-only --diff-filter=ACMR 2>/dev/null | grep '\.sh$' || true)
    elif [ "$CHECK_ALL" = true ]; then
        # Find all .sh files
        while IFS= read -r file; do
            if [ -n "$file" ]; then
                shell_files+=("$file")
            fi
        done < <(find "$PROJECT_DIR" -name "*.sh" -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/venv/*" -not -path "*/.worktrees/*" 2>/dev/null || true)
    else
        # Get recently changed .sh files
        while IFS= read -r file; do
            if [ -n "$file" ] && [ -f "${PROJECT_DIR}/${file}" ]; then
                shell_files+=("${PROJECT_DIR}/${file}")
            fi
        done < <(cd "$PROJECT_DIR" && git diff --name-only HEAD~5..HEAD 2>/dev/null | grep '\.sh$' || true)
    fi

    if [ ${#shell_files[@]} -eq 0 ]; then
        log_info "No shell scripts found to check"
        record_pass "Shellcheck: no scripts to check"
        return
    fi

    log_info "Checking ${#shell_files[@]} shell script(s)..."

    local total_errors=0
    local total_warnings=0

    for script in "${shell_files[@]}"; do
        local sc_output
        local sc_exit=0
        sc_output=$(shellcheck -f gcc "$script" 2>&1) || sc_exit=$?

        if [ "$sc_exit" -eq 0 ]; then
            if [ "$VERBOSE" = true ]; then
                log_info "  Clean: ${script}"
            fi
        else
            local errors
            local warnings
            errors=$(echo "$sc_output" | grep -c ":error:" || true)
            warnings=$(echo "$sc_output" | grep -c ":warning:" || true)
            total_errors=$((total_errors + errors))
            total_warnings=$((total_warnings + warnings))

            if [ "$errors" -gt 0 ]; then
                log_fail "  ${script}: ${errors} error(s), ${warnings} warning(s)"
            else
                log_warn "  ${script}: ${warnings} warning(s)"
            fi

            if [ "$VERBOSE" = true ] && [ -n "$sc_output" ]; then
                printf "    %s\n" "$sc_output" | head -15
            fi
        fi
    done

    if [ "$total_errors" -gt 0 ]; then
        record_fail "Shellcheck: ${total_errors} error(s) in ${#shell_files[@]} script(s)"
    elif [ "$total_warnings" -gt 0 ]; then
        record_warn "Shellcheck: ${total_warnings} warning(s) in ${#shell_files[@]} script(s)"
    else
        record_pass "Shellcheck: all ${#shell_files[@]} script(s) clean"
    fi
}

# ---------------------------------------------------------------------------
# Check: Common Security Patterns
# ---------------------------------------------------------------------------
check_common_patterns() {
    log_step "Common security pattern checks..."

    local files_to_check=""

    if [ "$STAGED_ONLY" = true ]; then
        files_to_check=$(cd "$PROJECT_DIR" && git diff --cached --name-only --diff-filter=ACMR 2>/dev/null || true)
    else
        files_to_check=$(cd "$PROJECT_DIR" && git diff --name-only HEAD~5..HEAD 2>/dev/null || true)
    fi

    if [ -z "$files_to_check" ]; then
        log_info "No changed files to check for security patterns"
        return
    fi

    # Check for hardcoded credentials patterns
    local cred_hits=0
    while IFS= read -r file; do
        if [ -n "$file" ] && [ -f "${PROJECT_DIR}/${file}" ]; then
            local matches
            matches=$(grep -nE "(password|secret|api_key|apikey|token|credential)\s*=\s*['\"][^'\"]+['\"]" "${PROJECT_DIR}/${file}" 2>/dev/null | grep -vi "test\|mock\|fake\|example\|placeholder\|_ENV\|environ\|getenv\|os\." || true)
            if [ -n "$matches" ]; then
                cred_hits=$((cred_hits + 1))
                if [ "$VERBOSE" = true ]; then
                    log_warn "  Potential hardcoded credential in: ${file}"
                    printf "    %s\n" "$matches" | head -5
                fi
            fi
        fi
    done <<< "$files_to_check"

    if [ "$cred_hits" -gt 0 ]; then
        record_warn "Found ${cred_hits} file(s) with potential hardcoded credentials"
    else
        record_pass "No hardcoded credential patterns detected"
    fi

    # Check for .env files being committed
    local env_files
    env_files=$(echo "$files_to_check" | grep -E "^\.env$|\.env\.local$|\.env\.prod" || true)
    if [ -n "$env_files" ]; then
        record_fail "Environment file(s) in changes: ${env_files}"
    else
        record_pass "No .env files in changes"
    fi
}

# ---------------------------------------------------------------------------
# Main Checks
# ---------------------------------------------------------------------------
run_checks() {
    log_step "Staged Review — Security Checks"
    log_info "Project directory: ${PROJECT_DIR}"
    if [ "$STAGED_ONLY" = true ]; then
        log_info "Mode: staged files only"
    elif [ "$CHECK_ALL" = true ]; then
        log_info "Mode: all files"
    else
        log_info "Mode: recently changed files"
    fi
    echo ""

    run_gitleaks
    echo ""
    run_shellcheck
    echo ""
    check_common_patterns
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
        log_fail "Overall: FAILED — security issues found"
        return 1
    elif [ "$WARN_COUNT" -gt 0 ]; then
        log_warn "Overall: PASSED WITH WARNINGS — review security warnings"
        return 2
    else
        log_pass "Overall: ALL SECURITY CHECKS PASSED"
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
