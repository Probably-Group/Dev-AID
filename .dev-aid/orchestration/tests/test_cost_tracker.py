import json
import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock
from router.cost_tracker import CostTracker, RoutingDecision


class TestCostTracker:
    @pytest.fixture
    def tracker(self, tmp_path):
        logs_dir = tmp_path / "logs"
        return CostTracker(logs_dir)

    def test_init_creates_files(self, tracker):
        assert tracker.logs_dir.exists()
        # Files are created on save, not init?
        # No, init loads costs which might not exist.
        assert tracker.costs["total_all_time"] == 0.0

    def test_log_decision(self, tracker):
        tracker.log_decision(
            mode="solo",
            task_type="code_generation",
            model="claude-sonnet",
            provider="anthropic",
            cost=0.5,
            tokens_input=100,
            tokens_output=200,
            latency_ms=500,
            request="Test request",
        )

        assert tracker.costs["total_all_time"] == 0.5
        assert tracker.costs["by_model"]["claude-sonnet"]["cost"] == 0.5

        # Check log file
        assert tracker.routing_log_file.exists()
        content = tracker.routing_log_file.read_text()
        assert "Test request" in content
        assert "claude-sonnet" in content

    def test_get_today_cost(self, tracker):
        tracker.log_decision("solo", "test", "model", "provider", 1.5, 10, 10, 100, "req")
        assert tracker.get_today_cost() == 1.5

    def test_budget_status(self, tracker):
        tracker.log_decision("solo", "test", "model", "provider", 80.0, 10, 10, 100, "req")

        status = tracker.get_budget_status(100.0)
        assert status["used"] == 80.0
        assert status["remaining"] == 20.0
        assert status["over_budget"] is False
        assert status["percentage"] == 80.0

        status_over = tracker.get_budget_status(50.0)
        assert status_over["over_budget"] is True

    def test_get_recent_decisions(self, tracker):
        tracker.log_decision("solo", "task1", "model1", "p1", 0.1, 10, 10, 100, "req1")
        tracker.log_decision("solo", "task2", "model2", "p2", 0.2, 10, 10, 100, "req2")

        decisions = tracker.get_recent_decisions(limit=1)
        assert len(decisions) == 1
        assert decisions[0]["task_type"] == "task2"
        assert decisions[0]["cost"] == 0.2

    def test_persistence(self, tmp_path):
        logs_dir = tmp_path / "logs"
        tracker1 = CostTracker(logs_dir)
        tracker1.log_decision("solo", "task", "model", "p", 1.0, 10, 10, 100, "req")

        # Reload
        tracker2 = CostTracker(logs_dir)
        assert tracker2.costs["total_all_time"] == 1.0
