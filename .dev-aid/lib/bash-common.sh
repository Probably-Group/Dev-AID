#!/usr/bin/env bash
# Shared Bash security and utility functions for Dev-AID
# Compliant with bash-expert skill (HIGH-RISK) requirements
#
# Usage: source "${SCRIPT_DIR}/.dev-aid/lib/bash-common.sh"

set -euo pipefail

# Validate path is within allowed base directory (CWE-22: Path Traversal)
validate_path_containment() {
    local path="$1"
    local base="$2"
    local resolved_path
    local resolved_base

    # Resolve to absolute paths
    # Note: realpath -m is GNU coreutils; falls through to error on macOS without it
    resolved_path="$(realpath -m "$path" 2>/dev/null)" || {
        echo "Error: Failed to resolve path: $path" >&2
        return 1
    }

    resolved_base="$(realpath -m "$base" 2>/dev/null)" || {
        echo "Error: Failed to resolve base directory: $base" >&2
        return 1
    }

    # Check containment
    if [[ "$resolved_path" != "${resolved_base}/"* && "$resolved_path" != "${resolved_base}" ]]; then
        echo "Error: Path traversal attempt detected: $path is outside $base" >&2
        return 1
    fi

    # Check for null bytes
    if [[ "$resolved_path" =~ $'\0' ]]; then
        echo "Error: Path contains null bytes" >&2
        return 1
    fi

    return 0
}

# Validate input doesn't contain shell metacharacters (CWE-78: Command Injection)
validate_safe_input() {
    local input="$1"
    local field_name="${2:-input}"

    # Check for shell metacharacters
    if [[ "$input" =~ [\;\|\&\$\`\(\)\<\>] ]]; then
        echo "Error: Invalid characters in $field_name" >&2
        return 1
    fi

    # Check for null bytes
    if [[ "$input" =~ $'\0' ]]; then
        echo "Error: Null bytes in $field_name" >&2
        return 1
    fi

    # Check reasonable length (prevent DoS)
    if [[ ${#input} -gt 10000 ]]; then
        echo "Error: $field_name too long (max 10000 characters)" >&2
        return 1
    fi

    return 0
}

# Create secure temporary file (CWE-377: Insecure Temporary File)
create_secure_temp() {
    local template="${1:-/tmp/dev-aid.XXXXXX}"
    local temp_file

    # Create temp file atomically
    temp_file=$(mktemp "$template") || {
        echo "Error: Failed to create temporary file" >&2
        return 1
    }

    # Set restrictive permissions immediately
    chmod 600 "$temp_file" || {
        rm -f "$temp_file"
        echo "Error: Failed to set temp file permissions" >&2
        return 1
    }

    echo "$temp_file"
}

# Secure cleanup of temporary file
secure_cleanup_file() {
    local file="$1"

    if [[ -f "$file" ]]; then
        # Use shred if available, otherwise rm
        if command -v shred >/dev/null 2>&1; then
            shred -u "$file" 2>/dev/null || rm -f "$file"
        else
            rm -f "$file"
        fi
    fi
}

# Validate environment variable is set and safe (CVE-2014-6271: Shellshock)
validate_env_var() {
    local var_name="$1"
    local var_value="${!var_name:-}"
    local required="${2:-true}"

    # Check if variable is set
    if [[ -z "$var_value" ]]; then
        if [[ "$required" == "true" ]]; then
            echo "Error: Required environment variable $var_name not set" >&2
            return 1
        else
            return 0
        fi
    fi

    # Check for shellshock pattern (CVE-2014-6271)
    if [[ "$var_value" =~ ^\(\)[[:space:]]*\{ ]]; then
        echo "Error: Potential shellshock exploit detected in $var_name" >&2
        return 1
    fi

    # Check for null bytes
    if [[ "$var_value" =~ $'\0' ]]; then
        echo "Error: Null bytes in $var_name" >&2
        return 1
    fi

    return 0
}

# Validate command exists and is in expected location
validate_command() {
    local cmd="$1"
    local expected_path="${2:-}"
    local actual_path

    # Check command exists
    if ! actual_path=$(command -v "$cmd" 2>/dev/null); then
        echo "Error: Command not found: $cmd" >&2
        return 1
    fi

    # Verify location if specified
    if [[ -n "$expected_path" && "$actual_path" != "$expected_path" ]]; then
        echo "Error: Command location mismatch for $cmd" >&2
        echo "Expected: $expected_path, Got: $actual_path" >&2
        return 1
    fi

    return 0
}

# Sanitize environment for secure execution
sanitize_environment() {
    # Reset PATH to safe value
    export PATH="/usr/local/bin:/usr/bin:/bin"

    # Unset dangerous environment variables
    unset LD_PRELOAD 2>/dev/null || true
    unset LD_LIBRARY_PATH 2>/dev/null || true
    unset BASH_ENV 2>/dev/null || true
    unset ENV 2>/dev/null || true

    return 0
}

# Validate numeric input
validate_numeric() {
    local value="$1"
    local field_name="${2:-value}"
    local min="${3:--2147483648}"  # INT_MIN
    local max="${4:-2147483647}"   # INT_MAX

    # Check if numeric
    if ! [[ "$value" =~ ^-?[0-9]+$ ]]; then
        echo "Error: $field_name must be numeric" >&2
        return 1
    fi

    # Check range
    if [[ $value -lt $min || $value -gt $max ]]; then
        echo "Error: $field_name out of range [$min, $max]" >&2
        return 1
    fi

    return 0
}

# Validate file exists and is readable
validate_file_readable() {
    local file="$1"
    local file_desc="${2:-file}"

    if [[ ! -f "$file" ]]; then
        echo "Error: $file_desc not found: $file" >&2
        return 1
    fi

    if [[ ! -r "$file" ]]; then
        echo "Error: $file_desc not readable: $file" >&2
        return 1
    fi

    return 0
}

# Validate directory exists and is accessible
validate_directory() {
    local dir="$1"
    local dir_desc="${2:-directory}"

    if [[ ! -d "$dir" ]]; then
        echo "Error: $dir_desc not found: $dir" >&2
        return 1
    fi

    if [[ ! -r "$dir" || ! -x "$dir" ]]; then
        echo "Error: $dir_desc not accessible: $dir" >&2
        return 1
    fi

    return 0
}

# Safe source of external files
safe_source() {
    local file="$1"
    local base_dir="${2:-}"

    # Validate file is readable
    validate_file_readable "$file" "source file" || return 1

    # Validate containment if base_dir specified
    if [[ -n "$base_dir" ]]; then
        validate_path_containment "$file" "$base_dir" || return 1
    fi

    # shellcheck source=/dev/null
    source "$file"
}

# Log with timestamp (for audit trail)
log_message() {
    local level="$1"
    shift
    local message="$*"
    local timestamp

    timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
    echo "[${timestamp}] [${level}] ${message}" >&2
}

# Error logging
log_error() {
    log_message "ERROR" "$@"
}

# Warning logging
log_warning() {
    log_message "WARN" "$@"
}

# Info logging
log_info() {
    log_message "INFO" "$@"
}

# Check if running with elevated privileges
check_not_root() {
    if [[ $EUID -eq 0 ]]; then
        echo "Error: This script should not be run as root" >&2
        return 1
    fi
    return 0
}

# Check minimum Bash version
check_bash_version() {
    local min_version="${1:-4.0}"
    local current_version="${BASH_VERSION%%.*}"

    if [[ "$current_version" -lt "${min_version%%.*}" ]]; then
        echo "Error: Bash version $min_version or higher required (current: $BASH_VERSION)" >&2
        return 1
    fi

    return 0
}

# Export functions for use in scripts
export -f validate_path_containment
export -f validate_safe_input
export -f create_secure_temp
export -f secure_cleanup_file
export -f validate_env_var
export -f validate_command
export -f sanitize_environment
export -f validate_numeric
export -f validate_file_readable
export -f validate_directory
export -f safe_source
export -f log_message
export -f log_error
export -f log_warning
export -f log_info
export -f check_not_root
export -f check_bash_version
