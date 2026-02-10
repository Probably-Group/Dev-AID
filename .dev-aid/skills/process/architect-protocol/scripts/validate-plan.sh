#!/usr/bin/env bash
# ============================================================================
# Dev-AID Process Skill: Architect Protocol — Plan Validator
# ============================================================================
# Verifies that an architect plan has required sections: Summary, Files,
# Steps, Criteria, and Risks. Checks that file list references actual paths
# and validates that success criteria are measurable.
#
# Exit codes:
#   0 = PASS  — Plan meets all requirements
#   1 = FAIL  — Missing required sections or invalid references
#   2 = WARN  — Partial compliance
#
# Usage:
#   ./validate-plan.sh [OPTIONS] [PLAN_FILE]
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
SCRIPT_DESC="Validate architect plan: sections, file refs, success criteria"

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
    -h, --help          Show this help message
    -v, --verbose       Enable verbose output
    -q, --quiet         Suppress non-error output
    --project-dir DIR   Project root for file path validation (default: .)

${BOLD}ARGUMENTS:${RESET}
    PLAN_FILE       Path to architect plan (auto-detects if not specified)

${BOLD}EXIT CODES:${RESET}
    0   Plan meets all requirements
    1   Missing required sections or invalid references
    2   Partial compliance (warnings)

${BOLD}REQUIRED SECTIONS:${RESET}
    - Summary
    - Affected Files (or Files)
    - Implementation Steps (or Steps)
    - Success Criteria (or Criteria)
    - Risks & Mitigations (or Risks)

${BOLD}EXAMPLES:${RESET}
    ${SCRIPT_NAME}                          # Auto-detect plan file
    ${SCRIPT_NAME} PLAN.md                  # Validate specific plan
    ${SCRIPT_NAME} --project-dir /src PLAN.md
EOF
}

# ---------------------------------------------------------------------------
# Argument Parsing
# ---------------------------------------------------------------------------
VERBOSE=false
QUIET=false
PLAN_FILE=""
PROJECT_ROOT="."

parse_args() {
    while [ $# -gt 0 ]; do
        case "$1" in
            -h|--help) usage; exit 0 ;;
            -v|--verbose) VERBOSE=true ;;
            -q|--quiet) QUIET=true ;;
            --project-dir)
                shift
                PROJECT_ROOT="${1:-.}"
                ;;
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
        "IMPLEMENTATION_PLAN.md"
        "implementation-plan.md"
        "ARCHITECT_PLAN.md"
        "architect-plan.md"
        ".dev-aid/plan.md"
        "docs/plan.md"
        "docs/implementation-plan.md"
        "RFC.md"
        "rfc.md"
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
# Check: Required Section Exists
# ---------------------------------------------------------------------------
check_section() {
    local section_name="$1"
    shift
    local patterns=("$@")

    for pattern in "${patterns[@]}"; do
        if grep -qiE "$pattern" "$PLAN_FILE" 2>/dev/null; then
            record_pass "Section found: ${section_name}"
            if [ "$VERBOSE" = true ]; then
                local match
                match=$(grep -iE "$pattern" "$PLAN_FILE" | head -1)
                log_info "  Matched: ${match}"
            fi
            return 0
        fi
    done

    record_fail "Missing section: ${section_name}"
    return 1
}

# ---------------------------------------------------------------------------
# Check: File References Are Valid
# ---------------------------------------------------------------------------
check_file_references() {
    log_step "Checking file path references..."

    # Extract file paths from the plan (backtick-quoted paths and markdown paths)
    local file_paths=()
    local raw_paths

    # Match backtick-quoted paths (e.g., `path/to/file.ts`)
    raw_paths=$(grep -oE '`[a-zA-Z0-9_./-]+\.[a-zA-Z0-9]+`' "$PLAN_FILE" 2>/dev/null | tr -d '`' | sort -u || true)

    if [ -z "$raw_paths" ]; then
        record_warn "No file path references found in plan"
        return
    fi

    local total_paths=0
    local valid_paths=0
    local invalid_paths=0
    local new_paths=0

    while IFS= read -r filepath; do
        [ -z "$filepath" ] && continue
        total_paths=$((total_paths + 1))

        # Check if file exists (relative to project root)
        if [ -f "${PROJECT_ROOT}/${filepath}" ]; then
            valid_paths=$((valid_paths + 1))
            if [ "$VERBOSE" = true ]; then
                log_info "  Exists: ${filepath}"
            fi
        else
            # Check if it's marked as NEW in the plan
            if grep -q "${filepath}.*NEW\|NEW.*${filepath}\|new file\|create.*${filepath}" "$PLAN_FILE" 2>/dev/null; then
                new_paths=$((new_paths + 1))
                if [ "$VERBOSE" = true ]; then
                    log_info "  New file (planned): ${filepath}"
                fi
            else
                invalid_paths=$((invalid_paths + 1))
                if [ "$VERBOSE" = true ]; then
                    log_warn "  Not found: ${filepath}"
                fi
            fi
        fi
    done <<< "$raw_paths"

    log_info "File references: ${total_paths} total, ${valid_paths} exist, ${new_paths} planned new, ${invalid_paths} not found"

    if [ "$invalid_paths" -eq 0 ]; then
        record_pass "All file references are valid (${valid_paths} existing, ${new_paths} new)"
    elif [ "$invalid_paths" -le 2 ]; then
        record_warn "${invalid_paths} file reference(s) not found and not marked as NEW"
    else
        record_fail "${invalid_paths} file references not found — verify paths are correct"
    fi
}

# ---------------------------------------------------------------------------
# Check: Success Criteria Are Measurable
# ---------------------------------------------------------------------------
check_success_criteria() {
    log_step "Checking success criteria quality..."

    # Extract success criteria section content
    local in_criteria=false
    local criteria_lines=()
    local criteria_count=0

    while IFS= read -r line; do
        # Detect criteria section start
        if echo "$line" | grep -qiE "^#+.*success.*criter|^#+.*criteria|^#+.*acceptance"; then
            in_criteria=true
            continue
        fi

        # Detect next section (exit criteria section)
        if [ "$in_criteria" = true ] && echo "$line" | grep -qE "^#+"; then
            in_criteria=false
            continue
        fi

        if [ "$in_criteria" = true ] && [ -n "$line" ]; then
            criteria_lines+=("$line")
            # Count checkbox items
            if echo "$line" | grep -qE "^\s*(-|\*)\s*\["; then
                criteria_count=$((criteria_count + 1))
            fi
        fi
    done < "$PLAN_FILE"

    if [ ${#criteria_lines[@]} -eq 0 ]; then
        record_fail "No success criteria content found"
        return
    fi

    if [ "$criteria_count" -eq 0 ]; then
        record_warn "Success criteria exist but not in checklist format (- [ ] ...)"
    else
        record_pass "Found ${criteria_count} success criteria in checklist format"
    fi

    # Check for measurable language
    local measurable_count=0
    local vague_count=0

    for line in "${criteria_lines[@]}"; do
        # Measurable patterns: numbers, "pass", "exit code", "100%", "no errors"
        if echo "$line" | grep -qiE "[0-9]+|pass|exit.code|no.error|no.warning|zero|100%|coverage|succeed|compile|build|test"; then
            measurable_count=$((measurable_count + 1))
        # Vague patterns: "good", "nice", "proper", "clean" without specifics
        elif echo "$line" | grep -qiE "good|nice|proper|clean|well|better|improved" && ! echo "$line" | grep -qiE "[0-9]+|pass|test|build"; then
            vague_count=$((vague_count + 1))
        fi
    done

    if [ "$measurable_count" -gt 0 ] && [ "$vague_count" -eq 0 ]; then
        record_pass "Success criteria appear measurable (${measurable_count} measurable items)"
    elif [ "$measurable_count" -gt "$vague_count" ]; then
        record_warn "Some criteria may be vague (${vague_count} vague vs ${measurable_count} measurable)"
    elif [ "$vague_count" -gt 0 ]; then
        record_fail "Success criteria are too vague — use measurable outcomes (test pass, exit code 0, etc.)"
    fi
}

# ---------------------------------------------------------------------------
# Check: Risks Section Quality
# ---------------------------------------------------------------------------
check_risks() {
    log_step "Checking risks & mitigations..."

    local has_risks=false
    local has_mitigations=false

    if grep -qiE "^#+.*risk|^#+.*mitigation" "$PLAN_FILE" 2>/dev/null; then
        has_risks=true
    fi

    if grep -qiE "mitigation|fallback|workaround|alternative|contingency|if.*fail" "$PLAN_FILE" 2>/dev/null; then
        has_mitigations=true
    fi

    if [ "$has_risks" = true ] && [ "$has_mitigations" = true ]; then
        record_pass "Risks section with mitigations found"
    elif [ "$has_risks" = true ] && [ "$has_mitigations" = false ]; then
        record_warn "Risks identified but mitigations may be missing"
    else
        record_fail "No risks section found — identify potential issues and mitigations"
    fi
}

# ---------------------------------------------------------------------------
# Main Checks
# ---------------------------------------------------------------------------
run_checks() {
    log_step "Architect Protocol — Plan Validation"

    if ! find_plan_file; then
        record_fail "No plan file found"
        log_info "Create a plan file (e.g., PLAN.md) with required sections:"
        log_info "  - Summary"
        log_info "  - Affected Files"
        log_info "  - Implementation Steps"
        log_info "  - Success Criteria"
        log_info "  - Risks & Mitigations"
        return
    fi

    log_info "Validating: ${PLAN_FILE}"
    log_info "Project root: ${PROJECT_ROOT}"
    echo ""

    log_step "Checking required sections..."
    check_section "Summary" \
        "^#+.*summary" "^#+.*overview" "^#+.*description"
    check_section "Affected Files" \
        "^#+.*affected.file" "^#+.*file" "^#+.*modified.file" "^#+.*changed.file"
    check_section "Implementation Steps" \
        "^#+.*implementation.step" "^#+.*step" "^#+.*plan" "^#+.*procedure"
    check_section "Success Criteria" \
        "^#+.*success.criter" "^#+.*criteria" "^#+.*acceptance" "^#+.*definition.of.done"
    check_section "Risks & Mitigations" \
        "^#+.*risk" "^#+.*mitigation" "^#+.*concern" "^#+.*caveat"

    echo ""
    check_file_references
    echo ""
    check_success_criteria
    echo ""
    check_risks
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
        log_fail "Overall: FAILED — plan does not meet architect protocol requirements"
        return 1
    elif [ "$WARN_COUNT" -gt 0 ]; then
        log_warn "Overall: PASSED WITH WARNINGS — improve plan before implementation"
        return 2
    else
        log_pass "Overall: ALL CHECKS PASSED — plan is ready for implementation"
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
