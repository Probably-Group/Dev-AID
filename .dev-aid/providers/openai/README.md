# OpenAI Provider

This directory contains OpenAI-specific configuration for Dev-AID.

## Context File

When Dev-AID is installed in a project, it generates `OPENAI.md` at the project root (symlinked to `.dev-aid/providers/openai/OPENAI.md`).

This context file contains:
- Project knowledge base references (memory-bank)
- OpenAI's role in the Dev-AID multi-model setup
- Auto-detected tech stack information

## How Context is Used

Unlike Claude Code or Gemini CLI, OpenAI doesn't have a standard CLI tool that auto-reads context files. Context is used through:

1. **ChatGPT with file uploads** - Upload OPENAI.md as context
2. **Custom GPT** - Include context in GPT instructions
3. **API integrations** - Dev-AID router injects context into prompts
4. **IDE plugins** - Tools like Continue.dev can use context files

## Slash Command Gap

OpenAI does not provide a standardized CLI with command discovery (unlike Claude Code's `.claude/commands/` or Gemini CLI's `.gemini/commands/`). As a result, `.openai/commands/` is **empty** — there are no `/aid-*` slash commands for OpenAI-native tools.

### Workarounds

| Tool | Agent Access | How |
|------|-------------|-----|
| **Python CLI** | Full (all 8 agents + 4 teams) | `dev-aid-agent pr-reviewer --pr 42 --provider openai` |
| **Codex CLI** | Full | Reads `AGENTS.md.template` triggers + symlinked skills |
| **Cursor / Windsurf / Cline** | Full slash commands | These editors read `.claude/commands/` natively |
| **ChatGPT** | Context only | Upload `OPENAI.md` manually |
| **Custom GPTs** | Context only | Paste instructions from `OPENAI.md` |

For programmatic agent execution with OpenAI models, use the Python CLI — it has full feature parity with Anthropic and Google providers including multi-agent teams, JSON output, and cost tracking.

## Directory Structure

```
.dev-aid/providers/openai/
├── README.md           # This file
├── OPENAI.md          # Generated context file (after install)
└── .openai/
    └── commands/      # Empty — OpenAI has no CLI command discovery
```

## Memory Bank Integration

The generated OPENAI.md includes instructions to read:
- `.dev-aid/memory-bank/patterns.md` - Coding conventions
- `.dev-aid/memory-bank/security.md` - Security rules
- `.dev-aid/memory-bank/decisions.md` - Architecture decisions

## Models Supported

From `models.json`:
- `gpt-4o` (default) - Latest multimodal model
- `gpt-4-turbo` - Fast GPT-4 variant
- `gpt-4.1` - Extended context version
- `gpt-3.5-turbo` - Cost-effective option
