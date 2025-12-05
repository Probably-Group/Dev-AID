# Advanced Bash Patterns

Advanced patterns for expert-level Bash scripting with focus on performance, maintainability, and robustness.

---

## Pattern 1: Parallel Processing with Job Control

### Use Case
Process multiple items concurrently to improve performance, while limiting parallelism to avoid resource exhaustion.

### Implementation

```bash
# Process files in parallel with max concurrent jobs
parallel_process() {
    local max_jobs=4
    local -a pids=()

    for file in *.txt; do
        # Start background process
        process_file "$file" &
        pids+=($!)

        # Wait if we've reached max jobs
        if [[ ${#pids[@]} -ge $max_jobs ]]; then
            wait "${pids[0]}" || echo "Job failed: ${pids[0]}" >&2
            pids=("${pids[@]:1}")  # Remove first element
        fi
    done

    # Wait for remaining jobs
    for pid in "${pids[@]}"; do
        wait "$pid" || echo "Job failed: $pid" >&2
    done
}

# More robust parallel execution with error tracking
parallel_with_error_tracking() {
    local max_jobs=4
    local -a pids=()
    local -A job_files=()
    local failed=0

    for file in *.txt; do
        process_file "$file" &
        local pid=$!
        pids+=($pid)
        job_files[$pid]="$file"

        if [[ ${#pids[@]} -ge $max_jobs ]]; then
            local first_pid="${pids[0]}"
            if ! wait "$first_pid"; then
                echo "Error: Failed processing ${job_files[$first_pid]}" >&2
                ((failed++))
            fi
            unset "job_files[$first_pid]"
            pids=("${pids[@]:1}")
        fi
    done

    for pid in "${pids[@]}"; do
        if ! wait "$pid"; then
            echo "Error: Failed processing ${job_files[$pid]}" >&2
            ((failed++))
        fi
    done

    return "$failed"
}
```

### Trade-offs
**Pros**:
- Significant performance improvement for I/O-bound operations
- Simple implementation with built-in job control
- No external dependencies

**Cons**:
- Limited to CPU core count for optimal performance
- Harder to debug than sequential execution
- Resource consumption monitoring required

---

## Pattern 2: Advanced Parameter Parsing with getopt

### Use Case
Robust command-line parsing with support for both short and long options, required arguments, and validation.

### Implementation

```bash
#!/usr/bin/env bash

parse_arguments() {
    # Define options
    local -r short_opts="hvo:c:"
    local -r long_opts="help,verbose,output:,config:,dry-run"

    # Parse options
    local parsed
    if ! parsed=$(getopt -o "$short_opts" -l "$long_opts" -n "$SCRIPT_NAME" -- "$@"); then
        usage
        exit 1
    fi

    eval set -- "$parsed"

    # Process options
    local output_file=""
    local config_file=""
    local verbose=false
    local dry_run=false

    while true; do
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
            -c|--config)
                config_file="$2"
                if [[ ! -f "$config_file" ]]; then
                    echo "Error: Config file not found: $config_file" >&2
                    exit 1
                fi
                shift 2
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            --)
                shift
                break
                ;;
            *)
                echo "Programming error" >&2
                exit 3
                ;;
        esac
    done

    # Remaining arguments
    local -a positional_args=("$@")

    # Validate required arguments
    if [[ ${#positional_args[@]} -eq 0 ]]; then
        echo "Error: Missing required input file" >&2
        usage
        exit 1
    fi

    # Export parsed values (or use a different pattern)
    export PARSED_OUTPUT_FILE="$output_file"
    export PARSED_CONFIG_FILE="$config_file"
    export PARSED_VERBOSE="$verbose"
    export PARSED_DRY_RUN="$dry_run"
    export PARSED_INPUTS=("${positional_args[@]}")
}
```

---

## Pattern 3: Configuration File Parsing

### Use Case
Load and validate configuration from external files in various formats.

### Implementation

```bash
# Parse simple KEY=VALUE config file
load_config() {
    local config_file="$1"
    local -A config=()

    if [[ ! -f "$config_file" ]]; then
        echo "Error: Config file not found: $config_file" >&2
        return 1
    fi

    # Read config file
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        [[ "$key" =~ ^[[:space:]]*# ]] && continue
        [[ -z "$key" ]] && continue

        # Remove leading/trailing whitespace
        key="${key#"${key%%[![:space:]]*}"}"
        key="${key%"${key##*[![:space:]]}"}"
        value="${value#"${value%%[![:space:]]*}"}"
        value="${value%"${value##*[![:space:]]}"}"

        # Store in associative array
        config["$key"]="$value"
    done < "$config_file"

    # Validate required keys
    local -a required_keys=(DATABASE_URL API_KEY)
    for key in "${required_keys[@]}"; do
        if [[ -z "${config[$key]:-}" ]]; then
            echo "Error: Missing required config key: $key" >&2
            return 1
        fi
    done

    # Export configuration
    for key in "${!config[@]}"; do
        export "CONFIG_$key=${config[$key]}"
    done

    return 0
}

# Parse JSON config (requires jq)
load_json_config() {
    local config_file="$1"

    if ! command -v jq &>/dev/null; then
        echo "Error: jq is required for JSON config parsing" >&2
        return 1
    fi

    # Validate JSON
    if ! jq empty "$config_file" 2>/dev/null; then
        echo "Error: Invalid JSON in $config_file" >&2
        return 1
    fi

    # Extract and export values
    export CONFIG_DATABASE_URL=$(jq -r '.database.url' "$config_file")
    export CONFIG_API_KEY=$(jq -r '.api.key' "$config_file")

    # Validate
    if [[ "$CONFIG_DATABASE_URL" == "null" || -z "$CONFIG_DATABASE_URL" ]]; then
        echo "Error: Missing database.url in config" >&2
        return 1
    fi

    return 0
}
```

---

## Pattern 4: Signal Handling and Graceful Shutdown

### Use Case
Handle signals properly to clean up resources and allow graceful shutdown.

### Implementation

```bash
#!/usr/bin/env bash

# Global state
declare -g SHUTDOWN_REQUESTED=false
declare -g BACKGROUND_PIDS=()

# Signal handler
handle_signal() {
    local signal=$1

    echo "Received signal: $signal" >&2
    SHUTDOWN_REQUESTED=true

    # Send TERM to all background processes
    for pid in "${BACKGROUND_PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            echo "Terminating child process: $pid" >&2
            kill -TERM "$pid" 2>/dev/null || true
        fi
    done

    # Wait for background processes with timeout
    local timeout=10
    local elapsed=0
    while [[ $elapsed -lt $timeout ]]; do
        local remaining=0
        for pid in "${BACKGROUND_PIDS[@]}"; do
            if kill -0 "$pid" 2>/dev/null; then
                ((remaining++))
            fi
        done

        if [[ $remaining -eq 0 ]]; then
            break
        fi

        sleep 1
        ((elapsed++))
    done

    # Force kill if still running
    for pid in "${BACKGROUND_PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            echo "Force killing process: $pid" >&2
            kill -KILL "$pid" 2>/dev/null || true
        fi
    done

    exit 143  # 128 + 15 (SIGTERM)
}

# Setup signal handlers
trap 'handle_signal INT' INT
trap 'handle_signal TERM' TERM

# Main processing loop
main() {
    while ! $SHUTDOWN_REQUESTED; do
        # Start background task
        process_task &
        local pid=$!
        BACKGROUND_PIDS+=($pid)

        # Check if tasks completed
        for i in "${!BACKGROUND_PIDS[@]}"; do
            local pid="${BACKGROUND_PIDS[$i]}"
            if ! kill -0 "$pid" 2>/dev/null; then
                wait "$pid" || echo "Task $pid failed" >&2
                unset 'BACKGROUND_PIDS[$i]'
            fi
        done

        # Rebuild array without holes
        BACKGROUND_PIDS=("${BACKGROUND_PIDS[@]}")

        sleep 1
    done

    echo "Shutdown complete" >&2
}
```

---

## Pattern 5: Retry Logic with Exponential Backoff

### Use Case
Retry failed operations with increasing delay between attempts.

### Implementation

```bash
# Retry a command with exponential backoff
retry_with_backoff() {
    local max_attempts="${1:-5}"
    local initial_delay="${2:-2}"
    local max_delay="${3:-60}"
    shift 3
    local cmd=("$@")

    local attempt=1
    local delay=$initial_delay

    while [[ $attempt -le $max_attempts ]]; do
        echo "Attempt $attempt/$max_attempts: ${cmd[*]}" >&2

        if "${cmd[@]}"; then
            echo "Success on attempt $attempt" >&2
            return 0
        fi

        local exit_code=$?

        if [[ $attempt -eq $max_attempts ]]; then
            echo "Failed after $max_attempts attempts" >&2
            return "$exit_code"
        fi

        echo "Failed with exit code $exit_code, retrying in ${delay}s..." >&2
        sleep "$delay"

        # Exponential backoff with max cap
        delay=$((delay * 2))
        if [[ $delay -gt $max_delay ]]; then
            delay=$max_delay
        fi

        ((attempt++))
    done
}

# Usage
retry_with_backoff 5 2 30 curl -f https://api.example.com/health

# Retry with custom condition
retry_until_success() {
    local max_attempts=10
    local delay=5
    local attempt=1

    while [[ $attempt -le $max_attempts ]]; do
        if check_service_healthy; then
            echo "Service is healthy after $attempt attempts" >&2
            return 0
        fi

        echo "Service not ready, attempt $attempt/$max_attempts" >&2
        sleep "$delay"
        ((attempt++))
    done

    echo "Service failed to become healthy" >&2
    return 1
}
```

---

## Pattern 6: Structured Logging with Context

### Use Case
Production-ready logging with structured data and context.

### Implementation

```bash
# Structured logging with JSON output
log_json() {
    local level="$1"
    local message="$2"
    shift 2
    local -A context=("$@")

    local timestamp
    timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

    # Build JSON object
    local json_parts=()
    json_parts+=("\"timestamp\":\"$timestamp\"")
    json_parts+=("\"level\":\"$level\"")
    json_parts+=("\"message\":\"$message\"")
    json_parts+=("\"script\":\"$SCRIPT_NAME\"")
    json_parts+=("\"pid\":$$")

    # Add context
    for key in "${!context[@]}"; do
        local value="${context[$key]}"
        json_parts+=("\"$key\":\"$value\"")
    done

    # Output JSON
    local json
    json=$(printf "{%s}" "$(IFS=,; echo "${json_parts[*]}")")
    echo "$json" >&2
}

# Usage
log_json "INFO" "Processing started" \
    file="data.txt" \
    records=1000

log_json "ERROR" "Failed to process file" \
    file="data.txt" \
    error="Permission denied"

# Colorized terminal output with context
log_colored() {
    local level="$1"
    local message="$2"
    shift 2
    local context="$*"

    local timestamp
    timestamp="$(date '+%Y-%m-%d %H:%M:%S')"

    # Color codes
    local -A colors=(
        [ERROR]='\033[0;31m'
        [WARN]='\033[0;33m'
        [INFO]='\033[0;32m'
        [DEBUG]='\033[0;36m'
    )
    local reset='\033[0m'

    local color="${colors[$level]:-$reset}"

    echo -e "${color}[$timestamp] $level:${reset} $message${context:+ ($context)}" >&2
}
```

---

## Pattern 7: Lock Files for Mutual Exclusion

### Use Case
Prevent multiple instances of a script from running simultaneously.

### Implementation

```bash
# Acquire exclusive lock
acquire_lock() {
    local lock_file="${1:-/tmp/$SCRIPT_NAME.lock}"
    local max_wait="${2:-60}"
    local waited=0

    while [[ $waited -lt $max_wait ]]; do
        # Try to create lock file exclusively
        if (set -o noclobber; echo $$ > "$lock_file") 2>/dev/null; then
            # Success - we have the lock
            echo "Acquired lock: $lock_file" >&2

            # Setup trap to remove lock on exit
            trap "rm -f '$lock_file'" EXIT INT TERM

            return 0
        fi

        # Check if lock holder is still running
        if [[ -f "$lock_file" ]]; then
            local lock_pid
            lock_pid=$(<"$lock_file")

            if ! kill -0 "$lock_pid" 2>/dev/null; then
                # Stale lock - remove it
                echo "Removing stale lock from PID $lock_pid" >&2
                rm -f "$lock_file"
                continue
            fi
        fi

        # Wait and retry
        echo "Lock held by another process, waiting... ($waited/${max_wait}s)" >&2
        sleep 2
        waited=$((waited + 2))
    done

    echo "Error: Failed to acquire lock after ${max_wait}s" >&2
    return 1
}

# Usage
if ! acquire_lock "/var/lock/myapp.lock" 30; then
    echo "Another instance is running" >&2
    exit 1
fi

# Do work...
echo "Doing work with exclusive lock"
```

---

## Pattern 8: Data Validation and Type Checking

### Use Case
Validate data types and formats before processing.

### Implementation

```bash
# Type validation functions
is_integer() {
    [[ "$1" =~ ^-?[0-9]+$ ]]
}

is_positive_integer() {
    [[ "$1" =~ ^[0-9]+$ ]] && [[ "$1" -gt 0 ]]
}

is_float() {
    [[ "$1" =~ ^-?[0-9]+\.?[0-9]*$ ]]
}

is_boolean() {
    [[ "$1" =~ ^(true|false|yes|no|1|0)$ ]]
}

is_ip_address() {
    local ip="$1"
    local regex='^([0-9]{1,3}\.){3}[0-9]{1,3}$'

    if [[ ! "$ip" =~ $regex ]]; then
        return 1
    fi

    # Validate each octet
    local IFS='.'
    local -a octets=($ip)
    for octet in "${octets[@]}"; do
        if [[ $octet -gt 255 ]]; then
            return 1
        fi
    done

    return 0
}

is_url() {
    local url="$1"
    [[ "$url" =~ ^https?://[a-zA-Z0-9.-]+(:[0-9]+)?(/.*)?$ ]]
}

# Comprehensive validation
validate_config_value() {
    local key="$1"
    local value="$2"
    local expected_type="$3"

    case "$expected_type" in
        integer)
            if ! is_integer "$value"; then
                echo "Error: $key must be an integer, got: $value" >&2
                return 1
            fi
            ;;
        positive_integer)
            if ! is_positive_integer "$value"; then
                echo "Error: $key must be a positive integer, got: $value" >&2
                return 1
            fi
            ;;
        float)
            if ! is_float "$value"; then
                echo "Error: $key must be a float, got: $value" >&2
                return 1
            fi
            ;;
        boolean)
            if ! is_boolean "$value"; then
                echo "Error: $key must be boolean (true/false/yes/no/1/0), got: $value" >&2
                return 1
            fi
            ;;
        ip)
            if ! is_ip_address "$value"; then
                echo "Error: $key must be a valid IP address, got: $value" >&2
                return 1
            fi
            ;;
        url)
            if ! is_url "$value"; then
                echo "Error: $key must be a valid URL, got: $value" >&2
                return 1
            fi
            ;;
        *)
            echo "Error: Unknown type: $expected_type" >&2
            return 1
            ;;
    esac

    return 0
}

# Usage
validate_config_value "PORT" "8080" "positive_integer" || exit 1
validate_config_value "API_URL" "https://api.example.com" "url" || exit 1
```

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Parsing ls Output

**Problem**: Parsing `ls` output is fragile and breaks with special characters.

**Bad Example**:
```bash
# DON'T DO THIS
for file in $(ls *.txt); do
    echo "$file"
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
```

**Why Better**: Glob expansion handles special characters correctly, and `find` with `-print0` handles all filenames safely.

---

### Anti-Pattern 2: Using cat Unnecessarily

**Problem**: Spawning external process when Bash can read files directly.

**Bad Example**:
```bash
while read line; do
    echo "$line"
done < <(cat file.txt)
```

**Better Approach**:
```bash
while IFS= read -r line; do
    echo "$line"
done < file.txt
```

**Why Better**: More efficient, fewer processes, clearer intent.

---

### Anti-Pattern 3: Not Checking Command Existence

**Problem**: Assuming commands exist without verification.

**Bad Example**:
```bash
jq '.field' file.json
```

**Better Approach**:
```bash
if ! command -v jq &>/dev/null; then
    echo "Error: jq is required but not installed" >&2
    exit 1
fi

jq '.field' file.json
```

**Why Better**: Fails early with clear error message instead of cryptic "command not found".
