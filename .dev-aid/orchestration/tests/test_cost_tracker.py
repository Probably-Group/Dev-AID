"""
Unit tests for cost_tracker.py
"""

import pytest
from pathlib import Path
from datetime import datetime
import sys
import json
import tempfile

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from router.cost_tracker import CostTracker, RequestLog


class TestCostTracker:
    """Test suite for CostTracker"""

    @pytest.fixture
    def temp_log_file(self):
        """Create temporary log file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        yield temp_path
        # Cleanup
        if temp_path.exists():
            temp_path.unlink()

    @pytest.fixture
    def cost_tracker(self, temp_log_file):
        """Create CostTracker with temporary log file"""
        return CostTracker(log_path=temp_log_file)

    def test_track_request_basic(self, cost_tracker):
        """Test basic request tracking"""
        cost_tracker.track_request(
            model="claude-sonnet-4.5",
            task_type="code_generation",
            input_tokens=1000,
            output_tokens=500,
            cost=0.015
        )

        logs = cost_tracker.get_today_logs()
        assert len(logs) == 1
        assert logs[0].model == "claude-sonnet-4.5"
        assert logs[0].task_type == "code_generation"
        assert logs[0].cost == 0.015

    def test_track_multiple_requests(self, cost_tracker):
        """Test tracking multiple requests"""
        requests = [
            ("claude-sonnet-4.5", "code_generation", 1000, 500, 0.015),
            ("gemini-flash", "massive_context", 50000, 1000, 0.004),
            ("gpt-4o", "documentation", 2000, 800, 0.025)
        ]

        for model, task, input_tok, output_tok, cost in requests:
            cost_tracker.track_request(model, task, input_tok, output_tok, cost)

        logs = cost_tracker.get_today_logs()
        assert len(logs) == 3

    def test_get_today_cost(self, cost_tracker):
        """Test calculating today's total cost"""
        cost_tracker.track_request("claude-sonnet-4.5", "code_generation", 1000, 500, 0.015)
        cost_tracker.track_request("gemini-flash", "massive_context", 50000, 1000, 0.004)

        total_cost = cost_tracker.get_today_cost()
        assert total_cost == 0.019

    def test_get_cost_by_model(self, cost_tracker):
        """Test getting cost breakdown by model"""
        cost_tracker.track_request("claude-sonnet-4.5", "code_generation", 1000, 500, 0.015)
        cost_tracker.track_request("claude-sonnet-4.5", "debugging", 800, 400, 0.012)
        cost_tracker.track_request("gemini-flash", "massive_context", 50000, 1000, 0.004)

        by_model = cost_tracker.get_cost_by_model()

        assert "claude-sonnet-4.5" in by_model
        assert "gemini-flash" in by_model
        assert by_model["claude-sonnet-4.5"] == 0.027
        assert by_model["gemini-flash"] == 0.004

    def test_get_cost_by_task_type(self, cost_tracker):
        """Test getting cost breakdown by task type"""
        cost_tracker.track_request("claude-sonnet-4.5", "code_generation", 1000, 500, 0.015)
        cost_tracker.track_request("gemini-flash", "code_generation", 2000, 600, 0.002)
        cost_tracker.track_request("claude-sonnet-4.5", "debugging", 800, 400, 0.012)

        by_task = cost_tracker.get_cost_by_task_type()

        assert "code_generation" in by_task
        assert "debugging" in by_task
        assert by_task["code_generation"] == 0.017
        assert by_task["debugging"] == 0.012

    def test_check_budget_under_limit(self, cost_tracker):
        """Test budget check when under limit"""
        cost_tracker.track_request("claude-sonnet-4.5", "code_generation", 1000, 500, 5.0)

        # Daily limit is 100 by default
        is_over, current, limit = cost_tracker.check_budget()

        assert is_over is False
        assert current == 5.0
        assert limit == 100.0

    def test_check_budget_over_limit(self, cost_tracker):
        """Test budget check when over limit"""
        # Track requests totaling over 100
        for _ in range(30):
            cost_tracker.track_request("claude-opus-4", "complex_reasoning", 10000, 5000, 4.0)

        is_over, current, limit = cost_tracker.check_budget()

        assert is_over is True
        assert current == 120.0
        assert limit == 100.0

    def test_persistence(self, temp_log_file):
        """Test that logs persist across CostTracker instances"""
        # Create first tracker and log request
        tracker1 = CostTracker(log_path=temp_log_file)
        tracker1.track_request("claude-sonnet-4.5", "code_generation", 1000, 500, 0.015)

        # Create second tracker with same log file
        tracker2 = CostTracker(log_path=temp_log_file)
        logs = tracker2.get_today_logs()

        assert len(logs) == 1
        assert logs[0].model == "claude-sonnet-4.5"
        assert logs[0].cost == 0.015

    def test_json_format(self, temp_log_file, cost_tracker):
        """Test that log file is valid JSON"""
        cost_tracker.track_request("claude-sonnet-4.5", "code_generation", 1000, 500, 0.015)

        # Read log file
        with open(temp_log_file, 'r') as f:
            data = json.load(f)

        assert isinstance(data, list)
        assert len(data) == 1
        assert "model" in data[0]
        assert "timestamp" in data[0]
        assert "cost" in data[0]

    def test_get_request_count(self, cost_tracker):
        """Test getting total request count"""
        for _ in range(5):
            cost_tracker.track_request("claude-sonnet-4.5", "code_generation", 1000, 500, 0.015)

        logs = cost_tracker.get_today_logs()
        assert len(logs) == 5

    def test_zero_cost_tracking(self, cost_tracker):
        """Test tracking requests with zero cost"""
        cost_tracker.track_request("test-model", "test_task", 100, 50, 0.0)

        logs = cost_tracker.get_today_logs()
        assert len(logs) == 1
        assert logs[0].cost == 0.0

    def test_custom_daily_limit(self, temp_log_file):
        """Test custom daily limit"""
        tracker = CostTracker(log_path=temp_log_file, daily_limit=50.0)

        tracker.track_request("claude-opus-4", "complex_reasoning", 10000, 5000, 60.0)

        is_over, current, limit = tracker.check_budget()

        assert is_over is True
        assert current == 60.0
        assert limit == 50.0


class TestRequestLog:
    """Test RequestLog dataclass"""

    def test_request_log_creation(self):
        """Test creating RequestLog"""
        log = RequestLog(
            timestamp=datetime.now().isoformat(),
            model="claude-sonnet-4.5",
            task_type="code_generation",
            input_tokens=1000,
            output_tokens=500,
            cost=0.015,
            latency_ms=2500
        )

        assert log.model == "claude-sonnet-4.5"
        assert log.task_type == "code_generation"
        assert log.input_tokens == 1000
        assert log.output_tokens == 500
        assert log.cost == 0.015
        assert log.latency_ms == 2500

    def test_request_log_to_dict(self):
        """Test converting RequestLog to dict"""
        log = RequestLog(
            timestamp="2025-12-05T10:00:00",
            model="claude-sonnet-4.5",
            task_type="code_generation",
            input_tokens=1000,
            output_tokens=500,
            cost=0.015
        )

        log_dict = {
            "timestamp": log.timestamp,
            "model": log.model,
            "task_type": log.task_type,
            "input_tokens": log.input_tokens,
            "output_tokens": log.output_tokens,
            "cost": log.cost,
            "latency_ms": log.latency_ms
        }

        assert log_dict["model"] == "claude-sonnet-4.5"
        assert log_dict["cost"] == 0.015


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
