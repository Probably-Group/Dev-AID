#!/usr/bin/env bash
# Run update system integration tests
# Usage: ./run-update-tests.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    Dev-AID Update System Tests             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d ".dev-aid/orchestration/.venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found${NC}"
    echo "Creating virtual environment..."

    cd .dev-aid/orchestration
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    deactivate
    cd ../..

    echo -e "${GREEN}✓ Virtual environment created${NC}"
    echo ""
fi

# Activate virtual environment
echo -e "${BLUE}→ Activating virtual environment...${NC}"
source .dev-aid/orchestration/.venv/bin/activate

# Run tests
echo -e "${BLUE}→ Running update system tests...${NC}"
echo ""

python3 .dev-aid/orchestration/tests/test_update_system.py

TEST_EXIT_CODE=$?

# Deactivate virtual environment
deactivate

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║         All Tests Passed! ✅               ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
else
    echo -e "${RED}╔════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║         Tests Failed! ❌                   ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════╝${NC}"
fi

exit $TEST_EXIT_CODE
