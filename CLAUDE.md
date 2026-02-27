- always commit changes, Im not doing it from local working directory
- do NOT create PRs — just commit directly to feature branches. This is a git repo, commits are sufficient
- always use websearch when you want to know which app, library, or env versions are latest stable. never use your internal knowledge which is one year old

## Pre-commit hooks & code quality

The orchestration module (`.dev-aid/orchestration/`) has pre-commit hooks that run on every commit:
- **Black** formatter — always run `black` on changed files before committing
- **Flake8** linter — check for unused imports (F401), undefined names (F821), import order (E402)
- **MyPy** strict — always use parameterized generics (`Dict[str, Any]` not bare `dict`); never remove `type: ignore` comments without testing that MyPy passes without them
- **Pytest** with coverage — minimum 80% coverage threshold

### Common mistakes to avoid
- When changing error messages in shared utility modules, search for and update all test assertions that match on those messages (e.g., `pytest.raises(ValueError, match="...")`)
- When extracting shared modules, verify that all imports in the new module are actually used (Flake8 F401)
- When splitting a module into a package, use `Dict[str, ...]` from `typing` for type annotations (not bare `dict`) to satisfy MyPy strict mode
- Always run the venv test suite before committing: `cd .dev-aid/orchestration && venv/bin/python -m pytest tests/ -v`
- When Task agents create branches, always verify they used the correct branch name before committing

For architecture details, command aliases, and file structures, see CLAUDE-REFERENCE.md