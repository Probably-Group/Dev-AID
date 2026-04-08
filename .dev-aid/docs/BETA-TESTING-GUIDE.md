# Beta Testing Guide — Dev-AID v1.5.1

**Status**: Active Beta
**Last Updated**: 2026-04-08
**Issue Template**: [Beta Feedback](../../.github/ISSUE_TEMPLATE/beta_feedback.yml)

---

## 1. Quick Start for Testers

### Prerequisites

| Requirement | Minimum | Check Command |
|-------------|---------|---------------|
| Python | 3.11+ | `python3 --version` |
| Git | 2.30+ | `git --version` |
| Bash | 4.0+ | `bash --version` |
| AI CLI | At least one | See below |

**Supported AI CLIs** (at least one required):

- **Claude Code** — `claude --version`
- **Gemini CLI** — `gemini --version`
- **Codex CLI** — `codex --version`
- **Cursor** — Cursor IDE with Dev-AID project open
- **Windsurf** — Windsurf IDE with Dev-AID project open
- **Cline** — VS Code with Cline extension

**Optional**:

- Docker (for security scanners: Gitleaks, Trivy, Opengrep)
- Ollama (for local LLM testing)
- API keys for router testing (Anthropic, Google, OpenAI)

### Setup Steps

The canonical install path is via the `gh dev-aid` extension. Use this on
the project you actually want to test Dev-AID against — Dev-AID is installed
*into* your project, not run from a clone of the Dev-AID repo.

```bash
# 1. Install the gh extension (one-time)
gh extension install Probably-Group/gh-dev-aid

# 2. Initialize Dev-AID in your project (interactive wizard)
cd ~/your-project
gh dev-aid init

# 2b. Or non-interactive for CI / automated testing
gh dev-aid init --yes

# 3. Configure API keys (optional — for router testing)
#    These can also be added to .dev-aid/config/.env after setup.
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="..."
export OPENAI_API_KEY="sk-..."

# 4. Verify installation
cat .dev-aid/VERSION
# Expected: 1.5.1
```

<details>
<summary><strong>Alternative: clone the Dev-AID repo directly</strong> (only useful if you want to hack on Dev-AID itself, not test it on your project)</summary>

```bash
git clone https://github.com/Probably-Group/Dev-AID.git
cd Dev-AID
./.dev-aid/scripts/setup-dev-aid.sh
```

</details>

### Verify Installation

In your AI CLI session (Claude Code, Gemini CLI, etc.):

```
/aid-status    # Shows configuration, providers, context files
/aid-help      # Lists all available commands
```

Both commands should run without errors and display meaningful output.

---

## 2. What to Test (Test Matrix)

### 2.1 Installation & Setup (P0 — Critical Path)

**What it does**: Initializes Dev-AID environment with directory structure, configs, symlinks, and git hooks.

**How to test**:
```bash
# Fresh setup
./.dev-aid/scripts/setup-dev-aid.sh

# Verify structure
ls .dev-aid/config/routing.json
ls .dev-aid/logs/
ls .dev-aid/skills/expert/
```

**What to look for**:
- `setup-dev-aid.sh` completes without errors
- Prerequisites check passes (or clearly reports what's missing)
- `routing.json`, `models.json` created in `.dev-aid/config/`
- `.dev-aid/logs/` directory exists
- Symlinks from provider directories to shared skills resolve correctly

---

### 2.2 Slash Commands & Discovery (P0 — Critical Path)

**What it does**: Provides `aid-*` short aliases for all Dev-AID commands with autocomplete discovery.

**How to test**:
```
# Discovery
/aid-help                    # Should list ALL commands

# Autocomplete (type and wait)
/aid-                        # Should show autocomplete dropdown

# Test individual aliases resolve
/aid-status                  # Should show status (not "command not found")
/aid-analyze                 # Should start codebase analysis
```

**What to look for**:
- `/aid-help` lists all command categories (Agents, Router, Security, Quality, etc.)
- Typing `/aid-` triggers autocomplete in supported editors
- Each alias resolves to the correct full command
- Command descriptions are action-oriented (not "Short alias for...")

---

### 2.3 Skills System (P0 — Critical Path)

**What it does**: Auto-loads relevant expert skills based on detected project context (tech stack, files, dependencies).

**How to test**:
```bash
# Check which skills auto-load for your project
# (In Claude Code session, skills load at session start via hooks)

# Configure core skills
/aid-config

# Verify skill registry exists
ls .dev-aid/skills/registry/skills-index.json

# Check expert skills directory
ls .dev-aid/skills/expert/
```

**What to look for**:
- Skills relevant to the project's tech stack load automatically
- `/aid-config` shows the 5 core skills with enable/disable options
- Profiles work: minimal, ide-user, no-ide-setup, ci-cd
- Skills don't conflict or duplicate each other

---

### 2.4 Security Hooks (P0 — Critical Path)

**What it does**: Git hooks that scan for secrets, vulnerabilities, and code issues before commits and pushes.

**How to test**:
```bash
# Pre-commit: Create a file with a fake secret
echo 'API_KEY = "AKIAIOSFODNN7EXAMPLE"' > test-secret.py
git add test-secret.py
git commit -m "test: should be blocked"
# Expected: Gitleaks/Opengrep blocks the commit

# Clean up
rm test-secret.py
git reset HEAD test-secret.py 2>/dev/null

# Check hook is installed
ls -la .git/hooks/pre-commit
```

**What to look for**:
- Pre-commit hook catches hardcoded secrets (AWS keys, API tokens)
- Opengrep runs SAST rules on changed files
- Trivy scans for known vulnerabilities (if Docker available)
- Hook failures show clear, actionable error messages
- Clean commits (no secrets) pass without issues

**Note**: Security scanners require Docker. If Docker is unavailable, hooks should skip those checks gracefully.

---

### 2.5 Multi-AI Router (P1 — Important)

**What it does**: Routes requests across multiple AI providers (Anthropic, Google, OpenAI) with challenger, ensemble, and solo modes.

**How to test**:
```
# Check router status
/aid-router-status

# Solo mode (single provider)
/aid-ensemble "Explain what a mutex is in 2 sentences"

# Challenger mode (two models, pick best)
/aid-challenger "Write a Python function to check if a number is prime"
```

**What to look for**:
- Router correctly selects provider based on request type
- Logs written to `.dev-aid/logs/routing.log`
- Cost tracking written to `.dev-aid/logs/costs.json`
- Fallback works when primary provider fails
- Large context (>100K tokens) routes to Gemini
- Error handling with invalid/missing API keys is clear

**Note**: Router testing requires real API credits (~$0.10-0.50 per test). Test selectively.

---

### 2.6 Agent Framework (P1 — Important)

**What it does**: Autonomous AI agents that perform multi-step tasks (PR review, test generation, tech debt scanning, etc.).

**How to test**:
```bash
# List available agents
/aid-help   # Check Agents section

# PR Review (requires GitHub access)
/aid-pr <PR-NUMBER>

# Test generation
/aid-test src/

# Tech debt scan
/aid-debt . high

# Onboarding guide
/aid-onboard

# Doc audit
/aid-docs .

# Research
/aid-research "async patterns in Python"
```

**What to look for**:
- Each agent completes its task without hanging
- Output is actionable (not generic boilerplate)
- `--dry-run` flag prevents write operations
- `--json` flag produces valid JSON output
- Agent respects safety constraints (command blocklist)
- Agent loads relevant expert skills as system prompts

---

### 2.7 Local Search / RAG (P1 — Important)

**What it does**: Builds a semantic index of the codebase for hybrid search (keyword + vector) via MCP integration.

**How to test**:
```bash
# Check if local search is installed
ls .dev-aid/local-search/

# Build index (first time)
# Follow instructions in /aid-status output

# Test search (via MCP if configured)
# Search for a known function name in your project
```

**What to look for**:
- Index builds without errors
- Search returns relevant results (not random files)
- Results include file paths and line numbers
- MCP integration makes search available to AI CLIs
- Index stored at `~/.claude_code_search/` (per-project)

---

### 2.8 MCP Integration (P1 — Important)

**What it does**: Connects AI CLIs to external tools (databases, APIs, search) via Model Context Protocol servers.

**How to test**:
```bash
# Check MCP configuration in your AI CLI
# Claude Code: check .claude/settings.json for mcpServers
# Gemini CLI: check .gemini/settings.json

# Verify Dev-AID's MCP servers are discoverable
/aid-status    # Should show MCP status
```

**What to look for**:
- MCP servers listed in status output
- Servers start without errors
- Environment variables are isolated (not leaking between servers)
- Enable/disable toggles work

---

### 2.9 Process Skills (P2 — Nice to Have)

**What it does**: Workflow enforcement skills (verification-gate, TDD protocol, etc.) that guide structured development processes.

**How to test**:
```bash
# Check process skills directory
ls .dev-aid/skills/process/

# Process skills activate contextually
# (e.g., verification-gate activates during deployment workflows)
```

**What to look for**:
- Process skills load when relevant workflow context is detected
- Skill instructions are clear and actionable
- No conflicts with expert skills

---

### 2.10 Utility Scripts (P2 — Nice to Have)

**What it does**: Standalone shell scripts for CI generation, architecture mapping, data fabrication, and documentation sync.

**How to test**:
```bash
# CI Generator
./.dev-aid/scripts/generate-ci.sh
./.dev-aid/scripts/generate-ci.sh --optimize

# Architecture mapper
./.dev-aid/scripts/map-architecture.sh

# Data fabricator (needs a schema file)
# ./.dev-aid/scripts/fabricate-data.sh schema.json

# Doc sync checker
./.dev-aid/scripts/sync-docs.sh
```

**What to look for**:
- Scripts detect project type correctly (Node.js, Python, Rust, Go)
- Generated CI workflows are valid YAML
- Architecture diagrams render as valid Mermaid.js
- Scripts handle edge cases (empty projects, monorepos)

---

### 2.11 Local LLM Support (P2 — Nice to Have)

**What it does**: Setup wizard and smart routing for local inference runtimes (Ollama, LM Studio) as Dev-AID providers.

**How to test**:
```bash
# Check if Ollama is running
ollama list

# Use local provider with agent framework
dev-aid-agent research --topic "test" --provider local

# Check local LLM documentation
cat .dev-aid/docs/LOCAL-LLM-GUIDE.md
```

**What to look for**:
- Local provider connects to Ollama/LM Studio
- Model selection based on hardware capabilities
- Fallback to cloud provider when local model can't handle request
- Clear error messages when no local runtime is available

---

### 2.12 Cross-Editor Compatibility (P2 — Nice to Have)

**What it does**: Slash commands and skills work across Claude Code, Gemini CLI, Codex CLI, Cursor, Windsurf, and Cline.

**How to test**:

Test in each available editor:
1. Open a project with Dev-AID initialized
2. Run `/aid-help` — should list all commands
3. Run `/aid-status` — should show configuration
4. Test autocomplete with `/aid-`
5. Run one agent command (e.g., `/aid-onboard`)

**What to look for**:
- Commands exist for both Claude (`.md`) and Gemini (`.toml`) formats
- Slash command syntax works in each editor
- Skills load correctly per provider
- No provider-specific errors or missing files

---

## 3. How to Report Issues

### Environment Snapshot

Run this one-liner to capture your environment info (paste output into bug reports):

```bash
echo "=== Dev-AID Environment ===" && \
echo "Version: $(cat .dev-aid/VERSION 2>/dev/null || echo 'unknown')" && \
echo "OS: $(uname -s) $(uname -r)" && \
echo "Python: $(python3 --version 2>/dev/null || echo 'not found')" && \
echo "Git: $(git --version 2>/dev/null || echo 'not found')" && \
echo "Bash: $(bash --version | head -1)" && \
echo "Claude: $(claude --version 2>/dev/null || echo 'not installed')" && \
echo "Gemini: $(gemini --version 2>/dev/null || echo 'not installed')" && \
echo "Docker: $(docker --version 2>/dev/null || echo 'not installed')" && \
echo "Ollama: $(ollama --version 2>/dev/null || echo 'not installed')"
```

### Required Fields

Every issue should include:

| Field | Description |
|-------|-------------|
| **Component** | Which feature area (see test matrix above) |
| **Steps to Reproduce** | Exact commands you ran, in order |
| **Expected Result** | What should have happened |
| **Actual Result** | What actually happened (include error messages) |
| **Environment** | Output from the snapshot command above |

### Where to Find Logs

| Log | Location | Contains |
|-----|----------|----------|
| Router log | `.dev-aid/logs/routing.log` | Request routing decisions, provider selection, errors |
| Cost tracking | `.dev-aid/logs/costs.json` | Token usage and cost per request |
| Git hook output | Terminal (stderr) | Security scan results, blocked commits |
| Init script log | Terminal (stdout) | Setup progress and errors |

### Severity Guide

| Severity | Definition | Example |
|----------|------------|---------|
| **Blocker** | Cannot use Dev-AID at all, data loss risk | `setup-dev-aid.sh` crashes, security hook deletes files |
| **Major** | Feature doesn't work, no workaround | `/aid-pr` always fails, router returns wrong provider |
| **Minor** | Feature works but has issues, workaround exists | Autocomplete shows stale entries, typo in output |
| **Suggestion** | Not broken, but could be better | Better error message, clearer docs |

### Labeling

When filing issues, add these labels:

- `beta` — Always add this for beta feedback
- Component tag: `router`, `agents`, `skills`, `security`, `rag`, `mcp`, `setup`, `docs`
- Severity: `blocker`, `major`, `minor`, `suggestion`

### Good vs Bad Bug Reports

**Bad**:
> "The router doesn't work."

**Good**:
> **Component**: Multi-AI Router
> **Steps**: Ran `/aid-challenger "Write a hello world in Rust"` in Claude Code
> **Expected**: Two models should generate responses, best one selected
> **Actual**: Error: `KeyError: 'anthropic'` in routing.log (line 145)
> **Environment**: macOS 15.3, Python 3.12.1, Dev-AID 1.5.1
> **Logs**: [attached routing.log snippet]

---

## 4. Known Limitations

These are documented issues that are **not bugs** — they're known gaps in the current beta:

| Limitation | Details | Workaround |
|------------|---------|------------|
| Windows untested | Dev-AID works on macOS and Linux; Windows support is untested | Use WSL on Windows |
| Router costs real money | Each router test uses API credits (~$0.10-0.50) | Test selectively; use solo mode for cheaper tests |
| Docker required for scanners | Gitleaks, Trivy, and Opengrep require Docker | Install Docker, or accept that security hooks will skip scanner checks |

---

## 5. Feedback Categories

Use these categories when reporting feedback (matches the [Beta Feedback issue template](../../.github/ISSUE_TEMPLATE/beta_feedback.yml)):

| Category | When to Use | Example |
|----------|-------------|---------|
| **Bug** | Something is broken or crashes | Command throws an error, wrong output |
| **UX Issue** | Confusing, unclear, or unexpected behavior | Command succeeds but output is hard to understand |
| **Missing Feature** | Expected something that doesn't exist | "I expected `/aid-rollback` to exist" |
| **Documentation Gap** | Docs are wrong, missing, or misleading | Guide says to run X but the actual command is Y |
| **Performance** | Slow, resource-heavy, or unresponsive | Skill loading takes >30 seconds |
| **General** | Doesn't fit other categories | General impressions, suggestions |

---

## Quick Reference

| Action | Command |
|--------|---------|
| Check version | `cat .dev-aid/VERSION` |
| Verify setup | `/aid-status` |
| List all commands | `/aid-help` |
| File a bug | [Beta Feedback template](https://github.com/Probably-Group/Dev-AID/issues/new?template=beta_feedback.yml) |
| View router logs | `cat .dev-aid/logs/routing.log` |
| View cost data | `cat .dev-aid/logs/costs.json` |
| Run environment snapshot | See section 3 above |
