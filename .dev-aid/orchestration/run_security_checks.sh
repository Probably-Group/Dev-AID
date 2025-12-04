#!/bin/bash
#
# Security Checks Script for Dev-AID Router
# Runs all security and quality checks as required by Python skill
#

set -e  # Exit on error

echo "========================================="
echo "Dev-AID Router Security Checks"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track failures
FAILURES=0

# Function to run a check
run_check() {
    local name="$1"
    local command="$2"

    echo -e "${YELLOW}Running: ${name}${NC}"
    if eval "$command"; then
        echo -e "${GREEN}✓ ${name} PASSED${NC}"
        echo ""
    else
        echo -e "${RED}✗ ${name} FAILED${NC}"
        echo ""
        FAILURES=$((FAILURES + 1))
    fi
}

# Change to orchestration directory
cd "$(dirname "$0")"

echo "Step 1: Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "========================================="
echo "Phase 1: Testing"
echo "========================================="
echo ""

run_check "Unit Tests" "pytest tests/ -v --tb=short"
run_check "Test Coverage (80%+)" "pytest tests/ --cov=router --cov-fail-under=80 --cov-report=term-missing"
run_check "Security Tests" "pytest tests/test_security.py -v"

echo ""
echo "========================================="
echo "Phase 2: Static Analysis"
echo "========================================="
echo ""

run_check "Bandit Security Scan" "bandit -r router/ -ll"
run_check "MyPy Type Checking" "mypy router/ --strict --ignore-missing-imports"

echo ""
echo "========================================="
echo "Phase 3: Dependency Security"
echo "========================================="
echo ""

run_check "Pip Audit" "pip-audit --desc"
run_check "Safety Check" "safety check --json || safety check"

echo ""
echo "========================================="
echo "Phase 4: Code Quality"
echo "========================================="
echo ""

run_check "Black Formatting Check" "black --check router/ tests/"
run_check "Isort Import Order" "isort --check router/ tests/"
run_check "Flake8 Linting" "flake8 router/ --max-line-length=100 --extend-ignore=E203,W503"

echo ""
echo "========================================="
echo "Summary"
echo "========================================="
echo ""

if [ $FAILURES -eq 0 ]; then
    echo -e "${GREEN}✓ All security checks PASSED${NC}"
    echo ""
    echo "Code is ready for production deployment."
    exit 0
else
    echo -e "${RED}✗ ${FAILURES} check(s) FAILED${NC}"
    echo ""
    echo "Please fix the issues above before deploying."
    exit 1
fi
