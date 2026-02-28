# Dev-AID Update System Guide

**Version:** 2.0.0
**Status:** Beta Implementation
**Last Updated:** 2026-02-28

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Usage](#usage)
5. [Conflict Resolution](#conflict-resolution)
6. [Automated Checks](#automated-checks)
7. [Rollback](#rollback)
8. [Protected Paths](#protected-paths)
9. [Troubleshooting](#troubleshooting)
10. [Advanced Usage](#advanced-usage)
11. [Security](#security)

---

## Quick Start

### Check for Updates
```bash
# Via gh extension (recommended)
gh dev-aid check

# Via script (fallback)
./.dev-aid/scripts/check-update-notify.sh
```

### Apply Update
```bash
# Via gh extension (recommended) — handles backup, protected paths, cleanup
gh dev-aid update

# Via script (fallback)
./.dev-aid/scripts/update-dev-aid.sh
```

### Automatic Notifications

Dev-AID automatically checks for updates on every session start (Claude Code and Gemini CLI). The check is throttled to **once per 24 hours** and uses a **global cache** (`~/.cache/dev-aid/`) so multiple projects share a single API call:

```
⬆️  Update available: 1.5.0-beta.1 -> 1.6.0 (run: gh dev-aid update)
```

### Rollback to Previous Version
```bash
# List available backups
./.dev-aid/scripts/rollback.sh

# Restore from specific backup
./.dev-aid/scripts/rollback.sh .dev-aid-backup-YYYYMMDD-HHMMSS
```

---

## Features

### 🛡️ **Phase 1: Safety Features** (Implemented)

| Feature | Description | Benefit |
|---------|-------------|---------|
| **Conflict Detection** | Detects user-modified files before overwriting | Never lose customizations silently |
| **Interactive Merge** | Prompts for each conflict: keep/take/merge | Full control over what gets updated |
| **Dry-Run Mode** | Preview changes without applying them | Zero-risk exploration |
| **Automated Rollback** | Auto-restore on errors | Safe updates with one-command restore |
| **Checksum Verification** | SHA256 verification of downloads | Protection against MITM attacks |
| **Protected Paths** | Never overwrites .env, memory-bank, custom skills | Critical data always preserved |

### 🧠 **Phase 2: Intelligence Features** (Complete)

| Feature | Status | Description |
|---------|--------|-------------|
| **Semantic Versioning** | ✅ Implemented in lib | Warns on major version changes |
| **Breaking Change Detection** | ✅ Implemented in lib | Prompts before applying breaking updates |
| **Selective Updates** | ✅ Implemented | Choose which components to update via `--component` flag |

### 🤖 **Phase 3: Automation Features** (Implemented)

| Feature | Description | Configuration |
|---------|-------------|---------------|
| **Session-Start Notification** | Auto-checks on every session (Claude/Gemini) | Throttled: once per 24h |
| **Global Cache** | Shared across all projects using Dev-AID | `~/.cache/dev-aid/` |
| **gh Extension** | `gh dev-aid update` / `gh dev-aid check` | Install: `gh extension install Probably-Group/gh-dev-aid` |
| **GitHub API Integration** | Fetches version via `gh api` | Uses existing GitHub auth |

---

## Architecture

### File Structure

```
# gh-dev-aid extension (separate repo: Probably-Group/gh-dev-aid)
gh-dev-aid                          # CLI extension: init, update, check, status, version

# In-repo scripts
.dev-aid/
├── scripts/
│   ├── check-update-notify.sh     # Session-start notification (global cache)
│   ├── update-dev-aid.sh          # Legacy update script (fallback)
│   ├── update-lib.sh              # Shared update functions
│   └── rollback.sh                # Rollback tool
│
├── orchestration/
│   ├── conflict_resolver.py       # Interactive conflict resolution
│   └── github_client.py           # GitHub API client
│
└── docs/
    └── UPDATE-SYSTEM-GUIDE.md     # This document
```

### Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                   User Interface                        │
│  (update-dev-aid.sh, rollback.sh, check-update-notify.sh) │
└────────────────────┬────────────────────────────────────┘
                     │
            ┌────────┴────────┐
            ▼                 ▼
┌───────────────────┐  ┌──────────────────┐
│   update-lib.sh   │  │  GitHub API      │
│  (Shared Logic)   │  │  (github_client  │
│                   │  │   .py)           │
│ - Version compare │  │                  │
│ - Checksums       │  │ - Fetch releases │
│ - Backups         │  │ - Download       │
│ - Protected paths │  │ - Checksums      │
└─────────┬─────────┘  └────────┬─────────┘
          │                     │
          └─────────┬───────────┘
                    ▼
         ┌─────────────────────┐
         │  conflict_resolver  │
         │       .py           │
         │                     │
         │ - Detect conflicts  │
         │ - Show diffs        │
         │ - Interactive merge │
         └─────────────────────┘
```

---

## Usage

### Interactive Update

The standard update flow with full safety features:

```bash
$ ./.dev-aid/scripts/update-dev-aid.sh

╔════════════════════════════════════════════╗
║        Dev-AID Update Tool                 ║
╚════════════════════════════════════════════╝

→ Current Dev-AID version: 1.5.0-beta.1

Update source options:
  1. Pull from official repository (recommended)
  2. Copy from local Dev-AID installation
  3. Manual update (guide only)

Choose option [1-3]: 1

Creating backup...
→ Backing up user data...
✓ Backup created: .dev-aid-backup-20260209-143022

Checking for conflicts...
🔍 Found 2 conflicting files
   Resolving each conflict interactively...

[1/2] Resolving: templates/ci/python.yml
────────────────────────────────────────────────

⚠️  Conflict in: templates/ci/python.yml

Options:
  [y] Keep YOUR version (preserve your changes)
  [u] Take UPSTREAM version (accept new version)
  [m] Manual MERGE (create merge file)
  [d] Show DIFF again
  [s] SKIP this file for now

Your choice [y/u/m/d/s/?]:
```

### Dry-Run Mode

Preview what will change without making any modifications:

```bash
$ ./.dev-aid/scripts/update-dev-aid.sh --dry-run

🔍 DRY RUN MODE (no changes will be made)

→ Current Dev-AID version: 1.5.0-beta.1

Checking for conflicts...
[DRY-RUN] Would detect conflicts in 2 files:
  - templates/ci/python.yml
  - scripts/generate-ci.sh

[DRY-RUN] Would download: dev-aid-v1.5.0-beta.1.tar.gz
[DRY-RUN] Would verify checksum: a3f2b1c...
[DRY-RUN] Would update dependencies

✅ Dry run complete - no changes made
   Run without --dry-run to apply update
```

### Selective Updates

Update only specific components instead of everything:

```bash
# List available components
$ ./.dev-aid/scripts/update-dev-aid.sh --list-components

Available components for selective update:

  COMPONENT      DESCRIPTION                                        PATHS
  ─────────────  ──────────────────────────────────────────────────  ──────────────────────
  router         Orchestration router, context detection, routing    orchestration/
  skills         Skill definitions (core, expert, process)           skills/
  agents         Agent framework, adapters, teams                    agents/
  scripts        Utility scripts and CLI tools                       scripts/
  security       Security scanning, checks, config                   orchestration/run_security_checks.sh,...
  templates      CI templates, ADR templates, onboarding             templates/
  providers      Provider configurations (Claude, Gemini, etc.)      providers/
  docs           Documentation files                                 docs/,CHANGELOG.md,...
  config         Configuration files (models, routing, teams)        config/
  search         Local search and RAG integration                    local-search/,deep-research/
  automation     Automation workflows and presets                     automation/,presets/
```

```bash
# Update only the router
$ ./.dev-aid/scripts/update-dev-aid.sh --component router

# Update skills and agents together
$ ./.dev-aid/scripts/update-dev-aid.sh --component skills --component agents

# Preview a selective update (dry-run)
$ ./.dev-aid/scripts/update-dev-aid.sh --component router --dry-run
```

**Notes:**
- The `--component` flag is repeatable -- pass it multiple times for multiple components
- Protected paths are still respected during selective updates
- Backup and rollback work the same way for selective updates
- Python dependencies are only updated when the `router` component is included
- Without `--component`, the script updates everything (backward compatible)

---

## Conflict Resolution

### Interactive Merge Options

When a conflict is detected, you have 5 options:

#### 1. Keep YOUR Version (y)
```
✅ Keeping your version of templates/ci/python.yml
```
- **Use when:** You've customized for your project
- **Effect:** Ignores upstream changes
- **Safety:** Your modifications are preserved

#### 2. Take UPSTREAM Version (u)
```
✅ Taking upstream version of templates/ci/python.yml
```
- **Use when:** Upstream has bug fixes or you want defaults
- **Effect:** Replaces with new version
- **Safety:** Your changes are lost (but backed up)

#### 3. Manual MERGE (m)
```
🔧 Creating merge file for templates/ci/python.yml...
✅ Merged file created: .dev-aid/templates/ci/python.yml.merged
   Review and replace templates/ci/python.yml when ready
```
- **Use when:** Both versions have important changes
- **Effect:** Creates file with git-style conflict markers
- **Process:**
  ```
  <<<<<<< YOUR VERSION
  your changes here
  =======
  upstream changes here
  >>>>>>> UPSTREAM VERSION
  ```
- **Next steps:** Edit `.merged` file, then replace original

#### 4. Show DIFF (d)
```
====================================================================
📝 Diff for: templates/ci/python.yml
====================================================================
--- current/templates/ci/python.yml
+++ upstream/templates/ci/python.yml
@@ -10,7 +10,7 @@
-      python-version: ['3.9', '3.10', '3.11']
+      python-version: ['3.10', '3.11', '3.12']
====================================================================
```
- **Use when:** Need to see what changed before deciding
- **Effect:** Shows unified diff with color coding
- **Returns:** Back to choice prompt

#### 5. SKIP (s)
```
⏭️  Skipped templates/ci/python.yml (will not be updated)
```
- **Use when:** Need more time to decide
- **Effect:** File unchanged, update continues
- **Note:** Can update manually later

### Conflict Resolution Summary

After resolving all conflicts, you'll see a summary:

```
====================================================================
📊 Resolution Summary
====================================================================
  Kept your version: 1
  Took upstream: 3
  Manual merge: 1
  Skipped: 0
  Total conflicts: 5

⚠️  Note: Review .merged files and replace originals when ready
====================================================================
```

---

## Automated Checks

### Session-Start Notifications

Dev-AID checks for updates automatically every time you start a session in Claude Code or Gemini CLI. The check is:

- **Throttled** — at most once per 24 hours (configurable via `CHECK_INTERVAL` in `check-update-notify.sh`)
- **Global** — uses `~/.cache/dev-aid/` so all your projects share one API call per day
- **Non-blocking** — 3-second timeout, won't delay session start
- **Per-project comparison** — each project compares its own `.dev-aid/VERSION` against the cached remote

#### Output (when update available):
```
⬆️  Update available: 1.5.0-beta.1 -> 1.6.0 (run: gh dev-aid update)
```

### Manual Check

```bash
# Quick version check (no clone, just API call)
gh dev-aid check

# Full status including health
gh dev-aid status
```

### Configuration

Edit check interval in `.dev-aid/scripts/check-update-notify.sh`:
```bash
CHECK_INTERVAL=86400  # 24 hours in seconds (default)
```

---

## Rollback

### List Available Backups

```bash
$ ./.dev-aid/scripts/rollback.sh

╔════════════════════════════════════════════╗
║        Dev-AID Rollback Tool               ║
╚════════════════════════════════════════════╝

Available backups:

1. .dev-aid-backup-20260205-143022
   Version: 1.5.0-beta.1
   Created: Thu Feb  5 14:30:22 PST 2026
   Size: 15M

2. .dev-aid-backup-20260128-091530
   Version: 1.4.0
   Created: Wed Jan 28 09:15:30 PST 2026
   Size: 14M

Example:
  ./rollback.sh .dev-aid-backup-20251210-143022
```

### Restore from Backup

```bash
$ ./.dev-aid/scripts/rollback.sh .dev-aid-backup-20251210-143022

Backup Information:
  Path: .dev-aid-backup-20260205-143022
  Version: 1.5.0-beta.1

Dev-AID Backup Manifest
Created: Thu Feb  5 14:30:22 PST 2026
Current Version: 1.5.0-beta.1

Backed up:
- API keys (.env files)
- Memory bank
- Logs
- RAG indices
- Custom skills
- VERSION file

⚠️  This will replace your current Dev-AID installation
   Current version: 1.5.0-beta.1
   Backup version:  1.4.0

Proceed with rollback? [y/N]: y

Starting rollback...

→ Creating safety backup of current state...
✓ Safety backup created: .dev-aid-pre-rollback-20260209-150622

→ Restoring Dev-AID from backup...
  ✓ Restored VERSION file
  ✓ Restored .env files
  ✓ Restored memory bank
  ✓ Restored logs
  ✓ Restored RAG indices
  ✓ Restored custom skills for claude

✓ Rollback complete

╔════════════════════════════════════════════╗
║         Rollback Complete! ✅              ║
╚════════════════════════════════════════════╝

Version: 1.5.0-beta.1 → 1.4.0
```

### Automatic Rollback on Error

If an update fails, the system automatically rolls back:

```bash
❌ Update failed!

Attempting automatic rollback...
→ Restoring from backup...
✓ Successfully rolled back to previous version

Backup preserved at: .dev-aid-backup-20260209-143022
Review logs and try updating again later.
```

---

## Protected Paths

These paths are **NEVER** overwritten during updates:

| Path | Content | Why Protected |
|------|---------|---------------|
| `.dev-aid/config/.env*` | API keys, secrets | User credentials |
| `.dev-aid/memory-bank/` | Patterns, decisions, context | User knowledge base |
| `.dev-aid/logs/` | Routing history, costs | Historical data |
| `.dev-aid/local-search/index/` | RAG vector indices | Expensive to rebuild |
| `.dev-aid/providers/*/skills/custom/` | User-created skills | Custom functionality |

### Verification

To verify protected paths:
```bash
source .dev-aid/scripts/update-lib.sh
get_protected_paths
```

Output:
```
.dev-aid/config/.env*
.dev-aid/memory-bank/
.dev-aid/logs/
.dev-aid/local-search/index/
.dev-aid/providers/*/skills/custom/
```

---

## Troubleshooting

### "Checksum mismatch" Error

**Symptom:**
```
❌ Checksum mismatch!
   Expected: a3f2b1c4d5e6f7a8b9c0d1e2f3a4b5c6...
   Got:      b9c0d1e2f3a4b5c6a7b8c9d0e1f2a3b4...

   Possible causes:
   - Corrupted download
   - MITM attack
   - Wrong file downloaded
```

**Solution:**
1. Check your internet connection
2. Retry the update: `./.dev-aid/scripts/update-dev-aid.sh`
3. If persists, download manually from GitHub
4. Verify GitHub is not experiencing issues

### "Breaking changes detected" Warning

**Symptom:**
```
⚠️  BREAKING CHANGES DETECTED
   Current version: 1.9.0
   New version:     2.0.0

   Major version changed - may require migration
   Review changelog: .dev-aid/CHANGELOG.md

Continue with update? [y/N]:
```

**Solution:**
1. Review CHANGELOG.md for migration guide
2. Test in a separate branch first:
   ```bash
   git checkout -b test-update
   ./.dev-aid/scripts/update-dev-aid.sh
   # Test everything works
   git checkout main
   ```
3. Keep backup until verified working
4. If issues arise, rollback:
   ```bash
   ./.dev-aid/scripts/rollback.sh <backup-name>
   ```

### Update Failed Mid-Process

**Symptom:**
```
❌ Update failed!

Attempting automatic rollback...
```

**Solution:**
The updater automatically rolls back on errors.

**Manual rollback if needed:**
```bash
# List backups
ls -td .dev-aid-backup-*

# Restore from most recent
./.dev-aid/scripts/rollback.sh .dev-aid-backup-YYYYMMDD-HHMMSS
```

### GitHub API Rate Limit Exceeded

**Symptom:**
```
❌ GitHub API rate limit exceeded. Reset in 1823 seconds.
   Set GITHUB_TOKEN environment variable for higher limits.
```

**Solution:**
1. **Wait for rate limit reset** (shown in error)
2. **Use GitHub token** for 5000 req/hour:
   ```bash
   export GITHUB_TOKEN="ghp_your_token_here"
   ./.dev-aid/scripts/check-update-notify.sh
   ```
3. **Check rate limit status:**
   ```bash
   python3 .dev-aid/orchestration/github_client.py check-rate-limit
   ```

### Conflict Resolution Stuck

**Symptom:**
```
[1/5] Resolving: templates/ci/python.yml

Your choice [y/u/m/d/s/?]: ^C
```

**Solution:**
1. **Ctrl+C** to cancel update
2. Backup is preserved automatically
3. Review conflicts manually
4. Retry update when ready

---

## Advanced Usage

### Force Update (Skip Conflicts)

**⚠️ WARNING:** Overwrites all conflicts with upstream.

```bash
./.dev-aid/scripts/update-dev-aid.sh --force
```

**Use when:**
- You want a clean upstream state
- You've backed up customizations elsewhere
- Conflicts are in non-critical files

### Update from Local Copy

```bash
# Clone Dev-AID repository
git clone https://github.com/your-org/dev-aid /tmp/dev-aid

# Update from local copy
./.dev-aid/scripts/update-dev-aid.sh --source /tmp/dev-aid
```

### Disable Auto-Check

**Option 1: Remove the notification script**
```bash
rm .dev-aid/scripts/check-update-notify.sh
```

**Option 2: Clear the cache to force re-check**
```bash
rm -rf ~/.cache/dev-aid/
```

### Custom Repository

```bash
# Set custom repo
export DEV_AID_REPO="your-fork/dev-aid"

# Check updates from fork
./.dev-aid/scripts/check-update-notify.sh
```

---

## Security

### Checksum Verification

All downloads are verified with SHA256 checksums from GitHub releases:

```bash
# Verify checksum manually
python3 .dev-aid/orchestration/github_client.py get-checksums

# Output:
{
  "dev-aid-v1.5.0-beta.1.tar.gz": "a3f2b1c4d5e6f7a8b9c0d1e2f3a4b5c6...",
  "dev-aid-v1.5.0-beta.1.zip": "b9c0d1e2f3a4b5c6a7b8c9d0e1f2a3b4..."
}
```

### Backup Before Update

Every update creates a timestamped backup:
```
.dev-aid-backup-YYYYMMDD-HHMMSS/
├── .env*              # API keys
├── memory-bank/       # Patterns, decisions
├── logs/              # Routing history
├── local-search/      # RAG indices
├── providers/         # Custom skills
├── VERSION            # Version reference
└── MANIFEST.txt       # Backup metadata
```

### Rollback on Failure

If an update fails, the system automatically restores from backup:
1. Error detected via `trap ERR`
2. Restore triggered automatically
3. User notified with recovery steps
4. Backup preserved for manual inspection

### Protected Data

User data is NEVER overwritten:
- ✅ API keys (.env files)
- ✅ Memory bank content
- ✅ Custom expert skills
- ✅ RAG vector indices
- ✅ Routing logs and costs

---

## FAQ

**Q: Will updating overwrite my custom skills?**
A: No. Custom skills in `.dev-aid/providers/*/skills/custom/` are protected and never overwritten.

**Q: What happens to my API keys?**
A: API keys in `.env` files are never overwritten. They're backed up and restored after updates.

**Q: Can I update just the router code?**
A: Yes! Use `--component router` to update only the router. You can also combine components: `--component skills --component agents`. Use `--list-components` to see all available components.

**Q: How do I disable update notifications?**
A: Remove `.dev-aid/scripts/check-update-notify.sh` or delete the `check_update` function from your provider's session-start hook.

**Q: Where are backups stored?**
A: In the project root as `.dev-aid-backup-YYYYMMDD-HHMMSS/`

**Q: How long are backups kept?**
A: By default, the 3 most recent backups are kept. Older backups are cleaned up automatically.

**Q: Can I rollback multiple versions?**
A: Yes! Use `./rollback.sh` to list all backups and choose any version.

**Q: What if rollback fails?**
A: Rollback creates a "pre-rollback" backup. You can restore that if needed.

**Q: Does this work offline?**
A: Partially. You can update from local copy (`--source` flag), but GitHub API checks require internet.

---

## Support

- **Documentation:** `.dev-aid/docs/`
- **Issues:** GitHub Issues
- **Discussions:** GitHub Discussions

---

## Changelog

### v2.0.0 (2026-02-28)
- ✅ Phase 2: Intelligence features — selective updates
- ✨ `--component <name>` flag for updating specific components
- ✨ `--list-components` flag to display available components
- ✨ 11 components: router, skills, agents, scripts, security, templates, providers, docs, config, search, automation
- ✨ Component-aware conflict detection (only checks files in selected components)
- ✨ Component-aware rsync filtering (only syncs files in selected components)
- ✨ Smart dependency updates (only when router component is selected)
- ✨ Backward compatible (no flags = update everything)

### v1.0.0 (2025-12-10)
- ✨ Initial implementation
- ✅ Phase 1: Safety features (conflict detection, dry-run, rollback, checksums)
- ✅ Phase 3: Automation features (weekly checks, GitHub API)

---

**Built with safety and user control in mind. Your customizations matter.**
