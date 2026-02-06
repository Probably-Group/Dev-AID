#!/usr/bin/env bash
#
# Script: validate-bash-scripts.sh
# Description: Validates Bash scripts for bash-expert skill compliance
# Usage: validate-bash-scripts.sh [--strict] [script_files...]
#        Default: scans all .sh files in .dev-aid/ (excluding venv/)
#

# Strict mode
set -euo pipefail
IFS=$'\n\t'

# Script metadata
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"
readonly DEV_AID_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly BOLD='\033[1m'
readonly NC='\033[0m'

# Counters (declare -i for arithmetic)
declare -i total_pass=0
declare -i total_fail=0
declare -i total_warn=0
declare -i total_files=0
declare -i strict_mode=0

# Cleanup function
cleanup() {
    local exit_code=$?
    exit "${exit_code}"
}
trap cleanup EXIT INT TERM

# ── Logging ──────────────────────────────────────────────────────────────────

log_pass() {
    local msg="$1"
    echo -e "  ${GREEN}PASS${NC}  ${msg}"
    total_pass+=1
}

log_fail() {
    local msg="$1"
    echo -e "  ${RED}FAIL${NC}  ${msg}"
    total_fail+=1
}

log_warn() {
    local msg="$1"
    if [[ "${strict_mode}" -eq 1 ]]; then
        echo -e "  ${RED}FAIL${NC}  ${msg} (strict mode: WARN->FAIL)"
        total_fail+=1
    else
        echo -e "  ${YELLOW}WARN${NC}  ${msg}"
        total_warn+=1
    fi
}

# ── Check Functions ──────────────────────────────────────────────────────────

check_shebang() {
    local script="$1"
    local first_line
    first_line="$(head -1 "${script}")"

    if [[ "${first_line}" == "#!/usr/bin/env bash" ]]; then
        log_pass "Shebang: #!/usr/bin/env bash"
    elif [[ "${first_line}" == "#!/bin/bash" ]]; then
        log_fail "Shebang: #!/bin/bash (must be #!/usr/bin/env bash)"
    else
        log_fail "Shebang: missing or incorrect (found: ${first_line})"
    fi
}

check_strict_mode() {
    local script="$1"

    if grep -q "^set -euo pipefail" "${script}"; then
        log_pass "Strict mode: set -euo pipefail"
    else
        log_fail "Strict mode: missing 'set -euo pipefail'"
    fi
}

check_ifs() {
    local script="$1"

    if grep -q "^IFS=\\\$'\\\\n\\\\t'" "${script}"; then
        log_pass "IFS: IFS=\$'\\n\\t' is set"
    else
        log_fail "IFS: missing IFS=\$'\\n\\t' after strict mode"
    fi
}

check_cleanup_trap() {
    local script="$1"

    if grep -qE "^trap\s+\S+\s+.*EXIT" "${script}"; then
        log_pass "Cleanup trap: trap ... EXIT found"
    else
        log_fail "Cleanup trap: no 'trap ... EXIT' found"
    fi
}

check_syntax() {
    local script="$1"

    if bash -n "${script}" 2>/dev/null; then
        log_pass "Syntax: bash -n passed"
    else
        log_fail "Syntax: bash -n failed"
    fi
}

check_dangerous_patterns() {
    local script="$1"
    local found_issues=0

    # Check for eval usage — exclude lines that are themselves grep/check patterns
    # by filtering out lines containing "grep", "check", or quoted 'eval'
    local eval_hits
    eval_hits="$(grep -nE "^[^#]*\beval\b" "${script}" \
        | grep -vE "(grep|log_|echo|check_|#)" \
        || true)"
    if [[ -n "${eval_hits}" ]]; then
        log_fail "Dangerous: uses 'eval' (avoid)"
        found_issues=1
    fi

    # Check for backticks (excluding comments and grep patterns)
    local backtick_hits
    backtick_hits="$(grep -n '`' "${script}" \
        | grep -vE "(^\s*#|grep|log_|echo)" \
        || true)"
    if [[ -n "${backtick_hits}" ]]; then
        log_fail "Dangerous: uses backticks (use \$() instead)"
        found_issues=1
    fi

    if [[ "${found_issues}" -eq 0 ]]; then
        log_pass "Dangerous patterns: none detected"
    fi
}

check_test_brackets() {
    local script="$1"
    local bad_lines

    # Find lines with single [ (space after) that are NOT [[ (exclude comments)
    bad_lines="$(grep -nE '\[\s' "${script}" \
        | grep -vE '(\[\[|^\s*#|grep|echo|log_)' \
        || true)"

    if [[ -n "${bad_lines}" ]]; then
        local count
        count="$(echo "${bad_lines}" | wc -l | tr -d ' ')"
        log_fail "Test brackets: uses single [ ] instead of [[ ]] — ${count} occurrence(s)"
    else
        log_pass "Test brackets: uses [[ ]] consistently"
    fi
}

check_variable_braces() {
    local script="$1"
    local bad_count
    declare -i bad_count=0

    # Find "$VAR" without braces (should be "${VAR}"), excluding comments
    bad_count=$(grep -cE '^\s*[^#]*"\$[A-Za-z_][A-Za-z_0-9]*[^}]' "${script}" || true)

    if [[ "${bad_count}" -gt 0 ]]; then
        log_warn "Variable braces: ~${bad_count} variable(s) without \${} braces"
    else
        log_pass "Variable braces: all variables use \${var} form"
    fi
}

check_local_in_functions() {
    local script="$1"
    local found_issues=0
    local in_function=0
    local local_vars=""
    local global_vars=""

    # First pass: collect top-level (global) variable names
    while IFS= read -r line; do
        # Top-level declare/readonly
        if [[ "${line}" =~ ^(declare|readonly)[[:space:]]+([-a-zA-Z]*[[:space:]]+)?([a-zA-Z_][a-zA-Z_0-9]*) ]]; then
            global_vars="${global_vars} ${BASH_REMATCH[3]}"
        fi
        # Top-level VAR= (no leading whitespace)
        if [[ "${line}" =~ ^([a-zA-Z_][a-zA-Z_0-9]*)= ]]; then
            global_vars="${global_vars} ${BASH_REMATCH[1]}"
        fi
    done < "${script}"

    # Second pass: check functions
    while IFS= read -r line; do
        # Detect function start
        if [[ "${line}" =~ ^[[:space:]]*(function[[:space:]]+)?([a-zA-Z_][a-zA-Z_0-9]*)[[:space:]]*\(\)[[:space:]]*\{ ]]; then
            in_function=1
            local_vars=""
            continue
        fi

        # Detect function end (closing brace)
        if [[ "${in_function}" -eq 1 ]] && [[ "${line}" =~ ^[[:space:]]*\}[[:space:]]*$ ]]; then
            in_function=0
            local_vars=""
            continue
        fi

        # Inside a function
        if [[ "${in_function}" -eq 1 ]]; then
            # Skip comments, empty lines
            if [[ "${line}" =~ ^[[:space:]]*# ]] || [[ -z "${line// }" ]]; then
                continue
            fi

            # Track variables declared with local/declare inside function
            if [[ "${line}" =~ ^[[:space:]]*(local|declare)[[:space:]]+([-a-zA-Z]*[[:space:]]+)?([a-zA-Z_][a-zA-Z_0-9]*) ]]; then
                local_vars="${local_vars} ${BASH_REMATCH[3]}"
                continue
            fi

            # Skip lines with export/readonly/typeset
            if [[ "${line}" =~ ^[[:space:]]*(readonly|export|typeset)[[:space:]] ]]; then
                continue
            fi

            # Skip control flow, commands, etc.
            if [[ "${line}" =~ ^[[:space:]]*(if|then|else|elif|fi|for|while|do|done|case|esac|return|echo|continue|break|total_|log_) ]]; then
                continue
            fi

            # Match: VAR= or VAR+= (assignment)
            if [[ "${line}" =~ ^[[:space:]]+([a-zA-Z_][a-zA-Z_0-9]*)(\+)?= ]]; then
                local var_name="${BASH_REMATCH[1]}"
                # Skip if declared with local in this function or is a known global
                if [[ " ${local_vars} " != *" ${var_name} "* ]] && \
                   [[ " ${global_vars} " != *" ${var_name} "* ]]; then
                    found_issues=1
                fi
            fi
        fi
    done < "${script}"

    if [[ "${found_issues}" -eq 1 ]]; then
        log_fail "Local vars: function variable(s) assigned without 'local'"
    else
        log_pass "Local vars: all function variables use 'local'"
    fi
}

check_readonly_constants() {
    local script="$1"
    declare -i bad_count=0

    # Check top-level UPPERCASE= assignments that lack readonly
    while IFS= read -r line; do
        # Skip comments and empty lines
        if [[ "${line}" =~ ^[[:space:]]*# ]] || [[ -z "${line}" ]]; then
            continue
        fi
        # Match top-level uppercase assignments without readonly/declare/export
        # Exclude shell builtins (IFS, PATH, PS1, etc.)
        if [[ "${line}" =~ ^[A-Z_][A-Z_0-9]*= ]] && \
           ! [[ "${line}" =~ ^(readonly|declare|export)[[:space:]] ]] && \
           ! [[ "${line}" =~ ^(IFS|PATH|PS1|PS2|PS4|HOME|SHELL|TERM|LANG|LC_)= ]]; then
            bad_count+=1
        fi
    done < "${script}"

    if [[ "${bad_count}" -gt 0 ]]; then
        log_warn "Readonly: ${bad_count} top-level constant(s) without 'readonly'"
    else
        log_pass "Readonly: all top-level constants use 'readonly'"
    fi
}

check_chmod_permissions() {
    local script="$1"
    local bad_lines

    bad_lines="$(grep -nE '^\s*[^#]*(chmod\s+(777|666)|chmod\s+o\+w)' "${script}" || true)"

    if [[ -n "${bad_lines}" ]]; then
        log_fail "Permissions: insecure chmod (777/666/o+w) detected"
    else
        log_pass "Permissions: no insecure chmod patterns"
    fi
}

check_mktemp_usage() {
    local script="$1"
    local bad_lines

    # Find hardcoded /tmp/ paths that don't use mktemp (exclude comments and grep patterns)
    bad_lines="$(grep -nE '^\s*[^#]*/tmp/' "${script}" \
        | grep -vE "(mktemp|grep|echo|log_)" \
        || true)"

    if [[ -n "${bad_lines}" ]]; then
        log_warn "Temp files: hardcoded /tmp/ path(s) — use mktemp instead"
    else
        log_pass "Temp files: no hardcoded /tmp/ paths (or uses mktemp)"
    fi
}

check_curl_pipe() {
    local script="$1"
    local bad_lines

    # Find curl | bash patterns, but exclude lines that are grep patterns checking for this
    bad_lines="$(grep -nE '^\s*[^#]*curl\s.*\|\s*(ba)?sh' "${script}" \
        | grep -vE "(grep|log_|echo|check_)" \
        || true)"

    if [[ -n "${bad_lines}" ]]; then
        log_fail "Curl pipe: curl | bash pattern detected (never pipe to shell)"
    else
        log_pass "Curl pipe: no curl | bash patterns"
    fi
}

check_unquoted_subshell() {
    local script="$1"
    declare -i bad_count=0

    # Find unquoted command substitution: VAR=$(...) without quotes
    bad_count=$(grep -cE '^\s*[^#]*[a-zA-Z_]+=[^"]*\$\(' "${script}" || true)

    if [[ "${bad_count}" -gt 0 ]]; then
        log_warn "Unquoted \$(): ~${bad_count} unquoted command substitution(s)"
    else
        log_pass "Unquoted \$(): all command substitutions properly quoted"
    fi
}

# ── File Discovery ───────────────────────────────────────────────────────────

find_bash_scripts() {
    # Find all .sh files in .dev-aid/ excluding venv/ and __pycache__/
    find "${DEV_AID_DIR}" \
        -name "*.sh" \
        -not -path "*/venv/*" \
        -not -path "*/__pycache__/*" \
        -not -path "*/.git/*" \
        -type f | sort
}

# ── Validate Single Script ──────────────────────────────────────────────────

validate_script() {
    local script="$1"
    local relative_path

    relative_path="$(python3 -c "import os; print(os.path.relpath('${script}', '${DEV_AID_DIR}'))" 2>/dev/null || echo "${script}")"

    echo ""
    echo -e "${BOLD}── ${relative_path} ──${NC}"

    check_shebang "${script}"
    check_strict_mode "${script}"
    check_ifs "${script}"
    check_cleanup_trap "${script}"
    check_syntax "${script}"
    check_dangerous_patterns "${script}"
    check_test_brackets "${script}"
    check_variable_braces "${script}"
    check_local_in_functions "${script}"
    check_readonly_constants "${script}"
    check_chmod_permissions "${script}"
    check_mktemp_usage "${script}"
    check_curl_pipe "${script}"
    check_unquoted_subshell "${script}"

    total_files+=1
}

# ── Usage ────────────────────────────────────────────────────────────────────

usage() {
    echo "Usage: ${SCRIPT_NAME} [--strict] [file ...]"
    echo ""
    echo "Validates Bash scripts for bash-expert skill compliance."
    echo ""
    echo "Options:"
    echo "  --strict    Treat WARN as FAIL"
    echo "  --help      Show this help message"
    echo ""
    echo "If no files specified, scans all .sh files in .dev-aid/ (excluding venv/)."
}

# ── Main ─────────────────────────────────────────────────────────────────────

main() {
    local -a scripts_to_check=()
    local -a args=()

    # Parse arguments
    for arg in "$@"; do
        if [[ "${arg}" == "--strict" ]]; then
            strict_mode=1
        elif [[ "${arg}" == "--help" ]] || [[ "${arg}" == "-h" ]]; then
            usage
            exit 0
        else
            args+=("${arg}")
        fi
    done

    echo -e "${BOLD}Bash Expert Skill Compliance Validator${NC}"
    echo "========================================"
    if [[ "${strict_mode}" -eq 1 ]]; then
        echo -e "${YELLOW}Mode: STRICT (WARN -> FAIL)${NC}"
    fi

    if [[ "${#args[@]}" -gt 0 ]]; then
        # Validate specified files
        for file in "${args[@]}"; do
            if [[ ! -f "${file}" ]]; then
                echo -e "${RED}Error: file not found: ${file}${NC}"
                total_fail+=1
                continue
            fi
            validate_script "${file}"
        done
    else
        # Auto-discover all .sh files
        local script_list
        script_list="$(find_bash_scripts)"

        if [[ -z "${script_list}" ]]; then
            echo "No .sh files found in ${DEV_AID_DIR}"
            exit 0
        fi

        while IFS= read -r script; do
            validate_script "${script}"
        done <<< "${script_list}"
    fi

    # Summary
    echo ""
    echo "========================================"
    echo -e "${BOLD}Summary${NC}"
    echo "========================================"
    echo "Files scanned: ${total_files}"
    echo -e "${GREEN}PASS:${NC} ${total_pass}"
    echo -e "${RED}FAIL:${NC} ${total_fail}"
    echo -e "${YELLOW}WARN:${NC} ${total_warn}"
    echo ""

    if [[ "${total_fail}" -gt 0 ]]; then
        echo -e "${RED}${BOLD}RESULT: FAILED${NC} (${total_fail} failure(s))"
        exit 1
    else
        echo -e "${GREEN}${BOLD}RESULT: PASSED${NC} (${total_warn} warning(s))"
        exit 0
    fi
}

main "$@"
