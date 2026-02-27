---
name: dev-aid-agent-lessons
description: Manage the lessons ledger — view, add, resolve, and clear agent failure patterns
category: agents
author: Dev-AID Team (https://probably.group)
version: 1.0.0
---

# Lessons Ledger

You manage the **Lessons Ledger** — a structured record of agent failure patterns that gets injected into future agent runs so they avoid repeating mistakes.

## Arguments

Parse from `$ARGUMENTS`:
- **action** (required) — one of: `list`, `add`, `resolve`, `clear-resolved`
- For `add`: `--agent <name> --failure-mode <text> --detection-signal <text> --prevention-rule <text>`
- For `resolve`: `<lesson-id> [--note <text>]`

Examples:
- `list` — show all active lessons
- `add --agent pr-reviewer --failure-mode "missed XSS" --detection-signal "no input validation check" --prevention-rule "always check user input sanitization"`
- `resolve abc12345 --note "Fixed in PR #142"`
- `clear-resolved` — remove all resolved lessons from the ledger

## How It Works

1. **Automatic recording**: When agents fail (provider errors, max iterations, DoD gate failures), lessons are auto-recorded
2. **Prompt injection**: Active lessons are injected into agent system prompts before each run
3. **Manual lessons**: You can add lessons manually for patterns you've observed
4. **Resolution**: Mark lessons as resolved once the underlying issue is fixed
5. **Cleanup**: Clear resolved lessons to keep the ledger focused

## Storage

Lessons are stored in `.dev-aid/memory-bank/lessons-ledger.md` in a structured markdown format.

## Workflow

### For `list`:
1. Read `.dev-aid/memory-bank/lessons-ledger.md`
2. Display all lessons with their ID, agent, failure mode, detection signal, prevention rule, and status
3. Highlight unresolved lessons

### For `add`:
1. Validate the provided fields
2. Add a new lesson entry to the ledger file
3. Confirm the lesson ID

### For `resolve`:
1. Find the lesson by ID
2. Mark it as resolved with an optional note
3. Confirm the resolution

### For `clear-resolved`:
1. Count resolved lessons
2. Remove them from the ledger
3. Report how many were removed

## CLI Usage

```bash
dev-aid-agent lessons list
dev-aid-agent lessons add --agent pr-reviewer --failure-mode "timeout" --detection-signal "exceeded 60s" --prevention-rule "set shorter timeout"
dev-aid-agent lessons resolve abc12345 --note "Fixed"
dev-aid-agent lessons clear-resolved
```

---

**Execute lessons command with `$ARGUMENTS`.**
