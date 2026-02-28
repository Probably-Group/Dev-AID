# Architecture Decision Records (ADRs)

**Purpose**: Document architectural decisions so AI assistants understand WHY things are built this way
**Used by**: Claude, Gemini, Cursor, and other AI coding assistants
**Update**: When significant technical decisions are made

---

## Quick Reference

| ADR | Decision | Status |
|-----|----------|--------|
| 001 | Python venv isolation | Accepted |
| 002 | Open-source CLI-only (no SaaS) | Accepted |
| 003 | TOON format for token reduction | Accepted |
| 004 | Multi-AI routing with ensemble/challenger | Accepted |
| 005 | Pre-commit hooks for quality enforcement | Accepted |
| 006 | Monorepo structure under `.dev-aid/` | Accepted |

---

## Decisions

### ADR-001: Python venv isolation

**Date**: 2025-06-15
**Status**: Accepted

#### Context
Dev-AID's orchestration module depends on multiple Python packages (pydantic, anthropic SDK, google-generativeai, openai, rich, typer). Installing these globally risks version conflicts with user projects.

#### Decision
Use a project-local virtual environment at `.dev-aid/orchestration/venv/`. All test and lint commands run through `venv/bin/python`.

#### Alternatives Considered
- **Global pip install**: Rejected — pollutes user's Python environment, version conflicts
- **Docker**: Rejected — too heavy for a CLI tool, adds friction
- **Poetry/pipenv**: Rejected — adds another dependency; plain venv is sufficient

#### Consequences
- **Positive**: Zero conflict with user's Python; reproducible environment; easy to recreate
- **Negative**: Slightly larger disk footprint; users must activate venv for manual commands

---

### ADR-002: Open-source CLI-only distribution (no SaaS)

**Date**: 2025-07-01
**Status**: Accepted

#### Context
Dev-AID could be distributed as a SaaS platform, a VS Code extension, or a local CLI tool. The target audience is developers who already use AI coding assistants and want multi-AI orchestration.

#### Decision
Distribute as an open-source CLI tool that integrates into existing workflows (Claude Code, Cursor, Windsurf) via slash commands and MCP servers. No hosted backend.

#### Alternatives Considered
- **SaaS platform**: Rejected — requires hosting, adds latency, users distrust proxying API keys
- **VS Code extension only**: Rejected — excludes Cursor, Windsurf, terminal-based workflows

#### Consequences
- **Positive**: Users keep their API keys local; zero hosting cost; works with any AI assistant
- **Negative**: No centralized analytics; monetization limited to sponsorship and affiliates

---

### ADR-003: TOON format for token reduction

**Date**: 2025-09-10
**Status**: Accepted

#### Context
Memory bank files and configuration are injected into AI context windows. JSON is verbose and wastes tokens. We need a compact serialization format.

#### Decision
Use TOON (Token-Optimized Object Notation) — a custom compact format that reduces token usage by 30-50% compared to JSON while remaining human-readable.

#### Alternatives Considered
- **YAML**: Rejected — ambiguous parsing, whitespace-sensitive, not significantly smaller
- **MessagePack/CBOR**: Rejected — binary, not human-readable, harder to debug
- **Just use JSON**: Rejected — wastes tokens at scale

#### Consequences
- **Positive**: Significant token savings for large configs; dual JSON/TOON support
- **Negative**: Custom format requires encoder/decoder; learning curve for contributors

---

### ADR-004: Multi-AI routing with ensemble/challenger modes

**Date**: 2025-08-01
**Status**: Accepted

#### Context
Different AI models excel at different tasks (Gemini for massive context, Claude for code, GPT for docs). Users shouldn't have to manually choose models per task.

#### Decision
Implement three orchestration modes:
- **Solo**: Single model, user's choice
- **Ensemble**: Task classifier routes to best model automatically
- **Challenger**: Primary model generates, secondary reviews for quality

#### Alternatives Considered
- **Single-model only**: Rejected — doesn't leverage multi-provider advantage
- **Automatic only**: Rejected — users want control over when to use multi-model

#### Consequences
- **Positive**: Optimal model for each task; quality gate via challenger review
- **Negative**: Higher cost in challenger mode (2x API calls); complexity in routing logic

---

### ADR-005: Pre-commit hooks for quality enforcement

**Date**: 2025-10-15
**Status**: Accepted

#### Context
The orchestration module has grown to 2900+ lines with 1300+ tests. Manual quality checks are unreliable, especially with AI-assisted development generating code quickly.

#### Decision
Enforce quality via pre-commit hooks: Black (formatting), Flake8 (linting), MyPy strict (type checking), Pytest with 80% coverage minimum.

#### Alternatives Considered
- **CI-only checks**: Rejected — feedback loop too slow; broken code gets committed
- **Manual review**: Rejected — doesn't scale with AI-generated code velocity

#### Consequences
- **Positive**: Every commit is formatted, typed, and tested; catches issues immediately
- **Negative**: Commits take 30-60s longer; occasional false positives from MyPy strict

---

### ADR-006: Monorepo structure under `.dev-aid/`

**Date**: 2025-06-01
**Status**: Accepted

#### Context
Dev-AID has multiple components: orchestration router, local search, deep research, scripts, config, memory bank. These could be separate repos or a monorepo.

#### Decision
Single repo with all components under `.dev-aid/` directory. The dot-prefix keeps it hidden from normal directory listings and signals it's tooling infrastructure.

#### Alternatives Considered
- **Separate repos**: Rejected — adds complexity for users; cross-component changes require multi-repo PRs
- **Top-level directories**: Rejected — clutters the user's project root

#### Consequences
- **Positive**: Single clone; atomic cross-component changes; simple dependency management
- **Negative**: Repo size grows; need clear directory structure to avoid confusion

---

**AI Instructions**: When working on this codebase:
- Check this file for relevant decisions before suggesting architectural changes
- If a suggestion conflicts with an ADR, explain the conflict
- Propose new ADRs for significant changes rather than just making them
