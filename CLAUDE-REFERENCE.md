## Agent Framework (`.dev-aid/agents/`)

Provider-agnostic agent system with 9 built-in agents, multi-agent teams, and CI/CD automation.

### Architecture

```
.dev-aid/agents/
├── core/                    # Framework infrastructure
│   ├── agent_runner.py      # Main execution loop (25 max iterations)
│   ├── skill_loader.py      # Converts SKILL.md → system prompts
│   ├── tool_registry.py     # Tool definitions, provider format export
│   ├── provider_adapter.py  # Protocol for LLM provider adapters
│   ├── team_runner.py       # Multi-agent team orchestration
│   ├── team_models.py       # Team data models (slots, tasks, messages)
│   ├── shared_state.py      # Shared state between team agents
│   ├── lessons.py           # Lessons Ledger (failure pattern tracking)
│   ├── safety.py            # Risk-level tool execution checks
│   ├── cost.py              # Per-model cost tracking
│   └── models.py            # AgentDefinition, AgentResult, ToolCall
├── agents/                  # 9 built-in agents
│   ├── pr_reviewer.py       # PR review (security, quality, architecture)
│   ├── test_generator.py    # Test generation (pytest/jest/vitest)
│   ├── tech_debt_hunter.py  # Tech debt scanning & prioritization
│   ├── ci_fixer.py          # CI/CD failure diagnosis & fix
│   ├── conflict_resolver.py # Merge conflict resolution (smart/ours/theirs)
│   ├── research_agent.py    # Technical research with web + codebase
│   ├── onboarding_agent.py  # Codebase onboarding guide generation
│   ├── doc_auditor.py       # Documentation audit & health scoring
│   └── dod_gate.py          # Definition of Done verification gate
├── adapters/                # LLM provider adapters
│   ├── anthropic_adapter.py # Claude (Anthropic Messages API)
│   ├── google_adapter.py    # Gemini
│   └── openai_adapter.py    # OpenAI + local (Ollama, LM Studio)
├── tools/                   # Agent tools (file, git, github, bash, search)
├── teams/
│   └── builtin_teams.py     # 4 predefined teams (see below)
└── cli.py                   # CLI entry point
```

### Built-in Teams

| Team | Agents | Workflow |
|------|--------|----------|
| `pr-review-team` | security-reviewer, quality-reviewer, test-coverage-reviewer | parallel |
| `security-audit-team` | vulnerability-scanner, auth-reviewer, dependency-auditor | parallel |
| `architect-implement-team` | architect → implementer → reviewer | DAG |
| `issue-resolution-team` | researcher → fixer → test-writer | DAG |

### CI/CD Automation (GitHub Actions)

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `auto-fix-issues.yml` | Issue labeled `auto-fix`/`good-first-issue`/`typo`/`documentation` | Auto-analyze and fix simple issues |
| `auto-resolve-conflicts.yml` | Manual dispatch | Detect and resolve PR merge conflicts |
| `auto-triage-issues.yml` | Issue opened | Auto-label, estimate complexity, suggest auto-fix |
| `pr-check.yml` | Push/PR on main | Black, Flake8, MyPy, Pytest, Shellcheck |
| `release-gate.yml` | Release created | Gitleaks, Trivy, Opengrep SAST, cross-platform tests, SBOM |
| `security.yml` | Tags, weekly, release | Gitleaks, Opengrep (340+ rules), Trivy filesystem scan |

### Deep Research MCP Server (`.dev-aid/deep-research/`)

Multi-provider research with smart routing:
- **Providers**: Tavily (quick/standard), Perplexity Sonar (standard/deep), Gemini Deep Research
- **MCP tools**: `research`, `quick_research`, `deep_research`, `get_providers`, cache management
- **CLI**: `dev-aid-research` command (search, quick, deep, providers, cache)
- **Smart router**: Auto-selects provider based on query complexity

### Agent Tracing & APO

**Trace collection** — Add `--trace` to any agent or team command to record JSONL execution traces:
```bash
dev-aid-agent pr-reviewer --pr 135 --trace
dev-aid-agent team security-audit-team -m "Audit" --trace --trace-dir /custom/path
```
Traces stored at `.dev-aid/agent-traces/{agent-name}/`.

**Automatic Prompt Optimization** — LLM-driven prompt improvement with human approval:
```bash
dev-aid-agent apo optimize <agent> [--beam-width 3] [--dry-run]
dev-aid-agent apo rollback <agent> [--version N]
dev-aid-agent apo history <agent>
dev-aid-agent apo status
```

**Data paths (gitignored, protected by update-lib.sh):**
- `.dev-aid/agent-traces/` — Execution trace JSONL files
- `.dev-aid/agent-prompts/` — APO-optimized prompt versions
- `.dev-aid/config/golden-tests.json` — Golden test cases (committed)
- `.dev-aid/memory-bank/agent-optimization.md` — APO results in memory bank

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
| `aid-apo` | `dev-aid-agent-apo` | `aid-apo optimize pr-reviewer` |
| `aid-lessons` | `dev-aid-agent-lessons` | `aid-lessons list` |
| `aid-dod` | `dev-aid-agent-dod-gate` | `aid-dod` |

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
| `aid-smoke` | `dev-aid-smoke` |
| `aid-lint` | `dev-aid-lint` |
| `aid-typecheck` | `dev-aid-typecheck` |
| `aid-commit` | `dev-aid-commit-plan` |
| `aid-api` | `dev-aid-api-contract` |
| `aid-plan` | `dev-aid-plan` |
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
│   ├── productivity/
│   │   ├── dev-aid-plan.md              # Full command
│   │   └── aid-plan.md                  # Short alias
│   ├── quality/
│   │   ├── dev-aid-smoke.md             # Smoke tests
│   │   ├── dev-aid-lint.md              # Auto-lint
│   │   ├── dev-aid-typecheck.md         # Type checking
│   │   └── aid-*.md                     # Short aliases
│   └── ...
└── gemini/.gemini/commands/
    ├── agents/
    │   ├── dev-aid-agent-pr-review.toml
    │   └── aid-pr.toml
    └── ...
```