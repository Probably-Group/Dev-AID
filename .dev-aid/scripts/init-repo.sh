#!/usr/bin/env bash
# Dev-AID Repository Initialization (backward-compatibility wrapper)
#
# Thin wrapper that delegates to setup-dev-aid.sh with whatever args
# the caller passed. Used by `gh dev-aid init` and any historical
# scripts that called init-repo.sh directly.
#
# IMPORTANT: This wrapper used to default to `--infrastructure-only`,
# which silently skipped phases 3 (Configuration Wizard), 5 (Provider
# Context Files), and 6 (Memory Bank) — the three phases that need
# user input. Beta testers running `gh dev-aid init` got an install
# that "looked done" but had no model assignments, no API keys, and
# no provider symlinks.
#
# Fix: forward args verbatim and let setup-dev-aid.sh decide which
# phases to run based on detected state. A fresh install runs all 8
# phases. An already-installed project runs all 8 phases too, but
# detect_state() suppresses redundant work (the existing wizard re-
# init flow uses load_existing_settings to pre-fill defaults).
#
# To get the OLD behavior (skip wizard / provider / memory bank),
# pass --infrastructure-only explicitly:
#     ./.dev-aid/scripts/init-repo.sh --infrastructure-only

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/setup-dev-aid.sh" "$@"
