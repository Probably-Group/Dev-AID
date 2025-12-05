#!/usr/bin/env bash
#
# Script: select-skills.sh
# Description: Selects relevant skills based on context using scoring algorithm
# Usage: select-skills.sh "context keywords" [max_skills]
#
# Note: This is now a lightweight wrapper around the optimized Python implementation

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"
readonly PYTHON_DETECTOR="$SCRIPT_DIR/context-detector.py"

# Input validation
if [[ $# -lt 1 ]]; then
    echo "Usage: $SCRIPT_NAME \"context keywords\" [max_skills]" >&2
    exit 1
fi

readonly CONTEXT="$1"
readonly MAX_SKILLS="${2:-5}"

# Check if Python detector exists
if [[ ! -x "$PYTHON_DETECTOR" ]]; then
    echo "Error: Python detector not found or not executable: $PYTHON_DETECTOR" >&2
    exit 1
fi

# Use optimized Python implementation
exec "$PYTHON_DETECTOR" select "$CONTEXT" "$MAX_SKILLS"
