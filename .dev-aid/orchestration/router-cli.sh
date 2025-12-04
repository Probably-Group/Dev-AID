#!/bin/bash
# Dev-AID Router CLI Wrapper
# Calls the Python router implementation
# Automatically uses virtual environment if available

set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROUTER_DIR="$SCRIPT_DIR/router"
VENV_DIR="$SCRIPT_DIR/.venv"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not found${NC}" >&2
    echo "Please install Python 3.9 or higher" >&2
    exit 1
fi

# Check if router package exists
if [ ! -f "$ROUTER_DIR/__init__.py" ]; then
    echo -e "${RED}Error: Router package not found at $ROUTER_DIR${NC}" >&2
    exit 1
fi

# Check and activate virtual environment
activate_venv() {
    if [ -d "$VENV_DIR" ]; then
        # Virtual environment exists - activate it
        if [ -f "$VENV_DIR/bin/activate" ]; then
            source "$VENV_DIR/bin/activate"
            return 0
        else
            echo -e "${YELLOW}Warning: venv directory exists but activate script not found${NC}" >&2
            return 1
        fi
    else
        # No virtual environment - warn user
        return 1
    fi
}

# Check if dependencies are installed
check_dependencies() {
    python3 -c "import anthropic" 2>/dev/null || {
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" >&2
        echo -e "${YELLOW}⚠️  Router dependencies not installed${NC}" >&2
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" >&2
        echo "" >&2
        echo -e "${BLUE}Recommended: Use virtual environment to avoid conflicts${NC}" >&2
        echo "" >&2
        echo -e "Run: ${GREEN}$SCRIPT_DIR/setup-venv.sh${NC}" >&2
        echo "" >&2
        echo -e "This will:" >&2
        echo -e "  • Create isolated Python environment" >&2
        echo -e "  • Install all dependencies" >&2
        echo -e "  • Keep your system Python clean" >&2
        echo "" >&2
        echo -e "Or install manually (NOT recommended):" >&2
        echo -e "  ${YELLOW}pip install -r $SCRIPT_DIR/requirements.txt${NC}" >&2
        echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" >&2
        return 1
    }
    return 0
}

# Execute router CLI
execute_router() {
    # Try to activate venv first
    if ! activate_venv; then
        # No venv - check if dependencies are in system Python
        if ! check_dependencies; then
            exit 1
        fi
    fi

    # Add router directory to PYTHONPATH
    export PYTHONPATH="$SCRIPT_DIR:${PYTHONPATH:-}"

    # Execute Python CLI
    python3 -m router.cli "$@"

    local exit_code=$?

    # Deactivate venv if it was activated
    if [ -n "${VIRTUAL_ENV:-}" ]; then
        deactivate 2>/dev/null || true
    fi

    return $exit_code
}

# Main execution
main() {
    execute_router "$@"
}

# Run
main "$@"
