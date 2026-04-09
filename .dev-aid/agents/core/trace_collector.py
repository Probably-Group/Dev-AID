"""
Agent trace collection for execution analysis.

Records agent rollouts as JSONL files for post-hoc analysis,
debugging, and automatic prompt optimization (APO).
"""

import hashlib
import json
import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import AgentDefinition, AgentResult

logger = logging.getLogger(__name__)


@dataclass
class TraceConfig:
    """Configuration for trace collection."""

    enabled: bool = False
    trace_dir: Path = field(default_factory=lambda: Path(".dev-aid/agent-traces"))
    include_output_preview: bool = True
    output_preview_length: int = 500


class TraceCollector:
    """Collects execution traces as JSONL files.

    Thread-safe: uses a lock for file writes so traces from
    parallel team agents don't interleave.
    """

    def __init__(
        self,
        config: TraceConfig,
        agent_name: str,
        model: str,
    ) -> None:
        self._config = config
        self._agent_name = agent_name
        self._model = model
        self._trace_id: str = ""
        self._trace_path: Optional[Path] = None
        self._lock = threading.Lock()
        self._start_time: float = 0.0

    def start_trace(
        self,
        agent_def: AgentDefinition,
        user_message: str,
        system_prompt: str,
        model: str,
    ) -> str:
        """Begin a new trace. Returns the trace ID."""
        self._trace_id = uuid.uuid4().hex[:12]
        # perf_counter (not monotonic): see StopWatch docstring in models.py
        self._start_time = time.perf_counter()

        # Build output path: {trace_dir}/{agent_name}/{YYYYMMDD-HHMMSS}-{id}.jsonl
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d-%H%M%S")
        agent_dir = self._config.trace_dir / self._agent_name
        agent_dir.mkdir(parents=True, exist_ok=True)
        self._trace_path = agent_dir / f"{timestamp}-{self._trace_id}.jsonl"

        prompt_hash = hashlib.sha256(system_prompt.encode()).hexdigest()[:16]

        self._write_line(
            {
                "event": "run_start",
                "trace_id": self._trace_id,
                "agent_name": self._agent_name,
                "model": model,
                "system_prompt_hash": prompt_hash,
                "user_message": user_message,
                "temperature": agent_def.temperature,
                "max_iterations": agent_def.max_iterations,
                "tools": agent_def.tools,
                "timestamp": now.isoformat(),
            }
        )
        return self._trace_id

    def record_iteration(
        self,
        iteration: int,
        tokens_used: Dict[str, int],
        cost: float,
        stop_reason: str,
        tool_calls: List[Dict[str, Any]],
        latency_ms: float,
    ) -> None:
        """Record an iteration (LLM call + response)."""
        self._write_line(
            {
                "event": "iteration",
                "trace_id": self._trace_id,
                "iteration": iteration,
                "tokens_used": tokens_used,
                "cost": cost,
                "stop_reason": stop_reason,
                "tool_calls": tool_calls,
                "latency_ms": round(latency_ms, 1),
            }
        )

    def record_tool_result(
        self,
        iteration: int,
        tool_name: str,
        success: bool,
        output_length: int,
        error: Optional[str],
        latency_ms: float,
    ) -> None:
        """Record a tool execution result."""
        self._write_line(
            {
                "event": "tool_result",
                "trace_id": self._trace_id,
                "iteration": iteration,
                "tool_name": tool_name,
                "success": success,
                "output_length": output_length,
                "error": error,
                "latency_ms": round(latency_ms, 1),
            }
        )

    def end_trace(self, result: AgentResult) -> None:
        """Finalize the trace with the agent result."""
        elapsed_ms = (time.perf_counter() - self._start_time) * 1000.0

        preview = ""
        if self._config.include_output_preview and result.output:
            preview = result.output[: self._config.output_preview_length]

        self._write_line(
            {
                "event": "run_end",
                "trace_id": self._trace_id,
                "success": result.success,
                "output_length": len(result.output),
                "output_preview": preview,
                "totals": {
                    "iterations": result.iterations,
                    "tokens": result.total_tokens,
                    "cost": result.total_cost,
                    "latency_ms": round(elapsed_ms, 1),
                    "tool_calls": result.tool_calls_made,
                },
            }
        )
        logger.info(
            "Trace %s written to %s",
            self._trace_id,
            self._trace_path,
        )

    def _write_line(self, data: Dict[str, Any]) -> None:
        """Thread-safe JSONL append."""
        if not self._trace_path:
            return
        with self._lock:
            with open(self._trace_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(data, default=str) + "\n")

    @staticmethod
    def list_traces(
        trace_dir: Path,
        agent_name: Optional[str] = None,
        limit: int = 20,
    ) -> List[Path]:
        """List recent trace files, newest first."""
        if agent_name:
            search_dir = trace_dir / agent_name
        else:
            search_dir = trace_dir

        if not search_dir.is_dir():
            return []

        pattern = "**/*.jsonl" if not agent_name else "*.jsonl"
        traces = sorted(
            search_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True
        )
        return traces[:limit]

    @staticmethod
    def load_trace(path: Path) -> List[Dict[str, Any]]:
        """Load all events from a JSONL trace file."""
        events: List[Dict[str, Any]] = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    events.append(json.loads(line))
        return events
