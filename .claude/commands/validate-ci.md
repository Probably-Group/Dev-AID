# Validate CI Checks Locally

Run the same checks locally that CI runs on GitHub Actions. This ensures your code will pass CI before you push, saving time and avoiding failed builds.

## What it does:
1. Runs Black (code formatting)
2. Runs isort (import sorting)
3. Runs Flake8 (linting)
4. Runs MyPy (type checking)
5. Runs Pytest (unit tests)
6. Runs Shellcheck (bash scripts)

All checks match the exact configuration used in `.github/workflows/pr-check.yml`.

## Usage:
```bash
.dev-aid/scripts/run-local-ci-checks.sh
```

## Auto-fix formatting issues:
The script will tell you exactly how to fix any issues found. For formatting:
```bash
cd .dev-aid/orchestration
black .
isort .
```

## Setup auto-formatting pre-commit hook:
Install the improved Git hook that auto-fixes formatting on commit:
```bash
.dev-aid/scripts/setup-better-git-hooks.sh
```

Once installed, every `git commit` will automatically:
- Format code with Black
- Sort imports with isort
- Check for linting errors
- Block commits with errors

## Benefits:
✅ Catch issues before pushing
✅ Auto-fix formatting problems
✅ Save CI runner time
✅ Faster feedback loop
✅ Match CI environment exactly
