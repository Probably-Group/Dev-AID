#!/usr/bin/env bash
# ============================================================================
# Dev-AID Process Skill: Plan Execution — Checkpoint Validator
# ============================================================================
# Validates checkpoint format (numbered, has description), verifies evidence
# files exist for completed checkpoints, and reports completion percentage.
#
# Exit codes:
#   0 = PASS  — All checkpoints valid
#   1 = FAIL  — Checkpoint validation failed
#   2 = WARN  — Partial issues found
#
# Usage:
#   ./checkpoint-validator.sh [OPTIONS] [PLAN_FILE]
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
SCRIPT_DESC="Validate checkpoint format, evidence, and completion percentage"

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
    ${SCRIPT_NAME} [OPTIONS] [PLAN_FILE]

${BOLD}OPTIONS:${RESET}
    -h, --help      Show this help message
    -v, --verbose   Enable verbose output
    -q, --quiet     Suppress non-error output

${BOLD}ARGUMENTS:${RESET}
    PLAN_FILE       Path to plan/checkpoint file (auto-detects if not specified)

${BOLD}EXIT CODES:${RESET}
    0   All checkpoints valid
    1   Checkpoint validation failed
    2   Partial issues found

${BOLD}EXPECTED CHECKPOINT FORMATS:${RESET}
    - [x] Task 1: Description         # Completed
    - [ ] Task 2: Description         # Pending
    1. [x] Step description            # Numbered, completed
    1. [ ] Step description            # Numbered, pending

${BOLD}EXAMPLES:${RESET}
    ${SCRIPT_NAME}                  # Auto-detect plan file
    ${SCRIPT_NAME} PLAN.md          # Validate specific plan
    ${SCRIPT_NAME} --verbose        # Verbose output
EOF
}

# ---------------------------------------------------------------------------
# Argument Parsing
# ---------------------------------------------------------------------------
VERBOSE=false
QUIET=false
PLAN_FILE=""

parse_args() {
    while [ $# -gt 0 ]; do
        case "$1" in
            -h|--help) usage; exit 0 ;;
            -v|--verbose) VERBOSE=true ;;
            -q|--quiet) QUIET=true ;;
            -*) log_warn "Unknown option: $1" ;;
            *) PLAN_FILE="$1" ;;
        esac
        shift
    done
}

# ---------------------------------------------------------------------------
# Auto-Detect Plan File
# ---------------------------------------------------------------------------
find_plan_file() {
    if [ -n "$PLAN_FILE" ] && [ -f "$PLAN_FILE" ]; then
        return 0
    fi

    local candidates=(
        "PLAN.md"
        "plan.md"
        "EXECUTION_PLAN.md"
        "execution-plan.md"
        "TASKS.md"
        "tasks.md"
        "TODO.md"
        "todo.md"
        "CHECKPOINT.md"
        "checkpoint.md"
        ".dev-aid/plan.md"
        "docs/plan.md"
    )

    for f in "${candidates[@]}"; do
        if [ -f "$f" ]; then
            PLAN_FILE="$f"
            log_info "Auto-detected plan file: ${f}"
            return 0
        fi
    done

    return 1
}

# ---------------------------------------------------------------------------
# Check: Checkpoint Format
# ---------------------------------------------------------------------------
check_checkpoint_format() {
    log_step "Checking checkpoint format..."

    # Count total checkpoints (both checked and unchecked)
    local total_checkpoints
    total_checkpoints=$(grep -cE "^[[:space:]]*(-|\*|[0-9]+\.)\s*\[(x|X| )\]" "$PLAN_FILE" 2>/dev/null || true)

    if [ "$total_checkpoints" -eq 0 ]; then
        record_fail "No checkpoints found — use '- [ ] Task' or '1. [ ] Step' format"
        return
    fi

    record_pass "Found ${total_checkpoints} checkpoint(s)"

    # Check if checkpoints have descriptions (not just empty brackets)
    local empty_checkpoints
    empty_checkpoints=$(grep -cE "^[[:space:]]*(-|\*|[0-9]+\.)\s*\[(x|X| )\]\s*$" "$PLAN_FILE" 2>/dev/null || true)

    if [ "$empty_checkpoints" -gt 0 ]; then
        record_fail "${empty_checkpoints} checkpoint(s) have no description"
    else
        record_pass "All checkpoints have descriptions"
    fi

    # Check for numbered format
    local numbered_checkpoints
    numbered_checkpoints=$(grep -cE "^[[:space:]]*[0-9]+\.\s*\[(x|X| )\]" "$PLAN_FILE" 2>/dev/null || true)

    if [ "$numbered_checkpoints" -gt 0 ]; then
        record_pass "Checkpoints use numbered format (${numbered_checkpoints} numbered)"

        # Verify sequential numbering
        local prev_num=0
        local seq_ok=true
        while IFS= read -r line; do
            local num
            num=$(echo "$line" | grep -oE "^[[:space:]]*[0-9]+" | tr -d '[:space:]')
            if [ -n "$num" ]; then
                if [ "$num" -le "$prev_num" ] && [ "$prev_num" -gt 0 ]; then
                    seq_ok=false
                fi
                prev_num="$num"
            fi
        done < <(grep -E "^[[:space:]]*[0-9]+\.\s*\[(x|X| )\]" "$PLAN_FILE" 2>/dev/null || true)

        if [ "$seq_ok" = true ]; then
            record_pass "Checkpoint numbering is sequential"
        else
            record_warn "Checkpoint numbering may not be sequential"
        fi
    else
        record_warn "Checkpoints use unnumbered format — consider numbering for clarity"
    fi
}

# ---------------------------------------------------------------------------
# Check: Evidence for Completed Checkpoints
# ---------------------------------------------------------------------------
check_evidence() {
    log_step "Checking evidence for completed checkpoints..."

    local completed_checkpoints
    completed_checkpoints=$(grep -cE "^[[:space:]]*(-|\*|[0-9]+\.)\s*\[(x|X)\]" "$PLAN_FILE" 2>/dev/null || true)

    if [ "$completed_checkpoints" -eq 0 ]; then
        log_info "No completed checkpoints yet"
        return
    fi

    log_info "${completed_checkpoints} completed checkpoint(s) found"

    # Check for evidence patterns near completed checkpoints
    local evidence_count=0
    local missing_evidence=0

    while IFS= read -r line; do
        # Get the line number of this completed checkpoint
        local line_num
        line_num=$(grep -nE "^[[:space:]]*(-|\*|[0-9]+\.)\s*\[(x|X)\]" "$PLAN_FILE" 2>/dev/null | grep -F "$line" | head -1 | cut -d: -f1)

        if [ -z "$line_num" ]; then
            continue
        fi

        # Check the next 3 lines for evidence patterns
        local has_evidence=false
        local context
        context=$(sed -n "$((line_num)),$((line_num + 3))p" "$PLAN_FILE" 2>/dev/null)

        if echo "$context" | grep -qiE "evidence|result|output|pass|exit.code|verified|test.*pass|build.*success"; then
            has_evidence=true
        fi

        # Also check for emoji indicators
        if echo "$context" | grep -qE "✅|✓|☑"; then
            has_evidence=true
        fi

        if [ "$has_evidence" = true ]; then
            evidence_count=$((evidence_count + 1))
            if [ "$VERBOSE" = true ]; then
                log_info "  Evidence found for: $(echo "$line" | head -c 60)"
            fi
        else
            missing_evidence=$((missing_evidence + 1))
            if [ "$VERBOSE" = true ]; then
                log_warn "  No evidence for: $(echo "$line" | head -c 60)"
            fi
        fi
    done < <(grep -E "^[[:space:]]*(-|\*|[0-9]+\.)\s*\[(x|X)\]" "$PLAN_FILE" 2>/dev/null || true)

    if [ "$missing_evidence" -eq 0 ]; then
        record_pass "All ${completed_checkpoints} completed checkpoints have evidence"
    elif [ "$missing_evidence" -lt "$completed_checkpoints" ]; then
        record_warn "${missing_evidence} of ${completed_checkpoints} completed checkpoints lack evidence"
    else
        record_fail "No evidence found for any completed checkpoint"
    fi
}

# ---------------------------------------------------------------------------
# Check: Completion Percentage
# ---------------------------------------------------------------------------
check_completion() {
    log_step "Completion status..."

    local total
    total=$(grep -cE "^[[:space:]]*(-|\*|[0-9]+\.)\s*\[(x|X| )\]" "$PLAN_FILE" 2>/dev/null || true)

    local completed
    completed=$(grep -cE "^[[:space:]]*(-|\*|[0-9]+\.)\s*\[(x|X)\]" "$PLAN_FILE" 2>/dev/null || true)

    local pending
    pending=$(grep -cE "^[[:space:]]*(-|\*|[0-9]+\.)\s*\[( )\]" "$PLAN_FILE" 2>/dev/null || true)

    if [ "$total" -eq 0 ]; then
        log_info "No checkpoints to calculate completion"
        return
    fi

    local percentage=$((completed * 100 / total))

    printf "  Total:     %d\n" "$total"
    printf "  Completed: %d\n" "$completed"
    printf "  Pending:   %d\n" "$pending"
    printf "  Progress:  %d%%\n" "$percentage"
    echo ""

    if [ "$percentage" -eq 100 ]; then
        record_pass "Plan execution complete: 100% (${completed}/${total})"
    elif [ "$percentage" -ge 75 ]; then
        record_pass "Good progress: ${percentage}% (${completed}/${total})"
    elif [ "$percentage" -ge 50 ]; then
        log_info "Progress: ${percentage}% (${completed}/${total})"
    elif [ "$percentage" -ge 25 ]; then
        log_info "Early progress: ${percentage}% (${completed}/${total})"
    else
        log_info "Just starting: ${percentage}% (${completed}/${total})"
    fi
}

# ---------------------------------------------------------------------------
# Main Checks
# ---------------------------------------------------------------------------
run_checks() {
    log_step "Plan Execution — Checkpoint Validation"

    if ! find_plan_file; then
        record_fail "No plan file found"
        log_info "Create a plan file (e.g., PLAN.md) with checkpoint format:"
        log_info "  - [ ] Task description"
        log_info "  - [x] Completed task (with evidence)"
        return
    fi

    log_info "Validating: ${PLAN_FILE}"
    echo ""

    check_checkpoint_format
    echo ""
    check_evidence
    echo ""
    check_completion
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
        log_fail "Overall: FAILED — checkpoint validation issues found"
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
