# Bash Anti-Patterns and Common Mistakes

Common mistakes in Bash scripting that lead to bugs, security vulnerabilities, or maintenance issues.

---

## Anti-Pattern 1: Parsing ls Output

**Problem**: Parsing `ls` output is fragile and breaks with special characters, spaces, or newlines in filenames.

**Bad Example**:
```bash
# DON'T DO THIS - breaks with spaces in filenames
for file in $(ls *.txt); do
    echo "$file"
done

# Also bad - parsing ls -l output
ls -l | awk '{print $9}' | while read file; do
    process "$file"
done
```

**Better Approach**:
```bash
# Use glob expansion directly
for file in *.txt; do
    [[ -e "$file" ]] || continue  # Handle no matches
    echo "$file"
done

# Or use find for more control
while IFS= read -r -d '' file; do
    echo "$file"
done < <(find . -name "*.txt" -print0)

# For file attributes, use stat instead of parsing ls
stat -c '%n %s %Y' *.txt | while read name size mtime; do
    echo "File: $name, Size: $size, Modified: $mtime"
done
```

**Why Better**: Glob expansion handles special characters correctly, and `find` with `-print0` handles all filenames safely including those with spaces, newlines, or special characters.

---

## Anti-Pattern 2: Unquoted Variables

**Problem**: Unquoted variables undergo word splitting and glob expansion, leading to unexpected behavior.

**Bad Example**:
```bash
file_name="my document.txt"
cat $file_name  # Tries to cat "my" and "document.txt" separately

search_pattern="*.txt"
find . -name $search_pattern  # Glob expands before find sees it

empty_var=""
[ $empty_var = "value" ]  # Syntax error if var is empty
```

**Better Approach**:
```bash
file_name="my document.txt"
cat "$file_name"  # Correct: treats as single argument

search_pattern="*.txt"
find . -name "$search_pattern"  # Correct: passes literal pattern to find

empty_var=""
[[ "$empty_var" = "value" ]]  # Correct: handles empty values
```

**Why Better**: Quoting prevents word splitting and glob expansion, making code predictable and safe.

---

## Anti-Pattern 3: Using cat Unnecessarily (UUOC)

**Problem**: Useless Use Of Cat - spawning external process when Bash can read files directly.

**Bad Example**:
```bash
# Wasteful - spawns cat process
cat file.txt | grep pattern

# Even worse - multiple cats in pipeline
cat file.txt | cat | grep pattern | cat

# Unnecessary cat in while loop
while read line; do
    echo "$line"
done < <(cat file.txt)
```

**Better Approach**:
```bash
# Direct file input to grep
grep pattern file.txt

# Or with process substitution
grep pattern < file.txt

# Direct file redirection in while loop
while IFS= read -r line; do
    echo "$line"
done < file.txt
```

**Why Better**: More efficient (fewer processes), faster, clearer intent, and less resource usage.

---

## Anti-Pattern 4: Using eval with Untrusted Input

**Problem**: `eval` executes arbitrary code, making it a security vulnerability with untrusted input.

**Bad Example**:
```bash
# DANGEROUS - command injection vulnerability
read -p "Enter command: " user_cmd
eval "$user_cmd"  # User can run anything!

# Also bad - dynamic variable names
var_name="user_input"
eval "$var_name=value"  # Can execute arbitrary code

# Trying to preserve spaces
args="arg1 'arg with spaces' arg3"
eval "command $args"  # Dangerous!
```

**Better Approach**:
```bash
# Use arrays for commands
user_args=("arg1" "arg with spaces" "arg3")
command "${user_args[@]}"

# For dynamic variable names, use nameref (Bash 4.3+)
declare -n var_ref="$var_name"
var_ref="value"

# Or use associative arrays
declare -A data
data["$var_name"]="value"

# For conditional execution, use case statement
case "$action" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    *)
        echo "Unknown action: $action" >&2
        exit 1
        ;;
esac
```

**Why Better**: Avoids code injection, maintains security, and is easier to understand and maintain.

---

## Anti-Pattern 5: Not Checking Command Existence

**Problem**: Assuming commands exist without verification leads to cryptic errors.

**Bad Example**:
```bash
# Fails with "command not found" if jq not installed
jq '.field' file.json

# Script continues even if critical tool missing
convert image.png image.jpg  # Fails silently if ImageMagick not installed
process_result
```

**Better Approach**:
```bash
# Check before use
if ! command -v jq &>/dev/null; then
    echo "Error: jq is required but not installed" >&2
    echo "Install with: apt-get install jq" >&2
    exit 1
fi

jq '.field' file.json

# Check multiple dependencies at once
check_dependencies() {
    local missing=()
    local -a required=(jq curl git docker)

    for cmd in "${required[@]}"; do
        if ! command -v "$cmd" &>/dev/null; then
            missing+=("$cmd")
        fi
    done

    if [[ ${#missing[@]} -gt 0 ]]; then
        echo "Error: Missing required commands: ${missing[*]}" >&2
        return 1
    fi

    return 0
}

check_dependencies || exit 1
```

**Why Better**: Fails early with clear error message instead of cryptic "command not found" errors.

---

## Anti-Pattern 6: Ignoring Exit Codes

**Problem**: Not checking if commands succeeded leads to cascading failures.

**Bad Example**:
```bash
# No error checking
cd /some/directory
rm -rf *  # Might delete wrong files if cd failed!

# Ignoring critical failures
wget https://example.com/important.tar.gz
tar xzf important.tar.gz  # Fails if wget failed
./important/install.sh  # Runs with incomplete data
```

**Better Approach**:
```bash
# Use set -e to exit on error
set -euo pipefail

# Or check explicitly
if ! cd /some/directory; then
    echo "Error: Failed to change directory" >&2
    exit 1
fi
rm -rf *

# Chain with &&
cd /some/directory && rm -rf *

# Check critical operations
if ! wget https://example.com/important.tar.gz; then
    echo "Error: Download failed" >&2
    exit 1
fi

if ! tar xzf important.tar.gz; then
    echo "Error: Extraction failed" >&2
    exit 1
fi

./important/install.sh
```

**Why Better**: Catches errors early, prevents cascading failures, and makes debugging easier.

---

## Anti-Pattern 7: Using Backticks for Command Substitution

**Problem**: Backticks are harder to read, don't nest well, and are deprecated.

**Bad Example**:
```bash
# Old style - hard to read
result=`grep pattern file.txt`

# Impossible to nest
outer=`echo inner=\`echo nested\` `  # Escaping nightmare

# Hard to see
files=`ls *.txt`
```

**Better Approach**:
```bash
# Modern style - clear and nests well
result=$(grep pattern file.txt)

# Easy to nest
outer=$(echo "inner=$(echo nested)")

# Clear and readable
files=$(find . -name "*.txt")
```

**Why Better**: More readable, nests properly, easier to maintain, and is the modern standard.

---

## Anti-Pattern 8: Not Using Strict Mode

**Problem**: Without strict mode, scripts continue with errors, use undefined variables, and ignore pipe failures.

**Bad Example**:
```bash
#!/bin/bash
# No strict mode

# Uses undefined variable - becomes empty string
echo "User: $USRE"  # Typo, should be $USER

# Continues after error
false  # Returns 1
echo "This still runs"

# Ignores pipe failures
failing_command | grep pattern  # Only checks grep's exit code
```

**Better Approach**:
```bash
#!/bin/bash
# Strict mode
set -euo pipefail

# Fails on undefined variable
echo "User: $USER"  # Correct variable name required

# Exits on error
false  # Script stops here
echo "This won't run"

# Catches pipe failures
failing_command | grep pattern  # Fails if failing_command fails

# Optional: trace execution for debugging
# set -x
```

**Why Better**: Catches errors early, prevents undefined variable bugs, and fails on pipe errors.

---

## Anti-Pattern 9: Using [ ] Instead of [[ ]] for Tests

**Problem**: Single brackets `[ ]` are less powerful and more error-prone than double brackets `[[ ]]`.

**Bad Example**:
```bash
# Single brackets require careful quoting
[ $var = "value" ]  # Fails if var is empty or contains spaces

# No regex support
[ "$string" = *pattern* ]  # Doesn't work as expected

# Less readable comparisons
[ "$a" -a "$b" ]  # Deprecated syntax
```

**Better Approach**:
```bash
# Double brackets handle empty values and spaces
[[ $var = "value" ]]  # Safe even if var is empty

# Regex support
[[ "$string" =~ pattern ]]  # Native regex matching

# Clearer boolean logic
[[ "$a" && "$b" ]]  # Clear and safe

# Pattern matching
[[ "$file" = *.txt ]]  # Glob pattern matching
```

**Why Better**: Safer, more powerful, better error handling, and more readable.

---

## Anti-Pattern 10: Not Cleaning Up Temporary Files

**Problem**: Leaving temporary files creates security risks and fills up disk space.

**Bad Example**:
```bash
# Creates temp file but doesn't clean up
temp_file="/tmp/data_$$"
echo "data" > "$temp_file"
process_file "$temp_file"
# Script exits without cleanup - file remains

# No cleanup on error
process_data || exit 1  # Exits without cleanup
```

**Better Approach**:
```bash
# Create temp file securely
temp_file=$(mktemp) || exit 1
chmod 600 "$temp_file"

# Setup cleanup trap - runs even on error
trap 'rm -f "$temp_file"' EXIT INT TERM

# Use temp file
echo "data" > "$temp_file"
process_file "$temp_file"

# Cleanup happens automatically on exit

# For temp directories
temp_dir=$(mktemp -d) || exit 1
trap 'rm -rf "$temp_dir"' EXIT INT TERM
chmod 700 "$temp_dir"
```

**Why Better**: Ensures cleanup even on errors, prevents disk space issues, and improves security.

---

## Anti-Pattern 11: Hardcoding Paths and Values

**Problem**: Hardcoded values make scripts less portable and harder to maintain.

**Bad Example**:
```bash
# Hardcoded paths
cd /home/john/projects/myapp
./run.sh

# Hardcoded credentials
DB_USER="admin"
DB_PASS="password123"

# Hardcoded configuration
MAX_CONNECTIONS=100
TIMEOUT=30
```

**Better Approach**:
```bash
# Use script directory as base
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1
./run.sh

# Use environment variables or config files
DB_USER="${DB_USER:-admin}"
DB_PASS="${DB_PASS:?Database password not set}"

# Load from config file
if [[ -f "$HOME/.myapp/config" ]]; then
    source "$HOME/.myapp/config"
fi

# Use variables with defaults
MAX_CONNECTIONS="${MAX_CONNECTIONS:-100}"
TIMEOUT="${TIMEOUT:-30}"
```

**Why Better**: More portable, easier to configure, and separates config from code.

---

## Anti-Pattern 12: Using -a and -o in Test Expressions

**Problem**: The `-a` (AND) and `-o` (OR) operators are deprecated and error-prone.

**Bad Example**:
```bash
# Deprecated and fragile
[ -f "$file" -a -r "$file" ]
[ "$x" = "a" -o "$x" = "b" ]

# Confusing precedence
[ "$a" -o "$b" -a "$c" ]  # Order matters!
```

**Better Approach**:
```bash
# Use separate tests with && and ||
[[ -f "$file" && -r "$file" ]]
[[ "$x" = "a" || "$x" = "b" ]]

# Or use separate test commands
[ -f "$file" ] && [ -r "$file" ]
[ "$x" = "a" ] || [ "$x" = "b" ]

# Clear precedence with parentheses
[[ "$a" || ("$b" && "$c") ]]
```

**Why Better**: Clearer precedence, more readable, and uses modern syntax.

---

## Anti-Pattern 13: Using echo for User Output in Functions

**Problem**: Using `echo` in functions that should return values mixes output with return values.

**Bad Example**:
```bash
get_username() {
    echo "Fetching username..."  # Goes to stdout
    echo "admin"  # Return value also goes to stdout
}

# Captures both messages
username=$(get_username)  # username="Fetching username...\nadmin"
```

**Better Approach**:
```bash
get_username() {
    # Progress to stderr
    echo "Fetching username..." >&2

    # Return value to stdout
    echo "admin"
}

# Only captures return value
username=$(get_username)  # username="admin"
# Progress still visible on terminal

# Or use return codes and global variables
get_username() {
    echo "Fetching username..." >&2
    USERNAME="admin"
    return 0
}

if get_username; then
    echo "Got username: $USERNAME"
fi
```

**Why Better**: Separates progress messages from return values, making functions more composable.

---

## Anti-Pattern 14: Not Handling Spaces in for Loops

**Problem**: For loops split on spaces instead of lines when iterating over command output.

**Bad Example**:
```bash
# Splits on spaces, not lines
for file in $(find . -name "*.txt"); do
    echo "$file"
done
# "my file.txt" becomes two iterations: "my" and "file.txt"

# Also bad
for line in $(cat file.txt); do
    echo "$line"
done
```

**Better Approach**:
```bash
# Use while read for line-by-line processing
while IFS= read -r file; do
    echo "$file"
done < <(find . -name "*.txt")

# Or with null-separated output for files
while IFS= read -r -d '' file; do
    echo "$file"
done < <(find . -name "*.txt" -print0)

# Use mapfile/readarray for arrays (Bash 4+)
mapfile -t files < <(find . -name "*.txt")
for file in "${files[@]}"; do
    echo "$file"
done
```

**Why Better**: Correctly handles filenames with spaces, tabs, and other special characters.

---

## Anti-Pattern 15: Using Uppercase Variable Names

**Problem**: Uppercase variables may collide with environment variables and shell built-ins.

**Bad Example**:
```bash
# Might override environment variables
PATH="/my/custom/path"  # Breaks command execution!
HOME="/tmp/test"  # Confuses programs
USER="testuser"  # Overrides actual user

# Might conflict with shell variables
IFS=","  # Permanently changes field separator if not restored
```

**Better Approach**:
```bash
# Use lowercase for local variables
custom_path="/my/custom/path"
test_home="/tmp/test"
test_user="testuser"

# Use readonly for constants
readonly MAX_RETRIES=3
readonly DEFAULT_TIMEOUT=30

# Prefix to avoid collisions
MY_APP_PATH="/my/custom/path"
MY_APP_USER="testuser"

# Save and restore if modifying shell variables
old_ifs="$IFS"
IFS=","
# ... use custom IFS ...
IFS="$old_ifs"
```

**Why Better**: Avoids collisions with environment variables and shell built-ins.

---

## Summary: Best Practices

**DO**:
- ✅ Quote all variable expansions: `"$var"`
- ✅ Use `[[ ]]` instead of `[ ]`
- ✅ Use `set -euo pipefail`
- ✅ Check exit codes explicitly
- ✅ Use `$(command)` instead of backticks
- ✅ Clean up temp files with trap
- ✅ Use arrays for commands
- ✅ Validate inputs before use
- ✅ Use lowercase variable names
- ✅ Check command existence

**DON'T**:
- ❌ Parse `ls` output
- ❌ Use unquoted variables
- ❌ Use unnecessary `cat`
- ❌ Use `eval` with user input
- ❌ Ignore exit codes
- ❌ Use backticks
- ❌ Skip strict mode
- ❌ Hardcode paths/values
- ❌ Use `-a` and `-o` in tests
- ❌ Use uppercase for local variables
