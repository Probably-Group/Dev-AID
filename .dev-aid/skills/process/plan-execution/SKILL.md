---
name: plan-execution
description: "Batch execution with checkpoints - systematic plan implementation"
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

## 9. References

For detailed information, see:
- `references/checkpoint-protocols.md` - Detailed checkpoint procedures
