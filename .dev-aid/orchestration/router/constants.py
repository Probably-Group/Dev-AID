"""Shared constants for Dev-AID Router.

Centralizes magic numbers and configuration defaults used across modules.
"""

from typing import Dict

# Token estimation factor: ~1.3 words per token for English text and code
TOKEN_ESTIMATION_FACTOR = 1.3

# Default timeout for MCP server communication (seconds)
MCP_DEFAULT_TIMEOUT = 30.0

# Context size threshold for massive_context task classification (tokens)
CONTEXT_THRESHOLD = 100_000

# Default token budget for memory bank standing context
DEFAULT_STANDING_CONTEXT_TOKENS = 1000

# Multipliers for memory bank budget modes
MEMORY_BANK_BUDGET_MULTIPLIERS: Dict[str, float] = {
    "minimal": 0.5,
    "balanced": 1.0,
    "generous": 2.0,
}
