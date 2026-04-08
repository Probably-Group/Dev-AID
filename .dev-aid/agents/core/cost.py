"""
Cost estimation for LLM API calls.

Provides approximate per-token pricing for common models.
Prices are approximate and should be updated as providers change pricing.
"""

from typing import Any, Dict

# Costs per million tokens (USD) — approximate as of early 2026
MODEL_COSTS: Dict[str, Dict[str, float]] = {
    # Anthropic
    "claude-sonnet-4-5-20250929": {"input": 3.0, "output": 15.0},
    "claude-opus-4-6": {"input": 15.0, "output": 75.0},
    "claude-haiku-4-5-20251001": {"input": 0.8, "output": 4.0},
    # OpenAI
    "gpt-4o": {"input": 2.5, "output": 10.0},
    "gpt-4o-mini": {"input": 0.15, "output": 0.6},
    "gpt-4.1": {"input": 2.0, "output": 8.0},
    "gpt-4.1-mini": {"input": 0.4, "output": 1.6},
    # Google
    "gemini-2.0-flash": {"input": 0.1, "output": 0.4},
    "gemini-2.5-pro": {"input": 1.25, "output": 10.0},
    "gemini-2.5-flash": {"input": 0.15, "output": 0.6},
}


def estimate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
    custom_costs: Dict[str, Dict[str, float]] = {},  # noqa: B006
) -> float:
    """
    Estimate API call cost in USD.

    Args:
        model: Model identifier string
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        custom_costs: Optional override pricing table

    Returns:
        Estimated cost in USD, or 0.0 if model pricing unknown
    """
    lookup: Dict[str, Dict[str, float]] = {**MODEL_COSTS, **custom_costs}
    costs = lookup.get(model)

    if not costs:
        # Try prefix matching for versioned model names
        for model_name, c in lookup.items():
            if model.startswith(model_name) or model_name.startswith(model):
                costs = c
                break

    if not costs:
        return 0.0

    return (
        input_tokens * costs.get("input", 0) + output_tokens * costs.get("output", 0)
    ) / 1_000_000


def get_known_models() -> Dict[str, Dict[str, Any]]:
    """Return all known models with their pricing."""
    return dict(MODEL_COSTS)
