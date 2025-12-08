# Router Installation & Setup Guide

Complete guide to installing and using the Dev-AID Router for multi-AI orchestration.

## 🚀 Quick Start (5 Minutes)

### Step 1: Setup Virtual Environment (Recommended)

**Why virtual environment?**
- ✅ Isolates dependencies from system Python
- ✅ Prevents version conflicts between projects
- ✅ Keeps your system clean
- ✅ Easy to remove (just delete `.venv/` folder)

```bash
cd /path/to/your/project
cd .dev-aid/orchestration

# Automated setup (recommended)
./setup-venv.sh
```

This will:
1. Create isolated Python environment in `.venv/`
2. Install all dependencies
3. Test the installation
4. Show usage instructions

**Alternative: Manual installation (NOT recommended)**
```bash
# Only if you know what you're doing
pip install -r requirements.txt
# Warning: Installs to system Python - may cause conflicts!
```

**Required packages**:
- `anthropic` - Claude API
- `google-genai` - Gemini API (unified SDK)
- `openai` - GPT API
- `python-dotenv` - Environment variables
- `pydantic` - Data validation
- `rich`, `typer` - CLI interface

### Step 2: Configure Authentication

**Dev-AID Router supports two authentication methods:**

#### Option A: Session-Based Authentication (Recommended)

If you have consumer AI subscriptions (Claude Pro/Max, Gemini CLI):

```bash
# For Claude (Pro/Max subscriptions)
claude login  # One-time setup - stores session token in system keychain

# For Gemini (via gcloud)
gcloud auth application-default login  # One-time setup - stores ADC credentials

# Check authentication status
cd .dev-aid/orchestration
python -m router.cli auth-status
```

**Benefits:**
- ✅ No API keys needed for Claude Pro/Max users (API keys not available anyway!)
- ✅ Automatically detected from CLI sessions
- ✅ Stored securely in system keychain
- ✅ Works immediately after login

#### Option B: API Keys (Traditional Method)

If you have API access:

Create or edit `.dev-aid/config/.env`:

```bash
# Navigate to config directory
cd ../../config

# Create .env file
nano .env
```

Add your API keys:

```bash
# Anthropic (Claude) - If you have API access
ANTHROPIC_API_KEY=sk-ant-api03-...

# Google (Gemini) - If not using gcloud ADC
GOOGLE_API_KEY=AIza...

# OpenAI (GPT) - API key required (ChatGPT Plus ≠ API access)
OPENAI_API_KEY=sk-...
```

**Where to get keys:**
- Anthropic: https://console.anthropic.com/ (Note: Claude Pro/Max users don't have API access)
- Google: https://aistudio.google.com/app/apikey
- OpenAI: https://platform.openai.com/api-keys

**Priority**: The router tries session auth first, then falls back to API keys.

### Step 3: Enable Providers

Edit `.dev-aid/config/models.json` - set `"enabled": true` for providers you have keys for:

```json
{
  "claude": {
    "enabled": true,  // ✅ You have Anthropic key
    ...
  },
  "gemini": {
    "enabled": true,  // ✅ You have Google key
    ...
  },
  "openai": {
    "enabled": false,  // ❌ No key yet
    ...
  }
}
```

### Step 4: Test Configuration

```bash
cd ../orchestration

# Using virtual environment (auto-activated)
./router-cli.sh test
```

**Expected output**:
```
✅ Configuration loaded successfully
   Root: /path/to/project
   Mode: solo

🔌 Testing Providers:
   ✅ claude      - Ready
   ✅ gemini      - Ready

🎭 Available Modes:
   ✅ solo       - Single model handles everything
   ✅ ensemble   - Route by task type
   ✅ challenger - Primary generates, challenger reviews

📚 Memory Bank:
   ✅ activeContext.md

✅ Configuration test complete!
```

### Step 5: Test Router

```bash
# Test with a simple request (venv auto-activated)
./router-cli.sh execute "What is 2+2?" --verbose
```

If you see a response, **you're all set!** 🎉

**Note**: The `router-cli.sh` wrapper automatically:
- Activates the virtual environment
- Runs the router
- Deactivates the venv when done
- Shows helpful error messages if dependencies missing

---

## 🔒 Dependency Isolation Benefits

### Why Dev-AID Uses Virtual Environments

**Problem**: Installing Python packages system-wide causes:
- ❌ Version conflicts between projects
- ❌ "Works on my machine" syndrome
- ❌ Difficult cleanup (uninstall affects all projects)
- ❌ Potential system Python corruption

**Dev-AID Solution**: Three-layer isolation strategy:
- ✅ **Router venv** (.dev-aid/orchestration/.venv/) - Router dependencies
- ✅ **RAG uv environment** (~/.local/share/claude-context-local/) - RAG dependencies
- ✅ **System Python** (built-ins only) - No packages installed

### What This Means for You

**1. Zero System Pollution**
```bash
# Before Dev-AID
pip list | wc -l
# Output: 23 packages

# After Dev-AID setup
pip list | wc -l
# Output: 23 packages (unchanged!)
```

**2. Project Isolation**
```bash
# Project A: Uses anthropic==0.40.0
cd ~/project-a/.dev-aid/orchestration
source .venv/bin/activate && pip list | grep anthropic
# anthropic==0.40.0

# Project B: Uses anthropic==0.35.0 (no conflict!)
cd ~/project-b/.dev-aid/orchestration
source .venv/bin/activate && pip list | grep anthropic
# anthropic==0.35.0
```

**3. Easy Cleanup**
```bash
# Remove router entirely
rm -rf .dev-aid/orchestration/.venv

# System Python unaffected ✅
```

**4. Reproducible Environments**
```bash
# Same setup on every machine
./setup-venv.sh
# Always installs exact versions from requirements.txt
```

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Your System                          │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  System Python (3.9+)                                    │
│  ├─ No router packages installed ✅                      │
│  └─ Only built-in modules used (json, sys, etc.)         │
│                                                           │
├───────────────────────────────────────────────────────── │
│                                                           │
│  Project A (.dev-aid/orchestration/.venv/)               │
│  ├─ anthropic==0.40.0                                    │
│  ├─ openai==1.58.1                                       │
│  └─ Isolated from system ✅                              │
│                                                           │
│  Project B (.dev-aid/orchestration/.venv/)               │
│  ├─ anthropic==0.35.0                                    │
│  ├─ openai==1.50.0                                       │
│  └─ Isolated from Project A ✅                           │
│                                                           │
│  claude-context-local (~/.local/share/...)               │
│  ├─ torch, transformers, faiss                           │
│  ├─ Managed by uv (automatic isolation)                  │
│  └─ Isolated from everything ✅                          │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### Complete Isolation Documentation

See [DEPENDENCY-ISOLATION.md](../../docs/DEPENDENCY-ISOLATION.md) for:
- Complete architecture breakdown
- venv vs Anaconda comparison
- Troubleshooting dependency issues
- Best practices for multi-project setups

---

## 📖 Usage

### Command Line

#### Execute Requests

```bash
# Default mode (from config)
./router-cli.sh execute "Implement user authentication"

# Specific mode
./router-cli.sh execute "Analyze entire codebase" --mode ensemble

# With verbose output (shows costs, tokens, latency)
./router-cli.sh execute "Fix the bug in auth.ts" --verbose --mode solo
```

#### Check Status

```bash
# Show current status
./router-cli.sh status

# Include routing history
./router-cli.sh status --history
```

#### Direct Python (if you activated venv manually)

```bash
# Activate venv first
source .dev-aid/orchestration/.venv/bin/activate

# Then use Python directly
python -m router.cli execute "Your request"
python -m router.cli status

# Deactivate when done
deactivate
```

### From Slash Commands

The router integrates with slash commands via bash wrappers:

```bash
# Via router-cli.sh
.dev-aid/orchestration/router-cli.sh execute "Your request"

# Via router.sh (now points to Python implementation)
.dev-aid/orchestration/router.sh execute "Your request"
```

**Integration with existing commands**: The `/dev-aid-router-*` commands will automatically use the Python router once you've completed installation.

---

## 🎭 Orchestration Modes

### Solo Mode (Simplest)

**What it does**: Uses one AI model for everything

**When to use**:
- You only have one API key
- Simple workflows
- Predictable costs

**Configuration** (`.dev-aid/config/settings.json`):
```json
{
  "orchestration_mode": "solo",
  "default_model": "claude-sonnet-4.5"
}
```

**Usage**:
```bash
python -m router.cli execute "Implement login" --mode solo
```

### Ensemble Mode (Smart Routing)

**What it does**: Automatically routes to the best AI for each task type

**Task Classification**:
| Task Type | Routed To | Why? |
|-----------|-----------|------|
| Massive context (100+ files) | Gemini Flash | 2M token context |
| Code generation | Claude Sonnet | Best coder |
| Security audit | Claude Sonnet | Security expert |
| Documentation | GPT-4o | Clear writing |
| Debugging | Claude Sonnet | Strong reasoning |
| Architecture decisions | Claude Opus | Maximum capability |

**When to use**:
- You have multiple AI API keys
- Want cost optimization
- Tasks vary in nature (some large, some small)

**Configuration** (`.dev-aid/config/routing.json`):
```json
{
  "modes": {
    "ensemble": {
      "enabled": true,
      "routing_strategy": "semantic",
      "task_routes": {
        "massive_context": "gemini-flash",
        "code_generation": "claude-sonnet",
        "security_audit": "claude-sonnet",
        "documentation": "gpt-4o"
      }
    }
  }
}
```

**Usage**:
```bash
# Automatically routes based on request
python -m router.cli execute "Analyze entire codebase for API endpoints" --mode ensemble
# → Routes to Gemini (massive context)

python -m router.cli execute "Implement OAuth2" --mode ensemble
# → Routes to Claude (code generation)
```

**Cost Savings Example**:
- 250K token request with Claude: $0.825
- 250K token request with Gemini: $0.021
- **Savings: 97%** 💰

### Challenger Mode (Best Quality)

**What it does**: Primary AI generates, second AI reviews for issues

**Workflow**:
1. Primary (usually Claude) generates solution
2. Challenger (usually Gemini) reviews for:
   - Security vulnerabilities
   - Logic errors
   - Performance issues
   - Edge cases
3. If issues found (HIGH/CRITICAL severity), primary refines
4. You get both perspectives

**When to use**:
- Security-critical code (auth, payments, encryption)
- High-stakes features
- Want extra confidence in code quality

**Auto-triggers on keywords**: `auth`, `password`, `token`, `crypto`, `secret`, `oauth`, `jwt`

**Configuration** (`.dev-aid/config/routing.json`):
```json
{
  "modes": {
    "challenger": {
      "enabled": true,
      "primary_model": "claude-sonnet",
      "challenger_model": "gemini-flash",
      "auto_refine_on": ["HIGH", "CRITICAL"],
      "review_triggers": [
        "auth", "password", "crypto", "token", "secret"
      ]
    }
  }
}
```

**Usage**:
```bash
python -m router.cli execute "Implement password validation" --mode challenger
# Automatically triggers challenger review
```

---

## 💰 Cost Management

### View Costs

```bash
# See today's costs
python -m router.cli status

# See routing history with costs
python -m router.cli status --history
```

### Set Budget Limits

Edit `.dev-aid/config/routing.json`:

```json
{
  "cost_limit_per_day": 100.0
}
```

The router will refuse requests if daily budget is exceeded.

### Cost Tracking

All costs are logged:
- `.dev-aid/logs/routing.log` - Human-readable
- `.dev-aid/logs/costs.json` - Structured data

Example log entry:
```
2025-12-03 14:23:15 [ENSEMBLE] Task: massive_context | Model: gemini-flash | Cost: $0.0212 | Tokens: 250000→5000 | Latency: 8500ms
```

---

## 🔧 Configuration Files

### settings.json

Main Dev-AID settings:

```json
{
  "orchestration_mode": "solo",  // or "ensemble", "challenger"
  "default_model": "claude-sonnet-4.5",
  "enabled_providers": ["claude", "gemini"]
}
```

### routing.json

Router-specific configuration:

```json
{
  "default_mode": "solo",
  "modes": {
    "solo": { "primary_model": "claude-sonnet" },
    "ensemble": { "enabled": true, "task_routes": {...} },
    "challenger": { "enabled": true, "primary_model": "claude-sonnet" }
  },
  "fallback_chain": ["claude-sonnet", "gpt-4o", "gemini-flash"],
  "cost_limit_per_day": 100.0
}
```

### models.json

Model definitions and costs:

```json
{
  "claude": {
    "enabled": true,
    "api_key_env": "ANTHROPIC_API_KEY",
    "models": {
      "sonnet-4.5": {
        "id": "claude-sonnet-4-5",
        "cost_per_1m_tokens": { "input": 3.00, "output": 15.00 }
      }
    }
  }
}
```

---

## ❓ Troubleshooting

### Problem: Dependencies not installed

```
⚠️  Router dependencies not installed

Recommended: Use virtual environment to avoid conflicts

Run: /path/to/.dev-aid/orchestration/setup-venv.sh
```

**Solution (recommended)**:
```bash
cd .dev-aid/orchestration
./setup-venv.sh
```

**Solution (manual - not recommended)**:
```bash
cd .dev-aid/orchestration
pip install -r requirements.txt
# Warning: Installs to system Python
```

### Problem: Authentication not found

```
Error: No authentication found for anthropic
```

**Solution (Option A - Recommended for Claude Pro/Max users)**:
```bash
# Use session-based authentication
claude login  # For Claude
gcloud auth application-default login  # For Gemini

# Verify
cd .dev-aid/orchestration
python -m router.cli auth-status
```

**Solution (Option B - API Keys)**:
1. Create `.dev-aid/config/.env`
2. Add: `ANTHROPIC_API_KEY=sk-ant-...` (or `GOOGLE_API_KEY` or `OPENAI_API_KEY`)
3. Test: `python -m router.cli test`

**Note**: Claude Pro/Max subscriptions don't include API keys - use session auth (Option A)

### Problem: Provider not enabled

```
Error: Provider 'gemini' is not enabled in models.json
```

**Solution**:
1. Edit `.dev-aid/config/models.json`
2. Set `"gemini": { "enabled": true }`
3. Make sure you have `GOOGLE_API_KEY` in `.env`

### Problem: Python not found

```
Error: Python 3 is required but not found
```

**Solution**:
```bash
# Install Python 3.9+
# Ubuntu/Debian
sudo apt install python3 python3-pip

# macOS
brew install python3

# Verify
python3 --version  # Should be 3.9+
```

### Problem: Over budget

```
Error: Daily budget limit exceeded ($100.00)
```

**Solution**:
1. Check costs: `python -m router.cli status`
2. Increase limit in `.dev-aid/config/routing.json`
3. Or wait until tomorrow (resets daily at midnight)

### Problem: Slow responses

**Ensemble mode uses Gemini for large context** - this can take 8-10s for 250K tokens. This is normal!

To speed up:
- Use solo mode for quick tasks
- Reduce context size
- Use Haiku for simple requests

---

## 🎯 Examples

### Example 1: Cost-Optimized Large Analysis

**Task**: Analyze entire codebase (200 files)

**Without router** (Claude only):
```
Cost: $0.825 per run
```

**With router** (ensemble mode):
```bash
python -m router.cli execute "Analyze entire codebase and list all API endpoints" --mode ensemble

# Routes to: Gemini Flash
# Cost: $0.021
# Savings: $0.80 (97%)
```

### Example 2: Security Review

**Task**: Implement authentication

**Without router**:
- Write code yourself
- Hope you didn't miss vulnerabilities
- Manual review

**With router** (challenger mode):
```bash
python -m router.cli execute "Implement JWT authentication" --mode challenger

# Process:
# 1. Claude generates implementation
# 2. Gemini reviews for security issues
# 3. Claude refines based on feedback
# 4. You get secure, reviewed code
```

### Example 3: Mixed Workflow

Use different modes for different tasks:

```bash
# Quick bug fix - Solo mode (fast)
python -m router.cli execute "Fix bug in login.ts" --mode solo

# Large refactor - Ensemble mode (cost-effective)
python -m router.cli execute "Refactor entire auth module" --mode ensemble

# Security feature - Challenger mode (quality)
python -m router.cli execute "Implement OAuth2" --mode challenger
```

---

## 🚀 Next Steps

1. **Test Each Mode**: Try solo, ensemble, and challenger
2. **Monitor Costs**: Run `python -m router.cli status` regularly
3. **Adjust Configuration**: Fine-tune task routes in `routing.json`
4. **Integrate with Slash Commands**: Use from `/dev-aid-router-*` commands
5. **Review Logs**: Check `.dev-aid/logs/routing.log` to understand routing decisions

---

## 📚 Additional Resources

- **Full Documentation**: `.dev-aid/orchestration/router/README.md`
- **Implementation Plan**: `.dev-aid/docs/router/README.md`
- **Architecture Details**: `.dev-aid/orchestration/router/` (source code)
- **Configuration Reference**: `.dev-aid/config/*.json` files

---

## ✅ Verification Checklist

- [ ] Python 3.9+ installed (`python3 --version`)
- [ ] Virtual environment created (`./setup-venv.sh`)
- [ ] Dependencies installed (done by setup-venv.sh)
- [ ] Authentication configured (session auth via `claude login`/`gcloud auth` OR API keys in `.dev-aid/config/.env`)
- [ ] Check auth status: `python -m router.cli auth-status` (should show ✅ for at least one provider)
- [ ] Providers enabled in `.dev-aid/config/models.json`
- [ ] Configuration test passes (`./router-cli.sh test`)
- [ ] Test request works (`./router-cli.sh execute "test"`)
- [ ] Status command shows data (`./router-cli.sh status`)

If all checks pass, **you're ready to use the router!** 🎉

### Verify Virtual Environment

```bash
# Check if venv exists
ls -la .dev-aid/orchestration/.venv

# Check installed packages (inside venv)
source .dev-aid/orchestration/.venv/bin/activate
pip list
deactivate
```
