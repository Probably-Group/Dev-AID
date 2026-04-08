# Dev-AID Router - Python Implementation

Multi-AI orchestration engine that routes requests to different AI providers based on task type and configuration.

## Features

✅ **Multi-Provider Support**: Anthropic (Claude), Google (Gemini), OpenAI (GPT)
✅ **Session-Based Auth**: Works with Claude Pro/Max, Gemini CLI (no API keys needed!)
✅ **Keyring Integration**: Secure access to system keychain (macOS/Windows/Linux)
✅ **Three Orchestration Modes**: Solo, Ensemble, Challenger
✅ **Task Classification**: Automatic routing based on task type
✅ **Cost Tracking**: Real-time cost monitoring and budgets
✅ **Logging**: Structured logging of all routing decisions
✅ **Fallback Chain**: Automatic fallback if primary model fails

## Installation

### 1. Install Python Dependencies

**Important:** All dependencies are pinned to exact versions for reproducible builds and security.

```bash
cd .dev-aid/orchestration

# Option 1: Install directly (not recommended for production)
pip install -r requirements.txt

# Option 2: Use virtual environment (recommended)
./setup-venv.sh
# This creates an isolated environment with all dependencies
```

**Security Note:**
- All 63 dependencies use exact version pins (`==`)
- Prevents supply chain attacks via malicious 'latest' versions
- See requirements.txt for version details and update instructions

### 2. Configure Authentication

Dev-AID Router supports **two authentication methods**:

#### Option A: Session-Based Auth (Recommended for Consumer Subscriptions)

If you have Claude Pro/Max, Gemini CLI, or other consumer subscriptions:

```bash
# Anthropic (Claude Pro/Max)
claude login  # Stores session token locally

# Google (Gemini CLI, ADC)
gcloud auth application-default login  # Stores ADC credentials

# OpenAI
# Note: OpenAI only supports API keys (ChatGPT Plus ≠ API access)
```

**No additional configuration needed!** The router automatically detects and uses your CLI sessions.

#### Option B: API Keys (Traditional Method)

Add your API keys to `.dev-aid/config/.env`:

```bash
# Anthropic (Claude)
ANTHROPIC_API_KEY=sk-ant-...

# Google (Gemini)
GOOGLE_API_KEY=...

# OpenAI (GPT)
OPENAI_API_KEY=sk-...
```

**Priority**: Session auth is tried first, then falls back to API keys.

### 3. Test Configuration

```bash
python -m router.cli test
```

## Usage

### Command Line Interface

```bash
# Execute a request
python -m router.cli execute "Implement user authentication"

# Execute with specific mode
python -m router.cli execute "Analyze codebase" --mode ensemble

# Check authentication status
python -m router.cli auth-status

# Show router status
python -m router.cli status

# Show status with history
python -m router.cli status --history
```

### From Bash (Slash Commands)

```bash
# Via wrapper script
.dev-aid/orchestration/router-cli.sh execute "Your request here"

# Or via router.sh (now points to Python implementation)
.dev-aid/orchestration/router.sh execute "Your request here"
```

### From Python

```python
from router.executor import execute_request

# Execute request
output = execute_request(
    request="Implement user authentication",
    mode="ensemble",  # or "solo", "challenger"
    verbose=True
)

print(output)
```

## Orchestration Modes

### Solo Mode

Single model handles all tasks.

**Configuration**: `.dev-aid/config/settings.json`
```json
{
  "orchestration_mode": "solo",
  "default_model": "claude-sonnet-4.5"
}
```

**Usage**:
```bash
python -m router.cli execute "Your request" --mode solo
```

### Ensemble Mode

Automatic routing to best model based on task type.

**Task Classification**:
- `massive_context`: Large codebase analysis → Gemini (2M context)
- `code_generation`: Writing code → Claude Sonnet
- `security_audit`: Security review → Claude Sonnet
- `documentation`: Writing docs → GPT-4o
- `debugging`: Bug fixes → Claude Sonnet
- `complex_reasoning`: Architecture decisions → Claude Opus

**Configuration**: `.dev-aid/config/routing.json`
```json
{
  "modes": {
    "ensemble": {
      "enabled": true,
      "routing_strategy": "semantic",
      "task_routes": {
        "massive_context": "gemini-flash",
        "code_generation": "claude-sonnet",
        "security_audit": "claude-sonnet"
      }
    }
  }
}
```

**Usage**:
```bash
python -m router.cli execute "Analyze entire codebase" --mode ensemble
```

### Challenger Mode

Two-model review workflow: Primary generates, challenger reviews.

**Workflow**:
1. Primary model generates solution
2. Challenger model reviews for issues
3. If issues found (HIGH/CRITICAL), primary refines
4. User sees all perspectives

**Triggers**: Automatically challenges requests containing:
- Security keywords: `auth`, `password`, `token`, `crypto`, `secret`
- Critical operations: `payment`, `encryption`, `oauth`

**Configuration**: `.dev-aid/config/routing.json`
```json
{
  "modes": {
    "challenger": {
      "enabled": true,
      "primary_model": "claude-sonnet",
      "challenger_model": "gemini-flash",
      "auto_refine_on": ["HIGH", "CRITICAL"],
      "review_triggers": ["auth", "password", "crypto"]
    }
  }
}
```

**Usage**:
```bash
python -m router.cli execute "Implement OAuth2 authentication" --mode challenger
```

## Architecture

```
router/
├── __init__.py           # Package initialization
├── cli.py                # CLI interface
├── executor.py           # Main execution engine
├── config_loader.py      # Configuration loading
├── api_clients.py        # API wrappers (Anthropic, Google, OpenAI)
├── context_builder.py    # Dev-AID context gathering
├── task_classifier.py    # Task type classification
├── cost_tracker.py       # Cost tracking and logging
└── modes/
    ├── solo.py           # Solo mode
    ├── ensemble.py       # Ensemble mode
    └── challenger.py     # Challenger mode
```

## Cost Tracking

All routing decisions are logged with costs:

```
.dev-aid/logs/
├── routing.log           # Human-readable log
└── costs.json            # Structured cost data
```

**View costs**:
```bash
python -m router.cli status

# Or check logs directly
cat .dev-aid/logs/routing.log
```

**Budget limits**: Set in `.dev-aid/config/routing.json`:
```json
{
  "cost_limit_per_day": 100.0
}
```

## Examples

### Example 1: Ensemble Mode Routes to Gemini

```bash
$ python -m router.cli execute "Analyze the entire codebase and find all API endpoints" --mode ensemble --verbose

======================================================================
🤖 Dev-AID Router Response (ENSEMBLE mode)
======================================================================

📊 Task Classification: massive_context
🎯 Explanation: Large-scale codebase analysis requiring extensive context (confidence: 100%)
🤖 Selected Model: gemini-flash

📝 Response:
----------------------------------------------------------------------
I've analyzed your codebase (250 files, 45,000 lines of code).

Here are all the API endpoints I found:

[... detailed analysis ...]
----------------------------------------------------------------------

📊 Metrics:
   Cost: $0.0212
   Tokens: 280,000 input → 5,000 output
   Latency: 8,500ms
```

**Cost savings**: $0.825 (Claude) vs $0.021 (Gemini) = **97% cheaper!**

### Example 2: Challenger Mode Reviews Security Code

```bash
$ python -m router.cli execute "Implement password validation" --mode challenger --verbose

======================================================================
🤖 Dev-AID Router Response (CHALLENGER mode)
======================================================================

⚔️  Challenger Mode Workflow:
   Primary Model: claude-sonnet
   Challenger Model: gemini-flash
   Issues Found: Yes
   ✨ Solution Refined

📝 Response:
----------------------------------------------------------------------
[... refined implementation after challenger feedback ...]
----------------------------------------------------------------------

🔍 Challenger Review:
======================================================================
**SEVERITY**: MEDIUM

**Issues Found:**
1. Password validation doesn't check for common passwords
   - Impact: Users could set "password123"
   - Recommendation: Add common password blacklist

2. No rate limiting on password attempts
   - Impact: Vulnerable to brute force
   - Recommendation: Add rate limiting

[Solution was refined to address these issues]
```

## Troubleshooting

### Dependencies Not Installed

```
Error: anthropic package not installed
```

**Fix**:
```bash
pip install -r .dev-aid/orchestration/requirements.txt
```

### No Authentication Found

```
Error: No authentication found for anthropic
```

**Fix** (choose one method):

**Option 1: Session-Based Auth (Recommended)**
```bash
# For Claude (Pro/Max subscriptions)
claude login

# For Gemini
gcloud auth application-default login

# Check status
python -m router.cli auth-status
```

**Option 2: API Keys**
1. Add to `.dev-aid/config/.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   GOOGLE_API_KEY=...
   OPENAI_API_KEY=sk-...
   ```
2. Run test: `python -m router.cli test`

**Note**: Claude Pro/Max users cannot get API keys - use session auth (Option 1)

### Provider Not Enabled

```
Error: Provider 'gemini' is not enabled in models.json
```

**Fix**:
1. Edit `.dev-aid/config/models.json`
2. Set `"enabled": true` for the provider
3. Add API key to `.env`

### Over Budget

```
Error: Daily budget limit exceeded ($100.00)
```

**Fix**:
1. Check costs: `python -m router.cli status`
2. Increase limit in `.dev-aid/config/routing.json`
3. Or wait until tomorrow (resets daily)

## Development

### Running Tests

```bash
# Test configuration
python -m router.cli test

# Test specific provider
python -m router.config_loader

# Test task classifier
python -m router.task_classifier
```

### Adding New Provider

1. Add provider to `.dev-aid/config/models.json`
2. Implement client in `router/api_clients.py`
3. Add to `create_client()` factory function
4. Test with `python -m router.cli test`

## Performance

- **Routing decision**: < 50ms
- **Task classification**: < 10ms
- **API call latency**: 1-10s (depends on model)
- **Cost tracking overhead**: < 5ms

## Security

- ✅ API keys stored in `.env` (gitignored)
- ✅ Logs sanitized (no secrets logged)
- ✅ Budget limits prevent runaway costs
- ✅ All requests logged for audit

## Contributing

### 🚀 Development Workflow

**Set up local PR checks (recommended):**

```bash
# One-time setup from repo root
../../scripts/setup-git-hooks.sh

# Or run checks manually before pushing
../../scripts/run-pr-checks.sh

# Or use Makefile from this directory
make check      # Run all checks (formatting, linting, tests)
make format     # Auto-fix formatting issues
make test       # Run tests only
```

**All PR checks run locally before CI** - catches Black/Flake8/test issues instantly!

📖 **Full guide:** [Development Workflow](../../docs/DEVELOPMENT-WORKFLOW.md)

### Implementation Status

**Core Features**: ✅ Complete
- ✅ API clients for all 3 providers (Anthropic, Google, OpenAI)
- ✅ Session-based authentication (Claude Pro/Max, Gemini CLI, ADC)
- ✅ System keychain integration (macOS Keychain, Windows Credential Manager, Linux Secret Service)
- ✅ All three orchestration modes (Solo, Ensemble, Challenger)
- ✅ Cost tracking and logging
- ✅ CLI interface with auth-status command
- ✅ Task classification and routing
- ✅ Context building with memory bank and skills
- ✅ MCP integration (see `ROUTER-MCP-INTEGRATION.md`)
- ✅ Unit tests (11 test files, 224 passing tests, 69.71% coverage)
- ✅ Development workflow tools (pre-commit hooks, Makefile, check scripts)
- ✅ E2E integration tests (see `../../docs/IMPLEMENTED-FEATURES-LOG.md`)

## License

MIT License - See LICENSE file in repository root
