"""
Tests for input validation models
"""

import pytest
from pydantic import ValidationError

from router.validators import (
    ExecuteRequest,
    SafePath,
    SubprocessCommand,
    APIKeyConfig,
    ModelConfig,
    CostLimit
)


class TestExecuteRequest:
    """Test ExecuteRequest validation"""

    def test_valid_request(self):
        """Test valid execute request"""
        req = ExecuteRequest(
            request="Implement user authentication",
            mode="solo",
            context_size=1000,
            use_mcp=True
        )
        assert req.request == "Implement user authentication"
        assert req.mode == "solo"
        assert req.context_size == 1000

    def test_request_too_short(self):
        """Test request that's too short"""
        with pytest.raises(ValidationError, match="at least 1 character"):
            ExecuteRequest(request="")

    def test_request_too_long(self):
        """Test request that's too long"""
        long_request = "x" * 50001
        with pytest.raises(ValidationError):
            ExecuteRequest(request=long_request)

    def test_invalid_mode(self):
        """Test invalid orchestration mode"""
        with pytest.raises(ValidationError):
            ExecuteRequest(request="test", mode="invalid_mode")

    def test_negative_context_size(self):
        """Test negative context size"""
        with pytest.raises(ValidationError):
            ExecuteRequest(request="test", context_size=-1)

    def test_null_byte_rejection(self):
        """Test that null bytes are rejected"""
        with pytest.raises(ValidationError, match="Null bytes not allowed"):
            ExecuteRequest(request="test\x00injection")

    def test_injection_pattern_detection(self):
        """Test detection of injection patterns"""
        dangerous_patterns = [
            "__import__('os').system('ls')",
            "eval('malicious code')",
            "exec('bad code')",
            "compile('code', 'string', 'exec')",
            "../../../etc/passwd",
            "${java:runtime}",
        ]

        for pattern in dangerous_patterns:
            with pytest.raises(ValidationError, match="potentially unsafe pattern"):
                ExecuteRequest(request=pattern)

    def test_whitespace_stripping(self):
        """Test that whitespace is stripped"""
        req = ExecuteRequest(request="  test request  ")
        assert req.request == "test request"


class TestSafePath:
    """Test SafePath validation"""

    def test_valid_relative_path(self):
        """Test valid relative path"""
        path = SafePath(path="configs/settings.json", base_dir="/app")
        assert path.path == "configs/settings.json"

    def test_path_traversal_detection(self):
        """Test path traversal detection"""
        with pytest.raises(ValidationError, match="traversal"):
            SafePath(path="../../../etc/passwd", base_dir="/app")

    def test_absolute_path_with_base_dir(self):
        """Test that absolute paths are rejected when base_dir is set"""
        with pytest.raises(ValidationError, match="Absolute paths not allowed"):
            SafePath(path="/etc/passwd", base_dir="/app")

    def test_null_byte_in_path(self):
        """Test null byte rejection in path"""
        with pytest.raises(ValidationError, match="invalid characters"):
            SafePath(path="test\x00file.txt")

    def test_newline_in_path(self):
        """Test newline rejection in path"""
        with pytest.raises(ValidationError, match="invalid characters"):
            SafePath(path="test\nfile.txt")


class TestSubprocessCommand:
    """Test SubprocessCommand validation"""

    def test_valid_git_command(self):
        """Test valid git command"""
        cmd = SubprocessCommand(
            program="git",
            args=["status", "--short"],
            cwd="/app/repo"
        )
        assert cmd.program == "git"
        assert cmd.args == ["status", "--short"]

    def test_invalid_program(self):
        """Test that only allowed programs are accepted"""
        with pytest.raises(ValidationError):
            SubprocessCommand(program="rm", args=["-rf", "/"])

    def test_shell_metacharacters_detection(self):
        """Test detection of shell metacharacters in arguments"""
        dangerous_args = [
            "test; rm -rf /",
            "test | cat /etc/passwd",
            "test && evil",
            "test `whoami`",
            "test $(whoami)",
            "test\nrm -rf /",
        ]

        for arg in dangerous_args:
            with pytest.raises(ValidationError, match="shell metacharacters"):
                SubprocessCommand(program="git", args=[arg])

    def test_null_bytes_in_args(self):
        """Test null byte detection in arguments"""
        with pytest.raises(ValidationError, match="null bytes"):
            SubprocessCommand(program="git", args=["test\x00"])

    def test_too_many_args(self):
        """Test argument count limit"""
        too_many = ["arg"] * 51
        with pytest.raises(ValidationError):
            SubprocessCommand(program="git", args=too_many)


class TestAPIKeyConfig:
    """Test APIKeyConfig validation"""

    def test_valid_api_key(self):
        """Test valid API key"""
        config = APIKeyConfig(
            provider="anthropic",
            api_key="sk-ant-1234567890abcdef"
        )
        assert config.provider == "anthropic"
        assert config.api_key == "sk-ant-1234567890abcdef"

    def test_empty_api_key(self):
        """Test empty API key rejection"""
        with pytest.raises(ValidationError, match="cannot be empty"):
            APIKeyConfig(provider="anthropic", api_key="   ")

    def test_api_key_with_newline(self):
        """Test API key with newline"""
        with pytest.raises(ValidationError, match="invalid characters"):
            APIKeyConfig(provider="anthropic", api_key="key\nmalicious")

    def test_api_key_with_null_byte(self):
        """Test API key with null byte"""
        with pytest.raises(ValidationError, match="invalid characters"):
            APIKeyConfig(provider="anthropic", api_key="key\x00evil")

    def test_api_key_too_short(self):
        """Test API key that's too short"""
        with pytest.raises(ValidationError):
            APIKeyConfig(provider="anthropic", api_key="short")


class TestModelConfig:
    """Test ModelConfig validation"""

    def test_valid_model_config(self):
        """Test valid model configuration"""
        config = ModelConfig(
            provider="anthropic",
            model_id="claude-sonnet-4",
            max_tokens=4096,
            temperature=0.7
        )
        assert config.provider == "anthropic"
        assert config.model_id == "claude-sonnet-4"

    def test_invalid_model_id(self):
        """Test model ID with invalid characters"""
        with pytest.raises(ValidationError, match="alphanumeric"):
            ModelConfig(
                provider="anthropic",
                model_id="model; rm -rf /",
                max_tokens=4096
            )

    def test_temperature_out_of_range(self):
        """Test temperature validation"""
        with pytest.raises(ValidationError):
            ModelConfig(
                provider="anthropic",
                model_id="claude-sonnet",
                temperature=3.0  # Too high
            )

    def test_negative_max_tokens(self):
        """Test negative max_tokens"""
        with pytest.raises(ValidationError):
            ModelConfig(
                provider="anthropic",
                model_id="claude-sonnet",
                max_tokens=-1
            )


class TestCostLimit:
    """Test CostLimit validation"""

    def test_valid_cost_limit(self):
        """Test valid cost limit"""
        limit = CostLimit(daily_limit=100.0, warning_threshold=0.8)
        assert limit.daily_limit == 100.0
        assert limit.warning_threshold == 0.8

    def test_negative_daily_limit(self):
        """Test negative daily limit"""
        with pytest.raises(ValidationError):
            CostLimit(daily_limit=-10.0)

    def test_warning_threshold_too_high(self):
        """Test warning threshold >= 1.0"""
        with pytest.raises(ValidationError, match="less than 1.0"):
            CostLimit(daily_limit=100.0, warning_threshold=1.0)

    def test_warning_threshold_negative(self):
        """Test negative warning threshold"""
        with pytest.raises(ValidationError):
            CostLimit(daily_limit=100.0, warning_threshold=-0.1)


class TestSecurityDefaults:
    """Test security defaults across all models"""

    def test_extra_fields_forbidden(self):
        """Test that extra fields are rejected"""
        with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
            ExecuteRequest(
                request="test",
                extra_field="should be rejected"
            )

    def test_null_bytes_rejected_universally(self):
        """Test null byte rejection across models"""
        # Test in ExecuteRequest
        with pytest.raises(ValidationError, match="Null bytes"):
            ExecuteRequest(request="test\x00")

        # Test in SafePath
        with pytest.raises(ValidationError):
            SafePath(path="file\x00.txt")

        # Test in SubprocessCommand args
        with pytest.raises(ValidationError):
            SubprocessCommand(program="git", args=["test\x00"])
