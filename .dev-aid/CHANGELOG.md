# Dev-AID Changelog

All notable changes to Dev-AID will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- **validate-bash-scripts.sh**: Compliance checker for bash-expert skill guidelines (32 validation checks)
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

## Upcoming Features (Planned)

### v1.1.0 (Q1 2025)
- [ ] Web dashboard for cost analytics
- [ ] Model performance benchmarking
- [ ] Custom routing rules via UI
- [ ] Multi-repository RAG support

### v1.2.0 (Q2 2025)
- [ ] LightRAG integration option
- [ ] LlamaIndex adapter
- [ ] Cloud RAG fallback
- [ ] Team cost allocation

---

## Contributing

See the repository documentation for how to propose changes.

---

## Support

- **Documentation**: `.dev-aid/docs/`
- **Issues**: [GitHub Issues](https://github.com/your-org/dev-aid/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/dev-aid/discussions)
