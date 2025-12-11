---
name: dev-aid-config-core-skills
description: Configure which core skills are auto-loaded at session start
category: setup
version: 1.0.0
---

# Configure Core Skills

Interactive configuration for core skills (real-time automated checking).

## Purpose

Core skills provide automated tool execution on file save:
- **code-reviewer**: Real-time code quality suggestions
- **secret-scanner**: Prevent credential leaks
- **test-runner**: Auto-run relevant tests
- **linter**: Auto-lint code
- **type-checker**: Auto-check types

Each core skill consumes ~250 tokens of standing context.

## Task

1. **Read current configuration:**
   ```bash
   cat .dev-aid/config/core-skills.json
   ```

2. **Show current status:**
   ```
   📊 Current Core Skills Configuration

   ✅ Enabled (500 tokens):
   • code-reviewer (250 tokens) - Real-time code quality
   • secret-scanner (250 tokens) - Prevent credential leaks

   ⏸️  Disabled (0 tokens):
   • test-runner (250 tokens) - Auto-run tests
   • linter (250 tokens) - Auto-lint code
   • type-checker (250 tokens) - Auto-check types

   Profile: minimal (recommended)
   Token usage: 500/1250 (0.25% of 200k budget)
   ```

3. **Ask user which to enable/disable:**
   Use the AskUserQuestion tool with these options:

   **Question 1: Select profile (or custom)**
   - minimal (recommended) - code-reviewer + secret-scanner (500 tokens)
   - ide-user - code-reviewer + secret-scanner (500 tokens)
   - no-ide-setup - all 5 enabled (1,250 tokens)
   - ci-cd - secret-scanner only (250 tokens)
   - custom - choose individual skills

   **Question 2 (if custom): Which skills to enable?**
   (multiSelect: true)
   - code-reviewer (recommended for all)
   - secret-scanner (recommended for all)
   - test-runner (recommended if no IDE test runner)
   - linter (recommended if no IDE linter)
   - type-checker (recommended if no IDE type checker)

4. **Update configuration:**
   ```bash
   # Update .dev-aid/config/core-skills.json with selections
   # Calculate new token budget
   # Set lastUpdated timestamp
   ```

5. **Display summary:**
   ```
   ✅ Core skills configuration updated!

   Enabled skills (3):
   • code-reviewer (250 tokens)
   • secret-scanner (250 tokens)
   • test-runner (250 tokens)

   Total: 750 tokens (0.375% of 200k budget)
   Remaining: 199,250 tokens (99.625%)

   💡 Changes take effect on next session start.
   💡 Reload now: Restart Claude Code session
   💡 Team sharing: Commit .dev-aid/config/core-skills.json
   💡 Personal override: Create .dev-aid/config/core-skills.local.json (gitignored)
   ```

## Profile Descriptions

**minimal** (default):
- Best for: Most developers
- Enabled: code-reviewer, secret-scanner
- Token cost: 500 (0.25%)
- Why: Essential safety nets without overhead

**ide-user**:
- Best for: VS Code/JetBrains users with extensions
- Enabled: code-reviewer, secret-scanner
- Token cost: 500 (0.25%)
- Why: IDE already provides test/lint/type checking

**no-ide-setup**:
- Best for: Vim/Emacs/command-line developers
- Enabled: All 5 core skills
- Token cost: 1,250 (0.625%)
- Why: Dev-AID provides all automated checking

**ci-cd**:
- Best for: GitHub Actions, CI pipelines
- Enabled: secret-scanner only
- Token cost: 250 (0.125%)
- Why: CI already runs tests/lints, only need secret check

## Examples

### Example 1: Developer with VS Code + ESLint extension
User would select: **ide-user** profile
- Enables: code-reviewer, secret-scanner
- Rationale: ESLint extension already provides linting

### Example 2: Vim user, no IDE setup
User would select: **no-ide-setup** profile
- Enables: All 5 core skills
- Rationale: No IDE extensions, need all automated checks

### Example 3: Custom selection
User selects: **custom** → enables code-reviewer, secret-scanner, test-runner
- Enables: code-reviewer, secret-scanner, test-runner (750 tokens)
- Rationale: Has IDE linting/types, but no test runner

## Implementation Notes

- Read from: `.dev-aid/config/core-skills.json`
- Personal overrides: `.dev-aid/config/core-skills.local.json` (if exists)
- Update `enabled` and `disabled` arrays
- Recalculate `tokenUsage.current`
- Set `lastUpdated` to current ISO timestamp
- Preserve comments and structure

## Related Commands

- `/dev-aid-status` - View current configuration
- `/dev-aid-analyze` - Initial project setup (includes core skills config)
