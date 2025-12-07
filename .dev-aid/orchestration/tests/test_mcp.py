"""Tests for MCP client and registry"""

import asyncio
import json
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from router.mcp_client import (
    MCPClient,
    MCPClientPool,
    MCPServerConfig,
    MCPTool,
)
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
        config = MCPServerConfig(
            name="test-server", command="npx", args=["-y", "test-mcp-server"]
        )
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

        with patch(
            "asyncio.create_subprocess_exec", return_value=mock_process
        ) as mock_exec:
            result = await mcp_client.connect()

            assert result is True
            assert mcp_client.process is not None
            assert "search" in mcp_client.available_tools
            assert mcp_client.available_tools["search"].name == "search"
            mock_exec.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_failure(self, mcp_client):
        """Test connection failure"""
        with patch(
            "asyncio.create_subprocess_exec", side_effect=Exception("Failed to start")
        ):
            result = await mcp_client.connect()
            assert result is False
            assert mcp_client.process is None

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
        with patch.object(
            MCPClient, "call_tool", return_value=mock_result
        ) as mock_call:
            result = await pool.call_tool("test-server", "test_tool", {"arg": "val"})

            assert result == mock_result
            mock_call.assert_called_once_with("test_tool", {"arg": "val"})

    @pytest.mark.asyncio
    async def test_call_tool_server_not_found(self, pool):
        """Test calling tool on server that doesn't exist"""
        with pytest.raises(ValueError, match="Server .* not in pool"):
            await pool.call_tool("nonexistent", "tool", {})

    def test_get_all_tools(self, pool):
        """Test getting all tools from all servers"""
        # Create mock clients with tools
        mock_client1 = Mock()
        mock_client1.get_tools = Mock(
            return_value=[MCPTool("tool1", "Test", {}, "server1")]
        )

        mock_client2 = Mock()
        mock_client2.get_tools = Mock(
            return_value=[MCPTool("tool2", "Test", {}, "server2")]
        )

        pool.clients = {"server1": mock_client1, "server2": mock_client2}

        all_tools = pool.get_all_tools()

        assert "server1" in all_tools
        assert "server2" in all_tools
        assert len(all_tools["server1"]) == 1
        assert len(all_tools["server2"]) == 1

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
        server = MCPServerInfo(
            name="test-server", command="test", args=[], enabled_for_router=True
        )
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
        server1 = MCPServerInfo(
            name="enabled", command="test", args=[], enabled_for_router=True
        )
        server2 = MCPServerInfo(
            name="disabled", command="test", args=[], enabled_for_router=False
        )

        registry.servers = {"enabled": server1, "disabled": server2}

        enabled = registry.get_enabled_servers()

        assert len(enabled) == 1
        assert "enabled" in enabled
        assert "disabled" not in enabled

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

        with patch.object(registry, "_read_claude_config", return_value=mock_config):
            servers = registry._discover_claude()

            assert "test-server" in servers
            assert servers["test-server"].command == "npx"
            assert servers["test-server"].source == "claude"

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
            "os.path.expanduser", return_value=str(gemini_config_path.parent / "mcp.json")
        ):
            servers = registry._discover_gemini()

            assert "gemini-server" in servers
            assert servers["gemini-server"].command == "node"
            assert servers["gemini-server"].source == "gemini"

    def test_discover_gemini_file_not_found(self, registry):
        """Test Gemini discovery when config doesn't exist"""
        with patch("os.path.exists", return_value=False):
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

        with patch.object(
            registry, "_discover_claude", return_value=claude_servers
        ), patch.object(registry, "_discover_gemini", return_value=gemini_servers):
            all_servers = registry.discover_all()

            assert len(all_servers) == 2
            assert "claude-server" in all_servers
            assert "gemini-server" in all_servers

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
