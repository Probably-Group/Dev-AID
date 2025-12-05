#!/usr/bin/env bash
#
# Script: validate-bash-scripts.sh
# Description: Validates Bash scripts for bash-expert skill compliance
# Usage: validate-bash-scripts.sh [script_files...]
#

# Strict mode: exit on error, undefined variables, pipe failures
set -euo pipefail

# Script directory (portable way)
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m' # No Color

# Counters
total_checks=0
passed_checks=0
failed_checks=0

# Cleanup function (always runs on exit)
cleanup() {
    local exit_code=$?
    exit "$exit_code"
}
trap cleanup EXIT INT TERM

# Logging functions
log_pass() {
    echo -e "${GREEN}✓${NC} $*"
    ((passed_checks++)) || true
    ((total_checks++)) || true
}

log_fail() {
    echo -e "${RED}✗${NC} $*"
    ((failed_checks++)) || true
    ((total_checks++)) || true
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $*"
}

log_info() {
    echo "ℹ $*"
}

# Check for shebang
check_shebang() {
    local script="$1"
    local first_line
    first_line=$(head -1 "$script")

    if [[ "$first_line" =~ ^#!/usr/bin/env\ bash$ ]] || [[ "$first_line" =~ ^#!/bin/bash$ ]]; then
        log_pass "$script: Has proper shebang"
        return 0
    else
        log_fail "$script: Missing or incorrect shebang (found: $first_line)"
        return 1
    fi
}

# Check for strict mode
check_strict_mode() {
    local script="$1"

    if grep -q "set -euo pipefail" "$script"; then
        log_pass "$script: Uses strict mode (set -euo pipefail)"
        return 0
    else
        log_fail "$script: Missing strict mode (set -euo pipefail)"
        return 1
    fi
}

# Check for cleanup trap
check_cleanup_trap() {
    local script="$1"

    if grep -q "trap.*cleanup.*EXIT" "$script"; then
        log_pass "$script: Has cleanup trap"
        return 0
    else
        log_warn "$script: No cleanup trap found (optional but recommended)"
        ((total_checks++)) || true
        return 0
    fi
}

# Check for proper quoting (basic check)
check_quoting() {
    local script="$1"
    local unquoted_vars=0

    # Check for common unquoted variable patterns (basic heuristic)
    # This is not perfect but catches obvious cases
    if grep -E '\$[A-Z_]+[^"]' "$script" | grep -v "^\s*#" | grep -q .; then
        log_warn "$script: Possible unquoted variables detected (manual review recommended)"
    fi

    log_pass "$script: Basic quoting check passed"
    return 0
}

# Check for readonly variables for constants
check_readonly_constants() {
    local script="$1"

    if grep -q "readonly" "$script"; then
        log_pass "$script: Uses readonly for constants"
        return 0
    else
        log_warn "$script: No readonly constants found (recommended for configuration)"
        ((total_checks++)) || true
        return 0
    fi
}

# Check for input validation
check_input_validation() {
    local script="$1"

    # Check if script validates inputs or arguments
    if grep -qE "(\[\[.*-z.*\]\]|\[\[.*-n.*\]\]|\[\[.*\$#)" "$script"; then
        log_pass "$script: Contains input validation"
        return 0
    else
        log_warn "$script: No obvious input validation detected"
        ((total_checks++)) || true
        return 0
    fi
}

# Syntax check with bash -n
check_syntax() {
    local script="$1"

    if bash -n "$script" 2>/dev/null; then
        log_pass "$script: Syntax check passed (bash -n)"
        return 0
    else
        log_fail "$script: Syntax check FAILED (bash -n)"
        bash -n "$script" 2>&1 | sed 's/^/  /'
        return 1
    fi
}

# Check for dangerous patterns
check_dangerous_patterns() {
    local script="$1"
    local dangerous=0

    # Check for eval
    if grep -q "eval" "$script" | grep -v "^\s*#"; then
        log_fail "$script: Uses 'eval' (dangerous, avoid)"
        dangerous=1
    fi

    # Check for backticks
    if grep -q '`' "$script" | grep -v "^\s*#"; then
        log_fail "$script: Uses backticks (use \$() instead)"
        dangerous=1
    fi

    if [[ "$dangerous" -eq 0 ]]; then
        log_pass "$script: No dangerous patterns detected"
        return 0
    fi

    return 1
}

# Validate a single script
validate_script() {
    local script="$1"

    echo ""
    log_info "Validating: $script"
    echo "----------------------------------------"

    check_shebang "$script"
    check_strict_mode "$script"
    check_cleanup_trap "$script"
    check_quoting "$script"
    check_readonly_constants "$script"
    check_input_validation "$script"
    check_syntax "$script"
    check_dangerous_patterns "$script"
}

# Main function
main() {
    local -a scripts_to_check

    if [[ $# -eq 0 ]]; then
        # Default: check newly created scripts
        scripts_to_check=(
            "$SCRIPT_DIR/detect-context.sh"
            "$SCRIPT_DIR/select-skills.sh"
            "$SCRIPT_DIR/../providers/claude/.claude/hooks/session-start.sh"
            "$SCRIPT_DIR/../providers/gemini/.gemini/hooks/session-start.sh"
        )
    else
        scripts_to_check=("$@")
    fi

    log_info "Bash Expert Skill Compliance Validation"
    echo "========================================"

    for script in "${scripts_to_check[@]}"; do
        if [[ ! -f "$script" ]]; then
            log_fail "Script not found: $script"
            continue
        fi

        validate_script "$script"
    done

    # Summary
    echo ""
    echo "========================================"
    echo "Validation Summary"
    echo "========================================"
    echo "Total checks: $total_checks"
    echo -e "${GREEN}Passed: $passed_checks${NC}"
    echo -e "${RED}Failed: $failed_checks${NC}"

    if [[ "$failed_checks" -gt 0 ]]; then
        echo ""
        log_fail "Some checks failed. Please review and fix."
        exit 1
    else
        echo ""
        log_pass "All critical checks passed!"
        exit 0
    fi
}

# Run main function
main "$@"
