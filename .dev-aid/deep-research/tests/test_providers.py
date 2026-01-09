"""Tests for research providers."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from providers.base import (
    ProviderNotAvailableError,
    ResearchDepth,
    ResearchResult,
)
from providers.perplexity import PerplexityProvider
from providers.tavily import TavilyProvider


class TestTavilyProvider:
    """Tests for Tavily provider."""

    def test_name(self):
        """Test provider name."""
        provider = TavilyProvider(api_key="test-key")
        assert provider.name == "tavily"

    def test_supported_depths(self):
        """Test supported depth levels."""
        provider = TavilyProvider(api_key="test-key")
        assert ResearchDepth.QUICK in provider.supported_depths
        assert ResearchDepth.STANDARD in provider.supported_depths
        assert ResearchDepth.DEEP not in provider.supported_depths

    def test_is_available_with_key(self):
        """Test availability with API key."""
        provider = TavilyProvider(api_key="test-key")
        assert provider.is_available() is True

    def test_is_not_available_without_key(self):
        """Test unavailability without API key."""
        provider = TavilyProvider(api_key=None)
        assert provider.is_available() is False

    @pytest.mark.asyncio
    async def test_search_raises_without_key(self):
        """Test search raises error without API key."""
        provider = TavilyProvider(api_key=None)

        with pytest.raises(ProviderNotAvailableError):
            await provider.search("test query")

    @pytest.mark.asyncio
    async def test_search_quick_depth(self, mock_tavily_response):
        """Test quick search returns correct result."""
        provider = TavilyProvider(api_key="test-key")

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_tavily_response
            mock_response.raise_for_status = Mock()
            mock_client.post.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            result = await provider.search(
                "latest Node.js version",
                depth=ResearchDepth.QUICK,
            )

            assert isinstance(result, ResearchResult)
            assert result.provider == "tavily"
            assert result.depth == ResearchDepth.QUICK
            assert "Node.js" in result.content
            assert len(result.sources) > 0


class TestPerplexityProvider:
    """Tests for Perplexity provider."""

    def test_name(self):
        """Test provider name."""
        provider = PerplexityProvider(api_key="test-key")
        assert provider.name == "perplexity-sonar"

    def test_supported_depths(self):
        """Test supported depth levels."""
        provider = PerplexityProvider(api_key="test-key")
        assert ResearchDepth.STANDARD in provider.supported_depths
        assert ResearchDepth.DEEP in provider.supported_depths
        assert ResearchDepth.QUICK not in provider.supported_depths

    def test_is_available_with_key(self):
        """Test availability with API key."""
        provider = PerplexityProvider(api_key="test-key")
        assert provider.is_available() is True

    def test_is_not_available_without_key(self):
        """Test unavailability without API key."""
        provider = PerplexityProvider(api_key=None)
        assert provider.is_available() is False

    @pytest.mark.asyncio
    async def test_search_raises_without_key(self):
        """Test search raises error without API key."""
        provider = PerplexityProvider(api_key=None)

        with pytest.raises(ProviderNotAvailableError):
            await provider.search("test query")

    @pytest.mark.asyncio
    async def test_search_standard_depth(self, mock_perplexity_response):
        """Test standard search returns correct result."""
        provider = PerplexityProvider(api_key="test-key")

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_perplexity_response
            mock_response.raise_for_status = Mock()
            mock_client.post.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client

            result = await provider.search(
                "Compare React vs Vue",
                depth=ResearchDepth.STANDARD,
            )

            assert isinstance(result, ResearchResult)
            assert result.provider == "perplexity-sonar"
            assert result.depth == ResearchDepth.STANDARD
            assert len(result.citations) > 0
