"""
Context Builder for Dev-AID Router

Gathers relevant context from:
- Memory bank files
- Active skills
- Git context
- Project structure
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class DevAIDContext:
    """Represents Dev-AID context for AI request"""
    memory_bank: Dict[str, str]  # filename -> content
    project_info: Dict[str, Any]
    git_context: Optional[Dict[str, str]] = None
    active_skills: Optional[List[str]] = None


class ContextBuilder:
    """Builds context from Dev-AID configuration and state"""

    def __init__(self, config_loader):
        """
        Initialize context builder

        Args:
            config_loader: ConfigLoader instance
        """
        self.config = config_loader
        self.root = config_loader.root
        self.memory_bank_path = config_loader.get_memory_bank_path()

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

        return DevAIDContext(
            memory_bank=memory_bank,
            project_info=project_info,
            git_context=git_context,
            active_skills=None  # TODO: Implement skill detection
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
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        memory_bank[filename] = content
                except Exception as e:
                    # Log error but continue
                    print(f"Warning: Could not read {filename}: {e}")

        return memory_bank

    def _get_project_info(self) -> Dict[str, Any]:
        """Get basic project information"""
        project_name = self.config.settings.get("project_name", "unknown")

        return {
            "name": project_name,
            "root": str(self.root),
            "orchestration_mode": self.config.get_orchestration_mode(),
            "enabled_providers": self.config.get_enabled_providers()
        }

    def _get_git_context(self) -> Optional[Dict[str, str]]:
        """Get git context if available"""
        import subprocess

        try:
            # Get current branch
            branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.root,
                stderr=subprocess.DEVNULL,
                text=True
            ).strip()

            # Get last commit
            last_commit = subprocess.check_output(
                ["git", "log", "-1", "--oneline"],
                cwd=self.root,
                stderr=subprocess.DEVNULL,
                text=True
            ).strip()

            # Get status (short)
            status = subprocess.check_output(
                ["git", "status", "--short"],
                cwd=self.root,
                stderr=subprocess.DEVNULL,
                text=True
            ).strip()

            return {
                "branch": branch,
                "last_commit": last_commit,
                "status": status if status else "(clean)"
            }

        except (subprocess.CalledProcessError, FileNotFoundError):
            # Git not available or not a git repo
            return None

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
        sections.append(f"Project: {context.project_info['name']}")
        sections.append(f"Orchestration Mode: {context.project_info['orchestration_mode']}")

        if context.git_context:
            sections.append(f"\n## Git Context")
            sections.append(f"Branch: {context.git_context['branch']}")
            sections.append(f"Last Commit: {context.git_context['last_commit']}")
            sections.append(f"Status: {context.git_context['status']}")

        # Memory bank
        if context.memory_bank:
            sections.append(f"\n## Memory Bank")
            for filename, content in context.memory_bank.items():
                sections.append(f"\n### {filename}")
                sections.append(content)

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
                with open(active_context_file, 'r', encoding='utf-8') as f:
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

        print(f"\n✅ Context built successfully")
        print(f"   Memory Bank Files: {len(context.memory_bank)}")
        print(f"   Project: {context.project_info['name']}")

        if context.git_context:
            print(f"   Git Branch: {context.git_context['branch']}")

        print(f"\n📝 System Prompt Preview:")
        print("=" * 60)
        system_prompt = build_system_prompt(context, builder)
        print(system_prompt[:500] + "..." if len(system_prompt) > 500 else system_prompt)

    except Exception as e:
        print(f"❌ Error: {e}")
