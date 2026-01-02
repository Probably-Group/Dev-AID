#!/usr/bin/env bash
# CLAUDE.md Backup Utilities
# Handles backing up existing CLAUDE.md files with clear naming

set -euo pipefail

# Backup existing CLAUDE.md with timestamp
# Args:
#   $1: Source CLAUDE.md file path
#   $2: Project root directory
# Returns:
#   Path to backup file
backup_claude_md() {
    local source_file="$1"
    local project_root="$2"
    local timestamp=$(date +%Y%m%d_%H%M%S)

    # Ensure backup directory exists
    local backup_dir="${project_root}/.dev-aid/backups"
    mkdir -p "$backup_dir"

    # Create backup with timestamp
    local backup_file="${backup_dir}/CLAUDE_original-backup_${timestamp}.md"
    cp "$source_file" "$backup_file"

    # Update .latest tracker
    echo "$backup_file" > "${backup_dir}/.latest"

    # Create/update symlink in project root for easy access
    local symlink="${project_root}/CLAUDE_original-backup.md"
    rm -f "$symlink"
    ln -s ".dev-aid/backups/CLAUDE_original-backup_${timestamp}.md" "$symlink"

    echo "$backup_file"
}

# Restore from backup
# Args:
#   $1: Project root directory
#   $2: Backup file path (optional, uses latest if not provided)
restore_claude_md_backup() {
    local project_root="$1"
    local backup_file="${2:-}"

    # Use latest backup if not specified
    if [ -z "$backup_file" ]; then
        local latest_file="${project_root}/.dev-aid/backups/.latest"
        if [ ! -f "$latest_file" ]; then
            echo "Error: No backup found to restore" >&2
            return 1
        fi
        backup_file=$(cat "$latest_file")
    fi

    if [ ! -f "$backup_file" ]; then
        echo "Error: Backup file not found: $backup_file" >&2
        return 1
    fi

    # Remove existing CLAUDE.md (might be symlink)
    local target="${project_root}/CLAUDE.md"
    rm -f "$target"

    # Restore from backup
    cp "$backup_file" "$target"

    echo "✓ Restored CLAUDE.md from backup: $(basename "$backup_file")"
}

# List all backups
# Args:
#   $1: Project root directory
list_claude_md_backups() {
    local project_root="$1"
    local backup_dir="${project_root}/.dev-aid/backups"

    if [ ! -d "$backup_dir" ]; then
        echo "No backups found"
        return 0
    fi

    local backups=$(find "$backup_dir" -name "CLAUDE_original-backup_*.md" -type f | sort -r)

    if [ -z "$backups" ]; then
        echo "No backups found"
        return 0
    fi

    echo "Available CLAUDE.md backups:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    local latest=$(cat "${backup_dir}/.latest" 2>/dev/null || echo "")

    while IFS= read -r backup; do
        local basename=$(basename "$backup")
        local timestamp=$(echo "$basename" | sed 's/CLAUDE_original-backup_\(.*\)\.md/\1/')
        local size=$(wc -l < "$backup" | tr -d ' ')
        local marker=""

        if [ "$backup" = "$latest" ]; then
            marker=" ← latest"
        fi

        printf "  %s (%s lines)%s\n" "$basename" "$size" "$marker"
    done <<< "$backups"
}

# Get latest backup path
# Args:
#   $1: Project root directory
get_latest_backup() {
    local project_root="$1"
    local latest_file="${project_root}/.dev-aid/backups/.latest"

    if [ -f "$latest_file" ]; then
        cat "$latest_file"
    else
        echo ""
    fi
}

# Check if backup exists
# Args:
#   $1: Project root directory
has_backup() {
    local project_root="$1"
    local latest=$(get_latest_backup "$project_root")

    if [ -n "$latest" ] && [ -f "$latest" ]; then
        return 0
    else
        return 1
    fi
}

# Cleanup old backups (keep last N)
# Args:
#   $1: Project root directory
#   $2: Number of backups to keep (default: 5)
cleanup_old_backups() {
    local project_root="$1"
    local keep_count="${2:-5}"
    local backup_dir="${project_root}/.dev-aid/backups"

    if [ ! -d "$backup_dir" ]; then
        return 0
    fi

    local backups=$(find "$backup_dir" -name "CLAUDE_original-backup_*.md" -type f | sort -r)
    local count=0

    while IFS= read -r backup; do
        ((count++))
        if [ $count -gt $keep_count ]; then
            rm -f "$backup"
            echo "Removed old backup: $(basename "$backup")"
        fi
    done <<< "$backups"
}
