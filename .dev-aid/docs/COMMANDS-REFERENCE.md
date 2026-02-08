# Dev-AID Slash Commands Reference

Complete guide to all available slash commands in Dev-AID.

---

## 📋 Built-in Commands

### Setup & Analysis

#### `/dev-aid-analyze`
**Category:** Setup
**Purpose:** Analyze codebase and generate adaptation plan
**When to use:** After installation, when adding Dev-AID to existing project
**Output:**
- `.dev-aid/analysis/adaptation-plan.md`
- `.dev-aid/analysis/quick-start-checklist.md`

**Example:**
```
/dev-aid-analyze
```

#### `/dev-aid-status`
**Category:** Setup
**Purpose:** Show current Dev-AID configuration and setup status
**When to use:** After installation, troubleshooting, regular checkups
**Output:** Console display of configuration, providers, context files, memory bank status

**Example:**
```
/dev-aid-status
```

#### `/dev-aid-config-core-skills` (NEW!)
**Category:** Setup
**Purpose:** Configure which core skills are auto-loaded at session start
**When to use:** Initial setup, changing automated checking preferences
**Output:** Updated `.dev-aid/config/core-skills.json`

Core skills provide **automated tool execution** on file save:
- `code-reviewer` - Real-time code quality suggestions (✅ enabled by default)
- `secret-scanner` - Prevent credential leaks (✅ enabled by default)
- `test-runner` - Auto-run tests on save (⏸️ disabled by default)
- `linter` - Auto-lint code (⏸️ disabled by default)
- `type-checker` - Auto-check types (⏸️ disabled by default)

**Profiles:**
- **minimal** (default): code-reviewer + secret-scanner = 500 tokens
- **ide-user**: Same as minimal (for devs with IDE extensions)
- **no-ide-setup**: All 5 enabled = 1,250 tokens (for command-line devs)
- **ci-cd**: secret-scanner only = 250 tokens

**Example:**
```
/dev-aid-config-core-skills
```

**Value:** Configurable real-time feedback saves 5-15 min/day per developer

#### `/generate-ci` (Script)
**Category:** Automation
**Purpose:** Auto-generate production-ready CI/CD workflows
**When to use:** Setting up CI/CD, migrating projects, adding automation
**Output:** `.github/workflows/ci.yml`
**Supported:** Python, Node.js, Java, Go, Rust, C#, PHP, Ruby, C++

**Example:**
```bash
# Auto-detect and generate
./.dev-aid/scripts/generate-ci.sh

# Generate with optimizations (recommended)
./.dev-aid/scripts/generate-ci.sh --optimize

# Custom output location
./.dev-aid/scripts/generate-ci.sh -o .github/workflows/custom.yml
```

**Documentation:** See [CI-GENERATOR-GUIDE.md](./CI-GENERATOR-GUIDE.md)

---

## 🤖 Autonomous Agents (NEW!)

### `dev-aid-agent` (CLI Tool)
**Category:** Automation
**Purpose:** Run autonomous AI agents powered by Dev-AID's expert skills
**When to use:** Automated PR reviews, test generation, tech debt scanning, CI debugging, conflict resolution, research, onboarding
**Location:** `.dev-aid/scripts/dev-aid-agent`

**Agents:**
- `pr-reviewer` — Review PRs for security, quality, best practices
- `test-generator` — Generate tests for untested code
- `tech-debt-hunter` — Scan for code smells and technical debt
- `ci-fixer` — Diagnose CI failures and propose fixes
- `conflict-resolver` — Auto-resolve merge conflicts
- `research` — Deep research on technical topics
- `onboarding` — Generate codebase onboarding guide

**Global Options:**
- `--provider <name>` — Override provider (anthropic, google, openai, local)
- `--model <name>` — Override model
- `--dry-run` — Show actions without making changes
- `--verbose` — Show tool call details
- `--json` — JSON output for scripts/CI
- `--max-iterations <n>` — Override max iterations

**Commands:**
```bash
# PR review
dev-aid-agent pr-reviewer --pr 135

# Generate tests
dev-aid-agent test-generator --path src/auth/ --framework pytest

# Tech debt scan
dev-aid-agent tech-debt-hunter --severity high

# CI debugging
dev-aid-agent ci-fixer --run-id 12345

# Conflict resolution
dev-aid-agent conflict-resolver --pr 67 --strategy smart

# Research
dev-aid-agent research --topic "async patterns" --depth deep

# Onboarding guide
dev-aid-agent onboarding

# Use different provider
dev-aid-agent research --topic "migration" --provider google

# JSON output for CI
dev-aid-agent tech-debt-hunter --severity critical --json

# Dry run (read-only, no changes)
dev-aid-agent test-generator --path src/ --dry-run
```

**Features:**
- 16 built-in tools (file, git, GitHub, bash, search) with safety enforcement
- Loads Dev-AID expert skills as system prompts (72+ available)
- Provider-agnostic: Anthropic, OpenAI, Google, Local (Ollama/LM Studio)
- Command blocklist prevents dangerous bash operations
- Per-tool risk levels (safe/moderate/dangerous)
- Exit code 0 on success, 1 on failure

**Documentation:** [Agent Framework Guide](Dev-AID-AGENTS.md)

### Agent Slash Commands (Native)

Each agent is also available as a **native slash command** for interactive use in Claude Code, Gemini CLI, Cursor, Windsurf, and Cline. Slash commands load directly in the AI session — no separate CLI process needed.

Each command has a **full name** and a **short alias** (prefix `aid-`):

| Full Command | Short Alias | Description | Example |
|-------------|------------|-------------|---------|
| `dev-aid-agent-pr-review` | `aid-pr` | Review PR for security, quality, architecture | `/agents:aid-pr 135` |
| `dev-aid-agent-test-gen` | `aid-test` | Generate tests for untested code | `/agents:aid-test src/auth/` |
| `dev-aid-agent-tech-debt` | `aid-debt` | Scan for code smells and tech debt | `/agents:aid-debt src/ high` |
| `dev-aid-agent-ci-fix` | `aid-ci` | Diagnose and fix CI failures | `/agents:aid-ci 12345` |
| `dev-aid-agent-conflict-resolve` | `aid-conflict` | Resolve merge conflicts intelligently | `/agents:aid-conflict 42 smart` |
| `dev-aid-agent-research` | `aid-research` | Deep research on technical topics | `/agents:aid-research "async patterns"` |
| `dev-aid-agent-onboard` | `aid-onboard` | Generate codebase onboarding guide | `/agents:aid-onboard` |
| `dev-aid-agent-doc-audit` | `aid-docs` | Audit documentation for drift and gaps | `/agents:aid-docs . docs-only` |
| — | `aid-help` | Show all Dev-AID commands | `/agents:aid-help` |

**When to use slash commands vs CLI:**
- **Slash commands** — Interactive sessions in Claude Code, Gemini CLI, Cursor, Windsurf, Cline. Type `/agents:aid-` for autocomplete.
- **CLI (`dev-aid-agent`)** — Scripts, CI/CD pipelines, automation. Supports `--json`, `--dry-run`, `--provider` flags.

**Supported editors/tools:**
- **Native slash commands**: Claude Code, Gemini CLI, Cursor, Windsurf, Cline
- **MCP integration only**: VS Code Copilot Chat, Zed, JetBrains AI Assistant

---

## 🚀 Productivity Tools (NEW!)

### `/dev-aid-api-contract`
**Category:** Productivity
**Purpose:** Generate OpenAPI specs, TypeScript clients, and MSW mocks from data models
**When to use:** Starting new API development, unblocking frontend
**Output:** OpenAPI spec, TypeScript client, MSW mocks, tests, validation middleware

**What it generates:**
- `api/user-api.yaml` - OpenAPI 3.1 specification
- `src/api/user-client.ts` - Type-safe API client (openapi-fetch)
- `src/mocks/user.mocks.ts` - MSW mock handlers
- `src/api/__tests__/user-api.test.ts` - Contract tests
- `src/middleware/user-validator.ts` - Request validation (Zod)

**Example:**
```bash
# From TypeScript interface
/dev-aid-api-contract --from src/models/user.ts --name UserAPI

# From Zod schema
/dev-aid-api-contract --from src/schemas/user-schema.ts --name UserAPI

# Infer from existing controller
/dev-aid-api-contract --infer src/controllers/user-controller.ts
```

**Value:** Unblocks frontend immediately (2-4 weeks saved), $675,000/year for 100 devs

### `/dev-aid-commit-plan`
**Category:** Productivity
**Purpose:** Analyze unstaged changes and propose atomic commits
**When to use:** After coding session, before committing
**Output:** Interactive commit plan with groupings and suggested messages

**What it does:**
1. Analyzes all unstaged changes
2. Groups files by logical changes (feat, fix, refactor, docs)
3. Proposes atomic commits with conventional commit messages
4. Shows dependency order and conflicts
5. Interactive approval/edit before execution

**Example:**
```bash
# Generate commit plan
/dev-aid-commit-plan

# Output shows:
# 1. feat: Add user authentication (8 files)
# 2. fix: Resolve null pointer in profile (2 files)
# 3. refactor: Extract validation utils (3 files)
# 4. docs: Update API documentation (1 file)
#
# Actions: [A]pprove & execute | [E]dit plan | [P]review | [C]ancel
```

**Value:** Prevents mega-commits, teaches good habits, $425,000/year for 100 devs

### `/dev-aid-review-staged`
**Category:** Quality
**Purpose:** Comprehensive pre-commit review (Rubber Duck Pre-Reviewer)
**When to use:** Before committing, as pre-commit hook
**Output:** Security, performance, test, and code quality issues

**Focus modes:**
```bash
# Comprehensive review
/dev-aid-review-staged

# Security-only review
/dev-aid-review-staged --focus security

# Test coverage review
/dev-aid-review-staged --focus tests

# Performance review
/dev-aid-review-staged --focus performance

# Code style review
/dev-aid-review-staged --focus style
```

**What it catches:**
- 🔴 Blockers: Hardcoded secrets, SQL injection, security vulnerabilities
- 🟡 Warnings: Missing tests, debug code, performance anti-patterns
- 🔵 Suggestions: Code smells, naming issues, complexity

**Value:** Catches issues early, $1,050,000/year for 100 devs (prevented rework)

### `dev-aid-research` (CLI Tool)
**Category:** Research & Knowledge
**Purpose:** Multi-provider deep research with smart routing and caching
**When to use:** External research, fact-checking, exploring new technologies
**Output:** Research results with sources and citations

**Providers:**
- **Tavily**: Fast factual queries (free tier: 1000 credits/month)
- **Perplexity Sonar**: Balanced depth and speed
- **Gemini Deep Research**: Complex exploratory research

**Commands:**
```bash
# Auto-route to best provider
dev-aid-research search "Compare React vs Vue 2026"

# Quick factual lookup (Tavily)
dev-aid-research quick "Latest Node.js LTS version"

# Deep exploratory research (Gemini)
dev-aid-research deep "Kubernetes security best practices"

# Force specific provider
dev-aid-research search "topic" --provider perplexity-sonar

# Skip cache for fresh results
dev-aid-research search "topic" --no-cache
```

**Features:**
- Smart query classification (factual/exploratory/technical)
- Semantic caching with 70% similarity threshold (24-48h TTL)
- MCP server integration for Claude Code/Gemini CLI
- Auto-fallback when local context insufficient

**Environment Variables:**
```bash
TAVILY_API_KEY=...       # Free tier available
PERPLEXITY_API_KEY=...   # Token-based pricing
GOOGLE_API_KEY=...       # For Gemini Deep Research
```

**Value:** Access to real-time information, reduces AI hallucinations, improves research accuracy

---

## 🎯 Quality & Security Analysis Commands (Included!)

**These commands are already included in Dev-AID** (adapted from claude-code-tresor):

### Security Commands

#### `/dev-aid-audit`
**Purpose:** Comprehensive security audit
**Status:** ✅ Included
**Phases:** 3-4 phases with multiple agents
**Coverage:** Code, dependencies, configuration, secrets
**Location:** `.dev-aid/providers/claude/.claude/commands/security/dev-aid-audit.md`
**Value:** Prevents security breaches ($500K avg cost)

#### `/dev-aid-vulnerability-scan`
**Purpose:** Deep CVE scanning for dependencies
**Status:** ✅ Included
**Features:**
- CVE database correlation
- Severity scoring and prioritization
- Auto-fix recommendations
**Location:** `.dev-aid/providers/claude/.claude/commands/security/dev-aid-vulnerability-scan.md`
**Value:** Saves 1-2 hrs/CVE, prevents incidents ($250K avg)

### Quality Commands

#### `/dev-aid-code-health`
**Purpose:** Comprehensive code quality assessment
**Status:** ✅ Included
**Metrics:**
- Code quality metrics
- Test coverage analysis
- Documentation assessment
- Maintainability scoring
**Location:** `.dev-aid/providers/claude/.claude/commands/quality/dev-aid-code-health.md`
**Value:** Early tech debt detection, prevents $100K/year accumulation

#### `/dev-aid-debt-analysis`
**Purpose:** Technical debt identification and prioritization
**Status:** ✅ Included
**Features:**
- Debt quantification (time wasted)
- Risk assessment
- Effort estimation
- Refactoring roadmap
**Location:** `.dev-aid/providers/claude/.claude/commands/quality/dev-aid-debt-analysis.md`
**Value:** Saves 2-4 hrs/quarter in manual analysis

### Validation Commands (Skill Compliance)

#### `run-validators.py` (Script)
**Purpose:** Auto-discover and run all skill compliance validators
**Status:** ✅ Included
**Location:** `.dev-aid/scripts/run-validators.py`

**Usage:**
```bash
# Run all validators matching project technologies
python3 .dev-aid/scripts/run-validators.py --filter-context --target-dir .

# Run all validators (no filtering)
python3 .dev-aid/scripts/run-validators.py --target-dir .

# JSON output for CI
python3 .dev-aid/scripts/run-validators.py --json --strict --target-dir .

# Run specific validators only
python3 .dev-aid/scripts/run-validators.py --validators bash-expert,python --target-dir .
```

**Flags:**
- `--strict` — Treat WARN as FAIL
- `--json` — Machine-readable JSON output
- `--filter-context` — Only run validators matching detected project technologies
- `--validators name,...` — Run only named validators
- `--target-dir` — Directory to scan (default: `.`)

**Exit codes:** 0 = pass, 1 = failures found, 2 = runner error

#### Bash Expert Validator
**Purpose:** Validate bash scripts against bash-expert skill standards (14 checks)
**Location:** `.dev-aid/skills/expert/bash-expert/validate.py`

```bash
python3 .dev-aid/skills/expert/bash-expert/validate.py --target-dir .
```

**Checks:** shebang, strict mode, IFS, cleanup trap, syntax, dangerous patterns (eval/backticks), test brackets, variable braces, local vars in functions, readonly constants, chmod permissions, mktemp usage, curl pipe, unquoted subshell

#### Python Validator
**Purpose:** Validate Python files with AST analysis (8 checks)
**Location:** `.dev-aid/skills/expert/python/validate.py`

```bash
python3 .dev-aid/skills/expert/python/validate.py --target-dir . --skip-tests
```

**Checks:** shell=True, eval/exec, pickle.load, hardcoded secrets, generic exceptions, print in library code, missing type annotations, test coverage

**Value:** Catches security issues, enforces coding standards. Extensible — any skill can add a `validate.py`.

Full guide: [VALIDATOR-FRAMEWORK.md](VALIDATOR-FRAMEWORK.md)

### Operations Commands

#### `/dev-aid-deploy-validate`
**Purpose:** Pre-deployment validation
**Status:** ✅ Included
**Checks:** Tests, linting, security, dependencies
**Location:** `.dev-aid/providers/claude/.claude/commands/operations/dev-aid-deploy-validate.md`
**Value:** Prevents production incidents

### Maintenance Commands

#### `/dev-aid-models-update`
**Purpose:** Update AI model registry with latest releases
**Status:** ✅ Included
**Features:**
- Latest model pricing
- Capability tracking
- Performance benchmarks
**Location:** `.dev-aid/providers/claude/.claude/commands/maintenance/dev-aid-models-update.md`
**Value:** Optimal model selection, cost optimization

---

## 📦 Additional Commands from Tresor (Optional Add-Ons)

Want even more capabilities? These can be added from claude-code-tresor:

#### `/compliance-check`
**Purpose:** Verify compliance (GDPR, SOC2, etc.)
**How to add:** Copy from `claude-code-tresor/commands/security/compliance-check/`

#### `/profile`
**Purpose:** Performance profiling
**Analyzes:** CPU, memory, I/O bottlenecks
**How to add:** Copy from `claude-code-tresor/commands/performance/profile/`

#### `/benchmark`
**Purpose:** Run benchmarking tests
**How to add:** Copy from `claude-code-tresor/commands/performance/benchmark/`

#### `/health-check`
**Purpose:** System health monitoring
**How to add:** Copy from `claude-code-tresor/commands/operations/health-check/`

#### `/incident-response`
**Purpose:** Incident management workflow
**How to add:** Copy from `claude-code-tresor/commands/operations/incident-response/`

---

## 🛠️ Creating Custom Commands

### Template for New Command

Create: `.dev-aid/providers/claude/.claude/commands/[category]/[command-name].md`

```markdown
---
name: my-command
description: Brief description
category: category-name
author: Your Name
version: 1.0.0
---

# Command Name

Your command instructions here...

## Purpose
What this command does

## Usage
How to use it

## Output
What it produces
```

### Example: Custom Test Command

```markdown
---
name: run-tests
description: Run all tests with coverage
category: testing
author: Dev Team
version: 1.0.0
---

# Run Tests with Coverage

Run the full test suite with coverage reporting.

## Steps
1. Run unit tests
2. Run integration tests
3. Generate coverage report
4. Check coverage threshold (80%)

## Output
- Test results
- Coverage report in `.dev-aid/reports/coverage/`
```

---

## 📚 How-To Guides for Developers

### Quick Start: Using Slash Commands

**Step 1: Discover available commands**
```bash
# In Claude Code, type:
/
# This shows autocomplete of available commands
```

**Step 2: Run a command**
```bash
/dev-aid-analyze
```

**Step 3: Review output**
```bash
cat .dev-aid/analysis/adaptation-plan.md
```

### Adding Commands from Tresor

**Option 1: Copy Individual Command**
```bash
# Copy command file
cp claude-code-tresor/commands/security/audit/audit.md \
   dev-aid/.dev-aid/providers/claude/.claude/commands/security/

# Test it
/audit
```

**Option 2: Copy Entire Category**
```bash
# Copy all security commands
cp -r claude-code-tresor/commands/security/ \
   dev-aid/.dev-aid/providers/claude/.claude/commands/

# Now you have: /audit, /vulnerability-scan, /compliance-check
```

### Customizing Commands for Your Project

**Example: Customize /audit for your stack**

1. Copy the command:
```bash
cp claude-code-tresor/commands/security/audit/audit.md \
   dev-aid/.dev-aid/providers/claude/.claude/commands/security/
```

2. Edit for your needs:
```bash
vim dev-aid/.dev-aid/providers/claude/.claude/commands/security/audit.md
```

3. Add project-specific checks:
```markdown
## Custom Checks for Our Project
- Check Stripe API key rotation (every 90 days)
- Verify AWS IAM policies
- Scan for exposed Redis ports
```

---

## 🎯 Recommended Command Workflow

### For New Projects

**Week 1: Setup**
```bash
/dev-aid-analyze              # Understand codebase
/dev-aid-status               # Verify configuration
# Review adaptation plan
# Implement Phase 1 recommendations
```

**Week 2: Quality**
```bash
/code-health              # Assess code quality
/debt-analysis            # Identify tech debt
# Address critical issues
```

**Week 3: Security**
```bash
/audit                    # Security audit
/vulnerability-scan       # Check dependencies
# Fix security issues
```

**Week 4: Performance**
```bash
/profile                  # Find bottlenecks
/benchmark                # Baseline performance
# Optimize critical paths
```

### For Production Projects

**Before Deployment**
```bash
/deploy-validate          # Pre-deployment checks
# Fix any issues
# Deploy
```

**After Deployment**
```bash
/health-check             # Verify system health
# Monitor for 24 hours
```

**Monthly Maintenance**
```bash
/vulnerability-scan       # Security updates
/code-health              # Code quality
/debt-analysis            # Tech debt review
```

---

## 🔗 Command Chaining

You can chain commands for workflows:

**Example: Full Quality Check**
```bash
# Run multiple checks
/code-health
/debt-analysis
/audit
/vulnerability-scan

# Then review all reports
cat .dev-aid/reports/code-health.md
cat .dev-aid/reports/debt-analysis.md
cat .dev-aid/reports/audit.md
cat .dev-aid/reports/vulnerabilities.md
```

---

## 📊 Command Categories

| Category | Commands Available | Purpose |
|----------|-------------------|---------|
| **Agents (CLI)** | `dev-aid-agent` (8 subcommands + teams) | Autonomous AI agents for scripts/CI |
| **Agents (Slash)** | `aid-pr`, `aid-test`, `aid-debt`, `aid-ci`, `aid-conflict`, `aid-research`, `aid-onboard`, `aid-docs`, `aid-help` | Interactive agent slash commands with short aliases |
| **Setup** | `/dev-aid-analyze`, `/dev-aid-status`, `/dev-aid-config-core-skills` | Initial setup, analysis, configuration |
| **Router** | `/dev-aid-router-challenger`, `/dev-aid-router-ensemble`, `/dev-aid-router-status` | Multi-AI orchestration |
| **Security** | `/dev-aid-audit`, `/dev-aid-vulnerability-scan` | Security operations |
| **Quality** | `/dev-aid-code-health`, `/dev-aid-debt-analysis` | Code quality |
| **Productivity** | `/dev-aid-api-contract`, `/dev-aid-commit-plan`, `/dev-aid-review-staged` | Development workflow |
| **Operations** | `/dev-aid-deploy-validate` | DevOps workflows |
| **Performance** | `/profile`, `/benchmark` (add from Tresor) | Performance analysis |
| **Documentation** | (custom) | Doc generation |

---

## 💡 Best Practices

### 1. Use Commands Consistently
- Run `/code-health` weekly
- Run `/audit` monthly
- Run `/deploy-validate` before every deploy

### 2. Automate with CI/CD
```yaml
# .github/workflows/quality.yml
jobs:
  quality-check:
    runs-on: ubuntu-latest
    steps:
      - name: Code health check
        run: claude run /code-health

      - name: Security audit
        run: claude run /audit
```

### 3. Review and Act on Reports
- Don't just run commands - review outputs
- Track metrics over time
- Set quality gates

### 4. Customize for Your Needs
- Adapt commands to your tech stack
- Add project-specific checks
- Remove irrelevant checks

---

## 🛠️ Utility Scripts

Dev-AID provides standalone utility scripts for common development tasks:

### CI/CD Automation

#### `generate-ci.sh`
**Purpose:** Auto-generate GitHub Actions workflows
**Location:** `.dev-aid/scripts/generate-ci.sh`
**Detects:** Node.js, Python, Rust, Go projects
**Features:**
- Auto-detects package managers (npm/yarn/pnpm/bun, pip/poetry/uv, cargo)
- Security by default (Gitleaks + Trivy included)
- Docker support with image scanning
- Optional `--optimize` flag for 40-70% faster CI runs
**Usage:**
```bash
.dev-aid/scripts/generate-ci.sh
.dev-aid/scripts/generate-ci.sh --optimize  # Recommended: faster CI with caching
.dev-aid/scripts/generate-ci.sh -o custom-workflow.yml
```

### Architecture & Visualization

#### `map-architecture.sh`
**Purpose:** Generate Mermaid.js architecture diagrams
**Location:** `.dev-aid/scripts/map-architecture.sh`
**Generates:**
- Class diagrams (OOP structure)
- Module dependency graphs
- C4 component diagrams
**Usage:**
```bash
.dev-aid/scripts/map-architecture.sh
.dev-aid/scripts/map-architecture.sh src/ -t class
.dev-aid/scripts/map-architecture.sh -o docs/my-diagram.md
```

### Testing & Data

#### `fabricate-data.sh`
**Purpose:** Generate realistic mock test data
**Location:** `.dev-aid/scripts/fabricate-data.sh`
**Supports:** JSON Schema, Pydantic, TypeScript interfaces
**Formats:** JSON, CSV, SQL
**Usage:**
```bash
.dev-aid/scripts/fabricate-data.sh schema.json
.dev-aid/scripts/fabricate-data.sh model.py -c 100 -f csv
.dev-aid/scripts/fabricate-data.sh schema.json -f sql -o data.sql
```

### Documentation

#### `sync-docs.sh`
**Purpose:** Detect documentation drift
**Location:** `.dev-aid/scripts/sync-docs.sh`
**Checks:** Package managers, scripts, Docker ports
**Usage:**
```bash
.dev-aid/scripts/sync-docs.sh
.dev-aid/scripts/sync-docs.sh --readme CONTRIBUTING.md
```

### Productivity

#### `dev-aid-guide.sh`
**Purpose:** Interactive feature discovery
**Location:** `.dev-aid/scripts/dev-aid-guide.sh`
**Features:** Menu-driven, best practices, command catalog
**Usage:**
```bash
.dev-aid/scripts/dev-aid-guide.sh
```

#### `draft-pr.sh`
**Purpose:** Generate PR descriptions from git diff
**Location:** `.dev-aid/scripts/draft-pr.sh`
**Usage:**
```bash
.dev-aid/scripts/draft-pr.sh > pr-description.md
```

#### `onboard.sh`
**Purpose:** Onboard new developers
**Location:** `.dev-aid/scripts/onboard.sh`
**Features:** Environment checks, project detection, setup guide
**Usage:**
```bash
.dev-aid/scripts/onboard.sh
```

---

## 🚀 Next Steps

1. **Try the built-in commands:**
   ```bash
   /dev-aid-analyze    # Analyze codebase
   /dev-aid-status     # Check configuration
   ```

2. **Add recommended commands from Tresor:**
   ```bash
   # Add security commands
   cp -r claude-code-tresor/commands/security/ \
      dev-aid/.dev-aid/providers/claude/.claude/commands/
   ```

3. **Create your first custom command:**
   ```bash
   vim dev-aid/.dev-aid/providers/claude/.claude/commands/testing/run-all-tests.md
   ```

4. **Set up CI/CD integration:**
   - Add commands to your GitHub Actions
   - Set quality gates
   - Automate reports

---

## 📖 Additional Resources

- [Dev-AID Style Guide](./DEV-AID-STYLE-GUIDE.md)
- [Automation Guide](./AUTOMATION-GUIDE.md)

---

**Last Updated:** 2026-02-08
**Version:** 1.5.0-beta.1
