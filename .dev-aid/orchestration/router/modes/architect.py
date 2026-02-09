#!/usr/bin/env python3
"""
Architect Mode Router

Implements the two-agent architect pattern:
1. Architect agent analyzes and creates implementation plan
2. User approves/modifies plan
3. Implementer agent executes the plan

This is a reference implementation - actual orchestration depends on
the AI provider's capabilities.
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional, cast


class PlanStatus(Enum):
    """Status of an implementation plan."""

    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ImplementationPlan:
    """Structured implementation plan from architect."""

    summary: str
    affected_files: list[dict[str, Any]]
    implementation_steps: list[str]
    success_criteria: list[str]
    risks: list[dict[str, Any]] = field(default_factory=list)
    alternatives: list[str] = field(default_factory=list)
    testing_strategy: str = ""
    status: PlanStatus = PlanStatus.DRAFT

    def to_markdown(self) -> str:
        """Convert plan to markdown format."""
        md = []
        md.append(f"## Summary\n{self.summary}\n")

        md.append("## Affected Files")
        for f in self.affected_files:
            action = f.get("action", "modify")
            desc = f.get("description", "")
            if action == "new":
                md.append(f"- `{f['path']}` - **NEW**: {desc}")
            else:
                md.append(f"- `{f['path']}` - {desc}")
        md.append("")

        md.append("## Implementation Steps")
        for i, step in enumerate(self.implementation_steps, 1):
            md.append(f"{i}. {step}")
        md.append("")

        md.append("## Success Criteria")
        for criterion in self.success_criteria:
            md.append(f"- [ ] {criterion}")
        md.append("")

        if self.risks:
            md.append("## Risks & Mitigations")
            for risk in self.risks:
                md.append(f"- **Risk**: {risk.get('risk', 'Unknown')}")
                md.append(f"  - **Mitigation**: {risk.get('mitigation', 'TBD')}")
            md.append("")

        if self.alternatives:
            md.append("## Alternative Approaches")
            for alt in self.alternatives:
                md.append(f"- {alt}")
            md.append("")

        if self.testing_strategy:
            md.append(f"## Testing Strategy\n{self.testing_strategy}\n")

        return "\n".join(md)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ImplementationPlan":
        """Create plan from dictionary."""
        return cls(
            summary=data.get("summary", ""),
            affected_files=data.get("affected_files", []),
            implementation_steps=data.get("implementation_steps", []),
            success_criteria=data.get("success_criteria", []),
            risks=data.get("risks", []),
            alternatives=data.get("alternatives", []),
            testing_strategy=data.get("testing_strategy", ""),
            status=PlanStatus(data.get("status", "draft")),
        )


class ArchitectMode:
    """
    Architect mode orchestrator.

    Coordinates between architect and implementer agents.
    """

    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path)
        self.current_plan: Optional[ImplementationPlan] = None

    def _load_config(self, config_path: Optional[Path] = None) -> dict[str, Any]:
        """Load orchestration config."""
        if config_path is None:
            # Find project root
            cwd = Path.cwd()
            for parent in [cwd] + list(cwd.parents):
                config_file = parent / ".dev-aid" / "config" / "orchestration.json"
                if config_file.exists():
                    config_path = config_file
                    break

        if config_path and config_path.exists():
            with open(config_path) as f:
                full_config: dict[str, Any] = json.load(f)
                result: dict[str, Any] = full_config.get("architect", {})
                return result

        # Default config
        return {
            "enabled": False,
            "architect_model": "claude-opus-4.5",
            "implementer_model": "claude-sonnet-4.5",
        }

    @property
    def is_enabled(self) -> bool:
        """Check if architect mode is enabled."""
        return cast(bool, self.config.get("enabled", False))

    @property
    def architect_model(self) -> str:
        """Get architect model identifier."""
        return cast(str, self.config.get("architect_model", "claude-opus-4.5"))

    @property
    def implementer_model(self) -> str:
        """Get implementer model identifier."""
        return cast(str, self.config.get("implementer_model", "claude-sonnet-4.5"))

    def should_activate(self, task_description: str, estimated_files: int = 0) -> bool:
        """
        Determine if architect mode should activate for this task.

        Args:
            task_description: Description of the task
            estimated_files: Estimated number of files to change

        Returns:
            True if architect mode should be used
        """
        if not self.is_enabled:
            return False

        triggers = self.config.get("triggers", {}).get("auto_activate", {})
        if not triggers.get("enabled", False):
            return False

        conditions = triggers.get("conditions", {})

        # Check file count trigger
        if estimated_files > conditions.get("estimated_file_changes_gt", 999):
            return True

        # Check keyword triggers
        keywords = conditions.get("keywords", [])
        task_lower = task_description.lower()
        for keyword in keywords:
            if keyword.lower() in task_lower:
                return True

        return False

    def get_architect_prompt(self, task: str, context: str = "") -> str:
        """
        Generate the architect's system prompt.

        Args:
            task: The user's task description
            context: Additional context (code snippets, requirements, etc.)

        Returns:
            System prompt for the architect agent
        """
        plan_sections = self.config.get("plan_format", {}).get(
            "required_sections",
            [
                "## Summary",
                "## Affected Files",
                "## Implementation Steps",
                "## Success Criteria",
                "## Risks & Mitigations",
            ],
        )

        return (
            f"""You are an expert software architect. """
            f"""Your role is to analyze requirements and create a detailed implementation plan.

## Your Task
{task}

## Context
{context if context else "No additional context provided."}

## Instructions

1. **Analyze** the requirements thoroughly
2. **Explore** the existing codebase to understand current architecture
3. **Design** a solution that fits the existing patterns
4. **Document** your plan in the required format

## Output Format

You MUST produce a plan with these sections:
{chr(10).join(f"- {section}" for section in plan_sections)}

## Constraints

- **DO NOT** write any implementation code
- **DO** read and reference existing code
- **DO** be specific about file paths and changes
- **DO** consider edge cases and error handling
- **DO** make steps actionable (not vague)

## Example Plan Structure

```markdown
## Summary
[1-2 sentences describing what will be built]

## Affected Files
- `src/auth/login.ts` - Add OAuth2 flow
- `src/auth/types.ts` - Add OAuth token types
- `src/auth/oauth-provider.ts` - NEW: OAuth provider abstraction

## Implementation Steps
1. Create OAuth provider interface in `src/auth/types.ts`
2. Implement Google OAuth provider
3. Add login endpoint with OAuth flow
4. Add token refresh logic
5. Update frontend to use new auth flow

## Success Criteria
- [ ] Users can log in with Google OAuth
- [ ] Tokens refresh automatically
- [ ] All existing tests pass
- [ ] New auth flow has 90%+ test coverage

## Risks & Mitigations
- **Risk**: Breaking existing session auth
  - **Mitigation**: Run parallel auth systems during migration
```

Now analyze the task and create your implementation plan."""
        )

    def get_implementer_prompt(self, plan: ImplementationPlan) -> str:
        """
        Generate the implementer's system prompt.

        Args:
            plan: The approved implementation plan

        Returns:
            System prompt for the implementer agent
        """
        return f"""You are an expert software implementer. \
Your role is to execute the approved implementation plan precisely.

## Implementation Plan

{plan.to_markdown()}

## Instructions

1. **Follow** the plan steps in order
2. **Write** clean, tested code
3. **Verify** each success criterion
4. **Report** any necessary deviations

## Deviation Protocol

If you discover the plan needs changes:
1. STOP implementation
2. Explain what was planned vs. what's needed
3. Propose the deviation
4. Wait for approval before continuing

## Constraints

- Follow the plan unless deviation is necessary
- Run tests after each significant change
- Don't add features beyond the plan scope
- Report completion of each step

Begin implementing the plan."""

    def validate_plan(self, plan: ImplementationPlan) -> list[str]:
        """
        Validate an implementation plan.

        Args:
            plan: The plan to validate

        Returns:
            List of validation issues (empty if valid)
        """
        issues = []

        if not plan.summary:
            issues.append("Missing summary")

        if not plan.affected_files:
            issues.append("No affected files identified")

        if not plan.implementation_steps:
            issues.append("No implementation steps defined")
        elif len(plan.implementation_steps) < 2:
            issues.append("Too few implementation steps (minimum 2)")

        if not plan.success_criteria:
            issues.append("No success criteria defined")
        elif len(plan.success_criteria) < 2:
            issues.append("Too few success criteria (minimum 2)")

        # Check for vague language
        vague_terms = ["maybe", "possibly", "somehow", "etc", "and so on"]
        for step in plan.implementation_steps:
            for term in vague_terms:
                if term in step.lower():
                    issues.append(f"Vague language in step: '{term}'")
                    break

        return issues


def main() -> None:
    """CLI interface for architect mode."""
    import argparse

    parser = argparse.ArgumentParser(description="Architect Mode Router")
    parser.add_argument("--check", action="store_true", help="Check if architect mode is enabled")
    parser.add_argument(
        "--should-activate", type=str, help="Check if task should trigger architect mode"
    )
    parser.add_argument("--files", type=int, default=0, help="Estimated file changes")

    args = parser.parse_args()

    mode = ArchitectMode()

    if args.check:
        print(f"Architect mode enabled: {mode.is_enabled}")
        print(f"Architect model: {mode.architect_model}")
        print(f"Implementer model: {mode.implementer_model}")

    if args.should_activate:
        should = mode.should_activate(args.should_activate, args.files)
        print(f"Should activate architect mode: {should}")


if __name__ == "__main__":
    main()
