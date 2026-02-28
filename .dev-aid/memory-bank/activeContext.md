# Active Context

**Purpose**: Current project state for AI assistants (Claude, Gemini, Cursor, etc.)
**Auto-loaded**: At session start to provide immediate context
**Update**: When sprint goals change or significant progress is made

---

## Current Sprint/Focus

### Active Work
- [x] v1.6 improvements: test coverage, model accuracy, growth prep
- [x] Token estimation upgraded to char-based heuristic
- [x] Model IDs verified and updated to February 2026
- [ ] Beta launch preparation

### Recent Changes
- **2026-02-28**: v1.6 shipped — model IDs updated, token estimation improved, memory bank populated
- **2026-02-28**: v1.5.1 complete — 1301 tests at 89% coverage, RAG integration done

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
- `tests/` — 1300+ tests with 80%+ coverage threshold

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
