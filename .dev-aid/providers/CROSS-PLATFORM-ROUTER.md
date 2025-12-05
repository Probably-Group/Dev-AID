# Cross-Platform Router Implementation

## Overview

The Dev-AID router system supports **both Claude Code and Gemini CLI** through provider-specific slash command implementations.

## Why Two Implementations?

**Claude Code** and **Gemini CLI** use different slash command formats:

| Aspect | Claude Code | Gemini CLI |
|--------|-------------|------------|
| **File Format** | Markdown (`.md`) | TOML (`.toml`) |
| **Location** | `.claude/commands/` | `.gemini/commands/` |
| **Frontmatter** | YAML between `---` | TOML config |
| **Arguments** | Implicit from user input | Explicit with `{{args}}` |
| **Shell Commands** | Not supported in prompts | Supported with `!{command}` |

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
│   └── gemini/
│       └── .gemini/commands/router/
│           ├── aid-router-challenger.toml
│           ├── aid-router-ensemble.toml
│           └── aid-router-status.toml
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
      "model": "claude-sonnet-4.5-20250929",
      "cost_per_mtok": {"input": 3.0, "output": 15.0},
      "strengths": ["code_generation", "security"]
    },
    "gemini-flash": {
      "provider": "google",
      "model": "gemini-2.0-flash-exp",
      "cost_per_mtok": {"input": 0.075, "output": 0.30},
      "max_context": 2000000,
      "strengths": ["massive_context", "cost_effective"]
    }
  }
}
```

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

## References

**Claude Code Documentation:**
- [Custom Commands](https://github.com/anthropics/claude-code)

**Gemini CLI Documentation:**
- [Custom Slash Commands Blog](https://cloud.google.com/blog/topics/developers-practitioners/gemini-cli-custom-slash-commands)
- [Gemini CLI Tutorial Series](https://medium.com/google-cloud/gemini-cli-tutorial-series-part-7-custom-slash-commands-64c06195294b)
- [Official GitHub](https://github.com/google-gemini/gemini-cli)
- [Google Codelabs](https://codelabs.developers.google.com/gemini-cli-hands-on)

---

**Last Updated:** 2025-11-28
**Version:** 1.0.0
**Status:** Production-ready for both platforms
