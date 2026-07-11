"""Regression tests for audit Sprint-2 MCP client robustness (B-1, M11, M12)."""

import json
from unittest.mock import AsyncMock, Mock

import pytest

from router.mcp_client import (
    MCPClient,
    MCPServerConfig,
    MCPTool,
    _is_env_override_blocked,
)


def _client():
    return MCPClient(MCPServerConfig(name="test", command="x", args=[]))


def _line(obj):
    return (json.dumps(obj) + "\n").encode()


# --------------------------------------------------------------------------- #
# B-1 — a late reply from a timed-out request (old id) is discarded
# --------------------------------------------------------------------------- #
@pytest.mark.asyncio
async def test_send_request_discards_stale_response_by_id():
    client = _client()
    client.available_tools["t"] = MCPTool(name="t", description="", input_schema={}, server="test")

    proc = AsyncMock()
    proc.stdin = AsyncMock()
    proc.stdin.write = Mock()
    proc.stdin.drain = AsyncMock()
    proc.stdout = AsyncMock()
    # First a stale response (id=99 from a prior timed-out call), then the
    # real one whose id matches this request (id=1 on a fresh client).
    proc.stdout.readline = AsyncMock(
        side_effect=[
            _line({"jsonrpc": "2.0", "id": 99, "result": {"stale": True}}),
            _line({"jsonrpc": "2.0", "id": 1, "result": {"ok": True}}),
        ]
    )
    client.process = proc

    result = await client.call_tool("t", {})
    assert result == {"ok": True}


@pytest.mark.asyncio
async def test_send_request_bounded_when_never_matching():
    client = _client()
    client.available_tools["t"] = MCPTool(name="t", description="", input_schema={}, server="test")

    proc = AsyncMock()
    proc.stdin = AsyncMock()
    proc.stdin.write = Mock()
    proc.stdin.drain = AsyncMock()
    proc.stdout = AsyncMock()
    proc.stdout.readline = AsyncMock(
        return_value=_line({"jsonrpc": "2.0", "id": 999, "result": {}})
    )
    client.process = proc

    with pytest.raises(RuntimeError, match="desynchronized"):
        await client.call_tool("t", {})


# --------------------------------------------------------------------------- #
# M11 — dangerous env overrides are blocked
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "key,blocked",
    [
        ("DYLD_INSERT_LIBRARIES", True),
        ("DYLD_LIBRARY_PATH", True),
        ("LD_PRELOAD", True),
        ("LD_LIBRARY_PATH", True),
        ("NODE_OPTIONS", True),
        ("PYTHONPATH", True),
        ("PYTHONSTARTUP", True),
        ("PATH", True),
        ("MY_SERVER_TOKEN", False),
        ("API_BASE_URL", False),
    ],
)
def test_env_override_blocklist(key, blocked):
    assert _is_env_override_blocked(key) is blocked
