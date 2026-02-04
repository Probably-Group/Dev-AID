#!/usr/bin/env bash
#
# Script: tdd-gate-check.sh
# Description: TDD Enforcement Gate - checks for test-first compliance
# Usage: Called before code generation to enforce TDD protocol
#
# Exit codes:
#   0 - Gate passed (test exists and failed, or gate bypassed)
#   1 - Gate blocked (strict mode, no failing test)
#   2 - Gate warning (warning mode, no test but allowed)
#

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[0;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

# Logging
log_info() { echo -e "${BLUE}[tdd-gate]${NC} $*"; }
log_pass() { echo -e "${GREEN}[tdd-gate]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[tdd-gate]${NC} $*"; }
log_block() { echo -e "${RED}[tdd-gate]${NC} $*"; }

# Find project root
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

# Get TDD enforcement level from config
get_enforcement_level() {
    local project_root="$1"
    local config_file="$project_root/.dev-aid/config/process-skills.json"

    if [[ ! -f "$config_file" ]]; then
        echo "warning"
        return
    fi

    if command -v jq &>/dev/null; then
        local level
        level=$(jq -r '.enforcement["tdd-protocol"].level // "warning"' "$config_file" 2>/dev/null || echo "warning")
        echo "$level"
    else
        echo "warning"
    fi
}

# Check if target file has associated tests
find_related_tests() {
    local project_root="$1"
    local target_file="$2"

    # Extract base name without extension
    local base_name
    base_name=$(basename "$target_file" | sed 's/\.[^.]*$//')

    # Common test patterns
    local patterns=(
        "**/test*${base_name}*"
        "**/${base_name}*test*"
        "**/${base_name}*spec*"
        "**/__tests__/${base_name}*"
        "**/tests/${base_name}*"
        "**/${base_name}.test.*"
        "**/${base_name}.spec.*"
        "**/${base_name}_test.*"
        "**/test_${base_name}.*"
    )

    local found_tests=()
    for pattern in "${patterns[@]}"; do
        while IFS= read -r -d '' test_file; do
            found_tests+=("$test_file")
        done < <(find "$project_root" -path "*node_modules*" -prune -o -path "*.git*" -prune -o -type f -name "$pattern" -print0 2>/dev/null || true)
    done

    printf '%s\n' "${found_tests[@]}" | sort -u
}

# Check if tests were recently run and failed
check_recent_test_failure() {
    local project_root="$1"

    # Check common test output locations
    local indicators=(
        "$project_root/.test-results"
        "$project_root/test-results.json"
        "$project_root/coverage"
        "$project_root/.pytest_cache"
        "$project_root/.jest-cache"
    )

    for indicator in "${indicators[@]}"; do
        if [[ -e "$indicator" ]]; then
            # Check if modified in last 5 minutes
            local age
            if [[ "$(uname)" == "Darwin" ]]; then
                age=$(( $(date +%s) - $(stat -f %m "$indicator" 2>/dev/null || echo 0) ))
            else
                age=$(( $(date +%s) - $(stat -c %Y "$indicator" 2>/dev/null || echo 0) ))
            fi

            if (( age < 300 )); then
                return 0  # Recent test activity
            fi
        fi
    done

    return 1  # No recent test activity
}

# Main gate check
main() {
    local target_file="${1:-}"
    local bypass_reason="${2:-}"

    local project_root
    project_root=$(find_project_root "$(pwd)")

    local level
    level=$(get_enforcement_level "$project_root")

    # Check for bypass
    if [[ -n "$bypass_reason" ]]; then
        log_pass "Gate bypassed: $bypass_reason"
        exit 0
    fi

    # If level is off, skip check
    if [[ "$level" == "off" ]]; then
        exit 0
    fi

    echo ""
    log_info "Checking TDD compliance (level: $level)"

    # If no target file specified, give general reminder
    if [[ -z "$target_file" ]]; then
        if [[ "$level" == "strict" ]]; then
            echo ""
            log_block "TDD GATE: Strict mode active"
            echo ""
            echo "  Before writing production code:"
            echo "  1. Write a test that describes the expected behavior"
            echo "  2. Run the test and verify it FAILS"
            echo "  3. Only then write code to make it pass"
            echo ""
            echo "  To bypass: Specify bypass reason (e.g., 'refactoring only')"
            echo ""
            exit 1
        else
            echo ""
            log_warn "TDD Reminder: Consider writing a test first"
            echo ""
            exit 2
        fi
    fi

    # Check for related tests
    local related_tests
    related_tests=$(find_related_tests "$project_root" "$target_file")

    if [[ -n "$related_tests" ]]; then
        log_info "Found related test files:"
        echo "$related_tests" | head -5 | while read -r test; do
            echo "  - $test"
        done

        if check_recent_test_failure "$project_root"; then
            log_pass "Recent test activity detected - proceeding"
            exit 0
        else
            if [[ "$level" == "strict" ]]; then
                echo ""
                log_block "TDD GATE: Run tests before proceeding"
                echo ""
                echo "  Test files exist but haven't been run recently."
                echo "  Please run: npm test / pytest / cargo test"
                echo ""
                exit 1
            else
                log_warn "Tests exist but weren't run recently"
                exit 2
            fi
        fi
    else
        if [[ "$level" == "strict" ]]; then
            echo ""
            log_block "TDD GATE: No test found for $target_file"
            echo ""
            echo "  Write a failing test first, then implement."
            echo ""
            echo "  Suggested test location:"
            local dir
            dir=$(dirname "$target_file")
            local base
            base=$(basename "$target_file" | sed 's/\.[^.]*$//')
            echo "    $dir/__tests__/${base}.test.ts"
            echo "    $dir/${base}.test.ts"
            echo "    tests/test_${base}.py"
            echo ""
            exit 1
        else
            log_warn "No test found for $target_file - consider TDD"
            exit 2
        fi
    fi
}

# Show usage
usage() {
    echo "Usage: $0 [target_file] [bypass_reason]"
    echo ""
    echo "Arguments:"
    echo "  target_file    File being modified (optional)"
    echo "  bypass_reason  Reason to bypass gate (e.g., 'refactoring only')"
    echo ""
    echo "Exit codes:"
    echo "  0 - Gate passed"
    echo "  1 - Gate blocked (strict mode)"
    echo "  2 - Gate warning"
}

# Handle help flag
if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    usage
    exit 0
fi

main "$@"
