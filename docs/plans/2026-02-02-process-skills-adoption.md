# Implementation Plan: Process Skills Adoption from Superpowers

**Date**: 2026-02-02
**Status**: Draft
**Author**: Dev-AID Enhancement Initiative

---

## Executive Summary

This plan introduces a new **process skills** category to Dev-AID, adopting and enhancing methodology patterns from the Superpowers project (42k+ GitHub stars). Unlike Dev-AID's existing expert skills (declarative knowledge), process skills are **behavioral protocols** that enforce disciplined workflows.

### Key Improvements Over Superpowers

| Superpowers Approach | Dev-AID Enhanced Approach |
|---------------------|---------------------------|
| Generic verification commands | Language-aware verification (detects pytest vs jest vs cargo test) |
| Single-model execution | Integrates with router (challenger mode for cross-model verification) |
| Manual worktree setup | Auto-creates worktree from GitHub issue |
| No cost tracking | Full cost tracking per workflow stage |
| Static debugging steps | Integrates with local search (FAISS) for pattern matching |
| No security integration | Connects to existing security tools (Gitleaks, Trivy, etc.) |

---

## Architecture Overview

### New Directory Structure

```
.dev-aid/skills/
├── core/                    # Existing (5 skills)
├── expert/                  # Existing (72 skills)
└── process/                 # NEW: Workflow enforcement skills
    ├── README.md
    ├── verification-gate/
    │   ├── SKILL.md
    │   └── references/
    │       └── language-commands.md
    ├── tdd-protocol/
    │   ├── SKILL.md
    │   └── references/
    │       ├── language-patterns.md
    │       └── test-templates.md
    ├── systematic-debugging/
    │   ├── SKILL.md
    │   └── references/
    │       └── investigation-patterns.md
    ├── isolated-development/
    │   ├── SKILL.md
    │   └── references/
    │       └── project-setup-commands.md
    ├── design-first/
    │   ├── SKILL.md
    │   └── references/
    │       └── design-templates.md
    ├── staged-review/
    │   ├── SKILL.md
    │   └── references/
    │       └── review-checklists.md
    └── plan-execution/
        ├── SKILL.md
        └── references/
            └── checkpoint-protocols.md
```

### Configuration Extension

```json
// .dev-aid/config/process-skills.json
{
  "version": "1.0.0",
  "enforcement": {
    "verification-gate": {
      "level": "strict",      // strict | warning | off
      "autoTrigger": true     // Trigger on completion claims
    },
    "tdd-protocol": {
      "level": "warning",     // Default to warning, user can enable strict
      "autoTrigger": false    // Only when user invokes TDD workflow
    },
    "systematic-debugging": {
      "level": "warning",
      "autoTrigger": true     // Trigger on error patterns
    }
  },
  "integration": {
    "useRouterChallenger": true,   // Use challenger mode for verification
    "useLocalSearch": true,         // Use FAISS for pattern matching
    "useSecurityTools": true        // Connect to existing security scanning
  }
}
```

---

## Skill Specifications

---

### 1. Verification Gate (CRITICAL)

**Purpose**: Prevent false completion claims. Every "done" must have evidence.

**Improvement over Superpowers**: Language-aware verification commands, integration with Dev-AID's test-runner core skill.

#### SKILL.md Structure

```markdown
---
name: verification-gate
version: 1.0.0
domain: process/quality
risk_level: LOW
enforcement: strict
token_budget: 300
triggers:
  - completion_claim
  - "done"
  - "fixed"
  - "implemented"
  - "finished"
---

# Verification Gate

## 0. Anti-Hallucination Protocol

### 0.1 Risk Assessment
**Risk Level**: LOW
**Key Risk**: False completion claims leading to broken code in production.

### 0.3 Enforcement Rules

**ABSOLUTE REQUIREMENT**: Evidence before claims, always.

**Forbidden Phrases** (trigger re-verification):
- "should pass" / "should work"
- "probably works" / "likely fixed"
- "Done!" / "Finished!" / "Complete!"
- "I believe this fixes..."
- "This should resolve..."

When detected → STOP → Run verification → Show evidence → Only then claim.

---

## 1. The Protocol

### 1.1 Five-Step Verification

```
┌─────────────────────────────────────────────────────────┐
│ 1. IDENTIFY what proves the claim                       │
│    → "Tests passing proves the bug is fixed"            │
├─────────────────────────────────────────────────────────┤
│ 2. RUN the verification command FRESH                   │
│    → Don't rely on cached results                       │
│    → Don't assume previous run still valid              │
├─────────────────────────────────────────────────────────┤
│ 3. READ the complete output                             │
│    → Check exit codes (0 = success)                     │
│    → Count failures/errors                              │
│    → Note warnings                                      │
├─────────────────────────────────────────────────────────┤
│ 4. VERIFY output confirms the claim                     │
│    → If not, state actual status with evidence          │
│    → Don't rationalize partial success                  │
├─────────────────────────────────────────────────────────┤
│ 5. CLAIM with evidence                                  │
│    → "Tests pass: 47 passed, 0 failed (exit code 0)"    │
│    → "Build succeeded: exit code 0, no warnings"        │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Language-Aware Commands

**Auto-detected based on project files:**

| Evidence Type | Python | TypeScript/JS | Rust | Go |
|--------------|--------|---------------|------|-----|
| Tests pass | `pytest -v` | `npm test` | `cargo test` | `go test ./...` |
| Build succeeds | `python -m py_compile` | `npm run build` | `cargo build` | `go build ./...` |
| Lint clean | `flake8 . && mypy .` | `npm run lint` | `cargo clippy` | `golangci-lint run` |
| Types valid | `mypy .` | `tsc --noEmit` | (built-in) | (built-in) |

**Detection Priority:**
1. Check `package.json` → Node.js project
2. Check `Cargo.toml` → Rust project
3. Check `go.mod` → Go project
4. Check `pyproject.toml` or `setup.py` → Python project
5. Check `requirements.txt` → Python project

### 1.3 Evidence Requirements by Task

| Task Type | Required Evidence |
|-----------|-------------------|
| Bug fix | Test that reproduced bug now passes |
| New feature | New tests + all existing tests pass |
| Refactor | All tests pass, no behavior change |
| Build fix | Build command exits 0 |
| Lint fix | Linter exits 0, 0 errors |
| Type fix | Type checker exits 0 |

---

## 2. Integration with Dev-AID

### 2.1 Router Integration
When verification runs, use **challenger mode** if configured:
- Primary model runs verification
- Secondary model confirms output interpretation
- Disagreement → re-run with human review

### 2.2 Test Runner Integration
Connect to `test-runner` core skill for automatic test execution.

### 2.3 Cost Tracking
Log verification costs separately for analytics:
- `verification_tokens_used`
- `verification_commands_run`
- `false_completion_prevented`

---

## 3. Common Evasion Patterns (Block These)

❌ "I verified mentally that..."
❌ "Based on my analysis, this should..."
❌ "The changes look correct, so..."
❌ "I'm confident this fixes..."
❌ "Testing isn't necessary because..."

**Response**: "Show me the command output."

---

## 4. Quality Metrics

Track:
- False completion attempts blocked
- Verification success rate
- Time saved from catching issues early
- Cost of verification vs. cost of bugs
```

---

### 2. TDD Protocol (HIGH)

**Purpose**: Enforce test-driven development. No code without failing test first.

**Improvement over Superpowers**: Language-specific test templates, integration with local search for finding similar tests.

#### SKILL.md Structure

```markdown
---
name: tdd-protocol
version: 1.0.0
domain: process/quality
risk_level: LOW
enforcement: warning
token_budget: 400
triggers:
  - new_feature
  - bug_fix
  - implementation_request
---

# TDD Protocol

## 0. Core Principle

**NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST**

This is not optional. This is not "when convenient." This is the protocol.

---

## 1. The Red-Green-Refactor Cycle

### Phase 1: RED (Write Failing Test)

```
┌─────────────────────────────────────────────────────────┐
│ 1. Write ONE minimal test for the required behavior     │
│    → Test the interface, not implementation details     │
│    → Name describes expected behavior                   │
├─────────────────────────────────────────────────────────┤
│ 2. Run the test suite                                   │
│    → Verify test FAILS                                  │
│    → Verify it fails for the RIGHT reason              │
│    → Not import error, not typo, not missing file       │
├─────────────────────────────────────────────────────────┤
│ 3. STOP here until you see the correct failure          │
└─────────────────────────────────────────────────────────┘
```

**Correct failure examples:**
- `AssertionError: expected 5, got None`
- `TypeError: function not defined`
- `AttributeError: 'NoneType' has no attribute 'x'`

**Wrong failures (fix these first):**
- `ImportError: No module named 'x'`
- `SyntaxError: invalid syntax`
- `FileNotFoundError`

### Phase 2: GREEN (Minimal Implementation)

```
┌─────────────────────────────────────────────────────────┐
│ 1. Write ONLY enough code to make the test pass         │
│    → Hardcode values if that makes it pass              │
│    → No "while I'm here" improvements                   │
│    → No anticipating future needs                       │
├─────────────────────────────────────────────────────────┤
│ 2. Run the test suite                                   │
│    → Verify your test PASSES                            │
│    → Verify no OTHER tests broke                        │
├─────────────────────────────────────────────────────────┤
│ 3. STOP here. Resist urge to "clean up"                 │
└─────────────────────────────────────────────────────────┘
```

### Phase 3: REFACTOR (Only When Green)

```
┌─────────────────────────────────────────────────────────┐
│ 1. Now (and only now) improve the code                  │
│    → Remove duplication                                 │
│    → Improve naming                                     │
│    → Extract functions                                  │
├─────────────────────────────────────────────────────────┤
│ 2. Run tests after EACH change                          │
│    → If tests break, revert immediately                │
│    → Don't accumulate changes                          │
├─────────────────────────────────────────────────────────┤
│ 3. Keep all tests green throughout                      │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Absolute Rules

### What You MUST Do
- ✅ Write test BEFORE implementation
- ✅ See test fail BEFORE writing code
- ✅ Verify failure is for expected reason
- ✅ Write minimal code to pass
- ✅ Run tests after every change
- ✅ Refactor only when green

### What You MUST NOT Do
- ❌ Write production code before test
- ❌ Keep code written before test (DELETE IT)
- ❌ Use pre-written code as "reference" for tests
- ❌ Add features beyond test scope
- ❌ Refactor while red
- ❌ Skip "obvious" tests

---

## 3. Rationalization Red Flags

When you think one of these, STOP:

| Rationalization | Reality |
|-----------------|---------|
| "I'll add tests after" | You won't. And you'll miss edge cases. |
| "This is too simple to test" | Simple code has simple tests. Write it. |
| "Manual testing is enough" | Manual testing doesn't prevent regression. |
| "I already know this works" | Then proving it with a test takes 30 seconds. |
| "Testing would slow me down" | Debugging untested code slows you down more. |
| "The framework handles this" | Test YOUR usage of the framework. |

**If you catch yourself rationalizing**: Delete any code written, start with the test.

---

## 4. Integration with Dev-AID

### 4.1 Local Search Integration
Use FAISS to find similar existing tests:
```
Search: "test + [function_name] + [similar_behavior]"
→ Show 3 most similar tests as templates
```

### 4.2 Test Template Generation
Based on detected language, provide starter:

**Python:**
```python
import pytest

def test_[behavior]_[scenario]():
    # Given
    [setup]

    # When
    result = [action]

    # Then
    assert result == [expected]
```

**TypeScript:**
```typescript
describe('[Feature]', () => {
  it('should [behavior] when [scenario]', () => {
    // Given
    const [setup]

    // When
    const result = [action]

    // Then
    expect(result).toBe([expected])
  })
})
```

### 4.3 Enforcement Levels

| Level | Behavior |
|-------|----------|
| `strict` | Block any code generation until test exists |
| `warning` | Warn but allow proceeding |
| `off` | No enforcement (not recommended) |

Configure in `.dev-aid/config/process-skills.json`

---

## 5. Metrics

Track:
- Tests written before code vs. after
- Red-green-refactor cycle adherence
- Test coverage trend
- Bugs found in tested vs. untested code
```

---

### 3. Systematic Debugging (HIGH)

**Purpose**: Prevent random fix attempts. Root cause first, fix second.

**Improvement over Superpowers**: Integration with local search for pattern matching, connection to existing security tools for vulnerability correlation.

#### SKILL.md Structure

```markdown
---
name: systematic-debugging
version: 1.0.0
domain: process/debugging
risk_level: LOW
enforcement: warning
token_budget: 450
triggers:
  - error_message
  - stack_trace
  - "bug"
  - "broken"
  - "not working"
  - "fails"
---

# Systematic Debugging Protocol

## 0. Core Principle

**NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST**

Symptom fixes mask underlying issues and waste time.

---

## 1. The Four-Phase Protocol

### Phase 1: Root Cause Investigation

**Complete this BEFORE attempting any fix.**

#### Step 1.1: Examine Error Thoroughly
```
┌─────────────────────────────────────────────────────────┐
│ □ Read COMPLETE stack trace (not just last line)        │
│ □ Note exact line numbers                               │
│ □ Note exact error codes/types                          │
│ □ Check for warnings BEFORE the error                   │
│ □ Look for "caused by" chains                           │
└─────────────────────────────────────────────────────────┘
```

#### Step 1.2: Establish Reproduction
```
┌─────────────────────────────────────────────────────────┐
│ □ Can you trigger the issue consistently?               │
│ □ Document exact steps to reproduce                     │
│ □ Note: specific inputs, timing, environment            │
│ □ If non-reproducible: gather more data first           │
└─────────────────────────────────────────────────────────┘
```

#### Step 1.3: Review Recent Changes
```
┌─────────────────────────────────────────────────────────┐
│ □ git diff since last working state                     │
│ □ Check dependency updates (package.json, etc.)         │
│ □ Check configuration changes                           │
│ □ Check environment differences (dev vs. prod)          │
└─────────────────────────────────────────────────────────┘
```

#### Step 1.4: Trace Data Flow (Multi-Component)
```
┌─────────────────────────────────────────────────────────┐
│ □ Log what data ENTERS the failing component            │
│ □ Log what data EXITS to next component                 │
│ □ Verify configuration propagates correctly             │
│ □ Check state at each system boundary                   │
│ □ Identify WHICH component actually fails               │
└─────────────────────────────────────────────────────────┘
```

#### Step 1.5: Find the Source
```
┌─────────────────────────────────────────────────────────┐
│ □ Trace backward from symptom to origin                 │
│ □ Follow call stack upward                              │
│ □ Find where bad values FIRST appear                    │
│ □ The bug is at the SOURCE, not where it manifests      │
└─────────────────────────────────────────────────────────┘
```

---

### Phase 2: Pattern Analysis

**Study working examples before implementing fixes.**

```
┌─────────────────────────────────────────────────────────┐
│ 1. Find similar WORKING code in codebase                │
│    → Use Dev-AID local search (FAISS)                   │
│    → Search: "[error_type] + working + [component]"     │
├─────────────────────────────────────────────────────────┤
│ 2. Read working code COMPLETELY                         │
│    → Don't skim                                         │
│    → Understand every line                              │
├─────────────────────────────────────────────────────────┤
│ 3. List ALL differences between working and broken      │
│    → Configuration                                      │
│    → Dependencies                                       │
│    → Environment                                        │
│    → Code structure                                     │
├─────────────────────────────────────────────────────────┤
│ 4. Understand assumptions in working code               │
│    → What does it expect to be true?                    │
│    → What might be different in broken context?         │
└─────────────────────────────────────────────────────────┘
```

---

### Phase 3: Hypothesis Testing

**Scientific method for fixes.**

```
┌─────────────────────────────────────────────────────────┐
│ 1. STATE hypothesis clearly                             │
│    → "I believe X causes this because Y"                │
│    → Write it down before testing                       │
├─────────────────────────────────────────────────────────┤
│ 2. TEST with ONE change                                 │
│    → Change only ONE variable                           │
│    → Multiple changes = can't know what worked          │
├─────────────────────────────────────────────────────────┤
│ 3. VERIFY before concluding                             │
│    → Run verification protocol                          │
│    → Don't assume success                               │
├─────────────────────────────────────────────────────────┤
│ 4. If wrong, NEW hypothesis                             │
│    → Don't keep tweaking same approach                  │
│    → Return to Phase 1 if needed                        │
└─────────────────────────────────────────────────────────┘
```

---

### Phase 4: Implementation

```
┌─────────────────────────────────────────────────────────┐
│ 1. Create FAILING test that reproduces the bug          │
│    → Test should fail now, pass after fix               │
├─────────────────────────────────────────────────────────┤
│ 2. Implement SINGLE root-cause fix                      │
│    → Address source, not symptom                        │
│    → One fix, not multiple "while I'm here" changes     │
├─────────────────────────────────────────────────────────┤
│ 3. Verify test now passes                               │
│    → Run full test suite                                │
│    → Check no other tests broke                         │
├─────────────────────────────────────────────────────────┤
│ 4. If 3+ fixes fail: STOP                               │
│    → Question the architecture                          │
│    → The problem may be systemic                        │
│    → Get fresh perspective                              │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Red Flags (Return to Phase 1)

| Red Flag | What It Means |
|----------|---------------|
| Proposing fix without understanding cause | You're guessing |
| Making multiple simultaneous changes | Can't know what works |
| Each fix reveals new problems | Systemic issue, not local bug |
| 3+ fix attempts failed | Wrong mental model |
| "This should definitely work" | Overconfidence, verify first |

---

## 3. Integration with Dev-AID

### 3.1 Local Search (FAISS)
```bash
# Find similar errors in codebase
dev-aid search "TypeError: cannot read property"

# Find working patterns
dev-aid search "authentication flow success"
```

### 3.2 Security Tool Correlation
When error matches security pattern:
- Check Trivy scan results
- Check Gitleaks for exposed secrets
- Cross-reference with Opengrep findings

### 3.3 Git History Analysis
```bash
# Auto-run on debugging start
git log --oneline -10
git diff HEAD~5..HEAD -- [affected_file]
```

---

## 4. Metrics

Track:
- Fix attempts per bug (target: <3)
- Root cause found before fix rate
- Regression rate (bugs that come back)
- Time: investigation vs. random fixing
```

---

### 4. Isolated Development (MEDIUM)

**Purpose**: Create clean, isolated environment per feature/issue.

**Improvement over Superpowers**: Auto-create from GitHub issue, integrate with Dev-AID issue resolver.

#### SKILL.md Structure (Abbreviated)

```markdown
---
name: isolated-development
version: 1.0.0
domain: process/workflow
risk_level: LOW
enforcement: warning
token_budget: 300
triggers:
  - new_feature
  - issue_resolution
  - "start work on"
---

# Isolated Development

## 1. Auto-Create from Issue

When user says "work on issue #123":

```
┌─────────────────────────────────────────────────────────┐
│ 1. Fetch issue details (gh issue view 123)              │
├─────────────────────────────────────────────────────────┤
│ 2. Create worktree                                      │
│    git worktree add .worktrees/issue-123 -b fix/123     │
├─────────────────────────────────────────────────────────┤
│ 3. Setup project                                        │
│    → Detect type (Node/Python/Rust/Go)                  │
│    → Run install commands                               │
├─────────────────────────────────────────────────────────┤
│ 4. Verify baseline                                      │
│    → Run test suite                                     │
│    → If fails: STOP, report, ask guidance               │
├─────────────────────────────────────────────────────────┤
│ 5. Load issue context into session                      │
│    → Issue description                                  │
│    → Related files (from issue mentions)                │
│    → Relevant expert skills                             │
└─────────────────────────────────────────────────────────┘
```

## 2. Integration with Issue Resolver

Connect to existing `dev-aid-resolve-issue`:
1. Issue analysis happens in worktree context
2. Solution implementation isolated from main
3. Easy cleanup if approach doesn't work

## 3. Cleanup Protocol

| Outcome | Action |
|---------|--------|
| Merged to main | Remove worktree |
| PR created | Keep worktree |
| Abandoned | Remove worktree (confirm first) |
| In progress | Keep worktree |
```

---

### 5. Design-First Protocol (MEDIUM)

**Purpose**: Think before coding. Explore options before committing.

**Improvement over Superpowers**: Integration with Deep Research system, memory bank for design decisions.

#### SKILL.md Structure (Abbreviated)

```markdown
---
name: design-first
version: 1.0.0
domain: process/planning
risk_level: LOW
enforcement: warning
token_budget: 350
triggers:
  - new_feature
  - architecture_change
  - "implement"
  - "add feature"
---

# Design-First Protocol

## 1. Before ANY Implementation

### Phase 1: Understanding (One Question at a Time)

```
┌─────────────────────────────────────────────────────────┐
│ Ask clarifying questions SEQUENTIALLY                   │
│ → One question per message                              │
│ → Prefer multiple choice when possible                  │
│ → Wait for answer before next question                  │
├─────────────────────────────────────────────────────────┤
│ Understand:                                             │
│ □ What problem does this solve?                         │
│ □ Who are the users?                                    │
│ □ What are the constraints? (time, tech, team)          │
│ □ What does success look like?                          │
│ □ What are the non-negotiables?                         │
└─────────────────────────────────────────────────────────┘
```

### Phase 2: Exploration (2-3 Options)

```
┌─────────────────────────────────────────────────────────┐
│ Present 2-3 different approaches                        │
│ → Lead with recommended approach                        │
│ → Explain WHY it's recommended                          │
│ → List trade-offs for each                              │
│                                                         │
│ For each approach:                                      │
│ □ How it works (brief)                                  │
│ □ Advantages                                            │
│ □ Disadvantages                                         │
│ □ When to choose this                                   │
├─────────────────────────────────────────────────────────┤
│ Apply YAGNI ruthlessly                                  │
│ → Remove features not explicitly needed                 │
│ → Question every "nice to have"                         │
│ → Simplest solution that works                          │
└─────────────────────────────────────────────────────────┘
```

### Phase 3: Validation (Chunked)

```
┌─────────────────────────────────────────────────────────┐
│ Break design into sections (200-300 words each)         │
│ After each section: "Does this match expectations?"     │
│                                                         │
│ Sections:                                               │
│ □ Architecture overview                                 │
│ □ Data flow                                             │
│ □ API/Interface design                                  │
│ □ Error handling                                        │
│ □ Testing strategy                                      │
└─────────────────────────────────────────────────────────┘
```

## 2. Integration with Dev-AID

### Memory Bank
Save approved designs to `.dev-aid/memory-bank/decisions.md`:
- Decision made
- Alternatives considered
- Why this approach chosen
- Date and context

### Deep Research
For unfamiliar domains, trigger deep research:
- Query Gemini Deep Research for best practices
- Check Perplexity for recent developments
- Cache results for team reuse
```

---

### 6. Staged Review Protocol (MEDIUM)

**Purpose**: Two-stage review (spec compliance → code quality).

**Improvement over Superpowers**: Integration with challenger mode, security-focused quality checks.

#### SKILL.md Structure (Abbreviated)

```markdown
---
name: staged-review
version: 1.0.0
domain: process/quality
risk_level: LOW
enforcement: warning
token_budget: 400
triggers:
  - pr_review
  - code_complete
  - "review"
---

# Staged Review Protocol

## 1. Two-Stage Process

### Stage 1: Spec Compliance (Required First)

```
┌─────────────────────────────────────────────────────────┐
│ Does code implement EXACTLY what was specified?         │
├─────────────────────────────────────────────────────────┤
│ Checklist:                                              │
│ □ All requirements implemented                          │
│ □ No missing functionality                              │
│ □ No extra functionality (scope creep)                  │
│ □ Behavior matches specification                        │
│ □ Edge cases from spec handled                          │
├─────────────────────────────────────────────────────────┤
│ If issues found:                                        │
│ → Fix issues                                            │
│ → Re-run Stage 1                                        │
│ → Do NOT proceed to Stage 2 until passing               │
└─────────────────────────────────────────────────────────┘
```

### Stage 2: Code Quality (Only After Stage 1 Passes)

```
┌─────────────────────────────────────────────────────────┐
│ Architecture & Design                                   │
│ □ SOLID principles followed                             │
│ □ Separation of concerns                                │
│ □ Consistent with existing patterns                     │
│ □ Appropriate abstraction level                         │
├─────────────────────────────────────────────────────────┤
│ Implementation Quality                                  │
│ □ Error handling complete                               │
│ □ Type safety maintained                                │
│ □ Defensive programming applied                         │
│ □ No code smells                                        │
├─────────────────────────────────────────────────────────┤
│ Security (Integration with Dev-AID tools)               │
│ □ Gitleaks: No secrets exposed                          │
│ □ Opengrep: No SAST findings                            │
│ □ Input validation present                              │
│ □ Authorization checks in place                         │
├─────────────────────────────────────────────────────────┤
│ Testing                                                 │
│ □ Happy path covered                                    │
│ □ Edge cases covered                                    │
│ □ Error conditions covered                              │
│ □ Coverage meets threshold                              │
└─────────────────────────────────────────────────────────┘
```

## 2. Challenger Mode Integration

When configured, run both stages with cross-model verification:
- Claude performs review
- Gemini validates findings
- Disagreements flagged for human review

## 3. Response Protocol

**Receiving review:**
- ❌ NO "You're absolutely right!"
- ❌ NO performative agreement
- ✅ "Fixed. [brief description]"
- ✅ Technical pushback with evidence if needed
```

---

### 7. Plan Execution Protocol (MEDIUM)

**Purpose**: Execute plans in batches with checkpoints.

**Improvement over Superpowers**: Integration with task tracking, cost tracking per batch.

#### SKILL.md Structure (Abbreviated)

```markdown
---
name: plan-execution
version: 1.0.0
domain: process/workflow
risk_level: LOW
enforcement: warning
token_budget: 350
triggers:
  - plan_file
  - "execute plan"
  - "implement plan"
---

# Plan Execution Protocol

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

## 2. Stop Conditions

**STOP immediately when:**
- Hit blocker mid-batch
- Plan has critical gaps
- Don't understand instruction
- Verification fails 3+ times
- Estimated cost exceeds budget

**Blocker Protocol:**
1. Stop all work
2. Describe blocker specifically
3. Propose 2-3 solutions
4. Wait for guidance (don't guess)

## 3. Integration with Dev-AID

### Cost Tracking
Track per batch:
- Tokens used
- API calls
- Time elapsed
- Estimated remaining

### Task Tracking
Use Dev-AID task list:
- Create tasks from plan
- Mark in_progress when starting
- Mark completed with evidence
```

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

| Task | Priority | Effort | Dependencies |
|------|----------|--------|--------------|
| Create `process/` directory structure | P0 | Low | None |
| Create `process-skills.json` config | P0 | Low | None |
| Implement `verification-gate` | P0 | Medium | None |
| Update skill loader to support process skills | P0 | Medium | None |
| Add language detection utility | P1 | Low | verification-gate |

### Phase 2: Core Process Skills (Week 3-4)

| Task | Priority | Effort | Dependencies |
|------|----------|--------|--------------|
| Implement `tdd-protocol` | P0 | Medium | verification-gate |
| Implement `systematic-debugging` | P0 | Medium | verification-gate |
| Integrate with local search (FAISS) | P1 | Medium | tdd, debugging |
| Add test templates per language | P1 | Low | tdd-protocol |

### Phase 3: Workflow Skills (Week 5-6)

| Task | Priority | Effort | Dependencies |
|------|----------|--------|--------------|
| Implement `isolated-development` | P1 | Medium | None |
| Integrate with `dev-aid-resolve-issue` | P1 | Medium | isolated-development |
| Implement `design-first` | P2 | Medium | None |
| Integrate with deep research | P2 | Low | design-first |

### Phase 4: Review & Execution (Week 7-8)

| Task | Priority | Effort | Dependencies |
|------|----------|--------|--------------|
| Implement `staged-review` | P1 | Medium | verification-gate |
| Integrate with challenger mode | P1 | Medium | staged-review |
| Implement `plan-execution` | P2 | Medium | verification-gate |
| Add cost tracking per workflow | P2 | Low | plan-execution |

### Phase 5: Documentation & Testing (Week 9)

| Task | Priority | Effort | Dependencies |
|------|----------|--------|--------------|
| Write comprehensive tests | P0 | High | All skills |
| Update main README | P1 | Medium | All skills |
| Create tutorial/guide | P1 | Medium | All skills |
| Dogfood on Dev-AID itself | P0 | High | All skills |

---

## Success Metrics

### Adoption Metrics
- % of sessions using process skills
- % of completions with verification evidence
- % of bugs fixed with TDD protocol

### Quality Metrics
- False completion rate (target: <5%)
- Bugs caught before commit (target: >80%)
- Fix attempts per bug (target: <3)

### Efficiency Metrics
- Time to resolution with protocol vs. without
- Cost per verified completion
- Rework rate reduction

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Process skills slow down development | Make enforcement configurable (strict/warning/off) |
| Too many tokens consumed | Keep each skill <500 tokens, load contextually |
| Users disable all process skills | Track disabled rate, gather feedback, iterate |
| Integration complexity | Implement incrementally, test each integration |

---

## Appendix: Key Differences from Superpowers

| Aspect | Superpowers | Dev-AID Enhanced |
|--------|-------------|------------------|
| Verification commands | Generic | Language-aware auto-detection |
| Model usage | Single model | Multi-model via router |
| Search capability | None | FAISS local semantic search |
| Security integration | None | Gitleaks, Trivy, Opengrep |
| Cost tracking | None | Per-workflow analytics |
| Issue integration | Manual | Auto-worktree from GitHub issue |
| Design decisions | Ephemeral | Persisted in memory bank |
| Review | Single-stage | Two-stage + challenger mode |

---

**Next Steps:**
1. Review and approve this plan
2. Create feature branch: `feature/process-skills`
3. Begin Phase 1 implementation
