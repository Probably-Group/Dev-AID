#!/usr/bin/env bash
# Provider Context File Smart Initialization Orchestrator
# Main entry point for context file migration and initialization (CLAUDE.md, GEMINI.md, OPENAI.md)

set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source all library files
source "$SCRIPT_DIR/claude-md-backup.sh"
source "$SCRIPT_DIR/claude-md-validator.sh"
source "$SCRIPT_DIR/claude-md-merger.sh"
source "$SCRIPT_DIR/progressive-disclosure.sh"
source "$SCRIPT_DIR/migration-report.sh"

# Configuration
PROGRESSIVE_DISCLOSURE_THRESHOLD=500

# Get context file name for provider
# Args: $1: provider (claude, gemini, openai)
get_context_filename() {
    local provider="$1"
    case "$provider" in
        claude) echo "CLAUDE.md" ;;
        gemini) echo "GEMINI.md" ;;
        openai) echo "OPENAI.md" ;;
        *) echo "${provider^^}.md" ;;
    esac
}

# Main initialization function
# Args: $1: project_root, $2: provider (claude, gemini, openai)
init_context_file() {
    local project_root="$1"
    local provider="${2:-claude}"
    local context_filename=$(get_context_filename "$provider")
    local context_file="$project_root/$context_filename"

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  $context_filename Initialization"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Check if context file already exists and is not a symlink
    if [ -f "$context_file" ] && [ ! -L "$context_file" ]; then
        echo "📋 Existing $context_filename detected"
        echo ""
        handle_existing_context_file "$project_root" "$provider"
    else
        echo "No existing $context_filename found"
        echo "Creating new $context_filename from Dev-AID template..."
        echo ""
        create_new_context_file "$project_root" "$provider"
    fi
}

# Handle existing context file
# Args: $1: project_root, $2: provider
handle_existing_context_file() {
    local project_root="$1"
    local provider="$2"
    local context_filename=$(get_context_filename "$provider")
    local context_file="$project_root/$context_filename"

    echo "🔍 Analyzing existing $context_filename..."
    echo ""

    # Step 1: Backup
    echo "1️⃣  Creating backup..."
    local backup_file=$(backup_context_file "$context_file" "$project_root" "$provider")
    echo "   ✓ Backed up to: $(basename "$backup_file")"
    echo ""

    # Step 2: Validate
    echo "2️⃣  Validating content..."
    local issue_count=$(run_all_validations "$context_file" "$project_root")
    local validation_json=$(get_validation_issues_json)
    echo "   $(get_validation_summary | head -1)"
    echo ""

    # Step 3: Merge
    echo "3️⃣  Merging with Dev-AID template..."
    local merged_content=$(create_merged_context "$context_file" "$project_root" "$provider" "$validation_json")
    local merged_lines=$(echo "$merged_content" | grep -c '^' || echo "0")
    echo "   ✓ Merged content: $merged_lines lines"
    echo ""

    # Step 4: Check if progressive disclosure needed
    local needs_split=$(needs_splitting "$merged_content")

    if [ "$needs_split" = "true" ]; then
        echo "4️⃣  Applying progressive disclosure (content exceeds $PROGRESSIVE_DISCLOSURE_THRESHOLD lines)..."

        local custom_content=$(extract_custom_content "$context_file")
        local provider_dir="$project_root/.dev-aid/providers/$provider"

        local split_stats=$(apply_progressive_disclosure "$merged_content" "$custom_content" "$provider_dir")
        echo ""
    else
        echo "4️⃣  Creating single $context_filename file..."
        local provider_dir="$project_root/.dev-aid/providers/$provider"
        mkdir -p "$provider_dir"
        echo "$merged_content" > "$provider_dir/$context_filename"
        echo "   ✓ Created: $provider_dir/$context_filename ($merged_lines lines)"
        echo ""

        split_stats=$(cat <<EOF
{
  "main_lines": $merged_lines,
  "extended_lines": 0,
  "has_extended": false,
  "has_custom": false,
  "split": false
}
EOF
)
    fi

    # Step 5: Create symlink
    echo "5️⃣  Creating symlink..."
    create_symlink "$project_root" "$provider"
    echo ""

    # Step 6: Generate and display report
    echo "6️⃣  Generating migration report..."
    echo ""

    local original_lines=$(wc -l < "$context_file" | tr -d ' ')
    local template_lines=350  # Approximate
    local custom_lines=$(extract_custom_content "$context_file" | grep -c '^' || echo "0")

    local stats_json=$(cat <<EOF
{
  "original_lines": $original_lines,
  "template_lines": $template_lines,
  "merged_lines": $merged_lines,
  "final_lines": $(echo "$split_stats" | grep -o '"main_lines": *[0-9]*' | grep -o '[0-9]*' || echo "$merged_lines"),
  "custom_lines": $custom_lines,
  "split": $(echo "$split_stats" | grep -o '"split": *[a-z]*' | grep -o '[a-z]*' || echo "false"),
  "has_extended": $(echo "$split_stats" | grep -o '"has_extended": *[a-z]*' | grep -o '[a-z]*' || echo "false"),
  "has_custom": $(echo "$split_stats" | grep -o '"has_custom": *[a-z]*' | grep -o '[a-z]*' || echo "false")
}
EOF
)

    generate_migration_report "$validation_json" "$stats_json" "$backup_file"

    # Save report to file
    local report_file="$project_root/.dev-aid/logs/${provider}-context-migration-$(date +%Y%m%d_%H%M%S).log"
    mkdir -p "$(dirname "$report_file")"
    generate_migration_report "$validation_json" "$stats_json" "$backup_file" | \
        sed 's/\x1b\[[0-9;]*m//g' > "$report_file"

    echo "Report saved to: $report_file"
    echo ""
}

# Create new context file from template
# Args: $1: project_root, $2: provider
create_new_context_file() {
    local project_root="$1"
    local provider="$2"
    local context_filename=$(get_context_filename "$provider")

    echo "1️⃣  Generating Dev-AID template..."
    local template=$(generate_devaid_template "$project_root" "$provider")
    echo "   ✓ Template generated"
    echo ""

    echo "2️⃣  Creating $context_filename..."
    local provider_dir="$project_root/.dev-aid/providers/$provider"
    mkdir -p "$provider_dir"
    echo "$template" > "$provider_dir/$context_filename"
    echo "   ✓ Created: $provider_dir/$context_filename"
    echo ""

    echo "3️⃣  Creating symlink..."
    create_symlink "$project_root" "$provider"
    echo ""

    echo "✅ $context_filename initialization complete!"
    echo ""
}

# Create symlink from project root to provider file
# Args: $1: project_root, $2: provider
create_symlink() {
    local project_root="$1"
    local provider="$2"
    local context_filename=$(get_context_filename "$provider")
    local target="$project_root/$context_filename"

    # Remove existing file/symlink
    rm -f "$target"

    # Create symlink (relative path)
    ln -s ".dev-aid/providers/$provider/$context_filename" "$target"

    echo "   ✓ Created symlink: $context_filename → .dev-aid/providers/$provider/$context_filename"
}

# Interactive mode (ask user before proceeding)
# Args: $1: project_root, $2: provider
init_context_file_interactive() {
    local project_root="$1"
    local provider="${2:-claude}"
    local context_filename=$(get_context_filename "$provider")
    local context_file="$project_root/$context_filename"

    if [ -f "$context_file" ] && [ ! -L "$context_file" ]; then
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "  Existing $context_filename detected"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "Dev-AID will:"
        echo "  1. Backup your existing $context_filename"
        echo "  2. Validate content for outdated/conflicting statements"
        echo "  3. Merge with Dev-AID template"
        echo "  4. Apply progressive disclosure if needed (>500 lines)"
        echo "  5. Show you a detailed migration report"
        echo ""

        read -p "Proceed with smart migration? [Y/n]: " confirm
        confirm=${confirm:-Y}

        if [[ ! "$confirm" =~ ^[Yy] ]]; then
            echo ""
            echo "Migration cancelled. Your $context_filename remains unchanged."
            echo "You can run this later with: dev-aid init-context-file"
            echo ""
            return 1
        fi

        echo ""
    fi

    init_context_file "$project_root" "$provider"
}

# Restore from backup
# Args: $1: project_root, $2: provider
restore_from_backup() {
    local project_root="$1"
    local provider="${2:-claude}"

    echo "Restoring from backup..."
    restore_context_backup "$project_root" "$provider"
}

# List available backups
# Args: $1: project_root, $2: provider
list_backups() {
    local project_root="$1"
    local provider="${2:-claude}"
    list_context_backups "$project_root" "$provider"
}

# Validate existing context file without migrating
# Args: $1: project_root, $2: provider
validate_only() {
    local project_root="$1"
    local provider="${2:-claude}"
    local context_filename=$(get_context_filename "$provider")
    local context_file="$project_root/$context_filename"

    if [ ! -f "$context_file" ]; then
        echo "Error: $context_filename not found"
        return 1
    fi

    echo "Validating $context_filename..."
    echo ""

    local issue_count=$(run_all_validations "$context_file" "$project_root")
    echo ""
    get_validation_summary
    echo ""

    if [ "$issue_count" -gt 0 ]; then
        echo "Run 'dev-aid init-context-file' to apply fixes and migrate"
    else
        echo "✅ No issues found!"
    fi
}

# Main CLI entry point
# Args: $@: command and arguments
main() {
    local command="${1:-init}"
    local project_root="${2:-.}"
    local provider="${3:-claude}"

    # Ensure absolute path
    project_root="$(cd "$project_root" && pwd)"

    case "$command" in
        init)
            init_context_file "$project_root" "$provider"
            ;;
        init-interactive)
            init_context_file_interactive "$project_root" "$provider"
            ;;
        restore)
            restore_from_backup "$project_root" "$provider"
            ;;
        list-backups)
            list_backups "$project_root" "$provider"
            ;;
        validate)
            validate_only "$project_root" "$provider"
            ;;
        *)
            echo "Usage: $0 {init|init-interactive|restore|list-backups|validate} [project_root] [provider]"
            echo "  provider: claude (default), gemini, openai"
            return 1
            ;;
    esac
}

# If script is run directly (not sourced), run main
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
