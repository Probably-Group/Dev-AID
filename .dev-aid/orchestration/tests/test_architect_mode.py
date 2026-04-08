"""Tests for ArchitectMode and ImplementationPlan"""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from router.modes.architect import ArchitectMode, ImplementationPlan, PlanStatus


class TestPlanStatus:
    """Test PlanStatus enum"""

    def test_all_statuses_exist(self):
        assert PlanStatus.DRAFT.value == "draft"
        assert PlanStatus.PENDING_APPROVAL.value == "pending_approval"
        assert PlanStatus.APPROVED.value == "approved"
        assert PlanStatus.REJECTED.value == "rejected"
        assert PlanStatus.IN_PROGRESS.value == "in_progress"
        assert PlanStatus.COMPLETED.value == "completed"
        assert PlanStatus.FAILED.value == "failed"

    def test_from_string(self):
        assert PlanStatus("draft") == PlanStatus.DRAFT
        assert PlanStatus("approved") == PlanStatus.APPROVED


class TestImplementationPlan:
    """Test ImplementationPlan dataclass"""

    @pytest.fixture
    def sample_plan(self):
        return ImplementationPlan(
            summary="Add user authentication",
            affected_files=[
                {"path": "src/auth.py", "action": "new", "description": "Auth module"},
                {"path": "src/main.py", "description": "Add auth middleware"},
            ],
            implementation_steps=[
                "Create auth module",
                "Add middleware",
                "Write tests",
            ],
            success_criteria=["Users can log in", "Tests pass", "90% coverage"],
            risks=[{"risk": "Breaking changes", "mitigation": "Feature flag"}],
            alternatives=["Use OAuth2 instead"],
            testing_strategy="Unit + integration tests",
        )

    def test_create_plan(self, sample_plan):
        assert sample_plan.summary == "Add user authentication"
        assert len(sample_plan.affected_files) == 2
        assert len(sample_plan.implementation_steps) == 3
        assert sample_plan.status == PlanStatus.DRAFT

    def test_to_markdown_full(self, sample_plan):
        md = sample_plan.to_markdown()
        assert "## Summary" in md
        assert "Add user authentication" in md
        assert "## Affected Files" in md
        assert "**NEW**" in md
        assert "## Implementation Steps" in md
        assert "1. Create auth module" in md
        assert "## Success Criteria" in md
        assert "- [ ] Users can log in" in md
        assert "## Risks & Mitigations" in md
        assert "Breaking changes" in md
        assert "## Alternative Approaches" in md
        assert "Use OAuth2 instead" in md
        assert "## Testing Strategy" in md

    def test_to_markdown_minimal(self):
        plan = ImplementationPlan(
            summary="Minimal plan",
            affected_files=[{"path": "file.py", "description": "change"}],
            implementation_steps=["Do thing"],
            success_criteria=["It works"],
        )
        md = plan.to_markdown()
        assert "## Summary" in md
        assert "Risks" not in md
        assert "Alternative" not in md
        assert "Testing Strategy" not in md

    def test_to_markdown_modify_action(self):
        plan = ImplementationPlan(
            summary="Test",
            affected_files=[{"path": "src/app.py", "action": "modify", "description": "Update"}],
            implementation_steps=["Step 1"],
            success_criteria=["Done"],
        )
        md = plan.to_markdown()
        assert "**NEW**" not in md
        assert "`src/app.py` - Update" in md

    def test_from_dict(self):
        data = {
            "summary": "Test plan",
            "affected_files": [{"path": "a.py"}],
            "implementation_steps": ["Step 1", "Step 2"],
            "success_criteria": ["Criterion 1", "Criterion 2"],
            "status": "approved",
        }
        plan = ImplementationPlan.from_dict(data)
        assert plan.summary == "Test plan"
        assert plan.status == PlanStatus.APPROVED
        assert len(plan.implementation_steps) == 2

    def test_from_dict_defaults(self):
        plan = ImplementationPlan.from_dict({})
        assert plan.summary == ""
        assert plan.affected_files == []
        assert plan.status == PlanStatus.DRAFT

    def test_from_dict_with_risks(self):
        data = {
            "summary": "Plan",
            "affected_files": [],
            "implementation_steps": ["A", "B"],
            "success_criteria": ["C", "D"],
            "risks": [{"risk": "Downtime", "mitigation": "Blue-green deploy"}],
            "alternatives": ["Alternative A"],
            "testing_strategy": "E2E tests",
        }
        plan = ImplementationPlan.from_dict(data)
        assert len(plan.risks) == 1
        assert plan.risks[0]["risk"] == "Downtime"
        assert plan.testing_strategy == "E2E tests"


class TestArchitectMode:
    """Test ArchitectMode class"""

    @pytest.fixture
    def config_dir(self, tmp_path):
        dev_aid = tmp_path / ".dev-aid" / "config"
        dev_aid.mkdir(parents=True)
        config = {
            "architect": {
                "enabled": True,
                "architect_model": "claude-opus-4",
                "implementer_model": "claude-sonnet-4",
                "triggers": {
                    "auto_activate": {
                        "enabled": True,
                        "conditions": {
                            "estimated_file_changes_gt": 3,
                            "keywords": ["refactor", "redesign", "migrate"],
                        },
                    }
                },
                "plan_format": {
                    "required_sections": ["## Summary", "## Steps"],
                },
            }
        }
        (dev_aid / "orchestration.json").write_text(json.dumps(config))
        return dev_aid / "orchestration.json"

    def test_init_default_config(self, tmp_path):
        with patch.object(Path, "cwd", return_value=tmp_path):
            mode = ArchitectMode()
        assert mode.is_enabled is False
        assert mode.architect_model == "claude-opus-4.5"
        assert mode.implementer_model == "claude-sonnet-4.5"

    def test_init_with_config(self, config_dir):
        mode = ArchitectMode(config_path=config_dir)
        assert mode.is_enabled is True
        assert mode.architect_model == "claude-opus-4"
        assert mode.implementer_model == "claude-sonnet-4"

    def test_init_nonexistent_config(self, tmp_path):
        mode = ArchitectMode(config_path=tmp_path / "nonexistent.json")
        assert mode.is_enabled is False

    def test_should_activate_disabled(self, tmp_path):
        with patch.object(Path, "cwd", return_value=tmp_path):
            mode = ArchitectMode()
        assert mode.should_activate("refactor the auth system") is False

    def test_should_activate_keyword_match(self, config_dir):
        mode = ArchitectMode(config_path=config_dir)
        assert mode.should_activate("refactor the auth module") is True
        assert mode.should_activate("Please redesign the API") is True

    def test_should_activate_keyword_no_match(self, config_dir):
        mode = ArchitectMode(config_path=config_dir)
        assert mode.should_activate("fix a typo in readme") is False

    def test_should_activate_file_count(self, config_dir):
        mode = ArchitectMode(config_path=config_dir)
        assert mode.should_activate("update config", estimated_files=5) is True

    def test_should_activate_file_count_below_threshold(self, config_dir):
        mode = ArchitectMode(config_path=config_dir)
        assert mode.should_activate("update config", estimated_files=2) is False

    def test_should_activate_no_auto_activate(self, tmp_path):
        dev_aid = tmp_path / ".dev-aid" / "config"
        dev_aid.mkdir(parents=True)
        config = {"architect": {"enabled": True}}
        (dev_aid / "orchestration.json").write_text(json.dumps(config))
        mode = ArchitectMode(config_path=dev_aid / "orchestration.json")
        assert mode.should_activate("refactor everything") is False

    def test_get_architect_prompt(self, config_dir):
        mode = ArchitectMode(config_path=config_dir)
        prompt = mode.get_architect_prompt("Build auth system", "Some context")
        assert "Build auth system" in prompt
        assert "Some context" in prompt
        assert "## Summary" in prompt
        assert "## Steps" in prompt

    def test_get_architect_prompt_no_context(self, config_dir):
        mode = ArchitectMode(config_path=config_dir)
        prompt = mode.get_architect_prompt("Build auth")
        assert "No additional context provided" in prompt

    def test_get_architect_prompt_default_sections(self, tmp_path):
        with patch.object(Path, "cwd", return_value=tmp_path):
            mode = ArchitectMode()
        prompt = mode.get_architect_prompt("task")
        assert "## Summary" in prompt
        assert "## Affected Files" in prompt
        assert "## Implementation Steps" in prompt

    def test_get_implementer_prompt(self, config_dir):
        mode = ArchitectMode(config_path=config_dir)
        plan = ImplementationPlan(
            summary="Build auth",
            affected_files=[{"path": "auth.py", "description": "new"}],
            implementation_steps=["Step 1", "Step 2"],
            success_criteria=["Works", "Tested"],
        )
        prompt = mode.get_implementer_prompt(plan)
        assert "Build auth" in prompt
        assert "Step 1" in prompt
        assert "Deviation Protocol" in prompt

    def test_validate_plan_valid(self, config_dir):
        mode = ArchitectMode(config_path=config_dir)
        plan = ImplementationPlan(
            summary="Good plan",
            affected_files=[{"path": "a.py"}],
            implementation_steps=["Step 1", "Step 2"],
            success_criteria=["Criterion 1", "Criterion 2"],
        )
        issues = mode.validate_plan(plan)
        assert issues == []

    def test_validate_plan_missing_summary(self, config_dir):
        mode = ArchitectMode(config_path=config_dir)
        plan = ImplementationPlan(
            summary="",
            affected_files=[{"path": "a.py"}],
            implementation_steps=["Step 1", "Step 2"],
            success_criteria=["C1", "C2"],
        )
        issues = mode.validate_plan(plan)
        assert "Missing summary" in issues

    def test_validate_plan_no_files(self, config_dir):
        mode = ArchitectMode(config_path=config_dir)
        plan = ImplementationPlan(
            summary="Plan",
            affected_files=[],
            implementation_steps=["Step 1", "Step 2"],
            success_criteria=["C1", "C2"],
        )
        issues = mode.validate_plan(plan)
        assert "No affected files identified" in issues

    def test_validate_plan_too_few_steps(self, config_dir):
        mode = ArchitectMode(config_path=config_dir)
        plan = ImplementationPlan(
            summary="Plan",
            affected_files=[{"path": "a.py"}],
            implementation_steps=["Only one"],
            success_criteria=["C1", "C2"],
        )
        issues = mode.validate_plan(plan)
        assert "Too few implementation steps (minimum 2)" in issues

    def test_validate_plan_no_steps(self, config_dir):
        mode = ArchitectMode(config_path=config_dir)
        plan = ImplementationPlan(
            summary="Plan",
            affected_files=[{"path": "a.py"}],
            implementation_steps=[],
            success_criteria=["C1", "C2"],
        )
        issues = mode.validate_plan(plan)
        assert "No implementation steps defined" in issues

    def test_validate_plan_too_few_criteria(self, config_dir):
        mode = ArchitectMode(config_path=config_dir)
        plan = ImplementationPlan(
            summary="Plan",
            affected_files=[{"path": "a.py"}],
            implementation_steps=["S1", "S2"],
            success_criteria=["Only one"],
        )
        issues = mode.validate_plan(plan)
        assert "Too few success criteria (minimum 2)" in issues

    def test_validate_plan_no_criteria(self, config_dir):
        mode = ArchitectMode(config_path=config_dir)
        plan = ImplementationPlan(
            summary="Plan",
            affected_files=[{"path": "a.py"}],
            implementation_steps=["S1", "S2"],
            success_criteria=[],
        )
        issues = mode.validate_plan(plan)
        assert "No success criteria defined" in issues

    def test_validate_plan_vague_language(self, config_dir):
        mode = ArchitectMode(config_path=config_dir)
        plan = ImplementationPlan(
            summary="Plan",
            affected_files=[{"path": "a.py"}],
            implementation_steps=["Do something maybe", "Step 2"],
            success_criteria=["C1", "C2"],
        )
        issues = mode.validate_plan(plan)
        assert any("Vague language" in i for i in issues)

    def test_validate_plan_multiple_issues(self, config_dir):
        mode = ArchitectMode(config_path=config_dir)
        plan = ImplementationPlan(
            summary="",
            affected_files=[],
            implementation_steps=[],
            success_criteria=[],
        )
        issues = mode.validate_plan(plan)
        assert len(issues) >= 4
