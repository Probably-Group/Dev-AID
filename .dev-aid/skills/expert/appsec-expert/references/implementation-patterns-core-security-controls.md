## 7. Implementation Patterns (Core Security Controls)

### Pattern 1: Input Validation and Sanitization

```python
# ✅ SECURE: Comprehensive input validation
from typing import Optional
import re
from html import escape
from urllib.parse import urlparse

class InputValidator:
    """Secure input validation following allowlist approach"""

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email using strict regex"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email)) and len(email) <= 254

    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username - alphanumeric only, 3-20 chars"""
        pattern = r'^[a-zA-Z0-9_]{3,20}$'
        return bool(re.match(pattern, username))

    @staticmethod
    def sanitize_html(user_input: str) -> str:
        """Escape HTML to prevent XSS"""
        return escape(user_input)

    @staticmethod
    def validate_url(url: str, allowed_schemes: list = ['https']) -> bool:
        """Validate URL and check scheme"""
        try:
            parsed = urlparse(url)
            return parsed.scheme in allowed_schemes and bool(parsed.netloc)
        except Exception:
            return False

    @staticmethod
    def validate_integer(value: str, min_val: int = None, max_val: int = None) -> Optional[int]:
        """Safely parse and validate integer"""
        try:
            num = int(value)
            if min_val is not None and num < min_val:
                return None
            if max_val is not None and num > max_val:
                return None
            return num
        except (ValueError, TypeError):
            return None
```

---

### Pattern 2: SQL Injection Prevention

```python
# ❌ DANGEROUS: String concatenation (SQLi vulnerable)
def get_user_vulnerable(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)  # Vulnerable to: ' OR '1'='1

# ✅ SECURE: Parameterized queries (prepared statements)
def get_user_secure(username):
    query = "SELECT * FROM users WHERE username = ?"
    cursor.execute(query, (username,))

# ✅ SECURE: ORM with parameterized queries
from sqlalchemy import text

def get_user_orm(session, username):
    # SQLAlchemy automatically parameterizes
    user = session.query(User).filter(User.username == username).first()
    return user

# ✅ SECURE: Raw query with parameters
def search_users(session, search_term):
    query = text("SELECT * FROM users WHERE username LIKE :pattern")
    results = session.execute(query, {"pattern": f"%{search_term}%"})
    return results.fetchall()
```

---

### Pattern 3: Cross-Site Scripting (XSS) Prevention

```javascript
// ❌ DANGEROUS: Direct HTML insertion
element.innerHTML = 'Hello ' + name;  // Vulnerable to XSS

// ✅ SECURE: Use textContent (no HTML parsing)
element.textContent = 'Hello ' + name;

// ✅ SECURE: DOMPurify for rich HTML
import DOMPurify from 'dompurify';
const clean = DOMPurify.sanitize(html, {
  ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p'],
  ALLOWED_ATTR: ['href']
});

// ✅ SECURE: React/Vue automatically escape {variables}
```

---

### Pattern 4: Authentication and Password Security

```python
# ✅ SECURE: Password hashing with Argon2id
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import secrets

class SecureAuth:
    def __init__(self):
        self.ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4)

    def hash_password(self, password: str) -> str:
        if len(password) < 12:
            raise ValueError("Password must be at least 12 characters")
        return self.ph.hash(password)

    def verify_password(self, password: str, hash: str) -> bool:
        try:
            self.ph.verify(hash, password)
            return True
        except VerifyMismatchError:
            return False

    def generate_secure_token(self, bytes_length: int = 32) -> str:
        return secrets.token_urlsafe(bytes_length)

# ❌ NEVER: hashlib.md5(password.encode()).hexdigest()
```

---

### Pattern 5: JWT Authentication with Security Best Practices

```python
# ✅ SECURE: JWT implementation
import jwt
from datetime import datetime, timedelta
import secrets

class JWTManager:
    def __init__(self, secret_key: str, algorithm: str = 'HS256'):
        self.secret_key = secret_key
        self.algorithm = algorithm

    def create_access_token(self, user_id: int, roles: list) -> str:
        now = datetime.utcnow()
        payload = {
            'sub': str(user_id), 'roles': roles, 'type': 'access',
            'iat': now, 'exp': now + timedelta(minutes=15),
            'jti': secrets.token_hex(16)
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str, expected_type: str = 'access'):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm],
                options={'verify_exp': True, 'require': ['sub', 'exp', 'type', 'jti']})
            if payload.get('type') != expected_type:
                return None
            return payload
        except jwt.InvalidTokenError:
            return None
```

**📚 For advanced patterns** (Security Headers, Secrets Management with Vault, CI/CD Security Integration):
- See `references/implementation-patterns.md`

---

