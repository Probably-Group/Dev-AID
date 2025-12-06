from unittest.mock import AsyncMock, Mock

import pytest

from router.context_builder import ContextBuilder, DevAIDContext


class TestContextBuilder:
    @pytest.fixture
    def mock_config(self):
        return Mock(
            get_orchestration_mode=Mock(return_value="solo"),
            get_enabled_providers=Mock(return_value=["claude"]),
            root=Path("/tmp"),
        )

    @pytest.fixture
    def builder(self, mock_config):
        return ContextBuilder(mock_config)

    def test_build_context_basic(self, builder):
        # Mock methods that access files
        builder._load_memory_bank = Mock(return_value={})
        builder._detect_active_skills = Mock(return_value=[])
        builder._get_git_context = Mock(return_value={})

        context = builder.build_context()
        assert isinstance(context, DevAIDContext)
        assert context.project_info["orchestration_mode"] == "solo"

    @pytest.mark.asyncio
    async def test_gather_mcp_context(self, builder):
        builder.mcp_pool = AsyncMock()
        builder.mcp_pool.clients = {"code-search": True}
        builder.mcp_pool.call_tool.return_value = {"content": "found"}

        context = await builder.gather_mcp_context("find login logic")

        assert "code_search" in context
        assert context["code_search"]["search_results"] == "found"

    def test_format_context(self, builder):
        context = DevAIDContext(
            memory_bank={"activeContext.md": "# Active\nDoing things"},
            project_info={"name": "Test", "orchestration_mode": "solo"},
            git_context={"branch": "main"},
        )

        formatted = builder.format_context_for_ai(context)
        assert "Project Context" in formatted
        assert "Active Context" in formatted
        assert "# Active" in formatted
        assert "Branch: main" in formatted


from pathlib import Path
