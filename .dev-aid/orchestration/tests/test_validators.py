import pytest
from pydantic import ValidationError

from router.validators import CostLimit, ExecuteRequest, ModelConfig, SafePath, SubprocessCommand


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


class TestCostLimit:
    def test_valid(self):
        limit = CostLimit(daily_limit=10.0)
        assert limit.daily_limit == 10.0

    def test_invalid_threshold(self):
        with pytest.raises(ValidationError, match="less than or equal to"):
            CostLimit(daily_limit=10.0, warning_threshold=1.5)
