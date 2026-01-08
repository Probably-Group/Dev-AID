"""Smart router for research queries.

Routes queries to the most appropriate provider based on:
- Query complexity (simple/moderate/complex)
- Available providers
- User preferences (speed vs depth)
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from ..providers.base import ResearchDepth, ResearchProvider

logger = logging.getLogger(__name__)


class QueryComplexity(Enum):
    """Query complexity classification."""

    SIMPLE = "simple"  # Fact lookup, definitions, syntax
    MODERATE = "moderate"  # Comparisons, how-to, implementation
    COMPLEX = "complex"  # Multi-faceted research, architecture


@dataclass
class RoutingDecision:
    """Result of routing decision."""

    provider: str
    depth: ResearchDepth
    reasoning: str
    estimated_time_seconds: int
    complexity: QueryComplexity


class SmartRouter:
    """Intelligently routes queries to appropriate providers.

    Routing logic:
    - SIMPLE queries -> Tavily basic (fast, cheap)
    - MODERATE queries -> Tavily advanced or Perplexity standard
    - COMPLEX queries -> Gemini Deep Research or Perplexity deep
    """

    # Keywords indicating deep research need
    DEEP_KEYWORDS = [
        "comprehensive",
        "in-depth",
        "research",
        "analyze",
        "compare",
        "evaluate",
        "pros and cons",
        "best practices",
        "architecture",
        "design patterns",
        "tradeoffs",
        "trade-offs",
        "alternatives",
        "state of the art",
        "deep dive",
        "thorough",
    ]

    # Keywords indicating quick search
    QUICK_KEYWORDS = [
        "what is",
        "define",
        "definition",
        "syntax",
        "error",
        "how to",
        "example",
        "latest version",
        "current version",
        "documentation",
        "api reference",
        "install",
        "quick",
    ]

    # Provider priority by depth
    PROVIDER_PRIORITY = {
        ResearchDepth.QUICK: ["tavily", "perplexity-sonar"],
        ResearchDepth.STANDARD: ["tavily", "perplexity-sonar"],
        ResearchDepth.DEEP: ["gemini-deep-research", "perplexity-sonar"],
    }

    # Estimated times in seconds
    ESTIMATED_TIMES = {
        ("tavily", ResearchDepth.QUICK): 3,
        ("tavily", ResearchDepth.STANDARD): 5,
        ("perplexity-sonar", ResearchDepth.STANDARD): 8,
        ("perplexity-sonar", ResearchDepth.DEEP): 30,
        ("gemini-deep-research", ResearchDepth.DEEP): 180,
    }

    def __init__(self, providers: List[ResearchProvider]):
        """Initialize router with available providers.

        Args:
            providers: List of initialized provider instances
        """
        self.providers: Dict[str, ResearchProvider] = {p.name: p for p in providers}
        self._available_providers = [p for p in providers if p.is_available()]

        logger.info(
            f"SmartRouter initialized with {len(self._available_providers)} "
            f"available providers: {[p.name for p in self._available_providers]}"
        )

    def classify_query(self, query: str) -> QueryComplexity:
        """Classify query complexity based on content.

        Args:
            query: The research query

        Returns:
            QueryComplexity classification
        """
        query_lower = query.lower()

        # Check for deep research indicators
        deep_score = sum(1 for kw in self.DEEP_KEYWORDS if kw in query_lower)
        quick_score = sum(1 for kw in self.QUICK_KEYWORDS if kw in query_lower)

        # Word count heuristic - longer queries tend to be more complex
        word_count = len(query.split())

        # Question complexity patterns
        has_multiple_aspects = bool(
            re.search(r"\b(and|or|vs|versus|compared to)\b", query_lower)
        )
        is_opinion_seeking = bool(
            re.search(r"\b(should|best|recommend|opinion)\b", query_lower)
        )

        # Scoring
        if deep_score >= 2 or (deep_score >= 1 and has_multiple_aspects):
            return QueryComplexity.COMPLEX
        elif word_count > 30 and is_opinion_seeking:
            return QueryComplexity.COMPLEX
        elif quick_score >= 2 or (quick_score >= 1 and word_count < 15):
            return QueryComplexity.SIMPLE
        elif has_multiple_aspects or is_opinion_seeking:
            return QueryComplexity.MODERATE
        else:
            return QueryComplexity.MODERATE

    def route(
        self,
        query: str,
        prefer_speed: bool = False,
        force_provider: Optional[str] = None,
        force_depth: Optional[ResearchDepth] = None,
    ) -> RoutingDecision:
        """Route query to best provider.

        Args:
            query: The research query
            prefer_speed: If True, prefer faster providers even for complex queries
            force_provider: Force a specific provider
            force_depth: Force a specific depth level

        Returns:
            RoutingDecision with provider, depth, and reasoning
        """
        complexity = self.classify_query(query)

        # Handle forced provider
        if force_provider:
            provider = self.providers.get(force_provider)
            if provider and provider.is_available():
                depth = force_depth or self._default_depth_for_complexity(complexity)
                if not provider.supports_depth(depth):
                    depth = provider.supported_depths[0]
                return RoutingDecision(
                    provider=force_provider,
                    depth=depth,
                    reasoning=f"Forced provider: {force_provider}",
                    estimated_time_seconds=self._estimate_time(force_provider, depth),
                    complexity=complexity,
                )

        # Handle forced depth
        if force_depth:
            return self._route_by_depth(force_depth, complexity)

        # Speed preference overrides complexity
        if prefer_speed:
            return self._route_quick(query, complexity)

        # Route based on complexity
        if complexity == QueryComplexity.SIMPLE:
            return self._route_quick(query, complexity)
        elif complexity == QueryComplexity.COMPLEX:
            return self._route_deep(query, complexity)
        else:
            return self._route_standard(query, complexity)

    def _default_depth_for_complexity(self, complexity: QueryComplexity) -> ResearchDepth:
        """Get default depth for complexity level."""
        mapping = {
            QueryComplexity.SIMPLE: ResearchDepth.QUICK,
            QueryComplexity.MODERATE: ResearchDepth.STANDARD,
            QueryComplexity.COMPLEX: ResearchDepth.DEEP,
        }
        return mapping[complexity]

    def _route_by_depth(
        self, depth: ResearchDepth, complexity: QueryComplexity
    ) -> RoutingDecision:
        """Route to first available provider supporting the depth."""
        for provider_name in self.PROVIDER_PRIORITY.get(depth, []):
            provider = self.providers.get(provider_name)
            if provider and provider.is_available() and provider.supports_depth(depth):
                return RoutingDecision(
                    provider=provider_name,
                    depth=depth,
                    reasoning=f"Forced depth {depth.value} -> {provider_name}",
                    estimated_time_seconds=self._estimate_time(provider_name, depth),
                    complexity=complexity,
                )

        # Fallback to any available provider
        for provider in self._available_providers:
            if provider.supports_depth(depth):
                return RoutingDecision(
                    provider=provider.name,
                    depth=depth,
                    reasoning=f"Fallback for depth {depth.value}",
                    estimated_time_seconds=self._estimate_time(provider.name, depth),
                    complexity=complexity,
                )

        raise ValueError(f"No provider available for depth: {depth.value}")

    def _route_quick(
        self, query: str, complexity: QueryComplexity
    ) -> RoutingDecision:
        """Route to quick search provider."""
        # Prefer Tavily for quick searches (1 credit, fast)
        if "tavily" in self.providers and self.providers["tavily"].is_available():
            return RoutingDecision(
                provider="tavily",
                depth=ResearchDepth.QUICK,
                reasoning="Quick factual query -> Tavily basic search",
                estimated_time_seconds=3,
                complexity=complexity,
            )

        # Fallback to Perplexity standard
        if (
            "perplexity-sonar" in self.providers
            and self.providers["perplexity-sonar"].is_available()
        ):
            return RoutingDecision(
                provider="perplexity-sonar",
                depth=ResearchDepth.STANDARD,
                reasoning="Quick search fallback -> Perplexity",
                estimated_time_seconds=8,
                complexity=complexity,
            )

        raise ValueError("No quick search provider available")

    def _route_standard(
        self, query: str, complexity: QueryComplexity
    ) -> RoutingDecision:
        """Route to standard search provider."""
        # Prefer Tavily advanced for cost efficiency
        if "tavily" in self.providers and self.providers["tavily"].is_available():
            return RoutingDecision(
                provider="tavily",
                depth=ResearchDepth.STANDARD,
                reasoning="Moderate complexity -> Tavily advanced search",
                estimated_time_seconds=5,
                complexity=complexity,
            )

        # Fallback to Perplexity
        if (
            "perplexity-sonar" in self.providers
            and self.providers["perplexity-sonar"].is_available()
        ):
            return RoutingDecision(
                provider="perplexity-sonar",
                depth=ResearchDepth.STANDARD,
                reasoning="Standard search -> Perplexity Sonar",
                estimated_time_seconds=8,
                complexity=complexity,
            )

        raise ValueError("No standard search provider available")

    def _route_deep(
        self, query: str, complexity: QueryComplexity
    ) -> RoutingDecision:
        """Route to deep research provider."""
        # Prefer Gemini for comprehensive research
        if (
            "gemini-deep-research" in self.providers
            and self.providers["gemini-deep-research"].is_available()
        ):
            return RoutingDecision(
                provider="gemini-deep-research",
                depth=ResearchDepth.DEEP,
                reasoning="Complex research query -> Gemini Deep Research",
                estimated_time_seconds=180,
                complexity=complexity,
            )

        # Fallback to Perplexity Sonar Deep
        if (
            "perplexity-sonar" in self.providers
            and self.providers["perplexity-sonar"].is_available()
        ):
            return RoutingDecision(
                provider="perplexity-sonar",
                depth=ResearchDepth.DEEP,
                reasoning="Deep research fallback -> Perplexity Sonar Deep",
                estimated_time_seconds=30,
                complexity=complexity,
            )

        raise ValueError("No deep research provider available")

    def _estimate_time(self, provider: str, depth: ResearchDepth) -> int:
        """Get estimated time for provider/depth combination."""
        return self.ESTIMATED_TIMES.get((provider, depth), 10)

    def get_available_providers(self) -> List[str]:
        """Get list of available provider names."""
        return [p.name for p in self._available_providers]
