#!/usr/bin/env bash
#
# Script: session-end.sh
# Description: Codex CLI SessionEnd hook - saves session progress
# Usage: Called automatically by Codex CLI at session end
#

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"

# Export provider identifier
export DEV_AID_PROVIDER="codex"

# Run the centralized session progress script
if [[ -x "$PROJECT_ROOT/.dev-aid/scripts/save-session-progress.sh" ]]; then
    "$PROJECT_ROOT/.dev-aid/scripts/save-session-progress.sh" "$PROJECT_ROOT"
else
    echo "[warn] Session progress script not found"
fi
