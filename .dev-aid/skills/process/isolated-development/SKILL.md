---
name: isolated-development
description: "Git worktree per feature/issue - clean, isolated development environments"
risk_level: low
version: 1.0.0
domain: process/workflow
enforcement: warning
token_budget: 300
triggers:
  - new_feature
  - issue_resolution
  - "start work on"
---

# Isolated Development

## 0. Core Principle

**ONE WORKTREE PER FEATURE/ISSUE**

Never pollute main development with experimental changes.

---

## 1. Auto-Create from Issue

When user says "work on issue #123":

```
┌─────────────────────────────────────────────────────────┐
│ 1. Fetch issue details                                  │
│    gh issue view 123 --json title,body,labels           │
├─────────────────────────────────────────────────────────┤
│ 2. Create worktree                                      │
│    git worktree add .worktrees/issue-123 -b fix/123     │
├─────────────────────────────────────────────────────────┤
│ 3. Setup project                                        │
│    → Detect type (Node/Python/Rust/Go)                  │
│    → Run install commands                               │
├─────────────────────────────────────────────────────────┤
│ 4. Verify baseline                                      │
│    → Run test suite                                     │
│    → If fails: STOP, report, ask guidance               │
├─────────────────────────────────────────────────────────┤
│ 5. Load issue context into session                      │
│    → Issue description                                  │
│    → Related files (from issue mentions)                │
│    → Relevant expert skills                             │
└─────────────────────────────────────────────────────────┘
```

---

## 2. Worktree Commands

### Create Worktree

```bash
# From issue number
git worktree add .worktrees/issue-123 -b fix/123

# From feature name
git worktree add .worktrees/feature-oauth -b feature/oauth

# From branch name (existing branch)
git worktree add .worktrees/my-branch my-branch
```

### List Worktrees

```bash
git worktree list
```

### Remove Worktree

```bash
# Clean removal (after merge)
git worktree remove .worktrees/issue-123

# Force removal (abandoned work)
git worktree remove --force .worktrees/issue-123

# Also delete the branch
git branch -d fix/123
```

---

## 3. Project Setup Commands

**Auto-detected based on project files (see references/project-setup-commands.md)**

| Project Type | Setup Command |
|--------------|---------------|
| Node.js (npm) | `npm install` |
| Node.js (yarn) | `yarn install` |
| Node.js (pnpm) | `pnpm install` |
| Python (pip) | `pip install -r requirements.txt` |
| Python (poetry) | `poetry install` |
| Python (uv) | `uv sync` |
| Rust | `cargo build` |
| Go | `go mod download` |

---

## 4. Integration with Dev-AID

### Issue Resolver Integration

Connect to existing `dev-aid-resolve-issue`:

```bash
# Work on issue in isolated worktree
dev-aid-resolve-issue --issue 123 --worktree

# This automatically:
# 1. Creates worktree
# 2. Sets up project
# 3. Analyzes issue
# 4. Proposes solution
```

### Session Context

When entering a worktree, load:
- Issue title and description
- Labels (for skill auto-selection)
- Related file mentions
- Previous comments/discussion

---

## 5. Workflow

### Starting Work

```
┌─────────────────────────────────────────────────────────┐
│ 1. "Work on issue #123"                                 │
│    → Creates .worktrees/issue-123/                      │
│    → Checks out fix/123 branch                          │
├─────────────────────────────────────────────────────────┤
│ 2. Navigate to worktree                                 │
│    cd .worktrees/issue-123                              │
├─────────────────────────────────────────────────────────┤
│ 3. Work normally                                        │
│    → All changes isolated to this worktree              │
│    → Main worktree unchanged                            │
├─────────────────────────────────────────────────────────┤
│ 4. Create PR when ready                                 │
│    gh pr create --title "Fix #123: ..."                 │
└─────────────────────────────────────────────────────────┘
```

### Switching Context

```bash
# Return to main development
cd /path/to/project

# Switch to different issue
cd .worktrees/issue-456

# Each worktree is independent:
# - Different branch
# - Different working state
# - No stash/commit needed to switch
```

---

## 6. Cleanup Protocol

| Outcome | Action |
|---------|--------|
| Merged to main | Remove worktree and branch |
| PR created | Keep worktree (for updates) |
| Abandoned | Remove worktree (confirm first) |
| In progress | Keep worktree |

### Cleanup Commands

```bash
# After merge
git worktree remove .worktrees/issue-123
git branch -d fix/123

# Prune stale worktrees
git worktree prune
```

---

## 7. Best Practices

### DO
- ✅ Create worktree at project start
- ✅ Verify tests pass before starting work
- ✅ Keep worktrees for open PRs
- ✅ Clean up after merge

### DON'T
- ❌ Make changes in main worktree
- ❌ Leave orphaned worktrees
- ❌ Work on multiple issues in one worktree
- ❌ Skip baseline verification

---

## 8. References

For detailed information, see:
- `references/project-setup-commands.md` - Per-language setup commands
