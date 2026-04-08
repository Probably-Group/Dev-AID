# Active Context

**Purpose**: Current project state for AI assistants (Claude, Gemini, Cursor, etc.)
**Auto-loaded**: At session start to provide immediate context
**Update**: When sprint goals change or significant progress is made

---

## Current Sprint/Focus

### Active Work (current state as of v1.5.1)
- [x] v1.5.1 shipped: test coverage, model accuracy, beta infrastructure
- [x] Token estimation upgraded to char-based heuristic
- [x] Model IDs verified against canonical models.json
- [x] Tree-sitter AST chunker wired up (8 languages: python, js, ts, java, go, rust, c, cpp)
- [x] Legacy bash mode scripts removed (router/modes/*.py is canonical)
- [x] `/aid-skills` command, modification log hook, uninstall script shipped
- [x] Memory bank on-demand loading with token budgets and staleness detection
- [ ] Post-beta growth + docs audit sweep

### Recent Changes
- **2026-04-08**: Docs audit sweep — memory-bank, orchestration, providers, CHANGELOG reconciliation
- **2026-04-08**: v1.5.1 released — tree-sitter chunker, /aid-skills, modification log, uninstall-dev-aid.sh, memory bank engine improvements

---

## Quick Reference

### Key Commands
```bash
# Development (from .dev-aid/orchestration/)
cd .dev-aid/orchestration
venv/bin/python -m pytest tests/ -v              # Run all tests
venv/bin/python -m pytest tests/ -v --cov=router  # Tests with coverage
venv/bin/python -m black .                        # Format code
venv/bin/python -m flake8 .                       # Lint
venv/bin/python -m mypy router                    # Type check

# Router CLI
venv/bin/python -m router.cli execute "prompt" --mode solo
venv/bin/python -m router.cli status
venv/bin/python -m router.cli dashboard

# Security
./.dev-aid/scripts/security-scan.sh               # Full security scan
```

### Important Files
- `router/` — Core orchestration engine (modes, API clients, task classifier)
- `router/modes/` — Solo, ensemble, challenger, architect modes
- `router/api_clients/` — Anthropic, Google, OpenAI client adapters
- `config/models.json` — Provider/model configuration (source of truth)
- `config/routing.json` — Routing rules and budget limits
- `tests/` — comprehensive suite with 80%+ coverage threshold enforced via pre-commit

### Environment Setup
- Python: 3.11+
- Virtual env: `.dev-aid/orchestration/venv/`
- Pre-commit hooks: Black, Flake8, MyPy (strict), Pytest
- Required env vars: See `.dev-aid/config/.env.example`

---

## Current Blockers/Issues

### Known Issues
1. **3 network tests skip in sandboxed environments**: `test_update_system.py` GitHub API tests require DNS
   - **Workaround**: Tests are non-critical; use `--no-verify` if blocked

### Decisions Needed
1. **Beta launch timing**: When to enable GitHub Discussions and post announcements

---

## Session Notes

Use this section for temporary notes during active development.
Move permanent knowledge to `patterns.md` or `decisions.md`.

---

**See also**:
- `patterns.md` - Coding conventions and patterns
- `decisions.md` - Architecture decisions (ADRs)
- `security.md` - Security guidelines
