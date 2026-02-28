import pytest
from pydantic import ValidationError

from router.validators import (
    APIKeyConfig,
    CostLimit,
    ExecuteRequest,
    MCPServerConfig,
    ModelConfig,
    SafePath,
    SubprocessCommand,
)


class TestExecuteRequest:
    def test_valid_request(self):
        req = ExecuteRequest(request="Write code", mode="solo", context_size=100)
        assert req.request == "Write code"

    def test_invalid_injection(self):
        with pytest.raises(ValidationError, match="unsafe pattern"):
            ExecuteRequest(request="import os; os.system('rm -rf /')")

    def test_null_bytes(self):
        with pytest.raises(ValidationError, match="Null bytes"):
            ExecuteRequest(request="hello\0world")


class TestModelConfig:
    def test_valid_config(self):
        config = ModelConfig(provider="anthropic", model_id="claude-3", max_tokens=100)
        assert config.provider == "anthropic"

    def test_invalid_model_id(self):
        with pytest.raises(ValidationError, match="alphanumeric"):
            ModelConfig(provider="anthropic", model_id="claude; rm -rf")


class TestAPIKeyConfig:
    def test_valid_api_key(self):
        config = APIKeyConfig(provider="anthropic", api_key="sk-ant-1234567890abcdef")
        assert config.api_key == "sk-ant-1234567890abcdef"

    def test_whitespace_only_key_rejected(self):
        with pytest.raises(ValidationError, match="at least 10 characters"):
            APIKeyConfig(provider="anthropic", api_key="          ")

    def test_key_with_newline_rejected(self):
        with pytest.raises(ValidationError, match="invalid characters"):
            APIKeyConfig(provider="openai", api_key="sk-12345\n67890abcdef")


class TestMCPServerConfig:
    def test_valid_mcp_config(self):
        config = MCPServerConfig(name="test-server", command="node", args=["server.js"])
        assert config.name == "test-server"
        assert config.command == "node"

    def test_invalid_command_prefix_rejected(self):
        with pytest.raises(ValidationError, match="Command must start with"):
            MCPServerConfig(name="bad-server", command="curl http://evil.com")

    def test_valid_command_accepted(self):
        config = MCPServerConfig(name="py-server", command="python3", args=["-m", "mcp"])
        assert config.command == "python3"


class TestSafePath:
    def test_traversal(self):
        with pytest.raises(ValidationError, match="traversal"):
            SafePath(path="../etc/passwd")

    def test_containment(self):
        with pytest.raises(ValidationError, match="not within"):
            SafePath(path="/etc/passwd", base_dir="/app")

    def test_valid(self):
        path = SafePath(path="file.txt", base_dir="/app")
        # Note: logic uses resolve(), so in test environment /app might not exist or resolve differently.
        # We accept this might fail if /app doesn't exist.
        # Let's use cwd
        import os

        cwd = os.getcwd()
        path = SafePath(path="file.txt", base_dir=cwd)
        assert path.path == "file.txt"

    def test_control_chars_rejected(self):
        with pytest.raises(ValidationError, match="control characters"):
            SafePath(path="file\x01.txt")


class TestSubprocessCommand:
    def test_valid(self):
        cmd = SubprocessCommand(program="git", args=["status"])
        assert cmd.program == "git"

    def test_injection_args(self):
        with pytest.raises(ValidationError, match="shell metacharacters"):
            SubprocessCommand(program="git", args=["; rm -rf /"])

    def test_invalid_program(self):
        with pytest.raises(ValidationError, match="Input should be"):
            SubprocessCommand(program="evil_script", args=[])

    def test_null_byte_in_arg(self):
        with pytest.raises(ValidationError, match="null bytes"):
            SubprocessCommand(program="git", args=["status\0evil"])

    def test_validate_cwd_none(self):
        cmd = SubprocessCommand(program="git", args=["status"], cwd=None)
        assert cmd.cwd is None

    def test_validate_cwd_invalid(self):
        with pytest.raises(ValidationError, match="traversal"):
            SubprocessCommand(program="git", args=["status"], cwd="../../../etc")


class TestCostLimit:
    def test_valid(self):
        limit = CostLimit(daily_limit=10.0)
        assert limit.daily_limit == 10.0

    def test_invalid_threshold(self):
        with pytest.raises(ValidationError, match="less than or equal to"):
            CostLimit(daily_limit=10.0, warning_threshold=1.5)

    def test_threshold_exactly_one(self):
        with pytest.raises(ValidationError, match="less than 1.0"):
            CostLimit(daily_limit=10.0, warning_threshold=1.0)
