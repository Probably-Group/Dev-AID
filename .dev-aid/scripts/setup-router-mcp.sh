#!/bin/bash
# Interactive MCP Setup for Dev-AID Router
# Discovers and configures MCP servers for router context gathering

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROUTER_DIR="$SCRIPT_DIR/../orchestration"

echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}   Dev-AID Router - MCP Setup${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""
echo "This setup will:"
echo "  1. Discover MCP servers from Claude Code and Gemini CLI"
echo "  2. Let you choose which servers to enable for router"
echo "  3. Configure automatic context gathering"
echo ""

# Check if router CLI is available
if [ ! -f "$ROUTER_DIR/router-cli.sh" ]; then
    echo -e "${RED}✗ Router not found${NC}"
    echo "  Please run setup-venv.sh first"
    exit 1
fi

echo -e "${GREEN}Discovering MCP servers...${NC}"
echo ""

# Discover MCPs
cd "$ROUTER_DIR"
./router-cli.sh mcp discover

echo ""
echo -e "${YELLOW}─────────────────────────────────────────${NC}"
echo -e "${YELLOW}   Configure MCP Servers for Router${NC}"
echo -e "${YELLOW}─────────────────────────────────────────${NC}"
echo ""
echo "The router can use MCP servers to gather context before"
echo "generating responses. This makes responses much more accurate!"
echo ""
echo -e "${BLUE}Examples:${NC}"
echo "  • code-search → Find relevant code in your project"
echo "  • postgres → Get database schema for migrations"
echo "  • github → Check related issues/PRs"
echo ""

read -p "Do you want to configure MCP servers now? [Y/n] " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    # Get list of discovered servers
    SERVERS=$(./router-cli.sh mcp list 2>/dev/null | grep -E "^\s+(✓ Enabled|Disabled)" | awk '{print $3}')

    if [ -z "$SERVERS" ]; then
        echo -e "${YELLOW}⚠ No MCP servers found${NC}"
        echo ""
        echo "To add MCP servers:"
        echo -e "  ${BLUE}Claude Code:${NC} claude mcp add <name> ..."
        echo -e "  ${BLUE}Gemini CLI:${NC} Edit ~/.gemini/mcp.json"
        echo ""
        echo "After adding MCP servers, run this script again."
        exit 0
    fi

    echo ""
    echo -e "${BLUE}Found MCP servers:${NC}"
    echo ""

    while IFS= read -r server; do
        # Skip if empty
        if [ -z "$server" ]; then
            continue
        fi

        # Get server capabilities
        SERVER_INFO=$(./router-cli.sh mcp list 2>/dev/null | grep "$server")

        echo -e "${YELLOW}───────────────────────────────────────${NC}"
        echo -e "${BLUE}Server:${NC} $server"
        echo "$SERVER_INFO" | awk '{$1=$2=""; print "  "$0}'
        echo ""

        # Check if already enabled
        if echo "$SERVER_INFO" | grep -q "✓ Enabled"; then
            read -p "Currently enabled. Keep enabled? [Y/n] " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Nn]$ ]]; then
                ./router-cli.sh mcp disable "$server"
            else
                echo -e "${GREEN}✓${NC} Keeping enabled"
            fi
        else
            read -p "Enable for router? [Y/n] " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                ./router-cli.sh mcp enable "$server"
            else
                echo -e "${BLUE}→${NC} Skipped"
            fi
        fi
        echo ""
    done <<< "$SERVERS"

    echo -e "${GREEN}═══════════════════════════════════════════${NC}"
    echo -e "${GREEN}   MCP Configuration Complete!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════${NC}"
    echo ""

    # Show final configuration
    echo -e "${BLUE}Final Configuration:${NC}"
    echo ""
    ./router-cli.sh mcp list
    echo ""

    echo -e "${BLUE}Usage:${NC}"
    echo "  • To execute with MCP context:"
    echo "    ./router-cli.sh execute \"Generate database migration\" --mode challenger"
    echo ""
    echo "  • The router will automatically:"
    echo "    1. Detect task type (database, github, etc.)"
    echo "    2. Query relevant MCP servers"
    echo "    3. Include context in AI prompts"
    echo ""
    echo "  • To manage MCPs later:"
    echo "    ./router-cli.sh mcp discover  # Scan for new MCPs"
    echo "    ./router-cli.sh mcp enable <name>"
    echo "    ./router-cli.sh mcp disable <name>"
    echo "    ./router-cli.sh mcp sync  # Re-scan all"
    echo ""

else
    echo -e "${BLUE}→${NC} Skipped MCP configuration"
    echo ""
    echo "You can configure MCPs later with:"
    echo "  ./.dev-aid/scripts/setup-router-mcp.sh"
    echo ""
fi

echo -e "${GREEN}✓ Setup complete!${NC}"
