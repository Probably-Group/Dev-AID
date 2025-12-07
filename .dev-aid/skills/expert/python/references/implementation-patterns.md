## 5. Implementation Patterns

### Pattern 1: Type-Safe Input Validation

```python
from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Annotated
import re

class UserCreate(BaseModel):
    """Validated user creation request."""
    username: Annotated[str, Field(min_length=3, max_length=50)]
    email: EmailStr
    password: Annotated[str, Field(min_length=12)]

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username must be alphanumeric')
        return v

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not all([re.search(r'[A-Z]', v), re.search(r'[a-z]', v), re.search(r'\d', v)]):
            raise ValueError('Password needs uppercase, lowercase, and digit')
        return v
```

### Pattern 2: Secure Password Hashing

```python
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4)

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(password: str, hash: str) -> bool:
    try:
        ph.verify(hash, password)
        return True
    except VerifyMismatchError:
        return False
```

### Pattern 3: Safe Database Queries

```python
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

# NEVER: f"SELECT * FROM users WHERE username = '{username}'"

async def get_user_safe(db: AsyncSession, username: str) -> User | None:
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def search_users(db: AsyncSession, pattern: str) -> list:
    stmt = text("SELECT * FROM users WHERE username LIKE :pattern")
    result = await db.execute(stmt, {"pattern": f"%{pattern}%"})
    return result.fetchall()
```

### Pattern 4: Safe File Operations

```python
from pathlib import Path

def safe_read_file(base_dir: Path, user_filename: str) -> str:
    if '..' in user_filename or user_filename.startswith('/'):
        raise ValueError("Invalid filename")

    file_path = (base_dir / user_filename).resolve()
    if not file_path.is_relative_to(base_dir.resolve()):
        raise ValueError("Path traversal detected")

    return file_path.read_text()
```

### Pattern 5: Safe Subprocess Execution

```python
import subprocess

ALLOWED_PROGRAMS = {'git', 'python', 'pip'}

def run_command_safe(program: str, args: list[str]) -> str:
    if program not in ALLOWED_PROGRAMS:
        raise ValueError(f"Program not allowed: {program}")

    result = subprocess.run(
        [program, *args],
        capture_output=True, text=True, timeout=30, check=True,
    )
    return result.stdout
```

---

