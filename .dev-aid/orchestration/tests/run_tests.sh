#!/usr/bin/env bash
# Test runner for Dev-AID Router

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly ROUTER_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m' # No Color

echo "========================================="
echo "Dev-AID Router Test Suite"
echo "========================================="
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}✗ pytest not found${NC}"
    echo "Install it with: pip install pytest pytest-cov"
    exit 1
fi

echo -e "${GREEN}✓ pytest found${NC}"
echo ""

# Change to router directory
cd "$ROUTER_DIR"

# Run tests
echo "Running tests..."
echo ""

if pytest tests/ -v --tb=short --color=yes; then
    echo ""
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo -e "${GREEN}=========================================${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}=========================================${NC}"
    echo -e "${RED}✗ Some tests failed${NC}"
    echo -e "${RED}=========================================${NC}"
    exit 1
fi
