# What's New in Dev-AID v1.3.0

## New Provider Support

### Codex CLI Integration (NEW!)
OpenAI's Codex CLI is now fully supported as the fourth AI coding tool:
- **Zero-Conversion Skills**: Same SKILL.md format as Claude Code (YAML frontmatter + Markdown)
- **Symlink-Based Sharing**: All 85 Dev-AID skills work out of the box
- **AGENTS.md Generation**: Auto-generates context file from project detection
- **Session-Start Hook**: Auto-loads relevant skills at session start
- **ROI**: Use the same skills across Claude Code, Gemini CLI, Cursor, and Codex CLI
- Documentation: [Codex Provider README](.dev-aid/providers/codex/README.md)

**Supported AI Tools (4 total):**
- Claude Code (Anthropic)
- Gemini CLI (Google)
- Cursor
- Codex CLI (OpenAI) - NEW!

---

## Performance & Architecture
- **10x Faster Context Detection**: Optimized from 2s+ to <200ms with new Python implementation
- **Dynamic Skill Loading**: Patterns now loaded from skills-index.json (no hardcoded lists)
- **Code Reduction**: 84% reduction in orchestration scripts (367 → 59 lines)

## Security Enhancements
- **Pinned Dependencies**: All 63 Python packages now use exact versions for reproducible builds
- **Active Security Scanning**: GitHub Actions now running automated scans on all commits/PRs
- **CVE Patched**: Updated h11 to fix critical HTTP request smuggling vulnerability
- **Fail-Closed Hooks**: Pre-commit now blocks when security tools missing (no more silent bypasses)
- **Checksum Verification**: RAG installer now verifies SHA256 before execution

## New Features

### Cross-Platform CI Support
- **Windows, macOS, Linux**: Full GitHub Actions support across all major platforms
- **Matrix Testing**: Automated tests run on ubuntu-22.04, windows-latest, and macos-latest
- **Platform-Specific Workflows**: Handles OS differences automatically (venv activation, path separators)
- **Parallel Execution**: All platforms test concurrently for faster feedback
- **ROI**: Wider adoption + earlier platform-specific bug detection
- Documentation: [Cross-Platform CI Guide](.github/workflows/pr-check.yml)

### End-to-End Testing Framework
- **Complete CLI Workflow Testing**: pytest-based E2E tests for real-world scenarios
- **Config Validation**: Tests config loading, cost tracking, task classification
- **Script Integration**: Validates all core scripts for syntax and executability
- **Memory Bank Testing**: Ensures persistent context system works correctly
- **Fast by Default**: Slow tests marked and skipped in CI (use `-m "not slow"`)
- **ROI**: Prevents regressions + ensures release quality
- Tests: [E2E Test Suite](.dev-aid/orchestration/tests/test_e2e.py)

### TOON Format Integration (Fully Implemented)
- **Token Reduction**: 40-60% fewer tokens vs JSON in LLM prompts
- **Better Accuracy**: 74% vs JSON's 70% (validated benchmarks)
- **Pure Python**: Uses `toon-format` package (no Node.js dependency)
- **Complete SDK**: Full encode/decode/conversion utilities
- **Config Loader Support**: Automatic .toon file detection and parsing
- **Migration Tool**: One-command JSON → TOON conversion (`migrate-to-toon.sh`)
- **21 Unit Tests**: 100% pass rate, comprehensive test coverage
- **Roundtrip Preservation**: Perfect data fidelity guaranteed
- **Ready to Use**: Skills can output TOON, configs support TOON format
- **ROI**: $30-50K/year token savings for 100-developer team
- Quick Start: [TOON Quick Start Guide](.dev-aid/docs/TOON-QUICK-START.md)
- Full Details: [TOON Implementation Plan](.dev-aid/docs/TOON-IMPLEMENTATION-PLAN.md)
- Code: [TOON Module](.dev-aid/orchestration/toon/)

### Local CI Validation System
- **Prevent CI Failures**: Run same checks locally that CI runs on GitHub Actions
- **Auto-Fix on Commit**: Pre-commit hook auto-formats code (Black, isort) and blocks errors
- **Fast Feedback**: Get results in 10-30s locally vs 2-5 min waiting for CI
- **Slash Command**: `/validate-ci` for quick access from Claude Code
- **Smart Detection**: Auto-detects venv and Node.js, provides helpful error messages
- **ROI**: $83,300/year for 100 devs (prevents failed builds, faster iteration)
- Scripts: `run-local-ci-checks.sh`, `setup-better-git-hooks.sh`
- Documentation: [Local CI Validation Guide](.dev-aid/docs/LOCAL-CI-VALIDATION.md)

### Smart Context Initialization
- **Progressive Disclosure Detection**: Automatically detects existing `.claude/rules/` directories and `@` file references
- **Preserves Your Structure**: If you already use progressive disclosure, Dev-AID enhances without overwriting
- **Quality Assessment**: Analyzes existing CLAUDE.md for completeness, placeholders, and structure
- **Quality Levels**: Classifies files as `good`, `incomplete`, `draft`, or `poor` with actionable feedback
- **Enhanced Templates**: Provider templates now include Code Quality Standards, Security (OWASP Top 10), and Testing Requirements
- **Multi-Provider Support**: Works with Claude, Gemini, and OpenAI context files
- **8-Step Smart Migration**: Backup → PD Detection → Quality → Validate → Merge → Split/Skip → Symlink → Report
- **ROI**: Prevents context duplication, preserves team customizations, ensures consistent AI guidance
- Scripts: `.dev-aid/scripts/lib/claude-md-init.sh`, `provider-context-init.sh`

### Deep Research / External Brain MCP
- **Multi-Provider Research**: Gemini Deep Research, Perplexity Sonar, and Tavily integration
- **Smart Query Routing**: Auto-classifies queries (factual/exploratory/technical) and selects optimal provider
- **Semantic Caching**: SQLite-based cache with 70% similarity threshold, 24-48h TTL
- **MCP Server**: Full Model Context Protocol implementation with 6 research tools
- **CLI Tool**: `dev-aid-research search|quick|deep "query"` for direct access
- **Router Integration**: Auto-fallback to external research when local context insufficient
- **ROI**: Access to real-time information, reduces hallucinations, improves research accuracy
- Module: `.dev-aid/deep-research/`
- Skill: `deep-research-expert` (auto-activates on research keywords)

---

### Safe Update System
Never lose customizations while staying current:
- **Interactive Conflict Resolution**: 5-option menu (keep/take/merge/diff/skip) for each modified file
- **Protected Paths**: Never overwrites `.env`, memory-bank, custom skills, RAG indices
- **Automatic Rollback**: Error trap restores from backup on failures
- **SHA256 Verification**: Checksum validation prevents MITM attacks
- **Weekly Auto-Check**: Silent CLI hooks with 7-day cache (respects GitHub rate limits)
- **Breaking Change Detection**: Warns about major version bumps with release notes
- Scripts: `update-dev-aid.sh`, `check-updates.sh`, `rollback.sh`, `setup-update-hooks.sh`
- Documentation: [Complete Guide](.dev-aid/docs/UPDATE-SYSTEM-GUIDE.md)

### Intelligent Automation System
Complete automation for issues, conflicts, and workflows:

**Issue Resolution** (`dev-aid-resolve-issue`): AI analyzes GitHub issues and proposes solutions
- Safety checks block security/critical issues
- Multi-mode orchestration (solo/ensemble/challenger)
- Dry-run mode for safe previewing
- Saves 15-45 minutes per issue

**Conflict Resolution** (`dev-aid-fix-conflicts`): Smart merge conflict resolution
- Multiple strategies: smart, ours, theirs
- Understands both sides of conflict
- Preserves intent from both branches
- Saves 10-30 minutes per conflict

**Git Hooks**: Automatic conflict detection locally
- Post-merge hook detects conflicts
- Optional auto-resolution
- Helpful guidance and tips

**GitHub Actions Workflows**: Automated triage, conflict detection, and fixing
- Auto-triage new issues with labels
- Detect PR conflicts automatically
- Optional automated issue fixing

Documentation: [Complete Guide](.dev-aid/docs/AUTOMATION-README.md)

### Auto-Generate CI/CD Workflows
Production-ready GitHub Actions from project detection:
- Supports Node.js, Python, Rust, Go with auto-detection
- Security by default: Gitleaks + Trivy included
- Detects package managers: npm/yarn/pnpm/bun, pip/poetry/uv, cargo, go
- Usage: `.dev-aid/scripts/generate-ci.sh`

### Refactoring Expert Skill
522-line comprehensive guide for safe code refactoring:
- Safety-first methodology with mandatory testing
- Strangler Fig pattern for legacy modernization
- Auto-activates on keywords: refactor, rewrite, legacy, technical debt

### RAG Vendoring Support
Documentation and tooling for dependency stability:
- Fork and maintain your own copy
- Environment variable support for custom repositories

### VCR/Replay Testing
Cost-free AI client testing with recorded HTTP interactions:
- Record once with real API keys, replay forever in CI
- Automatic API key sanitization
- Fast, deterministic, $0 cost testing

### PR Check Workflow
Fast feedback loop for pull requests:
- Path-based filtering (runs only on relevant changes)
- Python/Bash linting, type checking, unit tests
- Saves GitHub Actions minutes

### Release Gate Workflow
Deep validation before releases:
- Cross-platform tests (Ubuntu, MacOS, Windows)
- Comprehensive security scans
- Documentation link validation

### Architecture Mapper
Visual codebase understanding with Mermaid diagrams:
- Auto-generates class diagrams, dependency graphs, C4 components
- Supports Python (AST) and TypeScript/JavaScript (regex)
- Usage: `.dev-aid/scripts/map-architecture.sh`

### Test Data Factory
Realistic mock data generation from schemas:
- Supports JSON Schema, Pydantic, TypeScript interfaces
- Output formats: JSON, CSV, SQL INSERT statements
- Realistic data pools (names, emails, addresses, phones)
- Usage: `.dev-aid/scripts/fabricate-data.sh schema.json`

### Living README
Documentation drift detector:
- Detects mismatches between README and project reality
- Checks package managers, scripts, Docker ports
- Actionable fix suggestions
- Usage: `.dev-aid/scripts/sync-docs.sh`

### Interactive Guide
Feature discovery and best practices:
- Menu-driven interface for all Dev-AID capabilities
- Context-aware recommendations
- Complete command catalog
- Usage: `.dev-aid/scripts/dev-aid-guide.sh`

### PR Storyteller
Auto-generate semantic PR descriptions:
- Analyzes git diff and commit history
- Structured template with verification checklist
- Usage: `.dev-aid/scripts/draft-pr.sh > pr.md`

### Onboarding Buddy
Interactive developer setup:
- Environment checks and project detection
- Shows correct install commands
- Lists available Dev-AID features
- Usage: `.dev-aid/scripts/onboard.sh`

---

## Code Quality
- **DRY Improvements**: Eliminated 158 lines of duplicate code in API clients
- **Decorator Pattern**: New `@track_api_call` for centralized error handling and timing
- **Dynamic Package Testing**: Setup script now parses requirements.txt automatically

---

**See full changelog:** [CHANGELOG.md](./.dev-aid/CHANGELOG.md)

**Issues resolved:** #17-24, #26-28, #31-42 (26 total issues)
