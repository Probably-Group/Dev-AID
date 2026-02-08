"""Tavily search provider.

Tavily is optimized for fast, LLM-friendly web search with two modes:
- Basic search (1 credit): Quick factual lookups
- Advanced search (2 credits): Deeper search with more sources

API: https://api.tavily.com/search
Free tier: 1,000 credits/month
"""

import logging
import os
import time
from typing import Any, Dict, List, Optional

import httpx

from .base import (
    ProviderError,
    ProviderNotAvailableError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ResearchDepth,
    ResearchProvider,
    ResearchResult,
)

logger = logging.getLogger(__name__)


class TavilyProvider(ResearchProvider):
    """Tavily search API provider.

    Best for: Quick factual lookups, documentation search, simple how-to queries.
    """

    ENDPOINT = "https://api.tavily.com/search"
    DEFAULT_TIMEOUT = 30.0

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Tavily provider.

        Args:
            api_key: Tavily API key. Falls back to TAVILY_API_KEY env var.
        """
        self._api_key = api_key or os.getenv("TAVILY_API_KEY")

    @property
    def name(self) -> str:
        return "tavily"

    @property
    def supported_depths(self) -> List[ResearchDepth]:
        return [ResearchDepth.QUICK, ResearchDepth.STANDARD]

    def is_available(self) -> bool:
        return bool(self._api_key)

    async def search(
        self,
        query: str,
        depth: ResearchDepth = ResearchDepth.STANDARD,
        max_sources: int = 10,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> ResearchResult:
        """Execute Tavily search.

        Args:
            query: Search query
            depth: QUICK for basic (1 credit), STANDARD for advanced (2 credits)
            max_sources: Max results (1-20)
            include_domains: Only search these domains
            exclude_domains: Exclude these domains
            **kwargs: Additional Tavily-specific options

        Returns:
            ResearchResult with answer and sources

        Raises:
            ProviderNotAvailableError: If API key not configured
            ProviderRateLimitError: If rate limit exceeded
            ProviderTimeoutError: If request times out
            ProviderError: For other errors
        """
        if not self.is_available():
            raise ProviderNotAvailableError(
                "API key not configured",
                self.name,
                "Set TAVILY_API_KEY environment variable",
            )

        start_time = time.time()

        # Map depth to Tavily search type
        search_depth = "basic" if depth == ResearchDepth.QUICK else "advanced"

        # Build request payload
        payload: Dict[str, Any] = {
            "api_key": self._api_key,
            "query": query,
            "search_depth": search_depth,
            "include_answer": True,
            "include_raw_content": False,
            "max_results": min(max_sources, 20),
        }

        if include_domains:
            payload["include_domains"] = include_domains
        if exclude_domains:
            payload["exclude_domains"] = exclude_domains

        try:
            async with httpx.AsyncClient(timeout=self.DEFAULT_TIMEOUT) as client:
                response = await client.post(
                    self.ENDPOINT,
                    json=payload,
                    timeout=self.DEFAULT_TIMEOUT,
                )

                if response.status_code == 429:
                    raise ProviderRateLimitError(
                        "Rate limit exceeded",
                        self.name,
                        "Monthly credit limit may be reached",
                    )

                response.raise_for_status()
                data = response.json()

        except httpx.TimeoutException as e:
            raise ProviderTimeoutError(
                f"Request timed out after {self.DEFAULT_TIMEOUT}s",
                self.name,
                str(e),
            )
        except httpx.HTTPStatusError as e:
            raise ProviderError(
                f"HTTP error: {e.response.status_code}",
                self.name,
                str(e),
            )
        except Exception as e:
            raise ProviderError(
                "Search failed",
                self.name,
                str(e),
            )

        processing_time = int((time.time() - start_time) * 1000)

        # Parse results
        sources = [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "snippet": r.get("content", ""),
                "score": r.get("score", 0.0),
            }
            for r in data.get("results", [])
        ]

        citations = [s["url"] for s in sources if s.get("url")]

        # Confidence based on search depth and result count
        confidence = 0.6 if depth == ResearchDepth.QUICK else 0.8
        if len(sources) == 0:
            confidence = 0.2

        return ResearchResult(
            query=query,
            content=data.get("answer", ""),
            sources=sources,
            provider=self.name,
            depth=depth,
            citations=citations,
            confidence_score=confidence,
            processing_time_ms=processing_time,
            metadata={
                "search_depth": search_depth,
                "results_count": len(sources),
            },
        )
