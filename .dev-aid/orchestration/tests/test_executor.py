"""Tests for RouterExecutor"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from router.executor import RouterExecutor


class TestRouterExecutor:
    """Test RouterExecutor"""

    @pytest.fixture
    def mock_config(self, tmp_path):
        """Mock configuration"""
        config = Mock()
        config.root = tmp_path
        config.get_orchestration_mode = Mock(return_value="solo")
        config.get_cost_limit = Mock(return_value=10.0)
        config.get_api_key = Mock(return_value="test-key")
        config.get_model_config = Mock(
            return_value={
                "model_id": "claude-sonnet-4",
                "provider": "anthropic",
                "max_tokens": 4096,
                "cost_per_1m_tokens": {"input": 3.0, "output": 15.0},
            }
        )
        return config

    @pytest.fixture
    def executor_no_mcp(self, mock_config, tmp_path):
        """Create executor without MCP"""
        with patch("router.executor.load_config", return_value=mock_config):
            executor = RouterExecutor(dev_aid_root=tmp_path, use_mcp=False)
            return executor

    def test_init_without_mcp(self, mock_config, tmp_path):
        """Test initialization without MCP"""
        with patch("router.executor.load_config", return_value=mock_config):
            executor = RouterExecutor(dev_aid_root=tmp_path, use_mcp=False)

            assert executor.config == mock_config
            assert executor.mcp_enabled is False
            assert executor.mcp_pool is None
            assert executor.mcp_registry is None
            assert "solo" in executor.modes
            assert "ensemble" in executor.modes
            assert "challenger" in executor.modes

    def test_init_with_mcp_failure(self, mock_config, tmp_path):
        """Test initialization when MCP setup fails"""
        with patch("router.executor.load_config", return_value=mock_config):
            with patch("router.executor.MCPRegistry") as mock_registry:
                mock_registry.side_effect = RuntimeError("MCP not available")

                executor = RouterExecutor(dev_aid_root=tmp_path, use_mcp=True)

                # Should gracefully handle MCP failure
                assert executor.mcp_enabled is False

    def test_execute_solo_mode(self, executor_no_mcp):
        """Test executing in solo mode"""
        # Mock the solo mode execute
        executor_no_mcp.modes["solo"].execute = Mock(
            return_value={
                "success": True,
                "mode": "solo",
                "provider": "anthropic",
                "model": "claude-sonnet-4",
                "response": "Test response",
                "cost": 0.05,
                "tokens_used": {"input": 100, "output": 50},
            }
        )

        result = executor_no_mcp.execute("Test request", mode="solo")

        assert result["success"] is True
        assert result["mode"] == "solo"
        assert result["response"] == "Test response"
        executor_no_mcp.modes["solo"].execute.assert_called_once()

    def test_execute_ensemble_mode(self, executor_no_mcp):
        """Test executing in ensemble mode"""
        executor_no_mcp.modes["ensemble"].execute = Mock(
            return_value={
                "success": True,
                "mode": "ensemble",
                "providers": ["anthropic", "google"],
                "response": "Ensemble response",
                "cost": 0.10,
            }
        )

        result = executor_no_mcp.execute("Test request", mode="ensemble")

        assert result["success"] is True
        assert result["mode"] == "ensemble"

    def test_execute_with_default_mode(self, executor_no_mcp):
        """Test executing with default mode from config"""
        executor_no_mcp.config.get_orchestration_mode = Mock(return_value="solo")
        executor_no_mcp.modes["solo"].execute = Mock(return_value={"success": True, "mode": "solo"})

        result = executor_no_mcp.execute("Test request")

        executor_no_mcp.config.get_orchestration_mode.assert_called_once()
        assert result["mode"] == "solo"

    def test_execute_with_invalid_mode(self, executor_no_mcp):
        """Test executing with invalid mode raises error"""
        with pytest.raises(ValueError, match="Unknown mode"):
            executor_no_mcp.execute("Test request", mode="invalid_mode")

    def test_execute_budget_exceeded(self, executor_no_mcp):
        """Test execution blocked when budget exceeded"""
        executor_no_mcp.cost_tracker.is_over_budget = Mock(return_value=True)
        executor_no_mcp.cost_tracker.get_budget_status = Mock(
            return_value={"spent": 12.0, "limit": 10.0}
        )

        result = executor_no_mcp.execute("Test request")

        assert result["success"] is False
        assert "budget limit exceeded" in result["error"].lower()
        assert "budget_status" in result

    def test_execute_mode_error_handling(self, executor_no_mcp):
        """Test error handling when mode execution fails"""
        executor_no_mcp.modes["solo"].execute = Mock(side_effect=RuntimeError("API error"))

        result = executor_no_mcp.execute("Test request", mode="solo")

        assert result["success"] is False
        assert "error" in result
        assert "failed" in result["error"].lower()

    def test_execute_challenger_mode(self, executor_no_mcp):
        """Test executing in challenger mode"""
        executor_no_mcp.modes["challenger"].execute = Mock(
            return_value={
                "success": True,
                "mode": "challenger",
                "challenged": False,
                "primary_model": "claude-sonnet-4",
                "response": "Response",
                "cost": 0.05,
            }
        )

        result = executor_no_mcp.execute("Test request", mode="challenger")

        assert result["success"] is True
        assert result["mode"] == "challenger"

    def test_log_decision(self, executor_no_mcp):
        """Test logging successful decisions"""
        executor_no_mcp.modes["solo"].execute = Mock(
            return_value={
                "success": True,
                "mode": "solo",
                "provider": "anthropic",
                "model": "claude-sonnet-4",
                "cost": 0.05,
                "tokens_used": {"input": 100, "output": 50},
            }
        )

        with patch.object(executor_no_mcp.cost_tracker, "log_decision") as mock_log:
            executor_no_mcp.execute("Test request", mode="solo")
            mock_log.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_async_basic(self, executor_no_mcp):
        """Test async execution"""
        executor_no_mcp.modes["solo"].execute = Mock(return_value={"success": True, "mode": "solo"})

        result = await executor_no_mcp._execute_async("Test request", "solo")

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_execute_async_with_mcp_context(self, mock_config, tmp_path):
        """Test async execution with MCP context gathering"""
        with patch("router.executor.load_config", return_value=mock_config):
            with patch("router.executor.MCPRegistry"):
                with patch("router.executor.MCPClientPool"):
                    executor = RouterExecutor(dev_aid_root=tmp_path, use_mcp=True)
                    executor.mcp_enabled = True

                    # Mock MCP initialization and context gathering
                    executor._initialize_mcp_servers = AsyncMock()
                    executor.context_builder.gather_mcp_context = AsyncMock(
                        return_value={"code_search": {"results": ["test.py"]}}
                    )
                    executor.modes["solo"].execute = Mock(return_value={"success": True})

                    result = await executor._execute_async("Test request", "solo")

                    assert result["success"] is True
                    executor.context_builder.gather_mcp_context.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_async_mcp_failure(self, mock_config, tmp_path):
        """Test async execution continues when MCP gathering fails"""
        with patch("router.executor.load_config", return_value=mock_config):
            with patch("router.executor.MCPRegistry"):
                with patch("router.executor.MCPClientPool"):
                    executor = RouterExecutor(dev_aid_root=tmp_path, use_mcp=True)
                    executor.mcp_enabled = True

                    # Mock MCP context gathering to fail
                    executor._initialize_mcp_servers = AsyncMock()
                    executor.context_builder.gather_mcp_context = AsyncMock(
                        side_effect=RuntimeError("MCP error")
                    )
                    executor.modes["solo"].execute = Mock(return_value={"success": True})

                    result = await executor._execute_async("Test request", "solo")

                    # Should still succeed despite MCP failure
                    assert result["success"] is True

    @pytest.mark.asyncio
    async def test_initialize_mcp_servers(self, mock_config, tmp_path):
        """Test MCP server initialization"""
        with patch("router.executor.load_config", return_value=mock_config):
            with patch("router.executor.MCPRegistry") as mock_registry_class:
                with patch("router.executor.MCPClientPool") as mock_pool_class:
                    mock_registry = Mock()
                    mock_pool = Mock()
                    mock_pool.clients = {}

                    mock_registry_class.return_value = mock_registry
                    mock_pool_class.return_value = mock_pool

                    # Mock server info
                    server_info = Mock()
                    server_info.name = "test-server"
                    server_info.command = ["test", "command"]
                    server_info.args = []
                    server_info.env = {}

                    mock_registry.get_enabled_servers = Mock(
                        return_value={"test-server": server_info}
                    )
                    mock_pool.add_server = AsyncMock(return_value=True)

                    executor = RouterExecutor(dev_aid_root=tmp_path, use_mcp=True)
                    executor.mcp_registry = mock_registry
                    executor.mcp_pool = mock_pool

                    await executor._initialize_mcp_servers()

                    # Should have tried to add the server
                    assert mock_pool.add_server.called
