"""Perplexity Sonar provider.

Perplexity offers two main models for research:
- sonar: Standard search with citations
- sonar-deep-research: Multi-step comprehensive research

API: https://api.perplexity.ai/chat/completions
Pricing: $0.002/1K input tokens, $0.008/1K output tokens
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


class PerplexityProvider(ResearchProvider):
    """Perplexity Sonar API provider.

    Best for: Technology comparisons, implementation guides, multi-source synthesis.
    """

    ENDPOINT = "https://api.perplexity.ai/chat/completions"
    DEFAULT_TIMEOUT = 60.0
    DEEP_TIMEOUT = 120.0

    # Model mapping by depth
    MODELS = {
        ResearchDepth.STANDARD: "sonar",
        ResearchDepth.DEEP: "sonar-deep-research",
    }

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Perplexity provider.

        Args:
            api_key: Perplexity API key. Falls back to PERPLEXITY_API_KEY env var.
        """
        self._api_key = api_key or os.getenv("PERPLEXITY_API_KEY")

    @property
    def name(self) -> str:
        return "perplexity-sonar"

    @property
    def supported_depths(self) -> List[ResearchDepth]:
        return [ResearchDepth.STANDARD, ResearchDepth.DEEP]

    def is_available(self) -> bool:
        return bool(self._api_key)

    async def search(
        self,
        query: str,
        depth: ResearchDepth = ResearchDepth.STANDARD,
        max_sources: int = 10,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> ResearchResult:
        """Execute Perplexity search.

        Args:
            query: Search query
            depth: STANDARD for sonar, DEEP for sonar-deep-research
            max_sources: Hint for number of sources (not directly controllable)
            system_prompt: Optional system prompt for context
            **kwargs: Additional options

        Returns:
            ResearchResult with synthesized content and citations

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
                "Set PERPLEXITY_API_KEY environment variable",
            )

        start_time = time.time()

        # Select model based on depth
        model = self.MODELS.get(depth, "sonar")
        timeout = self.DEEP_TIMEOUT if depth == ResearchDepth.DEEP else self.DEFAULT_TIMEOUT

        # Build messages
        messages: List[Dict[str, str]] = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Add research-focused instruction
        research_instruction = (
            "Provide a comprehensive answer with citations. "
            "Include relevant sources and be specific about versions, dates, and facts."
        )
        messages.append(
            {
                "role": "user",
                "content": f"{research_instruction}\n\nQuery: {query}",
            }
        )

        # Build request payload
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "return_citations": True,
        }

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.ENDPOINT,
                    headers=headers,
                    json=payload,
                    timeout=timeout,
                )

                if response.status_code == 429:
                    raise ProviderRateLimitError(
                        "Rate limit exceeded",
                        self.name,
                    )

                response.raise_for_status()
                data = response.json()

        except httpx.TimeoutException as e:
            raise ProviderTimeoutError(
                f"Request timed out after {timeout}s",
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

        # Parse response
        choice = data.get("choices", [{}])[0]
        message = choice.get("message", {})
        content = message.get("content", "")
        citations = data.get("citations", [])

        # Build sources from citations
        sources = [
            {
                "title": "",
                "url": url,
                "snippet": "",
            }
            for url in citations
        ]

        # Confidence based on depth and citations
        confidence = 0.85 if depth == ResearchDepth.DEEP else 0.7
        if len(citations) == 0:
            confidence = 0.4

        # Track token usage for cost
        usage = data.get("usage", {})

        return ResearchResult(
            query=query,
            content=content,
            sources=sources,
            provider=self.name,
            depth=depth,
            citations=citations,
            confidence_score=confidence,
            processing_time_ms=processing_time,
            metadata={
                "model": model,
                "input_tokens": usage.get("prompt_tokens", 0),
                "output_tokens": usage.get("completion_tokens", 0),
            },
        )
