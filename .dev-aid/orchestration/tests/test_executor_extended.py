"""Extended tests for RouterExecutor — covering format_output and _log_decision"""

from unittest.mock import MagicMock

from router.cost_tracker import CostTracker


class TestFormatOutput:
    """Test RouterExecutor.format_output without full init"""

    def _make_executor(self, tmp_path):
        """Create a minimal executor-like object for format_output testing"""
        from router.executor import RouterExecutor

        executor = RouterExecutor.__new__(RouterExecutor)
        executor.cost_tracker = CostTracker(tmp_path / "logs")
        executor.config = MagicMock()
        executor.modes = {}
        return executor

    def test_format_error_result(self, tmp_path):
        executor = self._make_executor(tmp_path)
        result = {"success": False, "error": "Something went wrong"}
        output = executor.format_output(result)
        assert "Error" in output
        assert "Something went wrong" in output

    def test_format_error_result_unknown(self, tmp_path):
        executor = self._make_executor(tmp_path)
        result = {"success": False}
        output = executor.format_output(result)
        assert "Unknown error" in output

    def test_format_solo_result(self, tmp_path):
        executor = self._make_executor(tmp_path)
        result = {
            "success": True,
            "mode": "solo",
            "response": "Hello from solo mode",
        }
        output = executor.format_output(result)
        assert "SOLO mode" in output
        assert "Hello from solo mode" in output

    def test_format_ensemble_result(self, tmp_path):
        executor = self._make_executor(tmp_path)
        result = {
            "success": True,
            "mode": "ensemble",
            "response": "Ensemble response",
            "task_type": "code_generation",
            "explanation": "Code task detected",
            "selected_model": "claude-sonnet",
            "used_fallback": False,
        }
        output = executor.format_output(result)
        assert "ENSEMBLE mode" in output
        assert "code_generation" in output
        assert "claude-sonnet" in output

    def test_format_ensemble_with_fallback(self, tmp_path):
        executor = self._make_executor(tmp_path)
        result = {
            "success": True,
            "mode": "ensemble",
            "response": "Fallback response",
            "task_type": "general",
            "explanation": "fallback",
            "selected_model": "gpt-4o",
            "used_fallback": True,
        }
        output = executor.format_output(result)
        assert "fallback" in output.lower()

    def test_format_challenger_result(self, tmp_path):
        executor = self._make_executor(tmp_path)
        result = {
            "success": True,
            "mode": "challenger",
            "response": "Challenged response",
            "challenged": True,
            "primary_model": "claude-sonnet",
            "challenger_model": "gpt-4o",
            "issues_found": True,
            "refined": True,
        }
        output = executor.format_output(result)
        assert "Challenger Mode" in output
        assert "claude-sonnet" in output
        assert "Refined" in output

    def test_format_challenger_no_issues(self, tmp_path):
        executor = self._make_executor(tmp_path)
        result = {
            "success": True,
            "mode": "challenger",
            "response": "Good response",
            "challenged": True,
            "primary_model": "claude-sonnet",
            "challenger_model": "gpt-4o",
            "issues_found": False,
            "refined": False,
        }
        output = executor.format_output(result)
        assert "Issues Found: No" in output

    def test_format_verbose_metrics(self, tmp_path):
        executor = self._make_executor(tmp_path)
        result = {
            "success": True,
            "mode": "solo",
            "response": "Response",
            "tokens_used": {"input": 100, "output": 200},
            "cost": 0.0045,
            "latency_ms": 1234.5,
        }
        output = executor.format_output(result, verbose=True)
        assert "Metrics" in output
        assert "$0.0045" in output
        assert "100 input" in output
        assert "200 output" in output
        assert "1235ms" in output or "1234ms" in output

    def test_format_verbose_challenger_review(self, tmp_path):
        executor = self._make_executor(tmp_path)
        result = {
            "success": True,
            "mode": "challenger",
            "response": "Final answer",
            "challenged": True,
            "primary_model": "m1",
            "challenger_model": "m2",
            "issues_found": True,
            "challenger_review": "Found issue X in line 5",
            "tokens_used": {"input": 50, "output": 100},
            "cost": 0.01,
            "latency_ms": 500,
        }
        output = executor.format_output(result, verbose=True)
        assert "Challenger Review" in output
        assert "Found issue X" in output


class TestLogDecision:
    """Test RouterExecutor._log_decision for different modes"""

    def _make_executor(self, tmp_path):
        from router.executor import RouterExecutor

        executor = RouterExecutor.__new__(RouterExecutor)
        executor.cost_tracker = CostTracker(tmp_path / "logs")
        return executor

    def test_log_solo_decision(self, tmp_path):
        executor = self._make_executor(tmp_path)
        result = {
            "success": True,
            "mode": "solo",
            "model": "claude-sonnet",
            "provider": "anthropic",
            "cost": 0.5,
            "tokens_used": {"input": 100, "output": 200},
            "latency_ms": 500,
        }
        executor._log_decision(result, "solo", "test request")
        assert executor.cost_tracker.costs["total_all_time"] == 0.5

    def test_log_ensemble_decision(self, tmp_path):
        executor = self._make_executor(tmp_path)
        result = {
            "success": True,
            "selected_model": "gpt-4o",
            "task_type": "code_generation",
            "provider": "openai",
            "cost": 0.3,
            "tokens_used": {"input": 50, "output": 100},
            "latency_ms": 300,
        }
        executor._log_decision(result, "ensemble", "test")
        assert executor.cost_tracker.costs["total_all_time"] == 0.3

    def test_log_challenger_decision(self, tmp_path):
        executor = self._make_executor(tmp_path)
        result = {
            "success": True,
            "primary_model": "claude-sonnet",
            "challenged": True,
            "provider": "anthropic",
            "cost": 0.8,
            "tokens_used": {"input": 200, "output": 400},
            "latency_ms": 1000,
        }
        executor._log_decision(result, "challenger", "test")

    def test_log_decision_missing_fields(self, tmp_path):
        """Test _log_decision handles missing fields gracefully"""
        executor = self._make_executor(tmp_path)
        result = {"success": True}
        # Should not raise
        executor._log_decision(result, "solo", "test")
