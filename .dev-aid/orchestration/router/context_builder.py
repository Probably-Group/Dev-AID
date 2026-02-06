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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

from .security_utils import validate_safe_path

logger = logging.getLogger(__name__)


@runtime_checkable
class ConfigLoaderProtocol(Protocol):
    """Protocol describing the ConfigLoader interface used by ContextBuilder."""

    root: Path
    settings: Dict[str, Any]

    def get_memory_bank_path(self) -> Path: ...

    def get_memory_bank_files(self) -> List[str]: ...

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

    def build_context(self, include_memory: bool = True) -> DevAIDContext:
        """
        Build complete Dev-AID context

        Args:
            include_memory: Whether to include memory bank files

        Returns:
            DevAIDContext object
        """
        memory_bank = {}
        if include_memory:
            memory_bank = self._load_memory_bank()

        project_info = self._get_project_info()
        git_context = self._get_git_context()
        active_skills = self._detect_active_skills()

        return DevAIDContext(
            memory_bank=memory_bank,
            project_info=project_info,
            git_context=git_context,
            active_skills=active_skills,
        )

    def _load_memory_bank(self) -> Dict[str, str]:
        """Load memory bank files"""
        memory_bank = {}

        # Get files to auto-load
        auto_load_files = self.config.get_memory_bank_files()

        for filename in auto_load_files:
            filepath = self.memory_bank_path / filename

            if filepath.exists():
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        memory_bank[filename] = content
                except Exception as e:
                    # Log error but continue
                    logger.warning("Could not read %s: %s", filename, e)

        return memory_bank

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
        except Exception:
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

    async def build_context_async(self, include_memory: bool = True) -> "DevAIDContext":
        """
        Build complete Dev-AID context using async subprocess calls

        Args:
            include_memory: Whether to include memory bank files

        Returns:
            DevAIDContext object
        """
        memory_bank = {}
        if include_memory:
            memory_bank = self._load_memory_bank()

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
        )

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

        mcp_context = {}

        try:
            # Auto-select MCPs based on task type if not specified
            if requested_servers is None:
                requested_servers = self._auto_select_mcps(prompt, task_type)

            # Gather context from all servers in parallel
            async def _query_server(
                server_name: str,
            ) -> tuple[Optional[str], Optional[Dict[str, Any]]]:
                """Query a single MCP server, returning (context_key, result)"""
                try:
                    if server_name == "code-search":
                        return ("code_search", await self._query_code_search(prompt))
                    elif server_name == "deep-research":
                        return ("external_research", await self._query_deep_research(prompt))
                    elif "postgres" in server_name or "database" in server_name:
                        return (
                            "database_schema",
                            await self._query_database_schema(server_name),
                        )
                    elif "github" in server_name:
                        return (
                            "github",
                            await self._query_github_context(server_name, prompt),
                        )
                except Exception as e:
                    logger.warning("Failed to gather context from %s: %s", server_name, e)
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

    def _auto_select_mcps(self, prompt: str, task_type: Optional[str]) -> List[str]:
        """
        Automatically select which MCP servers to query based on prompt/task type

        Args:
            prompt: User's prompt
            task_type: Task type classification

        Returns:
            List of MCP server names to query
        """
        selected = []
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

        # Research-related (explicit request)
        research_keywords = [
            "research",
            "latest version",
            "best practice",
            "compare",
            "alternatives",
            "documentation",
        ]
        if task_type == "research" or any(kw in prompt_lower for kw in research_keywords):
            if self.mcp_pool and "deep-research" in self.mcp_pool.clients:
                selected.append("deep-research")

        return selected

    async def _query_code_search(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Query Dev-AID Local Search MCP"""
        try:
            # Extract search query from prompt
            search_terms = self._extract_search_terms(prompt)

            result = await self.mcp_pool.call_tool(
                "code-search", "search", {"query": search_terms, "limit": 5}
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
                sections.append(content)

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
