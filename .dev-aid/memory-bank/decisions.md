# Architecture Decision Records (ADRs)

**Purpose**: Document important architectural and technical decisions
**Load Strategy**: On-demand
**Update Frequency**: When significant decisions are made

---

## ADR Format

Each decision follows this structure:
- **Date**: When decided
- **Status**: Proposed | Accepted | Deprecated | Superseded
- **Context**: Why we needed to decide
- **Decision**: What we chose
- **Alternatives**: What else we considered
- **Consequences**: Impacts (positive and negative)
- **Revisit**: When to reconsider

---

## ADR-001: [Decision Title]

**Date**: 2025-11-25
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

### Implementation Notes
- File changes needed
- Migration strategy
- Rollback plan

### Revisit Criteria
We should reconsider this decision if:
- Condition 1
- Condition 2

---

## ADR-002: Database Technology Choice

**Date**: 2025-11-25
**Status**: Accepted

### Context
Need to choose database for user data, transactions, and analytics.

**Requirements**:
- ACID compliance
- Horizontal scalability
- Complex queries
- Real-time analytics

### Decision
PostgreSQL for transactional data + Redis for caching

### Alternatives Considered

**MongoDB**:
- Pros: Flexible schema, horizontal scaling
- Cons: Eventual consistency, complex transactions
- Why rejected: Need ACID guarantees

**MySQL**:
- Pros: Mature, widely supported
- Cons: JSON support weaker than Postgres
- Why rejected: Postgres has better features

### Consequences

**Positive**:
- ACID compliance ✓
- Advanced JSON support ✓
- Excellent query optimizer ✓
- Strong community ✓

**Negative**:
- Team learning curve
- More complex than simple NoSQL
- Vertical scaling limits

**Mitigation**:
- Training sessions scheduled
- Read replicas for scaling
- Connection pooling configured

### Implementation
- Files: `src/database/postgres.config.ts`
- ORM: Prisma
- Migration strategy: Prisma Migrate

---

## ADR-003: Authentication Strategy

**Date**: 2025-11-25
**Status**: Accepted

### Context
Need secure, scalable authentication for web and mobile.

**Requirements**:
- Stateless (for scalability)
- Mobile-friendly
- Refresh token rotation
- MFA support

### Decision
JWT access tokens (15 min) + HTTP-only refresh tokens (7 days)

**Details**:
- Access token: Short-lived, in memory
- Refresh token: HTTP-only cookie, secure flag
- Rotation: New refresh token on each use
- Storage: Access in memory, refresh in HTTP-only cookie

### Alternatives Considered

**Sessions**:
- Pros: Simpler, server-side revocation
- Cons: Not stateless, scaling issues
- Why rejected: Need horizontal scaling

**OAuth2 only**:
- Pros: Industry standard, third-party support
- Cons: Overkill for internal use
- Why rejected: Can add later if needed

### Consequences

**Positive**:
- Stateless (scales horizontally) ✓
- Secure (HTTP-only, short-lived) ✓
- Mobile-friendly ✓

**Negative**:
- Can't invalidate access tokens before expiry
- More complex implementation

**Mitigation**:
- Short expiry (15 min) limits damage
- Blacklist for emergency logout
- Refresh token rotation prevents replay

### Implementation
- Files: `src/auth/jwt.service.ts`, `src/auth/token.middleware.ts`
- Library: `jsonwebtoken`
- Secret rotation: Monthly (automated)

---

## ADR-004: Monorepo vs Multi-Repo

**Date**: 2025-11-25
**Status**: Accepted

### Context
Multiple services (API, frontend, mobile, admin) need to share code.

### Decision
Monorepo with workspaces (pnpm workspaces)

### Rationale
- Shared TypeScript types
- Atomic changes across services
- Unified CI/CD
- Code sharing simplified

### Consequences

**Positive**:
- Single source of truth ✓
- Easier refactoring ✓
- Shared configs ✓

**Negative**:
- Larger repo size
- Build complexity
- Permissions granularity

**Mitigation**:
- Workspace-level scripts
- Selective CI (only changed packages)
- Clear module boundaries

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

### Implementation
Technical details

### Revisit Criteria
When to reconsider
```

---

**Usage**: Add new ADR when making significant technical decisions.
Link from CLAUDE-activeContext.md when relevant to current work.
