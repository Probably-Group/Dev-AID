# Quick Start Guide

Get Dev-AID running in 5 minutes!

## Prerequisites

- Git
- Bash shell
- **Authentication**: Choose one method per provider:
  - **Session-based** (Recommended): Logged into Claude Code/Gemini CLI (`claude login`, `gcloud auth`)
  - **API keys**: ANTHROPIC_API_KEY, GOOGLE_API_KEY, or OPENAI_API_KEY

## Installation

### 1. Clone Dev-AID

```bash
# Clone into your project
cd your-project/
git clone https://github.com/user/dev-aid .dev-aid-temp
cp -r .dev-aid-temp/.dev-aid .
rm -rf .dev-aid-temp

# Or clone standalone and copy to projects
git clone https://github.com/user/dev-aid
# Use dev-aid/.dev-aid/ in your projects
```

### 2. Run Installer

```bash
./.dev-aid/scripts/install.sh
```

Follow the 6-step wizard:
1. **Context Budget**: Choose "Balanced" (recommended)
2. **Auto-Activation**: Choose "Conservative" (recommended)
3. **Providers**: Select your AI providers
4. **Orchestration**: Choose mode (Solo for single AI, Ensemble for multi-AI)
5. **Model Assignment**: Assign models to tasks (if multi-AI)
6. **Authentication**: Session auth auto-detected, or enter API keys if needed

### 3. Start Developing

```bash
# Start Claude Code (or your AI interface)
claude code

# Dev-AID is now active!
# - Memory bank loaded
# - Skills auto-activate based on files
# - Models route automatically (if Ensemble)
```

## Common Scenarios

### Single AI User (Claude only)

```bash
# Option A: With Claude Pro/Max (no API key needed)
claude login  # One-time setup
# During installation:
- Providers: Enable Claude only
- Orchestration: Choose "Solo" or "None"
- Authentication: Auto-detected from Claude Code session

# Option B: With API key
# During installation:
- Providers: Enable Claude only
- Orchestration: Choose "Solo" or "None"
- API Key: Enter ANTHROPIC_API_KEY

# Result: Simple, single-model setup
```

### Multi-AI Team (Claude + Gemini + OpenAI)

```bash
# Option A: With consumer subscriptions (Claude Pro/Gemini CLI)
claude login          # One-time setup for Claude
gcloud auth application-default login  # One-time setup for Gemini

# During installation:
- Providers: Enable all three
- Orchestration: Choose "Ensemble"
- Model Assignment:
  - Code generation: claude-sonnet-4.5
  - Massive context: gemini-2.0-flash
  - Documentation: gpt-4o
- Authentication: Claude/Gemini auto-detected, enter OPENAI_API_KEY if using GPT

# Option B: With API keys
# During installation:
- API Keys: Enter ANTHROPIC_API_KEY, GOOGLE_API_KEY, OPENAI_API_KEY

# Result: Automatic routing, cost optimization
```

### Change Your Mind Later

```bash
# Reconfigure anytime
./.dev-aid/scripts/reconfigure.sh

# Your memory bank and context are preserved!
```

## 🛠️ For Contributors

**Set up development workflow to prevent CI failures:**

```bash
# One-time setup
./.dev-aid/scripts/setup-git-hooks.sh

# Now all PR checks run automatically on every commit!
# ✓ Formatting ✓ Linting ✓ Tests ✓ Coverage
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for full development guide.

## Verification

Check your setup:

```bash
# View configuration
./.dev-aid/scripts/reconfigure.sh --validate

# Check logs (if using Ensemble/Challenger)
tail -f .dev-aid/logs/context-sharing.log

# View memory bank
cat .dev-aid/memory-bank/activeContext.md
```

## Next Steps

- Read [README.md](README.md) for full features
- Check [.dev-aid/docs/SKILLS-ARCHITECTURE.md](.dev-aid/docs/SKILLS-ARCHITECTURE.md) for architecture
- See [.dev-aid/docs/CONTEXT-SHARING.md](.dev-aid/docs/CONTEXT-SHARING.md) for multi-model details

## Troubleshooting

**Issue**: Installer not found
```bash
# Make sure you're in the right directory
ls -la .dev-aid/scripts/install.sh
chmod +x .dev-aid/scripts/install.sh
```

**Issue**: Authentication not working
```bash
# Check authentication status (for Dev-AID Router)
cd .dev-aid/orchestration
python -m router.cli auth-status

# Option A: Use session auth (recommended)
claude login  # For Claude Pro/Max
gcloud auth application-default login  # For Gemini

# Option B: Check API keys in .env
cat .dev-aid/config/.env
# Or reconfigure
./.dev-aid/scripts/reconfigure.sh
```

**Issue**: Models not routing correctly
```bash
# Check orchestration mode
cat .dev-aid/config/settings.json | grep orchestration_mode
# View logs
tail -f .dev-aid/logs/context-sharing.log
```

Need help? Check the [full documentation](README.md) or open an issue!
