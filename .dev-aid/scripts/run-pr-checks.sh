#!/bin/bash
# Run all PR checks locally before pushing
# Usage: ./.dev-aid/scripts/run-pr-checks.sh

set -e

REPO_ROOT="$(git rev-parse --show-toplevel)"
ORCH_DIR="$REPO_ROOT/.dev-aid/orchestration"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 Running ALL PR Checks Locally"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Track failures
FAILED_CHECKS=()

# Function to run a check
run_check() {
    local name="$1"
    local command="$2"

    echo "┌─────────────────────────────────────────────────────"
    echo "│ 🔍 $name"
    echo "└─────────────────────────────────────────────────────"

    if eval "$command"; then
        echo "✅ $name passed"
    else
        echo "❌ $name failed"
        FAILED_CHECKS+=("$name")
    fi
    echo ""
}

# Python checks (orchestration)
if [ -d "$ORCH_DIR" ]; then
    cd "$ORCH_DIR"

    # Activate venv if it exists
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    elif [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    fi

    echo "📦 Running Python checks in orchestration..."
    echo ""

    run_check "Black (formatting)" "black --check --diff ."
    run_check "Flake8 (linting)" "flake8 . --max-line-length=120 --extend-ignore=E203,W503 --exclude=venv,.venv,__pycache__,.git"
    run_check "MyPy (type checking)" "mypy router --ignore-missing-imports --no-strict-optional"
    run_check "Pytest (tests)" "pytest tests/ -v --tb=short"
    run_check "Coverage (59%+)" "pytest tests/ --cov=router --cov-report=term-missing --cov-fail-under=59"
fi

# Bash linting
cd "$REPO_ROOT"
echo "📦 Running Bash checks..."
echo ""

BASH_FILES=$(find .dev-aid/scripts -name "*.sh" 2>/dev/null || true)
if [ -n "$BASH_FILES" ]; then
    run_check "Shellcheck (bash linting)" "shellcheck $BASH_FILES"
fi

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 PR Checks Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ${#FAILED_CHECKS[@]} -eq 0 ]; then
    echo "✅ All checks passed! Safe to push."
    echo ""
    echo "Next steps:"
    echo "  git push origin <branch-name>"
    exit 0
else
    echo "❌ ${#FAILED_CHECKS[@]} check(s) failed:"
    for check in "${FAILED_CHECKS[@]}"; do
        echo "  • $check"
    done
    echo ""
    echo "Please fix the issues above before pushing."
    echo ""
    echo "Quick fixes:"
    echo "  • Black formatting: cd .dev-aid/orchestration && black ."
    echo "  • Flake8 errors: Review and fix linting issues manually"
    echo "  • MyPy errors: Add type hints or update code"
    echo "  • Test failures: Debug and fix failing tests"
    exit 1
fi
