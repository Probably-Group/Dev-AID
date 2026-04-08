"""
CLI entry point for Dev-AID Agent framework.

Provides subcommands for each built-in agent with provider/model overrides,
dry-run mode, and verbose output. Also supports multi-agent team execution.
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from .agents.ci_fixer import CI_FIXER
from .agents.conflict_resolver import CONFLICT_RESOLVER
from .agents.doc_auditor import DOC_AUDITOR
from .agents.dod_gate import DOD_GATE
from .agents.onboarding_agent import ONBOARDING_AGENT
from .agents.pr_reviewer import PR_REVIEWER
from .agents.research_agent import RESEARCH_AGENT
from .agents.tech_debt_hunter import TECH_DEBT_HUNTER
from .agents.test_generator import TEST_GENERATOR
from .core.agent_runner import AgentRunner
from .core.apo import APOConfig, APOOptimizer, get_apo_prompt_override
from .core.lessons import LessonsConfig, LessonsLedger
from .core.models import AgentDefinition, AgentResult, ToolCall
from .core.provider_adapter import ProviderResponse, create_adapter
from .core.safety import SafetyConfig
from .core.skill_loader import SkillLoader
from .core.team_models import AgentMessage, TeamDefinition
from .core.team_runner import TeamRunner
from .core.tool_registry import ToolRegistry
from .core.trace_collector import TraceCollector, TraceConfig
from .teams.builtin_teams import BUILTIN_TEAMS
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
    "doc-auditor": DOC_AUDITOR,
    "dod-gate": DOD_GATE,
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


def _apply_config_overrides(
    agent_def: AgentDefinition,
    config: Dict[str, Any],
) -> AgentDefinition:
    """Apply agents.json per-agent config overrides.

    Returns a new AgentDefinition with overrides applied,
    without mutating the original singleton.
    """
    agent_config = config.get("agents", {}).get(agent_def.name, {})
    if not agent_config:
        return agent_def

    overrides: Dict[str, Any] = {}
    if "max_iterations" in agent_config:
        overrides["max_iterations"] = agent_config["max_iterations"]
    if "temperature" in agent_config:
        overrides["temperature"] = agent_config["temperature"]
    if "risk_level" in agent_config:
        overrides["risk_level"] = agent_config["risk_level"]

    if overrides:
        return agent_def.copy(**overrides)
    return agent_def


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
    parser.add_argument(
        "--json", action="store_true", dest="json_output", help="JSON output"
    )
    parser.add_argument("--max-iterations", type=int, help="Override max iterations")
    parser.add_argument(
        "--trace", action="store_true", help="Enable execution trace collection"
    )
    parser.add_argument(
        "--trace-dir",
        type=str,
        help="Directory for trace files (default: .dev-aid/agent-traces)",
    )
    parser.add_argument(
        "--dod",
        action="store_true",
        help="Run DoD gate after agent completes to verify output quality",
    )

    subparsers = parser.add_subparsers(dest="agent", help="Agent to run")

    # PR Reviewer
    pr = subparsers.add_parser("pr-reviewer", help="Review a pull request")
    pr.add_argument("--pr", type=int, required=True, help="PR number")

    # Test Generator
    tg = subparsers.add_parser("test-generator", help="Generate tests for code")
    tg.add_argument(
        "--path", required=True, help="File or directory to generate tests for"
    )
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

    # Doc Auditor
    da = subparsers.add_parser(
        "doc-auditor", help="Audit documentation for drift and gaps"
    )
    da.add_argument("--path", help="Project root to audit (default: auto-detect)")
    da.add_argument(
        "--scope",
        choices=["full", "docs-only", "code-only"],
        default="full",
        help="Audit scope",
    )

    # Team subcommand
    team_parser = subparsers.add_parser("team", help="Run a multi-agent team")
    team_parser.add_argument("team_name", nargs="?", help="Team name to run")
    team_parser.add_argument(
        "-m", "--message", required=False, help="Task message for the team"
    )
    team_parser.add_argument("--budget", type=float, help="Override max budget (USD)")
    team_parser.add_argument(
        "--workflow",
        choices=["parallel", "sequential", "dag"],
        help="Override workflow strategy",
    )
    team_parser.add_argument(
        "--list-teams", action="store_true", help="List available teams"
    )

    # APO subcommand
    apo_parser = subparsers.add_parser("apo", help="Automatic Prompt Optimization")
    apo_sub = apo_parser.add_subparsers(dest="apo_action", help="APO action")

    apo_opt = apo_sub.add_parser("optimize", help="Optimize an agent's prompt")
    apo_opt.add_argument("agent_name", help="Agent to optimize")
    apo_opt.add_argument(
        "--beam-width", type=int, default=3, help="Number of candidate prompts"
    )

    apo_rb = apo_sub.add_parser(
        "rollback", help="Rollback to a previous prompt version"
    )
    apo_rb.add_argument("agent_name", help="Agent to rollback")
    apo_rb.add_argument("--version", type=int, help="Specific version to rollback to")

    apo_hist = apo_sub.add_parser("history", help="Show prompt version history")
    apo_hist.add_argument("agent_name", help="Agent to show history for")

    apo_sub.add_parser("status", help="Show APO status for all agents")

    # Lessons subcommand
    lessons_parser = subparsers.add_parser(
        "lessons", help="Manage the lessons ledger (failure patterns)"
    )
    lessons_sub = lessons_parser.add_subparsers(
        dest="lessons_action", help="Lessons action"
    )

    lessons_sub.add_parser("list", help="List all active lessons")

    lessons_add = lessons_sub.add_parser("add", help="Manually add a lesson")
    lessons_add.add_argument("--agent", required=True, help="Agent name")
    lessons_add.add_argument(
        "--failure-mode", required=True, help="Short description of failure"
    )
    lessons_add.add_argument(
        "--detection-signal", required=True, help="How to detect this failure"
    )
    lessons_add.add_argument(
        "--prevention-rule", required=True, help="How to prevent this failure"
    )

    lessons_resolve = lessons_sub.add_parser(
        "resolve", help="Mark a lesson as resolved"
    )
    lessons_resolve.add_argument("lesson_id", help="Lesson ID to resolve")
    lessons_resolve.add_argument("--note", default="", help="Resolution note")

    lessons_sub.add_parser("clear-resolved", help="Remove all resolved lessons")

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

    elif agent_name == "doc-auditor":
        path = args.path or "the project"
        return (
            f"Audit documentation in {path}.\n"
            f"Scope: {args.scope}. "
            f"Check for broken links, missing docs, naming violations, "
            f"and documentation drift."
        )

    return "Execute the agent task."


# ── Main Entry Point ──────────────────────────────────────────────────


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.agent:
        parser.print_help()
        return 1

    # Handle team subcommand
    if args.agent == "team":
        return _handle_team_command(args)

    # Handle APO subcommand
    if args.agent == "apo":
        return _handle_apo_command(args)

    # Handle lessons subcommand
    if args.agent == "lessons":
        return _handle_lessons_command(args)

    if args.agent not in AGENTS:
        print(_c(Colors.RED, f"Unknown agent: {args.agent}"), file=sys.stderr)
        return 1

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(level=log_level, format="%(name)s: %(message)s")

    # Setup
    root = _find_dev_aid_root()
    config = _load_config(root)
    defaults = config.get("defaults", {})

    # Create a copy of the agent definition with config overrides
    # (never mutate the shared singleton)
    agent_def = _apply_config_overrides(AGENTS[args.agent], config)

    # Apply CLI overrides (also via copy)
    if args.max_iterations:
        agent_def = agent_def.copy(max_iterations=args.max_iterations)

    # Apply APO prompt override if available
    prompts_dir = root / ".dev-aid" / "agent-prompts"
    apo_override = get_apo_prompt_override(prompts_dir, args.agent)
    if apo_override:
        agent_def = agent_def.copy(system_prompt_extra=apo_override)
        if not getattr(args, "json_output", False):
            print(_c(Colors.DIM, "  Using APO-optimized prompt"))

    provider = args.provider or defaults.get("provider", "anthropic")
    model = args.model or defaults.get("model", "claude-sonnet-4-5-20250929")

    # Safety config with project-scoped path restrictions
    safety = SafetyConfig(
        dry_run=args.dry_run,
        allowed_tools=set(agent_def.tools) if agent_def.tools else None,
        allowed_paths=[root],  # Restrict to project root
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
            tools_str = (
                ", ".join(tc.name for tc in resp.tool_calls) if resp.tool_calls else ""
            )
            print(
                _c(Colors.DIM, f"  [{n}/{agent_def.max_iterations}] {status}")
                + (_c(Colors.CYAN, f" ({tools_str})") if tools_str else "")
            )

    # Build trace collector if enabled
    trace_collector: Optional[TraceCollector] = None
    if getattr(args, "trace", False):
        trace_dir = (
            Path(args.trace_dir)
            if args.trace_dir
            else root / ".dev-aid" / "agent-traces"
        )
        trace_config = TraceConfig(enabled=True, trace_dir=trace_dir)
        trace_collector = TraceCollector(
            config=trace_config,
            agent_name=agent_def.name,
            model=model,
        )
        if not args.json_output:
            print(_c(Colors.DIM, f"  Trace enabled → {trace_dir}/{agent_def.name}/"))

    # Build lessons ledger
    ledger_path = root / ".dev-aid" / "memory-bank" / "lessons-ledger.md"
    lessons_config = LessonsConfig(ledger_path=ledger_path)
    lessons_ledger = LessonsLedger(lessons_config)

    runner = AgentRunner(
        adapter=adapter,
        registry=registry,
        skill_loader=skill_loader,
        on_tool_call=on_tool_call if args.verbose else None,
        on_iteration=on_iteration,
        trace_collector=trace_collector,
        lessons_ledger=lessons_ledger,
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

    # Run DoD gate if requested and agent succeeded
    dod_result: Optional[AgentResult] = None
    if getattr(args, "dod", False) and result.success:
        dod_result = _run_dod_gate(
            runner=runner,
            user_message=user_message,
            agent_result=result,
            model=model,
            lessons_ledger=lessons_ledger,
            json_output=args.json_output,
        )

    # Output
    if args.json_output:
        output: Dict[str, Any] = {
            "agent": result.agent_name,
            "success": result.success,
            "output": result.output,
            "metrics": {
                "tool_calls": result.tool_calls_made,
                "iterations": result.iterations,
                "tokens": result.total_tokens,
                "cost_usd": round(result.total_cost, 6),
                "latency_ms": round(result.total_latency_ms, 1),
            },
        }
        if dod_result:
            verdict = _parse_dod_verdict(dod_result.output)
            output["dod_gate"] = {
                "verdict": verdict,
                "output": dod_result.output,
                "summary": _extract_dod_summary(dod_result.output),
            }
        print(json.dumps(output, indent=2))
    else:
        if result.success:
            print(result.output)
            cost_str = f", ${result.total_cost:.4f}" if result.total_cost > 0 else ""
            print(
                _c(
                    Colors.GREEN,
                    f"\n--- Completed in {result.iterations} iterations, "
                    f"{result.tool_calls_made} tool calls, "
                    f"{result.total_latency_ms/1000:.1f}s{cost_str} ---",
                )
            )
            if dod_result:
                verdict = _parse_dod_verdict(dod_result.output)
                color = (
                    Colors.GREEN
                    if verdict == "PASS"
                    else Colors.YELLOW if verdict == "WARN" else Colors.RED
                )
                print(_c(color, f"\n  DoD Gate: {verdict}"))
                summary = _extract_dod_summary(dod_result.output)
                if summary:
                    print(_c(Colors.DIM, f"  {summary}"))
                suggestions = _extract_dod_suggestions(dod_result.output)
                for s in suggestions:
                    print(_c(Colors.DIM, f"    - {s}"))
        else:
            print(_c(Colors.RED, f"Agent failed: {result.output}"), file=sys.stderr)

    return 0 if result.success else 1


# ── Team Execution ───────────────────────────────────────────────────


def _load_team_config(root: Path) -> Dict[str, Any]:
    """Load teams.json config."""
    config_path = root / ".dev-aid" / "config" / "teams.json"
    if config_path.is_file():
        return json.loads(config_path.read_text())  # type: ignore[no-any-return]
    return {}


def _apply_team_config(
    team_def: TeamDefinition,
    team_config: Dict[str, Any],
    args: argparse.Namespace,
) -> TeamDefinition:
    """Apply teams.json and CLI overrides to a team definition.

    Returns a new TeamDefinition without mutating the original.
    """
    from copy import deepcopy

    team = deepcopy(team_def)
    config = team_config.get("teams", {}).get(team.name, {})

    # Apply config overrides
    if "max_budget_usd" in config:
        team.max_budget_usd = float(config["max_budget_usd"])

    # Apply per-agent config overrides
    agent_configs = config.get("agents", {})
    for slot in team.agents:
        slot_config = agent_configs.get(slot.name, {})
        if "provider" in slot_config:
            slot.provider = slot_config["provider"]
        if "model" in slot_config:
            slot.model = slot_config["model"]

    # Apply CLI overrides (highest priority)
    if args.budget is not None:
        team.max_budget_usd = args.budget
    if args.workflow is not None:
        team.workflow = args.workflow

    return team


def _list_teams() -> None:
    """Print available teams."""
    print(_c(Colors.BOLD, "\nAvailable Teams:"))
    print(_c(Colors.BOLD, "=" * 60))
    for name, team in BUILTIN_TEAMS.items():
        agents_str = ", ".join(s.name for s in team.agents)
        print(f"\n  {_c(Colors.CYAN, name)}")
        print(f"    {team.description}")
        print(f"    Workflow: {team.workflow} | Agents: {agents_str}")
        print(
            f"    Budget: ${team.max_budget_usd:.2f} | Timeout: {team.timeout_seconds}s"
        )
    print()


def _handle_team_command(args: argparse.Namespace) -> int:
    """Handle the 'team' subcommand."""
    # --list-teams flag
    if args.list_teams:
        _list_teams()
        return 0

    # Validate arguments
    if not args.team_name:
        print(_c(Colors.RED, "Error: team name required"), file=sys.stderr)
        print("Use --list-teams to see available teams.", file=sys.stderr)
        return 1

    if args.team_name not in BUILTIN_TEAMS:
        print(
            _c(Colors.RED, f"Unknown team: {args.team_name}"),
            file=sys.stderr,
        )
        print(
            f"Available: {', '.join(BUILTIN_TEAMS.keys())}",
            file=sys.stderr,
        )
        return 1

    if not args.message:
        print(_c(Colors.RED, "Error: -m/--message required"), file=sys.stderr)
        return 1

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(level=log_level, format="%(name)s: %(message)s")

    # Load config and apply overrides
    root = _find_dev_aid_root()
    team_config = _load_team_config(root)
    team_def = _apply_team_config(BUILTIN_TEAMS[args.team_name], team_config, args)

    # Build API keys map
    api_keys: Dict[str, str] = {}
    for provider_name in ("anthropic", "openai", "google"):
        key = _resolve_api_key(provider_name)
        if key:
            api_keys[provider_name] = key

    # Skills
    skills_root = root / ".dev-aid" / "skills"
    skill_loader = SkillLoader(skills_root) if skills_root.is_dir() else None

    # Callbacks
    def on_agent_start(name: str) -> None:
        if not args.json_output:
            print(_c(Colors.DIM, f"  Starting agent: {name}"))

    def on_agent_complete(name: str, result: AgentResult) -> None:
        if not args.json_output:
            status = (
                _c(Colors.GREEN, "done") if result.success else _c(Colors.RED, "failed")
            )
            cost = f", ${result.total_cost:.4f}" if result.total_cost > 0 else ""
            print(f"  Agent {name}: {status}{cost}")

    def on_message(msg: AgentMessage) -> None:
        if args.verbose and not args.json_output:
            print(
                _c(
                    Colors.DIM,
                    f"  [{msg.from_agent} -> {msg.to_agent}] "
                    f"{msg.message_type}: {msg.content[:80]}",
                )
            )

    # Build trace config for team if enabled
    team_trace_config: Optional[TraceConfig] = None
    if getattr(args, "trace", False):
        trace_dir = (
            Path(args.trace_dir)
            if args.trace_dir
            else root / ".dev-aid" / "agent-traces"
        )
        team_trace_config = TraceConfig(enabled=True, trace_dir=trace_dir)
        if not args.json_output:
            print(_c(Colors.DIM, f"  Trace enabled → {trace_dir}/"))

    # Build lessons ledger for team
    ledger_path = root / ".dev-aid" / "memory-bank" / "lessons-ledger.md"
    team_lessons_config = LessonsConfig(ledger_path=ledger_path)
    team_lessons_ledger = LessonsLedger(team_lessons_config)

    # Create TeamRunner
    runner = TeamRunner(
        registry_factory=_build_registry,
        skill_loader=skill_loader,
        agents_registry=AGENTS,
        on_agent_start=on_agent_start,
        on_agent_complete=on_agent_complete,
        on_message=on_message if args.verbose else None,
        trace_config=team_trace_config,
        lessons_ledger=team_lessons_ledger,
    )

    # Print header
    if not args.json_output:
        agents_str = ", ".join(s.name for s in team_def.agents)
        print(_c(Colors.BOLD, f"\n{'='*60}"))
        print(_c(Colors.BOLD, f"  Dev-AID Team: {team_def.name}"))
        print(
            _c(
                Colors.DIM,
                f"  Agents: {agents_str}",
            )
        )
        print(
            _c(
                Colors.DIM,
                f"  Workflow: {team_def.workflow} | "
                f"Budget: ${team_def.max_budget_usd:.2f}",
            )
        )
        if args.dry_run:
            print(_c(Colors.YELLOW, "  MODE: DRY RUN"))
        print(_c(Colors.BOLD, f"{'='*60}\n"))

    # Run team
    result = asyncio.run(
        runner.run(
            team_def=team_def,
            user_message=args.message,
            api_keys=api_keys,
        )
    )

    # Output
    if args.json_output:
        output = {
            "team": result.team_name,
            "success": result.success,
            "partial": result.partial,
            "output": result.aggregated_output,
            "agents": result.agent_results,
            "metrics": {
                "agents_completed": result.tasks_completed,
                "agents_failed": result.tasks_failed,
                "tokens": result.total_tokens,
                "cost_usd": round(result.total_cost, 6),
                "latency_ms": round(result.total_latency_ms, 1),
                "messages_exchanged": result.messages_exchanged,
            },
        }
        print(json.dumps(output, indent=2))
    else:
        print(result.aggregated_output)
        cost_str = f"${result.total_cost:.4f}" if result.total_cost > 0 else "$0"
        partial_str = " (partial)" if result.partial else ""
        print(
            _c(
                Colors.GREEN if result.success else Colors.RED,
                f"\n--- {result.tasks_completed}/{result.tasks_completed + result.tasks_failed}"
                f" agents completed{partial_str}, "
                f"{result.total_latency_ms/1000:.1f}s, {cost_str} ---",
            )
        )

    return 0 if result.success else 1


def _handle_apo_command(args: argparse.Namespace) -> int:
    """Handle the 'apo' subcommand."""
    action = getattr(args, "apo_action", None)
    if not action:
        print(_c(Colors.RED, "Error: APO action required"), file=sys.stderr)
        print(
            "Usage: dev-aid-agent apo {optimize|rollback|history|status}",
            file=sys.stderr,
        )
        return 1

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(level=log_level, format="%(name)s: %(message)s")

    root = _find_dev_aid_root()
    config = _load_config(root)
    defaults = config.get("defaults", {})

    apo_config = APOConfig(
        traces_dir=root / ".dev-aid" / "agent-traces",
        prompts_dir=root / ".dev-aid" / "agent-prompts",
        golden_tests_path=root / ".dev-aid" / "config" / "golden-tests.json",
        memory_bank_path=root / ".dev-aid" / "memory-bank",
    )

    if action == "status":
        # Status doesn't need an adapter
        optimizer = APOOptimizer(config=apo_config, adapter=None)  # type: ignore[arg-type]
        print(optimizer.status(AGENTS))
        return 0

    # Actions that need agent_name
    agent_name = getattr(args, "agent_name", None)
    if not agent_name:
        print(_c(Colors.RED, "Error: agent name required"), file=sys.stderr)
        return 1

    if action == "history":
        optimizer = APOOptimizer(config=apo_config, adapter=None)  # type: ignore[arg-type]
        versions = optimizer.history(agent_name)
        if not versions:
            print(f"No prompt versions found for '{agent_name}'.")
            return 0
        print(_c(Colors.BOLD, f"\nPrompt History: {agent_name}"))
        print("=" * 50)
        for v in versions:
            score_str = f", score={v.score:.2f}" if v.score is not None else ""
            parent_str = f" (from v{v.parent_version})" if v.parent_version else ""
            print(
                f"  v{v.version:03d} | {v.source}{parent_str}{score_str} | {v.created_at}"
            )
        return 0

    if action == "rollback":
        optimizer = APOOptimizer(config=apo_config, adapter=None)  # type: ignore[arg-type]
        to_version = getattr(args, "version", None)
        success = optimizer.rollback(agent_name, to_version)
        return 0 if success else 1

    if action == "optimize":
        if agent_name not in AGENTS:
            print(_c(Colors.RED, f"Unknown agent: {agent_name}"), file=sys.stderr)
            return 1

        provider = args.provider or defaults.get("provider", "anthropic")
        api_key = _resolve_api_key(provider)
        adapter = create_adapter(provider=provider, api_key=api_key)

        beam_width = getattr(args, "beam_width", 3)
        apo_config.beam_width = beam_width

        optimizer = APOOptimizer(config=apo_config, adapter=adapter)
        agent_def = AGENTS[agent_name]

        print(_c(Colors.BOLD, f"\n{'='*60}"))
        print(_c(Colors.BOLD, f"  APO: Optimizing {agent_name}"))
        print(_c(Colors.DIM, f"  Beam width: {beam_width}"))
        if args.dry_run:
            print(_c(Colors.YELLOW, "  MODE: DRY RUN"))
        print(_c(Colors.BOLD, f"{'='*60}\n"))

        result = optimizer.optimize(
            agent_name=agent_name,
            agent_def=agent_def,
            dry_run=args.dry_run,
        )
        return 0 if result else 1

    print(_c(Colors.RED, f"Unknown APO action: {action}"), file=sys.stderr)
    return 1


# ── Lessons Ledger Command ────────────────────────────────────────────


def _handle_lessons_command(args: argparse.Namespace) -> int:
    """Handle the 'lessons' subcommand."""
    action = getattr(args, "lessons_action", None)
    if not action:
        print(_c(Colors.RED, "Error: lessons action required"), file=sys.stderr)
        print(
            "Usage: dev-aid-agent lessons {list|add|resolve|clear-resolved}",
            file=sys.stderr,
        )
        return 1

    root = _find_dev_aid_root()
    ledger_path = root / ".dev-aid" / "memory-bank" / "lessons-ledger.md"
    config = LessonsConfig(ledger_path=ledger_path)
    ledger = LessonsLedger(config)

    if action == "list":
        lessons = ledger.get_lessons(include_resolved=True)
        if not lessons:
            print("No lessons recorded.")
            return 0
        print(_c(Colors.BOLD, f"\nLessons Ledger ({len(lessons)} entries)"))
        print("=" * 60)
        for lesson in lessons:
            resolved_mark = " [RESOLVED]" if lesson.resolved else ""
            print(
                f"\n  {_c(Colors.CYAN, f'LESSON-{lesson.id}')}"
                f" | {lesson.agent_name}{resolved_mark}"
            )
            print(f"    Failure: {lesson.failure_mode}")
            print(f"    Signal:  {lesson.detection_signal}")
            print(f"    Rule:    {lesson.prevention_rule}")
            print(f"    Source:  {lesson.source} | {lesson.timestamp}")
            if lesson.resolution_note:
                print(f"    Note:    {lesson.resolution_note}")
        print()
        return 0

    elif action == "add":
        agent_name = getattr(args, "agent", "")
        failure_mode = getattr(args, "failure_mode", "")
        detection_signal = getattr(args, "detection_signal", "")
        prevention_rule = getattr(args, "prevention_rule", "")
        lesson = ledger.add_lesson(
            agent_name=agent_name,
            failure_mode=failure_mode,
            detection_signal=detection_signal,
            prevention_rule=prevention_rule,
            source="manual",
        )
        print(_c(Colors.GREEN, f"Added lesson LESSON-{lesson.id}"))
        return 0

    elif action == "resolve":
        lesson_id = getattr(args, "lesson_id", "")
        note = getattr(args, "note", "")
        if ledger.mark_resolved(lesson_id, note):
            print(_c(Colors.GREEN, f"Resolved LESSON-{lesson_id}"))
            return 0
        else:
            print(
                _c(Colors.RED, f"Lesson '{lesson_id}' not found"),
                file=sys.stderr,
            )
            return 1

    elif action == "clear-resolved":
        removed = ledger.clear_resolved()
        print(_c(Colors.GREEN, f"Cleared {removed} resolved lessons"))
        return 0

    print(_c(Colors.RED, f"Unknown lessons action: {action}"), file=sys.stderr)
    return 1


# ── DoD Gate ─────────────────────────────────────────────────────────


def _run_dod_gate(
    runner: AgentRunner,
    user_message: str,
    agent_result: AgentResult,
    model: str,
    lessons_ledger: LessonsLedger,
    json_output: bool,
) -> AgentResult:
    """Run the DoD gate against a completed agent's output."""
    if not json_output:
        print(_c(Colors.DIM, "\n  Running DoD gate verification..."))

    composite_message = (
        f"## Original Request\n\n{user_message}\n\n"
        f"## Agent Output ({agent_result.agent_name})\n\n"
        f"{agent_result.output}"
    )

    dod_result = runner.run(
        agent_def=DOD_GATE,
        user_message=composite_message,
        model=model,
    )

    # Auto-create lesson on FAIL or WARN
    verdict = _parse_dod_verdict(dod_result.output)
    if verdict in ("FAIL", "WARN"):
        summary = _extract_dod_summary(dod_result.output)
        suggestions = _extract_dod_suggestions(dod_result.output)
        lessons_ledger.add_lesson(
            agent_name=agent_result.agent_name,
            failure_mode=f"dod_gate_{verdict.lower()}",
            detection_signal=summary or f"DoD gate returned {verdict}",
            prevention_rule=(
                "; ".join(suggestions)
                if suggestions
                else "Ensure output includes concrete artifacts and verification"
            ),
            source="dod-gate",
        )

    return dod_result


def _parse_dod_verdict(output: str) -> str:
    """Extract the overall verdict from DoD gate output.

    Looks for **Overall Verdict**: PASS/WARN/FAIL pattern.
    Returns "UNKNOWN" if not found.
    """
    import re

    match = re.search(
        r"\*\*Overall Verdict\*\*\s*:\s*(PASS|WARN|FAIL)",
        output,
        re.IGNORECASE,
    )
    if match:
        return match.group(1).upper()
    return "UNKNOWN"


def _extract_dod_summary(output: str) -> str:
    """Extract the summary line from DoD gate output."""
    import re

    match = re.search(
        r"\*\*Summary\*\*\s*:\s*(.+?)(?:\n|$)",
        output,
    )
    if match:
        return match.group(1).strip()
    return ""


def _extract_dod_suggestions(output: str) -> List[str]:
    """Extract suggestion bullet points from DoD gate output."""
    import re

    suggestions: List[str] = []
    in_suggestions = False
    for line in output.split("\n"):
        stripped = line.strip()
        if re.match(r"\*\*Suggestions?\*\*", stripped, re.IGNORECASE):
            in_suggestions = True
            continue
        if in_suggestions:
            if stripped.startswith("- "):
                suggestions.append(stripped[2:])
            elif stripped.startswith("#") or (
                stripped and not stripped.startswith("-")
            ):
                break
    return suggestions


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
