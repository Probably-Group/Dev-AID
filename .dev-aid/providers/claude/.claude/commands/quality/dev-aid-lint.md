---
name: dev-aid-lint
description: Run linters and auto-fix issues
category: quality
author: Dev-AID
version: 1.0.0
allowed-tools: Bash(ruff:*), Bash(eslint:*), Bash(prettier:*), Bash(gofmt:*), Bash(rustfmt:*), Bash(shellcheck:*), Bash(npx:*), Bash(cargo:*), Read, Edit
---

# Run Linters with Auto-Fix

Run the appropriate linters for this project and fix issues automatically.

## Commands by Language

- **Python**: `ruff check --fix . && ruff format .`
- **TypeScript/JS**: `npx eslint --fix . && npx prettier --write .`
- **Go**: `gofmt -w . && goimports -w .`
- **Rust**: `cargo fmt`
- **Shell**: `shellcheck scripts/*.sh`

## Protocol

1. Detect the project language(s) from config files (pyproject.toml, package.json, go.mod, Cargo.toml)
2. Run the appropriate linters with auto-fix
3. Report any issues that require manual intervention
4. Summarize what was fixed

$ARGUMENTS
