"""Regression tests for audit Sprint-2 reliability fixes (H4, M16)."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from agents.core.agent_runner import _is_retryable_error, _retry_after_seconds
from router.api_clients.base import (
    APIClientError,
    _is_auth_error,
    _is_transient_error,
)


class _Err(Exception):
    def __init__(self, status=None, headers=None):
        super().__init__("boom")
        if status is not None:
            self.status_code = status
        if headers is not None:
            self.response = SimpleNamespace(headers=headers)


# --------------------------------------------------------------------------- #
# H4 — retry classification
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "status,expected",
    [(429, True), (500, True), (503, True), (401, False), (400, False), (404, False)],
)
def test_is_retryable_by_status(status, expected):
    assert _is_retryable_error(_Err(status=status)) is expected


def test_is_retryable_unknown_defaults_true():
    assert _is_retryable_error(Exception("network blip")) is True


def test_is_retryable_by_name():
    class RateLimitError(Exception):
        pass

    class AuthenticationError(Exception):
        pass

    assert _is_retryable_error(RateLimitError()) is True
    assert _is_retryable_error(AuthenticationError()) is False


def test_retry_after_parses_header():
    assert _retry_after_seconds(_Err(status=429, headers={"retry-after": "12"})) == 12.0
    assert _retry_after_seconds(_Err(status=429, headers={})) is None
    assert _retry_after_seconds(Exception("no response")) is None


# --------------------------------------------------------------------------- #
# H4/M16 — APIClientError classification (router side)
# --------------------------------------------------------------------------- #
def test_apiclienterror_carries_retryable_flag():
    err = APIClientError("nope", retryable=False, status_code=401)
    assert err.retryable is False
    assert err.status_code == 401


def test_router_error_classifiers():
    assert _is_auth_error(_Err(status=401), 401) is True
    assert _is_transient_error(_Err(status=429), 429) is True
    assert _is_transient_error(_Err(status=400), 400) is False


# --------------------------------------------------------------------------- #
# M16 — anthropic response never crashes on refusal / empty content
# --------------------------------------------------------------------------- #
def _anthropic_client():
    from router.api_clients.anthropic_client import AnthropicClient

    client = AnthropicClient.__new__(AnthropicClient)  # skip SDK init
    client.model_config = {"cost_per_1m_tokens": {"input": 3.0, "output": 15.0}}
    client.provider = "anthropic"
    return client


def _mock_anthropic_response(content, stop_reason):
    return SimpleNamespace(
        content=content,
        stop_reason=stop_reason,
        id="msg_1",
        usage=SimpleNamespace(input_tokens=5, output_tokens=0),
    )


def test_anthropic_refusal_does_not_crash():
    client = _anthropic_client()
    client.client = Mock()
    client.client.messages.create = Mock(
        return_value=_mock_anthropic_response(content=[], stop_reason="refusal")
    )
    from router.api_clients.base import Message

    resp = client.send_request([Message(role="user", content="hi")], "claude-sonnet-4")
    assert resp.content == "[model declined to respond]"


def test_anthropic_max_tokens_flags_truncated():
    client = _anthropic_client()
    client.client = Mock()
    block = SimpleNamespace(type="text", text="partial answer")
    client.client.messages.create = Mock(
        return_value=_mock_anthropic_response(content=[block], stop_reason="max_tokens")
    )
    from router.api_clients.base import Message

    resp = client.send_request([Message(role="user", content="hi")], "claude-sonnet-4")
    assert resp.content == "partial answer"
    assert resp.metadata["truncated"] is True
