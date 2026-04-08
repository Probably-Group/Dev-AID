# Dev-AID Changelog

All notable changes to Dev-AID will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

(no unreleased changes — see [1.5.1] below for the most recent shipped work)

---

## [1.5.1] - 2026-04-08

### Added
- **Tree-sitter AST Chunker**: Local search now does true AST-aware chunking for python, javascript, typescript, java, go, rust, c, and cpp. Walks the tree-sitter parse tree and emits one chunk per function/class/method, with line-based fallback for unsupported languages or parse failures. Class chunks intentionally overlap with their nested method chunks. Replaces a stub `_init_parsers()` that did nothing.
- **`/aid-skills` command**: List the skills installed in `.dev-aid/skills/` and (when possible) which auto-loaded for the current session.
- **`uninstall-dev-aid.sh`**: Clean uninstall script that removes generated provider directories, symlinks, and `.dev-aid/` after a confirmation prompt with optional memory-bank export.
- **Modification log hook**: `post-tool-use-tracker.sh` now appends `timestamp | tool | files` to `.claude/modification-log.txt` (was an `exit 0` stub).
- **Agent Trace Collection**: JSONL-based execution recording with `--trace` flag for all agents and teams
- **Automatic Prompt Optimization (APO)**: LLM-driven critique + beam search to improve agent prompts with human approval gate
  - `apo optimize` — analyze traces, generate candidates, score against golden tests, present diff
  - `apo rollback` — restore previous prompt versions
  - `apo history` / `apo status` — version tracking and status overview
- **Golden Test Cases**: Predefined test cases for all 9 agents at `.dev-aid/config/golden-tests.json`
- **Memory Bank Integration**: `agent-optimization.md` for storing APO results with on-demand keyword loading
- **APO Slash Commands**: `aid-apo` alias for Claude and Gemini providers
- New protected paths: agent-traces, agent-prompts, golden-tests.json in update-lib.sh
- New directories: agent-traces, agent-prompts in setup-dev-aid.sh Phase 2
- **Memory Bank Engine Improvements**: 6 new capabilities in the orchestration router
  - **On-demand loading**: Memory bank files loaded based on query relevance using keyword matching (not unconditionally)
  - **Token budget**: Configurable `standing_context_tokens` with `minimal`/`balanced`/`generous` budget modes
  - **Staleness detection**: Files older than `staleness_warning_days` (default: 30) annotated with warnings
  - **Write-back instructions**: System prompt and stop hook instruct AI to update memory bank files when patterns/decisions change
  - **Section-level extraction**: Oversized on-demand files trimmed to most relevant sections per query (scored by keyword overlap)
  - **Per-file metadata**: `memory_bank_metadata` tracks category, token count, age, and staleness per file
- New `MemoryBankConfig` fields: `on_demand`, `standing_context_tokens`, `standing_context_budget`, `staleness_warning_days`
- New `ConfigLoader` methods: `get_on_demand_files()`, `get_standing_context_tokens()`
- New `ConfigLoaderProtocol` methods matching the above
- New `DevAIDContext.memory_bank_metadata` field
- `build_context()` and `build_context_async()` accept optional `prompt` parameter for query-aware loading
- All 3 provider templates (Claude, Gemini, OpenAI) include "Memory Bank Updates" write-back section
- Stop hook provides specific per-file update guidance instead of generic reminder
- 20+ new tests covering budget enforcement, staleness, on-demand selection, markdown parsing, section extraction

### Changed
- **README Restructured**: Major reorder for faster "wow moment"
  - Quick Start moved from line 867 to line 48 (reachable in 2 scrolls)
  - New flow: pitch → TL;DR → Quick Start → automations table → features
  - All 12 core feature sections wrapped in collapsible `<details>` tags
  - Feature Reference Table, comparison tables, and research results collapsed
  - "What's New" replaced with 4-bullet summary linking to WHATS-NEW.md and CHANGELOG
  - Merged 3 comparison tables into one collapsed block, removed redundant Key Differentiators
  - Net reduction: ~90 lines while preserving all content
- `_load_memory_bank()` returns `Tuple[Dict, Dict]` (content + metadata) instead of plain `Dict`
- Solo, Ensemble, and Challenger modes pass `prompt=request` to `build_context()` for query-aware loading
- `format_context_for_ai()` includes age annotations and write-back maintenance reminder when memory bank is non-empty
- Updated documentation: README, QUICK-START, FAQ, DEV-AID-STYLE-GUIDE, ROUTER-STATUS, STORAGE-LOCATIONS, OpenAI README, MEMORY-BANK-GUIDE
- `setup-venv.sh` uses plain `realpath` instead of `realpath -m` for macOS BSD compatibility (the `-m` flag is GNU-only and crashed Phase 7 of setup on macOS).
- `search.json` `vector` block updated to document the runtime defaults (`google/embeddinggemma-300m`, dim 768) instead of the stale `all-MiniLM-L6-v2` placeholder. The block is still informational only — `hybrid_scorer._load_config()` does not currently read it.
- README + LinkedIn post: added a one-line clarification to the "native with 6 editors" claim noting that Cursor, Windsurf, and Cline are Claude-compatible (they read `.claude/commands/` natively, so every `/aid-*` slash command works in all 6 editors with no extra setup).

### Removed
- Legacy bash mode scripts at `.dev-aid/orchestration/modes/{solo,ensemble,challenger,none}.sh` (~340 LOC). Zero references in the repo. The real implementations are at `.dev-aid/orchestration/router/modes/*.py` and have been since the Python router migration.

### Fixed
- `skill-activation-conservative.sh` hook renamed "Auto-loading: X" labels to "Suggested skill: X" so the messages match what the hook actually does (it prints suggestions to stdout that Claude Code sees as context — it does not load skills itself).

---

## [1.5.0-beta.3] - 2026-02-09

### Added
- **`gh-dev-aid` CLI Extension**: Single-command installation and management via GitHub CLI
  - `gh dev-aid init [path]` — Install Dev-AID into any project (uses `gh repo clone` for auth)
  - `gh dev-aid update` — Update with backup, protected paths, and old backup cleanup
  - `gh dev-aid check` — Lightweight version check via GitHub API (no clone)
  - `gh dev-aid status` — Show version + health check
  - `gh dev-aid version` — Show extension and installed versions
  - Extension repo: [`Probably-Group/gh-dev-aid`](https://github.com/Probably-Group/gh-dev-aid)
- **Proactive Update Notifications**: Automatic version check on session start for Claude Code and Gemini CLI
  - Throttled to once per 24 hours using global cache (`~/.cache/dev-aid/`)
  - Shared across all projects — one API call per day regardless of how many projects use Dev-AID
  - Non-blocking with 3-second timeout (macOS compatible, no `timeout` dependency)
  - Script: `.dev-aid/scripts/check-update-notify.sh`
- **`/aid-team` Slash Command**: New command for multi-agent team orchestration
  - Full command (`dev-aid-agent-team`) + short alias (`aid-team`) for both Claude and Gemini
  - Documents parallel, sequential, and DAG workflow types
  - Corrected agent names to match `builtin_teams.py`: vulnerability-scanner, auth-reviewer, dependency-auditor
- **Unified Init System** (`setup-dev-aid.sh`): Single entry point for complete Dev-AID initialization
  - 8-phase setup: prerequisites, directories, interactive wizard, config files, context files + provider setup, memory bank, infrastructure, validation
  - Flags: `--yes` (non-interactive), `--minimal` (skip infrastructure), `--infrastructure-only`, `--wizard-only`
  - State detection for idempotent re-initialization (safe to run multiple times)
  - Extracted libraries: `lib/detection.sh`, `lib/wizard-functions.sh`, `lib/provider-setup.sh`

### Changed
- **Repository moved to `Probably-Group/Dev-AID`** (was `martinholovsky/Dev-AID`)
- **Documentation uses `/aid-*` slash commands as primary interface** — CLI-form `dev-aid-agent` kept as reference for CI/scripts
- **Update system now uses `gh dev-aid update`** as primary method (replaces `update-dev-aid.sh` option 1 which was unimplemented)
- Updated README.md, QUICK-START.md, VALUE-PROPOSITION.md Quick Start sections to use `gh extension install` as primary
- Updated CONTRIBUTING.md to reference `setup-dev-aid.sh` as primary setup
- Added `.github/copilot-ignore` and `.github/pull_request_template.md` for beta security
- **`init-repo.sh`** and **`install.sh`** are now thin backward-compatibility wrappers delegating to `setup-dev-aid.sh`
- **`gh dev-aid init`** now calls `setup-dev-aid.sh` for complete setup (was `init-repo.sh` for infrastructure-only)
- **hooks.json** and **hooks.toml**: Fixed session-start hook to reference `check-update-notify.sh` (was `check-updates.sh`)
- Updated all documentation to reference `setup-dev-aid.sh` as primary setup script

### Removed
- `CLAUDE.md.example` (stale)
- `docs/plans/` directory (stale)
- `gh-dev-aid/` from main repo (moved to its own repo)

---

## [1.5.0-beta.2] - 2026-02-08

### Added
- **Language-Specific Security Scanners in Pre-Push Hook**: Auto-detected security checks that run only when the language is present in the repository
  - **Opengrep Fine-Tuning**: Expanded from 5 default rulesets to 10 universal rulesets (added OWASP Top 10, TrailOfBits, command injection, insecure transport, JWT) + 12 auto-detected language-specific rulesets (Python, JavaScript, TypeScript, Go, Rust, Swift, Java, Kotlin, Ruby, PHP, C#, Scala)
  - **Shell SAST**: ShellCheck for `*.sh` files with warning-level severity
  - **C/C++ SAST**: Flawfinder for `*.c`, `*.h`, `*.cpp`, `*.cc`, `*.cxx` files with CWE-mapped findings (level 2+)
  - **Swift SAST**: mobsfscan for `*.swift` files with OWASP MASVS/MSTG compliance
  - **Python SAST**: Bandit for `*.py` files with medium+ severity (excludes venv/node_modules)
  - **Python Deps**: pip-audit for `requirements*.txt` or `pyproject.toml`
  - **JS/TS Deps**: npm audit for `package-lock.json` or `yarn.lock` (high+ severity)
  - **Rust Deps**: cargo audit for `Cargo.lock`
  - **Go Vulns**: govulncheck for `go.mod`
  - Missing tools emit warnings (non-blocking) — each check is optional and independent
  - All temp files use secure cleanup with shred when available

### Changed
- **install-security-tools.sh**: Added `install_python_security_tools()` for bandit, pip-audit, flawfinder, mobsfscan via pipx (preferred) or pip --user
- **install.sh** (now wrapper): Previous version added optional tool checks for ShellCheck, Bandit, pip-audit, Flawfinder, mobsfscan, cargo-audit, govulncheck
- **SECURITY-TOOLS-REFERENCE.md**: Complete documentation for all 11 security tools (3 universal + 4 language SAST + 4 dependency audit)
- **AUTOMATION-GUIDE.md**: Updated architecture diagrams, tool stack tables, and pre-push hook documentation

---

## [1.3.0-beta.15] - 2026-02-07

### Added
- **Agent Framework** (`.dev-aid/agents/`): Provider-agnostic autonomous agent framework powered by Dev-AID's 72+ expert skills
  - **Core**: `AgentRunner` loop (send → tool calls → execute → repeat), `ToolRegistry` with per-provider format export, `SkillLoader` for SKILL.md parsing, `SafetyConfig` with command blocklist and dry-run mode
  - **Provider Adapters**: Anthropic (Messages API + optional Claude Agent SDK bridge), OpenAI (+ Ollama/LM Studio compatible), Google Gemini — all via unified `ProviderAdapter` protocol
  - **Built-in Tools**: `read_file`, `write_file`, `list_directory`, `glob_files`, `grep_search`, `find_files`, `run_bash`, `git_status`, `git_diff`, `git_log`, `git_add`, `git_commit`, `gh_issue_view`, `gh_pr_view`, `gh_pr_create`
  - **8 Built-in Agents**: `pr-reviewer`, `test-generator`, `tech-debt-hunter`, `ci-fixer`, `conflict-resolver`, `research`, `onboarding`, `doc-auditor`
  - **CLI**: `dev-aid-agent <agent> [options]` with `--provider`, `--model`, `--dry-run`, `--verbose`, `--json` flags
  - **Safety**: Per-tool risk levels (safe/moderate/dangerous), command blocklist with pattern matching, path restrictions, dry-run mode
  - **Config**: `.dev-aid/config/agents.json` for per-agent defaults
  - **Tests**: 112 tests covering models, safety, skill loader, tool registry, tools, agent runner, and provider adapters

---

## [1.3.0-beta.14] - 2026-02-06

### Added
- **Skill Validator Framework**: Extensible compliance checking where any skill can include a `validate.py` that gets auto-discovered and run
  - Shared library: `.dev-aid/lib/validator_common.py` (types, CLI, output formatting)
  - Bash Expert validator: 14 checks (shebang, strict mode, IFS, trap, syntax, eval/backticks, test brackets, variable braces, local vars, readonly, chmod, mktemp, curl pipe, unquoted subshell)
  - Python validator: 8 AST-based checks (shell=True, eval/exec, pickle, hardcoded secrets, generic exceptions, print in libs, type annotations, coverage)
  - Runner script: `.dev-aid/scripts/run-validators.py` with `--filter-context`, `--json`, `--strict`, `--validators`
  - Context-aware filtering: detects project technologies, only runs relevant validators
  - JSON output mode for CI integration
  - Documentation: `.dev-aid/docs/VALIDATOR-FRAMEWORK.md`
- Compliance scan integrated into `setup-dev-aid.sh` Phase 8

### Changed
- **CI optimization**: PR checks now run on ubuntu-only instead of 3-OS matrix (ubuntu + windows + macos), saving CI minutes on free plans. Cross-platform testing remains in `release-gate.yml` for releases
- PR check summary job now tolerates skipped/cancelled upstream jobs (handles billing limits gracefully)

### Removed
- `validate-bash-scripts.sh` from orchestration/ (replaced by `.dev-aid/skills/expert/bash-expert/validate.py`)
- `validate-python-scripts.py` from orchestration/ (replaced by `.dev-aid/skills/expert/python/validate.py`)

---

## [1.3.0-beta.13] - 2026-02-03

### Added
- **Codex CLI Support**: Full integration with OpenAI's Codex CLI as a fourth supported AI coding tool
  - Symlink-based skill sharing (zero duplication with existing 85 skills)
  - `AGENTS.md` generation from project context detection
  - Session-start hook for auto-loading relevant skills
  - Same skill format as Claude Code (YAML frontmatter + Markdown)
  - New provider directory: `.dev-aid/providers/codex/`
  - Installation guide and troubleshooting documentation

### Changed
- Supported AI tools: 3 → 4 (Claude Code, Gemini CLI, Cursor, Codex CLI)
- Updated `provider-context-init.sh` to support `codex` provider with `AGENTS.md` context file
- Updated `CROSS-PLATFORM-ROUTER.md` with Codex CLI configuration section
- Updated README.md to include Codex CLI in supported tools

### Notes
- Codex CLI uses `AGENTS.md` (not `CODEX.md`) per OpenAI's specification
- Skills are shared via symlinks - changes to skills propagate to all providers automatically
- AGENTS.md loading order: `~/.codex/AGENTS.override.md` > `~/.codex/AGENTS.md` > project `AGENTS.md` > subdirectory files

---

## [1.3.0-beta.12] - 2026-02-02

### Added
- `talos-cluster-ops` skill - Comprehensive K8s/Talos cluster operations for troubleshooting, upgrades, and health monitoring
- `nuxt4` skill - Nuxt 4 full-stack patterns with server routes, useFetch, hybrid rendering, and runtime config security
- `vue3` skill - Pure Vue 3 Composition API patterns with reactivity, composables, provide/inject, and XSS prevention

### Changed
- **BREAKING**: Replaced all 69 shared expert skills with improved dotfiles versions
  - More concise CWE-based security patterns (NEVER/ALWAYS format)
  - 2-3x more code examples and patterns per skill
  - Removed verbose CVE research protocols in favor of timeless vulnerability classes
  - All skills now follow unified v2.0.0 template

### Removed
- `async-programming` skill (consolidated into `async-expert`)
- `typescript` skill (consolidated into `typescript-expert`)
- `fastapi` skill (consolidated into `fastapi-expert`)
- `vue-nuxt` skill (consolidated into `vue3` and `nuxt4`)
- `vue-nuxt-expert` skill (consolidated into `vue3` and `nuxt4`)
- `docker-expert` skill (not in dotfiles, was redundant)

### Notes
- Expert skills count: 72 → 73 (removed 4 duplicates, added 3 new)
- All skills synced from personal dotfiles for improved quality
- Skills registry updated to match new skill set

---

## [1.3.0-beta.11] - 2026-02-02

### Added
- **Process Skills System** (7 new skills): Behavioral protocols for disciplined workflows
  - `verification-gate` - No completion claims without evidence (strict enforcement)
  - `tdd-protocol` - Enforce RED-GREEN-REFACTOR cycle
  - `systematic-debugging` - Root cause first, fix second (4-phase protocol)
  - `isolated-development` - Git worktree per feature/issue with auto-setup
  - `design-first` - Think before coding (YAGNI enforcement)
  - `staged-review` - Two-stage review (spec compliance → code quality)
  - `plan-execution` - Batch execution with checkpoints and blocker protocol

  Key enhancements over traditional process patterns:
  - Language-aware verification commands (auto-detects Python/Node/Rust/Go)
  - Router integration for challenger mode cross-model verification
  - FAISS local search integration for pattern matching
  - Security tool correlation (Trivy/Gitleaks findings)
  - Task list integration for progress tracking
  - Memory bank persistence for design decisions
  - Configurable enforcement levels (strict/warning/off)

  Configuration: `.dev-aid/config/process-skills.json`
  Documentation: `.dev-aid/skills/process/README.md`

### Changed
- Updated skills README to include process skills category
- Skills system now has three tiers: core (5), expert (72), process (7)

---

## [1.3.0-beta.10] - 2026-01-09

### Added
- **Deep Research / External Brain MCP** (Issue #94): Multi-provider research system for Dev-AID
  - 3 Research Providers: Gemini Deep Research, Perplexity Sonar, Tavily
  - Smart Query Routing: Auto-classifies queries (factual/exploratory/technical) and selects optimal provider
  - Semantic Caching: SQLite-based cache with 70% similarity threshold, 24-48h TTL
  - MCP Server: Full Model Context Protocol implementation with 6 research tools
  - CLI Tool: `dev-aid-research search|quick|deep "query"` for direct access
  - Router Integration: Auto-fallback to external research when local context insufficient
  - Expert Skill: `deep-research-expert` auto-activates on research keywords
  - Module location: `.dev-aid/deep-research/`

- **Quality Detection for Context Files**: New comprehensive quality assessment during initialization
  - Detects low-quality content (< 20 lines, < 3 sections)
  - Identifies placeholder text (TODO, FIXME, TBD, etc.)
  - Checks for recommended sections (Role/Purpose, Tech Stack, Guidelines, Workflow, Testing)
  - Detects empty or minimal sections (< 3 lines of content)
  - Quality levels: `good`, `incomplete`, `draft`, `poor`
  - Clear feedback on what will be enhanced during merge

- **Enhanced Provider Templates**: All provider templates now include robust guidance
  - Code Quality Standards (Style, Error Handling, Security)
  - Testing Requirements (unit, integration, e2e)
  - OWASP Top 10 security awareness
  - Consistent structure across Claude, Gemini, and OpenAI templates
  - Provider-specific strengths highlighted (e.g., Gemini's large context window)

### Fixed
- **Smart Context Initialization**: Fixed handling of existing context files that already use progressive disclosure
  - Detects `.<provider>/rules/` directory with markdown files (e.g., `.claude/rules/`, `.gemini/rules/`)
  - Detects `@` file references in existing context files
  - Skips redundant splitting when user has already organized content across multiple files
  - Respects user's existing structure - rules directories and `@` references remain untouched
  - Prevents double-splitting that could break existing file reference chains

### Changed
- **Multi-Provider Support**: All initialization features now work for Claude, Gemini, and OpenAI
  - Progressive disclosure detection is provider-agnostic
  - Quality detection works for CLAUDE.md, GEMINI.md, and OPENAI.md
  - Provider selection happens in Step 3 of install wizard (`ask_providers()`)
  - Templates automatically adapt to detected tech stack

- **Initialization Flow**: Updated to 8 steps (was 6)
  1. Backup existing context file
  2. Detect existing progressive disclosure
  3. Assess content quality
  4. Validate content for issues
  5. Merge with Dev-AID template
  6. Apply progressive disclosure (or skip if already in use)
  7. Create symlink
  8. Generate migration report

---

## [1.3.0-beta.9] - 2026-01-06

### Added
- **TOON Format Integration (Phase 1)**: Pure Python implementation for 40-60% token reduction
  - Native Python TOON encoder with YAML-like syntax and CSV tabular data support
  - Pure Python TOON decoder with full format parsing
  - JSON ↔ TOON bidirectional converter with token savings estimation
  - 21 comprehensive unit tests (100% pass rate)
  - Zero external dependencies (no Node.js required)
  - Ready for skill and config integration (Phases 2-4)
  - Expected savings: $30,000-$50,000/year for 100-developer teams
- **Smart Context File Initialization**: Intelligent handling of existing provider context files
  - Backs up existing CLAUDE.md, GEMINI.md, OPENAI.md files
  - Validates content for outdated tech versions and conflicts
  - Merges user content with Dev-AID enhancements
  - Progressive disclosure for files >500 lines
  - Migration reports with clear resolution suggestions

### Fixed
- **Test Suite Updates**: Fixed API changes and root permission handling
  - Updated E2E tests for current API methods
  - Added pytest.skip() for root-only permission tests
  - All 294 tests passing (100% pass rate)
- **CI Shellcheck Warnings**: Resolved 7 shellcheck warnings across 5 bash scripts
  - Fixed SC2076 (regex pattern matching) in reconfigure.sh
  - Fixed SC2064 (trap statement expansion) in 3 scripts
  - Fixed SC2289, SC2027, SC2140 (backticks and quoting) in dev-aid-dependencies.sh

## [1.3.0-beta.1] - 2025-12-10

### Added
- **Optimized CI Workflow**: New `CI (Optimized)` template with advanced caching, concurrency groups, and parallel execution support
  - 40-70% faster execution times
  - Automated dependency caching for Python and Node.js
  - Smart concurrency to cancel outdated builds
- **Parallel Testing Support**: Integrated `pytest-xdist` into optimized CI templates
  - Auto-detection of CPU cores for parallel test execution
  - Significant reduction in test suite runtime
- **Enhanced Linting Configuration**: Updated `flake8` configuration in CI generator
  - Automatically excludes `.venv`, `venv`, and `.env` directories
  - Prevents false positive linting errors from virtual environment files

### Fixed
- **CI Workflow Bugs**: Resolved issue where `pytest-xdist` was missing in optimized workflows
- **Cache Invalidation**: Fixed persistent cache issues by implementing versioned cache keys
- **Linting Noise**: Eliminated thousands of linting errors by properly excluding virtual environments

## [1.2.0] - 2025-12-06

### Added

#### Performance & Architecture
- **Optimized Context Detection**: New Python implementation (`context-detector.py`) replaces O(n²) bash loops with single-pass scanning
  - **10x performance improvement**: <200ms vs >2s on large repositories
  - **Dynamic pattern loading**: Reads from `skills-index.json` instead of hardcoded patterns
  - **Three modes**: `detect`, `select`, `auto` for flexible usage
  - Maintains backward compatibility via bash wrapper scripts

#### Security Enhancements
- **Pinned Dependencies**: All 63 Python dependencies now use exact versions (`==`) for reproducible builds
  - Prevents supply chain attacks via malicious 'latest' versions
  - Deterministic builds across all environments
  - Added security notice and update instructions in requirements.txt

- **GitHub Actions Security Pipeline**: Activated automated security scanning
  - Workflow now runs on push, PR, weekly schedule, and manual triggers
  - Scans: Gitleaks (secrets), Semgrep (SAST), Trivy (dependencies), Hadolint (Docker), Checkov (IaC)
  - Results uploaded to GitHub Security tab with SARIF format

- **Pre-Commit Hook Fail-Closed**: Security tools now block commits when missing
  - Changed from warnings to errors for missing gitleaks/opengrep/trivy
  - Provides installation instructions when tools not found
  - Can bypass with `git commit --no-verify` if needed

- **RAG Installer Checksum Verification**: Setup script now verifies SHA256 before execution
  - Downloads to temp file, verifies hash, then executes
  - Supports custom forks via `RAG_REPO_URL` environment variable
  - Prevents MITM attacks and compromised upstream scenarios

- **CI/CD Tool Installation Security**: Replaced insecure patterns with official GitHub Actions
  - Uses `gitleaks/gitleaks-action@v2`, `aquasecurity/trivy-action@master`, `hadolint/hadolint-action@v3.1.0`
  - Eliminated `curl | bash` and unverified `wget` patterns

#### New Features
- **Refactoring Expert Skill**: Comprehensive 522-line skill for safe code refactoring
  - Safety-first methodology with mandatory pre-refactor testing
  - Strangler Fig pattern for legacy system modernization
  - Anti-hallucination protocol for safe code changes
  - Auto-activates on: refactor, rewrite, legacy, technical debt

- **RAG Vendoring Support**: Documentation and tooling for dependency management
  - Guide for forking and maintaining custom copies
  - Three strategies: Vendored copy, Git submodule, or Upstream
  - Environment variable support for custom repositories

#### CI/CD & Testing Automation
- **PR Check Workflow** (#33): Fast feedback loop for pull requests
  - Path-based filtering (runs only on *.py, *.sh, workflows, .dev-aid changes)
  - Python Lint: Black, Isort, Flake8 + Pytest with coverage + Mypy type checking
  - Bash Lint: Shellcheck for all shell scripts
  - Summary job for overall pass/fail status
  - Saves GitHub Actions minutes by filtering irrelevant changes

- **Release Gate Workflow** (#34): Deep validation before publishing releases
  - Cross-platform testing: Ubuntu, macOS, Windows (Python 3.9-3.11)
  - Deep security: Full Gitleaks + Trivy scans (all severities)
  - Documentation validation: Lychee link checker for all markdown
  - Blocks release if CRITICAL vulnerabilities found
  - Comprehensive reporting with SARIF upload

- **VCR/Replay Testing** (#35): Cost-free AI client testing
  - Record HTTP interactions once with real API keys
  - Replay from cassettes in CI (fast, free, deterministic)
  - Automatic API key sanitization in recordings
  - Test suite: test_api_clients_vcr.py with multi-provider support
  - Smart skip logic: runs with cassettes OR API keys

#### Developer Productivity Tools
- **Auto-Generate CI/CD Workflows** (#36): Production-ready GitHub Actions from project detection
  - Supports: Node.js (npm/yarn/pnpm/bun), Python (pip/poetry/uv), Rust (cargo), Go
  - Security by default: All workflows include Gitleaks + Trivy
  - Auto-detects: package managers, build tools, test frameworks
  - Template library: Modular YAML templates in .dev-aid/templates/ci/
  - Docker support: Build and scan images if Dockerfile present
  - Usage: `.dev-aid/scripts/generate-ci.sh`

- **Architecture Mapper** (#37): Visual codebase understanding with Mermaid diagrams
  - AST-based analysis for Python files (classes, methods, inheritance)
  - Regex-based analysis for TypeScript/JavaScript
  - Generates: Class diagrams, Module dependency graphs, C4 component diagrams
  - Auto-saves to docs/architecture/generated-diagram.md
  - Limits: 100 files for performance, skips node_modules/venv/dist
  - Usage: `.dev-aid/scripts/map-architecture.sh`

- **Test Data Factory** (#38): Realistic mock data generation from schemas
  - Multi-schema support: JSON Schema, Pydantic models, TypeScript interfaces
  - Realistic data pools: names, emails, phones, addresses, URLs, UUIDs
  - Output formats: JSON, CSV, SQL INSERT statements
  - Type constraints: minLength, maxLength, minimum, maximum, patterns
  - Reproducible with --seed option
  - Usage: `.dev-aid/scripts/fabricate-data.sh schema.json -c 100 -f csv`

- **Living README** (#39): Documentation drift detector
  - Detects mismatches between README and project reality
  - Checks: Package manager commands, npm/pip scripts, Docker ports
  - Severity levels: HIGH, MEDIUM, LOW with actionable suggestions
  - Truth sources: package.json, pyproject.toml, Dockerfile, lockfiles
  - Usage: `.dev-aid/scripts/sync-docs.sh`

- **Interactive Guide** (#40): Feature discovery and best practices
  - Menu-driven interface for all Dev-AID capabilities
  - Context-aware tips: New project, bug fix, code review workflows
  - Complete command catalog with descriptions
  - Best practices for security, performance, quality
  - Usage: `.dev-aid/scripts/dev-aid-guide.sh`

- **PR Storyteller** (#41): Auto-generate semantic PR descriptions
  - Analyzes git diff and commit history
  - Structured template: Summary, Changes, Commits, Verification, Risk
  - Generates markdown ready for GitHub PRs
  - Usage: `.dev-aid/scripts/draft-pr.sh > pr-description.md`

- **Onboarding Buddy** (#42): Interactive developer setup
  - Environment checks: git, python, node, docker
  - Auto-detects: project type, package manager, build system
  - Shows correct install commands for the detected stack
  - Lists available Dev-AID features
  - Reduces "Time to First Commit" for new developers
  - Usage: `.dev-aid/scripts/onboard.sh`

### Changed

#### Code Quality Improvements
- **DRY Refactoring**: Eliminated 158 lines of duplicate code in API clients
  - New `@track_api_call` decorator centralizes timing and error handling
  - Applied to AnthropicClient, GoogleClient, OpenAIClient
  - Single source of truth for exception handling and latency tracking

- **Dynamic Package Management**: Setup script now parses requirements.txt dynamically
  - Removed hardcoded package arrays (lines 165, 188 in setup-venv.sh)
  - Import name mapping for packages with different import names
  - Single source of truth for package testing

- **Bash Script Simplification**: Orchestration scripts reduced to lightweight wrappers
  - `detect-context.sh`: 157 lines → 28 lines (82% reduction)
  - `select-skills.sh`: 210 lines → 31 lines (85% reduction)
  - Python backend handles all complexity

### Fixed

#### Security Vulnerabilities
- **CVE-2025-43859**: Updated h11 from 0.14.0 to 0.16.0
  - Patches critical HTTP request smuggling/desync vulnerability
  - Verified compatibility with httpcore and httpx

#### Issues Resolved
- #17: Restored refactoring expert skill with comprehensive methodology
- #18: Optimized O(n²) context detection loops to single-pass O(n)
- #19: Pre-commit hook now fails closed when security tools missing
- #20: Hardcoded patterns replaced with dynamic skills-index.json loading
- #21: RAG installer now verifies checksums before execution
- #22: Added vendoring support for RAG dependency stability
- #23: CI/CD tool installation now uses official GitHub Actions
- #24: Eliminated code duplication in orchestration scripts
- #26: Pinned all Python dependencies to exact versions
- #27: Refactored DRY violations in API client error handling
- #28: Removed hardcoded package lists from setup script
- #31: Patched h11 CVE-2025-43859 vulnerability
- #32: Activated GitHub Actions security workflows
- #33: Added optimized PR check workflow for fast feedback
- #34: Implemented release gate workflow with cross-platform testing
- #35: Added VCR/replay testing for cost-free AI client tests
- #36: Created auto-generate CI/CD workflows tool
- #37: Implemented architecture mapper for visual diagrams
- #38: Built test data factory for mock generation
- #39: Added living README documentation drift detector
- #40: Created interactive guide for feature discovery
- #41: Implemented PR storyteller for auto PR descriptions
- #42: Built onboarding buddy for new developer setup

**Total: 26 issues resolved in v1.2.0**

### Technical Details

#### Dependency Updates
- anthropic: 0.18.0+ → 0.39.0
- google-generativeai: 0.3.0+ → 0.8.3
- openai: 1.0.0+ → 1.54.5
- pydantic: 2.0.0+ → 2.10.3
- pytest: 7.4.0+ → 8.3.4
- h11: 0.14.0 → 0.16.0 (CVE fix)
- Plus 57 additional pinned packages

#### Performance Metrics
- Context detection: 2000ms+ → <200ms (10x improvement)
- API client code: 590 lines → 432 lines (27% reduction)
- Orchestration scripts: 367 lines → 59 lines (84% reduction)

#### Automated Security
- GitHub Dependabot: Active and creating PRs for vulnerabilities
- Security workflow: Running on all commits and PRs
- 5 security tools: Gitleaks, Semgrep, Trivy, Hadolint, Checkov

### Migration Notes

#### For Developers
- Run `pip install -r requirements.txt` to update to pinned versions
- Security tools (gitleaks, trivy, opengrep) now required for commits
- Context detection is now much faster (<200ms)

#### For Contributors
- GitHub Actions now runs security scans on all PRs
- Pre-commit hooks will block commits if security tools missing
- Install tools: `brew install gitleaks trivy semgrep`

---

## [1.1.0] - 2025-12-05

### Added

#### Hook-Based Skill Auto-Loading (NEW!)
- **Intelligent Context Detection**: Analyzes project files, dependencies, and tech stack to identify relevant technologies
- **Scoring Algorithm**: Ranks skills using weighted scoring (primary keywords: 10pts, technologies: 8pts, secondary keywords: 5pts)
- **SessionStart Hooks**: Auto-loads relevant skills once per session for both Claude Code and Gemini CLI
- **External Registry**: `.dev-aid/skills/registry/skills-index.json` with activation metadata for all skills
- **Universal Architecture**: Same auto-loading logic works across all AI providers

#### New Components
- **detect-context.sh**: Scans project for file patterns, config files (package.json, requirements.txt), and technology indicators
- **select-skills.sh**: Intelligent skill selector with scoring, conflict resolution, and dependency management
- **validate-bash-scripts.sh**: Compliance checker for bash-expert skill guidelines (32 validation checks) — _moved to `.dev-aid/skills/expert/bash-expert/validate.py`_
- **Claude SessionStart Hook**: `.dev-aid/providers/claude/.claude/hooks/session-start.sh` displays auto-loaded skills
- **Gemini SessionStart Hook**: `.dev-aid/providers/gemini/.gemini/hooks/session-start.sh` updates GEMINI.md once per session
- **Gemini Configuration**: `.dev-aid/providers/gemini/.gemini/settings.json` for hook management

#### Skills Registry
- **10 Initial Skills**: api-expert, bash-expert, devsecops-expert, typescript-expert, fastapi-expert, graphql-expert, docker-expert, python, rust, cicd-expert
- **Metadata Format**: Keywords, file patterns, technologies, confidence weights, dependencies, exclusions
- **Extensible Design**: Easy to add new skills with activation rules

### Changed
- **GEMINI.md Update Strategy**: Now updated ONCE at session start (not after every prompt) for better performance
- **Skills Architecture**: Enhanced from v2.0 (Shared Skills) to v3.0 (Hook-Based Auto-Loading + Shared Skills)
- **Documentation**: Comprehensive update to SKILLS-ARCHITECTURE.md with new sections on hook-based system

### Technical Details
- **Compliance**: All Bash scripts follow bash-expert skill guidelines with strict mode, proper quoting, input validation
- **Validation**: 32/32 checks passed for bash-expert compliance
- **JSON Validation**: All JSON files validated with jq
- **Testing**: End-to-end testing confirmed for both Claude and Gemini providers

### Benefits
- ✅ **Zero manual skill management** - Skills auto-load based on project context
- ✅ **GEMINI.md efficiency** - Updated once per session, not per prompt
- ✅ **Multi-provider consistency** - Same logic for Claude, Gemini, future providers
- ✅ **Intelligent selection** - Top 5 relevant skills chosen automatically
- ✅ **Respects limits** - Honors Claude's 2000-line Read tool limit

---

## [1.0.0] - 2025-12-04

### Added

#### Multi-AI Router (NEW!)
- **Challenger Mode**: Claude generates, Gemini reviews, with optional auto-refinement
- **Ensemble Mode**: Automatic routing to optimal AI based on task classification
- **Solo Mode**: Single model for predictable workflows
- **Cost Tracking**: Real-time cost monitoring with daily budgets and logging
- **Slash Commands**: `/dev-aid-router-challenger`, `/dev-aid-router-ensemble`, `/dev-aid-router-status`
- **Full API Integration**: Anthropic, Google, OpenAI clients with unified interface
- **Virtual Environment Support**: Complete dependency isolation with automated setup

#### Local Semantic Search (NEW!)
- **claude-context-local Integration**: 100% local RAG with $0 cost
- **EmbeddingGemma Model**: Google's embedding model for semantic search
- **MCP Native**: Works with Claude Code and Gemini CLI out of the box
- **Auto-indexing**: Git hooks for automatic codebase reindexing
- **Setup Scripts**: One-command installation (`.dev-aid/scripts/setup-rag.sh`)
- **Status Monitoring**: Check RAG health with `rag-status.sh`

#### Documentation
- **DEPENDENCY-ISOLATION.md**: Complete three-layer isolation architecture guide
- **STORAGE-LOCATIONS.md**: Where files are stored and why (5MB vs 2.7GB breakdown)
- **ROUTER-INSTALL.md**: Step-by-step router installation with isolation benefits
- **router/README.md**: Full implementation roadmap
- **VENV-INFO.md**: Virtual environment deep-dive (venv vs Anaconda)
- **Enhanced README**: Native integration positioning, benefits comparison tables

#### Infrastructure
- **VERSION File**: Semantic versioning for update tracking
- **CHANGELOG.md**: Release notes and version history
- **Update Mechanism**: `update-dev-aid.sh` script for safe upgrades
- **Enhanced .gitignore**: Runtime files, costs, logs properly excluded

### Changed
- **Product Positioning**: From "NOT a standalone CLI" to "works natively inside tools you use"
- **Router Implementation**: Bash scripts → Full Python package with API integration
- **Dependency Management**: Manual pip install → Automated venv setup with `setup-venv.sh`

### Security
- **Isolated Dependencies**: Router venv + RAG uv environment + system Python (zero pollution)
- **API Key Protection**: `.env` files properly ignored in Git
- **No System Pollution**: All packages in isolated environments

---

## Release Notes

### v1.0.0 - Initial Production Release

This is the first production-ready release of Dev-AID with complete multi-AI orchestration and local semantic search capabilities.

**Highlights**:
- ✅ 65 expert skills across 10+ domains
- ✅ Multi-AI routing with cost optimization
- ✅ 100% local RAG ($0 forever, private)
- ✅ Complete dependency isolation
- ✅ Automated security scanning (5 tools)
- ✅ Works with Claude Code, Cursor, Gemini CLI

**Breaking Changes**: None (first release)

**Migration Guide**: N/A (first release)

---

## Version History

- **1.0.0** (2025-12-04) - Initial production release

---

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for how to propose changes.

---

## Support

- **Documentation**: `.dev-aid/docs/`
- **Issues**: [GitHub Issues](https://github.com/Probably-Group/Dev-AID/issues)
