"""
Rich TUI Dashboard for Dev-AID Router

Displays cost analytics, budget status, model usage, and routing
decisions using rich tables, panels, and progress bars.

Usage:
    python -m router.dashboard [--root PATH] [--days N]
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .cost_tracker import CostTracker


def _budget_bar(used: float, limit: float, width: int = 40) -> Text:
    """Build a coloured budget bar: green < 60%, yellow 60-85%, red > 85%."""
    pct = (used / limit * 100) if limit > 0 else 0.0
    pct = min(pct, 100.0)

    if pct < 60:
        style = "green"
    elif pct < 85:
        style = "yellow"
    else:
        style = "bold red"

    filled = int(width * pct / 100)
    bar = Text()
    bar.append("█" * filled, style=style)
    bar.append("░" * (width - filled), style="dim")
    bar.append(f" {pct:.1f}%", style=style)
    return bar


def render_dashboard(
    tracker: CostTracker,
    daily_limit: float = 100.0,
    history_days: int = 7,
    console: Optional[Console] = None,
) -> None:
    """Render the full dashboard to the console.

    Args:
        tracker: Initialised CostTracker with loaded data.
        daily_limit: Daily budget limit in USD.
        history_days: Number of recent days to show in the history table.
        console: Rich Console (creates a new one if not provided).
    """
    if console is None:
        console = Console()

    costs = tracker.costs

    # ── Header ────────────────────────────────────────────────────────────
    console.print()
    console.print(
        Panel(
            "[bold cyan]Dev-AID Router Dashboard[/bold cyan]",
            subtitle=f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M')}[/dim]",
            border_style="cyan",
        )
    )

    # ── Budget Panel ──────────────────────────────────────────────────────
    budget = tracker.get_budget_status(daily_limit)
    today_requests = tracker.get_today_requests()

    budget_text = Text()
    budget_text.append("Daily Limit:  ", style="dim")
    budget_text.append(f"${daily_limit:.2f}\n", style="bold")
    budget_text.append("Used Today:   ", style="dim")
    budget_text.append(f"${budget['used']:.4f}\n", style="bold")
    budget_text.append("Remaining:    ", style="dim")
    remaining_style = "bold green" if budget["remaining"] > 0 else "bold red"
    budget_text.append(f"${budget['remaining']:.4f}\n", style=remaining_style)
    budget_text.append("Requests:     ", style="dim")
    budget_text.append(f"{today_requests}\n\n", style="bold")
    budget_text.append_text(_budget_bar(budget["used"], daily_limit))

    status_icon = (
        "[red bold]OVER BUDGET[/red bold]"
        if budget["over_budget"]
        else "[green]Under budget[/green]"
    )
    console.print(
        Panel(
            budget_text,
            title=f"[bold]Budget Status[/bold]  {status_icon}",
            border_style="green" if not budget["over_budget"] else "red",
        )
    )

    # ── All-time Summary ──────────────────────────────────────────────────
    total_days = len(costs.get("by_date", {}))
    total_cost = costs.get("total_all_time", 0.0)
    avg_daily = total_cost / total_days if total_days > 0 else 0.0

    summary_table = Table(show_header=False, box=None, padding=(0, 2))
    summary_table.add_column("label", style="dim")
    summary_table.add_column("value", style="bold")
    summary_table.add_row("All-time cost", f"${total_cost:.4f}")
    summary_table.add_row("Active days", str(total_days))
    summary_table.add_row("Avg daily cost", f"${avg_daily:.4f}")

    console.print(Panel(summary_table, title="[bold]All-Time Summary[/bold]", border_style="blue"))

    # ── Model Usage (all-time) ────────────────────────────────────────────
    by_model: Dict[str, Any] = costs.get("by_model", {})
    if by_model:
        model_table = Table(title="Model Usage (All-Time)", border_style="cyan")
        model_table.add_column("Model", style="bold")
        model_table.add_column("Calls", justify="right")
        model_table.add_column("Cost", justify="right", style="green")
        model_table.add_column("Avg/Call", justify="right")

        for model, stats in sorted(by_model.items(), key=lambda x: x[1]["cost"], reverse=True):
            calls = stats["calls"]
            cost = stats["cost"]
            avg = cost / calls if calls > 0 else 0.0
            model_table.add_row(model, str(calls), f"${cost:.4f}", f"${avg:.4f}")

        console.print(model_table)

    # ── Provider Usage (all-time) ─────────────────────────────────────────
    by_provider: Dict[str, Any] = costs.get("by_provider", {})
    if by_provider:
        provider_table = Table(title="Provider Usage (All-Time)", border_style="magenta")
        provider_table.add_column("Provider", style="bold")
        provider_table.add_column("Calls", justify="right")
        provider_table.add_column("Cost", justify="right", style="green")

        for provider, stats in sorted(
            by_provider.items(), key=lambda x: x[1]["cost"], reverse=True
        ):
            provider_table.add_row(provider, str(stats["calls"]), f"${stats['cost']:.4f}")

        console.print(provider_table)

    # ── Daily History ─────────────────────────────────────────────────────
    by_date: Dict[str, Any] = costs.get("by_date", {})
    if by_date:
        sorted_dates = sorted(by_date.keys(), reverse=True)[:history_days]

        history_table = Table(
            title=f"Daily History (Last {history_days} Days)", border_style="yellow"
        )
        history_table.add_column("Date", style="bold")
        history_table.add_column("Requests", justify="right")
        history_table.add_column("Cost", justify="right", style="green")
        history_table.add_column("Models", style="dim")

        for date in sorted_dates:
            day_data = by_date[date]
            models = ", ".join(day_data.get("by_model", {}).keys())
            history_table.add_row(
                date,
                str(day_data.get("requests", 0)),
                f"${day_data.get('total', 0.0):.4f}",
                models or "-",
            )

        console.print(history_table)

    # ── Recent Decisions ──────────────────────────────────────────────────
    recent = tracker.get_recent_decisions(limit=10)
    if recent:
        decision_table = Table(title="Recent Routing Decisions", border_style="white")
        decision_table.add_column("Time", style="dim")
        decision_table.add_column("Mode", style="bold cyan")
        decision_table.add_column("Task", style="dim")
        decision_table.add_column("Model")
        decision_table.add_column("Cost", justify="right", style="green")

        for d in reversed(recent):
            ts = d.get("timestamp", "")
            # Show only time portion if today
            if ts.startswith(datetime.now().strftime("%Y-%m-%d")):
                ts = (
                    ts.split("T")[-1].split(".")[0]
                    if "T" in ts
                    else ts.split(" ")[-1].split(".")[0]
                )
            else:
                ts = ts.split(".")[0]

            decision_table.add_row(
                ts,
                d.get("mode", "?"),
                d.get("task_type", "-"),
                d.get("model", "-"),
                f"${d.get('cost', 0.0):.4f}",
            )

        console.print(decision_table)

    console.print()


def main() -> int:
    """CLI entry point for the dashboard."""
    import argparse

    parser = argparse.ArgumentParser(description="Dev-AID Router Cost Dashboard")
    parser.add_argument("--root", help="Dev-AID root directory", default=None)
    parser.add_argument(
        "--days", type=int, default=7, help="Number of days for history (default: 7)"
    )
    parser.add_argument(
        "--budget", type=float, default=None, help="Daily budget override (default: from config)"
    )
    args = parser.parse_args()

    # Resolve root
    if args.root:
        root = Path(args.root)
    else:
        # Walk up to find .dev-aid/
        cwd = Path.cwd()
        root = cwd
        while root != root.parent:
            if (root / ".dev-aid").is_dir():
                break
            root = root.parent
        else:
            print("Error: Could not find .dev-aid/ directory", file=sys.stderr)
            return 1

    logs_dir = root / ".dev-aid" / "logs"
    if not logs_dir.exists():
        print(f"No logs directory found at {logs_dir}", file=sys.stderr)
        print("Run some router requests first to generate data.", file=sys.stderr)
        return 1

    tracker = CostTracker(logs_dir)

    # Determine budget
    daily_limit = args.budget
    if daily_limit is None:
        # Try to load from config
        try:
            from .config_loader import load_config

            config = load_config(root)
            daily_limit = config.get_cost_limit()
        except Exception:
            daily_limit = 100.0  # sensible default

    render_dashboard(tracker, daily_limit=daily_limit, history_days=args.days)
    return 0


if __name__ == "__main__":
    sys.exit(main())
