"""Shared token estimation utilities for Dev-AID Router"""

from .constants import CHARS_PER_TOKEN, TOKEN_ESTIMATION_FACTOR  # noqa: F401


def estimate_tokens(text: str) -> int:
    """
    Estimate token count from text using character-based heuristic.

    Uses ~4 characters per token, which is more accurate than word-based
    estimation across languages and code.

    Args:
        text: Text to estimate tokens for

    Returns:
        Estimated token count (always >= 0)
    """
    if not text:
        return 0
    return int(len(text) / CHARS_PER_TOKEN)
