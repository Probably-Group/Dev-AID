# Components Manifest - Source Mapping

**Purpose**: Lists which components to source from which repositories, plus Dev-AID native components
**Version**: 1.1.0
**Date**: 2025-12-05

This manifest maps our elite setup components to their source repositories for installation, and documents Dev-AID's native components.

---

## 🆕 Dev-AID Native Components (v1.1.0)

### Hook-Based Skill Auto-Loading System

**Location**: `.dev-aid/`

**Components**:
```
.dev-aid/
├── skills/registry/
│   └── skills-index.json              # Activation metadata for all skills
├── orchestration/
│   ├── detect-context.sh              # Project context analyzer
│   ├── select-skills.sh               # Intelligent skill selector
│   └── context-detector.py            # Project context analyzer (Python)
└── providers/
    ├── claude/.claude/hooks/
    │   └── session-start.sh           # Claude SessionStart hook
    └── gemini/.gemini/
        ├── hooks/
        │   └── session-start.sh       # Gemini SessionStart hook
        ├── settings.json              # Hook configuration
        └── GEMINI.md                  # Auto-generated (don't edit manually)
```

**Purpose**: Automatically loads relevant skills based on project context at session start

**Features**:
- Context detection from files, dependencies, tech stack
- Scoring algorithm (primary: 10pts, tech: 8pts, secondary: 5pts)
- Universal architecture for Claude, Gemini, and future providers
- GEMINI.md updated once per session (not per prompt)
- Compliance validated via [Validator Framework](VALIDATOR-FRAMEWORK.md)

**Registry Format** (`.dev-aid/skills/registry/skills-index.json`):
```json
{
  "skill-name": {
    "activation": {
      "primary_keywords": ["keyword1", "keyword2"],
      "secondary_keywords": ["keyword3"],
      "file_patterns": ["*/pattern/*"],
      "technologies": ["Tech1", "Tech2"],
      "confidence_weights": {"keyword1": 0.3},
      "requires": ["dependency-skill"],
      "exclude_with": ["conflicting-skill"]
    }
  }
}
```

**10 Initial Registry Skills**: api-expert, bash-expert, devsecops-expert, typescript-expert, fastapi-expert, graphql-expert, docker-expert, python, rust, cicd-expert

---

### Autonomous Agent Framework

**Location**: `.dev-aid/agents/`

**Components**:
```
.dev-aid/agents/
├── __init__.py                     # Public API surface
├── cli.py                          # CLI entry point (argparse subcommands)
├── core/
│   ├── models.py                   # AgentDefinition, ToolCall, ToolResult, AgentResult
│   ├── agent_runner.py             # Main agent loop (send → tool calls → execute → repeat)
│   ├── tool_registry.py            # Register/discover/execute tools, provider format export
│   ├── skill_loader.py             # Parse SKILL.md files into system prompts
│   ├── provider_adapter.py         # ProviderAdapter protocol + create_adapter() factory
│   └── safety.py                   # SafetyConfig, command blocklist, dry-run
├── adapters/
│   ├── anthropic_adapter.py        # Anthropic Messages API
│   ├── openai_adapter.py           # OpenAI + Ollama/LM Studio
│   └── google_adapter.py           # Gemini function calling
├── agents/
│   ├── pr_reviewer.py              # PR Reviewer
│   ├── test_generator.py           # Test Generator
│   ├── tech_debt_hunter.py         # Tech Debt Scanner
│   ├── ci_fixer.py                 # CI/CD Fixer
│   ├── conflict_resolver.py        # Merge Conflict Resolver
│   ├── research_agent.py           # Deep Research
│   └── onboarding_agent.py         # Codebase Onboarding
└── tools/
    ├── file_tools.py               # read_file, write_file, list_directory, glob_files
    ├── bash_tool.py                # run_bash (timeout, blocklist)
    ├── git_tools.py                # git_status, git_diff, git_log, git_add, git_commit
    ├── github_tools.py             # gh_issue_view, gh_pr_view, gh_pr_create
    └── search_tools.py             # grep_search, find_files
```

**Purpose**: Provider-agnostic autonomous AI agents powered by Dev-AID's 72+ expert skills

**Features**:
- Agent loop: send → tool calls → execute → repeat
- 7 built-in agents, 16 built-in tools
- 4 provider adapters (Anthropic, OpenAI, Google, Local)
- Safety enforcement: command blocklist, dry-run, per-tool risk levels
- Skill integration: loads SKILL.md files as system prompts
- CLI: `dev-aid-agent <agent> [options]`

**Configuration**: `.dev-aid/config/agents.json`
**CLI entry**: `.dev-aid/scripts/dev-aid-agent`
**Documentation**: [Agent Framework Guide](Dev-AID-AGENTS.md)

---

## 📦 Installation Strategy

**Foundation (Included)**:
- ✅ Configuration files (settings.json, skill-rules.json)
- ✅ Memory bank system (7 CLAUDE-*.md files)
- ✅ Essential skills (2 compact skills)
- ✅ Hooks (4 bash scripts)
- ✅ Validator Framework (shared lib + runner + 2 validators)

**To Install (Source from repos)**:
- Skills (23 additional)
- Agents (35 total)
- Commands (20 total)

---

## 🎨 SKILLS TO SOURCE (25 Total)

### From claude-code-tresor (0 skills - use agents instead)
Tresor uses agents, not skills. We'll source agents from here.

### From claude-code-infrastructure-showcase (3 skills)
**Location**: `claude-code-infrastructure-showcase/.claude/skills/`

```bash
# Copy these skills:
cp -r claude-code-infrastructure-showcase/.claude/skills/backend-dev-guidelines elite-claude-dev/.claude/skills/core/
cp -r claude-code-infrastructure-showcase/.claude/skills/frontend-dev-guidelines elite-claude-dev/.claude/skills/core/
cp -r claude-code-infrastructure-showcase/.claude/skills/skill-developer elite-claude-dev/.claude/skills/core/
```

### From claude-code-skill-factory (4 skills)
**Location**: `claude-code-skill-factory/generated-skills/`

```bash
# Copy factory skills (NOTE: agent-factory deprecated, use skill-creation-expert skill):
# cp -r claude-code-skill-factory/generated-skills/agent-factory elite-claude-dev/.claude/skills/factory/
cp -r claude-code-skill-factory/generated-skills/prompt-factory elite-claude-dev/.claude/skills/factory/
cp -r claude-code-skill-factory/generated-skills/hook-factory elite-claude-dev/.claude/skills/factory/
cp -r claude-code-skill-factory/generated-skills/slash-command-factory elite-claude-dev/.claude/skills/factory/
```

### From my-claude-code-setup (1 skill)
**Location**: `my-claude-code-setup/.claude/skills/`

```bash
# Copy claude docs skill:
cp -r my-claude-code-setup/.claude/skills/claude-docs-consultant elite-claude-dev/.claude/skills/core/
```

### From martins-ai-templates (15 skills - selective)
**Location**: `martins-ai-templates/skills/`

**Engineering (8)**:
```bash
cp -r martins-ai-templates/skills/api-expert elite-claude-dev/.claude/skills/domain/
cp -r martins-ai-templates/skills/database-design elite-claude-dev/.claude/skills/domain/
cp -r martins-ai-templates/skills/cicd-expert elite-claude-dev/.claude/skills/domain/
cp -r martins-ai-templates/skills/devsecops-expert elite-claude-dev/.claude/skills/domain/
cp -r martins-ai-templates/skills/async-expert elite-claude-dev/.claude/skills/domain/
cp -r martins-ai-templates/skills/cloud-api-integration elite-claude-dev/.claude/skills/domain/
cp -r martins-ai-templates/skills/microservices elite-claude-dev/.claude/skills/domain/ # If exists
cp -r martins-ai-templates/skills/event-driven elite-claude-dev/.claude/skills/domain/ # If exists
```

**Architecture (3)**:
```bash
cp -r martins-ai-templates/skills/design-patterns elite-claude-dev/.claude/skills/domain/ # If exists
cp -r martins-ai-templates/skills/clean-code elite-claude-dev/.claude/skills/domain/ # If exists
cp -r martins-ai-templates/skills/performance-expert elite-claude-dev/.claude/skills/domain/ # If exists
```

**Testing & Quality (2)**:
```bash
cp -r martins-ai-templates/skills/testing-expert elite-claude-dev/.claude/skills/domain/ # If exists
cp -r martins-ai-templates/skills/accessibility-wcag elite-claude-dev/.claude/skills/domain/
```

**Security (2)**:
```bash
cp -r martins-ai-templates/skills/appsec-expert elite-claude-dev/.claude/skills/security/
cp -r martins-ai-templates/skills/encryption elite-claude-dev/.claude/skills/security/
```

---

## 🤖 AGENTS TO SOURCE (35 Total)

### From claude-code-tresor (15 agents)
**Location**: `claude-code-tresor/agents/` and `claude-code-tresor/subagents/`

**Core Production (8)**:
```bash
cp claude-code-tresor/agents/config-safety-reviewer.md elite-claude-dev/.claude/agents/core/
cp claude-code-tresor/agents/test-engineer.md elite-claude-dev/.claude/agents/core/
cp claude-code-tresor/agents/docs-writer.md elite-claude-dev/.claude/agents/core/
cp claude-code-tresor/agents/systems-architect.md elite-claude-dev/.claude/agents/core/
cp claude-code-tresor/agents/root-cause-analyzer.md elite-claude-dev/.claude/agents/core/
cp claude-code-tresor/agents/security-auditor.md elite-claude-dev/.claude/agents/core/
cp claude-code-tresor/agents/performance-tuner.md elite-claude-dev/.claude/agents/core/
cp claude-code-tresor/agents/refactor-expert.md elite-claude-dev/.claude/agents/core/
```

**Domain Specialists (7 from subagents/engineering/)**:
```bash
# If subagents exist, copy:
cp claude-code-tresor/subagents/engineering/database-optimizer.md elite-claude-dev/.claude/agents/domain/
cp claude-code-tresor/subagents/engineering/frontend-performance.md elite-claude-dev/.claude/agents/domain/
cp claude-code-tresor/subagents/engineering/backend-architect.md elite-claude-dev/.claude/agents/domain/
cp claude-code-tresor/subagents/engineering/api-designer.md elite-claude-dev/.claude/agents/domain/
cp claude-code-tresor/subagents/engineering/cicd-specialist.md elite-claude-dev/.claude/agents/domain/
cp claude-code-tresor/subagents/engineering/infrastructure-security.md elite-claude-dev/.claude/agents/domain/
cp claude-code-tresor/subagents/engineering/penetration-tester.md elite-claude-dev/.claude/agents/domain/
```

### From claude-code-infrastructure-showcase (4 agents)
**Location**: `claude-code-infrastructure-showcase/.claude/agents/`

```bash
cp claude-code-infrastructure-showcase/.claude/agents/code-architecture-reviewer.md elite-claude-dev/.claude/agents/quality/
cp claude-code-infrastructure-showcase/.claude/agents/refactor-planner.md elite-claude-dev/.claude/agents/quality/
cp claude-code-infrastructure-showcase/.claude/agents/frontend-error-fixer.md elite-claude-dev/.claude/agents/quality/
cp claude-code-infrastructure-showcase/.claude/agents/web-research-specialist.md elite-claude-dev/.claude/agents/quality/
```

### From my-claude-code-setup (4 agents)
**Location**: `my-claude-code-setup/.claude/agents/`

```bash
cp my-claude-code-setup/.claude/agents/memory-bank-synchronizer.md elite-claude-dev/.claude/agents/context/
cp my-claude-code-setup/.claude/agents/code-searcher.md elite-claude-dev/.claude/agents/context/
cp my-claude-code-setup/.claude/agents/ux-design-expert.md elite-claude-dev/.claude/agents/domain/
cp my-claude-code-setup/.claude/agents/get-current-datetime.md elite-claude-dev/.claude/agents/context/
```

### From claude-code-skill-factory (4 agents)
**Location**: `claude-code-skill-factory/.claude/agents/`

```bash
cp claude-code-skill-factory/.claude/agents/factory-guide.md elite-claude-dev/.claude/agents/factory/
cp claude-code-skill-factory/.claude/agents/skills-guide.md elite-claude-dev/.claude/agents/factory/
cp claude-code-skill-factory/.claude/agents/agents-guide.md elite-claude-dev/.claude/agents/factory/
cp claude-code-skill-factory/.claude/agents/hooks-guide.md elite-claude-dev/.claude/agents/factory/
```

---

## 💬 COMMANDS TO SOURCE (20 Total)

### From claude-code-tresor (14 commands)
**Location**: `claude-code-tresor/commands/`

**Workflow (5)**:
```bash
cp -r claude-code-tresor/commands/workflow/prompt-create elite-claude-dev/.claude/commands/workflow/
cp -r claude-code-tresor/commands/workflow/prompt-run elite-claude-dev/.claude/commands/workflow/
cp -r claude-code-tresor/commands/workflow/todo-add elite-claude-dev/.claude/commands/workflow/
cp -r claude-code-tresor/commands/workflow/todo-check elite-claude-dev/.claude/commands/workflow/
cp -r claude-code-tresor/commands/workflow/handoff-create elite-claude-dev/.claude/commands/workflow/
```

**Orchestration (9)** - assuming they exist in tresor/commands/orchestration:
```bash
# Security
cp -r claude-code-tresor/commands/security/audit elite-claude-dev/.claude/commands/orchestration/
cp -r claude-code-tresor/commands/security/vulnerability-scan elite-claude-dev/.claude/commands/orchestration/
cp -r claude-code-tresor/commands/security/compliance-check elite-claude-dev/.claude/commands/orchestration/

# Performance
cp -r claude-code-tresor/commands/performance/profile elite-claude-dev/.claude/commands/orchestration/
cp -r claude-code-tresor/commands/performance/benchmark elite-claude-dev/.claude/commands/orchestration/

# Operations
cp -r claude-code-tresor/commands/operations/deploy-validate elite-claude-dev/.claude/commands/orchestration/
cp -r claude-code-tresor/commands/operations/health-check elite-claude-dev/.claude/commands/orchestration/
cp -r claude-code-tresor/commands/operations/incident-response elite-claude-dev/.claude/commands/orchestration/

# Quality
cp -r claude-code-tresor/commands/quality/code-health elite-claude-dev/.claude/commands/orchestration/
```

### From my-claude-code-setup (2 commands)
**Location**: `my-claude-code-setup/.claude/commands/`

```bash
cp -r my-claude-code-setup/.claude/commands/anthropic/update-memory-bank elite-claude-dev/.claude/commands/memory/
cp -r my-claude-code-setup/.claude/commands/cleanup/cleanup-context elite-claude-dev/.claude/commands/memory/
```

### From claude-code-skill-factory (4 commands)
**Location**: `claude-code-skill-factory/.claude/commands/`

```bash
cp -r claude-code-skill-factory/.claude/commands/build elite-claude-dev/.claude/commands/development/
cp -r claude-code-skill-factory/.claude/commands/build-skill elite-claude-dev/.claude/commands/development/
# build-agent is DEPRECATED - use /dev-aid-build-skill instead (creates skills, not agents)
# cp -r claude-code-skill-factory/.claude/commands/build-agent elite-claude-dev/.claude/commands/development/
cp -r claude-code-skill-factory/.claude/commands/validate-output elite-claude-dev/.claude/commands/development/
```

---

## 📦 INSTALLATION SCRIPT

Create `install-components.sh`:

```bash
#!/bin/bash
# Elite Claude Dev - Component Installation Script

set -e

ELITE_DIR="elite-claude-dev"
REPOS_DIR="."

echo "🚀 Installing Elite Claude Dev Components..."
echo ""

# Skills
echo "📦 Installing Skills..."
# (Copy commands from above)

# Agents
echo "🤖 Installing Agents..."
# (Copy commands from above)

# Commands
echo "💬 Installing Commands..."
# (Copy commands from above)

echo ""
echo "✅ Installation Complete!"
echo ""
echo "📊 Component Summary:"
echo "  - Skills: 25 installed"
echo "  - Agents: 35 installed"
echo "  - Commands: 20 installed"
echo ""
echo "🎯 Next Steps:"
echo "  1. Review: elite-claude-dev/README.md"
echo "  2. Configure: .claude/settings.json"
echo "  3. Test: Start Claude Code in elite-claude-dev/"
echo ""
```

---

## 🔄 UPDATE STRATEGY

**When to update components**:
- Monthly: Check source repos for updates
- After major releases: Review changelogs
- When issues found: Update specific components

**How to update**:
1. Check source repo for changes
2. Test in isolated environment
3. Update specific component
4. Validate integration

---

**Note**: This manifest assumes all referenced components exist in source repos.
Adjust paths if actual structure differs.
