# Testing Status

The orchestration module enforces a minimum 80% coverage threshold via the
pytest pre-commit hook. Tests are run using the project-local virtual
environment at `.dev-aid/orchestration/venv/`.

## Running Tests

```bash
cd .dev-aid/orchestration

# Full suite with coverage (matches pre-commit hook behaviour)
venv/bin/python -m pytest tests/ -v --cov=router --cov-fail-under=80

# Quick run, no coverage
venv/bin/python -m pytest tests/ -v
```

## Test Organization

- `tests/test_api_clients/` - Provider adapter unit tests
- `tests/test_config_loader*.py` - Configuration loading and validation
- `tests/test_context_builder*.py` - Memory bank / context assembly
- `tests/test_security.py` - Input validation, path traversal, injection defenses
- `tests/test_task_classifier.py` - Ensemble mode task classification
- `tests/test_validators.py` - Pydantic request validators
- `tests/test_memory_bank*.py` - On-demand loading, staleness, section extraction
- `tests/test_mcp.py` - MCP subprocess environment isolation

## Known Environmental Skips

A small number of tests skip in sandboxed environments:

- `test_update_system.py` — GitHub API tests require outbound DNS.
  Workaround: tests are non-critical and can be skipped with standard
  pytest markers; CI runs them normally.

All other tests are expected to pass cleanly before a commit is accepted.

---
Last updated: 2026-04-08
