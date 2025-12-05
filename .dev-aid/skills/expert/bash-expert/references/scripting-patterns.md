# Bash Scripting Patterns

Detailed implementation patterns and common workflows for Bash scripting, extracted from real-world production scripts.

---

## Pattern 1: Complete Script Template

### Production-Ready Script Skeleton

```bash
#!/usr/bin/env bash
#
# Script: app-manager.sh
# Description: Manage application lifecycle with logging, error handling, and cleanup
# Usage: app-manager.sh [start|stop|restart|status] [options]
# Author: DevOps Team
# Version: 1.0.0
#

# Strict mode: exit on error, undefined variables, pipe failures
set -euo pipefail

# Optional: Enable debug mode
# set -x

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONSTANTS AND GLOBALS
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Script metadata
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"
readonly SCRIPT_VERSION="1.0.0"

# Exit codes
readonly EXIT_SUCCESS=0
readonly EXIT_FAILURE=1
readonly EXIT_INVALID_ARGS=2
readonly EXIT_MISSING_DEPENDENCY=3

# Application settings
readonly APP_NAME="myapp"
readonly APP_DIR="$SCRIPT_DIR"
readonly PID_FILE="/var/run/${APP_NAME}.pid"
readonly LOG_FILE="/var/log/${APP_NAME}.log"
readonly CONFIG_FILE="${CONFIG_FILE:-$HOME/.${APP_NAME}/config}"

# Logging levels
readonly LOG_ERROR=0
readonly LOG_WARN=1
readonly LOG_INFO=2
readonly LOG_DEBUG=3
LOG_LEVEL=${LOG_LEVEL:-$LOG_INFO}

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LOGGING FUNCTIONS
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp
    timestamp="$(date '+%Y-%m-%d %H:%M:%S')"

    case "$level" in
        $LOG_ERROR)
            [[ $LOG_LEVEL -ge $LOG_ERROR ]] && echo "[$timestamp] ERROR: $message" >&2 | tee -a "$LOG_FILE"
            ;;
        $LOG_WARN)
            [[ $LOG_LEVEL -ge $LOG_WARN ]] && echo "[$timestamp] WARN:  $message" >&2 | tee -a "$LOG_FILE"
            ;;
        $LOG_INFO)
            [[ $LOG_LEVEL -ge $LOG_INFO ]] && echo "[$timestamp] INFO:  $message" | tee -a "$LOG_FILE"
            ;;
        $LOG_DEBUG)
            [[ $LOG_LEVEL -ge $LOG_DEBUG ]] && echo "[$timestamp] DEBUG: $message" | tee -a "$LOG_FILE"
            ;;
    esac
}

log_error() { log $LOG_ERROR "$@"; }
log_warn()  { log $LOG_WARN "$@"; }
log_info()  { log $LOG_INFO "$@"; }
log_debug() { log $LOG_DEBUG "$@"; }

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLEANUP AND ERROR HANDLING
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

cleanup() {
    local exit_code=$?

    log_debug "Running cleanup (exit code: $exit_code)"

    # Cleanup temporary files
    if [[ -n "${TEMP_FILE:-}" && -f "$TEMP_FILE" ]]; then
        rm -f "$TEMP_FILE"
        log_debug "Removed temp file: $TEMP_FILE"
    fi

    # Cleanup temporary directory
    if [[ -n "${TEMP_DIR:-}" && -d "$TEMP_DIR" ]]; then
        rm -rf "$TEMP_DIR"
        log_debug "Removed temp directory: $TEMP_DIR"
    fi

    exit "$exit_code"
}

trap cleanup EXIT INT TERM

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VALIDATION FUNCTIONS
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

check_dependencies() {
    local missing=()
    local -a required=(curl jq systemctl)

    for cmd in "${required[@]}"; do
        if ! command -v "$cmd" &>/dev/null; then
            missing+=("$cmd")
        fi
    done

    if [[ ${#missing[@]} -gt 0 ]]; then
        log_error "Missing required commands: ${missing[*]}"
        return $EXIT_MISSING_DEPENDENCY
    fi

    log_debug "All dependencies satisfied"
    return 0
}

validate_file() {
    local file="$1"

    if [[ ! -f "$file" ]]; then
        log_error "File not found: $file"
        return 1
    fi

    if [[ ! -r "$file" ]]; then
        log_error "File not readable: $file"
        return 1
    fi

    return 0
}

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BUSINESS LOGIC FUNCTIONS
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

start_app() {
    log_info "Starting $APP_NAME..."

    # Check if already running
    if [[ -f "$PID_FILE" ]]; then
        local pid
        pid=$(<"$PID_FILE")

        if kill -0 "$pid" 2>/dev/null; then
            log_warn "$APP_NAME is already running (PID: $pid)"
            return 0
        else
            log_warn "Removing stale PID file"
            rm -f "$PID_FILE"
        fi
    fi

    # Start application
    "$APP_DIR/app" &
    local pid=$!

    # Save PID
    echo "$pid" > "$PID_FILE"

    # Verify it started
    sleep 2
    if kill -0 "$pid" 2>/dev/null; then
        log_info "$APP_NAME started successfully (PID: $pid)"
        return 0
    else
        log_error "$APP_NAME failed to start"
        rm -f "$PID_FILE"
        return 1
    fi
}

stop_app() {
    log_info "Stopping $APP_NAME..."

    if [[ ! -f "$PID_FILE" ]]; then
        log_warn "$APP_NAME is not running (no PID file)"
        return 0
    fi

    local pid
    pid=$(<"$PID_FILE")

    if ! kill -0 "$pid" 2>/dev/null; then
        log_warn "$APP_NAME is not running (stale PID file)"
        rm -f "$PID_FILE"
        return 0
    fi

    # Send TERM signal
    kill -TERM "$pid" 2>/dev/null || true

    # Wait for graceful shutdown
    local timeout=30
    local waited=0
    while kill -0 "$pid" 2>/dev/null; do
        if [[ $waited -ge $timeout ]]; then
            log_warn "Graceful shutdown timeout, force killing..."
            kill -KILL "$pid" 2>/dev/null || true
            break
        fi
        sleep 1
        ((waited++))
    done

    rm -f "$PID_FILE"
    log_info "$APP_NAME stopped successfully"
    return 0
}

status_app() {
    if [[ ! -f "$PID_FILE" ]]; then
        echo "$APP_NAME is not running"
        return 1
    fi

    local pid
    pid=$(<"$PID_FILE")

    if kill -0 "$pid" 2>/dev/null; then
        echo "$APP_NAME is running (PID: $pid)"
        return 0
    else
        echo "$APP_NAME is not running (stale PID file)"
        return 1
    fi
}

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COMMAND LINE INTERFACE
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

usage() {
    cat <<EOF
Usage: $SCRIPT_NAME [COMMAND] [OPTIONS]

Manage $APP_NAME application lifecycle.

Commands:
    start       Start the application
    stop        Stop the application
    restart     Restart the application
    status      Show application status

Options:
    -h, --help      Show this help message
    -v, --verbose   Enable verbose output
    -V, --version   Show version
    -c, --config    Config file path

Examples:
    $SCRIPT_NAME start
    $SCRIPT_NAME stop
    $SCRIPT_NAME restart
    $SCRIPT_NAME status

EOF
}

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN FUNCTION
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

main() {
    # Parse options
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                usage
                exit $EXIT_SUCCESS
                ;;
            -v|--verbose)
                LOG_LEVEL=$LOG_DEBUG
                shift
                ;;
            -V|--version)
                echo "$SCRIPT_NAME version $SCRIPT_VERSION"
                exit $EXIT_SUCCESS
                ;;
            -c|--config)
                CONFIG_FILE="$2"
                shift 2
                ;;
            start|stop|restart|status)
                COMMAND="$1"
                shift
                break
                ;;
            -*)
                log_error "Unknown option: $1"
                usage
                exit $EXIT_INVALID_ARGS
                ;;
            *)
                COMMAND="$1"
                shift
                break
                ;;
        esac
    done

    # Check dependencies
    check_dependencies || exit $EXIT_MISSING_DEPENDENCY

    # Execute command
    case "${COMMAND:-}" in
        start)
            start_app
            ;;
        stop)
            stop_app
            ;;
        restart)
            stop_app
            start_app
            ;;
        status)
            status_app
            ;;
        *)
            log_error "Missing or unknown command: ${COMMAND:-}"
            usage
            exit $EXIT_INVALID_ARGS
            ;;
    esac
}

# Run main function
main "$@"
```

---

## Pattern 2: Argument Parsing with getopt

### Advanced Command-Line Parsing

```bash
#!/usr/bin/env bash

set -euo pipefail

readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

usage() {
    cat <<EOF
Usage: $SCRIPT_NAME [OPTIONS] <input-file>

Process input file with various options.

Options:
    -h, --help              Show this help message
    -v, --verbose           Enable verbose output
    -o, --output FILE       Output file (default: stdout)
    -f, --format FORMAT     Output format: json|csv|xml (default: json)
    -c, --config FILE       Config file path
    -d, --dry-run           Don't write output, just validate
    -q, --quiet             Suppress non-error output
    -n, --number NUM        Process N records (default: all)
    -k, --key VALUE         Set configuration key

Examples:
    $SCRIPT_NAME input.txt
    $SCRIPT_NAME -v -o output.json input.txt
    $SCRIPT_NAME --format csv --output results.csv data.txt
    $SCRIPT_NAME -k api_key=abc123 -k timeout=30 input.txt

EOF
}

parse_args() {
    # Define short and long options
    local short_opts="hvo:f:c:dqn:k:"
    local long_opts="help,verbose,output:,format:,config:,dry-run,quiet,number:,key:"

    # Parse using getopt
    local parsed
    if ! parsed=$(getopt -o "$short_opts" -l "$long_opts" -n "$SCRIPT_NAME" -- "$@"); then
        usage
        exit 1
    fi

    eval set -- "$parsed"

    # Default values
    local output_file=""
    local format="json"
    local config_file=""
    local verbose=false
    local dry_run=false
    local quiet=false
    local number_records=0
    declare -A config_keys

    # Process options
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
            -f|--format)
                format="$2"
                # Validate format
                case "$format" in
                    json|csv|xml) ;;
                    *)
                        echo "Error: Invalid format: $format" >&2
                        usage
                        exit 1
                        ;;
                esac
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
            -d|--dry-run)
                dry_run=true
                shift
                ;;
            -q|--quiet)
                quiet=true
                shift
                ;;
            -n|--number)
                number_records="$2"
                if [[ ! "$number_records" =~ ^[0-9]+$ ]]; then
                    echo "Error: Number must be an integer: $number_records" >&2
                    exit 1
                fi
                shift 2
                ;;
            -k|--key)
                # Parse key=value
                local key="${2%%=*}"
                local value="${2#*=}"
                config_keys["$key"]="$value"
                shift 2
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

    # Remaining positional arguments
    local -a input_files=("$@")

    # Validate required arguments
    if [[ ${#input_files[@]} -eq 0 ]]; then
        echo "Error: Missing required input file" >&2
        usage
        exit 1
    fi

    # Export parsed values
    export PARSED_OUTPUT_FILE="$output_file"
    export PARSED_FORMAT="$format"
    export PARSED_CONFIG_FILE="$config_file"
    export PARSED_VERBOSE="$verbose"
    export PARSED_DRY_RUN="$dry_run"
    export PARSED_QUIET="$quiet"
    export PARSED_NUMBER_RECORDS="$number_records"
    export PARSED_INPUT_FILES=("${input_files[@]}")

    # Export config keys
    for key in "${!config_keys[@]}"; do
        export "PARSED_CONFIG_${key}=${config_keys[$key]}"
    done
}

# Parse arguments
parse_args "$@"

# Use parsed values
if [[ "$PARSED_VERBOSE" = true ]]; then
    echo "Verbose mode enabled"
    echo "Output: ${PARSED_OUTPUT_FILE:-stdout}"
    echo "Format: $PARSED_FORMAT"
    echo "Input files: ${PARSED_INPUT_FILES[*]}"
fi
```

---

## Pattern 3: Configuration File Loading

### Multi-Format Configuration

```bash
#!/usr/bin/env bash

set -euo pipefail

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Configuration Loading Functions
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Load KEY=VALUE format
load_env_config() {
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

        # Remove quotes from value
        value="${value%\"}"
        value="${value#\"}"

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

# Load INI format [section] key=value
load_ini_config() {
    local config_file="$1"
    local current_section=""

    if [[ ! -f "$config_file" ]]; then
        echo "Error: Config file not found: $config_file" >&2
        return 1
    fi

    while IFS= read -r line; do
        # Skip comments and empty lines
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "$line" ]] && continue

        # Section header
        if [[ "$line" =~ ^\[(.+)\]$ ]]; then
            current_section="${BASH_REMATCH[1]}"
            continue
        fi

        # Key=value pair
        if [[ "$line" =~ ^([^=]+)=(.*)$ ]]; then
            local key="${BASH_REMATCH[1]}"
            local value="${BASH_REMATCH[2]}"

            # Remove whitespace
            key="${key#"${key%%[![:space:]]*}"}"
            key="${key%"${key##*[![:space:]]}"}"
            value="${value#"${value%%[![:space:]]*}"}"
            value="${value%"${value##*[![:space:]]}"}"

            # Export with section prefix
            if [[ -n "$current_section" ]]; then
                export "CONFIG_${current_section}_${key}=$value"
            else
                export "CONFIG_${key}=$value"
            fi
        fi
    done < "$config_file"

    return 0
}

# Load JSON format (requires jq)
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

    # Extract values (example structure)
    export CONFIG_DATABASE_URL=$(jq -r '.database.url' "$config_file")
    export CONFIG_DATABASE_NAME=$(jq -r '.database.name' "$config_file")
    export CONFIG_API_KEY=$(jq -r '.api.key' "$config_file")
    export CONFIG_API_TIMEOUT=$(jq -r '.api.timeout' "$config_file")

    # Validate required fields
    if [[ "$CONFIG_DATABASE_URL" == "null" || -z "$CONFIG_DATABASE_URL" ]]; then
        echo "Error: Missing database.url in config" >&2
        return 1
    fi

    return 0
}

# Load YAML format (requires yq or python)
load_yaml_config() {
    local config_file="$1"

    if command -v yq &>/dev/null; then
        # Using yq
        export CONFIG_DATABASE_URL=$(yq e '.database.url' "$config_file")
        export CONFIG_API_KEY=$(yq e '.api.key' "$config_file")
    elif command -v python3 &>/dev/null; then
        # Using Python with PyYAML
        python3 <<EOF
import yaml
import os

with open('$config_file', 'r') as f:
    config = yaml.safe_load(f)

os.environ['CONFIG_DATABASE_URL'] = config['database']['url']
os.environ['CONFIG_API_KEY'] = config['api']['key']
EOF
    else
        echo "Error: yq or python3 required for YAML parsing" >&2
        return 1
    fi

    return 0
}

# Auto-detect and load config
load_config() {
    local config_file="$1"

    case "$config_file" in
        *.json)
            load_json_config "$config_file"
            ;;
        *.ini|*.conf)
            load_ini_config "$config_file"
            ;;
        *.yaml|*.yml)
            load_yaml_config "$config_file"
            ;;
        *.env|*)
            load_env_config "$config_file"
            ;;
    esac
}
```

---

## Pattern 4: Temporary File Handling

### Secure Temporary Resources

```bash
#!/usr/bin/env bash

set -euo pipefail

# Global temp file/directory tracking
declare -a TEMP_FILES=()
declare -a TEMP_DIRS=()

# Create secure temporary file
create_temp_file() {
    local template="${1:-/tmp/$(basename "$0").XXXXXX}"
    local temp_file

    temp_file=$(mktemp "$template") || {
        echo "Error: Failed to create temporary file" >&2
        return 1
    }

    # Set restrictive permissions
    chmod 600 "$temp_file"

    # Track for cleanup
    TEMP_FILES+=("$temp_file")

    echo "$temp_file"
    return 0
}

# Create secure temporary directory
create_temp_dir() {
    local template="${1:-/tmp/$(basename "$0").XXXXXX}"
    local temp_dir

    temp_dir=$(mktemp -d "$template") || {
        echo "Error: Failed to create temporary directory" >&2
        return 1
    }

    # Set restrictive permissions
    chmod 700 "$temp_dir"

    # Track for cleanup
    TEMP_DIRS+=("$temp_dir")

    echo "$temp_dir"
    return 0
}

# Cleanup all temporary resources
cleanup_temp_resources() {
    local exit_code=$?

    # Clean up temporary files
    for temp_file in "${TEMP_FILES[@]}"; do
        if [[ -f "$temp_file" ]]; then
            rm -f "$temp_file"
        fi
    done

    # Clean up temporary directories
    for temp_dir in "${TEMP_DIRS[@]}"; do
        if [[ -d "$temp_dir" ]]; then
            rm -rf "$temp_dir"
        fi
    done

    exit "$exit_code"
}

# Register cleanup handler
trap cleanup_temp_resources EXIT INT TERM

# Usage example
main() {
    # Create temp file
    local temp_file
    temp_file=$(create_temp_file) || exit 1

    echo "data" > "$temp_file"
    process_file "$temp_file"

    # Create temp directory
    local temp_dir
    temp_dir=$(create_temp_dir) || exit 1

    cp source_files/* "$temp_dir/"
    process_directory "$temp_dir"

    # Cleanup happens automatically on exit
}

main "$@"
```

---

## Pattern 5: Logging Framework

### Production Logging System

```bash
#!/usr/bin/env bash

set -euo pipefail

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Logging Configuration
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Logging levels
readonly LOG_LEVEL_ERROR=0
readonly LOG_LEVEL_WARN=1
readonly LOG_LEVEL_INFO=2
readonly LOG_LEVEL_DEBUG=3
readonly LOG_LEVEL_TRACE=4

# Current log level
LOG_LEVEL=${LOG_LEVEL:-$LOG_LEVEL_INFO}

# Log file
LOG_FILE=${LOG_FILE:-/var/log/$(basename "$0" .sh).log}

# Log to both file and console
LOG_TO_CONSOLE=${LOG_TO_CONSOLE:-true}
LOG_TO_FILE=${LOG_TO_FILE:-true}

# Color support
LOG_COLOR=${LOG_COLOR:-true}

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Color Codes
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if [[ "$LOG_COLOR" = true ]]; then
    readonly COLOR_ERROR='\033[0;31m'    # Red
    readonly COLOR_WARN='\033[0;33m'     # Yellow
    readonly COLOR_INFO='\033[0;32m'     # Green
    readonly COLOR_DEBUG='\033[0;36m'    # Cyan
    readonly COLOR_TRACE='\033[0;35m'    # Magenta
    readonly COLOR_RESET='\033[0m'       # Reset
else
    readonly COLOR_ERROR=''
    readonly COLOR_WARN=''
    readonly COLOR_INFO=''
    readonly COLOR_DEBUG=''
    readonly COLOR_TRACE=''
    readonly COLOR_RESET=''
fi

#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Logging Functions
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_log() {
    local level="$1"
    local level_name="$2"
    local color="$3"
    shift 3
    local message="$*"

    # Check if this level should be logged
    [[ $LOG_LEVEL -lt $level ]] && return 0

    local timestamp
    timestamp="$(date '+%Y-%m-%d %H:%M:%S')"

    local log_line="[$timestamp] $level_name: $message"
    local console_line="${color}[$timestamp] $level_name:${COLOR_RESET} $message"

    # Log to file
    if [[ "$LOG_TO_FILE" = true ]]; then
        echo "$log_line" >> "$LOG_FILE"
    fi

    # Log to console
    if [[ "$LOG_TO_CONSOLE" = true ]]; then
        case "$level" in
            $LOG_LEVEL_ERROR|$LOG_LEVEL_WARN)
                echo -e "$console_line" >&2
                ;;
            *)
                echo -e "$console_line"
                ;;
        esac
    fi
}

log_error() { _log $LOG_LEVEL_ERROR "ERROR" "$COLOR_ERROR" "$@"; }
log_warn()  { _log $LOG_LEVEL_WARN  "WARN " "$COLOR_WARN"  "$@"; }
log_info()  { _log $LOG_LEVEL_INFO  "INFO " "$COLOR_INFO"  "$@"; }
log_debug() { _log $LOG_LEVEL_DEBUG "DEBUG" "$COLOR_DEBUG" "$@"; }
log_trace() { _log $LOG_LEVEL_TRACE "TRACE" "$COLOR_TRACE" "$@"; }

# Structured logging (JSON)
log_json() {
    local level="$1"
    local message="$2"
    shift 2

    local timestamp
    timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

    # Build JSON
    local json="{\"timestamp\":\"$timestamp\",\"level\":\"$level\",\"message\":\"$message\""

    # Add extra fields
    while [[ $# -gt 0 ]]; do
        json="$json,\"$1\":\"$2\""
        shift 2
    done

    json="$json}"

    echo "$json" >> "$LOG_FILE"
}
```

This comprehensive set of scripting patterns provides production-ready templates for common Bash scripting scenarios. Each pattern emphasizes security, error handling, and maintainability.
