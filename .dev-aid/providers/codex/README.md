# Codex CLI Integration for Dev-AID

This directory provides Dev-AID integration for [OpenAI Codex CLI](https://developers.openai.com/codex/cli/).

## Overview

Codex CLI uses the same SKILL.md format as Claude Code (YAML frontmatter + Markdown body), which means **existing Dev-AID skills work with zero conversion**. Skills are shared via symlinks for automatic synchronization.

## Prerequisites

1. **Codex CLI installed** (v1.0.0+)
   ```bash
   npm install -g @openai/codex-cli
   # or
   brew install codex
   ```

2. **OpenAI API key configured**
   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```

3. **Dev-AID installed in your project**
   ```bash
   # Check Dev-AID is present
   ls -la .dev-aid/
   ```

## Quick Setup

### Option 1: Symlink-Based (Recommended)

Create symlinks from your project root to use Dev-AID's Codex configuration:

```bash
# From your project root
ln -s .dev-aid/providers/codex/.codex .codex

# Create AGENTS.md symlink (or copy)
ln -s .dev-aid/providers/codex/.codex/AGENTS.md AGENTS.md
```

### Option 2: Copy-Based

Copy the Codex configuration to your project:

```bash
# Copy .codex directory
cp -r .dev-aid/providers/codex/.codex .codex

# Copy AGENTS.md template
cp .dev-aid/providers/codex/AGENTS.md.template AGENTS.md
```

## Directory Structure

```
.dev-aid/providers/codex/
├── README.md                    # This file
├── AGENTS.md.template           # Source of truth (triggers + guidelines + skill markers)
└── .codex/
    ├── AGENTS.md                # Generated at session start from template
    ├── hooks/
    │   └── session-start.sh     # Reads template, injects skills, writes AGENTS.md
    └── skills/                  # Symlinks to Dev-AID skills
        ├── core -> ../../../../skills/core
        ├── expert -> ../../../../skills/expert
        └── process -> ../../../../skills/process
```

## AGENTS.md Loading Order

Codex loads context files in this order (from [docs](https://developers.openai.com/codex/guides/agents-md)):

1. `~/.codex/AGENTS.override.md` (highest priority)
2. `~/.codex/AGENTS.md` (global base)
3. Project root `AGENTS.md`
4. Subdirectory `AGENTS.md` files (walked toward CWD)

Files are concatenated with blank lines, max 32 KiB.

## How AGENTS.md Is Generated

The `session-start.sh` hook uses a **template-based injection** architecture:

1. **Reads** `AGENTS.md.template` — the source of truth containing all 26 trigger phrases, team workflows, utility commands, and project guidelines
2. **Detects** project context via `detect-context.sh` (languages, frameworks, tools)
3. **Selects** the top 5 most relevant skills via `select-skills.sh`
4. **Replaces** the `<!-- AUTO-GENERATED SKILLS START/END -->` block in the template with dynamic `@file` skill references
5. **Writes** the result as `.codex/AGENTS.md`

If the template is missing, the hook falls back to generating a minimal AGENTS.md with only skill references (no triggers).

### Auto-Loading

Run the session-start hook to automatically select relevant skills:

```bash
.dev-aid/providers/codex/.codex/hooks/session-start.sh
```

This analyzes your project and generates an AGENTS.md with appropriate skill references and all 26 command trigger phrases.

### Manual Skill References

Reference skills directly in your AGENTS.md:

```markdown
## Active Skills

@.codex/skills/expert/fastapi-expert/SKILL.md
@.codex/skills/expert/devsecops-expert/SKILL.md
@.codex/skills/core/code-reviewer/SKILL.md
```

### Available Skills

| Category | Count | Examples |
|----------|-------|----------|
| **Core** | 5 | test-runner, linter, type-checker, code-reviewer, secret-scanner |
| **Expert** | 74 | fastapi-expert, devsecops-expert, api-expert, typescript-expert, prd-generator |
| **Process** | 7 | tdd-protocol, verification-gate, systematic-debugging |

Browse all skills:
```bash
ls .codex/skills/expert/
ls .codex/skills/core/
ls .codex/skills/process/
```

## Skill Format Compatibility

Codex CLI uses the **same skill format as Claude Code**:

```yaml
---
name: skill-name
description: What the skill does and when to use it
---

# Skill Instructions

Markdown body with patterns, examples, security guidelines, etc.
```

This means:
- All 85 Dev-AID skills work out of the box
- No conversion or adaptation needed
- Skills are maintained in one place, shared across all providers

## Verification

### Check symlinks are working

```bash
ls -la .codex/skills/
# Should show symlinks to ../../../skills/{core,expert,process}
```

### Check AGENTS.md is valid

```bash
head -30 AGENTS.md
# Should show skill references with @ syntax
```

### Test in Codex CLI

```bash
codex "list available skills"
# Should show Dev-AID skills
```

## Hooks Configuration

To enable the session-start hook, add to your Codex CLI config (`~/.codex/config.toml` or `.codex/config.toml`):

```toml
[hooks]
session_start = ".codex/hooks/session-start.sh"
```

## Troubleshooting

### "Skill file not found"

Verify symlinks are intact:
```bash
ls -la .codex/skills/expert/fastapi-expert/
# Should resolve to actual skill directory
```

If broken, recreate:
```bash
cd .codex/skills
rm -f core expert process
ln -s ../../../../.dev-aid/skills/core core
ln -s ../../../../.dev-aid/skills/expert expert
ln -s ../../../../.dev-aid/skills/process process
```

### "AGENTS.md too large"

Codex has a 32 KiB limit for AGENTS.md. If you hit this:

1. Use the session-start hook to load only relevant skills (default: top 5)
2. Reference skills individually instead of entire directories
3. Use progressive disclosure with `@file` references

### "Hook not executing"

1. Verify hook is executable: `chmod +x .codex/hooks/session-start.sh`
2. Check Codex config has hook configured
3. Run manually to check for errors: `.codex/hooks/session-start.sh`

## Trigger Phrase Coverage

The template provides natural language trigger phrases for all 26 Dev-AID commands:

| Category | Commands | Triggers |
|----------|----------|----------|
| **Agents** (8) | PR review, test gen, tech debt, CI fix, conflicts, research, onboard, doc audit | 4 trigger phrases each |
| **Teams** (4) | PR review team, security audit, architect-implement, issue resolution | 4 trigger phrases each |
| **Router** (4) | Challenger, challenger-RAG, ensemble, router status | 3-4 trigger phrases each |
| **Security** (2) | Security audit, vulnerability scan | 4 trigger phrases each |
| **Quality** (3) | Code health, debt analysis, review staged | 4 trigger phrases each |
| **Productivity** (2) | API contract, commit plan | 4 trigger phrases each |
| **Operations** (1) | Deploy validation | 4 trigger phrases |
| **Setup** (5) | Analyze, status, configure skills, build skill, update models | 4 trigger phrases each |

## Comparison with Other Providers

| Feature | Codex CLI | Claude Code | Gemini CLI |
|---------|-----------|-------------|------------|
| Context file | `AGENTS.md` | `CLAUDE.md` | `GEMINI.md` |
| Command discovery | Natural language triggers (26) | `/slash` commands (26) | `/slash` commands (26) |
| Skills directory | `.codex/skills/` | `.claude/skills/` | `.gemini/` (via refs) |
| File references | `@file` syntax | `@file` syntax | `@file` syntax |
| Hooks config | `config.toml` | `hooks.json` | `hooks.toml` |
| Skill format | YAML frontmatter + MD | YAML frontmatter + MD | YAML frontmatter + MD |

## Resources

- [Codex CLI Documentation](https://developers.openai.com/codex/cli/)
- [AGENTS.md Guide](https://developers.openai.com/codex/guides/agents-md)
- [Codex Skills Creation](https://developers.openai.com/codex/skills/create-skill)
- [Dev-AID Documentation](../../docs/)

---

**Last Updated:** 2026-02-09
**Version:** 1.1.0
**Status:** Production-ready
