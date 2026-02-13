"""
Main agent execution loop.

Orchestrates the send -> tool_calls -> execute -> repeat cycle,
building system prompts from skills and tracking costs.
Includes retry with exponential backoff and context management.
"""

import logging
import time
from typing import Any, Callable, Dict, List, Optional

from .models import AgentDefinition, AgentResult, StopWatch, ToolCall
from .provider_adapter import ProviderAdapter, ProviderResponse
from .skill_loader import SkillLoader
from .tool_registry import ToolRegistry
from .trace_collector import TraceCollector

logger = logging.getLogger(__name__)

# Default context budget (tokens) before trimming kicks in
DEFAULT_MAX_CONTEXT_TOKENS = 100_000

# Retry configuration
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_BASE_DELAY = 1.0  # seconds


class AgentRunner:
    """Runs an agent loop: send messages -> execute tools -> repeat."""

    def __init__(
        self,
        adapter: ProviderAdapter,
        registry: ToolRegistry,
        skill_loader: Optional[SkillLoader] = None,
        on_tool_call: Optional[Callable[[ToolCall], None]] = None,
        on_iteration: Optional[Callable[[int, ProviderResponse], None]] = None,
        max_context_tokens: int = DEFAULT_MAX_CONTEXT_TOKENS,
        max_retries: int = DEFAULT_MAX_RETRIES,
        trace_collector: Optional[TraceCollector] = None,
    ) -> None:
        self._adapter = adapter
        self._registry = registry
        self._skill_loader = skill_loader
        self._on_tool_call = on_tool_call
        self._on_iteration = on_iteration
        self._max_context_tokens = max_context_tokens
        self._max_retries = max_retries
        self._trace_collector = trace_collector

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

    def _get_tool_definitions(
        self,
        agent_def: AgentDefinition,
    ) -> List[Dict[str, Any]]:
        """Get tool definitions in the adapter's native format."""
        tool_names = agent_def.tools or None
        tool_format = getattr(self._adapter, "tool_format", "anthropic")

        if tool_format == "openai":
            return self._registry.to_openai_format(tool_names)
        elif tool_format == "gemini":
            return self._registry.to_gemini_format(tool_names)
        else:
            return self._registry.to_anthropic_format(tool_names)

    def _send_with_retry(
        self,
        messages: List[Dict[str, Any]],
        tool_defs: List[Dict[str, Any]],
        system_prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
    ) -> ProviderResponse:
        """Send request with exponential backoff retry on transient errors."""
        last_error: Optional[Exception] = None
        delay = DEFAULT_RETRY_BASE_DELAY

        for attempt in range(1, self._max_retries + 1):
            try:
                return self._adapter.send_with_tools(
                    messages=messages,
                    tools=tool_defs,
                    system_prompt=system_prompt,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                )
            except Exception as e:
                last_error = e
                if attempt < self._max_retries:
                    logger.warning(
                        "Provider error (attempt %d/%d): %s — retrying in %.1fs",
                        attempt,
                        self._max_retries,
                        e,
                        delay,
                    )
                    time.sleep(delay)
                    delay *= 2  # exponential backoff
                else:
                    logger.error(
                        "Provider error (attempt %d/%d): %s — giving up",
                        attempt,
                        self._max_retries,
                        e,
                    )

        raise last_error  # type: ignore[misc]

    @staticmethod
    def _estimate_message_tokens(messages: List[Dict[str, Any]]) -> int:
        """Rough estimate of token count across all messages.

        Uses ~4 chars per token as a fast heuristic.
        """
        total_chars = 0
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                total_chars += len(content)
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        for key in ("content", "text", "result"):
                            val = block.get(key, "")
                            if isinstance(val, str):
                                total_chars += len(val)
            # Also count parts (Gemini format)
            parts = msg.get("parts", [])
            if isinstance(parts, list):
                for part in parts:
                    if isinstance(part, dict):
                        if "text" in part:
                            total_chars += len(str(part["text"]))
                        fr = part.get("function_response", {})
                        if isinstance(fr, dict):
                            resp = fr.get("response", {})
                            if isinstance(resp, dict):
                                total_chars += len(str(resp.get("result", "")))
        return total_chars // 4

    def _trim_context(self, messages: List[Dict[str, Any]]) -> None:
        """Trim old tool results if context is approaching the limit.

        Keeps the first message (user task) and last few messages
        (recent context) intact. Truncates tool output in the middle.
        """
        estimated = self._estimate_message_tokens(messages)
        if estimated <= self._max_context_tokens:
            return

        # Keep first message and last 6 messages
        keep_last = min(6, len(messages) - 1)
        if len(messages) <= keep_last + 1:
            return

        truncation_limit = 300  # chars to keep per truncated block
        for i in range(1, len(messages) - keep_last):
            msg = messages[i]
            content = msg.get("content", "")

            if isinstance(content, str) and len(content) > truncation_limit:
                messages[i] = {
                    **msg,
                    "content": content[:truncation_limit] + "\n... [truncated] ...",
                }
            elif isinstance(content, list):
                new_content: List[Dict[str, Any]] = []
                for block in content:
                    if isinstance(block, dict):
                        new_block = dict(block)
                        for key in ("content", "text"):
                            if (
                                key in new_block
                                and isinstance(new_block[key], str)
                                and len(new_block[key]) > truncation_limit
                            ):
                                new_block[key] = (
                                    new_block[key][:truncation_limit]
                                    + "\n... [truncated] ..."
                                )
                        new_content.append(new_block)
                    else:
                        new_content.append(block)
                messages[i] = {**msg, "content": new_content}

            # Handle Gemini parts format
            parts = msg.get("parts", [])
            if isinstance(parts, list):
                new_parts: List[Dict[str, Any]] = []
                for part in parts:
                    if isinstance(part, dict) and "text" in part:
                        text = part["text"]
                        if isinstance(text, str) and len(text) > truncation_limit:
                            new_parts.append(
                                {"text": text[:truncation_limit] + "\n... [truncated] ..."}
                            )
                        else:
                            new_parts.append(part)
                    else:
                        new_parts.append(part)
                if new_parts:
                    messages[i] = {**msg, "parts": new_parts}

        logger.info(
            "Trimmed context from ~%d to ~%d estimated tokens",
            estimated,
            self._estimate_message_tokens(messages),
        )

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

        # Start trace if collector is present
        if self._trace_collector:
            self._trace_collector.start_trace(
                agent_def, user_message, system_prompt, model
            )

        # Get tool definitions in the adapter's native format
        tool_defs = self._get_tool_definitions(agent_def)

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

            # Trim context if getting too large
            self._trim_context(messages)

            try:
                response = self._send_with_retry(
                    messages=messages,
                    tool_defs=tool_defs,
                    system_prompt=system_prompt,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=agent_def.temperature,
                )
            except Exception as e:
                logger.error("Provider error after retries: %s", e)
                error_result = AgentResult(
                    agent_name=agent_def.name,
                    success=False,
                    output=f"Provider error: {e}",
                    tool_calls_made=tool_calls_made,
                    iterations=iteration,
                    total_tokens=total_tokens,
                    total_cost=total_cost,
                    total_latency_ms=timer.elapsed_ms(),
                )
                if self._trace_collector:
                    self._trace_collector.end_trace(error_result)
                return error_result

            # Accumulate tokens and cost
            total_tokens["input"] += response.tokens_used.get("input", 0)
            total_tokens["output"] += response.tokens_used.get("output", 0)
            total_cost += response.cost

            # Record iteration trace
            if self._trace_collector:
                stop_reason = "tool_use" if response.tool_calls else "end_turn"
                tc_summary = [
                    {"name": tc.name, "id": tc.id}
                    for tc in (response.tool_calls or [])
                ]
                self._trace_collector.record_iteration(
                    iteration=iteration,
                    tokens_used=response.tokens_used,
                    cost=response.cost,
                    stop_reason=stop_reason,
                    tool_calls=tc_summary,
                    latency_ms=timer.elapsed_ms(),
                )

            # Notify iteration callback
            if self._on_iteration:
                self._on_iteration(iteration, response)

            # If no tool calls, we have the final response
            if not response.tool_calls:
                final_output = response.content or ""
                success_result = AgentResult(
                    agent_name=agent_def.name,
                    success=True,
                    output=final_output,
                    tool_calls_made=tool_calls_made,
                    iterations=iteration,
                    total_tokens=total_tokens,
                    total_cost=total_cost,
                    total_latency_ms=timer.elapsed_ms(),
                )
                if self._trace_collector:
                    self._trace_collector.end_trace(success_result)
                return success_result

            # Append assistant message with tool calls
            if hasattr(self._adapter, "format_assistant_tool_use"):
                assistant_msg = self._adapter.format_assistant_tool_use(
                    response.tool_calls, response.content
                )
            else:
                assistant_msg = {"role": "assistant", "content": response.content or ""}
            messages.append(assistant_msg)

            # Execute all tool calls
            results = []
            for tool_call in response.tool_calls:
                tool_calls_made += 1
                if self._on_tool_call:
                    self._on_tool_call(tool_call)

                logger.info("Executing tool: %s(%s)", tool_call.name, tool_call.arguments)
                tool_timer = StopWatch()
                result = self._registry.execute(tool_call)
                results.append(result)

                if self._trace_collector:
                    self._trace_collector.record_tool_result(
                        iteration=iteration,
                        tool_name=tool_call.name,
                        success=result.success,
                        output_length=len(result.output),
                        error=result.error,
                        latency_ms=tool_timer.elapsed_ms(),
                    )

            # Format and append tool results (batched per adapter requirements)
            if hasattr(self._adapter, "format_tool_results"):
                result_messages = self._adapter.format_tool_results(results)
                messages.extend(result_messages)
            else:
                # Fallback for adapters without format_tool_results
                for r in results:
                    messages.append(
                        {
                            "role": "user",
                            "content": r.output if r.success else (r.error or ""),
                        }
                    )

        # Max iterations reached
        logger.warning(
            "Agent '%s' reached max iterations (%d)",
            agent_def.name,
            agent_def.max_iterations,
        )
        max_iter_result = AgentResult(
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
        if self._trace_collector:
            self._trace_collector.end_trace(max_iter_result)
        return max_iter_result
