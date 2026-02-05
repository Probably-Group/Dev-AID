# Architecture Decision Records (ADRs)

**Purpose**: Document important architectural and technical decisions (team-shared)
**Note**: For personal AI notes, use Claude's built-in memory (`~/.claude/projects/*/memory/`)

---

## ADR Format

Each decision follows this structure:
- **Date**: When decided
- **Status**: Proposed | Accepted | Deprecated | Superseded
- **Context**: Why we needed to decide
- **Decision**: What we chose
- **Alternatives**: What else we considered
- **Consequences**: Impacts (positive and negative)

---

## ADR-001: [Decision Title]

**Date**: YYYY-MM-DD
**Status**: Accepted
**Deciders**: [Who decided]

### Context
Why did we need to make this decision?
- Problem statement
- Constraints
- Requirements

### Decision
What did we choose?

**Implementation**:
```
Technical details
```

### Alternatives Considered

**Option A**: Description
- Pros: X
- Cons: Y
- Why rejected: Z

**Option B**: Description
- Pros: X
- Cons: Y
- Why rejected: Z

### Consequences

**Positive**:
- Benefit 1
- Benefit 2

**Negative**:
- Trade-off 1
- Trade-off 2

**Risks**:
- Risk 1 and mitigation
- Risk 2 and mitigation

---

## Template for New ADRs

```markdown
## ADR-XXX: [Title]

**Date**: YYYY-MM-DD
**Status**: Proposed | Accepted | Deprecated

### Context
Problem and constraints

### Decision
What we chose

### Alternatives
Options considered and why rejected

### Consequences
Positive, negative, risks, mitigations
```

---

**Usage**: Add new ADR when making significant technical decisions.
This file is committed to git and shared with the team.
