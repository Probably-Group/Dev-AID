# OS Keychain Anti-Patterns

This guide covers common mistakes and anti-patterns when working with OS keychain services. These patterns lead to security vulnerabilities, performance issues, or cross-platform compatibility problems.

---

## 1. Environment Variables for Secrets

### Anti-Pattern

```python
# NEVER: Visible in /proc, logs, shell history
api_key = os.environ.get('API_KEY')
DATABASE_PASSWORD = os.environ['DB_PASS']
```

### Why This Is Dangerous

- **Visible in process listings**: `/proc/<pid>/environ` readable by other processes
- **Logged in shell history**: `.bash_history`, `.zsh_history`
- **Exposed in error messages**: Stack traces often dump environment
- **Inherited by child processes**: Subprocesses inherit environment
- **Visible in container orchestration**: Kubernetes ConfigMaps, Docker inspect

### Correct Approach

```python
# ALWAYS: OS keychain
api_key = SecureCredentialStore("api").retrieve("api-key")
db_password = SecureCredentialStore("database").retrieve("password")
```

**Why Better**:
- Encrypted at rest with platform-native encryption
- Requires explicit access per credential
- Not visible in process listings
- Not inherited by child processes

---

## 2. Hardcoded Credentials

### Anti-Pattern

```python
# NEVER: In source code
DATABASE_PASSWORD = "production-password-123"
API_KEY = "sk-1234567890abcdef"

class Config:
    DB_HOST = "db.prod.example.com"
    DB_USER = "admin"
    DB_PASS = "admin123"  # Committed to git!
```

### Why This Is Dangerous

- **Version control exposure**: Visible in git history forever
- **Code review exposure**: All reviewers see credentials
- **Binary inspection**: Decompilers extract string literals
- **Accidental sharing**: Easy to share code with credentials
- **Rotation impossible**: Changing password requires code deploy

### Correct Approach

```python
# ALWAYS: Retrieved at runtime
class Config:
    def __init__(self):
        cred_store = SecureCredentialStore("database")
        self.db_host = "db.prod.example.com"  # Non-secret config is OK
        self.db_user = cred_store.retrieve("username")
        self.db_pass = cred_store.retrieve("password")

config = Config()
```

**Why Better**:
- Credentials never in source code or git
- Can rotate without code changes
- Different credentials per environment
- No risk of accidental commits

---

## 3. Insecure File Storage

### Anti-Pattern

```python
# NEVER: Plain files
with open(os.path.expanduser('~/.config/app/credentials.json')) as f:
    creds = json.load(f)

# NEVER: Base64 encoding (not encryption!)
with open('secrets.b64') as f:
    password = base64.b64decode(f.read()).decode()

# NEVER: Config files with secrets
config = configparser.ConfigParser()
config.read('config.ini')
api_key = config.get('api', 'key')
```

### Why This Is Dangerous

- **Readable by any process**: No OS-level access control
- **Backup exposure**: Synced to cloud, backups, snapshots
- **File permission errors**: Easy to misconfigure `chmod`
- **Base64 is not encryption**: Trivially decoded
- **Config file leaks**: Accidentally shared or committed

### Correct Approach

```python
# ALWAYS: Platform keychain
store = SecureCredentialStore("app")
token = store.retrieve("access-token")

# For config files, reference keychain entries
# config.ini:
# [api]
# keychain_service = com.jarvis.assistant.api
# keychain_key = access-token

config = configparser.ConfigParser()
config.read('config.ini')
service = config.get('api', 'keychain_service')
key = config.get('api', 'keychain_key')
# Then retrieve from keychain (not stored in file)
```

**Why Better**:
- OS-level encryption (DPAPI, Secure Enclave, etc.)
- ACL enforcement by OS
- Not exposed in backups (keychain separate)
- Cannot accidentally share credentials

---

## 4. Logging Credentials

### Anti-Pattern

```python
# NEVER: Log credential values
logger.info(f"Retrieved API key: {api_key}")
logger.debug(f"Using password: {password}")
print(f"Token: {token}")

# NEVER: Log with identifiable key names
logger.info(f"Retrieved credential for user: admin@example.com")
```

### Why This Is Dangerous

- **Log aggregation exposure**: Sent to centralized logging
- **Log file readable**: Often world-readable or overly permissive
- **Log retention**: Credentials persist long after rotation
- **Debug logs in production**: Accidentally enabled debug mode
- **Compliance violations**: GDPR, PCI-DSS prohibit credential logging

### Correct Approach

```python
# ALWAYS: Log metadata only
logger.info("credential.retrieved", extra={
    'service': 'api-keys',
    'key': 'openai-key',  # Key name is OK if not sensitive
    'timestamp': time.time()
})

# For errors, never include credential values
try:
    cred = store.retrieve("api-key")
except KeyError:
    logger.error("credential.not_found", extra={'key': 'api-key'})
    raise
```

**Why Better**:
- Audit trail without exposing secrets
- Compliance-friendly logging
- Useful for debugging without security risk
- Structured logging for analysis

---

## 5. Single Service Name for All Credentials

### Anti-Pattern

```python
# NEVER: All credentials under one service
store = SecureCredentialStore("jarvis")
store.store("db-password", "...")
store.store("api-key", "...")
store.store("encryption-key", "...")
store.store("ssh-private-key", "...")
```

### Why This Is Dangerous

- **No isolation**: Compromise of one credential exposes all
- **Access control all-or-nothing**: Cannot grant partial access
- **Rotation coordination**: Must rotate all at once
- **Blast radius**: Single breach compromises entire system
- **Difficult auditing**: Cannot track access per credential type

### Correct Approach

```python
# ALWAYS: Namespace by credential type and scope
db_store = SecureCredentialStore("database")
db_store.store("password", "...")

api_store = SecureCredentialStore("api-keys")
api_store.store("openai-key", "...")

encryption_store = SecureCredentialStore("encryption")
encryption_store.store("master-key", "...")

ssh_store = SecureCredentialStore("ssh")
ssh_store.store("private-key", "...")
```

**Why Better**:
- Isolated blast radius per credential type
- Granular access control possible
- Independent rotation schedules
- Better audit trails
- Principle of least privilege

---

## 6. Ignoring Keyring Backend Verification

### Anti-Pattern

```python
# NEVER: Use keyring without verification
import keyring

class UnsafeStore:
    def __init__(self, namespace: str):
        self._service = f"com.app.{namespace}"
        # No backend check!

    def store(self, key: str, value: str):
        keyring.set_password(self._service, key, value)
```

### Why This Is Dangerous

On systems without secure keyring (e.g., headless Linux), `keyring` falls back to:
- **PlaintextKeyring**: Credentials in `~/.local/share/python_keyring/keyring_pass.cfg`
- **Plaintext files**: No encryption, world-readable
- **Silent degradation**: No warning of insecure storage

### Correct Approach

```python
# ALWAYS: Verify secure backend at initialization
import keyring
from keyring.errors import KeyringError

class SecureCredentialStore:
    def __init__(self, namespace: str):
        self._service = f"com.app.{namespace}"
        self._verify_backend()

    def _verify_backend(self):
        """Verify secure keyring backend is available."""
        backend = keyring.get_keyring()
        backend_name = type(backend).__name__

        insecure_backends = [
            'PlaintextKeyring',
            'NullKeyring',
            'ChainerBackend',
            'fail.Keyring'
        ]

        if backend_name in insecure_backends:
            raise RuntimeError(
                f"Insecure keyring backend: {backend_name}. "
                f"Install secure backend: pip install keyrings.alt"
            )

        logger.info("keychain.backend.verified", extra={'backend': backend_name})
```

**Why Better**:
- Fails fast on insecure systems
- Explicit security requirement
- Clear error messages
- Prevents silent credential exposure

---

## 7. Credentials in Test Fixtures

### Anti-Pattern

```python
# NEVER: Real credentials in tests
class TestAPIClient:
    def test_authentication(self):
        client = APIClient(api_key="sk-real-production-key")  # NEVER!
        response = client.make_request()
        assert response.status_code == 200

# NEVER: Credentials in test data files
# tests/fixtures/credentials.json
{
    "api_key": "sk-1234567890",
    "database_password": "production-password"
}
```

### Why This Is Dangerous

- **Committed to git**: Test files in version control
- **Shared with team**: All developers see credentials
- **CI/CD exposure**: Visible in build logs
- **External services**: Tests may use real APIs
- **Accidental use**: Production credentials in tests

### Correct Approach

```python
# ALWAYS: Mock keyring in tests
import pytest
from unittest.mock import MagicMock, patch

class TestAPIClient:
    @patch('keyring.get_password')
    def test_authentication(self, mock_get_password):
        mock_get_password.return_value = "test-key-12345"

        client = APIClient()  # Retrieves from mocked keyring
        response = client.make_request()

        assert response.status_code == 200
        mock_get_password.assert_called_once()

# For integration tests, use test-specific keyring namespace
@pytest.fixture
def test_credentials():
    store = SecureCredentialStore("test-environment")
    store.store("api-key", "test-key-12345")
    yield store
    # Cleanup
    store.delete("api-key")
```

**Why Better**:
- No real credentials in tests
- Tests run without production access
- Safe to commit test code
- Fast tests (no real API calls)
- Isolated test environment

---

## 8. Synchronous Keychain Calls in Hot Path

### Anti-Pattern

```python
# NEVER: Keychain access per request
@app.route('/api/data')
def get_data():
    api_key = keyring.get_password("app", "api-key")  # 50-200ms per request!
    data = external_api.fetch(api_key)
    return jsonify(data)
```

### Why This Is Bad

- **High latency**: 50-200ms added to every request
- **Keychain service overload**: Excessive IPC calls
- **Scalability issues**: 10 req/sec = 1-2 seconds in keychain calls
- **User experience**: Slow response times

### Correct Approach

```python
# ALWAYS: Cache credentials at startup
class APIService:
    def __init__(self):
        store = SecureCredentialStore("app")
        self._api_key = store.retrieve("api-key")  # Once at startup
        self._cache_time = time.time()

    def get_data(self):
        # Use cached credential (nanoseconds, not milliseconds)
        return external_api.fetch(self._api_key)

# Initialize once
api_service = APIService()

@app.route('/api/data')
def get_data():
    data = api_service.get_data()
    return jsonify(data)
```

**Why Better**:
- One-time startup cost
- Sub-microsecond cached access
- Scales to high request rates
- Better user experience

---

## Summary of Anti-Patterns

| Anti-Pattern | Impact | Correct Approach |
|--------------|--------|------------------|
| Environment variables | Process exposure, logs | OS keychain |
| Hardcoded credentials | Git history, sharing | Runtime retrieval |
| File storage | Backup exposure, permissions | Platform keychain |
| Logging credentials | Compliance, exposure | Log metadata only |
| Single service name | No isolation, blast radius | Namespace by type |
| No backend verification | Silent insecurity | Verify at startup |
| Credentials in tests | Version control exposure | Mock keyring |
| Hot path keychain calls | Performance degradation | Startup caching |

**Golden Rule**: If you can see the credential in plain text anywhere (logs, files, env, code), you're doing it wrong.
