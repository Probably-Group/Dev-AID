"""Merge Conflict Resolver agent definition."""

from ..core.models import AgentDefinition

CONFLICT_RESOLVER = AgentDefinition(
    name="conflict-resolver",
    description="Auto-resolve merge conflicts intelligently",
    skills=["senior-architect"],
    tools=[
        "read_file",
        "write_file",
        "run_bash",
        "git_status",
        "git_diff",
        "grep_search",
    ],
    system_prompt_extra="""You are a merge conflict resolution specialist. Your task:

1. Check git status to identify conflicted files
2. For each conflicted file:
   a. Read the file to see the conflict markers
   b. Understand the intent of BOTH sides (ours and theirs)
   c. Read surrounding code for context
   d. Resolve the conflict by combining both changes intelligently
3. After resolving, verify the code is syntactically correct
4. Stage the resolved files

Resolution strategies:
- **Both additions**: Keep both, ordering logically
- **Competing changes**: Understand intent, pick the more complete version or merge both
- **Structural conflicts**: Ensure the final structure is consistent
- **Import conflicts**: Deduplicate and sort
- Never blindly pick one side — understand what each change does""",
    max_iterations=15,
    temperature=0.3,
    risk_level="moderate",
    output_format="markdown",
)
