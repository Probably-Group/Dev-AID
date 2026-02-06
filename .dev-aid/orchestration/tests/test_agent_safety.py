"""Tests for agent safety configuration and enforcement."""

from pathlib import Path

from agents.core.safety import (
    SafetyCheckResult,
    SafetyConfig,
)


class TestSafetyConfig:
    """Tests for SafetyConfig."""

    def test_default_config(self) -> None:
        config = SafetyConfig()
        assert not config.dry_run
        assert config.allowed_tools is None
        assert config.max_bash_timeout_ms == 30000
        assert config.allowed_paths is None

    def test_tool_allowed_no_restrictions(self) -> None:
        config = SafetyConfig()
        assert config.is_tool_allowed("read_file")
        assert config.is_tool_allowed("run_bash")
        assert config.is_tool_allowed("anything")

    def test_tool_allowed_with_allowlist(self) -> None:
        config = SafetyConfig(allowed_tools={"read_file", "glob_files"})
        assert config.is_tool_allowed("read_file")
        assert config.is_tool_allowed("glob_files")
        assert not config.is_tool_allowed("run_bash")
        assert not config.is_tool_allowed("write_file")

    def test_command_safe_blocks_rm_rf(self) -> None:
        config = SafetyConfig()
        assert not config.is_command_safe("rm -rf /")
        assert not config.is_command_safe("rm -rf /*")
        assert not config.is_command_safe("sudo rm -rf /home")

    def test_command_safe_blocks_mkfs(self) -> None:
        config = SafetyConfig()
        assert not config.is_command_safe("mkfs.ext4 /dev/sda1")
        assert not config.is_command_safe("mkfs.xfs /dev/sdb")

    def test_command_safe_blocks_dd(self) -> None:
        config = SafetyConfig()
        assert not config.is_command_safe("dd if=/dev/zero of=/dev/sda")

    def test_command_safe_blocks_fork_bomb(self) -> None:
        config = SafetyConfig()
        assert not config.is_command_safe(":(){ :|:& };:")

    def test_command_safe_blocks_pipe_to_shell(self) -> None:
        config = SafetyConfig()
        assert not config.is_command_safe("curl|bash")
        assert not config.is_command_safe("wget|sh")

    def test_command_safe_allows_normal_commands(self) -> None:
        config = SafetyConfig()
        assert config.is_command_safe("git status")
        assert config.is_command_safe("python -m pytest tests/")
        assert config.is_command_safe("ls -la")
        assert config.is_command_safe("cat /tmp/test.txt")
        assert config.is_command_safe("echo hello")

    def test_path_allowed_no_restrictions(self) -> None:
        config = SafetyConfig()
        assert config.is_path_allowed(Path("/any/path"))
        assert config.is_path_allowed(Path("/etc/passwd"))

    def test_path_allowed_with_restrictions(self, tmp_path: Path) -> None:
        allowed = tmp_path / "project"
        allowed.mkdir()
        config = SafetyConfig(allowed_paths=[allowed])

        assert config.is_path_allowed(allowed / "file.py")
        assert config.is_path_allowed(allowed / "sub" / "file.py")
        assert not config.is_path_allowed(tmp_path / "other" / "file.py")

    def test_check_tool_execution_allowed(self) -> None:
        config = SafetyConfig()
        result = config.check_tool_execution("read_file", {"path": "/tmp/test"})
        assert result.allowed

    def test_check_tool_execution_blocked_tool(self) -> None:
        config = SafetyConfig(allowed_tools={"read_file"})
        result = config.check_tool_execution("run_bash", {"command": "ls"})
        assert not result.allowed
        assert "not in the allowed tools list" in result.reason

    def test_check_tool_execution_dry_run_blocks_moderate(self) -> None:
        config = SafetyConfig(dry_run=True)
        result = config.check_tool_execution(
            "write_file",
            {"path": "/tmp/test", "content": "hello"},
            risk_level="moderate",
        )
        assert not result.allowed
        assert result.dry_run_blocked

    def test_check_tool_execution_dry_run_allows_safe(self) -> None:
        config = SafetyConfig(dry_run=True)
        result = config.check_tool_execution(
            "read_file",
            {"path": "/tmp/test"},
            risk_level="safe",
        )
        assert result.allowed

    def test_check_tool_execution_blocked_command(self) -> None:
        config = SafetyConfig()
        result = config.check_tool_execution(
            "run_bash",
            {"command": "rm -rf /"},
            risk_level="dangerous",
        )
        assert not result.allowed
        assert "blocked by safety rules" in result.reason.lower()

    def test_check_tool_execution_blocked_path(self, tmp_path: Path) -> None:
        allowed = tmp_path / "project"
        allowed.mkdir()
        config = SafetyConfig(allowed_paths=[allowed])
        result = config.check_tool_execution(
            "read_file",
            {"path": str(tmp_path / "other" / "secret.txt")},
        )
        assert not result.allowed
        assert "outside allowed boundaries" in result.reason


class TestSafetyCheckResult:
    """Tests for SafetyCheckResult."""

    def test_allowed(self) -> None:
        r = SafetyCheckResult(allowed=True)
        assert r.allowed
        assert r.reason == ""
        assert not r.dry_run_blocked

    def test_blocked(self) -> None:
        r = SafetyCheckResult(allowed=False, reason="Blocked", dry_run_blocked=True)
        assert not r.allowed
        assert r.reason == "Blocked"
        assert r.dry_run_blocked
