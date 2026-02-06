"""
Main agent execution loop.

Orchestrates the send → tool_calls → execute → repeat cycle,
building system prompts from skills and tracking costs.
"""

import logging
from typing import Any, Callable, Dict, List, Optional

from .models import AgentDefinition, AgentResult, StopWatch, ToolCall
from .provider_adapter import ProviderAdapter, ProviderResponse
from .skill_loader import SkillLoader
from .tool_registry import ToolRegistry

logger = logging.getLogger(__name__)


class AgentRunner:
    """Runs an agent loop: send messages → execute tools → repeat."""

    def __init__(
        self,
        adapter: ProviderAdapter,
        registry: ToolRegistry,
        skill_loader: Optional[SkillLoader] = None,
        on_tool_call: Optional[Callable[[ToolCall], None]] = None,
        on_iteration: Optional[Callable[[int, ProviderResponse], None]] = None,
    ) -> None:
        self._adapter = adapter
        self._registry = registry
        self._skill_loader = skill_loader
        self._on_tool_call = on_tool_call
        self._on_iteration = on_iteration

    def _build_system_prompt(
        self,
        agent_def: AgentDefinition,
        extra_context: str = "",
    ) -> str:
        """Build the system prompt from skills and agent config."""
        parts: List[str] = []

        # Load skill prompts
        if self._skill_loader and agent_def.skills:
            skill_prompt = self._skill_loader.build_system_prompt(agent_def.skills)
            if skill_prompt:
                parts.append(skill_prompt)

        # Agent-specific instructions
        if agent_def.system_prompt_extra:
            parts.append(agent_def.system_prompt_extra)

        # Extra context (project info, memory bank, etc.)
        if extra_context:
            parts.append(extra_context)

        # Output format instructions
        if agent_def.output_format:
            parts.append(f"\nOutput your final response in {agent_def.output_format} format.")

        return "\n\n---\n\n".join(parts) if parts else ""

    def _get_adapter_formatter(self) -> Any:
        """Get the adapter for formatting tool results in messages."""
        return self._adapter

    def run(
        self,
        agent_def: AgentDefinition,
        user_message: str,
        model: str = "",
        max_tokens: int = 4096,
        extra_context: str = "",
    ) -> AgentResult:
        """
        Execute the agent loop.

        Args:
            agent_def: Agent definition with skills, tools, and config
            user_message: Initial user message/task
            model: Model to use (overrides default)
            max_tokens: Max tokens per response
            extra_context: Additional context to inject into system prompt

        Returns:
            AgentResult with output, metrics, and cost
        """
        timer = StopWatch()
        system_prompt = self._build_system_prompt(agent_def, extra_context)

        # Get tool definitions in the format the adapter expects
        tool_defs = self._registry.to_anthropic_format(agent_def.tools or None)

        messages: List[Dict[str, Any]] = [
            {"role": "user", "content": user_message},
        ]

        total_tokens: Dict[str, int] = {"input": 0, "output": 0}
        total_cost: float = 0.0
        tool_calls_made: int = 0
        final_output: str = ""

        for iteration in range(1, agent_def.max_iterations + 1):
            logger.info(
                "Agent '%s' iteration %d/%d",
                agent_def.name,
                iteration,
                agent_def.max_iterations,
            )

            try:
                response = self._adapter.send_with_tools(
                    messages=messages,
                    tools=tool_defs,
                    system_prompt=system_prompt,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=agent_def.temperature,
                )
            except Exception as e:
                logger.error("Provider error on iteration %d: %s", iteration, e)
                return AgentResult(
                    agent_name=agent_def.name,
                    success=False,
                    output=f"Provider error: {e}",
                    tool_calls_made=tool_calls_made,
                    iterations=iteration,
                    total_tokens=total_tokens,
                    total_cost=total_cost,
                    total_latency_ms=timer.elapsed_ms(),
                )

            # Accumulate tokens and cost
            total_tokens["input"] += response.tokens_used.get("input", 0)
            total_tokens["output"] += response.tokens_used.get("output", 0)
            total_cost += response.cost

            # Notify iteration callback
            if self._on_iteration:
                self._on_iteration(iteration, response)

            # If no tool calls, we have the final response
            if not response.tool_calls:
                final_output = response.content or ""
                return AgentResult(
                    agent_name=agent_def.name,
                    success=True,
                    output=final_output,
                    tool_calls_made=tool_calls_made,
                    iterations=iteration,
                    total_tokens=total_tokens,
                    total_cost=total_cost,
                    total_latency_ms=timer.elapsed_ms(),
                )

            # Append assistant message with tool calls
            adapter = self._get_adapter_formatter()
            if hasattr(adapter, "format_assistant_tool_use"):
                assistant_msg = adapter.format_assistant_tool_use(
                    response.tool_calls, response.content
                )
            else:
                # Fallback for adapters without the helper
                assistant_msg = {"role": "assistant", "content": response.content or ""}
            messages.append(assistant_msg)

            # Execute each tool call and append results
            for tool_call in response.tool_calls:
                tool_calls_made += 1
                if self._on_tool_call:
                    self._on_tool_call(tool_call)

                logger.info("Executing tool: %s(%s)", tool_call.name, tool_call.arguments)
                result = self._registry.execute(tool_call)

                if hasattr(adapter, "format_tool_result"):
                    result_msg = adapter.format_tool_result(
                        call_id=result.call_id,
                        output=result.output if result.success else (result.error or ""),
                        is_error=not result.success,
                    )
                else:
                    result_msg = {"role": "user", "content": result.output}
                messages.append(result_msg)

        # Max iterations reached
        logger.warning(
            "Agent '%s' reached max iterations (%d)",
            agent_def.name,
            agent_def.max_iterations,
        )
        return AgentResult(
            agent_name=agent_def.name,
            success=False,
            output=(
                final_output
                or "[warning] Agent reached maximum iterations without completing the task."
            ),
            tool_calls_made=tool_calls_made,
            iterations=agent_def.max_iterations,
            total_tokens=total_tokens,
            total_cost=total_cost,
            total_latency_ms=timer.elapsed_ms(),
        )
