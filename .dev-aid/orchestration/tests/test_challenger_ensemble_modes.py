"""Tests for ChallengerMode and EnsembleMode"""

from unittest.mock import Mock, patch

import pytest

from router.api_clients import APIResponse
from router.modes.challenger import ChallengerMode
from router.modes.ensemble import EnsembleMode

# ── Shared Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def mock_config():
    """Mock ModeConfigProtocol"""
    config = Mock()
    config.get_default_model = Mock(return_value="claude-sonnet")
    config.validate_provider = Mock(return_value=(True, ""))
    config.get_model_config = Mock(
        return_value={
            "id": "claude-sonnet-4",
            "provider": "anthropic",
            "max_tokens": 4096,
            "cost_per_1m_tokens": {"input": 3.0, "output": 15.0},
        }
    )
    config.get_routing_config = Mock(
        return_value={
            "modes": {
                "challenger": {
                    "enabled": True,
                    "primary_model": "claude-sonnet",
                    "challenger_model": "gemini-flash",
                    "review_triggers": ["security", "auth", "database"],
                    "auto_refine_on": ["HIGH", "CRITICAL"],
                },
                "ensemble": {
                    "enabled": True,
                    "routing_strategy": "semantic",
                    "task_routes": {},
                },
            },
            "fallback_chain": ["claude-sonnet"],
        }
    )
    config.get_auth_credentials = Mock(
        return_value=Mock(
            provider="anthropic",
            auth_type="api_key",
            credentials={"api_key": "test-key"},
        )
    )
    config.get_fallback_chain = Mock(return_value=["claude-sonnet", "gemini-flash"])
    config.models = {
        "anthropic": {
            "models": {
                "sonnet": {
                    "id": "claude-sonnet-4",
                    "cost_per_1m_tokens": {"input": 3.0, "output": 15.0},
                }
            }
        }
    }
    return config


@pytest.fixture
def mock_context_builder():
    """Mock ContextBuilder"""
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
    builder.format_context_for_ai = Mock(return_value="Context")
    return builder


def _make_api_response(content="Response", cost=0.01, latency=100):
    return APIResponse(
        content=content,
        model="claude-sonnet-4",
        provider="anthropic",
        tokens_used={"input": 100, "output": 50},
        cost=cost,
        latency_ms=latency,
    )


# ── ChallengerMode Tests ────────────────────────────────────────────────────


class TestChallengerShouldChallenge:
    """Test _should_challenge logic"""

    def test_trigger_match(self, mock_config, mock_context_builder):
        mode = ChallengerMode(mock_config, mock_context_builder)
        assert (
            mode._should_challenge(
                "Fix the security vulnerability", {"review_triggers": ["security"]}
            )
            is True
        )

    def test_trigger_no_match(self, mock_config, mock_context_builder):
        mode = ChallengerMode(mock_config, mock_context_builder)
        assert mode._should_challenge("Fix the typo", {"review_triggers": ["security"]}) is False

    def test_trigger_case_insensitive(self, mock_config, mock_context_builder):
        mode = ChallengerMode(mock_config, mock_context_builder)
        assert mode._should_challenge("SECURITY issue", {"review_triggers": ["security"]}) is True

    def test_no_triggers(self, mock_config, mock_context_builder):
        mode = ChallengerMode(mock_config, mock_context_builder)
        assert mode._should_challenge("anything", {"review_triggers": []}) is False


class TestChallengerParseReview:
    """Test _parse_review_for_issues"""

    def test_no_issues_none_severity(self, mock_config, mock_context_builder):
        mode = ChallengerMode(mock_config, mock_context_builder)
        assert mode._parse_review_for_issues("**SEVERITY**: NONE\nLooks good!") is False

    def test_no_issues_looks_good(self, mock_config, mock_context_builder):
        mode = ChallengerMode(mock_config, mock_context_builder)
        assert mode._parse_review_for_issues("Implementation looks good!") is False

    def test_has_issues_high(self, mock_config, mock_context_builder):
        mode = ChallengerMode(mock_config, mock_context_builder)
        assert mode._parse_review_for_issues("**SEVERITY: HIGH**\nSQL injection found") is True

    def test_has_issues_critical(self, mock_config, mock_context_builder):
        mode = ChallengerMode(mock_config, mock_context_builder)
        assert mode._parse_review_for_issues("SEVERITY: CRITICAL\nRCE vulnerability") is True

    def test_has_issues_medium(self, mock_config, mock_context_builder):
        mode = ChallengerMode(mock_config, mock_context_builder)
        assert mode._parse_review_for_issues("SEVERITY: MEDIUM\nMissing input validation") is True

    def test_substantial_review_assumes_issues(self, mock_config, mock_context_builder):
        mode = ChallengerMode(mock_config, mock_context_builder)
        review = "x" * 150  # Long review without explicit markers
        assert mode._parse_review_for_issues(review) is True

    def test_short_review_no_markers(self, mock_config, mock_context_builder):
        mode = ChallengerMode(mock_config, mock_context_builder)
        assert mode._parse_review_for_issues("OK") is False


class TestChallengerExecute:
    """Test ChallengerMode.execute"""

    def test_execute_no_challenge(self, mock_config, mock_context_builder):
        mode = ChallengerMode(mock_config, mock_context_builder)

        with patch("router.modes.challenger.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.return_value = _make_api_response("Primary response")
            mock_create.return_value = mock_client

            result = mode.execute("Fix typo in readme")

            assert result["success"] is True
            assert result["challenged"] is False
            assert result["response"] == "Primary response"

    def test_execute_force_challenge(self, mock_config, mock_context_builder):
        mode = ChallengerMode(mock_config, mock_context_builder)

        with patch("router.modes.challenger.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.side_effect = [
                _make_api_response("Primary response"),
                _make_api_response("SEVERITY: NONE\nLooks good!", cost=0.005, latency=50),
            ]
            mock_create.return_value = mock_client

            result = mode.execute("Fix typo", force_challenge=True)

            assert result["success"] is True
            assert result["challenged"] is True
            assert result["issues_found"] is False

    def test_execute_challenge_with_issues_no_refine(self, mock_config, mock_context_builder):
        """Challenge finds LOW severity issues - no auto-refine"""
        mode = ChallengerMode(mock_config, mock_context_builder)

        with patch("router.modes.challenger.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.side_effect = [
                _make_api_response("Primary response"),
                _make_api_response("SEVERITY: LOW\nMinor style issue", cost=0.005, latency=50),
            ]
            mock_create.return_value = mock_client

            result = mode.execute("security review needed", force_challenge=True)

            assert result["success"] is True
            assert result["challenged"] is True
            assert result["issues_found"] is True
            assert result["refined"] is False
            assert result["final_response"] == "Primary response"

    def test_execute_challenge_with_auto_refine(self, mock_config, mock_context_builder):
        """Challenge finds HIGH severity - triggers auto-refine"""
        mode = ChallengerMode(mock_config, mock_context_builder)

        with patch("router.modes.challenger.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.side_effect = [
                _make_api_response("Primary response"),
                _make_api_response("SEVERITY: HIGH\nSQL injection found", cost=0.005, latency=50),
                _make_api_response("Refined response", cost=0.01, latency=80),
            ]
            mock_create.return_value = mock_client

            result = mode.execute("security review", force_challenge=True)

            assert result["success"] is True
            assert result["refined"] is True
            assert result["final_response"] == "Refined response"
            assert result["cost"] > 0.01  # Combined cost

    def test_execute_challenger_fails(self, mock_config, mock_context_builder):
        """Challenger model fails - return primary response"""
        mode = ChallengerMode(mock_config, mock_context_builder)

        with patch("router.modes.challenger.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.side_effect = [
                _make_api_response("Primary response"),
                RuntimeError("Challenger API error"),
            ]
            mock_create.return_value = mock_client

            result = mode.execute("security test", force_challenge=True)

            assert result["success"] is True
            assert result["challenged"] is True
            assert result["challenger_failed"] is True

    def test_execute_primary_fails(self, mock_config, mock_context_builder):
        """Primary model fails"""
        mode = ChallengerMode(mock_config, mock_context_builder)

        with patch("router.modes.challenger.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.side_effect = RuntimeError("API error")
            mock_create.return_value = mock_client

            result = mode.execute("security test", force_challenge=True)

            assert result["success"] is False

    def test_execute_no_auth(self, mock_config, mock_context_builder):
        """No auth credentials available"""
        mock_config.get_auth_credentials = Mock(return_value=None)
        mode = ChallengerMode(mock_config, mock_context_builder)

        result = mode.execute("test request")

        assert result["success"] is False
        assert "authentication" in result["error"].lower()

    def test_execute_provider_invalid(self, mock_config, mock_context_builder):
        """Provider validation fails"""
        mock_config.validate_provider = Mock(return_value=(False, "Provider disabled"))
        mode = ChallengerMode(mock_config, mock_context_builder)

        with pytest.raises(RuntimeError, match="Provider disabled"):
            mode.execute("test request")

    def test_execute_model_not_found(self, mock_config, mock_context_builder):
        """Model config not found for primary - uses default model as fallback"""
        default_config = {
            "id": "claude-sonnet-4",
            "provider": "anthropic",
            "cost_per_1m_tokens": {"input": 3.0, "output": 15.0},
        }

        def model_side_effect(name):
            if name == "claude-sonnet":
                return None
            return default_config

        mock_config.get_model_config = Mock(side_effect=model_side_effect)
        mock_config.get_default_model = Mock(return_value="claude-sonnet-fallback")
        mode = ChallengerMode(mock_config, mock_context_builder)

        with patch("router.modes.challenger.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.return_value = _make_api_response()
            mock_create.return_value = mock_client

            result = mode.execute("test")
            assert result["success"] is True


class TestChallengerGetInfo:
    """Test ChallengerMode.get_info"""

    def test_get_info(self, mock_config, mock_context_builder):
        mode = ChallengerMode(mock_config, mock_context_builder)
        info = mode.get_info()
        assert info["mode"] == "challenger"
        assert "primary_model" in info
        assert "challenger_model" in info
        assert "review_triggers" in info


class TestChallengerBuildReviewPrompt:
    """Test _build_review_prompt"""

    def test_build_review_prompt(self, mock_config, mock_context_builder):
        mode = ChallengerMode(mock_config, mock_context_builder)
        prompt = mode._build_review_prompt("Add auth", "def login(): pass")
        assert "Add auth" in prompt
        assert "def login(): pass" in prompt
        assert "Security Issues" in prompt


# ── EnsembleMode Tests ───────────────────────────────────────────────────────


class TestEnsembleExecute:
    """Test EnsembleMode.execute"""

    def test_execute_success(self, mock_config, mock_context_builder):
        mode = EnsembleMode(mock_config, mock_context_builder)

        with patch("router.modes.ensemble.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.return_value = _make_api_response("Ensemble response")
            mock_create.return_value = mock_client

            result = mode.execute("Write a function to sort a list")

            assert result["success"] is True
            assert result["mode"] == "ensemble"
            assert result["response"] == "Ensemble response"
            assert "task_type" in result

    def test_execute_model_not_found_fallback(self, mock_config, mock_context_builder):
        """Model not found, falls back to default"""
        call_count = [0]
        original_get = mock_config.get_model_config

        def side_effect(name):
            call_count[0] += 1
            if call_count[0] == 1:
                return None  # First call fails
            return original_get(name)

        mock_config.get_model_config = Mock(side_effect=side_effect)
        mode = EnsembleMode(mock_config, mock_context_builder)

        with patch("router.modes.ensemble.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.return_value = _make_api_response()
            mock_create.return_value = mock_client

            result = mode.execute("test")
            assert result["success"] is True

    def test_execute_provider_invalid_uses_fallback(self, mock_config, mock_context_builder):
        """Provider invalid, uses fallback chain"""
        call_count = [0]

        def validate_side_effect(provider):
            call_count[0] += 1
            if call_count[0] <= 1:
                return (False, "Provider disabled")
            return (True, "")

        mock_config.validate_provider = Mock(side_effect=validate_side_effect)
        mode = EnsembleMode(mock_config, mock_context_builder)

        with patch("router.modes.ensemble.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.return_value = _make_api_response()
            mock_create.return_value = mock_client

            result = mode.execute("test")
            assert result["success"] is True
            assert result["used_fallback"] is True

    def test_execute_no_auth_fallback(self, mock_config, mock_context_builder):
        """No auth for primary, falls back"""
        call_count = [0]

        def auth_side_effect(provider):
            call_count[0] += 1
            if call_count[0] <= 1:
                return None
            return Mock(
                provider="anthropic",
                auth_type="api_key",
                credentials={"api_key": "key"},
            )

        mock_config.get_auth_credentials = Mock(side_effect=auth_side_effect)
        mode = EnsembleMode(mock_config, mock_context_builder)

        with patch("router.modes.ensemble.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.return_value = _make_api_response()
            mock_create.return_value = mock_client

            result = mode.execute("test")
            assert result["success"] is True

    def test_execute_no_auth_anywhere(self, mock_config, mock_context_builder):
        """No auth for any provider"""
        mock_config.get_auth_credentials = Mock(return_value=None)
        mode = EnsembleMode(mock_config, mock_context_builder)

        result = mode.execute("test")
        assert result["success"] is False
        assert "authentication" in result["error"].lower()

    def test_execute_api_error(self, mock_config, mock_context_builder):
        mode = EnsembleMode(mock_config, mock_context_builder)

        with patch("router.modes.ensemble.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.side_effect = RuntimeError("API down")
            mock_create.return_value = mock_client

            result = mode.execute("test")
            assert result["success"] is False
            assert "API down" in result["error"]

    def test_execute_with_mcp_context(self, mock_config, mock_context_builder):
        mode = EnsembleMode(mock_config, mock_context_builder)

        with patch("router.modes.ensemble.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.return_value = _make_api_response()
            mock_create.return_value = mock_client

            result = mode.execute("test", mcp_context={"tool": "data"})
            assert result["success"] is True


class TestEnsembleFallback:
    """Test _get_fallback_model"""

    def test_fallback_returns_first_valid(self, mock_config, mock_context_builder):
        mode = EnsembleMode(mock_config, mock_context_builder)
        name, config, provider = mode._get_fallback_model()
        assert name == "claude-sonnet"
        assert provider == "anthropic"

    def test_fallback_all_invalid(self, mock_config, mock_context_builder):
        """All fallback models invalid, returns default"""
        mock_config.validate_provider = Mock(return_value=(False, "disabled"))
        mock_config.get_fallback_chain = Mock(return_value=["bad-model"])
        mock_config.get_model_config = Mock(
            return_value={
                "id": "default",
                "provider": "anthropic",
                "cost_per_1m_tokens": {"input": 3.0, "output": 15.0},
            }
        )
        mode = EnsembleMode(mock_config, mock_context_builder)
        name, config, provider = mode._get_fallback_model()
        # Should fall through to default model
        assert name == "claude-sonnet"


class TestEnsembleGetInfo:
    """Test EnsembleMode.get_info"""

    def test_get_info(self, mock_config, mock_context_builder):
        mode = EnsembleMode(mock_config, mock_context_builder)
        info = mode.get_info()
        assert info["mode"] == "ensemble"
        assert "routing_strategy" in info
        assert "fallback_chain" in info


class TestEnsembleCostComparison:
    """Test estimate_cost_comparison"""

    def test_cost_comparison(self, mock_config, mock_context_builder):
        mode = EnsembleMode(mock_config, mock_context_builder)
        costs = mode.estimate_cost_comparison({"input": 1_000_000, "output": 500_000})
        assert isinstance(costs, dict)
        # Should have at least one model
        assert len(costs) >= 1

    def test_cost_comparison_handles_non_dict(self, mock_config, mock_context_builder):
        """Handles non-dict entries in models config"""
        mock_config.models = {
            "anthropic": {
                "models": {
                    "sonnet": {
                        "cost_per_1m_tokens": {"input": 3.0, "output": 15.0},
                    },
                    "bad_entry": "not a dict",
                }
            },
            "bad_provider": "not a dict",
        }
        mode = EnsembleMode(mock_config, mock_context_builder)
        costs = mode.estimate_cost_comparison({"input": 1000, "output": 500})
        assert isinstance(costs, dict)
