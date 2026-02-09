---
name: dev-aid-agent-team
description: Run multi-agent teams for complex tasks — PR review, security audit, architecture, issue resolution
category: agents
author: Dev-AID Team (https://probably.group)
version: 1.0.0
---

# Multi-Agent Team Command

You orchestrate multi-agent teams where specialized agents collaborate on complex tasks. Each team combines 2-4 agents with complementary expertise.

## Arguments

Parse from `$ARGUMENTS`:
- **Team name** (required) — which team to run (see Available Teams below)
- **`-m` or `--message`** (required) — the task message for the team
- **`--budget`** (optional) — max budget in USD (default: team-specific)
- **`--workflow`** (optional) — override workflow strategy: `parallel`, `sequential`, `dag`
- **`--list-teams`** (optional, standalone) — list all available teams

If `--list-teams` is passed, list teams and exit. Otherwise, team name and message are required.

## Available Teams

Read the team definitions from `.dev-aid/agents/teams/` directory. Each YAML file defines a team with:
- **agents**: List of agent roles with their skills and prompts
- **workflow**: Execution strategy (parallel, sequential, dag)
- **budget**: Default max budget

Common teams:
| Team | Agents | Workflow | Use Case |
|------|--------|----------|----------|
| `pr-review-team` | security-reviewer, quality-reviewer, test-coverage-reviewer | parallel | Comprehensive PR review from 3 perspectives |
| `security-audit-team` | vulnerability-scanner, config-auditor, dependency-checker | parallel | Full security audit |
| `architect-implement-team` | architect, implementer, reviewer | sequential | Design then implement then review |
| `issue-resolution-team` | analyst, implementer, tester | dag | Analyze, fix, and verify issues |

## Workflow

### Phase 1: Load Team Definition

```bash
ls .dev-aid/agents/teams/
cat .dev-aid/agents/teams/<team-name>.yaml
```

If the team doesn't exist, show available teams and exit.

### Phase 2: Execute Team

Run the team using the CLI:

```bash
cd <project-root>
.dev-aid/agents/venv/bin/python -m agents.cli team <team-name> -m "<message>" [options]
```

Or if no venv exists, guide the user to set up:
```bash
.dev-aid/scripts/setup-agents.sh
```

### Phase 3: Report Results

Display the aggregated output from all agents, including:
- Which agents ran and their individual findings
- The merged/synthesized result
- Cost breakdown (if budget tracking enabled)

## Output Format

```markdown
# Team Report: <team-name>

## Task
<original message>

## Agent Results

### <Agent 1 Name>
<findings>

### <Agent 2 Name>
<findings>

## Synthesized Result
<merged findings and recommendations>

## Cost
| Agent | Tokens | Cost |
|-------|--------|------|
| ...   | ...    | ...  |
| **Total** | ... | ... |
```

## Examples

```
/dev-aid-agent-team pr-review-team -m "Review PR #42"
/dev-aid-agent-team security-audit-team -m "Audit the auth module" --budget 5.0
/dev-aid-agent-team architect-implement-team -m "Add rate limiting to the API"
/dev-aid-agent-team --list-teams
```

---

**Execute the team command with: $ARGUMENTS**
