## 3. Implementation Workflow

### Phase 1: Context Deep Dive

**Objective**: Understand the existing system thoroughly before reviewing the plan

**Actions**:
1. **Read Plan Document Completely**
   - Identify all components mentioned
   - Note proposed changes and their scope
   - Extract success criteria
   - List all technologies, APIs, libraries referenced

2. **Examine Existing Architecture**
   - Read `CLAUDE.md`, `README.md`, architecture docs
   - Check current tech stack and versions (`package.json`, `requirements.txt`, `Cargo.toml`)
   - Identify existing patterns (auth, error handling, database access)
   - Note coding conventions and style

3. **Analyze Current Implementations**
   - Search for similar existing features (Grep/Glob)
   - Review how comparable problems were solved
   - Identify reusable patterns and components
   - Note deviations from plan approach

4. **Identify Constraints**
   - Technical: Required libraries, framework versions, infrastructure
   - Business: Timeline, budget, team expertise
   - Security: Compliance requirements, data sensitivity
   - Operational: Deployment process, monitoring capabilities

**Validation**: Can you answer "How does the current system handle X?" for every component in the plan?

---

### Phase 2: Plan Deconstruction

**Objective**: Break down the plan systematically to identify structure and dependencies

**Actions**:
1. **Map All Components**
   - List every proposed component, file, configuration
   - Identify new vs modified vs deleted items
   - Note affected existing components

2. **Analyze Step Dependencies**
   - Order steps chronologically
   - Identify dependencies (Step B requires Step A)
   - Check for circular dependencies
   - Verify logical ordering

3. **Extract Success Criteria**
   - Are success criteria defined?
   - Are they measurable and testable?
   - Do they cover functional and non-functional requirements?

4. **Identify Implicit Steps**
   - Database migrations mentioned but not migration code?
   - API integration mentioned but not error handling?
   - New dependencies added but not version pinning?

**Validation**: Can you draw a dependency graph of all steps and components?

---

### Phase 3: Research & Verification

**Objective**: Verify every technology, API, and claim in the plan with authoritative sources

**Actions**:
1. **Verify API Availability**
   - Check official API documentation
   - Confirm endpoints exist in current stable version
   - Verify authentication methods supported
   - Check rate limits and quotas
   - Note deprecation warnings

2. **Check Library Compatibility**
   - Verify library versions exist (npm, PyPI, crates.io)
   - Check compatibility with current framework version
   - Review changelog for breaking changes
   - Identify peer dependency conflicts
   - Check license compatibility

3. **Research Known Issues**
   - Search GitHub issues for mentioned libraries
   - Check CVE databases for security vulnerabilities
   - Review Stack Overflow for common gotchas
   - Read release notes for recent versions

4. **Validate Configuration Options**
   - Verify config options exist in official docs
   - Check default values
   - Note required vs optional settings
   - Identify deprecated config patterns

**Validation**: Every technology claim has a link to official documentation

---

### Phase 4: Gap Analysis (9 Critical Areas)

**Objective**: Identify missing considerations in each critical area

**1. Authentication/Authorization**
- [ ] Token validation logic specified?
- [ ] Refresh token strategy defined?
- [ ] Session management approach documented?
- [ ] Authorization rules explicit?
- [ ] Compatibility with existing auth system verified?
- [ ] Multi-tenancy considerations (if applicable)?

**2. Database Operations**
- [ ] Migration up/down scripts included?
- [ ] Indexes defined for query patterns?
- [ ] Foreign key constraints specified?
- [ ] Data validation rules documented?
- [ ] Rollback plan for failed migration?
- [ ] Performance impact assessed (table size, lock duration)?

**3. API Integrations**
- [ ] Authentication method specified and verified?
- [ ] Rate limiting strategy defined?
- [ ] Error handling for all error codes?
- [ ] Timeout configuration specified?
- [ ] Retry logic with exponential backoff?
- [ ] Circuit breaker pattern considered?

**4. Type Safety**
- [ ] TypeScript types defined for new data structures?
- [ ] Null/undefined handling explicit?
- [ ] Type guards for runtime validation?
- [ ] API response types match documentation?

**5. Error Handling**
- [ ] Error scenarios identified?
- [ ] Logging strategy defined (what, where, when)?
- [ ] User-facing error messages planned?
- [ ] Graceful degradation for non-critical failures?
- [ ] Error monitoring and alerting?

**6. Performance**
- [ ] Scalability considered (1K users → 100K users)?
- [ ] Caching strategy defined?
- [ ] N+1 query prevention addressed?
- [ ] Pagination for large result sets?
- [ ] Query optimization plan?
- [ ] Load testing planned?

**7. Security**
- [ ] Input validation for all user data?
- [ ] SQL injection prevention?
- [ ] XSS prevention?
- [ ] CSRF protection (if web app)?
- [ ] Authorization checks at API and database level?
- [ ] Sensitive data encryption?
- [ ] Secrets management (no hardcoded keys)?

**8. Testing Strategy**
- [ ] Unit tests identified?
- [ ] Integration tests planned?
- [ ] E2E tests specified?
- [ ] Mocking strategy for external dependencies?
- [ ] Test data generation plan?
- [ ] Coverage targets defined?

**9. Rollback Plan**
- [ ] Rollback triggers identified (what indicates failure)?
- [ ] Rollback steps documented?
- [ ] Database rollback tested?
- [ ] Feature flags for gradual rollout?
- [ ] Monitoring and metrics defined?

**Validation**: Each of 9 areas has at least 3 specific checks

---

### Phase 5: Impact Analysis

**Objective**: Consider broader implications beyond immediate changes

**Actions**:
1. **Performance Impact**
   - Effect on existing feature response times
   - Database query performance degradation
   - Memory/CPU usage increase
   - Infrastructure scaling needs

2. **Security Impact**
   - New attack vectors introduced
   - Expanded attack surface
   - New authorization points needed
   - Data protection requirements

3. **User Experience Impact**
   - Breaking changes to existing APIs
   - Backward compatibility requirements
   - Error message quality
   - Migration path for existing users

4. **Operational Impact**
   - New infrastructure requirements
   - Monitoring and alerting needs
   - Deployment process changes
   - On-call burden increase

**Validation**: Impact assessment covers performance, security, UX, and operations

---

### Phase 6: Generate Review Report

**Objective**: Create comprehensive, actionable review report

**Report Structure**:

```markdown
# [Plan Name] Review - [YYYY-MM-DD]

## Executive Summary
**Overall Assessment**: [Ready to Implement | Needs Revisions | Significant Issues]

**Key Findings**:
- [3-5 bullet points summarizing main issues/recommendations]

**Recommendation**: [Approve | Approve with Conditions | Request Revisions | Reject]

---

## Critical Issues (Show-stoppers)

| Severity | Category | Issue | Impact | Recommendation |
|----------|----------|-------|--------|----------------|
| Critical | Security | [Specific issue] | [Concrete impact] | [Actionable fix] |

---

## Missing Considerations

### [Category Name]
**What's Missing**: [Specific gap]
**Why It Matters**: [Concrete risk/impact]
**Recommendation**: [Specific addition needed]

---

## Alternative Approaches

### Alternative 1: [Name]
**Description**: [How it works]
**Advantages**: [Specific benefits]
**Disadvantages**: [Specific drawbacks]
**When to Use**: [Conditions favoring this approach]

---

## Research Findings

### [Technology/API Name]
**Documentation**: [Official docs link]
**Version Compatibility**: [Compatible versions]
**Known Issues**: [Link to issues/CVEs]
**Recommendation**: [Use version X.Y.Z, avoid pattern Z]

---

## Detailed Analysis by Component

### [Component Name]
**Current State**: [How it works now]
**Proposed Changes**: [What plan suggests]
**Assessment**: [Analysis with specific concerns]
**Risks**: [Concrete risks with likelihood]
**Recommendations**: [Specific improvements]

---

## Implementation Recommendations

**Must Have** (Critical for success):
- [Specific requirement]

**Should Have** (Important but not blocking):
- [Specific requirement]

**Nice to Have** (Quality improvements):
- [Specific requirement]

---

## Risk Assessment & Mitigation

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|-----------|---------|-------------------|
| [Specific risk] | High/Medium/Low | High/Medium/Low | [Concrete mitigation] |

---

## Testing Recommendations

**Unit Tests**:
- [ ] [Specific test case]

**Integration Tests**:
- [ ] [Specific test scenario]

**E2E Tests**:
- [ ] [Specific user workflow]

---

## Rollback Strategy

**Pre-Implementation Checklist**:
- [ ] [Verification step]

**Rollback Triggers** (When to roll back):
- [Specific metric or failure condition]

**Rollback Steps**:
1. [Specific action]

---

## Questions for the Team

1. [Specific clarification needed]

---

## Approval Checklist

- [ ] All critical issues resolved
- [ ] Research findings addressed
- [ ] Testing strategy defined
- [ ] Rollback plan documented
- [ ] Security review completed
- [ ] Performance impact assessed

---

**Reviewer**: Plan Review Expert (Dev-AID)
**Review Date**: [YYYY-MM-DD]
**Plan Version**: [Version if applicable]
```

**Save Location**: `/documentation/reviews/[plan-name]-review-YYYY-MM-DD.md`

---

### Phase 7: Clarification & Iteration

**Objective**: Answer team questions and refine review

**Actions**:
1. Ask clarifying questions:
   - Where is the plan document?
   - What is the scope of changes?
   - Are there specific concerns?
   - What is the timeline?
   - Are there non-negotiable constraints?

2. Iterate on feedback:
   - Address team responses
   - Re-research based on new information
   - Update recommendations
   - Add missing context

**Validation**: All team questions answered with concrete recommendations


