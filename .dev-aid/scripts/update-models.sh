#!/bin/bash
# Dev-AID Model Auto-Discovery
# Discovers and updates to latest AI model versions

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🔄 Dev-AID Model Auto-Discovery${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Get Dev-AID root
DEV_AID_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$DEV_AID_ROOT"

# Check if venv exists and activate it
VENV_DIR=".dev-aid/orchestration/venv"
if [ -d "$VENV_DIR" ]; then
    echo -e "${BLUE}→ Activating virtual environment...${NC}"
    source "$VENV_DIR/bin/activate"
else
    echo -e "${YELLOW}⚠ Virtual environment not found${NC}"
    echo -e "${YELLOW}  Run: ./.dev-aid/orchestration/setup-venv.sh${NC}"
    exit 1
fi

# Run model discovery
echo -e "${BLUE}→ Running model discovery...${NC}"
echo ""

python3 .dev-aid/orchestration/models-updater.py "$@"

echo ""
echo -e "${GREEN}Done!${NC}"
