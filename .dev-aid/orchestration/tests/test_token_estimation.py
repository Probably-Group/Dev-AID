"""Tests for shared token_estimation module"""

from router.token_estimation import TOKEN_ESTIMATION_FACTOR, estimate_tokens


class TestEstimateTokens:
    """Tests for estimate_tokens"""

    def test_empty_string(self):
        """Test empty string returns 0"""
        assert estimate_tokens("") == 0

    def test_single_word(self):
        """Test single word"""
        result = estimate_tokens("hello")
        assert result == int(1 * TOKEN_ESTIMATION_FACTOR)

    def test_multiple_words(self):
        """Test multiple words"""
        text = "hello world this is a test"
        result = estimate_tokens(text)
        assert result == int(6 * TOKEN_ESTIMATION_FACTOR)

    def test_long_text(self):
        """Test longer text"""
        text = " ".join(["word"] * 1000)
        result = estimate_tokens(text)
        assert result == int(1000 * TOKEN_ESTIMATION_FACTOR)

    def test_returns_int(self):
        """Test return type is always int"""
        result = estimate_tokens("hello world")
        assert isinstance(result, int)

    def test_unicode_text(self):
        """Test with unicode characters"""
        text = "hello 世界 こんにちは мир"
        result = estimate_tokens(text)
        assert result == int(4 * TOKEN_ESTIMATION_FACTOR)

    def test_code_text(self):
        """Test with code-like text"""
        text = "def hello_world(): return 42"
        result = estimate_tokens(text)
        assert result > 0

    def test_factor_value(self):
        """Test that the factor is the expected value"""
        assert TOKEN_ESTIMATION_FACTOR == 1.3
