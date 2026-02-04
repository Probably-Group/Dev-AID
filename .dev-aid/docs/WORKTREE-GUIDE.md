# Git Worktree Isolation Guide

## Overview

Git worktrees allow parallel development by creating multiple working directories from a single repository. Dev-AID enhances this with:

- **Scope declarations** - Document what each worktree modifies
- **Architecture locks** - Protect critical code during refactoring
- **Conflict detection** - Identify potential merge issues early

## Quick Start

### Create a Worktree

```bash
# Basic usage
.dev-aid/scripts/create-worktree.sh feature/new-auth

# With scope declaration
.dev-aid/scripts/create-worktree.sh feature/new-auth --scope "src/auth,tests/auth"

# From specific base branch
.dev-aid/scripts/create-worktree.sh feature/new-auth develop
```

### Check for Conflicts

```bash
# Quick conflict check
.dev-aid/scripts/sync-worktrees.sh --check

# Detailed view
.dev-aid/scripts/sync-worktrees.sh --verbose

# List all worktrees
.dev-aid/scripts/sync-worktrees.sh --list
```

### Clean Up

```bash
# Remove a worktree when done
git worktree remove .worktrees/feature/new-auth

# Or force remove if needed
git worktree remove --force .worktrees/feature/new-auth
```

## Scope Declarations

When you create a worktree, Dev-AID creates a `SCOPE.md` file documenting:

- Branch name and creation date
- Description of the work
- Affected file paths
- Guidelines for staying within scope

### Example SCOPE.md

```markdown
# Worktree Scope Declaration

**Branch**: feature/new-auth
**Created**: 2024-02-01T10:30:00Z

## Description
Implementing OAuth2 authentication with Google provider

## Affected Paths
- `src/auth/`
- `src/middleware/auth.ts`
- `tests/auth/`

## Guidelines
1. Stay within scope
2. Update if scope changes
3. Sync before merging
```

## Architecture Locks

For major refactoring, protect critical paths with locks:

### Creating a Lock

```bash
# Create lock file
cat > .dev-aid/architecture-locks/auth-refactor.lock << 'EOF'
# Owner: @yourname
# Expires: 2024-02-15
# Reason: Major auth system refactor

src/auth/
src/middleware/auth.ts
tests/auth/
EOF

# Commit the lock
git add .dev-aid/architecture-locks/auth-refactor.lock
git commit -m "chore: lock auth paths for refactor"
```

### Lock Behavior

When someone tries to create a worktree with overlapping scope:

```
$ .dev-aid/scripts/create-worktree.sh feature/login --scope "src/auth/login.ts"

[warn] Architecture locks detected for requested scope:
  - auth-refactor: src/auth/

Continue despite architecture locks? [y/N]
```

## Conflict Prevention Workflow

### Before Starting Work

1. **Check existing worktrees**: `sync-worktrees.sh --list`
2. **Check for locks**: Look at `.dev-aid/architecture-locks/`
3. **Declare scope**: Use `--scope` flag when creating worktree

### During Development

1. **Stay within scope**: Only modify declared paths
2. **Update scope if needed**: Edit SCOPE.md if you need more files
3. **Check periodically**: Run `sync-worktrees.sh --check`

### Before Merging

1. **Sync check**: `sync-worktrees.sh --check`
2. **Rebase on latest**: `git pull --rebase origin main`
3. **Resolve conflicts**: Address any detected overlaps
4. **Remove worktree**: Clean up after merge

## Best Practices

### Do

- Declare scope upfront
- Keep worktrees focused (one feature/fix each)
- Run conflict checks before PRs
- Remove worktrees promptly when done
- Communicate with team about locks

### Don't

- Create worktrees for tiny changes (just use branches)
- Lock too broadly (be specific)
- Keep stale worktrees lying around
- Ignore conflict warnings

## Integration with AI Coding

When using AI coding assistants (Claude Code, Codex, Gemini):

1. **Start in worktree**: `cd .worktrees/feature/new-auth`
2. **AI sees scope**: The SCOPE.md helps AI understand boundaries
3. **Isolated changes**: AI can't accidentally affect other work
4. **Clean history**: Each worktree has its own commit history

## Troubleshooting

### "Worktree already exists"

```bash
# Check existing worktrees
git worktree list

# Remove if stale
git worktree remove .worktrees/old-branch
```

### "Branch already exists"

The script will use the existing branch. If you want a fresh start:

```bash
git branch -D feature/old-branch
.dev-aid/scripts/create-worktree.sh feature/new-branch
```

### "Cannot remove worktree with changes"

```bash
# Commit or stash changes first
cd .worktrees/feature/branch
git stash

# Then remove
cd /path/to/main/repo
git worktree remove .worktrees/feature/branch
```

## Directory Structure

```
project/
├── .worktrees/                    # All worktrees live here
│   ├── feature-auth/              # Worktree directory
│   │   ├── SCOPE.md               # Scope declaration
│   │   ├── src/                   # Working copy
│   │   └── ...
│   └── fix-login-bug/
│       ├── SCOPE.md
│       └── ...
├── .dev-aid/
│   ├── architecture-locks/        # Lock files
│   │   ├── README.md
│   │   └── auth-refactor.lock
│   └── scripts/
│       ├── create-worktree.sh
│       └── sync-worktrees.sh
└── src/                           # Main working copy
```
