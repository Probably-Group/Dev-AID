## 3. Implementation Workflow (TDD)

### Step 1: Write Failing Test First

```python
# tests/test_cloud_api.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.cloud_api import SecureClaudeClient, CloudAPIConfig

class TestSecureClaudeClient:
    """Test cloud API client with mocked external calls."""

    @pytest.fixture
    def mock_config(self):
        return CloudAPIConfig(
            anthropic_key="test-key-12345",
            timeout=30.0
        )

    @pytest.fixture
    def mock_anthropic_response(self):
        """Mock Anthropic API response."""
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Test response")]
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 20
        return mock_response

    @pytest.mark.asyncio
    async def test_generate_sanitizes_input(self, mock_config, mock_anthropic_response):
        """Test that prompts are sanitized before sending."""
        with patch('anthropic.Anthropic') as mock_client:
            mock_client.return_value.messages.create.return_value = mock_anthropic_response

            client = SecureClaudeClient(mock_config)
            result = await client.generate("Test <script>alert('xss')</script>")

            # Verify sanitization was applied
            call_args = mock_client.return_value.messages.create.call_args
            assert "<script>" not in str(call_args)
            assert result == "Test response"

    @pytest.mark.asyncio
    async def test_rate_limiter_blocks_excess_requests(self):
        """Test rate limiting blocks requests over threshold."""
        from src.cloud_api import RateLimiter

        limiter = RateLimiter(rpm=2, daily_cost=100)

        await limiter.acquire(100)
        await limiter.acquire(100)

        with pytest.raises(Exception):  # RateLimitError
            await limiter.acquire(100)

    @pytest.mark.asyncio
    async def test_multi_provider_fallback(self, mock_config):
        """Test fallback to secondary provider on failure."""
        from src.cloud_api import MultiProviderClient

        with patch('src.cloud_api.SecureClaudeClient') as mock_claude:
            with patch('src.cloud_api.SecureOpenAIClient') as mock_openai:
                mock_claude.return_value.generate = AsyncMock(
                    side_effect=Exception("Rate limited")
                )
                mock_openai.return_value.generate = AsyncMock(
                    return_value="OpenAI response"
                )

                client = MultiProviderClient(mock_config)
                result = await client.generate("test prompt")

                assert result == "OpenAI response"
                mock_openai.return_value.generate.assert_called_once()
```

### Step 2: Implement Minimum to Pass

```python
# src/cloud_api.py
class SecureClaudeClient:
    def __init__(self, config: CloudAPIConfig):
        self.client = Anthropic(api_key=config.anthropic_key.get_secret_value())
        self.sanitizer = PromptSanitizer()

    async def generate(self, prompt: str) -> str:
        sanitized = self.sanitizer.sanitize(prompt)
        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            messages=[{"role": "user", "content": sanitized}]
        )
        return self._filter_output(response.content[0].text)
```

### Step 3: Refactor with Patterns

Apply caching, connection pooling, and retry logic from Performance Patterns.

### Step 4: Run Full Verification

```bash
# Run all tests with coverage
pytest tests/test_cloud_api.py -v --cov=src.cloud_api --cov-report=term-missing

# Run security checks
bandit -r src/cloud_api.py

# Type checking
mypy src/cloud_api.py --strict
```

---


