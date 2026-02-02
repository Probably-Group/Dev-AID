# Design Templates

Templates for common design patterns and decisions.

## API Design Template

```markdown
## API: [Endpoint Name]

### Overview
[Brief description of what this API does]

### Endpoint
`[METHOD] /api/v1/[path]`

### Request
```json
{
  "field1": "type (required/optional) - description",
  "field2": "type (required/optional) - description"
}
```

### Response
```json
{
  "data": { ... },
  "meta": { ... }
}
```

### Error Responses
| Status | Code | Description |
|--------|------|-------------|
| 400 | INVALID_INPUT | [When this occurs] |
| 401 | UNAUTHORIZED | [When this occurs] |
| 404 | NOT_FOUND | [When this occurs] |

### Authentication
[Auth requirements]

### Rate Limiting
[Limits if applicable]

### Example
```bash
curl -X POST /api/v1/[path] \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"field1": "value"}'
```
```

---

## Database Schema Template

```markdown
## Table: [table_name]

### Purpose
[What this table stores and why]

### Columns
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK | Primary identifier |
| [col1] | [type] | [constraints] | [description] |
| created_at | TIMESTAMP | NOT NULL | Creation timestamp |
| updated_at | TIMESTAMP | NOT NULL | Last update timestamp |

### Indexes
| Name | Columns | Type | Purpose |
|------|---------|------|---------|
| idx_[name] | [columns] | [btree/hash/gin] | [why needed] |

### Foreign Keys
| Column | References | On Delete |
|--------|------------|-----------|
| [col] | [table.col] | [CASCADE/SET NULL/RESTRICT] |

### Constraints
- [Constraint description]

### Notes
- [Performance considerations]
- [Data integrity rules]
```

---

## Component Architecture Template

```markdown
## Component: [Name]

### Responsibility
[Single responsibility of this component]

### Interface
```typescript
interface [Name] {
  // Public methods
  method1(param: Type): ReturnType;
  method2(param: Type): Promise<ReturnType>;
}
```

### Dependencies
- [Dependency 1]: [Why needed]
- [Dependency 2]: [Why needed]

### State
[What state this component manages, if any]

### Events
| Event | Payload | When Emitted |
|-------|---------|--------------|
| [event] | [type] | [trigger] |

### Error Handling
| Error | Cause | Recovery |
|-------|-------|----------|
| [error] | [cause] | [how to handle] |
```

---

## Feature Design Template

```markdown
## Feature: [Name]

### Problem Statement
[What problem does this solve for users?]

### User Stories
- As a [role], I want [capability] so that [benefit]
- As a [role], I want [capability] so that [benefit]

### Acceptance Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

### Technical Approach
[High-level description of implementation]

### Components Affected
- [Component 1]: [Changes needed]
- [Component 2]: [Changes needed]

### Data Model Changes
[New tables/columns/migrations needed]

### API Changes
[New endpoints or modifications]

### Security Considerations
- [Security concern 1]
- [Security concern 2]

### Testing Strategy
- Unit tests: [What to test]
- Integration tests: [What to test]
- E2E tests: [What to test]

### Rollout Plan
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Metrics
[How we'll measure success]
```

---

## Integration Design Template

```markdown
## Integration: [External System Name]

### Overview
[What this integration does]

### Authentication
[How we authenticate with the external system]

### Data Flow
```
[Your System] → [Transform] → [External API]
[External API] → [Transform] → [Your System]
```

### Endpoints Used
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/... | GET | [purpose] |

### Rate Limits
[External system's rate limits]

### Error Handling
| Error | Meaning | Our Response |
|-------|---------|--------------|
| 429 | Rate limited | Retry with backoff |
| 503 | Service unavailable | Queue for retry |

### Data Mapping
| Our Field | Their Field | Transform |
|-----------|-------------|-----------|
| user_id | userId | Direct |
| created_at | createdAt | ISO8601 → Unix |

### Circuit Breaker
[When to stop calling the external system]

### Fallback
[What to do when external system is unavailable]
```

---

## Migration Design Template

```markdown
## Migration: [Description]

### Current State
[How the system works now]

### Target State
[How the system will work after]

### Migration Steps
1. [Step 1]
   - Reversible: Yes/No
   - Downtime: None/Brief/Extended
2. [Step 2]
3. [Step 3]

### Rollback Plan
1. [Rollback step 1]
2. [Rollback step 2]

### Data Migration
[How existing data will be transformed]

### Compatibility Period
[How long both old and new will work together]

### Verification
[How to verify migration succeeded]

### Timeline
| Phase | Duration | Activities |
|-------|----------|------------|
| Preparation | [time] | [activities] |
| Migration | [time] | [activities] |
| Verification | [time] | [activities] |
| Cleanup | [time] | [activities] |
```

---

## Performance Design Template

```markdown
## Performance: [Feature/Component]

### Current Performance
- [Metric]: [Current value]
- [Metric]: [Current value]

### Target Performance
- [Metric]: [Target value]
- [Metric]: [Target value]

### Bottleneck Analysis
[What's causing performance issues]

### Optimization Options

#### Option 1: [Name]
- Approach: [Description]
- Expected improvement: [%]
- Trade-offs: [List]
- Effort: [Low/Medium/High]

#### Option 2: [Name]
- Approach: [Description]
- Expected improvement: [%]
- Trade-offs: [List]
- Effort: [Low/Medium/High]

### Caching Strategy
[What to cache, where, for how long]

### Database Optimization
[Indexes, query optimization, denormalization]

### Measurement Plan
[How we'll verify improvements]
```

---

## Security Design Template

```markdown
## Security: [Feature/System]

### Threat Model
| Threat | Impact | Likelihood | Mitigation |
|--------|--------|------------|------------|
| [threat] | [H/M/L] | [H/M/L] | [mitigation] |

### Authentication
[How users/systems authenticate]

### Authorization
[How permissions are checked]

### Data Protection
- At rest: [Encryption method]
- In transit: [TLS version, etc.]

### Input Validation
[What inputs are validated, how]

### Audit Logging
[What security events are logged]

### Compliance
[Relevant compliance requirements: GDPR, HIPAA, etc.]

### Security Testing
- [ ] SAST (static analysis)
- [ ] DAST (dynamic analysis)
- [ ] Dependency scanning
- [ ] Penetration testing
```
