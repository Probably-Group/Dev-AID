#!/usr/bin/env bash
# Living README - Documentation Drift Detector
# Detects when docs drift out of sync with reality

set -euo pipefail

# shellcheck disable=SC2155
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SYNCER="$SCRIPT_DIR/../orchestration/doc-sync.py"
readonly VENV_DIR="$SCRIPT_DIR/../orchestration/venv"
readonly ALT_VENV_DIR="$SCRIPT_DIR/../orchestration/.venv"

# Colors
readonly BLUE='\033[0;34m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m'

main() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Dev-AID Living README${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    # Try to activate virtual environment if it exists
    PYTHON_CMD="python3"
    if [ -f "$VENV_DIR/bin/python3" ]; then
        # shellcheck disable=SC1091
        source "$VENV_DIR/bin/activate" 2>/dev/null || true
        PYTHON_CMD="$VENV_DIR/bin/python3"
    elif [ -f "$ALT_VENV_DIR/bin/python3" ]; then
        # shellcheck disable=SC1091
        source "$ALT_VENV_DIR/bin/activate" 2>/dev/null || true
        PYTHON_CMD="$ALT_VENV_DIR/bin/python3"
    fi

    # Check if Python 3 is available
    if ! command -v "$PYTHON_CMD" &> /dev/null; then
        echo "❌ Python 3 is required but not found"
        echo -e "${YELLOW}💡 Try running: .dev-aid/orchestration/setup-venv.sh${NC}"
        exit 1
    fi

    # Run syncer
    "$PYTHON_CMD" "$SYNCER" "$@"
}

main "$@"
