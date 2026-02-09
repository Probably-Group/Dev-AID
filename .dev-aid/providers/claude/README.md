# Claude Code Integration for Dev-AID

This directory provides Dev-AID integration for [Claude Code](https://docs.anthropic.com/en/docs/claude-code), the primary supported provider.

## Overview

Claude Code uses Markdown-based slash commands with YAML frontmatter. Dev-AID provides **53 slash commands** across 8 categories, all with short `aid-*` aliases for quick discovery. Skills are shared via symlinks for automatic synchronization.

## Prerequisites

1. **Claude Code installed** (v1.0.0+)
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

2. **Anthropic API key configured**
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."
   ```

3. **Dev-AID installed in your project**
   ```bash
   ls -la .dev-aid/
   ```

## Quick Setup

### Option 1: Symlink-Based (Recommended)

Create symlinks from your project root to use Dev-AID's Claude configuration:

```bash
# From your project root
ln -s .dev-aid/providers/claude/.claude .claude

# Create CLAUDE.md symlink (or copy)
ln -s .dev-aid/providers/claude/CLAUDE.md CLAUDE.md
```

### Option 2: Copy-Based

Copy the Claude configuration to your project:

```bash
cp -r .dev-aid/providers/claude/.claude .claude
cp .dev-aid/providers/claude/CLAUDE.md CLAUDE.md
```

## Directory Structure

```
.dev-aid/providers/claude/
├── README.md                    # This file
└── .claude/
    ├── commands/                # 53 slash commands (.md files)
    │   ├── agents/              # PR review, test gen, tech debt, CI fix, etc.
    │   ├── maintenance/         # Update models, deploy validation
    │   ├── operations/          # Deploy validation
    │   ├── productivity/        # API contract, commit plan
    │   ├── quality/             # Code health, debt analysis, review staged
    │   ├── router/              # Challenger, ensemble, router status
    │   ├── security/            # Audit, vulnerability scan
    │   └── setup/               # Analyze, status, config, build skill
    ├── hooks/                   # 5 lifecycle hooks
    │   ├── session-start.sh             # Initial context loading
    │   ├── session-start-load-context.sh # Auto-load skills based on project
    │   ├── skill-activation-conservative.sh # Conservative skill activation
    │   ├── post-tool-use-tracker.sh     # Tool usage tracking
    │   └── stop-quality-gates.sh        # Quality gates on session end
    ├── settings.json            # Permissions, hooks config, auto-load strategy
    └── skills -> ../../../skills # Symlink to shared skills directory
```

## Slash Commands

All commands use Markdown format with YAML frontmatter:

```markdown
---
name: dev-aid-agent-pr-review
description: AI-powered pull request review
category: agents
author: Dev-AID Team (https://probably.group)
version: 1.0.0
---

# PR Review Agent

[Full instructions with $ARGUMENTS support]
```

### Command Categories

| Category | Commands | Examples |
|----------|----------|----------|
| **Agents** | 16 (8 full + 8 aliases) | `/aid-pr`, `/aid-test`, `/aid-debt`, `/aid-ci` |
| **Router** | 8 (4 full + 4 aliases) | `/aid-challenger`, `/aid-ensemble`, `/aid-router-status` |
| **Security** | 4 (2 full + 2 aliases) | `/aid-audit`, `/aid-vulnscan` |
| **Quality** | 6 (3 full + 3 aliases) | `/aid-health`, `/aid-debt-report`, `/aid-review` |
| **Productivity** | 4 (2 full + 2 aliases) | `/aid-commit`, `/aid-api` |
| **Operations** | 2 (1 full + 1 alias) | `/aid-deploy` |
| **Setup** | 10 (5 full + 5 aliases) | `/aid-analyze`, `/aid-status`, `/aid-config` |
| **Maintenance** | 3 (misc) | `/aid-models`, `/aid-help` |

### Dual Naming System

Every command has both a full name and a short alias:

- **Full**: `/dev-aid-agent-pr-review <PR_NUMBER>` — complete documentation
- **Short**: `/aid-pr <PR_NUMBER>` — thin wrapper pointing to the full command

Type `/aid-` in Claude Code to trigger autocomplete and browse all available commands.

## Hooks Configuration

Claude Code hooks execute at specific lifecycle events:

| Hook | Event | Purpose |
|------|-------|---------|
| `session-start.sh` | Session start | Load initial context |
| `session-start-load-context.sh` | Session start | Auto-detect project and load relevant skills |
| `skill-activation-conservative.sh` | User prompt | Conservative skill activation (max 2-3 per session) |
| `post-tool-use-tracker.sh` | Post tool use | Track tool usage patterns |
| `stop-quality-gates.sh` | Session stop | Enforce quality gates before session ends |

Hooks are configured in `settings.json`. The architecture is designed for token efficiency — standing context budget is ~900-1,500 tokens (0.45-0.75% of 200k context window).

## Context Loading

Claude Code loads context files in this order:

1. `~/.claude/CLAUDE.md` (user's global instructions)
2. Project root `CLAUDE.md` (project-specific instructions)
3. Subdirectory `CLAUDE.md` files (walked toward CWD)

The `CLAUDE.md` file is generated by the install script and contains project-specific instructions, command references, and architecture context.

## Skills

Skills are shared across all providers via symlinks:

| Category | Count | Examples |
|----------|-------|----------|
| **Core** | 5 | test-runner, linter, type-checker, code-reviewer, secret-scanner |
| **Expert** | 73 | fastapi-expert, devsecops-expert, api-expert, typescript-expert |
| **Process** | 7 | tdd-protocol, verification-gate, systematic-debugging |

Browse available skills:
```bash
ls .claude/skills/expert/
ls .claude/skills/core/
ls .claude/skills/process/
```

## Verification

### Check symlinks are working

```bash
ls -la .claude/skills/
# Should show symlinks to ../../../skills/{core,expert,process}
```

### Check commands are discoverable

In a Claude Code session:
```
/aid-help      # Lists all available commands
/aid-status    # Shows configuration and providers
```

### Test a command

```
/aid-onboard   # Should generate an onboarding guide for the project
```

## Troubleshooting

### "Skill file not found"

Verify symlinks are intact:
```bash
ls -la .claude/skills/expert/fastapi-expert/
```

If broken, recreate:
```bash
cd .claude/skills
rm -f core expert process
ln -s ../../../../.dev-aid/skills/core core
ln -s ../../../../.dev-aid/skills/expert expert
ln -s ../../../../.dev-aid/skills/process process
```

### "Command not found"

1. Verify `.claude/commands/` directory exists and contains `.md` files
2. Check that the symlink from project root points to the provider directory
3. Restart Claude Code session to reload commands

### "Hook not executing"

1. Verify hook is executable: `chmod +x .claude/hooks/*.sh`
2. Check `settings.json` has hooks configured
3. Run manually to check for errors: `.claude/hooks/session-start.sh`

## Comparison with Other Providers

| Feature | Claude Code | Gemini CLI | Codex CLI |
|---------|-------------|------------|-----------|
| Context file | `CLAUDE.md` | `GEMINI.md` | `AGENTS.md` |
| Command format | Markdown (.md) | TOML (.toml) | Natural language triggers |
| Command discovery | `/slash` commands (53) | `/slash` commands (31) | Trigger phrases (26) |
| Skills directory | `.claude/skills/` | `.gemini/skills/` | `.codex/skills/` |
| Hooks count | 5 | 1 | 1 |
| Skill format | YAML frontmatter + MD | YAML frontmatter + MD | YAML frontmatter + MD |

## Resources

- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code)
- [Claude Code Slash Commands](https://docs.anthropic.com/en/docs/claude-code/slash-commands)
- [Claude Code Hooks](https://docs.anthropic.com/en/docs/claude-code/hooks)
- [Dev-AID Documentation](../../docs/)

---

**Last Updated:** 2026-02-09
**Version:** 1.0.0
**Status:** Production-ready
