# Security Guidelines

**Purpose**: Security requirements for AI assistants to follow when generating code
**Used by**: Claude, Gemini, Cursor, and other AI coding assistants
**Update**: After security reviews or when requirements change

---

## Security Rules for AI

When generating code, AI assistants MUST:

1. **Never hardcode secrets** - Use environment variables
2. **Always validate input** - At API boundaries
3. **Use parameterized queries** - Never string concatenation for SQL
4. **Escape output** - Prevent XSS
5. **Check authorization** - Before every sensitive operation

---

## Input Validation

```typescript
// ✅ Always validate at API boundaries
import { z } from 'zod';

const UserSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
  age: z.number().int().positive().max(150),
});

// In route handler
const validated = UserSchema.parse(req.body);
```

---

## Database Queries

```typescript
// ❌ NEVER do this - SQL injection vulnerability
const query = `SELECT * FROM users WHERE id = ${userId}`;

// ✅ Always use parameterized queries
const user = await db.query('SELECT * FROM users WHERE id = $1', [userId]);

// ✅ Or use ORM with proper escaping
const user = await prisma.user.findUnique({ where: { id: userId } });
```

---

## Authentication

```typescript
// ✅ Secure password handling
import bcrypt from 'bcrypt';

// Hashing (minimum 12 rounds)
const hash = await bcrypt.hash(password, 12);

// Verification
const isValid = await bcrypt.compare(password, hash);

// ❌ Never store plain text passwords
// ❌ Never log passwords
// ❌ Never return passwords in API responses
```

---

## Secrets Management

```typescript
// ✅ Use environment variables
const apiKey = process.env.API_KEY;

// ❌ Never hardcode
const apiKey = 'sk-1234567890abcdef';

// ❌ Never commit .env files
// .env should be in .gitignore
```

**Required in .gitignore**:
```
.env
.env.local
.env.*.local
*.pem
*.key
credentials.json
```

---

## Output Encoding

```typescript
// ✅ React automatically escapes (safe)
return <div>{userInput}</div>;

// ❌ Dangerous - XSS vulnerability
return <div dangerouslySetInnerHTML={{ __html: userInput }} />;

// If you must use dangerouslySetInnerHTML, sanitize first
import DOMPurify from 'dompurify';
return <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(userInput) }} />;
```

---

## Authorization

```typescript
// ✅ Always check authorization
async function deleteUser(requesterId: string, targetUserId: string) {
  const requester = await getUser(requesterId);

  // Check permission BEFORE action
  if (requester.role !== 'admin' && requesterId !== targetUserId) {
    throw new ForbiddenError('Not authorized to delete this user');
  }

  await db.users.delete(targetUserId);
}
```

---

## API Security Headers

```typescript
// Use helmet.js or set headers manually
app.use(helmet());

// Or manually:
res.setHeader('X-Content-Type-Options', 'nosniff');
res.setHeader('X-Frame-Options', 'DENY');
res.setHeader('X-XSS-Protection', '1; mode=block');
res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
```

---

## Rate Limiting

```typescript
// ✅ Protect sensitive endpoints
import rateLimit from 'express-rate-limit';

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 attempts per window
  message: 'Too many login attempts, try again later'
});

app.post('/login', loginLimiter, loginHandler);
```

---

## Security Scanning

This project uses comprehensive automated security scanning via pre-push hooks:

**Universal tools (always run):**
- **Gitleaks**: Secret detection in git history + current files
- **Trivy**: CVE + misconfig + secrets scanning (HIGH + CRITICAL)
- **Opengrep**: SAST with 10 universal rulesets (OWASP Top 10, CWE Top 25, TrailOfBits, command injection, insecure transport, JWT) + 12 auto-detected language-specific rulesets

**Language-specific SAST (auto-detected by file presence):**
- **ShellCheck**: Bash/Shell static analysis
- **Flawfinder**: C/C++ CWE-mapped security scanner
- **mobsfscan**: Swift/iOS OWASP MASVS/MSTG scanner
- **Bandit**: Python SAST (medium+ severity)

**Dependency audit (auto-detected):**
- **pip-audit**: Python dependency vulnerabilities
- **npm audit**: JS/TS dependency vulnerabilities (high+)
- **cargo audit**: Rust dependency vulnerabilities (RustSec)
- **govulncheck**: Go official vulnerability check

Run manually: `./.dev-aid/scripts/security-scan.sh`
Tool reference: `./.dev-aid/docs/SECURITY-TOOLS-REFERENCE.md`

---

**AI Instructions**: When generating code:
- Follow these security patterns without exception
- If you're unsure about security implications, flag it
- Never suggest disabling security features "for simplicity"
- Always validate untrusted input, even in internal functions
