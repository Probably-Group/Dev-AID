#!/bin/bash

# Dev-AID Router - AI Model Orchestration Engine
# Routes tasks to appropriate AI models based on configuration
#
# THIS IS NOW A WRAPPER FOR THE PYTHON IMPLEMENTATION
# See router/ directory for the actual implementation

set -euo pipefail

# Configuration paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Use Python CLI wrapper
ROUTER_CLI="$SCRIPT_DIR/router-cli.sh"

if [ ! -f "$ROUTER_CLI" ]; then
    echo "Error: Router CLI not found at $ROUTER_CLI" >&2
    exit 1
fi

# Execute router with Python implementation
"$ROUTER_CLI" "$@"
