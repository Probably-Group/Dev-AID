"""
Main Executor for Dev-AID Router

Orchestrates the complete routing workflow:
1. Load configuration
2. Determine orchestration mode
3. Gather MCP context (optional)
4. Execute with appropriate mode
5. Track costs and log decisions
6. Format output
"""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from .config_loader import load_config
from .context_builder import ContextBuilder
from .cost_tracker import CostTracker
from .mcp_client import MCPClientPool, MCPServerConfig
from .mcp_registry import MCPRegistry
from .modes.challenger import ChallengerMode
from .modes.ensemble import EnsembleMode
from .modes.solo import SoloMode

logger = logging.getLogger(__name__)


class RouterExecutor:
    """Main executor for routing and executing AI requests"""

    def __init__(self, dev_aid_root: Optional[Path] = None, use_mcp: bool = True):
        """
        Initialize router executor

        Args:
            dev_aid_root: Root directory of Dev-AID (auto-detected if None)
            use_mcp: Whether to enable MCP context gathering (default: True)
        """
        # Load configuration
        self.config = load_config(dev_aid_root)

        # Initialize MCP components
        self.mcp_enabled = use_mcp
        self.mcp_pool = None
        self.mcp_registry = None

        if use_mcp:
            try:
                self.mcp_registry = MCPRegistry()
                self.mcp_registry.discover_all()
                self.mcp_pool = MCPClientPool()
                # Pool will be populated when needed
            except (OSError, ValueError, RuntimeError) as e:
                logger.warning("MCP initialization failed: %s", e)
                self.mcp_enabled = False

        # Initialize components
        self.context_builder = ContextBuilder(self.config, mcp_pool=self.mcp_pool)
        self.cost_tracker = CostTracker(self.config.root / ".dev-aid" / "logs")

        # Initialize modes
        self.modes: Dict[str, Any] = {
            "solo": SoloMode(self.config, self.context_builder),
            "ensemble": EnsembleMode(self.config, self.context_builder),
            "challenger": ChallengerMode(self.config, self.context_builder),
        }

    async def _execute_async(
        self, request: str, mode: str, context_size: int = 0, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Async execution helper

        Args:
            request: User request
            mode: Orchestration mode
            context_size: Estimated context size in tokens
            **kwargs: Additional parameters

        Returns:
            Result dictionary
        """
        # Gather MCP context if enabled
        if self.mcp_enabled and self.mcp_pool:
            try:
                # Initialize MCP servers if not already done
                await self._initialize_mcp_servers()

                # Gather MCP context (async operation)
                mcp_context = await self.context_builder.gather_mcp_context(request)

                # Store MCP context for this request
                kwargs["mcp_context"] = mcp_context
            except (OSError, RuntimeError, asyncio.TimeoutError) as e:
                logger.warning("MCP context gathering failed: %s", e)
                # Continue without MCP context

        # Execute with appropriate mode
        mode_handler = self.modes[mode]

        try:
            result: Dict[str, Any] = mode_handler.execute(
                request, context_size=context_size, **kwargs
            )

            # Log decision if successful
            if result.get("success"):
                self._log_decision(result, mode, request)

            return result

        except (RuntimeError, ValueError, ConnectionError, TimeoutError) as e:
            logger.error("Execution failed in %s mode: %s", mode, e, exc_info=True)
            error_result: Dict[str, Any] = {
                "success": False,
                "mode": mode,
                "error": "Execution failed. Check logs for details.",
            }
            return error_result

    def execute(
        self,
        request: str,
        mode: Optional[str] = None,
        context_size: int = 0,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Execute a request with routing

        Args:
            request: User request
            mode: Override orchestration mode (None = use config)
            context_size: Estimated context size in tokens
            **kwargs: Additional parameters for API calls

        Returns:
            Result dictionary
        """
        # Determine mode
        if mode is None:
            mode = self.config.get_orchestration_mode()

        if mode not in self.modes:
            raise ValueError(f"Unknown mode: {mode}. Available: {list(self.modes.keys())}")

        # Check budget before executing
        daily_limit = self.config.get_cost_limit()
        if self.cost_tracker.is_over_budget(daily_limit):
            logger.warning("SECURITY: Daily budget limit exceeded ($%.2f)", daily_limit)
            return {
                "success": False,
                "error": f"Daily budget limit exceeded (${daily_limit:.2f})",
                "budget_status": self.cost_tracker.get_budget_status(daily_limit),
            }

        # Run async execution in single event loop
        return asyncio.run(self._execute_async(request, mode, context_size, **kwargs))

    async def _initialize_mcp_servers(self) -> None:
        """Initialize MCP server connections"""
        if not self.mcp_registry or not self.mcp_pool:
            return

        # Get enabled servers
        enabled_servers = self.mcp_registry.get_enabled_servers()

        # Connect to each enabled server
        for server_name, server_info in enabled_servers.items():
            if server_name not in self.mcp_pool.clients:
                config = MCPServerConfig(
                    name=server_info.name,
                    command=server_info.command,
                    args=server_info.args,
                    env=server_info.env,
                )
                try:
                    await self.mcp_pool.add_server(config)
                except (OSError, RuntimeError, ConnectionError) as e:
                    logger.warning("Failed to connect to MCP server %s: %s", server_name, e)

    def _log_decision(self, result: Dict[str, Any], mode: str, request: str) -> None:
        """Log routing decision and cost"""

        # Extract data from result
        tokens_used = result.get("tokens_used", {})
        cost = result.get("cost", 0.0)
        latency_ms = result.get("latency_ms", 0.0)

        # Determine model and provider
        if mode == "ensemble":
            model = result.get("selected_model", "unknown")
            task_type = result.get("task_type", "general")
        elif mode == "challenger":
            model = result.get("primary_model", "unknown")
            task_type = "challenged" if result.get("challenged") else "general"
        else:  # solo
            model = result.get("model", "unknown")
            task_type = "general"

        provider = result.get("provider", "unknown")

        # Log to cost tracker
        self.cost_tracker.log_decision(
            mode=mode,
            task_type=task_type,
            model=model,
            provider=provider,
            cost=cost,
            tokens_input=tokens_used.get("input", 0),
            tokens_output=tokens_used.get("output", 0),
            latency_ms=latency_ms,
            request=request,
        )

    def get_status(self) -> Dict[str, Any]:
        """Get current router status and statistics"""

        # Get current configuration
        mode = self.config.get_orchestration_mode()
        mode_handler = self.modes[mode]
        mode_info = mode_handler.get_info()

        # Get cost statistics
        daily_limit = self.config.get_cost_limit()
        budget_status = self.cost_tracker.get_budget_status(daily_limit)

        today_cost = self.cost_tracker.get_today_cost()
        today_requests = self.cost_tracker.get_today_requests()

        # Get per-model stats
        model_stats = self.cost_tracker.get_model_stats_today()

        # Get recent decisions
        recent_decisions = self.cost_tracker.get_recent_decisions(limit=10)

        return {
            "current_mode": mode,
            "mode_info": mode_info,
            "budget": budget_status,
            "today": {
                "cost": today_cost,
                "requests": today_requests,
                "average_cost": (today_cost / today_requests if today_requests > 0 else 0.0),
            },
            "models": model_stats,
            "recent_decisions": recent_decisions,
            "enabled_providers": self.config.get_enabled_providers(),
            "fallback_chain": self.config.get_fallback_chain(),
        }

    def format_output(self, result: Dict[str, Any], verbose: bool = False) -> str:
        """
        Format result as human-readable string

        Args:
            result: Result dictionary from execute()
            verbose: Include detailed information

        Returns:
            Formatted string
        """
        if not result.get("success"):
            error = result.get("error", "Unknown error")
            return f"❌ Error: {error}"

        mode = result.get("mode", "unknown")
        response = result.get("response", "")

        # Build output
        lines = []

        # Header
        lines.append(f"{'='*70}")
        lines.append(f"🤖 Dev-AID Router Response ({mode.upper()} mode)")
        lines.append(f"{'='*70}\n")

        # Mode-specific information
        if mode == "ensemble":
            task_type = result.get("task_type", "unknown")
            explanation = result.get("explanation", "")
            selected_model = result.get("selected_model", "unknown")

            lines.append(f"📊 Task Classification: {task_type}")
            lines.append(f"🎯 Explanation: {explanation}")
            lines.append(f"🤖 Selected Model: {selected_model}")

            if result.get("used_fallback"):
                lines.append("⚠️  Note: Used fallback model")

            lines.append("")

        elif mode == "challenger" and result.get("challenged"):
            primary = result.get("primary_model", "unknown")
            challenger = result.get("challenger_model", "unknown")
            issues_found = result.get("issues_found", False)

            lines.append("⚔️  Challenger Mode Workflow:")
            lines.append(f"   Primary Model: {primary}")
            lines.append(f"   Challenger Model: {challenger}")
            lines.append(f"   Issues Found: {'Yes' if issues_found else 'No'}")

            if result.get("refined"):
                lines.append("   ✨ Solution Refined")

            lines.append("")

        # Main response
        lines.append("📝 Response:")
        lines.append("-" * 70)
        lines.append(response)
        lines.append("-" * 70)
        lines.append("")

        # Metrics
        if verbose:
            tokens = result.get("tokens_used", {})
            cost = result.get("cost", 0.0)
            latency = result.get("latency_ms", 0.0)

            lines.append("📊 Metrics:")
            lines.append(f"   Cost: ${cost:.4f}")
            lines.append(
                f"   Tokens: {tokens.get('input', 0)} input → {tokens.get('output', 0)} output"
            )
            lines.append(f"   Latency: {latency:.0f}ms")
            lines.append("")

        # Challenger mode details
        if verbose and mode == "challenger" and result.get("challenged"):
            lines.append("\n" + "=" * 70)
            lines.append("🔍 Challenger Review:")
            lines.append("=" * 70)
            lines.append(result.get("challenger_review", "No review available"))
            lines.append("")

        return "\n".join(lines)


def execute_request(
    request: str,
    mode: Optional[str] = None,
    context_size: int = 0,
    verbose: bool = False,
    use_mcp: bool = True,
    dev_aid_root: Optional[Path] = None,
    **kwargs: Any,
) -> str:
    """
    Convenience function to execute a request and return formatted output

    Args:
        request: User request
        mode: Orchestration mode (None = use config)
        context_size: Estimated context size
        verbose: Include detailed information
        use_mcp: Whether to use MCP context gathering (default: True)
        dev_aid_root: Dev-AID root directory
        **kwargs: Additional API parameters

    Returns:
        Formatted response string
    """
    executor = RouterExecutor(dev_aid_root, use_mcp=use_mcp)
    result = executor.execute(request, mode=mode, context_size=context_size, **kwargs)
    return executor.format_output(result, verbose=verbose)


# Example usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m router.executor '<request>' [mode]")
        print("Example: python -m router.executor 'Implement user authentication' ensemble")
        sys.exit(1)

    request = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        output = execute_request(request, mode=mode, verbose=True)
        print(output)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
