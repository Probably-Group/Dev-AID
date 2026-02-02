---
name: systematic-debugging
description: "Root cause first, fix second - prevent random fix attempts"
risk_level: low
version: 1.0.0
domain: process/debugging
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

## 4. 3-Strike Rule

After 3 failed fix attempts:

```
┌─────────────────────────────────────────────────────────┐
│ STOP attempting fixes                                   │
│                                                         │
│ Consider:                                               │
│ □ Is this a systemic architecture issue?                │
│ □ Am I working with incorrect assumptions?              │
│ □ Should I ask for a fresh perspective?                 │
│ □ Is the problem definition itself wrong?               │
│                                                         │
│ Actions:                                                │
│ • Document all findings so far                          │
│ • Request architectural review                          │
│ • Consider if scope is larger than expected             │
└─────────────────────────────────────────────────────────┘
```

---

## 5. Metrics

Track debugging effectiveness:
- Fix attempts per bug (target: <3)
- Root cause found before fix rate
- Regression rate (bugs that come back)
- Time: investigation vs. random fixing

---

## 6. References

For detailed information, see:
- `references/investigation-patterns.md` - Common investigation patterns
