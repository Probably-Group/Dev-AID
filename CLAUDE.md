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

## Agent Slash Commands

The agent framework has native slash commands for interactive use (in addition to the `dev-aid-agent` CLI for scripts/CI).

### Invocation

Each agent has a **full name** and a **short alias**:

| Full Command | Short Alias | Usage |
|-------------|------------|-------|
| `/agents:dev-aid-agent-pr-review` | `/agents:aid-pr` | `/agents:aid-pr 135` |
| `/agents:dev-aid-agent-test-gen` | `/agents:aid-test` | `/agents:aid-test src/auth/` |
| `/agents:dev-aid-agent-tech-debt` | `/agents:aid-debt` | `/agents:aid-debt src/ high` |
| `/agents:dev-aid-agent-ci-fix` | `/agents:aid-ci` | `/agents:aid-ci 12345` |
| `/agents:dev-aid-agent-conflict-resolve` | `/agents:aid-conflict` | `/agents:aid-conflict 42 smart` |
| `/agents:dev-aid-agent-research` | `/agents:aid-research` | `/agents:aid-research "async patterns" deep` |
| `/agents:dev-aid-agent-onboard` | `/agents:aid-onboard` | `/agents:aid-onboard` |
| `/agents:dev-aid-agent-doc-audit` | `/agents:aid-docs` | `/agents:aid-docs . docs-only` |
| — | `/agents:aid-help` | Show all commands |

Type `/agents:aid-` to trigger autocomplete and see all short aliases.

### Adding a New Agent Slash Command

When adding a new agent to the framework, also create slash commands:

1. **Claude command** — `.dev-aid/providers/claude/.claude/commands/agents/dev-aid-agent-<name>.md`
   - Uses YAML frontmatter (`name`, `description`, `category`, `author`, `version`)
   - Full instructions with `$ARGUMENTS` for user input
2. **Claude alias** — `.dev-aid/providers/claude/.claude/commands/agents/aid-<short>.md`
   - Thin wrapper (~5 lines) that points to the full command file
3. **Gemini command** — `.dev-aid/providers/gemini/.gemini/commands/agents/dev-aid-agent-<name>.toml`
   - TOML format with `[metadata]` and `[prompt]` sections
4. **Gemini alias** — `.dev-aid/providers/gemini/.gemini/commands/agents/aid-<short>.toml`
   - Thin wrapper that points to the full command file
5. **AGENTS.md.template** — Add a trigger entry in `.dev-aid/templates/AGENTS.md.template`

### File Structure

```
.dev-aid/providers/
├── claude/.claude/commands/agents/
│   ├── dev-aid-agent-pr-review.md       # Full command
│   ├── aid-pr.md                        # Short alias
│   ├── aid-help.md                      # Discovery command
│   └── ...
└── gemini/.gemini/commands/agents/
    ├── dev-aid-agent-pr-review.toml     # Full command
    ├── aid-pr.toml                      # Short alias
    ├── aid-help.toml                    # Discovery command
    └── ...
```