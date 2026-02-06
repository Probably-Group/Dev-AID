"""Extended tests for CostTracker — covering error paths and edge cases"""

from unittest.mock import patch

import pytest

from router.cost_tracker import CostTracker, RoutingDecision


class TestRoutingDecision:
    """Test RoutingDecision dataclass"""

    def test_create_decision(self):
        d = RoutingDecision(
            timestamp="2024-01-01T00:00:00",
            mode="solo",
            task_type="code",
            model="claude-sonnet",
            provider="anthropic",
            cost=0.5,
            tokens_input=100,
            tokens_output=200,
            latency_ms=350.0,
            request_preview="Test request",
        )
        assert d.mode == "solo"
        assert d.cost == 0.5
        assert d.tokens_input == 100


class TestCostTrackerLoadErrors:
    """Test _load_costs error handling"""

    def test_load_corrupt_json(self, tmp_path):
        """Test loading corrupt cost file"""
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        costs_file = logs_dir / "costs.json"
        costs_file.write_text("{bad json")

        tracker = CostTracker(logs_dir)
        assert tracker.costs["total_all_time"] == 0.0

    def test_load_io_error(self, tmp_path):
        """Test loading when file read fails"""
        logs_dir = tmp_path / "logs"
        logs_dir.mkdir()
        costs_file = logs_dir / "costs.json"
        costs_file.write_text("{}")

        with patch("builtins.open", side_effect=IOError("read fail")):
            # CostTracker falls back to default when open fails
            tracker = CostTracker.__new__(CostTracker)
            tracker.logs_dir = logs_dir
            tracker.routing_log_file = logs_dir / "routing.log"
            tracker.costs_file = costs_file
            tracker.costs = tracker._load_costs()
            assert tracker.costs["total_all_time"] == 0.0


class TestCostTrackerSaveErrors:
    """Test _save_costs error handling"""

    def test_save_io_error(self, tmp_path, capsys):
        """Test save when write fails"""
        logs_dir = tmp_path / "logs"
        tracker = CostTracker(logs_dir)
        tracker.costs["total_all_time"] = 5.0

        with patch("builtins.open", side_effect=IOError("write fail")):
            tracker._save_costs()

        captured = capsys.readouterr()
        assert "Could not save costs" in captured.out


class TestCostTrackerWriteLogErrors:
    """Test _write_routing_log error handling"""

    def test_write_log_io_error(self, tmp_path, capsys):
        """Test log write when file write fails"""
        logs_dir = tmp_path / "logs"
        tracker = CostTracker(logs_dir)

        decision = RoutingDecision(
            timestamp="2024-01-01T00:00:00",
            mode="solo",
            task_type="code",
            model="model",
            provider="prov",
            cost=0.1,
            tokens_input=10,
            tokens_output=20,
            latency_ms=100.0,
            request_preview="test",
        )

        with patch("builtins.open", side_effect=IOError("write fail")):
            tracker._write_routing_log(decision)

        captured = capsys.readouterr()
        assert "Could not write routing log" in captured.out


class TestCostTrackerAdditionalMethods:
    """Test additional methods not covered"""

    @pytest.fixture
    def tracker(self, tmp_path):
        return CostTracker(tmp_path / "logs")

    def test_get_today_requests(self, tracker):
        """Test get_today_requests"""
        assert tracker.get_today_requests() == 0

        tracker.log_decision("solo", "t1", "m1", "p1", 0.1, 10, 20, 100, "r1")
        tracker.log_decision("solo", "t2", "m2", "p2", 0.2, 10, 20, 100, "r2")

        assert tracker.get_today_requests() == 2

    def test_is_over_budget(self, tracker):
        """Test is_over_budget"""
        assert tracker.is_over_budget(100.0) is False

        tracker.log_decision("solo", "t", "m", "p", 150.0, 10, 20, 100, "r")
        assert tracker.is_over_budget(100.0) is True

    def test_get_model_stats_today(self, tracker):
        """Test get_model_stats_today"""
        assert tracker.get_model_stats_today() == {}

        tracker.log_decision("solo", "t", "model-a", "p", 0.5, 100, 200, 100, "r")
        tracker.log_decision("solo", "t", "model-b", "p", 0.3, 50, 100, 100, "r")

        stats = tracker.get_model_stats_today()
        assert "model-a" in stats
        assert stats["model-a"]["cost"] == 0.5
        assert stats["model-a"]["calls"] == 1
        assert stats["model-a"]["tokens_input"] == 100
        assert stats["model-a"]["tokens_output"] == 200

        assert "model-b" in stats
        assert stats["model-b"]["cost"] == 0.3

    def test_get_recent_decisions_no_file(self, tracker):
        """Test get_recent_decisions when no log exists"""
        decisions = tracker.get_recent_decisions()
        assert decisions == []

    def test_get_recent_decisions_malformed_line(self, tracker):
        """Test get_recent_decisions with malformed log lines"""
        tracker.routing_log_file.write_text("malformed line\n")
        decisions = tracker.get_recent_decisions()
        # Lines with <4 parts get skipped
        assert decisions == []

    def test_get_recent_decisions_bad_cost(self, tracker):
        """Test get_recent_decisions with unparseable cost"""
        log_line = (
            "2024-01-01T00:00:00 [SOLO] Task: code | "
            "Model: m1 | Cost: $BADVALUE | "
            "Tokens: 10→20 | Latency: 100ms | "
            'Request: "test..."\n'
        )
        tracker.routing_log_file.write_text(log_line)
        decisions = tracker.get_recent_decisions()
        assert len(decisions) == 1
        assert decisions[0]["cost"] == 0.0

    def test_get_budget_status_zero_limit(self, tracker):
        """Test budget status with zero daily limit"""
        status = tracker.get_budget_status(0.0)
        assert status["percentage"] == 0
        assert status["daily_limit"] == 0.0

    def test_update_costs_multiple_same_model(self, tracker):
        """Test updating costs multiple times with same model"""
        tracker.log_decision("solo", "t", "model-a", "prov", 1.0, 100, 200, 100, "r")
        tracker.log_decision("solo", "t", "model-a", "prov", 2.0, 150, 250, 100, "r")

        assert tracker.costs["by_model"]["model-a"]["cost"] == 3.0
        assert tracker.costs["by_model"]["model-a"]["calls"] == 2

    def test_update_costs_by_provider(self, tracker):
        """Test provider tracking"""
        tracker.log_decision("solo", "t", "m", "anthropic", 1.0, 10, 20, 100, "r")
        tracker.log_decision("solo", "t", "m", "openai", 0.5, 10, 20, 100, "r")

        assert tracker.costs["by_provider"]["anthropic"]["cost"] == 1.0
        assert tracker.costs["by_provider"]["openai"]["cost"] == 0.5
