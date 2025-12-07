"""Tests for orchestration modes"""

from unittest.mock import Mock, patch

import pytest

from router.modes.challenger import ChallengerMode
from router.modes.ensemble import EnsembleMode
from router.modes.solo import SoloMode


class TestSoloMode:
    """Test SoloMode"""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration"""
        config = Mock()
        config.get_api_key = Mock(return_value="test-key")
        config.get_model_config = Mock(
            return_value={
                "model_id": "claude-sonnet-4",
                "provider": "anthropic",
                "max_tokens": 4096,
                "cost_per_1m_tokens": {"input": 3.0, "output": 15.0},
            }
        )
        return config

    @pytest.fixture
    def mock_context_builder(self):
        """Mock context builder"""
        builder = Mock()
        builder.build_context = Mock(
            return_value=Mock(
                memory_bank={},
                project_info={"name": "test"},
                git_context=None,
                active_skills=None,
                mcp_context={},
            )
        )
        builder.format_context_for_ai = Mock(return_value="Formatted context")
        return builder

    @pytest.fixture
    def solo_mode(self, mock_config, mock_context_builder):
        """Create SoloMode instance"""
        return SoloMode(mock_config, mock_context_builder)

    def test_execute_success(self, solo_mode):
        """Test successful execution"""
        with patch("router.modes.solo.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request = Mock(
                return_value=Mock(
                    content="Response text",
                    model="claude-sonnet-4",
                    provider="anthropic",
                    tokens_used={"input": 100, "output": 50},
                    cost=0.0225,
                )
            )
            mock_create.return_value = mock_client

            result = solo_mode.execute("Test request")

            assert result["success"] is True
            assert result["mode"] == "solo"
            assert result["response"] == "Response text"
            assert result["cost"] == 0.0225
            assert result["provider"] == "anthropic"

    def test_execute_with_context_size(self, solo_mode, mock_context_builder):
        """Test execution with context size parameter"""
        with patch("router.modes.solo.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request = Mock(
                return_value=Mock(
                    content="Response",
                    model="claude-sonnet-4",
                    provider="anthropic",
                    tokens_used={"input": 100, "output": 50},
                    cost=0.01,
                )
            )
            mock_create.return_value = mock_client

            result = solo_mode.execute("Test request", context_size=50000)

            assert result["success"] is True
            # Should still build context even with large context size
            mock_context_builder.build_context.assert_called()


class TestEnsembleMode:
    """Test EnsembleMode"""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration"""
        config = Mock()
        config.get_api_key = Mock(return_value="test-key")
        config.get_enabled_providers = Mock(return_value=["anthropic", "google"])
        config.get_model_config = Mock(
            return_value={
                "model_id": "claude-sonnet-4",
                "provider": "anthropic",
                "max_tokens": 4096,
                "cost_per_1m_tokens": {"input": 3.0, "output": 15.0},
            }
        )
        config.get_fallback_chain = Mock(
            return_value=[
                {
                    "provider": "anthropic",
                    "model_id": "claude-sonnet-4",
                    "max_tokens": 4096,
                    "cost_per_1m_tokens": {"input": 3.0, "output": 15.0},
                }
            ]
        )
        return config

    @pytest.fixture
    def mock_context_builder(self):
        """Mock context builder"""
        builder = Mock()
        builder.build_context = Mock(
            return_value=Mock(
                memory_bank={},
                project_info={"name": "test"},
                git_context=None,
                active_skills=None,
                mcp_context={},
            )
        )
        builder.format_context_for_ai = Mock(return_value="Formatted context")
        return builder

    @pytest.fixture
    def ensemble_mode(self, mock_config, mock_context_builder):
        """Create EnsembleMode instance"""
        return EnsembleMode(mock_config, mock_context_builder)

    def test_execute_with_multiple_providers(self, ensemble_mode):
        """Test execution with multiple providers"""
        with patch("router.modes.ensemble.create_client") as mock_create:
            # Mock multiple successful responses
            mock_client1 = Mock()
            mock_client1.send_request = Mock(
                return_value=Mock(
                    content="Response from Anthropic",
                    model="claude-sonnet-4",
                    provider="anthropic",
                    tokens_used={"input": 100, "output": 50},
                    cost=0.02,
                )
            )

            mock_client2 = Mock()
            mock_client2.send_request = Mock(
                return_value=Mock(
                    content="Response from Google",
                    model="gemini-pro",
                    provider="google",
                    tokens_used={"input": 100, "output": 50},
                    cost=0.01,
                )
            )

            mock_create.side_effect = [mock_client1, mock_client2]

            result = ensemble_mode.execute("Test request")

            assert result["success"] is True
            assert result["mode"] == "ensemble"
            # Should aggregate responses
            assert "responses" in result or "response" in result


class TestChallengerMode:
    """Test ChallengerMode"""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration"""
        config = Mock()
        config.get_api_key = Mock(return_value="test-key")
        config.get_model_config = Mock(
            return_value={
                "model_id": "claude-sonnet-4",
                "provider": "anthropic",
                "max_tokens": 4096,
                "cost_per_1m_tokens": {"input": 3.0, "output": 15.0},
            }
        )
        config.get_fallback_chain = Mock(
            return_value=[
                {
                    "provider": "anthropic",
                    "model_id": "claude-sonnet-4",
                    "max_tokens": 4096,
                    "cost_per_1m_tokens": {"input": 3.0, "output": 15.0},
                },
                {
                    "provider": "google",
                    "model_id": "gemini-pro",
                    "max_tokens": 4096,
                    "cost_per_1m_tokens": {"input": 1.0, "output": 3.0},
                },
            ]
        )
        return config

    @pytest.fixture
    def mock_context_builder(self):
        """Mock context builder"""
        builder = Mock()
        builder.build_context = Mock(
            return_value=Mock(
                memory_bank={},
                project_info={"name": "test"},
                git_context=None,
                active_skills=None,
                mcp_context={},
            )
        )
        builder.format_context_for_ai = Mock(return_value="Formatted context")
        return builder

    @pytest.fixture
    def challenger_mode(self, mock_config, mock_context_builder):
        """Create ChallengerMode instance"""
        return ChallengerMode(mock_config, mock_context_builder)

    def test_execute_primary_success(self, challenger_mode):
        """Test execution when primary provider succeeds"""
        with patch("router.modes.challenger.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request = Mock(
                return_value=Mock(
                    content="Primary response",
                    model="claude-sonnet-4",
                    provider="anthropic",
                    tokens_used={"input": 100, "output": 50},
                    cost=0.02,
                )
            )
            mock_create.return_value = mock_client

            result = challenger_mode.execute("Test request")

            assert result["success"] is True
            assert result["mode"] == "challenger"
            assert "primary_provider" in result or "provider" in result

    def test_execute_fallback_on_failure(self, challenger_mode, mock_config):
        """Test fallback when primary fails"""
        with patch("router.modes.challenger.create_client") as mock_create:
            # Primary fails
            mock_client1 = Mock()
            mock_client1.send_request = Mock(side_effect=Exception("API error"))

            # Fallback succeeds
            mock_client2 = Mock()
            mock_client2.send_request = Mock(
                return_value=Mock(
                    content="Fallback response",
                    model="gemini-pro",
                    provider="google",
                    tokens_used={"input": 100, "output": 50},
                    cost=0.01,
                )
            )

            mock_create.side_effect = [mock_client1, mock_client2]

            result = challenger_mode.execute("Test request")

            # Should succeed using fallback
            assert result.get("success") is True or "response" in result
