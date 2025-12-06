#!/usr/bin/env bash
# Generate Architecture Diagrams
# Creates Mermaid.js diagrams for visual codebase understanding

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly MAPPER="$SCRIPT_DIR/../orchestration/architecture-mapper.py"

# Colors
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

main() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Dev-AID Architecture Mapper${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    # Check if Python 3 is available
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is required but not found"
        exit 1
    fi

    # Run mapper
    python3 "$MAPPER" "$@"
}

main "$@"
