"""Shared constants for Dev-AID Router.

Centralizes magic numbers and configuration defaults used across modules.
"""

from typing import Dict

# Token estimation factor: ~1.3 words per token for English text and code
TOKEN_ESTIMATION_FACTOR = 1.3

# Character-based token estimation: ~4 characters per token (standard approximation)
CHARS_PER_TOKEN = 4

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

# MCP query cache TTL (seconds)
MCP_CACHE_TTL = 300.0

# Codebase size thresholds for adaptive search depth
CODEBASE_SIZE_SMALL_MAX_FILES = 100
CODEBASE_SIZE_SMALL_MAX_CHUNKS = 500
CODEBASE_SIZE_MEDIUM_MAX_FILES = 500
CODEBASE_SIZE_MEDIUM_MAX_CHUNKS = 2000
CODEBASE_SEARCH_TOP_K: Dict[str, int] = {"small": 5, "medium": 10, "large": 15}

# Codebase size detection cache TTL (seconds) — longer since index rarely changes
CODEBASE_SIZE_CACHE_TTL = 600.0
