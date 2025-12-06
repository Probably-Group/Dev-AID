"""
MCP Client for Dev-AID Router

Implements Model Context Protocol client to connect to MCP servers
and execute tools for enhanced context gathering.
"""

import json
import subprocess
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import time


@dataclass
class MCPTool:
    """Represents an MCP tool"""

    name: str
    description: str
    input_schema: Dict[str, Any]
    server: str


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server"""

    name: str
    command: str
    args: List[str]
    env: Optional[Dict[str, str]] = None


class MCPClient:
    """Client for communicating with MCP servers via stdio protocol"""

    def __init__(self, server_config: MCPServerConfig):
        """
        Initialize MCP client

        Args:
            server_config: Configuration for the MCP server
        """
        self.config = server_config
        self.process: Optional[asyncio.subprocess.Process] = None
        self.message_id = 0
        self.available_tools: Dict[str, MCPTool] = {}

    async def connect(self) -> bool:
        """
        Connect to MCP server

        Returns:
            True if connection successful
        """
        try:
            # Start MCP server process
            env = self.config.env if self.config.env else {}

            self.process = await asyncio.create_subprocess_exec(
                self.config.command,
                *self.config.args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**dict(os.environ), **env},
            )

            # Initialize connection
            init_response = await self._send_request(
                {
                    "jsonrpc": "2.0",
                    "id": self._next_id(),
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "devaid-router", "version": "1.0.0"},
                    },
                }
            )

            if "result" not in init_response:
                return False

            # List available tools
            tools_response = await self._send_request(
                {"jsonrpc": "2.0", "id": self._next_id(), "method": "tools/list", "params": {}}
            )

            if "result" in tools_response and "tools" in tools_response["result"]:
                for tool in tools_response["result"]["tools"]:
                    self.available_tools[tool["name"]] = MCPTool(
                        name=tool["name"],
                        description=tool.get("description", ""),
                        input_schema=tool.get("inputSchema", {}),
                        server=self.config.name,
                    )

            return True

        except Exception as e:
            print(f"Failed to connect to MCP server {self.config.name}: {e}")
            return False

    async def disconnect(self):
        """Disconnect from MCP server"""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            self.process = None

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call an MCP tool

        Args:
            tool_name: Name of the tool to call
            arguments: Arguments for the tool

        Returns:
            Tool execution result
        """
        if tool_name not in self.available_tools:
            raise ValueError(f"Tool {tool_name} not available on server {self.config.name}")

        response = await self._send_request(
            {
                "jsonrpc": "2.0",
                "id": self._next_id(),
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": arguments},
            }
        )

        if "error" in response:
            raise RuntimeError(f"MCP tool error: {response['error']}")

        return response.get("result", {})

    async def _send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send JSON-RPC request to MCP server

        Args:
            request: JSON-RPC request

        Returns:
            JSON-RPC response
        """
        if not self.process:
            raise RuntimeError("Not connected to MCP server")

        # Send request
        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json.encode())
        await self.process.stdin.drain()

        # Read response
        response_line = await self.process.stdout.readline()
        response = json.loads(response_line.decode())

        return response

    def _next_id(self) -> int:
        """Get next message ID"""
        self.message_id += 1
        return self.message_id

    def get_tools(self) -> List[MCPTool]:
        """Get list of available tools from this server"""
        return list(self.available_tools.values())


class MCPClientPool:
    """Pool of MCP clients for multiple servers"""

    def __init__(self):
        """Initialize MCP client pool"""
        self.clients: Dict[str, MCPClient] = {}

    async def add_server(self, config: MCPServerConfig) -> bool:
        """
        Add and connect to an MCP server

        Args:
            config: Server configuration

        Returns:
            True if successful
        """
        if config.name in self.clients:
            return True

        client = MCPClient(config)
        if await client.connect():
            self.clients[config.name] = client
            return True

        return False

    async def remove_server(self, name: str):
        """
        Remove MCP server from pool

        Args:
            name: Server name
        """
        if name in self.clients:
            await self.clients[name].disconnect()
            del self.clients[name]

    async def call_tool(
        self, server_name: str, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call tool on specific server

        Args:
            server_name: Name of the server
            tool_name: Name of the tool
            arguments: Tool arguments

        Returns:
            Tool result
        """
        if server_name not in self.clients:
            raise ValueError(f"Server {server_name} not in pool")

        return await self.clients[server_name].call_tool(tool_name, arguments)

    def get_all_tools(self) -> Dict[str, List[MCPTool]]:
        """
        Get all available tools from all servers

        Returns:
            Dict mapping server name to list of tools
        """
        return {name: client.get_tools() for name, client in self.clients.items()}

    async def disconnect_all(self):
        """Disconnect from all servers"""
        for client in self.clients.values():
            await client.disconnect()
        self.clients.clear()


# Import os module that was missing
import os
