#!/usr/bin/env bash
# Living README - Documentation Drift Detector
# Detects when docs drift out of sync with reality

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SYNCER="$SCRIPT_DIR/../orchestration/doc-sync.py"

# Colors
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

main() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Dev-AID Living README${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    # Check if Python 3 is available
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is required but not found"
        exit 1
    fi

    # Run syncer
    python3 "$SYNCER" "$@"
}

main "$@"
