"""Shared test fixtures for deep-research tests."""

import tempfile
from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock, Mock

import pytest


@pytest.fixture
def temp_cache_dir():
    """Create temporary cache directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_tavily_response() -> Dict[str, Any]:
    """Mock successful Tavily API response."""
    return {
        "answer": "Node.js 22 is the current LTS version as of 2025.",
        "results": [
            {
                "title": "Node.js Releases",
                "url": "https://nodejs.org/en/about/releases/",
                "content": "Current LTS: v22.x (Jod)",
                "score": 0.95,
            },
            {
                "title": "Download Node.js",
                "url": "https://nodejs.org/en/download/",
                "content": "Download the latest LTS version of Node.js",
                "score": 0.88,
            },
        ],
    }


@pytest.fixture
def mock_perplexity_response() -> Dict[str, Any]:
    """Mock successful Perplexity API response."""
    return {
        "choices": [
            {
                "message": {
                    "content": "Based on my research, here are the key findings..."
                }
            }
        ],
        "citations": [
            "https://example.com/source1",
            "https://example.com/source2",
        ],
        "usage": {
            "prompt_tokens": 150,
            "completion_tokens": 500,
        },
    }


@pytest.fixture
def mock_httpx_client():
    """Create mock httpx AsyncClient."""
    mock_client = AsyncMock()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()
    mock_client.post.return_value = mock_response
    return mock_client, mock_response


@pytest.fixture
def sample_research_result() -> Dict[str, Any]:
    """Sample research result for testing."""
    return {
        "query": "What is the latest Node.js version?",
        "content": "Node.js 22 is the current LTS version.",
        "sources": [
            {
                "title": "Node.js Releases",
                "url": "https://nodejs.org/en/about/releases/",
                "snippet": "Current LTS: v22.x",
            }
        ],
        "provider": "tavily",
        "depth": "quick",
        "citations": ["https://nodejs.org/en/about/releases/"],
        "confidence_score": 0.8,
        "processing_time_ms": 1500,
        "cached": False,
    }
