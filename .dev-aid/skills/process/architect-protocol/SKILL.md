---
name: architect-protocol
description: "Splits complex tasks into Architect (plans, no code) and Implementer (executes plan, writes code) phases with user approval gate. Key capabilities: structured plan templates, deviation protocol, model selection per role, TDD/verification integration. Use when building complex features requiring design, multi-file changes, architecture decisions. Do NOT use for simple bug fixes, one-file changes, config tweaks, or urgent hotfixes."
risk_level: low
version: 1.0.0
domain: process/planning
enforcement: optional
token_budget: 500
triggers:
  - complex_feature
  - multi_file_change
  - architecture_decision
---

# Architect Protocol

## 0. Core Principle

**PLAN BEFORE YOU CODE**

Complex tasks benefit from separating planning from implementation. The Architect designs; the Implementer builds.

---

## 1. When to Use Architect Mode

### Recommended Triggers

| Scenario | Why Architect Mode Helps |
|----------|-------------------------|
| Multi-file changes (5+ files) | Prevents scattered, inconsistent changes |
| New feature implementation | Ensures coherent design before coding |
| Major refactoring | Maps dependencies before disrupting them |
| Architecture decisions | Documents rationale for future reference |
| Unclear requirements | Forces clarification before commitment |

### Skip Architect Mode When

- Single-file bug fixes
- Minor tweaks or config changes
- Well-defined, isolated changes
- Urgent hotfixes (but document later)

---

## 2. The Two-Agent Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                        ARCHITECT PHASE                          │
│                                                                 │
│  Model: claude-opus-4.5 (or equivalent high-reasoning model)   │
│  Task: Analyze requirements, design solution, create plan       │
│  Output: Structured implementation plan                         │
│  Constraint: NO CODE WRITING                                   │
├─────────────────────────────────────────────────────────────────┤
│                        USER APPROVAL                            │
│                                                                 │
│  User reviews the plan                                          │
│  Options: Approve / Modify / Reject                             │
├─────────────────────────────────────────────────────────────────┤
│                      IMPLEMENTER PHASE                          │
│                                                                 │
│  Model: claude-sonnet-4.5 (or equivalent fast coding model)    │
│  Task: Execute plan, write code, run tests                      │
│  Input: Approved implementation plan                            │
│  Constraint: FOLLOW PLAN (report deviations)                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Architect Phase Requirements

### 3.1 Plan Structure

The architect MUST produce a plan with these sections:

```markdown
## Summary
[1-2 sentence description of what will be built]

## Affected Files
- `path/to/file1.ts` - [what changes]
- `path/to/file2.ts` - [what changes]
- `path/to/new-file.ts` - [NEW: purpose]

## Implementation Steps
1. [First step with clear deliverable]
2. [Second step with clear deliverable]
3. [Continue...]

## Success Criteria
- [ ] [Measurable outcome 1]
- [ ] [Measurable outcome 2]
- [ ] [Tests pass]

## Risks & Mitigations
- **Risk**: [potential issue]
  - **Mitigation**: [how to handle]
```

### 3.2 Architect Constraints

The architect MUST:
- Read and understand all relevant code before planning
- Identify ALL files that will be modified
- Consider edge cases and error handling
- Define clear, verifiable success criteria
- Keep plan actionable (not vague)

The architect MUST NOT:
- Write actual implementation code
- Make assumptions without verification
- Skip reading existing code
- Leave steps ambiguous

---

## 4. Implementer Phase Requirements

### 4.1 Following the Plan

The implementer MUST:
- Read the approved plan completely before starting
- Execute steps in order (unless plan allows parallel)
- Report any necessary deviations with rationale
- Verify success criteria after implementation

### 4.2 Deviation Protocol

If the implementer discovers the plan needs changes:

```
┌─────────────────────────────────────────────────────────────────┐
│ DEVIATION DETECTED                                              │
│                                                                 │
│ 1. STOP implementation                                          │
│ 2. Document the issue:                                          │
│    - What was planned                                           │
│    - Why it doesn't work                                        │
│    - Proposed alternative                                       │
│ 3. Request user approval for deviation                          │
│ 4. Continue only after approval                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Configuration

### 5.1 Enable Architect Mode

In `.dev-aid/config/orchestration.json`:

```json
{
  "mode": "architect",
  "architect": {
    "enabled": true,
    "architect_model": "claude-opus-4.5",
    "implementer_model": "claude-sonnet-4.5"
  }
}
```

### 5.2 Manual Activation

Use the `/architect` command to activate for a single task:

```
/architect Implement user authentication with OAuth2
```

### 5.3 Model Selection

| Role | Recommended Model | Rationale |
|------|------------------|-----------|
| Architect | claude-opus-4.5 | Best reasoning for complex planning |
| Architect (budget) | gemini-2.0-pro | Good reasoning, larger context |
| Implementer | claude-sonnet-4.5 | Fast, accurate code generation |
| Implementer (budget) | claude-haiku-4 | Quick execution for simple plans |

---

## 6. Fallback Behavior

When architect mode can't be used:

| Condition | Fallback |
|-----------|----------|
| Architect model unavailable | Use solo mode with planning prompt |
| User rejects plan | Architect revises based on feedback |
| Implementation blocked | Return to architect for replanning |

---

## 7. Integration with Other Protocols

### With TDD Protocol
- Architect identifies test requirements
- Implementer writes tests first (RED)
- Implementer implements (GREEN)
- Implementer refactors (REFACTOR)

### With Verification Gate
- Implementer must verify all success criteria
- No completion claim without evidence

### With Challenger Mode
- Can run challenger on architect's plan
- Can run challenger on implementer's code

---

## 8. Metrics

Track architect mode effectiveness:
- Plan approval rate (first attempt)
- Plan deviation frequency
- Implementation success vs solo mode
- Time to completion comparison

---

## 9. Rollback Procedures

### Triggers
- Architect plan is rejected by the user after review
- Implementation reveals fundamental flaws in the plan
- Implementer reports a deviation that requires replanning

### Steps
- Archive the rejected plan: `cp PLAN.md PLAN-v1-rejected.md`
- Revert implementation changes: `git revert HEAD~N..HEAD` for commits made under the rejected plan
- Document rejection reason in the plan archive for future reference
- Return to the Architect Phase with updated constraints

### Reset
- Delete implementation artifacts from the rejected plan
- Clear the implementer's working state: `git checkout -- .` in the working directory
- Re-run the Architect Phase with feedback from the failed implementation incorporated

### Abandon vs. Retry
- **Retry** architect phase if the plan was close but missed key requirements
- **Retry** implementation with a revised plan if only specific steps were flawed
- **Abandon** architect mode and use solo mode for urgent hotfixes or trivial changes
- **Abandon** and escalate if architect and implementer models consistently disagree on feasibility

---

## 10. Scripts

- `scripts/validate-plan.sh` — Verify plan has required sections (Summary, Files, Steps, Criteria, Risks), check file references exist, and validate success criteria are measurable
