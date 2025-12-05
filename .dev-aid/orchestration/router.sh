#!/usr/bin/env bash

# Dev-AID Router - AI Model Orchestration Engine
# Routes tasks to appropriate AI models based on configuration
#
# THIS IS NOW A WRAPPER FOR THE PYTHON IMPLEMENTATION
# See router/ directory for the actual implementation

set -euo pipefail

# Constants
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly ROUTER_CLI="$SCRIPT_DIR/router-cli.sh"

# Cleanup handler
cleanup() {
    local exit_code=$?
    # No resources to clean up in this wrapper, but trap is good practice
    exit "$exit_code"
}

trap cleanup EXIT INT TERM

# Usage function
usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS] COMMAND

Dev-AID Router - AI Model Orchestration Engine

COMMANDS:
    execute <request>    Execute a request with AI orchestration
    test                 Test router configuration
    version              Show router version

OPTIONS:
    -h, --help           Show this help message
    -v, --verbose        Enable verbose output

Examples:
    $(basename "$0") execute "implement user authentication"
    $(basename "$0") test

For more details, run: $(basename "$0") --help
EOF
}

# Handle help flag
if [[ "${1:-}" == "-h" ]] || [[ "${1:-}" == "--help" ]]; then
    usage
    exit 0
fi

# Validate router CLI exists
if [[ ! -f "$ROUTER_CLI" ]]; then
    echo "Error: Router CLI not found at $ROUTER_CLI" >&2
    exit 1
fi

# Execute router with Python implementation
"$ROUTER_CLI" "$@"
