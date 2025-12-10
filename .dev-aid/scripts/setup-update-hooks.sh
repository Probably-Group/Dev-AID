#!/bin/bash
# Setup update check hooks for Claude Code and Gemini CLI
# This script installs hooks that check for Dev-AID updates weekly

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    Dev-AID Update Hooks Setup              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check if we're in a Dev-AID repository
if [ ! -d ".dev-aid" ]; then
    echo -e "${RED}❌ Error: Not in a Dev-AID repository${NC}"
    exit 1
fi

# Detect which CLI tools are available
HAS_CLAUDE=false
HAS_GEMINI=false

if command -v claude &>/dev/null; then
    HAS_CLAUDE=true
fi

if command -v gemini &>/dev/null || command -v gemini-cli &>/dev/null; then
    HAS_GEMINI=true
fi

if [ "$HAS_CLAUDE" = false ] && [ "$HAS_GEMINI" = false ]; then
    echo -e "${YELLOW}⚠️  No supported CLI tools detected${NC}"
    echo "   Supported: Claude Code, Gemini CLI"
    echo ""
    echo "Hooks will still be configured for when you install these tools."
    echo ""
fi

# Setup Claude Code hooks
echo -e "${BLUE}→ Setting up Claude Code hooks...${NC}"

CLAUDE_HOOK_SOURCE=".dev-aid/providers/claude/.claude/hooks.json"
CLAUDE_HOOK_DEST=".claude/hooks.json"

if [ -f "$CLAUDE_HOOK_SOURCE" ]; then
    # Create .claude directory if it doesn't exist
    mkdir -p .claude

    # Copy hooks configuration
    cp "$CLAUDE_HOOK_SOURCE" "$CLAUDE_HOOK_DEST"

    echo -e "${GREEN}✓ Claude Code hooks configured${NC}"
    echo "  Location: $CLAUDE_HOOK_DEST"

    if [ "$HAS_CLAUDE" = true ]; then
        echo -e "${GREEN}  Claude Code detected - hooks will run on next session${NC}"
    else
        echo -e "${YELLOW}  Claude Code not detected - hooks will activate when installed${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Hook template not found: $CLAUDE_HOOK_SOURCE${NC}"
fi

echo ""

# Setup Gemini CLI hooks
echo -e "${BLUE}→ Setting up Gemini CLI hooks...${NC}"

GEMINI_HOOK_SOURCE=".dev-aid/providers/gemini/.gemini/hooks.toml"
GEMINI_HOOK_DEST=".gemini/hooks.toml"

if [ -f "$GEMINI_HOOK_SOURCE" ]; then
    # Create .gemini directory if it doesn't exist
    mkdir -p .gemini

    # Copy hooks configuration
    cp "$GEMINI_HOOK_SOURCE" "$GEMINI_HOOK_DEST"

    echo -e "${GREEN}✓ Gemini CLI hooks configured${NC}"
    echo "  Location: $GEMINI_HOOK_DEST"

    if [ "$HAS_GEMINI" = true ]; then
        echo -e "${GREEN}  Gemini CLI detected - hooks will run on next session${NC}"
    else
        echo -e "${YELLOW}  Gemini CLI not detected - hooks will activate when installed${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Hook template not found: $GEMINI_HOOK_SOURCE${NC}"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         Hooks Setup Complete! ✅           ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${BLUE}What was configured:${NC}"
echo "  ✓ Weekly update checks (cached for 7 days)"
echo "  ✓ Silent mode (non-intrusive notifications)"
echo "  ✓ Runs on CLI session start"
echo ""

echo -e "${BLUE}How it works:${NC}"
echo "  - Checks GitHub for new Dev-AID versions"
echo "  - Shows notification if update available"
echo "  - Respects GitHub rate limits (60 req/hour free)"
echo "  - Caches result for 7 days"
echo ""

echo -e "${BLUE}To disable auto-check:${NC}"
echo "  1. Remove hook files:"
echo "     rm .claude/hooks.json .gemini/hooks.toml"
echo ""
echo "  2. Or set environment variable:"
echo "     export DEV_AID_UPDATE_CHECK_DISABLED=true"
echo ""

echo -e "${BLUE}To test update check:${NC}"
echo "  ./.dev-aid/scripts/check-updates.sh"
echo ""
