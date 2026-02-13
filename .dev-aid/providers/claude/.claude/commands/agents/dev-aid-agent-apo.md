---
name: dev-aid-agent-apo
description: Automatic Prompt Optimization — optimize, rollback, and manage agent prompts
category: agents
author: Dev-AID Team (https://probably.group)
version: 1.0.0
---

# Automatic Prompt Optimization (APO)

You are managing the APO system for Dev-AID agents. APO analyzes agent execution traces and uses LLM-driven critique + beam search to improve agent system prompts.

## Arguments

Parse from `$ARGUMENTS`:
- **action** (required) — one of: `optimize`, `rollback`, `history`, `status`
- **agent name** (required for optimize/rollback/history) — the agent to operate on
- **options** — `--beam-width N`, `--dry-run`, `--version N`

If no action is provided, show available actions.

## Workflow

### For `optimize <agent-name>`

1. Check that the agent has sufficient traces (minimum 5 runs with `--trace` flag)
2. Run the APO pipeline:
   ```bash
   cd <project-root>
   python -m .dev-aid.agents.cli apo optimize <agent-name> [--beam-width 3] [--dry-run]
   ```
3. The pipeline will:
   - Analyze recent execution traces
   - Generate a critique of the current prompt
   - Create candidate improved prompts (beam search)
   - Score candidates against golden test cases
   - Show a unified diff for human approval
4. If approved, the new prompt is saved and activated

### For `rollback <agent-name>`

```bash
python -m .dev-aid.agents.cli apo rollback <agent-name> [--version N]
```

Restores the previous (or specified) prompt version.

### For `history <agent-name>`

```bash
python -m .dev-aid.agents.cli apo history <agent-name>
```

Shows all prompt versions with scores and sources.

### For `status`

```bash
python -m .dev-aid.agents.cli apo status
```

Shows APO status across all agents (trace counts, current versions, scores).

## Safety

- **Human approval required** — No prompt changes are applied without explicit user confirmation
- **Version history** — Every prompt version is preserved; rollback is always available
- **Golden tests** — Candidates are scored against predefined test cases before presentation
- **Non-destructive** — Original agent prompts in code are never modified

## Output Format

Present results clearly with:
- Current vs proposed prompt diff (for optimize)
- Score comparison (old → new)
- Version history table (for history)
- Per-agent status summary (for status)
