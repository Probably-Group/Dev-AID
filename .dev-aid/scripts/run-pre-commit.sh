#!/usr/bin/env bash
# Run pre-commit checks manually
# Usage: ./run-pre-commit.sh [files...]

set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

echo "🔍 Running pre-commit checks..."
echo ""

# Install pre-commit if not already installed
if ! command -v pre-commit &> /dev/null; then
    echo "Installing pre-commit..."
    pip install pre-commit
    pre-commit install
fi

# Run on specified files or all files
if [ $# -gt 0 ]; then
    echo "Checking specified files: $*"
    pre-commit run --files "$@"
else
    echo "Checking all files..."
    pre-commit run --all-files
fi

echo ""
echo "✅ Pre-commit checks completed!"
