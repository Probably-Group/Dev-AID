# Architecture Decision Records (ADRs)

**Purpose**: Document architectural decisions so AI assistants understand WHY things are built this way
**Used by**: Claude, Gemini, Cursor, and other AI coding assistants
**Update**: When significant technical decisions are made

---

## How to Use This File

AI assistants should:
1. **Read before suggesting changes** - Understand existing decisions
2. **Respect decisions** - Don't suggest alternatives to accepted decisions
3. **Reference when relevant** - Cite ADRs when explaining code structure
4. **Suggest updates** - If a decision should be revisited, note it

---

## ADR Template

```markdown
## ADR-XXX: [Title]

**Date**: YYYY-MM-DD
**Status**: Proposed | Accepted | Deprecated | Superseded by ADR-XXX

### Context
What is the issue or requirement?

### Decision
What did we decide?

### Alternatives Considered
What else was considered and why rejected?

### Consequences
- **Positive**: Benefits
- **Negative**: Trade-offs
- **Risks**: What could go wrong
```

---

## Decisions

### ADR-001: [Your First Decision Title]

**Date**: YYYY-MM-DD
**Status**: Accepted

#### Context
Describe the situation that required a decision.

#### Decision
We will use [X] because [Y].

#### Alternatives Considered
- **Option A**: Why rejected
- **Option B**: Why rejected

#### Consequences
- **Positive**: What we gain
- **Negative**: What we trade off

---

### ADR-002: [Add More Decisions Here]

**Date**: YYYY-MM-DD
**Status**: Accepted

#### Context
[Describe the context]

#### Decision
[What was decided]

---

## Quick Reference

| ADR | Decision | Status |
|-----|----------|--------|
| 001 | [Short description] | Accepted |
| 002 | [Short description] | Accepted |

---

**AI Instructions**: When working on this codebase:
- Check this file for relevant decisions before suggesting architectural changes
- If a suggestion conflicts with an ADR, explain the conflict
- Propose new ADRs for significant changes rather than just making them
