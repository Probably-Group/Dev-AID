#!/usr/bin/env bash
# Generate Test Data from Schemas
# Creates realistic mock data for testing

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly FACTORY="$SCRIPT_DIR/../orchestration/data-factory.py"

# Colors
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

main() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Dev-AID Test Data Factory${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    # Check if Python 3 is available
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is required but not found"
        exit 1
    fi

    # Run factory
    python3 "$FACTORY" "$@"
}

main "$@"
