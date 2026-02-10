---
name: verification-gate
description: "Prevents false completion claims by requiring evidence for every done/fixed/finished assertion. Key capabilities: five-step verification, language-aware test/build/lint commands, exit code validation. Use when finishing tasks, claiming done, marking work complete. Do NOT use for in-progress work, exploration, or mid-task check-ins."
risk_level: low
version: 1.0.0
domain: process/quality
enforcement: strict
token_budget: 300
triggers:
  - completion_claim
  - "done"
  - "fixed"
  - "implemented"
  - "finished"
---

# Verification Gate

## 0. Anti-Hallucination Protocol

### 0.1 Quick Risk Assessment

**Risk Level**: LOW
**Key Risk**: False completion claims leading to broken code in production.

### 0.3 Enforcement Rules

**ABSOLUTE REQUIREMENT**: Evidence before claims, always.

**Forbidden Phrases** (trigger re-verification):
- "should pass" / "should work"
- "probably works" / "likely fixed"
- "Done!" / "Finished!" / "Complete!"
- "I believe this fixes..."
- "This should resolve..."

When detected → STOP → Run verification → Show evidence → Only then claim.

---

## 1. The Protocol

### 1.1 Five-Step Verification

```
┌─────────────────────────────────────────────────────────┐
│ 1. IDENTIFY what proves the claim                       │
│    → "Tests passing proves the bug is fixed"            │
├─────────────────────────────────────────────────────────┤
│ 2. RUN the verification command FRESH                   │
│    → Don't rely on cached results                       │
│    → Don't assume previous run still valid              │
├─────────────────────────────────────────────────────────┤
│ 3. READ the complete output                             │
│    → Check exit codes (0 = success)                     │
│    → Count failures/errors                              │
│    → Note warnings                                      │
├─────────────────────────────────────────────────────────┤
│ 4. VERIFY output confirms the claim                     │
│    → If not, state actual status with evidence          │
│    → Don't rationalize partial success                  │
├─────────────────────────────────────────────────────────┤
│ 5. CLAIM with evidence                                  │
│    → "Tests pass: 47 passed, 0 failed (exit code 0)"    │
│    → "Build succeeded: exit code 0, no warnings"        │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Language-Aware Commands

**Auto-detected based on project files (see references/language-commands.md)**

| Evidence Type | Python | TypeScript/JS | Rust | Go |
|--------------|--------|---------------|------|-----|
| Tests pass | `pytest -v` | `npm test` | `cargo test` | `go test ./...` |
| Build succeeds | `python -m py_compile` | `npm run build` | `cargo build` | `go build ./...` |
| Lint clean | `flake8 . && mypy .` | `npm run lint` | `cargo clippy` | `golangci-lint run` |
| Types valid | `mypy .` | `tsc --noEmit` | (built-in) | (built-in) |

**Detection Priority**:
1. Check `package.json` → Node.js project
2. Check `Cargo.toml` → Rust project
3. Check `go.mod` → Go project
4. Check `pyproject.toml` or `setup.py` → Python project
5. Check `requirements.txt` → Python project

### 1.3 Evidence Requirements by Task

| Task Type | Required Evidence |
|-----------|-------------------|
| Bug fix | Test that reproduced bug now passes |
| New feature | New tests + all existing tests pass |
| Refactor | All tests pass, no behavior change |
| Build fix | Build command exits 0 |
| Lint fix | Linter exits 0, 0 errors |
| Type fix | Type checker exits 0 |

---

## 2. Integration with Dev-AID

### 2.1 Router Integration
When verification runs, use **challenger mode** if configured:
- Primary model runs verification
- Secondary model confirms output interpretation
- Disagreement → re-run with human review

### 2.2 Test Runner Integration
Connect to `test-runner` core skill for automatic test execution.

### 2.3 Metrics
Log verification metrics:
- `verification_tokens_used`
- `verification_commands_run`
- `false_completion_prevented`

---

## 3. Common Evasion Patterns (Block These)

❌ "I verified mentally that..."
❌ "Based on my analysis, this should..."
❌ "The changes look correct, so..."
❌ "I'm confident this fixes..."
❌ "Testing isn't necessary because..."

**Response**: "Show me the command output."

---

## 4. Claim Format

### Correct Claims (with evidence)
```
✅ "Tests pass: 47 passed, 0 failed, 0 skipped (exit code 0)"
✅ "Build successful: compiled in 2.3s, 0 warnings (exit code 0)"
✅ "Lint clean: 0 errors, 0 warnings across 23 files"
✅ "Type check passed: 156 modules checked, no errors"
```

### Incorrect Claims (block these)
```
❌ "Done! The feature is implemented."
❌ "Fixed. This should work now."
❌ "I've completed the task."
❌ "The bug is resolved."
```

---

## 5. Rollback Procedures

### Triggers
- Verification command produces false positives (reports pass when code is broken)
- Verification runs modify project state (e.g., build artifacts corrupt working directory)
- Wrong project type detected, causing incorrect commands to run

### Steps
- `git checkout -- .` to discard any file changes caused by verification commands
- `git clean -fd` to remove build artifacts or generated files if verification polluted the tree
- For Python: `rm -rf __pycache__ .pytest_cache .mypy_cache` to clear caches
- For Node: `rm -rf node_modules/.cache dist/` to clear build caches

### Reset
- Re-run verification with `--verbose` flag to inspect actual command output
- Manually run each verification step individually to isolate which check is misbehaving
- If project type detection is wrong, specify the project directory explicitly

### Abandon vs. Retry
- **Retry** if verification fails due to environment issues (missing tool, wrong Python version)
- **Retry** after installing missing tools (e.g., `pip install flake8 mypy`)
- **Abandon** verification gate if the project has no test suite yet — focus on writing tests first
- **Abandon** if the project type is genuinely unsupported — document manually instead

---

## 6. Scripts

- `scripts/verify-completion.sh` — Auto-detect project type and run tests, lint, and type checks to verify completion claims

---

## 7. References

For detailed information, see:
- `references/language-commands.md` - Complete per-language verification commands
