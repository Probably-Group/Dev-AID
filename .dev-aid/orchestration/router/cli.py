"""
CLI Interface for Dev-AID Router

Provides command-line access to router functionality:
- execute: Execute a request
- status: Show router status
- test: Test configuration
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Any, cast

from pydantic import ValidationError

from .config_loader import load_config
from .dashboard import render_dashboard
from .executor import RouterExecutor, execute_request
from .mcp_registry import MCPRegistry
from .validators import ExecuteRequest

# Configure secure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)


class SafeError(Exception):
    """Error that is safe to display to users"""


def cmd_execute(args: Any) -> int:
    """Execute a request with routing"""
    try:
        # Validate inputs with Pydantic
        try:
            validated_request = ExecuteRequest(
                request=args.request,
                mode=args.mode,
                context_size=args.context_size,
                use_mcp=not args.no_mcp if hasattr(args, "no_mcp") else True,
            )
        except ValidationError as e:
            # Safe error message - don't leak validation details
            error_msg = "Invalid request parameters. Please check your input."
            logger.error(f"Validation error: {e}")
            raise SafeError(error_msg)

        output = execute_request(
            request=validated_request.request,
            mode=validated_request.mode,
            context_size=validated_request.context_size,
            verbose=args.verbose,
            use_mcp=validated_request.use_mcp,
            dev_aid_root=Path(args.root) if args.root else None,
        )
        print(output)
        return 0
    except SafeError as e:
        # Safe to display
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        # Log full error, show safe message
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(
            "❌ An unexpected error occurred. Please check logs for details.",
            file=sys.stderr,
        )
        return 1


def cmd_status(args: Any) -> int:
    """Show router status"""
    try:
        executor = RouterExecutor(Path(args.root) if args.root else None)
        status = executor.get_status()

        # Format status output
        print("=" * 70)
        print("🚀 Dev-AID Router Status")
        print("=" * 70)
        print()

        # Current configuration
        print(f"⚙️  Current Mode: {status['current_mode'].upper()}")
        print()

        # Mode info
        mode_info = status["mode_info"]
        print("📋 Mode Configuration:")
        for key, value in mode_info.items():
            if key != "mode":
                print(f"   {key}: {value}")
        print()

        # Budget
        budget = status["budget"]
        print("💰 Budget Status:")
        print(f"   Daily Limit: ${budget['daily_limit']:.2f}")
        print(f"   Used Today: ${budget['used']:.4f} ({budget['percentage']:.1f}%)")
        print(f"   Remaining: ${budget['remaining']:.4f}")
        print(f"   Status: {'❌ OVER BUDGET' if budget['over_budget'] else '✅ Under budget'}")
        print()

        # Today's stats
        today = status["today"]
        print("📊 Today's Activity:")
        print(f"   Total Cost: ${today['cost']:.4f}")
        print(f"   Requests: {today['requests']}")
        print(f"   Average Cost: ${today['average_cost']:.4f}")
        print()

        # Per-model stats
        if status["models"]:
            print("🤖 Models Used Today:")
            for model, stats in status["models"].items():
                print(f"   {model}:")
                print(f"      Calls: {stats['calls']}")
                print(f"      Cost: ${stats['cost']:.4f}")
                print(f"      Tokens: {stats['tokens_input']}→{stats['tokens_output']}")
            print()

        # Recent decisions
        if args.history:
            recent = status["recent_decisions"]
            if recent:
                print("📝 Recent Routing Decisions:")
                for decision in reversed(recent[-10:]):
                    timestamp = decision["timestamp"].split(".")[0]  # Remove microseconds
                    print(
                        f"   [{timestamp}] {decision['mode']:10} → {decision['model']:15} ${decision['cost']:.4f}"
                    )
                print()

        return 0

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


def cmd_test(args: Any) -> int:
    """Test configuration"""
    try:
        print("🔍 Testing Dev-AID Router Configuration...\n")

        # Load config
        config = load_config(Path(args.root) if args.root else None)
        print("✅ Configuration loaded successfully")
        print(f"   Root: {config.root}")
        print(f"   Mode: {config.get_orchestration_mode()}")
        print()

        # Test providers
        print("🔌 Testing Providers:")
        enabled_providers = config.get_enabled_providers()

        for provider in enabled_providers:
            is_valid, error = config.validate_provider(provider)

            if is_valid:
                print(f"   ✅ {provider:10} - Ready")
            else:
                print(f"   ❌ {provider:10} - {error}")

        print()

        # Test modes
        print("🎭 Available Modes:")
        modes = ["solo", "ensemble", "challenger"]

        for mode in modes:
            mode_config = config.get_mode_config(mode)
            enabled = mode_config.get("enabled", True)
            status_icon = "✅" if enabled else "❌"
            print(
                f"   {status_icon} {mode:10} - {mode_config.get('description', 'No description')}"
            )

        print()

        # Memory bank
        print("📚 Memory Bank:")
        memory_path = config.get_memory_bank_path()
        auto_load = config.get_memory_bank_files()

        for filename in auto_load:
            filepath = memory_path / filename
            exists = filepath.exists()
            status_icon = "✅" if exists else "❌"
            print(f"   {status_icon} {filename}")

        print()
        print("✅ Configuration test complete!")

        return 0

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


def cmd_auth_status(args: Any) -> int:
    """Show authentication status for all providers"""
    try:
        print("🔐 Authentication Status for Dev-AID Router\n")
        print("=" * 90)

        # Detect authentication for all providers
        from .auth_detector import AuthDetector

        auth_detector = AuthDetector()
        detected_auth = auth_detector.detect_all()

        # Get all configured providers
        all_providers = ["claude", "gemini", "openai"]

        print(f"{'Provider':<15} {'Status':<15} {'Auth Type':<15} {'Source':<45}")
        print("=" * 90)

        for provider in all_providers:
            auth = detected_auth.get(provider)

            if auth:
                status = "✅ Authenticated"
                auth_type = auth.auth_type.upper()
                source = auth.source

                # Truncate long source paths
                if len(source) > 43:
                    source = "..." + source[-40:]

                print(f"{provider:<15} {status:<15} {auth_type:<15} {source:<45}")
            else:
                status = "❌ No Auth"
                auth_type = "-"
                source = "Not configured"
                print(f"{provider:<15} {status:<15} {auth_type:<15} {source:<45}")

        print()
        print("🔑 Authentication Types:")
        print("   SESSION  - Authenticated via CLI (claude login, gcloud auth)")
        print("   API_KEY  - Using API key from environment variable")
        print("   ADC      - Using Google Application Default Credentials")
        print()
        print("💡 Tips:")
        print("   - Claude: Run 'claude login' or set ANTHROPIC_API_KEY")
        print("   - Gemini: Run 'gcloud auth application-default login' or set GOOGLE_API_KEY")
        print("   - OpenAI: Set OPENAI_API_KEY (API key only)")
        print()
        print("   Note: ChatGPT Plus does NOT include API access!")
        print()

        return 0

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


def cmd_dashboard(args: Any) -> int:
    """Show rich TUI cost analytics dashboard"""
    try:
        root = Path(args.root) if args.root else None

        # Resolve root
        if root is None:
            cwd = Path.cwd()
            root = cwd
            while root != root.parent:
                if (root / ".dev-aid").is_dir():
                    break
                root = root.parent

        logs_dir = root / ".dev-aid" / "logs"
        if not logs_dir.exists():
            print(
                "No logs directory found. Run some router requests first.",
                file=sys.stderr,
            )
            return 1

        from .cost_tracker import CostTracker

        tracker = CostTracker(logs_dir)

        # Determine budget
        daily_limit = args.budget
        if daily_limit is None:
            try:
                config = load_config(root)
                daily_limit = config.get_cost_limit()
            except Exception:
                daily_limit = 100.0

        render_dashboard(tracker, daily_limit=daily_limit, history_days=args.days)
        return 0

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


def cmd_mcp_discover(args: Any) -> int:
    """Discover available MCP servers"""
    try:
        print("🔍 Discovering MCP servers...\n")

        registry = MCPRegistry()
        servers = registry.discover_all()

        if not servers:
            print("❌ No MCP servers found")
            print("\nTo add MCP servers:")
            print("  - Claude Code: Use 'claude mcp add <name> ...'")
            print("  - Gemini CLI: Edit ~/.gemini/mcp.json")
            return 1

        print(f"Found {len(servers)} MCP server(s):\n")
        print("=" * 90)
        print(f"{'Status':<12} {'Name':<20} {'Source':<10} {'Capabilities':<40}")
        print("=" * 90)

        for name, server in servers.items():
            status = "✓ Enabled" if server.enabled_for_router else "  Disabled"
            capabilities = ", ".join(server.capabilities) if server.capabilities else "unknown"
            print(f"{status:<12} {name:<20} {server.source:<10} {capabilities:<40}")

        print("\nTo enable/disable servers for router use:")
        print("  router-cli.sh mcp enable <name>")
        print("  router-cli.sh mcp disable <name>")

        return 0

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


def cmd_mcp_enable(args: Any) -> int:
    """Enable MCP server for router"""
    try:
        registry = MCPRegistry()
        registry.discover_all()

        if args.name not in registry.servers:
            print(f"❌ MCP server '{args.name}' not found")
            print("\nRun 'mcp discover' to see available servers")
            return 1

        if registry.enable_server(args.name):
            server = registry.servers[args.name]
            caps = ", ".join(server.capabilities) if server.capabilities else "unknown capabilities"
            print(f"✅ Enabled '{args.name}' for router use")
            print(f"   Source: {server.source}")
            print(f"   Capabilities: {caps}")
            print("\nThe router will now use this MCP server to gather context.")
            return 0
        else:
            print(f"❌ Failed to enable '{args.name}'")
            return 1

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


def cmd_mcp_disable(args: Any) -> int:
    """Disable MCP server for router"""
    try:
        registry = MCPRegistry()
        registry.discover_all()

        if args.name not in registry.servers:
            print(f"❌ MCP server '{args.name}' not found")
            return 1

        if registry.disable_server(args.name):
            print(f"✅ Disabled '{args.name}' for router use")
            print("   The server is still installed, just not used by router")
            return 0
        else:
            print(f"❌ Failed to disable '{args.name}'")
            return 1

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


def cmd_mcp_list(args: Any) -> int:
    """List MCP servers"""
    try:
        registry = MCPRegistry()
        registry.discover_all()

        print(registry.get_summary())
        return 0

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


def cmd_mcp_sync(args: Any) -> int:
    """Re-scan and sync MCP configuration"""
    try:
        print("🔄 Syncing MCP configuration...\n")

        registry = MCPRegistry()
        servers = registry.sync()

        print("✅ Sync complete!")
        print(f"   Discovered: {len(servers)} server(s)")
        print(f"   Enabled: {len(registry.get_enabled_servers())} server(s)")
        print("\nRun 'mcp list' to see details")

        return 0

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Dev-AID Router - Multi-AI Orchestration CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Execute with default mode
  python -m router.cli execute "Implement user authentication"

  # Execute with specific mode
  python -m router.cli execute "Analyze codebase" --mode ensemble

  # Show status
  python -m router.cli status

  # Show status with history
  python -m router.cli status --history

  # Test configuration
  python -m router.cli test

  # Check authentication status
  python -m router.cli auth-status
        """,
    )

    parser.add_argument(
        "--root",
        help="Dev-AID root directory (auto-detected if not specified)",
        default=None,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Execute command
    execute_parser = subparsers.add_parser("execute", help="Execute a request")
    execute_parser.add_argument("request", help="User request to execute")
    execute_parser.add_argument(
        "--mode",
        choices=["solo", "ensemble", "challenger"],
        help="Orchestration mode (overrides config)",
    )
    execute_parser.add_argument(
        "--context-size", type=int, default=0, help="Estimated context size in tokens"
    )
    execute_parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    execute_parser.add_argument(
        "--no-mcp",
        action="store_true",
        help="Disable MCP context gathering (default: MCP enabled)",
    )
    execute_parser.set_defaults(func=cmd_execute)

    # Status command
    status_parser = subparsers.add_parser("status", help="Show router status")
    status_parser.add_argument(
        "--history", action="store_true", help="Include recent routing decisions"
    )
    status_parser.set_defaults(func=cmd_status)

    # Test command
    test_parser = subparsers.add_parser("test", help="Test configuration")
    test_parser.set_defaults(func=cmd_test)

    # Dashboard command
    dashboard_parser = subparsers.add_parser(
        "dashboard", help="Show rich TUI cost analytics dashboard"
    )
    dashboard_parser.add_argument(
        "--days", type=int, default=7, help="Number of days for history (default: 7)"
    )
    dashboard_parser.add_argument(
        "--budget",
        type=float,
        default=None,
        help="Daily budget override (default: from config)",
    )
    dashboard_parser.set_defaults(func=cmd_dashboard)

    # Auth status command
    auth_status_parser = subparsers.add_parser(
        "auth-status", help="Show authentication status for all providers"
    )
    auth_status_parser.set_defaults(func=cmd_auth_status)

    # MCP commands
    mcp_parser = subparsers.add_parser("mcp", help="Manage MCP server integration")
    mcp_subparsers = mcp_parser.add_subparsers(dest="mcp_command", help="MCP sub-command")

    # mcp discover
    mcp_discover_parser = mcp_subparsers.add_parser(
        "discover", help="Discover available MCP servers"
    )
    mcp_discover_parser.set_defaults(func=cmd_mcp_discover)

    # mcp enable
    mcp_enable_parser = mcp_subparsers.add_parser("enable", help="Enable MCP server for router")
    mcp_enable_parser.add_argument("name", help="Name of MCP server to enable")
    mcp_enable_parser.set_defaults(func=cmd_mcp_enable)

    # mcp disable
    mcp_disable_parser = mcp_subparsers.add_parser("disable", help="Disable MCP server for router")
    mcp_disable_parser.add_argument("name", help="Name of MCP server to disable")
    mcp_disable_parser.set_defaults(func=cmd_mcp_disable)

    # mcp list
    mcp_list_parser = mcp_subparsers.add_parser("list", help="List all MCP servers")
    mcp_list_parser.set_defaults(func=cmd_mcp_list)

    # mcp sync
    mcp_sync_parser = mcp_subparsers.add_parser("sync", help="Re-scan and sync MCP configuration")
    mcp_sync_parser.set_defaults(func=cmd_mcp_sync)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return cast(int, args.func(args))


if __name__ == "__main__":
    sys.exit(main())
