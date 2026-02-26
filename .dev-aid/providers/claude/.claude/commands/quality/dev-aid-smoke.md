---
name: dev-aid-smoke
description: Run smoke tests and report results
category: quality
author: Dev-AID
version: 1.0.0
allowed-tools: Bash(./scripts/*:*), Bash(bash scripts/*:*), Read
---

# Run Smoke Tests

Run all smoke test scripts and report results.

## Protocol

1. Find all smoke test scripts:
   ```bash
   ls scripts/smoke-*.sh scripts/validate-*.sh scripts/verify-*.sh 2>/dev/null
   ```

2. Run each script and capture output:
   ```bash
   bash scripts/<script>.sh
   ```

3. For each result:
   - Report PASS/FAIL/WARN counts
   - Identify root causes for any failures
   - Suggest specific fixes

4. If a fix is straightforward (missing dependency, config issue), offer to apply it.

5. Summarize overall health at the end.

$ARGUMENTS
