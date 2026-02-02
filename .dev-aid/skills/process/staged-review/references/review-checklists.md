# Review Checklists

Detailed checklists for code review by category.

## Stage 1: Spec Compliance Checklist

### Requirements Coverage

- [ ] Every requirement in spec has corresponding implementation
- [ ] No requirements were skipped or deferred without approval
- [ ] Implementation matches acceptance criteria exactly
- [ ] All user stories are addressed
- [ ] Edge cases from spec are handled

### Behavior Verification

- [ ] Happy path works as specified
- [ ] Error cases behave as specified
- [ ] UI matches designs (if applicable)
- [ ] API responses match contract
- [ ] Performance meets specified thresholds

### Scope Check

- [ ] No features added beyond spec
- [ ] No "while I'm here" improvements
- [ ] No premature optimization
- [ ] No unnecessary abstraction
- [ ] Changes are limited to spec scope

---

## Stage 2: Architecture & Design

### SOLID Principles

**Single Responsibility**
- [ ] Each class/module has one reason to change
- [ ] Functions do one thing
- [ ] No god classes/modules

**Open/Closed**
- [ ] New behavior can be added without modifying existing code
- [ ] Extension points are clear
- [ ] No hardcoded switches for future features

**Liskov Substitution**
- [ ] Subclasses can replace parent classes
- [ ] Interface contracts are respected
- [ ] No type checking to determine behavior

**Interface Segregation**
- [ ] Interfaces are focused
- [ ] Clients don't depend on methods they don't use
- [ ] No "fat" interfaces

**Dependency Inversion**
- [ ] High-level modules don't depend on low-level details
- [ ] Dependencies are injected
- [ ] Abstractions don't depend on details

### Patterns & Consistency

- [ ] Follows existing codebase patterns
- [ ] Naming conventions respected
- [ ] File organization matches project structure
- [ ] Similar problems solved similarly

---

## Stage 2: Implementation Quality

### Error Handling

- [ ] All errors are caught appropriately
- [ ] Error messages are descriptive
- [ ] Errors don't leak sensitive information
- [ ] Recovery strategies are clear
- [ ] No swallowed exceptions
- [ ] Async errors are handled

### Type Safety

- [ ] Strong typing used throughout
- [ ] No `any` types (TypeScript)
- [ ] Null/undefined handled explicitly
- [ ] Type guards where needed
- [ ] Generic types used appropriately

### Code Smells

| Smell | Check |
|-------|-------|
| Long Method | Methods < 30 lines? |
| Long Parameter List | < 4 parameters? |
| Duplicated Code | DRY respected? |
| Dead Code | All code reachable? |
| Magic Numbers | Named constants used? |
| Feature Envy | Methods belong to right class? |
| Data Clumps | Related data grouped? |

### Defensive Programming

- [ ] Preconditions validated
- [ ] Postconditions verified
- [ ] Invariants maintained
- [ ] Fail-fast on invalid state
- [ ] Assertions for unexpected conditions

---

## Stage 2: Security Checklist

### Input Validation

- [ ] All user input validated
- [ ] Input length limits enforced
- [ ] Input format validated (email, URL, etc.)
- [ ] Whitelist validation preferred over blacklist
- [ ] File uploads validated (type, size, content)

### Authentication & Authorization

- [ ] Authentication required for protected routes
- [ ] Authorization checked before operations
- [ ] Session management secure
- [ ] Password handling follows best practices
- [ ] Multi-factor authentication where required

### Data Protection

- [ ] Sensitive data encrypted at rest
- [ ] Sensitive data encrypted in transit
- [ ] PII not logged
- [ ] Secrets not in code
- [ ] Data retention policies followed

### OWASP Top 10

| Vulnerability | Check |
|---------------|-------|
| Injection | Parameterized queries? Sanitized input? |
| Broken Auth | Strong session management? |
| Sensitive Data | Encryption? Minimization? |
| XXE | XML parsing disabled external entities? |
| Broken Access | Authorization checks? |
| Misconfiguration | Secure defaults? |
| XSS | Output encoding? CSP? |
| Insecure Deserialization | Trusted data only? |
| Known Vulnerabilities | Dependencies scanned? |
| Logging | Security events logged? |

### API Security

- [ ] Rate limiting implemented
- [ ] CORS configured correctly
- [ ] API keys not exposed
- [ ] Endpoints require authentication
- [ ] Response doesn't leak internal details

---

## Stage 2: Performance Checklist

### Database

- [ ] Queries use indexes
- [ ] No N+1 queries
- [ ] Connections pooled
- [ ] Pagination for large datasets
- [ ] No unnecessary data fetched

### Memory

- [ ] No memory leaks
- [ ] Large objects released
- [ ] Streams used for large data
- [ ] Caching bounded

### Network

- [ ] Responses paginated
- [ ] Assets compressed
- [ ] Requests batched where appropriate
- [ ] Caching headers set

### Async/Concurrent

- [ ] No blocking operations in async code
- [ ] Proper use of parallel execution
- [ ] Race conditions avoided
- [ ] Deadlocks prevented

---

## Stage 2: Testing Checklist

### Coverage

- [ ] Unit tests for all public methods
- [ ] Integration tests for external dependencies
- [ ] E2E tests for critical paths
- [ ] Coverage threshold met (typically 80%)

### Test Quality

- [ ] Tests are readable
- [ ] Tests are maintainable
- [ ] Tests are deterministic
- [ ] Tests are isolated
- [ ] Tests are fast

### Scenarios

| Type | Covered? |
|------|----------|
| Happy path | [ ] |
| Empty input | [ ] |
| Invalid input | [ ] |
| Boundary values | [ ] |
| Error conditions | [ ] |
| Concurrent access | [ ] |

### Test Anti-Patterns

- [ ] No testing implementation details
- [ ] No brittle selectors (UI tests)
- [ ] No excessive mocking
- [ ] No testing framework internals
- [ ] No flaky tests

---

## Stage 2: Documentation Checklist

### Code Documentation

- [ ] Public APIs documented
- [ ] Complex algorithms explained
- [ ] Non-obvious decisions explained
- [ ] No outdated comments
- [ ] TODO comments have tickets

### User Documentation

- [ ] README updated if needed
- [ ] API documentation updated
- [ ] Changelog entry added
- [ ] Migration guide if breaking changes

---

## Review Feedback Template

```
## Stage 1: Spec Compliance

### Requirements
- [x] Requirement 1: Implemented correctly
- [ ] Requirement 2: Missing edge case handling
- [x] Requirement 3: Implemented correctly

### Issues
- **BLOCKER** [SPEC]: Missing validation for negative numbers
  - Location: `src/calculator.ts:45`
  - Spec says: "Handle negative numbers with error"
  - Fix: Add validation check before calculation

## Stage 2: Code Quality (if Stage 1 passes)

### Architecture
- [x] SOLID principles followed
- [x] Consistent with codebase

### Security
- [ ] Input validation missing for user input
  - **MAJOR** [SECURITY]: No sanitization on `name` field
  - Location: `src/api/users.ts:23`
  - Fix: Add input validation middleware

### Performance
- [x] No obvious bottlenecks

### Testing
- [ ] Missing test for error case
  - **MINOR** [TEST]: No test for network timeout
  - Location: `tests/api.test.ts`
  - Suggestion: Add test for timeout scenario
```
