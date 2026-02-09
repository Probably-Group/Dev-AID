---
name: dev-aid-commit-plan
description: Plan atomic commits from unstaged changes (prevents mega-commits)
category: productivity
version: 1.0.0
author: Dev-AID Team (https://probably.group)
---

# Commit Planner - Atomic Commit Guide

Analyzes unstaged changes and proposes logical, atomic commits.

## Purpose

Prevent "mega-commits" by identifying distinct logical changes:
- Features should be separate commits
- Bug fixes should be separate commits
- Refactorings should be separate commits
- Each commit should be self-contained and reversible

## Task

1. **Analyze unstaged changes:**
   ```bash
   git status
   git diff --stat
   git diff
   ```

2. **Identify logical groupings:**
   Analyze files and changes to detect:
   - **Feature additions** (new files, new functionality)
   - **Bug fixes** (fixes, error handling)
   - **Refactorings** (code reorganization, no behavior change)
   - **Tests** (test files for above changes)
   - **Documentation** (README, docs, comments)

3. **Group changes by:**
   - **Semantic cohesion**: Changes that belong together logically
   - **Dependency order**: Some changes must come before others
   - **File relationships**: Files that are always modified together
   - **Conventional commits**: feat, fix, refactor, test, docs, chore

4. **Generate commit plan:**
   ```
   ╭─ Commit Plan ──────────────────────────────────────────────╮
   │                                                             │
   │ Analyzed: 13 files changed (+487, -156 lines)              │
   │ Detected: 4 logical changes                                │
   │                                                             │
   │ ┌─────────────────────────────────────────────────────────┐│
   │ │ 1. feat: Add user authentication system                ││
   │ │    8 files (+312 lines)                                 ││
   │ │    Priority: ★★★ (foundation for other changes)        ││
   │ │                                                          ││
   │ │    ✓ src/auth/auth-controller.ts         (+87 lines)   ││
   │ │    ✓ src/auth/auth-service.ts            (+65 lines)   ││
   │ │    ✓ src/auth/jwt-manager.ts             (+43 lines)   ││
   │ │    ✓ src/models/user-model.ts            (+52 lines)   ││
   │ │    ✓ src/middleware/auth-middleware.ts   (+38 lines)   ││
   │ │    ✓ src/routes/auth-routes.ts           (+27 lines)   ││
   │ │    ✓ tests/auth.test.ts                  (+78 lines)   ││
   │ │    ✓ package.json                        (+22 lines)   ││
   │ │                                                          ││
   │ │    Message:                                             ││
   │ │    feat: implement JWT-based authentication system     ││
   │ │                                                          ││
   │ │    - Add AuthController with login/logout endpoints    ││
   │ │    - Implement JWT token generation and validation     ││
   │ │    - Create auth middleware for protected routes       ││
   │ │    - Add User model with password hashing              ││
   │ │    - Include comprehensive test coverage (78 tests)    ││
   │ └─────────────────────────────────────────────────────────┘│
   │                                                             │
   │ ┌─────────────────────────────────────────────────────────┐│
   │ │ 2. fix: Resolve null pointer exception in profile      ││
   │ │    2 files (+23, -15 lines)                             ││
   │ │    Priority: ★★ (bug fix, should go early)             ││
   │ │                                                          ││
   │ │    ✓ src/services/profile-service.ts     (+12, -8)     ││
   │ │    ✓ tests/profile-service.test.ts       (+11, -7)     ││
   │ │                                                          ││
   │ │    Message:                                             ││
   │ │    fix: handle null user in profile service            ││
   │ │                                                          ││
   │ │    - Add null check before accessing user properties   ││
   │ │    - Return early with 404 for missing users           ││
   │ │    - Add test cases for null/undefined scenarios       ││
   │ └─────────────────────────────────────────────────────────┘│
   │                                                             │
   │ ┌─────────────────────────────────────────────────────────┐│
   │ │ 3. refactor: Extract validation utils                  ││
   │ │    3 files (+98, -141 lines)                            ││
   │ │    Priority: ★ (cleanup, can go last)                  ││
   │ │                                                          ││
   │ │    ✓ src/utils/validators.ts             (+87 lines)   ││
   │ │    ✓ src/auth/auth-controller.ts         (-67 lines)   ││
   │ │    ✓ src/services/user-service.ts        (-74 lines)   ││
   │ │                                                          ││
   │ │    Message:                                             ││
   │ │    refactor: centralize validation logic               ││
   │ │                                                          ││
   │ │    - Extract common validators to utils                ││
   │ │    - Remove duplicated validation code                 ││
   │ │    - DRY up email/password validation                  ││
   │ └─────────────────────────────────────────────────────────┘│
   │                                                             │
   │ ┌─────────────────────────────────────────────────────────┐│
   │ │ 4. docs: Update API documentation                      ││
   │ │    1 file (+54 lines)                                   ││
   │ │    Priority: ★ (documentation, can go last)            ││
   │ │                                                          ││
   │ │    ✓ README.md                           (+54 lines)   ││
   │ │                                                          ││
   │ │    Message:                                             ││
   │ │    docs: add authentication endpoints to README        ││
   │ │                                                          ││
   │ │    - Document /auth/login and /auth/logout endpoints   ││
   │ │    - Add JWT token usage examples                      ││
   │ │    - Update getting started guide                      ││
   │ └─────────────────────────────────────────────────────────┘│
   │                                                             │
   ├─────────────────────────────────────────────────────────────┤
   │                                                             │
   │ 💡 Recommended order:                                      │
   │    1 (feat) → 2 (fix) → 3 (refactor) → 4 (docs)          │
   │                                                             │
   │ ⚠️  Note: Commit #3 modifies files from commit #1         │
   │    Consider squashing if both are uncommitted             │
   │                                                             │
   │ Actions:                                                    │
   │   [A]pprove & execute    - Create all commits in order    │
   │   [E]dit plan            - Modify groupings or messages   │
   │   [P]review commands     - Show git commands only         │
   │   [C]ancel               - Discard plan                   │
   │                                                             │
   ╰─────────────────────────────────────────────────────────────╯
   ```

5. **Use AskUserQuestion for confirmation:**
   Ask user to choose action:
   - **Approve & execute**: Run git commands to create commits
   - **Edit plan**: Allow user to modify groupings or messages
   - **Preview commands**: Show what git commands will run
   - **Cancel**: Exit without committing

6. **If approved, execute commits:**
   ```bash
   # Commit 1: feat
   git add src/auth/auth-controller.ts src/auth/auth-service.ts \
           src/auth/jwt-manager.ts src/models/user-model.ts \
           src/middleware/auth-middleware.ts src/routes/auth-routes.ts \
           tests/auth.test.ts package.json
   git commit -m "feat: implement JWT-based authentication system

   - Add AuthController with login/logout endpoints
   - Implement JWT token generation and validation
   - Create auth middleware for protected routes
   - Add User model with password hashing
   - Include comprehensive test coverage (78 tests)"

   # Commit 2: fix
   git add src/services/profile-service.ts tests/profile-service.test.ts
   git commit -m "fix: handle null user in profile service

   - Add null check before accessing user properties
   - Return early with 404 for missing users
   - Add test cases for null/undefined scenarios"

   # ... and so on
   ```

7. **Show summary:**
   ```
   ✅ Commit plan executed successfully!

   Created 4 atomic commits:
   ├─ a1b2c3d feat: implement JWT-based authentication system
   ├─ d4e5f6g fix: handle null user in profile service
   ├─ h7i8j9k refactor: centralize validation logic
   └─ l0m1n2o docs: add authentication endpoints to README

   💡 Next steps:
   - Review commits: git log --oneline -4
   - Push to remote: git push origin <branch>
   - Create PR: gh pr create
   ```

## Grouping Algorithm

**How changes are grouped:**

1. **File analysis:**
   - New files → likely new feature
   - Modified tests → goes with implementation
   - README/docs → separate documentation commit

2. **Semantic analysis:**
   - Related function/class names (auth*, user*, payment*)
   - Import relationships (files that import each other)
   - Conventional commit type detection

3. **Change type detection:**
   - `+` only → Feature addition
   - `-` only → Code removal
   - Equal `+/-` → Refactoring
   - Bug keywords (fix, null, undefined, error) → Bug fix

4. **Dependency detection:**
   - Some commits must come before others
   - Tests go with their implementation
   - Config changes go with feature that needs them

## Edge Cases

**No clear groupings:**
```
ℹ️  Could not detect distinct logical changes

All changes appear to be part of one feature.

Suggested commit:
feat: <your description>

Files: 13 changed (+487, -156)
```

**Too many changes:**
```
⚠️  Large changeset detected (25 files, 2,341 lines)

Recommendation: Review changes manually
Consider creating a feature branch and multiple PRs
```

**Conflicts between groups:**
```
⚠️  Detected overlapping changes:
- Commit #1 (feat) modifies user-model.ts
- Commit #3 (refactor) also modifies user-model.ts

Options:
1. Merge commits #1 and #3
2. Stage partial changes (git add -p)
3. Manual resolution needed
```

## Integration with Git Workflow

**Daily workflow:**
```bash
# After coding session
/dev-aid-commit-plan

# Review and approve plan
# Commits created automatically

# Push commits
git push origin feature-branch

# Create PR
gh pr create
```

**Team best practice:**
```bash
# Add to pre-push hook
#!/bin/bash
# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Uncommitted changes detected"
    echo "💡 Run: /dev-aid-commit-plan"
    exit 1
fi
```

## Comparison to Atomic Commit Splitter

| Approach | Commit Planner (this) | Atomic Splitter |
|----------|----------------------|-----------------|
| **Timing** | Before commits | After commits |
| **Safety** | Safe (no git history manipulation) | Risky (rewrites history) |
| **UX** | Interactive, preview before execute | Automatic |
| **Learning** | Teaches good habits | Black box |
| **Flexibility** | Can edit plan | Fixed splitting |

## Value Proposition

**Time savings:**
- 10-15 min/day saved vs manual commit planning
- 30-60 min saved in PR review (atomic commits easier to review)
- Cleaner git history (easier debugging with git bisect)

**For 100 developers:**
- 10 min/day/dev × 100 devs = 1,000 min/day = 17 hours/day
- Annual: 17 hrs/day × 250 days = 4,250 hours
- At $100/hr: **$425,000/year** in improved productivity

**Quality improvements:**
- Better code review (smaller, focused commits)
- Easier rollbacks (atomic commits)
- Cleaner git history (easier git bisect)
- Teaching tool (developers learn good commit habits)

## Related Commands

- `/dev-aid-review-staged` - Review before committing
- `gh pr create` - Create PR from commits
- `git log --oneline` - Review commit history
