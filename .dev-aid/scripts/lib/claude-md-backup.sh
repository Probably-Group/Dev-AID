#!/usr/bin/env bash
# Provider Context File Backup Utilities
# Handles backing up existing context files (CLAUDE.md, GEMINI.md, OPENAI.md) with clear naming

set -euo pipefail

# Backup existing context file with timestamp
# Args:
#   $1: Source context file path
#   $2: Project root directory
#   $3: Provider name (claude, gemini, openai)
# Returns:
#   Path to backup file
backup_context_file() {
    local source_file="$1"
    local project_root="$2"
    local provider="${3:-claude}"

    # Validate provider
    case "$provider" in
        claude|gemini|openai|codex|cursor) ;;
        *) echo "Error: Invalid provider '$provider'" >&2; return 1 ;;
    esac
    local provider_upper="${provider^^}"
    local timestamp=$(date +%Y%m%d_%H%M%S)

    # Ensure backup directory exists
    local backup_dir="${project_root}/.dev-aid/backups"
    mkdir -p "$backup_dir"

    # Create backup with timestamp
    local backup_file="${backup_dir}/${provider_upper}_original-backup_${timestamp}.md"
    cp "$source_file" "$backup_file"

    # Update .latest tracker for this provider
    echo "$backup_file" > "${backup_dir}/.latest-${provider}"

    # Create/update symlink in project root for easy access (atomic operation)
    local symlink="${project_root}/${provider_upper}_original-backup.md"
    ln -sf ".dev-aid/backups/${provider_upper}_original-backup_${timestamp}.md" "$symlink"

    echo "$backup_file"
}

# Legacy wrapper for backward compatibility
backup_claude_md() {
    backup_context_file "$1" "$2" "claude"
}

# Restore from backup
# Args:
#   $1: Project root directory
#   $2: Provider name (claude, gemini, openai)
#   $3: Backup file path (optional, uses latest if not provided)
restore_context_backup() {
    local project_root="$1"
    local provider="${2:-claude}"

    # Validate provider
    case "$provider" in
        claude|gemini|openai|codex|cursor) ;;
        *) echo "Error: Invalid provider '$provider'" >&2; return 1 ;;
    esac
    local backup_file="${3:-}"
    local provider_upper="${provider^^}"

    # Use latest backup if not specified
    if [ -z "$backup_file" ]; then
        local latest_file="${project_root}/.dev-aid/backups/.latest-${provider}"
        if [ ! -f "$latest_file" ]; then
            echo "Error: No backup found for $provider" >&2
            return 1
        fi
        backup_file=$(cat "$latest_file")
    fi

    # Validate backup file is within expected directory
    local backup_dir="${project_root}/.dev-aid/backups"
    local resolved_backup
    resolved_backup=$(cd "$backup_dir" && realpath "$backup_file" 2>/dev/null || echo "")
    if [[ -z "$resolved_backup" || "$resolved_backup" != "$backup_dir"/* ]]; then
        echo "Error: Invalid backup path" >&2
        return 1
    fi


    if [ ! -f "$backup_file" ]; then
        echo "Error: Backup file not found: $backup_file" >&2
        return 1
    fi

    # Remove existing context file (might be symlink)
    local target="${project_root}/${provider_upper}.md"
    rm -f "$target"

    # Restore from backup
    cp "$backup_file" "$target"

    echo "✓ Restored ${provider_upper}.md from backup: $(basename "$backup_file")"
}

# Legacy wrapper for backward compatibility
restore_claude_md_backup() {
    restore_context_backup "$1" "claude" "${2:-}"
}

# List all backups
# Args:
#   $1: Project root directory
#   $2: Provider name (claude, gemini, openai)
list_context_backups() {
    local project_root="$1"
    local provider="${2:-claude}"

    # Validate provider
    case "$provider" in
        claude|gemini|openai|codex|cursor) ;;
        *) echo "Error: Invalid provider '$provider'" >&2; return 1 ;;
    esac
    local provider_upper="${provider^^}"
    local backup_dir="${project_root}/.dev-aid/backups"

    if [ ! -d "$backup_dir" ]; then
        echo "No backups found"
        return 0
    fi

    local backups=$(find "$backup_dir" -name "${provider_upper}_original-backup_*.md" -type f | sort -r)

    if [ -z "$backups" ]; then
        echo "No backups found for $provider"
        return 0
    fi

    echo "Available ${provider_upper}.md backups:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    local latest=$(cat "${backup_dir}/.latest-${provider}" 2>/dev/null || echo "")

    while IFS= read -r backup; do
        local basename=$(basename "$backup")
        local timestamp=$(echo "$basename" | sed "s/${provider_upper}_original-backup_\(.*\)\.md/\1/")
        local size=$(wc -l < "$backup" | tr -d ' ')
        local marker=""

        if [ "$backup" = "$latest" ]; then
            marker=" ← latest"
        fi

        printf "  %s (%s lines)%s\n" "$basename" "$size" "$marker"
    done <<< "$backups"
}

# Legacy wrapper for backward compatibility
list_claude_md_backups() {
    list_context_backups "$1" "claude"
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
        count=$((count + 1))
        if [ $count -gt $keep_count ]; then
            rm -f "$backup"
            echo "Removed old backup: $(basename "$backup")"
        fi
    done <<< "$backups"
}
