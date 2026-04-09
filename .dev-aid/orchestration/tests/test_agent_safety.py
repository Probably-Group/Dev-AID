"""Tests for agent safety configuration and enforcement."""

from pathlib import Path

from agents.core.safety import SafetyCheckResult, SafetyConfig


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

    def test_command_safe_blocks_split_flags(self) -> None:
        """rm with split flags should be blocked."""
        config = SafetyConfig()
        assert not config.is_command_safe("rm -r -f /home")
        assert not config.is_command_safe("rm -f -r /var")

    def test_command_safe_blocks_long_form_flags(self) -> None:
        """rm with long-form flags should be blocked."""
        config = SafetyConfig()
        assert not config.is_command_safe("rm --recursive --force /home")
        assert not config.is_command_safe("rm --force --recursive /var")

    def test_command_safe_blocks_chmod_root(self) -> None:
        """chmod 777 on root paths should be blocked."""
        config = SafetyConfig()
        assert not config.is_command_safe("chmod 777 /")
        assert not config.is_command_safe("chmod -R 777 /")

    def test_command_safe_allows_normal_commands(self) -> None:
        config = SafetyConfig()
        assert config.is_command_safe("git status")
        assert config.is_command_safe("python -m pytest tests/")
        assert config.is_command_safe("ls -la")
        assert config.is_command_safe("cat /tmp/test.txt")
        assert config.is_command_safe("echo hello")

    def test_command_safe_allows_rm_in_project(self) -> None:
        """rm on non-root paths should be allowed."""
        config = SafetyConfig()
        assert config.is_command_safe("rm -rf /tmp/test_dir")
        assert config.is_command_safe("rm build/output.o")

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


class TestDevAidScopeGuard:
    """Tests for the .dev-aid/ scope guard (issue #147)."""

    def _make_host_layout(self, tmp_path: Path) -> tuple[Path, Path]:
        """Create a fake host project with a .dev-aid/ scaffold inside it."""
        host = tmp_path / "host_project"
        host.mkdir()
        (host / "src").mkdir()
        (host / "src" / "main.py").write_text("# host source\n")
        scaffold = host / ".dev-aid"
        scaffold.mkdir()
        (scaffold / "config").mkdir()
        (scaffold / "config" / "models.json").write_text("{}")
        return host, scaffold

    def test_is_dev_aid_path_detects_scaffold(self, tmp_path: Path) -> None:
        host, scaffold = self._make_host_layout(tmp_path)
        assert SafetyConfig.is_dev_aid_path(scaffold / "config" / "models.json")
        assert SafetyConfig.is_dev_aid_path(scaffold / "skills" / "expert" / "x.md")

    def test_is_dev_aid_path_ignores_host_files(self, tmp_path: Path) -> None:
        host, _ = self._make_host_layout(tmp_path)
        assert not SafetyConfig.is_dev_aid_path(host / "src" / "main.py")
        assert not SafetyConfig.is_dev_aid_path(host / "README.md")

    def test_is_dev_aid_path_handles_nonexistent_path(self, tmp_path: Path) -> None:
        # About-to-be-created files should still match lexically.
        host, _ = self._make_host_layout(tmp_path)
        assert SafetyConfig.is_dev_aid_path(host / ".dev-aid" / "new" / "file.md")
        assert not SafetyConfig.is_dev_aid_path(host / "src" / "new.py")

    def test_write_to_scaffold_blocked_by_default(self, tmp_path: Path) -> None:
        host, scaffold = self._make_host_layout(tmp_path)
        config = SafetyConfig(allowed_paths=[host])
        result = config.check_tool_execution(
            "write_file",
            {"path": str(scaffold / "config" / "models.json"), "content": "{}"},
            risk_level="moderate",
        )
        assert not result.allowed
        assert "scaffold" in result.reason
        assert "scope=dev-aid" in result.reason

    def test_edit_scaffold_blocked_by_default(self, tmp_path: Path) -> None:
        host, scaffold = self._make_host_layout(tmp_path)
        config = SafetyConfig(allowed_paths=[host])
        result = config.check_tool_execution(
            "edit_file",
            {
                "path": str(scaffold / "config" / "models.json"),
                "old_string": "{}",
                "new_string": '{"x": 1}',
            },
            risk_level="moderate",
        )
        assert not result.allowed
        assert ".dev-aid" in result.reason

    def test_write_to_scaffold_allowed_with_opt_in(self, tmp_path: Path) -> None:
        host, scaffold = self._make_host_layout(tmp_path)
        config = SafetyConfig(allowed_paths=[host], allow_dev_aid_writes=True)
        result = config.check_tool_execution(
            "write_file",
            {"path": str(scaffold / "config" / "models.json"), "content": "{}"},
            risk_level="moderate",
        )
        assert result.allowed

    def test_write_to_host_path_always_allowed(self, tmp_path: Path) -> None:
        """The guard must NOT trigger on host-project files."""
        host, _ = self._make_host_layout(tmp_path)
        config = SafetyConfig(allowed_paths=[host])
        result = config.check_tool_execution(
            "write_file",
            {"path": str(host / "src" / "main.py"), "content": "# new"},
            risk_level="moderate",
        )
        assert result.allowed

    def test_read_from_scaffold_always_allowed(self, tmp_path: Path) -> None:
        """Read tools are not in WRITE_TOOL_NAMES — agents need them."""
        host, scaffold = self._make_host_layout(tmp_path)
        config = SafetyConfig(allowed_paths=[host])  # default scope
        result = config.check_tool_execution(
            "read_file",
            {"path": str(scaffold / "config" / "models.json")},
        )
        assert result.allowed


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
