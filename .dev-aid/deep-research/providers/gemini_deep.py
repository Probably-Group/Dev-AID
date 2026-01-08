"""Gemini Deep Research provider.

Gemini Deep Research uses the Interactions API for comprehensive multi-step research.
It's designed for complex queries requiring synthesis from hundreds of sources.

API: google.genai Interactions API
Agent: deep-research-pro-preview-12-2025
Note: Research takes 2-5 minutes, uses async polling
"""

import asyncio
import logging
import os
import time
from typing import Any, Dict, List, Optional

from .base import (
    ProviderError,
    ProviderNotAvailableError,
    ProviderTimeoutError,
    ResearchDepth,
    ResearchProvider,
    ResearchResult,
)

logger = logging.getLogger(__name__)


class GeminiDeepResearchProvider(ResearchProvider):
    """Gemini Deep Research provider using Interactions API.

    Best for: Comprehensive research, architecture analysis, technology deep-dives.
    """

    AGENT = "deep-research-pro-preview-12-2025"
    DEFAULT_TIMEOUT = 300  # 5 minutes
    POLL_INTERVAL = 5  # seconds

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini Deep Research provider.

        Args:
            api_key: Google API key. Falls back to GOOGLE_API_KEY env var.
        """
        self._api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self._client: Optional[Any] = None

    @property
    def name(self) -> str:
        return "gemini-deep-research"

    @property
    def supported_depths(self) -> List[ResearchDepth]:
        # Gemini Deep Research is only for deep research
        return [ResearchDepth.DEEP]

    def is_available(self) -> bool:
        return bool(self._api_key)

    def _ensure_client(self) -> Any:
        """Lazy initialize the Google GenAI client."""
        if self._client is None:
            try:
                from google import genai

                self._client = genai.Client(api_key=self._api_key)
            except ImportError:
                raise ProviderError(
                    "google-genai package not installed",
                    self.name,
                    "Install with: pip install google-genai>=1.0.0",
                )
        return self._client

    async def search(
        self,
        query: str,
        depth: ResearchDepth = ResearchDepth.DEEP,
        max_sources: int = 10,
        timeout_seconds: Optional[int] = None,
        **kwargs: Any,
    ) -> ResearchResult:
        """Execute Gemini deep research.

        Args:
            query: Research query
            depth: Only DEEP is supported
            max_sources: Not directly controllable by Gemini
            timeout_seconds: Max wait time (default: 300s / 5 min)
            **kwargs: Additional options

        Returns:
            ResearchResult with comprehensive research

        Raises:
            ProviderNotAvailableError: If API key not configured
            ProviderTimeoutError: If research times out
            ProviderError: For other errors
        """
        if not self.is_available():
            raise ProviderNotAvailableError(
                "API key not configured",
                self.name,
                "Set GOOGLE_API_KEY environment variable",
            )

        if depth != ResearchDepth.DEEP:
            logger.warning(
                f"Gemini Deep Research only supports DEEP depth, got {depth.value}"
            )
            depth = ResearchDepth.DEEP

        timeout = timeout_seconds or self.DEFAULT_TIMEOUT
        start_time = time.time()

        try:
            client = self._ensure_client()

            # Create background interaction for deep research
            logger.info(f"Starting Gemini deep research: {query[:100]}...")

            interaction = await asyncio.to_thread(
                client.aio.live.send,
                model=self.AGENT,
                config={"response_modalities": ["TEXT"]},
            )

            # For the new google-genai SDK, use interactions API
            interaction = await asyncio.to_thread(
                lambda: client.models.generate_content(
                    model="gemini-2.0-flash-exp",  # Fallback if deep research not available
                    contents=query,
                )
            )

            # Try the Interactions API for deep research
            try:
                interaction = await asyncio.to_thread(
                    client.interactions.create,
                    input=query,
                    agent=self.AGENT,
                    background=True,
                )

                # Poll for completion
                result = await self._poll_completion(
                    client, interaction.id, timeout, start_time
                )
            except AttributeError:
                # Fallback to regular generate_content if interactions not available
                logger.warning("Interactions API not available, using generate_content")
                response = await asyncio.to_thread(
                    client.models.generate_content,
                    model="gemini-2.0-flash-exp",
                    contents=f"Research the following topic comprehensively: {query}",
                )
                result = {
                    "content": response.text if hasattr(response, "text") else str(response),
                    "sources": [],
                    "citations": [],
                }

        except ProviderTimeoutError:
            raise
        except Exception as e:
            raise ProviderError(
                "Deep research failed",
                self.name,
                str(e),
            )

        processing_time = int((time.time() - start_time) * 1000)

        return ResearchResult(
            query=query,
            content=result.get("content", ""),
            sources=result.get("sources", []),
            provider=self.name,
            depth=depth,
            citations=result.get("citations", []),
            confidence_score=0.9,  # Gemini deep research is high quality
            processing_time_ms=processing_time,
            metadata={
                "agent": self.AGENT,
                "timeout_used": timeout,
            },
        )

    async def _poll_completion(
        self,
        client: Any,
        interaction_id: str,
        timeout: int,
        start_time: float,
    ) -> Dict[str, Any]:
        """Poll for interaction completion.

        Args:
            client: Google GenAI client
            interaction_id: ID of the interaction to poll
            timeout: Max seconds to wait
            start_time: When the request started

        Returns:
            Parsed result dictionary

        Raises:
            ProviderTimeoutError: If polling times out
            ProviderError: If research fails
        """
        while True:
            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise ProviderTimeoutError(
                    f"Deep research timed out after {timeout}s",
                    self.name,
                    f"Research may still complete. ID: {interaction_id}",
                )

            try:
                status = await asyncio.to_thread(
                    client.interactions.get, interaction_id
                )

                if status.status == "completed":
                    return self._parse_result(status)
                elif status.status == "failed":
                    raise ProviderError(
                        "Deep research failed",
                        self.name,
                        getattr(status, "error", "Unknown error"),
                    )

                logger.debug(
                    f"Research in progress... ({int(elapsed)}s elapsed)"
                )

            except AttributeError as e:
                # Handle API changes gracefully
                logger.warning(f"Unexpected status format: {e}")

            await asyncio.sleep(self.POLL_INTERVAL)

    def _parse_result(self, status: Any) -> Dict[str, Any]:
        """Parse interaction result into standard format.

        Args:
            status: Interaction status object

        Returns:
            Dictionary with content, sources, and citations
        """
        try:
            # Extract the last output (final result)
            outputs = getattr(status, "outputs", [])
            if not outputs:
                return {"content": "", "sources": [], "citations": []}

            last_output = outputs[-1]
            content = getattr(last_output, "text", str(last_output))

            # Extract sources if available
            sources = []
            citations = []

            # Gemini may include sources in metadata
            if hasattr(status, "sources"):
                for source in status.sources:
                    sources.append(
                        {
                            "title": getattr(source, "title", ""),
                            "url": getattr(source, "url", ""),
                            "snippet": getattr(source, "snippet", ""),
                        }
                    )
                    if hasattr(source, "url"):
                        citations.append(source.url)

            return {
                "content": content,
                "sources": sources,
                "citations": citations,
            }

        except Exception as e:
            logger.warning(f"Error parsing result: {e}")
            return {"content": str(status), "sources": [], "citations": []}
