#!/usr/bin/env bash
# Dev-AID Update Library
# Shared functions for update system
# Version: 1.0.0

set -euo pipefail

# Colors for output
export GREEN='\033[0;32m'
export BLUE='\033[0;34m'
export YELLOW='\033[1;33m'
export RED='\033[0;31m'
export CYAN='\033[0;36m'
export NC='\033[0m' # No Color

# ============================================================================
# Version Comparison Functions
# ============================================================================

# Parse semantic version (removes 'v' prefix and pre-release suffixes)
parse_version() {
    local version="$1"
    # Remove 'v' prefix
    version=${version#v}
    # Remove pre-release suffixes (-beta, -rc, etc)
    version=${version%%-*}
    echo "$version"
}

# Check if version A > version B
# Returns: 0 (true) if v1 > v2, 1 (false) otherwise
is_version_greater() {
    # shellcheck disable=SC2155
    local v1=$(parse_version "$1")
    # shellcheck disable=SC2155
    local v2=$(parse_version "$2")

    # Use sort -V for semantic version comparison
    if [[ "$(printf '%s\n' "$v1" "$v2" | sort -V | tail -n1)" == "$v1" && "$v1" != "$v2" ]]; then
        return 0  # v1 > v2
    else
        return 1  # v1 <= v2
    fi
}

# Check for breaking changes (major version bump)
# Returns: 0 (true) if breaking changes, 1 (false) otherwise
has_breaking_changes() {
    # shellcheck disable=SC2155
    local current=$(parse_version "$1")
    # shellcheck disable=SC2155
    local new=$(parse_version "$2")

    # shellcheck disable=SC2155
    local curr_major=$(echo "$current" | cut -d. -f1)
    # shellcheck disable=SC2155
    local new_major=$(echo "$new" | cut -d. -f1)

    [[ "$new_major" != "$curr_major" ]]
}

# Display breaking change warning
check_breaking_changes() {
    local current="$1"
    local new="$2"

    if has_breaking_changes "$current" "$new"; then
        echo ""
        echo -e "${RED}⚠️  BREAKING CHANGES DETECTED${NC}"
        echo -e "${YELLOW}   Current version: $current${NC}"
        echo -e "${YELLOW}   New version:     $new${NC}"
        echo ""
        echo "   Major version changed - may require migration"
        echo "   Review changelog: .dev-aid/CHANGELOG.md"
        echo ""

        read -p "Continue with update? [y/N]: " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${RED}❌ Update cancelled by user${NC}"
            exit 0
        fi
    fi
}

# ============================================================================
# Backup Functions
# ============================================================================

# Create timestamped backup of user data
# Returns: Backup directory path
create_backup() {
    # shellcheck disable=SC2155
    local backup_dir=".dev-aid-backup-$(date +%Y%m%d-%H%M%S)"

    echo -e "${GREEN}Creating backup...${NC}"
    mkdir -p "$backup_dir"

    # Backup critical user data that should NEVER be overwritten
    echo -e "${BLUE}→ Backing up user data...${NC}"

    # API keys and configuration
    cp -r .dev-aid/config/.env* "$backup_dir/" 2>/dev/null || true

    # Memory bank (user's patterns, decisions, context)
    if [ -d ".dev-aid/memory-bank" ]; then
        cp -r .dev-aid/memory-bank "$backup_dir/"
    fi

    # Logs (routing history, costs)
    if [ -d ".dev-aid/logs" ]; then
        cp -r .dev-aid/logs "$backup_dir/"
    fi

    # RAG indices (expensive to rebuild)
    if [ -d ".dev-aid/local-search/index" ]; then
        mkdir -p "$backup_dir/local-search"
        cp -r .dev-aid/local-search/index "$backup_dir/local-search/" 2>/dev/null || true
    fi

    # Custom user-created skills
    if [ -d ".dev-aid/providers" ]; then
        for provider_dir in .dev-aid/providers/*/; do
            if [ -d "${provider_dir}skills/custom" ]; then
                provider_name=$(basename "$provider_dir")
                mkdir -p "$backup_dir/providers/$provider_name/skills"
                cp -r "${provider_dir}skills/custom" "$backup_dir/providers/$provider_name/skills/"
            fi
        done
    fi

    # VERSION file (for rollback reference)
    cp .dev-aid/VERSION "$backup_dir/" 2>/dev/null || true

    # Agent prompt versions (APO-optimized prompts)
    if [ -d ".dev-aid/agent-prompts" ]; then
        cp -r .dev-aid/agent-prompts "$backup_dir/"
    fi
    # Golden test cases (user-defined)
    if [ -f ".dev-aid/config/golden-tests.json" ]; then
        cp .dev-aid/config/golden-tests.json "$backup_dir/"
    fi

    # Create manifest of what was backed up
    cat > "$backup_dir/MANIFEST.txt" <<EOF
Dev-AID Backup Manifest
Created: $(date)
Current Version: $(cat .dev-aid/VERSION 2>/dev/null || echo "unknown")

Backed up:
- API keys (.env files)
- Memory bank
- Logs
- RAG indices
- Custom skills
- VERSION file
- Agent prompt versions (APO)
- Golden test cases

To restore this backup:
  ./.dev-aid/scripts/rollback.sh $backup_dir
EOF

    echo -e "${GREEN}✓ Backup created: ${backup_dir}${NC}"
    echo "$backup_dir"
}

# Clean up old backups (keep only N most recent)
cleanup_old_backups() {
    local keep_count="${1:-3}"  # Default: keep 3 backups

    # shellcheck disable=SC2012,SC2155
    local backup_count=$(ls -1d .dev-aid-backup-* 2>/dev/null | wc -l)

    if [ "$backup_count" -gt "$keep_count" ]; then
        echo -e "${BLUE}→ Cleaning up old backups (keeping $keep_count most recent)...${NC}"

        # Get list of backups sorted by time (oldest first)
        # shellcheck disable=SC2012,SC2155
        local backups_to_delete=$(ls -1td .dev-aid-backup-* | tail -n +$((keep_count + 1)))

        for backup in $backups_to_delete; do
            echo -e "${YELLOW}  Removing old backup: $backup${NC}"
            rm -rf "$backup"
        done

        echo -e "${GREEN}✓ Cleanup complete${NC}"
    fi
}

# ============================================================================
# Checksum Verification Functions
# ============================================================================

# Verify file integrity with SHA256 checksum
# Args: file_path, expected_checksum
# Returns: 0 if valid, 1 if invalid
verify_checksum() {
    local file="$1"
    local expected="$2"

    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ File not found: $file${NC}"
        return 1
    fi

    echo -e "${BLUE}→ Verifying checksum...${NC}"

    # Calculate actual checksum (cross-platform)
    local actual
    if command -v sha256sum &>/dev/null; then
        actual=$(sha256sum "$file" | cut -d' ' -f1)
    elif command -v shasum &>/dev/null; then
        actual=$(shasum -a 256 "$file" | cut -d' ' -f1)
    else
        echo -e "${YELLOW}⚠️  Warning: No SHA256 tool found, skipping verification${NC}"
        return 0
    fi

    if [[ "$actual" != "$expected" ]]; then
        echo -e "${RED}❌ Checksum mismatch!${NC}"
        echo -e "${RED}   Expected: $expected${NC}"
        echo -e "${RED}   Got:      $actual${NC}"
        echo ""
        echo -e "${RED}   Possible causes:${NC}"
        echo "   - Corrupted download"
        echo "   - MITM attack"
        echo "   - Wrong file downloaded"
        echo ""
        return 1
    fi

    echo -e "${GREEN}✓ Checksum valid${NC}"
    return 0
}

# ============================================================================
# File Modification Detection
# ============================================================================

# Check if file was modified by user (differs from original)
# Args: file_path, original_checksum
# Returns: 0 if modified, 1 if not modified
is_user_modified() {
    local file="$1"
    local original_hash="$2"

    if [ ! -f "$file" ]; then
        return 1  # File doesn't exist, not modified
    fi

    # Calculate current file hash
    local current_hash
    if command -v sha256sum &>/dev/null; then
        current_hash=$(sha256sum "$file" | cut -d' ' -f1)
    elif command -v shasum &>/dev/null; then
        current_hash=$(shasum -a 256 "$file" | cut -d' ' -f1)
    else
        return 1  # Can't determine, assume not modified
    fi

    if [[ "$current_hash" == "$original_hash" ]]; then
        return 1  # Not modified (matches original)
    else
        return 0  # Modified by user
    fi
}

# ============================================================================
# Protected Paths
# ============================================================================

# Get list of paths that should NEVER be overwritten
get_protected_paths() {
    cat <<EOF
.dev-aid/config/.env*
.dev-aid/memory-bank/
.dev-aid/logs/
.dev-aid/local-search/index/
.dev-aid/providers/*/skills/custom/
.dev-aid/agent-traces/
.dev-aid/agent-prompts/
.dev-aid/config/golden-tests.json
EOF
}

# Check if path is protected
# Args: file_path
# Returns: 0 if protected, 1 if not protected
is_protected_path() {
    local path="$1"

    # Check against each protected pattern
    while IFS= read -r pattern; do
        # Convert glob pattern to regex for matching
        # shellcheck disable=SC2053
        if [[ "$path" == $pattern ]]; then
            return 0  # Protected
        fi
    done < <(get_protected_paths)

    return 1  # Not protected
}

# ============================================================================
# Progress Display
# ============================================================================

# Show progress bar
# Args: current, total, label
show_progress() {
    local current="$1"
    local total="$2"
    local label="${3:-Progress}"

    local percent=$((current * 100 / total))
    local filled=$((percent / 2))
    local empty=$((50 - filled))

    # shellcheck disable=SC2059
    printf "\r${BLUE}$label: [${NC}"
    printf "%${filled}s" | tr ' ' '='
    printf "%${empty}s" | tr ' ' ' '
    # shellcheck disable=SC2059
    printf "${BLUE}] $percent%%${NC}"

    if [ "$current" -eq "$total" ]; then
        echo ""  # New line when complete
    fi
}

# ============================================================================
# Dependency Management
# ============================================================================

# Check if required tools are installed
check_dependencies() {
    local missing_deps=()

    # Required tools
    local required_tools=(
        "git"
        "python3"
        "rsync"
    )

    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &>/dev/null; then
            missing_deps+=("$tool")
        fi
    done

    if [ ${#missing_deps[@]} -gt 0 ]; then
        echo -e "${RED}❌ Missing required dependencies:${NC}"
        for dep in "${missing_deps[@]}"; do
            echo "   - $dep"
        done
        echo ""
        echo "Please install missing dependencies and try again."
        return 1
    fi

    return 0
}

# Update Python dependencies in virtual environment
update_python_deps() {
    local venv_path="${1:-.dev-aid/orchestration/.venv}"

    if [ ! -d "$venv_path" ]; then
        echo -e "${YELLOW}⚠️  No virtual environment found at $venv_path${NC}"
        return 1
    fi

    echo -e "${BLUE}→ Updating Python dependencies...${NC}"

    # Activate virtual environment
    # shellcheck disable=SC1091
    source "$venv_path/bin/activate"

    # Upgrade pip
    pip install --upgrade pip -q

    # Install/upgrade requirements
    local req_file=".dev-aid/orchestration/requirements.txt"
    if [ -f "$req_file" ]; then
        pip install -r "$req_file" --upgrade -q
        echo -e "${GREEN}✓ Dependencies updated${NC}"
    else
        echo -e "${YELLOW}⚠️  No requirements.txt found${NC}"
    fi

    # Deactivate
    deactivate

    return 0
}

# ============================================================================
# Error Handling
# ============================================================================

# Global variable for error trap backup directory
_ERROR_TRAP_BACKUP_DIR=""

# Trap handler for automatic rollback on error
setup_error_trap() {
    _ERROR_TRAP_BACKUP_DIR="$1"

    trap 'handle_error "$_ERROR_TRAP_BACKUP_DIR"' ERR
}

# Handle errors with automatic rollback
handle_error() {
    local backup_dir="$1"

    echo ""
    echo -e "${RED}❌ Update failed!${NC}"
    echo ""

    if [ -n "$backup_dir" ] && [ -d "$backup_dir" ]; then
        echo -e "${YELLOW}Attempting automatic rollback...${NC}"

        # Restore from backup
        if restore_from_backup "$backup_dir"; then
            echo -e "${GREEN}✓ Successfully rolled back to previous version${NC}"
            echo ""
            echo "Backup preserved at: $backup_dir"
            echo "Review logs and try updating again later."
        else
            echo -e "${RED}❌ Automatic rollback failed!${NC}"
            echo ""
            echo "Please manually restore from backup:"
            echo "  ./.dev-aid/scripts/rollback.sh $backup_dir"
        fi
    else
        echo "No backup available for automatic rollback."
        echo "You may need to reinstall Dev-AID."
    fi

    exit 1
}

# Restore from backup directory
restore_from_backup() {
    local backup_dir="$1"

    if [ ! -d "$backup_dir" ]; then
        echo -e "${RED}Backup directory not found: $backup_dir${NC}"
        return 1
    fi

    echo -e "${BLUE}→ Restoring from backup...${NC}"

    # Restore user data
    if [ -d "$backup_dir/.env" ]; then
        cp -r "$backup_dir/.env"* .dev-aid/config/ 2>/dev/null || true
    fi

    if [ -d "$backup_dir/memory-bank" ]; then
        cp -r "$backup_dir/memory-bank" .dev-aid/
    fi

    if [ -d "$backup_dir/logs" ]; then
        cp -r "$backup_dir/logs" .dev-aid/
    fi

    if [ -d "$backup_dir/local-search" ]; then
        cp -r "$backup_dir/local-search/index" .dev-aid/local-search/ 2>/dev/null || true
    fi

    if [ -f "$backup_dir/VERSION" ]; then
        cp "$backup_dir/VERSION" .dev-aid/VERSION
    fi

    return 0
}

# ============================================================================
# Dry-Run Support
# ============================================================================

# Execute command only if not in dry-run mode
exec_unless_dry_run() {
    if [[ "${DRY_RUN:-false}" == "true" ]]; then
        echo -e "${CYAN}[DRY-RUN] Would execute: $*${NC}"
        return 0
    else
        "$@"
    fi
}

# ============================================================================
# Display Functions
# ============================================================================

# Show update summary
show_update_summary() {
    local current_version="$1"
    local new_version="$2"
    local backup_dir="$3"

    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║         Update Complete! 🎉                ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Version: $current_version → $new_version${NC}"
    echo ""
    echo -e "${BLUE}What was updated:${NC}"
    echo "  ✓ Router code (.dev-aid/orchestration/)"
    echo "  ✓ Scripts (.dev-aid/scripts/)"
    echo "  ✓ Documentation (.dev-aid/docs/)"
    echo "  ✓ Provider configs (skills, commands)"
    echo "  ✓ Dependencies (requirements.txt)"
    echo ""
    echo -e "${BLUE}What was preserved:${NC}"
    echo "  ✓ Your API keys (.env)"
    echo "  ✓ Your memory bank (patterns, decisions)"
    echo "  ✓ Your logs (routing history, costs)"
    echo "  ✓ Your RAG indices"
    echo "  ✓ Your custom skills"
    echo ""
    echo -e "${BLUE}Backup location:${NC}"
    echo "  $backup_dir"
    echo "  (delete this after verifying everything works)"
    echo ""
}

# Show available commands after update
show_next_steps() {
    echo -e "${GREEN}Next steps:${NC}"
    echo ""
    echo "1. Test your setup:"
    echo "   ./.dev-aid/orchestration/router-cli.sh status"
    echo ""
    echo "2. View changelog:"
    echo "   cat .dev-aid/CHANGELOG.md"
    echo ""
    echo "3. If something broke, rollback:"
    echo "   ./.dev-aid/scripts/rollback.sh $1"
    echo ""
}

# ============================================================================
# Validation Functions
# ============================================================================

# Validate Dev-AID repository structure
validate_dev_aid_repo() {
    if [ ! -d ".dev-aid" ]; then
        echo -e "${RED}✗ Error: Not in a Dev-AID repository${NC}"
        echo "  Expected to find .dev-aid/ directory"
        return 1
    fi

    if [ ! -f ".dev-aid/VERSION" ]; then
        echo -e "${YELLOW}⚠️  Warning: VERSION file not found${NC}"
        echo "unknown" > .dev-aid/VERSION
    fi

    return 0
}

# ============================================================================
# Export functions for use in other scripts
# ============================================================================

export -f parse_version
export -f is_version_greater
export -f has_breaking_changes
export -f check_breaking_changes
export -f create_backup
export -f cleanup_old_backups
export -f verify_checksum
export -f is_user_modified
export -f get_protected_paths
export -f is_protected_path
export -f show_progress
export -f check_dependencies
export -f update_python_deps
export -f setup_error_trap
export -f handle_error
export -f restore_from_backup
export -f exec_unless_dry_run
export -f show_update_summary
export -f show_next_steps
export -f validate_dev_aid_repo
