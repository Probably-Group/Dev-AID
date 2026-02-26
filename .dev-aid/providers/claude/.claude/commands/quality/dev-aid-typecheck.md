---
name: dev-aid-typecheck
description: Run TypeScript type checking and fix type errors
category: quality
author: Dev-AID
version: 1.0.0
allowed-tools: Bash(npx tsc:*), Bash(npx:*), Read, Edit, Grep, Glob
---

# TypeScript Type Checking

Run TypeScript compiler in check mode and fix any type errors.

## Protocol

1. Run type checking:
   ```bash
   npx tsc --noEmit
   ```

2. If errors found:
   - Group errors by file
   - Read each affected file
   - Apply type-safe fixes (prefer narrowing over `as` assertions)
   - Re-run to verify all errors resolved

3. Common fixes:
   - Missing types → add proper type annotations
   - `any` usage → narrow to specific types
   - Null checks → add optional chaining or guards
   - Import types → use `import type` where appropriate

4. Report summary of fixes applied.

$ARGUMENTS
