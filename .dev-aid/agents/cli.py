"""
CLI entry point for Dev-AID Agent framework.

Provides subcommands for each built-in agent with provider/model overrides,
dry-run mode, and verbose output.
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from .agents.ci_fixer import CI_FIXER
from .agents.conflict_resolver import CONFLICT_RESOLVER
from .agents.onboarding_agent import ONBOARDING_AGENT
from .agents.pr_reviewer import PR_REVIEWER
from .agents.research_agent import RESEARCH_AGENT
from .agents.tech_debt_hunter import TECH_DEBT_HUNTER
from .agents.test_generator import TEST_GENERATOR
from .core.agent_runner import AgentRunner
from .core.models import AgentDefinition, ToolCall
from .core.provider_adapter import ProviderResponse, create_adapter
from .core.safety import SafetyConfig
from .core.skill_loader import SkillLoader
from .core.tool_registry import ToolRegistry
from .tools import bash_tool, file_tools, git_tools, github_tools, search_tools

logger = logging.getLogger(__name__)

# ── Agent Registry ────────────────────────────────────────────────────

AGENTS: Dict[str, AgentDefinition] = {
    "pr-reviewer": PR_REVIEWER,
    "test-generator": TEST_GENERATOR,
    "tech-debt-hunter": TECH_DEBT_HUNTER,
    "ci-fixer": CI_FIXER,
    "conflict-resolver": CONFLICT_RESOLVER,
    "research": RESEARCH_AGENT,
    "onboarding": ONBOARDING_AGENT,
}


# ── Colors ────────────────────────────────────────────────────────────


class Colors:
    """ANSI color codes for terminal output."""

    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    CYAN = "\033[36m"
    BLUE = "\033[34m"
    RESET = "\033[0m"


def _supports_color() -> bool:
    """Check if the terminal supports color."""
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _c(color: str, text: str) -> str:
    """Colorize text if terminal supports it."""
    if _supports_color():
        return f"{color}{text}{Colors.RESET}"
    return text


# ── Tool Registration ─────────────────────────────────────────────────


def _build_registry(safety: SafetyConfig) -> ToolRegistry:
    """Register all built-in tools."""
    registry = ToolRegistry(safety=safety)

    # File tools
    for defn in file_tools.ALL_DEFINITIONS:
        handler = getattr(file_tools, defn.name)
        registry.register(defn, handler)

    # Bash tool
    registry.register(bash_tool.RUN_BASH_DEFINITION, bash_tool.run_bash)

    # Git tools
    for defn in git_tools.ALL_DEFINITIONS:
        handler = getattr(git_tools, defn.name)
        registry.register(defn, handler)

    # GitHub tools
    for defn in github_tools.ALL_DEFINITIONS:
        handler = getattr(github_tools, defn.name)
        registry.register(defn, handler)

    # Search tools
    for defn in search_tools.ALL_DEFINITIONS:
        handler = getattr(search_tools, defn.name)
        registry.register(defn, handler)

    return registry


# ── CLI Argument Parsing ──────────────────────────────────────────────


def _find_dev_aid_root() -> Path:
    """Find the .dev-aid directory from current working directory upward."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".dev-aid").is_dir():
            return current
        current = current.parent
    # Fallback to cwd
    return Path.cwd()


def _load_config(root: Path) -> Dict[str, Any]:
    """Load agents.json config."""
    config_path = root / ".dev-aid" / "config" / "agents.json"
    if config_path.is_file():
        return json.loads(config_path.read_text())  # type: ignore[no-any-return]
    return {}


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="dev-aid-agent",
        description="Dev-AID Agent Framework — Autonomous AI agents powered by expert skills",
    )

    # Global options
    parser.add_argument(
        "--provider",
        choices=["anthropic", "google", "openai", "local"],
        help="Override provider",
    )
    parser.add_argument("--model", help="Override model name")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show actions without making changes"
    )
    parser.add_argument("--verbose", action="store_true", help="Show tool call details")
    parser.add_argument("--json", action="store_true", dest="json_output", help="JSON output")
    parser.add_argument("--max-iterations", type=int, help="Override max iterations")

    subparsers = parser.add_subparsers(dest="agent", help="Agent to run")

    # PR Reviewer
    pr = subparsers.add_parser("pr-reviewer", help="Review a pull request")
    pr.add_argument("--pr", type=int, required=True, help="PR number")

    # Test Generator
    tg = subparsers.add_parser("test-generator", help="Generate tests for code")
    tg.add_argument("--path", required=True, help="File or directory to generate tests for")
    tg.add_argument(
        "--framework",
        choices=["pytest", "jest", "vitest"],
        default="pytest",
        help="Test framework",
    )

    # Tech Debt Hunter
    td = subparsers.add_parser("tech-debt-hunter", help="Scan for technical debt")
    td.add_argument(
        "--severity",
        choices=["low", "medium", "high", "critical"],
        default="medium",
        help="Minimum severity to report",
    )
    td.add_argument("--path", help="Directory to scan (default: project root)")

    # CI Fixer
    ci = subparsers.add_parser("ci-fixer", help="Fix CI failures")
    ci.add_argument("--run-id", help="CI run ID to investigate")
    ci.add_argument("--pr", type=int, help="PR number with failing CI")

    # Conflict Resolver
    cr = subparsers.add_parser("conflict-resolver", help="Resolve merge conflicts")
    cr.add_argument("--pr", type=int, help="PR number with conflicts")
    cr.add_argument(
        "--strategy",
        choices=["smart", "ours", "theirs"],
        default="smart",
        help="Resolution strategy",
    )

    # Research
    rs = subparsers.add_parser("research", help="Deep research on a topic")
    rs.add_argument("--topic", required=True, help="Research topic")
    rs.add_argument(
        "--depth",
        choices=["quick", "standard", "deep"],
        default="standard",
        help="Research depth",
    )

    # Onboarding
    ob = subparsers.add_parser("onboarding", help="Generate onboarding guide")
    ob.add_argument("--path", help="Project root to analyze (default: auto-detect)")

    return parser


def _build_user_message(agent_name: str, args: argparse.Namespace) -> str:
    """Build the user message from CLI arguments."""
    if agent_name == "pr-reviewer":
        return f"Review pull request #{args.pr}. Provide a thorough code review."

    elif agent_name == "test-generator":
        return (
            f"Generate {args.framework} tests for the code at: {args.path}\n"
            f"Follow existing test patterns in the project."
        )

    elif agent_name == "tech-debt-hunter":
        path = args.path or "the project"
        return (
            f"Scan {path} for technical debt.\n"
            f"Report issues at severity {args.severity} or higher."
        )

    elif agent_name == "ci-fixer":
        parts = ["Diagnose and fix the CI failure."]
        if args.run_id:
            parts.append(f"CI run ID: {args.run_id}")
        if args.pr:
            parts.append(f"PR #{args.pr}")
        return " ".join(parts)

    elif agent_name == "conflict-resolver":
        msg = "Resolve all merge conflicts in the current branch."
        if args.pr:
            msg = f"Resolve merge conflicts in PR #{args.pr}."
        msg += f" Strategy: {args.strategy}"
        return msg

    elif agent_name == "research":
        depth_map = {"quick": 5, "standard": 15, "deep": 30}
        return (
            f"Research topic: {args.topic}\n"
            f"Depth: {args.depth} (aim for ~{depth_map[args.depth]} minutes of analysis)"
        )

    elif agent_name == "onboarding":
        return "Generate a comprehensive onboarding guide for this codebase."

    return "Execute the agent task."


# ── Main Entry Point ──────────────────────────────────────────────────


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.agent:
        parser.print_help()
        return 1

    if args.agent not in AGENTS:
        print(_c(Colors.RED, f"Unknown agent: {args.agent}"), file=sys.stderr)
        return 1

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(level=log_level, format="%(name)s: %(message)s")

    agent_def = AGENTS[args.agent]

    # Apply CLI overrides
    if args.max_iterations:
        agent_def.max_iterations = args.max_iterations

    # Setup
    root = _find_dev_aid_root()
    config = _load_config(root)
    defaults = config.get("defaults", {})

    provider = args.provider or defaults.get("provider", "anthropic")
    model = args.model or defaults.get("model", "claude-sonnet-4-5-20250929")

    # Safety config
    safety = SafetyConfig(
        dry_run=args.dry_run,
        allowed_tools=set(agent_def.tools) if agent_def.tools else None,
    )

    # Build components
    registry = _build_registry(safety)

    skills_root = root / ".dev-aid" / "skills"
    skill_loader = SkillLoader(skills_root) if skills_root.is_dir() else None

    # Resolve API key
    api_key = _resolve_api_key(provider)

    adapter = create_adapter(
        provider=provider,
        api_key=api_key,
        base_url=defaults.get("base_url"),
    )

    # Progress callbacks
    def on_tool_call(tc: ToolCall) -> None:
        if args.verbose:
            print(_c(Colors.DIM, f"  -> {tc.name}({json.dumps(tc.arguments)[:100]})"))

    def on_iteration(n: int, resp: ProviderResponse) -> None:
        if not args.json_output:
            status = "tool_use" if resp.tool_calls else "thinking"
            tools_str = ", ".join(tc.name for tc in resp.tool_calls) if resp.tool_calls else ""
            print(
                _c(Colors.DIM, f"  [{n}/{agent_def.max_iterations}] {status}")
                + (_c(Colors.CYAN, f" ({tools_str})") if tools_str else "")
            )

    runner = AgentRunner(
        adapter=adapter,
        registry=registry,
        skill_loader=skill_loader,
        on_tool_call=on_tool_call if args.verbose else None,
        on_iteration=on_iteration,
    )

    # Print header
    if not args.json_output:
        print(_c(Colors.BOLD, f"\n{'='*60}"))
        print(_c(Colors.BOLD, f"  Dev-AID Agent: {agent_def.name}"))
        print(_c(Colors.DIM, f"  Provider: {provider} | Model: {model}"))
        if args.dry_run:
            print(_c(Colors.YELLOW, "  MODE: DRY RUN (no changes will be made)"))
        print(_c(Colors.BOLD, f"{'='*60}\n"))

    # Build user message
    user_message = _build_user_message(args.agent, args)

    # Run
    result = runner.run(
        agent_def=agent_def,
        user_message=user_message,
        model=model,
    )

    # Output
    if args.json_output:
        output = {
            "agent": result.agent_name,
            "success": result.success,
            "output": result.output,
            "metrics": {
                "tool_calls": result.tool_calls_made,
                "iterations": result.iterations,
                "tokens": result.total_tokens,
                "cost": result.total_cost,
                "latency_ms": round(result.total_latency_ms, 1),
            },
        }
        print(json.dumps(output, indent=2))
    else:
        if result.success:
            print(result.output)
            print(
                _c(
                    Colors.GREEN,
                    f"\n--- Completed in {result.iterations} iterations, "
                    f"{result.tool_calls_made} tool calls, "
                    f"{result.total_latency_ms/1000:.1f}s ---",
                )
            )
        else:
            print(_c(Colors.RED, f"Agent failed: {result.output}"), file=sys.stderr)

    return 0 if result.success else 1


def _resolve_api_key(provider: str) -> Optional[str]:
    """Resolve API key from environment variables."""
    env_map: Dict[str, str] = {
        "anthropic": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
        "google": "GOOGLE_API_KEY",
        "local": "",
    }
    env_var = env_map.get(provider, "")
    if env_var:
        return os.environ.get(env_var)
    return None


if __name__ == "__main__":
    sys.exit(main())
