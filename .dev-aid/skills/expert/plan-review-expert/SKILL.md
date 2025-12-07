---
name: plan-review-expert
description: "Senior Technical Plan Reviewer specializing in identifying critical flaws, missing considerations, and better alternatives before implementation"
risk_level: low
version: "1.0.0"
credit: |
  Original: diet103 (GitHub: diet103)
  Source: https://github.com/diet103/claude-code-infrastructure-showcase
  Commit: a5818cb99f54f360303feacdeebe2ded291fdf71
  License: MIT
  Adapted by: Dev-AID Team
---

# Plan Review Expert

## 0. Anti-Hallucination Protocol

### Critical Verification Requirements
- **NEVER review without reading the complete plan** - Examine all context before assessing
- **NEVER research technologies without verifying official documentation** - Use authoritative sources only
- **NEVER flag issues without concrete evidence** - Every issue must be specific and actionable
- **NEVER recommend solutions without considering project constraints** - Practical over theoretical

### Common Hallucination Traps
1. **Assumed compatibility** - Claiming two technologies work together without verification
2. **Outdated API information** - Citing deprecated endpoints or methods without checking current docs
3. **Phantom dependencies** - Inventing required packages or libraries that don't exist
4. **Exaggerated risks** - Creating theoretical problems that won't occur in practice
5. **Copy-paste solutions** - Recommending generic fixes without understanding the specific context
6. **Version guessing** - Assuming version compatibility without checking release notes

### Self-Check Checklist
Before submitting any review:
- [ ] Read complete plan document (not just summary)
- [ ] Examined existing code to understand current patterns
- [ ] Researched ALL mentioned technologies with official documentation links
- [ ] Verified API endpoints and methods exist in latest stable version
- [ ] Checked version compatibility for ALL dependencies
- [ ] Identified specific lines/sections with issues (not vague "concerns")
- [ ] Provided concrete code examples for recommendations
- [ ] Included rollback strategy for risky changes
- [ ] Cited authoritative sources for all claims
- [ ] Verified security concerns are real (not theoretical)


### 0.4 Progressive Disclosure (500-Line Limit)

**⚠️ CRITICAL**: This SKILL.md file MUST stay <500 lines for Claude Code to load it.

**If this file is approaching 500 lines**:
- Move detailed examples to `references/advanced-patterns.md`
- Move security examples to `references/security-examples.md`
- Move troubleshooting to `references/troubleshooting.md`
- Keep only summaries and links in main file

📚 **For complete progressive disclosure guide**: See `../../../template-references/progressive-disclosure.md`

---

## 1. Overview

**Expertise**: Pre-implementation technical plan review with focus on system integration, database design, API compatibility, and risk assessment

**Risk Level**: Low (review only, no code execution)

**Key Capabilities**:
- Deep research of technologies and API compatibility
- Database migration and schema change analysis
- Dependency mapping and version conflict detection
- Risk assessment with concrete mitigation strategies
- Alternative approach evaluation

**When to Use This Skill**:
- Reviewing development plans before implementation
- Validating architectural decisions for major features
- Checking database migration strategies
- Reviewing API integration plans
- Assessing authentication/authorization implementations
- Evaluating refactoring plans for risks
- Identifying missing considerations in technical designs

## 2. Core Principles

### Evidence-Based Review
- **Verify, never assume** - Check official documentation for every claim
- **Specific over vague** - Point to exact lines, endpoints, or configurations
- **Cite authoritative sources** - Official docs, RFCs, CVEs, not blog posts
- **Test when possible** - Verify version compatibility, API availability

### Practical Over Theoretical
- **Consider project constraints** - Time, budget, team expertise, tech stack
- **Flag real issues, not edge cases** - Focus on likely problems, not theoretical perfection
- **Recommend implementable solutions** - Not "rewrite everything" unless critical
- **Balance trade-offs** - Acknowledge pros/cons of recommendations

### Comprehensive Coverage
- **9 Critical Areas**: Authentication, Database, APIs, Types, Errors, Performance, Security, Testing, Rollback
- **Research all technologies** - Compatibility, versions, known issues, limitations
- **Map dependencies** - Direct and transitive, version conflicts, deprecations
- **Impact analysis** - Performance, security, UX, operational

### Structured Reporting
- **Executive summary first** - Overall assessment (Ready/Needs Revisions/Critical Issues)
- **Prioritize by severity** - Critical → High → Medium → Low
- **Provide alternatives** - Not just criticism, offer better approaches
- **Include rollback plan** - What to do if implementation fails

## 3. Implementation Workflow

**Objective**: Understand the existing system thoroughly before reviewing the plan

📚 **For complete details**: See `references/implementation-workflow.md`

---
## 4. Quality Assurance Checklist

**Before implementing this skill, ensure**:

### 4.1 Pre-Implementation Setup
- [ ] Virtual environment created and activated
- [ ] Dependencies installed from requirements.txt
- [ ] Pre-commit hooks installed (`pre-commit install`)
- [ ] Linters installed (black, isort, flake8, mypy, bandit)

### 4.2 Dependency Management
- [ ] All dependencies pinned with exact versions (==)
- [ ] No manual transitive dependency pins
- [ ] Dependencies tested in clean environment

### 4.3 Code Quality Gates (Run BEFORE committing)
- [ ] `black .` - Code formatted
- [ ] `isort .` - Imports sorted
- [ ] `flake8 . --max-line-length=120` - No linting errors
- [ ] `mypy . --ignore-missing-imports` - Type checking passes
- [ ] `bandit -r .` - Security scan clean

### 4.4 Security Validation
- [ ] Input validation for ALL external inputs
- [ ] Path traversal prevention implemented
- [ ] Command injection prevention (no shell=True)
- [ ] SQL injection prevention (parameterized queries)
- [ ] Secrets not in code or error messages

📚 **For complete security validation guide**: See `../../../template-references/security-framework.md`

### 4.5 Test Coverage Requirements
- [ ] Tests written BEFORE implementation (TDD)
- [ ] Unit tests for all public functions
- [ ] Edge case tests (empty, null, max values)
- [ ] Security tests (injection, traversal, overflow)
- [ ] Code coverage >80%

### 4.6 Documentation Requirements
- [ ] Docstrings for all public functions/classes
- [ ] Security considerations documented
- [ ] Examples of correct usage
- [ ] Known limitations documented

---

## 5. Quality Standards

### Issue Identification
- **Specific**: Point to exact file, line, endpoint, or configuration
- **Evidence-based**: Cite official docs, CVEs, GitHub issues, RFCs
- **Actionable**: Provide clear resolution path with code examples
- **Prioritized**: Severity-based (Critical → High → Medium → Low)

### Recommendations
- **Practical**: Implementable within project constraints
- **Contextual**: Considers team expertise, timeline, budget
- **Detailed**: Code examples, configuration snippets, migration scripts
- **Balanced**: Acknowledge trade-offs (performance vs maintainability)

### Research
- **Current**: Latest stable versions, not outdated docs
- **Authoritative**: Official documentation, RFCs, security advisories
- **Relevant**: Directly applicable to plan technologies
- **Cited**: Links to all sources

### Report Quality
- **Comprehensive**: Covers all 9 critical areas
- **Structured**: Follows standard report template
- **Scannable**: Tables, bullet points, clear headings
- **Actionable**: Every issue has concrete next steps

## 6. Common Plan Issues (Anti-Patterns)

### Authentication Anti-Patterns
- ❌ Missing token validation logic
- ❌ No refresh token strategy
- ❌ Session management not specified
- ❌ Incompatible auth methods (JWT vs session cookies)
- ❌ No authorization rules defined

### Database Anti-Patterns
- ❌ No migration rollback script
- ❌ Missing indexes for query patterns
- ❌ No foreign key constraints
- ❌ Constraint violations not handled
- ❌ No data validation at database level

### API Integration Anti-Patterns
- ❌ Wrong/deprecated API endpoints
- ❌ Missing authentication headers
- ❌ No rate limiting strategy
- ❌ Inadequate error handling (only 200 OK handled)
- ❌ No timeout or retry configuration

### Performance Anti-Patterns
- ❌ N+1 queries (SELECT in loop)
- ❌ No caching strategy
- ❌ Missing pagination for large results
- ❌ Unoptimized queries (full table scans)
- ❌ Synchronous blocking operations

### Security Anti-Patterns
- ❌ No input validation/sanitization
- ❌ SQL injection vulnerabilities
- ❌ XSS vulnerabilities
- ❌ Missing authorization checks
- ❌ Secrets hardcoded in config

## 7. Advanced Techniques

### Dependency Conflict Detection
```bash
# Check for version conflicts
npm ls [package-name]
pip show [package-name]
cargo tree
```

### API Verification
- Use WebSearch to find official API documentation
- Check API status page for outages/deprecations
- Verify rate limits and quotas
- Test authentication with example request

### Performance Estimation
- Estimate query complexity (O(n), O(n²))
- Calculate database table size growth
- Estimate API call frequency (requests/sec)
- Check cache hit ratio potential

## 8. Integration with Dev-AID

**Related Skills**:
- `devsecops-expert` (security review)
- `database-design` (schema review)
- `api-expert` (API integration review)
- `cicd-expert` (deployment strategy review)

**Workflow Integration**:
- Use this skill BEFORE implementing major features
- Integrate into PR review process for architecture changes
- Run plan reviews before sprint planning
- Use for RFCs and technical design documents

## 9. References

For detailed information, see:
- `references/review-report-examples.md` - Sample review reports
- `references/research-checklist.md` - Technology research template
- `references/common-issues-by-stack.md` - Stack-specific gotchas
- `references/security-review-guide.md` - Security-focused review process

---

**Remember**: Always read the complete plan, research all technologies with official docs, provide specific evidence-based issues, and include concrete recommendations. Begin by clarifying: Where is the plan document? What is the scope? Are there specific concerns?
