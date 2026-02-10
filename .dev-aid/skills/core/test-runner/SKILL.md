---
name: test-runner
description: "Auto-runs relevant tests on file save with smart test file mapping and fast feedback. Key capabilities: jest/vitest/pytest/cargo-test/go-test detection, changed-file-to-test mapping, watch mode, bail-on-failure. Use when editing test files or source code with tests. Do NOT use for files without test coverage, documentation, or config files."
version: 1.0.0
category: core
auto_load: true
token_budget: 250
triggers:
  - file_save
  - edit_complete
tools:
  - Bash
  - Read
  - Grep
---

# Test Runner - Compact

**Purpose**: Auto-run tests on file changes (fast feedback loop)

## Test Execution Strategy

### Detect Test Framework
- **JavaScript/TypeScript**: jest, vitest, mocha, ava
- **Python**: pytest, unittest, nose2
- **Rust**: cargo test
- **Go**: go test
- **Ruby**: rspec, minitest

### Run Relevant Tests Only
- Changed file: `user.ts` → Run: `user.test.ts`
- Test file: `auth.test.ts` → Run: Just this test
- Multiple changes → Run all affected tests

### Performance Optimization
- Use watch mode flags (`--onlyChanged`, `--bail`)
- Skip integration tests on file save
- Run full suite on demand only

## Output Format
```
✅ Tests Passed (12/12) - 1.2s
   user.test.ts: 5 passed
   auth.test.ts: 7 passed
```

```
❌ Tests Failed (2/12) - 1.5s
📍 user.test.ts:45 - Expected true, got false
📍 auth.test.ts:23 - TypeError: Cannot read property 'role'

💡 Fix tests before committing
```

## When to Skip
- No test files found
- `--no-test` flag in commit message
- File in `.testignore`

**Token Budget**: ~250 tokens
**Mode**: Non-blocking (informational only)
**Full Suite**: Run manually with `/test` command
