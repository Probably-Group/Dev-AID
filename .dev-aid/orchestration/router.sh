#!/bin/bash

# Dev-AID Router - AI Model Orchestration Engine
# Routes tasks to appropriate AI models based on configuration

set -euo pipefail

# Configuration paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEV_AID_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_DIR="$DEV_AID_ROOT/.dev-aid/config"

# Load configuration
load_config() {
    if [ ! -f "$CONFIG_DIR/settings.json" ]; then
        echo "Error: settings.json not found" >&2
        exit 1
    fi

    # Extract configuration using jq (or fallback to grep if jq not available)
    if command -v jq &> /dev/null; then
        ORCHESTRATION_MODE=$(jq -r '.orchestration_mode' "$CONFIG_DIR/settings.json")
        DEFAULT_MODEL=$(jq -r '.default_model' "$CONFIG_DIR/settings.json")
    else
        # Fallback to grep/sed
        ORCHESTRATION_MODE=$(grep '"orchestration_mode"' "$CONFIG_DIR/settings.json" | sed 's/.*: *"\([^"]*\)".*/\1/')
        DEFAULT_MODEL=$(grep '"default_model"' "$CONFIG_DIR/settings.json" | sed 's/.*: *"\([^"]*\)".*/\1/')
    fi
}

# Route task based on mode
route_task() {
    local task_type="${1:-general}"
    local context_size="${2:-0}"
    local keywords="${3:-}"

    case "$ORCHESTRATION_MODE" in
        solo)
            "$SCRIPT_DIR/modes/solo.sh" "$DEFAULT_MODEL"
            ;;

        ensemble)
            "$SCRIPT_DIR/modes/ensemble.sh" "$task_type" "$context_size" "$keywords"
            ;;

        challenger)
            "$SCRIPT_DIR/modes/challenger.sh" "$task_type"
            ;;

        *)
            echo "Error: Unknown orchestration mode: $ORCHESTRATION_MODE" >&2
            echo "Defaulting to solo mode with $DEFAULT_MODEL" >&2
            "$SCRIPT_DIR/modes/solo.sh" "$DEFAULT_MODEL"
            ;;
    esac
}

# Main execution
main() {
    load_config

    local task_type="${1:-general}"
    local context_size="${2:-0}"
    local keywords="${3:-}"

    route_task "$task_type" "$context_size" "$keywords"
}

# Run if executed directly
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
