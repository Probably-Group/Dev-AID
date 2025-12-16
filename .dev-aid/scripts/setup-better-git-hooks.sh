#!/bin/bash
# Setup improved Git hooks that match CI checks exactly
# Part of Dev-AID Pre-Commit Validation System

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "🔧 Setting up Dev-AID Git Hooks"
echo "================================"
echo

# Create hooks directory if it doesn't exist
mkdir -p "$ROOT_DIR/.git/hooks"

# Create improved pre-commit hook
cat > "$ROOT_DIR/.git/hooks/pre-commit" << 'HOOK_EOF'
#!/bin/bash
# Dev-AID Pre-Commit Hook (Improved)
# Runs the same checks as CI to catch issues early

# Find the Dev-AID root
HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
GIT_DIR="$(dirname "$HOOK_DIR")"
ROOT_DIR="$(dirname "$GIT_DIR")"
ORCHESTRATION_DIR="$ROOT_DIR/.dev-aid/orchestration"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if Python files changed
if git diff --cached --name-only | grep -q "\.py$"; then
    echo -e "${BLUE}🔍 Python files changed - running checks...${NC}"

    # Find venv
    VENV_PATH="$ORCHESTRATION_DIR/venv"
    if [ ! -d "$VENV_PATH" ]; then
        VENV_PATH="$ORCHESTRATION_DIR/.venv"
    fi

    if [ ! -d "$VENV_PATH" ]; then
        echo -e "${YELLOW}⚠️  No venv found - skipping Python checks${NC}"
        echo "   Run: cd .dev-aid/orchestration && python -m venv .venv"
        exit 0
    fi

    # Activate venv and run checks
    source "$VENV_PATH/bin/activate"

    # Run black
    echo -e "${BLUE}  → Black (formatting)...${NC}"
    if ! black --check --quiet $ORCHESTRATION_DIR 2>/dev/null; then
        echo -e "${YELLOW}  ⚠️  Black formatting needed - auto-fixing...${NC}"
        black $ORCHESTRATION_DIR
        # Re-add formatted files
        git add $ORCHESTRATION_DIR/**/*.py
        echo -e "${GREEN}  ✓ Files formatted and re-staged${NC}"
    fi

    # Run isort
    echo -e "${BLUE}  → isort (imports)...${NC}"
    if ! isort --check-only --quiet $ORCHESTRATION_DIR 2>/dev/null; then
        echo -e "${YELLOW}  ⚠️  Import sorting needed - auto-fixing...${NC}"
        isort $ORCHESTRATION_DIR
        # Re-add sorted files
        git add $ORCHESTRATION_DIR/**/*.py
        echo -e "${GREEN}  ✓ Imports sorted and re-staged${NC}"
    fi

    # Run flake8 (don't auto-fix, just warn)
    echo -e "${BLUE}  → Flake8 (linting)...${NC}"
    if ! flake8 $ORCHESTRATION_DIR --max-line-length=120 --extend-ignore=E203,W503 --exclude .venv,venv,node_modules 2>/dev/null; then
        echo -e "${RED}  ✗ Flake8 errors found!${NC}"
        echo -e "${YELLOW}  Please fix linting errors before committing.${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ All pre-commit checks passed!${NC}"
fi

exit 0
HOOK_EOF

# Make hook executable
chmod +x "$ROOT_DIR/.git/hooks/pre-commit"

echo "✅ Git hooks installed!"
echo
echo "📋 What was set up:"
echo "  • Pre-commit hook: Auto-formats with black & isort"
echo "  • Flake8 linting: Blocks commits with errors"
echo "  • Matches CI checks: Same rules as GitHub Actions"
echo
echo "💡 Usage:"
echo "  • Hooks run automatically on 'git commit'"
echo "  • Auto-fixes formatting issues"
echo "  • Run full CI checks: .dev-aid/scripts/run-local-ci-checks.sh"
echo
echo "✨ Your commits will now pass CI checks!"
