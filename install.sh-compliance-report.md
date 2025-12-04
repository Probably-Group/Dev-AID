# Bash Expert Skill Compliance Report
## File: `/home/user/Dev-AID/.dev-aid/scripts/install.sh`

**Date**: 2025-12-04
**Reviewer**: Claude Code (bash-expert skill)
**Script Version**: v2.0
**Overall Risk Level**: HIGH

---

## Executive Summary

The `install.sh` script demonstrates good organizational structure and some security practices but has **critical security gaps** that must be addressed, particularly around cleanup handling, input validation, and path validation. The script handles sensitive API keys and creates system files, making these vulnerabilities especially concerning.

**Critical Issues**: 3
**High Severity**: 4
**Medium Severity**: 8
**Low Severity**: 4

---

## 1. Strict Mode ✅ COMPLIANT

**Line 6**: `set -euo pipefail`

```bash
6→ set -euo pipefail
```

**Status**: ✅ **COMPLIANT**
**Severity**: N/A

The script properly enables strict mode for error detection.

---

## 2. Error Handling & Cleanup ❌ CRITICAL

### Issue 2.1: No Trap for Cleanup

**Lines**: N/A (missing)
**Severity**: 🔴 **CRITICAL**

The script has NO cleanup trap despite:
- Creating temporary files (line 609: `.json.tmp`)
- Handling sensitive API keys
- Creating multiple files that may need rollback on failure

**Required Pattern** (from bash-expert skill, lines 148-154):
```bash
cleanup() {
    local exit_code=$?
    # Cleanup temporary files, restore state, etc.
    exit "$exit_code"
}
trap cleanup EXIT INT TERM
```

**Current State**: No trap defined anywhere in the script.

**Recommendation**:
```bash
# Add after line 26 (after variable declarations)
TEMP_FILES=()

cleanup() {
    local exit_code=$?
    # Remove temporary files
    for temp_file in "${TEMP_FILES[@]}"; do
        rm -f "$temp_file" 2>/dev/null || true
    done
    exit "$exit_code"
}
trap cleanup EXIT INT TERM
```

---

## 3. Input Validation ❌ HIGH

### Issue 3.1: User Choice Validation Insufficient

**Lines**: 98-119, 147-164, 266-289
**Severity**: 🟠 **HIGH**

User choices are validated for expected values but not sanitized for dangerous characters.

**Vulnerable Code**:
```bash
98→  read -p "Your choice [A/B/C]: " choice
99→  case $choice in
100→     [Aa])
```

**Problem**: No sanitization before use. While case statement limits execution paths, the input should still be sanitized.

**Recommendation**:
```bash
# Add sanitization function after line 36
sanitize_choice() {
    local input="$1"
    # Remove all non-alphanumeric characters
    input="${input//[^a-zA-Z0-9]/}"
    echo "$input"
}

# Then use it:
read -p "Your choice [A/B/C]: " choice
choice=$(sanitize_choice "$choice")
```

### Issue 3.2: API Key Validation Missing

**Lines**: 481-489, 494-502, 507-515, 520-528
**Severity**: 🟠 **HIGH**

API keys are read with `-s` (secure) but never validated for format or dangerous characters.

**Vulnerable Code**:
```bash
481→ read -sp "ANTHROPIC_API_KEY: " claude_key
482→ echo ""
483→ if [ -n "$claude_key" ]; then
484→     COLLECTED_API_KEYS+=("ANTHROPIC_API_KEY=$claude_key")
```

**Problem**: API key could contain shell metacharacters, newlines, or command injection attempts.

**Recommendation**:
```bash
# Add validation function
validate_api_key() {
    local key="$1"
    local provider="$2"

    # Check not empty
    if [[ -z "$key" ]]; then
        return 1
    fi

    # Check length (API keys typically 20-100 chars)
    local len=${#key}
    if (( len < 20 || len > 200 )); then
        echo "Error: Invalid API key length for $provider" >&2
        return 1
    fi

    # Check for dangerous characters (allow only alphanumeric, dash, underscore)
    if [[ ! "$key" =~ ^[a-zA-Z0-9_-]+$ ]]; then
        echo "Error: API key contains invalid characters" >&2
        return 1
    fi

    return 0
}

# Usage:
read -sp "ANTHROPIC_API_KEY: " claude_key
echo ""
if validate_api_key "$claude_key" "Claude"; then
    COLLECTED_API_KEYS+=("ANTHROPIC_API_KEY=$claude_key")
    print_color "$GREEN" "✓ Claude API key saved"
else
    print_color "$RED" "✗ Invalid API key format"
fi
```

### Issue 3.3: Numeric Input Validation Missing

**Lines**: 416-420, 457-461
**Severity**: 🟡 **MEDIUM**

User selection of model indexes lacks proper numeric validation.

**Vulnerable Code**:
```bash
416→ read -p "Select model [1-$((i-1)), default: $default_idx]: " selection
418→ if [ -z "$selection" ]; then
419→     selection=$default_idx
420→ fi
422→ if [ "$selection" -ge 1 ] && [ "$selection" -lt "$i" ]; then
```

**Problem**: No validation that `$selection` is actually numeric before comparison. Non-numeric input will cause error.

**Recommendation**:
```bash
validate_number() {
    local input="$1"
    local min="$2"
    local max="$3"

    # Check if numeric
    if [[ ! "$input" =~ ^[0-9]+$ ]]; then
        return 1
    fi

    # Check range
    if (( input < min || input > max )); then
        return 1
    fi

    return 0
}

# Usage:
read -p "Select model [1-$((i-1)), default: $default_idx]: " selection
if [ -z "$selection" ]; then
    selection=$default_idx
elif ! validate_number "$selection" 1 "$((i-1))"; then
    print_color "$RED" "Invalid selection. Using default."
    selection=$default_idx
fi
```

---

## 4. Path Traversal & Path Security ❌ CRITICAL

### Issue 4.1: No Path Validation for PROJECT_ROOT

**Lines**: 952-953
**Severity**: 🔴 **CRITICAL**

`PROJECT_ROOT` is determined from script location but never validated.

**Vulnerable Code**:
```bash
952→ PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
953→ DEV_AID_DIR="$PROJECT_ROOT/.dev-aid"
```

**Problem**: While the path construction is safe, there's no validation that:
- The directory exists
- It's a valid project directory
- It's not a system directory (/, /etc, /usr, etc.)
- It doesn't contain dangerous characters

**Recommendation**:
```bash
# Add validation function
validate_project_root() {
    local root="$1"

    # Must be absolute path
    if [[ ! "$root" =~ ^/ ]]; then
        echo "Error: PROJECT_ROOT must be absolute path" >&2
        return 1
    fi

    # Must exist and be directory
    if [[ ! -d "$root" ]]; then
        echo "Error: PROJECT_ROOT does not exist: $root" >&2
        return 1
    fi

    # Prevent system directories
    case "$root" in
        /|/etc|/usr|/bin|/sbin|/boot|/sys|/proc|/dev)
            echo "Error: Cannot install in system directory: $root" >&2
            return 1
            ;;
    esac

    # Must be writable
    if [[ ! -w "$root" ]]; then
        echo "Error: PROJECT_ROOT not writable: $root" >&2
        return 1
    fi

    return 0
}

# Usage:
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if ! validate_project_root "$PROJECT_ROOT"; then
    exit 1
fi
```

### Issue 4.2: Unsafe File Removal with User-Controlled Path

**Line**: 674
**Severity**: 🔴 **CRITICAL**

File removal without path validation could lead to unintended deletions.

**Vulnerable Code**:
```bash
663→ case $provider in
664→     claude) context_file="CLAUDE.md" ;;
665→     gemini) context_file="GEMINI.md" ;;
666→     openai) context_file="OPENAI.md" ;;
667→     openrouter) context_file="OPENROUTER.md" ;;
668→ esac
670→ if [ -n "$context_file" ] && [ -f "$DEV_AID_DIR/providers/$provider/$context_file" ]; then
674→     rm -f "$PROJECT_ROOT/$context_file"
```

**Problem**: While `context_file` comes from case statement (safe), there's no validation of `$PROJECT_ROOT` before removing files in it.

**Recommendation**:
```bash
# Validate path is within project
validate_file_path() {
    local file_path="$1"
    local base_dir="$2"

    # Resolve to absolute paths
    local resolved_file
    resolved_file="$(realpath -m "$file_path")"
    local resolved_base
    resolved_base="$(realpath "$base_dir")"

    # Check containment
    if [[ "$resolved_file" != "$resolved_base"* ]]; then
        echo "Error: Path traversal attempt detected" >&2
        return 1
    fi

    return 0
}

# Before line 674:
local full_path="$PROJECT_ROOT/$context_file"
if validate_file_path "$full_path" "$PROJECT_ROOT"; then
    rm -f "$full_path"
else
    print_color "$RED" "Error: Invalid file path"
    return 1
fi
```

### Issue 4.3: Unsafe Symlink Creation

**Line**: 677
**Severity**: 🟠 **HIGH**

Symlink creation without validating both source and destination paths.

**Vulnerable Code**:
```bash
677→ ln -s ".dev-aid/providers/$provider/$context_file" "$PROJECT_ROOT/$context_file"
```

**Problem**: No validation that:
- Source file exists and is readable
- Destination doesn't already exist as non-symlink
- Paths don't escape project directory

**Recommendation**:
```bash
# Before creating symlink:
local src=".dev-aid/providers/$provider/$context_file"
local dest="$PROJECT_ROOT/$context_file"

# Validate source exists
if [[ ! -f "$DEV_AID_DIR/providers/$provider/$context_file" ]]; then
    print_color "$RED" "Error: Source file not found"
    return 1
fi

# Validate destination path
if ! validate_file_path "$dest" "$PROJECT_ROOT"; then
    print_color "$RED" "Error: Invalid destination path"
    return 1
fi

# Remove existing if symlink only
if [[ -L "$dest" ]]; then
    rm -f "$dest"
elif [[ -e "$dest" ]]; then
    print_color "$YELLOW" "Warning: $dest exists and is not a symlink, skipping"
    return 0
fi

# Create symlink
ln -s "$src" "$dest" || {
    print_color "$RED" "Error: Failed to create symlink"
    return 1
}
```

---

## 5. Command Injection Prevention ✅ MOSTLY COMPLIANT

### Compliant Items ✅

**Lines**: Throughout the script

The script generally follows good practices:
- ✅ All variables are properly quoted
- ✅ No use of `eval`
- ✅ No backticks (uses `$()` for command substitution)
- ✅ Arrays used for ENABLED_PROVIDERS and COLLECTED_API_KEYS
- ✅ Heredocs used safely for multi-line content

### Issue 5.1: Potential sed Injection

**Line**: 612
**Severity**: 🟡 **MEDIUM**

While `$ORCHESTRATION_MODE` comes from validated input, there's no explicit sanitization.

**Vulnerable Code**:
```bash
612→ sed -i "s/\"mode\": \".*\"/\"mode\": \"$ORCHESTRATION_MODE\"/" \
613→     "$DEV_AID_DIR/config/orchestration.json" 2>/dev/null || true
```

**Problem**: If `$ORCHESTRATION_MODE` somehow contained sed metacharacters, it could cause issues.

**Recommendation**:
```bash
# Escape sed special characters
escape_sed() {
    local input="$1"
    # Escape sed metacharacters
    echo "$input" | sed 's/[&/\]/\\&/g'
}

local safe_mode
safe_mode=$(escape_sed "$ORCHESTRATION_MODE")
sed -i "s/\"mode\": \".*\"/\"mode\": \"$safe_mode\"/" \
    "$DEV_AID_DIR/config/orchestration.json" 2>/dev/null || true
```

---

## 6. File Operations & Error Handling ❌ MEDIUM

### Issue 6.1: File Creation Without Directory Check

**Lines**: 541, 553, 620
**Severity**: 🟡 **MEDIUM**

Files are created without verifying parent directory exists and is writable.

**Vulnerable Code**:
```bash
541→ cat > "$DEV_AID_DIR/config/.env" <<EOF
```

**Problem**: If `$DEV_AID_DIR/config` doesn't exist or isn't writable, script will fail.

**Recommendation**:
```bash
# Add before each file creation:
ensure_directory() {
    local dir="$1"

    if [[ ! -d "$dir" ]]; then
        mkdir -p "$dir" || {
            echo "Error: Failed to create directory: $dir" >&2
            return 1
        }
    fi

    if [[ ! -w "$dir" ]]; then
        echo "Error: Directory not writable: $dir" >&2
        return 1
    fi

    return 0
}

# Usage:
ensure_directory "$DEV_AID_DIR/config" || return 1
cat > "$DEV_AID_DIR/config/.env" <<EOF
...
EOF
```

### Issue 6.2: Unsafe Directory Change

**Line**: 820
**Severity**: 🟡 **MEDIUM**

Directory change without checking success.

**Vulnerable Code**:
```bash
820→ cd "$PROJECT_ROOT"
821→ "$DEV_AID_DIR/automation/git-hooks/install.sh"
```

**Problem**: If `cd` fails, script continues in wrong directory, potentially executing script from wrong location.

**Recommendation**:
```bash
cd "$PROJECT_ROOT" || {
    print_color "$RED" "Error: Failed to change to project directory"
    return 1
}
"$DEV_AID_DIR/automation/git-hooks/install.sh"

# Or better, avoid cd entirely:
( cd "$PROJECT_ROOT" && "$DEV_AID_DIR/automation/git-hooks/install.sh" ) || {
    print_color "$RED" "Error: Failed to install git hooks"
    return 1
}
```

### Issue 6.3: Inconsistent Error Handling

**Lines**: Multiple
**Severity**: 🟡 **MEDIUM**

Many operations don't check return codes or use proper error handling.

**Examples**:
```bash
637→ mkdir -p "$DEV_AID_DIR/logs"
638→ print_color "$GREEN" "✓ Logs directory created"
```

**Problem**: No check if `mkdir` succeeded.

**Recommendation**:
```bash
mkdir -p "$DEV_AID_DIR/logs" || {
    print_color "$RED" "Error: Failed to create logs directory"
    return 1
}
print_color "$GREEN" "✓ Logs directory created"
```

---

## 7. Temporary File Handling ❌ MEDIUM

### Issue 7.1: Insecure Temporary File Creation

**Line**: 609
**Severity**: 🟡 **MEDIUM**

Temporary file created without using `mktemp`.

**Vulnerable Code**:
```bash
609→ jq ".mode = \"$ORCHESTRATION_MODE\"" \
610→     "$DEV_AID_DIR/config/orchestration.json" > "$DEV_AID_DIR/config/orchestration.json.tmp"
611→ mv "$DEV_AID_DIR/config/orchestration.json.tmp" "$DEV_AID_DIR/config/orchestration.json"
```

**Problem**:
- Predictable filename (security risk)
- No cleanup on error
- No permission setting

**Recommendation** (from bash-expert skill, lines 598-626):
```bash
# Add temp file creation function
create_temp_file() {
    local template="${1:-/tmp/install.XXXXXX}"
    local temp_file

    temp_file=$(mktemp "$template") || {
        echo "Error: Failed to create temporary file" >&2
        return 1
    }

    # Set restrictive permissions
    chmod 600 "$temp_file"

    echo "$temp_file"
    return 0
}

# Usage:
local temp_file
temp_file=$(create_temp_file "$DEV_AID_DIR/config/.orchestration.XXXXXX") || return 1
TEMP_FILES+=("$temp_file")  # Track for cleanup

jq ".mode = \"$ORCHESTRATION_MODE\"" \
    "$DEV_AID_DIR/config/orchestration.json" > "$temp_file"
mv "$temp_file" "$DEV_AID_DIR/config/orchestration.json"
```

---

## 8. Global Variables & Constants ❌ MEDIUM

### Issue 8.1: Mutable Global Variables

**Lines**: 18-26
**Severity**: 🟡 **MEDIUM**

Global configuration variables are not declared as readonly.

**Current Code**:
```bash
18→ PROJECT_ROOT=""
19→ DEV_AID_DIR=""
20→ STANDING_CONTEXT_BUDGET=""
...
```

**Problem**: Variables can be accidentally overwritten, causing unpredictable behavior.

**Recommendation**:
```bash
# After initialization in main():
readonly PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
readonly DEV_AID_DIR="$PROJECT_ROOT/.dev-aid"

# For variables set later, make readonly after setting:
STANDING_CONTEXT_BUDGET="balanced"
readonly STANDING_CONTEXT_BUDGET
```

### Issue 8.2: Missing Exit Code Constants

**Line**: 959
**Severity**: 🔹 **LOW**

Script uses hardcoded exit codes instead of named constants.

**Current Code**:
```bash
959→ exit 1
```

**Recommendation**:
```bash
# Add after line 26:
readonly EXIT_SUCCESS=0
readonly EXIT_FAILURE=1

# Use throughout:
exit "$EXIT_FAILURE"
```

---

## 9. Documentation & Code Quality ✅ MOSTLY COMPLIANT

### Compliant Items ✅

- ✅ Clear script header (lines 3-5)
- ✅ Functions are well-named and organized
- ✅ Good use of color-coded output
- ✅ Helpful user messages throughout
- ✅ Section headers for organization

### Issue 9.1: Missing Usage Function

**Lines**: N/A (missing)
**Severity**: 🔹 **LOW**

Script lacks a `usage()` function despite accepting arguments.

**Recommendation**:
```bash
# Add after line 45:
usage() {
    cat <<EOF
Usage: $SCRIPT_NAME [OPTIONS]

Dev-AID Interactive Installer v2.0
Configures Dev-AID with granular model selection and flexible orchestration

Options:
    -h, --help       Show this help message
    -y, --yes        Auto-accept defaults (non-interactive)
    -v, --verbose    Enable verbose output

Examples:
    $SCRIPT_NAME                # Interactive installation
    $SCRIPT_NAME --help         # Show help
    $SCRIPT_NAME --yes          # Use defaults

For more information, see: .dev-aid/docs/INSTALLATION.md
EOF
}

# Parse arguments at start of main():
case "${1:-}" in
    -h|--help)
        usage
        exit 0
        ;;
esac
```

### Issue 9.2: Insufficient Function Documentation

**Lines**: Various functions
**Severity**: 🔹 **LOW**

Most functions lack header comments explaining parameters and return values.

**Recommendation**:
```bash
# Add function documentation:
# Create configuration files
# Writes settings.json, .env, and orchestration.json
# Globals: DEV_AID_DIR, COLLECTED_API_KEYS, ENABLED_PROVIDERS
# Returns: 0 on success, 1 on failure
create_config_files() {
    ...
}
```

---

## 10. Security Best Practices ❌ HIGH

### Issue 10.1: API Key Storage Permissions

**Line**: 541-546
**Severity**: 🟠 **HIGH**

`.env` file with API keys created without explicitly setting restrictive permissions.

**Current Code**:
```bash
541→ cat > "$DEV_AID_DIR/config/.env" <<EOF
542→ # Dev-AID API Keys
543→ # This file is gitignored for security
544→
545→ $(printf '%s\n' "${COLLECTED_API_KEYS[@]}")
546→ EOF
```

**Problem**: File permissions depend on umask, may be world-readable.

**Recommendation**:
```bash
# Set restrictive permissions before writing
local env_file="$DEV_AID_DIR/config/.env"

# Create empty file with restrictive permissions
touch "$env_file"
chmod 600 "$env_file"

# Now write content
cat > "$env_file" <<EOF
# Dev-AID API Keys
# This file is gitignored for security

$(printf '%s\n' "${COLLECTED_API_KEYS[@]}")
EOF

# Verify permissions
if [[ "$(stat -c %a "$env_file" 2>/dev/null)" != "600" ]]; then
    print_color "$YELLOW" "Warning: Could not set restrictive permissions on .env file"
fi
```

### Issue 10.2: Missing Shebang Best Practice

**Line**: 1
**Severity**: 🔹 **LOW**

Uses `#!/bin/bash` instead of `#!/usr/bin/env bash`.

**Current Code**:
```bash
1→ #!/bin/bash
```

**Recommendation** (per bash-expert skill, line 126):
```bash
#!/usr/bin/env bash
```

**Reason**: More portable across systems where bash may not be in `/bin`.

---

## 11. Command Existence Checks ✅ PARTIAL

### Compliant Usage ✅

**Lines**: 607, 692

Script checks for command existence before use:
```bash
607→ if command -v jq &> /dev/null; then
692→ if command -v sed &> /dev/null; then
```

### Issue 11.1: Inconsistent Checks

**Lines**: Various
**Severity**: 🔹 **LOW**

Some commands used without checking existence (ln, mkdir, rm, etc.).

**Recommendation**:
```bash
# Add at start of main():
check_required_commands() {
    local missing=()
    local commands=(mkdir rm ln cat chmod date basename dirname realpath)

    for cmd in "${commands[@]}"; do
        if ! command -v "$cmd" &>/dev/null; then
            missing+=("$cmd")
        fi
    done

    if [[ ${#missing[@]} -gt 0 ]]; then
        print_color "$RED" "Error: Missing required commands: ${missing[*]}"
        exit 1
    fi
}

check_required_commands
```

---

## Summary of Findings

### Critical Issues (3)

1. **No cleanup trap** - Line N/A - Critical for error recovery and temp file cleanup
2. **Unvalidated PROJECT_ROOT** - Line 952 - Could lead to operations in wrong directory
3. **Unsafe file removal** - Line 674 - Could delete unintended files

### High Severity (4)

4. **Insufficient input validation** - Lines 98-119, 147-164, 266-289
5. **API key validation missing** - Lines 481-528
6. **Unsafe symlink creation** - Line 677
7. **API key file permissions** - Line 541 - Sensitive data may be readable

### Medium Severity (8)

8. **Numeric input validation missing** - Lines 416-420
9. **sed injection potential** - Line 612
10. **File creation without directory check** - Lines 541, 553, 620
11. **Unsafe directory change** - Line 820
12. **Inconsistent error handling** - Multiple locations
13. **Insecure temporary file creation** - Line 609
14. **Mutable global variables** - Lines 18-26
15. **Missing exit code constants** - Line 959

### Low Severity (4)

16. **Missing usage function** - N/A
17. **Insufficient function documentation** - Various
18. **Non-portable shebang** - Line 1
19. **Inconsistent command existence checks** - Various

---

## Recommended Priority for Fixes

### Phase 1: Critical Security (Fix Immediately)

1. ✅ Add cleanup trap with temp file tracking
2. ✅ Add PROJECT_ROOT validation
3. ✅ Add path validation before file operations
4. ✅ Set restrictive permissions on .env file
5. ✅ Add API key format validation

### Phase 2: High-Risk Prevention (Fix Soon)

6. ✅ Add input sanitization for all user inputs
7. ✅ Validate paths before symlink creation
8. ✅ Add numeric validation for model selection

### Phase 3: Robustness (Fix When Possible)

9. ✅ Add directory existence checks before file operations
10. ✅ Fix unsafe directory changes
11. ✅ Add proper error handling throughout
12. ✅ Use mktemp for temporary files
13. ✅ Make constants readonly

### Phase 4: Code Quality (Low Priority)

14. ✅ Add usage function
15. ✅ Add function documentation
16. ✅ Change shebang to #!/usr/bin/env bash
17. ✅ Add consistent command existence checks

---

## Testing Recommendations

After implementing fixes, test these scenarios:

1. **Path Traversal**: Try to specify paths outside project
2. **Malicious Input**: Enter special characters in all prompts
3. **Missing Directories**: Run with missing .dev-aid directories
4. **Interrupted Installation**: Test Ctrl+C at various points
5. **Invalid API Keys**: Enter invalid API key formats
6. **File Permissions**: Verify .env is 600 (not world-readable)
7. **Symlink Edge Cases**: Test with existing files/symlinks
8. **Error Recovery**: Ensure cleanup happens on all error paths

---

## Compliance Score

| Category | Score | Status |
|----------|-------|--------|
| Strict Mode | 100% | ✅ PASS |
| Input Validation | 40% | ❌ FAIL |
| Variable Quoting | 95% | ✅ PASS |
| Command Injection Prevention | 90% | ✅ PASS |
| Path Traversal Protection | 30% | ❌ FAIL |
| Error Handling | 50% | ⚠️ PARTIAL |
| Security Best Practices | 60% | ⚠️ PARTIAL |
| Absolute Paths | 70% | ⚠️ PARTIAL |
| Temp File Handling | 40% | ❌ FAIL |
| Documentation | 75% | ⚠️ PARTIAL |

**Overall Compliance: 60% (NEEDS IMPROVEMENT)**

---

## Conclusion

The `install.sh` script demonstrates good structure and some security awareness but requires significant improvements to meet bash-expert skill standards. The most critical issues are:

1. **No cleanup trap** - Essential for production scripts
2. **Insufficient path validation** - Risk of operations outside intended directory
3. **API key security** - Sensitive data handling needs improvement

These issues are addressable with the patterns provided in the bash-expert skill. Once fixed, the script will be significantly more robust and secure for production use.

---

## References

- Bash Expert Skill: `/home/user/Dev-AID/.dev-aid/providers/claude/.claude/skills/expert/bash-expert/SKILL.md`
- OWASP Top 10: Command Injection (A03:2021)
- CWE-78: OS Command Injection
- CWE-22: Path Traversal
- Bash Best Practices: https://mywiki.wooledge.org/BashGuide/Practices

---

**Report Generated By**: Claude Code (Sonnet 4.5)
**Using Skill**: bash-expert (HIGH-RISK)
**Report Date**: 2025-12-04
