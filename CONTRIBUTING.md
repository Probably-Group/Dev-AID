# Contributing to Dev-AID

Thank you for your interest in contributing to Dev-AID!

## How to Contribute

### Reporting Issues

- Check existing issues first
- Provide clear reproduction steps
- Include your configuration (orchestration mode, providers, etc.)
- Share relevant logs (sanitize any secrets!)

### Suggesting Features

- Explain the use case
- Describe expected behavior
- Consider how it affects existing features

### Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test thoroughly (try `setup-dev-aid.sh` and `reconfigure.sh`)
5. Update documentation if needed
6. Commit with clear messages
7. Submit a pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/Dev-AID
cd Dev-AID

# Initialize Dev-AID in the project
./.dev-aid/scripts/setup-dev-aid.sh

# Test reconfiguration
./.dev-aid/scripts/reconfigure.sh
```

### 🚀 Set Up Development Workflow (Recommended)

**Prevent CI failures by running checks locally:**

```bash
# One-time setup - Install pre-commit hooks
./.dev-aid/scripts/setup-git-hooks.sh

# Hooks now run automatically on every commit:
# ✓ Black formatting   ✓ Flake8 linting
# ✓ MyPy type checking ✓ Pytest + coverage
# ✓ Shellcheck         (for bash scripts)
```

**Manual checks before pushing:**
```bash
# Run all PR checks (same as CI)
./.dev-aid/scripts/run-pr-checks.sh

# Or use Makefile
cd .dev-aid/orchestration
make check      # Run all checks
make format     # Auto-fix formatting issues
make test       # Run tests only
make fix        # Auto-fix everything possible
```

**Why use these tools?**
- ✅ Catch issues in seconds (not minutes waiting for CI)
- ✅ Fast feedback loop while you have full context
- ✅ Prevent wasted CI minutes and broken PRs
- ✅ Better developer experience

📖 **Full guide:** [Development Workflow](.dev-aid/docs/DEVELOPMENT-WORKFLOW.md)

## Code Style

### Python Code (Router/Orchestration)

- **Formatter:** Black (100 char line length)
- **Linter:** Flake8 with `--max-line-length=120 --extend-ignore=E203,W503`
- **Type checking:** MyPy with strict mode
- **Testing:** Pytest with 59%+ coverage required

**Quick fixes:**
```bash
cd .dev-aid/orchestration
make format     # Auto-fix formatting
make lint       # Check linting
```

### Shell Scripts

- Follow existing style, use shellcheck
- Executable scripts should have `#!/bin/bash` shebang
- Use `set -e` for error handling
- Document complex functions

### Documentation

- Clear, concise, with examples
- Update README.md for user-facing changes
- Add inline comments for complex logic only

## Testing Checklist

Before submitting a PR:

- [ ] Pre-commit hooks installed (`./.dev-aid/scripts/setup-git-hooks.sh`)
- [ ] All local checks pass (`make check` or `./run-pr-checks.sh`)
- [ ] Setup script works from scratch
- [ ] All orchestration modes work
- [ ] Reconfiguration preserves memory bank
- [ ] Documentation is updated
- [ ] No secrets in commits
- [ ] Python code: Black formatted, Flake8 clean, MyPy passes, tests pass
- [ ] Bash scripts: Shellcheck clean

## Questions?

Open an issue for discussion before major changes.
