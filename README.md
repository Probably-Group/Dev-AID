![Dev-AID Logo](./img/dev-aid-logo-small.png)

# 🚀 Dev-AID (Development AI Driver)

[![CI](https://github.com/Probably-Group/Dev-AID/actions/workflows/pr-check.yml/badge.svg)](https://github.com/Probably-Group/Dev-AID/actions/workflows/pr-check.yml)
[![OpenSSF Scorecard](https://img.shields.io/badge/OpenSSF_Scorecard-Active-green?logo=opensourcesecurity)](https://github.com/Probably-Group/Dev-AID/security/code-scanning)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Version](https://img.shields.io/badge/version-1.5.0--beta.3-brightgreen.svg)](.dev-aid/VERSION)

*You're in flow, solving a real problem — then a merge conflict pulls you out. An hour later, you're writing tests instead of shipping.* **Dev-AID changes that.** It supercharges your AI coding tools with auto-loading expertise, dual-AI review, and security automation on every commit. One setup, nothing new to learn — it works inside the tools you already use.

> **💡 Other tools make you choose. Dev-AID lets you use the best of everything.**

> **🎯 Dev-AID adds structure to AI-assisted development: expert skills guide AI behavior, verification gates demand proof, and dual-AI review catches what single-model workflows miss.**

> 📊 **For Managers/Stakeholders:** See **[VALUE-PROPOSITION.md](./VALUE-PROPOSITION.md)** for ROI analysis ($6.5M+ annual value for 100-dev teams).

---

### TL;DR - One Command Examples

```bash
# All commands use short /aid-* aliases — type /aid- for autocomplete

/aid-challenger "Implement OAuth2 with refresh tokens"  # Dual-AI review
/aid-pr 135                        # Review a PR
/aid-test src/auth/                # Generate tests
/aid-conflict 42 smart             # Resolve merge conflict
/aid-debt src/ high                # Tech debt scan
/aid-research "async patterns"     # Deep research
/aid-audit                         # Security audit
/aid-commit                        # Plan atomic commits
/aid-help                          # Show all commands

# Security scanning runs automatically on every commit
git commit -m "feat: add login"    # → Gitleaks, Trivy, Opengrep in ~10s

# Setup (one-time)
gh extension install Probably-Group/gh-dev-aid
gh dev-aid init                    # Initialize Dev-AID
./.dev-aid/scripts/setup-local-llm.sh  # Optional: local AI ($0, offline)
```

---

## 🚀 Quick Start

### Install Dev-AID into Your Project

```bash
# Install the Dev-AID CLI (one-time)
gh extension install Probably-Group/gh-dev-aid

# Add Dev-AID to your project
cd ~/my-project
gh dev-aid init

# Start your AI coding tool
claude    # or gemini, cursor, windsurf, etc.
```

That's it. Type `/aid-help` to see all available commands.

<details>
<summary><strong>Manual installation (without GitHub CLI)</strong></summary>

```bash
# 1. Clone Dev-AID
git clone https://github.com/Probably-Group/Dev-AID.git

# 2. Copy .dev-aid into your project
cp -r Dev-AID/.dev-aid ~/my-project/.dev-aid

# 3. Initialize
cd ~/my-project
./.dev-aid/scripts/setup-dev-aid.sh
```
</details>

### Optional Add-ons (run inside your project)

```bash
# Local semantic search ($0, offline, 5 min setup)
./.dev-aid/scripts/setup-rag.sh

# Local LLM — zero-cost AI (auto-detects GPU, installs Ollama)
./.dev-aid/scripts/setup-local-llm.sh

# Security scanning tools (Gitleaks, Trivy, Opengrep)
./.dev-aid/automation/tools/install-security-tools.sh
```

---

## 😤 What Dev-AID Automates

| Task | Typical Time | Dev-AID Solution | Time Saved |
|--------------|-------------|------------------|------------|
| **Merge conflicts** | 10-30 min each | AI understands both sides, resolves intelligently | 90% |
| **GitHub issues** | 15-45 min to analyze & fix | AI proposes complete solution with code | 80% |
| **Writing tests** | Hours per feature | AI generates comprehensive test suites | 70-85% |
| **PR descriptions** | 5-10 min each | Auto-generated from git diff | 95% |
| **Security reviews** | 30+ min manual checks | Automated on every commit (CVE, SAST, secrets) | 100% |
| **Debugging** | 30-45 min root cause | AI diagnosis in <10 min | 70% |
| **Code reviews** | Waiting for reviewers | Dual-AI review catches bugs instantly | 60% |
| **CI/CD setup** | Days of YAML hell | Auto-generated, optimized workflows | 90% |
| **Documentation** | "I'll do it later" | AI keeps docs in sync with code | 55% |
| **Context switching** | 50× per day | Works inside your existing tools | 100% |

---

## 🎯 What is Dev-AID?

Dev-AID enhances your existing AI tools (Claude Code, Gemini CLI, Cursor, Windsurf, Cline, Codex CLI) with:

- **🤖 Intelligent Automation** - Resolves issues, conflicts, generates tests
- **🔀 Multi-AI Router** - Best model for each task, dual-AI code review
- **🏠 Local LLM Support** - Offline, private, zero-cost AI via Ollama/LM Studio 🆕
- **🔍 Local Code Search** - Hybrid BM25 + Vector search, 100% private, $0 forever
- **🎓 73 Expert Skills** - Auto-loads domain expertise (DevSecOps, API design, etc.)
- **⚡ 8 Process Skills** - Enforce TDD, verification, systematic debugging
- **🏗️ Architect Mode** - Two-agent pattern: plan before implementation
- **📂 Git Worktree Isolation** - Parallel development with conflict detection
- **💾 Session Persistence** - Auto-save/restore progress across restarts
- **🔒 Security Automation** - CVE, SAST, secrets, misconfig scanning on every commit
- **✅ Skill Validators** - Extensible compliance checking per skill (bash, Python, auto-discovered)

**No new CLI to learn.** Works inside the tools you already use — native with Claude Code, Gemini CLI, Codex CLI, Cursor, Windsurf, Cline + MCP with VS Code Copilot Chat, Zed, JetBrains AI Assistant.

### How It Works

```
┌─────────────────────────────────────────────┐
│  Your Familiar Environment                  │
│  ✨ claude code        (no change needed)   │
│  ✨ cursor .           (no change needed)   │
│  ✨ gemini-cli         (no change needed)   │
│  ✨ codex              (no change needed)   │
│  ✨ Any AI tool with config support         │
└─────────────────┬───────────────────────────┘
                  │
                  │ Dev-AID Configuration
                  │ (loaded automatically)
                  ↓
┌─────────────────────────────────────────────┐
│  Your AI Gets Superpowers ⚡                 │
│  • 100% local semantic search (private RAG) │
│  • Multi-AI orchestration (best tool/task)  │
│  • MCP integration (databases, GitHub, etc) │
│  • 5 core + 73 expert + 8 process skills    │
│  • Persistent memory (ADRs, patterns)       │
│  • Automated security (CVE+SAST+secrets)    │
│  • Specialized workflows (slash commands)   │
└─────────────────────────────────────────────┘

Real-World Examples:
• "Find authentication functions"
  → Local RAG searches instantly ($0, never leaves your machine)

• /aid-challenger "Implement OAuth2"
  → Claude generates code, Gemini reviews security, all in one command

• "Show me all users in database with open GitHub issues"
  → MCP servers query Postgres + GitHub, combine results automatically

• Start coding session
  → Auto-loads relevant skills based on your tech stack (Python, React, Docker...)

• Edit src/auth/password.ts
  → devsecops-expert skill provides OWASP guidelines in context

• git commit
  → Automatic security scans (Gitleaks, Trivy, Opengrep) in ~10s

• /aid-router-status
  → View AI routing decisions and costs across all sessions
```

---

## 🎯 Core Features

<details open>
<summary><strong>🤖 Autonomous Agent Framework + APO</strong> — 8 agents, 16 tools, 4 providers, automatic prompt optimization</summary>

Provider-agnostic autonomous AI agents powered by Dev-AID's 73+ expert skills. Each agent runs an autonomous loop: send to LLM → parse tool calls → execute tools → repeat.

| Feature | What It Does | Developer Benefits |
|---------|-------------|-------------------|
| **8 Built-in Agents** | PR reviewer, test generator, tech debt hunter, CI fixer, conflict resolver, research, onboarding, doc auditor | Ready-to-use agents for common workflows |
| **16 Built-in Tools** | File I/O, git, GitHub, bash, search — all with safety enforcement | Agents can read, write, search, and interact with git/GitHub |
| **4 Provider Adapters** | Anthropic, OpenAI, Google Gemini, Local (Ollama/LM Studio) | Use any provider — switch with `--provider` |
| **Skill Integration** | Loads SKILL.md files as system prompts | Agents get expert knowledge from Dev-AID's 73+ skills |
| **Safety System** | Command blocklist, dry-run mode, per-tool risk levels | Safe by default — dangerous operations require explicit opt-in |
| **Trace Collection** | JSONL execution traces with `--trace` flag | Debug agent behavior, feed into APO |
| **Automatic Prompt Optimization** | LLM-driven prompt improvement with beam search and golden tests | Continuous improvement with human approval gate |

**Quick Start:**
```bash
/aid-pr 135                        # Review a PR
/aid-test src/auth/                # Generate tests
/aid-debt src/ high                # Tech debt scan
/aid-team security-audit-team -m "Audit auth module"  # Multi-agent team
```

**For CI/scripts:** `dev-aid-agent pr-reviewer --pr 135 --json`

📖 [**Agent Framework Guide**](.dev-aid/docs/Dev-AID-AGENTS.md) — CLI reference, slash commands, agent catalog, tools, safety, configuration.

</details>

<details>
<summary><strong>🔀 Multi-AI Router</strong> — 4 routing modes, dual-AI review, 97% cost savings on large context</summary>

- **Challenger mode** - Claude generates, Gemini reviews
- **Ensemble mode** - Route to best AI for each task
- **Cost optimization** - Gemini for large context (97% cheaper)
- **Configuration-driven** - JSON-based routing rules
- **Slash commands** - `/aid-challenger`, `/aid-ensemble`, `/aid-help`

</details>

<details>
<summary><strong>🏠 Local LLM Support</strong> — Offline, private, zero-cost AI via Ollama/LM Studio/llama.cpp</summary>

**Run AI models locally for offline, private, zero-cost inference.**

| Feature | Description |
|---------|-------------|
| **Privacy** | Your code never leaves your machine |
| **Offline** | Works without internet connection |
| **Zero Cost** | No API fees, no usage limits |
| **Auto-Detection** | Detects your GPU/VRAM automatically |
| **Smart Recommendations** | Suggests best model for your hardware |

**Inference Runtimes** (software that runs models on your hardware):
- **[Ollama](https://ollama.ai)** - Easy CLI tool with built-in model library (recommended)
- **[LM Studio](https://lmstudio.ai)** - GUI app with visual model browser
- **[llama.cpp](https://github.com/ggerganov/llama.cpp)** - C++ runtime, maximum control

> **Clarification:** Ollama, LM Studio, and llama.cpp are **runtimes** (like Docker for containers), not models themselves. They run open-source models like Qwen, Phi, Codestral, etc.

**Recommended Models (2026 Benchmarks):**

| Model | Score | VRAM | Best For |
|-------|-------|------|----------|
| **Phi-4-Mini** | 58 | 3GB | Entry-level, fast iterations |
| **Codestral 22B** | 72 | 14GB | Mid-tier excellence |
| **Qwen2.5-Coder 32B** | 68 | 20GB | ⭐ Best bang-for-buck |
| **GLM-4.7 Thinking** | 74 | 48GB | Deep reasoning |
| **Kimi-K2-Thinking** | 83 | 80GB | Best-in-class |

**Quick Start:**
```bash
./.dev-aid/scripts/setup-local-llm.sh    # Interactive setup wizard
ollama pull qwen2.5-coder:32b            # Or manually with Ollama
```

<details>
<summary>Hardware Guide</summary>

| Tier | VRAM | RAM | Recommended Model |
|------|------|-----|-------------------|
| Entry | 4-8GB | 16GB | Phi-4-Mini |
| Mid | 14-16GB | 24GB | Codestral 22B |
| High | 20-24GB | 32GB | Qwen2.5-Coder 32B |
| Pro | 48GB+ | 64GB | GLM-4.7 Thinking |
| Enterprise | 80GB+ | 128GB | Kimi-K2-Thinking |
| CPU-only | N/A | 32GB+ | Phi-4-Mini (slow) |

</details>

<details>
<summary>How Local LLM Integrates with Dev-AID</summary>

```
┌─────────────────────────────────────────────────────────────┐
│                   Dev-AID Router                             │
│  Routes requests to optimal provider based on task type      │
└──────┬──────────────┬──────────────┬──────────────┬─────────┘
       │              │              │              │
       ▼              ▼              ▼              ▼
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│  Claude  │   │  Gemini  │   │  OpenAI  │   │  Local   │
│   API    │   │   API    │   │   API    │   │   LLM    │
│          │   │          │   │          │   │  (Local) │
└──────────┘   └──────────┘   └──────────┘   └──────────┘
   Cloud          Cloud          Cloud         Your GPU
```

- **Dev-AID Router** can route tasks to local LLMs alongside cloud providers
- **Simple tasks** → Route to local (free, private)
- **Complex reasoning** → Route to cloud (Claude Opus)
- **Massive context** → Route to Gemini (1M+ tokens)

> **Note:** Local LLM support works through Dev-AID's router, not as a backend for Claude Code or Gemini CLI directly. Those tools use their own proprietary APIs.

</details>

📖 **[Complete Local LLM Guide](.dev-aid/docs/LOCAL-LLM-GUIDE.md)** | **[Developer Guide](.dev-aid/docs/LOCAL-LLM-DEVELOPER-GUIDE.md)**

</details>

<details>
<summary><strong>🔍 Dev-AID Local Search (RAG)</strong> — Hybrid BM25 + Vector search, 100% private, $0 forever</summary>

- **100% local** - Code never leaves your machine
- **$0 forever** - No API costs for embeddings
- **EmbeddingGemma model** - Google's state-of-the-art embeddings
- **Fast** - 0.15s queries with FAISS vector search
- **Smart** - AST parsing for 9+ languages
- **MCP native** - Works with Claude Code, Gemini CLI, Codex CLI, Cursor, Windsurf, Cline + VS Code/Zed/JetBrains via MCP
- **Based on** - claude-context-local by [FarhanAliRaza](https://github.com/FarhanAliRaza/claude-context-local) (embedded fork)

</details>

<details>
<summary><strong>🎓 Skills System</strong> — 5 core + 73 expert + 8 process skills for automated checking, domain expertise, and workflow enforcement</summary>

#### 🛡️ 5 Core Skills — Automated Checking

Core skills **actually run tools** automatically (tests, linters, type checkers) and provide immediate feedback:

| Skill | What It Does | Token Cost | Default |
|-------|-------------|------------|---------|
| `code-reviewer` | Real-time code quality suggestions | 250 tokens | ✅ Enabled |
| `secret-scanner` | Prevent credential leaks before commit | 250 tokens | ✅ Enabled |
| `test-runner` | Auto-run relevant tests on file save | 250 tokens | ⏸️ Disabled |
| `linter` | Auto-lint code (ESLint, Flake8, Clippy) | 250 tokens | ⏸️ Disabled |
| `type-checker` | Auto-check types (TypeScript, mypy, cargo) | 250 tokens | ⏸️ Disabled |

**Configure**: Run `/aid-config` to enable/disable
- **Minimal** (default): code-reviewer + secret-scanner = 500 tokens (0.25%)
- **Maximum** (all enabled): 1,250 tokens (0.625%)

#### 🎓 73 Expert Skills — Domain Expertise (Hook-Based Auto-Loading)

Expert skills **give advice** (not automated execution) and auto-load based on context:

- **Intelligent auto-loading** - Detects project context (tech stack, files) at session start
- **Scoring algorithm** - Ranks skills by relevance (keywords, technologies, file patterns)
- **Zero configuration** - Works automatically for Claude Code and Gemini CLI
- **Universal architecture** - Same auto-loading logic across all AI providers
- **Manual activation** - Still available via skill name when needed
- **Custom skills** - Generate new skills with `/aid-skill`
- **Domains**: DevSecOps, TDD, API design, databases, etc. [full list](.dev-aid/providers/claude/.claude/skills/expert)

#### 📋 8 Process Skills — Workflow Enforcement

Process skills **enforce how you work**, not just what you know:

| Skill | What It Does | Enforcement | Default |
|-------|-------------|-------------|---------|
| `verification-gate` | No completion claims without test evidence | Strict | ✅ On |
| `tdd-protocol` | Enforce RED-GREEN-REFACTOR cycle | Warning | ⚠️ On |
| `systematic-debugging` | Root cause first, fix second (4-phase) | Warning | ⚠️ On |
| `architect-protocol` | Architecture-first approach: plan → approve → implement | Warning | ⚠️ On |
| `isolated-development` | Git worktree per feature/issue | Off | ⏸️ Off |
| `design-first` | Think before coding (YAGNI enforcement) | Warning | ⚠️ On |
| `staged-review` | Two-stage review (spec → quality) | Warning | ⚠️ On |
| `plan-execution` | Batch execution with checkpoints | Warning | ⚠️ On |

**Key enhancements over traditional process patterns:**
- **Language-aware commands** - Auto-detects Python/Node/Rust/Go for verification
- **Router integration** - Challenger mode for cross-model verification
- **Local search** - FAISS integration for finding similar tests/patterns
- **Security tools** - Correlates with Trivy/Gitleaks findings
- **Configurable** - strict/warning/off per skill

**Key Difference:**
- **Core skills** → Execute tools automatically
- **Expert skills** → Provide knowledge and guidance
- **Process skills** → Enforce workflow discipline

</details>

<details>
<summary><strong>🔒 Security Automation</strong> — Pre-commit/pre-push hooks with CVE, SAST, secrets, misconfig scanning</summary>

- **Pre-commit hooks**: Secrets scan, SAST, Critical CVEs (~10s)
- **Pre-push hooks**: Full SAST + language-specific security checks (~90s)
  - Universal: Gitleaks (secrets + git history), Opengrep (10 universal + 12 auto-detected language rulesets), Trivy (CVE + misconfig)
  - Language SAST: ShellCheck (bash), Flawfinder (C/C++), mobsfscan (Swift), Bandit (Python) — auto-detected
  - Dependency audit: pip-audit, npm audit, cargo audit, govulncheck — auto-detected
- **Isolated dependencies**: Virtual environments, zero system pollution ([details](./.dev-aid/docs/DEPENDENCY-ISOLATION.md))

</details>

<details>
<summary><strong>🤖 Intelligent Automation</strong> — AI-powered issue resolution, conflict resolution, auto-triage, and git hooks</summary>

AI-powered automation for issues, conflicts, and workflows - saving hours of manual work while following best practices.

| Feature | What It Does | Developer Benefits | Documentation |
|---------|-------------|-------------------|---------------|
| 🎯 **Issue Resolution** | Analyzes GitHub issues and proposes complete solutions using LLMs | ⏱️ Saves 15-45 min per issue<br>✅ Follows your code style<br>🔒 Safety checks for security issues<br>📝 Detailed implementation guidance | [Quick Start](.dev-aid/docs/ISSUE-RESOLVER-GUIDE.md) |
| 🔧 **Conflict Resolution** | Automatically resolves merge conflicts by understanding both sides | ⏱️ Saves 10-30 min per conflict<br>🧠 Smart merge strategies<br>🔁 Avoids "redo" work<br>✨ Preserves intent from both branches | [Quick Start](.dev-aid/docs/CONFLICT-RESOLVER-GUIDE.md) |
| 🏷️ **Auto-Triage** | Labels and categorizes new issues automatically | ⏱️ Instant issue organization<br>📊 Complexity estimation<br>🎯 Identifies auto-fixable issues<br>👥 Better team coordination | [GitHub Actions](.dev-aid/docs/AUTOMATION-README.md#phase-4-github-actions-) |
| 🪝 **Git Hooks** | Detects conflicts and offers automated resolution locally | ⚡ Immediate feedback<br>🔧 Optional auto-fix<br>💡 Helpful guidance<br>🚫 Prevents broken merges | [Git Hooks](.dev-aid/docs/AUTOMATION-README.md#phase-3-conflict-resolution-) |
| 🔄 **GitHub Actions** | Automated workflows for triage, conflict detection, and issue fixing | 🤖 24/7 automation<br>📈 Scales with team<br>🔒 Configurable safety<br>📊 Audit trail | [Complete Guide](.dev-aid/docs/AUTOMATION-README.md) |

**Key Commands:**
```bash
dev-aid-resolve-issue --issue 123 --mode ensemble    # Analyze and resolve GitHub issues
dev-aid-fix-conflicts --strategy smart               # Resolve merge conflicts intelligently
.dev-aid/automation/git-hooks/install.sh             # Install git hooks
```

📖 [**Complete Automation Guide**](.dev-aid/docs/AUTOMATION-README.md)

</details>

<details>
<summary><strong>🚀 Productivity Tools</strong> — API contract generator, commit planner, pre-commit reviewer</summary>

Essential tools for faster, higher-quality development workflows.

| Feature | What It Does | Developer Benefits | Commands |
|---------|-------------|-------------------|----------|
| 🎯 **API Contract Generator** | Generate OpenAPI specs, TypeScript clients, MSW mocks from data models | ⏱️ **Unblocks frontend immediately** (2-4 weeks saved)<br>🔄 Parallel frontend/backend development<br>📝 Single source of truth prevents API drift<br>✅ Auto-generated contract tests<br>🎭 MSW mocks enable offline development | `/aid-api --from models/user.ts` |
| 📋 **Commit Planner** | Analyzes unstaged changes and proposes atomic commits | ⏱️ **Saves 10-15 min/day** in commit planning<br>🎓 Teaches good git habits<br>✅ Safe (no git history manipulation)<br>🔄 Interactive planning with preview<br>📊 Cleaner git history for easier debugging | `/aid-commit` |
| 🔍 **Pre-Commit Reviewer** | Comprehensive "rubber duck" review before committing | ⏱️ **Saves 5-10 min/commit** catching issues early<br>🔒 Security checks (secrets, injection, auth)<br>⚡ Performance anti-patterns<br>🧪 Missing test detection<br>🎯 Focus modes (security, tests, style) | `/aid-review --focus security` |

> See [VALUE-PROPOSITION.md](./VALUE-PROPOSITION.md) for detailed ROI analysis of these tools.

**Quick Start:**
```bash
/aid-api --from src/models/user.ts --name UserAPI   # Generate API contract from model
/aid-commit                                          # Plan atomic commits
/aid-review --focus security                         # Review staged changes
```

</details>

<details>
<summary><strong>💾 Persistent Memory Bank</strong> — Cross-session context with on-demand loading, token budgets, and staleness detection</summary>

- Context survives across sessions
- Architecture decisions (ADRs)
- Code patterns & anti-patterns
- Security guidelines
- **Team-shared via git** — no cloud sync needed, new devs get full context on clone
- **On-demand loading** — files loaded based on query relevance, not unconditionally
- **Token budget** — configurable budget (minimal/balanced/generous) prevents context bloat
- **Staleness detection** — warns when memory bank files haven't been updated recently
- **Write-back** — AI assistants prompted to update memory bank when patterns/decisions change
- **Section extraction** — oversized files trimmed to most relevant sections per query

</details>

<details>
<summary><strong>🔌 MCP (Model Context Protocol) Integration</strong> — Dual-layer architecture with auto-discovery and smart context gathering</summary>

Connect your AI to external data sources and tools via the industry-standard Model Context Protocol. Dev-AID provides **two-layer MCP support** for maximum flexibility.

| Feature | What It Does | Developer Benefits |
|---------|-------------|-------------------|
| 🔍 **Auto-Discovery** | Discovers MCP servers from Claude Code and Gemini CLI configurations | 🚀 Zero duplication needed<br>📦 Share servers across tools<br>🔄 One install, works everywhere |
| 🎯 **Smart Context Gathering** | Router pre-fetches database schemas, GitHub issues, search results before sending to LLM | ⚡ Faster responses<br>🧠 Better context quality<br>💰 Fewer API roundtrips |
| 🔒 **Security Hardened** | Environment variable isolation prevents API key leakage to MCP servers | 🛡️ LLM keys stay safe<br>🔐 Per-server credentials<br>✅ MITM protection |
| 🎨 **Dual-Layer Architecture** | LLM CLIs use MCP natively + Router can enhance with additional context | 🔌 Works with/without router<br>⚙️ Optional enhancement<br>🎮 Full control |

**Quick Start:**
```bash
# Install MCP servers via your LLM CLI
claude mcp add github npx -y @modelcontextprotocol/server-github
claude mcp add postgres npx -y @modelcontextprotocol/server-postgres
claude mcp add brave-search npx -y @modelcontextprotocol/server-brave-search

# Discover servers from CLI configs
python -m router.cli mcp discover

# Enable for Dev-AID router enhancement (optional)
python -m router.cli mcp enable github
python -m router.cli mcp enable postgres

# Use with router (MCP context auto-gathered)
python -m router.cli execute "Show database schema and related GitHub issues" --mode ensemble

# Or use directly via LLM CLI (no router needed)
claude code  # MCP servers work automatically
```

**How It Works:**

**Layer 1: Native LLM CLI Usage**
```
Your LLM CLI (Claude Code, Gemini) → Uses MCP servers directly
```
- MCP servers configured via `claude mcp add` work automatically
- No Dev-AID router needed for basic MCP usage
- All major LLMs support MCP (Claude, OpenAI, Gemini, local LLMs)

**Layer 2: Router Enhancement (Optional)**
```
Dev-AID Router → Discovers servers → Pre-gathers context → Enhanced LLM request
```
- Router discovers MCP servers from CLI configs
- Connects to enabled servers for context gathering
- Pre-fetches schemas, issues, search results
- Sends enhanced context to LLM in system prompt
- LLM can still use MCP servers directly during execution

**Supported MCP Servers:**
- **Databases**: PostgreSQL, MySQL, SQLite
- **APIs**: GitHub, Jira, Slack, Linear, Google Drive
- **Search**: Brave Search, Exa, code search
- **Tools**: File system, browser automation (Puppeteer), AWS
- **Custom**: Build your own MCP servers

📖 **[Complete MCP Guide](.dev-aid/docs/MCP-GUIDE.md)** — Installation, security, troubleshooting, and advanced usage.

</details>

<details>
<summary><strong>⚡ Optimized CI/CD Generator</strong> — Auto-detect tech stack, 40-70% faster CI, configurable frequency profiles</summary>

Generate production-ready GitHub Actions workflows tailored to your tech stack—with optional performance optimizations that make CI 40-70% faster and configurable frequency profiles to control GitHub Actions costs.

| Feature | What It Does | Developer Benefits |
|---------|-------------|-------------------|
| 🔍 **Smart Detection** | Auto-detects Python, Node.js, Go, Rust, Java, C#, PHP, Ruby, C++ projects | 🚀 Zero configuration needed<br>📦 Right package manager detected<br>🎯 Tech-stack specific commands |
| ⚡ **Optimization Mode** | Optional `--optimize` flag adds advanced caching, concurrency, parallel execution | ⏱️ 40-70% faster CI runs<br>💰 Reduced GitHub Actions costs<br>🔄 Cancels outdated runs automatically |
| 📊 **Frequency Profiles** | Three configurable CI execution profiles: aggressive, balanced, minimal | 💰 Up to 95% cost reduction<br>🎯 Choose thoroughness vs. cost<br>⚙️ Automatic workflow configuration |
| 🛡️ **Security Built-In** | All workflows include Gitleaks + Trivy scanning by default | 🔒 Catches secrets & CVEs early<br>✅ Production-ready security<br>📊 SARIF reports to GitHub |
| 🎨 **Tech-Stack Aware** | Different optimizations per language (venv caching for Python, node_modules for Node.js, cargo for Rust) | 🧠 Smart caching strategies<br>⚡ Parallel linting/testing<br>🏗️ Build artifact caching |

**CI Frequency Profiles:**

- **Aggressive (100% cost)**: Maximum thoroughness - Runs on every push/PR, 3 OS platforms, no filters
- **Balanced (15-30% cost)**: Recommended default - PR-only, single OS, code file filters, draft skip
- **Minimal (5-10% cost)**: Lowest overhead - Main branch only, minimal triggers

**Quick Start:**
```bash
# Generate standard workflow
./.dev-aid/scripts/generate-ci.sh /path/to/your/project

# Generate optimized workflow with balanced frequency (recommended)
./.dev-aid/scripts/generate-ci.sh /path/to/your/project --optimize --frequency balanced

# Generate minimal cost workflow
./.dev-aid/scripts/generate-ci.sh /path/to/your/project --optimize --frequency minimal
```

<details>
<summary>Optimization Examples by Language</summary>

**Python** - Virtual env caching, parallel linting (Black + Isort + Flake8)
```yaml
# Before optimization: 5 min
# After optimization: 1.5-2 min (58-73% faster)

- Concurrency groups cancel outdated runs
- Full venv caching (not just pip)
- Shared setup job (install once, reuse 3x)
- Parallel linting: black & isort & flake8 & wait
```

**Node.js** - node_modules caching, parallel linting (ESLint + Prettier + TSC)
```yaml
# Before: 4 min
# After: 1.5 min (62% faster)

- node_modules cache + package manager cache
- Parallel linting: eslint & prettier & tsc & wait
- Optimized for npm, pnpm, yarn, bun
```

**Go** - Module + build cache, parallel checks
```yaml
# Before: 3 min
# After: 1 min (67% faster)

- Go module cache + build artifact cache
- Parallel: gofmt & go vet & wait
- Race detector in tests
```

**Rust** - Comprehensive cargo caching, parallel clippy + fmt
```yaml
# Before: 8 min (compile heavy)
# After: 2-3 min (62-75% faster with warm cache)

- Cache: registry + git + build artifacts
- Parallel: cargo fmt & cargo clippy & wait
- Incremental compilation
```

</details>

**Real-World Cost Example (5-developer team, 20 PRs/week):**
- **Aggressive**: 900 min/week (46,800 min/year) - Maximum confidence
- **Balanced**: 120 min/week (6,240 min/year) - **87% savings**
- **Minimal**: 10 min/week (520 min/year) - **98% savings**

📖 **[CI Optimization Guide](.dev-aid/docs/CI-OPTIMIZATION-GUIDE.md)** | **[CI Frequency Guide](.dev-aid/docs/CI-FREQUENCY-GUIDE.md)**

</details>

<details>
<summary><strong>🔄 Safe Update System</strong> — Interactive conflict resolution, auto-rollback, SHA256 verification</summary>

Dev-AID's update system ensures you never lose customizations while staying current with latest features and security patches.

| Feature | What It Does | Developer Benefits |
|---------|-------------|-------------------|
| 🛡️ **Protected Paths** | Never overwrites `.env`, memory-bank, custom skills, RAG indices, logs | 🔒 Your data always safe<br>🎯 API keys never lost<br>📝 Custom work preserved |
| ⚔️ **Conflict Resolution** | Interactive prompts for each modified file with 5 options: keep/take/merge/diff/skip | 🎮 Full control over updates<br>👁️ See exactly what changed<br>🔀 Choose resolution per file |
| 🔙 **Automatic Rollback** | Creates timestamped backups, auto-restores on errors | 🛟 Safe experimentation<br>⏮️ One-command undo<br>💾 Keep last 3 backups |
| 🔐 **Security Verification** | SHA256 checksum validation on all downloads | 🚫 Prevent MITM attacks<br>✅ Verify authenticity<br>🔒 Tamper detection |
| 🔔 **Weekly Auto-Check** | Silent background checks with 7-day cache (respects GitHub rate limits) | 📢 Never miss updates<br>⚡ Stay current automatically<br>💰 Free tier friendly |
| 🎯 **Breaking Change Detection** | Semantic version analysis warns about major version bumps | ⚠️ Know before you update<br>📋 See release notes first<br>🛡️ Avoid surprises |

**Quick Start:**
```bash
./.dev-aid/scripts/check-updates.sh          # Check for updates (cached for 7 days)
./.dev-aid/scripts/update-dev-aid.sh          # Update with interactive conflict resolution
./.dev-aid/scripts/update-dev-aid.sh --dry-run  # Preview changes without applying
./.dev-aid/scripts/rollback.sh                # Rollback to previous version
```

<details>
<summary>Interactive Conflict Resolution Example</summary>

When the update system detects files you've modified, it shows you a diff and asks:
```
⚠️  Conflict in: .dev-aid/config/providers.yaml

[y] Keep YOUR version (preserve customizations)
[u] Take UPSTREAM version (accept new version)
[m] Manual MERGE (create merge file with conflict markers)
[d] Show DIFF again
[s] SKIP this file for now

Your choice [y/u/m/d/s/?]:
```

</details>

**Automatic Session Notifications:**

Dev-AID checks for updates automatically on session start (throttled to once per 24h, shared across all your projects):
```
⬆️  Update available: 1.5.0-beta.1 -> 1.6.0 (run: gh dev-aid update)
```

**Update via CLI Extension:**
```bash
gh dev-aid check    # Check for updates
gh dev-aid update   # Apply update (with backup + protected paths)
```

📖 **[Complete Update System Guide](.dev-aid/docs/UPDATE-SYSTEM-GUIDE.md)** — Detailed walkthroughs, troubleshooting, and advanced usage.

</details>

---

<details>
<summary><strong>✨ Complete Feature Reference Table</strong> — All Dev-AID capabilities ranked by developer impact</summary>

| Feature | What It Does | Key Benefits | Impact |
|---------|-------------|--------------|--------|
| **🏠 Local LLM Support** 🆕 | Run AI locally via Ollama/LM Studio/llama.cpp | • **$0 forever** (no API costs)<br>• 100% private (code stays local)<br>• Works offline<br>• Auto hardware detection | ⭐⭐⭐⭐⭐ |
| **🔍 Hybrid Search** | BM25 lexical + Vector semantic search with RRF fusion | • Best of both: keywords + meaning<br>• Configurable alpha weighting<br>• $0 forever (no API costs)<br>• AST-aware (9+ languages) | ⭐⭐⭐⭐⭐ |
| **🔀 Multi-AI Router** | Route tasks to best LLM (Claude/Gemini/OpenAI) with challenger mode | • 97% cost savings (Gemini for big context)<br>• Dual-AI review catches bugs<br>• Automatic task classification | ⭐⭐⭐⭐⭐ |
| **🏗️ Architect Mode** | Two-agent pattern: Architect plans, Implementer executes | • Prevents wasted work<br>• User approval before coding<br>• Model-agnostic (any provider)<br>• Fallback to solo mode | ⭐⭐⭐⭐ |
| **📂 Git Worktree Isolation** | Parallel development with scope declarations and conflict detection | • Scope declarations prevent overlap<br>• Architecture locks protect critical code<br>• Pre-merge conflict detection<br>• Clear cleanup workflow | ⭐⭐⭐⭐ |
| **💾 Session Persistence** | Auto-save progress on session end, restore on restart | • Never lose your place<br>• Cross-provider support<br>• Git-aware (tracks branch, changes)<br>• Task/todo preservation | ⭐⭐⭐⭐ |
| **🛡️ 5 Core Skills** | Automated checking (test-runner, linter, type-checker, code-reviewer, secret-scanner) | • Real-time feedback on file save<br>• Actually runs tools automatically<br>• Configurable (2 enabled by default) | ⭐⭐⭐⭐⭐ |
| **🎓 73 Expert Skills** | Auto-loading domain expertise (DevSecOps, TDD, API design, etc.) | • Zero config (auto-detects context)<br>• Scoring algorithm ranks relevance<br>• Custom skill generation | ⭐⭐⭐⭐⭐ |
| **💾 Persistent Memory** | Cross-session context (ADRs, patterns, security guidelines) | • Context survives sessions<br>• Team-shared via git (no cloud needed)<br>• New devs get full context on clone | ⭐⭐⭐⭐ |
| **🔒 Automated Security** | Pre-commit/pre-push hooks with CVE, SAST, secrets, misconfig scanning | • 10s pre-commit scan<br>• Catches secrets before push<br>• Covers: deps, Dockerfiles, IaC, code | ⭐⭐⭐⭐⭐ |
| **🤖 Issue Auto-Resolution** | AI analyzes GitHub issues and proposes complete solutions | • Saves 15-45 min/issue<br>• Follows your code style<br>• Safety checks for security | ⭐⭐⭐⭐ |
| **🔧 Conflict Auto-Resolution** | Smart merge conflict resolution understanding both sides | • Saves 10-30 min/conflict<br>• Preserves intent<br>• Avoids "redo" work | ⭐⭐⭐⭐ |
| **🔌 MCP Integration** | Connect to databases, GitHub, APIs via Model Context Protocol | • Install once, works everywhere<br>• Secure (key isolation)<br>• Pre-gathers context | ⭐⭐⭐⭐ |
| **🎯 API Contract Generator** | Generate OpenAPI specs, TypeScript clients, and MSW mocks from models | • Unblocks frontend immediately<br>• Parallel development<br>• Contract-first approach<br>• Auto-generated tests | ⭐⭐⭐⭐ |
| **🧠 Smart Context Init** | Intelligent CLAUDE.md/GEMINI.md initialization with quality detection | • Detects existing progressive disclosure<br>• Quality assessment (good/incomplete/draft/poor)<br>• Enhanced templates (OWASP, testing)<br>• Multi-provider support | ⭐⭐⭐⭐ |
| **🔬 Deep Research MCP** | Multi-provider research system (Gemini/Perplexity/Tavily) with smart routing | • Auto-selects best provider per query<br>• Semantic caching (70% similarity)<br>• MCP server integration<br>• CLI: `dev-aid-research` | ⭐⭐⭐⭐ |
| **⚡ 8 Process Skills** | Behavioral protocols enforcing TDD, verification, systematic debugging | • TDD: 40-90% defect reduction<br>• Verification-gate: no false completions<br>• Language-aware commands<br>• Configurable (strict/warning/off) | ⭐⭐⭐⭐⭐ |
| **🤖 Agent Framework** 🆕 | Autonomous AI agents with tool use (8 agents, 16 tools, 4 providers) | • Provider-agnostic (Anthropic/OpenAI/Google/Local)<br>• Skill-powered system prompts<br>• Safety: blocklist + dry-run + risk levels<br>• CLI: `dev-aid-agent <agent> [options]` | ⭐⭐⭐⭐⭐ |
| **🧠 Agent APO** 🆕 | Automatic Prompt Optimization with trace collection and beam search | • JSONL trace collection (`--trace`)<br>• LLM-driven critique + beam search<br>• Golden test scoring<br>• Human approval gate (no auto-deploy) | ⭐⭐⭐⭐ |
| **📦 TOON Format** | Token-optimized notation for 40-60% token reduction on structured data | • Pure Python (no Node.js)<br>• JSON ↔ TOON converter<br>• Better accuracy (73.9% vs 69.7%)<br>• $30-50K/year savings | ⭐⭐⭐⭐ |
| **📋 Commit Planner** | AI-guided atomic commits from unstaged changes | • Prevents mega-commits<br>• Teaches good habits<br>• Safe (no git history manipulation)<br>• Interactive planning | ⭐⭐⭐⭐ |
| **🔍 Pre-Commit Reviewer** | Comprehensive review of staged changes before commit | • Catches issues early<br>• Security/performance/tests<br>• Optional blocking<br>• Saves review time | ⭐⭐⭐⭐ |
| **⚡ CI/CD Generator** | Auto-generate optimized GitHub Actions workflows | • 40-70% faster CI<br>• Security built-in<br>• Tech-stack aware<br>• Frequency profiles (up to 98% cost reduction) | ⭐⭐⭐⭐ |
| **📦 SBOM Generation** | Software Bill of Materials in releases | • Supply chain transparency<br>• Compliance ready<br>• Dependency diff tool<br>• CycloneDX + SPDX | ⭐⭐⭐⭐ |
| **🔍 Impact Analysis** | Find code that depends on a function/class | • Shows affected files<br>• Test suggestions<br>• JSON/Markdown output<br>• Saves 30-60 min pre-refactor | ⭐⭐⭐⭐ |
| **🌳 Dependency Tree** | Visualize import relationships | • Forward/reverse deps<br>• Mermaid diagrams<br>• Circular detection<br>• Python/JS/TS support | ⭐⭐⭐⭐ |
| **❤️ Health Check** | Quick status of Dev-AID components | • Exit 0/1 for scripts<br>• Checks RAG/Router/Skills<br>• Age warnings<br>• Pre-commit ready | ⭐⭐⭐ |
| **🔄 Safe Update System** | Update Dev-AID without losing customizations | • Interactive conflict resolution<br>• Auto-rollback on errors<br>• Protected paths (.env, memory) | ⭐⭐⭐⭐ |
| **📊 Code Health Analysis** | Comprehensive quality metrics, test coverage, maintainability scoring | • Identify tech debt<br>• Track quality trends<br>• Actionable insights | ⭐⭐⭐⭐ |
| **🛡️ Vulnerability Scanning** | Deep CVE scanning with auto-fix recommendations | • CVE database correlation<br>• Severity scoring<br>• Patch guidance | ⭐⭐⭐⭐ |
| **🏷️ Auto-Triage (GitHub)** | Automatically label and categorize new issues | • Instant organization<br>• Complexity estimation<br>• Auto-fixable detection | ⭐⭐⭐ |
| **📐 Architecture Mapping** | Generate Mermaid diagrams (class, dependency, C4) | • Visual codebase understanding<br>• Onboarding acceleration<br>• Documentation automation | ⭐⭐⭐ |
| **🎭 Mock Data Generation** | Generate realistic test data from schemas | • JSON/CSV/SQL formats<br>• Schema-aware<br>• Pydantic/TypeScript support | ⭐⭐⭐ |
| **📝 PR Description Generator** | Auto-generate PR descriptions from git diff | • Saves 5-10 min/PR<br>• Consistent format<br>• Detailed changelogs | ⭐⭐⭐ |
| **👨‍💻 Developer Onboarding** | Automated onboarding for new team members | • Environment checks<br>• Project detection<br>• Setup guidance | ⭐⭐⭐ |
| **⚙️ Reconfiguration Tool** | Change settings without breaking memory/context | • Safe config changes<br>• Backup automation<br>• No data loss | ⭐⭐ |
| **📚 Documentation Sync** | Detect when docs drift from reality | • Package manager checks<br>• Script validation<br>• Port verification | ⭐⭐ |
| **✅ Skill Validator Framework** | Auto-discovered compliance validators per skill (bash, Python, extensible) | • 14 bash checks + 8 Python AST checks<br>• Context-aware (runs relevant validators)<br>• JSON output for CI<br>• Extensible: drop `validate.py` in any skill | ⭐⭐⭐⭐ |
| **🔧 Skill Condensing** | Auto-condense skills >500 lines into references | • Keep skills concise<br>• Organized structure<br>• Better context usage | ⭐⭐ |
| **🔄 Model Registry Updates** | Keep AI model catalog current with latest releases | • Latest model info<br>• Pricing updates<br>• Capability tracking | ⭐⭐ |

**Legend:** ⭐⭐⭐⭐⭐ = Game-changer | ⭐⭐⭐⭐ = High impact | ⭐⭐⭐ = Solid value | ⭐⭐ = Nice to have

</details>

<details>
<summary><strong>🆚 How Dev-AID Compares</strong> — vs. standalone AI coding tools and enhancement frameworks</summary>

**Dev-AID is not a replacement — it's an enhancement layer that works WITH your existing tools.**

#### vs. Standalone AI Coding Tools

| Capability | Dev-AID | [Cursor](https://cursor.sh) | [GitHub Copilot](https://github.com/features/copilot) | [Aider](https://aider.chat) | [Windsurf](https://windsurf.com) |
|------------|---------|--------|----------------|-------|----------|
| **Type** | Enhancement layer | Full IDE | IDE extension | CLI tool | Full IDE |
| **Works with existing tools** | ✅ 6 native + 3 MCP | ❌ Replaces IDE | ⚠️ Limited IDEs | ✅ Any terminal | ❌ Replaces IDE |
| **Multi-AI routing** | ✅ 4 modes (solo/challenger/ensemble/architect) | ⚠️ Model selection | ⚠️ Model selection | ✅ Any model | ⚠️ Model selection |
| **Dual-AI review (Challenger)** | ✅ Claude → Gemini reviews | ❌ | ❌ | ❌ | ❌ |
| **Local LLM support** | ✅ Ollama/LM Studio/llama.cpp | ⚠️ Via API override | ❌ | ✅ Native Ollama | ⚠️ Enterprise only |
| **Local RAG ($0 forever)** | ✅ EmbeddingGemma + FAISS | ⚠️ Cloud-based | ⚠️ Cloud-based | ❌ | ⚠️ Cloud-based |
| **Expert skills** | ✅ 73 auto-loading | ❌ | ❌ | ❌ | ❌ |
| **Process skills** | ✅ 8 behavioral protocols | ❌ | ❌ | ❌ | ❌ |
| **Agent framework** | ✅ 8 agents, 16 tools, 4 providers | ✅ Background agents | ✅ Coding agent | ⚠️ Scripting mode | ✅ Cascade agent |
| **Security scanning** | ✅ CVE + SAST + Secrets + Misconfig | ❌ | ✅ CodeQL Autofix | ❌ | ⚠️ Platform-level |
| **Deep research** | ✅ Gemini/Perplexity/Tavily | ❌ | ❌ | ❌ | ❌ |
| **MCP integration** | ✅ Dual-layer (native + router) | ❌ | ❌ | ❌ | ❌ |
| **Session persistence** | ✅ Auto-save/restore | ❌ | ❌ | ❌ | ❌ |
| **Architect mode** | ✅ Plan → approve → implement | ❌ | ❌ | ❌ | ❌ |
| **Git worktree isolation** | ✅ Scope + conflict detection | ❌ | ❌ | ❌ | ❌ |
| **Memory bank** | ✅ Git-synced, query-aware, token-budgeted | ❌ | ❌ | ❌ | ❌ |
| **CI/CD generator** | ✅ Auto-detect + frequency profiles | ⚠️ Agent can generate | ⚠️ Agent can generate | ❌ | ❌ |
| **Cost tracking** | ✅ Built-in with budget limits | ✅ Spend limits | ✅ Premium budgets | ✅ Token reporting | ⚠️ Credit dashboard |
| **Pre-commit review** | ✅ AI-driven staged review | ✅ Agent hooks | ✅ Copilot Code Review | ⚠️ Hook-based | ⚠️ Linting hooks |
| **Commit planning** | ✅ AI-guided atomic commits | ⚠️ /plan mode | ❌ | ⚠️ Auto-commits | ❌ |
| **API contract generation** | ✅ OpenAPI + TS clients + MSW | ⚠️ Agent can generate | ❌ | ❌ | ❌ |
| **SBOM generation** | ✅ CycloneDX + SPDX | ❌ | ❌ | ❌ | ❌ |
| **Onboarding assistant** | ✅ Interactive onboarding | ❌ | ⚠️ Code explanation | ❌ | ✅ Built-in |
| **Doc sync / drift detection** | ✅ Automated detection | ❌ | ⚠️ Basic | ❌ | ❌ |
| **Skill validators** | ✅ Auto-discovered compliance | ❌ | ❌ | ❌ | ❌ |
| **Safe update system** | ✅ Rollback + conflict resolution | ❌ | ❌ | ⚠️ Git revert | ❌ |
| **Token optimization** | ✅ TOON format (40-60%) | ❌ | ❌ | ❌ | ❌ |
| **Cost** | **Free** (open source) | $20/mo | $10-19/mo | Free (BYOK) | $15-60/mo |
| **Privacy** | ✅ 100% local option | ❌ Cloud | ❌ Cloud | ✅ Local option | ❌ Cloud |

#### vs. Claude Code Enhancement Frameworks

| Capability | Dev-AID | [everything-claude-code](https://github.com/affaan-m/everything-claude-code) | [agents](https://github.com/wshobson/agents) | [Superpowers](https://github.com/obra/superpowers) | [claude-context](https://github.com/zilliztech/claude-context) | [my-claude-code-setup](https://github.com/centminmod/my-claude-code-setup) |
|------------|---------|----------------------|--------|-------------|----------------|---------------------|
| **GitHub Stars** | ~100 | **42.7K** ⭐ | **28.2K** ⭐ | **48.2K** ⭐ | 5.3K | 1.8K |
| **Type** | Multi-provider framework | Claude config collection | Agent orchestration | Skills framework | Semantic search MCP | Starter template |
| **Multi-provider support** | ✅ 6 native + 3 MCP | ❌ Claude only | ❌ Claude only | ❌ Claude only | ❌ Claude only | ❌ Claude only |
| **Expert skills/agents** | 73 + 8 process | 108 agents + 129 skills | 112 agents + 73 plugins | ~15 skills | ❌ | ❌ |
| **Multi-AI router** | ✅ 4 modes (challenger/ensemble/architect/solo) | ⚠️ Model tier strategy | ❌ | ❌ | ❌ | ❌ |
| **Local LLM support** | ✅ Ollama/LM Studio/llama.cpp | ❌ | ❌ | ❌ | ⚠️ Cloud embeddings | ❌ |
| **Local RAG** | ✅ FAISS + BM25 hybrid ($0, private) | ❌ | ❌ | ❌ | ⚠️ Zilliz Cloud | ❌ |
| **Security automation** | ✅ CVE + SAST + Secrets + Misconfig | ⚠️ Trufflehog + npm audit | ✅ SAST + dependency scan | ❌ | ❌ | ❌ |
| **Agent framework** | ✅ 8 agents, 16 tools, 4 providers | ✅ 15+ agents, PM2 orchestration | ✅ 16 orchestrators | ✅ Parallel subagents | ❌ | ⚠️ Subagents |
| **Process skills (TDD)** | ✅ 8 behavioral protocols | ✅ /tdd, /plan commands | ⚠️ Basic | ✅ Core strength | ❌ | ❌ |
| **Session persistence** | ✅ Auto-save/restore | ⚠️ Basic | ❌ | ❌ | ❌ | ❌ |
| **Architect mode** | ✅ Two-agent pattern | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Hybrid search (BM25+Vector)** | ✅ RRF fusion | ❌ | ❌ | ❌ | ✅ Zilliz-based | ❌ |
| **Git worktree isolation** | ✅ With safeguards | ❌ | ❌ | ✅ Basic | ❌ | ❌ |
| **Memory bank** | ✅ Git-synced, query-aware, token-budgeted | ⚠️ Basic | ❌ | ⚠️ Memory notes | ❌ | ✅ Synced |
| **MCP integration** | ✅ Dual-layer (native + router) | ⚠️ Limited | ❌ | ❌ | ✅ Vector search | ✅ Multiple servers |
| **Deep research** | ✅ Gemini/Perplexity/Tavily | ❌ | ❌ | ❌ | ❌ | ❌ |
| **CI/CD generator** | ✅ Auto-detect + frequency profiles | ❌ | ✅ cicd-automation plugin | ❌ | ❌ | ❌ |
| **Cost tracking** | ✅ Built-in with budget limits | ❌ | ⚠️ Model selection guide | ❌ | ⚠️ Token reduction | ✅ USD cost display |
| **Pre-commit review** | ✅ AI-driven staged review | ✅ Code reviewer agent | ✅ code-review-ai plugin | ✅ Code review skills | ❌ | ❌ |
| **Commit planning** | ✅ AI-guided atomic commits | ✅ Planner agent | ⚠️ git-pr-workflows | ✅ writing-plans skill | ❌ | ❌ |
| **API contract generation** | ✅ OpenAPI + TS + MSW | ❌ | ⚠️ api-scaffolding plugin | ❌ | ❌ | ❌ |
| **Doc sync / drift detection** | ✅ Automated detection | ✅ Doc updater agent | ⚠️ documentation plugin | ❌ | ❌ | ✅ Memory sync |
| **Skill validators** | ✅ Auto-discovered compliance | ⚠️ Review agents | ✅ Compliance plugins | ⚠️ Verification skill | ❌ | ❌ |
| **Safe update system** | ✅ Rollback + conflict resolution | ✅ Versioned releases | ❌ | ❌ | ❌ | ❌ |
| **SBOM generation** | ✅ CycloneDX + SPDX | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Onboarding assistant** | ✅ Interactive onboarding | ❌ | ⚠️ team-collaboration | ❌ | ❌ | ✅ /init command |
| **Token optimization** | ✅ TOON format (40-60%) | ⚠️ Progressive disclosure | ✅ Progressive disclosure | ❌ | ✅ 40% reduction | ❌ |

**Legend:** ✅ = Full support | ⚠️ = Partial/Limited | ❌ = Not available

> 💡 **Bottom line:** Other frameworks lock you into Claude. Dev-AID lets you use the best of everything.

</details>

<details>
<summary><strong>🔬 Research-Backed Results</strong> — Based on 100+ case studies</summary>

| Task | Without AI | With Generic AI | With Dev-AID |
|------|------------|-----------------|--------------|
| Unit Testing | Baseline | 40% faster | **70-85% faster** |
| Refactoring | Baseline | 19% SLOWER* | **50-60% faster** |
| Debugging | 30-45 min | 20 min | **<10 min** |
| Code Review | Wait hours | N/A | **Instant dual-AI** |

*\*METR study: Senior devs 19% slower with generic AI on complex features. Dev-AID's challenger mode fixes this.*

**Real Results:**
- AWS: 9-month migration → 16 weeks (56% faster)
- Nubank: 12x efficiency on tech debt cleanup
- DreamHost: 273 tests in 3 days, zero manual code

> 📖 **Full analysis**: [VALUE-PROPOSITION.md](./VALUE-PROPOSITION.md)

</details>

---

## 🆕 Latest Changes

- **🤖 Autonomous Agent Framework** — 8 agents, 16 tools, 4 providers with slash commands (`/aid-pr`, `/aid-test`, `/aid-team`) — [Guide](.dev-aid/docs/Dev-AID-AGENTS.md)
- **🧠 Agent APO** — Automatic Prompt Optimization with trace collection (`--trace`), beam search, and golden test scoring
- **🏠 Local LLM Support** — Offline AI via Ollama/LM Studio/llama.cpp with hardware auto-detection and smart model recommendations
- **🔍 Hybrid Search** — BM25 + Vector with Reciprocal Rank Fusion, two-agent Architect Mode, Git Worktree Isolation, Session Persistence

📖 **[Full release notes →](./WHATS-NEW.md)** | **[Changelog](./.dev-aid/CHANGELOG.md)**

---

## 📚 Available Slash Commands

### 🔍 **RAG Commands** (Local Semantic Search)

**In Claude Code or Gemini CLI:**

```bash
# Find code with natural language
You: "Find all authentication functions"
AI: *uses local RAG, returns relevant code*

# Or via router with RAG
/aid-challenger-rag "Implement password reset"
```

**What happens:**
1. Searches codebase semantically (local, $0 cost)
2. Finds similar implementations & patterns
3. Claude generates using YOUR codebase style
4. Gemini reviews for security issues

> 💡 **How does the AI know to use local search?** See [How Local Search Works](.dev-aid/docs/HOW-LOCAL-SEARCH-WORKS.md) for the complete explanation of MCP integration and automatic tool selection.

### 🔀 **Router Commands** (Multi-AI Orchestration)

> **All commands have short `aid-*` aliases.** Type `aid-` in autocomplete to browse everything.
> Full names (`dev-aid-router-*`) also work.

#### `/aid-challenger` (alias for `dev-aid-router-challenger`)
**Two-AI review workflow**

```bash
/aid-challenger "Implement OAuth2 authentication"
```

**Process:**
1. Claude generates implementation
2. Gemini reviews for security issues
3. Claude refines based on feedback
4. You see both perspectives

**Best for:** Security-critical features, auth, payments, encryption

---

#### `/aid-challenger-rag` (alias for `dev-aid-router-challenger-rag`)
**Challenger mode + Local RAG**

```bash
/aid-challenger-rag "Add password validation"
```

**Process:**
1. **Local search** finds existing patterns (0.15s, $0)
2. Claude generates using your patterns
3. Gemini reviews with same context
4. Result: Code matching your style + security review

**Best for:** When you have similar code and want consistency

---

#### `/aid-ensemble` (alias for `dev-aid-router-ensemble`)
**Smart routing to optimal AI**

```bash
/aid-ensemble "Analyze entire codebase for security issues"
```

**Routing logic:**
- **Massive context** (100k+ tokens) → Gemini Flash (1M context, 97% cheaper)
- **Code generation** → Claude Sonnet (best coder)
- **Security audit** → Claude Sonnet (security expert)
- **Documentation** → GPT-4o (clear writing)
- **Complex reasoning** → Claude Opus (maximum capability)

**Best for:** Cost optimization, automatic best-AI selection

---

#### `/aid-router-status` (alias for `dev-aid-router-status`)
**View routing stats**

```bash
/aid-router-status
```

**Shows:**
- Current routing configuration
- Cost breakdown by model
- Recent routing decisions
- Budget status (under/over limit)

---

### 🤖 **Automation Commands**

#### `dev-aid-resolve-issue`
**Analyze and resolve GitHub issues with AI**

```bash
# Analyze issue and propose solution
dev-aid-resolve-issue --issue 123

# Preview without changes
dev-aid-resolve-issue --issue 123 --dry-run

# Use ensemble mode for accuracy
dev-aid-resolve-issue --issue 123 --mode ensemble
```

**Features:**
- Fetches issue from GitHub automatically
- Safety checks block security/critical issues
- Multiple orchestration modes
- Detailed solution proposals
- Time saved: 15-45 minutes per issue

[Quick Start Guide](.dev-aid/docs/ISSUE-RESOLVER-GUIDE.md)

---

#### `dev-aid-fix-conflicts`
**Resolve merge conflicts intelligently**

```bash
# Resolve conflicts in current branch
dev-aid-fix-conflicts

# Resolve conflicts in a PR
dev-aid-fix-conflicts --pr 67

# Use specific strategy
dev-aid-fix-conflicts --strategy smart

# Preview resolution
dev-aid-fix-conflicts --dry-run
```

**Strategies:**
- `smart` - Analyzes both sides, creates optimal merge (default)
- `ours` - Prefers current branch changes
- `theirs` - Prefers incoming branch changes

**Features:**
- Understands intent from both sides
- Preserves functionality
- Ensemble mode for accuracy
- Time saved: 10-30 minutes per conflict

[Quick Start Guide](.dev-aid/docs/CONFLICT-RESOLVER-GUIDE.md)

---

### 🤖 **Agent Slash Commands** (Interactive)

> Run any Dev-AID agent as a slash command. Each has a **full name** and a **short alias** (`aid-*`).
> Type `/aid-` in Claude Code or `aid-` in Gemini CLI for autocomplete.

| Short Alias | Full Command | What It Does |
|------------|-------------|-------------|
| `/aid-pr 135` | `/dev-aid-agent-pr-review` | Review PR for security, quality, architecture |
| `/aid-test src/` | `/dev-aid-agent-test-gen` | Generate tests for untested code |
| `/aid-debt src/ high` | `/dev-aid-agent-tech-debt` | Scan for tech debt and code smells |
| `/aid-ci 12345` | `/dev-aid-agent-ci-fix` | Diagnose and fix CI failures |
| `/aid-conflict 42` | `/dev-aid-agent-conflict-resolve` | Resolve merge conflicts intelligently |
| `/aid-research "topic"` | `/dev-aid-agent-research` | Deep research on technical topics |
| `/aid-onboard` | `/dev-aid-agent-onboard` | Generate codebase onboarding guide |
| `/aid-docs .` | `/dev-aid-agent-doc-audit` | Audit documentation for drift and gaps |
| `/aid-team <team> -m "..."` | `/dev-aid-agent-team` | Run multi-agent teams (PR review, security audit, etc.) |
| `/aid-help` | — | Show all Dev-AID commands |

**Supported in:** Claude Code, Gemini CLI, Cursor, Windsurf, Cline
**For CI/scripts:** Use the CLI instead — `dev-aid-agent pr-reviewer --pr 135 --json`

---

### 🛠️ **All Slash Commands**

> Every command has a short `aid-*` alias. Type `aid-` for autocomplete.

#### Security

| Alias | Full Command | What It Does |
|-------|-------------|-------------|
| `/aid-audit` | `dev-aid-audit` | Comprehensive security audit (Gitleaks + Trivy + Opengrep) |
| `/aid-vulnscan` | `dev-aid-vulnerability-scan` | Deep CVE scanning with auto-fix recommendations |

#### Quality & Analysis

| Alias | Full Command | What It Does |
|-------|-------------|-------------|
| `/aid-health` | `dev-aid-code-health` | Code health metrics, test coverage, maintainability |
| `/aid-debt-report` | `dev-aid-debt-analysis` | Tech debt analysis with severity scoring |
| `/aid-review` | `dev-aid-review-staged` | Pre-commit review of staged changes |
| `/aid-analyze` | `dev-aid-analyze` | Codebase analysis and structure mapping |

#### Productivity

| Alias | Full Command | What It Does |
|-------|-------------|-------------|
| `/aid-commit` | `dev-aid-commit-plan` | AI-guided atomic commit planning |
| `/aid-api` | `dev-aid-api-contract` | Generate OpenAPI specs, TypeScript clients, MSW mocks |

#### Setup & Configuration

| Alias | Full Command | What It Does |
|-------|-------------|-------------|
| `/aid-status` | `dev-aid-status` | Show Dev-AID configuration and component status |
| `/aid-config` | `dev-aid-config-core-skills` | Enable/disable core skills |
| `/aid-skill` | `dev-aid-build-skill` | Generate custom expert skills |

#### Operations & Maintenance

| Alias | Full Command | What It Does |
|-------|-------------|-------------|
| `/aid-deploy` | `dev-aid-deploy-validate` | Pre-deployment validation (deps, configs, security, tests) |
| `/aid-models` | `dev-aid-models-update` | Update AI model registry with latest releases |

#### Discovery

| Alias | What It Does |
|-------|-------------|
| `/aid-help` | Show all Dev-AID commands with descriptions |

---

### ✅ **Validation Commands** (Skill Compliance)

#### Validator Runner
**Run all skill compliance validators**

```bash
# Scan project with all relevant validators (auto-detected)
python3 .dev-aid/scripts/run-validators.py --filter-context --target-dir .

# Run specific validator only
python3 .dev-aid/skills/expert/bash-expert/validate.py --target-dir .
python3 .dev-aid/skills/expert/python/validate.py --target-dir .

# JSON output for CI pipelines
python3 .dev-aid/scripts/run-validators.py --json --strict --target-dir .
```

**Available validators:**
- **bash-expert** — 14 checks: shebang, strict mode, IFS, trap, syntax, eval/backticks, test brackets, variable braces, local vars, readonly, chmod, mktemp, curl pipe, unquoted subshell
- **python** — 8 AST checks: shell=True, eval/exec, pickle, hardcoded secrets, generic exceptions, print in libs, type annotations, test coverage

**Extensible:** Any skill can include a `validate.py` — auto-discovered by the runner, no registration needed.

📖 **Full guide:** [Validator Framework](.dev-aid/docs/VALIDATOR-FRAMEWORK.md)

---

## 🔧 Configuration

### Router Configuration

**File:** `.dev-aid/config/routing.json`

```json
{
  "default_mode": "solo",
  "modes": {
    "challenger": {
      "enabled": true,
      "primary_model": "claude-sonnet",
      "challenger_model": "gemini-flash",
      "auto_refine_on": ["HIGH", "CRITICAL"],
      "review_triggers": [
        "auth", "password", "crypto", "payment"
      ]
    },
    "ensemble": {
      "enabled": true,
      "routing_strategy": "semantic",
      "task_routes": {
        "massive_context": "gemini-flash",
        "code_generation": "claude-sonnet",
        "security_audit": "claude-sonnet"
      }
    }
  },
  "cost_limit_per_day": 100.0
}
```

### Model Registry

**File:** `.dev-aid/config/models.json`

```json
{
  "models": {
    "claude-sonnet": {
      "provider": "anthropic",
      "cost_per_mtok": {"input": 3.0, "output": 15.0},
      "strengths": ["code_generation", "security"]
    },
    "gemini-flash": {
      "provider": "google",
      "cost_per_mtok": {"input": 0.075, "output": 0.30},
      "max_context": 2000000,
      "strengths": ["massive_context", "cost_effective"]
    }
  }
}
```

---

## 🔍 RAG (Local Semantic Search)

### What is RAG?

**Retrieval-Augmented Generation** - AI finds relevant code in your codebase before answering.

**Traditional:** AI only knows what you tell it
**With RAG:** AI searches your codebase, finds examples, then answers

### Why Local RAG?

**Cloud RAG:**
- ❌ Costs $0.13/M tokens (OpenAI embeddings)
- ❌ Code sent to API (privacy concern)
- ❌ Requires internet

**Local RAG (Dev-AID Local Search):**
- ✅ $0 forever
- ✅ 100% private (code never leaves machine)
- ✅ Works offline
- ✅ Fast (0.15s queries)

### Setup RAG

```bash
# One command setup (5 minutes)
./.dev-aid/scripts/setup-rag.sh
```

**What it does:**
1. Installs Dev-AID Local Search (embedded semantic search engine)
2. Downloads EmbeddingGemma model (1.2GB)
3. Registers MCP server with Claude Code or Gemini CLI
4. Indexes your codebase
5. Creates helper scripts

### Using RAG

**Automatic (in Claude Code):**
```
You: "Find all password validation functions"
Claude: *automatically uses local RAG*
# Returns: src/auth/password.py:12, src/utils/validation.py:45
```

**Via Router:**
```bash
/aid-challenger-rag "Implement authentication"
# Uses RAG to find existing patterns, then generates
```

### RAG Maintenance

```bash
# Check status
./.dev-aid/scripts/rag-status.sh

# Reindex after changes
./.dev-aid/scripts/reindex-codebase.sh

# Auto-reindex on commits (optional)
# Git hook created during setup
```

### Supported Languages (RAG)

**AST-parsed (best results):**
- Python, JavaScript, TypeScript, Java, Go, Rust, C/C++, C#, Svelte

**Text-indexed (good results):**
- Markdown, JSON, TOML, YAML, XML

---

## 🏗️ Architecture

### Directory Structure

```
.dev-aid/
├── 📄 RAG-SETUP.md                    # RAG documentation
│
├── 📁 agents/                          # Autonomous agent framework
│   ├── core/                           # AgentRunner, ToolRegistry, SkillLoader, Safety
│   ├── adapters/                       # Anthropic, OpenAI, Google provider adapters
│   ├── agents/                         # 8 built-in agent definitions
│   └── tools/                          # 16 built-in tools (file, git, bash, search)
│
├── 📁 config/
│   ├── routing.json                   # Router configuration
│   ├── models.json                    # Model registry
│   ├── mcp-template.json              # MCP configuration
│   ├── orchestration.json             # Orchestration rules
│   └── settings.json                  # Global settings
│
├── 📁 providers/
│   ├── 📄 CLAUDE-CONTEXT-LOCAL.md     # Local RAG analysis
│   ├── 📄 CROSS-PLATFORM-ROUTER.md    # Router guide
│   ├── 📄 RAG-IMPLEMENTATION.md       # RAG overview
│   │
│   ├── claude/
│   │   └── .claude/
│   │       ├── commands/router/
│   │       │   ├── dev-aid-router-challenger.md
│   │       │   ├── dev-aid-router-challenger-rag.md
│   │       │   ├── dev-aid-router-ensemble.md
│   │       │   └── dev-aid-router-status.md
│   │       └── skills/expert/ (73 skills)
│   │
│   └── gemini/
│       └── .gemini/
│           └── commands/router/
│               ├── dev-aid-router-challenger.toml
│               ├── dev-aid-router-challenger-rag.toml
│               ├── dev-aid-router-ensemble.toml
│               └── dev-aid-router-status.toml
│
├── 📁 memory-bank/
│   ├── activeContext.md               # Current sprint (auto-loaded)
│   ├── patterns.md                    # Code patterns (on-demand)
│   ├── decisions.md                   # ADRs (on-demand)
│   ├── security.md                    # Security context (on-demand)
│   ├── testing.md                     # Testing standards (on-demand)
│   ├── performance.md                 # Performance guidelines (on-demand)
│   └── chaos.md                       # Error handling patterns (on-demand)
│
├── 📁 scripts/
│   ├── setup-dev-aid.sh                # Initialize Dev-AID (unified setup)
│   ├── init-repo.sh                   # (backward compat wrapper)
│   ├── setup-rag.sh                   # Setup local RAG
│   ├── reindex-codebase.sh            # Reindex for RAG
│   └── rag-status.sh                  # Check RAG status
│
└── 📁 automation/
    ├── pre-commit                     # Security hooks
    └── pre-push                       # Full audit
```

---

## 💰 Cost Analysis

### Without Dev-AID Router

```
# All requests go to Claude Sonnet
100 requests/month × 150k tokens × $3/M = $45/month
```

### With Dev-AID Router (Ensemble Mode)

```
# Smart routing
30 code requests → Claude Sonnet     = $13.50
50 large context → Gemini Flash      = $0.75
20 docs → GPT-4o                     = $7.50

Total: $21.75/month
Savings: $23.25/month (52% reduction)
```

### With RAG (Local Semantic Search)

```
# Traditional approach
100 requests × 150k tokens = 15M tokens
Embeddings (OpenAI): $1.95

# With Dev-AID Local Search
100 requests × 50k tokens = 5M tokens (67% reduction)
Embeddings: $0 (local)

Additional savings: $11.70/month
Total savings: $35/month (78% reduction)
```

### With Local LLM (Zero-Cost Mode) 🆕

```
# Cloud API approach
100 requests × 150k tokens × $3/M = $45/month

# With Local LLM (Ollama + Qwen2.5-Coder)
100 requests × 150k tokens = $0/month

Total savings: $45/month (100% reduction)

One-time cost: ~$800-1500 for GPU (RTX 4090)
ROI: 2-3 months if you use AI heavily
```

**When to use Local vs Cloud:**
| Scenario | Recommendation |
|----------|---------------|
| Sensitive/proprietary code | ✅ Local LLM |
| No internet access | ✅ Local LLM |
| Cost optimization | ✅ Local LLM |
| Maximum quality needed | Cloud (Claude/GPT) |
| No GPU available | Cloud (any provider) |
| Complex reasoning | Cloud (Claude Opus) |

---

## 🎓 Expert Skills (73 Skills)

### Core Skills
- **devsecops-expert** - Security-first development
- **tdd-expert** - Test-driven development
- **code-reviewer** - Code quality analysis
- **secret-scanner** - Credential detection

### Domain Experts (Sample)
- **api-expert** - REST API design
- **database-design** - Schema optimization
- **async-expert** - Async/await patterns
- **graphql-expert** - GraphQL best practices
- **fastapi-expert** - FastAPI patterns
- **rust** - Rust programming
- **typescript-expert** - TypeScript patterns
- **cicd-expert** - CI/CD pipelines
- **appsec-expert** - Application security
- **llm-integration** - LLM integration patterns

[See full list in `.dev-aid/providers/claude/.claude/skills/expert/`]

### Auto-Activation Rules

Skills auto-activate based on file patterns:

```json
{
  "devsecops-expert": ["*auth*", "*password*", "*token*", "*session*"],
  "database-design": ["*schema*", "*migration*", "*model*"],
  "api-expert": ["*api*", "*endpoint*", "*route*"]
}
```

**Example:**
```bash
# Edit src/auth/password.py
# → devsecops-expert auto-loads
# → security.md context added
# → OWASP guidelines active
```

---

## 🔒 Security Automation

### Git Hooks

**Pre-commit (~10s):**
- ✅ Secrets scan (Gitleaks)
- ✅ SAST - ERROR only (Opengrep)
- ✅ Critical CVEs (Trivy)

**Pre-push (~90s):**
- ✅ Full SAST — 10 universal + auto-detected language rulesets (Opengrep)
- ✅ Git history scan (Gitleaks)
- ✅ CVE + misconfig scan — HIGH + CRITICAL (Trivy)
- ✅ Shell SAST (ShellCheck) — auto-detected
- ✅ C/C++ SAST (Flawfinder) — auto-detected
- ✅ Swift SAST (mobsfscan) — auto-detected
- ✅ Python SAST (Bandit) + dependency audit (pip-audit) — auto-detected
- ✅ JS/TS dependency audit (npm audit) — auto-detected
- ✅ Rust dependency audit (cargo audit) — auto-detected
- ✅ Go vulnerability check (govulncheck) — auto-detected

### Security Tools

**Universal (always run):**

| Tool | Scan Type | Coverage |
|------|-----------|----------|
| **Gitleaks** | Secrets | Git history + current files |
| **Trivy** | CVE + Misconfig + Secrets | Dependencies, Dockerfiles, Terraform, K8s, GitHub Actions |
| **Opengrep** | SAST (10 universal + 12 language rulesets) | OWASP Top 10, CWE Top 25, CI/CD, command injection, insecure transport, JWT, TrailOfBits |

**Language-specific (auto-detected by file presence):**

| Tool | Language | Scan Type |
|------|----------|-----------|
| **ShellCheck** | Bash/Shell | Static analysis (SC warnings) |
| **Flawfinder** | C/C++ | CWE-mapped security audit |
| **mobsfscan** | Swift/iOS | OWASP MASVS/MSTG compliance |
| **Bandit** | Python | SAST (medium+ severity) |
| **pip-audit** | Python | Dependency vulnerability scan |
| **npm audit** | JS/TS | Dependency vulnerability scan |
| **cargo audit** | Rust | RustSec advisory database |
| **govulncheck** | Go | Official Go vulnerability check |

---

## 📖 Documentation

### Core Documentation
- **[COMMANDS-REFERENCE.md](.dev-aid/docs/COMMANDS-REFERENCE.md)** - Complete reference for all slash commands and aliases
- **[FAQ.md](.dev-aid/docs/FAQ.md)** - Frequently asked questions
- **[STORAGE-LOCATIONS.md](.dev-aid/docs/STORAGE-LOCATIONS.md)** - Where files are stored (5MB vs 2.7GB breakdown)
- **[DEPENDENCY-ISOLATION.md](.dev-aid/docs/DEPENDENCY-ISOLATION.md)** - Zero system pollution architecture
- **[HOW-LOCAL-SEARCH-WORKS.md](.dev-aid/docs/HOW-LOCAL-SEARCH-WORKS.md)** - How AI automatically uses local search via MCP
- **[MCP-EXTENSIBILITY.md](.dev-aid/docs/MCP-EXTENSIBILITY.md)** - Using Dev-AID with other MCP servers (GitHub, Slack, databases)
- **[UPDATING.md](.dev-aid/docs/UPDATING.md)** - How to update Dev-AID in existing repos
- **[CHANGELOG.md](.dev-aid/CHANGELOG.md)** - Version history and release notes

### Validation & Quality
- **[VALIDATOR-FRAMEWORK.md](.dev-aid/docs/VALIDATOR-FRAMEWORK.md)** - Skill compliance validator framework (creating validators, CLI, output formats)

### Agent Framework
- **[Dev-AID-AGENTS.md](.dev-aid/docs/Dev-AID-AGENTS.md)** - Agent framework guide (CLI vs slash commands, agents, teams, tools, local LLM support, safety, configuration)

### Automation Guides
- **[AUTOMATION-README.md](.dev-aid/docs/AUTOMATION-README.md)** - Complete automation overview and architecture
- **[ISSUE-RESOLVER-GUIDE.md](.dev-aid/docs/ISSUE-RESOLVER-GUIDE.md)** - Quick start guide for `dev-aid-resolve-issue`
- **[CONFLICT-RESOLVER-GUIDE.md](.dev-aid/docs/CONFLICT-RESOLVER-GUIDE.md)** - Quick start guide for `dev-aid-fix-conflicts`
- **[ISSUE-AUTOMATION-IMPLEMENTATION.md](.dev-aid/docs/ISSUE-AUTOMATION-IMPLEMENTATION.md)** - Technical implementation details
- **[ISSUE-AUTOMATION-PROPOSAL.md](.dev-aid/docs/ISSUE-AUTOMATION-PROPOSAL.md)** - Original feature design

### Setup Guides
- **[LOCAL-LLM-GUIDE.md](.dev-aid/docs/LOCAL-LLM-GUIDE.md)** - Complete local LLM setup guide (Ollama, LM Studio, llama.cpp)
- **[RAG-SETUP.md](.dev-aid/RAG-SETUP.md)** - Complete RAG setup guide
- **[ROUTER-INSTALL.md](.dev-aid/orchestration/ROUTER-INSTALL.md)** - Router installation with venv setup
- **[VENV-INFO.md](.dev-aid/orchestration/VENV-INFO.md)** - Virtual environment deep-dive
- **[BETA-TESTING-GUIDE.md](.dev-aid/docs/BETA-TESTING-GUIDE.md)** - Beta testing procedures and test matrix

### Technical Analysis
- **[CLAUDE-CONTEXT-LOCAL.md](.dev-aid/providers/CLAUDE-CONTEXT-LOCAL.md)** - Local RAG analysis
- **[CROSS-PLATFORM-ROUTER.md](.dev-aid/providers/CROSS-PLATFORM-ROUTER.md)** - Router implementation guide
- **[RAG-IMPLEMENTATION.md](.dev-aid/providers/RAG-IMPLEMENTATION.md)** - RAG options overview
- **[LIGHTRAG-AND-FORMATS.md](.dev-aid/providers/LIGHTRAG-AND-FORMATS.md)** - Format support comparison

### Legal & Community
- **[LICENSE](LICENSE)** - MIT License
- **[SECURITY.md](SECURITY.md)** - Vulnerability reporting policy
- **[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)** - Contributor Covenant v2.1
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines

### Provider Docs
- **[Claude Provider](.dev-aid/providers/claude/README.md)** — Primary provider: 53 slash commands, 5 hooks, Markdown format
- **[Gemini Provider](.dev-aid/providers/gemini/README.md)** — Gemini CLI: 31 slash commands, TOML format
- **[Local LLM Provider](.dev-aid/providers/local/README.md)** - Local model setup, agent compatibility, tool calling requirement, recommended models
- **[OpenAI Provider](.dev-aid/providers/openai/README.md)** - OpenAI integration, slash command gap explanation, workarounds
- **[Codex CLI Provider](.dev-aid/providers/codex/README.md)** - Codex CLI integration, skills loading, hook configuration
- **CLAUDE.md** - Claude Code context file (auto-generated by install script, gitignored)
- **GEMINI.md** - Gemini CLI context file (created when Gemini is enabled)
- **OPENAI.md** - OpenAI context file (created when OpenAI is enabled)
- **AGENTS.md** - Codex CLI context file (created when Codex is enabled)

---

## 🤝 Contributing

### 🚀 Quick Start for Contributors

**Before making changes, set up local PR checks (one-time setup):**

```bash
# Install pre-commit hooks (runs all CI checks automatically)
./.dev-aid/scripts/setup-git-hooks.sh

# Now every commit automatically checks:
# ✓ Black formatting ✓ Flake8 linting ✓ MyPy types ✓ Tests ✓ Coverage
```

**Or run checks manually before pushing:**
```bash
# Run all PR checks locally (same as CI)
./.dev-aid/scripts/run-pr-checks.sh

# Or use Makefile commands
cd .dev-aid/orchestration
make check      # Run all checks
make format     # Auto-fix formatting
make test       # Run tests
```

📖 **Full guide:** [Development Workflow](.dev-aid/docs/DEVELOPMENT-WORKFLOW.md)

### Adding New Skills

```bash
# Use built-in generator
/aid-skill "Create a [domain] expert skill"

# Or manually:
# 1. Create .dev-aid/providers/claude/.claude/skills/expert/your-skill/
# 2. Add skill.json with metadata
# 3. Add references/*.md with documentation
```

### Adding Router Commands

**Claude Code:** Add `.md` file to `.claude/commands/router/`
**Gemini CLI:** Add `.toml` file to `.gemini/commands/router/`

See existing commands as templates.

---

## 🐛 Troubleshooting

### RAG Issues

**"MCP tool 'code-search' not found"**
```bash
./.dev-aid/scripts/setup-rag.sh
```

**"No results found" or poor quality**
```bash
./.dev-aid/scripts/reindex-codebase.sh
```

**Check RAG status**
```bash
./.dev-aid/scripts/rag-status.sh
```

### Router Issues

**"Command not found"**
- Ensure you're in project root with `.dev-aid/` directory
- For Claude Code: Commands are in `.claude/commands/router/`
- For Gemini CLI: Commands are in `.gemini/commands/router/`

**Costs too high**
```bash
# Check routing config
cat .dev-aid/config/routing.json

# View current costs
/aid-router-status

# Adjust cost_limit_per_day
```

---

## 📝 License

MIT License. Copyright (c) 2025 Probably Nothing s.r.o. and Dev-AID Contributors. See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Dev-AID builds on excellent open-source projects and incorporates patterns from the AI development community:

### Inspiration & Structure
- **[claude-skills-generator](https://github.com/martinholovsky/claude-skills-generator)** by [Dev-AID Team (https://probably.group)](https://github.com/Probably-Group) - Project structure, configuration patterns, and AI integration architecture
- **[Superpowers](https://github.com/obra/superpowers)** by [Jesse Vincent](https://github.com/obra) - Inspiration for process skills architecture, TDD enforcement, and verification-gate patterns. Dev-AID's process skills adopt Superpowers' behavioral protocols while adding language-aware verification, multi-AI challenger mode, and FAISS local search integration
- **[claude-code-tresor](https://github.com/alirezarezvani/claude-code-tresor)** by [Alireza Rezvani](https://github.com/alirezarezvani) - Inspiration for security commands and DevSecOps patterns (integrated as skills)

### Core Technologies
- **[claude-context-local](https://github.com/FarhanAliRaza/claude-context-local)** by [FarhanAliRaza](https://github.com/FarhanAliRaza) - Inspiration and foundation for Dev-AID Local Search (embedded fork with enhancements)
- **[EmbeddingGemma](https://huggingface.co/google/embeddinggemma-300m)** by Google - State-of-the-art embedding model (300M parameters) for semantic code search
- **[FAISS](https://github.com/facebookresearch/faiss)** by Meta AI - High-performance vector search

### AI Platforms
- **[Claude Code](https://claude.ai/code)** by Anthropic - AI development environment
- **[Gemini CLI](https://ai.google.dev/)** by Google - Multi-model AI access
- **[Codex CLI](https://github.com/openai/codex)** by OpenAI - Terminal AI coding assistant
- **[Cursor](https://cursor.sh/)** - AI-powered code editor
- **[Windsurf](https://windsurf.com/)** - AI-powered code editor
- **[Cline](https://github.com/cline/cline)** - VS Code AI extension
- **[OpenRouter](https://openrouter.ai/)** - Unified AI API access

### Security Tools
- **[Opengrep (fork of Semgrep OSS)](https://www.opengrep.dev/)** - SAST with 10 universal + 12 auto-detected language rulesets
- **[Gitleaks](https://gitleaks.io/)** - Secrets detection in git history + current files
- **[Trivy](https://trivy.dev/)** - CVE, misconfig, and secrets scanning
