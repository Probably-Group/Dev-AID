# Makefile for Dev-AID Router Development
# Quick commands for common development tasks

.PHONY: help install test lint format check all clean

# Default target
help:
	@echo "Dev-AID Router - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install        Install dependencies in venv"
	@echo "  make setup-hooks    Setup git pre-commit hooks"
	@echo ""
	@echo "Development:"
	@echo "  make format         Auto-fix formatting (Black, isort)"
	@echo "  make lint           Run linting checks (Flake8, MyPy)"
	@echo "  make test           Run tests with coverage"
	@echo "  make check          Run ALL checks (format + lint + test)"
	@echo ""
	@echo "Shortcuts:"
	@echo "  make all            Same as 'make check'"
	@echo "  make fix            Auto-fix everything possible"
	@echo "  make clean          Remove generated files"

# Install dependencies
install:
	@echo "📦 Installing dependencies..."
	./setup-venv.sh

# Setup git hooks
setup-hooks:
	@echo "🪝 Setting up git hooks..."
	../../scripts/setup-git-hooks.sh

# Auto-fix formatting
format:
	@echo "🎨 Formatting code..."
	black .
	isort .
	@echo "✅ Formatting complete"

# Run linting checks (no auto-fix)
lint:
	@echo "🔍 Running linting checks..."
	@echo "  → Black (check only)..."
	@black --check --diff .
	@echo "  → Flake8..."
	@flake8 . --max-line-length=120 --extend-ignore=E203,W503
	@echo "  → MyPy..."
	@mypy router --ignore-missing-imports --no-strict-optional
	@echo "✅ Linting complete"

# Run tests
test:
	@echo "🧪 Running tests..."
	pytest tests/ -v
	@echo "✅ Tests complete"

# Run tests with coverage
test-cov:
	@echo "🧪 Running tests with coverage..."
	pytest tests/ -v --cov=router --cov-report=term-missing
	@echo "✅ Tests complete"

# Run ALL checks (what CI runs)
check:
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "🔍 Running ALL PR Checks"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@make lint
	@make test-cov
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "✅ All checks passed! Safe to push."
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Alias
all: check

# Auto-fix everything possible
fix:
	@echo "🔧 Auto-fixing issues..."
	@make format
	@echo "✅ Auto-fix complete. Run 'make check' to verify."

# Clean generated files
clean:
	@echo "🧹 Cleaning generated files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "coverage.xml" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Clean complete"
