#!/usr/bin/env bash
# CLAUDE.md Smart Initialization Orchestrator
# Main entry point for CLAUDE.md migration and initialization

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

# Main initialization function
# Args: $1: project_root, $2: provider (default: claude)
init_claude_md() {
    local project_root="$1"
    local provider="${2:-claude}"
    local claude_md="$project_root/CLAUDE.md"

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  CLAUDE.md Initialization"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    # Check if CLAUDE.md already exists and is not a symlink
    if [ -f "$claude_md" ] && [ ! -L "$claude_md" ]; then
        echo "📋 Existing CLAUDE.md detected"
        echo ""
        handle_existing_claude_md "$project_root" "$provider"
    else
        echo "No existing CLAUDE.md found"
        echo "Creating new CLAUDE.md from Dev-AID template..."
        echo ""
        create_new_claude_md "$project_root" "$provider"
    fi
}

# Handle existing CLAUDE.md file
# Args: $1: project_root, $2: provider
handle_existing_claude_md() {
    local project_root="$1"
    local provider="$2"
    local claude_md="$project_root/CLAUDE.md"

    echo "🔍 Analyzing existing CLAUDE.md..."
    echo ""

    # Step 1: Backup
    echo "1️⃣  Creating backup..."
    local backup_file=$(backup_claude_md "$claude_md" "$project_root")
    echo "   ✓ Backed up to: $(basename "$backup_file")"
    echo ""

    # Step 2: Validate
    echo "2️⃣  Validating content..."
    local issue_count=$(run_all_validations "$claude_md" "$project_root")
    local validation_json=$(get_validation_issues_json)
    echo "   $(get_validation_summary | head -1)"
    echo ""

    # Step 3: Merge
    echo "3️⃣  Merging with Dev-AID template..."
    local merged_content=$(create_merged_claude_md "$claude_md" "$project_root" "$validation_json")
    local merged_lines=$(echo "$merged_content" | grep -c '^' || echo "0")
    echo "   ✓ Merged content: $merged_lines lines"
    echo ""

    # Step 4: Check if progressive disclosure needed
    local needs_split=$(needs_splitting "$merged_content")

    if [ "$needs_split" = "true" ]; then
        echo "4️⃣  Applying progressive disclosure (content exceeds $PROGRESSIVE_DISCLOSURE_THRESHOLD lines)..."

        local custom_content=$(extract_custom_content "$claude_md")
        local provider_dir="$project_root/.dev-aid/providers/$provider"

        local split_stats=$(apply_progressive_disclosure "$merged_content" "$custom_content" "$provider_dir")
        echo ""
    else
        echo "4️⃣  Creating single CLAUDE.md file..."
        local provider_dir="$project_root/.dev-aid/providers/$provider"
        mkdir -p "$provider_dir"
        echo "$merged_content" > "$provider_dir/CLAUDE.md"
        echo "   ✓ Created: $provider_dir/CLAUDE.md ($merged_lines lines)"
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

    local original_lines=$(wc -l < "$claude_md" | tr -d ' ')
    local template_lines=350  # Approximate
    local custom_lines=$(extract_custom_content "$claude_md" | grep -c '^' || echo "0")

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
    local report_file="$project_root/.dev-aid/logs/claude-md-migration-$(date +%Y%m%d_%H%M%S).log"
    mkdir -p "$(dirname "$report_file")"
    generate_migration_report "$validation_json" "$stats_json" "$backup_file" | \
        sed 's/\x1b\[[0-9;]*m//g' > "$report_file"

    echo "Report saved to: $report_file"
    echo ""
}

# Create new CLAUDE.md from template
# Args: $1: project_root, $2: provider
create_new_claude_md() {
    local project_root="$1"
    local provider="$2"

    echo "1️⃣  Generating Dev-AID template..."
    local template=$(generate_devaid_template "$project_root")
    echo "   ✓ Template generated"
    echo ""

    echo "2️⃣  Creating CLAUDE.md..."
    local provider_dir="$project_root/.dev-aid/providers/$provider"
    mkdir -p "$provider_dir"
    echo "$template" > "$provider_dir/CLAUDE.md"
    echo "   ✓ Created: $provider_dir/CLAUDE.md"
    echo ""

    echo "3️⃣  Creating symlink..."
    create_symlink "$project_root" "$provider"
    echo ""

    echo "✅ CLAUDE.md initialization complete!"
    echo ""
}

# Create symlink from project root to provider file
# Args: $1: project_root, $2: provider
create_symlink() {
    local project_root="$1"
    local provider="$2"
    local target="$project_root/CLAUDE.md"

    # Remove existing file/symlink
    rm -f "$target"

    # Create symlink (relative path)
    ln -s ".dev-aid/providers/$provider/CLAUDE.md" "$target"

    echo "   ✓ Created symlink: CLAUDE.md → .dev-aid/providers/$provider/CLAUDE.md"
}

# Interactive mode (ask user before proceeding)
# Args: $1: project_root, $2: provider
init_claude_md_interactive() {
    local project_root="$1"
    local provider="${2:-claude}"
    local claude_md="$project_root/CLAUDE.md"

    if [ -f "$claude_md" ] && [ ! -L "$claude_md" ]; then
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "  Existing CLAUDE.md detected"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "Dev-AID will:"
        echo "  1. Backup your existing CLAUDE.md"
        echo "  2. Validate content for outdated/conflicting statements"
        echo "  3. Merge with Dev-AID template"
        echo "  4. Apply progressive disclosure if needed (>500 lines)"
        echo "  5. Show you a detailed migration report"
        echo ""

        read -p "Proceed with smart migration? [Y/n]: " confirm
        confirm=${confirm:-Y}

        if [[ ! "$confirm" =~ ^[Yy] ]]; then
            echo ""
            echo "Migration cancelled. Your CLAUDE.md remains unchanged."
            echo "You can run this later with: dev-aid init-claude-md"
            echo ""
            return 1
        fi

        echo ""
    fi

    init_claude_md "$project_root" "$provider"
}

# Restore from backup
# Args: $1: project_root
restore_from_backup() {
    local project_root="$1"

    echo "Restoring CLAUDE.md from backup..."
    restore_claude_md_backup "$project_root"
}

# List available backups
# Args: $1: project_root
list_backups() {
    local project_root="$1"
    list_claude_md_backups "$project_root"
}

# Validate existing CLAUDE.md without migrating
# Args: $1: project_root
validate_only() {
    local project_root="$1"
    local claude_md="$project_root/CLAUDE.md"

    if [ ! -f "$claude_md" ]; then
        echo "Error: CLAUDE.md not found"
        return 1
    fi

    echo "Validating CLAUDE.md..."
    echo ""

    local issue_count=$(run_all_validations "$claude_md" "$project_root")
    echo ""
    get_validation_summary
    echo ""

    if [ "$issue_count" -gt 0 ]; then
        echo "Run 'dev-aid init-claude-md' to apply fixes and migrate"
    else
        echo "✅ No issues found!"
    fi
}

# Main CLI entry point
# Args: $@: command and arguments
main() {
    local command="${1:-init}"
    local project_root="${2:-.}"

    # Ensure absolute path
    project_root="$(cd "$project_root" && pwd)"

    case "$command" in
        init)
            init_claude_md "$project_root" "claude"
            ;;
        init-interactive)
            init_claude_md_interactive "$project_root" "claude"
            ;;
        restore)
            restore_from_backup "$project_root"
            ;;
        list-backups)
            list_backups "$project_root"
            ;;
        validate)
            validate_only "$project_root"
            ;;
        *)
            echo "Usage: $0 {init|init-interactive|restore|list-backups|validate} [project_root]"
            return 1
            ;;
    esac
}

# If script is run directly (not sourced), run main
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
