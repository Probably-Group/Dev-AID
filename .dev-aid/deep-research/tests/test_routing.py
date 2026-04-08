"""Tests for smart router."""

import pytest
from providers.base import ResearchDepth
from providers.perplexity import PerplexityProvider
from providers.tavily import TavilyProvider
from routing.smart_router import QueryComplexity, SmartRouter


class TestQueryClassification:
    """Tests for query complexity classification."""

    @pytest.fixture
    def router(self):
        """Create router with mock providers."""
        tavily = TavilyProvider(api_key="test-key")
        perplexity = PerplexityProvider(api_key="test-key")
        return SmartRouter([tavily, perplexity])

    def test_simple_query_detection(self, router):
        """Test simple queries are classified correctly."""
        simple_queries = [
            "What is Python?",
            "How to install Node.js",
            "Python list syntax",
            "Error: module not found",
            "Latest version of React",
        ]

        for query in simple_queries:
            complexity = router.classify_query(query)
            assert complexity == QueryComplexity.SIMPLE, f"Failed for: {query}"

    def test_complex_query_detection(self, router):
        """Test complex queries are classified correctly."""
        complex_queries = [
            "Compare React vs Vue for enterprise applications with pros and cons",
            "Comprehensive analysis of microservices architecture patterns",
            "In-depth evaluation of database alternatives for high-traffic apps",
            "Research best practices for Kubernetes security in production",
        ]

        for query in complex_queries:
            complexity = router.classify_query(query)
            assert complexity == QueryComplexity.COMPLEX, f"Failed for: {query}"

    def test_moderate_query_detection(self, router):
        """Test moderate queries are classified correctly."""
        moderate_queries = [
            "How should I structure my React project?",
            "Redis vs Memcached for session storage",
            "Best way to handle authentication in FastAPI",
        ]

        for query in moderate_queries:
            complexity = router.classify_query(query)
            assert complexity in [
                QueryComplexity.MODERATE,
                QueryComplexity.COMPLEX,
            ], f"Failed for: {query}"


class TestRouting:
    """Tests for routing decisions."""

    @pytest.fixture
    def router(self):
        """Create router with mock providers."""
        tavily = TavilyProvider(api_key="test-key")
        perplexity = PerplexityProvider(api_key="test-key")
        return SmartRouter([tavily, perplexity])

    def test_simple_query_routes_to_tavily(self, router):
        """Test simple queries route to Tavily."""
        decision = router.route("What is Python?")

        assert decision.provider == "tavily"
        assert decision.depth == ResearchDepth.QUICK

    def test_complex_query_routes_to_deep_provider(self, router):
        """Test complex queries route to deep research provider."""
        decision = router.route(
            "Comprehensive analysis of microservices vs monolith architecture"
        )

        assert decision.depth == ResearchDepth.DEEP
        # Should route to perplexity since gemini not available
        assert decision.provider == "perplexity-sonar"

    def test_prefer_speed_overrides_complexity(self, router):
        """Test prefer_speed flag routes to faster provider."""
        decision = router.route(
            "Compare all JavaScript frameworks comprehensively",
            prefer_speed=True,
        )

        assert decision.depth == ResearchDepth.QUICK
        assert decision.provider == "tavily"

    def test_force_provider(self, router):
        """Test forcing specific provider."""
        decision = router.route(
            "What is Python?",
            force_provider="perplexity-sonar",
        )

        assert decision.provider == "perplexity-sonar"

    def test_force_depth(self, router):
        """Test forcing specific depth."""
        decision = router.route(
            "What is Python?",
            force_depth=ResearchDepth.STANDARD,
        )

        assert decision.depth == ResearchDepth.STANDARD

    def test_routing_decision_has_reasoning(self, router):
        """Test routing decision includes reasoning."""
        decision = router.route("What is Python?")

        assert decision.reasoning is not None
        assert len(decision.reasoning) > 0

    def test_routing_decision_has_estimated_time(self, router):
        """Test routing decision includes time estimate."""
        decision = router.route("What is Python?")

        assert decision.estimated_time_seconds > 0

    def test_get_available_providers(self, router):
        """Test getting list of available providers."""
        providers = router.get_available_providers()

        assert "tavily" in providers
        assert "perplexity-sonar" in providers
