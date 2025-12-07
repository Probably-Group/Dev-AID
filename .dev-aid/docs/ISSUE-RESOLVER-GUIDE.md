# dev-aid-resolve-issue - Quick Start Guide

## Overview

`dev-aid-resolve-issue` automatically analyzes and proposes solutions for GitHub issues using your configured LLM.

## Basic Usage

```bash
# Analyze an issue and get proposed solution
dev-aid-resolve-issue --issue 48

# Preview without making changes (dry-run)
dev-aid-resolve-issue --issue 48 --dry-run

# Use ensemble mode for higher accuracy
dev-aid-resolve-issue --issue 48 --mode ensemble
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

3. **Run from repository root**
   ```bash
   cd /path/to/your/repo
   dev-aid-resolve-issue --issue 123
   ```

## Safety Features

### Automatic Safety Checks

The script automatically blocks auto-resolution for issues with these labels:
- `security` - Security-sensitive changes
- `breaking-change` - API/behavior changes
- `critical` - High-impact issues
- `needs-discussion` - Requires team discussion
- `wontfix` / `duplicate` - Not actionable

**Example:**
```bash
$ dev-aid-resolve-issue --issue 48

❌ Cannot auto-resolve this issue: Issue has blocked labels: security
ℹ️  Use --skip-safety-check to override (not recommended)
```

### Override Safety (Use with Caution)

```bash
# Only use when you're sure it's safe
dev-aid-resolve-issue --issue 48 --skip-safety-check
```

## Command Options

### Required
- `--issue NUMBER` - GitHub issue number to resolve

### Optional
- `--mode {solo|ensemble|challenger}` - Orchestration mode (default: solo)
  - `solo` - Single LLM, fastest
  - `ensemble` - Multiple LLMs vote, more accurate
  - `challenger` - Competing proposals, best for complex issues

- `--dry-run` - Preview solution without making changes
- `--auto` - Skip confirmation prompts (use in CI)
- `--verbose` - Show detailed LLM interaction
- `--skip-safety-check` - Bypass safety checks (not recommended)

## Example Workflows

### 1. Interactive Analysis (Recommended)

```bash
# Step 1: Analyze the issue
dev-aid-resolve-issue --issue 52

# Output:
# 📊 Issue Analysis
# Title: Fix typo in README.md
# Complexity: trivial
# Labels: documentation, good-first-issue
#
# ❓ Proceed with automated resolution? [Y/n]:

# Step 2: Review proposed solution
# 💡 Proposed Solution
# [Detailed solution provided by LLM]

# Step 3: Implement manually
# 🚀 Next Steps
# 1. Create branch: git checkout -b docs/issue-52-fix-typo
# 2. Make changes...
```

### 2. Quick Preview (Dry-Run)

```bash
# Get solution without any prompts
dev-aid-resolve-issue --issue 52 --dry-run

# Great for:
# - Checking if issue is auto-fixable
# - Getting implementation guidance
# - Learning approach before coding
```

### 3. Batch Analysis

```bash
# Analyze multiple issues
for issue in 45 46 47 48; do
    echo "=== Issue #$issue ==="
    dev-aid-resolve-issue --issue $issue --dry-run
    echo
done
```

### 4. High-Accuracy Mode

```bash
# Use ensemble mode for important fixes
dev-aid-resolve-issue --issue 99 --mode ensemble --verbose

# Best for:
# - Bug fixes
# - Refactoring tasks
# - Important enhancements
```

## Output Format

The script provides:

1. **Issue Analysis**
   - Title and metadata
   - Estimated complexity
   - Safety check results

2. **Proposed Solution**
   - Problem analysis
   - Files to modify
   - Exact code changes
   - Implementation explanation
   - Testing recommendations

3. **Next Steps**
   - Suggested branch name
   - Git commands to run
   - PR creation guidance

## Integration with CI/CD

### GitHub Actions Example

```yaml
# .github/workflows/auto-analyze-issues.yml
name: Auto-Analyze New Issues

on:
  issues:
    types: [opened, labeled]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Dependencies
        run: pip install -r .dev-aid/orchestration/requirements.txt

      - name: Analyze Issue
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          ANALYSIS=$(.dev-aid/scripts/dev-aid-resolve-issue \
            --issue ${{ github.event.issue.number }} \
            --dry-run \
            --mode solo)

          # Add analysis as comment
          gh issue comment ${{ github.event.issue.number }} \
            --body "🤖 **Auto-Analysis**\n\n$ANALYSIS"
```

## Troubleshooting

### "gh: command not found"

Install GitHub CLI:
```bash
# macOS
brew install gh

# Linux
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

Then authenticate:
```bash
gh auth login
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

### "Issue has blocked labels"

This is a safety feature. Review the issue manually to determine if auto-resolution is appropriate.

Only use `--skip-safety-check` if you're certain the issue is safe to auto-resolve.

### No LLM Response / API Errors

Check your API keys:
```bash
# For Anthropic (Claude)
echo $ANTHROPIC_API_KEY

# For OpenAI
echo $OPENAI_API_KEY

# For Google (Gemini)
echo $GOOGLE_API_KEY
```

Set in environment:
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

Or configure in `.dev-aid/config/settings.json`

## Best Practices

1. **Start with Dry-Run**
   - Always preview solutions first
   - Verify the approach makes sense
   - Check if all necessary files are identified

2. **Use Ensemble for Important Issues**
   - Bug fixes: Use `--mode ensemble`
   - Simple typos: `--mode solo` is fine
   - Complex refactoring: Consider `--mode challenger`

3. **Review Before Implementing**
   - The LLM provides guidance, not gospel
   - Verify the solution against requirements
   - Test thoroughly before committing

4. **Respect Safety Checks**
   - Don't routinely bypass safety checks
   - Security issues need human review
   - Breaking changes require discussion

5. **Iterate if Needed**
   - If solution isn't perfect, run again with more context
   - Use `--verbose` to understand LLM reasoning
   - Refine the issue description for better results

## What's Next

This is Phase 1 implementation. Coming soon:

- ✅ **Phase 1 (Current)**: Issue analysis and solution proposals
- 🔜 **Phase 2**: Automatic branch creation and PR generation
- 🔜 **Phase 3**: Conflict resolution (`dev-aid-fix-conflicts`)
- 🔜 **Phase 4**: Full CI/CD integration

## Contributing

Found a bug or have suggestions? Open an issue!

## License

Part of Dev-AID project. See main repository for license.
