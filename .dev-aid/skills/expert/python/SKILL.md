---
name: python
version: 2.0.0
description: "Python backend service development with type hints, async programming, packaging, and secure coding practices. Use when writing Python modules, designing async services, configuring logging, or implementing CLI tools with Python. Do NOT use for FastAPI-specific patterns (use fastapi-expert) or Django framework development."
compatibility: "Python 3.11+"
risk_level: HIGH
---

# Python Expert - Code Generation Rules

## 0. Anti-Hallucination Protocol

### 0.1 Mandatory Verification

**BEFORE generating any code:**
1. Verify the pattern exists in official documentation
2. Check version compatibility for all APIs used
3. Never invent method names or parameters
4. If unsure, state uncertainty explicitly

### 0.2 Security Patterns (NEVER violate)

**CWE-89: SQL Injection**
- NEVER: `f"SELECT * FROM users WHERE id = {user_id}"` or `.format()`
- ALWAYS: Parameterized queries or ORM methods

**CWE-78: OS Command Injection**
- NEVER: `os.system(user_input)` or `subprocess.run(cmd, shell=True)` with user data
- ALWAYS: `subprocess.run([binary, arg1, arg2], shell=False)` with validated args

**CWE-22: Path Traversal**
- NEVER: `open(user_provided_path)` without validation
- ALWAYS: Use `pathlib`, resolve paths, verify within allowed directory

**CWE-502: Insecure Deserialization**
- NEVER: `pickle.loads(user_data)` or `yaml.load(data, Loader=yaml.Loader)`
- ALWAYS: `yaml.safe_load()`, validate JSON schema, avoid pickle with untrusted data

**CWE-798: Hardcoded Credentials**
- NEVER: `password = "secret123"` in code
- ALWAYS: Environment variables, secrets manager, never commit secrets

### 0.3 Risk Level: HIGH

**Verification requirements for HIGH risk:**
- Test all generated code before presenting
- Include error handling for edge cases
- Validate security implications of patterns used

---

## 1. Security Principles

### 1.1 Data ≠ Code (CWE-94, CWE-78, CWE-89)

**Principle:** Never construct executable code/commands/queries from untrusted data via string operations.

**NEVER** use string formatting for SQL, commands, or eval:
```python
# ❌ WRONG - SQL injection (CWE-89)
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)

# ❌ WRONG - Command injection (CWE-78)
os.system(f"echo {user_input}")
subprocess.run(f"ls {directory}", shell=True)

# ❌ WRONG - Code injection (CWE-94)
eval(user_expression)
exec(f"result = {user_input}")

# ✅ CORRECT - Parameterized query
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# ✅ CORRECT - ORM
result = session.execute(select(User).where(User.id == user_id))

# ✅ CORRECT - Command as list, no shell
subprocess.run(["ls", directory], check=True)

# ✅ CORRECT - Safe evaluation
import ast
ast.literal_eval(user_input)  # Only literals, no code
```

### 1.2 Input Validation (CWE-20)

**Principle:** Validate all input at trust boundaries. Allowlist > Denylist. Reject by default.

**ALWAYS** use Pydantic for validation:
```python
# ❌ WRONG - No validation
def create_user(data: dict):
    username = data["username"]  # Could be anything
    # ...

# ✅ CORRECT - Pydantic validation with constraints
from pydantic import BaseModel, Field, EmailStr
from typing import Annotated

class UserCreate(BaseModel):
    model_config = {"extra": "forbid", "str_strip_whitespace": True}

    username: Annotated[str, Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")]
    email: EmailStr
    age: Annotated[int, Field(ge=0, le=150)]
    role: Literal["user", "admin"]  # Allowlist

def create_user(data: UserCreate):  # Validated
    # ...
```

### 1.3 Output Encoding (CWE-79, CWE-116)

**Principle:** Encode output based on context. Data rendered as data, never as code.

```python
# ❌ WRONG - Raw output in HTML
return f"<div>Hello, {username}</div>"

# ❌ WRONG - Raw output in JSON (can break structure)
return f'{{"name": "{name}"}}'

# ✅ CORRECT - HTML escaping
import html
return f"<div>Hello, {html.escape(username)}</div>"

# ✅ CORRECT - JSON serialization
import json
return json.dumps({"name": name})

# ✅ CORRECT - Shell escaping when needed
import shlex
safe_arg = shlex.quote(user_input)
```

### 1.4 Least Privilege (CWE-250)

**Principle:** Minimum permissions needed. Drop privileges. Scope access narrowly.

```python
# ❌ WRONG - Running as root unnecessarily
if os.geteuid() != 0:
    sys.exit("Must run as root")

# ❌ WRONG - Overly broad file permissions
os.chmod(config_file, 0o777)

# ✅ CORRECT - Restricted file permissions
os.chmod(config_file, 0o600)  # Owner read/write only

# ✅ CORRECT - Drop privileges after binding privileged port
import pwd
if os.geteuid() == 0:
    sock.bind(('0.0.0.0', 443))
    os.setuid(pwd.getpwnam('nobody').pw_uid)  # Drop to nobody
```

### 1.5 Fail Secure (CWE-636)

**Principle:** Default deny. On error, deny access. Never fail open.

```python
# ❌ WRONG - Fail open
def check_permission(user, resource):
    try:
        return has_access(user, resource)
    except Exception:
        return True  # DANGEROUS: error = access granted

# ✅ CORRECT - Fail closed
def check_permission(user, resource):
    try:
        return has_access(user, resource)
    except Exception as e:
        logger.error(f"Permission check failed: {e}")
        return False  # Safe: error = access denied

# ❌ WRONG - Silent exception swallowing
try:
    validate_token(token)
except Exception:
    pass  # Token treated as valid!

# ✅ CORRECT - Explicit handling
def validate_request(token: str) -> bool:
    try:
        validate_token(token)
        return True
    except (TokenExpired, TokenInvalid) as e:
        logger.warning(f"Token validation failed: {e}")
        return False
```

### 1.6 Defense in Depth

**Principle:** Multiple security layers. Don't rely on single control.

```python
# Layer 1: Input validation at API boundary
@router.post("/upload")
async def upload_file(file: UploadFile, user: User = Depends(get_current_user)):
    # Layer 2: File type validation
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "Invalid file type")

    # Layer 3: File size limit
    contents = await file.read(MAX_SIZE + 1)
    if len(contents) > MAX_SIZE:
        raise HTTPException(413, "File too large")

    # Layer 4: Path validation
    safe_name = secure_filename(file.filename)
    safe_path = (UPLOAD_DIR / safe_name).resolve()
    if not safe_path.is_relative_to(UPLOAD_DIR):
        raise HTTPException(400, "Invalid path")

    # Layer 5: Database constraint
    # (UNIQUE constraint, foreign key to user)
```

### 1.7 Secrets ≠ Code (CWE-798)

**Principle:** Never hardcode secrets. Use environment/vault. Never log secrets.

```python
# ❌ WRONG - Hardcoded secrets
API_KEY = "sk-1234567890abcdef"
DATABASE_URL = "postgresql://user:password@localhost/db"

# ❌ WRONG - Secrets in error messages
raise ValueError(f"Failed to connect with key: {api_key}")

# ❌ WRONG - Logging secrets
logger.info(f"Using API key: {api_key}")

# ✅ CORRECT - Secrets from environment
import os
API_KEY = os.environ["API_KEY"]  # Fails if not set
DATABASE_URL = os.environ["DATABASE_URL"]

# ✅ CORRECT - Safe error messages
raise ValueError("Authentication failed")

# ✅ CORRECT - Redacted logging
logger.info("API key configured: ***")
```

### 1.8 Trust Boundaries (CWE-501)

**Principle:** Explicitly identify trusted vs untrusted. Validate at every boundary crossing.

```python
# Trust boundaries in a typical application:
#
#  [Untrusted]        [Boundary]           [Trusted]
#  HTTP Request  -->  API Endpoint  -->    Service Layer
#  File Upload   -->  Validator     -->    Storage
#  Database      -->  ORM           -->    Application
#  External API  -->  Response Val  -->    Internal Use

# ❌ WRONG - Trusting external API response
external_data = await client.get("https://api.example.com/data")
user_id = external_data["user_id"]  # No validation

# ✅ CORRECT - Validate at boundary
external_data = await client.get("https://api.example.com/data")
validated = ExternalResponse.model_validate(external_data.json())
user_id = validated.user_id  # Now validated
```

---

## 2. Version Requirements

**ALWAYS use these minimum versions:**
```
python>=3.12.8          # CVE-2024-12718 tarfile bypass, CVE-2024-12254 asyncio
pydantic>=2.5.0         # Validation
cryptography>=42.0.0    # CVE-2023-50782 RSA disclosure
sqlalchemy>=2.0.0       # Async support, type safety
argon2-cffi>=21.0.0     # Password hashing
httpx>=0.25.0           # Async HTTP client
```

**WHEN generating pyproject.toml or requirements.txt** → pin these exact versions or higher.

---

## 3. Code Patterns

### 3.1 WHEN creating async service

```python
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user(self, user_id: int) -> User:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        return user

    async def create_user(self, data: UserCreate) -> User:
        user = User(**data.model_dump())
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
```

### 3.2 WHEN hashing passwords

```python
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4
)

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(hash: str, password: str) -> bool:
    try:
        ph.verify(hash, password)
        return True
    except VerifyMismatchError:
        return False
```

### 3.3 WHEN making HTTP requests

```python
import httpx
from pydantic import BaseModel

class ExternalResponse(BaseModel):
    id: int
    name: str

async def fetch_external_data(url: str) -> ExternalResponse:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return ExternalResponse.model_validate(response.json())
```

### 3.4 WHEN reading files with user input

```python
from pathlib import Path

ALLOWED_DIR = Path("/app/data").resolve()

def safe_read_file(user_filename: str) -> str:
    # Resolve path and check containment
    file_path = (ALLOWED_DIR / user_filename).resolve()

    if not file_path.is_relative_to(ALLOWED_DIR):
        raise ValueError("Path traversal blocked")

    if not file_path.exists():
        raise FileNotFoundError(f"File not found")

    return file_path.read_text()
```

### 3.5 WHEN extracting archives

```python
import tarfile

def safe_extract_tar(tar_path: str, dest_dir: str):
    dest = Path(dest_dir).resolve()

    with tarfile.open(tar_path) as tar:
        # Python 3.12+: Use filter='data' to block dangerous entries
        tar.extractall(dest, filter='data')
```

### 3.6 WHEN running subprocesses

```python
import subprocess

def run_command(cmd: str, args: list[str]) -> str:
    # Validate command is in allowlist
    ALLOWED_COMMANDS = {"ls", "cat", "head"}
    if cmd not in ALLOWED_COMMANDS:
        raise ValueError(f"Command not allowed: {cmd}")

    # Run with list arguments, never shell=True
    result = subprocess.run(
        [cmd, *args],
        capture_output=True,
        text=True,
        check=True,
        timeout=30
    )
    return result.stdout
```

---

## 4. Anti-Patterns

### 4.1 Deserialization

**NEVER** use pickle with untrusted data (CWE-502, CVE-2025-68664):
```python
# ❌ WRONG - Arbitrary code execution
import pickle
data = pickle.loads(untrusted_bytes)  # RCE!

# ✅ CORRECT - Safe serialization
import json
data = json.loads(untrusted_string)

# ✅ CORRECT - If objects needed, use Pydantic
from pydantic import BaseModel
data = MyModel.model_validate_json(untrusted_string)
```

### 4.2 Password Storage

**NEVER** use MD5/SHA for passwords (CWE-328):
```python
# ❌ WRONG - Weak hashing
import hashlib
hash = hashlib.md5(password.encode()).hexdigest()
hash = hashlib.sha256(password.encode()).hexdigest()

# ✅ CORRECT - Argon2id with proper parameters
from argon2 import PasswordHasher
ph = PasswordHasher()
hash = ph.hash(password)
```

### 4.3 Subprocess Shell

**NEVER** use shell=True with user input (CWE-78):
```python
# ❌ WRONG - Command injection
subprocess.run(f"echo {user_input}", shell=True)
os.system(f"ls {directory}")

# ✅ CORRECT - List arguments
subprocess.run(["echo", user_input])
```

### 4.4 Eval/Exec

**NEVER** use eval/exec with user input (CWE-94):
```python
# ❌ WRONG - Code injection
result = eval(user_expression)
exec(user_code)

# ✅ CORRECT - ast.literal_eval for safe literals only
import ast
result = ast.literal_eval(user_input)  # Only parses literals
```

---

## 5. Testing

**ALWAYS write security tests:**
```python
import pytest

class TestSecurityPatterns:
    def test_sql_injection_prevented(self, db_session):
        service = UserService(db_session)
        # These should not cause errors or return unexpected results
        payloads = ["'; DROP TABLE users; --", "' OR '1'='1", "admin'--"]
        for payload in payloads:
            result = service.get_user_by_username(payload)
            assert result is None

    def test_path_traversal_blocked(self):
        attacks = ["../etc/passwd", "..\\..\\etc\\passwd", "foo/../../etc/passwd"]
        for attack in attacks:
            with pytest.raises(ValueError, match="traversal"):
                safe_read_file(attack)

    def test_command_injection_blocked(self):
        attacks = ["; rm -rf /", "| cat /etc/passwd", "$(whoami)"]
        for attack in attacks:
            with pytest.raises(ValueError):
                run_command("ls", [attack])

    def test_deserialization_uses_json_not_pickle(self):
        # Verify pickle is not used for untrusted data
        import pickle
        malicious = pickle.dumps({"__reduce__": (os.system, ("whoami",))})
        with pytest.raises(Exception):  # Should fail, not execute
            process_untrusted_data(malicious)
```

**Test coverage requirements:**
- [ ] Security tests for all input handling
- [ ] SQL injection tests
- [ ] Path traversal tests
- [ ] Command injection tests
- [ ] Deserialization tests (verify no pickle)

---

## 6. Pre-Generation Checklist

**BEFORE generating any Python code:**

- [ ] Data ≠ Code: No f-strings in SQL/commands/eval
- [ ] Input validation: All external input through Pydantic
- [ ] Output encoding: Context-appropriate escaping
- [ ] Secrets: From os.environ, never hardcoded
- [ ] Passwords: Argon2id, never MD5/SHA
- [ ] Subprocess: List args, never shell=True with user input
- [ ] Files: Path containment check before access
- [ ] Archives: tarfile filter='data' (Python 3.12+)
- [ ] Deserialization: json/Pydantic, never pickle for untrusted
- [ ] Error handling: Fail closed, no internals in messages

---

**Performance**: Quality over speed. Verify all code examples compile. Never skip security checks. See `template-references/performance-notes.md` for full guidelines.