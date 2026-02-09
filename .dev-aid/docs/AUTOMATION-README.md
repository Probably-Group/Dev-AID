# Dev-AID Automation Features

Comprehensive automation for GitHub issues, merge conflicts, and CI/CD workflows using LLMs.

## Quick Links

- **[Issue Resolution Guide](ISSUE-RESOLVER-GUIDE.md)** - Automatically resolve GitHub issues
- **[Conflict Resolution Guide](CONFLICT-RESOLVER-GUIDE.md)** - Automatically resolve merge conflicts
- **[Implementation Details](ISSUE-AUTOMATION-IMPLEMENTATION.md)** - Technical implementation
- **[Original Proposal](ISSUE-AUTOMATION-PROPOSAL.md)** - Feature design

## Overview

Dev-AID provides intelligent automation for common development tasks:

### 🎯 Issue Resolution
Automatically analyze and propose solutions for GitHub issues using LLMs.

### 🔧 Conflict Resolution
Intelligently resolve merge conflicts by understanding both sides of the conflict.

### 🏷️ Auto-Triage
Automatically label and categorize new issues based on their content.

### 🤖 GitHub Actions
Integrated workflows for automated triage, conflict detection, and issue fixing.

### 🪝 Git Hooks
Local hooks that enhance your development workflow with automatic conflict detection.

## Quick Start

### 1. Install Git Hooks

```bash
.dev-aid/automation/git-hooks/install.sh
```

### 2. Resolve an Issue

```bash
# Analyze and propose solution
dev-aid-resolve-issue --issue 123

# Preview without changes
dev-aid-resolve-issue --issue 123 --dry-run

# Use ensemble mode for accuracy
dev-aid-resolve-issue --issue 123 --mode ensemble
```

### 3. Fix Merge Conflicts

```bash
# Resolve conflicts in current branch
dev-aid-fix-conflicts

# Resolve conflicts in a PR
dev-aid-fix-conflicts --pr 67

# Preview resolution
dev-aid-fix-conflicts --dry-run
```

### 4. Configure Automation

Edit `.dev-aid/config/automation.yml`:

```yaml
issue_automation:
  enabled: true
  auto_fix:
    enabled: false  # Enable with caution
    default_mode: ensemble

conflict_resolution:
  auto_resolve: false  # Enable for git hooks auto-resolve
  strategy: smart
  default_mode: ensemble
```

## Features by Phase

### ✅ Phase 1: Issue Analysis (Completed)

**Command:** `dev-aid-resolve-issue`

**Features:**
- Fetch issue details from GitHub
- Analyze issue complexity
- Generate solution proposals
- Safety guardrails (blocks security/critical issues)
- Interactive and dry-run modes
- Multi-mode orchestration (solo/ensemble/challenger)

**Documentation:**
- [Quick Start Guide](ISSUE-RESOLVER-GUIDE.md)

### ✅ Phase 3: Conflict Resolution (Completed)

**Command:** `dev-aid-fix-conflicts`

**Features:**
- Detect conflicts in current branch or PR
- Parse conflict markers
- Multiple resolution strategies (smart/ours/theirs)
- Ensemble mode for accuracy
- Git hooks integration
- Interactive and dry-run modes

**Documentation:**
- [Quick Start Guide](CONFLICT-RESOLVER-GUIDE.md)

**Git Hooks:**
- `post-merge`: Detects conflicts after merge
- Optional auto-resolution with `DEV_AID_AUTO_RESOLVE=true`

### ✅ Phase 4: GitHub Actions (Completed)

**Workflows:**

1. **Auto-Triage Issues** (`.github/workflows/auto-triage-issues.yml`)
   - Triggers on new/edited issues
   - Analyzes content and suggests labels
   - Estimates complexity
   - Identifies auto-fixable issues

2. **Auto-Resolve Conflicts** (`.github/workflows/auto-resolve-conflicts.yml`)
   - Triggers on PR open/update
   - Detects merge conflicts
   - Labels PRs with conflicts
   - Optional auto-resolution with `DEV_AID_AUTO_RESOLVE_CONFLICTS=true`

3. **Auto-Fix Issues** (`.github/workflows/auto-fix-issues.yml`)
   - Triggers when specific labels are added
   - Generates solution proposals
   - Creates draft PRs (when enabled)
   - Safety checks for sensitive issues

**Enable in your repo:**
```bash
# Workflows are ready to use!
# Just set the required secrets:
gh secret set ANTHROPIC_API_KEY
gh secret set OPENAI_API_KEY
gh secret set GOOGLE_API_KEY

# Optional: Enable auto-resolution
gh variable set DEV_AID_AUTO_RESOLVE_CONFLICTS --body "true"
```

### 🔜 Phase 2: Auto-Implementation (Future)

**Planned Features:**
- Automatic branch creation
- Automatic file editing based on LLM output
- Automatic PR creation
- Test execution and validation

**Status:** Phase 1 provides solution proposals that can be implemented manually.

## Architecture

```
Dev-AID Automation
├── CLI Commands
│   ├── dev-aid-resolve-issue    # Issue resolution
│   └── dev-aid-fix-conflicts    # Conflict resolution
│
├── Git Hooks
│   ├── post-merge               # Conflict detection
│   └── install.sh         # Installation script
│
├── GitHub Actions
│   ├── auto-triage-issues.yml   # Issue triage
│   ├── auto-resolve-conflicts.yml # PR conflict detection
│   └── auto-fix-issues.yml      # Automated fixing
│
├── Configuration
│   └── automation.yml           # Centralized config
│
└── Documentation
    ├── ISSUE-RESOLVER-GUIDE.md
    ├── CONFLICT-RESOLVER-GUIDE.md
    ├── AUTOMATION-README.md (this file)
    └── ISSUE-AUTOMATION-IMPLEMENTATION.md
```

## Configuration

### Central Configuration

All automation features are configured in `.dev-aid/config/automation.yml`.

**Key sections:**
- `issue_automation`: Issue resolution settings
- `conflict_resolution`: Conflict resolution settings
- `orchestration`: LLM orchestration modes
- `github_actions`: Workflow settings
- `git_hooks`: Local hook settings
- `safety`: Safety and rate limiting

### Environment Variables

**LLM API Keys:**
```bash
export ANTHROPIC_API_KEY="sk-..."
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="..."
```

**Feature Toggles:**
```bash
# Enable auto-resolution in git hooks
export DEV_AID_AUTO_RESOLVE=true

# GitHub Actions auto-resolution (set as repo variable)
gh variable set DEV_AID_AUTO_RESOLVE_CONFLICTS --body "true"
```

### Repository Secrets (GitHub Actions)

Set in GitHub repository settings:
- `ANTHROPIC_API_KEY`: For Claude
- `OPENAI_API_KEY`: For GPT-4
- `GOOGLE_API_KEY`: For Gemini

## Safety Features

### 1. Blocked Labels
Issues with these labels are never auto-fixed:
- `security`
- `breaking-change`
- `critical`
- `needs-discussion`
- `wontfix`
- `duplicate`

### 2. Confirmation Required
- Interactive mode asks for confirmation
- Use `--auto` flag to skip (use with caution)
- Dry-run mode for previewing

### 3. Rate Limiting
Configurable limits in `automation.yml`:
- Max auto-fixes per day
- Max conflict resolutions per PR
- Request timeouts

### 4. Audit Logging
All LLM interactions are logged:
- `.dev-aid/logs/automation.log`
- `.dev-aid/logs/audit.log`

## Best Practices

### Issue Resolution

1. **Start with dry-run**
   ```bash
   dev-aid-resolve-issue --issue 123 --dry-run
   ```

2. **Use ensemble for important issues**
   ```bash
   dev-aid-resolve-issue --issue 123 --mode ensemble
   ```

3. **Review before implementing**
   - Verify the solution makes sense
   - Check all files are identified
   - Test thoroughly

### Conflict Resolution

1. **Preview first**
   ```bash
   dev-aid-fix-conflicts --dry-run
   ```

2. **Choose appropriate strategy**
   - `smart`: Most cases (default)
   - `ours`: When your changes are correct
   - `theirs`: When accepting upstream

3. **Test after resolution**
   - Run full test suite
   - Verify functionality
   - Check for regressions

### GitHub Actions

1. **Start with triage only**
   - Enable `auto-triage-issues.yml`
   - Observe behavior
   - Gradually enable other workflows

2. **Don't enable auto-fix immediately**
   - Keep `auto_fix.enabled: false`
   - Use manual trigger first
   - Review several proposals

3. **Monitor and adjust**
   - Review workflow runs
   - Adjust configuration
   - Update safety rules

## Troubleshooting

### Commands not found

Add to PATH:
```bash
export PATH="$PATH:$(pwd)/.dev-aid/scripts"
```

Or create symlinks:
```bash
sudo ln -s $(pwd)/.dev-aid/scripts/dev-aid-resolve-issue /usr/local/bin/
sudo ln -s $(pwd)/.dev-aid/scripts/dev-aid-fix-conflicts /usr/local/bin/
```

### GitHub CLI not authenticated

```bash
gh auth login
```

### LLM requests failing

Check API keys:
```bash
echo $ANTHROPIC_API_KEY
echo $OPENAI_API_KEY
echo $GOOGLE_API_KEY
```

### Git hooks not working

Reinstall:
```bash
.dev-aid/automation/git-hooks/install.sh
```

Verify installation:
```bash
ls -la .git/hooks/
```

### Workflows not running

Check:
1. Workflows are enabled in repository settings
2. Required secrets are set
3. Workflow file syntax is correct
4. Trigger conditions are met

## Examples

### Example 1: Fix a Documentation Typo

```bash
# Issue #52: "Fix typo in README.md"
$ dev-aid-resolve-issue --issue 52

🤖 Dev-AID Issue Resolver

📊 Issue Analysis
  Title: Fix typo in README.md
  Complexity: trivial
  Labels: documentation, typo

💡 Proposed Solution:
Change "recieve" to "receive" on line 42 of README.md

🚀 Next Steps:
  1. git checkout -b docs/issue-52-fix-typo
  2. Edit README.md line 42
  3. git commit -am 'docs: fix typo in README'
  4. git push -u origin docs/issue-52-fix-typo
  5. gh pr create --fill
```

### Example 2: Resolve Merge Conflict

```bash
$ git merge feature-branch
CONFLICT (content): Merge conflict in src/app.py

$ dev-aid-fix-conflicts --strategy smart

🔧 Dev-AID Conflict Resolver

📋 Conflicted Files:
  - src/app.py

💡 Proposed Resolution:
[Shows merged code with explanation]

Applied resolution to src/app.py
Next: git add src/app.py && git merge --continue
```

### Example 3: Auto-Triage New Issue

When a new issue is created, GitHub Actions automatically:
1. Analyzes the content
2. Suggests labels (bug, enhancement, etc.)
3. Estimates complexity
4. Adds a comment with analysis
5. Suggests if it's auto-fixable

## Performance

### Orchestration Modes

**Solo** (Fast - ~10s):
- Single LLM
- Good for simple tasks
- Lower cost

**Ensemble** (Balanced - ~30s):
- 3 LLMs vote
- Higher accuracy
- Recommended for most tasks

**Challenger** (Best - ~60s):
- Competing proposals
- Highest quality
- Use for critical tasks

### Cost Optimization

1. Use `solo` mode for triage
2. Use `ensemble` for issue/conflict resolution
3. Use `challenger` only for critical fixes
4. Set rate limits in `automation.yml`

## Roadmap

### ✅ Completed
- [x] Issue analysis and proposals
- [x] Conflict detection and resolution
- [x] Git hooks integration
- [x] GitHub Actions workflows
- [x] Comprehensive documentation
- [x] Safety guardrails
- [x] Configuration system

### 🔜 Upcoming
- [ ] Auto-implementation (Phase 2)
- [ ] Learning from past resolutions
- [ ] VS Code extension
- [ ] Slack/Discord notifications
- [ ] Analytics dashboard
- [ ] Custom resolution strategies

### 💡 Future Ideas
- AI-powered code review
- Automatic test generation
- Security vulnerability auto-patching
- Performance optimization suggestions

## Contributing

Contributions welcome! Please:

1. Read the implementation guide
2. Test locally first
3. Add documentation
4. Include tests
5. Follow conventional commits

## Support

- **Documentation**: `.dev-aid/docs/`
- **Issues**: [GitHub Issues](https://github.com/Probably-Group/Dev-AID/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Probably-Group/Dev-AID/discussions)

## License

Part of Dev-AID project. See main repository for license.
