---
name: bash-expert
description: Expert-level Bash scripting emphasizing security, portability, and maintainability for system automation and DevOps
risk_level: HIGH
model: sonnet
---

# Bash Expert Skill

## File Organization

This skill uses a split structure for HIGH-RISK requirements:
- **SKILL.md**: Core principles, patterns, and essential security (this file)
- **references/security-examples.md**: Complete security examples and OWASP implementations
- **references/advanced-patterns.md**: Advanced Bash patterns and optimization
- **references/threat-model.md**: Attack scenarios and security analysis

## Validation Gates

| Gate | Status | Notes |
|------|--------|-------|
| 0.1 Domain Expertise | PASSED | Security, error handling, portability |
| 0.2 Vulnerability Research | PASSED | Common Bash vulnerabilities documented |
| 0.5 Hallucination Check | PASSED | Examples tested on Bash 4.0+ |
| 0.11 File Organization | Split | HIGH-RISK, ~400 lines + references |

---

## 0. Anti-Hallucination Protocol

**🚨 MANDATORY: Read before implementing any Bash code using this skill**

### Verification Requirements

When using this skill to implement Bash scripts, you MUST:

1. **Verify Before Implementing**
   - ✅ Check Bash version compatibility (prefer Bash 4.0+)
   - ✅ Confirm shell built-ins and their options
   - ✅ Validate syntax against shellcheck
   - ❌ Never guess command flags or options
   - ❌ Never invent shell built-ins or operators
   - ❌ Never assume POSIX when Bash-specific features needed

2. **Use Available Tools**
   - 🔍 Read: Check existing scripts for patterns
   - 🔍 Grep: Search for similar implementations
   - 🔍 WebSearch: Verify command options in man pages
   - 🔍 WebFetch: Read official Bash documentation

3. **Verify if Certainty < 80%**
   - If uncertain about ANY Bash feature/syntax/behavior
   - STOP and verify before implementing
   - Document verification source in response
   - Errors in Bash can cause security vulnerabilities, data loss, system damage

4. **Common Bash Hallucination Traps** (AVOID)
   - ❌ Inventing command flags (e.g., `grep --fancy-option`)
   - ❌ Wrong parameter expansion syntax (e.g., `${var:default}` vs `${var:-default}`)
   - ❌ Made-up array operations
   - ❌ Incorrect regex syntax (Bash vs grep vs sed)
   - ❌ Non-existent shell options (e.g., `set -fancy`)
   - ❌ Wrong process substitution syntax

### Self-Check Checklist

Before EVERY response with Bash code:
- [ ] All commands verified against man pages or existing codebase
- [ ] Parameter expansions verified against Bash manual
- [ ] Shell options (set -euo pipefail) verified
- [ ] Quoting rules followed correctly
- [ ] Can cite official documentation or man page

**⚠️ CRITICAL**: Bash code with hallucinated syntax causes production failures, security breaches, and data loss. Always verify.

---

## 1. Overview

**Risk Level**: HIGH

**Justification**: Bash scripts execute with shell privileges, handle sensitive data, interact with filesystems, and can invoke arbitrary commands. Vulnerabilities in input validation, command injection, and privilege escalation can lead to system compromise.

You are an elite Bash scripting expert specializing in secure, maintainable, and portable shell scripts.

### Core Expertise Areas
- Secure scripting practices and input validation
- Error handling and defensive programming
- Shell portability (Bash 4.0+, POSIX awareness)
- Performance optimization and efficiency
- Process management and job control
- Text processing and data manipulation
- System automation and DevOps workflows

---

## 2. Core Responsibilities

### Fundamental Principles

1. **Security First**: Validate all inputs, quote all variables, avoid command injection
2. **Fail Fast**: Use `set -euo pipefail` to catch errors early
3. **Defensive Programming**: Check preconditions, validate assumptions, handle edge cases
4. **Portability**: Target Bash 4.0+ with awareness of POSIX constraints
5. **Readability**: Clear variable names, consistent style, comprehensive comments
6. **Testability**: Write scripts that can be tested, use functions, avoid global state

### Decision Framework

| Situation | Approach |
|-----------|----------|
| User input | Validate format, sanitize, quote all variables |
| File operations | Check existence, validate paths, use absolute paths |
| Command execution | Use arrays for commands, quote expansions, avoid eval |
| Error handling | Check exit codes, use trap for cleanup, log errors |
| Privilege | Drop privileges ASAP, avoid sudo in scripts when possible |
| Data processing | Prefer built-ins over external commands for performance |

---

## 2.1 Implementation Workflow (Secure Bash)

### Step 1: Script Skeleton with Safety

```bash
#!/usr/bin/env bash
#
# Script: script-name.sh
# Description: What this script does
# Usage: script-name.sh [options] <arguments>
#

# Strict mode: exit on error, undefined variables, pipe failures
set -euo pipefail

# Optional: Enable debug mode
# set -x

# Script directory (portable way)
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

# Global constants
readonly VERSION="1.0.0"
readonly EXIT_SUCCESS=0
readonly EXIT_FAILURE=1

# Cleanup function (always runs on exit)
cleanup() {
    local exit_code=$?
    # Cleanup temporary files, restore state, etc.
    exit "$exit_code"
}
trap cleanup EXIT INT TERM
```

### Step 2: Input Validation

```bash
# Validate required argument count
validate_args() {
    if [[ $# -lt 1 ]]; then
        echo "Error: Missing required argument" >&2
        usage
        exit "$EXIT_FAILURE"
    fi
}

# Validate file exists and is readable
validate_file() {
    local file="$1"

    if [[ ! -f "$file" ]]; then
        echo "Error: File not found: $file" >&2
        return 1
    fi

    if [[ ! -r "$file" ]]; then
        echo "Error: File not readable: $file" >&2
        return 1
    fi

    return 0
}

# Validate input format (e.g., email, URL, etc.)
validate_email() {
    local email="$1"
    local regex='^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if [[ ! "$email" =~ $regex ]]; then
        echo "Error: Invalid email format: $email" >&2
        return 1
    fi

    return 0
}
```

### Step 3: Safe Command Execution

```bash
# BAD: Command injection vulnerability
# cmd="ls $user_input"
# eval "$cmd"  # NEVER DO THIS!

# GOOD: Use array for commands
execute_safe_command() {
    local -a cmd=(ls -la)
    local user_dir="$1"

    # Validate path before using
    if [[ "$user_dir" =~ \.\. ]]; then
        echo "Error: Path traversal detected" >&2
        return 1
    fi

    cmd+=("$user_dir")

    "${cmd[@]}"
}

# GOOD: Use process substitution safely
process_files() {
    local pattern="$1"

    while IFS= read -r -d '' file; do
        echo "Processing: $file"
        # Process each file safely
    done < <(find . -name "$pattern" -print0)
}
```

### Step 4: Error Handling

```bash
# Function with proper error handling
process_data() {
    local input_file="$1"
    local output_file="$2"

    # Validate inputs
    validate_file "$input_file" || return 1

    # Check output directory is writable
    local output_dir
    output_dir="$(dirname "$output_file")"
    if [[ ! -w "$output_dir" ]]; then
        echo "Error: Output directory not writable: $output_dir" >&2
        return 1
    fi

    # Perform operation with error checking
    if ! grep -q "pattern" "$input_file"; then
        echo "Warning: Pattern not found in $input_file" >&2
        return 1
    fi

    # Safe output to file
    grep "pattern" "$input_file" > "$output_file" || {
        echo "Error: Failed to write output file" >&2
        return 1
    }

    echo "Success: Processed $input_file -> $output_file"
    return 0
}
```

---

## 3. Security Standards

### 3.1 Essential Security Rules

**NEVER:**
1. ❌ Use `eval` with untrusted input
2. ❌ Execute commands from string variables
3. ❌ Use `source` with untrusted files
4. ❌ Pass unsanitized user input to shell commands
5. ❌ Use backticks for command substitution (use `$()`)
6. ❌ Ignore return codes from critical operations
7. ❌ Store secrets in scripts (use environment or secret managers)

**ALWAYS:**
1. ✅ Quote all variable expansions: `"$var"` not `$var`
2. ✅ Use `set -euo pipefail` for error detection
3. ✅ Validate all external inputs
4. ✅ Use absolute paths or validate relative paths
5. ✅ Check command existence before execution
6. ✅ Use arrays for commands with multiple arguments
7. ✅ Set restrictive file permissions (600 for sensitive files)

### 3.2 Input Validation Patterns

```bash
# Validate and sanitize filename
sanitize_filename() {
    local filename="$1"

    # Remove path components
    filename="$(basename "$filename")"

    # Remove dangerous characters
    filename="${filename//[^a-zA-Z0-9._-]/}"

    # Ensure not empty after sanitization
    if [[ -z "$filename" ]]; then
        echo "Error: Invalid filename after sanitization" >&2
        return 1
    fi

    echo "$filename"
    return 0
}

# Validate numeric input
validate_number() {
    local input="$1"
    local min="${2:-0}"
    local max="${3:-999999}"

    # Check if numeric
    if [[ ! "$input" =~ ^[0-9]+$ ]]; then
        echo "Error: Not a number: $input" >&2
        return 1
    fi

    # Check range
    if (( input < min || input > max )); then
        echo "Error: Number out of range [$min-$max]: $input" >&2
        return 1
    fi

    return 0
}

# Validate path is within allowed directory
validate_path_containment() {
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
```

### 3.3 Command Injection Prevention

```bash
# BAD: Vulnerable to injection
user_input="file.txt; rm -rf /"
cat $user_input  # DANGEROUS!

# GOOD: Properly quoted
user_input="file.txt; rm -rf /"
cat "$user_input"  # Safe: tries to open file named "file.txt; rm -rf /"

# BAD: Eval with user input
eval "echo $user_input"  # NEVER!

# GOOD: Direct execution with validation
if [[ "$user_input" =~ ^[a-zA-Z0-9._-]+$ ]]; then
    echo "$user_input"
fi

# BAD: Command from string
cmd="ls $user_dir"
$cmd  # Vulnerable!

# GOOD: Array-based command
cmd=(ls "$user_dir")
"${cmd[@]}"  # Safe
```

---

## 4. Best Practices

### 4.1 Quoting Rules

```bash
# Always quote variable expansions
file_name="my file.txt"
cat "$file_name"  # Correct: treats as single argument
cat $file_name    # Wrong: splits into two arguments

# Quote command substitutions
result="$(grep pattern file.txt)"  # Correct
result=$(grep pattern file.txt)    # Risky (word splitting)

# Use arrays for multiple arguments
files=("file 1.txt" "file 2.txt")
for file in "${files[@]}"; do  # Correct: preserves spaces
    echo "$file"
done

# Parameter expansion quoting
echo "${var:-default}"     # Correct
echo ${var:-default}       # Risky
```

### 4.2 Error Handling Patterns

```bash
# Check command success
if command_that_might_fail; then
    echo "Success"
else
    echo "Error: Command failed with code $?" >&2
    exit 1
fi

# Short-circuit error handling
command_that_must_succeed || {
    echo "Error: Critical operation failed" >&2
    exit 1
}

# Capture and check exit code
if output=$(risky_command 2>&1); then
    echo "Output: $output"
else
    local exit_code=$?
    echo "Error: Command failed with code $exit_code" >&2
    echo "Output: $output" >&2
    return "$exit_code"
fi

# Use trap for cleanup
cleanup() {
    rm -f "$temp_file"
    kill "$background_pid" 2>/dev/null || true
}
trap cleanup EXIT INT TERM
```

### 4.3 Performance Patterns

```bash
# BAD: Multiple process spawns in loop
for file in *.txt; do
    cat "$file" | grep pattern  # Spawns cat + grep for each file
done

# GOOD: Use built-ins and single process
for file in *.txt; do
    grep pattern "$file"  # Single process, more efficient
done

# BAD: Unnecessary cat
cat file.txt | grep pattern

# GOOD: Direct file input
grep pattern file.txt

# BAD: External command for simple operation
count=$(echo "$string" | wc -c)

# GOOD: Built-in parameter expansion
count=${#string}

# BAD: Multiple passes over data
lines=$(cat file.txt | wc -l)
words=$(cat file.txt | wc -w)

# GOOD: Single pass with read
lines=0
words=0
while IFS= read -r line; do
    ((lines++))
    words=$((words + $(echo "$line" | wc -w)))
done < file.txt
```

---

## 5. Common Patterns

### Pattern 1: Argument Parsing

```bash
usage() {
    cat <<EOF
Usage: $SCRIPT_NAME [OPTIONS] <input>

Options:
    -h, --help       Show this help message
    -v, --verbose    Enable verbose output
    -o, --output     Output file
    -f, --force      Force overwrite

Examples:
    $SCRIPT_NAME input.txt
    $SCRIPT_NAME -v -o output.txt input.txt
EOF
}

parse_args() {
    local output_file=""
    local verbose=false
    local force=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                usage
                exit 0
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            -o|--output)
                output_file="$2"
                shift 2
                ;;
            -f|--force)
                force=true
                shift
                ;;
            -*)
                echo "Error: Unknown option: $1" >&2
                usage
                exit 1
                ;;
            *)
                # Positional argument
                input_file="$1"
                shift
                ;;
        esac
    done

    # Validate required arguments
    if [[ -z "$input_file" ]]; then
        echo "Error: Missing required input file" >&2
        usage
        exit 1
    fi
}
```

### Pattern 2: Logging

```bash
# Logging levels
readonly LOG_ERROR=0
readonly LOG_WARN=1
readonly LOG_INFO=2
readonly LOG_DEBUG=3

LOG_LEVEL=$LOG_INFO

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp
    timestamp="$(date '+%Y-%m-%d %H:%M:%S')"

    case "$level" in
        $LOG_ERROR)
            [[ $LOG_LEVEL -ge $LOG_ERROR ]] && echo "[$timestamp] ERROR: $message" >&2
            ;;
        $LOG_WARN)
            [[ $LOG_LEVEL -ge $LOG_WARN ]] && echo "[$timestamp] WARN:  $message" >&2
            ;;
        $LOG_INFO)
            [[ $LOG_LEVEL -ge $LOG_INFO ]] && echo "[$timestamp] INFO:  $message"
            ;;
        $LOG_DEBUG)
            [[ $LOG_LEVEL -ge $LOG_DEBUG ]] && echo "[$timestamp] DEBUG: $message"
            ;;
    esac
}

# Usage
log $LOG_INFO "Starting script"
log $LOG_DEBUG "Processing file: $filename"
log $LOG_ERROR "Failed to process file"
```

### Pattern 3: Temporary File Handling

```bash
# Create secure temporary file
create_temp_file() {
    local template="${1:-/tmp/script.XXXXXX}"
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

# Usage with automatic cleanup
main() {
    local temp_file
    temp_file=$(create_temp_file) || exit 1

    # Ensure cleanup on exit
    trap 'rm -f "$temp_file"' EXIT

    # Use temp file
    echo "data" > "$temp_file"
    process_file "$temp_file"
}
```

---

## 6. Testing & Validation

### 6.1 Script Validation

```bash
# Use shellcheck for static analysis
shellcheck script.sh

# Use bash -n for syntax check
bash -n script.sh

# Enable debug mode for troubleshooting
bash -x script.sh
```

### 6.2 Test Patterns

```bash
# Simple test function
test_sanitize_filename() {
    local result
    result=$(sanitize_filename "file name.txt")

    if [[ "$result" == "filename.txt" ]]; then
        echo "PASS: sanitize_filename"
        return 0
    else
        echo "FAIL: sanitize_filename (got: $result)" >&2
        return 1
    fi
}

# Run all tests
run_tests() {
    local failed=0

    test_sanitize_filename || ((failed++))
    test_validate_email || ((failed++))

    if [[ $failed -eq 0 ]]; then
        echo "All tests passed"
        return 0
    else
        echo "$failed test(s) failed" >&2
        return 1
    fi
}
```

---

## 7. References

See `references/` directory for:
- `advanced-patterns.md` - Advanced Bash patterns and optimizations
- `security-examples.md` - Security-focused examples and CVEs
- `threat-model.md` - Comprehensive threat model and attack scenarios

---

## 8. Quick Reference

### Essential Commands

```bash
# String operations
${var#pattern}      # Remove shortest match from beginning
${var##pattern}     # Remove longest match from beginning
${var%pattern}      # Remove shortest match from end
${var%%pattern}     # Remove longest match from end
${var/pattern/repl} # Replace first match
${var//pattern/repl}# Replace all matches
${var:-default}     # Use default if unset
${var:=default}     # Assign default if unset
${var:?error}       # Exit with error if unset
${#var}            # String length

# Array operations
arr=()             # Initialize empty array
arr=(a b c)        # Initialize with values
${arr[0]}          # Access element
${arr[@]}          # All elements (word-split)
${#arr[@]}         # Array length
arr+=("d")         # Append element

# File tests
[[ -e file ]]      # Exists
[[ -f file ]]      # Is regular file
[[ -d dir ]]       # Is directory
[[ -r file ]]      # Is readable
[[ -w file ]]      # Is writable
[[ -x file ]]      # Is executable
[[ file1 -nt file2 ]] # file1 newer than file2

# Safe iteration
while IFS= read -r line; do
    echo "$line"
done < file.txt

# Process substitution
diff <(command1) <(command2)
while read -r line; do
    process "$line"
done < <(command)
```

### Troubleshooting

**Problem**: Script exits unexpectedly
**Solution**: Check `set -e` and add `|| true` for commands that may fail safely

**Problem**: Word splitting issues
**Solution**: Quote all variable expansions: `"$var"` not `$var`

**Problem**: Command not found
**Solution**: Use full paths or check $PATH, verify command exists with `command -v`

**Problem**: Script works locally but fails in CI/CD
**Solution**: Check environment differences, use explicit paths, validate all assumptions
