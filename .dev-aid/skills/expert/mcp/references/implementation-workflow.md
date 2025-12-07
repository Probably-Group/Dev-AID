## 2. Implementation Workflow (TDD)

Follow this workflow for all MCP implementations:

### Step 1: Write Failing Test First

```python
# tests/test_mcp_server.py
import pytest
from unittest.mock import AsyncMock, patch
from mcp.server import Server
from myserver.tools import create_file_reader_tool

class TestFileReaderTool:
    """Test MCP tool before implementation."""

    @pytest.fixture
    def server(self):
        return Server("test-server")

    @pytest.mark.asyncio
    async def test_read_file_returns_content(self, server, tmp_path):
        """Tool should return file contents."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, MCP!")

        tool = create_file_reader_tool(allowed_dir=str(tmp_path))
        result = await tool.execute({"path": str(test_file)})

        assert result.content[0].text == "Hello, MCP!"

    @pytest.mark.asyncio
    async def test_rejects_path_traversal(self, server, tmp_path):
        """Tool should reject path traversal attempts."""
        tool = create_file_reader_tool(allowed_dir=str(tmp_path))

        with pytest.raises(ValueError, match="Path traversal"):
            await tool.execute({"path": "../../../etc/passwd"})

    @pytest.mark.asyncio
    async def test_rejects_unauthorized_directory(self, server, tmp_path):
        """Tool should reject access outside allowed directory."""
        tool = create_file_reader_tool(allowed_dir=str(tmp_path))

        with pytest.raises(PermissionError, match="Access denied"):
            await tool.execute({"path": "/etc/passwd"})
```

### Step 2: Implement Minimum to Pass

```python
# myserver/tools.py
from pathlib import Path
from mcp.types import TextContent

def create_file_reader_tool(allowed_dir: str):
    """Create a secure file reader tool."""
    base_path = Path(allowed_dir).resolve()

    async def execute(arguments: dict) -> dict:
        path = arguments.get("path", "")

        # Validate path traversal
        if ".." in path:
            raise ValueError("Path traversal not allowed")

        file_path = Path(path).resolve()

        # Validate directory access
        if not str(file_path).startswith(str(base_path)):
            raise PermissionError("Access denied")

        content = file_path.read_text()
        return {"content": [TextContent(type="text", text=content)]}

    return type("Tool", (), {"execute": execute})()
```

### Step 3: Refactor if Needed

Add caching, connection pooling, or additional validation while keeping tests passing.

### Step 4: Run Full Verification

```bash
# Run all MCP tests
pytest tests/test_mcp_server.py -v

# Run with coverage
pytest --cov=myserver --cov-report=term-missing

# Run security-specific tests
pytest tests/ -k "security or injection or traversal" -v
```

---

