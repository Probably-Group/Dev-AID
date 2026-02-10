---
name: plan-execution
description: "Executes multi-step plans in batches of 3-7 tasks with verification checkpoints and user approval gates. Key capabilities: per-task verification, blocker protocol, cost tracking, checkpoint reports, stop conditions. Use when implementing multi-step implementation plans, executing approved designs. Do NOT use for single-step tasks, quick fixes, or exploratory work."
risk_level: low
version: 1.0.0
domain: process/workflow
enforcement: warning
token_budget: 350
triggers:
  - plan_file
  - "execute plan"
  - "implement plan"
---

# Plan Execution Protocol

## 0. Core Principle

**BATCH EXECUTION WITH CHECKPOINTS**

Execute plans in small batches, verify at each checkpoint, get feedback.

---

## 1. Batch Execution (3 Tasks Default)

```
┌─────────────────────────────────────────────────────────┐
│ BATCH N                                                 │
│ ├── Task 1: Execute → Verify → Commit                   │
│ ├── Task 2: Execute → Verify → Commit                   │
│ └── Task 3: Execute → Verify → Commit                   │
├─────────────────────────────────────────────────────────┤
│ CHECKPOINT                                              │
│ ├── Report: completed, issues, next batch               │
│ ├── Cost: tokens used, API calls                        │
│ ├── Wait for feedback                                   │
│ └── Apply feedback before continuing                    │
├─────────────────────────────────────────────────────────┤
│ BATCH N+1 (only after approval)                         │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Task Execution Flow

### Per-Task Workflow

```
┌─────────────────────────────────────────────────────────┐
│ 1. Mark task IN_PROGRESS                                │
│    → Update task list                                   │
│    → Note start time                                    │
├─────────────────────────────────────────────────────────┤
│ 2. Execute task                                         │
│    → Follow relevant process skills (TDD, etc.)         │
│    → Make atomic changes                                │
├─────────────────────────────────────────────────────────┤
│ 3. Verify completion                                    │
│    → Run verification-gate                              │
│    → Tests pass? Build succeeds?                        │
├─────────────────────────────────────────────────────────┤
│ 4. Mark task COMPLETE with evidence                     │
│    → "Tests pass: 47 passed, 0 failed"                  │
│    → Not just "Done"                                    │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Checkpoint Report Format

```markdown
## Batch N Checkpoint

### Completed
- [x] Task 1: [Brief description] ✅
  - Evidence: [Test output / Build result]
- [x] Task 2: [Brief description] ✅
  - Evidence: [Test output / Build result]
- [x] Task 3: [Brief description] ✅
  - Evidence: [Test output / Build result]

### Issues Encountered
- [Issue 1]: [Description] - [Resolution]
- None

### Cost (This Batch)
- Tokens: [X]
- Duration: [Y min]

### Next Batch
- [ ] Task 4: [Description]
- [ ] Task 5: [Description]
- [ ] Task 6: [Description]

### Questions
- [Any clarifications needed]

**Awaiting approval to continue...**
```

---

## 4. Stop Conditions

**STOP immediately when:**

| Condition | Action |
|-----------|--------|
| Hit blocker mid-batch | Report and wait |
| Plan has critical gaps | Report and wait |
| Don't understand instruction | Ask for clarification |
| Verification fails 3+ times | Report and escalate |
| Estimated cost exceeds budget | Report remaining work |

### Blocker Protocol

```
┌─────────────────────────────────────────────────────────┐
│ 1. STOP all work immediately                            │
│                                                         │
│ 2. DESCRIBE blocker specifically                        │
│    → What were you trying to do?                        │
│    → What prevented completion?                         │
│    → What information is missing?                       │
│                                                         │
│ 3. PROPOSE 2-3 solutions                                │
│    → Option A: [Description + Trade-offs]               │
│    → Option B: [Description + Trade-offs]               │
│                                                         │
│ 4. WAIT for guidance                                    │
│    → Don't guess                                        │
│    → Don't proceed with uncertainty                     │
└─────────────────────────────────────────────────────────┘
```

---

## 5. Integration with Dev-AID

### Task List Integration

Use Dev-AID task tracking:

```bash
# Create tasks from plan
TaskCreate: "Implement user authentication"
TaskCreate: "Add password validation"
TaskCreate: "Create login endpoint"

# Update status during execution
TaskUpdate: task_id=1, status=in_progress
TaskUpdate: task_id=1, status=completed

# List remaining tasks
TaskList
```

### Cost Tracking

Track per batch:
- Tokens used (input + output)
- API calls made
- Time elapsed
- Estimated remaining cost

### Verification Integration

Each task completion triggers verification-gate:
- Run appropriate tests
- Check build status
- Validate changes

---

## 6. Batch Size Configuration

| Project Size | Batch Size | Reason |
|--------------|------------|--------|
| Small (< 10 tasks) | 3 tasks | Frequent checkpoints |
| Medium (10-30 tasks) | 5 tasks | Balance feedback/progress |
| Large (> 30 tasks) | 5-7 tasks | Reduce checkpoint overhead |

Configurable in `process-skills.json`:
```json
{
  "plan-execution": {
    "defaultBatchSize": 3,
    "maxBatchSize": 7
  }
}
```

---

## 7. Plan Validation

Before starting execution, validate the plan:

```
┌─────────────────────────────────────────────────────────┐
│ Plan Validation Checklist:                              │
│                                                         │
│ □ All tasks have clear completion criteria              │
│ □ Task dependencies are explicit                        │
│ □ No tasks are ambiguous                                │
│ □ Estimated effort is reasonable                        │
│ □ Blockers are identified upfront                       │
│ □ Testing strategy is clear                             │
└─────────────────────────────────────────────────────────┘
```

If validation fails:
1. Request plan clarification
2. Do not start execution
3. Wait for updated plan

---

## 8. Metrics

Track execution effectiveness:

- Batch completion rate
- Tasks completed per batch
- Blockers per plan
- Rework rate (tasks reopened)
- Cost per task

---

## 9. Rollback Procedures

### Triggers
- A batch introduces regressions in previously passing checkpoints
- Blocker discovered mid-batch that invalidates remaining tasks
- Plan execution diverges significantly from the approved plan

### Steps
- Revert the current batch: `git revert HEAD~N..HEAD` where N is the number of commits in the batch
- Mark affected checkpoints as `[ ]` (pending) in the plan file
- Document the issue in the checkpoint report under "Issues Encountered"
- Notify the user with a blocker report before continuing

### Reset
- Return to the last successful checkpoint: identify it from the plan file and `git log`
- Re-run verification on the last checkpoint to confirm it is still valid
- Update the plan to reflect the new starting point for the next batch

### Abandon vs. Retry
- **Retry** the batch with a modified approach if the blocker has a clear workaround
- **Retry** individual tasks that failed while keeping successful ones
- **Abandon** the current plan and return to planning phase if 3+ batches fail consecutively
- **Abandon** and escalate if estimated remaining cost exceeds the budget

---

## 10. Scripts

- `scripts/checkpoint-validator.sh` — Validate checkpoint format (numbered, has description), verify evidence files for completed checkpoints, and report completion percentage

---

## 11. References

For detailed information, see:
- `references/checkpoint-protocols.md` - Detailed checkpoint procedures
