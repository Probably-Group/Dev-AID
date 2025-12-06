![Dev-AID Logo](./img/dev-aid-logo-small.png)

# 🚀 Dev-AID (Development AI Driver)

**Expert Skills, Multi-AI Routing, Local Semantic Search, and Persistent Context for AI-Assisted Development**

> The only AI development framework that works natively inside the tools you already use—no new CLIs to learn, no context switching, just enhanced capabilities where you code.

*Built for developers who want AI superpowers without the workflow disruption.*
---

## 🎯 What is Dev-AID?

**Dev-AID brings enterprise-grade AI capabilities directly into your existing development workflow.** Instead of forcing you to learn yet another CLI tool, Dev-AID integrates seamlessly with Claude Code, Cursor, Gemini CLI, and other AI assistants—enhancing them with 65 expert skills, multi-AI orchestration, 100% local semantic search, and automated security scanning.

### Why Native Integration Matters

**The Old Way:**
```
You: Working in VS Code
Also You: Switch to separate AI CLI
And You: Copy/paste context manually
Still You: Switch back to VS Code
😫 Repeat 50× per day
```

**The Dev-AID Way:**
```
You: Working in Claude Code (or Cursor, or Gemini CLI)
Dev-AID: *Already there, enhancing your AI with expert skills*
You: /dev-aid-router-challenger "Implement OAuth"
Dev-AID: *Claude generates, Gemini reviews, all in one place*
✨ Never left your editor
```

### How It Works

```
┌─────────────────────────────────────────────┐
│  Your Familiar Environment                  │
│  ✨ claude code        (no change needed)   │
│  ✨ cursor .           (no change needed)   │
│  ✨ gemini-cli         (no change needed)   │
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
│  • 65 expert skills (context-aware)         │
│  • Persistent memory (ADRs, patterns)       │
│  • Automated security (5 tools, git hooks)  │
│  • Specialized workflows (slash commands)   │
└─────────────────────────────────────────────┘

Real-World Examples:
• "Find authentication functions"
  → Local RAG searches instantly ($0, never leaves your machine)

• /dev-aid-router-challenger "Implement OAuth2"
  → Claude generates code, Gemini reviews security, all in one command

• Start coding session
  → Auto-loads relevant skills based on your tech stack (Python, React, Docker...)

• Edit src/auth/password.ts
  → devsecops-expert skill provides OWASP guidelines in context

• git commit
  → Automatic security scans (Gitleaks, Trivy, Opengrep) in ~10s

• /dev-aid-router-status
  → View AI routing decisions and costs across all sessions
```

---

## 🌟 Why Dev-AID's Native Integration is a Game-Changer

Most AI tools force you to learn a new CLI, switch contexts constantly, and manually manage multiple tools. Dev-AID takes a radically different approach: **enhance what you already use** instead of replacing it.

### 🎯 Benefits You'll Feel Immediately

| Traditional Standalone AI Tools | Dev-AID Native Integration |
|--------------------------------|----------------------------|
| 😫 Learn new CLI syntax | ✨ Use tools you already know |
| 😫 Switch between editor and AI tool | ✨ AI enhanced right where you code |
| 😫 Copy/paste context manually | ✨ Auto-loaded from memory bank |
| 😫 One AI, take it or leave it | ✨ Multi-AI routing to best model |
| 😫 Cloud RAG costs $$$ | ✨ 100% local RAG, $0 forever |
| 😫 Manual security checks | ✨ Automated git hooks |
| 😫 Reinvent the wheel for each tool | ✨ One config, works everywhere |

### 💡 Real Developer Benefits

**For Individual Developers:**
- ✅ **Zero context switching** - Work in Claude Code/Cursor/Gemini, get all features
- ✅ **Instant setup** - 5 minutes from clone to productive
- ✅ **Your workflow, enhanced** - Not disrupted or replaced
- ✅ **Learn once, use anywhere** - Same skills work across AI tools

**For Teams:**
- ✅ **Consistent standards** - Same expert skills across all devs
- ✅ **Portable configuration** - One `.dev-aid/` folder, entire team benefits
- ✅ **Tool flexibility** - Devs choose their AI tool, get same capabilities
- ✅ **Zero vendor lock-in** - Works with Anthropic, Google, OpenAI, and future tools

**For Security/Compliance:**
- ✅ **100% local RAG** - Code never leaves your machine
- ✅ **Isolated dependencies** - Virtual environments, zero system pollution
- ✅ **Automated scanning** - 5 security tools in git hooks
- ✅ **Audit trail** - All AI routing decisions logged with costs

### 🚀 The Philosophy

> **"The best tool is the one that disappears into your workflow."**

Dev-AID doesn't demand your attention or force you to adapt. It quietly enhances your existing AI tools with enterprise capabilities, then gets out of your way. You use Claude Code or Gemini CLI just like before—except now they're 10× more powerful.

---

## ✨ Key Features

### 🔍 **Dev-AID Local Search** (NEW!)
- **100% local** - Code never leaves your machine
- **$0 forever** - No API costs for embeddings
- **EmbeddingGemma model** - Google's state-of-the-art embeddings
- **Fast** - 0.15s queries with FAISS vector search
- **Smart** - AST parsing for 9+ languages
- **MCP native** - Works with Claude Code, Gemini CLI & Cursor
- **Powered by** - claude-context-local by [FarhanAliRaza](https://github.com/FarhanAliRaza/claude-context-local)

### 🔀 **Multi-AI Router** (NEW!)
- **Challenger mode** - Claude generates, Gemini reviews
- **Ensemble mode** - Route to best AI for each task
- **Cost optimization** - Gemini for large context (97% cheaper)
- **Configuration-driven** - JSON-based routing rules
- **Slash commands** - `/dev-aid-router-challenger`, `/dev-aid-router-ensemble`

### 🎓 **65 Expert Skills** (🆕 Hook-Based Auto-Loading)
- **Intelligent auto-loading** - Detects project context (tech stack, files) at session start
- **Scoring algorithm** - Ranks skills by relevance (keywords, technologies, file patterns)
- **Zero configuration** - Works automatically for Claude Code and Gemini CLI
- **Universal architecture** - Same auto-loading logic across all AI providers
- **Manual activation** - Still available via skill name when needed
- **Custom skills** - Generate new skills with `/dev-aid-build-skill`
- **Domains**: DevSecOps, TDD, API design, databases, etc. [full list](/.dev-aid/providers/claude/.claude/skills/expert)

### 💾 **Persistent Memory Bank**
- Context survives across sessions
- Architecture decisions (ADRs)
- Code patterns & anti-patterns
- Security guidelines

### 🔒 **Automated Security**
- **Pre-commit hooks**: Secrets scan, SAST, Critical CVEs (~10s)
- **Pre-push hooks**: Full SAST, git history scan (~60s)
- **5 Security tools**: Opengrep, Gitleaks, Trivy, Hadolint, Checkov
- **Isolated dependencies**: Virtual environments, zero system pollution ([details](./.dev-aid/docs/DEPENDENCY-ISOLATION.md))

### ⚙️ **Works Everywhere You Do**
- **Native integration** with Claude Code, Cursor, Gemini CLI
- **Multi-provider routing** - Use the best AI for each task
- **Consistent experience** - Same capabilities regardless of tool
- **Future-proof** - Works with any AI tool that reads config files

---

## 🆕 What's New in v1.2.0 (2025-12-06)

### Performance & Architecture
- **⚡ 10x Faster Context Detection**: Optimized from 2s+ to <200ms with new Python implementation
- **🎯 Dynamic Skill Loading**: Patterns now loaded from skills-index.json (no hardcoded lists)
- **📦 Code Reduction**: 84% reduction in orchestration scripts (367 → 59 lines)

### Security Enhancements
- **🔒 Pinned Dependencies**: All 63 Python packages now use exact versions for reproducible builds
- **🛡️ Active Security Scanning**: GitHub Actions now running automated scans on all commits/PRs
- **🔐 CVE Patched**: Updated h11 to fix critical HTTP request smuggling vulnerability
- **✅ Fail-Closed Hooks**: Pre-commit now blocks when security tools missing (no more silent bypasses)
- **🔑 Checksum Verification**: RAG installer now verifies SHA256 before execution

### New Features
- **🤖 Auto-Generate CI/CD Workflows**: Production-ready GitHub Actions from project detection
  - Supports Node.js, Python, Rust, Go with auto-detection
  - Security by default: Gitleaks + Trivy included
  - Detects package managers: npm/yarn/pnpm/bun, pip/poetry/uv, cargo, go
  - Usage: `.dev-aid/scripts/generate-ci.sh`

- **🔧 Refactoring Expert Skill**: 522-line comprehensive guide for safe code refactoring
  - Safety-first methodology with mandatory testing
  - Strangler Fig pattern for legacy modernization
  - Auto-activates on keywords: refactor, rewrite, legacy, technical debt

- **📚 RAG Vendoring Support**: Documentation and tooling for dependency stability
  - Fork and maintain your own copy
  - Environment variable support for custom repositories

- **🧪 VCR/Replay Testing**: Cost-free AI client testing with recorded HTTP interactions
  - Record once with real API keys, replay forever in CI
  - Automatic API key sanitization
  - Fast, deterministic, $0 cost testing

- **✅ PR Check Workflow**: Fast feedback loop for pull requests
  - Path-based filtering (runs only on relevant changes)
  - Python/Bash linting, type checking, unit tests
  - Saves GitHub Actions minutes

- **🚀 Release Gate Workflow**: Deep validation before releases
  - Cross-platform tests (Ubuntu, MacOS, Windows)
  - Comprehensive security scans
  - Documentation link validation

### Code Quality
- **♻️ DRY Improvements**: Eliminated 158 lines of duplicate code in API clients
- **🎨 Decorator Pattern**: New `@track_api_call` for centralized error handling and timing
- **📋 Dynamic Package Testing**: Setup script now parses requirements.txt automatically

**See full changelog:** [CHANGELOG.md](./.dev-aid/CHANGELOG.md)

**Issues resolved:** #17-24, #26-28, #31-36

---

## 🚀 Quick Start

### Option 1: New Project with Dev-AID

```bash
# Clone Dev-AID repository
git clone <repo> my-project
cd my-project

# Copy Dev-AID configuration
cp -r devaid-standalone/.dev-aid .

# Initialize (with optional Local Search)
./.dev-aid/scripts/init-repo.sh
# Answer "Y" to install Dev-AID Local Search

# Done! Start using
claude
# or
gemini
```

### Option 2: Add to Existing Project

```bash
# Copy Dev-AID to your project
cd ~/my-existing-project
cp -r /path/to/devaid-standalone/.dev-aid .

# Initialize
./.dev-aid/scripts/init-repo.sh

# Done!
```

### Option 3: Just Add Local Search to Existing Dev-AID

```bash
# If you already have Dev-AID
cd your-project

# Add Dev-AID Local Search
./.dev-aid/scripts/setup-rag.sh

# 5 minutes later: Local Search ready!
```

---

## 📚 Available Slash Commands

### 🔍 **RAG Commands** (Local Semantic Search)

**In Claude Code or Gemini CLI:**

```bash
# Find code with natural language
You: "Find all authentication functions"
AI: *uses local RAG, returns relevant code*

# Or via router with RAG
/dev-aid-router-challenger-rag "Implement password reset"
```

**What happens:**
1. Searches codebase semantically (local, $0 cost)
2. Finds similar implementations & patterns
3. Claude generates using YOUR codebase style
4. Gemini reviews for security issues

> 💡 **How does the AI know to use local search?** See [How Local Search Works](.dev-aid/docs/HOW-LOCAL-SEARCH-WORKS.md) for the complete explanation of MCP integration and automatic tool selection.

### 🔀 **Router Commands** (Multi-AI Orchestration)

#### `/dev-aid-router-challenger`
**Two-AI review workflow**

```bash
/dev-aid-router-challenger "Implement OAuth2 authentication"
```

**Process:**
1. Claude generates implementation
2. Gemini reviews for security issues
3. Claude refines based on feedback
4. You see both perspectives

**Best for:** Security-critical features, auth, payments, encryption

---

#### `/dev-aid-router-challenger-rag`
**Challenger mode + Local RAG**

```bash
/dev-aid-router-challenger-rag "Add password validation"
```

**Process:**
1. **Local search** finds existing patterns (0.15s, $0)
2. Claude generates using your patterns
3. Gemini reviews with same context
4. Result: Code matching your style + security review

**Best for:** When you have similar code and want consistency

---

#### `/dev-aid-router-ensemble`
**Smart routing to optimal AI**

```bash
/dev-aid-router-ensemble "Analyze entire codebase for security issues"
```

**Routing logic:**
- **Massive context** (100k+ tokens) → Gemini Flash (1M context, 97% cheaper)
- **Code generation** → Claude Sonnet (best coder)
- **Security audit** → Claude Sonnet (security expert)
- **Documentation** → GPT-4o (clear writing)
- **Complex reasoning** → Claude Opus (maximum capability)

**Best for:** Cost optimization, automatic best-AI selection

---

#### `/dev-aid-router-status`
**View routing stats**

```bash
/dev-aid-router-status
```

**Shows:**
- Current routing configuration
- Cost breakdown by model
- Recent routing decisions
- Budget status (under/over limit)

---

### 🛠️ **Development Commands**

#### `/dev-aid-audit`
Security audit with 5 tools

```bash
/dev-aid-audit
```

Runs: Opengrep, Gitleaks, Trivy, Hadolint, Checkov

---

#### `/dev-aid-build-skill`
Generate custom expert skill

```bash
/dev-aid-build-skill "Create a Kubernetes expert skill"
```

Generates skill with references, activation rules, and context.

---

#### `/dev-aid-deploy-validate`
Pre-deployment validation

```bash
/dev-aid-deploy-validate production
```

Validates: Dependencies, configs, security, tests

---

#### `/dev-aid-test-suite`
Run comprehensive test suite

```bash
/dev-aid-test-suite
```

Runs all tests with coverage

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

**Local RAG (claude-context-local):**
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
1. Installs claude-context-local
2. Downloads EmbeddingGemma model (1.2GB)
3. Registers MCP with Claude Code or Gemini CLI
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
/dev-aid-router-challenger-rag "Implement authentication"
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
│   │       └── skills/expert/ (65 skills)
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
│   ├── activeContext.md               # Current sprint
│   ├── patterns.md                    # Code patterns
│   ├── decisions.md                   # ADRs
│   └── security.md                    # Security context
│
├── 📁 scripts/
│   ├── init-repo.sh                   # Initialize Dev-AID
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

# With claude-context-local
100 requests × 50k tokens = 5M tokens (67% reduction)
Embeddings: $0 (local)

Additional savings: $11.70/month
Total savings: $35/month (78% reduction)
```

---

## 🎓 Expert Skills (65 Skills)

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

**Pre-push (~60s):**
- ✅ Full SAST (Opengrep)
- ✅ Git history scan (Gitleaks)
- ✅ Dependency audit (Trivy)
- ✅ Container scan (Trivy + Hadolint)
- ✅ IaC scan (Checkov)

### Security Tools

1. **Opengrep** - SAST (OWASP Top 10)
2. **Gitleaks** - Secrets detection
3. **Trivy** - Vulnerability scanning
4. **Hadolint** - Dockerfile linting
5. **Checkov** - IaC security

---

## 🆚 Comparison

### vs Standalone AI CLIs

| Aspect | Standalone AI Tools | Dev-AID Enhancement Layer |
|--------|-------------------|---------------------------|
| **Integration** | Separate CLI to learn | Works in your existing tools ✨ |
| **Context switching** | Constant (editor ↔ CLI) | Zero - stay in your editor ✨ |
| **Setup complexity** | New tool + config | 5-minute one-time setup ✨ |
| **Workflow disruption** | High (new habits) | None (enhances current flow) ✨ |
| **Multi-AI support** | One tool = one AI | Route to best AI per task ✨ |
| **Portability** | Tool-specific | Works across Claude/Gemini/Cursor ✨ |

### vs Manual Configuration

| Feature | Manual | Dev-AID |
|---------|--------|---------|
| Expert skills | Write yourself | 65 pre-built ✅ |
| Security scans | Remember to run | Automated (git hooks) ✅ |
| Memory bank | Manual notes | Persistent, auto-loaded ✅ |
| Multi-AI routing | Manual switching | Automatic routing ✅ |
| Local RAG | Complex setup | One command ✅ |
| Slash commands | Create each one | All included ✅ |
| Dependency isolation | Manual venv setup | Automated with setup script ✅ |
| Time to setup | Days | 5 minutes ✅ |

### vs Cloud RAG

| Feature | Cloud RAG | Dev-AID Local Search |
|---------|-----------|-------------------|
| Cost | $0.13/M tokens | $0 forever |
| Privacy | Code sent to API | 100% local |
| Speed | 0.3-0.5s + network | 0.15s (local) |
| Offline | ❌ No | ✅ Yes |
| Setup | API keys, config | One command |

---

## 📖 Documentation

### Core Documentation
- **[STORAGE-LOCATIONS.md](.dev-aid/docs/STORAGE-LOCATIONS.md)** - Where files are stored (5MB vs 2.7GB breakdown)
- **[DEPENDENCY-ISOLATION.md](.dev-aid/docs/DEPENDENCY-ISOLATION.md)** - Zero system pollution architecture
- **[HOW-LOCAL-SEARCH-WORKS.md](.dev-aid/docs/HOW-LOCAL-SEARCH-WORKS.md)** - How AI automatically uses local search via MCP
- **[MCP-EXTENSIBILITY.md](.dev-aid/docs/MCP-EXTENSIBILITY.md)** - Using Dev-AID with other MCP servers (GitHub, Slack, databases)
- **[UPDATING.md](.dev-aid/docs/UPDATING.md)** - How to update Dev-AID in existing repos
- **[CHANGELOG.md](.dev-aid/CHANGELOG.md)** - Version history and release notes

### Setup Guides
- **RAG-SETUP.md** - Complete RAG setup guide
- **ROUTER-INSTALL.md** - Router installation with venv setup
- **VENV-INFO.md** - Virtual environment deep-dive

### Technical Analysis
- **CLAUDE-CONTEXT-LOCAL.md** - Local RAG analysis
- **CROSS-PLATFORM-ROUTER.md** - Router implementation guide
- **RAG-IMPLEMENTATION.md** - RAG options overview
- **LIGHTRAG-AND-FORMATS.md** - Format support comparison

### Provider Docs
- **providers/claude/CLAUDE.md** - Claude Code setup
- **providers/gemini/GEMINI.md** - Gemini CLI setup
- **providers/openai/OPENAI.md** - OpenAI integration

---

## 🤝 Contributing

### Adding New Skills

```bash
# Use built-in generator
/dev-aid-build-skill "Create a [domain] expert skill"

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
/dev-aid-router-status

# Adjust cost_limit_per_day
```

---

## 📝 License

[Your license here]

---

## 🙏 Acknowledgments

Dev-AID builds on excellent open-source projects and incorporates patterns from the AI development community:

### Inspiration & Structure
- **[claude-skills-generator](https://github.com/martinholovsky/claude-skills-generator)** by [Martin Holovsky - Dev-AID author](https://github.com/martinholovsky) - Project structure, configuration patterns, and AI integration architecture
- **[claude-code-tresor](https://github.com/alirezarezvani/claude-code-tresor)** by [Alireza Rezvani](https://github.com/alirezarezvani) - Inspiration for security commands and DevSecOps patterns (integrated as skills)

### Core Technologies
- **[claude-context-local](https://github.com/FarhanAliRaza/claude-context-local)** by [FarhanAliRaza](https://github.com/FarhanAliRaza) - Powers Dev-AID Local Search with 100% local semantic code search using EmbeddingGemma
- **[EmbeddingGemma](https://huggingface.co/google/gemma-2b-it)** by Google - State-of-the-art embedding model for semantic search
- **[FAISS](https://github.com/facebookresearch/faiss)** by Meta AI - High-performance vector search

### AI Platforms
- **[Claude Code](https://claude.ai/code)** by Anthropic - AI development environment
- **[Gemini CLI](https://ai.google.dev/)** by Google - Multi-model AI access
- **[Cursor](https://cursor.sh/)** - AI-powered code editor
- **[OpenRouter](https://openrouter.ai/)** - Unified AI API access

### Security Tools
- **[Opengrep (fork of Semgrep OSS)](https://www.opengrep.dev/)** - SAST for OWASP Top 10
- **[Gitleaks](https://gitleaks.io/)** - Secrets detection
- **[Trivy](https://trivy.dev/)** - Vulnerability scanning
- **[Hadolint](https://hadolint.github.io/hadolint/)** - Dockerfile linting
- **[Checkov](https://www.checkov.io/)** - IaC security

---

## 🔗 Links

- **Documentation:** `.dev-aid/` directory
- **Issues:** [GitHub Issues]
- **Discussions:** [GitHub Discussions]

---

**Dev-AID: Enterprise-grade AI capabilities that integrate natively into the tools you already love. No context switching. No new CLIs. Just smarter development, right where you code.**

---

*Built for developers who want AI superpowers without the workflow disruption.*
