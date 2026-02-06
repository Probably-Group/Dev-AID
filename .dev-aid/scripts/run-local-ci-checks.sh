#!/usr/bin/env bash
# Run the same checks locally that CI runs
# This ensures your code will pass CI before pushing
# Part of Dev-AID Pre-Commit Validation System

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ORCHESTRATION_DIR="$(dirname "$SCRIPT_DIR")/orchestration"
ROOT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Temp file cleanup
TEMP_FILES=()
cleanup() { rm -f "${TEMP_FILES[@]}" 2>/dev/null; }
trap cleanup EXIT

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Dev-AID Local CI Checks${NC}"
echo "========================================"
echo "Running the same checks that CI runs..."
echo

# Track failures
FAILURES=0
CHECKS_RUN=0

# Helper function to run a check
run_check() {
    local name="$1"
    local command="$2"
    local log_file
    log_file=$(mktemp /tmp/devaid-check-XXXXXX.log)
    TEMP_FILES+=("$log_file")

    CHECKS_RUN=$((CHECKS_RUN + 1))
    echo -e "${BLUE}[$CHECKS_RUN] $name${NC}"

    if bash -c "$command" > "$log_file" 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        echo
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        echo -e "${YELLOW}Error details:${NC}"
        tail -20 "$log_file"
        echo
        FAILURES=$((FAILURES + 1))
        return 1
    fi
}

# Ensure we're in the right directory
cd "$ROOT_DIR"

# Check if orchestration venv exists
VENV_PATH="$ORCHESTRATION_DIR/venv"
if [ ! -d "$VENV_PATH" ]; then
    VENV_PATH="$ORCHESTRATION_DIR/.venv"
    if [ ! -d "$VENV_PATH" ]; then
        echo -e "${RED}❌ Python virtual environment not found${NC}"
        echo "   Please set up the environment first."
        exit 1
    fi
fi

# Activate venv
echo -e "${BLUE}📦 Activating Python environment...${NC}"
# shellcheck disable=SC1091
source "$VENV_PATH/bin/activate"
echo -e "${GREEN}✓ Environment active${NC}"
echo

# Check Node.js (for TOON tests)
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js available: $NODE_VERSION${NC}"

    # Install npm dependencies if needed
    if [ -f "$ORCHESTRATION_DIR/package.json" ] && [ ! -d "$ORCHESTRATION_DIR/node_modules" ]; then
        echo -e "${BLUE}📦 Installing npm dependencies...${NC}"
        cd "$ORCHESTRATION_DIR" && npm install --silent
        cd "$ROOT_DIR"
    fi
else
    echo -e "${YELLOW}⚠️  Node.js not found - TOON tests will be skipped${NC}"
fi
echo

# 1. Black formatting check
run_check "Black (Code Formatting)" \
    "cd '$ORCHESTRATION_DIR' && black --check --diff ."

# 2. isort import sorting check
run_check "isort (Import Sorting)" \
    "cd '$ORCHESTRATION_DIR' && isort --check-only --diff ."

# 3. Flake8 linting
run_check "Flake8 (Linting)" \
    "cd '$ORCHESTRATION_DIR' && flake8 . --max-line-length=120 --extend-ignore=E203,W503 --exclude .venv,venv,node_modules"

# 4. MyPy type checking (non-blocking)
echo -e "${BLUE}[$((CHECKS_RUN + 1))] MyPy (Type Checking)${NC}"
CHECKS_RUN=$((CHECKS_RUN + 1))
MYPY_LOG=$(mktemp /tmp/devaid-check-XXXXXX.log)
TEMP_FILES+=("$MYPY_LOG")
if cd "$ORCHESTRATION_DIR" && mypy router --ignore-missing-imports --no-strict-optional > "$MYPY_LOG" 2>&1; then
    echo -e "${GREEN}✓ PASS${NC}"
else
    echo -e "${YELLOW}⚠️  WARNINGS (non-blocking)${NC}"
    tail -10 "$MYPY_LOG"
fi
echo

# 5. Pytest unit tests
run_check "Pytest (Unit Tests)" \
    "cd '$ORCHESTRATION_DIR' && pytest tests/ -v --tb=short -x"

# 6. Shellcheck (bash scripts)
if command -v shellcheck &> /dev/null; then
    echo -e "${BLUE}[$((CHECKS_RUN + 1))] Shellcheck (Bash Scripts)${NC}"
    CHECKS_RUN=$((CHECKS_RUN + 1))

    # Find all .sh files in .dev-aid
    mapfile -t SHELL_FILES < <(find .dev-aid/scripts -name "*.sh" 2>/dev/null)
    SHELLCHECK_LOG=$(mktemp /tmp/devaid-check-XXXXXX.log)
    TEMP_FILES+=("$SHELLCHECK_LOG")

    if [ ${#SHELL_FILES[@]} -gt 0 ]; then
        if shellcheck "${SHELL_FILES[@]}" > "$SHELLCHECK_LOG" 2>&1; then
            echo -e "${GREEN}✓ PASS${NC}"
        else
            echo -e "${YELLOW}⚠️  WARNINGS (non-blocking)${NC}"
            tail -10 "$SHELLCHECK_LOG"
        fi
    else
        echo -e "${YELLOW}⚠️  No shell scripts found${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Shellcheck not installed - skipping bash lint${NC}"
fi
echo

# Summary
echo "========================================"
if [ "$FAILURES" -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED! ($CHECKS_RUN checks)${NC}"
    echo
    echo "Your code is ready to push! 🚀"
    echo "CI should pass without issues."
    exit 0
else
    echo -e "${RED}❌ $FAILURES CHECK(S) FAILED (out of $CHECKS_RUN)${NC}"
    echo
    echo "Please fix the issues above before pushing."
    echo
    echo -e "${YELLOW}Quick fixes:${NC}"
    echo "  • Black formatting:  cd .dev-aid/orchestration && black ."
    echo "  • isort imports:     cd .dev-aid/orchestration && isort ."
    echo "  • Run tests:         cd .dev-aid/orchestration && pytest tests/"
    echo
    exit 1
fi
