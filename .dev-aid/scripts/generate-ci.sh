#!/usr/bin/env bash
# Generate GitHub Actions CI/CD Workflow
# Auto-detects project type and creates production-ready workflows

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly GENERATOR="$SCRIPT_DIR/../orchestration/ci-generator.py"

# Colors
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

main() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Dev-AID CI/CD Workflow Generator${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    # Check if Python 3 is available
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is required but not found"
        exit 1
    fi

    # Run generator
    python3 "$GENERATOR" "$@"
}

main "$@"
