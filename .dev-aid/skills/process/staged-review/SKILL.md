---
name: staged-review
description: "Two-stage review: spec compliance first, then code quality"
risk_level: low
version: 1.0.0
domain: process/quality
enforcement: warning
token_budget: 400
triggers:
  - pr_review
  - code_complete
  - "review"
---

# Staged Review Protocol

## 0. Core Principle

**TWO STAGES: SPEC FIRST, QUALITY SECOND**

Don't waste time on code quality for code that doesn't meet requirements.

---

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

---

## 2. Challenger Mode Integration

When configured, run both stages with cross-model verification:

```
┌─────────────────────────────────────────────────────────┐
│ Stage 1: Spec Compliance                                │
│ ├── Claude reviews against spec                         │
│ ├── Gemini validates findings                           │
│ └── Disagreements → flag for human review               │
├─────────────────────────────────────────────────────────┤
│ Stage 2: Code Quality                                   │
│ ├── Claude checks architecture/code quality             │
│ ├── Gemini checks security/performance                  │
│ └── Combined findings presented                         │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Response Protocol

### Receiving Review Feedback

**Forbidden Responses:**
- ❌ "You're absolutely right!"
- ❌ "Great catch!"
- ❌ "Thanks for pointing that out!"
- ❌ Any performative agreement

**Required Responses:**
- ✅ "Fixed." + brief description of change
- ✅ "Addressed in [commit/line]"
- ✅ Technical pushback with evidence if disagreeing

### Giving Review Feedback

**Format:**
```
[SEVERITY] [CATEGORY]: [Issue]
Location: [file:line]
Why: [Brief explanation]
Fix: [Suggested fix or direction]
```

**Severity Levels:**
| Level | Meaning | Action Required |
|-------|---------|-----------------|
| BLOCKER | Breaks functionality or security | Must fix before merge |
| MAJOR | Significant issue | Should fix before merge |
| MINOR | Small improvement | Nice to have |
| NITPICK | Style/preference | Optional |

---

## 4. Security Integration

### Automatic Security Checks

Before Stage 2 begins, automatically run:

```bash
# Secrets detection
gitleaks detect --source . --no-git

# SAST scanning
opengrep scan

# Dependency vulnerabilities (if lockfile changed)
trivy fs .
```

### Security Review Checklist

| Category | Checks |
|----------|--------|
| Input Validation | All user input validated, sanitized |
| Authentication | Auth required where needed |
| Authorization | Permissions checked correctly |
| Data Protection | Sensitive data encrypted, not logged |
| SQL Injection | Parameterized queries only |
| XSS | Output properly escaped |
| CSRF | Tokens validated for state-changing ops |

---

## 5. Review Categories

### Stage 1 Categories

| Category | What to Check |
|----------|---------------|
| **Completeness** | All requirements implemented |
| **Correctness** | Behavior matches spec |
| **Scope** | No unauthorized changes |
| **Edge Cases** | Spec-defined edge cases handled |

### Stage 2 Categories

| Category | What to Check |
|----------|---------------|
| **Architecture** | Design patterns, SOLID, separation |
| **Code Quality** | Readability, naming, complexity |
| **Performance** | No obvious bottlenecks |
| **Security** | OWASP Top 10, input validation |
| **Testing** | Coverage, test quality |
| **Documentation** | API docs, comments where needed |

---

## 6. PR Size Guidelines

| Lines Changed | Review Time | Recommendation |
|---------------|-------------|----------------|
| < 200 | 15-30 min | Ideal |
| 200-400 | 30-60 min | Acceptable |
| 400-800 | 1-2 hours | Consider splitting |
| > 800 | 2+ hours | Split required |

Large PRs should be split into:
- Refactoring (no behavior change)
- Feature implementation
- Tests
- Documentation

---

## 7. Metrics

Track review effectiveness:

- Issues found in Stage 1 vs Stage 2
- Time spent per stage
- Issues caught before production
- Review turnaround time

---

## 8. References

For detailed information, see:
- `references/review-checklists.md` - Detailed checklists by category
