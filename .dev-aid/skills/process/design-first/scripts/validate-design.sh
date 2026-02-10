#!/usr/bin/env bash
# ============================================================================
# Dev-AID Process Skill: Design-First — Design Document Validator
# ============================================================================
# Checks that a design document has required sections: Problem, Constraints,
# Options, and Decision. Validates at least 2 options are considered and
# that a decision rationale exists.
#
# Exit codes:
#   0 = PASS  — Design document meets all requirements
#   1 = FAIL  — Missing required sections or content
#   2 = WARN  — Partial compliance
#
# Usage:
#   ./validate-design.sh [OPTIONS] [DESIGN_DOC]
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
SCRIPT_DESC="Validate design document has required sections and content"

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
    ${SCRIPT_NAME} [OPTIONS] [DESIGN_DOC]

${BOLD}OPTIONS:${RESET}
    -h, --help      Show this help message
    -v, --verbose   Enable verbose output
    -q, --quiet     Suppress non-error output

${BOLD}ARGUMENTS:${RESET}
    DESIGN_DOC      Path to design document (auto-detects if not specified)

${BOLD}EXIT CODES:${RESET}
    0   Design document meets all requirements
    1   Missing required sections or content
    2   Partial compliance (warnings)

${BOLD}EXAMPLES:${RESET}
    ${SCRIPT_NAME}                          # Auto-detect design doc
    ${SCRIPT_NAME} docs/design.md           # Validate specific file
    ${SCRIPT_NAME} --verbose DESIGN.md      # Verbose output
EOF
}

# ---------------------------------------------------------------------------
# Argument Parsing
# ---------------------------------------------------------------------------
VERBOSE=false
QUIET=false
DESIGN_DOC=""

parse_args() {
    while [ $# -gt 0 ]; do
        case "$1" in
            -h|--help) usage; exit 0 ;;
            -v|--verbose) VERBOSE=true ;;
            -q|--quiet) QUIET=true ;;
            -*) log_warn "Unknown option: $1" ;;
            *) DESIGN_DOC="$1" ;;
        esac
        shift
    done
}

# ---------------------------------------------------------------------------
# Auto-Detect Design Document
# ---------------------------------------------------------------------------
find_design_doc() {
    if [ -n "$DESIGN_DOC" ] && [ -f "$DESIGN_DOC" ]; then
        return 0
    fi

    local candidates=(
        "DESIGN.md"
        "design.md"
        "DESIGN_DOC.md"
        "design-doc.md"
        "docs/design.md"
        "docs/DESIGN.md"
        ".dev-aid/memory-bank/decisions.md"
        "ADR.md"
        "adr.md"
        "docs/adr.md"
        "ARCHITECTURE.md"
        "architecture.md"
        "RFC.md"
        "rfc.md"
    )

    for f in "${candidates[@]}"; do
        if [ -f "$f" ]; then
            DESIGN_DOC="$f"
            log_info "Auto-detected design document: ${f}"
            return 0
        fi
    done

    return 1
}

# ---------------------------------------------------------------------------
# Check: Required Section Exists
# ---------------------------------------------------------------------------
check_section() {
    local section_name="$1"
    shift
    local patterns=("$@")

    for pattern in "${patterns[@]}"; do
        if grep -qi "$pattern" "$DESIGN_DOC" 2>/dev/null; then
            record_pass "Section found: ${section_name}"
            if [ "$VERBOSE" = true ]; then
                local match
                match=$(grep -i "$pattern" "$DESIGN_DOC" | head -1)
                log_info "  Matched: ${match}"
            fi
            return 0
        fi
    done

    record_fail "Missing section: ${section_name}"
    return 1
}

# ---------------------------------------------------------------------------
# Check: At Least 2 Options Considered
# ---------------------------------------------------------------------------
check_options_count() {
    log_step "Checking for multiple options..."

    # Count option headers (##+ Option, ###+ Approach, numbered options)
    local option_count=0

    # Pattern: "Option N", "Approach N", "Alternative N"
    local numbered_options
    numbered_options=$(grep -ciE "^#+.*option|^#+.*approach|^#+.*alternative" "$DESIGN_DOC" 2>/dev/null || true)
    option_count=$((option_count + numbered_options))

    # Pattern: "### Option 1: Name" style headers
    local named_options
    named_options=$(grep -cE "^#+.*[Oo]ption [0-9]" "$DESIGN_DOC" 2>/dev/null || true)
    if [ "$named_options" -gt "$option_count" ]; then
        option_count="$named_options"
    fi

    # Pattern: "Pros/Cons" blocks (each block = 1 option)
    local pros_cons
    pros_cons=$(grep -ciE "^\*\*pros\*\*|^pros:|^\*\*advantages\*\*" "$DESIGN_DOC" 2>/dev/null || true)
    if [ "$pros_cons" -gt "$option_count" ]; then
        option_count="$pros_cons"
    fi

    if [ "$VERBOSE" = true ]; then
        log_info "Detected options: ${option_count}"
    fi

    if [ "$option_count" -ge 2 ]; then
        record_pass "At least 2 options considered (found: ${option_count})"
    elif [ "$option_count" -eq 1 ]; then
        record_fail "Only 1 option found — design-first requires at least 2 options"
    else
        record_fail "No options section found — present at least 2 approaches"
    fi
}

# ---------------------------------------------------------------------------
# Check: Decision Rationale
# ---------------------------------------------------------------------------
check_decision_rationale() {
    log_step "Checking for decision rationale..."

    # Look for decision section
    local has_decision=false
    if grep -qiE "^#+.*decision|^#+.*chosen|^#+.*selected|^#+.*recommendation" "$DESIGN_DOC" 2>/dev/null; then
        has_decision=true
    fi

    # Look for rationale content ("because", "reason", "chose X over Y")
    local has_rationale=false
    if grep -qi "because\|rationale\|reason\|chose.*over\|selected.*due\|prefer.*because\|decided" "$DESIGN_DOC" 2>/dev/null; then
        has_rationale=true
    fi

    if [ "$has_decision" = true ] && [ "$has_rationale" = true ]; then
        record_pass "Decision section with rationale found"
    elif [ "$has_decision" = true ] && [ "$has_rationale" = false ]; then
        record_warn "Decision section exists but rationale may be weak — explain WHY"
    elif [ "$has_decision" = false ] && [ "$has_rationale" = true ]; then
        record_warn "Rationale text exists but no clear Decision section header"
    else
        record_fail "No decision or rationale found — document which option was chosen and why"
    fi
}

# ---------------------------------------------------------------------------
# Main Checks
# ---------------------------------------------------------------------------
run_checks() {
    log_step "Design-First — Design Document Validation"

    if ! find_design_doc; then
        record_fail "No design document found"
        log_info "Create a design document (e.g., DESIGN.md) with sections:"
        log_info "  - Problem Statement"
        log_info "  - Constraints"
        log_info "  - Options Considered (at least 2)"
        log_info "  - Decision (with rationale)"
        return
    fi

    log_info "Validating: ${DESIGN_DOC}"
    echo ""

    log_step "Checking required sections..."
    check_section "Problem Statement" \
        "problem" "problem statement" "what we.re solving" "objective" "goal" "overview"
    check_section "Constraints" \
        "constraint" "limitation" "requirement" "non.negotiable" "boundary"
    check_section "Options Considered" \
        "option" "approach" "alternative" "considered" "comparison"
    check_section "Decision" \
        "decision" "chosen" "selected" "recommendation" "conclusion"

    echo ""
    check_options_count
    echo ""
    check_decision_rationale
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
        log_fail "Overall: FAILED — design document does not meet requirements"
        return 1
    elif [ "$WARN_COUNT" -gt 0 ]; then
        log_warn "Overall: PASSED WITH WARNINGS — improve design document"
        return 2
    else
        log_pass "Overall: ALL CHECKS PASSED — design document is complete"
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
