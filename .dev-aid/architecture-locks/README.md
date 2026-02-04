# Architecture Locks

This directory contains architecture lock files that protect critical code paths from concurrent modifications.

## Purpose

Architecture locks prevent multiple worktrees/branches from modifying the same critical areas simultaneously, reducing merge conflicts and accidental breakages.

## How It Works

1. Create a `.lock` file for areas under active refactoring
2. The `create-worktree.sh` script checks locks before allowing scope overlap
3. Locks should be removed when refactoring is complete

## Creating a Lock

```bash
# Create a lock for auth system refactoring
echo "src/auth/" > .dev-aid/architecture-locks/auth-refactor.lock
echo "src/middleware/auth.ts" >> .dev-aid/architecture-locks/auth-refactor.lock
```

## Lock File Format

Each `.lock` file contains paths (one per line) that should not be modified by other worktrees:

```
# auth-refactor.lock
# Active until: 2024-02-15
# Owner: @username

src/auth/
src/middleware/auth.ts
src/types/auth.ts
tests/auth/
```

## Example Workflow

1. Developer A starts auth refactor:
   ```bash
   echo "src/auth/" > .dev-aid/architecture-locks/auth-refactor.lock
   ./dev-aid/scripts/create-worktree.sh feature/auth-oauth --scope "src/auth"
   ```

2. Developer B tries to work on related code:
   ```bash
   ./dev-aid/scripts/create-worktree.sh feature/login-ui --scope "src/auth/login.ts"
   # Warning: Architecture lock detected for src/auth/
   ```

3. Developer B can:
   - Wait for the lock to be released
   - Coordinate with Developer A
   - Work on non-locked areas

4. When refactoring is done, Developer A removes the lock:
   ```bash
   rm .dev-aid/architecture-locks/auth-refactor.lock
   ```

## Best Practices

- Use locks for major refactoring, not small fixes
- Include an expiration date in lock files
- Commit lock files so the team sees them
- Remove locks promptly when done
- Keep lock scope as narrow as possible
