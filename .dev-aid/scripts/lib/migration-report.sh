#!/usr/bin/env bash
# Migration Report Generator
# Creates user-friendly reports for CLAUDE.md migration

set -euo pipefail

# Colors for terminal output
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    BOLD='\033[1m'
    RESET='\033[0m'
else
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    BOLD=''
    RESET=''
fi

# Generate migration report
# Args: $1: validation_issues_json, $2: stats_json, $3: backup_path
generate_migration_report() {
    local issues_json="$1"
    local stats_json="$2"
    local backup_path="$3"

    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    # Parse stats
    local original_lines=$(echo "$stats_json" | grep -o '"original_lines": *[0-9]*' | grep -o '[0-9]*' || echo "0")
    local template_lines=$(echo "$stats_json" | grep -o '"template_lines": *[0-9]*' | grep -o '[0-9]*' || echo "0")
    local merged_lines=$(echo "$stats_json" | grep -o '"merged_lines": *[0-9]*' | grep -o '[0-9]*' || echo "0")
    local final_lines=$(echo "$stats_json" | grep -o '"final_lines": *[0-9]*' | grep -o '[0-9]*' || echo "0")
    local custom_lines=$(echo "$stats_json" | grep -o '"custom_lines": *[0-9]*' | grep -o '[0-9]*' || echo "0")

    # Count issues by severity
    local total_issues=0
    local high_issues=0
    local medium_issues=0
    local low_issues=0
    local auto_fixed=0
    local flagged=0

    if [ "$issues_json" != "[]" ] && [ -n "$issues_json" ]; then
        total_issues=$(echo "$issues_json" | grep -o '"type":' | wc -l || echo "0")
        high_issues=$(echo "$issues_json" | grep -c '"severity": "high"' || echo "0")
        medium_issues=$(echo "$issues_json" | grep -c '"severity": "medium"' || echo "0")
        low_issues=$(echo "$issues_json" | grep -c '"severity": "low"' || echo "0")
        auto_fixed=$(echo "$issues_json" | grep -c '"auto_fix": true' || echo "0")
        flagged=$(echo "$issues_json" | grep -c '"auto_fix": false' || echo "0")
    fi

    # Generate report
    cat <<EOF

╔════════════════════════════════════════════════════════════════╗
║                 CLAUDE.md Migration Report                     ║
╚════════════════════════════════════════════════════════════════╝

Generated: $timestamp

EOF

    # Section 1: Preserved Content
    if [ "$custom_lines" -gt 0 ]; then
        echo -e "${GREEN}✅ Successfully Preserved${RESET}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "  ✓ Custom content preserved: $custom_lines lines"
        echo "  ✓ Original file backed up: $(basename "$backup_path")"
        echo ""
    fi

    # Section 2: Issues Detected
    if [ "$total_issues" -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Issues Detected & Resolutions${RESET}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""

        # Parse and display issues
        local issue_num=1
        if [ "$issues_json" != "[]" ]; then
            # Extract each issue (simplified - would use jq in production)
            echo "$issues_json" | grep -o '{[^}]*}' | while read -r issue; do
                local type=$(echo "$issue" | grep -o '"type": *"[^"]*"' | cut -d'"' -f4)
                local line=$(echo "$issue" | grep -o '"line": *[0-9]*' | grep -o '[0-9]*')
                local desc=$(echo "$issue" | grep -o '"description": *"[^"]*"' | cut -d'"' -f4)
                local severity=$(echo "$issue" | grep -o '"severity": *"[^"]*"' | cut -d'"' -f4)
                local auto_fix=$(echo "$issue" | grep -o '"auto_fix": *[a-z]*' | grep -o '[a-z]*')

                local action_text="FLAGGED - Please review"
                if [ "$auto_fix" = "true" ]; then
                    action_text="AUTO-FIXED ✓"
                fi

                echo "### $issue_num. $type"
                echo "**Issue**: $desc"
                echo "**Location**: Original line $line"
                echo "**Severity**: $severity"
                echo "**Action**: $action_text"
                echo ""

                ((issue_num++))
            done
        fi
    fi

    # Section 3: Statistics
    echo -e "${BLUE}📊 Migration Statistics${RESET}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Original file: $original_lines lines"
    echo "  Dev-AID template: $template_lines lines"
    echo "  Merged total: $merged_lines lines"
    echo "  Final size: $final_lines lines"
    echo ""

    if [ "$total_issues" -gt 0 ]; then
        echo "  Issues found: $total_issues"
        echo "    • High priority: $high_issues"
        echo "    • Medium priority: $medium_issues"
        echo "    • Low priority: $low_issues"
        echo ""
        echo "  Auto-fixed: $auto_fixed"
        echo "  Flagged for review: $flagged"
        echo ""
    fi

    # Section 4: Progressive Disclosure (if applied)
    if [ "$final_lines" -lt "$merged_lines" ] || echo "$stats_json" | grep -q '"split": true'; then
        echo -e "${BLUE}🔀 Progressive Disclosure Applied${RESET}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "**Reason**: Content exceeds 500 lines ($merged_lines lines total)"
        echo ""
        echo "**File structure created**:"
        echo "  • CLAUDE.md (Main - ≤450 lines)"
        echo "    ├── Core role and context"
        echo "    ├── Essential tech stack summary"
        echo "    ├── Top critical guidelines"
        echo "    └── Quick reference links"
        echo ""

        if echo "$stats_json" | grep -q '"has_extended": true'; then
            local ext_lines=$(echo "$stats_json" | grep -o '"extended_lines": *[0-9]*' | grep -o '[0-9]*' || echo "0")
            echo "  • CLAUDE_extended.md ($ext_lines lines)"
            echo "    ├── Complete tech stack details"
            echo "    ├── All Dev-AID best practices"
            echo "    └── Advanced patterns"
            echo ""
        fi

        if echo "$stats_json" | grep -q '"has_custom": true'; then
            echo "  • CLAUDE_custom.md ($custom_lines lines)"
            echo "    ├── All your original custom instructions"
            echo "    ├── Project-specific guidelines"
            echo "    └── Team conventions"
            echo ""
        fi
    fi

    # Section 5: Action Required
    if [ "$flagged" -gt 0 ]; then
        echo -e "${RED}🔍 Action Required${RESET}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo "**Items Needing Your Review**:"

        local review_num=1
        echo "$issues_json" | grep -o '{[^}]*}' | while read -r issue; do
            local auto_fix=$(echo "$issue" | grep -o '"auto_fix": *[a-z]*' | grep -o '[a-z]*')
            if [ "$auto_fix" = "false" ]; then
                local desc=$(echo "$issue" | grep -o '"description": *"[^"]*"' | cut -d'"' -f4)
                local line=$(echo "$issue" | grep -o '"line": *[0-9]*' | grep -o '[0-9]*')
                echo "  $review_num. Line $line: $desc"
                ((review_num++))
            fi
        done

        echo ""
    else
        echo -e "${GREEN}✅ No Action Required${RESET}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "  All issues were automatically resolved."
        echo ""
    fi

    # Section 6: Backup Information
    echo -e "${BLUE}📁 Backup Information${RESET}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Original file backed up to:"
    echo "    → $backup_path"
    echo "    → Symlink: CLAUDE_original-backup.md (for easy access)"
    echo ""

    # Section 7: Next Steps
    echo -e "${BOLD}✨ Next Steps${RESET}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if [ "$flagged" -gt 0 ]; then
        echo "  1. Review flagged items in CLAUDE_custom.md"
        echo "  2. Update any outdated references"
        echo "  3. Test the new CLAUDE.md with your AI assistant"
        echo "  4. Customize CLAUDE_custom.md as needed"
    else
        echo "  1. Review the merged CLAUDE.md"
        echo "  2. Test with your AI assistant"
        echo "  3. Customize as needed"
    fi
    echo ""

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if [ "$flagged" -gt 0 ]; then
        echo -e "${YELLOW}Status: ⚠️  Migration completed - Review recommended${RESET}"
    else
        echo -e "${GREEN}Status: ✅ Migration completed successfully${RESET}"
    fi
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# Generate simple summary (one line)
# Args: $1: total_issues, $2: auto_fixed, $3: flagged
generate_summary() {
    local total="$1"
    local fixed="$2"
    local flagged="$3"

    if [ "$total" -eq 0 ]; then
        echo -e "${GREEN}✓${RESET} No issues found"
    elif [ "$flagged" -eq 0 ]; then
        echo -e "${GREEN}✓${RESET} $total issues found, all auto-fixed"
    else
        echo -e "${YELLOW}⚠${RESET} $total issues found: $fixed auto-fixed, $flagged need review"
    fi
}

# Save report to file
# Args: $1: report_content, $2: output_file
save_report() {
    local content="$1"
    local output="$2"

    # Strip ANSI color codes for file output
    echo "$content" | sed 's/\x1b\[[0-9;]*m//g' > "$output"
    echo "Report saved to: $output"
}

# Create markdown report (for documentation)
# Args: $1: report_content, $2: output_file
save_markdown_report() {
    local content="$1"
    local output="$2"

    # Convert ANSI report to markdown
    # (Simplified - would need proper conversion in production)
    echo "$content" | sed 's/\x1b\[[0-9;]*m//g' | \
        sed 's/^### /### /' | \
        sed 's/^## /## /' | \
        sed 's/━━━/---/g' | \
        sed 's/╔═*╗/---/' | \
        sed 's/║/|/g' | \
        sed 's/╚═*╝/---/' > "$output"

    echo "Markdown report saved to: $output"
}

# Display report interactively (with paging if needed)
# Args: $1: report_content
display_report() {
    local content="$1"

    # Check if output is terminal and content is long
    if [ -t 1 ]; then
        local lines=$(echo "$content" | wc -l)
        if [ "$lines" -gt 40 ]; then
            echo "$content" | less -R
        else
            echo -e "$content"
        fi
    else
        echo -e "$content"
    fi
}
