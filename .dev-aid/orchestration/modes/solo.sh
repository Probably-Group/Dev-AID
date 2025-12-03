#!/bin/bash

# Dev-AID Solo Mode
# Single model handles all tasks

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEV_AID_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Solo mode: Use default model for everything
solo_mode() {
    local model="${1:-claude-sonnet-4.5}"

    echo "🎯 Solo Mode: Using $model"
    echo ""
    echo "All tasks will be handled by your default AI model."
    echo ""
    echo "Model: $model"
    echo "Mode: Solo (single model)"
    echo ""
}

# Main execution
main() {
    local model="${1:-claude-sonnet-4.5}"
    solo_mode "$model"
}

# Run if executed directly
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
