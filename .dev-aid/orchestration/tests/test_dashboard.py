"""
Tests for Dev-AID Router TUI Dashboard

Verifies rich-based dashboard rendering, budget bar logic,
and CLI entry point.
"""

import json
from pathlib import Path
from typing import Any, Dict

from rich.console import Console
from rich.text import Text

from router.cost_tracker import CostTracker
from router.dashboard import _budget_bar, render_dashboard

# ── Budget bar unit tests ─────────────────────────────────────────────────


class TestBudgetBar:
    """Tests for the _budget_bar helper."""

    def test_green_under_60(self) -> None:
        bar = _budget_bar(30.0, 100.0)
        assert isinstance(bar, Text)
        plain = bar.plain
        assert "30.0%" in plain

    def test_yellow_at_70(self) -> None:
        bar = _budget_bar(70.0, 100.0)
        assert "70.0%" in bar.plain

    def test_red_above_85(self) -> None:
        bar = _budget_bar(90.0, 100.0)
        assert "90.0%" in bar.plain

    def test_caps_at_100(self) -> None:
        bar = _budget_bar(150.0, 100.0)
        assert "100.0%" in bar.plain

    def test_zero_limit(self) -> None:
        bar = _budget_bar(5.0, 0.0)
        assert "0.0%" in bar.plain


# ── Dashboard rendering tests ─────────────────────────────────────────────


def _seed_tracker(tmp_path: Path, costs: Dict[str, Any]) -> CostTracker:
    """Create a CostTracker with pre-seeded data."""
    logs_dir = tmp_path / "logs"
    logs_dir.mkdir(parents=True)
    (logs_dir / "costs.json").write_text(json.dumps(costs))
    return CostTracker(logs_dir)


class TestRenderDashboard:
    """Tests for the render_dashboard function."""

    def test_renders_with_empty_data(self, tmp_path: Path) -> None:
        """Dashboard renders without error when there is no data."""
        tracker = _seed_tracker(
            tmp_path,
            {"total_all_time": 0.0, "by_date": {}, "by_model": {}, "by_provider": {}},
        )
        console = Console(file=None, force_terminal=True, width=120)
        # Should not raise
        render_dashboard(tracker, daily_limit=100.0, console=console)

    def test_renders_with_populated_data(self, tmp_path: Path) -> None:
        """Dashboard renders with realistic multi-day data."""
        costs: Dict[str, Any] = {
            "total_all_time": 1.25,
            "by_date": {
                "2026-02-26": {
                    "total": 0.75,
                    "requests": 5,
                    "by_model": {
                        "claude-sonnet": {
                            "cost": 0.60,
                            "calls": 3,
                            "tokens_input": 3000,
                            "tokens_output": 1500,
                        },
                        "gemini-flash": {
                            "cost": 0.15,
                            "calls": 2,
                            "tokens_input": 2000,
                            "tokens_output": 800,
                        },
                    },
                },
                "2026-02-27": {
                    "total": 0.50,
                    "requests": 3,
                    "by_model": {
                        "claude-sonnet": {
                            "cost": 0.50,
                            "calls": 3,
                            "tokens_input": 2500,
                            "tokens_output": 1200,
                        },
                    },
                },
            },
            "by_model": {
                "claude-sonnet": {"cost": 1.10, "calls": 6},
                "gemini-flash": {"cost": 0.15, "calls": 2},
            },
            "by_provider": {
                "anthropic": {"cost": 1.10, "calls": 6},
                "google": {"cost": 0.15, "calls": 2},
            },
        }

        tracker = _seed_tracker(tmp_path, costs)
        console = Console(file=None, force_terminal=True, width=120)
        render_dashboard(tracker, daily_limit=10.0, console=console)

    def test_renders_with_routing_log(self, tmp_path: Path) -> None:
        """Dashboard includes recent decisions when routing.log exists."""
        costs: Dict[str, Any] = {
            "total_all_time": 0.05,
            "by_date": {},
            "by_model": {},
            "by_provider": {},
        }
        tracker = _seed_tracker(tmp_path, costs)

        # Write a routing log entry
        log_line = (
            "2026-02-27T10:00:00 [SOLO] Task: general | "
            "Model: claude-sonnet | Cost: $0.0500 | "
            "Tokens: 100→50 | Latency: 1234ms | "
            'Request: "test request..."\n'
        )
        (tmp_path / "logs" / "routing.log").write_text(log_line)

        # Re-load tracker to pick up routing log
        tracker = CostTracker(tmp_path / "logs")

        console = Console(file=None, force_terminal=True, width=120)
        render_dashboard(tracker, daily_limit=100.0, console=console)

    def test_budget_over_renders_red(self, tmp_path: Path) -> None:
        """Over-budget state renders without error."""
        costs: Dict[str, Any] = {
            "total_all_time": 200.0,
            "by_date": {
                "2026-02-27": {
                    "total": 200.0,
                    "requests": 10,
                    "by_model": {},
                },
            },
            "by_model": {},
            "by_provider": {},
        }
        tracker = _seed_tracker(tmp_path, costs)
        console = Console(file=None, force_terminal=True, width=120)
        render_dashboard(tracker, daily_limit=50.0, console=console)


# ── Capture output tests ──────────────────────────────────────────────────


class TestDashboardOutput:
    """Tests that verify actual dashboard output content."""

    def test_output_contains_budget_info(self, tmp_path: Path) -> None:
        """Output includes budget-related text."""
        costs: Dict[str, Any] = {
            "total_all_time": 5.0,
            "by_date": {},
            "by_model": {"claude-sonnet": {"cost": 5.0, "calls": 10}},
            "by_provider": {"anthropic": {"cost": 5.0, "calls": 10}},
        }
        tracker = _seed_tracker(tmp_path, costs)

        from io import StringIO

        output = StringIO()
        console = Console(file=output, force_terminal=True, width=120)
        render_dashboard(tracker, daily_limit=100.0, console=console)

        text = output.getvalue()
        assert "Budget Status" in text
        assert "All-Time Summary" in text

    def test_output_contains_model_table(self, tmp_path: Path) -> None:
        """Output includes model usage table when data exists."""
        costs: Dict[str, Any] = {
            "total_all_time": 2.0,
            "by_date": {},
            "by_model": {
                "claude-sonnet": {"cost": 1.5, "calls": 5},
                "gemini-flash": {"cost": 0.5, "calls": 3},
            },
            "by_provider": {},
        }
        tracker = _seed_tracker(tmp_path, costs)

        from io import StringIO

        output = StringIO()
        console = Console(file=output, force_terminal=True, width=120)
        render_dashboard(tracker, daily_limit=50.0, console=console)

        text = output.getvalue()
        assert "claude-sonnet" in text
        assert "gemini-flash" in text
        assert "Model Usage" in text
