---
name: tdd-protocol
description: "Enforce RED-GREEN-REFACTOR cycle - no production code without failing test first"
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

### 4.1 Local Search Integration
Use FAISS to find similar existing tests:
```
Search: "test + [function_name] + [similar_behavior]"
→ Show 3 most similar tests as templates
```

### 4.2 Test Templates

See `references/test-templates.md` for language-specific templates.

### 4.3 Enforcement Levels

| Level | Behavior |
|-------|----------|
| `strict` | Block any code generation until test exists |
| `warning` | Warn but allow proceeding |
| `off` | No enforcement (not recommended) |

Configure in `.dev-aid/config/process-skills.json`

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

## 7. References

For detailed information, see:
- `references/test-templates.md` - Language-specific test templates
- `references/language-patterns.md` - Framework-specific patterns
