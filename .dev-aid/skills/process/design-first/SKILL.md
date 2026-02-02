---
name: design-first
description: "Think before coding - explore options before committing to implementation"
risk_level: low
version: 1.0.0
domain: process/planning
enforcement: warning
token_budget: 350
triggers:
  - new_feature
  - architecture_change
  - "implement"
  - "add feature"
---

# Design-First Protocol

## 0. Core Principle

**THINK BEFORE CODING**

Exploration before implementation. Options before commitment.

---

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

---

## 2. YAGNI Enforcement

**You Aren't Gonna Need It**

Before adding any feature/capability, ask:

| Question | If "No" |
|----------|---------|
| Is this explicitly requested? | Remove it |
| Will this be used in the first release? | Defer it |
| Does removing this break requirements? | Remove it |
| Is there a simpler alternative? | Use the simpler one |

### Common YAGNI Violations

- ❌ "Future-proofing" for unspecified requirements
- ❌ Adding configuration for non-configurable features
- ❌ Abstract base classes for single implementations
- ❌ Plugin systems with only one plugin
- ❌ Database fields "we might need later"

---

## 3. Design Document Template

```markdown
## Problem Statement
[1-2 sentences describing what we're solving]

## Constraints
- [Technical constraints]
- [Business constraints]
- [Time constraints]

## Options Considered

### Option 1: [Name] (Recommended)
**How it works**: [Brief description]
**Pros**: [List]
**Cons**: [List]
**Best when**: [Conditions]

### Option 2: [Name]
**How it works**: [Brief description]
**Pros**: [List]
**Cons**: [List]
**Best when**: [Conditions]

## Decision
[Which option and why]

## Implementation Outline
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Testing Strategy
[How we'll verify this works]

## Rollback Plan
[How to undo if needed]
```

---

## 4. Integration with Dev-AID

### Memory Bank Persistence

Save approved designs to `.dev-aid/memory-bank/decisions.md`:

```markdown
## [Date] - [Feature Name]

**Context**: [Why this decision was needed]

**Decision**: [What was decided]

**Alternatives Considered**:
- [Option 2]: Rejected because [reason]
- [Option 3]: Rejected because [reason]

**Consequences**:
- [Positive consequence]
- [Trade-off accepted]
```

### Deep Research Integration

For unfamiliar domains, trigger deep research:

```bash
# Query external research
dev-aid-research search "best practices for [domain]"
dev-aid-research deep "[complex question]"
```

Research results are cached for team reuse.

---

## 5. Decision Matrix

For complex decisions with multiple factors:

| Criteria | Weight | Option 1 | Option 2 | Option 3 |
|----------|--------|----------|----------|----------|
| Simplicity | 3 | 5 | 3 | 2 |
| Performance | 2 | 3 | 5 | 4 |
| Maintainability | 3 | 4 | 3 | 2 |
| **Total** | | **35** | **31** | **22** |

Score: 1-5 (1=poor, 5=excellent)
Total = Sum(Weight × Score)

---

## 6. When to Skip Design-First

Some tasks don't need full design exploration:

- ✅ Bug fixes (use systematic-debugging instead)
- ✅ Typo fixes
- ✅ Small refactors (<50 lines)
- ✅ Adding tests for existing code
- ✅ Documentation updates

Design-first is for:
- New features
- Architecture changes
- Integration with external systems
- Performance-critical code
- Security-sensitive code

---

## 7. References

For detailed information, see:
- `references/design-templates.md` - Templates for common design patterns
