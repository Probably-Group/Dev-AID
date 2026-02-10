# Refactoring Plan

## Metadata

| Field | Value |
|-------|-------|
| **Module/Component** | [Name and path] |
| **Author** | [Name] |
| **Date** | [YYYY-MM-DD] |
| **Estimated Effort** | [S / M / L / XL] |
| **Risk Level** | [Low / Medium / High] |

---

## 1. Current State

### Description
[What the code does today and how it is structured. 2-3 sentences.]

### Pain Points
- [Specific problem 1: e.g., "God class with 800+ LOC and 15 methods"]
- [Specific problem 2: e.g., "Hard-coded dependencies prevent unit testing"]
- [Specific problem 3: e.g., "Duplicated validation logic in 4 places"]

### Current Metrics
| Metric | Value |
|--------|-------|
| Lines of Code | [N] |
| Cyclomatic Complexity (max) | [N] |
| Test Coverage | [N%] |
| Number of Direct Dependencies | [N] |

---

## 2. Target State

### Description
[What the code should look like after refactoring. 2-3 sentences.]

### Improvements
- [Improvement 1: e.g., "Split into 3 focused services, each < 200 LOC"]
- [Improvement 2: e.g., "Dependency injection via protocols for testability"]
- [Improvement 3: e.g., "Shared validation module, single source of truth"]

### Target Metrics
| Metric | Target |
|--------|--------|
| Lines of Code (per module) | [< 200] |
| Cyclomatic Complexity (max) | [< 10] |
| Test Coverage | [>= 80%] |
| Number of Direct Dependencies | [< N] |

---

## 3. Refactoring Steps

Each step should be a single, atomic commit that keeps tests green.

| Step | Description | Before | After |
|------|-------------|--------|-------|
| 1 | [Extract interface/protocol for UserRepository] | [Direct DB calls in service] | [Service depends on protocol] |
| 2 | [Extract validation to shared module] | [Duplicated in 4 files] | [Single validate_email() function] |
| 3 | [Split UserService into UserService + UserNotificationService] | [One 800-LOC class] | [Two focused classes < 300 LOC each] |
| 4 | [Replace conditional chain with strategy pattern] | [15-branch if/elif] | [Registry of strategy classes] |
| 5 | [Add missing test coverage for edge cases] | [60% coverage] | [85% coverage] |

---

## 4. Test Plan

### Before Starting
- [ ] All existing tests pass
- [ ] Coverage baseline recorded: [N%]

### At Each Step
- [ ] Run full test suite after each change
- [ ] No test regressions (same assertions, same behavior)
- [ ] Add tests for newly exposed interfaces

### After Completion
- [ ] All original tests still pass
- [ ] New tests added for extracted modules
- [ ] Coverage meets target: [>= N%]
- [ ] Manual smoke test of affected functionality

---

## 5. Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| [Behavioral regression in edge case] | [Medium] | [High] | [Add characterization tests before refactoring] |
| [Security control accidentally removed] | [Low] | [Critical] | [Audit all validation/auth checks at each step] |
| [Refactoring scope creep] | [High] | [Medium] | [Strict scope: refactoring only, no features] |
| [Merge conflicts with parallel work] | [Medium] | [Low] | [Communicate with team, small frequent merges] |

---

## 6. Rollback Plan

- **Git strategy:** Each step is a separate commit; revert individual commits if needed
- **Feature flags:** [Yes/No -- describe if applicable]
- **Rollback trigger:** [Tests fail, performance regression > N%, error rate increase]
- **Rollback steps:**
  1. [Revert to last known good commit]
  2. [Verify tests pass on reverted code]
  3. [Deploy reverted code if already released]
