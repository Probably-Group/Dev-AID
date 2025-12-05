# FastAPI Security Examples

This document contains security patterns and OWASP Top 10 mitigations for FastAPI applications.

## OWASP Top 10 2025 Mapping

| OWASP ID | Category | FastAPI Mitigation |
|----------|----------|-------------------|
| A01:2025 | Broken Access Control | `Depends(get_current_user)` on all protected routes |
| A02:2025 | Security Misconfiguration | Disable docs in prod, use Pydantic Settings |
| A03:2025 | Supply Chain | Pin dependencies in requirements.txt |
| A04:2025 | Insecure Design | Pydantic validation on all inputs |
| A05:2025 | Identification & Auth | JWT with bcrypt, OAuth2PasswordBearer |
| A06:2025 | Vulnerable Components | Run `pip-audit` and `safety check` |
| A07:2025 | Cryptographic Failures | HTTPS only, bcrypt for passwords |
| A08:2025 | Injection | SQLAlchemy ORM, parameterized queries |
| A09:2025 | Logging Failures | Structured logging, exclude secrets |
| A10:2025 | Exception Handling | Custom handlers, hide stack traces |

## Input Validation & Injection Prevention

```python
# ✅ PREVENT SQL INJECTION
from pydantic import BaseModel, field_validator

class SearchQuery(BaseModel):
    query: str = Field(..., min_length=1, max_length=100)

    @field_validator('query')
    @classmethod
    def sanitize(cls, v: str) -> str:
        # Block SQL injection patterns
        forbidden = ['--', ';', '/*', 'xp_', 'union', 'select', 'drop']
        if any(p in v.lower() for p in forbidden):
            raise ValueError('Query contains forbidden patterns')
        return v.strip()

# ✅ ALWAYS use ORM (parameterized queries)
result = await db.execute(select(User).where(User.email == email))

# ❌ NEVER string concatenation
# query = f"SELECT * FROM users WHERE email = '{email}'"  # VULNERABLE!
```

## CORS Security

```python
# ❌ NEVER use wildcard in production
app.add_middleware(CORSMiddleware, allow_origins=["*"])  # DANGEROUS!

# ✅ Whitelist specific origins
app.add_middleware(CORSMiddleware, allow_origins=[
    "https://yourdomain.com",
    "https://app.yourdomain.com"
])
```

## Secrets Management

```python
# .env file (add to .gitignore!)
SECRET_KEY=your-32-char-secret-key-here
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db

# ❌ NEVER hardcode secrets
SECRET_KEY = "my-secret"  # DON'T!

# ✅ Use environment variables
SECRET_KEY = settings.SECRET_KEY

# ❌ NEVER log sensitive data
logger.info(f"Password: {password}")  # DON'T!

# ✅ Sanitize logs
logger.info(f"User {user.email} logged in")
```

## Critical Security Rules

### ALWAYS:
- Use bcrypt for password hashing (cost factor >= 12)
- Implement rate limiting on authentication endpoints
- Validate ALL inputs with Pydantic models
- Use HTTPS in production
- Set short token expiration (15-30 min for access tokens)
- Separate request and response models
- Use parameterized queries (ORM)

### NEVER:
- Expose password hashes in responses
- Use `allow_origins=["*"]` with credentials
- Disable HTTPS in production
- Trust user input without validation
- Use MD5/SHA1 for passwords
- Expose stack traces in production
- Log passwords or tokens
