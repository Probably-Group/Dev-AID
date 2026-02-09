#!/usr/bin/env bash
# Dev-AID Interactive Installer (backward-compatibility wrapper)
# Delegates to setup-dev-aid.sh --wizard-only
#
# For full setup, run: ./.dev-aid/scripts/setup-dev-aid.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/setup-dev-aid.sh" --wizard-only "$@"
