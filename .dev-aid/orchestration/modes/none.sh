#!/bin/bash

# Dev-AID None (Manual) Mode
# User explicitly selects AI model for each task

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEV_AID_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# None mode: No automatic routing - user chooses manually
none_mode() {
    echo "🎛️  Manual Mode (No Orchestration)"
    echo ""
    echo "You are in full control of which AI model to use."
    echo ""
    echo "To use a specific model, explicitly specify it in your prompt:"
    echo ""
    echo "Examples:"
    echo "  • '@claude analyze this code'"
    echo "  • '@gemini read all files in /src'"
    echo "  • '@openai write a README'"
    echo ""
    echo "Or use your default AI interface (Claude Code, etc.)"
    echo ""
    echo "💡 Tip: Switch to Ensemble mode for automatic routing:"
    echo "   .dev-aid/scripts/reconfigure.sh"
    echo ""
}

# Main execution
main() {
    none_mode
}

# Run if executed directly
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
