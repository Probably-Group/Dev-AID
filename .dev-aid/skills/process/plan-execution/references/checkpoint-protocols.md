# Checkpoint Protocols

Detailed procedures for plan execution checkpoints.

## Checkpoint Types

### 1. Batch Checkpoint (Standard)

After completing each batch of tasks.

```markdown
## Batch [N] Checkpoint

### Status: [ALL_COMPLETE / PARTIAL / BLOCKED]

### Completed Tasks
| Task | Status | Evidence |
|------|--------|----------|
| [Task 1] | ✅ | Tests: 47 passed, 0 failed |
| [Task 2] | ✅ | Build: exit code 0 |
| [Task 3] | ✅ | Lint: 0 errors |

### Cost Summary
| Metric | Value |
|--------|-------|
| Tokens Used | [X] |
| Duration | [Y min] |
| Running Total | [Z tokens] |

### Next Batch Preview
1. [Task 4]: [Brief description]
2. [Task 5]: [Brief description]
3. [Task 6]: [Brief description]

### Awaiting Approval
[ ] Continue to next batch
[ ] Modify upcoming tasks
[ ] Stop and discuss
```

---

### 2. Blocker Checkpoint (Immediate)

When a blocking issue is encountered.

```markdown
## ⚠️ BLOCKER CHECKPOINT

### Current Task
[Task being attempted]

### Blocker Description
[Specific description of what's blocking]

### What I Tried
1. [Approach 1]: [Result]
2. [Approach 2]: [Result]

### Proposed Solutions

#### Option A: [Name]
- **Approach**: [Description]
- **Pros**: [List]
- **Cons**: [List]
- **Recommended**: [Yes/No]

#### Option B: [Name]
- **Approach**: [Description]
- **Pros**: [List]
- **Cons**: [List]

### Questions
1. [Specific question needing answer]

### Awaiting Guidance
I will not proceed until direction is provided.
```

---

### 3. Plan Deviation Checkpoint

When implementation diverges from original plan.

```markdown
## ⚡ PLAN DEVIATION CHECKPOINT

### Original Plan
[What the plan specified]

### Actual Implementation
[What was actually needed]

### Reason for Deviation
[Why the change was necessary]

### Impact
| Aspect | Impact |
|--------|--------|
| Scope | [Increased/Decreased/Same] |
| Effort | [Increased/Decreased/Same] |
| Risk | [Increased/Decreased/Same] |

### Options
1. **Continue with deviation**: [Consequences]
2. **Return to original plan**: [Consequences]
3. **Update plan formally**: [New plan outline]

### Recommendation
[Which option and why]

### Awaiting Decision
```

---

### 4. Quality Gate Checkpoint

After critical implementation milestones.

```markdown
## 🔒 QUALITY GATE CHECKPOINT

### Milestone
[What was completed]

### Quality Checks

#### Tests
| Suite | Passed | Failed | Coverage |
|-------|--------|--------|----------|
| Unit | [X] | [Y] | [Z%] |
| Integration | [X] | [Y] | [Z%] |
| E2E | [X] | [Y] | N/A |

#### Security
| Tool | Findings |
|------|----------|
| Gitleaks | [X findings] |
| Opengrep | [X findings] |
| Trivy | [X findings] |

#### Code Quality
| Metric | Value | Threshold |
|--------|-------|-----------|
| Lint Errors | [X] | 0 |
| Type Errors | [X] | 0 |
| Complexity | [X] | < 10 |

### Gate Status
[ ] PASS - All checks pass
[ ] WARN - Non-critical issues
[ ] FAIL - Critical issues found

### Issues (if any)
[List of issues requiring attention]

### Awaiting Approval
[ ] Proceed despite warnings
[ ] Fix issues first
[ ] Discuss approach
```

---

### 5. Completion Checkpoint (Final)

At plan completion.

```markdown
## ✅ PLAN COMPLETION CHECKPOINT

### Plan Summary
| Metric | Value |
|--------|-------|
| Total Tasks | [X] |
| Completed | [Y] |
| Deferred | [Z] |
| Duration | [Time] |
| Total Cost | [Tokens] |

### Deliverables
| Deliverable | Status | Evidence |
|-------------|--------|----------|
| [Item 1] | ✅ | [Link/Description] |
| [Item 2] | ✅ | [Link/Description] |

### Quality Summary
- Tests: [X passed, Y failed]
- Coverage: [Z%]
- Security: [No critical findings]
- Performance: [Within thresholds]

### Deviations from Plan
| Planned | Actual | Reason |
|---------|--------|--------|
| [X] | [Y] | [Why] |

### Lessons Learned
1. [Lesson 1]
2. [Lesson 2]

### Follow-up Items
- [ ] [Item 1]
- [ ] [Item 2]

### Ready for Review
All planned work complete. Awaiting final review.
```

---

## Checkpoint Communication

### Principles

1. **Be Specific**: Numbers, not qualifiers ("47 tests pass" not "tests mostly pass")
2. **Be Honest**: Report actual state, not desired state
3. **Be Concise**: Key information first, details on request
4. **Be Actionable**: Clear next steps or questions

### Response Expectations

| Checkpoint Type | Expected Response Time |
|-----------------|----------------------|
| Batch | When convenient |
| Blocker | As soon as possible |
| Deviation | Before continuing |
| Quality Gate | Before next phase |
| Completion | Before closing |

---

## Escalation Protocol

### When to Escalate

1. **Technical Blocker** lasting > 30 minutes
2. **Security Finding** of HIGH or CRITICAL severity
3. **Scope Creep** > 20% estimated effort increase
4. **Dependencies** blocking multiple tasks
5. **Ambiguity** in critical requirements

### Escalation Format

```markdown
## 🚨 ESCALATION

### Severity: [LOW / MEDIUM / HIGH / CRITICAL]

### Summary
[One sentence description]

### Impact
[What this blocks]

### Attempted Resolution
[What's been tried]

### Needed From
[Person/Team]: [What's needed]

### Deadline
[When this blocks progress]
```

---

## Cost Tracking

### Per-Task Tracking

```json
{
  "task_id": "123",
  "task_name": "Implement login",
  "cost": {
    "tokens_input": 1500,
    "tokens_output": 800,
    "api_calls": 3,
    "duration_seconds": 180
  },
  "status": "completed",
  "evidence": "Tests: 12 passed, 0 failed"
}
```

### Batch Summary

```json
{
  "batch": 1,
  "tasks_completed": 3,
  "total_tokens": 6800,
  "total_duration": 540,
  "average_per_task": 2267
}
```

### Budget Monitoring

When approaching budget limits:

```markdown
## ⚠️ BUDGET ALERT

### Current Usage
- Spent: [X tokens]
- Budget: [Y tokens]
- Remaining: [Z tokens] ([%])

### Remaining Work
- Tasks: [N]
- Estimated cost: [X tokens]

### Options
1. Continue (may exceed budget)
2. Prioritize critical tasks only
3. Stop and review

### Recommendation
[Which option and why]
```
