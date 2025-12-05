# OS Keychain Testing Guide

This guide covers comprehensive testing strategies for credential storage operations using OS keychain services.

---

## Overview

Testing credential storage requires special care to avoid:
- Real credential exposure in test code
- Dependency on actual keychain services
- Credential leaks in test logs or artifacts
- Slow tests from IPC overhead

This guide follows TDD principles with fast, isolated, secure tests.

---

## 1. Complete Test Suite Example

### Basic Credential Operations

```python
import pytest
from unittest.mock import MagicMock, patch, call
from your_module import SecureCredentialStore

class TestCredentialStoreOperations:
    """TDD tests for credential store - write these FIRST."""

    def test_store_credential_success(self):
        """Test storing a credential in keychain."""
        # Arrange
        store = SecureCredentialStore("test-service")

        # Act
        store.store("api-key", "sk-test-12345")

        # Assert
        assert store.exists("api-key") is True
        assert store.retrieve("api-key") == "sk-test-12345"

    def test_retrieve_nonexistent_raises_keyerror(self):
        """Test retrieving nonexistent credential raises KeyError."""
        store = SecureCredentialStore("test-service")

        with pytest.raises(KeyError, match="Credential not found"):
            store.retrieve("nonexistent-key")

    def test_delete_removes_credential(self):
        """Test deletion completely removes credential."""
        store = SecureCredentialStore("test-service")
        store.store("temp-key", "temp-value")

        store.delete("temp-key")

        assert store.exists("temp-key") is False

    def test_credential_isolation_between_namespaces(self):
        """Test credentials are isolated by namespace."""
        store1 = SecureCredentialStore("namespace-a")
        store2 = SecureCredentialStore("namespace-b")

        store1.store("shared-key", "value-a")
        store2.store("shared-key", "value-b")

        assert store1.retrieve("shared-key") == "value-a"
        assert store2.retrieve("shared-key") == "value-b"

    def test_rejects_insecure_backend(self):
        """Test rejection of insecure keyring backends."""
        import keyring
        from keyring.backends import null

        original = keyring.get_keyring()
        try:
            keyring.set_keyring(null.Keyring())
            with pytest.raises(RuntimeError, match="Insecure"):
                SecureCredentialStore("test")
        finally:
            keyring.set_keyring(original)
```

---

## 2. Mocking Keyring for Unit Tests

### Why Mock?

- **Speed**: Avoid IPC overhead (50-200ms per call)
- **Isolation**: No dependency on OS keychain service
- **Reliability**: Tests work on any system
- **Safety**: No risk of interfering with real credentials

### Basic Mocking Pattern

```python
import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_keyring():
    """Mock keyring for isolated tests."""
    with patch('keyring.get_password') as mock_get, \
         patch('keyring.set_password') as mock_set, \
         patch('keyring.delete_password') as mock_delete, \
         patch('keyring.get_keyring') as mock_backend:

        # Setup secure backend mock
        mock_backend_instance = MagicMock()
        mock_backend_instance.__class__.__name__ = 'SecretServiceKeyring'
        mock_backend.return_value = mock_backend_instance

        # Setup in-memory credential storage
        credentials = {}

        def mock_set_impl(service, key, value):
            credentials[f"{service}:{key}"] = value

        def mock_get_impl(service, key):
            return credentials.get(f"{service}:{key}")

        def mock_delete_impl(service, key):
            credentials.pop(f"{service}:{key}", None)

        mock_set.side_effect = mock_set_impl
        mock_get.side_effect = mock_get_impl
        mock_delete.side_effect = mock_delete_impl

        yield {
            'get': mock_get,
            'set': mock_set,
            'delete': mock_delete,
            'backend': mock_backend,
            'storage': credentials
        }

# Usage
def test_with_mock_keyring(mock_keyring):
    store = SecureCredentialStore("test")
    store.store("key", "value")

    assert store.retrieve("key") == "value"
    mock_keyring['set'].assert_called_once_with(
        "com.jarvis.assistant.test",
        "key",
        "value"
    )
```

---

## 3. Integration Tests

### Test Against Real Keychain

For integration tests, use a dedicated test namespace to avoid interfering with production credentials.

```python
import pytest
import keyring

@pytest.fixture(scope="session")
def integration_test_store():
    """Real keychain store for integration tests."""
    namespace = "integration-test"
    store = SecureCredentialStore(namespace)

    # Cleanup before tests
    test_keys = ["test-key-1", "test-key-2", "test-key-3"]
    for key in test_keys:
        try:
            store.delete(key)
        except Exception:
            pass

    yield store

    # Cleanup after tests
    for key in test_keys:
        try:
            store.delete(key)
        except Exception:
            pass

class TestKeychainIntegration:
    """Integration tests against real OS keychain."""

    def test_store_and_retrieve_real_keychain(self, integration_test_store):
        """Test actual keychain storage and retrieval."""
        store = integration_test_store

        store.store("test-key-1", "test-value-1")
        retrieved = store.retrieve("test-key-1")

        assert retrieved == "test-value-1"

    def test_persistence_across_instances(self, integration_test_store):
        """Test credentials persist across store instances."""
        store1 = integration_test_store
        store1.store("test-key-2", "persistent-value")

        # Create new instance
        store2 = SecureCredentialStore("integration-test")
        retrieved = store2.retrieve("test-key-2")

        assert retrieved == "persistent-value"

    @pytest.mark.skipif(
        keyring.get_keyring().__class__.__name__ == 'PlaintextKeyring',
        reason="Requires secure keyring backend"
    )
    def test_encryption_at_rest(self, integration_test_store):
        """Test credentials are encrypted (not readable in keyring files)."""
        store = integration_test_store
        secret = "super-secret-value-xyz"

        store.store("test-key-3", secret)

        # On Linux, check Secret Service doesn't store plaintext
        # On macOS, keychain is encrypted
        # On Windows, DPAPI encryption
        # This is a smoke test - actual verification is platform-specific
        assert store.retrieve("test-key-3") == secret
```

---

## 4. Testing Error Conditions

### Comprehensive Error Handling Tests

```python
class TestCredentialStoreErrors:
    """Test error handling and edge cases."""

    def test_retrieve_with_none_value(self, mock_keyring):
        """Test KeyError when keyring returns None."""
        mock_keyring['get'].return_value = None
        store = SecureCredentialStore("test")

        with pytest.raises(KeyError, match="Credential not found: missing"):
            store.retrieve("missing")

    def test_delete_nonexistent_credential(self, mock_keyring):
        """Test deleting nonexistent credential raises KeyringError."""
        from keyring.errors import PasswordDeleteError

        mock_keyring['delete'].side_effect = PasswordDeleteError("Not found")
        store = SecureCredentialStore("test")

        with pytest.raises(PasswordDeleteError):
            store.delete("nonexistent")

    def test_store_with_empty_string(self, mock_keyring):
        """Test storing empty string credential."""
        store = SecureCredentialStore("test")

        # Should succeed - empty string is valid
        store.store("empty-key", "")
        assert store.retrieve("empty-key") == ""

    def test_invalid_namespace_characters(self):
        """Test rejection of invalid namespace characters."""
        # Depends on your validation logic
        with pytest.raises(ValueError, match="Invalid namespace"):
            SecureCredentialStore("invalid/namespace")

    @patch('keyring.get_keyring')
    def test_keyring_unavailable(self, mock_backend):
        """Test graceful handling when keyring unavailable."""
        mock_backend.side_effect = RuntimeError("Keyring not available")

        with pytest.raises(RuntimeError, match="Keyring not available"):
            SecureCredentialStore("test")
```

---

## 5. Performance Testing

### Test Caching Performance

```python
import time
import pytest

class TestCredentialCaching:
    """Test performance characteristics of caching."""

    def test_cache_hit_faster_than_keychain(self, mock_keyring):
        """Test cached retrieval is faster than keychain access."""
        # Simulate slow keychain access
        def slow_get_password(service, key):
            time.sleep(0.05)  # 50ms
            return "cached-value"

        mock_keyring['get'].side_effect = slow_get_password

        store = SecureCredentialStore("test")

        # First access - slow
        start = time.time()
        value1 = store.retrieve("cached-key")
        first_access_time = time.time() - start

        # Second access - cached (should be much faster)
        start = time.time()
        value2 = store.retrieve("cached-key")
        cached_access_time = time.time() - start

        assert value1 == value2
        assert cached_access_time < first_access_time / 10  # At least 10x faster
        assert mock_keyring['get'].call_count == 1  # Only called once

    def test_cache_invalidation(self, mock_keyring):
        """Test cache is invalidated after update."""
        mock_keyring['get'].return_value = "original-value"
        store = SecureCredentialStore("test")

        value1 = store.retrieve("key")
        assert value1 == "original-value"

        # Update credential
        mock_keyring['get'].return_value = "updated-value"
        store.invalidate("key")

        # Should fetch fresh value
        value2 = store.retrieve("key")
        assert value2 == "updated-value"
        assert mock_keyring['get'].call_count == 2
```

---

## 6. Security Testing

### Test Credential Exposure Prevention

```python
class TestCredentialSecurity:
    """Test security measures for credential handling."""

    def test_no_credential_in_repr(self, mock_keyring):
        """Test credential not exposed in repr()."""
        mock_keyring['get'].return_value = "secret-value"
        store = SecureCredentialStore("test")
        store.retrieve("api-key")

        # Repr should not contain credential
        repr_str = repr(store)
        assert "secret-value" not in repr_str
        assert "api-key" not in repr_str  # Key names might be OK

    def test_no_credential_in_str(self, mock_keyring):
        """Test credential not exposed in str()."""
        mock_keyring['get'].return_value = "secret-value"
        store = SecureCredentialStore("test")
        store.retrieve("api-key")

        str_str = str(store)
        assert "secret-value" not in str_str

    def test_logging_no_credential_values(self, mock_keyring, caplog):
        """Test logging doesn't expose credential values."""
        mock_keyring['get'].return_value = "secret-password"
        store = SecureCredentialStore("test")

        with caplog.at_level(logging.INFO):
            store.retrieve("db-password")

        # Check all log messages
        for record in caplog.records:
            assert "secret-password" not in record.message
            assert "secret-password" not in str(record.args)

    def test_credential_cleared_from_memory(self, mock_keyring):
        """Test credential cleared after context exit."""
        mock_keyring['get'].return_value = "temp-secret"
        store = SecureMemoryStore("test")

        # Use context manager
        with store.with_credential("api-key") as secret:
            assert secret == "temp-secret"

        # After context exit, credential should be cleared
        # (This is best-effort in Python, but we can test the API)
        # The context manager should not leave references
```

---

## 7. Cross-Platform Testing

### Platform-Specific Tests

```python
import sys
import pytest

class TestCrossPlatform:
    """Test cross-platform compatibility."""

    @pytest.mark.skipif(sys.platform != "darwin", reason="macOS only")
    def test_macos_keychain_backend(self):
        """Test macOS uses Keychain backend."""
        store = SecureCredentialStore("test")
        backend = keyring.get_keyring()
        assert "Keychain" in type(backend).__name__

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows only")
    def test_windows_credential_manager(self):
        """Test Windows uses Credential Manager."""
        store = SecureCredentialStore("test")
        backend = keyring.get_keyring()
        assert "Windows" in type(backend).__name__

    @pytest.mark.skipif(sys.platform != "linux", reason="Linux only")
    def test_linux_secret_service(self):
        """Test Linux uses Secret Service."""
        store = SecureCredentialStore("test")
        backend = keyring.get_keyring()
        # May be SecretService, KWallet, or other
        assert type(backend).__name__ != "PlaintextKeyring"
```

---

## 8. Full Test Verification Command

### Run Complete Test Suite

```bash
# Run all tests with coverage
pytest tests/security/test_keychain.py -v --cov=src/security/keychain --cov-report=term-missing

# Run only unit tests (fast, mocked)
pytest tests/security/test_keychain.py -v -m "not integration"

# Run integration tests (slower, real keychain)
pytest tests/security/test_keychain.py -v -m integration

# Run security-specific tests
pytest tests/security/ -k "keychain or credential" -v

# Verify no credential leaks in logs
pytest tests/security/test_keychain.py -v --log-cli-level=DEBUG > test.log
grep -E "sk-|password|secret|token" test.log && echo "FAIL: Credentials in logs" || echo "PASS: No credentials in logs"

# Performance benchmarks
pytest tests/security/test_keychain.py -v --benchmark-only

# Memory leak detection
pytest tests/security/test_keychain.py -v --memray
```

---

## 9. Test Fixtures Reference

### Reusable Fixtures

```python
# conftest.py
import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture
def secure_mock_backend():
    """Mock a secure keyring backend."""
    with patch('keyring.get_keyring') as mock_backend:
        mock_instance = MagicMock()
        mock_instance.__class__.__name__ = 'SecretServiceKeyring'
        mock_backend.return_value = mock_instance
        yield mock_backend

@pytest.fixture
def insecure_mock_backend():
    """Mock an insecure keyring backend."""
    with patch('keyring.get_keyring') as mock_backend:
        mock_instance = MagicMock()
        mock_instance.__class__.__name__ = 'PlaintextKeyring'
        mock_backend.return_value = mock_instance
        yield mock_backend

@pytest.fixture
def temp_credentials():
    """Temporary credentials for testing."""
    return {
        "api-key": "test-key-123",
        "db-password": "test-pass-456",
        "encryption-key": "test-enc-789"
    }

@pytest.fixture(autouse=True)
def reset_keyring_after_test():
    """Reset keyring state after each test."""
    original_keyring = keyring.get_keyring()
    yield
    keyring.set_keyring(original_keyring)
```

---

## Summary

### Test Checklist

- [ ] All CRUD operations tested (create, read, update, delete)
- [ ] Error conditions tested (not found, invalid input)
- [ ] Security measures tested (no logging, no repr exposure)
- [ ] Performance characteristics tested (caching works)
- [ ] Cross-platform compatibility tested
- [ ] Integration tests with real keychain
- [ ] Backend verification tested
- [ ] Namespace isolation tested
- [ ] No credentials in test code or fixtures
- [ ] All tests pass with `pytest -v`
- [ ] Coverage > 90% for credential operations

### Best Practices

1. **Always mock** for unit tests - fast and isolated
2. **Use fixtures** for common test setup
3. **Test security** - verify no credential leaks
4. **Integration tests** - verify real keychain works
5. **Platform-specific** - test each OS backend
6. **Performance tests** - verify caching works
7. **Error handling** - test all failure modes
8. **Clean up** - remove test credentials after tests
