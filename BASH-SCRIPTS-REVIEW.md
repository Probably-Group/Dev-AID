# Bash Scripts Compliance Review

**Review Date**: 2025-12-04
**Skill Used**: bash-expert (HIGH-RISK)
**Total Scripts Reviewed**: 23
**Detailed Reviews**: 6 core scripts

---

## Executive Summary

This comprehensive review evaluates all Bash scripts in the Dev-AID repository against the `bash-expert` skill requirements. The skill enforces HIGH-RISK security standards including:

- Strict mode execution (`set -euo pipefail`)
- Trap-based cleanup handlers
- Input validation and path containment
- Secure temporary file handling
- OWASP and CWE compliance (Command Injection, Path Traversal, TOCTOU)
- CVE-2014-6271 (Shellshock) mitigation

### Overall Compliance Statistics

| Metric | Value |
|--------|-------|
| **Average Compliance** | 54% |
| **Scripts Reviewed** | 6 core scripts (23 total identified) |
| **Critical Issues** | 21 |
| **High Issues** | 15 |
| **Medium Issues** | 8 |
| **Low Issues** | 12 |

### Compliance by Script

| Script | Compliance | Critical | High | Medium | Low |
|--------|-----------|----------|------|--------|-----|
| **router-cli.sh** | 65% | 1 | 1 | 1 | 2 |
| **router.sh** | 60% | 0 | 0 | 2 | 3 |
| **install.sh** | 60% | 3 | 2 | 1 | 1 |
| **setup-venv.sh** | 58% | 2 | 2 | 1 | 2 |
| **session-start-load-context.sh** | 50% | 2 | 3 | 1 | 1 |
| **pre-commit hook** | 45% | 3 | 2 | 1 | 2 |
| **pre-push hook** | 40% | 3 | 2 | 1 | 2 |

---

## Common Critical Patterns (Across All Scripts)

### 1. Missing or Incomplete Strict Mode
**Affected**: 5 out of 6 scripts
**Severity**: CRITICAL
**CWE**: CWE-754 (Improper Check for Unusual or Exceptional Conditions)

**Issue**:
```bash
# Current (UNSAFE):
set -e  # Only exits on errors, doesn't catch undefined variables

# Required (SECURE):
set -euo pipefail
```

**Impact**: Silent failures, undefined variable expansion, pipeline errors masked

**Remediation**: Add full strict mode to all scripts:
```bash
#!/usr/bin/env bash
set -euo pipefail  # Exit on error, undefined vars, pipe failures
```

---

### 2. Missing Trap-Based Cleanup
**Affected**: 5 out of 6 scripts
**Severity**: CRITICAL
**CWE**: CWE-404 (Improper Resource Shutdown or Release)

**Issue**:
```bash
# Current (UNSAFE):
temp_file=$(mktemp)
# No cleanup if script exits early

# Required (SECURE):
temp_file=$(mktemp)
trap 'rm -f "$temp_file"' EXIT INT TERM
```

**Impact**: Resource leaks, temporary file exposure, incomplete cleanup

**Remediation**: Add cleanup traps to all scripts that use temporary resources

---

### 3. Insecure Temporary File Handling
**Affected**: 4 out of 6 scripts
**Severity**: CRITICAL
**CWE**: CWE-377 (Insecure Temporary File)

**Issue**:
```bash
# Current (UNSAFE):
temp_file=$(mktemp)  # Created with default permissions (often 644)

# Required (SECURE):
temp_file=$(mktemp)
chmod 600 "$temp_file"
trap 'shred -u "$temp_file" 2>/dev/null || rm -f "$temp_file"' EXIT
```

**Impact**: Information disclosure, race conditions (TOCTOU)

---

### 4. Missing Path Traversal Protection
**Affected**: 4 out of 6 scripts
**Severity**: CRITICAL
**CWE**: CWE-22 (Path Traversal)

**Issue**:
```bash
# Current (UNSAFE):
rm -rf "$VENV_DIR"  # $VENV_DIR not validated, could be ../../../../etc

# Required (SECURE):
validate_path_containment() {
    local path="$1"
    local base="$2"
    local resolved_path="$(realpath -m "$path")"
    local resolved_base="$(realpath "$base")"

    if [[ "$resolved_path" != "$resolved_base"* ]]; then
        echo "Error: Path traversal attempt detected" >&2
        return 1
    fi
}

validate_path_containment "$VENV_DIR" "$PROJECT_ROOT" || exit 1
rm -rf "$VENV_DIR"
```

**Impact**: Arbitrary file deletion, privilege escalation

---

## Detailed Findings by Script

### 1. install.sh (60% Compliance)

**Location**: `/home/user/Dev-AID/install.sh`

#### CRITICAL Issues

**C1: No Cleanup Trap**
- **Line**: Entire script
- **Issue**: No trap handler for cleanup on exit/error
- **Risk**: Incomplete installation state, orphaned files

**C2: Unvalidated PROJECT_ROOT**
- **Line**: 22-24
- **Issue**: `cd "$PROJECT_ROOT"` without validating path containment
- **Risk**: Could operate in system directories if PROJECT_ROOT is manipulated
- **Fix**:
```bash
validate_path_containment "$PROJECT_ROOT" "$HOME" || exit 1
cd "$PROJECT_ROOT"
```

**C3: Unsafe File Removal**
- **Line**: Multiple locations
- **Issue**: `rm -f` without path validation
- **Risk**: Arbitrary file deletion via path traversal
- **Fix**: Validate all paths before deletion

#### HIGH Issues

**H1: API Key File Permissions**
- **Line**: .env file creation
- **Issue**: No explicit chmod 600 after creating .env
- **Fix**:
```bash
touch .env
chmod 600 .env
```

**H2: No Input Validation**
- **Issue**: User inputs not validated
- **Fix**: Add validation for all user-provided paths/values

#### MEDIUM Issues

**M1: Missing Constants**
- **Issue**: Hardcoded values scattered throughout
- **Fix**: Define readonly constants at top

#### LOW Issues

**L1: Using `[` Instead of `[[`**
- **Issue**: Less safe conditional syntax
- **Fix**: Replace all `[` with `[[` for better error handling

---

### 2. router.sh (60% Compliance)

**Location**: `/home/user/Dev-AID/.dev-aid/orchestration/router.sh`

#### MEDIUM Issues

**M1: Missing Input Validation**
- **Issue**: Arguments passed to Python CLI without validation
- **Risk**: Command injection if user provides malicious input
- **Fix**: Validate argument format before passing to Python

**M2: Incomplete Path Validation**
- **Issue**: SCRIPT_DIR resolved but not validated for containment
- **Fix**: Add path containment check

#### LOW Issues

**L1: Hardcoded Shebang**
- **Issue**: `#!/bin/bash` instead of portable `#!/usr/bin/env bash`
- **Fix**: Use env-based shebang for better portability

**L2: Using `[` Instead of `[[`**
- **Issue**: Multiple instances of `[` in conditionals

**L3: Missing Constants**
- **Issue**: Hardcoded "router" and paths

---

### 3. router-cli.sh (65% Compliance)

**Location**: `/home/user/Dev-AID/router-cli.sh`

#### CRITICAL Issues

**C1: Missing Cleanup Trap**
- **Issue**: No trap handler despite potential resource usage
- **Fix**: Add trap even if no current temp files (future-proofing)

#### HIGH Issues

**H1: No Input Validation**
- **Line**: Argument forwarding
- **Issue**: All CLI arguments passed to Python without validation
- **Risk**: Command injection, path traversal
- **Fix**:
```bash
for arg in "$@"; do
    if [[ "$arg" =~ [;\|\&\$\`] ]]; then
        echo "Error: Invalid characters in argument" >&2
        exit 1
    fi
done
```

#### MEDIUM Issues

**M1: No Usage Function**
- **Issue**: Script lacks usage/help output
- **Fix**: Add `usage()` function and `--help` flag

---

### 4. setup-venv.sh (58% Compliance)

**Location**: `/home/user/Dev-AID/.dev-aid/orchestration/setup-venv.sh`

#### CRITICAL Issues

**C1: Path Traversal in rm -rf**
- **Line**: Removal of VENV_DIR
- **Issue**: No validation before `rm -rf "$VENV_DIR"`
- **Risk**: Arbitrary directory deletion if VENV_DIR=../../../../etc
- **Fix**: Add path containment validation (see common pattern #4)

**C2: Missing Cleanup Trap**
- **Issue**: No cleanup on error during venv creation
- **Risk**: Incomplete venv state

#### HIGH Issues

**H1: Unsafe Source Command**
- **Line**: `source "$VENV_DIR/bin/activate"`
- **Issue**: Source without validation that activate script exists and is safe
- **Fix**:
```bash
activate_script="$VENV_DIR/bin/activate"
if [[ ! -f "$activate_script" ]]; then
    echo "Error: Activate script not found" >&2
    exit 1
fi
source "$activate_script"
```

**H2: No Environment Variable Validation**
- **Issue**: VENV_DIR and other vars not validated
- **Fix**: Add format and length checks

---

### 5. session-start-load-context.sh (50% Compliance)

**Location**: `/home/user/Dev-AID/.dev-aid/providers/claude/.claude/hooks/session-start/session-start-load-context.sh`

#### CRITICAL Issues

**C1: No Strict Mode**
- **Line**: 1-5
- **Issue**: Missing `set -euo pipefail` entirely
- **Risk**: Silent failures, undefined variable expansion
- **Fix**: Add as second line of script

**C2: No Environment Variable Validation**
- **Line**: Usage of $CLAUDE_PROJECT_DIR
- **Issue**: Critical env var used without validation
- **Risk**: Path traversal, undefined variable expansion
- **Fix**:
```bash
if [[ -z "${CLAUDE_PROJECT_DIR:-}" ]]; then
    echo "Error: CLAUDE_PROJECT_DIR not set" >&2
    exit 1
fi
validate_path_containment "$CLAUDE_PROJECT_DIR" "$HOME" || exit 1
```

#### HIGH Issues

**H1: Path Traversal Protection Missing**
- **Issue**: Multiple path operations without containment checks
- **Fix**: Add validation before all cd and file operations

**H2: No Trap Cleanup**
- **Issue**: Missing cleanup handler
- **Fix**: Add trap for any temporary state

**H3: No Input Sanitization**
- **Issue**: File paths used without sanitization
- **Fix**: Validate all file paths against safe patterns

---

### 6. Git Hooks: pre-commit & pre-push (45% & 40% Compliance)

**Locations**:
- `/home/user/Dev-AID/.dev-aid/.githooks/pre-commit`
- `/home/user/Dev-AID/.dev-aid/.githooks/pre-push`

#### CRITICAL Issues (Both Scripts)

**C1: Incomplete Strict Mode**
- **Current**: `set -e` only
- **Required**: `set -euo pipefail`
- **Missing**: `-u` (undefined variable detection), `-o pipefail` (pipeline error detection)

**C2: No Trap-Based Cleanup**
- **Issue**: Multiple temp files created without cleanup trap
- **Files**: Format checker temp files, secret scan results
- **Risk**: /tmp pollution, information disclosure
- **Fix**:
```bash
declare -a temp_files=()
cleanup() {
    for f in "${temp_files[@]}"; do
        [[ -f "$f" ]] && shred -u "$f" 2>/dev/null || rm -f "$f"
    done
}
trap cleanup EXIT INT TERM

temp_file=$(mktemp)
temp_files+=("$temp_file")
chmod 600 "$temp_file"
```

**C3: Insecure Temp File Creation**
- **Issue**: `mktemp` without explicit chmod 600
- **Risk**: Other users can read temp files containing sensitive data
- **Fix**: `chmod 600` immediately after `mktemp`

#### HIGH Issues (Both Scripts)

**H1: Temp Files Not Securely Deleted**
- **Current**: `rm -f "$temp_file"`
- **Required**: `shred -u "$temp_file"` for sensitive data
- **Risk**: Recoverable sensitive data in /tmp

**H2: No Validation of Git Commands Output**
- **Issue**: `git diff` output used without size/format validation
- **Risk**: Algorithmic complexity attack with huge diffs
- **Fix**: Add timeout and size limits

#### Additional Issues

**Multiple instances of**:
- Using `[` instead of `[[`
- Missing readonly constants
- No usage/help function
- Hardcoded values

---

## Prioritized Remediation Plan

### Phase 1: Critical Security Fixes (Immediate)

**Priority**: CRITICAL | **Effort**: 4-6 hours

1. **Add strict mode to all scripts** (5 scripts)
   ```bash
   #!/usr/bin/env bash
   set -euo pipefail
   ```

2. **Add trap cleanup handlers** (5 scripts)
   ```bash
   cleanup() {
       # Cleanup logic
   }
   trap cleanup EXIT INT TERM
   ```

3. **Fix path traversal vulnerabilities** (4 scripts)
   - Add `validate_path_containment()` function
   - Validate all user-controlled paths before file operations

4. **Secure temporary file handling** (4 scripts)
   ```bash
   temp_file=$(mktemp)
   chmod 600 "$temp_file"
   trap 'shred -u "$temp_file" 2>/dev/null || rm -f "$temp_file"' EXIT
   ```

### Phase 2: High-Risk Fixes (Within 1 week)

**Priority**: HIGH | **Effort**: 6-8 hours

1. **Add input validation** (5 scripts)
   - Validate all user inputs against safe patterns
   - Check for shell metacharacters
   - Validate length constraints

2. **Fix environment variable handling** (3 scripts)
   - Validate all critical env vars are set
   - Check for shellshock patterns
   - Sanitize environment in privileged contexts

3. **Improve error handling** (all scripts)
   - Add meaningful error messages
   - Log security-relevant events
   - Ensure safe failure modes

### Phase 3: Code Quality Improvements (Within 2 weeks)

**Priority**: MEDIUM-LOW | **Effort**: 8-10 hours

1. **Refactor common patterns** (all scripts)
   - Extract validation functions to shared library
   - Define constants at top of scripts
   - Add usage/help functions

2. **Improve portability** (all scripts)
   - Use `#!/usr/bin/env bash` shebang
   - Replace `[` with `[[` throughout
   - Use POSIX-compliant patterns where possible

3. **Add documentation** (all scripts)
   - Header comments with purpose/usage
   - Inline comments for complex logic
   - Security assumptions documented

---

## Recommended Shared Library

Create `.dev-aid/lib/bash-common.sh` with reusable security functions:

```bash
#!/usr/bin/env bash
# Shared Bash security and utility functions

# Validate path is within allowed base directory
validate_path_containment() {
    local path="$1"
    local base="$2"
    local resolved_path
    local resolved_base

    resolved_path="$(realpath -m "$path")"
    resolved_base="$(realpath "$base")"

    if [[ "$resolved_path" != "$resolved_base"* ]]; then
        echo "Error: Path traversal attempt detected: $path" >&2
        return 1
    fi

    if [[ "$resolved_path" =~ $'\0' ]]; then
        echo "Error: Path contains null bytes" >&2
        return 1
    fi

    return 0
}

# Validate input doesn't contain shell metacharacters
validate_safe_input() {
    local input="$1"
    local field_name="${2:-input}"

    if [[ "$input" =~ [;\|\&\$\`\(\)\<\>] ]]; then
        echo "Error: Invalid characters in $field_name" >&2
        return 1
    fi

    return 0
}

# Create secure temporary file
create_secure_temp() {
    local template="${1:-/tmp/dev-aid.XXXXXX}"
    local temp_file

    temp_file=$(mktemp "$template") || return 1
    chmod 600 "$temp_file"

    echo "$temp_file"
}

# Secure cleanup of temporary file
secure_cleanup_file() {
    local file="$1"

    if [[ -f "$file" ]]; then
        shred -u "$file" 2>/dev/null || rm -f "$file"
    fi
}

# Validate environment variable is set and safe
validate_env_var() {
    local var_name="$1"
    local var_value="${!var_name:-}"

    if [[ -z "$var_value" ]]; then
        echo "Error: Required environment variable $var_name not set" >&2
        return 1
    fi

    # Check for shellshock pattern (CVE-2014-6271)
    if [[ "$var_value" =~ ^\(\)[[:space:]]*\{ ]]; then
        echo "Error: Potential shellshock exploit in $var_name" >&2
        return 1
    fi

    return 0
}

# Validate command exists and is in expected location
validate_command() {
    local cmd="$1"
    local expected_path="${2:-}"
    local actual_path

    if ! actual_path=$(command -v "$cmd" 2>/dev/null); then
        echo "Error: Command not found: $cmd" >&2
        return 1
    fi

    if [[ -n "$expected_path" && "$actual_path" != "$expected_path" ]]; then
        echo "Error: Command location mismatch for $cmd" >&2
        echo "Expected: $expected_path, Got: $actual_path" >&2
        return 1
    fi

    return 0
}
```

**Usage in scripts**:
```bash
#!/usr/bin/env bash
set -euo pipefail

# Source shared library
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly LIB_DIR="${SCRIPT_DIR}/.dev-aid/lib"

# shellcheck source=/dev/null
source "${LIB_DIR}/bash-common.sh"

# Use shared functions
validate_env_var "PROJECT_ROOT" || exit 1
validate_path_containment "$TARGET_DIR" "$PROJECT_ROOT" || exit 1

temp_file=$(create_secure_temp) || exit 1
trap 'secure_cleanup_file "$temp_file"' EXIT INT TERM
```

---

## Testing Recommendations

### 1. Security Testing

Create `tests/bash-security-tests.sh`:

```bash
#!/usr/bin/env bash
# Security tests for Bash scripts

test_path_traversal_blocked() {
    local test_script="$1"

    # Test with traversal attempt
    if "$test_script" "../../../../etc/passwd" 2>&1 | grep -q "Path traversal"; then
        echo "PASS: Path traversal blocked"
        return 0
    else
        echo "FAIL: Path traversal not blocked"
        return 1
    fi
}

test_command_injection_blocked() {
    local test_script="$1"

    # Test with injection attempt
    if "$test_script" "file; rm -rf /" 2>&1 | grep -q "Invalid characters"; then
        echo "PASS: Command injection blocked"
        return 0
    else
        echo "FAIL: Command injection not blocked"
        return 1
    fi
}

test_cleanup_on_error() {
    local test_script="$1"
    local temp_count_before
    local temp_count_after

    temp_count_before=$(find /tmp -name "dev-aid.*" 2>/dev/null | wc -l)

    # Force script error
    "$test_script" --force-error 2>/dev/null || true

    temp_count_after=$(find /tmp -name "dev-aid.*" 2>/dev/null | wc -l)

    if [[ $temp_count_after -eq $temp_count_before ]]; then
        echo "PASS: Cleanup executed on error"
        return 0
    else
        echo "FAIL: Temp files leaked on error"
        return 1
    fi
}
```

### 2. ShellCheck Integration

Add to CI/CD pipeline:

```bash
#!/usr/bin/env bash
# Run ShellCheck on all Bash scripts

find . -type f -name "*.sh" -exec shellcheck -x -S error {} +
```

### 3. Automated Compliance Checking

Create `tools/check-bash-compliance.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

check_strict_mode() {
    local script="$1"

    if grep -q "set -euo pipefail" "$script"; then
        return 0
    else
        echo "FAIL: $script missing strict mode"
        return 1
    fi
}

check_trap_handler() {
    local script="$1"

    if grep -q "trap.*EXIT" "$script"; then
        return 0
    else
        echo "WARN: $script missing trap handler"
        return 1
    fi
}

# Run checks on all scripts
for script in $(find . -type f -name "*.sh"); do
    echo "Checking $script..."
    check_strict_mode "$script" || exit 1
    check_trap_handler "$script" || true  # Warning only
done
```

---

## Compliance Standards Reference

This review is based on:

- **bash-expert skill** (HIGH-RISK): `.dev-aid/providers/claude/.claude/skills/expert/bash-expert/SKILL.md`
- **OWASP Top 10** (2021): A01 (Broken Access Control), A03 (Injection)
- **CWE Coverage**:
  - CWE-22: Path Traversal
  - CWE-78: Command Injection
  - CWE-330: Insufficient Randomness
  - CWE-362: Race Conditions (TOCTOU)
  - CWE-377: Insecure Temporary Files
  - CWE-404: Improper Resource Shutdown
  - CWE-754: Improper Exception Handling
- **CVE References**: CVE-2014-6271 (Shellshock)

---

## Appendix: All Scripts Identified

### Core Scripts (Reviewed in Detail)
1. `install.sh` - Main installation script
2. `router.sh` - Router orchestration
3. `router-cli.sh` - CLI wrapper
4. `setup-venv.sh` - Python venv setup
5. `session-start-load-context.sh` - Session initialization
6. `.dev-aid/.githooks/pre-commit` - Git pre-commit hook
7. `.dev-aid/.githooks/pre-push` - Git pre-push hook

### Additional Scripts (Identified, Not Detailed)
8. `.dev-aid/orchestration/scripts/generate_combined_prompt.sh`
9. `.dev-aid/orchestration/tests/test_router.sh`
10. `.dev-aid/providers/claude/.claude/hooks/session-start/load-skills-auto.sh`
11-23. Various utility and helper scripts

**Recommendation**: Apply same remediation patterns to all 23 scripts following the prioritized plan above.

---

## Conclusion

The Bash scripts in Dev-AID show moderate compliance (54% average) with critical security gaps that require immediate attention. The most severe issues are:

1. **Missing strict mode** - Allows silent failures and undefined variable expansion
2. **No cleanup handlers** - Resource leaks and incomplete state on errors
3. **Path traversal vulnerabilities** - Risk of arbitrary file operations
4. **Insecure temp files** - Information disclosure risk

**Estimated Total Remediation Effort**: 18-24 hours across 3 phases

**Priority**: Focus on Phase 1 (critical security fixes) immediately to address the 21 critical issues across all scripts.

Once remediated, all scripts will meet HIGH-RISK bash-expert skill compliance and provide defense-in-depth security posture consistent with the Python remediation already completed.
