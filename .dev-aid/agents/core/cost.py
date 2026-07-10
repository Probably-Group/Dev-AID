"""
Cost estimation for LLM API calls.

Provides approximate per-token pricing for common models.

NOTE: The router subsystem keeps the canonical model registry (including
per-model pricing) in ``.dev-aid/config/models.json``. This table is the
agents-subsystem mirror; when provider pricing changes, update both. Prices
verified against provider pricing pages (2026-07).
"""

import logging
from typing import Any, Dict, Set

logger = logging.getLogger(__name__)

# Costs per million tokens (USD). Verified 2026-07 against Anthropic pricing.
MODEL_COSTS: Dict[str, Dict[str, float]] = {
    # Anthropic — current generation (match models.json ids)
    "claude-sonnet-4-6": {"input": 3.0, "output": 15.0},
    "claude-opus-4-6": {"input": 5.0, "output": 25.0},
    "claude-haiku-4-5": {"input": 1.0, "output": 5.0},
    # Anthropic — dated ids still used as agents-subsystem defaults
    "claude-sonnet-4-5-20250929": {"input": 3.0, "output": 15.0},
    "claude-haiku-4-5-20251001": {"input": 1.0, "output": 5.0},
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

# Conservative fallback for unknown models: the most expensive current entry,
# so budget enforcement over-counts rather than silently under-counting an
# unpriced model to $0.00 (audit finding H7).
_UNKNOWN_MODEL_COST: Dict[str, float] = {"input": 5.0, "output": 25.0}

# Track models we've already warned about, to avoid per-call log spam.
_warned_unknown_models: Set[str] = set()


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
        Estimated cost in USD. Unknown models fall back to a conservative
        (most-expensive-known) rate and log a warning, so budget limits are
        never bypassed by an unpriced model.
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
        if model not in _warned_unknown_models:
            _warned_unknown_models.add(model)
            logger.warning(
                "No pricing for model '%s'; using conservative fallback "
                "($%.2f/$%.2f per 1M tokens) so budget limits still apply. "
                "Add it to MODEL_COSTS / models.json.",
                model,
                _UNKNOWN_MODEL_COST["input"],
                _UNKNOWN_MODEL_COST["output"],
            )
        costs = _UNKNOWN_MODEL_COST

    return (
        input_tokens * costs.get("input", 0) + output_tokens * costs.get("output", 0)
    ) / 1_000_000


def get_known_models() -> Dict[str, Dict[str, Any]]:
    """Return all known models with their pricing."""
    return dict(MODEL_COSTS)
