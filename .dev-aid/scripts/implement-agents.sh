#!/usr/bin/env bash
# Agent Integration Implementation Script
# Creates all agents, slash commands, and updates documentation

set -euo pipefail

echo "======================================"
echo "Dev-AID Agent Integration"
echo "======================================"
echo ""

# Update renamed command names
echo "📝 Updating command names in renamed files..."

update_command_name() {
    local file="$1"
    local old_name="$2"
    local new_name="$3"

    if [[ -f "$file" ]]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/^name: $old_name$/name: $new_name/" "$file"
        else
            sed -i "s/^name: $old_name$/name: $new_name/" "$file"
        fi
        echo "  ✅ Updated $file"
    fi
}

# Update all renamed commands
update_command_name ".dev-aid/providers/claude/.claude/commands/operations/dev-aid-deploy-validate.md" "aid-deploy-validate" "dev-aid-deploy-validate"
update_command_name ".dev-aid/providers/claude/.claude/commands/quality/dev-aid-code-health.md" "aid-code-health" "dev-aid-code-health"
update_command_name ".dev-aid/providers/claude/.claude/commands/quality/dev-aid-debt-analysis.md" "aid-debt-analysis" "dev-aid-debt-analysis"
update_command_name ".dev-aid/providers/claude/.claude/commands/router/dev-aid-router-challenger-rag.md" "aid-router-challenger-rag" "dev-aid-router-challenger-rag"
update_command_name ".dev-aid/providers/claude/.claude/commands/router/dev-aid-router-challenger.md" "aid-router-challenger" "dev-aid-router-challenger"
update_command_name ".dev-aid/providers/claude/.claude/commands/router/dev-aid-router-ensemble.md" "aid-router-ensemble" "dev-aid-router-ensemble"
update_command_name ".dev-aid/providers/claude/.claude/commands/router/dev-aid-router-status.md" "aid-router-status" "dev-aid-router-status"
update_command_name ".dev-aid/providers/claude/.claude/commands/security/dev-aid-audit.md" "aid-audit" "dev-aid-audit"
update_command_name ".dev-aid/providers/claude/.claude/commands/security/dev-aid-vulnerability-scan.md" "aid-vulnerability-scan" "dev-aid-vulnerability-scan"
update_command_name ".dev-aid/providers/claude/.claude/commands/setup/dev-aid-analyze.md" "aid-analyze" "dev-aid-analyze"
update_command_name ".dev-aid/providers/claude/.claude/commands/setup/dev-aid-build-skill.md" "aid-build-skill" "dev-aid-build-skill"
update_command_name ".dev-aid/providers/claude/.claude/commands/setup/dev-aid-status.md" "aid-status" "dev-aid-status"

echo ""
echo "✅ All command names updated!"
echo ""
echo "Next steps:"
echo "1. Run Task tool to fetch and adapt agents from repositories"
echo "2. Create Claude commands, Gemini commands, and Claude agents"
echo "3. Create AGENT-CREDITS.md"
echo "4. Update all documentation references"
echo ""
