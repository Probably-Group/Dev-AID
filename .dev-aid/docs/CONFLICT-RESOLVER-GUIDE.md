# dev-aid-fix-conflicts - Quick Start Guide

## Overview

`dev-aid-fix-conflicts` automatically analyzes and resolves merge conflicts using your configured LLM.

## Basic Usage

```bash
# Resolve conflicts in current branch
dev-aid-fix-conflicts

# Resolve conflicts in a specific PR
dev-aid-fix-conflicts --pr 67

# Preview resolution without applying
dev-aid-fix-conflicts --dry-run

# Use specific resolution strategy
dev-aid-fix-conflicts --strategy smart
```

## Prerequisites

1. **GitHub CLI installed and authenticated**
   ```bash
   # Install
   brew install gh  # macOS
   # or visit https://cli.github.com/

   # Authenticate
   gh auth login
   ```

2. **Dev-AID orchestration configured**
   - API keys set in environment or config
   - At least one LLM provider configured

3. **Active merge conflict**
   - You must have an ongoing merge/rebase with conflicts
   - Or specify a PR with conflicts

## Resolution Strategies

### Smart (Recommended)
Analyzes both sides and creates the optimal merge:
```bash
dev-aid-fix-conflicts --strategy smart
```
- Understands intent of both changes
- Preserves functionality from both sides
- Best for most conflicts

### Ours
Prefers current branch changes:
```bash
dev-aid-fix-conflicts --strategy ours
```
- Keeps your current changes
- Incorporates non-conflicting parts from incoming
- Good when you know your version is correct

### Theirs
Prefers incoming branch changes:
```bash
dev-aid-fix-conflicts --strategy theirs
```
- Accepts incoming changes
- Incorporates non-conflicting parts from current
- Good for accepting upstream updates

## Example Workflows

### 1. Basic Conflict Resolution

```bash
# During a merge that hits conflicts
$ git merge feature-branch

Auto-merging src/app.py
CONFLICT (content): Merge conflict in src/app.py
Automatic merge failed; fix conflicts and then commit the result.

# Use Dev-AID to resolve
$ dev-aid-fix-conflicts

🔧 Dev-AID Conflict Resolver

ℹ️  Detecting conflicts in current branch...

📋 Conflicted Files:
  - src/app.py

🔍 Analyzing: src/app.py
ℹ️  Found 2 conflict(s)
ℹ️  Resolving conflicts using ensemble mode...

💡 Proposed Resolution:
[Detailed resolution from LLM]

❓ Apply the proposed resolutions? [y/N]: y
```

### 2. PR Conflict Resolution

```bash
# Check a PR for conflicts and resolve
$ dev-aid-fix-conflicts --pr 67

🔧 Dev-AID Conflict Resolver

ℹ️  Checking PR #67 for conflicts...
ℹ️  PR has conflicts

[Resolution process as above]
```

### 3. Preview Mode

```bash
# See what the resolution would look like
$ dev-aid-fix-conflicts --dry-run

[Shows proposed resolutions without applying]

ℹ️  Dry-run mode - no changes applied
ℹ️  Remove --dry-run to apply resolutions
```

## Orchestration Modes

### Solo Mode (Fast)
```bash
dev-aid-fix-conflicts --mode solo
```
- Single LLM
- Fastest resolution
- Good for simple conflicts

### Ensemble Mode (Recommended)
```bash
dev-aid-fix-conflicts --mode ensemble
```
- Multiple LLMs vote
- Higher accuracy
- Default mode for conflicts
- Best for important merges

### Challenger Mode (Best Quality)
```bash
dev-aid-fix-conflicts --mode challenger
```
- Competing proposals
- Highest quality
- Slower
- Use for critical conflicts

## Git Hooks Integration

Dev-AID provides git hooks that automatically detect conflicts.

### Installation

```bash
# Install hooks
.dev-aid/automation/git-hooks/install-hooks.sh
```

### Automatic Detection

After installation, conflicts are automatically detected:

```bash
$ git merge feature-branch

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 Merge conflicts detected!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Conflicted files:
  - src/app.py
  - README.md

💡 Tip: Run 'dev-aid-fix-conflicts' to resolve automatically
   Or set DEV_AID_AUTO_RESOLVE=true for automatic resolution
```

### Enable Auto-Resolution

```bash
# Enable automatic conflict resolution
export DEV_AID_AUTO_RESOLVE=true

# Now merges will auto-resolve conflicts
git merge feature-branch
# Conflicts automatically resolved!
```

## GitHub Actions Integration

Dev-AID includes workflows for automatic conflict detection in PRs.

### Conflict Detection

The `auto-resolve-conflicts.yml` workflow:
- Runs on PR open/update
- Detects merge conflicts
- Adds comment with conflict details
- Labels PR with `conflicts`

### Enable Auto-Resolution in CI

Set repository variable:
```
DEV_AID_AUTO_RESOLVE_CONFLICTS=true
```

This enables automatic resolution in GitHub Actions.

## Configuration

Configure conflict resolution in `.dev-aid/config/automation.yml`:

```yaml
conflict_resolution:
  # Enable automatic conflict resolution
  auto_resolve: false

  # Conflict resolution strategy
  strategy: smart

  # Maximum number of conflicts to auto-resolve
  max_conflicts: 5

  # Require tests to pass after resolution
  require_tests_pass: true

  # Default orchestration mode
  default_mode: ensemble
```

## Output Format

The tool provides:

1. **Conflict Analysis**
   - List of conflicted files
   - Number of conflicts per file
   - Conflict locations

2. **Proposed Resolution**
   - Complete resolved code
   - Explanation of resolution decisions
   - Trade-offs and concerns

3. **Next Steps**
   - How to apply the resolution
   - Commands to continue merge
   - Testing recommendations

## Troubleshooting

### "No conflicts detected"

Make sure you're in an active merge:
```bash
# Check git status
git status

# You should see:
# Unmerged paths:
#   (use "git add <file>..." to mark resolution)
#   both modified:   file.py
```

### "gh: command not found"

Install GitHub CLI:
```bash
# macOS
brew install gh

# Linux
sudo apt install gh
```

### "Could not import Dev-AID orchestration modules"

Activate the virtual environment:
```bash
source .dev-aid/orchestration/venv/bin/activate
```

Or install dependencies:
```bash
pip install -r .dev-aid/orchestration/requirements.txt
```

### Resolution doesn't look correct

Try a different strategy:
```bash
# If smart merge isn't working, try ours or theirs
dev-aid-fix-conflicts --strategy ours

# Or use a different orchestration mode
dev-aid-fix-conflicts --mode challenger
```

### Want to see more details

Use verbose mode:
```bash
dev-aid-fix-conflicts --verbose
```

## Best Practices

1. **Always Review Resolutions**
   - LLM provides guidance, not gospel
   - Verify the resolution makes sense
   - Run tests before committing

2. **Use Dry-Run First**
   - Preview the resolution
   - Understand the approach
   - Verify all conflicts are addressed

3. **Choose the Right Strategy**
   - `smart`: Most conflicts (default)
   - `ours`: When you know your changes are correct
   - `theirs`: When accepting upstream updates

4. **Use Ensemble for Important Merges**
   - Release branches
   - Main/master merges
   - Complex conflicts

5. **Test After Resolution**
   - Always run test suite
   - Verify functionality
   - Check for regressions

## Safety Features

- **No automatic commits**: You review before committing
- **Dry-run mode**: Preview without applying
- **Conflict limits**: Won't auto-resolve too many conflicts
- **Test requirements**: Can require tests to pass
- **Audit logging**: All resolutions are logged

## What's Next

Current capabilities:
- ✅ Detect conflicts in current branch
- ✅ Detect conflicts in PRs
- ✅ Multiple resolution strategies
- ✅ Ensemble mode for accuracy
- ✅ Git hooks integration
- ✅ GitHub Actions workflows

Future enhancements:
- Auto-parse LLM output and apply directly
- Learn from past conflict resolutions
- Suggest strategy based on conflict type
- Integration with VS Code and other IDEs

## Contributing

Found a bug or have suggestions? Open an issue!

## License

Part of Dev-AID project. See main repository for license.
