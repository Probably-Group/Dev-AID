"""
Multi-agent team orchestration engine.

Wraps multiple AgentRunner instances to execute teams of agents
in parallel, sequential, or DAG workflows with shared state.
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .agent_runner import AgentRunner
from .apo import get_apo_prompt_override
from .lessons import LessonsLedger
from .models import AgentDefinition, AgentResult
from .provider_adapter import create_adapter
from .safety import SafetyConfig
from .shared_state import BudgetTracker, FileLockSet, MessageBus, SharedTaskList
from .skill_loader import SkillLoader
from .team_models import AgentMessage, AgentSlot, TeamDefinition, TeamResult
from .tool_registry import ToolRegistry
from .trace_collector import TraceCollector, TraceConfig

logger = logging.getLogger(__name__)

# Max messages to inject into team context
_MAX_CONTEXT_MESSAGES = 5
# Max chars per prior agent result in context
_MAX_RESULT_CHARS = 1000


class TeamRunner:
    """Orchestrates a team of agents using shared state.

    Supports parallel, sequential, and DAG execution strategies.
    Each agent gets its own AgentRunner, ToolRegistry, and ProviderAdapter
    (allowing provider mixing within a team).
    """

    def __init__(
        self,
        registry_factory: Callable[[SafetyConfig], ToolRegistry],
        skill_loader: Optional[SkillLoader],
        agents_registry: Dict[str, AgentDefinition],
        on_agent_start: Optional[Callable[[str], None]] = None,
        on_agent_complete: Optional[Callable[[str, AgentResult], None]] = None,
        on_message: Optional[Callable[[AgentMessage], None]] = None,
        trace_config: Optional[TraceConfig] = None,
        lessons_ledger: Optional[LessonsLedger] = None,
    ) -> None:
        self._registry_factory = registry_factory
        self._skill_loader = skill_loader
        self._agents_registry = agents_registry
        self._on_agent_start = on_agent_start
        self._on_agent_complete = on_agent_complete
        self._on_message = on_message
        self._trace_config = trace_config
        self._lessons_ledger = lessons_ledger

    async def run(
        self,
        team_def: TeamDefinition,
        user_message: str,
        extra_context: str = "",
        api_keys: Optional[Dict[str, str]] = None,
    ) -> TeamResult:
        """Execute a team of agents.

        Args:
            team_def: Team definition with agents and workflow.
            user_message: The task for the team.
            extra_context: Additional context for all agents.
            api_keys: Provider-to-API-key mapping.

        Returns:
            TeamResult with aggregated output and metrics.
        """
        # perf_counter (not monotonic): see StopWatch docstring in models.py.
        # Windows time.monotonic has 15.6 ms granularity which makes short
        # team runs report 0.0 ms latency.
        start_time = time.perf_counter()
        keys = api_keys or {}

        # Initialize shared state
        task_list = SharedTaskList()
        message_bus = MessageBus()
        file_locks = FileLockSet()
        budget = BudgetTracker(max_budget_usd=team_def.max_budget_usd)

        # Subscribe to message bus for external callback
        if self._on_message:
            cb = self._on_message
            for slot in team_def.agents:
                message_bus.subscribe(slot.name, cb)

        # Dispatch to workflow strategy
        if team_def.workflow == "parallel":
            agent_results = await self._run_parallel(
                team_def,
                user_message,
                extra_context,
                keys,
                task_list,
                message_bus,
                file_locks,
                budget,
            )
        elif team_def.workflow == "sequential":
            agent_results = await self._run_sequential(
                team_def,
                user_message,
                extra_context,
                keys,
                task_list,
                message_bus,
                file_locks,
                budget,
            )
        elif team_def.workflow == "dag":
            agent_results = await self._run_dag(
                team_def,
                user_message,
                extra_context,
                keys,
                task_list,
                message_bus,
                file_locks,
                budget,
            )
        else:
            raise ValueError(f"Unknown workflow: {team_def.workflow}")

        # Aggregate results
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return self._aggregate_results(
            team_def,
            agent_results,
            message_bus,
            budget,
            elapsed_ms,
        )

    async def _run_parallel(
        self,
        team_def: TeamDefinition,
        user_message: str,
        extra_context: str,
        api_keys: Dict[str, str],
        task_list: SharedTaskList,
        message_bus: MessageBus,
        file_locks: FileLockSet,
        budget: BudgetTracker,
    ) -> Dict[str, AgentResult]:
        """Run all agents simultaneously."""
        coros = []
        for slot in team_def.agents:
            coros.append(
                self._run_single_agent(
                    slot,
                    team_def,
                    user_message,
                    extra_context,
                    api_keys,
                    task_list,
                    message_bus,
                    file_locks,
                    budget,
                    prior_results={},
                )
            )
        raw_results = await asyncio.gather(*coros, return_exceptions=True)

        results: Dict[str, AgentResult] = {}
        for slot, result in zip(team_def.agents, raw_results):
            if isinstance(result, BaseException):
                logger.error("Agent '%s' raised exception: %s", slot.name, result)
                results[slot.name] = AgentResult(
                    agent_name=slot.name,
                    success=False,
                    output=f"Agent error: {result}",
                )
            else:
                results[slot.name] = result
        return results

    async def _run_sequential(
        self,
        team_def: TeamDefinition,
        user_message: str,
        extra_context: str,
        api_keys: Dict[str, str],
        task_list: SharedTaskList,
        message_bus: MessageBus,
        file_locks: FileLockSet,
        budget: BudgetTracker,
    ) -> Dict[str, AgentResult]:
        """Run agents one after another, passing results forward."""
        results: Dict[str, AgentResult] = {}
        for slot in team_def.agents:
            if budget.is_over_budget():
                logger.warning("Budget exhausted, skipping agent '%s'", slot.name)
                results[slot.name] = AgentResult(
                    agent_name=slot.name,
                    success=False,
                    output="Skipped: budget exhausted",
                )
                continue

            result = await self._run_single_agent(
                slot,
                team_def,
                user_message,
                extra_context,
                api_keys,
                task_list,
                message_bus,
                file_locks,
                budget,
                prior_results=results,
            )
            results[slot.name] = result

            # Broadcast result as handoff message
            message_bus.send(
                AgentMessage(
                    id=AgentMessage.generate_id(),
                    from_agent=slot.name,
                    to_agent="*",
                    content=result.output[:_MAX_RESULT_CHARS],
                    message_type="handoff",
                )
            )

        return results

    async def _run_dag(
        self,
        team_def: TeamDefinition,
        user_message: str,
        extra_context: str,
        api_keys: Dict[str, str],
        task_list: SharedTaskList,
        message_bus: MessageBus,
        file_locks: FileLockSet,
        budget: BudgetTracker,
    ) -> Dict[str, AgentResult]:
        """Run agents in topological order respecting dependencies.

        Ready agents (all deps completed) run in parallel batches.
        """
        results: Dict[str, AgentResult] = {}
        slots_by_name = {s.name: s for s in team_def.agents}
        completed: set[str] = set()
        remaining = set(slots_by_name.keys())

        while remaining:
            # Find ready agents (all deps completed or no deps)
            ready = []
            for name in remaining:
                slot = slots_by_name[name]
                if all(dep in completed for dep in slot.depends_on):
                    ready.append(slot)

            if not ready:
                # Deadlock: remaining agents have unresolvable deps
                for name in remaining:
                    results[name] = AgentResult(
                        agent_name=name,
                        success=False,
                        output="Deadlocked: unresolvable dependencies",
                    )
                break

            if budget.is_over_budget():
                for slot in ready:
                    results[slot.name] = AgentResult(
                        agent_name=slot.name,
                        success=False,
                        output="Skipped: budget exhausted",
                    )
                    remaining.discard(slot.name)
                continue

            # Run ready batch in parallel
            coros = []
            for slot in ready:
                coros.append(
                    self._run_single_agent(
                        slot,
                        team_def,
                        user_message,
                        extra_context,
                        api_keys,
                        task_list,
                        message_bus,
                        file_locks,
                        budget,
                        prior_results=results,
                    )
                )
            raw = await asyncio.gather(*coros, return_exceptions=True)

            for slot, result in zip(ready, raw):
                if isinstance(result, BaseException):
                    logger.error("Agent '%s' raised: %s", slot.name, result)
                    results[slot.name] = AgentResult(
                        agent_name=slot.name,
                        success=False,
                        output=f"Agent error: {result}",
                    )
                else:
                    results[slot.name] = result

                # Broadcast result
                output = results[slot.name].output
                message_bus.send(
                    AgentMessage(
                        id=AgentMessage.generate_id(),
                        from_agent=slot.name,
                        to_agent="*",
                        content=output[:_MAX_RESULT_CHARS],
                        message_type="handoff",
                    )
                )
                completed.add(slot.name)
                remaining.discard(slot.name)

        return results

    async def _run_single_agent(
        self,
        slot: AgentSlot,
        team_def: TeamDefinition,
        user_message: str,
        extra_context: str,
        api_keys: Dict[str, str],
        task_list: SharedTaskList,
        message_bus: MessageBus,
        file_locks: FileLockSet,
        budget: BudgetTracker,
        prior_results: Dict[str, AgentResult],
    ) -> AgentResult:
        """Run a single agent within the team context.

        Wraps synchronous AgentRunner.run() in asyncio.to_thread().
        """
        if self._on_agent_start:
            self._on_agent_start(slot.name)

        # Check budget before starting
        if budget.is_over_budget():
            return AgentResult(
                agent_name=slot.name,
                success=False,
                output="Skipped: budget exhausted",
            )

        # Resolve agent definition
        agent_def = self._resolve_agent_def(slot)

        # Resolve provider and model
        provider = slot.provider or team_def.default_provider
        model = slot.model or team_def.default_model

        # Build team context
        team_context = self._build_team_context(
            slot.name,
            extra_context,
            message_bus,
            prior_results,
        )

        # Create per-agent components
        api_key = api_keys.get(provider)
        adapter = create_adapter(provider=provider, api_key=api_key)
        safety = SafetyConfig()
        registry = self._registry_factory(safety)

        # Create per-agent trace collector if tracing is enabled
        trace_collector: Optional[TraceCollector] = None
        if self._trace_config and self._trace_config.enabled:
            trace_collector = TraceCollector(
                config=self._trace_config,
                agent_name=slot.name,
                model=model,
            )

        runner = AgentRunner(
            adapter=adapter,
            registry=registry,
            skill_loader=self._skill_loader,
            trace_collector=trace_collector,
            lessons_ledger=self._lessons_ledger,
        )

        # Run in thread (AgentRunner.run is synchronous)
        result = await asyncio.to_thread(
            runner.run,
            agent_def=agent_def,
            user_message=user_message,
            model=model,
            extra_context=team_context,
        )

        # Record cost
        budget.record_cost(slot.name, result.total_cost)

        # Release file locks
        file_locks.release_all(slot.name)

        # Auto-record team agent failure as a lesson
        if (
            not result.success
            and self._lessons_ledger
            and self._lessons_ledger.config.auto_record_on_failure
        ):
            self._lessons_ledger.add_lesson(
                agent_name=slot.agent_def_name,
                failure_mode="team_agent_failure",
                detection_signal=result.output[:200],
                prevention_rule=(
                    f"Agent '{slot.name}' failed in team context. "
                    "Check agent configuration, input message, and provider."
                ),
            )

        if self._on_agent_complete:
            self._on_agent_complete(slot.name, result)

        return result

    def _resolve_agent_def(self, slot: AgentSlot) -> AgentDefinition:
        """Look up and customize an agent definition for a slot."""
        base = self._agents_registry.get(slot.agent_def_name)
        if base is None:
            raise ValueError(
                f"Agent definition '{slot.agent_def_name}' not found in registry. "
                f"Available: {list(self._agents_registry.keys())}"
            )

        overrides: Dict[str, Any] = {}

        # Apply APO prompt override if available
        if self._trace_config:
            prompts_dir = self._trace_config.trace_dir.parent / "agent-prompts"
        else:
            prompts_dir = Path(".dev-aid/agent-prompts")
        apo_override = get_apo_prompt_override(prompts_dir, slot.agent_def_name)
        if apo_override:
            overrides["system_prompt_extra"] = apo_override

        if slot.role_prompt:
            # Append role_prompt to existing system_prompt_extra
            new_prompt = overrides.get("system_prompt_extra", base.system_prompt_extra)
            if new_prompt:
                new_prompt += "\n\n"
            new_prompt += slot.role_prompt
            overrides["system_prompt_extra"] = new_prompt

        if overrides:
            return base.copy(**overrides)
        return base

    @staticmethod
    def _build_team_context(
        agent_name: str,
        extra_context: str,
        message_bus: MessageBus,
        prior_results: Dict[str, AgentResult],
    ) -> str:
        """Build extra context with team coordination info."""
        parts: List[str] = []

        if extra_context:
            parts.append(extra_context)

        # Inject prior agent results
        if prior_results:
            results_section = ["## Prior Agent Results"]
            for name, result in prior_results.items():
                status = "completed" if result.success else "failed"
                output = result.output[:_MAX_RESULT_CHARS]
                results_section.append(f"### {name} ({status})\n{output}")
            parts.append("\n".join(results_section))

        # Inject recent messages from bus
        messages = message_bus.get_messages_for(agent_name)
        if messages:
            recent = messages[-_MAX_CONTEXT_MESSAGES:]
            msg_section = ["## Team Messages"]
            for msg in recent:
                msg_section.append(
                    f"**{msg.from_agent}** [{msg.message_type}]: {msg.content}"
                )
            parts.append("\n".join(msg_section))

        return "\n\n".join(parts)

    @staticmethod
    def _aggregate_results(
        team_def: TeamDefinition,
        agent_results: Dict[str, AgentResult],
        message_bus: MessageBus,
        budget: BudgetTracker,
        elapsed_ms: float,
    ) -> TeamResult:
        """Aggregate individual agent results into a TeamResult."""
        strategy = team_def.aggregation_strategy

        # Gather metrics
        total_tokens: Dict[str, int] = {"input": 0, "output": 0}
        completed = 0
        failed = 0
        any_success = False

        for result in agent_results.values():
            total_tokens["input"] += result.total_tokens.get("input", 0)
            total_tokens["output"] += result.total_tokens.get("output", 0)
            if result.success:
                completed += 1
                any_success = True
            else:
                failed += 1

        # Build aggregated output
        if strategy == "concatenate":
            output = _aggregate_concatenate(agent_results)
        elif strategy == "merge_sections":
            output = _aggregate_merge_sections(agent_results)
        elif strategy == "vote":
            output = _aggregate_vote(agent_results)
        else:
            output = _aggregate_concatenate(agent_results)

        return TeamResult(
            team_name=team_def.name,
            success=any_success,
            aggregated_output=output,
            agent_results={
                name: {
                    "success": r.success,
                    "output": r.output,
                    "tool_calls": r.tool_calls_made,
                    "iterations": r.iterations,
                    "cost": r.total_cost,
                    "latency_ms": r.total_latency_ms,
                }
                for name, r in agent_results.items()
            },
            tasks_completed=completed,
            tasks_failed=failed,
            total_cost=budget.get_total_cost(),
            total_tokens=total_tokens,
            total_latency_ms=elapsed_ms,
            messages_exchanged=len(message_bus.get_all_messages()),
            partial=(any_success and failed > 0),
        )


def _aggregate_concatenate(results: Dict[str, AgentResult]) -> str:
    """Concatenate outputs with section headers."""
    sections = []
    for name, result in results.items():
        status = "Completed" if result.success else "Failed"
        sections.append(f"## {name} ({status})\n\n{result.output}")
    return "\n\n---\n\n".join(sections)


def _aggregate_merge_sections(results: Dict[str, AgentResult]) -> str:
    """Merge outputs with deduplication markers."""
    sections = []
    for name, result in results.items():
        if result.success:
            sections.append(f"### From {name}\n\n{result.output}")
    if not sections:
        return "All agents failed."
    return "\n\n".join(sections)


def _aggregate_vote(results: Dict[str, AgentResult]) -> str:
    """Present all perspectives with a vote tally."""
    sections = []
    successes = 0
    for name, result in results.items():
        vote = "PASS" if result.success else "FAIL"
        sections.append(f"### {name}: {vote}\n\n{result.output}")
        if result.success:
            successes += 1
    total = len(results)
    tally = f"## Vote Tally: {successes}/{total} passed\n\n"
    return tally + "\n\n---\n\n".join(sections)
