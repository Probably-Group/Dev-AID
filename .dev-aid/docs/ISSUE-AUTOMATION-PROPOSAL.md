# Issue & Conflict Automation Proposal

## Overview
Enhance Dev-AID to automatically handle GitHub issues and resolve merge conflicts using the configured LLM for each repository.

## Implementation Phases

### Phase 1: CLI Commands (Week 1-2)

#### New Commands

**1. `dev-aid-resolve-issue`**
```bash
dev-aid-resolve-issue --issue <number> [--mode solo|ensemble|challenger] [--dry-run]
```

**Workflow:**
1. Fetch issue details from GitHub API
2. Analyze issue type (bug, feature, refactor)
3. Create feature branch
4. Gather relevant codebase context
5. Generate fix using configured LLM
6. Run tests and linting
7. Create PR with detailed explanation
8. Link PR to original issue

**Safety Guardrails:**
- Dry-run mode shows proposed changes without committing
- Requires confirmation for commits
- Auto-labels PR as "ai-generated"
- Runs all CI checks before marking ready for review

**2. `dev-aid-fix-conflicts`**
```bash
dev-aid-fix-conflicts --pr <number> [--strategy ours|theirs|smart]
```

**Workflow:**
1. Fetch PR and identify conflicted files
2. Gather context about both branches
3. Analyze conflict reasons
4. Propose resolution strategy
5. Apply resolution
6. Run tests to verify
7. Push resolution and add comment explaining changes

**Safety Guardrails:**
- Shows diff of proposed resolution
- Requires approval before pushing
- Falls back to manual resolution if confidence is low
- Adds detailed commit message explaining resolution

#### Configuration

Add to `.dev-aid/config/settings.json`:
```json
{
  "automation": {
    "issue_handling": {
      "enabled": true,
      "auto_create_pr": false,
      "require_approval": true,
      "allowed_labels": ["good-first-issue", "bug", "enhancement"],
      "excluded_labels": ["security", "breaking-change"],
      "default_mode": "ensemble"
    },
    "conflict_resolution": {
      "enabled": true,
      "strategy": "smart",
      "require_tests_pass": true,
      "max_conflicts": 5
    }
  }
}
```

### Phase 2: Git Hooks (Week 3)

#### Enhanced Hooks

**1. `post-merge` Hook**
```bash
#!/bin/bash
# .dev-aid/automation/git-hooks/post-merge

# Check for merge conflicts
if git ls-files -u | grep -q .; then
    echo "🔍 Merge conflicts detected!"

    if [ "$DEV_AID_AUTO_RESOLVE" = "true" ]; then
        echo "🤖 Attempting automatic resolution..."
        dev-aid fix-conflicts --auto
    else
        echo "💡 Tip: Run 'dev-aid fix-conflicts' to resolve automatically"
    fi
fi
```

**2. Enhanced `pre-commit` Hook**
```bash
# Add to existing pre-commit
if [ "$DEV_AID_AUTO_FIX" = "true" ]; then
    # Auto-fix linting issues
    dev-aid auto-fix --staged
fi
```

### Phase 3: GitHub Actions (Week 4-5)

#### New Workflows

**1. Auto-Triage Issues**
```yaml
# .github/workflows/auto-triage.yml
name: Auto-Triage Issues

on:
  issues:
    types: [opened]

jobs:
  triage:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Analyze Issue
        run: |
          dev-aid analyze-issue \
            --issue ${{ github.event.issue.number }} \
            --add-labels \
            --estimate-complexity

      - name: Add Context
        run: |
          dev-aid add-issue-context \
            --issue ${{ github.event.issue.number }} \
            --find-related-code \
            --suggest-assignee
```

**2. Auto-Resolve Conflicts**
```yaml
# .github/workflows/auto-resolve-conflicts.yml
name: Auto-Resolve PR Conflicts

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  check-conflicts:
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write

    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Check for Conflicts
        id: conflicts
        run: |
          git fetch origin ${{ github.base_ref }}
          if git merge-tree $(git merge-base HEAD origin/${{ github.base_ref }}) HEAD origin/${{ github.base_ref }} | grep -q '<<<<<<<'; then
            echo "has_conflicts=true" >> $GITHUB_OUTPUT
          fi

      - name: Attempt Auto-Resolution
        if: steps.conflicts.outputs.has_conflicts == 'true'
        run: |
          dev-aid fix-conflicts \
            --pr ${{ github.event.pull_request.number }} \
            --auto-push \
            --add-comment
```

**3. Simple Issue Auto-Fixer**
```yaml
# .github/workflows/auto-fix-issues.yml
name: Auto-Fix Simple Issues

on:
  issues:
    types: [labeled]

jobs:
  auto-fix:
    if: contains(github.event.label.name, 'auto-fixable')
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Dev-AID
        run: |
          pip install -r .dev-aid/orchestration/requirements.txt

      - name: Attempt Fix
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          dev-aid resolve-issue \
            --issue ${{ github.event.issue.number }} \
            --mode solo \
            --create-pr \
            --mark-draft

      - name: Add Comment
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '🤖 Attempted auto-fix but encountered issues. Manual intervention needed.'
            })
```

## Security & Safety Considerations

### Guardrails

1. **Issue Type Filtering**
   - Only auto-handle specific labels (e.g., "good-first-issue", "bug")
   - Never auto-handle "security" or "breaking-change" issues

2. **Review Requirements**
   - All auto-generated PRs marked as draft by default
   - Require approval from maintainers
   - Add "ai-generated" label for transparency

3. **Testing Requirements**
   - Must pass all CI checks
   - Run additional safety tests
   - Rollback if tests fail

4. **Rate Limiting**
   - Max 5 auto-fixes per day
   - Max 3 conflict resolutions per PR
   - Configurable per repository

### Audit Trail

- Log all LLM interactions
- Store prompts and responses
- Track success/failure rates
- Generate weekly reports

## User Experience

### Interactive Mode (Default)

```bash
$ dev-aid resolve-issue --issue 48

🔍 Analyzing issue #48: "Security: Harden Opengrep Rulesets"

📊 Issue Analysis:
   Type: Enhancement
   Complexity: Low
   Estimated time: 15 minutes
   Files to modify: 1-2

🤖 Proposed Solution:
   - Update .github/workflows/security.yml
   - Replace --config=auto with explicit rulesets
   - Add p/security-audit, p/python, p/bash, p/owasp-top-10, p/secrets

⚡ Quick Actions:
   [1] Create PR automatically
   [2] Show me the changes first (dry-run)
   [3] Open interactive editor
   [4] Cancel

Your choice: █
```

### Automated Mode (CI)

```yaml
# .dev-aid/config/automation.yml
auto_handle:
  issues:
    - label: "good-first-issue"
      mode: "solo"
      create_pr: true

    - label: "bug"
      mode: "ensemble"
      require_approval: true

  conflicts:
    auto_resolve: true
    max_files: 5
    require_tests: true
```

## Rollout Strategy

### Week 1-2: Core Commands
- Implement CLI commands
- Add configuration options
- Create documentation

### Week 3: Git Hooks
- Enhance existing hooks
- Add interactive prompts
- Test with real conflicts

### Week 4-5: GitHub Actions
- Create workflow templates
- Add safety checks
- Beta test with selected repos

### Week 6: Documentation & Training
- Write user guides
- Create video tutorials
- Gather feedback

## Success Metrics

- **Adoption**: % of devs using auto-commands
- **Success Rate**: % of auto-fixes that don't need rework
- **Time Saved**: Average time saved per issue/conflict
- **Quality**: Pass rate of auto-generated PRs in CI
- **Satisfaction**: Developer feedback scores

## Next Steps

1. ✅ Create this proposal document
2. ⏳ Get feedback from team
3. ⏳ Implement Phase 1 CLI commands
4. ⏳ Test with real issues
5. ⏳ Iterate based on feedback
