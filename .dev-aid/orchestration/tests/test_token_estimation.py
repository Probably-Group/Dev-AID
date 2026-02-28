"""Tests for shared token_estimation module"""

from router.constants import CHARS_PER_TOKEN
from router.token_estimation import estimate_tokens


class TestEstimateTokens:
    """Tests for estimate_tokens"""

    def test_empty_string(self):
        """Test empty string returns 0"""
        assert estimate_tokens("") == 0

    def test_single_word(self):
        """Test single word"""
        result = estimate_tokens("hello")
        assert result == int(len("hello") / CHARS_PER_TOKEN)

    def test_multiple_words(self):
        """Test multiple words"""
        text = "hello world this is a test"
        result = estimate_tokens(text)
        assert result == int(len(text) / CHARS_PER_TOKEN)

    def test_long_text(self):
        """Test longer text"""
        text = " ".join(["word"] * 1000)
        result = estimate_tokens(text)
        assert result == int(len(text) / CHARS_PER_TOKEN)

    def test_returns_int(self):
        """Test return type is always int"""
        result = estimate_tokens("hello world")
        assert isinstance(result, int)

    def test_unicode_text(self):
        """Test with unicode characters"""
        text = "hello 世界 こんにちは мир"
        result = estimate_tokens(text)
        assert result == int(len(text) / CHARS_PER_TOKEN)

    def test_code_text(self):
        """Test with code-like text"""
        text = "def hello_world(): return 42"
        result = estimate_tokens(text)
        assert result > 0

    def test_factor_value(self):
        """Test that the char-per-token constant is the expected value"""
        assert CHARS_PER_TOKEN == 4

    def test_whitespace_only(self):
        """Test whitespace-only string"""
        result = estimate_tokens("   ")
        assert result == int(len("   ") / CHARS_PER_TOKEN)

    def test_newline_only(self):
        """Test newline-only string"""
        result = estimate_tokens("\n\n\n")
        assert result == int(len("\n\n\n") / CHARS_PER_TOKEN)
