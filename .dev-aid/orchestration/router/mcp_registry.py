"""
MCP Registry - Discover and manage MCP servers

Discovers MCP servers from:
- Claude Code configuration
- Gemini CLI configuration
- Manual Dev-AID configuration
"""

import json
import os
import subprocess
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class MCPServerInfo:
    """Information about an MCP server"""

    name: str
    command: str
    args: List[str]
    env: Optional[Dict[str, str]] = None
    source: str = "unknown"  # "claude", "gemini", "devaid"
    capabilities: List[str] = None  # ["database", "github", "search", etc.]
    enabled_for_router: bool = False

    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []


class MCPRegistry:
    """Registry for discovering and managing MCP servers"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize MCP registry

        Args:
            config_path: Path to Dev-AID MCP configuration file
        """
        if config_path is None:
            config_path = os.path.expanduser("~/.dev-aid/orchestration/config/mcp-config.json")

        self.config_path = config_path
        self.servers: Dict[str, MCPServerInfo] = {}

        # Load existing configuration
        self._load_config()

    def discover_all(self) -> Dict[str, MCPServerInfo]:
        """
        Discover all MCP servers from all sources

        Returns:
            Dict of server name to MCPServerInfo
        """
        # Discover from Claude Code
        claude_servers = self._discover_claude()
        for name, server in claude_servers.items():
            self.servers[name] = server

        # Discover from Gemini CLI
        gemini_servers = self._discover_gemini()
        for name, server in gemini_servers.items():
            if name not in self.servers:
                self.servers[name] = server

        # Apply saved configuration (enabled/disabled state)
        self._load_config()

        return self.servers

    def _discover_claude(self) -> Dict[str, MCPServerInfo]:
        """
        Discover MCP servers from Claude Code

        Returns:
            Dict of server name to MCPServerInfo
        """
        servers = {}

        try:
            # Try using 'claude mcp list' command
            result = subprocess.run(
                ["claude", "mcp", "list"], capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                # Parse output
                # Expected format: name, command, status
                lines = result.stdout.strip().split("\n")
                for line in lines[1:]:  # Skip header
                    if not line.strip():
                        continue

                    parts = line.split()
                    if len(parts) >= 2:
                        name = parts[0]
                        # Get full config by reading Claude's config file
                        config = self._read_claude_config()
                        if config and name in config.get("mcpServers", {}):
                            server_config = config["mcpServers"][name]
                            servers[name] = MCPServerInfo(
                                name=name,
                                command=server_config.get("command", ""),
                                args=server_config.get("args", []),
                                env=server_config.get("env"),
                                source="claude",
                                capabilities=self._infer_capabilities(name),
                            )

        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            # Claude CLI not available, try reading config directly
            config = self._read_claude_config()
            if config:
                for name, server_config in config.get("mcpServers", {}).items():
                    servers[name] = MCPServerInfo(
                        name=name,
                        command=server_config.get("command", ""),
                        args=server_config.get("args", []),
                        env=server_config.get("env"),
                        source="claude",
                        capabilities=self._infer_capabilities(name),
                    )

        return servers

    def _read_claude_config(self) -> Optional[Dict]:
        """Read Claude Code configuration file"""
        config_paths = [
            os.path.expanduser("~/.claude-code/config.json"),
            os.path.expanduser("~/.claude/config.json"),
        ]

        for path in config_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r") as f:
                        return json.load(f)
                except Exception:
                    continue

        return None

    def _discover_gemini(self) -> Dict[str, MCPServerInfo]:
        """
        Discover MCP servers from Gemini CLI

        Returns:
            Dict of server name to MCPServerInfo
        """
        servers = {}

        gemini_config_path = os.path.expanduser("~/.gemini/mcp.json")

        if os.path.exists(gemini_config_path):
            try:
                with open(gemini_config_path, "r") as f:
                    config = json.load(f)

                for name, server_config in config.get("mcpServers", {}).items():
                    servers[name] = MCPServerInfo(
                        name=name,
                        command=server_config.get("command", ""),
                        args=server_config.get("args", []),
                        env=server_config.get("env"),
                        source="gemini",
                        capabilities=self._infer_capabilities(name),
                    )

            except Exception as e:
                print(f"Failed to read Gemini config: {e}")

        return servers

    def _infer_capabilities(self, server_name: str) -> List[str]:
        """
        Infer capabilities from server name

        Args:
            server_name: Name of the MCP server

        Returns:
            List of capability tags
        """
        name_lower = server_name.lower()
        capabilities = []

        # Database servers
        if any(db in name_lower for db in ["postgres", "mysql", "sqlite", "database", "db"]):
            capabilities.append("database")

        # Version control
        if any(vcs in name_lower for vcs in ["github", "gitlab", "git"]):
            capabilities.append("github")

        # Search
        if any(search in name_lower for search in ["search", "code-search", "brave", "exa"]):
            capabilities.append("search")

        # Filesystem
        if any(fs in name_lower for fs in ["file", "filesystem", "fs"]):
            capabilities.append("filesystem")

        # Communication
        if any(comm in name_lower for comm in ["slack", "discord", "teams"]):
            capabilities.append("communication")

        # Browser automation
        if any(browser in name_lower for browser in ["puppeteer", "playwright", "selenium"]):
            capabilities.append("browser")

        # Project management
        if any(pm in name_lower for pm in ["jira", "linear", "asana"]):
            capabilities.append("project-management")

        # Cloud
        if any(cloud in name_lower for cloud in ["aws", "gcp", "azure", "cloud"]):
            capabilities.append("cloud")

        # Research (NEW)
        if any(
            research in name_lower
            for research in ["research", "deep-research", "tavily", "perplexity"]
        ):
            capabilities.append("research")

        return capabilities

    def enable_server(self, name: str) -> bool:
        """
        Enable MCP server for router use

        Args:
            name: Server name

        Returns:
            True if successful
        """
        if name not in self.servers:
            return False

        self.servers[name].enabled_for_router = True
        self._save_config()
        return True

    def disable_server(self, name: str) -> bool:
        """
        Disable MCP server for router use

        Args:
            name: Server name

        Returns:
            True if successful
        """
        if name not in self.servers:
            return False

        self.servers[name].enabled_for_router = False
        self._save_config()
        return True

    def get_enabled_servers(self) -> Dict[str, MCPServerInfo]:
        """
        Get all enabled MCP servers

        Returns:
            Dict of enabled servers
        """
        return {name: server for name, server in self.servers.items() if server.enabled_for_router}

    def get_servers_by_capability(self, capability: str) -> List[MCPServerInfo]:
        """
        Get servers with specific capability

        Args:
            capability: Capability to filter by

        Returns:
            List of matching servers
        """
        return [
            server
            for server in self.servers.values()
            if capability in server.capabilities and server.enabled_for_router
        ]

    def sync(self) -> Dict[str, MCPServerInfo]:
        """
        Re-scan and sync with CLI configurations

        Returns:
            Updated servers dict
        """
        return self.discover_all()

    def _load_config(self):
        """Load saved configuration"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    config = json.load(f)

                # Apply enabled/disabled state
                for name, saved_server in config.get("servers", {}).items():
                    if name in self.servers:
                        self.servers[name].enabled_for_router = saved_server.get("enabled", False)

            except Exception as e:
                print(f"Failed to load MCP config: {e}")

    def _save_config(self):
        """Save configuration"""
        config = {"version": "1.0.0", "servers": {}}

        for name, server in self.servers.items():
            config["servers"][name] = {
                "name": name,
                "enabled": server.enabled_for_router,
                "capabilities": server.capabilities,
                "source": server.source,
            }

        # Ensure directory exists
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=2)

    def get_summary(self) -> str:
        """
        Get human-readable summary of MCP servers

        Returns:
            Formatted summary string
        """
        lines = []
        lines.append(f"Total MCP servers discovered: {len(self.servers)}")
        lines.append(f"Enabled for router: {len(self.get_enabled_servers())}")
        lines.append("")

        for name, server in self.servers.items():
            status = "✓ Enabled" if server.enabled_for_router else "  Disabled"
            capabilities = ", ".join(server.capabilities) if server.capabilities else "unknown"
            lines.append(f"{status} | {name:20s} | {server.source:10s} | {capabilities}")

        return "\n".join(lines)
