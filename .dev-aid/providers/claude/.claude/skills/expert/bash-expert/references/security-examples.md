# Bash Security Examples

Comprehensive security examples covering common vulnerabilities in Bash scripts with CVE references and mitigations.

---

## 1. Command Injection (CWE-78)

### CVE-2014-6271 (Shellshock)

**Description**: Bash vulnerability allowing arbitrary code execution through specially crafted environment variables.

**Vulnerable Pattern**:
```bash
# Bash versions < 4.3
# Environment variable can contain function definitions followed by commands
env x='() { :;}; echo vulnerable' bash -c "echo test"
```

**Mitigation**:
```bash
# Always use latest Bash version
# Validate and sanitize all environment variables
# Never trust environment in privileged contexts

validate_env() {
    local var_name="$1"
    local var_value="${!var_name}"

    # Check for shellshock patterns
    if [[ "$var_value" =~ ^\(\)[[:space:]]*\{ ]]; then
        echo "Error: Potential shellshock exploit in $var_name" >&2
        return 1
    fi

    return 0
}
```

### Command Injection via User Input

**Vulnerable Code**:
```bash
#!/bin/bash
# VULNERABLE: Takes user input and executes it

read -p "Enter filename: " filename
cat $filename  # UNSAFE: No quoting

# Even worse
read -p "Enter command: " cmd
eval "$cmd"  # NEVER DO THIS!

# Still bad
git log --author="$user_input"  # If user_input contains "; rm -rf /"
```

**Secure Code**:
```bash
#!/bin/bash
# SECURE: Proper validation and quoting

read -p "Enter filename: " filename

# Validate filename format
if [[ ! "$filename" =~ ^[a-zA-Z0-9._-]+$ ]]; then
    echo "Error: Invalid filename format" >&2
    exit 1
fi

# Check file exists and is regular file
if [[ ! -f "$filename" ]]; then
    echo "Error: File not found or not a regular file" >&2
    exit 1
fi

# Use with proper quoting
cat "$filename"

# For git commands, use array-based execution
read -p "Enter author name: " author

# Validate author name
if [[ ! "$author" =~ ^[a-zA-Z0-9@._ -]+$ ]]; then
    echo "Error: Invalid author name" >&2
    exit 1
fi

# Use array for command
git_cmd=(git log "--author=$author")
"${git_cmd[@]}"
```

**Explanation**: Always validate input format, use proper quoting, never use `eval` with user input, and prefer array-based command execution.

---

## 2. Path Traversal (CWE-22)

### Scenario: User-Controlled File Operations

**Vulnerable Code**:
```bash
#!/bin/bash
# VULNERABLE: Path traversal attack

base_dir="/var/www/uploads"
read -p "Enter filename to view: " filename

# User can enter: ../../../../etc/passwd
cat "$base_dir/$filename"

# Also vulnerable
rm -f "/tmp/user_${username}.txt"  # If username="../../etc/passwd"
```

**Secure Code**:
```bash
#!/bin/bash
# SECURE: Path validation and containment checks

readonly BASE_DIR="/var/www/uploads"

validate_and_read_file() {
    local filename="$1"

    # Remove any directory components
    filename="$(basename "$filename")"

    # Validate filename contains only safe characters
    if [[ ! "$filename" =~ ^[a-zA-Z0-9._-]+$ ]]; then
        echo "Error: Invalid filename" >&2
        return 1
    fi

    # Construct full path
    local full_path="$BASE_DIR/$filename"

    # Resolve to absolute path
    full_path="$(realpath -m "$full_path")"

    # Verify path is still within base directory
    if [[ "$full_path" != "$BASE_DIR"* ]]; then
        echo "Error: Path traversal attempt detected" >&2
        return 1
    fi

    # Check file exists and is regular file
    if [[ ! -f "$full_path" ]]; then
        echo "Error: File not found" >&2
        return 1
    fi

    # Safe to read
    cat "$full_path"
    return 0
}

# Usage
read -p "Enter filename: " user_filename
validate_and_read_file "$user_filename"
```

**Explanation**: Use `basename` to remove directory components, validate filename format, resolve absolute paths, and verify containment within allowed directory.

---

## 3. Race Conditions (CWE-362)

### Scenario: Temporary File Race Condition (TOCTOU)

**Vulnerable Code**:
```bash
#!/bin/bash
# VULNERABLE: Check-then-use race condition

temp_file="/tmp/myapp_$$"

# Check if file exists
if [[ ! -f "$temp_file" ]]; then
    # Race window here!
    # Attacker can create symlink: /tmp/myapp_$$ -> /etc/passwd
    echo "secret data" > "$temp_file"
fi
```

**Secure Code**:
```bash
#!/bin/bash
# SECURE: Atomic operations and secure temp file creation

# Use mktemp for secure temp file creation
temp_file=$(mktemp /tmp/myapp.XXXXXX) || {
    echo "Error: Failed to create temp file" >&2
    exit 1
}

# Set restrictive permissions immediately
chmod 600 "$temp_file"

# Ensure cleanup
trap 'rm -f "$temp_file"' EXIT INT TERM

# Now safe to use
echo "secret data" > "$temp_file"

# Alternative: Use mktemp with directory
temp_dir=$(mktemp -d /tmp/myapp.XXXXXX) || exit 1
trap 'rm -rf "$temp_dir"' EXIT INT TERM
chmod 700 "$temp_dir"

# Create files in secure directory
echo "data" > "$temp_dir/file1.txt"
```

**Explanation**: Use `mktemp` for atomic temp file creation, set restrictive permissions immediately, and use cleanup traps.

---

## 4. Privilege Escalation

### Scenario: Running Scripts with sudo

**Vulnerable Code**:
```bash
#!/bin/bash
# VULNERABLE: Unsafe sudo script

# Script runs as root via sudo
# Takes user input without validation

read -p "Enter service name: " service
sudo systemctl restart "$service"  # User can inject commands

# Environment variables from user
sudo -E /path/to/script.sh  # Inherits user's environment

# PATH manipulation
export PATH="/tmp:$PATH"
sudo some-command  # Might execute /tmp/some-command instead
```

**Secure Code**:
```bash
#!/bin/bash
# SECURE: Proper privilege management

# Validate service name against whitelist
readonly ALLOWED_SERVICES=("nginx" "apache2" "mysql")

restart_service() {
    local service="$1"

    # Validate service is in whitelist
    local found=false
    for allowed in "${ALLOWED_SERVICES[@]}"; do
        if [[ "$service" == "$allowed" ]]; then
            found=true
            break
        fi
    done

    if ! $found; then
        echo "Error: Service not allowed: $service" >&2
        return 1
    fi

    # Validate service name format
    if [[ ! "$service" =~ ^[a-z0-9-]+$ ]]; then
        echo "Error: Invalid service name format" >&2
        return 1
    fi

    # Use absolute path to systemctl
    if ! sudo /usr/bin/systemctl restart "$service"; then
        echo "Error: Failed to restart $service" >&2
        return 1
    fi

    return 0
}

# Drop privileges after initialization
if [[ $EUID -eq 0 ]]; then
    # Running as root, drop to normal user for most operations
    readonly NORMAL_USER="appuser"

    # Do privileged setup here
    setup_privileged_resources

    # Drop privileges
    exec sudo -u "$NORMAL_USER" "$0" "$@"
fi

# Now running as normal user
# Do unprivileged work here

# Reset PATH to safe value
export PATH="/usr/local/bin:/usr/bin:/bin"
```

**Explanation**: Use whitelists for privileged operations, validate all inputs, use absolute paths for commands, drop privileges as soon as possible, and control environment variables.

---

## 5. Information Disclosure

### Scenario: Leaking Sensitive Data in Errors

**Vulnerable Code**:
```bash
#!/bin/bash
# VULNERABLE: Leaks sensitive information

API_KEY="sk-secret-1234567890"

# Error shows API key
curl -H "Authorization: Bearer $API_KEY" https://api.example.com/data || {
    echo "Error: curl failed with key: $API_KEY" >&2
    exit 1
}

# Debug mode exposes secrets
set -x  # All commands shown including secrets
curl -u "admin:$PASSWORD" https://example.com/
set +x

# Password in process list
mysql -u root -p"$DB_PASSWORD" -e "SELECT * FROM users"
```

**Secure Code**:
```bash
#!/bin/bash
# SECURE: Protects sensitive data

# Load secrets from secure source
if [[ -f "$HOME/.secrets/api_key" ]]; then
    API_KEY=$(<"$HOME/.secrets/api_key")
elif [[ -n "$API_KEY_ENV" ]]; then
    API_KEY="$API_KEY_ENV"
else
    echo "Error: API key not configured" >&2
    exit 1
fi

# Validate API key format without exposing it
if [[ ! "$API_KEY" =~ ^sk-[a-zA-Z0-9]{32,}$ ]]; then
    echo "Error: Invalid API key format" >&2
    exit 1
fi

# Use without exposing in errors
if ! curl -H "Authorization: Bearer $API_KEY" https://api.example.com/data 2>/tmp/curl_error.log; then
    echo "Error: API request failed (check logs for details)" >&2
    # Log file should have restricted permissions
    exit 1
fi

# Use credential files instead of command-line arguments
cat > /tmp/my.cnf <<EOF
[client]
user=root
password=$DB_PASSWORD
EOF
chmod 600 /tmp/my.cnf
trap 'rm -f /tmp/my.cnf' EXIT

mysql --defaults-extra-file=/tmp/my.cnf -e "SELECT * FROM users"

# Use process substitution for sensitive input
mysql -u root -p <(echo "$DB_PASSWORD") -e "SELECT * FROM users"
```

**Explanation**: Load secrets from secure sources, never echo secrets in error messages, use credential files instead of command-line arguments, and clean up sensitive temporary files.

---

## 6. Denial of Service

### Scenario: Resource Exhaustion

**Vulnerable Code**:
```bash
#!/bin/bash
# VULNERABLE: No resource limits

# Unbounded loop
while true; do
    process_data &  # Fork bomb potential
done

# No limit on file size
cat /dev/urandom > largefile.dat

# Recursive function without limit
process() {
    process &
    process &
}
process
```

**Secure Code**:
```bash
#!/bin/bash
# SECURE: Resource limits and bounds

# Set resource limits
ulimit -v 1048576  # 1GB virtual memory limit
ulimit -f 1048576  # 1GB file size limit
ulimit -u 100      # Max 100 processes

# Bounded parallel processing
readonly MAX_JOBS=4
declare -a pids=()

for item in "${items[@]}"; do
    # Limit concurrent jobs
    while [[ ${#pids[@]} -ge $MAX_JOBS ]]; do
        # Wait for any job to finish
        wait -n
        # Remove finished jobs from array
        for i in "${!pids[@]}"; do
            if ! kill -0 "${pids[$i]}" 2>/dev/null; then
                unset 'pids[$i]'
            fi
        done
        pids=("${pids[@]}")  # Reindex array
    done

    process_data "$item" &
    pids+=($!)
done

# Wait for remaining jobs
wait

# Limit recursion depth
process_recursive() {
    local depth="${1:-0}"
    local max_depth=10

    if [[ $depth -ge $max_depth ]]; then
        echo "Error: Max recursion depth reached" >&2
        return 1
    fi

    # Do work
    process_recursive $((depth + 1))
}

# Timeout for operations
timeout 30 long_running_command || {
    echo "Error: Operation timed out" >&2
    exit 1
}
```

**Explanation**: Set resource limits with `ulimit`, bound loops and parallelism, limit recursion depth, and use timeouts for operations.

---

## 7. Insecure Randomness (CWE-330)

### Scenario: Using Predictable Random Values

**Vulnerable Code**:
```bash
#!/bin/bash
# VULNERABLE: Predictable random values

# $RANDOM is not cryptographically secure
session_id=$RANDOM
token="${RANDOM}${RANDOM}${RANDOM}"

# Predictable temp file names
temp_file="/tmp/session_$$"  # PID is predictable
```

**Secure Code**:
```bash
#!/bin/bash
# SECURE: Cryptographically secure random values

# Use /dev/urandom for secure randomness
generate_secure_token() {
    local length="${1:-32}"

    # Generate hex token
    xxd -l "$length" -p /dev/urandom | tr -d '\n'
}

# Or use openssl
generate_secure_token_openssl() {
    local length="${1:-32}"
    openssl rand -hex "$length"
}

# Secure session ID
session_id=$(generate_secure_token 32)

# Secure temp file
temp_file=$(mktemp)  # Uses secure random template
chmod 600 "$temp_file"

# Secure password generation
generate_password() {
    local length="${1:-20}"

    # Generate strong password
    tr -dc 'A-Za-z0-9!@#$%^&*' < /dev/urandom | head -c "$length"
    echo
}
```

**Explanation**: Use `/dev/urandom` or `openssl rand` for cryptographic randomness, never use `$RANDOM` for security-sensitive values, and use `mktemp` for secure temp files.

---

## 8. Input Validation Bypass

### Scenario: Incomplete Validation

**Vulnerable Code**:
```bash
#!/bin/bash
# VULNERABLE: Incomplete validation

read -p "Enter email: " email

# Weak validation
if [[ "$email" == *"@"* ]]; then
    echo "Valid email: $email"
else
    echo "Invalid email"
fi

# Bypassable with: admin@evil.com OR user@localhost; rm -rf /
```

**Secure Code**:
```bash
#!/bin/bash
# SECURE: Comprehensive validation

validate_email() {
    local email="$1"

    # Comprehensive regex for email
    local regex='^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if [[ ! "$email" =~ $regex ]]; then
        echo "Error: Invalid email format" >&2
        return 1
    fi

    # Additional checks
    local domain="${email##*@}"

    # Check no shell metacharacters
    if [[ "$email" =~ [;\|\&\$\`] ]]; then
        echo "Error: Invalid characters in email" >&2
        return 1
    fi

    # Validate length
    if [[ ${#email} -gt 254 ]]; then
        echo "Error: Email too long" >&2
        return 1
    fi

    # Check domain has at least one dot
    if [[ ! "$domain" == *.* ]]; then
        echo "Error: Invalid domain" >&2
        return 1
    fi

    return 0
}

# Validate URL
validate_url() {
    local url="$1"

    # Comprehensive URL validation
    local regex='^https?://[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*(/[a-zA-Z0-9._~:/?#\[\]@!$&'\''()*+,;=-]*)?$'

    if [[ ! "$url" =~ $regex ]]; then
        echo "Error: Invalid URL format" >&2
        return 1
    fi

    # Ensure HTTPS for sensitive operations
    if [[ "$url" != https://* ]]; then
        echo "Warning: URL is not HTTPS" >&2
    fi

    # Blocklist dangerous domains
    local -a blocked_domains=("localhost" "127.0.0.1" "0.0.0.0" "169.254.169.254")
    local domain="${url#*://}"
    domain="${domain%%/*}"

    for blocked in "${blocked_domains[@]}"; do
        if [[ "$domain" == *"$blocked"* ]]; then
            echo "Error: Blocked domain detected" >&2
            return 1
        fi
    done

    return 0
}
```

**Explanation**: Use comprehensive regex patterns, check for shell metacharacters, validate length constraints, and implement domain/protocol checks.

---

## Security Checklist

Before deploying any Bash script:

### Input Validation
- [ ] All user inputs validated with strict regex patterns
- [ ] No shell metacharacters allowed in untrusted input
- [ ] File paths checked for traversal attempts
- [ ] Numeric inputs validated for type and range
- [ ] URL/email formats validated comprehensively

### Command Execution
- [ ] All variable expansions quoted
- [ ] No use of `eval` with untrusted input
- [ ] Commands use array-based execution
- [ ] Absolute paths used for critical commands
- [ ] Command existence checked before execution

### File Operations
- [ ] Temporary files created with `mktemp`
- [ ] File permissions set to 600/700 for sensitive files
- [ ] Cleanup traps configured
- [ ] Path containment verified
- [ ] Race conditions avoided

### Privilege Management
- [ ] Privileges dropped as soon as possible
- [ ] Whitelist approach for privileged operations
- [ ] No unsafe sudo usage
- [ ] Environment sanitized for privileged contexts

### Secrets Management
- [ ] No hardcoded secrets in scripts
- [ ] Secrets loaded from secure sources (env, files, managers)
- [ ] Secrets never exposed in error messages or logs
- [ ] Credential files use restrictive permissions
- [ ] Temporary files with secrets cleaned up

### Resource Management
- [ ] Resource limits set (ulimit)
- [ ] Parallelism bounded
- [ ] Timeouts configured for operations
- [ ] Recursion depth limited

### Error Handling
- [ ] `set -euo pipefail` enabled
- [ ] All critical operations error-checked
- [ ] Safe error messages (no sensitive data)
- [ ] Cleanup on error via trap

### Randomness
- [ ] `/dev/urandom` or `openssl rand` for crypto operations
- [ ] Never use `$RANDOM` for security-sensitive values
- [ ] Secure tokens have sufficient length (32+ bytes)
