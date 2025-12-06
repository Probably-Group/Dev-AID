---
name: dev-aid-models-update
description: Auto-discover and update to latest AI model versions
category: maintenance
author: Dev-AID
version: 1.0.0
---

# Dev-AID Model Auto-Discovery

Automatically discovers the latest AI model versions from provider APIs and updates your configuration.

## Purpose

Keeps your Dev-AID installation using the newest, most capable models without manual configuration drift.

## What This Does

1. **Queries Provider APIs**: Checks Anthropic, Google, and OpenAI for available models
2. **Version Parsing**: Identifies the latest version of each model tier (Opus, Sonnet, Haiku, Pro, Flash, GPT-4)
3. **Smart Updates**: Updates `.dev-aid/config/models.json` with newest model IDs
4. **Summary Report**: Shows what changed and why

## Usage

```bash
# Run model discovery and update
cd .dev-aid/orchestration
python3 models-updater.py

# Dry run (show changes without saving)
python3 models-updater.py --dry-run
```

## Example Output

```
🔍 Discovering models from AI providers...

Querying Anthropic API...
Querying Google API...
Querying OpenAI API...

✓ Discovered 12 models

Latest models by tier:
  • claude:opus: claude-opus-4-5-20251101 (v4.5)
  • claude:sonnet: claude-sonnet-4-5-20250929 (v4.5)
  • gemini:flash: gemini-2.0-flash (v2.0)
  • gemini:pro: gemini-2.0-pro (v2.0)
  • openai:gpt-4: gpt-4o (v4.0)

Proposed changes (2):
  • claude/opus: claude-opus-4-0-20240229 → claude-opus-4-5-20251101
  • gemini/pro: gemini-1.5-pro → gemini-2.0-pro

✅ Model configuration updated successfully!
