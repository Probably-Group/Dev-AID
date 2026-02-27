"""
End-to-End Router Integration Tests

Tests complete routing workflows with mocked API responses.
Validates the full pipeline: config loading -> mode selection -> API call -> cost tracking.
No real API calls are made; all provider clients are mocked.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from unittest.mock import Mock, patch

import pytest

from router.api_clients import APIResponse
from router.config_loader import ConfigLoader
from router.cost_tracker import CostTracker
from router.executor import RouterExecutor


# ── Helpers ──────────────────────────────────────────────────────────────────


def create_test_config(
    tmpdir: Path,
    mode: str = "solo",
    budget: float = 100.0,
    providers: Optional[Dict[str, Any]] = None,
    fallback_chain: Optional[List[str]] = None,
) -> Path:
    """Create a complete test configuration directory tree in *tmpdir*.

    Returns the root path (i.e. ``tmpdir`` itself) so it can be fed directly
    to ``ConfigLoader`` / ``RouterExecutor``.
    """
    config_dir = tmpdir / ".dev-aid" / "config"
    logs_dir = tmpdir / ".dev-aid" / "logs"
    memory_bank_dir = tmpdir / ".dev-aid" / "memory-bank"
    config_dir.mkdir(parents=True)
    logs_dir.mkdir(parents=True)
    memory_bank_dir.mkdir(parents=True)

    settings: Dict[str, Any] = {
        "project_name": "test-e2e-router",
        "orchestration_mode": mode,
        "default_model": "claude-sonnet",
        "enabled_providers": ["claude", "gemini"],
        "memory_bank": {
            "auto_load": ["activeContext.md"],
            "on_demand": [],
            "standing_context_tokens": 500,
            "standing_context_budget": "balanced",
            "staleness_warning_days": 30,
        },
    }

    routing: Dict[str, Any] = {
        "modes": {
            "solo": {"enabled": True, "model": "claude-sonnet"},
            "ensemble": {
                "enabled": True,
                "routing_strategy": "semantic",
                "task_routes": {},
            },
            "challenger": {
                "enabled": True,
                "primary_model": "claude-sonnet",
                "challenger_model": "gemini-flash",
                "challenge_threshold": 0.5,
                "review_triggers": ["security", "auth", "database"],
                "auto_refine_on": ["HIGH", "CRITICAL"],
            },
        },
        "fallback_chain": fallback_chain or ["claude-sonnet", "gemini-flash"],
        "cost_limit_per_day": budget,
        "logging": {"level": "INFO"},
    }

    if providers is None:
        providers = {
            "claude": {
                "enabled": True,
                "api_key_env": "ANTHROPIC_API_KEY",
                "models": {
                    "claude-sonnet": {
                        "id": "claude-sonnet-4",
                        "context_window": 200000,
                        "cost_per_1m_tokens": {"input": 3.0, "output": 15.0},
                        "max_tokens": 4096,
                    },
                },
                "default": "claude-sonnet",
            },
            "gemini": {
                "enabled": True,
                "api_key_env": "GOOGLE_API_KEY",
                "models": {
                    "gemini-flash": {
                        "id": "gemini-2.0-flash",
                        "context_window": 1000000,
                        "cost_per_1m_tokens": {"input": 0.075, "output": 0.3},
                        "max_tokens": 8192,
                    },
                },
                "default": "gemini-flash",
            },
        }

    orchestration: Dict[str, Any] = {"enabled": True, "default_mode": mode}

    env_content = "ANTHROPIC_API_KEY=test-key-anthropic\nGOOGLE_API_KEY=test-key-google\n"

    (config_dir / "settings.json").write_text(json.dumps(settings, indent=2))
    (config_dir / "routing.json").write_text(json.dumps(routing, indent=2))
    (config_dir / "models.json").write_text(json.dumps(providers, indent=2))
    (config_dir / "orchestration.json").write_text(json.dumps(orchestration, indent=2))
    (config_dir / ".env").write_text(env_content)

    # Memory bank file expected by ContextBuilder
    (memory_bank_dir / "activeContext.md").write_text("# E2E Test Context\n\nRunning E2E tests.")

    return tmpdir


def make_api_response(
    content: str = "Test response",
    model: str = "claude-sonnet-4",
    provider: str = "anthropic",
    cost: float = 0.02,
    input_tokens: int = 100,
    output_tokens: int = 50,
    latency_ms: float = 1234.5,
) -> APIResponse:
    """Build a realistic ``APIResponse`` dataclass instance."""
    return APIResponse(
        content=content,
        model=model,
        provider=provider,
        tokens_used={"input": input_tokens, "output": output_tokens},
        cost=cost,
        latency_ms=latency_ms,
        metadata={"stop_reason": "end_turn"},
    )


def _clear_config_cache(config: ConfigLoader) -> None:
    """Clear the lru_cache on ``get_model_config`` so fresh lookups happen."""
    config.get_model_config.cache_clear()  # type: ignore[union-attr]


def _mock_auth_detect_all() -> Dict[str, Any]:
    """Return deterministic auth credentials for all providers.

    Avoids network I/O from ``detect_available_backend`` (which probes localhost
    ports for Ollama / LM Studio) and filesystem reads for CLI session tokens.
    """
    from router.auth_detector import AuthCredentials

    return {
        "claude": AuthCredentials(
            provider="claude",
            auth_type="api_key",
            credentials={"api_key": "test-key-anthropic"},
            source="test fixture",
        ),
        "gemini": AuthCredentials(
            provider="gemini",
            auth_type="api_key",
            credentials={"api_key": "test-key-google"},
            source="test fixture",
        ),
        "openai": None,
        "local": None,
    }


def _build_executor(root: Path) -> RouterExecutor:
    """Build a ``RouterExecutor`` with MCP disabled and deterministic auth.

    Pre-populates ``_detected_auth`` on the config loader so that
    ``AuthDetector.detect_all`` is never invoked (avoids network probes to
    localhost ports and filesystem reads for CLI sessions).
    Also sets env vars so ``validate_provider`` finds API keys.
    """
    os.environ.setdefault("ANTHROPIC_API_KEY", "test-key-anthropic")
    os.environ.setdefault("GOOGLE_API_KEY", "test-key-google")
    executor = RouterExecutor(dev_aid_root=root, use_mcp=False)
    # Inject pre-computed auth so detect_all() is skipped
    executor.config._detected_auth = _mock_auth_detect_all()
    return executor


# ── Solo Mode E2E ────────────────────────────────────────────────────────────


@pytest.mark.e2e
class TestSoloModeE2E:
    """End-to-end tests for solo routing mode."""

    def test_solo_execute_returns_response(self, tmp_path: Path) -> None:
        """Solo mode executes a request and returns a well-formed result."""
        root = create_test_config(tmp_path, mode="solo")

        with patch("router.modes.solo.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.return_value = make_api_response()
            mock_create.return_value = mock_client

            executor = _build_executor(root)
            result = executor.execute("Write a hello world function")

        assert result["success"] is True
        assert result["response"] == "Test response"
        assert result["mode"] == "solo"
        assert result["provider"] == "claude"
        assert result["cost"] == 0.02

    def test_solo_passes_request_to_client(self, tmp_path: Path) -> None:
        """The user prompt reaches the underlying API client."""
        root = create_test_config(tmp_path, mode="solo")

        with patch("router.modes.solo.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.return_value = make_api_response()
            mock_create.return_value = mock_client

            executor = _build_executor(root)
            executor.execute("Implement retry logic")

        # Verify send_request was called and messages include the user request
        mock_client.send_request.assert_called_once()
        call_kwargs = mock_client.send_request.call_args
        messages = call_kwargs.kwargs.get("messages") or call_kwargs.args[0]
        user_contents = [m.content for m in messages if m.role == "user"]
        assert any("Implement retry logic" in c for c in user_contents)

    def test_solo_tracks_cost_to_disk(self, tmp_path: Path) -> None:
        """After solo execution the cost tracker persists data to costs.json."""
        root = create_test_config(tmp_path, mode="solo")

        with patch("router.modes.solo.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.return_value = make_api_response(cost=0.05)
            mock_create.return_value = mock_client

            executor = _build_executor(root)
            executor.execute("Test request")

        costs_file = root / ".dev-aid" / "logs" / "costs.json"
        assert costs_file.exists(), "costs.json was not created"
        costs = json.loads(costs_file.read_text())
        assert costs["total_all_time"] > 0

    def test_solo_writes_routing_log(self, tmp_path: Path) -> None:
        """A human-readable routing.log entry is written after execution."""
        root = create_test_config(tmp_path, mode="solo")

        with patch("router.modes.solo.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.return_value = make_api_response()
            mock_create.return_value = mock_client

            executor = _build_executor(root)
            executor.execute("Hello world")

        log_file = root / ".dev-aid" / "logs" / "routing.log"
        assert log_file.exists(), "routing.log was not created"
        log_text = log_file.read_text()
        assert "[SOLO]" in log_text
        assert "Hello world" in log_text


# ── Ensemble Mode E2E ────────────────────────────────────────────────────────


@pytest.mark.e2e
class TestEnsembleModeE2E:
    """End-to-end tests for ensemble routing mode."""

    def test_ensemble_classifies_and_routes(self, tmp_path: Path) -> None:
        """Ensemble mode classifies the task and returns with task_type."""
        root = create_test_config(tmp_path, mode="ensemble")

        with patch("router.modes.ensemble.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.return_value = make_api_response(
                content="Security audit complete."
            )
            mock_create.return_value = mock_client

            executor = _build_executor(root)
            result = executor.execute("Perform a security audit of the codebase")

        assert result["success"] is True
        assert result["mode"] == "ensemble"
        assert "task_type" in result
        assert "explanation" in result

    def test_ensemble_returns_task_confidence(self, tmp_path: Path) -> None:
        """Ensemble mode provides classification confidence."""
        root = create_test_config(tmp_path, mode="ensemble")

        with patch("router.modes.ensemble.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.return_value = make_api_response()
            mock_create.return_value = mock_client

            executor = _build_executor(root)
            result = executor.execute("Write documentation for the API")

        assert result["success"] is True
        assert "task_confidence" in result

    def test_ensemble_tracks_selected_model(self, tmp_path: Path) -> None:
        """Result includes which model was selected."""
        root = create_test_config(tmp_path, mode="ensemble")

        with patch("router.modes.ensemble.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.return_value = make_api_response()
            mock_create.return_value = mock_client

            executor = _build_executor(root)
            result = executor.execute("Implement a sorting algorithm")

        assert result["success"] is True
        assert "selected_model" in result


# ── Challenger Mode E2E ──────────────────────────────────────────────────────


@pytest.mark.e2e
class TestChallengerModeE2E:
    """End-to-end tests for challenger routing mode."""

    def test_challenger_without_trigger_runs_primary_only(self, tmp_path: Path) -> None:
        """Without force_challenge or trigger keywords, only primary runs."""
        root = create_test_config(tmp_path, mode="challenger")

        with patch("router.modes.challenger.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.return_value = make_api_response(content="Primary only output")
            mock_create.return_value = mock_client

            executor = _build_executor(root)
            result = executor.execute("Fix a typo in the readme")

        assert result["success"] is True
        assert result["mode"] == "challenger"
        assert result["challenged"] is False
        assert result["response"] == "Primary only output"

    def test_challenger_force_challenge_calls_both_models(self, tmp_path: Path) -> None:
        """force_challenge=True runs both primary and challenger models."""
        root = create_test_config(tmp_path, mode="challenger")

        with patch("router.modes.challenger.create_client") as mock_create:
            mock_client = Mock()
            primary_resp = make_api_response(content="Primary output", cost=0.02)
            challenger_resp = make_api_response(
                content="SEVERITY: NONE\nImplementation looks good!",
                model="gemini-2.0-flash",
                provider="gemini",
                cost=0.001,
            )
            mock_client.send_request.side_effect = [primary_resp, challenger_resp]
            mock_create.return_value = mock_client

            executor = _build_executor(root)
            result = executor.execute("Review this code", force_challenge=True)

        assert result["success"] is True
        assert result["mode"] == "challenger"
        assert result["challenged"] is True
        assert result["issues_found"] is False
        assert mock_client.send_request.call_count == 2

    def test_challenger_trigger_keyword_activates_review(self, tmp_path: Path) -> None:
        """A review trigger keyword in the request activates the challenger."""
        root = create_test_config(tmp_path, mode="challenger")

        with patch("router.modes.challenger.create_client") as mock_create:
            mock_client = Mock()
            primary_resp = make_api_response(content="Auth implementation", cost=0.02)
            reviewer_resp = make_api_response(
                content="SEVERITY: LOW\nMinor issue with token expiry",
                cost=0.005,
            )
            mock_client.send_request.side_effect = [primary_resp, reviewer_resp]
            mock_create.return_value = mock_client

            executor = _build_executor(root)
            # "security" is in the review_triggers list
            result = executor.execute("Implement security middleware for auth tokens")

        assert result["success"] is True
        assert result["challenged"] is True
        assert result["issues_found"] is True

    def test_challenger_auto_refine_on_high_severity(self, tmp_path: Path) -> None:
        """HIGH severity triggers auto-refinement (three API calls)."""
        root = create_test_config(tmp_path, mode="challenger")

        with patch("router.modes.challenger.create_client") as mock_create:
            mock_client = Mock()
            primary_resp = make_api_response(content="Initial implementation", cost=0.02)
            review_resp = make_api_response(
                content="SEVERITY: HIGH\nSQL injection vulnerability found", cost=0.005
            )
            refined_resp = make_api_response(content="Refined safe implementation", cost=0.02)
            mock_client.send_request.side_effect = [primary_resp, review_resp, refined_resp]
            mock_create.return_value = mock_client

            executor = _build_executor(root)
            result = executor.execute("security critical code review", force_challenge=True)

        assert result["success"] is True
        assert result["refined"] is True
        assert result["final_response"] == "Refined safe implementation"
        assert result["cost"] > 0.04  # Sum of all three calls
        assert mock_client.send_request.call_count == 3

    def test_challenger_graceful_when_reviewer_fails(self, tmp_path: Path) -> None:
        """If challenger model fails, primary response is still returned."""
        root = create_test_config(tmp_path, mode="challenger")

        with patch("router.modes.challenger.create_client") as mock_create:
            mock_client = Mock()
            primary_resp = make_api_response(content="Good output", cost=0.02)
            mock_client.send_request.side_effect = [
                primary_resp,
                RuntimeError("Challenger API timeout"),
            ]
            mock_create.return_value = mock_client

            executor = _build_executor(root)
            result = executor.execute("security audit", force_challenge=True)

        assert result["success"] is True
        assert result["challenged"] is True
        assert result.get("challenger_failed") is True


# ── Budget Enforcement E2E ───────────────────────────────────────────────────


@pytest.mark.e2e
class TestBudgetEnforcementE2E:
    """End-to-end tests for daily budget limit enforcement."""

    def test_rejects_when_over_budget(self, tmp_path: Path) -> None:
        """After exceeding daily budget the router returns a budget error."""
        root = create_test_config(tmp_path, mode="solo", budget=0.01)

        with patch("router.modes.solo.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.return_value = make_api_response(cost=0.05)
            mock_create.return_value = mock_client

            executor = _build_executor(root)

            # First request succeeds (budget checked *before* execution)
            result1 = executor.execute("First request")
            assert result1["success"] is True

            # Second request should be rejected because cost_tracker now
            # shows $0.05 spent against a $0.01 daily limit
            result2 = executor.execute("Second request")
            assert result2["success"] is False
            assert "budget" in result2["error"].lower()

    def test_budget_status_included_in_rejection(self, tmp_path: Path) -> None:
        """Rejection payload includes detailed budget_status dict."""
        root = create_test_config(tmp_path, mode="solo", budget=0.01)

        with patch("router.modes.solo.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.return_value = make_api_response(cost=0.05)
            mock_create.return_value = mock_client

            executor = _build_executor(root)
            executor.execute("First")
            result = executor.execute("Second")

        assert "budget_status" in result
        assert result["budget_status"]["over_budget"] is True

    def test_zero_budget_rejects_immediately(self, tmp_path: Path) -> None:
        """A budget of 0.0 rejects every request."""
        root = create_test_config(tmp_path, mode="solo", budget=0.0)

        # Pre-seed cost tracker with a tiny cost to trigger is_over_budget
        # (is_over_budget uses >, so 0 > 0 is False; we test the "just over" case)
        logs_dir = root / ".dev-aid" / "logs"
        tracker = CostTracker(logs_dir)
        tracker.log_decision(
            mode="solo",
            task_type="test",
            model="test",
            provider="test",
            cost=0.001,
            tokens_input=1,
            tokens_output=1,
            latency_ms=1,
            request="seed",
        )

        executor = _build_executor(root)
        result = executor.execute("Any request")
        assert result["success"] is False
        assert "budget" in result["error"].lower()


# ── Fallback Chain E2E ───────────────────────────────────────────────────────


@pytest.mark.e2e
class TestFallbackChainE2E:
    """End-to-end tests for model fallback when primary fails."""

    def test_ensemble_uses_fallback_on_provider_failure(self, tmp_path: Path) -> None:
        """When the recommended model's provider is invalid, ensemble falls back."""
        root = create_test_config(tmp_path, mode="ensemble")

        with patch("router.modes.ensemble.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.return_value = make_api_response(content="Fallback response")
            mock_create.return_value = mock_client

            executor = _build_executor(root)

            # Sabotage provider validation for the first call only,
            # then succeed on fallback.
            original_validate = executor.config.validate_provider
            call_count = [0]

            def validate_side_effect(provider: str) -> Tuple[bool, str]:
                call_count[0] += 1
                if call_count[0] <= 1:
                    return (False, "Provider temporarily unavailable")
                return original_validate(provider)

            executor.config.validate_provider = validate_side_effect  # type: ignore[assignment]
            # Clear lru_cache so the ensemble re-resolves
            _clear_config_cache(executor.config)

            result = executor.execute("Implement a function")

        assert result["success"] is True
        assert result["used_fallback"] is True

    def test_solo_api_error_returns_failure(self, tmp_path: Path) -> None:
        """Solo mode surfaces the error when the API client raises."""
        root = create_test_config(tmp_path, mode="solo")

        with patch("router.modes.solo.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.side_effect = ConnectionError("Network down")
            mock_create.return_value = mock_client

            executor = _build_executor(root)
            result = executor.execute("Anything")

        assert result["success"] is False
        assert "Network down" in result.get("error", "")


# ── Cost Tracking Persistence E2E ────────────────────────────────────────────


@pytest.mark.e2e
class TestCostPersistenceE2E:
    """End-to-end tests for cost tracking file persistence."""

    def test_costs_json_structure_after_single_request(self, tmp_path: Path) -> None:
        """costs.json has correct structure after one request."""
        root = create_test_config(tmp_path, mode="solo")

        with patch("router.modes.solo.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.return_value = make_api_response(cost=0.03)
            mock_create.return_value = mock_client

            executor = _build_executor(root)
            executor.execute("Single request")

        costs = json.loads((root / ".dev-aid" / "logs" / "costs.json").read_text())
        assert costs["total_all_time"] == pytest.approx(0.03, abs=1e-6)
        # by_date should have today's entry
        assert len(costs["by_date"]) == 1
        day_entry = next(iter(costs["by_date"].values()))
        assert day_entry["requests"] == 1

    def test_costs_accumulate_across_requests(self, tmp_path: Path) -> None:
        """Multiple requests accumulate costs correctly."""
        root = create_test_config(tmp_path, mode="solo")

        with patch("router.modes.solo.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.side_effect = [
                make_api_response(cost=0.01),
                make_api_response(cost=0.02),
                make_api_response(cost=0.03),
            ]
            mock_create.return_value = mock_client

            executor = _build_executor(root)
            executor.execute("Request 1")
            executor.execute("Request 2")
            executor.execute("Request 3")

        costs = json.loads((root / ".dev-aid" / "logs" / "costs.json").read_text())
        assert costs["total_all_time"] == pytest.approx(0.06, abs=1e-6)
        day_entry = next(iter(costs["by_date"].values()))
        assert day_entry["requests"] == 3

    def test_routing_log_grows_per_request(self, tmp_path: Path) -> None:
        """Each successful request appends a line to routing.log."""
        root = create_test_config(tmp_path, mode="solo")

        with patch("router.modes.solo.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.return_value = make_api_response()
            mock_create.return_value = mock_client

            executor = _build_executor(root)
            executor.execute("Request A")
            executor.execute("Request B")

        log_text = (root / ".dev-aid" / "logs" / "routing.log").read_text()
        lines = [line for line in log_text.strip().split("\n") if line.strip()]
        assert len(lines) == 2

    def test_model_stats_recorded_per_day(self, tmp_path: Path) -> None:
        """Per-model stats in by_date entry are updated correctly."""
        root = create_test_config(tmp_path, mode="solo")

        with patch("router.modes.solo.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.return_value = make_api_response(
                cost=0.05, input_tokens=200, output_tokens=100
            )
            mock_create.return_value = mock_client

            executor = _build_executor(root)
            executor.execute("Test model stats")

        costs = json.loads((root / ".dev-aid" / "logs" / "costs.json").read_text())
        day_entry = next(iter(costs["by_date"].values()))
        # The model key logged by _log_decision is result["model"], which is
        # the short model name from SoloMode (e.g. "claude-sonnet").
        assert len(day_entry["by_model"]) >= 1
        model_stats = next(iter(day_entry["by_model"].values()))
        assert model_stats["calls"] == 1
        assert model_stats["tokens_input"] > 0


# ── Mode Selection E2E ───────────────────────────────────────────────────────


@pytest.mark.e2e
class TestModeSelectionE2E:
    """End-to-end tests for mode selection from config and overrides."""

    def test_default_mode_from_config(self, tmp_path: Path) -> None:
        """Without an explicit mode the router uses orchestration_mode from settings.json."""
        root = create_test_config(tmp_path, mode="solo")

        with patch("router.modes.solo.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.return_value = make_api_response()
            mock_create.return_value = mock_client

            executor = _build_executor(root)
            result = executor.execute("Test default mode")

        assert result["mode"] == "solo"

    def test_explicit_mode_overrides_config(self, tmp_path: Path) -> None:
        """Passing ``mode='challenger'`` overrides the config default."""
        root = create_test_config(tmp_path, mode="solo")

        with patch("router.modes.challenger.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.return_value = make_api_response()
            mock_create.return_value = mock_client

            executor = _build_executor(root)
            result = executor.execute("Test override", mode="challenger")

        assert result["mode"] == "challenger"

    def test_invalid_mode_raises_valueerror(self, tmp_path: Path) -> None:
        """An unknown mode raises ``ValueError``."""
        root = create_test_config(tmp_path, mode="solo")
        executor = _build_executor(root)

        with pytest.raises(ValueError, match="Unknown mode"):
            executor.execute("Test", mode="nonexistent")

    def test_ensemble_config_mode(self, tmp_path: Path) -> None:
        """Config set to ensemble uses ensemble mode by default."""
        root = create_test_config(tmp_path, mode="ensemble")

        with patch("router.modes.ensemble.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.return_value = make_api_response()
            mock_create.return_value = mock_client

            executor = _build_executor(root)
            result = executor.execute("Do something useful")

        assert result["mode"] == "ensemble"

    def test_challenger_config_mode(self, tmp_path: Path) -> None:
        """Config set to challenger uses challenger mode by default."""
        root = create_test_config(tmp_path, mode="challenger")

        with patch("router.modes.challenger.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.return_value = make_api_response()
            mock_create.return_value = mock_client

            executor = _build_executor(root)
            result = executor.execute("Innocent request without triggers")

        assert result["mode"] == "challenger"


# ── Output Formatting E2E ────────────────────────────────────────────────────


@pytest.mark.e2e
class TestOutputFormattingE2E:
    """End-to-end tests for the executor's format_output method."""

    def test_format_success_solo(self, tmp_path: Path) -> None:
        """format_output produces readable text for a solo result."""
        root = create_test_config(tmp_path, mode="solo")

        with patch("router.modes.solo.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.return_value = make_api_response(content="Hello, world!")
            mock_create.return_value = mock_client

            executor = _build_executor(root)
            result = executor.execute("Say hello")
            formatted = executor.format_output(result)

        assert "Hello, world!" in formatted
        assert "SOLO" in formatted

    def test_format_failure(self, tmp_path: Path) -> None:
        """format_output for a failed result includes the error message."""
        root = create_test_config(tmp_path, mode="solo")
        executor = _build_executor(root)

        failure_result: Dict[str, Any] = {
            "success": False,
            "error": "Something went wrong",
        }
        formatted = executor.format_output(failure_result)
        assert "Something went wrong" in formatted

    def test_format_verbose_includes_metrics(self, tmp_path: Path) -> None:
        """Verbose formatting includes cost and token metrics."""
        root = create_test_config(tmp_path, mode="solo")

        with patch("router.modes.solo.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.return_value = make_api_response(cost=0.0225)
            mock_create.return_value = mock_client

            executor = _build_executor(root)
            result = executor.execute("Test")
            formatted = executor.format_output(result, verbose=True)

        assert "$0.0225" in formatted
        assert "Tokens:" in formatted


# ── Router Status E2E ────────────────────────────────────────────────────────


@pytest.mark.e2e
class TestRouterStatusE2E:
    """End-to-end tests for get_status after executing requests."""

    def test_status_reflects_execution(self, tmp_path: Path) -> None:
        """After execution, get_status returns updated cost data."""
        root = create_test_config(tmp_path, mode="solo")

        with patch("router.modes.solo.create_client") as mock_create:
            mock_client = Mock()
            mock_client.send_request.return_value = make_api_response(cost=0.10)
            mock_create.return_value = mock_client

            executor = _build_executor(root)
            executor.execute("Status test")

            status = executor.get_status()

        assert status["current_mode"] == "solo"
        assert status["today"]["cost"] == pytest.approx(0.10, abs=1e-6)
        assert status["today"]["requests"] == 1
        assert "budget" in status
