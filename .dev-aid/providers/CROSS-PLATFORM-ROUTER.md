# Cross-Platform Router Implementation

## Overview

The Dev-AID router system supports **Claude Code, Gemini CLI, and Codex CLI** through provider-specific slash command implementations. Additionally, **Cursor, Windsurf, and Cline** inherit Claude Code's commands natively.

> **Note:** OpenAI does not provide a CLI with slash command discovery. For OpenAI model usage, use the Python CLI (`dev-aid-agent --provider openai`). See the [OpenAI provider README](openai/README.md) for details.

## Why Multiple Implementations?

**Claude Code**, **Gemini CLI**, and **Codex CLI** use different slash command formats:

| Aspect | Claude Code | Gemini CLI | Codex CLI | OpenAI |
|--------|-------------|------------|-----------|--------|
| **File Format** | Markdown (`.md`) | TOML (`.toml`) | YAML frontmatter + MD | N/A |
| **Location** | `.claude/commands/` | `.gemini/commands/` | `.codex/skills/` | `.openai/commands/` (empty) |
| **Context File** | `CLAUDE.md` | `GEMINI.md` | `AGENTS.md` | `OPENAI.md` |
| **Slash Commands** | 50+ commands | 50+ commands | Skill triggers | None — no CLI discovery |
| **Agent Support** | Full (via Python CLI) | Full (via Python CLI) | Full (via Python CLI) | Full (via Python CLI only) |

## File Structure

```
dev-aid/.dev-aid/
├── config/
│   ├── routing.json          # Shared routing configuration
│   └── models.json           # Shared model registry
├── providers/
│   ├── claude/
│   │   └── .claude/commands/router/
│   │       ├── aid-router-challenger.md
│   │       ├── aid-router-ensemble.md
│   │       └── aid-router-status.md
│   ├── gemini/
│   │   └── .gemini/commands/router/
│   │       ├── aid-router-challenger.toml
│   │       ├── aid-router-ensemble.toml
│   │       └── aid-router-status.toml
│   └── codex/
│       ├── README.md             # Installation guide
│       ├── AGENTS.md.template    # Template for project AGENTS.md
│       └── .codex/
│           ├── hooks/
│           │   └── session-start.sh  # Context detection hook
│           └── skills/           # Symlinks to Dev-AID skills
│               ├── core -> ../../../../skills/core
│               ├── expert -> ../../../../skills/expert
│               └── process -> ../../../../skills/process
└── logs/
    ├── routing.log           # Shared routing logs
    └── costs.json            # Shared cost tracking
```

## Installation

### For Claude Code

Symlink or copy the Claude commands to your project:

```bash
# Project-scoped (recommended for team sharing)
ln -s dev-aid/.dev-aid/providers/claude/.claude .claude

# User-scoped (personal preferences)
ln -s dev-aid/.dev-aid/providers/claude/.claude ~/.claude
```

### For Gemini CLI

Symlink or copy the Gemini commands to your project:

```bash
# Project-scoped (recommended for team sharing)
ln -s dev-aid/.dev-aid/providers/gemini/.gemini .gemini

# User-scoped (personal preferences)
ln -s dev-aid/.dev-aid/providers/gemini/.gemini ~/.gemini
```

### For Codex CLI

Symlink or copy the Codex configuration to your project:

```bash
# Project-scoped (recommended for team sharing)
ln -s dev-aid/.dev-aid/providers/codex/.codex .codex

# Create AGENTS.md (context file for Codex)
ln -s dev-aid/.dev-aid/providers/codex/.codex/AGENTS.md AGENTS.md
# Or copy the template:
cp dev-aid/.dev-aid/providers/codex/AGENTS.md.template AGENTS.md
```

**Note:** Codex CLI uses `AGENTS.md` (not `CODEX.md`) per OpenAI's specification.

## Usage

### Claude Code

```bash
# In Claude Code terminal
/dev-aid-router-challenger "Implement OAuth2 authentication"
/dev-aid-router-ensemble "Analyze entire codebase for performance issues"
/dev-aid-router-status
```

### Gemini CLI

```bash
# In Gemini CLI
/dev-aid-router-challenger Implement OAuth2 authentication
/dev-aid-router-ensemble Analyze entire codebase for performance issues
/dev-aid-router-status
```

### Codex CLI

```bash
# In Codex CLI (skills are loaded via AGENTS.md)
# Use natural language - skills are automatically available
codex "Implement OAuth2 authentication using the devsecops-expert skill"
codex "Review this code for security issues"
```

**Note:** Codex CLI doesn't use slash commands for routing. Instead, skills are loaded via `@file` references in AGENTS.md and are available as context for all prompts.

## Command Reference

### `/dev-aid-router-challenger`

**Purpose:** Two-AI review workflow (Claude generates, Gemini reviews)

**Claude Code:**
```bash
/dev-aid-router-challenger "Your request here"
```

**Gemini CLI:**
```bash
/dev-aid-router-challenger Your request here
```

**Output:**
- Primary implementation from Claude
- Security critique from Gemini
- Severity rating (LOW/MEDIUM/HIGH/CRITICAL)
- Refined implementation if issues found

---

### `/dev-aid-router-ensemble`

**Purpose:** Smart routing to optimal AI model based on task type

**Claude Code:**
```bash
/dev-aid-router-ensemble "Analyze entire codebase"
/dev-aid-router-ensemble "Implement user authentication"
```

**Gemini CLI:**
```bash
/dev-aid-router-ensemble Analyze entire codebase
/dev-aid-router-ensemble Implement user authentication
```

**Routing Logic:**
- Massive context analysis → Gemini Flash (2M context, cheap)
- Code generation → Claude Sonnet (best coder)
- Security audit → Claude Sonnet (security expert)
- Documentation → GPT-4o (clear writing)
- Debugging → Claude Sonnet (strong reasoning)
- Complex reasoning → Claude Opus (maximum capability)

---

### `/dev-aid-router-status`

**Purpose:** View routing configuration and cost analytics

**Claude Code:**
```bash
/dev-aid-router-status
/dev-aid-router-status --costs
/dev-aid-router-status --history
```

**Gemini CLI:**
```bash
/dev-aid-router-status
/dev-aid-router-status --costs
/dev-aid-router-status --history
```

**Output:**
- Current routing configuration
- Cost breakdown by model
- Recent routing decisions
- Budget status

## Configuration

Both implementations share the same configuration files:

### `routing.json`

Controls routing behavior:

```json
{
  "default_mode": "solo",
  "modes": {
    "challenger": {
      "enabled": true,
      "primary_model": "claude-sonnet",
      "challenger_model": "gemini-flash",
      "auto_refine_on": ["HIGH", "CRITICAL"],
      "review_triggers": ["auth", "crypto", "password"]
    },
    "ensemble": {
      "enabled": true,
      "routing_strategy": "semantic",
      "task_routes": {
        "massive_context": "gemini-flash",
        "code_generation": "claude-sonnet",
        "security_audit": "claude-sonnet"
      }
    }
  },
  "fallback_chain": ["claude-sonnet", "gpt-4o", "gemini-flash"],
  "cost_limit_per_day": 100.0
}
```

### `models.json`

Model registry with costs and capabilities:

```json
{
  "models": {
    "claude-sonnet": {
      "provider": "anthropic",
      "model": "claude-sonnet-4-6",
      "cost_per_mtok": {"input": 3.0, "output": 15.0},
      "strengths": ["code_generation", "security"]
    },
    "gemini-pro": {
      "provider": "google",
      "model": "gemini-3.1-pro",
      "cost_per_mtok": {"input": 2.0, "output": 12.0},
      "max_context": 1000000,
      "strengths": ["massive_context", "multimodal"]
    }
  }
}
```

> See `.dev-aid/config/models.json` for the authoritative, always-current model registry.

## Implementation Details

### Claude Code Implementation

**File:** `.claude/commands/router/dev-aid-router-challenger.md`

```markdown
---
name: aid-router-challenger
description: Execute with Challenger mode - Claude generates, Gemini reviews
tags: [routing, multi-ai, security, review]
---

# Detailed prompt instructions...
[Complete implementation workflow]
```

### Gemini CLI Implementation

**File:** `.gemini/commands/router/dev-aid-router-challenger.toml`

```toml
description = "Execute with Challenger mode - Claude generates, Gemini reviews"

prompt = """
# Detailed prompt instructions...
[Complete implementation workflow]

User Request: {{args}}

Context: !{cat .dev-aid/memory-bank/security.md}
"""
```

**Key Differences:**
1. Gemini uses `{{args}}` for user input
2. Gemini supports `!{shell command}` for context gathering
3. Gemini uses TOML config instead of YAML frontmatter

## Shell Command Integration (Gemini Only)

Gemini CLI's `!{command}` syntax enables dynamic context gathering:

```toml
prompt = """
Recent changes: !{git diff --name-only HEAD~3..HEAD}
Memory bank: !{cat .dev-aid/memory-bank/security.md}
Routing config: !{cat .dev-aid/config/routing.json}
"""
```

This is more powerful than Claude Code's static prompts but requires the commands to be safe.

## Logging and Cost Tracking

Both implementations log to shared files:

**Routing Log:** `.dev-aid/logs/routing.log`
```
2025-11-28 14:23:15 [CHALLENGER] Model: claude-sonnet | Cost: $0.045
2025-11-28 14:23:42 [REVIEW] Model: gemini-flash | Issues: 2 | Severity: MEDIUM
```

**Cost Data:** `.dev-aid/logs/costs.json`
```json
{
  "2025-11-28": {
    "total": 2.47,
    "by_model": {
      "claude-sonnet": {"calls": 18, "cost": 1.85},
      "gemini-flash": {"calls": 3, "cost": 0.42}
    }
  }
}
```

## Team Collaboration

### Option 1: Check Commands Into Git

```bash
# Include provider-specific commands in repository
git add .claude/
git add .gemini/
git commit -m "Add router slash commands for Claude Code and Gemini CLI"
```

**Pros:**
- Team members get commands automatically
- Commands version-controlled
- Changes tracked in git history

**Cons:**
- Adds ~15KB to repository
- May need provider-specific tweaks

### Option 2: User-Scoped Installation

Each team member installs commands locally:

```bash
# Claude Code users
ln -s $(pwd)/dev-aid/.dev-aid/providers/claude/.claude ~/.claude

# Gemini CLI users
ln -s $(pwd)/dev-aid/.dev-aid/providers/gemini/.gemini ~/.gemini
```

**Pros:**
- Repository stays clean
- Users can customize commands
- No git noise

**Cons:**
- Manual setup required
- Commands not version-controlled
- Easier to drift out of sync

### Recommended: Hybrid Approach

1. Check in shared config files:
   ```bash
   git add .dev-aid/config/
   ```

2. Document command installation in README:
   ```markdown
   ## Setup Router Commands

   ### For Claude Code
   ln -s $(pwd)/dev-aid/.dev-aid/providers/claude/.claude .claude

   ### For Gemini CLI
   ln -s $(pwd)/dev-aid/.dev-aid/providers/gemini/.gemini .gemini
   ```

3. Add `.claude/` and `.gemini/` to `.gitignore` if using symlinks

## Troubleshooting

### Command not found in Claude Code

1. Check file location: `.claude/commands/router/dev-aid-router-*.md`
2. Verify frontmatter syntax (YAML with `---`)
3. Restart Claude Code session

### Command not found in Gemini CLI

1. Check file location: `.gemini/commands/router/dev-aid-router-*.toml`
2. Verify TOML syntax (`description = "..."`)
3. Update Gemini CLI: `gemini update` (requires v0.4.0+)
4. Check command discovery: `gemini /help`

### Shell commands failing in Gemini CLI

1. Verify file paths are correct
2. Check file permissions (must be readable)
3. Add error handling: `!{cat file.txt 2>/dev/null || echo "Not found"}`

### API keys not configured

Both implementations require API keys:

```bash
# Set environment variables
export ANTHROPIC_API_KEY="your-key-here"
export GOOGLE_API_KEY="your-key-here"
export OPENAI_API_KEY="your-key-here"
```

## Cost Optimization Tips

1. **Use ensemble routing** for automatic cost optimization
2. **Route massive context to Gemini** (97% cheaper than Claude)
3. **Use challenger mode selectively** (only for security-critical code)
4. **Set daily budget limits** in `routing.json`
5. **Monitor with /dev-aid-router-status** to track spending

## Roadmap

### Phase 1: ✅ Basic Implementation (COMPLETE)
- Slash commands for both platforms
- Shared configuration
- Manual routing

### Phase 2: 🚧 Logging & Metrics (IN PROGRESS)
- Cost tracking implementation
- Routing decision logs
- Analytics dashboard

### Phase 3: 📋 Advanced Features (PLANNED)
- Automatic semantic routing
- API fallback chains
- Circuit breakers
- MCP integration

### Phase 4: 📋 Production (PLANNED)
- Rate limiting
- Retries with exponential backoff
- Model performance analytics
- Cost anomaly detection

## Codex CLI Integration

### Key Differences

Codex CLI differs from Claude Code and Gemini CLI in several ways:

1. **Context File**: Uses `AGENTS.md` instead of `CLAUDE.md` or `GEMINI.md`
2. **No Slash Commands**: Skills are loaded via `@file` references, not `/commands`
3. **Same Skill Format**: Uses identical YAML frontmatter + Markdown format as Claude Code
4. **Session Hooks**: Configure via `config.toml` instead of `hooks.json`

### AGENTS.md Loading Order

From [Codex documentation](https://developers.openai.com/codex/guides/agents-md):

1. `~/.codex/AGENTS.override.md` (highest priority)
2. `~/.codex/AGENTS.md` (global base)
3. Project root `AGENTS.md`
4. Subdirectory `AGENTS.md` files (walked toward CWD)

Files are concatenated with blank lines, max 32 KiB.

### Using Skills in Codex

Reference Dev-AID skills in your AGENTS.md:

```markdown
## Active Skills

@.codex/skills/expert/fastapi-expert/SKILL.md
@.codex/skills/expert/devsecops-expert/SKILL.md
@.codex/skills/core/code-reviewer/SKILL.md
```

### Auto-Loading Skills

Run the session-start hook to automatically detect and load relevant skills:

```bash
.dev-aid/providers/codex/.codex/hooks/session-start.sh
```

This:
1. Detects project context (tech stack, files)
2. Selects top 5 most relevant skills
3. Generates AGENTS.md with `@file` references
4. Reports loaded skills

### Codex Hooks Configuration

Add to `.codex/config.toml`:

```toml
[hooks]
session_start = ".codex/hooks/session-start.sh"
```

## References

**Claude Code Documentation:**
- [Custom Commands](https://github.com/anthropics/claude-code)

**Gemini CLI Documentation:**
- [Custom Slash Commands Blog](https://cloud.google.com/blog/topics/developers-practitioners/gemini-cli-custom-slash-commands)
- [Gemini CLI Tutorial Series](https://medium.com/google-cloud/gemini-cli-tutorial-series-part-7-custom-slash-commands-64c06195294b)
- [Official GitHub](https://github.com/google-gemini/gemini-cli)
- [Google Codelabs](https://codelabs.developers.google.com/gemini-cli-hands-on)

**Codex CLI Documentation:**
- [Codex CLI](https://developers.openai.com/codex/cli/)
- [AGENTS.md Guide](https://developers.openai.com/codex/guides/agents-md)
- [Skills Creation](https://developers.openai.com/codex/skills/create-skill)
- [GitHub Repository](https://github.com/openai/codex)

---

**Last Updated:** 2026-04-08
**Version:** 1.5.1
**Status:** Production-ready for Claude Code, Gemini CLI, and Codex CLI
