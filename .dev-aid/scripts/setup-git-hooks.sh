#!/usr/bin/env bash
# Setup git hooks for Dev-AID development
# Usage: ./.dev-aid/scripts/setup-git-hooks.sh

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
GIT_HOOKS_DIR="$REPO_ROOT/.git/hooks"

echo "Setting up git hooks for Dev-AID..."

# Create pre-commit hook
cat > "$GIT_HOOKS_DIR/pre-commit" << 'HOOK_EOF'
#!/bin/bash
# Pre-commit hook for Dev-AID
# Runs formatting and linting checks before allowing commit

set -e

REPO_ROOT="$(git rev-parse --show-toplevel)"
ORCH_DIR="$REPO_ROOT/.dev-aid/orchestration"

echo "🔍 Running pre-commit checks..."

# Check if orchestration files are being committed
ORCH_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep "^\.dev-aid/orchestration/" || true)

if [ -n "$ORCH_FILES" ]; then
    echo "📝 Python files in orchestration changed, running checks..."

    cd "$ORCH_DIR"

    # Activate venv if it exists
    if [ -d "venv/bin/activate" ]; then
        source venv/bin/activate
    fi

    # 1. Black formatting check
    echo "  → Black (formatting)..."
    black --check --diff . || {
        echo "❌ Black formatting failed!"
        echo "💡 Run: cd .dev-aid/orchestration && black ."
        exit 1
    }

    # 2. Flake8 linting
    echo "  → Flake8 (linting)..."
    flake8 . --max-line-length=120 --extend-ignore=E203,W503 || {
        echo "❌ Flake8 linting failed!"
        exit 1
    }

    # 3. MyPy type checking
    echo "  → MyPy (type checking)..."
    mypy router --ignore-missing-imports --no-strict-optional || {
        echo "❌ MyPy type checking failed!"
        exit 1
    }

    # 4. Encoding guard — catches Windows cp1252 landmines (write_text/read_text
    #    without encoding="utf-8" inside functions that use non-ASCII string
    #    literals). See check_text_io_encoding.py for the heuristic.
    echo "  → Encoding guard (Windows cp1252)..."
    ORCH_REL_FILES=$(git diff --cached --name-only --diff-filter=ACM \
        | grep "^\.dev-aid/orchestration/.*\.py$" \
        | sed 's|^\.dev-aid/orchestration/||' || true)
    if [ -n "$ORCH_REL_FILES" ]; then
        python check_text_io_encoding.py $ORCH_REL_FILES || {
            echo "❌ Encoding guard failed! Add encoding=\"utf-8\" to flagged calls."
            exit 1
        }
    fi

    # 5. Run tests with coverage
    echo "  → Pytest (tests + coverage)..."
    pytest tests/ -v --tb=short || {
        echo "❌ Tests failed!"
        exit 1
    }

    echo "✅ All pre-commit checks passed!"
fi

# Check bash scripts
BASH_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep "\.sh$" || true)

if [ -n "$BASH_FILES" ]; then
    echo "📝 Bash scripts changed, running shellcheck..."
    while IFS= read -r file; do
        if [ -f "$REPO_ROOT/$file" ]; then
            shellcheck "$REPO_ROOT/$file" || {
                echo "❌ Shellcheck failed for $file"
                exit 1
            }
        fi
    done <<< "$BASH_FILES"
    echo "✅ Shellcheck passed!"
fi

# Check GitHub workflow files
WORKFLOW_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep "^\.github/workflows/.*\.ya\?ml$" || true)

if [ -n "$WORKFLOW_FILES" ]; then
    echo "📝 GitHub workflow files changed, validating..."

    VENV_PY="$REPO_ROOT/.dev-aid/orchestration/venv/bin/python"
    if [ ! -x "$VENV_PY" ]; then
        VENV_PY="$REPO_ROOT/.dev-aid/orchestration/.venv/bin/python"
    fi

    if [ -x "$VENV_PY" ]; then
        for wf in $WORKFLOW_FILES; do
            "$VENV_PY" -c "import yaml; yaml.safe_load(open('$REPO_ROOT/$wf'))" || {
                echo "❌ YAML syntax error in $wf"
                exit 1
            }
        done
        echo "✅ Workflow YAML syntax OK"
    fi

    if command -v actionlint >/dev/null 2>&1; then
        for wf in $WORKFLOW_FILES; do
            actionlint "$REPO_ROOT/$wf" || {
                echo "❌ actionlint failed for $wf"
                exit 1
            }
        done
        echo "✅ actionlint passed"
    fi
fi

echo "✅ Pre-commit hook completed successfully!"
HOOK_EOF

# Make hook executable
chmod +x "$GIT_HOOKS_DIR/pre-commit"

echo "✅ Pre-commit hook installed at: $GIT_HOOKS_DIR/pre-commit"
echo ""
echo "The hook will automatically run:"
echo "  • Black formatting check"
echo "  • Flake8 linting"
echo "  • MyPy type checking"
echo "  • Encoding guard (Windows cp1252 landmines)"
echo "  • Pytest with coverage"
echo "  • Shellcheck (for .sh files)"
echo "  • GitHub workflow YAML syntax (+ actionlint if installed)"
echo ""
echo "To bypass the hook (not recommended): git commit --no-verify"
echo ""
echo "To manually run checks: ./.dev-aid/scripts/run-pr-checks.sh"
