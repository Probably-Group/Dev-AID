"""
CLI Interface for Dev-AID Router

Provides command-line access to router functionality:
- execute: Execute a request
- status: Show router status
- test: Test configuration
"""

import sys
from pathlib import Path
from typing import Optional
import argparse
from .executor import RouterExecutor, execute_request
from .config_loader import load_config


def cmd_execute(args):
    """Execute a request with routing"""
    try:
        output = execute_request(
            request=args.request,
            mode=args.mode,
            context_size=args.context_size,
            verbose=args.verbose,
            dev_aid_root=Path(args.root) if args.root else None
        )
        print(output)
        return 0
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


def cmd_status(args):
    """Show router status"""
    try:
        executor = RouterExecutor(Path(args.root) if args.root else None)
        status = executor.get_status()

        # Format status output
        print("="*70)
        print("🚀 Dev-AID Router Status")
        print("="*70)
        print()

        # Current configuration
        print(f"⚙️  Current Mode: {status['current_mode'].upper()}")
        print()

        # Mode info
        mode_info = status['mode_info']
        print(f"📋 Mode Configuration:")
        for key, value in mode_info.items():
            if key != "mode":
                print(f"   {key}: {value}")
        print()

        # Budget
        budget = status['budget']
        print(f"💰 Budget Status:")
        print(f"   Daily Limit: ${budget['daily_limit']:.2f}")
        print(f"   Used Today: ${budget['used']:.4f} ({budget['percentage']:.1f}%)")
        print(f"   Remaining: ${budget['remaining']:.4f}")
        print(f"   Status: {'❌ OVER BUDGET' if budget['over_budget'] else '✅ Under budget'}")
        print()

        # Today's stats
        today = status['today']
        print(f"📊 Today's Activity:")
        print(f"   Total Cost: ${today['cost']:.4f}")
        print(f"   Requests: {today['requests']}")
        print(f"   Average Cost: ${today['average_cost']:.4f}")
        print()

        # Per-model stats
        if status['models']:
            print(f"🤖 Models Used Today:")
            for model, stats in status['models'].items():
                print(f"   {model}:")
                print(f"      Calls: {stats['calls']}")
                print(f"      Cost: ${stats['cost']:.4f}")
                print(f"      Tokens: {stats['tokens_input']}→{stats['tokens_output']}")
            print()

        # Recent decisions
        if args.history:
            recent = status['recent_decisions']
            if recent:
                print(f"📝 Recent Routing Decisions:")
                for decision in reversed(recent[-10:]):
                    timestamp = decision['timestamp'].split('.')[0]  # Remove microseconds
                    print(f"   [{timestamp}] {decision['mode']:10} → {decision['model']:15} ${decision['cost']:.4f}")
                print()

        return 0

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


def cmd_test(args):
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
            print(f"   {status_icon} {mode:10} - {mode_config.get('description', 'No description')}")

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


def main():
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
        """
    )

    parser.add_argument(
        "--root",
        help="Dev-AID root directory (auto-detected if not specified)",
        default=None
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Execute command
    execute_parser = subparsers.add_parser("execute", help="Execute a request")
    execute_parser.add_argument("request", help="User request to execute")
    execute_parser.add_argument(
        "--mode",
        choices=["solo", "ensemble", "challenger"],
        help="Orchestration mode (overrides config)"
    )
    execute_parser.add_argument(
        "--context-size",
        type=int,
        default=0,
        help="Estimated context size in tokens"
    )
    execute_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output"
    )
    execute_parser.set_defaults(func=cmd_execute)

    # Status command
    status_parser = subparsers.add_parser("status", help="Show router status")
    status_parser.add_argument(
        "--history",
        action="store_true",
        help="Include recent routing decisions"
    )
    status_parser.set_defaults(func=cmd_status)

    # Test command
    test_parser = subparsers.add_parser("test", help="Test configuration")
    test_parser.set_defaults(func=cmd_test)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
