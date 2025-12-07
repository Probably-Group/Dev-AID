# Issue Automation - Implementation Guide

## Quick Reference

### Commands to Implement
```bash
dev-aid-resolve-issue    # Automatically resolve GitHub issues
dev-aid-fix-conflicts    # Resolve PR merge conflicts
dev-aid-triage-issues    # Auto-triage and label issues
dev-aid-analyze-issue    # Analyze issue complexity and type
dev-aid-auto-fix         # Auto-fix linting/simple issues
```

## Implementation Roadmap

### Phase 1: Core Python CLI (Week 1)

**Skill:** `python` + `api-expert`

**File:** `.dev-aid/scripts/dev-aid-resolve-issue`

```python
#!/usr/bin/env python3
"""
dev-aid-resolve-issue: Automatically resolve GitHub issues

Usage:
    dev-aid-resolve-issue --issue 48 [--mode solo|ensemble|challenger] [--dry-run]

Leverages:
- Dev-AID orchestration for LLM routing
- GitHub API for issue fetching
- Git operations for branching and PRs
"""

import argparse
import sys
from pathlib import Path

# Use Dev-AID orchestration
sys.path.insert(0, str(Path(__file__).parent.parent / "orchestration"))
from router.executor import execute_request
from router.config_loader import ConfigLoader

def main():
    parser = argparse.ArgumentParser(
        description="Automatically resolve a GitHub issue using LLM"
    )
    parser.add_argument("--issue", type=int, required=True, help="Issue number")
    parser.add_argument("--mode", choices=["solo", "ensemble", "challenger"],
                       default="solo", help="Orchestration mode")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show proposed changes without committing")
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    # Step 1: Fetch issue from GitHub
    issue_data = fetch_issue(args.issue)

    # Step 2: Build context-rich prompt
    prompt = build_issue_prompt(issue_data)

    # Step 3: Execute via Dev-AID orchestration
    result = execute_request(
        request=prompt,
        mode=args.mode,
        verbose=args.verbose
    )

    # Step 4: Create PR if not dry-run
    if not args.dry_run:
        create_pr(issue_data, result)
    else:
        print(f"\n🔍 Dry-run mode - Proposed solution:\n{result}")

if __name__ == "__main__":
    main()
```

**Implementation Steps:**
1. ✅ Use existing `router/executor.py` for LLM orchestration
2. ✅ Add GitHub API client using `gh` CLI
3. ✅ Implement context builder from issue description
4. ✅ Add safety validations (use `router/validators.py`)
5. ✅ Create PR with proper linking

### Phase 2: Conflict Resolution (Week 2)

**Skill:** `bash-expert` + `python`

**File:** `.dev-aid/scripts/dev-aid-fix-conflicts`

```python
#!/usr/bin/env python3
"""
dev-aid-fix-conflicts: Resolve merge conflicts in PRs

Usage:
    dev-aid-fix-conflicts --pr 67 [--strategy smart|ours|theirs]

Strategy:
- smart: LLM analyzes both sides and creates optimal merge
- ours: Prefer current branch changes
- theirs: Prefer incoming branch changes
"""

import subprocess
import sys
from pathlib import Path

def detect_conflicts():
    """Use git to detect conflicted files"""
    result = subprocess.run(
        ["git", "ls-files", "-u"],
        capture_output=True,
        text=True
    )
    return result.stdout.strip().split('\n') if result.stdout else []

def get_conflict_context(file_path):
    """Extract conflict markers and surrounding context"""
    with open(file_path) as f:
        content = f.read()

    # Parse conflict markers
    conflicts = []
    in_conflict = False
    current_conflict = []

    for line in content.split('\n'):
        if line.startswith('<<<<<<<'):
            in_conflict = True
            current_conflict = [line]
        elif line.startswith('=======') and in_conflict:
            current_conflict.append(line)
        elif line.startswith('>>>>>>>') and in_conflict:
            current_conflict.append(line)
            conflicts.append('\n'.join(current_conflict))
            current_conflict = []
            in_conflict = False
        elif in_conflict:
            current_conflict.append(line)

    return conflicts

def resolve_with_llm(conflicts, strategy="smart"):
    """Use Dev-AID orchestration to resolve conflicts"""
    prompt = f"""
    Resolve the following merge conflicts using '{strategy}' strategy:

    {conflicts}

    Provide clean, merged code without conflict markers.
    Explain your resolution decisions.
    """

    # Use Dev-AID router
    from router.executor import execute_request

    return execute_request(
        request=prompt,
        mode="ensemble",  # Use ensemble for higher accuracy
        verbose=True
    )

def main():
    # Implementation here
    pass

if __name__ == "__main__":
    main()
```

### Phase 3: Git Hooks Integration (Week 2)

**Skill:** `bash-expert`

**File:** `.dev-aid/automation/git-hooks/post-merge`

```bash
#!/bin/bash
# Dev-AID post-merge hook
# Auto-detect and optionally resolve merge conflicts

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check for conflicts
if git ls-files -u | grep -q .; then
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}🔥 Merge conflicts detected!${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo

    # Show conflicted files
    echo -e "${YELLOW}Conflicted files:${NC}"
    git ls-files -u | cut -f2 | sort -u | while read -r file; do
        echo "  - $file"
    done
    echo

    # Check if auto-resolution is enabled
    if [ "${DEV_AID_AUTO_RESOLVE:-false}" = "true" ]; then
        echo -e "${BLUE}🤖 Auto-resolution enabled${NC}"
        dev-aid-fix-conflicts --auto
    else
        echo -e "${GREEN}💡 Tip: Run 'dev-aid-fix-conflicts' to resolve automatically${NC}"
        echo -e "${GREEN}   Or set DEV_AID_AUTO_RESOLVE=true for automatic resolution${NC}"
    fi

    exit 1
fi

exit 0
```

### Phase 4: GitHub Actions Workflows (Week 3)

**Skill:** `cicd-expert` + `devsecops-expert`

**File:** `.github/workflows/auto-triage-issues.yml`

```yaml
name: Auto-Triage Issues

on:
  issues:
    types: [opened, edited]
  workflow_dispatch:

permissions:
  issues: write
  contents: read

jobs:
  triage:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Dev-AID
        run: |
          pip install -r .dev-aid/orchestration/requirements.txt

      - name: Analyze Issue
        id: analyze
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          # Use dev-aid-analyze-issue to classify
          RESULT=$(dev-aid-analyze-issue --issue ${{ github.event.issue.number }} --json)

          # Extract labels and complexity
          LABELS=$(echo "$RESULT" | jq -r '.labels | join(",")')
          COMPLEXITY=$(echo "$RESULT" | jq -r '.complexity')

          echo "labels=$LABELS" >> $GITHUB_OUTPUT
          echo "complexity=$COMPLEXITY" >> $GITHUB_OUTPUT

      - name: Apply Labels
        uses: actions/github-script@v7
        with:
          script: |
            const labels = '${{ steps.analyze.outputs.labels }}'.split(',');
            await github.rest.issues.addLabels({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              labels: labels
            });

      - name: Add Complexity Comment
        uses: actions/github-script@v7
        with:
          script: |
            const complexity = '${{ steps.analyze.outputs.complexity }}';
            const body = `🤖 **Auto-Triage Analysis**

            **Estimated Complexity:** ${complexity}

            This issue has been automatically analyzed and labeled by Dev-AID.
            `;

            await github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });

      - name: Check if Auto-Fixable
        id: auto_fixable
        if: contains(steps.analyze.outputs.labels, 'good-first-issue')
        run: |
          echo "Can attempt auto-fix for good-first-issue"
          echo "should_auto_fix=true" >> $GITHUB_OUTPUT

  auto_fix:
    needs: triage
    if: needs.triage.outputs.should_auto_fix == 'true'
    runs-on: ubuntu-latest

    steps:
      - name: Attempt Auto-Fix
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          dev-aid-resolve-issue \
            --issue ${{ github.event.issue.number }} \
            --mode ensemble \
            --create-draft-pr
```

## Security & Safety Implementation

**Skill:** `devsecops-expert` + `appsec-expert`

### Input Validation

Use existing `router/validators.py`:

```python
from router.validators import SecureInput, SafePath
from pydantic import Field, field_validator

class IssueRequest(SecureInput):
    """Validated issue resolution request"""

    issue_number: int = Field(ge=1, le=999999)
    mode: Literal["solo", "ensemble", "challenger"] = "solo"
    dry_run: bool = False

    @field_validator("issue_number")
    @classmethod
    def validate_issue_exists(cls, v: int) -> int:
        """Verify issue exists in GitHub"""
        # Use gh CLI to verify
        result = subprocess.run(
            ["gh", "issue", "view", str(v)],
            capture_output=True
        )
        if result.returncode != 0:
            raise ValueError(f"Issue #{v} not found")
        return v
```

### Safety Guardrails

```python
class SafetyChecks:
    """Safety checks before auto-fixing"""

    BLOCKED_LABELS = ["security", "breaking-change", "critical"]
    ALLOWED_FILE_PATTERNS = [
        "*.md",           # Documentation
        "*.yml",          # Config files
        "tests/*.py",     # Test files
        ".github/**/*.yml" # Workflow files
    ]
    MAX_FILES_CHANGED = 5

    @staticmethod
    def is_safe_to_auto_fix(issue_data: dict) -> tuple[bool, str]:
        """Check if issue is safe for auto-fixing"""

        # Check labels
        labels = [l["name"] for l in issue_data.get("labels", [])]
        if any(blocked in labels for blocked in SafetyChecks.BLOCKED_LABELS):
            return False, "Issue has blocked labels"

        # Check complexity
        if issue_data.get("estimated_complexity", "low") != "low":
            return False, "Issue complexity too high for auto-fix"

        return True, "Safe to proceed"
```

## Testing Strategy

**File:** `.dev-aid/orchestration/tests/test_issue_automation.py`

```python
import pytest
from unittest.mock import patch, Mock

class TestIssueResolution:
    """Test automated issue resolution"""

    @pytest.fixture
    def mock_issue(self):
        return {
            "number": 48,
            "title": "Security: Harden Opengrep Rulesets",
            "body": "Replace --config=auto with explicit rulesets",
            "labels": [{"name": "enhancement"}, {"name": "security"}]
        }

    def test_fetch_issue(self, mock_issue):
        """Test GitHub issue fetching"""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                stdout=json.dumps(mock_issue),
                returncode=0
            )

            result = fetch_issue(48)
            assert result["number"] == 48

    def test_safety_check_blocks_security_issues(self, mock_issue):
        """Test that security issues are not auto-fixed"""
        is_safe, reason = SafetyChecks.is_safe_to_auto_fix(mock_issue)
        assert not is_safe
        assert "blocked labels" in reason.lower()

    @pytest.mark.integration
    def test_full_resolution_dry_run(self, mock_issue):
        """Test full issue resolution in dry-run mode"""
        # This would test the entire flow
        pass
```

## Configuration

**File:** `.dev-aid/config/automation.yml`

```yaml
# Issue Automation Configuration
issue_automation:
  enabled: true

  # Auto-fix settings
  auto_fix:
    enabled: false  # Disabled by default for safety
    allowed_labels:
      - "good-first-issue"
      - "documentation"
      - "typo"
    blocked_labels:
      - "security"
      - "breaking-change"
      - "critical"
    max_files: 5
    require_tests: true
    create_draft_pr: true

  # Triage settings
  triage:
    enabled: true
    auto_label: true
    complexity_estimation: true

  # Conflict resolution
  conflicts:
    auto_resolve: false
    strategy: "smart"  # smart|ours|theirs
    max_conflicts: 3
    require_tests_pass: true

# Orchestration defaults
orchestration:
  default_mode: "solo"
  issue_resolution_mode: "ensemble"  # Use ensemble for higher accuracy
  conflict_resolution_mode: "ensemble"
```

## Next Steps

### Immediate (This Week)
1. [ ] Implement `dev-aid-resolve-issue` Python script
2. [ ] Add GitHub API integration
3. [ ] Create safety validation layer
4. [ ] Write unit tests

### Short-term (Next 2 Weeks)
1. [ ] Implement `dev-aid-fix-conflicts`
2. [ ] Add git hooks integration
3. [ ] Create configuration system
4. [ ] Add integration tests

### Long-term (Month 2)
1. [ ] GitHub Actions workflows
2. [ ] Advanced triage logic
3. [ ] Learning from past resolutions
4. [ ] Dashboard for tracking success rates

## Success Criteria

- ✅ Commands follow `dev-aid-*` naming convention
- ✅ Leverage existing Dev-AID orchestration
- ✅ Use appropriate expert skills
- ✅ Comprehensive safety guardrails
- ✅ Full test coverage
- ✅ Clear documentation
- ✅ Configurable per repository
