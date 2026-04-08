#!/usr/bin/env bash
# CLAUDE.md Smart Initialization Orchestrator
# Main entry point for CLAUDE.md migration and initialization

set -euo pipefail

# IMPORTANT: Use a unique local-ish variable so we don't clobber the parent
# script's SCRIPT_DIR. setup-dev-aid.sh sets SCRIPT_DIR to .dev-aid/scripts/
# and then later expects $SCRIPT_DIR/setup-git-hooks.sh — if we leak our
# .dev-aid/scripts/lib/ value into SCRIPT_DIR, that lookup fails with
# "setup-git-hooks.sh not found". Same root cause as the preset path bug
# fixed in commit 4a6a411.
_cmi_lib_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source all library files
source "$_cmi_lib_dir/claude-md-backup.sh"
source "$_cmi_lib_dir/claude-md-validator.sh"
source "$_cmi_lib_dir/claude-md-merger.sh"
source "$_cmi_lib_dir/progressive-disclosure.sh"
source "$_cmi_lib_dir/migration-report.sh"
unset _cmi_lib_dir

# Configuration
PROGRESSIVE_DISCLOSURE_THRESHOLD=500

# Detect existing progressive disclosure patterns
# Checks for .claude/rules/ directory and @ file references in CLAUDE.md
# Args: $1: project_root, $2: claude_md_path
# Returns: JSON with detection results
detect_existing_progressive_disclosure() {
    local project_root="$1"
    local claude_md="$2"

    local has_rules_dir="false"
    local rules_file_count=0
    local rules_total_lines=0
    local has_at_references="false"
    local at_reference_count=0
    local at_references=""

    # Check for .claude/rules/ directory
    local rules_dir="$project_root/.claude/rules"
    if [ -d "$rules_dir" ]; then
        # Count markdown files in rules directory
        rules_file_count=$(find "$rules_dir" -maxdepth 1 -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')
        if [ "$rules_file_count" -gt 0 ]; then
            has_rules_dir="true"
            # Calculate total lines across all rule files
            rules_total_lines=$(find "$rules_dir" -maxdepth 1 -name "*.md" -type f -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}' || echo "0")
        fi
    fi

    # Check for @ file references in CLAUDE.md
    if [ -f "$claude_md" ]; then
        # Match patterns like @path/to/file.md, @.claude/rules/*, @~/path, etc.
        # Claude Code supports: @file.md, @./relative/path.md, @~/home/path.md
        at_references=$(grep -oE '@[A-Za-z0-9_.~/-]+\.md|@\.claude/[A-Za-z0-9_/-]+' "$claude_md" 2>/dev/null || true)
        at_reference_count=$(echo "$at_references" | grep -c '^@' || true)
        if [ "$at_reference_count" -gt 0 ]; then
            has_at_references="true"
        fi
    fi

    # Determine if progressive disclosure is already in use
    local already_using_pd="false"
    if [ "$has_rules_dir" = "true" ] || [ "$has_at_references" = "true" ]; then
        already_using_pd="true"
    fi

    # Return JSON result
    cat <<EOF
{
  "already_using_progressive_disclosure": $already_using_pd,
  "has_rules_dir": $has_rules_dir,
  "rules_dir": "$rules_dir",
  "rules_file_count": $rules_file_count,
  "rules_total_lines": $rules_total_lines,
  "has_at_references": $has_at_references,
  "at_reference_count": $at_reference_count
}
EOF
}

# Display progressive disclosure detection results
# Args: $1: detection_json
display_pd_detection() {
    local detection_json="$1"

    local already_using=$(echo "$detection_json" | grep -o '"already_using_progressive_disclosure": *[a-z]*' | grep -o 'true\|false')
    local has_rules=$(echo "$detection_json" | grep -o '"has_rules_dir": *[a-z]*' | grep -o 'true\|false')
    local rules_count=$(echo "$detection_json" | grep -o '"rules_file_count": *[0-9]*' | grep -o '[0-9]*')
    local rules_lines=$(echo "$detection_json" | grep -o '"rules_total_lines": *[0-9]*' | grep -o '[0-9]*')
    local has_refs=$(echo "$detection_json" | grep -o '"has_at_references": *[a-z]*' | grep -o 'true\|false')
    local refs_count=$(echo "$detection_json" | grep -o '"at_reference_count": *[0-9]*' | grep -o '[0-9]*')

    if [ "$already_using" = "true" ]; then
        echo "   ✓ Existing progressive disclosure detected:"
        if [ "$has_rules" = "true" ]; then
            echo "     • .claude/rules/: $rules_count files ($rules_lines lines total)"
        fi
        if [ "$has_refs" = "true" ]; then
            echo "     • @ file references: $refs_count found in CLAUDE.md"
        fi
        echo "     → Skipping redundant splitting (your structure is preserved)"
    else
        echo "   • No existing progressive disclosure detected"
    fi
}

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

    # Step 2: Detect existing progressive disclosure
    echo "2️⃣  Checking for existing progressive disclosure..."
    local pd_detection=$(detect_existing_progressive_disclosure "$project_root" "$claude_md")
    local already_using_pd=$(echo "$pd_detection" | grep -o '"already_using_progressive_disclosure": *[a-z]*' | grep -o 'true\|false')
    display_pd_detection "$pd_detection"
    echo ""

    # Step 3: Assess quality
    echo "3️⃣  Assessing content quality..."
    local quality_json=$(get_quality_assessment "$claude_md")
    display_quality_assessment "$quality_json"
    echo ""

    # Step 4: Validate content
    echo "4️⃣  Validating content..."
    local issue_count=$(run_all_validations "$claude_md" "$project_root")
    local validation_json=$(get_validation_issues_json)
    echo "   $(get_validation_summary | head -1)"
    echo ""

    # Step 5: Merge
    echo "5️⃣  Merging with Dev-AID template..."
    local merged_content=$(create_merged_claude_md "$claude_md" "$project_root" "$validation_json")
    local merged_lines=$(echo "$merged_content" | grep -c '^' || true)
    echo "   ✓ Merged content: $merged_lines lines"
    echo ""

    # Step 6: Check if progressive disclosure needed (skip if already using)
    local needs_split="false"
    local split_stats=""

    if [ "$already_using_pd" = "true" ]; then
        # User already has progressive disclosure - don't apply redundant splitting
        echo "6️⃣  Preserving existing structure (progressive disclosure already in use)..."
        local provider_dir="$project_root/.dev-aid/providers/$provider"
        mkdir -p "$provider_dir"
        echo "$merged_content" > "$provider_dir/CLAUDE.md"
        echo "   ✓ Created: $provider_dir/CLAUDE.md ($merged_lines lines)"
        echo "   ✓ Your .claude/rules/ and @ references remain untouched"
        echo ""

        split_stats=$(cat <<EOF
{
  "main_lines": $merged_lines,
  "extended_lines": 0,
  "has_extended": false,
  "has_custom": false,
  "split": false,
  "skipped_reason": "existing_progressive_disclosure"
}
EOF
)
    else
        # Check if content needs splitting
        needs_split=$(needs_splitting "$merged_content")

        if [ "$needs_split" = "true" ]; then
            echo "6️⃣  Applying progressive disclosure (content exceeds $PROGRESSIVE_DISCLOSURE_THRESHOLD lines)..."

            local custom_content=$(extract_custom_content "$claude_md")
            local provider_dir="$project_root/.dev-aid/providers/$provider"

            split_stats=$(apply_progressive_disclosure "$merged_content" "$custom_content" "$provider_dir")
            echo ""
        else
            echo "6️⃣  Creating single CLAUDE.md file..."
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
    fi

    # Step 7: Create symlink
    echo "7️⃣  Creating symlink..."
    create_symlink "$project_root" "$provider"
    echo ""

    # Step 8: Generate and display report
    echo "8️⃣  Generating migration report..."
    echo ""

    local original_lines=$(wc -l < "$claude_md" | tr -d ' ')
    local template_lines=350  # Approximate
    local custom_lines=$(extract_custom_content "$claude_md" | grep -c '^' || true)

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

    # Create symlink (atomic, replaces existing)
    ln -sf ".dev-aid/providers/$provider/CLAUDE.md" "$target"

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
        echo "  2. Detect existing progressive disclosure (.claude/rules/, @ references)"
        echo "  3. Assess content quality (completeness, placeholders, structure)"
        echo "  4. Validate content for outdated/conflicting statements"
        echo "  5. Merge with Dev-AID template (enhancing low-quality content)"
        echo "  6. Apply progressive disclosure if needed (>500 lines) - skipped if already in use"
        echo "  7. Show you a detailed migration report"
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

    # Refuse to operate on system directories
    if [[ "$project_root" == "/" || "$project_root" == "/etc"* || "$project_root" == "/usr"* || "$project_root" == "/bin"* || "$project_root" == "/sbin"* ]]; then
        echo "Error: Refusing to operate on system directory: $project_root" >&2
        exit 1
    fi

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
