---
name: bash-expert
version: 2.0.0
description: "Secure bash scripting with shellcheck compliance, proper quoting, error handling, and POSIX compatibility."
risk_level: HIGH
---

# Bash Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-78: Command Injection**
- NEVER: `eval "$user_input"` or backticks with user data
- NEVER: `cmd="ls $userpath"; $cmd` - indirect execution
- ALWAYS: Quote variables, use arrays for commands

**CWE-20: Unquoted Variables**
- NEVER: `rm -rf $path` or `[ $var = "value" ]`
- ALWAYS: `rm -rf "$path"` and `[ "$var" = "value" ]`

**CWE-22: Path Traversal**
- NEVER: `cat "$userdir/$userfile"` without validation
- ALWAYS: Validate path doesn't contain `..`, use `realpath` and check prefix

**CWE-377: Insecure Temp Files**
- NEVER: `echo "$data" > /tmp/myfile` - predictable name
- ALWAYS: `tmpfile=$(mktemp)` or `mktemp -d` for directories

**CWE-732: Insecure Permissions**
- NEVER: `chmod 777 file` or world-writable scripts
- ALWAYS: `chmod 600` for sensitive files, `700` for scripts

### 0.3 Risk Level: HIGH

**Verification requirements for HIGH risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Script Header Requirements

**ALWAYS start every script with:**
```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'
```

**What these do:**
- `set -e` → Exit immediately on error
- `set -u` → Error on undefined variables
- `set -o pipefail` → Fail on pipe errors
- `IFS=$'\n\t'` → Safer word splitting

---

## 2. Security Rules (CVE-Driven)

### 2.1 Command Injection Prevention (CVE-2014-6271 Shellshock, CWE-78)

**NEVER** use unquoted variables in commands:
```bash
# ❌ WRONG - Command injection possible
rm -rf $user_input
curl $url
eval $command

# ✅ CORRECT - Always quote variables
rm -rf "${user_input}"
curl "${url}"
# NEVER use eval with user input
```

**NEVER** use eval, source, or . with untrusted input:
```bash
# ❌ WRONG - Arbitrary code execution
eval "$user_config"
source "$user_file"

# ✅ CORRECT - Parse config safely
while IFS='=' read -r key value; do
    case "$key" in
        allowed_setting) setting="$value" ;;
        *) echo "Unknown setting: $key" >&2 ;;
    esac
done < "$config_file"
```

### 2.2 Argument Injection (CWE-88)

**NEVER** pass user input directly to commands that interpret options:
```bash
# ❌ WRONG - User can inject -o /etc/passwd
filename="$1"
curl "$filename"  # If filename is "-o /etc/passwd http://evil.com"

# ✅ CORRECT - Use -- to end option parsing
curl -- "${filename}"

# ✅ CORRECT - Validate input
if [[ "$filename" == -* ]]; then
    echo "Invalid filename" >&2
    exit 1
fi
```

### 2.3 Path Traversal (CWE-22)

**NEVER** use user input in paths without validation:
```bash
# ❌ WRONG - Path traversal possible
cat "/data/${user_input}"

# ✅ CORRECT - Validate and resolve path
validate_path() {
    local base_dir="$1"
    local user_path="$2"
    local resolved

    resolved="$(cd "${base_dir}" && realpath -m "${user_path}" 2>/dev/null)" || return 1

    # Check if resolved path is under base_dir
    if [[ "${resolved}" != "${base_dir}"/* ]]; then
        echo "Path traversal attempt blocked" >&2
        return 1
    fi
    echo "${resolved}"
}

safe_path="$(validate_path "/data" "${user_input}")" || exit 1
cat "${safe_path}"
```

### 2.4 Temporary File Handling (CWE-377, CWE-367)

**NEVER** use predictable temp file names:
```bash
# ❌ WRONG - Race condition, predictable name
temp_file="/tmp/myapp_temp"
echo "$data" > "$temp_file"

# ✅ CORRECT - Use mktemp with cleanup trap
cleanup() {
    rm -rf "${TEMP_DIR:-}"
}
trap cleanup EXIT

TEMP_DIR="$(mktemp -d)"
temp_file="${TEMP_DIR}/data"
echo "$data" > "$temp_file"
```

### 2.5 Privilege Handling

**NEVER** run as root unnecessarily:
```bash
# ❌ WRONG - Entire script runs as root
sudo ./myscript.sh

# ✅ CORRECT - Drop privileges, elevate only when needed
if [[ $EUID -eq 0 ]]; then
    echo "Don't run as root" >&2
    exit 1
fi

# Only specific commands need sudo
sudo systemctl restart myservice
```

---

## 3. Code Patterns

### 3.1 WHEN processing command line arguments

```bash
#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat << EOF
Usage: ${0##*/} [OPTIONS] <input_file>

Options:
    -o, --output FILE    Output file (default: stdout)
    -v, --verbose        Enable verbose output
    -h, --help           Show this help

Example:
    ${0##*/} -o result.txt input.txt
EOF
}

# Defaults
output="/dev/stdout"
verbose=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -o|--output)
            [[ $# -lt 2 ]] && { echo "Missing argument for $1" >&2; exit 1; }
            output="$2"
            shift 2
            ;;
        -v|--verbose)
            verbose=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        --)
            shift
            break
            ;;
        -*)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
        *)
            break
            ;;
    esac
done

# Validate required arguments
if [[ $# -lt 1 ]]; then
    echo "Error: Missing input file" >&2
    usage >&2
    exit 1
fi

input_file="$1"

# Validate input file exists
if [[ ! -f "$input_file" ]]; then
    echo "Error: File not found: $input_file" >&2
    exit 1
fi
```

### 3.2 WHEN reading files line by line

```bash
# ❌ WRONG - Breaks on special characters
for line in $(cat file.txt); do
    echo "$line"
done

# ✅ CORRECT - Proper line reading
while IFS= read -r line || [[ -n "$line" ]]; do
    echo "$line"
done < file.txt

# ✅ CORRECT - Process with field splitting
while IFS=: read -r user _ uid gid _ home shell; do
    echo "User: $user, UID: $uid, Shell: $shell"
done < /etc/passwd
```

### 3.3 WHEN handling errors

```bash
#!/usr/bin/env bash
set -euo pipefail

# Error handler with line number
error_handler() {
    local line_no="$1"
    local error_code="$2"
    echo "Error on line ${line_no}: exit code ${error_code}" >&2
}
trap 'error_handler ${LINENO} $?' ERR

# Cleanup handler
cleanup() {
    local exit_code=$?
    rm -rf "${TEMP_DIR:-}"
    exit "$exit_code"
}
trap cleanup EXIT

# Function with error handling
process_file() {
    local file="$1"

    if [[ ! -r "$file" ]]; then
        echo "Cannot read file: $file" >&2
        return 1
    fi

    # Process file...
}
```

### 3.4 WHEN calling external commands

```bash
# ❌ WRONG - Assumes command exists
jq '.data' file.json

# ✅ CORRECT - Check command exists
require_command() {
    local cmd="$1"
    if ! command -v "$cmd" &>/dev/null; then
        echo "Required command not found: $cmd" >&2
        exit 1
    fi
}

require_command jq
require_command curl

# ❌ WRONG - Ignores exit code
output=$(some_command)

# ✅ CORRECT - Check exit code
if ! output=$(some_command 2>&1); then
    echo "Command failed: $output" >&2
    exit 1
fi
```

### 3.5 WHEN working with arrays

```bash
# Declare array
declare -a files=()

# Add elements
files+=("file1.txt")
files+=("file2.txt")

# Iterate safely (handles spaces in names)
for file in "${files[@]}"; do
    echo "Processing: $file"
done

# Check if array is empty
if [[ ${#files[@]} -eq 0 ]]; then
    echo "No files to process"
    exit 0
fi

# Pass array to function
process_files() {
    local -a files=("$@")
    for file in "${files[@]}"; do
        echo "$file"
    done
}
process_files "${files[@]}"
```

### 3.6 WHEN making HTTP requests

```bash
# ✅ CORRECT - Safe curl usage
fetch_url() {
    local url="$1"
    local output="${2:-/dev/stdout}"
    local max_time="${3:-30}"

    curl \
        --fail \
        --silent \
        --show-error \
        --location \
        --max-time "$max_time" \
        --output "$output" \
        -- "$url"
}

# With retry logic
fetch_with_retry() {
    local url="$1"
    local max_attempts=3
    local attempt=1

    while [[ $attempt -le $max_attempts ]]; do
        if fetch_url "$url"; then
            return 0
        fi
        echo "Attempt $attempt failed, retrying..." >&2
        ((attempt++))
        sleep $((attempt * 2))
    done

    echo "Failed after $max_attempts attempts" >&2
    return 1
}
```

---

## 4. Variable Rules

**ALWAYS** use braces `{}` and double quotes `""`:
```bash
# ❌ WRONG - word splitting, glob expansion, ambiguous
echo $var
echo "$var"              # Works but inconsistent style

# ✅ CORRECT - always "${var}" (parameter expansion syntax)
echo "${var}"
echo "${file_name}"

# WHY braces matter - disambiguation:
filename="report"
echo "$filename_final"   # Variable: $filename_final (undefined!)
echo "${filename}_final" # Variable: $filename, then _final ✓

# Handles embedded quotes, spaces, globs safely:
var='AA"BB *.txt'
echo "${var}"            # Output: AA"BB *.txt (literal, no expansion)
```

**ALWAYS** use `local` in functions:
```bash
# ❌ WRONG - Pollutes global scope
process() {
    result="done"
}

# ✅ CORRECT - Local scope
process() {
    local result="done"
    echo "$result"
}
```

**ALWAYS** use `readonly` for constants:
```bash
readonly CONFIG_DIR="/etc/myapp"
readonly MAX_RETRIES=3
readonly -a ALLOWED_EXTENSIONS=("txt" "log" "csv")
```

---

## 5. Conditional Rules

**ALWAYS** use `[[` instead of `[`:
```bash
# ❌ WRONG - Old test syntax
if [ "$var" = "value" ]; then
if [ -z $var ]; then

# ✅ CORRECT - Modern test syntax
if [[ "$var" == "value" ]]; then
if [[ -z "${var:-}" ]]; then
```

**ALWAYS** use pattern matching safely:
```bash
# Check if variable matches pattern
if [[ "$filename" == *.txt ]]; then
    echo "Text file"
fi

# Check if variable is integer
if [[ "$num" =~ ^[0-9]+$ ]]; then
    echo "Valid number"
fi

# Check if file exists and is readable
if [[ -f "$file" && -r "$file" ]]; then
    cat "$file"
fi
```

---

## 6. Logging Pattern

```bash
#!/usr/bin/env bash
set -euo pipefail

# Log levels
readonly LOG_ERROR=0
readonly LOG_WARN=1
readonly LOG_INFO=2
readonly LOG_DEBUG=3

LOG_LEVEL="${LOG_LEVEL:-$LOG_INFO}"

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp
    timestamp="$(date '+%Y-%m-%d %H:%M:%S')"

    if [[ "$level" -le "$LOG_LEVEL" ]]; then
        case "$level" in
            "$LOG_ERROR") echo "[$timestamp] ERROR: $message" >&2 ;;
            "$LOG_WARN")  echo "[$timestamp] WARN:  $message" >&2 ;;
            "$LOG_INFO")  echo "[$timestamp] INFO:  $message" ;;
            "$LOG_DEBUG") echo "[$timestamp] DEBUG: $message" ;;
        esac
    fi
}

# Usage
log "$LOG_INFO" "Starting process"
log "$LOG_ERROR" "Something went wrong"
```

---

## 7. Testing Pattern

```bash
#!/usr/bin/env bash
# test_myscript.sh

set -euo pipefail

# Source the script being tested (without executing main)
source ./myscript.sh --source-only 2>/dev/null || true

test_validate_path() {
    local result

    # Test valid path
    result="$(validate_path "/data" "file.txt")"
    [[ "$result" == "/data/file.txt" ]] || { echo "FAIL: valid path"; return 1; }

    # Test path traversal blocked
    if validate_path "/data" "../etc/passwd" 2>/dev/null; then
        echo "FAIL: path traversal not blocked"
        return 1
    fi

    echo "PASS: validate_path"
}

test_require_command() {
    # Test existing command
    require_command bash || { echo "FAIL: bash not found"; return 1; }

    # Test missing command
    if require_command nonexistent_command_12345 2>/dev/null; then
        echo "FAIL: missing command not detected"
        return 1
    fi

    echo "PASS: require_command"
}

# Run tests
main() {
    local failed=0

    test_validate_path || ((failed++))
    test_require_command || ((failed++))

    if [[ $failed -gt 0 ]]; then
        echo "FAILED: $failed tests"
        exit 1
    fi

    echo "All tests passed"
}

main "$@"
```

---

## 8. Pre-Generation Checklist

**BEFORE generating any Bash code, verify:**

- [ ] Script starts with `#!/usr/bin/env bash` and `set -euo pipefail`
- [ ] All variables are quoted: `"${var}"`
- [ ] All variables in functions use `local`
- [ ] No `eval`, `source`, or `. ` with user input
- [ ] All file paths are validated against traversal
- [ ] Temp files use `mktemp` with cleanup trap
- [ ] External commands checked with `command -v`
- [ ] Arguments after `--` to prevent option injection
- [ ] Error handling with `trap` for cleanup
- [ ] No running as root unless absolutely required
