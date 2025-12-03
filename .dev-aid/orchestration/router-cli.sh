#!/bin/bash
# Dev-AID Router CLI Wrapper
# Calls the Python router implementation

set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROUTER_DIR="$SCRIPT_DIR/router"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Check if dependencies are installed
check_dependencies() {
    python3 -c "import anthropic" 2>/dev/null || {
        echo -e "${YELLOW}Warning: anthropic package not installed${NC}" >&2
        echo "Install with: pip install -r $SCRIPT_DIR/requirements.txt" >&2
        return 1
    }
    return 0
}

# Execute router CLI
execute_router() {
    # Add router directory to PYTHONPATH
    export PYTHONPATH="$SCRIPT_DIR:${PYTHONPATH:-}"

    # Execute Python CLI
    python3 -m router.cli "$@"
}

# Main execution
main() {
    # Check dependencies (non-fatal)
    check_dependencies || true

    # Execute router
    execute_router "$@"
}

# Run
main "$@"
