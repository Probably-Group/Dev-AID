"""Regression tests for audit Sprint-2 injection hardening (M3, F2)."""

from pathlib import Path

import pytest

from conflict_resolver import ConflictResolver
from router.context_builder import _sanitize_untrusted


# --------------------------------------------------------------------------- #
# M3 — hidden-character stripping for untrusted MCP content
# --------------------------------------------------------------------------- #
def test_sanitize_strips_zero_width_and_control_chars():
    dirty = "hello​world‮RTL\x07bell﻿bom"
    clean = _sanitize_untrusted(dirty)
    assert clean == "helloworldRTLbellbom"


def test_sanitize_keeps_normal_whitespace():
    assert _sanitize_untrusted("line1\nline2\ttabbed") == "line1\nline2\ttabbed"


def test_sanitize_coerces_non_str():
    assert _sanitize_untrusted(123) == "123"


# --------------------------------------------------------------------------- #
# F2 — conflict resolver refuses path traversal
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("bad", ["../../etc/passwd", "/etc/passwd", "a/../../b"])
def test_reject_traversal_blocks_escape(bad):
    with pytest.raises(ValueError, match="outside"):
        ConflictResolver._reject_traversal(Path(".dev-aid"), bad)


def test_reject_traversal_allows_in_tree():
    # Should not raise for a normal relative path inside the tree.
    ConflictResolver._reject_traversal(Path(".dev-aid"), "orchestration/router/x.py")
