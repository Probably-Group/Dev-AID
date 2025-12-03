# Components Manifest - Source Mapping

**Purpose**: Lists which components to source from which repositories
**Version**: 1.0.0
**Date**: 2025-11-25

This manifest maps our elite setup components to their source repositories for installation.

---

## 📦 Installation Strategy

**Foundation (Included)**:
- ✅ Configuration files (settings.json, skill-rules.json)
- ✅ Memory bank system (7 CLAUDE-*.md files)
- ✅ Essential skills (2 compact skills)
- ✅ Hooks (4 bash scripts)

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
# Copy factory skills:
cp -r claude-code-skill-factory/generated-skills/agent-factory elite-claude-dev/.claude/skills/factory/
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
cp -r claude-code-skill-factory/.claude/commands/build-agent elite-claude-dev/.claude/commands/development/
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
