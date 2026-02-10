---
name: tdd-protocol
description: "Enforces strict RED-GREEN-REFACTOR TDD cycle requiring a failing test before any production code. Key capabilities: gate enforcement (strict/warning/off), test template suggestions via FAISS, bug-fix TDD variant, rationalization detection. Use when implementing features, fixing bugs with code changes. Do NOT use for documentation, config updates, exploratory prototyping, or refactoring-only changes."
risk_level: low
version: 1.0.0
domain: process/quality
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

### 4.1 Enforcement Gate Logic

**When TDD gate is triggered (new feature/bug fix request):**

```
┌─────────────────────────────────────────────────────────────────┐
│ GATE CHECK: Is there a failing test for this change?            │
├─────────────────────────────────────────────────────────────────┤
│ 1. SCAN: Look for test files related to target code             │
│    → Pattern: *test*, *spec*, __tests__/                        │
│    → Check recent git changes for test files                    │
├─────────────────────────────────────────────────────────────────┤
│ 2. VERIFY: If test exists, has it been run and failed?          │
│    → Check test output in terminal/logs                         │
│    → Must see actual failure, not just test file exists         │
├─────────────────────────────────────────────────────────────────┤
│ 3. ENFORCE based on level:                                      │
│    → strict: BLOCK code generation, require test first          │
│    → warning: WARN but allow proceeding with reminder           │
│    → off: No enforcement                                        │
└─────────────────────────────────────────────────────────────────┘
```

**Enforcement behavior by level:**

| Level | On Implementation Request | Message |
|-------|--------------------------|---------|
| `strict` | **BLOCK** - Must write and run failing test first | "TDD Gate: Write a failing test first. I cannot generate production code until I see a test that fails for the expected reason." |
| `warning` | **WARN** - Show reminder, allow proceeding | "TDD Reminder: Consider writing a test first. Proceeding without test, but TDD improves reliability." |
| `off` | No message | - |

### 4.2 Gate Bypass Conditions

The gate allows proceeding WITHOUT test first when:
- Task is explicitly marked as "refactoring only" (no behavior change)
- Modifying existing well-tested code with high coverage
- Documentation-only changes
- Configuration changes
- User explicitly says "skip TDD for this"

### 4.3 Local Search Integration

Use FAISS to find similar existing tests:
```
Search: "test + [function_name] + [similar_behavior]"
→ Show 3 most similar tests as templates
```

### 4.4 Test Templates

See `references/test-templates.md` for language-specific templates.

### 4.5 Configuration

Configure enforcement in `.dev-aid/config/process-skills.json`:

```json
{
  "enforcement": {
    "tdd-protocol": {
      "level": "strict",     // strict | warning | off
      "autoTrigger": true,   // auto-activate on implementation requests
      "tokenBudget": 400
    }
  }
}
```

**Profiles available:**
- `strict` profile: TDD level=strict, autoTrigger=true
- `balanced` profile: TDD level=warning, autoTrigger=false
- `minimal` profile: TDD level=off

---

## 5. Bug Fix Protocol

For bug fixes, the TDD cycle is modified:

```
┌─────────────────────────────────────────────────────────┐
│ 1. REPRODUCE: Write test that fails with the bug        │
│    → Test captures exact failing scenario               │
│    → Test MUST fail before any fix attempt              │
├─────────────────────────────────────────────────────────┤
│ 2. FIX: Write minimal code to make test pass            │
│    → Single root cause fix                              │
│    → No opportunistic improvements                      │
├─────────────────────────────────────────────────────────┤
│ 3. VERIFY: Run full test suite                          │
│    → Bug reproduction test now passes                   │
│    → No other tests broke                               │
└─────────────────────────────────────────────────────────┘
```

---

## 6. Metrics

Track TDD adherence:
- Tests written before code vs. after
- Red-green-refactor cycle adherence
- Test coverage trend
- Bugs found in tested vs. untested code

---

## 7. Rollback Procedures

### Triggers
- Implementation code was written before the failing test (protocol violation)
- Refactoring broke existing tests (REFACTOR phase regression)
- Test was written to match implementation instead of specifying behavior

### Steps
- **Protocol violation**: Delete implementation code, keep only tests: `git checkout -- <impl-files>`
- **Refactor regression**: Immediately revert the refactor: `git checkout -- <changed-files>`, return to GREEN state
- **Test contamination**: Delete both test and implementation, start the RED-GREEN-REFACTOR cycle fresh
- For partial reverts: `git stash push -m "save-work"`, revert, then selectively re-apply test files only

### Reset
- Return to the last GREEN state (all tests passing): `git log --oneline` to find it
- Verify GREEN state by running the full test suite
- Begin the next RED phase from this clean GREEN state

### Abandon vs. Retry
- **Retry** the RED phase if the test was testing the wrong behavior — rewrite the test
- **Retry** with a simpler test if the original test was too complex to implement incrementally
- **Abandon** TDD for this specific change if the user explicitly requests it (`skip TDD for this`)
- **Abandon** TDD cycle and switch to test-after only for pure configuration or documentation changes

---

## 8. Scripts

- `scripts/tdd-gate.sh` — Check for failing tests before allowing implementation code, detect project type, run test framework, and verify RED phase

---

## 9. References

For detailed information, see:
- `references/test-templates.md` - Language-specific test templates
- `references/language-patterns.md` - Framework-specific patterns
