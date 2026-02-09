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

## Slash Command Aliases (`aid-*`)

**Every Dev-AID command has a short `aid-*` alias.** Type `aid-` in autocomplete to browse all commands.

### Agent Aliases

| Short Alias | Full Command | Usage |
|------------|-------------|-------|
| `aid-pr` | `dev-aid-agent-pr-review` | `aid-pr 135` |
| `aid-test` | `dev-aid-agent-test-gen` | `aid-test src/auth/` |
| `aid-debt` | `dev-aid-agent-tech-debt` | `aid-debt src/ high` |
| `aid-ci` | `dev-aid-agent-ci-fix` | `aid-ci 12345` |
| `aid-conflict` | `dev-aid-agent-conflict-resolve` | `aid-conflict 42 smart` |
| `aid-research` | `dev-aid-agent-research` | `aid-research "async patterns" deep` |
| `aid-onboard` | `dev-aid-agent-onboard` | `aid-onboard` |
| `aid-docs` | `dev-aid-agent-doc-audit` | `aid-docs . docs-only` |
| `aid-team` | `dev-aid-agent-team` | `aid-team security-audit-team -m "Audit auth"` |

### Router Aliases

| Short Alias | Full Command |
|------------|-------------|
| `aid-challenger` | `dev-aid-router-challenger` |
| `aid-challenger-rag` | `dev-aid-router-challenger-rag` |
| `aid-ensemble` | `dev-aid-router-ensemble` |
| `aid-router-status` | `dev-aid-router-status` |

### Other Aliases

| Short Alias | Full Command |
|------------|-------------|
| `aid-audit` | `dev-aid-audit` |
| `aid-vulnscan` | `dev-aid-vulnerability-scan` |
| `aid-health` | `dev-aid-code-health` |
| `aid-debt-report` | `dev-aid-debt-analysis` |
| `aid-review` | `dev-aid-review-staged` |
| `aid-commit` | `dev-aid-commit-plan` |
| `aid-api` | `dev-aid-api-contract` |
| `aid-analyze` | `dev-aid-analyze` |
| `aid-status` | `dev-aid-status` |
| `aid-config` | `dev-aid-config-core-skills` |
| `aid-skill` | `dev-aid-build-skill` |
| `aid-deploy` | `dev-aid-deploy-validate` |
| `aid-models` | `dev-aid-models-update` |
| `aid-help` | Show all commands |

### Adding a New Command

When adding any new slash command, always create both the full command and an `aid-*` alias:

1. **Claude command** — `.dev-aid/providers/claude/.claude/commands/<category>/dev-aid-<name>.md`
   - Uses YAML frontmatter (`name`, `description`, `category`, `author`, `version`)
   - Full instructions with `$ARGUMENTS` for user input
2. **Claude alias** — `.dev-aid/providers/claude/.claude/commands/<category>/aid-<short>.md`
   - Thin wrapper (~5 lines) that points to the full command file
3. **Gemini command** — `.dev-aid/providers/gemini/.gemini/commands/<category>/dev-aid-<name>.toml`
   - TOML format with `[metadata]` and `[prompt]` sections
4. **Gemini alias** — `.dev-aid/providers/gemini/.gemini/commands/<category>/aid-<short>.toml`
   - Thin wrapper that points to the full command file
5. **Update `aid-help`** — Add the new alias to both `aid-help.md` and `aid-help.toml`
6. **For agents only** — Also add a trigger entry in `.dev-aid/templates/AGENTS.md.template`

### File Structure

```
.dev-aid/providers/
├── claude/.claude/commands/
│   ├── agents/
│   │   ├── dev-aid-agent-pr-review.md   # Full command
│   │   ├── aid-pr.md                    # Short alias
│   │   └── aid-help.md                  # Discovery command
│   ├── router/
│   │   ├── dev-aid-router-challenger.md # Full command
│   │   └── aid-challenger.md            # Short alias
│   ├── security/
│   │   ├── dev-aid-audit.md             # Full command
│   │   └── aid-audit.md                 # Short alias
│   └── ...
└── gemini/.gemini/commands/
    ├── agents/
    │   ├── dev-aid-agent-pr-review.toml
    │   └── aid-pr.toml
    └── ...
```