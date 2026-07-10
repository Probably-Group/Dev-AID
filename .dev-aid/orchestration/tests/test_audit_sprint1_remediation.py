"""Regression tests for audit Sprint-1 remediation (H1, H3).

These lock in three fixes:
- H1: the shipped routing config must reference model names that resolve
  against the shipped model registry, and the configured default model must
  resolve (otherwise solo mode raises on every request and the challenger
  security review silently no-ops).
- H1 (output): a failed challenger review must never render as
  "Issues Found: No".
- H3: orchestration-only kwargs (context_size, mcp_context) must not leak
  into the provider SDK call, whose signature rejects unknown keywords.
"""

from unittest.mock import Mock, patch

import pytest

from router.config_loader import load_config
from router.executor import RouterExecutor
from router.modes._protocol import provider_kwargs
from router.modes.challenger import ChallengerMode
from router.modes.ensemble import EnsembleMode
from router.modes.solo import SoloMode


# --------------------------------------------------------------------------- #
# H1 — shipped config integrity
# --------------------------------------------------------------------------- #
class TestShippedConfigResolves:
    """The real .dev-aid/config must be internally consistent."""

    @pytest.fixture(scope="class")
    def config(self):
        return load_config()  # auto-detects the repo's .dev-aid root

    def test_default_model_resolves(self, config):
        default = config.get_default_model()
        assert config.get_model_config(default) is not None, (
            f"default_model {default!r} does not resolve against models.json — "
            "solo mode would raise on every request"
        )

    def test_all_routed_models_resolve(self, config):
        routing = config.get_routing_config()
        unresolved = []
        for mode_name, mode_cfg in routing.get("modes", {}).items():
            if not isinstance(mode_cfg, dict):
                continue
            names = [
                mode_cfg.get("primary_model"),
                mode_cfg.get("challenger_model"),
                *(mode_cfg.get("task_routes") or {}).values(),
            ]
            for name in filter(None, names):
                if config.get_model_config(name) is None:
                    unresolved.append(f"{mode_name}:{name}")
        for name in config.get_fallback_chain():
            if config.get_model_config(name) is None:
                unresolved.append(f"fallback:{name}")
        assert not unresolved, f"routing references unresolvable models: {unresolved}"

    def test_challenger_model_is_on_an_enabled_provider(self, config):
        """The challenger review must be able to actually run out of the box."""
        challenger = config.get_routing_config().get("modes", {}).get("challenger", {})
        model_cfg = config.get_model_config(challenger.get("challenger_model"))
        assert model_cfg is not None
        provider = model_cfg["provider"]
        assert config.models.get(provider, {}).get("enabled") is True, (
            "challenger_model is on a disabled provider — the security review "
            "would silently no-op"
        )


# --------------------------------------------------------------------------- #
# H1 — challenger failure is never rendered as "no issues"
# --------------------------------------------------------------------------- #
def test_failed_challenger_not_reported_as_clean():
    executor = RouterExecutor.__new__(RouterExecutor)  # skip __init__/config load
    result = {
        "success": True,
        "mode": "challenger",
        "challenged": True,
        "challenger_failed": True,
        "challenger_error": "Model configuration not found: opus-4.6",
        "primary_model": "sonnet-4.6",
        "challenger_model": "opus-4.6",
        "response": "some code",
    }
    out = RouterExecutor.format_output(executor, result)
    assert "Issues Found: No" not in out
    assert "did not run" in out.lower() or "unreviewed" in out.lower()


# --------------------------------------------------------------------------- #
# H3 — orchestration kwargs never reach the provider SDK
# --------------------------------------------------------------------------- #
def test_provider_kwargs_strips_orchestration_keys():
    cleaned = provider_kwargs({"context_size": 10, "mcp_context": {"x": 1}, "max_tokens": 4096})
    assert cleaned == {"max_tokens": 4096}


def _mock_config():
    config = Mock()
    config.get_default_model = Mock(return_value="sonnet-4.6")
    config.validate_provider = Mock(return_value=(True, ""))
    config.get_auth_credentials = Mock(return_value=Mock())
    config.get_model_config = Mock(return_value={"id": "claude-sonnet-4-6", "provider": "claude"})
    config.get_routing_config = Mock(
        return_value={"modes": {"challenger": {"review_triggers": []}}}
    )
    return config


def _mock_context_builder():
    builder = Mock()
    builder.build_context = Mock(return_value=Mock(mcp_context={}))
    return builder


@pytest.mark.parametrize("mode_cls", [SoloMode, EnsembleMode, ChallengerMode])
def test_modes_do_not_leak_orchestration_kwargs(mode_cls):
    mode = mode_cls(_mock_config(), _mock_context_builder())
    module = mode_cls.__module__
    with (
        patch(f"{module}.create_client") as mock_create,
        patch(f"{module}.build_system_prompt", return_value="sys"),
    ):
        mock_client = Mock()
        mock_client.send_request = Mock(
            return_value=Mock(
                content="ok",
                tokens_used={"input": 1, "output": 1},
                cost=0.0,
                latency_ms=1.0,
                metadata={},
            )
        )
        mock_create.return_value = mock_client

        # These are exactly what RouterExecutor threads through.
        mode.execute("Test request", context_size=99, mcp_context={"github": "x"})

        assert mock_client.send_request.called
        sent = mock_client.send_request.call_args.kwargs
        assert "context_size" not in sent
        assert "mcp_context" not in sent
