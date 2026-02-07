# Dev-AID Agent Framework

Provider-agnostic autonomous AI agents powered by Dev-AID's 72+ expert skills.

**Module location:** `.dev-aid/agents/`
**CLI entry point:** `dev-aid-agent`
**Configuration:** `.dev-aid/config/agents.json`

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

# JSON output for scripts/CI
dev-aid-agent tech-debt-hunter --severity critical --json
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI (cli.py)                           │
│  Parses args, resolves provider/model, wires components     │
└──────┬──────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│                   AgentRunner (core/agent_runner.py)         │
│  1. Build system prompt from skills + agent extras          │
│  2. Send messages to LLM via ProviderAdapter                │
│  3. If tool_calls → execute via ToolRegistry → loop         │
│  4. If final text → return AgentResult                      │
│  5. If max_iterations → stop with warning                   │
└──────┬──────────────┬──────────────┬────────────────────────┘
       │              │              │
       ▼              ▼              ▼
┌────────────┐ ┌────────────┐ ┌────────────┐
│ SkillLoader│ │ToolRegistry│ │  Provider  │
│  (SKILL.md │ │ (16 tools, │ │  Adapter   │
│  → system  │ │  safety,   │ │ (Anthropic,│
│  prompts)  │ │  formats)  │ │ OpenAI,    │
└────────────┘ └────────────┘ │ Google,    │
                              │ Local)     │
                              └────────────┘
```

### Agent Loop

1. **Build system prompt** — loads SKILL.md files for the agent's skills and appends `system_prompt_extra`
2. **Send to LLM** — via `ProviderAdapter.send_with_tools()` with tool definitions in the provider's native format
3. **Parse response** — if the LLM returns `tool_calls`, execute each one through the `ToolRegistry`
4. **Append results** — tool results are formatted per-provider and appended to the conversation
5. **Repeat** — loop back to step 2 until the LLM returns a final text response or `max_iterations` is reached

---

## CLI Reference

```
dev-aid-agent <agent-name> [options]
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

### Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Agent completed successfully |
| `1` | Agent failed or unknown agent name |

### JSON Output Format

When using `--json`, the output follows this schema:

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

### Overriding Defaults

CLI flags take precedence over `agents.json`, which takes precedence over hardcoded defaults:

```
CLI flags > agents.json > AgentDefinition defaults
```

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
├── __init__.py                     # Public API surface
├── cli.py                          # CLI entry point (argparse)
├── core/
│   ├── __init__.py
│   ├── models.py                   # AgentDefinition, ToolCall, ToolResult, AgentResult
│   ├── agent_runner.py             # Main agent loop
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
│   └── onboarding_agent.py         # Codebase Onboarding
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
# Run agent tests
cd .dev-aid/orchestration
venv/bin/python -m pytest tests/test_agent_*.py -v

# Run all tests (including agents)
venv/bin/python -m pytest tests/ -v
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

**Coverage:** 112 tests, all passing. No real API calls — everything is mocked.
