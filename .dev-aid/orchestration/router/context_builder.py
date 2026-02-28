"""
Context Builder for Dev-AID Router

Gathers relevant context from:
- Memory bank files
- Active skills
- Git context
- Project structure
- MCP servers (database, GitHub, code search, etc.)
"""

import asyncio
import logging
import os
import time
from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Tuple, runtime_checkable

from .constants import (
    CHARS_PER_TOKEN,
    CODEBASE_SEARCH_TOP_K,
    CODEBASE_SIZE_CACHE_TTL,
    CODEBASE_SIZE_MEDIUM_MAX_CHUNKS,
    CODEBASE_SIZE_MEDIUM_MAX_FILES,
    CODEBASE_SIZE_SMALL_MAX_CHUNKS,
    CODEBASE_SIZE_SMALL_MAX_FILES,
    MEMORY_BANK_BUDGET_MULTIPLIERS,
    MCP_CACHE_TTL,
)
from .security_utils import validate_safe_path
from .token_estimation import estimate_tokens

logger = logging.getLogger(__name__)

# Keyword map for query-aware on-demand file selection
MEMORY_FILE_KEYWORDS: Dict[str, List[str]] = {
    "patterns.md": [
        "pattern",
        "convention",
        "style",
        "naming",
        "format",
        "lint",
        "standard",
    ],
    "decisions.md": [
        "decision",
        "architecture",
        "adr",
        "design",
        "tradeoff",
        "migration",
        "why",
    ],
    "security.md": [
        "security",
        "auth",
        "vulnerability",
        "xss",
        "injection",
        "secret",
        "owasp",
        "cve",
    ],
    "performance.md": [
        "performance",
        "speed",
        "latency",
        "cache",
        "optimize",
        "benchmark",
        "slow",
    ],
    "testing.md": [
        "test",
        "coverage",
        "mock",
        "fixture",
        "jest",
        "pytest",
        "spec",
        "qa",
    ],
    "chaos.md": [
        "error",
        "resilience",
        "retry",
        "circuit",
        "fallback",
        "chaos",
        "failure",
        "exception",
    ],
    "agent-optimization.md": [
        "agent",
        "optimization",
        "prompt",
        "apo",
        "trace",
        "performance",
        "improvement",
    ],
}


@runtime_checkable
class ConfigLoaderProtocol(Protocol):
    """Protocol describing the ConfigLoader interface used by ContextBuilder."""

    root: Path
    settings: Dict[str, Any]

    def get_memory_bank_path(self) -> Path: ...

    def get_memory_bank_files(self) -> List[str]: ...

    def get_on_demand_files(self) -> List[str]: ...

    def get_standing_context_tokens(self) -> int: ...

    def get_orchestration_mode(self) -> str: ...

    def get_enabled_providers(self) -> List[str]: ...


@dataclass
class DevAIDContext:
    """Represents Dev-AID context for AI request"""

    memory_bank: Dict[str, str]  # filename -> content
    project_info: Dict[str, Any]
    git_context: Optional[Dict[str, str]] = None
    active_skills: Optional[List[str]] = None
    mcp_context: Optional[Dict[str, Any]] = field(default_factory=dict)  # MCP-gathered context
    memory_bank_metadata: Dict[str, Dict[str, Any]] = field(
        default_factory=dict
    )  # per-file metadata


@dataclass
class _CacheEntry:
    """TTL cache entry for MCP query results."""

    result: Dict[str, Any]
    timestamp: float
    ttl: float = MCP_CACHE_TTL

    @property
    def is_expired(self) -> bool:
        return (time.time() - self.timestamp) > self.ttl


class ContextBuilder:
    """Builds context from Dev-AID configuration and state"""

    def __init__(self, config_loader: ConfigLoaderProtocol, mcp_pool: Any = None) -> None:
        """
        Initialize context builder

        Args:
            config_loader: ConfigLoader instance (must satisfy ConfigLoaderProtocol)
            mcp_pool: Optional MCPClientPool for MCP context gathering
        """
        self.config = config_loader
        self.root = config_loader.root
        self.memory_bank_path = config_loader.get_memory_bank_path()
        self.mcp_pool = mcp_pool
        self._mcp_cache: Dict[str, _CacheEntry] = {}

    def _cache_key(self, prompt: str, server_name: str) -> str:
        """Generate cache key from prompt and server."""
        raw = f"{server_name}:{prompt.strip().lower()}"
        return sha256(raw.encode()).hexdigest()[:16]

    def _get_cached(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached MCP result if not expired."""
        entry = self._mcp_cache.get(key)
        if entry and not entry.is_expired:
            return entry.result
        if entry:
            del self._mcp_cache[key]
        return None

    def _set_cached(self, key: str, result: Dict[str, Any], ttl: float = MCP_CACHE_TTL) -> None:
        """Cache an MCP query result."""
        self._mcp_cache[key] = _CacheEntry(result=result, timestamp=time.time(), ttl=ttl)

    def clear_mcp_cache(self) -> None:
        """Clear the MCP query cache."""
        self._mcp_cache.clear()

    def build_context(
        self,
        include_memory: bool = True,
        prompt: Optional[str] = None,
    ) -> DevAIDContext:
        """
        Build complete Dev-AID context

        Args:
            include_memory: Whether to include memory bank files
            prompt: Optional user prompt for query-aware on-demand loading

        Returns:
            DevAIDContext object
        """
        memory_bank: Dict[str, str] = {}
        memory_bank_metadata: Dict[str, Dict[str, Any]] = {}
        if include_memory:
            memory_bank, memory_bank_metadata = self._load_memory_bank(prompt=prompt)

        project_info = self._get_project_info()
        git_context = self._get_git_context()
        active_skills = self._detect_active_skills()

        return DevAIDContext(
            memory_bank=memory_bank,
            project_info=project_info,
            git_context=git_context,
            active_skills=active_skills,
            memory_bank_metadata=memory_bank_metadata,
        )

    def _validate_and_read_file(self, filename: str) -> Optional[str]:
        """Validate a memory bank filename and read its content.

        Returns file content or None if invalid/missing.
        """
        # Validate filename doesn't contain traversal (CWE-22)
        if ".." in filename or filename.startswith("/"):
            logger.warning("Skipping unsafe memory bank filename: %s", filename)
            return None

        filepath = self.memory_bank_path / filename

        # Verify resolved path stays within memory bank directory
        try:
            resolved = filepath.resolve()
            if not resolved.is_relative_to(self.memory_bank_path.resolve()):
                logger.warning("Path traversal blocked for memory bank file: %s", filename)
                return None
        except (ValueError, OSError):
            logger.warning("Invalid memory bank path: %s", filename)
            return None

        if not filepath.exists():
            return None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.warning("Could not read %s: %s", filename, e)
            return None

    def _get_file_staleness(self, filepath: Path, warning_days: int = 30) -> Dict[str, Any]:
        """Compute staleness metadata for a memory bank file.

        Returns dict with age_days, age_human, is_stale.
        """
        try:
            mtime = os.path.getmtime(filepath)
            age_seconds = time.time() - mtime
            age_days = int(age_seconds / 86400)

            if age_days == 0:
                age_human = "today"
            elif age_days == 1:
                age_human = "1 day ago"
            else:
                age_human = f"{age_days} days ago"

            return {
                "age_days": age_days,
                "age_human": age_human,
                "is_stale": age_days > warning_days,
            }
        except OSError:
            return {
                "age_days": -1,
                "age_human": "unknown",
                "is_stale": False,
            }

    def _enforce_token_budget(
        self,
        auto_load: Dict[str, str],
        on_demand: Dict[str, str],
        budget: int,
        prompt: Optional[str] = None,
    ) -> Tuple[Dict[str, str], Dict[str, int]]:
        """Enforce token budget on memory bank content.

        Auto-load files are always included (warning if they exceed budget).
        On-demand files are added in order until budget is exhausted.
        Returns (merged content dict, per-file token counts).
        """
        result: Dict[str, str] = {}
        token_counts: Dict[str, int] = {}
        used_tokens = 0

        # Auto-load files always included
        for filename, content in auto_load.items():
            tokens = estimate_tokens(content)
            result[filename] = content
            token_counts[filename] = tokens
            used_tokens += tokens

        if used_tokens > budget and auto_load:
            logger.warning(
                "Auto-load files alone (%d tokens) exceed budget (%d tokens)",
                used_tokens,
                budget,
            )

        # On-demand files added until budget exhausted
        remaining = max(0, budget - used_tokens)
        for filename, content in on_demand.items():
            if filename in result:
                continue  # Skip duplicates
            tokens = estimate_tokens(content)
            if tokens <= remaining:
                result[filename] = content
                token_counts[filename] = tokens
                remaining -= tokens
            elif remaining > 0:
                # Partial: extract relevant sections or truncate
                truncated = self._extract_relevant_sections(content, prompt, remaining)
                result[filename] = truncated
                token_counts[filename] = estimate_tokens(truncated)
                remaining = 0
            else:
                break  # Budget exhausted

        return result, token_counts

    def _select_on_demand_files(
        self, prompt: str, available: List[str], budget_mode: str = "balanced"
    ) -> List[str]:
        """Select on-demand files relevant to the prompt using keyword matching.

        Args:
            prompt: User prompt to match against
            available: List of available on-demand filenames
            budget_mode: Budget mode (minimal requires 2+ matches, generous loads all)

        Returns:
            List of selected filenames
        """
        if budget_mode == "generous":
            return list(available)

        prompt_lower = prompt.lower()
        min_matches = 2 if budget_mode == "minimal" else 1
        selected: List[str] = []

        for filename in available:
            keywords = MEMORY_FILE_KEYWORDS.get(filename, [])
            match_count = sum(1 for kw in keywords if kw in prompt_lower)
            if match_count >= min_matches:
                selected.append(filename)

        return selected

    def _parse_markdown_sections(self, content: str) -> List[Dict[str, Any]]:
        """Parse markdown content into sections by headers.

        Skips '#' characters inside fenced code blocks.
        Returns list of dicts with 'header', 'level', 'content'.
        """
        sections: List[Dict[str, Any]] = []
        lines = content.split("\n")
        current_header = ""
        current_level = 0
        current_lines: List[str] = []
        in_code_block = False

        for line in lines:
            stripped = line.strip()

            # Track fenced code blocks
            if stripped.startswith("```"):
                in_code_block = not in_code_block

            # Check for headers (only outside code blocks)
            if not in_code_block and stripped.startswith("#"):
                # Count header level
                level = 0
                for ch in stripped:
                    if ch == "#":
                        level += 1
                    else:
                        break

                if level <= 6 and (len(stripped) == level or stripped[level] == " "):
                    # Save previous section
                    if current_lines or current_header:
                        sections.append(
                            {
                                "header": current_header,
                                "level": current_level,
                                "content": "\n".join(current_lines),
                            }
                        )
                    current_header = stripped
                    current_level = level
                    current_lines = []
                    continue

            current_lines.append(line)

        # Save final section
        if current_lines or current_header:
            sections.append(
                {
                    "header": current_header,
                    "level": current_level,
                    "content": "\n".join(current_lines),
                }
            )

        return sections

    def _extract_relevant_sections(
        self,
        content: str,
        prompt: Optional[str],
        max_tokens: int,
    ) -> str:
        """Extract most relevant sections from content within token budget.

        If full content fits, returns as-is. Otherwise scores sections by
        keyword overlap with prompt, always includes preamble.
        """
        if estimate_tokens(content) <= max_tokens:
            return content

        if not prompt:
            # No prompt: just truncate
            target_chars = int(max_tokens * CHARS_PER_TOKEN) if max_tokens > 0 else 0
            return content[:target_chars]

        sections = self._parse_markdown_sections(content)
        if not sections:
            target_chars = int(max_tokens * CHARS_PER_TOKEN) if max_tokens > 0 else 0
            return content[:target_chars]

        prompt_lower = prompt.lower()
        prompt_words = set(prompt_lower.split())

        # Preamble: first section if it has no header (level 0)
        preamble = ""
        scorable: List[Tuple[int, Dict[str, Any]]] = []
        for section in sections:
            if not section["header"] and not preamble:
                preamble = section["content"]
            else:
                # Score by keyword overlap
                section_lower = (section["header"] + " " + section["content"]).lower()
                section_words = set(section_lower.split())
                score = len(prompt_words & section_words)
                scorable.append((score, section))

        # Sort by score descending
        scorable.sort(key=lambda x: x[0], reverse=True)

        # Build result within budget
        parts: List[str] = []
        used = 0
        total_sections = len(scorable)
        included = 0

        if preamble:
            preamble_tokens = estimate_tokens(preamble)
            if preamble_tokens <= max_tokens:
                parts.append(preamble)
                used += preamble_tokens

        for _score, section in scorable:
            section_text = section["header"] + "\n" + section["content"]
            section_tokens = estimate_tokens(section_text)
            if used + section_tokens <= max_tokens:
                parts.append(section_text)
                used += section_tokens
                included += 1
            else:
                break

        if included < total_sections:
            parts.append(f"\n*[Truncated: {included} of {total_sections} sections shown]*")

        return "\n\n".join(parts)

    def _load_memory_bank(
        self, prompt: Optional[str] = None
    ) -> Tuple[Dict[str, str], Dict[str, Dict[str, Any]]]:
        """Load memory bank files with on-demand selection and token budget.

        Returns (content dict, metadata dict).
        """
        auto_load_content: Dict[str, str] = {}
        on_demand_content: Dict[str, str] = {}
        metadata: Dict[str, Dict[str, Any]] = {}

        # Get configuration
        auto_load_files = self.config.get_memory_bank_files()
        all_on_demand_files = self.config.get_on_demand_files()
        token_budget = self.config.get_standing_context_tokens()

        # Get budget mode from settings
        memory_config = self.config.settings.get("memory_bank", {})
        budget_mode = memory_config.get("standing_context_budget", "balanced")
        staleness_days = memory_config.get("staleness_warning_days", 30)

        # Apply budget multiplier
        multiplier = MEMORY_BANK_BUDGET_MULTIPLIERS.get(budget_mode, 1.0)
        effective_budget = int(token_budget * multiplier)

        # Load auto_load files
        for filename in auto_load_files:
            content = self._validate_and_read_file(filename)
            if content is not None:
                auto_load_content[filename] = content
                filepath = self.memory_bank_path / filename
                staleness = self._get_file_staleness(filepath, staleness_days)
                metadata[filename] = {
                    "category": "auto_load",
                    "tokens": estimate_tokens(content),
                    **staleness,
                }

        # Select and load on-demand files
        if prompt and all_on_demand_files:
            selected_on_demand = self._select_on_demand_files(
                prompt, all_on_demand_files, budget_mode
            )
        else:
            selected_on_demand = []

        for filename in selected_on_demand:
            if filename in auto_load_content:
                continue  # Already loaded as auto_load
            content = self._validate_and_read_file(filename)
            if content is not None:
                on_demand_content[filename] = content
                filepath = self.memory_bank_path / filename
                staleness = self._get_file_staleness(filepath, staleness_days)
                metadata[filename] = {
                    "category": "on_demand",
                    "tokens": estimate_tokens(content),
                    **staleness,
                }

        # Enforce token budget
        final_content, token_counts = self._enforce_token_budget(
            auto_load_content, on_demand_content, effective_budget, prompt
        )

        # Update metadata with final token counts
        for filename, tokens in token_counts.items():
            if filename in metadata:
                metadata[filename]["tokens"] = tokens

        return final_content, metadata

    def _get_project_info(self) -> Dict[str, Any]:
        """Get basic project information"""
        project_name = self.config.settings.get("project_name", "unknown")

        return {
            "name": project_name,
            "root": str(self.root),
            "orchestration_mode": self.config.get_orchestration_mode(),
            "enabled_providers": self.config.get_enabled_providers(),
        }

    def _validate_safe_path(self, path: Path) -> Path:
        """
        Validate path is safe and within expected boundaries.

        Delegates to shared security_utils.validate_safe_path().
        """
        return validate_safe_path(path)

    def _get_git_context(self) -> Optional[Dict[str, str]]:
        """Get git context if available"""
        import subprocess

        try:
            # Validate root path before using in subprocess
            safe_root = self._validate_safe_path(self.root)

            # Get current branch
            branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-re", "HEAD"],
                cwd=safe_root,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=5,  # Add timeout for security
            ).strip()

            # Get last commit
            last_commit = subprocess.check_output(
                ["git", "log", "-1", "--oneline"],
                cwd=safe_root,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=5,
            ).strip()

            # Get status (short)
            status = subprocess.check_output(
                ["git", "status", "--short"],
                cwd=safe_root,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=5,
            ).strip()

            return {
                "branch": branch,
                "last_commit": last_commit,
                "status": status if status else "(clean)",
            }

        except (
            subprocess.CalledProcessError,
            subprocess.TimeoutExpired,
            FileNotFoundError,
            ValueError,
        ):
            # Git not available, timeout, or invalid path
            return None

    def _detect_active_skills(self) -> Optional[List[str]]:
        """
        Detect currently active skills using Dev-AID's context detection

        Returns:
            List of active skill names, or None if detection fails
        """
        import subprocess

        try:
            # Validate root path
            safe_root = self._validate_safe_path(self.root)

            # Path to orchestration scripts
            orchestration_dir = safe_root / ".dev-aid" / "orchestration"
            detect_context_script = orchestration_dir / "detect-context-enhanced.sh"
            select_skills_script = orchestration_dir / "select-skills.sh"

            # Fall back to basic detect-context.sh if enhanced version doesn't exist
            if not detect_context_script.exists():
                detect_context_script = orchestration_dir / "detect-context.sh"

            # Check if scripts exist
            if not detect_context_script.exists() or not select_skills_script.exists():
                return None

            # Step 1: Detect project context
            context_output = subprocess.check_output(
                [str(detect_context_script), str(safe_root)],
                cwd=safe_root,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=10,
            ).strip()

            if not context_output:
                return None

            # Step 2: Select skills based on context
            skills_output = subprocess.check_output(
                [str(select_skills_script), context_output, "10"],
                cwd=safe_root,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=5,
            ).strip()

            if not skills_output:
                return None

            # Parse skills (one per line)
            skills = [skill.strip() for skill in skills_output.split("\n") if skill.strip()]

            return skills if skills else None

        except (
            subprocess.CalledProcessError,
            subprocess.TimeoutExpired,
            FileNotFoundError,
            ValueError,
            Exception,
        ):
            # Skill detection failed, return None
            # Don't raise exception - this is optional context
            return None

    async def _get_git_context_async(self) -> Optional[Dict[str, str]]:
        """Get git context using async subprocess (non-blocking)"""
        try:
            safe_root = self._validate_safe_path(self.root)
            safe_root_str = str(safe_root)

            async def _run_git(args: List[str]) -> str:
                proc = await asyncio.create_subprocess_exec(
                    "git",
                    *args,
                    cwd=safe_root_str,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.DEVNULL,
                )
                stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=5)
                if proc.returncode != 0:
                    raise RuntimeError(f"git {args[0]} failed")
                return stdout.decode().strip()

            branch, last_commit, status = await asyncio.gather(
                _run_git(["rev-parse", "--abbrev-ref", "HEAD"]),
                _run_git(["log", "-1", "--oneline"]),
                _run_git(["status", "--short"]),
            )

            return {
                "branch": branch,
                "last_commit": last_commit,
                "status": status if status else "(clean)",
            }
        except (OSError, RuntimeError, asyncio.TimeoutError) as e:
            logger.debug("Async git context detection failed: %s", e)
            return None

    async def _detect_active_skills_async(self) -> Optional[List[str]]:
        """Detect active skills using async subprocess (non-blocking)"""
        try:
            safe_root = self._validate_safe_path(self.root)
            orchestration_dir = safe_root / ".dev-aid" / "orchestration"
            detect_context_script = orchestration_dir / "detect-context-enhanced.sh"
            select_skills_script = orchestration_dir / "select-skills.sh"

            if not detect_context_script.exists():
                detect_context_script = orchestration_dir / "detect-context.sh"

            if not detect_context_script.exists() or not select_skills_script.exists():
                return None

            # Step 1: Detect project context
            proc = await asyncio.create_subprocess_exec(
                str(detect_context_script),
                str(safe_root),
                cwd=str(safe_root),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
            if proc.returncode != 0:
                return None
            context_output = stdout.decode().strip()
            if not context_output:
                return None

            # Step 2: Select skills based on context
            proc = await asyncio.create_subprocess_exec(
                str(select_skills_script),
                context_output,
                "10",
                cwd=str(safe_root),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=5)
            if proc.returncode != 0:
                return None
            skills_output = stdout.decode().strip()
            if not skills_output:
                return None

            skills = [s.strip() for s in skills_output.split("\n") if s.strip()]
            return skills if skills else None
        except Exception:
            return None

    async def build_context_async(
        self,
        include_memory: bool = True,
        prompt: Optional[str] = None,
    ) -> "DevAIDContext":
        """
        Build complete Dev-AID context using async subprocess calls

        Args:
            include_memory: Whether to include memory bank files
            prompt: Optional user prompt for query-aware on-demand loading

        Returns:
            DevAIDContext object
        """
        memory_bank: Dict[str, str] = {}
        memory_bank_metadata: Dict[str, Dict[str, Any]] = {}
        if include_memory:
            memory_bank, memory_bank_metadata = self._load_memory_bank(prompt=prompt)

        project_info = self._get_project_info()

        # Run git context and skill detection concurrently
        git_context, active_skills = await asyncio.gather(
            self._get_git_context_async(),
            self._detect_active_skills_async(),
        )

        return DevAIDContext(
            memory_bank=memory_bank,
            project_info=project_info,
            git_context=git_context,
            active_skills=active_skills,
            memory_bank_metadata=memory_bank_metadata,
        )

    async def _get_codebase_size(self) -> Dict[str, Any]:
        """Query codebase size from local search index."""
        cache_key = self._cache_key("__index_status__", "code-search")
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        result: Dict[str, Any] = {
            "total_chunks": 0,
            "indexed_files_count": 0,
            "size_category": "small",
        }

        try:
            if self.mcp_pool and "code-search" in self.mcp_pool.clients:
                status = await self.mcp_pool.call_tool(
                    "code-search",
                    "get_index_status",
                    {"project_path": str(self.root)},
                )
                total_chunks = status.get("total_chunks", 0)
                indexed_files = status.get("indexed_files", [])
                file_count = len(indexed_files) if isinstance(indexed_files, list) else 0
                result["total_chunks"] = total_chunks
                result["indexed_files_count"] = file_count

                if (
                    file_count > CODEBASE_SIZE_MEDIUM_MAX_FILES
                    or total_chunks > CODEBASE_SIZE_MEDIUM_MAX_CHUNKS
                ):
                    result["size_category"] = "large"
                elif (
                    file_count > CODEBASE_SIZE_SMALL_MAX_FILES
                    or total_chunks > CODEBASE_SIZE_SMALL_MAX_CHUNKS
                ):
                    result["size_category"] = "medium"
        except Exception as e:
            logger.debug("Codebase size detection failed: %s", e)

        self._set_cached(cache_key, result, ttl=CODEBASE_SIZE_CACHE_TTL)
        return result

    @staticmethod
    def _server_context_key(server_name: str) -> str:
        """Map MCP server name to context dictionary key."""
        if server_name == "code-search":
            return "code_search"
        elif server_name == "deep-research":
            return "external_research"
        elif "postgres" in server_name or "database" in server_name:
            return "database_schema"
        elif "github" in server_name:
            return "github"
        return server_name

    async def gather_mcp_context(
        self,
        prompt: str,
        task_type: Optional[str] = None,
        requested_servers: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Gather context from MCP servers

        Args:
            prompt: User's prompt/query
            task_type: Type of task (database, github, etc.) for smart MCP selection
            requested_servers: Specific MCP servers to query

        Returns:
            Dict of MCP context
        """
        if not self.mcp_pool:
            return {}

        mcp_context: Dict[str, Any] = {}

        try:
            # Detect codebase size for adaptive search depth
            codebase_info = await self._get_codebase_size()
            size_category = codebase_info.get("size_category", "small")
            search_top_k = CODEBASE_SEARCH_TOP_K.get(size_category, 5)

            # Auto-select MCPs based on task type if not specified
            if requested_servers is None:
                requested_servers = self._auto_select_mcps(
                    prompt, task_type, size_category=size_category
                )

            # Gather context from all servers in parallel
            async def _query_server(
                server_name: str,
            ) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
                """Query a single MCP server, returning (context_key, result)"""
                # Check cache first
                cache_key = self._cache_key(prompt, server_name)
                cached = self._get_cached(cache_key)
                if cached is not None:
                    return (self._server_context_key(server_name), cached)

                context_key: Optional[str] = None
                result: Optional[Dict[str, Any]] = None
                try:
                    if server_name == "code-search":
                        context_key = "code_search"
                        result = await self._query_code_search(prompt, top_k=search_top_k)
                    elif server_name == "deep-research":
                        context_key = "external_research"
                        result = await self._query_deep_research(prompt)
                    elif "postgres" in server_name or "database" in server_name:
                        context_key = "database_schema"
                        result = await self._query_database_schema(server_name)
                    elif "github" in server_name:
                        context_key = "github"
                        result = await self._query_github_context(server_name, prompt)
                except Exception as e:
                    logger.warning("Failed to gather context from %s: %s", server_name, e)

                # Cache successful results
                if context_key and result:
                    self._set_cached(cache_key, result)
                    return (context_key, result)

                return (None, None)

            gather_results = await asyncio.gather(
                *[_query_server(s) for s in requested_servers],
                return_exceptions=True,
            )

            for r in gather_results:
                if isinstance(r, BaseException):
                    logger.warning("MCP server query failed: %s", r)
                    continue
                key, value = r
                if key and value:
                    mcp_context[key] = value

            # Check if external research is needed as fallback
            if self._needs_external_research(prompt, mcp_context):
                research_result = await self._trigger_research_fallback(prompt)
                if research_result:
                    mcp_context["external_research"] = research_result

        except Exception as e:
            logger.error("Error gathering MCP context: %s", e)

        return mcp_context

    def _needs_external_research(self, prompt: str, context: Dict[str, Any]) -> bool:
        """
        Determine if external research is needed based on context.

        Triggers research when:
        1. Local code search returned empty or insufficient results
        2. Query contains research-indicating keywords
        3. Explicit external knowledge request

        Args:
            prompt: User's prompt
            context: Currently gathered MCP context

        Returns:
            True if external research should be triggered
        """
        # Skip if research already gathered
        if "external_research" in context:
            return False

        # Check if deep-research MCP is available
        if not self.mcp_pool or "deep-research" not in self.mcp_pool.clients:
            return False

        prompt_lower = prompt.lower()

        # Keywords that indicate need for external research
        research_keywords = [
            "latest",
            "current version",
            "best practice",
            "best practices",
            "compare",
            "comparison",
            "alternatives",
            "documentation",
            "how to",
            "tutorial",
            "library",
            "framework",
            "2024",
            "2025",
            "2026",
            "new feature",
            "recently",
            "updated",
        ]

        # Check for research keywords
        has_research_keywords = any(kw in prompt_lower for kw in research_keywords)

        # Check if local search returned empty
        code_search = context.get("code_search", {})
        search_results = code_search.get("search_results", [])
        local_search_empty = len(search_results) == 0

        # Explicit research request
        explicit_research = "research" in prompt_lower or "external" in prompt_lower

        return (local_search_empty and has_research_keywords) or explicit_research

    async def _trigger_research_fallback(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Trigger external research via deep-research MCP server.

        Args:
            prompt: User's prompt to research

        Returns:
            Research result dictionary or None if failed
        """
        try:
            if not self.mcp_pool or "deep-research" not in self.mcp_pool.clients:
                return None

            result = await self.mcp_pool.call_tool(
                "deep-research",
                "research",
                {
                    "query": prompt,
                    "depth": "auto",
                    "use_cache": True,
                    "prefer_speed": True,  # Prefer faster results for context gathering
                },
            )

            if result:
                return {
                    "source": "deep-research",
                    "content": result.get("content", ""),
                    "citations": result.get("citations", []),
                    "provider": result.get("provider", ""),
                    "cached": result.get("cached", False),
                    "routing_reasoning": result.get("routing_reasoning", ""),
                }

            return None

        except Exception as e:
            logger.warning("Research fallback failed: %s", e)
            return None

    async def _query_deep_research(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Query Deep Research MCP for external knowledge.

        Args:
            prompt: Research query

        Returns:
            Research result or None
        """
        try:
            result = await self.mcp_pool.call_tool(
                "deep-research",
                "research",
                {
                    "query": prompt,
                    "depth": "auto",
                    "use_cache": True,
                },
            )

            if result:
                return {
                    "source": "deep-research",
                    "content": result.get("content", ""),
                    "citations": result.get("citations", []),
                    "provider": result.get("provider", ""),
                    "cached": result.get("cached", False),
                }

            return None

        except Exception as e:
            logger.warning("Deep research query failed: %s", e)
            return None

    def _auto_select_mcps(
        self,
        prompt: str,
        task_type: Optional[str],
        size_category: str = "small",
    ) -> List[str]:
        """
        Automatically select which MCP servers to query based on prompt/task type

        Args:
            prompt: User's prompt
            task_type: Task type classification
            size_category: Codebase size ("small", "medium", "large")

        Returns:
            List of MCP server names to query
        """
        selected: List[str] = []
        prompt_lower = prompt.lower()

        # Always include code-search if available
        if self.mcp_pool and "code-search" in self.mcp_pool.clients:
            selected.append("code-search")

        # Database-related
        if task_type == "database" or any(
            kw in prompt_lower
            for kw in ["database", "db", "sql", "query", "table", "schema", "migration"]
        ):
            for server_name in self.mcp_pool.clients.keys():
                if "postgres" in server_name or "mysql" in server_name or "sqlite" in server_name:
                    selected.append(server_name)
                    break

        # GitHub-related
        if task_type == "github" or any(
            kw in prompt_lower
            for kw in ["github", "issue", "pr", "pull request", "bug", "feature request"]
        ):
            for server_name in self.mcp_pool.clients.keys():
                if "github" in server_name:
                    selected.append(server_name)
                    break

        # Filesystem operations
        if any(kw in prompt_lower for kw in ["file", "directory", "folder", "path"]):
            for server_name in self.mcp_pool.clients.keys():
                if "filesystem" in server_name or "fs" in server_name:
                    selected.append(server_name)
                    break

        # Research-related (explicit request or large codebase with broad queries)
        research_keywords = [
            "research",
            "latest version",
            "best practice",
            "compare",
            "alternatives",
            "documentation",
        ]
        broad_impl_keywords = ["implement", "build", "create", "design", "architect"]
        needs_research = task_type == "research" or any(
            kw in prompt_lower for kw in research_keywords
        )
        # Large codebases with broad implementation queries also benefit from research
        if not needs_research and size_category == "large":
            needs_research = any(kw in prompt_lower for kw in broad_impl_keywords)

        if needs_research:
            if self.mcp_pool and "deep-research" in self.mcp_pool.clients:
                selected.append("deep-research")

        return selected

    async def _query_code_search(self, prompt: str, top_k: int = 5) -> Optional[Dict[str, Any]]:
        """Query Dev-AID Local Search MCP"""
        try:
            # Extract search query from prompt
            search_terms = self._extract_search_terms(prompt)

            result = await self.mcp_pool.call_tool(
                "code-search",
                "search_code",
                {"query": search_terms, "limit": top_k},
            )

            return {"search_results": result.get("content", []), "query": search_terms}

        except Exception as e:
            logger.warning("Code search failed: %s", e)
            return None

    async def _query_database_schema(self, server_name: str) -> Optional[Dict[str, Any]]:
        """Query database schema from postgres/mysql MCP"""
        try:
            # Try to get schema information
            result = await self.mcp_pool.call_tool(server_name, "get_schema", {})

            return {"schema": result, "server": server_name}

        except Exception as e:
            logger.warning("Database schema query failed: %s", e)
            return None

    async def _query_github_context(
        self, server_name: str, prompt: str
    ) -> Optional[Dict[str, Any]]:
        """Query GitHub issues/PRs"""
        try:
            # Extract issue/PR numbers or search terms
            search_query = self._extract_search_terms(prompt)

            result = await self.mcp_pool.call_tool(
                server_name, "search_issues", {"query": search_query, "limit": 3}
            )

            return {"issues": result.get("issues", []), "query": search_query}

        except Exception as e:
            logger.warning("GitHub query failed: %s", e)
            return None

    def _extract_search_terms(self, prompt: str) -> str:
        """Extract meaningful search terms from prompt"""
        # Simple extraction - remove common words
        stop_words = {
            "the",
            "a",
            "an",
            "is",
            "are",
            "was",
            "were",
            "find",
            "show",
            "get",
            "how",
            "what",
            "where",
        }
        words = prompt.lower().split()
        search_terms = " ".join(word for word in words if word not in stop_words)
        return search_terms[:100]  # Limit length

    def format_context_for_ai(self, context: DevAIDContext) -> str:
        """
        Format context as string for AI system prompt

        Args:
            context: DevAIDContext object

        Returns:
            Formatted context string
        """
        sections = []

        # Project info
        sections.append("# Project Context")
        sections.append(f"Project: {context.project_info.get('name', 'Unknown')}")
        if "orchestration_mode" in context.project_info:
            sections.append(f"Orchestration Mode: {context.project_info['orchestration_mode']}")

        # Active skills
        if context.active_skills:
            sections.append("\n## Active Skills")
            sections.append("The following Dev-AID skills are active for this project:")
            for skill in context.active_skills:
                sections.append(f"  - {skill}")

        if context.git_context:
            sections.append("\n## Git Context")
            if "branch" in context.git_context:
                sections.append(f"Branch: {context.git_context['branch']}")
            if "last_commit" in context.git_context:
                sections.append(f"Last Commit: {context.git_context['last_commit']}")
            if "status" in context.git_context:
                sections.append(f"Status: {context.git_context['status']}")

        # Memory bank
        if context.memory_bank:
            sections.append("\n## Memory Bank")
            for filename, content in context.memory_bank.items():
                # Special handling for activeContext.md
                if filename == "activeContext.md":
                    sections.append("\n### Active Context")
                else:
                    sections.append(f"\n### {filename}")

                # Add staleness annotation if metadata available
                file_meta = context.memory_bank_metadata.get(filename, {})
                if file_meta:
                    age_human = file_meta.get("age_human", "")
                    tokens = file_meta.get("tokens", 0)
                    is_stale = file_meta.get("is_stale", False)
                    if is_stale:
                        sections.append(
                            f"*Last updated: {age_human}"
                            f" — WARNING: may be outdated | {tokens} tokens*"
                        )
                    elif age_human:
                        sections.append(f"*Last updated: {age_human} | {tokens} tokens*")

                sections.append(content)

            # Write-back maintenance reminder
            sections.append("\n### Memory Bank Maintenance")
            sections.append(
                "Update relevant .dev-aid/memory-bank/ files when you"
                " establish new patterns,\nmake architecture decisions,"
                " or identify security concerns. Append with timestamps.\n"
                "Always update activeContext.md at session end."
            )

        # MCP Context
        if context.mcp_context:
            sections.append("\n## MCP Context (From External Tools)")

            if "code_search" in context.mcp_context:
                sections.append("\n### Code Search Results")
                cs = context.mcp_context["code_search"]
                sections.append(f"Query: {cs.get('query', '')}")
                sections.append("Relevant code found in your codebase:")
                for result in cs.get("search_results", [])[:5]:
                    sections.append(f"  - {result}")

            if "database_schema" in context.mcp_context:
                sections.append("\n### Database Schema")
                db = context.mcp_context["database_schema"]
                sections.append(f"Server: {db.get('server', '')}")
                sections.append("Schema information:")
                sections.append(str(db.get("schema", ""))[:1000])  # Limit size

            if "github" in context.mcp_context:
                sections.append("\n### GitHub Issues/PRs")
                gh = context.mcp_context["github"]
                sections.append(f"Search: {gh.get('query', '')}")
                sections.append("Related issues:")
                for issue in gh.get("issues", [])[:3]:
                    sections.append(f"  - {issue}")

            if "external_research" in context.mcp_context:
                sections.append("\n### External Research")
                research = context.mcp_context["external_research"]
                sections.append(f"Provider: {research.get('provider', 'unknown')}")
                if research.get("cached"):
                    sections.append("(Cached result)")
                sections.append("\nResearch findings:")
                content = research.get("content", "")
                # Limit content size for context
                sections.append(content[:2000] if len(content) > 2000 else content)
                if research.get("citations"):
                    sections.append("\nSources:")
                    for citation in research.get("citations", [])[:5]:
                        sections.append(f"  - {citation}")

        return "\n".join(sections)

    def get_minimal_context(self) -> str:
        """
        Get minimal context (just active context)

        Returns:
            Minimal context string
        """
        active_context_file = self.memory_bank_path / "activeContext.md"

        if active_context_file.exists():
            try:
                with open(active_context_file, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                pass

        return "No active context available."


def build_system_prompt(context: DevAIDContext, context_builder: ContextBuilder) -> str:
    """
    Build system prompt with Dev-AID context

    Args:
        context: DevAIDContext object
        context_builder: ContextBuilder instance

    Returns:
        System prompt string
    """
    base_prompt = """You are an expert AI development assistant powered by Dev-AID.

You have access to project context, memory bank, and coding best practices.

Your role:
- Follow established patterns from the memory bank
- Apply security best practices
- Write clean, maintainable code
- Consider performance implications
- Document your decisions

Project Context:
"""

    context_str = context_builder.format_context_for_ai(context)

    return base_prompt + "\n" + context_str


# Example usage
if __name__ == "__main__":
    from config_loader import load_config

    try:
        config = load_config()
        builder = ContextBuilder(config)

        print("Building context...")
        context = builder.build_context()

        print("\n✅ Context built successfully")
        print(f"   Memory Bank Files: {len(context.memory_bank)}")
        print(f"   Project: {context.project_info['name']}")

        if context.git_context:
            print(f"   Git Branch: {context.git_context['branch']}")

        print("\n📝 System Prompt Preview:")
        print("=" * 60)
        system_prompt = build_system_prompt(context, builder)
        print(system_prompt[:500] + "..." if len(system_prompt) > 500 else system_prompt)

    except Exception as e:
        print(f"❌ Error: {e}")
