# Dev-AID Agent Framework

Provider-agnostic autonomous AI agents powered by Dev-AID's 72+ expert skills.

**Module location:** `.dev-aid/agents/`
**CLI entry point:** `dev-aid-agent`
**Configuration:** `.dev-aid/config/agents.json`, `.dev-aid/config/teams.json`

---

## Quick Start

```bash
# Review a PR
dev-aid-agent pr-reviewer --pr 135

# Generate tests
dev-aid-agent test-generator --path src/auth/

# Scan for tech debt
dev-aid-agent tech-debt-hunter --severity high --dry-run

# Research a topic with a specific provider
dev-aid-agent research --topic "async patterns in Python" --provider google

# Audit documentation health
dev-aid-agent doc-auditor --scope full

# JSON output for scripts/CI
dev-aid-agent tech-debt-hunter --severity critical --json

# Run a multi-agent team
dev-aid-agent team pr-review-team -m "Review PR #42"

# List available teams
dev-aid-agent team --list-teams
```

---

## Native Slash Commands

Each agent is available as a **native slash command** for interactive use alongside the CLI. Slash commands load directly in the AI session — no separate process.

### Command Mapping

| CLI Command | Slash Command (Full) | Slash Command (Short Alias) |
|-------------|---------------------|----------------------------|
| `dev-aid-agent pr-reviewer --pr 135` | `/dev-aid-agent-pr-review 135` | `/aid-pr 135` |
| `dev-aid-agent test-generator --path src/` | `/dev-aid-agent-test-gen src/` | `/aid-test src/` |
| `dev-aid-agent tech-debt-hunter --severity high` | `/dev-aid-agent-tech-debt src/ high` | `/aid-debt src/ high` |
| `dev-aid-agent ci-fixer --run-id 12345` | `/dev-aid-agent-ci-fix 12345` | `/aid-ci 12345` |
| `dev-aid-agent conflict-resolver --pr 42` | `/dev-aid-agent-conflict-resolve 42 smart` | `/aid-conflict 42 smart` |
| `dev-aid-agent research --topic "async"` | `/dev-aid-agent-research "async" deep` | `/aid-research "async" deep` |
| `dev-aid-agent onboarding` | `/dev-aid-agent-onboard` | `/aid-onboard` |
| `dev-aid-agent doc-auditor --scope full` | `/dev-aid-agent-doc-audit . full` | `/aid-docs . full` |
| — | — | `/aid-help` |

### When to Use CLI vs Slash Commands

| Use Case | Recommended | Why |
|----------|-------------|-----|
| Interactive coding session | Slash commands (`/aid-pr 135`) | Loads in-session, uses your AI's full context |
| CI/CD pipelines | CLI (`dev-aid-agent pr-reviewer --pr 135 --json`) | Structured output, exit codes, `--dry-run` |
| Scripts and automation | CLI | Supports `--provider`, `--json`, `--verbose` flags |
| Quick one-off tasks | Short aliases (`/aid-test src/`) | Fastest to type, autocomplete with `aid-` |

### Supported Editors/Tools

**Native slash commands** (auto-discovered from `.claude/commands/` and `.gemini/commands/`):
- Claude Code (terminal CLI + VS Code extension)
- Gemini CLI (terminal + VS Code/JetBrains via Gemini Code Assist)
- Codex CLI (via AGENTS.md.template triggers)
- Cursor (reads `.claude/commands/` natively)
- Windsurf (reads `.claude/commands/` natively)
- Cline (VS Code extension, reads `.claude/commands/`)

**MCP integration only** (skills + local search, but no custom slash commands):
- VS Code Copilot Chat, Zed, JetBrains AI Assistant

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI (cli.py)                           │
│  Parses args, resolves provider/model, wires components     │
│  Routes to AgentRunner (single) or TeamRunner (multi)       │
└──────┬─────────────────────────────────┬────────────────────┘
       │ single agent                    │ team
       ▼                                 ▼
┌──────────────────────┐  ┌────────────────────────────────────┐
│ AgentRunner          │  │ TeamRunner (core/team_runner.py)    │
│ (core/agent_runner.py│  │  Wraps N AgentRunner instances      │
│  Single agent loop)  │  │  Parallel / Sequential / DAG        │
└──────┬───────┬───────┘  │  Shared state + budget tracking     │
       │       │          └──────┬──────┬──────┬───────────────┘
       │       │                 │      │      │
       ▼       ▼                 ▼      ▼      ▼
┌────────┐ ┌────────┐    ┌────────┐ ┌────────┐ ┌────────┐
│ Skill  │ │  Tool  │    │Shared  │ │Message │ │Budget  │
│ Loader │ │Registry│    │TaskList│ │  Bus   │ │Tracker │
└────────┘ └────────┘    └────────┘ └────────┘ └────────┘
```

### Agent Loop

1. **Build system prompt** — loads SKILL.md files for the agent's skills and appends `system_prompt_extra`
2. **Send to LLM** — via `ProviderAdapter.send_with_tools()` with tool definitions in the provider's native format
3. **Parse response** — if the LLM returns `tool_calls`, execute each one through the `ToolRegistry`
4. **Append results** — tool results are formatted per-provider and appended to the conversation
5. **Repeat** — loop back to step 2 until the LLM returns a final text response or `max_iterations` is reached

### Team Orchestration

The `TeamRunner` wraps multiple `AgentRunner` instances to execute teams of agents with three workflow strategies:

- **Parallel** — all agents run simultaneously via `asyncio.gather()`. Each gets independent tools, safety, and provider. GIL is released during I/O-bound LLM calls for true parallelism.
- **Sequential** — agents run one after another. Each agent's result is broadcast via `MessageBus` as a handoff message. Subsequent agents receive prior results in their context.
- **DAG** — agents run in topological order respecting `depends_on` declarations. Ready agents (all deps completed) run in parallel batches. Deadlock detection stops remaining agents if dependencies cannot be resolved.

Each agent in a team gets its own `AgentRunner`, `ToolRegistry`, and `ProviderAdapter`, enabling provider mixing within a single team (e.g., architect on Claude Opus, implementer on Gemini).

---

## CLI Reference

```
dev-aid-agent <agent-name> [options]
dev-aid-agent team <team-name> -m <message> [options]
```

### Global Options

| Flag | Description |
|------|-------------|
| `--provider <name>` | Override provider: `anthropic`, `google`, `openai`, `local` |
| `--model <name>` | Override model (e.g., `gemini-2.0-flash`, `gpt-4o`) |
| `--dry-run` | Show planned actions without making changes |
| `--verbose` | Show individual tool call details |
| `--json` | JSON output (for scripts and CI pipelines) |
| `--max-iterations <n>` | Override maximum agent loop iterations |

### Agent Subcommands

#### `pr-reviewer`
Review a pull request for security, quality, and best practices.

```bash
dev-aid-agent pr-reviewer --pr <number>
```

#### `test-generator`
Generate tests for untested code.

```bash
dev-aid-agent test-generator --path <file-or-dir> [--framework pytest|jest|vitest]
```

#### `tech-debt-hunter`
Scan codebase for code smells and technical debt.

```bash
dev-aid-agent tech-debt-hunter [--severity low|medium|high|critical] [--path <dir>]
```

#### `ci-fixer`
Diagnose CI failures and propose fixes.

```bash
dev-aid-agent ci-fixer [--run-id <id>] [--pr <number>]
```

#### `conflict-resolver`
Resolve merge conflicts intelligently.

```bash
dev-aid-agent conflict-resolver [--pr <number>] [--strategy smart|ours|theirs]
```

#### `research`
Deep research on a technical topic.

```bash
dev-aid-agent research --topic <text> [--depth quick|standard|deep]
```

#### `onboarding`
Generate a comprehensive codebase onboarding guide.

```bash
dev-aid-agent onboarding [--path <project-root>]
```

#### `doc-auditor`
Audit documentation for drift, broken links, missing docs, and naming violations.

```bash
dev-aid-agent doc-auditor [--scope full|docs-only|code-only] [--path <project-root>]
```

#### `team`
Run a multi-agent team. See [Team CLI Reference](#team-cli-reference) below.

```bash
dev-aid-agent team <team-name> -m <message> [--budget <usd>] [--workflow <strategy>]
```

### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Agent or team completed successfully |
| `1` | Agent/team failed or unknown name |

### JSON Output Format

When using `--json` with a single agent:

```json
{
  "agent": "pr-reviewer",
  "success": true,
  "output": "## PR Review\n...",
  "metrics": {
    "tool_calls": 8,
    "iterations": 5,
    "tokens": {"input": 12500, "output": 3200},
    "cost": 0.042,
    "latency_ms": 15200.3
  }
}
```

When using `--json` with a team:

```json
{
  "team": "pr-review-team",
  "success": true,
  "partial": false,
  "output": "### From security-reviewer\n...",
  "agents": {
    "security-reviewer": {
      "success": true,
      "output": "## Security Review\n...",
      "tool_calls": 5,
      "iterations": 3,
      "cost": 0.018,
      "latency_ms": 8200.1
    },
    "quality-reviewer": { "..." : "..." },
    "test-coverage-reviewer": { "..." : "..." }
  },
  "metrics": {
    "agents_completed": 3,
    "agents_failed": 0,
    "tokens": {"input": 38000, "output": 9600},
    "cost_usd": 0.047,
    "latency_ms": 12300.5,
    "messages_exchanged": 0
  }
}
```

The `partial` flag is `true` when some agents failed but the team still produced output from the remaining agents.

---

## Built-in Agents

| Agent | Skills | Tools | Risk | Use Case |
|-------|--------|-------|------|----------|
| **pr-reviewer** | appsec-expert, senior-architect, devsecops-expert | read_file, git_diff, git_log, gh_pr_view, grep_search, glob_files | safe | Review PRs for security, quality, best practices |
| **test-generator** | python | read_file, write_file, glob_files, grep_search, run_bash | moderate | Generate tests for untested code |
| **tech-debt-hunter** | senior-architect, refactoring-expert | read_file, glob_files, grep_search, git_log | safe | Scan for code smells, create issue reports |
| **ci-fixer** | cicd-expert, bash-expert | read_file, write_file, run_bash, git_diff, gh_pr_view, grep_search, glob_files | moderate | Diagnose CI failures, propose fixes |
| **conflict-resolver** | senior-architect | read_file, write_file, run_bash, git_status, git_diff, grep_search | moderate | Auto-resolve merge conflicts |
| **research** | deep-research-expert, web-research-expert | read_file, glob_files, grep_search | safe | Deep research on technical topics |
| **onboarding** | senior-architect | read_file, glob_files, grep_search, git_log, list_directory | safe | Generate codebase onboarding guide |
| **doc-auditor** | senior-architect | read_file, glob_files, grep_search, list_directory, find_files, git_log | safe | Audit docs for drift, broken links, gaps |

---

## Built-in Teams

Teams compose multiple agents from the registry above, each with a specialized `role_prompt` for differentiated perspectives. Each agent slot references a base agent via `agent_def_name` and can override provider/model.

| Team | Workflow | Agents | Budget | Use Case |
|------|----------|--------|--------|----------|
| **pr-review-team** | parallel | security-reviewer, quality-reviewer, test-coverage-reviewer | $2.00 | Comprehensive PR review from 3 perspectives |
| **security-audit-team** | parallel | vulnerability-scanner, auth-reviewer, dependency-auditor | $3.00 | Deep security audit with specialist angles |
| **architect-implement-team** | dag | architect → implementer → reviewer | $5.00 | Plan with senior architect, implement, review |
| **issue-resolution-team** | dag | researcher → fixer → test-writer | $4.00 | Investigate issue, fix it, add regression tests |

### Team Details

#### `pr-review-team`

Three parallel reviewers each examine the same PR from a different angle. Results are merged with `merge_sections` aggregation.

| Agent Slot | Base Agent | Focus |
|------------|------------|-------|
| security-reviewer | pr-reviewer | Authentication, injection, OWASP Top 10 |
| quality-reviewer | pr-reviewer | Readability, design patterns, performance |
| test-coverage-reviewer | pr-reviewer | Missing tests, edge cases, assertion quality |

#### `security-audit-team`

Three parallel security specialists scan the codebase from different attack surfaces. Results are merged.

| Agent Slot | Base Agent | Focus |
|------------|------------|-------|
| vulnerability-scanner | pr-reviewer | Injection, XSS, CSRF, SSRF, path traversal |
| auth-reviewer | pr-reviewer | Authentication, authorization, session management |
| dependency-auditor | tech-debt-hunter | CVEs, outdated packages, supply chain risks |

#### `architect-implement-team`

A DAG workflow: architect plans first (using Claude Opus), implementer follows the plan, reviewer validates the result.

| Agent Slot | Base Agent | Depends On | Provider Override |
|------------|------------|------------|-------------------|
| architect | research | (none) | anthropic / claude-opus-4-6 |
| implementer | test-generator | architect | (team default) |
| reviewer | pr-reviewer | implementer | (team default) |

#### `issue-resolution-team`

A DAG workflow: researcher investigates the root cause, fixer applies a minimal fix, test-writer adds regression tests.

| Agent Slot | Base Agent | Depends On |
|------------|------------|------------|
| researcher | research | (none) |
| fixer | ci-fixer | researcher |
| test-writer | test-generator | fixer |

---

## Team CLI Reference

```
dev-aid-agent team <team-name> -m <message> [options]
dev-aid-agent team --list-teams
```

### Team Options

| Flag | Description |
|------|-------------|
| `<team-name>` | Name of the team to run (see `--list-teams`) |
| `-m, --message <text>` | Task message for the team (required) |
| `--budget <usd>` | Override maximum budget in USD |
| `--workflow <strategy>` | Override workflow: `parallel`, `sequential`, `dag` |
| `--list-teams` | List all available teams with descriptions |

### Examples

```bash
# Comprehensive PR review from 3 perspectives
dev-aid-agent team pr-review-team -m "Review PR #42"

# Security audit with custom budget
dev-aid-agent team security-audit-team -m "Audit the auth module" --budget 5.0

# Architect-implement with JSON output
dev-aid-agent team architect-implement-team -m "Add rate limiting to the API" --json

# Override workflow (run DAG team sequentially instead)
dev-aid-agent team issue-resolution-team -m "Fix login timeout bug" --workflow sequential

# List all teams
dev-aid-agent team --list-teams

# Verbose mode shows inter-agent messages
dev-aid-agent team pr-review-team -m "Review PR #42" --verbose
```

### Team Output

```
============================================================
  Dev-AID Team: pr-review-team
  Agents: security-reviewer, quality-reviewer, test-coverage-reviewer
  Workflow: parallel | Budget: $2.00
============================================================

  Starting agent: security-reviewer
  Starting agent: quality-reviewer
  Starting agent: test-coverage-reviewer
  Agent security-reviewer: done, $0.018
  Agent quality-reviewer: done, $0.015
  Agent test-coverage-reviewer: done, $0.014

### From security-reviewer

[Security review output...]

### From quality-reviewer

[Quality review output...]

### From test-coverage-reviewer

[Test coverage review output...]

--- 3/3 agents completed, 12.3s, $0.0470 ---
```

### Graceful Degradation

If an agent fails within a team, the team continues with the remaining agents. The result is marked as `partial: true` and includes outputs from successful agents. Budget exhaustion also causes remaining agents to be skipped gracefully.

---

## Shared State Primitives

The team orchestration layer provides four thread-safe primitives (all use `threading.Lock`) for coordinating concurrent agent execution:

| Primitive | Purpose |
|-----------|---------|
| `SharedTaskList` | Task tracking with dependency resolution. Tasks auto-unblock when dependencies complete. |
| `MessageBus` | Inter-agent messaging with pub/sub. Supports targeted and broadcast (`to_agent="*"`) messages. |
| `FileLockSet` | Advisory file locks to prevent write conflicts between concurrent agents. Re-entrant for the same agent. |
| `BudgetTracker` | Per-agent cost tracking with team-level budget enforcement. Returns `float('inf')` for unlimited budgets. |

### Aggregation Strategies

When a team completes, individual agent results are combined using one of three strategies:

| Strategy | Description | Used By |
|----------|-------------|---------|
| `concatenate` | Each agent's output as a section with `---` separators | architect-implement-team, issue-resolution-team |
| `merge_sections` | Outputs merged with `### From <agent>` headers, failed agents omitted | pr-review-team, security-audit-team |
| `vote` | All perspectives with pass/fail tally header | (available for custom teams) |

---

## Built-in Tools (16)

### File Tools

| Tool | Risk | Description |
|------|------|-------------|
| `read_file` | safe | Read file contents with optional offset/limit |
| `write_file` | moderate | Write or create a file (creates parent directories) |
| `list_directory` | safe | List directory contents (hides dotfiles) |
| `glob_files` | safe | Match files by glob pattern (caps at 500 results) |

### Search Tools

| Tool | Risk | Description |
|------|------|-------------|
| `grep_search` | safe | Search file contents by regex (uses rg or grep) |
| `find_files` | safe | Find files by name pattern (skips hidden dirs, node_modules, __pycache__) |

### Git Tools

| Tool | Risk | Description |
|------|------|-------------|
| `git_status` | safe | Show working tree status |
| `git_diff` | safe | Show diffs (staged, unstaged, or between refs) |
| `git_log` | safe | Show recent commits |
| `git_add` | moderate | Stage files for commit |
| `git_commit` | moderate | Create a git commit |

### GitHub Tools

| Tool | Risk | Description |
|------|------|-------------|
| `gh_issue_view` | safe | View GitHub issue details via `gh` CLI |
| `gh_pr_view` | safe | View PR details via `gh` CLI |
| `gh_pr_create` | moderate | Create a pull request via `gh` CLI |

### System Tools

| Tool | Risk | Description |
|------|------|-------------|
| `run_bash` | dangerous | Execute bash command (max 120s timeout, output truncation at 50KB) |

---

## Safety System

The agent framework enforces safety at multiple levels via `SafetyConfig`:

### Risk Levels

Each tool has a risk level: **safe**, **moderate**, or **dangerous**.

| Level | Description | Examples |
|-------|-------------|---------|
| **safe** | Read-only, no side effects | read_file, git_status, grep_search |
| **moderate** | Writes files or creates commits | write_file, git_add, git_commit |
| **dangerous** | Arbitrary command execution | run_bash |

### Command Blocklist

The `run_bash` tool blocks dangerous commands including:

- Destructive commands: `rm -rf /`, `mkfs`, `dd if=`, `:(){ :|:& };:`
- System modification: `chmod -R 777`, `shutdown`, `reboot`, `init 0`
- Network attacks: `nmap`, `nc -l`
- Crypto mining: `cryptominer`, `xmrig`

Both exact string matching and regex pattern matching are used.

### Dry-Run Mode

When `--dry-run` is passed, all **moderate** and **dangerous** tools are blocked. The agent can still read files and search, but cannot make changes.

### Allowed Tools

Each agent definition specifies which tools it can use. The `SafetyConfig` enforces this — if an agent tries to use a tool not in its allowed list, the call is blocked with an error.

### Team Safety

Each agent in a team gets its own `SafetyConfig` and `ToolRegistry`. The `FileLockSet` provides advisory write locks — when multiple agents run in parallel, only one can hold a write lock on a given file path at a time. Locks are automatically released when an agent completes.

---

## Provider Adapters

The framework supports 4 providers through a unified `ProviderAdapter` protocol:

| Provider | Adapter | Tool Format | Notes |
|----------|---------|-------------|-------|
| **Anthropic** | `AnthropicAdapter` | Messages API `tools=[]` | Optional Claude Agent SDK bridge via lazy import |
| **OpenAI** | `OpenAIAdapter` | Chat Completions `tools=[]` | Also used for Ollama and LM Studio |
| **Google** | `GoogleAdapter` | `FunctionDeclaration` | Gemini function calling |
| **Local** | `OpenAIAdapter` | Same as OpenAI | Uses `base_url` override (e.g., `http://localhost:11434/v1`) |

### Authentication

API keys are resolved from environment variables:

| Provider | Environment Variable |
|----------|---------------------|
| Anthropic | `ANTHROPIC_API_KEY` |
| OpenAI | `OPENAI_API_KEY` |
| Google | `GOOGLE_API_KEY` |
| Local | (none required) |

### Provider Mixing in Teams

Each agent slot in a team can specify its own `provider` and `model` overrides. The `TeamRunner` creates a separate `ProviderAdapter` per agent, enabling provider mixing within a single team execution. For example, `architect-implement-team` uses Claude Opus for the architect and the team default (Sonnet) for the implementer and reviewer.

---

## Configuration

### agents.json

File: `.dev-aid/config/agents.json`

```json
{
  "defaults": {
    "provider": "anthropic",
    "model": "claude-sonnet-4-5-20250929",
    "max_tokens": 4096,
    "temperature": 0.3,
    "max_iterations": 25
  },
  "agents": {
    "pr-reviewer": {
      "description": "Review PRs for security, quality, and best practices",
      "model": "claude-sonnet-4-5-20250929",
      "max_iterations": 15,
      "risk_level": "safe"
    }
  }
}
```

### teams.json

File: `.dev-aid/config/teams.json`

Configures team defaults and per-team/per-agent overrides for provider, model, and budget.

```json
{
  "defaults": {
    "provider": "anthropic",
    "model": "claude-sonnet-4-5-20250929",
    "max_budget_usd": 5.0,
    "timeout_seconds": 600
  },
  "teams": {
    "pr-review-team": {
      "enabled": true,
      "max_budget_usd": 2.0,
      "agents": {
        "security-reviewer": {
          "provider": "anthropic"
        },
        "quality-reviewer": {
          "provider": "anthropic"
        },
        "test-coverage-reviewer": {
          "provider": "anthropic"
        }
      }
    },
    "architect-implement-team": {
      "enabled": true,
      "max_budget_usd": 5.0,
      "agents": {
        "architect": {
          "provider": "anthropic",
          "model": "claude-opus-4-6"
        }
      }
    }
  }
}
```

### Override Precedence

For single agents:

```
CLI flags > agents.json > AgentDefinition defaults
```

For teams:

```
CLI flags (--budget, --workflow) > teams.json > TeamDefinition defaults
```

Per-agent-slot overrides within `teams.json` are applied to provider and model settings.

### Using a Local Model

```bash
# Use Ollama with Qwen
dev-aid-agent tech-debt-hunter --provider local --model qwen2.5-coder:32b --severity high
```

The local provider uses the OpenAI-compatible API at `http://localhost:11434/v1` (Ollama's default).

---

## Skill Loader

The `SkillLoader` parses SKILL.md files from `.dev-aid/skills/` and injects them as system prompts for agents. Each agent specifies which skills to load in its `skills` field.

### How Skills Become System Prompts

1. Agent definition specifies `skills: ["appsec-expert", "senior-architect"]`
2. SkillLoader finds `.dev-aid/skills/expert/appsec-expert/SKILL.md` and `.dev-aid/skills/expert/senior-architect/SKILL.md`
3. YAML frontmatter is parsed for metadata (name, version, description)
4. Markdown body is extracted as the system prompt text
5. Multiple skills are concatenated with `---` separators

### SKILL.md Format

```markdown
---
name: appsec-expert
version: 2.0.0
description: "Application security expert"
risk_level: MEDIUM
category: expert
tools: [Read, Grep]
---

# Application Security Expert

Your security review instructions here...
```

---

## Module Structure

```
.dev-aid/agents/
├── __init__.py                     # Public API (agents + teams exports)
├── cli.py                          # CLI entry point (single agent + team subcommands)
├── core/
│   ├── __init__.py
│   ├── models.py                   # AgentDefinition, ToolCall, ToolResult, AgentResult
│   ├── agent_runner.py             # Single agent execution loop
│   ├── team_models.py              # TeamDefinition, AgentSlot, TeamResult, TeamTask, AgentMessage
│   ├── team_runner.py              # Multi-agent orchestration (parallel/sequential/DAG)
│   ├── shared_state.py             # SharedTaskList, MessageBus, FileLockSet, BudgetTracker
│   ├── tool_registry.py            # Tool registration, execution, format export
│   ├── skill_loader.py             # SKILL.md parsing and prompt building
│   ├── provider_adapter.py         # ProviderAdapter protocol + create_adapter()
│   └── safety.py                   # SafetyConfig, blocklist, dry-run
├── adapters/
│   ├── __init__.py
│   ├── anthropic_adapter.py        # Anthropic Messages API
│   ├── openai_adapter.py           # OpenAI + local models
│   └── google_adapter.py           # Gemini function calling
├── agents/
│   ├── __init__.py
│   ├── pr_reviewer.py              # PR Reviewer agent definition
│   ├── test_generator.py           # Test Generator
│   ├── tech_debt_hunter.py         # Tech Debt Scanner
│   ├── ci_fixer.py                 # CI/CD Fixer
│   ├── conflict_resolver.py        # Merge Conflict Resolver
│   ├── research_agent.py           # Deep Research
│   ├── onboarding_agent.py         # Codebase Onboarding
│   └── doc_auditor.py              # Documentation Auditor
├── teams/
│   ├── __init__.py                 # Team package exports
│   └── builtin_teams.py            # 4 pre-built team definitions
└── tools/
    ├── __init__.py
    ├── file_tools.py               # read_file, write_file, list_directory, glob_files
    ├── bash_tool.py                # run_bash with timeout/blocklist
    ├── git_tools.py                # git_status, git_diff, git_log, git_add, git_commit
    ├── github_tools.py             # gh_issue_view, gh_pr_view, gh_pr_create
    └── search_tools.py             # grep_search, find_files
```

---

## Testing

Tests are in `.dev-aid/orchestration/tests/` and integrate with the existing pre-commit hooks:

```bash
# Run all tests
cd .dev-aid/orchestration
venv/bin/python -m pytest tests/ -v

# Run agent tests only
venv/bin/python -m pytest tests/test_agent_*.py -v

# Run team tests only
venv/bin/python -m pytest tests/test_team_*.py tests/test_builtin_teams.py -v
```

### Test Files

| File | What It Tests |
|------|---------------|
| `test_agent_models.py` | Data model validation, defaults, edge cases |
| `test_agent_safety.py` | Command blocklist, dry-run, path restrictions |
| `test_agent_skill_loader.py` | SKILL.md parsing, multi-skill prompt building, caching |
| `test_agent_tool_registry.py` | Registration, execution, safety enforcement, format export |
| `test_agent_builtin_tools.py` | File, search tools against temp directories |
| `test_agent_runner.py` | Agent loop with mocked LLM (no real API calls) |
| `test_agent_provider_adapters.py` | Format conversion for all 3 providers |
| `test_team_models.py` | TeamDefinition validation, TeamTask state, AgentMessage uniqueness |
| `test_shared_state.py` | Thread safety for SharedTaskList, MessageBus, FileLockSet, BudgetTracker |
| `test_team_runner.py` | Parallel/sequential/DAG execution, budget enforcement, aggregation |
| `test_builtin_teams.py` | Built-in team loading, agent references, DAG cycle detection |
| `test_doc_auditor.py` | Doc-auditor definition validation, CLI integration, scope handling |

**Coverage:** 903 tests, all passing. No real API calls — everything is mocked.
