#!/usr/bin/env bash
# ============================================================================
# Dev-AID Process Skill: Verification Gate — Completion Verifier
# ============================================================================
# Auto-detects project type and runs tests, lint, and type checks to verify
# that a completion claim has evidence.
#
# Exit codes:
#   0 = PASS  — All checks passed
#   1 = FAIL  — One or more checks failed
#   2 = WARN  — Checks passed with warnings
#
# Usage:
#   ./verify-completion.sh [OPTIONS] [PROJECT_DIR]
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
SCRIPT_DESC="Auto-detect project type and run tests, lint, and type checks"

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
    0   All checks passed
    1   One or more checks failed
    2   Checks passed with warnings

${BOLD}EXAMPLES:${RESET}
    ${SCRIPT_NAME}                  # Verify current directory
    ${SCRIPT_NAME} /path/to/project # Verify specific project
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
# Project Detection
# ---------------------------------------------------------------------------
detect_project_type() {
    local dir="$1"
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
# Run Command Helper
# ---------------------------------------------------------------------------
run_check() {
    local label="$1"
    shift
    local cmd="$*"

    if [ "$VERBOSE" = true ]; then
        log_info "Running: ${cmd}"
    fi

    local output
    local exit_code=0
    output=$(eval "${cmd}" 2>&1) || exit_code=$?

    if [ "$exit_code" -eq 0 ]; then
        record_pass "${label}: exit code 0"
        if [ "$VERBOSE" = true ] && [ -n "$output" ]; then
            printf "  %s\n" "$output"
        fi
    else
        record_fail "${label}: exit code ${exit_code}"
        if [ -n "$output" ]; then
            printf "  %s\n" "$output" | head -20
        fi
    fi
}

# ---------------------------------------------------------------------------
# Optional Check (warns if tool not available)
# ---------------------------------------------------------------------------
run_optional_check() {
    local label="$1"
    local tool="$2"
    shift 2
    local cmd="$*"

    if ! command -v "$tool" >/dev/null 2>&1; then
        record_warn "${label}: '${tool}' not found, skipping"
        return
    fi

    run_check "$label" "$cmd"
}

# ---------------------------------------------------------------------------
# Main Checks
# ---------------------------------------------------------------------------
run_checks() {
    local dir="$PROJECT_DIR"
    local project_type
    project_type=$(detect_project_type "$dir")

    log_step "Verification Gate — Completion Check"
    log_info "Project directory: ${dir}"
    log_info "Detected project type: ${project_type}"
    echo ""

    case "$project_type" in
        python)
            log_step "Running Python verification..."
            run_optional_check "Tests (pytest)" "pytest" "cd \"${dir}\" && python -m pytest -v"
            run_optional_check "Lint (flake8)" "flake8" "cd \"${dir}\" && flake8 ."
            run_optional_check "Type check (mypy)" "mypy" "cd \"${dir}\" && mypy ."
            ;;
        node)
            log_step "Running Node.js verification..."
            if [ -f "${dir}/package.json" ]; then
                local has_test
                has_test=$(python3 -c "import json; d=json.load(open('${dir}/package.json')); print('yes' if 'test' in d.get('scripts',{}) else 'no')" 2>/dev/null || echo "no")
                if [ "$has_test" = "yes" ]; then
                    run_check "Tests (npm test)" "cd \"${dir}\" && npm test"
                else
                    record_warn "Tests: no 'test' script in package.json"
                fi

                local has_lint
                has_lint=$(python3 -c "import json; d=json.load(open('${dir}/package.json')); print('yes' if 'lint' in d.get('scripts',{}) else 'no')" 2>/dev/null || echo "no")
                if [ "$has_lint" = "yes" ]; then
                    run_check "Lint (npm run lint)" "cd \"${dir}\" && npm run lint"
                else
                    run_optional_check "Lint (eslint)" "eslint" "cd \"${dir}\" && npx eslint ."
                fi

                run_optional_check "Type check (tsc)" "tsc" "cd \"${dir}\" && npx tsc --noEmit"
            fi
            ;;
        rust)
            log_step "Running Rust verification..."
            run_check "Tests (cargo test)" "cd \"${dir}\" && cargo test"
            run_check "Check (cargo check)" "cd \"${dir}\" && cargo check"
            run_optional_check "Lint (clippy)" "cargo-clippy" "cd \"${dir}\" && cargo clippy -- -D warnings"
            ;;
        go)
            log_step "Running Go verification..."
            run_check "Tests (go test)" "cd \"${dir}\" && go test ./..."
            run_check "Vet (go vet)" "cd \"${dir}\" && go vet ./..."
            run_optional_check "Lint (golangci-lint)" "golangci-lint" "cd \"${dir}\" && golangci-lint run"
            ;;
        *)
            record_warn "Unknown project type — cannot auto-detect verification commands"
            log_info "Looked for: pyproject.toml, package.json, Cargo.toml, go.mod"
            log_info "Specify project directory or ensure project markers exist"
            ;;
    esac
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
        log_fail "Overall: FAILED — completion claim NOT verified"
        return 1
    elif [ "$WARN_COUNT" -gt 0 ]; then
        log_warn "Overall: PASSED WITH WARNINGS — review warnings before claiming done"
        return 2
    else
        log_pass "Overall: ALL CHECKS PASSED — completion claim verified"
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
