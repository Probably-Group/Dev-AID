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

# Source claude-md-init.sh for progressive disclosure detection functions
# (they work for any provider's rules directory pattern)
source "$SCRIPT_DIR/claude-md-init.sh" 2>/dev/null || true

# Detect existing progressive disclosure patterns (provider-agnostic)
# Checks for .<provider>/rules/ directory and @ file references
# Args: $1: project_root, $2: context_file_path, $3: provider
detect_provider_progressive_disclosure() {
    local project_root="$1"
    local context_file="$2"
    local provider="$3"

    local has_rules_dir="false"
    local rules_file_count=0
    local rules_total_lines=0
    local has_at_references="false"
    local at_reference_count=0

    # Check for .<provider>/rules/ directory (e.g., .claude/rules/, .gemini/rules/)
    local rules_dir="$project_root/.$provider/rules"
    if [ -d "$rules_dir" ]; then
        rules_file_count=$(find "$rules_dir" -maxdepth 1 -name "*.md" -type f 2>/dev/null | wc -l | tr -d ' ')
        if [ "$rules_file_count" -gt 0 ]; then
            has_rules_dir="true"
            rules_total_lines=$(find "$rules_dir" -maxdepth 1 -name "*.md" -type f -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}' || echo "0")
        fi
    fi

    # Check for @ file references in context file
    if [ -f "$context_file" ]; then
        local at_references=$(grep -oE '@[A-Za-z0-9_.~/-]+\.md|@\.[a-z]+/[A-Za-z0-9_/-]+' "$context_file" 2>/dev/null || true)
        at_reference_count=$(echo "$at_references" | grep -c '^@' || echo "0")
        if [ "$at_reference_count" -gt 0 ]; then
            has_at_references="true"
        fi
    fi

    local already_using_pd="false"
    if [ "$has_rules_dir" = "true" ] || [ "$has_at_references" = "true" ]; then
        already_using_pd="true"
    fi

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

# Display provider progressive disclosure detection results
# Args: $1: detection_json, $2: provider
display_provider_pd_detection() {
    local detection_json="$1"
    local provider="$2"

    local already_using=$(echo "$detection_json" | grep -o '"already_using_progressive_disclosure": *[a-z]*' | grep -o 'true\|false')
    local has_rules=$(echo "$detection_json" | grep -o '"has_rules_dir": *[a-z]*' | grep -o 'true\|false')
    local rules_count=$(echo "$detection_json" | grep -o '"rules_file_count": *[0-9]*' | grep -o '[0-9]*')
    local rules_lines=$(echo "$detection_json" | grep -o '"rules_total_lines": *[0-9]*' | grep -o '[0-9]*')
    local has_refs=$(echo "$detection_json" | grep -o '"has_at_references": *[a-z]*' | grep -o 'true\|false')
    local refs_count=$(echo "$detection_json" | grep -o '"at_reference_count": *[0-9]*' | grep -o '[0-9]*')

    if [ "$already_using" = "true" ]; then
        echo "   ✓ Existing progressive disclosure detected:"
        if [ "$has_rules" = "true" ]; then
            echo "     • .$provider/rules/: $rules_count files ($rules_lines lines total)"
        fi
        if [ "$has_refs" = "true" ]; then
            echo "     • @ file references: $refs_count found"
        fi
        echo "     → Skipping redundant splitting (your structure is preserved)"
    else
        echo "   • No existing progressive disclosure detected"
    fi
}

# Get context file name for provider
# Args: $1: provider (claude, gemini, openai, codex)
get_context_filename() {
    local provider="$1"
    case "$provider" in
        claude) echo "CLAUDE.md" ;;
        gemini) echo "GEMINI.md" ;;
        openai) echo "OPENAI.md" ;;
        codex) echo "AGENTS.md" ;;
        *) echo "${provider^^}.md" ;;
    esac
}

# Main initialization function
# Args: $1: project_root, $2: provider (claude, gemini, openai)
init_context_file() {
    local project_root="$1"
    local provider="${2:-claude}"

    # Validate provider
    case "$provider" in
        claude|gemini|openai|codex|cursor) ;;
        *) echo "Error: Invalid provider '$provider'" >&2; return 1 ;;
    esac
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

    # Step 2: Detect existing progressive disclosure
    echo "2️⃣  Checking for existing progressive disclosure..."
    local pd_detection=$(detect_provider_progressive_disclosure "$project_root" "$context_file" "$provider")
    local already_using_pd=$(echo "$pd_detection" | grep -o '"already_using_progressive_disclosure": *[a-z]*' | grep -o 'true\|false')
    display_provider_pd_detection "$pd_detection" "$provider"
    echo ""

    # Step 3: Assess quality
    echo "3️⃣  Assessing content quality..."
    local quality_json=$(get_quality_assessment "$context_file")
    display_quality_assessment "$quality_json"
    echo ""

    # Step 4: Validate content
    echo "4️⃣  Validating content..."
    local issue_count=$(run_all_validations "$context_file" "$project_root")
    local validation_json=$(get_validation_issues_json)
    echo "   $(get_validation_summary | head -1)"
    echo ""

    # Step 5: Merge
    echo "5️⃣  Merging with Dev-AID template..."
    local merged_content=$(create_merged_context "$context_file" "$project_root" "$provider" "$validation_json")
    local merged_lines=$(echo "$merged_content" | grep -c '^' || echo "0")
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
        echo "$merged_content" > "$provider_dir/$context_filename"
        echo "   ✓ Created: $provider_dir/$context_filename ($merged_lines lines)"
        echo "   ✓ Your .$provider/rules/ and @ references remain untouched"
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

            local custom_content=$(extract_custom_content "$context_file")
            local provider_dir="$project_root/.dev-aid/providers/$provider"

            split_stats=$(apply_progressive_disclosure "$merged_content" "$custom_content" "$provider_dir")
            echo ""
        else
            echo "6️⃣  Creating single $context_filename file..."
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
    fi

    # Step 7: Create symlink
    echo "7️⃣  Creating symlink..."
    create_symlink "$project_root" "$provider"
    echo ""

    # Step 8: Generate and display report
    echo "8️⃣  Generating migration report..."
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

# Inject preset-specific content into a context file
# Adds Context Groups, Plan Execution Protocol, and Proactive Context Loading
# Args: $1: context_file_path
inject_preset_content() {
    local context_file="$1"

    [[ -f "$context_file" ]] || return 0

    # Only inject if preset variables are available
    if [[ -z "${CONTEXT_GROUPS:-}" ]] && [[ -z "${CONTEXT_LOADING_TABLE:-}" ]]; then
        return 0
    fi

    local inject_block=""

    # Context Groups section
    if [[ -n "${CONTEXT_GROUPS:-}" ]]; then
        inject_block+="
## Context Groups

Load a named group to get all relevant files at once:

${CONTEXT_GROUPS}
"
    fi

    # Proactive Context Loading table
    if [[ -n "${CONTEXT_LOADING_TABLE:-}" ]]; then
        inject_block+="
## Proactive Context Loading

| Task | Read First |
|------|-----------|
${CONTEXT_LOADING_TABLE}
"
    fi

    # Plan Execution Protocol
    inject_block+="
## Plan Execution Protocol

When working on multi-step tasks:

1. **Before starting**: Create a plan with \`/aid-plan <task>\`
2. **After each step**: Update the Progress Log
3. **If interrupted**: The plan file records where you stopped
4. **On resume**: Read the plan file to pick up where you left off

Always end sessions with: **Stopped at:** Step N -- {what's next}
"

    # Append to the end of the context file (before any final blank lines)
    printf '%s\n' "$inject_block" >> "$context_file"
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

    # Inject preset content if available
    if [[ -n "${CONTEXT_GROUPS:-}" ]] || [[ -n "${CONTEXT_LOADING_TABLE:-}" ]]; then
        echo "2b. Injecting preset content..."
        inject_preset_content "$provider_dir/$context_filename"
        echo "   ✓ Preset content injected"
        echo ""
    fi

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
    # Create symlink (atomic, replaces existing)
    ln -sf ".dev-aid/providers/$provider/$context_filename" "$target"
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
        echo "  2. Detect existing progressive disclosure (.$provider/rules/, @ references)"
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

    # Refuse to operate on system directories
    if [[ "$project_root" == "/" || "$project_root" == "/etc"* || "$project_root" == "/usr"* || "$project_root" == "/bin"* || "$project_root" == "/sbin"* ]]; then
        echo "Error: Refusing to operate on system directory: $project_root" >&2
        exit 1
    fi

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
