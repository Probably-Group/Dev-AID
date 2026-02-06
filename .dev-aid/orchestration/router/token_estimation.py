"""Shared token estimation utilities for Dev-AID Router"""

# Consistent factor for estimating tokens from word count.
# ~1.3 words per token is a reasonable average for English text and code.
TOKEN_ESTIMATION_FACTOR = 1.3


def estimate_tokens(text: str) -> int:
    """
    Estimate token count from text using word-based heuristic.

    Args:
        text: Text to estimate tokens for

    Returns:
        Estimated token count (always >= 0)
    """
    if not text:
        return 0
    return int(len(text.split()) * TOKEN_ESTIMATION_FACTOR)
