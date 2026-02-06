"""Shared constants for Dev-AID Router.

Centralizes magic numbers and configuration defaults used across modules.
"""

# Token estimation factor: ~1.3 words per token for English text and code
TOKEN_ESTIMATION_FACTOR = 1.3

# Default timeout for MCP server communication (seconds)
MCP_DEFAULT_TIMEOUT = 30.0

# Context size threshold for massive_context task classification (tokens)
CONTEXT_THRESHOLD = 100_000
