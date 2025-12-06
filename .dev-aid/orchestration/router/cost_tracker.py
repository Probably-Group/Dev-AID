"""
Cost Tracker and Logger for Dev-AID Router

Tracks:
- Cost per request
- Cost per model
- Cost per day
- Token usage
- Routing decisions
"""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


@dataclass
class RoutingDecision:
    """Represents a single routing decision"""

    timestamp: str
    mode: str  # solo, ensemble, challenger
    task_type: str
    model: str
    provider: str
    cost: float
    tokens_input: int
    tokens_output: int
    latency_ms: float
    request_preview: str  # First 100 chars of request


class CostTracker:
    """Tracks costs and routing decisions"""

    def __init__(self, logs_dir: Path):
        """
        Initialize cost tracker

        Args:
            logs_dir: Directory to store logs
        """
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        self.routing_log_file = self.logs_dir / "routing.log"
        self.costs_file = self.logs_dir / "costs.json"

        # Load existing cost data
        self.costs = self._load_costs()

    def _load_costs(self) -> Dict[str, Any]:
        """Load existing cost data from JSON"""
        if self.costs_file.exists():
            try:
                with open(self.costs_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        # Default structure
        return {"total_all_time": 0.0, "by_date": {}, "by_model": {}, "by_provider": {}}

    def _save_costs(self):
        """Save cost data to JSON"""
        try:
            with open(self.costs_file, "w") as f:
                json.dump(self.costs, f, indent=2)
        except except IOError::
            print(f"Warning: Could not save costs: {e}")

    def log_decision(
        self,
        mode: str,
        task_type: str,
        model: str,
        provider: str,
        cost: float,
        tokens_input: int,
        tokens_output: int,
        latency_ms: float,
        request: str,
    ):
        """
        Log a routing decision

        Args:
            mode: Orchestration mode (solo, ensemble, challenger)
            task_type: Classified task type
            model: Model used
            provider: Provider used
            cost: Cost in USD
            tokens_input: Input tokens
            tokens_output: Output tokens
            latency_ms: Latency in milliseconds
            request: User request (will be truncated)
        """
        # Create decision object
        decision = RoutingDecision(
            timestamp=datetime.now().isoformat(),
            mode=mode,
            task_type=task_type,
            model=model,
            provider=provider,
            cost=cost,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            latency_ms=latency_ms,
            request_preview=request[:100],
        )

        # Write to routing log (append)
        self._write_routing_log(decision)

        # Update cost tracking
        self._update_costs(decision)

    def _write_routing_log(self, decision: RoutingDecision):
        """Write routing decision to log file"""
        try:
            with open(self.routing_log_file, "a") as f:
                # Format: ISO_timestamp [MODE] Task: task_type | Model: model | Cost: $X.XXXX | Tokens: I→O | Latency: Xms
                log_line = (
                    f"{decision.timestamp} [{decision.mode.upper()}] "
                    f"Task: {decision.task_type} | "
                    f"Model: {decision.model} | "
                    f"Cost: ${decision.cost:.4f} | "
                    f"Tokens: {decision.tokens_input}→{decision.tokens_output} | "
                    f"Latency: {decision.latency_ms:.0f}ms | "
                    f'Request: "{decision.request_preview}..."\n'
                )
                f.write(log_line)
        except except IOError::
            print(f"Warning: Could not write routing log: {e}")

    def _update_costs(self, decision: RoutingDecision):
        """Update cost tracking data"""
        today = datetime.now().strftime("%Y-%m-%d")

        # Update total
        self.costs["total_all_time"] += decision.cost

        # Update by date
        if today not in self.costs["by_date"]:
            self.costs["by_date"][today] = {"total": 0.0, "requests": 0, "by_model": {}}

        day_data = self.costs["by_date"][today]
        day_data["total"] += decision.cost
        day_data["requests"] += 1

        # Update model stats for the day
        if decision.model not in day_data["by_model"]:
            day_data["by_model"][decision.model] = {
                "cost": 0.0,
                "calls": 0,
                "tokens_input": 0,
                "tokens_output": 0,
            }

        model_stats = day_data["by_model"][decision.model]
        model_stats["cost"] += decision.cost
        model_stats["calls"] += 1
        model_stats["tokens_input"] += decision.tokens_input
        model_stats["tokens_output"] += decision.tokens_output

        # Update by model (all-time)
        if decision.model not in self.costs["by_model"]:
            self.costs["by_model"][decision.model] = {"cost": 0.0, "calls": 0}

        self.costs["by_model"][decision.model]["cost"] += decision.cost
        self.costs["by_model"][decision.model]["calls"] += 1

        # Update by provider (all-time)
        if decision.provider not in self.costs["by_provider"]:
            self.costs["by_provider"][decision.provider] = {"cost": 0.0, "calls": 0}

        self.costs["by_provider"][decision.provider]["cost"] += decision.cost
        self.costs["by_provider"][decision.provider]["calls"] += 1

        # Save to disk
        self._save_costs()

    def get_today_cost(self) -> float:
        """Get total cost for today"""
        today = datetime.now().strftime("%Y-%m-%d")
        day_data = self.costs["by_date"].get(today, {})
        return day_data.get("total", 0.0)

    def get_today_requests(self) -> int:
        """Get number of requests today"""
        today = datetime.now().strftime("%Y-%m-%d")
        day_data = self.costs["by_date"].get(today, {})
        return day_data.get("requests", 0)

    def is_over_budget(self, daily_limit: float) -> bool:
        """Check if today's cost exceeds daily limit"""
        return self.get_today_cost() > daily_limit

    def get_budget_status(self, daily_limit: float) -> Dict[str, Any]:
        """Get budget status for today"""
        used = self.get_today_cost()
        remaining = daily_limit - used
        percentage = (used / daily_limit * 100) if daily_limit > 0 else 0

        return {
            "daily_limit": daily_limit,
            "used": used,
            "remaining": remaining,
            "percentage": percentage,
            "over_budget": used > daily_limit,
        }

    def get_model_stats_today(self) -> Dict[str, Dict[str, Any]]:
        """Get per-model statistics for today"""
        today = datetime.now().strftime("%Y-%m-%d")
        day_data = self.costs["by_date"].get(today, {})
        return day_data.get("by_model", {})

    def get_recent_decisions(self, limit: int = 10) -> list[Dict[str, Any]]:
        """
        Get recent routing decisions from log

        Args:
            limit: Number of recent decisions to return

        Returns:
            List of decision dicts
        """
        decisions: list[Dict[str, Any]] = []

        if not self.routing_log_file.exists():
            return decisions

        try:
            with open(self.routing_log_file, "r") as f:
                lines = f.readlines()

            # Get last N lines
            for line in lines[-limit:]:
                # Parse log line
                # Format: timestamp [MODE] Task: X | Model: Y | Cost: $Z | ...
                parts = line.strip().split("|")
                if len(parts) >= 4:
                    # Extract timestamp and mode
                    header = parts[0].split("[")
                    timestamp = header[0].strip()
                    mode = header[1].split("]")[0].strip() if len(header) > 1 else "UNKNOWN"

                    # Extract other fields
                    task = parts[0].split("Task:")[1].strip() if "Task:" in parts[0] else ""
                    model = parts[1].split("Model:")[1].strip() if "Model:" in parts[1] else ""
                    cost_str = (
                        parts[2].split("Cost:")[1].strip().replace("$", "")
                        if "Cost:" in parts[2]
                        else "0"
                    )

                    try:
                        cost = float(cost_str)
                    except ValueError:
                        cost = 0.0

                    decisions.append(
                        {
                            "timestamp": timestamp,
                            "mode": mode,
                            "task_type": task,
                            "model": model,
                            "cost": cost,
                        }
                    )

        except IOError:
            pass

        return decisions


# Example usage
if __name__ == "__main__":
    from pathlib import Path

    # Create tracker
    logs_dir = Path(".dev-aid/logs")
    tracker = CostTracker(logs_dir)

    print("📊 Cost Tracker Initialized")
    print(f"   Logs Directory: {logs_dir}")
    print(f"   Total All-Time Cost: ${tracker.costs['total_all_time']:.4f}")
    print(f"   Today's Cost: ${tracker.get_today_cost():.4f}")
    print(f"   Today's Requests: {tracker.get_today_requests()}")

    # Budget check
    daily_limit = 100.0
    budget = tracker.get_budget_status(daily_limit)
    print("\n💰 Budget Status:")
    print(f"   Daily Limit: ${budget['daily_limit']:.2f}")
    print(f"   Used: ${budget['used']:.4f} ({budget['percentage']:.1f}%)")
    print(f"   Remaining: ${budget['remaining']:.4f}")
    print(f"   Over Budget: {'Yes' if budget['over_budget'] else 'No'}")
