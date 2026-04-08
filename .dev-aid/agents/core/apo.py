"""
Automatic Prompt Optimization (APO) for Dev-AID agents.

Uses LLM-driven critique + beam search to iteratively improve agent
system prompts. Requires human approval before any prompt changes
are activated.

Inspired by Microsoft agent-lightning APO concepts.
"""

import difflib
import json
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .models import AgentDefinition
from .provider_adapter import ProviderAdapter
from .trace_collector import TraceCollector

logger = logging.getLogger(__name__)


@dataclass
class GoldenTestCase:
    """A test case used to evaluate prompt quality."""

    id: str
    agent_name: str
    user_message: str
    expected_behaviors: List[str]


@dataclass
class PromptVersion:
    """A versioned agent prompt with metadata."""

    version: int
    agent_name: str
    prompt_text: str
    created_at: str
    source: str  # "original", "apo_v{N}", "manual"
    parent_version: Optional[int] = None
    score: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APOConfig:
    """Configuration for Automatic Prompt Optimization."""

    traces_dir: Path = field(default_factory=lambda: Path(".dev-aid/agent-traces"))
    prompts_dir: Path = field(default_factory=lambda: Path(".dev-aid/agent-prompts"))
    golden_tests_path: Path = field(
        default_factory=lambda: Path(".dev-aid/config/golden-tests.json")
    )
    memory_bank_path: Path = field(default_factory=lambda: Path(".dev-aid/memory-bank"))
    beam_width: int = 3
    max_iterations: int = 3
    min_traces_for_optimization: int = 5
    critique_model: str = "claude-sonnet-4-5-20250929"


class APOOptimizer:
    """LLM-driven prompt optimizer with human approval gate.

    Pipeline:
    1. Load recent execution traces
    2. Generate critique (LLM analyzes failure patterns)
    3. Generate candidate prompts (beam search)
    4. Score candidates against golden test cases
    5. Present diff for human approval
    6. Save approved version to disk
    7. Write summary to memory bank
    """

    def __init__(
        self,
        config: APOConfig,
        adapter: ProviderAdapter,
    ) -> None:
        self._config = config
        self._adapter = adapter

    def optimize(
        self,
        agent_name: str,
        agent_def: AgentDefinition,
        dry_run: bool = False,
    ) -> Optional[PromptVersion]:
        """Run the full APO pipeline for an agent.

        Returns the new PromptVersion if approved, None otherwise.
        """
        # 1. Load recent traces
        traces = self._load_recent_traces(agent_name)
        if len(traces) < self._config.min_traces_for_optimization:
            logger.warning(
                "Only %d traces found for '%s' (need %d). Run the agent more first.",
                len(traces),
                agent_name,
                self._config.min_traces_for_optimization,
            )
            return None

        # 2. Get current prompt and version
        current_prompt, current_version = self._get_current_prompt(
            agent_name, agent_def
        )

        # 3. Generate critique
        trace_summaries = self._summarize_traces(traces)
        critique = self._generate_critique(agent_name, current_prompt, trace_summaries)
        print(f"\n--- Critique ---\n{critique}\n")

        if dry_run:
            print("[dry-run] Would generate candidate prompts next.")
            return None

        # 4. Generate candidate prompts
        candidates = self._generate_candidates(
            agent_name,
            current_prompt,
            critique,
            self._config.beam_width,
        )

        if not candidates:
            logger.warning("No candidate prompts generated.")
            return None

        # 5. Score candidates against golden tests
        golden_tests = self._load_golden_tests(agent_name)
        old_score = self._score_candidate(agent_name, current_prompt, golden_tests)

        best_candidate = current_prompt
        best_score = old_score
        for i, candidate in enumerate(candidates):
            score = self._score_candidate(agent_name, candidate, golden_tests)
            print(f"  Candidate {i+1}/{len(candidates)}: score={score:.2f}")
            if score > best_score:
                best_score = score
                best_candidate = candidate

        if best_candidate == current_prompt:
            print("\nNo candidate scored higher than the current prompt.")
            return None

        # 6. Present diff for human approval
        approved = self._present_diff_for_approval(
            agent_name, current_prompt, best_candidate, old_score, best_score
        )
        if not approved:
            print("Optimization declined by user.")
            return None

        # 7. Save version
        new_version = PromptVersion(
            version=current_version + 1,
            agent_name=agent_name,
            prompt_text=best_candidate,
            created_at=datetime.now().isoformat(),
            source=f"apo_v{current_version + 1}",
            parent_version=current_version,
            score=best_score,
            metadata={
                "critique": critique[:500],
                "old_score": old_score,
                "beam_width": self._config.beam_width,
                "traces_analyzed": len(traces),
            },
        )
        self._save_version(new_version)
        self._activate_version(agent_name, new_version.version)

        # 8. Write to memory bank
        self._write_to_memory_bank(
            agent_name,
            current_version,
            new_version.version,
            old_score,
            best_score,
            critique,
        )

        print(
            f"\nPrompt v{new_version.version} activated for '{agent_name}' "
            f"(score: {old_score:.2f} → {best_score:.2f})"
        )
        return new_version

    def rollback(
        self,
        agent_name: str,
        to_version: Optional[int] = None,
    ) -> bool:
        """Rollback to a previous prompt version."""
        history = self.history(agent_name)
        if len(history) < 2:
            logger.warning("No previous version to rollback to.")
            return False

        if to_version is not None:
            target = next((v for v in history if v.version == to_version), None)
            if target is None:
                logger.error("Version %d not found.", to_version)
                return False
        else:
            # Rollback to parent of current
            current = history[-1]
            if current.parent_version is None:
                logger.warning("Current version has no parent.")
                return False
            target = next(
                (v for v in history if v.version == current.parent_version),
                None,
            )
            if target is None:
                logger.error("Parent version %d not found.", current.parent_version)
                return False

        self._activate_version(agent_name, target.version)
        print(
            f"Rolled back '{agent_name}' to version {target.version} "
            f"(source: {target.source})"
        )
        return True

    def history(self, agent_name: str) -> List[PromptVersion]:
        """List all prompt versions for an agent."""
        agent_dir = self._config.prompts_dir / agent_name
        if not agent_dir.is_dir():
            return []

        versions: List[PromptVersion] = []
        for vfile in sorted(agent_dir.glob("v*.json")):
            try:
                data = json.loads(vfile.read_text(encoding="utf-8"))
                versions.append(
                    PromptVersion(
                        version=data["version"],
                        agent_name=data["agent_name"],
                        prompt_text=data["prompt_text"],
                        created_at=data["created_at"],
                        source=data["source"],
                        parent_version=data.get("parent_version"),
                        score=data.get("score"),
                        metadata=data.get("metadata", {}),
                    )
                )
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning("Skipping malformed version file %s: %s", vfile, e)
        return versions

    def status(self, agents_registry: Dict[str, AgentDefinition]) -> str:
        """Show APO status for all agents."""
        lines = ["Agent APO Status", "=" * 50]
        for agent_name in sorted(agents_registry.keys()):
            versions = self.history(agent_name)
            traces = TraceCollector.list_traces(
                self._config.traces_dir, agent_name, limit=100
            )
            current_txt = self._config.prompts_dir / agent_name / "current.txt"
            has_override = current_txt.is_file()

            status_parts = []
            status_parts.append(f"  traces: {len(traces)}")
            if versions:
                latest = versions[-1]
                status_parts.append(f"  version: v{latest.version} ({latest.source})")
                if latest.score is not None:
                    status_parts.append(f"  score: {latest.score:.2f}")
            else:
                status_parts.append("  version: original (no APO)")
            status_parts.append(f"  override: {'active' if has_override else 'none'}")

            lines.append(f"\n{agent_name}:")
            lines.extend(status_parts)

        return "\n".join(lines)

    # ── Internal helpers ─────────────────────────────────────────────

    def _load_recent_traces(
        self, agent_name: str, limit: int = 20
    ) -> List[List[Dict[str, Any]]]:
        """Load recent trace files for an agent."""
        paths = TraceCollector.list_traces(
            self._config.traces_dir, agent_name, limit=limit
        )
        traces: List[List[Dict[str, Any]]] = []
        for path in paths:
            try:
                events = TraceCollector.load_trace(path)
                if events:
                    traces.append(events)
            except Exception as e:
                logger.warning("Failed to load trace %s: %s", path, e)
        return traces

    @staticmethod
    def _summarize_traces(
        traces: List[List[Dict[str, Any]]],
    ) -> str:
        """Summarize traces into a text block for the LLM."""
        summaries: List[str] = []
        for i, events in enumerate(traces[:10]):  # Cap at 10 traces
            start = next((e for e in events if e.get("event") == "run_start"), {})
            end = next((e for e in events if e.get("event") == "run_end"), {})
            totals = end.get("totals", {})
            tool_events = [e for e in events if e.get("event") == "tool_result"]
            failed_tools = [e for e in tool_events if not e.get("success")]

            summary = (
                f"Trace {i+1}: "
                f"success={end.get('success', '?')}, "
                f"iterations={totals.get('iterations', '?')}, "
                f"cost=${totals.get('cost', 0):.4f}, "
                f"tools_used={len(tool_events)}, "
                f"tools_failed={len(failed_tools)}"
            )
            preview = end.get("output_preview", "")
            if preview:
                summary += f"\n  Output: {preview[:200]}"
            summaries.append(summary)

        return "\n".join(summaries)

    def _generate_critique(
        self,
        agent_name: str,
        current_prompt: str,
        trace_summaries: str,
    ) -> str:
        """Ask LLM to critique the current prompt based on traces."""
        critique_prompt = f"""You are an expert prompt engineer analyzing an AI agent's performance.

Agent: {agent_name}
Current system prompt (first 2000 chars):
---
{current_prompt[:2000]}
---

Recent execution traces:
{trace_summaries}

Analyze the agent's performance and identify:
1. Patterns in failures or suboptimal behavior
2. Specific weaknesses in the system prompt
3. Missing instructions that would improve performance
4. Redundant or confusing instructions

Provide a concise critique (max 500 words) with specific, actionable suggestions."""

        response = self._adapter.send_with_tools(
            messages=[{"role": "user", "content": critique_prompt}],
            tools=[],
            system_prompt="You are a prompt optimization expert.",
            model=self._config.critique_model,
            max_tokens=2048,
            temperature=0.3,
        )
        return response.content or ""

    def _generate_candidates(
        self,
        agent_name: str,
        current_prompt: str,
        critique: str,
        beam_width: int,
    ) -> List[str]:
        """Generate beam_width candidate improved prompts."""
        gen_prompt = f"""You are an expert prompt engineer. Based on the critique below,
generate {beam_width} improved versions of the agent's system prompt.

Agent: {agent_name}

Current prompt:
---
{current_prompt[:3000]}
---

Critique:
{critique}

Generate exactly {beam_width} improved prompt versions. Each should address
the critique while preserving the agent's core capabilities. Output as JSON:
{{"candidates": ["prompt1", "prompt2", ...]}}

Only output valid JSON, nothing else."""

        response = self._adapter.send_with_tools(
            messages=[{"role": "user", "content": gen_prompt}],
            tools=[],
            system_prompt="You are a prompt optimization expert. Output only valid JSON.",
            model=self._config.critique_model,
            max_tokens=8192,
            temperature=0.7,
        )

        try:
            content = response.content or ""
            # Strip markdown code fences if present
            if "```" in content:
                lines = content.split("\n")
                json_lines = []
                in_block = False
                for line in lines:
                    if line.strip().startswith("```"):
                        in_block = not in_block
                        continue
                    if in_block or not any(
                        line.strip().startswith(c) for c in ("```",)
                    ):
                        json_lines.append(line)
                content = "\n".join(json_lines)

            data = json.loads(content)
            candidates = data.get("candidates", [])
            if isinstance(candidates, list):
                return [c for c in candidates if isinstance(c, str) and len(c) > 50]
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("Failed to parse candidate prompts: %s", e)

        return []

    def _score_candidate(
        self,
        agent_name: str,
        candidate_prompt: str,
        golden_tests: List[GoldenTestCase],
    ) -> float:
        """Score a prompt candidate against golden test cases.

        Returns a score between 0.0 and 1.0.
        """
        if not golden_tests:
            return 0.5  # Neutral score when no golden tests exist

        total_behaviors = 0
        met_behaviors = 0

        for test in golden_tests:
            # Ask the LLM to simulate how the agent would respond
            sim_prompt = f"""Given this system prompt for agent '{agent_name}':
---
{candidate_prompt[:2000]}
---

And this user message:
"{test.user_message}"

Briefly describe (in 2-3 sentences) what the agent would likely do and focus on."""

            response = self._adapter.send_with_tools(
                messages=[{"role": "user", "content": sim_prompt}],
                tools=[],
                system_prompt="Briefly predict agent behavior.",
                model=self._config.critique_model,
                max_tokens=512,
                temperature=0.1,
            )
            sim_output = response.content or ""

            # Evaluate each expected behavior
            for behavior in test.expected_behaviors:
                total_behaviors += 1
                if self._evaluate_behavior(sim_output, behavior):
                    met_behaviors += 1

        return met_behaviors / total_behaviors if total_behaviors > 0 else 0.5

    def _evaluate_behavior(self, output: str, expected_behavior: str) -> bool:
        """Use LLM to judge whether output exhibits expected behavior."""
        eval_prompt = f"""Does the following agent response plan exhibit this behavior?

Behavior: "{expected_behavior}"

Response plan:
"{output[:500]}"

Answer only "yes" or "no"."""

        response = self._adapter.send_with_tools(
            messages=[{"role": "user", "content": eval_prompt}],
            tools=[],
            system_prompt="Answer only yes or no.",
            model=self._config.critique_model,
            max_tokens=10,
            temperature=0.0,
        )
        answer = (response.content or "").strip().lower()
        return answer.startswith("yes")

    def _present_diff_for_approval(
        self,
        agent_name: str,
        old_prompt: str,
        new_prompt: str,
        old_score: float,
        new_score: float,
    ) -> bool:
        """Show unified diff and scores, await user approval."""
        diff = difflib.unified_diff(
            old_prompt.splitlines(keepends=True),
            new_prompt.splitlines(keepends=True),
            fromfile=f"{agent_name}/current",
            tofile=f"{agent_name}/proposed",
            lineterm="",
        )
        diff_text = "\n".join(diff)

        print(f"\n{'='*60}")
        print(f"  APO Proposal for: {agent_name}")
        print(
            f"  Score: {old_score:.2f} → {new_score:.2f} "
            f"(+{new_score - old_score:.2f})"
        )
        print(f"{'='*60}")
        print(diff_text)
        print(f"{'='*60}")

        try:
            answer = input("\nApply this optimization? [y/N] ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return False
        return answer in ("y", "yes")

    def _get_current_prompt(
        self,
        agent_name: str,
        agent_def: AgentDefinition,
    ) -> Tuple[str, int]:
        """Get the current active prompt and its version number."""
        current_txt = self._config.prompts_dir / agent_name / "current.txt"
        if current_txt.is_file():
            prompt = current_txt.read_text(encoding="utf-8")
            # Find version number from history
            history_file = self._config.prompts_dir / agent_name / "history.json"
            if history_file.is_file():
                data = json.loads(history_file.read_text(encoding="utf-8"))
                return prompt, data.get("current_version", 1)
            return prompt, 1

        # No APO override — use the agent definition's built-in prompt
        return agent_def.system_prompt_extra, 0

    def _save_version(self, version: PromptVersion) -> None:
        """Save a prompt version to disk."""
        agent_dir = self._config.prompts_dir / version.agent_name
        agent_dir.mkdir(parents=True, exist_ok=True)

        version_file = agent_dir / f"v{version.version:03d}.json"
        version_file.write_text(
            json.dumps(
                {
                    "version": version.version,
                    "agent_name": version.agent_name,
                    "prompt_text": version.prompt_text,
                    "created_at": version.created_at,
                    "source": version.source,
                    "parent_version": version.parent_version,
                    "score": version.score,
                    "metadata": version.metadata,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    def _activate_version(self, agent_name: str, version_num: int) -> None:
        """Set a version as the active prompt."""
        agent_dir = self._config.prompts_dir / agent_name
        version_file = agent_dir / f"v{version_num:03d}.json"

        if not version_file.is_file():
            raise FileNotFoundError(f"Version file not found: {version_file}")

        data = json.loads(version_file.read_text(encoding="utf-8"))
        prompt_text = data["prompt_text"]

        # Write current.txt
        current_txt = agent_dir / "current.txt"
        current_txt.write_text(prompt_text, encoding="utf-8")

        # Update history.json
        history_file = agent_dir / "history.json"
        if history_file.is_file():
            history = json.loads(history_file.read_text(encoding="utf-8"))
        else:
            history = {"agent_name": agent_name, "versions": []}

        history["current_version"] = version_num
        if version_num not in history.get("versions", []):
            history.setdefault("versions", []).append(version_num)

        history_file.write_text(json.dumps(history, indent=2), encoding="utf-8")

    def _load_golden_tests(self, agent_name: str) -> List[GoldenTestCase]:
        """Load golden test cases for an agent."""
        if not self._config.golden_tests_path.is_file():
            return []

        try:
            data = json.loads(
                self._config.golden_tests_path.read_text(encoding="utf-8")
            )
        except (json.JSONDecodeError, OSError) as e:
            logger.warning("Failed to load golden tests: %s", e)
            return []

        tests: List[GoldenTestCase] = []
        agent_tests = data.get(agent_name, [])
        for t in agent_tests:
            tests.append(
                GoldenTestCase(
                    id=t.get("id", ""),
                    agent_name=agent_name,
                    user_message=t.get("user_message", ""),
                    expected_behaviors=t.get("expected_behaviors", []),
                )
            )
        return tests

    def _write_to_memory_bank(
        self,
        agent_name: str,
        old_version: int,
        new_version: int,
        old_score: float,
        new_score: float,
        critique: str,
    ) -> None:
        """Append optimization result to memory bank."""
        opt_file = self._config.memory_bank_path / "agent-optimization.md"
        if not opt_file.parent.is_dir():
            return

        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = (
            f"\n### {agent_name} — v{old_version} → v{new_version} "
            f"({now})\n"
            f"- Score: {old_score:.2f} → {new_score:.2f}\n"
            f"- Key insight: {critique[:200]}\n"
        )

        try:
            if opt_file.is_file():
                content = opt_file.read_text(encoding="utf-8")
            else:
                content = "# Agent Optimization History\n\n"
                content += "Results from Automatic Prompt Optimization (APO) runs.\n"

            # Append under Optimization History section
            content += entry
            opt_file.write_text(content, encoding="utf-8")
        except OSError as e:
            logger.warning("Failed to write to memory bank: %s", e)


def get_apo_prompt_override(prompts_dir: Path, agent_name: str) -> Optional[str]:
    """Load the APO prompt override for an agent, if one exists.

    Used by cli.py and team_runner.py to apply optimized prompts.
    """
    current_txt = prompts_dir / agent_name / "current.txt"
    if current_txt.is_file():
        return current_txt.read_text(encoding="utf-8")
    return None
