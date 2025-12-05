#!/usr/bin/env bash
#
# Script: detect-context.sh
# Description: Detects project context by analyzing files, keywords, and technologies
# Usage: detect-context.sh [directory]
#
# Note: This is now a lightweight wrapper around the optimized Python implementation

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_DIR="${1:-.}"
readonly PYTHON_DETECTOR="$SCRIPT_DIR/context-detector.py"

# Validate project directory
if [[ ! -d "$PROJECT_DIR" ]]; then
    echo "Error: Directory does not exist: $PROJECT_DIR" >&2
    exit 1
fi

# Check if Python detector exists
if [[ ! -x "$PYTHON_DETECTOR" ]]; then
    echo "Error: Python detector not found or not executable: $PYTHON_DETECTOR" >&2
    exit 1
fi

# Use optimized Python implementation
exec "$PYTHON_DETECTOR" detect "$PROJECT_DIR"
