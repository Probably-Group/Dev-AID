# FastAPI Pre-Implementation Checklist

Use this checklist to ensure your FastAPI implementation follows best practices.

## Phase 1: Before Writing Code

### Requirements Analysis
- [ ] Identify all endpoints needed
- [ ] Define request/response schemas
- [ ] List authentication requirements
- [ ] Identify database models needed
- [ ] Plan error responses

### Test Planning
- [ ] Write test cases for each endpoint (TDD)
- [ ] Plan authentication test scenarios
- [ ] Plan authorization test scenarios
- [ ] Plan validation error test cases
- [ ] Set up test fixtures and conftest.py

### Security Planning
- [ ] Review OWASP Top 10 mitigations
- [ ] Plan input validation strategy
- [ ] Define rate limiting requirements
- [ ] Plan secrets management

---

## Phase 2: During Implementation

### Code Quality
- [ ] All endpoints use `async def`
- [ ] Pydantic models for all inputs
- [ ] Separate request/response models
- [ ] Dependency injection for auth/db
- [ ] Proper error handling with HTTPException

### Security Implementation
- [ ] Bcrypt password hashing (cost >= 12)
- [ ] JWT secret keys >= 32 characters
- [ ] Access tokens expire in 15-30 min
- [ ] CORS whitelist (no "*")
- [ ] Rate limiting on auth endpoints
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (ORM only)
- [ ] Secrets in environment variables

### Database
- [ ] Async database driver (asyncpg)
- [ ] Connection pooling configured
- [ ] Alembic migrations created
- [ ] Indexes on queried columns
- [ ] Transaction rollback on errors
- [ ] No N+1 query issues (eager loading)

### Performance
- [ ] asyncio.gather for concurrent operations
- [ ] Background tasks for non-critical ops
- [ ] Caching for frequently accessed data
- [ ] Streaming for large responses
- [ ] No blocking operations

---

## Phase 3: Before Committing

### Testing Verification
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Coverage >= 80%: `pytest --cov=app`
- [ ] Authentication tests pass
- [ ] Authorization tests pass
- [ ] Validation error tests pass

### Code Quality Verification
- [ ] Type checking passes: `mypy app/`
- [ ] Linting passes: `ruff check app/`
- [ ] No security vulnerabilities: `pip-audit`
- [ ] Dependencies secure: `safety check`

### API Verification
- [ ] OpenAPI docs generate correctly
- [ ] All endpoints documented
- [ ] Response models serialize correctly
- [ ] Proper HTTP status codes
- [ ] Error responses standardized

### Production Readiness
- [ ] Docs disabled in production config
- [ ] HTTPS enforced in production
- [ ] Stack traces hidden in production
- [ ] .env in .gitignore
- [ ] Environment-specific configs work
- [ ] Health check endpoint working
- [ ] Structured logging configured
- [ ] Error tracking configured (Sentry)
