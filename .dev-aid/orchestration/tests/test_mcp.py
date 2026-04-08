"""Tests for MCP client and registry"""

import asyncio
import json
import os
import subprocess
from unittest.mock import AsyncMock, Mock, patch

import pytest

from router.mcp_client import MCPClient, MCPClientPool, MCPServerConfig, MCPTool
from router.mcp_registry import MCPRegistry, MCPServerInfo


class TestMCPTool:
    """Test MCPTool dataclass"""

    def test_create_tool(self):
        """Test creating an MCP tool"""
        tool = MCPTool(
            name="search",
            description="Search code",
            input_schema={"type": "object"},
            server="code-search",
        )
        assert tool.name == "search"
        assert tool.description == "Search code"
        assert tool.server == "code-search"


class TestMCPServerConfig:
    """Test MCPServerConfig dataclass"""

    def test_create_config(self):
        """Test creating server config"""
        config = MCPServerConfig(name="test-server", command="npx", args=["-y", "test-mcp-server"])
        assert config.name == "test-server"
        assert config.command == "npx"
        assert config.args == ["-y", "test-mcp-server"]
        assert config.env is None

    def test_create_config_with_env(self):
        """Test creating server config with environment variables"""
        config = MCPServerConfig(
            name="test-server",
            command="test",
            args=[],
            env={"API_KEY": "test-key"},
        )
        assert config.env == {"API_KEY": "test-key"}


class TestMCPClient:
    """Test MCPClient"""

    @pytest.fixture
    def server_config(self):
        """Mock server configuration"""
        return MCPServerConfig(name="test-server", command="test", args=[])

    @pytest.fixture
    def mcp_client(self, server_config):
        """Create MCP client instance"""
        return MCPClient(server_config)

    def test_init(self, mcp_client, server_config):
        """Test client initialization"""
        assert mcp_client.config == server_config
        assert mcp_client.process is None
        assert mcp_client.message_id == 0
        assert mcp_client.available_tools == {}

    @pytest.mark.asyncio
    async def test_connect_success(self, mcp_client):
        """Test successful connection"""
        mock_process = AsyncMock()
        mock_process.stdin = AsyncMock()
        mock_process.stdout = AsyncMock()
        mock_process.stdin.write = Mock()
        mock_process.stdin.drain = AsyncMock()

        # Mock responses
        init_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {"capabilities": {}},
        }
        tools_response = {
            "jsonrpc": "2.0",
            "id": 2,
            "result": {
                "tools": [
                    {
                        "name": "search",
                        "description": "Search code",
                        "inputSchema": {"type": "object"},
                    }
                ]
            },
        }

        # Setup readline to return responses
        mock_process.stdout.readline = AsyncMock(
            side_effect=[
                (json.dumps(init_response) + "\n").encode(),
                (json.dumps(tools_response) + "\n").encode(),
            ]
        )

        with patch("asyncio.create_subprocess_exec", return_value=mock_process) as mock_exec:
            result = await mcp_client.connect()

            assert result is True
            assert mcp_client.process is not None
            assert "search" in mcp_client.available_tools
            assert mcp_client.available_tools["search"].name == "search"
            mock_exec.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_init_no_result(self, mcp_client):
        """Test connect returns False when init response has no 'result' key"""
        mock_process = AsyncMock()
        mock_process.stdin = AsyncMock()
        mock_process.stdout = AsyncMock()
        mock_process.stdin.write = Mock()
        mock_process.stdin.drain = AsyncMock()

        # Init response without "result" key - e.g., an error response
        init_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {"code": -32600, "message": "Protocol error"},
        }

        mock_process.stdout.readline = AsyncMock(
            return_value=(json.dumps(init_response) + "\n").encode()
        )

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await mcp_client.connect()
            assert result is False

    @pytest.mark.asyncio
    async def test_connect_tools_no_result(self, mcp_client):
        """Test connect with no tools in tools/list response"""
        mock_process = AsyncMock()
        mock_process.stdin = AsyncMock()
        mock_process.stdout = AsyncMock()
        mock_process.stdin.write = Mock()
        mock_process.stdin.drain = AsyncMock()

        init_response = {"jsonrpc": "2.0", "id": 1, "result": {"capabilities": {}}}
        # tools/list returns error, no result key
        tools_response = {
            "jsonrpc": "2.0",
            "id": 2,
            "error": {"code": -32601, "message": "Method not found"},
        }

        mock_process.stdout.readline = AsyncMock(
            side_effect=[
                (json.dumps(init_response) + "\n").encode(),
                (json.dumps(tools_response) + "\n").encode(),
            ]
        )

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await mcp_client.connect()
            # Still returns True because connection was initialized; just no tools
            assert result is True
            assert len(mcp_client.available_tools) == 0

    @pytest.mark.asyncio
    async def test_connect_tools_minimal_fields(self, mcp_client):
        """Test connect with tools that have minimal fields (no description/inputSchema)"""
        mock_process = AsyncMock()
        mock_process.stdin = AsyncMock()
        mock_process.stdout = AsyncMock()
        mock_process.stdin.write = Mock()
        mock_process.stdin.drain = AsyncMock()

        init_response = {"jsonrpc": "2.0", "id": 1, "result": {"capabilities": {}}}
        tools_response = {
            "jsonrpc": "2.0",
            "id": 2,
            "result": {"tools": [{"name": "bare-tool"}]},  # no description, no inputSchema
        }

        mock_process.stdout.readline = AsyncMock(
            side_effect=[
                (json.dumps(init_response) + "\n").encode(),
                (json.dumps(tools_response) + "\n").encode(),
            ]
        )

        with patch("asyncio.create_subprocess_exec", return_value=mock_process):
            result = await mcp_client.connect()
            assert result is True
            assert "bare-tool" in mcp_client.available_tools
            assert mcp_client.available_tools["bare-tool"].description == ""
            assert mcp_client.available_tools["bare-tool"].input_schema == {}

    @pytest.mark.asyncio
    async def test_connect_failure(self, mcp_client):
        """Test connection failure"""
        with patch("asyncio.create_subprocess_exec", side_effect=Exception("Failed to start")):
            result = await mcp_client.connect()
            assert result is False
            assert mcp_client.process is None

    @pytest.mark.asyncio
    async def test_environment_isolation(self, mcp_client):
        """Test that API keys and secrets are not leaked to MCP subprocesses"""
        # Set up environment with secrets
        test_env = {
            "PATH": "/usr/bin",
            "HOME": "/home/user",
            "USER": "testuser",
            "LANG": "en_US.UTF-8",
            "ANTHROPIC_API_KEY": "sk-ant-secret-key-should-not-leak",
            "OPENAI_API_KEY": "sk-openai-secret-key-should-not-leak",
            "GOOGLE_API_KEY": "google-secret-key-should-not-leak",
            "AWS_SECRET_ACCESS_KEY": "aws-secret-should-not-leak",
        }

        mock_process = AsyncMock()
        mock_process.stdin = AsyncMock()
        mock_process.stdout = AsyncMock()
        mock_process.stdin.write = Mock()
        mock_process.stdin.drain = AsyncMock()

        # Mock responses
        init_response = {"jsonrpc": "2.0", "id": 1, "result": {"capabilities": {}}}
        tools_response = {"jsonrpc": "2.0", "id": 2, "result": {"tools": []}}

        mock_process.stdout.readline = AsyncMock(
            side_effect=[
                (json.dumps(init_response) + "\n").encode(),
                (json.dumps(tools_response) + "\n").encode(),
            ]
        )

        with patch("asyncio.create_subprocess_exec", return_value=mock_process) as mock_exec:
            with patch.dict(os.environ, test_env, clear=True):
                result = await mcp_client.connect()

                assert result is True

                # Verify create_subprocess_exec was called
                mock_exec.assert_called_once()

                # Extract the env parameter from the call
                call_kwargs = mock_exec.call_args[1]
                passed_env = call_kwargs["env"]

                # Assert whitelisted vars are present
                assert "PATH" in passed_env
                assert "HOME" in passed_env
                assert "USER" in passed_env
                assert "LANG" in passed_env

                # Assert API keys and secrets are NOT present (SECURITY CHECK)
                assert (
                    "ANTHROPIC_API_KEY" not in passed_env
                ), "SECURITY VIOLATION: Anthropic API key leaked to subprocess"
                assert (
                    "OPENAI_API_KEY" not in passed_env
                ), "SECURITY VIOLATION: OpenAI API key leaked to subprocess"
                assert (
                    "GOOGLE_API_KEY" not in passed_env
                ), "SECURITY VIOLATION: Google API key leaked to subprocess"
                assert (
                    "AWS_SECRET_ACCESS_KEY" not in passed_env
                ), "SECURITY VIOLATION: AWS secret leaked to subprocess"

    @pytest.mark.asyncio
    async def test_server_specific_env_passed(self):
        """Test that server-specific env vars are passed correctly"""
        config = MCPServerConfig(
            name="test-server",
            command="test",
            args=[],
            env={"SERVER_API_KEY": "server-specific-key"},
        )
        client = MCPClient(config)

        mock_process = AsyncMock()
        mock_process.stdin = AsyncMock()
        mock_process.stdout = AsyncMock()
        mock_process.stdin.write = Mock()
        mock_process.stdin.drain = AsyncMock()

        init_response = {"jsonrpc": "2.0", "id": 1, "result": {"capabilities": {}}}
        tools_response = {"jsonrpc": "2.0", "id": 2, "result": {"tools": []}}

        mock_process.stdout.readline = AsyncMock(
            side_effect=[
                (json.dumps(init_response) + "\n").encode(),
                (json.dumps(tools_response) + "\n").encode(),
            ]
        )

        with patch("asyncio.create_subprocess_exec", return_value=mock_process) as mock_exec:
            result = await client.connect()

            assert result is True

            # Extract env parameter
            call_kwargs = mock_exec.call_args[1]
            passed_env = call_kwargs["env"]

            # Server-specific env should be present
            assert "SERVER_API_KEY" in passed_env
            assert passed_env["SERVER_API_KEY"] == "server-specific-key"

    @pytest.mark.asyncio
    async def test_disconnect(self, mcp_client):
        """Test disconnecting from server"""
        mock_process = AsyncMock()
        mock_process.terminate = Mock()
        mock_process.wait = AsyncMock()

        mcp_client.process = mock_process

        await mcp_client.disconnect()

        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called_once()
        assert mcp_client.process is None

    @pytest.mark.asyncio
    async def test_disconnect_when_not_connected(self, mcp_client):
        """Test disconnecting when process is None (no-op)"""
        assert mcp_client.process is None
        # Should not raise any errors
        await mcp_client.disconnect()
        assert mcp_client.process is None

    @pytest.mark.asyncio
    async def test_call_tool_success(self, mcp_client):
        """Test calling a tool successfully"""
        # Setup available tool
        mcp_client.available_tools["test_tool"] = MCPTool(
            name="test_tool",
            description="Test",
            input_schema={},
            server="test-server",
        )

        # Mock process and response
        mock_process = AsyncMock()
        mock_process.stdin = AsyncMock()
        mock_process.stdout = AsyncMock()
        mock_process.stdin.write = Mock()
        mock_process.stdin.drain = AsyncMock()

        response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {"status": "success", "data": "test"},
        }

        mock_process.stdout.readline = AsyncMock(
            return_value=(json.dumps(response) + "\n").encode()
        )

        mcp_client.process = mock_process

        result = await mcp_client.call_tool("test_tool", {"arg": "value"})

        assert result == {"status": "success", "data": "test"}

    @pytest.mark.asyncio
    async def test_call_tool_with_custom_timeout(self, mcp_client):
        """Test calling a tool with a custom timeout value"""
        mcp_client.available_tools["test_tool"] = MCPTool(
            name="test_tool",
            description="Test",
            input_schema={},
            server="test-server",
        )

        mock_process = AsyncMock()
        mock_process.stdin = AsyncMock()
        mock_process.stdout = AsyncMock()
        mock_process.stdin.write = Mock()
        mock_process.stdin.drain = AsyncMock()

        response = {"jsonrpc": "2.0", "id": 1, "result": {"data": "ok"}}
        mock_process.stdout.readline = AsyncMock(
            return_value=(json.dumps(response) + "\n").encode()
        )

        mcp_client.process = mock_process

        result = await mcp_client.call_tool("test_tool", {"arg": "val"}, timeout=60.0)
        assert result == {"data": "ok"}

    @pytest.mark.asyncio
    async def test_call_tool_empty_result(self, mcp_client):
        """Test call_tool returns empty dict when response has no 'result' key"""
        mcp_client.available_tools["test_tool"] = MCPTool(
            name="test_tool",
            description="Test",
            input_schema={},
            server="test-server",
        )

        mock_process = AsyncMock()
        mock_process.stdin = AsyncMock()
        mock_process.stdout = AsyncMock()
        mock_process.stdin.write = Mock()
        mock_process.stdin.drain = AsyncMock()

        # Response with neither "result" nor "error"
        response = {"jsonrpc": "2.0", "id": 1}
        mock_process.stdout.readline = AsyncMock(
            return_value=(json.dumps(response) + "\n").encode()
        )

        mcp_client.process = mock_process

        result = await mcp_client.call_tool("test_tool", {})
        assert result == {}

    @pytest.mark.asyncio
    async def test_call_tool_not_available(self, mcp_client):
        """Test calling a tool that doesn't exist"""
        with pytest.raises(ValueError, match="Tool .* not available"):
            await mcp_client.call_tool("nonexistent_tool", {})

    @pytest.mark.asyncio
    async def test_call_tool_error_response(self, mcp_client):
        """Test tool call with error response"""
        mcp_client.available_tools["test_tool"] = MCPTool(
            name="test_tool", description="Test", input_schema={}, server="test-server"
        )

        mock_process = AsyncMock()
        mock_process.stdin = AsyncMock()
        mock_process.stdout = AsyncMock()
        mock_process.stdin.write = Mock()
        mock_process.stdin.drain = AsyncMock()

        error_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {"code": -32600, "message": "Invalid request"},
        }

        mock_process.stdout.readline = AsyncMock(
            return_value=(json.dumps(error_response) + "\n").encode()
        )

        mcp_client.process = mock_process

        with pytest.raises(RuntimeError, match="MCP tool error"):
            await mcp_client.call_tool("test_tool", {})

    @pytest.mark.asyncio
    async def test_send_request_not_connected(self, mcp_client):
        """Test sending request when not connected"""
        with pytest.raises(RuntimeError, match="Not connected"):
            await mcp_client._send_request({"test": "request"})

    @pytest.mark.asyncio
    async def test_send_request_stdin_none(self, mcp_client):
        """Test sending request when stdin is None"""
        mock_process = AsyncMock()
        mock_process.stdin = None
        mock_process.stdout = AsyncMock()
        mcp_client.process = mock_process

        with pytest.raises(RuntimeError, match="Not connected"):
            await mcp_client._send_request({"test": "request"})

    @pytest.mark.asyncio
    async def test_send_request_stdout_none(self, mcp_client):
        """Test sending request when stdout is None"""
        mock_process = AsyncMock()
        mock_process.stdin = AsyncMock()
        mock_process.stdout = None
        mcp_client.process = mock_process

        with pytest.raises(RuntimeError, match="Not connected"):
            await mcp_client._send_request({"test": "request"})

    @pytest.mark.asyncio
    async def test_send_request_timeout(self, mcp_client):
        """Test that _send_request raises TimeoutError on slow responses"""
        mock_process = AsyncMock()
        mock_process.stdin = AsyncMock()
        mock_process.stdout = AsyncMock()
        mock_process.stdin.write = Mock()
        mock_process.stdin.drain = AsyncMock()

        # Make readline raise TimeoutError (simulating asyncio.wait_for timeout)
        mock_process.stdout.readline = AsyncMock(side_effect=asyncio.TimeoutError())

        mcp_client.process = mock_process

        with pytest.raises(asyncio.TimeoutError):
            await mcp_client._send_request({"test": "request"}, timeout=0.1)

    @pytest.mark.asyncio
    async def test_send_request_valid_json_rpc(self, mcp_client):
        """Test that _send_request sends valid JSON-RPC and reads response"""
        mock_process = AsyncMock()
        mock_process.stdin = AsyncMock()
        mock_process.stdout = AsyncMock()
        mock_process.stdin.write = Mock()
        mock_process.stdin.drain = AsyncMock()

        response = {"jsonrpc": "2.0", "id": 1, "result": {"ok": True}}
        mock_process.stdout.readline = AsyncMock(
            return_value=(json.dumps(response) + "\n").encode()
        )

        mcp_client.process = mock_process

        request = {"jsonrpc": "2.0", "id": 1, "method": "test"}
        result = await mcp_client._send_request(request)

        assert result == response
        # Verify the request was written as JSON + newline
        written_data = mock_process.stdin.write.call_args[0][0]
        assert written_data == (json.dumps(request) + "\n").encode()

    def test_next_id(self, mcp_client):
        """Test message ID generation"""
        assert mcp_client._next_id() == 1
        assert mcp_client._next_id() == 2
        assert mcp_client._next_id() == 3

    def test_get_tools(self, mcp_client):
        """Test getting available tools"""
        tool1 = MCPTool("tool1", "Test 1", {}, "server")
        tool2 = MCPTool("tool2", "Test 2", {}, "server")

        mcp_client.available_tools = {"tool1": tool1, "tool2": tool2}

        tools = mcp_client.get_tools()
        assert len(tools) == 2
        assert tool1 in tools
        assert tool2 in tools

    def test_get_tools_empty(self, mcp_client):
        """Test getting tools when none available"""
        tools = mcp_client.get_tools()
        assert tools == []


class TestMCPClientPool:
    """Test MCPClientPool"""

    @pytest.fixture
    def pool(self):
        """Create MCP client pool"""
        return MCPClientPool()

    @pytest.mark.asyncio
    async def test_init(self, pool):
        """Test pool initialization"""
        assert pool.clients == {}

    @pytest.mark.asyncio
    async def test_add_server_success(self, pool):
        """Test adding server successfully"""
        config = MCPServerConfig(name="test-server", command="test", args=[])

        with patch.object(MCPClient, "connect", return_value=True):
            result = await pool.add_server(config)

            assert result is True
            assert "test-server" in pool.clients

    @pytest.mark.asyncio
    async def test_add_server_failure(self, pool):
        """Test adding server that fails to connect"""
        config = MCPServerConfig(name="test-server", command="test", args=[])

        with patch.object(MCPClient, "connect", return_value=False):
            result = await pool.add_server(config)

            assert result is False
            assert "test-server" not in pool.clients

    @pytest.mark.asyncio
    async def test_add_server_already_exists(self, pool):
        """Test adding server that already exists"""
        config = MCPServerConfig(name="test-server", command="test", args=[])

        # Add first time
        with patch.object(MCPClient, "connect", return_value=True):
            await pool.add_server(config)

        # Add second time - should return True without connecting again
        result = await pool.add_server(config)
        assert result is True

    @pytest.mark.asyncio
    async def test_remove_server(self, pool):
        """Test removing server from pool"""
        config = MCPServerConfig(name="test-server", command="test", args=[])

        with patch.object(MCPClient, "connect", return_value=True):
            await pool.add_server(config)

        with patch.object(MCPClient, "disconnect") as mock_disconnect:
            await pool.remove_server("test-server")

            mock_disconnect.assert_called_once()
            assert "test-server" not in pool.clients

    @pytest.mark.asyncio
    async def test_remove_nonexistent_server(self, pool):
        """Test removing server that doesn't exist"""
        # Should not raise error
        await pool.remove_server("nonexistent")

    @pytest.mark.asyncio
    async def test_call_tool(self, pool):
        """Test calling tool on specific server"""
        config = MCPServerConfig(name="test-server", command="test", args=[])

        with patch.object(MCPClient, "connect", return_value=True):
            await pool.add_server(config)

        mock_result = {"status": "success"}
        with patch.object(MCPClient, "call_tool", return_value=mock_result) as mock_call:
            result = await pool.call_tool("test-server", "test_tool", {"arg": "val"})

            assert result == mock_result
            mock_call.assert_called_once_with("test_tool", {"arg": "val"}, timeout=30.0)

    @pytest.mark.asyncio
    async def test_call_tool_custom_timeout(self, pool):
        """Test calling tool on specific server with custom timeout"""
        config = MCPServerConfig(name="test-server", command="test", args=[])

        with patch.object(MCPClient, "connect", return_value=True):
            await pool.add_server(config)

        mock_result = {"status": "ok"}
        with patch.object(MCPClient, "call_tool", return_value=mock_result) as mock_call:
            result = await pool.call_tool("test-server", "test_tool", {"arg": "val"}, timeout=120.0)

            assert result == mock_result
            mock_call.assert_called_once_with("test_tool", {"arg": "val"}, timeout=120.0)

    @pytest.mark.asyncio
    async def test_call_tool_server_not_found(self, pool):
        """Test calling tool on server that doesn't exist"""
        with pytest.raises(ValueError, match="Server .* not in pool"):
            await pool.call_tool("nonexistent", "tool", {})

    def test_get_all_tools(self, pool):
        """Test getting all tools from all servers"""
        # Create mock clients with tools
        mock_client1 = Mock()
        mock_client1.get_tools = Mock(return_value=[MCPTool("tool1", "Test", {}, "server1")])

        mock_client2 = Mock()
        mock_client2.get_tools = Mock(return_value=[MCPTool("tool2", "Test", {}, "server2")])

        pool.clients = {"server1": mock_client1, "server2": mock_client2}

        all_tools = pool.get_all_tools()

        assert "server1" in all_tools
        assert "server2" in all_tools
        assert len(all_tools["server1"]) == 1
        assert len(all_tools["server2"]) == 1

    def test_get_all_tools_empty(self, pool):
        """Test getting all tools when pool has no clients"""
        all_tools = pool.get_all_tools()
        assert all_tools == {}

    @pytest.mark.asyncio
    async def test_disconnect_all(self, pool):
        """Test disconnecting from all servers"""
        config1 = MCPServerConfig(name="server1", command="test", args=[])
        config2 = MCPServerConfig(name="server2", command="test", args=[])

        with patch.object(MCPClient, "connect", return_value=True):
            await pool.add_server(config1)
            await pool.add_server(config2)

        assert len(pool.clients) == 2

        with patch.object(MCPClient, "disconnect") as mock_disconnect:
            await pool.disconnect_all()

            assert mock_disconnect.call_count == 2
            assert len(pool.clients) == 0

    @pytest.mark.asyncio
    async def test_disconnect_all_empty(self, pool):
        """Test disconnecting when pool is empty"""
        await pool.disconnect_all()
        assert len(pool.clients) == 0


class TestMCPServerInfo:
    """Test MCPServerInfo dataclass"""

    def test_create_server_info(self):
        """Test creating server info"""
        info = MCPServerInfo(
            name="test",
            command="npx",
            args=["-y", "test"],
            source="claude",
        )
        assert info.name == "test"
        assert info.command == "npx"
        assert info.capabilities == []
        assert info.enabled_for_router is False

    def test_create_with_capabilities(self):
        """Test creating server info with capabilities"""
        info = MCPServerInfo(
            name="test",
            command="test",
            args=[],
            capabilities=["database", "search"],
        )
        assert info.capabilities == ["database", "search"]

    def test_post_init_none_capabilities(self):
        """Test __post_init__ initializes None capabilities to empty list"""
        info = MCPServerInfo(
            name="test",
            command="test",
            args=[],
            capabilities=None,
        )
        assert info.capabilities == []

    def test_default_source(self):
        """Test default source is 'unknown'"""
        info = MCPServerInfo(name="test", command="test", args=[])
        assert info.source == "unknown"

    def test_create_with_env(self):
        """Test creating server info with environment variables"""
        info = MCPServerInfo(
            name="test",
            command="test",
            args=[],
            env={"KEY": "value"},
        )
        assert info.env == {"KEY": "value"}


class TestMCPRegistry:
    """Test MCPRegistry"""

    @pytest.fixture
    def tmp_config_path(self, tmp_path):
        """Temporary config path"""
        return str(tmp_path / "mcp-config.json")

    @pytest.fixture
    def registry(self, tmp_config_path):
        """Create registry instance"""
        return MCPRegistry(config_path=tmp_config_path)

    def test_init(self, registry):
        """Test registry initialization"""
        assert registry.servers == {}

    def test_init_default_path(self):
        """Test registry with default config path"""
        with patch.object(MCPRegistry, "_load_config"):
            registry = MCPRegistry()
            assert registry.config_path.endswith("mcp-config.json")

    def test_init_null_byte_in_path(self):
        """Test registry raises ValueError for null bytes in config path"""
        with pytest.raises(ValueError, match="Config path contains null bytes"):
            MCPRegistry(config_path="/some/path\0/evil")

    def test_infer_capabilities_database(self, registry):
        """Test inferring database capabilities"""
        caps = registry._infer_capabilities("postgres-server")
        assert "database" in caps

        caps = registry._infer_capabilities("mysql-db")
        assert "database" in caps

    def test_infer_capabilities_github(self, registry):
        """Test inferring GitHub capabilities"""
        caps = registry._infer_capabilities("github-mcp")
        assert "github" in caps

    def test_infer_capabilities_search(self, registry):
        """Test inferring search capabilities"""
        caps = registry._infer_capabilities("code-search")
        assert "search" in caps

    def test_infer_capabilities_multiple(self, registry):
        """Test inferring multiple capabilities"""
        caps = registry._infer_capabilities("github-code-search")
        assert "github" in caps
        assert "search" in caps

    def test_infer_capabilities_filesystem(self, registry):
        """Test inferring filesystem capabilities"""
        caps = registry._infer_capabilities("filesystem-server")
        assert "filesystem" in caps

        caps = registry._infer_capabilities("my-file-manager")
        assert "filesystem" in caps

        caps = registry._infer_capabilities("fs-tools")
        assert "filesystem" in caps

    def test_infer_capabilities_communication(self, registry):
        """Test inferring communication capabilities"""
        caps = registry._infer_capabilities("slack-bot")
        assert "communication" in caps

        caps = registry._infer_capabilities("discord-mcp")
        assert "communication" in caps

        caps = registry._infer_capabilities("teams-connector")
        assert "communication" in caps

    def test_infer_capabilities_browser(self, registry):
        """Test inferring browser capabilities"""
        caps = registry._infer_capabilities("puppeteer-server")
        assert "browser" in caps

        caps = registry._infer_capabilities("playwright-mcp")
        assert "browser" in caps

        caps = registry._infer_capabilities("selenium-driver")
        assert "browser" in caps

    def test_infer_capabilities_project_management(self, registry):
        """Test inferring project management capabilities"""
        caps = registry._infer_capabilities("jira-mcp")
        assert "project-management" in caps

        caps = registry._infer_capabilities("linear-server")
        assert "project-management" in caps

        caps = registry._infer_capabilities("asana-connector")
        assert "project-management" in caps

    def test_infer_capabilities_cloud(self, registry):
        """Test inferring cloud capabilities"""
        caps = registry._infer_capabilities("aws-toolkit")
        assert "cloud" in caps

        caps = registry._infer_capabilities("gcp-server")
        assert "cloud" in caps

        caps = registry._infer_capabilities("azure-mcp")
        assert "cloud" in caps

        caps = registry._infer_capabilities("cloud-manager")
        assert "cloud" in caps

    def test_infer_capabilities_research(self, registry):
        """Test inferring research capabilities"""
        caps = registry._infer_capabilities("deep-research-server")
        assert "research" in caps

        caps = registry._infer_capabilities("tavily-search")
        assert "research" in caps
        # Also has "search"
        assert "search" in caps

        caps = registry._infer_capabilities("perplexity-mcp")
        assert "research" in caps

    def test_infer_capabilities_none_matched(self, registry):
        """Test inferring capabilities when no patterns match"""
        caps = registry._infer_capabilities("custom-server")
        assert caps == []

    def test_infer_capabilities_sqlite(self, registry):
        """Test sqlite name triggers database capability"""
        caps = registry._infer_capabilities("sqlite-mcp")
        assert "database" in caps

    def test_infer_capabilities_gitlab(self, registry):
        """Test gitlab name triggers github (vcs) capability"""
        caps = registry._infer_capabilities("gitlab-server")
        assert "github" in caps

    def test_infer_capabilities_brave(self, registry):
        """Test brave name triggers search capability"""
        caps = registry._infer_capabilities("brave-search")
        assert "search" in caps

    def test_infer_capabilities_exa(self, registry):
        """Test exa name triggers search capability"""
        caps = registry._infer_capabilities("exa-mcp")
        assert "search" in caps

    def test_enable_server(self, registry):
        """Test enabling a server"""
        server = MCPServerInfo(
            name="test-server", command="test", args=[], enabled_for_router=False
        )
        registry.servers["test-server"] = server

        result = registry.enable_server("test-server")

        assert result is True
        assert registry.servers["test-server"].enabled_for_router is True

    def test_enable_nonexistent_server(self, registry):
        """Test enabling server that doesn't exist"""
        result = registry.enable_server("nonexistent")
        assert result is False

    def test_disable_server(self, registry):
        """Test disabling a server"""
        server = MCPServerInfo(name="test-server", command="test", args=[], enabled_for_router=True)
        registry.servers["test-server"] = server

        result = registry.disable_server("test-server")

        assert result is True
        assert registry.servers["test-server"].enabled_for_router is False

    def test_disable_nonexistent_server(self, registry):
        """Test disabling server that doesn't exist"""
        result = registry.disable_server("nonexistent")
        assert result is False

    def test_get_enabled_servers(self, registry):
        """Test getting enabled servers"""
        server1 = MCPServerInfo(name="enabled", command="test", args=[], enabled_for_router=True)
        server2 = MCPServerInfo(name="disabled", command="test", args=[], enabled_for_router=False)

        registry.servers = {"enabled": server1, "disabled": server2}

        enabled = registry.get_enabled_servers()

        assert len(enabled) == 1
        assert "enabled" in enabled
        assert "disabled" not in enabled

    def test_get_enabled_servers_empty(self, registry):
        """Test getting enabled servers when none are enabled"""
        server1 = MCPServerInfo(name="disabled1", command="test", args=[], enabled_for_router=False)
        registry.servers = {"disabled1": server1}

        enabled = registry.get_enabled_servers()
        assert len(enabled) == 0

    def test_get_servers_by_capability(self, registry):
        """Test getting servers by capability"""
        server1 = MCPServerInfo(
            name="db-server",
            command="test",
            args=[],
            capabilities=["database"],
            enabled_for_router=True,
        )
        server2 = MCPServerInfo(
            name="search-server",
            command="test",
            args=[],
            capabilities=["search"],
            enabled_for_router=True,
        )
        server3 = MCPServerInfo(
            name="disabled-db",
            command="test",
            args=[],
            capabilities=["database"],
            enabled_for_router=False,
        )

        registry.servers = {
            "db-server": server1,
            "search-server": server2,
            "disabled-db": server3,
        }

        db_servers = registry.get_servers_by_capability("database")

        assert len(db_servers) == 1
        assert db_servers[0].name == "db-server"

    def test_get_servers_by_capability_none_match(self, registry):
        """Test getting servers by capability when none match"""
        server1 = MCPServerInfo(
            name="db-server",
            command="test",
            args=[],
            capabilities=["database"],
            enabled_for_router=True,
        )
        registry.servers = {"db-server": server1}

        result = registry.get_servers_by_capability("browser")
        assert result == []

    def test_get_servers_by_capability_none_capabilities(self, registry):
        """Test getting servers by capability when a server has None capabilities"""
        # Force capabilities to None after creation to test the guard clause
        server = MCPServerInfo(
            name="no-caps",
            command="test",
            args=[],
            enabled_for_router=True,
        )
        server.capabilities = None  # type: ignore[assignment]
        registry.servers = {"no-caps": server}

        result = registry.get_servers_by_capability("database")
        assert result == []

    def test_save_and_load_config(self, registry, tmp_config_path):
        """Test saving and loading configuration"""
        server = MCPServerInfo(
            name="test-server",
            command="test",
            args=[],
            enabled_for_router=True,
            capabilities=["database"],
            source="claude",
        )
        registry.servers["test-server"] = server

        # Save
        registry._save_config()

        # Verify file exists
        assert os.path.exists(tmp_config_path)

        # Load in new registry
        new_registry = MCPRegistry(config_path=tmp_config_path)
        new_registry.servers["test-server"] = MCPServerInfo(
            name="test-server", command="test", args=[]
        )
        new_registry._load_config()

        assert new_registry.servers["test-server"].enabled_for_router is True

    def test_save_config_creates_directory(self, tmp_path):
        """Test _save_config creates parent directory if it doesn't exist"""
        nested_path = str(tmp_path / "a" / "b" / "c" / "mcp-config.json")
        registry = MCPRegistry(config_path=nested_path)
        registry.servers["test"] = MCPServerInfo(
            name="test", command="cmd", args=[], source="claude"
        )
        registry._save_config()

        assert os.path.exists(nested_path)
        with open(nested_path, "r") as f:
            data = json.load(f)
        assert data["version"] == "1.0.0"
        assert "test" in data["servers"]

    def test_save_config_structure(self, registry, tmp_config_path):
        """Test _save_config writes correct JSON structure"""
        server = MCPServerInfo(
            name="my-server",
            command="test",
            args=[],
            enabled_for_router=True,
            capabilities=["search", "database"],
            source="gemini",
        )
        registry.servers["my-server"] = server
        registry._save_config()

        with open(tmp_config_path, "r") as f:
            data = json.load(f)

        assert data["version"] == "1.0.0"
        assert "my-server" in data["servers"]
        saved = data["servers"]["my-server"]
        assert saved["name"] == "my-server"
        assert saved["enabled"] is True
        assert saved["capabilities"] == ["search", "database"]
        assert saved["source"] == "gemini"

    def test_load_config_nonexistent_file(self, registry):
        """Test _load_config handles nonexistent config file gracefully"""
        registry.config_path = "/nonexistent/path/to/config.json"
        # Should not raise; config file doesn't exist so nothing to load
        registry._load_config()
        assert registry.servers == {}

    def test_load_config_invalid_json(self, tmp_path):
        """Test _load_config handles invalid JSON gracefully"""
        config_file = tmp_path / "bad-config.json"
        config_file.write_text("not valid json{{{")

        registry = MCPRegistry(config_path=str(config_file))
        # _load_config was called in __init__ but should not raise
        assert registry.servers == {}

    def test_load_config_permission_error(self, tmp_path):
        """Test _load_config handles permission errors gracefully"""
        config_file = tmp_path / "perm-config.json"
        config_file.write_text('{"servers": {}}')

        with patch("builtins.open", side_effect=PermissionError("Access denied")):
            registry = MCPRegistry.__new__(MCPRegistry)
            registry.config_path = str(config_file)
            registry.servers = {}
            # Should not raise
            registry._load_config()

    def test_load_config_applies_enabled_state(self, tmp_path):
        """Test _load_config applies enabled/disabled state from saved config"""
        config_file = tmp_path / "config.json"
        config_data = {
            "servers": {
                "server-a": {"enabled": True},
                "server-b": {"enabled": False},
                "server-c": {"enabled": True},  # Not in registry, should be ignored
            }
        }
        config_file.write_text(json.dumps(config_data))

        registry = MCPRegistry(config_path=str(config_file))
        registry.servers["server-a"] = MCPServerInfo(
            name="server-a", command="cmd", args=[], enabled_for_router=False
        )
        registry.servers["server-b"] = MCPServerInfo(
            name="server-b", command="cmd", args=[], enabled_for_router=True
        )
        registry._load_config()

        assert registry.servers["server-a"].enabled_for_router is True
        assert registry.servers["server-b"].enabled_for_router is False

    def test_discover_claude_config_not_found(self, registry):
        """Test Claude discovery when config file doesn't exist"""
        with patch.object(registry, "_read_claude_config", return_value=None):
            servers = registry._discover_claude()
            assert servers == {}

    def test_discover_claude_success(self, registry):
        """Test successful Claude discovery"""
        mock_config = {
            "mcpServers": {
                "test-server": {
                    "command": "npx",
                    "args": ["-y", "test"],
                    "env": {"KEY": "value"},
                }
            }
        }

        # Mock subprocess.run to raise FileNotFoundError (simulating claude CLI not found)
        # This ensures the fallback path that reads config directly is used
        with patch("subprocess.run", side_effect=FileNotFoundError("claude not found")):
            with patch.object(registry, "_read_claude_config", return_value=mock_config):
                servers = registry._discover_claude()

                assert "test-server" in servers
                assert servers["test-server"].command == "npx"
                assert servers["test-server"].source == "claude"

    def test_discover_claude_cli_success_path(self, registry):
        """Test Claude discovery via successful 'claude mcp list' CLI command"""
        mock_config = {
            "mcpServers": {
                "github-mcp": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-github"],
                    "env": {"GITHUB_TOKEN": "ghp_test"},
                },
                "filesystem": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem"],
                },
            }
        }

        # Simulate successful 'claude mcp list' output
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = (
            "Name         Type     Status\n"
            "github-mcp   stdio    running\n"
            "filesystem   stdio    running\n"
        )

        with patch("subprocess.run", return_value=mock_result):
            with patch.object(registry, "_read_claude_config", return_value=mock_config):
                servers = registry._discover_claude()

                assert "github-mcp" in servers
                assert servers["github-mcp"].source == "claude"
                assert servers["github-mcp"].command == "npx"
                assert servers["github-mcp"].env == {"GITHUB_TOKEN": "ghp_test"}
                assert "github" in servers["github-mcp"].capabilities

                assert "filesystem" in servers
                assert servers["filesystem"].source == "claude"
                assert "filesystem" in servers["filesystem"].capabilities

    def test_discover_claude_cli_success_server_not_in_config(self, registry):
        """Test Claude CLI lists a server not found in config file"""
        mock_config = {
            "mcpServers": {
                # Only github-mcp in config, but CLI lists filesystem too
                "github-mcp": {
                    "command": "npx",
                    "args": ["-y", "server-github"],
                }
            }
        }

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = (
            "Name         Type     Status\n"
            "github-mcp   stdio    running\n"
            "filesystem   stdio    running\n"
        )

        with patch("subprocess.run", return_value=mock_result):
            with patch.object(registry, "_read_claude_config", return_value=mock_config):
                servers = registry._discover_claude()

                # Only github-mcp is in config, so only that should be returned
                assert "github-mcp" in servers
                assert "filesystem" not in servers

    def test_discover_claude_cli_success_config_returns_none(self, registry):
        """Test Claude CLI succeeds but config file is not readable"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Name         Type     Status\ngithub-mcp   stdio    running\n"

        with patch("subprocess.run", return_value=mock_result):
            with patch.object(registry, "_read_claude_config", return_value=None):
                servers = registry._discover_claude()
                # Config is None, so no servers can be created from it
                assert servers == {}

    def test_discover_claude_cli_nonzero_returncode(self, registry):
        """Test Claude CLI returns non-zero exit code"""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""

        mock_config = {"mcpServers": {}}

        with patch("subprocess.run", return_value=mock_result):
            with patch.object(registry, "_read_claude_config", return_value=mock_config):
                servers = registry._discover_claude()
                assert servers == {}

    def test_discover_claude_cli_empty_lines(self, registry):
        """Test Claude CLI output with empty lines"""
        mock_config = {"mcpServers": {"my-server": {"command": "node", "args": ["server.js"]}}}

        mock_result = Mock()
        mock_result.returncode = 0
        # Header + blank lines + data
        mock_result.stdout = "Name         Type\n\nmy-server    stdio\n\n"

        with patch("subprocess.run", return_value=mock_result):
            with patch.object(registry, "_read_claude_config", return_value=mock_config):
                servers = registry._discover_claude()
                assert "my-server" in servers

    def test_discover_claude_timeout(self, registry):
        """Test Claude CLI times out"""
        mock_config = {"mcpServers": {"test-server": {"command": "test", "args": []}}}

        with patch(
            "subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd="claude", timeout=5),
        ):
            with patch.object(registry, "_read_claude_config", return_value=mock_config):
                servers = registry._discover_claude()
                # Falls back to reading config directly
                assert "test-server" in servers
                assert servers["test-server"].source == "claude"

    def test_discover_claude_subprocess_error(self, registry):
        """Test Claude CLI raises SubprocessError"""
        mock_config = {"mcpServers": {"fallback-server": {"command": "test", "args": []}}}

        with patch("subprocess.run", side_effect=subprocess.SubprocessError("Process error")):
            with patch.object(registry, "_read_claude_config", return_value=mock_config):
                servers = registry._discover_claude()
                assert "fallback-server" in servers

    def test_discover_claude_os_error(self, registry):
        """Test Claude CLI raises OSError"""
        mock_config = {"mcpServers": {"os-fallback": {"command": "test", "args": []}}}

        with patch("subprocess.run", side_effect=OSError("OS error")):
            with patch.object(registry, "_read_claude_config", return_value=mock_config):
                servers = registry._discover_claude()
                assert "os-fallback" in servers

    def test_discover_claude_fallback_config_none(self, registry):
        """Test Claude CLI error and config read returns None"""
        with patch("subprocess.run", side_effect=FileNotFoundError("claude not found")):
            with patch.object(registry, "_read_claude_config", return_value=None):
                servers = registry._discover_claude()
                assert servers == {}

    def test_discover_claude_fallback_config_empty_mcp_servers(self, registry):
        """Test Claude CLI error and config has empty mcpServers"""
        mock_config = {"mcpServers": {}}

        with patch("subprocess.run", side_effect=FileNotFoundError("claude not found")):
            with patch.object(registry, "_read_claude_config", return_value=mock_config):
                servers = registry._discover_claude()
                assert servers == {}

    def test_discover_claude_cli_line_less_than_two_parts(self, registry):
        """Test Claude CLI output with a line having fewer than 2 parts"""
        mock_config = {"mcpServers": {"good-server": {"command": "test", "args": []}}}

        mock_result = Mock()
        mock_result.returncode = 0
        # Header line, then a single-word line and a proper line
        mock_result.stdout = "Name         Type\nsingleword\ngood-server  stdio\n"

        with patch("subprocess.run", return_value=mock_result):
            with patch.object(registry, "_read_claude_config", return_value=mock_config):
                servers = registry._discover_claude()
                assert "good-server" in servers
                # "singleword" has only 1 part, so it's skipped
                assert "singleword" not in servers

    def test_read_claude_config_first_path(self, registry, tmp_path):
        """Test _read_claude_config reads from first available path"""
        config_data = {"mcpServers": {"test": {"command": "test", "args": []}}}
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config_data))

        with patch("os.path.expanduser", return_value=str(config_file)):
            result = registry._read_claude_config()
            assert result is not None
            assert "mcpServers" in result

    def test_read_claude_config_second_path(self, registry, tmp_path):
        """Test _read_claude_config reads from second path when first doesn't exist"""
        config_data = {"mcpServers": {"from-second": {"command": "cmd", "args": []}}}
        second_config = tmp_path / "config.json"
        second_config.write_text(json.dumps(config_data))

        call_count = 0

        def mock_expanduser(path):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return str(tmp_path / "nonexistent-config.json")
            return str(second_config)

        with patch("os.path.expanduser", side_effect=mock_expanduser):
            result = registry._read_claude_config()
            assert result is not None
            assert "from-second" in result.get("mcpServers", {})

    def test_read_claude_config_none_when_no_files(self, registry, tmp_path):
        """Test _read_claude_config returns None when no config files exist"""
        with patch(
            "os.path.expanduser",
            return_value=str(tmp_path / "nonexistent.json"),
        ):
            result = registry._read_claude_config()
            assert result is None

    def test_read_claude_config_json_decode_error(self, registry, tmp_path):
        """Test _read_claude_config handles JSON decode errors"""
        bad_file = tmp_path / "config.json"
        bad_file.write_text("not json")

        with patch("os.path.expanduser", return_value=str(bad_file)):
            result = registry._read_claude_config()
            # Both paths point to bad file, both fail, returns None
            assert result is None

    def test_read_claude_config_permission_error(self, registry, tmp_path):
        """Test _read_claude_config handles permission errors"""
        config_file = tmp_path / "config.json"
        config_file.write_text('{"mcpServers": {}}')

        def mock_expanduser(path):
            return str(config_file)

        with patch("os.path.expanduser", side_effect=mock_expanduser):
            with patch("builtins.open", side_effect=PermissionError("denied")):
                with patch("os.path.exists", return_value=True):
                    result = registry._read_claude_config()
                    assert result is None

    def test_discover_gemini_success(self, registry, tmp_path):
        """Test successful Gemini discovery"""
        gemini_config = {
            "mcpServers": {
                "gemini-server": {
                    "command": "node",
                    "args": ["server.js"],
                }
            }
        }

        gemini_config_path = tmp_path / ".gemini" / "mcp.json"
        gemini_config_path.parent.mkdir(parents=True)
        with open(gemini_config_path, "w") as f:
            json.dump(gemini_config, f)

        with patch(
            "os.path.expanduser",
            return_value=str(gemini_config_path.parent / "mcp.json"),
        ):
            servers = registry._discover_gemini()

            assert "gemini-server" in servers
            assert servers["gemini-server"].command == "node"
            assert servers["gemini-server"].source == "gemini"

    def test_discover_gemini_with_env(self, registry, tmp_path):
        """Test Gemini discovery with server environment variables"""
        gemini_config = {
            "mcpServers": {
                "search-server": {
                    "command": "npx",
                    "args": ["-y", "search-mcp"],
                    "env": {"API_KEY": "test-key"},
                }
            }
        }

        gemini_config_path = tmp_path / ".gemini" / "mcp.json"
        gemini_config_path.parent.mkdir(parents=True)
        with open(gemini_config_path, "w") as f:
            json.dump(gemini_config, f)

        with patch(
            "os.path.expanduser",
            return_value=str(gemini_config_path.parent / "mcp.json"),
        ):
            servers = registry._discover_gemini()

            assert "search-server" in servers
            assert servers["search-server"].env == {"API_KEY": "test-key"}
            assert "search" in servers["search-server"].capabilities

    def test_discover_gemini_file_not_found(self, registry):
        """Test Gemini discovery when config doesn't exist"""
        with patch("os.path.exists", return_value=False):
            servers = registry._discover_gemini()
            assert servers == {}

    def test_discover_gemini_json_decode_error(self, registry, tmp_path):
        """Test Gemini discovery with invalid JSON config"""
        gemini_config_path = tmp_path / ".gemini" / "mcp.json"
        gemini_config_path.parent.mkdir(parents=True)
        gemini_config_path.write_text("invalid json{{{")

        with patch(
            "os.path.expanduser",
            return_value=str(gemini_config_path),
        ):
            servers = registry._discover_gemini()
            assert servers == {}

    def test_discover_gemini_permission_error(self, registry, tmp_path):
        """Test Gemini discovery with permission error reading config"""
        gemini_config_path = tmp_path / ".gemini" / "mcp.json"
        gemini_config_path.parent.mkdir(parents=True)
        gemini_config_path.write_text('{"mcpServers": {}}')

        with patch(
            "os.path.expanduser",
            return_value=str(gemini_config_path),
        ):
            with patch("builtins.open", side_effect=PermissionError("denied")):
                with patch("os.path.exists", return_value=True):
                    servers = registry._discover_gemini()
                    assert servers == {}

    def test_discover_gemini_os_error(self, registry, tmp_path):
        """Test Gemini discovery with OS error reading config"""
        gemini_config_path = tmp_path / ".gemini" / "mcp.json"
        gemini_config_path.parent.mkdir(parents=True)
        gemini_config_path.write_text('{"mcpServers": {}}')

        with patch(
            "os.path.expanduser",
            return_value=str(gemini_config_path),
        ):
            with patch("builtins.open", side_effect=OSError("OS error")):
                with patch("os.path.exists", return_value=True):
                    servers = registry._discover_gemini()
                    assert servers == {}

    def test_discover_all(self, registry):
        """Test discovering all servers"""
        claude_servers = {
            "claude-server": MCPServerInfo("claude-server", "test", [], source="claude")
        }
        gemini_servers = {
            "gemini-server": MCPServerInfo("gemini-server", "test", [], source="gemini")
        }

        # Use nested with statements to avoid Black AST bug
        with patch.object(registry, "_discover_claude", return_value=claude_servers):
            with patch.object(registry, "_discover_gemini", return_value=gemini_servers):
                all_servers = registry.discover_all()

                assert len(all_servers) == 2
                assert "claude-server" in all_servers
                assert "gemini-server" in all_servers

    def test_discover_all_gemini_dedup(self, registry):
        """Test discover_all skips Gemini servers already discovered from Claude"""
        claude_servers = {
            "shared-server": MCPServerInfo(
                "shared-server", "npx", ["-y", "server"], source="claude"
            )
        }
        gemini_servers = {
            "shared-server": MCPServerInfo(
                "shared-server", "npx", ["-y", "different"], source="gemini"
            ),
            "gemini-only": MCPServerInfo("gemini-only", "node", ["g.js"], source="gemini"),
        }

        with patch.object(registry, "_discover_claude", return_value=claude_servers):
            with patch.object(registry, "_discover_gemini", return_value=gemini_servers):
                all_servers = registry.discover_all()

                assert len(all_servers) == 2
                # shared-server should be from Claude, not overwritten by Gemini
                assert all_servers["shared-server"].source == "claude"
                assert "gemini-only" in all_servers

    def test_sync(self, registry):
        """Test syncing with CLI configurations"""
        with patch.object(registry, "discover_all") as mock_discover:
            mock_discover.return_value = {"test": MCPServerInfo("test", "cmd", [])}
            result = registry.sync()

            mock_discover.assert_called_once()
            assert result == {"test": MCPServerInfo("test", "cmd", [])}

    def test_get_summary(self, registry):
        """Test getting summary"""
        server1 = MCPServerInfo(
            name="enabled-server",
            command="test",
            args=[],
            enabled_for_router=True,
            capabilities=["database"],
            source="claude",
        )
        server2 = MCPServerInfo(
            name="disabled-server",
            command="test",
            args=[],
            enabled_for_router=False,
            source="gemini",
        )

        registry.servers = {"enabled-server": server1, "disabled-server": server2}

        summary = registry.get_summary()

        assert "Total MCP servers discovered: 2" in summary
        assert "Enabled for router: 1" in summary
        assert "enabled-server" in summary
        assert "disabled-server" in summary

    def test_get_summary_empty(self, registry):
        """Test getting summary with no servers"""
        summary = registry.get_summary()
        assert "Total MCP servers discovered: 0" in summary
        assert "Enabled for router: 0" in summary

    def test_get_summary_no_capabilities(self, registry):
        """Test getting summary for server with empty capabilities"""
        server = MCPServerInfo(
            name="no-caps",
            command="test",
            args=[],
            enabled_for_router=False,
            capabilities=[],
            source="devaid",
        )
        registry.servers = {"no-caps": server}

        summary = registry.get_summary()
        assert "no-caps" in summary
        assert "unknown" in summary  # empty capabilities shows "unknown"

    def test_get_summary_multiple_capabilities(self, registry):
        """Test getting summary for server with multiple capabilities"""
        server = MCPServerInfo(
            name="multi-server",
            command="test",
            args=[],
            enabled_for_router=True,
            capabilities=["database", "search", "github"],
            source="claude",
        )
        registry.servers = {"multi-server": server}

        summary = registry.get_summary()
        assert "database, search, github" in summary
        assert "Enabled" in summary
