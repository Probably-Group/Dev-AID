"""Tests for cost estimation module."""

from agents.core.cost import estimate_cost, get_known_models


class TestEstimateCost:
    """Tests for estimate_cost function."""

    def test_known_model(self) -> None:
        cost = estimate_cost("claude-sonnet-4-5-20250929", 1000, 500)
        # 1000 * 3.0 / 1M + 500 * 15.0 / 1M = 0.003 + 0.0075 = 0.0105
        assert abs(cost - 0.0105) < 0.0001

    def test_unknown_model_uses_conservative_fallback(self) -> None:
        # Audit H7: unknown models must not silently cost $0.00 (which would
        # bypass budget limits). They fall back to a conservative rate.
        cost = estimate_cost("unknown-model-xyz", 1000, 500)
        # 1000 * 5.0 / 1M + 500 * 25.0 / 1M = 0.005 + 0.0125 = 0.0175
        assert abs(cost - 0.0175) < 0.0001
        assert cost > 0.0

    def test_opus_4_6_pricing_is_current(self) -> None:
        # Audit H7: Opus 4.6 is $5/$25 per 1M tokens, not the old $15/$75.
        cost = estimate_cost("claude-opus-4-6", 1_000_000, 1_000_000)
        assert abs(cost - 30.0) < 0.0001

    def test_zero_tokens(self) -> None:
        cost = estimate_cost("claude-sonnet-4-5-20250929", 0, 0)
        assert cost == 0.0

    def test_prefix_matching(self) -> None:
        """Models with version suffixes should match known prefixes."""
        cost = estimate_cost("gpt-4o-2024-08-06", 1000, 500)
        # Should match "gpt-4o" via prefix matching
        assert cost > 0.0

    def test_custom_costs_override(self) -> None:
        custom = {"my-model": {"input": 10.0, "output": 50.0}}
        cost = estimate_cost("my-model", 1_000_000, 0, custom_costs=custom)
        assert cost == 10.0

    def test_get_known_models(self) -> None:
        models = get_known_models()
        assert "claude-sonnet-4-5-20250929" in models
        assert "gpt-4o" in models
        assert "gemini-2.0-flash" in models
        assert "input" in models["gpt-4o"]
        assert "output" in models["gpt-4o"]
