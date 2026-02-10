# Frequently Asked Questions (FAQ)

Quick answers to common Dev-AID questions.

---

## 📦 Storage & Git

### Q: Where is the Gemma model stored? Will it be uploaded to GitHub?

**A: No, the model is NOT in your repository and will NOT be uploaded to GitHub.**

**Storage locations:**
- ✅ **Model**: `~/.local/share/claude-context-local/` (in your HOME directory, not project)
- ✅ **Index**: `~/.claude_code_search/` (in your HOME directory, not project)
- ✅ **Size**: ~1.2GB for model + varies for index

**Git behavior:**
- ❌ NOT tracked by Git (stored outside repository)
- ✅ Shared across ALL your projects that use Dev-AID
- ✅ Downloaded once, used everywhere

**Repository size**: Only ~5MB of configuration is committed (without .venv)

[Full details: STORAGE-LOCATIONS.md](./STORAGE-LOCATIONS.md)

---

### Q: Should the whole .dev-aid folder be in .gitignore?

**A: NO! Most of .dev-aid SHOULD be committed.**

**What to commit** ✅:
```
.dev-aid/
├── config/            # ✅ Routing, models (except .env)
├── providers/         # ✅ Expert skills, commands
├── memory-bank/       # ✅ Team knowledge
├── scripts/           # ✅ Setup scripts
├── orchestration/router/  # ✅ Python code
├── docs/              # ✅ Documentation
├── VERSION            # ✅ Version tracking
└── CHANGELOG.md       # ✅ Release notes
```

**What to ignore** ❌:
```
.dev-aid/
├── config/.env*       # ❌ API keys (SECURITY)
├── orchestration/.venv/  # ❌ Virtual environment (70MB)
└── logs/              # ❌ Runtime logs
```

**Why commit most of .dev-aid:**
- ✅ Team shares same expert skills
- ✅ Consistent routing configuration
- ✅ Portable across projects
- ✅ Version control for team changes

**Current .gitignore** already excludes sensitive files:
```gitignore
# API Keys (NEVER commit these!)
.dev-aid/config/.env
.dev-aid/config/.env.*

# Logs and Runtime Files
.dev-aid/logs/*.log
.dev-aid/logs/costs.json
.dev-aid/logs/routing-history.json

# Python Virtual Environment
.dev-aid/orchestration/.venv/
```

[Full details: STORAGE-LOCATIONS.md](./STORAGE-LOCATIONS.md)

---

## 🔄 Updates

### Q: How to update Dev-AID in existing repositories?

**A: Use the automated update script:**

```bash
cd your-project
./.dev-aid/scripts/update-dev-aid.sh
```

**What it does:**
1. ✅ Checks current version
2. ✅ Creates automatic backup (preserves .env, memory-bank, logs)
3. ✅ Updates code, scripts, docs, skills
4. ✅ Updates dependencies
5. ✅ Shows changelog

**Update options:**
- **Option 1**: Pull from official repository (recommended)
- **Option 2**: Copy from local Dev-AID installation
- **Option 3**: Manual update (with guide)

**What's preserved:**
- ✅ Your API keys (.env files)
- ✅ Your memory bank (team knowledge)
- ✅ Your logs (routing history, costs)
- ✅ Your custom modifications

**Time**: 2-5 minutes

[Full details: UPDATING.md](./UPDATING.md)

---

### Q: How often should I update?

**A: Depends on version type:**

| Update Type | Frequency | Risk | Time |
|-------------|-----------|------|------|
| **Patch** (1.0.0 → 1.0.1) | Monthly | ✅ Low | 2 min |
| **Minor** (1.0.0 → 1.1.0) | Quarterly | ⚠️ Medium | 5 min |
| **Major** (1.x → 2.0) | Yearly | ⚠️ High | 15-30 min |

**Recommendation:**
- Individual: Update monthly for security patches
- Teams: Coordinate updates, test in staging first
- CI/CD: Pin version in README, update together

**Check for updates:**
```bash
# Your version
cat .dev-aid/VERSION

# Latest version
curl -s https://raw.githubusercontent.com/your-org/dev-aid/main/.dev-aid/VERSION
```

[Full details: UPDATING.md](./UPDATING.md)

---

## 🔒 Dependencies & Isolation

### Q: Will Dev-AID install packages to my system Python?

**A: No! Dev-AID uses three-layer isolation - ZERO system pollution.**

**Architecture:**
```
1. Router venv (.dev-aid/orchestration/.venv/)
   - Router Python packages (anthropic, openai, etc.)
   - ~70MB per project

2. RAG uv environment (~/.local/share/claude-context-local/)
   - RAG Python packages (torch, transformers, etc.)
   - ~1.2GB, shared across all projects

3. System Python (built-ins only)
   - NO packages installed
   - Only uses json, sys (built-in modules)
```

**Proof:**
```bash
# Before Dev-AID
pip list | wc -l
# Output: 23 packages

# After Dev-AID setup
pip list | wc -l
# Output: 23 packages (unchanged!)
```

**Benefits:**
- ✅ No version conflicts between projects
- ✅ Each project can use different package versions
- ✅ Easy cleanup (just delete .venv/)
- ✅ Reproducible environments

[Full details: DEPENDENCY-ISOLATION.md](./DEPENDENCY-ISOLATION.md)

---

### Q: Why not use Anaconda instead of venv?

**A: venv is lighter and perfect for Dev-AID's needs.**

| Feature | Python venv | Anaconda |
|---------|-------------|----------|
| **Size** | ~50MB | ~3GB |
| **Installation** | Built into Python 3.3+ | Separate download |
| **Speed** | Fast | Slower |
| **Use Case** | Pure Python ✅ | Data science + system libs |
| **Dev-AID fit** | ✅ Perfect | ❌ Overkill |

**Why venv:**
- ✅ Built-in, no extra installation
- ✅ Lightweight for pure Python packages
- ✅ Standard practice for Python development
- ✅ Sufficient for router dependencies

**When to use Anaconda:**
- If you're already using it for data science
- If you need system-level libraries (CUDA, etc.)
- If your team standardizes on conda

**Note**: RAG uses `uv` (not venv or conda) because claude-context-local chose it. You don't manage it - it's automatic.

[Full details: DEPENDENCY-ISOLATION.md](./DEPENDENCY-ISOLATION.md)

---

## 🏗️ Architecture

### Q: What parts of Dev-AID run in which environment?

**A: Clear separation by component:**

| Component | Environment | Location | Isolation |
|-----------|-------------|----------|-----------|
| **Router** | Router venv | `.dev-aid/orchestration/.venv/` | Per-project |
| **RAG** | uv environment | `~/.local/share/claude-context-local/` | Shared, automatic |
| **Scripts** | System bash | `.dev-aid/scripts/` | No Python needed |
| **Hooks** | System bash | `.dev-aid/providers/*/hooks/` | No Python needed |
| **Status check** | System Python | Built-in json.tool | No packages |

**Execution examples:**

```bash
# Router (uses venv automatically)
./router-cli.sh execute "request"
# → Activates .venv/, runs router, deactivates

# RAG (uses uv automatically)
claude-context-local index .
# → uv run handles isolation automatically

# Scripts (no Python packages)
./setup-rag.sh
# → Pure bash, calls Python only for built-ins

# Hooks (no Python packages)
git commit
# → Runs bash hooks with security tools (not Python)
```

[Full details: STORAGE-LOCATIONS.md](./STORAGE-LOCATIONS.md)

---

## 🚀 Performance

### Q: How big is Dev-AID? Will it slow down my repository?

**A: Repository impact is minimal (5MB). Heavy files are in home directory.**

**Breakdown:**

| Location | What | Size | In Git? |
|----------|------|------|---------|
| Repository | Config, scripts, skills | ~5MB | ✅ Yes |
| Repository | Virtual env (.venv) | ~70MB | ❌ No (ignored) |
| Repository | Logs | ~1MB | ❌ No (ignored) |
| Home directory | RAG model | ~1.2GB | ❌ No (not in repo) |
| Home directory | RAG index | ~200MB | ❌ No (not in repo) |

**Git operations:**
- `git clone`: Downloads ~5MB for Dev-AID
- `git pull`: Updates only changed config files (~KB)
- `git push`: Uploads only config changes (~KB)

**Repository size impact**: +5MB (negligible)

[Full details: STORAGE-LOCATIONS.md](./STORAGE-LOCATIONS.md#-total-disk-usage)

---

## 🔐 Security

### Q: Are my API keys safe?

**A: Yes, with proper .gitignore.**

**Protection layers:**
1. ✅ `.dev-aid/config/.env` is in `.gitignore`
2. ✅ Update script preserves .env (never overwrites)
3. ✅ Backup script excludes .env from commits

**Verify:**
```bash
# Check .env is ignored
git status --ignored | grep .env
# Should show: .dev-aid/config/.env (ignored)

# Try to add .env (should fail)
git add .dev-aid/config/.env
# Output: The following paths are ignored by one of your .gitignore files
```

**Best practices:**
- ✅ Use `.env` files for API keys
- ✅ Never commit `.env` (already in .gitignore)
- ✅ Use `.env.example` as template (commit this)
- ✅ Team members create own `.env` from example

**Example .env.example:**
```bash
# Anthropic (Claude) - Get from https://console.anthropic.com/
ANTHROPIC_API_KEY=your-key-here

# Google (Gemini) - Get from https://aistudio.google.com/app/apikey
GOOGLE_API_KEY=your-key-here

# OpenAI (GPT) - Optional
OPENAI_API_KEY=your-key-here
```

---

## 🤝 Team Usage

### Q: How do teams use Dev-AID across multiple projects?

**A: Each developer has own setup, team shares config.**

**Per-Developer (not shared):**
- API keys (`.env` - personal credentials)
- RAG model (~1.2GB in home directory - downloaded once)
- Virtual environment (.venv/ - per project, ignored in Git)

**Team-Shared (in Git):**
- Configuration (routing.json, models.json)
- Expert skills (all 85 skills - core, expert, process)
- Memory bank (team knowledge, ADRs)
- Scripts (setup, automation)

**Setup for new team member:**
```bash
# 1. Clone repository (includes .dev-aid/ config)
git clone <repo>
cd project

# 2. Setup router (5 minutes)
./.dev-aid/orchestration/setup-venv.sh

# 3. Add personal API keys
cp .dev-aid/config/.env.example .dev-aid/config/.env
nano .dev-aid/config/.env  # Add keys

# 4. Optional: Setup RAG (10 minutes, one-time)
./.dev-aid/scripts/setup-rag.sh

# Done! ✅
```

**Keeping in sync:**
```bash
# Pull latest config from team
git pull

# Update Dev-AID if version changed
./.dev-aid/scripts/update-dev-aid.sh
```

---

## 🛠️ Productivity Tools

### Q: What developer productivity tools does Dev-AID provide?

**A: Dev-AID includes 7 standalone utility scripts for common development tasks:**

**CI/CD Automation:**
- **`generate-ci.sh`** - Auto-generate GitHub Actions workflows from project detection
  - Detects: Node.js, Python, Rust, Go with package managers
  - Security by default (Gitleaks + Trivy included)
  - Usage: `.dev-aid/scripts/generate-ci.sh`

**Architecture & Visualization:**
- **`map-architecture.sh`** - Generate Mermaid.js diagrams from codebase
  - Creates: Class diagrams, dependency graphs, C4 component diagrams
  - Supports: Python (AST), TypeScript/JavaScript (regex)
  - Usage: `.dev-aid/scripts/map-architecture.sh`

**Testing & Data:**
- **`fabricate-data.sh`** - Generate realistic mock test data
  - Supports: JSON Schema, Pydantic models, TypeScript interfaces
  - Formats: JSON, CSV, SQL INSERT statements
  - Usage: `.dev-aid/scripts/fabricate-data.sh schema.json -c 100 -f csv`

**Documentation:**
- **`sync-docs.sh`** - Detect documentation drift
  - Checks: Package manager commands, scripts, Docker ports
  - Compares: README vs package.json, pyproject.toml, Dockerfile
  - Usage: `.dev-aid/scripts/sync-docs.sh`

**Developer Experience:**
- **`dev-aid-guide.sh`** - Interactive feature discovery menu
  - Usage: `.dev-aid/scripts/dev-aid-guide.sh`
- **`draft-pr.sh`** - Generate PR descriptions from git diff
  - Usage: `.dev-aid/scripts/draft-pr.sh > pr-description.md`
- **`onboard.sh`** - New developer onboarding assistant
  - Usage: `.dev-aid/scripts/onboard.sh`

**All scripts are:**
- ✅ Ready to use (no configuration needed)
- ✅ Standalone (can be copied to other projects)
- ✅ Well-documented with `--help` options

[Full details: COMMANDS-REFERENCE.md](./COMMANDS-REFERENCE.md#-utility-scripts)

---

## 💰 Cost

### Q: What's the total cost to use Dev-AID?

**A: $0 for Dev-AID itself. You only pay for AI API usage.**

**Dev-AID costs:**
- ✅ Software: $0 (open source)
- ✅ RAG (local): $0 forever
- ✅ Storage: ~2.8GB disk space (one-time)

**You pay for:**
- AI API usage (Anthropic, Google, OpenAI)
- Cost depends on your usage, not Dev-AID

**Cost optimization:**
- ✅ Ensemble mode routes to cheapest model
- ✅ Gemini Flash 97% cheaper than Claude for large context
- ✅ Local RAG saves $0.13/M tokens (vs cloud embeddings)
- ✅ Cost tracking logs every request with token usage

**Example savings:**
```
Without Dev-AID: $45/month (all Claude Sonnet)
With Dev-AID:    $22/month (smart routing)
Savings:         $23/month (51%)

With Local RAG:  $10/month (67% token reduction)
Total Savings:   $35/month (78%)
```

[Full details: README.md Cost Analysis](../../README.md#-cost-analysis)

---

## 🧠 AI Context

### Q: What is the memory-bank folder for?

**A: A shared knowledge base for AI assistants (Claude, Gemini, Cursor, etc.) with smart loading.**

**What it contains:**
- `activeContext.md` - Current sprint/focus (**auto-loaded** every request)
- `patterns.md` - Coding conventions AI should follow (**on-demand**)
- `security.md` - Security rules (non-negotiable) (**on-demand**)
- `decisions.md` - Architecture decisions (ADRs) (**on-demand**)
- `testing.md` - Testing standards (**on-demand**)
- `performance.md` - Performance guidelines (**on-demand**)
- `chaos.md` - Error handling patterns (**on-demand**)

**How it works:**
- Claude Code auto-loads files via `@` references in CLAUDE.md
- The orchestration router loads on-demand files based on **query relevance** (keyword matching)
- **Token budget** prevents context window bloat (configurable: minimal/balanced/generous)
- **Staleness detection** warns when files haven't been updated in >30 days
- **Write-back prompts** instruct AI to update memory bank when it learns new patterns or decisions
- Files exceeding token budget are **smart-trimmed** to most relevant sections

**Benefits:**
- ✅ Consistent code from AI assistants
- ✅ No repeating context every session
- ✅ Team knowledge persists across developers
- ✅ Only relevant context loaded per query (saves tokens)
- ✅ AI assistants keep memory bank up to date

[Full details: MEMORY-BANK-GUIDE.md](./MEMORY-BANK-GUIDE.md)

---

## 🛠️ Compatibility

### Q: Which editors and AI tools does Dev-AID support?

**Native support** (slash commands, skills, hooks — full feature set):
- Claude Code (terminal CLI + VS Code extension)
- Gemini CLI (terminal + VS Code/JetBrains via Gemini Code Assist)
- Codex CLI (via AGENTS.md triggers)
- Cursor (reads `.claude/commands/` natively)
- Windsurf (reads `.claude/commands/` natively)
- Cline (VS Code extension, reads `.claude/commands/`)

**MCP integration** (skills + local search, but no custom slash commands):
- VS Code Copilot Chat
- Zed
- JetBrains AI Assistant

**Summary:** 6 tools with full native support, 3 more via MCP.

---

## 🔗 Quick Links

- [STORAGE-LOCATIONS.md](./STORAGE-LOCATIONS.md) - Storage architecture
- [DEPENDENCY-ISOLATION.md](./DEPENDENCY-ISOLATION.md) - Isolation strategy
- [UPDATING.md](./UPDATING.md) - Update guide
- [MEMORY-BANK-GUIDE.md](./MEMORY-BANK-GUIDE.md) - Memory bank for AI assistants
- [README.md](../../README.md) - Full documentation

---

**Still have questions?** Open an issue or discussion on GitHub!
